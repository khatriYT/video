"""Episode 3 v2 renderer: detailed static plates + animated character passes (+ two full-3D shots).

  blender -b --factory-startup -P tools/vulture3d/render3.py -- plate <KEY,KEY|all> <out_root> [--preview]
  blender -b --factory-startup -P tools/vulture3d/render3.py -- chars <ids e.g. 3,12> <out_root> [--preview]
  blender -b --factory-startup -P tools/vulture3d/render3.py -- full  <71,73> <out_root>

plates -> <out_root>/plates/<KEY>.png (2304x1296, 32 samples)
chars  -> <out_root>/chars/SC###/char_####.png (RGBA, alpha = character mask) + shadow_####.png + shadow_base
full   -> <out_root>/full/SC###/f_####.png
Character passes use the plate's camera, lights and terrain, so they composite exactly (compose3.py).
"""
import json
import math
import os
import random
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy  # noqa: E402
from mathutils import Euler, Vector  # noqa: E402

import envs2 as E  # noqa: E402
import lib as L  # noqa: E402
import rigs as R  # noqa: E402

ARGV = sys.argv[sys.argv.index("--") + 1:]
MODE, WANT, OUT = ARGV[0], ARGV[1], ARGV[2]
PREVIEW = "--preview" in ARGV
PROJ = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "01_PROJECTS", "what_if_vultures_disappeared")
FPS = 12

# ------------------------------------------------------------------ cameras
CAM = {
    "WIDE": dict(loc=(-1.5, -15.5, 3.4), target=(1.0, 4.0, 1.2), lens=30),
    "LOW": dict(loc=(4.6, -5.2, 1.1), target=(0.2, 0.2, 0.7), lens=42, dof="auto", fstop=4.0),
    "CU_DOG": dict(loc=(4.9, -6.2, 0.95), target=(2.1, -2.0, 0.65), lens=50, dof="auto", fstop=2.8),
    "PIP": dict(loc=(-0.6, -12.6, 1.7), target=(-3.4, -7.0, 1.7), lens=40, dof="auto", fstop=4.0),
    "WIDE_HIGH": dict(loc=(-3.0, -18.0, 4.5), target=(0.5, 4.0, 3.5), lens=28),
    "ROOST_WIDE": dict(loc=(3.0, -14.0, 2.6), target=(0.0, 0.0, 3.8), lens=38),
    "ROOST_UP": dict(loc=(2.0, -9.0, 0.6), target=(0.0, 0.0, 6.5), lens=24),
    "FALLEN": dict(loc=(3.9, -5.0, 2.7), target=(1.3, -1.5, 0.15), lens=42, dof="auto", fstop=4.0),
    "SKY_UP": dict(loc=(0, -10, 1.6), target=(0, 6, 22), lens=24),
    "SKY_HERO": dict(loc=(1.4, -3.6, -1.6), target=(0.0, 0.2, 0.6), lens=40),
    "SKY_HIGH": dict(loc=(1.4, -3.6, -1.6), target=(0.6, 0.6, 0.9), lens=40),
    "ROOM": dict(loc=(0.4, -4.2, 1.8), target=(0.0, 0.3, 1.45), lens=40, dof="auto", fstop=3.5),
    "STREET": dict(loc=(0.3, -6.5, 1.5), target=(0.0, 8.0, 1.4), lens=30),
    "YARD": dict(loc=(4.0, -3.5, 1.6), target=(0.4, 5.0, 1.3), lens=38),
    "TOWER": dict(loc=(14.0, -30.0, 6.0), target=(0.0, 5.0, 4.0), lens=40),
    "SAVANNA": dict(loc=(2.0, -15.0, 2.2), target=(0.0, 4.0, 3.6), lens=35),
}

# ------------------------------------------------------------------ plates
PLATES = {
    "DUMP_dawn": dict(env="dump", state="fresh", light="dawn", cam="WIDE"),
    "DUMP_morning_low": dict(env="dump", state="fresh", light="morning", cam="LOW"),
    "DUMP_morning_wide": dict(env="dump", state="fresh", light="morning", cam="WIDE"),
    "DUMP_noon_wide": dict(env="dump", state="fresh", light="noon_hot", cam="WIDE"),
    "DUMP_noon_low": dict(env="dump", state="fresh", light="noon_hot", cam="LOW"),
    "DUMP_day3": dict(env="dump", state="bloated", light="overcast", cam="WIDE", shadow_k=0.25),
    "DUMP_week2": dict(env="dump", state="bloated", light="golden", cam="WIDE"),
    "DUMP_dogcu": dict(env="dump", state="bloated", light="golden", cam="CU_DOG"),
    "DUMP_year1": dict(env="dump", state="year1", light="dusk", cam="WIDE", shadow_k=0.35),
    "DUMP_year10": dict(env="dump", state="year10", light="night", cam="WIDE", shadow_k=0.3),
    "DUMP_pip": dict(env="dump", state="fresh", light="morning", cam="PIP"),
    "DUMP_nepal": dict(env="dump", state="fresh", light="dawn", cam="WIDE_HIGH", green=True),
    "ROOST_wide": dict(env="roost", light="dawn", cam="ROOST_WIDE"),
    "ROOST_portrait": dict(env="roost", light="golden", cam="PORTRAIT"),
    "ROOST_head": dict(env="roost", light="golden", cam="HEAD"),
    "ROOST_up": dict(env="roost", light="day", cam="ROOST_UP"),
    "ROOST_fallen": dict(env="roost", light="overcast", cam="FALLEN", shadow_k=0.25),
    "SKY_up": dict(env="sky", light="morning", cam="SKY_UP"),
    "SKY_hero": dict(env="sky", light="day", cam="SKY_HERO"),
    "SKY_high": dict(env="sky_high", light="day", cam="SKY_HIGH"),
    "ROOM": dict(env="room", light="day", cam="ROOM"),
    "VILLAGE_street": dict(env="village", light="dusk", cam="STREET", shadow_k=0.35),
    "VILLAGE_yard": dict(env="village", light="morning", cam="YARD", cow=True),
    "TOWER_dawn": dict(env="tower", light="dawn", cam="TOWER"),
    "TOWER_monsoon": dict(env="tower", light="monsoon", cam="TOWER", mirrors=True, shadow_k=0.2),
    "SAVANNA_golden": dict(env="savanna", light="golden", cam="SAVANNA"),
    "SAVANNA_dusk": dict(env="savanna", light="dusk", cam="SAVANNA", shadow_k=0.35),
}

