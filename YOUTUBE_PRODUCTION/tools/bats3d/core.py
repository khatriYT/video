"""Episode 4 (v3) core: scene utilities, implicit-surface modelling, skinning, PBR material library,
cinematic light rigs and Eevee render settings.

Units are metres (Pip is 1.68 m tall). Z is up; characters face -Y in their rest pose.
Every material is procedural, so a re-run rebuilds exactly the same look (no external textures).
"""
import math
import random

from array import array

import bpy
from mathutils import Matrix, Quaternion, Vector
from mathutils.geometry import intersect_point_line

MB_K = 1.0 / 0.574          # metaball nominal radius -> visible radius (threshold 0.6, stiffness 2)


# ------------------------------------------------------------------ basics
def hex_lin(h):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c)


def rgba(h, a=1.0):
    return (*hex_lin(h), a)


def reset(seed=7):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    random.seed(seed)
    _CACHE.clear()


_CACHE = {}


def link(ob, coll=None):
    (coll or bpy.context.scene.collection).objects.link(ob)
    return ob


def smooth(ob, angle=None):
    me = ob.data
    me.polygons.foreach_set("use_smooth", [True] * len(me.polygons))
    return ob


def mesh_ob(name, verts, faces, mat=None, smooth_=True):
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(v) for v in verts], [], [tuple(f) for f in faces])
    me.update()
    ob = link(bpy.data.objects.new(name, me))
    if mat:
        me.materials.append(mat)
    if smooth_:
        smooth(ob)
    return ob


def verts_np(ob):
    """Vertex positions as a list of Vectors (object space)."""
    me = ob.data
    a = array("d", [0.0]) * (len(me.vertices) * 3)
    me.vertices.foreach_get("co", a)
    return [Vector(a[i:i + 3]) for i in range(0, len(a), 3)]


def set_verts(ob, vs):
    a = array("d", [0.0]) * (len(vs) * 3)
    for i, v in enumerate(vs):
        a[3 * i], a[3 * i + 1], a[3 * i + 2] = v[0], v[1], v[2]
    ob.data.vertices.foreach_set("co", a)
    ob.data.update()


def edges_np(ob):
    me = ob.data
    e = array("i", [0]) * (len(me.edges) * 2)
    me.edges.foreach_get("vertices", e)
    return [(e[i], e[i + 1]) for i in range(0, len(e), 2)]


def laplacian(ob, iters=2, lam=0.5, mask=None):
    """Umbrella-operator smoothing. mask: per-vertex weight 0..1 (list)."""
    v = verts_np(ob)
    n = len(v)
    nb = [[] for _ in range(n)]
    for a, b in edges_np(ob):
        nb[a].append(b)
        nb[b].append(a)
    for _ in range(iters):
        nv = []
        for i in range(n):
            ns = nb[i]
            if not ns:
                nv.append(v[i])
                continue
            avg = Vector((0.0, 0.0, 0.0))
            for j in ns:
                avg += v[j]
            avg /= len(ns)
            w = lam if mask is None else lam * mask[i]
            nv.append(v[i] + (avg - v[i]) * w)
        v = nv
    set_verts(ob, v)
    return ob


def fix_texspace(ob):
    """Metric generated coordinates: Generated = co / 2 + 0.5 (stable under armature deformation)."""
    me = ob.data
    if hasattr(me, "use_auto_texspace"):
        me.use_auto_texspace = False
        me.texspace_location = (0, 0, 0)
        me.texspace_size = (1, 1, 1)
    return ob


def color_attr(ob, name, rgb):
    """Per-vertex colour attribute from a list of (r, g, b) (linear 0..1)."""
    me = ob.data
    if name in me.color_attributes:
        me.color_attributes.remove(me.color_attributes[name])
    ca = me.color_attributes.new(name, "FLOAT_COLOR", "POINT")
    a = array("f", [1.0]) * (len(me.vertices) * 4)
    for i, c in enumerate(rgb):
        a[4 * i], a[4 * i + 1], a[4 * i + 2] = c[0], c[1], c[2]
    ca.data.foreach_set("color", a)
    return ca


def apply_mods(ob):
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    old = ob.data
    ob.modifiers.clear()
    ob.data = me
    bpy.data.meshes.remove(old)
    return ob


def join(obs, name):
    """Join mesh objects (with their materials) into one, without operators."""
    import bmesh
    bm = bmesh.new()
    mats = []
    for ob in obs:
        me = ob.data.copy()
        me.transform(ob.matrix_world)
        remap = []
        for m in me.materials:
            if m not in mats:
                mats.append(m)
            remap.append(mats.index(m))
        if remap:
            idx = array("i", [0]) * len(me.polygons)
            me.polygons.foreach_get("material_index", idx)
            me.polygons.foreach_set("material_index", array("i", [remap[i] for i in idx]))
        bm.from_mesh(me)
        bpy.data.meshes.remove(me)
    out = bpy.data.meshes.new(name)
    bm.to_mesh(out)
    bm.free()
    for m in mats:
        out.materials.append(m)
    for ob in obs:
        bpy.data.objects.remove(ob)
    ob = link(bpy.data.objects.new(name, out))
    return ob


# ------------------------------------------------------------------ implicit modelling (metaballs)
def E(co, r, typ="BALL", size=None, rot=None, neg=False, stiff=2.0):
    """Metaball element spec. r/size are VISIBLE radii (semi-axes) in metres."""
    return dict(co=co, r=r, type=typ, size=size, rot=rot, neg=neg, stiff=stiff)


def cap(a, b, r, neg=False, stiff=2.0):
    """Capsule between points a and b with visible radius r."""
    a, b = Vector(a), Vector(b)
    d = b - a
    L = d.length
    q = Vector((1, 0, 0)).rotation_difference(d.normalized()) if L > 1e-6 else Quaternion()
    return dict(co=tuple((a + b) / 2), r=r, type="CAPSULE", size=(L / 2 + r, r, r), rot=q, neg=neg, stiff=stiff)


def ell(co, sx, sy, sz, rot=None, neg=False, stiff=2.0):
    return dict(co=co, r=min(sx, sy, sz), type="ELLIPSOID", size=(sx, sy, sz), rot=rot, neg=neg, stiff=stiff)


def implicit(name, elems, res=0.006, mat=None, smooth_iters=2):
    mb = bpy.data.metaballs.new(name + "_mb")
    mb.resolution = res
    mb.render_resolution = res
    mb.threshold = 0.6
    for e in elems:
        el = mb.elements.new()
        el.type = e["type"]
        el.co = e["co"]
        el.stiffness = e.get("stiff", 2.0)
        el.use_negative = bool(e.get("neg"))
        if el.type == "BALL":
            el.radius = e["r"] * MB_K
        else:
            sx, sy, sz = e["size"]
            r = min(sx, sy, sz) if el.type != "CAPSULE" else e["r"]
            el.radius = r * MB_K
            if el.type == "ELLIPSOID":
                el.size_x, el.size_y, el.size_z = sx / r, sy / r, sz / r
            else:
                el.size_x = max(sx - r, 0.0)
        if e.get("rot") is not None:
            el.rotation = e["rot"]
    tmp = link(bpy.data.objects.new(name + "_tmp", mb))
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(tmp.evaluated_get(dg))
    bpy.data.objects.remove(tmp)
    bpy.data.metaballs.remove(mb)
    me.name = name
    ob = link(bpy.data.objects.new(name, me))
    if mat:
        me.materials.append(mat)
    smooth(ob)
    if smooth_iters:
        laplacian(ob, smooth_iters, 0.5)
    return ob


