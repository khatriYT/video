"""Episode 4 renderer (v3).

blender -b --python tools/bats3d/render4.py -- <root> plate <SHOT>
blender -b --python tools/bats3d/render4.py -- <root> chars <SHOT> <duration_s> [first last]
blender -b --python tools/bats3d/render4.py -- <root> full  <SHOT> <duration_s> [first last]
blender -b --python tools/bats3d/render4.py -- <root> sprites <species> <preset>

Plates: 2304x1296 Eevee, soft shadows, contact shadows, GTAO, volumetrics; plus 16-bit depth.
Character pass: same camera/lights; RGBA (AOV mask), shadow + AO ratios vs a character-free baseline,
16-bit depth for occlusion against the plate depth; three-point character lighting (key = environment key,
fill and rim without shadows). 12 fps.
"""
import json
import math
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402
from bpy_extras.object_utils import world_to_camera_view  # noqa: E402

import core as C  # noqa: E402
import envs4  # noqa: E402
import flora as FL  # noqa: E402
from shots4 import SHOTS  # noqa: E402

PLATE_RES = (2304, 1296)
CHAR_FPS = 12
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []


# ------------------------------------------------------------------ props
def cave_clusters(E, state, rnd_seed=3):
    import random
    import bat as B
    rnd = random.Random(rnd_seed)
    n = dict(healthy=160, infected=110, empty=3, hope=60)[state]
    wns = 1.0 if state == "infected" else 0.0
    dg = bpy.context.evaluated_depsgraph_get()
    cave = E.ground[0].evaluated_get(dg)
    tmpl = B.build("clt", "myotis", "hanger", wns=wns, fur=True, fur_density=0.35)
    tmpl.root.hide_render = True
    bare = B.build("clb", "myotis", "hanger", wns=wns, fur=False)
    bare.root.hide_render = True
    hero_area = E.marks["cluster"] + Vector((-0.24, -0.3, 0))
    centers = [E.marks["cluster"], E.marks["cluster2"], E.marks["cluster"] + Vector((1.6, 1.2, 0)),
               E.marks["cluster2"] + Vector((-1.4, 1.0, 0))]
    placed = []
    for k in range(n):
        c = centers[k % len(centers)] if state != "empty" else centers[k]
        for _ in range(20):
            p = Vector((c.x + rnd.gauss(0, 0.11 + 0.03 * (k % 3)), c.y + rnd.gauss(0, 0.09), 1.5))
            if all((p.xy - q.xy).length > 0.06 for q in placed):
                break
        ok, loc, nrm, idx = cave.ray_cast(p, Vector((0, 0, 1)))
        if not ok:
            continue
        placed.append(loc)
        src = tmpl if (loc.xy - hero_area.xy).length < 0.55 else bare     # real fur only near the macro hero
        b = src.body.copy()
        b.data = src.body.data
        bpy.context.scene.collection.objects.link(b)
        b.hide_render = False
        sc = rnd.uniform(0.92, 1.08) * 1.35     # slightly enlarged for readability at cave-wide framings
        b.scale = (sc, sc, sc)
        b.location = loc - Vector((0, 0, 0.043 * sc))
        b.rotation_euler = (rnd.uniform(-0.12, 0.12), rnd.uniform(-0.12, 0.12), rnd.uniform(0, 6.28))
        for e in src.parts:
            if e is not src.body:
                e2 = e.copy()
                bpy.context.scene.collection.objects.link(e2)
                e2.parent = b
    return placed


def net_cage(c, s=(4.0, 4.0, 2.8)):
    m = C.m_simple("netting", "#E8E8E0", 0.8)
    x0, y0 = c[0] - s[0] / 2, c[1] - s[1] / 2
    lines = []
    for k in range(13):
        u = k / 12
        for (a, b) in (((x0 + s[0] * u, y0, 0), (x0 + s[0] * u, y0, s[2])), ((x0, y0 + s[1] * u, 0), (x0, y0 + s[1] * u, s[2])),
                       ((x0 + s[0] * u, y0 + s[1], 0), (x0 + s[0] * u, y0 + s[1], s[2])),
                       ((x0 + s[0], y0 + s[1] * u, 0), (x0 + s[0], y0 + s[1] * u, s[2])),
                       ((x0 + s[0] * u, y0, s[2]), (x0 + s[0] * u, y0 + s[1], s[2])),
                       ((x0, y0 + s[1] * u, s[2]), (x0 + s[0], y0 + s[1] * u, s[2]))):
            lines.append(C.tube(f"net{len(lines)}", [Vector(a), Vector(b)], [0.006, 0.006], 4, m))
        z = s[2] * u
        for (a, b) in (((x0, y0, z), (x0 + s[0], y0, z)), ((x0, y0, z), (x0, y0 + s[1], z)),
                       ((x0 + s[0], y0, z), (x0 + s[0], y0 + s[1], z)), ((x0, y0 + s[1], z), (x0 + s[0], y0 + s[1], z))):
            lines.append(C.tube(f"net{len(lines)}", [Vector(a), Vector(b)], [0.006, 0.006], 4, m))
    pole = FL.m_bark("pole", "#8A7A62", 10.0)
    for (x, y) in ((x0, y0), (x0 + s[0], y0), (x0, y0 + s[1]), (x0 + s[0], y0 + s[1])):
        C.tube(f"pole{x}{y}", [Vector((x, y, 0)), Vector((x, y, s[2] + 0.1))], [0.04, 0.04], 6, pole)


