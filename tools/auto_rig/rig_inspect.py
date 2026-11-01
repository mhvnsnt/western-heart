#!/usr/bin/env python3
"""tools/auto_rig/rig_inspect.py — look inside a rig: joint fits, mesh sections, skin-weight maps, real stretch.

The diagnostics behind the Negativo re-rig (2026-10-31), kept so any agent can re-run them on any fighter:

  fit       mesh point cloud (front + side) with one or two refit_skeleton/refit_landmarks fit JSONs drawn on it
            (red = first, blue = second). Shows joints sitting in hair, arms above the real arms, hips in the belly.
  sections  thin slabs through the mesh (mid-sagittal + two coronal) with the fit's joints: throat, chin, crotch,
            armpits are measured from these.
  weights   skinned GLB: every vertex coloured by its dominant bone group (Head/Neck/Spine/Clav/Arm/Leg) front +
            side, plus the Head weight along the mid-line. Shows faces on chest bones, bellies on thigh bones.
  shares    skinned GLB: weight share per bone inside named body regions (face, chin, neck, arms, chest, ...),
            using the GLB's own joint positions (regions are relative to Head/Neck/Spine2/Arm joints).
  seams     skinned GLB: do the copies of every UV-seam vertex (same position) carry the same weights? If not, the
            seam opens into a crack under animation; no edge-stretch metric can see it (no triangle edge spans a
            seam). smooth_weights.py left 6,688 such copies on Negativo (2026-11-01).
  stretch   skinned GLB with an embedded clip: per-edge stretch with smooth_weights.py's own edge filter (keeps
            the dense-mesh edges anim_check.py's 0.5%-of-height filter drops), plus the ABSOLUTE elongation in mm
            and where the stretched edges sit (dominant-bone pairs, height bands). Ratio alone on a 1M-vertex
            mesh flags sub-millimetre noise; the mm numbers say whether a tear is visible.

usage:
  python3 tools/auto_rig/rig_inspect.py fit      --fit A.json [--fit2 B.json] --out fit.png
  python3 tools/auto_rig/rig_inspect.py sections --fit A.json --out sections.png
  python3 tools/auto_rig/rig_inspect.py weights  --glb RIG.glb --out weights.png [--min-y 0.3]
  python3 tools/auto_rig/rig_inspect.py shares   --glb RIG.glb
  python3 tools/auto_rig/rig_inspect.py seams    --glb RIG.glb
  python3 tools/auto_rig/rig_inspect.py stretch  --glb RIG_WITH_CLIP.glb [--frames 10]
Plain glTF (decode meshopt first). The plotting modes need matplotlib (pip install matplotlib).
"""
import argparse
import collections
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, 'backends'))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(HERE)), 'tools', 'model-audit'))

GROUPS = (('Head', ('Head',)), ('Neck', ('Neck',)), ('Spine', ('Spine', 'Hips')),
          ('Clav', ('LeftShoulder', 'RightShoulder')),
          ('Arm', ('LeftArm', 'RightArm', 'LeftFore', 'RightFore', 'LeftHand', 'RightHand')),
          ('Leg', ('LeftUp', 'RightUp', 'LeftLeg', 'RightLeg', 'LeftFoot', 'RightFoot', 'LeftToe', 'RightToe')))
COLORS = {'Head': '#d62728', 'Neck': '#ff7f0e', 'Spine': '#1f77b4', 'Clav': '#2ca02c', 'Arm': '#9467bd',
          'Leg': '#8c564b', 'other': '#7f7f7f'}


def _plt():
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        return plt
    except ImportError:
        raise SystemExit('this mode needs matplotlib: pip install matplotlib')


def load_skinned(path):
    """(positions, JOINTS_0, WEIGHTS_0, triangle indices, joint names, joint bind positions) of the first skinned
    primitive, positions in the mesh's bind space."""
    import rig_qa
    js, blob = rig_qa.read_glb(path)
    nd = next(n for n in js['nodes'] if 'mesh' in n and n.get('skin') is not None)
    sk = js['skins'][nd['skin']]
    names = [js['nodes'][j].get('name', '') for j in sk['joints']]
    pr = next(p for p in js['meshes'][nd['mesh']]['primitives'] if 'JOINTS_0' in p['attributes'])
    at = pr['attributes']
    P = rig_qa.accessor(js, blob, at['POSITION']).astype(np.float64)
    Jn = rig_qa.accessor(js, blob, at['JOINTS_0']).astype(int)
    W = rig_qa.accessor(js, blob, at['WEIGHTS_0']).astype(np.float64)
    T = rig_qa.accessor(js, blob, pr['indices']).reshape(-1, 3).astype(np.int64) if 'indices' in pr else None
    ibm = rig_qa.accessor(js, blob, sk['inverseBindMatrices']).reshape(-1, 4, 4).transpose(0, 2, 1)
    jp = {n: np.linalg.inv(m)[:3, 3] for n, m in zip(names, ibm)}
    return P, Jn, W, T, names, jp


