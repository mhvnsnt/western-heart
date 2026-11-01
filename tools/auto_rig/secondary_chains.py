#!/usr/bin/env python3
"""tools/auto_rig/secondary_chains.py — long hair gets its own bone chains (production hair physics, owner 2026-11-01:
"industry standard ... production studio level hair physics"), so it hangs from the head and the game simulates it,
instead of riding the spine and thighs and tearing (Phantom's waist-length hair failed the stretch gate at p99.9
7.3 because it was weighted to his legs: docs/proof/2026-11-01/refit-batch/phantom-a1/weights.png).

  1. long hair = the part of the mesh that hangs off the head below the neck: a flood fill from the Head-weighted
     vertices above the Neck joint through every vertex that is not body skin (neck cylinder, arm capsules, the back
     surface down to the hips, the leg capsules: head_territory.py's barriers without its "nothing below Spine2"
     cut), kept below the neck. None, or too short: the GLB is copied unchanged.
  2. 2-6 guide strands across its width (equal-count lateral bins), each a chain of --joints joints from the back
     of the head to the hair tips; every bone's +Y points down its strand (the game's springbones.js aims +Y at the
     simulated tail). Named hair_jiggle_<strand>_<joint>: game/js/springbones.js autoDiscover finds them (family
     'hair': TressFX-style stiffness falloff, body colliders) and integration.js runs them every frame.
  3. weights: along the strand a hat function per bone, across strands a linear blend between the two nearest,
     the root faded into Head; top-4, normalized. The baked gate clip has no channels for the new bones, so in the
     stretch gate the hair moves rigidly with the head (as it does at rest in the game before physics moves it).

    python3 tools/auto_rig/secondary_chains.py --in RIG.glb --out RIG2.glb [--report rep.json] [--joints 4]
Plain glTF in (decode meshopt first). Called by tools/auto_rig/refit_rig.py after head_territory.py.
"""
import argparse
import json
import os
import shutil
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fix_sternum_weights import read_glb, write_glb, view  # noqa: E402


def node_local(nd):
    if 'matrix' in nd:
        return np.asarray(nd['matrix'], dtype=np.float64).reshape(4, 4).T
    T = np.eye(4)
    t = nd.get('translation', [0, 0, 0]); r = nd.get('rotation', [0, 0, 0, 1]); s = nd.get('scale', [1, 1, 1])
    x, y, z, w = r
    R = np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                  [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                  [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])
    T[:3, :3] = R * np.asarray(s)[None, :]
    T[:3, 3] = t
    return T


def world_matrices(js):
    par = {}
    for i, nd in enumerate(js['nodes']):
        for c in nd.get('children', []):
            par[c] = i
    cache = {}

    def W(i):
        if i not in cache:
            cache[i] = (W(par[i]) if i in par else np.eye(4)) @ node_local(js['nodes'][i])
        return cache[i]
    return W


def quat_from_matrix(R):
    m = R
    tr = m[0, 0] + m[1, 1] + m[2, 2]
    if tr > 0:
        s = np.sqrt(tr + 1.0) * 2; w = 0.25 * s
        x = (m[2, 1] - m[1, 2]) / s; y = (m[0, 2] - m[2, 0]) / s; z = (m[1, 0] - m[0, 1]) / s
    elif m[0, 0] > m[1, 1] and m[0, 0] > m[2, 2]:
        s = np.sqrt(1.0 + m[0, 0] - m[1, 1] - m[2, 2]) * 2
        w = (m[2, 1] - m[1, 2]) / s; x = 0.25 * s; y = (m[0, 1] + m[1, 0]) / s; z = (m[0, 2] + m[2, 0]) / s
    elif m[1, 1] > m[2, 2]:
        s = np.sqrt(1.0 + m[1, 1] - m[0, 0] - m[2, 2]) * 2
        w = (m[0, 2] - m[2, 0]) / s; x = (m[0, 1] + m[1, 0]) / s; y = 0.25 * s; z = (m[1, 2] + m[2, 1]) / s
    else:
        s = np.sqrt(1.0 + m[2, 2] - m[0, 0] - m[1, 1]) * 2
        w = (m[1, 0] - m[0, 1]) / s; x = (m[0, 2] + m[2, 0]) / s; y = (m[1, 2] + m[2, 1]) / s; z = 0.25 * s
    q = np.array([x, y, z, w]); return q / np.linalg.norm(q)


def y_to(d):
    """Rotation whose +Y axis points along d."""
    y = d / max(np.linalg.norm(d), 1e-9)
    a = np.array([0.0, 0.0, 1.0]) if abs(y[2]) < 0.9 else np.array([1.0, 0.0, 0.0])
    x = np.cross(y, a); x /= np.linalg.norm(x)
    z = np.cross(x, y)
    return np.stack([x, y, z], axis=1)