# ------------------------------------------------------------------ scenes: (kind, action, loc, rz, scale, seed, kw)
# loc may be "perch:i" (roost/dump dead tree perches) or "acacia:i"
V, D, C, PIP, VIL, COW = "vulture", "dog", "crow", "pip", "villager", "cow"


def ring(n, r0=1.5, r1=2.6, a0=20, a1=250, seed=0):
    rnd = random.Random(seed)
    out = []
    for i in range(n):
        a = math.radians(a0 + (a1 - a0) * i / max(1, n - 1)) + rnd.uniform(-0.15, 0.15)
        r = rnd.uniform(r0, r1)
        out.append((math.cos(a) * r, math.sin(a) * r, 0, math.atan2(-math.sin(a), -math.cos(a))))
    return out


def feeders(n, seed, rate=0.55):
    return [(V, "feed", (x, y, 0), rz, 1.0, seed * 10 + i, dict(rate=rate + 0.1 * (i % 3)))
            for i, (x, y, z, rz) in enumerate(ring(n, seed=seed))]


def circlers(n, center, r=(5, 10), z=(10, 18), seed=0, speed=0.3):
    rnd = random.Random(seed)
    out = []
    for i in range(n):
        out.append((V, "circle", center, 0, 1.0, seed * 7 + i,
                    dict(center=(center[0], center[1], rnd.uniform(*z)), radius=rnd.uniform(*r), phase=rnd.uniform(0, 6.3),
                         speed=speed * rnd.uniform(0.8, 1.2), cw=bool(i % 2), bank=0.35)))
    return out


def perched(n, seed, act="idle", start=0):
    return [(V, act, f"perch:{start + i}", (-0.45 if i == 0 else 1.6 + i * 0.9), 1.0, seed + i, {}) for i in range(n)]


def landers(n, seed, delay0=0.3, gap=1.6, dur=2.4, then="feed"):
    out = []
    for i, (x, y, z, rz) in enumerate(ring(n, r0=1.8, r1=2.8, a0=60, a1=230, seed=seed + 5)):
        st = (x - math.cos(rz) * 7, y - math.sin(rz) * 7, 6 + i)
        out.append((V, "land", (x, y, 0), rz, 1.0, seed + i,
                    dict(start=st, dur=dur, then=then, schedule=[(0, "hidden"), (delay0 + gap * i, "land")])))
    return out


def dogs(spec, seed=0):
    return [(D, a, (x, y, 0), rz, 1.1, seed + i, dict(kw, coat=coat) if (kw := extra) is not None else {})
            for i, (a, x, y, rz, coat, extra) in enumerate(spec)]


TAN, DARK, PALE, GREY = ("#C99A5E", "#A87A44"), ("#7A5638", "#5E4029"), ("#DDC49A", "#C2A67A"), ("#8E8780", "#6F6861")

