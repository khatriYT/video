"""Scene definitions for 'What If All Mosquitoes Disappeared?' (scenes 001-010).

Each scene function: f(t, T, fr) -> (svg_content, camera(scale,cx,cy))
  t  = seconds since scene start, T = scene duration, fr = frame index
KEYFRAME[n] = fraction of T used for the still image in 04_IMAGES/scenes.
"""
import math
from draw import *

# ---------------- backgrounds ----------------
def bg_bedroom_night(clock_min_angle=0.0, lamp=False):
    stars = "".join(f'<circle cx="{x}" cy="{y}" r="2.5" fill="#F4E9B8"/>' for x, y in [(250, 220), (330, 300), (470, 210), (420, 380), (290, 420)])
    clock_ticks = "".join(
        f'<path d="M0 -72 L0 -60" transform="rotate({i * 30})" stroke="{INK}" stroke-width="5"/>' for i in range(12))
    return f"""
<rect x="-400" y="-300" width="2720" height="1700" fill="#2E3A57"/>
<rect x="-400" y="860" width="2720" height="600" fill="#1E2740"/>
<path d="M-400 860 L2320 860" stroke="{INK}" stroke-width="{SW}"/>
<!-- window -->
<rect x="170" y="140" width="400" height="380" rx="8" fill="#1B2442" stroke="{INK}" stroke-width="{SW}"/>
{stars}
<circle cx="480" cy="230" r="48" fill="#F4E9B8" stroke="{INK}" stroke-width="5"/>
<circle cx="500" cy="218" r="9" fill="#E3D59E"/><circle cx="462" cy="250" r="6" fill="#E3D59E"/>
<path d="M370 140 L370 520 M170 330 L570 330" stroke="{INK}" stroke-width="{SW}"/>
<rect x="150" y="515" width="440" height="22" rx="6" fill="#4A5878" stroke="{INK}" stroke-width="5"/>
<!-- moonlight beam -->
<path d="M200 530 L560 530 L1180 860 L520 860 Z" fill="#F4E9B8" opacity="0.08"/>
<!-- clock -->
<g transform="translate(1520 250)">
 <circle r="88" fill="#F3EAD3" stroke="{INK}" stroke-width="{SW}"/>{clock_ticks}
 <path d="M0 0 L0 -40" stroke="{INK}" stroke-width="8" stroke-linecap="round"/>
 <path d="M0 0 L0 -64" transform="rotate({clock_min_angle:.2f})" stroke="{RED}" stroke-width="6" stroke-linecap="round"/>
 <circle r="7" fill="{INK}"/>
</g>
<!-- nightstand + glasses -->
<rect x="250" y="690" width="190" height="170" rx="6" fill="#5C4433" stroke="{INK}" stroke-width="{SW}"/>
<path d="M250 760 L440 760" stroke="{INK}" stroke-width="5"/><circle cx="345" cy="725" r="7" fill="{INK}"/>
<path d="M300 640 L300 690 M270 690 L330 690" stroke="{INK}" stroke-width="6"/>
<path d="M265 600 L335 600 L318 640 L282 640 Z" fill="{'#F2B33D' if lamp else '#8E7C5C'}" stroke="{INK}" stroke-width="5" stroke-linejoin="round"/>
<g transform="translate(390 676)"><circle cx="-14" r="11" fill="none" stroke="{INK}" stroke-width="4"/><circle cx="14" r="11" fill="none" stroke="{INK}" stroke-width="4"/><path d="M-3 0 L3 0" stroke="{INK}" stroke-width="4"/></g>
"""


def bed(with_hat=True):
    hat = f'<g transform="translate(548 452) rotate(-12) scale(0.8)">{bucket_hat()}</g>' if with_hat else ""
    return f"""
<rect x="520" y="470" width="44" height="400" rx="10" fill="#7A5338" stroke="{INK}" stroke-width="{SW}"/>
<rect x="1520" y="640" width="36" height="230" rx="10" fill="#7A5338" stroke="{INK}" stroke-width="{SW}"/>
<rect x="540" y="660" width="1000" height="150" rx="14" fill="#7A5338" stroke="{INK}" stroke-width="{SW}"/>
<rect x="556" y="610" width="975" height="70" rx="22" fill="#E8E1D0" stroke="{INK}" stroke-width="{SW}"/>
{hat}
"""


