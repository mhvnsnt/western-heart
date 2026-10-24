"""Star: retarget CMU lambada BVH onto StarRig — local-rest-relative delta
math copied from tools/anim-retarget/retarget_def_rig.py (PR #364), the method
that produced Scarlett's verified MocapRetarget action:
  rel = S_local_rest^-1 @ (P_src_pose^-1 @ S_pose)
  M   = P_tgt_set @ T_local @ rel          (armature-space target pose)
  basis = bone.matrix_local^-1 @ P_rest @ P_set^-1 @ M
Root: rotation = T_rest_rot @ (S_rest^-1 @ S_pose)_rot; translation pinned
in-plane, vertical bob scaled by leg-length ratio.
In: star-jiggle-baked-v3.blend. Out: star_delta.blend (action MocapRetarget).
"""
import bpy, sys
from mathutils import Matrix, Vector

argv = sys.argv[sys.argv.index("--") + 1:]
SRC, BVH, OUT = argv[0], argv[1], argv[2]

PAIRS = [("Hips", "Hips"), ("LowerBack", "Spine"), ("Spine", "Spine1"),
         ("Spine1", "Spine2"), ("Neck", "Neck"), ("Head", "Head"),
         ("LeftShoulder", "Shoulder.L"), ("LeftArm", "UpperArm.L"),
         ("LeftForeArm", "ForeArm.L"), ("LeftHand", "Hand.L"),
         ("RightShoulder", "Shoulder.R"), ("RightArm", "UpperArm.R"),
         ("RightForeArm", "ForeArm.R"), ("RightHand", "Hand.R"),
         ("LeftUpLeg", "UpLeg.L"), ("LeftLeg", "Leg.L"),
         ("LeftFoot", "Foot.L"), ("LeftToeBase", "ToeBase.L"),
         ("RightUpLeg", "UpLeg.R"), ("RightLeg", "Leg.R"),
         ("RightFoot", "Foot.R"), ("RightToeBase", "ToeBase.R")]

bpy.ops.wm.open_mainfile(filepath=SRC)
tgt = bpy.data.objects["StarRig"]
if tgt.animation_data and tgt.animation_data.action:
    old = tgt.animation_data.action
    tgt.animation_data.action = None
    bpy.data.actions.remove(old)

before = set(bpy.data.objects)
bpy.ops.import_anim.bvh(filepath=BVH, rotate_mode="NATIVE")
src = next(o for o in bpy.data.objects if o not in before and o.type == "ARMATURE")
sact = src.animation_data.action
f0, f1 = [int(x) for x in sact.frame_range]
n = f1 - f0 + 1
print(f"SOURCE {src.name} frames {f0}..{f1}")

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
root_scale = leg_len(tgt, ["Hips", "UpLeg.L", "Leg.L", "Foot.L"]) / \
             max(leg_len(src, ["Hips", "LeftUpLeg", "LeftLeg", "LeftFoot"]), 1e-6)
print("ROOT SCALE:", round(root_scale, 4))

bpy.context.view_layer.objects.active = tgt
tgt.select_set(True)
bpy.ops.object.mode_set(mode="POSE")
for pb in tgt.pose.bones:
    pb.rotation_mode = "QUATERNION"
if not tgt.animation_data:
    tgt.animation_data_create()
action = bpy.data.actions.new("MocapRetarget")
action.use_fake_user = True
tgt.animation_data.action = action

scene = bpy.context.scene
hips_pose0 = None
for i, f in enumerate(range(f0, f1 + 1)):
    out_f = i + 1
    scene.frame_set(f)
    bpy.context.view_layer.update()
    set_mats = {}
    for (s_name, s_parent, t_name, t_parent,
         S_local_rest_inv, T_local, _d, S_rest_inv, T_rest) in pairs:
        s_pb = src.pose.bones[s_name]
        t_pb = tgt.pose.bones[t_name]
        if s_name == "Hips":
            D = S_rest_inv @ s_pb.matrix
            _dl, drot, _ds = D.decompose()
            if hips_pose0 is None:
                hips_pose0 = s_pb.matrix.translation.copy()
            T_loc, T_rot, _s = T_rest.decompose()
            dz = (s_pb.matrix.translation.z - hips_pose0.z) * root_scale
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
print("RETARGET DONE:", action.name, "fcurves:", len(action.fcurves), "range:", action.frame_range[:])
try:
    bpy.ops.wm.save_as_mainfile(filepath=OUT)
    print("SAVED (with src in scene):", OUT)
except RuntimeError as e:
    print("SAVE WITH SRC FAILED:", e)
    bpy.data.objects.remove(src, do_unlink=True)
    bpy.ops.wm.save_as_mainfile(filepath=OUT)
    print("SAVED (after src removal):", OUT)
