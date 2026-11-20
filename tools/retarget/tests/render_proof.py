#!/usr/bin/env python3
"""
render_proof.py — render proof frames of a retargeted GLB.

  blender-softwaregl -b --python tools/retarget/tests/render_proof.py -- \\
      --glb out.glb --fps 30 --outdir /tmp/proof --frames 5

Renders --frames evenly spaced frames with the workbench engine.
Requires a GL context: use blender-softwaregl (bundled Mesa) or xvfb-run.
"""
import argparse
import math
import os
import sys

import bpy
from mathutils import Euler


def parse_args():
    argv = sys.argv
    argv = argv[argv.index("--") + 1:] if "--" in argv else []
    p = argparse.ArgumentParser()
    p.add_argument("--glb", required=True)
    p.add_argument("--fps", type=int, default=30)
    p.add_argument("--outdir", required=True)
    p.add_argument("--frames", type=int, default=5)
    p.add_argument("--action", default=None,
                   help="action name to play (default: armature's action)")
    return p.parse_args(argv)


def main():
    args = parse_args()
    os.makedirs(args.outdir, exist_ok=True)
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    bpy.ops.import_scene.gltf(filepath=args.glb)
    arms = [o for o in bpy.context.scene.objects if o.type == "ARMATURE"]
    if not arms:
        raise SystemExit("no armature in " + args.glb)
    arm = max(arms, key=lambda a: len(a.data.bones))
    scene = bpy.context.scene
    scene.render.fps = args.fps
    if args.action:
        if arm.animation_data is None:
            arm.animation_data_create()
        arm.animation_data.action = bpy.data.actions[args.action]
    act = arm.animation_data.action if arm.animation_data else None
    if act is None:
        raise SystemExit("no action to play")
    f0, f1 = [int(x) for x in act.frame_range]
    print(f"rendering {args.frames} frames of '{act.name}' ({f0}..{f1})")

    scene.render.engine = "BLENDER_WORKBENCH"
    scene.render.resolution_x, scene.render.resolution_y = 640, 480
    scene.render.film_transparent = True
    for o in scene.objects:
        if o.type == "ARMATURE":
            o.display_type = "WIRE"
    # Character faces -Y in our fixtures; camera in front (-Y), slightly above.
    bpy.ops.object.camera_add(location=(0, -4.5, 1.6))
    cam = bpy.context.object
    cam.rotation_euler = Euler((math.radians(72), 0, 0), "XYZ")
    scene.camera = cam
    bpy.ops.object.light_add(type="SUN", location=(3, -4, 6))

    # Show meshes too if present
    for o in scene.objects:
        if o.type == "MESH":
            o.display_type = "TEXTURED"

    for i in range(args.frames):
        fr = f0 + int((f1 - f0) * i / max(1, args.frames - 1))
        scene.frame_set(fr)
        bpy.context.view_layer.update()
        out = os.path.join(args.outdir, f"proof_f{fr:03d}.png")
        scene.render.filepath = out
        bpy.ops.render.render(write_still=True)
        print(f"rendered {out}", flush=True)


if __name__ == "__main__":
    main()
