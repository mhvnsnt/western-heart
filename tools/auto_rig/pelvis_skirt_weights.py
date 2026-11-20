#!/usr/bin/env python3
"""tools/auto_rig/pelvis_skirt_weights.py — give a body's pelvis, belt and armoured skirt back to the Hips bone.

Why (2026-11-10, Thor): Blender's bone heat weights by distance to each bone SEGMENT. On a stocky Tripo body whose
Hips deform bone is only a few cm long (Thor: Hips 1.092 m -> Spine 1.129 m, 3.7 cm), the long thigh bones win the
whole lower torso: Thor's belly, belt and armoured skirt carry Hips 0-5% and the thighs 50-74%
(docs/proof/2026-11-10/thor-ganryu/pelvis_profile_before.txt). Any wide stance then swings the belt and the skirt
plates rigidly with the thighs; his own sumo stance (Ganryu's T7 kamae) splays them out flat like a tray, and the
front panel tears down the middle, split between the two thighs.

The standard no-extra-bones skirt weighting (what game rigs do for kilts and short skirts when there are no skirt
bones or cloth): the belt rides the pelvis fully and each skirt point follows the thighs PART of the way, more toward
the hem; the thigh share of the centre panels is split evenly between both thighs, so the panel stretches between
the legs instead of tearing. Rule-based and deterministic (the same family as reskin_pantera_weights.py's tail
rule), applied only where the model's own geometry says "outer shell" (far from the thigh bone), so the bare legs
below the hem keep their weights:

  per vertex (bind space, metres, y up), with the thigh bones' own axes (UpLeg -> Leg joints):
    r      = distance from the nearer thigh axis
    shell  = smoothstep(r_leg, r_leg + r_blend, r)                   outer shell (belly / belt / skirt) vs leg
    f(y)   = 1 above --belt-y; smoothstep down to --hem-f at --hem-y; down to 0 by --hem-y - --hem-fade
    moved  = shell * f(y) * (UpLeg.L + UpLeg.R weight)                -> Hips
    the thigh share left: split by side = mix(original split, sigmoid(x / --split-sigma), shell)
  everything else (cape on the shoulders, arms, spine) untouched; top-4 influences kept (continuous cut), renormalized.

Only JOINTS_0 / WEIGHTS_0 change, in place, in a PLAIN (decoded) GLB: run tools/anim/gltf_codec.mjs decode first and
encode after (rig_tripo_static.py's order). Measure first with --profile (prints the radial profile around the thigh
axes that sets --r-leg / --belt-y / --hem-y), then judge the result by eye in a wide stance and a kick.

    python3 tools/auto_rig/pelvis_skirt_weights.py --in plain.glb --profile
    python3 tools/auto_rig/pelvis_skirt_weights.py --in plain.glb --out fixed.glb --belt-y 0.95 --hem-y 0.62 \\
        --hem-f 0.5 --r-leg 0.15 --r-blend 0.05 --report report.json
"""
import argparse
import json
import os
import shutil
import struct
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import anim_check as ac  # noqa: E402

_NP = {5121: np.uint8, 5123: np.uint16, 5125: np.uint32, 5126: np.float32}


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def glb_bin_offset(raw):
    n = struct.unpack_from('<I', raw, 12)[0]
    return 20 + n + 8  # header 12 + JSON chunk header 8 + JSON + BIN chunk header 8


def accessor_view(js, raw, boff, acc_i):
    """(numpy array view into raw, writable) for a VEC4 accessor, honouring byteStride."""
    acc = js['accessors'][acc_i]
    bv = js['bufferViews'][acc['bufferView']]
    dt = np.dtype(_NP[acc['componentType']]).newbyteorder('<')
    size = dt.itemsize
    stride = bv.get('byteStride', 0) or 4 * size
    base = boff + bv.get('byteOffset', 0) + acc.get('byteOffset', 0)
    return np.ndarray(shape=(acc['count'], 4), dtype=dt, buffer=raw, offset=base, strides=(stride, size)), acc


def thigh_axes(model, names):
    bind = model.bind_world()
    jpos = {names[k]: bind[int(j)][:3, 3] for k, j in enumerate(model.joint_nodes)}
    axes = {}
    for side in ('Left', 'Right'):
        h, k = jpos[side + 'UpLeg'], jpos[side + 'Leg']
        d = k - h
        axes[side] = (h, d / np.linalg.norm(d), float(np.linalg.norm(d)))
    return jpos, axes


