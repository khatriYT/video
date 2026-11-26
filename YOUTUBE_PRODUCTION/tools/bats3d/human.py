"""v3 stylised human characters (CHR_PIP v3, CHR_FARMER, CHR_RESEARCHER).

Built from implicit surfaces (metaballs -> mesh -> smoothing), skinned to a real armature with
numpy distance weights. Faces have sculpted brows, nose with alae and nostrils, lips, cheeks, chin and
ears with a carved concha; separate glossy eyeballs with procedural irises, eyelid shells (blinks),
lashes and brows; five-fingered hands with three-segment fingers and a thumb; layered clothing
(shirt with collar and rolled sleeves, vest with pockets, trousers with belt and cuffs, laced boots),
bucket hat, round wire glasses, bandana, satchel. All materials are PBR (core.py).

Pose convention: rotations are Euler degrees about the ARMATURE axes at rest (x right, y back, z up),
applied relative to the parent's posed frame. Character faces -Y.
"""
import math

import bpy
import random
from mathutils import Euler, Matrix, Quaternion, Vector

from core import (Rig, fix_texspace, _shift, lathe, link, m_eye, m_fabric,
                  m_glass, m_hair, m_leather, m_metal, m_rubber, m_simple, m_skin, mesh_ob, smooth, tube, verts_np)

HEAD_C = Vector((0.0, 0.0, 1.565))      # head centre (rest)

PALETTES = {
    "pip": dict(skin="#E0A986", blush="#D0705C", hair="#7A3B1E", hair_tip="#B0663A", iris="#5C7E3A",
                iris2="#C9A04E", shirt="#EDE3CC", vest="#6E8B3D", trousers="#3D4A5E", boots="#6B4226",
                hat="#E9A21A", band="#7A4A1E", glasses="#3B2A1E", scarf="#C8442E", satchel="#B39563",
                freckles=0.45, hat_kind="bucket", vest_on=True, glasses_on=True, beard=False),
    "farmer": dict(skin="#9A6646", blush="#A85445", hair="#2B211C", hair_tip="#4A3A30", iris="#4A3020",
                   iris2="#7A5430", shirt=("plaid", "#B53A2E", "#2E3F66", "#E8D9B8"), vest="#355C8C",
                   trousers="#3A5A8A", boots="#5A3A22", hat="#D9CDB0", band="#6E5A3E", glasses="#3B2A1E",
                   scarf=None, satchel=None, freckles=0.0, hat_kind="cap", vest_on=False, overalls=True,
                   glasses_on=False, beard=True),
    "researcher": dict(skin="#C68A62", blush="#C0604E", hair="#1E1714", hair_tip="#3A2A22", iris="#3B2618",
                       iris2="#6B4A2A", shirt="#4E7C8A", vest="#C9873A", trousers="#4B4038", boots="#3E2E22",
                       hat="#E8C23A", band="#3A3A3A", glasses="#222222", scarf=None, satchel="#7A6A52",
                       freckles=0.0, hat_kind="helmet", vest_on=True, glasses_on=False, beard=False),
}


# ------------------------------------------------------------------ helpers
def linspace(a, b, n):
    return [a + (b - a) * i / (n - 1) for i in range(n)]


def hx(ob, S=None):
    """Scale a head-attached object about the head centre by the stylised head scale."""
    S = SK.HEAD_S if S is None else S
    Hc = Vector(SK.HEAD_C)
    if ob.location.length < 1e-9 and ob.parent is None:
        ob.data.transform(Matrix.Translation(Hc) @ Matrix.Scale(S, 4) @ Matrix.Translation(-Hc))
    else:
        ob.location = Hc + (Vector(ob.location) - Hc) * S
        ob.scale = Vector(ob.scale) * S
    return ob


