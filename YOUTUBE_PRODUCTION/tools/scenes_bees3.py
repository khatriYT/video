"""Episode 2 scenes 071-105."""
import math
from draw import *
from draw2 import stroke, text, sky, tree, bat, moth, beetle, hoverfly, spider, web, question_mark, auto_eyes, check, calendar, person_icon, dragonfly, vulture_sil
from draw3 import *
from scenes_bees2 import table_scene, beige_plate, worker, badge

KEYFRAME = {}


def s071(t, T, fr):
    fade = seg(t, 0.1 * T, 0.95 * T)
    c = bg_meadow2(t, fade=0.85 * fade, seed=71)
    yr = 1 + int(fade * 9)
    c += f'<g transform="translate(1700 300)"><rect x="-140" y="-60" width="280" height="110" rx="14" fill="{CREAM}" {stroke(6)}/>' + text(0, 22, f"YEAR {yr}", 60) + '</g>'
    return c, (1.0, 960, 560)


def tomato_flower(x, y, s=1.0, glow=0.0):
    pet = "".join(f'<path d="M0 0 L{60 * math.cos(math.radians(a)):.0f} {60 * math.sin(math.radians(a)):.0f}" stroke="{MUSTARD}" stroke-width="26" stroke-linecap="round"/>' for a in range(-90, 270, 60))
    return (f'<g transform="translate({x} {y}) scale({s})"><path d="M0 0 L0 260" stroke="#4E7F3A" stroke-width="10"/>{pet}'
            + "".join(f'<path d="M0 0 L{60 * math.cos(math.radians(a)):.0f} {60 * math.sin(math.radians(a)):.0f}" fill="none" {stroke(2)} opacity="0.4"/>' for a in range(-90, 270, 60)) +
            f'<circle r="{40 + 10 * glow:.0f}" fill="url(#glow)" opacity="{glow:.2f}"/><path d="M-16 0 L0 90 L16 0 Z" fill="#E6C24A" {stroke(4)}/>'
            f'<path d="M-16 0 L16 0" {stroke(4)}/></g>')


def s072(t, T, fr):
    c = bg_greenhouse(t) + f'<rect x="-600" y="-400" width="3200" height="1900" fill="#FFFFFF" opacity="0.25"/>'
    c += tomato_flower(960, 420, 3.0, 0.5 + 0.5 * math.sin(t * 3))
    c += f'<path d="M1140 560 Q1260 600 1300 700" fill="none" stroke="{RED}" stroke-width="8" stroke-dasharray="14 10"/>' + text(1340, 760, "pollen locked inside", 34, INK, weight=800)
    return c, cam_push(t, T, 1.0, 1.08, 960, 520)


def s073(t, T, fr):
    c = bg_greenhouse(t) + f'<rect x="-600" y="-400" width="3200" height="1900" fill="#FFFFFF" opacity="0.25"/>'
    c += tomato_flower(960, 420, 3.0)
    shake = 1.0 if 0.15 * T < t < 0.85 * T else 0.0
    c += bumblebee(960, 300, 1.6, fr, rot=90, shake=shake)
    if shake:
        c += "".join(f'<path d="M{820 - k * 26} {220 + k * 30} q-20 20 0 40 M{1100 + k * 26} {220 + k * 30} q20 20 0 40" fill="none" {stroke(5)}/>' for k in range(3))
        r = rnd(int(t * 10))
        c += "".join(f'<circle cx="{960 + r.uniform(-40, 40):.0f}" cy="{520 + r.uniform(0, 200):.0f}" r="7" fill="#FFD25A" {stroke(2)}/>' for _ in range(14))
    c += (f'<g transform="translate(400 760) rotate({12 * math.sin(t * 20) if shake else 0:.1f})"><rect x="-50" y="-110" width="100" height="140" rx="20" fill="#F6F0E2" {stroke(5)}/>'
          f'<path d="M-50 -110 Q0 -170 50 -110 Z" fill="#C9C6C0" {stroke(5)}/>' + "".join(f'<circle cx="{dx}" cy="-140" r="4" fill="{INK}"/>' for dx in (-14, 0, 14)) + '</g>')
    return c, (1.0, 960, 540)


