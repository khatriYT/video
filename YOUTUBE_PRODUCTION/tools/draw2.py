"""Extended house-style library: environments, creatures and props for the full episode."""
import math
from draw import *

SEPIA = "#C9B08A"


def stroke(w=SW):
    return f'stroke="{INK}" stroke-width="{w}" stroke-linejoin="round" stroke-linecap="round"'


def T_(x, y, s=1.0, r=0.0):
    return f"translate({x:.1f} {y:.1f}) rotate({r:.2f}) scale({s:.3f})"


def text(x, y, txt, size=60, color=INK, anchor="middle", weight=900, outline=None, rot=0):
    o = f'stroke="{outline}" stroke-width="{size * 0.12:.1f}" paint-order="stroke" stroke-linejoin="round"' if outline else ""
    return (f'<text x="{x}" y="{y}" transform="rotate({rot} {x} {y})" text-anchor="{anchor}" font-family="Inter Display, Inter, sans-serif" '
            f'font-weight="{weight}" font-size="{size}" fill="{color}" {o}>{txt}</text>')


def auto_eyes(t, T, extra=()):
    return "blink" if blinking(t, [0.27 * T, 0.71 * T] + list(extra)) else "open"


# ---------------- environments ----------------
def bg_paper(color="#F4EEDF"):
    return f'<rect x="-600" y="-400" width="3200" height="1900" fill="{color}"/>'


def sky(top, bottom, gid):
    return (f'<defs><linearGradient id="{gid}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{top}"/>'
            f'<stop offset="1" stop-color="{bottom}"/></linearGradient></defs><rect x="-600" y="-400" width="3200" height="1900" fill="url(#{gid})"/>')


def hills(base=760, c1="#8FB27A", c2="#6E9A5E", far="#A9C29A"):
    return (f'<path d="M-600 {base - 70} Q300 {base - 190} 900 {base - 100} Q1500 {base - 190} 2600 {base - 90} L2600 1600 L-600 1600 Z" fill="{far}" {stroke(5)}/>'
            f'<path d="M-600 {base} Q500 {base - 80} 1100 {base} Q1600 {base - 60} 2600 {base + 10} L2600 1600 L-600 1600 Z" fill="{c1}" {stroke()}/>'
            f'<path d="M-600 {base + 150} Q600 {base + 70} 1200 {base + 150} Q1700 {base + 110} 2600 {base + 170} L2600 1600 L-600 1600 Z" fill="{c2}" {stroke()}/>')


def flower(x, y, s=1.0, col="#E58FA6", t=0.0, i=0):
    sway = 4 * math.sin(t * 1.5 + i)
    petals = "".join(f'<ellipse cx="0" cy="-26" rx="13" ry="22" transform="rotate({k * 72})" fill="{col}" {stroke(4)}/>' for k in range(5))
    return (f'<g transform="{T_(x, y, s, sway)}"><path d="M0 0 L0 -120" {stroke(5)} fill="none"/>'
            f'<path d="M0 -50 Q30 -70 46 -54 Q28 -40 0 -50 Z" fill="#7FA65A" {stroke(4)}/>'
            f'<g transform="translate(0 -130)">{petals}<circle r="14" fill="{MUSTARD}" {stroke(4)}/></g></g>')


def bg_meadow(t, dusk=False):
    top, bot = ("#5B5F8C", "#F2A76B") if dusk else ("#BFD9D6", "#F3E6C4")
    out = sky(top, bot, "mead" + ("d" if dusk else ""))
    out += hills(760, "#7FA65A" if not dusk else "#5E7F4E", "#6E9A5E" if not dusk else "#4D6B44", "#A9C29A" if not dusk else "#7C8E78")
    r = rnd(11)
    for i in range(14):
        out += flower(r.uniform(-200, 2100), r.uniform(900, 1080), r.uniform(0.6, 1.0), r.choice(["#E58FA6", "#F2B33D", "#F3EFE6", "#9DB8D6"]), t, i)
    return out


def bg_backyard_dusk(t, dark=0.0):
    out = sky("#3E4A72", "#D98A6A", "byd")
    out += f'<rect x="-600" y="760" width="3200" height="900" fill="#4D6B44" {stroke()}/>'
    for x in range(-200, 2200, 120):
        out += f'<rect x="{x}" y="560" width="90" height="220" fill="#8A6A4E" {stroke(5)}/><path d="M{x} 560 L{x + 45} 520 L{x + 90} 560" fill="#8A6A4E" {stroke(5)}/>'
    out += f'<path d="M-600 640 L2600 640" stroke="#6B4A35" stroke-width="14"/>'
    out += (f'<rect x="1500" y="300" width="500" height="470" fill="#B98B5E" {stroke()}/><rect x="1620" y="420" width="160" height="200" fill="#F7D488" {stroke()}/>'
            f'<circle cx="1830" cy="380" r="22" fill="#FFE9A8" {stroke(4)}/><circle cx="1830" cy="380" r="{90 + 6 * math.sin(t * 9):.0f}" fill="url(#glow)" opacity="0.7"/>')
    if dark:
        out += f'<rect x="-600" y="-400" width="3200" height="1900" fill="#101830" opacity="{dark}"/>'
    return out


def bg_underwater(t, surface=170, bottom=980):
    bub = ""
    r = rnd(3)
    for i in range(14):
        bx = r.uniform(0, 1920); sp = r.uniform(40, 90)
        by = bottom - ((t * sp + r.uniform(0, 800)) % (bottom - surface))
        bub += f'<circle cx="{bx + 8 * math.sin(t * 2 + i):.0f}" cy="{by:.0f}" r="{r.uniform(5, 12):.0f}" fill="#DDF0F2" fill-opacity="0.5" {stroke(3)}/>'
    weeds = ""
    for i, x in enumerate(range(-100, 2100, 170)):
        sw = 12 * math.sin(t * 1.3 + i)
        h = 180 + (i * 53) % 140
        weeds += f'<path d="M{x} {bottom + 40} Q{x + sw + 30} {bottom - h / 2} {x + sw * 2} {bottom - h}" fill="none" stroke="#4E7F5A" stroke-width="16" stroke-linecap="round"/>'
    return (sky("#DCEBE6", "#F3E6C4", "uwsky") +
            f'<defs><linearGradient id="uw" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#7FB4BE"/><stop offset="1" stop-color="#3F6F7E"/></linearGradient></defs>'
            f'<rect x="-600" y="{surface}" width="3200" height="1500" fill="url(#uw)"/>'
            f'<path d="M-600 {surface} ' + " ".join(f"Q{x + 60} {surface + 8 * math.sin(t * 2 + x / 90):.1f} {x + 120} {surface}" for x in range(-600, 2600, 120)) +
            f'" fill="none" {stroke()}/>' + weeds +
            f'<path d="M-600 {bottom} Q400 {bottom - 40} 1000 {bottom} Q1600 {bottom + 30} 2600 {bottom - 10} L2600 1600 L-600 1600 Z" fill="#C9B07E" {stroke()}/>' + bub)