SCENES = {
    1: dict(plate="DUMP_dawn", actors=circlers(3, (0, 10, 0), seed=1) + perched(2, 1) +
            [(C, "hop", (2.6, -1.4, 0), 2.0, 1.2, 3, {})]),
    2: dict(plate="SKY_up", actors=circlers(9, (0, 8, 0), r=(3, 11), z=(16, 32), seed=2, speed=0.35)),
    3: dict(plate="DUMP_morning_low", actors=feeders(6, 3) + [(V, "display", (-1.2, 2.6, 0), -0.6, 1.0, 9, {})] +
            landers(1, 30, delay0=1.0)),
    4: dict(plate="ROOST_wide", actors=perched(6, 4) + [(V, "display", "perch:6", 1.2, 1.0, 40, {})] +
            circlers(2, (0, 6, 0), r=(6, 9), z=(9, 13), seed=4)),
    6: dict(plate="DUMP_noon_wide", actors=[(C, "peck", (0.6, -0.4, 0.62), 2.4, 1.2, 1, {}),
                                            (C, "hop", (-1.8, -1.0, 0), 0.6, 1.2, 2, {})]),
    7: dict(plate="ROOST_up", actors=[(C, "fly", (-14, 4, 12), 0, 1.4, 1, dict(vel=(3.2, 0.3, 0))),
                                      (C, "fly", (-18, 7, 14), 0, 1.4, 2, dict(vel=(3.0, 0.2, 0.1)))]),
    8: dict(plate="DUMP_pip", actors=[(PIP, "wave", (-3.4, -7.0, 0), 0.55, 1.0, 1,
                                       dict(schedule=[(0, "wave"), (2.6, "talk")]))]),
    9: dict(plate="ROOST_portrait", actors=perched(1, 9)),
    10: dict(plate="SKY_hero", actors=[(V, "circle", (0, 0.2, 0), 0, 1.0, 10,
                                        dict(center=(-0.7, 2.1, 1.75), radius=1.1, speed=0.24, phase=-1.4, bank=0.3))]),
    12: dict(plate="DUMP_morning_wide", actors=feeders(4, 12) + landers(5, 120, delay0=0.2, gap=1.7) +
             circlers(3, (0, 6, 0), seed=12)),
    13: dict(plate="SKY_high", actors=[(V, "glide", (-1.6, 0.3, 0.4), 0, 1.0, 13, dict(vel=(0.35, 0.05, 0.02)))]),
    14: dict(plate="ROOST_head", actors=perched(1, 14)),
    16: dict(plate="DUMP_morning_low", actors=feeders(7, 16, rate=0.7)),
    17: dict(plate="ROOST_wide", actors=perched(5, 17) + [(V, "land", "perch:5", 1.4, 1.0, 171,
                                                            dict(start=(-8, -4, 9), dur=2.8, then="idle"))]),
    18: dict(plate="ROOST_fallen", actors=[(V, "fallen", (1.2, -1.6, 0), math.radians(210), 1.0, 18, {}),
                                          (V, "fallen", (-1.6, 0.8, 0), math.radians(40), 1.0, 19, {}),
                                          (C, "hop", (3.0, -0.4, 0), 2.6, 1.2, 1, {})]),
    21: dict(plate="ROOM", actors=[(PIP, "point", (0.0, 0.9, 0), 0.0, 1.0, 21, {})]),
    22: dict(plate="VILLAGE_yard", actors=[(COW, "idle", (0.5, 5.0, 0), -2.4, 1.0, 22, {}),
                                          (VIL, "talk", (-1.8, 4.0, 0), -0.6, 0.85, 23,
                                           dict(skin="#B27A50", shirt="#C0563A", pants="#3E4A63"))]),
    24: dict(plate="ROOST_fallen", actors=[(V, "fallen", (1.2, -1.6, 0), math.radians(210), 1.0, 18, {}),
                                          (V, "fallen", (-1.6, 0.8, 0), math.radians(40), 1.0, 19, {}),
                                          (C, "peck", (-0.6, -1.4, 0), 1.0, 1.2, 4, {})]),
    28: dict(plate="ROOST_up", actors=[(C, "fly", (-16, 6, 13), 0, 1.4, 5, dict(vel=(3.4, 0.2, 0)))]),
    29: dict(plate="DUMP_noon_wide", actors=[(PIP, "walk", (-6.5, -5.0, 0), 0, 1.0, 29, dict(vel=(0.55, 0.15, 0),
                                                                                           schedule=[(0, "walk"), (5.0, "look_up")])),
                                            (C, "peck", (0.6, -0.4, 0.62), 2.4, 1.2, 6, {})]),
    30: dict(plate="DUMP_noon_low", actors=[(C, "peck", (0.6, -0.4, 0.62), 2.4, 1.2, 1, {}),
                                           (C, "hop", (-1.4, -1.0, 0), 0.6, 1.2, 2, {}),
                                           (C, "peck", (1.8, -1.2, 0), 2.0, 1.2, 3, {})]),
    31: dict(plate="DUMP_day3", actors=[(C, "peck", (0.6, -0.4, 0.7), 2.4, 1.2, 1, {}),
                                       (C, "hop", (-1.6, -0.9, 0), 0.6, 1.2, 2, {}),
                                       (C, "peck", (2.2, 0.2, 0), 3.4, 1.2, 3, {}),
                                       (C, "hop", (-0.8, 1.4, 0), 5.0, 1.2, 4, {})]),
    34: dict(plate="DUMP_dogcu", actors=dogs([("bark", 2.1, -2.0, -0.55, TAN, {}),
                                              ("tug", 1.5, -0.8, 1.6, DARK, {})], 34)),
    35: dict(plate="DUMP_week2", actors=dogs([("tug", 1.9, -0.9, 2.6, TAN, {}), ("tug", -1.9, -0.5, 0.2, DARK, {}),
                                              ("sniff_walk", 3.5, 2.0, 3.6, PALE, dict(vel=(-0.25, -0.15, 0))),
                                              ("walk", -9.0, 6.0, -0.5, TAN, dict(vel=(0.85, -0.6, 0)))], 35)),
    36: dict(plate="DUMP_year1", actors=dogs([("tug", 1.9, -0.9, 2.6, TAN, {}), ("tug", -1.9, -0.5, 0.2, DARK, {}),
                                              ("sniff", 1.0, 1.7, 4.4, PALE, {}), ("walk", -8, 4, -0.4, TAN, dict(vel=(0.9, -0.5, 0))),
                                              ("sniff", 4.0, 1.0, 2.4, DARK, {}), ("idle", 6.2, 3.8, 3.8, PALE, {}),
                                              ("sit", -4.2, 2.6, 5.5, TAN, {}),
                                              ("walk", 7, -3, 2.8, GREY, dict(vel=(-0.8, 0.3, 0))),
                                              ("idle", -3.8, -2.8, 0.9, DARK, {})], 36)),
    38: dict(plate="VILLAGE_street", actors=dogs([("walk", 0.5, 0.0, 0, TAN, dict(vel=(0.0, 0.9, 0))),
                                                  ("sniff", -1.5, 6.5, -0.4, DARK, {}),
                                                  ("walk", 1.8, 10.5, 0, PALE, dict(vel=(-0.2, -0.8, 0))),
                                                  ("sit", -0.5, 11.0, 1.0, TAN, {}),
                                                  ("trot", 2.6, 3.0, 0, GREY, dict(vel=(-0.3, 1.2, 0)))], 38) +
            [(VIL, "walk", (-3.4, 12.5, 0), 0, 0.75, 1, dict(vel=(0.2, -0.5, 0), skin="#8D5A3B", shirt="#B3473A")),
             (VIL, "idle", (3.4, 14.0, 0), 0.4, 0.75, 2, dict(skin="#C68B5E", shirt="#3F6EA8"))]),
    40: dict(plate="DUMP_year10", actors=dogs([("sniff", 1.4, -1.0, 3.3, TAN, {}), ("idle", -2.3, -0.6, 0.2, DARK, {}),
                                               ("sit", 1.0, 1.7, 4.4, PALE, {}), ("walk", -6, -3, 0.5, TAN, dict(vel=(0.7, 0.3, 0))),
                                               ("sniff", 4.0, 1.0, 2.4, GREY, {}), ("idle", 6.2, 3.8, 3.8, TAN, {}),
                                               ("sit", -4.2, 2.6, 5.5, DARK, {}), ("walk", 6, -2, 2.8, PALE, dict(vel=(-0.7, 0.2, 0))),
                                               ("sniff", -3.8, -2.8, 0.9, TAN, {}), ("idle", -6.0, 4.5, 0.4, GREY, {}),
                                               ("walk", 2.0, 8.0, 4.0, DARK, dict(vel=(-0.5, -0.6, 0))),
                                               ("bark", 7.5, 0.5, 2.8, TAN, {})], 40)),
    47: dict(plate="TOWER_dawn", actors=[(C, "fly", (-14, -6, 9), 0, 2.0, 7, dict(vel=(3.0, 0.8, 0)))]),
    48: dict(plate="TOWER_dawn", actors=circlers(4, (0, 6, 0), r=(5, 9), z=(10, 15), seed=48, speed=0.3)),
    49: dict(plate="TOWER_monsoon", actors=[]),
    53: dict(plate="SAVANNA_golden", actors=[(V, "idle", f"acacia:{i}", 1.2 + i * 1.3, 1.0, 53 + i, {}) for i in range(5)] +
             circlers(3, (0, 10, 0), r=(5, 9), z=(9, 13), seed=53)),
    55: dict(plate="SAVANNA_dusk", actors=dogs([("sniff_walk", -7, -1, 0, GREY, dict(vel=(0.6, 0.1, 0)))], 55)),
    58: dict(plate="DUMP_pip", actors=[(PIP, "shrug", (-3.4, -7.0, 0), 0.55, 1.0, 58, dict(talk=True))]),
    61: dict(plate="DUMP_year1", actors=dogs([("tug", 1.9, -0.9, 2.6, TAN, {}), ("tug", -1.9, -0.5, 0.2, DARK, {}),
                                              ("sniff", 1.0, 1.7, 4.4, PALE, {}), ("walk", 7, -2, 2.8, GREY, dict(vel=(-0.8, 0.25, 0))),
                                              ("idle", 6.2, 3.8, 3.8, PALE, {}), ("sit", -4.2, 2.6, 5.5, TAN, {})], 61)),
    63: dict(plate="DUMP_nepal", actors=circlers(5, (0, 4, 0), r=(4, 8), z=(6, 12), seed=63) +
             [(PIP, "look_up", (-5.5, -6.5, 0), 0.3, 1.0, 63, {})]),
    66: dict(plate="DUMP_nepal", actors=feeders(3, 66) + landers(3, 660, delay0=0.5, gap=2.6, dur=2.6) +
             circlers(2, (0, 4, 0), r=(5, 8), z=(8, 12), seed=66) +
             [(PIP, "binoculars", (-5.5, -6.5, 0), 0.3, 1.0, 66, {})]),
    67: dict(plate="ROOST_wide", actors=perched(4, 67) + [(V, "land", "perch:4", 1.4, 1.0, 671,
                                                           dict(start=(9, -5, 10), dur=3.0, then="idle")),
                                                          (V, "land", "perch:5", 2.4, 1.0, 672,
                                                           dict(start=(-9, -3, 11), dur=3.0, then="idle",
                                                                schedule=[(0, "hidden"), (2.5, "land")]))]),
    68: dict(plate="ROOST_up", actors=[(V, "circle", (0, 8, 0), 0, 1.0, 68,
                                        dict(center=(2, 10, 30), radius=6, speed=0.25, bank=0.35))]),
    69: dict(plate="DUMP_dawn", actors=circlers(4, (0, 6, 0), r=(4, 8), z=(6, 12), seed=69) + perched(2, 69)),
    70: dict(plate="DUMP_morning_low", actors=feeders(7, 70, rate=0.6)),
    72: dict(plate="ROOST_portrait", actors=perched(1, 72)),
    74: dict(plate="DUMP_pip", actors=[(PIP, "talk", (-3.4, -7.0, 0), 0.55, 1.0, 74,
                                        dict(schedule=[(0, "talk"), (6.5, "wave")]))]),
}
FULL = {
    71: dict(plate="ROOST_wide", light="golden", actors=perched(7, 710), camera="orbit"),
}
SCENES[73] = dict(plate="DUMP_nepal", actors=feeders(4, 73) + landers(2, 730, delay0=0.6, gap=2.4) +
                  circlers(5, (0, 4, 0), r=(4, 9), z=(6, 13), seed=73) +
                  [(PIP, "look_up", (-5.5, -6.5, 0), 0.3, 1.0, 73, {})])


