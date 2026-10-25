#!/usr/bin/env python3
"""tools/auto_rig/reskin_pantera_weights.py — re-derive pantera.glb skin weights.

Replaces the skin weights (JOINTS_0/WEIGHTS_0) in game/assets/models/pantera.glb
with weights transferred from game/assets/models/steve-fox.glb via k-NN, plus
rule-based corrections. Everything else in the GLB (skeleton, IBMs,
animations, materials, mesh order) is preserved byte-for-byte.

Why: the shipped pantera.glb weights were measured (2026-10-21) to be
systematically wrong — forearm verts 86% weighted to hand/spine instead of
forearm, waist 62% to leg joints, tail 77% to leg/foot joints, left hand 17%
to spine. Under any non-bind pose this produces the in-game "stretching
forearms/hands, crumpled legs, hand dragged toward the tail" symptoms.
steve-fox.glb carries the same 49-joint Mixamo skeleton with clean weights
(92%+ correct on forearms/shins/biceps), so it is the donor.

Pipeline (all rule-based, no hand-painted weights):
  1. k-NN (k=4, inverse-distance) from the donor's full concatenated mesh,
     in bind space after bbox normalize (feet y=0, height match). Target and
     donor both face -Z in T-pose, so no --rotate-y is needed.
  2. Side-constrained matching: target verts with |x|>3cm only match donor
     verts on the same side (prevents L/R bleed across the midline).
  3. Tail rule: the leopard tail (z<-0.15, behind the butt; the donor has no
     tail) blends from k-NN weights at the base to rigid Hips at the tip
     over a 12cm smoothstep — tear-free, follows the pelvis.
  4. Anatomical side correction: any influence whose joint is on the opposite
     side of the vertex (x sign vs Left/Right joint name) is mirrored to the
     correct side; duplicates merged, renormalized.
  5. Seam blend: iteratively average weight vectors across triangle edges
     whose Idle-pose/rest length ratio exceeds 2.0 (same method as
     repair_pantera_glb.py step 3), until anim_check's 2.5 gate passes.

Usage (run from tools/auto_rig):
    python3 reskin_pantera_weights.py \\
        --in ../../game/assets/models/pantera.glb \\
        --donor ../../game/assets/models/steve-fox.glb \\
        --out ../../game/assets/models/pantera.glb
Then verify:
    python3 anim_check.py --in ../../game/assets/models/pantera.glb
    python3 validate.py --in ../../game/assets/models/pantera.glb
"""
import argparse
import json
import struct
import sys

import numpy as np

sys.path.insert(0, '.')
import anim_check as ac  # noqa: E402
from validate import read_glb  # noqa: E402

COMP = {5121: np.uint8, 5123: np.uint16, 5125: np.uint32, 5126: np.float32}
COMP_FMT = {5121: 'B', 5123: 'H', 5125: 'I', 5126: 'f'}
K = 4
SIDE_TOL = 0.03   # |x| above this: same-side k-NN matching only
SIDE_X = 0.025    # |x| above this: anatomical side correction applies
TAIL_Z = -0.15    # verts behind this plane (and y in (0, 1.15)) are tail
TAIL_BLEND_M = 0.12


def acc_arr(js, bdat, ai):
    acc = js["accessors"][ai]
    bv = js["bufferViews"][acc["bufferView"]]
    off = bv.get("byteOffset", 0) + acc.get("byteOffset", 0)
    n, ct, typ = acc["count"], acc["componentType"], acc["type"]
    per = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4}[typ]
    arr = np.frombuffer(bdat, dtype=COMP[ct], count=n * per, offset=off)
    return arr.reshape(n, per)


def bin_offset(raw):
    return 20 + struct.unpack_from('<I', raw, 12)[0] + 8


