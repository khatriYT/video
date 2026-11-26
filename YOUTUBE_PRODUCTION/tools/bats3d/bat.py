"""v3 bats: rigged flyer (fur, membrane wings stretched over finger bones) and hanging roosters.

CRE_BAT_MYOTIS (little brown bat), CRE_BAT_FREETAIL (Brazilian / Mexican free-tailed bat),
CRE_BAT_NECTAR (lesser long-nosed bat), CRE_BAT_FLYINGFOX (fruit bat). Variant `wns=True` adds the
white-nose fungus (white fuzz on muzzle, ears and wing membranes).
"""
import math
import os

import bpy
from mathutils import Euler, Quaternion, Vector

import batskel as BK
import meshio
from core import (NB, Rig, _shift, attr, fix_texspace, link, m_membrane, m_simple, mesh_ob, new_mat, rgba, smooth,
                  tube)

MODELS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "01_PROJECTS",
                      "what_if_bats_disappeared", "07_3D_Assets", "models")


def m_batskin(name, S, wns=0.0):
    """Body shader: fur colour where fur grows (attr R), bare dark skin (G), white fungus (B * wns)."""
    nb, m = new_mat(name)
    if nb is None:
        return m
    t = attr(nb, "tint")
    sep = nb.n("ShaderNodeSeparateColor")
    nb.l(t.outputs["Color"], sep.inputs[0])
    gen = nb.coord("Generated")
    nz = nb.noise(gen, 900.0, 4.0, 0.6)
    furc = nb.ramp(nz.outputs["Fac"], [(0.3, _shift(S["fur"], -0.05)), (0.7, S["fur_tip"])]).outputs[0]
    skinc = nb.ramp(nz.outputs["Fac"], [(0.3, _shift(S["skin"], -0.03)), (0.7, _shift(S["skin"], 0.05))]).outputs[0]
    col = nb.mix(furc, skinc, sep.outputs[1])
    if S.get("mantle"):
        sp = nb.n("ShaderNodeSeparateXYZ")
        nb.l(gen, sp.inputs[0])
        mm = nb.ramp(sp.outputs[1], [(0.47, 1.0), (0.49, 0.0)])   # front half (neck + shoulders): golden mantle
        mm2 = nb.math("MULTIPLY", mm.outputs[0], sep.outputs[0])
        col = nb.mix(col, S["mantle"], mm2)
    fun = nb.math("MULTIPLY", sep.outputs[2], wns)
    fz = nb.noise(gen, 2600.0, 3.0, 0.8)
    fm = nb.math("MULTIPLY", fun, nb.ramp(fz.outputs["Fac"], [(0.35, 0.3), (0.6, 1.0)]).outputs[0])
    col = nb.mix(col, "#F4F1EA", fm)
    h = nb.math("ADD", nz.outputs["Fac"], nb.math("MULTIPLY", fz.outputs["Fac"], fun))
    rough = nb.math("ADD", 0.45, nb.math("MULTIPLY", sep.outputs[0], 0.35))
    nb.bsdf(**{"Base Color": col, "Roughness": rough, "Normal": nb.bump(h, 0.3, 0.0003),
               "Subsurface Weight": 0.12, "Subsurface Radius": (1.0, 0.35, 0.2), "Subsurface Scale": 0.002,
               "Sheen Weight": 0.6, "Specular IOR Level": 0.4})
    return m


def m_fur(name, root, tip, white=0.0):
    nb, m = new_mat(name)
    if nb is None:
        return m
    hi = nb.n("ShaderNodeHairInfo")
    f = nb.math("ADD", hi.outputs["Intercept"], nb.math("MULTIPLY", hi.outputs["Random"], 0.3))
    col = nb.ramp(f, [(0.0, _shift(root, -0.08)), (0.5, root), (1.0, tip)]).outputs[0]
    if white:
        col = nb.mix(col, "#F6F3EC", None, fac_val=white)
    nb.bsdf(**{"Base Color": col, "Roughness": 0.55, "Sheen Weight": 0.7, "Specular IOR Level": 0.35})
    return m


