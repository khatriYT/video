"""Episode 2 scenes 001-035. Kinetic on-screen text is added automatically by render.py from storyboard.json."""
import math
from draw import *
from draw2 import stroke, text, sky, tree, bat, moth, beetle, hoverfly, spider, web, question_mark, auto_eyes, check, dinosaur
from draw3 import *

KEYFRAME = {}


def clock_icon(x, y, r, t):
    ticks = "".join(f'<path d="M0 {-r + 6} L0 {-r + 18}" transform="rotate({k * 30})" {stroke(4)}/>' for k in range(12))
    return (f'<g transform="translate({x} {y})"><circle r="{r}" fill="#F3EAD3" {stroke(6)}/>{ticks}<path d="M0 0 L0 {-r * 0.5}" {stroke(7)}/>'
            f'<path d="M0 0 L0 {-r * 0.75}" transform="rotate({t * 60 % 360:.0f})" stroke="{RED}" stroke-width="5" stroke-linecap="round"/><circle r="5" fill="{INK}"/></g>')


def cork_board(t, card=True, card_y=0.0, card_scale=1.0, card_rot=-3):
    out = f'<rect x="-600" y="-400" width="3200" height="1900" fill="#D9C9A8"/><rect x="-600" y="900" width="3200" height="700" fill="#8A6A4E" {stroke()}/>'
    out += f'<rect x="300" y="110" width="1320" height="760" rx="10" fill="#C9955E" stroke="#6B4A35" stroke-width="24"/>'
    r = rnd(3)
    out += "".join(f'<circle cx="{r.uniform(330, 1590):.0f}" cy="{r.uniform(140, 840):.0f}" r="3" fill="#A8743A"/>' for _ in range(160))
    out += f'<rect x="1260" y="200" width="250" height="180" fill="#F6F0E2" transform="rotate(5 1385 290)" {stroke(4)}/><path d="M1300 330 L1360 260 L1400 300 L1470 230" fill="none" stroke="#5B8DB8" stroke-width="6" transform="rotate(5 1385 290)"/>'
    out += f'<rect x="420" y="620" width="220" height="160" fill="#FFF6E0" transform="rotate(-6 530 700)" {stroke(4)}/>'
    sil = (f'<g transform="translate(530 690) rotate(-6) scale(0.8)"><circle cx="0" cy="-10" r="40" fill="#C8BFA8"/>'
           + "".join(f'<path d="M{-40 + k * 10} -40 q{-6 + k * 2} -24 {-10 + k * 4} -30" fill="none" stroke="#8A8070" stroke-width="5"/>' for k in range(9)) +
           f'<path d="M-50 70 Q0 30 50 70" fill="#C8BFA8"/></g>')
    out += sil + text(530, 760, "?", 40, "#8A8070")
    if card:
        k = card_scale
        out += (f'<g transform="translate(960 {490 + card_y:.0f}) rotate({card_rot}) scale({k:.3f})"><rect x="-380" y="-200" width="760" height="400" fill="#F3E6C4" {stroke(6)}/>'
                f'<path d="M-340 -120 L340 -120 M-340 -60 L340 -60 M-340 0 L340 0 M-340 60 L240 60" stroke="#E2CDA4" stroke-width="4"/>'
                f'<circle cx="0" cy="-180" r="16" fill="{RED}" {stroke(4)}/></g>')
    return out


# ---------------- HOOK ----------------
def s001(t, T, fr):
    up = ease(seg(t, 0.25 * T, 0.6 * T))
    c = bg_cottage_garden(t, "sunrise", window_open=1.0, insects=False)
    c += pp(1150, 1010, 1.05, t, T, arms=(lerp(18, 155, up), lerp(18, 155, up)), mouth="o" if 0.3 < up < 0.9 else "smile", eyes="closed" if 0.3 < up < 0.9 else auto_eyes(t, T))
    return c, cam_push(t, T, 1.0, 1.08, 1000, 640)


def s002(t, T, fr):
    c = bg_paper2(t, "#EFE6D0") + f'<rect x="240" y="150" width="1440" height="860" rx="14" fill="#FBF6EA" {stroke(6)}/>'
    kinds = []
    for row in range(4):
        for col in range(7):
            k = row * 7 + col
            x, y = 360 + col * 200, 280 + row * 200
            gone = seg(t, 0.25 * T + row * 0.13 * T, 0.33 * T + row * 0.13 * T)
            c += f'<path d="M{x - 70} {y + 70} L{x + 70} {y + 70}" stroke="#E2CDA4" stroke-width="3"/>' + text(x, y + 94, f"No. {k + 1}", 18, "#B5A88E", weight=700)
            if gone < 1:
                if k % 4 == 0:
                    b = honeybee(x, y, 0.55, 0, flap=False)
                elif k % 4 == 1:
                    b = bumblebee(x, y, 0.5, 0)
                elif k % 4 == 2:
                    b = solitary_bee(x, y, 0.8, 0, ["#4A5A78", "#3E7A4A", "#8A6A4E", "#5E4E8A"][k % 4], flip=False)
                else:
                    b = solitary_bee(x, y, 0.7, 0, "#2F2622", "#F2B33D")
                c += f'<g opacity="{1 - gone:.2f}">{b}</g>'
            c += puff(x, y, gone, 40)
    return c, cam_push(t, T, 1.08, 1.0, 960, 560)


def s003(t, T, fr):
    lid = seg(t, 0.2 * T, 0.55 * T)
    c = bg_apiary(t)
    c += hive_box(400, 960, 0.8, "#9DB8D6") + hive_box(1500, 960, 0.8, MUSTARD)
    c += hive_box(960, 1000, 1.3, "#F6F0E2", lid=lid)
    if lid > 0.4:
        for k in range(5):
            c += f'<rect x="{850 + k * 46}" y="{720 - 30 * ease(lid):.0f}" width="34" height="60" fill="#E7A33A" {stroke(3)}/>'
    c += beekeeper(1320, 1020, 1.2, t, T, arms=(20, lerp(20, 70, ease(lid))), mouth="o" if lid > 0.6 else "flat")
    return c, cam_push(t, T, 1.0, 1.08, 1060, 660)


