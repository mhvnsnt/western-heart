#!/usr/bin/env python3
"""True linear-blend-skinning distortion arbiter for head-region fixes.

Skins the model's own verts with its own weights under two canonical poses
and measures pairwise-distance distortion inside spatial bands along the
Neck->Head axis (t: neck joint = 0, head joint = 1):

  face    t >= 1.2          (skull/face proper)
  jaw     0.4 <= t < 1.2    (jaw / lower face / throat)
  collar  -0.6 <= t < 0.4   (neck base / collar / shoulder junction)

Poses (world-space deltas about each joint's bind position, composed down
the hierarchy so descendants inherit):
  A head-turn : Head +35 deg about the Neck->Head axis, Neck -12 deg
                (a genuine bank head turn with natural counter-rotation)
  B body-sway : chest (Neck's parent joint) + L/R Shoulder +8 deg pitch
                about the armature X axis; head/neck unposed, they inherit
                chest motion through the hierarchy — face distortion here is
                pure weight-bleed drag from body bones.

Bands: face/jaw are intersected with the head-assembly region
(chainw >= 0.10) — on multi-arm rigs (dxmmii) the spatial shell above the
neck also contains raised arm geometry weighted to arm bones; pairwise
distortion across two anatomical parts measures their relative motion,
not face stretch. The collar band stays purely spatial (it is the seam
zone).

Seam metric: mean change in collar<->chest pairwise distances (chest =
verts with chainw < 0.02 and -2.5 <= t < -0.6) under each pose — how much
the collar band separates from the chest it sits on.

Usage: head_distortion.py file.glb  -> JSON
"""
import json, sys, os
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ingest import GLBDoc
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from headpick import pick_head

def local_mat(nd):
    if 'matrix' in nd:
        return np.array(nd['matrix'], dtype=np.float64).reshape(4, 4).T
    t = nd.get('translation', [0, 0, 0]); r = nd.get('rotation', [0, 0, 0, 1]); s = nd.get('scale', [1, 1, 1])
    x, y, z, w = r
    R = np.array([[1-2*(y*y+z*z), 2*(x*y-z*w), 2*(x*z+y*w)],
                  [2*(x*y+z*w), 1-2*(x*x+z*z), 2*(y*z-x*w)],
                  [2*(x*z-y*w), 2*(y*z+x*w), 1-2*(x*x+y*y)]], dtype=np.float64)
    M = np.eye(4); M[:3, :3] = R * np.array(s, dtype=np.float64); M[:3, 3] = t
    return M

def rot_about(axis, deg, point):
    a = axis / np.linalg.norm(axis)
    th = np.radians(deg); c, s = np.cos(th), np.sin(th)
    K = np.array([[0, -a[2], a[1]], [a[2], 0, -a[0]], [-a[1], a[0], 0]])
    R = np.eye(3) * c + s * K + (1 - c) * np.outer(a, a)
    M = np.eye(4); M[:3, :3] = R; M[:3, 3] = point - R @ point
    return M

