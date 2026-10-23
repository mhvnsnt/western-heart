#!/usr/bin/env python3
"""Face-cone skin-weight audit + fixer (tools/rig/weight_audit.py).

The "upside-down teardrop / stretched balloon" artefact on faces is caused by
vertices above the neck line carrying weight on spine / pelvis / root / limb
bones. When the fighter animates, those verts get dragged toward the torso and
the face stretches into a cone down to the chin and spine. See
docs/tech/SKIN-WEIGHTS.md.

Reuses the GLB surgery helpers from tools/rig-repair/_common.py (PR #840).
Zones are computed in bind space from the inverse bind matrices:
  L      = head_y - neck_y
  zone A = y >= head_y - 0.2L, within R = 2.5L of the head axis  (face/skull)
           -> only head/jaw/face bones allowed
  zone B = neck_y <= y < zone A (same radius) -> neck/head/upper-chest allowed
Flags: face-cone verts (bad weight > 0.02), unnormalized (|sum-1| > 0.01),
>4 influences (JOINTS_1 in use), zero-weight verts.

Usage:
  weight_audit.py audit  FILE.glb...  [--json out.json]   exit 1 on face-cone
  weight_audit.py fix    IN.glb OUT.glb                    mesh/textures untouched
"""
import json, sys, os
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'rig-repair'))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))  # meshopt fallback shim
from _common import Glb, skin_joints, skinned_meshes  # noqa: E402

BAD_T = 0.02
HEADK = ('head', 'jaw', 'face', 'eye', 'brow', 'lip', 'tongue', 'cheek',
         'nose', 'ear', 'chin', 'teeth', 'mouth', 'hair', 'lid')
UPPER = ('neck', 'spine2', 'spine3', 'chest', 'upperchest', 'clavicle_')


def bname(g, j):
    return g['nodes'][j].get('name', '').lower().replace('mixamorig:', '').replace('mixamorig', '')


def is_head(n):
    return any(k in n for k in HEADK) and 'headtop_end' not in n or n.endswith('head')


def classify(g, joints):
    names = [bname(g, j) for j in joints]
    head = [i for i, n in enumerate(names) if is_head(n)]
    neck = [i for i, n in enumerate(names) if 'neck' in n]
    upper = [i for i, n in enumerate(names) if any(k in n for k in UPPER)]
    return names, set(head), set(neck), set(upper) | set(neck)


def bind_pos(glb, skin):
    ibm = glb.decode(skin['inverseBindMatrices']).reshape(-1, 4, 4).transpose(0, 2, 1)
    return np.array([np.linalg.inv(m)[:3, 3] for m in ibm])