def s004(t, T, fr):
    c = sky("#A9CFE0", "#F3E6C4", "s4") + clouds(t, 150, seed=2, n=3)
    c += f'<path d="M-600 820 Q900 760 2600 820 L2600 1600 L-600 1600 Z" fill="#7FA65A" {stroke()}/>'
    r = rnd(4)
    for k, x in enumerate(range(80, 1900, 180)):
        f = [daisy, tulip, rose, sunflower][k % 4]
        s = r.uniform(2.0, 2.6) if f is not sunflower else 1.5
        c += f(x, 1100, s, t * 0.6, k) if f is not daisy else daisy(x, 1100, s, t * 0.6, k, col=["#FFFFFF", "#F6A6B8", "#C9B6E4"][k % 3], stem=150)
    c += grass_tufts(-200, 2200, 1080, n=60, t=t)
    c += clock_icon(1700, 180, 90, t * 3)
    return c, cam_pan(t, T, 900, 1060, 1.04)


def s005(t, T, fr):
    drop = ease_out_bounce(seg(t, 0.1 * T, 0.5 * T))
    return cork_board(t, True, card_y=-300 * (1 - drop), card_scale=0.9), cam_push(t, T, 1.0, 1.06, 960, 520)


def s006(t, T, fr):
    return cork_board(t, True, card_scale=1.75, card_rot=-1), cam_push(t, T, 1.0, 1.04, 960, 490)


def s007(t, T, fr):
    sh = 10 * math.sin(t * 50) * (1 - seg(t, 0.3 * T + 0.25, 0.3 * T + 0.6)) if t > 0.3 * T + 0.2 else 0
    return cork_board(t, True, card_scale=1.75, card_rot=-1), (1.04, 960 + sh, 490)


def fridge(x, y, s, door, t):
    shelf = ""
    items = [lambda a, b: apple(a, b, 0.6), lambda a, b: strawberry(a, b, 0.6), lambda a, b: blueberry(a, b, 0.6), lambda a, b: avocado(a, b, 0.5),
             lambda a, b: cherry(a, b, 0.6), lambda a, b: melon(a, b, 0.5), lambda a, b: apple(a, b, 0.6, "#F2B33D"), lambda a, b: pumpkin(a, b, 0.4)]
    for row in range(3):
        shelf += f'<path d="M-150 {-300 + row * 150} L150 {-300 + row * 150}" stroke="#C9D6E0" stroke-width="8"/>'
        for k in range(3):
            shelf += items[(row * 3 + k) % 8](-90 + k * 90, -330 + row * 150)
    w = 320 * (1 - door)
    return (f'<g transform="translate({x} {y}) scale({s})"><rect x="-170" y="-560" width="340" height="560" rx="20" fill="#F4F6F4" {stroke(6)}/>'
            f'<rect x="-160" y="-540" width="320" height="520" fill="#E9F3F6"/>' + f'<circle cx="0" cy="-460" r="200" fill="url(#glow)" opacity="{0.7 * door:.2f}"/>' + shelf +
            f'<path d="M-170 -560 L{-170 + w + 40 * door:.0f} {-560 - 30 * door:.0f} L{-170 + w + 40 * door:.0f} {30 * door:.0f} L-170 0 Z" fill="#DDE6E8" {stroke(6)}/></g>')


def s008(t, T, fr):
    door = ease(seg(t, 0.05 * T, 0.35 * T))
    c = bg_kitchen(t) + fridge(1250, 1040, 1.0, door, t)
    think = t > 0.4 * T
    c += pp(760, 1060, 1.15, t, T, arms=(15, 150 if think else 20), mouth="flat" if think else "o", look=(8, -4), tilt=-6 if think else 0)
    return c, cam_push(t, T, 1.0, 1.05, 1000, 620)


def s009(t, T, fr):
    drop = seg(t, 0.08 * T, 0.6 * T)
    hat_dy = -320 * (1 - ease_out_bounce(drop))
    c = f'<rect x="-600" y="-400" width="3200" height="1900" fill="#E8D4B0"/>' + "".join(f'<path d="M{x} -400 L{x} 900" stroke="#DCC59A" stroke-width="14"/>' for x in range(-560, 2600, 80))
    c += f'<rect x="-600" y="900" width="3200" height="700" fill="#9C7B5B" {stroke()}/>' + "".join(f'<path d="M{x} 900 L{x - 60} 1600" stroke="#8A6A4E" stroke-width="4"/>' for x in range(-500, 2600, 160))
    c += (f'<defs><linearGradient id="dr9" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stroke-color="#A9CFE0" stop-color="#A9CFE0"/><stop offset="1" stop-color="#F7C98B"/></linearGradient></defs>'
          f'<rect x="1100" y="220" width="420" height="680" fill="url(#dr9)" {stroke()}/>' + daisy(1200, 900, 1.2, t, 1) + tulip(1300, 900, 1.2, t, 2) + rose(1420, 900, 1.1, t, 3) +
          f'<path d="M1520 220 L1700 260 L1700 860 L1520 900 Z" fill="#5B8DB8" {stroke()}/>')
    c += f'<rect x="330" y="300" width="240" height="22" rx="6" fill="#7A5338" {stroke(5)}/>' + "".join(f'<circle cx="{x}" cy="340" r="10" fill="{INK}"/>' for x in (380, 450, 520))
    c += f'<g transform="translate(520 380) scale(0.6)"><path d="M-30 0 L30 0 L20 120 L-20 120 Z" fill="#8A5A35" {stroke(5)}/></g>'
    c += f'<rect x="380" y="560" width="180" height="120" rx="8" fill="#F6F0E2" {stroke(5)}/>' + daisy(470, 670, 0.5, t, 4)
    c += pp(820, 960, 1.25, t, T, arms=(20, 22), hat_dy=hat_dy, mouth="grin" if drop > 0.6 else "o", look=(0, -6 + 6 * drop))
    return c, (1.0, 960, 560)


def s010(t, T, fr):
    c = bg_farmland(t)
    c += f'<path d="M-600 1000 Q300 820 1000 900 L1000 1600 L-600 1600 Z" fill="#6E9A5E" {stroke()}/>' + flower_bed(-200, 900, 1000, t, seed=3, density=1.0, scale=0.7)
    c += pp(420, 960, 0.9, t, T, look=(8, -2), arms=(18, 22))
    return c, cam_push(t, T, 1.1, 1.0, 960, 540)


