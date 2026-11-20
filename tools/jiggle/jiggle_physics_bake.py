"""Jiggle Physics bake: apply naelstrof/blender-jiggle-physics (Wiggle 2 fork,
Unity JigglePhysics verlet solver) to a mocap action.

Usage: blender -b <in.blend> --python jiggle_physics_bake.py -- <out.blend> <action_name> <config>
config: preset values from the addon's own shipped presets (Breast.py / Tail.py).
The source action is duplicated first so rest-pose keys never pollute it.
Verification: SHA-256 fcurve digest of all NON-jiggle bones must be identical
between source action and baked action; face bones must carry no curves.
"""
import bpy, sys, hashlib, json

BREAST_PRESET = dict(jiggle_root_elasticity=0.9, jiggle_angle_elasticity=0.8,
                     jiggle_length_elasticity=0.9, jiggle_elasticity_soften=0.5,
                     jiggle_gravity=0.0, jiggle_blend=1.0, jiggle_air_drag=0.0,
                     jiggle_friction=0.1)
TAIL_PRESET = dict(jiggle_root_elasticity=0.9, jiggle_angle_elasticity=0.6,
                   jiggle_length_elasticity=0.9, jiggle_elasticity_soften=0.1,
                   jiggle_gravity=0.5, jiggle_blend=1.0, jiggle_air_drag=0.2,
                   jiggle_friction=0.4)

def digest(action, exclude):
    h = hashlib.sha256(); n = 0
    for fc in action.fcurves:
        dp = fc.data_path
        if any(f'pose.bones["{e}"]' in dp for e in exclude):
            continue
        h.update(dp.encode()); h.update(str(fc.array_index).encode())
        for kp in fc.keyframe_points:
            h.update(f"{kp.co[0]:.4f},{kp.co[1]:.6f};".encode()); n += 1
    return h.hexdigest(), n

def main():
    argv = sys.argv[sys.argv.index("--") + 1:]
    out_path, action_name, config = argv[0], argv[1], argv[2]
    src = bpy.data.actions[action_name]
    src.use_fake_user = True
    arm = next((o for o in bpy.data.objects if o.type == "ARMATURE"
                and o.animation_data and o.animation_data.action == src),
               None)
    if arm is None:
        arm = max((o for o in bpy.data.objects if o.type == "ARMATURE"),
                  key=lambda o: len(o.data.bones))
    arm.animation_data.action = src
    print("ARMATURE:", arm.name)

    bone_names = {b.name for b in arm.data.bones}
    if config == "scarlett":
        breast = [f"DEF-breast.{s}{x}" for s in ("L", "R") for x in ("", ".001", ".002", ".003")]
        butt = [f"Butt_{s}{x}" for s in ("L", "R") for x in ("", ".001", ".002", ".003", ".004")]
        tail = sorted(n for n in bone_names if n.startswith("DEF-tail"))
        groups = [(breast, BREAST_PRESET), (butt, BREAST_PRESET), (tail, TAIL_PRESET)]
    elif config == "star":
        flesh = ["Jiggle_Breast.L", "Jiggle_Breast.R", "Jiggle_Belly",
                 "Jiggle_Thigh.L", "Jiggle_Thigh.R", "Jiggle_Glute.L", "Jiggle_Glute.R"]
        groups = [(flesh, BREAST_PRESET)]
    else:
        raise SystemExit(f"unknown config {config}")
    jiggle = [n for g, _ in groups for n in g if n in bone_names]
    missing = [n for g, _ in groups for n in g if n not in bone_names]
    print("JIGGLE BONES:", jiggle)
    if missing: print("MISSING (skipped):", missing)

    # work on a copy of the action
    work = src.copy(); work.name = src.name + "+JP"
    arm.animation_data.action = work
    sc = bpy.context.scene
    sc.frame_set(sc.frame_start)
    # rest-pose keys on jiggle bones at frame_start (addon requirement)
    for n in jiggle:
        pb = arm.pose.bones[n]
        pb.keyframe_insert("location", frame=sc.frame_start)
        if pb.rotation_mode == "QUATERNION":
            pb.keyframe_insert("rotation_quaternion", frame=sc.frame_start)
        else:
            pb.keyframe_insert("rotation_euler", frame=sc.frame_start)
    # enable + params
    for bones, preset in groups:
        for n in bones:
            if n not in bone_names: continue
            pb = arm.pose.bones[n]
            pb.jiggle.enable = True
            for k, v in preset.items():
                setattr(pb, k, v)
    sc.jiggle.enable = True
    sc.jiggle.preroll = 24
    sc.jiggle.bake_overwrite = False
    before, nb = digest(src, jiggle)
    arm.jiggle.enable = True
    bpy.context.view_layer.objects.active = arm
    arm.select_set(True)
    bpy.ops.object.mode_set(mode="POSE")
    bpy.ops.armature.jiggle_bake()
    bpy.ops.object.mode_set(mode="OBJECT")
    baked = arm.animation_data.action
    print("BAKED ACTION:", baked.name, "fcurves:", len(baked.fcurves))
    after, na = digest(baked, jiggle)
    print(f"NON-JIGGLE DIGEST src={before[:16]} ({nb} keys) baked={after[:16]} ({na} keys) MATCH={before == after}")
    face = [fc.data_path for fc in baked.fcurves if any(w in fc.data_path.lower() for w in
            ("brow", "lid", "jaw", "lip", "nose", "cheek", "tongue", "eye"))]
    print("FACE FCURVES IN BAKED ACTION:", len(face))
    jcount = sum(1 for fc in baked.fcurves if any(f'pose.bones["{n}"]' in fc.data_path for n in jiggle))
    print("JIGGLE FCURVES IN BAKED ACTION:", jcount)
    if len(argv) > 3 and argv[3] == "nla":
        ad = arm.animation_data
        ad.action = None
        for tr_name, act in (("Base", src), ("Jiggle", baked)):
            tr = ad.nla_tracks.new(); tr.name = tr_name
            tr.strips.new(act.name, 1, act)
        print("NLA BUILT: Base=", src.name, " Jiggle=", baked.name)
    bpy.ops.wm.save_as_mainfile(filepath=out_path)
    print("SAVED:", out_path)

main()
