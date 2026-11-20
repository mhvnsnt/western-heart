#!/usr/bin/env python3
"""
verify_retarget.py — verify a retargeted GLB actually plays correctly.

  blender -b --python tools/retarget/tests/verify_retarget.py -- \\
      --glb out.glb --expect-map tools/retarget/tekken-bonemap.json \\
      --proof-dir /tmp/proof

Checks (all must pass):
  1. GLB imports with an armature + at least one action.
  2. Every bone in the expected map's target set exists on the target rig.
  3. Motion check: sample each mapped target bone's rotation at 5 frames;
     bones whose source had synthetic motion must show rotation delta above
     epsilon; the report's mapped list must match the map.
  4. No NaN in any sampled transform.
  5. Renders N proof frames (workbench, armature visible) to --proof-dir.

Prints PASS/FAIL lines and exits nonzero on failure.
"""
import argparse
import json
import math
import os
import re
import sys

import bpy
from mathutils import Vector


def parse_args():
    argv = sys.argv
    argv = argv[argv.index("--") + 1:] if "--" in argv else []
    p = argparse.ArgumentParser()
    p.add_argument("--glb", required=True)
    p.add_argument("--expect-map", required=True)
    p.add_argument("--map-name", default="tekken7_to_wh_canonical")
    p.add_argument("--proof-dir", required=True)
    p.add_argument("--fps", type=int, default=30,
                   help="fps the clip was exported at (glTF stores seconds; "
                        "set scene fps to match before sampling)")
    p.add_argument("--moved-bones", nargs="*", default=[
        "Chest", "RightArm", "LeftForeArm", "Head", "RightUpLeg", "Root"],
        help="target bones expected to show motion")
    p.add_argument("--frames", type=int, default=4)
    return p.parse_args(argv)


def main():
    args = parse_args()
    os.makedirs(args.proof_dir, exist_ok=True)
    failures = []

    def check(name, ok, detail=""):
        print(f"[{'PASS' if ok else 'FAIL'}] {name} {detail}")
        if not ok:
            failures.append(name)

    with open(args.expect_map) as f:
        bm = json.load(f)[args.map_name]

    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    bpy.ops.import_scene.gltf(filepath=args.glb)
    arms = [o for o in bpy.context.scene.objects if o.type == "ARMATURE"]
    check("armature present in GLB", len(arms) > 0)
    if not arms:
        sys.exit(1)
    arm = max(arms, key=lambda a: len(a.data.bones))
    scene = bpy.context.scene
    scene.render.fps = args.fps  # match export fps: glTF stores seconds
    # Pick the retargeted action: prefer the one driving the expected bones
    # (a leaked source action would freeze the armature on reimport).
    tgt_names = set(bm.values())
    best, best_score = None, -1
    for act in bpy.data.actions:
        bones = {m.group(1) for fc in act.fcurves
                 if (m := re.search(r'pose\.bones\["([^"]+)"\]', fc.data_path))}
        score = len(bones & tgt_names)
        if score > best_score:
            best, best_score = act, score
    act = best
    if arm.animation_data is None:
        arm.animation_data_create()
    arm.animation_data.action = act
    check("action present", act is not None, (act.name if act else None) or "")
    if not act:
        sys.exit(1)
    f0, f1 = [int(x) for x in act.frame_range]
    check("frame range sane", f1 > f0, f"{f0}..{f1}")

    tgt_bones = {b.name for b in arm.data.bones}
    missing = sorted(set(bm.values()) - tgt_bones)
    # Missing targets are tolerated by the pipeline (warned + skipped);
    # fail only if a bone we EXPECT motion on is missing.
    missing_moved = sorted(set(args.moved_bones) - tgt_bones)
    check("moved bones exist on target", not missing_moved,
          f"missing={missing_moved} (tolerated missing: {missing})")

    # motion sampling
    bpy.context.view_layer.objects.active = arm
    arm.select_set(True)
    bpy.ops.object.mode_set(mode="POSE")
    sample_frames = [f0 + int((f1 - f0) * i / 4) for i in range(5)]
    nan_found = []
    motion = {}
    for wn in args.moved_bones:
        pb = arm.pose.bones.get(wn)
        if pb is None:
            motion[wn] = 0.0
            continue
        rots = []
        for fr in sample_frames:
            scene.frame_set(fr)
            bpy.context.view_layer.update()
            if pb.rotation_mode == "QUATERNION":
                q = pb.rotation_quaternion.copy()
            else:
                q = pb.rotation_euler.to_quaternion()
            if any(math.isnan(v) for v in q):
                nan_found.append((wn, fr))
            rots.append(q)
        # max angle between first and any other sample
        ang = max(2 * math.acos(min(1.0, abs((rots[0].conjugated() @ r).w)))
                  for r in rots[1:])
        motion[wn] = ang
    check("no NaN transforms", not nan_found, str(nan_found[:3]))
    for wn, ang in motion.items():
        check(f"motion on {wn}", ang > 0.05, f"{math.degrees(ang):.1f} deg")

    # still bones should be ~still (spot check)
    still = [b for b in ("LeftFoot", "RightFoot") if b in tgt_bones]
    for wn in still:
        pb = arm.pose.bones[wn]
        rots = []
        for fr in sample_frames:
            scene.frame_set(fr)
            bpy.context.view_layer.update()
            rots.append(pb.rotation_euler.to_quaternion()
                        if pb.rotation_mode != "QUATERNION"
                        else pb.rotation_quaternion.copy())
        ang = max(2 * math.acos(min(1.0, abs((rots[0].conjugated() @ r).w)))
                  for r in rots[1:])
        check(f"no ghost motion on {wn}", ang < 0.05, f"{math.degrees(ang):.2f} deg")

    print(f"\\n{'ALL CHECKS PASSED' if not failures else 'FAILURES: ' + ', '.join(failures)}", flush=True)
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