# ---------------- MEET THE BEES ----------------
def s011(t, T, fr):
    cr = seg(t, 0.3 * T, 0.6 * T)
    c = f'<rect x="-600" y="-400" width="3200" height="1900" fill="#3E4A5E"/><circle cx="960" cy="500" r="760" fill="url(#glow)" opacity="0.35"/>'
    c += "".join(f'<rect x="{x}" y="120" width="40" height="{h}" fill="{col}" {stroke(3)}/>' for x, h, col in [(150, 180, "#C9563F"), (200, 160, "#5B8DB8"), (250, 190, MUSTARD), (1650, 170, "#7FA65A"), (1700, 150, "#D96C8A")])
    c += pp(720, 1300, 2.0, t, T, arms=(15, 80), mouth="smile", look=(10, -2))
    c += f'<g transform="translate(1260 520) rotate(4)"><rect x="-260" y="-200" width="520" height="400" fill="#FBF6EA" {stroke(6)}/>{honeybee(0, 10, 1.6, 0, flap=False)}</g>'
    if cr > 0:
        c += f'<path d="M1020 340 L{1020 + 480 * min(1, cr * 2):.0f} {340 + 360 * min(1, cr * 2):.0f}" stroke="{RED}" stroke-width="22" stroke-linecap="round"/>'
        if cr > 0.5:
            u = (cr - 0.5) * 2
            c += f'<path d="M1500 340 L{1500 - 480 * u:.0f} {340 + 360 * u:.0f}" stroke="{RED}" stroke-width="22" stroke-linecap="round"/>'
    return c, (1.0, 960, 540)


def s012(t, T, fr):
    c = bg_apiary(t)
    cols = ["#F6F0E2", "#9DB8D6", MUSTARD, "#9CC5A1", "#D96C8A", "#F6F0E2"]
    for k in range(6):
        c += hive_box(140 + k * 300, 980 - (k % 2) * 30, 0.75, cols[k])
    c += beekeeper(1000, 1060, 1.1, t, T, arms=(20, 60), tool=(1, lambda hx, hy: smoker(hx + 40, hy + 10, 0.9, t)))
    r = rnd(5)
    for k in range(14):
        u = (t * 0.3 + k / 14) % 1
        x0 = 140 + (k % 6) * 300
        c += honeybee(x0 + 200 * math.sin(u * 6 + k), 780 - 400 * u + 30 * math.sin(t * 3 + k), 0.18, fr + k, flip=k % 2 == 0)
    return c, cam_pan(t, T, 860, 1060, 1.0)


def s013(t, T, fr):
    c = sky("#A9CFE0", "#F3E6C4", "s13") + f'<rect x="-600" y="300" width="3200" height="80" fill="#7FA65A" {stroke()}/>' + flower_bed(-200, 2200, 320, t, seed=5, density=1.2, scale=0.6)
    c += f'<rect x="-600" y="380" width="3200" height="1200" fill="#8A6A4E" {stroke()}/>'
    r = rnd(6)
    c += "".join(f'<circle cx="{r.uniform(-100, 2000):.0f}" cy="{r.uniform(420, 1080):.0f}" r="{r.choice([4, 6, 9])}" fill="#7A5A3E"/>' for _ in range(140))
    c += "".join(f'<ellipse cx="{r.uniform(0, 1900):.0f}" cy="{r.uniform(450, 1050):.0f}" rx="{r.uniform(14, 30):.0f}" ry="10" fill="#A8A096" {stroke(3)}/>' for _ in range(16))
    for k, x in enumerate((300, 760, 1220, 1640)):
        path = f"M{x} 380 Q{x + 40} 560 {x - 20} 700 Q{x - 60} 800 {x + 30} 900"
        c += f'<path d="{path}" fill="none" stroke="#5A3E28" stroke-width="44" stroke-linecap="round"/><path d="{path}" fill="none" {stroke(4)} opacity="0.5"/>'
        for j, (cx, cy) in enumerate([(x + 40, 620), (x - 40, 760), (x + 50, 900)]):
            c += f'<ellipse cx="{cx}" cy="{cy}" rx="60" ry="38" fill="#5A3E28" {stroke(4)}/><circle cx="{cx}" cy="{cy + 8}" r="18" fill="{MUSTARD}" {stroke(3)}/>'
        c += solitary_bee(x + 40, 610 - 14, 0.6, 0, ["#4A5A78", "#3E7A4A", "#2F2622", "#8A6A4E"][k], flip=k % 2 == 1)
    u = ease(seg(t, 0.2 * T, 0.9 * T))
    c += solitary_bee(lerp(1100, 1220, u), lerp(260, 440, u), 0.7, fr, "#5E4E8A", rot=lerp(0, 70, u))
    return c, (lerp(1.0, 1.06, t / T), 960, lerp(500, 620, ease(t / T)))


def s014(t, T, fr):
    c = sky("#B7CFE0", "#EEF3F4", "alp")
    c += f'<path d="M-600 600 L100 180 L500 460 L900 120 L1400 460 L1900 160 L2600 600 L2600 1600 L-600 1600 Z" fill="#8A9AAA" {stroke()}/>'
    c += f'<path d="M0 240 L100 180 L200 240 L150 260 Z M800 180 L900 120 L1000 180 L940 200 Z M1800 220 L1900 160 L2000 220 L1950 240 Z" fill="#FFFFFF" {stroke(4)}/>'
    c += f'<path d="M-600 760 Q800 680 2600 780 L2600 1600 L-600 1600 Z" fill="#9CB98A" {stroke()}/>'
    c += flower_bed(-200, 2200, 1000, t, seed=8, density=1.2, scale=0.9).replace("#7FA65A", "#8FB2A8")
    c += "".join(f'<path d="M{x} {y} l6 6 m-6 0 l6 -6" stroke="#FFFFFF" stroke-width="3"/>' for x, y in [(200, 960), (520, 990), (900, 1010), (1300, 980), (1700, 1000)])
    r = rnd(7)
    c += "".join(f'<circle cx="{(r.uniform(-100, 2000) + t * 20) % 2000:.0f}" cy="{(r.uniform(0, 1080) + t * 70) % 1080:.0f}" r="{r.choice([3, 4, 5])}" fill="#FFFFFF"/>' for _ in range(70))
    u = t / T
    c += bumblebee(lerp(200, 1600, u), 640 + 60 * math.sin(u * 6), 1.2, fr, look=(3, 2))
    c += f'<g opacity="0.6">' + "".join(f'<circle cx="{lerp(200, 1600, u) - 60 - k * 40:.0f}" cy="{640 + 60 * math.sin(u * 6) + 10:.0f}" r="{10 + k * 4}" fill="#FFFFFF" opacity="{0.5 - k * 0.1:.2f}"/>' for k in range(4)) + '</g>'
    return c, cam_pan(t, T, 800, 1120, 1.0)


