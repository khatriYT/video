"""Render house-style scenes to stills (PNG) and animated clips (MP4).

Usage:
  python3 render.py <project_dir> still  [ids...]   -> 04_IMAGES/scenes/scene_###.png
  python3 render.py <project_dir> anim   [ids...]   -> 05_ANIMATIONS/scene_###/scene_###.mp4
Scene duration = narration length (06_AUDIO/narration/durations.json) + PAD, min MIN_DUR.
Never overwrites an existing output unless --force is given.
"""
import json, os, subprocess, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from playwright.sync_api import sync_playwright
import importlib
from draw import frame_svg
import kinetic

opts = dict(a[2:].split("=", 1) for a in sys.argv[1:] if a.startswith("--") and "=" in a)
S = importlib.import_module(opts.get("scenes", "scenes_mosquito"))   # e.g. --scenes=scenes_bees
CHROME = os.environ.get("CHROME_PATH", "/opt/pw-browsers/chromium-1243/chrome-linux64/chrome")
FPS, PAD, MIN_DUR = 24, float(opts.get("pad", 0.7)), 2.0                # e.g. --pad=0.85
BOIL_FPS = 8

args = [a for a in sys.argv[1:] if not a.startswith("--")]
force = "--force" in sys.argv
proj, mode = args[0], args[1]
ids = [int(i) for i in args[2:]] or sorted(S.SCENES)
durs = json.load(open(os.path.join(proj, "06_AUDIO", "narration", "durations.json")))
_sb = os.path.join(proj, "03_STORYBOARD", "storyboard.json")
ONSCREEN = {s["id"]: s.get("onscreen", "") for s in json.load(open(_sb))["scenes"]} if os.path.exists(_sb) else {}


def scene_T(i):
    return round(max(MIN_DUR, durs[f"scene_{i:03d}"] + PAD), 3)


def svg_at(i, t, T, fr):
    content, cam = S.SCENES[i](t, T, fr)
    seed = 1 + (int(t * BOIL_FPS) % 3)  # line boil: 3 alternating drawings at 8 fps
    overlay = kinetic.render(ONSCREEN.get(i, ""), t, T)   # animated on-screen text, kept crisp (outside line boil)
    return frame_svg(content, cam, seed=seed, overlay=overlay), seed


with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROME)
    page = b.new_page(viewport={"width": 1920, "height": 1080})
    page.set_content('<html><body style="margin:0;background:#000"><div id="r"></div></body></html>')
    import draw
    draw.GRAIN["external"] = True  # grain is added by ffmpeg's noise filter instead (much faster)

    def put(svg, seed):
        page.evaluate("s => { document.getElementById('r').innerHTML = s; }", svg)
    for i in ids:
        T = scene_T(i)
        name = f"scene_{i:03d}"
        if mode == "still":
            out = os.path.join(proj, "04_IMAGES", "scenes", name + ".png")
            if os.path.exists(out) and not force:
                print("exists, skipping", out); continue
            t = S.KEYFRAME[i] * T
            put(*svg_at(i, t, T, int(t * FPS)))
            page.screenshot(path=out, clip={"x": 0, "y": 0, "width": 1920, "height": 1080})
            print("still", out, flush=True)
        else:
            d = os.path.join(proj, "05_ANIMATIONS", name)
            os.makedirs(d, exist_ok=True)
            out = os.path.join(d, name + ".mp4")
            if os.path.exists(out) and not force:
                print("exists, skipping", out); continue
            n = int(round(T * FPS))
            t0 = time.time()
            ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(FPS),
                                   "-c:v", "mjpeg", "-i", "-", "-vf", "noise=alls=4", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                                   "-pix_fmt", "yuv420p", "-r", str(FPS), "-movflags", "+faststart", out], stdin=subprocess.PIPE)
            for fr in range(n):
                put(*svg_at(i, fr / FPS, T, fr))
                ff.stdin.write(page.screenshot(type="jpeg", quality=95, clip={"x": 0, "y": 0, "width": 1920, "height": 1080}))
            ff.stdin.close(); ff.wait()
            print(f"anim {out} frames={n} T={T}s ({time.time() - t0:.0f}s)", flush=True)
    b.close()
