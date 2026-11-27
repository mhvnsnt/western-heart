#!/usr/bin/env python3
"""tools/auto_rig/transplant_weights_by_position.py — bring a re-skin back into the ORIGINAL file's exact layout.

Why (2026-11-27, Pantera Classic): Blender-based weight solvers (backends/surface_heat.py, blender_heat.py) re-export
the GLB: primitive order, vertex order/count (seam splits), node order, materials and clips can all change. The game
and every attire re-texture built on that file (A4/A5/A6 share its parts vertex-for-vertex) need the original layout.
This takes ONLY the weights from the re-skinned file and writes them into a copy of the original:

  * parts are matched by node name (the mesh's node), joints by joint name (skeletons must share names);
  * each original vertex takes the weights of the re-skinned vertex at the same bind-space (rest) position in the
    same part (k-d tree; the report lists the max match distance; refuses above --max-dist);
  * only JOINTS_0 / WEIGHTS_0 values change, in place; everything else is byte-identical.

    python3 tools/auto_rig/transplant_weights_by_position.py --orig ORIGINAL.glb --skin RESKINNED.glb --out OUT.glb
        [--max-dist 1e-4] [--report r.json]
Plain glTF (no meshopt), float WEIGHTS_0 in the original.
"""
import argparse, json, os, sys
import numpy as np
from scipy.spatial import cKDTree
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, 'backends'))
from fix_sternum_weights import read_glb, write_glb, view  # noqa: E402
import anim_check as ac  # noqa: E402


def rest_parts(path):
    """{node name: (rest positions (n,3), joints (n,4) as names-index, weights (n,4), prim attrs)} via the skin's bind."""
    m = ac.AnimModel(path)
    js = m.js
    jn = [js['nodes'][j]['name'] for j in m.joint_nodes]
    bind = m.bind_world()
    skin_m = np.stack([bind[int(j)] @ m.ibm[k] for k, j in enumerate(m.joint_nodes)])
    mesh2node = {n['mesh']: n.get('name') for n in js['nodes'] if 'mesh' in n}
    out, k = {}, 0
    for mi, mesh in enumerate(js['meshes']):
        for pi, pr in enumerate(mesh['primitives']):
            at = pr['attributes']
            if 'JOINTS_0' not in at or 'POSITION' not in at: continue
            q = m.prims[k]; k += 1
            P = np.c_[q['pos'], np.ones(len(q['pos']))]
            M = np.einsum('vk,vkij->vij', q['weights'], skin_m[q['joints']])
            rest = np.einsum('vij,vj->vi', M, P)[:, :3]
            out.setdefault(mesh2node[mi], []).append((rest, q['joints'], q['weights'], (mi, pi)))
    return js, jn, out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--orig', required=True); ap.add_argument('--skin', required=True); ap.add_argument('--out', required=True)
    ap.add_argument('--max-dist', type=float, default=1e-4); ap.add_argument('--report')
    a = ap.parse_args()
    js_o, jn_o, parts_o = rest_parts(a.orig)
    _, jn_s, parts_s = rest_parts(a.skin)
    remap = np.array([jn_o.index(n) for n in jn_s])  # skin joint index -> original joint index
    js, binarr = read_glb(a.orig)
    rep = {'tool': 'tools/auto_rig/transplant_weights_by_position.py', 'orig': a.orig, 'skin': a.skin, 'out': a.out, 'parts': {}}
    worst = 0.0
    for name, plist in parts_o.items():
        if name not in parts_s: raise SystemExit('part %s missing in re-skinned file' % name)
        S = parts_s[name]
        sp = np.concatenate([s[0] for s in S]); sj = np.concatenate([s[1] for s in S]); sw = np.concatenate([s[2] for s in S])
        tree = cKDTree(sp)
        for rest, _, _, (mi, pi) in plist:
            d, i = tree.query(rest)
            worst = max(worst, float(d.max()))
            if d.max() > a.max_dist: raise SystemExit('part %s: max match distance %.3g > %.3g' % (name, d.max(), a.max_dist))
            at = js['meshes'][mi]['primitives'][pi]['attributes']
            Jv, _ = view(js, binarr, at['JOINTS_0']); Wv, wacc = view(js, binarr, at['WEIGHTS_0'])
            if wacc['componentType'] != 5126: raise SystemExit('original WEIGHTS_0 must be float')
            W = sw[i].astype(np.float64); W /= np.maximum(W.sum(1, keepdims=True), 1e-12)
            Jv[:] = remap[sj[i]].astype(Jv.dtype); Wv[:] = W.astype(Wv.dtype)
            rep['parts'][name] = {'verts': int(len(rest)), 'max_match_dist': float(d.max())}
    rep['max_match_dist'] = worst
    write_glb(a.out, js, binarr)
    if a.report: json.dump(rep, open(a.report, 'w'), indent=1)
    print(json.dumps({'max_match_dist': worst, 'parts': len(rep['parts'])}))


if __name__ == '__main__':
    main()
