#!/usr/bin/env python3
"""Episode 4 compositor (v3): plate + character pass (shadows, contact AO, depth occlusion) + 3D-projected bat
swarms from pre-rendered sprite atlases + particles (dust, snow, fireflies, moths, spray, pollen, seeds, sonar)
+ cinematic grade (contrast curve, split toning, saturation, bloom, vignette, grain) + eased camera move + on-screen
text. Card scenes use cards4 over a defocused 3D backdrop.

python3 tools/bats3d/compose4.py <project> timing
python3 tools/bats3d/compose4.py <project> render [ids] [--force]
"""
import json
import math
import os
import random
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "vulture3d"))
sys.path.insert(0, HERE)
from cards import H, W, ease, overlay_fn  # noqa: E402
from compose import MOVES, parse_ids  # noqa: E402

FPS = 24
ROOT = None
HOLD = {"title": 0.8, "end": 12.0, "chapter": 0.6}
GAP = 0.42


# ------------------------------------------------------------------ timing
def make_timing(proj):
    P = lambda *x: os.path.join(proj, *x)   # noqa: E731
    sb = json.load(open(P("06_Storyboard", "storyboard.json")))["scenes"]
    durs = json.load(open(P("10_Audio", "narration", "durations.json")))
    out, t = {}, 0.0
    for s in sb:
        d = durs[s["file"]] + GAP + 0.25
        st = (s["visual"].get("text") or {}).get("style")
        if st in HOLD:
            d += HOLD[st]
        if s["visual"]["type"] == "card":
            d += 0.3
        out[s["file"]] = dict(start=round(t, 3), duration=round(d, 3), narration=durs[s["file"]])
        t += d
    os.makedirs(P("09_Animation"), exist_ok=True)
    json.dump(out, open(P("09_Animation", "scene_timing.json"), "w"), indent=1)
    print("total", round(t, 1), "s")


# ------------------------------------------------------------------ camera projection
class Cam:
    def __init__(self, meta, size):
        M = np.array(meta["matrix"], dtype=np.float64)
        self.inv = np.linalg.inv(M)
        self.pos = M[:3, 3]
        self.W, self.H = size
        self.f = meta["lens"] / meta["sensor"] * self.W

    def project(self, P):
        """P: (n,3) world -> (x, y, depth) arrays; depth > 0 in front."""
        Ph = np.concatenate([P, np.ones((len(P), 1))], axis=1) @ self.inv.T
        z = -Ph[:, 2]
        zs = np.where(z > 1e-3, z, 1e-3)
        x = self.W / 2 + self.f * Ph[:, 0] / zs
        y = self.H / 2 - self.f * Ph[:, 1] / zs
        return x, y, z


def decode_depth(path, size):
    d = np.asarray(Image.open(path).resize(size, Image.NEAREST), dtype=np.float32)
    d = d / (65535.0 if d.max() > 256 else 255.0)
    return 10.0 * (1.0 / np.maximum(d, 1e-4) - 1.0)


# ------------------------------------------------------------------ sprites
class Atlas:
    def __init__(self, sp, preset, root):
        d = os.path.join(root, "sprites", f"{sp}_{preset}")
        self.meta = json.load(open(os.path.join(d, "meta.json")))
        self.frames = [Image.open(os.path.join(d, f"atlas_{f:02d}.png")).convert("RGBA")
                       for f in range(self.meta["frames"])]
        self.cell = self.meta["cell"]
        self.naz = self.meta["az"]
        self.els = self.meta["el"]
        self.cache = {}
        dirs = []
        for ei, el in enumerate(self.els):
            for ai in range(self.naz):
                az = 2 * math.pi * ai / self.naz
                e = math.radians(-el)
                Rz = np.array([[math.cos(az), -math.sin(az), 0], [math.sin(az), math.cos(az), 0], [0, 0, 1]])
                Rx = np.array([[1, 0, 0], [0, math.cos(e), -math.sin(e)], [0, math.sin(e), math.cos(e)]])
                R = Rz @ Rx
                dirs.append(R.T @ np.array([0.0, -1.0, 0.0]))
        self.dirs = np.array(dirs)
        # crop each cell to its content once (bbox of alpha)
        self.k = 0

    def cellimg(self, f, ci, size, tint=None):
        key = (f, ci, size, tint)
        im = self.cache.get(key)
        if im is None:
            ei, ai = divmod(ci, self.naz)
            c = self.cell
            src = self.frames[f].crop((ai * c, ei * c, ai * c + c, ei * c + c))
            if tint == "sil":
                a = src.getchannel("A")
                src = Image.new("RGBA", src.size, (14, 12, 20, 255))
                src.putalpha(a)
            im = src.resize((size, size), Image.LANCZOS if size < c else Image.BICUBIC)
            if len(self.cache) > 6000:
                self.cache.clear()
            self.cache[key] = im
        return im

    def pick(self, cam_dir_local):
        return np.argmax(self.dirs @ cam_dir_local.T, axis=0)


