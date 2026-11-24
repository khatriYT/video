"""Episode 2 scenes 036-070."""
import math
from draw import *
from draw2 import stroke, text, sky, tree, bat, moth, beetle, hoverfly, spider, web, question_mark, auto_eyes, check, calendar, person_icon
from draw3 import *
from scenes_bees import magnolia, fern, clock_icon, pollen_trail

KEYFRAME = {}


def table_scene(t):
    c = bg_kitchen(t)
    c += f'<path d="M-600 780 L2600 780 L2600 1600 L-600 1600 Z" fill="#B98B5E" {stroke()}/>' + "".join(f'<path d="M-600 {y} L2600 {y}" stroke="#A67A50" stroke-width="4"/>' for y in (860, 960, 1060))
    return c


def s036(t, T, fr):
    c = table_scene(t)
    c += rice_bowl(500, 880, 2.2) + bread(960, 860, 2.0) + corn(1400, 830, 1.6, 20) + corn(1500, 850, 1.6, 40)
    frac = 0.5 * ease(seg(t, 0.15 * T, 0.6 * T))
    c += pie_chart(1640, 330, 120, frac, MUSTARD, "#F6F0E2")
    return c, cam_push(t, T, 1.0, 1.05, 960, 640)


def s037(t, T, fr):
    c = sky("#A9CFE0", "#F3E6C4", "sm") + clouds(t, 140, seed=37, n=4)
    c += f'<rect x="-600" y="860" width="3200" height="700" fill="#9C9A94" {stroke()}/>' + "".join(f'<path d="M{x} 900 L{x + 60} 900" stroke="#F6F0E2" stroke-width="10"/>' for x in range(-600, 2600, 200))
    c += f'<rect x="200" y="300" width="1520" height="560" fill="#F0E0C0" {stroke()}/><path d="M160 300 L1760 300 L1700 220 L220 220 Z" fill="#6E9A5E" {stroke()}/>'
    c += f'<rect x="600" y="230" width="720" height="110" rx="14" fill="#FFF6E0" {stroke(5)}/>' + text(960, 310, "MARKET", 84, "#6E9A5E")
    op = ease(seg(t, 0.15 * T, 0.5 * T))
    c += f'<rect x="760" y="520" width="400" height="340" fill="#BFD9D6" {stroke()}/>'
    c += f'<rect x="{760 - 200 * op:.0f}" y="520" width="200" height="340" fill="#DCEEF0" fill-opacity="0.85" {stroke(5)}/><rect x="{960 + 200 * op:.0f}" y="520" width="200" height="340" fill="#DCEEF0" fill-opacity="0.85" {stroke(5)}/>'
    for x in (300, 1420):
        c += f'<rect x="{x}" y="440" width="260" height="300" fill="#BFD9D6" {stroke(5)}/>' + "".join(apple(x + 50 + k * 60, 700, 0.6, ["#E0533A", MUSTARD, "#7FA65A"][k % 3]) for k in range(3))
    px = lerp(400, 820, ease(seg(t, 0.2 * T, 0.95 * T)))
    cart = f'<g transform="translate({px + 130:.0f} 1010)"><path d="M-80 -110 L90 -110 L70 -20 L-60 -20 Z" fill="#C9C6C0" fill-opacity="0.6" {stroke(5)}/><path d="M-110 -150 L-80 -110" {stroke(6)}/><circle cx="-50" cy="0" r="16" fill="{INK}"/><circle cx="60" cy="0" r="16" fill="{INK}"/></g>'
    c += pp(px, 1020, 0.95, t, T, arms=(70, 70), bob=4 * abs(math.sin(t * 6))) + cart
    return c, cam_push(t, T, 1.0, 1.08, 960, 600)


def s038(t, T, fr):
    c = bg_supermarket(t)
    s = lerp(0.7, 0.85, ease(t / T))
    c += pp(960, 1160, s, t, T, arms=(70, 70), look=(0, -4), bob=4 * abs(math.sin(t * 6)))
    return c, cam_push(t, T, 1.0, 1.06, 960, 560)