class Face:
    """Eyes, lids, lashes, brows and their animation (all parented to the head bone)."""

    def __init__(self, name, pal, rig, head_c):
        self.parts = []
        self.eyes, self.uplids, self.lolids, self.brows = [], [], [], []
        em = m_eye("eye_" + name, pal["iris"], pal["iris2"])
        lid_m = m_skin("skin_" + name, pal["skin"], pal["blush"], pal["freckles"])
        lash_m = m_simple("lash_" + name, _shift(pal["hair"], -0.12), 0.5)
        brow_m = m_hair("brow_" + name, _shift(pal["hair"], -0.03), pal["hair"], scale=260)
        self.r = 0.0172
        self.lamp = None
        for sx in (1, -1):
            c = head_c + Vector((sx * 0.033, -0.067, 0.002))
            eye = _sphere(f"{name}_eye{sx}", 1.0, em, 40, 20)
            eye.scale = (self.r,) * 3
            eye.location = c
            eye.rotation_euler = (0, 0, math.radians(-sx * 4))
            hx(eye)
            rig.attach(eye, "head")
            self.eyes.append((eye, c, sx))
            up = _sphere(f"{name}_lidU{sx}", self.r * 1.075, lid_m, 40, 20, cut=(2, 1))
            sol = up.modifiers.new("sol", "SOLIDIFY")
            sol.thickness = 0.0014
            sol.offset = 1.0
            up.location = c
            hx(up)
            rig.attach(up, "head")
            lo = _sphere(f"{name}_lidL{sx}", self.r * 1.06, lid_m, 40, 20, cut=(2, -1))
            sol = lo.modifiers.new("sol", "SOLIDIFY")
            sol.thickness = 0.0012
            sol.offset = 1.0
            lo.location = c
            hx(lo)
            rig.attach(lo, "head")
            # lashes: a thin fan along the upper lid edge (built in lid-local space, rotates with the lid)
            pts, faces = [], []
            n = 14
            for k in range(n + 1):
                a = math.radians(-70 + 140 * k / n)     # around the front of the eye
                x, y = math.sin(a) * self.r * 1.09, -math.cos(a) * self.r * 1.09
                pts.append((x, y, 0.0004))
                ln = 0.0042 * (0.55 + 0.45 * math.sin(math.pi * k / n)) * (1.25 if sx * x > 0 else 1.0)
                pts.append((x * 1.18, y * 1.18 + 0.0012, ln))
            for k in range(n):
                faces.append((2 * k, 2 * k + 2, 2 * k + 3, 2 * k + 1))
            lash = mesh_ob(f"{name}_lash{sx}", pts, faces, lash_m)
            lash.parent = up
            self.uplids.append((up, sx))
            self.lolids.append((lo, sx))
            # brow: tapered flattened tube
            bp = []
            for k in range(9):
                u = k / 8
                x = sx * (0.012 + 0.04 * u)
                bp.append(head_c + Vector((x, -0.0885 + 0.0125 * u * u, 0.034 + 0.0075 * math.sin(math.pi * u * 0.9))))
            brow = tube(f"{name}_brow{sx}", bp, [0.0036 * (1 - 0.5 * k / 8) + 0.0008 for k in range(9)], 8, brow_m)
            hx(brow)
            rig.attach(brow, "head")
            self.brows.append((brow, sx, brow.location.copy(), brow.rotation_euler.copy()))
            self.parts += [eye, up, lo, lash, brow]
        self.set(0.0, 0.0, (0, -1, 0))

    def set(self, blink=0.0, brow_up=0.0, look=(0, -1, 0), squint=0.0, worried=0.0):
        """blink 0 open .. 1 closed; brow_up -1..1; look: direction in head space (default forward)."""
        lk = Vector(look).normalized()
        for eye, c, sx in self.eyes:
            q = Vector((0, -1, 0)).rotation_difference(lk)
            eye.rotation_mode = "QUATERNION"
            eye.rotation_quaternion = q @ Euler((0, 0, math.radians(-sx * 4))).to_quaternion()
        o = 0.5 - 0.1 * squint
        for up, sx in self.uplids:
            ang = -math.asin(o) + (math.asin(o) + math.asin(0.2)) * blink
            up.rotation_euler = (ang + 0.1 * lk.z, 0, math.radians(sx * 6 * worried))
        for lo, sx in self.lolids:
            ang = math.asin(0.48 - 0.12 * squint - 0.1 * blink)
            lo.rotation_euler = (ang, 0, 0)
        for brow, sx, l0, r0 in self.brows:
            brow.location = l0 + Vector((0, 0, 0.004 * brow_up + 0.002 * worried))
            brow.rotation_euler = (r0.x, r0.y + math.radians(sx * 10 * worried), r0.z)