def bg_tundra(t, sky_top="#C9DCE4", sky_bot="#F3DDB8", snow=True):
    out = sky(sky_top, sky_bot, "tun" + sky_top[1:])
    out += f'<circle cx="1500" cy="640" r="70" fill="#F7D488" {stroke(5)}/>'
    out += f'<path d="M-600 640 Q200 560 800 620 Q1400 570 2600 630 L2600 1600 L-600 1600 Z" fill="#B7B596" {stroke(5)}/>'
    out += f'<path d="M-600 720 Q600 680 1200 720 Q1800 700 2600 730 L2600 1600 L-600 1600 Z" fill="#9C9A6A" {stroke()}/>'
    if snow:
        out += f'<path d="M100 620 Q260 580 420 618 Z" fill="#F4F6F4" {stroke(4)}/><path d="M1600 600 Q1800 560 1980 604 Z" fill="#F4F6F4" {stroke(4)}/>'
    for (x, y, w) in [(300, 860, 220), (900, 930, 300), (1500, 850, 260)]:
        out += f'<ellipse cx="{x}" cy="{y}" rx="{w}" ry="{w * 0.22:.0f}" fill="#8FC1CC" {stroke(5)}/>'
        out += f'<path d="M{x - w * 0.4:.0f} {y} l{w * 0.25:.0f} 0" stroke="#E9F4F2" stroke-width="5" stroke-linecap="round" opacity="{0.6 + 0.4 * math.sin(t * 2 + x):.2f}"/>'
    return out


def spruce(x, y, s=1.0, col="#3E5E46"):
    return (f'<g transform="{T_(x, y, s)}"><rect x="-10" y="-40" width="20" height="40" fill="#6B4A35" {stroke(4)}/>'
            f'<path d="M0 -300 L70 -170 L40 -170 L95 -60 L-95 -60 L-40 -170 L-70 -170 Z" fill="{col}" {stroke(5)}/></g>')


def bg_forest(t, dusk=False):
    out = sky("#9FB5B0" if not dusk else "#56607E", "#DCD6BC" if not dusk else "#C88C78", "for" + str(int(dusk)))
    for i, x in enumerate(range(-300, 2300, 150)):
        out += spruce(x + (i % 2) * 40, 640 + (i % 3) * 20, 1.2 + (i % 2) * 0.3, "#5C7A64")
    out += f'<path d="M-600 760 Q800 700 2600 770 L2600 1600 L-600 1600 Z" fill="#6E8B5A" {stroke()}/>'
    for i, x in enumerate(range(-200, 2300, 260)):
        out += spruce(x, 900 + (i % 2) * 30, 1.7, "#3E5E46")
    out += f'<path d="M-600 900 Q900 840 2600 920 L2600 1600 L-600 1600 Z" fill="#7E9B5C" {stroke()}/>'
    return out


def bg_night(t, trees=True):
    out = sky("#141C36", "#2E3A57", "nite")
    r = rnd(9)
    for i in range(60):
        out += f'<circle cx="{r.uniform(-200, 2100):.0f}" cy="{r.uniform(-100, 600):.0f}" r="{r.choice([2, 2.5, 3])}" fill="#F4E9B8" opacity="{0.5 + 0.5 * math.sin(t * 2 + i):.2f}"/>'
    out += f'<circle cx="1550" cy="230" r="90" fill="#F4E9B8" {stroke(5)}/><circle cx="1580" cy="210" r="14" fill="#E3D59E"/>'
    if trees:
        for i, x in enumerate(range(-200, 2300, 140)):
            out += spruce(x, 1000 + (i % 2) * 20, 1.6 + (i % 3) * 0.2, "#0F1626")
    return out


def bg_lab2():
    return (f'<rect x="-600" y="-400" width="3200" height="1900" fill="#E6E0D2"/><rect x="-600" y="880" width="3200" height="700" fill="#C9B99A"/>'
            f'<path d="M-600 880 L2600 880" {stroke()}/>'
            + "".join(f'<rect x="{x}" y="160" width="300" height="380" rx="6" fill="#F6F0E2" {stroke(5)}/>' for x in (-200, 1800))
            + f'<rect x="300" y="660" width="1320" height="40" rx="6" fill="#B98B5E" {stroke()}/>')


def bg_chalkboard():
    return (f'<rect x="-600" y="-400" width="3200" height="1900" fill="#D9CBB0"/>'
            f'<rect x="160" y="100" width="1600" height="820" rx="16" fill="#3F5B4C" stroke="#8A5A35" stroke-width="28"/>'
            f'<rect x="160" y="100" width="1600" height="820" rx="16" fill="none" {stroke()}/>'
            f'<rect x="-600" y="960" width="3200" height="600" fill="#9C7B5B" {stroke()}/>')


def bg_sepia():
    return f'<rect x="-600" y="-400" width="3200" height="1900" fill="#E9DCC0"/>'


def sepia_wrap(content):
    return f'<g filter="url(#sep)">{content}</g>'


SEPIA_DEF = ('<defs><filter id="sep"><feColorMatrix type="matrix" values="0.39 0.77 0.19 0 0.02  0.35 0.69 0.17 0 0.01  '
             '0.27 0.53 0.13 0 0  0 0 0 1 0"/></filter></defs>')


