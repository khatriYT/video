"""House-style SVG drawing library ("The Disappearance Files").

All characters and props follow 00_SYSTEM/COMPETITOR_VISUAL_STYLE_GUIDE.md, Part B.
Coordinates are for a 1920x1080 canvas.
"""
import math, random

INK = "#2B2420"
SW = 7
SKIN_PIP = "#F6F0E2"
MUSTARD, MUSTARD_D = "#F2B33D", "#C98A1E"
OLIVE = "#6E8B3D"
BOOT = "#5A3A28"
SATCHEL = "#8A5A35"
RED = "#E0533A"
CREAM = "#FFF6E0"


# ---------- easing / helpers ----------
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def ease_out_back(x, k=1.70158):
    x = clamp(x) - 1
    return 1 + (k + 1) * x ** 3 + k * x ** 2


def ease_out_bounce(x):
    x = clamp(x)
    n, d = 7.5625, 2.75
    if x < 1 / d:
        return n * x * x
    if x < 2 / d:
        x -= 1.5 / d; return n * x * x + .75
    if x < 2.5 / d:
        x -= 2.25 / d; return n * x * x + .9375
    x -= 2.625 / d; return n * x * x + .984375


def seg(t, a, b):
    """progress 0..1 of t within [a,b]"""
    return clamp((t - a) / (b - a)) if b > a else float(t >= a)


def lerp(a, b, x):
    return a + (b - a) * x


def blinking(t, times, dur=0.13):
    return any(bt <= t < bt + dur for bt in times)


def g(content, tr="", extra=""):
    return f'<g transform="{tr}" {extra}>{content}</g>' if tr or extra else content


# ---------- shared defs ----------
def defs(seed):
    return f"""<defs>
<filter id="boil" x="-5%" y="-5%" width="110%" height="110%">
 <feTurbulence type="fractalNoise" baseFrequency="0.018" numOctaves="2" seed="{seed}" result="n"/>
 <feDisplacementMap in="SourceGraphic" in2="n" scale="4.5" xChannelSelector="R" yChannelSelector="G"/>
</filter>
<filter id="grain" x="0" y="0" width="100%" height="100%">
 <feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="2" seed="{seed % 3}"/>
 <feColorMatrix values="0 0 0 0 0.17  0 0 0 0 0.14  0 0 0 0 0.12  0 0 0 0.55 0"/>
</filter>
<radialGradient id="vig" cx="50%" cy="50%" r="75%">
 <stop offset="60%" stop-color="#000" stop-opacity="0"/><stop offset="100%" stop-color="#000" stop-opacity="0.32"/>
</radialGradient>
<radialGradient id="glow" cx="50%" cy="50%" r="50%">
 <stop offset="0%" stop-color="#FFF3C4" stop-opacity="0.9"/><stop offset="100%" stop-color="#FFF3C4" stop-opacity="0"/>
</radialGradient>
<clipPath id="abdclip"><ellipse cx="-45" cy="6" rx="42" ry="13" transform="rotate(-10 -45 6)"/></clipPath>
<pattern id="mesh" width="14" height="14" patternUnits="userSpaceOnUse">
 <path d="M0 0 L14 14 M14 0 L0 14" stroke="#FFFFFF" stroke-width="1.4" opacity="0.8"/>
</pattern>
</defs>"""


GRAIN = {}  # seed -> data URI of a pre-rendered transparent grain texture (set by render.py; much faster than live filter)


def grain_svg(seed):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="1920" height="1080">{defs(seed)}'
            f'<rect width="1920" height="1080" filter="url(#grain)" opacity="0.5"/></svg>')


def frame_svg(content, cam=(1.0, 960, 540), seed=1, vignette=0.9, grain=0.07, overlay=""):
    s, cx, cy = cam
    tr = f"translate(960 540) scale({s:.5f}) translate({-cx:.2f} {-cy:.2f})"
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="1920" height="1080" viewBox="0 0 1920 1080">'
            f'{defs(seed)}<g filter="url(#boil)"><g transform="{tr}">{content}</g></g>'
            f'<rect width="1920" height="1080" fill="url(#vig)" opacity="{vignette}"/>'
            + ('' if (GRAIN or grain <= 0) else
               f'<rect width="1920" height="1080" filter="url(#grain)" opacity="{grain / 0.07 * 0.5:.3f}"/>') +
            f'{overlay}</svg>')


