"""Episode 3 3D asset library (Blender 4.0, run inside Blender).

Stable asset IDs (see 05_Style_Bible): CHR_PIP, CHR_VILLAGER, CRE_VULTURE, CRE_DOG, CRE_CROW,
OBJ_COW, OBJ_BONES, OBJ_VIAL, OBJ_TREE_{NEEM,ACACIA,DEAD}, OBJ_HOUSE, OBJ_TOWER, ENV ground/sky.
All geometry is procedural so every shot rebuilds identical assets from these functions.
Units: 1 BU ~ "toy metre"; Pip is 2.2 BU tall.
"""
import math
import random

import bpy
from mathutils import Euler, Matrix, Quaternion, Vector

MB_K = 1.0 / 0.574          # metaball nominal radius -> visible radius (threshold 0.6, stiffness 2)


# ------------------------------------------------------------------ utils
def hex_lin(h):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c)


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    random.seed(7)
    _TUFT.clear()


def link(ob, coll=None):
    (coll or bpy.context.scene.collection).objects.link(ob)
    return ob


def smooth(ob):
    for p in ob.data.polygons:
        p.use_smooth = True
    return ob


def mat(name, color, rough=0.75, sss=0.0, emit=0.0, noise=None, noise_scale=8.0, spec=0.25, alpha=1.0):
    """Matte principled material. noise=(hex2, amount) mixes a second colour by a noise texture."""
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Roughness"].default_value = rough
    try:
        b.inputs["Specular IOR Level"].default_value = spec
    except KeyError:
        pass
    if sss:
        b.inputs["Subsurface Weight"].default_value = sss
        b.inputs["Subsurface Radius"].default_value = (0.3, 0.15, 0.1)
        b.inputs["Subsurface Scale"].default_value = 0.05
    if emit:
        b.inputs["Emission Color"].default_value = (*hex_lin(color), 1)
        b.inputs["Emission Strength"].default_value = emit
    if noise:
        tex = nt.nodes.new("ShaderNodeTexNoise")
        tex.inputs["Scale"].default_value = noise_scale
        tex.inputs["Detail"].default_value = 4
        ramp = nt.nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].position = 0.5 - noise[1] / 2
        ramp.color_ramp.elements[1].position = 0.5 + noise[1] / 2
        ramp.color_ramp.elements[0].color = (*hex_lin(color), 1)
        ramp.color_ramp.elements[1].color = (*hex_lin(noise[0]), 1)
        nt.links.new(tex.outputs["Fac"], ramp.inputs["Fac"])
        nt.links.new(ramp.outputs["Color"], b.inputs["Base Color"])
    else:
        b.inputs["Base Color"].default_value = (*hex_lin(color), 1)
    if alpha < 1:
        b.inputs["Alpha"].default_value = alpha
        m.blend_method = "BLEND"
    add_mask_aov(m)
    return m


def add_mask_aov(m):
    """Every material writes AOV 'mask' = the object's custom property 'mask' (1 = animated character)."""
    nt = m.node_tree
    if any(n.type == "OUTPUT_AOV" for n in nt.nodes):
        return
    at = nt.nodes.new("ShaderNodeAttribute")
    at.attribute_type = "OBJECT"
    at.attribute_name = "mask"
    ao = nt.nodes.new("ShaderNodeOutputAOV")
    ao.name = "mask"
    nt.links.new(at.outputs["Fac"], ao.inputs["Value"])


def setmat(ob, m):
    ob.data.materials.clear()
    ob.data.materials.append(m)
    return ob


def prim(kind, name, loc=(0, 0, 0), scale=(1, 1, 1), rot=(0, 0, 0), m=None, seg=24, **kw):
    if kind == "sphere":
        bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=seg // 2, radius=1, location=loc)
    elif kind == "ico":
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=kw.get("subdiv", 2), radius=1, location=loc)
    elif kind == "cyl":
        bpy.ops.mesh.primitive_cylinder_add(vertices=seg, radius=1, depth=1, location=loc)
    elif kind == "cone":
        bpy.ops.mesh.primitive_cone_add(vertices=seg, radius1=1, radius2=kw.get("r2", 0), depth=1, location=loc)
    elif kind == "cube":
        bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    elif kind == "torus":
        bpy.ops.mesh.primitive_torus_add(major_radius=1, minor_radius=kw.get("minor", 0.1),
                                         major_segments=seg, minor_segments=12, location=loc)
    elif kind == "plane":
        bpy.ops.mesh.primitive_plane_add(size=1, location=loc)
    ob = bpy.context.object
    ob.name = name
    ob.scale = scale
    ob.rotation_euler = rot
    if kind in ("sphere", "ico", "torus") or kw.get("smooth"):
        smooth(ob)
    if m:
        setmat(ob, m)
    return ob


def meta(name, elems, m, res=0.035):
    """elems: dicts(co, r [visible], type BALL/ELLIPSOID/CAPSULE, size (sx,sy,sz) as visible semi-axes, rot quat)."""
    mb = bpy.data.metaballs.new(name + "_mb")
    mb.resolution = res
    mb.render_resolution = res
    mb.threshold = 0.6
    for e in elems:
        el = mb.elements.new()
        el.type = e.get("type", "BALL")
        el.co = e["co"]
        el.stiffness = 2.0
        if el.type == "BALL":
            el.radius = e["r"] * MB_K
        else:
            sx, sy, sz = e["size"]
            r = min(sx, sy, sz)
            el.radius = r * MB_K
            if el.type == "ELLIPSOID":
                el.size_x, el.size_y, el.size_z = sx / r, sy / r, sz / r
            else:  # CAPSULE: size_x = absolute half-length of the core segment (BU)
                el.size_x = max(sx - r, 0.0)
        if "rot" in e:
            el.rotation = e["rot"]
    tmp = link(bpy.data.objects.new(name + "_tmp", mb))
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(tmp.evaluated_get(dg))
    bpy.data.objects.remove(tmp)
    bpy.data.metaballs.remove(mb)
    ob = link(bpy.data.objects.new(name, me))
    smooth(ob)
    setmat(ob, m)
    return ob


def seg_capsule(a, b, r):
    """Capsule element between points a and b (visible radius r)."""
    a, b = Vector(a), Vector(b)
    d = b - a
    q = Vector((1, 0, 0)).rotation_difference(d.normalized())
    return dict(type="CAPSULE", co=tuple((a + b) / 2), size=(d.length / 2 + r, r, r), rot=q)


def group(name, parts, loc=(0, 0, 0), rot=(0, 0, 0), scale=1.0):
    """Parent parts to an empty so the asset can be placed as one unit."""
    root = link(bpy.data.objects.new(name, None))
    for p in parts:
        p.parent = root
    root.location = loc
    root.rotation_euler = rot
    root.scale = (scale, scale, scale)
    return root