def lathe(name, profile, seg=48, mat=None, close_top=True, close_bottom=True):
    """Surface of revolution around Z. profile: list of (r, z)."""
    verts, faces = [], []
    n = len(profile)
    for i in range(seg):
        a = 2 * math.pi * i / seg
        ca, sa = math.cos(a), math.sin(a)
        for r, z in profile:
            verts.append((r * ca, r * sa, z))
    for i in range(seg):
        j = (i + 1) % seg
        for k in range(n - 1):
            faces.append((i * n + k, j * n + k, j * n + k + 1, i * n + k + 1))
    if close_bottom and profile[0][0] > 1e-6:
        verts.append((0, 0, profile[0][1]))
        c = len(verts) - 1
        for i in range(seg):
            j = (i + 1) % seg
            faces.append((j * n, i * n, c))
    if close_top and profile[-1][0] > 1e-6:
        verts.append((0, 0, profile[-1][1]))
        c = len(verts) - 1
        for i in range(seg):
            j = (i + 1) % seg
            faces.append((i * n + n - 1, j * n + n - 1, c))
    return mesh_ob(name, verts, faces, mat)


def tube(name, pts, radii, seg=10, mat=None, caps=True):
    """Swept tube along a polyline with per-point radius (parallel-transport frames)."""
    pts = [Vector(p) for p in pts]
    if not hasattr(radii, "__len__"):
        radii = [radii] * len(pts)
    verts, faces = [], []
    t_prev = (pts[1] - pts[0]).normalized()
    nrm = t_prev.orthogonal().normalized()
    for i, p in enumerate(pts):
        if i == 0:
            t = (pts[1] - pts[0]).normalized()
        elif i == len(pts) - 1:
            t = (pts[-1] - pts[-2]).normalized()
        else:
            t = (pts[i + 1] - pts[i - 1]).normalized()
        q = t_prev.rotation_difference(t)
        nrm = (q @ nrm).normalized()
        t_prev = t
        b = t.cross(nrm).normalized()
        for k in range(seg):
            a = 2 * math.pi * k / seg
            verts.append(tuple(p + (nrm * math.cos(a) + b * math.sin(a)) * radii[i]))
    n = len(pts)
    for i in range(n - 1):
        for k in range(seg):
            k2 = (k + 1) % seg
            faces.append((i * seg + k, i * seg + k2, (i + 1) * seg + k2, (i + 1) * seg + k))
    if caps:
        verts.append(tuple(pts[0]))
        verts.append(tuple(pts[-1]))
        c0, c1 = len(verts) - 2, len(verts) - 1
        for k in range(seg):
            k2 = (k + 1) % seg
            faces.append((k2, k, c0))
            faces.append(((n - 1) * seg + k, (n - 1) * seg + k2, c1))
    return mesh_ob(name, verts, faces, mat)


# ------------------------------------------------------------------ skinning
class Rig:
    """Armature built from a bone spec, plus distance-based smooth skin weights (numpy)."""

    def __init__(self, name, bones):
        """bones: list of (name, head, tail, parent or None, deform=True)."""
        arm = bpy.data.armatures.new(name + "_arm")
        arm.display_type = "STICK"
        self.ob = link(bpy.data.objects.new(name, arm))
        bpy.context.view_layer.objects.active = self.ob
        bpy.ops.object.mode_set(mode="EDIT")
        self.spec = {}
        for b in bones:
            nm, h, t, par = b[:4]
            deform = b[4] if len(b) > 4 else True
            eb = arm.edit_bones.new(nm)
            eb.head, eb.tail = h, t
            eb.use_deform = deform
            if par:
                eb.parent = arm.edit_bones[par]
            self.spec[nm] = (tuple(h), tuple(t), deform)
        bpy.ops.object.mode_set(mode="OBJECT")
        for pb in self.ob.pose.bones:
            pb.rotation_mode = "XYZ"

    def skin(self, ob, allowed=None, power=5.0, eps=0.004, topk=3, rigid=None, side=None, radius=None):
        """Weight mesh `ob` to the rig with inverse-distance weights to bone segments.
        allowed: bone names (default all deform bones). rigid: one bone at 100%.
        radius: {bone: r} subtracts a bone's flesh radius so surfaces belong to their own bone."""
        mw = ob.matrix_world
        vs = [mw @ v for v in verts_np(ob)]
        names = [n for n, s in self.spec.items() if s[2]] if allowed is None else list(allowed)
        if side:
            bad = ".R" if side == "L" else ".L"
            names = [n for n in names if not n.endswith(bad)]
        if rigid:
            names = [rigid]
        groups = {n: (ob.vertex_groups.get(n) or ob.vertex_groups.new(name=n)) for n in names}
        segs = [(n, Vector(self.spec[n][0]), Vector(self.spec[n][1]), (radius or {}).get(n, 0.0)) for n in names]
        buckets = {n: {} for n in names}
        for i, v in enumerate(vs):
            ws = []
            for n, h, t, r in segs:
                p, u = intersect_point_line(v, h, t)
                if u < 0.0:
                    p = h
                elif u > 1.0:
                    p = t
                d = max((v - p).length - r, 0.0)
                ws.append((1.0 / (d + eps) ** power, n))
            if topk and len(ws) > topk:
                ws.sort(reverse=True)
                ws = ws[:topk]
            tot = sum(w for w, _ in ws)
            for w, n in ws:
                w /= tot
                if w > 1e-4:
                    buckets[n].setdefault(round(w, 4), []).append(i)
        for n, b in buckets.items():
            for w, idx in b.items():
                groups[n].add(idx, w, "REPLACE")
        mod = ob.modifiers.new("Armature", "ARMATURE")
        mod.object = self.ob
        mod.use_deform_preserve_volume = True
        ob.parent = self.ob
        return ob

    def attach(self, ob, bone):
        """Rigidly parent an object to a bone, keeping its world transform."""
        mw = Matrix.LocRotScale(ob.location, ob.rotation_euler.to_quaternion() if ob.rotation_mode != "QUATERNION"
                                else ob.rotation_quaternion, ob.scale)
        if ob.parent is not None:
            bpy.context.view_layer.update()
            mw = ob.matrix_world.copy()
        ob.parent = self.ob
        ob.parent_type = "BONE"
        ob.parent_bone = bone
        bpy.context.view_layer.update()
        pb = self.ob.pose.bones[bone]
        # bone parenting attaches at the bone tail; compensate with the inverse of the bone matrix
        ob.matrix_parent_inverse = (self.ob.matrix_world @ pb.matrix @
                                    Matrix.Translation((0, pb.bone.length, 0))).inverted()
        ob.matrix_world = mw
        return ob


