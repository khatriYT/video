"""Episode 3 shot builder. Run inside Blender:

  blender -b --factory-startup -P tools/vulture3d/shots.py -- <out_dir> <SHOT,SHOT|all> [--preview] [--frames=N]

Stills are rendered at 2304x1296 (1.2x headroom for camera moves); --preview renders 960x540 with few samples.
Animated shots (A01-A03) render 12 fps PNG sequences at 1920x1080 into <out_dir>/<shot>/.
Each render writes <shot>_settings.json (camera, light preset, state) next to the image.
"""
import json
import math
import os
import random
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy  # noqa: E402
from mathutils import Vector  # noqa: E402

import lib as L  # noqa: E402

ARGV = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = ARGV[0] if ARGV else "/tmp/renders"
WANT = ARGV[1].split(",") if len(ARGV) > 1 else ["all"]
PREVIEW = "--preview" in ARGV
FRAMES = {k: int(v) for k, v in (a[9:].split(":") for a in ARGV if a.startswith("--frames="))}

CARCASS = (0.0, 0.0)


# ------------------------------------------------------------------ environments
def env_dump(M, state, light, green=False):
    """ENV_DUMP: the observation plate at the edge of an Indian village.
    state: hour0 | arrive | feed | day1 | day3 | week2 | year1 | year10 | nepal"""
    haze = L.world(light, clouds=0.35 if light not in ("night", "overcast", "monsoon") else 0.0,
                   stars=(light == "night"))
    L.ground(M, color="#C9AF7F" if not green else "#A7A167", color2="#AD9260" if not green else "#8E8B52")
    rnd = random.Random(11)
    # landmarks (fixed positions: never move between time steps)
    L.tree(M, "dead", (-7.5, 7.0, 0), 1.25, seed=4)
    L.tree(M, "neem", (10.0, 14.0, 0), 1.5, seed=2)
    L.tree(M, "neem", (-16.0, 20.0, 0), 1.7, seed=3)
    L.tree(M, "neem", (22.0, 30.0, 0), 1.6, seed=5)
    L.tree(M, "neem", (-30.0, 38.0, 0), 1.9, seed=6)
    houses = [(4, 34, 0.2, "#D9B98C", "#A65E3A", "flat"), (8, 36, -0.1, "#C9A27A", "#8C4A30", "tile"),
              (12.5, 33, 0.05, "#B9C3C0", "#6C7F86", "flat"), (-2, 37, 0.15, "#E1C79D", "#A65E3A", "tile"),
              (16, 38, -0.2, "#D7A58A", "#9A5A40", "flat"), (-7, 35, 0.0, "#CBB89A", "#7E5A3A", "flat"),
              (20, 35, 0.1, "#E3CFA8", "#A65E3A", "tile")]
    for x, y, r, w, t, roof in houses:
        L.house(M, (x, y, 0), r, wall=w, trim=t, roof=roof, scale=1.4)
    if light == "night" or state == "year10":
        for x, y, *_ in houses[:5]:
            L.point_light((x + 0.4, y - 2.6, 1.6), energy=600, radius=0.6)
    for k in range(5):
        L.hill(M, (-120 + k * 60, 160 + rnd.uniform(-10, 10), -5), (45, 25, rnd.uniform(10, 18)))
    L.scatter(M, lambda p, r: L.rock(M, p, r), 40, ((-25, 25), (-12, 30)), avoid=[(0, 0, 3)], seed=2)
    L.scatter(M, lambda p, r: L.tuft(M, p, r, green), 650 if not green else 900, ((-26, 26), (-14, 30)),
              avoid=[(0, 0, 2.2)], seed=3)
    # carcass / remains by state
    if state in ("hour0", "arrive", "feed", "day1", "nepal"):
        L.cow(M, (CARCASS[0], CARCASS[1], 0), 0.35, "carcass", 1.0)
    elif state in ("day3", "week2"):
        L.cow(M, (CARCASS[0], CARCASS[1], 0), 0.35, "bloated", 1.0)
    elif state == "year1":
        L.cow(M, (CARCASS[0], CARCASS[1], 0), 0.35, "bloated", 1.0)
        L.bones(M, (5.0, 2.5, 0), 1.2, 1.0, seed=4)
    elif state == "year10":
        L.bones(M, (0, 0, 0), 0.35, 1.1, seed=1)
        L.bones(M, (5.0, 2.5, 0), 1.2, 1.0, seed=4)
        L.bones(M, (-4.5, 3.5, 0), -0.6, 0.9, seed=7)
        L.bones(M, (2.5, 7.5, 0), 2.2, 0.9, seed=9)
    # animals by state
    tree_perches = [(-7.5 + 1.5, 7.3, 3.6), (-7.5 - 1.2, 8.0, 3.9), (-7.5, 7.0, 4.0)]
    if state == "hour0":
        for i, (x, y, z) in enumerate([(-5, 20, 18), (6, 25, 22), (14, 15, 15)]):
            L.vulture(M, (x, y, z), i * 1.7, "soar", 1.0, bank=0.3)
        L.vulture(M, (-7.5 + 1.0, 7.4, 3.75), 2.6, "perch", 0.95)
        L.vulture(M, (-7.5 - 0.8, 7.6, 3.65), 0.4, "perch", 0.95)
    if state in ("arrive", "feed", "nepal"):
        ring = [(math.cos(math.radians(a)) * r, math.sin(math.radians(a)) * r, 0) for a, r in
                [(95, 1.5), (140, 1.9), (30, 2.3), (180, 2.2), (60, 1.9), (220, 2.4), (115, 3.2), (5, 2.6), (160, 3.4)]]
        n = {"arrive": 6, "feed": 9, "nepal": 5}[state]
        for i, (x, y, r) in enumerate(ring[:n]):
            pose = "feed" if i % 3 != 2 else ("spread" if i == 2 else "stand")
            face = math.atan2(CARCASS[1] - y, CARCASS[0] - x) + (0.0 if pose == "feed" else 0.9)
            L.vulture(M, (x, y, 0), face, pose, 1.0)
        n_air = {"arrive": 6, "feed": 3, "nepal": 4}[state]
        for i in range(n_air):
            a = i * 2.1
            L.vulture(M, (math.cos(a) * (4 + i), math.sin(a) * (3 + i) + 3, 3.5 + i * 1.6), a + 1.6, "soar", 1.0,
                      bank=0.35)
        for p in tree_perches[:2]:
            L.vulture(M, p, 2.0, "perch", 0.9)
    if state in ("day1", "day3"):
        L.crow(M, (0.6, -0.5, 0.75), 2.4, 1.2, peck=True)
        L.crow(M, (-1.6, -0.9, 0), 0.6, 1.2)
        if state == "day3":
            L.crow(M, (2.2, 0.2, 0), 3.4, 1.2, peck=True)
            L.crow(M, (-0.8, 1.4, 0), 5.0, 1.2)
    if state == "week2":
        for (x, y, r, pose) in [(2.4, -1.0, 3.3, "sniff"), (-2.3, -0.6, 0.2, "stand"), (1.0, 1.7, 4.4, "sniff"),
                                (-1.0, -2.3, 1.2, "walk")]:
            L.dog(M, (x, y, 0), r, pose, 1.1)
        L.crow(M, (-3.5, 1.5, 0), 0.6, 1.2)
    if state == "year1":
        spots = [(2.4, -1.0, 3.3, "sniff"), (-2.3, -0.6, 0.2, "stand"), (1.0, 1.7, 4.4, "sniff"),
                 (-1.0, -2.3, 1.2, "walk"), (4.0, 1.0, 2.4, "sniff"), (6.2, 3.8, 3.8, "stand"),
                 (-4.2, 2.6, 5.5, "sit"), (3.4, -3.0, 2.0, "walk"), (-3.8, -2.8, 0.9, "stand")]
        for (x, y, r, pose) in spots:
            L.dog(M, (x, y, 0), r, pose, 1.1)
    if state == "year10":
        spots = [(1.4, -1.0, 3.3, "sniff"), (-2.3, -0.6, 0.2, "stand"), (1.0, 1.7, 4.4, "sit"),
                 (-1.0, -2.3, 1.2, "walk"), (4.0, 1.0, 2.4, "sniff"), (6.2, 3.8, 3.8, "stand"),
                 (-4.2, 2.6, 5.5, "sit"), (3.4, -3.0, 2.0, "walk"), (-3.8, -2.8, 0.9, "stand"),
                 (-6.0, 4.5, 0.4, "stand"), (2.0, 8.0, 4.0, "walk"), (7.5, 0.5, 2.8, "sit")]
        for (x, y, r, pose) in spots:
            L.dog(M, (x, y, 0), r, pose, 1.1)
    return haze