SPECIES_SCALE = {"myotis": 1.0, "freetail": 1.05, "nectar": 1.1, "flyingfox": 3.4}
FLAP_HZ = {"myotis": 10.0, "freetail": 8.0, "nectar": 12.0, "flyingfox": 3.0}
HAZE = {"sunset": (232, 150, 120), "dusk": (120, 106, 160), "moon": (24, 34, 70), "dawn": (232, 224, 200)}


def swarm_state(kind, t, meta, rng_seed, density, dur):
    """Return positions (n,3), headings (n,3), phase offsets (n) for the swarm at time t (world space)."""
    rng = np.random.default_rng(rng_seed)
    marks = {k: np.array(v) for k, v in meta.get("marks", {}).items()}
    camp = np.array(meta["cam"]["matrix"])[:3, 3]
    if kind in ("emerge", "column", "moon", "bathouse", "mine_out"):
        mouth = marks.get("bathouse" if kind == "bathouse" else "mouth", np.array([0.0, 8.0, 0.5]))
        rate = {"emerge": 220, "column": 420, "moon": 120, "bathouse": 30}[kind] * density
        tstart = {"emerge": -6.0, "column": -26.0, "moon": -30.0, "bathouse": -2.0}[kind]
        nb = int(rate * (dur - tstart))
        birth = np.sort(rng.uniform(tstart, dur, nb))
        a = t - birth
        alive = a > 0
        a = a[alive]
        n = len(a)
        th0 = rng.uniform(0, 2 * np.pi, nb)[alive]
        lat = rng.normal(0, 1.0, (nb, 3))[alive]
        rr = rng.uniform(0.7, 1.3, nb)[alive]
        if kind == "bathouse":
            out = np.stack([np.zeros(n), -np.ones(n), np.zeros(n)], 1)
            p = mouth + out * (2.5 * a)[:, None] + np.array([0, 0, 1.0]) * (0.6 * a ** 1.4)[:, None]
            p += np.stack([np.sin(th0 + a * 1.5), np.cos(th0 + a * 1.7), np.zeros(n)], 1) * (1.2 * a * rr)[:, None]
        elif kind == "moon":
            target = camp + np.array([-0.35, 1.0, 0.32]) / np.linalg.norm([-0.35, 1.0, 0.32]) * 140.0
            u = np.clip(a / 26.0, 0, 1.2)[:, None]
            p = mouth + (target - mouth) * u + lat * (2 + 18 * u) + np.array([0, 0, 1]) * (np.sin(u * 3) * 6)
        else:
            exit_t = 1.4
            ax = mouth + np.array([0.0, -5.0, 0.0])
            ex = np.minimum(a, exit_t)
            p_exit = mouth + np.array([0.0, -1.0, 0.25])[None] * (4.0 * ex)[:, None] + lat * np.array([1.6, 0.4, 0.9])
            sa = np.maximum(a - exit_t, 0.0)
            R = (3.5 + 1.6 * sa) * rr
            th = th0 + sa * (0.9 / rr)
            z = 2.0 + 2.6 * sa ** 1.08
            drift = np.array([3.0, 4.0, 0.0])[None] * (sa / 10.0)[:, None]
            p_sp = ax + np.stack([R * np.cos(th), R * np.sin(th), z], 1) + drift + lat * 0.6
            w = np.clip((a - exit_t + 0.6) / 1.2, 0, 1)[:, None]
            p = p_exit * (1 - w) + p_sp * w
        keep = p[:, 2] < 160
        p = p[keep]
        # heading by finite difference
        return p, None, rng.uniform(0, 1, nb)[alive][keep], ("emerge", alive, keep)
    if kind in ("hunt", "agave", "durian", "sky", "fig", "fly_over", "silhouette", "mine"):
        n = {"hunt": 70, "agave": 40, "durian": 4, "sky": 90, "fig": 14, "fly_over": 1, "silhouette": 40,
             "mine": 60}[kind]
        n = max(1, int(n * density * (1 if kind in ("fly_over", "durian") else 2.0)))
        tgt = np.array(meta["cam"]["matrix"])[:3, :3] @ np.array([0, 0, -1.0])
        center = camp + tgt * {"hunt": 22, "agave": 18, "durian": 2.0, "sky": 30, "fig": 20, "fly_over": 6,
                               "silhouette": 110, "mine": 12}[kind]
        if kind == "agave" and meta.get("clusters"):
            cl = np.array([c for s in meta["clusters"] for c in s])
            base = cl[rng.integers(0, len(cl), n)]
        elif kind == "durian" and meta.get("flowers"):
            fl = np.array(meta["flowers"])
            base = fl[rng.integers(0, len(fl), n)] + np.array([0, -0.12, 0])
        elif kind == "mine":
            m = marks.get("mouth", np.array([0, 0.8, 1.6]))
            base = np.repeat(m[None], n, 0)
        else:
            spread = {"hunt": (14, 10, 5), "sky": (40, 40, 14), "fig": (24, 10, 6), "fly_over": (0, 0, 0),
                      "silhouette": (14, 8, 6)}[kind]
            base = center + rng.uniform(-1, 1, (n, 3)) * np.array(spread)
            if kind in ("hunt",):
                base[:, 2] = np.maximum(base[:, 2], 2.0)
        ph = rng.uniform(0, 2 * np.pi, (n, 3))
        sp = rng.uniform(0.6, 1.4, (n, 1))
        if kind == "hunt":
            amp = np.array([6.0, 4.0, 2.0])
            p = base + amp * np.sin(t * sp * np.array([0.9, 1.3, 1.9]) + ph)
        elif kind in ("agave", "durian"):
            amp = np.array([0.9, 0.7, 0.5]) if kind == "agave" else np.array([0.15, 0.1, 0.08])
            p = base + amp * np.sin(t * sp * np.array([1.4, 1.1, 2.3]) + ph)
        elif kind == "sky":
            p = base + np.array([8.0, 6.0, 3.0]) * np.sin(t * sp * np.array([0.5, 0.7, 0.9]) + ph)
        elif kind == "fig":
            v = np.array([1.0, 0.25, 0.05]) * 4.0
            p = base + v * ((t - 6.0 + ph[:, :1]) * sp) + np.array([0, 0, 1]) * np.sin(t + ph[:, 1:2])
        elif kind == "fly_over":
            p = camp + np.array([-12.0 + 4.0 * t, 8.0, 5.0 - 0.1 * t])[None]
        elif kind == "silhouette":
            v = np.array([1.0, 0.0, 0.25])
            p = base + v * ((t - 4.0 + ph[:, :1] * 2) * 6.0 * sp)
        elif kind == "mine":
            u = np.clip((t + ph[:, :1] * 2.0) / 6.0 % 1.0, 0, 1)
            start = base + np.array([-30.0, -15.0, 12.0]) + rng.normal(0, 6, (n, 3))
            p = start + (base - start) * u
        return p, None, ph[:, 0] / (2 * np.pi), (kind,)
    raise ValueError(kind)