def s074(t, T, fr):
    g = ease(seg(t, 0.1 * T, 0.7 * T))
    c = bg_greenhouse(t)
    for k, x in enumerate(range(200, 1000, 260)):
        for j in range(3):
            c += f'<circle cx="{x + 40}" cy="{420 + j * 160}" r="{lerp(10, 44, g):.0f}" fill="#E0533A" {stroke(4)}/>'
    c += f'<rect x="1080" y="300" width="900" height="900" fill="#DCEEE8" opacity="0.6"/>'
    for k in range(4):
        bx = 1220 + k * 200
        c += f'<ellipse cx="{bx}" cy="760" rx="130" ry="200" fill="#5E8E4A" {stroke(5)}/>'
        c += "".join(blueberry(bx + dx, 660 + dy, lerp(0.3, 0.9, g)) for dx, dy in [(-50, 0), (40, 60), (-20, 140), (50, 180)])
    return c, cam_pan(t, T, 880, 1060, 1.0)


def s075(t, T, fr):
    c = bg_greenhouse(t)
    vib = 4 * math.sin(t * 40)
    c += person(440, 1000, 1.1, skin="#C68E64", outfit="shirt", outfit_color="#7FA65A", arms=(20, 70), mouth="flat", eyes=auto_eyes(t, T), look=(6, 0))
    c += f'<g transform="translate({600 + vib:.1f} 760) rotate(-20)"><rect x="0" y="-12" width="140" height="24" rx="8" fill="#6E6A66" {stroke(4)}/><circle cx="150" cy="0" r="14" fill="{MUSTARD}" {stroke(3)}/></g>'
    c += f'<path d="M960 -400 L960 1600" stroke="{CREAM}" stroke-width="16"/>'
    c += (f'<g transform="translate(1420 900)"><rect x="-200" y="-140" width="400" height="200" fill="#D9C49A" {stroke(6)}/><path d="M-200 -140 L-160 -200 L240 -200 L200 -140 Z" fill="#C9B07E" {stroke(6)}/>'
          + honeybee(0, -40, 0.45, 0, flap=False).replace("#F2B33D", "#F2B33D") + text(0, 30, "BUMBLEBEES", 34, INK) + '</g>')
    for k in range(6):
        u = (t * 0.4 + k / 6) % 1
        c += bumblebee(1420 + 300 * math.sin(u * 5 + k) * u, 760 - 500 * u, 0.35, fr + k)
    return c, (1.0, 960, 560)


def hedge(t, berries=1.0):
    c = sky("#A9CFE0", "#F3E6C4", "hed") + f'<path d="M-600 800 L2600 800 L2600 1600 L-600 1600 Z" fill="#7FA65A" {stroke()}/>'
    c += "".join(f'<ellipse cx="{x}" cy="{700 + (i % 2) * 20}" rx="220" ry="200" fill="{["#4E7F3A", "#5E8E4A"][i % 2]}" {stroke(5)}/>' for i, x in enumerate(range(-200, 2300, 300)))
    r = rnd(76)
    n = int(60 * berries)
    c += "".join(f'<circle cx="{r.uniform(-100, 2000):.0f}" cy="{r.uniform(560, 820):.0f}" r="14" fill="#B5263A" {stroke(3)}/>' for _ in range(n))
    return c


def s076(t, T, fr):
    berries = 1 - 0.85 * ease(seg(t, 0.1 * T, 0.8 * T))
    c = hedge(t, berries)
    c += songbird(760, 860, 1.2, 0) + mouse(1180, 1000, 1.2, t)
    c += question_mark(960, 560 + 10 * math.sin(t * 3), 0.8) if t > 0.6 * T else ""
    return c, cam_push(t, T, 1.0, 1.06, 960, 700)


def s077(t, T, fr):
    c = sky("#A9CFE0", "#F3E6C4", "rb") + f'<path d="M-600 720 Q900 660 2600 730 L2600 1600 L-600 1600 Z" fill="#7FA65A" {stroke()}/>'
    c += f'<path d="M-600 900 Q900 840 2600 920 L2600 1100 Q900 1000 -600 1080 Z" fill="#7FB4BE" {stroke()}/>'
    c += f'<path d="M100 640 Q600 560 900 600" fill="none" stroke="#6B4A35" stroke-width="30" stroke-linecap="round"/>'
    look = 14 * math.sin(t * 2)
    c += bee_eater(560, 520, 1.5, look=look)
    c += web(1500, 400, 1.3) + spider(1500, 400, 0.7, t)
    c += dragonfly(1100 + 40 * math.sin(t * 2), 760, 0.9, fr)
    return c, cam_pan(t, T, 880, 1060, 1.0)


