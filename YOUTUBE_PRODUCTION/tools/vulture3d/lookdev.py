"""Look-dev sheet for v2 characters: blender -b --factory-startup -P tools/vulture3d/lookdev.py -- <out_dir>"""
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from mathutils import Vector
import lib as L
import rigs as R
OUT = sys.argv[sys.argv.index("--") + 1]
os.makedirs(OUT, exist_ok=True)
CASES = [("vulture", "stand", 1.2, (2.4, -2.6, 1.0), (0, 0, 0.75), 0.0),
         ("vulture", "feed", 0.9, (2.4, -2.6, 1.0), (0.2, 0, 0.5), 0.0),
         ("vulture", "spread", 0.5, (3.2, -3.6, 1.2), (0, 0, 0.8), 0.0),
         ("vulture", "soar", 1.0, (1.4, -3.4, 2.4), (0, 0, 4.4), 0.0),
         ("dog", "walk", 0.3, (2.0, -2.4, 0.8), (0.1, 0, 0.55), 0.0),
         ("dog", "sit", 0.3, (2.0, -2.4, 0.8), (0.1, 0, 0.55), 0.0),
         ("pip", "idle", 0.5, (1.6, -4.0, 1.7), (0, 0, 1.2), 0.0),
         ("pip", "binoculars", 1.5, (2.2, -3.8, 1.7), (0, 0, 1.3), 0.0),
         ("pip", "wave", 0.6, (1.6, -4.0, 1.7), (0, 0, 1.2), 0.0),
         ("pip", "walk", 0.4, (2.4, -3.8, 1.6), (0, 0, 1.1), 0.0),
         ("crow", "hop", 0.1, (0.9, -1.0, 0.4), (0, 0, 0.25), 0.0),
         ("cow", "idle", 1.0, (3.6, -4.4, 1.6), (0.3, 0, 1.0), 0.0),
         ("villager", "walk", 0.6, (2.0, -4.0, 1.6), (0, 0, 1.1), 0.0)]
ONLY = sys.argv[sys.argv.index("--") + 2:] if len(sys.argv) > sys.argv.index("--") + 2 else None
for i, (kind, act, t, cam, tgt, rz) in enumerate(CASES):
    if ONLY and str(i) not in ONLY:
        continue
    L.reset(); R.reset_caches()
    M = L.P(); M2 = R.M2()
    L.world("morning", clouds=0.3)
    g = L.ground(M, size=30, color="#B9A27A", color2="#A58C61")
    g.modifiers["d"].strength = 0.0
    P = R.build(M2, kind, kind)
    A = R.Actor(P, act, (0, 0, 4.0 if act == "soar" else 0), rz, 1.0, seed=1, radius=0.0, center=(0, 0, 4.0), vel=(0.0, -0.6, 0) if kind in ("pip", "villager") else (0.6, 0, 0))
    A.update(t)
    L.camera(cam, tgt, lens=45)
    L.render_setup((640, 640), 16, haze="#DCDCD4", mist=(40, 200), haze_amt=0.3)
    bpy.context.scene.render.filepath = f"{OUT}/{i:02d}_{kind}_{act}.png"
    bpy.ops.render.render(write_still=True)
    print("LOOKDEV", kind, act, flush=True)
