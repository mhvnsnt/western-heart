"""tools/auto_rig/render_poses.py — Blender workbench renders of a rigged GLB at given clip times.

Front / back / side orthographic views per time, textured, so a rig can be checked by eye
(tearing, sides, facing). Used by tools/auto_rig/rig_tripo_static.py (2026-10-21, Claude session).

    xvfb-run -a env -u PYTHONPATH blender -b --factory-startup --python render_poses.py -- \
        RIGGED.glb OUTDIR 0,1.2,1.7
"""
import bpy, sys, math, os
argv = sys.argv[sys.argv.index("--") + 1:]
inp, outdir = argv[0], argv[1]
times = [float(t) for t in argv[2].split(",")]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=inp)
scn = bpy.context.scene
arm = [o for o in scn.objects if o.type == "ARMATURE"][0]
act = arm.animation_data.action if arm.animation_data else None
fps = scn.render.fps
scn.render.engine = "BLENDER_WORKBENCH"; scn.display.shading.light = "STUDIO"; scn.display.shading.color_type = "TEXTURE"
scn.render.resolution_x = 520; scn.render.resolution_y = 700
cd = bpy.data.cameras.new("c"); cd.type = "ORTHO"; cd.ortho_scale = 2.2
cam = bpy.data.objects.new("c", cd); scn.collection.objects.link(cam); scn.camera = cam
views = {"front": ((0, 5, 0.95), (math.radians(90), 0, math.radians(180))), "back": ((0, -5, 0.95), (math.radians(90), 0, 0)), "side": ((5, 0, 0.95), (math.radians(90), 0, math.radians(90)))}
for t in times:
    scn.frame_set(int(round(t * fps)) + (int(act.frame_range[0]) if act else 0))
    for name, (loc, rot) in views.items():
        cam.location = loc; cam.rotation_euler = rot
        scn.render.filepath = os.path.join(outdir, f"pose_t{t:.2f}_{name}.png")
        bpy.ops.render.render(write_still=True)
print("POSE_DONE")
