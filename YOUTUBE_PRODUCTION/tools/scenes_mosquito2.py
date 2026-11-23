"""Scenes 011-048: Why it matters, How a mosquito finds you, Ancient survivor, Never think about, The water, Night shift."""
import math
from draw import *
from draw2 import *
import scenes_mosquito as S1


def pp(x, y, s, t, T, **kw):
    kw.setdefault("eyes", auto_eyes(t, T))
    return pip(x, y, s, **kw)


def cam_push(t, T, a=1.0, b=1.06, cx=960, cy=540):
    return (lerp(a, b, ease(t / T)), cx, cy)


def cam_pan(t, T, x0, x1, s=1.0, cy=540):
    return (s, lerp(x0, x1, ease(t / T)), cy)


# ---------------- WHY MOSQUITOES MATTER ----------------
def s011(t, T, fr):
    flip = seg(t, 0.25 * T, 0.45 * T)
    nb = (f'<g transform="translate(1110 660)"><rect x="-70" y="-50" width="140" height="100" rx="8" fill="#F6F0E2" {stroke(5)}/>'
          f'<path d="M0 -50 L0 50" {stroke(4)}/><path d="M-50 -20 L-14 -20 M-50 0 L-20 0 M14 -20 L50 -20 M14 0 L44 0" stroke="#B5A88E" stroke-width="6" stroke-linecap="round"/>'
          f'<path d="M0 -50 Q{lerp(60, -60, flip):.0f} -70 {lerp(70, -70, flip):.0f} {lerp(-50, -50, flip):.0f} L{lerp(70, -70, flip):.0f} 50 Q{lerp(60, -60, flip):.0f} 30 0 50 Z" fill="#FFFBF0" {stroke(4)} opacity="{1 if 0 < flip < 1 else 0}"/></g>')
    path = f'<path d="M700 1100 Q900 800 960 700 Q1020 800 1220 1100 Z" fill="#C9A77C" {stroke(5)}/>'
    body = pp(960, 960, 1.15, t, T, arms=(20, 62), mouth="smile", look=(4, 6), bob=4 * math.sin(t * 6))
    return S1.bg_sunrise() + path + body + nb, cam_push(t, T, 1.0, 1.06, 980, 600)


def s012(t, T, fr):
    drop = ease_out_bounce(seg(t, 0.3 * T, 0.7 * T))
    content = sky("#BFD9D6", "#E9F1EE", "pod") + podium(960, 920)
    content += shark(760, 690, 0.55, t) + snake(1160, 780, 0.45, t)
    content += mosquito(960, 600 + 6 * math.sin(t * 4), 0.9, frame=fr, look=(0, 2))
    content += medal(960, lerp(260, 640, drop), 0.9)
    content += sparkle(1060, 520, seg(t, 0.72 * T, T), 34)
    return content, cam_push(t, T, 1.0, 1.12, 960, 620)


def s013(t, T, fr):
    lift = 14 * math.sin(t * 5) if t > 0.3 * T else 0
    content = sky("#A9C29A", "#DCE6C8", "blur") + "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#FFFFFF" opacity="0.18"/>' for x, y, r in [(300, 300, 120), (1500, 200, 160), (1700, 800, 140), (500, 850, 100)])
    content += (f'<path d="M300 1200 Q520 760 760 700 Q940 660 1080 720" fill="none" stroke="{INK}" stroke-width="40" stroke-linecap="round"/>'
                f'<path d="M300 1200 Q520 760 760 700 Q940 660 1080 720" fill="none" stroke="{INK}" stroke-width="22" stroke-linecap="round"/>'
                f'<circle cx="1180" cy="700" r="150" fill="{SKIN_PIP}" {stroke(10)}/>')
    content += mosquito(1200, 520 - lift * 0.2, 1.5, frame=fr, look=(-2, 3), rot=-4)
    if t > 0.3 * T:
        content += f'<path d="M1230 560 l40 -50" stroke="{INK}" stroke-width="5" stroke-linecap="round" transform="rotate({lift:.1f} 1230 560)"/>'
    return content, cam_push(t, T, 1.0, 1.04, 1100, 560)


