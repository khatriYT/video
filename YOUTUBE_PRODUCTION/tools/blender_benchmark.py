"""Blender capability benchmark: a small stylized scene, rendered with one engine.
Run: blender -b --factory-startup -P tools/blender_benchmark.py -- <WORKBENCH|EEVEE|CYCLES> <out.png> [samples]
"""
import bpy, sys, time, math

argv = sys.argv[sys.argv.index("--") + 1:]
engine, out = argv[0], argv[1]
samples = int(argv[2]) if len(argv) > 2 else 32

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene

def mat(name, rgb, rough=0.6, sss=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*rgb, 1)
    b.inputs["Roughness"].default_value = rough
    if sss:
        b.inputs["Subsurface Weight"].default_value = sss
    return m

ground = mat("ground", (0.45, 0.38, 0.26), 0.9)
skin = mat("head", (0.93, 0.90, 0.84), 0.5, 0.15)
coat = mat("coat", (0.80, 0.55, 0.12), 0.7)
leaf = mat("leaf", (0.20, 0.42, 0.15), 0.8)
bark = mat("bark", (0.30, 0.20, 0.12), 0.9)

bpy.ops.mesh.primitive_plane_add(size=40); bpy.context.object.data.materials.append(ground)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.55, location=(0, 0, 1.75), segments=48, ring_count=24)
bpy.ops.object.shade_smooth(); bpy.context.object.data.materials.append(skin)
bpy.ops.mesh.primitive_cylinder_add(radius=0.35, depth=1.0, location=(0, 0, 0.75))
bpy.context.object.data.materials.append(coat)
for i, (x, y) in enumerate([(-3, 4), (2.5, 6), (5, 3), (-6, 8), (8, 9)]):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.18, depth=2.4, location=(x, y, 1.2))
    bpy.context.object.data.materials.append(bark)
    bpy.ops.mesh.primitive_ico_sphere_add(radius=1.3, subdivisions=3, location=(x, y, 3.0))
    bpy.ops.object.shade_smooth(); bpy.context.object.data.materials.append(leaf)

bpy.ops.object.light_add(type="SUN", rotation=(math.radians(50), 0, math.radians(35)))
bpy.context.object.data.energy = 3.5
bpy.context.object.data.color = (1.0, 0.86, 0.68)
bpy.ops.object.light_add(type="AREA", location=(-3, -3, 3))
bpy.context.object.data.energy = 150; bpy.context.object.data.size = 3
bpy.context.object.data.color = (0.7, 0.8, 1.0)

world = bpy.data.worlds.new("w"); sc.world = world; world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.45, 0.6, 0.8, 1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.6

bpy.ops.object.camera_add(location=(0, -7.5, 1.9), rotation=(math.radians(88), 0, 0))
sc.camera = bpy.context.object
bpy.context.object.data.lens = 45
bpy.context.object.data.dof.use_dof = True
bpy.context.object.data.dof.focus_distance = 7.5
bpy.context.object.data.dof.aperture_fstop = 2.8

sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
sc.render.filepath = out
sc.render.image_settings.file_format = "PNG"
if engine == "CYCLES":
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = samples
    sc.cycles.use_denoising = "OPENIMAGEDENOISE" in [i.identifier for i in sc.cycles.bl_rna.properties["denoiser"].enum_items]
    try:
        sc.cycles.denoiser = "OPENIMAGEDENOISE"
    except Exception as e:
        print("OIDN unavailable:", e)
elif engine == "EEVEE":
    sc.render.engine = "BLENDER_EEVEE"
    sc.eevee.taa_render_samples = samples
    sc.eevee.use_soft_shadows = True
    sc.eevee.use_gtao = True
else:
    sc.render.engine = "BLENDER_WORKBENCH"

t = time.time()
bpy.ops.render.render(write_still=True)
print(f"BENCH {engine} samples={samples} seconds={time.time() - t:.1f}")