# ------------------------------------------------------------------ build (SDF-sculpted parts from sdf.py)
import json  # noqa: E402
import os  # noqa: E402

import meshio  # noqa: E402
import skeleton as SK  # noqa: E402

MODELS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "01_PROJECTS",
                      "what_if_bats_disappeared", "07_3D_Assets", "models")


def _sphere(name, r, mat, seg=32, rings=16, cut=None):
    """UV sphere (radius r). cut=(axis, sign): keep the half where sign*coord >= 0."""
    verts, faces = [], []
    for i in range(rings + 1):
        th = math.pi * i / rings
        for j in range(seg):
            ph = 2 * math.pi * j / seg
            verts.append((math.sin(th) * math.cos(ph), math.sin(th) * math.sin(ph), math.cos(th)))
    for i in range(rings):
        for j in range(seg):
            j2 = (j + 1) % seg
            faces.append((i * seg + j, i * seg + j2, (i + 1) * seg + j2, (i + 1) * seg + j))
    ob = mesh_ob(name, [(x * r, y * r, z * r) for x, y, z in verts], faces, mat)
    if cut:
        import bmesh
        ax, sg = cut
        bm = bmesh.new()
        bm.from_mesh(ob.data)
        kill = [v for v in bm.verts if sg * v.co[ax] < -1e-6]
        bmesh.ops.delete(bm, geom=kill, context="VERTS")
        bm.to_mesh(ob.data)
        bm.free()
        smooth(ob)
    return ob


def materials(name, pal):
    M = {}
    M["skin"] = m_skin("skin_" + name, pal["skin"], pal["blush"], pal["freckles"])
    M["hair"] = m_hair("hair_" + name, pal["hair"], pal["hair_tip"], scale=420, along="Z")
    sc = pal["shirt"]
    if isinstance(sc, tuple):
        M["shirt"] = m_fabric("shirt_" + name, sc[3], weave=900, pattern=("plaid", sc[1], sc[2], 14.0), bump=0.12)
    else:
        M["shirt"] = m_fabric("shirt_" + name, sc, weave=1100, rough=0.8, sheen=0.25, bump=0.1)
    M["vest"] = m_fabric("vest_" + name, pal["vest"], weave=700, rough=0.86, sheen=0.3, var=0.06, bump=0.16)
    M["trousers"] = m_fabric("trousers_" + name, pal["trousers"], weave=800, rough=0.86, sheen=0.22, var=0.05,
                             bump=0.16)
    M["belt"] = m_leather("belt_" + name, "#4A3020")
    M["boot"] = m_leather("boot_" + name, pal["boots"])
    M["sole"] = m_rubber("sole_" + name)
    if pal.get("scarf"):
        M["scarf"] = m_fabric("scarf_" + name, pal["scarf"], weave=1000, rough=0.78, sheen=0.35, bump=0.1,
                              pattern=("dots", "#F3E6CF", 260.0))
    if pal.get("satchel"):
        M["satchel"] = m_fabric("satchel_" + name, pal["satchel"], weave=500, rough=0.88, sheen=0.2, bump=0.2)
    return M


