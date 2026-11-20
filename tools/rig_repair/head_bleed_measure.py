#!/usr/bin/env python3
"""Measure head-region skin-weight bleed in a GLB (v2).

Definitions (bind pose, per skinned primitive, pooled):
  chain  = Head joint + its node descendants (they inherit Head's motion and
           move rigidly with it when the game drives Head)
  Neck   = Head's parent joint (the anatomical transition; driven == chest
           in the banks, so Neck weight shears on genuine head turns but is
           a legitimate blend at the jaw/neck junction)
  R10    = verts with chain weight >= 0.10 (the head assembly's region)
Over R10, report:
  mean_chainw   mean weight on the head chain (rigid-with-head fraction)
  mean_neckw    mean Neck weight
  drag_hard     mean weight on canonical driven bones outside chain+Neck
                (shoulders/spine/arms/... — dragged by body motion in match)
  drag_soft     mean weight on AUX rig joints outside chain+Neck
                (ADR_/PMP_/ATH_ muscle/driver/twist/null — inert in game)
  max_headw     max single Head weight in the region (audit anchor: 0.48)
  soft_frac     fraction of R10 with chainw < 0.90
  worst         top non-chain joints by total share of the drag
Severity order: drag_hard + drag_soft (desc), then mean_neckw.

Usage: head_bleed_measure.py <file.glb> -> one JSON object on stdout
"""
import json, sys, os
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ingest import GLBDoc
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from headpick import pick_head

AUX_HINTS = ('adr_', 'pmp_', 'ath_', '_mus', '_drv', '_twt', '_bnd', 'null',
             '_aim_', '_plv_', '_scale_', 'twist')

def is_aux(name):
    n = name.lower()
    return any(h in n for h in AUX_HINTS)

def measure(path):
    out = {'path': path, 'ok': False}
    try:
        doc = GLBDoc(path)
    except Exception as e:
        out['error'] = f'parse: {type(e).__name__}: {e}'
        return out
    j = doc.json
    out['extensions'] = j.get('extensionsUsed', [])
    out['size'] = os.path.getsize(path)
    nodes = j['nodes']
    children, parent = {}, {}
    for i, nd in enumerate(nodes):
        for c in nd.get('children', []):
            children.setdefault(i, []).append(c)
            parent[c] = i
    def descendants(ni):
        res, stack = [], list(children.get(ni, []))
        while stack:
            c = stack.pop()
            res.append(c)
            stack += children.get(c, [])
        return res
    skins = j.get('skins', [])
    if not skins:
        out['error'] = 'no skins'
        return out
    agg = dict(r10=0, chain=0.0, neck=0.0, hard=0.0, soft=0.0,
               max_headw=0.0, soft_frac_n=0, verts=0, any_chain=0)
    drag_joints = {}
    head_names, neck_names = set(), set()
    has_joints1 = False
    n_joints_total = 0
    for mi, m in enumerate(j.get('meshes', [])):
        skin_idx = 0
        for nd in nodes:
            if nd.get('mesh') == mi:
                skin_idx = nd.get('skin', 0)
                break
        if skin_idx >= len(skins):
            continue
        sk = skins[skin_idx]
        joint_nodes = sk['joints']
        n_joints_total = max(n_joints_total, len(joint_nodes))
        jname = {ji: (nodes[n].get('name') or f'j{n}') for ji, n in enumerate(joint_nodes)}
        node2joint = {n: ji for ji, n in enumerate(joint_nodes)}
        prim_JW = []
        for pr in m['primitives']:
            at = pr['attributes']
            if 'JOINTS_0' not in at:
                continue
            if 'JOINTS_1' in at:
                has_joints1 = True
            prim_JW.append((doc.accessor(at['JOINTS_0']).astype(np.int64),
                            doc.accessor(at['WEIGHTS_0']).astype(np.float64)))
        hj, chain = pick_head(jname, joint_nodes,
                              descendants, node2joint, prim_JW)
        if hj is None:
            continue
        head_node = joint_nodes[hj]
        head_names.add(jname[hj])
        neck_ji = None
        pn = parent.get(head_node)
        if pn is not None and pn in node2joint:
            neck_ji = node2joint[pn]
            neck_names.add(jname[neck_ji])
        aux_cache = {ji: is_aux(nm) for ji, nm in jname.items()}
        for J, W in prim_JW:
            n = len(W)
            agg['verts'] += n
            chainw = np.where(np.isin(J, list(chain)), W, 0.0).sum(axis=1)
            headw = np.where(J == hj, W, 0.0).sum(axis=1)
            neckw = (np.where(J == neck_ji, W, 0.0).sum(axis=1)
                     if neck_ji is not None else np.zeros(n))
            agg['any_chain'] += int((chainw > 0).sum())
            r10 = chainw >= 0.10
            if r10.sum() == 0:
                continue
            subJ, subW = J[r10], W[r10]
            agg['r10'] += int(r10.sum())
            agg['chain'] += float(chainw[r10].sum())
            agg['neck'] += float(neckw[r10].sum())
            agg['max_headw'] = max(agg['max_headw'], float(headw[r10].max()))
            agg['soft_frac_n'] += int((chainw[r10] < 0.90).sum())
            # drag split per joint
            dragmask = ~np.isin(subJ, list(chain)) & (subJ != neck_ji if neck_ji is not None else True)
            flatJ, flatW = subJ[dragmask], subW[dragmask]
            if len(flatJ):
                for ju in np.unique(flatJ):
                    s = float(flatW[flatJ == ju].sum())
                    nm = jname[int(ju)]
                    drag_joints[nm] = drag_joints.get(nm, 0.0) + s
                    if aux_cache[int(ju)]:
                        agg['soft'] += s
                    else:
                        agg['hard'] += s
    if agg['r10'] == 0:
        out['error'] = 'no head-region verts (chainw>=0.10)'
        out['head_names'] = sorted(head_names)
        return out
    r = agg['r10']
    out.update(
        ok=True, head_names=sorted(head_names), neck_names=sorted(neck_names),
        n_joints=n_joints_total, has_joints1=has_joints1,
        verts=agg['verts'], r10=r, any_chain=agg['any_chain'],
        mean_chainw=agg['chain'] / r, mean_neckw=agg['neck'] / r,
        max_headw=agg['max_headw'], soft_frac=agg['soft_frac_n'] / r,
        drag_hard=agg['hard'] / r, drag_soft=agg['soft'] / r,
        drag_total=(agg['hard'] + agg['soft']) / r,
    )
    if drag_joints:
        tot = sum(drag_joints.values())
        if tot > 0:
            top = sorted(drag_joints.items(), key=lambda x: -x[1])[:5]
            out['worst_drag_joints'] = [(nm, round(v / tot, 3)) for nm, v in top]
        else:
            out['worst_drag_joints'] = []
    return out

if __name__ == '__main__':
    print(json.dumps(measure(sys.argv[1])))
