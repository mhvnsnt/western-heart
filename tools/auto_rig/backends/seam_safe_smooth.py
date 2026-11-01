#!/usr/bin/env python3
"""tools/auto_rig/backends/seam_safe_smooth.py — stretch-masked Laplacian weight smoothing for DENSE meshes,
on welded vertices so UV seams can never open.

Why (Negativo re-rig, 2026-10-31): smooth_weights.py averages the two endpoints of each over-stretched edge, a few
thousand vertices per round. On a 1.2M-vertex Tripo mesh (median edge 1.06 mm) it plateaued above the gate (heat
skin p99.9 4.73 -> 3.03 after 11 rounds; gate 2.5). It also works on unwelded vertices, so the copies of a UV-seam
vertex (378,075 of them on Negativo) can end up with different weights and the seam opens under animation; no
triangle edge spans a seam, so no stretch metric sees that crack.

Method (topology-respecting; nothing painted):
  1. weld vertices by position: every copy of a seam vertex shares ONE weight vector, so seams stay closed;
  2. evaluate the embedded clip(s) exactly like smooth_weights.evaluate (same edge filter: rest length >=
     min(9.8 mm, half the median edge)), and mark the vertices of every edge stretched > --threshold;
  3. grow the mark by --rings edge rings and run --iters damped Jacobi Laplacian steps on the marked vertices
     only (w <- (1 - lam) w + lam * mean of the edge neighbours; unmarked vertices are fixed, rows stay summed to 1);
  4. CONTINUOUS top-4 (each vertex's 5th-largest weight subtracted from its top 4, renormalized: a hard cut
     flips the 4th bone between neighbours and tears them; see top4()), evaluated again; repeat for --rounds or
     until p99.9 <= --gate;
  5. written back into the same JOINTS_0/WEIGHTS_0 accessors (every other byte, incl. the clip, unchanged).

usage: python3 tools/auto_rig/backends/seam_safe_smooth.py --in RIG_WITH_CLIP.glb --out OUT.glb
           [--threshold 2.0] [--gate 2.5] [--rounds 8] [--rings 2] [--iters 10] [--lam 0.5] [--frames 10]
Exit 0 when the gate is reached, 1 otherwise (the output is written either way). Plain glTF, float WEIGHTS_0.
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import anim_check as ac  # noqa: E402
from smooth_weights import _skin_fast, prim_edges  # noqa: E402
from fix_sternum_weights import read_glb, write_glb, view  # noqa: E402


def top4(D):
    """CONTINUOUS 4-influence limit: subtract each vertex's 5th-largest weight from its top 4, renormalize.
    A hard top-4 cut drops whichever bone ranks 5th, so neighbours whose 4th/5th bones swap rank keep different
    bones (Negativo: one vertex kept RightUpLeg 0.05, its 0.5 mm neighbour Spine2 0.04 -> 7-9 mm tears on every
    kick, the whole stretch plateau). Here a bone reaches 0 exactly where it leaves the top 4, so the limited
    weights stay continuous across the mesh."""
    idx = np.argsort(-D, axis=1)[:, :5]
    v = np.take_along_axis(D, idx, 1).astype(np.float64)
    if v.shape[1] < 5:
        v = np.c_[v, np.zeros((len(v), 5 - v.shape[1]))]
    w = np.maximum(v[:, :4] - v[:, 4:5], 0.0)
    s = w.sum(1, keepdims=True)
    w = np.where(s > 1e-9, w / np.maximum(s, 1e-12), 0.25)
    return idx[:, :4], w


def run(inp, outp, threshold=2.0, gate=2.5, rounds=8, rings=2, iters=10, lam=0.5, frames=10):
    from scipy.sparse import coo_matrix
    model = ac.AnimModel(inp)
    if not model.js.get('animations'):
        raise SystemExit('no embedded clip to evaluate against (bake one: heat_rebind.py --donor ...)')
    if not model.prims:
        raise SystemExit('no skinned primitive')
    # multi-part exports (2026-11-01): all skinned primitives are smoothed as ONE welded mesh (they share the
    # skeleton's bind space), so seams between parts also get identical weights; each part's slice is written back.
    offs = np.cumsum([0] + [len(q['pos']) for q in model.prims])
    jidx = np.array(model.joint_nodes)
    bind = model.bind_world()
    bind_skin = np.stack([bind[int(j)] @ model.ibm[k] for k, j in enumerate(jidx)])
    frame_skins = []
    for an in model.js['animations']:
        times, chans = model.animation_frames(an, frames)
        for t in times:
            w = model.eval_world(chans, t)
            frame_skins.append(np.stack([w[int(j)] @ model.ibm[k] for k, j in enumerate(jidx)]))
    prim = {'pos': np.concatenate([q['pos'] for q in model.prims]),
            'joints': np.concatenate([q['joints'] for q in model.prims]),
            'weights': np.concatenate([q['weights'] for q in model.prims]),
            'idx': np.concatenate([(q['idx'] if q['idx'] is not None else np.arange(len(q['pos']))) + o
                                   for q, o in zip(model.prims, offs[:-1])])}
    P = prim['pos']
    pos_h = np.c_[P, np.ones(len(P))]
    E = prim_edges(prim)
    r0 = _skin_fast(bind_skin, prim, pos_h)
    rest = np.linalg.norm(r0[E[:, 0]] - r0[E[:, 1]], axis=1)
    keep = rest >= min(0.0098, 0.5 * float(np.median(rest)))
    E, rest = E[keep], rest[keep]
    # weld
    key = np.round(P / 1e-6).astype(np.int64)
    _, first, inv = np.unique(key, axis=0, return_index=True, return_inverse=True)
    inv = inv.reshape(-1)
    nw = len(first)
    Ea = prim_edges(prim)
    Ew = np.unique(np.sort(inv[Ea], 1), axis=0)
    Ew = Ew[Ew[:, 0] != Ew[:, 1]]
    A = coo_matrix((np.ones(2 * len(Ew), np.float32), (np.r_[Ew[:, 0], Ew[:, 1]], np.r_[Ew[:, 1], Ew[:, 0]])),
                   shape=(nw, nw)).tocsr()
    deg = np.asarray(A.sum(1)).ravel()
    deg[deg == 0] = 1
    nb = len(jidx)
    D = np.zeros((len(P), nb), np.float32)
    np.add.at(D, (np.repeat(np.arange(len(P)), 4), prim['joints'].ravel()), prim['weights'].ravel())
    Wd = D[first].copy()
    del D

    def evaluate(Wd):
        J4, W4 = top4(Wd[inv])
        prim['joints'], prim['weights'] = J4, W4
        maxr = np.zeros(len(E))
        for fs in frame_skins:
            c = _skin_fast(fs, prim, pos_h)
            maxr = np.maximum(maxr, np.linalg.norm(c[E[:, 0]] - c[E[:, 1]], axis=1) / rest)
        return maxr, J4, W4

    log = []
    maxr, J4, W4 = evaluate(Wd)
    p999 = float(np.percentile(maxr, 99.9))
    log.append({'round': 0, 'p999': round(p999, 3), 'over_threshold': int((maxr > threshold).sum())})
    print('round 0: p99.9 %.3f, edges > %.1f: %d' % (p999, threshold, (maxr > threshold).sum()), flush=True)
    for rnd in range(1, rounds + 1):
        if p999 <= gate:
            break
        bad = E[maxr > threshold]
        mark = np.zeros(nw, bool)
        mark[inv[bad.ravel()]] = True
        for _ in range(rings):
            mark |= (A @ mark.astype(np.float32)) > 0
        for _ in range(iters):
            avg = (A @ Wd) / deg[:, None]
            Wd[mark] = (1 - lam) * Wd[mark] + lam * avg[mark]
        maxr, J4, W4 = evaluate(Wd)
        p999 = float(np.percentile(maxr, 99.9))
        log.append({'round': rnd, 'p999': round(p999, 3), 'over_threshold': int((maxr > threshold).sum()),
                    'smoothed_welded_verts': int(mark.sum())})
        print('round %d: smoothed %d welded verts -> p99.9 %.3f, edges > %.1f: %d'
              % (rnd, mark.sum(), p999, threshold, (maxr > threshold).sum()), flush=True)
    # write back (top-4 of the welded weights, identical on every seam copy)
    # same primitive order as anim_check.AnimModel._load_skin_data (meshes, then their skinned primitives)
    js, binarr = read_glb(inp)
    k = 0
    for mesh in js.get('meshes', []):
        for pr in mesh.get('primitives', []):
            at = pr['attributes']
            if 'JOINTS_0' not in at or 'POSITION' not in at:
                continue
            Jv, _ = view(js, binarr, at['JOINTS_0'])
            Wv, wacc = view(js, binarr, at['WEIGHTS_0'])
            if wacc['componentType'] != 5126:
                raise SystemExit('WEIGHTS_0 must be float')
            sl = slice(offs[k], offs[k + 1])
            Jv[:] = J4[sl].astype(Jv.dtype)
            Wv[:] = W4[sl].astype(Wv.dtype)
            k += 1
    if k != len(model.prims):
        raise SystemExit('wrote %d primitives, read %d' % (k, len(model.prims)))
    write_glb(outp, js, binarr)
    rep = {'input': inp, 'output': outp, 'tool': 'tools/auto_rig/backends/seam_safe_smooth.py', 'gate': gate,
           'threshold': threshold, 'rings': rings, 'iters': iters, 'lam': lam, 'frames_per_clip': frames,
           'welded_verts': int(nw), 'rounds': log, 'pass': p999 <= gate}
    print(json.dumps(rep, indent=1))
    return rep


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--in', dest='inp', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--threshold', type=float, default=2.0)
    ap.add_argument('--gate', type=float, default=2.5)
    ap.add_argument('--rounds', type=int, default=8)
    ap.add_argument('--rings', type=int, default=2)
    ap.add_argument('--iters', type=int, default=10)
    ap.add_argument('--lam', type=float, default=0.5)
    ap.add_argument('--frames', type=int, default=10)
    ap.add_argument('--report', default=None)
    a = ap.parse_args()
    rep = run(a.inp, a.out, a.threshold, a.gate, a.rounds, a.rings, a.iters, a.lam, a.frames)
    if a.report:
        json.dump(rep, open(a.report, 'w'), indent=1)
    sys.exit(0 if rep['pass'] else 1)


if __name__ == '__main__':
    main()