def foxes_hanging(E):
    import bat as B
    tmpl = B.build("fxh", "flyingfox", "hanger", fur=True, fur_density=0.5)
    spots = [(-2.2, 0.8, 6.6), (1.8, -1.2, 7.0), (3.2, 1.6, 7.4), (-3.6, -1.4, 7.2), (0.6, 2.4, 6.8)]
    for k, p in enumerate(spots):
        b = tmpl.body.copy()
        b.data = tmpl.body.data
        bpy.context.scene.collection.objects.link(b)
        b.location = Vector(p) - Vector((0, 0, 0.13))
        b.scale = (3.4, 3.4, 3.4)
        b.rotation_euler = (0, 0, k * 1.3)
        for e in tmpl.parts:
            if e is not tmpl.body:
                e2 = e.copy()
                bpy.context.scene.collection.objects.link(e2)
                e2.parent = b
    tmpl.root.location = spots[0]
    tmpl.root.hide_render = True


def durian_branch(E):
    """A low durian branch near the camera with hanging cream flower clusters and spiky fruit."""
    bark = FL.m_bark("durian_bark", "#6A5A4A", 6.0, moss="#5A7A3A")
    C.tube("dbranch", [Vector((-6, 2, 3.2)), Vector((-2, 1.0, 4.0)), Vector((1.5, 0.4, 4.4)), Vector((4, 0.6, 4.6))],
           [0.18, 0.14, 0.1, 0.06], 10, bark)
    pet = C.m_simple("durian_petal", "#F4EAD0", 0.5, sss=0.4)
    stam = C.m_simple("durian_stamen", "#F2D27A", 0.5, sss=0.3)
    fruit = FL.m_leaf("durian_fruit", "#7A8A3A", 0.08, 0.6, 0.1)
    E.flowers = []
    for k, x in enumerate((-1.6, -0.6, 0.4, 1.3, 2.2)):
        top = Vector((x, 0.75 - 0.08 * x, 4.05 + 0.1 * x))
        for j in range(5):
            stalk = top + Vector(((j - 2) * 0.05, 0.02 * j, -0.12 - 0.04 * (j % 2)))
            C.tube(f"dst{k}{j}", [top, stalk], [0.006, 0.004], 5, FL.m_leaf("dstalk", "#7A8A4A", 0.05))
            f = FL.icosphere(f"dfl{k}{j}", 0.035, 2, pet)
            f.location = stalk - Vector((0, 0, 0.03))
            f.scale = (1.0, 1.0, 1.4)
            s = FL.icosphere(f"dsm{k}{j}", 0.022, 1, stam)
            s.location = stalk - Vector((0, 0, 0.075))
            FL.disp(s, 0.01, 0.005, depth=1)
            E.flowers.append(stalk - Vector((0, 0, 0.07)))
    for k, x in enumerate((-3.5, 3.2)):
        fr = FL.icosphere(f"dfruit{k}", 0.16, 3, fruit)
        fr.location = (x, 0.9, 3.85)
        fr.scale = (1.0, 1.0, 1.25)
        FL.disp(fr, 0.05, 0.02, kind="VORONOI")


def add_props(E, shot):
    for p in shot["props"]:
        kind, arg = p
        if kind == "clusters":
            E.cluster_pts = cave_clusters(E, arg)
        elif kind == "net":
            net_cage(arg)
        elif kind == "foxes_hanging":
            foxes_hanging(E)
    if shot["env"] == "tropic" and shot["env_kw"].get("scene") == "durian":
        durian_branch(E)


# ------------------------------------------------------------------ actors
class Actor:
    def __init__(self, kind, obj, update, parts):
        self.kind, self.obj, self.update, self.parts = kind, obj, update, parts


def hero_point(E):
    """Ceiling attachment for the hero hibernating bat (edge of the main cluster)."""
    dg = bpy.context.evaluated_depsgraph_get()
    cave = E.ground[0].evaluated_get(dg)
    p = E.marks["cluster"] + Vector((-0.24, -0.3, 0))
    ok, loc, nrm, idx = cave.ray_cast(Vector((p.x, p.y, 1.5)), Vector((0, 0, 1)))
    return loc if ok else E.marks["cluster"]


def flower_point(E):
    """A low flower cluster on the hero flowering stalk (the nectar-bat close-up target)."""
    return E.flower_clusters[0][3]


