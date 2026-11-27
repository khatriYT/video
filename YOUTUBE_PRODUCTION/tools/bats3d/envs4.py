"""Episode 4 environments (v3): colourful, art-directed sets with consistent palettes per location.

Each builder returns an Env with named anchor points (character marks, camera targets), the key-light
direction and colour (so character passes match the plate), and a palette.
ENV_HILL   Texas Hill Country sinkhole cave (sunset / dusk / night)
ENV_CAVE   hibernaculum interior (headlamp; healthy / infected / empty / hope states)
ENV_FARM   corn + cotton farm with red barn and farmhouse (day / dusk / night)
ENV_AGAVE  agave fields under Jalisco-style hills (sunset / blue hour / night)
ENV_TROPIC fig forest, durian orchard at night, regrowing clearing
ENV_SKY    high-altitude night sky over farm lights; moon sky
ENV_STUDIO colour-gradient studio for the wing anatomy shot
ENV_MINE   mine entrance in green hills at dusk
ENV_WIND   ridge with wind turbines at sunset
"""
import math
import os
import random

import bpy
from mathutils import Vector

import core as C
import flora as FL
import meshio

MODELS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "01_PROJECTS",
                      "what_if_bats_disappeared", "07_3D_Assets", "models")


class Env:
    def __init__(self, name):
        self.name = name
        self.marks = {}
        self.key = None            # (direction_to_light, colour, energy)
        self.fill = None
        self.rim = None
        self.ground = []           # shadow-receiving objects (kept in character passes)
        self.palette = {}
        self.bat_light = "#FFB070"


