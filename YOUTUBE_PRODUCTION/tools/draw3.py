"""Episode-2 library: richly detailed environments, bees & other creatures, food and props.
Same house style (ink #2B2420 outlines, flat colour + soft shading) but denser detail per frame."""
import math
from draw import *
from draw2 import (stroke, text, sky, flower as simple_flower, spruce, tree, bat, moth, beetle, hoverfly, web, spider,
                   bird, dragonfly, magnifier, calendar, check, cage, person_icon, question_mark, auto_eyes, virus)

SW5 = stroke(5)
SW4 = stroke(4)


def pp(x, y, s, t, T, **kw):
    kw.setdefault("eyes", auto_eyes(t, T))
    return pip(x, y, s, **kw)


def cam_push(t, T, a=1.0, b=1.06, cx=960, cy=540):
    return (lerp(a, b, ease(t / T)), cx, cy)


def cam_pan(t, T, x0, x1, s=1.0, cy=540):
    return (s, lerp(x0, x1, ease(t / T)), cy)


def band(rx, ry, x1, x2, cx=0, cy=0, n=8):
    """vertical stripe inside an ellipse (no clipPath needed)"""
    x1, x2 = max(-rx, x1), min(rx, x2)
    xs = [x1 + (x2 - x1) * k / n for k in range(n + 1)]
    top = [(x, -ry * math.sqrt(max(0, 1 - (x / rx) ** 2))) for x in xs]
    bot = [(x, ry * math.sqrt(max(0, 1 - (x / rx) ** 2))) for x in reversed(xs)]
    return "M" + " L".join(f"{cx + x:.1f} {cy + y:.1f}" for x, y in top + bot) + " Z"


# ====================== bees & insects ======================
def honeybee(x, y, s=1.0, fr=0, rot=0, flip=False, look=(0, 0), baskets=False, mouth="smile", flap=True, queen=False, cap=False, alpha=1.0):
    w = (fr % 2) * 20 if flap else 0
    rx, ry = (78, 44) if queen else (60, 44)
    body_col = "#F2B33D"
    stripes = "".join(f'<path d="{band(rx, ry, x1, x1 + 15, -10, 4)}" fill="#3B2A1E"/>' for x1 in ((-40, -12, 16) if not queen else (-56, -28, 0, 28)))
    fuzz = "".join(f'<path d="M{-10 + rx * math.cos(a):.1f} {4 + ry * math.sin(a):.1f} l{6 * math.cos(a):.1f} {6 * math.sin(a):.1f}" stroke="{INK}" stroke-width="3" stroke-linecap="round"/>'
                   for a in [k * 0.42 for k in range(15)])
    legs = "".join(f'<path d="M{dx} 40 q{-6 + k * 4} 22 {-14 + k * 6} 36" fill="none" {stroke(3.5)}/>' for k, dx in enumerate((-20, 0, 18)))
    bask = (f'<circle cx="-38" cy="74" r="13" fill="#FFD25A" {stroke(3.5)}/><circle cx="-14" cy="78" r="12" fill="#FFD25A" {stroke(3.5)}/>' if baskets else "")
    lx, ly = look
    m = {"smile": f'<path d="M50 14 Q60 22 70 13" fill="none" {stroke(3.5)}/>', "o": f'<ellipse cx="60" cy="18" rx="5" ry="6" fill="{INK}"/>',
         "flat": f'<path d="M52 16 L68 16" {stroke(3.5)}/>', "frown": f'<path d="M50 20 Q60 12 70 20" fill="none" {stroke(3.5)}/>'}[mouth]
    crown = (f'<path d="M38 -52 L44 -72 L54 -58 L62 -76 L70 -58 L80 -72 L84 -52 Z" fill="{MUSTARD}" {stroke(3.5)}/>' if queen else "")
    capp = (f'<path d="M36 -36 Q60 -66 86 -36 Z" fill="{RED}" {stroke(3.5)}/><path d="M80 -38 L102 -34" stroke="{RED}" stroke-width="7" stroke-linecap="round"/>' if cap else "")
    body = (f'<ellipse cx="-26" cy="-46" rx="40" ry="20" transform="rotate({-32 + w} -6 -30)" fill="#DDEFF5" fill-opacity="0.7" {stroke(3)}/>'
            f'{legs}{bask}{fuzz}'
            f'<ellipse cx="-10" cy="4" rx="{rx}" ry="{ry}" fill="{body_col}" {stroke(5)}/>{stripes}'
            f'<path d="M{-10 - rx - 2} 4 l-16 4 l14 6 Z" fill="{INK}"/>'
            f'<ellipse cx="-10" cy="4" rx="{rx}" ry="{ry}" fill="none" {stroke(5)}/>'
            f'<path d="M-30 -24 Q-10 -36 14 -28" fill="none" stroke="#FFE39A" stroke-width="8" stroke-linecap="round" opacity="0.7"/>'
            f'<circle cx="58" cy="-2" r="34" fill="#3B2A1E" {stroke(5)}/>'
            f'<path d="M50 -32 Q44 -60 30 -66 M66 -32 Q74 -60 88 -62" fill="none" {stroke(3.5)}/><circle cx="30" cy="-66" r="5" fill="{INK}"/><circle cx="88" cy="-62" r="5" fill="{INK}"/>'
            f'{crown}{capp}'
            f'<circle cx="50" cy="-8" r="11" fill="#FFF" {stroke(3)}/><circle cx="72" cy="-6" r="11" fill="#FFF" {stroke(3)}/>'
            f'<circle cx="{52 + lx}" cy="{-7 + ly}" r="5" fill="{INK}"/><circle cx="{74 + lx}" cy="{-5 + ly}" r="5" fill="{INK}"/>{m}'
            f'<ellipse cx="-34" cy="-52" rx="44" ry="20" transform="rotate({-12 - w} -6 -30)" fill="#DDEFF5" fill-opacity="0.75" {stroke(3)}/>')
    fl = " scale(-1 1)" if flip else ""
    return f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({s:.3f}){fl}" opacity="{alpha:.2f}">{body}</g>'


def bumblebee(x, y, s=1.0, fr=0, rot=0, flip=False, look=(0, 0), shake=0.0):
    sx = shake * math.sin(fr * 2.7) * 6
    w = (fr % 2) * 16
    fuzz = "".join(f'<path d="M{-6 + 70 * math.cos(a):.1f} {6 + 56 * math.sin(a):.1f} l{9 * math.cos(a):.1f} {9 * math.sin(a):.1f}" stroke="{INK}" stroke-width="3.5" stroke-linecap="round"/>'
                   for a in [k * 0.33 for k in range(19)])
    body = (f'<ellipse cx="-20" cy="-50" rx="30" ry="15" transform="rotate({-30 + w} -6 -30)" fill="#DDEFF5" fill-opacity="0.7" {stroke(3)}/>'
            + "".join(f'<path d="M{dx} 50 q-4 20 -10 32" fill="none" {stroke(4)}/>' for dx in (-30, -6, 18)) + fuzz +
            f'<ellipse cx="-6" cy="6" rx="70" ry="56" fill="#2F2622" {stroke(5)}/>'
            f'<path d="{band(70, 56, -14, 14, -6, 6)}" fill="{MUSTARD}"/><path d="{band(70, 56, 30, 70, -6, 6)}" fill="{MUSTARD}"/>'
            f'<path d="{band(70, 56, -70, -44, -6, 6)}" fill="#F6F0E2"/>'
            f'<ellipse cx="-6" cy="6" rx="70" ry="56" fill="none" {stroke(5)}/>'
            f'<circle cx="70" cy="0" r="32" fill="#2F2622" {stroke(5)}/>'
            f'<path d="M64 -28 Q60 -52 48 -58 M80 -28 Q88 -52 100 -54" fill="none" {stroke(3.5)}/>'
            f'<circle cx="62" cy="-6" r="11" fill="#FFF" {stroke(3)}/><circle cx="84" cy="-4" r="11" fill="#FFF" {stroke(3)}/>'
            f'<circle cx="{64 + look[0]}" cy="{-5 + look[1]}" r="5" fill="{INK}"/><circle cx="{86 + look[0]}" cy="{-3 + look[1]}" r="5" fill="{INK}"/>'
            f'<path d="M62 16 Q72 24 82 15" fill="none" stroke="#F6F0E2" stroke-width="3.5"/>'
            f'<ellipse cx="-28" cy="-56" rx="36" ry="17" transform="rotate({-10 - w} -6 -30)" fill="#DDEFF5" fill-opacity="0.75" {stroke(3)}/>')
    fl = " scale(-1 1)" if flip else ""
    return f'<g transform="translate({x + sx:.1f} {y:.1f}) rotate({rot:.1f}) scale({s:.3f}){fl}">{body}</g>'


def solitary_bee(x, y, s=1.0, fr=0, col="#4A5A78", stripe="#C9D6E0", flip=False, rot=0):
    """slim mason / leafcutter / sweat bee"""
    w = (fr % 2) * 18
    body = (f'<ellipse cx="-20" cy="-30" rx="30" ry="12" transform="rotate({-28 + w} 0 -20)" fill="#DDEFF5" fill-opacity="0.7" {stroke(3)}/>'
            + "".join(f'<path d="M{dx} 18 q-4 16 -10 26" fill="none" {stroke(3)}/>' for dx in (-14, 2, 16)) +
            f'<ellipse cx="-20" cy="4" rx="46" ry="22" fill="{col}" {stroke(4)}/>'
            + "".join(f'<path d="{band(46, 22, x1, x1 + 6, -20, 4)}" fill="{stripe}"/>' for x1 in (-30, -14, 2)) +
            f'<ellipse cx="-20" cy="4" rx="46" ry="22" fill="none" {stroke(4)}/>'
            f'<circle cx="34" cy="-2" r="22" fill="{col}" {stroke(4)}/><circle cx="38" cy="-8" r="8" fill="#FFF" {stroke(2.5)}/><circle cx="40" cy="-7" r="3.5" fill="{INK}"/>'
            f'<path d="M30 -20 Q26 -40 16 -44 M42 -20 Q48 -40 60 -42" fill="none" {stroke(3)}/>'
            f'<ellipse cx="-24" cy="-34" rx="32" ry="12" transform="rotate({-10 - w} 0 -20)" fill="#DDEFF5" fill-opacity="0.75" {stroke(3)}/>')
    fl = " scale(-1 1)" if flip else ""
    return f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({s:.3f}){fl}">{body}</g>'


