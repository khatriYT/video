"""Assemble animated scene clips + narration + SFX + music into the final video, plus editing-project files.

Usage: python3 assemble.py <project_dir> <first_id> <last_id> <output_basename>
"""
import json, os, shutil, subprocess, sys
import numpy as np
import soundfile as sf

_args = [x for x in sys.argv[1:] if not x.startswith("--")]
OPTS = dict(x[2:].split("=", 1) for x in sys.argv[1:] if x.startswith("--") and "=" in x)
proj, a, b, base = _args[0], int(_args[1]), int(_args[2]), _args[3]
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


# SFX cues: scene id -> list of (file, time in seconds, relative gain, loop_seconds)
# Gains are relative; everything is scaled by SFX_MASTER and ducked under the narration.
SFX_MASTER = 0.28   # about -11 dB vs. v1 (user feedback: effects were too loud)


def cues(i, T):
    c = {
        1: [("clock_tick", k * 0.5, 0.35, None) for k in range(int(0.5 * T / 0.5) + 1)] +
           [("mosquito_buzz", 0.0, 0.25, 0.68 * T), ("thud", 0.68 * T + 0.5, 0.5, None)],
        2: [("whoosh", 0.12 * T, 0.6, None)],
        3: [("mosquito_buzz", 0.0, 0.35, 0.45 * T), ("puff", 0.45 * T, 0.7, None)],
        4: [("scratch", 0.0, 0.5, None), ("sparkle", 0.72 * T, 0.5, None)],
        5: [("whoosh", 0.12 * T, 0.5, None)],
        6: [("pop", 0.42 * T, 0.6, None), ("sparkle", 0.47 * T, 0.5, None)],
        9: [("thud", 0.08 * T + 0.364 * 0.52 * T, 0.7, None)],
        10: [("pop", 0.3 * T, 0.7, None)],
        12: [("thud", 0.55 * T, 0.5, None), ("sparkle", 0.72 * T, 0.5, None)],
        19: [("mosquito_buzz", 0.2 * T, 0.15, 0.7 * T)],
        25: [("puff", 0.82 * T, 0.7, None)],
        49: [("whoosh", 0.05 * T, 0.5, None)],
        66: [("pop", (0.12 + k * 0.22) * T, 0.6, None) for k in range(3)],
        75: [("pop", 0.7 * T, 0.6, None)],
        77: [("thud", 0.7 * T, 0.7, None)],
        81: [("pop", 0.9 * T, 0.5, None)],
        82: [("whoosh", 0.15 * T, 0.5, None)],
        97: [("mosquito_buzz", 0.35 * T, 0.15, 0.55 * T)],
    }
    return c.get(i, [])


MUSIC_FILE = "music_bed_curious_72bpm.wav"
if "sfx" in OPTS:                      # per-project cue sheet, e.g. --sfx=sfx_bees
    import importlib
    _m = importlib.import_module(OPTS["sfx"])
    cues = _m.cues
    SFX_MASTER = getattr(_m, "SFX_MASTER", SFX_MASTER)
    MUSIC_FILE = getattr(_m, "MUSIC_FILE", MUSIC_FILE)

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
# voice-activity envelope (10 ms blocks) used to duck music and SFX under the narration
blk = SR // 100
nb = n // blk
rms = np.sqrt(np.mean(voice[: nb * blk].reshape(nb, blk) ** 2, axis=1))
active = (rms > 0.01).astype(np.float32)
k = np.ones(25, np.float32) / 25                      # 250 ms smoothing
active = np.clip(np.convolve(np.convolve(active, k, "same"), k, "same") * 1.5, 0, 1)
env = np.repeat(active, blk)
env = np.concatenate([env, np.full(n - len(env), env[-1] if len(env) else 0, np.float32)])
fx = fx * SFX_MASTER * (1 - 0.45 * env)               # SFX: -11 dB master, another ~-5 dB while speaking
music = load(P("06_AUDIO", "music", MUSIC_FILE))
music = np.resize(music, n) * (0.17 - 0.07 * env)      # music bed ducks under the voice
fo = int(2.5 * SR); music[-fo:] *= np.linspace(1, 0, fo)
fi = int(0.8 * SR); music[:fi] *= np.linspace(0, 1, fi)
vpk = np.abs(voice).max()
voice = voice / max(vpk, 1e-9) * 0.8
mix = voice + fx + music
mix = mix / max(1.0, np.abs(mix).max() / 0.95)
os.makedirs(P("08_EDITING_PROJECT"), exist_ok=True)
mix_path = P("08_EDITING_PROJECT", base + "_audio_mix.wav")
sf.write(mix_path, mix, SR, subtype="PCM_16")
sf.write(P("08_EDITING_PROJECT", base + "_voice_only.wav"), voice, SR, subtype="PCM_16")
sf.write(P("08_EDITING_PROJECT", base + "_sfx_only.wav"), fx, SR, subtype="PCM_16")
sf.write(P("08_EDITING_PROJECT", base + "_music_only.wav"), music, SR, subtype="PCM_16")
print("levels (peak): voice %.2f  sfx %.2f  music %.2f" % (np.abs(voice).max(), np.abs(fx).max(), np.abs(music).max()))
print("levels (rms):  voice %.3f  sfx %.4f  music %.4f" % (np.sqrt(np.mean(voice ** 2)), np.sqrt(np.mean(fx ** 2)), np.sqrt(np.mean(music ** 2))))

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
meas = subprocess.run(["ffmpeg", "-hide_banner", "-i", mix_path, "-af", "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json",
                       "-f", "null", "-"], capture_output=True, text=True).stderr
mj = json.loads(meas[meas.rindex("{"):meas.rindex("}") + 1])
ln = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={mj['input_i']}:measured_TP={mj['input_tp']}:"
      f"measured_LRA={mj['input_lra']}:measured_thresh={mj['input_thresh']}:offset={mj['target_offset']}:linear=true")
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", silent, "-i", mix_path, "-map", "0:v", "-map", "1:a",
                "-c:v", "copy", "-af", ln, "-ar", str(SR), "-ac", "2", "-c:a", "aac", "-b:a", "192k",
                "-shortest", "-movflags", "+faststart", final], check=True)
os.makedirs(P("10_EXPORTS"), exist_ok=True)
shutil.copy2(final, P("10_EXPORTS", base + ".mp4"))
shutil.copy2(srt, P("10_EXPORTS", base + ".srt"))
json.dump(dict(fps=FPS, resolution="1920x1080", total_duration=round(total, 3), narration_offset=NARR_OFFSET,
               music="../06_AUDIO/music/music_bed_curious_72bpm.wav", music_gain=0.16, scenes=timeline),
          open(P("08_EDITING_PROJECT", base + "_timeline.json"), "w"), indent=1)
print("FINAL", final, round(total, 2), "s")