# ---------- characters ----------
def face(mouth="smile", eyes="open", look=(0, 0), glasses=True, ink=INK):
    lx, ly = look
    out = ""
    if eyes == "open":
        out += f'<circle cx="{-20 + lx}" cy="{4 + ly}" r="6.5" fill="{ink}"/><circle cx="{20 + lx}" cy="{4 + ly}" r="6.5" fill="{ink}"/>'
    elif eyes == "blink":
        out += f'<path d="M-28 5 L-12 5 M12 5 L28 5" stroke="{ink}" stroke-width="5" stroke-linecap="round"/>'
    elif eyes == "closed":
        out += f'<path d="M-29 2 Q-20 11 -11 2 M11 2 Q20 11 29 2" stroke="{ink}" stroke-width="5" fill="none" stroke-linecap="round"/>'
    elif eyes == "happy":
        out += f'<path d="M-29 8 Q-20 -2 -11 8 M11 8 Q20 -2 29 8" stroke="{ink}" stroke-width="5" fill="none" stroke-linecap="round"/>'
    elif eyes == "annoyed":
        out += (f'<circle cx="-20" cy="7" r="6" fill="{ink}"/><circle cx="20" cy="7" r="6" fill="{ink}"/>'
                f'<path d="M-30 1 L-10 3 M10 3 L30 1" stroke="{ink}" stroke-width="5" stroke-linecap="round"/>')
    if glasses:
        out += (f'<circle cx="-20" cy="4" r="18" fill="#DDEFF5" fill-opacity="0.18" stroke="{ink}" stroke-width="4.5"/>'
                f'<circle cx="20" cy="4" r="18" fill="#DDEFF5" fill-opacity="0.18" stroke="{ink}" stroke-width="4.5"/>'
                f'<path d="M-2 3 L2 3 M-38 1 L-57 -4 M38 1 L57 -4" stroke="{ink}" stroke-width="4" stroke-linecap="round"/>')
    m = {
        "smile": '<path d="M-14 31 Q0 43 14 31" stroke="{i}" stroke-width="5" fill="none" stroke-linecap="round"/>',
        "grin": '<path d="M-18 29 Q0 50 18 29 Z" fill="{i}" stroke="{i}" stroke-width="4" stroke-linejoin="round"/>',
        "o": '<ellipse cx="0" cy="36" rx="7" ry="9" fill="{i}"/>',
        "flat": '<path d="M-12 35 L12 35" stroke="{i}" stroke-width="5" stroke-linecap="round"/>',
        "frown": '<path d="M-13 39 Q0 28 13 39" stroke="{i}" stroke-width="5" fill="none" stroke-linecap="round"/>',
        "sleep": '<ellipse cx="0" cy="36" rx="5" ry="4" fill="{i}"/>',
        "none": "",
    }[mouth].format(i=ink)
    return out + m


def bucket_hat():
    return (f'<path d="M-48 -26 L-40 -80 Q0 -100 40 -80 L48 -26 Z" fill="{MUSTARD}" stroke="{INK}" stroke-width="{SW}" stroke-linejoin="round"/>'
            f'<path d="M-46 -40 L46 -40 L48 -26 L-48 -26 Z" fill="{MUSTARD_D}" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/>'
            f'<path d="M-86 -16 Q0 -44 86 -16 Q92 -8 82 -4 Q0 -28 -82 -4 Q-92 -8 -86 -16 Z" fill="{MUSTARD}" stroke="{INK}" stroke-width="{SW}" stroke-linejoin="round"/>')


def hair(style, color):
    if style == "tuft":
        return "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{color}" stroke="{INK}" stroke-width="5"/>'
                       for x, y, r in [(-58, -14, 16), (-50, -34, 14), (58, -14, 16), (50, -34, 14)])
    if style == "bun":
        return (f'<circle cx="0" cy="-78" r="24" fill="{color}" stroke="{INK}" stroke-width="{SW}"/>'
                f'<path d="M-62 -6 Q-60 -66 0 -64 Q60 -66 62 -6 Q40 -38 0 -40 Q-40 -38 -62 -6 Z" fill="{color}" stroke="{INK}" stroke-width="{SW}" stroke-linejoin="round"/>')
    if style == "scarf":
        return (f'<path d="M-70 30 Q-78 -70 0 -72 Q78 -70 70 30 Q64 -30 0 -34 Q-64 -30 -70 30 Z" fill="{color}" stroke="{INK}" stroke-width="{SW}" stroke-linejoin="round"/>'
                f'<path d="M50 -50 Q90 -60 84 -20" fill="none" stroke="{INK}" stroke-width="5"/>')
    if style == "curly":
        return "".join(f'<circle cx="{x}" cy="{y}" r="15" fill="{color}" stroke="{INK}" stroke-width="5"/>'
                       for x, y in [(-44, -40), (-22, -56), (0, -62), (22, -56), (44, -40), (-56, -16), (56, -16)])
    return ""


