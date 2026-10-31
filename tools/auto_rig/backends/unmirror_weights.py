#!/usr/bin/env python3
"""tools/auto_rig/backends/unmirror_weights.py — repair L/R-mirrored skins.

Some exports ship JOINTS_0 indices with Left and Right swapped: every
vertex's weights name the mirror-side joint (geometry and skeleton
agree; only the weight indices point across the body). skin_audit
reads that as massive contamination (demonio bloodline-ember:
37.875% of weight mass on far segments), and a prune+fill cleanup
would DESTROY the authored weight gradients to fix it.

This tool remaps JOINTS_0 indices through the Left<->Right joint-name
swap (joint data only: no geometry, no skeleton, no weight VALUES
change). It refuses to run unless the swap is a clear win: it measures
skin_audit's contamination rule before and after the swap and aborts
when the swapped contamination is not dramatically lower.

    python3 unmirror_weights.py --in MODEL.glb --out UNMIRRORED.glb
        [--report R.json]

Container handling matches weight_cleanup.py: accessor shapes never
change, BIN bytes are patched in place, file size is stable.
"""

import argparse
import json
import os
import re
import struct
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
from validate import read_glb  # noqa: E402
import skin_audit as sa  # noqa: E402
from weight_cleanup import accessor_patch_target  # noqa: E402

BODY_RE = re.compile(
    r"^(Left|Right)?(Hips|Spine|Neck|Head|Shoulder|Arm|ForeArm|Hand|"
    r"UpLeg|Leg|Foot|ToeBase)|Tail\d")


def gather(js, bdat):
    pos_l, jj_l, ww_l = [], [], []
    for nd in js.get("nodes", []):
        if "mesh" not in nd or "skin" not in nd:
            continue
        for prim in js["meshes"][nd["mesh"]]["primitives"]:
            at = prim.get("attributes", {})
            if "POSITION" not in at or "JOINTS_0" not in at:
                continue
            pos_l.append(sa.read_accessor(js, bdat, at["POSITION"]).astype(
                np.float64))
            jj_l.append(sa.read_accessor(js, bdat, at["JOINTS_0"]).astype(
                np.int64))
            ww_l.append(sa.read_weights(js, bdat, at["WEIGHTS_0"]))
    return (np.concatenate(pos_l), np.concatenate(jj_l),
            np.concatenate(ww_l))


def contamination(js, bdat, names, jj, ww, pos):
    if "inverseBindMatrices" in js["skins"][0]:
        ibm = sa.read_accessor(js, bdat,
                               js["skins"][0]["inverseBindMatrices"])
        jpos = np.array([np.linalg.inv(
            ibm[i].reshape(4, 4, order="F"))[:3, 3]
            for i in range(len(names))])
    else:
        worlds, _ = sa.world_matrices(js)
        jpos = np.array([worlds[j][:3, 3] for j in js["skins"][0]["joints"]])
    name_to_joint = {n: i for i, n in enumerate(names)}
    child = {}
    for i, n in enumerate(names):
        want = sa.CANON_CHILD.get(n)
        if want in name_to_joint:
            child[i] = name_to_joint[want]
    worlds, parent = sa.world_matrices(js)
    node_to_joint = {n: i for i, n in enumerate(js["skins"][0]["joints"])}
    seg_b = []
    for i in range(len(names)):
        if i in child:
            seg_b.append(jpos[child[i]])
        else:
            seg_b.append(jpos[i] + np.array([0.0, 0.05, 0.0]))
    seg_b = np.array(seg_b)
    segd = np.empty((len(pos), len(names)), dtype=np.float32)
    for j in range(len(names)):
        segd[:, j] = sa.seg_dist(pos, jpos[j], seg_b[j])
    nearest = segd.min(axis=1)
    height = float(pos[:, 1].max() - pos[:, 1].min())
    margin = np.maximum(0.10 * height, 2.5 * nearest)
    body = np.array([bool(BODY_RE.match(n)) for n in names])
    d_slot = segd[np.arange(len(pos))[:, None], jj]
    mask = (d_slot > (nearest + margin)[:, None]) & (ww >= 0.05) & body[jj]
    return float(ww[mask].sum() / max(ww.sum(), 1e-9)), \
        int(mask.any(axis=1).sum())


