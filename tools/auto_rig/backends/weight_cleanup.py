#!/usr/bin/env python3
"""tools/auto_rig/backends/weight_cleanup.py — automatic skin-weight repair.

Repairs, in a versioned copy (the input is never modified), the weight
defects skin_audit.py measures:

  1. CONTAMINATION PRUNE — influences >= 0.05 on body joints whose bone
     segment is far from the vertex while another joint is near it
     (skin_audit's rule) are zeroed. The hand-weighted-to-a-tail class.
  2. DEAD-JOINT REVIVAL — a major joint carrying zero weight (e.g.
     baek.glb's LeftHand/RightHand: hand animation channels that move
     nothing) receives 50% of the weight of the verts whose nearest
     bone segment IS that joint and whose dominant joint is its chain
     parent or child — proximity reassignment, the standard fix.
  3. UNWEIGHTED FILL — verts left with no weight get their nearest
     joint at 1.0 (unweighted verts crash glTF exporters / the game).
  4. EDGE SMOOTHING — one Laplacian pass over mesh edges on the global
     weight vectors (topology-respecting: weights never bleed across
     disconnected surfaces), then re-prune.
  5. PRUNE + NORMALIZE — weights < 0.02 dropped, top-4 kept, every
     vertex renormalized to sum exactly 1.

GLB container is rebuilt (JSON chunk re-padded, BIN patched in place —
accessor shapes never change, so byte lengths are stable).

    python3 weight_cleanup.py --in MODEL.glb --out FIXED.glb
        [--smooth-iters 1] [--revive-frac 0.5] [--report R.json]
Exit 0 always on success; the JSON report lists every change count.
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

BODY_RE = re.compile(
    r"^(Left|Right)?(Hips|Spine|Neck|Head|Shoulder|Arm|ForeArm|Hand|"
    r"UpLeg|Leg|Foot|ToeBase)|Tail\d")
HELPER_RE = re.compile(r"Thumb|Index|Middle|Ring|Pinky|Palm|Breast|Pelvis")


def joint_geometry(js, bdat):
    skin = js["skins"][0]
    joint_nodes = skin["joints"]
    nodes = js.get("nodes", [])
    names = [nodes[j].get("name", "") for j in joint_nodes]
    if "inverseBindMatrices" in skin:
        ibm = sa.read_accessor(js, bdat, skin["inverseBindMatrices"])
        jpos = np.array([np.linalg.inv(
            ibm[i].reshape(4, 4, order="F"))[:3, 3]
            for i in range(len(joint_nodes))])
    else:
        worlds, _ = sa.world_matrices(js)
        jpos = np.array([worlds[j][:3, 3] for j in joint_nodes])
    name_to_joint = {n: i for i, n in enumerate(names)}
    node_to_joint = {n: i for i, n in enumerate(joint_nodes)}
    child_joint = {}
    parent_joint = {}
    for i, n in enumerate(joint_nodes):
        want = sa.CANON_CHILD.get(names[i])
        if want in name_to_joint:
            child_joint[i] = name_to_joint[want]
        else:
            for c in nodes[n].get("children", []):
                if c in node_to_joint:
                    child_joint[i] = node_to_joint[c]
                    break
    for i, c in child_joint.items():
        parent_joint.setdefault(c, i)
    # Canonical chain mapping names ONE child per joint (Hips->Spine),
    # so joints whose only incoming edge is a non-canonical node-tree
    # child slot (LeftUpLeg/RightUpLeg: Hips' other children) end up
    # with NO parent — and the dead-joint revival then has neither a
    # parent territory nor the parent in its chain set, so a dead
    # UpLeg can never be revived (demonio bloodline-ember, 2026-10-31:
    # LeftLeg revived, LeftUpLeg stayed at zero mass). Fill missing
    # parents from the full node tree; canonical parents win where
    # both exist.
    for i, n in enumerate(joint_nodes):
        for c in nodes[n].get("children", []):
            if c in node_to_joint:
                parent_joint.setdefault(node_to_joint[c], i)
    seg_b = []
    for i in range(len(jpos)):
        if i in child_joint:
            seg_b.append(jpos[child_joint[i]])
        elif i in parent_joint:
            d = jpos[i] - jpos[parent_joint[i]]
            seg_b.append(jpos[i] + d)
        else:
            seg_b.append(jpos[i] + np.array([0.0, 0.05, 0.0]))
    return names, jpos, np.array(seg_b), child_joint, parent_joint, \
        node_to_joint


def accessor_patch_target(js, acc_idx):
    """(byte offset into BIN, count, ncomp, componentType) for an accessor."""
    acc = js["accessors"][acc_idx]
    bv = js["bufferViews"][acc["bufferView"]]
    off = bv.get("byteOffset", 0) + acc.get("byteOffset", 0)
    return off, acc["count"], sa.NCOMP[acc["type"]], acc["componentType"], \
        bv.get("byteStride", 0)


def write_accessor(binarr, js, acc_idx, values, normalized=False):
    """Write a (count, ncomp) array back into the BIN bytearray in the
    accessor's own component type. WEIGHTS accessors are normalized
    (0..1 maps to the full int range); JOINTS accessors are raw
    indices and must be written verbatim — scaling them by 255 was
    the first version's bug (joint 1 became the 255 sentinel)."""
    off, count, ncomp, ctype, stride = accessor_patch_target(js, acc_idx)
    dt = sa.COMP[ctype]
    item = np.dtype(dt).itemsize * ncomp
    stride = stride or item
    if ctype == 5121 and normalized:
        q = np.clip(np.round(values * 255.0), 0, 255).astype(np.uint8)
    elif ctype == 5123 and normalized:
        q = np.clip(np.round(values * 65535.0), 0, 65535).astype(np.uint16)
    elif ctype == 5121:
        q = values.astype(np.uint8)
    elif ctype == 5123:
        q = values.astype(np.uint16)
    elif ctype == 5125:
        q = values.astype(np.uint32)
    else:
        q = values.astype(np.float32)
    flat = q.reshape(count, ncomp)
    for i in range(count):
        o = off + i * stride
        binarr[o:o + item] = flat[i].tobytes()
    return