def arm_path(sx, sy, ang, side, length=118, bend=14):
    a = math.radians(ang)
    ex = sx + side * length * math.sin(a)
    ey = sy + length * math.cos(a)
    mx, my = (sx + ex) / 2, (sy + ey) / 2
    # perpendicular bend (elbow outward)
    px, py = -(ey - sy), (ex - sx)
    n = math.hypot(px, py) or 1
    cx, cy = mx + side * px / n * bend, my + side * py / n * bend
    return f'M{sx} {sy} Q{cx:.1f} {cy:.1f} {ex:.1f} {ey:.1f}', (ex, ey)


def person(x, y, s=1.0, *, skin=SKIN_PIP, outfit="vest", outfit_color=OLIVE, arms=(15, 15), mouth="smile",
           eyes="open", look=(0, 0), glasses=False, hat=None, hat_dy=0.0, hat_squash=1.0, hair_style=None,
           hair_color="#222", tilt=0, satchel=False, legs=True, thumbs=(False, False), bob=0.0, hand_tool=None,
           flip=False):
    """Stick figure standing with feet at (x, y). arms = (left, right) angle in degrees away from body (0 = down)."""
    parts = []
    # legs
    if legs:
        parts.append(f'<path d="M-12 -140 L-36 -12 M12 -140 L36 -12" stroke="{INK}" stroke-width="{SW}" stroke-linecap="round"/>')
        parts.append(f'<rect x="-58" y="-20" width="38" height="18" rx="8" fill="{BOOT}" stroke="{INK}" stroke-width="5"/>'
                     f'<rect x="20" y="-20" width="38" height="18" rx="8" fill="{BOOT}" stroke="{INK}" stroke-width="5"/>')
    # torso line
    parts.append(f'<path d="M0 -282 L0 -140" stroke="{INK}" stroke-width="{SW}" stroke-linecap="round"/>')
    # outfit
    if outfit == "vest":
        parts.append(f'<path d="M-38 -264 L38 -264 L48 -152 Q48 -138 34 -138 L-34 -138 Q-48 -138 -48 -152 Z" fill="{outfit_color}" stroke="{INK}" stroke-width="{SW}" stroke-linejoin="round"/>'
                     f'<path d="M-14 -264 L0 -238 L14 -264" stroke="{INK}" stroke-width="5" fill="none"/>'
                     f'<rect x="10" y="-228" width="22" height="20" rx="3" fill="none" stroke="{INK}" stroke-width="4"/>')
    elif outfit == "coat":
        parts.append(f'<path d="M-40 -266 L40 -266 L58 -70 L-58 -70 Z" fill="{outfit_color}" stroke="{INK}" stroke-width="{SW}" stroke-linejoin="round"/>'
                     f'<path d="M-16 -266 L0 -226 L16 -266 M0 -226 L0 -74" stroke="{INK}" stroke-width="4.5" fill="none"/>'
                     f'<rect x="-44" y="-170" width="24" height="20" rx="3" fill="none" stroke="{INK}" stroke-width="4"/>')
    elif outfit == "dress":
        parts.append(f'<path d="M-34 -266 L34 -266 L64 -80 L-64 -80 Z" fill="{outfit_color}" stroke="{INK}" stroke-width="{SW}" stroke-linejoin="round"/>')
    elif outfit == "shirt":
        parts.append(f'<path d="M-34 -266 L34 -266 L40 -150 L-40 -150 Z" fill="{outfit_color}" stroke="{INK}" stroke-width="{SW}" stroke-linejoin="round"/>')
    if satchel:
        parts.append(f'<path d="M-30 -258 L44 -156" stroke="{SATCHEL}" stroke-width="9"/>'
                     f'<rect x="26" y="-170" width="56" height="44" rx="8" fill="{SATCHEL}" stroke="{INK}" stroke-width="5"/>'
                     f'<path d="M26 -152 L82 -152" stroke="{INK}" stroke-width="4"/>')
    # arms + hands
    for side, ang, th in ((-1, arms[0], thumbs[0]), (1, arms[1], thumbs[1])):
        d, (hx, hy) = arm_path(side * 30, -250, ang, side)
        parts.append(f'<path d="{d}" stroke="{INK}" stroke-width="{SW}" fill="none" stroke-linecap="round"/>')
        if th:
            parts.append(f'<rect x="{hx - 6:.1f}" y="{hy - 38:.1f}" width="13" height="28" rx="6" fill="{skin}" stroke="{INK}" stroke-width="4.5"/>')
        parts.append(f'<circle cx="{hx:.1f}" cy="{hy:.1f}" r="16" fill="{skin}" stroke="{INK}" stroke-width="5"/>')
        if hand_tool and hand_tool[0] == side:
            parts.append(hand_tool[1](hx, hy))
    # head
    head = (hair(hair_style, hair_color) if hair_style in ("bun",) else "")
    head_inner = f'<circle cx="0" cy="0" r="62" fill="{skin}" stroke="{INK}" stroke-width="{SW}"/>'
    if hair_style in ("tuft", "curly", "scarf"):
        head_inner += hair(hair_style, hair_color)
    head_inner = head + head_inner + face(mouth, eyes, look, glasses, INK if skin != "#3B2A22" else "#F6F0E2")
    if hat == "bucket":
        head_inner += f'<g transform="translate(0 {hat_dy:.1f}) scale({1 / hat_squash:.3f} {hat_squash:.3f})">{bucket_hat()}</g>'
    parts.append(f'<g transform="translate(0 -340) rotate({tilt:.2f} 0 60)">{head_inner}</g>')
    fl = " scale(-1 1)" if flip else ""
    return f'<g transform="translate({x:.1f} {y + bob:.1f}) scale({s:.3f}){fl}">{"".join(parts)}</g>'


