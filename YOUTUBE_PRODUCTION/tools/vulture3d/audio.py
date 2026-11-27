#!/usr/bin/env python3
"""Episode 3 audio: original synthesized score (timed to chapters) + SFX, then mix + final assembly.

Usage:
  python3 tools/vulture3d/audio.py <project_dir> assets     # SFX library -> 10_Audio/sound_effects/
  python3 tools/vulture3d/audio.py <project_dir> music      # score timed to 09_Animation/scene_timing.json
  python3 tools/vulture3d/audio.py <project_dir> assemble <basename>
Everything is generated with numpy (royalty-free, original). Mix: narration on top, music bed and SFX ducked
under the voice, two-pass loudnorm to -14 LUFS / -1.5 dBTP.
"""
import json
import os
import shutil
import subprocess
import sys

import numpy as np
import soundfile as sf

SR = 48000
NARR_OFFSET = 0.12
SCORE_NAME = "score_vultures.wav"
rng = np.random.default_rng(31)


def t_(d):
    return np.arange(int(d * SR)) / SR


def env(n, a=0.01, r=0.2):
    e = np.ones(n)
    na, nr = min(n, int(a * SR)), min(n, int(r * SR))
    if na:
        e[:na] = np.linspace(0, 1, na)
    if nr:
        e[-nr:] *= np.linspace(1, 0, nr)
    return e


def onepole(x, alpha):
    """Vectorised-ish one-pole low-pass via cumulative trick in blocks (alpha small = darker)."""
    y = np.empty_like(x)
    acc = 0.0
    B = 4096
    for s in range(0, len(x), B):
        blk = x[s:s + B]
        out = np.empty_like(blk)
        a = acc
        for i in range(len(blk)):
            a += alpha * (blk[i] - a)
            out[i] = a
        acc = a
        y[s:s + B] = out
    return y


def fft_lowpass(x, cutoff):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1 / (1 + (f / cutoff) ** 4)
    return np.fft.irfft(X, len(x))


def fft_bandpass(x, lo, hi):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= (1 / (1 + (lo / np.maximum(f, 1)) ** 4)) * (1 / (1 + (f / hi) ** 4))
    return np.fft.irfft(X, len(x))


def norm(x, peak=0.9):
    return x / (np.max(np.abs(x)) + 1e-9) * peak


def save(path, x, peak=0.9):
    sf.write(path, norm(x, peak).astype(np.float32), SR)


hz = lambda m: 440 * 2 ** ((m - 69) / 12)


