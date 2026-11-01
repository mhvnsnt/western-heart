#!/usr/bin/env python3
"""tools/auto_rig/backends/smooth_weights.py — stretch-driven weight smoothing.

k-NN weight transfer (knn_transfer.py + apply_skin.py) copies weights
from a low-res donor onto a dense target. Wherever the target's volume
departs from the donor's surface (fur ruffs, paw gloves, hard part
seams inherited from the donor's own prim boundaries), adjacent target
verts land on very different donor weight vectors, and under animation
the edges between them tear — anim_check.py's edge-stretch gate
(p99.9 <= 2.5) fails by an order of magnitude.

This is the fix the repo already proved on pantera.glb itself
(repair_pantera_glb.py step 3: donor p99.9 11.27 -> 1.88), generalized
from one clip / one file to any skinned GLB and all its embedded clips:

  repeat:
    * evaluate every embedded clip (uniform frame sample) with
      anim_check's own AnimModel/_skin machinery
    * for every mesh edge whose posed/rest stretch exceeds
      --threshold, average the two endpoints' weight vectors
      (identical weights move together, so the seam behaves like
      fabric), cap at 4 influences, renormalize
    * patch JOINTS_0/WEIGHTS_0 in place (file + in-memory model)
  until no edge exceeds the threshold or --rounds runs out.

Weights are only ever averaged between verts that share a mesh edge —
surface topology is respected (a tail hanging near a leg does not
bleed leg weights; the two surfaces share no edges).

2026-11-01 (Negativo re-rig): every averaged vertex now writes the SAME
weights to all of its UV-seam copies (vertices at the same position).
Before, only the copy on the stretched edge changed, so seam copies
drifted apart (6,688 on Negativo, up to 0.546 L1) and the seam opened
into a crack under animation — invisible to every edge metric, since no
triangle edge spans a seam. The 4-influence limit is now CONTINUOUS
(5th-largest weight subtracted from the top 4): the hard top-4 cut kept
different 4th bones on neighbouring verts and itself caused stretch.

Usage:
    python3 smooth_weights.py --in MODEL.glb [--threshold 2.0]
        [--rounds 12] [--frames-per-clip 10] [--gate 2.5]
Then verify with anim_check.py (the official gate).
"""
import argparse
import struct
import sys

import numpy as np

sys.path.insert(0, '..')
sys.path.insert(0, '.')
import anim_check as ac  # noqa: E402
from validate import read_glb  # noqa: E402

COMP = {5121: ('B', 1), 5123: ('H', 2), 5125: ('I', 4), 5126: ('f', 4)}


def seam_groups(pos):
    """(order, start, gid): the copies of vertex v (same position, i.e. UV-seam duplicates, v included) are
    order[start[gid[v]]:start[gid[v] + 1]]."""
    key = np.round(np.asarray(pos, dtype=np.float64) / 1e-6).astype(np.int64)
    _, gid = np.unique(key, axis=0, return_inverse=True)
    gid = gid.reshape(-1)
    order = np.argsort(gid, kind='stable')
    start = np.r_[0, np.cumsum(np.bincount(gid))]
    return order, start, gid


def limit4(avg):
    """{joint: weight} -> (4 joints, 4 weights): CONTINUOUS 4-influence limit (the 5th-largest weight is
    subtracted from the top 4, renormalized), so a bone fades to 0 exactly where it leaves the top 4."""
    items = sorted(avg.items(), key=lambda kv: -kv[1])
    t = items[4][1] if len(items) > 4 else 0.0
    top = [(k, max(0.0, v - t)) for k, v in items[:4]]
    tot = sum(v for _, v in top)
    if tot <= 1e-12:  # 5+ exactly tied: fall back to the plain top 4
        top = items[:4]
        tot = sum(v for _, v in top) or 1.0
    jj = [k for k, _ in top] + [0] * (4 - len(top))
    ww = [v / tot for _, v in top] + [0.0] * (4 - len(top))
    return jj, ww