def s078(t, T, fr):
    c = bg_paper2(t)
    icons = [honeybee(0, 0, 0.45, 0, flap=False), daisy(0, 60, 0.8, 0, 0, col="#F6A6B8", stem=40), cherry(0, 0, 1.2), bird(0, 0, 0.5, 0, col="#B5543F", belly="#F3D9B1")]
    for k, ic in enumerate(icons):
        fall = seg(t, 0.2 * T + k * 0.15 * T, 0.32 * T + k * 0.15 * T)
        c += domino(480 + k * 300, 860, 1.4, fall, ic)
    if t < 0.25 * T:
        c += f'<path d="M260 600 l60 0" stroke="{RED}" stroke-width="12" stroke-linecap="round"/>'
    return c, (1.0, 960, 600)


def s079(t, T, fr):
    c = bg_farmyard(t)
    c += cow(1100, 940, 1.1, t, t * 0.5)
    c += pp(480, 1060, 1.2, t, T, mouth="smile", look=(8, 0), arms=(15, 60))
    return c, cam_push(t, T, 1.0, 1.05, 900, 640)


def alfalfa(x, y, s=1.0, t=0.0, i=0):
    sw = 3 * math.sin(t * 1.5 + i)
    buds = "".join(f'<circle cx="{(-1) ** k * 8}" cy="{-90 - k * 12}" r="9" fill="#8E7CC3" {stroke(2)}/>' for k in range(6))
    return f'<g transform="translate({x:.0f} {y:.0f}) rotate({sw:.1f}) scale({s:.2f})"><path d="M0 0 L0 -90" stroke="#4E7F3A" stroke-width="5"/><path d="M0 -40 q-24 -8 -30 -24 q20 0 30 14 Z" fill="#7FA65A" {stroke(2)}/>{buds}</g>'


def s080(t, T, fr):
    c = sky("#A9CFE0", "#F3E6C4", "alf") + f'<path d="M-600 640 L2600 640 L2600 1600 L-600 1600 Z" fill="#7FA65A" {stroke()}/>'
    r = rnd(80)
    for j in range(6):
        for k in range(24):
            c += alfalfa(r.uniform(-200, 1200), 700 + j * 80, 0.6 + j * 0.15, t, k + j * 30)
    c += solitary_bee(560 + 60 * math.sin(t * 2), 720 + 20 * math.sin(t * 4), 1.4, fr, "#6E6A66", "#E6E0D2")
    c += f'<g transform="translate(1500 1000)"><rect x="-200" y="-90" width="400" height="140" rx="40" fill="#C9B35E" {stroke(6)}/>' + "".join(f'<path d="M-180 {y} L180 {y}" stroke="#A8943E" stroke-width="5"/>' for y in (-50, -10, 30)) + '</g>'
    c += cow(1550, 880, 0.9, t, t)
    return c, cam_pan(t, T, 820, 1100, 1.0)


def s081(t, T, fr):
    c = sky("#A9CFE0", "#F3E6C4", "ccs") + clouds(t, 150, seed=81, n=3)
    c += f'<path d="M-600 560 L2600 560 L2600 1600 L-600 1600 Z" fill="#9CB98A" {stroke()}/>'
    c += f'<path d="M-600 600 L640 600 L640 1200 L-600 1200 Z" fill="#7FA65A" {stroke(4)}/>' + "".join(
        f'<g transform="translate({x} {y})"><path d="M0 0 L0 -60" stroke="#6B4A35" stroke-width="5"/><circle cx="0" cy="-70" r="20" fill="#FFFFFF" {stroke(3)}/><circle cx="-14" cy="-62" r="14" fill="#FFFFFF" {stroke(3)}/><circle cx="14" cy="-62" r="14" fill="#FFFFFF" {stroke(3)}/></g>'
        for x in range(20, 620, 90) for y in range(720, 1180, 120))
    c += "".join(sunflower(x, y, 0.55, t, x) for x in range(700, 1240, 110) for y in (840, 1000, 1160))
    c += f'<path d="M1260 600 L2600 600 L2600 1200 L1260 1200 Z" fill="#E6D24A" {stroke(4)}/>' + "".join(f'<circle cx="{x}" cy="{y}" r="16" fill="#F6E06A" {stroke(2)}/>' for x in range(1290, 2000, 60) for y in range(650, 1180, 70))
    c += text(320, 660, "COTTON", 44, CREAM, outline=INK) + text(970, 660, "SUNFLOWERS", 44, CREAM, outline=INK) + text(1600, 660, "CANOLA", 44, CREAM, outline=INK)
    c += "".join(honeybee(300 + k * 600 + 60 * math.sin(t * 2 + k), 800 + 30 * math.sin(t * 3 + k), 0.4, fr + k) for k in range(3))
    return c, (1.0, 960, 560)