# ------------------------------------------------------------------ SFX
def make_assets(proj):
    d = os.path.join(proj, "10_Audio", "sound_effects")
    os.makedirs(d, exist_ok=True)
    # wind bed (10 s loop, crossfaded)
    n = rng.standard_normal(int(10 * SR))
    w = fft_bandpass(n, 120, 900) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.11 * t_(10)) ** 2)
    save(os.path.join(d, "wind.wav"), w * env(len(w), 0.5, 0.5), 0.5)
    # fly buzz (3 s loop)
    t = t_(3.0)
    f = 190 + 25 * np.sin(2 * np.pi * 3.1 * t) + 14 * np.sin(2 * np.pi * 7.3 * t)
    ph = 2 * np.pi * np.cumsum(f) / SR
    buzz = sum(np.sin(k * ph) / k ** 1.1 for k in range(1, 12)) * (0.7 + 0.3 * np.sin(2 * np.pi * 0.9 * t))
    save(os.path.join(d, "flies.wav"), fft_lowpass(buzz, 2500) * env(len(t), 0.2, 0.2), 0.5)
    # whoosh
    t = t_(0.8)
    wh = fft_bandpass(rng.standard_normal(len(t)), 300, 3000) * np.sin(np.pi * t / 0.8) ** 3
    save(os.path.join(d, "whoosh.wav"), wh, 0.5)
    # wing flap: low "whump" bursts
    t = t_(0.5)
    fl = fft_lowpass(rng.standard_normal(len(t)), 400) * np.exp(-t * 9)
    save(os.path.join(d, "wingflap.wav"), fl, 0.6)
    # pop
    t = t_(0.16)
    fr = np.linspace(600, 1400, len(t))
    save(os.path.join(d, "pop.wav"), np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t * 24), 0.5)
    # stamp
    t = t_(0.4)
    save(os.path.join(d, "stamp.wav"), (np.sin(2 * np.pi * 85 * t) + 0.6 * fft_lowpass(rng.standard_normal(len(t)), 1500))
         * np.exp(-t * 16), 0.7)
    # tick
    t = t_(0.03)
    save(os.path.join(d, "tick.wav"), np.sin(2 * np.pi * 3000 * t) * np.exp(-t * 200), 0.3)
    # rain loop
    n = rng.standard_normal(int(6 * SR))
    drops = np.zeros_like(n)
    idx = rng.integers(0, len(n) - 400, 900)
    for i in idx:
        drops[i:i + 400] += np.exp(-np.arange(400) / 60) * rng.uniform(0.3, 1)
    save(os.path.join(d, "rain.wav"), fft_bandpass(n, 800, 7000) * 0.5 + fft_lowpass(drops * rng.standard_normal(len(n)), 4000),
         0.5)
    # low riser/impact for title
    t = t_(2.0)
    rs = fft_lowpass(rng.standard_normal(len(t)), 900) * (t / 2.0) ** 2
    save(os.path.join(d, "riser.wav"), rs, 0.5)
    t = t_(1.6)
    save(os.path.join(d, "boom.wav"), np.sin(2 * np.pi * (55 - 20 * t) * t) * np.exp(-t * 3.5), 0.8)
    print("sfx done:", sorted(os.listdir(d)))


# ------------------------------------------------------------------ music
MOOD = {  # section -> (drone, pad, pluck density 0..1, pulse, brightness 0..1, chord set)
    "Cold open": (1.0, 0.4, 0.25, 0.0, 0.3, "minor"),
    "Meet the cleanup crew": (0.6, 0.7, 0.7, 0.0, 0.7, "minor"),
    "The collapse": (1.0, 0.6, 0.2, 0.0, 0.2, "minor"),
    "A world without vultures": (1.0, 0.4, 0.15, 0.6, 0.25, "minor"),
    "The bill": (0.9, 0.7, 0.0, 0.3, 0.2, "minor"),
    "Ripples": (0.6, 0.7, 0.4, 0.0, 0.5, "minor"),
    "It's happening again": (1.0, 0.5, 0.2, 0.5, 0.3, "minor"),
    "Could anything replace them?": (0.6, 0.6, 0.5, 0.0, 0.5, "minor"),
    "Holding the line": (0.5, 0.9, 0.8, 0.0, 0.9, "major"),
}
CHORDS = {"minor": [[50, 53, 57], [46, 50, 53], [41, 45, 48], [48, 52, 55]],     # Dm Bb F C
          "major": [[41, 45, 48], [48, 52, 55], [50, 53, 57], [46, 50, 53]]}     # F C Dm Bb


def pluck(freq, dur, bright):
    t = t_(dur)
    x = np.zeros_like(t)
    for k in range(1, 9):
        x += np.sin(2 * np.pi * freq * k * t) * np.exp(-t * (3 + k * (4 - 3 * bright))) / k ** (1.4 - 0.5 * bright)
    return x * env(len(t), 0.003, 0.05)