def bin_offset(raw):
    return 20 + struct.unpack_from('<I', raw, 12)[0] + 8


def prim_edges(prim):
    tris = prim['idx'].reshape(-1, 3)
    e = np.concatenate([tris[:, [0, 1]], tris[:, [1, 2]], tris[:, [2, 0]]])
    e = np.sort(e, 1)
    return np.unique(e, axis=0)


def _skin_fast(skin_m, prim, pos_h):
    """Identical math to anim_check._skin (sum_k w_k * M_jk @ p) but
    chunked per influence slot: _skin materializes (V,4,4,4), which on
    a ~1M-vert mesh costs ~0.5 GB and many seconds per frame."""
    J = skin_m.shape[0]
    ji = np.clip(prim['joints'], 0, J - 1)
    out = np.zeros((len(pos_h), 3), dtype=np.float64)
    for slot in range(4):
        w = prim['weights'][:, slot]
        if not np.any(w):
            continue
        M = skin_m[ji[:, slot]]                       # (V,4,4)
        p = np.einsum('vij,vj->vi', M, pos_h)[:, :3]  # (V,3)
        out += p * w[:, None]
    return out


def evaluate(model, clip_frames):
    """clip_frames: [(times, chans), ...] -> (per-prim bad edges, p99.9)."""
    bind = model.bind_world()
    jidx = np.array(model.joint_nodes)
    bind_skin = np.stack([bind[int(j)] @ model.ibm[k]
                          for k, j in enumerate(jidx)])
    frame_skins = []
    for times, chans in clip_frames:
        for t in times:
            w = model.eval_world(chans, t)
            frame_skins.append(np.stack([w[int(j)] @ model.ibm[k]
                                          for k, j in enumerate(jidx)]))
    bad_all, allr = {}, []
    for mi, prim in enumerate(model.prims):
        pos_h = np.concatenate(
            [prim['pos'], np.ones((len(prim['pos']), 1))], 1)
        edges = prim_edges(prim)
        srest = _skin_fast(bind_skin, prim, pos_h)
        rest_e = np.linalg.norm(srest[edges[:, 0]] - srest[edges[:, 1]],
                                axis=1)
        # Skip near-degenerate edges. Dense Tripo meshes (~1M verts, e.g. Waterfall) have no edge
        # over 1 cm, so the cutoff drops to half the median edge there instead of keeping nothing.
        keep = rest_e >= min(0.0098, 0.5 * float(np.median(rest_e)) if len(rest_e) else 0.0098)
        edges, rest_e = edges[keep], rest_e[keep]
        maxr = np.zeros(len(edges))
        for fs in frame_skins:
            cur = _skin_fast(fs, prim, pos_h)
            el = np.linalg.norm(cur[edges[:, 0]] - cur[edges[:, 1]], axis=1)
            maxr = np.maximum(maxr, el / rest_e)
        allr.append(maxr)
        bad_all[mi] = (edges, maxr)
    p999 = float(np.percentile(np.concatenate(allr), 99.9))
    return bad_all, p999


def write_vert_weights(path, model, prim_i, updates):
    js = model.js
    meta = []
    for mesh in js['meshes']:
        for p in mesh['primitives']:
            at = p.get('attributes', {})
            if 'JOINTS_0' in at and 'POSITION' in at:
                meta.append((at['JOINTS_0'], at['WEIGHTS_0']))
    raw = bytearray(open(path, 'rb').read())
    boff = bin_offset(raw)
    for acc_i, is_j in ((meta[prim_i][0], True), (meta[prim_i][1], False)):
        acc = js['accessors'][acc_i]
        bv = js['bufferViews'][acc['bufferView']]
        base = boff + bv.get('byteOffset', 0) + acc.get('byteOffset', 0)
        fmt, size = COMP[acc['componentType']]
        stride = bv.get('byteStride', 0) or 4 * size
        for v, (jj, ww) in updates.items():
            vals = jj if is_j else ww
            for k in range(4):
                struct.pack_into('<' + fmt, raw,
                                 base + v * stride + k * size,
                                 vals[k] if is_j else float(vals[k]))
    open(path, 'wb').write(raw)