def poly_mesh(name, pts2d, thick, m, plane="XY"):
    """Flat extruded polygon (e.g. a wing) from 2D outline points."""
    import bmesh
    bm = bmesh.new()
    vs = [bm.verts.new((x, y, 0)) for x, y in pts2d]
    f = bm.faces.new(vs)
    bmesh.ops.triangulate(bm, faces=[f])
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = link(bpy.data.objects.new(name, me))
    sol = ob.modifiers.new("sol", "SOLIDIFY")
    sol.thickness = thick
    sol.offset = 0
    setmat(ob, m)
    return ob


# ------------------------------------------------------------------ palette (house style + episode)
def P():
    return dict(
        pip_head=mat("pip_head", "#F6F0E2", 0.55, sss=0.15),
        pip_hat=mat("pip_hat", "#F2B33D", 0.8, noise=("#E3A42F", 0.4), noise_scale=30),
        pip_band=mat("pip_band", "#C98A1E", 0.7),
        pip_vest=mat("pip_vest", "#6E8B3D", 0.85, noise=("#62803A", 0.3), noise_scale=25),
        pip_dark=mat("pip_dark", "#2B2420", 0.6),
        pip_boot=mat("pip_boot", "#5A3B22", 0.6),
        pip_glass=mat("pip_glass", "#3B2A1E", 0.35, spec=0.6),
        black=mat("black_gloss", "#0C0B0A", 0.25, spec=0.6),
        v_body=mat("v_body", "#A8875F", 0.9, noise=("#C2A47B", 0.6), noise_scale=14),
        v_wing=mat("v_wing", "#3A2D24", 0.85, noise=("#4A3A2E", 0.5), noise_scale=20),
        v_cov=mat("v_cov", "#B89B72", 0.9, noise=("#9C7F58", 0.5), noise_scale=18),
        v_ruff=mat("v_ruff", "#EAE1CF", 0.95, noise=("#D8CDB8", 0.5), noise_scale=30),
        v_skin=mat("v_skin", "#6E6763", 0.6, sss=0.1, noise=("#7E726B", 0.4), noise_scale=12),
        v_beak=mat("v_beak", "#57504A", 0.4),
        v_leg=mat("v_leg", "#8A8580", 0.6),
        dog=mat("dog", "#C79B62", 0.85, noise=("#D9B27E", 0.5), noise_scale=10),
        dog_dark=mat("dog_dark", "#8A6239", 0.85),
        crow=mat("crow", "#1C1B1E", 0.5, spec=0.5),
        crow_grey=mat("crow_grey", "#5D5A5C", 0.6),
        cow=mat("cow", "#B9B2A6", 0.85, noise=("#9E968A", 0.7), noise_scale=4),
        cow_dark=mat("cow_dark", "#8F877D", 0.8),
        horn=mat("horn", "#4A4038", 0.5),
        bone=mat("bone", "#E6DCC4", 0.7, noise=("#CDBF9F", 0.5), noise_scale=20),
        bark=mat("bark", "#5B4632", 0.95, noise=("#4A3828", 0.6), noise_scale=12),
        dead_bark=mat("dead_bark", "#8C8478", 0.95, noise=("#6E675D", 0.6), noise_scale=10),
        neem=mat("neem", "#4F7432", 0.85, noise=("#6B8F3E", 0.6), noise_scale=5),
        acacia=mat("acacia", "#6F7F38", 0.85, noise=("#8A9545", 0.6), noise_scale=5),
        grass=mat("grass", "#B7A060", 0.9, noise=("#9C8E4E", 0.6), noise_scale=3),
        grass_green=mat("grass_green", "#7E9446", 0.9),
        rock=mat("rock", "#8F8679", 0.9, noise=("#756C61", 0.6), noise_scale=6),
        stone=mat("stone", "#B7AA94", 0.95, noise=("#9C8F79", 0.6), noise_scale=4),
        glass_vial=mat("glass_vial", "#D8E6EC", 0.08, spec=0.9),
        label=mat("label", "#F3EEDF", 0.8),
        label_red=mat("label_red", "#E0533A", 0.6),
        wood=mat("wood", "#8B6240", 0.75, noise=("#77522F", 0.6), noise_scale=4),
        mirror=mat("mirror", "#C9D6DE", 0.12, spec=1.0),
        lamp=mat("lamp", "#FFC56B", 0.5, emit=6.0),
    )


# ------------------------------------------------------------------ characters
def pip(M, loc=(0, 0, 0), rot_z=0.0, pose="stand", look=(0, 0)):
    """CHR_PIP. pose: stand | binoculars | point | look_up. look=(yaw, pitch) of head in radians."""
    parts = []
    head_c = Vector((0, 0, 1.75))
    head = prim("sphere", "pip_head", head_c, (0.55, 0.55, 0.55), m=M["pip_head"], seg=40)
    parts.append(head)
    hd = []  # parts that follow the head
    for sx in (-1, 1):
        hd.append(prim("sphere", "pip_eye", (sx * 0.17, -0.5, 1.83), (0.05, 0.03, 0.06), m=M["black"]))
        ring = prim("torus", "pip_glass", (sx * 0.17, -0.53, 1.83), (0.13, 0.13, 0.13),
                    rot=(math.pi / 2, 0, 0), m=M["pip_glass"], minor=0.09)
        hd.append(ring)
    hd.append(prim("cyl", "pip_bridge", (0, -0.55, 1.85), (0.012, 0.012, 0.1), rot=(0, math.pi / 2, 0), m=M["pip_glass"]))
    hd.append(prim("sphere", "pip_mouth", (0, -0.535, 1.6), (0.085, 0.02, 0.022), m=M["pip_dark"]))
    if pose == "binoculars":
        for sx in (-1, 1):
            hd.append(prim("cyl", "pip_bino", (sx * 0.13, -0.72, 1.83), (0.09, 0.09, 0.3),
                           rot=(math.pi / 2, 0, 0), m=M["pip_dark"]))
    crown = prim("cyl", "pip_hatcrown", (0, 0, 2.2), (0.5, 0.5, 0.32), m=M["pip_hat"], seg=40)
    bev = crown.modifiers.new("bev", "BEVEL")
    bev.width = 0.12
    bev.segments = 4
    smooth(crown)
    brim = prim("cone", "pip_brim", (0, 0, 2.05), (0.78, 0.78, 0.12), m=M["pip_hat"], seg=48, r2=0.62)
    band = prim("cyl", "pip_band", (0, 0, 2.08), (0.515, 0.515, 0.07), m=M["pip_band"], seg=40)
    hd += [crown, brim, band]
    # head rotation pivot
    hp = link(bpy.data.objects.new("pip_headpivot", None))
    hp.location = head_c
    for p in [head] + hd:
        p.parent = hp
        p.location = p.location - head_c
    hp.rotation_euler = (look[1], 0, look[0])
    parts = [hp]
    body = prim("sphere", "pip_body", (0, 0, 0.95), (0.33, 0.3, 0.5), m=M["pip_dark"])
    vest = prim("sphere", "pip_vest", (0, 0, 0.98), (0.37, 0.34, 0.45), m=M["pip_vest"])
    pocket = prim("cube", "pip_pocket", (0.14, -0.33, 1.08), (0.14, 0.04, 0.12), m=M["pip_vest"])
    parts += [body, vest, pocket]
    for sx in (-1, 1):
        parts.append(prim("cyl", "pip_leg", (sx * 0.14, 0, 0.32), (0.07, 0.07, 0.55), m=M["pip_dark"]))
        parts.append(prim("sphere", "pip_boot", (sx * 0.15, -0.08, 0.06), (0.14, 0.2, 0.08), m=M["pip_boot"]))
    # arms: shoulder pivots; pose angles (x = forward raise, y = sideways)
    poses = {"stand": [(0.15, 0.25), (0.15, -0.25)], "binoculars": [(1.75, 0.55), (1.75, -0.55)],
             "point": [(0.15, 0.25), (1.6, -0.2)], "look_up": [(0.3, 0.35), (0.3, -0.35)],
             "wave": [(0.15, 0.25), (2.7, -0.5)]}
    for sx, (fx, fy) in zip((-1, 1), poses.get(pose, poses["stand"])):
        sh = link(bpy.data.objects.new("pip_shoulder", None))
        sh.location = (sx * 0.36, 0, 1.3)
        arm = prim("cyl", "pip_arm", (0, 0, -0.32), (0.06, 0.06, 0.62), m=M["pip_dark"])
        hand = prim("sphere", "pip_hand", (0, 0, -0.66), (0.11, 0.11, 0.11), m=M["pip_head"])
        arm.parent = sh
        hand.parent = sh
        sh.rotation_euler = (-fx, 0, 0)
        sh.rotation_euler.rotate_axis("Y", fy * sx * -1 if False else fy)
        parts.append(sh)
    return group("CHR_PIP", parts, loc, (0, 0, rot_z))