def make_music(proj):
    P = lambda *x: os.path.join(proj, *x)
    sb = json.load(open(P("06_Storyboard", "storyboard.json")))["scenes"]
    timing = json.load(open(P("09_Animation", "scene_timing.json")))
    # section spans
    spans, t0 = [], 0.0
    for s in sb:
        d = timing[s["file"]]["duration"]
        if spans and spans[-1][0] == s["section"]:
            spans[-1][2] = t0 + d
        else:
            spans.append([s["section"], t0, t0 + d])
        t0 += d
    total = t0 + 1.0
    n = int(total * SR)
    out = np.zeros(n)
    bpm = 72
    beat = 60 / bpm
    bar = 4 * beat

    def ctl(tt, idx):     # smooth per-section control value
        vals = np.zeros_like(tt)
        for name, a, b in spans:
            m = MOOD[name][idx]
            vals[(tt >= a) & (tt < b)] = m
        vals[tt >= spans[-1][2]] = MOOD[spans[-1][0]][idx]
        k = int(1.5 * SR / 200)
        sm = np.convolve(np.repeat(vals[::200], 1)[:], np.ones(k) / k, "same")
        return np.repeat(sm, 200)[:len(tt)]

    tt = np.arange(n) / SR
    c_drone, c_pad, c_pulse = ctl(tt, 0), ctl(tt, 1), ctl(tt, 3)
    # tanpura-like drone: D2 + A2 + D3 with slow beating harmonics
    dr = np.zeros(n)
    for f, g in ((hz(38), 1.0), (hz(45), 0.6), (hz(50), 0.45)):
        for k in range(1, 7):
            dr += g * np.sin(2 * np.pi * f * k * tt * (1 + 0.0007 * k) + k) / k ** 1.3 * \
                  (0.75 + 0.25 * np.sin(2 * np.pi * (0.07 + 0.03 * k) * tt + k))
    out += fft_lowpass(dr, 1800) * 0.11 * c_drone
    # pads + plucks per bar, following the section mood
    nb = int(total / bar) + 1
    for b in range(nb):
        start = b * bar
        sec = next((sp for sp in spans if sp[1] <= start < sp[2]), spans[-1])
        drone, pad_g, dens, pulse, bright, cs = MOOD[sec[0]]
        ch = CHORDS[cs][b % 4]
        s0 = int(start * SR)
        tt_b = t_(bar + 1.5)
        pad = sum(np.sin(2 * np.pi * hz(m) * tt_b) + 0.3 * np.sin(2 * np.pi * hz(m) * 2.003 * tt_b) +
                  0.15 * np.sin(2 * np.pi * hz(m + 12) * 0.998 * tt_b) for m in ch)
        pad *= env(len(tt_b), 1.0, 1.4) * 0.05
        seg = out[s0:s0 + len(pad)]
        seg += pad[:len(seg)] * c_pad[s0:s0 + len(seg)]
        notes = [ch[0] + 12, ch[1] + 12, ch[2] + 12, ch[1] + 24, ch[2] + 12, ch[0] + 24, ch[1] + 12, ch[2] + 24]
        for k in range(8):
            if rng.random() > dens:
                continue
            ps = int((start + k * beat / 2) * SR)
            if ps >= n:
                break
            pl = pluck(hz(notes[k]), 1.6, bright) * 0.045
            seg2 = out[ps:ps + len(pl)]
            seg2 += pl[:len(seg2)]
        if pulse > 0:
            for k in range(4):
                ps = int((start + k * beat) * SR)
                tp = t_(0.35)
                kick = np.sin(2 * np.pi * (62 - 30 * tp) * tp) * np.exp(-tp * 11) * 0.09 * pulse
                seg3 = out[ps:ps + len(kick)]
                seg3 += kick[:len(seg3)]
    # final swell & fade
    fo = int(4 * SR)
    out[-fo:] *= np.linspace(1, 0, fo)
    fi = int(1.5 * SR)
    out[:fi] *= np.linspace(0, 1, fi)
    os.makedirs(P("10_Audio", "music"), exist_ok=True)
    save(P("10_Audio", "music", SCORE_NAME), out, 0.8)
    json.dump([dict(section=a, start=round(b, 2), end=round(c, 2)) for a, b, c in spans],
              open(P("10_Audio", "music", "score_sections.json"), "w"), indent=1)
    print("music", round(total, 1), "s,", len(spans), "sections")