def wasp(x, y, s=1.0, fr=0, flip=False):
    w = (fr % 2) * 18
    body = (f'<ellipse cx="-10" cy="-34" rx="34" ry="12" transform="rotate({-25 + w})" fill="#DDEFF5" fill-opacity="0.7" {stroke(3)}/>'
            f'<ellipse cx="-60" cy="10" rx="44" ry="22" fill="{MUSTARD}" {stroke(4)}/>'
            + "".join(f'<path d="{band(44, 22, x1, x1 + 10, -60, 10)}" fill="{INK}"/>' for x1 in (-30, -10, 10)) +
            f'<ellipse cx="-60" cy="10" rx="44" ry="22" fill="none" {stroke(4)}/><path d="M-16 6 L4 0" stroke="{INK}" stroke-width="6"/>'
            f'<ellipse cx="18" cy="-2" rx="20" ry="16" fill="{MUSTARD}" {stroke(4)}/><circle cx="48" cy="-8" r="18" fill="{MUSTARD}" {stroke(4)}/>'
            f'<circle cx="54" cy="-12" r="7" fill="{INK}"/><path d="M44 -24 Q40 -44 28 -46 M54 -24 Q62 -44 74 -44" fill="none" {stroke(3)}/>'
            + "".join(f'<path d="M{dx} 14 q-6 18 -14 28" fill="none" {stroke(3)}/>' for dx in (6, 18, 30)))
    fl = " scale(-1 1)" if flip else ""
    return f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.3f}){fl}">{body}</g>'


def butterfly(x, y, s=1.0, fr=0, c1="#E58A4A", c2="#F2B33D"):
    k = 0.35 + 0.65 * abs(math.cos(fr * 0.5))
    wing = (f'<g transform="scale({k:.2f} 1)"><path d="M0 0 Q-90 -110 -130 -40 Q-110 10 0 4 Z" fill="{c1}" {SW4}/>'
            f'<path d="M0 4 Q-80 30 -90 90 Q-30 80 0 10 Z" fill="{c2}" {SW4}/><circle cx="-80" cy="-50" r="14" fill="#FFF6E0" {stroke(3)}/>'
            f'<path d="M0 0 Q90 -110 130 -40 Q110 10 0 4 Z" fill="{c1}" {SW4}/><path d="M0 4 Q80 30 90 90 Q30 80 0 10 Z" fill="{c2}" {SW4}/>'
            f'<circle cx="80" cy="-50" r="14" fill="#FFF6E0" {stroke(3)}/></g>')
    return (f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.3f})">{wing}<ellipse cx="0" cy="10" rx="9" ry="44" fill="{INK}"/>'
            f'<path d="M-4 -30 Q-20 -64 -32 -66 M4 -30 Q20 -64 32 -66" fill="none" {stroke(3)}/></g>')


def hummingbird(x, y, s=1.0, fr=0, flip=False):
    w = -50 if fr % 2 else 30
    fl = " scale(-1 1)" if flip else ""
    return (f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.3f}){fl}"><path d="M-10 -10 Q-50 {w - 30} -90 {w}" fill="none" stroke="#7FB4BE" stroke-width="26" stroke-linecap="round" opacity="0.7"/>'
            f'<ellipse cx="0" cy="0" rx="46" ry="26" fill="#3E9A6A" {SW5}/><path d="M-40 6 L-90 30 L-80 0 Z" fill="#2E6E4A" {SW4}/>'
            f'<path d="M10 14 Q30 24 44 10" fill="#C9563F"/><circle cx="44" cy="-10" r="20" fill="#3E9A6A" {SW5}/>'
            f'<path d="M62 -12 L120 -6" stroke="{INK}" stroke-width="5" stroke-linecap="round"/><circle cx="50" cy="-14" r="5" fill="{INK}"/></g>')


def bee_eater(x, y, s=1.0, look=0):
    return (f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.3f})"><path d="M-40 30 L-110 120 L-80 126 L-30 50 Z" fill="#3E9A6A" {SW5}/>'
            f'<ellipse cx="0" cy="0" rx="60" ry="44" fill="#3E9AA6" {SW5}/><ellipse cx="10" cy="20" rx="40" ry="20" fill="#7FC6C0"/>'
            f'<circle cx="48" cy="-30" r="34" fill="#C98A3E" {SW5}/><path d="M24 -36 L80 -30" stroke="{INK}" stroke-width="12" stroke-linecap="round"/>'
            f'<path d="M30 -8 Q50 -2 70 -14" fill="{MUSTARD}" {SW4}/><path d="M78 -34 Q120 -30 140 -16 Q110 -22 78 -26 Z" fill="{INK}"/>'
            f'<circle cx="{52 + look}" cy="-36" r="5" fill="#FFF"/></g>')


def songbird(x, y, s=1.0, fr=0, look=0):
    return bird(x, y, s, fr, col="#B5543F", belly="#F3D9B1")


def mouse(x, y, s=1.0, t=0.0):
    return (f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.3f})"><path d="M-60 20 Q-110 10 -130 {30 + 6 * math.sin(t * 4):.0f}" fill="none" stroke="#C9A77C" stroke-width="6" stroke-linecap="round"/>'
            f'<ellipse cx="0" cy="0" rx="64" ry="40" fill="#A8A096" {SW5}/><circle cx="56" cy="-14" r="30" fill="#A8A096" {SW5}/>'
            f'<circle cx="44" cy="-46" r="18" fill="#E9B8B0" {SW4}/><circle cx="66" cy="-14" r="5" fill="{INK}"/><circle cx="86" cy="-6" r="6" fill="#D96C8A"/>'
            f'<path d="M80 -4 l26 -6 M80 0 l26 4" stroke="{INK}" stroke-width="2"/></g>')


def cow(x, y, s=1.0, t=0.0, chew=0.0):
    tail = 10 * math.sin(t * 2)
    jaw = 6 * abs(math.sin(chew * 8))
    spots = "".join(f'<path d="M{a} {b} q20 -20 40 0 q10 20 -10 30 q-30 10 -30 -30 Z" fill="{INK}"/>' for a, b in [(-100, -40), (0, -20), (50, -60)])
    return (f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.3f})"><path d="M-150 -40 Q-180 {20 + tail:.0f} -170 {60 + tail:.0f}" fill="none" {stroke(6)}/>'
            + "".join(f'<rect x="{lx}" y="20" width="26" height="110" fill="#F6F0E2" {SW5}/><rect x="{lx}" y="112" width="26" height="18" fill="{INK}"/>' for lx in (-130, -90, 60, 100)) +
            f'<rect x="-160" y="-90" width="300" height="140" rx="60" fill="#F6F0E2" {SW5}/>{spots}'
            f'<ellipse cx="-20" cy="54" rx="34" ry="18" fill="#E9B8B0" {SW4}/>'
            f'<g transform="translate(170 -60)"><path d="M-40 -40 L-60 -70 M40 -40 L60 -70" stroke="#E6DCC8" stroke-width="12" stroke-linecap="round"/>'
            f'<ellipse cx="0" cy="0" rx="62" ry="56" fill="#F6F0E2" {SW5}/><ellipse cx="0" cy="{40 + jaw:.0f}" rx="52" ry="32" fill="#E9B8B0" {SW5}/>'
            f'<circle cx="-16" cy="38" r="6" fill="{INK}"/><circle cx="16" cy="38" r="6" fill="{INK}"/>'
            f'<circle cx="-24" cy="-10" r="8" fill="{INK}"/><circle cx="24" cy="-10" r="8" fill="{INK}"/>'
            f'<ellipse cx="-70" cy="-20" rx="26" ry="12" fill="#F6F0E2" {SW4}/><ellipse cx="70" cy="-20" rx="26" ry="12" fill="#F6F0E2" {SW4}/></g></g>')


def mite(x, y, s=1.0, t=0.0):
    legs = "".join(f'<path d="M{side * 20} {k * 10 - 10} q{side * 20} {-6 + 6 * math.sin(t * 8 + k)} {side * 34} {k * 8}" fill="none" {stroke(4)}/>' for side in (-1, 1) for k in range(4))
    return (f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.3f})">{legs}<ellipse cx="0" cy="0" rx="40" ry="30" fill="#8A3A2E" {SW5}/>'
            f'<path d="M-24 -10 Q0 -22 24 -10" fill="none" stroke="#B5655E" stroke-width="6" stroke-linecap="round"/>'
            f'<circle cx="-10" cy="6" r="5" fill="#FFF"/><circle cx="10" cy="6" r="5" fill="#FFF"/><circle cx="-10" cy="7" r="2.5" fill="{INK}"/><circle cx="10" cy="7" r="2.5" fill="{INK}"/></g>')


