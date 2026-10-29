"""render_proof.py — headless Blender proof render of animated GLB(s) (side by side).
Usage: blender -b --python render_proof.py -- --glb a.glb [b.glb] --out /tmp/frames/f_ --frames 90 [--every 2]
Workbench engine; camera framed on armature joints, in front of the -Z-facing (glTF) rig."""
import bpy, sys, argparse
from mathutils import Vector
a = sys.argv[sys.argv.index("--")+1:]
p = argparse.ArgumentParser(); p.add_argument("--glb", nargs="+"); p.add_argument("--out"); p.add_argument("--frames", type=int, default=90); p.add_argument("--every", type=int, default=1); p.add_argument("--spacing", type=float, default=1.2); p.add_argument("--anim", nargs="*", default=[], help="optional anim-only GLB per model (same order) whose action is applied")
args = p.parse_args(a)
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
arms = []
for i, g in enumerate(args.glb):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=g)
    new = [o for o in bpy.data.objects if o not in before]
    for r in [o for o in new if o.parent is None]: r.location.x += (i - (len(args.glb)-1)/2) * args.spacing
    arm = [o for o in new if o.type == "ARMATURE"][0]; arms.append(arm)
    if i < len(args.anim):
        acts = set(bpy.data.actions)
        b2 = set(bpy.data.objects); bpy.ops.import_scene.gltf(filepath=args.anim[i])
        act = [x for x in bpy.data.actions if x not in acts][0]
        for o in [o for o in bpy.data.objects if o not in b2]: bpy.data.objects.remove(o, do_unlink=True)
        arm.animation_data_create(); arm.animation_data.action = act
sc.frame_start, sc.frame_end = 1, args.frames
sc.frame_set(1); bpy.context.view_layer.update()
pts = [arm.matrix_world @ pb.head for arm in arms for pb in arm.pose.bones]
mn = Vector((min(v.x for v in pts), min(v.y for v in pts), min(v.z for v in pts)))
mx = Vector((max(v.x for v in pts), max(v.y for v in pts), max(v.z for v in pts)))
ctr = (mn+mx)/2; h = max(mx.z-mn.z, mx.x-mn.x)
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(cam); sc.camera = cam
cam.location = ctr + Vector((h*0.5, -h*2.2, h*0.15))
cam.rotation_euler = (ctr - cam.location).to_track_quat('-Z', 'Y').to_euler()
sc.render.engine = "BLENDER_WORKBENCH"; sc.display.shading.light = "STUDIO"; sc.display.shading.color_type = "TEXTURE"
sc.render.resolution_x, sc.render.resolution_y = 480 * max(1, len(args.glb)), 540
sc.world = bpy.data.worlds.new("w"); sc.world.color = (0.12, 0.12, 0.14)
for f in range(1, args.frames+1, args.every):
    sc.frame_set(f); sc.render.filepath = f"{args.out}{f:04d}.png"; bpy.ops.render.render(write_still=True)
print("RENDERED", args.out)