# ------------------------------------------------------------------ cue sheet + assemble
OUTDOOR = {"P00", "P01", "P02", "P03", "P03C", "P04", "P05", "P06", "P07", "P08", "P09", "P12", "P13", "P14", "P15",
           "P17", "P20", "P21", "P22", "P24", "A02", "A03"}


def cues(s, T):
    v = s["visual"]
    c = []
    shot = v.get("shot")
    if v["type"] in ("plate", "anim") and shot in OUTDOOR:
        c.append(("wind", 0.0, 0.35, T))
    if "flies" in v.get("fx", []):
        c.append(("flies", 0.0, 0.3, T))
    if "rain" in v.get("fx", []):
        c.append(("rain", 0.0, 0.45, T))
    if shot in ("A01", "P01", "A03"):
        c += [("wingflap", 0.6 + k * 1.3, 0.35, None) for k in range(int(T / 1.3) - 1)]
    if v.get("tab"):
        c.append(("whoosh", 0.25, 0.35, None))
    tx = (v.get("text") or {}).get("style")
    if tx == "chapter":
        c.append(("whoosh", 0.25, 0.5, None))
    if tx == "title":
        c += [("riser", 0.0, 0.5, None), ("boom", 0.6, 0.8, None)]
    if tx == "end":
        c.append(("boom", 1.2, 0.5, None))
    if v["type"] == "card":
        c.append(("pop", 0.2, 0.4, None))
        if v["card"] in ("bans", "suspects"):
            c += [("stamp", (0.8 + k * 0.8) if v["card"] == "bans" else (T - 1.4 + k * 0.25), 0.6, None)
                  for k in range(3)]
        if v["card"] == "trucks_numbers":
            c += [("tick", 0.6 + k * 0.08, 0.4, None) for k in range(28)]
    return c


def load(path):
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", path, "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).copy()


