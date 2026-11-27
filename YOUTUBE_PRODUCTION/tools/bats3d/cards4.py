"""Episode 4 evidence cards: same design system as Episode 3 (cards.py), but each card sits over a defocused,
darkened frame of the film's 3D world (so cards and 3D shots feel like one production), with bat-themed icons.
"""
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "vulture3d"))
import cards as K  # noqa: E402
from cards import H, W, Card, Layer, add_tag, ease, title_layer  # noqa: E402

C = K.C
C.update(coral="#F0705A", teal="#4FB3B0", violet="#9C7BD8", gold="#F6C04A")


# ------------------------------------------------------------------ icons
def ic_bat(L, cx, cy, s, col="cream"):
    pts = [(-1.0, -0.05), (-0.78, -0.32), (-0.55, -0.12), (-0.4, -0.3), (-0.22, -0.08), (-0.1, -0.22), (-0.06, -0.36),
           (0.0, -0.26), (0.06, -0.36), (0.1, -0.22), (0.22, -0.08), (0.4, -0.3), (0.55, -0.12), (0.78, -0.32),
           (1.0, -0.05), (0.72, 0.12), (0.5, 0.05), (0.32, 0.2), (0.14, 0.12), (0.0, 0.3), (-0.14, 0.12), (-0.32, 0.2),
           (-0.5, 0.05), (-0.72, 0.12)]
    L.poly([(cx + x * s, cy + y * s) for x, y in pts], col)


def ic_moth(L, cx, cy, s, col="cream"):
    L.ell((cx - s * 0.9, cy - s * 0.5, cx - s * 0.05, cy + s * 0.25), col)
    L.ell((cx + s * 0.05, cy - s * 0.5, cx + s * 0.9, cy + s * 0.25), col)
    L.ell((cx - s * 0.6, cy + s * 0.05, cx - s * 0.05, cy + s * 0.55), col)
    L.ell((cx + s * 0.05, cy + s * 0.05, cx + s * 0.6, cy + s * 0.55), col)
    L.rrect((cx - s * 0.08, cy - s * 0.5, cx + s * 0.08, cy + s * 0.5), int(s * 0.08), "bg")


def ic_beetle(L, cx, cy, s, col="cream"):
    L.ell((cx - s * 0.5, cy - s * 0.55, cx + s * 0.5, cy + s * 0.65), col)
    L.ell((cx - s * 0.3, cy - s * 0.85, cx + s * 0.3, cy - s * 0.4), col)
    L.line([(cx, cy - s * 0.45), (cx, cy + s * 0.6)], "bg", max(2, int(s * 0.06)))
    for k in (-1, 1):
        for j in (-0.2, 0.15, 0.45):
            L.line([(cx + k * s * 0.45, cy + j * s), (cx + k * s * 0.85, cy + (j + 0.12) * s)], col, max(2, int(s * 0.07)))


def ic_mosquito(L, cx, cy, s, col="cream"):
    L.ell((cx - s * 0.1, cy - s * 0.4, cx + s * 0.1, cy + s * 0.5), col)
    L.ell((cx - s * 0.7, cy - s * 0.3, cx - s * 0.05, cy - s * 0.05), col)
    L.ell((cx + s * 0.05, cy - s * 0.3, cx + s * 0.7, cy - s * 0.05), col)
    L.line([(cx, cy - s * 0.4), (cx, cy - s * 0.85)], col, max(2, int(s * 0.04)))
    for k in (-1, 1):
        L.line([(cx, cy + s * 0.1), (cx + k * s * 0.8, cy + s * 0.75)], col, max(2, int(s * 0.04)))


def ic_fruit(L, cx, cy, s, col="coral"):
    L.ell((cx - s * 0.6, cy - s * 0.45, cx + s * 0.6, cy + s * 0.75), col)
    L.ell((cx - s * 0.05, cy - s * 0.85, cx + s * 0.45, cy - s * 0.45), "green")


def ic_flower(L, cx, cy, s, col="gold"):
    for k in range(6):
        a = k * math.pi / 3
        x, y = cx + math.cos(a) * s * 0.45, cy + math.sin(a) * s * 0.45
        L.ell((x - s * 0.32, y - s * 0.32, x + s * 0.32, y + s * 0.32), col)
    L.ell((cx - s * 0.25, cy - s * 0.25, cx + s * 0.25, cy + s * 0.25), "coral")


