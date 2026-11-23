"""Detailed before/after thumbnail (reference-channel principles, original execution).

11:59 PM: Pip in bed, awake and annoyed, surrounded by buzzing mosquitoes, warm lamp light.
12:00 AM: same room in moonlight, every mosquito has dropped dead, Pip shocked.
Usage: python3 render_thumbnail_detailed.py <project_dir>
"""
import math, os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from playwright.sync_api import sync_playwright
from draw import *
from draw2 import stroke, text, buzz_lines as _bl
from render_thumbnails_v2 import shocked_head

proj = sys.argv[1]
out = os.path.join(proj, "09_THUMBNAIL")


def room(night, minute_angle):
    """One-point-perspective bedroom in a 1000x1080 panel. night=True -> moonlit, lamp off."""
    wall, side, ceil, floor_c = (("#2C3A5E", "#1F2A47", "#18213A", "#3A3550") if night else ("#D9B98A", "#B8946A", "#A9855E", "#9C6E4A"))
    o = []
    o.append(f'<rect x="-50" y="-50" width="1100" height="1200" fill="{wall}"/>')
    # wallpaper stripes on back wall
    o += [f'<path d="M{x} 120 L{x} 700" stroke="{"#33436A" if night else "#CFAE7E"}" stroke-width="14"/>' for x in range(175, 850, 50)]
    o.append(f'<path d="M0 0 L150 120 L150 700 L0 1080 Z" fill="{side}" {stroke()}/>')
    o.append(f'<path d="M1000 0 L850 120 L850 700 L1000 1080 Z" fill="{side}" {stroke()}/>')
    o.append(f'<path d="M0 0 L1000 0 L850 120 L150 120 Z" fill="{ceil}" {stroke()}/>')
    o.append(f'<path d="M150 700 L850 700 L1000 1080 L0 1080 Z" fill="{floor_c}" {stroke()}/>')
    # floorboards converging to the vanishing point (500, 420)
    for k in range(-6, 7):
        x2 = 500 + k * 170
        o.append(f'<path d="M{500 + k * 58:.0f} 700 L{x2:.0f} 1080" stroke="{"#2E2944" if night else "#875C3C"}" stroke-width="4"/>')
    for y in (760, 840, 950):
        o.append(f'<path d="M0 {y} L1000 {y}" stroke="{"#2E2944" if night else "#875C3C"}" stroke-width="3" opacity="0.6"/>')
    # rug
    o.append(f'<path d="M260 900 L740 900 L840 1060 L160 1060 Z" fill="{"#4A3F66" if night else "#B5543F"}" {stroke(5)}/>'
             f'<path d="M300 925 L700 925 L780 1040 L220 1040 Z" fill="none" stroke="{"#6A5F86" if night else MUSTARD}" stroke-width="6"/>')
    # window with curtains on back wall
    o.append(f'<rect x="580" y="180" width="220" height="250" rx="6" fill="#141C36" {stroke()}/>'
             f'<circle cx="730" cy="240" r="34" fill="#F4E9B8" {stroke(4)}/>'
             + "".join(f'<circle cx="{x}" cy="{y}" r="3" fill="#F4E9B8"/>' for x, y in [(610, 210), (650, 300), (700, 380), (760, 330), (620, 390)]) +
             f'<path d="M690 180 L690 430 M580 305 L800 305" {stroke(6)}/>'
             f'<path d="M560 170 Q590 300 570 450 L610 450 Q600 300 600 170 Z" fill="{"#5E4E8A" if night else "#C9563F"}" {stroke(5)}/>'
             f'<path d="M820 170 Q790 300 810 450 L770 450 Q780 300 780 170 Z" fill="{"#5E4E8A" if night else "#C9563F"}" {stroke(5)}/>'
             f'<path d="M545 170 L835 170" {stroke(10)}/>')
    if night:  # moonbeam
        o.append('<path d="M590 430 L800 430 L900 1060 L420 1060 Z" fill="#F4E9B8" opacity="0.10"/>')
    # wall clock
    ticks = "".join(f'<path d="M0 -62 L0 -50" transform="rotate({k * 30})" {stroke(5)}/>' for k in range(12))
    o.append(f'<g transform="translate(300 230)"><circle r="74" fill="#F3EAD3" {stroke()}/>{ticks}'
             f'<path d="M0 0 L0 -36" {stroke(9)}/><path d="M0 0 L0 -56" transform="rotate({minute_angle})" stroke="{RED}" stroke-width="7" stroke-linecap="round"/><circle r="7" fill="{INK}"/></g>')
    # framed poster (on left wall, skewed) and bookshelf (on right wall)
    o.append(f'<path d="M30 200 L110 230 L110 420 L30 420 Z" fill="#F6F0E2" {stroke(5)}/><path d="M50 300 Q70 260 95 300" fill="none" stroke="#7FA65A" stroke-width="8"/>')
    o.append(f'<path d="M880 260 L980 220 L980 600 L880 590 Z" fill="#6B4A35" {stroke(5)}/>')
    cols = ["#C9563F", MUSTARD, "#5B8DB8", "#7FA65A", "#D96C8A", "#9C7B5B"]
    for sh, y in enumerate((300, 420, 540)):
        o.append(f'<path d="M880 {y + 30} L980 {y - 10 + sh * 4}" {stroke(5)}/>')
        for b in range(5):
            x = 890 + b * 18
            o.append(f'<rect x="{x}" y="{y - 60 - b * 3 + sh * 2}" width="14" height="{80 + (b % 2) * 6}" fill="{cols[(b + sh) % 6]}" {stroke(3)}/>')
    # nightstand + lamp + book
    o.append(f'<rect x="60" y="640" width="190" height="230" rx="6" fill="#5C4433" {stroke()}/><path d="M60 740 L250 740" {stroke(5)}/><circle cx="155" cy="700" r="8" fill="{INK}"/>'
             f'<path d="M120 580 L120 640 M90 640 L150 640" {stroke(7)}/>'
             f'<path d="M70 520 L170 520 L150 585 L90 585 Z" fill="{MUSTARD if not night else "#7A6A52"}" {stroke(5)}/>'
             f'<rect x="170" y="616" width="66" height="24" rx="3" fill="#5B8DB8" {stroke(4)}/>')
    if not night:
        o.append('<circle cx="120" cy="560" r="330" fill="url(#glow)" opacity="0.75"/>')
    return "".join(o)