def pip(x, y, s=1.0, **kw):
    kw.setdefault("hat", "bucket")
    kw.setdefault("glasses", True)
    kw.setdefault("satchel", True)
    return person(x, y, s, **kw)


def head_only(x, y, r=62, rot=0, skin=SKIN_PIP, **facekw):
    s = r / 62
    return (f'<g transform="translate({x} {y}) rotate({rot}) scale({s:.3f})">'
            f'<circle cx="0" cy="0" r="62" fill="{skin}" stroke="{INK}" stroke-width="{SW}"/>{face(**facekw)}</g>')


# ---------- mosquito ----------
def mosquito(x, y, s=1.0, rot=0, frame=0, dead=False, flap=True, look=(0, 0), alpha=1.0, flip=False):
    w = (frame % 2) * 18 if flap else 0
    legs = ""
    for i, bx in enumerate((-2, 8, 16)):
        for side in (-1,):
            k = 1 + i * 0.25
            legs += (f'<path d="M{bx} 10 L{bx - 22 + i * 18} {34 * k:.0f} L{bx - 34 + i * 30} {66 * k:.0f}" stroke="{INK}" '
                     f'stroke-width="3.2" fill="none" stroke-linejoin="round" stroke-linecap="round"/>')
    if dead:
        eyes = (f'<path d="M20 -22 l10 10 M30 -22 l-10 10 M34 -18 l9 9 M43 -18 l-9 9" stroke="{INK}" stroke-width="3.2" stroke-linecap="round"/>')
    else:
        lx, ly = look
        eyes = (f'<circle cx="25" cy="-16" r="9" fill="#FFF" stroke="{INK}" stroke-width="3"/>'
                f'<circle cx="39" cy="-13" r="9" fill="#FFF" stroke="{INK}" stroke-width="3"/>'
                f'<circle cx="{27 + lx}" cy="{-15 + ly}" r="4" fill="{INK}"/><circle cx="{41 + lx}" cy="{-12 + ly}" r="4" fill="{INK}"/>')
    body = (
        f'<ellipse cx="-2" cy="-18" rx="34" ry="11" transform="rotate({-38 + w} 4 -12)" fill="#CFE7F2" fill-opacity="0.6" stroke="{INK}" stroke-width="2.5"/>'
        f'{legs}'
        f'<ellipse cx="-45" cy="6" rx="42" ry="13" transform="rotate(-10 -45 6)" fill="#8B7E74" stroke="{INK}" stroke-width="3.5"/>'
        f'<g clip-path="url(#abdclip)">' + "".join(f'<rect x="{-80 + i * 16}" y="-20" width="7" height="50" fill="#F3EFE6"/>' for i in range(5)) + '</g>'
        f'<ellipse cx="-45" cy="6" rx="42" ry="13" transform="rotate(-10 -45 6)" fill="none" stroke="{INK}" stroke-width="3.5"/>'
        f'<ellipse cx="4" cy="-2" rx="20" ry="15" fill="#6E625A" stroke="{INK}" stroke-width="3.5"/>'
        f'<path d="M44 -4 L92 14" stroke="{INK}" stroke-width="3.2" stroke-linecap="round"/>'
        f'<path d="M34 -22 Q44 -40 56 -38 M30 -24 Q34 -44 46 -48" stroke="{INK}" stroke-width="2.5" fill="none"/>'
        f'<circle cx="32" cy="-8" r="14" fill="#6E625A" stroke="{INK}" stroke-width="3.5"/>'
        f'{eyes}'
        f'<ellipse cx="-12" cy="-22" rx="36" ry="12" transform="rotate({-24 - w} -2 -10)" fill="#CFE7F2" fill-opacity="0.65" stroke="{INK}" stroke-width="2.5"/>'
    )
    fl = " scale(-1 1)" if flip else ""
    return f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({s:.3f}){fl}" opacity="{alpha:.3f}">{body}</g>'