def build_actors(E, shot, hidden=False):
    import human
    import bat as B
    acts = []
    for spec in shot["actors"]:
        kind = spec[0]
        if kind in ("pip", "farmer"):
            _, who, rot, motion, kw = spec
            p = E.marks[who] if isinstance(who, str) else Vector((who[0], who[1], 0.0))
            if not isinstance(who, str):
                p = envs4.ground_point(E.ground, p.x, p.y)
            # build at the origin, mount lamps in rig space, then place the character
            h = human.build(kind if kind == "farmer" else "pip", kind if kind == "farmer" else "pip",
                            loc=(0, 0, 0), rot_z=0.0)
            lamp_ob = None
            if kw.get("lamp") or motion == "lantern":
                if kw.get("lamp"):
                    lamp_ob = C.spot("HEADLAMP", (0, 0, 0), (0, -1, 0), "#FFE2B8", 420.0, 30.0, 0.5, 0.02)
                    lamp_ob.rotation_euler = (math.radians(-90), 0, 0)
                    hl = FL.icosphere("headlamp_body", 0.022, 2, C.m_simple("lampbody", "#2E2E2E", 0.4))
                    hl.location = Vector(human.SK.HEAD_C) + Vector((0, -0.118, 0.06))
                    hl.scale = (1.0, 0.7, 0.8)
                    human.hx(hl)
                    h.rig.attach(hl, "head")
                    hl["mask"] = 1.0
                    h.parts.append(hl)
                    lamp_ob.location = Vector(human.SK.HEAD_C) + Vector((0, -0.135, 0.06))
                    human.hx(lamp_ob)
                    h.rig.attach(lamp_ob, "head")
                else:
                    lamp_ob = C.point("LANTERN", (0, 0, 0), "#FFB45A", 90.0, 0.06)
                    lan = FL.icosphere("lantern_glass", 0.06, 2, C.m_emit("lantern_glow", "#FFC070", 10.0))
                    lan.scale = (1, 1, 1.4)
                    wr = Vector(human.SK.mirror(human.SK.WR, -1))
                    lan.location = wr + Vector((0, -0.02, -0.16))
                    lamp_ob.location = lan.location
                    h.rig.attach(lan, "hand.R")
                    h.rig.attach(lamp_ob, "hand.R")
                    lan["mask"] = 1.0
                    h.parts.append(lan)
            h.rig.ob.location = tuple(p)
            h.rig.ob.rotation_euler = (0, 0, rot)
            t_kw = dict(kw)
            if motion == "walk_to":
                start = Vector(p)
                end = envs4.ground_point(E.ground, kw["to"][0], kw["to"][1])

                def upd(t, h=h, start=start, end=end):
                    u = min(1.0, t / 6.0)
                    h.rig.ob.location = start.lerp(end, u)
                    human.animate(h, "walk", t, seed=2, speed=0.95)
            elif motion == "lantern":
                def upd(t, h=h):
                    rots, loc, face = human.motion("look_up", t * 0.3, 3)
                    rots["upperarm.R"] = (-30, 10, 8)
                    rots["forearm.R"] = (-60, 0, 0)
                    human.fingers(rots, "R", 0.85, 0.6)
                    rots["head"] = (-6, 0, 18 + 6 * math.sin(t * 0.6))
                    h.pose(rots, loc)
                    face["look"] = (0.25, -1, -0.1)
                    h.face.set(**face)
            else:
                def upd(t, h=h, motion=motion, t_kw=t_kw):
                    human.animate(h, motion if motion != "look_up" or not t_kw.get("awe") else "look_up", t, seed=1,
                                  **{k: v for k, v in t_kw.items() if k in ("awe", "side")})
            acts.append(Actor(kind, h.rig.ob, upd, h.parts + [h.rig.ob]))
        elif kind == "hanger":
            _, sp, where, motion, kw = spec
            b = B.build("hero", sp, "hanger", wns=kw.get("wns", 0.0), fur=True, fur_density=1.0)
            hp = hero_point(E)
            b.root.location = hp - Vector((0, 0, 0.043))
            b.root.rotation_euler = (0, 0, 0.5)

            def upd(t, b=b, motion=motion):
                B.animate(b, t, "wake" if motion == "wake" and t > 1.2 else "breathe", rz=0.5)
                if motion == "wake":
                    for e in b.parts:
                        if e.name.startswith("hero_eye"):
                            e.scale = (B.BK.SPECIES[b.sp]["eye_r"],) * 2 + (B.BK.SPECIES[b.sp]["eye_r"] *
                                                                        (0.35 if t < 1.6 else 1.0),)
            acts.append(Actor(kind, b.root, upd, b.parts))
            E.hero = hp
        elif kind == "nectar":
            _, where, motion, kw = spec
            b = B.build("nb", kw.get("sp", "nectar"), "flyer", fur=True)
            target = flower_point(E) if where == "flower" else E.flowers[2]
            # hover just outside the blossoms on the camera side, facing them, body tilted up
            camp = Vector(shot["cam"][1]) if False else None
            cam_off = Vector((0.42, -0.82, 0.08)) if where == "flower" else Vector((0.9, -1.1, 0.1))
            f = (-cam_off).normalized()                      # camera viewing direction
            right = f.cross(Vector((0, 0, 1))).normalized()   # screen-right in the world
            lat = 0.23 if where == "flower" else 0.1
            base = target - right * lat - f * 0.04 + Vector((0, 0, -0.03))
            yaw = math.atan2(right.x, -right.y)              # snout (local -Y) points screen-right, into the flower
            b.rig.ob.rotation_euler = (math.radians(-35), 0, yaw)
            d = right

            def upd(t, b=b, base=base, d=d):
                side = Vector((-d.y, d.x, 0))
                off = side * 0.03 * math.sin(t * 1.3) + d * 0.015 * math.sin(t * 0.7) + Vector((0, 0, 0.012 * math.sin(t * 2.1)))
                b.rig.ob.location = base + off
                B.animate(b, t, "hover", freq=4.0 if where == "flower" else 3.0)
            acts.append(Actor(kind, b.rig.ob, upd, b.parts + [b.rig.ob]))
        elif kind == "tractor":
            _, a, z = spec
            tr = envs4.tractor("tractor_a", (a[0], a[1], 0.0), math.radians(0), spray=True)
            pa = envs4.ground_point(E.ground, *a)
            pz = envs4.ground_point(E.ground, *z)
            parts = [tr] + list(tr.children)

            def upd(t, tr=tr, pa=pa, pz=pz):
                u = min(1.0, t / 9.0)
                tr.location = pa.lerp(pz, u)
                tr.rotation_euler = (0, 0, math.radians(180))
            acts.append(Actor(kind, tr, upd, parts))
        elif kind == "rotors":
            def upd(t, rots=E.turbines):
                # angle with exponential slow-down (curtailment)
                for k, r in enumerate(rots):
                    w = 1.6 * math.exp(-t / 3.0)
                    ang = 1.6 * 3.0 * (1 - math.exp(-t / 3.0)) + k * 0.7
                    r.rotation_euler = (0, ang, 0)
            parts = []
            for r in E.turbines:
                parts += [r] + list(r.children)
            acts.append(Actor(kind, None, upd, parts))
        elif kind == "seedlings":
            def upd(t, sd=E.seedlings):
                for k, r in enumerate(sd):
                    g = max(0.02, min(1.0, (t - 0.25 * (k % 7)) / 5.0))
                    g = g * g * (3 - 2 * g)
                    r.scale = (g, g, g)
            parts = []
            for r in E.seedlings:
                parts += [r] + list(r.children)
            acts.append(Actor(kind, None, upd, parts))
        elif kind == "studio_bat":
            b = B.build("sb", spec[1], "flyer", fur="xray" not in shot.get("fx", []))
            if "xray" in shot.get("fx", []):
                glow = C.m_emit("xray_bone", "#7FF4FF", 6.0)
                ghost = C.m_glass("xray_skin", "#2A6A8A", 0.18)
                for ob in b.parts:
                    if ob.type != "MESH":
                        continue
                    if "_d" in ob.name or "_hum" in ob.name or "_fore" in ob.name or "_j" in ob.name or "claw" in ob.name:
                        ob.data.materials[0] = glow
                    else:
                        for i in range(len(ob.data.materials)):
                            ob.data.materials[i] = ghost
            b.rig.ob.location = (0, 0, 1.45)
            b.rig.ob.rotation_euler = (math.radians(-90), 0, 0)    # face the camera, belly forward, wings spread

            def upd(t, b=b):
                b.rig.ob.rotation_euler = (math.radians(-82), 0, math.radians(14 * math.sin(t * 0.45)))
                spread = min(1.0, t / 2.0)
                B.pose(b, B.flap(0.0, glide=1.0) if spread >= 1 else B.flap(0.0, amp=0, fold=60 * (1 - spread),
                                                                           glide=spread))
            acts.append(Actor(kind, b.rig.ob, upd, b.parts + [b.rig.ob]))
    for a in acts:
        for ob in a.parts:
            ob["mask"] = 1.0
            if hidden:
                ob.hide_render = True
    return acts


