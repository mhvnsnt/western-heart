#!/usr/bin/env python3
"""tools/auto_rig/head_territory.py — head + hair ride the Head bone rigidly, the neck rides the Neck bone.

Owner 2026-10-31 (Negativo): "head and neck all like waited down towards his pelvis his f****** face is stretch like
in a cone" / "hair bursting through their face". After a landmark re-fit (refit_landmarks.py) + bone heat, the face
is already ~97% Head, but bone heat still (a) splits hair that hangs down to the shoulders between Head and the
clavicles, so any shoulder roll drags the hair through the head, and (b) gives the short Neck bone almost nothing,
so the neck skin follows the clavicles / chest instead of the neck.

A height cut ("everything above the neck joint -> Head", fix_sternum_weights.py --head) tears hair spikes that hang
below the neck (measured A/B 2026-10-31). This tool uses mesh connectivity instead:

  1. weld UV-seam duplicates by position, so the flood fill crosses seams;
  2. barrier vertices (the fill never enters them):
       neck   : below the Head joint, within neck_r of the Neck->Head axis; neck_r = 1.15 x half the throat's
                front-to-back depth at mid-neck height (the neck's own surface, not hair around it);
       arms   : within --arm-r x upper-arm length of either clavicle or upper-arm bone;
       torso  : below the Neck joint and in front of the back plane (the mid-line back surface, front_back()
                of refit_landmarks.py, minus 0.01 H) - hair hangs behind the back, skin is in front of it;
  3. head territory = every connected piece of the non-barrier mesh that holds a vertex above the Head joint;
     territory -> Head 1.0, faded in by GEODESIC distance (Dijkstra over mesh edges) from where the territory
     touches the arm/torso barriers: smoothstep(0, --band x H, d). Hair fused onto the shoulders keeps its bone
     heat weights at the contact and becomes rigid Head a band away (a hard Head 1.0 there tore 2,157 edges by
     > 20 mm, up to 127 mm, on Negativo's boxing gate clip; measured 2026-10-31). The neck side is not faded:
     it continues into the neck blend below, so the jaw stays on the head;
  4. neck: neck-cylinder vertices between Spine2 and Head heights -> Neck blended into Head over Neck->Head
     (smoothstep), faded in from the vertex's own weights over the half of Spine2->Neck just under the Neck joint
     (and, there only, radially over the outer quarter of the cylinder: torso lies outside it);
  5. every vertex keeps its 4 largest influences, renormalized, written back into the same accessors
     (every other byte, incl. an embedded gate clip, unchanged).
Then run backends/smooth_weights.py (stretch-driven seam smoothing) and anim_check.py (the gate).

usage: python3 tools/auto_rig/head_territory.py --in RIG.glb --out RIG-territory.glb [--report R.json] [--band 0.08]
       plain glTF in (decode meshopt first), canonical joint names (Hips/Spine2/Neck/Head/Left|RightShoulder/...).
"""
import argparse
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fix_sternum_weights import read_glb, write_glb, view, smoothstep  # noqa: E402


def joint_positions(js, binarr, skin):
    ibm, _ = view(js, binarr, skin['inverseBindMatrices'])
    M = np.asarray(ibm, dtype=np.float64).reshape(-1, 4, 4).transpose(0, 2, 1)
    names = [js['nodes'][j].get('name', '') for j in skin['joints']]
    return names, {n: np.linalg.inv(m)[:3, 3] for n, m in zip(names, M)}


def seg_dist(P, A, B):
    d = B - A
    t = np.clip(((P - A) @ d) / max(float(d @ d), 1e-12), 0, 1)
    return np.linalg.norm(P - (A + t[:, None] * d), axis=1)


