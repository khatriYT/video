"""Three high-contrast thumbnail variants for YouTube 'Test & compare'.

Usage: python3 render_thumbnails_v2.py <project_dir>
Outputs 09_THUMBNAIL/thumb_A|B|C_1280x720.jpg (<2 MB, YouTube limit) + 1920 masters + mobile preview sheet.
"""
import os, sys, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from playwright.sync_api import sync_playwright
from draw import *
from draw2 import *
import scenes_mosquito as S

proj = sys.argv[1]
out = os.path.join(proj, "09_THUMBNAIL")


def shocked_head(x, y, r, look=(0, 0), mouth="o", hat=True, skin=SKIN_PIP):
    s = r / 62
    lx, ly = look
    eyes = (f'<circle cx="-21" cy="4" r="14" fill="#FFF" stroke="{INK}" stroke-width="3"/><circle cx="21" cy="4" r="14" fill="#FFF" stroke="{INK}" stroke-width="3"/>'
            f'<circle cx="{-21 + lx}" cy="{4 + ly}" r="6" fill="{INK}"/><circle cx="{21 + lx}" cy="{4 + ly}" r="6" fill="{INK}"/>')
    glasses = (f'<circle cx="-21" cy="4" r="19" fill="none" stroke="{INK}" stroke-width="4.5"/><circle cx="21" cy="4" r="19" fill="none" stroke="{INK}" stroke-width="4.5"/>'
               f'<path d="M-2 3 L2 3 M-40 1 L-58 -4 M40 1 L58 -4" stroke="{INK}" stroke-width="4" stroke-linecap="round"/>')
    m = {"o": f'<ellipse cx="0" cy="40" rx="11" ry="14" fill="{INK}"/><ellipse cx="0" cy="46" rx="6" ry="4" fill="#C9563F"/>',
         "worried": f'<path d="M-14 42 Q0 32 14 42" fill="none" stroke="{INK}" stroke-width="5" stroke-linecap="round"/>'}[mouth]
    brows = f'<path d="M-36 -22 Q-22 -32 -8 -24 M8 -24 Q22 -32 36 -22" fill="none" stroke="{INK}" stroke-width="5" stroke-linecap="round"/>'
    sweat = f'<path d="M50 -10 Q58 6 50 14 Q42 6 50 -10 Z" fill="#9DD3E6" stroke="{INK}" stroke-width="3"/>'
    h = f'<g transform="translate(0 -6)">{bucket_hat()}</g>' if hat else ""
    return (f'<g transform="translate({x} {y}) scale({s:.3f})"><circle r="62" fill="{skin}" stroke="{INK}" stroke-width="5"/>'
            f'{eyes}{glasses}{brows}{m}{sweat}{h}</g>')


def big_text(lines, x, y, size, anchor="start", lh=0.98):
    o = ""
    for i, (t, c) in enumerate(lines):
        o += (f'<text x="{x}" y="{y + i * size * lh:.0f}" text-anchor="{anchor}" font-family="Inter Display, Inter, sans-serif" font-weight="900" '
              f'font-size="{size}" letter-spacing="2" fill="{c}" stroke="{INK}" stroke-width="{size * 0.16:.0f}" stroke-linejoin="round" paint-order="stroke">{t}</text>')
    return o


def glow_bg(c1, c2, cx=60, cy=45, gid="tb"):
    return (f'<defs><radialGradient id="{gid}" cx="{cx}%" cy="{cy}%" r="75%"><stop offset="0" stop-color="{c1}"/><stop offset="1" stop-color="{c2}"/></radialGradient></defs>'
            f'<rect x="-100" y="-100" width="2120" height="1280" fill="url(#{gid})"/>')


def clock(x, y, r):
    ticks = "".join(f'<path d="M0 {-r + 8} L0 {-r + 28}" transform="rotate({k * 30})" stroke="{INK}" stroke-width="8"/>' for k in range(12))
    return (f'<g transform="translate({x} {y})"><circle r="{r}" fill="#F3EAD3" stroke="{INK}" stroke-width="12"/>{ticks}'
            f'<path d="M0 0 L0 {-r * 0.5}" stroke="{INK}" stroke-width="16" stroke-linecap="round"/>'
            f'<path d="M0 0 L0 {-r * 0.78}" stroke="{RED}" stroke-width="12" stroke-linecap="round"/><circle r="14" fill="{INK}"/></g>')