# ------------------------------------------------------------------ scene assembly
def camera_for(E, shot, acts=None):
    cam = shot["cam"]
    if cam[0] == "flower":
        tgt = flower_point(E)
        loc = tgt + Vector((0.42, -0.82, 0.08))
        c = C.camera(tuple(loc), tuple(tgt + Vector((0, -0.04, 0.0))), cam[2],
                     dof=(None, cam[3]) if len(cam) > 3 else None)
    elif cam[0] == "durian":
        tgt = E.flowers[2]
        loc = tgt + Vector((0.9, -1.1, 0.1))
        c = C.camera(tuple(loc), tuple(tgt), cam[2], dof=(None, cam[3]) if len(cam) > 3 else None)
    else:
        loc, tgt, lens = cam[0], cam[1], cam[2]
        if shot["env"] == "cave" and len(cam) > 3:      # close-ups are relative to the hero bat
            hp = getattr(E, "hero", None) or hero_point(E)
            tgt = hp - Vector((0, 0, 0.045))
            off = Vector(loc) - Vector((0.8, 0.6, 3.36))
            loc = tgt + off * 1.0 + Vector((0, 0, 0.0))
        c = C.camera(tuple(loc), tuple(tgt), lens, dof=(None, cam[3]) if len(cam) > 3 else None)
    c.data.dof.aperture_blades = 7
    return c


