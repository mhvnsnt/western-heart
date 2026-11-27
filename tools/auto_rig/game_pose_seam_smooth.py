#!/usr/bin/env python3
"""tools/auto_rig/game_pose_seam_smooth.py — seam-safe weight smoothing judged on the poses the GAME plays.

Why (2026-11-27, Pantera attires): pantera.glb's weights were repaired against its own embedded Idle clip
(repair_pantera_glb.py, reskin_pantera_weights.py: Idle p99.9 1.88). In the fight it never plays that clip; it plays
the T7 King bank retargeted at runtime, and under those poses (wide stance, kicks) poselab's stretchMap measured edge
stretch p99.9 40-52 on pants / boots2 / logo: visible shards off the standing shin and torn trousers in the kick.

Method (nothing painted, nothing cut, skeleton/IBMs/geometry untouched):
  1. capture the game's own posed skeleton: poselab showFighter for every action slot at several times, each bone's
     local TRS (capture script: docs/proof/2026-11-27/pantera-attires/capture_poses.mjs) -> poses.json;
  2. embed them as one glTF clip per action slot (STEP samplers) in a TEMPORARY copy of the model;
  3. run tools/auto_rig/backends/seam_safe_smooth.py (welded, stretch-masked Laplacian, continuous top-4) on it,
     unchanged, so its gate is measured on the game's poses;
  4. copy only the resulting JOINTS_0 / WEIGHTS_0 back into a copy of the ORIGINAL file (its own clips, materials,
     everything else byte-identical). The input is never modified.

    python3 tools/auto_rig/game_pose_seam_smooth.py --in MODEL.glb --poses poses.json --out FIXED.glb
        [--threshold 2.0] [--gate 2.5] [--rounds 8] [--rings 2] [--iters 10] [--lam 0.5] [--report r.json]
Plain glTF (no meshopt), float WEIGHTS_0.
"""
import argparse, json, os, struct, sys, tempfile
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'backends')); sys.path.insert(0, HERE)
from fix_sternum_weights import read_glb, write_glb, view  # noqa: E402
import seam_safe_smooth as sss  # noqa: E402


def _append(js, binarr, arr, typ, comp=5126):
    arr = np.ascontiguousarray(arr, np.float32)
    while len(binarr) % 4: binarr.append(0)
    off = len(binarr); binarr.extend(arr.tobytes())
    js['bufferViews'].append({'buffer': 0, 'byteOffset': off, 'byteLength': arr.nbytes})
    acc = {'bufferView': len(js['bufferViews']) - 1, 'componentType': comp, 'count': int(arr.shape[0]), 'type': typ}
    if typ == 'SCALAR': acc['min'] = [float(arr.min())]; acc['max'] = [float(arr.max())]
    js['accessors'].append(acc)
    return len(js['accessors']) - 1


def embed(inp, poses, outp):
    js, binarr = read_glb(inp)
    skin = js['skins'][0]
    name2node = {js['nodes'][j].get('name'): j for j in skin['joints']}
    by_clip = {}
    for f in poses['frames']:
        by_clip.setdefault(f['clip'], []).append(f)
    anims, missing = [], set()
    for clip, frs in by_clip.items():
        times = _append(js, binarr, np.arange(len(frs), dtype=np.float32)[:, None] / 30.0, 'SCALAR')
        samplers, chans = [], []
        for nm, node in name2node.items():
            if not all(nm in f['bones'] for f in frs):
                missing.add(nm); continue
            for path, key, typ in (('rotation', 'q', 'VEC4'), ('translation', 'p', 'VEC3'), ('scale', 's', 'VEC3')):
                out = _append(js, binarr, np.array([f['bones'][nm][key] for f in frs]), typ)
                samplers.append({'input': times, 'output': out, 'interpolation': 'STEP'})
                chans.append({'sampler': len(samplers) - 1, 'target': {'node': node, 'path': path}})
        anims.append({'name': 'game_' + clip, 'samplers': samplers, 'channels': chans})
    js['animations'] = anims
    js['buffers'][0]['byteLength'] = len(binarr)
    write_glb(outp, js, binarr)
    return {'clips': len(anims), 'frames': len(poses['frames']), 'joints_missing_in_capture': sorted(missing)}


def transplant(orig, smoothed, outp):
    js, binarr = read_glb(orig)
    js2, bin2 = read_glb(smoothed)
    n = 0
    for mi, mesh in enumerate(js.get('meshes', [])):
        for pi, pr in enumerate(mesh.get('primitives', [])):
            at = pr['attributes']
            if 'JOINTS_0' not in at or 'POSITION' not in at: continue
            at2 = js2['meshes'][mi]['primitives'][pi]['attributes']
            for k in ('JOINTS_0', 'WEIGHTS_0'):
                dst, _ = view(js, binarr, at[k]); src, _ = view(js2, bin2, at2[k])
                assert dst.shape == src.shape
                dst[:] = src
            n += 1
    write_glb(outp, js, binarr)
    return n


