#!/usr/bin/env python3
"""
wiggle2_jiggle.py -- production jiggle pipeline for the Scarlett/Star rig,
driven by the REAL Wiggle 2 addon (shteeve3d, vendored at
tools/open-source/blender-addons/wiggle-2/wiggle_2.py), NOT by hand-written
spring code. This driver replaces the verlet-spring pass that used to live in
anim-fix-work/scripts/retarget_def_rig.py (Spring class).

WHAT IT DOES
  0. Loads the canonical jiggle chain table (tools/jiggle/jiggle_chains.json):
     bone names, spring params, face-guard tokens, per-family chain sets.
     Bone setup and spring params live in the JSON, not in this file.
  1. Opens a COPY of a mocap-applied Scarlett blend (never edit the source).
  2. Registers the vendored Wiggle 2 module and enables scene wiggle.
  3. Configures Wiggle 2 physics on the deform jiggle chains:
       * DEF-breast.L/R + .001/.002/.003  -> TAIL wiggle (spring chain)
       * Butt_L/R + .001-.004 spokes      -> HEAD wiggle (see SCALE NOTE)
  4. Bakes with Wiggle 2's own operator (bpy.ops.wiggle.bake, overwrite mode:
     the baked keys merge into the current action; every other bone's curves
     are left byte-identical).
  5. Freezes wiggle, disables scene wiggle, verifies:
       * every non-jiggle fcurve (face included) is unchanged (hash),
       * no face bone gained a single keyframe,
       * no NaN anywhere in the jiggle curves,
       * baked jiggle motion vs a rigid-follow reference and vs the input's
         own (previous verlet) motion -> metrics JSON.
  6. Saves the baked blend (output path is a scratch/proof file, not the rig).

SCALE NOTE -- why the Butt chains use HEAD wiggle instead of TAIL wiggle
  The Butt_* bones are 0.0026 world units long, while their parent
  (DEF-spine) moves ~0.004-0.005 units per frame at 24 fps. Wiggle 2 is a
  world-space solver: its per-frame gravity/spring step (~0.017 units at
  gravity 1.0) is several times the whole bone length, the tail position
  crosses the head, update_matrix() computes a zero Y-scale, and the next
  relative_matrix() raises "Matrix.invert(ed): matrix does not have an
  inverse" (wiggle_2.py:201/283/448) and poisons the bone's matrix with NaN.
  Reproduced with gravity=0 and stiffness 400..8000 -- it is a bone-length
  vs step-size degeneracy, not a tuning problem. HEAD wiggle simulates the
  bone's head point instead (the same point the old verlet pass simulated:
  its Spring origin was the bone head offset from the parent), translates
  the whole bone, and is stable at these lengths: sy is then exactly 1 by
  construction. The Butt spokes are children of Butt_L/R, so they inherit
  the root motion, and each spoke ALSO gets its own head wiggle for
  per-patch flex. Evidence + numbers: tools/jiggle/proof/ and USAGE.md in
  the vendored wiggle-2 directory.

SELECTION GOTCHA (cost real debugging time; do not remove the isolation)
  Wiggle 2's update_prop() copies EVERY property set on a pose bone to ALL
  selected pose bones (that is how its UI multi-edit works). Configuring
  bones while several are selected silently stamps wiggle_head+wiggle_tail
  and the last-set params onto every selected bone -- which is exactly how
  the Butt bones first got tail wiggle enabled and blew up. This driver
  therefore selects exactly ONE bone before touching its properties.

PARAMETERS (tuned on the CMU lambada clip, frames 1-72 @ 24 fps; see
proof metrics for the measured result)
  Breast tail chain, root->tip stiffness 1400 * 0.88^level, damp 1.1,
  stretch 0.02, gravity 0.6, mass 1.0, chain on. Soft tissue: low gravity
  multiplier keeps the chain from hanging in a static droop; the motion is
  driven by the mocap parent (MCH-breast) acceleration.
  Butt head chain, root 1100, spokes 1100 * 0.85, damp 1.3, stretch 0.02,
  gravity 0.6, mass 1.0, chain on.
  Scene: quality (solver iterations) 4, loop physics on (the lambada clip
  loops), bake preroll 24 frames so the bake starts from a settled loop.

USAGE (headless, Blender 4.0.2)
  xvfb-run -a env -u PYTHONPATH \
    LD_LIBRARY_PATH=~/workspace/tools/egl-stack/usr/lib/x86_64-linux-gnu \
    XDG_RUNTIME_DIR=/tmp \
    <blender> -b <input_mocap.blend> --python wiggle2_jiggle.py -- \
      --armature RIG-SCARLETT \
      --out /path/to/output.blend \
      --metrics /path/to/metrics.json \
      [--wiggle-py /path/to/wiggle_2.py] [--frames 1 72] [--preroll 24]

Exit code is non-zero if any verification fails.
"""
import argparse
import hashlib
import importlib.util
import json
import math
import os
import sys