def _sstep(a, b, x):
    t = max(0.0, min(1.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)


def terrain(name, size, n, hfn, mat, hole=None, z_off=0.0):
    verts, faces = [], []
    idx = {}
    for j in range(n + 1):
        for i in range(n + 1):
            x = -size / 2 + size * i / n
            y = -size / 2 + size * j / n
            idx[(i, j)] = len(verts)
            verts.append((x, y, hfn(x, y) + z_off))
    for j in range(n):
        for i in range(n):
            if hole:
                cx = -size / 2 + size * (i + 0.5) / n
                cy = -size / 2 + size * (j + 0.5) / n
                if hole(cx, cy):
                    continue
            faces.append((idx[(i, j)], idx[(i + 1, j)], idx[(i + 1, j + 1)], idx[(i, j + 1)]))
    ob = C.mesh_ob(name, verts, faces, mat)
    return ob


def prefab(objs, name, col_name):
    """Group objects into an instance collection (origin at 0)."""
    col = bpy.data.collections.get(col_name) or bpy.data.collections.new(col_name)
    for ob in objs:
        for c in list(ob.users_collection):
            c.objects.unlink(ob)
        col.objects.link(ob)
    return col


def place(col, loc, rot=0.0, s=1.0, name="inst"):
    e = C.link(bpy.data.objects.new(name, None))
    e.instance_type = "COLLECTION"
    e.instance_collection = col
    e.location = loc
    e.rotation_euler = (0, 0, rot)
    e.scale = (s, s, s)
    return e


def lib_collection(name, builders):
    """Build several variants into one collection laid out at the origin (each a separate child hierarchy)
    so Geometry-Nodes scattering can pick between them."""
    col = bpy.data.collections.new(name)
    for k, b in enumerate(builders):
        objs = b(k)
        objs = objs if isinstance(objs, list) else [objs]
        root = C.link(bpy.data.objects.new(f"{name}_{k}", None))
        for ob in objs:
            if ob.parent is None:
                ob.parent = root
        # Collection Info 'Separate Children' instances every OBJECT of a collection on its own, so a
        # multi-part plant (corn: stalk + leaves + tassel + ear) must live in its own child collection
        # to be instanced whole. Single-mesh variants keep the original layout (plates already rendered
        # with it must keep matching their character passes).
        dest = col
        if len(objs) > 1:
            dest = bpy.data.collections.new(f"{name}_{k}")
            col.children.link(dest)
        for ob in [root] + objs:
            for c in list(ob.users_collection):
                c.objects.unlink(ob)
            dest.objects.link(ob)
    return col


def ground_point(objs, x, y, z0=200.0):
    """Ray-cast straight down onto the given objects."""
    dg = bpy.context.evaluated_depsgraph_get()
    best = None
    for ob in objs:
        mw = ob.matrix_world
        inv = mw.inverted()
        o = inv @ Vector((x, y, z0))
        d = (inv.to_3x3() @ Vector((0, 0, -1))).normalized()
        ok, loc, nrm, idx = ob.evaluated_get(dg).ray_cast(o, d)
        if ok:
            p = mw @ loc
            if best is None or p.z > best.z:
                best = p
    return best if best is not None else Vector((x, y, 0))


# ------------------------------------------------------------------ shared vegetation libraries
def veg_hill():
    gm = FL.m_leaf("grass_gold", "#C8A55A", 0.12, 0.7, 0.2, tip="#E8CF8A")
    gm2 = FL.m_leaf("grass_green", "#8FA04E", 0.1, 0.65, 0.25, tip="#C9C27A")
    stem = FL.m_leaf("stem", "#5E7A3A", 0.05)
    blue = C.m_simple("bluebonnet", "#3F5FD0", 0.5, sss=0.3)
    white = C.m_simple("bb_tip", "#F2F0FF", 0.5, sss=0.3)
    red = C.m_simple("paintbrush", "#E8502E", 0.5, sss=0.3)
    yel = C.m_simple("daisy_y", "#F6C531", 0.45, sss=0.3)
    brn = C.m_simple("daisy_c", "#6A3A1A", 0.6)
    pink = C.m_simple("primrose", "#F29AC0", 0.45, sss=0.35)
    grass = lib_collection("L_grass", [lambda k: FL.grass_clump(f"gr{k}", gm if k % 3 else gm2, 22, 0.36 + 0.08 * k,
                                                                   0.016, seed=k, spread=0.12) for k in range(4)])
    flowers = lib_collection("L_flowers", [
        lambda k: FL.flower_spike(f"bb{k}", stem, blue, white, 0.3, 0.12, seed=k),
        lambda k: FL.flower_spike(f"bb{k}", stem, blue, white, 0.26, 0.1, seed=k + 3),
        lambda k: FL.flower_spike(f"pb{k}", stem, red, red, 0.28, 0.09, 0.02, seed=k),
        lambda k: FL.daisy(f"dz{k}", yel, brn, stem, 0.3, 0.03),
        lambda k: FL.daisy(f"pr{k}", pink, yel, stem, 0.2, 0.026, 5),
    ])
    return grass, flowers


# ------------------------------------------------------------------ ENV_HILL
def env_hill(state="sunset", detail=1.0):
    E = Env("hill")
    rnd = random.Random(4)
    if state == "sunset":
        C.world_sky([(0.0, "#FFC27A"), (0.05, "#FF945E"), (0.14, "#E0607E"), (0.32, "#8A4590"), (0.6, "#41307A"),
                     (1.0, "#1E1F4E")], strength=1.4, sun_dir=(1.0, -0.15, 0.09), sun_col="#FFD08A", sun_glow=1.6,
                    clouds=("#FFB89A", 0.42, 2.2, "#8A4A7A"), ground="#6A4A40", ambient=("#8C86B8", 0.9))
        E.key = ((1.0, -0.15, 0.12), "#FFA868", 6.0)
        E.fill = ("#8C7BC8", 0.6)
        E.rim = ("#FFC27A", 1.0)
        haze = ("#F2A27A", 0.0035)
    elif state == "dusk":
        C.world_sky([(0.0, "#F29A6A"), (0.06, "#C86A86"), (0.2, "#6A4A9A"), (0.5, "#2C2F72"), (1.0, "#121638")],
                    strength=0.9, sun_dir=(0.3, 1.0, -0.02), sun_col="#FF9A7A", sun_glow=0.6,
                    clouds=("#E08AA0", 0.38, 2.2, "#4A3A6A"), ground="#2A2030", stars=0.4)
        E.key = ((0.3, 1.0, 0.05), "#E78A7A", 1.6)
        E.fill = ("#6A6AC0", 0.7)
        E.rim = ("#FFB08A", 0.8)
        haze = ("#9A7AB0", 0.003)
    else:   # night
        C.world_sky([(0.0, "#3A4A7A"), (0.1, "#22305E"), (0.4, "#121A3C"), (1.0, "#070A1C")], strength=0.9,
                    stars=1.6, moon=((-0.35, 1.0, 0.32), 1.6, "#FFF6DE"), ground="#0A0C14",
                    clouds=("#3A4A6E", 0.25, 2.0, "#141A30"))
        E.key = ((-0.35, 1.0, 0.45), "#B8C8FF", 1.2)
        E.fill = ("#3A4A8A", 0.7)
        E.rim = ("#9AB0FF", 0.9)
        haze = ("#3A4A7A", 0.0035)
    E.palette = dict(sky_top="#1C1D47", sky_mid="#D9577A", sky_low="#FFB868", ground="#C8A55A")

    def h(x, y):
        r = math.hypot(x, y - 2.0)
        re = math.hypot(x / 9.0, (y - 6.0) / 6.0)
        bowl = -1.6 * (1 - _sstep(0.3, 1.0, re))          # shallow dip in front of the cave arch
        roll = 1.6 * math.sin(x / 31.0) * math.cos(y / 23.0) + 0.7 * math.sin(x / 11.0 + y / 13.0)
        roll *= _sstep(14.0, 30.0, r)
        roll += 4.5 * _sstep(8.0, 22.0, y) * (1 - _sstep(18.0, 40.0, abs(x)))   # hill behind the cliff
        far = max(0.0, r - 90.0) * 0.11 + 6.0 * math.sin(x / 80.0) * _sstep(90.0, 200.0, r)
        return bowl + roll + far
    gmat = FL.m_ground("hill_ground", [("#8A8A44", 0.2), ("#B8A252", 0.42), ("#D2B462", 0.6), ("#9AAA4A", 0.78),
                                       ("#C8B062", 0.95)], 0.12, 0.15, slope_rock="#D0C0A0")
    near = terrain("hill_near", 90, 220, h, gmat)
    far = terrain("hill_far", 900, 150, h, gmat, hole=lambda x, y: abs(x) < 42 and abs(y) < 42, z_off=-0.05)
    E.ground = [near, far]
    rock_m = FL.m_rock("limestone", "#D8C8A6", "#8E7C62", lichen=("#E0902E", "#A8B860"))
    cliff_m = FL.m_rock("cliff_lime", "#B89C74", "#5E4A36", lichen=("#D88A2E", "#8AA050"), scale=0.6)
    mouth = meshio.load(os.path.join(MODELS, "env", "cave_mouth.bin"), "cave_mouth", cliff_m, decimate=1.0)
    mouth.location = (0, 6.5, -1.9)
    dark = C.m_simple("cave_dark", "#050404", 1.0)
    back = FL.icosphere("cave_void", 3.0, 2, dark)
    back.location = (0, 13.0, -2.0)
    back.scale = (1.6, 2.6, 1.2)
    E.ground.append(mouth)
    # ledges / boulders around the rim
    for k in range(34):
        a = rnd.uniform(0, 6.28)
        rr = rnd.uniform(12.5, 19.0)
        x, y = math.cos(a) * rr, 2 + math.sin(a) * rr
        if (y > 0 and abs(x) < 13) or (y < -5 and abs(x) < 7):
            continue
        b = FL.rock(f"rk{k}", rnd.uniform(0.4, 1.6), rock_m, seed=k, flat=0.55)
        b.location = (x, y, h(x, y) - 0.2)
        b.rotation_euler = (0, 0, rnd.uniform(0, 6.28))
    # vegetation libraries
    grass, flowers = veg_hill()
    jun_t = FL.m_bark("juniper_bark", "#6A4C3A")
    jun_l = FL.m_canopy("juniper_leaf", "#2E4428", 0.1, 9.0, 0.2)
    jun_c = FL.m_leaf("juniper_sprig", "#4E6E3E", 0.12, 0.6, 0.25, scale=6.0)
    oak_t = FL.m_bark("oak_bark", "#5A4A40", moss="#7A8A4A")
    oak_l = FL.m_canopy("oak_leaf", "#3A5226", 0.1, 7.0, 0.25)
    oak_c = FL.m_leaf("oak_lf", "#6E8E3E", 0.14, 0.5, 0.35, scale=6.0)
    pear_m = FL.m_leaf("pear_pad", "#6E9A4A", 0.08, 0.5, 0.2, waxy=0.3)
    pfl = C.m_simple("pear_flower", "#F7D23A", 0.4, sss=0.3)
    pfr = C.m_simple("pear_fruit", "#B8265A", 0.4, sss=0.2)
    junipers = [prefab(FL.tree(f"jn{k}", "juniper", seed=k, h=rnd.uniform(3.5, 5.5), crown=rnd.uniform(1.2, 1.8),
                               trunk_m=jun_t, leaf_m=jun_l, lean=rnd.uniform(-0.3, 0.3),
                               leaves=(jun_c, "needle", 0.22, 70.0 * detail)), f"jn{k}", f"C_jn{k}")
                for k in range(3)]
    oaks = [prefab(FL.tree(f"ok{k}", "oak", seed=10 + k, h=rnd.uniform(5.0, 7.0), crown=rnd.uniform(3.0, 4.0),
                           trunk_m=oak_t, leaf_m=oak_l, leaves=(oak_c, "broad", 0.13, 90.0 * detail)),
                   f"ok{k}", f"C_ok{k}") for k in range(2)]
    jun_far = [prefab(FL.tree(f"jf{k}", "juniper", seed=k + 5, h=4.5, crown=1.5, trunk_m=jun_t, leaf_m=jun_l),
                      f"jf{k}", f"C_jf{k}") for k in range(2)]
    pears = [prefab(FL.prickly_pear(f"pp{k}", pear_m, pfl, pfr, seed=k), f"pp{k}", f"C_pp{k}") for k in range(2)]
    marks_avoid = [Vector((-3.5, -10.5, 0)), Vector((3.0, -11.5, 0)), Vector((0, -22, 0)), Vector((0, 4, 0))]
    for k in range(int(70 * detail)):
        a = rnd.uniform(0, 6.28)
        rr = rnd.uniform(18.0, 85.0) if k % 4 else rnd.uniform(15.0, 30.0)
        x, y = math.cos(a) * rr, 2 + math.sin(a) * rr
        if any((Vector((x, y, 0)) - m).length < 5.0 for m in marks_avoid) or (y < -6 and abs(x) < 8) or \
                (abs(x) < 14 and -2 < y < 16):
            continue
        col = (junipers if k % 3 else oaks)[k % (3 if k % 3 else 2)]
        place(col, (x, y, h(x, y) - 0.1), rnd.uniform(0, 6.28), rnd.uniform(0.8, 1.25), f"tree{k}")
    for k in range(40):
        a = rnd.uniform(0, 6.28)
        rr = rnd.uniform(13.0, 40.0)
        x, y = math.cos(a) * rr, 2 + math.sin(a) * rr
        if any((Vector((x, y, 0)) - m).length < 2.5 for m in marks_avoid):
            continue
        place(pears[k % 2], (x, y, h(x, y)), rnd.uniform(0, 6.28), rnd.uniform(0.8, 1.4), f"pear{k}")
    # treeline on the far hills (cheap blobs)
    for k in range(int(140 * detail)):
        a = rnd.uniform(0.0, math.pi) if k % 5 else rnd.uniform(math.pi, 2 * math.pi)
        rr = rnd.uniform(95.0, 300.0)
        x, y = math.cos(a) * rr, 2 + math.sin(a) * rr
        place(jun_far[k % 2], (x, y, h(x, y) - 0.2), rnd.uniform(0, 6.28), rnd.uniform(1.0, 1.8), f"ft{k}")
    # grass + flowers scattered on the near terrain, avoiding the bowl floor
    focus = Vector((0.0, -10.0, 0.0))

    def near_w(p):
        return 0.12 + 0.88 * (1.0 - _sstep(10.0, 34.0, (Vector((p.x, p.y, 0)) - focus).length))
    FL.vgroup_from_fn(near, "veg", lambda p: _sstep(0.9, 1.3, math.hypot(p.x / 9.0, (p.y - 6.0) / 6.0)) * near_w(p))
    FL.vgroup_from_fn(near, "flw", lambda p: _sstep(1.0, 1.4, math.hypot(p.x / 9.0, (p.y - 6.0) / 6.0)) * near_w(p) *
                      (0.25 + 0.75 * max(0.0, math.sin(p.x * 0.21 + 0.5) * math.cos(p.y * 0.17))) ** 0.7)
    FL.scatter(near, grass, 14.0 * detail, seed=3, scale=(0.7, 1.3), mask="veg", name="sc_grass")
    FL.scatter(near, flowers, 9.0 * detail, seed=5, scale=(0.8, 1.3), mask="flw", name="sc_flw")
    C.volume_fog(haze[1], haze[0], 0.35, size=500.0, center=(0, 0, 10), height=25.0)
    E.marks = dict(pip=Vector((-3.4, -10.6, h(-3.4, -10.6))), pip2=Vector((2.6, -11.4, h(2.6, -11.4))),
                   mouth=Vector((0, 8.0, 0.5)), column_top=Vector((0, 10.0, 40.0)), rim=Vector((0, -10, 0)))
    return E


# ------------------------------------------------------------------ ENV_CAVE (hibernaculum)
def env_cave(state="healthy", detail=1.0, bats=True, exterior=False):
    E = Env("cave")
    C.world_flat("#2A3C44", 1.6)
    wall = FL.m_rock("cave_wall", "#7C8A86", "#3E4A4A", strata=True, lichen=None, wet=0.35, scale=1.4)
    cave = meshio.load(os.path.join(MODELS, "env", "hibernaculum.bin"), "hibernaculum", wall, decimate=1.0)
    E.ground = [cave]
    flow = FL.m_rock("flowstone", "#D9A86A", "#8A5A36", strata=False, lichen=None, wet=0.6, scale=2.0)
    stal = FL.m_rock("stalactite", "#B8AE9A", "#6E6658", strata=False, lichen=None, wet=0.7, scale=3.0)
    rnd = random.Random(9)
    # stalactites hanging from the ceiling (ray-cast upward), stalagmites on the floor
    dg = bpy.context.evaluated_depsgraph_get()
    ce = cave.evaluated_get(dg)
    n_st = int(160 * detail)
    for k in range(n_st):
        x, y = rnd.uniform(-6.5, 6.5), rnd.uniform(-4.5, 9.0)
        ok, loc, nrm, idx = ce.ray_cast(Vector((x, y, 1.5)), Vector((0, 0, 1)))
        if not ok or loc.z < 2.2:
            continue
        L = rnd.uniform(0.15, 0.9) * (1.6 if k % 9 == 0 else 1.0)
        wob = Vector((rnd.gauss(0, 0.03), rnd.gauss(0, 0.03), 0))
        st = C.tube(f"stal{k}", [loc + Vector((0, 0, 0.12)), loc - Vector((0, 0, L * 0.35)) + wob * 0.5,
                                 loc - Vector((0, 0, L * 0.7)) + wob, loc - Vector((0, 0, L)) + wob * 1.3],
                    [0.07 + L * 0.09, 0.045 + L * 0.05, 0.02 + L * 0.02, 0.003], 10, stal)
        FL.disp(st, 0.02 + L * 0.02, 0.05, depth=3)
    for k in range(int(40 * detail)):
        x, y = rnd.uniform(-6.0, 6.0), rnd.uniform(-4.2, 3.5)
        ok, loc, nrm, idx = ce.ray_cast(Vector((x, y, 1.0)), Vector((0, 0, -1)))
        if not ok:
            continue
        L = rnd.uniform(0.1, 0.6)
        C.tube(f"stag{k}", [loc - Vector((0, 0, 0.05)), loc + Vector((0, 0, L))], [0.08 + L * 0.1, 0.02], 8, flow)
    # puddles (mirror-like water) on the floor
    water = C.m_simple("water", "#0E1A1C", 0.02, coat=1.0, spec=1.0)
    for k, (x, y, s) in enumerate(((-1.5, -1.0, 1.4), (2.2, -2.4, 0.9), (0.2, 2.2, 1.1))):
        ok, loc, nrm, idx = ce.ray_cast(Vector((x, y, 1.0)), Vector((0, 0, -1)))
        p = FL.icosphere(f"puddle{k}", s, 3, water)
        p.scale = (1.0, 0.7, 0.012)
        p.location = loc + Vector((0, 0, 0.02))
    # daylight entrance at the end of the passage (bright snowy opening)
    if not exterior:
        snow = C.m_emit("entrance_light", "#E6EEF5", 6.0)
        ent = FL.icosphere("entrance", 2.4, 2, snow)
        ent.location = (3.6, 11.6, 1.6)
        ent.scale = (1.0, 0.2, 0.9)
    C.area("ENT_LIGHT", (3.4, 10.2, 2.0), (1.0, 4.0, 0.8), "#CFE0FF", 900.0, 2.5, shadow=True)
    snow_g = C.m_simple("snow", "#F2F6FA", 0.6, sss=0.3)
    sg = FL.grid("snow_ground", 40, 30, 20, 15, snow_g)
    sg.location = (3.5, 25.0, -0.2)
    trunk = FL.m_bark("winter_bark", "#3A3430", 6.0)
    for k, (x, y) in enumerate(((0.5, 16), (6.5, 18), (2.0, 22), (8.5, 24), (-2.0, 20), (5.0, 28))):
        if not exterior:
            C.tube(f"wtrunk{k}", [Vector((x, y, -0.2)), Vector((x + 0.2, y, 9.0))], [0.22, 0.12], 8, trunk)
    if exterior:
        # the opening looks out on a real winter scene instead of a glowing placeholder: overcast sky backdrop,
        # sky light on the snowfield, bare winter trees with branches, snow drifts against the trunks
        sky = C.m_emit("winter_sky", "#C9D8E6", 2.2)
        bd = FL.grid("winter_backdrop", 140, 60, 2, 2, sky)
        bd.rotation_euler = (math.radians(90), 0, 0)
        bd.location = (3.5, 46.0, 18.0)
        C.area("SNOW_SKY", (3.5, 24.0, 16.0), (3.5, 24.0, 0.0), "#E4EEFF", 9000.0, 24.0, shadow=True)
        for k, (x, y, hh) in enumerate(((0.5, 16, 9.0), (6.5, 18, 10.0), (2.0, 22, 8.0), (8.5, 24, 11.0),
                                         (-2.0, 20, 9.5), (5.0, 28, 10.0), (11.0, 30, 9.0), (-4.5, 27, 8.5))):
            for ob in FL.bare_tree(f"wtree{k}", trunk, h=hh, seed=40 + k, depth=4):
                ob.location = Vector(ob.location) + Vector((x + 0.3, y + 0.4, -0.25))
            dr = FL.icosphere(f"drift{k}", 0.9, 2, snow_g)
            dr.scale = (1.4, 1.0, 0.25)
            dr.location = (x + 0.3, y + 0.4, -0.2)
    # cool ambient bounce (hidden area lights) so the chamber volume reads outside the lamp beam
    C.area("BOUNCE1", (0.0, 0.0, 0.4), (0.0, 0.0, 4.0), "#6A9AAA", 400.0, 6.0)
    C.area("BOUNCE2", (-3.6, -2.6, 2.0), (2.0, 2.0, 2.5), "#4A6A8A", 200.0, 4.0)
    C.area("BOUNCE3", (4.0, 1.0, 1.0), (0.0, 0.0, 3.0), "#C08A5A", 160.0, 3.0)
    E.key = None
    E.marks = dict(pip=Vector((-0.6, -2.6, 0.0)), cluster=Vector((0.8, 0.6, 3.6)), cluster2=Vector((-2.6, -0.8, 3.4)),
                   wall=Vector((3.2, -1.2, 2.6)), entrance=Vector((3.6, 11.0, 1.4)))
    for k, m in E.marks.items():
        if k in ("cluster", "cluster2", "wall"):
            continue
        ok, loc, nrm, idx = ce.ray_cast(m + Vector((0, 0, 1.0)), Vector((0, 0, -1)))
        if ok:
            E.marks[k] = loc
    for k in ("cluster", "cluster2"):
        m = E.marks[k]
        ok, loc, nrm, idx = ce.ray_cast(Vector((m.x, m.y, 1.5)), Vector((0, 0, 1)))
        if ok:
            E.marks[k] = loc
    C.volume_fog(0.012, "#9AB4C0", 0.55, size=40.0, center=(0, 2, 2), emission=None)
    E.palette = dict(wall="#7C8A86", flow="#D9A86A", lamp="#FFD9A0", ambient="#4A7A8A")
    return E


# ------------------------------------------------------------------ farm buildings
def barn(name, loc, rot=0.0, s=1.0):
    red = C.m_paint("barn_red", "#B0302A", 0.62, grime=0.25, chip=0.3)
    white = C.m_paint("trim_white", "#F1EBDD", 0.5, grime=0.2)
    roof = C.m_metal("roof_tin", "#7A7F86", 0.45)
    objs = []
    w, d, hw, hr = 9.0, 14.0, 5.0, 3.6
    prof = [(-w / 2, 0), (w / 2, 0), (w / 2, hw), (w * 0.32, hw + hr * 0.7), (0, hw + hr), (-w * 0.32, hw + hr * 0.7),
            (-w / 2, hw)]
    verts, faces = [], []
    for yy in (-d / 2, d / 2):
        for x, z in prof:
            verts.append((x, yy, z))
    n = len(prof)
    for i in range(n):
        j = (i + 1) % n
        faces.append((i, j, n + j, n + i))
    faces.append(tuple(range(n))[::-1])
    faces.append(tuple(range(n, 2 * n)))
    body = C.mesh_ob(name + "_body", verts, faces, red, smooth_=False)
    FL.disp(body, 0.0, 1.0)
    objs.append(body)
    # roof panels
    for sgn in (-1, 1):
        rp = [(sgn * (w / 2 + 0.35), -d / 2 - 0.4, hw - 0.15), (sgn * w * 0.32, -d / 2 - 0.4, hw + hr * 0.7 + 0.12),
              (sgn * w * 0.32, d / 2 + 0.4, hw + hr * 0.7 + 0.12), (sgn * (w / 2 + 0.35), d / 2 + 0.4, hw - 0.15)]
        rq = [(sgn * w * 0.32, -d / 2 - 0.4, hw + hr * 0.7 + 0.12), (0, -d / 2 - 0.4, hw + hr + 0.15),
              (0, d / 2 + 0.4, hw + hr + 0.15), (sgn * w * 0.32, d / 2 + 0.4, hw + hr * 0.7 + 0.12)]
        for k, q in enumerate((rp, rq)):
            o = C.mesh_ob(f"{name}_roof{sgn}{k}", q, [(0, 1, 2, 3) if sgn < 0 else (3, 2, 1, 0)], roof, smooth_=False)
            o.modifiers.new("s", "SOLIDIFY").thickness = 0.08
            objs.append(o)
    # white trim: door X-braces and frame on the gable end facing -Y
    def bar(a, b, r=0.09):
        objs.append(C.tube(f"{name}_trim{len(objs)}", [Vector(a), Vector(b)], [r, r], 6, white))
    y = -d / 2 - 0.06
    for (a, b) in (((-2, y, 0), (-2, y, 3.6)), ((2, y, 0), (2, y, 3.6)), ((-2, y, 3.6), (2, y, 3.6)),
                   ((-2, y, 0), (2, y, 3.6)), ((-2, y, 3.6), (2, y, 0)), ((-w / 2, y, hw), (0, y, hw + hr)),
                   ((0, y, hw + hr), (w / 2, y, hw)), ((-w / 2, y, 0.05), (-w / 2, y, hw)),
                   ((w / 2, y, 0.05), (w / 2, y, hw))):
        bar(a, b)
    hay = C.m_simple("hayloft", "#2A1A12", 0.9)
    loft = C.mesh_ob(name + "_loft", [(-1.0, y - 0.02, hw + 0.4), (1.0, y - 0.02, hw + 0.4), (1.0, y - 0.02, hw + 2.0),
                                      (-1.0, y - 0.02, hw + 2.0)], [(0, 1, 2, 3)], hay, smooth_=False)
    objs.append(loft)
    for ob in objs:
        if ob.parent is None:
            ob.location = Vector(loc) + Vector(ob.location)
    root = C.link(bpy.data.objects.new(name, None))
    for ob in objs:
        ob.location = Vector(ob.location) - Vector(loc)
        ob.parent = root
    root.location = loc
    root.rotation_euler = (0, 0, rot)
    root.scale = (s, s, s)
    return root


def farmhouse(name, loc, rot=0.0, lit=False):
    wall = C.m_paint("house_wall", "#EDE3CF", 0.6, grime=0.15)
    roof = C.m_paint("house_roof", "#3E4A5E", 0.55, grime=0.2)
    trim = C.m_paint("house_trim", "#2E5A6E", 0.5)
    glass = C.m_emit("window_lit", "#FFC46A", 5.0) if lit else C.m_simple("window_dark", "#1E2A33", 0.05, coat=1.0)
    w, d, h, hr = 8.0, 6.0, 3.0, 2.2
    objs = []
    prof = [(-w / 2, 0), (w / 2, 0), (w / 2, h), (0, h + hr), (-w / 2, h)]
    verts = [(x, yy, z) for yy in (-d / 2, d / 2) for x, z in prof]
    n = len(prof)
    faces = [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)]
    faces += [tuple(range(n))[::-1], tuple(range(n, 2 * n))]
    objs.append(C.mesh_ob(name + "_body", verts, faces, wall, smooth_=False))
    for sgn in (-1, 1):
        q = [(sgn * (w / 2 + 0.4), -d / 2 - 0.4, h - 0.2), (0, -d / 2 - 0.4, h + hr + 0.1), (0, d / 2 + 0.4, h + hr + 0.1),
             (sgn * (w / 2 + 0.4), d / 2 + 0.4, h - 0.2)]
        o = C.mesh_ob(f"{name}_roof{sgn}", q, [(0, 1, 2, 3) if sgn < 0 else (3, 2, 1, 0)], roof, smooth_=False)
        o.modifiers.new("s", "SOLIDIFY").thickness = 0.1
        objs.append(o)
    for x in (-2.6, -0.9, 0.9, 2.6):    # windows with trim on the front
        for z in (0.9,):
            win = C.mesh_ob(f"{name}_win{x}", [(x - 0.45, -d / 2 - 0.03, z), (x + 0.45, -d / 2 - 0.03, z),
                                                (x + 0.45, -d / 2 - 0.03, z + 1.3), (x - 0.45, -d / 2 - 0.03, z + 1.3)],
                            [(0, 1, 2, 3)], glass, smooth_=False)
            objs.append(win)
            for a, b in (((x - 0.5, -d / 2 - 0.06, z), (x + 0.5, -d / 2 - 0.06, z)),
                         ((x - 0.5, -d / 2 - 0.06, z + 1.35), (x + 0.5, -d / 2 - 0.06, z + 1.35)),
                         ((x - 0.5, -d / 2 - 0.06, z), (x - 0.5, -d / 2 - 0.06, z + 1.35)),
                         ((x + 0.5, -d / 2 - 0.06, z), (x + 0.5, -d / 2 - 0.06, z + 1.35))):
                objs.append(C.tube(f"{name}_wt{len(objs)}", [Vector(a), Vector(b)], [0.05, 0.05], 5, trim))
    # porch roof + posts
    pr = C.mesh_ob(name + "_porch", [(-w / 2, -d / 2, 2.4), (w / 2, -d / 2, 2.4), (w / 2, -d / 2 - 2.0, 2.1),
                                     (-w / 2, -d / 2 - 2.0, 2.1)], [(0, 1, 2, 3)], roof, smooth_=False)
    pr.modifiers.new("s", "SOLIDIFY").thickness = 0.08
    objs.append(pr)
    for x in (-w / 2 + 0.2, -1.4, 1.4, w / 2 - 0.2):
        objs.append(C.tube(f"{name}_post{x}", [Vector((x, -d / 2 - 1.9, 0)), Vector((x, -d / 2 - 1.9, 2.15))],
                           [0.07, 0.07], 6, wall))
    if lit:
        C.point(name + "_porchlight", (Vector(loc) + Vector((0, -d / 2 - 1.2, 2.0))), "#FFB860", 80.0, 0.2)
    root = C.link(bpy.data.objects.new(name, None))
    for ob in objs:
        ob.parent = root
    root.location = loc
    root.rotation_euler = (0, 0, rot)
    return root