def robot_bee(x, y, s=1.0, fr=0, t=0.0):
    w = (fr % 2) * 20
    led = RED if int(t * 4) % 2 else "#7FE08A"
    return (f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.3f})">'
            f'<rect x="-40" y="-70" width="50" height="10" transform="rotate({-20 + w} 0 -40)" fill="#DDEFF5" fill-opacity="0.8" {stroke(3)}/>'
            f'<rect x="-10" y="-70" width="50" height="10" transform="rotate({20 - w} 0 -40)" fill="#DDEFF5" fill-opacity="0.8" {stroke(3)}/>'
            f'<rect x="-50" y="-36" width="100" height="70" rx="18" fill="#B8BEC4" {SW5}/><path d="M-50 -6 L50 -6" stroke="#6E7880" stroke-width="5"/>'
            f'<circle cx="-18" cy="-14" r="9" fill="#2E3A57" {SW4}/><circle cx="18" cy="-14" r="9" fill="#2E3A57" {SW4}/><circle cx="0" cy="16" r="6" fill="{led}"/>'
            f'<path d="M-30 34 l-10 20 M0 34 l0 22 M30 34 l10 20" {stroke(4)}/></g>')


def midge(x, y, s=1.0, fr=0):
    w = (fr % 2) * 20
    return (f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.3f})"><ellipse cx="-6" cy="-16" rx="22" ry="8" transform="rotate({-30 + w})" fill="#DDEFF5" fill-opacity="0.7" {stroke(2.5)}/>'
            f'<path d="M-30 6 L16 -4" stroke="#6E625A" stroke-width="12" stroke-linecap="round"/><circle cx="22" cy="-6" r="10" fill="#6E625A" {stroke(3)}/>'
            f'<circle cx="26" cy="-9" r="4" fill="#FFF"/><path d="M0 4 l-6 18 M8 2 l2 18" {stroke(2.5)}/></g>')


# ====================== plants ======================
def daisy(x, y, s=1.0, t=0.0, i=0, col="#FFFFFF", center=MUSTARD, stem=110):
    sw = 4 * math.sin(t * 1.4 + i)
    petals = "".join(f'<ellipse cx="0" cy="-22" rx="9" ry="20" transform="rotate({k * 30})" fill="{col}" {stroke(3)}/>' for k in range(12))
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({sw:.2f}) scale({s:.3f})"><path d="M0 0 Q4 {-stem / 2} 0 {-stem}" fill="none" stroke="#4E7F3A" stroke-width="6"/>'
            f'<path d="M0 -40 q22 -16 34 -6 q-18 14 -34 6 Z" fill="#7FA65A" {stroke(3)}/><g transform="translate(0 {-stem})">{petals}<circle r="12" fill="{center}" {stroke(3)}/></g></g>')


def tulip(x, y, s=1.0, t=0.0, i=0, col="#E0533A"):
    sw = 3 * math.sin(t * 1.3 + i)
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({sw:.2f}) scale({s:.3f})"><path d="M0 0 L0 -110" stroke="#4E7F3A" stroke-width="7"/>'
            f'<path d="M0 -20 Q-40 -60 -20 -100 Q-10 -60 0 -30 Z" fill="#7FA65A" {stroke(3)}/>'
            f'<path d="M-24 -110 Q-28 -150 -14 -160 L0 -140 L14 -160 Q28 -150 24 -110 Q0 -96 -24 -110 Z" fill="{col}" {stroke(4)}/></g>')


def lavender(x, y, s=1.0, t=0.0, i=0):
    sw = 4 * math.sin(t * 1.5 + i)
    buds = "".join(f'<ellipse cx="{(-1) ** k * 5}" cy="{-90 - k * 10}" rx="6" ry="8" fill="#8E7CC3" {stroke(2)}/>' for k in range(7))
    return f'<g transform="translate({x:.1f} {y:.1f}) rotate({sw:.2f}) scale({s:.3f})"><path d="M0 0 L0 -90" stroke="#6E8B5A" stroke-width="5"/>{buds}</g>'


def rose(x, y, s=1.0, t=0.0, i=0, col="#D96C8A"):
    sw = 3 * math.sin(t * 1.2 + i)
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({sw:.2f}) scale({s:.3f})"><path d="M0 0 L0 -100" stroke="#4E7F3A" stroke-width="6"/>'
            f'<path d="M0 -60 q-30 -10 -36 -30 q22 0 36 20 Z" fill="#7FA65A" {stroke(3)}/>'
            f'<circle cx="0" cy="-120" r="30" fill="{col}" {SW4}/><path d="M-14 -122 Q0 -140 14 -122 Q4 -108 -8 -116" fill="none" stroke="#A8435E" stroke-width="4"/></g>')


def sunflower(x, y, s=1.0, t=0.0, i=0):
    sw = 2 * math.sin(t + i)
    petals = "".join(f'<ellipse cx="0" cy="-46" rx="14" ry="30" transform="rotate({k * 22.5})" fill="{MUSTARD}" {stroke(3)}/>' for k in range(16))
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({sw:.2f}) scale({s:.3f})"><path d="M0 0 L0 -200" stroke="#4E7F3A" stroke-width="10"/>'
            f'<path d="M0 -80 q-60 -30 -70 0 q40 20 70 0 Z M0 -120 q60 -30 70 0 q-40 20 -70 0 Z" fill="#6E9A5E" {stroke(3)}/>'
            f'<g transform="translate(0 -220)">{petals}<circle r="34" fill="#6B4A35" {SW4}/></g></g>')


def flower_bed(x0, x1, y, t, seed=1, density=1.0, scale=1.0, fade=0.0):
    r = rnd(seed)
    out = ""
    n = int((x1 - x0) / 46 * density)
    kinds = [daisy, tulip, lavender, rose, daisy]
    cols = ["#FFFFFF", "#F6A6B8", "#E0533A", "#F2B33D", "#9DB8D6", "#C9B6E4"]
    for k in range(n):
        x = r.uniform(x0, x1); yy = y + r.uniform(-20, 30); s = r.uniform(0.55, 0.95) * scale
        f = r.choice(kinds)
        if fade and r.random() < fade:
            continue
        if f in (daisy,):
            out += daisy(x, yy, s, t, k, col=r.choice(cols))
        elif f is tulip:
            out += tulip(x, yy, s, t, k, col=r.choice(["#E0533A", "#F2B33D", "#D96C8A", "#F6F0E2"]))
        elif f is rose:
            out += rose(x, yy, s, t, k, col=r.choice(["#D96C8A", "#E0533A", "#F6A6B8"]))
        else:
            out += lavender(x, yy, s, t, k)
    return out


def grass_tufts(x0, x1, y, seed=2, col="#5E8E4A", n=40, t=0.0):
    r = rnd(seed)
    out = ""
    for k in range(n):
        x = r.uniform(x0, x1); yy = y + r.uniform(-10, 40); h = r.uniform(16, 34); sw = 3 * math.sin(t * 2 + k)
        out += f'<path d="M{x - 8:.0f} {yy:.0f} l{-4 + sw:.1f} {-h:.0f} M{x:.0f} {yy:.0f} l{sw:.1f} {-h - 8:.0f} M{x + 8:.0f} {yy:.0f} l{4 + sw:.1f} {-h:.0f}" stroke="{col}" stroke-width="4" stroke-linecap="round"/>'
    return out


def blossom_tree(x, y, s=1.0, t=0.0, i=0, col="#F8E1E7", bare=False, petals_fall=False):
    r = rnd(100 + i)
    out = (f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.3f})"><path d="M-14 0 Q-10 -80 -40 -150 M10 0 Q14 -90 50 -160 M0 -60 Q0 -120 6 -190" fill="none" stroke="#6B4A35" stroke-width="22" stroke-linecap="round"/>'
           f'<path d="M-14 0 Q-10 -80 -40 -150 M10 0 Q14 -90 50 -160 M0 -60 Q0 -120 6 -190" fill="none" {stroke(3)} opacity="0.5"/>')
    if not bare:
        for k in range(16):
            cx, cy, rr = r.uniform(-120, 120), r.uniform(-260, -130), r.uniform(36, 60)
            out += f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="{rr:.0f}" fill="{col}" {stroke(3.5)}/>'
        for k in range(26):
            cx, cy = r.uniform(-130, 130), r.uniform(-280, -120)
            out += f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="5" fill="#E58FA6"/>'
    if petals_fall:
        for k in range(8):
            u = ((t * 0.2 + k / 8) % 1)
            out += f'<ellipse cx="{r.uniform(-150, 150) + 40 * math.sin(t + k):.0f}" cy="{-200 + 260 * u:.0f}" rx="6" ry="4" fill="#F6C6D2" opacity="{1 - u:.2f}"/>'
    return out + "</g>"


def fruit_tree(x, y, s=1.0, t=0.0, i=0, fruit="#E0533A", n=10):
    r = rnd(200 + i)
    out = tree(0, 0, 1.0, "#5E8E4A", t, i)
    fr = "".join(f'<circle cx="{r.uniform(-120, 120):.0f}" cy="{r.uniform(-300, -150):.0f}" r="14" fill="{fruit}" {stroke(3)}/>' for _ in range(n))
    return f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.3f})">{out}{fr}</g>'


# ====================== food ======================
def apple(x, y, s=1.0, col="#E0533A"):
    return (f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.3f})"><path d="M0 -30 Q-40 -50 -44 -6 Q-44 40 0 44 Q44 40 44 -6 Q40 -50 0 -30 Z" fill="{col}" {SW4}/>'
            f'<path d="M0 -30 L4 -50" {stroke(4)}/><path d="M6 -44 q18 -14 26 -2 q-14 10 -26 2 Z" fill="#7FA65A" {stroke(3)}/>'
            f'<path d="M-26 -14 Q-24 -26 -14 -30" fill="none" stroke="#FFFFFF" stroke-width="5" stroke-linecap="round" opacity="0.6"/></g>')


def cherry(x, y, s=1.0):
    return (f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.3f})"><path d="M-14 0 Q-6 -50 16 -60 M14 6 Q12 -40 16 -60" fill="none" stroke="#4E7F3A" stroke-width="4"/>'
            f'<circle cx="-16" cy="8" r="18" fill="#B5263A" {SW4}/><circle cx="16" cy="12" r="18" fill="#B5263A" {SW4}/></g>')


