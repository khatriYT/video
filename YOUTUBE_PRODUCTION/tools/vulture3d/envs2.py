"""Episode 3 v2 high-detail environments (static plates). Characters are animated separately (render3.py).

Builders return dict(cam=..., occluders=[objects that must also exist in the character pass]).
Everything is deterministic (seeded) so the plate pass and the character pass share identical terrain.
"""
import math
import random

import bmesh
import bpy
from mathutils import Vector

import lib as L

CARCASS = (0.0, 0.0)


# ------------------------------------------------------------------ materials
def mat_ground(name, base="#C9AB7C", soil="#9E7D55", grass="#C8B26A", green="#8E9E58", green_amt=0.15):
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Roughness"].default_value = 0.95
    try:
        b.inputs["Specular IOR Level"].default_value = 0.15
    except KeyError:
        pass
    tc = nt.nodes.new("ShaderNodeTexCoord")

    def noise(scale, detail=6):
        n = nt.nodes.new("ShaderNodeTexNoise")
        n.inputs["Scale"].default_value = scale
        n.inputs["Detail"].default_value = detail
        nt.links.new(tc.outputs["Object"], n.inputs["Vector"])
        return n

    def ramp(src, p0, p1, c0, c1):
        r = nt.nodes.new("ShaderNodeValToRGB")
        r.color_ramp.elements[0].position = p0
        r.color_ramp.elements[1].position = p1
        r.color_ramp.elements[0].color = (*L.hex_lin(c0), 1)
        r.color_ramp.elements[1].color = (*L.hex_lin(c1), 1)
        nt.links.new(src, r.inputs["Fac"])
        return r

    def mix(a, b_, fac):
        x = nt.nodes.new("ShaderNodeMix")
        x.data_type = "RGBA"
        nt.links.new(a, x.inputs["A"])
        nt.links.new(b_, x.inputs["B"])
        nt.links.new(fac, x.inputs["Factor"])
        return x.outputs["Result"]

    n1, n2, n3 = noise(0.06), noise(0.25), noise(1.6, 8)
    dirt = ramp(n3.outputs["Fac"], 0.3, 0.7, soil, base).outputs["Color"]
    grass_mask = ramp(n1.outputs["Fac"], 0.45, 0.6, "#000000", "#FFFFFF").outputs["Color"]
    col = mix(dirt, ramp(n3.outputs["Fac"], 0.35, 0.75, "#A8924F", grass).outputs["Color"], grass_mask)
    green_mask = ramp(n2.outputs["Fac"], 0.68 - green_amt, 0.75 - green_amt * 0.5, "#000000", "#FFFFFF").outputs["Color"]
    col = mix(col, ramp(n3.outputs["Fac"], 0.3, 0.8, "#6F8445", green).outputs["Color"], green_mask)
    vor = nt.nodes.new("ShaderNodeTexVoronoi")
    vor.inputs["Scale"].default_value = 9.0
    nt.links.new(tc.outputs["Object"], vor.inputs["Vector"])
    peb = ramp(vor.outputs["Distance"], 0.0, 0.08, "#FFFFFF", "#000000").outputs["Color"]
    col = mix(col, ramp(n3.outputs["Fac"], 0.2, 0.8, "#8C8377", "#B9AFA1").outputs["Color"], peb)
    nt.links.new(col, b.inputs["Base Color"])
    bm = nt.nodes.new("ShaderNodeBump")
    bm.inputs["Strength"].default_value = 0.35
    nt.links.new(n3.outputs["Fac"], bm.inputs["Height"])
    nt.links.new(bm.outputs["Normal"], b.inputs["Normal"])
    L.add_mask_aov(m)
    return m