def windmill(name, loc, s=1.0):
    met = C.m_metal("mill_metal", "#8A8F96", 0.5)
    objs = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            objs.append(C.tube(f"{name}_leg{sx}{sy}", [Vector((sx * 1.2, sy * 1.2, 0)), Vector((sx * 0.25, sy * 0.25, 9.0))],
                               [0.05, 0.04], 5, met))
    for z in (2.5, 5.0, 7.5):
        k = 1.2 - (1.2 - 0.25) * z / 9.0
        for a, b in (((-k, -k), (k, -k)), ((k, -k), (k, k)), ((k, k), (-k, k)), ((-k, k), (-k, -k))):
            objs.append(C.tube(f"{name}_br{len(objs)}", [Vector((a[0], a[1], z)), Vector((b[0], b[1], z))],
                               [0.025, 0.025], 4, met))
    hub = Vector((0, -0.4, 9.3))
    for k in range(18):
        a = 2 * math.pi * k / 18
        d = Vector((math.cos(a), 0, math.sin(a)))
        q = [hub + d * 0.5 + Vector((0, 0, 0)), hub + d * 2.0, hub + d * 2.0 + Vector((math.sin(a), 0, -math.cos(a))) * 0.35,
             hub + d * 0.5 + Vector((math.sin(a), 0, -math.cos(a))) * 0.12]
        objs.append(C.mesh_ob(f"{name}_blade{k}", q, [(0, 1, 2, 3)], met, smooth_=False))
    tail = C.mesh_ob(name + "_tail", [(0, 0.2, 9.1), (0, 2.6, 9.4), (0, 2.6, 10.4), (0, 0.2, 9.6)], [(0, 1, 2, 3)], met,
                     smooth_=False)
    objs.append(tail)
    root = C.link(bpy.data.objects.new(name, None))
    for ob in objs:
        ob.parent = root
    root.location = loc
    root.scale = (s, s, s)
    return root