def blueberry(x, y, s=1.0):
    return (f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.3f})">' + "".join(
        f'<circle cx="{dx}" cy="{dy}" r="16" fill="#4A5A9A" {stroke(3)}/><path d="M{dx - 4} {dy - 10} l4 4 l4 -4" stroke="{INK}" stroke-width="2"/>' for dx, dy in [(-14, 0), (14, 2), (0, -18)]) + '</g>')


def strawberry(x, y, s=1.0):
    seeds = "".join(f'<ellipse cx="{dx}" cy="{dy}" rx="2" ry="3" fill="#F6E39A"/>' for dx, dy in [(-12, -6), (8, -10), (-4, 8), (12, 6), (-14, 16), (4, 22)])
    return (f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.3f})"><path d="M-28 -16 Q0 -28 28 -16 Q24 30 0 40 Q-24 30 -28 -16 Z" fill="#E0533A" {SW4}/>{seeds}'
            f'<path d="M-20 -18 L-8 -30 L0 -20 L8 -30 L20 -18 Z" fill="#4E7F3A" {stroke(3)}/></g>')


def almond(x, y, s=1.0, r_=0):
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({r_}) scale({s:.3f})"><path d="M0 -34 Q24 -10 18 18 Q10 34 0 36 Q-10 34 -18 18 Q-24 -10 0 -34 Z" fill="#B5784A" {SW4}/>'
            f'<path d="M-6 -16 Q-10 4 -4 22 M6 -10 Q10 8 4 24" fill="none" stroke="#8A5A35" stroke-width="3"/></g>')


def avocado(x, y, s=1.0):
    return (f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.3f})"><path d="M0 -44 Q30 -40 34 10 Q34 44 0 46 Q-34 44 -34 10 Q-30 -40 0 -44 Z" fill="#4E7F3A" {SW4}/>'
            f'<path d="M0 -30 Q20 -26 22 10 Q22 34 0 36 Q-22 34 -22 10 Q-20 -26 0 -30 Z" fill="#D8E4A0"/><circle cx="0" cy="14" r="14" fill="#8A5A35" {stroke(3)}/></g>')


def melon(x, y, s=1.0):
    stripes = "".join(f'<path d="M{dx} -40 Q{dx * 1.3:.0f} 0 {dx} 40" fill="none" stroke="#3E6E3A" stroke-width="6"/>' for dx in (-30, -10, 10, 30))
    return f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.3f})"><ellipse rx="50" ry="42" fill="#7FA65A" {SW4}/>{stripes}<ellipse rx="50" ry="42" fill="none" {SW4}/></g>'


def pumpkin(x, y, s=1.0):
    return (f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.3f})">' + "".join(f'<ellipse cx="{dx}" cy="0" rx="26" ry="38" fill="#E58A3A" {SW4}/>' for dx in (-30, 30, -12, 12)) +
            f'<path d="M0 -38 q4 -20 16 -24" fill="none" stroke="#4E7F3A" stroke-width="8" stroke-linecap="round"/></g>')


def coffee(x, y, s=1.0):
    return (f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.3f})"><path d="M-40 -30 L40 -30 L32 40 Q0 50 -32 40 Z" fill="#F6F0E2" {SW4}/>'
            f'<ellipse cx="0" cy="-30" rx="40" ry="10" fill="#6B4A35" {SW4}/><path d="M40 -14 Q66 -10 56 14 Q50 24 36 20" fill="none" {stroke(5)}/>'
            f'<path d="M-12 -50 q-8 -14 4 -24 M10 -50 q-8 -14 4 -24" fill="none" stroke="#C8BFA8" stroke-width="4"/></g>')


def bread(x, y, s=1.0):
    return (f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.3f})"><path d="M-70 20 Q-80 -40 -20 -46 Q0 -60 20 -46 Q80 -40 70 20 Z" fill="#D8A060" {SW5}/>'
            f'<path d="M-30 -30 l-10 20 M0 -36 l-10 22 M30 -30 l-10 20" stroke="#A8743A" stroke-width="6" stroke-linecap="round"/></g>')


def rice_bowl(x, y, s=1.0):
    grains = "".join(f'<ellipse cx="{dx}" cy="{dy}" rx="6" ry="3" fill="#FFFFFF" {stroke(1.5)}/>' for dx, dy in [(-30, -20), (-10, -28), (12, -24), (30, -16), (0, -14), (-20, -10), (20, -6)])
    return (f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.3f})"><path d="M-60 -10 Q0 -60 60 -10 Z" fill="#F6F0E2" {SW4}/>{grains}'
            f'<path d="M-70 -10 L70 -10 Q60 50 0 52 Q-60 50 -70 -10 Z" fill="#5B8DB8" {SW5}/><path d="M-60 10 Q0 22 60 10" fill="none" stroke="#F6F0E2" stroke-width="5"/></g>')


def corn(x, y, s=1.0, r_=0):
    kern = "".join(f'<circle cx="{dx}" cy="{dy}" r="6" fill="{MUSTARD}" {stroke(1.5)}/>' for dy in range(-60, 50, 14) for dx in (-10, 0, 10))
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({r_}) scale({s:.3f})"><path d="M-6 60 Q-60 20 -30 -40 Q-20 10 0 60 Z M6 60 Q60 20 30 -40 Q20 10 0 60 Z" fill="#7FA65A" {stroke(3)}/>'
            f'<ellipse cx="0" cy="-6" rx="22" ry="70" fill="#F2C94A" {SW4}/>{kern}</g>')


def potato(x, y, s=1.0):
    return f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.3f})"><ellipse rx="44" ry="30" fill="#C9A06A" {SW4}/><circle cx="-14" cy="-6" r="3" fill="#8A6A4E"/><circle cx="16" cy="6" r="3" fill="#8A6A4E"/></g>'


def honey_jar(x, y, s=1.0, fill=1.0):
    h = 140 * fill
    return (f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.3f})"><rect x="-70" y="-150" width="140" height="160" rx="26" fill="#F6F0E2" fill-opacity="0.5" {SW5}/>'
            f'<rect x="-64" y="{4 - h:.0f}" width="128" height="{h:.0f}" rx="20" fill="#E7A33A" opacity="0.95"/>'
            f'<rect x="-70" y="-150" width="140" height="160" rx="26" fill="none" {SW5}/><rect x="-78" y="-176" width="156" height="34" rx="8" fill="{RED}" {SW4}/>'
            f'<path d="M-78 -160 L78 -160" stroke="#FFF6E0" stroke-width="4" stroke-dasharray="10 8"/>'
            f'<rect x="-46" y="-96" width="92" height="56" rx="8" fill="#FFF6E0" {stroke(3)}/>' + text(0, -58, "HONEY", 26) + '</g>')


def price_tag(x, y, label, s=1.0, r_=0):
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({r_:.1f}) scale({s:.3f})"><path d="M-50 -24 L40 -24 L60 0 L40 24 L-50 24 Z" fill="#FFF6E0" {SW4}/>'
            f'<circle cx="40" cy="0" r="5" fill="{INK}"/>' + text(-6, 12, label, 30, RED) + '</g>')


# ====================== props / structures ======================
def hive_box(x, y, s=1.0, col="#F6F0E2", lid=0.0, levels=2):
    out = f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.3f})"><rect x="-80" y="0" width="160" height="30" fill="#8A5A35" {SW4}/>'
    for k in range(levels):
        yy = -k * 90 - 90
        out += f'<rect x="-90" y="{yy}" width="180" height="90" fill="{col}" {SW5}/><path d="M-90 {yy + 30} L90 {yy + 30}" stroke="#00000022" stroke-width="3"/>'
        out += f'<rect x="-40" y="{yy + 40}" width="80" height="14" rx="6" fill="#00000033"/>'
    ly = -levels * 90 - 26 - 140 * ease(lid)
    out += f'<rect x="-100" y="{ly:.0f}" width="200" height="28" rx="4" fill="#B5784A" {SW5}/>'
    out += f'<rect x="-30" y="-14" width="60" height="10" fill="{INK}"/></g>'
    return out


def smoker(x, y, s=1.0, t=0.0):
    puffs = "".join(f'<circle cx="{10 + 20 * k + 6 * math.sin(t * 2 + k):.0f}" cy="{-90 - 34 * k - (t * 30) % 30:.0f}" r="{14 + 6 * k}" fill="#E9EEF0" opacity="{0.6 - 0.12 * k:.2f}"/>' for k in range(4))
    return (f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.3f})"><rect x="-26" y="-60" width="52" height="80" rx="8" fill="#C9C6C0" {SW4}/>'
            f'<path d="M-26 -60 L0 -84 L26 -60 Z" fill="#A8A49A" {SW4}/><rect x="26" y="-40" width="30" height="40" fill="#8A5A35" {SW4}/>{puffs}</g>')


def beekeeper(x, y, s=1.0, t=0.0, T=1.0, arms=(20, 20), mouth="flat", tool=None, flip=False):
    body = person(x, y, s, skin="#C68E64", outfit="coat", outfit_color="#F4F4F0", arms=arms, mouth=mouth, eyes=auto_eyes(t, T), hand_tool=tool, flip=flip)
    hx, hy = x, y - 340 * s
    veil = (f'<g transform="translate({hx:.1f} {hy:.1f}) scale({s:.3f})">'
            f'<path d="M-90 -40 L90 -40 L80 60 Q0 80 -80 60 Z" fill="#E6E8E4" fill-opacity="0.35" {stroke(4)}/>'
            f'<path d="M-90 -40 L90 -40" stroke="#DCDCD6" stroke-width="2"/>' + "".join(f'<path d="M{xx} -40 L{xx * 0.9:.0f} 66" stroke="#9AA0A4" stroke-width="1.5" opacity="0.6"/>' for xx in range(-80, 90, 16)) +
            f'<ellipse cx="0" cy="-48" rx="110" ry="22" fill="#F4F4F0" {SW5}/><path d="M-50 -50 Q0 -110 50 -50 Z" fill="#F4F4F0" {SW5}/></g>')
    return body + veil