def villager(M, loc, rot_z=0.0, skin="#C68B5E", cloth="#3F6EA8", hair="#1E1A18", scarf=None, scale=1.0):
    """CHR_VILLAGER: Pip's body language with varied skin tones and clothes (house style B.3)."""
    sk = mat("skin_" + skin, skin, 0.6, sss=0.12)
    cl = mat("cloth_" + cloth, cloth, 0.9, noise=(cloth, 0.2), noise_scale=20)
    hr = mat("hair_" + hair, hair, 0.7)
    parts = [prim("sphere", "v_head", (0, 0, 1.75), (0.52, 0.52, 0.52), m=sk, seg=32),
             prim("sphere", "v_hair", (0, 0.06, 1.92), (0.5, 0.5, 0.42), m=hr, seg=32),
             prim("sphere", "v_body", (0, 0, 0.9), (0.36, 0.32, 0.62), m=cl)]
    for sx in (-1, 1):
        parts.append(prim("sphere", "v_eye", (sx * 0.16, -0.47, 1.8), (0.045, 0.03, 0.055), m=M["black"]))
        parts.append(prim("cyl", "v_leg", (sx * 0.13, 0, 0.25), (0.07, 0.07, 0.5), m=M["pip_dark"]))
        parts.append(prim("cyl", "v_arm", (sx * 0.4, 0, 1.0), (0.06, 0.06, 0.6), rot=(0, sx * 0.25, 0), m=cl))
    if scarf:
        parts.append(prim("torus", "v_scarf", (0, 0, 1.33), (0.33, 0.33, 0.6), m=mat("scarf" + scarf, scarf, 0.9),
                          minor=0.35))
    return group("CHR_VILLAGER", parts, loc, (0, 0, rot_z), scale)


