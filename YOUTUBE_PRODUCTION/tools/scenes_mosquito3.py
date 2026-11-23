"""Scenes 049-098: Arctic, Flowers, Humans, We've tried this before, Could we do it, Risks, Conclusion, Outro."""
import math
from draw import *
from draw2 import *
import scenes_mosquito as S1
from scenes_mosquito2 import pp, cam_push, cam_pan, swarm


def parka_pip(x, y, s, t, T, **kw):
    kw.setdefault("outfit_color", "#B5543F")
    return pp(x, y, s, t, T, **kw)


# ---------------- ARCTIC ----------------
def s049(t, T, fr):
    u = ease(seg(t, 0.05 * T, 0.6 * T))
    content = bg_paper("#E9E2CF")
    content += (f'<path d="M300 900 Q500 700 700 760 Q900 620 1100 700 Q1300 560 1600 640 L1700 1000 L250 1000 Z" fill="#C9D6C0" {stroke()}/>'
                f'<path d="M200 300 Q600 160 1000 220 Q1400 140 1760 260 L1760 420 L200 420 Z" fill="#F4F6F4" {stroke()}/>')
    pts = [(lerp(900, 980, k / 20), lerp(900, 330, k / 20)) for k in range(21)]
    n = int(u * 20)
    content += "".join(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="9" fill="{RED}"/>' for x, y in pts[:n + 1])
    if t > 0.6 * T:
        content += parka_pip(980, 330, 0.55, t, T, mouth="smile", arms=(20, 120))
    return content, cam_push(t, T, 1.0, 1.08, 960, 520)


def s050(t, T, fr):
    g = ease(seg(t, 0, 0.9 * T))
    content = bg_tundra(t)
    dark = f'<ellipse cx="960" cy="{560 - 160 * g:.0f}" rx="{300 + 700 * g:.0f}" ry="{140 + 260 * g:.0f}" fill="#2B2420" opacity="{0.15 + 0.35 * g:.2f}"/>'
    content += dark + swarm(960, 560 - 160 * g, int(30 + 90 * g), t, fr, 300 + 600 * g, 0.55, seed=6)
    return content, cam_push(t, T, 1.0, 1.05, 960, 520)


def s051(t, T, fr):
    content = bg_tundra(t) + swarm(960, 420, 50, t, fr, 700, 0.5, seed=7)
    for k in range(3):
        u = ((t / T) + k * 0.33) % 1
        content += bird(lerp(-200, 2100, u), 360 + 140 * math.sin(u * 6 + k), 0.8, fr + k * 2, col="#8A6A4E", belly="#F3EFE6")
    return content, cam_pan(t, T, 900, 1020, 1.0)


def s052(t, T, fr):
    content = bg_tundra(t, snow=False)
    fade = seg(t, 0.35 * T, 0.75 * T)
    r = rnd(13)
    for k in range(12):
        x, y = 300 + (k % 6) * 260 + r.uniform(-40, 40), 300 + (k // 6) * 200
        op = 1 - fade if k % 2 else 1.0
        content += f'<g opacity="{op:.2f}">{bird(x + 20 * math.sin(t * 2 + k), y, 0.6, fr + k, col="#8A6A4E")}</g>'
    return content, (1.0, 960, 520)


def s053(t, T, fr):
    shrug = ease(seg(t, 0.35 * T, 0.5 * T)) * (1 - ease(seg(t, 0.8 * T, 0.92 * T)))
    content = bg_tundra(t)
    content += f'<path d="M1100 900 L1450 380 L1800 900 Z" fill="#D8A85A" {stroke()}/><path d="M1400 900 L1450 560 L1500 900 Z" fill="#8A6A4E" {stroke(5)}/>'
    content += person(820, 1060, 1.4, skin="#8D5A3B", outfit="coat", outfit_color="#7F96A8", arms=(lerp(14, 115, shrug), lerp(14, 115, shrug)),
                      hair_style="bun", hair_color="#1F1A17", mouth="flat", eyes=auto_eyes(t, T), tilt=-8 * shrug)
    content += icon_circle(420, 330, tiny_mosquito(0, 0, 2.2, frame=fr), 1.0, p=1.0) + icon_circle(1220, 300, tiny_mosquito(0, 0, 1.6, frame=fr).replace("#CFE7F2", "#E6E0D2"), 1.0, p=1.0)
    content += text(420, 470, "mosquito", 40) + text(1220, 440, "midge", 40)
    return content, (1.0, 960, 540)


def s054(t, T, fr):
    content = bg_tundra(t, snow=False)
    content += f'<path d="M900 1200 L1500 380 L2600 380 L2600 1200 Z" fill="#9C9A6A" {stroke()}/><path d="M1500 400 Q1800 330 2200 410 L2200 520 Q1800 470 1500 520 Z" fill="#F4F6F4" {stroke()}/>'
    content += f'<path d="M-200 1000 Q300 900 800 1000 L800 1300 L-200 1300 Z" fill="#7FA65A" {stroke()}/>'
    u = ease(t / T)
    for k in range(5):
        x = lerp(500 + k * 150, 1450 + k * 150, u)
        y = lerp(980 - k * 30, 520 - k * 20, u)
        content += caribou(x, y, 0.55, t, walk=t + k)
        content += swarm(x - 120, y - 150, 10, t, fr + k, 90, 0.45, seed=20 + k)
    return content, (1.0, lerp(900, 1500, u), lerp(760, 520, u))


def s055(t, T, fr):
    content = bg_tundra(t, snow=False) + f'<path d="M-600 760 L2600 760 L2600 1600 L-600 1600 Z" fill="#7FA65A" {stroke()}/>'
    for k, x in enumerate((520, 1020, 1480)):
        g = 0.5 + 0.5 * math.sin(t * 1.5 + k)
        content += caribou(x, 860 + (k % 2) * 60, 0.9, t, graze=g)
    content += "".join(flower(x, 1030, 0.5, "#F3EFE6", t, i) for i, x in enumerate(range(100, 1900, 220)))
    return content, cam_push(t, T, 1.0, 1.04, 960, 560)


def s056(t, T, fr):
    content = bg_paper("#EDE5CF")
    content += caribou(960, 560, 0.9, t, graze=0.3)
    a1 = seg(t, 0.2 * T, 0.5 * T); a2 = seg(t, 0.45 * T, 0.75 * T)
    content += f'<path d="M760 560 L{lerp(760, 420, a1):.0f} {lerp(560, 760, a1):.0f}" stroke="{RED}" stroke-width="14" stroke-linecap="round"/>'
    content += f'<path d="M1180 600 L{lerp(1180, 1500, a2):.0f} {lerp(600, 800, a2):.0f}" stroke="#4E7F5A" stroke-width="14" stroke-linecap="round"/>'
    if a1 > 0.95:
        content += wolf(320, 820, 0.8)
    if a2 > 0.95:
        content += "".join(flower(1500 + k * 90, 980, 0.8, "#F3EFE6", t, k) for k in range(3))
    return content, (1.0, 960, 560)


def s057(t, T, fr):
    content = bg_tundra(t, "#9C7FA0", "#F2A76B")
    hop = abs(math.sin(t * 4)) * 60
    content += caribou(1250, 860 - hop, 0.55, t)
    content += parka_pip(620, 1080, 1.4, t, T, mouth="smile" if t > 0.3 * T else "o", look=(8, 2), arms=(15, 25))
    content += sparkle(1300, 560, seg(t, 0.5 * T, T), 28, "#FFF3C4")
    return content, cam_push(t, T, 1.0, 1.06, 960, 560)


# ---------------- FLOWERS ----------------
def s058(t, T, fr):
    px = lerp(300, 1100, t / T)
    content = bg_forest(t)
    content += pp(px, 1040, 1.0, t, T, mouth="smile", arms=(20 + 10 * math.sin(t * 6), 20 - 10 * math.sin(t * 6)), bob=5 * abs(math.sin(t * 6)))
    return content, cam_pan(t, T, 760, 1120, 1.0)


def bog_bg(t, dusk=False):
    out = sky("#9FB5B0" if not dusk else "#5E5E80", "#E2E2C8" if not dusk else "#D89A7A", "bg2" + str(int(dusk)))
    out += "".join(spruce(x, 620, 1.0, "#5C7A64" if not dusk else "#3E4A50") for x in range(-200, 2300, 180))
    out += f'<path d="M-600 640 Q900 600 2600 650 L2600 1600 L-600 1600 Z" fill="#8FA86A" {stroke()}/>'
    out += "".join(f'<ellipse cx="{x}" cy="{y}" rx="{r}" ry="{r * 0.4:.0f}" fill="#A8BE7A" {stroke(4)}/>' for x, y, r in [(200, 960, 160), (700, 1010, 200), (1500, 980, 220), (1850, 900, 120)])
    return out


def s059(t, T, fr):
    return bog_bg(t) + orchid(960, 980, 2.1, t), cam_push(t, T, 1.0, 1.08, 960, 640)


def s060(t, T, fr):
    land = ease(seg(t, 0, 0.6 * T))
    content = bog_bg(t) + orchid(960, 980, 2.1, t)
    content += mosquito(lerp(1500, 1010, land), lerp(160, 390, land), 1.1, frame=fr if land < 1 else 0, flap=land < 1, flip=True, look=(-2, 3))
    return content, (1.1, 960, 560)


def s061(t, T, fr):
    content = bog_bg(t) + orchid(560, 1000, 1.6, t) + orchid(1380, 1000, 1.6, t + 1)
    u = (t / T)
    mx = lerp(620, 1340, ease(u)); my = 520 - 160 * math.sin(u * math.pi)
    content += scent(560, 560, t, 3, "#C9B6E4") + scent(1380, 560, t + 1, 3, "#C9B6E4")
    content += mosquito(mx, my, 0.9, frame=fr, look=(3, 2))
    content += f'<ellipse cx="{mx + 28:.0f}" cy="{my - 30:.0f}" rx="9" ry="6" fill="{MUSTARD}" {stroke(3)}/><ellipse cx="{mx + 44:.0f}" cy="{my - 26:.0f}" rx="9" ry="6" fill="{MUSTARD}" {stroke(3)}/>'
    return content, cam_pan(t, T, 860, 1060, 1.0)


def s062(t, T, fr):
    content = sky("#BFD9D6", "#F3E6C4", "farm") + hills(700, "#C9B35E", "#B59E4A", "#A9C29A")
    content += "".join(f'<path d="M{x} 1100 L{x + 20} 820" stroke="#8A7A3E" stroke-width="6"/>' + flower(x + 20, 860, 0.55, "#F3EFE6", t, x) for x in range(-100, 2100, 140))
    content += bee(500 + 40 * math.sin(t * 3), 560 + 20 * math.sin(t * 5), 1.1, fr)
    content += hoverfly(980 + 30 * math.sin(t * 4), 480, 0.9, fr)
    content += moth(1420, 520 + 20 * math.sin(t * 3), 0.55, fr)
    content += f'<g opacity="0.8">{mosquito(1760, 860, 0.6, frame=0, flap=False, look=(-4, 0))}</g>'
    return content, (1.0, 960, 540)


def s063(t, T, fr):
    droop = ease(seg(t, 0.1 * T, 0.8 * T))
    return bog_bg(t, dusk=True) + orchid(960, 1000, 2.2, t * 0.4, droop=droop), cam_push(t, T, 1.0, 1.08, 960, 620)


# ---------------- HUMANS ----------------
def s064(t, T, fr):
    turn = seg(t, 0.2 * T, 0.5 * T)
    content = town(t)
    content += pp(960, 1000, 1.4, t, T, mouth="smile", look=(lerp(-10, 0, turn), 0), arms=(15, lerp(15, 60, turn)))
    return content, cam_push(t, T, 1.0, 1.06, 960, 600)


def s065(t, T, fr):
    light = ease(seg(t, 0.1 * T, 0.5 * T))
    content = f'<rect x="-600" y="-400" width="3200" height="1900" fill="#DCE6E2"/><rect x="-600" y="820" width="3200" height="800" fill="#C9D6C8" {stroke()}/>'
    for k in range(4):
        x = 200 + k * 440
        content += (f'<rect x="{x}" y="680" width="340" height="60" rx="10" fill="#FFFFFF" {stroke()}/><rect x="{x}" y="740" width="340" height="30" fill="#9DB8D6" {stroke(5)}/>'
                    f'<path d="M{x + 20} 770 L{x + 20} 880 M{x + 320} 770 L{x + 320} 880" {stroke(6)}/><rect x="{x + 10}" y="660" width="110" height="40" rx="16" fill="#F6F0E2" {stroke(5)}/>')
        content += f'<circle cx="{x + 170}" cy="160" r="40" fill="#FFF3C4" {stroke(5)}/><circle cx="{x + 170}" cy="200" r="{260 * light:.0f}" fill="url(#glow)" opacity="{light * 0.8:.2f}"/>'
    content += f'<rect x="-600" y="-400" width="3200" height="1900" fill="#101830" opacity="{0.45 * (1 - light):.2f}"/>'
    return content, cam_pan(t, T, 860, 1100, 1.0)


def s066(t, T, fr):
    content = f'<rect x="-600" y="-400" width="3200" height="1900" fill="#B98B5E"/>' + "".join(f'<path d="M-600 {y} L2600 {y + 20}" stroke="#A67A50" stroke-width="5"/>' for y in range(-100, 1300, 90))
    for k, lab in enumerate(["MALARIA", "DENGUE", "ZIKA"]):
        x = 420 + k * 540
        content += file_card(x, 560, lab, 1.2)
        content += check(x + 120, 660, 1.0, seg(t, 0.12 * T + k * 0.22 * T, 0.25 * T + k * 0.22 * T))
    return content, (1.0, 960, 540)


def s067(t, T, fr):
    content = sky("#BFD9D6", "#F3E6C4", "sch") + f'<rect x="-600" y="840" width="3200" height="700" fill="#C9B07E" {stroke()}/>'
    content += (f'<rect x="1100" y="380" width="800" height="460" fill="#E8C9A0" {stroke()}/><path d="M1060 390 L1500 220 L1940 390 Z" fill="#B5543F" {stroke()}/>'
                f'<rect x="1440" y="640" width="120" height="200" fill="#8A5A35" {stroke(5)}/>' + "".join(f'<rect x="{x}" y="480" width="110" height="100" fill="#BFD9D6" {stroke(5)}/>' for x in (1170, 1640)))
    content += tree(300, 860, 1.0, t=t)
    skins = ["#8D5A3B", "#A86F4A", "#6B4430", "#C68E64", "#8D5A3B"]
    shirts = ["#C9563F", "#5B8DB8", MUSTARD, "#9CC5A1", "#D96C8A"]
    for k in range(5):
        x = ((t * 260 + k * 420) % 2200) - 200
        content += person(x, 1000 + (k % 2) * 40, 0.75, skin=skins[k], outfit="shirt", outfit_color=shirts[k],
                          arms=(40 + 30 * math.sin(t * 9 + k), 40 - 30 * math.sin(t * 9 + k)), mouth="grin",
                          hair_style="curly" if k % 2 else None, hair_color="#2B2420", bob=-20 * abs(math.sin(t * 9 + k)))
    return content, cam_pan(t, T, 900, 1060, 1.0)


def s068(t, T, fr):
    m = ease(seg(t, 0.3 * T, 0.7 * T))
    content = f'<rect x="-600" y="-400" width="3200" height="1900" fill="#D9CBB0"/><rect x="-600" y="860" width="3200" height="700" fill="#9C7B5B" {stroke()}/>'
    for k in range(3):
        x = 400 + k * 560
        a = f'<g opacity="{1 - m:.2f}"><rect x="{x - 150}" y="560" width="300" height="300" fill="#F4F6F4" {stroke()}/><path d="M{x - 150} 640 L{x + 150} 640 M{x - 150} 720 L{x + 150} 720" stroke="#C8BFA8" stroke-width="6"/>' \
            f'<rect x="{x + 80}" y="420" width="60" height="140" rx="10" fill="#E0533A" {stroke(5)}/></g>'
        b = (f'<g opacity="{m:.2f}"><rect x="{x - 150}" y="760" width="300" height="50" fill="#5B8DB8" {stroke(5)}/><rect x="{x - 140}" y="710" width="280" height="50" fill="#C9563F" {stroke(5)}/>'
             f'<rect x="{x - 130}" y="660" width="260" height="50" fill="{MUSTARD}" {stroke(5)}/><path d="M{x + 60} 640 L{x + 60} 500 M{x + 30} 500 L{x + 90} 500" {stroke(10)}/></g>')
        content += a + b
    content += sparkle(1200, 380, seg(t, 0.6 * T, T), 40)
    return content, (1.0, 960, 560)


def valley(t, road=0.0, clear=0.0):
    out = sky("#BFD9D6", "#E6EFD8", "val") + f'<path d="M-600 500 Q200 200 700 460 Q1200 160 1800 420 L2600 360 L2600 1600 L-600 1600 Z" fill="#5E8E5A" {stroke()}/>'
    out += f'<path d="M-600 760 Q900 600 2600 780 L2600 1600 L-600 1600 Z" fill="#6E9A5E" {stroke()}/>'
    r = rnd(21)
    for k in range(26):
        x, y = r.uniform(-200, 2100), r.uniform(520, 1040)
        gone = clear > 0 and (k % 3 != 0) and abs(x - 960) < 300 + 1000 * clear
        op = 1 - (clear if gone else 0)
        out += f'<g opacity="{op:.2f}">{palm(x, y, r.uniform(0.6, 0.9), t, k) if k % 2 else tree(x, y, r.uniform(0.6, 0.9), "#3E7A4A", t, k)}</g>'
    if road > 0:
        n = int(road * 30)
        pts = [(lerp(960, 900, k / 30) + 120 * math.sin(k / 5), lerp(1200, 520, k / 30)) for k in range(n + 1)]
        if len(pts) > 1:
            d = "M" + " L".join(f"{x:.0f} {y:.0f}" for x, y in pts)
            out += f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="{70}" stroke-linecap="round"/><path d="{d}" fill="none" stroke="#C9A77C" stroke-width="58" stroke-linecap="round"/>'
    if clear > 0:
        out += "".join(f'<rect x="{x}" y="{y}" width="{220 * clear:.0f}" height="{90 * clear:.0f}" fill="#C9B35E" {stroke(4)} opacity="{clear:.2f}"/>' for x, y in [(500, 900), (1250, 860), (1350, 980), (420, 1020)])
    return out


def s069(t, T, fr):
    return valley(t, road=ease(seg(t, 0.15 * T, 0.9 * T))), cam_push(t, T, 1.0, 1.06, 960, 700)


def s070(t, T, fr):
    return valley(t, road=1.0, clear=ease(seg(t, 0.1 * T, 0.85 * T))), (1.06, 960, 700)


def s071(t, T, fr):
    sal = ease_out_back(seg(t, 0.2 * T, 0.45 * T))
    content = sky("#9CC5A1", "#DCE6C8", "rain") + "".join(palm(x, 1100, 1.6, t, x) for x in range(-200, 2300, 260)) + "".join(tree(x, 1150, 1.4, "#3E7A4A", t, x) for x in range(-100, 2300, 330))
    content += f'<path d="M-600 1000 Q900 940 2600 1010 L2600 1600 L-600 1600 Z" fill="#4E7F5A" {stroke()}/>'
    content += mosquito(960, 600, 2.4, frame=fr, look=(0, 2))
    content += f'<g transform="translate(1040 528) rotate(-8) scale(1.2)">{ranger_hat()}</g>'
    content += f'<path d="M1010 640 Q{lerp(1060, 1100, sal):.0f} {lerp(700, 520, sal):.0f} {lerp(1070, 1110, sal):.0f} {lerp(760, 500, sal):.0f}" fill="none" stroke="{INK}" stroke-width="7" stroke-linecap="round"/>'
    return content, cam_push(t, T, 1.0, 1.08, 980, 560)


# ---------------- WE'VE TRIED THIS BEFORE ----------------
def frame_pic(x, y, inner, w=360, h=280):
    return (f'<rect x="{x - w / 2}" y="{y - h / 2}" width="{w}" height="{h}" fill="#E9DCC0" stroke="#8A5A35" stroke-width="22"/>'
            f'<rect x="{x - w / 2}" y="{y - h / 2}" width="{w}" height="{h}" fill="none" {stroke()}/>'
            f'<g filter="url(#sep)">{inner}</g>')


def s072(t, T, fr):
    content = SEPIA_DEF + f'<rect x="-600" y="-400" width="3200" height="1900" fill="#7A5A48"/><rect x="-600" y="880" width="3200" height="700" fill="#5A3A28" {stroke()}/>'
    content += frame_pic(380, 360, f'<path d="M280 420 L480 420 L450 460 L310 460 Z" fill="#6B4A35"/><path d="M380 420 L380 280 L460 400 Z" fill="#F4F6F4" {stroke(4)}/>')
    content += frame_pic(960, 330, f'<path d="M800 380 Q960 300 1120 380" fill="none" stroke="#3E7CA6" stroke-width="30"/><path d="M800 300 L1120 300" stroke="#6B4A35" stroke-width="10"/>')
    content += frame_pic(1540, 360, f'<rect x="1500" y="300" width="80" height="120" rx="16" fill="#8E8A86" {stroke(5)}/><path d="M1580 320 l60 -20" {stroke(6)}/>')
    look = math.sin(t * 1.2) * 10
    content += pp(960, 1060, 1.3, t, T, mouth="flat", look=(look, -6), arms=(15, 15))
    return content, cam_pan(t, T, 820, 1100, 1.0)


def panama_map(t, canal):
    return (f'<rect x="-600" y="-400" width="3200" height="1900" fill="#9FB8B8"/>'
            f'<path d="M-200 700 Q200 560 500 600 Q800 640 1000 520 Q1200 400 1500 460 Q1800 520 2200 380 L2200 760 Q1800 860 1500 760 Q1250 690 1050 800 Q820 920 500 860 Q200 820 -200 980 Z" fill="#C9B07E" {stroke()}/>'
            + (f'<path d="M{lerp(980, 980, 0)} 520 L{lerp(980, 1100, canal):.0f} {lerp(520, 800, canal):.0f}" stroke="#1F4E79" stroke-width="26" stroke-dasharray="34 20" stroke-linecap="round"/>' if canal > 0 else "")
            + text(400, 360, "CARIBBEAN SEA", 44, "#4E6E78") + text(1400, 980, "PACIFIC OCEAN", 44, "#4E6E78") + text(1250, 600, "PANAMA", 54, "#6B4A35"))


def s073(t, T, fr):
    canal = 0.5 * ease(seg(t, 0.1 * T, 0.45 * T))
    fade = seg(t, 0.5 * T, 0.95 * T)
    content = SEPIA_DEF + '<g filter="url(#sep)">' + panama_map(t, canal)
    for k in range(10):
        op = 1 - seg(fade, k * 0.07, k * 0.07 + 0.3)
        content += f'<g opacity="{op:.2f}">' + person(700 + (k % 5) * 80, 760 + (k // 5) * 100, 0.3, skin="#C68E64", outfit="shirt", outfit_color="#E9DCC0", arms=(30, 30), mouth="flat", hat=None) + '</g>'
    content += '</g>'
    content += calendar(1640, 260, 0.9, "1880s")
    return content, cam_push(t, T, 1.0, 1.08, 1000, 640)


def doctor(x, y, s, t, T, arms=(15, 15), mouth="flat"):
    body = person(x, y, s, skin="#F3D9C0", outfit="coat", outfit_color="#E9E2CF", arms=arms, mouth=mouth, eyes=auto_eyes(t, T), hair_style="tuft", hair_color="#6E6A66")
    hat = f'<g transform="translate({x:.0f} {y - 410 * s:.0f}) scale({s})"><rect x="-56" y="-60" width="112" height="56" rx="8" fill="#6B4A35" {stroke(5)}/><path d="M-90 -4 L90 -4" {stroke(12)}/></g>'
    must = f'<path d="M{x - 26 * s:.0f} {y - 312 * s:.0f} Q{x:.0f} {y - 330 * s:.0f} {x + 26 * s:.0f} {y - 312 * s:.0f}" fill="none" stroke="#4A3A30" stroke-width="{10 * s:.0f}" stroke-linecap="round"/>'
    return body + hat + must


def s074(t, T, fr):
    pt = ease_out_back(seg(t, 0.4 * T, 0.6 * T))
    content = SEPIA_DEF + '<g filter="url(#sep)">' + f'<rect x="-600" y="-400" width="3200" height="1900" fill="#D9C9A8"/><rect x="-600" y="880" width="3200" height="700" fill="#A88A66" {stroke()}/>'
    content += f'<rect x="980" y="200" width="760" height="560" rx="10" fill="#F6F0E2" {stroke()}/>' + mosquito(1360, 470, 2.4, frame=0, flap=False)
    content += doctor(620, 1000, 1.4, t, T, arms=(15, lerp(20, 82, pt)), mouth="flat")
    content += '</g>' + calendar(260, 240, 0.8, "1904")
    return content, cam_push(t, T, 1.0, 1.05, 960, 560)


def s075(t, T, fr):
    lid = seg(t, 0.1 * T, 0.35 * T)
    scr = ease(seg(t, 0.35 * T, 0.6 * T))
    content = SEPIA_DEF + '<g filter="url(#sep)">' + f'<rect x="-600" y="-400" width="3200" height="1900" fill="#D9C9A8"/><rect x="-600" y="880" width="3200" height="700" fill="#A88A66" {stroke()}/>'
    content += barrel(520, 900, 1.3, lid)
    content += person(820, 1000, 1.1, skin="#8D5A3B", outfit="shirt", outfit_color="#E9DCC0", arms=(15, 70), mouth="smile", eyes=auto_eyes(t, T), hat=None)
    content += f'<rect x="1180" y="260" width="460" height="420" fill="#6B4A35" {stroke()}/><rect x="1210" y="290" width="400" height="360" fill="#BFD9D6"/>'
    content += f'<rect x="1210" y="290" width="400" height="{360 * scr:.0f}" fill="url(#mesh)" opacity="0.9"/><rect x="1210" y="290" width="400" height="{360 * scr:.0f}" fill="#6E6A66" opacity="0.35"/>'
    content += '</g>' + check(1640, 820, 1.2, seg(t, 0.7 * T, 0.85 * T))
    return content, (1.0, 960, 560)


def s076(t, T, fr):
    puffp = (t * 1.2) % 1
    content = sky("#BFD9D6", "#F3E6C4", "ddt") + f'<rect x="-600" y="860" width="3200" height="700" fill="#C9B07E" {stroke()}/>'
    content += house(1300, 870, 1.8, "#E8C9A0", "#9C7B5B")
    content += sprayer_worker(720, 1000, 1.3, t, T, puffp)
    content += f'<g transform="translate(300 250)"><circle r="110" fill="#3E7CA6" {stroke()}/><path d="M-60 -40 Q-20 -80 30 -50 Q20 0 -30 10 Z M10 30 Q60 10 70 60 Q20 90 0 60 Z" fill="#7FA65A" {stroke(5)}/></g>'
    content += calendar(1700, 220, 0.8, "1955")
    return content, (1.0, 960, 560)


def s077(t, T, fr):
    content = sky("#BFD9D6", "#F3E6C4", "ddt2") + f'<rect x="-600" y="860" width="3200" height="700" fill="#C9B07E" {stroke()}/>' + house(1300, 870, 1.8, "#E8C9A0", "#9C7B5B")
    content += "".join(f'<circle cx="{800 + k * 90 + 20 * math.sin(t + k)}" cy="{520 + 40 * math.sin(k)}" r="{80 + 10 * k}" fill="#E9EEF0" opacity="0.45"/>' for k in range(6))
    for k in range(5):
        x = 760 + k * 140 + 40 * math.sin(t * 2 + k); y = 480 + 60 * math.sin(t * 3 + k * 2)
        content += mosquito(x, y, 0.55, frame=fr + k, look=(2, 0))
    content += calendar(300, 260, 0.9, "1969", flip=abs(math.sin(t * 6)) if t < 0.5 * T else 0)
    content += stamp(1000, 860, "ABANDONED", seg(t, 0.7 * T, 0.9 * T), RED, -10, 96)
    return content, (1.0, 960, 560)


def s078(t, T, fr):
    tap = abs(math.sin(t * 6)) if 0.25 * T < t < 0.8 * T else 0
    content = f'<rect x="-600" y="-400" width="3200" height="1900" fill="#E8C9A0"/><circle cx="960" cy="540" r="800" fill="url(#glow)" opacity="0.4"/>'
    content += pp(620, 1300, 2.0, t, T, arms=(15, lerp(150, 162, tap)), mouth="smile", look=(8, 0))
    content += mosquito(1400, 560, 2.2, frame=fr, look=(-4, 0), flip=True)
    content += f'<path d="M1330 470 Q{1300 - 20 * tap:.0f} 400 {1340 - 10 * tap:.0f} 360" fill="none" stroke="{INK}" stroke-width="7" stroke-linecap="round"/>'
    return content, cam_push(t, T, 1.0, 1.05, 960, 560)


# ---------------- COULD WE DO IT ----------------
def s079(t, T, fr):
    op = ease(seg(t, 0.15 * T, 0.6 * T))
    content = f'<rect x="-600" y="-400" width="3200" height="1900" fill="#D9D6CC"/><rect x="-600" y="900" width="3200" height="700" fill="#A8A49A" {stroke()}/>'
    content += f'<rect x="1000" y="240" width="460" height="660" fill="#F4F6F4" {stroke()}/><circle cx="1230" cy="520" r="200" fill="url(#glow)" opacity="{op:.2f}"/>'
    content += S1.bg_lab().replace('<rect x="-400" y="-300" width="4000" height="1700" fill="#E6E0D2"/>', '') if False else ""
    w = 460 * (1 - op)
    content += f'<path d="M1000 240 L{1000 + w:.0f} {240 + 40 * op:.0f} L{1000 + w:.0f} {900 - 40 * op:.0f} L1000 900 Z" fill="#5B8DB8" {stroke()}/>'
    content += pp(700, 1000, 1.2, t, T, mouth="o" if op > 0.5 else "smile", arms=(15, 70), look=(8, 0))
    return content, (1.0, 960, 560)


def s080(t, T, fr):
    glow = 0.5 + 0.5 * math.sin(t * 4)
    content = bg_lab2() + f'<circle cx="900" cy="520" r="520" fill="url(#glow)" opacity="0.4"/>'
    content += mosquito(900, 540, 4.0, frame=fr, look=(3, 2))
    r = rnd(30)
    content += "".join(f'<circle cx="{900 + r.uniform(-260, -40):.0f}" cy="{560 + r.uniform(-20, 40):.0f}" r="{8 + 4 * glow:.1f}" fill="#7FE08A" {stroke(2)}/>' for _ in range(10))
    b = seg(t, 0.35 * T, 0.8 * T)
    vx = lerp(1700, 1240, min(1, b * 2)) + (lerp(0, 500, max(0, b * 2 - 1)))
    vy = 420 - 200 * max(0, b * 2 - 1)
    content += virus(vx, vy, 1.0, "#D96C8A", t)
    return content, (1.0, 960, 540)


def s081(t, T, fr):
    g = ease(seg(t, 0.15 * T, 0.6 * T))
    content = bg_paper("#E9E2CF")
    r = rnd(31)
    for k in range(24):
        x, y = 160 + (k % 6) * 150, 200 + (k // 6) * 160
        treated = k % 2 == 0
        col = "#9CC5A1" if treated and g > k / 24 else "#D9CBB0"
        content += f'<rect x="{x}" y="{y}" width="130" height="140" rx="8" fill="{col}" {stroke(5)}/>'
    content += text(560, 900, "YOGYAKARTA", 52)
    sh = ease(seg(t, 0.55 * T, 0.9 * T))
    content += f'<rect x="1260" y="200" width="200" height="600" fill="#D9CBB0" {stroke()}/>' + text(1360, 860, "without", 40)
    h = 600 * (1 - 0.77 * sh)
    content += f'<rect x="1540" y="{800 - h:.0f}" width="200" height="{h:.0f}" fill="#7FA65A" {stroke()}/>' + text(1640, 860, "with", 40)
    if sh > 0.9:
        content += text(1640, 760 - h, "-77%", 80, RED, outline=INK)
    return content, (1.0, 960, 540)


def s082(t, T, fr):
    open_ = ease(seg(t, 0.05 * T, 0.25 * T))
    content = sky("#BFD9D6", "#F7C98B", "rel") + town(t).replace('<rect x="-600" y="-400" width="3200" height="1900" fill="url(#town)"/>', '')
    content += f'<rect x="760" y="760" width="400" height="220" fill="#C9C6C0" {stroke()}/><path d="M760 760 L{760 + 400 * (1 - open_):.0f} {760 - 160 * open_:.0f}" {stroke(10)}/>'
    for k in range(14):
        u = seg(t, 0.15 * T + k * 0.03 * T, 0.7 * T + k * 0.02 * T)
        if u > 0:
            content += mosquito(960 + (k - 7) * 60 * u + 40 * math.sin(t * 4 + k), 760 - 600 * u, 0.5, frame=fr + k)
    fade = seg(t, 0.6 * T, 0.95 * T)
    content += f'<g opacity="{1 - fade:.2f}">{egg_raft(1500, 1010, 24, 1.6)}</g>'
    content += f'<path d="M1420 960 L1600 1060 M1600 960 L1420 1060" stroke="{RED}" stroke-width="16" stroke-linecap="round" opacity="{fade:.2f}"/>'
    return content, (1.0, 960, 560)


def tree_nodes(gen_glow):
    out = ""
    levels = [[960], [600, 1320], [420, 780, 1140, 1500], [330, 510, 690, 870, 1050, 1230, 1410, 1590]]
    ys = [220, 440, 660, 880]
    for li in range(1, 4):
        for k, x in enumerate(levels[li]):
            px = levels[li - 1][k // 2]
            out += f'<path d="M{px} {ys[li - 1] + 40} L{x} {ys[li] - 40}" stroke="#C8BFA8" stroke-width="6"/>'
    for li, xs in enumerate(levels):
        for x in xs:
            g = gen_glow[li]
            out += f'<circle cx="{x}" cy="{ys[li]}" r="{60 * g:.0f}" fill="#7FE08A" opacity="{0.6 * g:.2f}"/>' + tiny_mosquito(x, ys[li], 1.6)
    return out


def s083(t, T, fr):
    content = f'<rect x="-600" y="-400" width="3200" height="1900" fill="#E6E0D2"/><rect x="160" y="100" width="1600" height="880" rx="12" fill="#FDFDFB" {stroke()}/>'
    gl = [seg(t, 0.1 * T + k * 0.18 * T, 0.25 * T + k * 0.18 * T) for k in range(4)]
    content += tree_nodes(gl)
    return content, (1.0, 960, 540)


def s084(t, T, fr):
    content = f'<rect x="-600" y="-400" width="3200" height="1900" fill="#D9D6CC"/><rect x="-600" y="900" width="3200" height="700" fill="#A8A49A" {stroke()}/>'
    content += cage(560, 260, 800, 600)
    alive = 1 - ease(seg(t, 0.15 * T, 0.85 * T))
    r = rnd(40)
    for k in range(30):
        if k / 30 < alive:
            content += tiny_mosquito(r.uniform(620, 1300) + 10 * math.sin(t * 5 + k), r.uniform(320, 820) + 8 * math.cos(t * 6 + k), 1.2, frame=fr + k)
    months = ["JAN", "MAR", "MAY", "JUL", "SEP", "NOV"]
    content += calendar(1640, 300, 0.9, months[min(5, int(seg(t, 0.1 * T, 0.9 * T) * 6))])
    return content, (1.0, 960, 560)


def s085(t, T, fr):
    content = bg_paper()
    cols = ["#8B7E74", "#6E625A", "#9C8A5E", "#7A6A8A", "#8A6A4E", "#5E6E5A", "#8B7E74"]
    for k in range(7):
        content += f'<g>{mosquito(220 + k * 250, 560, 0.8, frame=fr + k, flap=True).replace("#8B7E74", cols[k])}</g>'
    mx = lerp(220, 970, ease(seg(t, 0.05 * T, 0.6 * T)))
    on = seg(t, 0.6 * T, 0.8 * T)
    content += f'<circle cx="970" cy="560" r="{180 * on:.0f}" fill="{MUSTARD}" opacity="{0.35 * on:.2f}"/>'
    content += magnifier(mx - 150, 560, 1.6, 0)
    return content, cam_push(t, T, 1.0, 1.15, 970, 560)


def s086(t, T, fr):
    nod = 5 * math.sin(t * 5)
    content = S1.bg_lab()
    content += f'<rect x="760" y="300" width="560" height="460" rx="10" fill="#FDFDFB" {stroke()}/><circle cx="1040" cy="530" r="170" fill="#9DB8D6" {stroke()}/>'
    sl = seg(t, 0.3 * T, 0.6 * T)
    content += f'<path d="M1040 530 L1210 530 A170 170 0 0 0 1206 494 Z" fill="{RED}" {stroke(5)}/>' if sl > 0 else ""
    content += f'<circle cx="1040" cy="530" r="{230 + 20 * math.sin(t * 6):.0f}" fill="none" stroke="{RED}" stroke-width="6" opacity="{0.5 * sl:.2f}" stroke-dasharray="20 14"/>'
    content += person(500, 1000, 1.2, skin="#F3D9C0", outfit="coat", outfit_color="#F4F4F0", arms=(15, 30), hair_style="tuft", hair_color="#C8C6C0", mouth="smile", eyes=auto_eyes(t, T), tilt=nod)
    content += person(1560, 1000, 1.2, skin="#8D5A3B", outfit="coat", outfit_color="#F4F4F0", arms=(30, 15), hair_style="bun", hair_color="#1F1A17", mouth="smile", eyes=auto_eyes(t, T, [0.5 * T]), tilt=-nod, flip=True)
    return content, (1.0, 960, 560)


def s087(t, T, fr):
    sw = 14 * math.sin(t * 3)
    content = f'<rect x="-600" y="-400" width="3200" height="1900" fill="#D9D6CC"/><rect x="-600" y="900" width="3200" height="700" fill="#A8A49A" {stroke()}/>' + cage(560, 260, 800, 600)
    r = rnd(41)
    content += "".join(tiny_mosquito(r.uniform(620, 1300) + 10 * math.sin(t * 5 + k), r.uniform(320, 820), 1.2, frame=fr + k) for k in range(14))
    content += (f'<g transform="translate(1360 560) rotate({sw:.1f})"><path d="M0 0 L0 60" {stroke(5)}/><rect x="-130" y="60" width="260" height="90" rx="12" fill="{MUSTARD}" {stroke()}/>'
                + text(0, 122, "TESTING", 50) + '</g>')
    content += f'<g transform="translate(960 870)"><rect x="-50" y="-30" width="100" height="80" rx="10" fill="{MUSTARD_D}" {stroke(5)}/><path d="M-30 -30 Q-30 -80 0 -80 Q30 -80 30 -30" fill="none" {stroke(8)}/></g>'
    return content, cam_push(t, T, 1.0, 1.05, 960, 560)


# ---------------- RISKS ----------------
def s088(t, T, fr):
    g = ease(seg(t, 0.1 * T, 0.95 * T))
    content = bg_paper("#E9E2CF")
    content += (f'<path d="M100 200 Q700 120 1300 220 Q1800 260 1820 600 Q1800 920 1200 960 Q600 1000 200 900 Q60 600 100 200 Z" fill="#C9D6A8" {stroke()}/>')
    for d in ["M640 160 Q600 520 700 980", "M1180 200 Q1240 560 1120 980", "M120 560 Q900 520 1800 600"]:
        content += f'<path d="{d}" fill="none" stroke="#6B4A35" stroke-width="7" stroke-dasharray="22 16"/>'
    content += f'<circle cx="900" cy="560" r="{40 + 900 * g:.0f}" fill="#7FE08A" opacity="0.35"/><circle cx="900" cy="560" r="{20 + 600 * g:.0f}" fill="#7FE08A" opacity="0.3"/>'
    content += tiny_mosquito(900, 560, 2.4, frame=fr)
    return content, cam_push(t, T, 1.15, 1.0, 960, 560)


def s089(t, T, fr):
    content = sky("#BFD9D6", "#F3E6C4", "meet") + f'<rect x="-600" y="820" width="3200" height="800" fill="#C9B07E" {stroke()}/>'
    content += f'<rect x="900" y="300" width="120" height="540" fill="#7A5338" {stroke()}/><ellipse cx="960" cy="260" rx="700" ry="230" fill="#6E9A5E" {stroke()}/>'
    cast = [(380, "#8D5A3B", "scarf", "#3F7F7A", "dress", "#D08B3E"), (700, "#6B4430", "curly", "#2B2420", "shirt", "#5B8DB8"),
            (1220, "#8D5A3B", "bun", "#1F1A17", "coat", "#F4F4F0"), (1540, "#C68E64", None, "#222", "shirt", "#9C7B5B")]
    for k, (x, sk, hs, hc, of, oc) in enumerate(cast):
        g = math.sin(t * 3 + k * 1.7)
        talking = int(t * 1.2) % 4 == k
        content += person(x, 1000, 1.0, skin=sk, outfit=of, outfit_color=oc, hair_style=hs, hair_color=hc,
                          arms=(20, 50 + 30 * g if talking else 20), mouth="o" if talking and int(t * 6) % 2 else "smile",
                          eyes=auto_eyes(t, T, [k * 0.3]), tilt=4 * g, flip=x > 960)
    return content, cam_push(t, T, 1.0, 1.05, 960, 640)


# ---------------- CONCLUSION ----------------
def s090(t, T, fr):
    ang = lerp(-40, -5, ease(t / T))
    content = S1.bg_bedroom_night(ang) + S1.bed(False)
    content += pp(800, 900, 1.25, t, T, hat=None, satchel=False, legs=False, mouth="flat", look=(6, -4), arms=(15, 15))
    content += S1.blanket()
    return content, cam_push(t, T, 1.0, 1.1, 1000, 480)


def s091(t, T, fr):
    content = bg_tundra(t, "#7F7FA8", "#F2B38B")
    content += "".join(f'<ellipse cx="{(x + t * 40) % 2400 - 200:.0f}" cy="{y}" rx="{w}" ry="40" fill="#F6E9E0" opacity="0.8" {stroke(4)}/>' for x, y, w in [(200, 200, 180), (900, 140, 220), (1500, 260, 160)])
    return content, cam_pan(t, T, 880, 1040, 1.0)


def s092(t, T, fr):
    content = bg_underwater(t, surface=520)
    content += sky("#BFD9D6", "#F3E6C4", "s92").replace('<rect x="-600" y="-400" width="3200" height="1900"', '<rect x="-600" y="-400" width="3200" height="920"')
    content += fish(560, 760, 1.4, t, mouth_open=abs(math.sin(t * 3)))
    content += f'<g transform="translate(720 770)"><path d="M0 -30 Q12 0 0 30" fill="none" stroke="#B5543F" stroke-width="12" stroke-linecap="round"/></g>'
    content += bird(1340, 360 + 20 * math.sin(t * 3), 1.2, fr, col="#4A5A78")
    content += f'<g transform="translate(1500 330)">{moth(0, 0, 0.3, fr)}</g>'
    return content, (1.0, 960, 540)


def s093(t, T, fr):
    return bog_bg(t, dusk=True) + orchid(960, 1000, 2.2, t * 0.5, droop=0.5), cam_push(t, T, 1.0, 1.05, 960, 640)


def s094(t, T, fr):
    g = ease(t / T)
    content = sky("#BFD9D6", "#F3E6C4", "grow") + f'<rect x="-600" y="840" width="3200" height="700" fill="#C9B07E" {stroke()}/>'
    content += f'<rect x="1300" y="300" width="500" height="540" fill="#E8C9A0" {stroke()}/><rect x="1460" y="560" width="180" height="280" fill="#8A5A35" {stroke()}/>'
    skins = ["#8D5A3B", "#A86F4A", "#6B4430"]
    for k in range(3):
        s = lerp(0.55, 1.05, g)
        content += person(420 + k * 320, 1000, s, skin=skins[k], outfit="shirt", outfit_color=["#C9563F", "#5B8DB8", MUSTARD][k], mouth="grin",
                          hair_style="curly" if k == 1 else None, hair_color="#2B2420", arms=(25, 25), eyes=auto_eyes(t, T, [k * 0.4]))
    content += calendar(1550, 200, 0.7, str(2030 + int(g * 15)))
    return content, (1.0, 960, 560)


def s095(t, T, fr):
    content = bg_underwater(t, surface=540)
    content += sky("#BFD9D6", "#F3E6C4", "s95").replace('<rect x="-600" y="-400" width="3200" height="1900"', '<rect x="-600" y="-400" width="3200" height="940"')
    arrive = seg(t, 0, 0.8 * T)
    for k in range(10):
        u = seg(arrive, k * 0.06, k * 0.06 + 0.4)
        x = lerp(-200 if k % 2 else 2100, 300 + k * 140, ease(u))
        content += (dragonfly(x, 300 + (k % 3) * 60, 0.5, fr + k) if k % 3 == 0 else
                    bee(x, 380 + (k % 3) * 40, 0.5, fr + k) if k % 3 == 1 else
                    f'<g transform="translate({x:.0f} {720 + (k % 3) * 80})"><path d="M0 -40 Q12 0 0 40" fill="none" stroke="#B5543F" stroke-width="14" stroke-linecap="round"/></g>')
    return content, cam_push(t, T, 1.06, 1.0, 960, 540)


def s096(t, T, fr):
    content = f'<rect x="-600" y="-400" width="3200" height="1900" fill="#2E3A57"/><circle cx="1150" cy="300" r="700" fill="url(#glow)" opacity="0.55"/>'
    content += f'<rect x="-600" y="760" width="3200" height="120" fill="#8A5A35" {stroke()}/>'
    content += f'<path d="M1150 180 L1150 360 M1060 360 L1240 360 L1210 300 L1090 300 Z" fill="{MUSTARD}" {stroke(6)}/>'
    content += S1.jar(1150, 760, fr, 1.3)
    content += pp(640, 1300, 2.0, t, T, mouth="flat", look=(10, 4), arms=(15, 15), satchel=False)
    return content, cam_push(t, T, 1.0, 1.07, 960, 600)


def s097(t, T, fr):
    op = ease(seg(t, 0.15 * T, 0.4 * T))
    fly = seg(t, 0.35 * T, 0.95 * T)
    content = S1.bg_bedroom_night(0)
    content += pp(700, 1060, 1.35, t, T, mouth="smile", look=(10, -4), arms=(15, 75))
    jx, jy = 960, 700
    content += f'<g transform="translate({jx} {jy})"><rect x="-60" y="-150" width="120" height="150" rx="16" fill="#E8F2F4" fill-opacity="0.55" {stroke(5)}/></g>'
    content += f'<g transform="translate({jx + 80 * op:.0f} {jy - 160 - 60 * op:.0f}) rotate({60 * op:.0f})"><rect x="-66" y="-11" width="132" height="22" rx="6" fill="#8A5A35" {stroke(5)}/></g>'
    mx = lerp(965, 470, ease(fly)) + 30 * math.sin(fly * 9)
    my = lerp(620, 300, ease(fly))
    content += mosquito(mx, my, lerp(0.42, 0.25, fly), frame=fr, flip=True, alpha=1 - seg(fly, 0.85, 1))
    return content, cam_push(t, T, 1.08, 1.0, 900, 560)


def s098(t, T, fr):
    wave = math.sin(t * 7) * 20 if t > 0.1 * T else 0
    content = S1.bg_dawn(t, T)
    sil = [(vulture_sil, 1250, 300, 0.9), (lambda x, y, s: bat(x, y, s, fr), 1550, 360, 1.0), (lambda x, y, s: bee(x, y, s, fr), 1750, 520, 1.0), (lambda x, y, s: spider(x, y, s, t), 1400, 560, 1.4)]
    for k, (fn, x, y, s) in enumerate(sil):
        p = seg(t, 0.15 * T + k * 0.12 * T, 0.3 * T + k * 0.12 * T)
        if p > 0:
            content += f'<g opacity="0.85" transform="translate({x} {y}) scale({ease_out_back(p):.3f}) translate({-x} {-y})"><g filter="url(#sil)">{fn(x, y, s)}</g></g>'
            content += text(x + 60, y - 50, "?", 70, MUSTARD, outline=INK)
    content = '<defs><filter id="sil"><feColorMatrix type="matrix" values="0 0 0 0 0.17  0 0 0 0 0.14  0 0 0 0 0.12  0 0 0 1 0"/></filter></defs>' + content
    content += pp(620, 1000, 1.3, t, T, mouth="grin", arms=(15, 140 + wave), look=(4, -2))
    return content, (1.0, 960, 540)


SCENES = {i: globals()[f"s{i:03d}"] for i in range(49, 99)}