def knn_transfer(tjs, tbdat, djs, dbdat, log):
    from scipy.spatial import cKDTree  # noqa: E402
    # donor: all prims concatenated
    dpos, dj, dw = [], [], []
    for m in djs["meshes"]:
        for p in m["primitives"]:
            at = p["attributes"]
            if "JOINTS_0" not in at:
                continue
            dpos.append(acc_arr(djs, dbdat, at["POSITION"]).astype(np.float64))
            dj.append(acc_arr(djs, dbdat, at["JOINTS_0"]).astype(np.int64))
            dw.append(acc_arr(djs, dbdat, at["WEIGHTS_0"]).astype(np.float64))
    dpos = np.concatenate(dpos); dj = np.concatenate(dj); dw = np.concatenate(dw)
    dnames = [djs["nodes"][j].get("name", "") for j in djs["skins"][0]["joints"]]
    log.append(f"donor verts={len(dpos)}")
    # target prims
    tprims = []
    for mi, m in enumerate(tjs["meshes"]):
        for pi, p in enumerate(m["primitives"]):
            at = p["attributes"]
            if "JOINTS_0" not in at:
                continue
            tprims.append((mi, pi, at,
                           acc_arr(tjs, tbdat, at["POSITION"]).astype(np.float64)))
    # global bbox normalize
    tall = np.concatenate([t[3] for t in tprims])
    tmin, tmax = tall.min(0), tall.max(0)
    dmin, dmax = dpos.min(0), dpos.max(0)
    s = (dmax[1] - dmin[1]) / (tmax[1] - tmin[1])
    norm = lambda p: (p - tmin) * s + dmin  # noqa: E731
    log.append(f"normalize scale={s:.4f}")
    # side-split donor trees
    trees, gidx = {}, {}
    for sgn, sel in ((-1, dpos[:, 0] < -0.015), (1, dpos[:, 0] > 0.015),
                     (0, np.abs(dpos[:, 0]) <= 0.015)):
        trees[sgn] = cKDTree(dpos[sel]); gidx[sgn] = np.nonzero(sel)[0]
    njoints = int(dj.max()) + 1
    results = []
    for mi, pi, at, pos in tprims:
        pn = norm(pos)
        n = len(pos)
        side = np.sign(pn[:, 0]); side[np.abs(pn[:, 0]) <= SIDE_TOL] = 0
        dist = np.empty((n, K)); idx = np.empty((n, K), dtype=np.int64)
        for sgn in (-1, 1, 0):
            m = side == sgn
            if m.sum() == 0:
                continue
            d, ii = trees[sgn].query(pn[m], k=K)
            dist[m] = d; idx[m] = gidx[sgn][ii]
        w = 1.0 / (dist + 1e-9); wsum = w.sum(1, keepdims=True)
        accum = np.zeros((n, njoints))
        for ki in range(K):
            np.add.at(accum, (np.arange(n)[:, None], dj[idx[:, ki]]),
                      (w[:, ki] / wsum[:, 0])[:, None] * dw[idx[:, ki]])
        top = np.argsort(-accum, axis=1)[:, :4]
        rows = np.arange(n)[:, None]
        tw = accum[rows, top]
        tw = tw / tw.sum(1, keepdims=True).clip(min=1e-12)
        results.append([at, top.astype(np.uint16), tw, pos])
    return results, dnames, tprims


def apply_tail(results, log):
    n_tail = 0
    for r in results:
        at, tj, tw, pos = r
        is_tail = (pos[:, 2] < TAIL_Z) & (pos[:, 1] < 1.15) & \
                  (pos[:, 1] > 0.0) & (np.abs(pos[:, 0]) < 0.25)
        if is_tail.sum() == 0:
            continue
        d = np.clip((TAIL_Z - pos[is_tail, 2]) / TAIL_BLEND_M, 0, 1)
        ss = d * d * (3 - 2 * d)  # smoothstep 0@base -> 1@tip
        tw_t = tw[is_tail] * (1 - ss)[:, None]
        tj_t = tj[is_tail]
        hj = np.zeros((is_tail.sum(), 5), dtype=np.int64)
        hw = np.zeros((is_tail.sum(), 5))
        hj[:, 0] = 0; hw[:, 0] = ss  # joint 0 = Hips
        hj[:, 1:] = tj_t; hw[:, 1:] = tw_t
        merged_j = np.zeros((is_tail.sum(), 4), dtype=np.int64)
        merged_w = np.zeros((is_tail.sum(), 4))
        for ri in range(is_tail.sum()):
            dd = {}
            for k in range(5):
                dd[int(hj[ri, k])] = dd.get(int(hj[ri, k]), 0.0) + float(hw[ri, k])
            topk = sorted(dd.items(), key=lambda kv: -kv[1])[:4]
            tot = sum(v for _, v in topk)
            for k, (jj, ww) in enumerate(topk):
                merged_j[ri, k] = jj; merged_w[ri, k] = ww / tot
        tj[is_tail] = merged_j.astype(np.uint16)
        tw[is_tail] = merged_w
        n_tail += int(is_tail.sum())
    log.append(f"tail verts blended to Hips: {n_tail}")