def ladder(x, y, h=420, s=1.0, r_=-8):
    rungs = "".join(f'<path d="M-36 {-k * 50} L36 {-k * 50}" stroke="#C9A77C" stroke-width="9"/>' for k in range(1, int(h / 50)))
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({r_}) scale({s:.3f})"><path d="M-40 0 L-30 {-h} M40 0 L30 {-h}" stroke="#A8743A" stroke-width="12"/>{rungs}'
            f'<path d="M-40 0 L-30 {-h} M40 0 L30 {-h}" fill="none" {stroke(3)} opacity="0.5"/></g>')


def feather_brush(x, y, s=1.0, r_=0):
    fe = "".join(f'<path d="M0 0 Q{a * 0.6:.0f} -40 {a:.0f} -70" fill="none" stroke="#F6F0E2" stroke-width="10" stroke-linecap="round"/>' for a in (-30, -14, 0, 14, 30))
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({r_}) scale({s:.3f})"><path d="M0 0 L0 160" stroke="#C9A77C" stroke-width="10" stroke-linecap="round"/>'
            f'<g>{fe}</g>' + "".join(f'<path d="M0 0 Q{a * 0.6:.0f} -40 {a:.0f} -70" fill="none" {stroke(2)} opacity="0.4"/>' for a in (-30, 0, 30)) + '</g>')


def truck(x, y, s=1.0, t=0.0, hives=True, col="#C9563F"):
    wh = (t * 400) % 360
    hv = "".join(f'<rect x="{-260 + c * 62}" y="{-150 - r_ * 40}" width="56" height="38" fill="{["#F6F0E2", "#9DB8D6", MUSTARD, "#9CC5A1"][(c + r_) % 4]}" {stroke(3)}/>' for c in range(6) for r_ in range(3)) if hives else ""
    wheel = lambda wx: f'<g transform="translate({wx} 0) rotate({wh:.0f})"><circle r="34" fill="#2F2A28" {SW4}/><circle r="12" fill="#C9C6C0"/><path d="M-12 0 L12 0" stroke="{INK}" stroke-width="3"/></g>'
    return (f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.3f})"><rect x="-280" y="-34" width="400" height="30" fill="#6E6A66" {SW4}/>{hv}'
            f'<path d="M-270 -40 L110 -40" stroke="#8A5A35" stroke-width="6"/>'
            f'<path d="M120 -150 L220 -150 L260 -80 L260 -10 L120 -10 Z" fill="{col}" {SW5}/><path d="M150 -136 L210 -136 L238 -86 L150 -86 Z" fill="#BFD9D6" {SW4}/>'
            + wheel(-200) + wheel(-110) + wheel(200) + '</g>')


def tractor_sprayer(x, y, s=1.0, t=0.0, spray=True):
    wh = (t * 200) % 360
    mist = "".join(f'<circle cx="{-250 + k * 40 + 10 * math.sin(t * 3 + k):.0f}" cy="{-20 + 12 * math.sin(t * 5 + k):.0f}" r="{30 + 10 * (k % 3)}" fill="#E9EEF0" opacity="0.5"/>' for k in range(9)) if spray else ""
    return (f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.3f})">{mist}<path d="M-300 -60 L-20 -60" stroke="#6E6A66" stroke-width="10"/>'
            + "".join(f'<path d="M{xx} -60 l0 20" stroke="#6E6A66" stroke-width="6"/>' for xx in range(-290, -20, 40)) +
            f'<rect x="-20" y="-150" width="160" height="110" rx="12" fill="#4E7F3A" {SW5}/><rect x="40" y="-230" width="100" height="90" rx="8" fill="#BFD9D6" fill-opacity="0.7" {SW5}/>'
            f'<rect x="-60" y="-140" width="60" height="80" rx="10" fill="#F6F0E2" {SW4}/>'
            f'<g transform="translate(110 -20) rotate({wh:.0f})"><circle r="60" fill="#2F2A28" {SW5}/><circle r="22" fill="{MUSTARD}"/></g>'
            f'<g transform="translate(-10 0) rotate({wh:.0f})"><circle r="36" fill="#2F2A28" {SW5}/><circle r="12" fill="{MUSTARD}"/></g></g>')


def bulldozer(x, y, s=1.0, t=0.0):
    tr = "".join(f'<rect x="{-150 + k * 30 - (t * 60) % 30:.0f}" y="-40" width="14" height="40" fill="#2F2A28"/>' for k in range(10))
    return (f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.3f})"><rect x="-160" y="-44" width="300" height="48" rx="24" fill="#4A4442" {SW5}/>{tr}'
            f'<rect x="-120" y="-150" width="200" height="110" rx="10" fill="{MUSTARD}" {SW5}/><rect x="-80" y="-220" width="110" height="80" fill="#BFD9D6" fill-opacity="0.7" {SW5}/>'
            f'<path d="M140 -100 L200 -100 L230 0 L150 0 Z" fill="#6E6A66" {SW5}/><path d="M80 -90 L150 -60" stroke="#4A4442" stroke-width="14"/></g>')


def hourglass(x, y, s=1.0, p=0.0, t=0.0):
    top = 1 - p
    out = (f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.3f})"><rect x="-130" y="-240" width="260" height="30" rx="8" fill="#8A5A35" {SW5}/>'
           f'<rect x="-130" y="210" width="260" height="30" rx="8" fill="#8A5A35" {SW5}/>'
           f'<path d="M-100 -210 L100 -210 Q100 -60 12 0 Q100 60 100 210 L-100 210 Q-100 60 -12 0 Q-100 -60 -100 -210 Z" fill="#E8F2F4" fill-opacity="0.5" {SW5}/>')
    cols = ["#E0533A", "#F2B33D", "#7FA65A", "#4A5A9A", "#D96C8A"]
    r = rnd(4)
    for k in range(int(28 * top)):
        out += f'<circle cx="{r.uniform(-60, 60) * (1 - k / 40):.0f}" cy="{-30 - k * 5 - r.uniform(0, 30):.0f}" r="9" fill="{cols[k % 5]}" {stroke(2)}/>'
    for k in range(int(28 * p)):
        out += f'<circle cx="{r.uniform(-70, 70) * (0.4 + k / 50):.0f}" cy="{196 - (k // 6) * 16:.0f}" r="9" fill="#C9B07E" {stroke(2)}/>'
    if 0 < p < 1:
        out += f'<path d="M0 0 L0 {190 - p * 40:.0f}" stroke="#C9B07E" stroke-width="5" stroke-dasharray="6 10" stroke-dashoffset="{-t * 60:.0f}"/>'
    return out + "</g>"


def scale_balance(x, y, s=1.0, tilt=0.0, left="", right=""):
    a = math.radians(tilt)
    lx, ly = -220 * math.cos(a), -220 * math.sin(a)
    rx_, ry_ = 220 * math.cos(a), 220 * math.sin(a)
    pan = lambda px, py, content: (f'<path d="M{px - 70:.0f} {py + 120:.0f} L{px:.0f} {py:.0f} L{px + 70:.0f} {py + 120:.0f}" fill="none" {stroke(3)}/>'
                                   f'<path d="M{px - 100:.0f} {py + 120:.0f} Q{px:.0f} {py + 170:.0f} {px + 100:.0f} {py + 120:.0f} Z" fill="#C9A77C" {SW5}/>'
                                   f'<g transform="translate({px:.0f} {py + 110:.0f})">{content}</g>')
    return (f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.3f})"><path d="M0 0 L0 330 M-90 330 L90 330" {stroke(12)}/>'
            f'<path d="M{lx:.0f} {ly:.0f} L{rx_:.0f} {ry_:.0f}" {stroke(12)}/><circle r="16" fill="{MUSTARD}" {SW4}/>'
            + pan(lx, ly, left) + pan(rx_, ry_, right) + '</g>')


def domino(x, y, s=1.0, fall=0.0, icon=""):
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({85 * ease(fall):.1f}) scale({s:.3f})"><rect x="-50" y="-240" width="100" height="240" rx="12" fill="#F6F0E2" {SW5}/>'
            f'<g transform="translate(0 -150)">{icon}</g></g>')


def bee_hotel(x, y, s=1.0):
    tubes = "".join(f'<circle cx="{cx}" cy="{cy}" r="18" fill="#C9A06A" {stroke(3)}/><circle cx="{cx}" cy="{cy}" r="9" fill="#3B2A1E"/>'
                    for cy in range(-170, -40, 40) for cx in range(-80, 90, 40))
    return (f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.3f})"><path d="M-130 -200 L0 -280 L130 -200 Z" fill="#B5543F" {SW5}/>'
            f'<rect x="-110" y="-200" width="220" height="200" fill="#8A5A35" {SW5}/><rect x="-100" y="-192" width="200" height="184" fill="#5A3A28"/>{tubes}'
            f'<rect x="-10" y="0" width="20" height="160" fill="#6B4A35" {SW4}/></g>')


def window_box(x, y, s=1.0, t=0.0):
    return (f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.3f})">' + flower_bed(-170, 170, -40, t, seed=7, density=1.6, scale=0.7) +
            f'<rect x="-190" y="-50" width="380" height="80" rx="8" fill="#B5543F" {SW5}/><path d="M-190 -20 L190 -20" stroke="#8A3A2E" stroke-width="4"/></g>')


def laptop(x, y, s=1.0, screen=""):
    return (f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.3f})"><rect x="-140" y="-190" width="280" height="180" rx="10" fill="#4A4442" {SW5}/>'
            f'<rect x="-124" y="-176" width="248" height="152" fill="#BFD9D6"/>{screen}<path d="M-170 0 L170 0 L150 -14 L-150 -14 Z" fill="#8E8A86" {SW5}/></g>')