def tractor(name, loc, rot=0.0, spray=False):
    body = C.m_paint("tractor_red", "#C8372A", 0.4, chip=0.15, grime=0.3)
    dark = C.m_rubber("tyre")
    met = C.m_metal("tractor_metal", "#3A3E44", 0.4)
    glass = C.m_glass("cab_glass", "#BFD8E0", 0.25)
    objs = []
    hood = FL.icosphere(name + "_hood", 1.0, 3, body)
    hood.scale = (0.55, 1.2, 0.5)
    hood.location = (0, -1.0, 1.35)
    objs.append(hood)
    cab = FL.icosphere(name + "_cabin", 1.0, 2, glass)
    cab.scale = (0.75, 0.75, 0.85)
    cab.location = (0, 0.4, 2.2)
    objs.append(cab)
    roofc = FL.icosphere(name + "_roof", 1.0, 2, body)
    roofc.scale = (0.85, 0.9, 0.08)
    roofc.location = (0, 0.4, 3.05)
    objs.append(roofc)
    for sx in (-1, 1):
        for (y, r, wdt) in ((-1.5, 0.55, 0.35), (0.7, 0.95, 0.5)):
            t = C.lathe(f"{name}_tyre{sx}{y}", [(r * 0.55, -wdt / 2), (r, -wdt / 2 + 0.05), (r, wdt / 2 - 0.05),
                                               (r * 0.55, wdt / 2)], 32, dark)
            t.rotation_euler = (0, math.pi / 2, 0)
            t.location = (sx * (0.9 if y > 0 else 0.7), y, r)
            objs.append(t)
            hb = C.lathe(f"{name}_hub{sx}{y}", [(0.0, -wdt / 2 + 0.02), (r * 0.55, -wdt / 2 + 0.02), (r * 0.55, wdt / 2 - 0.02),
                                               (0.0, wdt / 2 - 0.02)], 24, C.m_paint("hub_yel", "#E8B030", 0.4))
            hb.rotation_euler = (0, math.pi / 2, 0)
            hb.location = t.location
            objs.append(hb)
    stack = C.tube(name + "_stack", [Vector((0.35, -1.4, 1.6)), Vector((0.35, -1.4, 2.9))], [0.06, 0.05], 8, met)
    objs.append(stack)
    if spray:
        tank = FL.icosphere(name + "_tank", 1.0, 2, C.m_paint("tank_white", "#E9E6DE", 0.35))
        tank.scale = (0.8, 0.9, 0.6)
        tank.location = (0, 2.2, 1.4)
        objs.append(tank)
        objs.append(C.tube(name + "_boom", [Vector((-7.0, 2.9, 1.1)), Vector((7.0, 2.9, 1.1))], [0.05, 0.05], 6, met))
    root = C.link(bpy.data.objects.new(name, None))
    for ob in objs:
        ob.parent = root
    root.location = loc
    root.rotation_euler = (0, 0, rot)
    return root