# ------------------------------------------------------------------ creatures
def vulture(M, loc=(0, 0, 0), rot_z=0.0, pose="stand", scale=1.0, bank=0.0):
    """CRE_VULTURE (Gyps-type, Indian vulture palette). Forward = +X.
    pose: stand | feed | spread | soar | fallen | perch"""
    parts = []
    soar = pose == "soar"
    if soar:
        body_c, neck_a, head_c = Vector((0, 0, 0)), Vector((0.42, 0, 0.05)), Vector((0.62, 0, 0.04))
        body = meta("v_body", [dict(type="ELLIPSOID", co=(0, 0, 0), size=(0.5, 0.26, 0.24)),
                               dict(type="ELLIPSOID", co=(-0.48, 0, 0.0), size=(0.28, 0.2, 0.06))], M["v_body"])
    else:
        tilt = {"feed": 0.55, "spread": 0.15, "fallen": -0.05, "perch": 0.35}.get(pose, 0.3)
        body_c = Vector((0, 0, 0.52 if pose != "fallen" else 0.24))
        q = Quaternion((0, 1, 0), tilt)
        tail = body_c + q @ Vector((-0.55, 0, -0.02))
        body = meta("v_body", [dict(type="ELLIPSOID", co=tuple(body_c), size=(0.46, 0.25, 0.3), rot=q),
                               dict(type="ELLIPSOID", co=tuple(tail), size=(0.26, 0.17, 0.06), rot=q)], M["v_body"])
        if pose == "feed":
            neck_a, head_c = Vector((0.4, 0, 0.6)), Vector((0.8, 0, 0.22))
        elif pose == "fallen":
            neck_a, head_c = Vector((0.36, 0, 0.3)), Vector((0.9, 0.22, 0.1))
        else:
            neck_a, head_c = Vector((0.33, 0, 0.74)), Vector((0.5, 0, 1.04))
    parts.append(body)
    # ruff collar at neck base
    ruff = []
    for k in range(10):
        a = 2 * math.pi * k / 10
        ruff.append(dict(co=tuple(neck_a + Vector((-0.04, 0.13 * math.cos(a), 0.11 * math.sin(a)))), r=0.085))
    parts.append(meta("v_ruff", ruff, M["v_ruff"], res=0.03))
    # neck + head (bare skin)
    mid = (neck_a + head_c) / 2 + Vector((0.04, 0, 0.05 if pose not in ("feed",) else 0.08))
    parts.append(meta("v_neck", [seg_capsule(neck_a, mid, 0.07), seg_capsule(mid, head_c, 0.065),
                                 dict(co=tuple(head_c), r=0.1),
                                 dict(type="ELLIPSOID", co=tuple(head_c + Vector((0.07, 0, -0.01))), size=(0.1, 0.075, 0.07))],
                      M["v_skin"], res=0.025))
    fwd = (head_c - mid).normalized()
    if pose == "feed":
        fwd = Vector((0.6, 0, -0.8)).normalized()
    elif soar:
        fwd = Vector((1, 0, -0.1)).normalized()
    else:
        fwd = Vector((1, 0, -0.15)).normalized()
    bq = Vector((0, 0, 1)).rotation_difference(fwd)
    beak = prim("cone", "v_beak", tuple(head_c + fwd * 0.2), (0.055, 0.055, 0.2), m=M["v_beak"], seg=16)
    beak.rotation_mode = "QUATERNION"
    beak.rotation_quaternion = bq
    parts.append(beak)
    eye_open = pose != "fallen"
    side = Vector((0, 0, 1)).cross(fwd).normalized()
    for s in (-1, 1):
        e = prim("sphere", "v_eye", tuple(head_c + fwd * 0.06 + side * s * 0.075 + Vector((0, 0, 0.035))),
                 (0.022, 0.022, 0.022 if eye_open else 0.004), m=M["black"], seg=12)
        parts.append(e)
    # wings
    if pose in ("spread", "soar", "fallen"):
        span = 1.55
        outline = [(0.16, 0.18), (0.3, 0.55), (0.3, 1.0), (0.2, 1.3), (0.12, span + 0.05),
                   (0.06, span - 0.12), (0.01, span + 0.02), (-0.04, span - 0.18), (-0.09, span - 0.02),
                   (-0.13, span - 0.24), (-0.19, span - 0.1), (-0.21, span - 0.3), (-0.29, span - 0.22),
                   (-0.3, span - 0.4), (-0.38, 1.0), (-0.36, 0.6), (-0.4, 0.35), (-0.3, 0.18)]
        cov = [(0.2, 0.18), (0.32, 0.6), (0.3, 1.05), (0.22, 1.32), (0.08, 1.25), (0.02, 0.9), (0.0, 0.5), (-0.05, 0.18)]
        dihedral = 0.12 if soar else (-0.04 if pose == "fallen" else 0.35)
        for s in (-1, 1):
            pts = [(x, y * s) for x, y in outline]
            cpts = [(x, y * s) for x, y in cov]
            if s < 0:
                pts, cpts = pts[::-1], cpts[::-1]
            w = poly_mesh("v_wing", pts, 0.035, M["v_wing"])
            c = poly_mesh("v_cov", cpts, 0.05, M["v_cov"])
            c.location.z += 0.02
            for ob in (w, c):
                ob.location = body_c + Vector((0, 0, (0.05 if soar else 0.15) if pose != "fallen" else -0.12)) + (Vector((0, 0, 0.025)) if ob is c else Vector())
                if pose == "fallen":
                    ob.scale = (1.0, 0.75, 1.0)
                ob.rotation_euler = (s * dihedral, 0, 0) if soar else (s * dihedral, -0.25, 0)
            parts += [w, c]
    elif pose != "fallen":
        q = Quaternion((0, 1, 0), {"feed": 0.55, "perch": 0.35}.get(pose, 0.3) - 0.1)
        for s in (-1, 1):
            parts.append(meta("v_wingf", [dict(type="ELLIPSOID", co=tuple(body_c + q @ Vector((-0.22, s * 0.2, 0.02))),
                                               size=(0.6, 0.055, 0.19), rot=q)], M["v_wing"]))
            parts.append(meta("v_covf", [dict(type="ELLIPSOID", co=tuple(body_c + q @ Vector((0.04, s * 0.215, 0.07))),
                                              size=(0.34, 0.06, 0.17), rot=q)], M["v_cov"]))
    # legs
    if not soar and pose != "fallen":
        for s in (-1, 1):
            top = body_c + Vector((0.02, s * 0.12, -0.25))
            parts.append(meta("v_leg", [seg_capsule(top, (0.05, s * 0.13, 0.08), 0.035),
                                        dict(type="ELLIPSOID", co=(0.1, s * 0.13, 0.03), size=(0.12, 0.06, 0.03))],
                              M["v_leg"], res=0.02))
    root = group("CRE_VULTURE", parts, loc, (0, 0, rot_z), scale)
    if soar:
        root.rotation_euler = (bank, 0, rot_z)
    return root


def dog(M, loc=(0, 0, 0), rot_z=0.0, pose="stand", scale=1.0):
    """CRE_DOG (Indian pariah type). Forward = +X. pose: stand | sniff | walk | sit."""
    head = {"sniff": Vector((0.62, 0, 0.32)), "sit": Vector((0.42, 0, 0.98))}.get(pose, Vector((0.6, 0, 0.82)))
    body_c = Vector((0, 0, 0.6)) if pose != "sit" else Vector((0.05, 0, 0.55))
    els = [dict(type="ELLIPSOID", co=tuple(body_c), size=(0.42, 0.17, 0.18),
                rot=Quaternion((0, 1, 0), -0.6 if pose == "sit" else 0.0)),
           seg_capsule(body_c + Vector((0.3, 0, 0.05)), head + Vector((-0.08, 0, -0.08)), 0.1),
           dict(co=tuple(head), r=0.15),
           seg_capsule(head, head + Vector((0.2, 0, -0.06)), 0.07)]
    legs = [(0.28, 0.1), (0.28, -0.1), (-0.3, 0.1), (-0.3, -0.1)]
    for i, (x, y) in enumerate(legs):
        sw = 0.12 * (1 if i in (0, 3) else -1) if pose == "walk" else 0
        if pose == "sit" and x < 0:
            els.append(dict(type="ELLIPSOID", co=(x + 0.1, y * 1.3, 0.15), size=(0.2, 0.08, 0.12)))
        else:
            els.append(seg_capsule((x, y, 0.55), (x + sw, y, 0.04), 0.05))
    parts = [meta("dog_body", els, M["dog"], res=0.03)]
    # tail curled up
    t0 = body_c + Vector((-0.4, 0, 0.08))
    parts.append(meta("dog_tail", [seg_capsule(t0, t0 + Vector((-0.12, 0, 0.2)), 0.045),
                                   seg_capsule(t0 + Vector((-0.12, 0, 0.2)), t0 + Vector((0.02, 0, 0.32)), 0.04)],
                      M["dog"], res=0.025))
    fwd = Vector((1, 0, -0.3 if pose != "sniff" else -0.9)).normalized()
    for s in (-1, 1):
        ear = prim("cone", "dog_ear", tuple(head + Vector((-0.05, s * 0.09, 0.14))), (0.06, 0.035, 0.13),
                   rot=(s * -0.25, -0.15, 0), m=M["dog_dark"], seg=12)
        eye = prim("sphere", "dog_eye", tuple(head + Vector((0.11, s * 0.075, 0.04))), (0.022, 0.022, 0.022),
                   m=M["black"], seg=12)
        parts += [ear, eye]
    parts.append(prim("sphere", "dog_nose", tuple(head + Vector((0.27, 0, -0.06)) if pose != "sniff"
                                                  else head + Vector((0.25, 0, -0.08))), (0.035, 0.035, 0.03),
                      m=M["black"], seg=12))
    return group("CRE_DOG", parts, loc, (0, 0, rot_z), scale)


