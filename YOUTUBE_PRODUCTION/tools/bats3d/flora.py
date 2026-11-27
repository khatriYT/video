"""v3 procedural plants, rocks and scattering (Geometry Nodes instancing) for Episode 4 environments.

All geometry is generated in Python; all materials are PBR (core.py) with subsurface/translucency on foliage.
"""
import math
import random

import bpy
from mathutils import Matrix, Vector

from core import NB, _shift, link, mesh_ob, new_mat, rgba, smooth, tube
from core import m_simple as C_simple


# ------------------------------------------------------------------ materials
def m_leaf(name, base, var=0.08, rough=0.55, sss=0.25, vein=None, waxy=0.0, scale=40.0, tip=None):
    nb, m = new_mat(name)
    if nb is None:
        return m
    gen = nb.coord("Generated")
    oi = nb.n("ShaderNodeObjectInfo")
    nz = nb.noise(gen, scale, 4.0, 0.6)
    f = nb.math("ADD", nb.math("MULTIPLY", nz.outputs["Fac"], 0.7), nb.math("MULTIPLY", oi.outputs["Random"], 0.6))
    col = nb.ramp(f, [(0.25, _shift(base, -var)), (0.55, base), (0.9, _shift(base, var))]).outputs[0]
    if tip:
        sep = nb.n("ShaderNodeSeparateXYZ")
        nb.l(nb.coord("Object"), sep.inputs[0])
        col = nb.mix(col, tip, nb.ramp(sep.outputs[2], [(0.0, 0.0), (1.0, 1.0)]).outputs[0])
    kw = {"Base Color": col, "Roughness": rough, "Subsurface Weight": sss, "Subsurface Radius": (0.6, 1.0, 0.3),
          "Subsurface Scale": 0.02, "Specular IOR Level": 0.45, "Normal": nb.bump(nz.outputs["Fac"], 0.2, 0.004)}
    if waxy:
        kw.update({"Coat Weight": waxy, "Coat Roughness": 0.35, "Sheen Weight": waxy * 0.6})
    nb.bsdf(**kw)
    m.use_backface_culling = False
    return m


def m_canopy(name, base, var=0.12, scale=14.0, sss=0.3, flower=None, flower_amt=0.0, fruit=None):
    """Stylised foliage mass: leaf-cluster cells (Voronoi), colour variation, translucency, deep bump."""
    nb, m = new_mat(name)
    if nb is None:
        return m
    gen = nb.coord("Object")
    vo = nb.n("ShaderNodeTexVoronoi", Scale=scale)
    nb.l(gen, vo.inputs["Vector"])
    vo2 = nb.n("ShaderNodeTexVoronoi", Scale=scale * 4)
    nb.l(gen, vo2.inputs["Vector"])
    nz = nb.noise(gen, 3.0, 3.0, 0.6)
    f = nb.math("ADD", nb.math("MULTIPLY", vo.outputs["Distance"], 0.8), nb.math("MULTIPLY", nz.outputs["Fac"], 0.6))
    col = nb.ramp(f, [(0.1, _shift(base, -var * 1.4)), (0.45, base), (0.85, _shift(base, var))]).outputs[0]
    if flower:
        fm = nb.ramp(vo2.outputs["Distance"], [(0.0, 1.0), (0.12 * flower_amt, 0.0)])
        col = nb.mix(col, flower, fm.outputs[0])
    if fruit:
        fr = nb.ramp(vo.outputs["Distance"], [(0.0, 1.0), (0.06, 0.0)])
        col = nb.mix(col, fruit, fr.outputs[0])
    h = nb.math("ADD", vo.outputs["Distance"], nb.math("MULTIPLY", vo2.outputs["Distance"], 0.5))
    nb.bsdf(**{"Base Color": col, "Roughness": 0.62, "Subsurface Weight": sss, "Subsurface Radius": (0.5, 1.0, 0.25),
               "Subsurface Scale": 0.15, "Normal": nb.bump(h, 0.6, 0.06), "Sheen Weight": 0.25})
    return m


