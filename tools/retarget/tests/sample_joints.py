#!/usr/bin/env python3
"""
sample_joints.py — sample world-space joint positions from a GLB animation.

  blender -b --python tools/retarget/tests/sample_joints.py -- \\
      --glb out.glb --fps 30 --frames 5 --out joints.json

Writes {frames: [f0..], bones: {name: [[x,y,z] per frame]}}. Used by
plot_proof.py to render stick-figure proof without needing a GL context.
"""
import argparse
import json
import os
import sys

import bpy


def parse_args():
    argv = sys.argv
    argv = argv[argv.index("--") + 1:] if "--" in argv else []
    p = argparse.ArgumentParser()
    p.add_argument("--glb", required=True)
    p.add_argument("--fps", type=int, default=30)
    p.add_argument("--frames", type=int, default=5)
    p.add_argument("--out", required=True)
    return p.parse_args(argv)


def main():
    args = parse_args()
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    bpy.ops.import_scene.gltf(filepath=args.glb)
    arms = [o for o in bpy.context.scene.objects if o.type == "ARMATURE"]
    arm = max(arms, key=lambda a: len(a.data.bones))
    # Normalize transform (same as the retarget does) so joints are in
    # a consistent space regardless of the file's baked object transform.
    arm.location = (0, 0, 0)
    arm.rotation_euler = (0, 0, 0)
    arm.scale = (1, 1, 1)
    bpy.context.view_layer.update()
    scene = bpy.context.scene
    scene.render.fps = args.fps
    act = arm.animation_data.action if arm.animation_data else None
    f0, f1 = [int(x) for x in act.frame_range] if act else (1, 1)
    frames = [f0 + int((f1 - f0) * i / max(1, args.frames - 1))
              for i in range(args.frames)]
    bones = {}
    bpy.context.view_layer.objects.active = arm
    for fr in frames:
        scene.frame_set(fr)
        bpy.context.view_layer.update()
        for pb in arm.pose.bones:
            # joint world position = head of the posed bone
            w = (arm.matrix_world @ pb.matrix).to_translation()
            bones.setdefault(pb.name, []).append([round(v, 4) for v in w])
    with open(args.out, "w") as f:
        json.dump({"glb": args.glb, "frames": frames, "bones": bones}, f)
    print(f"WROTE {args.out}: {len(bones)} bones x {len(frames)} frames")


if __name__ == "__main__":
    main()