def tshirt(x, y, s=1.0):
    return f'<g transform="translate({x} {y}) scale({s})"><path d="M-60 -80 L-120 -40 L-90 10 L-60 -10 L-60 90 L60 90 L60 -10 L90 10 L120 -40 L60 -80 Q0 -50 -60 -80 Z" fill="#5B8DB8" {stroke(6)}/></g>'


def milk(x, y, s=1.0):
    return (f'<g transform="translate({x} {y}) scale({s})"><path d="M-50 -60 L0 -110 L50 -60 L50 90 L-50 90 Z" fill="#F6F4EE" {stroke(6)}/><rect x="-50" y="-20" width="100" height="60" fill="#5B8DB8"/>'
            + text(0, 22, "MILK", 30, "#FFF6E0") + '</g>')


def oil(x, y, s=1.0):
    return (f'<g transform="translate({x} {y}) scale({s})"><rect x="-16" y="-120" width="32" height="30" fill="#6E9A5E" {stroke(5)}/><path d="M-50 -90 L50 -90 L56 90 L-56 90 Z" fill="#E6C24A" fill-opacity="0.85" {stroke(6)}/>'
            f'<rect x="-40" y="-10" width="80" height="50" rx="6" fill="#FFF6E0" {stroke(3)}/>' + text(0, 24, "OIL", 26, INK) + '</g>')


def s082(t, T, fr):
    c = table_scene(t)
    items = [tshirt, milk, oil]
    for k, f in enumerate(items):
        p = ease_out_back(seg(t, 0.1 * T + k * 0.45, 0.1 * T + k * 0.45 + 0.4))
        x = 360 + k * 380
        if p > 0:
            c += f'<g transform="translate({x} 820) scale({p:.2f}) translate({-x} -820)">' + f(x, 820, 1.6) + honeybee(x + 110, 660, 0.3, fr) + '</g>'
    return c, (1.0, 960, 560)


def s083(t, T, fr):
    c = f'<rect x="-600" y="-400" width="3200" height="1900" fill="#3E4A5E"/><circle cx="1300" cy="440" r="600" fill="url(#glow)" opacity="0.25"/>'
    c += f'<rect x="1000" y="140" width="760" height="520" rx="12" fill="#F6F0E2" {stroke(6)}/><path d="M1060 600 L1700 600 M1060 600 L1060 200" {stroke(5)}/>'
    p = seg(t, 0.1 * T, 0.8 * T)
    pts = [(lerp(1080, 1680, v), 260 + 300 * v + 30 * math.sin(v * 14)) for v in [i / 40 for i in range(int(40 * p) + 1)]]
    if len(pts) > 1:
        c += f'<path d="M{" L".join(f"{x:.0f} {y:.0f}" for x, y in pts)}" fill="none" stroke="{RED}" stroke-width="10" stroke-linecap="round"/>'
    c += pp(560, 1300, 2.0, t, T, mouth="flat", look=(10, -2), arms=(15, 15))
    return c, cam_push(t, T, 1.0, 1.06, 960, 560)


def s084(t, T, fr):
    lid = seg(t, 0.25 * T, 0.6 * T)
    c = bg_apiary(t, snow=True)
    c += "".join(hive_box(x, 980, 0.75, "#E6E8E4") + f'<path d="M{x - 100} {980 - 2 * 90 * 0.75 - 30} q100 -30 200 0" fill="#FFFFFF" {stroke(4)}/>' for x in (300, 1550))
    c += hive_box(900, 1000, 1.1, "#F6F0E2", lid=lid)
    c += beekeeper(1220, 1040, 1.1, t, T, arms=(20, lerp(20, 70, ease(lid))), mouth="frown")
    return c, cam_push(t, T, 1.0, 1.06, 960, 640)