def ground2(size=160, palette=None, disp=0.35, path=True):
    pal = palette or {}
    g = mat_ground("ground2_" + str(sorted(pal.items())), **pal)
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=160, y_subdivisions=160, size=size)
    ob = bpy.context.object
    ob.name = "ENV_GROUND"
    d = ob.modifiers.new("d", "DISPLACE")
    tex = bpy.data.textures.new("terrain2", "CLOUDS")
    tex.noise_scale = 7.0
    d.texture = tex
    d.strength = disp
    L.smooth(ob)
    L.setmat(ob, g)
    out = [ob]
    if path:   # worn dirt track: a slightly raised flattened strip curving towards the village
        pm = L.mat("path_dirt2", "#C7A87C", 0.97, noise=("#B39268", 0.8), noise_scale=0.9)
        pts = [(-26, -12), (-14, -6), (-6, -3.2), (3, -3.6), (10, 2), (14, 12), (16, 24), (17, 34)]
        bm = bmesh.new()
        prev = None
        for i in range(len(pts) - 1):
            a, b = Vector((*pts[i], 0)), Vector((*pts[i + 1], 0))
            for k in range(8):
                u = k / 8
                p = a.lerp(b, u)
                d_ = (b - a).normalized()
                nrm = Vector((-d_.y, d_.x, 0)) * 0.7
                v1 = bm.verts.new(p + nrm + Vector((0, 0, 0.025)))
                v2 = bm.verts.new(p - nrm + Vector((0, 0, 0.025)))
                if prev:
                    bm.faces.new([prev[0], prev[1], v2, v1])
                prev = (v1, v2)
        me = bpy.data.meshes.new("path")
        bm.to_mesh(me)
        bm.free()
        po = L.link(bpy.data.objects.new("ENV_PATH", me))
        sw = po.modifiers.new("sw", "SHRINKWRAP")
        sw.target = ob
        sw.wrap_method = "PROJECT"
        sw.use_project_z = True
        sw.use_negative_direction = True
        sw.offset = 0.02
        L.setmat(po, pm)
        out.append(po)
    return out


# ------------------------------------------------------------------ vegetation / props (instanced)
_MESH = {}


def tuft_mesh(kind):
    key = "tuft_" + kind
    if key in _MESH:
        return _MESH[key]
    r = random.Random(hash(kind) % 1000)
    bm = bmesh.new()
    n, hmin, hmax, lean = {"dry": (11, 0.2, 0.42, 0.45), "tall": (14, 0.35, 0.65, 0.35), "green": (12, 0.18, 0.38, 0.5),
                           "reed": (9, 0.4, 0.75, 0.2)}[kind]
    for i in range(n):
        a = r.uniform(0, 6.28)
        ln = r.uniform(0.1, lean)
        hgt = r.uniform(hmin, hmax)
        base = Vector((math.cos(a) * 0.05, math.sin(a) * 0.05, -0.02))
        mid = base + Vector((math.cos(a) * ln * hgt * 0.4, math.sin(a) * ln * hgt * 0.4, hgt * 0.55))
        top = base + Vector((math.cos(a) * ln * hgt, math.sin(a) * ln * hgt, hgt))
        side = Vector((-math.sin(a), math.cos(a), 0)) * 0.028
        v = [bm.verts.new(base - side), bm.verts.new(base + side), bm.verts.new(mid + side * 0.6),
             bm.verts.new(mid - side * 0.6), bm.verts.new(top)]
        bm.faces.new([v[0], v[1], v[2], v[3]])
        bm.faces.new([v[3], v[2], v[4]])
    me = bpy.data.meshes.new(key)
    bm.to_mesh(me)
    bm.free()
    cols = {"dry": ("#C9B06A", "#A8904E"), "tall": ("#D4BE7C", "#B39A58"), "green": ("#8FA552", "#6F8A3E"),
            "reed": ("#B8A564", "#9C8A4C")}[kind]
    me.materials.append(L.mat("grass2_" + kind, cols[0], 0.85, noise=(cols[1], 0.7), noise_scale=4))
    _MESH[key] = me
    return me


