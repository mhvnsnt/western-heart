#!/usr/bin/env python3
"""
retarget_blender.py — retarget a source animation (Mixamo/Rokoko FBX or BVH)
onto a Western Heart-rigged GLB, headless.

Method (studio-standard "rest-relative delta" retarget):
  For every mapped bone, per frame:
      T_pose_world = T_rest_world @ S_rest_world^-1 @ S_pose_world
  i.e. the target bone reproduces the source bone's deformation *relative to
  its own rest pose*. Root (Hips) translation is scaled by the hip-height
  ratio so a tall source doesn't make a short target moon-walk.

WH skeletons are Mixamo-named already (tools/auto_rig/backends/
skeleton_template.json), so Mixamo sources map 1:1; the bone map only
strips `mixamo:` prefixes and drops helper bones.

Usage (headless):
  xvfb-run -a env -u PYTHONPATH <blender> -b --python retarget_blender.py -- \\
      --source anims/punch.fbx --target game/assets/models/demonio-body.glb \\
      --out game/assets/models/demonio-body@Punch.glb \\
      --bonemap tools/anim-retarget/bone_maps/mixamo_to_wh.json \\
      [--clip-name Punch] [--fps 30] [--in-place]

--in-place: zero the Hips translation track (game pins it anyway; in-place
clips are required by AssetManager).
"""
import argparse, json, math, os, sys

import bpy
from mathutils import Matrix

# ---------------------------------------------------------------- args

def parse_args():
    # Blender eats argv; ours follow the literal `--`
    argv = sys.argv
    argv = argv[argv.index("--") + 1:] if "--" in argv else []
    p = argparse.ArgumentParser()
    p.add_argument("--source", required=True, help="FBX or BVH with the animation")
    p.add_argument("--target", required=True, help="WH-rigged GLB (the mesh + skeleton)")
    p.add_argument("--out", required=True, help="output animated GLB")
    p.add_argument("--bonemap", required=True)
    p.add_argument("--clip-name", default=None)
    p.add_argument("--fps", type=int, default=30)
    p.add_argument("--in-place", action="store_true",
                   help="zero Hips translation (in-place clip)")
    return p.parse_args(argv)

# ---------------------------------------------------------------- helpers

def deselect_all():
    bpy.ops.object.select_all(action="DESELECT")