CAM_WIDE = dict(loc=(-1.5, -15.5, 3.4), target=(1.0, 4.0, 1.2), lens=30)
CAM_LOW = dict(loc=(4.6, -5.2, 1.1), target=(0.2, 0.2, 0.7), lens=42)


def env_roost(M, light, n_birds=7, ground_color="#B99E6C"):
    """Dead roost tree + a neem, vultures perched (P13/P14/P15/A02)."""
    haze = L.world(light, clouds=0.3)
    L.ground(M, color=ground_color, color2="#9F8656")
    root, perches = L.tree(M, "dead", (0, 0, 0), 1.6, seed=4)
    L.tree(M, "neem", (-9, 10, 0), 1.6, seed=2)
    L.tree(M, "neem", (14, 22, 0), 1.8, seed=8)
    for k in range(4):
        L.hill(M, (-100 + k * 70, 150, -5), (50, 25, 14))
    L.scatter(M, lambda p, r: L.tuft(M, p, r), 400, ((-20, 20), (-10, 25)), seed=4)
    birds = []
    for i, p in enumerate(perches[:n_birds]):
        birds.append(L.vulture(M, (p[0], p[1], p[2] - 0.05), (-0.45 if i == 0 else 1.6 + i * 0.9), "perch", 1.0))
    return haze, perches, birds