def dominant_groups(Jn, W, names):
    dom = np.array(names, dtype=object)[Jn[np.arange(len(Jn)), W.argmax(1)]].astype(str)
    grp = np.full(len(dom), 'other', dtype=object)
    for g, prefixes in GROUPS:
        for p in prefixes:
            grp[np.char.startswith(dom, p)] = g
    return dom, grp


def bone_weight(Jn, W, names, bone):
    return (W * (Jn == names.index(bone))).sum(1) if bone in names else np.zeros(len(W))


def cmd_fit(a):
    from refit_landmarks import mesh_in_fit_space
    plt = _plt()
    fits = [json.load(open(a.fit))] + ([json.load(open(a.fit2))] if a.fit2 else [])
    Q = mesh_in_fit_space(fits[0])
    q = Q[np.random.default_rng(0).choice(len(Q), min(len(Q), 250000), replace=False)]
    fig, ax = plt.subplots(1, 2, figsize=(16, 9))
    for axi, (i, j, t) in zip(ax, [(0, 1, 'front (x,y)'), (2, 1, 'side (z,y)')]):
        axi.scatter(q[:, i], q[:, j], s=0.05, c='#999', alpha=0.3)
        for fit, col in zip(fits, ('r', 'b')):
            J = {k['name']: k for k in fit['joints']}
            for k in fit['joints']:
                n = k['name']
                if k['parent'] in J and not (n.startswith(('LeftHand', 'RightHand')) and n not in ('LeftHand', 'RightHand')):
                    p, c = J[k['parent']]['pos'], k['pos']
                    axi.plot([p[i], c[i]], [p[j], c[j]], col + '-', lw=1.5)
                    axi.plot([c[i]], [c[j]], col + 'o', ms=3)
        axi.set_aspect('equal')
        axi.set_title(t + ('  red = %s, blue = %s' % (os.path.basename(a.fit), os.path.basename(a.fit2)) if a.fit2 else ''))
        axi.grid(alpha=.3)
    plt.tight_layout()
    plt.savefig(a.out, dpi=80)
    print('wrote', a.out)


def cmd_sections(a):
    from refit_landmarks import mesh_in_fit_space
    plt = _plt()
    fit = json.load(open(a.fit))
    Q = mesh_in_fit_space(fit)
    J = {k['name']: k['pos'] for k in fit['joints']}
    H = fit.get('height_m') or float(Q[:, 1].max())
    cx = J['Hips'][0]
    zc = J['Spine1'][2]
    slabs = [('mid-sagittal |x|<0.01H (z,y)', np.abs(Q[:, 0] - cx) < 0.01 * H, 2),
             ('coronal z in Spine1.z +-0.02H (x,y)', np.abs(Q[:, 2] - zc) < 0.02 * H, 0),
             ('coronal z in Spine1.z-0.07H +-0.02H (x,y)', np.abs(Q[:, 2] - (zc - 0.07 * H)) < 0.02 * H, 0)]
    fig, ax = plt.subplots(1, 3, figsize=(24, 10))
    for axi, (t, m, i) in zip(ax, slabs):
        axi.scatter(Q[m, i], Q[m, 1], s=0.2, c='k')
        for n, p in J.items():
            if n.startswith(('LeftHand', 'RightHand')) and n not in ('LeftHand', 'RightHand'):
                continue
            axi.plot(p[i], p[1], 'ro', ms=4)
            axi.annotate(n, (p[i], p[1]), fontsize=6, color='r')
        axi.set_title(t)
        axi.set_aspect('equal')
        axi.grid(alpha=.4)
    plt.tight_layout()
    plt.savefig(a.out, dpi=60)
    print('wrote', a.out)


