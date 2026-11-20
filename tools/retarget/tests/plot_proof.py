#!/usr/bin/env python3
"""
plot_proof.py — stick-figure proof frames from sample_joints.py output.

  python3 tools/retarget/tests/plot_proof.py joints.json proof.png

Draws side-view (Y-Z) stick figures for each sampled frame using the bone
hierarchy inferred from joint positions (nearest-neighbor chaining along the
known bone list). Pure matplotlib — no GL needed.
"""
import json
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# parent map for the skeletons we plot (WH canonical + Mixamo core)
PARENTS = {
    "Root": None, "Hips": "Root", "Spine": "Hips", "Chest": "Spine",
    "Neck": "Chest", "Head": "Neck",
    "LeftShoulder": "Chest", "LeftArm": "LeftShoulder",
    "LeftForeArm": "LeftArm", "LeftHand": "LeftForeArm",
    "RightShoulder": "Chest", "RightArm": "RightShoulder",
    "RightForeArm": "RightArm", "RightHand": "RightForeArm",
    "LeftUpLeg": "Hips", "LeftLeg": "LeftUpLeg", "LeftFoot": "LeftLeg",
    "LeftToeBase": "LeftFoot",
    "RightUpLeg": "Hips", "RightLeg": "RightUpLeg", "RightFoot": "RightLeg",
    "RightToeBase": "RightFoot",
    # Mixamo extras map onto the same drawing
    "Spine1": "Spine", "Spine2": "Chest",
}


def main():
    joints_path, out_path = sys.argv[1], sys.argv[2]
    d = json.load(open(joints_path))
    frames, bones = d["frames"], d["bones"]
    # canonicalize Mixamo names to drawable set
    alias = {"Hips": "Hips", "Spine": "Spine", "Spine1": "Spine1",
             "Spine2": "Spine2", "Neck": "Neck", "Head": "Head"}
    n = len(frames)
    fig, axes = plt.subplots(1, n, figsize=(3 * n, 4.2))
    if n == 1:
        axes = [axes]
    for ax, fi in zip(axes, range(n)):
        drawn = set()
        for child, parent in PARENTS.items():
            if parent is None or child not in bones or parent not in bones:
                continue
            c, p = bones[child][fi], bones[parent][fi]
            # side view: x = depth(Y), y = height(Z)
            ax.plot([p[1], c[1]], [p[2], c[2]], "o-", color="#1f77b4",
                    lw=2.5, ms=4)
            drawn.add(child)
        ax.set_title(f"frame {frames[fi]}")
        ax.set_aspect("equal")
        ax.set_xlim(-1.2, 1.2)
        ax.set_ylim(0, 2.1)
        ax.set_xlabel("depth (Y)")
        ax.set_ylabel("height (Z)")
        ax.grid(True, alpha=0.3)
    fig.suptitle("Retargeted T7 punch — side view (from output GLB joints)")
    fig.tight_layout()
    fig.savefig(out_path, dpi=90)
    print(f"WROTE {out_path}")


if __name__ == "__main__":
    main()