def house(x, y, s=1.0, wall="#E8C9A0", roof="#B5543F"):
    return (f'<g transform="{T_(x, y, s)}"><rect x="-160" y="-220" width="320" height="220" fill="{wall}" {stroke()}/>'
            f'<path d="M-190 -210 L0 -360 L190 -210 Z" fill="{roof}" {stroke()}/>'
            f'<rect x="-40" y="-120" width="80" height="120" fill="#8A5A35" {stroke(5)}/>'
            f'<rect x="-130" y="-170" width="60" height="60" fill="#BFD9D6" {stroke(5)}/><rect x="70" y="-170" width="60" height="60" fill="#BFD9D6" {stroke(5)}/></g>')


def tree(x, y, s=1.0, col="#6E9A5E", t=0.0, i=0):
    sw = 2 * math.sin(t + i)
    return (f'<g transform="{T_(x, y, s, sw)}"><rect x="-18" y="-160" width="36" height="160" fill="#7A5338" {stroke(5)}/>'
            f'<circle cx="0" cy="-230" r="110" fill="{col}" {stroke()}/><circle cx="-70" cy="-180" r="70" fill="{col}" {stroke()}/>'
            f'<circle cx="75" cy="-185" r="75" fill="{col}" {stroke()}/></g>')


def palm(x, y, s=1.0, t=0.0, i=0):
    sw = 3 * math.sin(t * 1.2 + i)
    leaves = "".join(f'<path d="M0 -300 Q{60 * math.cos(math.radians(a))} {-330 + 30 * math.sin(math.radians(a))} {150 * math.cos(math.radians(a)):.0f} {-280 + 90 * math.sin(math.radians(a)):.0f}" fill="none" stroke="#3E7A4A" stroke-width="26" stroke-linecap="round"/>' for a in (200, 240, 300, 340, 20))
    return f'<g transform="{T_(x, y, s, sw)}"><path d="M0 0 Q20 -150 0 -300" fill="none" stroke="#7A5338" stroke-width="26"/>{leaves}</g>'


# ---------------- creatures ----------------
def fish(x, y, s=1.0, t=0.0, col="#E39B4A", face="smile", flip=False, mouth_open=0.0):
    tail = 12 * math.sin(t * 8)
    eye = '<circle cx="62" cy="-14" r="9" fill="#FFF" stroke="#2B2420" stroke-width="4"/><circle cx="64" cy="-13" r="4" fill="#2B2420"/>'
    m = (f'<path d="M86 10 Q78 18 70 12" fill="none" {stroke(4)}/>' if mouth_open < 0.5 else f'<ellipse cx="88" cy="8" rx="8" ry="{6 + 8 * mouth_open:.0f}" fill="{INK}"/>')
    fl = " scale(-1 1)" if flip else ""
    return (f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.3f}){fl}">'
            f'<path d="M-60 0 L-110 {-36 + tail:.1f} L-104 {36 + tail:.1f} Z" fill="{col}" {stroke(5)}/>'
            f'<ellipse cx="10" cy="0" rx="90" ry="48" fill="{col}" {stroke()}/>'
            f'<path d="M0 -44 Q20 -80 50 -40" fill="{col}" {stroke(5)}/><path d="M-10 10 Q10 30 30 12" fill="none" {stroke(4)}/>{eye}{m}</g>')


def larva(x, y, s=1.0, t=0.0, i=0):
    w = 10 * math.sin(t * 6 + i)
    segs = "".join(f'<ellipse cx="{-k * 16 * 0 + w * k / 6:.1f}" cy="{20 + k * 22}" rx="{13 - k:.0f}" ry="12" fill="#8B7E74" {stroke(3.5)}/>' for k in range(7))
    return (f'<g transform="{T_(x, y, s)}"><path d="M0 0 L0 24" stroke="{INK}" stroke-width="7"/>{segs}'
            f'<circle cx="{w:.1f}" cy="178" r="16" fill="#6E625A" {stroke(3.5)}/><path d="M{w - 14:.1f} 190 l-10 12 M{w + 14:.1f} 190 l10 12" {stroke(3)}/></g>')


def pupa(x, y, s=1.0, r=0.0):
    return (f'<g transform="{T_(x, y, s, r)}"><path d="M-10 -60 Q-60 -40 -60 10 Q-55 60 0 60 Q40 58 40 20 Q35 0 10 10 Q-5 15 -5 30" '
            f'fill="#8B7E74" {stroke(4)}/><circle cx="-30" cy="-10" r="34" fill="#8B7E74" {stroke(4)}/>'
            f'<path d="M-40 -42 l-8 -22 M-22 -44 l4 -22" {stroke(4)}/><circle cx="-26" cy="-14" r="5" fill="{INK}"/></g>')


def tadpole(x, y, s=1.0, t=0.0):
    tl = 18 * math.sin(t * 9)
    return (f'<g transform="{T_(x, y, s)}"><path d="M-30 0 Q-80 {tl:.1f} -130 {tl * 0.5:.1f}" fill="none" stroke="#4E4A42" stroke-width="14" stroke-linecap="round"/>'
            f'<ellipse cx="0" cy="0" rx="42" ry="34" fill="#5C574C" {stroke(5)}/><circle cx="20" cy="-10" r="8" fill="#FFF" {stroke(3)}/><circle cx="22" cy="-10" r="3.5" fill="{INK}"/></g>')


def nymph(x, y, s=1.0, t=0.0):
    leg = 6 * math.sin(t * 5)
    legs = "".join(f'<path d="M{dx} 0 L{dx - 20 + leg:.1f} 40 L{dx - 30} 60" fill="none" {stroke(4)}/><path d="M{dx} 0 L{dx + 10 - leg:.1f} -40 L{dx} -60" fill="none" {stroke(4)}/>' for dx in (-10, 20, 50))
    return (f'<g transform="{T_(x, y, s)}">{legs}<ellipse cx="-60" cy="0" rx="80" ry="26" fill="#7A8A55" {stroke()}/>'
            f'<ellipse cx="40" cy="0" rx="40" ry="30" fill="#7A8A55" {stroke()}/><circle cx="90" cy="-4" r="26" fill="#7A8A55" {stroke()}/>'
            f'<circle cx="100" cy="-18" r="10" fill="#FFF" {stroke(3)}/><circle cx="103" cy="-18" r="4" fill="{INK}"/></g>')