def blanket():
    return f"""
<path d="M850 600 Q1180 560 1530 610 L1540 770 Q1200 800 840 772 Z" fill="#4F6D7A" stroke="{INK}" stroke-width="{SW}" stroke-linejoin="round"/>
<path d="M850 600 Q860 690 840 772 L900 776 Q920 690 905 596 Z" fill="#D9D2C0" stroke="{INK}" stroke-width="5"/>
<path d="M1050 640 Q1150 660 1240 640 M1260 700 Q1350 715 1430 690" stroke="#3B5460" stroke-width="5" fill="none"/>
"""


def bg_space(t):
    r = rnd(7)
    stars = ""
    for i in range(140):
        x, y = r.uniform(-200, 2120), r.uniform(-150, 1230)
        tw = 0.55 + 0.45 * math.sin(t * 3 + i)
        stars += f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r.choice([1.5, 2, 2.5, 3.5])}" fill="#F4E9B8" opacity="{tw:.2f}"/>'
    return f"""<defs><linearGradient id="sp" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0E1426"/><stop offset="1" stop-color="#1B2442"/></linearGradient></defs>
<rect x="-300" y="-300" width="2520" height="1700" fill="url(#sp)"/>{stars}"""


def earth(cx=960, cy=540, R=320):
    land = [
        "M-210 -150 Q-120 -230 -40 -190 Q10 -150 -30 -90 Q-90 -60 -110 0 Q-150 40 -200 10 Q-260 -60 -210 -150 Z",
        "M-60 20 Q0 0 30 60 Q50 140 0 220 Q-40 250 -60 190 Q-80 120 -60 20 Z",
        "M60 -230 Q160 -260 230 -180 Q280 -110 220 -60 Q150 -30 120 -80 Q60 -120 60 -230 Z",
        "M110 -20 Q190 -40 230 30 Q250 110 180 150 Q120 160 100 90 Q90 30 110 -20 Z",
        "M200 170 Q260 160 270 210 Q240 250 200 230 Z",
    ]
    lands = "".join(f'<path d="{d}" fill="#7FA65A" stroke="{INK}" stroke-width="6" stroke-linejoin="round"/>' for d in land)
    return f"""<g transform="translate({cx} {cy})">
<circle r="{R + 26}" fill="#7FB6D6" opacity="0.18"/>
<clipPath id="ec"><circle r="{R}"/></clipPath>
<circle r="{R}" fill="#3E7CA6"/>
<g clip-path="url(#ec)">{lands}
<path d="M{R * 0.15} -{R + 10} A{R} {R} 0 0 1 {R * 0.15} {R + 10} Q{R * 0.75} 0 {R * 0.15} -{R + 10} Z" fill="#0E1426" opacity="0.0"/>
<circle cx="{R * 0.55}" cy="{R * 0.1}" r="{R * 1.05}" fill="#0E1426" opacity="0.38" transform="translate({R * 0.55} 0)"/>
<path d="M-260 -60 Q-200 -80 -150 -50" stroke="#FFF" stroke-width="6" opacity="0.35" fill="none" stroke-linecap="round"/>
</g>
<circle r="{R}" fill="none" stroke="{INK}" stroke-width="{SW + 1}"/>
</g>"""


def bg_lab():
    jars = ""
    for i, x in enumerate(range(150, 3100, 170)):
        col = ["#9CC5A1", "#E6C27A", "#9DB8D6", "#D99A8A"][i % 4]
        h = 70 + (i * 37) % 40
        jars += (f'<rect x="{x}" y="{330 - h}" width="64" height="{h}" rx="8" fill="#E8F2F4" fill-opacity="0.7" stroke="{INK}" stroke-width="5"/>'
                 f'<rect x="{x + 6}" y="{330 - h * 0.55:.0f}" width="52" height="{h * 0.55 - 6:.0f}" rx="5" fill="{col}"/>'
                 f'<rect x="{x - 4}" y="{322 - h}" width="72" height="14" rx="4" fill="#8A5A35" stroke="{INK}" stroke-width="4"/>')
    return f"""
<rect x="-400" y="-300" width="4000" height="1700" fill="#E6E0D2"/>
<rect x="-400" y="880" width="4000" height="600" fill="#C9B99A"/>
<path d="M-400 880 L3600 880" stroke="{INK}" stroke-width="{SW}"/>
<rect x="100" y="330" width="3050" height="22" fill="#B98B5E" stroke="{INK}" stroke-width="5"/>
{jars}
<!-- window -->
<rect x="1280" y="420" width="420" height="300" rx="8" fill="#BFD9D6" stroke="{INK}" stroke-width="{SW}"/>
<path d="M1490 420 L1490 720 M1280 570 L1700 570" stroke="{INK}" stroke-width="{SW}"/>
<path d="M1300 700 Q1400 620 1480 690 Q1560 610 1680 700 Z" fill="#8FB27A" stroke="{INK}" stroke-width="4"/>
<!-- posters -->
<rect x="2500" y="420" width="260" height="320" rx="6" fill="#F6F0E2" stroke="{INK}" stroke-width="{SW}"/>
<g transform="translate(2630 560) scale(0.9)">{mosquito(0, 0, 1.0, flap=False)}</g>
<path d="M2530 690 L2730 690 M2530 715 L2680 715" stroke="#B5A88E" stroke-width="8" stroke-linecap="round"/>
"""