def crow(M, loc, rot_z=0.0, scale=1.0, peck=False):
    """CRE_CROW (house crow). Forward = +X."""
    h = Vector((0.22, 0, 0.2)) if peck else Vector((0.2, 0, 0.42))
    parts = [meta("crow_body", [dict(type="ELLIPSOID", co=(0, 0, 0.3), size=(0.2, 0.1, 0.12),
                                     rot=Quaternion((0, 1, 0), 0.4 if peck else 0.25)),
                                dict(type="ELLIPSOID", co=(-0.2, 0, 0.24), size=(0.14, 0.06, 0.03)),
                                dict(co=tuple(h), r=0.085)], M["crow"], res=0.02),
             prim("sphere", "crow_nape", tuple(h + Vector((-0.04, 0, -0.02))), (0.08, 0.085, 0.08), m=M["crow_grey"]),
             prim("cone", "crow_beak", tuple(h + Vector((0.1, 0, -0.02))), (0.03, 0.03, 0.1),
                  rot=(0, math.pi / 2 + (0.6 if peck else 0.1), 0), m=M["crow"], seg=12)]
    for s in (-1, 1):
        parts.append(prim("sphere", "crow_eye", tuple(h + Vector((0.05, s * 0.06, 0.02))), (0.015,) * 3,
                          m=M["black"], seg=8))
        parts.append(prim("cyl", "crow_leg", (0.0, s * 0.04, 0.1), (0.012, 0.012, 0.2), m=M["crow"], seg=8))
    return group("CRE_CROW", parts, loc, (0, 0, rot_z), scale)


def cow(M, loc, rot_z=0.0, state="standing", scale=1.0):
    """OBJ_COW (zebu). state: standing | carcass | bloated. Forward = +X. Non-graphic by design."""
    if state == "standing":
        body = Vector((0, 0, 1.1))
        els = [dict(type="ELLIPSOID", co=tuple(body), size=(0.95, 0.4, 0.45)),
               dict(type="ELLIPSOID", co=(0.45, 0, 1.55), size=(0.25, 0.18, 0.25)),       # hump
               seg_capsule((0.75, 0, 1.25), (1.2, 0, 1.45), 0.2),                         # neck
               dict(type="ELLIPSOID", co=(1.35, 0, 1.35), size=(0.25, 0.18, 0.2)),
               seg_capsule((1.35, 0, 1.3), (1.6, 0, 1.15), 0.12),                          # muzzle
               dict(type="ELLIPSOID", co=(0.85, 0, 0.85), size=(0.15, 0.08, 0.3))]         # dewlap
        for x, y in [(0.6, 0.22), (0.6, -0.22), (-0.6, 0.22), (-0.6, -0.22)]:
            els.append(seg_capsule((x, y, 0.9), (x, y, 0.05), 0.09))
        parts = [meta("cow_body", els, M["cow"], res=0.04)]
        hc = Vector((1.35, 0, 1.4))
        up = True
    else:
        k = 1.12 if state == "bloated" else 1.0
        body = Vector((0, 0, 0.42 * k))
        els = [dict(type="ELLIPSOID", co=tuple(body), size=(0.95, 0.45 * k, 0.4 * k)),
               dict(type="ELLIPSOID", co=(0.45, -0.15, 0.62), size=(0.22, 0.25, 0.18)),
               seg_capsule((0.8, 0, 0.35), (1.25, 0.05, 0.25), 0.18),
               dict(type="ELLIPSOID", co=(1.4, 0.05, 0.2), size=(0.25, 0.17, 0.17)),
               seg_capsule((1.45, 0.05, 0.18), (1.7, 0.1, 0.12), 0.1)]
        for x in (0.6, -0.6):   # legs stiff, outward (lying on its side)
            els.append(seg_capsule((x, -0.2, 0.3), (x + 0.1, -0.95, 0.12), 0.08))
            els.append(seg_capsule((x + 0.12, -0.15, 0.35), (x + 0.25, -0.85, 0.2), 0.08))
        parts = [meta("cow_body", els, M["cow"], res=0.04)]
        hc = Vector((1.4, 0.05, 0.25))
        up = False
    hc_head = mat("cow_head", "#7C756C", 0.85)
    parts.append(prim("sphere", "cow_muzzle", tuple(hc + Vector((0.28, 0, -0.05))), (0.16, 0.14, 0.12), m=hc_head))
    for s in (-1, 1):
        if up:
            parts.append(prim("cone", "cow_horn", tuple(hc + Vector((-0.08, s * 0.14, 0.22))), (0.05, 0.05, 0.25),
                              rot=(s * -0.5, -0.3, 0), m=M["horn"], seg=12))
            parts.append(prim("sphere", "cow_ear", tuple(hc + Vector((-0.05, s * 0.24, 0.0))), (0.12, 0.05, 0.05),
                              rot=(0, 0, s * 0.3), m=M["cow_dark"]))
            parts.append(prim("sphere", "cow_eye", tuple(hc + Vector((0.12, s * 0.14, 0.06))), (0.03,) * 3, m=M["black"]))
        else:
            parts.append(prim("cone", "cow_horn", tuple(hc + Vector((-0.1, s * 0.12, 0.2 if s > 0 else 0.1))),
                              (0.05, 0.05, 0.22), rot=(s * -0.9, -0.5, 0), m=M["horn"], seg=12))
            parts.append(prim("sphere", "cow_eye", tuple(hc + Vector((0.12, 0.16, 0.06))), (0.03, 0.03, 0.005),
                              m=M["black"]))
    return group("OBJ_COW", parts, loc, (0, 0, rot_z), scale)


def bones(M, loc, rot_z=0.0, scale=1.0, n_extra=6, seed=3):
    """OBJ_BONES: stylized dry remains (ribs, skull, long bones). Non-graphic."""
    rnd = random.Random(seed)
    parts = []
    for i in range(7):   # ribs
        r = prim("torus", "rib", (-0.5 + i * 0.16, 0, 0.0), (0.42, 0.32, 0.42), rot=(0, math.pi / 2, 0),
                 m=M["bone"], minor=0.07, seg=24)
        r.rotation_euler = (math.pi / 2.2, math.pi / 2, 0)
        parts.append(r)
    parts.append(prim("cyl", "spine", (0.0, 0.0, 0.33), (0.05, 0.05, 1.3), rot=(0, math.pi / 2, 0), m=M["bone"]))
    sk = meta("skull", [dict(type="ELLIPSOID", co=(1.0, 0.2, 0.12), size=(0.28, 0.14, 0.13)),
                        dict(type="ELLIPSOID", co=(1.25, 0.25, 0.08), size=(0.16, 0.1, 0.08))], M["bone"])
    parts.append(sk)
    for i in range(n_extra):
        x, y = rnd.uniform(-1.6, 1.8), rnd.uniform(-1.4, 1.4)
        parts.append(prim("cyl", "longbone", (x, y, 0.04), (0.035, 0.035, rnd.uniform(0.35, 0.6)),
                          rot=(math.pi / 2, 0, rnd.uniform(0, math.pi)), m=M["bone"]))
    return group("OBJ_BONES", parts, loc, (0, 0, rot_z), scale)