def pie_chart(x, y, r, frac, col_a, col_b, s=1.0):
    a = frac * 2 * math.pi
    ex, ey = r * math.sin(a), -r * math.cos(a)
    large = 1 if frac > 0.5 else 0
    return (f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.3f})"><circle r="{r}" fill="{col_b}" {SW5}/>'
            + (f'<path d="M0 0 L0 {-r} A{r} {r} 0 {large} 1 {ex:.1f} {ey:.1f} Z" fill="{col_a}" {SW5}/>' if frac > 0.001 else "") + '</g>')


def hex_comb(x0, y0, cols, rows, r=34, capped=0.5, seed=3, honey=True):
    rr = rnd(seed)
    out = ""
    w = r * math.sqrt(3)
    for j in range(rows):
        for i in range(cols):
            cx = x0 + i * w + (w / 2 if j % 2 else 0)
            cy = y0 + j * r * 1.5
            pts = " ".join(f"{cx + r * math.cos(math.radians(60 * k + 30)):.1f},{cy + r * math.sin(math.radians(60 * k + 30)):.1f}" for k in range(6))
            v = rr.random()
            fill = "#F2C24A" if v < capped else ("#E7A33A" if (honey and v < capped + 0.3) else "#C98A3E")
            out += f'<polygon points="{pts}" fill="{fill}" stroke="#8A5A1E" stroke-width="4"/>'
            if v >= capped:
                out += f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="{r * 0.45:.0f}" fill="#A86A1E" opacity="0.5"/>'
            else:
                out += f'<path d="M{cx - r * 0.4:.0f} {cy - r * 0.3:.0f} q{r * 0.2:.0f} {-r * 0.2:.0f} {r * 0.4:.0f} 0" stroke="#FFF3C4" stroke-width="3" fill="none" opacity="0.7"/>'
    return out


# ====================== detailed environments ======================
def sun_rays(cx, cy, t, n=14, col="#FFF3C4", op=0.18, length=1400):
    return "".join(f'<path d="M{cx} {cy} L{cx + length * math.cos(math.radians(k * 360 / n + t * 3)):.0f} {cy + length * math.sin(math.radians(k * 360 / n + t * 3)):.0f} '
                   f'L{cx + length * math.cos(math.radians(k * 360 / n + t * 3 + 7)):.0f} {cy + length * math.sin(math.radians(k * 360 / n + t * 3 + 7)):.0f} Z" fill="{col}" opacity="{op}"/>' for k in range(n))


def clouds(t, y=180, seed=5, n=5, col="#FFFFFF", speed=12):
    r = rnd(seed)
    out = ""
    for k in range(n):
        x = (r.uniform(-300, 2200) + t * speed) % 2600 - 350
        yy = y + r.uniform(-80, 80); s = r.uniform(0.7, 1.3)
        out += (f'<g transform="translate({x:.0f} {yy:.0f}) scale({s:.2f})" opacity="0.92"><path d="M-110 30 Q-120 -10 -70 -14 Q-60 -60 -10 -52 Q20 -80 60 -50 Q110 -50 110 -6 Q140 10 110 30 Z" '
                f'fill="{col}" {stroke(4)}/></g>')
    return out


def cottage(x, y, s=1.0, t=0.0, night=False, window_open=0.0, smoke=True):
    tiles = ""
    for r_ in range(1, 5):
        yy = -300 + r_ * 36
        hw = 260 * (yy + 340) / 150 - 20
        k = -hw
        while k + 46 <= hw:
            tiles += f'<path d="M{k:.0f} {yy} q23 18 46 0" fill="none" stroke="#8A3A2E" stroke-width="4"/>'
            k += 46
    puffs = "".join(f'<circle cx="{150 + 16 * k + 10 * math.sin(t * 1.5 + k):.0f}" cy="{-440 - 50 * k - (t * 20) % 50:.0f}" r="{18 + 8 * k}" fill="#F4F6F4" opacity="{0.6 - 0.1 * k:.2f}"/>' for k in range(5)) if smoke else ""
    wl = "#F7D488" if night else "#BFD9D6"
    shutter = 70 * ease(window_open)
    return (f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.3f})">{puffs}'
            f'<rect x="130" y="-420" width="50" height="110" fill="#A8743A" {SW5}/>'
            f'<rect x="-220" y="-200" width="440" height="200" fill="#F0E0C0" {SW5}/>'
            + "".join(f'<path d="M-220 {yy} L220 {yy}" stroke="#E2CDA4" stroke-width="3"/>' for yy in range(-180, 0, 24)) +
            f'<path d="M-260 -190 L0 -340 L260 -190 Z" fill="#C9563F" {SW5}/>{tiles}<path d="M-260 -190 L0 -340 L260 -190 Z" fill="none" {SW5}/>'
            f'<rect x="-40" y="-130" width="80" height="130" rx="40" fill="#5B8DB8" {SW5}/><circle cx="24" cy="-60" r="6" fill="{MUSTARD}"/>'
            f'<rect x="-180" y="-160" width="100" height="90" fill="{wl}" {SW5}/><path d="M-130 -160 L-130 -70 M-180 -115 L-80 -115" {SW4}/>'
            f'<rect x="80" y="-160" width="100" height="90" fill="{wl}" {SW5}/><path d="M130 -160 L130 -70 M80 -115 L180 -115" {SW4}/>'
            f'<rect x="{80 - shutter * 0.6:.0f}" y="-160" width="{50 - shutter * 0.4:.0f}" height="90" fill="#6E9A5E" {SW4}/>'
            f'<rect x="{130 + shutter * 0.2:.0f}" y="-160" width="{50 - shutter * 0.4:.0f}" height="90" fill="#6E9A5E" {SW4}/>'
            f'<rect x="-190" y="-72" width="120" height="18" fill="#8A5A35" {SW4}/><rect x="70" y="-72" width="120" height="18" fill="#8A5A35" {SW4}/>'
            + flower_bed(-185, -75, -76, t, seed=31, density=1.8, scale=0.4) + flower_bed(75, 185, -76, t, seed=32, density=1.8, scale=0.4) + '</g>')


def picket_fence(x0, x1, y, col="#F6F0E2"):
    out = f'<path d="M{x0} {y - 70} L{x1} {y - 70} M{x0} {y - 30} L{x1} {y - 30}" stroke="{col}" stroke-width="14"/><path d="M{x0} {y - 70} L{x1} {y - 70} M{x0} {y - 30} L{x1} {y - 30}" fill="none" {stroke(3)} opacity="0.5"/>'
    for x in range(int(x0), int(x1), 50):
        out += f'<path d="M{x} {y} L{x} {y - 100} L{x + 15} {y - 120} L{x + 30} {y - 100} L{x + 30} {y} Z" fill="{col}" {stroke(4)}/>'
    return out


def bg_cottage_garden(t, tod="day", window_open=1.0, insects=True):
    skies = {"sunrise": ("#F6C8A0", "#FBE6C4", "#F7D488"), "day": ("#A9CFE0", "#E6F1EC", "#FFF3C4"), "sunset": ("#8E6A9A", "#F2A76B", "#F7C98B")}
    top, bot, sun = skies[tod]
    out = sky(top, bot, "cg" + tod)
    sy = {"sunrise": 520, "day": 160, "sunset": 560}[tod]
    out += sun_rays(1500, sy, t, op=0.12 if tod != "day" else 0.08) + f'<circle cx="1500" cy="{sy}" r="80" fill="{sun}" {SW5}/>'
    out += clouds(t, 160, seed=3, n=4)
    out += (f'<path d="M-600 640 Q100 520 700 600 Q1300 500 2600 620 L2600 1600 L-600 1600 Z" fill="#9CB98A" {SW5}/>'
            + "".join(tree(x, 640 + (i % 2) * 14, 0.55, "#6E9A5E", t, i) for i, x in enumerate(range(-100, 2200, 210))) +
            f'<path d="M-600 760 Q500 700 1100 760 Q1600 720 2600 770 L2600 1600 L-600 1600 Z" fill="#7FA65A" {SW5}/>')
    out += cottage(560, 820, 0.95, t, window_open=window_open)
    out += picket_fence(-200, 2200, 900)
    out += f'<path d="M560 820 Q620 940 500 1100 L700 1100 Q760 940 660 820 Z" fill="#D9C49A" {SW4}/>'
    out += "".join(f'<ellipse cx="{x}" cy="{y}" rx="34" ry="14" fill="#C9C6C0" {stroke(3)}/>' for x, y in [(600, 880), (590, 960), (630, 1040)])
    out += hive_box(1420, 960, 0.9, "#F6F0E2")
    out += f'<g transform="translate(1100 990)"><path d="M-20 0 L-10 -90 L10 -90 L20 0 Z" fill="#C9C6C0" {SW4}/><ellipse cx="0" cy="-96" rx="70" ry="18" fill="#BFD9D6" {SW4}/></g>'
    out += flower_bed(-150, 480, 1010, t, seed=11, density=1.3) + flower_bed(760, 1330, 1020, t, seed=12, density=1.3) + flower_bed(1550, 2100, 1000, t, seed=13, density=1.3)
    out += grass_tufts(-200, 2200, 1060, n=60, t=t)
    if insects:
        for k in range(3):
            out += butterfly(400 + k * 600 + 60 * math.sin(t + k), 700 + 40 * math.sin(t * 1.4 + k), 0.25, int(t * 12) + k, ["#E58A4A", "#9DB8D6", "#F2B33D"][k], "#F6F0E2")
    return out