def s085(t, T, fr):
    up = ease(seg(t, 0.1 * T, 0.45 * T))
    c = bg_apiary(t) + f'<rect x="-600" y="-400" width="3200" height="1900" fill="#5E4E66" opacity="0.35"/>'
    c += hive_box(560, 1000, 1.1, "#F6F0E2")
    c += beekeeper(1000, 1060, 1.2, t, T, arms=(60, 70), mouth="o")
    fy = lerp(800, 500, up)
    c += f'<rect x="1100" y="{fy - 160:.0f}" width="420" height="300" fill="#C98A3E" {stroke(6)}/>' + f'<g opacity="0.95">' + hex_comb(1120, fy - 140, 8, 6, 26, capped=0.8, seed=85).replace('stroke-width="4"', 'stroke-width="3"') + '</g>'
    c += honeybee(1310, fy - 10, 0.6, 0, queen=True, flap=False, mouth="o")
    c += "".join(question_mark(1180 + k * 180, 300 + 20 * math.sin(t * 3 + k), 0.6) for k in range(3))
    return c, cam_push(t, T, 1.0, 1.05, 1100, 560)


def s086(t, T, fr):
    c = f'<rect x="-600" y="-400" width="3200" height="1900" fill="#6B4A2E"/>' + hex_comb(-200, -100, 34, 26, 44, capped=0.5, seed=86) + f'<rect x="-600" y="-400" width="3200" height="1900" fill="#2B2420" opacity="0.4"/>'
    c += honeybee(900, 600, 3.6, fr, mouth="frown", look=(2, 4))
    c += mite(740, 420 + 4 * math.sin(t * 6), 1.6, t)
    c += "".join(virus(lerp(1400, 1300, k / 3) + 60 * math.sin(t + k), 260 + k * 180, 0.7, "#B5543F", t) for k in range(3))
    return c, cam_push(t, T, 1.0, 1.08, 900, 540)


def s087(t, T, fr):
    c = bg_farmland(t)
    c += tractor_sprayer(lerp(400, 1500, ease(t / T)), 900, 1.0, t)
    return c, cam_pan(t, T, 860, 1060, 1.0)


def parking(t):
    c = f'<rect x="-600" y="700" width="3200" height="900" fill="#8E8A86" {stroke()}/>'
    c += "".join(f'<path d="M{x} 760 L{x - 40} 1000" stroke="#F6F0E2" stroke-width="10"/>' for x in range(-400, 2600, 220))
    c += "".join(f'<rect x="{x}" y="{y}" width="160" height="80" rx="20" fill="{col}" {stroke(5)}/>' for x, y, col in [(-200, 820, "#5B8DB8"), (460, 830, "#C9563F"), (1100, 820, MUSTARD)])
    return c


def s088(t, T, fr):
    wipe = lerp(-400, 2400, ease(seg(t, 0.1 * T, 0.9 * T)))
    c = bg_meadow2(t, seed=88)
    c += f'<clipPath id="wp"><rect x="-600" y="-400" width="{wipe + 600:.0f}" height="1900"/></clipPath><g clip-path="url(#wp)">{sky("#C9C6C0", "#E6E0D2", "gry")}{parking(t)}</g>'
    c += bulldozer(wipe + 100, 1000, 1.0, t)
    return c, (1.0, 960, 560)


def s089(t, T, fr):
    c = bg_paper2(t)
    sep = ease(seg(t, 0.2 * T, 0.7 * T))
    c += calendar(lerp(860, 520, sep), 520, 2.0, "MAR") + daisy(lerp(860, 520, sep), 960, 1.6, t, 0, col="#F6A6B8", stem=150)
    c += calendar(lerp(1060, 1400, sep), 520, 2.0, "APR") + honeybee(lerp(1060, 1400, sep), 900, 1.0, fr, mouth="o")
    if sep > 0.5:
        c += f'<path d="M740 820 L1180 820" stroke="{RED}" stroke-width="12" stroke-dasharray="20 14" stroke-linecap="round"/>' + text(960, 790, "MISMATCH", 40, RED)
    return c, (1.0, 960, 560)