def seg_dist(P, A, B):
    ab = B - A
    t = np.clip(((P - A) @ ab) / max(ab @ ab, 1e-12), 0, 1)
    return np.linalg.norm(P - (A + t[:, None] * ab), axis=1)


def detect(P, tris, jp, H, Wh):
    """Welded-mesh flood fill from the Head-weighted vertices above the neck through non-body vertices."""
    from scipy.sparse import coo_matrix
    from scipy.sparse.csgraph import connected_components
    key = np.round(P / 1e-6).astype(np.int64)
    _, first, inv = np.unique(key, axis=0, return_index=True, return_inverse=True)
    inv = inv.reshape(-1)
    Pw = P[first]
    Tw = inv[tris]
    head, neck, s2, hips = jp['Head'], jp['Neck'], jp['Spine2'], jp['Hips']
    neck_r = 0.05 * H
    t = np.clip((Pw[:, 1] - neck[1]) / max(head[1] - neck[1], 1e-6), 0, 1)
    ax = neck[[0, 2]][None, :] * (1 - t[:, None]) + head[[0, 2]][None, :] * t[:, None]
    b_neck = (Pw[:, 1] < head[1]) & (np.linalg.norm(Pw[:, [0, 2]] - ax, axis=1) < neck_r)
    arm_r = 0.35 * np.mean([np.linalg.norm(jp[s + 'ForeArm'] - jp[s + 'Arm']) for s in ('Left', 'Right')])
    b_arm = np.min([seg_dist(Pw, jp[s + a], jp[s + b]) for s in ('Left', 'Right')
                    for a, b in (('Shoulder', 'Arm'), ('Arm', 'ForeArm'))], axis=0) < arm_r
    leg_r = 0.06 * H
    b_leg = np.min([seg_dist(Pw, jp[s + a], jp[s + b]) for s in ('Left', 'Right')
                    for a, b in (('UpLeg', 'Leg'), ('Leg', 'Foot'))], axis=0) < leg_r
    # the back surface at the mid-line, hips to neck: body = in front of it (1 cm margin)
    mid = np.abs(Pw[:, 0] - neck[0]) < 0.012 * H
    zb = []
    for y in np.linspace(hips[1], neck[1], 14):
        z = np.sort(Pw[mid & (np.abs(Pw[:, 1] - y) < 0.0015 * H), 2])[::-1]
        g = np.nonzero(-np.diff(z) > 0.012 * H)[0] if len(z) > 6 else []
        if len(g):
            zb.append((y, z[g[0] + 1]))
    if len(zb) < 3:
        return None, None, {'skipped': 'no back surface found at the mid-line'}
    zback = np.interp(Pw[:, 1], [y for y, _ in zb], [z for _, z in zb])
    b_torso = (Pw[:, 1] < neck[1]) & (Pw[:, 1] > hips[1] - 0.05 * H) & (Pw[:, 2] > zback - 0.01 * H)
    blocked = b_neck | b_arm | b_leg | b_torso
    ok = ~blocked
    e = np.concatenate([Tw[:, [0, 1]], Tw[:, [1, 2]], Tw[:, [2, 0]]])
    e = e[ok[e[:, 0]] & ok[e[:, 1]]]
    A = coo_matrix((np.ones(len(e), dtype=np.int8), (e[:, 0], e[:, 1])), shape=(len(Pw), len(Pw)))
    _, lab = connected_components(A, directed=False)
    seeds = ok & (Pw[:, 1] > head[1])     # geometric, as head_territory.py: independent of the incoming weights
    if not seeds.any():
        return None, None, {'skipped': 'no mesh above the Head joint'}
    reach = ok & np.isin(lab, np.unique(lab[seeds]))
    long_w = reach & (Pw[:, 1] < neck[1] - 0.02 * H)
    diag = {'barrier': {'neck': int(b_neck.sum()), 'arm': int(b_arm.sum()), 'leg': int(b_leg.sum()), 'torso': int(b_torso.sum())},
            'reach_welded': int(reach.sum()), 'long_hair_welded': int(long_w.sum())}
    return long_w[inv], neck[1], diag