# ------------------------------------------------------------------ node helper
class NB:
    """Tiny shader-node builder: n('ShaderNodeTexNoise', Scale=4) ; l(a.outputs[0], b.inputs['Color'])."""

    def __init__(self, mat):
        self.mat = mat
        self.nt = mat.node_tree
        self.nt.nodes.clear()
        self.out = self.nt.nodes.new("ShaderNodeOutputMaterial")
        self.x = 0

    def n(self, typ, **kw):
        node = self.nt.nodes.new(typ)
        for k, v in kw.items():
            if k.startswith("_"):
                setattr(node, k[1:], v)
            elif k in node.inputs:
                node.inputs[k].default_value = v
            else:
                setattr(node, k, v)
        return node

    def l(self, a, b):
        self.nt.links.new(a, b)

    # common building blocks ------------------------------------------------------
    def coord(self, kind="Generated"):
        tc = self.n("ShaderNodeTexCoord")
        return tc.outputs[kind]

    def noise(self, vec, scale, detail=4.0, rough=0.55, dist=0.0, w=None):
        nz = self.n("ShaderNodeTexNoise", Scale=scale, Detail=detail, Roughness=rough, Distortion=dist)
        if vec is not None:
            self.l(vec, nz.inputs["Vector"])
        return nz

    def ramp(self, fac, stops, interp="LINEAR"):
        """stops: list of (pos, hex or (r,g,b,a) or float)."""
        cr = self.n("ShaderNodeValToRGB")
        cr.color_ramp.interpolation = interp
        el = cr.color_ramp.elements
        while len(el) > 2:
            el.remove(el[-1])
        for i, (pos, col) in enumerate(stops):
            e = el[i] if i < 2 else el.new(pos)
            e.position = pos
            if isinstance(col, str):
                e.color = rgba(col)
            elif isinstance(col, (int, float)):
                e.color = (col, col, col, 1)
            else:
                e.color = col
        self.l(fac, cr.inputs["Fac"])
        return cr

    def mix(self, a, b, fac, blend="MIX", fac_val=None):
        m = self.n("ShaderNodeMix", data_type="RGBA", blend_type=blend)
        if fac is not None:
            self.l(fac, m.inputs[0])
        else:
            m.inputs[0].default_value = fac_val
        for sock, val in ((m.inputs[6], a), (m.inputs[7], b)):
            if isinstance(val, str):
                sock.default_value = rgba(val)
            elif isinstance(val, tuple):
                sock.default_value = val
            else:
                self.l(val, sock)
        return m.outputs[2]

    def math(self, op, a, b=None, clamp=False):
        m = self.n("ShaderNodeMath", operation=op, use_clamp=clamp)
        for i, val in enumerate((a, b)):
            if val is None:
                continue
            if isinstance(val, (int, float)):
                m.inputs[i].default_value = val
            else:
                self.l(val, m.inputs[i])
        return m.outputs[0]

    def bump(self, height, strength=0.3, dist=0.01, normal=None):
        b = self.n("ShaderNodeBump", Strength=strength, Distance=dist)
        self.l(height, b.inputs["Height"])
        if normal is not None:
            self.l(normal, b.inputs["Normal"])
        return b.outputs["Normal"]

    def bsdf(self, **kw):
        p = self.n("ShaderNodeBsdfPrincipled")
        for k, v in kw.items():
            sock = p.inputs[k]
            if isinstance(v, str):
                sock.default_value = rgba(v)
            elif hasattr(v, "is_linked") or hasattr(v, "links"):
                self.l(v, sock)
            else:
                sock.default_value = v
        self.l(p.outputs[0], self.out.inputs["Surface"])
        return p


def new_mat(name):
    if name in bpy.data.materials:
        return None, bpy.data.materials[name]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    return NB(m), m


def attr(nb, name, kind="GEOMETRY"):
    a = nb.n("ShaderNodeAttribute", attribute_name=name, attribute_type=kind)
    return a


def add_mask_aov(m, value_from_object=True):
    """AOV 'mask' = object custom property 'mask' (1 for characters, 0 for environment)."""
    nt = m.node_tree
    if any(n.bl_idname == "ShaderNodeOutputAOV" for n in nt.nodes):
        return
    a = nt.nodes.new("ShaderNodeAttribute")
    a.attribute_type = "OBJECT"
    a.attribute_name = "mask"
    o = nt.nodes.new("ShaderNodeOutputAOV")
    o.name = "mask"
    nt.links.new(a.outputs["Fac"], o.inputs["Value"])


# ------------------------------------------------------------------ PBR material library
def m_skin(name, base="#D7A07F", blush="#C9624E", freckles=0.35, rough=0.48, sss=0.32, tint_attr="tint"):
    """Skin: subsurface scattering (red-weighted radius), mottled albedo, vertex-colour blush/tint
    (attribute `tint`: R = blush, G = darker creases, B = lip), fine pore bump, freckles."""
    nb, m = new_mat(name)
    if nb is None:
        return m
    gen = nb.coord("Generated")
    t = attr(nb, tint_attr)
    sep = nb.n("ShaderNodeSeparateColor")
    nb.l(t.outputs["Color"], sep.inputs[0])
    mott = nb.noise(gen, 38.0, 5.0, 0.6)
    c0 = nb.ramp(mott.outputs["Fac"], [(0.35, _shift(base, -0.035)), (0.7, _shift(base, 0.03))])
    c1 = nb.mix(c0.outputs[0], blush, sep.outputs[0])                       # blush on cheeks/nose/ears
    c2 = nb.mix(c1, _shift(base, -0.16), sep.outputs[1], blend="MIX")        # creases / eyelid shadow
    c3 = nb.mix(c2, "#B05A52", sep.outputs[2])                               # lips
    fr = nb.noise(gen, 220.0, 2.0, 0.5)
    frm = nb.ramp(fr.outputs["Fac"], [(0.62, 0.0), (0.66, freckles)])
    frm2 = nb.math("MULTIPLY", frm.outputs[0], sep.outputs[0])
    col = nb.mix(c3, _shift(base, -0.22), frm2)
    pores = nb.noise(gen, 900.0, 2.0, 0.6)
    wr = nb.noise(gen, 120.0, 3.0, 0.5)
    h = nb.math("ADD", nb.math("MULTIPLY", pores.outputs["Fac"], 0.6), nb.math("MULTIPLY", wr.outputs["Fac"], 0.4))
    nrm = nb.bump(h, 0.12, 0.002)
    rv = nb.ramp(nb.noise(gen, 60.0, 2.0).outputs["Fac"], [(0.3, rough - 0.07), (0.7, rough + 0.07)])
    rlip = nb.math("SUBTRACT", rv.outputs[0], nb.math("MULTIPLY", sep.outputs[2], 0.18))
    nb.bsdf(**{"Base Color": col, "Roughness": rlip, "Subsurface Weight": sss,
               "Subsurface Radius": (1.0, 0.36, 0.2), "Subsurface Scale": 0.012, "Normal": nrm,
               "Specular IOR Level": 0.45, "Coat Weight": 0.06, "Coat Roughness": 0.35})
    m.use_sss_translucency = True
    return m


def _shift(h, d):
    """Lighten (+) / darken (-) a hex colour in sRGB space."""
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    c = [min(1, max(0, x + d)) for x in c]
    return "#%02X%02X%02X" % tuple(int(x * 255) for x in c)