# ------------------------------------------------------------------ environment builders
def build_env(pk, full):
    """full=True: complete detailed plate. full=False: only what the character pass needs
    (terrain, occluders, perch trees). Returns dict(perches=..., acacia=...)."""
    p = PLATES[pk]
    env, info = p["env"], dict(perches=[], acacia=[])
    if env not in ("sky", "sky_high", "room"):
        info["haze"] = L.world(p["light"], clouds=0.0 if p["light"] in ("night", "overcast", "monsoon") else 0.4,
                               stars=p["light"] == "night")
    if env == "dump":
        pal = dict(green_amt=0.35, green="#8FB25A") if p.get("green") else {}
        E.ground2(palette=pal)
        st = p["state"]
        if st in ("fresh",):
            E.carcass("fresh")
        elif st in ("bloated", "year1"):
            E.carcass("bloated")
        if st in ("year1", "year10"):
            E.bones2((5.0, 2.5, 0), 1.2, 1.0, seed=4)
        if st == "year10":
            E.bones2((0, 0, 0), 0.35, 1.1, seed=1)
            E.bones2((-4.5, 3.5, 0), -0.6, 0.9, seed=7)
            E.bones2((2.5, 7.5, 0), 2.2, 0.9, seed=9)
        _, info["perches"] = E.tree2("dead", (-7.5, 7.0, 0), 1.25, seed=4)
        if full:
            for (x, y, s, sd) in ((10, 14, 1.5, 2), (-16, 20, 1.7, 3), (22, 30, 1.6, 5), (-30, 38, 1.9, 6), (-22, 8, 1.4, 8),
                                  (30, 12, 1.5, 9)):
                E.tree2("neem", (x, y, 0), s, seed=sd)
            lit = p["light"] in ("night", "dusk")
            houses = [(4, 34, 0.2, "#D9B98C", "#A65E3A", "flat"), (8.5, 36, -0.1, "#C9A27A", "#8C4A30", "tile"),
                      (13, 33, 0.05, "#B9C3C0", "#6C7F86", "flat"), (-2, 37, 0.15, "#E1C79D", "#A65E3A", "tile"),
                      (17, 38, -0.2, "#D7A58A", "#9A5A40", "flat"), (-7, 35, 0.0, "#CBB89A", "#7E5A3A", "flat"),
                      (21, 35, 0.1, "#E3CFA8", "#A65E3A", "tile"), (-12, 38, 0.1, "#BFCFC4", "#5E7A6E", "flat")]
            for i, (x, y, r, w, t, roof) in enumerate(houses):
                E.house2((x, y, 0), r, wall=w, trim=t, roof=roof, seed=i, lit=lit)
                if lit:
                    L.point_light((x + 0.35, y - 2.2, 1.7), energy=500 if p["light"] == "night" else 150, radius=0.5)
            E.haystack((-4.5, 30), 1.0)
            E.haystack((25, 31), 1.2)
            E.treeline(95)
            for k in range(5):
                L.hill(L.P(), (-150 + k * 75, 190, -6), (55, 28, 20), color="#8E9C70")
            E.scatter_detail(((-30, 30), (-16, 32)), avoid=[(0, 0, 4.2), (-7.5, 7, 0.8), (5, 2.5, 1.8), (3.4, -3.8, 2.6),
                                                          (-3.4, -7.0, 1.6), (2.1, -2.0, 1.6), (-5.5, -6.5, 1.6),
                                                          (-4.2, 2.6, 1.2), (6.2, 3.8, 1.2), (-2.3, -2.6, 1.6)],
                             seed=3, green=0.5 if p.get("green") else 0.2)
    elif env == "roost":
        E.ground2(palette=dict(base="#C2A576", soil="#9C7B53"), path=False)
        _, info["perches"] = E.tree2("dead", (0, 0, 0), 1.6, seed=4)
        if full:
            E.tree2("neem", (-9, 10, 0), 1.6, seed=2)
            E.tree2("neem", (14, 22, 0), 1.8, seed=8)
            E.tree2("neem", (-20, 26, 0), 1.7, seed=11)
            E.treeline(80)
            for k in range(4):
                L.hill(L.P(), (-110 + k * 75, 160, -6), (55, 28, 18), color="#8E9C70")
            E.scatter_detail(((-22, 22), (-12, 28)), avoid=[(0, 0, 1.0)], seed=5, n_tuft=1200)
            if pk == "ROOST_fallen":
                rnd = random.Random(2)
                for i in range(10):
                    L.prim("sphere", "feather", (rnd.uniform(-2, 3), rnd.uniform(-3, 1), 0.03), (0.12, 0.03, 0.006),
                           rot=(0, 0, rnd.uniform(0, 6)), m=R.M2()["v_sec"])
    elif env in ("sky", "sky_high"):
        info["haze"] = L.world(p["light"], clouds=0.6)
        if env == "sky_high":
            w = bpy.context.scene.world.node_tree
            ramp = [n for n in w.nodes if n.type == "VALTORGB"][0]
            ramp.color_ramp.elements[0].color = (*L.hex_lin("#9FBCE0"), 1)
            ramp.color_ramp.elements[1].color = (*L.hex_lin("#0E2A63"), 1)
            if full:
                E.airliner((14, 70, 30), math.radians(-20), 3.0)
    elif env == "room":
        info["haze"] = L.world("day", clouds=0.0)
        wall = L.mat("plaster2", "#E9DDC4", 0.95, noise=("#D8C8A8", 0.6), noise_scale=3)
        floor = L.mat("floor2", "#B98E5E", 0.8, noise=("#A27A4E", 0.6), noise_scale=2)
        L.prim("cube", "floor", (0, 0, -0.05), (10, 8, 0.1), m=floor)
        L.prim("cube", "wall", (0, 2.2, 2.0), (10, 0.1, 4.2), m=wall)
        L.prim("cube", "table", (0, 0, 0.88), (2.4, 1.1, 0.08), m=L.mat("wood", "#8B6240", 0.75, noise=("#77522F", 0.6),
                                                                       noise_scale=4))
        for sx in (-1, 1):
            for sy in (-1, 1):
                L.prim("cube", "tleg", (sx * 1.1, sy * 0.45, 0.42), (0.08, 0.08, 0.84), m=L.mat("wood", "#8B6240"))
        if full:
            win = L.mat("window2", "#FFF2D8", 0.5, emit=3.5)
            L.prim("cube", "window", (1.8, 2.14, 2.2), (1.6, 0.02, 1.3), m=win)
            shelf = L.mat("shelf", "#7A5534", 0.8)
            L.prim("cube", "shelf", (-1.6, 2.05, 2.2), (2.0, 0.25, 0.06), m=shelf)
            rnd = random.Random(4)
            for k in range(6):
                c = rnd.choice(["#C0563A", "#3F6EA8", "#E8E2D4", "#5C9E5B", "#F2B33D"])
                L.prim("cyl", "jar", (-2.4 + k * 0.3, 2.05, 2.35), (0.09, 0.09, 0.24), m=L.mat("jar" + c, c, 0.5), seg=12)
            L.vial(L.P(), (-0.3, -0.2, 0.92), "red", 0.22)
            L.vial(L.P(), (0.0, -0.25, 0.92), "green", 0.22)
            L.vial(L.P(), (0.3, -0.15, 0.92), "red", 0.22)
            L.prim("cube", "box", (0.75, 0.0, 1.0), (0.35, 0.25, 0.18), m=L.mat("box", "#E9DCC0", 0.8))
        ld = bpy.data.lights.new("AREA", "AREA")
        ld.energy = 600
        ld.size = 3
        ld.color = L.hex_lin("#FFE9C8")
        a = L.link(bpy.data.objects.new("AREA", ld))
        a.location = (2.2, -1.5, 3.4)
        a.rotation_euler = (math.radians(35), math.radians(25), 0)
    elif env == "village":
        E.ground2(palette=dict(base="#C4A57A", soil="#A68960", grass="#B9A46A", green_amt=0.05), path=False)
        lit = p["light"] in ("dusk", "night")
        xs = [(-6.5, 0), (-6.5, 4.5), (-6.5, 9), (-6.5, 14), (6.5, 1), (6.5, 6), (6.5, 11), (6.5, 16)]
        cols = [("#D9B98C", "#A65E3A"), ("#B9C3C0", "#6C7F86"), ("#E1C79D", "#A65E3A"), ("#C9A27A", "#8C4A30"),
                ("#D7A58A", "#9A5A40"), ("#E3CFA8", "#A65E3A"), ("#CBB89A", "#7E5A3A"), ("#BFCFC4", "#5E7A6E")]
        if full:
            for i, ((x, y), (w, t)) in enumerate(zip(xs, cols)):
                E.house2((x, y, 0), math.pi / 2 if x < 0 else -math.pi / 2, w=3.6, d=3.2, h=2.7, wall=w, trim=t,
                         roof="flat" if i % 2 else "tile", seed=10 + i, lit=lit)
            E.tree2("neem", (-3.0, 20, 0), 1.6, seed=9)
            E.scatter_detail(((-4.6, -3.3), (-4, 20)), seed=8, n_tuft=70, n_flower=10, n_shrub=0, n_rock=10)
            E.scatter_detail(((3.3, 4.6), (-4, 20)), seed=9, n_tuft=70, n_flower=10, n_shrub=0, n_rock=10)
            E.scatter_detail(((-3.3, 3.3), (-4, 20)), seed=10, n_tuft=0, n_flower=0, n_shrub=0, n_rock=25)
        if lit:
            for (x, y) in xs[:6]:
                L.point_light((x * 0.72, y - 0.5, 2.1), energy=110, radius=0.3)
    elif env == "tower":
        E.ground2(palette=dict(base="#9AA466", soil="#7E8A50", grass="#A5AD6A", green_amt=0.4), path=False)
        L.hill(L.P(), (0, 6, -9.5), (24, 22, 11), color="#7E8D52")
        if full:
            L.tower(L.P(), (0, 6, 1.2), 1.0, mirrors=p.get("mirrors", False))
            for i, (x, y, s) in enumerate([(-12, 0, 1.8), (-16, 12, 2.0), (12, 2, 1.7), (15, 14, 2.1), (-6, 20, 2.2),
                                           (8, 22, 2.0), (-20, 4, 1.9), (20, 6, 2.0), (-26, 16, 2.0), (26, 18, 2.1)]):
                E.tree2("neem", (x, y, 0), s, seed=20 + i)
            city = L.mat("city", "#9AA3AC", 0.9)
            rnd = random.Random(3)
            for i in range(50):
                h = rnd.uniform(8, 38)
                L.prim("cube", "bldg", (-150 + i * 6 + rnd.uniform(-2, 2), 170 + rnd.uniform(-10, 10), h / 2),
                       (rnd.uniform(4, 7), rnd.uniform(4, 7), h), m=city)
            E.scatter_detail(((-30, 30), (-28, -8)), seed=12, n_tuft=600, n_flower=80, n_shrub=10, green=0.6)
    elif env == "savanna":
        E.ground2(palette=dict(base="#CDAE70", soil="#B08E55", grass="#D4BC72", green_amt=0.02), path=False)
        _, info["acacia"] = E.tree2("acacia", (0, 4, 0), 1.6, seed=12)
        if full:
            for i, (x, y, s) in enumerate([(-22, 30, 1.4), (26, 40, 1.6), (-45, 60, 1.8), (50, 70, 1.5), (-60, 90, 1.6)]):
                E.tree2("acacia", (x, y, 0), s, seed=30 + i)
            for k in range(4):
                L.hill(L.P(), (-160 + k * 100, 240, -8), (75, 32, 18), color="#9AA083")
            E.scatter_detail(((-28, 28), (-14, 34)), avoid=[(0, 4, 0.8)], seed=6, n_tuft=1800, n_flower=60, n_shrub=12,
                             green=0.0)
    return info