def s014(t, T, fr):
    heat = 0.5 + 0.5 * math.sin(t * 3)
    content = f'<rect x="-600" y="-400" width="3200" height="1900" fill="#355E66"/>' + "".join(
        f'<path d="M{x} {y} q40 -10 80 0" stroke="#4D7880" stroke-width="5" fill="none"/>' for x in range(0, 1900, 220) for y in range(80, 1080, 160))
    content += africa_map(900, 560, 1.4, heat)
    for k in range(12):
        p = seg(t, 0.2 * T + k * 0.05 * T, 0.3 * T + k * 0.05 * T)
        if p > 0:
            content += person_icon(1380 + (k % 4) * 90, 380 + (k // 4) * 130, 0.9, "#F6F0E2", p)
    return content, cam_push(t, T, 1.0, 1.05, 960, 540)


def s015(t, T, fr):
    g = ease(seg(t, 0.25 * T, 0.6 * T))
    bars = ""
    heights = [140, 180, 160, 230, 260]
    for k, (yr, h) in enumerate(zip(["2015", "2017", "2019", "2023", "2024"], heights)):
        x = 380 + k * 270
        hh = h if k < 4 else lerp(80, 620, g)
        col = "#F4F6F4" if k < 4 else MUSTARD
        bars += f'<rect x="{x}" y="{840 - hh:.0f}" width="150" height="{hh:.0f}" fill="none" stroke="{col}" stroke-width="8"/>'
        bars += f'<path d="M{x + 10} {840 - hh + 20:.0f} L{x + 140} {840 - 20:.0f}" stroke="{col}" stroke-width="3" opacity="0.4"/>'
        bars += text(x + 75, 890, yr, 44, "#F4F6F4", weight=700)
    top = 840 - lerp(80, 620, g)
    content = bg_chalkboard() + f'<path d="M320 840 L1660 840 M320 840 L320 160" stroke="#F4F6F4" stroke-width="6"/>' + bars
    content += mosquito(1530, top - 40 + 4 * math.sin(t * 5), 0.75, frame=fr, look=(-2, 2))
    content += text(560, 220, "DENGUE CASES", 56, "#F4F6F4", weight=800)
    return content, (1.0, 960, 540)


def s016(t, T, fr):
    names = [("ZIKA", "#D96C8A"), ("YELLOW FEVER", "#E6C27A"), ("WEST NILE", "#9DB8D6"), ("CHIKUNGUNYA", "#9CC5A1")]
    content = S1.bg_lab()
    for k, (n, c) in enumerate(names):
        x = 420 + k * 380
        on = seg(t, 0.1 * T + k * 0.15 * T, 0.2 * T + k * 0.15 * T)
        content += f'<circle cx="{x}" cy="560" r="{150 * on:.0f}" fill="url(#glow)" opacity="{on:.2f}"/>'
        content += f'<rect x="{x - 110}" y="430" width="220" height="260" rx="22" fill="#E8F2F4" fill-opacity="0.6" {stroke()}/><rect x="{x - 120}" y="410" width="240" height="36" rx="8" fill="#8A5A35" {stroke(5)}/>'
        content += virus(x, 570, 0.9, c, t * (0.5 + k * 0.2))
        content += f'<rect x="{x - 120}" y="720" width="240" height="64" rx="8" fill="#F6F0E2" {stroke(5)}/>' + text(x, 766, n, 30 if len(n) > 9 else 38)
    nod = 6 * math.sin(t * 6) if t > 0.75 * T else 0
    content += pp(1720, 1000, 0.9, t, T, mouth="flat", tilt=nod, arms=(15, 15))
    return content, cam_pan(t, T, 820, 1100, 1.0)


def s017(t, T, fr):
    surprised = t > 0.35 * T
    content = bg_meadow(t)
    content += flower(1240, 1000, 3.0, "#E58FA6", t * 0.3, 1)
    content += mosquito(1235, 560 + 4 * math.sin(t * 3), 1.2, frame=fr, rot=60, look=(2, 3), flip=True)
    content += pp(720, 1040, 1.4, t, T, mouth="o" if surprised else "smile", arms=(60, 60) if surprised else (15, 15),
                  tilt=-8 if surprised else 0, look=(8, 2))
    return content, (1.0, 960, 540)


# ---------------- HOW A MOSQUITO FINDS YOU ----------------
def s018(t, T, fr):
    px = lerp(600, 1300, t / T)
    content = bg_backyard_dusk(t)
    content += pp(px, 980, 1.0, t, T, mouth="smile", arms=(20 + 10 * math.sin(t * 6), 20 - 10 * math.sin(t * 6)), bob=5 * abs(math.sin(t * 6)))
    content += mosquito(px - 300 + 20 * math.sin(t * 3), 640 + 25 * math.sin(t * 5), 0.4, frame=fr)
    return content, cam_pan(t, T, 760, 1160, 1.0)


def s019(t, T, fr):
    content = bg_backyard_dusk(t, 0.25)
    breath = 0.5 + 0.5 * math.sin(t * 2.2)
    content += plume(640, 470, 1780, 330 + 30 * math.sin(t), t, width=lerp(40, 90, breath), op=0.45)
    content += pp(480, 1000, 1.3, t, T, mouth="o" if breath > 0.5 else "smile", look=(8, 0), arms=(15, 15))
    u = ease(seg(t, 0.2 * T, 0.95 * T))
    mx = lerp(1760, 900, u)
    my = 340 + 30 * math.sin(u * 9 - t * 3) * (1 - u) + lerp(0, 120, u)
    content += mosquito(mx, my, 0.65, frame=fr, flip=True, look=(-3, 1))
    return content, cam_push(t, T, 1.0, 1.04, 1000, 540)


def s020(t, T, fr):
    content = bg_backyard_dusk(t, 0.35)
    content += f'<path d="M-100 820 Q600 640 1500 700" fill="none" stroke="{INK}" stroke-width="44" stroke-linecap="round"/><circle cx="1540" cy="700" r="70" fill="{SKIN_PIP}" {stroke(8)}/>'
    p_smell = seg(t, 0.15 * T, 0.55 * T)
    p_heat = seg(t, 0.55 * T, 0.95 * T)
    if 0 < p_smell:
        content += f'<g opacity="{min(1, p_smell * 3) * (1 - 0.6 * p_heat):.2f}">' + scent(560, 660, t, 4) + scent(1100, 640, t + 1, 3) + '</g>'
    if p_heat > 0:
        content += f'<g opacity="{min(1, p_heat * 3):.2f}">' + heat_waves(800, 620, t, 4) + heat_waves(1250, 620, t + 0.5, 3) + '</g>'
    mx = lerp(1700, 1080, ease(t / T)); my = lerp(260, 470, ease(t / T))
    content += mosquito(mx + 10 * math.sin(t * 7), my, 1.1, frame=fr, flip=True, look=(-3, 3))
    return content, cam_push(t, T, 1.0, 1.08, 1100, 560)


def s021(t, T, fr):
    content = bg_paper()
    conv = ease(seg(t, 0.6 * T, 0.9 * T))
    tgt = seg(t, 0.75 * T, T)
    pos = [(460, 300), (960, 220), (1460, 300)]
    for k, (inner, (x, y)) in enumerate(zip([ICON_BREATH, ICON_SMELL, ICON_HEAT], pos)):
        x2, y2 = lerp(x, 960, conv), lerp(y, 640, conv)
        content += icon_circle(x2, y2, inner, lerp(1.0, 0.5, conv), p=seg(t, 0.05 * T + k * 0.15 * T, 0.2 * T + k * 0.15 * T))
    if tgt > 0:
        for r_, c in [(320, RED), (240, "#F6F0E2"), (160, RED)]:
            content += f'<circle cx="960" cy="640" r="{r_ * ease_out_back(tgt):.0f}" fill="none" stroke="{c}" stroke-width="18" opacity="0.8"/>'
    content += pp(960, 1000, 0.95, t, T, mouth="o" if tgt > 0.3 else "smile", arms=(15, 15))
    return content, (1.0, 960, 540)


# ---------------- AN ANCIENT SURVIVOR ----------------
def s022(t, T, fr):
    up = ease_out_back(seg(t, 0.1 * T, 0.45 * T))
    ang = lerp(15, 150, up)
    hx = 860 + 1.4 * (30 + 118 * math.sin(math.radians(ang)))
    hy = 1080 + 1.4 * (-250 + 118 * math.cos(math.radians(ang)))
    content = f'<rect x="-600" y="-400" width="3200" height="1900" fill="#D9C9A8"/><rect x="-600" y="860" width="3200" height="700" fill="#A88A66" {stroke()}/>'
    content += "".join(f'<rect x="{x}" y="200" width="260" height="320" rx="8" fill="#EADFC6" {stroke(5)}/>' for x in (120, 1540))
    content += pp(860, 1080, 1.4, t, T, arms=(15, ang), mouth="o" if up > 0.6 else "smile", look=(6, -6))
    content += amber(hx + 10, hy - 60, 0.45, glow=0.5 + 0.5 * math.sin(t * 4), inner=True)
    return content, cam_push(t, T, 1.0, 1.06, 960, 520)


def s023(t, T, fr):
    content = sky("#5E4E66", "#E39B6A", "pre")
    content += "".join(f'<path d="M{x} 900 Q{x - 60} 700 {x - 160} 640 M{x} 900 Q{x + 60} 700 {x + 160} 650" fill="none" stroke="#3E5E46" stroke-width="26" stroke-linecap="round"/>' for x in range(0, 2000, 300))
    content += f'<path d="M-600 900 Q900 840 2600 900 L2600 1600 L-600 1600 Z" fill="#4D5E3E" {stroke()}/>'
    content += dinosaur(lerp(-300, 900, t / T), 820, 1.2, "#2E2A3A", t * 3)
    content += amber(1280, 560, 1.6, glow=0.5 + 0.5 * math.sin(t * 3))
    return content, (1.0, 960, 540)


def s024(t, T, fr):
    content = S1.bg_lab()
    content += S1.desk(500, 700, 1000)
    content += (f'<path d="M620 700 L700 560 L1380 540 L1420 700 Z" fill="#8E8A86" {stroke()}/>'
                f'<path d="M700 600 L1360 590 M680 650 L1400 640" stroke="#77736F" stroke-width="5"/>')
    glow = 0.5 + 0.5 * math.sin(t * 4)
    content += f'<g opacity="0.7">{mosquito(1040, 620, 1.2, frame=0, flap=False)}</g>'
    content += f'<ellipse cx="985" cy="628" rx="{40 + 8 * glow:.0f}" ry="16" fill="{RED}" opacity="{0.35 + 0.35 * glow:.2f}" transform="rotate(-10 985 628)"/>'
    mx = lerp(1300, 1060, ease(seg(t, 0.2 * T, 0.6 * T)))
    content += person(1650, 1000, 1.2, skin="#F3D9C0", outfit="coat", outfit_color="#F4F4F0", arms=(15, 70), hair_style="tuft",
                      hair_color="#C8C6C0", mouth="o", eyes=auto_eyes(t, T), look=(-8, 4), flip=True)
    content += magnifier(mx - 140, 560, 1.0, 0)
    return content, cam_push(t, T, 1.0, 1.1, 1060, 600)


def s025(t, T, fr):
    content = bg_paper()
    panels = [("#E9F1F4", "ice"), ("#2E2A3A", "asteroid"), ("#CFE0C0", "drift")]
    for k, (c, kind) in enumerate(panels):
        x = 140 + k * 620
        content += f'<rect x="{x}" y="260" width="560" height="460" rx="18" fill="{c}" {stroke()}/>'
        if kind == "ice":
            content += f'<path d="{"M" + str(x)} 720 L{x + 80} 520 L{x + 200} 600 L{x + 320} 460 L{x + 460} 580 L{x + 560} 500 L{x + 560} 720 Z" fill="#FFFFFF" {stroke(5)}/>'
        elif kind == "asteroid":
            content += f'<path d="M{x + 120} 360 L{x + 400} 600" stroke="#F2A76B" stroke-width="40" stroke-linecap="round" opacity="0.7"/><circle cx="{x + 400}" cy="600" r="54" fill="#8A6A4E" {stroke()}/>'
        else:
            content += f'<path d="M{x + 60} 420 Q{x + 160} 360 {x + 230} 440 Q{x + 200} 560 {x + 100} 560 Z" fill="#7FA65A" {stroke(5)}/><path d="M{x + 320} 380 Q{x + 460} 400 {x + 480} 520 Q{x + 400} 640 {x + 300} 560 Z" fill="#7FA65A" {stroke(5)}/>'
    u = seg(t, 0.05 * T, 0.8 * T)
    xs = lerp(420, 1600, u)
    hop = abs(math.sin(u * math.pi * 3)) * 160
    gone = seg(t, 0.82 * T, 0.95 * T)
    if gone <= 0:
        content += mosquito(xs, 230 - hop, 0.9, frame=fr)
    content += puff(1620, 230, gone, 60)
    return content, cam_pan(t, T, 700, 1220, 1.0)


# ---------------- NEVER THINK ABOUT ----------------
RED_SET = {3, 18, 27, 40, 41, 55, 66, 71, 88, 97, 102, 115, 120, 131, 140, 152}


def s026(t, T, fr):
    content = bg_paper() + grid_icons(150, 130, 17, 9, 100, RED_SET, fr, 0.28, red_p=seg(t, 0.3 * T, 0.6 * T))
    return content, cam_push(t, T, 1.08, 1.0, 960, 540)


def s027(t, T, fr):
    fade = seg(t, 0.1 * T, 0.5 * T)
    keep = {41, 102}
    content = bg_paper() + grid_icons(150, 130, 17, 9, 100, keep, fr, 0.28, red_p=1.0)
    for k in RED_SET - keep:
        x, y = 150 + (k % 17) * 100, 130 + (k // 17) * 100
        content += f'<circle cx="{x}" cy="{y - 4}" r="30" fill="{RED}" opacity="{0.55 * (1 - fade):.2f}"/>'
    return content, (lerp(1.0, 1.5, ease(seg(t, 0.5 * T, T))), 760, 400)


def s028(t, T, fr):
    content = bg_underwater(t, surface=640)
    n = int(lerp(0, 40, seg(t, 0.2 * T, 0.9 * T)))
    content += egg_raft(1180, 620, n, 1.6)
    content += mosquito(760, 560 + 6 * math.sin(t * 3), 1.6, frame=fr, look=(4, 3))
    return content, cam_push(t, T, 1.0, 1.06, 960, 560)


def s029(t, T, fr):
    content = bg_meadow(t)
    content += flower(1000, 1100, 4.2, "#F2B33D", t * 0.3, 2)
    bliss = "closed" if t > 0.3 * T else "open"
    m = mosquito(990, 450 + 5 * math.sin(t * 2), 1.4, frame=fr, look=(2, 3))
    m = m.replace('<path d="M34 -22 Q44 -40 56 -38 M30 -24 Q34 -44 46 -48" stroke="#2B2420" stroke-width="2.5" fill="none"/>',
                  '<path d="M34 -22 Q44 -40 56 -38 M30 -24 Q34 -44 46 -48" stroke="#2B2420" stroke-width="7" fill="none" stroke-dasharray="3 3"/>')
    content += m
    content += sparkle(1160, 340, seg(t, 0.4 * T, 0.9 * T), 26, "#FFF3C4")
    return content, cam_push(t, T, 1.0, 1.08, 1000, 480)


def s030(t, T, fr):
    content = f'<rect x="-600" y="-400" width="3200" height="1900" fill="#B98B5E"/>' + "".join(f'<path d="M-600 {y} L2600 {y + 20}" stroke="#A67A50" stroke-width="5"/>' for y in range(-100, 1300, 90))
    content += f'<rect x="360" y="120" width="1200" height="860" fill="#FFFBF0" transform="rotate(-2 960 550)" {stroke()}/>'
    r = rnd(4)
    for k in range(18):
        content += f'<g opacity="0.85">{tiny_mosquito(480 + (k % 6) * 180, 260 + (k // 6) * 240, 2.0, frame=0, rot=r.uniform(-20, 20))}</g>'
    hv = 30 * math.sin(t * 3)
    ex, ey = 1000 + hv, 470 + 20 * math.sin(t * 5)
    content += (f'<g transform="translate({ex:.0f} {ey:.0f}) rotate(-20)"><rect x="-160" y="-70" width="320" height="140" rx="20" fill="#F2A3A0" {stroke()}/>'
                f'<rect x="-160" y="-70" width="110" height="140" rx="20" fill="#5B8DB8" {stroke()}/></g>')
    content += f'<path d="M{ex + 120:.0f} {ey + 20:.0f} Q1500 800 1900 1200" fill="none" stroke="{INK}" stroke-width="40" stroke-linecap="round"/><circle cx="{ex + 110:.0f}" cy="{ey + 10:.0f}" r="56" fill="{SKIN_PIP}" {stroke(8)}/>'
    return content, (1.0, 960, 540)


def s031(t, T, fr):
    content = f'<rect x="-600" y="-400" width="3200" height="1900" fill="#3A3550"/><circle cx="960" cy="420" r="700" fill="url(#glow)" opacity="0.5"/>'
    content += pp(900, 1300, 2.2, t, T, arms=(15, 150), mouth="flat", look=(6, -8), tilt=-8 * ease(seg(t, 0.1 * T, 0.5 * T)))
    content += question_mark(1380, 360 + 14 * math.sin(t * 4), 1.6)
    return content, cam_push(t, T, 1.0, 1.06, 960, 520)


# ---------------- THE WATER ----------------
def s032(t, T, fr):
    tilt = ease(seg(t, 0.4 * T, 0.95 * T))
    content = sky("#BFD9D6", "#F3E6C4", "pe") + f'<rect x="-600" y="700" width="3200" height="200" fill="#8FB27A" {stroke()}/>'
    content += bg_underwater(t, surface=860, bottom=1900).replace('<rect x="-600" y="-400" width="3200" height="1900" fill="url(#uwsky)"/>', '')
    content += "".join(f'<path d="M{x} 870 L{x + 10} 640" stroke="{INK}" stroke-width="5"/><rect x="{x + 2}" y="620" width="16" height="44" rx="8" fill="#8A5A35" {stroke(4)}/>' for x in range(1200, 1900, 50))
    content += person(700, 860, 1.1, outfit="vest", outfit_color=OLIVE, arms=(60, 95), mouth="o", hat="bucket", glasses=True, look=(6, 8),
                      eyes=auto_eyes(t, T), legs=True, tilt=12)
    content += magnifier(860, 770, 0.6, 20)
    content += "".join(larva(1000 + k * 120, 870, 0.5, t, k) for k in range(6))
    return content, (lerp(1.0, 1.25, tilt), 960, lerp(540, 1100, tilt))


def s033(t, T, fr):
    content = bg_underwater(t, surface=520)
    n = int(lerp(0, 56, seg(t, 0.15 * T, 0.9 * T)))
    content += egg_raft(960, 506, n, 2.0)
    content += mosquito(1000 + 30 * math.sin(t), 380 + 10 * math.sin(t * 3), 1.4, frame=fr, look=(-2, 4), rot=-10)
    content += "".join(f'<ellipse cx="960" cy="520" rx="{60 + ((t * 120 + k * 80) % 300):.0f}" ry="{(60 + ((t * 120 + k * 80) % 300)) * 0.12:.0f}" fill="none" stroke="#E9F4F2" stroke-width="4" opacity="{1 - ((t * 120 + k * 80) % 300) / 300:.2f}"/>' for k in range(3))
    return content, cam_push(t, T, 1.0, 1.1, 960, 520)


def s034(t, T, fr):
    rain = seg(t, 0.3 * T, T)
    content = sky("#8C99A6" if rain else "#D9CBB0", "#C9C6C0" if rain else "#F3E6C4", "bk" + str(int(rain > 0)))
    content += f'<rect x="-600" y="860" width="3200" height="700" fill="#8A7A5E" {stroke()}/>'
    content += bucket(960, 900, 2.0, water=ease(seg(t, 0.4 * T, T)) * 0.8)
    if rain > 0:
        r = rnd(5)
        content += "".join(f'<path d="M{(r.uniform(-200, 2100) + t * 200) % 2200 - 100:.0f} {(r.uniform(0, 1100) + t * 900) % 1100:.0f} l-14 46" stroke="#DCE6EA" stroke-width="5" stroke-linecap="round" opacity="0.8"/>' for _ in range(70))
    return content, cam_push(t, T, 1.0, 1.05, 960, 600)


def s035(t, T, fr):
    content = bg_underwater(t, surface=170)
    content += "".join(larva(300 + k * 190, 170, 0.9, t, k) for k in range(7))
    content += f'<circle cx="1620" cy="720" r="210" fill="#F3E6C4" {stroke()}/>' + tyre(1620, 740, 1.2)
    return content, cam_pan(t, T, 860, 1060, 1.0)


def s036(t, T, fr):
    content = bg_underwater(t, surface=-200)
    r = rnd(8)
    for k in range(26):
        u = ((t * 0.25 + k / 26) % 1)
        x = lerp(1900, 1000, u) + 40 * math.sin(k)
        y = 420 + r.uniform(-200, 260) * (1 - u)
        content += f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r.uniform(5, 12):.0f}" fill="#9C8A5E" opacity="{1 - u:.2f}"/>'
    content += f'<path d="M{lerp(1700, 1120, (t / T)):.0f} 300 q40 -30 80 0 q-40 30 -80 0 Z" fill="#8A6A4E" {stroke(4)}/>'
    content += larva(900, 0, 3.0, t, 0)
    return content, cam_push(t, T, 1.0, 1.04, 960, 540)


def s037(t, T, fr):
    content = bg_underwater(t, surface=120)
    yy = 520 + 160 * math.sin(t * 1.6)
    content += pupa(960, yy, 2.4, r=(t * 140) % 360 if (t % 2.4) < 1.0 else 0)
    return content, (1.0, 960, 540)


def s038(t, T, fr):
    content = bg_underwater(t, surface=640)
    p = seg(t, 0.1 * T, 0.55 * T)
    fly = seg(t, 0.6 * T, 0.9 * T)
    content += pupa(900, 690, 1.6, r=-20)
    if p > 0:
        content += mosquito(lerp(900, 980, p) + lerp(0, 600, fly), lerp(700, 610, p) - 420 * ease(fly), 1.3, frame=fr if fly > 0 else 0, flap=fly > 0, rot=lerp(-60, 0, p))
    content += calendar(1620, 280, 0.9, "7-14", flip=abs(math.sin(t * 5)) if t > 0.5 * T else 0)
    content += text(1620, 430, "days", 44)
    return content, (1.0, 960, 540)


def s039(t, T, fr):
    u = ease(seg(t, 0, 0.8 * T))
    content = bg_underwater(t, surface=170)
    content += "".join(larva(820 + k * 140, 170, 0.8, t, k) for k in range(5))
    content += fish(lerp(-200, 420, u), 640, 1.4, t)
    content += nymph(lerp(2200, 1640, u), 860, 1.2, t)
    content += tadpole(lerp(2100, 1500, u), 520, 1.2, t)
    return content, cam_push(t, T, 1.0, 1.05, 960, 540)


def s040(t, T, fr):
    content = bg_underwater(t, surface=170)
    look = 1 if math.sin(t * 2) > 0 else 0
    content += fish(900, 600, 2.0, t, flip=bool(look))
    content += question_mark(1300, 400 + 10 * math.sin(t * 3), 1.0)
    return content, (1.0, 960, 540)


def s041(t, T, fr):
    gulp = seg(t, 0.45 * T, 0.6 * T)
    content = bg_underwater(t, surface=170)
    fx = lerp(500, 780, ease(seg(t, 0.1 * T, 0.5 * T)))
    content += fish(fx, 600, 2.0, t, mouth_open=math.sin(gulp * math.pi))
    if gulp < 0.6:
        content += f'<g transform="translate(1090 610)"><ellipse rx="30" ry="22" fill="#D8B48A" {stroke(4)}/><path d="M-20 -10 l-20 -20 M20 -10 l20 -20" {stroke(3)}/></g>'
    content += sparkle(1150, 420, seg(t, 0.62 * T, T), 30, "#FFF3C4")
    return content, (1.0, 960, 540)


def s042(t, T, fr):
    content = bg_underwater(t, surface=170)
    r = rnd(12)
    for k in range(18):
        p = seg(t, k * 0.03 * T, 0.5 * T + k * 0.02 * T)
        x0, y0 = r.uniform(-200, 2100), r.uniform(250, 900)
        x = lerp(x0 + (600 if x0 > 960 else -600), x0, ease(p))
        if k % 2:
            content += f'<g transform="translate({x:.0f} {y0:.0f}) rotate({20 * math.sin(t * 3 + k):.1f})"><path d="M0 -40 Q12 0 0 40" fill="none" stroke="#B5543F" stroke-width="14" stroke-linecap="round"/></g>'
        else:
            content += f'<g transform="translate({x:.0f} {y0:.0f})"><ellipse rx="24" ry="18" fill="#D8B48A" {stroke(4)}/><path d="M-12 -12 l-18 -18 M12 -12 l18 -18" {stroke(3)}/><circle cx="8" cy="-4" r="4" fill="{INK}"/></g>'
    return content, cam_push(t, T, 1.08, 1.0, 960, 540)


def s043(t, T, fr):
    content = sky("#A9B89A", "#DCD6BC", "bog") + f'<rect x="-600" y="800" width="3200" height="800" fill="#6E8B5A" {stroke()}/>'
    for x in (300, 1650):
        content += f'<path d="M{x - 60} 820 Q{x - 80} 600 {x - 50} 420 L{x + 50} 420 Q{x + 80} 600 {x + 60} 820 Z" fill="#A85A5A" {stroke()}/>'
    content += (f'<path d="M760 980 Q700 560 790 260 L1130 260 Q1220 560 1160 980 Z" fill="#B5655E" {stroke()}/>'
                f'<path d="M800 560 Q960 590 1120 560 L1130 900 Q960 960 790 900 Z" fill="#7FB4BE" {stroke(5)}/>'
                f'<path d="M760 260 Q960 160 1160 260 Q960 300 760 260 Z" fill="#C9786E" {stroke()}/>')
    content += "".join(larva(860 + k * 70, 570, 0.4, t, k) for k in range(4))
    content += question_mark(1340, 330 + 12 * math.sin(t * 3), 1.2)
    return content, cam_push(t, T, 1.0, 1.08, 960, 560)


# ---------------- NIGHT SHIFT ----------------
def swarm(cx, cy, n, t, fr, spread=300, s=0.6, seed=2):
    r = rnd(seed)
    out = ""
    for k in range(n):
        a = r.uniform(0, 6.28); d = r.uniform(0, spread)
        x = cx + d * math.cos(a + t * 0.6) + 10 * math.sin(t * 5 + k)
        y = cy + d * 0.5 * math.sin(a + t * 0.6) + 8 * math.cos(t * 6 + k)
        out += tiny_mosquito(x, y, s, frame=fr + k)
    return out


def s044(t, T, fr):
    content = bg_meadow(t, dusk=True)
    rise = ease(seg(t, 0, 0.9 * T))
    content += swarm(960, lerp(900, 520, rise), 40, t, fr, 420, 0.7)
    return content, (1.0, 960, lerp(600, 520, ease(t / T)))


def s045(t, T, fr):
    content = bg_meadow(t, dusk=True) + web(260, 300, 1.3) + spider(260, 300, 0.7, t)
    content += swarm(1000, 500, 30, t, fr, 380, 0.65)
    u = seg(t, 0.05 * T, 0.45 * T)
    content += dragonfly(lerp(-200, 2200, u), 520 + 80 * math.sin(u * 6), 1.1, fr)
    v = seg(t, 0.5 * T, 0.95 * T)
    content += bird(lerp(2200, -200, v), 300 + 220 * math.sin(v * math.pi), 1.0, fr, flip=True, col="#2E3A57")
    return content, (1.0, 960, 540)


def s046(t, T, fr):
    content = bg_night(t)
    content += swarm(1000, 560, 30, t, fr, 380, 0.6, seed=4)
    u = ease(seg(t, 0.05 * T, 0.75 * T))
    content += bat(lerp(-100, 1100, u), 520 + 60 * math.sin(t * 4), 1.3, fr)
    content += question_mark(1500, 520 + 10 * math.sin(t * 3), 1.2)
    return content, (1.0, 960, 540)


def s047(t, T, fr):
    content = f'<rect x="-600" y="-400" width="3200" height="1900" fill="#2E3A57"/>'
    content += (f'<path d="M-100 1100 L300 200 L1100 200 L1500 1100 Z" fill="#C9B07E" {stroke()}/>'
                f'<circle cx="640" cy="320" r="40" fill="#F7D488" {stroke(5)}/><circle cx="640" cy="320" r="200" fill="url(#glow)" opacity="0.8"/>')
    content += person(420, 1000, 1.2, skin="#8D5A3B", outfit="coat", outfit_color="#F4F4F0", arms=(15, 75), hair_style="bun",
                      hair_color="#1F1A17", mouth="smile", eyes=auto_eyes(t, T), look=(8, 2))
    content += f'<ellipse cx="1200" cy="620" rx="380" ry="300" fill="#F6F0E2" {stroke()}/><ellipse cx="1200" cy="620" rx="290" ry="220" fill="none" stroke="#C8BFA8" stroke-width="6"/>'
    content += icon_circle(1080, 560, moth(0, 0, 0.55, fr), 1.0, "none", seg(t, 0.25 * T, 0.4 * T)).replace('fill="none"', 'fill="none" opacity="0"', 1)
    content += icon_circle(1290, 650, beetle(0, 0, 0.9), 1.0, "none", seg(t, 0.4 * T, 0.55 * T)).replace('fill="none"', 'fill="none" opacity="0"', 1)
    content += icon_circle(1500, 430, tiny_mosquito(0, 0, 1.6, frame=fr), 0.6, "none", seg(t, 0.6 * T, 0.75 * T)).replace('fill="none"', 'fill="none" opacity="0"', 1)
    return content, cam_push(t, T, 1.0, 1.05, 960, 560)


def s048(t, T, fr):
    content = bg_night(t, trees=False)
    content += f'<path d="M-200 520 Q900 470 2100 540" fill="none" stroke="#5A3A28" stroke-width="40" stroke-linecap="round"/>'
    chew = abs(math.sin(t * 8)) if t > 0.2 * T else 0
    content += (f'<g transform="translate(960 640) rotate(180)">{bat(0, 0, 1.6, 0, mouth="o" if chew > 0.5 else "smile").replace("rotate(0.00)", "")}</g>')
    content += f'<g transform="translate(860 {720 + 6 * chew:.0f}) rotate(180)">{moth(0, 0, 0.45, 0)}</g>'
    content += tiny_mosquito(1120, 700, 1.4, frame=0, rot=150)
    return content, cam_push(t, T, 1.0, 1.08, 960, 620)


SCENES = {i: globals()[f"s{i:03d}"] for i in range(11, 49)}
