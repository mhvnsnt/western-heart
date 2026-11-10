#!/usr/bin/env python3
"""tools/auto_rig/reparent_joints.py — move a joint under another parent without changing the bind pose.

Why (2026-11-10, TOU): the real Tekken 7 skeleton (SKT_CH_base) keeps the legs and the upper body as SIBLINGS under
BASE (BASE -> Hip -> legs, BASE -> Spine1 -> chest / arms / head). Every clip the game plays drives its root motion on
Hips, the way the Tekken 3 / Mixamo hierarchy it retargets onto expects (Hips -> Spine -> ...). On TOU's T7 body
(assembled from Paul's real parts, PR #1711) the Hips' drop and turn therefore moved only his legs: standing it does
not show, but his KO left his pelvis on the floor and his upper body hanging ~0.6 m above it on a stretched column.
Reparenting Spine1 under Hips gives the game's hierarchy. The child's new local transform is
inverse(new parent world) x child world, so every joint keeps its world bind transform: the inverse bind matrices,
the weights and the bind-pose mesh are unchanged (checked: max world-position change of every node is printed).

Input and output are PLAIN (decoded) GLBs (tools/anim/gltf_codec.mjs decode / encode). Only the JSON chunk changes.

    python3 tools/auto_rig/reparent_joints.py --in plain.glb --out out.glb --move Spine1:Hips [--move A:B ...]
"""
import argparse
import json
import struct
import sys

import numpy as np


def quat_to_mat(q):
    x, y, z, w = q
    return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                     [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                     [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])


def mat_to_quat(m):
    t = np.trace(m)
    if t > 0:
        s = np.sqrt(t + 1.0) * 2
        q = [(m[2, 1] - m[1, 2]) / s, (m[0, 2] - m[2, 0]) / s, (m[1, 0] - m[0, 1]) / s, 0.25 * s]
    elif m[0, 0] > m[1, 1] and m[0, 0] > m[2, 2]:
        s = np.sqrt(1.0 + m[0, 0] - m[1, 1] - m[2, 2]) * 2
        q = [0.25 * s, (m[0, 1] + m[1, 0]) / s, (m[0, 2] + m[2, 0]) / s, (m[2, 1] - m[1, 2]) / s]
    elif m[1, 1] > m[2, 2]:
        s = np.sqrt(1.0 + m[1, 1] - m[0, 0] - m[2, 2]) * 2
        q = [(m[0, 1] + m[1, 0]) / s, 0.25 * s, (m[1, 2] + m[2, 1]) / s, (m[0, 2] - m[2, 0]) / s]
    else:
        s = np.sqrt(1.0 + m[2, 2] - m[0, 0] - m[1, 1]) * 2
        q = [(m[0, 2] + m[2, 0]) / s, (m[1, 2] + m[2, 1]) / s, 0.25 * s, (m[1, 0] - m[0, 1]) / s]
    q = np.array(q)
    return q / np.linalg.norm(q)


def local_matrix(nd):
    if 'matrix' in nd:
        return np.array(nd['matrix'], dtype=np.float64).reshape(4, 4).T
    m = np.eye(4)
    s = np.array(nd.get('scale', [1, 1, 1]), dtype=np.float64)
    m[:3, :3] = quat_to_mat(nd.get('rotation', [0, 0, 0, 1])) * s[None, :]
    m[:3, 3] = nd.get('translation', [0, 0, 0])
    return m


def world_matrices(nodes):
    par = {c: i for i, nd in enumerate(nodes) for c in nd.get('children', [])}
    out = {}

    def w(i):
        if i not in out:
            out[i] = (w(par[i]) @ local_matrix(nodes[i])) if i in par else local_matrix(nodes[i])
        return out[i]
    for i in range(len(nodes)):
        w(i)
    return out, par


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--in', dest='inp', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--move', action='append', required=True, help='CHILD:NEWPARENT (node names)')
    a = ap.parse_args()
    raw = open(a.inp, 'rb').read()
    n = struct.unpack_from('<I', raw, 12)[0]
    js = json.loads(raw[20:20 + n])
    rest = raw[20 + n:]
    nodes = js['nodes']
    idx = {nd.get('name'): i for i, nd in enumerate(nodes)}
    before, _ = world_matrices(nodes)
    for mv in a.move:
        child, parent = mv.split(':')
        ci, pi = idx[child], idx[parent]
        W, par = world_matrices(nodes)
        if par.get(ci) == pi:
            continue
        anc = pi
        while anc in par:
            if anc == ci:
                sys.exit(f'{parent} is a descendant of {child}')
            anc = par[anc]
        loc = np.linalg.inv(W[pi]) @ W[ci]
        sc = np.linalg.norm(loc[:3, :3], axis=0)
        nd = nodes[ci]
        nd.pop('matrix', None)
        nd['translation'] = [float(x) for x in loc[:3, 3]]
        nd['rotation'] = [float(x) for x in mat_to_quat(loc[:3, :3] / sc[None, :])]
        if np.abs(sc - 1).max() > 1e-6:
            nd['scale'] = [float(x) for x in sc]
        else:
            nd.pop('scale', None)
        if ci in par:
            nodes[par[ci]]['children'] = [c for c in nodes[par[ci]]['children'] if c != ci]
            if not nodes[par[ci]]['children']:
                nodes[par[ci]].pop('children')
        else:
            for sc_ in js.get('scenes', []):
                sc_['nodes'] = [c for c in sc_.get('nodes', []) if c != ci]
        nodes[pi].setdefault('children', []).append(ci)
    after, _ = world_matrices(nodes)
    drift = max(float(np.abs(after[i] - before[i]).max()) for i in range(len(nodes)))
    j = json.dumps(js, separators=(',', ':')).encode()
    j += b' ' * ((4 - len(j) % 4) % 4)
    out = struct.pack('<III', 0x46546C67, 2, 12 + 8 + len(j) + len(rest)) + struct.pack('<II', len(j), 0x4E4F534A) + j + rest
    open(a.out, 'wb').write(out)
    print(json.dumps({'tool': 'tools/auto_rig/reparent_joints.py', 'moves': a.move, 'max_world_matrix_change': drift}))
    if drift > 1e-5:
        sys.exit('bind pose changed: refusing')


if __name__ == '__main__':
    main()