def env_sky(M, light, n=8):
    haze = L.world(light, clouds=0.55)
    g = L.ground(M, color="#B39A6B", color2="#8D7A52")
    g.location.z = -60
    return haze


def env_room(M):
    """Simple interior corner with a wooden table (P16)."""
    haze = L.world("day", clouds=0.0)
    wall = L.mat("plaster", "#E7DCC6", 0.95, noise=("#D9CBB0", 0.6), noise_scale=3)
    L.prim("cube", "table", (0, 0, -0.05), (6, 4, 0.1), m=M["wood"])
    L.prim("cube", "wall", (0, 1.6, 1.5), (8, 0.1, 4), m=wall)
    L.prim("cube", "wall2", (-3.2, 0, 1.5), (0.1, 6, 4), m=wall)
    win = L.mat("window", "#FFF2D8", 0.5, emit=3.0)
    L.prim("cube", "window", (1.6, 1.54, 1.6), (1.6, 0.02, 1.4), m=win)
    ld = bpy.data.lights.new("AREA", "AREA")
    ld.energy = 900
    ld.size = 2.5
    ld.color = L.hex_lin("#FFE9C8")
    a = L.link(bpy.data.objects.new("AREA", ld))
    a.location = (2.4, 0.6, 3.4)
    a.rotation_euler = (math.radians(30), math.radians(25), 0)
    # props: pills blister + cloth
    L.prim("cube", "cloth", (-1.2, 0.3, 0.005), (1.6, 1.2, 0.01), rot=(0, 0, 0.3),
           m=L.mat("cloth_blue", "#4C6E91", 0.95))
    for i in range(6):
        L.prim("sphere", "pill", (0.9 + (i % 3) * 0.13, -0.6 + (i // 3) * 0.13, 0.03), (0.05, 0.05, 0.025),
               m=L.mat("pill", "#F4F1EA", 0.4))
    return haze


def env_village(M, light, cow=False):
    """ENV_VILLAGE: street between houses (P18) or a yard with a cow (P19)."""
    haze = L.world(light, clouds=0.3)
    L.ground(M, color="#C2A57A", color2="#A88C62")
    xs = [(-6.5, 0), (-6.5, 4.5), (-6.5, 9), (-6.5, 14), (6.5, 1), (6.5, 6), (6.5, 11), (6.5, 16)]
    cols = [("#D9B98C", "#A65E3A"), ("#B9C3C0", "#6C7F86"), ("#E1C79D", "#A65E3A"), ("#C9A27A", "#8C4A30"),
            ("#D7A58A", "#9A5A40"), ("#E3CFA8", "#A65E3A"), ("#CBB89A", "#7E5A3A"), ("#BFCFC4", "#5E7A6E")]
    for (x, y), (w, t) in zip(xs, cols):
        L.house(M, (x, y, 0), math.pi / 2 if x < 0 else -math.pi / 2, w=3.5, d=3.2, h=2.6, wall=w, trim=t,
                roof="flat" if (x + y) % 2 else "tile", scale=1.0)
    L.tree(M, "neem", (-3.0, 20, 0), 1.6, seed=9)
    L.scatter(M, lambda p, r: L.rock(M, p, r, r.uniform(0.08, 0.2)), 25, ((-4, 4), (-3, 18)), seed=8)
    if light in ("dusk", "night"):
        for (x, y) in xs[:6]:
            L.point_light((x * 0.75, y - 0.5, 2.0), energy=90, radius=0.3)
    if cow:
        L.cow(M, (0.5, 5.0, 0), -2.4, "standing", 1.0)
        L.villager(M, (-1.8, 4.0, 0), -0.6, skin="#B27A50", cloth="#C0563A", hair="#151210", scale=0.75)
    return haze


def env_tower(M, light, mirrors=False):
    haze = L.world(light, clouds=0.0 if light == "monsoon" else 0.3)
    L.ground(M, color="#8E9A62", color2="#6F7C48")
    L.hill(M, (0, 6, -9.5), (24, 22, 11), color="#7E8D52")
    L.tower(M, (0, 6, 1.2), 1.0, mirrors=mirrors)
    for i, (x, y, s) in enumerate([(-12, 0, 1.8), (-16, 12, 2.0), (12, 2, 1.7), (15, 14, 2.1), (-6, 20, 2.2),
                                   (8, 22, 2.0), (-20, 4, 1.9), (20, 6, 2.0)]):
        L.tree(M, "neem", (x, y, 0), s, seed=20 + i)
    # far city skyline
    city = L.mat("city", "#9AA3AC", 0.9)
    rnd = random.Random(3)
    for i in range(40):
        h = rnd.uniform(8, 35)
        L.prim("cube", "bldg", (-120 + i * 6 + rnd.uniform(-2, 2), 170 + rnd.uniform(-10, 10), h / 2),
               (rnd.uniform(4, 7), rnd.uniform(4, 7), h), m=city)
    return haze


def env_savanna(M, light, birds=True):
    haze = L.world(light, clouds=0.25)
    L.ground(M, color="#C9A869", color2="#B08E52")
    root, perches = L.tree(M, "acacia", (0, 4, 0), 1.6, seed=12)
    for i, (x, y, s) in enumerate([(-22, 30, 1.4), (26, 40, 1.6), (-45, 60, 1.8), (50, 70, 1.5)]):
        L.tree(M, "acacia", (x, y, 0), s, seed=30 + i)
    for k in range(4):
        L.hill(M, (-140 + k * 90, 220, -8), (70, 30, 16), color="#9AA083")
    L.scatter(M, lambda p, r: L.tuft(M, p, r), 900, ((-25, 25), (-12, 30)), seed=6)
    if birds:
        extra = [(perches[0][0] - 0.7, perches[0][1] + 0.3, perches[0][2]), (perches[1][0] + 0.8, perches[1][1], perches[1][2])]
        for i, p in enumerate(perches + extra):
            L.vulture(M, (p[0], p[1], p[2] - 0.1), 1.2 + i * 1.3, "perch", 1.0)
        for i in range(3):
            L.vulture(M, (-6 + i * 7, 14 + i * 4, 9 + i * 2), i * 2.0, "soar", 1.0, bank=0.3)
    return haze


def airliner(loc, rot_z, scale):
    white = L.mat("plane_white", "#F1F1EE", 0.4)
    parts = [L.prim("cyl", "fus", (0, 0, 0), (0.25, 0.25, 4.0), rot=(0, math.pi / 2, 0), m=white),
             L.prim("cube", "wing", (0.1, 0, 0), (0.8, 4.0, 0.06), rot=(0, 0, 0.25), m=white),
             L.prim("cube", "tail", (-1.8, 0, 0.45), (0.5, 0.06, 0.9), rot=(0, 0.35, 0), m=white),
             L.prim("cube", "stab", (-1.85, 0, 0.1), (0.4, 1.4, 0.05), m=white)]
    return L.group("OBJ_AIRLINER", parts, loc, (0, 0, rot_z), scale)


# ------------------------------------------------------------------ shot table
def S(build, cam, light, **kw):
    return dict(build=build, cam=cam, light=light, **kw)


def build_shot(sid):
    L.reset()
    M = L.P()
    info = dict(shot=sid)
    if sid in ("P00", "P01", "P02", "P03", "P03C", "P04", "P05", "P06", "P07", "P08", "P09", "P24", "A03"):
        st = {"P00": ("hour0", "dawn"), "P01": ("arrive", "morning"), "P02": ("feed", "morning"),
              "P03": ("day1", "noon_hot"), "P03C": ("day1", "noon_hot"), "P04": ("day3", "overcast"),
              "P05": ("week2", "golden"), "P06": ("year1", "dusk"), "P07": ("year10", "night"),
              "P08": ("week2", "golden"), "P09": ("day1", "morning"), "P24": ("nepal", "dawn"),
              "A03": ("nepal", "dawn")}[sid]
        haze = env_dump(M, st[0], st[1], green=sid in ("P24", "A03"))
        info.update(env="ENV_DUMP", state=st[0], light=st[1])
        mist = (18, 160)
        if sid in ("P00", "P03", "P04", "P05", "P06", "P07", "P01"):
            L.camera(**CAM_WIDE)
            info["camera"] = "CAM_WIDE"
        elif sid in ("P02", "P03C"):
            L.camera(**CAM_LOW, dof_dist="auto", fstop=4.0)
            info["camera"] = "CAM_LOW"
        elif sid == "P08":
            L.camera((4.9, -6.2, 0.95), (2.1, -2.0, 0.65), lens=50, dof_dist="auto", fstop=2.8)
            # hero dog in 3/4 view, facing the camera
            L.dog(M, (2.1, -2.0, 0), -0.55, "stand", 1.1)
            info["camera"] = "CAM_CU_DOG"
        elif sid == "P09":
            L.pip(M, (-4.0, -8.0, 0), 0.25, "binoculars", look=(0.0, 0.35))
            L.camera((-0.6, -12.6, 1.6), (-3.2, -6.0, 2.4), lens=38, dof_dist=5.6, fstop=4.0)
            info["camera"] = "CAM_PIP"
        elif sid in ("P24", "A03"):
            L.pip(M, (-5.5, -6.5, 0), math.radians(-160), "look_up", look=(0.0, 0.35))
            L.camera((-3.0, -18.0, 4.5), (0.5, 4.0, 3.5), lens=28)
            info["camera"] = "CAM_WIDE_HIGH"
        return haze, mist, info
    if sid in ("P13", "P14", "P15", "A02"):
        light = {"P13": "golden", "P14": "golden", "P15": "dawn", "A02": "golden"}[sid]
        haze, perches, birds = env_roost(M, light, n_birds=1 if sid in ("P13", "P14") else 7)
        info.update(env="ENV_ROOST", light=light)
        b = birds[0]
        bpy.context.view_layer.update()
        hb = b.matrix_world @ Vector((0.5, 0, 1.04))
        if sid == "P13":
            L.camera(tuple(hb + Vector((2.6, -2.2, -0.1))), tuple(hb + Vector((-0.25, 0, -0.38))), lens=60,
                     dof_dist="auto", fstop=2.0)
        elif sid == "P14":
            L.camera(tuple(hb + Vector((0.55, -1.7, 0.12))), tuple(hb + Vector((0.05, 0, -0.08))), lens=85,
                     dof_dist="auto", fstop=2.0)
        else:
            L.camera((3.0, -13.0, 2.6), (0.0, 0.0, 3.6), lens=40)
        return haze, (25, 180), info
    if sid in ("P10", "P11", "P12", "A01"):
        light = {"P10": "day", "P11": "day", "P12": "day", "A01": "morning"}[sid]
        info.update(env="ENV_SKY", light=light)
        if sid == "P12":
            haze, perches, birds = env_roost(M, "day", n_birds=0)
            L.camera((2.0, -9.0, 0.6), (0.0, 0.0, 6.5), lens=24)
            return haze, (25, 180), info
        haze = env_sky(M, light)
        if sid == "P10":
            L.vulture(M, (0, 0, 0), math.radians(160), "soar", 1.0, bank=-0.25)
            L.camera((1.4, -3.6, -1.6), (0.0, 0.2, 0.4), lens=45, dof_dist="auto", fstop=5.6)
        elif sid == "P11":
            sc = bpy.context.scene
            w = sc.world.node_tree
            ramp = [n for n in w.nodes if n.type == "VALTORGB"][0]
            ramp.color_ramp.elements[0].color = (*L.hex_lin("#BFD3EA"), 1)
            ramp.color_ramp.elements[1].color = (*L.hex_lin("#1E3E78"), 1)
            ramp.color_ramp.elements[0].color = (*L.hex_lin("#9FBCE0"), 1)
            ramp.color_ramp.elements[1].color = (*L.hex_lin("#0E2A63"), 1)
            L.vulture(M, (0, 0, 0), math.radians(160), "soar", 1.0, bank=-0.25)
            airliner((14, 70, 30), math.radians(-20), 3.0)
            L.camera((1.4, -3.6, -1.6), (0.6, 0.6, 0.9), lens=40, dof_dist=3.9, fstop=8)
        elif sid == "A01":
            rig = L.link(bpy.data.objects.new("orbit", None))
            for i in range(9):
                r = 5 + (i % 4) * 3.5
                h = 18 + i * 2.6
                a = i * 2.4
                b = L.vulture(M, (math.cos(a) * r, math.sin(a) * r, h), a + math.pi / 2, "soar", 1.0, bank=0.35)
                b.parent = rig
            L.camera((0, -10, 1.6), (0, 6, 22), lens=24)
            info["rig"] = "orbit"
        return haze, (40, 400), info
    if sid == "P16":
        haze = env_room(M)
        L.vial(M, (0.1, -0.1, 0), "red", 0.9)
        L.vial(M, (0.75, 0.25, 0), "red", 0.9)
        L.camera((1.2, -3.2, 1.3), (0.35, 0.0, 0.5), lens=50, dof_dist="auto", fstop=2.4)
        info.update(env="ENV_ROOM", light="day")
        return haze, (40, 200), info
    if sid == "P17":
        haze, perches, birds = env_roost(M, "overcast", n_birds=0, ground_color="#A99470")
        L.vulture(M, (1.2, -1.6, 0), math.radians(210), "fallen", 1.0)
        rnd = random.Random(2)
        for i in range(8):
            L.prim("sphere", "feather", (rnd.uniform(-1.5, 3), rnd.uniform(-3, 0.5), 0.02),
                   (0.12, 0.03, 0.006), rot=(0, 0, rnd.uniform(0, 6)), m=M["v_wing"])
        L.camera((3.9, -5.0, 2.7), (1.3, -1.5, 0.15), lens=42, dof_dist="auto", fstop=4.0)
        info.update(env="ENV_ROOST", light="overcast")
        return haze, (25, 180), info
    if sid == "P18":
        haze = env_village(M, "dusk")
        for (x, y, r, pose) in [(0.5, 3.0, 2.0, "stand"), (-1.5, 6.5, -0.4, "sniff"), (1.8, 8.5, 3.6, "walk"),
                                (-0.5, 11.0, 1.0, "sit"), (2.4, 0.0, 2.6, "walk")]:
            L.dog(M, (x, y, 0), r, pose, 1.1)
        L.villager(M, (-3.4, 12.5, 0), 0.0, skin="#8D5A3B", cloth="#B3473A", hair="#151210", scale=0.75)
        L.villager(M, (3.4, 14.0, 0), 0.4, skin="#C68B5E", cloth="#3F6EA8", hair="#2A1F18", scale=0.75)
        L.camera((0.3, -6.5, 1.5), (0.0, 8.0, 1.4), lens=30)
        info.update(env="ENV_VILLAGE", light="dusk")
        return haze, (20, 120), info
    if sid == "P19":
        haze = env_village(M, "morning", cow=True)
        L.camera((4.0, -3.5, 1.6), (0.4, 5.0, 1.3), lens=38)
        info.update(env="ENV_VILLAGE", light="morning")
        return haze, (20, 120), info
    if sid in ("P20", "P20B"):
        light = "dawn" if sid == "P20" else "monsoon"
        haze = env_tower(M, light, mirrors=(sid == "P20B"))
        L.camera((14.0, -30.0, 6.0), (0.0, 5.0, 4.0), lens=40)
        info.update(env="ENV_TOWER", light=light)
        return haze, (30, 200), info
    if sid in ("P21", "P22"):
        light = "golden" if sid == "P21" else "dusk"
        haze = env_savanna(M, light, birds=(sid == "P21"))
        L.camera((2.0, -15.0, 2.2), (0.0, 4.0, 3.6), lens=35)
        info.update(env="ENV_SAVANNA", light=light)
        return haze, (30, 220), info
    raise KeyError(sid)


def animate(sid, nframes):
    sc = bpy.context.scene
    sc.render.fps = 12
    sc.frame_start, sc.frame_end = 1, nframes
    if sid == "A01":
        rig = bpy.data.objects["orbit"]
        rig.rotation_euler = (0, 0, 0)
        rig.keyframe_insert("rotation_euler", frame=1)
        rig.rotation_euler = (0, 0, -0.06 * nframes / 12 * 2.0)
        rig.keyframe_insert("rotation_euler", frame=nframes)
        for fc in rig.animation_data.action.fcurves:
            for kp in fc.keyframe_points:
                kp.interpolation = "LINEAR"
        cam = sc.camera
        cam.keyframe_insert("rotation_euler", frame=1)
        cam.rotation_euler.x += 0.06
        cam.keyframe_insert("rotation_euler", frame=nframes)
    elif sid == "A02":
        cam = sc.camera
        piv = L.link(bpy.data.objects.new("campivot", None))
        piv.location = (0, 0, 3.2)
        cam.location = (0, -9.0, 0.0)
        cam.parent = piv
        d = Vector((0, 0, 3.4)) - Vector((0, -9.0, 3.2))
        cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
        piv.rotation_euler = (0, 0, -0.5)
        piv.keyframe_insert("rotation_euler", frame=1)
        piv.rotation_euler = (0, 0, 0.35)
        piv.keyframe_insert("rotation_euler", frame=nframes)
    elif sid == "A03":
        cam = sc.camera
        cam.keyframe_insert("location", frame=1)
        cam.location = Vector(cam.location) + Vector((0.5, -3.5, 1.2))
        cam.keyframe_insert("location", frame=nframes)
        birds = [o for o in bpy.data.objects if o.name.startswith("CRE_VULTURE") and o.location.z > 2.5]
        for i, b in enumerate(birds):
            c = Vector(b.location)
            for f in (1, nframes):
                t = (f - 1) / 12.0
                a = 0.35 * t * (1 if i % 2 else -1)
                b.location = (c.x * math.cos(a) - c.y * math.sin(a), c.x * math.sin(a) + c.y * math.cos(a),
                              c.z - 0.25 * t)
                b.rotation_euler.z = b.rotation_euler.z + (a if f == nframes else 0)
                b.keyframe_insert("location", frame=f)
                b.keyframe_insert("rotation_euler", frame=f)


def render(sid):
    t0 = time.time()
    haze, mist, info = build_shot(sid)
    is_anim = sid.startswith("A")
    if PREVIEW:
        res, samples = (960, 540), 8
    elif is_anim:
        res, samples = (1600, 900), 8
    else:
        res, samples = (2304, 1296), 16
    L.render_setup(res, samples, haze=haze, mist=mist, haze_amt=0.5)
    os.makedirs(OUT, exist_ok=True)
    info.update(resolution=res, samples=samples, engine="EEVEE", mist=mist)
    if is_anim and not PREVIEW:
        n = FRAMES.get(sid, 72)
        animate(sid, n)
        d = os.path.join(OUT, sid)
        os.makedirs(d, exist_ok=True)
        bpy.context.scene.render.filepath = os.path.join(d, "f_")
        bpy.ops.render.render(animation=True)
        info["frames"] = n
    else:
        bpy.context.scene.render.filepath = os.path.join(OUT, sid + (".preview.png" if PREVIEW else ".png"))
        bpy.ops.render.render(write_still=True)
    info["seconds"] = round(time.time() - t0, 1)
    json.dump(info, open(os.path.join(OUT, sid + ("_preview" if PREVIEW else "") + "_settings.json"), "w"), indent=1)
    print(f"RENDERED {sid} in {info['seconds']} s", flush=True)


ALL = ["P00", "P01", "P02", "P03", "P03C", "P04", "P05", "P06", "P07", "P08", "P09", "P10", "P11", "P12", "P13",
       "P14", "P15", "P16", "P17", "P18", "P19", "P20", "P20B", "P21", "P22", "P24", "A01", "A02", "A03"]
for sid in (ALL if WANT == ["all"] else WANT):
    try:
        render(sid)
    except Exception as e:  # keep going; record the failure
        import traceback
        traceback.print_exc()
        print(f"FAILED {sid}: {e}", flush=True)