def run(path):
    doc = GLBDoc(path)
    j = doc.json
    nodes = j['nodes']
    parent = {}
    order = []
    for i, nd in enumerate(nodes):
        for c in nd.get('children', []):
            parent[c] = i
    # parent-before-child order via DFS from scene roots
    roots = [n for sc in j.get('scenes', [{}]) for n in sc.get('nodes', [])]
    seen = set()
    def dfs(n):
        if n in seen: return
        seen.add(n); order.append(n)
        for c in nodes[n].get('children', []): dfs(c)
    for r in roots: dfs(r)
    for i in range(len(nodes)): dfs(i)
    L = {i: local_mat(nodes[i]) for i in range(len(nodes))}
    W = {}
    for i in order:
        W[i] = (W[parent[i]] @ L[i]) if i in parent else L[i]
    sk = j['skins'][0]
    joint_nodes = sk['joints']
    n_j = len(joint_nodes)
    jname = {ji: (nodes[n].get('name') or f'j{n}') for ji, n in enumerate(joint_nodes)}
    node2joint = {n: ji for ji, n in enumerate(joint_nodes)}
    children = {}
    for i, nd in enumerate(nodes):
        for c in nd.get('children', []):
            children.setdefault(i, []).append(c)
    def descendants(ni):
        res, stack = [], list(children.get(ni, []))
        while stack:
            c = stack.pop(); res.append(c); stack += children.get(c, [])
        return res
    ibm = doc.accessor(sk['inverseBindMatrices']).astype(np.float64).reshape(n_j, 4, 4)
    ibm = np.transpose(ibm, (0, 2, 1))
    bindpos = np.linalg.inv(ibm)[:, :3, 3]
    prim_JW = []
    for mi, m in enumerate(j['meshes']):
        for pr in m['primitives']:
            at = pr['attributes']
            if 'JOINTS_0' not in at: continue
            Js = [doc.accessor(at['JOINTS_0']).astype(np.int64)]
            Ws = [doc.accessor(at['WEIGHTS_0']).astype(np.float64)]
            if 'JOINTS_1' in at:
                Js.append(doc.accessor(at['JOINTS_1']).astype(np.int64))
                Ws.append(doc.accessor(at['WEIGHTS_1']).astype(np.float64))
            prim_JW.append((np.concatenate(Js, 1), np.concatenate(Ws, 1)))
    hj, chain = pick_head(jname, joint_nodes, descendants, node2joint, prim_JW)
    head_node = joint_nodes[hj]
    neck_ji = node2joint[parent[head_node]]
    chest_ji = node2joint.get(parent[joint_nodes[neck_ji]])
    shoulder_jis = [ji for ji, nm in jname.items() if nm.lower().replace('_', '').replace(' ', '') in
                    ('leftshoulder', 'rightshoulder', 'lshoulder', 'rshoulder')]
    neck_pos, head_pos = bindpos[neck_ji], bindpos[hj]
    axis = head_pos - neck_pos; axlen = np.linalg.norm(axis); axis = axis / axlen
    # skin sanity: bind skin matrices ~ identity
    Sbind = np.stack([W[joint_nodes[k]] @ ibm[k] for k in range(n_j)])
    sanity = float(np.abs(Sbind - np.eye(4)).max())
    # gather verts (first skinned prim set, armature space)
    out = {'path': path, 'bind_sanity_max_dev': round(sanity, 4),
           'chest': jname.get(chest_ji), 'shoulders': [jname[s] for s in shoulder_jis]}
    allP, allJ, allW = [], [], []
    for mi, m in enumerate(j['meshes']):
        mn = next((i for i, nd in enumerate(nodes) if nd.get('mesh') == mi), None)
        MW = W[mn] if mn is not None else np.eye(4)
        for pr in m['primitives']:
            at = pr['attributes']
            if 'JOINTS_0' not in at: continue
            P0 = doc.accessor(at['POSITION']).astype(np.float64)
            P = (MW[:3, :3] @ P0.T).T + MW[:3, 3]
            Js = [doc.accessor(at['JOINTS_0']).astype(np.int64)]
            Ws = [doc.accessor(at['WEIGHTS_0']).astype(np.float64)]
            if 'JOINTS_1' in at:
                Js.append(doc.accessor(at['JOINTS_1']).astype(np.int64))
                Ws.append(doc.accessor(at['WEIGHTS_1']).astype(np.float64))
            allP.append(P); allJ.append(np.concatenate(Js, 1)); allW.append(np.concatenate(Ws, 1))
    P = np.concatenate(allP); J = np.concatenate(allJ); Wt = np.concatenate(allW)
    chainw = np.where(np.isin(J, list(chain)), Wt, 0.0).sum(axis=1)
    t = ((P - neck_pos) @ axis) / axlen
    # only verts in/near the measured bands can affect the metric — skin
    # just that subset (large models carry 1M+ verts, mostly legs/torso)
    keep = t >= -2.6
    P, J, Wt, chainw, t = P[keep], J[keep], Wt[keep], chainw[keep], t[keep]
    bands = {'face': (t >= 1.2) & (chainw >= 0.10), 'jaw': (t >= 0.4) & (t < 1.2) & (chainw >= 0.10),
             'collar': (t >= -0.6) & (t < 0.4)}
    chest_ref = (chainw < 0.02) & (t >= -2.5) & (t < -0.6)
    def sample(mask, k=48):
        idx = np.where(mask)[0]
        if len(idx) == 0: return idx
        return idx[::max(1, len(idx) // k)][:k]
    samples = {b: sample(m) for b, m in bands.items()}
    chest_s = sample(chest_ref, 32)
    def skin(S):
        # S: (n_j,4,4) skin matrices; returns posed positions
        acc = np.zeros((len(P), 3))
        Ph = np.concatenate([P, np.ones((len(P), 1))], 1)
        for c in range(J.shape[1]):
            jj = J[:, c]; w = Wt[:, c]
            sel = w > 0
            if not sel.any(): continue
            M = S[jj[sel]]
            acc[sel] += w[sel, None] * np.einsum('nij,nj->ni', M, Ph[sel])[:, :3]
        return acc
    def posed_world(deltas):
        Wp = {}
        for i in order:
            base = (Wp[parent[i]] @ np.linalg.inv(W[parent[i]]) @ W[i]) if i in parent else W[i]
            ji = node2joint.get(i)
            if ji is not None and ji in deltas:
                base = deltas[ji] @ base
            Wp[i] = base
        return np.stack([Wp[joint_nodes[k]] @ ibm[k] for k in range(n_j)])
    poses = {
        'A_headturn': {hj: rot_about(axis, 35.0, head_pos), neck_ji: rot_about(axis, -12.0, neck_pos)},
        'B_bodysway': {ji: rot_about(np.array([1.0, 0, 0]), 8.0, bindpos[ji])
                       for ji in ([chest_ji] if chest_ji is not None else []) + shoulder_jis},
    }
    def pairdist(A, B):
        d = np.linalg.norm(A[:, None, :] - B[None, :, :], axis=2)
        return d
    res = {}
    Sbind_m = np.stack([W[joint_nodes[k]] @ ibm[k] for k in range(n_j)])
    Prest = skin(Sbind_m)  # self-consistent rest: same pipeline as posed
    for pname, deltas in poses.items():
        Pp = skin(posed_world(deltas))
        pr = {}
        for b, idx in samples.items():
            if len(idx) < 4:
                pr[b] = None; continue
            d0 = pairdist(Prest[idx], Prest[idx]); d1 = pairdist(Pp[idx], Pp[idx])
            iu = np.triu_indices(len(idx), 1)
            eps = 0.01 * axlen  # coincident seam duplicates: ratio is meaningless
            good = d0[iu] >= eps
            rel = np.abs(d1[iu][good] - d0[iu][good]) / np.maximum(d0[iu][good], 1e-9)
            entry = {'n': int(len(idx)), 'mean': round(float(rel.mean()), 4) if len(rel) else 0.0,
                     'p90': round(float(np.percentile(rel, 90)), 4) if len(rel) else 0.0,
                     'max': round(float(rel.max()), 4) if len(rel) else 0.0}
            if (~good).any():
                entry['split_abs_max'] = round(float(np.abs(d1[iu][~good] - d0[iu][~good]).max()), 5)
                entry['degenerate_pairs'] = int((~good).sum())
            pr[b] = entry
        if len(chest_s) >= 4 and len(samples['collar']) >= 4:
            d0 = pairdist(Prest[samples['collar']], Prest[chest_s]); d1 = pairdist(Pp[samples['collar']], Pp[chest_s])
            rel = np.abs(d1 - d0) / np.maximum(d0, 1e-9)
            pr['seam_collar_chest'] = {'mean': round(float(rel.mean()), 4),
                                       'p90': round(float(np.percentile(rel, 90)), 4),
                                       'max': round(float(rel.max()), 4)}
        res[pname] = pr
    out['poses'] = res
    out['band_counts'] = {b: int(m.sum()) for b, m in bands.items()}
    return out

if __name__ == '__main__':
    print(json.dumps(run(sys.argv[1]), indent=1))