def s090(t, T, fr):
    c = bg_paper2(t)
    labels = [("MITES", "#B5543F"), ("PESTICIDES", "#7F96A8"), ("HABITAT LOSS", "#8A6A4E"), ("CLIMATE", "#E58A3A")]
    strain = 0
    for k, (lab, col) in enumerate(labels):
        p = ease_out_bounce(seg(t, 0.1 * T + k * 0.45, 0.1 * T + k * 0.45 + 0.5))
        if p <= 0:
            continue
        strain = k + p
        y = 700 - k * 120 - (1 - p) * 600
        c += f'<rect x="560" y="{y - 110:.0f}" width="560" height="110" rx="10" fill="{col}" {stroke(6)}/>' + text(840, y - 40, lab, 50, "#FFF6E0")
    c += honeybee(840, 790, 1.0 - 0.04 * strain, fr, mouth="frown", look=(0, -4)).replace('scale(', f'translate(0 {4 * math.sin(t * 20) * min(1, strain):.1f}) scale(', 1)
    return c, (1.0, 840, 520)


def s091(t, T, fr):
    c = bg_cottage_garden(t, "day")
    c += bee_hotel(1700, 1000, 0.9)
    arrive = seg(t, 0, 0.8 * T)
    for k in range(6):
        u = seg(arrive, k * 0.1, k * 0.1 + 0.5)
        x = lerp(2200, 300 + k * 220, ease(u)); y = lerp(300, 880 + (k % 2) * 40, ease(u)) + 20 * math.sin(t * 4 + k)
        c += (honeybee if k % 2 else bumblebee)(x, y, 0.3, fr + k, flip=True)
    return c, cam_push(t, T, 1.0, 1.05, 1000, 680)


def s092(t, T, fr):
    c = bg_cottage_garden(t, "day", insects=True)
    grow = ease(seg(t, 0.2 * T, 0.8 * T))
    c += f'<rect x="1260" y="980" width="600" height="120" fill="#8A6A4E" {stroke(5)}/>'
    c += "".join(daisy(1300 + k * 100, 1060, 0.9 * grow + 0.01, t, k, col=["#F6A6B8", MUSTARD, "#C9B6E4"][k % 3]) for k in range(6))
    c += pp(1100, 1060, 1.1, t, T, arms=(20, 100 + 10 * math.sin(t * 6)), mouth="smile", look=(8, 4))
    c += f'<g transform="translate(300 860)"><rect x="-40" y="-90" width="80" height="140" rx="14" fill="#9DB8D6" {stroke(5)}/><rect x="-20" y="-120" width="40" height="34" fill="#6E6A66" {stroke(4)}/>'
    c += f'<path d="M-80 -120 L80 60 M80 -120 L-80 60" stroke="{RED}" stroke-width="16" stroke-linecap="round"/></g>'
    return c, cam_push(t, T, 1.0, 1.05, 960, 660)


def s093(t, T, fr):
    c = f'<rect x="-600" y="-400" width="3200" height="1900" fill="#C9A77C"/>' + "".join(f'<path d="M{x} -400 L{x} 1500" stroke="#B98B5E" stroke-width="8"/>' for x in range(-600, 2600, 80))
    c += bee_hotel(960, 1000, 2.4)
    peek = ease_out_back(seg(t, 0.2 * T, 0.5 * T))
    c += solitary_bee(960 + 26 * peek, 645, 1.2, fr if peek > 0.9 else 0, "#2E3A6E", "#5E6E9E", rot=0)
    return c, cam_push(t, T, 1.0, 1.1, 960, 640)


def s094(t, T, fr):
    c = bg_city(t, green=False)
    c += f'<rect x="460" y="140" width="1000" height="760" fill="#E8C9A0" {stroke(6)}/><rect x="560" y="220" width="800" height="520" fill="#BFD9D6" {stroke(6)}/><path d="M960 220 L960 740 M560 480 L1360 480" {stroke(8)}/>'
    c += window_box(960, 820, 1.6, t)
    land = ease(seg(t, 0.15 * T, 0.6 * T))
    c += honeybee(lerp(1700, 1020, land), lerp(200, 640, land), 0.6, fr, flip=True)
    c += (f'<g transform="translate(1600 640)"><rect x="-60" y="-120" width="120" height="180" rx="12" fill="{RED}" {stroke(5)}/><rect x="-40" y="-100" width="80" height="50" fill="#FFF6E0" {stroke(3)}/>'
          f'<path d="M60 -60 Q100 -60 100 0 L100 40" fill="none" {stroke(6)}/></g>')
    return c, cam_push(t, T, 1.0, 1.06, 960, 560)


