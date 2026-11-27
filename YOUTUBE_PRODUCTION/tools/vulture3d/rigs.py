"""Episode 3 v2 animated characters: jointed puppets + procedural motion library (Blender 4.0).

Each character is a Puppet: an empty hierarchy (joints) with detailed parts parented to joints.
Rest pose is built at the origin (forward = +X for animals, -Y for Pip / villagers), then the root is placed.
Motion = Actor(puppet, action, params).update(t) sets joint rotations / root transform for time t (seconds).
All parts get the custom property mask=1 so the character pass can cut them out (see lib.add_mask_aov).
"""
import math
import random

import bmesh
import bpy
from mathutils import Euler, Matrix, Quaternion, Vector

import lib as L

TAU = 2 * math.pi


def smooth01(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def noise1(t, seed=0.0):
    """Cheap smooth 1D noise in [-1, 1]."""
    return (math.sin(t * 1.3 + seed) * 0.5 + math.sin(t * 2.7 + seed * 1.7) * 0.3 + math.sin(t * 4.1 + seed * 2.3) * 0.2)


# ------------------------------------------------------------------ materials (v2, richer)
def mat_feather(name, c1, c2, scale=22.0, bump=0.25, rough=0.85):
    """Feather-scallop pattern: Voronoi cells blended between two tones + bump."""
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Roughness"].default_value = rough
    try:
        b.inputs["Specular IOR Level"].default_value = 0.2
    except KeyError:
        pass
    tc = nt.nodes.new("ShaderNodeTexCoord")
    vor = nt.nodes.new("ShaderNodeTexVoronoi")
    vor.feature = "DISTANCE_TO_EDGE"
    vor.inputs["Scale"].default_value = scale
    nt.links.new(tc.outputs["Object"], vor.inputs["Vector"])
    nz = nt.nodes.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = scale * 0.25
    nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.0
    ramp.color_ramp.elements[0].color = (*L.hex_lin(c2), 1)
    ramp.color_ramp.elements[1].position = 0.12
    ramp.color_ramp.elements[1].color = (*L.hex_lin(c1), 1)
    nt.links.new(vor.outputs["Distance"], ramp.inputs["Fac"])
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    mix.blend_type = "MULTIPLY"
    mix.inputs["Factor"].default_value = 0.25
    nt.links.new(ramp.outputs["Color"], mix.inputs["A"])
    nt.links.new(nz.outputs["Color"], mix.inputs["B"])
    nt.links.new(mix.outputs["Result"], b.inputs["Base Color"])
    bm = nt.nodes.new("ShaderNodeBump")
    bm.inputs["Strength"].default_value = bump
    nt.links.new(vor.outputs["Distance"], bm.inputs["Height"])
    nt.links.new(bm.outputs["Normal"], b.inputs["Normal"])
    L.add_mask_aov(m)
    return m


def mat_fur(name, c1, c2, scale=40.0, rough=0.9):
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Roughness"].default_value = rough
    try:
        b.inputs["Specular IOR Level"].default_value = 0.15
    except KeyError:
        pass
    b.inputs["Subsurface Weight"].default_value = 0.08
    tc = nt.nodes.new("ShaderNodeTexCoord")
    nz = nt.nodes.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = scale
    nz.inputs["Detail"].default_value = 8
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (1, 1, 6)
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    nt.links.new(mp.outputs["Vector"], nz.inputs["Vector"])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.35
    ramp.color_ramp.elements[0].color = (*L.hex_lin(c2), 1)
    ramp.color_ramp.elements[1].position = 0.7
    ramp.color_ramp.elements[1].color = (*L.hex_lin(c1), 1)
    nt.links.new(nz.outputs["Fac"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], b.inputs["Base Color"])
    bm = nt.nodes.new("ShaderNodeBump")
    bm.inputs["Strength"].default_value = 0.2
    nt.links.new(nz.outputs["Fac"], bm.inputs["Height"])
    nt.links.new(bm.outputs["Normal"], b.inputs["Normal"])
    L.add_mask_aov(m)
    return m


def M2():
    return dict(
        v_body=mat_feather("v2_body", "#C4A47C", "#A2825C", 60, bump=0.12),
        v_cov=mat_feather("v2_cov", "#8A6A4A", "#6A4E35", 34, bump=0.18),
        v_prim=L.mat("v2_prim", "#2A211B", 0.7, noise=("#3D3027", 0.5), noise_scale=30),
        v_sec=L.mat("v2_sec", "#3A2D24", 0.75, noise=("#4C3B2F", 0.5), noise_scale=25),
        v_ruff=mat_fur("v2_ruff", "#F3ECDD", "#D9CDB6", 60),
        v_skin=L.mat("v2_skin", "#7A6A63", 0.55, sss=0.15, noise=("#8E7A70", 0.5), noise_scale=20),
        v_skin_dark=L.mat("v2_skin_dark", "#4E4440", 0.6),
        v_beak=L.mat("v2_beak", "#3C3734", 0.35, spec=0.5),
        v_cere=L.mat("v2_cere", "#9AA3A6", 0.5),
        v_leg=L.mat("v2_leg", "#8D8781", 0.6, noise=("#77716B", 0.6), noise_scale=60),
        talon=L.mat("v2_talon", "#1E1B19", 0.3, spec=0.6),
        eye=L.mat("v2_eye", "#2B160C", 0.12, spec=0.9),
        eye_hi=L.mat("v2_eyehi", "#FFFFFF", 0.2, emit=2.0),
        dog=mat_fur("v2_dog", "#C99A5E", "#A87A44", 35),
        dog_cream=mat_fur("v2_dogcream", "#EEDDBE", "#D9C29C", 40),
        dog_dark=L.mat("v2_dogdark", "#6B4A2C", 0.8),
        nose=L.mat("v2_nose", "#151313", 0.25, spec=0.7),
        crow=L.mat("v2_crow", "#17161A", 0.4, spec=0.55, noise=("#24232B", 0.5), noise_scale=30),
        crow_grey=mat_fur("v2_crowgrey", "#6A666A", "#55525A", 50),
        cow=mat_fur("v2_cow", "#E3DED4", "#C9C1B3", 12),
        cow_dark=mat_fur("v2_cowdark", "#8C857B", "#6E675E", 20),
        horn=L.mat("v2_horn", "#3D332B", 0.45, spec=0.4),
        hoof=L.mat("v2_hoof", "#2A2420", 0.5),
        pip_skin=L.mat("v2_pipskin", "#F7F1E3", 0.5, sss=0.2),
        pip_hat=mat_fur("v2_piphat", "#F2B33D", "#E09F2A", 30),
        pip_band=L.mat("v2_pipband", "#B7731B", 0.7),
        pip_vest=mat_fur("v2_pipvest", "#6E8B3D", "#5E7A33", 45),
        pip_shirt=mat_fur("v2_pipshirt", "#F1E7D2", "#E2D5BA", 50),
        pip_pants=mat_fur("v2_pippants", "#6E5139", "#5C432F", 45),
        pip_boot=L.mat("v2_pipboot", "#4A3221", 0.5, spec=0.4),
        pip_glass=L.mat("v2_pipglass", "#3B2A1E", 0.3, spec=0.6),
        pip_dark=L.mat("v2_pipdark", "#221B16", 0.4),
        blush=L.mat("v2_blush", "#F2A08E", 0.7),
        bag=mat_fur("v2_bag", "#8A5A35", "#764B2B", 30),
        metal=L.mat("v2_metal", "#3A3A3D", 0.3, spec=0.8),
        mouth=L.mat("v2_mouth", "#5A2A26", 0.5),
    )


# ------------------------------------------------------------------ geometry helpers
_FEATHER = {}


def feather_mesh(kind="long"):
    """Shared tapered, slightly curved feather blade (length 1 along -X from the base at origin)."""
    if kind in _FEATHER:
        return _FEATHER[kind]
    w = {"long": 0.16, "wide": 0.26, "short": 0.3, "tail": 0.22}[kind]
    n = 10
    bm = bmesh.new()
    top, bot = [], []
    for i in range(n + 1):
        u = i / n
        width = w * (math.sin(math.pi * min(1.0, u * 1.05)) ** 0.6 if u < 0.96 else 0.25 * (1 - u) / 0.04 + 0.02)
        z = 0.06 * math.sin(math.pi * u)
        top.append((bm.verts.new((-u, -width / 2, z)), bm.verts.new((-u, width / 2, z))))
        bot.append((bm.verts.new((-u, -width / 2, z - 0.012)), bm.verts.new((-u, width / 2, z - 0.012))))
    for i in range(n):
        bm.faces.new([top[i][0], top[i + 1][0], top[i + 1][1], top[i][1]])
        bm.faces.new([bot[i][1], bot[i + 1][1], bot[i + 1][0], bot[i][0]])
        bm.faces.new([top[i][0], bot[i][0], bot[i + 1][0], top[i + 1][0]])
        bm.faces.new([top[i + 1][1], bot[i + 1][1], bot[i][1], top[i][1]])
    me = bpy.data.meshes.new("feather_" + kind)
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    me.materials.append(L.mat("feather_placeholder", "#777777"))
    _FEATHER[kind] = me
    return me


def feather(name, m, base, direction, length, width_scale=1.0, kind="long", roll=0.0):
    ob = L.link(bpy.data.objects.new(name, feather_mesh(kind)))
    ob.material_slots[0].link = "OBJECT"
    ob.material_slots[0].material = m
    d = Vector(direction).normalized()
    q = Vector((-1, 0, 0)).rotation_difference(d)
    ob.rotation_mode = "QUATERNION"
    ob.rotation_quaternion = q @ Quaternion((1, 0, 0), roll)
    ob.location = base
    ob.scale = (length, width_scale * length * 0.9 + 0.1, length)
    return ob


def ell(name, m, loc, size, rot=(0, 0, 0), seg=24):
    return L.prim("sphere", name, loc, size, rot, m=m, seg=seg)


def caps(name, m, a, b, r, res=0.025):
    return L.meta(name, [L.seg_capsule(a, b, r)], m, res=res)


# ------------------------------------------------------------------ puppet
class Puppet:
    def __init__(self, name):
        self.name = name
        self.root = L.link(bpy.data.objects.new(name, None))
        self.J = {"root": (self.root, Vector((0, 0, 0)))}
        self.groups = {}       # visibility groups (e.g. folded / spread wings)
        self.objs = []

    def joint(self, name, parent, pos):
        e = L.link(bpy.data.objects.new(f"{self.name}.{name}", None))
        pe, ppos = self.J[parent]
        e.parent = pe
        e.matrix_parent_inverse = Matrix.Translation(-ppos)
        e.location = pos
        self.J[name] = (e, Vector(pos))
        return e

    def add(self, ob, joint, group=None):
        je, jpos = self.J[joint]
        ob.parent = je
        ob.matrix_parent_inverse = Matrix.Translation(-jpos)
        ob["mask"] = 1.0
        ob["_joint"] = joint
        ob["_group"] = group or ""
        self.objs.append(ob)
        if group:
            self.groups.setdefault(group, []).append(ob)
        return ob

    def finalize(self):
        """Merge parts sharing (joint, visibility group) into one mesh: far fewer draw calls for Eevee.
        Eye/brow parts stay separate because they are scaled/rotated individually."""
        bpy.context.view_layer.update()
        dg = bpy.context.evaluated_depsgraph_get()
        buckets = {}
        keep = []
        for ob in self.objs:
            g = ob["_group"]
            if g.startswith("eye") or g.startswith("brow") or ob.type != "MESH":
                keep.append(ob)
                continue
            buckets.setdefault((ob["_joint"], g), []).append(ob)
        new_groups = {g: [o for o in obs if o in keep] for g, obs in self.groups.items()}
        new_objs = list(keep)
        for (jn, g), obs in buckets.items():
            if len(obs) == 1:
                new_objs.append(obs[0])
                if g:
                    new_groups.setdefault(g, []).append(obs[0])
                continue
            bm = bmesh.new()
            mats = []
            for ob in obs:
                me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
                me.transform(ob.matrix_world)
                smap = []
                for slot in ob.material_slots:
                    if slot.material not in mats:
                        mats.append(slot.material)
                    smap.append(mats.index(slot.material))
                if smap:
                    for poly in me.polygons:
                        poly.material_index = smap[min(poly.material_index, len(smap) - 1)]
                tmp = bmesh.new()
                tmp.from_mesh(me)
                offset = len(bm.verts)
                vmap = [bm.verts.new(v.co) for v in tmp.verts]
                for f in tmp.faces:
                    try:
                        nf = bm.faces.new([vmap[v.index] for v in f.verts])
                        nf.material_index = f.material_index
                        nf.smooth = f.smooth
                    except ValueError:
                        pass
                tmp.free()
                bpy.data.meshes.remove(me)
            merged = bpy.data.meshes.new(f"{self.name}_{jn}_{g or 'base'}")
            bm.to_mesh(merged)
            bm.free()
            for m in mats:
                merged.materials.append(m)
            mo = L.link(bpy.data.objects.new(merged.name, merged))
            je, jpos = self.J[jn]
            mo.parent = je
            mo.matrix_parent_inverse = Matrix.Translation(-jpos) @ je.matrix_world.inverted() @ Matrix.Translation(jpos) \
                if False else Matrix.Translation(-jpos)
            mo.matrix_parent_inverse = Matrix.Translation(-jpos)
            mo["mask"] = 1.0
            mo["_joint"] = jn
            mo["_group"] = g
            new_objs.append(mo)
            if g:
                new_groups.setdefault(g, []).append(mo)
            for ob in obs:
                bpy.data.objects.remove(ob, do_unlink=True)
        self.objs = new_objs
        self.groups = new_groups

    def rot(self, joint, x=0.0, y=0.0, z=0.0):
        self.J[joint][0].rotation_euler = (x, y, z)

    def show(self, group, on):
        for o in self.groups.get(group, []):
            o.hide_render = not on
            o.hide_viewport = not on

    def place(self, loc, rz=0.0, scale=1.0):
        self.root.location = loc
        self.root.rotation_euler = (0, 0, rz)
        self.root.scale = (scale,) * 3
        self.base_loc = Vector(loc)
        self.base_rz = rz
        self.base_scale = scale


# ------------------------------------------------------------------ VULTURE v2
def build_vulture(M, name="vulture", seed=0):
    rnd = random.Random(seed)
    P = Puppet(name)
    body_c = Vector((0, 0, 0.55))
    P.joint("body", "root", body_c)
    P.joint("neck1", "body", (0.26, 0, 0.78))
    P.joint("neck2", "neck1", (0.36, 0, 0.95))
    P.joint("head", "neck2", (0.44, 0, 1.08))
    P.joint("tail", "body", (-0.42, 0, 0.5))
    for s, side in ((1, "L"), (-1, "R")):
        P.joint("wing" + side, "body", (0.08, s * 0.2, 0.72))
        P.joint("hand" + side, "wing" + side, (0.02, s * 0.85, 0.74))
        P.joint("leg" + side, "body", (0.04, s * 0.11, 0.32))
    # body: breast + back + belly
    body = L.meta(name + "_body", [
        dict(type="ELLIPSOID", co=(0.02, 0, 0.56), size=(0.42, 0.25, 0.28), rot=Quaternion((0, 1, 0), 0.32)),
        dict(type="ELLIPSOID", co=(0.15, 0, 0.6), size=(0.24, 0.22, 0.25)),
        dict(type="ELLIPSOID", co=(-0.3, 0, 0.5), size=(0.25, 0.17, 0.1), rot=Quaternion((0, 1, 0), 0.25)),
    ], M["v_body"], res=0.03)
    P.add(body, "body")
    # thighs (feathered "trousers")
    for s in (1, -1):
        P.add(ell(name + "_thigh", M["v_body"], (0.02, s * 0.12, 0.33), (0.13, 0.09, 0.14)), "body")
    # ruff: fluffy collar of feather tufts
    for k in range(30):
        a = TAU * k / 30
        base = Vector((0.24, 0.14 * math.cos(a), 0.78 + 0.1 * math.sin(a)))
        out = Vector((-0.25, math.cos(a), math.sin(a) * 0.8)).normalized()
        f = ell(name + "_ruff", M["v_ruff"], tuple(base + out * 0.04), (0.075, 0.04, 0.035), seg=10)
        f.rotation_mode = "QUATERNION"
        f.rotation_quaternion = Vector((1, 0, 0)).rotation_difference(out) @ Quaternion((1, 0, 0), rnd.uniform(0, 3))
        P.add(f, "body")
    P.add(ell(name + "_ruffcore", M["v_ruff"], (0.25, 0, 0.79), (0.08, 0.14, 0.11), seg=16), "body")
    # neck (bare skin, two segments)
    P.add(L.meta(name + "_neck1", [L.seg_capsule((0.26, 0, 0.78), (0.36, 0, 0.95), 0.058),
                                   dict(co=(0.36, 0, 0.95), r=0.058)], M["v_skin"], res=0.02), "neck1")
    P.add(L.meta(name + "_neck2", [L.seg_capsule((0.36, 0, 0.95), (0.44, 0, 1.08), 0.054)], M["v_skin"], res=0.02),
          "neck2")
    # head: skull + brow + cheek, bare skin
    hc = Vector((0.46, 0, 1.1))
    P.add(L.meta(name + "_head", [dict(type="ELLIPSOID", co=tuple(hc), size=(0.11, 0.085, 0.085)),
                                  dict(type="ELLIPSOID", co=tuple(hc + Vector((0.07, 0, -0.01))), size=(0.08, 0.065, 0.065)),
                                  dict(type="ELLIPSOID", co=tuple(hc + Vector((0.02, 0, 0.045))), size=(0.08, 0.07, 0.035))],
                 M["v_skin"], res=0.015), "head")
    for s in (1, -1):
        P.add(ell(name + "_brow", M["v_skin_dark"], tuple(hc + Vector((0.055, s * 0.055, 0.04))), (0.04, 0.02, 0.014),
                  rot=(s * 0.4, 0, 0), seg=12), "head")
        eye = ell(name + "_eye", M["eye"], tuple(hc + Vector((0.065, s * 0.062, 0.018))), (0.021, 0.014, 0.021), seg=14)
        P.add(eye, "head", group="eye")
        hi = ell(name + "_eyehi", M["eye_hi"], tuple(hc + Vector((0.08, s * 0.072, 0.03))), (0.006, 0.004, 0.006), seg=8)
        P.add(hi, "head", group="eye")
    # beak: cere + hooked bill
    P.add(ell(name + "_cere", M["v_cere"], tuple(hc + Vector((0.14, 0, 0.0))), (0.05, 0.04, 0.035)), "head")
    P.add(L.meta(name + "_beak", [L.seg_capsule(hc + Vector((0.15, 0, 0.0)), hc + Vector((0.27, 0, -0.005)), 0.03),
                                  L.seg_capsule(hc + Vector((0.27, 0, -0.005)), hc + Vector((0.3, 0, -0.06)), 0.018)],
                 M["v_beak"], res=0.01), "head")
    # folded wings (visible when perched / standing)
    q = Quaternion((0, 1, 0), 0.18)
    for s in (1, -1):
        P.add(L.meta(name + "_fold", [dict(type="ELLIPSOID", co=(-0.04, s * 0.235, 0.62), size=(0.42, 0.075, 0.23), rot=q)],
                     M["v_cov"]), "body", group="folded")
        for k in range(6):
            f = feather(name + "_ffold", M["v_prim" if k < 3 else "v_sec"], (0.02 - k * 0.05, s * (0.27 + 0.004 * k),
                                                                              0.66 - k * 0.02),
                        (-1, s * 0.02, -0.38 + k * 0.04), 0.78 - k * 0.06, 1.25, "wide", roll=s * 1.4)
            P.add(f, "body", group="folded")
    # spread wings: inner (secondaries + coverts) on wing joint, outer (primaries) on hand joint
    for s, side in ((1, "L"), (-1, "R")):
        for k in range(9):
            y = s * (0.22 + k * 0.075)
            f = feather(name + "_sec", M["v_sec"], (-0.02, y, 0.73), (-1, s * 0.05, 0), 0.5 + 0.03 * math.sin(k),
                        1.1, "wide")
            P.add(f, "wing" + side, group="spread")
        P.add(ell(name + "_wcov", M["v_cov"], (0.03, s * 0.55, 0.745), (0.17, 0.37, 0.035), seg=20), "wing" + side,
              group="spread")
        P.add(ell(name + "_wlead", M["v_body"], (0.1, s * 0.5, 0.75), (0.07, 0.36, 0.04), seg=16), "wing" + side,
              group="spread")
        for k in range(7):
            ang = math.radians(-15 + k * 13)
            d = (-math.sin(ang) * 0.4 - 0.2, s * math.cos(ang), 0)
            f = feather(name + "_prim", M["v_prim"], (0.02 - k * 0.01, s * 0.86, 0.74), d, 0.62 - k * 0.025, 0.9, "long",
                        roll=0.0)
            P.add(f, "hand" + side, group="spread")
        P.add(ell(name + "_pcov", M["v_cov"], (0.0, s * 0.98, 0.745), (0.12, 0.16, 0.03), seg=16), "hand" + side,
              group="spread")
    # tail fan
    for k in range(6):
        ang = math.radians(-25 + k * 10)
        f = feather(name + "_tail", M["v_prim"], (-0.38, 0, 0.5), (-1, math.sin(ang), -0.25), 0.34, 1.0, "tail")
        P.add(f, "tail")
    # legs: tarsus + toes + talons
    for s, side in ((1, "L"), (-1, "R")):
        P.add(caps(name + "_tars", M["v_leg"], (0.04, s * 0.11, 0.3), (0.07, s * 0.12, 0.05), 0.026), "leg" + side)
        for k, (dx, dy) in enumerate(((0.13, 0.0), (0.11, 0.05), (0.11, -0.05), (-0.07, 0.0))):
            tip = (0.07 + dx, s * 0.12 + dy * s, 0.02)
            P.add(caps(name + "_toe", M["v_leg"], (0.07, s * 0.12, 0.04), tip, 0.014, 0.01), "leg" + side)
            P.add(ell(name + "_talon", M["talon"], tip, (0.018, 0.01, 0.012), seg=8), "leg" + side)
    P.finalize()
    P.show("spread", False)
    P.kind = "vulture"
    return P


# ------------------------------------------------------------------ DOG v2 (Indian pariah)
def build_dog(M, name="dog", coat=("#C99A5E", "#A87A44"), seed=0):
    P = Puppet(name)
    fur = mat_fur(f"v2_dog_{coat[0]}", coat[0], coat[1], 35)
    P.joint("body", "root", (0, 0, 0.58))
    P.joint("head", "body", (0.38, 0, 0.72))
    P.joint("tail", "body", (-0.42, 0, 0.66))
    P.joint("tail2", "tail", (-0.5, 0, 0.85))
    for nm, (x, y) in (("FL", (0.27, 0.11)), ("FR", (0.27, -0.11)), ("BL", (-0.3, 0.11)), ("BR", (-0.3, -0.11))):
        P.joint("leg" + nm, "body", (x, y, 0.5))
        P.joint("knee" + nm, "leg" + nm, (x, y, 0.27))
    for s, side in ((1, "L"), (-1, "R")):
        P.joint("ear" + side, "head", (0.5, s * 0.08, 0.92))
    P.add(L.meta(name + "_body", [dict(type="ELLIPSOID", co=(0.0, 0, 0.6), size=(0.42, 0.16, 0.17)),
                                  dict(type="ELLIPSOID", co=(0.24, 0, 0.62), size=(0.2, 0.17, 0.2)),
                                  dict(type="ELLIPSOID", co=(-0.27, 0, 0.6), size=(0.18, 0.15, 0.16))], fur, res=0.03),
          "body")
    P.add(ell(name + "_chest", M["dog_cream"], (0.3, 0, 0.56), (0.13, 0.12, 0.15)), "body")
    P.add(L.meta(name + "_neck", [L.seg_capsule((0.3, 0, 0.66), (0.42, 0, 0.8), 0.095)], fur, res=0.025), "head")
    hc = Vector((0.5, 0, 0.84))
    P.add(L.meta(name + "_head", [dict(type="ELLIPSOID", co=tuple(hc), size=(0.13, 0.11, 0.11)),
                                  L.seg_capsule(hc + Vector((0.06, 0, -0.03)), hc + Vector((0.2, 0, -0.05)), 0.055)],
                 fur, res=0.02), "head")
    P.add(ell(name + "_muzzle", M["dog_cream"], tuple(hc + Vector((0.16, 0, -0.07))), (0.08, 0.05, 0.035)), "head")
    P.add(ell(name + "_nose", M["nose"], tuple(hc + Vector((0.255, 0, -0.04))), (0.028, 0.03, 0.022), seg=12), "head")
    for s, side in ((1, "L"), (-1, "R")):
        P.add(ell(name + "_eye", M["eye"], tuple(hc + Vector((0.09, s * 0.07, 0.03))), (0.022, 0.016, 0.024), seg=12),
              "head", group="eye")
        P.add(ell(name + "_eyehi", M["eye_hi"], tuple(hc + Vector((0.105, s * 0.08, 0.042))), (0.006, 0.004, 0.006), seg=6),
              "head", group="eye")
        ear = L.prim("cone", name + "_ear", (0.5, s * 0.08, 0.98), (0.055, 0.03, 0.14), rot=(s * -0.2, -0.1, 0), m=fur,
                     seg=12)
        P.add(ear, "ear" + side)
        inner = L.prim("cone", name + "_earin", (0.505, s * 0.08, 0.97), (0.035, 0.012, 0.1), rot=(s * -0.2, -0.1, 0),
                       m=L.mat("v2_earin", "#D9A08A", 0.7), seg=10)
        P.add(inner, "ear" + side)
    P.add(L.meta(name + "_tail1", [L.seg_capsule((-0.42, 0, 0.66), (-0.5, 0, 0.85), 0.045)], fur, res=0.02), "tail")
    P.add(L.meta(name + "_tail2", [L.seg_capsule((-0.5, 0, 0.85), (-0.4, 0, 0.98), 0.04),
                                   dict(co=(-0.4, 0, 0.98), r=0.045)], fur, res=0.02), "tail2")
    for nm, (x, y) in (("FL", (0.27, 0.11)), ("FR", (0.27, -0.11)), ("BL", (-0.3, 0.11)), ("BR", (-0.3, -0.11))):
        P.add(caps(name + "_upper", fur, (x, y, 0.52), (x, y, 0.27), 0.05), "leg" + nm)
        P.add(caps(name + "_lower", fur, (x, y, 0.27), (x, y, 0.04), 0.038), "knee" + nm)
        P.add(ell(name + "_paw", M["dog_cream"], (x + 0.03, y, 0.03), (0.055, 0.045, 0.03)), "knee" + nm)
    P.finalize()
    P.kind = "dog"
    return P


# ------------------------------------------------------------------ CROW v2
def build_crow(M, name="crow"):
    P = Puppet(name)
    P.joint("body", "root", (0, 0, 0.22))
    P.joint("head", "body", (0.16, 0, 0.36))
    P.joint("tail", "body", (-0.16, 0, 0.26))
    P.joint("wingL", "body", (0.06, 0.08, 0.3))
    P.joint("wingR", "body", (0.06, -0.08, 0.3))
    P.add(L.meta(name + "_body", [dict(type="ELLIPSOID", co=(0, 0, 0.27), size=(0.2, 0.1, 0.11),
                                       rot=Quaternion((0, 1, 0), 0.3))], M["crow"], res=0.015), "body")
    P.add(ell(name + "_nape", M["crow_grey"], (0.13, 0, 0.36), (0.08, 0.085, 0.08)), "head")
    hc = Vector((0.2, 0, 0.4))
    P.add(ell(name + "_head", M["crow"], tuple(hc), (0.08, 0.07, 0.07)), "head")
    P.add(L.meta(name + "_beak", [L.seg_capsule(hc + Vector((0.05, 0, -0.01)), hc + Vector((0.11, 0, -0.025)), 0.02)],
                 M["crow"], res=0.008), "head")
    for s in (1, -1):
        P.add(ell(name + "_eye", M["eye"], tuple(hc + Vector((0.04, s * 0.055, 0.02))), (0.013, 0.01, 0.013), seg=8), "head")
        P.add(caps(name + "_leg", M["crow"], (0.0, s * 0.04, 0.19), (0.01, s * 0.04, 0.01), 0.013, 0.008), "body")
        P.add(feather(name + "_wing", M["crow"], (0.06, s * 0.08, 0.3), (-1, s * 0.1, -0.2), 0.26, 1.0, "wide",
                      roll=s * 1.3), "wing" + ("L" if s > 0 else "R"))
    P.add(feather(name + "_tailf", M["crow"], (-0.15, 0, 0.26), (-1, 0, -0.3), 0.18, 1.3, "tail"), "tail")
    P.finalize()
    P.kind = "crow"
    return P


# ------------------------------------------------------------------ COW v2 (standing zebu)
def build_cow(M, name="cow"):
    P = Puppet(name)
    P.joint("body", "root", (0, 0, 1.1))
    P.joint("head", "body", (0.85, 0, 1.3))
    P.joint("tail", "body", (-0.95, 0, 1.2))
    for s, side in ((1, "L"), (-1, "R")):
        P.joint("ear" + side, "head", (1.25, s * 0.2, 1.42))
    P.add(L.meta(name + "_body", [dict(type="ELLIPSOID", co=(0, 0, 1.1), size=(0.95, 0.4, 0.42)),
                                  dict(type="ELLIPSOID", co=(0.45, 0, 1.55), size=(0.24, 0.17, 0.22)),
                                  dict(type="ELLIPSOID", co=(0.75, 0, 0.9), size=(0.16, 0.08, 0.3))], M["cow"], res=0.04),
          "body")
    for x, y in ((0.6, 0.22), (0.6, -0.22), (-0.6, 0.22), (-0.6, -0.22)):
        P.add(caps(name + "_leg", M["cow"], (x, y, 0.95), (x, y, 0.08), 0.085, 0.03), "body")
        P.add(L.prim("cyl", name + "_hoof", (x, y, 0.05), (0.08, 0.08, 0.1), m=M["hoof"], seg=12), "body")
    P.add(L.meta(name + "_neck", [L.seg_capsule((0.75, 0, 1.25), (1.15, 0, 1.4), 0.2)], M["cow"], res=0.04), "head")
    hc = Vector((1.3, 0, 1.33))
    P.add(L.meta(name + "_head", [dict(type="ELLIPSOID", co=tuple(hc), size=(0.25, 0.17, 0.19)),
                                  L.seg_capsule(hc + Vector((0.1, 0, -0.05)), hc + Vector((0.3, 0, -0.15)), 0.11)],
                 M["cow_dark"], res=0.03), "head")
    P.add(ell(name + "_muzzle", M["nose"], tuple(hc + Vector((0.38, 0, -0.17))), (0.07, 0.1, 0.06)), "head")
    for s, side in ((1, "L"), (-1, "R")):
        P.add(L.prim("cone", name + "_horn", tuple(hc + Vector((-0.08, s * 0.17, 0.27))), (0.06, 0.06, 0.36),
                     rot=(s * -0.55, -0.35, 0), m=M["horn"], seg=12), "head")
        P.add(ell(name + "_ear", M["cow_dark"], (1.25, s * 0.28, 1.4), (0.14, 0.06, 0.05), rot=(0, 0.3, s * 0.4)),
              "ear" + side)
        P.add(ell(name + "_eye", M["eye"], tuple(hc + Vector((0.12, s * 0.15, 0.06))), (0.03, 0.02, 0.03), seg=10), "head",
              group="eye")
    P.add(L.meta(name + "_tail", [L.seg_capsule((-0.95, 0, 1.2), (-1.05, 0, 0.55), 0.03), dict(co=(-1.05, 0, 0.5), r=0.07)],
                 M["cow_dark"], res=0.015), "tail")
    P.finalize()
    P.kind = "cow"
    return P


# ------------------------------------------------------------------ PIP v2 (and villagers)
def build_person(M, name="pip", pip=True, skin="#F7F1E3", shirt=None, pants=None, hair=None, scale=1.0):
    """Forward = -Y. Pip: bucket hat, round glasses, olive vest. Villagers: hair + coloured clothes."""
    P = Puppet(name)
    sk = M["pip_skin"] if pip else L.mat("v2_skin_" + skin, skin, 0.5, sss=0.2)
    sh = M["pip_shirt"] if pip else mat_fur("v2_shirt_" + shirt, shirt, shirt, 50)
    pa = M["pip_pants"] if pip else mat_fur("v2_pants_" + pants, pants, pants, 45)
    P.joint("hips", "root", (0, 0, 0.82))
    P.joint("spine", "hips", (0, 0, 0.95))
    P.joint("head", "spine", (0, 0, 1.32))
    for s, side in ((1, "L"), (-1, "R")):
        P.joint("sh" + side, "spine", (s * 0.33, 0, 1.25))
        P.joint("el" + side, "sh" + side, (s * 0.36, 0, 0.98))
        P.joint("hip" + side, "hips", (s * 0.13, 0, 0.78))
        P.joint("knee" + side, "hip" + side, (s * 0.13, 0, 0.42))
    # torso
    P.add(L.meta(name + "_torso", [dict(type="ELLIPSOID", co=(0, 0, 1.0), size=(0.33, 0.27, 0.38))], sh, res=0.03),
          "spine")
    if pip:
        for s in (1, -1):
            vest = L.meta(name + "_vest", [dict(type="ELLIPSOID", co=(s * 0.1, 0.0, 1.0), size=(0.25, 0.3, 0.36))],
                          M["pip_vest"], res=0.03)
            P.add(vest, "spine")
            P.add(L.prim("cube", name + "_pocket", (s * 0.15, -0.28, 0.95), (0.13, 0.04, 0.11), m=M["pip_vest"]), "spine")
            P.add(L.prim("cube", name + "_flap", (s * 0.15, -0.3, 1.0), (0.14, 0.035, 0.035), m=M["pip_band"]), "spine")
        for k in range(3):
            P.add(ell(name + "_button", M["pip_band"], (0.0, -0.275, 0.9 + k * 0.1), (0.022, 0.012, 0.022), seg=8), "spine")
        strap = L.prim("torus", name + "_strap", (0.0, 0.0, 1.03), (0.34, 0.3, 0.42), rot=(0, 0.75, 0),
                       m=M["bag"], minor=0.07)
        P.add(strap, "spine")
        P.add(L.prim("cube", name + "_bag", (-0.33, -0.05, 0.72), (0.08, 0.24, 0.2), m=M["bag"]), "spine")
    # head + face
    hc = Vector((0, 0, 1.72))
    P.add(ell(name + "_head", sk, tuple(hc), (0.52, 0.5, 0.48), seg=40), "head")
    for s, side in ((1, "L"), (-1, "R")):
        P.add(ell(name + "_eye", M["pip_dark"], tuple(hc + Vector((s * 0.17, -0.455, 0.08))), (0.055, 0.03, 0.075), seg=16),
              "head", group="eye")
        P.add(ell(name + "_eyehi", M["eye_hi"], tuple(hc + Vector((s * 0.17 + 0.02, -0.485, 0.11))), (0.016, 0.01, 0.018),
                  seg=8), "head", group="eye")
        P.add(L.prim("cube", name + "_brow", tuple(hc + Vector((s * 0.17, -0.44, 0.22))), (0.11, 0.025, 0.028),
                     rot=(0.35, 0, s * -0.12), m=M["pip_dark"]), "head", group="brow" + side)
        P.add(ell(name + "_cheek", M["blush"], tuple(hc + Vector((s * 0.3, -0.38, -0.08))), (0.07, 0.02, 0.045), seg=12),
              "head")
        if pip:
            P.add(L.prim("torus", name + "_glass", tuple(hc + Vector((s * 0.17, -0.475, 0.08))), (0.12, 0.12, 0.12),
                         rot=(math.pi / 2 - 0.25, 0, 0), m=M["pip_glass"], minor=0.1), "head")
            P.add(L.prim("cyl", name + "_temple", tuple(hc + Vector((s * 0.36, -0.25, 0.1))), (0.012, 0.012, 0.34),
                         rot=(math.pi / 2, 0, s * 0.45), m=M["pip_glass"]), "head")
    if pip:
        P.add(L.prim("cyl", name + "_bridge", tuple(hc + Vector((0, -0.5, 0.09))), (0.012, 0.012, 0.1),
                     rot=(0, math.pi / 2, 0), m=M["pip_glass"]), "head")
    P.add(L.meta(name + "_smile", [L.seg_capsule(hc + Vector((-0.08, -0.47, -0.12)), hc + Vector((0, -0.48, -0.15)), 0.018),
                                   L.seg_capsule(hc + Vector((0, -0.48, -0.15)), hc + Vector((0.08, -0.47, -0.12)), 0.018)],
                 M["pip_dark"], res=0.008), "head", group="smile")
    P.add(ell(name + "_mouthO", M["mouth"], tuple(hc + Vector((0, -0.465, -0.14))), (0.05, 0.03, 0.055), seg=12), "head",
          group="talk")
    if pip:
        crown = L.prim("cyl", name + "_crown", tuple(hc + Vector((0, 0, 0.42))), (0.46, 0.46, 0.3), m=M["pip_hat"], seg=48)
        bv = crown.modifiers.new("bev", "BEVEL")
        bv.width = 0.1
        bv.segments = 4
        L.smooth(crown)
        P.add(crown, "head")
        P.add(L.prim("torus", name + "_brim", tuple(hc + Vector((0, 0, 0.29))), (0.62, 0.62, 0.35), m=M["pip_hat"],
                     minor=0.12, seg=48), "head")
        P.add(L.prim("cyl", name + "_brimdisc", tuple(hc + Vector((0, 0, 0.29))), (0.62, 0.62, 0.03), m=M["pip_hat"],
                     seg=48), "head")
        P.add(L.prim("cyl", name + "_band", tuple(hc + Vector((0, 0, 0.36))), (0.47, 0.47, 0.08), m=M["pip_band"], seg=48),
              "head")
    elif hair:
        hm = L.mat("v2_hair_" + hair, hair, 0.5, spec=0.4)
        P.add(ell(name + "_hair", hm, tuple(hc + Vector((0, 0.05, 0.13))), (0.5, 0.48, 0.4), seg=32), "head")
        P.add(ell(name + "_bun", hm, tuple(hc + Vector((0, 0.32, 0.25))), (0.16, 0.16, 0.16), seg=16), "head")
    # arms + hands
    for s, side in ((1, "L"), (-1, "R")):
        P.add(caps(name + "_upper", sh, (s * 0.33, 0, 1.25), (s * 0.36, 0, 0.98), 0.075), "sh" + side)
        P.add(caps(name + "_fore", sh, (s * 0.36, 0, 0.98), (s * 0.37, 0, 0.74), 0.065), "el" + side)
        P.add(ell(name + "_hand", sk, (s * 0.37, 0, 0.68), (0.095, 0.085, 0.1), seg=20), "el" + side)
        P.add(caps(name + "_thigh", pa, (s * 0.13, 0, 0.8), (s * 0.13, 0, 0.42), 0.09), "hip" + side)
        P.add(caps(name + "_shin", pa, (s * 0.13, 0, 0.42), (s * 0.13, 0, 0.12), 0.08), "knee" + side)
        P.add(ell(name + "_boot", M["pip_boot"], (s * 0.13, -0.07, 0.07), (0.12, 0.17, 0.08), seg=20), "knee" + side)
    if pip:
        for s in (1, -1):
            P.add(L.prim("cyl", name + "_bino", (s * 0.13, -0.62, 1.74), (0.08, 0.08, 0.26),
                         rot=(math.pi / 2, 0, 0), m=M["metal"]), "head", group="bino")
    P.finalize()
    P.show("talk", False)
    P.show("bino", False)
    P.kind = "pip" if pip else "villager"
    return P


# ------------------------------------------------------------------ motion
class Actor:
    """Binds a puppet to an action. Actions: see update_*."""

    def __init__(self, P, action, loc, rz=0.0, scale=1.0, seed=0, **kw):
        self.P, self.action, self.kw = P, action, kw
        self.seed = seed
        self.loc0 = Vector(loc)
        self.rz0 = rz
        self.scale = scale
        P.place(loc, rz, scale)

    def blink(self, t, every=3.7):
        ph = (t + self.seed * 1.37) % every
        k = 1.0
        if ph < 0.18:
            k = abs(ph - 0.09) / 0.09
        for o in self.P.groups.get("eye", []):
            if "sz0" not in o:
                o["sz0"] = o.scale.z
            o.scale.z = o["sz0"] * max(0.08, k)

    def update(self, t):
        sched = self.kw.get("schedule")
        if sched:
            t0, act = 0.0, self.action
            for entry in sched:
                if t >= entry[0]:
                    t0, act = entry[0], entry[1]
                    if len(entry) > 2:
                        self.kw.update(entry[2])
            self.action = act
            t = t - t0 if act in ("point", "binoculars", "look_up", "land", "wave") else t
        if self.action == "hidden":
            self.P.root.scale = (1e-4,) * 3
            return
        self.P.root.scale = (self.scale,) * 3
        f = getattr(self, "u_" + self.P.kind)
        f(t)

    # --- vulture
    def u_vulture(self, t):
        P, a, sd, kw = self.P, self.action, self.seed, self.kw
        if a == "land" and t > kw.get("dur", 2.5):
            a = kw.get("then", "idle")
        P.root.location = self.loc0
        P.root.rotation_euler = (0, 0, self.rz0)
        for j in P.J:
            if j != "root":
                P.rot(j, 0, 0, 0)
        self.blink(t)
        breathe = 0.015 * math.sin(t * 2.4 + sd)
        P.J["body"][0].scale = (1, 1, 1 + breathe)
        if a in ("idle", "perch", "stand"):
            P.show("spread", False)
            P.show("folded", True)
            P.rot("neck1", 0, -0.1 + 0.08 * noise1(t * 0.6, sd), 0.35 * noise1(t * 0.4, sd + 3))
            P.rot("neck2", 0, 0.12 * noise1(t * 0.9, sd + 1), 0.25 * noise1(t * 0.5, sd + 5))
            P.rot("head", 0.15 * noise1(t * 0.7, sd + 2), 0.1 * noise1(t, sd + 4), 0.3 * noise1(t * 0.45, sd + 6))
            P.rot("tail", 0, 0.05 * math.sin(t * 1.1 + sd), 0.08 * noise1(t * 0.8, sd))
        elif a == "feed":
            P.show("spread", False)
            P.show("folded", True)
            cyc = (t * kw.get("rate", 0.55) + sd * 0.31) % 1.0
            dip = smooth01(cyc / 0.35) if cyc < 0.35 else (1.0 if cyc < 0.6 else 1 - smooth01((cyc - 0.6) / 0.4))
            tug = 0.12 * math.sin(t * 9 + sd) * (1 if 0.35 < cyc < 0.6 else 0)
            P.rot("body", 0, 0.3 * dip, 0.05 * noise1(t, sd))
            P.rot("neck1", 0, 0.9 * dip + tug, 0.15 * noise1(t * 0.5, sd))
            P.rot("neck2", 0, 0.6 * dip, 0.1 * noise1(t * 0.8, sd + 2))
            P.rot("head", 0, 0.3 * dip - tug, 0.2 * noise1(t * 1.4, sd + 3))
            P.rot("tail", 0, -0.2 * dip, 0)
        elif a in ("spread", "display"):
            P.show("spread", True)
            P.show("folded", False)
            flap = math.sin(t * 2.2 + sd)
            for s, side in ((1, "L"), (-1, "R")):
                P.rot("wing" + side, s * (-0.45 + 0.25 * flap), 0, s * -0.35)
                P.rot("hand" + side, s * (0.25 + 0.15 * flap), 0, s * -0.25)
            P.rot("neck1", 0, -0.1, 0.3 * noise1(t * 0.5, sd))
            P.rot("head", 0, 0.1, 0.3 * noise1(t * 0.7, sd))
        elif a in ("soar", "circle", "glide", "flap", "land"):
            P.show("spread", True)
            P.show("folded", False)
            if a == "flap":
                ph = t * kw.get("hz", 2.2) * TAU + sd
                up = math.sin(ph)
                for s, side in ((1, "L"), (-1, "R")):
                    P.rot("wing" + side, s * (-0.75 * up - 0.1), 0, 0)
                    P.rot("hand" + side, s * (-0.5 * math.sin(ph - 0.7)), 0, s * 0.1 * up)
            else:
                flex = 0.06 * math.sin(t * 1.3 + sd)
                for s, side in ((1, "L"), (-1, "R")):
                    P.rot("wing" + side, s * (0.1 + flex), 0, 0)
                    P.rot("hand" + side, s * (0.1 + flex * 0.8), 0, s * -0.05)
            for leg in ("legL", "legR"):
                P.rot(leg, 0, 1.2, 0)
            P.rot("body", 0, 0.3, 0)
            P.rot("neck1", 0, 0.75, 0)
            P.rot("neck2", 0, 0.15, 0)
            P.rot("head", 0, -0.55 + 0.1 * noise1(t, sd), 0.25 * noise1(t * 0.6, sd))
            P.rot("tail", 0, -0.3, 0.1 * noise1(t * 0.7, sd))
            if a in ("circle", "soar"):
                R = kw.get("radius", 6.0)
                w = kw.get("speed", 0.35) * (1 if kw.get("cw", True) else -1)
                ang = kw.get("phase", 0.0) + w * t
                c = Vector(kw.get("center", self.loc0))
                P.root.location = (c.x + R * math.cos(ang), c.y + R * math.sin(ang),
                                   c.z + kw.get("climb", 0.0) * t + 0.3 * math.sin(t * 0.8 + sd))
                heading = ang + (math.pi / 2 if w > 0 else -math.pi / 2)
                bank = kw.get("bank", 0.35) * (1 if w > 0 else -1)
                P.root.rotation_euler = (bank, 0, heading)
            elif a in ("glide", "flap"):
                v = Vector(kw.get("vel", (2.0, 0, 0)))
                P.root.location = self.loc0 + v * t + Vector((0, 0, 0.15 * math.sin(t * 1.5 + sd)))
                P.root.rotation_euler = (0.1 * math.sin(t * 0.7 + sd), -0.05, math.atan2(v.y, v.x))
            elif a == "land":
                T = kw.get("dur", 2.5)
                u = smooth01(t / T)
                start = Vector(kw.get("start", (self.loc0.x - 4, self.loc0.y, self.loc0.z + 5)))
                P.root.location = start.lerp(self.loc0, u)
                d = self.loc0 - start
                P.root.rotation_euler = (0, -0.25 * (1 - u), math.atan2(d.y, d.x))
                ph = t * 3.0 * TAU
                k = 1 - u * 0.6
                for s, side in ((1, "L"), (-1, "R")):
                    P.rot("wing" + side, s * (-0.6 * math.sin(ph) * k - 0.2), 0, 0)
                    P.rot("hand" + side, s * (-0.4 * math.sin(ph - 0.7) * k), 0, 0)
                for leg in ("legL", "legR"):
                    P.rot(leg, 0, 1.2 * (1 - u) - 0.3 * u, 0)
        elif a == "hop":
            P.show("spread", True)
            P.show("folded", False)
            per = kw.get("period", 1.6)
            ph = ((t + sd * 0.4) % per) / per
            jump = math.sin(math.pi * min(1, ph / 0.45)) if ph < 0.45 else 0
            step = int((t + sd * 0.4) / per) + smooth01(min(1, ph / 0.45))
            v = Vector(kw.get("step", (0.5, 0, 0)))
            P.root.location = self.loc0 + v * step + Vector((0, 0, 0.35 * jump))
            for s, side in ((1, "L"), (-1, "R")):
                P.rot("wing" + side, s * (-0.5 * jump - 0.3), 0, s * -0.5)
                P.rot("hand" + side, s * 0.3, 0, s * -0.4)
            P.rot("neck1", 0, -0.2 + 0.3 * jump, 0)
        elif a == "fallen":
            P.show("spread", True)
            P.show("folded", False)
            P.root.rotation_euler = (0, 0, self.rz0)
            P.root.location = self.loc0 + Vector((0, 0, -0.33 * self.scale))
            P.rot("body", 0, 0.05, 0)
            P.rot("neck1", 0, 1.15, 0.5)
            P.rot("neck2", 0, 0.4, 0.3)
            P.rot("head", 1.2, 0, 0)
            for s, side in ((1, "L"), (-1, "R")):
                flut = 0.02 * math.sin(t * 5 + s)
                P.rot("wing" + side, s * (0.15 + flut), 0, s * -0.55)
                P.rot("hand" + side, s * 0.1, 0, s * -0.4)
            for leg in ("legL", "legR"):
                P.rot(leg, 0, -0.9, 0)
            for o in P.groups.get("eye", []):
                o.scale.z = 0.002

    # --- dog
    def u_dog(self, t):
        P, a, sd, kw = self.P, self.action, self.seed, self.kw
        for j in P.J:
            if j != "root":
                P.rot(j, 0, 0, 0)
        self.blink(t, 4.3)
        wag = math.sin(t * kw.get("wag", 9.0) + sd)
        P.rot("tail", 0, -0.2, 0.5 * wag)
        P.rot("tail2", 0, 0.2, 0.4 * wag)
        P.rot("earL", 0.1 * noise1(t * 2, sd), 0, 0)
        P.rot("earR", -0.1 * noise1(t * 2, sd + 4), 0, 0)
        P.root.rotation_euler = (0, 0, self.rz0)
        if a in ("walk", "trot", "sniff_walk"):
            spd = {"walk": 1.0, "trot": 1.8, "sniff_walk": 0.6}[a] * kw.get("speed", 1.0)
            ph = t * spd * TAU * 1.0 + sd
            sw = 0.45 if a != "trot" else 0.6
            for nm, off in (("FL", 0), ("BR", 0), ("FR", math.pi), ("BL", math.pi)):
                P.rot("leg" + nm, 0, sw * math.sin(ph + off), 0)
                P.rot("knee" + nm, 0, 0.45 * max(0, math.sin(ph + off + 1.2)) * (1 if nm[0] == "F" else -1), 0)
            P.rot("body", 0.03 * math.sin(ph * 2), 0.03 * math.sin(ph * 2), 0)
            head_down = 0.55 if a == "sniff_walk" else 0.0
            P.rot("head", 0, head_down + 0.06 * math.sin(ph * 2), 0.15 * noise1(t * 0.6, sd))
            path = kw.get("path")
            if path:   # list of points; constant speed along polyline
                dist = t * 0.9 * spd * self.scale
                pts = [Vector(p) for p in path]
                loc, yaw = pts[-1], 0.0
                for p0, p1 in zip(pts[:-1], pts[1:]):
                    sl = (p1 - p0).length
                    if dist <= sl:
                        loc = p0.lerp(p1, dist / sl)
                        yaw = math.atan2((p1 - p0).y, (p1 - p0).x)
                        break
                    dist -= sl
                    yaw = math.atan2((p1 - p0).y, (p1 - p0).x)
                P.root.location = loc
                P.root.rotation_euler = (0, 0, yaw)
            else:
                v = Vector(kw.get("vel", (0, 0, 0)))
                P.root.location = self.loc0 + v * t
                if v.length > 0:
                    P.root.rotation_euler = (0, 0, math.atan2(v.y, v.x))
        elif a == "sniff":
            P.root.location = self.loc0
            dip = 0.5 + 0.5 * math.sin(t * 1.5 + sd)
            P.rot("head", 0, 0.7 * dip + 0.05 * math.sin(t * 14), 0.3 * noise1(t * 0.5, sd))
            P.rot("body", 0, 0.08 * dip, 0)
            P.rot("legFL", 0, -0.15 * dip, 0)
            P.rot("legFR", 0, -0.15 * dip, 0)
        elif a == "tug":
            P.root.location = self.loc0
            pull = math.sin(t * 3.2 + sd)
            P.rot("head", 0, 0.75 + 0.15 * pull, 0.25 * math.sin(t * 2.1 + sd))
            P.rot("body", 0, 0.12 - 0.06 * pull, 0)
            for nm in ("FL", "FR"):
                P.rot("leg" + nm, 0, -0.25 + 0.1 * pull, 0)
            for nm in ("BL", "BR"):
                P.rot("leg" + nm, 0, 0.2 + 0.08 * pull, 0)
        elif a == "sit":
            P.root.location = self.loc0
            P.rot("body", 0, -0.55, 0)
            for nm in ("BL", "BR"):
                P.rot("leg" + nm, 0, -1.1, 0)
                P.rot("knee" + nm, 0, 1.9, 0)
            for nm in ("FL", "FR"):
                P.rot("leg" + nm, 0, 0.55, 0)
            P.rot("head", 0, -0.45 + 0.05 * noise1(t, sd), 0.5 * noise1(t * 0.4, sd))
            P.rot("tail", 0, 0.9, 0.5 * wag)
        else:  # idle / stand / bark
            P.root.location = self.loc0
            bark = (a == "bark") and ((t * 1.3 + sd) % 1.0 < 0.18)
            P.rot("head", 0, (-0.25 if bark else 0.05 * noise1(t, sd)), 0.4 * noise1(t * 0.35, sd + 1))
            P.rot("body", 0, 0.02 * math.sin(t * 2.2), 0)

    # --- crow
    def u_crow(self, t):
        P, a, sd, kw = self.P, self.action, self.seed, self.kw
        for j in P.J:
            if j != "root":
                P.rot(j, 0, 0, 0)
        per = 1.4
        ph = ((t + sd) % per) / per
        P.root.rotation_euler = (0, 0, self.rz0 + 0.6 * math.sin(int((t + sd) / per) * 2.1))
        if a == "fly":
            v = Vector(kw.get("vel", (3.0, 0, 0)))
            P.root.location = self.loc0 + v * t + Vector((0, 0, 0.2 * math.sin(t * 2 + sd)))
            P.root.rotation_euler = (0, 0, math.atan2(v.y, v.x))
            ph = t * 4.5 * TAU + sd
            for s_, side in ((1, "L"), (-1, "R")):
                P.rot("wing" + side, s_ * (1.3 + 0.9 * math.sin(ph)), 0, 0)
            P.rot("body", 0, -0.2, 0)
            return
        if a == "peck":
            pk = math.sin(math.pi * min(1, ph / 0.25)) if ph < 0.25 else 0
            P.rot("body", 0, 0.6 * pk, 0)
            P.rot("head", 0, 0.4 * pk, 0)
            P.root.location = self.loc0
        else:  # hop
            jump = math.sin(math.pi * min(1, ph / 0.3)) if ph < 0.3 else 0
            P.root.location = self.loc0 + Vector((0, 0, 0.18 * jump))
            P.rot("head", 0, 0, 0.6 * noise1(t * 1.5, sd))
        P.rot("tail", 0, 0.2 * math.sin(t * 4 + sd), 0)

    # --- cow
    def u_cow(self, t):
        P, sd = self.P, self.seed
        for j in P.J:
            if j != "root":
                P.rot(j, 0, 0, 0)
        self.blink(t, 5.1)
        P.rot("head", 0, 0.05 * math.sin(t * 5.5) + 0.1 * noise1(t * 0.3, sd), 0.25 * noise1(t * 0.25, sd))
        P.rot("tail", 0.5 * math.sin(t * 1.7 + sd), 0, 0.3 * math.sin(t * 1.1))
        P.rot("earL", 0.3 * max(0, math.sin(t * 0.9)) ** 8, 0, 0)
        P.rot("earR", -0.3 * max(0, math.sin(t * 0.7 + 1)) ** 8, 0, 0)

    # --- people
    def u_pip(self, t):
        self.u_person(t)

    def u_villager(self, t):
        self.u_person(t)

    def u_person(self, t):
        P, a, sd, kw = self.P, self.action, self.seed, self.kw
        for j in P.J:
            if j != "root":
                P.rot(j, 0, 0, 0)
        self.blink(t, 3.3)
        P.root.location = self.loc0
        P.root.rotation_euler = (0, 0, self.rz0)
        breathe = 0.02 * math.sin(t * 2.0 + sd)
        P.rot("spine", breathe, 0, 0.04 * noise1(t * 0.5, sd))
        P.rot("head", 0.06 * noise1(t * 0.7, sd), 0.05 * noise1(t * 0.5, sd + 1), 0.15 * noise1(t * 0.4, sd + 2))
        P.rot("shL", 0, -0.12, 0)
        P.rot("shR", 0, 0.12, 0)
        talking = kw.get("talk", False) or a == "talk"
        P.show("talk", talking and (math.sin(t * 13 + 2 * math.sin(t * 3.1)) > 0.1))
        P.show("smile", not (talking and (math.sin(t * 13 + 2 * math.sin(t * 3.1)) > 0.1)))
        P.show("bino", a == "binoculars")
        if a == "walk":
            ph = t * 1.7 * TAU + sd
            for s, side in ((1, "L"), (-1, "R")):
                P.rot("hip" + side, 0.5 * math.sin(ph + (0 if s > 0 else math.pi)), 0, 0)
                P.rot("knee" + side, 0.7 * max(0, math.sin(ph + (0 if s > 0 else math.pi) + 1.4)), 0, 0)
                P.rot("sh" + side, -0.45 * math.sin(ph + (math.pi if s > 0 else 0)), -s * 0.12, 0)
                P.rot("el" + side, -0.25, 0, 0)
            P.root.location = self.loc0 + Vector(kw.get("vel", (0, -0.8, 0))) * t + Vector((0, 0, 0.04 * abs(math.sin(ph))))
            v = Vector(kw.get("vel", (0, -0.8, 0)))
            P.root.rotation_euler = (0, 0, math.atan2(v.y, v.x) + math.pi / 2)
        elif a == "wave":
            P.rot("shR", 0, 2.5, 0)
            P.rot("elR", 0, 0, 0.6 * math.sin(t * 7))
            P.rot("head", 0, 0, 0.2)
        elif a == "point":
            u = smooth01(t / 0.6)
            P.rot("shR", -1.35 * u, 0.3 * u, 0)
            P.rot("elR", -0.2 * u, 0, 0)
            P.rot("head", 0, 0, -0.35 * u)
        elif a == "binoculars":
            u = smooth01(t / 0.8)
            for s, side in ((1, "L"), (-1, "R")):
                P.rot("sh" + side, -1.55 * u, s * 0.6 * u, 0)
                P.rot("el" + side, -1.0 * u, 0, s * 0.5 * u)
            P.rot("head", -0.25 * u + 0.05 * noise1(t, sd), 0, 0.3 * noise1(t * 0.3, sd))
        elif a == "look_up":
            u = smooth01(t / 1.0)
            P.rot("head", -0.5 * u, 0, 0.25 * noise1(t * 0.3, sd))
            P.rot("shR", -0.4 * u, -0.6 * u, 0)
            P.rot("elR", -1.6 * u, 0, 0)
        elif a == "talk":
            g = math.sin(t * 1.6 + sd)
            P.rot("shR", -0.6 - 0.3 * g, -0.3, 0)
            P.rot("elR", -0.9 + 0.3 * math.sin(t * 2.3), 0, 0)
            P.rot("shL", -0.3 + 0.2 * math.sin(t * 1.9 + 1), 0.3, 0)
            P.rot("elL", -0.6, 0, 0)
            P.rot("head", 0.08 * math.sin(t * 3.0), 0, 0.15 * noise1(t * 0.6, sd))
        elif a == "shrug":
            u = 0.5 + 0.5 * math.sin(t * 2.0)
            for s, side in ((1, "L"), (-1, "R")):
                P.rot("sh" + side, -0.3 * u, -s * 0.9 * u, 0)
                P.rot("el" + side, -1.4 * u, 0, 0)
        elif a == "worried":
            for s, side in ((1, "L"), (-1, "R")):
                P.rot("sh" + side, -0.9, s * 0.2, s * -0.4)
                P.rot("el" + side, -1.7, 0, 0)
            P.rot("head", 0.1, 0, 0.3 * noise1(t * 0.8, sd))
            for side in ("L", "R"):
                for o in P.groups.get("brow" + side, []):
                    o.rotation_euler = (0.35, 0, (0.35 if side == "L" else -0.35))


def build(M, kind, name, seed=0, **kw):
    if kind == "vulture":
        return build_vulture(M, name, seed)
    if kind == "dog":
        return build_dog(M, name, kw.get("coat", ("#C99A5E", "#A87A44")), seed)
    if kind == "crow":
        return build_crow(M, name)
    if kind == "cow":
        return build_cow(M, name)
    if kind == "pip":
        return build_person(M, name, True)
    if kind == "villager":
        return build_person(M, name, False, skin=kw.get("skin", "#B27A50"), shirt=kw.get("shirt", "#C0563A"),
                            pants=kw.get("pants", "#3E4A63"), hair=kw.get("hair", "#151210"))
    raise KeyError(kind)


def reset_caches():
    _FEATHER.clear()
