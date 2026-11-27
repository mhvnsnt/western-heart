#!/usr/bin/env python3
"""tools/auto_rig/rig_multipart_from_donor.py — rig a MULTI-PART static re-texture of a rigged donor (2026-11-27).

For statics that are the donor's own mesh parts re-textured (e.g. Pantera A5 Crimson Rage / A6 T7 P2: the same 18
T7-King parts as pantera.glb, exported Z-up at another scale, plus an extra tail curve). backends/knn_transfer.py +
backends/apply_skin.py handle one single-primitive mesh; this drives the same method per part and reuses
apply_skin's GLB reader/builder and its tail fit (fit_tail / tail_weights) unchanged:

  1. Orientation + scale: every target part is taken into the file's world frame (node matrices), then ONE
     similarity transform (Umeyama, uniform scale, proper rotation) is fitted from the parts whose name AND vertex
     count match a donor part to the donor's bind space. The fit residual is reported; it must be ~0 for re-textures
     (refused above --max-residual). No per-vertex edits: positions/normals only get that one transform.
  2. Weights per part: same name + same count + per-vertex distance ~0 -> the donor's JOINTS_0/WEIGHTS_0 copied
     verbatim; same name, different count -> k-NN (k=4, inverse distance, top-4, the knn_transfer.py method) against
     that donor part only; no donor counterpart -> k-NN against the whole donor, except a part apply_skin.fit_tail
     recognises as a tail, which gets the Tail1..Tail4 chain under Hips with apply_skin's kernels.
  3. Output: donor skeleton nodes + skin verbatim (+ tail joints/IBMs), every target part skinned (no part dropped,
     no vertex removed), the target's own materials/textures byte-identical, donor animations copied.

    python3 tools/auto_rig/rig_multipart_from_donor.py --in STATIC.glb --donor game/assets/models/pantera.glb \
        --out RIGGED.glb [--report rep.json]
Plain glTF only (decode meshopt first: tools/anim/gltf_codec.mjs). Gate after: tools/auto_rig/validate.py,
tools/model-audit/rig_qa.py, and the game's own loader (game/poselab.html).
"""
import argparse
import hashlib
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backends'))
from apply_skin import read_glb, acc_array, node_worlds, GlbBuilder, fit_tail, tail_weights  # noqa: E402


def umeyama(X, Y):
    mx, my = X.mean(0), Y.mean(0)
    Xc, Yc = X - mx, Y - my
    U, S, Vt = np.linalg.svd(Yc.T @ Xc)
    D = np.eye(3)
    D[2, 2] = np.sign(np.linalg.det(U @ Vt))
    R = U @ D @ Vt
    s = (S * np.diag(D)).sum() / (Xc ** 2).sum()
    return s, R, my - s * R @ mx


