#!/usr/bin/env python3
"""Compose v2 scene clips: detailed plate + animated character pass + character shadows + camera move + overlays.

Usage: python3 tools/vulture3d/compose3.py <project_dir> <renders3_root> [ids] [--force]
Writes 09_Animation/SC###.mp4 for 3D scenes (cards are reused from compose.py). Scene durations come from
09_Animation/scene_timing.json, so the audio timeline is unchanged.
"""
import json
import os
import subprocess
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cards import H, W, ease, overlay_fn  # noqa: E402
from compose import MOVES, parse_ids, vignette  # noqa: E402

FPS = 24
PLATE_OF = None


def load_rgba(p, size):
    im = Image.open(p).convert("RGBA")
    return im if im.size == size else im.resize(size, Image.BICUBIC)


def main():
    proj, root = sys.argv[1], sys.argv[2]
    args = [a for a in sys.argv[3:] if not a.startswith("--")]
    force = "--force" in sys.argv
    sys.argv = [sys.argv[0], "--", root, "NONE"]     # render3 parses argv at import; keep it inert
    import importlib.util
    spec = importlib.util.spec_from_file_location("r3data", os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                                         "scenes3_data.json"))
    data = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "scenes3_data.json")))
    P = lambda *x: os.path.join(proj, *x)
    sb = json.load(open(P("06_Storyboard", "storyboard.json")))["scenes"]
    timing = json.load(open(P("09_Animation", "scene_timing.json")))
    ids = parse_ids(args[0] if args else "", len(sb))
    for s in sb:
        v = s["visual"]
        if s["id"] not in ids or v["type"] == "card":
            continue
        sid = s["id"]
        out = P("09_Animation", s["file"] + ".mp4")
        if os.path.exists(out) and not force and os.path.exists(out + ".v2"):
            continue
        dur = timing[s["file"]]["duration"]
        n = int(round(dur * FPS))
        over = overlay_fn(v, dur, seed=sid)
        full_dir = os.path.join(root, "full", f"SC{sid:03d}")
        if os.path.isdir(full_dir):                       # full-3D animated shot
            files = sorted(f for f in os.listdir(full_dir) if f.endswith(".png"))
            cache = {}

            def get(t, files=files, full_dir=full_dir, cache=cache):
                i = min(len(files) - 1, int(t * 12))
                if i not in cache:
                    cache.clear()
                    cache[i] = vignette(Image.open(os.path.join(full_dir, files[i])).convert("RGB").resize((W, H),
                                                                                                        Image.LANCZOS))
                return cache[i]
        else:                                             # layered: plate + character pass
            pk = data["scene_plate"][str(sid)]
            plate = Image.open(os.path.join(root, "plates", pk + ".png")).convert("RGB")
            sw, sh = plate.size
            cdir = os.path.join(root, "chars", f"SC{sid:03d}")
            meta = json.load(open(os.path.join(cdir, "meta.json"))) if os.path.exists(os.path.join(cdir, "meta.json")) else {}
            k = meta.get("shadow_k", 0.5)
            nfr = meta.get("frames", 0) if meta.get("actors", 0) else 0
            base = None
            if nfr:
                b = np.asarray(Image.open(os.path.join(cdir, "shadow_0000.png")).convert("L").resize((sw, sh),
                                                                                                    Image.BILINEAR),
                               dtype=np.float32)
                base = b
            plate_np = np.asarray(plate, dtype=np.float32)
            z0, z1, cx0, cx1, cy0, cy1 = MOVES[v.get("move", "push")]
            cache = {}

            def layer(i, cdir=cdir, base=base, plate_np=plate_np, sw=sw, sh=sh, k=k):
                if i in cache:
                    return cache[i]
                cache.clear()
                fn = os.path.join(cdir, f"char_{i:04d}.png")
                if base is None or not os.path.exists(fn):
                    cache[i] = Image.fromarray(plate_np.astype(np.uint8))
                    return cache[i]
                ch = Image.open(fn).convert("RGBA").resize((sw, sh), Image.BICUBIC)
                shd = np.asarray(Image.open(os.path.join(cdir, f"shadow_{i:04d}.png")).convert("L").resize(
                    (sw, sh), Image.BILINEAR), dtype=np.float32)
                ratio = np.where(base > 2.0, np.clip(shd / np.maximum(base, 1.0), 0.0, 1.0), 1.0)
                dark = 1.0 - k * (1.0 - ratio)
                img = Image.fromarray(np.clip(plate_np * dark[..., None], 0, 255).astype(np.uint8)).convert("RGBA")
                img.alpha_composite(ch)
                cache[i] = img.convert("RGB")
                return cache[i]

            def get(t, layer=layer, nfr=nfr, sw=sw, sh=sh, z0=z0, z1=z1, cx0=cx0, cx1=cx1, cy0=cy0, cy1=cy1, dur=dur):
                i = min(max(nfr, 1), 1 + int(t * 12))
                src = layer(i)
                u = ease(t / dur) * 0.85 + (t / dur) * 0.15
                z = z0 + (z1 - z0) * u
                cx = (cx0 + (cx1 - cx0) * u) * sw
                cy = (cy0 + (cy1 - cy0) * u) * sh
                bw, bh = sw / z, sh / z
                x0 = min(max(cx - bw / 2, 0), sw - bw)
                y0 = min(max(cy - bh / 2, 0), sh - bh)
                return vignette(src.transform((W, H), Image.EXTENT, (x0, y0, x0 + bw, y0 + bh), Image.BICUBIC))
        enc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                                "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast",
                                "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS), out], stdin=subprocess.PIPE)
        for kf in range(n):
            t = kf / FPS
            im = get(t).convert("RGBA")
            over(im, t)
            enc.stdin.write(im.convert("RGB").tobytes())
        enc.stdin.close()
        enc.wait()
        open(out + ".v2", "w").write("v2")
        print(s["file"], f"{dur:.2f}s", flush=True)


if __name__ == "__main__":
    main()