def lights_for(E, shot, cam, mode):
    if E.key:
        k = C.sun("SUN", E.key[0], E.key[1], E.key[2], angle=2.5)
    lamp = shot.get("lamp")
    bpy.context.view_layer.update()          # camera matrix must be current before aiming lamps at its view
    cl, ct = cam.matrix_world.translation.copy(), cam.matrix_world @ Vector((0, 0, -3))
    if lamp in ("cam", "cam_warm"):
        C.spot("TORCH", tuple(cl + Vector((0.25, 0.1, 0.25))), tuple(ct), "#FFD9A0" if lamp == "cam" else "#FFC27A",
               700.0, 42.0, 0.55, 0.03)
    elif lamp == "cam_left":
        C.spot("TORCH", tuple(cl + Vector((-0.25, -0.05, 0.08))), tuple(ct), "#FFDDB0", 60.0, 30.0, 0.6, 0.01)
        C.area("MACRO_FILL", tuple(cl + Vector((0.3, 0.0, -0.1))), tuple(ct), "#6A9AB0", 2.0, 0.3)
        C.area("MACRO_RIM", tuple(ct + Vector((0.2, 0.35, 0.05))), tuple(ct), "#FFD0A0", 4.0, 0.15)
    if E.name == "studio":
        C.area("KEY", (-1.6, -2.2, 2.6), (0, 0, 1.45), "#FFE6CC", 500.0, 1.6, shadow=True)
        C.area("FILL", (2.4, -1.8, 1.4), (0, 0, 1.45), "#7AB8E8", 180.0, 2.5)
        C.area("RIM", (0.5, 2.2, 2.4), (0, 0, 1.45), "#FF9A6A", 700.0, 1.0)
        C.area("RIM2", (-1.8, 1.6, 0.6), (0, 0, 1.45), "#B07AFF", 400.0, 1.0)


def char_rig_lights(E, shot, acts, cam):
    """Fill + rim for the characters (no shadows, so the shadow pass only holds the environment key)."""
    if not acts or E.name == "studio":
        return
    ob = acts[0].obj or acts[0].parts[0]
    s = ob.matrix_world.translation + Vector((0, 0, 1.0 if acts[0].kind in ("pip", "farmer") else 0.0))
    fill_col, fill_e = E.fill if E.fill else ("#8AA0C8", 0.6)
    rim_col, rim_e = E.rim if E.rim else ("#FFD0A0", 0.8)
    scale = 1.0 if acts[0].kind in ("pip", "farmer", "tractor") else 0.08
    to_cam = (cam.location - s)
    to_cam.z = 0
    to_cam.normalize()
    side = to_cam.cross(Vector((0, 0, 1))).normalized()
    C.area("CH_FILL", tuple(s + (to_cam * 1.0 + side * 0.8 + Vector((0, 0, 0.3))) * 3.0 * scale), tuple(s), fill_col,
           220.0 * fill_e * scale * scale, 3.0 * scale)
    C.area("CH_RIM", tuple(s + (-to_cam * 1.0 - side * 0.5 + Vector((0, 0, 0.8))) * 2.5 * scale), tuple(s), rim_col,
           420.0 * rim_e * scale * scale, 1.0 * scale)


def build(shot_id, mode, detail, props=True):
    shot = SHOTS[shot_id]
    C.reset()
    kw = dict(shot["env_kw"])
    bare = kw.pop("bare", False)
    if shot["env"] in ("studio", "sky", "mine", "wind"):
        E = envs4.BUILDERS[shot["env"]]()
    else:
        E = envs4.BUILDERS[shot["env"]](shot["state"], detail=detail, **kw)
    if bare and getattr(E, "seedlings", None):
        for r in E.seedlings:
            for ob in [r] + list(r.children):
                ob.hide_render = True
        E.seedlings = []
    if props:
        add_props(E, shot)
    elif shot["env"] == "tropic" and shot["env_kw"].get("scene") == "durian":
        durian_branch(E)          # needed for the actor's target flowers
    return shot, E