# ------------------------------------------------------------------ environment
def tree(M, kind, loc, scale=1.0, seed=1):
    """OBJ_TREE_NEEM / OBJ_TREE_ACACIA / OBJ_TREE_DEAD. Returns (root, perch_points)."""
    rnd = random.Random(seed)
    parts, perches = [], []
    if kind == "dead":
        trunk = prim("cone", "trunk", (0, 0, 1.6), (0.22, 0.22, 3.2), m=M["dead_bark"], seg=12, r2=0.1)
        parts.append(trunk)
        for i, (ang, h, ln, up) in enumerate([(0.3, 2.2, 1.6, 0.5), (2.5, 2.6, 1.4, 0.6), (4.2, 2.9, 1.2, 0.4),
                                              (1.4, 3.0, 1.0, 0.8), (5.4, 1.8, 1.3, 0.3)]):
            d = Vector((math.cos(ang), math.sin(ang), up)).normalized()
            base = Vector((0, 0, h))
            mid = base + d * ln / 2
            b = prim("cone", "branch", tuple(mid), (0.08, 0.08, ln), m=M["dead_bark"], seg=8, r2=0.03)
            b.rotation_mode = "QUATERNION"
            b.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(d)
            parts.append(b)
            perches.append(tuple(base + d * ln * 0.75))
        perches.append((0, 0, 3.2))
    else:
        h = 2.6 if kind == "neem" else 2.4
        parts.append(prim("cone", "trunk", (0, 0, h / 2), (0.2, 0.2, h), m=M["bark"], seg=10, r2=0.12))
        if kind == "neem":
            for i in range(7):
                a = rnd.uniform(0, 2 * math.pi)
                r = rnd.uniform(0.3, 1.0)
                c = prim("ico", "canopy", (math.cos(a) * r, math.sin(a) * r, h + rnd.uniform(0.3, 1.1)),
                         (rnd.uniform(0.9, 1.3),) * 3, m=M["neem"], subdiv=3)
                d = c.modifiers.new("d", "DISPLACE")
                tex = bpy.data.textures.new("lumps", "CLOUDS")
                tex.noise_scale = 0.4
                d.texture = tex
                d.strength = 0.35
                parts.append(c)
        else:   # acacia: flat umbrella with forked branches
            for ang in (0.4, 2.4, 4.3):
                d = Vector((math.cos(ang) * 0.6, math.sin(ang) * 0.6, 1)).normalized()
                b = prim("cone", "branch", tuple(Vector((0, 0, h)) + d * 0.6), (0.08, 0.08, 1.2), m=M["bark"],
                         seg=8, r2=0.04)
                b.rotation_mode = "QUATERNION"
                b.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(d)
                parts.append(b)
            for i in range(5):
                a = rnd.uniform(0, 2 * math.pi)
                r = rnd.uniform(0.2, 1.4)
                c = prim("sphere", "canopy", (math.cos(a) * r, math.sin(a) * r, h + 1.0 + rnd.uniform(-0.1, 0.15)),
                         (rnd.uniform(1.4, 2.0), rnd.uniform(1.2, 1.7), 0.32), m=M["acacia"])
                d = c.modifiers.new("d", "DISPLACE")
                tex = bpy.data.textures.new("lumps", "CLOUDS")
                tex.noise_scale = 0.3
                d.texture = tex
                d.strength = 0.15
                parts.append(c)
            perches = [(1.4, 0.3, h + 1.35), (-1.2, 0.6, h + 1.3), (0.3, -1.3, h + 1.3)]
    root = group("OBJ_TREE_" + kind.upper(), parts, loc, (0, 0, rnd.uniform(0, 6.28)), scale)
    bpy.context.view_layer.update()
    perches = [tuple(root.matrix_world @ Vector(p)) for p in perches]
    return root, perches


def house(M, loc, rot_z=0.0, w=2.6, d=2.2, h=2.0, wall="#D9B98C", trim="#A65E3A", roof="flat", scale=1.0):
    """OBJ_HOUSE: simple village house with parapet roof or tile roof, door and windows."""
    wm = mat("wall_" + wall, wall, 0.95, noise=("#" + "".join(f"{max(0, int(wall[i:i + 2], 16) - 18):02x}"
                                                              for i in (1, 3, 5)), 0.6), noise_scale=3)
    tm = mat("trim_" + trim, trim, 0.9)
    dark = mat("doorway", "#2A211B", 0.9)
    parts = [prim("cube", "wall", (0, 0, h / 2), (w, d, h), m=wm)]
    if roof == "flat":
        parts.append(prim("cube", "parapet", (0, 0, h + 0.12), (w + 0.1, d + 0.1, 0.24), m=tm))
    else:
        r = prim("cube", "roof", (0, 0, h + 0.4), (w + 0.4, d * 0.78, 0.12), rot=(0.55, 0, 0), m=tm)
        r2 = prim("cube", "roof2", (0, 0, h + 0.4), (w + 0.4, d * 0.78, 0.12), rot=(-0.55, 0, 0), m=tm)
        r.location = (0, -d * 0.3, h + 0.35)
        r2.location = (0, d * 0.3, h + 0.35)
        parts += [r, r2]
    parts.append(prim("cube", "door", (0.3, -d / 2 - 0.01, 0.65), (0.55, 0.04, 1.3), m=dark))
    parts.append(prim("cube", "win", (-0.7, -d / 2 - 0.01, 1.25), (0.4, 0.04, 0.4), m=dark))
    return group("OBJ_HOUSE", parts, loc, (0, 0, rot_z), scale)


def ground(M, size=160, color="#C8AE7E", color2="#A98E5E", seed=0, hills=True):
    g = mat("ground_" + color, color, 0.95, noise=(color2, 0.7), noise_scale=0.08)
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=120, y_subdivisions=120, size=size)
    ob = bpy.context.object
    ob.name = "ENV_GROUND"
    d = ob.modifiers.new("d", "DISPLACE")
    tex = bpy.data.textures.new("terrain", "CLOUDS")
    tex.noise_scale = 6.0
    d.texture = tex
    d.strength = 0.6
    d.mid_level = 0.5
    smooth(ob)
    setmat(ob, g)
    return ob


def scatter(M, make, n, area, avoid=(), seed=0, zfix=0.0):
    rnd = random.Random(seed)
    out = []
    (x0, x1), (y0, y1) = area
    tries = 0
    while len(out) < n and tries < n * 20:
        tries += 1
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        if any((x - ax) ** 2 + (y - ay) ** 2 < ar ** 2 for ax, ay, ar in avoid):
            continue
        out.append(make((x, y, zfix), rnd))
    return out