def m_fabric(name, base, weave=420.0, rough=0.82, sheen=0.35, var=0.05, dark=None, pattern=None, seams=0.0,
             fuzz=0.3, bump=0.18, coord="Generated"):
    """Woven fabric: twill weave (two wave textures), fibre fuzz, wrinkle bump, colour variation,
    optional pattern: ('plaid', hex2, hex3, scale) or ('stripe', hex2, scale)."""
    nb, m = new_mat(name)
    if nb is None:
        return m
    gen = nb.coord(coord)
    w1 = nb.n("ShaderNodeTexWave", wave_type="BANDS", bands_direction="X", Scale=weave, Distortion=0.0,
              Detail=0.0)
    w2 = nb.n("ShaderNodeTexWave", wave_type="BANDS", bands_direction="Y", Scale=weave, Distortion=0.0,
              Detail=0.0)
    nb.l(gen, w1.inputs["Vector"])
    nb.l(gen, w2.inputs["Vector"])
    wv = nb.math("MULTIPLY", w1.outputs["Fac"], w2.outputs["Fac"])
    fz = nb.noise(gen, weave * 1.7, 2.0, 0.7)
    wrinkle = nb.noise(gen, 9.0, 4.0, 0.55, dist=0.4)
    big = nb.noise(gen, 3.0, 2.0, 0.5)
    col = nb.ramp(big.outputs["Fac"], [(0.3, _shift(base, -var)), (0.7, _shift(base, var))]).outputs[0]
    if pattern and pattern[0] == "plaid":
        _, c2, c3, sc = pattern
        px = nb.n("ShaderNodeTexWave", wave_type="BANDS", bands_direction="X", Scale=sc, wave_profile="SAW")
        py = nb.n("ShaderNodeTexWave", wave_type="BANDS", bands_direction="Z", Scale=sc, wave_profile="SAW")
        nb.l(gen, px.inputs["Vector"])
        nb.l(gen, py.inputs["Vector"])
        bx = nb.ramp(px.outputs["Fac"], [(0.55, 0.0), (0.58, 1.0)], "CONSTANT")
        by = nb.ramp(py.outputs["Fac"], [(0.55, 0.0), (0.58, 1.0)], "CONSTANT")
        thin_x = nb.ramp(px.outputs["Fac"], [(0.2, 0.0), (0.24, 1.0), (0.27, 0.0)], "CONSTANT")
        col = nb.mix(col, c2, bx.outputs[0])
        col = nb.mix(col, c2, by.outputs[0])
        both = nb.math("MULTIPLY", bx.outputs[0], by.outputs[0])
        col = nb.mix(col, _shift(c2, -0.12), both)
        col = nb.mix(col, c3, thin_x.outputs[0])
    elif pattern and pattern[0] == "dots":
        _, c2, sc = pattern
        vo = nb.n("ShaderNodeTexVoronoi", Scale=sc, Randomness=0.25)
        nb.l(gen, vo.inputs["Vector"])
        dm = nb.ramp(vo.outputs["Distance"], [(0.16, 1.0), (0.2, 0.0)])
        col = nb.mix(col, c2, dm.outputs[0])
    elif pattern and pattern[0] == "stripe":
        _, c2, sc = pattern
        px = nb.n("ShaderNodeTexWave", wave_type="BANDS", bands_direction="Z", Scale=sc, wave_profile="SAW")
        nb.l(gen, px.inputs["Vector"])
        bx = nb.ramp(px.outputs["Fac"], [(0.5, 0.0), (0.53, 1.0)], "CONSTANT")
        col = nb.mix(col, c2, bx.outputs[0])
    shade = nb.ramp(wv, [(0.0, 0.86), (1.0, 1.0)])
    col = nb.mix(col, shade.outputs[0], None, blend="MULTIPLY", fac_val=1.0)
    if dark is not None:  # ambient-occlusion-ish darkening in folds from vertex attribute
        a = attr(nb, dark)
        col = nb.mix(col, _shift(base, -0.18), a.outputs["Fac"])
    h = nb.math("ADD", nb.math("MULTIPLY", wv, 0.5), nb.math("MULTIPLY", fz.outputs["Fac"], fuzz))
    n1 = nb.bump(h, bump, 0.0015)
    n2 = nb.bump(wrinkle.outputs["Fac"], 0.25, 0.02, n1)
    nb.bsdf(**{"Base Color": col, "Roughness": rough, "Sheen Weight": sheen, "Sheen Roughness": 0.4,
               "Normal": n2, "Specular IOR Level": 0.3})
    return m


def m_leather(name, base, rough=0.42, scale=140.0, wear=0.25):
    nb, m = new_mat(name)
    if nb is None:
        return m
    gen = nb.coord("Generated")
    vor = nb.n("ShaderNodeTexVoronoi", Scale=scale, feature="DISTANCE_TO_EDGE")
    nb.l(gen, vor.inputs["Vector"])
    big = nb.noise(gen, 6.0, 4.0, 0.6)
    col = nb.ramp(big.outputs["Fac"], [(0.35, _shift(base, -0.06)), (0.6, base), (0.8, _shift(base, wear * 0.5))])
    h = nb.ramp(vor.outputs["Distance"], [(0.0, 0.0), (0.08, 1.0)])
    nrm = nb.bump(h.outputs[0], 0.25, 0.001)
    rr = nb.ramp(big.outputs["Fac"], [(0.3, rough - 0.12), (0.8, rough + 0.12)])
    nb.bsdf(**{"Base Color": col.outputs[0], "Roughness": rr.outputs[0], "Normal": nrm, "Coat Weight": 0.15,
               "Coat Roughness": 0.3, "Specular IOR Level": 0.5})
    return m


def m_rubber(name, base="#2A2522", rough=0.75):
    nb, m = new_mat(name)
    if nb is None:
        return m
    gen = nb.coord("Generated")
    nz = nb.noise(gen, 300.0, 2.0)
    nb.bsdf(**{"Base Color": base, "Roughness": rough, "Normal": nb.bump(nz.outputs["Fac"], 0.1, 0.001)})
    return m


def m_metal(name, base="#B8B2A8", rough=0.3, aniso=0.0):
    nb, m = new_mat(name)
    if nb is None:
        return m
    gen = nb.coord("Generated")
    nz = nb.noise(gen, 80.0, 3.0)
    rr = nb.ramp(nz.outputs["Fac"], [(0.3, rough - 0.08), (0.7, rough + 0.1)])
    nb.bsdf(**{"Base Color": base, "Metallic": 1.0, "Roughness": rr.outputs[0]})
    return m


def m_paint(name, base, rough=0.45, metallic=0.0, chip=0.0, grime=0.15):
    """Painted surface (tractor, barn, bat house) with grime gathering and optional chipping."""
    nb, m = new_mat(name)
    if nb is None:
        return m
    gen = nb.coord("Generated")
    g = nb.noise(gen, 7.0, 6.0, 0.6)
    gr = nb.ramp(g.outputs["Fac"], [(0.45, 0.0), (0.75, grime)])
    col = nb.mix(base, _shift(base, -0.25), gr.outputs[0])
    if chip:
        c = nb.noise(gen, 25.0, 8.0, 0.7)
        cm = nb.ramp(c.outputs["Fac"], [(0.72 - chip * 0.2, 0.0), (0.74 - chip * 0.2, 1.0)], "CONSTANT")
        col = nb.mix(col, "#6B6259", cm.outputs[0])
    nz = nb.noise(gen, 200.0, 2.0)
    nb.bsdf(**{"Base Color": col, "Roughness": rough, "Metallic": metallic, "Coat Weight": 0.2,
               "Normal": nb.bump(nz.outputs["Fac"], 0.05, 0.001)})
    return m