def dragonfly(x, y, s=1.0, fr=0, r=0.0):
    w = (fr % 2) * 14
    return (f'<g transform="{T_(x, y, s, r)}">'
            f'<ellipse cx="0" cy="-30" rx="70" ry="16" transform="rotate({-10 + w})" fill="#CFE7F2" fill-opacity="0.65" {stroke(3)}/>'
            f'<ellipse cx="-10" cy="30" rx="66" ry="15" transform="rotate({12 - w})" fill="#CFE7F2" fill-opacity="0.65" {stroke(3)}/>'
            f'<path d="M-150 0 L10 0" stroke="#3E7CA6" stroke-width="16" stroke-linecap="round"/><path d="M-150 0 L10 0" {stroke(3)} fill="none" opacity="0.4"/>'
            f'<ellipse cx="30" cy="0" rx="30" ry="18" fill="#3E7CA6" {stroke(4)}/><circle cx="66" cy="0" r="20" fill="#3E7CA6" {stroke(4)}/>'
            f'<circle cx="74" cy="-10" r="8" fill="#FFF" {stroke(3)}/><circle cx="76" cy="-10" r="3.5" fill="{INK}"/></g>')


def web(x, y, s=1.0):
    spokes = "".join(f'<path d="M0 0 L{200 * math.cos(math.radians(a)):.0f} {200 * math.sin(math.radians(a)):.0f}" stroke="#F4F6F4" stroke-width="3"/>' for a in range(0, 360, 30))
    rings = "".join(f'<polygon points="' + " ".join(f"{r * math.cos(math.radians(a)):.0f},{r * math.sin(math.radians(a)):.0f}" for a in range(0, 360, 30)) + '" fill="none" stroke="#F4F6F4" stroke-width="2.5"/>' for r in (40, 80, 120, 160, 200))
    return f'<g transform="{T_(x, y, s)}" opacity="0.85">{spokes}{rings}</g>'


def spider(x, y, s=1.0, t=0.0):
    legs = "".join(f'<path d="M0 0 Q{side * 50} {-30 + k * 20} {side * 80} {10 + k * 22 + 4 * math.sin(t * 4 + k)}" fill="none" {stroke(5)}/>' for side in (-1, 1) for k in range(4))
    return f'<g transform="{T_(x, y, s)}">{legs}<circle r="30" fill="#3B2F28" {stroke(5)}/><circle cx="0" cy="-34" r="18" fill="#3B2F28" {stroke(5)}/><circle cx="-7" cy="-38" r="5" fill="#FFF"/><circle cx="7" cy="-38" r="5" fill="#FFF"/></g>'


def bird(x, y, s=1.0, fr=0, col="#4A5A78", belly="#F3EFE6", flip=False, r=0.0):
    up = (fr // 3) % 2
    wing = f'<path d="M-10 -10 Q-40 {-90 if up else 40} -110 {-70 if up else 30} Q-50 -10 -10 -10 Z" fill="{col}" {stroke(5)}/>'
    fl = " scale(-1 1)" if flip else ""
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({r:.1f}) scale({s:.3f}){fl}">'
            f'<path d="M-60 0 L-120 -20 L-110 20 Z" fill="{col}" {stroke(5)}/>'
            f'<ellipse cx="0" cy="0" rx="70" ry="34" fill="{col}" {stroke()}/><ellipse cx="10" cy="12" rx="50" ry="18" fill="{belly}"/>'
            f'<circle cx="60" cy="-14" r="26" fill="{col}" {stroke()}/><path d="M84 -14 L110 -8 L84 -2 Z" fill="{MUSTARD}" {stroke(4)}/>'
            f'<circle cx="66" cy="-20" r="5" fill="{INK}"/>{wing}</g>')


def bat(x, y, s=1.0, fr=0, flip=False, mouth="smile"):
    up = (fr // 2) % 2
    wy = -60 if up else 30
    wing = lambda sd: f'<path d="M{sd * 20} -10 Q{sd * 90} {wy - 40} {sd * 190} {wy} Q{sd * 160} {wy + 30} {sd * 130} {wy + 10} Q{sd * 100} {wy + 40} {sd * 70} {wy + 14} Q{sd * 40} 30 {sd * 20} 20 Z" fill="#4B3D52" {stroke(5)}/>'
    m = '<path d="M-10 8 Q0 16 10 8" fill="none" stroke="#F6F0E2" stroke-width="4"/>' if mouth == "smile" else '<ellipse cx="0" cy="10" rx="8" ry="10" fill="#1E1A22"/>'
    fl = " scale(-1 1)" if flip else ""
    return (f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.3f}){fl}">{wing(-1)}{wing(1)}'
            f'<ellipse cx="0" cy="10" rx="36" ry="46" fill="#5E4E66" {stroke()}/>'
            f'<path d="M-26 -24 L-34 -70 L-8 -38 Z M26 -24 L34 -70 L8 -38 Z" fill="#5E4E66" {stroke(5)}/>'
            f'<circle cx="0" cy="-14" r="30" fill="#5E4E66" {stroke()}/><circle cx="-11" cy="-18" r="6" fill="#F6F0E2"/><circle cx="11" cy="-18" r="6" fill="#F6F0E2"/>'
            f'<circle cx="-11" cy="-18" r="2.6" fill="{INK}"/><circle cx="11" cy="-18" r="2.6" fill="{INK}"/><g transform="translate(0 -12)">{m}</g></g>')


def moth(x, y, s=1.0, fr=0, col="#C9A77C"):
    w = (fr % 2) * 0.15
    return (f'<g transform="{T_(x, y, s)}"><g transform="scale({1 - w:.2f} 1)">'
            f'<path d="M0 -10 Q-120 -110 -150 -10 Q-120 40 0 10 Z" fill="{col}" {stroke(5)}/><path d="M0 -10 Q120 -110 150 -10 Q120 40 0 10 Z" fill="{col}" {stroke(5)}/>'
            f'<path d="M0 10 Q-90 30 -90 90 Q-30 80 0 20 Z" fill="{col}" {stroke(5)}/><path d="M0 10 Q90 30 90 90 Q30 80 0 20 Z" fill="{col}" {stroke(5)}/>'
            f'<circle cx="-80" cy="-40" r="16" fill="#8A6A4E" {stroke(3)}/><circle cx="80" cy="-40" r="16" fill="#8A6A4E" {stroke(3)}/></g>'
            f'<ellipse cx="0" cy="10" rx="16" ry="56" fill="#8A6A4E" {stroke(5)}/><path d="M-6 -44 Q-30 -90 -50 -86 M6 -44 Q30 -90 50 -86" fill="none" {stroke(4)}/></g>')


