"""Kinetic (animated) on-screen text, driven by the storyboard 'onscreen' field.

spec = "style|position|main|sub|extra..."
styles: count, pop, type, stamp, label, marker, list, title
positions: top, bottom, left, right, center, tl, tr, bl, br
"""
import math, re
from draw import INK, CREAM, MUSTARD, RED, ease, ease_out_back, seg, clamp

FONT = 'font-family="Inter Display, Inter, sans-serif"'
POS = {"top": (960, 175), "bottom": (960, 960), "center": (960, 520), "left": (420, 300), "right": (1500, 300),
       "tl": (90, 150), "tr": (1830, 150), "bl": (90, 900), "br": (1830, 900)}


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def t_(x, y, txt, size, fill, anchor="middle", stroke_w=None, weight=900, extra="", ls=1):
    sw = stroke_w if stroke_w is not None else size * 0.15
    return (f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" {FONT} font-weight="{weight}" font-size="{size}" letter-spacing="{ls}" '
            f'fill="{fill}" stroke="{INK}" stroke-width="{sw:.1f}" stroke-linejoin="round" paint-order="stroke" {extra}>{esc(txt)}</text>')


def anchor_for(pos):
    return "start" if pos in ("tl", "bl") else ("end" if pos in ("tr", "br") else "middle")


def fmt_num(v, template):
    dec = len(template.split(".")[1]) if "." in template else 0
    s = f"{v:,.{dec}f}" if "," in template else f"{v:.{dec}f}"
    return s


def count(spec, t, T, pos):
    main, sub = spec[2], spec[3] if len(spec) > 3 else ""
    x, y = POS[pos]
    a = anchor_for(pos)
    p_in = seg(t, 0.08 * T, 0.08 * T + 0.35)
    m = re.search(r"\d[\d,]*\.?\d*", main)
    if m:
        target = float(m.group(0).replace(",", ""))
        u = ease(seg(t, 0.08 * T, 0.08 * T + min(1.6, 0.5 * T)))
        shown = main[:m.start()] + fmt_num(target * u, m.group(0)) + main[m.end():]
    else:
        shown = main
    k = ease_out_back(p_in)
    size = 150 if len(shown) < 9 else 120
    out = f'<g transform="translate({x} {y}) scale({k:.3f})">' + t_(0, 0, shown, size, MUSTARD, a) + '</g>'
    if sub:
        ps = seg(t, 0.08 * T + 0.35, 0.08 * T + 0.75)
        dy = 20 * (1 - ease(ps))
        out += f'<g opacity="{ps:.2f}" transform="translate({x} {y + 70 + dy:.1f})">' + t_(0, 0, sub, 46, CREAM, a) + '</g>'
    return out


def pop(spec, t, T, pos):
    x, y = POS[pos]
    words = spec[2].split(" ")
    size = 120 if len(spec[2]) < 16 else 96
    # measure roughly: 0.62em per char
    widths = [sum(0.42 if ch in "I.,'!:1" else (0.95 if ch in 'MW' else 0.74) for ch in w) * size for w in words]
    total = sum(widths) + size * 0.32 * (len(words) - 1)
    cx = x - total / 2 if anchor_for(pos) == "middle" else (x if anchor_for(pos) == "start" else x - total)
    out = ""
    for i, (w, wd) in enumerate(zip(words, widths)):
        p = seg(t, 0.1 * T + i * 0.12, 0.1 * T + i * 0.12 + 0.3)
        if p <= 0:
            cx += wd + size * 0.32; continue
        k = ease_out_back(p)
        wob = 2.5 * math.sin(t * 3 + i)
        col = MUSTARD if i == len(words) - 1 and len(words) > 1 else CREAM
        out += f'<g transform="translate({cx + wd / 2:.1f} {y}) rotate({wob:.2f}) scale({k:.3f})">' + t_(0, 0, w, size, col) + '</g>'
        cx += wd + size * 0.32
    return out


def wrap(s, n):
    words, lines, cur = s.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > n:
            lines.append(cur); cur = w
        else:
            cur = (cur + " " + w).strip()
    lines.append(cur)
    return lines


def typewriter(spec, t, T, pos):
    x, y = POS[pos]
    lines = wrap(spec[2], 26)
    total = sum(len(l) for l in lines)
    n = int(total * seg(t, 0.05 * T, 0.8 * T))
    out, used = "", 0
    size = 78
    y0 = y - (len(lines) - 1) * size * 0.6
    for i, l in enumerate(lines):
        show = l[: max(0, n - used)]
        used += len(l)
        out += t_(x, y0 + i * size * 1.2, show, size, CREAM, "middle", weight=800)
        if 0 < len(show) < len(l) or (i == len(lines) - 1 and len(show) == len(l)):
            caret_on = int(t * 3) % 2 == 0
            if caret_on and len(show) <= len(l):
                cw = len(show) * size * 0.56
                out += f'<rect x="{x + cw / 2 + 6:.0f}" y="{y0 + i * size * 1.2 - size * 0.75:.0f}" width="10" height="{size * 0.85:.0f}" fill="{MUSTARD}"/>'
            if len(show) < len(l):
                break
    return out