def territory(P, tris, jp, H, arm_r_frac=0.35, band_m=0.08):
    """Boolean head territory + barrier diagnostics, on the welded mesh."""
    from scipy.sparse import coo_matrix
    from scipy.sparse.csgraph import connected_components
    key = np.round(P / 1e-6).astype(np.int64)
    _, weld_first, inv = np.unique(key, axis=0, return_index=True, return_inverse=True)
    inv = inv.reshape(-1)
    Pw = P[weld_first]
    nw = len(Pw)
    Tw = inv[tris]
    head, neck, s2 = jp['Head'], jp['Neck'], jp['Spine2']
    # neck axis (x, z) as a function of y: Neck joint below, Head joint above
    t = np.clip((Pw[:, 1] - neck[1]) / max(head[1] - neck[1], 1e-6), 0, 1)
    ax = neck[[0, 2]][None, :] * (1 - t[:, None]) + head[[0, 2]][None, :] * t[:, None]
    dh = np.linalg.norm(Pw[:, [0, 2]] - ax, axis=1)
    # neck radius from the throat: half the front-to-back depth of the mid-line slab at mid-neck height (the
    # front surface and the next surface behind it, as refit_landmarks.front_back); hair around the neck makes
    # any all-around percentile too wide (Negativo: 0.074 m, which swallowed the chin)
    y_mid = (neck[1] + head[1]) / 2
    zm = np.sort(Pw[(np.abs(Pw[:, 0] - neck[0]) < 0.012 * H) & (np.abs(Pw[:, 1] - y_mid) < 0.0015 * H), 2])[::-1]
    gm = np.nonzero(-np.diff(zm) > 0.012 * H)[0] if len(zm) > 6 else []
    if len(gm):
        neck_r = 1.15 * (zm[0] - zm[gm[0] + 1]) / 2
    else:
        ring = np.abs(Pw[:, 1] - y_mid) < 0.004 * H
        neck_r = 1.15 * float(np.percentile(dh[ring], 20)) if ring.sum() > 10 else 0.05 * H
    # anatomical clamp (2026-11-01): hair or a collar around the throat makes the slab read the hair mass as neck
    # (Phantom: 0.32 m = 18% of his height, so the Neck -> Head blend spread over his shoulders and chest). Clamp to
    # 2-6% of standing height (Negativo's passing refits measured 5.0-5.3%: unchanged)
    neck_r = float(np.clip(neck_r, 0.02 * H, 0.06 * H))
    b_neck = (Pw[:, 1] < head[1]) & (dh < neck_r)
    arm_len = np.mean([np.linalg.norm(jp[s + 'ForeArm'] - jp[s + 'Arm']) for s in ('Left', 'Right')])
    arm_r = arm_r_frac * arm_len
    limb = np.min([seg_dist(Pw, jp[s + a], jp[s + b]) for s in ('Left', 'Right')
                   for a, b in (('Shoulder', 'Arm'), ('Arm', 'ForeArm'))], axis=0)
    b_arm = limb < arm_r
    # back plane at the mid-line (refit_landmarks.front_back) between Spine2 and Neck heights
    mid = np.abs(Pw[:, 0] - neck[0]) < 0.012 * H
    z_back = []
    for y in np.linspace(s2[1], neck[1], 8):
        z = np.sort(Pw[mid & (np.abs(Pw[:, 1] - y) < 0.0015 * H), 2])[::-1]
        g = np.nonzero(-np.diff(z) > 0.012 * H)[0] if len(z) > 6 else []
        if len(g):
            z_back.append((y, z[g[0] + 1]))
    if z_back:
        zb = np.interp(Pw[:, 1], [y for y, _ in z_back], [z for _, z in z_back])
        b_torso = (Pw[:, 1] < neck[1]) & (Pw[:, 2] > zb - 0.01 * H)
    else:
        b_torso = Pw[:, 1] < neck[1]
    b_torso |= Pw[:, 1] < s2[1]
    blocked = b_neck | b_arm | b_torso
    ok = ~blocked
    e = np.concatenate([Tw[:, [0, 1]], Tw[:, [1, 2]], Tw[:, [2, 0]]])
    e = e[ok[e[:, 0]] & ok[e[:, 1]]]
    A = coo_matrix((np.ones(len(e), dtype=np.int8), (e[:, 0], e[:, 1])), shape=(nw, nw))
    _, lab = connected_components(A, directed=False)
    seeds = ok & (Pw[:, 1] > head[1])
    terr_w = ok & np.isin(lab, np.unique(lab[seeds]))
    # geodesic distance inside the territory from its contact with the arm / torso barriers (not the neck)
    from scipy.sparse.csgraph import dijkstra
    eu = np.unique(np.sort(np.concatenate([Tw[:, [0, 1]], Tw[:, [1, 2]], Tw[:, [2, 0]]]), 1), axis=0)
    eu = eu[eu[:, 0] != eu[:, 1]]
    hard = (b_arm | b_torso) & ~terr_w
    touch = (terr_w[eu[:, 0]] & hard[eu[:, 1]]) | (terr_w[eu[:, 1]] & hard[eu[:, 0]])
    src = np.unique(np.where(terr_w[eu[touch, 0]], eu[touch, 0], eu[touch, 1]))
    inside = eu[terr_w[eu[:, 0]] & terr_w[eu[:, 1]]]
    ln = np.linalg.norm(Pw[inside[:, 0]] - Pw[inside[:, 1]], axis=1) + 1e-9
    G = coo_matrix((ln, (inside[:, 0], inside[:, 1])), shape=(nw, nw)).tocsr()
    geo = np.full(nw, np.inf)
    if len(src):
        geo = dijkstra(G, directed=False, indices=src, min_only=True, limit=band_m)
    diag = {'neck_r_m': round(neck_r, 4), 'arm_r_m': round(float(arm_r), 4), 'welded_verts': int(nw),
            'barrier': {'neck': int(b_neck.sum()), 'arm': int(b_arm.sum()), 'torso': int(b_torso.sum())},
            'back_plane_samples': len(z_back), 'seeds': int(seeds.sum()),
            'territory_welded': int(terr_w.sum()),
            'territory_below_neck_joint': int((terr_w & (Pw[:, 1] < neck[1])).sum()),
            'territory_lowest_y': round(float(Pw[terr_w, 1].min()), 4) if terr_w.any() else None,
            'contact_sources': int(len(src)), 'band_m': round(float(band_m), 4),
            'territory_within_band': int((terr_w & np.isfinite(geo)).sum())}
    return terr_w[inv], dh[inv], geo[inv], neck_r, diag