def cleanup(inp, outp, smooth_iters=1, revive_frac=0.5):
    with open(inp, "rb") as f:
        raw = f.read()
    js, bdat = read_glb(inp)
    binarr = bytearray(bdat)
    names, jpos, seg_b, child_joint, parent_joint, node_to_joint = \
        joint_geometry(js, bdat)
    nj = len(names)
    body_joint = np.array([bool(BODY_RE.match(n)) for n in names])
    rep = {"in": inp, "out": outp, "changes": {}}
    tot_pruned = tot_revived_verts = tot_filled = 0

    # GLOBAL dead-major set: a joint is dead only if it carries ~no
    # weight in the WHOLE model. (Per-prim deadness is meaningless on
    # multi-part exports — every part prim leaves most joints at zero,
    # and reviving per-prim sprays weights across the whole body.)
    gtot = np.zeros(nj)
    gymin, gymax = np.inf, -np.inf
    for nd0 in js.get("nodes", []):
        if "mesh" not in nd0 or "skin" not in nd0:
            continue
        for prim0 in js["meshes"][nd0["mesh"]]["primitives"]:
            at0 = prim0.get("attributes", {})
            if "JOINTS_0" not in at0:
                continue
            j0 = sa.read_accessor(js, bdat, at0["JOINTS_0"]).astype(np.int64)
            w0 = sa.read_weights(js, bdat, at0["WEIGHTS_0"])
            np.add.at(gtot, j0.reshape(-1), w0.reshape(-1))
            if "POSITION" in at0:
                pp0 = sa.read_accessor(js, bdat, at0["POSITION"])
                gymin = min(gymin, float(pp0[:, 1].min()))
                gymax = max(gymax, float(pp0[:, 1].max()))
    model_height = (gymax - gymin) if np.isfinite(gymin) else 1.8
    dead_global = [j for j in range(nj)
                   if gtot[j] < 1e-4 and body_joint[j]
                   and not HELPER_RE.search(names[j])]
    rep["dead_major_joints"] = [names[j] for j in dead_global]

    # canonical descendant names (chain map BFS over names)
    canon_kids = {}
    for a_, b_ in sa.CANON_CHILD.items():
        canon_kids.setdefault(a_, []).append(b_)
    def canon_desc(name):
        seen, stack = set(), [name]
        while stack:
            x = stack.pop()
            for y in canon_kids.get(x, []):
                if y not in seen:
                    seen.add(y)
                    stack.append(y)
        return seen

    for nd in js.get("nodes", []):
        if "mesh" not in nd or "skin" not in nd:
            continue
        for prim in js["meshes"][nd["mesh"]]["primitives"]:
            at = prim.get("attributes", {})
            if "JOINTS_0" not in at or "POSITION" not in at:
                continue
            pos = sa.read_accessor(js, bdat, at["POSITION"]).astype(
                np.float64)
            jj = sa.read_accessor(js, bdat, at["JOINTS_0"]).astype(np.int64)
            ww = sa.read_weights(js, bdat, at["WEIGHTS_0"])
            n = len(pos)
            height = float(pos[:, 1].max() - pos[:, 1].min()) or 1.0
            # segment distances (verts x joints), chunked
            segd = np.empty((n, nj), dtype=np.float32)
            for j in range(nj):
                segd[:, j] = sa.seg_dist(pos, jpos[j], seg_b[j])
            nearest = segd.min(axis=1)
            nearest_j = segd.argmin(axis=1)

            # 1. contamination prune (per slot)
            d_slot = segd[np.arange(n)[:, None], jj]
            margin = np.maximum(0.10 * height, 2.5 * nearest)
            bad = (d_slot > (nearest + margin)[:, None]) & (ww >= 0.05) & \
                body_joint[jj]
            tot_pruned += int(ww[bad].size and np.sum(bad))
            ww = np.where(bad, 0.0, ww)

            # 2. revive globally dead major joints by proximity
            dead = dead_global
            # descendant sets over the FULL node-tree joint children
            # (not just the canonical chain child): a dead Hand's verts
            # are dominated by its finger joints, and fingers are
            # siblings in the chain map, not descendants of it.
            full_children = {}
            for i2, n2 in enumerate(js["skins"][0]["joints"]):
                full_children[i2] = [node_to_joint[c]
                                     for c in js["nodes"][n2].get(
                                         "children", [])
                                     if c in node_to_joint]
            desc = {}
            for j0 in range(nj):
                seen, stack = set(), [j0]
                while stack:
                    x = stack.pop()
                    for y in full_children.get(x, []):
                        if y not in seen:
                            seen.add(y)
                            stack.append(y)
                desc[j0] = seen
            for j in dead:
                chain = {x for x in (parent_joint.get(j),
                                     child_joint.get(j)) if x is not None}
                chain |= desc[j]
                fam = {i2 for i2, n2 in enumerate(names)
                       if n2.startswith(names[j]) or
                       n2 in canon_desc(names[j])}
                chain |= fam
                if not chain:
                    continue
                dom = jj[np.arange(n), np.argmax(ww, axis=1)]
                pj = parent_joint.get(j)
                territory = (nearest_j == j)
                if pj is not None:
                    territory = territory | (segd[:, j] <= segd[:, pj])
                cand = np.where(territory &
                                np.isin(dom, list(chain)) &
                                (ww.sum(axis=1) > 0))[0]
                for vi in cand:
                    slots = {}
                    for k in range(jj.shape[1]):
                        if ww[vi, k] > 0:
                            slots[int(jj[vi, k])] = slots.get(
                                int(jj[vi, k]), 0.0) + float(ww[vi, k])
                    tot = sum(slots.values())
                    if tot <= 0:
                        continue
                    for k2 in slots:
                        slots[k2] *= (1.0 - revive_frac)
                    slots[j] = slots.get(j, 0.0) + revive_frac * tot
                    top = sorted(slots.items(), key=lambda kv: -kv[1])[:4]
                    for k in range(jj.shape[1]):
                        if k < len(top):
                            jj[vi, k], ww[vi, k] = top[k][0], top[k][1]
                        else:
                            jj[vi, k], ww[vi, k] = top[0][0], 0.0
                    tot_revived_verts += 1

            # 3. unweighted fill
            sums = ww.sum(axis=1)
            empty = np.where(sums < 1e-6)[0]
            for vi in empty:
                jj[vi] = nearest_j[vi]
                ww[vi] = 0.0
                ww[vi, 0] = 1.0
                jj[vi, 1:] = nearest_j[vi]
            tot_filled += int(len(empty))

            # 4. edge smoothing on global weight vectors
            if smooth_iters and "indices" in prim and n * nj <= 40_000_000:
                idx = sa.read_accessor(js, bdat, prim["indices"]).astype(
                    np.int64).reshape(-1, 3)
                e = np.concatenate([idx[:, [0, 1]], idx[:, [1, 2]],
                                    idx[:, [2, 0]]])
                e = np.unique(np.sort(e, 1), axis=0)
                dense = np.zeros((n, nj))
                # Accumulate, never put_along_axis: glTF rows may repeat
                # a joint across slots (padding), and put_along_axis
                # lets the last (often 0.0) slot win, silently deleting
                # that joint's real weight (found on the synthetic
                # fixture: Hips 1.0 -> 0.0).
                rows_i = np.repeat(np.arange(n), jj.shape[1])
                np.add.at(dense, (rows_i, jj.reshape(-1)),
                          ww.reshape(-1))
                for _ in range(smooth_iters):
                    acc = dense.copy()
                    cnt = np.ones(n)
                    np.add.at(acc, e[:, 0], dense[e[:, 1]])
                    np.add.at(acc, e[:, 1], dense[e[:, 0]])
                    np.add.at(cnt, e[:, 0], 1)
                    np.add.at(cnt, e[:, 1], 1)
                    dense = 0.75 * dense + 0.25 * (acc / cnt[:, None])
                # back to top-4 slots
                top_idx = np.argsort(-dense, axis=1)[:, :4]
                top_w = np.take_along_axis(dense, top_idx, axis=1)
                jj = top_idx.astype(np.int64)
                ww = top_w

            # 4b. post-smoothing far-prune: smoothing bleeds small
            # weights across joint boundaries; re-apply the audit's
            # contamination rule so cleanup converges to audit-clean.
            nearest_d = segd.min(axis=1)
            margin = np.maximum(0.10 * model_height, 2.5 * nearest_d)
            slot_j = jj
            slot_d = np.take_along_axis(
                segd, np.clip(slot_j, 0, nj - 1), axis=1)
            far = (ww >= 0.05) & (slot_d > (nearest_d + margin)[:, None])
            far &= np.array([body_joint[int(j)] for j in range(nj)])[
                np.clip(slot_j, 0, nj - 1)]
            if far.any():
                tot_pruned += int(far.sum())
                ww = np.where(far, 0.0, ww)

            # 5. prune + normalize
            ww = np.where(ww < 0.02, 0.0, ww)
            # keep top-4 by weight within slots
            order = np.argsort(-ww, axis=1)
            jj = np.take_along_axis(jj, order, axis=1)
            ww = np.take_along_axis(ww, order, axis=1)
            sums = ww.sum(axis=1, keepdims=True)
            dead_rows = (sums[:, 0] < 1e-6)
            if dead_rows.any():
                for vi in np.where(dead_rows)[0]:
                    jj[vi] = nearest_j[vi]
                    ww[vi] = 0.0
                    ww[vi, 0] = 1.0
                    jj[vi, 1:] = nearest_j[vi]
                sums = ww.sum(axis=1, keepdims=True)
            ww = ww / np.maximum(sums, 1e-9)

            write_accessor(binarr, js, at["JOINTS_0"], jj)
            write_accessor(binarr, js, at["WEIGHTS_0"], ww,
                           normalized=True)

    rep["changes"] = {"contaminated_slots_pruned": tot_pruned,
                      "revived_verts": tot_revived_verts,
                      "unweighted_filled": tot_filled}
    # rebuild container
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
    return rep


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--smooth-iters", type=int, default=1)
    ap.add_argument("--revive-frac", type=float, default=0.5)
    ap.add_argument("--report", default=None)
    a = ap.parse_args()
    rep = cleanup(a.inp, a.out, a.smooth_iters, a.revive_frac)
    txt = json.dumps(rep, indent=1)
    print(txt)
    if a.report:
        with open(a.report, "w") as f:
            f.write(txt)


if __name__ == "__main__":
    main()