def build(name="pip", kind="pip", loc=(0, 0, 0), rot_z=0.0, scale=1.0):
    pal = PALETTES[kind]
    H = Vector(SK.HEAD_C)
    rig = Rig(name, SK.bones())
    bone_names = [b[0] for b in SK.bones()]
    M = materials(name, pal)
    man = json.load(open(os.path.join(MODELS, kind, "manifest.json")))
    parts = []
    for p in man["parts"]:
        ob = meshio.load(os.path.join(MODELS, kind, p["file"]), f"{name}_{p['file'][:-4]}", M.get(p["mat"]),
                         p["tint"], p["local"], bone_names)
        mod = ob.modifiers.new("Armature", "ARMATURE")
        mod.object = rig.ob
        mod.use_deform_preserve_volume = True
        ob.parent = rig.ob
        parts.append(ob)
    face = Face(name, pal, rig, H)
    parts += face.parts
    # ---- hat
    if pal["hat_kind"] == "bucket":
        hat_m = m_fabric("hat_" + name, pal["hat"], weave=1200, rough=0.84, sheen=0.4, var=0.05, bump=0.1)
        prof = [(0.0, 0.127), (0.05, 0.126), (0.077, 0.119), (0.0905, 0.1), (0.0955, 0.075), (0.0978, 0.056),
                (0.0986, 0.047), (0.106, 0.0415), (0.124, 0.03), (0.141, 0.0165), (0.149, 0.009)]
        hat = lathe(name + "_hat", prof, 72, hat_m, close_top=False, close_bottom=False)
        sol = hat.modifiers.new("sol", "SOLIDIFY")
        sol.thickness = 0.0035
        sub = hat.modifiers.new("sub", "SUBSURF")
        sub.levels = sub.render_levels = 1
        band = lathe(name + "_band", [(0.1004, 0.0465), (0.0996, 0.058), (0.0982, 0.068)], 72,
                     m_fabric("band_" + name, pal["band"], weave=1400, rough=0.6, bump=0.08), False, False)
        sol2 = band.modifiers.new("sol", "SOLIDIFY")
        sol2.thickness = 0.0025
        stitch_m = m_simple("stitch_" + name, _shift(pal["hat"], -0.22), 0.7)
        hp = [hat, band]
        for rr, zz in ((0.114, 0.0375), (0.127, 0.0306), (0.14, 0.0228)):
            ring = [Vector((math.cos(a) * rr, math.sin(a) * rr, zz + 0.0022)) for a in linspace(0, 2 * math.pi, 97)]
            hp.append(tube(f"{name}_stitch{rr}", ring, 0.0007, 4, stitch_m, caps=False))
        brass = m_metal("brass", "#C9A45A", 0.3)
        for sx in (1, -1):
            ey = tube(f"{name}_eyelet{sx}", [Vector((sx * 0.0935, math.cos(a) * 0.0035, 0.088 + math.sin(a) * 0.0035))
                                             for a in linspace(0, 2 * math.pi, 17)], 0.0012, 5, brass, caps=False)
            hp.append(ey)
        for ob in hp:
            ob.scale = (1.0, 1.1, 1.0)
            ob.location = H + Vector((0, 0.017, -0.006))
            ob.rotation_euler = (math.radians(-7), 0, 0)
            hx(ob)
            rig.attach(ob, "head")
            parts.append(ob)
    elif pal["hat_kind"] == "cap":
        hat_m = m_fabric("hat_" + name, pal["hat"], weave=900, rough=0.85, bump=0.1)
        prof = [(0.0, 0.142), (0.05, 0.14), (0.08, 0.125), (0.094, 0.095), (0.098, 0.06), (0.099, 0.045)]
        crown = lathe(name + "_cap", prof, 64, hat_m, close_top=False, close_bottom=False)
        crown.modifiers.new("sol", "SOLIDIFY").thickness = 0.003
        bill = _sphere(name + "_bill", 1.0, hat_m, 32, 12)
        bill.scale = (0.078, 0.07, 0.006)
        bill.location = (0, -0.1, 0.05)
        for ob in (crown, bill):
            ob.scale = (ob.scale[0], ob.scale[1] * (1.1 if ob is crown else 1.0), ob.scale[2])
            ob.location = H + Vector((0, 0.017, 0.0)) + (Vector(ob.location) if ob is bill else Vector())
            ob.rotation_euler = (math.radians(-4 if ob is crown else -14), 0, 0)
            hx(ob)
            rig.attach(ob, "head")
            parts.append(ob)
    elif pal["hat_kind"] == "helmet":
        hm = m_simple("helmet_" + name, pal["hat"], 0.3, coat=0.6, bump_scale=200.0, bump_strength=0.05)
        prof = [(0.0, 0.15), (0.05, 0.148), (0.085, 0.13), (0.1, 0.095), (0.104, 0.06), (0.106, 0.045),
                (0.112, 0.04), (0.118, 0.036)]
        dome = lathe(name + "_helmet", prof, 64, hm, close_top=False, close_bottom=False)
        dome.modifiers.new("sol", "SOLIDIFY").thickness = 0.004
        lamp = _sphere(name + "_lamp", 1.0, m_simple("lampbody", "#2E2E2E", 0.4), 24, 12)
        lamp.scale = (0.022, 0.016, 0.017)
        lamp.location = (0, -0.112, 0.075)
        lens = _sphere(name + "_lampl", 1.0, m_simple("lamplens", "#FFF4D6", 0.1, emit="#FFF1CF", emit_strength=12.0),
                       24, 12)
        lens.scale = (0.014, 0.004, 0.013)
        lens.location = (0, -0.127, 0.075)
        for ob in (dome, lamp, lens):
            if ob is dome:
                ob.scale = (1.0, 1.1, 1.0)
            ob.location = H + Vector((0, 0.017, 0.0)) + (Vector(ob.location) if ob is not dome else Vector())
            hx(ob)
            rig.attach(ob, "head")
            parts.append(ob)
        face.lamp = lens
    # ---- glasses
    if pal.get("glasses_on"):
        gm = m_metal("glassframe_" + name, pal["glasses"], 0.35)
        lm = m_glass("lens_" + name)
        gparts = []
        for sx in (1, -1):
            c = H + Vector((sx * 0.033, -0.096, 0.002))
            ring = [c + Vector((math.cos(a) * 0.0205, 0.0, math.sin(a) * 0.0195)) for a in linspace(0, 2 * math.pi, 41)]
            gparts.append(tube(f"{name}_rim{sx}", ring, 0.00115, 6, gm, caps=False))
            temple = [c + Vector((sx * 0.0205, 0.0, 0.002)), H + Vector((sx * 0.07, -0.078, 0.008)),
                      H + Vector((sx * 0.083, -0.03, 0.008)), H + Vector((sx * 0.085, 0.012, 0.004)),
                      H + Vector((sx * 0.083, 0.03, -0.012))]
            gparts.append(tube(f"{name}_temple{sx}", temple, 0.001, 5, gm))
            ln = _sphere(f"{name}_lens{sx}", 1.0, lm, 24, 12)
            ln.scale = (0.0203, 0.0016, 0.0193)
            ln.location = c
            gparts.append(ln)
        bridge = [H + Vector((0.0128, -0.096, 0.007)), H + Vector((0.0, -0.094, 0.012)),
                  H + Vector((-0.0128, -0.096, 0.007))]
        gparts.append(tube(name + "_bridge", bridge, 0.0011, 5, gm))
        for g in gparts:
            hx(g)
            rig.attach(g, "head")
            parts.append(g)
    # ---- shirt buttons, belt buckle, boot laces
    btn_m = m_simple("btn_" + name, "#E9E2D2" if not isinstance(pal["shirt"], tuple) else "#2A2A2A", 0.3, coat=0.8)
    for k, z in enumerate((1.33, 1.25, 1.17, 1.09, 1.01)):
        b = _sphere(f"{name}_btn{k}", 1.0, btn_m, 16, 8)
        b.scale = (0.0055, 0.0022, 0.0055)
        b.location = (0, -0.1135 + (0.004 if z > 1.2 else 0.0) - 0.003 * (z < 1.05), z)
        rig.attach(b, "chest" if z > 1.18 else "spine")
        parts.append(b)
    buckle = _sphere(name + "_buckle", 1.0, m_metal("brass", "#C9A45A", 0.3), 16, 8)
    buckle.scale = (0.02, 0.005, 0.016)
    buckle.location = (0, -0.112, 1.0)
    rig.attach(buckle, "pelvis")
    parts.append(buckle)
    lace_m = m_simple("lace_" + name, "#D8CBB0", 0.7)
    for sx, s in ((1, "L"), (-1, "R")):
        for k in range(5):
            z = 0.085 + k * 0.02
            y = -0.088 + k * 0.016
            la = tube(f"{name}_lace{s}{k}", [(sx * 0.1 - 0.022, y + 0.004, z - 0.004), (sx * 0.1, y - 0.006, z + 0.004),
                                              (sx * 0.1 + 0.022, y + 0.004, z - 0.004)], 0.0022, 5, lace_m)
            rig.attach(la, f"shin.{s}" if k > 2 else f"foot.{s}")
            parts.append(la)
    if pal.get("satchel"):
        sm = m_leather("strap_" + name, "#6A4428")
        strap = tube(name + "_strap", [(-0.17, -0.02, 1.0), (-0.135, -0.105, 1.15), (0.02, -0.13, 1.29),
                                       (0.15, -0.075, 1.385), (0.14, 0.07, 1.375), (-0.04, 0.115, 1.21),
                                       (-0.17, 0.045, 1.0)], 0.0075, 6, sm)
        rig.attach(strap, "chest")
        parts.append(strap)
    for ob in parts:
        ob["mask"] = 1.0
        fix_texspace(ob)
    rig.ob.location = loc
    rig.ob.rotation_euler = (0, 0, rot_z)
    rig.ob.scale = (scale,) * 3
    frames = {}
    for sx, s in ((1, "L"), (-1, "R")):
        A, F, N = SK.hand_frame(sx)
        frames[s] = (Vector(A), Vector(F), Vector(N))
    return Human(name, rig, face, parts, pal, frames)