def m_glass(name, tint="#DDEEF2", alpha=0.18, rough=0.02):
    nb, m = new_mat(name)
    if nb is None:
        return m
    nb.bsdf(**{"Base Color": tint, "Roughness": rough, "Alpha": alpha, "Specular IOR Level": 0.8,
               "Coat Weight": 1.0, "Coat Roughness": 0.02})
    m.blend_method = "BLEND"
    m.shadow_method = "NONE"
    m.show_transparent_back = False
    m.use_backface_culling = False
    return m


def m_eye(name, iris="#4F7A3A", iris2="#C8A25A", limbal="#1E2A1C", pupil_r=0.30, iris_r=0.56):
    """Eyeball: shading in object space; the iris faces local -Y. Glossy coat gives catch-lights."""
    nb, m = new_mat(name)
    if nb is None:
        return m
    oc = nb.coord("Object")
    sep = nb.n("ShaderNodeSeparateXYZ")
    nb.l(oc, sep.inputs[0])
    # distance from the -Y axis in the XZ plane, normalised by eyeball radius (object scale = radius 1)
    xx = nb.math("MULTIPLY", sep.outputs[0], sep.outputs[0])
    zz = nb.math("MULTIPLY", sep.outputs[2], sep.outputs[2])
    rr = nb.math("SQRT", nb.math("ADD", xx, zz))
    front = nb.math("LESS_THAN", sep.outputs[1], 0.0)
    ang = nb.math("ARCTAN2", sep.outputs[2], sep.outputs[0])
    fib = nb.n("ShaderNodeTexNoise", Scale=1.0, Detail=6.0, Roughness=0.7)
    cmb = nb.n("ShaderNodeCombineXYZ")
    nb.l(nb.math("MULTIPLY", ang, 6.0), cmb.inputs[0])
    nb.l(nb.math("MULTIPLY", rr, 14.0), cmb.inputs[1])
    nb.l(cmb.outputs[0], fib.inputs["Vector"])
    radial = nb.math("DIVIDE", rr, iris_r)
    icol = nb.ramp(radial, [(0.0, iris2), (0.55, iris), (0.88, _shift(iris, -0.12)), (1.0, limbal)])
    icol2 = nb.mix(icol.outputs[0], _shift(iris2, 0.1), nb.ramp(fib.outputs["Fac"], [(0.55, 0.0), (0.8, 0.6)]).outputs[0])
    pup = nb.ramp(rr, [(pupil_r * iris_r - 0.01, 1.0), (pupil_r * iris_r + 0.01, 0.0)])
    col = nb.mix(icol2, "#060504", pup.outputs[0])
    sclera_v = nb.ramp(rr, [(0.6, "#F4EEE6"), (0.95, "#E8C9BE")])
    isir = nb.ramp(rr, [(iris_r - 0.015, 1.0), (iris_r + 0.015, 0.0)])
    iris_mask = nb.math("MULTIPLY", isir.outputs[0], front)
    final = nb.mix(sclera_v.outputs[0], col, iris_mask)
    nb.bsdf(**{"Base Color": final, "Roughness": 0.25, "Coat Weight": 1.0, "Coat Roughness": 0.02,
               "Coat IOR": 1.38, "Subsurface Weight": 0.15, "Subsurface Radius": (1.0, 0.4, 0.3),
               "Subsurface Scale": 0.004, "Specular IOR Level": 0.6})
    return m