def setup_passes(mode):
    sc = bpy.context.scene
    vl = sc.view_layers[0]
    vl.use_pass_z = True
    if mode == "chars":
        vl.use_pass_shadow = True
        vl.use_pass_ambient_occlusion = True
        aov = vl.aovs.add()
        aov.name = "mask"
        aov.type = "VALUE"
    sc.use_nodes = True
    nt = sc.node_tree
    nt.nodes.clear()
    rl = nt.nodes.new("CompositorNodeRLayers")
    comp = nt.nodes.new("CompositorNodeComposite")
    nt.links.new(rl.outputs["Image"], comp.inputs["Image"])
    if mode == "chars":
        sa = nt.nodes.new("CompositorNodeSetAlpha")
        sa.mode = "REPLACE_ALPHA"
        nt.links.new(rl.outputs["Image"], sa.inputs["Image"])
        nt.links.new(rl.outputs["mask"], sa.inputs["Alpha"])
        nt.links.new(sa.outputs[0], comp.inputs["Image"])
    fo = nt.nodes.new("CompositorNodeOutputFile")
    fo.format.file_format = "PNG"
    fo.format.color_mode = "BW"
    fo.format.color_depth = "16"
    fo.file_slots.clear()
    # depth encoded as 1/(1+z/10): near = 1, far -> 0 (better precision close up)
    dv = nt.nodes.new("CompositorNodeMath")
    dv.operation = "DIVIDE"
    dv.inputs[1].default_value = 10.0
    nt.links.new(rl.outputs["Depth"], dv.inputs[0])
    ad = nt.nodes.new("CompositorNodeMath")
    ad.operation = "ADD"
    ad.inputs[1].default_value = 1.0
    nt.links.new(dv.outputs[0], ad.inputs[0])
    iv = nt.nodes.new("CompositorNodeMath")
    iv.operation = "DIVIDE"
    iv.inputs[0].default_value = 1.0
    nt.links.new(ad.outputs[0], iv.inputs[1])
    fo.file_slots.new("depth_")
    nt.links.new(iv.outputs[0], fo.inputs["depth_"])
    if mode == "chars":
        fo.file_slots.new("shadow_")
        nt.links.new(rl.outputs["Shadow"], fo.inputs["shadow_"])
        fo.file_slots.new("ao_")
        nt.links.new(rl.outputs["AO"], fo.inputs["ao_"])
    return fo


def cam_meta(cam, res):
    sc = bpy.context.scene
    return dict(matrix=[list(r) for r in cam.matrix_world], lens=cam.data.lens, sensor=cam.data.sensor_width,
                res=list(res), clip=[cam.data.clip_start, cam.data.clip_end])


def do_plate(root, shot_id):
    out = os.path.join(root, "plates")
    os.makedirs(out, exist_ok=True)
    if os.path.exists(os.path.join(out, shot_id + ".png")) and not os.environ.get("FORCE"):
        print("skip", shot_id)
        return
    t0 = time.time()
    shot, E = build(shot_id, "plate", 1.0)
    acts = build_actors(E, shot, hidden=True) if (shot.get("lamp") in ("pip", "lantern")) else []
    for a in acts:
        a.update(0.0)
    if shot["env"] == "wind":
        for r in E.turbines:
            for ob in [r] + list(r.children):
                ob.hide_render = True
    if getattr(E, "seedlings", None) and any(a[0] == "seedlings" for a in shot["actors"]):
        for r in E.seedlings:
            for ob in [r] + list(r.children):
                ob.hide_render = True
    cam = camera_for(E, shot, acts)
    lights_for(E, shot, cam, "plate")
    C.render_setup(PLATE_RES, int(os.environ.get("PLATE_SAMPLES", "20")), volumetric=True, vol_tile="8",
                   vol_samples=64, bloom=0.03)
    fo = setup_passes("plate")
    tmp = os.path.join(out, "tmp_" + shot_id)
    fo.base_path = tmp
    bpy.context.scene.render.filepath = os.path.join(out, shot_id + ".png")
    print("BUILD", shot_id, round(time.time() - t0, 1), flush=True)
    bpy.ops.render.render(write_still=True)
    for f in os.listdir(tmp):
        os.replace(os.path.join(tmp, f), os.path.join(out, shot_id + "_depth.png"))
    os.rmdir(tmp)
    json.dump(dict(cam=cam_meta(cam, PLATE_RES), key=E.key, marks={k: list(v) for k, v in E.marks.items()},
                   flowers=[list(p) for p in getattr(E, "flowers", [])],
                   stalks=[list(p) for p in getattr(E, "stalks", [])],
                   clusters=[[list(p) for p in c] for c in getattr(E, "flower_clusters", [])],
                   hero=list(getattr(E, "hero", Vector())) if getattr(E, "hero", None) else None),
              open(os.path.join(out, shot_id + ".json"), "w"), indent=1)
    print("PLATE", shot_id, round(time.time() - t0, 1), flush=True)