def cmd_weights(a):
    plt = _plt()
    P, Jn, W, _, names, jp = load_skinned(a.glb)
    _, grp = dominant_groups(Jn, W, names)
    hw = bone_weight(Jn, W, names, 'Head')
    idx = np.nonzero(P[:, 1] > a.min_y)[0]
    idx = np.random.default_rng(0).choice(idx, min(len(idx), 200000), replace=False)
    fig, ax = plt.subplots(1, 3, figsize=(24, 9))
    for axi, (i, t) in zip(ax[:2], [(0, 'front x,y'), (2, 'side z,y')]):
        for g, c in COLORS.items():
            k = idx[grp[idx] == g]
            axi.scatter(P[k, i], P[k, 1], s=0.08, c=c, label=g)
        axi.set_aspect('equal')
        axi.set_title('dominant bone ' + t)
        axi.grid(alpha=.3)
        axi.legend(markerscale=40, loc='lower left')
    cx = jp['Hips'][0] if 'Hips' in jp else 0.0
    k = idx[np.abs(P[idx, 0] - cx) < 0.012 * (P[:, 1].max() - P[:, 1].min())]
    sc = ax[2].scatter(P[k, 2], P[k, 1], s=1, c=hw[k], cmap='viridis', vmin=0, vmax=1)
    ax[2].set_aspect('equal')
    ax[2].set_title('Head weight along the mid-line')
    plt.colorbar(sc, ax=ax[2])
    plt.tight_layout()
    plt.savefig(a.out, dpi=70)
    print('wrote', a.out)


def cmd_shares(a):
    P, Jn, W, _, names, jp = load_skinned(a.glb)
    x, y, z = P[:, 0], P[:, 1], P[:, 2]
    hy, ny, s2 = jp['Head'][1], jp['Neck'][1], jp['Spine2'][1]
    hz = jp['Head'][2]
    lax, rax = jp['LeftArm'][0], jp['RightArm'][0]
    lfx, lhx = jp['LeftForeArm'][0], jp['LeftHand'][0]
    ya = jp['LeftArm'][1]
    H = y.max() - y.min()
    regions = [
        ('head + hair above the Head joint', (y > hy)),
        ('face (front of head)', (y > hy) & (y < hy + 0.15 * H) & (z > hz + 0.04 * H) & (np.abs(x) < 0.08 * H)),
        ('chin / jaw underside', (y > hy - 0.015 * H) & (y < hy) & (z > hz + 0.03 * H)),
        ('neck', (y > ny - 0.01 * H) & (y < hy) & (np.abs(x) < 0.05 * H)),
        ('chest front', (y > s2 - 0.05 * H) & (y < ya) & (np.abs(x) < 0.08 * H) & (z > jp['Spine2'][2] + 0.02 * H)),
        ('L upper arm', (x > lax + 0.01 * H) & (x < lfx) & (np.abs(y - ya) < 0.06 * H)),
        ('L forearm', (x > lfx) & (x < lhx) & (np.abs(y - ya) < 0.06 * H)),
        ('R upper arm', (x < rax - 0.01 * H) & (x > jp['RightForeArm'][0]) & (np.abs(y - ya) < 0.06 * H)),
        ('abdomen (Hips..Spine1)', (y > jp['Hips'][1]) & (y < jp['Spine1'][1]) & (np.abs(x) < 0.06 * H)),
    ]
    for label, m in regions:
        acc = np.zeros(len(names))
        np.add.at(acc, Jn[m].ravel(), W[m].ravel())
        acc /= max(acc.sum(), 1e-9)
        top = np.argsort(-acc)[:6]
        print('%-34s n=%8d  %s' % (label, m.sum(), '  '.join('%s %.1f%%' % (names[i], 100 * acc[i]) for i in top if acc[i] > 0.005)))


def cmd_seams(a):
    P, Jn, W, _, names, _ = load_skinned(a.glb)
    key = np.round(P / 1e-6).astype(np.int64)
    _, first, inv, cnt = np.unique(key, axis=0, return_index=True, return_inverse=True, return_counts=True)
    inv = inv.reshape(-1)
    D = np.zeros((len(P), len(names)), np.float32)
    np.add.at(D, (np.repeat(np.arange(len(P)), 4), Jn.ravel()), W.ravel())
    diff = np.abs(D - D[first[inv]]).sum(1)
    out = {'glb': a.glb, 'seam_copy_verts': int((cnt[inv] > 1).sum()),
           'copies_disagreeing_over_0.01': int((diff > 0.01).sum()), 'copies_disagreeing_over_0.1': int((diff > 0.1).sum()),
           'max_l1_disagreement': round(float(diff.max()), 4)}
    out['pass'] = out['copies_disagreeing_over_0.01'] == 0
    print(json.dumps(out, indent=1))
    return out