_TUFT = {}


def tuft(M, loc, rnd, green=False):
    key = "green" if green else "dry"
    if key not in _TUFT:
        me = bpy.data.meshes.new("tuft_" + key)
        import bmesh
        bm = bmesh.new()
        r2 = random.Random(5)
        for i in range(9):
            a = r2.uniform(0, 6.28)
            lean = r2.uniform(0.1, 0.45)
            hgt = r2.uniform(0.25, 0.5)
            base = Vector((math.cos(a) * 0.05, math.sin(a) * 0.05, 0))
            top = base + Vector((math.cos(a) * lean * hgt, math.sin(a) * lean * hgt, hgt))
            side = Vector((-math.sin(a), math.cos(a), 0)) * 0.025
            v = [bm.verts.new(base - side), bm.verts.new(base + side), bm.verts.new(top)]
            bm.faces.new(v)
        bm.to_mesh(me)
        bm.free()
        _TUFT[key] = me
    ob = link(bpy.data.objects.new("tuft", _TUFT[key]))
    ob.data.materials.clear() if not ob.data.materials else None
    if not _TUFT[key].materials:
        _TUFT[key].materials.append(M["grass_green" if green else "grass"])
    ob.location = loc
    s = rnd.uniform(0.7, 1.4)
    ob.scale = (s, s, s * rnd.uniform(0.8, 1.3))
    ob.rotation_euler = (0, 0, rnd.uniform(0, 6.28))
    return ob


def rock(M, loc, rnd, s=None):
    s = s or rnd.uniform(0.15, 0.5)
    ob = prim("ico", "rock", loc, (s * rnd.uniform(1, 1.6), s, s * 0.6), m=M["rock"], subdiv=2)
    ob.rotation_euler = (0, 0, rnd.uniform(0, 6.28))
    return ob


def hill(M, loc, scale, color="#8C9A6A"):
    m = mat("hill_" + color, color, 0.95, noise=("#7A8A5C", 0.5), noise_scale=2)
    return prim("sphere", "hill", loc, scale, m=m, seg=48)


def tower(M, loc, scale=1.0, mirrors=False):
    """OBJ_TOWER (Tower of Silence, stylized): low circular stone wall on a rise. No remains depicted."""
    parts = [prim("cyl", "tower_wall", (0, 0, 1.6), (6.0, 6.0, 3.2), m=M["stone"], seg=64),
             prim("cyl", "tower_cap", (0, 0, 3.25), (6.15, 6.15, 0.15), m=M["stone"], seg=64),
             prim("cube", "tower_door", (0, -6.02, 0.9), (1.0, 0.1, 1.8), m=mat("doorway", "#2A211B", 0.9))]
    if mirrors:
        for i in range(3):
            a = -1.0 + i * 0.6
            fr = prim("cube", "mirror", (math.cos(a) * 4.0, math.sin(a) * 4.0, 4.2), (2.2, 0.08, 1.4),
                      rot=(0.7, 0, a + math.pi / 2), m=M["mirror"])
            st = prim("cyl", "mirror_post", (math.cos(a) * 4.0, math.sin(a) * 4.0, 3.6), (0.06, 0.06, 1.0),
                      m=M["dead_bark"])
            parts += [fr, st]
    return group("OBJ_TOWER", parts, loc, (0, 0, 0), scale)


def vial(M, loc, label="red", scale=1.0):
    """OBJ_VIAL: small injectable vial with label (generic, no brand)."""
    lab = M["label_red"] if label == "red" else mat("label_green", "#5C9E5B", 0.6)
    parts = [prim("cyl", "vial_glass", (0, 0, 0.5), (0.22, 0.22, 1.0), m=M["glass_vial"], seg=32),
             prim("cyl", "vial_label", (0, 0, 0.45), (0.225, 0.225, 0.5), m=M["label"], seg=32),
             prim("cyl", "vial_band", (0, 0, 0.6), (0.227, 0.227, 0.12), m=lab, seg=32),
             prim("cyl", "vial_cap", (0, 0, 1.08), (0.16, 0.16, 0.18), m=lab, seg=32),
             prim("cyl", "vial_neck", (0, 0, 0.98), (0.12, 0.12, 0.08), m=M["glass_vial"], seg=32)]
    return group("OBJ_VIAL", parts, loc, (0, 0, 0), scale)


# ------------------------------------------------------------------ render, camera, light presets
LIGHT = {
    #          sun elev, sun azim, sun color, energy, angle, sky horizon, sky zenith, strength, haze color
    "dawn": (8, 70, "#FFB07A", 3.2, 4, "#F4C49A", "#7E9CC4", 0.9, "#E9C3A0"),
    "morning": (22, 60, "#FFD9AE", 4.0, 3, "#D9E3EA", "#4F8CD0", 1.0, "#DCDCD4"),
    "day": (55, 30, "#FFF1DC", 4.5, 2, "#C8DDEC", "#3F7FC8", 1.1, "#D0DCE4"),
    "noon_hot": (70, 20, "#FFF4E0", 5.0, 2, "#DDE4E4", "#5B95D0", 1.2, "#E2DCCB"),
    "golden": (14, 250, "#FFB766", 3.6, 3, "#F6C78C", "#8AA7CF", 0.95, "#EFC28E"),
    "overcast": (40, 120, "#E6E8EA", 1.4, 25, "#C9CDCF", "#9AA4AC", 1.4, "#C4C8CA"),
    "dusk": (3, 255, "#FF8A5B", 1.6, 5, "#E99A7A", "#3E4F7A", 0.55, "#B98C8C"),
    "night": (35, 200, "#A9C0F0", 1.1, 3, "#3E4C72", "#18223E", 0.6, "#2E3956"),
    "monsoon": (45, 120, "#D8DDE2", 0.9, 30, "#9CA4AA", "#6E777F", 0.9, "#8F979D"),
}