def m_hair(name, base="#6B3A21", tip="#A0603A", rough=0.38, scale=90.0, along="Z"):
    """Stylised hair clumps: strand striations (stretched noise), root-to-tip lightening."""
    nb, m = new_mat(name)
    if nb is None:
        return m
    gen = nb.coord("Generated")
    mp = nb.n("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (scale, scale, scale * 0.08) if along == "Z" else (scale * 0.08, scale, scale)
    nb.l(gen, mp.inputs["Vector"])
    st = nb.noise(mp.outputs[0], 1.0, 4.0, 0.6)
    col = nb.ramp(st.outputs["Fac"], [(0.3, _shift(base, -0.08)), (0.55, base), (0.75, tip)])
    nrm = nb.bump(st.outputs["Fac"], 0.35, 0.002)
    nb.bsdf(**{"Base Color": col.outputs[0], "Roughness": rough, "Normal": nrm, "Specular IOR Level": 0.65,
               "Coat Weight": 0.25, "Coat Roughness": 0.25, "Sheen Weight": 0.2})
    return m


def m_fur_strands(name, root="#5A3A26", tip="#A87A52", rough=0.5):
    """Material for particle-hair fur (Eevee strands): Hair Info intercept gives root->tip gradient."""
    nb, m = new_mat(name)
    if nb is None:
        return m
    hi = nb.n("ShaderNodeHairInfo")
    rnd = nb.math("MULTIPLY", hi.outputs["Random"], 0.25)
    f = nb.math("ADD", hi.outputs["Intercept"], rnd)
    col = nb.ramp(f, [(0.0, _shift(root, -0.06)), (0.55, root), (1.0, tip)])
    nb.bsdf(**{"Base Color": col.outputs[0], "Roughness": rough, "Specular IOR Level": 0.4, "Sheen Weight": 0.5})
    return m


def m_membrane(name, base="#3B2A24", vein="#5A2E2A", trans=0.45, rough=0.5):
    """Bat wing membrane: thin skin with vein network, translucency (back-lit glow) and slight sheen."""
    nb, m = new_mat(name)
    if nb is None:
        return m
    gen = nb.coord("Generated")
    vor = nb.n("ShaderNodeTexVoronoi", Scale=9.0, feature="DISTANCE_TO_EDGE", Randomness=0.9)
    mp = nb.n("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (1.0, 3.0, 1.0)
    nb.l(gen, mp.inputs["Vector"])
    nb.l(mp.outputs[0], vor.inputs["Vector"])
    vm = nb.ramp(vor.outputs["Distance"], [(0.0, 1.0), (0.035, 0.0)])
    wr = nb.noise(gen, 70.0, 5.0, 0.6)
    col = nb.mix(nb.ramp(wr.outputs["Fac"], [(0.3, _shift(base, -0.04)), (0.7, _shift(base, 0.04))]).outputs[0],
                 vein, vm.outputs[0])
    h = nb.math("ADD", vm.outputs[0], nb.math("MULTIPLY", wr.outputs["Fac"], 0.6))
    nrm = nb.bump(h, 0.35, 0.0015)
    p = nb.n("ShaderNodeBsdfPrincipled")
    nb.l(col, p.inputs["Base Color"])
    p.inputs["Roughness"].default_value = rough
    p.inputs["Sheen Weight"].default_value = 0.3
    p.inputs["Specular IOR Level"].default_value = 0.45
    nb.l(nrm, p.inputs["Normal"])
    tr = nb.n("ShaderNodeBsdfTranslucent")
    tc = nb.mix(col, "#7A2E22", None, fac_val=0.35)
    nb.l(tc, tr.inputs["Color"])
    nb.l(nrm, tr.inputs["Normal"])
    mx = nb.n("ShaderNodeMixShader")
    mx.inputs[0].default_value = trans
    nb.l(p.outputs[0], mx.inputs[1])
    nb.l(tr.outputs[0], mx.inputs[2])
    nb.l(mx.outputs[0], nb.out.inputs["Surface"])
    m.use_backface_culling = False
    return m


def m_simple(name, base, rough=0.6, metallic=0.0, emit=None, emit_strength=0.0, sss=0.0, spec=0.5, coat=0.0,
             bump_scale=0.0, bump_strength=0.15):
    nb, m = new_mat(name)
    if nb is None:
        return m
    kw = {"Base Color": base, "Roughness": rough, "Metallic": metallic, "Specular IOR Level": spec,
          "Coat Weight": coat}
    if sss:
        kw.update({"Subsurface Weight": sss, "Subsurface Radius": (1.0, 0.5, 0.3), "Subsurface Scale": 0.01})
    if emit:
        kw.update({"Emission Color": emit, "Emission Strength": emit_strength})
    if bump_scale:
        nz = nb.noise(nb.coord("Generated"), bump_scale, 3.0)
        kw["Normal"] = nb.bump(nz.outputs["Fac"], bump_strength, 0.002)
    nb.bsdf(**kw)
    return m


def m_emit(name, color, strength=5.0):
    nb, m = new_mat(name)
    if nb is None:
        return m
    e = nb.n("ShaderNodeEmission", Strength=strength)
    e.inputs["Color"].default_value = rgba(color)
    nb.l(e.outputs[0], nb.out.inputs["Surface"])
    return m


# ------------------------------------------------------------------ lighting
def _aim(ob, target):
    d = Vector(target) - ob.location
    ob.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()


def sun(name, direction_to_light, color="#FFF1DC", energy=4.0, angle=2.0, shadow=True, contact=True):
    """direction_to_light: vector pointing from the scene toward the light."""
    ld = bpy.data.lights.new(name, "SUN")
    ld.energy = energy
    ld.color = hex_lin(color)
    ld.angle = math.radians(angle)
    ld.use_shadow = shadow
    ld.use_contact_shadow = contact
    ld.contact_shadow_distance = 0.25
    ld.contact_shadow_thickness = 0.05
    ld.shadow_cascade_max_distance = 60.0
    ld.shadow_cascade_count = 4
    ld.shadow_cascade_fade = 0.15
    ob = link(bpy.data.objects.new(name, ld))
    d = Vector(direction_to_light).normalized()
    ob.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
    ob.location = d * 30
    return ob


def area(name, loc, target, color="#FFFFFF", energy=200.0, size=2.0, shadow=False, spread=180.0, shape="DISK"):
    ld = bpy.data.lights.new(name, "AREA")
    ld.energy = energy
    ld.color = hex_lin(color)
    ld.shape = shape
    ld.size = size
    ld.use_shadow = shadow
    try:
        ld.spread = math.radians(spread)
    except AttributeError:
        pass
    ob = link(bpy.data.objects.new(name, ld))
    ob.location = loc
    _aim(ob, target)
    return ob


def spot(name, loc, target, color="#FFE2B0", energy=300.0, angle=40.0, blend=0.4, radius=0.05, shadow=True):
    ld = bpy.data.lights.new(name, "SPOT")
    ld.energy = energy
    ld.color = hex_lin(color)
    ld.spot_size = math.radians(angle)
    ld.spot_blend = blend
    ld.shadow_soft_size = radius
    ld.use_shadow = shadow
    ld.use_contact_shadow = shadow
    ob = link(bpy.data.objects.new(name, ld))
    ob.location = loc
    _aim(ob, target)
    return ob


def point(name, loc, color="#FFD9A0", energy=50.0, radius=0.1, shadow=True):
    ld = bpy.data.lights.new(name, "POINT")
    ld.energy = energy
    ld.color = hex_lin(color)
    ld.shadow_soft_size = radius
    ld.use_shadow = shadow
    ob = link(bpy.data.objects.new(name, ld))
    ob.location = loc
    return ob


def three_point(subject, cam_loc, key_dir, key_col, key_e, fill_col, fill_e, rim_col, rim_e, dist=3.0, size=1.5,
                rim_size=0.8, key_is_sun=False):
    """Cinematic key/fill/rim around a subject. key_dir: direction from subject toward the key light.
    Fill sits on the camera side opposite the key; rim sits behind the subject. Fill/rim cast no shadow
    (only the key is in the shadow pass), so character shadows match the environment's sun."""
    s = Vector(subject)
    c = Vector(cam_loc)
    kd = Vector(key_dir).normalized()
    out = []
    if key_is_sun:
        out.append(sun("KEY", kd, key_col, key_e))
    else:
        out.append(area("KEY", s + kd * dist, s, key_col, key_e, size, shadow=True))
    to_cam = (c - s)
    to_cam.z = 0
    to_cam.normalize()
    side = Vector((-kd.x, -kd.y, 0))
    if side.length < 1e-3:
        side = to_cam.cross(Vector((0, 0, 1)))
    side.normalize()
    fdir = (to_cam + side * 0.9).normalized()
    fdir.z = 0.25
    out.append(area("FILL", s + fdir.normalized() * dist * 1.2, s, fill_col, fill_e, size * 2.0, shadow=False))
    rdir = (-to_cam + Vector((0, 0, 0.9)) - side * 0.4).normalized()
    out.append(area("RIM", s + rdir * dist, s, rim_col, rim_e, rim_size, shadow=False))
    return out


# ------------------------------------------------------------------ world / sky
def world_sky(stops, strength=1.0, stars=0.0, sun_dir=None, sun_col="#FFD7A0", sun_glow=0.0, clouds=None,
              ground="#3A3028", moon=None, ambient=None):
    """Gradient sky by elevation; optional sun glow, procedural clouds, stars and a moon disc.
    stops: list of (elevation 0..1, hex) from horizon (0) to zenith (1). clouds: (hex, coverage, scale)."""
    w = bpy.data.worlds.new("World")
    bpy.context.scene.world = w
    w.use_nodes = True
    nt = w.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputWorld")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Generated"], sep.inputs[0])
    # elevation = z of the normalised view direction
    nrm = nt.nodes.new("ShaderNodeVectorMath")
    nrm.operation = "NORMALIZE"
    nt.links.new(tc.outputs["Generated"], nrm.inputs[0])
    sep2 = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(nrm.outputs[0], sep2.inputs[0])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    el = ramp.color_ramp.elements
    for i, (pos, col) in enumerate(stops):
        e = el[i] if i < 2 else el.new(pos)
        e.position = pos
        e.color = rgba(col)
    # below horizon -> ground colour
    gmix = nt.nodes.new("ShaderNodeMix")
    gmix.data_type = "RGBA"
    lt = nt.nodes.new("ShaderNodeMath")
    lt.operation = "LESS_THAN"
    lt.inputs[1].default_value = -0.02
    nt.links.new(sep2.outputs[2], lt.inputs[0])
    nt.links.new(sep2.outputs[2], ramp.inputs[0])
    nt.links.new(lt.outputs[0], gmix.inputs[0])
    nt.links.new(ramp.outputs[0], gmix.inputs[6])
    gmix.inputs[7].default_value = rgba(ground)
    col = gmix.outputs[2]
    if sun_dir is not None and sun_glow > 0:
        d = Vector(sun_dir).normalized()
        dot = nt.nodes.new("ShaderNodeVectorMath")
        dot.operation = "DOT_PRODUCT"
        dot.inputs[1].default_value = tuple(d)
        nt.links.new(nrm.outputs[0], dot.inputs[0])
        pw = nt.nodes.new("ShaderNodeMath")
        pw.operation = "POWER"
        nt.links.new(dot.outputs["Value"], pw.inputs[0])
        pw.inputs[1].default_value = 24.0
        pw2 = nt.nodes.new("ShaderNodeMath")
        pw2.operation = "POWER"
        nt.links.new(dot.outputs["Value"], pw2.inputs[0])
        pw2.inputs[1].default_value = 900.0
        ad = nt.nodes.new("ShaderNodeMath")
        ad.operation = "ADD"
        nt.links.new(pw.outputs[0], ad.inputs[0])
        mlt = nt.nodes.new("ShaderNodeMath")
        mlt.operation = "MULTIPLY"
        mlt.inputs[1].default_value = 6.0
        nt.links.new(pw2.outputs[0], mlt.inputs[0])
        nt.links.new(mlt.outputs[0], ad.inputs[1])
        gl = nt.nodes.new("ShaderNodeMath")
        gl.operation = "MULTIPLY"
        gl.inputs[1].default_value = sun_glow
        nt.links.new(ad.outputs[0], gl.inputs[0])
        sm = nt.nodes.new("ShaderNodeMix")
        sm.data_type = "RGBA"
        sm.blend_type = "ADD"
        sm.clamp_result = False
        nt.links.new(gl.outputs[0], sm.inputs[0])
        nt.links.new(col, sm.inputs[6])
        sm.inputs[7].default_value = rgba(sun_col)
        col = sm.outputs[2]
    if clouds:
        ccol, cover, cscale = clouds[:3]
        cmap = nt.nodes.new("ShaderNodeMapping")
        cmap.inputs["Scale"].default_value = (1.0, 1.0, 4.0)
        nt.links.new(nrm.outputs[0], cmap.inputs["Vector"])
        cn = nt.nodes.new("ShaderNodeTexNoise")
        cn.inputs["Scale"].default_value = cscale
        cn.inputs["Detail"].default_value = 8.0
        cn.inputs["Roughness"].default_value = 0.62
        cn.inputs["Distortion"].default_value = 0.3
        nt.links.new(cmap.outputs[0], cn.inputs["Vector"])
        cr = nt.nodes.new("ShaderNodeValToRGB")
        cr.color_ramp.elements[0].position = 1.0 - cover
        cr.color_ramp.elements[1].position = min(1.0, 1.0 - cover + 0.18)
        nt.links.new(cn.outputs["Fac"], cr.inputs[0])
        # fade clouds near the horizon and zenith
        band = nt.nodes.new("ShaderNodeValToRGB")
        b = band.color_ramp.elements
        b[0].position, b[0].color = 0.02, (0, 0, 0, 1)
        b[1].position, b[1].color = 0.12, (1, 1, 1, 1)
        e3 = b.new(0.55)
        e3.color = (0.6, 0.6, 0.6, 1)
        nt.links.new(sep2.outputs[2], band.inputs[0])
        cm = nt.nodes.new("ShaderNodeMath")
        cm.operation = "MULTIPLY"
        nt.links.new(cr.outputs[0], cm.inputs[0])
        nt.links.new(band.outputs[0], cm.inputs[1])
        mx = nt.nodes.new("ShaderNodeMix")
        mx.data_type = "RGBA"
        nt.links.new(cm.outputs[0], mx.inputs[0])
        nt.links.new(col, mx.inputs[6])
        if len(clouds) > 3:   # two-tone clouds lit from the sun side
            cl2 = nt.nodes.new("ShaderNodeMix")
            cl2.data_type = "RGBA"
            nt.links.new(cn.outputs["Fac"], cl2.inputs[0])
            cl2.inputs[6].default_value = rgba(clouds[3])
            cl2.inputs[7].default_value = rgba(ccol)
            nt.links.new(cl2.outputs[2], mx.inputs[7])
        else:
            mx.inputs[7].default_value = rgba(ccol)
        col = mx.outputs[2]
    if stars > 0:
        vor = nt.nodes.new("ShaderNodeTexVoronoi")
        vor.inputs["Scale"].default_value = 420.0
        nt.links.new(nrm.outputs[0], vor.inputs["Vector"])
        sr = nt.nodes.new("ShaderNodeValToRGB")
        sr.color_ramp.elements[0].position = 0.0
        sr.color_ramp.elements[0].color = (1, 1, 1, 1)
        sr.color_ramp.elements[1].position = 0.06
        sr.color_ramp.elements[1].color = (0, 0, 0, 1)
        nt.links.new(vor.outputs["Distance"], sr.inputs[0])
        sn = nt.nodes.new("ShaderNodeTexNoise")
        sn.inputs["Scale"].default_value = 60.0
        nt.links.new(nrm.outputs[0], sn.inputs["Vector"])
        sm2 = nt.nodes.new("ShaderNodeMath")
        sm2.operation = "MULTIPLY"
        nt.links.new(sr.outputs[0], sm2.inputs[0])
        nt.links.new(sn.outputs["Fac"], sm2.inputs[1])
        sm3 = nt.nodes.new("ShaderNodeMath")
        sm3.operation = "MULTIPLY"
        sm3.inputs[1].default_value = stars
        nt.links.new(sm2.outputs[0], sm3.inputs[0])
        hz = nt.nodes.new("ShaderNodeMath")
        hz.operation = "MULTIPLY"
        nt.links.new(sm3.outputs[0], hz.inputs[0])
        nt.links.new(sep2.outputs[2], hz.inputs[1])
        ad2 = nt.nodes.new("ShaderNodeMix")
        ad2.data_type = "RGBA"
        ad2.blend_type = "ADD"
        nt.links.new(hz.outputs[0], ad2.inputs[0])
        nt.links.new(col, ad2.inputs[6])
        ad2.inputs[7].default_value = (1, 1, 1, 1)
        col = ad2.outputs[2]
    if moon is not None:
        mdir, msize, mcol = moon[:3]
        d = Vector(mdir).normalized()
        dot = nt.nodes.new("ShaderNodeVectorMath")
        dot.operation = "DOT_PRODUCT"
        dot.inputs[1].default_value = tuple(d)
        nt.links.new(nrm.outputs[0], dot.inputs[0])
        mr = nt.nodes.new("ShaderNodeValToRGB")
        c0 = math.cos(math.radians(msize))
        mr.color_ramp.elements[0].position = c0 - 0.00004
        mr.color_ramp.elements[0].color = (0, 0, 0, 1)
        mr.color_ramp.elements[1].position = c0 + 0.00002
        mr.color_ramp.elements[1].color = (1, 1, 1, 1)
        nt.links.new(dot.outputs["Value"], mr.inputs[0])
        disc = mr.outputs[0]
        if len(moon) > 3 and moon[3]:       # lunar maria: low-frequency dark patches across the disc
            mn = nt.nodes.new("ShaderNodeTexNoise")
            mn.inputs["Scale"].default_value = 90.0
            mn.inputs["Detail"].default_value = 5.0
            mn.inputs["Roughness"].default_value = 0.58
            nt.links.new(nrm.outputs[0], mn.inputs["Vector"])
            mrp = nt.nodes.new("ShaderNodeMapRange")
            mrp.inputs[1].default_value = 0.40
            mrp.inputs[2].default_value = 0.62
            mrp.inputs[3].default_value = 0.55
            mrp.inputs[4].default_value = 1.0
            nt.links.new(mn.outputs["Fac"], mrp.inputs[0])
            mm = nt.nodes.new("ShaderNodeMath")
            mm.operation = "MULTIPLY"
            nt.links.new(mr.outputs[0], mm.inputs[0])
            nt.links.new(mrp.outputs[0], mm.inputs[1])
            disc = mm.outputs[0]
        halo = nt.nodes.new("ShaderNodeMath")
        halo.operation = "POWER"
        nt.links.new(dot.outputs["Value"], halo.inputs[0])
        halo.inputs[1].default_value = 3000.0
        hm = nt.nodes.new("ShaderNodeMath")
        hm.operation = "MULTIPLY"
        hm.inputs[1].default_value = 0.35
        nt.links.new(halo.outputs[0], hm.inputs[0])
        tot = nt.nodes.new("ShaderNodeMath")
        tot.operation = "ADD"
        nt.links.new(disc, tot.inputs[0])
        nt.links.new(hm.outputs[0], tot.inputs[1])
        ad3 = nt.nodes.new("ShaderNodeMix")
        ad3.data_type = "RGBA"
        ad3.blend_type = "ADD"
        ad3.clamp_result = False
        nt.links.new(tot.outputs[0], ad3.inputs[0])
        nt.links.new(col, ad3.inputs[6])
        ad3.inputs[7].default_value = rgba(mcol, 1)
        col = ad3.outputs[2]
    bg = nt.nodes.new("ShaderNodeBackground")
    bg.name = "Background"
    bg.inputs["Strength"].default_value = strength
    nt.links.new(col, bg.inputs["Color"])
    if ambient is not None:
        # camera sees the art-directed sky; the scene is lit by a tuned ambient (keeps colours clean)
        amb = nt.nodes.new("ShaderNodeBackground")
        amb.name = "Ambient"
        amb.inputs["Color"].default_value = rgba(ambient[0])
        amb.inputs["Strength"].default_value = ambient[1]
        lp = nt.nodes.new("ShaderNodeLightPath")
        mx = nt.nodes.new("ShaderNodeMixShader")
        nt.links.new(lp.outputs["Is Camera Ray"], mx.inputs[0])
        nt.links.new(amb.outputs[0], mx.inputs[1])
        nt.links.new(bg.outputs[0], mx.inputs[2])
        nt.links.new(mx.outputs[0], out.inputs["Surface"])
    else:
        nt.links.new(bg.outputs[0], out.inputs["Surface"])
    return w


