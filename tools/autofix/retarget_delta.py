#!/usr/bin/env python3
"""retarget_delta.py — BVH -> rig retarget via LOCAL rest-relative deltas.

Generalized from the Star driver that produced Star's verified MocapRetarget
(anim-fix-work/tmp/star_retarget_delta.py). Per mapped bone, per frame:
    rel       = S_local_rest^-1 @ (P_src_pose^-1 @ S_pose)   (local joint delta)
    M         = P_tgt_set @ T_local_rest @ rel               (armature space)
    basis     = bone.matrix_local^-1 @ P_rest @ P_set^-1 @ M
Unlike world-delta retargeting (T_pose = T_rest @ S_rest^-1 @ S_pose), the
local formulation is rest-pose independent: it transfers joint motion, so a
source T-pose clip lands correctly on a target whose rest arms point down.

Pairs come from a bone-map JSON: {"pairs": [[src, tgt, note?], ...]}.
One source bone may drive several targets (mechanism followers use their own
rest matrices). Root (first pair whose src == --root-src): rotation from the
same delta decomposition; translation pinned in-plane, vertical bob scaled by
the leg-length ratio.

Usage (headless Blender):
  blender -b <target.blend> --python retarget_delta.py -- \
      --bvh clip.bvh --map bone_map.json --arm RIG-NAME --out out.blend \
      [--root-src Hips] [--legs Hips,DEF-thigh.L,DEF-shin.L,DEF-foot.L] \
      [--src-legs Hips,LeftUpLeg,LeftLeg,LeftFoot] [--action MocapRetarget]
"""
import argparse, json, sys
import bpy
from mathutils import Matrix, Vector


def parse_args():
    argv = sys.argv[sys.argv.index("--") + 1:]
    p = argparse.ArgumentParser()
    p.add_argument("--bvh", required=True)
    p.add_argument("--map", required=True)
    p.add_argument("--arm", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--root-src", default="Hips")
    p.add_argument("--legs", default="")
    p.add_argument("--src-legs", default="")
    p.add_argument("--action", default="MocapRetarget")
    return p.parse_args(argv)


args = parse_args()
pairs_json = json.load(open(args.map))["pairs"]
PAIRS = [(p[0], p[1]) for p in pairs_json]

tgt = bpy.data.objects[args.arm]
if tgt.animation_data and tgt.animation_data.action:
    tgt.animation_data.action = None
for o in bpy.data.objects:
    o.hide_viewport = False; o.hide_render = False

before = set(bpy.data.objects)
bpy.ops.import_anim.bvh(filepath=args.bvh, rotate_mode="NATIVE")
src = next(o for o in bpy.data.objects if o not in before and o.type == "ARMATURE")
sact = src.animation_data.action
f0, f1 = [int(x) for x in sact.frame_range]
print(f"SOURCE {src.name} frames {f0}..{f1}", flush=True)


def rest_world(arm, name):
    return arm.matrix_world @ arm.data.bones[name].matrix_local


def depth(bone):
    d = 0
    while bone.parent:
        d += 1; bone = bone.parent
    return d


pairs = []
for s_name, t_name in PAIRS:
    s_bone = src.data.bones[s_name]
    t_bone = tgt.data.bones[t_name]
    S_rest = rest_world(src, s_name)
    T_rest = rest_world(tgt, t_name)
    P_src_rest = rest_world(src, s_bone.parent.name) if s_bone.parent else Matrix()
    P_tgt_rest = rest_world(tgt, t_bone.parent.name) if t_bone.parent else Matrix()
    S_local_rest_inv = (P_src_rest.inverted() @ S_rest).inverted()
    T_local = P_tgt_rest.inverted() @ T_rest
    pairs.append((s_name, s_bone.parent.name if s_bone.parent else None,
                  t_name, t_bone.parent.name if t_bone.parent else None,
                  S_local_rest_inv, T_local, depth(t_bone),
                  S_rest.inverted(), T_rest))
pairs.sort(key=lambda p: p[6])
rest_arm = {b.name: rest_world(tgt, b.name) for b in tgt.data.bones}


def leg_len(arm, names):
    pts = [arm.matrix_world @ arm.data.bones[n].head_local for n in names]
    return sum((b - a).length for a, b in zip(pts, pts[1:]))


tgt_legs = args.legs.split(",") if args.legs else []
src_legs = args.src_legs.split(",") if args.src_legs else []
root_scale = 1.0
if tgt_legs and src_legs:
    root_scale = leg_len(tgt, tgt_legs) / max(leg_len(src, src_legs), 1e-6)
print("ROOT SCALE:", round(root_scale, 4), flush=True)

bpy.context.view_layer.objects.active = tgt
tgt.select_set(True)
bpy.ops.object.mode_set(mode="POSE")
for pb in tgt.pose.bones:
    pb.rotation_mode = "QUATERNION"
if not tgt.animation_data:
    tgt.animation_data_create()
action = bpy.data.actions.new(args.action)
action.use_fake_user = True
tgt.animation_data.action = action

scene = bpy.context.scene
root_pose0 = None
for i, f in enumerate(range(f0, f1 + 1)):
    out_f = i + 1
    scene.frame_set(f)
    bpy.context.view_layer.update()
    set_mats = {}
    for (s_name, s_parent, t_name, t_parent,
         S_local_rest_inv, T_local, _d, S_rest_inv, T_rest) in pairs:
        s_pb = src.pose.bones[s_name]
        t_pb = tgt.pose.bones[t_name]
        if s_name == args.root_src:
            # Root-driven targets (incl. mechanism followers like ORG-spine)
            # take the root path: the general path would mix BVH-object world
            # scale into the basis of parentless-source pairs and explode.
            D = S_rest_inv @ s_pb.matrix
            _dl, drot, _ds = D.decompose()
            if root_pose0 is None:
                root_pose0 = s_pb.matrix.translation.copy()
            T_loc, T_rot, _s = T_rest.decompose()
            dz = (s_pb.matrix.translation.z - root_pose0.z) * root_scale
            loc = Vector((T_loc.x, T_loc.y, T_loc.z + dz))
            M = Matrix.Translation(loc) @ (T_rot @ drot).to_matrix().to_4x4()
        else:
            P_src = src.pose.bones[s_parent].matrix if s_parent else Matrix()
            local_pose = P_src.inverted() @ s_pb.matrix
            rel = S_local_rest_inv @ local_pose
            if t_parent is None:
                P_tgt = Matrix()
            elif t_parent in set_mats:
                P_tgt = set_mats[t_parent]
            else:
                P_tgt = rest_arm[t_parent]
            M = P_tgt @ T_local @ rel
        if t_parent is None:
            P = Matrix(); PL = Matrix()
        elif t_parent in set_mats:
            P = set_mats[t_parent]; PL = rest_arm[t_parent]
        else:
            P = rest_arm[t_parent]; PL = rest_arm[t_parent]
        t_pb.matrix_basis = t_pb.bone.matrix_local.inverted() @ PL @ P.inverted() @ M
        t_pb.keyframe_insert(data_path="location", frame=out_f)
        t_pb.keyframe_insert(data_path="rotation_quaternion", frame=out_f)
        t_pb.keyframe_insert(data_path="scale", frame=out_f)
        set_mats[t_name] = M
bpy.ops.object.mode_set(mode="OBJECT")
print("RETARGET DONE:", action.name, "fcurves:", len(action.fcurves),
      "range:", action.frame_range[:], flush=True)
bpy.data.objects.remove(src, do_unlink=True)
bpy.ops.wm.save_as_mainfile(filepath=args.out)
print("SAVED:", args.out, flush=True)