def knn_weights(tpos, dpos, dj, dw, k=4):
    from scipy.spatial import cKDTree
    k = min(k, len(dpos))
    dist, idx = cKDTree(dpos).query(tpos, k=k)
    if k == 1:
        dist, idx = dist[:, None], idx[:, None]
    nj = int(dj.max()) + 1
    w = 1.0 / (dist + 1e-9)
    w /= w.sum(1, keepdims=True)
    acc = np.zeros((len(tpos), nj))
    for ki in range(k):
        np.add.at(acc, (np.arange(len(tpos))[:, None], dj[idx[:, ki]]), w[:, ki:ki + 1] * dw[idx[:, ki]])
    top = np.argsort(-acc, axis=1)[:, :4]
    tw = acc[np.arange(len(tpos))[:, None], top]
    tw /= tw.sum(1, keepdims=True).clip(min=1e-12)
    return top.astype(np.int64), tw, float(dist[:, 0].mean())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--in', dest='inp', required=True)
    ap.add_argument('--donor', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--report', default=None)
    ap.add_argument('--max-residual', type=float, default=1e-3)
    ap.add_argument('--rigid-part', action='append', default=[],
                    help='PART=Bone: a part with no donor counterpart that fit_tail cannot chain (e.g. a tail attached off '
                         'the centreline) rides that one donor bone rigidly instead of k-NN to whatever is nearest')
    a = ap.parse_args()
    tjs, tb = read_glb(a.inp)
    djs, db = read_glb(a.donor)
    rep = {'in': a.inp, 'donor': a.donor, 'parts': []}
    tw_ = node_worlds(tjs)
    dw_ = node_worlds(djs)

    def prim_parts(js, bd, worlds, skinned_bind):
        out = []
        for ni, nd in enumerate(js['nodes']):
            if 'mesh' not in nd:
                continue
            for pi, pr in enumerate(js['meshes'][nd['mesh']]['primitives']):
                p = acc_array(js, bd, pr['attributes']['POSITION']).astype(np.float64)
                M = np.eye(4) if (skinned_bind and nd.get('skin') is not None) else worlds[ni]
                out.append({'name': nd.get('name'), 'node': ni, 'prim': pi, 'pr': pr,
                            'pos': p @ M[:3, :3].T + M[:3, 3], 'M': M})
        return out

    T = prim_parts(tjs, tb, tw_, False)
    D = prim_parts(djs, db, dw_, True)   # donor skinned parts: positions are bind space
    dby = {d['name']: d for d in D}
    for d in D:
        d['J'] = acc_array(djs, db, d['pr']['attributes']['JOINTS_0']).astype(np.int64)
        d['W'] = acc_array(djs, db, d['pr']['attributes']['WEIGHTS_0']).astype(np.float64)
        if djs['accessors'][d['pr']['attributes']['WEIGHTS_0']]['componentType'] != 5126:
            d['W'] = d['W'] / d['W'].sum(1, keepdims=True).clip(min=1e-12)
    pairs = [(t, dby[t['name']]) for t in T if t['name'] in dby and len(t['pos']) == len(dby[t['name']]['pos'])]
    if not pairs:
        sys.exit('no part matches the donor by name + vertex count: not a re-texture of this donor')
    X = np.vstack([t['pos'] for t, _ in pairs])
    Y = np.vstack([d['pos'] for _, d in pairs])
    s, R, tr = umeyama(X, Y)
    res = np.linalg.norm((s * (R @ X.T)).T + tr - Y, axis=1)
    rep['similarity'] = {'scale': s, 'R': R.round(6).tolist(), 't': tr.round(6).tolist(),
                         'fit_parts': len(pairs), 'fit_verts': int(len(X)),
                         'residual_mean': float(res.mean()), 'residual_max': float(res.max())}
    if res.max() > a.max_residual:
        sys.exit(f'similarity residual {res.max():.5f} > {a.max_residual}: not a rigid re-texture; use the heat/refit path')
    dskin = djs['skins'][0]
    djoints = dskin['joints']
    dnames = [djs['nodes'][j].get('name') for j in djoints]
    hips_node = djoints[dnames.index('Hips')]
    hips_world = dw_[hips_node]
    allD = np.vstack([d['pos'] for d in D])
    allJ = np.vstack([d['J'] for d in D])
    allW = np.vstack([d['W'] for d in D])
    tail = None
    for t in T:
        t['pos_n'] = (s * (R @ t['pos'].T)).T + tr
        t['Rn'] = R @ t['M'][:3, :3]
        d = dby.get(t['name'])
        if d is not None and len(d['pos']) == len(t['pos']) and np.abs(d['pos'] - t['pos_n']).max() < a.max_residual:
            t['J'], t['W'], how = d['J'].copy(), d['W'].copy(), 'donor weights copied (same part, same vertex order)'
        elif d is not None:
            t['J'], t['W'], md = knn_weights(t['pos_n'], d['pos'], d['J'], d['W'])
            how = f'k-NN from donor part {d["name"]} (mean nn {md:.5f} m)'
        else:
            t['J'], t['W'], md = knn_weights(t['pos_n'], allD, allJ, allW)
            how = f'k-NN from whole donor (mean nn {md:.4f} m)'
            try:
                mask, chain, u, trep = fit_tail(t['pos_n'], hips_world[:3, 3])
            except SystemExit as e:
                mask, trep = None, str(e)
            if mask is not None and mask.mean() > 0.5:
                tail = (t, mask, chain, u)
                how = f'tail chain: {trep}'
            else:
                rig = dict(x.split('=', 1) for x in a.rigid_part)
                if t['name'] in rig:
                    bi = dnames.index(rig[t['name']])
                    t['J'] = np.zeros((len(t['pos']), 4), dtype=np.int64); t['J'][:, 0] = bi
                    t['W'] = np.zeros((len(t['pos']), 4)); t['W'][:, 0] = 1.0
                    how = f'rigid to donor bone {rig[t["name"]]} (--rigid-part; fit_tail: {trep})'
        rep['parts'].append({'name': t['name'], 'verts': int(len(t['pos'])), 'weights': how})
    # tail joints (apply_skin geometry: identity local rotation under Hips)
    tail_local, tail_ibm = [], []
    if tail is not None:
        t, mask, chain, u = tail
        twt = tail_weights(u[mask])
        combos = np.array([0] + [len(djoints) + k for k in range(4)])
        top = np.argsort(-twt, axis=1)[:, :4]
        nj = combos[top]
        nw = twt[np.arange(len(twt))[:, None], top]
        nw /= nw.sum(1, keepdims=True).clip(min=1e-12)
        hips_ord = dnames.index('Hips')
        nj = np.where(nj == 0, hips_ord, nj)
        t['J'][mask], t['W'][mask] = nj, nw
        hr = hips_world[:3, :3]
        hri = np.linalg.inv(hr)
        prev = hips_world[:3, 3]
        for k in range(4):
            tail_local.append(hri @ (chain[k] - prev))
            wm = np.eye(4); wm[:3, :3] = hr; wm[:3, 3] = chain[k]
            tail_ibm.append(np.linalg.inv(wm))
            prev = chain[k]
    # ---- build ----
    b = GlbBuilder()
    keep = [i for i, nd in enumerate(djs['nodes']) if 'mesh' not in nd and 'camera' not in nd]
    remap = {o: n for n, o in enumerate(keep)}
    nodes = []
    for o in keep:
        nd = json.loads(json.dumps(djs['nodes'][o]))
        if 'children' in nd:
            nd['children'] = [remap[c] for c in nd['children'] if c in remap]
        nodes.append(nd)
    tail_first = len(nodes)
    if tail is not None:
        for k in range(4):
            nd = {'name': f'Tail{k + 1}', 'translation': [float(v) for v in tail_local[k]]}
            if k < 3:
                nd['children'] = [tail_first + k + 1]
            nodes.append(nd)
        nodes[remap[hips_node]].setdefault('children', []).append(tail_first)
    dibm = acc_array(djs, db, dskin['inverseBindMatrices']).astype(np.float64)
    ibms = [dibm[i].reshape(4, 4).T for i in range(len(djoints))] + tail_ibm
    skin = {'name': dskin.get('name', 'skin'), 'joints': [remap[j] for j in djoints] +
            ([tail_first + k for k in range(4)] if tail is not None else []),
            'inverseBindMatrices': b.add_acc(np.stack([m.T.reshape(-1) for m in ibms]).astype('<f4'), 5126, 'MAT4')}
    if 'skeleton' in dskin:
        skin['skeleton'] = remap[dskin['skeleton']]
    # meshes: one new mesh per target primitive part, attributes rewritten
    out_meshes, mesh_nodes = [], []
    bymesh = {}
    for t in T:
        pr = t['pr']
        npr = {k: v for k, v in pr.items() if k not in ('attributes', 'indices')}
        att = {}
        for k, ai in pr['attributes'].items():
            arr = acc_array(tjs, tb, ai)
            acc = tjs['accessors'][ai]
            if k == 'POSITION':
                arr, ct = t['pos_n'].astype('<f4'), 5126
            elif k in ('NORMAL', 'TANGENT'):
                v = arr[:, :3].astype(np.float64)
                if acc['componentType'] == 5120:
                    v = v / 127.0
                v = v @ t['Rn'].T
                v /= np.linalg.norm(v, axis=1, keepdims=True).clip(min=1e-12)
                arr = np.hstack([v, arr[:, 3:4].astype(np.float64)]) if k == 'TANGENT' else v
                arr, ct = arr.astype('<f4'), 5126
            else:
                ct = acc['componentType']
            ni = b.add_acc(arr, ct, acc['type'])
            if acc.get('normalized') and ct == acc['componentType']:
                b.accs[ni]['normalized'] = True
            att[k] = ni
        att['JOINTS_0'] = b.add_acc(t['J'].astype('<u2'), 5123, 'VEC4')
        att['WEIGHTS_0'] = b.add_acc(t['W'].astype('<f4'), 5126, 'VEC4')
        npr['attributes'] = att
        if 'indices' in pr:
            ia = tjs['accessors'][pr['indices']]
            npr['indices'] = b.add_acc(acc_array(tjs, tb, pr['indices']).reshape(-1), ia['componentType'], 'SCALAR')
        key = t['node']
        if key not in bymesh:
            bymesh[key] = len(out_meshes)
            out_meshes.append({'name': tjs['meshes'][tjs['nodes'][key]['mesh']].get('name'), 'primitives': []})
            mesh_nodes.append(len(nodes))
            nodes.append({'name': t['name'], 'mesh': bymesh[key], 'skin': 0})
        out_meshes[bymesh[key]]['primitives'].append(npr)
    images = []
    for im in tjs.get('images', []):
        nim = dict(im)
        if 'bufferView' in im:
            bv = tjs['bufferViews'][im['bufferView']]
            o = bv.get('byteOffset', 0)
            nim['bufferView'] = b.add_bv(bytes(tb[o:o + bv['byteLength']]))
        images.append(nim)
    anims = []
    for an in djs.get('animations', []):
        smps, chs = [], []
        for ch in an['channels']:
            if ch['target'].get('node') not in remap:
                continue
            sm = an['samplers'][ch['sampler']]
            ia, oa = djs['accessors'][sm['input']], djs['accessors'][sm['output']]
            smps.append({'input': b.add_acc(acc_array(djs, db, sm['input']).reshape(-1), ia['componentType'], 'SCALAR'),
                         'output': b.add_acc(acc_array(djs, db, sm['output']), oa['componentType'], oa['type']),
                         'interpolation': sm.get('interpolation', 'LINEAR')})
            chs.append({'sampler': len(smps) - 1, 'target': {'node': remap[ch['target']['node']], 'path': ch['target']['path']}})
        anims.append({'name': an.get('name'), 'samplers': smps, 'channels': chs})
    out = {k: v for k, v in tjs.items() if k not in ('accessors', 'bufferViews', 'buffers', 'images', 'nodes', 'scenes',
                                                    'skins', 'animations', 'meshes', 'scene', 'extensionsUsed', 'extensionsRequired')}
    used = [e for e in tjs.get('extensionsUsed', []) if e != 'EXT_meshopt_compression']
    if used:
        out['extensionsUsed'] = used
    out['meshes'] = out_meshes
    if images:
        out['images'] = images
    out['nodes'] = nodes
    out['scenes'] = [{'name': 'Scene', 'nodes': [remap[r] for r in djs['scenes'][0]['nodes'] if r in remap] + mesh_nodes}]
    out['scene'] = 0
    out['skins'] = [skin]
    if anims:
        out['animations'] = anims
    out['asset'] = {'version': '2.0', 'generator': 'rig_multipart_from_donor.py (tools/auto_rig)'}
    b.write(a.out, out)
    rep['out'] = a.out
    rep['sha256'] = hashlib.sha256(open(a.out, 'rb').read()).hexdigest()
    rep['joints'] = len(skin['joints'])
    rep['tail'] = tail is not None
    print(json.dumps(rep, indent=1))
    if a.report:
        json.dump(rep, open(a.report, 'w'), indent=1)


if __name__ == '__main__':
    main()
