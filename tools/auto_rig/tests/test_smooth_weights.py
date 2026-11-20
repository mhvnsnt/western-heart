"""Unit tests for backends/smooth_weights.py (2026-11-01, Negativo re-rig findings) — pytest or plain python3.

  1. UV-seam copies (vertices at the same position, no shared edge) must receive the SAME smoothed weights,
     or the seam opens into a crack under animation (smooth_weights used to update only the copy on the
     stretched edge: 6,688 drifted copies on Negativo).
  2. The 4-influence limit must be continuous: two vertices whose 4th/5th bones differ by a hair must end up
     with nearly the same limited weights (a hard top-4 cut keeps different 4th bones -> tearing).
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", "backends"))
import anim_check  # noqa: E402
import smooth_weights as sw  # noqa: E402
from test_anim_check import make_glb  # noqa: E402


def dense(jj, ww, n=8):
    d = np.zeros(n)
    for j, w in zip(jj, ww):
        d[j] += w
    return d


def test_limit4_continuous():
    a = {0: 0.5, 1: 0.3, 2: 0.1, 3: 0.0500, 4: 0.0499}
    b = {0: 0.5, 1: 0.3, 2: 0.1, 3: 0.0499, 4: 0.0500}   # 4th/5th swapped by a hair
    da, db = dense(*sw.limit4(a)), dense(*sw.limit4(b))
    assert np.abs(da - db).sum() < 0.005, (da, db)
    assert abs(da.sum() - 1) < 1e-9 and abs(db.sum() - 1) < 1e-9
    # four or fewer influences pass through unchanged (renormalized)
    jj, ww = sw.limit4({2: 0.25, 5: 0.75})
    assert dense(jj, ww)[5] == 0.75 and dense(jj, ww)[2] == 0.25


def test_seam_copies_stay_identical():
    # v4 is a UV-seam copy of v2 (same position, different triangle); the Child joint teleports +1 m so the
    # Root|Child edges stretch and get averaged; v4 must follow v2 exactly.
    pos = [[-0.1, 0.9, 0], [0.1, 0.9, 0], [-0.1, 1.1, 0], [0.1, 1.1, 0], [-0.1, 1.1, 0], [0.0, 1.3, 0]]
    joints = [[0, 0, 0, 0], [0, 0, 0, 0], [1, 0, 0, 0], [1, 0, 0, 0], [1, 0, 0, 0], [1, 0, 0, 0]]
    weights = [[1, 0, 0, 0]] * 6
    idx = [0, 1, 2, 2, 1, 3, 4, 3, 5]
    path = make_glb([(1, "translation", [0, 0.5, 1.0], [[0, 1, 0], [0, 2.0, 0], [0, 1, 0]])],
                    pos=pos, joints=joints, weights=weights, idx=idx)
    try:
        sw.smooth(path, threshold=2.0, rounds=1, frames_per_clip=5, gate=2.5)
    except SystemExit:
        pass  # a 1 m teleport never reaches the gate in one round; only the written weights matter here
    pr = anim_check.AnimModel(path).prims[0]
    d2 = dense(pr["joints"][2], pr["weights"][2])
    d4 = dense(pr["joints"][4], pr["weights"][4])
    assert d2[0] > 0.1, "v2 was not smoothed (test setup)"
    assert np.allclose(d2, d4, atol=1e-6), (d2, d4)


if __name__ == "__main__":
    test_limit4_continuous()
    test_seam_copies_stay_identical()
    print("smooth_weights tests: 2/2 pass")