def m_bark(name, base="#5E4A3A", scale=6.0, moss=None):
    nb, m = new_mat(name)
    if nb is None:
        return m
    gen = nb.coord("Object")
    mp = nb.n("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (scale, scale, scale * 0.25)
    nb.l(gen, mp.inputs["Vector"])
    vo = nb.n("ShaderNodeTexVoronoi", feature="DISTANCE_TO_EDGE", Scale=4.0)
    nb.l(mp.outputs[0], vo.inputs["Vector"])
    nz = nb.noise(gen, 20.0, 5.0, 0.6)
    col = nb.ramp(nz.outputs["Fac"], [(0.3, _shift(base, -0.08)), (0.7, _shift(base, 0.06))]).outputs[0]
    cr = nb.ramp(vo.outputs["Distance"], [(0.0, 0.0), (0.12, 1.0)]).outputs[0]
    col = nb.mix(_shift(base, -0.2), col, cr)
    if moss:
        sep = nb.n("ShaderNodeSeparateXYZ")
        nb.l(nb.coord("Normal"), sep.inputs[0])
        mm = nb.math("MULTIPLY", nb.ramp(sep.outputs[2], [(0.2, 0.0), (0.7, 1.0)]).outputs[0],
                     nb.ramp(nz.outputs["Fac"], [(0.45, 0.0), (0.6, 1.0)]).outputs[0])
        col = nb.mix(col, moss, mm)
    nb.bsdf(**{"Base Color": col, "Roughness": 0.85, "Normal": nb.bump(cr, 0.6, 0.02)})
    return m


def m_rock(name, base="#C9BBA0", dark="#8A7D68", strata=True, lichen=("#D98C2B", "#9DB05A"), wet=0.0, scale=1.0):
    """Limestone: horizontal strata, pitted bump, lichen spots, optional wet sheen."""
    nb, m = new_mat(name)
    if nb is None:
        return m
    gen = nb.coord("Object")
    nz = nb.noise(gen, 3.0 * scale, 6.0, 0.62, dist=0.3)
    fine = nb.noise(gen, 40.0 * scale, 4.0, 0.6)
    col = nb.ramp(nz.outputs["Fac"], [(0.3, dark), (0.55, base), (0.8, _shift(base, 0.06))]).outputs[0]
    h = nb.math("ADD", nz.outputs["Fac"], nb.math("MULTIPLY", fine.outputs["Fac"], 0.35))
    if strata:
        w = nb.n("ShaderNodeTexWave", wave_type="BANDS", bands_direction="Z", Scale=2.2 * scale, Distortion=4.0,
                 Detail=3.0)
        nb.l(gen, w.inputs["Vector"])
        sm = nb.ramp(w.outputs["Fac"], [(0.3, 0.0), (0.5, 0.35), (0.7, 0.0)]).outputs[0]
        col = nb.mix(col, _shift(dark, -0.06), sm)
        h = nb.math("ADD", h, nb.math("MULTIPLY", w.outputs["Fac"], 0.3))
    if lichen:
        vo = nb.n("ShaderNodeTexVoronoi", Scale=18.0 * scale)
        nb.l(gen, vo.inputs["Vector"])
        sep = nb.n("ShaderNodeSeparateXYZ")
        nb.l(nb.coord("Normal"), sep.inputs[0])
        up = nb.ramp(sep.outputs[2], [(0.0, 0.0), (0.6, 1.0)]).outputs[0]
        l1 = nb.math("MULTIPLY", nb.ramp(vo.outputs["Distance"], [(0.0, 1.0), (0.18, 0.0)]).outputs[0], up)
        l1 = nb.math("MULTIPLY", l1, nb.ramp(nz.outputs["Fac"], [(0.45, 0.0), (0.6, 1.0)]).outputs[0])
        col = nb.mix(col, lichen[0], l1)
        l2 = nb.math("MULTIPLY", nb.ramp(fine.outputs["Fac"], [(0.55, 0.0), (0.7, 1.0)]).outputs[0], up)
        col = nb.mix(col, lichen[1], nb.math("MULTIPLY", l2, 0.7))
    rough = 0.82 - wet * 0.6
    nb.bsdf(**{"Base Color": col, "Roughness": rough, "Normal": nb.bump(h, 0.9, 0.05),
               "Coat Weight": wet, "Coat Roughness": 0.08, "Specular IOR Level": 0.4})
    return m


def m_ground(name, layers, scale=0.35, bump=0.5, wet=0.0, slope_rock=None):
    """layers: list of (hex, threshold) mixed by large + small noise; optional rock colour on steep slopes."""
    nb, m = new_mat(name)
    if nb is None:
        return m
    gen = nb.coord("Object")
    big = nb.noise(gen, scale, 5.0, 0.6, dist=0.4)
    small = nb.noise(gen, scale * 18, 4.0, 0.6)
    f = nb.math("ADD", nb.math("MULTIPLY", big.outputs["Fac"], 0.8), nb.math("MULTIPLY", small.outputs["Fac"], 0.3))
    stops = [(t, c) for c, t in layers]
    col = nb.ramp(f, stops).outputs[0]
    if slope_rock:
        sep = nb.n("ShaderNodeSeparateXYZ")
        nb.l(nb.coord("Normal"), sep.inputs[0])
        sr = nb.ramp(sep.outputs[2], [(0.72, 1.0), (0.86, 0.0)]).outputs[0]
        col = nb.mix(col, slope_rock, sr)
    pebble = nb.n("ShaderNodeTexVoronoi", Scale=scale * 120)
    nb.l(gen, pebble.inputs["Vector"])
    h = nb.math("ADD", small.outputs["Fac"], nb.math("MULTIPLY", pebble.outputs["Distance"], 0.4))
    nb.bsdf(**{"Base Color": col, "Roughness": 0.9 - wet * 0.5, "Normal": nb.bump(h, bump, 0.01),
               "Coat Weight": wet, "Coat Roughness": 0.1})
    return m


# ------------------------------------------------------------------ geometry helpers
def disp(ob, strength=0.2, size=0.5, kind="CLOUDS", depth=3, levels=0, coords="LOCAL"):
    if levels:
        sub = ob.modifiers.new("sub", "SUBSURF")
        sub.levels = sub.render_levels = levels
    tex = bpy.data.textures.new(ob.name + "_t", kind)
    if kind == "CLOUDS":
        tex.noise_scale = size
        tex.noise_depth = depth
    elif kind == "VORONOI":
        tex.noise_scale = size
    d = ob.modifiers.new("disp", "DISPLACE")
    d.texture = tex
    d.strength = strength
    d.mid_level = 0.5
    d.texture_coords = coords
    return ob


def icosphere(name, r, subdiv=3, mat=None):
    import bmesh
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=subdiv, radius=r)
    bm.to_mesh(me)
    bm.free()
    ob = link(bpy.data.objects.new(name, me))
    if mat:
        me.materials.append(mat)
    smooth(ob)
    return ob