def beetle(x, y, s=1.0):
    legs = "".join(f'<path d="M{sd * 40} {dy} l{sd * 40} {dy / 3 + 14}" {stroke(5)}/>' for sd in (-1, 1) for dy in (-20, 10, 40))
    return (f'<g transform="{T_(x, y, s)}">{legs}<ellipse cx="0" cy="10" rx="58" ry="74" fill="#3E5E46" {stroke()}/>'
            f'<path d="M0 -62 L0 84" {stroke(4)}/><circle cx="0" cy="-74" r="28" fill="#2F4636" {stroke()}/>'
            f'<circle cx="-10" cy="-80" r="5" fill="#FFF"/><circle cx="10" cy="-80" r="5" fill="#FFF"/></g>')


def bee(x, y, s=1.0, fr=0):
    w = (fr % 2) * 16
    return (f'<g transform="{T_(x, y, s)}"><ellipse cx="-10" cy="-40" rx="30" ry="18" transform="rotate({-20 + w})" fill="#DDEFF5" fill-opacity="0.7" {stroke(3)}/>'
            f'<ellipse cx="0" cy="0" rx="56" ry="38" fill="{MUSTARD}" {stroke()}/>'
            f'<path d="M-18 -36 L-18 36 M10 -38 L10 38" stroke="{INK}" stroke-width="12"/>'
            f'<circle cx="56" cy="-4" r="26" fill="#3B2F28" {stroke(5)}/><circle cx="64" cy="-10" r="7" fill="#FFF"/>'
            f'<path d="M-56 0 L-74 0" {stroke(5)}/></g>')


def hoverfly(x, y, s=1.0, fr=0):
    return (f'<g transform="{T_(x, y, s)}">' + mosquito(0, 0, 1.0, frame=fr, flap=True) .replace("#8B7E74", "#E5A73A") + '</g>')


def caribou(x, y, s=1.0, t=0.0, graze=0.0, walk=0.0, flip=False):
    lg = 14 * math.sin(walk * 8) if walk else 0
    head_r = 70 * graze
    legs = "".join(f'<path d="M{lx} 40 L{lx + (lg if k % 2 else -lg):.1f} 150" {stroke(8)} fill="none"/>' for k, lx in enumerate((-80, -50, 60, 90)))
    antler = (f'<path d="M10 -60 Q-10 -130 -40 -150 M-10 -110 L-50 -110 M10 -60 Q40 -140 70 -150 M40 -110 L80 -100" '
              f'fill="none" stroke="#8A6A4E" stroke-width="10" stroke-linecap="round"/>')
    head = (f'<g transform="translate(130 -40) rotate({head_r:.1f})">{antler}<path d="M-20 -20 Q10 -60 40 -40 L90 20 Q90 40 70 40 L10 20 Z" fill="#8A6A4E" {stroke()}/>'
            f'<circle cx="30" cy="-20" r="6" fill="{INK}"/><ellipse cx="86" cy="30" rx="12" ry="9" fill="#3B2F28"/></g>')
    fl = " scale(-1 1)" if flip else ""
    return (f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.3f}){fl}">{legs}'
            f'<path d="M-130 -10 Q-130 -70 -40 -70 L90 -70 Q140 -60 140 0 Q130 50 60 50 L-80 50 Q-130 50 -130 -10 Z" fill="#9C7B5B" {stroke()}/>'
            f'<path d="M40 -70 Q90 -40 80 30 Q50 40 40 -70 Z" fill="#E9DCC0" {stroke(5)}/>{head}</g>')


def wolf(x, y, s=1.0):
    return (f'<g transform="{T_(x, y, s)}"><path d="M-110 0 Q-160 -40 -170 -10" fill="none" stroke="#6E6A66" stroke-width="22" stroke-linecap="round"/>'
            + "".join(f'<path d="M{lx} 30 L{lx} 120" {stroke(8)}/>' for lx in (-80, -50, 50, 80)) +
            f'<path d="M-120 -10 Q-120 -60 -40 -60 L70 -60 Q110 -50 110 0 Q100 40 40 40 L-80 40 Q-120 40 -120 -10 Z" fill="#8E8A86" {stroke()}/>'
            f'<path d="M90 -60 L130 -110 L150 -60 L210 -30 Q200 0 150 0 L100 -10 Z" fill="#8E8A86" {stroke()}/>'
            f'<path d="M120 -80 L126 -104 L140 -76" fill="#6E6A66"/><circle cx="160" cy="-46" r="6" fill="{INK}"/><circle cx="208" cy="-30" r="8" fill="{INK}"/></g>')


def orchid(x, y, s=1.0, t=0.0, droop=0.0):
    sw = 3 * math.sin(t * 1.4)
    flowers = "".join(f'<g transform="translate({(-1) ** k * 26} {-260 + k * 48})"><path d="M0 0 Q-24 -16 -18 -36 Q0 -24 0 0 Z M0 0 Q24 -16 18 -36 Q0 -24 0 0 Z" fill="#CFE0A0" {stroke(4)}/>'
                      f'<path d="M0 0 Q-6 30 0 44 Q6 30 0 0 Z" fill="#B6D07A" {stroke(4)}/></g>' for k in range(4))
    return (f'<g transform="{T_(x, y, s, sw + droop * 18)}"><path d="M-110 0 Q-60 -90 0 -6 Q60 -90 120 0 Q0 30 -110 0 Z" fill="#6E9A5E" {stroke()}/>'
            f'<path d="M0 0 Q6 -150 0 -300" fill="none" stroke="#6E9A5E" stroke-width="12"/><path d="M0 0 Q6 -150 0 -300" fill="none" {stroke(3)} opacity="0.5"/>{flowers}</g>')


def shark(x, y, s=1.0, t=0.0):
    return (f'<g transform="{T_(x, y, s)}"><path d="M-170 0 L-230 -60 L-215 0 L-230 60 Z" fill="#7F96A8" {stroke()}/>'
            f'<path d="M-180 0 Q-60 -90 120 -30 Q190 0 120 30 Q-60 70 -180 0 Z" fill="#7F96A8" {stroke()}/>'
            f'<path d="M-30 -56 L10 -130 L40 -50 Z" fill="#7F96A8" {stroke()}/><path d="M-110 10 Q-20 50 120 20 Q-20 60 -110 10 Z" fill="#E9EEF0"/>'
            f'<circle cx="110" cy="-14" r="7" fill="{INK}"/><path d="M80 16 L130 12" {stroke(4)}/></g>')