def bg_kitchen(t):
    out = f'<rect x="-600" y="-400" width="3200" height="1900" fill="#F0E0C0"/>'
    out += "".join(f'<rect x="{x}" y="{y}" width="58" height="58" fill="#E9F1EE" stroke="#C9D6D0" stroke-width="3"/>' for x in range(-40, 1960, 60) for y in range(420, 620, 60))
    out += f'<rect x="-600" y="620" width="3200" height="60" fill="#B98B5E" {SW5}/><rect x="-600" y="680" width="3200" height="400" fill="#8FB2A8" {SW5}/>'
    out += "".join(f'<rect x="{x}" y="700" width="230" height="330" rx="8" fill="#9CC0B6" {SW4}/><circle cx="{x + 200}" cy="860" r="8" fill="{MUSTARD}" {stroke(2)}/>' for x in range(-120, 1900, 250))
    out += "".join(f'<rect x="{x}" y="60" width="230" height="280" rx="8" fill="#9CC0B6" {SW4}/><circle cx="{x + 200}" cy="200" r="8" fill="{MUSTARD}" {stroke(2)}/>' for x in (-120, 130, 1380, 1630))
    out += f'<rect x="420" y="80" width="560" height="300" fill="#BFD9D6" {SW5}/><path d="M700 80 L700 380 M420 230 L980 230" {SW5}/>'
    out += clouds(t, 160, seed=8, n=2).replace('<g transform', '<g clip-path="url(#kw)" transform') if False else ""
    out += f'<path d="M440 360 Q560 290 700 350 Q840 290 960 360 Z" fill="#9CC5A1" {SW4}/>'
    out += f'<rect x="380" y="380" width="640" height="22" fill="#F6F0E2" {SW4}/>'
    out += f'<g transform="translate(470 380)"><path d="M-30 0 L30 0 L22 -60 L-22 -60 Z" fill="#C9563F" {SW4}/>' + "".join(f'<path d="M0 -60 Q{a} -110 {a * 1.4:.0f} -140" fill="none" stroke="#4E7F3A" stroke-width="6"/>' for a in (-30, 0, 30)) + '</g>'
    out += f'<g transform="translate(900 380)"><rect x="-26" y="-70" width="52" height="70" rx="8" fill="#F6F0E2" {SW4}/></g>'
    out += f'<rect x="1180" y="420" width="70" height="200" fill="#C9C6C0" {SW4}/><path d="M1120 420 L1310 420 L1290 380 L1140 380 Z" fill="#6E6A66" {SW4}/>'
    return out


def bg_supermarket(t, fade=0.0, empty_ids=(), item_scale=1.0):
    vp = (960, 470)
    out = f'<rect x="-600" y="-400" width="3200" height="1900" fill="#EDE9E0"/>'
    out += f'<path d="M-200 -100 L2120 -100 L1200 380 L720 380 Z" fill="#F6F4EE" {SW5}/>'
    for k in range(5):
        y = 20 + k * 70
        out += f'<rect x="{960 - 300 + k * 50}" y="{y}" width="{600 - k * 100}" height="16" rx="8" fill="#FFFDF0" {stroke(3)}/>'
    out += f'<path d="M720 380 L1200 380 L1200 620 L720 620 Z" fill="#D9D3C4" {SW5}/>'
    out += f'<path d="M-200 1200 L720 620 L1200 620 L2120 1200 Z" fill="#E6E0D2" {SW5}/>'
    for k in range(-8, 9):
        out += f'<path d="M{960 + k * 30} 620 L{960 + k * 260} 1200" stroke="#D2CABA" stroke-width="3"/>'
    for y in (680, 780, 920, 1100):
        out += f'<path d="M-200 {y} L2120 {y}" stroke="#D2CABA" stroke-width="3"/>'
    out += f'<rect x="760" y="420" width="400" height="60" rx="8" fill="#6E9A5E" {SW4}/>' + text(960, 465, "FRESH PRODUCE", 34, "#FFF6E0")
    fruits = [apple, strawberry, blueberry, cherry, avocado, melon, lambda x, y, s: apple(x, y, s, "#F2B33D"), pumpkin, almond]
    r = rnd(17)
    for side in (-1, 1):
        for row in range(3):
            y_top = 420 + row * 130
            for b in range(4):
                u0, u1 = b / 4, (b + 0.9) / 4
                xa = 960 + side * (240 + u0 * 900); xb = 960 + side * (240 + u1 * 900)
                ya = y_top + (u0 * 1.0) * (row * 140 + 60); yb = y_top + (u1 * 1.0) * (row * 140 + 60)
                h = 90 + 90 * u1
                bid = (side, row, b)
                out += f'<path d="M{xa:.0f} {ya:.0f} L{xb:.0f} {yb:.0f} L{xb:.0f} {yb + h:.0f} L{xa:.0f} {ya + h * 0.7:.0f} Z" fill="#B98B5E" {stroke(4)}/>'
                f = fruits[(row * 4 + b + (side > 0) * 3) % len(fruits)]
                op = 1 - fade
                if bid in empty_ids or op <= 0:
                    continue
                n = 4 + b * 2
                sc = (0.35 + 0.45 * u1) * item_scale
                for k in range(n):
                    fx = lerp(xa, xb, (k + 0.5) / n) + r.uniform(-6, 6)
                    fy = lerp(ya, yb, (k + 0.5) / n) + r.uniform(4, 22) * sc
                    out += f'<g opacity="{op:.2f}">{f(fx, fy, sc)}</g>'
                out += f'<g opacity="{op:.2f}">' + price_tag((xa + xb) / 2, (ya + yb) / 2 + h * 0.75, "$" + str(1 + (row + b) % 5), 0.5 + 0.4 * u1) + '</g>'
    return out


def bg_meadow2(t, fade=0.0, seed=21, sky_top="#A9CFE0", sky_bot="#E6F1EC"):
    out = sky(sky_top, sky_bot, "md" + str(seed)) + clouds(t, 170, seed=seed, n=5)
    out += (f'<path d="M-600 560 Q200 430 800 520 Q1400 420 2600 540 L2600 1600 L-600 1600 Z" fill="#A9C29A" {SW5}/>'
            + "".join(tree(x, 560 + (i % 3) * 10, 0.5, "#7FA65A", t, i) for i, x in enumerate(range(-200, 2300, 180))) +
            f'<path d="M-600 680 Q600 600 1300 690 Q1800 650 2600 700 L2600 1600 L-600 1600 Z" fill="#8FB27A" {SW5}/>'
            f'<path d="M-600 860 Q800 780 2600 880 L2600 1600 L-600 1600 Z" fill="#7FA65A" {SW5}/>')
    out += flower_bed(-200, 2150, 730, t, seed=seed, density=1.6, scale=0.5, fade=fade)
    out += flower_bed(-200, 2150, 900, t, seed=seed + 1, density=1.4, scale=0.8, fade=fade)
    out += flower_bed(-200, 2150, 1070, t, seed=seed + 2, density=1.0, scale=1.15, fade=fade)
    out += grass_tufts(-200, 2200, 1070, seed=seed, n=70, t=t)
    return out


def bg_apiary(t, snow=False):
    top, bot = ("#C9D6E0", "#F4F6F4") if snow else ("#A9CFE0", "#F3E6C4")
    out = sky(top, bot, "ap" + str(int(snow))) + clouds(t, 170, seed=9, n=4, col="#FFFFFF")
    out += f'<path d="M-600 600 Q300 500 1000 580 Q1600 520 2600 600 L2600 1600 L-600 1600 Z" fill="{"#E9EEF0" if snow else "#9CB98A"}" {SW5}/>'
    out += (f'<g transform="translate(1600 640)"><rect x="-200" y="-260" width="400" height="260" fill="#B5543F" {SW5}/><path d="M-230 -250 L0 -400 L230 -250 Z" fill="#8A3A2E" {SW5}/>'
            f'<rect x="-60" y="-150" width="120" height="150" fill="#6B4A35" {SW5}/><path d="M-60 -150 L60 0 M60 -150 L-60 0" {stroke(4)}/></g>')
    out += f'<path d="M-600 720 Q500 680 1200 720 Q1800 700 2600 730 L2600 1600 L-600 1600 Z" fill="{"#F4F6F4" if snow else "#7FA65A"}" {SW5}/>'
    out += "".join(f'<ellipse cx="{x}" cy="660" rx="140" ry="70" fill="{"#C9D6D0" if snow else "#4E7F3A"}" {SW5}/>' for x in range(-200, 1300, 220))
    if not snow:
        out += flower_bed(-200, 2200, 1060, t, seed=41, density=0.8, scale=0.7)
    else:
        r = rnd(5)
        out += "".join(f'<circle cx="{(r.uniform(-200, 2100)) % 2200:.0f}" cy="{(r.uniform(0, 1100) + t * 60) % 1100:.0f}" r="{r.choice([3, 4, 6])}" fill="#FFFFFF"/>' for _ in range(90))
    return out


def bg_farmland(t):
    out = sky("#A9CFE0", "#F3E6C4", "farm2") + clouds(t, 140, seed=6, n=5)
    out += f'<path d="M-600 420 Q400 340 1200 400 Q1800 360 2600 420 L2600 1600 L-600 1600 Z" fill="#A9C29A" {SW5}/>'
    patches = [("#C9B35E", "#B59E4A"), ("#7FA65A", "#6E9A5E"), ("#E6D27A", "#C9B35E"), ("#9CB98A", "#7FA65A"), ("#B98B5E", "#A8743A")]
    r = rnd(8)
    for j in range(4):
        y0 = 440 + j * 150
        x = -600
        while x < 2600:
            w = r.uniform(300, 600)
            c, c2 = r.choice(patches)
            out += f'<path d="M{x:.0f} {y0} L{x + w:.0f} {y0 + 10} L{x + w + 20:.0f} {y0 + 160} L{x - 10:.0f} {y0 + 150} Z" fill="{c}" {stroke(4)}/>'
            for k in range(1, 6):
                out += f'<path d="M{x + k * w / 6:.0f} {y0 + 6} L{x + k * w / 6 + 6:.0f} {y0 + 150}" stroke="{c2}" stroke-width="5"/>'
            x += w
    out += "".join(fruit_tree(x, 600 + (i % 2) * 20, 0.35, t, i, "#E0533A", 6) for i, x in enumerate(range(1300, 2000, 110)))
    out += f'<path d="M-600 900 Q200 860 700 920 Q1200 980 2600 900" fill="none" stroke="#7FB4BE" stroke-width="40"/><path d="M-600 900 Q200 860 700 920 Q1200 980 2600 900" fill="none" {stroke(4)}/>'
    out += f'<g transform="translate(300 640) scale(0.5)"><rect x="-200" y="-260" width="400" height="260" fill="#B5543F" {SW5}/><path d="M-230 -250 L0 -400 L230 -250 Z" fill="#8A3A2E" {SW5}/></g>'
    return out