# ------------------------------------------------------------------ animation
class Human:
    def __init__(self, name, rig, face, parts, pal, hand_frames):
        self.name, self.rig, self.face, self.parts, self.pal = name, rig, face, parts, pal
        self.hand_frames = hand_frames
        self.rest = {b.name: b.matrix_local.to_quaternion() for b in rig.ob.data.bones}

    def pose(self, rots, loc=None):
        """rots: {bone: (x, y, z) degrees about rest armature axes}. Unlisted bones return to rest."""
        for pb in self.rig.ob.pose.bones:
            pb.rotation_mode = "QUATERNION"
            r = rots.get(pb.name)
            if r is None:
                pb.rotation_quaternion = Quaternion()
                continue
            if r[0] == "curl":
                A, F, N = self.hand_frames[pb.name[-1]]
                q = Quaternion(A.cross(N).normalized(), math.radians(r[1]))
            else:
                q = Euler([math.radians(a) for a in r], "XYZ").to_quaternion()
            R = self.rest[pb.name]
            pb.rotation_quaternion = R.inverted() @ q @ R
        pel = self.rig.ob.pose.bones["pelvis"]
        if loc is not None:
            R = self.rest["pelvis"].to_matrix()
            pel.location = R.inverted() @ Vector(loc)
        else:
            pel.location = (0, 0, 0)

    def hide(self, hidden=True):
        for ob in self.parts + [self.rig.ob]:
            ob.hide_render = hidden
            ob.hide_viewport = hidden