def setup_camera(pk, info):
    p = PLATES[pk]
    c = p["cam"]
    if c in ("PORTRAIT", "HEAD"):
        per = Vector(info["perches"][0])
        rz = -0.45
        head = per + Vector((0.46 * math.cos(rz), 0.46 * math.sin(rz), 1.1 - 0.05))
        fwd = Vector((math.cos(rz), math.sin(rz), 0))
        side = Vector((-math.sin(rz), math.cos(rz), 0))
        if c == "PORTRAIT":   # head and upper body, 3/4 front
            return L.camera(tuple(head + fwd * 3.0 - side * 1.3 + Vector((0, 0, -0.2))),
                            tuple(head - side * 0.5 + Vector((0, 0, -0.18))), lens=50, dof_dist="auto", fstop=2.2)
        return L.camera(tuple(head + fwd * 1.25 - side * 0.9 + Vector((0, 0, 0.05))), tuple(head + Vector((0.05, 0, -0.03))),
                        lens=85, dof_dist="auto", fstop=2.2)
    d = CAM[c]
    return L.camera(d["loc"], d["target"], lens=d["lens"], dof_dist=d.get("dof"), fstop=d.get("fstop", 2.8))


# ------------------------------------------------------------------ actors
def build_actors(spec, info):
    M2 = R.M2()
    actors = []
    for i, (kind, act, loc, rz, sc, seed, kw) in enumerate(spec):
        kw = dict(kw)
        if isinstance(loc, str):
            src, idx = loc.split(":")
            pts = info["perches"] if src == "perch" else info["acacia"]
            loc = tuple(Vector(pts[int(idx) % len(pts)]) + Vector((0, 0, -0.02)))
        extra = {k: kw.pop(k) for k in ("coat", "skin", "shirt", "pants", "hair") if k in kw}
        P = R.build(M2, kind, f"{kind}{i}", seed=seed, **extra)
        actors.append(R.Actor(P, act, loc, rz, sc, seed=seed, **kw))
    return actors


