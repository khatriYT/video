"""Quick environment look-dev: blender -b --python envtest.py -- out.png env state camx,camy,camz tx,ty,tz lens [w h samples] [pip]"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy  # noqa: E402
from mathutils import Vector  # noqa: E402

import core as C  # noqa: E402
import envs4  # noqa: E402

a = sys.argv[sys.argv.index("--") + 1:]
out, env, state = a[0], a[1], a[2]
cam = tuple(float(x) for x in a[3].split(","))
tgt = tuple(float(x) for x in a[4].split(","))
lens = float(a[5])
w, h, smp = (int(a[6]), int(a[7]), int(a[8])) if len(a) > 8 else (960, 540, 16)
C.reset()
t0 = time.time()
kw = {} if env in ("studio", "sky", "mine", "wind") else dict(detail=0.7)
E = envs4.BUILDERS[env](state, **kw) if env not in ("studio", "sky", "mine", "wind") else envs4.BUILDERS[env]()
if E.key:
    C.sun("SUN", E.key[0], E.key[1], E.key[2], angle=3.0)
if "pip" in a:
    import human
    p = E.marks.get("pip", Vector((0, 0, 0)))
    hm = human.build("pip", "pip", loc=tuple(p), rot_z=3.14159)
    human.animate(hm, "idle", 1.0)
if env == "cave":
    C.spot("LAMP", (-0.4, -3.4, 1.7), (0.8, 0.6, 3.4), "#FFD9A0", 900.0, 38.0, 0.6, 0.03)
print("BUILD", round(time.time() - t0, 1), flush=True)
if "bake" in a:
    C.irradiance_volume((tgt[0], tgt[1], tgt[2]), (25, 25, 8), (8, 8, 4))
    bpy.context.scene.eevee.gi_diffuse_bounces = 2
    t2 = time.time()
    ok = C.bake_light_cache()
    print("BAKE", ok, round(time.time() - t2, 1), flush=True)
C.camera(cam, tgt, lens)
C.render_setup((w, h), smp, volumetric=True, vol_tile="8", vol_samples=32)
if "bake" in a:
    pass
bpy.context.scene.render.filepath = out
t1 = time.time()
bpy.ops.render.render(write_still=True)
print("RENDER", round(time.time() - t1, 1), flush=True)