def bind_positions(model, prim):
    bind = model.bind_world()
    j0 = int(model.joint_nodes[0])
    B = bind[j0] @ model.ibm[0]
    p = np.concatenate([prim['pos'], np.ones((len(prim['pos']), 1))], 1) @ B.T
    return p[:, :3]


def radial(p, axis):
    h, u, _ = axis
    q = p - h
    t = q @ u
    return np.linalg.norm(q - t[:, None] * u[None, :], axis=1), t


def profile(path):
    model = ac.AnimModel(path)
    names = [model.nodes[int(j)].get('name', f'j{j}') for j in model.joint_nodes]
    jpos, axes = thigh_axes(model, names)
    out = []
    out.append('joints: ' + ' | '.join(f'{n} {np.round(jpos[n], 3).tolist()}' for n in
                                     ('Hips', 'Spine', 'LeftUpLeg', 'LeftLeg', 'RightUpLeg', 'RightLeg') if n in jpos))
    out.append('thigh length L %.3f R %.3f' % (axes['Left'][2], axes['Right'][2]))
    hip_i = names.index('Hips')
    ul = [names.index('LeftUpLeg'), names.index('RightUpLeg')]
    for prim in model.prims:
        p = bind_positions(model, prim)
        J, W = prim['joints'], prim['weights']
        rL, _ = radial(p, axes['Left'])
        wul = (W * np.isin(J, ul)).sum(1)
        whp = (W * (J == hip_i)).sum(1)
        ymax = p[:, 1].max()
        out.append('bind height %.3f' % ymax)
        for y in np.arange(round(axes['Left'][0][1] + 0.15, 2), 0.3, -0.05):
            m = (np.abs(p[:, 1] - y) < 0.025) & (p[:, 0] > 0.02)
            if not m.any():
                continue
            r = np.sort(rL[m])
            hist = np.bincount(np.minimum((r / 0.04).astype(int), 9), minlength=10)
            out.append('y %.2f n=%6d  r p10 %.3f p50 %.3f p90 %.3f  r-hist(4 cm bins) %s  UpLeg %.2f Hips %.2f' % (
                y, m.sum(), r[int(len(r) * .1)], r[int(len(r) * .5)], r[int(len(r) * .9)],
                ' '.join(str(int(h)) for h in hist), wul[m].mean(), whp[m].mean()))
    return '\n'.join(out)


