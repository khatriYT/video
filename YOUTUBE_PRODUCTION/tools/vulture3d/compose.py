#!/usr/bin/env python3
"""Compose per-scene clips for episode 3 (3D stills/anims + cards + overlays) -> 09_Animation/SC###.mp4

Usage: python3 tools/vulture3d/compose.py <project_dir> [ids e.g. 1-10,15] [--types=card,plate,anim] [--force]
Scene duration = narration + 0.75 s (min 2.5 s), plus holds for titles/end card. Clips are 1920x1080, 24 fps,
H.264 CRF 18 yuv420p, with light film grain. Writes 09_Animation/scene_timing.json.
"""
import json
import math
import os
import subprocess
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cards import H, W, card, ease, overlay_fn  # noqa: E402

FPS = 24
PAD, MIN_DUR = 0.75, 2.5
HOLD = {"title": 0.8, "end": 12.0}
MOVES = {  # (zoom0, zoom1, cx0, cx1, cy0, cy1) as fractions of the source image
    "push": (1.0, 1.1, 0.5, 0.5, 0.5, 0.5), "pull": (1.1, 1.0, 0.5, 0.5, 0.5, 0.5),
    "pan_l": (1.1, 1.1, 0.545, 0.455, 0.5, 0.5), "pan_r": (1.1, 1.1, 0.455, 0.545, 0.5, 0.5),
    "rise": (1.1, 1.1, 0.5, 0.5, 0.545, 0.455), "sink": (1.1, 1.1, 0.5, 0.5, 0.455, 0.545),
    "hold": (1.04, 1.04, 0.5, 0.5, 0.5, 0.5)}


def parse_ids(spec, n):
    if not spec:
        return list(range(1, n + 1))
    out = []
    for part in spec.split(","):
        if "-" in part:
            a, b = part.split("-")
            out += list(range(int(a), int(b) + 1))
        else:
            out.append(int(part))
    return out


_VIG = None


def vignette(im):
    global _VIG
    if _VIG is None:
        from PIL import ImageDraw, ImageFilter
        m = Image.new("L", (W, H), 0)
        d = ImageDraw.Draw(m)
        d.ellipse([-W * 0.15, -H * 0.2, W * 1.15, H * 1.2], fill=255)
        _VIG = m.filter(ImageFilter.GaussianBlur(160)).point(lambda v: int(150 + v * 105 / 255))
    black = Image.new("RGB", (W, H), (12, 10, 8))
    return Image.composite(im, black, _VIG)


def main():
    proj = sys.argv[1]
    args = [a for a in sys.argv[2:] if not a.startswith("--")]
    opts = dict(a[2:].split("=", 1) if "=" in a else (a[2:], "1") for a in sys.argv[2:] if a.startswith("--"))
    types = opts.get("types", "card,plate,anim").split(",")
    P = lambda *x: os.path.join(proj, *x)
    sb = json.load(open(P("06_Storyboard", "storyboard.json")))["scenes"]
    durs = json.load(open(P("10_Audio", "narration", "durations.json")))
    ids = parse_ids(args[0] if args else "", len(sb))
    os.makedirs(P("09_Animation"), exist_ok=True)
    timing_f = P("09_Animation", "scene_timing.json")
    timing = json.load(open(timing_f)) if os.path.exists(timing_f) else {}
    for s in sb:
        if s["id"] not in ids or s["visual"]["type"] not in types:
            continue
        v = s["visual"]
        out = P("09_Animation", s["file"] + ".mp4")
        dur = max(MIN_DUR, durs[s["file"]] + PAD) + HOLD.get((v.get("text") or {}).get("style"), 0)
        if s["id"] == 1:
            dur += 0.4
        n = int(round(dur * FPS))
        timing[s["file"]] = dict(duration=round(n / FPS, 3), narration=durs[s["file"]], type=v["type"])
        if os.path.exists(out) and "force" not in opts:
            continue
        over = overlay_fn(v, dur, seed=s["id"]) if v["type"] != "card" else None
        if v["type"] == "card":
            params = {k: x for k, x in v.items() if k not in ("type", "card")}
            fr = card(v["card"], params, dur)
            get = lambda t: fr(t)
        elif v["type"] == "plate":
            src = Image.open(P("08_Scenes", "renders", v["shot"] + ".png")).convert("RGB")
            sw, sh = src.size
            z0, z1, cx0, cx1, cy0, cy1 = MOVES[v.get("move", "push")]

            def get(t, src=src, sw=sw, sh=sh, z0=z0, z1=z1, cx0=cx0, cx1=cx1, cy0=cy0, cy1=cy1):
                u = ease(t / dur) * 0.85 + (t / dur) * 0.15
                z = z0 + (z1 - z0) * u
                cx = (cx0 + (cx1 - cx0) * u) * sw
                cy = (cy0 + (cy1 - cy0) * u) * sh
                bw, bh = sw / z, sh / z
                x0 = min(max(cx - bw / 2, 0), sw - bw)
                y0 = min(max(cy - bh / 2, 0), sh - bh)
                return vignette(src.transform((W, H), Image.EXTENT, (x0, y0, x0 + bw, y0 + bh), Image.BICUBIC))
        else:
            fdir = P("08_Scenes", "renders", v["shot"])
            files = sorted(f for f in os.listdir(fdir) if f.endswith(".png"))
            cache = {}

            def get(t, files=files, fdir=fdir, cache=cache):
                i = min(len(files) - 1, int(t * 12))
                if i not in cache:
                    cache.clear()
                    cache[i] = vignette(Image.open(os.path.join(fdir, files[i])).convert("RGB").resize((W, H),
                                                                                                    Image.LANCZOS))
                return cache[i]
        enc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                                "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-vf", "noise=alls=4:allf=t",
                                "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p",
                                "-r", str(FPS), out], stdin=subprocess.PIPE)
        for k in range(n):
            t = k / FPS
            im = get(t)
            if over is not None:
                im = im.convert("RGBA")
                over(im, t)
                im = im.convert("RGB")
            enc.stdin.write(im.tobytes())
        enc.stdin.close()
        enc.wait()
        print(s["file"], v["type"], v.get("shot") or v.get("card"), f"{dur:.2f}s", flush=True)
        json.dump(timing, open(timing_f, "w"), indent=1)
    json.dump(timing, open(timing_f, "w"), indent=1)


if __name__ == "__main__":
    main()