def run_coupled(inp, outp, threshold=2.0, gate=2.5, rounds=8, rings=2, iters=10, lam=0.5, frames=10,
                couple_radius=0.02, sep_tol=0.01):
    """seam_safe_smooth.run plus LAYER COUPLING for multi-part bodies (boots over shins, straps over boots, trousers
    over thighs): separate parts share no triangle edge, so edge smoothing never makes a strap agree with the boot under
    it; under the game's poses the strap then floats off as a rigid shard (no edge stretches, so no stretch gate sees
    it). Here welded vertices of different islands (separate parts, or separate pieces inside one part) closer than --couple-radius at bind are joined as Laplacian neighbours,
    and a pair whose posed distance changes by more than --sep-tol (m) in any frame counts as a defect like an
    over-stretched edge (marked and smoothed). Everything else is seam_safe_smooth.run's method, reused."""
    from scipy.sparse import coo_matrix
    from scipy.spatial import cKDTree
    top4, _skin_fast, prim_edges = sss.top4, sss._skin_fast, sss.prim_edges
    ac = sss.ac
    model = ac.AnimModel(inp)
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
    part = np.concatenate([np.full(len(q['pos']), i) for i, q in enumerate(model.prims)])
    prim = {'pos': np.concatenate([q['pos'] for q in model.prims]),
            'joints': np.concatenate([q['joints'] for q in model.prims]),
            'weights': np.concatenate([q['weights'] for q in model.prims]),
            'idx': np.concatenate([(q['idx'] if q['idx'] is not None else np.arange(len(q['pos']))) + o
                                   for q, o in zip(model.prims, offs[:-1])])}
    P = prim['pos']; pos_h = np.c_[P, np.ones(len(P))]
    E = prim_edges(prim)
    r0 = _skin_fast(bind_skin, prim, pos_h)
    rest = np.linalg.norm(r0[E[:, 0]] - r0[E[:, 1]], axis=1)
    keep = rest >= min(0.0098, 0.5 * float(np.median(rest)))
    E, rest = E[keep], rest[keep]
    key = np.round(r0 / 1e-6).astype(np.int64)
    _, first, inv = np.unique(key, axis=0, return_index=True, return_inverse=True)
    inv = inv.reshape(-1); nw = len(first)
    Ew = np.unique(np.sort(inv[prim_edges(prim)], 1), axis=0); Ew = Ew[Ew[:, 0] != Ew[:, 1]]
    # layer coupling pairs (welded ids), different parts only
    tree = cKDTree(r0[first])
    pairs = tree.query_pairs(couple_radius, output_type='ndarray')
    # couple across ISLANDS (connected components of the welded edge graph): a strap modelled as its own island
    # inside the boot part needs coupling just like a separate part does.
    from scipy.sparse.csgraph import connected_components
    _, isl = connected_components(coo_matrix((np.ones(len(Ew)), (Ew[:, 0], Ew[:, 1])), shape=(nw, nw)), directed=False)
    pairs = pairs[isl[pairs[:, 0]] != isl[pairs[:, 1]]]
    # never couple across limbs that legitimately move apart (inner thighs, hand near hip): classify each welded vertex
    # by the limb chain of its dominant joint (limb_isolation.py's rule) and keep only pairs on the same chain.
    jn = [model.js['nodes'][int(j)]['name'] for j in jidx]
    parent = {}
    for ni, nd in enumerate(model.js['nodes']):
        for c in nd.get('children', []): parent[c] = ni
    def limb(j):
        n = int(jidx[j])
        while n is not None:
            nm = model.js['nodes'][n].get('name', '')
            for side in ('Left', 'Right'):
                if nm in (side + 'UpLeg',): return side + '_leg'
                if nm in (side + 'Shoulder', side + 'Arm'): return side + '_arm'
            n = parent.get(n)
        return 'core'
    jl = np.array([limb(j) for j in range(len(jidx))])
    dom = jl[prim['joints'][first, np.argmax(prim['weights'][first], 1)]]
    pairs = pairs[dom[pairs[:, 0]] == dom[pairs[:, 1]]]
    Pv = first[pairs]  # representative vertex ids
    prest = np.linalg.norm(r0[Pv[:, 0]] - r0[Pv[:, 1]], axis=1)
    allE = np.r_[Ew, pairs]
    A = coo_matrix((np.ones(2 * len(allE), np.float32), (np.r_[allE[:, 0], allE[:, 1]], np.r_[allE[:, 1], allE[:, 0]])),
                   shape=(nw, nw)).tocsr()
    A.data[:] = 1.0
    deg = np.asarray(A.sum(1)).ravel(); deg[deg == 0] = 1
    D = np.zeros((len(P), len(jidx)), np.float32)
    np.add.at(D, (np.repeat(np.arange(len(P)), 4), prim['joints'].ravel()), prim['weights'].ravel())
    Wd = D[first].copy(); del D

    def evaluate(Wd):
        J4, W4 = top4(Wd[inv]); prim['joints'], prim['weights'] = J4, W4
        maxr = np.zeros(len(E)); sep = np.zeros(len(Pv))
        for fs in frame_skins:
            c = _skin_fast(fs, prim, pos_h)
            maxr = np.maximum(maxr, np.linalg.norm(c[E[:, 0]] - c[E[:, 1]], axis=1) / rest)
            sep = np.maximum(sep, np.abs(np.linalg.norm(c[Pv[:, 0]] - c[Pv[:, 1]], axis=1) - prest))
        return maxr, sep, J4, W4

    def stats(maxr, sep):
        return float(np.percentile(maxr, 99.9)), int((maxr > threshold).sum()), int((sep > sep_tol).sum()), float(sep.max() if len(sep) else 0)
    log = []
    maxr, sep, J4, W4 = evaluate(Wd)
    p999, nover, nsep, smax = stats(maxr, sep)
    log.append({'round': 0, 'p999': round(p999, 3), 'over_threshold': nover, 'separated_pairs': nsep, 'max_separation_m': round(smax, 4)})
    print('round 0: p99.9 %.3f, edges > %.1f: %d, layer pairs separating > %.3f m: %d (max %.3f)' % (p999, threshold, nover, sep_tol, nsep, smax), flush=True)
    for rnd in range(1, rounds + 1):
        if p999 <= gate and nsep == 0: break
        mark = np.zeros(nw, bool)
        mark[inv[E[maxr > threshold].ravel()]] = True
        mark[pairs[sep > sep_tol].ravel()] = True
        for _ in range(rings): mark |= (A @ mark.astype(np.float32)) > 0
        for _ in range(iters):
            avg = (A @ Wd) / deg[:, None]
            Wd[mark] = (1 - lam) * Wd[mark] + lam * avg[mark]
        maxr, sep, J4, W4 = evaluate(Wd)
        p999, nover, nsep, smax = stats(maxr, sep)
        log.append({'round': rnd, 'p999': round(p999, 3), 'over_threshold': nover, 'separated_pairs': nsep,
                    'max_separation_m': round(smax, 4), 'smoothed_welded_verts': int(mark.sum())})
        print('round %d: smoothed %d -> p99.9 %.3f, edges > %.1f: %d, separating pairs %d (max %.3f)' % (rnd, mark.sum(), p999, threshold, nover, nsep, smax), flush=True)
    js, binarr = read_glb(inp); k = 0
    for mesh in js.get('meshes', []):
        for pr in mesh.get('primitives', []):
            at = pr['attributes']
            if 'JOINTS_0' not in at or 'POSITION' not in at: continue
            Jv, _ = view(js, binarr, at['JOINTS_0']); Wv, wacc = view(js, binarr, at['WEIGHTS_0'])
            if wacc['componentType'] != 5126: raise SystemExit('WEIGHTS_0 must be float')
            sl = slice(offs[k], offs[k + 1]); Jv[:] = J4[sl].astype(Jv.dtype); Wv[:] = W4[sl].astype(Wv.dtype); k += 1
    write_glb(outp, js, binarr)
    return {'gate': gate, 'threshold': threshold, 'couple_radius': couple_radius, 'sep_tol': sep_tol, 'rings': rings,
            'iters': iters, 'lam': lam, 'frames_per_clip': frames, 'welded_verts': int(nw), 'layer_pairs': int(len(pairs)),
            'rounds': log, 'pass': bool(p999 <= gate and nsep == 0)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--in', dest='inp', required=True); ap.add_argument('--poses', required=True)
    ap.add_argument('--out', required=True); ap.add_argument('--report')
    ap.add_argument('--threshold', type=float, default=2.0); ap.add_argument('--gate', type=float, default=2.5)
    ap.add_argument('--rounds', type=int, default=8); ap.add_argument('--rings', type=int, default=2)
    ap.add_argument('--iters', type=int, default=10); ap.add_argument('--lam', type=float, default=0.5)
    ap.add_argument('--couple-radius', type=float, default=0.0,
                    help='>0: layer coupling between parts closer than this at bind (m); see run_coupled')
    ap.add_argument('--sep-tol', type=float, default=0.01)
    a = ap.parse_args()
    poses = json.load(open(a.poses))
    nf = max(sum(1 for f in poses['frames'] if f['clip'] == c) for c in {f['clip'] for f in poses['frames']})
    with tempfile.TemporaryDirectory() as td:
        tmp_in, tmp_out = os.path.join(td, 'eval.glb'), os.path.join(td, 'eval_smoothed.glb')
        emb = embed(a.inp, poses, tmp_in)
        if a.couple_radius > 0:
            rep = run_coupled(tmp_in, tmp_out, a.threshold, a.gate, a.rounds, a.rings, a.iters, a.lam, nf,
                              a.couple_radius, a.sep_tol)
        else:
            rep = sss.run(tmp_in, tmp_out, a.threshold, a.gate, a.rounds, a.rings, a.iters, a.lam, nf)
        nprim = transplant(a.inp, tmp_out, a.out)
    rep.update({'tool': 'tools/auto_rig/game_pose_seam_smooth.py', 'input': a.inp, 'output': a.out,
                'poses': a.poses, 'embedded': emb, 'primitives_written': nprim})
    if a.report: json.dump(rep, open(a.report, 'w'), indent=1)
    sys.exit(0 if rep['pass'] else 1)


if __name__ == '__main__':
    main()