def set_handler(actors, hide_frame0=True):
    bpy.app.handlers.frame_change_pre.clear()

    def h(scene, *a):
        f = scene.frame_current
        t = max(0, f - 1) / FPS
        for A in actors:
            if f == 0 and hide_frame0:
                A.P.root.scale = (1e-4,) * 3
            else:
                A.update(t)
    bpy.app.handlers.frame_change_pre.append(h)


def scene_frames(sid):
    timing = json.load(open(os.path.join(PROJ, "09_Animation", "scene_timing.json")))
    return int(math.ceil(timing[f"SC{sid:03d}"]["duration"] * FPS)) + 1


def char_compositor(outdir, haze, haze_amt=0.5):
    sc = bpy.context.scene
    vl = sc.view_layers[0]
    vl.use_pass_shadow = True
    vl.use_pass_mist = True
    if "mask" not in [a.name for a in vl.aovs]:
        a = vl.aovs.add()
        a.name = "mask"
        a.type = "VALUE"
    sc.render.film_transparent = False
    sc.use_nodes = True
    nt = sc.node_tree
    nt.nodes.clear()
    rl = nt.nodes.new("CompositorNodeRLayers")
    mix = nt.nodes.new("CompositorNodeMixRGB")
    mix.inputs[2].default_value = (*L.hex_lin(haze), 1)
    mul = nt.nodes.new("CompositorNodeMath")
    mul.operation = "MULTIPLY"
    mul.inputs[1].default_value = haze_amt
    nt.links.new(rl.outputs["Mist"], mul.inputs[0])
    nt.links.new(mul.outputs[0], mix.inputs[0])
    nt.links.new(rl.outputs["Image"], mix.inputs[1])
    sa = nt.nodes.new("CompositorNodeSetAlpha")
    nt.links.new(rl.outputs["Image"] if os.environ.get("HAZE", "0") != "1" else mix.outputs[0], sa.inputs["Image"])
    nt.links.new(rl.outputs["mask"], sa.inputs["Alpha"])
    fo = nt.nodes.new("CompositorNodeOutputFile")
    fo.base_path = outdir
    fo.format.file_format = "PNG"
    fo.format.color_mode = "RGBA"
    fo.file_slots.clear()
    fo.file_slots.new("char_")
    fo.file_slots.new("shadow_")
    nt.links.new(sa.outputs[0], fo.inputs[0])
    nt.links.new(rl.outputs["Shadow"], fo.inputs[1])
    comp = nt.nodes.new("CompositorNodeComposite")
    nt.links.new(rl.outputs["Image"], comp.inputs[0])