def reweight(path, out, belt_y, hem_y, hem_f, hem_fade, r_leg, r_blend, split_sigma):
    if out != path:
        shutil.copy(path, out)
    model = ac.AnimModel(out)
    names = [model.nodes[int(j)].get('name', f'j{j}') for j in model.joint_nodes]
    jpos, axes = thigh_axes(model, names)
    hip_i, li, ri = names.index('Hips'), names.index('LeftUpLeg'), names.index('RightUpLeg')
    raw = bytearray(open(out, 'rb').read())
    boff = glb_bin_offset(raw)
    js = model.js
    meta = [(p['attributes']['JOINTS_0'], p['attributes']['WEIGHTS_0']) for m in js['meshes'] for p in m['primitives']
            if 'JOINTS_0' in p.get('attributes', {}) and 'POSITION' in p.get('attributes', {})]
    rep = {'tool': 'tools/auto_rig/pelvis_skirt_weights.py',
           'params': dict(belt_y=belt_y, hem_y=hem_y, hem_f=hem_f, hem_fade=hem_fade, r_leg=r_leg, r_blend=r_blend,
                          split_sigma=split_sigma), 'prims': []}
    for (ja, wa), prim in zip(meta, model.prims):
        p = bind_positions(model, prim)
        J = prim['joints'].astype(np.int64)
        W = prim['weights'].astype(np.float64)
        rL, _ = radial(p, axes['Left'])
        rR, _ = radial(p, axes['Right'])
        r = np.minimum(rL, rR)
        shell = smoothstep(r_leg, r_leg + r_blend, r)
        y = p[:, 1]
        f = np.where(y >= belt_y, 1.0, hem_f + (1.0 - hem_f) * smoothstep(hem_y, belt_y, y))
        f = np.where(y < hem_y, hem_f * smoothstep(hem_y - hem_fade, hem_y, y), f)
        wl = (W * (J == li)).sum(1)
        wr = (W * (J == ri)).sum(1)
        wh = (W * (J == hip_i)).sum(1)
        thigh = wl + wr
        moved = shell * f * thigh
        left_share_orig = np.where(thigh > 1e-9, wl / np.maximum(thigh, 1e-9), 0.5)
        left_share_side = 1.0 / (1.0 + np.exp(-p[:, 0] / split_sigma))  # +x = character left (glTF, faces +Z)
        if jpos['LeftUpLeg'][0] < 0:  # rigs whose Left side sits at -x
            left_share_side = 1.0 - left_share_side
        left_share = left_share_orig + shell * (left_share_side - left_share_orig)
        keep_thigh = thigh - moved
        new_l, new_r, new_h = keep_thigh * left_share, keep_thigh * (1.0 - left_share), wh + moved
        # candidates: the other influences + Hips + both thighs; keep the top 4 with a continuous cut
        other = np.where(np.isin(J, [hip_i, li, ri]), 0.0, W)
        cj = np.concatenate([J, np.tile(np.array([hip_i, li, ri]), (len(J), 1))], 1)
        cw = np.concatenate([other, np.stack([new_h, new_l, new_r], 1)], 1)
        order = np.argsort(-cw, axis=1)
        cj = np.take_along_axis(cj, order, 1)
        cw = np.take_along_axis(cw, order, 1)
        fifth = cw[:, 4]
        top = np.maximum(cw[:, :4] - fifth[:, None], 0.0)
        s = top.sum(1, keepdims=True)
        bad = s[:, 0] <= 1e-9
        top[bad] = cw[bad, :4]
        s = top.sum(1, keepdims=True)
        top = top / np.maximum(s, 1e-12)
        cj4 = np.where(top > 0, cj[:, :4], 0)
        changed = np.abs(moved) > 1e-6
        changed |= np.abs(left_share - left_share_orig) * keep_thigh > 1e-6
        jv, jacc = accessor_view(js, raw, boff, ja)
        wv, wacc = accessor_view(js, raw, boff, wa)
        if wv.dtype != np.float32:
            sys.exit('WEIGHTS_0 must be float (decode the GLB first)')
        if cj4.max() > np.iinfo(jv.dtype).max:
            sys.exit('joint index does not fit JOINTS_0 component type')
        idx = np.nonzero(changed)[0]
        jv[idx] = cj4[idx].astype(jv.dtype)
        wv[idx] = top[idx].astype(np.float32)
        band = (y > hem_y) & (y < belt_y + 0.15)
        rep['prims'].append({
            'verts': int(len(J)), 'changed': int(len(idx)),
            'hips_mean_belt_to_hem_before': float(wh[band].mean()) if band.any() else None,
            'thigh_mean_belt_to_hem_before': float(thigh[band].mean()) if band.any() else None,
            'hips_mean_belt_to_hem_after': float(new_h[band].mean()) if band.any() else None,
            'thigh_mean_belt_to_hem_after': float(keep_thigh[band].mean()) if band.any() else None,
        })
    open(out, 'wb').write(raw)
    return rep


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--in', dest='inp', required=True, help='plain (decoded) skinned GLB')
    ap.add_argument('--out')
    ap.add_argument('--profile', action='store_true', help='print the radial profile around the thigh axes and exit')
    ap.add_argument('--belt-y', type=float, help='bind height (m) at and above which the shell rides the Hips fully')
    ap.add_argument('--hem-y', type=float, help='bind height (m) of the skirt hem')
    ap.add_argument('--hem-f', type=float, default=0.5, help='pelvis share of the thigh weight at the hem')
    ap.add_argument('--hem-fade', type=float, default=0.06, help='below the hem the pelvis share fades to 0 over this')
    ap.add_argument('--r-leg', type=float, help='radius (m) from the thigh axis inside which a vertex is leg, not shell')
    ap.add_argument('--r-blend', type=float, default=0.05)
    ap.add_argument('--split-sigma', type=float, default=0.035, help='width (m) of the L/R split across the midline')
    ap.add_argument('--report')
    a = ap.parse_args()
    if a.profile:
        print(profile(a.inp))
        return
    if None in (a.out, a.belt_y, a.hem_y, a.r_leg):
        sys.exit('--out, --belt-y, --hem-y and --r-leg are required (measure them with --profile)')
    rep = reweight(a.inp, a.out, a.belt_y, a.hem_y, a.hem_f, a.hem_fade, a.r_leg, a.r_blend, a.split_sigma)
    rep['input'], rep['output'] = a.inp, a.out
    txt = json.dumps(rep, indent=1)
    if a.report:
        open(a.report, 'w').write(txt + '\n')
    print(txt)


if __name__ == '__main__':
    main()