def s015(t, T, fr):
    c = f'<rect x="-600" y="-400" width="3200" height="1900" fill="#C9A77C"/>' + "".join(f'<rect x="{x + (y // 70 % 2) * 60}" y="{y}" width="116" height="66" fill="#B98B5E" {stroke(3)}/>' for x in range(-600, 2600, 120) for y in range(-400, 1500, 70))
    c += f'<rect x="460" y="180" width="1000" height="720" rx="30" fill="#8A6A4E" {stroke()}/>'
    for j in range(4):
        for i in range(5):
            cx, cy = 580 + i * 190, 280 + j * 170
            c += f'<circle cx="{cx}" cy="{cy}" r="74" fill="#D8B48A" {stroke(5)}/><circle cx="{cx}" cy="{cy}" r="48" fill="#3B2A1E"/>'
    mud = ease(seg(t, 0.15 * T, 0.85 * T))
    c += f'<circle cx="960" cy="620" r="{48 * mud:.0f}" fill="#7A5A3E" {stroke(3)}/>'
    c += "".join(f'<circle cx="{960 + 30 * math.cos(k):.0f}" cy="{620 + 30 * math.sin(k):.0f}" r="6" fill="#6B4A35"/>' for k in range(int(mud * 8)))
    c += solitary_bee(960 + 90 + 6 * math.sin(t * 8), 600, 1.6, fr, "#2E3A6E", "#5E6E9E", flip=True)
    return c, cam_push(t, T, 1.0, 1.15, 960, 620)


def s016(t, T, fr):
    c = sky("#9CC5A1", "#E6F1EC", "lc")
    leaf = 'M300 900 Q200 500 700 240 Q1300 100 1640 360 Q1500 860 900 960 Q500 1000 300 900 Z'
    c += f'<path d="{leaf}" fill="#6E9A5E" {stroke(7)}/><path d="M360 880 Q900 520 1600 380" fill="none" stroke="#4E7F3A" stroke-width="10"/>'
    c += "".join(f'<circle cx="{x}" cy="{y}" r="60" fill="#9CC5A1" {stroke(5)}/>' for x, y in [(700, 520), (1000, 420), (1250, 600)])
    cut = seg(t, 0.15 * T, 0.5 * T)
    fly = ease(seg(t, 0.55 * T, 0.95 * T))
    cx, cy = 900, 700
    if cut < 1:
        c += f'<circle cx="{cx}" cy="{cy}" r="60" fill="none" stroke="#FFF6E0" stroke-width="6" stroke-dasharray="{377 * cut:.0f} 400"/>'
        c += solitary_bee(cx + 60 * math.cos(cut * 6.28) + 40, cy + 60 * math.sin(cut * 6.28) - 20, 1.0, fr, "#6E6A66", "#E6E0D2")
    else:
        c += f'<circle cx="{cx}" cy="{cy}" r="60" fill="#9CC5A1" {stroke(5)}/>'
        bx, by = lerp(cx, 1900, fly), lerp(cy - 60, 200, fly)
        c += f'<circle cx="{bx:.0f}" cy="{by + 40:.0f}" r="56" fill="#6E9A5E" {stroke(4)}/>' + solitary_bee(bx, by, 1.0, fr, "#6E6A66", "#E6E0D2")
    return c, (1.0, 960, 560)


def pollen_trail(pts, t, k=0):
    d = "M" + " L".join(f"{x:.0f} {y:.0f}" for x, y in pts)
    return f'<path d="{d}" fill="none" stroke="{MUSTARD}" stroke-width="6" stroke-dasharray="4 16" stroke-linecap="round" stroke-dashoffset="{-t * 60 - k * 9:.0f}" opacity="0.9"/>'


def s017(t, T, fr):
    c = bg_meadow2(t, seed=31)
    r = rnd(31)
    for k in range(12):
        x0, y0 = r.uniform(100, 1800), r.uniform(650, 1000)
        x1, y1 = x0 + r.uniform(-300, 300), y0 + r.uniform(-120, 60)
        u = (t * 0.25 + k / 12) % 1
        pts = [(lerp(x0, x1, v), lerp(y0, y1, v) - 120 * math.sin(v * math.pi)) for v in [i / 10 for i in range(int(u * 10) + 1)]]
        if len(pts) > 1:
            c += pollen_trail(pts, t, k)
        bx, by = lerp(x0, x1, u), lerp(y0, y1, u) - 120 * math.sin(u * math.pi)
        c += [honeybee, bumblebee][k % 2](bx, by, 0.3, fr + k, flip=x1 < x0) if k % 3 else solitary_bee(bx, by, 0.5, fr + k, "#3E7A4A", flip=x1 < x0)
    return c, cam_push(t, T, 1.06, 1.0, 960, 600)


