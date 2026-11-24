"""Detailed before/after thumbnail for episode 2: the same produce aisle WITH BEES vs WITHOUT BEES."""
import math, os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from playwright.sync_api import sync_playwright
from draw import *
from draw2 import stroke, text
from draw3 import *
from render_thumbnails_v2 import shocked_head

proj = sys.argv[1]
out = os.path.join(proj, "09_THUMBNAIL")


def trolley(x, y, s, items):
    return (f'<g transform="translate({x} {y}) scale({s})">{items}<path d="M-160 -200 L170 -200 L140 -40 L-130 -40 Z" fill="#C9C6C0" fill-opacity="0.55" {stroke(6)}/>'
            + "".join(f'<path d="M{xx} -200 L{xx * 0.85:.0f} -40" stroke="#9A968E" stroke-width="4"/>' for xx in range(-120, 160, 50)) +
            f'<path d="M-200 -260 L-160 -200" {stroke(10)}/><path d="M-130 -40 L-110 0 L120 0" fill="none" {stroke(6)}/>'
            f'<circle cx="-90" cy="20" r="22" fill="{INK}"/><circle cx="100" cy="20" r="22" fill="{INK}"/></g>')


def panel(with_bees):
    c = bg_supermarket(0.3, fade=0.0 if with_bees else 1.0)
    if not with_bees:
        c += f'<rect x="-600" y="-400" width="3200" height="1900" fill="#5E6A7A" opacity="0.35"/>'
        c += "".join(f'<path d="M{x} {y} l18 -10 l-6 22 Z" fill="#C8BFA8" opacity="0.7"/>' for x, y in [(300, 980), (1500, 1020), (1100, 1080)])
    s = 1.55
    X, Y = 960, 1250
    if with_bees:
        fruit = (apple(-80, -230, 1.0) + strawberry(0, -240, 1.0) + melon(80, -230, 0.8) + cherry(-30, -280, 1.0) + avocado(60, -290, 0.8) + blueberry(-110, -280, 0.9) + pumpkin(120, -280, 0.7))
        c += pp(X, Y, s, 1.0, 3.0, arms=(70, 70), mouth="grin", look=(0, -4), eyes="open")
        c += trolley(X + 20, Y - 40, 1.0, fruit)
        r = rnd(9)
        for k in range(9):
            a = k / 9 * 6.28
            c += honeybee(960 + 560 * math.cos(a) + r.uniform(-60, 60), 520 + 300 * math.sin(a) + r.uniform(-40, 40), r.uniform(0.35, 0.5), k, flip=math.cos(a) > 0)
    else:
        c += person(X, Y, s, arms=(122, 122), mouth="none", eyes="open", hat="bucket", glasses=False, satchel=True)
        c += shocked_head(X, Y - 340 * s, 62 * s, mouth="o", hat=True, look=(0, 4))
        c += trolley(X + 20, Y - 40, 1.0, bread(-20, -230, 0.9) + rice_bowl(70, -240, 0.6))
    return c


r = rnd(5)
torn = "M965 -60 " + " ".join(f"L{965 + r.uniform(-22, 22):.0f} {y}" for y in range(-20, 1160, 36)) + " L965 1160"
right_clip = f"{torn} L2000 1160 L2000 -60 Z"


def label(txt, color, x, y, size=140):
    return (f'<text x="{x}" y="{y}" text-anchor="middle" font-family="Inter Display, Inter, sans-serif" font-weight="900" font-size="{size}" letter-spacing="3" '
            f'fill="{color}" stroke="{INK}" stroke-width="{size * 0.17:.0f}" stroke-linejoin="round" paint-order="stroke">{txt}</text>')


content = (f'<clipPath id="lc"><rect x="0" y="0" width="980" height="1080"/></clipPath><clipPath id="rcl"><path d="{right_clip}"/></clipPath>'
           f'<g clip-path="url(#lc)"><g transform="translate(490 540) scale(1.02) translate(-960 -540)">{panel(True)}</g></g>'
           f'<g clip-path="url(#rcl)"><g transform="translate(1430 540) scale(1.02) translate(-960 -540)">{panel(False)}</g></g>'
           f'<path d="{torn}" fill="none" stroke="{CREAM}" stroke-width="30"/><path d="{torn}" fill="none" stroke="{INK}" stroke-width="7"/>'
           + label("WITH BEES", CREAM, 480, 160) + label("WITHOUT", RED, 1440, 160)
           + f'<g transform="translate(1560 960) rotate(-7)"><rect x="-260" y="-62" width="520" height="104" rx="14" fill="{MUSTARD}" {stroke(8)}/>'
             f'<circle cx="-228" cy="-10" r="12" fill="{CREAM}" {stroke(5)}/>' + text(15, 16, "87 OF 115 CROPS", 50, INK) + '</g>')
svg = frame_svg(content, (1.0, 960, 540), seed=2, vignette=0.55, grain=0.0)
with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/opt/pw-browsers/chromium-1243/chrome-linux64/chrome")
    pg = b.new_page(viewport={"width": 1920, "height": 1080})
    pg.set_content('<html><body style="margin:0">' + svg + '</body></html>')
    master = os.path.join(out, "thumb_bees_detailed_master_1920x1080.png")
    pg.screenshot(path=master, clip={"x": 0, "y": 0, "width": 1920, "height": 1080})
    b.close()
jpg = os.path.join(out, "thumb_bees_detailed_1280x720.jpg")
subprocess.run(["convert", master, "-resize", "1280x720", "-unsharp", "0x0.6", "-quality", "90", jpg], check=True)
subprocess.run(["convert", jpg, "-resize", "336x189", os.path.join(out, "thumb_bees_mobile_336px.png")], check=True)
print(jpg, os.path.getsize(jpg) // 1024, "KB")