def swap_map(names):
    swap = {}
    for i, n in enumerate(names):
        if n.startswith("Left") and ("Right" + n[4:]) in names:
            j = names.index("Right" + n[4:])
            swap[i] = j
            swap[j] = i
    return swap


def unmirror(inp, outp):
    with open(inp, "rb") as f:
        raw = f.read()
    js, bdat = read_glb(inp)
    binarr = bytearray(bdat)
    nodes = js.get("nodes", [])
    names = [nodes[j].get("name", "") for j in js["skins"][0]["joints"]]
    swap = swap_map(names)
    if not swap:
        raise SystemExit("no Left/Right joint pairs found; nothing to do")
    pos, jj, ww = gather(js, bdat)
    before = contamination(js, bdat, names, jj, ww, pos)
    jj2 = jj.copy()
    for a, b in swap.items():
        jj2[jj == a] = b
    after = contamination(js, bdat, names, jj2, ww, pos)
    rep = {"in": inp, "out": outp,
           "swap_pairs": len(swap) // 2,
           "contamination_before": {"mass": round(before[0], 5),
                                    "verts": before[1]},
           "contamination_after_swap": {"mass": round(after[0], 5),
                                        "verts": after[1]}}
    # the swap must be a decisive win (>=10x), else this file is not a
    # mirror case and rewriting its indices would be vandalism
    if not (after[0] < 0.1 * before[0] and after[0] < 0.01):
        rep["applied"] = False
        rep["reason"] = "swap is not a decisive win; refusing to rewrite"
        print(json.dumps(rep, indent=1))
        raise SystemExit(2)
    # patch JOINTS_0 accessors in place
    changed = 0
    for nd in js.get("nodes", []):
        if "mesh" not in nd or "skin" not in nd:
            continue
        for prim in js["meshes"][nd["mesh"]]["primitives"]:
            at = prim.get("attributes", {})
            if "JOINTS_0" not in at:
                continue
            acc_i = at["JOINTS_0"]
            j0 = sa.read_accessor(js, bdat, acc_i).astype(np.int64)
            jn = j0.copy()
            for a, b in swap.items():
                jn[j0 == a] = b
            changed += int((jn != j0).sum())
            off, count, ncomp, ctype, stride = accessor_patch_target(
                js, acc_i)
            dt = sa.COMP[ctype]
            item = np.dtype(dt).itemsize * ncomp
            stride = stride or item
            q = jn.astype(dt)
            for i in range(count):
                o = off + i * stride
                binarr[o:o + item] = q[i].tobytes()
    rep["joint_slots_remapped"] = changed
    rep["applied"] = True
    jbytes = json.dumps(js, separators=(",", ":")).encode()
    jpad = (4 - len(jbytes) % 4) % 4
    jbytes += b" " * jpad
    bpad = (4 - len(binarr) % 4) % 4
    total = 12 + 8 + len(jbytes) + 8 + len(binarr) + bpad
    out = bytearray()
    out += b"glTF" + struct.pack("<II", 2, total)
    out += struct.pack("<I4s", len(jbytes), b"JSON") + jbytes
    out += struct.pack("<I4s", len(binarr) + bpad, b"BIN\x00") + binarr
    out += b"\x00" * bpad
    with open(outp, "wb") as f:
        f.write(bytes(out))
    print(json.dumps(rep, indent=1))
    return rep


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--report", default=None)
    a = ap.parse_args()
    rep = unmirror(a.inp, a.out)
    if a.report:
        with open(a.report, "w") as f:
            json.dump(rep, f, indent=1)


if __name__ == "__main__":
    main()