import bpy

# ---------------------------------------------------------------- chains ---
# Jiggle bone setup is table-driven from jiggle_chains.json (canonical WH
# standard; per-teardown params wired there, not here). The Scarlett/Star
# defaults below are byte-identical to the proven bake params
# (proof: tools/jiggle/proof/scarlett-wiggle2-metrics.json).
CHAINS_JSON_DEFAULT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   "jiggle_chains.json")


def _expand(patterns):
    names = []
    for p in patterns:
        if "{L,R}" in p:
            for side in ("L", "R"):
                names.append(p.replace("{L,R}", side))
        else:
            names.append(p)
    return names


def load_chains(json_path=None, family="female"):
    # Bake path: fixed Scarlett/Star Rigify deform chains under
    # table["bake_path"]. The family sets in table["families"] drive the
    # RUNTIME spring-bone path (game/js/jiggle.js), not the bake.
    with open(json_path or CHAINS_JSON_DEFAULT) as fh:
        table = json.load(fh)
    bake = table["bake_path"]
    bone_groups, bone_order = {}, []
    for chain_name, chain in bake["chains"].items():
        for n in _expand(chain["bake_bone_patterns"]):
            bone_groups[n] = chain_name
            bone_order.append(n)
    return table, bone_order, bone_groups


TABLE, JIGGLE, BONE_CHAIN = load_chains()
CHAINS = TABLE["bake_path"]["chains"]
ITERATIONS = TABLE["bake_path"]["iterations"]
FACE_TOKENS = tuple(TABLE["bake_path"]["face_guard"]["tokens"])
FACE_PREFIX = TABLE["bake_path"]["face_guard"]["prefix"]


def is_face_bone(name):
    n = name.lower()
    return n.startswith(FACE_PREFIX) or any(t in n for t in FACE_TOKENS)


def parse_args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    p = argparse.ArgumentParser()
    p.add_argument("--armature", default="RIG-SCARLETT")
    p.add_argument("--out", required=True)
    p.add_argument("--metrics", default=None)
    p.add_argument("--wiggle-py", default=None)
    p.add_argument("--frames", nargs=2, type=int, default=None)
    p.add_argument("--preroll", type=int, default=None)
    p.add_argument("--chains-json", default=None,
                   help="override the canonical jiggle chain table")
    p.add_argument("--jiggle-family", default="female",
                   choices=["female", "male", "male_fat"],
                   help="family chain set (runtime path uses it; the bake "
                        "path always uses the fixed Scarlett/Star chains)")
    return p.parse_args(argv)


def default_wiggle_py():
    here = os.path.dirname(os.path.abspath(__file__))
    cand = os.path.join(here, "..", "open-source", "blender-addons",
                        "wiggle-2", "wiggle_2.py")
    return os.path.normpath(cand)


