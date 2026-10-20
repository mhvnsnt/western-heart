#!/usr/bin/env python3
"""
keemap_retarget.py — production retarget driver: mocap BVH -> DEF-skeleton
rig (RIG-SCARLETT family) THROUGH Keemap (nkeeline, GPL-3.0), headless.

This is the Keemap path of tools/anim-retarget/. It replaces the hand-rolled
rest-relative math of retarget_def_rig.py with Keemap's own operators:

  * Keemap matches each mapped destination bone's WORLD-space rotation to
    the source bone's world-space rotation, then applies a per-bone
    correction quaternion (KeeMapBoneOperators.SetBoneRotation).
  * Corrections are calibrated by Keemap itself at a shared reference pose
    (bpy.ops.wm.calc_correct_all_bones — "CALC ALL ROTLOC CORRECTIONS"):
    the source clip's first frame is the CMU bind/T-pose (all rotation
    channels zero) and the target starts at its rest pose, so the operator
    measures, per bone, the rotational offset between the two rigs and
    stores it in the bone mapping (CorrectionFactor / QuatCorrectionFactor).
  * The transfer runs Keemap's own frame loop
    (bpy.ops.wm.perform_animation_transfer -> wm.test_all_bones ->
    wm.test_set_rotation_of_bone), parents before children.
  * Root (Hips -> DEF-spine) additionally transfers position
    (set_bone_position, Keemap SINGLE_BONE_OFFSET) with Keemap's calibrated
    position correction. The source armature OBJECT is uniformly scaled by
    the leg-length ratio first, so world positions are comparable and
    Keemap's position gain stays 1.0 (the "match hip proportions first"
    step — the stretch fix from the Keemap lane notes).

The bone map is Keemap's native JSON (the same file the Keemap GUI reads
and writes via wm.keemap_read_file / wm.keemap_save_file):
bone_maps/cmu_to_scarlett_keemap.json — pairs identical to
cmu_to_scarlett_def.json (source CMU/MotionBuilder name -> Scarlett DEF
bone, mechanism parents included as followers). Committed corrections in
that file are identity; the driver calibrates live every run and can
write the calibrated map back out with --save-map.

STATUS (2026-10-20, proof run in tools/anim-retarget/proof/keemap-lambada/):
this driver drives Keemap correctly end-to-end, but vendored Keemap
v0.0.9's calibration is not self-consistent on Rigify DEF rigs (its
SetBoneRotation applies a world-space delta in pose space; the
rest-orientation compensation is commented out upstream) and the
output mesh collapses. Keemap output for DEF rigs must NOT ship;
see the proof dir's METRICS.md for the full evidence. The driver is
kept so the finding is reproducible and so Keemap can be re-evaluated
if upstream fixes the math or for world-aligned rigs.

STATUS (2026-10-20, proof run in tools/anim-retarget/proof/keemap-lambada/):
this driver drives Keemap correctly end-to-end, but vendored Keemap
v0.0.9's calibration is not self-consistent on Rigify DEF rigs (its
SetBoneRotation applies a world-space delta in pose space; the
rest-orientation compensation is commented out upstream) and the
output mesh collapses. Keemap output for DEF rigs must NOT ship;
see the proof dir's METRICS.md for the full evidence. The driver is
kept so the finding is reproducible and so Keemap can be re-evaluated
if upstream fixes the math or for world-aligned rigs.

Usage (headless, from repo root):
  xvfb-run -a env -u PYTHONPATH <blender> -b <target.blend> --python \
      tools/anim-retarget/keemap_retarget.py -- \
      --source clip.bvh --target-arm RIG-SCARLETT \
      --bonemap tools/anim-retarget/bone_maps/cmu_to_scarlett_keemap.json \
      --out out.blend [--glb-out out.glb] [--save-map calibrated.json] \
      [--start-frame 1261] [--num-frames 356] [--keyframe-every 5] \
      [--out-fps 24] [--no-root-position]

--start-frame/--num-frames/--keyframe-every address the SOURCE timeline
(Blender frames after BVH import at scene fps = source fps). The proof
run retargets CMU 55_02 frames 1261..1616 step 5: exactly the 72 frames
of lambada_loop.bvh (the clip the hand-rolled baseline used), resampled
to 24 fps on the output timeline (frames shifted to start at 1).
"""
import argparse, json, math, os, sys