def desk(x, y, w=380):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="30" rx="6" fill="#B98B5E" stroke="{INK}" stroke-width="{SW}"/>'
            f'<rect x="{x + 20}" y="{y + 30}" width="24" height="{880 - y - 30}" fill="#8A5A35" stroke="{INK}" stroke-width="5"/>'
            f'<rect x="{x + w - 44}" y="{y + 30}" width="24" height="{880 - y - 30}" fill="#8A5A35" stroke="{INK}" stroke-width="5"/>')


def jar(x, y, fr, s=1.0):
    return (f'<g transform="translate({x} {y}) scale({s})">'
            f'<rect x="-60" y="-150" width="120" height="150" rx="16" fill="#E8F2F4" fill-opacity="0.55" stroke="{INK}" stroke-width="5"/>'
            f'{mosquito(5 + 10 * math.sin(fr * 0.3), -80 + 8 * math.sin(fr * 0.45), 0.42, frame=fr)}'
            f'<rect x="-66" y="-166" width="132" height="22" rx="6" fill="#8A5A35" stroke="{INK}" stroke-width="5"/>'
            f'<path d="M-40 -130 L-40 -40" stroke="#FFF" stroke-width="6" opacity="0.6" stroke-linecap="round"/></g>')


def bg_dawn(t, T):
    sun_y = 650 - 40 * ease(t / max(T, 0.1))
    reeds = ""
    for i, x in enumerate(range(1180, 1900, 46)):
        sway = 5 * math.sin(t * 1.6 + i * 0.7)
        h = 120 + (i * 29) % 70
        reeds += (f'<g transform="rotate({sway:.2f} {x} 840)"><path d="M{x} 840 L{x} {840 - h}" stroke="{INK}" stroke-width="5"/>'
                  f'<rect x="{x - 8}" y="{840 - h - 10}" width="16" height="40" rx="8" fill="#8A5A35" stroke="{INK}" stroke-width="4"/></g>')
    shimmer = "".join(f'<path d="M{1300 + i * 90 + 20 * math.sin(t * 2 + i):.0f} {760 + (i % 3) * 22} l50 0" stroke="#E9F4F2" stroke-width="5" stroke-linecap="round" opacity="0.8"/>' for i in range(6))
    return f"""<defs><linearGradient id="dawn" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#BFD9D6"/><stop offset="0.65" stop-color="#F3D9B1"/><stop offset="1" stop-color="#F7C98B"/></linearGradient></defs>
<rect x="-300" y="-300" width="2520" height="1700" fill="url(#dawn)"/>
<circle cx="1420" cy="{sun_y:.1f}" r="120" fill="url(#glow)"/>
<circle cx="1420" cy="{sun_y:.1f}" r="70" fill="#F7D488" stroke="{INK}" stroke-width="5"/>
<path d="M-300 690 Q300 560 900 650 Q1500 560 2220 660 L2220 1400 L-300 1400 Z" fill="#A9C29A" stroke="{INK}" stroke-width="5"/>
<path d="M-300 760 Q500 680 1100 760 Q1600 700 2220 770 L2220 1400 L-300 1400 Z" fill="#8FB27A" stroke="{INK}" stroke-width="{SW}"/>
<ellipse cx="1560" cy="800" rx="460" ry="80" fill="#6FA7B5" stroke="{INK}" stroke-width="{SW}"/>
{shimmer}{reeds}
<path d="M-300 900 Q200 760 860 860 Q1100 900 1250 1400 L-300 1400 Z" fill="#6E9A5E" stroke="{INK}" stroke-width="{SW}"/>
"""


