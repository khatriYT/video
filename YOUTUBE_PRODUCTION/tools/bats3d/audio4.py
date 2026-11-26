#!/usr/bin/env python3
"""Episode 4 audio: reuses the Episode 3 engine (vulture3d/audio.py) with a bat-episode mood map, new
ambiences/SFX (night insects, cave drips, swarm flutter, hover wingbeats, tractor, turbines, jungle dawn) and
cue rules driven by the v3 shot list. Everything is synthesised with numpy (original, royalty-free).

python3 tools/bats3d/audio4.py <project> assets|music|assemble <basename>
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "vulture3d"))
sys.path.insert(0, HERE)
import audio as A  # noqa: E402

A.SCORE_NAME = "score_bats.wav"
A.MOOD = {
    "Cold open": (1.0, 0.45, 0.2, 0.0, 0.25, "minor"),
    "The night shift": (0.5, 0.7, 0.75, 0.0, 0.8, "major"),
    "The white nose": (1.0, 0.5, 0.15, 0.0, 0.2, "minor"),
    "The experiment nobody wanted": (0.9, 0.6, 0.1, 0.35, 0.2, "minor"),
    "The bug hunters": (0.5, 0.7, 0.7, 0.5, 0.75, "major"),
    "The night gardeners": (0.5, 0.9, 0.8, 0.0, 0.9, "major"),
    "Aren't bats dangerous?": (0.9, 0.5, 0.3, 0.2, 0.35, "minor"),
    "A world without bats": (0.7, 0.85, 0.55, 0.0, 0.65, "major"),
}
SR = A.SR
rng = np.random.default_rng(44)


def make_assets(proj):
    A.make_assets(proj)
    d = os.path.join(proj, "10_Audio", "sound_effects")
    t_ = A.t_
    # night insects: layered cricket chirps + katydid buzz (8 s loop)
    T = 8.0
    t = t_(T)
    x = np.zeros_like(t)
    for k in range(9):
        f = rng.uniform(3800, 5200)
        rate = rng.uniform(2.0, 3.6)
        ph = rng.uniform(0, 1)
        gate = (np.sin(2 * np.pi * rate * t + ph * 6.28) > 0.55).astype(float)
        trill = (np.sin(2 * np.pi * 38 * t) > 0).astype(float)
        x += np.sin(2 * np.pi * f * t) * gate * trill * rng.uniform(0.3, 1.0)
    kat = A.fft_bandpass(rng.standard_normal(len(t)), 6000, 9000) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.4 * t))
    A.save(os.path.join(d, "crickets.wav"), A.fft_lowpass(x, 7000) * 0.6 + kat * 0.25, 0.45)
    # cave: low rumble + random drips with resonant plinks
    T = 10.0
    t = t_(T)
    rum = A.fft_lowpass(rng.standard_normal(len(t)), 140) * 1.5
    drips = np.zeros_like(t)
    for k in range(14):
        s0 = int(rng.uniform(0, T - 1) * SR)
        tt = t_(0.6)
        f = rng.uniform(900, 2200)
        pl = np.sin(2 * np.pi * (f + 300 * np.exp(-tt * 30)) * tt) * np.exp(-tt * 9) * rng.uniform(0.2, 0.6)
        drips[s0:s0 + len(pl)] += pl
    A.save(os.path.join(d, "cave.wav"), rum + drips, 0.5)
    # swarm: thousands of wingbeats = amplitude-modulated noise at 7-10 Hz, plus faint high chatter
    T = 6.0
    t = t_(T)
    n = rng.standard_normal(len(t))
    am = 0.55 + 0.45 * np.abs(np.sin(2 * np.pi * 8.3 * t)) * (0.7 + 0.3 * np.sin(2 * np.pi * 0.6 * t))
    chat = A.fft_bandpass(rng.standard_normal(len(t)), 5000, 9000) * (np.sin(2 * np.pi * 13 * t) > 0.6) * 0.25
    A.save(os.path.join(d, "swarm.wav"), A.fft_bandpass(n, 150, 1800) * am + chat, 0.5)
    # hover wingbeat (close bat)
    T = 3.0
    t = t_(T)
    hv = A.fft_lowpass(rng.standard_normal(len(t)), 700) * (np.abs(np.sin(2 * np.pi * 11 * t)) ** 2)
    A.save(os.path.join(d, "hover.wav"), hv, 0.5)
    # tractor: engine harmonics with slight wobble
    T = 6.0
    t = t_(T)
    f0 = 38 + 1.5 * np.sin(2 * np.pi * 0.3 * t)
    ph = 2 * np.pi * np.cumsum(f0) / SR
    eng = sum(np.sin(k * ph) / k for k in range(1, 14)) + A.fft_lowpass(rng.standard_normal(len(t)), 600) * 0.4
    A.save(os.path.join(d, "tractor.wav"), eng, 0.5)
    # turbine: periodic blade whoosh that slows down (6 s)
    T = 9.0
    t = t_(T)
    rate = 0.75 * np.exp(-t / 3.0) + 0.02
    ph = 2 * np.pi * np.cumsum(rate) / SR
    tb = A.fft_bandpass(rng.standard_normal(len(t)), 200, 1200) * (0.3 + 0.7 * np.abs(np.sin(ph * 1.5)) ** 4)
    A.save(os.path.join(d, "turbine.wav"), tb * (0.4 + 0.6 * np.exp(-t / 4.0)), 0.5)
    # jungle dawn: insects + bird whistles
    T = 8.0
    t = t_(T)
    j = A.fft_bandpass(rng.standard_normal(len(t)), 3000, 8000) * 0.15
    for k in range(10):
        s0 = int(rng.uniform(0, T - 1) * SR)
        tt = t_(0.5)
        f = rng.uniform(1800, 3400) + 900 * np.sin(2 * np.pi * rng.uniform(4, 9) * tt)
        bird = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * tt / 0.5) ** 2 * 0.35
        j[s0:s0 + len(bird)] += bird
    A.save(os.path.join(d, "jungle.wav"), j, 0.45)
    print("ep4 sfx done")


def cues(s, T):
    from shots4 import SHOTS
    v = s["visual"]
    c = []
    if v["type"] == "plate":
        sh = SHOTS.get(v["shot"], {})
        env, st = sh.get("env"), sh.get("state")
        if env == "cave":
            c.append(("cave", 0.0, 0.5, T))
        elif env in ("hill", "agave", "farm", "mine", "wind"):
            c.append(("wind", 0.0, 0.25, T))
            if st in ("dusk", "night", "blue") or env == "mine":
                c.append(("crickets", 0.0, 0.32, T))
        elif env == "tropic":
            c.append(("jungle" if st == "dawn" else "crickets", 0.0, 0.35, T))
        elif env == "sky":
            c.append(("wind", 0.0, 0.35, T))
        sw = sh.get("swarm")
        if sw:
            c.append(("swarm", 0.0, min(0.6, 0.12 + 0.5 * sw[3]), T))
        acts = [a[0] for a in sh.get("actors", [])]
        if "nectar" in acts:
            c.append(("hover", 0.2, 0.4, T - 0.2))
        if "tractor" in acts:
            c.append(("tractor", 0.0, 0.45, T))
        if "rotors" in acts:
            c.append(("turbine", 0.0, 0.5, None))
    if v.get("tab"):
        c.append(("whoosh", 0.25, 0.35, None))
    tx = (v.get("text") or {}).get("style")
    if tx == "chapter":
        c.append(("whoosh", 0.25, 0.5, None))
    if tx == "title":
        c += [("riser", 0.0, 0.5, None), ("boom", 0.6, 0.8, None)]
    if tx == "end":
        c.append(("boom", 1.2, 0.5, None))
    if tx == "callout":
        c.append(("pop", 0.8, 0.35, None))
    if v["type"] == "card":
        c.append(("pop", 0.2, 0.4, None))
    return c


A.cues = cues

if __name__ == "__main__":
    proj, what = sys.argv[1], sys.argv[2]
    if what == "assets":
        make_assets(proj)
    elif what == "music":
        A.make_music(proj)
    elif what == "assemble":
        A.assemble(proj, sys.argv[3])