def world(preset, clouds=0.35, stars=False):
    se, sa, sc, en, ang, hor, zen, st, haze = LIGHT[preset]
    w = bpy.data.worlds.new("ENV_SKY")
    bpy.context.scene.world = w
    w.use_nodes = True
    nt = w.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputWorld")
    bg = nt.nodes.new("ShaderNodeBackground")
    bg.inputs["Strength"].default_value = st
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Generated"], sep.inputs[0])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.0
    ramp.color_ramp.elements[0].color = (*hex_lin(hor), 1)
    ramp.color_ramp.elements[1].position = 0.32
    ramp.color_ramp.elements[1].color = (*hex_lin(zen), 1)
    nt.links.new(sep.outputs["Z"], ramp.inputs["Fac"])
    col = ramp.outputs["Color"]
    if clouds > 0:
        nz = nt.nodes.new("ShaderNodeTexNoise")
        nz.inputs["Scale"].default_value = 2.2
        nz.inputs["Detail"].default_value = 6
        nz.inputs["Roughness"].default_value = 0.6
        mp = nt.nodes.new("ShaderNodeMapping")
        mp.inputs["Scale"].default_value = (1.0, 1.0, 4.0)
        nt.links.new(tc.outputs["Generated"], mp.inputs["Vector"])
        nt.links.new(mp.outputs["Vector"], nz.inputs["Vector"])
        cr = nt.nodes.new("ShaderNodeValToRGB")
        cr.color_ramp.elements[0].position = 0.62 - clouds * 0.1
        cr.color_ramp.elements[1].position = 0.75
        cr.color_ramp.elements[0].color = (0, 0, 0, 1)
        cr.color_ramp.elements[1].color = (1, 1, 1, 1)
        nt.links.new(nz.outputs["Fac"], cr.inputs["Fac"])
        # fade clouds near horizon and zenith
        band = nt.nodes.new("ShaderNodeMapRange")
        band.inputs["From Min"].default_value = 0.0
        band.inputs["From Max"].default_value = 0.15
        nt.links.new(sep.outputs["Z"], band.inputs["Value"])
        mulc = nt.nodes.new("ShaderNodeMath")
        mulc.operation = "MULTIPLY"
        nt.links.new(cr.outputs["Color"], mulc.inputs[0])
        nt.links.new(band.outputs["Result"], mulc.inputs[1])
        mix = nt.nodes.new("ShaderNodeMix")
        mix.data_type = "RGBA"
        mix.inputs["B"].default_value = (*[min(1, c * 1.15 + 0.15) for c in hex_lin(hor)], 1)
        nt.links.new(mulc.outputs[0], mix.inputs["Factor"])
        nt.links.new(col, mix.inputs["A"])
        col = mix.outputs["Result"]
    if stars:
        vn = nt.nodes.new("ShaderNodeTexVoronoi")
        vn.inputs["Scale"].default_value = 180
        nt.links.new(tc.outputs["Generated"], vn.inputs["Vector"])
        sr = nt.nodes.new("ShaderNodeMath")
        sr.operation = "LESS_THAN"
        sr.inputs[1].default_value = 0.035
        nt.links.new(vn.outputs["Distance"], sr.inputs[0])
        add = nt.nodes.new("ShaderNodeMix")
        add.data_type = "RGBA"
        add.blend_type = "ADD"
        add.inputs["B"].default_value = (0.8, 0.85, 1.0, 1)
        nt.links.new(sr.outputs[0], add.inputs["Factor"])
        nt.links.new(col, add.inputs["A"])
        col = add.outputs["Result"]
    nt.links.new(col, bg.inputs["Color"])
    nt.links.new(bg.outputs[0], out.inputs["Surface"])
    # sun
    sun_d = bpy.data.lights.new("SUN", "SUN")
    sun_d.energy = en
    sun_d.color = hex_lin(sc)
    sun_d.angle = math.radians(ang)
    sun_d.shadow_cascade_max_distance = 80
    sun_d.shadow_cascade_count = 4
    sun = link(bpy.data.objects.new("SUN", sun_d))
    sun.rotation_euler = (math.radians(90 - se), 0, math.radians(sa))
    # fill (sky bounce, no shadow)
    fill_d = bpy.data.lights.new("FILL", "SUN")
    fill_d.energy = en * 0.18
    fill_d.color = hex_lin(zen)
    fill_d.use_shadow = False
    fill = link(bpy.data.objects.new("FILL", fill_d))
    fill.rotation_euler = (math.radians(50), 0, math.radians(sa + 180))
    return haze


def render_setup(res=(2304, 1296), samples=24, haze="#D4DFE6", mist=(15, 140), haze_amt=0.55, dof=None):
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_EEVEE"
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.resolution_percentage = 100
    e = sc.eevee
    e.taa_render_samples = samples
    e.use_soft_shadows = True
    e.use_gtao = True
    e.gtao_distance = 1.2
    e.use_bloom = True
    e.bloom_intensity = 0.03
    e.shadow_cube_size = "1024"
    e.shadow_cascade_size = "2048"
    sc.view_settings.view_transform = "AgX"
    try:
        sc.view_settings.look = "AgX - Punchy"
    except TypeError:
        pass
    sc.render.film_transparent = True
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGB"
    # atmospheric perspective via mist pass, applied to geometry only (sky comes from the Env pass)
    vl = sc.view_layers[0]
    vl.use_pass_mist = True
    vl.use_pass_environment = True
    sc.world.mist_settings.start = mist[0]
    sc.world.mist_settings.depth = mist[1]
    sc.world.mist_settings.falloff = "QUADRATIC"
    sc.use_nodes = True
    nt = sc.node_tree
    nt.nodes.clear()
    rl = nt.nodes.new("CompositorNodeRLayers")
    comp = nt.nodes.new("CompositorNodeComposite")
    mix = nt.nodes.new("CompositorNodeMixRGB")
    mix.inputs[2].default_value = (*hex_lin(haze), 1)
    mul = nt.nodes.new("CompositorNodeMath")
    mul.operation = "MULTIPLY"
    mul.inputs[1].default_value = haze_amt
    nt.links.new(rl.outputs["Mist"], mul.inputs[0])
    nt.links.new(mul.outputs[0], mix.inputs[0])
    nt.links.new(rl.outputs["Image"], mix.inputs[1])
    seta = nt.nodes.new("CompositorNodeSetAlpha")
    nt.links.new(mix.outputs[0], seta.inputs["Image"])
    nt.links.new(rl.outputs["Alpha"], seta.inputs["Alpha"])
    over = nt.nodes.new("CompositorNodeAlphaOver")
    nt.links.new(rl.outputs["Env"], over.inputs[1])
    nt.links.new(seta.outputs[0], over.inputs[2])
    nt.links.new(over.outputs[0], comp.inputs["Image"])


def camera(loc, target, lens=35, dof_dist=None, fstop=2.8, name="CAM"):
    cd = bpy.data.cameras.new(name)
    cd.lens = lens
    cd.clip_end = 2000
    cam = link(bpy.data.objects.new(name, cd))
    cam.location = loc
    d = Vector(target) - Vector(loc)
    cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    if dof_dist:
        cd.dof.use_dof = True
        cd.dof.focus_distance = dof_dist if dof_dist != "auto" else d.length
        cd.dof.aperture_fstop = fstop
    bpy.context.scene.camera = cam
    return cam


def point_light(loc, color="#FFC56B", energy=60, radius=0.3):
    ld = bpy.data.lights.new("PT", "POINT")
    ld.energy = energy
    ld.color = hex_lin(color)
    ld.shadow_soft_size = radius
    ob = link(bpy.data.objects.new("PT", ld))
    ob.location = loc
    return ob
