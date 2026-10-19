#!/usr/bin/env python3
"""tools/auto_rig/backends/ai_rig.py — GPU auto-rig adapter.

Runs one of the vendored AI riggers (magicarticulate / unirig / puppeteer)
on a GPU box (Kaggle/Colab — see ../kaggle/auto_rig_gpu.py), parses the
predicted skeleton, maps joint names onto the WH canonical set
(backends/retarget.py), and writes a WH-canonical GLB.

Pipeline per model:
  1. vendor inference -> predicted skeleton (rig .txt: "joints <name> x y z")
  2. canonicalize names -> WH set (unmapped joints are KEPT with their
     predicted names, flagged in the report — never silently dropped)
  3. report written as JSON; the rigged GLB is assembled by running
     blender-heat on the predicted skeleton (wired next wave — the
     adapter currently stops at the canonicalization report).

GPU-only. On a CPU box this module refuses to run the vendor inference
and tells you the Kaggle command instead.

Checkpoints are downloaded on first run (see ../checkpoints/README.md) —
never vendored.
"""

import argparse
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
VENDOR = os.path.join(os.path.dirname(HERE), "vendor")

sys.path.insert(0, os.path.dirname(HERE))
from backends.retarget import canonicalize  # noqa: E402

BACKENDS = {
    "magicarticulate": {
        "dir": os.path.join(VENDOR, "magicarticulate"),
        "demo": "bash demo.sh",
        "rig_glob": "results/*/*_pred.txt",
        "weights": "skeleton_ckpt/checkpoint_trainonv2_hier.pth",
    },
    "unirig": {
        "dir": os.path.join(VENDOR, "unirig"),
        "demo": "bash launch/inference/generate_skeleton.sh --input {inp} --output {out}",
        "rig_glob": "*.fbx",
        "weights": "hf://VAST-AI/UniRig",
    },
    "puppeteer": {
        "dir": os.path.join(VENDOR, "puppeteer"),
        "demo": "bash demo_rigging.sh",
        "rig_glob": "results/final_rigging/*.txt",
        "weights": "skeleton/skeleton_ckpts/puppeteer_skeleton_w_diverse_pose.pth",
    },
}


def parse_rig_txt(path):
    """Parse 'joints <name> <x> <y> <z>' lines -> [(name, (x,y,z))]."""
    joints = []
    with open(path) as f:
        for line in f:
            parts = line.split()
            if len(parts) == 5 and parts[0] == "joints":
                joints.append((parts[1], tuple(map(float, parts[2:5]))))
    return joints


def check_gpu():
    try:
        out = subprocess.run(
            ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
            capture_output=True, text=True, timeout=15)
        return out.returncode == 0 and bool(out.stdout.strip())
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", choices=BACKENDS, required=True)
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--rig-txt", default=None,
                    help="skip inference; use an existing rig .txt")
    ap.add_argument("--report", default="ai_rig_report.json")
    a = ap.parse_args()

    cfg = BACKENDS[a.backend]
    if not os.path.isdir(cfg["dir"]):
        sys.exit(f"vendor dir missing: {cfg['dir']}")

    joints = []
    if a.rig_txt:
        joints = parse_rig_txt(a.rig_txt)
    elif not check_gpu():
        sys.exit(
            "No GPU found. The AI backends need CUDA (4.6GB+ VRAM).\n"
            "Run on Kaggle instead:\n"
            "  python3 tools/auto_rig/kaggle/auto_rig_gpu.py"
            f" --backend {a.backend} --in {a.inp}")
    else:
        sys.exit("GPU inference path: copy this model to the Kaggle box and run "
                 "tools/auto_rig/kaggle/auto_rig_gpu.py "
                 f"--backend {a.backend} --in {os.path.basename(a.inp)}")

    names = [n for n, _ in joints]
    mapping, unmapped = canonicalize(names)
    report = {
        "backend": a.backend,
        "predicted_joints": len(joints),
        "mapped": len(mapping),
        "unmapped": unmapped,
        "mapping": mapping,
        "positions": {mapping.get(n, n): pos for n, pos in joints},
    }
    json.dump(report, open(a.report, "w"), indent=2)
    print(f"AI_RIG_OK backend={a.backend} joints={len(joints)} "
          f"mapped={len(mapping)} unmapped={len(unmapped)}")
    print(f"report: {a.report}")


if __name__ == "__main__":
    main()