def bed_parts(night):
    blanket_c = "#4F6D7A" if not night else "#3B4F66"
    back = (f'<rect x="230" y="470" width="540" height="270" rx="20" fill="#7A5338" {stroke()}/>'
            f'<rect x="250" y="490" width="500" height="40" rx="14" fill="#8E6544" {stroke(4)}/>'
            f'<path d="M230 470 L230 880 M770 470 L770 880" stroke="#5A3A28" stroke-width="26" stroke-linecap="round"/>'
            f'<g transform="translate(232 455) rotate(-14) scale(0.75)">{bucket_hat()}</g>'
            f'<ellipse cx="500" cy="620" rx="215" ry="95" fill="#EDE6D6" {stroke()}/>')
    front = (f'<path d="M180 745 Q500 700 820 745 L860 1000 Q500 1040 140 1000 Z" fill="{blanket_c}" {stroke()}/>'
             f'<path d="M196 775 Q500 732 804 775" fill="none" stroke="#DDD5C2" stroke-width="22"/>'
             f'<path d="M260 900 Q400 930 520 900 M560 940 Q680 960 780 930" fill="none" stroke="#2F4250" stroke-width="5"/>'
             f'<rect x="150" y="990" width="720" height="70" rx="12" fill="#7A5338" {stroke()}/>')
    return back, front


def panel_before():
    o = room(False, -6)
    back, front = bed_parts(False)
    o += back
    s = 1.6
    Y = 440 + 340 * s
    o += person(500, Y, s, arms=(95, -66), mouth="none", eyes="open", hat=None, satchel=False, legs=False)
    o += shocked_head(500, Y - 340 * s, 62 * s, mouth="worried", hat=False).replace(
        '<path d="M50 -10 Q58 6 50 14 Q42 6 50 -10 Z" fill="#9DD3E6" stroke="#2B2420" stroke-width="3"/>', "")
    # angry brows override + bites
    hx, hy = 500, Y - 340 * s
    o += f'<path d="M{hx - 52} {hy - 44} L{hx - 12} {hy - 30} M{hx + 12} {hy - 30} L{hx + 52} {hy - 44}" stroke="{INK}" stroke-width="10" stroke-linecap="round"/>'
    for bx, by in [(300, 580), (345, 576), (390, 572)]:
        o += f'<circle cx="{bx}" cy="{by - 0}" r="22" fill="#F2A3A0" opacity="0.7"/><circle cx="{bx}" cy="{by}" r="11" fill="{RED}" {stroke(3)}/>'
    o += front
    r = rnd(19)
    for k in range(13):
        a = k / 13 * 6.28
        x, y = 500 + 360 * math.cos(a) + r.uniform(-30, 30), 470 + 250 * math.sin(a) + r.uniform(-30, 30)
        o += mosquito(x, y, r.uniform(0.55, 0.8), rot=r.uniform(-25, 25), frame=k, look=(-2 if x > 500 else 2, 2), flip=x > 500)
        if k % 3 == 0:
            o += _bl(x, y - 10, k, 1.0)
    return o


