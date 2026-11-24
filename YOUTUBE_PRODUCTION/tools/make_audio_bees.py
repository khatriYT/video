"""Episode 2 audio assets (original, synthesized): bright music bed + bee/UI sound effects.

Usage: python3 make_audio_bees.py <project_dir>
"""
import os, sys
import numpy as np
import soundfile as sf

SR = 48000
proj = sys.argv[1]
sfx_dir = os.path.join(proj, "06_AUDIO", "sound_effects")
mus_dir = os.path.join(proj, "06_AUDIO", "music")
rng = np.random.default_rng(9)
t_ = lambda d: np.arange(int(d * SR)) / SR


def env(n, a=0.005, r=0.1):
    e = np.ones(n); na, nr = int(a * SR), int(r * SR)
    if na: e[:na] = np.linspace(0, 1, na)
    if nr: e[-nr:] *= np.linspace(1, 0, nr)
    return e


def lowpass(x, alpha):
    y = np.empty_like(x); acc = 0.0
    for i, v in enumerate(x):
        acc += alpha * (v - acc); y[i] = acc
    return y


def save(name, x, d=sfx_dir, peak=0.9):
    x = x / (np.max(np.abs(x)) + 1e-9) * peak
    sf.write(os.path.join(d, name + ".wav"), x.astype(np.float32), SR)
    print(name, round(len(x) / SR, 2))


# bee buzz: lower, rounder than the mosquito (~230 Hz), 3 s loop
t = t_(3.0)
f = 230 + 12 * np.sin(2 * np.pi * 5 * t) + 6 * np.sin(2 * np.pi * 0.7 * t)
ph = 2 * np.pi * np.cumsum(f) / SR
buzz = sum(np.sin(k * ph) / (k ** 1.3) for k in range(1, 10)) * (0.8 + 0.2 * np.sin(2 * np.pi * 31 * t))
save("bee_buzz", lowpass(buzz, 0.25) * env(len(t), 0.08, 0.08), peak=0.6)

t = t_(0.18); f = np.linspace(520, 1500, len(t))
save("pop", np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 22), peak=0.55)
t = t_(0.35)
save("stamp", (np.sin(2 * np.pi * 90 * t) + 0.5 * lowpass(rng.standard_normal(len(t)), 0.2)) * np.exp(-t * 18), peak=0.7)
t = t_(0.03)
save("tick", np.sin(2 * np.pi * 3200 * t) * np.exp(-t * 200), peak=0.35)
t = t_(0.9)
save("chime", sum(np.sin(2 * np.pi * fr * t) * np.exp(-t * (4 + i)) / (i + 1) for i, fr in enumerate([1318, 1760, 2093, 2637])), peak=0.4)
t = t_(0.7)
save("whoosh", lowpass(rng.standard_normal(len(t)), 0.06) * np.sin(np.pi * t / 0.7) ** 2, peak=0.45)
t = t_(0.06)
save("type_key", lowpass(rng.standard_normal(len(t)), 0.5) * np.exp(-t * 120), peak=0.3)

# music: sunny, curious 84 bpm, F major pad + marimba-like plucks, 40 bars (~114 s loop)
bpm, bars = 84, 40
beat = 60 / bpm
chords = [[53, 57, 60], [50, 53, 57], [46, 50, 53], [48, 52, 55]]  # F, Dm, Bb, C
hz = lambda m: 440 * 2 ** ((m - 69) / 12)
total = bars * 4 * beat
music = np.zeros(int(total * SR) + SR)
for b in range(bars):
    ch = chords[b % 4]; start = int(b * 4 * beat * SR); t = t_(4 * beat + 0.8)
    pad = sum(np.sin(2 * np.pi * hz(m) * t) + 0.25 * np.sin(2 * np.pi * hz(m) * 2.002 * t) for m in ch) * env(len(t), 0.7, 1.0) * 0.14
    bass = np.sin(2 * np.pi * hz(ch[0] - 12) * t) * env(len(t), 0.05, 0.6) * 0.2
    seg_ = music[start:start + len(t)]; seg_ += (pad + bass)[: len(seg_)]
    pattern = [0, 2, 1, 2, 0, 2, 1, 2] if b % 8 < 4 else [0, 1, 2, 1, 0, 2, 1, 0]
    for k in range(8):
        if (b + k) % 7 == 6:
            continue  # little rests keep it from feeling mechanical
        s0 = start + int(k * beat / 2 * SR); tt = t_(0.45)
        fq = hz(ch[pattern[k]] + 12)
        mar = (np.sin(2 * np.pi * fq * tt) + 0.3 * np.sin(2 * np.pi * fq * 4 * tt) * np.exp(-tt * 40)) * np.exp(-tt * 9) * 0.075
        seg_ = music[s0:s0 + len(tt)]; seg_ += mar[: len(seg_)]
music = lowpass(music, 0.4)
save("music_bed_sunny_84bpm", music, d=mus_dir, peak=0.7)