def s095(t, T, fr):
    c = bg_farmland(t)
    bloom = ease(seg(t, 0.1 * T, 0.7 * T))
    for j in range(4):
        y0 = 440 + j * 150
        c += f'<rect x="-600" y="{y0 - 10}" width="3200" height="{28 * bloom + 1:.0f}" fill="#9CB98A"/>'
        if bloom > 0.3:
            c += flower_bed(-200, 2200, y0 + 6, t, seed=95 + j, density=1.0, scale=0.3 + j * 0.08)
    return c, cam_push(t, T, 1.06, 1.0, 960, 600)


def s096(t, T, fr):
    c = bg_city(t, green=True)
    for k in range(8):
        u = (t * 0.25 + k / 8) % 1
        c += honeybee(lerp(-100, 2000, u), 380 + 120 * math.sin(u * 8 + k), 0.25, fr + k)
    return c, cam_pan(t, T, 860, 1060, 1.0)


def s097(t, T, fr):
    c = bg_cottage_garden(t, "sunset", insects=False)
    look = 10 * math.sin(t * 1.2)
    c += pp(1100, 1060, 1.1, t, T, mouth="flat", look=(look, -2), arms=(15, 15))
    return c, cam_push(t, T, 1.0, 1.08, 1060, 640)


def s098(t, T, fr):
    c = bg_cottage_garden(t, "day", insects=False)
    fly = ease(seg(t, 0.15 * T, 0.95 * T))
    x, y = lerp(900, 2300, fly), lerp(700, 120, fly) + 80 * math.sin(fly * 9)
    c += (f'<g transform="translate({x:.0f} {y:.0f}) rotate({fly * 540:.0f}) scale(0.6)"><rect x="-380" y="-200" width="760" height="400" fill="#F3E6C4" {stroke(8)}/>'
          + text(0, -20, "\"...FOUR YEARS...\"", 70, "#8A8070") + f'<path d="M-300 60 L300 60" stroke="#E2CDA4" stroke-width="6"/></g>')
    c += "".join(f'<path d="M{200 + k * 300 + (t * 400) % 300:.0f} {300 + k * 90} q60 -20 120 0" fill="none" stroke="#FFFFFF" stroke-width="6" stroke-linecap="round" opacity="0.8"/>' for k in range(5))
    return c, (1.0, 960, 560)


def s099(t, T, fr):
    c = table_scene(t)
    col = 1 - ease(seg(t, 0.15 * T, 0.85 * T))
    c += beige_plate(960, 880, 1.6, col)
    return c, cam_push(t, T, 1.0, 1.08, 960, 760)


def s100(t, T, fr):
    c = bg_orchard_rows(t, sky_top="#C98A7A")
    c += f'<rect x="-600" y="-400" width="3200" height="1900" fill="#5E4E66" opacity="0.25"/>'
    for k, (x, y, s) in enumerate([(520, 980, 0.6), (1400, 980, 0.6), (960, 760, 0.35)]):
        c += ladder(x - 40, y + 40, 380, s * 1.6, -6) + worker(x, y - 150 * s, s, t, k)
    return c, cam_pan(t, T, 880, 1040, 1.0)


def market_street(t):
    c = sky("#A9CFE0", "#F3E6C4", "mkt") + f'<rect x="-600" y="860" width="3200" height="700" fill="#C9B99A" {stroke()}/>'
    for k, x in enumerate(range(-100, 2100, 420)):
        col = ["#C9563F", "#5B8DB8", MUSTARD, "#7FA65A", "#D96C8A"][k % 5]
        c += f'<rect x="{x}" y="560" width="360" height="300" fill="#F0E0C0" {stroke(5)}/>'
        c += "".join(f'<path d="M{x + j * 60} 560 L{x + j * 60 + 60} 560 L{x + j * 60 + 60} 640 Q{x + j * 60 + 30} 680 {x + j * 60} 640 Z" fill="{col if j % 2 else "#FFF6E0"}" {stroke(3)}/>' for j in range(6))
        c += f'<rect x="{x + 20}" y="760" width="320" height="100" fill="#B98B5E" {stroke(4)}/>' + "".join([apple, strawberry, avocado, cherry][j % 4](x + 60 + j * 70, 780, 0.6) for j in range(4))
    return c


