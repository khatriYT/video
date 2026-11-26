"""Episode 3 flat evidence cards + on-screen text overlays (PIL).

Design system (house style v2 draft §5): forest-slate background #14211C, cream text, mustard/red/green
accents, evidence-tag pills. Every card is a list of pre-rendered layers with entry animations;
card(kind, params, dur) returns frame(t) -> RGB PIL image at 1920x1080.
"""
import math
import os
import random

import shapefile
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1920, 1080
SS = 2
FD = "/usr/share/fonts/opentype/inter/"
FONTS = {"black": FD + "InterDisplay-Black.otf", "xbold": FD + "InterDisplay-ExtraBold.otf",
         "bold": FD + "InterDisplay-Bold.otf", "semi": FD + "Inter-SemiBold.otf", "med": FD + "Inter-Medium.otf",
         "reg": FD + "Inter-Regular.otf"}
C = dict(bg="#14211C", bg2="#1C2E26", panel="#22382E", cream="#FFF6E0", mustard="#F2B33D", red="#E0533A",
         green="#8FB27A", leaf="#5C9E5B", grey="#8C978F", dim="#3A5045", dark="#2B2420", blue="#6FA7C9")
TAGS = {"STRONG": ("STRONG EVIDENCE", "#4E8F55"), "DEBATED": ("DEBATED", "#C98A1E"),
        "ESTIMATE": ("ESTIMATE", "#C2502F"), "HYPOTHESIS": ("HYPOTHESIS", "#6E7A82"),
        "INFERENCE": ("WHAT EXPERIMENTS SUGGEST", "#4F7896")}
SHAPES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "02_SHARED_ASSETS", "maps",
                      "naturalearth_lowres", "naturalearth_lowres.shp")
_fc = {}


def F(kind, size):
    k = (kind, size)
    if k not in _fc:
        _fc[k] = ImageFont.truetype(FONTS[kind], size)
    return _fc[k]


def rgba(h, a=255):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (a,)