def flower_mesh(color):
    key = "flower_" + color
    if key in _MESH:
        return _MESH[key]
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=5, radius1=0.012, radius2=0.008, depth=0.3,
                          matrix=__import__("mathutils").Matrix.Translation((0, 0, 0.15)))
    res = bmesh.ops.create_uvsphere(bm, u_segments=8, v_segments=6, radius=0.045,
                                    matrix=__import__("mathutils").Matrix.Translation((0, 0, 0.31)))
    me = bpy.data.meshes.new(key)
    bm.to_mesh(me)
    bm.free()
    me.materials.append(L.mat("stem", "#6E8A3E", 0.8))
    me.materials.append(L.mat("petal_" + color, color, 0.6, sss=0.2))
    nverts_stem = 12
    for p in me.polygons:
        p.material_index = 1 if p.center.z > 0.27 else 0
        p.use_smooth = True
    _MESH[key] = me
    return me


def inst(mesh, name, loc, rot_z=0.0, scale=1.0, sz=None):
    ob = L.link(bpy.data.objects.new(name, mesh))
    ob.location = loc
    ob.rotation_euler = (0, 0, rot_z)
    ob.scale = (scale, scale, sz if sz else scale)
    return ob


def shrub(loc, rnd, s=1.0, flowers=True):
    m = L.mat("shrub", "#5C7A35", 0.85, noise=("#728F42", 0.6), noise_scale=4)
    parts = []
    for k in range(rnd.randint(4, 7)):
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(0, 0.35) * s
        c = L.prim("ico", "shrub", (loc[0] + math.cos(a) * r, loc[1] + math.sin(a) * r, 0.25 * s + rnd.uniform(0, 0.2) * s),
                   (0.35 * s * rnd.uniform(0.8, 1.2),) * 3, m=m, subdiv=2)
        parts.append(c)
    if flowers:
        fm = L.mat("lantana", rnd.choice(["#F2A23A", "#E8608A", "#F5E06A"]), 0.6, emit=0.15)
        for k in range(10):
            a = rnd.uniform(0, 6.28)
            r = rnd.uniform(0.1, 0.5) * s
            parts.append(L.prim("ico", "bloom", (loc[0] + math.cos(a) * r, loc[1] + math.sin(a) * r,
                                                  rnd.uniform(0.3, 0.65) * s), (0.05 * s,) * 3, m=fm, subdiv=1))
    return parts


def scatter_detail(area, avoid=(), seed=1, n_tuft=1400, n_flower=220, n_shrub=18, n_rock=60, green=0.2,
                   ground_z=None):
    rnd = random.Random(seed)
    (x0, x1), (y0, y1) = area

    def ok(x, y):
        return not any((x - ax) ** 2 + (y - ay) ** 2 < ar ** 2 for ax, ay, ar in avoid)

    kinds = ["dry"] * 5 + ["tall"] * 2 + ["green"] * int(1 + green * 10) + ["reed"]
    for i in range(n_tuft):
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        if ok(x, y):
            s = rnd.uniform(0.7, 1.25)
            inst(tuft_mesh(rnd.choice(kinds)), "tuft", (x, y, 0), rnd.uniform(0, 6.28), s, s * rnd.uniform(0.8, 1.2))
    for i in range(n_flower):
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        if ok(x, y):
            inst(flower_mesh(rnd.choice(["#F5D547", "#FFFFFF", "#C77DD8", "#F28B3C"])), "flower", (x, y, 0),
                 rnd.uniform(0, 6), rnd.uniform(0.7, 1.4))
    for i in range(n_shrub):
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0 + 4, y1)
        if ok(x, y):
            shrub((x, y), rnd, rnd.uniform(0.8, 1.6))
    for i in range(n_rock):
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        if ok(x, y):
            L.rock(None, (x, y, 0.02), rnd, rnd.uniform(0.06, 0.4)) if False else _rock((x, y), rnd)