def bg_sunrise():
    return f"""<defs><linearGradient id="sr" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#BFD9D6"/><stop offset="0.7" stop-color="#F7C98B"/><stop offset="1" stop-color="#F2A76B"/></linearGradient></defs>
<rect x="-300" y="-300" width="2520" height="1700" fill="url(#sr)"/>
<circle cx="1360" cy="760" r="220" fill="url(#glow)"/>
<circle cx="1360" cy="760" r="120" fill="#F7D488" stroke="{INK}" stroke-width="5"/>
<path d="M-300 780 Q400 680 1000 770 Q1600 690 2220 780 L2220 1400 L-300 1400 Z" fill="#8FB27A" stroke="{INK}" stroke-width="{SW}"/>
<path d="M-300 900 Q600 820 1200 900 Q1700 860 2220 920 L2220 1400 L-300 1400 Z" fill="#6E9A5E" stroke="{INK}" stroke-width="{SW}"/>"""


# ---------------- scenes ----------------
def s001(t, T, fr):
    p_clock = seg(t, 0, 0.5 * T)
    ang = lerp(-30, 0, ease(p_clock))
    zz = "".join(f'<text x="{640 + i * 34 + 10 * math.sin(t * 2 + i)}" y="{520 - i * 40 - (t * 18) % 30}" font-family="Inter Display" font-weight="900" font-size="{34 + i * 8}" fill="#F4E9B8" opacity="0.8">z</text>' for i in range(3)) if t < 0.72 * T else ""
    head = head_only(760, 600, 70, rot=-8, eyes="closed", mouth="sleep", glasses=False)
    # mosquito: figure-8 hover then fall
    tf = 0.68 * T
    if t < tf:
        mx = 980 + 90 * math.sin(t * 2.2)
        my = 470 + 35 * math.sin(t * 4.4)
        m = mosquito(mx, my, 0.75, rot=8 * math.sin(t * 3), frame=fr, look=(-3, 2), flip=math.cos(t * 2.2) < 0)
    else:
        q = seg(t, tf, tf + 0.55)
        mx0 = 980 + 90 * math.sin(tf * 2.2)
        my0 = 470 + 35 * math.sin(tf * 4.4)
        m = mosquito(mx0 + 20 * q, lerp(my0, 590, q * q), 0.75, rot=lerp(0, 180, ease(q)), frame=0, dead=True, flap=False)
    content = bg_bedroom_night(ang) + bed() + head + blanket() + zz + m
    s = lerp(1.0, 1.06, ease(t / T))
    return content, (s, 920, 560)


def s002(t, T, fr):
    r = rnd(42)
    swarm = ""
    for i in range(170):
        a = r.uniform(0, 2 * math.pi)
        rad = r.uniform(360, 520)
        x = 960 + rad * math.cos(a) + 8 * math.sin(t * 5 + i)
        y = 540 + rad * math.sin(a) * 0.92 + 6 * math.cos(t * 6 + i)
        thr = 0.12 * T + (x + 200) / 2300 * 0.55 * T
        q = seg(t, thr, thr + 0.7)
        if q >= 1:
            continue
        swarm += tiny_mosquito(x + 10 * q, y + 140 * q * q, r.uniform(0.55, 0.9), frame=fr + i, alpha=1 - q, rot=150 * q)
    content = bg_space(t) + earth() + swarm
    s = lerp(1.08, 1.0, ease(t / T))
    return content, (s, 960, 540)