def bg_orchard_rows(t, bloom=True, bare=False, petals=True, sky_top="#9FC8E6"):
    out = sky(sky_top, "#EAF3F4", "orc") + clouds(t, 140, seed=4, n=4)
    out += f'<path d="M-600 440 Q300 380 1000 420 Q1600 380 2600 440 L2600 1600 L-600 1600 Z" fill="#B7C9A0" {SW5}/>'
    out += f'<path d="M-200 1200 L900 470 L1020 470 L2120 1200 Z" fill="#C9B07E" {SW4}/>'
    for side in (-1, 1):
        for k in range(9, -1, -1):
            u = k / 9
            x = 960 + side * lerp(140, 1200, (1 - u) ** 1.6)
            y = lerp(1200, 480, u ** 0.8)
            s = lerp(1.6, 0.25, u ** 0.8)
            out += blossom_tree(x, y, s, t, k + (side > 0) * 20, bare=bare, petals_fall=petals and s > 0.8, col="#FBEAF0" if bloom else "#7FA65A")
    return out


def bg_terraces(t):
    out = sky("#B7CFE0", "#EEF0E6", "ter") + clouds(t, 120, seed=12, n=4)
    out += f'<path d="M-600 500 L100 160 L500 400 L900 120 L1400 380 L1900 140 L2600 460 L2600 1600 L-600 1600 Z" fill="#9AAFA6" {SW5}/>'
    for k in range(7):
        y = 520 + k * 90
        out += f'<path d="M-600 {y} Q400 {y - 40} 1000 {y + 10} Q1600 {y - 30} 2600 {y} L2600 {y + 95} L-600 {y + 95} Z" fill="{["#9CB98A", "#8FB27A", "#7FA65A"][k % 3]}" {SW4}/>'
        for i, x in enumerate(range(-200 + (k % 2) * 90, 2200, 180)):
            out += blossom_tree(x, y + 30, 0.3 + k * 0.06, t, k * 30 + i, col="#FDF3F6")
    return out


def bg_greenhouse(t):
    out = f'<rect x="-600" y="-400" width="3200" height="1900" fill="#DCEEE8"/>'
    out += f'<path d="M-600 200 L960 -200 L2600 200" fill="none" stroke="#9AA8A4" stroke-width="16"/>'
    for x in range(-600, 2600, 200):
        out += f'<path d="M{x} -400 L{x} 1100" stroke="#B8C6C2" stroke-width="10"/>'
    for y in range(-300, 1100, 220):
        out += f'<path d="M-600 {y} L2600 {y}" stroke="#B8C6C2" stroke-width="6"/>'
    out += f'<rect x="-600" y="900" width="3200" height="700" fill="#8A6A4E" {SW5}/>'
    for k, x in enumerate(range(-100, 2100, 330)):
        out += f'<path d="M{x} 900 L{x} 300" stroke="#C9A77C" stroke-width="8"/>'
        for j in range(6):
            yy = 860 - j * 100
            out += f'<path d="M{x} {yy} q{(-1) ** j * 60} -20 {(-1) ** j * 90} 10" fill="none" stroke="#4E7F3A" stroke-width="7"/>'
            out += f'<path d="M{x + (-1) ** j * 60} {yy - 10} q20 -30 50 -10 q-20 26 -50 10 Z" fill="#6E9A5E" {stroke(3)}/>'
        for j in range(3):
            out += f'<circle cx="{x + (-1) ** j * 50}" cy="{760 - j * 170}" r="26" fill="#E0533A" {SW4}/>'
    return out


def bg_city(t, green=True):
    out = sky("#A9CFE0", "#F3E6C4", "city") + clouds(t, 140, seed=14, n=4)
    r = rnd(22)
    x = -300
    while x < 2300:
        w = r.uniform(180, 320); h = r.uniform(300, 700)
        col = r.choice(["#E8C9A0", "#C9D6C8", "#D8C2D6", "#F0D8B8", "#B8C6D2"])
        out += f'<rect x="{x:.0f}" y="{1000 - h:.0f}" width="{w:.0f}" height="{h:.0f}" fill="{col}" {SW5}/>'
        for wy in range(int(1000 - h + 40), 960, 70):
            for wx in range(int(x + 24), int(x + w - 40), 54):
                out += f'<rect x="{wx}" y="{wy}" width="30" height="40" fill="#BFD9D6" {stroke(3)}/>'
        if green:
            out += f'<path d="M{x:.0f} {1000 - h:.0f} q{w / 4:.0f} -40 {w / 2:.0f} -10 q{w / 4:.0f} -40 {w / 2:.0f} 0 Z" fill="#7FA65A" {SW4}/>'
            out += flower_bed(x + 10, x + w - 10, 1000 - h, t, seed=int(x) % 97, density=1.6, scale=0.35)
        x += w + r.uniform(10, 40)
    out += f'<rect x="-600" y="1000" width="3200" height="600" fill="#9C9A94" {SW5}/>'
    return out


def bg_lab3(t):
    out = f'<rect x="-600" y="-400" width="3200" height="1900" fill="#E6E0D2"/><rect x="-600" y="880" width="3200" height="700" fill="#C9B99A" {SW5}/>'
    out += f'<rect x="200" y="140" width="520" height="340" rx="10" fill="#FDFDFB" {SW5}/><path d="M240 420 L340 360 L420 390 L520 280 L620 300 L680 220" fill="none" stroke="#5B8DB8" stroke-width="8"/>'
    out += f'<rect x="1240" y="140" width="460" height="340" rx="10" fill="#FDFDFB" {SW5}/>' + "".join(f'<rect x="{1290 + k * 80}" y="{460 - h}" width="50" height="{h}" fill="{MUSTARD}" {stroke(3)}/>' for k, h in enumerate((120, 200, 160, 260, 300)))
    out += f'<rect x="100" y="640" width="1720" height="40" rx="6" fill="#B98B5E" {SW5}/>'
    return out


def bg_paper2(t, col="#F4EEDF"):
    out = f'<rect x="-600" y="-400" width="3200" height="1900" fill="{col}"/>'
    out += "".join(f'<path d="M-600 {y} L2600 {y}" stroke="#E6DCC6" stroke-width="2"/>' for y in range(-380, 1500, 60))
    out += "".join(f'<path d="M{x} -400 L{x} 1500" stroke="#EDE5D2" stroke-width="2"/>' for x in range(-580, 2600, 60))
    doodles = [(160, 140), (1760, 160), (180, 940), (1740, 940)]
    for k, (x, y) in enumerate(doodles):
        out += f'<g opacity="0.35">{daisy(x, y + 60, 0.5, 0, k, col="#F6F0E2")}</g>'
    return out


def bg_farmyard(t):
    out = sky("#A9CFE0", "#F3E6C4", "fy") + clouds(t, 150, seed=19, n=4)
    out += f'<path d="M-600 620 Q600 560 2600 640 L2600 1600 L-600 1600 Z" fill="#9CB98A" {SW5}/>'
    out += (f'<g transform="translate(1500 700)"><rect x="-260" y="-320" width="520" height="320" fill="#B5543F" {SW5}/><path d="M-290 -310 L0 -480 L290 -310 Z" fill="#8A3A2E" {SW5}/>'
            f'<rect x="-90" y="-200" width="180" height="200" fill="#F6F0E2" {SW5}/><path d="M-90 -200 L90 0 M90 -200 L-90 0" {stroke(5)}/>'
            f'<rect x="300" y="-420" width="120" height="420" rx="50" fill="#C9C6C0" {SW5}/></g>')
    out += f'<path d="M-600 760 L2600 760 L2600 1600 L-600 1600 Z" fill="#B7A27A" {SW5}/>'
    out += picket_fence(-200, 1000, 800, "#C9A77C")
    out += "".join(f'<g transform="translate({x} {y})"><rect x="-80" y="-60" width="160" height="90" rx="30" fill="#E6C27A" {SW5}/><path d="M-60 -30 L60 -30 M-60 0 L60 0" stroke="#C9A04A" stroke-width="4"/></g>' for x, y in [(160, 1000), (330, 1030)])
    return out


def bg_highway(t):
    out = sky("#A9CFE0", "#F3E6C4", "hw") + clouds(t, 150, seed=23, n=5, speed=30)
    out += f'<path d="M-600 520 Q200 380 900 480 Q1500 380 2600 500 L2600 1600 L-600 1600 Z" fill="#C9B35E" {SW5}/>'
    out += "".join(f'<ellipse cx="{x}" cy="{560 + (i % 2) * 20}" rx="70" ry="50" fill="#8FA86A" {stroke(4)}/>' for i, x in enumerate(range(-200, 2300, 160)))
    out += f'<rect x="-600" y="760" width="3200" height="240" fill="#6E6A66" {SW5}/>'
    out += "".join(f'<rect x="{(x - t * 400) % 2600 - 400:.0f}" y="870" width="120" height="14" fill="#F6F0E2"/>' for x in range(0, 2600, 260))
    out += f'<rect x="-600" y="1000" width="3200" height="600" fill="#B7A27A" {SW5}/>'
    return out