# ------------------------------------------------------------------ modes
def do_plate(pk):
    t0 = time.time()
    L.reset()
    R.reset_caches()
    E._MESH.clear()
    info = build_env(pk, full=True)
    setup_camera(pk, info)
    res, smp = ((960, 540), 8) if PREVIEW else ((2304, 1296), int(os.environ.get("PLATE_SAMPLES", "16")))
    if not PREVIEW and os.path.exists(os.path.join(OUT, "plates", pk + ".png")) and os.environ.get("SKIP", "1") == "1":
        print(f"PLATE {pk} exists, skipped", flush=True)
        return
    p = PLATES[pk]
    mist = (40, 400) if p["env"] in ("sky", "sky_high") else ((40, 200) if p["env"] == "room" else (18, 170))
    L.render_setup(res, smp, haze=info.get("haze", "#D0DCE4"), mist=mist, haze_amt=0.45)
    d = os.path.join(OUT, "plates")
    os.makedirs(d, exist_ok=True)
    bpy.context.scene.render.filepath = os.path.join(d, pk + (".preview.png" if PREVIEW else ".png"))
    bpy.ops.render.render(write_still=True)
    json.dump(dict(plate=pk, **{k: v for k, v in PLATES[pk].items()}, resolution=res, samples=smp,
                   seconds=round(time.time() - t0, 1)), open(os.path.join(d, pk + "_settings.json"), "w"), indent=1)
    print(f"PLATE {pk} {time.time() - t0:.1f}s", flush=True)