def apply(inp, outp, report=None, arm_r=0.35, band=0.08):
    """All skinned primitives are processed as ONE mesh (2026-11-01): multi-part exports (Awa Pop: 31 parts) were
    handled part by part, each with its own height and connectivity, so a 54-vertex part decided the head territory.
    Positions of skinned primitives share the skeleton's bind space, so they merge directly; every part's slice of
    the result is written back to its own accessors."""
    js, binarr = read_glb(inp)
    out = {'input': inp, 'tool': 'tools/auto_rig/head_territory.py'}
    parts, skin_i = [], None
    seen = set()
    for nd in js['nodes']:
        if 'mesh' not in nd or nd.get('skin') is None:
            continue
        if skin_i is None:
            skin_i = nd['skin']
        elif nd['skin'] != skin_i:
            raise SystemExit('more than one skin: head_territory expects one skeleton')
        for pi, prim in enumerate(js['meshes'][nd['mesh']]['primitives']):
            at = prim['attributes']
            if (nd['mesh'], pi) in seen or 'JOINTS_0' not in at:
                continue
            seen.add((nd['mesh'], pi))
            Jv, _ = view(js, binarr, at['JOINTS_0'])
            Wv, wacc = view(js, binarr, at['WEIGHTS_0'])
            if wacc['componentType'] != 5126:
                raise SystemExit('WEIGHTS_0 must be float (got componentType %d)' % wacc['componentType'])
            P = np.asarray(view(js, binarr, at['POSITION'])[0], dtype=np.float64)
            T = (np.asarray(view(js, binarr, prim['indices'])[0]).reshape(-1, 3).astype(np.int64) if 'indices' in prim
                 else np.arange(len(P)).reshape(-1, 3))
            parts.append({'mesh': nd['mesh'], 'primitive': pi, 'P': P, 'T': T, 'Jv': Jv, 'Wv': Wv})
    if not parts:
        raise SystemExit('no skinned primitive')
    skin = js['skins'][skin_i]
    names, jp = joint_positions(js, binarr, skin)
    need = ['Head', 'Neck', 'Spine2', 'LeftShoulder', 'RightShoulder', 'LeftArm', 'RightArm', 'LeftForeArm', 'RightForeArm']
    miss = [n for n in need if n not in jp]
    if miss:
        raise SystemExit('missing canonical joints: %s' % miss)
    ih, ink = names.index('Head'), names.index('Neck')
    offs = np.cumsum([0] + [len(q['P']) for q in parts])
    P = np.concatenate([q['P'] for q in parts])
    tris = np.concatenate([q['T'] + o for q, o in zip(parts, offs[:-1])])
    Jn = np.concatenate([np.asarray(q['Jv']).astype(np.int64) for q in parts])
    W = np.concatenate([np.asarray(q['Wv'], dtype=np.float64) for q in parts])
    H = float(P[:, 1].max() - P[:, 1].min())
    terr, dh, geo, neck_r, diag = territory(P, tris, jp, H, arm_r, band * H)
    nb = len(names)
    dense = np.zeros((len(P), nb))
    np.add.at(dense, (np.repeat(np.arange(len(P)), 4), Jn.ravel()), W.ravel())
    before_head = dense[:, ih].copy()
    # 4. neck band
    yn, yh, ys2 = jp['Neck'][1], jp['Head'][1], jp['Spine2'][1]
    neckm = (dh < neck_r) & (P[:, 1] >= yn - 0.5 * (yn - ys2)) & (P[:, 1] < yh) & ~terr
    s = smoothstep(yn, yh, P[neckm, 1])
    yb = P[neckm, 1]
    # fade in under the Neck joint, and radially at the cylinder's rim there (torso outside it); above the
    # Neck joint the outside is the head territory, so no radial fade (it would split chin from throat)
    a = smoothstep(yn - 0.5 * (yn - ys2), yn, yb) * np.where(
        yb < yn, 1 - smoothstep(0.75 * neck_r, neck_r, dh[neckm]), 1.0)
    tgt = np.zeros((neckm.sum(), nb))
    tgt[:, ink] = 1 - s
    tgt[:, ih] = s
    dense[neckm] = (1 - a)[:, None] * dense[neckm] + a[:, None] * tgt
    # 3. territory, faded in from the arm/torso contact
    f = np.where(np.isfinite(geo[terr]), smoothstep(0.0, band * H, geo[terr]), 1.0)
    tgt = np.zeros((terr.sum(), nb))
    tgt[:, ih] = 1
    dense[terr] = (1 - f)[:, None] * dense[terr] + f[:, None] * tgt
    changed = terr | neckm
    # 5. top-4, renormalize, write back to every part's own accessors
    idx = np.argsort(-dense, axis=1)[:, :4]
    w4 = np.take_along_axis(dense, idx, 1)
    w4 /= np.maximum(w4.sum(1, keepdims=True), 1e-12)
    for q, o in zip(parts, offs[:-1]):
        sl = slice(o, o + len(q['P']))
        ch = changed[sl]
        q['Jv'][ch] = idx[sl][ch].astype(q['Jv'].dtype)
        q['Wv'][ch] = w4[sl][ch].astype(q['Wv'].dtype)
    diag.update({'parts': len(parts), 'verts': len(P),
                 'territory_verts': int(terr.sum()), 'neck_band_verts': int(neckm.sum()),
                 'territory_faded_verts': int((terr & np.isfinite(geo)).sum()),
                 'head_weight_mean_in_territory_before': round(float(before_head[terr].mean()), 3) if terr.any() else None,
                 'territory_verts_that_had_head_below_0.5': int((terr & (before_head < 0.5)).sum())})
    out['primitives'] = [diag]
    write_glb(outp, js, binarr)
    if report:
        json.dump(out, open(report, 'w'), indent=1)
    print(json.dumps(out, indent=1))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--in', dest='inp', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--report', default=None)
    ap.add_argument('--arm-r', type=float, default=0.35, help='arm/clavicle barrier radius, x upper-arm length')
    ap.add_argument('--band', type=float, default=0.08, help='geodesic fade from the arm/torso contact, x height')
    a = ap.parse_args()
    apply(a.inp, a.out, a.report, a.arm_r, a.band)


if __name__ == '__main__':
    main()