def assemble(proj, base):
    P = lambda *x: os.path.join(proj, *x)
    sb = json.load(open(P("06_Storyboard", "storyboard.json")))["scenes"]
    timing = json.load(open(P("09_Animation", "scene_timing.json")))
    durs = json.load(open(P("10_Audio", "narration", "durations.json")))
    timeline, t0 = [], 0.0
    for s in sb:
        clip = P("09_Animation", s["file"] + ".mp4")
        if not os.path.exists(clip):
            sys.exit("MISSING " + clip)
        T = timing[s["file"]]["duration"]
        timeline.append(dict(id=s["id"], file=s["file"], section=s["section"], start=round(t0, 3), duration=T,
                             narration=s["narration"], visual=s["visual"], clip=os.path.relpath(clip, P("11_Edit")),
                             audio=os.path.relpath(P("10_Audio", "narration", s["file"] + ".wav"), P("11_Edit"))))
        t0 += T
    total = t0
    n = int((total + 0.5) * SR)
    voice, fx = np.zeros(n, np.float32), np.zeros(n, np.float32)
    cache = {}
    for e, s in zip(timeline, sb):
        v = load(P("10_Audio", "narration", e["file"] + ".wav"))
        s0 = int((e["start"] + NARR_OFFSET) * SR)
        voice[s0:s0 + len(v)] += v[: n - s0]
        for (name, at, gain, loop) in cues(s, e["duration"]):
            x = cache.setdefault(name, load(P("10_Audio", "sound_effects", name + ".wav")))
            if loop:
                x = np.tile(x, int(np.ceil(loop * SR / len(x))))[: int(loop * SR)].copy()
                f = min(len(x) // 2, int(0.3 * SR))
                x[:f] *= np.linspace(0, 1, f)
                x[-f:] *= np.linspace(1, 0, f)
            s0 = int((e["start"] + at) * SR)
            if s0 < n:
                fx[s0:s0 + len(x)] += gain * x[: n - s0]
    blk = SR // 100
    nb = n // blk
    rms = np.sqrt(np.mean(voice[: nb * blk].reshape(nb, blk) ** 2, axis=1))
    active = (rms > 0.01).astype(np.float32)
    k = np.ones(25, np.float32) / 25
    active = np.clip(np.convolve(np.convolve(active, k, "same"), k, "same") * 1.5, 0, 1)
    envv = np.repeat(active, blk)
    envv = np.concatenate([envv, np.full(n - len(envv), envv[-1] if len(envv) else 0, np.float32)])
    fx = fx * 0.3 * (1 - 0.45 * envv)
    music = load(P("10_Audio", "music", SCORE_NAME))
    music = np.resize(music, n) * (0.22 - 0.1 * envv)
    voice = voice / max(np.abs(voice).max(), 1e-9) * 0.8
    mix = voice + fx + music
    mix = mix / max(1.0, np.abs(mix).max() / 0.95)
    os.makedirs(P("11_Edit"), exist_ok=True)
    for name, sig in (("audio_mix", mix), ("voice_only", voice), ("sfx_only", fx), ("music_only", music)):
        sf.write(P("11_Edit", f"{base}_{name}.wav"), sig, SR, subtype="PCM_16")
    print("rms voice %.3f sfx %.4f music %.4f" % (np.sqrt(np.mean(voice ** 2)), np.sqrt(np.mean(fx ** 2)),
                                                   np.sqrt(np.mean(music ** 2))))
    lst = P("11_Edit", base + "_concat.txt")
    with open(lst, "w") as f:
        for e in timeline:
            f.write(f"file '{os.path.abspath(P('09_Animation', e['file'] + '.mp4'))}'\n")
    silent = P("11_Edit", base + "_video_only.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", silent],
                   check=True)

    def ts(x):
        h, r = divmod(x, 3600)
        m, s_ = divmod(r, 60)
        return f"{int(h):02d}:{int(m):02d}:{int(s_):02d},{int(round((s_ % 1) * 1000)) % 1000:03d}"
    srt = P("11_Edit", base + ".srt")
    with open(srt, "w") as f:
        for i, e in enumerate(timeline, 1):
            st = e["start"] + NARR_OFFSET
            f.write(f"{i}\n{ts(st)} --> {ts(st + durs[e['file']])}\n{e['narration']}\n\n")
    mix_path = P("11_Edit", f"{base}_audio_mix.wav")
    meas = subprocess.run(["ffmpeg", "-hide_banner", "-i", mix_path, "-af",
                           "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
                          capture_output=True, text=True).stderr
    mj = json.loads(meas[meas.rindex("{"):meas.rindex("}") + 1])
    ln = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={mj['input_i']}:measured_TP={mj['input_tp']}:"
          f"measured_LRA={mj['input_lra']}:measured_thresh={mj['input_thresh']}:offset={mj['target_offset']}:linear=true")
    os.makedirs(P("12_Exports"), exist_ok=True)
    final = P("12_Exports", base + "_REVIEW.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", silent, "-i", mix_path, "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-af", ln, "-ar", str(SR), "-ac", "2", "-c:a", "aac", "-b:a", "192k",
                    "-shortest", "-movflags", "+faststart", final], check=True)
    shutil.copy2(srt, P("12_Exports", base + "_REVIEW.srt"))
    # chapters from sections
    chap, last = [], None
    for e in timeline:
        if e["section"] != last:
            m, s_ = divmod(int(e["start"]), 60)
            chap.append(f"{m}:{s_:02d} {e['section']}")
            last = e["section"]
    open(P("12_Exports", base + "_chapters.txt"), "w").write("\n".join(chap) + "\n")
    json.dump(dict(fps=24, resolution="1920x1080", total_duration=round(total, 3), narration_offset=NARR_OFFSET,
                   scenes=timeline), open(P("11_Edit", base + "_timeline.json"), "w"), indent=1)
    print("FINAL", final, round(total, 2), "s")


if __name__ == "__main__":
    proj, what = sys.argv[1], sys.argv[2]
    if what == "assets":
        make_assets(proj)
    elif what == "music":
        make_music(proj)
    elif what == "assemble":
        assemble(proj, sys.argv[3])