def ic_drop(L, cx, cy, s, col="red"):
    L.poly([(cx, cy - s * 0.9), (cx + s * 0.55, cy + s * 0.1), (cx, cy + s * 0.75), (cx - s * 0.55, cy + s * 0.1)], col)
    L.ell((cx - s * 0.55, cy - s * 0.25, cx + s * 0.55, cy + s * 0.75), col)


def ic_tree(L, cx, cy, s, col="green"):
    L.rrect((cx - s * 0.1, cy, cx + s * 0.1, cy + s * 0.9), int(s * 0.05), "#8A6A4A")
    for dx, dy, r in ((0, -0.35, 0.55), (-0.4, 0.0, 0.42), (0.4, 0.0, 0.42)):
        L.ell((cx + (dx - r) * s, cy + (dy - r) * s, cx + (dx + r) * s, cy + (dy + r) * s), col)


def ic_corn(L, cx, cy, s, col="gold"):
    L.ell((cx - s * 0.3, cy - s * 0.9, cx + s * 0.3, cy + s * 0.9), col)
    for r in range(7):
        for q in (-0.12, 0.12):
            y = cy - s * 0.7 + r * s * 0.22
            L.ell((cx + q * s - s * 0.08, y - s * 0.08, cx + q * s + s * 0.08, y + s * 0.08), "#E8B830")
    L.poly([(cx - s * 0.35, cy + s * 0.2), (cx - s * 0.8, cy - s * 0.6), (cx - s * 0.2, cy + s * 0.9)], "leaf")
    L.poly([(cx + s * 0.35, cy + s * 0.2), (cx + s * 0.8, cy - s * 0.6), (cx + s * 0.2, cy + s * 0.9)], "leaf")


def ic_virus(L, cx, cy, s, col="violet"):
    for k in range(10):
        a = k * math.pi / 5
        L.line([(cx, cy), (cx + math.cos(a) * s * 0.85, cy + math.sin(a) * s * 0.85)], col, max(2, int(s * 0.08)))
        x, y = cx + math.cos(a) * s * 0.85, cy + math.sin(a) * s * 0.85
        L.ell((x - s * 0.12, y - s * 0.12, x + s * 0.12, y + s * 0.12), col)
    L.ell((cx - s * 0.55, cy - s * 0.55, cx + s * 0.55, cy + s * 0.55), col)


def ic_heart(L, cx, cy, s, col="coral"):
    L.ell((cx - s * 0.8, cy - s * 0.6, cx, cy + s * 0.2), col)
    L.ell((cx, cy - s * 0.6, cx + s * 0.8, cy + s * 0.2), col)
    L.poly([(cx - s * 0.78, cy - s * 0.1), (cx + s * 0.78, cy - s * 0.1), (cx, cy + s * 0.85)], col)


ICONS = dict(bat=ic_bat, moth=ic_moth, beetle=ic_beetle, mosquito=ic_mosquito, fruit=ic_fruit, flower=ic_flower,
             drop=ic_drop, tree=ic_tree, corn=ic_corn, virus=ic_virus, heart=ic_heart)


def icon(name, s=90, col="cream"):
    L = Layer(int(s * 2.4), int(s * 2.4))
    ICONS[name](L, s * 1.2, s * 1.2, s, col)
    return L


