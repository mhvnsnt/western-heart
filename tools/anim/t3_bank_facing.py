#!/usr/bin/env python3
"""tools/anim/t3_bank_facing.py — which T3 animation banks were baked facing the wrong way.

Offline twin of game/js/t3anims.js bankFacing() (2026-10-21, Claude session). Every bank's
skeleton.json says "faces +Z, character left = +X" and the runtime retarget relies on it. Banks
whose knees bend BEHIND the hips were in fact baked facing -Z (lab/tools/t3_to_gltf.py picks
"forward" from the head-mesh centroid, which flips on big-haired heads), so retargeted fighters
get the "owl": torso, arms and legs turned away while hips and head face the opponent (Doc Frank).

Cue (data only): forward kinematics of the bank's stance / walk / crouch-hold / guard frames over
skeleton.json; per leg the knee's horizontal offset from the hip-ankle midline, measured against
the hips' forward ((G_Hips * X) x Y); summed over frames. A negative forward sum = baked facing
-Z -> the game turns that bank 180 deg about Y and swaps its Left/Right joint names at load.

    python3 tools/anim/t3_bank_facing.py [game/assets/anim/t3]

Measured 2026-10-21: bosconovitch -179.5, eddy -178.6, gunjack 149.9, heihachi (own rig) 137.7,
yoshimitsu 155.1 deg -> turned; the other twelve banks within +/-61 deg -> untouched.
"""
import json
import math
import os
import sys

import numpy as np

CLIPS = ("t3_neutral.json", "t3_walk_fwd.json", "t3_crouch_hold.json", "t3_block.json")


def qmul(a, b):
    x1, y1, z1, w1 = a
    x2, y2, z2, w2 = b
    return (w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2, w1 * y2 - x1 * z2 + y1 * w2 + z1 * x2,
            w1 * z2 + x1 * y2 - y1 * x2 + z1 * w2, w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2)


def qrot(q, v):
    x, y, z, w = q
    u = np.array([x, y, z])
    v = np.asarray(v, float)
    return 2 * np.dot(u, v) * u + (w * w - np.dot(u, u)) * v + 2 * w * np.cross(u, v)


def bank_facing(bank_dir):
    sk = json.load(open(os.path.join(bank_dir, "skeleton.json")))
    P = {j["name"]: np.array(j["rest"], float) for j in sk["joints"]}
    par = {j["name"]: j["parent"] for j in sk["joints"]}
    order = [j["name"] for j in sk["joints"]]
    fwd_sum = left_sum = 0.0
    samples = 0
    for fn in CLIPS:
        p = os.path.join(bank_dir, fn)
        if not os.path.exists(p):
            continue
        rot = json.load(open(p))["rot_xyzw"]
        n = max(len(v) for v in rot.values())
        for f in range(n):
            G, X = {}, {}
            for j in order:
                r = rot.get(j)
                q = tuple(r[min(f, len(r) - 1)]) if r else (0, 0, 0, 1)
                pj = par.get(j)
                if pj and pj in G:
                    G[j] = qmul(G[pj], q)
                    X[j] = X[pj] + qrot(G[pj], P[j] - P[pj])
                else:
                    G[j] = q
                    X[j] = P[j].copy()
            if "Hips" not in G:
                continue
            fwd = np.cross(qrot(G["Hips"], (1, 0, 0)), (0, 1, 0))
            fwd[1] = 0
            if np.linalg.norm(fwd) < 1e-6:
                continue
            fwd /= np.linalg.norm(fwd)
            left = np.array([fwd[2], 0, -fwd[0]])
            for s in ("Left", "Right"):
                if not all(k in X for k in (s + "UpLeg", s + "Leg", s + "Foot")):
                    continue
                off = X[s + "Leg"] - (X[s + "UpLeg"] + X[s + "Foot"]) / 2
                off[1] = 0
                fwd_sum += float(np.dot(off, fwd))
                left_sum += float(np.dot(off, left))
                samples += 1
    return {"turned": samples > 0 and fwd_sum < 0, "knee_deg": math.degrees(math.atan2(left_sum, fwd_sum)),
            "samples": samples}


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else "game/assets/anim/t3"
    for bank in sorted(os.listdir(root)):
        d = os.path.join(root, bank)
        if not os.path.exists(os.path.join(d, "skeleton.json")):
            continue
        r = bank_facing(d)
        print(f"{bank:24s} knees {r['knee_deg']:7.1f} deg from hips forward  "
              f"({r['samples']} leg samples)  -> {'TURNED 180 at load' if r['turned'] else 'ok'}")


if __name__ == "__main__":
    main()