def _rock(xy, rnd):
    m = L.mat("rock2", "#9A9184", 0.9, noise=("#7B7368", 0.7), noise_scale=6)
    s = rnd.uniform(0.06, 0.38)
    ob = L.prim("ico", "rock", (xy[0], xy[1], s * 0.25), (s * rnd.uniform(1, 1.7), s, s * 0.6), m=m, subdiv=2)
    d = ob.modifiers.new("d", "DISPLACE")
    tex = bpy.data.textures.get("rocktex") or bpy.data.textures.new("rocktex", "CLOUDS")
    tex.noise_scale = 0.3
    d.texture = tex
    d.strength = 0.12 * s / 0.2
    ob.rotation_euler = (0, 0, rnd.uniform(0, 6.28))
    return ob


# ------------------------------------------------------------------ trees v2
def tree2(kind, loc, scale=1.0, seed=1):
    rnd = random.Random(seed)
    parts, perches = [], []
    bark = L.mat("bark2", "#5E4834", 0.95, noise=("#463424", 0.7), noise_scale=8)
    dead = L.mat("deadbark2", "#958C80", 0.95, noise=("#6F675C", 0.7), noise_scale=8)

    def branch(a, b, r0, r1, m):
        a, b = Vector(a), Vector(b)
        d = b - a
        ob = L.prim("cone", "branch", tuple((a + b) / 2), (r0, r0, d.length), m=m, seg=10, r2=r1 / r0)
        ob.rotation_mode = "QUATERNION"
        ob.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(d.normalized())
        parts.append(ob)
        parts.append(L.prim("sphere", "knot", tuple(b), (r1 * 1.05,) * 3, m=m, seg=10))
        return b

    if kind == "dead":
        top = branch((0, 0, 0), (0.1, 0, 3.4), 0.24, 0.12, dead)
        for ang, h, ln, up in [(0.3, 2.0, 1.7, 0.45), (2.4, 2.5, 1.5, 0.55), (4.1, 2.9, 1.3, 0.35), (1.3, 3.2, 1.1, 0.75),
                               (5.3, 1.7, 1.4, 0.3), (3.3, 3.3, 0.9, 0.9)]:
            base = Vector((0.03 * h, 0, h))
            dvec = Vector((math.cos(ang), math.sin(ang), up)).normalized()
            end = branch(base, base + dvec * ln, 0.09, 0.04, dead)
            perches.append(tuple(base + dvec * ln * 0.72))
            fork = Vector((math.cos(ang + 0.7), math.sin(ang + 0.7), up + 0.3)).normalized()
            branch(base + dvec * ln * 0.6, base + dvec * ln * 0.6 + fork * ln * 0.45, 0.045, 0.02, dead)
        perches.append((0.1, 0, 3.45))
    elif kind == "neem":
        h = 2.4
        branch((0, 0, 0), (0.05, 0, h), 0.26, 0.17, bark)
        leaf = L.mat("neem2", "#4C7230", 0.85, noise=("#6E9440", 0.7), noise_scale=3)
        leaf2 = L.mat("neem2b", "#5E8A38", 0.85, noise=("#82A84C", 0.7), noise_scale=3)
        for k in range(4):
            a = k * 1.6 + rnd.uniform(-0.3, 0.3)
            branch((0.05, 0, h - 0.2), (math.cos(a) * 1.0, math.sin(a) * 1.0, h + 1.0), 0.12, 0.06, bark)
        for k in range(14):
            a = rnd.uniform(0, 6.28)
            r = rnd.uniform(0.2, 1.4)
            c = L.prim("ico", "canopy", (math.cos(a) * r, math.sin(a) * r, h + 0.9 + rnd.uniform(0, 1.2) - r * 0.25),
                       (rnd.uniform(0.75, 1.15),) * 3, m=leaf if k % 3 else leaf2, subdiv=3)
            d = c.modifiers.new("d", "DISPLACE")
            tex = bpy.data.textures.get("lumps2") or bpy.data.textures.new("lumps2", "CLOUDS")
            tex.noise_scale = 0.35
            d.texture = tex
            d.strength = 0.3
            parts.append(c)
    elif kind == "acacia":
        h = 2.3
        branch((0, 0, 0), (0.1, 0, h), 0.18, 0.12, bark)
        leaf = L.mat("acacia2", "#73823A", 0.85, noise=("#8F9C4A", 0.7), noise_scale=4)
        tops = []
        for ang in (0.3, 2.3, 4.2):
            dvec = Vector((math.cos(ang) * 0.75, math.sin(ang) * 0.75, 1)).normalized()
            tops.append(branch((0.1, 0, h), Vector((0.1, 0, h)) + dvec * 1.5, 0.09, 0.05, bark))
        for k in range(7):
            a = rnd.uniform(0, 6.28)
            r = rnd.uniform(0.2, 1.7)
            c = L.prim("sphere", "canopy", (math.cos(a) * r, math.sin(a) * r, h + 1.3 + rnd.uniform(-0.1, 0.2)),
                       (rnd.uniform(1.2, 1.9), rnd.uniform(1.0, 1.6), 0.3), m=leaf)
            d = c.modifiers.new("d", "DISPLACE")
            tex = bpy.data.textures.get("lumps3") or bpy.data.textures.new("lumps3", "CLOUDS")
            tex.noise_scale = 0.25
            d.texture = tex
            d.strength = 0.18
            parts.append(c)
        perches = [(1.4, 0.3, h + 1.62), (-1.2, 0.6, h + 1.58), (0.3, -1.3, h + 1.6), (0.9, 1.1, h + 1.62),
                   (-0.4, -0.5, h + 1.66)]
    root = L.group("OBJ_TREE2_" + kind.upper(), parts, loc, (0, 0, rnd.uniform(0, 6.28)), scale)
    bpy.context.view_layer.update()
    perches = [tuple(root.matrix_world @ Vector(p)) for p in perches]
    return root, perches


