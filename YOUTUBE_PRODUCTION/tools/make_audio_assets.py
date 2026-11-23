"""Synthesize original (royalty-free) music bed + sound effects with numpy.

Usage: python3 make_audio_assets.py <project_dir>
"""
import os, sys
import numpy as np
import soundfile as sf

SR = 48000
proj = sys.argv[1]
sfx_dir = os.path.join(proj, "06_AUDIO", "sound_effects")
mus_dir = os.path.join(proj, "06_AUDIO", "music")
rng = np.random.default_rng(3)


def t_(d):
    return np.arange(int(d * SR)) / SR


def env(n, a=0.005, r=0.1):
    e = np.ones(n)
    na, nr = int(a * SR), int(r * SR)
    if na: e[:na] = np.linspace(0, 1, na)
    if nr: e[-nr:] *= np.linspace(1, 0, nr)
    return e


def lowpass(x, alpha):
    y = np.empty_like(x); acc = 0.0
    for i, v in enumerate(x):
        acc += alpha * (v - acc); y[i] = acc
    return y


def save(path, x, peak=0.9):
    x = x / (np.max(np.abs(x)) + 1e-9) * peak
    sf.write(path, x.astype(np.float32), SR)
    print(path, round(len(x) / SR, 2))


# --- mosquito buzz (2 s loop): bright saw with vibrato + tremolo
t = t_(2.0)
f = 560 + 25 * np.sin(2 * np.pi * 7 * t) + 10 * np.sin(2 * np.pi * 1.3 * t)
ph = 2 * np.pi * np.cumsum(f) / SR
saw = sum(np.sin(k * ph) / k for k in range(1, 9))
buzz = saw * (0.75 + 0.25 * np.sin(2 * np.pi * 23 * t)) * env(len(t), 0.05, 0.05)
save(os.path.join(sfx_dir, "mosquito_buzz.wav"), buzz, 0.6)

# --- clock tick
t = t_(0.06)
tick = (rng.standard_normal(len(t)) * 0.4 + np.sin(2 * np.pi * 2400 * t)) * np.exp(-t * 90)
save(os.path.join(sfx_dir, "clock_tick.wav"), tick, 0.5)

# --- puff (filtered noise burst)
t = t_(0.5)
puff = lowpass(rng.standard_normal(len(t)), 0.08) * np.exp(-t * 9) * env(len(t), 0.01, 0.05)
save(os.path.join(sfx_dir, "puff.wav"), puff, 0.7)

# --- pop (sine sweep)
t = t_(0.18)
f = np.linspace(500, 1400, len(t))
pop = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 22)
save(os.path.join(sfx_dir, "pop.wav"), pop, 0.55)

# --- sparkle chime
t = t_(0.9)
chime = sum(np.sin(2 * np.pi * fr * t) * np.exp(-t * (4 + i)) / (i + 1) for i, fr in enumerate([1568, 2093, 2637, 3136]))
save(os.path.join(sfx_dir, "sparkle.wav"), chime, 0.4)

# --- thud (hat landing)
t = t_(0.25)
thud = (np.sin(2 * np.pi * 110 * t) + 0.3 * lowpass(rng.standard_normal(len(t)), 0.1)) * np.exp(-t * 25)
save(os.path.join(sfx_dir, "thud.wav"), thud, 0.6)

# --- whoosh
t = t_(1.0)
n = rng.standard_normal(len(t))
wh = lowpass(n, 0.05) * np.sin(np.pi * t / 1.0) ** 2
save(os.path.join(sfx_dir, "whoosh.wav"), wh, 0.5)

# --- scratch (short rough noise bursts)
t = t_(0.9)
sc = rng.standard_normal(len(t)) * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 7 * t))) * env(len(t), 0.01, 0.1)
save(os.path.join(sfx_dir, "scratch.wav"), lowpass(sc, 0.35), 0.35)

# --- music bed: calm curious pad + soft plucks, 4-chord loop, 72 BPM, ~108 s
bpm, bars = 72, 32
beat = 60 / bpm
chords = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]  # Am F C G (MIDI)
hz = lambda m: 440 * 2 ** ((m - 69) / 12)
total = bars * 4 * beat
music = np.zeros(int(total * SR) + SR)
for b in range(bars):
    ch = chords[b % 4]
    start = int(b * 4 * beat * SR)
    t = t_(4 * beat + 0.8)
    pad = sum(np.sin(2 * np.pi * hz(m) * t) + 0.3 * np.sin(2 * np.pi * hz(m) * 2.003 * t) for m in ch)
    pad *= env(len(t), 0.9, 1.2) * 0.18
    music[start:start + len(t)] += pad[: len(music) - start]
    bass = np.sin(2 * np.pi * hz(ch[0] - 12) * t) * env(len(t), 0.2, 0.8) * 0.22
    music[start:start + len(t)] += bass[: len(music) - start]
    # plucks on 8th notes (arpeggio)
    arp = [ch[0] + 12, ch[1] + 12, ch[2] + 12, ch[1] + 12]
    for k in range(8):
        s0 = start + int(k * beat / 2 * SR)
        tt = t_(0.6)
        pl = (np.sin(2 * np.pi * hz(arp[k % 4]) * tt) + 0.4 * np.sin(4 * np.pi * hz(arp[k % 4]) * tt)) * np.exp(-tt * 7) * 0.07
        music[s0:s0 + len(tt)] += pl[: len(music) - s0]
music = lowpass(music, 0.35)
save(os.path.join(mus_dir, "music_bed_curious_72bpm.wav"), music, 0.7)