import bpy
from mathutils import Matrix, Vector

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DEFAULT_KEEMAP_DIR = os.path.join(
    REPO_ROOT, "tools", "open-source", "blender-addons",
    "keemap-retargeting", "Source", "SourceFiles")


# ---------------------------------------------------------------- args

def parse_args():
    argv = sys.argv
    argv = argv[argv.index("--") + 1:] if "--" in argv else []
    p = argparse.ArgumentParser()
    p.add_argument("--source", required=True, help="BVH with the animation")
    p.add_argument("--target-arm", required=True, help="target armature object name")
    p.add_argument("--bonemap", required=True, help="Keemap-format bone mapping JSON")
    p.add_argument("--out", required=True, help="output .blend")
    p.add_argument("--glb-out", default=None, help="also export animated GLB here")
    p.add_argument("--save-map", default=None,
                   help="write the calibrated Keemap bone map JSON here")
    p.add_argument("--keemap-dir", default=DEFAULT_KEEMAP_DIR,
                   help="dir containing Keemap SourceFiles (__init__.py)")
    p.add_argument("--start-frame", type=int, default=1,
                   help="first source-timeline frame to transfer")
    p.add_argument("--num-frames", type=int, default=None,
                   help="source-timeline frames to span (default: to end of clip)")
    p.add_argument("--keyframe-every", type=int, default=1)
    p.add_argument("--out-fps", type=int, default=24)
    p.add_argument("--rotation-mode", default="QUATERNION",
                   choices=["QUATERNION", "EULER"])
    p.add_argument("--root-source", default="Hips")
    p.add_argument("--root-target", default="DEF-spine")
    p.add_argument("--no-root-position", action="store_true")
    return p.parse_args(argv)


# ---------------------------------------------------------------- keemap load

def load_keemap(keemap_dir):
    """Load the vendored Keemap addon exactly the way its own
    'Source/Code Load.py' does: SourceFiles on sys.path, DEBUG_MODE in
    sys.argv (so __init__ imports the modules as top-level names), then
    exec __init__.py — whose register() registers all classes, giving us
    scene.keemap_settings, scene.keemap_bone_mapping_list and the
    wm.* operators (perform_animation_transfer, calc_correct_all_bones,
    keemap_read_file / keemap_save_file)."""
    if keemap_dir not in sys.path:
        sys.path.append(keemap_dir)
    added = "DEBUG_MODE" not in sys.argv
    if added:
        sys.argv.append("DEBUG_MODE")
    init_py = os.path.join(keemap_dir, "__init__.py")
    with open(init_py) as f:
        code = compile(f.read(), init_py, "exec")
    exec(code, {"__name__": "__main__", "__file__": init_py})
    if added:
        sys.argv.remove("DEBUG_MODE")
    assert hasattr(bpy.types.Scene, "keemap_settings"), "Keemap did not register"
    print("KEEMAP loaded: operators wm.perform_animation_transfer / "
          "wm.calc_correct_all_bones available")


# ---------------------------------------------------------------- helpers

def bone_depth(bone):
    d, b = 0, bone
    while b.parent:
        d += 1
        b = b.parent
    return d


def leg_len(arm, names):
    pts = [arm.matrix_world @ arm.data.bones[n].head_local for n in names]
    return sum((b - a).length for a, b in zip(pts, pts[1:]))


# ---------------------------------------------------------------- main