def run(inp, outp, report=None, joints=4):
    js, binarr = read_glb(inp)
    binarr = bytearray(binarr)
    parts, skin_i, seen = [], None, set()
    for nd in js['nodes']:
        if 'mesh' not in nd or nd.get('skin') is None:
            continue
        skin_i = nd['skin'] if skin_i is None else skin_i
        for pi, prim in enumerate(js['meshes'][nd['mesh']]['primitives']):
            at = prim['attributes']
            if (nd['mesh'], pi) in seen or 'JOINTS_0' not in at:
                continue
            seen.add((nd['mesh'], pi))
            P = np.asarray(view(js, binarr, at['POSITION'])[0], dtype=np.float64)
            T = (np.asarray(view(js, binarr, prim['indices'])[0]).reshape(-1, 3).astype(np.int64) if 'indices' in prim
                 else np.arange(len(P)).reshape(-1, 3))
            parts.append({'at': at, 'P': P, 'T': T})
    skin = js['skins'][skin_i]
    ibm_acc = skin['inverseBindMatrices']
    IBM = np.asarray(view(js, binarr, ibm_acc)[0], dtype=np.float64).reshape(-1, 4, 4).transpose(0, 2, 1)
    names = [js['nodes'][j].get('name', '').split(':')[-1] for j in skin['joints']]
    jp = {n: np.linalg.inv(m)[:3, 3] for n, m in zip(names, IBM)}
    out = {'input': inp, 'tool': 'tools/auto_rig/secondary_chains.py'}
    need = ['Head', 'Neck', 'Spine2', 'Hips', 'LeftArm', 'RightArm', 'LeftForeArm', 'RightForeArm', 'LeftShoulder',
            'RightShoulder', 'LeftUpLeg', 'RightUpLeg', 'LeftLeg', 'RightLeg', 'LeftFoot', 'RightFoot']
    if any(n not in jp for n in need) or any(n.startswith('hair_jiggle') for n in names):
        out['skipped'] = 'nonstandard skeleton or chains already present'
        shutil.copy(inp, outp)
        return out
    offs = np.cumsum([0] + [len(q['P']) for q in parts])
    P = np.concatenate([q['P'] for q in parts])
    tris = np.concatenate([q['T'] + o for q, o in zip(parts, offs[:-1])])
    Jv = [view(js, binarr, q['at']['JOINTS_0'])[0] for q in parts]
    Wv = [view(js, binarr, q['at']['WEIGHTS_0'])[0] for q in parts]
    Jn = np.concatenate([np.asarray(j).astype(np.int64) for j in Jv])
    W = np.concatenate([np.asarray(w, dtype=np.float64) for w in Wv])
    ih = names.index('Head')
    Wh = (W * (Jn == ih)).sum(1)
    H = float(P[:, 1].max() - P[:, 1].min())
    long, y_neck, diag = detect(P, tris, jp, H, Wh)
    out['detect'] = diag
    if long is None or long.sum() < max(200, 0.002 * len(P)) or (P[long, 1].max() - P[long, 1].min()) < 0.12 * H:
        out['skipped'] = out.get('skipped') or diag.get('skipped') or 'no long hair (none hangs 12% of the height below the neck)'
        shutil.copy(inp, outp)
        return out
    L = P[long]
    y0, y1 = float(y_neck), float(L[:, 1].min())
    width = float(np.percentile(L[:, 0], 95) - np.percentile(L[:, 0], 5))
    K = int(np.clip(round(width / (0.07 * H)), 2, 6))
    edges = np.percentile(L[:, 0], np.linspace(0, 100, K + 1))
    chains = []
    ys = np.linspace(y0, y1, joints)
    for k in range(K):
        sel = (L[:, 0] >= edges[k]) & (L[:, 0] <= edges[k + 1])
        Q = L[sel]
        pts = []
        for y in ys:
            band = Q[np.abs(Q[:, 1] - y) < max(0.03 * H, abs(y0 - y1) / (2 * joints))]
            if len(band) == 0:
                band = Q[np.argsort(np.abs(Q[:, 1] - y))[:20]]
            pts.append([float(np.median(band[:, 0])), float(y), float(np.median(band[:, 2]))])
        chains.append(np.array(pts))
    cx = np.array([c[:, 0].mean() for c in chains])
    # weights for the long-hair vertices
    s = np.clip((y0 - L[:, 1]) / max(y0 - y1, 1e-9), 0, 1) * (joints - 1)          # 0 .. joints-1 along the strand
    nb_old = len(names)
    jid = lambda k, i: nb_old + k * joints + i
    order = np.argsort(cx)
    cxs = cx[order]
    pos = np.clip(np.interp(L[:, 0], cxs, np.arange(K)), 0, K - 1)
    ka, kb = np.floor(pos).astype(int), np.minimum(np.floor(pos).astype(int) + 1, K - 1)
    tb = pos - ka
    newJ, newW = [], []
    for v in range(len(L)):
        acc = {}
        for kk, wk in ((order[ka[v]], 1 - tb[v]), (order[kb[v]], tb[v])):
            if wk <= 1e-6:
                continue
            for i in range(joints):
                h = max(0.0, 1.0 - abs(s[v] - i))          # hat around joint i: bone i carries the vertex near it
                if h > 0:
                    acc[jid(kk, i)] = acc.get(jid(kk, i), 0.0) + wk * h
        root = max(0.0, 1.0 - s[v] / 0.5)                  # the first half segment fades into Head
        if root > 0:
            acc = {j: w * (1 - root) for j, w in acc.items()}
            acc[ih] = acc.get(ih, 0.0) + root
        top = sorted(acc.items(), key=lambda kv: -kv[1])[:4]
        tot = sum(w for _, w in top) or 1.0
        top += [(0, 0.0)] * (4 - len(top))
        newJ.append([j for j, _ in top]); newW.append([w / tot for _, w in top])
    # nodes: hair_jiggle_<k>_<i>, +Y down the strand, root parented to the Head node
    Wm = world_matrices(js)
    head_node = skin['joints'][ih]
    new_nodes, new_ibm = [], []
    for k, c in enumerate(chains):
        parent, parent_world = head_node, Wm(head_node)
        for i in range(joints):
            d = (c[i + 1] - c[i]) if i < joints - 1 else (c[i] - c[i - 1])
            Wn = np.eye(4); Wn[:3, :3] = y_to(d); Wn[:3, 3] = c[i]
            local = np.linalg.inv(parent_world) @ Wn
            Rl = local[:3, :3]
            sc = np.linalg.norm(Rl, axis=0)
            nd = {'name': 'hair_jiggle_%d_%d' % (k, i), 'translation': [float(x) for x in local[:3, 3]],
                  'rotation': [float(x) for x in quat_from_matrix(Rl / sc[None, :])]}
            if np.any(np.abs(sc - 1) > 1e-4):
                nd['scale'] = [float(x) for x in sc]
            js['nodes'].append(nd)
            ni = len(js['nodes']) - 1
            js['nodes'][parent].setdefault('children', []).append(ni)
            skin['joints'].append(ni)
            new_ibm.append(np.linalg.inv(Wn))
            parent, parent_world = ni, Wn
            new_nodes.append(nd['name'])
    if len(skin['joints']) > 255 and any(js['accessors'][q['at']['JOINTS_0']]['componentType'] == 5121 for q in parts):
        raise SystemExit('more than 255 joints with 8-bit JOINTS_0')
    # new inverse-bind accessor (old + new), appended to the BIN chunk
    allm = np.concatenate([IBM, np.stack(new_ibm)]).transpose(0, 2, 1).astype(np.float32)   # column-major
    while len(binarr) % 4:
        binarr.append(0)
    off = len(binarr)
    binarr += allm.tobytes()
    js['bufferViews'].append({'buffer': 0, 'byteOffset': off, 'byteLength': allm.nbytes})
    js['accessors'].append({'bufferView': len(js['bufferViews']) - 1, 'componentType': 5126, 'count': len(allm), 'type': 'MAT4'})
    skin['inverseBindMatrices'] = len(js['accessors']) - 1
    js['buffers'][0]['byteLength'] = len(binarr)
    # write the long-hair vertices' joints / weights back into every part
    gidx = np.nonzero(long)[0]
    newJ, newW = np.array(newJ), np.array(newW)
    for q, o, jv, wv in zip(parts, offs[:-1], Jv, Wv):
        m = (gidx >= o) & (gidx < o + len(q['P']))
        if not m.any():
            continue
        loc = gidx[m] - o
        jv2, _ = view(js, binarr, q['at']['JOINTS_0'])
        wv2, _ = view(js, binarr, q['at']['WEIGHTS_0'])
        jv2[loc] = newJ[m].astype(jv2.dtype)
        wv2[loc] = newW[m].astype(wv2.dtype)
    write_glb(outp, js, bytes(binarr))
    out.update({'strands': K, 'joints_per_strand': joints, 'new_bones': new_nodes, 'long_hair_verts': int(long.sum()),
                'hair_span_m': [round(y0, 3), round(y1, 3)], 'width_m': round(width, 3)})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--in', dest='inp', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--report')
    ap.add_argument('--joints', type=int, default=4)
    a = ap.parse_args()
    rep = run(a.inp, a.out, a.report, a.joints)
    if a.report:
        json.dump(rep, open(a.report, 'w'), indent=1)
    print(json.dumps(rep, indent=1))


if __name__ == '__main__':
    main()