def s101(t, T, fr):
    g = ease(seg(t, 0.15 * T, 0.85 * T))
    c = market_street(t)
    c += f'<g filter="url(#grey{int(g * 10)})"></g>'
    c += f'<rect x="-600" y="-400" width="3200" height="1900" fill="#9A9690" opacity="{0.62 * g:.2f}" style="mix-blend-mode:color"/>'
    c += f'<rect x="-600" y="-400" width="3200" height="1900" fill="#7A7670" opacity="{0.25 * g:.2f}"/>'
    return c, cam_pan(t, T, 880, 1040, 1.0)


def s102(t, T, fr):
    fade = ease(seg(t, 0.05 * T, 0.95 * T))
    c = bg_meadow2(t, fade=0.9 * fade, seed=102, sky_top=["#A9CFE0", "#C9C6C0"][int(fade > 0.6)])
    return c, cam_push(t, T, 1.0, 0.9, 960, 600)


def s103(t, T, fr):
    c = bg_meadow2(t, seed=103)
    u = ease(seg(t, 0.05 * T, 0.95 * T))
    x, y = lerp(300, 1600, u), 640 - 200 * math.sin(u * math.pi)
    c += sunflower(300, 1060, 1.3, t, 0) + sunflower(1600, 1060, 1.3, t, 1)
    c += honeybee(x, y, 1.1, fr, cap=True)
    c += (f'<g transform="translate({x - 20:.0f} {y + 90:.0f})"><rect x="-50" y="-34" width="100" height="68" rx="6" fill="#D8B48A" {stroke(5)}/>'
          f'<path d="M-50 -10 L50 -10 M0 -34 L0 34" stroke="#A8743A" stroke-width="5"/><circle cx="26" cy="12" r="12" fill="#FFD25A" {stroke(3)}/></g>')
    return c, (1.0, 960, 560)


def s104(t, T, fr):
    c = bg_cottage_garden(t, "sunset", insects=False)
    land = ease(seg(t, 0.2 * T, 0.6 * T))
    c += daisy(1360, 1060, 1.8, t, 1, col="#F6A6B8", stem=130)
    c += pp(1060, 1060, 1.3, t, T, arms=(20, 70), mouth="grin" if land > 0.95 else "smile", look=(10, -2))
    c += honeybee(lerp(1800, 1370, land), lerp(300, 790, land), 0.6, fr if land < 1 else 0, flip=True, flap=land < 1)
    c += sparkle(1450, 720, seg(t, 0.62 * T, T), 34, "#FFF3C4")
    return c, cam_push(t, T, 1.0, 1.12, 1200, 760)


def s105(t, T, fr):
    wave = math.sin(t * 7) * 20 if t > 0.1 * T else 0
    c = bg_cottage_garden(t, "sunrise", insects=False)
    sil = [(lambda x, y: vulture_sil(x, y, 0.9), 1300, 300), (lambda x, y: bat(x, y, 1.0, fr), 1560, 400), (lambda x, y: spider(x, y, 1.4, t), 1760, 580)]
    for k, (fn, x, y) in enumerate(sil):
        p = seg(t, 0.15 * T + k * 0.12 * T, 0.3 * T + k * 0.12 * T)
        if p > 0:
            c += (f'<g opacity="0.9" transform="translate({x} {y}) scale({ease_out_back(p):.3f}) translate({-x} {-y})"><g filter="url(#sil2)">{fn(x, y)}</g></g>' + text(x + 70, y - 50, "?", 80, MUSTARD, outline=INK))
    c = '<defs><filter id="sil2"><feColorMatrix type="matrix" values="0 0 0 0 0.17  0 0 0 0 0.14  0 0 0 0 0.12  0 0 0 1 0"/></filter></defs>' + c
    c += pp(820, 1060, 1.3, t, T, mouth="grin", arms=(15, 140 + wave), look=(4, -2))
    return c, (1.0, 960, 560)


SCENES = {i: globals()[f"s{i:03d}"] for i in range(71, 106)}
KEYFRAME = {82: 0.9, 90: 0.95, 78: 0.7, 88: 0.55, 99: 0.6}
