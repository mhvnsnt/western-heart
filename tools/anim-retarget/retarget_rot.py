#!/usr/bin/env python3
"""retarget_rot.py — rotation-delta retarget (scale-safe) of BVH/FBX/GLB motion onto a WH GLB rig.

Why a second retargeter: retarget_blender.py copies full source pose matrices, so a
unit mismatch (CMU BVH in inches vs. a cm/SFM-scaled glTF rig) leaks scale into every
bone and shreds the mesh (seen 2026-10-23 on cyborg-x.glb), and the source action leaks
into the export because CMU bone names equal WH names. This one transfers ROTATION ONLY,
in world space, per mapped bone, parent-first:

    R_target_pose = (R_src_pose @ R_src_rest^-1) @ R_target_rest

Each target bone keeps its own rest offset (bone lengths never change). Hips translation
is a delta from the first baked frame scaled by thigh+shin length ratio, or dropped with
--in-place. Only the retargeted action is exported.

Usage:
  xvfb-run -a env -u PYTHONPATH <blender> -b --python retarget_rot.py -- \\
     --source clip.bvh --target game/assets/models/cyborg-x.glb --out out.glb \\
     --bonemap tools/anim-retarget/bone_maps/cmu_to_wh.json --clip-name idle \\
     [--step 4] [--skip 120] [--max-frames 150] [--in-place] [--anim-only]
CMU BVH is 120 fps: --step 4 bakes 30 fps. --anim-only drops meshes (skeleton + clip,
a few hundred KB) — the game binds clips by bone name.
"""
import argparse, json, os, sys
import bpy
from mathutils import Matrix

a = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
p = argparse.ArgumentParser()
for k in ("--source", "--target", "--out", "--bonemap"): p.add_argument(k, required=True)
p.add_argument("--clip-name", default=None); p.add_argument("--fps", type=int, default=30)
p.add_argument("--step", type=int, default=1); p.add_argument("--max-frames", type=int, default=0)
p.add_argument("--skip", type=int, default=0, help="skip N source frames (CMU takes often open in T-pose)")
p.add_argument("--in-place", action="store_true"); p.add_argument("--anim-only", action="store_true")
args = p.parse_args(a)

bm = json.load(open(args.bonemap))["map"]
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene; sc.render.fps = args.fps

def imp(path):
    before = set(bpy.data.objects)
    ext = os.path.splitext(path)[1].lower()
    if ext == ".bvh": bpy.ops.import_anim.bvh(filepath=path, rotate_mode="NATIVE")
    elif ext == ".fbx": bpy.ops.import_scene.fbx(filepath=path)
    else: bpy.ops.import_scene.gltf(filepath=path)
    new = [o for o in bpy.data.objects if o not in before]
    return [o for o in new if o.type == "ARMATURE"][0], new

src, _ = imp(args.source)
src_action = src.animation_data.action
tgt, tgt_objs = imp(args.target)
if tgt.animation_data: tgt.animation_data.action = None
for pb in tgt.pose.bones:
    pb.matrix_basis = Matrix.Identity(4); pb.rotation_mode = "QUATERNION"
bpy.context.view_layer.update()

def wq(arm, M): return (arm.matrix_world @ M).to_quaternion()
pairs = []
for s in src.data.bones:
    t = bm.get(s.name)
    if t and t in tgt.data.bones:
        pairs.append((s.name, t, wq(src, s.matrix_local), wq(tgt, tgt.data.bones[t].matrix_local)))
depth = lambda b: 0 if b.parent is None else 1 + depth(b.parent)
pairs.sort(key=lambda x: depth(tgt.data.bones[x[1]]))
print(f"mapped {len(pairs)} bones: {[q[1] for q in pairs]}")

f0, f1 = [int(x) for x in src_action.frame_range]
f0 += args.skip
if args.max_frames: f1 = min(f1, f0 + args.max_frames * args.step - 1)
def leg(arm, names):
    b = [arm.data.bones.get(n) for n in names]
    if not all(b): return None
    return sum(((arm.matrix_world @ x.tail_local) - (arm.matrix_world @ x.head_local)).length for x in b)
ls = leg(src, ["LeftUpLeg", "LeftLeg"]); lt = leg(tgt, ["LeftUpLeg", "LeftLeg"])
root_scale = (lt / ls) if (ls and lt) else 0.0
print(f"root scale {root_scale:.5f}")

act = bpy.data.actions.new(args.clip_name or os.path.basename(args.source))
tgt.animation_data_create(); tgt.animation_data.action = act
tw_inv = tgt.matrix_world.to_quaternion().inverted()
tw3_inv = tgt.matrix_world.to_3x3().inverted()
hip0 = None
for fr in range(f0, f1 + 1, args.step):
    sc.frame_set(fr)
    kf = 1 + (fr - f0) // args.step
    for s_name, t_name, Rs_rest, Rt_rest in pairs:
        sp = src.pose.bones[s_name]; tp = tgt.pose.bones[t_name]
        Ra = tw_inv @ ((wq(src, sp.matrix) @ Rs_rest.inverted()) @ Rt_rest)
        bpy.context.view_layer.update()
        head = tp.matrix.to_translation()
        if t_name == "Hips" and not args.in_place and root_scale:
            sw = src.matrix_world @ sp.head
            if hip0 is None: hip0 = sw.copy()
            head = tgt.data.bones["Hips"].head_local + tw3_inv @ ((sw - hip0) * root_scale)
        tp.matrix = Matrix.LocRotScale(head, Ra, tp.matrix.to_scale())
        bpy.context.view_layer.update()
        tp.keyframe_insert("rotation_quaternion", frame=kf)
        if t_name == "Hips": tp.keyframe_insert("location", frame=kf)
sc.frame_start, sc.frame_end = 1, 1 + (f1 - f0) // args.step
for o in list(bpy.data.objects):
    if o not in tgt_objs: bpy.data.objects.remove(o, do_unlink=True)
for x in list(bpy.data.actions):
    if x != act: bpy.data.actions.remove(x)
if args.anim_only:
    for o in list(bpy.data.objects):
        if o.type == "MESH": bpy.data.objects.remove(o, do_unlink=True)
bpy.ops.object.select_all(action="SELECT")
bpy.ops.export_scene.gltf(filepath=args.out, export_format="GLB", use_selection=True,
    export_animations=True, export_frame_range=True, export_anim_single_armature=True,
    export_skins=True, export_morph=False)
print(f"WROTE {args.out} frames={sc.frame_end} bones={len(pairs)}")