def side_correct(results, dnames, log):
    mirror = {}
    for i, nm in enumerate(dnames):
        if nm.startswith("Left"):
            r = "Right" + nm[4:]
            if r in dnames:
                mirror[i] = dnames.index(r)
        elif nm.startswith("Right"):
            lft = "Left" + nm[5:]
            if lft in dnames:
                mirror[i] = dnames.index(lft)
    n_fix = 0
    for r in results:
        at, tj, tw, pos = r
        for vi in range(len(tj)):
            x = pos[vi, 0]
            if abs(x) <= SIDE_X:
                continue
            changed = False
            for k in range(4):
                j = int(tj[vi, k]); nm = dnames[j]
                if x < 0 and nm.startswith("Right") and j in mirror:
                    tj[vi, k] = mirror[j]; changed = True
                elif x > 0 and nm.startswith("Left") and j in mirror:
                    tj[vi, k] = mirror[j]; changed = True
            if changed:
                dd = {}
                for k in range(4):
                    j = int(tj[vi, k])
                    dd[j] = dd.get(j, 0.0) + float(tw[vi, k])
                topk = sorted(dd.items(), key=lambda kv: -kv[1])[:4]
                tot = sum(v for _, v in topk)
                for k in range(4):
                    if k < len(topk):
                        tj[vi, k], tw[vi, k] = topk[k][0], topk[k][1] / tot
                    else:
                        tj[vi, k], tw[vi, k] = 0, 0.0
                n_fix += 1
    log.append(f"side-corrected verts: {n_fix} (mirror pairs: {len(mirror)//2})")


def write_weights(path, js, tjs, results):
    raw = bytearray(open(path, "rb").read())
    boff = bin_offset(raw)
    res_by_attr = {(id(r[0])): r for r in results}
    for mi, m in enumerate(tjs["meshes"]):
        for pi, p in enumerate(m["primitives"]):
            at = p["attributes"]
            if "JOINTS_0" not in at:
                continue
            r = res_by_attr[id(at)]
            tj, tw = r[1], r[2]
            for ai, arr, is_j in ((at["JOINTS_0"], tj, True),
                                  (at["WEIGHTS_0"], tw, False)):
                acc = tjs["accessors"][ai]
                bv = tjs["bufferViews"][acc["bufferView"]]
                base = boff + bv.get("byteOffset", 0) + acc.get("byteOffset", 0)
                fmt, size = COMP_FMT[acc["componentType"]], \
                    {5121: 1, 5123: 2, 5125: 4, 5126: 4}[acc["componentType"]]
                stride = bv.get("byteStride", 0) or 4 * size
                dt = {5121: "<u1", 5123: "<u2", 5125: "<u4",
                      5126: "<f4"}[acc["componentType"]]
                packed = np.ascontiguousarray(arr).astype(dt)
                assert len(packed.tobytes()) == acc["count"] * 4 * size
                for v in range(len(packed)):
                    for k in range(4):
                        struct.pack_into("<" + fmt, raw,
                                         base + v * stride + k * size,
                                         int(packed[v, k]) if is_j
                                         else float(packed[v, k]))
    open(path, "wb").write(raw)