# ------------------------------------------------------------------ backdrop
def backdrop(bg):
    if bg is None:
        return K.make_bg()
    im = bg.copy()
    g = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(g)
    for r in range(10, 0, -1):
        d.ellipse([W / 2 - r * 120, H / 2 - r * 75, W / 2 + r * 120, H / 2 + r * 75], fill=int(120 * (1 - r / 10)))
    g = g.filter(ImageFilter.GaussianBlur(70))
    dark = Image.new("RGBA", (W, H), K.rgba(C["bg"], 118))
    im.alpha_composite(dark)
    lift = Image.new("RGBA", (W, H), K.rgba(C["bg2"], 255))
    return Image.composite(lift, im, g.point(lambda v: v // 4))


def panel(w, h, a=200):
    L = Layer(w, h)
    L.rrect((0, 0, w, h), 30, K.rgba(C["bg"], a)[:3] and "bg")
    return L


# ------------------------------------------------------------------ cards
def k_bignum(p, dur):
    c = Card(bg=False)
    val = p["value"]
    col = "coral" if val.startswith(("−", "+", "≈", "$", "M")) else "gold"
    L = Layer(1700, 330)
    L.text((850, 165), val, 210 if len(val) > 6 else 250, "black", col)
    c.add(L, (110, 250), 0.15, 0.6, "pop")
    lab = Layer(1700, 80)
    lab.text((850, 40), p["label"], 46, "semi", "cream")
    c.add(lab, (110, 610), 0.55, 0.5, "up")
    if p.get("icons") == "bats_fade":
        n = 22
        for i in range(n):
            x = 960 - (n * 74) / 2 + i * 74
            c.add(icon("bat", 34, "cream"), (int(x) - 10, 720), 0.9 + i * 0.03, 0.3, "up")
            if i % 11:
                c.add(icon("bat", 34, "dim"), (int(x) - 10, 720), 1.7 + i * 0.07, 0.3, "fade")
    add_tag(c, p.get("tag"))
    return c


def k_fraction(p, dur):
    c = Card(bg=False)
    c.add(title_layer("Bats are a huge branch of the mammal family tree", 52), (160, 80), 0.1, 0.5)
    for i in range(20):
        r, q = divmod(i, 10)
        L = icon("bat", 46, "gold")
        if i >= 4:
            L = Layer(100, 100)
            L.ell((24, 24, 76, 76), "dim")
        c.add(L, (160 + q * 95, 300 + r * 140), 0.4 + i * 0.05, 0.3, "pop")
    big = Layer(700, 260)
    big.text((350, 130), p["value"], 190, "black", "gold")
    c.add(big, (1130, 260), 1.3, 0.6, "pop")
    lab = Layer(700, 200)
    lab.text((350, 50), "mammal species is a bat", 44, "semi", "cream")
    lab.text((350, 120), "1,400+ species · second only to rodents", 34, "med", "grey")
    c.add(lab, (1130, 560), 1.7, 0.5)
    add_tag(c, p.get("tag"))
    return c


def k_diets(p, dur):
    c = Card(bg=False)
    c.add(title_layer("What bats eat", 60), (160, 80), 0.1, 0.5)
    items = [("moth", "Insects", "most species", "cream"), ("fruit", "Fruit", "fruit bats", "coral"),
             ("flower", "Nectar & pollen", "nectar bats", "gold"), ("drop", "Blood", "only 3 species", "red")]
    for i, (ic, a, b, col) in enumerate(items):
        x = 160 + i * 410
        pn = Layer(360, 480)
        pn.rrect((0, 0, 360, 480), 34, "panel")
        c.add(pn, (x, 260), 0.3 + i * 0.35, 0.4, "up")
        c.add(icon(ic, 70, col), (x + 96, 300), 0.45 + i * 0.35, 0.4, "pop")
        t = Layer(360, 160)
        t.text((180, 50), a, 44, "black", "cream")
        t.text((180, 110), b, 32, "semi", "grey" if i < 3 else "coral")
        c.add(t, (x, 520), 0.6 + i * 0.35, 0.4, "up")
    add_tag(c, p.get("tag"))
    return c


def k_jobs(p, dur):
    c = Card(bg=False)
    c.add(title_layer("Three night jobs", 64), (160, 80), 0.1, 0.5)
    items = [("moth", "Pest control", "eating crop-damaging insects", "gold"),
             ("flower", "Pollination", "carrying pollen flower to flower", "coral"),
             ("tree", "Planting forests", "spreading seeds into clearings", "green")]
    for i, (ic, a, b, col) in enumerate(items):
        x = 170 + i * 545
        pn = Layer(500, 560)
        pn.rrect((0, 0, 500, 560), 36, "panel")
        pn.text((250, 60), str(i + 1), 56, "black", col)
        c.add(pn, (x, 240), 0.4 + i * 0.6, 0.4, "up")
        c.add(icon(ic, 80, col), (x + 154, 330), 0.6 + i * 0.6, 0.4, "pop")
        t = Layer(500, 170)
        t.text((250, 50), a, 50, "black", "cream")
        t.text((250, 115), b, 30, "med", "grey")
        c.add(t, (x, 600), 0.8 + i * 0.6, 0.4, "up")
    return c


def k_decline3(p, dur):
    c = Card(bg=False)
    c.add(title_layer("Three species fell more than 90% in under 10 years", 54), (160, 80), 0.1, 0.5)
    sp = ["Little brown bat", "Northern long-eared bat", "Tricolored bat"]
    for i, name in enumerate(sp):
        y = 270 + i * 210
        t = Layer(640, 90)
        t.text((0, 45), name, 44, "bold", "cream", anchor="lm")
        c.add(t, (160, y), 0.4 + i * 0.5, 0.4, "left")
        full = Layer(900, 64)
        full.rrect((0, 0, 900, 64), 16, "dim")
        c.add(full, (820, y + 12), 0.5 + i * 0.5, 0.4, "fade")
        rem = Layer(90, 64)
        rem.rrect((0, 0, 90, 64), 16, "gold")
        c.add(rem, (820, y + 12), 1.2 + i * 0.5, 0.5, "wipe")
        lab = Layer(260, 90)
        lab.text((130, 45), "> −90%", 54, "black", "coral")
        c.add(lab, (1500, y), 1.4 + i * 0.5, 0.4, "pop")
    n = Layer(1600, 60)
    n.text((800, 30), "Bar = population left, compared with before the fungus (USGS, 2021)", 30, "med", "grey")
    c.add(n, (160, 920), 2.4, 0.5)
    add_tag(c, p.get("tag"))
    return c


def k_spread(p, dur):
    c = Card(bg=False)
    L, pr = K.map_layer((-128, 24, -60, 54), 1500, 640, highlight=(), base_col="dim")
    c.add(L, (210, 230), 0.1, 0.6, "fade")
    c.add(title_layer("White-nose syndrome: first found in New York, 2006", 52), (160, 80), 0.1, 0.5)

    def dyn(im, t, pr=pr):
        k = max(0.0, min(1.0, (t - 0.6) / (dur * 0.75)))
        lay = Image.new("RGBA", (W * K.SS, H * K.SS), (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        x0, y0 = pr(-74.2, 42.7)
        rnd = __import__("random").Random(4)
        pts = []
        for i in range(260):
            ang = rnd.uniform(0, 2 * math.pi)
            r = abs(rnd.gauss(0, 1)) * 14 + rnd.uniform(0, 6)
            lon, lat = -74.2 + math.cos(ang) * r * 1.6, 42.7 + math.sin(ang) * r * 0.75
            if lon < -112 or lat < 27 or lat > 51:
                continue
            pts.append((r / 26.0, lon, lat))
        for rr, lon, lat in pts:
            if rr <= k:
                x, y = pr(lon, lat)
                a = int(150 * min(1.0, (k - rr) * 6 + 0.2))
                s = 22 * K.SS
                d.ellipse([(210 + x) * K.SS - s, (230 + y) * K.SS - s, (210 + x) * K.SS + s, (230 + y) * K.SS + s],
                          fill=K.rgba(C["coral"], a))
        lay = lay.filter(ImageFilter.GaussianBlur(6)).resize((W, H), Image.LANCZOS)
        im.alpha_composite(lay)
        dd = ImageDraw.Draw(im)
        dd.ellipse([210 + x0 - 12, 230 + y0 - 12, 210 + x0 + 12, 230 + y0 + 12], fill=K.rgba(C["gold"]))
        yr = 2006 + int(k * 19)
        dd.text((1580, 860), str(min(yr, 2025)), font=K.F("black", 90), fill=K.rgba(C["cream"]), anchor="mm")
    c.dyn.append(dyn)
    n = Layer(1600, 60)
    n.text((800, 30), "Schematic spread. Confirmed in 40+ US states and parts of Canada (USGS, 2025)", 30, "med", "grey")
    c.add(n, (160, 960), 1.0, 0.5)
    add_tag(c, p.get("tag"))
    return c


def k_paper(p, dur):
    c = Card(bg=False)
    pg = Layer(1180, 600)
    pg.rrect((0, 0, 1180, 600), 18, "#F3EEDF")
    who = p.get("who", "")
    journal = "SCIENCE · 2024" if "Science" in who else ("PROC. R. SOC. B · 2012" if "Proc" in who else "THE STUDY DESIGN")
    pg.text((60, 80), journal, 28, "bold", "#9A3B2A", anchor="lm")
    words = p["title"].split()
    lines, cur = [], ""
    for w_ in words:
        if K.F("black", 54).getlength(cur + " " + w_) > 1060:
            lines.append(cur)
            cur = w_
        else:
            cur = (cur + " " + w_).strip()
    lines.append(cur)
    for k, ln_ in enumerate(lines):
        pg.text((60, 180 + k * 68), ln_, 54, "black", "#2B2420", anchor="lm")
    pg.text((60, 520), who, 32, "bold", "#5A4E44", anchor="lm")
    for k in range(3):
        pg.rrect((60, 400 + k * 26, 60 + 1040 - k * 140, 410 + k * 26), 5, "#D9D1BE")
    c.add(pg, (370, 250), 0.3, 0.6, "up")
    if p.get("split"):
        for i, (lab, col) in enumerate((("Counties the fungus reached", "coral"), ("Similar counties not reached yet", "teal"))):
            L = Layer(760, 80)
            L.rrect((0, 0, 760, 80), 40, col)
            L.text((380, 40), lab, 34, "bold", "bg")
            c.add(L, (180 + i * 800, 890), 1.4 + i * 0.4, 0.4, "up")
    add_tag(c, p.get("tag"))
    return c


def k_quiet(p, dur):
    c = Card(bg=False)
    c.add(icon("heart", 80, "coral"), (864, 300), 0.3, 0.6, "pop")
    L = Layer(1600, 120)
    L.text((800, 60), p.get("main", ""), 80, "black", "cream")
    c.add(L, (160, 560), 0.6, 0.6, "up")
    return c


def k_compare(p, dur):
    c = Card(bg=False)
    c.add(title_layer("Infant deaths from internal causes, in affected counties", 52), (160, 80), 0.1, 0.5)
    (la, va), (lb, vb) = p["left"], p["right"]
    base_y = 820
    for i, (lab, val, col) in enumerate(((la, va, "grey"), (lb, vb, "coral"))):
        x = 560 + i * 520
        hgt = int(4.4 * val)
        bar = Layer(300, hgt)
        bar.rrect((0, 0, 300, hgt), 22, col)
        c.add(bar, (x, base_y - hgt), 0.5 + i * 0.8, 0.7, "up")
        t = Layer(520, 130)
        t.text((260, 40), lab, 36, "bold", "cream")
        c.add(t, (x - 110, base_y + 20), 0.6 + i * 0.8, 0.4, "up")
        v = Layer(400, 110)
        v.text((200, 55), "100" if i == 0 else "≈ +7.9%", 70, "black", "cream" if i == 0 else "coral")
        c.add(v, (x - 50, base_y - hgt - 120), 1.0 + i * 0.8, 0.4, "pop")
    n = Layer(1600, 60)
    n.text((800, 30), "Index: before the fungus = 100. Frank (2024), Science", 30, "med", "grey")
    c.add(n, (160, 970), 2.0, 0.5)
    add_tag(c, p.get("tag"))
    return c


def k_corn_compare(p, dur):
    c = Card(bg=False)
    c.add(title_layer("Corn netted at night, so bats couldn't feed (Illinois)", 52), (160, 80), 0.1, 0.5)
    for i, (lab, col) in enumerate((("Bats allowed", "green"), ("Bats kept out", "coral"))):
        x = 230 + i * 820
        pn = Layer(700, 600)
        pn.rrect((0, 0, 700, 600), 36, "panel")
        pn.text((350, 60), lab, 46, "black", col)
        c.add(pn, (x, 240), 0.3 + i * 0.5, 0.4, "up")
        c.add(icon("corn", 90, "gold"), (x + 30, 360), 0.5 + i * 0.5, 0.4, "pop")
        bugs = 5 if i == 0 else 8
        for k in range(bugs):
            c.add(icon("moth", 24, "cream"), (x + 300 + (k % 4) * 90, 380 + (k // 4) * 90), 0.9 + i * 0.6 + k * 0.08,
                  0.3, "pop")
        if i == 1:
            v = Layer(380, 200)
            v.text((190, 60), "+60%", 90, "black", "coral")
            v.text((190, 150), "earworms", 34, "bold", "cream")
            c.add(v, (x + 300, 600), 2.0, 0.4, "pop")
            v2 = Layer(330, 200)
            v2.text((165, 60), "+56%", 70, "black", "coral")
            v2.text((165, 130), "damaged kernels", 30, "bold", "cream")
            c.add(v2, (x + 20, 600), 2.6, 0.4, "pop")
    add_tag(c, p.get("tag"))
    return c


def k_range(p, dur):
    c = Card(bg=False)
    c.add(title_layer(p["label"], 56), (160, 80), 0.1, 0.5)
    x0, x1, y = 220, 1700, 520
    lo, mid, hi = p["lo"], p["mid"], p["hi"]
    sx = lambda v: x0 + (x1 - x0) * v / hi   # noqa: E731
    ax = Layer(x1 - x0 + 40, 40)
    ax.rrect((0, 10, x1 - x0 + 40, 30), 10, "dim")
    c.add(ax, (x0 - 20, y), 0.2, 0.5, "fade")
    band = Layer(int(sx(hi) - sx(lo)), 60)
    band.rrect((0, 0, int(sx(hi) - sx(lo)), 60), 30, "coral")
    c.add(band, (int(sx(lo)), y - 10), 0.7, 1.0, "wipe")
    for v, lab, t0 in ((lo, f"${lo:g} bn", 0.6), (mid, f"~${mid:g} bn", 1.4), (hi, f"${hi:g} bn", 1.8)):
        L = Layer(320, 200)
        L.ell((140, 0, 180, 40), "gold" if v == mid else "cream")
        L.text((160, 110), lab, 52 if v == mid else 42, "black", "gold" if v == mid else "cream")
        L.text((160, 170), {lo: "at least", mid: "central estimate", hi: "upper end"}[v], 28, "med", "grey")
        c.add(L, (int(sx(v)) - 160, y - 10), t0, 0.4, "pop")
    n = Layer(1600, 60)
    n.text((800, 30), "per year · Boyles et al. (2011), Science · a rough extrapolation", 30, "med", "grey")
    c.add(n, (160, 900), 2.2, 0.5)
    add_tag(c, p.get("tag"))
    return c


def k_menu(p, dur):
    c = Card(bg=False)
    c.add(title_layer("An insect-eating bat's menu (illustrative)", 56), (160, 80), 0.1, 0.5)
    plate = Layer(900, 620)
    plate.ell((0, 0, 900, 620), "#EDE6D6")
    plate.ell((60, 45, 840, 575), "#F7F2E6")
    c.add(plate, (510, 250), 0.3, 0.5, "pop")
    for k in range(6):
        a = k * 1.05
        c.add(icon("moth", 50, "#8A6A4A"), (int(860 + math.cos(a) * 200), int(480 + math.sin(a) * 140)),
              0.7 + k * 0.1, 0.3, "pop")
    for k in range(3):
        c.add(icon("beetle", 40, "#3A3A2A"), (int(800 + k * 120), 600), 1.3 + k * 0.1, 0.3, "pop")
    c.add(icon("mosquito", 26, "#5A5A5A"), (1270, 330), 1.9, 0.3, "pop")
    L = Layer(420, 300)
    L.text((210, 50), "Main course", 46, "black", "gold")
    L.text((210, 110), "moths · beetles", 34, "semi", "cream")
    L.text((210, 200), "Side dish", 40, "black", "grey")
    L.text((210, 255), "mosquitoes", 32, "semi", "grey")
    c.add(L, (1440, 360), 2.2, 0.5, "left")
    add_tag(c, p.get("tag"))
    return c


def k_cull_cycle(p, dur):
    c = Card(bg=False)
    c.add(title_layer("Why culling can backfire (a hypothesis)", 56), (160, 80), 0.1, 0.5)
    steps = [("bat", "Colony culled", "coral"), ("heart", "Immune adults removed", "grey"),
             ("bat", "More young bats with no immunity", "gold"), ("virus", "Virus can spread faster", "violet")]
    cx, cy, R = 960, 560, 300
    for i, (ic, lab, col) in enumerate(steps):
        a = -math.pi / 2 + i * math.pi / 2
        x, y = cx + math.cos(a) * R * 1.45, cy + math.sin(a) * R
        c.add(icon(ic, 46, col), (int(x - 55), int(y - 95)), 0.4 + i * 0.7, 0.4, "pop")
        L = Layer(560, 70)
        L.text((280, 35), lab, 34, "bold", "cream")
        c.add(L, (int(x - 280), int(y + 20)), 0.6 + i * 0.7, 0.4, "up")

    def dyn(im, t):
        k = max(0.0, min(1.0, (t - 0.6) / 3.0))
        d = ImageDraw.Draw(im)
        for i in range(4):
            if k * 4 < i + 0.2:
                break
            a0 = -math.pi / 2 + i * math.pi / 2 + 0.38
            a1 = a0 + math.pi / 2 - 0.76
            pts = [(cx + math.cos(a0 + (a1 - a0) * u / 20) * R * 1.45, cy + math.sin(a0 + (a1 - a0) * u / 20) * R)
                   for u in range(21)]
            d.line(pts, fill=K.rgba(C["dim"]), width=8)
    c.dyn.append(dyn)
    add_tag(c, p.get("tag"))
    return c


KINDS = {k[2:]: v for k, v in globals().items() if k.startswith("k_")}


def card(kind, params, dur, bg=None):
    cd = KINDS[kind](params, dur)
    cd.base = backdrop(bg)
    return cd.frame
