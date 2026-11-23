"""Assemble animated scene clips + narration + SFX + music into the final video, plus editing-project files.

Usage: python3 assemble.py <project_dir> <first_id> <last_id> <output_basename>
"""
import json, os, shutil, subprocess, sys
import numpy as np
import soundfile as sf

proj, a, b, base = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
SR, FPS, PAD, MIN_DUR, NARR_OFFSET = 48000, 24, 0.55, 2.0, 0.12
P = lambda *x: os.path.join(proj, *x)
sb = {s["id"]: s for s in json.load(open(P("03_STORYBOARD", "storyboard.json")))["scenes"]}
durs = json.load(open(P("06_AUDIO", "narration", "durations.json")))


def load(path):
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", path, "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).copy()


def probe_dur(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                         capture_output=True, text=True, check=True).stdout
    return float(out)


# SFX cues: scene id -> list of (file, time as fraction-of-T or seconds 's', gain, loop_seconds)
def cues(i, T):
    if i == 1:
        return [("clock_tick", k * 0.5, 0.5, None) for k in range(int(0.5 * T / 0.5) + 1)] + \
               [("mosquito_buzz", 0.0, 0.10, 0.68 * T), ("thud", 0.68 * T + 0.5, 0.25, None)]
    if i == 2: return [("whoosh", 0.12 * T, 0.35, None)]
    if i == 3: return [("mosquito_buzz", 0.0, 0.22, 0.45 * T), ("puff", 0.45 * T, 0.5, None)]
    if i == 4: return [("scratch", 0.0, 0.35, None), ("sparkle", 0.72 * T, 0.35, None)]
    if i == 5: return [("whoosh", 0.12 * T, 0.25, None)]
    if i == 6: return [("pop", 0.42 * T, 0.4, None), ("sparkle", 0.47 * T, 0.3, None)]
    if i == 9: return [("thud", 0.08 * T + 0.364 * 0.52 * T, 0.5, None)]
    if i == 10: return [("pop", 0.3 * T, 0.5, None)]
    return []


ids = list(range(a, b + 1))
timeline, t0 = [], 0.0
for i in ids:
    name = f"scene_{i:03d}"
    clip = P("05_ANIMATIONS", name, name + ".mp4")
    if not os.path.exists(clip):
        sys.exit(f"MISSING clip {clip}")
    T = probe_dur(clip)
    timeline.append(dict(id=i, file=name, start=round(t0, 3), duration=round(T, 3), narration=sb[i]["narration"],
                         clip=os.path.relpath(clip, P("08_EDITING_PROJECT")),
                         audio=os.path.relpath(P("06_AUDIO", "narration", name + ".wav"), P("08_EDITING_PROJECT"))))
    t0 += T
total = t0

# ---- audio mix
n = int((total + 0.5) * SR)
voice, fx = np.zeros(n, np.float32), np.zeros(n, np.float32)
cache = {}
for e in timeline:
    v = load(P("06_AUDIO", "narration", e["file"] + ".wav"))
    s0 = int((e["start"] + NARR_OFFSET) * SR)
    voice[s0:s0 + len(v)] += v[: n - s0]
    for (fname, at, gain, loop) in cues(e["id"], e["duration"]):
        x = cache.setdefault(fname, load(P("06_AUDIO", "sound_effects", fname + ".wav")))
        if loop:
            reps = int(np.ceil(loop * SR / len(x)))
            x = np.tile(x, reps)[: int(loop * SR)]
            fade = min(len(x), int(0.08 * SR))
            x = x.copy(); x[-fade:] *= np.linspace(1, 0, fade)
        s0 = int((e["start"] + at) * SR)
        fx[s0:s0 + len(x)] += gain * x[: n - s0]
music = load(P("06_AUDIO", "music", "music_bed_curious_72bpm.wav"))
music = np.resize(music, n) * 0.16
fo = int(1.5 * SR); music[-fo:] *= np.linspace(1, 0, fo)
fi = int(0.8 * SR); music[:fi] *= np.linspace(0, 1, fi)
mix = voice * 1.0 + fx + music
mix = mix / max(1e-9, np.abs(mix).max()) * 0.95
os.makedirs(P("08_EDITING_PROJECT"), exist_ok=True)
mix_path = P("08_EDITING_PROJECT", base + "_audio_mix.wav")
sf.write(mix_path, mix, SR)
sf.write(P("08_EDITING_PROJECT", base + "_voice_only.wav"), voice, SR)
sf.write(P("08_EDITING_PROJECT", base + "_sfx_only.wav"), fx, SR)

# ---- video concat (stream copy; all clips share codec/res/fps)
lst = P("08_EDITING_PROJECT", base + "_concat.txt")
with open(lst, "w") as f:
    for e in timeline:
        f.write(f"file '{os.path.abspath(P('05_ANIMATIONS', e['file'], e['file'] + '.mp4'))}'\n")
silent = P("08_EDITING_PROJECT", base + "_video_only.mp4")
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", silent], check=True)

# ---- subtitles
def ts(x):
    h, r = divmod(x, 3600); m, s = divmod(r, 60)
    return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{int(round((s % 1) * 1000)):03d}"
srt = P("08_EDITING_PROJECT", base + ".srt")
with open(srt, "w") as f:
    for k, e in enumerate(timeline, 1):
        st = e["start"] + NARR_OFFSET
        en = st + durs[e["file"]]
        f.write(f"{k}\n{ts(st)} --> {ts(en)}\n{e['narration']}\n\n")

# ---- final mux with loudness normalisation (-14 LUFS, YouTube-friendly)
os.makedirs(P("07_FINAL_VIDEO"), exist_ok=True)
final = P("07_FINAL_VIDEO", base + ".mp4")
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", silent, "-i", mix_path, "-map", "0:v", "-map", "1:a",
                "-c:v", "copy", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", str(SR), "-ac", "2", "-c:a", "aac", "-b:a", "192k",
                "-shortest", "-movflags", "+faststart", final], check=True)
os.makedirs(P("10_EXPORTS"), exist_ok=True)
shutil.copy2(final, P("10_EXPORTS", base + ".mp4"))
shutil.copy2(srt, P("10_EXPORTS", base + ".srt"))
json.dump(dict(fps=FPS, resolution="1920x1080", total_duration=round(total, 3), narration_offset=NARR_OFFSET,
               music="../06_AUDIO/music/music_bed_curious_72bpm.wav", music_gain=0.16, scenes=timeline),
          open(P("08_EDITING_PROJECT", base + "_timeline.json"), "w"), indent=1)
print("FINAL", final, round(total, 2), "s")