def ease(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def back_out(x):
    x = max(0.0, min(1.0, x))
    c = 1.4
    return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2


# ------------------------------------------------------------------ layers
class Layer:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.im = Image.new("RGBA", (w * SS, h * SS), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.im)

    def text(self, xy, s, size, kind="bold", fill="cream", anchor="mm", stroke=0, stroke_fill="bg"):
        self.d.text((xy[0] * SS, xy[1] * SS), s, font=F(kind, size * SS), fill=rgba(C.get(fill, fill)),
                    anchor=anchor, stroke_width=stroke * SS, stroke_fill=rgba(C.get(stroke_fill, stroke_fill)))

    def rrect(self, box, r, fill, outline=None, width=0):
        self.d.rounded_rectangle([v * SS for v in box], r * SS, fill=rgba(C.get(fill, fill)) if fill else None,
                                 outline=rgba(C.get(outline, outline)) if outline else None, width=width * SS)

    def ell(self, box, fill, outline=None, width=0):
        self.d.ellipse([v * SS for v in box], fill=rgba(C.get(fill, fill)) if fill else None,
                       outline=rgba(C.get(outline, outline)) if outline else None, width=width * SS)

    def poly(self, pts, fill, outline=None, width=0):
        self.d.polygon([(x * SS, y * SS) for x, y in pts], fill=rgba(C.get(fill, fill)) if fill else None,
                       outline=rgba(C.get(outline, outline)) if outline else None, width=width * SS)

    def line(self, pts, fill, width, joint="curve"):
        self.d.line([(x * SS, y * SS) for x, y in pts], fill=rgba(C.get(fill, fill)), width=int(width * SS),
                    joint=joint)

    def done(self):
        return self.im.resize((self.w, self.h), Image.LANCZOS)


class Card:
    def __init__(self, bg=True):
        self.items = []   # (img, (x, y), t0, dur, mode, extra)
        self.dyn = []     # callables (frame_img, t)
        self.base = make_bg() if bg else None

    def add(self, layer, xy, t0=0.0, dur=0.5, mode="up", extra=None):
        img = layer.done() if isinstance(layer, Layer) else layer
        self.items.append((img, xy, t0, dur, mode, extra or {}))

    def frame(self, t):
        im = self.base.copy()
        for img, (x, y), t0, dur, mode, ex in self.items:
            if t < t0:
                continue
            k = ease((t - t0) / dur) if dur > 0 else 1.0
            if "out" in ex and t > ex["out"]:
                k *= 1 - ease((t - ex["out"]) / 0.4)
                if k <= 0:
                    continue
            src = img
            dx, dy = 0, 0
            if mode == "up":
                dy = int((1 - k) * 36)
            elif mode == "left":
                dx = int((1 - k) * -60)
            elif mode == "pop":
                s = 0.6 + 0.4 * back_out((t - t0) / dur)
                if abs(s - 1) > 0.01:
                    src = img.resize((max(1, int(img.width * s)), max(1, int(img.height * s))), Image.BILINEAR)
                    dx, dy = (img.width - src.width) // 2, (img.height - src.height) // 2
            elif mode == "wipe":
                cw = max(1, int(img.width * k))
                src = img.crop((0, 0, cw, img.height))
                k = 1.0
            elif mode == "move":   # ex: path(t) -> (x, y)
                x, y = ex["path"](t)
            if k < 1 and mode != "wipe":
                a = src.getchannel("A").point(lambda v, k=k: int(v * k))
                src = src.copy()
                src.putalpha(a)
            im.alpha_composite(src, (int(x + dx), int(y + dy)))
        for f in self.dyn:
            f(im, t)
        return im.convert("RGB")


_BG = None


def make_bg():
    global _BG
    if _BG is None:
        im = Image.new("RGBA", (W, H), rgba(C["bg"]))
        g = Image.new("L", (W, H), 0)
        dg = ImageDraw.Draw(g)
        for r in range(12, 0, -1):
            v = int(46 * (1 - r / 12))
            dg.ellipse([W / 2 - r * 110, H / 2 - r * 70, W / 2 + r * 110, H / 2 + r * 70], fill=v)
        g = g.filter(ImageFilter.GaussianBlur(60))
        lift = Image.new("RGBA", (W, H), rgba(C["bg2"]))
        im = Image.composite(lift, im, g)
        rnd = random.Random(3)
        nz = Image.effect_noise((W // 2, H // 2), 18).resize((W, H)).point(lambda v: int(v * 0.06))
        im = Image.composite(Image.new("RGBA", (W, H), (255, 255, 255, 255)), im, nz)
        _BG = im
    return _BG.copy()


def tag_layer(tag):
    label, col = TAGS[tag]
    w = int(F("bold", 26).getlength(label)) + 70
    L = Layer(w, 56)
    L.rrect((0, 0, w, 56), 28, col)
    L.ell((20, 20, 36, 36), "cream")
    L.text((44, 29), label, 26, "bold", "cream", anchor="lm")
    return L, w


def add_tag(card, tag, t0=0.6):
    if tag:
        L, w = tag_layer(tag)
        card.add(L, (W - w - 70, H - 120), t0, 0.5, "left")


def title_layer(s, size=56, color="cream", w=1600):
    L = Layer(w, size + 30)
    L.text((w / 2, (size + 30) / 2), s, size, "xbold", color)
    return L


# ------------------------------------------------------------------ icons (drawn on a Layer, local coords)
def ic_vulture(L, cx, cy, s, col="cream"):
    pts = [(-1.0, 0.05), (-0.7, -0.12), (-0.35, -0.12), (-0.12, -0.05), (-0.08, -0.2), (0.0, -0.28), (0.08, -0.2),
           (0.12, -0.05), (0.35, -0.12), (0.7, -0.12), (1.0, 0.05), (0.92, 0.1), (0.95, 0.16), (0.84, 0.14),
           (0.85, 0.2), (0.72, 0.16), (0.5, 0.14), (0.18, 0.12), (0.12, 0.3), (-0.12, 0.3), (-0.18, 0.12),
           (-0.5, 0.14), (-0.72, 0.16), (-0.85, 0.2), (-0.84, 0.14), (-0.95, 0.16), (-0.92, 0.1)]
    L.poly([(cx + x * s, cy + y * s) for x, y in pts], col)


def ic_cow(L, cx, cy, s, col="cream", lying=False):
    if lying:
        L.ell((cx - 0.9 * s, cy - 0.3 * s, cx + 0.7 * s, cy + 0.3 * s), col)
        L.ell((cx + 0.55 * s, cy - 0.25 * s, cx + 1.0 * s, cy + 0.12 * s), col)
        for x in (-0.5, 0.2):
            L.line([(cx + x * s, cy + 0.15 * s), (cx + (x + 0.15) * s, cy + 0.55 * s)], col, 0.09 * s)
    else:
        L.ell((cx - 0.8 * s, cy - 0.35 * s, cx + 0.6 * s, cy + 0.25 * s), col)
        L.ell((cx + 0.45 * s, cy - 0.55 * s, cx + 0.95 * s, cy - 0.1 * s), col)
        L.ell((cx - 0.1 * s, cy - 0.5 * s, cx + 0.25 * s, cy - 0.15 * s), col)
        for x in (-0.6, -0.35, 0.25, 0.45):
            L.line([(cx + x * s, cy + 0.1 * s), (cx + x * s, cy + 0.75 * s)], col, 0.1 * s)
        L.line([(cx + 0.55 * s, cy - 0.5 * s), (cx + 0.5 * s, cy - 0.75 * s)], col, 0.05 * s)
        L.line([(cx + 0.85 * s, cy - 0.5 * s), (cx + 0.9 * s, cy - 0.75 * s)], col, 0.05 * s)


def ic_dog(L, cx, cy, s, col="cream", spots=False):
    L.ell((cx - 0.6 * s, cy - 0.25 * s, cx + 0.45 * s, cy + 0.15 * s), col)
    L.ell((cx + 0.3 * s, cy - 0.55 * s, cx + 0.7 * s, cy - 0.15 * s), col)
    L.poly([(cx + 0.62 * s, cy - 0.4 * s), (cx + 0.95 * s, cy - 0.3 * s), (cx + 0.62 * s, cy - 0.22 * s)], col)
    L.poly([(cx + 0.35 * s, cy - 0.5 * s), (cx + 0.42 * s, cy - 0.78 * s), (cx + 0.52 * s, cy - 0.52 * s)], col)
    for x in (-0.5, -0.3, 0.2, 0.35):
        L.line([(cx + x * s, cy), (cx + x * s, cy + 0.6 * s)], col, 0.09 * s)
    L.line([(cx - 0.55 * s, cy - 0.15 * s), (cx - 0.85 * s, cy - 0.5 * s)], col, 0.07 * s)
    if spots:
        for dx, dy in ((-0.3, -0.1), (0.0, -0.05), (-0.1, 0.05)):
            L.ell((cx + (dx - 0.06) * s, cy + (dy - 0.06) * s, cx + (dx + 0.06) * s, cy + (dy + 0.06) * s), "bg")


def ic_crow(L, cx, cy, s, col="cream"):
    L.ell((cx - 0.5 * s, cy - 0.25 * s, cx + 0.3 * s, cy + 0.2 * s), col)
    L.ell((cx + 0.15 * s, cy - 0.5 * s, cx + 0.5 * s, cy - 0.15 * s), col)
    L.poly([(cx + 0.45 * s, cy - 0.38 * s), (cx + 0.75 * s, cy - 0.3 * s), (cx + 0.45 * s, cy - 0.25 * s)], col)
    L.poly([(cx - 0.45 * s, cy - 0.05 * s), (cx - 0.85 * s, cy + 0.15 * s), (cx - 0.45 * s, cy + 0.15 * s)], col)
    for x in (-0.05, 0.1):
        L.line([(cx + x * s, cy + 0.15 * s), (cx + x * s, cy + 0.5 * s)], col, 0.05 * s)


def ic_rat(L, cx, cy, s, col="cream"):
    L.ell((cx - 0.5 * s, cy - 0.2 * s, cx + 0.35 * s, cy + 0.2 * s), col)
    L.poly([(cx + 0.25 * s, cy - 0.15 * s), (cx + 0.7 * s, cy + 0.05 * s), (cx + 0.25 * s, cy + 0.18 * s)], col)
    L.ell((cx + 0.15 * s, cy - 0.32 * s, cx + 0.35 * s, cy - 0.1 * s), col)
    L.line([(cx - 0.5 * s, cy + 0.05 * s), (cx - 0.8 * s, cy + 0.0 * s), (cx - 1.0 * s, cy + 0.15 * s)], col, 0.04 * s)


def ic_fly(L, cx, cy, s, col="cream"):
    L.ell((cx - 0.3 * s, cy - 0.15 * s, cx + 0.3 * s, cy + 0.15 * s), col)
    L.ell((cx + 0.2 * s, cy - 0.16 * s, cx + 0.45 * s, cy + 0.1 * s), col)
    L.ell((cx - 0.35 * s, cy - 0.65 * s, cx + 0.05 * s, cy - 0.1 * s), None, col, max(1, int(0.05 * s)))
    L.ell((cx - 0.05 * s, cy - 0.6 * s, cx + 0.3 * s, cy - 0.1 * s), None, col, max(1, int(0.05 * s)))


def ic_bacteria(L, cx, cy, s, col="green"):
    L.rrect((cx - 0.6 * s, cy - 0.22 * s, cx + 0.6 * s, cy + 0.22 * s), 0.22 * s, col)
    for k in range(4):
        x = cx - 0.4 * s + k * 0.27 * s
        L.ell((x - 0.05 * s, cy - 0.05 * s, x + 0.05 * s, cy + 0.05 * s), "bg")


def ic_truck(L, cx, cy, s, col="cream"):
    L.rrect((cx - 1.0 * s, cy - 0.5 * s, cx + 0.25 * s, cy + 0.2 * s), 0.06 * s, col)
    L.rrect((cx + 0.3 * s, cy - 0.3 * s, cx + 0.85 * s, cy + 0.2 * s), 0.1 * s, col)
    L.rrect((cx + 0.45 * s, cy - 0.22 * s, cx + 0.75 * s, cy - 0.02 * s), 0.04 * s, "bg")
    for x in (-0.7, -0.2, 0.6):
        L.ell((cx + (x - 0.15) * s, cy + 0.1 * s, cx + (x + 0.15) * s, cy + 0.4 * s), col, "bg", int(0.05 * s))


def ic_vial(L, cx, cy, s, col="cream", band="red"):
    L.rrect((cx - 0.3 * s, cy - 0.5 * s, cx + 0.3 * s, cy + 0.7 * s), 0.12 * s, col)
    L.rrect((cx - 0.3 * s, cy - 0.1 * s, cx + 0.3 * s, cy + 0.25 * s), 0.02 * s, band)
    L.rrect((cx - 0.2 * s, cy - 0.8 * s, cx + 0.2 * s, cy - 0.5 * s), 0.05 * s, band)


def ic_drop(L, cx, cy, s, col="blue"):
    L.poly([(cx, cy - 0.8 * s), (cx + 0.42 * s, cy - 0.05 * s), (cx - 0.42 * s, cy - 0.05 * s)], col)
    L.ell((cx - 0.48 * s, cy - 0.4 * s, cx + 0.48 * s, cy + 0.55 * s), col)


def ic_person(L, cx, cy, s, col="cream"):
    L.ell((cx - 0.22 * s, cy - 0.75 * s, cx + 0.22 * s, cy - 0.31 * s), col)
    L.rrect((cx - 0.3 * s, cy - 0.25 * s, cx + 0.3 * s, cy + 0.6 * s), 0.25 * s, col)


def ic_kidney(L, cx, cy, s, col="red"):
    L.ell((cx - 0.4 * s, cy - 0.6 * s, cx + 0.45 * s, cy + 0.6 * s), col)
    L.ell((cx + 0.15 * s, cy - 0.2 * s, cx + 0.6 * s, cy + 0.2 * s), "bg")


def ic_elephant(L, cx, cy, s, col="cream"):
    L.ell((cx - 0.8 * s, cy - 0.5 * s, cx + 0.5 * s, cy + 0.3 * s), col)
    L.ell((cx + 0.25 * s, cy - 0.6 * s, cx + 0.85 * s, cy + 0.0 * s), col)
    L.ell((cx + 0.15 * s, cy - 0.55 * s, cx + 0.45 * s, cy + 0.05 * s), "dim")
    L.line([(cx + 0.75 * s, cy - 0.2 * s), (cx + 0.85 * s, cy + 0.3 * s), (cx + 0.7 * s, cy + 0.55 * s)], col, 0.12 * s)
    for x in (-0.6, -0.3, 0.05, 0.3):
        L.rrect((cx + (x - 0.1) * s, cy + 0.1 * s, cx + (x + 0.1) * s, cy + 0.7 * s), 0.05 * s, col)


def ic_stomach(L, cx, cy, s, col="red"):
    L.ell((cx - 0.9 * s, cy - 0.6 * s, cx + 0.7 * s, cy + 0.7 * s), col)
    L.ell((cx - 0.3 * s, cy - 0.4 * s, cx + 0.5 * s, cy + 0.35 * s), "bg")
    L.rrect((cx + 0.35 * s, cy - 1.1 * s, cx + 0.7 * s, cy - 0.45 * s), 0.15 * s, col)


ICONS = dict(vulture=ic_vulture, cow=ic_cow, dog=ic_dog, crow=ic_crow, rat=ic_rat, fly=ic_fly, bacteria=ic_bacteria,
             truck=ic_truck, vaccine=ic_vial, water=ic_drop, person=ic_person, kidney=ic_kidney)


def icon_layer(name, s=90, col="cream", **kw):
    L = Layer(int(s * 2.4), int(s * 2.4))
    ICONS[name](L, s * 1.2, s * 1.2, s, col, **kw)
    return L


# ------------------------------------------------------------------ maps
_SHP = None


def countries():
    global _SHP
    if _SHP is None:
        r = shapefile.Reader(SHAPES)
        _SHP = [(rec["name"], rec["iso_a3"], rec["continent"], sh) for rec, sh in zip(r.records(), r.shapes())]
    return _SHP


def map_layer(bbox, w, h, highlight=(), hl_col="mustard", base_col="dim", outline="bg", continent=None):
    """Equirectangular map of lon/lat bbox=(lon0, lat0, lon1, lat1) into a w x h layer."""
    lon0, lat0, lon1, lat1 = bbox
    L = Layer(w, h)

    def pr(lon, lat):
        return ((lon - lon0) / (lon1 - lon0) * w, (lat1 - lat) / (lat1 - lat0) * h)

    for name, iso, cont, sh in countries():
        if continent and cont != continent and iso not in highlight:
            continue
        col = hl_col if (iso in highlight or name in highlight) else base_col
        pts = sh.points
        parts = list(sh.parts) + [len(pts)]
        for a, b in zip(parts[:-1], parts[1:]):
            ring = [pr(x, y) for x, y in pts[a:b]]
            if len(ring) > 2:
                L.poly(ring, col, outline, 1)
    return L, pr


def country_poly(iso):
    for name, i, cont, sh in countries():
        if i == iso:
            return sh
    return None


# ------------------------------------------------------------------ card types
def k_bignum(p, dur):
    c = Card()
    val = p["value"]
    col = "red" if val.startswith(("−", "+", "≈ 5", "$")) else "mustard"
    L = Layer(1700, 330)
    L.text((850, 165), val, 250, "black", col)
    c.add(L, (110, 260), 0.15, 0.6, "pop")
    lab = Layer(1700, 80)
    lab.text((850, 40), p["label"], 46, "semi", "cream")
    c.add(lab, (110, 620), 0.55, 0.5, "up")
    if p.get("icons") == "vultures_fade":
        n = 20
        for i in range(n):
            L2 = icon_layer("vulture", 34, "cream")
            x = 960 - (n * 78) / 2 + i * 78
            c.add(L2, (int(x), 760), 0.9 + i * 0.03, 0.3, "up")
            if i:
                L3 = icon_layer("vulture", 34, "dim")
                c.add(L3, (int(x), 760), 1.6 + i * 0.06, 0.3, "fade")
    add_tag(c, p.get("tag"))
    return c


def k_thermal(p, dur):
    c = Card()
    c.add(title_layer("Riding thermals: rising columns of warm air"), (160, 70), 0.1, 0.5)
    g = Layer(1920, 200)
    g.rrect((0, 120, 1920, 200), 0, "#3A3122")
    g.text((960, 165), "SUN-WARMED GROUND", 30, "bold", "#8C7A5A")
    c.add(g, (0, 880), 0.0, 0.4, "fade")
    for k in range(5):
        a = Layer(80, 560)
        pts = [(40 + 22 * math.sin(i / 6.0 + k), 540 - i * 9) for i in range(60)]
        a.line(pts, "#E0864A", 6)
        a.poly([(40 + 22 * math.sin(59 / 6.0 + k) - 16, 18), (40 + 22 * math.sin(59 / 6.0 + k) + 16, 18),
                (40 + 22 * math.sin(59 / 6.0 + k), -8)], "#E0864A")
        c.add(a, (640 + k * 140, 330), 0.3 + k * 0.12, 0.6, "up")
    v = icon_layer("vulture", 60, "mustard")

    def path(t):
        u = min(1.0, t / max(dur - 0.5, 1))
        ang = u * 6 * math.pi
        return (960 + 240 * math.cos(ang) - 72, 820 - u * 620 + 30 * math.sin(ang) - 72)
    c.add(v, (0, 0), 0.4, 0.3, "move", {"path": path})
    lab = Layer(600, 140)
    lab.text((300, 40), "Barely a wingbeat", 40, "bold", "cream")
    lab.text((300, 100), "circling up for hours", 32, "med", "grey")
    c.add(lab, (1250, 420), 1.2, 0.5)
    return c


def k_gut(p, dur):
    c = Card()
    c.add(title_layer("A digestive firewall"), (160, 70), 0.1, 0.5)
    st = Layer(600, 600)
    ic_stomach(st, 300, 330, 230, "#B9533E")
    c.add(st, (660, 230), 0.2, 0.6, "pop")
    rnd = random.Random(4)
    for i in range(9):
        b = Layer(120, 60)
        ic_bacteria(b, 60, 30, 50, "green")
        y0 = 380 + rnd.uniform(-120, 160)

        def path(t, i=i, y0=y0):
            u = min(1.0, max(0.0, (t - 0.6 - i * 0.25) / 1.8))
            return (200 + u * 640, y0)
        c.add(b, (0, 0), 0.6 + i * 0.25, 0.2, "move", {"path": path, "out": 2.2 + i * 0.25})
    lab = Layer(620, 300)
    lab.text((20, 50), "Harsh stomach acid", 44, "bold", "mustard", anchor="lm")
    lab.text((20, 130), "Specialised gut bacteria", 44, "bold", "green", anchor="lm")
    lab.text((20, 220), "Germs like anthrax are", 32, "med", "grey", anchor="lm")
    lab.text((20, 262), "largely filtered out", 32, "med", "grey", anchor="lm")
    c.add(lab, (1260, 380), 1.2, 0.5, "left")
    add_tag(c, p.get("tag"))
    return c


def k_decline(p, dur):
    c = Card()
    c.add(title_layer("South Asia's Gyps vultures"), (160, 70), 0.1, 0.5)
    base_y, x0 = 900, 520
    ax = Layer(1100, 20)
    ax.rrect((0, 0, 1100, 6), 3, "grey")
    c.add(ax, (x0 - 100, base_y), 0.1, 0.4, "fade")
    for i, (lab, frac, col, t0) in enumerate([("Early 1990s", 1.0, "mustard", 0.3), ("By mid-2000s", 0.045, "red", 1.2)]):
        hgt = int(620 * frac)
        b = Layer(260, max(hgt, 8))
        b.rrect((0, 0, 260, max(hgt, 8)), 10, col)
        c.add(b, (x0 + i * 520, base_y - max(hgt, 8)), t0, 0.6, "up")
        t = Layer(400, 60)
        t.text((200, 30), lab, 36, "bold", "cream")
        c.add(t, (x0 + i * 520 - 70, base_y + 20), t0, 0.4)
    big = Layer(500, 300)
    big.text((250, 90), "−95%+", 120, "black", "red")
    big.text((250, 200), "in about 10 years", 36, "semi", "cream")
    c.add(big, (1250, 360), 1.8, 0.5, "pop")
    wr = Layer(900, 70)
    wr.text((450, 35), "White-rumped vulture: up to −99.9% (some estimates)", 34, "semi", "grey")
    c.add(wr, (510, 990), 2.6, 0.5)
    add_tag(c, p.get("tag"))
    return c


def k_suspects(p, dur):
    c = Card()
    c.add(title_layer("What was killing them?"), (160, 70), 0.1, 0.5)
    for i, s in enumerate(["A virus?", "Pesticides?", "Something in the water?"]):
        L = Layer(520, 300)
        L.rrect((0, 0, 520, 300), 26, "panel", "dim", 3)
        L.text((260, 150), s, 46, "bold", "cream")
        c.add(L, (120 + i * 580, 380), 0.3 + i * 0.6, 0.45, "pop")
        X = Layer(520, 300)
        X.line([(120, 60), (400, 240)], "red", 16)
        X.line([(400, 60), (120, 240)], "red", 16)
        c.add(X, (120 + i * 580, 380), dur - 1.4 + i * 0.25, 0.25, "pop")
    return c


def k_chain(p, dur):
    c = Card()
    c.add(title_layer("How a painkiller kills a vulture"), (160, 70), 0.1, 0.5)
    steps = [("vaccine", "Cow treated with", "diclofenac", {}), ("cow", "It dies; traces", "stay in the body", {"lying": True}),
             ("vulture", "Vultures feed", "on the carcass", {}), ("kidney", "Kidney failure", "within days", {})]
    for i, (ic, a, b, kw) in enumerate(steps):
        x = 120 + i * 440
        panel = Layer(380, 460)
        panel.rrect((0, 0, 380, 460), 28, "panel")
        ICONS[ic](panel, 190, 170, 90, "red" if ic == "kidney" else ("mustard" if ic == "vulture" else "cream"),
                  **kw)
        panel.text((190, 350), a, 34, "bold", "cream")
        panel.text((190, 400), b, 32, "med", "grey")
        c.add(panel, (x, 330), 0.3 + i * 0.7, 0.5, "up")
        if i < 3:
            ar = Layer(80, 60)
            ar.poly([(0, 18), (45, 18), (45, 0), (80, 30), (45, 60), (45, 42), (0, 42)], "mustard")
            c.add(ar, (x + 382, 530), 0.6 + i * 0.7, 0.3, "left")
    add_tag(c, p.get("tag"))
    return c


def k_timeline(p, dur):
    c = Card()
    items = p["items"]
    ln = Layer(1500, 12)
    ln.rrect((0, 0, 1500, 10), 5, "grey")
    c.add(ln, (210, 560), 0.1, 0.8, "wipe")
    for i, (yr, lab) in enumerate(items):
        x = 360 + i * (1200 // max(1, len(items) - 1) if len(items) > 1 else 0)
        dot = Layer(60, 60)
        dot.ell((0, 0, 60, 60), "mustard")
        c.add(dot, (x - 30, 535), 0.4 + i * 1.2, 0.35, "pop")
        t = Layer(700, 230)
        t.text((350, 60), yr, 96, "black", "mustard")
        t.text((350, 170), lab, 42, "bold", "cream")
        c.add(t, (x - 350, 270 if i % 2 == 0 else 620), 0.5 + i * 1.2, 0.5)
    add_tag(c, p.get("tag"))
    return c


def k_grid(p, dur):
    c = Card()
    c.add(title_layer("How much poisoned meat did it take?"), (160, 60), 0.1, 0.5)
    cols, rows = 26, 10
    g = Layer(1300, 520)
    for i in range(cols * rows):
        x, y = (i % cols) * 50 + 25, (i // cols) * 52 + 26
        g.ell((x - 14, y - 14, x + 14, y + 14), "dim")
    c.add(g, (310, 200), 0.3, 0.6, "fade")
    red = Layer(1300, 520)
    for x, y in [(7 * 50 + 25, 3 * 52 + 26), (20 * 50 + 25, 7 * 52 + 26)]:
        red.ell((x - 18, y - 18, x + 18, y + 18), "red")
    c.add(red, (310, 200), 1.3, 0.4, "pop")
    t = Layer(1600, 200)
    t.text((800, 55), "Lethal dose in as few as 1 carcass in 130 to 1 in 760", 46, "bold", "cream")
    t.text((800, 140), "could explain the whole collapse (Green et al. 2004)", 34, "med", "grey")
    c.add(t, (160, 780), 1.8, 0.5)
    add_tag(c, p.get("tag"))
    return c


def k_redlist(p, dur):
    c = Card()
    c.add(title_layer("IUCN Red List status"), (160, 80), 0.1, 0.5)
    for i, sp in enumerate(["White-rumped vulture", "Indian vulture", "Slender-billed vulture"]):
        L = Layer(1300, 160)
        L.rrect((0, 0, 1300, 160), 24, "panel")
        ic_vulture(L, 120, 80, 70, "mustard")
        L.text((240, 80), sp, 50, "bold", "cream", anchor="lm")
        L.rrect((820, 40, 1260, 120), 40, "red")
        L.text((1040, 80), "CRITICALLY ENDANGERED", 28, "bold", "cream")
        c.add(L, (310, 280 + i * 200), 0.3 + i * 0.5, 0.5, "left")
    add_tag(c, p.get("tag"))
    return c


def k_compare(p, dur):
    c = Card()
    c.add(title_layer(p["title"] + ": vultures kept away from carcasses", 50), (160, 80), 0.1, 0.5)
    for i, (lab, mult) in enumerate(p["rows"]):
        y = 300 + i * 300
        t = Layer(600, 100)
        t.text((0, 50), lab, 46, "bold", "cream", anchor="lm")
        c.add(t, (160, y + 20), 0.4 + i * 1.0, 0.4, "left")
        b1 = Layer(230, 50)
        b1.rrect((0, 0, 230, 50), 12, "grey")
        b1.text((16, 25), "with vultures", 24, "semi", "bg", anchor="lm")
        c.add(b1, (780, y + 10), 0.6 + i * 1.0, 0.4, "wipe")
        k = float(mult.strip("×"))
        b2 = Layer(int(230 * k), 50)
        b2.rrect((0, 0, int(230 * k), 50), 12, "red")
        b2.text((16, 25), "vultures kept away", 24, "semi", "cream", anchor="lm")
        c.add(b2, (780, y + 80), 0.9 + i * 1.0, 0.6, "wipe")
        lg = Layer(260, 140)
        lg.text((0, 35), "with vultures", 26, "med", "grey", anchor="lm")
        lg.text((0, 105), "without", 26, "med", "red", anchor="lm")
        m = Layer(260, 160)
        m.text((130, 80), mult, 120, "black", "red")
        c.add(m, (1560, y - 10), 1.3 + i * 1.0, 0.4, "pop")
    add_tag(c, p.get("tag"))
    return c


def k_lines(p, dur):
    c = Card()
    c.add(title_layer("As vultures fell, feral dogs rose"), (160, 70), 0.1, 0.5)
    x0, y0, w, h = 260, 260, 1400, 560
    ax = Layer(w + 40, h + 80)
    ax.line([(20, 0), (20, h), (w + 20, h)], "grey", 4, "")
    ax.text((60, h + 45), "1990", 30, "med", "grey", anchor="mm")
    ax.text((w - 20, h + 45), "2005", 30, "med", "grey", anchor="mm")
    c.add(ax, (x0 - 20, y0), 0.1, 0.4, "fade")
    v = Layer(w + 40, h)
    v.line([(20 + w * i / 50, h * (0.08 + 0.85 / (1 + math.exp(-(i - 22) / 3.5)))) for i in range(51)], "mustard", 10)
    c.add(v, (x0 - 20, y0), 0.5, 2.0, "wipe")
    d = Layer(w + 40, h)
    d.line([(20 + w * i / 50, h * (0.85 - 0.55 / (1 + math.exp(-(i - 26) / 6)))) for i in range(51)], "red", 10)
    c.add(d, (x0 - 20, y0), 0.8, 2.0, "wipe")
    lg = Layer(500, 150)
    lg.text((0, 40), "Vultures", 40, "bold", "mustard", anchor="lm")
    lg.text((0, 110), "Feral dogs", 40, "bold", "red", anchor="lm")
    c.add(lg, (1400, 300), 2.4, 0.5)
    n = Layer(1400, 60)
    n.text((700, 30), "Illustrative trend, not data. Whether one caused the other is debated.", 30, "med", "grey")
    c.add(n, (260, 930), 2.8, 0.5)
    add_tag(c, p.get("tag"))
    return c


def k_fraction(p, dur):
    c = Card()
    L, pr = map_layer((-170, -58, 180, 80), 1100, 540, highlight=("IND",), hl_col="mustard", base_col="dim")
    c.add(L, (90, 300), 0.1, 0.8, "fade")
    big = Layer(700, 280)
    big.text((350, 140), p["value"], 200, "black", "mustard")
    c.add(big, (1150, 300), 0.8, 0.6, "pop")
    lab = Layer(700, 200)
    for k, line in enumerate(["of the world's rabies deaths", "happen in India (WHO)", "Dogs cause almost all of them"]):
        lab.text((350, 40 + k * 62), line, 38 if k < 2 else 32, "semi" if k < 2 else "med", "cream" if k < 2 else "grey")
    c.add(lab, (1150, 600), 1.3, 0.5)
    add_tag(c, p.get("tag"))
    return c


def k_paper(p, dur):
    c = Card()
    pg = Layer(1100, 640)
    pg.rrect((0, 0, 1100, 640), 18, "#F3EEDF")
    pg.text((60, 90), "AMERICAN ECONOMIC REVIEW · 2024", 28, "bold", "#9A3B2A", anchor="lm")
    words = p["title"].split()
    lines, cur = [], ""
    for w_ in words:
        if F("black", 60).getlength(cur + " " + w_) > 960:
            lines.append(cur)
            cur = w_
        else:
            cur = (cur + " " + w_).strip()
    lines.append(cur)
    for k, ln_ in enumerate(lines):
        pg.text((60, 200 + k * 76), ln_, 60, "black", "#2B2420", anchor="lm")
    pg.text((60, 200 + len(lines) * 76 + 50), "Evidence from the Decline of Vultures in India", 34, "semi", "#5A4E44", anchor="lm")
    pg.text((60, 560), "Eyal Frank · Anant Sudarshan", 34, "bold", "#2B2420", anchor="lm")
    for k in range(4):
        pg.rrect((60, 420 + k * 26 + 0, 60 + 980 - k * 120, 420 + k * 26 + 10), 5, "#D9D1BE")
    c.add(pg, (410, 260), 0.3, 0.6, "up")
    ch = p.get("chapter")
    if ch:
        L = Layer(900, 150)
        L.text((0, 40), ch["sub"].upper(), 30, "bold", "mustard", anchor="lm")
        L.text((0, 105), ch["main"], 72, "black", "cream", anchor="lm")
        c.add(L, (110, 60), 0.1, 0.5, "left")
    return c


def k_districts(p, dur):
    c = Card()
    sh = country_poly("IND")
    lon0, lat0, lon1, lat1 = 67, 6, 98, 37
    w, h = 760, 760

    def pr(lon, lat):
        return ((lon - lon0) / (lon1 - lon0) * w, (lat1 - lat) / (lat1 - lat0) * h)

    from PIL import ImageDraw as _ID
    mask = Image.new("L", (w, h), 0)
    md = _ID.Draw(mask)
    pts = sh.points
    parts = list(sh.parts) + [len(pts)]
    for a, b in zip(parts[:-1], parts[1:]):
        md.polygon([pr(x, y) for x, y in pts[a:b]], fill=255)
    for side, (ox, title, t0) in enumerate([(130, "BEFORE (1990)", 0.3), (1030, "AFTER (2005)", 1.4)]):
        L = Layer(w, h + 120)
        rnd = random.Random(5)
        for gx in range(0, w, 34):
            for gy in range(0, h, 34):
                if mask.getpixel((min(w - 1, gx + 17), min(h - 1, gy + 17))) > 0:
                    rich = rnd.random() < 0.55
                    col = ("mustard" if rich else "dim") if side == 0 else ("#6B5A2E" if rich else "dim")
                    L.rrect((gx + 3, gy + 3, gx + 31, gy + 31), 6, col)
        L.text((w / 2, h + 60), title, 40, "bold", "cream")
        c.add(L, (ox, 140), t0, 0.6, "fade")
    lg = Layer(1700, 60)
    lg.text((850, 30), "Schematic: districts suitable for vultures (gold) vs. not (grey). Compare deaths before and after.",
            28, "med", "grey")
    c.add(lg, (110, 1000), 2.2, 0.5)
    return c


def k_icons2(p, dur):
    c = Card()
    for i, (ic, lab) in enumerate([p["left"], p["right"]]):
        x = 260 + i * 760
        pan = Layer(640, 620)
        pan.rrect((0, 0, 640, 620), 30, "panel")
        ICONS[ic](pan, 320, 250, 130, "cream" if ic == "vaccine" else "blue")
        if ic == "water":
            for dx, dy in ((-40, 260), (30, 300), (60, 230)):
                ic_bacteria(pan, 320 + dx, dy, 22, "green")
        up = "↑" in lab
        ar = [(560, 120), (600, 60), (640, 120)] if up else [(560, 60), (600, 120), (640, 60)]
        pan.poly([(x_ - 60, y_) for x_, y_ in ar], "red")
        pan.text((320, 540), lab.replace("↑", "").replace("↓", "").strip(), 42, "bold", "cream")
        c.add(pan, (x, 230), 0.3 + i * 1.6, 0.5, "pop")
    add_tag(c, p.get("tag"))
    return c


def k_map(p, dur):
    c = Card()
    L, pr = map_layer((-15, 30, 35, 62), 1600, 900, highlight=(p["country"],), hl_col="mustard", base_col="dim")
    c.add(L, (160, 90), 0.1, 0.8, "fade")
    x, y = pr(-3.7, 40.3)
    lab = Layer(500, 100)
    lab.text((250, 50), p["label"].upper(), 60, "black", "cream", stroke=4)
    c.add(lab, (int(160 + x - 250), int(90 + y - 50)), 0.8, 0.5, "pop")
    return c


def k_trucks(p, dur):
    c = Card()
    c.add(title_layer("Instead of vultures: collection trucks"), (160, 80), 0.1, 0.5)
    road = Layer(1920, 120)
    road.rrect((0, 30, 1920, 110), 0, "#2E3A33")
    for k in range(0, 1920, 120):
        road.rrect((k, 66, k + 60, 74), 3, "grey")
    c.add(road, (0, 620), 0.1, 0.4, "fade")
    for i in range(3):
        tl = icon_layer("truck", 70, "cream")

        def path(t, i=i):
            return (-260 + ((t * 260 + i * 650) % 2400), 470)
        c.add(tl, (0, 0), 0.3 + i * 0.3, 0.3, "move", {"path": path})
    n = Layer(1600, 160)
    n.text((800, 45), "EU sanitary rules after the BSE (mad cow) crisis:", 38, "semi", "grey")
    n.text((800, 115), "dead livestock collected and processed, not left out", 44, "bold", "cream")
    c.add(n, (160, 830), 0.8, 0.5)
    return c


def k_trucks_numbers(p, dur):
    c = Card()
    c.add(title_layer("Spain's carcass collection, per year (Morales-Reyes et al. 2015)", 46), (160, 80), 0.1, 0.5)
    for i, (target, fmt, unit, col) in enumerate([(49.8, "{:.1f} million", "km driven", "cream"),
                                                 (77344, "{:,.0f} t", "of CO₂-equivalent (a minimum)", "red")]):
        x = 160 + i * 820
        pan = Layer(760, 420)
        pan.rrect((0, 0, 760, 420), 30, "panel")
        c.add(pan, (x, 280), 0.3 + i * 0.8, 0.5, "pop")

        def draw(im, t, i=i, target=target, fmt=fmt, unit=unit, col=col, x=x):
            t0 = 0.6 + i * 0.8
            if t < t0:
                return
            v = target * ease((t - t0) / 1.6)
            d = ImageDraw.Draw(im)
            d.text((x + 380, 420), fmt.format(v), font=F("black", 96), fill=rgba(C[col]), anchor="mm")
            d.text((x + 380, 540), unit, font=F("semi", 36), fill=rgba(C["grey"]), anchor="mm")
        c.dyn.append(draw)
    add_tag(c, p.get("tag"))
    return c


def k_africa(p, dur):
    c = Card()
    L, pr = map_layer((-20, -36, 53, 38), 720, 730, continent="Africa", base_col="mustard")
    c.add(L, (130, 200), 0.1, 0.8, "fade")
    rows = [("8 species", "fell 62% on average", "mustard"), ("7 of them", "fell 80% or more", "red"),
            ("", "over just three generations", "grey")]
    for i, (a, b, col) in enumerate(rows):
        t = Layer(1000, 130)
        if a:
            t.text((0, 45), a, 70, "black", col, anchor="lm")
        t.text((0, 105 if a else 60), b, 40, "semi", "cream" if a else "grey", anchor="lm")
        c.add(t, (930, 260 + i * 190), 0.6 + i * 0.8, 0.5, "left")
    s = Layer(800, 60)
    s.text((0, 30), "Ogada et al. 2016, Conservation Letters", 28, "med", "grey", anchor="lm")
    c.add(s, (930, 900), 2.6, 0.5)
    add_tag(c, p.get("tag"))
    return c


def k_poison(p, dur):
    c = Card()
    e = Layer(500, 380)
    ic_elephant(e, 250, 200, 200, "grey")
    c.add(e, (280, 420), 0.2, 0.5, "fade")
    rnd = random.Random(8)
    for i in range(14):
        v = icon_layer("vulture", 34, "mustard")
        x = rnd.uniform(160, 820)
        y = rnd.uniform(140, 330)

        y1 = rnd.uniform(650, 790)

        def path(t, x=x, y=y, i=i, y1=y1):
            u = ease((t - 2.0 - i * 0.08) / 1.2)
            return (x, y + u * (y1 - y))
        c.add(v, (0, 0), 0.4 + i * 0.05, 0.3, "move", {"path": path})
    t = Layer(820, 420)
    t.text((0, 60), "Poisoned on purpose", 54, "black", "cream", anchor="lm")
    t.text((0, 140), "so circling vultures can't", 38, "semi", "grey", anchor="lm")
    t.text((0, 190), "lead rangers to the kill", 38, "semi", "grey", anchor="lm")
    t.text((0, 300), "~500", 110, "black", "red", anchor="lm")
    t.text((0, 380), "vultures at one carcass (Namibia)", 36, "semi", "cream", anchor="lm")
    c.add(t, (1000, 280), 1.0, 0.6, "left")
    add_tag(c, p.get("tag"))
    return c


def k_replacements(p, dur):
    c = Card()
    c.add(title_layer("Who else eats the dead?"), (160, 80), 0.1, 0.5)
    items = [("dog", "Dogs", {}), ("dog", "Jackals", {}), ("dog", "Hyenas", {"spots": True}), ("crow", "Crows", {}),
             ("rat", "Rats", {}), ("fly", "Flies", {}), ("bacteria", "Bacteria", {})]
    for i, (ic, lab, kw) in enumerate(items):
        pan = Layer(230, 300)
        pan.rrect((0, 0, 230, 300), 24, "panel")
        ICONS[ic](pan, 115, 120, 70, "green" if ic == "bacteria" else "cream", **kw)
        pan.text((115, 250), lab, 34, "bold", "cream")
        c.add(pan, (115 + i * 250, 400), 0.3 + i * 0.45, 0.4, "pop")
    return c


def k_checklist(p, dur):
    c = Card()
    cols = ["Spots a carcass from afar", "Strips it in minutes", "Destroys the germs"]
    rows = [("Vultures", ["✓", "✓", "✓"]), ("Dogs, jackals, hyenas", ["~", "~", "✗"]),
            ("Crows", ["✓", "✗", "✗"]), ("Flies, bacteria", ["✗", "✗", "✗"])]
    hdr = Layer(1700, 120)
    for j, s in enumerate(cols):
        hdr.text((700 + j * 340, 60), s, 30, "bold", "grey")
    c.add(hdr, (110, 180), 0.1, 0.5)
    sym = {"✓": ("leaf", "✓"), "~": ("mustard", "~"), "✗": ("red", "✗")}
    for i, (name, vals) in enumerate(rows):
        r = Layer(1700, 140)
        r.rrect((0, 0, 1700, 140), 22, "panel" if i else "#2D4A3B")
        r.text((40, 70), name, 44, "bold", "mustard" if i == 0 else "cream", anchor="lm")
        for j, v in enumerate(vals):
            col, ch = sym[v]
            r.ell((700 + j * 340 - 45, 25, 700 + j * 340 + 45, 115), col)
            r.text((700 + j * 340, 70), ch, 56, "black", "cream")
        c.add(r, (110, 320 + i * 165), 0.4 + i * 0.6, 0.45, "left")
    add_tag(c, p.get("tag"))
    return c


def k_keystone(p, dur):
    c = Card()
    cx, cy, R = 960, 860, 430
    n = 9
    stones = []
    for i in range(n):
        a0 = math.pi - i * math.pi / n
        a1 = math.pi - (i + 1) * math.pi / n
        pts = []
        for a in (a0, a1):
            pts.append((cx + R * math.cos(a), cy - R * math.sin(a)))
        for a in (a1, a0):
            pts.append((cx + (R - 150) * math.cos(a), cy - (R - 150) * math.sin(a)))
        stones.append(pts)
    for i, pts in enumerate(stones):
        if i == n // 2:
            continue
        L = Layer(1920, 1080)
        L.poly(pts, "#9C8F79", "bg", 3)
        c.add(L, (0, 0), 0.1 + i * 0.08, 0.4, "up")
    k = Layer(1920, 1080)
    k.poly(stones[n // 2], "mustard", "bg", 3)
    ic_vulture(k, cx, cy - R + 75, 55, "dark")

    def path(t):
        u = ease((t - 2.4) / 1.0)
        return (0, -u * 260)
    c.add(k, (0, 0), 0.9, 0.4, "move", {"path": path})
    lab = Layer(1600, 100)
    lab.text((800, 50), "Keystone species: remove it and the structure fails", 44, "bold", "cream")
    c.add(lab, (160, 930), 1.4, 0.5)
    return c


def k_bans(p, dur):
    c = Card()
    c.add(title_layer("India's veterinary drug bans"), (160, 80), 0.1, 0.5)
    for i, (drug, yr) in enumerate([("Diclofenac", "2006"), ("Ketoprofen", "2023"), ("Aceclofenac", "2023")]):
        pan = Layer(520, 480)
        pan.rrect((0, 0, 520, 480), 30, "panel")
        ic_vial(pan, 260, 140, 85, "cream", "red")
        pan.text((260, 280), drug, 48, "black", "cream")
        pan.text((260, 335), "for animals · " + yr, 32, "semi", "grey")
        c.add(pan, (130 + i * 580, 280), 0.3 + i * 0.8, 0.5, "up")
        st = Layer(420, 130)
        st.rrect((0, 0, 420, 130), 18, None, "red", 10)
        st.text((210, 65), "BANNED", 70, "black", "red")
        c.add(st.done().rotate(-8, expand=True, resample=Image.BICUBIC), (175 + i * 580, 620), 0.8 + i * 0.8, 0.3,
              "pop")
    add_tag(c, p.get("tag"))
    return c


KINDS = {k[2:]: v for k, v in globals().items() if k.startswith("k_")}


def card(kind, params, dur):
    return KINDS[kind](params, dur).frame


# ------------------------------------------------------------------ plate overlays
def overlay_fn(v, dur, seed=0):
    """Returns draw(im RGBA, t) for plate/anim overlays: tab, tag, text, fx."""
    rnd = random.Random(seed)
    layers = []
    tab = v.get("tab")
    if tab:
        main, _, sub = tab.partition(" · ")
        wm = F("black", 44).getlength(main)
        ws = F("semi", 32).getlength(sub) if sub else 0
        w = int(wm + ws + (70 if sub else 50))
        L = Layer(w + 20, 84)
        L.rrect((0, 0, w, 76), 14, "mustard")
        L.text((24, 38), main, 44, "black", "dark", anchor="lm")
        if sub:
            L.text((24 + wm + 26, 40), sub, 32, "semi", "dark", anchor="lm")
        layers.append((L.done(), (70, H - 150), 0.3, "left", None))
    if v.get("tag"):
        L, w = tag_layer(v["tag"])
        layers.append((L.done(), (W - w - 70, H - 126), 0.6, "left", None))
    tx = v.get("text")
    if tx:
        st = tx["style"]
        if st == "title":
            L = Layer(W, 420)
            L.rrect((260, 40, W - 260, 380), 40, "#14211CCC" if False else "bg")
            L.text((W / 2, 150), tx["main"], 92, "black", "cream")
            L.text((W / 2, 270), tx["sub"], 120, "black", "mustard")
            layers.append((L.done(), (0, 300), 0.6, "pop", None))
        elif st == "chapter":
            L = Layer(1000, 170)
            L.rrect((0, 0, 1000, 170), 24, "bg")
            L.rrect((0, 0, 14, 170), 6, "mustard")
            L.text((50, 52), tx["sub"].upper(), 30, "bold", "mustard", anchor="lm")
            L.text((50, 115), tx["main"], 64, "black", "cream", anchor="lm")
            layers.append((L.done(), (70, 70), 0.3, "left", 3.4))
        elif st == "callout":
            L = Layer(760, 260)
            L.text((380, 100), tx["main"], 140, "black", "cream", stroke=6, stroke_fill="bg")
            L.text((380, 210), tx["sub"], 40, "bold", "mustard", stroke=4, stroke_fill="bg")
            layers.append((L.done(), (W - 840, 120), 0.8, "pop", None))
        elif st == "label":
            wv = int(max(F("black", 64).getlength(tx["main"]), F("semi", 34).getlength(tx["sub"]))) + 100
            L = Layer(wv, 190)
            L.rrect((0, 0, wv, 180), 26, "bg")
            L.text((wv / 2, 70), tx["main"], 64, "black", "mustard")
            L.text((wv / 2, 135), tx["sub"], 34, "semi", "cream")
            layers.append((L.done(), (int(W / 2 - wv / 2), H - 300), 0.5, "up", None))
        elif st == "end":
            L = Layer(W, 360)
            L.rrect((360, 30, W - 360, 330), 40, "bg")
            L.text((W / 2, 140), tx["main"], 84, "black", "cream")
            L.text((W / 2, 250), tx["sub"], 44, "bold", "mustard")
            layers.append((L.done(), (0, 330), 1.2, "pop", None))
    fx = v.get("fx", [])
    flies = [(rnd.uniform(0.38, 0.62), rnd.uniform(0.55, 0.78), rnd.uniform(0, 6.28), rnd.uniform(0.6, 1.6))
             for _ in range(70 if "flies" in fx else 0)]
    dust = [(rnd.uniform(0, 1), rnd.uniform(0, 1), rnd.uniform(0.5, 2.5), rnd.uniform(0, 6.28))
            for _ in range(60 if "dust" in fx else 0)]
    rain = [(rnd.uniform(0, 1), rnd.uniform(0, 1)) for _ in range(260 if "rain" in fx else 0)]

    def draw(im, t):
        if not fx:
            return draw_layers(im, t)
        fxl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(fxl, "RGBA")
        for fx_, fy, ph, sp in flies:
            x = (fx_ + 0.03 * math.sin(t * 7 * sp + ph) + 0.02 * math.sin(t * 13 + ph * 2)) * W
            y = (fy + 0.025 * math.cos(t * 9 * sp + ph)) * H
            d.ellipse([x - 3, y - 3, x + 3, y + 3], fill=(20, 18, 16, 230))
        for dx, dy, sz, ph in dust:
            x = ((dx + 0.01 * t) % 1) * W
            y = ((dy - 0.006 * t + 0.01 * math.sin(t + ph)) % 1) * H
            d.ellipse([x - sz, y - sz, x + sz, y + sz], fill=(255, 240, 210, 90))
        for rx, ry in rain:
            x = ((rx + 0.12 * t) % 1) * W
            y = ((ry + 0.9 * t) % 1) * H
            d.line([(x, y), (x - 10, y + 34)], fill=(220, 230, 240, 110), width=2)
        if "heat" in fx:
            d.rectangle([0, 0, W, H], fill=(255, 170, 80, 18))
        im.alpha_composite(fxl)
        draw_layers(im, t)

    def draw_layers(im, t):
        for img, (x, y), t0, mode, out in layers:
            if t < t0:
                continue
            k = ease((t - t0) / 0.45)
            if out and t > out:
                k *= 1 - ease((t - out) / 0.45)
            if k <= 0:
                continue
            src = img
            dx = dy = 0
            if mode == "left":
                dx = int((1 - k) * -80)
            elif mode == "up":
                dy = int((1 - k) * 40)
            elif mode == "pop":
                s = 0.75 + 0.25 * back_out((t - t0) / 0.5)
                if abs(s - 1) > 0.01:
                    src = img.resize((max(1, int(img.width * s)), max(1, int(img.height * s))), Image.BILINEAR)
                    dx, dy = (img.width - src.width) // 2, (img.height - src.height) // 2
            if k < 1:
                src = src.copy()
                src.putalpha(src.getchannel("A").point(lambda a, k=k: int(a * k)))
            im.alpha_composite(src, (x + dx, y + dy))
    return draw