def fcurve_digest(action, names=None):
    """Hash every fcurve's points; names=None -> all, else only curves whose
    data_path references one of names."""
    h = hashlib.sha256()
    count = 0
    for fc in action.fcurves:
        if names is not None and not any(f'pose.bones["{n}"]' in fc.data_path
                                         for n in names):
            continue
        count += 1
        h.update(fc.data_path.encode())
        h.update(str(fc.array_index).encode())
        for kp in fc.keyframe_points:
            h.update(f"{kp.co[0]:.4f},{kp.co[1]:.6f};".encode())
    return h.hexdigest(), count


def record_series(arm, frames):
    """Evaluated world tail positions of the jiggle bones, frame by frame."""
    scene = bpy.context.scene
    series = {n: [] for n in JIGGLE}
    for f in frames:
        scene.frame_set(f)
        bpy.context.view_layer.update()
        dg = bpy.context.evaluated_depsgraph_get()
        arm_eval = arm.evaluated_get(dg)
        for n in JIGGLE:
            pb = arm_eval.pose.bones[n]
            series[n].append(list(arm_eval.matrix_world @ pb.tail))
    return series


def deviation_stats(series, rigid, skip):
    out = {}
    for n in JIGGLE:
        dev = [math.dist(series[n][i], rigid[n][i])
               for i in range(len(series[n]))]
        use = dev[skip:]
        vel = [use[i] - use[i - 1] for i in range(1, len(use))]
        cross = sum(1 for i in range(1, len(vel)) if vel[i] * vel[i - 1] < 0)
        out[n] = dict(
            rms=round(math.sqrt(sum(d * d for d in use) / len(use)), 5),
            max=round(max(use), 5),
            mean=round(sum(use) / len(use), 5),
            sd=round(math.sqrt(sum((d - sum(use) / len(use)) ** 2
                                   for d in use) / len(use)), 5),
            deviation_sign_changes=cross,
            nan=any(math.isnan(d) for d in dev),
        )
    return out