def treeline(y, x_span=(-160, 160), n=70, seed=5, scale=(3, 6)):
    rnd = random.Random(seed)
    m = L.mat("farleaf", "#5D7A45", 0.9, noise=("#6E8A52", 0.6), noise_scale=2)
    tm = L.mat("fartrunk", "#4E3D2E", 0.9)
    for i in range(n):
        x = rnd.uniform(*x_span)
        yy = y + rnd.uniform(-12, 12)
        s = rnd.uniform(*scale)
        L.prim("cyl", "ftrunk", (x, yy, s * 0.4), (0.12 * s, 0.12 * s, s * 0.8), m=tm, seg=6)
        L.prim("ico", "fcan", (x, yy, s * 1.1), (s * 0.7, s * 0.7, s * 0.6), m=m, subdiv=2)


# ------------------------------------------------------------------ village v2
def house2(loc, rot_z=0.0, w=3.0, d=2.6, h=2.4, wall="#D9B98C", trim="#A65E3A", roof="flat", props=True, seed=0,
           lit=False):
    rnd = random.Random(seed)
    def darker(hx, k=22):
        return "#" + "".join(f"{max(0, int(hx[i:i + 2], 16) - k):02x}" for i in (1, 3, 5))
    wm = L.mat("wall2_" + wall, wall, 0.95, noise=(darker(wall, 14), 0.6), noise_scale=2.5)
    dado = L.mat("dado_" + wall, darker(wall, 45), 0.9)
    tm = L.mat("trim2_" + trim, trim, 0.85)
    wood = L.mat("door_wood", "#6B4A2E", 0.8, noise=("#5A3D25", 0.6), noise_scale=8)
    doorc = L.mat("door_" + trim, rnd.choice(["#2F6E8C", "#3C7A4A", "#8C3B2F", "#6B4A2E"]), 0.7)
    glass = L.mat("win_lit" if lit else "win_dark", "#FFC86A" if lit else "#2A2522", 0.5, emit=4.0 if lit else 0.0)
    parts = [L.prim("cube", "wall", (0, 0, h / 2), (w, d, h), m=wm),
             L.prim("cube", "dado", (0, 0, 0.3), (w + 0.04, d + 0.04, 0.6), m=dado)]
    if roof == "flat":
        parts.append(L.prim("cube", "parapet", (0, 0, h + 0.15), (w + 0.12, d + 0.12, 0.3), m=tm))
        parts.append(L.prim("cube", "roofcap", (0, 0, h + 0.02), (w, d, 0.06), m=wm))
        if props and rnd.random() < 0.7:
            parts.append(L.prim("cyl", "tank", (w * 0.25, d * 0.2, h + 0.55), (0.32, 0.32, 0.7),
                                m=L.mat("tank", "#1E1E20", 0.4, spec=0.5), seg=16))
    else:
        rm = L.mat("tile_" + trim, trim, 0.85, noise=(darker(trim, 25), 0.7), noise_scale=12)
        for s_ in (1, -1):
            r = L.prim("cube", "roof", (0, s_ * d * 0.27, h + 0.42), (w + 0.4, d * 0.62, 0.1), rot=(s_ * -0.55, 0, 0), m=rm)
            parts.append(r)
    # door with frame
    parts.append(L.prim("cube", "doorframe", (0.35, -d / 2 - 0.02, 0.75), (0.8, 0.06, 1.5), m=tm))
    parts.append(L.prim("cube", "door", (0.35, -d / 2 - 0.05, 0.72), (0.62, 0.04, 1.38), m=doorc))
    parts.append(L.prim("cube", "step", (0.35, -d / 2 - 0.25, 0.08), (1.0, 0.45, 0.16), m=dado))
    # windows with shutters
    for wx in (-w * 0.3,):
        parts.append(L.prim("cube", "winframe", (wx, -d / 2 - 0.02, 1.35), (0.62, 0.06, 0.62), m=tm))
        parts.append(L.prim("cube", "glass", (wx, -d / 2 - 0.04, 1.35), (0.46, 0.04, 0.46), m=glass))
        for sx in (-1, 1):
            parts.append(L.prim("cube", "shutter", (wx + sx * 0.42, -d / 2 - 0.06, 1.35), (0.22, 0.03, 0.5), m=doorc))
    if props:
        if rnd.random() < 0.6:   # clothesline with cloth
            line = L.prim("cyl", "line", (w / 2 + 0.9, -d / 2 - 0.6, 1.6), (0.01, 0.01, 1.8), rot=(math.pi / 2, 0, 0.3),
                          m=L.mat("rope", "#3A3028", 0.8), seg=6)
            parts.append(line)
            for k in range(3):
                c = rnd.choice(["#D84A3A", "#3A7BC8", "#F2C14E", "#8E4AB0", "#E8E2D4"])
                parts.append(L.prim("cube", "cloth", (w / 2 + 0.9 + 0.15 * k, -d / 2 - 1.2 + 0.5 * k, 1.35), (0.04, 0.4, 0.5),
                                    rot=(0, 0, 0.3), m=L.mat("cloth2_" + c, c, 0.9)))
        if rnd.random() < 0.6:   # clay pots
            for k in range(rnd.randint(1, 3)):
                parts.append(L.prim("sphere", "pot", (-w / 2 + 0.4 + 0.35 * k, -d / 2 - 0.35, 0.18), (0.18, 0.18, 0.2),
                                    m=L.mat("clay", "#A85A35", 0.8, noise=("#8E4A2A", 0.6), noise_scale=10)))
        if rnd.random() < 0.5:   # charpai (string bed)
            cm = L.mat("charpai", "#8A6A43", 0.8)
            parts.append(L.prim("cube", "bedtop", (-w / 2 - 1.0, -d / 2 - 0.8, 0.45), (0.9, 1.7, 0.06),
                                m=L.mat("weave", "#D9C59A", 0.9, noise=("#BFA97C", 0.7), noise_scale=30)))
            for sx in (-1, 1):
                for sy in (-1, 1):
                    parts.append(L.prim("cube", "bedleg", (-w / 2 - 1.0 + sx * 0.4, -d / 2 - 0.8 + sy * 0.8, 0.22),
                                        (0.07, 0.07, 0.45), m=cm))
    return L.group("OBJ_HOUSE2", parts, loc, (0, 0, rot_z), 1.0)


