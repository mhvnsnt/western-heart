#!/usr/bin/env python3
"""Blender-lane job (PREPARED, not run here): MB-Lab + MPFB
parametric-human generation for the creation suite.

Why prepared-not-run: no Blender binary exists on this VM, and
MB-Lab is a Blender addon (44MB pulled to ~/workspace/pulls-wire/
mblab/; MPFB lives in the repo at tools/mpfb2/ — USE that dir,
do not re-clone it). This job runs where Blender exists: the
Kaggle GPU notebook (Blender installed in-notebook) or any
Blender-equipped lane machine, via the coordinator's browser
delegation. Sign-in for Kaggle: Google tap-to-sign-in ONLY
(fmmg.mars@gmail.com / marsfmmg). Never a password card.

Run with Blender headless, e.g.:
  blender --background --python tools/gpu-lane/mblab-blender-job.py \
    -- --preset <preset.json> --out <model.glb>

Inside Blender this script must:
  1. Enable the MB-Lab addon (from the pulled addon dir) or MPFB
     (from tools/mpfb2/) — one human generator per run, recorded
     in the report so the pipeline knows which produced the mesh.
  2. Apply the preset's morph sliders (body/head/face/torso/arms/
     legs/expressions — MB-Lab's categories) or MPFB parameters.
  3. Export GLB to --out, plus a report JSON next to it:
     generator, preset, rig type (must be a rig-compat.js type),
     mapped core roles, vertex count.
  4. FAIL if any core semantic role (rig-compat.js) is unmapped
     on the exported rig — every tool must work on every rig.

Outside Blender (plain `python3` run, as in CI lint), this file
only validates its own arguments and prints the Blender command
— it never pretends a human was generated.
"""
import argparse
import json
import os
import sys

try:
    import bpy  # noqa: F401  (only present inside Blender)
    IN_BLENDER = True
except ImportError:
    IN_BLENDER = False


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--preset", default="")
    p.add_argument("--out", default="mblab-out.glb")
    args = p.parse_args()
    if not IN_BLENDER:
        print("MBLAB-BLENDER-JOB: not inside Blender — prepared only.")
        print("MBLAB-BLENDER-JOB: run: blender --background --python "
              "tools/gpu-lane/mblab-blender-job.py -- --preset <preset.json> --out <model.glb>")
        return 0
    # ---- Inside Blender: the lane that runs this fills in the
    # generator-specific calls (MB-Lab API / MPFB API) from the
    # addon docs at run time; the contract below is fixed. ----
    raise NotImplementedError(
        "MBLAB-BLENDER-JOB: generator calls are filled in by the "
        "Blender lane from the MB-Lab/MPFB addon docs at run time; "
        "this stub refuses to fake a generation. Contract: export "
        "--out GLB + report JSON (generator, preset, rig type, "
        "mapped core roles, verts); fail on any unmapped core role."
    )


if __name__ == "__main__":
    sys.exit(main())