def add_fur(ob, mat, density_group, count, length, radius=0.0002, children=0, clump=0.3, seed=1):
    mod = ob.modifiers.new("fur", "PARTICLE_SYSTEM")
    ps = ob.particle_systems[-1]
    st = ps.settings
    st.type = "HAIR"
    st.count = count
    st.hair_length = length
    st.use_advanced_hair = False
    st.emit_from = "FACE"
    st.use_emit_random = True
    st.distribution = "RAND"
    st.root_radius = 1.0
    st.tip_radius = 0.0
    st.radius_scale = radius
    st.use_close_tip = True
    st.display_step = 3
    st.render_step = 3
    st.child_type = "INTERPOLATED" if children else "NONE"
    st.rendered_child_count = children
    st.child_percent = max(1, children // 4)
    st.clump_factor = clump
    st.roughness_1 = 0.4
    st.roughness_1_size = 1.0
    st.roughness_endpoint = 0.1
    st.length_random = 0.4
    ob.data.materials.append(mat)
    st.material = len(ob.data.materials)
    ps.vertex_group_density = density_group
    ps.vertex_group_length = density_group
    ps.seed = seed
    return ps


def group_from_attr(ob, name, channel, src="tint", power=1.0):
    me = ob.data
    ca = me.color_attributes[src]
    vg = ob.vertex_groups.new(name=name)
    buckets = {}
    for i, d in enumerate(ca.data):
        w = d.color[channel] ** power
        if w > 0.02:
            buckets.setdefault(round(w, 2), []).append(i)
    for w, idx in buckets.items():
        vg.add(idx, w, "REPLACE")
    return name


# ------------------------------------------------------------------ membrane
def _resample(chain, n):
    """chain: list of (point Vector, bone name); returns n samples [(point, {bone: w})]."""
    pts = [p for p, _ in chain]
    L = [0.0]
    for i in range(1, len(pts)):
        L.append(L[-1] + (pts[i] - pts[i - 1]).length)
    out = []
    for k in range(n):
        u = L[-1] * k / (n - 1)
        i = max(0, min(len(pts) - 2, next((j for j in range(len(pts) - 1) if L[j + 1] >= u), len(pts) - 2)))
        t = (u - L[i]) / max(L[i + 1] - L[i], 1e-9)
        p = pts[i].lerp(pts[i + 1], t)
        b0 = chain[i][1]
        w = {b0: 1.0}
        if t > 0.75 and i + 1 < len(chain) - 1 and chain[i + 1][1] != b0:     # blend into the next bone
            a = (t - 0.75) / 0.5
            w = {b0: 1.0 - a, chain[i + 1][1]: a}
        elif t < 0.25 and i > 0 and chain[i - 1][1] != b0:
            a = (0.25 - t) / 0.5
            w = {b0: 1.0 - a, chain[i - 1][1]: a}
        out.append((p, w))
    return out


def membrane(name, panels, mat, nu=14, nv=8):
    """panels: list of (chainA, chainB, sag, nu, nv). Each grid vertex = lerp(A(u), B(u), v), trailing edge sags
    inward. Returns object + per-vertex bone weights."""
    verts, faces, weights = [], [], []
    for A, B, sag, pu, pv in panels:
        pu = pu or nu
        pv = pv or nv
        a = _resample(A, pu)
        b = _resample(B, pu)
        base = len(verts)
        for i in range(pu):
            u = i / (pu - 1)
            for j in range(pv):
                v = j / (pv - 1)
                p = a[i][0].lerp(b[i][0], v)
                if i == pu - 1 or sag:
                    # pull the free trailing edge toward the wrist side (scalloped edge)
                    edge = (u ** 6)
                    mid = a[0][0].lerp(b[0][0], v)
                    p = p.lerp(mid, sag * edge * math.sin(math.pi * v))
                    p.z += 0.0008 * math.sin(math.pi * v) * (1 - u) * 0.5   # slight billow
                verts.append(p)
                w = {}
                for bn, x in a[i][1].items():
                    w[bn] = w.get(bn, 0) + x * (1 - v)
                for bn, x in b[i][1].items():
                    w[bn] = w.get(bn, 0) + x * v
                weights.append(w)
        for i in range(pu - 1):
            for j in range(pv - 1):
                q = base + i * pv + j
                faces.append((q, q + pv, q + pv + 1, q + 1))
    ob = mesh_ob(name, verts, faces, mat)
    for i, w in enumerate(weights):
        for bn, x in w.items():
            if x > 1e-3:
                vg = ob.vertex_groups.get(bn) or ob.vertex_groups.new(name=bn)
                vg.add([i], x, "REPLACE")
    return ob


class Bat:
    pass


def build(name, sp, mode="flyer", wns=0.0, fur=True, loc=(0, 0, 0), scale=1.0, fur_density=1.0):
    S = BK.SPECIES[sp]
    sc = S["scale"] * scale
    b = Bat()
    b.name, b.sp, b.mode, b.S = name, sp, mode, S
    body_m = m_batskin(f"batskin_{sp}_{wns}", S, wns)
    fur_m = m_fur(f"batfur_{sp}", S["fur"], S["fur_tip"])
    eye_m = m_simple("bateye", "#050403", 0.08, coat=1.0, spec=0.8)
    parts = []
    if mode == "flyer":
        rig = Rig(name, BK.bones(sp))
        b.rig = rig
        body = meshio.load(os.path.join(MODELS, f"bat_{sp}", "body.bin"), name + "_body", body_m, 3)
        rig.skin(body, allowed=[n for n in ("body", "head", "tail", "thigh.L", "thigh.R", "shin.L", "shin.R")
                                if n in rig.spec], power=4.0, eps=0.003)
        parts.append(body)
        P = {k: Vector(v) for k, v in BK.points(sp).items()}
        sn = S["snout"]
        for sx in (1, -1):
            e = _eye(f"{name}_eye{sx}", eye_m, S["eye_r"])
            e.location = (sx * 0.0062, -0.0445 - sn * 0.25, 0.0088)
            rig.attach(e, "head")
            parts.append(e)
        # arm and finger bones (visible through the membrane), thumb claw
        bone_m = m_simple(f"batbone_{sp}", _shift(S["skin"], 0.06), 0.45, sss=0.2)
        claw_m = m_simple("batclaw", "#1A1410", 0.3, coat=0.5)
        mem_m = m_membrane(f"membrane_{sp}_{wns}", S["membrane"], _shift(S["membrane"], 0.08), 0.45)
        panels = []
        for sx, s in ((1, "L"), (-1, "R")):
            M = lambda k: Vector((P[k].x * sx, P[k].y, P[k].z))   # noqa: E731
            segs = [("S", "E", f"hum.{s}", 0.0024, 0.002), ("E", "W", f"fore.{s}", 0.0019, 0.0017),
                    ("W", "K2", f"d2a.{s}", 0.0009, 0.0007), ("K2", "tip2", f"d2b.{s}", 0.0007, 0.0004),
                    ("W", "K3", f"d3a.{s}", 0.001, 0.0008), ("K3", "tip3", f"d3b.{s}", 0.0008, 0.0004),
                    ("W", "K4", f"d4a.{s}", 0.0009, 0.0007), ("K4", "tip4", f"d4b.{s}", 0.0007, 0.0004),
                    ("W", "K5", f"d5a.{s}", 0.0009, 0.0007), ("K5", "tip5", f"d5b.{s}", 0.0007, 0.0004),
                    ("W", "T", f"d1.{s}", 0.0011, 0.0006)]
            for a, c, bn, ra, rc in segs:
                t = tube(f"{name}_{bn}_{a}", [M(a), M(a).lerp(M(c), 0.5), M(c)], [ra, (ra + rc) / 2, rc], 8, bone_m)
                rig.attach(t, bn)
                parts.append(t)
            for k in ("E", "W", "K3", "K4", "K5", "K2"):
                j = _eye(f"{name}_j{k}{s}", bone_m, 0.0013 if k in ("E", "W") else 0.0008)
                j.location = M(k)
                rig.attach(j, {"E": f"fore.{s}", "W": f"fore.{s}", "K3": f"d3b.{s}", "K4": f"d4b.{s}",
                               "K5": f"d5b.{s}", "K2": f"d2b.{s}"}[k])
                parts.append(j)
            cl = tube(f"{name}_claw{s}", [M("T"), M("T") + Vector((0, -0.0022, -0.0012)),
                                         M("T") + Vector((0, -0.003, -0.003))], [0.0007, 0.0004, 0.0001], 6, claw_m)
            rig.attach(cl, f"d1.{s}")
            parts.append(cl)
            arm = [(M("S"), f"hum.{s}"), (M("E"), f"fore.{s}"), (M("W"), f"fore.{s}")]
            front = [(M("S") + Vector((0, -0.006, 0.001)), f"hum.{s}"), (M("E") + Vector((0, -0.013, 0.0)), f"hum.{s}"),
                     (M("W") + Vector((0, -0.006, 0.0)), f"fore.{s}")]
            d2 = [(M("W"), f"d2a.{s}"), (M("K2"), f"d2b.{s}"), (M("tip2"), f"d2b.{s}")]
            d3 = [(M("W"), f"d3a.{s}"), (M("K3"), f"d3b.{s}"), (M("tip3"), f"d3b.{s}")]
            d4 = [(M("W"), f"d4a.{s}"), (M("K4"), f"d4b.{s}"), (M("tip4"), f"d4b.{s}")]
            d5 = [(M("W"), f"d5a.{s}"), (M("K5"), f"d5b.{s}"), (M("tip5"), f"d5b.{s}")]
            armd5 = [(M("S"), f"hum.{s}"), (M("E"), f"fore.{s}"), (M("W"), f"d5a.{s}"), (M("K5"), f"d5b.{s}"),
                     (M("tip5"), f"d5b.{s}")]
            side = [(M("S"), "body"), (Vector((sx * 0.012, 0.004, 0.0)), "body"), (M("H"), f"thigh.{s}"),
                    (M("Kn"), f"shin.{s}"), (M("A"), f"shin.{s}")]
            panels += [(arm, front, 0.0, 10, 3), (d2, d3, 0.05, 12, 4), (d3, d4, 0.32, 14, 9), (d4, d5, 0.22, 12, 8),
                       (side, armd5, 0.18, 18, 12)]
            if S["tail"] > 0:
                leg = [(M("H"), f"thigh.{s}"), (M("Kn"), f"shin.{s}"), (M("A"), f"shin.{s}")]
                tl = [(P["tail0"], "tail"), (P["tail0"].lerp(P["tail1"], 0.8 if S["free_tail"] else 1.0), "tail")]
                panels.append((tl, leg, 0.25, 8, 6))
        mem = membrane(name + "_membrane", panels, mem_m)
        sub = mem.modifiers.new("sub", "SUBSURF")
        sub.levels = sub.render_levels = 1
        mod = mem.modifiers.new("Armature", "ARMATURE")
        mod.object = rig.ob
        mem.modifiers.move(1, 0)
        mem.parent = rig.ob
        if wns:
            # fungus patches on the membranes via a second material slot blend: handled by the membrane shader tint
            pass
        parts.append(mem)
        b.membrane = mem
        root = rig.ob
    else:
        body = meshio.load(os.path.join(MODELS, f"bat_{sp}", "hanger.bin"), name + "_hang", body_m, 3)
        sn = S["snout"]
        for sx in (1, -1):
            e = _eye(f"{name}_eye{sx}", eye_m, S["eye_r"])
            e.location = (sx * 0.006, -0.0105, -0.037)
            e.scale = (1.0, 1.0, 0.35 if wns or sp == "myotis" else 1.0)     # hibernating: eyes shut
            e.parent = body
            parts.append(e)
        parts.append(body)
        root = body
        b.rig = None
    if fur:
        group_from_attr(body, "fur", 0)
        n = int((5000 if mode == "flyer" else 3500) * fur_density)
        add_fur(body, fur_m, "fur", n, 0.0042 if sp != "flyingfox" else 0.0038, radius=0.00022,
                children=6 if fur_density >= 1 else 3, seed=len(name))
        if wns:
            group_from_attr(body, "fungus", 2, power=1.5)
            wm = m_fur("fungusfur", "#E9E6DE", "#FFFFFF", 0.0)
            add_fur(body, wm, "fungus", int(2500 * wns), 0.0016, radius=0.00012, children=4, clump=0.0, seed=3)
    for ob in parts:
        ob["mask"] = 1.0
        fix_texspace(ob)
    root.location = loc
    root.scale = (sc,) * 3
    b.parts = parts
    b.root = root
    b.body = body
    return b


def _eye(name, m, r):
    from human import _sphere
    e = _sphere(name, 1.0, m, 16, 8)
    e.scale = (r,) * 3
    return e


# ------------------------------------------------------------------ motion
def pose(b, rots):
    rig = b.rig
    for pb in rig.ob.pose.bones:
        pb.rotation_mode = "QUATERNION"
        r = rots.get(pb.name)
        if r is None:
            pb.rotation_quaternion = Quaternion()
            continue
        q = Euler([math.radians(a) for a in r], "XYZ").to_quaternion()
        R = pb.bone.matrix_local.to_quaternion()
        pb.rotation_quaternion = R.inverted() @ q @ R


def flap(t, freq=8.0, amp=55.0, fold=38.0, phase=0.0, glide=0.0, hover=0.0):
    """Wing-beat cycle. glide 0..1 blends toward a fixed extended glide; hover tilts the stroke plane."""
    ph = 2 * math.pi * (t * freq) + phase
    e = amp * math.cos(ph) * (1 - glide) + 8 * glide
    up = max(0.0, -math.sin(ph)) ** 0.8 * (1 - glide)
    f = fold * up
    r = {}
    for s, sg in (("L", 1), ("R", -1)):
        r[f"hum.{s}"] = (0, -sg * e, sg * (6 + 0.3 * f))
        r[f"fore.{s}"] = (0, -sg * 0.25 * e, sg * f * 0.9)
        r[f"d3a.{s}"] = (0, 0, sg * f * 0.6)
        r[f"d3b.{s}"] = (0, -sg * 10 * math.cos(ph) * (1 - glide), sg * f * 0.4)
        r[f"d4a.{s}"] = (0, 0, sg * f * 0.5)
        r[f"d4b.{s}"] = (0, 0, sg * f * 0.3)
        r[f"d5a.{s}"] = (0, 0, sg * f * 0.3)
        r[f"d2a.{s}"] = (0, 0, sg * f * 0.6)
        r[f"thigh.{s}"] = (8, 0, 0)
    r["head"] = (-4 * math.cos(ph), 0, 0)
    r["tail"] = (6 * math.sin(ph), 0, 0)
    r["body"] = (2 * math.sin(ph) + hover * 0.0, 0, 0)
    return r


def animate(b, t, kind="flap", **kw):
    if b.mode == "flyer":
        if kind == "flap":
            pose(b, flap(t, **kw))
        elif kind == "glide":
            pose(b, flap(t, glide=1.0))
        elif kind == "spread":
            pose(b, flap(0.0, glide=1.0))
        elif kind == "hover":
            pose(b, flap(t, freq=kw.get("freq", 11.0), amp=40, fold=25))
    else:
        # hanging: slow breathing; `wake` adds shivering
        br = 1.0 + 0.02 * math.sin(t * 2 * math.pi / 2.5)
        sc = b.S["scale"] * kw.get("scale", 1.0)
        b.root.scale = (sc * br, sc * br, sc)
        if kind == "wake":
            b.root.rotation_euler = (0.0, 0.03 * math.sin(t * 61.0), kw.get("rz", 0.0) + 0.05 * math.sin(t * 2.0))