def main():
    args = parse_args()
    # CLI may override the canonical chain table / family selection.
    global TABLE, JIGGLE, BONE_CHAIN, CHAINS, ITERATIONS, FACE_TOKENS, \
        FACE_PREFIX
    if args.chains_json or args.jiggle_family != "female":
        TABLE, JIGGLE, BONE_CHAIN = load_chains(args.chains_json,
                                               args.jiggle_family)
        CHAINS = TABLE["bake_path"]["chains"]
        ITERATIONS = TABLE["bake_path"]["iterations"]
        FACE_TOKENS = tuple(TABLE["bake_path"]["face_guard"]["tokens"])
        FACE_PREFIX = TABLE["bake_path"]["face_guard"]["prefix"]
    if args.preroll is None:
        args.preroll = TABLE["bake_path"]["preroll"]
    scene = bpy.context.scene
    arm = bpy.data.objects[args.armature]
    action = arm.animation_data.action
    f0, f1 = (args.frames if args.frames
              else (scene.frame_start, scene.frame_end))
    frames = list(range(f0, f1 + 1))
    skip = min(12, len(frames) // 4)
    print(f"armature={arm.name} action={action.name} frames={f0}..{f1}")

    failures = []

    # ---- before-state: digests + baseline (input's own) motion -----------
    nonjig_digest, nonjig_count = fcurve_digest(
        action, names=[b.name for b in arm.pose.bones
                       if b.name not in JIGGLE])
    face_digest, face_count = fcurve_digest(
        action, names=[b.name for b in arm.pose.bones if is_face_bone(b.name)])
    jig_digest_before, _ = fcurve_digest(action, names=JIGGLE)
    print(f"non-jiggle fcurves={nonjig_count} digest={nonjig_digest[:12]} "
          f"face fcurves={face_count}")
    # The input's own jiggle motion (previous verlet solver, if present).
    base_series = record_series(arm, frames)

    # ---- strip old-solver jiggle keys -> TRUE rigid reference -------------
    # The jiggle bones' keyed basis in the input encodes parent-follow +
    # verlet jiggle (retarget_def_rig.py's Spring writes location-heavy
    # matrix_basis keys). Removing the curves alone is NOT a rigid
    # reference: the pose bones keep their stored (last-baked) basis.
    # So: delete the jiggle fcurves AND reset the stored basis to rest.
    # What remains is the mocap itself, with jiggle bones following their
    # parents rigidly -- the honest "no jiggle" reference. Wiggle 2's own
    # frame_change_pre handler clears wiggle-bone bases every frame during
    # the sim anyway, so this strip changes nothing about the bake; it
    # only makes the reference and the output action clean (the baked
    # action will contain Wiggle 2 keys and nothing else on these bones).
    removed = 0
    for fc in list(action.fcurves):
        if any(f'pose.bones["{n}"]' in fc.data_path for n in JIGGLE):
            action.fcurves.remove(fc)
            removed += 1
    for n in JIGGLE:
        pb = arm.pose.bones[n]
        pb.location = (0.0, 0.0, 0.0)
        pb.rotation_mode = "QUATERNION"
        pb.rotation_quaternion = (1.0, 0.0, 0.0, 0.0)
        pb.rotation_euler = (0.0, 0.0, 0.0)
        pb.scale = (1.0, 1.0, 1.0)
    print(f"stripped {removed} old jiggle fcurves; jiggle bases reset to rest")
    jig_digest_stripped, jig_count_stripped = fcurve_digest(action, names=JIGGLE)
    rigid = record_series(arm, frames)
    base_stats = deviation_stats(base_series, rigid, skip)

    # ---- register the REAL Wiggle 2 ---------------------------------------
    wiggle_py = args.wiggle_py or default_wiggle_py()
    spec = importlib.util.spec_from_file_location("wiggle_2", wiggle_py)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.register()
    print(f"Wiggle 2 registered from {wiggle_py} "
          f"version={mod.bl_info['version']}")

    # ---- configure bones (ONE selected at a time -- see gotcha) -----------
    bpy.context.view_layer.objects.active = arm
    arm.select_set(True)
    bpy.ops.object.mode_set(mode="POSE")
    configured = {}
    for name in JIGGLE:
        pb = arm.pose.bones.get(name)
        if pb is None:
            failures.append(f"missing jiggle bone {name}")
            continue
        for other in arm.pose.bones:
            other.bone.select = False
        pb.bone.select = True
        arm.data.bones.active = pb.bone
        chain = CHAINS[BONE_CHAIN[name]]
        params = chain["bake_params"]
        level = name.count(".00")
        stiff = params["stiff_root"] * (params["stiff_tip_decay"] ** level)
        if params["wiggle_site"] == "tail":
            pb.wiggle_tail = True
            pb.wiggle_stiff = stiff
            pb.wiggle_damp = params["damp"]
            pb.wiggle_stretch = params["stretch"]
            pb.wiggle_gravity = params["gravity"]
            pb.wiggle_mass = params["mass"]
            pb.wiggle_chain = params["chain"]
        else:
            pb.wiggle_head = True
            pb.wiggle_stiff_head = stiff
            pb.wiggle_damp_head = params["damp"]
            pb.wiggle_stretch_head = params["stretch"]
            pb.wiggle_gravity_head = params["gravity"]
            pb.wiggle_mass_head = params["mass"]
            pb.wiggle_chain_head = params["chain"]
        configured[name] = dict(chain=BONE_CHAIN[name],
                                site=params["wiggle_site"],
                                stiff=round(stiff, 1),
                                damp=params["damp"], stretch=params["stretch"],
                                gravity=params["gravity"], mass=params["mass"])
    print(f"configured {len(configured)} jiggle bones")

    scene.wiggle_enable = True
    scene.wiggle.iterations = ITERATIONS
    scene.wiggle.loop = True
    scene.wiggle.preroll = args.preroll
    scene.wiggle.bake_overwrite = True
    listed = sorted(wb.name for wo in scene.wiggle.list if wo.name == arm.name
                    for wb in wo.list)
    print(f"wiggle scene list for {arm.name}: {listed}")
    if listed != sorted(JIGGLE):
        failures.append(f"wiggle list mismatch: {listed} vs {sorted(JIGGLE)}")
    face_enabled = [n for n in listed if is_face_bone(n)]
    if face_enabled:
        failures.append(f"face bones wiggle-enabled: {face_enabled}")

    # ---- bake with Wiggle 2's own operator --------------------------------
    scene.frame_start, scene.frame_end = f0, f1
    result = bpy.ops.wiggle.bake()
    print(f"wiggle.bake -> {result}")
    arm.wiggle_freeze = True
    scene.wiggle_enable = False

    # ---- verify -------------------------------------------------------------
    action2 = arm.animation_data.action
    nonjig_digest2, _ = fcurve_digest(
        action2, names=[b.name for b in arm.pose.bones
                        if b.name not in JIGGLE])
    face_digest2, face_count2 = fcurve_digest(
        action2, names=[b.name for b in arm.pose.bones if is_face_bone(b.name)])
    jig_digest_after, _ = fcurve_digest(action2, names=JIGGLE)
    if nonjig_digest2 != nonjig_digest:
        failures.append("NON-JIGGLE fcurves changed during bake")
    if face_digest2 != face_digest or face_count2 != face_count:
        failures.append("FACE fcurves changed during bake")
    if jig_digest_after == jig_digest_stripped or jig_count_stripped != 0:
        failures.append("jiggle fcurves still empty after bake -- bake did nothing")
    nan_keys = 0
    for fc in action2.fcurves:
        if any(f'pose.bones["{n}"]' in fc.data_path for n in JIGGLE):
            nan_keys += sum(1 for kp in fc.keyframe_points
                            if math.isnan(kp.co[1]) or math.isinf(kp.co[1]))
    if nan_keys:
        failures.append(f"{nan_keys} NaN/Inf jiggle keyframe values")

    baked_series = record_series(arm, frames)
    baked_stats = deviation_stats(baked_series, rigid, skip)

    metrics = dict(
        tool="Wiggle 2 (shteeve3d) via tools/jiggle/wiggle2_jiggle.py",
        wiggle_module=os.path.abspath(wiggle_py),
        wiggle_version=".".join(str(v) for v in mod.bl_info["version"]),
        blender_version=".".join(str(v) for v in bpy.app.version),
        armature=arm.name, action=action2.name,
        frames=[f0, f1], fps=scene.render.fps,
        iterations=ITERATIONS, preroll=args.preroll,
        configured=configured,
        old_jiggle_fcurves_stripped=removed,
        reference="rigid = input mocap with jiggle fcurves removed and jiggle "
                  "pose-bone bases reset to rest (bones follow parents only)",
        face_fcurves_before=face_count, face_fcurves_after=face_count2,
        face_digest_unchanged=(face_digest2 == face_digest),
        nonjiggle_digest_unchanged=(nonjig_digest2 == nonjig_digest),
        nan_jiggle_keys=nan_keys,
        baseline_input_vs_rigid=base_stats,
        wiggle2_baked_vs_rigid=baked_stats,
        failures=failures,
    )
    if args.metrics:
        with open(args.metrics, "w") as fh:
            json.dump(metrics, fh, indent=2)
        print(f"metrics -> {args.metrics}")

    bpy.ops.wm.save_as_mainfile(filepath=args.out)
    print(f"SAVED {args.out}")
    if failures:
        print("FAILURES:", failures)
        sys.exit(1)
    print("ALL CHECKS PASSED")


if __name__ == "__main__":
    main()