# ---------------- INSIDE THE HIVE ----------------
def s018(t, T, fr):
    c = f'<rect x="-600" y="-400" width="3200" height="1900" fill="#6B4A2E"/>' + hex_comb(-200, -100, 34, 26, 44, capped=0.45)
    c += f'<rect x="-600" y="-400" width="3200" height="1900" fill="#3B2A1E" opacity="0.2"/><circle cx="960" cy="560" r="640" fill="url(#glow)" opacity="0.45"/>'
    r = rnd(18)
    for k in range(34):
        x, y = r.uniform(-100, 2000), r.uniform(-50, 1150)
        if abs(x - 960) < 200 and abs(y - 560) < 160:
            continue
        c += honeybee(x + 12 * math.sin(t * 2 + k), y + 8 * math.cos(t * 2.4 + k), 0.38, 0, rot=r.uniform(-180, 180), flap=False)
    glow = 0.5 + 0.5 * math.sin(t * 3)
    c += f'<circle cx="960" cy="560" r="{180 + 20 * glow:.0f}" fill="url(#glow)" opacity="0.8"/>' + honeybee(960, 560, 1.4, fr, queen=True, flap=False)
    return c, cam_push(t, T, 1.0, 1.08, 960, 560)


def s019(t, T, fr):
    c = f'<rect x="-600" y="-400" width="3200" height="1900" fill="#6B4A2E"/>' + hex_comb(-200, -100, 34, 26, 44, capped=0.55, seed=19)
    c += f'<rect x="-600" y="-400" width="3200" height="1900" fill="#3B2A1E" opacity="0.25"/>'
    u = (t / 2.2) % 1
    a = u * 2 * math.pi
    if u < 0.5:
        x, y = 960 + 200 * math.sin(a * 2) * 0.5 - 100, 560 + 140 * math.cos(a * 2) * 0.0 + lerp(140, -140, u * 2)
        x = 960 + 18 * math.sin(t * 40)
        y = lerp(700, 420, u * 2)
        rot = -90
    else:
        v = (u - 0.5) * 2
        side = -1 if int(t / 2.2) % 2 else 1
        x = 960 + side * 200 * math.sin(v * math.pi)
        y = lerp(420, 700, v)
        rot = 90 if v > 0.5 else -90
    c += f'<path d="M960 420 L960 700" stroke="#FFF3C4" stroke-width="6" stroke-dasharray="14 12" opacity="0.8"/>'
    c += f'<path d="M960 700 Q760 560 960 420 Q1160 560 960 700" fill="none" stroke="#FFF3C4" stroke-width="5" stroke-dasharray="10 14" opacity="0.6"/>'
    c += "".join(honeybee(960 + 260 * math.cos(k * 1.2), 560 + 220 * math.sin(k * 1.2), 0.5, 0, rot=math.degrees(k * 1.2) + 180, flap=False, look=(-3, 0)) for k in range(6))
    c += honeybee(x, y, 0.75, fr, rot=rot)
    c += f'<g transform="translate(1560 260)"><circle r="70" fill="{MUSTARD}" {stroke(5)}/>' + "".join(f'<path d="M0 -90 L0 -110" transform="rotate({k * 45})" {stroke(6)}/>' for k in range(8)) + '</g>'
    c += f'<path d="M1500 340 L1220 520" stroke="{RED}" stroke-width="12" stroke-linecap="round" stroke-dasharray="20 14"/>'
    c += daisy(1250, 880, 1.2, t, 1) + daisy(1340, 900, 1.0, t, 2, col="#F6A6B8")
    return c, (1.0, 960, 540)