def s003(t, T, fr):
    gone = 0.45 * T
    content = bg_bedroom_night(0) + f'<rect x="-300" y="560" width="2600" height="900" fill="#E8E1D0" stroke="{INK}" stroke-width="{SW}"/>'
    content += f'<ellipse cx="900" cy="760" rx="420" ry="120" fill="#F2ECDD" stroke="{INK}" stroke-width="{SW}"/>'
    happy = t > gone + 0.25
    eyes = "happy" if happy else ("blink" if blinking(t, [0.3]) else "annoyed")
    content += head_only(900, 600, 210, rot=-4, eyes=eyes, mouth="smile" if happy else "flat", glasses=False)
    content += f'<path d="M-300 820 Q900 760 2300 830 L2300 1400 L-300 1400 Z" fill="#4F6D7A" stroke="{INK}" stroke-width="{SW}"/>'
    if t < gone:
        mx, my = 1240 + 20 * math.sin(t * 9), 450 + 12 * math.sin(t * 13)
        content += mosquito(mx, my, 1.05, rot=-6, frame=fr, look=(-4, 2), flip=True) + buzz_lines(mx, my - 10, fr, 1.6)
    content += puff(1240, 450, seg(t, gone, gone + 0.6), 70)
    return content, (lerp(1.0, 1.03, t / T), 960, 560)


def s004(t, T, fr):
    from draw import arm_path
    sc = abs(math.sin(t * 14)) if t < 0.45 * T else 0
    fade = 1 - seg(t, 0.4 * T, 0.75 * T)
    X, Y, K = 1000, 935, 1.7
    calm = fade <= 0.5
    body = pip(X, Y, K, arms=(86, -74 - 10 * sc if not calm else 15), mouth="smile" if calm else "frown",
               eyes="happy" if calm else "annoyed", hat=None, satchel=False, legs=False)
    d, _ = arm_path(-30, -250, 86, -1)
    nums = [float(v) for v in d.replace("M", "").replace("Q", " ").split()]
    (x0, y0, cx, cy, ex, ey) = nums
    bites = ""
    for u in (0.5, 0.68, 0.86):
        bx = (1 - u) ** 2 * x0 + 2 * (1 - u) * u * cx + u * u * ex
        by = (1 - u) ** 2 * y0 + 2 * (1 - u) * u * cy + u * u * ey
        bx, by = X + K * bx, Y + K * by - 6
        rr = 15 * (0.4 + 0.6 * fade)
        bites += (f'<circle cx="{bx:.0f}" cy="{by:.0f}" r="{rr * 1.8:.1f}" fill="#F2A3A0" opacity="{0.6 * fade:.2f}"/>'
                  f'<circle cx="{bx:.0f}" cy="{by:.0f}" r="{rr:.1f}" fill="{RED}" stroke="{INK}" stroke-width="4" opacity="{fade:.2f}"/>')
    lines = ""
    if sc > 0:
        lines = f'<path d="M770 430 l-24 -30 M810 410 l-6 -38 M850 425 l18 -32" stroke="#F4E9B8" stroke-width="6" stroke-linecap="round"/>'
    sp = sparkle(820, 420, seg(t, 0.72 * T, T), 34, "#F4E9B8")
    content = bg_bedroom_night(0) + bed(False) + body + blanket() + bites + lines + sp
    return content, (1.3, 930, 520)


def s005(t, T, fr):
    p = ease(seg(t, 0.12 * T, 0.8 * T))
    sun = lerp(0.35, 0.85, p)
    content = f"""<rect x="-300" y="-300" width="2600" height="1700" fill="#E8C9A0"/>
<rect x="-300" y="860" width="2600" height="700" fill="#B98B5E"/><path d="M-300 860 L2300 860" stroke="{INK}" stroke-width="{SW}"/>
<defs><linearGradient id="sun5" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F7D9A0"/><stop offset="1" stop-color="#F2A76B"/></linearGradient></defs>
<rect x="1360" y="200" width="360" height="380" rx="10" fill="url(#sun5)" stroke="{INK}" stroke-width="{SW}"/>
<circle cx="1540" cy="520" r="70" fill="#F7D488" stroke="{INK}" stroke-width="5"/>
<path d="M1540 200 L1540 580 M1360 390 L1720 390" stroke="{INK}" stroke-width="{SW}"/>
<circle cx="1540" cy="420" r="420" fill="url(#glow)" opacity="{sun:.2f}"/>
<rect x="420" y="700" width="900" height="80" rx="16" fill="#F1E7D2" stroke="{INK}" stroke-width="{SW}"/>
<rect x="400" y="760" width="940" height="110" rx="12" fill="#8A5A35" stroke="{INK}" stroke-width="{SW}"/>
<rect x="420" y="860" width="30" height="60" fill="#6B4A35" stroke="{INK}" stroke-width="5"/><rect x="1290" y="860" width="30" height="60" fill="#6B4A35" stroke="{INK}" stroke-width="5"/>
"""
    happy = t > 0.5 * T
    parent = person(720, 840, 1.15, skin="#8D5A3B", outfit="dress", outfit_color="#D08B3E", arms=(30, 55),
                    mouth="smile" if happy else "flat", eyes="happy" if happy else "open", hair_style="scarf",
                    hair_color="#3F7F7A", legs=False, look=(4, 0))
    child = person(980, 840, 0.82, skin="#A86F4A", outfit="shirt", outfit_color="#C9563F", arms=(55, 25),
                   mouth="grin" if happy else "o", eyes="open", hair_style="curly", hair_color="#2B2420", legs=False, look=(-3, -3))
    net_y = -1100 * p
    net = (f'<g transform="translate(0 {net_y:.1f})">'
           f'<path d="M880 60 L360 790 L1380 790 Z" fill="url(#mesh)" stroke="#FFFFFF" stroke-width="5" opacity="0.9"/>'
           f'<path d="M880 60 L360 790 L1380 790 Z" fill="#FFFFFF" opacity="0.28"/>'
           f'<path d="M880 60 L360 790 M880 60 L1380 790" stroke="{INK}" stroke-width="3" opacity="0.6"/>'
           f'<path d="M880 -400 L880 60" stroke="{INK}" stroke-width="4"/><circle cx="880" cy="60" r="10" fill="{INK}"/></g>')
    return content + parent + child + net, (lerp(1.0, 1.04, ease(t / T)), 900, 560)