def bat_house(name, loc, rot=0.0):
    wood = C.m_paint("bathouse_wood", "#7A5A3E", 0.75, grime=0.3)
    b = FL.icosphere(name, 1.0, 1, wood)
    b.data = C.mesh_ob(name + "_m", [(-0.3, -0.05, 0), (0.3, -0.05, 0), (0.3, -0.05, 0.75), (0, -0.05, 0.9),
                                     (-0.3, -0.05, 0.75)], [(0, 1, 2, 3, 4)], wood, smooth_=False).data
    b.modifiers.new("s", "SOLIDIFY").thickness = 0.12
    b.location = loc
    b.rotation_euler = (0, 0, rot)
    return b


def fence(name, a, b, n=14):
    wood = FL.m_bark("fence_wood", "#7A6A58", 10.0)
    a, b = Vector(a), Vector(b)
    objs = []
    for k in range(n + 1):
        p = a.lerp(b, k / n)
        objs.append(C.tube(f"{name}_p{k}", [p, p + Vector((0, 0, 1.2))], [0.06, 0.05], 6, wood))
    wire = C.m_metal("wire", "#9A9A9A", 0.4)
    for z in (0.5, 0.85, 1.15):
        objs.append(C.tube(f"{name}_w{z}", [a + Vector((0, 0, z)), b + Vector((0, 0, z))], [0.006, 0.006], 4, wire))
    return objs


# ------------------------------------------------------------------ ENV_FARM
def _seg_dist(px, py, x0, y0, x1, y1):
    dx, dy = x1 - x0, y1 - y0
    L2 = dx * dx + dy * dy
    u = 0.0 if L2 < 1e-9 else max(0.0, min(1.0, ((px - x0) * dx + (py - y0) * dy) / L2))
    return math.hypot(px - (x0 + u * dx), py - (y0 + u * dy)), u


def clear_factor(x, y, clear):
    """0 inside any clearing (segments (x0, y0, x1, y1, w0, w1) with widths interpolated along them), else 1.
    Used to keep a camera's line of sight and the actors' spots free of crop plants."""
    for (x0, y0, x1, y1, w0, w1) in clear or ():
        d, u = _seg_dist(x, y, x0, y0, x1, y1)
        if d < w0 + (w1 - w0) * u:
            return 0.0
    return 1.0


def env_farm(state="dusk", detail=1.0, crop="corn", sprayer=False, bathouse=False, clear=None):
    E = Env("farm")
    rnd = random.Random(21)
    lit = state in ("dusk", "night")
    if state == "day":
        C.world_sky([(0.0, "#CFE4F2"), (0.1, "#9CCBEA"), (0.4, "#5C9FDA"), (1.0, "#2E6CC0")], strength=1.0,
                    sun_dir=(-0.6, -0.5, 0.55), sun_col="#FFF2D8", sun_glow=0.3,
                    clouds=("#FFFFFF", 0.42, 2.5, "#B8C8DA"), ground="#5A5A3A", ambient=("#A8C4E0", 1.1))
        E.key = ((-0.6, -0.5, 0.55), "#FFF0D6", 4.5)
        E.fill = ("#9AC0E8", 0.8)
        E.rim = ("#FFF6E0", 0.4)
        haze = ("#BFD8EA", 0.0016)
    elif state == "dusk":
        C.world_sky([(0.0, "#FFB070"), (0.05, "#F27C6A"), (0.14, "#B85A8C"), (0.32, "#5A4A9A"), (0.6, "#2A3072"),
                     (1.0, "#141A44")], strength=0.95, sun_dir=(0.7, 1.0, 0.02), sun_col="#FF9A62", sun_glow=1.1,
                    clouds=("#F59A8A", 0.36, 2.4, "#5A3E70"), ground="#3A3040", stars=0.3,
                    moon=((-0.6, 1.0, 0.5), 0.9, "#FFF4D8"), ambient=("#8A80C0", 1.2))
        bpy.context.scene.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 1.5
        E.key = ((1.0, 0.25, 0.08), "#FF9A62", 3.2)
        E.fill = ("#7A6AC0", 0.7)
        E.rim = ("#FFB078", 1.0)
        haze = ("#C88AA0", 0.003)
    else:
        C.world_sky([(0.0, "#2E3E6A"), (0.12, "#1E2A56"), (0.45, "#0E1636"), (1.0, "#060A1A")], strength=0.9,
                    stars=1.4, moon=((-0.6, 1.0, 0.5), 1.3, "#FFF4D8"), ground="#0A0C10", ambient=("#2A3C72", 0.9))
        E.key = ((-0.6, 1.0, 0.5), "#AFC2FF", 1.1)
        E.fill = ("#2A3A7A", 0.7)
        E.rim = ("#8AA0FF", 0.8)
        haze = ("#2A3A6A", 0.003)

    def h(x, y):
        r = math.hypot(x, y)
        return 0.6 * math.sin(x / 40.0) * math.cos(y / 33.0) + max(0.0, r - 150.0) * 0.06 + \
            4.0 * math.sin(x / 70.0 + 1.0) * _sstep(150.0, 300.0, r)
    soil = FL.m_ground("farm_ground", [("#6A5034", 0.2), ("#8A6A44", 0.45), ("#7A8A44", 0.65), ("#9AA052", 0.85)],
                       0.1, 0.5)
    near = terrain("farm_near", 160, 200, h, soil)
    far = terrain("farm_far", 1200, 140, h, soil, hole=lambda x, y: abs(x) < 78 and abs(y) < 78, z_off=-0.05)
    E.ground = [near, far]
    barn("barn", (14.0, 24.0, h(14, 24) - 0.05), math.radians(-18))
    farmhouse("house", (-14.0, 30.0, h(-14, 30) - 0.05), math.radians(12), lit=lit)
    windmill("mill", (2.0, 34.0, h(2, 34)), 1.0)
    silo_m = C.m_metal("silo", "#A8AEB4", 0.35)
    silo = C.lathe("silo", [(3.0, 0), (3.0, 12.0), (2.4, 13.6), (0.2, 14.6)], 40, silo_m, close_top=True)
    silo.location = (24.0, 30.0, h(24, 30))
    for ob in fence("fence", (-30, 8, 0.0), (30, 8, 0.0), 30):
        pass
    if bathouse:
        bat_house("bathouse", (8.3, 16.2, 3.2), math.radians(-18))
    # crop rows
    leaf = FL.m_leaf("corn_leaf", "#4E8E32" if state != "day" else "#6FA83A", 0.1, 0.55, 0.3, tip="#A8B04E")
    stalk = FL.m_leaf("corn_stalk", "#8AA04A", 0.06)
    tas = C.m_simple("tassel", "#D8B860", 0.6, sss=0.2)
    ear = FL.m_leaf("corn_ear", "#9AB060", 0.06, 0.6)
    corn = lib_collection("L_corn", [lambda k: FL.corn_plant(f"cp{k}", leaf, stalk, tas, ear, 2.1 + 0.15 * k, seed=k)
                                     for k in range(3)])
    cot_leaf = FL.m_leaf("cotton_leaf", "#4E7A34", 0.08, 0.55, 0.3)
    boll = C.m_simple("boll", "#F7F4EC", 0.8, sss=0.4)
    cotton = lib_collection("L_cotton", [lambda k: FL.cotton_plant(f"ct{k}", cot_leaf, boll, stalk, 0.9, seed=k)
                                         for k in range(3)])
    rows = FL.grid("rows", 120, 70, 120, 70, None)
    rows.location = (0, -30, 0)
    rows.data.materials.append(soil)
    for v in rows.data.vertices:
        v.co.z = h(v.co.x, v.co.y - 30) - 0.02
    # rows.matrix_world may not be updated yet here: convert the mask point to world y explicitly
    y_off = -30.0 - rows.matrix_world.translation.y
    FL.vgroup_from_fn(rows, "rowmask", lambda p: (1.0 if (p.x % 1.4) < 0.35 else 0.0) *
                      (0.0 if (abs(p.x + 2.0) < 1.7 and p.y > -24.0) else 1.0) *
                      (clear_factor(p.x, p.y + y_off, clear) if crop == "corn" else 1.0))
    FL.scatter(rows, corn if crop == "corn" else cotton, (16.0 if crop == "corn" else 18.0) * detail, seed=11,
               scale=(0.85, 1.15), mask="rowmask", name="sc_crop", rot_tilt=0.08)
    # grass verge and wildflowers
    grass, flowers = veg_hill()
    FL.vgroup_from_fn(near, "verge", lambda p: (1.0 if p.y > 4.0 or p.y < -66 or abs(p.x) > 60 else 0.0))
    FL.scatter(near, grass, 2.0 * detail, seed=3, scale=(0.6, 1.1), mask="verge", name="sc_grass")
    FL.scatter(near, flowers, 0.8 * detail, seed=4, scale=(0.8, 1.2), mask="verge", name="sc_flw")
    oak_t = FL.m_bark("oak_bark", "#5A4A40", moss="#7A8A4A")
    oak_l = FL.m_canopy("farm_leaf", "#2E4A24", 0.12, 7.0, 0.25)
    oak_c = FL.m_leaf("farm_lf", "#5E8A3A", 0.14, 0.5, 0.35, scale=6.0)
    oaks = [prefab(FL.tree(f"fo{k}", "oak", seed=30 + k, h=rnd.uniform(6, 9), crown=rnd.uniform(3, 4.5),
                           trunk_m=oak_t, leaf_m=oak_l, leaves=(oak_c, "broad", 0.14, 80.0 * detail)),
                   f"fo{k}", f"C_fo{k}") for k in range(2)]
    for k in range(int(90 * detail)):
        a = rnd.uniform(0.15, math.pi - 0.15)
        rr = rnd.uniform(50.0, 260.0)
        x, y = math.cos(a) * rr * 1.4, 10 + math.sin(a) * rr
        place(oaks[k % 2], (x, y, h(x, y)), rnd.uniform(0, 6.28), rnd.uniform(0.7, 1.3), f"ftree{k}")
    for k, p in enumerate(((-22, 22), (-9, 40), (30, 18))):
        place(oaks[k % 2], (p[0], p[1], h(*p)), k, 1.2, f"ytree{k}")
    if sprayer:
        tractor("tractor", (-2.0, -14.0, h(-2, -14)), math.radians(90), spray=True)
    C.volume_fog(haze[1], haze[0], 0.3, size=700.0, center=(0, 0, 10), height=30.0)
    E.marks = dict(farmer=Vector((-1.5, -2.0, h(-1.5, -2.0))), pip=Vector((1.6, -2.6, h(1.6, -2.6))),
                   field=Vector((0, -20, 2.0)), barn=Vector((14, 24, 5)), house=Vector((-14, 30, 3)),
                   bathouse=Vector((8.3, 16.0, 3.6)), tractor=Vector((-2.0, -14.0, 1.5)))
    return E