def cmd_stretch(a):
    import anim_check as ac
    from smooth_weights import _skin_fast, prim_edges
    m = ac.AnimModel(a.glb)
    if not m.js.get('animations'):
        raise SystemExit('no embedded clip: bake one (heat_rebind.py --donor ...) before measuring stretch')
    jidx = np.array(m.joint_nodes)
    bind = m.bind_world()
    pr = m.prims[0]
    ph = np.c_[pr['pos'], np.ones(len(pr['pos']))]
    E = prim_edges(pr)
    bs = np.stack([bind[int(j)] @ m.ibm[k] for k, j in enumerate(jidx)])
    r0 = _skin_fast(bs, pr, ph)
    rl = np.linalg.norm(r0[E[:, 0]] - r0[E[:, 1]], axis=1)
    cut = min(0.0098, 0.5 * float(np.median(rl)))       # smooth_weights.evaluate's filter
    keep = rl >= cut
    E, rl = E[keep], rl[keep]
    mr, ma = np.zeros(len(E)), np.zeros(len(E))
    for an in m.js['animations']:
        times, chans = m.animation_frames(an, a.frames)
        for t in times:
            w = m.eval_world(chans, t)
            c = _skin_fast(np.stack([w[int(j)] @ m.ibm[k] for k, j in enumerate(jidx)]), pr, ph)
            el = np.linalg.norm(c[E[:, 0]] - c[E[:, 1]], axis=1)
            mr = np.maximum(mr, el / rl)
            ma = np.maximum(ma, el - rl)
    names = [m.nodes[j].get('name', '') for j in m.joint_nodes]
    J, W, P = pr['joints'], pr['weights'], pr['pos']
    dom = np.array(names, dtype=object)[J[np.arange(len(P)), W.argmax(1)]]
    b = mr > 2
    out = {'glb': a.glb, 'edges_measured': int(len(E)), 'edge_cutoff_mm': round(1000 * cut, 3),
           'median_rest_edge_mm': round(1000 * float(np.median(rl)), 3),
           'stretch_p999': round(float(np.percentile(mr, 99.9)), 3), 'stretch_max': round(float(mr.max()), 3),
           'edges_over_2x': int(b.sum()), 'edges_over_4x': int((mr > 4).sum()),
           'elongation_mm': {'median_of_over_2x': round(1000 * float(np.median(ma[b])), 2) if b.any() else 0,
                             'p90_of_over_2x': round(1000 * float(np.percentile(ma[b], 90)), 2) if b.any() else 0,
                             'max': round(1000 * float(ma.max()), 2)},
           'edges_elongated_over_mm': {str(t): int((ma > t / 1000).sum()) for t in (2, 5, 10, 20)},
           'over_2x_by_dominant_bones': dict(collections.Counter(
               ' | '.join(sorted((dom[p], dom[q]))) for p, q in E[b]).most_common(14))}
    mid = (P[E[b, 0]] + P[E[b, 1]]) / 2
    ys = np.linspace(P[:, 1].min(), P[:, 1].max(), 6)
    out['over_2x_by_height'] = {'%.2f-%.2f' % (lo, hi): int(((mid[:, 1] >= lo) & (mid[:, 1] < hi)).sum())
                                for lo, hi in zip(ys[:-1], ys[1:])}
    print(json.dumps(out, indent=1))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    sub = ap.add_subparsers(dest='mode', required=True)
    p = sub.add_parser('fit'); p.add_argument('--fit', required=True); p.add_argument('--fit2'); p.add_argument('--out', required=True)
    p = sub.add_parser('sections'); p.add_argument('--fit', required=True); p.add_argument('--out', required=True)
    p = sub.add_parser('weights'); p.add_argument('--glb', required=True); p.add_argument('--out', required=True)
    p.add_argument('--min-y', type=float, default=0.3)
    p = sub.add_parser('shares'); p.add_argument('--glb', required=True)
    p = sub.add_parser('seams'); p.add_argument('--glb', required=True)
    p = sub.add_parser('stretch'); p.add_argument('--glb', required=True); p.add_argument('--frames', type=int, default=10)
    a = ap.parse_args()
    {'fit': cmd_fit, 'sections': cmd_sections, 'weights': cmd_weights, 'shares': cmd_shares, 'seams': cmd_seams,
     'stretch': cmd_stretch}[a.mode](a)


if __name__ == '__main__':
    main()