def world_flat(color="#202830", strength=1.0):
    w = bpy.data.worlds.new("World")
    bpy.context.scene.world = w
    w.use_nodes = True
    bg = w.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = rgba(color)
    bg.inputs["Strength"].default_value = strength
    return w


# ------------------------------------------------------------------ camera + render
def camera(loc, target, lens=35.0, dof=None, sensor=36.0, name="Cam"):
    cd = bpy.data.cameras.new(name)
    cd.lens = lens
    cd.sensor_width = sensor
    cd.clip_start = 0.02
    cd.clip_end = 3000
    ob = link(bpy.data.objects.new(name, cd))
    ob.location = loc
    _aim(ob, target)
    if dof:
        cd.dof.use_dof = True
        cd.dof.focus_distance = (Vector(target) - Vector(loc)).length if dof[0] is None else dof[0]
        cd.dof.aperture_fstop = dof[1]
    bpy.context.scene.camera = ob
    return ob


def render_setup(res=(1920, 1080), samples=32, volumetric=False, vol_tile="8", vol_samples=64, ssr=True,
                 gtao_dist=0.6, bloom=0.04, look="AgX - Punchy", exposure=0.0, gamma=1.0, transparent=False,
                 shadow_cube="2048", shadow_cascade="4096", motion_blur=False, high_bit=False):
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_EEVEE"
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.resolution_percentage = 100
    sc.render.film_transparent = transparent
    e = sc.eevee
    e.taa_render_samples = samples
    e.use_soft_shadows = True
    e.shadow_cube_size = shadow_cube
    e.shadow_cascade_size = shadow_cascade
    e.use_shadow_high_bitdepth = True
    e.use_gtao = True
    e.gtao_distance = gtao_dist
    e.gtao_factor = 1.0
    e.use_gtao_bent_normals = True
    e.use_gtao_bounce = True
    e.use_bloom = bloom > 0
    e.bloom_intensity = bloom
    e.bloom_threshold = 1.2
    e.bloom_radius = 5.0
    e.use_ssr = ssr
    e.use_ssr_refraction = False
    e.ssr_quality = 0.5
    e.ssr_thickness = 0.1
    e.sss_samples = 9
    e.sss_jitter_threshold = 0.3
    e.use_volumetric_lights = True
    e.use_volumetric_shadows = volumetric
    e.volumetric_tile_size = vol_tile
    e.volumetric_samples = vol_samples
    e.volumetric_start = 0.5
    e.volumetric_end = 400.0
    e.use_motion_blur = motion_blur
    e.gi_diffuse_bounces = 2
    e.gi_cubemap_resolution = "512"
    e.gi_visibility_resolution = "16"
    e.gi_irradiance_smoothing = 0.2
    e.light_threshold = 0.005
    sc.view_settings.view_transform = "AgX"
    try:
        sc.view_settings.look = look
    except TypeError:
        pass
    sc.view_settings.exposure = exposure
    sc.view_settings.gamma = gamma
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGBA" if transparent else "RGB"
    sc.render.image_settings.color_depth = "16" if high_bit else "8"
    sc.render.filter_size = 1.2
    return sc