# ------------------------------------------------------------------ ENV_AGAVE
def env_agave(state="sunset", detail=1.0, stalks=True):
    E = Env("agave")
    rnd = random.Random(31)
    if state == "sunset":
        C.world_sky([(0.0, "#FFC27A"), (0.05, "#FF9A5C"), (0.15, "#E0607A"), (0.35, "#8A4A8E"), (0.65, "#3C2F72"),
                     (1.0, "#1A1C48")], strength=1.1, sun_dir=(-1.0, 0.35, 0.07), sun_col="#FFD090", sun_glow=1.3,
                    clouds=("#FFB28A", 0.4, 2.0, "#8A4A70"), ground="#4A2A20", ambient=("#A08AB8", 1.1))
        E.key = ((-1.0, 0.35, 0.1), "#FFA060", 5.5)
        E.fill = ("#8A7AC0", 0.6)
        E.rim = ("#FFC27A", 1.0)
        haze = ("#F2A07A", 0.003)
    elif state == "blue":
        C.world_sky([(0.0, "#F2A47A"), (0.05, "#C8789A"), (0.2, "#5A5AA8"), (0.5, "#2A3478"), (1.0, "#10164A")],
                    strength=0.9, sun_dir=(-0.4, 1.0, -0.03), sun_col="#FF9A7A", sun_glow=0.5, stars=0.6,
                    moon=((0.5, 1.0, 0.35), 1.2, "#FFF6E0"), ground="#1A1420", ambient=("#6A6AB8", 1.0))
        E.key = ((0.5, 1.0, 0.4), "#B8C4FF", 1.2)
        E.fill = ("#5A5AB0", 0.8)
        E.rim = ("#F2A47A", 0.7)
        haze = ("#7A6AB0", 0.003)
    else:
        C.world_sky([(0.0, "#2E3A6A"), (0.12, "#1A2452"), (0.45, "#0C1234"), (1.0, "#05081A")], strength=0.9,
                    stars=1.5, moon=((0.5, 1.0, 0.35), 1.4, "#FFF6E0"), ground="#05060C", ambient=("#2A3C72", 0.9))
        E.key = ((0.5, 1.0, 0.4), "#AFC0FF", 1.1)
        E.fill = ("#2A3A7A", 0.7)
        E.rim = ("#8AA0FF", 0.8)
        haze = ("#2A3A6A", 0.003)

    def h(x, y):
        r = math.hypot(x, y)
        return 1.2 * math.sin(x / 25.0) * math.cos(y / 31.0) + 0.8 * math.sin((x + y) / 15.0) + \
            _sstep(120.0, 260.0, r) * (30.0 + 25.0 * math.sin(x / 60.0))
    soil = FL.m_ground("agave_soil", [("#6A2E1E", 0.2), ("#9A4A2E", 0.45), ("#B05A34", 0.65), ("#8A6A3A", 0.9)],
                       0.12, 0.6)
    near = terrain("agave_near", 160, 200, h, soil)
    far = terrain("agave_far", 1400, 160, h, FL.m_ground("agave_hills", [("#3A4A3A", 0.3), ("#5A6A40", 0.6),
                                                                         ("#7A5A3A", 0.9)], 0.02, 0.4),
                  hole=lambda x, y: abs(x) < 78 and abs(y) < 78, z_off=-0.05)
    E.ground = [near, far]
    leaf = FL.m_leaf("agave_leaf", "#4E8C8E", 0.06, 0.4, 0.15, waxy=0.25, scale=8.0, tip="#2E5A56")
    agv = lib_collection("L_agave", [lambda k: FL.agave(f"ag{k}", leaf, 36 + k * 4, 1.5 + 0.2 * k, seed=k)
                                     for k in range(3)])
    rows = FL.grid("agave_rows", 150, 150, 150, 150, soil)
    for v in rows.data.vertices:
        v.co.z = h(v.co.x, v.co.y) - 0.01
    FL.vgroup_from_fn(rows, "rowmask", lambda p: (1.0 if (p.x % 2.6) < 0.45 else 0.0) *
                      (0.0 if (abs(p.x) < 4.0 and -14 < p.y < 6) else 1.0))
    FL.scatter(rows, agv, 6.0 * detail, seed=7, scale=(0.85, 1.15), mask="rowmask", name="sc_agave", rot_tilt=0.05,
               min_dist=1.5)
    stalk_m = FL.m_leaf("quiote", "#7A8A4A", 0.08, 0.6)
    flw = FL.m_canopy("agave_flower", "#F2C43A", 0.12, 30.0, 0.4)
    E.stalks = []
    E.flower_clusters = []
    if stalks:
        for k, (x, y) in enumerate(((-2.0, 2.0), (6.0, 9.0), (-11.0, 14.0), (14.0, 22.0), (-20.0, 30.0), (24.0, 38.0),
                                    (2.0, 26.0), (-7.0, 44.0))):
            cl = []
            for ob in FL.agave_stalk(f"stk{k}", stalk_m, flw, rnd.uniform(5.0, 7.0), seed=k, clusters=cl, hero=(k == 0)):
                ob.location = Vector(ob.location) + Vector((x, y, h(x, y)))
            E.flower_clusters.append([c + Vector((x, y, h(x, y))) for c in cl])
            ag = place(agv, (x, y, h(x, y)), rnd.uniform(0, 6.28), 1.2, f"agb{k}")
            E.stalks.append(Vector((x, y, h(x, y))))
    rock_m = FL.m_rock("volcanic", "#6A5A52", "#3A302C", strata=False, lichen=("#C8A23A", "#8AA05A"))
    for k in range(18):
        x, y = rnd.uniform(-60, 60), rnd.uniform(-10, 70)
        b = FL.rock(f"ark{k}", rnd.uniform(0.3, 1.1), rock_m, seed=k)
        b.location = (x, y, h(x, y) - 0.1)
    grass, flowers = veg_hill()
    FL.vgroup_from_fn(near, "verge", lambda p: 1.0 if abs(p.x) > 70 or p.y > 72 else 0.15)
    FL.scatter(near, grass, 1.0 * detail, seed=3, scale=(0.5, 1.0), mask="verge", name="sc_grass")
    C.volume_fog(haze[1], haze[0], 0.3, size=900.0, center=(0, 0, 10), height=35.0)
    E.marks = dict(pip=Vector((-1.5, -9.0, h(-1.5, -9.0))), hero_stalk=E.stalks[0] if E.stalks else Vector((0, 0, 0)),
                   field=Vector((0, 20, 1.0)))
    return E