def draw_swarm(canvas, depth, cam, atlas, sp, kind, t, meta, density, dur, preset, seed):
    dt = 1.0 / 48
    p0, _, ph, _ = swarm_state(kind, t, meta, seed, density, dur)
    p1, _, _, _ = swarm_state(kind, t + dt, meta, seed, density, dur)
    m = min(len(p0), len(p1))
    p0, p1, ph = p0[:m], p1[:m], ph[:m]
    if m == 0:
        return
    vel = p1 - p0
    spd = np.linalg.norm(vel, axis=1, keepdims=True)
    hd = np.where(spd > 1e-6, vel / np.maximum(spd, 1e-6), np.array([[0, -1.0, 0]]))
    x, y, z = cam.project(p0)
    ok = (z > 0.3) & (x > -200) & (x < cam.W + 200) & (y > -200) & (y < cam.H + 200)
    if not ok.any():
        return
    idx = np.nonzero(ok)[0]
    idx = idx[np.argsort(-z[idx])]      # far to near
    # bat local frame: Y_l = -heading, Z_l = up (orthogonalised), X_l = Y x Z
    Yl = -hd[idx]
    up = np.array([0, 0, 1.0])
    Zl = up - (Yl @ up)[:, None] * Yl
    Zl /= np.maximum(np.linalg.norm(Zl, axis=1, keepdims=True), 1e-6)
    Xl = np.cross(Yl, Zl)
    v = cam.pos[None] - p0[idx]
    v /= np.linalg.norm(v, axis=1, keepdims=True)
    loc = np.stack([(v * Xl).sum(1), (v * Yl).sum(1), (v * Zl).sum(1)], 1)
    cells = atlas.pick(loc)
    hz = FLAP_HZ[sp]
    nfr = len(atlas.frames)
    world_cell = 0.42 * SPECIES_SCALE[sp] * (0.55 if kind == "mine" else 1.0)
    haze = np.array(HAZE.get(preset, (128, 128, 128)), dtype=np.float32)
    fogd = {"sunset": 140.0, "dusk": 110.0, "moon": 90.0, "dawn": 80.0}.get(preset, 120.0)
    img = canvas
    Hh, Ww = depth.shape
    for j, i in enumerate(idx):
        size = int(cam.f * world_cell / z[i])
        if size < 3:
            continue
        cx, cy = int(x[i]), int(y[i])
        if 0 <= cx < Ww and 0 <= cy < Hh and depth[cy, cx] < z[i] - 0.3:
            continue                                    # behind scenery
        f = int(((t * hz + ph[i]) % 1.0) * nfr) % nfr
        if size > 360:
            size = 360
        size = size + (size & 1)
        spr = atlas.cellimg(f, int(cells[j]), size, "sil" if kind == "silhouette" else None)
        fogk = 1.0 - math.exp(-z[i] / fogd)
        if fogk > 0.05 and kind != "silhouette":
            a = np.asarray(spr, dtype=np.float32)
            a[..., :3] = a[..., :3] * (1 - fogk * 0.85) + haze * fogk * 0.85
            spr = Image.fromarray(a.astype(np.uint8), "RGBA")
        img.alpha_composite(spr, (cx - size // 2, cy - size // 2))


# ------------------------------------------------------------------ particles
def particles(im, fx, t, rng_seed, cam_meta=None, shot=None, dur=10.0):
    if not fx:
        return
    Wc, Hc = im.size
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay, "RGBA")
    rnd = random.Random(rng_seed)
    glow = Image.new("RGBA", im.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow, "RGBA")
    for kind in fx:
        if kind == "dust":
            for k in range(140):
                x0, y0, s, ph = rnd.random(), rnd.random(), rnd.uniform(0.8, 3.0), rnd.uniform(0, 6.28)
                x = ((x0 + 0.004 * t + 0.01 * math.sin(t * 0.4 + ph)) % 1) * Wc
                y = ((y0 - 0.003 * t + 0.008 * math.cos(t * 0.3 + ph)) % 1) * Hc
                a = int(70 + 60 * math.sin(t * 0.8 + ph))
                d.ellipse([x - s, y - s, x + s, y + s], fill=(255, 236, 205, max(0, a)))
        elif kind == "snow":
            for k in range(320):
                x0, y0, s = rnd.random(), rnd.random(), rnd.uniform(1.0, 3.5)
                sp = rnd.uniform(0.04, 0.09)
                x = ((x0 + 0.01 * math.sin(t * 0.7 + k)) % 1) * Wc * 0.55 + Wc * 0.25
                y = ((y0 + sp * t) % 1) * Hc * 0.7
                d.ellipse([x - s, y - s, x + s, y + s], fill=(245, 250, 255, 170))
        elif kind in ("fireflies",):
            for k in range(70):
                x0, y0, ph = rnd.random(), rnd.uniform(0.45, 0.95), rnd.uniform(0, 6.28)
                x = (x0 + 0.01 * math.sin(t * 0.5 + ph)) * Wc
                y = (y0 + 0.01 * math.cos(t * 0.6 + ph)) * Hc
                on = max(0.0, math.sin(t * rnd.uniform(1.0, 2.2) + ph)) ** 3
                if on > 0.05:
                    r = 2 + 6 * on
                    gd.ellipse([x - r * 3, y - r * 3, x + r * 3, y + r * 3], fill=(200, 255, 90, int(60 * on)))
                    d.ellipse([x - r * 0.5, y - r * 0.5, x + r * 0.5, y + r * 0.5], fill=(240, 255, 170, int(255 * on)))
        elif kind in ("moths", "moths_dense", "moths_porch"):
            n = {"moths": 40, "moths_dense": 160, "moths_porch": 60}[kind]
            for k in range(n):
                if kind == "moths_porch":
                    cx, cy, rad = 0.34, 0.5, 0.06
                else:
                    cx, cy, rad = rnd.uniform(0.05, 0.95), rnd.uniform(0.2, 0.8), rnd.uniform(0.02, 0.08)
                ph, sp = rnd.uniform(0, 6.28), rnd.uniform(1.5, 3.5)
                x = (cx + rad * math.sin(t * sp + ph) + 0.4 * rad * math.sin(t * 2.7 * sp + ph * 2)) * Wc
                y = (cy + rad * 0.7 * math.cos(t * sp * 1.3 + ph)) * Hc
                s = rnd.uniform(3, 7) * (1.5 if kind == "moths_dense" and k % 5 == 0 else 1.0)
                flap = abs(math.sin(t * 40 + ph))
                col = (232, 220, 196, 230)
                d.ellipse([x - s, y - s * 0.35 * (0.4 + flap), x, y + s * 0.35 * (0.4 + flap)], fill=col)
                d.ellipse([x, y - s * 0.35 * (0.4 + flap), x + s, y + s * 0.35 * (0.4 + flap)], fill=col)
                if kind == "moths_porch":
                    gd.ellipse([x - 10, y - 10, x + 10, y + 10], fill=(255, 200, 120, 25))
        elif kind == "pollen":
            for k in range(90):
                x0, y0, ph = rnd.uniform(0.3, 0.7), rnd.uniform(0.3, 0.7), rnd.uniform(0, 6.28)
                x = (x0 + 0.03 * math.sin(t * 0.6 + ph) + 0.004 * t) * Wc
                y = (y0 + 0.02 * t * rnd.uniform(0.2, 1.0) + 0.02 * math.cos(t * 0.5 + ph)) * Hc
                s = rnd.uniform(1.0, 2.6)
                gd.ellipse([x - s * 3, y - s * 3, x + s * 3, y + s * 3], fill=(255, 210, 80, 30))
                d.ellipse([x - s, y - s, x + s, y + s], fill=(255, 220, 110, 200))
        elif kind == "seeds":
            for k in range(26):
                t0 = rnd.uniform(0, dur)
                if t < t0:
                    continue
                a = t - t0
                x = (0.15 + 0.7 * ((t0 * 0.09) % 1) + 0.01 * math.sin(a * 3 + k)) * Wc
                y = (0.12 + 0.12 * a * a) * Hc
                if y < Hc * 0.92:
                    d.ellipse([x - 3, y - 3, x + 3, y + 3], fill=(80, 50, 30, 230))
        elif kind == "spray":
            for k in range(240):
                ph = rnd.uniform(0, 1)
                age = (t * 0.6 + ph) % 1.0
                x = (rnd.uniform(0.0, 1.0)) * Wc
                y = (0.58 + 0.08 * rnd.random() - 0.05 * age) * Hc
                r = 6 + 40 * age
                gd.ellipse([x - r, y - r * 0.6, x + r, y + r * 0.6], fill=(236, 242, 236, int(26 * (1 - age))))
        elif kind == "sonar":
            cx, cy = 0.62 * Wc, 0.32 * Hc
            for k in range(4):
                r = ((t * 0.9 + k * 0.25) % 1.0) * 0.32 * Wc
                a = int(200 * (1 - r / (0.32 * Wc)))
                d.arc([cx - r, cy - r, cx + r, cy + r], 150, 230, fill=(150, 230, 255, a), width=5)
    glow = glow.filter(ImageFilter.GaussianBlur(6))
    im.alpha_composite(glow)
    im.alpha_composite(lay)


# ------------------------------------------------------------------ grade
GRADES = {
    "sunset": dict(sat=1.12, contrast=0.28, shadows=(0.06, 0.0, 0.10), highs=(0.05, 0.02, -0.03), bloom=0.32, exp=1.05),
    "dusk": dict(sat=1.1, contrast=0.25, shadows=(0.0, 0.01, 0.09), highs=(0.05, 0.01, -0.02), bloom=0.3, exp=1.08),
    "night": dict(sat=1.05, contrast=0.22, shadows=(0.0, 0.02, 0.08), highs=(0.0, 0.02, 0.05), bloom=0.38, exp=1.15),
    "cave": dict(sat=1.08, contrast=0.3, shadows=(-0.01, 0.04, 0.07), highs=(0.06, 0.02, -0.03), bloom=0.35, exp=1.2),
    "day": dict(sat=1.12, contrast=0.22, shadows=(0.0, 0.01, 0.04), highs=(0.03, 0.02, -0.01), bloom=0.18, exp=1.0),
    "dawn": dict(sat=1.12, contrast=0.24, shadows=(0.0, 0.03, 0.05), highs=(0.06, 0.03, -0.02), bloom=0.3, exp=1.02),
    "studio": dict(sat=1.08, contrast=0.25, shadows=(0.02, 0.0, 0.08), highs=(0.04, 0.02, 0.0), bloom=0.25, exp=1.0),
}


def grade(rgb, g, rng):
    """rgb: float32 (h, w, 3) 0..1 -> graded float32."""
    x = np.clip(rgb * g["exp"], 0, 1)
    lum = x @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)
    x = lum[..., None] + (x - lum[..., None]) * g["sat"]
    s = x * x * (3 - 2 * x)
    x = x + (s - x) * g["contrast"]
    lum = np.clip(x @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32), 0, 1)[..., None]
    x = x + np.array(g["shadows"], dtype=np.float32) * (1 - lum) ** 2 + np.array(g["highs"], dtype=np.float32) * lum ** 2
    x = np.clip(x, 0, 1)
    # bloom: blurred highlights
    hi = np.clip((x - 0.72) / 0.28, 0, 1)
    if g["bloom"] > 0:
        h_, w_ = x.shape[:2]
        sm = Image.fromarray((hi * 255).astype(np.uint8)).resize((w_ // 8, h_ // 8), Image.BILINEAR)
        sm = sm.filter(ImageFilter.GaussianBlur(6)).resize((w_, h_), Image.BILINEAR)
        x = 1 - (1 - x) * (1 - np.asarray(sm, dtype=np.float32) / 255.0 * g["bloom"])
    h_, w_ = x.shape[:2]
    yy, xx = np.mgrid[0:h_, 0:w_].astype(np.float32)
    r = np.sqrt(((xx - w_ / 2) / (w_ / 2)) ** 2 + ((yy - h_ / 2) / (h_ / 2)) ** 2)
    x *= (1 - 0.28 * np.clip((r - 0.55) / 0.8, 0, 1) ** 1.6)[..., None]
    x += rng.normal(0, 0.008, x.shape[:2]).astype(np.float32)[..., None]
    return np.clip(x, 0, 1)


def grade_key(shot_id, shot):
    if shot["env"] == "cave":
        return "cave"
    if shot["env"] == "studio":
        return "studio"
    st = shot["state"] or ("sunset" if shot["env"] in ("wind",) else "dusk" if shot["env"] == "mine" else "night")
    return {"sunset": "sunset", "dusk": "dusk", "blue": "dusk", "night": "night", "day": "day", "dawn": "dawn",
            "healthy": "cave"}.get(st, "dusk")


# ------------------------------------------------------------------ scene renderer
def compose_plate_scene(proj, root, s, dur, out):
    from shots4 import SHOTS
    v = s["visual"]
    sid = v["shot"]
    shot = SHOTS[sid]
    pdir = os.path.join(root, "plates")
    full_dir = os.path.join(root, "full", sid)
    meta = json.load(open(os.path.join(pdir, sid + ".json"))) if os.path.exists(os.path.join(pdir, sid + ".json")) \
        else json.load(open(os.path.join(full_dir, "meta.json")))
    is_full = shot["full"]
    if is_full:
        files = sorted(f for f in os.listdir(full_dir) if f.startswith("char_"))
        size = Image.open(os.path.join(full_dir, files[0])).size
    else:
        plate = Image.open(os.path.join(pdir, sid + ".png")).convert("RGB")
        size = plate.size
        plate_np = np.asarray(plate, dtype=np.float32) / 255.0
        depth = decode_depth(os.path.join(pdir, sid + "_depth.png"), size)
    cam = Cam(meta["cam"], size)
    cdir = os.path.join(root, "chars", sid)
    have_chars = os.path.isdir(cdir) and os.path.exists(os.path.join(cdir, "meta.json"))
    if have_chars:
        cm = json.load(open(os.path.join(cdir, "meta.json")))
        nchar = len([f for f in os.listdir(cdir) if f.startswith("char_")])
        base_s = np.asarray(Image.open(os.path.join(cdir, "base_shadow.png")).convert("F"), dtype=np.float32)
        base_a = np.asarray(Image.open(os.path.join(cdir, "base_ao.png")).convert("F"), dtype=np.float32)
    sw = shot.get("swarm")
    atlas = None
    if sw:
        kind, sp, preset, dens = sw
        if os.path.isdir(os.path.join(root, "sprites", f"{sp}_{preset}")):
            atlas = Atlas(sp, preset, root)
    gk = grade_key(sid, shot)
    g = GRADES[gk]
    rng = np.random.default_rng(7)
    z0, z1, cx0, cx1, cy0, cy1 = MOVES[v.get("move", "push")]
    over = overlay_fn(v, dur, seed=s["id"])
    n = int(round(dur * FPS))
    enc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                            "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "17",
                            "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    sw_, sh_ = size
    for kf in range(n):
        t = kf / FPS
        if is_full:
            i = min(len(files) - 1, int(t * meta.get("fps", 12)))
            base = np.asarray(Image.open(os.path.join(full_dir, files[i])).convert("RGB"), dtype=np.float32) / 255.0
            canvas = base
        else:
            canvas = plate_np.copy()
            if have_chars:
                i = min(nchar - 1, int(round(t * cm.get("fps", 12))))
                fn = os.path.join(cdir, f"char_{i:04d}.png")
                if os.path.exists(fn):
                    ch = np.asarray(Image.open(fn).convert("RGBA"), dtype=np.float32) / 255.0
                    shd = np.asarray(Image.open(os.path.join(cdir, f"shadow_{i:04d}.png")).convert("F"), np.float32)
                    ao = np.asarray(Image.open(os.path.join(cdir, f"ao_{i:04d}.png")).convert("F"), np.float32)
                    zc = decode_depth(os.path.join(cdir, f"depth_{i:04d}.png"), size)
                    rs = np.where(base_s > 300, np.clip(shd / np.maximum(base_s, 1), 0, 1), 1.0)
                    ra = np.where(base_a > 300, np.clip(ao / np.maximum(base_a, 1), 0, 1), 1.0)
                    dark = (1 - 0.62 * (1 - rs)) * (1 - 0.5 * (1 - ra))
                    canvas *= dark[..., None]
                    vis = ch[..., 3] * np.clip((depth - zc) / (0.04 * zc + 0.02) + 1.0, 0, 1)
                    canvas = canvas * (1 - vis[..., None]) + ch[..., :3] * vis[..., None]
        im = Image.fromarray((np.clip(canvas, 0, 1) * 255).astype(np.uint8)).convert("RGBA")
        if atlas is not None and not is_full:
            draw_swarm(im, depth, cam, atlas, sw[1], sw[0], t, meta, sw[3], dur, sw[2], s["id"])
        particles(im, shot.get("fx", []), t, s["id"] * 31, meta, shot, dur)
        x = np.asarray(im.convert("RGB"), dtype=np.float32) / 255.0
        x = grade(x, g, rng)
        src = Image.fromarray((x * 255).astype(np.uint8))
        u = ease(t / dur) * 0.85 + (t / dur) * 0.15
        z = z0 + (z1 - z0) * u
        cx = (cx0 + (cx1 - cx0) * u) * sw_
        cy = (cy0 + (cy1 - cy0) * u) * sh_
        bw, bh = sw_ / z, sh_ / z
        x0 = min(max(cx - bw / 2, 0), sw_ - bw)
        y0 = min(max(cy - bh / 2, 0), sh_ - bh)
        frame = src.transform((W, H), Image.EXTENT, (x0, y0, x0 + bw, y0 + bh), Image.BICUBIC).convert("RGBA")
        over(frame, t)
        enc.stdin.write(frame.convert("RGB").tobytes())
    enc.stdin.close()
    enc.wait()


def compose_card_scene(proj, root, s, dur, out, backdrop):
    import cards4
    v = s["visual"]
    fr = cards4.card(v["card"], v, dur, backdrop)
    n = int(round(dur * FPS))
    enc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                            "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "17",
                            "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for kf in range(n):
        enc.stdin.write(fr(kf / FPS).tobytes())
    enc.stdin.close()
    enc.wait()


def backdrop_for(root, sb, idx):
    """Defocused, darkened plate from the nearest preceding 3D scene (cards sit 'inside' the film's world)."""
    for j in range(idx, -1, -1):
        v = sb[j]["visual"]
        if v["type"] == "plate":
            p = os.path.join(root, "plates", v["shot"] + ".png")
            if os.path.exists(p):
                im = Image.open(p).convert("RGB").resize((W // 4, H // 4), Image.BILINEAR)
                im = im.filter(ImageFilter.GaussianBlur(10)).resize((W, H), Image.BICUBIC)
                a = np.asarray(im, dtype=np.float32) * 0.42
                return Image.fromarray(a.astype(np.uint8)).convert("RGBA")
    return None


def main():
    proj, mode = sys.argv[1], sys.argv[2]
    if mode == "timing":
        make_timing(proj)
        return
    root = os.path.join(proj, "08_Scenes", "renders4")
    args = [a for a in sys.argv[3:] if not a.startswith("--")]
    force = "--force" in sys.argv
    sb = json.load(open(os.path.join(proj, "06_Storyboard", "storyboard.json")))["scenes"]
    timing = json.load(open(os.path.join(proj, "09_Animation", "scene_timing.json")))
    ids = parse_ids(args[0] if args else "", len(sb))
    for k, s in enumerate(sb):
        if s["id"] not in ids:
            continue
        out = os.path.join(proj, "09_Animation", s["file"] + ".mp4")
        if os.path.exists(out) and not force:
            continue
        dur = timing[s["file"]]["duration"]
        if s["visual"]["type"] == "card":
            compose_card_scene(proj, root, s, dur, out, backdrop_for(root, sb, k))
        else:
            compose_plate_scene(proj, root, s, dur, out)
        print(s["file"], f"{dur:.2f}s", flush=True)


if __name__ == "__main__":
    main()