def snake(x, y, s=1.0, t=0.0):
    pts = " ".join(f"{-200 + k * 40},{20 * math.sin(k * 0.9 + t * 3):.1f}" for k in range(11))
    return (f'<g transform="{T_(x, y, s)}"><polyline points="{pts}" fill="none" stroke="{INK}" stroke-width="44" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<polyline points="{pts}" fill="none" stroke="#7FA65A" stroke-width="32" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<ellipse cx="225" cy="{20 * math.sin(10 * 0.9 + t * 3) - 10:.1f}" rx="44" ry="30" fill="#7FA65A" {stroke()}/>'
            f'<circle cx="236" cy="{20 * math.sin(10 * 0.9 + t * 3) - 22:.1f}" r="6" fill="{INK}"/></g>')


def dinosaur(x, y, s=1.0, col="#3A3A4A", step=0.0):
    lg = 16 * math.sin(step)
    return (f'<g transform="{T_(x, y, s)}" opacity="0.85"><path d="M-300 -40 Q-150 -120 0 -110 Q150 -100 200 -260 Q230 -330 300 -320 Q330 -300 300 -280 Q260 -260 240 -90 Q230 -20 160 0 L-100 0 Q-200 0 -300 -40 Z" fill="{col}"/>'
            f'<path d="M-60 -10 L{-70 + lg:.0f} 120 M60 -10 L{70 - lg:.0f} 120 M-20 -10 L{-10 - lg:.0f} 120 M120 -10 L{110 + lg:.0f} 120" stroke="{col}" stroke-width="40" stroke-linecap="round"/></g>')


def vulture_sil(x, y, s=1.0, col="#2B2420"):
    return (f'<g transform="{T_(x, y, s)}"><path d="M-200 0 Q-100 -60 0 -10 Q100 -60 200 0 Q100 -20 0 20 Q-100 -20 -200 0 Z" fill="{col}"/>'
            f'<circle cx="0" cy="-20" r="22" fill="{col}"/></g>')


# ---------------- props / infographics ----------------
def question_mark(x, y, s=1.0, col=MUSTARD):
    return text(x, y, "?", int(160 * s), col, outline=INK)


def check(x, y, s=1.0, p=1.0):
    if p <= 0:
        return ""
    k = ease_out_back(p)
    return (f'<g transform="{T_(x, y, s * k)}"><circle r="70" fill="#7FA65A" {stroke()}/>'
            f'<path d="M-34 0 L-8 26 L38 -26" fill="none" stroke="#FFF" stroke-width="16" stroke-linecap="round" stroke-linejoin="round"/></g>')


def stamp(x, y, label, p, col=RED, rot=-12, size=80):
    if p <= 0:
        return ""
    k = 1 + 1.4 * (1 - ease(min(1, p * 3)))
    w = len(label) * size * 0.68 + 60
    return (f'<g transform="translate({x} {y}) rotate({rot}) scale({k:.3f})" opacity="{min(1, p * 4):.2f}">'
            f'<rect x="{-w / 2:.0f}" y="{-size * 0.85:.0f}" width="{w:.0f}" height="{size * 1.3:.0f}" rx="12" fill="none" stroke="{col}" stroke-width="12"/>'
            + text(0, size * 0.25, label, size, col) + '</g>')


def calendar(x, y, s=1.0, label="", flip=0.0):
    return (f'<g transform="{T_(x, y, s)}"><rect x="-90" y="-100" width="180" height="200" rx="14" fill="#F6F0E2" {stroke()}/>'
            f'<rect x="-90" y="-100" width="180" height="50" rx="14" fill="{RED}" {stroke()}/>'
            f'<circle cx="-45" cy="-100" r="9" fill="{INK}"/><circle cx="45" cy="-100" r="9" fill="{INK}"/>'
            + text(0, 40, label, 64) +
            (f'<path d="M-90 -50 L90 -50 L90 {-50 + 150 * (1 - flip):.0f} L-90 {-50 + 150 * (1 - flip):.0f} Z" fill="#E6DCC8" {stroke(4)} opacity="{0.9 * flip:.2f}"/>' if flip > 0 else "")
            + '</g>')


def magnifier(x, y, s=1.0, r=-30):
    return (f'<g transform="{T_(x, y, s, r)}"><path d="M0 0 L80 0" stroke="#5A3A28" stroke-width="22" stroke-linecap="round"/>'
            f'<circle cx="150" cy="0" r="70" fill="#CFE7F2" fill-opacity="0.45" {stroke()}/></g>')


def amber(x, y, s=1.0, glow=0.0, inner=True, fr=0):
    return (f'<g transform="{T_(x, y, s)}"><circle r="{200 + 30 * glow:.0f}" fill="url(#glow)" opacity="{0.5 + 0.4 * glow:.2f}"/>'
            f'<path d="M-150 -40 Q-120 -140 0 -150 Q140 -140 160 -30 Q170 90 40 130 Q-110 150 -160 60 Z" fill="#E7A33A" fill-opacity="0.92" {stroke()}/>'
            + (mosquito(0, 0, 0.9, frame=0, flap=False) if inner else "") +
            f'<path d="M-100 -80 Q-60 -110 -10 -112" fill="none" stroke="#FFF3C4" stroke-width="12" stroke-linecap="round" opacity="0.7"/></g>')


def cage(x, y, w=700, h=480):
    bars = "".join(f'<path d="M{x + k * w / 14:.0f} {y} L{x + k * w / 14:.0f} {y + h}" stroke="#6E6A66" stroke-width="4"/>' for k in range(15))
    hb = "".join(f'<path d="M{x} {y + k * h / 10:.0f} L{x + w} {y + k * h / 10:.0f}" stroke="#6E6A66" stroke-width="3"/>' for k in range(11))
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#E8F2F4" fill-opacity="0.35" {stroke()}/>{bars}{hb}<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" {stroke()}/>'