def do_chars(sid):
    t0 = time.time()
    spec = SCENES[sid]
    pk = spec["plate"]
    L.reset()
    R.reset_caches()
    E._MESH.clear()
    info = build_env(pk, full=False)
    # cheap stand-in shading for everything that is not a character: it only has to occlude and receive shadows
    cheap = L.mat("charpass_cheap", "#B0A890", 0.9)
    for ob in list(bpy.data.objects):
        if ob.type == "MESH":
            ob.data.materials.clear()
            ob.data.materials.append(cheap)
    p_ = PLATES[pk]
    if p_["env"] not in ("sky", "sky_high", "room"):
        info["haze"] = L.world(p_["light"], clouds=0.0, stars=False)
        for o in [o for o in bpy.data.objects if o.type == "LIGHT" and o.name.startswith(("SUN.", "FILL."))]:
            bpy.data.objects.remove(o)
    else:
        L.world(p_["light"] if p_["env"] != "room" else "day", clouds=0.0)
        if p_["env"] != "room":
            for o in [o for o in bpy.data.objects if o.type == "LIGHT" and o.name.startswith(("SUN.", "FILL."))]:
                bpy.data.objects.remove(o)
    setup_camera(pk, info)
    actors = build_actors(spec["actors"], info)
    n = scene_frames(sid)
    p = PLATES[pk]
    mist = (40, 400) if p["env"] in ("sky", "sky_high") else ((40, 200) if p["env"] == "room" else (18, 170))
    close = PLATES[pk]["cam"] in ("LOW", "CU_DOG", "PIP", "PORTRAIT", "HEAD", "ROOM", "SKY_HERO", "SKY_HIGH", "FALLEN",
                                  "YARD")
    dflt = "1600x900" if close else "1280x720"
    res, smp = ((960, 540), 4) if PREVIEW else (tuple(int(x) for x in os.environ.get("RES", dflt).split("x")), 4)
    L.render_setup(res, smp, haze=info.get("haze", "#D0DCE4"), mist=mist, haze_amt=0.45)
    d = os.path.join(OUT, "chars", f"SC{sid:03d}")
    os.makedirs(d, exist_ok=True)
    char_compositor(d + "/", info.get("haze", "#D0DCE4"), 0.45)
    sc = bpy.context.scene
    sc.render.fps = FPS
    sc.render.filepath = os.path.join(d, "_combined_")
    set_handler(actors)
    if actors and os.environ.get("BORDER", "1") == "1":
        from bpy_extras.object_utils import world_to_camera_view
        cam = sc.camera
        sun = next((o for o in bpy.data.objects if o.type == "LIGHT" and o.data.type == "SUN" and o.data.use_shadow), None)
        sdir = (sun.matrix_world.to_quaternion() @ Vector((0, 0, -1))) if sun else Vector((0, 0, -1))
        xs, ys = [], []
        for f in range(1, n + 1, 3):
            sc.frame_set(f)
            bpy.context.view_layer.update()
            for A in actors:
                if A.P.root.scale.x < 0.01:
                    continue
                c = A.P.root.matrix_world.translation
                r_ = 1.7 * A.scale
                for dx, dy, dz in ((r_, 0, 0), (-r_, 0, 0), (0, r_, 0), (0, -r_, 0), (0, 0, 2.4 * A.scale), (0, 0, -0.2)):
                    pp = c + Vector((dx, dy, dz))
                    pts = [pp]
                    if sdir.z < -0.05:
                        pts.append(pp + sdir * (pp.z / -sdir.z))
                    for q in pts:
                        v = world_to_camera_view(sc, cam, q)
                        if v.z > 0:
                            xs.append(v.x)
                            ys.append(v.y)
        if xs:
            m = 0.05
            sc.render.use_border = True
            sc.render.use_crop_to_border = False
            sc.render.border_min_x = max(0.0, min(xs) - m)
            sc.render.border_max_x = min(1.0, max(xs) + m)
            sc.render.border_min_y = max(0.0, min(ys) - m)
            sc.render.border_max_y = min(1.0, max(ys) + m)
            print("BORDER", sid, round(sc.render.border_min_x, 2), round(sc.render.border_max_x, 2),
                  round(sc.render.border_min_y, 2), round(sc.render.border_max_y, 2), flush=True)
    sc.frame_set(0)
    bpy.ops.render.render(write_still=False)   # baseline: characters hidden -> shadow_0000
    sc.frame_start, sc.frame_end = 1, (6 if PREVIEW else min(n, int(os.environ.get("NFR", n))))
    sc.eevee.use_soft_shadows = os.environ.get("SOFT", "0") == "1"
    sc.eevee.taa_render_samples = int(os.environ.get("SAMPLES", "4"))
    sc.eevee.use_gtao = os.environ.get("AO", "1") == "1"
    sc.eevee.use_bloom = False
    sc.eevee.shadow_cascade_size = os.environ.get("CASC", "1024")
    sc.eevee.shadow_cube_size = "512"
    for lo in [o for o in bpy.data.objects if o.type == "LIGHT" and o.data.type == "SUN"]:
        lo.data.shadow_cascade_count = int(os.environ.get("NCASC", "2"))
        lo.data.shadow_cascade_max_distance = 40
    if actors:
        bpy.ops.render.render(animation=True)
    for f in os.listdir(d):
        if f.startswith("_combined_"):
            os.remove(os.path.join(d, f))
    json.dump(dict(scene=sid, plate=pk, frames=n, fps=FPS, shadow_k=p.get("shadow_k", 0.5), actors=len(actors),
                   seconds=round(time.time() - t0, 1)), open(os.path.join(d, "meta.json"), "w"), indent=1)
    print(f"CHARS SC{sid:03d} {n} frames {time.time() - t0:.1f}s", flush=True)


def do_full(sid):
    t0 = time.time()
    spec = FULL[sid]
    pk = spec["plate"]
    L.reset()
    R.reset_caches()
    E._MESH.clear()
    if spec.get("light"):
        PLATES[pk] = dict(PLATES[pk], light=spec["light"])
    info = build_env(pk, full=True)
    cam = setup_camera(pk, info)
    actors = build_actors(spec["actors"], info)
    n = scene_frames(sid)
    L.render_setup((1600, 900), 8, haze=info.get("haze", "#D0DCE4"), mist=(18, 170), haze_amt=0.45)
    sc = bpy.context.scene
    sc.eevee.use_soft_shadows = False
    sc.render.fps = FPS
    sc.frame_start, sc.frame_end = 1, n
    if spec["camera"] == "orbit":
        piv = L.link(bpy.data.objects.new("campivot", None))
        piv.location = (0, 0, 3.4)
        cam.location = (0, -9.5, 0.2)
        cam.parent = piv
        cam.rotation_euler = (Vector((0, 0, 0.3)) - Vector((0, -9.5, 0.2))).to_track_quat("-Z", "Y").to_euler()
        piv.rotation_euler = (0, 0, -0.55)
        piv.keyframe_insert("rotation_euler", frame=1)
        piv.rotation_euler = (0, 0, 0.35)
        piv.keyframe_insert("rotation_euler", frame=n)
    else:
        cam.keyframe_insert("location", frame=1)
        cam.location = Vector(cam.location) + Vector((0.5, -3.5, 1.2))
        cam.keyframe_insert("location", frame=n)
    set_handler(actors, hide_frame0=False)
    d = os.path.join(OUT, "full", f"SC{sid:03d}")
    os.makedirs(d, exist_ok=True)
    sc.render.filepath = os.path.join(d, "f_")
    bpy.ops.render.render(animation=True)
    os.makedirs(os.path.join(OUT, "logs"), exist_ok=True)
    open(os.path.join(OUT, "logs", f"full_{sid}.done"), "w").write("done")
    print(f"FULL SC{sid:03d} {n} frames {time.time() - t0:.1f}s", flush=True)


json.dump(dict(scene_plate={str(k): v["plate"] for k, v in SCENES.items()}, full=sorted(FULL)),
          open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "scenes3_data.json"), "w"), indent=1)
keys = list(PLATES) if (MODE == "plate" and WANT == "all") else WANT.split(",")
for k in keys:
    try:
        if MODE == "plate":
            do_plate(k)
        elif MODE == "chars":
            do_chars(int(k))
        elif MODE == "queue":       # shared work queue: claim a scene atomically, render it, move on
            os.makedirs(os.path.join(OUT, "claims"), exist_ok=True)
            try:
                os.mkdir(os.path.join(OUT, "claims", f"SC{int(k):03d}"))
            except FileExistsError:
                continue
            if int(k) in FULL:
                do_full(int(k))
            else:
                do_chars(int(k))
        elif MODE == "full":
            do_full(int(k))
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"FAILED {MODE} {k}: {e}", flush=True)