def tiny_mosquito(x, y, s=1.0, frame=0, alpha=1.0, rot=0):
    w = (frame % 2) * 20
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({s:.3f})" opacity="{alpha:.3f}">'
            f'<ellipse cx="-2" cy="-12" rx="16" ry="6" transform="rotate({-35 + w})" fill="#CFE7F2" fill-opacity="0.7" stroke="{INK}" stroke-width="2"/>'
            f'<path d="M-26 4 L18 -4" stroke="{INK}" stroke-width="7" stroke-linecap="round"/>'
            f'<path d="M18 -4 L38 4 M-4 0 L-12 18 M4 -1 L6 18" stroke="{INK}" stroke-width="2.5" stroke-linecap="round"/>'
            f'<circle cx="20" cy="-6" r="5" fill="#FFF" stroke="{INK}" stroke-width="2"/></g>')


def puff(x, y, p, r=40, color="#E9E4D8"):
    """smoke puff at progress p (0..1)"""
    if p <= 0 or p >= 1:
        return ""
    out = ""
    for i, (dx, dy) in enumerate([(0, 0), (-r * .7, -r * .3), (r * .7, -r * .2), (-r * .3, r * .5), (r * .4, r * .5)]):
        rr = r * (0.4 + 0.8 * p) * (0.7 + 0.1 * i)
        out += f'<circle cx="{x + dx * (0.5 + p):.1f}" cy="{y + dy * (0.5 + p):.1f}" r="{rr:.1f}" fill="{color}" stroke="{INK}" stroke-width="4"/>'
    return f'<g opacity="{1 - p ** 2:.3f}">{out}</g>'


def buzz_lines(x, y, frame, s=1.0):
    j = (frame % 3) * 3
    return (f'<g transform="translate({x} {y}) scale({s})" stroke="{INK}" stroke-width="4" fill="none" stroke-linecap="round">'
            f'<path d="M{-20 - j} -30 Q{-30 - j} -10 {-20 - j} 10"/><path d="M{-38 - j} -40 Q{-52 - j} -10 {-38 - j} 20"/>'
            f'<path d="M{20 + j} -30 Q{30 + j} -10 {20 + j} 10"/><path d="M{38 + j} -40 Q{52 + j} -10 {38 + j} 20"/></g>')


def sparkle(x, y, p, size=40, color=MUSTARD):
    if p <= 0:
        return ""
    k = ease_out_back(min(p * 2, 1)) * (1 - max(0, p - 0.6) / 0.4 * 0.6)
    s = size * k
    return (f'<path d="M{x} {y - s} Q{x} {y} {x + s} {y} Q{x} {y} {x} {y + s} Q{x} {y} {x - s} {y} Q{x} {y} {x} {y - s} Z" '
            f'fill="{color}" stroke="{INK}" stroke-width="4"/>')


def title_text(lines, x, y, size=110, anchor="middle", p=1.0, lh=1.05):
    """lines = [(text, color), ...] pop-in with progress p"""
    if p <= 0:
        return ""
    k = ease_out_back(p)
    out = ""
    for i, (txt, col) in enumerate(lines):
        out += (f'<text x="0" y="{i * size * lh:.0f}" text-anchor="{anchor}" font-family="Inter Display, Inter, sans-serif" '
                f'font-weight="900" font-size="{size}" fill="{col}" stroke="{INK}" stroke-width="{size * 0.13:.1f}" '
                f'stroke-linejoin="round" paint-order="stroke">{txt}</text>')
    return f'<g transform="translate({x} {y}) scale({k:.3f})">{out}</g>'


def rnd(seed):
    return random.Random(seed)