def s006(t, T, fr):
    up = ease_out_back(seg(t, 0.05 * T, 0.45 * T))
    ang = lerp(15, 140, up)
    body = pip(820, 1240, 1.9, arms=(18, ang), thumbs=(False, up > 0.7), mouth="grin" if up > 0.5 else "smile",
               eyes="blink" if blinking(t, [0.8 * T]) else "open", look=(4, -2), tilt=-5 * up, bob=4 * math.sin(t * 3))
    hx = 820 + 1.9 * (30 + 118 * math.sin(math.radians(ang)))
    hy = 1240 + 1.9 * (-250 + 118 * math.cos(math.radians(ang)))
    sp = sparkle(hx + 70, hy - 90, seg(t, 0.45 * T, T), 46) + sparkle(hx - 40, hy - 150, seg(t, 0.55 * T, T), 28)
    return bg_sunrise() + body + sp, (lerp(1.0, 1.05, ease(t / T)), 900, 560)


def scientist_a(x, t, T, shrug=0.0):
    ang = lerp(12, 118, shrug)
    return person(x, 880, 1.3, skin="#F3D9C0", outfit="coat", outfit_color="#F4F4F0", arms=(ang, ang),
                  mouth="smile", eyes="blink" if blinking(t, [0.25 * T, 0.8 * T]) else "open", glasses=False,
                  hair_style="tuft", hair_color="#C8C6C0", tilt=-8 * shrug)


def s007(t, T, fr):
    sh = ease(seg(t, 0.35 * T, 0.5 * T)) * (1 - ease(seg(t, 0.75 * T, 0.88 * T)))
    content = bg_lab() + desk(430, 640, 420) + jar(560, 640, fr, 0.9)
    content += '<rect x="680" y="610" width="120" height="30" rx="3" fill="#FFF" stroke="#2B2420" stroke-width="4" transform="rotate(-6 740 625)"/>'
    content += scientist_a(1000, t, T, sh)
    cx = lerp(820, 1080, ease(t / T))
    return content, (1.08, cx, 560)


def s008(t, T, fr):
    up = ease_out_back(seg(t, 0.05 * T, 0.45 * T))
    ang = lerp(20, 78, up)

    def mag(hx, hy):
        return (f'<g transform="translate({hx:.0f} {hy:.0f}) rotate(-30)"><path d="M0 0 L60 0" stroke="#5A3A28" stroke-width="14" stroke-linecap="round"/>'
                f'<circle cx="100" cy="0" r="44" fill="#CFE7F2" fill-opacity="0.55" stroke="{INK}" stroke-width="{SW}"/></g>')
    content = bg_lab() + desk(1880, 640, 420) + jar(2060, 640, fr, 0.9)
    content += person(2400, 880, 1.3, skin="#8D5A3B", outfit="coat", outfit_color="#F4F4F0", arms=(14, ang),
                      mouth="frown", eyes="blink" if blinking(t, [0.7 * T]) else "open", look=(-6, 2),
                      hair_style="bun", hair_color="#1F1A17", hand_tool=(1, mag), flip=True)
    cx = lerp(2180, 2260, ease(t / T))
    return content, (1.08, cx, 560)


