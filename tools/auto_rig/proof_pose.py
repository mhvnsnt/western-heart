"""tools/auto_rig/proof_pose.py — Blender posed proof renders.

Poses named bones by fixed angles and renders front/back/side, so a
weight fix can be checked BY EYE: a bone with no skin weight (a dead
joint) moves nothing when posed; after weight_cleanup revives it, the
body part follows. Rest-pose renders cannot show this — weights do not
change the rest pose.

    xvfb-run -a env -u PYTHONPATH $BLENDER -b --factory-startup \
        --python proof_pose.py -- MODEL.glb OUTDIR \
        BoneName:axis:degrees [BoneName:axis:degrees ...]

axis is the pose bone's local axis letter (X/Y/Z). Workbench engine,
same camera set as render_poses.py.
"""
import bpy
import math
import os
import sys

argv = sys.argv[sys.argv.index("--") + 1:]
inp, outdir = argv[0], argv[1]
poses = []
for spec in argv[2:]:
    bone, axis, deg = spec.split(":")
    poses.append((bone, axis.upper(), math.radians(float(deg))))

os.makedirs(outdir, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=inp)
scn = bpy.context.scene
arm = [o for o in scn.objects if o.type == "ARMATURE"][0]
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode="POSE")
for bone_name, axis, ang in poses:
    pb = arm.pose.bones.get(bone_name)
    if pb is None:
        print("MISSING_BONE", bone_name)
        continue
    pb.rotation_mode = "XYZ"
    e = list(pb.rotation_euler)
    e["XYZ".index(axis)] = ang
    pb.rotation_euler = e
bpy.ops.object.mode_set(mode="OBJECT")

scn.render.engine = "BLENDER_WORKBENCH"
scn.display.shading.light = "STUDIO"
scn.display.shading.color_type = "TEXTURE"
scn.render.resolution_x = 520
scn.render.resolution_y = 700
cd = bpy.data.cameras.new("c")
cd.type = "ORTHO"
cd.ortho_scale = 2.2
cam = bpy.data.objects.new("c", cd)
scn.collection.objects.link(cam)
scn.camera = cam
views = {"front": ((0, 5, 0.95), (math.radians(90), 0, math.radians(180))),
         "back": ((0, -5, 0.95), (math.radians(90), 0, 0)),
         "side": ((5, 0, 0.95), (math.radians(90), 0, math.radians(90)))}
for name, (loc, rot) in views.items():
    cam.location = loc
    cam.rotation_euler = rot
    scn.render.filepath = os.path.join(outdir, f"posed_{name}.png")
    bpy.ops.render.render(write_still=True)
print("POSE_PROOF_DONE")