def grid(name, sx, sy, nx, ny, mat=None, height=None):
    verts, faces = [], []
    for j in range(ny + 1):
        for i in range(nx + 1):
            x = -sx / 2 + sx * i / nx
            y = -sy / 2 + sy * j / ny
            verts.append((x, y, height(x, y) if height else 0.0))
    for j in range(ny):
        for i in range(nx):
            a = j * (nx + 1) + i
            faces.append((a, a + 1, a + nx + 2, a + nx + 1))
    return mesh_ob(name, verts, faces, mat)


def blade(length, width, bend=0.4, segs=6, twist=0.0, taper=1.0, fold=0.0):
    """Leaf/blade strip in local space (base at origin, growing +Z, bending toward +Y). Returns verts, faces."""
    verts, faces = [], []
    for k in range(segs + 1):
        u = k / segs
        ang = bend * u * u * 1.6
        y = math.sin(ang) * length * u * 0.6
        z = math.cos(ang * 0.6) * length * u
        w = width * (1 - u ** 1.5 * taper) * (0.5 + 0.5 * math.sin(math.pi * min(1, u * 1.3 + 0.15)))
        tw = twist * u
        for sgn in (-1, 0, 1):
            x = sgn * w / 2
            yy = y + abs(sgn) * fold * w * 0.5
            verts.append((x * math.cos(tw) - yy * math.sin(tw) * 0.2, yy + x * math.sin(tw), z))
    for k in range(segs):
        a = k * 3
        faces.append((a, a + 1, a + 4, a + 3))
        faces.append((a + 1, a + 2, a + 5, a + 4))
    return verts, faces


def combine(parts):
    """parts: list of (verts, faces, matrix) -> verts, faces."""
    V, F = [], []
    for v, f, M in parts:
        base = len(V)
        V += [tuple(M @ Vector(p)) for p in v]
        F += [tuple(i + base for i in face) for face in f]
    return V, F


def _rz(a):
    return Matrix.Rotation(a, 4, "Z")


def _rx(a):
    return Matrix.Rotation(a, 4, "X")


# ------------------------------------------------------------------ plants
def grass_clump(name, mat, n=14, h=0.45, w=0.012, seed=1, spread=0.06):
    rnd = random.Random(seed)
    parts = []
    for i in range(n):
        v, f = blade(h * rnd.uniform(0.6, 1.2), w * rnd.uniform(0.7, 1.2), rnd.uniform(0.3, 0.9), 5,
                     twist=rnd.uniform(-0.5, 0.5))
        M = (Matrix.Translation((rnd.gauss(0, spread * 0.3), rnd.gauss(0, spread * 0.3), 0)) @ _rz(rnd.uniform(0, 6.28))
             @ _rx(rnd.uniform(-0.25, 0.25)))
        parts.append((v, f, M))
    V, F = combine(parts)
    return mesh_ob(name, V, F, mat)


def flower_spike(name, stem_m, flower_m, tip_m=None, h=0.35, head=0.12, r=0.022, seed=1):
    """Bluebonnet / paintbrush-like flower: stem + leaves + conical cluster of florets."""
    rnd = random.Random(seed)
    import bmesh
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    for m in (stem_m, flower_m, tip_m or flower_m):
        me.materials.append(m)
    # stem
    st = bmesh.ops.create_cone(bm, cap_ends=True, segments=6, radius1=0.004, radius2=0.003, depth=h)
    bmesh.ops.translate(bm, verts=st["verts"], vec=(0, 0, h / 2))
    # florets: small spheres on a cone
    nfl = 26
    for k in range(nfl):
        u = k / nfl
        z = h - head + head * u
        rr = r * (1 - u * 0.75)
        a = k * 2.4
        res = bmesh.ops.create_icosphere(bm, subdivisions=1, radius=0.0075 * (1 - 0.4 * u))
        bmesh.ops.translate(bm, verts=res["verts"], vec=(math.cos(a) * rr, math.sin(a) * rr, z))
        for f in {f for v in res["verts"] for f in v.link_faces}:
            f.material_index = 2 if u > 0.78 else 1
    # leaves
    for k in range(4):
        v, f = blade(0.09, 0.025, 0.9, 4)
        M = _rz(k * 1.57 + rnd.random()) @ _rx(0.6)
        vs = [bm.verts.new(tuple(M @ Vector(p))) for p in v]
        for face in f:
            bm.faces.new([vs[i] for i in face])
    bm.to_mesh(me)
    bm.free()
    ob = link(bpy.data.objects.new(name, me))
    smooth(ob)
    return ob


def daisy(name, petal_m, center_m, stem_m, h=0.3, r=0.03, petals=12):
    import bmesh
    me = bpy.data.meshes.new(name)
    for m in (stem_m, petal_m, center_m):
        me.materials.append(m)
    bm = bmesh.new()
    st = bmesh.ops.create_cone(bm, cap_ends=True, segments=5, radius1=0.003, radius2=0.002, depth=h)
    bmesh.ops.translate(bm, verts=st["verts"], vec=(0, 0, h / 2))
    c = bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r * 0.35)
    bmesh.ops.scale(bm, verts=c["verts"], vec=(1, 1, 0.6))
    bmesh.ops.translate(bm, verts=c["verts"], vec=(0, 0, h))
    for f in {f for v in c["verts"] for f in v.link_faces}:
        f.material_index = 2
    for k in range(petals):
        a = 2 * math.pi * k / petals
        p0 = Vector((math.cos(a) * r * 0.3, math.sin(a) * r * 0.3, h))
        p1 = Vector((math.cos(a) * r, math.sin(a) * r, h - 0.004))
        side = Vector((-math.sin(a), math.cos(a), 0)) * r * 0.16
        vs = [bm.verts.new(tuple(p)) for p in (p0 - side * 0.5, p1 - side, p1 + side, p0 + side * 0.5)]
        f = bm.faces.new(vs)
        f.material_index = 1
    bm.to_mesh(me)
    bm.free()
    ob = link(bpy.data.objects.new(name, me))
    smooth(ob)
    return ob