# ------------------------------------------------------------------ ENV_TROPIC
def env_tropic(state="dawn", detail=1.0, scene="fig"):
    E = Env("tropic")
    rnd = random.Random(41)
    if state == "dawn":
        C.world_sky([(0.0, "#FFE0B0"), (0.08, "#FFC89A"), (0.25, "#9AD0E0"), (0.6, "#5AA8D8"), (1.0, "#3A7AC0")],
                    strength=1.1, sun_dir=(0.5, 1.0, 0.18), sun_col="#FFE2A0", sun_glow=1.0,
                    clouds=("#FFF2E0", 0.35, 2.0, "#C8B8B0"), ground="#2A3A20", ambient=("#A8C8B0", 1.2))
        E.key = ((0.5, 1.0, 0.2), "#FFD58A", 4.5)
        E.fill = ("#9AD0C8", 0.8)
        E.rim = ("#FFE0A0", 1.0)
        haze = ("#F2E8C8", 0.02)
    else:   # night (durian orchard)
        C.world_sky([(0.0, "#1E3A4A"), (0.15, "#13283A"), (0.5, "#0A1422"), (1.0, "#050A12")], strength=0.9,
                    stars=1.2, moon=((-0.3, 1.0, 0.6), 1.2, "#FFF4DE"), ground="#05080A", ambient=("#1E4A5A", 1.0))
        E.key = ((-0.3, 1.0, 0.6), "#A8C8FF", 1.4)
        E.fill = ("#1E5A5A", 0.7)
        E.rim = ("#FFC27A", 0.9)
        haze = ("#2A5A5A", 0.012)

    def h(x, y):
        r = math.hypot(x, y)
        return 0.8 * math.sin(x / 13.0) * math.cos(y / 17.0) + _sstep(60.0, 200.0, r) * 25.0
    soil = FL.m_ground("tropic_soil", [("#3A2A1A", 0.2), ("#5A3E24", 0.4), ("#3E5A24", 0.6), ("#2E4A1E", 0.9)],
                       0.15, 0.3, wet=0.15)
    near = terrain("tropic_near", 120, 160, h, soil)
    far = terrain("tropic_far", 1000, 120, h, FL.m_ground("tropic_hills", [("#2A4A2A", 0.4), ("#3E6A30", 0.9)], 0.03),
                  hole=lambda x, y: abs(x) < 58 and abs(y) < 58, z_off=-0.05)
    E.ground = [near, far]
    bark = FL.m_bark("fig_bark", "#7A6A5A", 5.0, moss="#5A7A3A")
    can = FL.m_canopy("fig_leaf", "#3E7A34", 0.14, 6.0, 0.35, fruit="#E0702E" if scene == "fig" else None)
    can2 = FL.m_canopy("jungle_leaf", "#2E6A3A", 0.16, 8.0, 0.35)
    can3 = FL.m_canopy("jungle_leaf2", "#5A8A2E", 0.14, 8.0, 0.35, flower="#F0E0B0" if scene == "durian" else None,
                       flower_amt=0.6)
    palm_t = FL.m_bark("palm_bark", "#8A7A62", 8.0)
    palm_l = FL.m_leaf("palm_leaf", "#4E8A3A", 0.1, 0.5, 0.3)
    ban_l = FL.m_leaf("banana_leaf", "#6AA83E", 0.08, 0.45, 0.35, waxy=0.2)
    ban_s = FL.m_leaf("banana_stem", "#7A9A4A", 0.06)
    fern_m = FL.m_leaf("fern", "#4E8A34", 0.1, 0.55, 0.3)
    tl1 = FL.m_leaf("trop_lf1", "#3E8A34", 0.14, 0.45, 0.4, scale=6.0)
    tl2 = FL.m_leaf("trop_lf2", "#6AA83A", 0.14, 0.45, 0.4, scale=6.0)
    jt = [prefab(FL.tree(f"jt{k}", "oak", seed=50 + k, h=rnd.uniform(10, 15), crown=rnd.uniform(4, 6), trunk_m=bark,
                         leaf_m=(can2, can3)[k % 2], leaves=((tl1, tl2)[k % 2], "long", 0.32, 40.0 * detail)),
                 f"jt{k}", f"C_jt{k}") for k in range(3)]
    jt_far = [prefab(FL.tree(f"jtf{k}", "oak", seed=70 + k, h=13, crown=5, trunk_m=bark, leaf_m=(can2, can3)[k % 2]),
                     f"jtf{k}", f"C_jtf{k}") for k in range(2)]
    palms = [prefab(FL.tree(f"pl{k}", "palm", seed=60 + k, h=rnd.uniform(7, 10), trunk_m=palm_t, leaf_m=palm_l,
                            lean=rnd.uniform(-1, 1)), f"pl{k}", f"C_pl{k}") for k in range(2)]
    bans = [prefab(FL.banana(f"bn{k}", ban_l, ban_s, seed=k), f"bn{k}", f"C_bn{k}") for k in range(2)]
    ferns = lib_collection("L_fern", [lambda k: FL.fern(f"fn{k}", fern_m, seed=k, s=0.8 + 0.2 * k) for k in range(3)])
    E.marks = {}
    if scene in ("fig", "durian"):
        figl = FL.m_leaf("fig_lf", "#3E8A30", 0.14, 0.4, 0.4, scale=6.0)
        hero = FL.tree("hero", "fig", seed=77, h=13.0, crown=6.5, trunk_m=bark, leaf_m=can if scene == "fig" else can3,
                       leaves=(figl, "broad", 0.24, 70.0 * detail))
        if scene == "durian":       # keep the big tree clear of the low durian branch and the camera
            for ob in hero:
                if ob.parent is None:
                    ob.location = Vector(ob.location) + Vector((9.0, 11.0, 0.0))
        E.marks["hero"] = Vector((0, 0, 9.0))
    for k in range(int(60 * detail)):
        a = rnd.uniform(0, 6.28)
        rr = rnd.uniform(16.0, 55.0)
        x, y = math.cos(a) * rr, math.sin(a) * rr + 10
        if scene == "clearing" and math.hypot(x, y - 6) < 26:
            continue
        place(jt[k % 3], (x, y, h(x, y)), rnd.uniform(0, 6.28), rnd.uniform(0.8, 1.3), f"jtree{k}")
    for k in range(int(26 * detail)):
        x, y = rnd.uniform(-40, 40), rnd.uniform(-5, 50)
        if scene == "clearing" and math.hypot(x, y - 6) < 22:
            continue
        place((palms + bans)[k % 4], (x, y, h(x, y)), rnd.uniform(0, 6.28), rnd.uniform(0.8, 1.2), f"pb{k}")
    for k in range(int(200 * detail)):
        a = rnd.uniform(0, 6.28)
        rr = rnd.uniform(70.0, 300.0)
        x, y = math.cos(a) * rr, math.sin(a) * rr
        place(jt_far[k % 2], (x, y, h(x, y)), rnd.uniform(0, 6.28), rnd.uniform(1.0, 1.8), f"ftr{k}")
    if scene == "clearing":
        stump_m = FL.m_bark("stump", "#6A5440", 6.0)
        for k in range(14):
            x, y = rnd.uniform(-16, 16), rnd.uniform(-6, 20)
            C.tube(f"stump{k}", [Vector((x, y, h(x, y) - 0.1)), Vector((x, y, h(x, y) + rnd.uniform(0.3, 0.7)))],
                   [rnd.uniform(0.25, 0.45), 0.25], 10, stump_m)
        sl = FL.m_leaf("seedling", "#7ABA3E", 0.1, 0.5, 0.35)
        E.seedlings = []
        for k in range(26):
            x, y = rnd.uniform(-12, 12), rnd.uniform(-6, 16)
            objs = FL.seedling(f"sd{k}", sl, FL.m_leaf("sd_stem", "#6A7A3A", 0.05), rnd.uniform(0.25, 0.5), seed=k)
            root = C.link(bpy.data.objects.new(f"seedroot{k}", None))
            for ob in objs:
                ob.parent = root
            root.location = (x, y, h(x, y))
            E.seedlings.append(root)
        E.marks["clearing"] = Vector((0, 4, 0.5))
    FL.vgroup_from_fn(near, "under", lambda p: 1.0 if scene != "clearing" or math.hypot(p.x, p.y - 6) > 20 else 0.05)
    FL.scatter(near, ferns, 0.5 * detail, seed=9, scale=(0.7, 1.4), mask="under", name="sc_fern")
    if state == "night":
        for k, p in enumerate(((-4, 2, 2.2), (5, 6, 2.0))):
            C.point(f"lantern{k}", p, "#FFB060", 60.0, 0.15)
            lm = FL.icosphere(f"lantern_m{k}", 0.12, 2, C.m_emit("lantern", "#FFC070", 8.0))
            lm.location = p
    C.volume_fog(haze[1], haze[0], 0.6, size=300.0, center=(0, 10, 6), height=12.0)
    return E


# ------------------------------------------------------------------ small environments
def env_studio(top="#2A1E5A", bottom="#0E6A78"):
    E = Env("studio")
    C.world_sky([(0.0, bottom), (0.5, "#4A3A8A"), (1.0, top)], strength=0.6)
    back = FL.grid("backdrop", 40, 40, 2, 2, C.m_simple("backdrop", "#1C2A4A", 0.9))
    back.rotation_euler = (math.radians(90), 0, 0)
    back.location = (0, 6, 0)
    E.key = ((-0.6, -0.8, 0.8), "#FFE6CC", 3.0)
    E.marks = dict(center=Vector((0, 0, 1.5)))
    return E