def _lerp(a, b, t):
    return a + (b - a) * t


def _sm(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


RELAX_ARMS = {"upperarm.L": (0, 6, 4), "upperarm.R": (0, -6, -4), "forearm.L": (-14, 0, 0), "forearm.R": (-14, 0, 0)}


def fingers(rots, s, curl=0.2, thumb=0.2, point=False):
    for f in ("index", "middle", "ring", "pinky"):
        c = curl if not (point and f == "index") else 0.0
        if point and f != "index":
            c = 1.0
        rots[f"{f}1.{s}"] = ("curl", 70 * c)
        rots[f"{f}2.{s}"] = ("curl", 85 * c)
    rots[f"thumb1.{s}"] = ("curl", 15 * thumb)
    rots[f"thumb2.{s}"] = ("curl", 35 * thumb)


def motion(kind, t, seed=0, **kw):
    """Procedural motion library. Returns (bone rotations, pelvis offset, face params)."""
    ph = seed * 1.7
    br = math.sin(t * 2 * math.pi / 3.6 + ph)                  # breathing
    sway = math.sin(t * 2 * math.pi / 5.3 + ph)
    r = {"spine": (1.5 * br, 0, 1.2 * sway), "chest": (1.2 * br, 0, 0), "neck": (0, 0, 0),
         "head": (2 * math.sin(t * 0.9 + ph), 0, 4 * math.sin(t * 0.43 + ph))}
    for k, v in RELAX_ARMS.items():
        r[k] = v
    fingers(r, "L", 0.25, 0.3)
    fingers(r, "R", 0.25, 0.3)
    loc = (0.004 * sway, 0, 0.002 * br)
    face = dict(blink=_blink(t, seed), brow_up=0.0, look=(0, -1, 0), squint=0.0, worried=0.0)
    if kind == "wave":
        u = _sm(min(t / 0.6, 1.0))
        w = math.sin(t * 2 * math.pi * 1.6)
        r["upperarm.R"] = (_lerp(0, -20, u), _lerp(-6, 150, u), _lerp(-4, 10, u))
        r["forearm.R"] = (_lerp(-14, -25, u), 0, _lerp(0, -35 + 22 * w, u))
        r["hand.R"] = (0, 0, 10 * w * u)
        fingers(r, "R", 0.05, 0.1)
        r["head"] = (4, 0, -8)
        face.update(brow_up=0.6, squint=0.3)
    elif kind == "point":
        tgt = kw.get("side", 1)
        u = _sm(min(t / 0.7, 1.0))
        s, sg = ("R", -1) if tgt > 0 else ("L", 1)
        r[f"upperarm.{s}"] = (_lerp(0, -70, u), _lerp(0, sg * 30, u), _lerp(0, sg * -15, u))
        r[f"forearm.{s}"] = (_lerp(-14, -10, u), 0, 0)
        fingers(r, s, point=True)
        r["head"] = (0, 0, -tgt * 18 * u)
        r["chest"] = (0, 0, -tgt * 6 * u)
        face.update(brow_up=0.5 * u, look=(-tgt * 0.3, -1, 0))
    elif kind == "look_up":
        u = _sm(min(t / 1.0, 1.0))
        r["head"] = (_lerp(0, 28, u) + r["head"][0], 0, r["head"][2])
        r["neck"] = (_lerp(0, 10, u), 0, 0)
        r["chest"] = (_lerp(0, 4, u), 0, 0)
        face.update(brow_up=0.8 * u, look=(0, -1, 0.35 * u))
        if kw.get("awe"):
            r["upperarm.L"] = (-10, 8, 4)
            r["forearm.L"] = (-60, 0, 0)
    elif kind == "binoculars":
        u = _sm(min(t / 0.8, 1.0))
        for s, sg in (("L", 1), ("R", -1)):
            r[f"upperarm.{s}"] = (_lerp(0, -58, u), _lerp(0, sg * 18, u), _lerp(0, sg * -28, u))
            r[f"forearm.{s}"] = (_lerp(-14, -118, u), 0, _lerp(0, sg * 22, u))
            fingers(r, s, 0.55, 0.5)
        r["head"] = (_lerp(0, 8, u), 0, 2 * math.sin(t * 0.5))
    elif kind == "camera":
        u = _sm(min(t / 0.8, 1.0))
        for s, sg in (("L", 1), ("R", -1)):
            r[f"upperarm.{s}"] = (_lerp(0, -45, u), _lerp(0, sg * 14, u), _lerp(0, sg * -30, u))
            r[f"forearm.{s}"] = (_lerp(-14, -115, u), 0, _lerp(0, sg * 25, u))
            fingers(r, s, 0.5, 0.4)
        r["head"] = (_lerp(0, -4, u), 0, 0)
        r["chest"] = (_lerp(0, -6, u), 0, 0)
    elif kind == "worried":
        u = _sm(min(t / 0.8, 1.0))
        for s, sg in (("L", 1), ("R", -1)):
            r[f"upperarm.{s}"] = (_lerp(0, -28, u), _lerp(0, sg * -4, u), _lerp(0, sg * -22, u))
            r[f"forearm.{s}"] = (_lerp(-14, -80, u), 0, _lerp(0, sg * 30, u))
            fingers(r, s, 0.45, 0.4)
        r["head"] = (-6 * u, 0, 6 * math.sin(t * 0.8))
        face.update(worried=u, brow_up=0.3 * u, look=(0, -1, -0.1))
    elif kind == "shrug":
        cyc = _sm(min((t % 3.0) / 0.6, 1.0)) * (1 - _sm(max(0, (t % 3.0) - 1.4) / 0.6))
        for s, sg in (("L", 1), ("R", -1)):
            r[f"shoulder.{s}"] = (0, 0, sg * 10 * cyc)
            r[f"upperarm.{s}"] = (-10 * cyc, sg * 25 * cyc, sg * -10 * cyc)
            r[f"forearm.{s}"] = (-14 - 70 * cyc, 0, sg * -50 * cyc)
            fingers(r, s, 0.1, 0.1)
        face.update(brow_up=0.9 * cyc)
    elif kind == "talk":
        g = math.sin(t * 2 * math.pi * 0.7 + ph)
        r["upperarm.R"] = (-25, -10, -8 + 5 * g)
        r["forearm.R"] = (-70 + 15 * g, 0, -25)
        fingers(r, "R", 0.15, 0.2)
        r["head"] = (3 * math.sin(t * 3.1), 0, 6 * math.sin(t * 0.9))
        face.update(brow_up=0.3 + 0.3 * max(0, g))
    elif kind == "walk":
        sp = kw.get("speed", 1.0)
        c = t * 2 * math.pi * 0.95 * sp
        s1, c2 = math.sin(c), math.cos(c)
        for s, sg in (("L", 1), ("R", -1)):
            ph2 = 0 if s == "L" else math.pi
            sl = math.sin(c + ph2)
            kn = max(0.0, math.sin(c + ph2 + 1.4))
            r[f"thigh.{s}"] = (28 * sl, 0, 0)
            r[f"shin.{s}"] = (50 * kn, 0, 0)
            r[f"foot.{s}"] = (12 * max(0, -sl) - 10 * kn * 0.5, 0, 0)
            r[f"upperarm.{s}"] = (-22 * sl, RELAX_ARMS[f"upperarm.{s}"][1], RELAX_ARMS[f"upperarm.{s}"][2])
            r[f"forearm.{s}"] = (-18 - 12 * max(0, -sl), 0, 0)
        r["pelvis"] = (0, 0, 5 * s1)
        r["chest"] = (2, 0, -6 * s1)
        loc = (0.012 * s1, 0, 0.022 * abs(c2) - 0.012)
    elif kind == "kneel":
        u = _sm(min(t / 1.0, 1.0))
        r["thigh.L"] = (_lerp(0, -85, u), 0, 0)
        r["shin.L"] = (_lerp(0, 90, u), 0, 0)
        r["thigh.R"] = (_lerp(0, 10, u), 0, 0)
        r["shin.R"] = (_lerp(0, 100, u), 0, 0)
        r["foot.R"] = (_lerp(0, -40, u), 0, 0)
        r["chest"] = (_lerp(0, -12, u), 0, 0)
        loc = (0, 0, _lerp(0, -0.36, u))
    return r, loc, face


def _blink(t, seed):
    period = 3.3 + (seed % 3) * 0.7
    x = (t + seed * 0.37) % period
    return max(0.0, 1.0 - abs(x - 0.12) / 0.07) if x < 0.25 else 0.0


def animate(h, kind, t, seed=0, **kw):
    rots, loc, face = motion(kind, t, seed, **kw)
    h.pose(rots, loc)
    h.face.set(**face)
