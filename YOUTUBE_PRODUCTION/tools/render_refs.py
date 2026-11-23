"""Render reusable reference assets: character sheet, creature sheet, background plates.

Usage: python3 render_refs.py <project_dir> <shared_assets_dir>
"""
import os, shutil, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from playwright.sync_api import sync_playwright
from draw import *
import scenes_mosquito as S

proj, shared = sys.argv[1], sys.argv[2]
CHROME = "/opt/pw-browsers/chromium-1243/chrome-linux64/chrome"


def label(x, y, txt, size=34):
    return (f'<text x="{x}" y="{y}" text-anchor="middle" font-family="Inter" font-weight="800" font-size="{size}" '
            f'fill="{INK}">{txt}</text>')


paper = '<rect x="-300" y="-300" width="2600" height="1700" fill="#F4EEDF"/>'
chars = paper + label(960, 90, "PIP — house mascot (mustard bucket hat, round glasses, olive vest, satchel)", 40)
for k, (x, kw, cap) in enumerate([
        (230, dict(), "neutral"), (560, dict(arms=(15, 140), thumbs=(False, True), mouth="grin"), "thumbs up"),
        (890, dict(mouth="o", arms=(40, 40)), "surprised"), (1220, dict(mouth="frown", eyes="annoyed"), "annoyed"),
        (1550, dict(eyes="happy", arms=(110, 110), mouth="grin"), "joy")]):
    chars += pip(x, 860, 1.25, **kw) + label(x, 950, cap)
chars += label(1780, 950, "hat")
chars += f'<g transform="translate(1780 700) scale(1.4)">{bucket_hat()}</g>'

cast = paper + label(960, 90, "Supporting cast + creature (generic roles, varied skin tones)", 40)
cast += person(250, 880, 1.15, skin="#F3D9C0", outfit="coat", outfit_color="#F4F4F0", hair_style="tuft", hair_color="#C8C6C0") + label(250, 960, "Scientist A")
cast += person(560, 880, 1.15, skin="#8D5A3B", outfit="coat", outfit_color="#F4F4F0", hair_style="bun", hair_color="#1F1A17", mouth="flat") + label(560, 960, "Scientist B")
cast += person(860, 880, 1.15, skin="#8D5A3B", outfit="dress", outfit_color="#D08B3E", hair_style="scarf", hair_color="#3F7F7A") + label(860, 960, "Parent")
cast += person(1110, 880, 0.82, skin="#A86F4A", outfit="shirt", outfit_color="#C9563F", hair_style="curly", hair_color="#2B2420", mouth="grin") + label(1110, 960, "Child")
cast += mosquito(1560, 420, 2.6, frame=0) + label(1560, 640, "Mosquito (Aedes-style bands)")
cast += mosquito(1560, 800, 1.3, frame=0, dead=True, rot=180, flap=False) + label(1560, 960, "'gone' pose")

assets = [
    ("characters", "pip_character_sheet.png", chars),
    ("characters", "supporting_cast_and_mosquito.png", cast),
    ("backgrounds", "bg_bedroom_night.png", S.bg_bedroom_night(0) + S.bed() + S.blanket()),
    ("backgrounds", "bg_space_earth.png", S.bg_space(0) + S.earth()),
    ("backgrounds", "bg_lab_wide.png", S.bg_lab()),
    ("backgrounds", "bg_dawn_pond.png", S.bg_dawn(0, 5)),
    ("backgrounds", "bg_sunrise_hills.png", S.bg_sunrise()),
    ("objects", "obj_specimen_jar.png", paper + S.jar(960, 700, 0, 2.5)),
]
cams = {"bg_lab_wide.png": (0.6, 1600, 560)}
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROME)
    page = b.new_page(viewport={"width": 1920, "height": 1080})
    page.set_content('<html><body style="margin:0"><div id="r"></div></body></html>')
    for sub, fn, content in assets:
        out = os.path.join(proj, "04_IMAGES", sub, fn)
        page.evaluate("s => { document.getElementById('r').innerHTML = s; }",
                      frame_svg(content, cams.get(fn, (1.0, 960, 540)), seed=1, vignette=0.4 if sub != "backgrounds" else 0.9))
        page.screenshot(path=out, clip={"x": 0, "y": 0, "width": 1920, "height": 1080})
        dst = os.path.join(shared, "characters" if sub == "characters" else ("backgrounds" if sub == "backgrounds" else "reusable_objects"), fn)
        shutil.copy2(out, dst)
        print(out)
    b.close()
