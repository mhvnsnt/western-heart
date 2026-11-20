#!/usr/bin/env python3
"""
make_test_fixtures.py — build test fixtures for the Tekken retarget pipeline.

  blender -b --python tools/retarget/tests/make_test_fixtures.py -- --outdir /tmp/fix

Produces:
  test_t7_anim.fbx — the REAL extracted T7 base skeleton (60 core bones from
      tools/retarget/tekken_skeleton_base.json) with a SYNTHETIC test
      animation ("TEST_Punch", 40 frames @30fps). The skeleton is real T7
      teardown data; the clip is a clearly-labeled stand-in until real T7
      animation extractions land (owner acquisition pending).
  test_wh_rig.glb  — WH-Canonical-22 armature as GLB (alternate target path).

The clip uses a distinct, asymmetric motion per bone so the verifier can
prove each mapped bone received its own motion (not a frozen or smeared copy):
  Base      : bounce in Z (root motion)
  Spine2    : twist about Z
  R_Arm     : swing about X
  L_ForeArm : bend about X (opposite phase)
  Head      : nod about X
  R_UpLeg   : lift about X (small)
"""
import argparse
import json
import math
import os
import sys

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
# tekken_skeleton_base.json lives next to this script in the repo
# (tools/retarget/tests/ -> tools/retarget/); fall back to script dir.
RETARGET_DIR = HERE
if not os.path.exists(os.path.join(HERE, "tekken_skeleton_base.json")):
    _up = os.path.abspath(os.path.join(HERE, ".."))
    if os.path.exists(os.path.join(_up, "tekken_skeleton_base.json")):
        RETARGET_DIR = _up


def parse_args():
    argv = sys.argv
    argv = argv[argv.index("--") + 1:] if "--" in argv else []
    p = argparse.ArgumentParser()
    p.add_argument("--outdir", required=True)
    return p.parse_args(argv)


def build_t7_armature():
    with open(os.path.join(RETARGET_DIR, "tekken_skeleton_base.json")) as f:
        skel = json.load(f)
    pos = {b["name"]: tuple(b["rest_pos"]) for b in skel["bones"]}
    par = {b["name"]: b["parent"] for b in skel["bones"]}

    bpy.ops.object.armature_add(enter_editmode=True)
    arm = bpy.context.object
    arm.name = "SKT_CH_base_Skeleton"
    adata = arm.data
    adata.edit_bones.remove(adata.edit_bones[0])
    eb = {}

    def emit(name):
        if name in eb:
            return
        p = par[name]
        if p and p in pos:
            emit(p)
        b = adata.edit_bones.new(name)
        head = pos[name]
        kids = [k for k, pp in par.items() if pp == name and k in pos]
        tail = pos[kids[0]] if kids else (head[0], head[1], head[2] - 0.08)
        if math.dist(head, tail) < 1e-4:
            tail = (head[0], head[1], head[2] - 0.08)
        b.head = head
        b.tail = tail
        if p and p in eb:
            b.parent = eb[p]
            b.use_connect = False
        eb[name] = b

    for b in skel["bones"]:
        emit(b["name"])
    bpy.ops.object.mode_set(mode="OBJECT")
    return arm


# (bone, axis, amplitude_rad, phase_frames) — distinct motion per bone.
# phase_frames shifts the envelope in time so each bone peaks differently.
# T7 rest is a T-pose (arms along +/-X); R_Arm rotZ swings the right arm
# forward (-Y) for a punch.
MOTIONS = [
    ("Base", "loc_y", -0.10, 0),
    ("Spine2", "rotz", 0.18, 0),
    ("R_Arm", "rotz", 1.25, 0),
    ("R_ForeArm", "rotz", 0.35, 4),
    ("L_Arm", "rotz", -0.25, 6),
    ("Head", "rotx", 0.15, -4),
    ("R_UpLeg", "rotx", 0.20, 10),
]

NFRAMES = 40


def punch_envelope(t):
    # windup(0-.25) -> strike(.25-.5) -> hold(.5-.7) -> recover(.7-1)
    if t < 0.25:
        return -0.4 * math.sin(t / 0.25 * math.pi / 2)
    elif t < 0.5:
        return -0.4 + 1.4 * ((t - 0.25) / 0.25)
    elif t < 0.7:
        return 1.0
    else:
        return 1.0 - 1.0 * ((t - 0.7) / 0.3)


def animate(arm):
    bpy.context.view_layer.objects.active = arm
    arm.select_set(True)
    bpy.ops.object.mode_set(mode="POSE")
    for pb in arm.pose.bones:
        pb.rotation_mode = "XYZ"
    act = bpy.data.actions.new(name="TEST_Punch_SYNTHETIC")
    arm.animation_data_create()
    arm.animation_data.action = act
    scene = bpy.context.scene
    scene.render.fps = 30
    scene.frame_start = 1
    scene.frame_end = NFRAMES
    for frame in range(1, NFRAMES + 1):
        for bone, kind, amp, phase in MOTIONS:
            pb = arm.pose.bones.get(bone)
            if pb is None:
                continue
            # envelope evaluated at phase-shifted time
            t = (frame - 1 + phase) / (NFRAMES - 1)
            t = max(0.0, min(1.0, t))
            e = punch_envelope(t)
            v = amp * e
            if kind == "loc_z":
                pb.location = (0, 0, v)
                pb.keyframe_insert(data_path="location", frame=frame)
            elif kind == "loc_y":
                pb.location = (0, v, 0)
                pb.keyframe_insert(data_path="location", frame=frame)
            elif kind == "rotx":
                pb.rotation_euler = (v, 0, 0)
                pb.keyframe_insert(data_path="rotation_euler", frame=frame)
            elif kind == "rotz":
                pb.rotation_euler = (0, 0, v)
                pb.keyframe_insert(data_path="rotation_euler", frame=frame)
        scene.frame_set(frame)
    bpy.ops.object.mode_set(mode="OBJECT")
    return act


def main():
    args = parse_args()
    os.makedirs(args.outdir, exist_ok=True)
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)

    arm = build_t7_armature()
    act = animate(arm)
    print(f"T7 armature: {len(arm.data.bones)} bones, action '{act.name}' "
          f"{NFRAMES} frames")

    fbx_path = os.path.join(args.outdir, "test_t7_anim.fbx")
    bpy.ops.object.select_all(action="DESELECT")
    arm.select_set(True)
    bpy.context.view_layer.objects.active = arm
    bpy.ops.export_scene.fbx(filepath=fbx_path, use_selection=True,
                             add_leaf_bones=False,
                             bake_anim=True, bake_anim_simplify_factor=0.0)
    print(f"WROTE {fbx_path}")

    glb_path = os.path.join(args.outdir, "test_t7_anim.glb")
    bpy.ops.export_scene.gltf(filepath=glb_path, export_format="GLB",
                              use_selection=True, export_animations=True,
                              export_frame_range=True)
    print(f"WROTE {glb_path}")


if __name__ == "__main__":
    main()