def seam_blend(path, log, rounds=20):
    for rnd in range(rounds):
        model = ac.AnimModel(path)
        js = model.js
        anim = next(a for a in js["animations"] if a.get("name") == "Idle")
        times, chans = model.animation_frames(anim, 120)
        bind = model.bind_world()
        jidx = np.array(model.joint_nodes)
        bind_skin = np.stack([bind[int(j)] @ model.ibm[k]
                              for k, j in enumerate(jidx)])
        frame_skin = []
        for t in times:
            w = model.eval_world(chans, t)
            frame_skin.append(np.stack([w[int(j)] @ model.ibm[k]
                                        for k, j in enumerate(jidx)]))
        bad, allr = {}, []
        for mi, prim in enumerate(model.prims):
            pos_h = np.concatenate([prim["pos"],
                                    np.ones((len(prim["pos"]), 1))], 1)
            tris = prim["idx"].reshape(-1, 3)
            e = np.concatenate([tris[:, [0, 1]], tris[:, [1, 2]],
                                tris[:, [2, 0]]])
            e = np.sort(e, 1)
            edges = np.unique(e, axis=0)
            srest = ac._skin(model, bind_skin, prim, pos_h)
            rest_e = np.linalg.norm(srest[edges[:, 0]] - srest[edges[:, 1]],
                                    axis=1)
            keep = rest_e >= 0.0098
            edges, rest_e = edges[keep], rest_e[keep]
            maxr = np.zeros(len(edges))
            for fi in range(len(times)):
                cur = ac._skin(model, frame_skin[fi], prim, pos_h)
                el = np.linalg.norm(cur[edges[:, 0]] - cur[edges[:, 1]], axis=1)
                maxr = np.maximum(maxr, el / rest_e)
            allr.append(maxr)
            for ei in np.nonzero(maxr > 2.0)[0]:
                bad.setdefault(mi, []).append(
                    (float(maxr[ei]), int(edges[ei][0]), int(edges[ei][1])))
        p999 = float(np.percentile(np.concatenate(allr), 99.9))
        nbad = sum(len(v) for v in bad.values())
        if rnd % 5 == 0 or not bad:
            log.append(f"seam blend round {rnd}: p99.9={p999:.2f} "
                       f"bad_edges={nbad}")
        if not bad:
            return
        for mi, ebs in bad.items():
            prim = model.prims[mi]
            J = prim["joints"].copy(); W = prim["weights"].copy()
            updates = {}

            def vec(v):
                d = {}
                for k in range(4):
                    if W[v][k] > 0:
                        j = int(J[v][k])
                        d[j] = d.get(j, 0.0) + float(W[v][k])
                return d

            for _ratio, a, b in sorted(ebs, reverse=True):
                da, db = vec(a), vec(b)
                avg = {k: (da.get(k, 0.0) + db.get(k, 0.0)) / 2.0
                       for k in set(da) | set(db)}
                top = sorted(avg.items(), key=lambda kv: -kv[1])[:4]
                tot = sum(v for _, v in top)
                jj = [k for k, _ in top] + [0] * (4 - len(top))
                ww = [v / tot for _, v in top] + [0.0] * (4 - len(top))
                for v in (a, b):
                    J[v] = jj; W[v] = ww; updates[v] = (jj, ww)
            if updates:
                _write_vert_weights(path, model, mi, updates)
    raise SystemExit("seam blend did not converge")


def _write_vert_weights(path, model, prim_i, updates):
    js = model.js
    meta = []
    for mesh in js["meshes"]:
        for p in mesh["primitives"]:
            at = p.get("attributes", {})
            if "JOINTS_0" in at and "POSITION" in at:
                meta.append((at["JOINTS_0"], at["WEIGHTS_0"]))
    raw = bytearray(open(path, "rb").read())
    boff = bin_offset(raw)
    for acc_i, is_j in ((meta[prim_i][0], True), (meta[prim_i][1], False)):
        acc = js["accessors"][acc_i]
        bv = js["bufferViews"][acc["bufferView"]]
        base = boff + bv.get("byteOffset", 0) + acc.get("byteOffset", 0)
        fmt = COMP_FMT[acc["componentType"]]
        size = {5121: 1, 5123: 2, 5125: 4, 5126: 4}[acc["componentType"]]
        stride = bv.get("byteStride", 0) or 4 * size
        for v, (jj, ww) in updates.items():
            vals = jj if is_j else ww
            for k in range(4):
                struct.pack_into("<" + fmt, raw,
                                 base + v * stride + k * size,
                                 vals[k] if is_j else float(vals[k]))
    open(path, "wb").write(raw)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--donor", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    log = []
    tjs, tbdat = read_glb(args.inp)[:2]
    djs, dbdat = read_glb(args.donor)[:2]
    results, dnames, tprims = knn_transfer(tjs, tbdat, djs, dbdat, log)
    apply_tail(results, log)
    side_correct(results, dnames, log)
    # copy input -> output, then write weights in place
    open(args.out, "wb").write(open(args.inp, "rb").read())
    write_weights(args.out, tjs, tjs, results)
    log.append("weights written")
    seam_blend(args.out, log)
    print("RESKIN_OK")
    for line in log:
        print(" ", line)
    import hashlib
    sha = hashlib.sha256(open(args.out, "rb").read()).hexdigest()
    print(f"  out={args.out} sha256={sha}")


if __name__ == "__main__":
    main()