def analyse(glb, fix=False):
    g = glb.g
    out = []
    for ni, si, mesh, pi, prim in skinned_meshes(glb):
        skin = g['skins'][si]
        joints = skin['joints']
        names, head, neck, allowB = classify(g, joints)
        rec = {'mesh': mesh.get('name', str(ni)), 'prim': pi, 'verts': 0,
               'face_cone': 0, 'unnormalized': 0, 'over4': 0, 'zero': 0,
               'skipped': None}
        if not head or not neck or 'inverseBindMatrices' not in skin:
            rec['skipped'] = 'no head/neck bones'
            out.append(rec); continue
        P = glb.decode(prim['attributes']['POSITION'], normalize=False)
        J = glb.decode_int(prim['attributes']['JOINTS_0'])
        W = glb.decode(prim['attributes']['WEIGHTS_0']).astype(np.float64)
        rec['verts'] = len(P)
        if 'WEIGHTS_1' in prim['attributes']:
            W1 = glb.decode(prim['attributes']['WEIGHTS_1'])
            rec['over4'] = int(((W1 > 1e-4).sum(1) > 0).sum())
        bp = bind_pos(glb, skin)
        hi = min(head, key=lambda i: (names[i] != 'head', -bp[i][1] if names[i] != 'head' else 0))
        hi = next((i for i in head if names[i] == 'head'), hi)
        nk = next((i for i in neck if names[i] == 'neck'), min(neck))
        hy, ny = bp[hi][1], bp[nk][1]
        L = hy - ny
        if L <= 1e-6:
            rec['skipped'] = 'degenerate neck/head'
            out.append(rec); continue
        R = 2.5 * L
        rad = np.hypot(P[:, 0] - bp[hi][0], P[:, 2] - bp[hi][2])
        zA = (P[:, 1] >= hy - 0.2 * L) & (rad < R)
        zB = (P[:, 1] >= ny) & ~zA & (rad < R)
        s = W.sum(1)
        rec['unnormalized'] = int((np.abs(s - 1) > 0.01).sum())
        rec['zero'] = int((s < 1e-6).sum())
        headmask = np.isin(J, list(head))
        allowBm = np.isin(J, list(allowB | head))
        badA = (W * ~headmask).sum(1) * zA
        badB = (W * ~allowBm).sum(1) * zB
        bad = (badA > BAD_T) | (badB > BAD_T)
        rec['face_cone'] = int(bad.sum())
        rec['max_bad'] = float(max(badA.max(initial=0), badB.max(initial=0)))
        top = {}
        for v in np.nonzero(bad)[0][:5000]:
            for k in range(4):
                if W[v, k] > BAD_T and not headmask[v, k]:
                    top[names[J[v, k]]] = top.get(names[J[v, k]], 0) + 1
        rec['offending_bones'] = dict(sorted(top.items(), key=lambda t: -t[1])[:6])
        if fix and (bad.any() or rec['unnormalized'] or rec['zero']):
            jaw = next((i for i in head if 'jaw' in names[i]), None)
            NJ, NW = J.copy(), W.copy()
            for v in np.nonzero(bad | (np.abs(s - 1) > 0.01))[0]:
                y = P[v, 1]
                if zA[v] or zB[v]:
                    t = float(np.clip((y - ny) / max((hy - 0.2 * L) - ny, 1e-6), 0, 1))
                    t = t * t * (3 - 2 * t)  # smoothstep across the neck
                    keep = {}
                    okm = headmask[v] if zA[v] else allowBm[v]
                    for k in range(4):
                        if okm[k] and W[v, k] > 0:
                            keep[int(J[v, k])] = keep.get(int(J[v, k]), 0) + W[v, k]
                    lost = 1.0 - sum(keep.values())
                    tgt_head = hi
                    if jaw is not None and np.linalg.norm(P[v] - bp[jaw]) < np.linalg.norm(P[v] - bp[hi]) and y < hy:
                        tgt_head = jaw
                    keep[tgt_head] = keep.get(tgt_head, 0) + max(lost, 0) * t
                    keep[nk] = keep.get(nk, 0) + max(lost, 0) * (1 - t) * (0 if zA[v] else 1)
                    if zA[v]:
                        keep[tgt_head] += max(lost, 0) * (1 - t)
                else:
                    keep = {int(J[v, k]): W[v, k] for k in range(4) if W[v, k] > 0}
                    if not keep: keep = {nk: 1.0}
                items = sorted(keep.items(), key=lambda kv: -kv[1])[:4]
                tot = sum(w for _, w in items) or 1
                NJ[v] = 0; NW[v] = 0
                for k, (j, w) in enumerate(items):
                    NJ[v, k] = j; NW[v, k] = w / tot
            # zero-weight verts outside the head: bind to nearest bone
            for v in np.nonzero(NW.sum(1) < 1e-6)[0]:
                NJ[v] = 0; NW[v] = 0
                NJ[v, 0] = int(np.argmin(np.linalg.norm(bp - P[v], axis=1))); NW[v, 0] = 1
            glb.encode_into(prim['attributes']['JOINTS_0'], NJ)
            glb.encode_into(prim['attributes']['WEIGHTS_0'], NW)
            rec['fixed'] = True
        out.append(rec)
    return out


def main(a):
    if a[0] == 'audit':
        files = [x for x in a[1:] if x.endswith('.glb')]
        jout = a[a.index('--json') + 1] if '--json' in a else None
        rep, failed = {}, 0
        for f in files:
            try:
                r = analyse(Glb(f))
            except Exception as e:  # noqa
                r = [{'error': f'{type(e).__name__}: {e}'}]
            rep[f] = r
            n = sum(x.get('face_cone', 0) for x in r)
            err = any('error' in x for x in r)
            failed += (n > 0) or err
            if err: print('ERROR', r[0]['error'], f)
            print(f"{'FAIL' if n else 'ok  '} {n:7d} face-cone verts  {f}")
        if jout:
            json.dump(rep, open(jout, 'w'), indent=1)
        print(f"{failed}/{len(files)} files with face-cone weights")
        return 1 if failed else 0
    if a[0] == 'fix':
        glb = Glb(a[1]); r = analyse(glb, fix=True); glb.save(a[2])
        print(json.dumps(r)); return 0
    print(__doc__); return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
