#!/usr/bin/env python3
"""
render_proof.py -- render proof videos from a BAKED blend (e.g. the
output of wiggle2_jiggle.py). Same framing/lighting as the approved
verlet-baseline videos (anim-fix-work/scripts/render_videos.py):
EEVEE 320x320, 24 fps, frames 1-72, dark world, 3 point lights,
camera on a 1.152*1.9 radius around (0.038, -0.047, 0.052).

Wiggle 2 does not run during rendering (its handlers early-out when
is_rendering), so the input MUST be a baked blend -- which is exactly
what the pipeline produces.

Usage (headless):
  <blender> -b <baked.blend> --python render_proof.py -- \
      --out-dir /path/to/frames --prefix scarlett-wiggle2 \
      --views front,back --video-dir /path/for/mp4s
Writes <prefix>-<view>.mp4 into --video-dir (ffmpeg, libx264, crf 18).
"""
import argparse
import os
import subprocess
import sys

import bpy
from mathutils import Vector


def parse_args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    p = argparse.ArgumentParser()
    p.add_argument("--out-dir", required=True)
    p.add_argument("--video-dir", required=True)
    p.add_argument("--prefix", default="scarlett-wiggle2")
    p.add_argument("--views", default="front,back")
    p.add_argument("--frames", nargs=2, type=int, default=(1, 72))
    return p.parse_args(argv)


def main():
    args = parse_args()
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.eevee.taa_render_samples = 4
    scene.render.resolution_x = 320
    scene.render.resolution_y = 320
    if scene.world is None:
        scene.world = bpy.data.worlds.new("W")
    scene.world.color = (0.05, 0.05, 0.05)
    for o in bpy.data.objects:
        o.hide_render = False
        o.hide_viewport = False
    for name, loc, energy in [("Key", (2, -2, 3), 800),
                              ("Fill", (-2, 1, 1), 300),
                              ("Rim", (0, 2, 2), 500)]:
        ld = bpy.data.lights.new(name, "POINT")
        ld.energy = energy
        lo = bpy.data.objects.new(name, ld)
        lo.location = loc
        scene.collection.objects.link(lo)

    center = Vector((0.038, -0.047, 0.052))
    dist = 1.152 * 1.9
    angles = {"back": (0, 1, 0.08), "front": (0, -1, 0.08),
              "side": (1, 0, 0.08), "34": (0.72, -0.72, 0.14)}
    cams = {}
    for name in args.views.split(","):
        off = angles[name]
        cd = bpy.data.cameras.new(name)
        cd.lens = 50
        co = bpy.data.objects.new("cam_" + name, cd)
        scene.collection.objects.link(co)
        co.location = center + Vector(off) * dist
        target = center + Vector((0, 0, 1.152 * 0.05))
        co.rotation_euler = (target - co.location).to_track_quat(
            "-Z", "Y").to_euler()
        cams[name] = co

    scene.frame_start, scene.frame_end = args.frames
    os.makedirs(args.out_dir, exist_ok=True)
    os.makedirs(args.video_dir, exist_ok=True)
    for name, co in cams.items():
        scene.camera = co
        d = os.path.join(args.out_dir, name)
        os.makedirs(d, exist_ok=True)
        scene.render.filepath = os.path.join(d, "f")
        bpy.ops.render.render(animation=True)
        out = os.path.join(args.video_dir, f"{args.prefix}-{name}.mp4")
        subprocess.run(
            ["ffmpeg", "-y", "-framerate", "24", "-i",
             os.path.join(d, "f%04d.png"), "-c:v", "libx264",
             "-pix_fmt", "yuv420p", "-crf", "18", out],
            check=True, capture_output=True)
        print("WROTE", out)
    print("ALL DONE")


if __name__ == "__main__":
    main()