def s009(t, T, fr):
    drop = seg(t, 0.08 * T, 0.6 * T)
    hat_dy = -320 * (1 - ease_out_bounce(drop))
    squash = 1.0 - 0.18 * max(0, math.sin(min(drop * 3.0, 1) * math.pi)) * (drop > 0.35)
    content = f"""<rect x="-300" y="-300" width="2600" height="1700" fill="#D9CBB0"/>
<rect x="-300" y="900" width="2600" height="600" fill="#9C7B5B"/><path d="M-300 900 L2300 900" stroke="{INK}" stroke-width="{SW}"/>
<defs><linearGradient id="door" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#BFD9D6"/><stop offset="1" stop-color="#F7C98B"/></linearGradient></defs>
<rect x="1100" y="200" width="420" height="700" fill="url(#door)" stroke="{INK}" stroke-width="{SW}"/>
<path d="M1100 700 Q1250 620 1350 680 Q1430 640 1520 690 L1520 900 L1100 900 Z" fill="#8FB27A" stroke="{INK}" stroke-width="5"/>
<circle cx="1400" cy="560" r="44" fill="#F7D488" stroke="{INK}" stroke-width="5"/>
<path d="M1520 200 L1700 240 L1700 860 L1520 900 Z" fill="#7A5338" stroke="{INK}" stroke-width="{SW}" stroke-linejoin="round"/>
<circle cx="1670" cy="560" r="12" fill="{MUSTARD}" stroke="{INK}" stroke-width="4"/>
<path d="M1100 900 L1520 900 L1700 1060 L900 1060 Z" fill="#F7C98B" opacity="0.35"/>
<rect x="340" y="330" width="200" height="22" rx="6" fill="#7A5338" stroke="{INK}" stroke-width="5"/>
<circle cx="390" cy="370" r="10" fill="{INK}"/><circle cx="490" cy="370" r="10" fill="{INK}"/>
<rect x="420" y="560" width="160" height="110" rx="8" fill="#E9DFC8" stroke="{INK}" stroke-width="5"/><path d="M440 640 Q500 580 560 640" stroke="#8FB27A" stroke-width="10" fill="none"/>
"""
    happy = drop > 0.6
    body = pip(820, 960, 1.25, arms=(20, 22), hat_dy=hat_dy, hat_squash=squash, mouth="grin" if happy else "o",
               eyes="blink" if blinking(t, [0.8 * T]) else "open", look=(0, -6 + 6 * drop))
    return content + body, (1.0, 960, 560)


def s010(t, T, fr):
    body = pip(520, 900, 0.95, arms=(18, 22), look=(8, -2), mouth="smile",
               eyes="blink" if blinking(t, [0.3 * T]) else "open")
    title = title_text([("WHAT IF ALL", CREAM), ("MOSQUITOES", MUSTARD), ("DISAPPEARED?", CREAM)], 1230, 230,
                       118, p=seg(t, 0.3 * T, 0.5 * T))
    s = lerp(1.08, 1.0, ease(t / T))
    return bg_dawn(t, T) + body + title, (s, 960, 540)


SCENES = {1: s001, 2: s002, 3: s003, 4: s004, 5: s005, 6: s006, 7: s007, 8: s008, 9: s009, 10: s010}
KEYFRAME = {1: 0.4, 2: 0.25, 3: 0.3, 4: 0.25, 5: 0.15, 6: 0.7, 7: 0.6, 8: 0.6, 9: 0.9, 10: 0.9}


# ---- scenes 011+ live in scenes_mosquito2.py / scenes_mosquito3.py ----
def _extend():
    import importlib
    for mod in ("scenes_mosquito2", "scenes_mosquito3"):
        try:
            m = importlib.import_module(mod)
        except ModuleNotFoundError as e:
            if e.name == mod:
                continue
            raise
        SCENES.update(m.SCENES)
        KEYFRAME.update({k: getattr(m, "KEYFRAME", {}).get(k, 0.6) for k in m.SCENES})


_extend()