def tree(name, kind, seed=1, h=5.0, crown=2.5, trunk_m=None, leaf_m=None, lean=0.0, leaves=None):
    """leaves: None (smooth stylised masses) or (leaf material, kind, size, density) for leaf-card foliage."""
    """Stylised tree: branching trunk tubes + clustered foliage masses (displaced icospheres)."""
    rnd = random.Random(seed)
    objs = []
    base = Vector((0, 0, 0))
    if kind in ("oak", "fig"):
        # spreading trunk that forks into 3-5 limbs
        top = Vector((lean, 0, h * 0.35))
        objs.append(tube(name + "_trunk", [base, base.lerp(top, 0.5) + Vector((0.1, 0, 0)), top],
                         [h * 0.07, h * 0.055, h * 0.045], 10, trunk_m))
        ends = []
        for k in range(rnd.randint(3, 5)):
            a = rnd.uniform(0, 6.28)
            d = Vector((math.cos(a), math.sin(a), 0))
            e = top + d * crown * rnd.uniform(0.55, 0.9) + Vector((0, 0, h * rnd.uniform(0.3, 0.5)))
            mid = top.lerp(e, 0.5) + Vector((0, 0, -0.2))
            objs.append(tube(f"{name}_limb{k}", [top, mid, e], [h * 0.04, h * 0.03, h * 0.015], 8, trunk_m))
            ends.append(e)
        if kind == "fig":   # buttress roots + hanging aerial roots
            for k in range(6):
                a = k * 1.05 + rnd.random() * 0.3
                d = Vector((math.cos(a), math.sin(a), 0))
                objs.append(tube(f"{name}_root{k}", [base + Vector((0, 0, h * 0.12)), base + d * h * 0.09,
                                                     base + d * h * 0.16 + Vector((0, 0, -0.1))],
                                 [h * 0.03, h * 0.025, h * 0.01], 6, trunk_m))
        blobs = []
        for e in ends:
            for k in range(rnd.randint(4, 6)):
                off = Vector((rnd.gauss(0, crown * 0.35), rnd.gauss(0, crown * 0.35), rnd.gauss(0.1, crown * 0.18)))
                blobs.append((e + off, crown * rnd.uniform(0.32, 0.5)))
        blobs.append((top + Vector((0, 0, h * 0.5)), crown * 0.7))
    elif kind == "juniper":
        objs.append(tube(name + "_trunk", [base, Vector((lean * 0.5, 0, h * 0.4)), Vector((lean, 0, h * 0.85))],
                         [h * 0.05, h * 0.035, h * 0.02], 8, trunk_m))
        blobs = []
        for k in range(9):
            u = k / 8
            z = h * (0.25 + 0.7 * u)
            rr = crown * (1 - u * 0.75) * rnd.uniform(0.8, 1.1)
            blobs.append((Vector((lean * u + rnd.gauss(0, 0.15), rnd.gauss(0, 0.15), z)), rr * 0.75))
            for j in range(2):
                a = rnd.uniform(0, 6.28)
                blobs.append((Vector((math.cos(a) * rr * 0.6 + lean * u, math.sin(a) * rr * 0.6, z + rnd.gauss(0, 0.2))),
                              rr * 0.45))
    elif kind == "palm":
        top = Vector((lean, rnd.gauss(0, 0.2), h))
        pts = [base.lerp(top, k / 6) + Vector((math.sin(k * 0.5) * 0.15 * lean, 0, 0)) for k in range(7)]
        objs.append(tube(name + "_trunk", pts, [0.16, 0.15, 0.14, 0.13, 0.12, 0.12, 0.13], 10, trunk_m))
        fr = []
        for k in range(11):
            a = 2 * math.pi * k / 11 + rnd.random() * 0.2
            v, f = blade(2.6, 0.7, 1.6, 9, fold=0.4)
            M = Matrix.Translation(top) @ _rz(a) @ _rx(-1.0 + rnd.uniform(-0.2, 0.3))
            fr.append((v, f, M))
        V, F = combine(fr)
        objs.append(mesh_ob(name + "_fronds", V, F, leaf_m))
        blobs = []
    else:
        raise ValueError(kind)
    for k, (c, r) in enumerate(blobs):
        b = icosphere(f"{name}_leaf{k}", r, 3, leaf_m)
        b.location = c
        b.scale = (1.0, 1.0, rnd.uniform(0.7, 0.9))
        disp(b, r * 0.35, r * 0.5, depth=2)
        if leaves:
            lm, lk, ls, ld = leaves
            foliage(b, lm, lk, ls, ld, seed=k + seed * 13, inner_m=leaf_m)
        objs.append(b)
    return objs


def agave(name, leaf_m, n=38, h=1.4, seed=1, spine_m=None):
    """Blue agave rosette: rigid, straight, V-section leaves radiating from the core (golden-angle phyllotaxis),
    outer leaves near horizontal, inner leaves upright; dark terminal spines."""
    rnd = random.Random(seed)
    parts = []
    for k in range(n):
        u = k / n
        a = k * 2.39996 + rnd.uniform(-0.05, 0.05)
        tilt = 1.25 - 1.05 * u          # outer (first) leaves spread wide
        L = h * (0.75 + 0.35 * math.sin(math.pi * min(1.0, u * 1.3))) * rnd.uniform(0.92, 1.05)
        v, f = blade(L, 0.12 * h * (0.75 + 0.25 * (1 - u)), 0.04, 8, taper=1.0, fold=0.9)
        M = Matrix.Translation((0, 0, 0.05 * h * u)) @ _rz(a) @ _rx(-tilt)
        parts.append((v, f, M))
    V, F = combine(parts)
    ob = mesh_ob(name, V, F, leaf_m)
    sol = ob.modifiers.new("sol", "SOLIDIFY")
    sol.thickness = 0.035 * h
    sol.offset = 0.0
    return ob


