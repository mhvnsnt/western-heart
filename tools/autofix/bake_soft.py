"""Soft-jiggle re-bake (one-shot autofix).
Base action prep (scripted, no hand edits):
  Scarlett: copy MocapRetarget -> strip ORG-/MCH- duplicate-layer curves ->
            strip the soft-chain ROOT curves (DEF-breast .000/.001, Butt .000/.001)
            so Jiggle Physics owns the whole soft chains.
  Star:     MocapRetarget as-is (its Jiggle_* bones are not keyed by base).
Jiggle Physics (naelstrof, GPL, Blender Extensions) with SOFT settings -
the prior proofs used the addon's stiff Breast preset (root elasticity 0.9)
which suppresses visible secondary motion. These values loosen the return
spring so the jiggle actually reads on screen, while length elasticity stays
high so bones do not stretch.
Usage (Blender 4.2): blender -b <in.blend> --python bake_soft.py -- <out.blend> <char>
"""
import bpy, sys, hashlib

SOFT_FLESH = dict(jiggle_root_elasticity=0.25, jiggle_angle_elasticity=0.35,
                  jiggle_length_elasticity=0.95, jiggle_elasticity_soften=0.3,
                  jiggle_gravity=0.35, jiggle_blend=1.0, jiggle_air_drag=0.05,
                  jiggle_friction=0.05)
SOFT_TAIL = dict(jiggle_root_elasticity=0.3, jiggle_angle_elasticity=0.4,
                 jiggle_length_elasticity=0.95, jiggle_elasticity_soften=0.2,
                 jiggle_gravity=0.5, jiggle_blend=1.0, jiggle_air_drag=0.1,
                 jiggle_friction=0.15)

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

def strip_bones(action, bones):
    rm = [fc for fc in action.fcurves if '"' in fc.data_path and fc.data_path.split('"')[1] in bones]
    for fc in rm:
        action.fcurves.remove(fc)
    return len(rm)

def strip_prefixes(action, prefixes):
    rm = [fc for fc in action.fcurves if '"' in fc.data_path and fc.data_path.split('"')[1].startswith(prefixes)]
    for fc in rm:
        action.fcurves.remove(fc)
    return len(rm)

def main():
    argv = sys.argv[sys.argv.index("--") + 1:]
    out_path, char = argv[0], argv[1]
    # enable Jiggle Physics extension if present
    try:
        bpy.ops.preferences.addon_enable(module="bl_ext.blender_org.jiggle_physics")
        print("JP extension enabled")
    except Exception as e:
        print("JP enable note:", e)
    for o in bpy.data.objects:
        o.hide_viewport = False; o.hide_render = False

    if char == "scarlett":
        arm = bpy.data.objects["RIG-SCARLETT"]
        src = next(a for a in bpy.data.actions if a.name.startswith("MocapRetarget"))
        base = src.copy(); base.name = "BaseDelta"
        # NOTE: no ORG-/MCH- strip — in the delta-retargeted action those
        # follower curves are load-bearing parents of the DEF chains
        # (the de-layering hypothesis was A/B-refuted: identical deformation).
        soft_roots = [f"DEF-breast.{s}{x}" for s in ("L", "R") for x in ("", ".001")] + \
                     [f"Butt_{s}{x}" for s in ("L", "R") for x in ("", ".001")]
        n2 = strip_bones(base, set(soft_roots))
        print(f"BaseDelta: stripped {n2} soft-root curves (delta action keys none); {len(base.fcurves)} remain")
        breast = [f"DEF-breast.{s}{x}" for s in ("L", "R") for x in ("", ".001", ".002", ".003")]
        butt = [f"Butt_{s}{x}" for s in ("L", "R") for x in ("", ".001", ".002", ".003", ".004")]
        tail = sorted(n for n in (b.name for b in arm.data.bones) if n.startswith("DEF-tail"))
        groups = [(breast, SOFT_FLESH), (butt, SOFT_FLESH), (tail, SOFT_TAIL)]
        # DQS on all armature modifiers (carried into the saved file)
        for ob in bpy.data.objects:
            if ob.type == "MESH":
                for m in ob.modifiers:
                    if m.type == "ARMATURE":
                        m.use_deform_preserve_volume = False
    elif char == "star":
        arm = bpy.data.objects["StarRig"]
        base = next(a for a in bpy.data.actions if a.name.startswith("MocapRetarget"))
        flesh = ["Jiggle_Breast.L", "Jiggle_Breast.R", "Jiggle_Belly",
                 "Jiggle_Thigh.L", "Jiggle_Thigh.R", "Jiggle_Glute.L", "Jiggle_Glute.R"]
        groups = [(flesh, SOFT_FLESH)]
        for ob in bpy.data.objects:
            if ob.type == "MESH":
                for m in ob.modifiers:
                    if m.type == "ARMATURE" and m.object == arm:
                        m.use_deform_preserve_volume = False
    else:
        raise SystemExit(f"unknown char {char}")

    bone_names = {b.name for b in arm.data.bones}
    jiggle = [n for g, _ in groups for n in g if n in bone_names]
    print("JIGGLE BONES:", jiggle)
    base.use_fake_user = True
    if arm.animation_data is None:
        arm.animation_data_create()
    arm.animation_data.action = base
    sc = bpy.context.scene
    sc.frame_set(sc.frame_start)
    for n in jiggle:
        pb = arm.pose.bones[n]
        pb.keyframe_insert("location", frame=sc.frame_start)
        if pb.rotation_mode == "QUATERNION":
            pb.keyframe_insert("rotation_quaternion", frame=sc.frame_start)
        else:
            pb.keyframe_insert("rotation_euler", frame=sc.frame_start)
    work = base  # bake writes into a new action via addon (bake_overwrite False -> new action)
    for bones, preset in groups:
        for n in bones:
            if n not in bone_names:
                continue
            pb = arm.pose.bones[n]
            pb.jiggle.enable = True
            for k, v in preset.items():
                setattr(pb, k, v)
    sc.jiggle.enable = True
    sc.jiggle.preroll = 24
    sc.jiggle.bake_overwrite = False
    arm.jiggle.enable = True
    before, nb = digest(base, jiggle)
    bpy.context.view_layer.objects.active = arm
    arm.select_set(True)
    bpy.ops.object.mode_set(mode="POSE")
    bpy.ops.armature.jiggle_bake()
    bpy.ops.object.mode_set(mode="OBJECT")
    baked = arm.animation_data.action
    print("BAKED ACTION:", baked.name, "fcurves:", len(baked.fcurves))
    after, na = digest(baked, jiggle)
    print(f"NON-JIGGLE DIGEST base={before[:16]} ({nb}) baked={after[:16]} ({na}) MATCH={before == after}")
    # final stack: base as active is replaced by NLA (Base track + Jiggle track)
    ad = arm.animation_data
    ad.action = None
    for tr_name, act in (("Base", base), ("Jiggle", baked)):
        tr = ad.nla_tracks.new(); tr.name = tr_name
        tr.strips.new(act.name, 1, act)
    bpy.ops.wm.save_as_mainfile(filepath=out_path)
    print("SAVED:", out_path)

main()