def smooth(path, threshold=2.0, rounds=12, frames_per_clip=10, gate=2.5):
    model = ac.AnimModel(path)
    clip_frames = []
    for anim in model.js.get('animations', []):
        times, chans = model.animation_frames(anim, frames_per_clip)
        clip_frames.append((times, chans))
        print(f'clip {anim.get("name")}: {len(times)} sampled frames')
    if not clip_frames:
        raise SystemExit('no animations to evaluate against')

    # bind-consistency: skinned-at-bind must equal stored positions
    bind = model.bind_world()
    jidx = np.array(model.joint_nodes)
    bind_skin = np.stack([bind[int(j)] @ model.ibm[k]
                          for k, j in enumerate(jidx)])
    prim = model.prims[0]
    pos_h = np.concatenate([prim['pos'], np.ones((len(prim['pos']), 1))], 1)
    dev = np.abs(_skin_fast(bind_skin, prim, pos_h) - prim['pos']).max()
    print(f'bind-consistency max dev: {dev:.2e} m')

    seams = {mi: seam_groups(p['pos']) for mi, p in enumerate(model.prims)}
    for rnd in range(rounds):
        bad_all, p999 = evaluate(model, clip_frames)
        nbad = {mi: int((mr > threshold).sum())
                for mi, (_, mr) in bad_all.items()}
        print(f'round {rnd}: edge p99.9 = {p999:.2f} '
              f'(edges > {threshold}: {nbad})')
        if p999 <= gate and sum(nbad.values()) == 0:
            print('SMOOTH_OK — no edges above threshold')
            return
        changed = False
        for mi, (edges, maxr) in bad_all.items():
            prim = model.prims[mi]
            J = prim['joints'].copy()
            W = prim['weights'].copy()
            updates = {}
            s_order, s_start, s_gid = seams[mi]

            def vec(v):
                d = {}
                for k in range(4):
                    if W[v][k] > 0:
                        j = int(J[v][k])
                        d[j] = d.get(j, 0.0) + float(W[v][k])
                return d

            bad_idx = np.nonzero(maxr > threshold)[0]
            order = bad_idx[np.argsort(-maxr[bad_idx])]
            for ei in order:
                a, b = int(edges[ei][0]), int(edges[ei][1])
                da, db = vec(a), vec(b)
                if da == db:
                    continue
                avg = {k: (da.get(k, 0.0) + db.get(k, 0.0)) / 2.0
                       for k in set(da) | set(db)}
                jj, ww = limit4(avg)
                for v in (a, b):
                    g = s_gid[v]
                    for u in s_order[s_start[g]:s_start[g + 1]]:  # v and its UV-seam copies
                        u = int(u)
                        J[u] = jj
                        W[u] = ww
                        updates[u] = (jj, ww)
            if updates:
                changed = True
                prim['joints'][:] = J
                prim['weights'][:] = W
                write_vert_weights(path, model, mi, updates)
                print(f'  prim {mi}: averaged {len(updates)} verts')
        if not changed:
            print('no changes — converged')
            return
    bad_all, p999 = evaluate(model, clip_frames)
    print(f'final: edge p99.9 = {p999:.2f}')
    if p999 > gate:
        raise SystemExit(f'smoothing did not reach the {gate} gate')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--in', dest='inp', required=True)
    ap.add_argument('--threshold', type=float, default=2.0)
    ap.add_argument('--rounds', type=int, default=12)
    ap.add_argument('--frames-per-clip', type=int, default=10)
    ap.add_argument('--gate', type=float, default=2.5)
    args = ap.parse_args()
    smooth(args.inp, args.threshold, args.rounds,
           args.frames_per_clip, args.gate)
    print('smooth complete')


if __name__ == '__main__':
    main()