def file_card(x, y, label, s=1.0):
    return (f'<g transform="{T_(x, y, s)}"><rect x="-170" y="-120" width="340" height="240" rx="12" fill="#F6F0E2" {stroke()}/>'
            f'<rect x="-170" y="-120" width="340" height="70" rx="12" fill="#E6C27A" {stroke(5)}/>' + text(0, -68, label, 44) +
            f'<path d="M-130 0 L130 0 M-130 40 L80 40" stroke="#C8BFA8" stroke-width="10" stroke-linecap="round"/></g>')


def virus(x, y, s=1.0, col="#D96C8A", t=0.0):
    sp = "".join(f'<path d="M{40 * math.cos(math.radians(a)):.0f} {40 * math.sin(math.radians(a)):.0f} L{62 * math.cos(math.radians(a)):.0f} {62 * math.sin(math.radians(a)):.0f}" {stroke(5)}/><circle cx="{66 * math.cos(math.radians(a)):.0f}" cy="{66 * math.sin(math.radians(a)):.0f}" r="9" fill="{col}" {stroke(4)}/>' for a in range(0, 360, 45))
    return f'<g transform="{T_(x, y, s, t * 40)}">{sp}<circle r="42" fill="{col}" {stroke()}/><circle cx="-12" cy="-8" r="5" fill="{INK}"/><circle cx="12" cy="-8" r="5" fill="{INK}"/><path d="M-10 12 Q0 20 10 12" fill="none" {stroke(4)}/></g>'


def ranger_hat():
    return (f'<path d="M-60 -10 Q0 -30 60 -10 L40 -40 Q0 -80 -40 -40 Z" fill="#B98B5E" {stroke(5)}/>'
            f'<path d="M-90 -8 Q0 -26 90 -8 Q0 6 -90 -8 Z" fill="#B98B5E" {stroke(5)}/><path d="M-40 -36 L40 -36" stroke="#6B4A35" stroke-width="8"/>')


def podium(x, y):
    return (f'<rect x="{x - 300}" y="{y - 160}" width="200" height="160" fill="#C9C6C0" {stroke()}/>' + text(x - 200, y - 50, "2", 80, "#6E6A66") +
            f'<rect x="{x - 100}" y="{y - 260}" width="200" height="260" fill="{MUSTARD}" {stroke()}/>' + text(x, y - 130, "1", 100, "#8A5A35") +
            f'<rect x="{x + 100}" y="{y - 110}" width="200" height="110" fill="#C98A5E" {stroke()}/>' + text(x + 200, y - 30, "3", 70, "#6B4A35"))


def medal(x, y, s=1.0):
    return (f'<g transform="{T_(x, y, s)}"><path d="M-30 -120 L0 -20 L30 -120" fill="none" stroke="{RED}" stroke-width="16"/>'
            f'<circle cx="0" cy="10" r="38" fill="{MUSTARD}" {stroke()}/><path d="M0 -8 L6 6 L20 6 L9 14 L13 28 L0 20 L-13 28 L-9 14 L-20 6 L-6 6 Z" fill="#FFF3C4"/></g>')


def icon_circle(x, y, inner, s=1.0, col="#F6F0E2", p=1.0):
    if p <= 0:
        return ""
    k = ease_out_back(p)
    return f'<g transform="{T_(x, y, s * k)}"><circle r="90" fill="{col}" {stroke()}/>{inner}</g>'


ICON_BREATH = f'<path d="M-50 10 Q-50 -30 -10 -30 Q0 -60 30 -40 Q60 -40 56 -6 Q70 20 40 30 L-40 30 Q-60 30 -50 10 Z" fill="#DCE6EA" {stroke(5)}/>'
ICON_SMELL = "".join(f'<path d="M{dx} 40 Q{dx - 20} 10 {dx} -10 Q{dx + 20} -30 {dx} -50" fill="none" stroke="#7FA65A" stroke-width="9" stroke-linecap="round"/>' for dx in (-30, 0, 30))
ICON_HEAT = (f'<rect x="-14" y="-60" width="28" height="90" rx="14" fill="#F6F0E2" {stroke(5)}/><circle cx="0" cy="40" r="26" fill="{RED}" {stroke(5)}/>'
             f'<rect x="-6" y="-20" width="12" height="60" fill="{RED}"/>')


def plume(x0, y0, x1, y1, t, col="#DCE6EA", width=60, op=0.55):
    pts = []
    for k in range(21):
        u = k / 20
        x = lerp(x0, x1, u)
        y = lerp(y0, y1, u) + 26 * math.sin(u * 9 - t * 3) * u
        pts.append((x, y))
    d = "M" + " L".join(f"{x:.0f} {y:.0f}" for x, y in pts)
    return (f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{width}" stroke-linecap="round" opacity="{op}"/>'
            f'<path d="{d}" fill="none" stroke="#FFFFFF" stroke-width="{width * 0.3:.0f}" stroke-linecap="round" opacity="{op * 0.6:.2f}"/>')


def heat_waves(x, y, t, n=3, col="#E58A4A"):
    return "".join(f'<path d="M{x + k * 40 - 40} {y} q-14 -25 0 -50 q14 -25 0 -50" fill="none" stroke="{col}" stroke-width="8" stroke-linecap="round" '
                   f'opacity="{0.4 + 0.4 * math.sin(t * 5 + k):.2f}" transform="translate(0 {-((t * 40 + k * 20) % 30):.0f})"/>' for k in range(n))


def scent(x, y, t, n=3, col="#7FA65A"):
    return "".join(f'<path d="M{x + k * 36 - 36} {y} q-18 -30 0 -60 q18 -30 0 -60" fill="none" stroke="{col}" stroke-width="8" stroke-linecap="round" '
                   f'opacity="{0.5 + 0.3 * math.sin(t * 4 + k):.2f}" transform="translate({6 * math.sin(t * 2 + k):.1f} {-((t * 30 + k * 15) % 26):.0f})"/>' for k in range(n))


def egg_raft(x, y, n, s=1.0):
    eggs = "".join(f'<ellipse cx="{(k % 8) * 18 - 63}" cy="{(k // 8) * 14}" rx="8" ry="6" fill="#3B2F28" {stroke(2)}/>' for k in range(n))
    return f'<g transform="{T_(x, y, s)}">{eggs}</g>'