def flower_cluster(name, centre, r, tube_m, stamen_m, anther_m, seed=1, n=46):
    """Detailed agave umbel: upright tubular flowers on a dome, each with six long stamens tipped by anthers."""
    rnd = random.Random(seed)
    tubes, stam, anth = [], [], []
    import bmesh
    for k in range(n):
        u = (k + 0.5) / n
        th = math.acos(1 - u * 1.1)            # dome (upper hemisphere and a bit more)
        ph = k * 2.39996
        d = Vector((math.sin(th) * math.cos(ph), math.sin(th) * math.sin(ph), math.cos(th))).normalized()
        base = Vector(centre) + d * r * 0.45
        tip = base + d * r * 0.55
        tubes.append(([base, base.lerp(tip, 0.6), tip], [0.011, 0.014, 0.009]))
        for j in range(6):
            a = 2 * math.pi * j / 6 + rnd.random() * 0.3
            side = d.orthogonal().normalized()
            side2 = d.cross(side)
            spread = (side * math.cos(a) + side2 * math.sin(a)) * 0.35
            end = tip + (d + spread).normalized() * r * rnd.uniform(0.55, 0.75)
            stam.append(([tip, tip.lerp(end, 0.5), end], [0.0016, 0.0013, 0.001]))
            anth.append(end)
    objs = []
    for lst, m, seg in ((tubes, tube_m, 6), (stam, stamen_m, 4)):
        V, F = [], []
        for pts, radii in lst:
            ob = tube("tmp", pts, radii, seg, None)
            base = len(V)
            V += [tuple(v.co) for v in ob.data.vertices]
            F += [tuple(i + base for i in p.vertices) for p in ob.data.polygons]
            bpy.data.objects.remove(ob)
        objs.append(mesh_ob(f"{name}_{m.name}", V, F, m))
    bm = bmesh.new()
    for p in anth:
        res = bmesh.ops.create_icosphere(bm, subdivisions=1, radius=0.0042)
        bmesh.ops.scale(bm, verts=res["verts"], vec=(1.0, 1.0, 1.8))
        bmesh.ops.translate(bm, verts=res["verts"], vec=tuple(p))
    me = bpy.data.meshes.new(name + "_anthers")
    bm.to_mesh(me)
    bm.free()
    ob = link(bpy.data.objects.new(name + "_anthers", me))
    me.materials.append(anther_m)
    smooth(ob)
    objs.append(ob)
    return objs


def agave_stalk(name, stalk_m, flower_m, h=6.0, seed=1, clusters=None, hero=False):
    """Flowering stalk (quiote) with candelabra branches tipped by yellow flower clusters.
    clusters: optional list that receives the local cluster centres."""
    rnd = random.Random(seed)
    objs = [tube(name, [(0, 0, 0), (0.05, 0, h * 0.5), (0.12, 0.05, h)], [0.09, 0.06, 0.03], 8, stalk_m)]
    for k in range(9):
        z = h * (0.5 + 0.48 * k / 8)
        a = k * 2.4
        L = 0.5 * (1 - k / 10) + 0.15
        p0 = Vector((0.05 + 0.07 * k / 8, 0.02 * k / 8, z))
        p1 = p0 + Vector((math.cos(a) * L, math.sin(a) * L, 0.25))
        objs.append(tube(f"{name}_br{k}", [p0, p1], [0.025, 0.012], 6, stalk_m))
        if hero and k in (2, 3, 4):
            tm = C_simple("agave_tube", "#C8B83A", 0.5)
            sm = C_simple("agave_stamen", "#F2D84A", 0.45)
            am = C_simple("agave_anther", "#B8862A", 0.6)
            for ob in flower_cluster(f"{name}_hfl{k}", p1 + Vector((0, 0, 0.06)), 0.17 * (1 - k / 14), tm, sm, am,
                                     seed=k):
                ob.location = Vector(ob.location) - Vector((0, 0, 0))
                objs.append(ob)
            if clusters is not None:
                clusters.append(p1 + Vector((0, 0, 0.06)))
            continue
        cl = icosphere(f"{name}_fl{k}", 0.17 * (1 - k / 14), 2, flower_m)
        cl.location = p1 + Vector((0, 0, 0.06))
        if clusters is not None:
            clusters.append(Vector(cl.location))
        cl.scale = (1.0, 1.0, 0.7)
        disp(cl, 0.08, 0.05, depth=1)
        objs.append(cl)
    return objs