def mask_all_materials():
    for m in bpy.data.materials:
        if m.use_nodes:
            C.add_mask_aov(m)


def stand_in_materials(acts):
    keep = set()
    for a in acts:
        for ob in a.parts:
            keep.add(ob.name)
    m = C.m_simple("standin", "#808080", 0.9)
    for ob in bpy.context.scene.objects:
        if ob.name in keep or ob.type != "MESH":
            continue
        if ob.data.materials:
            for i in range(len(ob.data.materials)):
                ob.data.materials[i] = m
        # volumetric fog cube: hide in the character pass
        if ob.name.startswith("Fog"):
            ob.hide_render = True
    for nm in list(bpy.data.node_groups.keys()):   # drop scattered vegetation instances
        pass
    for ob in bpy.context.scene.objects:
        for md in list(ob.modifiers):
            if md.type == "NODES" and md.name.startswith("sc_"):
                md.show_render = False


def char_border(cam, acts, sc, key_dir):
    pts = []
    dg = bpy.context.evaluated_depsgraph_get()
    for a in acts:
        for ob in a.parts:
            if ob.type not in ("MESH",) or ob.hide_render:
                continue
            for c in ob.bound_box:
                w = ob.matrix_world @ Vector(c)
                pts.append(w)
                if key_dir is not None:      # shadow reach on the ground
                    d = Vector(key_dir).normalized()
                    if d.z > 0.05:
                        t = (w.z - (a.obj.matrix_world.translation.z if a.obj else 0.0)) / d.z
                        pts.append(w - d * min(t, 30.0))
    if not pts:
        return None
    xs, ys = [], []
    for p in pts:
        v = world_to_camera_view(sc, cam, p)
        if v.z > 0:
            xs.append(v.x)
            ys.append(v.y)
    if not xs:
        return None
    m = 0.03
    return max(0.0, min(xs) - m), min(1.0, max(xs) + m), max(0.0, min(ys) - m), min(1.0, max(ys) + m)


def do_chars(root, shot_id, dur, first=None, last=None, full=False):
    shot, E = build(shot_id, "chars", 1.0 if full else 0.0, props=full)
    acts = build_actors(E, shot)
    cam = camera_for(E, shot, acts)
    lights_for(E, shot, cam, "chars")
    char_rig_lights(E, shot, acts, cam)
    sc = bpy.context.scene
    res = PLATE_RES if not full else (1920, 1080)
    if full:
        C.render_setup(res, int(os.environ.get("SAMPLES", "24")), volumetric=False, bloom=0.04)
        setup_passes("full")
    else:
        stand_in_materials(acts)
        mask_all_materials()
        C.render_setup(res, int(os.environ.get("SAMPLES", "6")), volumetric=False, bloom=0.0, transparent=True,
                       shadow_cube="512", shadow_cascade="2048")
        sc.eevee.use_ssr = False
        sc.eevee.use_soft_shadows = os.environ.get("SOFT", "0") == "1"
        sc.eevee.sss_samples = 5
        sc.eevee.gtao_distance = 0.4
        for ob in bpy.context.scene.objects:      # only the key light needs high-res cascades here
            if ob.type == "LIGHT" and ob.data.type == "SUN":
                ob.data.shadow_cascade_count = 2
                ob.data.shadow_cascade_max_distance = 25.0
        fo = setup_passes("chars")
    out = os.path.join(root, "full" if full else "chars", shot_id)
    os.makedirs(out, exist_ok=True)
    fps = int(os.environ.get("CHAR_FPS", str(shot.get("fps", CHAR_FPS))))
    n = 1 if shot.get("hold") else int(math.ceil(dur * fps)) + 1
    a0 = 0 if first is None else first
    a1 = n - 1 if last is None else min(last, n - 1)
    key_dir = E.key[0] if E.key else None
    if not full and not os.path.exists(os.path.join(out, "base_shadow.png")):
        # character-free baseline for shadow / AO ratios
        for a in acts:
            a.update(0.0)
            for ob in a.parts:
                ob.hide_render = True
        tmp = os.path.join(out, "tmp_base")
        fo.base_path = tmp
        sc.render.filepath = os.path.join(out, "base_rgba.png")
        sc.render.use_border = False
        bpy.ops.render.render(write_still=True)
        for f in os.listdir(tmp):
            os.replace(os.path.join(tmp, f), os.path.join(out, "base_" + f.split("_")[0] + ".png"))
        os.rmdir(tmp)
        for a in acts:
            for ob in a.parts:
                ob.hide_render = False
    json.dump(dict(cam=cam_meta(cam, res), fps=fps, frames=n, key=E.key),
              open(os.path.join(out, "meta.json"), "w"), indent=1)
    for i in range(a0, a1 + 1):
        fn = os.path.join(out, f"char_{i:04d}.png")
        if os.path.exists(fn):
            continue
        t = i / fps
        for a in acts:
            a.update(t)
        bpy.context.view_layer.update()
        if not full:
            b = char_border(cam, acts, sc, key_dir)
            if b:
                sc.render.use_border = True
                sc.render.use_crop_to_border = False
                sc.render.border_min_x, sc.render.border_max_x, sc.render.border_min_y, sc.render.border_max_y = b
            tmp = os.path.join(out, f"tmp_{i:04d}")
            fo.base_path = tmp
        t1 = time.time()
        sc.render.filepath = fn
        bpy.ops.render.render(write_still=True)
        if not full:
            for f in os.listdir(tmp):
                os.replace(os.path.join(tmp, f), os.path.join(out, f.split("_")[0] + f"_{i:04d}.png"))
            os.rmdir(tmp)
        print("FRAME", shot_id, i, round(time.time() - t1, 1), flush=True)