def grid_icons(x0, y0, cols, rows, gap, red_set=(), fr=0, s=0.28, red_p=1.0):
    out = ""
    for r_ in range(rows):
        for c in range(cols):
            k = r_ * cols + c
            x, y = x0 + c * gap, y0 + r_ * gap
            red = k in red_set
            m = tiny_mosquito(x, y, s * 2.2, frame=fr + k)
            if red and red_p > 0:
                out += f'<circle cx="{x}" cy="{y - 4}" r="{30 * red_p:.1f}" fill="{RED}" opacity="0.55"/>'
            out += m
    return out


def person_icon(x, y, s=1.0, col="#F6F0E2", op=1.0):
    return f'<g transform="{T_(x, y, s)}" opacity="{op:.2f}"><circle cx="0" cy="-40" r="18" fill="{col}" {stroke(5)}/><path d="M-22 20 Q-22 -16 0 -16 Q22 -16 22 20 Z" fill="{col}" {stroke(5)}/></g>'


def africa_map(cx, cy, s=1.0, heat=0.5):
    d = ("M-170 -260 Q-60 -300 60 -270 Q140 -250 170 -180 Q230 -120 260 -90 Q250 -40 200 -10 Q170 60 150 140 Q120 230 60 290 "
         "Q20 320 -10 280 Q-50 200 -60 120 Q-90 60 -150 40 Q-240 10 -260 -60 Q-270 -160 -170 -260 Z")
    return (f'<g transform="{T_(cx, cy, s)}"><path d="{d}" fill="#D9C49A" {stroke()}/>'
            f'<clipPath id="afc"><path d="{d}"/></clipPath><g clip-path="url(#afc)">'
            f'<ellipse cx="-20" cy="20" rx="{230 + 20 * heat:.0f}" ry="{120 + 12 * heat:.0f}" fill="{RED}" opacity="{0.35 + 0.25 * heat:.2f}"/>'
            f'<ellipse cx="-20" cy="20" rx="160" ry="80" fill="{RED}" opacity="{0.25 + 0.2 * heat:.2f}"/></g>'
            f'<path d="{d}" fill="none" {stroke()}/></g>')


def bucket(x, y, s=1.0, water=0.0):
    wl = 150 * water
    return (f'<g transform="{T_(x, y, s)}"><path d="M-130 -200 L130 -200 L100 0 L-100 0 Z" fill="#8FA3A8" {stroke()}/>'
            + (f'<path d="M{-100 - 30 * water:.0f} {-wl:.0f} L{100 + 30 * water:.0f} {-wl:.0f} L100 0 L-100 0 Z" fill="#6FA7B5" opacity="0.9"/>' if water > 0 else
               '<path d="M-90 -6 l40 -10 l20 8 l30 -12 l40 10" fill="none" stroke="#6B5A48" stroke-width="4"/>')
            + "".join(f'<ellipse cx="{-80 + k * 22}" cy="{-160 + (k % 2) * 6}" rx="7" ry="5" fill="#3B2F28"/>' for k in range(8))
            + f'<path d="M-130 -200 L130 -200 L100 0 L-100 0 Z" fill="none" {stroke()}/><path d="M-130 -200 Q0 -330 130 -200" fill="none" {stroke(6)}/></g>')


def tyre(x, y, s=1.0):
    return (f'<g transform="{T_(x, y, s)}"><ellipse rx="120" ry="60" fill="#2F2A28" {stroke()}/><ellipse rx="64" ry="30" fill="#6FA7B5" {stroke(5)}/>'
            + "".join(larva(-30 + k * 30, -20, 0.22, 0, k) for k in range(3)) + '</g>')


def barrel(x, y, s=1.0, lid=1.0):
    ly = -260 - 200 * (1 - ease(lid))
    return (f'<g transform="{T_(x, y, s)}"><path d="M-110 -240 Q-130 -120 -110 0 L110 0 Q130 -120 110 -240 Z" fill="#9C7B5B" {stroke()}/>'
            f'<path d="M-122 -170 L122 -170 M-122 -70 L122 -70" stroke="#5A3A28" stroke-width="12"/>'
            f'<ellipse cx="0" cy="{ly:.0f}" rx="120" ry="26" fill="#7A5338" {stroke()}/></g>')


def sprayer_worker(x, y, s, t, T, puff_p):
    body = person(x, y, s, skin="#A86F4A", outfit="shirt", outfit_color="#5B8DB8", arms=(25, 70), mouth="flat",
                  eyes=auto_eyes(t, T), hat=None, glasses=False)
    tank = f'<rect x="{x - 75 * s:.0f}" y="{y - 280 * s:.0f}" width="{50 * s:.0f}" height="{120 * s:.0f}" rx="12" fill="#C9C6C0" {stroke(5)}/>'
    nx, ny = x + (30 + 118 * math.sin(math.radians(70))) * s, y + (-250 + 118 * math.cos(math.radians(70))) * s
    wand = f'<path d="M{nx:.0f} {ny:.0f} l{120 * s:.0f} {-20 * s:.0f}" stroke="#6E6A66" stroke-width="10" stroke-linecap="round"/>'
    mist = "".join(f'<circle cx="{nx + 140 * s + k * 34 + 30 * puff_p:.0f}" cy="{ny - 26 * s + 18 * math.sin(k + t * 4):.0f}" r="{18 + k * 6 + 20 * puff_p:.0f}" fill="#E9EEF0" opacity="{0.55 - k * 0.07:.2f}"/>' for k in range(6))
    return tank + body + wand + mist


def town(t):
    out = sky("#BFD9D6", "#F3E6C4", "town")
    out += f'<rect x="-600" y="820" width="3200" height="800" fill="#D9CBB0" {stroke()}/>'
    for i, (x, w, h, c) in enumerate([(-100, 320, 420, "#E8C9A0"), (260, 280, 520, "#C9D6C8"), (580, 360, 380, "#F0D8B8"), (1300, 340, 480, "#D8C2D6"), (1680, 360, 400, "#E8C9A0")]):
        out += f'<rect x="{x}" y="{820 - h}" width="{w}" height="{h}" fill="{c}" {stroke()}/>'
        for wy in range(820 - h + 60, 760, 120):
            for wx in range(x + 40, x + w - 60, 100):
                out += f'<rect x="{wx}" y="{wy}" width="56" height="70" fill="#BFD9D6" {stroke(4)}/>'
    out += tree(1100, 830, 1.0, t=t)
    return out
