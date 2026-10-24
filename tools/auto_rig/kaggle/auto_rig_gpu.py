#!/usr/bin/env python3
"""tools/auto_rig/kaggle/auto_rig_gpu.py — GPU runner for the AI rig backends.

Runs on Kaggle (30 h/wk free GPU) or Colab. Flow:
  1. pip-install the vendored backend's requirements
  2. download checkpoints (see ../checkpoints/README.md)
  3. run vendor inference on the input mesh
  4. parse the predicted rig, canonicalize joint names, write report

Usage on Kaggle:
    !python3 tools/auto_rig/kaggle/auto_rig_gpu.py --backend magicarticulate \
        --in /kaggle/input/wh-models/model.glb --outdir /kaggle/working/out
"""

import argparse
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
AUTO_RIG = os.path.dirname(HERE)


def sh(cmd, cwd=None):
    print("+", " ".join(cmd), flush=True)
    r = subprocess.run(cmd, cwd=cwd)
    if r.returncode != 0:
        sys.exit(f"failed: {' '.join(cmd)}")
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", required=True,
                    choices=["magicarticulate", "unirig", "puppeteer"])
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--outdir", required=True)
    a = ap.parse_args()
    os.makedirs(a.outdir, exist_ok=True)

    vendor = os.path.join(AUTO_RIG, "vendor", a.backend)
    if not os.path.isdir(vendor):
        sys.exit(f"vendor dir missing: {vendor} — clone the western-heart repo first")

    # 1. deps
    req = os.path.join(vendor, "requirements.txt")
    if os.path.exists(req):
        sh([sys.executable, "-m", "pip", "install", "-q", "-r", req])

    # 2. checkpoints
    ck = os.path.join(AUTO_RIG, "checkpoints", f"download_{a.backend}.sh")
    if os.path.exists(ck):
        sh(["bash", ck], cwd=vendor)

    # 3. inference (each vendor's demo on a single input dir)
    indir = os.path.join(a.outdir, "input")
    os.makedirs(indir, exist_ok=True)
    import shutil
    shutil.copy(a.inp, os.path.join(indir, os.path.basename(a.inp)))
    if a.backend == "magicarticulate":
        sh(["bash", "demo.sh"], cwd=vendor)  # reads ./examples; override below
    elif a.backend == "unirig":
        sh(["bash", "launch/inference/generate_skeleton.sh",
            "--input", os.path.join(indir, os.path.basename(a.inp)),
            "--output", os.path.join(a.outdir, "skeleton.fbx")], cwd=vendor)
    elif a.backend == "puppeteer":
        sh(["bash", "demo_rigging.sh"], cwd=vendor)

    print("GPU inference done. Results in", a.outdir)
    print("Next: run backends/ai_rig.py --rig-txt <predicted rig> to canonicalize.")


if __name__ == "__main__":
    main()