# ------------------------------------------------------------------ sprites
SPRITE_LIGHTS = {
    "sunset": dict(key=((1.0, -0.15, 0.12), "#FFA868", 6.0), world=("#8C86B8", 0.9), rim=("#FFC27A", 1.0)),
    "dusk": dict(key=((0.7, 1.0, 0.06), "#FF8E5E", 2.4), world=("#6A6AC0", 0.8), rim=("#FFB078", 1.0)),
    "moon": dict(key=((-0.35, 1.0, 0.45), "#B8C8FF", 1.3), world=("#2A3A7A", 0.6), rim=("#9AB0FF", 0.9)),
    "dawn": dict(key=((0.5, 1.0, 0.2), "#FFD58A", 4.5), world=("#9AD0C8", 0.8), rim=("#FFE0A0", 1.0)),
}
SPR_AZ = 8
SPR_EL = (-35.0, 0.0, 35.0)
SPR_FRAMES = 12
SPR_CELL = 256


def do_sprites(root, sp, preset):
    """Atlas per flap frame: rows = elevations, columns = azimuths. The bat is seen from direction
    (az, el) in its own frame; the compositor picks the nearest cell for each simulated bat."""
    import bat as B
    out = os.path.join(root, "sprites", f"{sp}_{preset}")
    os.makedirs(out, exist_ok=True)
    C.reset()
    L = SPRITE_LIGHTS[preset]
    C.world_flat(L["world"][0], L["world"][1])
    C.sun("SUN", L["key"][0], L["key"][1], L["key"][2], angle=3.0)
    C.sun("RIM", (-L["key"][0][0], -L["key"][0][1], 0.3), L["rim"][0], L["rim"][1] * 2.0, angle=8.0, shadow=False)
    k = B.BK.SPECIES[sp]["scale"]
    bats = []
    spacing = 0.42 * k
    for ei, el in enumerate(SPR_EL):
        for ai in range(SPR_AZ):
            b = B.build(f"s{ei}{ai}", sp, "flyer", fur=True, fur_density=0.5)
            az = 2 * math.pi * ai / SPR_AZ
            # orient the bat so the (fixed, -Y looking) camera sees it from (az, el)
            b.rig.ob.rotation_mode = "XYZ"
            b.rig.ob.rotation_euler = (math.radians(-el), 0.0, az)
            b.rig.ob.location = (spacing * (ai - (SPR_AZ - 1) / 2), 0.0, spacing * (1 - ei))
            bats.append(b)
    cam = C.camera((0, -40.0 * k, 0), (0, 0, 0), 50)
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = spacing * SPR_AZ
    C.render_setup((SPR_CELL * SPR_AZ, SPR_CELL * len(SPR_EL)), 16, volumetric=False, bloom=0.0, transparent=True,
                   ssr=False)
    sc = bpy.context.scene
    for f in range(SPR_FRAMES):
        fn = os.path.join(out, f"atlas_{f:02d}.png")
        if os.path.exists(fn):
            continue
        t = f / (SPR_FRAMES * 8.0)
        for b in bats:
            B.animate(b, t, "flap", freq=8.0)
        sc.render.filepath = fn
        bpy.ops.render.render(write_still=True)
        print("SPRITE", sp, preset, f, flush=True)
    json.dump(dict(az=SPR_AZ, el=list(SPR_EL), frames=SPR_FRAMES, cell=SPR_CELL), open(os.path.join(out, "meta.json"), "w"))


if __name__ == "__main__" and argv:
    root, mode = argv[0], argv[1]
    if mode == "plate":
        for sid in argv[2].split(","):
            do_plate(root, sid)
    elif mode in ("chars", "full"):
        sid, dur = argv[2], float(argv[3])
        a = int(argv[4]) if len(argv) > 4 else None
        b = int(argv[5]) if len(argv) > 5 else None
        do_chars(root, sid, dur, a, b, full=(mode == "full"))
    elif mode == "sprites":
        do_sprites(root, argv[2], argv[3])