def stamp(spec, t, T, pos):
    x, y = POS[pos]
    label = spec[2]
    size = 88 if len(label) < 12 else 66
    w = len(label) * size * 0.66 + 70
    if pos in ("tr", "br"):
        x = 1880 - w / 2
    if pos in ("tl", "bl"):
        x = 40 + w / 2
    p = seg(t, 0.3 * T, 0.3 * T + 0.25)
    if p <= 0:
        return ""
    k = 1 + 1.6 * (1 - ease(p))
    shake = 6 * math.sin(t * 60) * (1 - seg(t, 0.3 * T + 0.25, 0.3 * T + 0.5)) if p >= 1 else 0
    return (f'<g transform="translate({x + shake:.1f} {y}) rotate(-9) scale({k:.3f})" opacity="{min(1, p * 3):.2f}">'
            f'<rect x="{-w / 2:.0f}" y="{-size * 0.95:.0f}" width="{w:.0f}" height="{size * 1.35:.0f}" rx="14" fill="#FFF6E0" fill-opacity="0.85" stroke="{RED}" stroke-width="14"/>'
            f'<rect x="{-w / 2 + 12:.0f}" y="{-size * 0.95 + 12:.0f}" width="{w - 24:.0f}" height="{size * 1.35 - 24:.0f}" rx="8" fill="none" stroke="{RED}" stroke-width="4"/>'
            + f'<text x="0" y="{size * 0.15:.0f}" text-anchor="middle" {FONT} font-weight="900" font-size="{size}" fill="{RED}">{esc(label)}</text></g>')


def label(spec, t, T, pos):
    x, y = POS[pos]
    main, sub = spec[2], spec[3] if len(spec) > 3 else ""
    p = ease_out_back(seg(t, 0.06 * T, 0.06 * T + 0.45))
    w = max(len(main) * 34, len(sub) * 22) + 80
    h = 96 if sub else 76
    right = pos in ("tr", "br")
    bx = x - w if right else (x - w / 2 if anchor_for(pos) == "middle" else x)
    slide = (1 - p) * (260 if right else -260)
    out = (f'<g transform="translate({slide:.1f} 0)" opacity="{clamp(p * 1.5):.2f}">'
           f'<rect x="{bx + 6:.0f}" y="{y - 58 + 6:.0f}" width="{w:.0f}" height="{h}" rx="14" fill="{INK}" opacity="0.35"/>'
           f'<rect x="{bx:.0f}" y="{y - 58:.0f}" width="{w:.0f}" height="{h}" rx="14" fill="{CREAM}" stroke="{INK}" stroke-width="6"/>'
           f'<rect x="{bx:.0f}" y="{y - 58:.0f}" width="18" height="{h}" rx="6" fill="{MUSTARD}" stroke="{INK}" stroke-width="6"/>'
           + t_(bx + 42, y - 8 if sub else y, main, 46, INK, "start", stroke_w=0)
           + (t_(bx + 42, y + 26, sub, 28, "#6B5A48", "start", stroke_w=0, weight=700) if sub else "") + '</g>')
    return out


def marker(spec, t, T, pos):
    x, y = POS[pos]
    txt = spec[2]
    size = 66
    w = len(txt) * size * 0.6 + 50
    p = ease(seg(t, 0.12 * T, 0.12 * T + 0.5))
    pt = seg(t, 0.12 * T + 0.25, 0.12 * T + 0.6)
    return (f'<path d="M{x - w / 2:.0f} {y - 22} L{x - w / 2 + w * p:.0f} {y - 30}" stroke="{MUSTARD}" stroke-width="{size * 1.05:.0f}" stroke-linecap="round" opacity="0.95"/>'
            f'<g opacity="{pt:.2f}">' + t_(x, y, txt, size, INK, stroke_w=0) + '</g>')


def listing(spec, t, T, pos):
    items = [s for s in spec[2:] if s]
    x, y = POS[pos]
    out = ""
    for i, it in enumerate(items):
        p = ease_out_back(seg(t, 0.1 * T + i * 0.45, 0.1 * T + i * 0.45 + 0.35))
        if p <= 0:
            continue
        w = len(it) * 30 + 120
        yy = y + i * 96
        sx = (1 - p) * 300
        out += (f'<g transform="translate({sx:.1f} 0)" opacity="{clamp(p):.2f}">'
                f'<rect x="{x - w / 2:.0f}" y="{yy - 48:.0f}" width="{w:.0f}" height="80" rx="40" fill="{CREAM}" stroke="{INK}" stroke-width="6"/>'
                f'<circle cx="{x - w / 2 + 42:.0f}" cy="{yy - 8:.0f}" r="24" fill="{MUSTARD}" stroke="{INK}" stroke-width="5"/>'
                f'<path d="M{x - w / 2 + 30:.0f} {yy - 8:.0f} l9 10 l17 -18" fill="none" stroke="{INK}" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>'
                + t_(x - w / 2 + 80, yy + 6, it, 40, INK, "start", stroke_w=0) + '</g>')
    return out


def title(spec, t, T, pos):
    x, y = POS[pos]
    a = ease_out_back(seg(t, 0.25 * T, 0.25 * T + 0.4))
    b = ease_out_back(seg(t, 0.25 * T + 0.3, 0.25 * T + 0.75))
    out = ""
    if a > 0:
        out += f'<g transform="translate({x} {y}) scale({a:.3f})">' + t_(0, 0, spec[2], 110, CREAM) + '</g>'
    if b > 0 and len(spec) > 3:
        out += f'<g transform="translate({x} {y + 130}) scale({b:.3f}) rotate({1.5 * math.sin(t * 2):.2f})">' + t_(0, 0, spec[3], 130, MUSTARD) + '</g>'
    return out


STYLES = {"count": count, "pop": pop, "type": typewriter, "stamp": stamp, "label": label, "marker": marker, "list": listing, "title": title}


def render(spec_str, t, T):
    if not spec_str:
        return ""
    spec = spec_str.split("|")
    fn = STYLES.get(spec[0])
    if not fn:
        return ""
    body = fn(spec, t, T, spec[1] if len(spec) > 1 and spec[1] in POS else "top")
    fade = 1 - seg(t, T - 0.22, T)
    return f'<g opacity="{fade:.3f}">{body}</g>' if body else ""