def env_sky(state="night", moon_scene=False, moon_tex=False):
    E = Env("sky")
    if moon_scene or moon_tex:      # textured moon, moonlit cloud wisps (ridge + trees only for moon_scene)
        C.world_sky([(0.0, "#3A4A7A"), (0.1, "#22305E"), (0.4, "#121A3C"), (1.0, "#070A1C")], strength=0.9,
                    stars=1.8, moon=((0.2, 1.0, 0.25), 2.0, "#FFF6DE", True),
                    ground="#05060C" if moon_scene else "#141C30",      # far moonlit land, not a black void
                    clouds=("#8A9AC8", 0.42, 2.4, "#1A2244"))
    else:
        C.world_sky([(0.0, "#3A4A7A"), (0.1, "#22305E"), (0.4, "#121A3C"), (1.0, "#070A1C")], strength=0.9,
                    stars=1.8, moon=((0.2, 1.0, 0.25), 2.0, "#FFF6DE"), ground="#05060C",
                    clouds=("#4A5A86", 0.3, 1.6, "#161C34"))
    ground = FL.grid("night_ground", 6000, 6000, 60, 60, FL.m_ground("night_fields", [("#1A2A2A", 0.3),
                                                                                         ("#2A3A30", 0.6),
                                                                                         ("#3A4A3A", 0.9)], 0.002))
    ground.location = (0, 0, -600)
    lights = C.m_emit("farm_lights", "#FFC070", 40.0)
    rnd = random.Random(3)
    for k in range(220):
        x, y = rnd.uniform(-2500, 2500), rnd.uniform(200, 3000)
        b = FL.icosphere(f"fl{k}", rnd.uniform(2.0, 4.0), 1, lights)
        b.location = (x, y, -598)
    for t in range(4):                      # small towns: clusters of lights
        cx, cy = rnd.uniform(-1500, 1500), rnd.uniform(600, 2600)
        for k in range(90):
            b = FL.icosphere(f"town{t}_{k}", rnd.uniform(1.5, 3.0), 1, lights)
            b.location = (cx + rnd.gauss(0, 60), cy + rnd.gauss(0, 60), -598)
    if moon_tex and not moon_scene:
        # high-altitude view: distant farm and town lights sprinkle the horizon band (sized by distance)
        for k in range(420):
            a = math.radians(rnd.uniform(-45.0, 45.0))
            d = 3500.0 * (1.0 + rnd.random() ** 1.5 * 4.0)
            if k % 7 == 0:          # a few clustered towns
                d0, a0 = d, a
            if k % 7 in (1, 2, 3):
                d, a = d0 + rnd.gauss(0, 150), a0 + rnd.gauss(0, 0.004)
            b = FL.icosphere(f"far{k}", d * rnd.uniform(0.0009, 0.0016), 1, lights)
            b.location = (d * math.sin(a), d * math.cos(a), -598)
    if moon_scene:
        # a dark ridge line with gnarled bare trees, back-lit by the moon (silhouettes frame the chapter shots)
        sil = C.m_simple("silhouette", "#06070E", 0.9)

        def ridge_h(x, wy):     # world y; rises out of view to a wavy crest ~230 m away
            return -60.0 + _sstep(150.0, 230.0, wy) * (84.0 + 6.0 * math.sin(x / 37.0) + 3.0 * math.sin(x / 13.0 + 1.0))
        haze = C.m_simple("ridge_haze", "#151C36", 0.95)       # distant ridge a touch lighter: aerial perspective
        ridge = terrain("ridge", 900, 300, lambda x, y: ridge_h(x, y + 350.0), haze)
        ridge.location = (0, 350, 0)
        rnd2 = random.Random(9)
        trees = [(27.0, 48.0, 22.0, -9.0), (-6.0, 240.0, 16.0, None), (2.0, 250.0, 12.0, None),
                 (17.0, 260.0, 14.0, None), (-14.0, 245.0, 18.0, None), (35.0, 236.0, 13.0, None)]
        for k, (yaw, dist, hh, z0) in enumerate(trees):
            a = math.radians(yaw)
            x, y = dist * math.sin(a), dist * math.cos(a)
            z = z0 if z0 is not None else ridge_h(x, y) - 1.0
            for ob in FL.bare_tree(f"bare{k}", sil, h=hh, seed=11 + k, depth=5 if z0 is not None else 3,
                                   lean=rnd2.uniform(-0.3, 0.3)):
                ob.location = Vector(ob.location) + Vector((x, y, z))
    E.key = ((0.2, 1.0, 0.25), "#B8C8FF", 1.2)
    E.marks = dict(center=Vector((0, 30, 0)))
    return E


def env_mine():
    E = Env("mine")
    C.world_sky([(0.0, "#FFC08A"), (0.06, "#F08A7A"), (0.2, "#8A6AA8"), (0.5, "#3A4A8A"), (1.0, "#1A2454")],
                strength=1.0, sun_dir=(-0.8, 1.0, 0.05), sun_col="#FFB880", sun_glow=1.0,
                clouds=("#F6A890", 0.38, 2.2, "#5A4A7A"), ambient=("#9A8AB8", 1.2))

    def h(x, y):
        return 8.0 * _sstep(-5.0, 25.0, y) + 2.0 * math.sin(x / 9.0) + _sstep(60, 200, math.hypot(x, y)) * 30
    g = FL.m_ground("mine_ground", [("#5A3A2A", 0.25), ("#4E7A30", 0.5), ("#6A9A3A", 0.8)], 0.12, 0.5,
                    slope_rock="#8A6A52")
    near = terrain("mine_near", 160, 180, h, g)
    rock_m = FL.m_rock("mine_rock", "#9A7462", "#4A3A32", lichen=("#C89A3A", "#7A9A4A"), scale=0.8)
    face = meshio.load(os.path.join(MODELS, "env", "cave_mouth.bin"), "mine_face", rock_m, decimate=1.0)
    face.scale = (0.42, 0.42, 0.42)
    face.location = (0, 0.6, h(0, 2.0) - 0.4)
    dark = C.m_simple("mine_dark", "#030202", 1.0)
    hole = FL.icosphere("mine_void", 1.6, 2, dark)
    hole.scale = (1.3, 2.4, 1.1)
    hole.location = (0, 4.6, h(0, 2.0) + 0.3)
    timber = FL.m_bark("timber", "#6A4A30", 8.0)
    z0 = h(0, 2.0) - 0.3
    for a, b in (((-1.3, 1.6, z0), (-1.3, 1.6, z0 + 2.6)), ((1.3, 1.6, z0), (1.3, 1.6, z0 + 2.6)),
                 ((-1.6, 1.6, z0 + 2.5), (1.6, 1.6, z0 + 2.5)), ((-1.3, 2.6, z0), (-1.3, 2.6, z0 + 2.4)),
                 ((1.3, 2.6, z0), (1.3, 2.6, z0 + 2.4)), ((-1.5, 2.6, z0 + 2.35), (1.5, 2.6, z0 + 2.35))):
        C.tube(f"timber{a}{b}", [Vector(a), Vector(b)], [0.13, 0.13], 6, timber)
    ban_l = FL.m_leaf("banana_leaf", "#6AA83E", 0.08, 0.45, 0.35, waxy=0.2)
    ban_s = FL.m_leaf("banana_stem", "#7A9A4A", 0.06)
    rnd = random.Random(5)
    bans = [prefab(FL.banana(f"mb{k}", ban_l, ban_s, seed=k), f"mb{k}", f"C_mb{k}") for k in range(2)]
    for k in range(30):
        x, y = rnd.uniform(-30, 30), rnd.uniform(-20, 40)
        if abs(x) < 6 and -10 < y < 6:
            continue
        place(bans[k % 2], (x, y, h(x, y)), rnd.uniform(0, 6.28), rnd.uniform(0.8, 1.3), f"mban{k}")
    grass, flowers = veg_hill()
    FL.vgroup_from_fn(near, "g", lambda p: 1.0)
    FL.scatter(near, grass, 1.5, seed=2, scale=(0.6, 1.1), mask="g", name="sc_g")
    C.volume_fog(0.003, "#F2B090", 0.3, size=500.0, center=(0, 0, 10), height=20.0)
    E.key = ((-1.0, -0.35, 0.12), "#FFA062", 4.5)
    E.ground = [near]
    E.marks = dict(mouth=Vector((0, 2.0, h(0, 2.0) + 1.0)))
    return E


def env_wind():
    E = Env("wind")
    C.world_sky([(0.0, "#FFC27A"), (0.05, "#FF9060"), (0.16, "#D85A7A"), (0.35, "#7A4A8E"), (1.0, "#1C1D47")],
                strength=1.0, sun_dir=(0.2, 1.0, 0.04), sun_col="#FFD08A", sun_glow=1.5,
                clouds=("#FFB28A", 0.4, 2.0, "#7A4A70"))

    def h(x, y):
        return 12.0 * math.exp(-((y - 40) / 30.0) ** 2) + 2.0 * math.sin(x / 20.0) + \
            _sstep(100, 300, math.hypot(x, y)) * 20
    g = FL.m_ground("wind_ground", [("#8A6A3A", 0.3), ("#C8A55A", 0.55), ("#9AA052", 0.85)], 0.1, 0.5)
    near = terrain("wind_near", 600, 220, h, g)
    white = C.m_paint("turbine_white", "#ECEDEA", 0.35, grime=0.08)
    E.turbines = []
    for k, x in enumerate((-90, -30, 30, 90, 150)):
        base = Vector((x, 40 + (k % 2) * 25, h(x, 40 + (k % 2) * 25)))
        C.tube(f"tower{k}", [base, base + Vector((0, 0, 60))], [2.2, 1.3], 16, white)
        nac = FL.icosphere(f"nacelle{k}", 1.0, 2, white)
        nac.scale = (1.6, 5.0, 1.8)
        nac.location = base + Vector((0, 0, 61))
        hub = C.link(bpy.data.objects.new(f"rotor{k}", None))
        hub.location = base + Vector((0, -5.0, 61))
        for b in range(3):
            a = 2 * math.pi * b / 3
            d = Vector((math.cos(a), 0, math.sin(a)))
            bl = C.tube(f"blade{k}{b}", [Vector((0, 0, 0)), d * 20, d * 42], [1.4, 1.0, 0.25], 6, white)
            bl.scale = (1.0, 0.35, 1.0)
            bl.parent = hub
        E.turbines.append(hub)
    grass, flowers = veg_hill()
    FL.vgroup_from_fn(near, "g", lambda p: 1.0 if abs(p.x) < 60 and p.y < 20 else 0.0)
    FL.scatter(near, grass, 2.5, seed=2, scale=(0.6, 1.1), mask="g", name="sc_g")
    FL.scatter(near, flowers, 1.5, seed=3, scale=(0.8, 1.2), mask="g", name="sc_f")
    C.volume_fog(0.002, "#F2A07A", 0.4, size=1200.0, center=(0, 0, 20), height=40.0)
    E.key = ((0.2, 1.0, 0.05), "#FF9A58", 4.0)
    E.ground = [near]
    E.marks = dict(center=Vector((0, 40, 40)))
    return E


BUILDERS = dict(hill=env_hill, cave=env_cave, farm=env_farm, agave=env_agave, tropic=env_tropic, studio=env_studio,
                sky=env_sky, mine=env_mine, wind=env_wind)