def corn_plant(name, leaf_m, stalk_m, tassel_m, ear_m, h=2.2, seed=1):
    rnd = random.Random(seed)
    parts = [tube(name + "_stalk", [(0, 0, 0), (0, 0.02, h * 0.5), (0.02, 0.0, h)], [0.022, 0.018, 0.01], 6, stalk_m)]
    leaves = []
    for k in range(11):
        z = h * (0.12 + 0.7 * k / 10)
        a = k * math.pi + rnd.uniform(-0.3, 0.3)
        v, f = blade(0.9 * (1 - abs(k - 5) / 12), 0.085, 2.0, 8, twist=rnd.uniform(-0.3, 0.3))
        M = Matrix.Translation((0, 0, z)) @ _rz(a) @ _rx(-0.55)
        leaves.append((v, f, M))
    V, F = combine(leaves)
    parts.append(mesh_ob(name + "_leaves", V, F, leaf_m))
    tas = []
    for k in range(7):
        v, f = blade(0.28, 0.01, 1.2, 4)
        tas.append((v, f, Matrix.Translation((0.02, 0, h)) @ _rz(k * 0.9) @ _rx(-0.4)))
    V, F = combine(tas)
    parts.append(mesh_ob(name + "_tassel", V, F, tassel_m))
    ear = icosphere(name + "_ear", 0.05, 2, ear_m)
    ear.scale = (0.8, 0.8, 3.2)
    ear.location = (0.05, 0, h * 0.55)
    ear.rotation_euler = (0, 0.35, 0)
    parts.append(ear)
    return parts


def bare_tree(name, mat, h=12.0, seed=1, depth=4, lean=0.0):
    """Gnarled leafless tree for moonlit silhouettes: recursive forking limbs with kinks and taper."""
    rnd = random.Random(seed)
    objs = []

    def limb(p0, d, length, r0, lvl, k):
        pts, rad = [p0], [r0]
        p = p0.copy()
        n = 4
        for i in range(1, n + 1):
            d = (d + Vector((rnd.gauss(0, 0.22), rnd.gauss(0, 0.22), rnd.gauss(0.04, 0.12)))).normalized()
            p = p + d * (length / n)
            pts.append(p.copy())
            rad.append(r0 * (1 - 0.55 * i / n))
        objs.append(tube(f"{name}_l{lvl}_{k}", pts, rad, max(5, 10 - 2 * lvl), mat))
        if lvl < depth:
            nb = 2 if lvl == 0 else rnd.choice((2, 2, 3))
            for j in range(nb):
                a = rnd.uniform(0, 6.283)
                side = Vector((math.cos(a), math.sin(a), 0))
                nd = (d * 0.55 + side * rnd.uniform(0.45, 0.8) + Vector((0, 0, rnd.uniform(0.1, 0.45)))).normalized()
                start = pts[-1] if j == 0 else pts[rnd.randint(2, n)]
                limb(start, nd, length * rnd.uniform(0.55, 0.75), rad[-1] * 1.15 if j == 0 else rad[-2],
                     lvl + 1, k * 4 + j)
    limb(Vector((0, 0, 0)), Vector((lean, 0, 1)).normalized(), h * 0.42, h * 0.045, 0, 0)
    return objs


def cotton_plant(name, leaf_m, boll_m, stem_m, h=1.0, seed=1):
    rnd = random.Random(seed)
    parts = [tube(name + "_stem", [(0, 0, 0), (0, 0, h * 0.9)], [0.012, 0.006], 5, stem_m)]
    leaves = []
    for k in range(14):
        z = h * rnd.uniform(0.25, 0.95)
        v, f = blade(0.16, 0.13, 0.5, 4, fold=0.2)
        leaves.append((v, f, Matrix.Translation((0, 0, z)) @ _rz(rnd.uniform(0, 6.28)) @ _rx(-1.1)))
    V, F = combine(leaves)
    parts.append(mesh_ob(name + "_leaves", V, F, leaf_m))
    for k in range(7):
        b = icosphere(f"{name}_boll{k}", 0.045, 2, boll_m)
        b.location = (rnd.gauss(0, 0.15), rnd.gauss(0, 0.15), h * rnd.uniform(0.4, 1.0))
        disp(b, 0.03, 0.02, depth=1)
        parts.append(b)
    return parts


def prickly_pear(name, pad_m, flower_m, fruit_m, seed=1, n=9):
    rnd = random.Random(seed)
    objs = []

    def pad(c, rot, s):
        p = icosphere(f"{name}_pad{len(objs)}", 0.16 * s, 3, pad_m)
        p.scale = (1.0, 0.22, 1.25)
        p.location = c
        p.rotation_euler = rot
        objs.append(p)
        return p
    pad(Vector((0, 0, 0.18)), (0, 0, rnd.random()), 1.0)
    for k in range(n - 1):
        a = rnd.uniform(0, 6.28)
        c = Vector((math.cos(a) * 0.22, math.sin(a) * 0.22, 0.38 + rnd.uniform(0, 0.25)))
        pad(c, (rnd.uniform(-0.4, 0.4), rnd.uniform(-0.5, 0.5), a), rnd.uniform(0.7, 0.95))
        if k % 2 == 0:
            top = c + Vector((0, 0, 0.18))
            f = icosphere(f"{name}_fl{k}", 0.04, 2, flower_m if k % 4 == 0 else fruit_m)
            f.location = top
            f.scale = (1, 1, 0.7 if k % 4 == 0 else 1.3)
            objs.append(f)
    return objs


def banana(name, leaf_m, stem_m, h=2.6, seed=1):
    rnd = random.Random(seed)
    objs = [tube(name + "_stem", [(0, 0, 0), (0, 0, h * 0.6)], [0.12, 0.09], 8, stem_m)]
    parts = []
    for k in range(8):
        v, f = blade(1.8, 0.55, 1.2, 9, fold=0.15)
        parts.append((v, f, Matrix.Translation((0, 0, h * 0.58)) @ _rz(k * 0.8 + rnd.random() * 0.3)
                      @ _rx(-0.5 - rnd.uniform(0, 0.5))))
    V, F = combine(parts)
    objs.append(mesh_ob(name + "_leaves", V, F, leaf_m))
    return objs


