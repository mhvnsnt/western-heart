"""Unit tests for backends/skin_audit.py + backends/weight_cleanup.py.

Synthetic skinned GLB with two planted defects:
  1. DEAD major joint — LeftHand carries zero weight; the hand verts
     are all weighted to LeftHandMiddle1 (a finger joint).
  2. CONTAMINATION — one wrist vert is weighted 0.9 to Hips, ~1 m
     away from its segment.
skin_audit must flag both; weight_cleanup must fix both (revived Hand
carries weight, contaminated mass ~0) without breaking weight sums.

Run: python3 tests/test_skin_fixes.py  (or pytest)
"""
import json
import os
import struct
import sys
import tempfile

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backends"))
import skin_audit as sa      # noqa: E402
import weight_cleanup as wc  # noqa: E402


JOINTS = [  # name, world position (chain via children lists below)
    ("Hips", (0.0, 0.95, 0.0)),
    ("Spine", (0.0, 1.05, 0.0)),
    ("Chest", (0.0, 1.20, 0.0)),
    ("LeftArm", (-0.22, 1.38, 0.0)),
    ("LeftForeArm", (-0.47, 1.38, 0.0)),
    ("LeftHand", (-0.70, 1.38, 0.0)),
    ("LeftHandMiddle1", (-0.80, 1.38, 0.0)),
]
CHILDREN = {0: [1], 1: [2], 2: [3], 3: [4], 4: [5], 5: [6], 6: []}
# verts: (pos, {joint_idx: weight})
VERTS = [
    ((0.0, 0.90, 0.02), {0: 1.0}),
    ((0.0, 1.00, 0.02), {0: 0.5, 1: 0.5}),
    ((0.0, 1.12, 0.02), {1: 0.5, 2: 0.5}),
    ((-0.10, 1.30, 0.02), {2: 1.0}),
    ((-0.30, 1.40, 0.02), {3: 1.0}),
    ((-0.40, 1.40, 0.02), {3: 0.5, 4: 0.5}),
    ((-0.55, 1.40, 0.02), {4: 1.0}),
    ((-0.66, 1.40, 0.02), {4: 0.5, 6: 0.5}),     # wrist blend, no Hand
    ((-0.74, 1.40, 0.02), {6: 1.0}),              # hand vert, finger only
    ((-0.78, 1.40, 0.02), {6: 1.0}),              # hand vert, finger only
    ((-0.68, 1.36, 0.02), {0: 0.9, 4: 0.1}),      # CONTAMINATED (Hips)
    ((0.0, 0.02, 0.02), {0: 1.0}),                # low vert (floor ref)
]
FACES = [(0, 1, 2), (2, 1, 3), (3, 4, 5), (5, 4, 6), (6, 7, 8),
         (8, 7, 9), (9, 7, 10), (0, 2, 11)]


def make_glb(path):
    pos = np.array([v[0] for v in VERTS], dtype=np.float32)
    jj = np.zeros((len(VERTS), 4), dtype=np.uint16)
    ww = np.zeros((len(VERTS), 4), dtype=np.float32)
    for i, (_, wmap) in enumerate(VERTS):
        for k, (j, w) in enumerate(sorted(wmap.items())):
            jj[i, k], ww[i, k] = j, w
    idx = np.array([i for f in FACES for i in f], dtype=np.uint16)
    ibm = []
    for _, p in JOINTS:
        m = np.eye(4, dtype=np.float32)
        m[:3, 3] = -np.array(p)
        ibm.append(m.T.flatten())
    ibm = np.array(ibm, dtype=np.float32)

    buf = b""
    views, accs = [], []

    def add(arr, typ, comp):
        nonlocal buf
        pad = (-len(buf)) % 4
        buf += b"\x00" * pad
        views.append({"buffer": 0, "byteOffset": len(buf),
                      "byteLength": arr.nbytes})
        buf += arr.tobytes()
        accs.append({"bufferView": len(views) - 1, "componentType": comp,
                     "count": arr.size // {"VEC3": 3, "VEC4": 4,
                                           "MAT4": 16, "SCALAR": 1}[typ],
                     "type": typ})
        return len(accs) - 1

    a_pos = add(pos, "VEC3", 5126)
    a_j = add(jj, "VEC4", 5123)
    a_w = add(ww, "VEC4", 5126)
    a_i = add(idx, "SCALAR", 5123)
    a_ibm = add(ibm, "MAT4", 5126)

    nodes = []
    for i, (name, p) in enumerate(JOINTS):
        nd = {"name": name, "translation": list(p)}
        if CHILDREN[i]:
            nd["children"] = CHILDREN[i]
        nodes.append(nd)
    nodes.append({"name": "mesh", "mesh": 0, "skin": 0})
    js = {
        "asset": {"version": "2.0"},
        "scene": 0,
        "scenes": [{"nodes": [0, 7]}],
        "nodes": nodes,
        "meshes": [{"primitives": [{
            "attributes": {"POSITION": a_pos, "JOINTS_0": a_j,
                           "WEIGHTS_0": a_w},
            "indices": a_i}]}],
        "skins": [{"joints": list(range(len(JOINTS))),
                   "inverseBindMatrices": a_ibm}],
        "buffers": [{"byteLength": len(buf)}],
        "bufferViews": views,
        "accessors": accs,
    }
    jb = json.dumps(js).encode()
    jb += b" " * ((-len(jb)) % 4)
    data = (b"glTF" + struct.pack("<II", 2, 12 + 8 + len(jb) + 8 + len(buf))
            + struct.pack("<I", len(jb)) + b"JSON" + jb
            + struct.pack("<I", len(buf)) + b"BIN\x00" + buf)
    with open(path, "wb") as f:
        f.write(data)
    return path


def main():
    d = tempfile.mkdtemp()
    src = make_glb(os.path.join(d, "synth.glb"))
    rep = sa.audit(src)
    assert rep["checks"]["skinned"], rep["checks"]
    assert "LeftHand" in rep["measured"]["dead_major_joints"], \
        rep["measured"]["dead_major_joints"]
    assert rep["checks"]["no_dead_joints"] is False
    assert rep["measured"]["contaminated_weight_mass"] > 0.01, \
        rep["measured"]["contaminated_weight_mass"]
    assert rep["checks"]["no_contamination"] is False

    out = os.path.join(d, "synth_fixed.glb")
    crep = wc.cleanup(src, out)
    assert "LeftHand" in crep["dead_major_joints"]
    rep2 = sa.audit(out)
    assert rep2["checks"]["no_dead_joints"] is True, \
        rep2["measured"]["dead_major_joints"]
    assert rep2["checks"]["no_contamination"] is True, \
        rep2["measured"]["contaminated_weight_mass"]
    assert rep2["checks"]["weight_sum_ok"] is True
    assert rep2["checks"]["no_unweighted"] is True
    print("test_skin_fixes: ALL PASS "
          f"(revived={crep['changes']['revived_verts']}, "
          f"pruned={crep['changes']['contaminated_slots_pruned']})")


if __name__ == "__main__":
    main()