def haystack(loc, s=1.0):
    m = L.mat("hay", "#D8B85E", 0.95, noise=("#BF9F48", 0.7), noise_scale=20)
    a = L.prim("cone", "hay", (loc[0], loc[1], 1.0 * s), (1.1 * s, 1.1 * s, 2.0 * s), m=m, seg=24, r2=0.15)
    return a


# ------------------------------------------------------------------ carcass (static occluder)
def carcass(state="fresh"):
    """Stylized zebu carcass, non-graphic (eyes closed, no blood). state: fresh | bloated | none."""
    if state == "none":
        return []
    import rigs as R
    M2 = R.M2()
    k = 1.12 if state == "bloated" else 1.0
    body = Vector((0, 0, 0.42 * k))
    els = [dict(type="ELLIPSOID", co=tuple(body), size=(0.95, 0.45 * k, 0.4 * k)),
           dict(type="ELLIPSOID", co=(0.45, -0.15, 0.62), size=(0.22, 0.25, 0.18)),
           L.seg_capsule((0.8, 0, 0.35), (1.25, 0.05, 0.25), 0.18)]
    for x in (0.6, -0.6):
        els.append(L.seg_capsule((x, -0.2, 0.3), (x + 0.1, -0.95, 0.12), 0.08))
        els.append(L.seg_capsule((x + 0.12, -0.15, 0.35), (x + 0.25, -0.85, 0.2), 0.08))
    hide = L.mat("carcass_hide", "#B8B1A6", 0.8, noise=("#9D968B", 0.6), noise_scale=5)
    parts = [L.meta("carcass_body", els, hide, res=0.035)]
    hc = Vector((1.4, 0.05, 0.25))
    parts.append(L.meta("carcass_head", [dict(type="ELLIPSOID", co=tuple(hc), size=(0.25, 0.17, 0.17)),
                                         L.seg_capsule(hc + Vector((0.1, 0, -0.03)), hc + Vector((0.32, 0.05, -0.08)), 0.1)],
                        M2["cow_dark"], res=0.03))
    for s in (1, -1):
        parts.append(L.prim("cone", "carcass_horn", tuple(hc + Vector((-0.1, s * 0.12, 0.2 if s > 0 else 0.1))),
                            (0.05, 0.05, 0.3), rot=(s * -0.9, -0.5, 0), m=M2["horn"], seg=12))
    for x in (0.7, -0.5, 0.82, -0.38):
        parts.append(L.prim("cyl", "carcass_hoof", (x + 0.12, -0.93 if x in (0.7, -0.5) else -0.84, 0.12),
                            (0.07, 0.07, 0.1), rot=(math.pi / 2, 0, 0), m=M2["hoof"], seg=10))
    root = L.group("OBJ_CARCASS", parts, (CARCASS[0], CARCASS[1], 0), (0, 0, 0.35), 1.0)
    return [root] + parts


def bones2(loc, rot_z=0.0, scale=1.0, seed=3):
    r = L.bones(L.P(), loc, rot_z, scale, seed=seed)
    return [r] + list(r.children)


def airliner(loc, rot_z, scale):
    white = L.mat("plane_white", "#F1F1EE", 0.4)
    parts = [L.prim("cyl", "fus", (0, 0, 0), (0.25, 0.25, 4.0), rot=(0, math.pi / 2, 0), m=white),
             L.prim("cube", "wing", (0.1, 0, 0), (0.8, 4.0, 0.06), rot=(0, 0, 0.25), m=white),
             L.prim("cube", "tail", (-1.8, 0, 0.45), (0.5, 0.06, 0.9), rot=(0, 0.35, 0), m=white),
             L.prim("cube", "stab", (-1.85, 0, 0.1), (0.4, 1.4, 0.05), m=white)]
    return L.group("OBJ_AIRLINER", parts, loc, (0, 0, rot_z), scale)