def fern(name, leaf_m, seed=1, s=1.0):
    rnd = random.Random(seed)
    parts = []
    for k in range(10):
        v, f = blade(0.9 * s, 0.22 * s, 1.6, 8, fold=-0.2)
        parts.append((v, f, _rz(k * 0.63 + rnd.random() * 0.3) @ _rx(-0.6 - rnd.uniform(0, 0.4))))
    V, F = combine(parts)
    return mesh_ob(name, V, F, leaf_m)


def seedling(name, leaf_m, stem_m, h=0.35, seed=1):
    rnd = random.Random(seed)
    objs = [tube(name + "_stem", [(0, 0, 0), (0.01, 0, h)], [0.006, 0.003], 5, stem_m)]
    parts = []
    for k in range(5):
        v, f = blade(0.12, 0.07, 0.4, 3)
        parts.append((v, f, Matrix.Translation((0, 0, h * (0.5 + 0.12 * k))) @ _rz(k * 2.4) @ _rx(-1.0)))
    V, F = combine(parts)
    objs.append(mesh_ob(name + "_lv", V, F, leaf_m))
    return objs


def rock(name, size, mat, seed=1, flat=0.7, rough=0.35):
    r = icosphere(name, size, 3, mat)
    r.scale = (1.0, random.Random(seed).uniform(0.7, 1.0), flat)
    disp(r, size * rough, size * 0.45, depth=3)
    tex = r.modifiers["disp"].texture
    tex.noise_basis = "VORONOI_F1"
    return r


# ------------------------------------------------------------------ scattering (Geometry Nodes)
def to_collection(objs, name):
    """Move objects into a hidden collection to be used as instance sources."""
    col = bpy.data.collections.get(name) or bpy.data.collections.new(name)
    if name not in bpy.context.scene.collection.children:
        bpy.context.scene.collection.children.link(col)
    for ob in objs:
        for c in list(ob.users_collection):
            c.objects.unlink(ob)
        col.objects.link(ob)
        ob.location = ob.location   # keep local placement
    col.hide_render = True
    col.hide_viewport = True
    return col


def group_objects(objs, name):
    """Parent a list of objects under one empty (a 'prefab')."""
    e = link(bpy.data.objects.new(name, None))
    for ob in objs:
        ob.parent = e
    return e


def scatter(target, col, density, seed=1, scale=(0.8, 1.2), mask=None, rot_tilt=0.12, name="scatter",
            align=False, min_dist=0.0):
    """Instance a collection's objects over `target`'s faces. mask: vertex-group name scaling density."""
    ng = bpy.data.node_groups.new(name, "GeometryNodeTree")
    ng.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    ng.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    N = ng.nodes
    L = ng.links
    gi = N.new("NodeGroupInput")
    go = N.new("NodeGroupOutput")
    dist = N.new("GeometryNodeDistributePointsOnFaces")
    if min_dist:
        dist.distribute_method = "POISSON"
        dist.inputs["Distance Min"].default_value = min_dist
        dist.inputs["Density Max"].default_value = density
    else:
        dist.inputs["Density"].default_value = density
    dist.inputs["Seed"].default_value = seed
    L.new(gi.outputs[0], dist.inputs["Mesh"])
    if mask:
        na = N.new("GeometryNodeInputNamedAttribute")
        na.data_type = "FLOAT"
        na.inputs["Name"].default_value = mask
        mul = N.new("ShaderNodeMath")
        mul.operation = "MULTIPLY"
        mul.inputs[1].default_value = density
        L.new(na.outputs["Attribute"], mul.inputs[0])
        L.new(mul.outputs[0], dist.inputs["Density Factor"] if min_dist else dist.inputs["Density"])
        if min_dist:
            L.new(na.outputs["Attribute"], dist.inputs["Density Factor"])
    ci = N.new("GeometryNodeCollectionInfo")
    ci.inputs["Collection"].default_value = col
    ci.inputs["Separate Children"].default_value = True
    ci.inputs["Reset Children"].default_value = True
    ci.transform_space = "ORIGINAL"
    iop = N.new("GeometryNodeInstanceOnPoints")
    iop.inputs["Pick Instance"].default_value = True
    rv_i = N.new("FunctionNodeRandomValue")
    rv_i.data_type = "INT"
    rv_i.inputs["Min"].default_value = 0
    rv_i.inputs["Max"].default_value = 100
    rv_i.inputs["Seed"].default_value = seed + 7
    rv_r = N.new("FunctionNodeRandomValue")
    rv_r.data_type = "FLOAT_VECTOR"
    rv_r.inputs["Min"].default_value = (-rot_tilt, -rot_tilt, 0.0)
    rv_r.inputs["Max"].default_value = (rot_tilt, rot_tilt, 6.283)
    rv_r.inputs["Seed"].default_value = seed + 3
    rv_s = N.new("FunctionNodeRandomValue")
    rv_s.data_type = "FLOAT"
    rv_s.inputs["Min"].default_value = scale[0]
    rv_s.inputs["Max"].default_value = scale[1]
    rv_s.inputs["Seed"].default_value = seed + 5
    L.new(dist.outputs["Points"], iop.inputs["Points"])
    L.new(ci.outputs[0], iop.inputs["Instance"])
    L.new(rv_i.outputs[2], iop.inputs["Instance Index"])
    L.new(rv_r.outputs[0], iop.inputs["Rotation"])
    L.new(rv_s.outputs[1], iop.inputs["Scale"])
    jn = N.new("GeometryNodeJoinGeometry")
    L.new(gi.outputs[0], jn.inputs[0])
    L.new(iop.outputs[0], jn.inputs[0])
    L.new(jn.outputs[0], go.inputs[0])
    mod = target.modifiers.new(name, "NODES")
    mod.node_group = ng
    return mod


