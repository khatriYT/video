"""Look-dev turntable / portrait renders for v3 assets.

blender -b --python tools/bats3d/lookdev4.py -- <out_dir> <asset> [views] [samples]
asset: pip | farmer | researcher | bat_<species> ...
views: comma list of full,face,hands,back,pose_<motion>
"""
import math
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy  # noqa: E402
from mathutils import Vector  # noqa: E402

import core  # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:]
out, asset = argv[0], argv[1]
views = argv[2].split(",") if len(argv) > 2 else ["full", "face"]
samples = int(argv[3]) if len(argv) > 3 else 32
os.makedirs(out, exist_ok=True)

core.reset()
t0 = time.time()
if asset in ("pip", "farmer", "researcher"):
    import human
    h = human.build(asset, asset)
    subject = h
else:
    import bat
    parts = asset.split("_")
    sp = parts[1]
    wns = 1.0 if "wns" in parts else 0.0
    h = bat.build("bat", sp, "flyer", wns=wns)
    hang = bat.build("hang", sp, "hanger", wns=wns, loc=(0.25 * bat.BK.SPECIES[sp]["scale"], 0.0, 0.0))
    subject = h
print("BUILD s", round(time.time() - t0, 1), flush=True)

# studio floor + cyclorama
floor = core.lathe("cyc", [(0.0, 0.0), (6.0, 0.0), (7.0, 0.6), (7.2, 3.0)], 64,
                   core.m_simple("cyc", "#6F7F86", 0.7), close_top=False)
core.world_sky([(0.0, "#C9D6DC"), (1.0, "#7E98A8")], strength=0.6)
core.render_setup((1080, 1350), samples, bloom=0.02)

human_like = asset in ("pip", "farmer", "researcher")
for v in views:
    for ob in list(bpy.data.objects):
        if ob.type in ("LIGHT", "CAMERA"):
            bpy.data.objects.remove(ob)
    if human_like:
        if v.startswith("pose_"):
            human.animate(h, v[5:], 2.0, seed=1)
        else:
            human.animate(h, "idle", 1.3, seed=1)
        bpy.context.view_layer.update()
        if v in ("full", "back") or v.startswith("pose_"):
            tgt = Vector((0, 0, 0.92))
            camloc = Vector((1.3, -3.6, 1.25)) if v != "back" else Vector((-1.6, 3.4, 1.4))
            lens = 55
        elif v == "face":
            tgt = Vector((0, -0.04, 1.565))
            camloc = Vector((0.32, -0.78, 1.6))
            lens = 85
        elif v == "hands":
            tgt = Vector((0.33, -0.02, 0.83))
            camloc = Vector((0.75, -0.75, 0.95))
            lens = 85
        cam = core.camera(tuple(camloc), tuple(tgt), lens)
        core.three_point(tuple(tgt), tuple(camloc), (-0.7, -0.9, 0.9), "#FFE9D2", 900 if v != "face" else 260,
                         "#A9C8E8", 160 if v != "face" else 60, "#FFD6A8", 900 if v != "face" else 300,
                         dist=3.0 if v != "face" else 1.6, size=1.4 if v != "face" else 0.8)
    else:
        k = bat.BK.SPECIES[sp]["scale"]
        bat.animate(h, 0.0, "spread" if v == "top" else "flap", freq=0.0) if v != "flap" else bat.animate(h, 0.07)
        if v == "top":
            tgt, camloc, lens = Vector((0, 0.01, 0)) * k, Vector((0.0, 0.05, 0.55)) * k, 50
        elif v == "front":
            tgt, camloc, lens = Vector((0, -0.01, 0.0)) * k, Vector((0.12, -0.38, 0.12)) * k, 50
        elif v == "face":
            tgt, camloc, lens = Vector((0, -0.045, 0.006)) * k, Vector((0.05, -0.16, 0.03)) * k, 85
        elif v == "flap":
            tgt, camloc, lens = Vector((0, 0.0, 0.0)) * k, Vector((0.25, -0.35, 0.18)) * k, 50
        elif v == "hang":
            tgt, camloc, lens = Vector((0.25, 0.0, -0.01)) * k, Vector((0.33, -0.18, -0.03)) * k, 70
        cam = core.camera(tuple(camloc), tuple(tgt), lens)
        floor.hide_render = True
        core.three_point(tuple(tgt), tuple(camloc), (-0.7, -0.9, 0.9), "#FFE9D2", 12 * k * k, "#A9C8E8", 2.5 * k * k,
                         "#FFC690", 20 * k * k, dist=0.5 * k, size=0.25 * k)
    bpy.context.scene.render.filepath = os.path.join(out, f"{asset}_{v}.png")
    t1 = time.time()
    bpy.ops.render.render(write_still=True)
    print("RENDER", v, round(time.time() - t1, 1), flush=True)