def s039(t, T, fr):
    c = f'<rect x="-600" y="-400" width="3200" height="1900" fill="#E9DCC0"/>' + "".join(f'<path d="M{x} -400 L{x} 1500" stroke="#DCCDAA" stroke-width="40"/>' for x in range(-600, 2600, 160))
    items = [("APPLES", lambda x, y: apple(x, y, 1.6)), ("CHERRIES", lambda x, y: cherry(x, y, 1.6)), ("BLUEBERRIES", lambda x, y: blueberry(x, y, 1.6)),
             ("STRAWBERRIES", lambda x, y: strawberry(x, y, 1.6)), ("ALMONDS", lambda x, y: almond(x - 20, y, 1.4, -10) + almond(x + 24, y + 6, 1.4, 14)),
             ("AVOCADOS", lambda x, y: avocado(x, y, 1.5)), ("MELONS", lambda x, y: melon(x, y, 1.4)), ("PUMPKINS", lambda x, y: pumpkin(x, y, 1.4)), ("COFFEE", lambda x, y: coffee(x, y, 1.4))]
    n = len(items)
    for k, (name, f) in enumerate(items):
        p = seg(t, 0.03 * T + k * (0.85 * T / n), 0.03 * T + k * (0.85 * T / n) + 0.3)
        if p <= 0:
            continue
        x, y = 360 + (k % 5) * 300, 330 + (k // 5) * 420
        if k >= 5:
            x += 150
        kk = ease_out_back(p)
        c += f'<g transform="translate({x} {y}) scale({kk:.2f}) translate({-x} {-y})"><circle cx="{x}" cy="{y}" r="120" fill="#FFF6E0" {stroke(6)}/>{f(x, y)}</g>'
        c += f'<g opacity="{p:.2f}">' + text(x, y + 170, name, 30, CREAM, outline=INK) + '</g>'
    return c, (1.0, 960, 560)


def s040(t, T, fr):
    c = bg_paper2(t)
    frac = 0.35 * ease(seg(t, 0.1 * T, 0.5 * T))
    c += pie_chart(960, 600, 330, frac, "#E0533A", "#E6D2A0")
    r = rnd(40)
    for k in range(14):
        a = r.uniform(0.05, 0.3) * 2 * math.pi; d = r.uniform(90, 280)
        if frac > 0.3:
            c += [apple, strawberry, cherry, blueberry][k % 4](960 + d * math.sin(a), 600 - d * math.cos(a), 0.5)
    for k in range(14):
        a = r.uniform(0.4, 0.95) * 2 * math.pi; d = r.uniform(90, 280)
        c += [lambda x, y, s: bread(x, y, s * 0.6), lambda x, y, s: rice_bowl(x, y, s * 0.6), lambda x, y, s: corn(x, y, s * 0.5), potato][k % 4](960 + d * math.sin(a), 600 - d * math.cos(a), 0.7)
    return c, (1.0, 960, 560)


def s041(t, T, fr):
    return bg_supermarket(t, fade=ease(seg(t, 0.1 * T, 0.85 * T))), cam_push(t, T, 1.0, 1.04, 960, 560)


def s042(t, T, fr):
    c = f'<rect x="-600" y="-400" width="3200" height="1900" fill="#EDE9E0"/><rect x="-600" y="640" width="3200" height="60" fill="#B98B5E" {stroke()}/><rect x="-600" y="700" width="3200" height="900" fill="#D9D3C4" {stroke()}/>'
    c += apple(620, 560, 2.6) + "".join(almond(1180 + k * 60, 600, 1.0, k * 20) for k in range(3))
    spin = 1 - ease(seg(t, 0.1 * T, 0.6 * T))
    c += price_tag(620, 760, "$12", 1.8, 360 * spin * 2) + price_tag(1240, 760, "$40", 1.8, -360 * spin * 2)
    c += sparkle(760, 380, seg(t, 0.6 * T, T), 40)
    return c, cam_push(t, T, 1.0, 1.06, 900, 600)


def cacao_pod(x, y, s=1.0):
    ridges = "".join(f'<path d="M{dx} -70 Q{dx * 1.4:.0f} 0 {dx} 70" fill="none" stroke="#8A4A1E" stroke-width="5"/>' for dx in (-24, 0, 24))
    return f'<g transform="translate({x} {y}) scale({s})"><ellipse rx="50" ry="90" fill="#C9772E" {stroke(5)}/>{ridges}<path d="M0 -90 L0 -120" {stroke(8)}/></g>'


def s043(t, T, fr):
    c = sky("#9CC5A1", "#DCE6C8", "cac") + "".join(tree(x, 1200, 1.6, "#3E7A4A", t, x) for x in range(-200, 2300, 330))
    c += f'<path d="M700 1100 L760 200" stroke="#6B4A35" stroke-width="60"/><path d="M700 1100 L760 200" fill="none" {stroke(4)}/>'
    c += cacao_pod(860, 560, 1.4) + cacao_pod(660, 760, 1.2)
    c += (f'<g transform="translate(1300 760) rotate(-8)"><rect x="-200" y="-110" width="400" height="220" rx="10" fill="#5A3A28" {stroke()}/>'
          + "".join(f'<rect x="{-180 + i * 92}" y="{-90 + j * 100}" width="80" height="80" rx="6" fill="#6B4A35" {stroke(3)}/>' for i in range(4) for j in range(2)) + '</g>')
    wave = 20 * math.sin(t * 8)
    c += midge(1300, 440, 2.4, fr) + f'<path d="M1350 420 l{20 + wave * 0.5:.0f} -40" stroke="{INK}" stroke-width="4" stroke-linecap="round"/>'
    c += f'<g transform="translate(1660 220)"><circle r="80" fill="#2E3A57" {stroke(5)}/>{mosquito(0, 6, 0.7, frame=fr)}</g>' + text(1660, 340, "EP. 1", 30, CREAM, outline=INK)
    return c, cam_push(t, T, 1.0, 1.05, 1000, 560)


def s044(t, T, fr):
    c = f'<rect x="-600" y="-400" width="3200" height="1900" fill="#EDE9E0"/>'
    for j, y in enumerate((300, 600, 900)):
        c += f'<rect x="-600" y="{y}" width="3200" height="30" fill="#B98B5E" {stroke(5)}/>'
    g = 0.4 + 0.3 * math.sin(t * 3)
    for k in range(9):
        x = 140 + k * 210
        c += bread(x, 260, 1.2)
        c += f'<g transform="translate({x} 560)"><path d="M-70 40 L-60 -60 Q0 -80 60 -60 L70 40 Z" fill="#F0E0C0" {stroke(5)}/>' + text(0, 10, "RICE", 30, "#8A5A35") + '</g>'
        c += f'<g transform="translate({x} 860)"><rect x="-60" y="-110" width="120" height="110" fill="{["#E0533A", "#5B8DB8", MUSTARD][k % 3]}" {stroke(5)}/>' + text(0, -45, "PASTA", 26, "#FFF6E0") + '</g>'
    c += "".join(potato(x, 1020, 1.2) for x in range(100, 1900, 120))
    c += f'<rect x="-600" y="-400" width="3200" height="1900" fill="#FFF3C4" opacity="{0.12 * g:.2f}"/>'
    return c, cam_pan(t, T, 880, 1040, 1.0)


def beige_plate(x, y, s=1.0, color_amt=0.0):
    out = f'<g transform="translate({x} {y}) scale({s})"><ellipse rx="300" ry="110" fill="#F6F4EE" {stroke(6)}/><ellipse rx="230" ry="80" fill="none" stroke="#E2DCCE" stroke-width="5"/>'
    out += f'<ellipse cx="-80" cy="-10" rx="90" ry="40" fill="#E6D2A0" {stroke(4)}/><ellipse cx="80" cy="0" rx="80" ry="34" fill="#D8C49A" {stroke(4)}/>' + bread(0, -30, 0.8)
    if color_amt > 0:
        out += f'<g opacity="{color_amt:.2f}">' + apple(-150, -40, 0.7) + strawberry(140, -40, 0.7) + blueberry(60, 30, 0.6) + avocado(-60, 30, 0.6) + '</g>'
    return out + '</g>'


def s045(t, T, fr):
    c = table_scene(t)
    poke = 10 * math.sin(t * 4) if t > 0.3 * T else 0
    c += pp(960, 1100, 1.4, t, T, arms=(40, 70 + poke), mouth="frown", eyes="blink" if blinking(t, [0.5 * T]) else "annoyed", hat="bucket", legs=False)
    c += beige_plate(960, 900, 1.2)
    return c, cam_push(t, T, 1.0, 1.08, 960, 640)


def badge(x, y, label, col):
    return f'<g transform="translate({x:.0f} {y:.0f})"><circle r="34" fill="{col}" {stroke(4)}/>' + text(0, 12, label, 30, "#FFF6E0") + '</g>'


def s046(t, T, fr):
    c = table_scene(t)
    foods = [(380, 820, lambda x, y: apple(x, y, 1.8)), (720, 840, lambda x, y: avocado(x, y, 1.6)), (1060, 830, lambda x, y: strawberry(x, y, 1.8)), (1340, 850, lambda x, y: almond(x, y, 1.8))]
    labs = [("A", "#E0533A"), ("B9", "#7FA65A"), ("C", MUSTARD), ("E", "#5B8DB8")]
    for k, (x, y, f) in enumerate(foods):
        c += f(x, y)
        a = t * 2 + k
        c += badge(x + 120 * math.cos(a), y - 60 + 50 * math.sin(a), *labs[k])
        c += sparkle(x + 60, y - 120, (t * 0.7 + k * 0.25) % 1, 22, "#FFF3C4")
    return c, cam_pan(t, T, 820, 1000, 1.0)


def s047(t, T, fr):
    c = bg_lab3(t)
    lines = int(t * 6) % 5
    scr = "".join(f'<rect x="-104" y="{-160 + k * 24}" width="{120 + 60 * ((k * 7) % 3)}" height="10" fill="#5B8DB8"/>' for k in range(lines + 1))
    c += laptop(1080, 640, 1.6, scr)
    c += person(1580, 1000, 1.2, skin="#8D5A3B", outfit="coat", outfit_color="#F4F4F0", arms=(15, 60 + 10 * math.sin(t * 12)), hair_style="bun", hair_color="#1F1A17", mouth="flat", eyes=auto_eyes(t, T), flip=True, look=(-6, 4))
    return c, cam_push(t, T, 1.0, 1.05, 1100, 560)


CONT = [  # simplified world map blobs
    "M200 260 Q320 180 460 220 Q520 300 470 380 Q420 420 380 520 Q320 560 300 480 Q240 420 200 360 Z",
    "M430 560 Q500 540 520 620 Q530 720 470 820 Q430 840 420 760 Q400 660 430 560 Z",
    "M820 230 Q900 200 980 240 Q960 300 900 320 Q840 300 820 230 Z",
    "M860 360 Q980 340 1020 420 Q1040 560 960 680 Q900 700 880 600 Q840 480 860 360 Z",
    "M1000 220 Q1250 160 1480 230 Q1560 320 1440 380 Q1300 420 1180 380 Q1060 340 1000 220 Z",
    "M1440 620 Q1540 600 1580 660 Q1560 720 1470 720 Q1420 680 1440 620 Z",
]


def world_map(t, op=1.0):
    c = f'<rect x="-600" y="-400" width="3200" height="1900" fill="#3E6E86"/>' + "".join(f'<path d="M{x} {y} q40 -10 80 0" stroke="#5A88A0" stroke-width="5" fill="none"/>' for x in range(0, 1900, 200) for y in range(80, 1080, 160))
    c += f'<g transform="translate(-120 40) scale(1.15)">' + "".join(f'<path d="{d}" fill="#D9C49A" {stroke(6)}/>' for d in CONT) + '</g>'
    return c


def s048(t, T, fr):
    c = world_map(t)
    r = rnd(48)
    fade = seg(t, 0.2 * T, 0.9 * T)
    for k in range(60):
        x, y = r.uniform(180, 1720), r.uniform(320, 900)
        th = r.random()
        op = 1.0 if th > 0.25 else 1 - seg(fade, th * 2, th * 2 + 0.3)
        c += person_icon(x, y, 0.55, "#F6F0E2", op)
    return c, cam_push(t, T, 1.0, 1.05, 960, 600)


def s049(t, T, fr):
    c = bg_paper2(t)
    dim = seg(t, 0.25 * T, 0.8 * T)
    c += (f'<g transform="translate(620 600)"><path d="M-240 0 Q0 -170 240 0 Q0 170 -240 0 Z" fill="#FFFFFF" {stroke(8)}/><circle r="90" fill="#5B8DB8" {stroke(6)}/>'
          f'<circle r="40" fill="{INK}"/><circle cx="-24" cy="-26" r="14" fill="#FFFFFF"/></g>')
    c += (f'<g transform="translate(1300 620)"><circle cx="0" cy="-60" r="110" fill="#F3D9C0" {stroke(7)}/><circle cx="-36" cy="-70" r="9" fill="{INK}"/><circle cx="36" cy="-70" r="9" fill="{INK}"/>'
          f'<path d="M-24 -20 Q0 0 24 -20" fill="none" {stroke(5)}/><path d="M-40 -170 q40 -30 70 0" fill="none" {stroke(5)}/>'
          f'<path d="M-150 220 Q-150 60 0 50 Q150 60 150 220 Z" fill="#F6E0A0" {stroke(7)}/></g>')
    c += f'<g opacity="{1 - 0.7 * dim:.2f}">' + badge(820, 420, "A", "#E0533A") + badge(1500, 420, "B9", "#7FA65A") + '</g>'
    c += f'<rect x="-600" y="-400" width="3200" height="1900" fill="#2E3A57" opacity="{0.25 * dim:.2f}"/>'
    return c, (1.0, 960, 560)


def s050(t, T, fr):
    c = bg_paper2(t)
    blocks = [("BEES", 520, "#F2B33D"), ("FLIES", 150, "#9CC5A1"), ("BEETLES", 90, "#8A6A4E"), ("BUTTERFLIES & MOTHS", 120, "#D96C8A"), ("BIRDS & BATS", 80, "#5B8DB8")]
    y = 880
    for k, (name, h, col) in enumerate(blocks):
        p = ease_out_bounce(seg(t, 0.08 * T + k * 0.1 * T, 0.2 * T + k * 0.1 * T))
        hh = h * 0.9
        yy = y - hh - (1 - p) * 500
        if p > 0:
            c += f'<rect x="660" y="{yy:.0f}" width="600" height="{hh:.0f}" fill="{col}" {stroke(6)}/>' + text(960, yy + hh / 2 + 14, name, 40 if h > 100 else 30, INK)
        y -= hh
    c += honeybee(1450, 700, 0.8, fr, flip=True, look=(-4, 0))
    return c, (1.0, 960, 520)


def s051(t, T, fr):
    c = f'<rect x="-600" y="-400" width="3200" height="1900" fill="#2E3A57"/><circle cx="960" cy="540" r="600" fill="url(#glow)" opacity="0.4"/>'
    c += hourglass(960, 560, 1.7, ease(seg(t, 0.05 * T, 0.95 * T)), t)
    return c, cam_push(t, T, 1.0, 1.08, 960, 560)


CALI = "M760 120 L1060 120 L1060 420 L1340 760 Q1380 840 1320 900 L1180 960 Q1100 900 1080 820 Q980 640 860 520 Q760 400 760 120 Z"


def s052(t, T, fr):
    c = f'<rect x="-600" y="-400" width="3200" height="1900" fill="#9FC8E6"/>' + "".join(f'<path d="M{x} {y} q40 -10 80 0" stroke="#BFD9E6" stroke-width="5" fill="none"/>' for x in range(0, 900, 200) for y in range(80, 1080, 160))
    c += f'<path d="M1060 -400 L2600 -400 L2600 1600 L1100 1600 L1180 960 L1320 900 Q1380 840 1340 760 L1060 420 Z" fill="#D9C49A" {stroke()}/>'
    c += f'<path d="{CALI}" fill="#E6D2A0" {stroke(8)}/><path d="M900 300 Q1000 520 1120 700" stroke="#9CB98A" stroke-width="90" stroke-linecap="round" opacity="0.8"/>'
    pin = ease_out_bounce(seg(t, 0.25 * T, 0.6 * T))
    c += f'<g transform="translate(1010 {lerp(100, 520, pin):.0f})"><path d="M0 0 Q-40 -50 -40 -80 A40 40 0 1 1 40 -80 Q40 -50 0 0 Z" fill="{RED}" {stroke(5)}/><circle cx="0" cy="-80" r="16" fill="#FFF6E0"/></g>'
    c += calendar(1600, 300, 1.2, "FEB")
    return c, cam_push(t, T, 1.0, 1.08, 1000, 520)


def s053(t, T, fr):
    return bg_orchard_rows(t), cam_pan(t, T, 880, 1040, 1.02)


def s054(t, T, fr):
    c = bg_highway(t)
    c += truck(lerp(-400, 900, ease(t / T)), 930, 1.1, t) + truck(lerp(-1400, 0, ease(t / T)), 860, 0.75, t, col="#5B8DB8")
    c += "".join(blossom_tree(x, 760, 0.6, t, i) for i, x in enumerate(range(1300, 2200, 220)))
    return c, (1.0, 960, 560)


def s055(t, T, fr):
    c = bg_orchard_rows(t, petals=True)
    cols = ["#F6F0E2", "#9DB8D6", MUSTARD, "#9CC5A1", "#D96C8A"]
    for k in range(5):
        c += hive_box(560 + k * 200, 1060, 0.55, cols[k])
    r = rnd(55)
    for k in range(36):
        u = seg(t, k * 0.012 * T, 0.6 * T + k * 0.008 * T)
        x0 = 560 + (k % 5) * 200
        x = x0 + (r.uniform(-700, 700)) * u
        y = 980 - 700 * u + 40 * math.sin(t * 4 + k)
        if u > 0:
            c += honeybee(x, y, 0.16 + 0.1 * (1 - u), fr + k, flip=x < x0)
    c += beekeeper(1600, 1080, 1.0, t, T, arms=(20, 40))
    return c, cam_push(t, T, 1.08, 1.0, 960, 640)


USA = "M180 300 L520 260 L900 280 L1300 260 L1560 220 L1720 300 L1680 420 L1580 520 L1560 640 L1440 760 L1300 800 L1200 900 L1100 820 L900 820 L700 860 L560 800 L420 700 L260 660 L200 520 Z"


def s056(t, T, fr):
    c = f'<rect x="-600" y="-400" width="3200" height="1900" fill="#9FC8E6"/>' + f'<path d="{USA}" fill="#E6D2A0" {stroke(8)}/>'
    c += f'<path d="M200 520 L260 660 L420 700 L380 560 L300 300 Z" fill="#D9C49A" {stroke(5)}/>'
    routes = [[(320, 560), (360, 380), (300, 310)], [(320, 560), (800, 460), (1300, 360), (1560, 300)], [(320, 560), (900, 600), (1400, 520), (1600, 420)]]
    p = seg(t, 0.15 * T, 0.85 * T)
    for k, rt in enumerate(routes):
        pts = []
        for i in range(len(rt) - 1):
            for j in range(21):
                v = j / 20
                pts.append((lerp(rt[i][0], rt[i + 1][0], v), lerp(rt[i][1], rt[i + 1][1], v)))
        n = max(2, int(len(pts) * clamp(p * 1.3 - k * 0.15)))
        c += f'<path d="M{" L".join(f"{x:.0f} {y:.0f}" for x, y in pts[:n])}" fill="none" stroke="{RED}" stroke-width="10" stroke-dasharray="20 14" stroke-linecap="round"/>'
        if n >= len(pts) - 1:
            ex, ey = rt[-1]
            c += f'<g transform="translate({ex} {ey})">' + apple(0, 0, 0.6) + '</g>' if k == 1 else f'<g transform="translate({ex} {ey})">' + (cherry(0, 0, 0.7) if k == 0 else blueberry(0, 0, 0.8)) + '</g>'
        u = clamp(p * 1.3 - k * 0.15)
        i = min(len(pts) - 1, int(len(pts) * u))
        c += truck(pts[i][0], pts[i][1], 0.18, t)
    c += f'<g transform="translate(320 560)"><circle r="20" fill="{MUSTARD}" {stroke(5)}/></g>' + text(320, 620, "ALMONDS", 30, INK)
    return c, (1.0, 960, 560)


def s057(t, T, fr):
    c = bg_orchard_rows(t, bloom=False, bare=True, petals=False, sky_top="#B7C4CC")
    shrug = ease(seg(t, 0.3 * T, 0.5 * T)) * (1 - ease(seg(t, 0.8 * T, 0.95 * T)))
    c += person(960, 1060, 1.3, skin="#C68E64", outfit="shirt", outfit_color="#5B8DB8", arms=(lerp(15, 115, shrug), lerp(15, 115, shrug)), mouth="frown", eyes=auto_eyes(t, T), tilt=-8 * shrug)
    c += f'<g transform="translate(960 548) scale(1.3)"><ellipse cx="0" cy="-10" rx="110" ry="22" fill="#D8B48A" {stroke(5)}/><path d="M-60 -14 Q0 -80 60 -14 Z" fill="#D8B48A" {stroke(5)}/></g>'
    return c, cam_push(t, T, 1.0, 1.06, 960, 640)


# ---------------- PEOPLE AS BEES ----------------
def s058(t, T, fr):
    c = bg_orchard_rows(t, petals=True)
    look = 6 * math.sin(t * 2)
    c += pp(820, 1300, 2.0, t, T, arms=(15, 75), mouth="flat", look=(10 + look, -4), tilt=-6)
    c += feather_brush(1170, 760, 1.4, -30)
    return c, cam_push(t, T, 1.0, 1.06, 960, 600)


def worker(x, y, s, t, k, dab=True):
    a = 120 + 20 * math.sin(t * 5 + k) if dab else 40
    w = person(x, y, s, skin="#C68E64", outfit="shirt", outfit_color=["#5B8DB8", "#C9563F", "#7FA65A"][k % 3], arms=(30, a), mouth="smile", eyes="open")
    hat = f'<g transform="translate({x} {y - 400 * s:.0f}) scale({s})"><path d="M-110 10 L0 -50 L110 10 Z" fill="#E6D27A" {stroke(5)}/></g>'
    hx = x + s * (30 + 118 * math.sin(math.radians(a))); hy = y + s * (-250 + 118 * math.cos(math.radians(a)))
    return w + hat + feather_brush(hx, hy, s * 0.8, 20)


def s059(t, T, fr):
    c = bg_terraces(t)
    for k, (x, y, s) in enumerate([(420, 900, 0.55), (980, 820, 0.45), (1480, 960, 0.6)]):
        c += ladder(x - 40, y + 30, 360, s * 1.6, -6) + worker(x, y - 140 * s, s, t, k)
    return c, cam_pan(t, T, 860, 1060, 1.0)


def s060(t, T, fr):
    c = sky("#B7CFE0", "#EEF0E6", "bl60")
    c += f'<path d="M-200 900 Q600 700 1400 640 Q1800 620 2200 560" fill="none" stroke="#6B4A35" stroke-width="60" stroke-linecap="round"/>'
    for k, (x, y) in enumerate([(700, 660), (1100, 610), (1500, 580)]):
        c += (f'<g transform="translate({x} {y})">' + "".join(f'<ellipse cx="0" cy="-60" rx="44" ry="64" transform="rotate({j * 72})" fill="#FDF3F6" {stroke(5)}/>' for j in range(5)) +
              f'<circle r="26" fill="#F2B33D" {stroke(4)}/>' + "".join(f'<path d="M0 0 L{50 * math.cos(math.radians(j * 40)):.0f} {50 * math.sin(math.radians(j * 40)):.0f}" stroke="#E58FA6" stroke-width="3"/>' for j in range(9)) + '</g>')
    dab = abs(math.sin(t * 4))
    c += feather_brush(1100 + 40 * dab, 640 - 60 * dab, 2.4, -20)
    c += puff(1100, 600, (t * 2) % 1, 30, "#FFE39A")
    return c, cam_push(t, T, 1.0, 1.08, 1100, 600)


def s061(t, T, fr):
    c = bg_paper2(t)
    tilt = lerp(0, 18, ease(seg(t, 0.25 * T, 0.7 * T)))
    coins = "".join(f'<ellipse cx="{-60 + (k % 4) * 40}" cy="{-10 - (k // 4) * 18}" rx="20" ry="8" fill="{MUSTARD}" {stroke(3)}/>' for k in range(16))
    w = person(80, 0, 0.32, skin="#C68E64", outfit="shirt", outfit_color="#5B8DB8", arms=(10, 10), mouth="frown", eyes="closed")
    c += scale_balance(960, 400, 1.3, -tilt, left=honeybee(0, -40, 0.9, fr), right=coins + w)
    return c, (1.0, 960, 600)


def s062(t, T, fr):
    c = bg_terraces(t)
    r = rnd(62)
    for k in range(30):
        x, y = r.uniform(-100, 2000), r.uniform(560, 1100)
        s = 0.12 + (y - 560) / 540 * 0.18
        c += worker(x, y, s, t, k)
    c += f'<g transform="translate(1680 200)"><circle r="110" fill="#F3EAD3" {stroke(6)}/><path d="M0 0 L0 -60" transform="rotate({t * 720:.0f})" {stroke(8)}/>'
    c += f'<path d="M0 0 L0 -90" transform="rotate({t * 2600:.0f})" stroke="{RED}" stroke-width="6" stroke-linecap="round"/></g>'
    return c, cam_push(t, T, 1.0, 0.85, 960, 560)


# ---------------- ROBOT BEES ----------------
def s063(t, T, fr):
    c = bg_lab3(t) + f'<circle cx="960" cy="480" r="420" fill="url(#glow)" opacity="0.4"/>'
    c += robot_bee(960, 480 + 30 * math.sin(t * 3), 2.6, fr, t)
    return c, cam_push(t, T, 1.0, 1.08, 960, 500)


def s064(t, T, fr):
    c = bg_lab3(t)
    c += laptop(420, 640, 1.4)
    rx_, ry_ = 760 + 30 * math.sin(t * 5), 380 + 20 * math.sin(t * 7)
    c += f'<path d="M480 520 Q620 300 {rx_:.0f} {ry_ + 40:.0f}" fill="none" stroke="#2F2A28" stroke-width="5"/>' + robot_bee(rx_, ry_, 0.9, fr, t)
    dx = 30 * math.sin(t * 9)
    c += daisy(1380, 660, 1.8, t, 1, col="#F6A6B8", stem=60)
    c += (f'<g transform="translate({1380 + dx:.0f} {380 + 20 * math.sin(t * 6):.0f}) rotate({8 * math.sin(t * 9):.1f})"><rect x="-90" y="-20" width="180" height="40" rx="12" fill="#6E6A66" {stroke(5)}/>'
          + "".join(f'<ellipse cx="{x}" cy="-30" rx="50" ry="8" fill="#B8BEC4" {stroke(3)}/>' for x in (-90, 90)) + '</g>')
    c += person(1720, 1000, 1.1, skin="#F3D9C0", outfit="coat", outfit_color="#F4F4F0", arms=(30, 90), mouth="o", eyes="open", hair_style="curly", hair_color="#6B4A35", flip=True, look=(-6, -4))
    c += f'<path d="M1680 560 Q1690 580 1680 600 Q1670 580 1680 560 Z" fill="#9DD3E6" {stroke(3)}/>'
    return c, (1.0, 960, 560)


def s065(t, T, fr):
    c = sky("#F7D9A0", "#F3E6C4", "s65") + f'<circle cx="960" cy="560" r="560" fill="url(#glow)" opacity="0.5"/>'
    c += sunflower(960, 1700, 5.5, t * 0.2, 0)
    c += honeybee(960, 470, 2.6, fr, mouth="smile" if int(t * 2) % 2 else "o", look=(2, 4))
    c += sparkle(1300, 300, (t * 0.8) % 1, 40, "#FFF3C4") + sparkle(620, 340, (t * 0.8 + 0.5) % 1, 30, "#FFF3C4")
    return c, cam_push(t, T, 1.0, 1.06, 960, 480)


# ---------------- OTHER INSECTS ----------------
def s066(t, T, fr):
    c = bg_meadow2(t, seed=66)
    c += pp(420, 1060, 1.2, t, T, arms=(60, 70), mouth="smile", look=(8, 0))
    c += f'<g transform="translate(560 720) rotate(-10)"><rect x="-50" y="-70" width="100" height="140" rx="8" fill="#B98B5E" {stroke(5)}/><rect x="-40" y="-56" width="80" height="116" fill="#FFF6E0"/>' + "".join(f'<path d="M-30 {y} L30 {y}" stroke="#C8BFA8" stroke-width="5"/>' for y in (-30, -10, 10, 30)) + '</g>'
    cast = [lambda x, y: hoverfly(x, y, 1.1, fr), lambda x, y: beetle(x, y, 0.9), lambda x, y: butterfly(x, y, 0.5, fr), lambda x, y: moth(x, y, 0.45, fr)]
    for k, f in enumerate(cast):
        step = ease_out_back(seg(t, 0.15 * T + k * 0.12 * T, 0.3 * T + k * 0.12 * T))
        x = 900 + k * 260
        c += f(x, lerp(820, 700, step))
    return c, (1.0, 960, 560)


def s067(t, T, fr):
    c = sky("#A9CFE0", "#F3E6C4", "s67") + f'<path d="M-600 760 L2600 760 L2600 1600 L-600 1600 Z" fill="#C9B35E" {stroke()}/>'
    c += "".join(sunflower(x, 1100, 0.9, t, i) for i, x in enumerate(range(-100, 2100, 180)))
    c += hoverfly(760 + 30 * math.sin(t * 2), 420 + 20 * math.sin(t * 3), 2.0, fr)
    for k in range(10):
        on = k < 4 and t > (0.3 + k * 0.08) * T
        x = 1150 + (k % 5) * 110; y = 300 + (k // 5) * 140
        c += f'<rect x="{x - 40}" y="{y - 50}" width="80" height="100" rx="14" fill="{MUSTARD if on else "#F6F0E2"}" {stroke(5)}/>'
        c += hoverfly(x, y, 0.45, fr) if on else honeybee(x, y, 0.28, fr)
    return c, (1.0, 960, 560)


def s068(t, T, fr):
    c = f'<defs><linearGradient id="dn" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#A9CFE0"/><stop offset="0.6" stop-color="#E6B8A0"/><stop offset="1" stop-color="#2E3A57"/></linearGradient></defs>'
    c += f'<rect x="-600" y="-400" width="3200" height="1900" fill="url(#dn)"/><circle cx="1720" cy="200" r="70" fill="#F4E9B8" {stroke(5)}/>'
    c += f'<path d="M-600 820 Q900 760 2600 830 L2600 1600 L-600 1600 Z" fill="#6E9A5E" {stroke()}/>'
    c += rose(420, 1000, 2.6, t, 1, col="#F6E0E6") + beetle(420, 650, 0.7)
    c += "".join(daisy(960 + dx, 960, 1.6, t, k, col=["#E0533A", "#F2B33D", "#D96C8A"][k], stem=160) for k, dx in enumerate((-80, 0, 80)))
    c += butterfly(960 + 20 * math.sin(t * 2), 640, 0.7, fr)
    c += (f'<g transform="translate(1600 960)"><path d="M0 0 L0 -220" stroke="#4E7F3A" stroke-width="8"/>' + "".join(f'<path d="M0 -220 Q{a} -300 {a * 1.5:.0f} -330" fill="none" stroke="#F6F0E2" stroke-width="14" stroke-linecap="round"/>' for a in (-50, -20, 20, 50)) + '</g>')
    c += moth(1600 + 30 * math.sin(t * 3), 560, 0.5, fr)
    return c, cam_pan(t, T, 820, 1100, 1.0)


def s069(t, T, fr):
    c = bg_paper2(t)
    petals = "".join(f'<ellipse cx="0" cy="-200" rx="110" ry="190" transform="rotate({k * 60})" fill="{["#F6A6B8", "#C9B6E4", MUSTARD][k % 3]}" {stroke(7)}/>' for k in range(6))
    c += f'<g transform="translate(960 540)">{petals}<circle r="160" fill="#F6F0E2" {stroke(7)}/>'
    c += f'<path d="M-90 -20 Q-90 -70 -30 -70 Q20 -100 60 -60 Q110 -60 110 0 Q110 60 40 70 Q-40 80 -90 40 Z" fill="#E6DCC6" stroke="{INK}" stroke-width="6" stroke-dasharray="14 10"/></g>'
    tries = [lambda x, y: hoverfly(x, y, 0.9, fr), lambda x, y: beetle(x, y, 0.8), lambda x, y: butterfly(x, y, 0.45, fr)]
    k = int(t / (T / 3)) % 3
    u = (t % (T / 3)) / (T / 3)
    x = lerp(1500, 980, ease(min(1, u * 2))) + (0 if u < 0.5 else 300 * (u - 0.5) * 2)
    c += tries[k](x, 540 - 120 * math.sin(u * math.pi))
    c += question_mark(1500, 260 + 10 * math.sin(t * 3), 0.9)
    return c, (1.0, 960, 560)


# ---------------- THE WILD WORLD ----------------
def s070(t, T, fr):
    c = bg_farmland(t)
    c += "".join(spruce(x, 700 + (i % 2) * 20, 1.0, "#3E5E46") for i, x in enumerate(range(1300, 2300, 120)))
    for k in range(3):
        u = ((t * 0.35) + k / 3) % 1
        c += f'<ellipse cx="960" cy="700" rx="{100 + 1100 * u:.0f}" ry="{40 + 420 * u:.0f}" fill="none" stroke="#FFF6E0" stroke-width="{10 * (1 - u):.1f}" opacity="{1 - u:.2f}"/>'
    return c, cam_push(t, T, 1.0, 0.92, 960, 600)


SCENES = {i: globals()[f"s{i:03d}"] for i in range(36, 71)}
KEYFRAME = {39: 0.95, 41: 0.6, 51: 0.5, 56: 0.9, 61: 0.8}