def vgroup_from_fn(ob, name, fn):
    """Vertex group with weights fn(world_co) in 0..1 (for scatter masks)."""
    vg = ob.vertex_groups.new(name=name)
    mw = ob.matrix_world
    buckets = {}
    for v in ob.data.vertices:
        w = max(0.0, min(1.0, fn(mw @ v.co)))
        if w > 0.01:
            buckets.setdefault(round(w, 2), []).append(v.index)
    for w, idx in buckets.items():
        vg.add(idx, w, "REPLACE")
    return name


# ------------------------------------------------------------------ leaf-card foliage
_LEAF = {}


def leaf_mesh(kind="broad", size=0.18):
    key = (kind, size)
    if key in _LEAF:
        return _LEAF[key]
    if kind == "broad":      # simple folded leaf with a pointed tip
        pts = [(0, 0, 0), (-0.32, 0.25, 0.04), (-0.38, 0.6, 0.06), (-0.2, 0.88, 0.04), (0, 1.0, 0.0),
               (0.2, 0.88, 0.04), (0.38, 0.6, 0.06), (0.32, 0.25, 0.04), (0, 0.5, -0.05)]
        faces = [(0, 1, 8), (1, 2, 8), (2, 3, 8), (3, 4, 8), (4, 5, 8), (5, 6, 8), (6, 7, 8), (7, 0, 8)]
    elif kind == "needle":   # juniper sprig: narrow scale-leaf spray
        pts = [(0, 0, 0), (-0.12, 0.5, 0.02), (0, 1.0, 0.0), (0.12, 0.5, 0.02), (0, 0.5, -0.03)]
        faces = [(0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4)]
    else:                    # long tropical leaf
        pts = [(0, 0, 0), (-0.22, 0.3, 0.05), (-0.25, 0.7, 0.05), (0, 1.0, 0.0), (0.25, 0.7, 0.05),
               (0.22, 0.3, 0.05), (0, 0.5, -0.06)]
        faces = [(0, 1, 6), (1, 2, 6), (2, 3, 6), (3, 4, 6), (4, 5, 6), (5, 0, 6)]
    me = bpy.data.meshes.new(f"leaf_{kind}")
    me.from_pydata([(x * size, y * size * (1.6 if kind != "needle" else 1.0), z * size) for x, y, z in pts], [],
                   faces)
    me.update()
    ob = bpy.data.objects.new(f"leaf_{kind}_{size}", me)
    col = bpy.data.collections.get("TEMPLATES")
    if col is None:
        col = bpy.data.collections.new("TEMPLATES")
        bpy.context.scene.collection.children.link(col)
        col.hide_render = True
        col.hide_viewport = True
    col.objects.link(ob)
    _LEAF[key] = ob
    return ob


def foliage(blob, leaf_m, kind="broad", size=0.18, density=60.0, seed=1, inner_m=None):
    """Cover a canopy mass with instanced leaves aligned to its surface (keeps the mass as a dark core)."""
    leaf = leaf_mesh(kind, size)
    if leaf.data.materials:
        leaf.data.materials[0] = leaf_m
    else:
        leaf.data.materials.append(leaf_m)
    ng = bpy.data.node_groups.get(f"foliage_{kind}_{size}_{density}")
    if ng is None:
        ng = bpy.data.node_groups.new(f"foliage_{kind}_{size}_{density}", "GeometryNodeTree")
        ng.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
        ng.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
        N, L = ng.nodes, ng.links
        gi, go = N.new("NodeGroupInput"), N.new("NodeGroupOutput")
        dist = N.new("GeometryNodeDistributePointsOnFaces")
        dist.inputs["Density"].default_value = density
        dist.inputs["Seed"].default_value = seed
        L.new(gi.outputs[0], dist.inputs["Mesh"])
        oi = N.new("GeometryNodeObjectInfo")
        oi.inputs["Object"].default_value = leaf
        iop = N.new("GeometryNodeInstanceOnPoints")
        # align leaf Z to the surface normal, then randomise the spin and tilt
        al = N.new("FunctionNodeAlignEulerToVector")
        al.axis = "Z"
        L.new(dist.outputs["Normal"], al.inputs["Vector"])
        rv = N.new("FunctionNodeRandomValue")
        rv.data_type = "FLOAT_VECTOR"
        rv.inputs["Min"].default_value = (-0.6, -0.6, -3.14)
        rv.inputs["Max"].default_value = (0.6, 0.6, 3.14)
        add = N.new("ShaderNodeVectorMath")
        add.operation = "ADD"
        L.new(al.outputs[0], add.inputs[0])
        L.new(rv.outputs[0], add.inputs[1])
        rs = N.new("FunctionNodeRandomValue")
        rs.data_type = "FLOAT"
        rs.inputs["Min"].default_value = 0.7
        rs.inputs["Max"].default_value = 1.3
        L.new(dist.outputs["Points"], iop.inputs["Points"])
        L.new(oi.outputs["Geometry"], iop.inputs["Instance"])
        L.new(add.outputs[0], iop.inputs["Rotation"])
        L.new(rs.outputs[1], iop.inputs["Scale"])
        jn = N.new("GeometryNodeJoinGeometry")
        L.new(gi.outputs[0], jn.inputs[0])
        L.new(iop.outputs[0], jn.inputs[0])
        L.new(jn.outputs[0], go.inputs[0])
    mod = blob.modifiers.new("foliage", "NODES")
    mod.node_group = ng
    if inner_m is not None:
        blob.data.materials.clear()
        blob.data.materials.append(inner_m)
    return mod