def import_source(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".fbx":
        bpy.ops.import_scene.fbx(filepath=path)
    elif ext == ".bvh":
        bpy.ops.import_anim.bvh(filepath=path)
    else:
        raise SystemExit(f"unsupported source format: {ext}")
    arms = [o for o in bpy.context.scene.objects if o.type == "ARMATURE"]
    if not arms:
        raise SystemExit("no armature found in source file")
    # FBX can import several armatures; take the one with an action / most bones
    arms.sort(key=lambda a: len(a.data.bones), reverse=True)
    return arms[0]

def import_target_glb(path):
    bpy.ops.import_scene.gltf(filepath=path)
    arms = [o for o in bpy.context.scene.objects if o.type == "ARMATURE"]
    if not arms:
        raise SystemExit("no armature found in target GLB")
    arms.sort(key=lambda a: len(a.data.bones), reverse=True)
    return arms[0]

def strip_prefix(name, prefixes):
    for pre in prefixes:
        if name.startswith(pre):
            return name[len(pre):]
    return name

def rest_world(arm, bone_name):
    """Rest matrix of a bone in armature space."""
    b = arm.data.bones[bone_name]
    return arm.matrix_world @ b.matrix_local

def hip_height(arm, hips_name="Hips"):
    b = arm.data.bones.get(hips_name)
    if b is None:
        return 1.0
    return (arm.matrix_world @ b.head_local).z

# ---------------------------------------------------------------- main

def main():
    args = parse_args()

    with open(args.bonemap) as f:
        bm = json.load(f)
    bone_map = bm["map"]               # source name -> WH name (null = drop)
    prefixes = bm.get("strip_prefixes", [])

    # Clean scene, deterministic FPS
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    scene = bpy.context.scene
    scene.render.fps = args.fps

    src_arm = import_source(args.source)
    tgt_arm = import_target_glb(args.target)

    # Normalize: both armatures at origin, scale 1
    for arm in (src_arm, tgt_arm):
        arm.location = (0, 0, 0)
        arm.rotation_euler = (0, 0, 0)
        arm.scale = (1, 1, 1)
    bpy.context.view_layer.update()

    # Build the mapped pair list (source bone -> target bone)
    src_bones = {b.name: b for b in src_arm.data.bones}
    tgt_bones = {b.name: b for b in tgt_arm.data.bones}
    pairs = []  # (src_name, tgt_name, S_rest_world_inv, T_rest_world)
    unmapped_src = []
    for s_name in src_bones:
        clean = strip_prefix(s_name, prefixes)
        t_name = bone_map.get(clean, bone_map.get(s_name))
        if not t_name:
            unmapped_src.append(s_name)
            continue
        if t_name not in tgt_bones:
            print(f"WARN: target has no bone '{t_name}' (source '{s_name}') — skipping")
            continue
        S = rest_world(src_arm, s_name)
        T = rest_world(tgt_arm, t_name)
        pairs.append((s_name, t_name, S.inverted(), T))
    print(f"mapped {len(pairs)} bones; dropped {len(unmapped_src)} source helpers")

    # Frame range from the source action
    src_action = src_arm.animation_data.action if src_arm.animation_data else None
    if src_action is None:
        raise SystemExit("source armature has no action — nothing to retarget")
    f_start, f_end = [int(x) for x in src_action.frame_range]
    print(f"source frames {f_start}..{f_end} @ {args.fps}fps")

    # Root-motion scale = target hip height / source hip height
    root_scale = hip_height(tgt_arm) / max(hip_height(src_arm), 1e-6)
    print(f"root motion scale: {root_scale:.3f}")

    # Retarget onto the target armature
    deselect_all()
    tgt_arm.select_set(True)
    bpy.context.view_layer.objects.active = tgt_arm
    bpy.ops.object.mode_set(mode="POSE")
    for pb in tgt_arm.pose.bones:
        pb.rotation_mode = "QUATERNION"
    tgt_action = bpy.data.actions.new(name=args.clip_name or os.path.splitext(os.path.basename(args.source))[0])
    tgt_arm.animation_data_create()
    tgt_arm.animation_data.action = tgt_action

    for frame in range(f_start, f_end + 1):
        scene.frame_set(frame)
        bpy.context.view_layer.update()
        for s_name, t_name, S_inv, T_rest in pairs:
            s_pb = src_arm.pose.bones[s_name]
            t_pb = tgt_arm.pose.bones[t_name]
            # T_pose = T_rest @ S_rest^-1 @ S_pose   (armature space)
            M = T_rest @ S_inv @ s_pb.matrix
            if args.in_place and t_name == "Hips":
                # keep rotation, zero translation (bind-pose Hips position)
                loc, rot, scl = M.decompose()
                bind = (tgt_arm.matrix_world @ tgt_arm.data.bones["Hips"].matrix_local).decompose()[0]
                M = Matrix.Translation(bind) @ rot.to_matrix().to_4x4() @ Matrix.Diagonal(scl).to_4x4()
            elif t_name == "Hips":
                # scale root translation by hip-height ratio
                loc, rot, scl = M.decompose()
                M = Matrix.Translation(loc * root_scale) @ rot.to_matrix().to_4x4() @ Matrix.Diagonal(scl).to_4x4()
            t_pb.matrix = M
            t_pb.keyframe_insert(data_path="location", frame=frame)
            t_pb.keyframe_insert(data_path="rotation_quaternion", frame=frame)
            t_pb.keyframe_insert(data_path="scale", frame=frame)
    bpy.ops.object.mode_set(mode="OBJECT")

    # Remove the source rig — only the retargeted target ships
    def is_target_side(o):
        while o is not None:
            if o == tgt_arm:
                return True
            o = o.parent
        return False
    deselect_all()
    for o in list(bpy.context.scene.objects):
        if not is_target_side(o):
            bpy.data.objects.remove(o, do_unlink=True)
    bpy.context.view_layer.update()

    # Export: target only
    deselect_all()
    for o in bpy.context.scene.objects:
        keep = (o == tgt_arm) or (o.parent is not None and o.parent == tgt_arm)
        o.select_set(bool(keep))
    tgt_arm.select_set(True)
    bpy.context.view_layer.objects.active = tgt_arm
    bpy.ops.export_scene.gltf(
        filepath=args.out,
        export_format="GLB",
        use_selection=True,
        export_animations=True,
        export_frame_range=True,
        export_anim_single_armature=True,
        export_skins=True,
        export_morph=False,
    )
    print(f"WROTE {args.out}  ({f_end - f_start + 1} frames, {len(pairs)} bones)")

if __name__ == "__main__":
    main()
