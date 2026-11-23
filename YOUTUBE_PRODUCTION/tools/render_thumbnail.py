"""Render the episode thumbnail (1280x720 export + 1920x1080 master).

Usage: python3 render_thumbnail.py <project_dir>
"""
import os, sys, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from playwright.sync_api import sync_playwright
from draw import *
import scenes_mosquito as S

proj = sys.argv[1]
r = rnd(5)
torn = "M1000 -50 " + " ".join(f"L{1000 + r.uniform(-28, 28):.0f} {y}" for y in range(0, 1160, 40)) + " L2300 1150 L2300 -50 Z"
left = S.bg_bedroom_night(0)
swarm = "".join(tiny_mosquito(r.uniform(60, 900), r.uniform(80, 700), r.uniform(0.6, 1.0), frame=k, rot=r.uniform(-20, 20)) for k in range(26))
big = mosquito(520, 640, 3.0, frame=0, look=(3, 1))
right = f'<clipPath id="rc"><path d="{torn}"/></clipPath><g clip-path="url(#rc)">{S.bg_dawn(0, 5)}</g>'
edge = f'<path d="{torn}" fill="none" stroke="{CREAM}" stroke-width="26"/><path d="{torn}" fill="none" stroke="{INK}" stroke-width="7"/>'
hero = pip(1480, 1330, 2.3, mouth="o", eyes="open", look=(-8, -2), arms=(20, 20))
txt = (title_text([("EVERY", CREAM), ("MOSQUITO", MUSTARD)], 520, 150, 150, lh=1.0) +
       title_text([("GONE?", RED)], 1500, 210, 190))
content = left + swarm + big + right + edge + hero + txt
svg = frame_svg(content, (1.0, 960, 540), seed=1, vignette=0.6, grain=0.0)
out_dir = os.path.join(proj, "09_THUMBNAIL")
master = os.path.join(out_dir, "thumbnail_master_1920x1080.png")
with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/opt/pw-browsers/chromium-1243/chrome-linux64/chrome")
    pg = b.new_page(viewport={"width": 1920, "height": 1080})
    pg.set_content('<html><body style="margin:0">' + svg + '</body></html>')
    pg.screenshot(path=master, clip={"x": 0, "y": 0, "width": 1920, "height": 1080})
    b.close()
subprocess.run(["convert", master, "-resize", "1280x720", "-quality", "92", os.path.join(out_dir, "thumbnail_1280x720.jpg")], check=True)
print(master)
