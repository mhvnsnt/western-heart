"""tools/auto_rig/reorient_static.py — stand a lying (Z-up) static upright before rigging.

Blender 4.0.2:  blender -b --factory-startup --python tools/auto_rig/reorient_static.py -- IN.glb OUT.glb [deg_x]

The SmutBase extractor outputs (tools/blender17-extract) come out Z-up: in glTF the head points +Z and the
front -Y, so in the game they lie on their backs. Rotating about glTF X by -90 deg (the default) stands them
up facing +Z. Read the four-view renders first (+Z/+X/-Z/-X cameras) to confirm the axis; never guess.
The original file is never modified. IN must be plain glTF (decode meshopt with tools/anim/gltf_codec.mjs).
Then rig: tools/auto_rig/rig_tripo_static.py --in OUT.glb --facing +Z.
"""
import math
import sys

import bpy

argv = sys.argv[sys.argv.index("--") + 1:]
inp, out = argv[0], argv[1]
deg = float(argv[2]) if len(argv) > 2 else -90.0
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=inp)
roots = [o for o in bpy.context.scene.objects if o.parent is None]
for o in bpy.context.scene.objects:
    o.select_set(o in roots)
bpy.context.view_layer.objects.active = roots[0]
# glTF X == Blender X, so the same angle applies.
for o in roots:
    o.rotation_mode = "XYZ"
    o.rotation_euler.x += math.radians(deg)
for o in bpy.context.scene.objects:
    o.select_set(o.type == "MESH")
bpy.context.view_layer.objects.active = next(o for o in bpy.context.scene.objects if o.type == "MESH")
bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
# feet on the floor: lowest vertex to y=0 (Blender z=0)
lo = min((o.matrix_world @ v.co).z for o in bpy.context.scene.objects if o.type == "MESH" for v in o.data.vertices)
for o in roots:
    o.location.z -= lo
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_apply=True)
print("reoriented", inp, "->", out, "deg_x", deg, "floor shift", -lo)