def bake_light_cache(irr=None, cubemap=None):
    """Bake Eevee indirect light (irradiance volumes + reflection cubemaps). Works headless with EGL."""
    try:
        bpy.ops.scene.light_cache_bake()
        return True
    except Exception as ex:   # pragma: no cover
        print("light cache bake failed:", ex)
        return False


def irradiance_volume(loc, size, res=(6, 6, 3), bias=0.3):
    pr = bpy.data.lightprobes.new("Irr", "GRID")
    pr.grid_resolution_x, pr.grid_resolution_y, pr.grid_resolution_z = res
    try:
        pr.grid_bake_samples = 512
    except AttributeError:
        pass
    ob = link(bpy.data.objects.new("Irr", pr))
    ob.location = loc
    ob.scale = size
    return ob


def volume_fog(density=0.01, color="#D8E2EA", anisotropy=0.3, size=200.0, center=(0, 0, 0), height=None,
               emission=None):
    """Large cube with a Principled Volume for atmospheric depth and light shafts (plates only)."""
    nb, m = new_mat("fog_%s_%s" % (color, density))
    if nb is not None:
        pv = nb.n("ShaderNodeVolumePrincipled", Density=density, Anisotropy=anisotropy)
        pv.inputs["Color"].default_value = rgba(color)
        if height is not None:   # exponential falloff with height
            tc = nb.coord("Object")
            sep = nb.n("ShaderNodeSeparateXYZ")
            nb.l(tc, sep.inputs[0])
            ex = nb.math("MULTIPLY", sep.outputs[2], -1.0 / height)
            ex2 = nb.math("EXPONENT", ex)
            d = nb.math("MULTIPLY", ex2, density)
            nb.l(d, pv.inputs["Density"])
        if emission:
            pv.inputs["Emission Color"].default_value = rgba(emission[0])
            pv.inputs["Emission Strength"].default_value = emission[1]
        nb.l(pv.outputs[0], nb.out.inputs["Volume"])
    bpy.ops.mesh.primitive_cube_add(size=1)
    ob = bpy.context.active_object
    ob.name = "Fog"
    ob.location = center
    ob.scale = (size, size, size * 0.25)
    ob.data.materials.append(m)
    return ob