def main():
    args = parse_args()
    scene = bpy.context.scene

    tgt = bpy.data.objects[args.target_arm]
    if tgt.animation_data:
        tgt.animation_data_clear()

    load_keemap(args.keemap_dir)

    # --- import mocap source at native fps so source frames are 1:1 ---
    with open(args.source) as f:
        head = f.read(200000)
    src_fps = 120
    for line in head.splitlines():
        if line.startswith("Frame Time:"):
            src_fps = round(1.0 / float(line.split(":")[1]))
            break
    scene.render.fps = src_fps
    before = set(bpy.data.objects)
    bpy.ops.import_anim.bvh(filepath=args.source, rotate_mode="NATIVE")
    src = next(o for o in bpy.data.objects
               if o not in before and o.type == "ARMATURE")
    src_action = src.animation_data.action
    f0, f1 = [int(x) for x in src_action.frame_range]
    print(f"source {src.name}: frames {f0}..{f1} @ {src_fps}fps, "
          f"{len(src.data.bones)} bones")

    # --- hip-proportion first: uniform-scale the source OBJECT by the
    # leg-length ratio so Keemap world positions are comparable (gain 1).
    src_leg = leg_len(src, ["Hips", "LeftUpLeg", "LeftLeg", "LeftFoot"])
    tgt_leg = leg_len(tgt, ["DEF-spine", "DEF-thigh.L", "DEF-shin.L", "DEF-foot.L"])
    ratio = tgt_leg / max(src_leg, 1e-9)
    src.scale = (ratio, ratio, ratio)
    bpy.context.view_layer.update()
    print(f"leg lengths src={src_leg:.4f} tgt={tgt_leg:.4f} "
          f"source object scale={ratio:.6f}")

    # --- Keemap settings + bone mapping (its native file format) ---
    # NOTE: wm.keemap_read_file overwrites the settings from the file, so
    # rig names / mode are (re)applied AFTER the read.
    km = scene.keemap_settings
    km.bone_mapping_file = os.path.abspath(args.bonemap)
    bpy.ops.wm.keemap_read_file()
    km.source_rig_name = src.name
    km.destination_rig_name = tgt.name
    km.bone_rotation_mode = args.rotation_mode
    pairs = [(it.SourceBoneName, it.DestinationBoneName)
             for it in scene.keemap_bone_mapping_list]
    print(f"bone map: {len(pairs)} pairs from {args.bonemap}")

    # validate + order parents-before-children (Keemap panel rule: the
    # list MUST be ordered parent -> child; transfer runs in list order)
    kept = []
    for s_name, t_name in pairs:
        if s_name not in src.data.bones:
            print(f"WARN source missing {s_name} — dropping -> {t_name}")
            continue
        if t_name not in tgt.data.bones:
            print(f"WARN target missing {t_name} — dropping {s_name} ->")
            continue
        kept.append((s_name, t_name))
    kept.sort(key=lambda pr: bone_depth(tgt.data.bones[pr[1]]))
    lst = scene.keemap_bone_mapping_list
    if [(it.SourceBoneName, it.DestinationBoneName) for it in lst] != kept:
        saved = []
        for it in lst:
            if (it.SourceBoneName, it.DestinationBoneName) in kept:
                cf, qf, pf = it.CorrectionFactor, it.QuatCorrectionFactor, \
                    it.position_correction_factor
                saved.append(dict(
                    name=it.name, SourceBoneName=it.SourceBoneName,
                    DestinationBoneName=it.DestinationBoneName,
                    set_bone_rotation=it.set_bone_rotation,
                    set_bone_position=it.set_bone_position,
                    corr=tuple(cf), quat=tuple(qf), pos=tuple(pf),
                    gain=it.position_gain))
        saved.sort(key=lambda d: bone_depth(tgt.data.bones[d["DestinationBoneName"]]))
        lst.clear()
        for d in saved:
            it = lst.add()
            it.name = d["name"]; it.SourceBoneName = d["SourceBoneName"]
            it.DestinationBoneName = d["DestinationBoneName"]
            it.set_bone_rotation = d["set_bone_rotation"]
            it.set_bone_position = d["set_bone_position"]
            it.CorrectionFactor = d["corr"]
            it.QuatCorrectionFactor = d["quat"]
            it.position_correction_factor = d["pos"]
            it.position_gain = d["gain"]
        print(f"bone map reordered parents-first: {len(lst)} entries")

    # root position transfer (Keemap position channel, root entry only)
    for it in scene.keemap_bone_mapping_list:
        if it.SourceBoneName == args.root_source and \
           it.DestinationBoneName == args.root_target:
            it.set_bone_position = not args.no_root_position
            print(f"root position transfer: {it.set_bone_position} "
                  f"({args.root_source} -> {args.root_target})")

    # --- calibrate corrections with Keemap itself at the shared pose:
    # frame f0 of a CMU BVH is the bind/T-pose (zero rotations) and the
    # target is at rest. CALC ALL ROTLOC CORRECTIONS measures each bone's
    # correction and restores the target pose afterwards.
    scene.frame_set(f0)
    bpy.context.view_layer.update()
    bpy.ops.wm.calc_correct_all_bones()
    print("calibration done (wm.calc_correct_all_bones @ frame", f0, ")")
    for it in scene.keemap_bone_mapping_list[:4]:
        q = it.QuatCorrectionFactor
        print(f"  corr {it.SourceBoneName} -> {it.DestinationBoneName}: "
              f"quat=({q.w:.4f},{q.x:.4f},{q.y:.4f},{q.z:.4f}) "
              f"pos_corr={tuple(round(v, 4) for v in it.position_correction_factor)}")
    if args.save_map:
        km.bone_mapping_file = os.path.abspath(args.save_map)
        bpy.ops.wm.keemap_save_file()
        print(f"calibrated bone map saved: {args.save_map}")
        km.bone_mapping_file = os.path.abspath(args.bonemap)

    # --- transfer through Keemap's own animation-transfer operator ---
    start = args.start_frame
    num = args.num_frames if args.num_frames is not None else (f1 - start + 1)
    km.start_frame_to_apply = start
    km.number_of_frames_to_apply = num
    km.keyframe_every_n_frames = args.keyframe_every
    print(f"transfer: start={start} num={num} every={args.keyframe_every} "
          f"mode={args.rotation_mode}")
    bpy.ops.wm.perform_animation_transfer()
    print("transfer done (wm.perform_animation_transfer)")

    act = tgt.animation_data.action if tgt.animation_data else None
    if act is None:
        raise SystemExit("Keemap transfer produced no action on target")
    k0, k1 = [int(x) for x in act.frame_range]
    print(f"target action {act.name}: frames {k0}..{k1}, fcurves={len(act.fcurves)}")
    act.name = "Lambada_Keemap"

    # --- normalize output timeline: keys were laid on source frames at
    # source fps; remap x -> 1 + (x - k0) * out_fps/src_fps so the clip
    # starts at frame 1 and plays at --out-fps with identical timing.
    factor = args.out_fps / float(src_fps)
    if k0 != 1 or factor != 1.0:
        for fc in act.fcurves:
            for kp in fc.keyframe_points:
                for pt in (kp.co, kp.handle_left, kp.handle_right):
                    pt.x = 1 + (pt.x - k0) * factor
            fc.update()
    out_last = int(round(act.frame_range[1]))
    n_keys = (k1 - k0) // args.keyframe_every + 1
    scene.render.fps = args.out_fps
    scene.frame_start, scene.frame_end = 1, out_last
    print(f"normalized: clip frames 1..{out_last} @ {args.out_fps}fps "
          f"({n_keys} key steps, time factor {factor})")

    # drop the source rig and its action (an orphan BVH action makes
    # the glTF exporter try to sample 2k frames onto the wrong rig),
    # keep only the Keemap-produced action on the target.
    bpy.data.objects.remove(src, do_unlink=True)
    for a in list(bpy.data.actions):
        if a != act:
            bpy.data.actions.remove(a)
    bpy.ops.wm.save_as_mainfile(filepath=args.out)
    print(f"SAVED {args.out}")

    if args.glb_out:
        # headless selection is unreliable; the .blend is already saved,
        # so drop stray non-rig meshes in-memory and export the scene.
        for o in list(bpy.data.objects):
            if o.type == "MESH" and o.parent != tgt:
                bpy.data.objects.remove(o, do_unlink=True)
        bpy.ops.export_scene.gltf(
            filepath=args.glb_out, export_format="GLB", use_selection=False,
            export_animations=True, export_animation_mode="ACTIONS",
            export_frame_range=True, export_force_sampling=True)
        print(f"GLB {args.glb_out}")


if __name__ == "__main__":
    main()