def main():
    # A: "EVERY ONE. GONE." -- dead mosquito falling at midnight + shocked Pip
    A = glow_bg("#3E4F7E", "#0E1426", 30, 40, "ga")
    A += f'<circle cx="560" cy="470" r="520" fill="url(#glow)" opacity="0.35"/>'
    A += clock(1010, 170, 115)
    A += "".join(f'<path d="M{x} {y} l0 -90" stroke="#F4E9B8" stroke-width="7" stroke-linecap="round" opacity="0.55"/>' for x, y in [(380, 330), (470, 270), (640, 300), (720, 360)])
    A += mosquito(560, 560, 4.2, rot=165, frame=0, dead=True, flap=False)
    A += shocked_head(1450, 790, 330, look=(-6, -2))
    A += big_text([("EVERY ONE.", CREAM), ("GONE.", RED)], 60, 860, 170)

    # B: giant mosquito looming over Pip, "DELETE THEM?"
    B = glow_bg("#F7C98B", "#B5543F", 70, 40, "gb")
    B += mosquito(1250, 470, 6.0, frame=0, look=(-6, 4), flip=True)
    B += shocked_head(470, 930, 330, look=(10, -6), mouth="worried")
    B += big_text([("DELETE", CREAM), ("THEM ALL?", MUSTARD)], 60, 180, 150)

    # C: Earth with every mosquito vanishing, "ALL GONE?"
    r_ = rnd(77)
    C = glow_bg("#1B2442", "#05070F", 50, 50, "gc")
    C += "".join(f'<circle cx="{r_.uniform(0, 1920):.0f}" cy="{r_.uniform(0, 1080):.0f}" r="{r_.choice([2, 3, 4])}" fill="#F4E9B8"/>' for _ in range(90))
    C += S.earth(1260, 560, 380)
    for k in range(46):
        import math
        a = r_.uniform(0, 6.28); d = r_.uniform(420, 560)
        x, y = 1260 + d * math.cos(a), 560 + d * math.sin(a) * 0.9
        C += tiny_mosquito(x, y, 1.6, frame=k, alpha=1.0 if x < 1260 else 0.25, rot=r_.uniform(-20, 20))
        if x >= 1260:
            C += f'<path d="M{x - 16:.0f} {y - 16:.0f} l32 32 M{x + 16:.0f} {y - 16:.0f} l-32 32" stroke="{RED}" stroke-width="9" stroke-linecap="round"/>'
    C += shocked_head(330, 830, 230, look=(10, -4))
    C += big_text([("ALL 3,500", CREAM), ("SPECIES?", MUSTARD)], 60, 180, 150)

    variants = {"A": A, "B": B, "C": C}
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path="/opt/pw-browsers/chromium-1243/chrome-linux64/chrome")
        pg = b.new_page(viewport={"width": 1920, "height": 1080})
        for k, content in variants.items():
            svg = frame_svg(content, (1.0, 960, 540), seed=1, vignette=0.7, grain=0.0)
            pg.set_content('<html><body style="margin:0">' + svg + '</body></html>')
            master = os.path.join(out, f"thumb_{k}_master_1920x1080.png")
            pg.screenshot(path=master, clip={"x": 0, "y": 0, "width": 1920, "height": 1080})
            jpg = os.path.join(out, f"thumb_{k}_1280x720.jpg")
            subprocess.run(["convert", master, "-resize", "1280x720", "-unsharp", "0x0.6", "-quality", "90", jpg], check=True)
            print(jpg, os.path.getsize(jpg) // 1024, "KB")
        b.close()
    # mobile-size readability check (YouTube home feed on phones shows ~320-360 px wide)
    subprocess.run(["montage"] + [os.path.join(out, f"thumb_{k}_1280x720.jpg") for k in "ABC"] +
                   ["-tile", "3x1", "-geometry", "336x189+8+8", "-background", "#0F0F0F", os.path.join(out, "mobile_preview_336px.png")], check=True)


if __name__ == "__main__":
    main()