def dead_mosquito(x, y, s, rot):
    return mosquito(x, y, s, rot=rot, frame=0, dead=True, flap=False)


def panel_after():
    o = room(True, 0)
    back, front = bed_parts(True)
    o += back
    s = 1.6
    Y = 440 + 340 * s
    o += person(500, Y, s, arms=(122, 122), mouth="none", eyes="open", hat=None, satchel=False, legs=False)
    o += shocked_head(500, Y - 340 * s, 62 * s, mouth="o", look=(0, 4), hat=False)
    o += front
    r = rnd(23)
    spots = [(230, 860), (330, 900), (600, 880), (700, 920), (780, 850), (420, 960), (120, 1000), (880, 1030), (560, 1010), (300, 1040), (660, 1050)]
    for x, y in spots:
        o += dead_mosquito(x, y, r.uniform(0.5, 0.65), 180 + r.uniform(-25, 25))
    # a few still falling, with motion lines
    for x, y in [(250, 420), (760, 380), (830, 600)]:
        o += f'<path d="M{x - 6} {y - 120} l0 70 M{x + 22} {y - 110} l0 60" stroke="#F4E9B8" stroke-width="6" stroke-linecap="round" opacity="0.7"/>'
        o += dead_mosquito(x, y, 0.6, 160)
    return o


def label(txt, color, x, y, size=150):
    return (f'<text x="{x}" y="{y}" text-anchor="middle" font-family="Inter Display, Inter, sans-serif" font-weight="900" font-size="{size}" '
            f'letter-spacing="3" fill="{color}" stroke="{INK}" stroke-width="{size * 0.17:.0f}" stroke-linejoin="round" paint-order="stroke">{txt}</text>')


r = rnd(5)
torn = "M965 -60 " + " ".join(f"L{965 + r.uniform(-22, 22):.0f} {y}" for y in range(-20, 1160, 36)) + " L965 1160"
right_clip = f"{torn} L2000 1160 L2000 -60 Z"
content = (f'<clipPath id="lc"><rect x="0" y="0" width="980" height="1080"/></clipPath><clipPath id="rcl"><path d="{right_clip}"/></clipPath>'
           f'<g clip-path="url(#lc)"><g transform="translate(-10 0)">{panel_before()}</g></g>'
           f'<g clip-path="url(#rcl)"><g transform="translate(940 0)">{panel_after()}</g></g>'
           f'<path d="{torn}" fill="none" stroke="{CREAM}" stroke-width="30"/><path d="{torn}" fill="none" stroke="{INK}" stroke-width="7"/>'
           + label("11:59 PM", CREAM, 480, 175) + label("12:00 AM", RED, 1440, 175)
           + f'<g transform="translate(1560 950) rotate(-7)"><rect x="-250" y="-62" width="500" height="104" rx="14" fill="{MUSTARD}" {stroke(8)}/>'
             f'<circle cx="-218" cy="-10" r="12" fill="{CREAM}" {stroke(5)}/>'
           + text(15, 16, "ALL 3,500 SPECIES", 48, INK) + '</g>')
svg = frame_svg(content, (1.0, 960, 540), seed=2, vignette=0.55, grain=0.0)
with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/opt/pw-browsers/chromium-1243/chrome-linux64/chrome")
    pg = b.new_page(viewport={"width": 1920, "height": 1080})
    pg.set_content('<html><body style="margin:0">' + svg + '</body></html>')
    master = os.path.join(out, "thumb_D_detailed_master_1920x1080.png")
    pg.screenshot(path=master, clip={"x": 0, "y": 0, "width": 1920, "height": 1080})
    b.close()
jpg = os.path.join(out, "thumb_D_detailed_1280x720.jpg")
subprocess.run(["convert", master, "-resize", "1280x720", "-unsharp", "0x0.6", "-quality", "90", jpg], check=True)
subprocess.run(["convert", jpg, "-resize", "336x189", os.path.join(out, "thumb_D_mobile_336px.png")], check=True)
print(jpg, os.path.getsize(jpg) // 1024, "KB")