def s020(t, T, fr):
    c = f'<rect x="-600" y="-400" width="3200" height="1900" fill="#E8D4B0"/><rect x="420" y="80" width="1080" height="640" fill="#A9CFE0" {stroke()}/>'
    c += clouds(t, 220, seed=20, n=2) + f'<path d="M420 600 Q700 480 960 560 Q1200 470 1500 580 L1500 720 L420 720 Z" fill="#8FB27A" {stroke(5)}/>'
    c += f'<path d="M960 80 L960 720 M420 400 L1500 400" {stroke(10)}/><rect x="380" y="720" width="1160" height="40" fill="#F6F0E2" {stroke(5)}/>'
    c += honey_jar(960, 700, 1.6, fill=ease(seg(t, 0.1 * T, 0.95 * T)))
    for k in range(10):
        p = seg(t, 0.1 * T + k * 0.07 * T, 0.18 * T + k * 0.07 * T)
        if p > 0:
            x, y = 560 + (k % 5) * 50 + (k // 5) * 760, 640 - (k % 3) * 40
            c += f'<g transform="translate({x} {y}) scale({ease_out_back(p):.2f}) translate({-x} {-y})">' + daisy(x, y + 60, 0.45, t, k, col=["#FFFFFF", "#F6A6B8", "#C9B6E4"][k % 3]) + '</g>'
    c += honeybee(1240 + 40 * math.sin(t * 2), 520 + 20 * math.sin(t * 3), 0.5, fr, flip=True)
    return c, cam_push(t, T, 1.0, 1.05, 960, 520)


def s021(t, T, fr):
    c = bg_paper2(t)
    c += (f'<path d="M140 300 Q500 160 900 260 Q1300 160 1760 300 Q1840 620 1700 860 Q1200 980 900 880 Q500 980 200 860 Q80 600 140 300 Z" fill="#D6E2C0" {stroke(6)}/>')
    n = int(lerp(1, 70, ease(seg(t, 0.15 * T, 0.9 * T))))
    r = rnd(21)
    for k in range(n):
        x, y = r.uniform(240, 1680), r.uniform(330, 840)
        kind = k % 4
        c += (honeybee(x, y, 0.22, 0, flap=False) if kind == 0 else bumblebee(x, y, 0.2, 0) if kind == 1 else
              solitary_bee(x, y, 0.32, 0, ["#4A5A78", "#3E7A4A", "#8A6A4E", "#5E4E8A"][k % 4]))
    c += hive_box(960, 620, 0.35, MUSTARD)
    return c, cam_push(t, T, 1.6, 1.0, 960, 600)


# ---------------- HOW POLLINATION WORKS ----------------
def s022(t, T, fr):
    lean = 8 * math.sin(t * 1.8)
    c = bg_meadow2(t, seed=22)
    c += f'<path d="M760 1200 Q900 800 960 640 Q1020 800 1160 1200 Z" fill="#D9C49A" {stroke(5)}/>'
    c += f'<g transform="rotate({8 + lean:.1f} 420 1060)">' + daisy(420, 1060, 3.0, 0, 0, col="#F6A6B8", stem=130) + '</g>'
    c += f'<g transform="rotate({-8 - lean:.1f} 1500 1060)">' + daisy(1500, 1060, 3.0, 0, 1, col="#C9B6E4", stem=130) + '</g>'
    return c, (1.0, 960, 560)


def s023(t, T, fr):
    c = bg_paper2(t)
    c += daisy(500, 900, 3.0, t * 0.4, 0, col="#F6A6B8", stem=150) + daisy(1420, 900, 3.0, t * 0.4, 1, col="#F6A6B8", stem=150)
    p = seg(t, 0.15 * T, 0.6 * T)
    pts = [(lerp(500, 1420, v), 450 - 260 * math.sin(v * math.pi)) for v in [i / 30 for i in range(31)]]
    d = "M" + " L".join(f"{x:.0f} {y:.0f}" for x, y in pts)
    c += f'<path d="{d}" fill="none" stroke="#B5A88E" stroke-width="6" stroke-dasharray="14 14"/>'
    for k in range(6):
        v = clamp(p * 1.2 - k * 0.04)
        if 0 < v < 1:
            x, y = lerp(500, 1420, v), 450 - 260 * math.sin(v * math.pi)
            c += f'<circle cx="{x:.0f}" cy="{y + (k % 3) * 10:.0f}" r="12" fill="{MUSTARD}" {stroke(3)}/>'
    g = ease_out_back(seg(t, 0.6 * T, 0.9 * T))
    if g > 0:
        c += f'<g transform="translate(1420 520) scale({g:.2f})">' + apple(0, 0, 1.6, "#E0533A") + '</g>'
    return c, (1.0, 960, 560)


def s024(t, T, fr):
    c = f'<rect x="-600" y="-400" width="3200" height="1900" fill="#F3E6C4"/>' + "".join(f'<path d="M{x} -400 L{x} 1500" stroke="#EAD8A8" stroke-width="30"/>' for x in range(-600, 2600, 120))
    c += f'<rect x="-600" y="760" width="3200" height="80" fill="#B98B5E" {stroke()}/><rect x="-600" y="840" width="3200" height="700" fill="#8A6A4E" {stroke()}/>'
    c += sunflower(760, 780, 2.2, t * 0.3, 0)
    drip = ease(seg(t, 0.2 * T, 0.6 * T))
    c += f'<path d="M{900} {360 + 180 * drip:.0f} q-20 30 0 50 q20 -20 0 -50 Z" fill="#F2C24A" {stroke(4)}/>' if drip < 1 else f'<ellipse cx="900" cy="560" rx="40" ry="16" fill="#F2C24A" {stroke(4)}/>'
    c += f'<g transform="translate(640 640)">' + "".join(f'<circle cx="{dx}" cy="{dy}" r="14" fill="#FFD25A" {stroke(3)}/>' for dx, dy in [(0, 0), (22, 8), (10, -18), (-18, 10)]) + '</g>'
    c += honeybee(1260, 500 + 10 * math.sin(t * 3), 1.3, fr, flip=True, look=(-4, 2), mouth="o" if drip > 0.5 else "smile")
    return c, cam_push(t, T, 1.0, 1.06, 1000, 520)


def s025(t, T, fr):
    c = sky("#F7D9A0", "#F3E6C4", "s25") + sunflower(960, 1700, 6.0, 0, 0)
    c += honeybee(960, 420, 3.2, fr, baskets=True, look=(2, 3))
    r = rnd(25)
    n = int(40 * ease(seg(t, 0.1 * T, 0.7 * T)))
    for k in range(n):
        a, d = r.uniform(0, 6.28), r.uniform(20, 150)
        c += f'<circle cx="{960 - 30 + d * 1.6 * math.cos(a):.0f}" cy="{430 + d * math.sin(a):.0f}" r="7" fill="#FFD25A" {stroke(2)}/>'
    c += sparkle(1250, 260, seg(t, 0.6 * T, T), 40, "#FFF3C4")
    return c, cam_push(t, T, 1.0, 1.06, 960, 480)


def s026(t, T, fr):
    g = 0.5 + 0.5 * math.sin(t * 3)
    left = f'<rect x="-600" y="-400" width="1560" height="1900" fill="#A9CFE0"/>' + sunflower(480, 1500, 4.0, 0, 0)
    right = (f'<rect x="960" y="-400" width="1700" height="1900" fill="#2E2A5E"/>'
             f'<g transform="translate(1440 620)">' + "".join(f'<ellipse cx="0" cy="-120" rx="34" ry="90" transform="rotate({k * 22.5})" fill="#B8A8F0" {stroke(4)}/>' for k in range(16)) +
             f'<circle r="{160 + 10 * g:.0f}" fill="#5E4E8A" opacity="0.8"/><circle r="100" fill="#F6F0E2" opacity="{0.6 + 0.3 * g:.2f}"/><circle r="60" fill="#3E2A6E" {stroke(4)}/>'
             + "".join(f'<path d="M0 0 L{200 * math.cos(math.radians(k * 45)):.0f} {200 * math.sin(math.radians(k * 45)):.0f}" stroke="#F6F0E2" stroke-width="8" opacity="{0.3 + 0.4 * g:.2f}"/>' for k in range(8)) + '</g>')
    c = left + right + f'<path d="M960 -400 L960 1500" stroke="{CREAM}" stroke-width="20"/><path d="M960 -400 L960 1500" {stroke(5)}/>'
    c += honeybee(1700, 300, 0.6, fr, flip=True, look=(-4, 4))
    c += text(480, 150, "HUMAN VIEW", 70, CREAM, outline=INK) + text(1440, 150, "BEE VIEW (UV)", 70, MUSTARD, outline=INK)
    return c, (1.0, 960, 560)


def s027(t, T, fr):
    c = bg_paper2(t)
    for k in range(10):
        on = seg(t, 0.15 * T + k * 0.06 * T, 0.22 * T + k * 0.06 * T) if k < 9 else 0
        x = 200 + k * 170
        c += f'<circle cx="{x}" cy="600" r="{75 * on:.0f}" fill="url(#glow)"/>'
        col = MUSTARD if on > 0.5 else "#D8D0BE"
        c += daisy(x, 760, 1.4, t * 0.4, k, col=col, center="#F6F0E2" if on > 0.5 else "#B8B0A0", stem=120)
    c += f'<g transform="translate(1730 520)">' + honeybee(0, 0, 0.5, fr, look=(-4, 2), flip=True) + '</g>' if t > 0.8 * T else ""
    return c, (1.0, 960, 560)


def s028(t, T, fr):
    c = f'<rect x="-600" y="-400" width="3200" height="1900" fill="#3E4A5E"/><rect x="-600" y="820" width="3200" height="800" fill="#8A5A35" {stroke()}/>'
    c += "".join(f'<circle cx="{x}" cy="300" r="320" fill="url(#glow)" opacity="0.35"/>' for x in (300, 960, 1620))
    c += f'<path d="M-600 -400 Q-300 300 -100 820 L-600 820 Z M2600 -400 Q2300 300 2100 820 L2600 820 Z" fill="#B5543F" {stroke()}/>'
    cast = [lambda x, y: butterfly(x, y, 0.6, fr), lambda x, y: moth(x, y, 0.55, fr), lambda x, y: hoverfly(x, y, 1.0, fr),
            lambda x, y: beetle(x, y, 0.9), lambda x, y: hummingbird(x, y, 0.9, fr), lambda x, y: bat(x, y, 0.9, fr)]
    slide = ease(seg(t, 0.45 * T, 0.85 * T))
    for k, f in enumerate(cast):
        x = lerp(200 + k * 300, 120 + k * 150, slide)
        c += f'<g transform="translate({x:.0f} 660) scale({lerp(1, 0.6, slide):.2f}) translate({-x:.0f} -660)">' + f(x, 660) + '</g>'
    if slide > 0:
        r = rnd(28)
        for k in range(40):
            bx = lerp(2400, 1100, slide) + r.uniform(0, 900)
            by = r.uniform(300, 780)
            c += honeybee(bx, by + 10 * math.sin(t * 4 + k), 0.3, fr + k, flip=True)
    return c, (1.0, 960, 560)


# ---------------- 100 MILLION YEARS ----------------
def fern(x, y, s=1.0, t=0.0, i=0, col="#3E6E4A"):
    sw = 3 * math.sin(t + i)
    leaves = "".join(f'<path d="M0 {-k * 30} q{side * 50} -10 {side * 70} -30" fill="none" stroke="{col}" stroke-width="10" stroke-linecap="round"/>' for k in range(1, 9) for side in (-1, 1))
    return f'<g transform="translate({x:.0f} {y:.0f}) rotate({sw:.1f}) scale({s:.2f})"><path d="M0 0 Q10 -150 -10 -280" fill="none" stroke="{col}" stroke-width="10"/>{leaves}</g>'


def magnolia(x, y, s=1.0, col="#F6E0E6"):
    return (f'<g transform="translate({x:.0f} {y:.0f}) scale({s:.2f})"><path d="M0 0 L0 120" stroke="#6B4A35" stroke-width="10"/>'
            + "".join(f'<path d="M0 0 Q{-40 + k * 20} -80 {-10 + k * 10} -120 Q{10 + k * 5} -60 0 0 Z" fill="{col}" {stroke(4)}/>' for k in range(5)) + '</g>')


def s029(t, T, fr):
    c = sky("#8E6A9A", "#F2A76B", "pre2") + f'<circle cx="1500" cy="520" r="110" fill="#F7D488" {stroke(5)}/>' + sun_rays(1500, 520, t, op=0.12)
    c += f'<path d="M-600 640 Q600 560 2600 650 L2600 1600 L-600 1600 Z" fill="#5E6E4E" {stroke()}/>'
    c += dinosaur(lerp(1700, 1200, t / T), 680, 0.6, "#3A3550", t * 3)
    c += "".join(fern(x, 1000 + (i % 2) * 30, 1.2 + (i % 3) * 0.2, t, i) for i, x in enumerate(range(-100, 2100, 230)))
    c += f'<path d="M-600 960 Q900 900 2600 980 L2600 1600 L-600 1600 Z" fill="#4D5E3E" {stroke()}/>'
    c += magnolia(600, 900, 1.2) + magnolia(1320, 920, 1.0, "#F2E6C0")
    return c, cam_pan(t, T, 880, 1060, 1.0)


def s030(t, T, fr):
    c = bg_paper2(t)
    m = ease(seg(t, 0.3 * T, 0.75 * T))
    c += f'<g opacity="{1 - 0.5 * m:.2f}">' + wasp(520, 520, 1.8, fr) + f'<path d="M560 600 q60 30 120 0 q-30 40 -120 0 Z" fill="#7FA65A" {stroke(4)}/></g>'
    c += f'<path d="M820 520 L{820 + 260 * m:.0f} 520" stroke="{RED}" stroke-width="16" stroke-linecap="round"/>' + (f'<path d="M1080 480 L1120 520 L1080 560" fill="none" stroke="{RED}" stroke-width="16" stroke-linecap="round"/>' if m > 0.95 else "")
    c += f'<g opacity="{m:.2f}">' + honeybee(1420, 520, 1.6, fr, baskets=True) + '</g>'
    return c, (1.0, 960, 560)


def s031(t, T, fr):
    c = bg_paper2(t, "#EFE6D0")
    p = seg(t, 0.05 * T, 0.85 * T)
    pts = []
    N = 120
    for k in range(int(N * p) + 1):
        a = k / N * 4 * math.pi
        r_ = 40 + k * 3.4
        pts.append((960 + r_ * math.cos(a), 580 + r_ * 0.78 * math.sin(a)))
    if len(pts) > 1:
        c += f'<path d="M{" L".join(f"{x:.0f} {y:.0f}" for x, y in pts)}" fill="none" stroke="#B5A88E" stroke-width="10" stroke-linecap="round"/>'
    for j in range(8):
        k = int((j + 1) * N / 8) - 1
        if k < len(pts):
            x, y = pts[k]
            s = 0.4 + j * 0.12
            c += daisy(x, y + 40 * s, s, t * 0.4, j, col=["#F6F0E2", "#F6A6B8", "#C9B6E4", MUSTARD, "#E0533A", "#9DB8D6", "#F6A6B8", MUSTARD][j], stem=60)
            if j % 2:
                c += honeybee(x + 50, y - 70 * s, 0.2 + j * 0.05, fr + j, flap=True)
    return c, cam_push(t, T, 1.1, 1.0, 960, 580)


def s032(t, T, fr):
    c = sky("#A9CFE0", "#F3E6C4", "fx") + f'<path d="M-600 900 Q900 820 2600 900 L2600 1600 L-600 1600 Z" fill="#7FA65A" {stroke()}/>'
    c += f'<path d="M960 1200 L960 100" stroke="#4E7F3A" stroke-width="16"/>'
    for k in range(5):
        y = 220 + k * 150
        c += (f'<g transform="translate({960 + (-1) ** k * 40} {y}) rotate({(-1) ** k * 20})"><path d="M0 0 Q-60 20 -90 100 Q0 130 90 100 Q60 20 0 0 Z" fill="#C97AB8" {stroke(5)}/>'
              f'<path d="M-60 90 Q0 150 60 90 Q0 110 -60 90 Z" fill="#E8B8DE" {stroke(4)}/>' + "".join(f'<circle cx="{dx}" cy="{70 + abs(dx) * 0.2:.0f}" r="5" fill="#7A3A6E"/>' for dx in (-30, -10, 10, 30)) + '</g>')
    land = ease(seg(t, 0.15 * T, 0.6 * T))
    c += honeybee(lerp(1600, 1010, land), lerp(200, 700, land), 0.7, fr if land < 1 else 0, flip=True, flap=land < 1, rot=lerp(0, -15, land))
    return c, cam_push(t, T, 1.0, 1.12, 980, 680)


# ---------------- THE FIRST MORNING ----------------
def s033(t, T, fr):
    c = bg_cottage_garden(t, "day", insects=False)
    px = lerp(560, 900, ease(t / T))
    c += pp(px, 1060, 1.0, t, T, arms=(20 + 10 * math.sin(t * 6), 20 - 10 * math.sin(t * 6)), bob=5 * abs(math.sin(t * 6)), mouth="flat", look=(6, -2))
    return c, cam_push(t, T, 1.0, 1.05, 900, 640)


def s034(t, T, fr):
    c = sky("#A9CFE0", "#F3E6C4", "park") + clouds(t, 150, seed=34, n=5)
    c += f'<path d="M-600 600 Q900 520 2600 620 L2600 1600 L-600 1600 Z" fill="#8FB27A" {stroke()}/>'
    c += "".join(tree(x, 640 + (i % 2) * 20, 0.8, ["#6E9A5E", "#7FA65A", "#5E8E4A"][i % 3], t, i) for i, x in enumerate(range(-100, 2200, 260)))
    c += f'<ellipse cx="1400" cy="900" rx="320" ry="70" fill="#7FB4BE" {stroke()}/>'
    c += f'<path d="M-600 980 Q900 900 2600 1000 L2600 1080 Q900 980 -600 1060 Z" fill="#D9C49A" {stroke(5)}/>'
    c += f'<g transform="translate(400 900)"><rect x="-120" y="-30" width="240" height="20" fill="#8A5A35" {stroke(4)}/><path d="M-100 -10 L-100 40 M100 -10 L100 40" {stroke(6)}/></g>'
    jx = lerp(-200, 2100, t / T)
    c += person(jx, 1030, 0.9, skin="#8D5A3B", outfit="shirt", outfit_color="#D96C8A", arms=(40 + 30 * math.sin(t * 10), 40 - 30 * math.sin(t * 10)),
                mouth="smile", eyes="open", hair_style="bun", hair_color="#1F1A17", bob=-12 * abs(math.sin(t * 10)))
    c += grass_tufts(-200, 2200, 1080, n=50, t=t)
    return c, cam_pan(t, T, 880, 1040, 1.0)


def s035(t, T, fr):
    c = sky("#A9CFE0", "#F7E6C0", "wh") + clouds(t * 3, 160, seed=35, n=4, speed=40)
    c += f'<path d="M-600 560 Q900 500 2600 570 L2600 1600 L-600 1600 Z" fill="#E6C27A" {stroke()}/>'
    for j in range(7):
        y = 600 + j * 80
        for i in range(-2, 26):
            x = i * 90 + (j % 2) * 45
            sw = 10 * math.sin(t * 3 + i * 0.4 + j)
            s = 0.5 + j * 0.12
            c += (f'<g transform="translate({x} {y}) rotate({sw:.1f}) scale({s:.2f})"><path d="M0 0 L0 -120" stroke="#C9A04A" stroke-width="6"/>'
                  f'<ellipse cx="0" cy="-140" rx="12" ry="34" fill="#E6B84A" {stroke(3)}/></g>')
    for k in range(10):
        u = ((t * 0.5 + k / 10) % 1)
        y = 300 + k * 50
        c += f'<path d="M{-300 + u * 2600:.0f} {y} q60 -20 120 0 t120 0" fill="none" stroke="#FFFFFF" stroke-width="6" stroke-linecap="round" opacity="0.7"/>'
        c += "".join(f'<circle cx="{-260 + u * 2600 + d * 30:.0f}" cy="{y + 20 + 6 * math.sin(d + t * 4):.0f}" r="5" fill="#F6E39A"/>' for d in range(5))
    return c, cam_pan(t, T, 860, 1060, 1.0)


SCENES = {i: globals()[f"s{i:03d}"] for i in range(1, 36)}
KEYFRAME.update({i: 0.6 for i in SCENES})
KEYFRAME.update({2: 0.2, 7: 0.7, 6: 0.85, 10: 0.8, 16: 0.35, 28: 0.75})

try:
    import scenes_bees2 as _b2
    SCENES.update(_b2.SCENES); KEYFRAME.update({k: 0.6 for k in _b2.SCENES}); KEYFRAME.update(getattr(_b2, "KEYFRAME", {}))
except ModuleNotFoundError as e:
    if e.name != "scenes_bees2":
        raise
try:
    import scenes_bees3 as _b3
    SCENES.update(_b3.SCENES); KEYFRAME.update({k: 0.6 for k in _b3.SCENES}); KEYFRAME.update(getattr(_b3, "KEYFRAME", {}))
except ModuleNotFoundError as e:
    if e.name != "scenes_bees3":
        raise
