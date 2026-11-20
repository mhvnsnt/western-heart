#!/usr/bin/env python3
"""dw_roundtrip.py — position round-trip check for a baked DW bank.
Rebuilds the joint positions from the baked clips (FK through the canonical
hierarchy, using the baked skeleton rest positions and the baked locals) and
compares them to the true DW positions (FK from the raw curves, hips-relative
so the root travel does not dominate). Reports the worst distance per clip.
Head/Neck/ToeBase are excluded — their rest positions are proportions, not
measurements. The residual is the skipped-joint residual (DW joints 5/7):
expect ~130-290 mm worst at the feet during a big throw.
Usage: python3 dw_roundtrip.py --curves <dw-motion-curves.json> --bank <dir>
       --ref <reference clip> [--pack <moves.NAME.pack.json>]
       (default: every moves.*.pack.json in the bank dir, per-pack worst + overall)
"""
import argparse
import json
import math
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
# dw_fk.py lives beside these scripts; dw_curve_bake.py lives in tools/anim/
# (three levels up from teardown/tekken5/tools/ to the repo root).
for _p in (_HERE, os.path.join(_HERE, '..', '..', '..', 'tools', 'anim')):
    if _p not in sys.path:
        sys.path.insert(0, os.path.abspath(_p))
from dw_fk import (
    PARENT35, OFFSET35, PARENT27, OFFSET27,
    quat_mul, quat_apply, world_rotations, _position_at,
)
from dw_curve_bake import (
    CANON, CANON_PARENT, CANON_DW_BONE_35, CANON_DW_BONE_27,
    reference_frame,
)

MEASURED = [j for j, _ in CANON if j not in ('Head', 'Neck', 'LeftToeBase', 'RightToeBase')]

def fk_positions(rest, rot_xyzw, ki, root_t):
    """Canonical FK: joint positions (metres) from the baked clip at keyframe ki.
    root_t is the baked root translation (metres); the hips sit at root_t and
    every other joint follows the baked locals from the rest positions."""
    P = {}
    depth = {}
    def dep(j):
        if j not in depth:
            p = CANON_PARENT[j]
            depth[j] = 0 if p is None else dep(p) + 1
        return depth[j]
    for j in sorted(CANON_PARENT, key=lambda x: (dep(x), x)):
        q = rot_xyzw[j][ki]
        q = (q[0], q[1], q[2], q[3])
        if j == 'Hips':
            P[j] = (root_t[0], root_t[1], root_t[2])
            continue
        p = CANON_PARENT[j]
        # offset from parent rest position, rotated by the parent's composed G
        off = (rest[j][0] - rest[p][0], rest[j][1] - rest[p][1], rest[j][2] - rest[p][2])
        # parent's composed rotation: product of baked locals down to the parent
        G = (0.0, 0.0, 0.0, 1.0)
        chain = []
        c = p
        while c is not None:
            chain.append(c)
            c = CANON_PARENT[c]
        chain.reverse()
        for cc in chain:
            qq = rot_xyzw[cc][ki]
            G = quat_mul(G, (qq[0], qq[1], qq[2], qq[3]))
        r = quat_apply(G, off)
        P[j] = (P[p][0] + r[0], P[p][1] + r[1], P[p][2] + r[2])
    return P

def true_positions(dw, ki, parent, offset, bone_map):
    """True DW joint positions (metres, hips-relative) at keyframe ki."""
    W = world_rotations(dw, ki, parent)
    p0 = _position_at(dw, 0, ki)
    h1 = _position_at(dw, 1, ki)
    P = {0: p0, 1: (p0[0] + h1[0], p0[1] + h1[1], p0[2] + h1[2])}
    depth = {}
    def dep(b):
        if b not in depth:
            pp = parent.get(b)
            depth[b] = 0 if pp is None else dep(pp) + 1
        return depth[b]
    for b in sorted(parent.keys(), key=lambda x: (dep(x), x)):
        if b in (0, 1):
            continue
        p = parent.get(b)
        if p is None:
            P[b] = (0.0, 0.0, 0.0)
            continue
        off = offset.get(b, (0.0, 0.0, 0.0))
        r = quat_apply(W[p], off)
        P[b] = (P[p][0] + r[0], P[p][1] + r[1], P[p][2] + r[2])
    # Hips-relative, in metres, for the measured canonical joints.
    hips = P[1]
    out = {}
    for j in MEASURED:
        b = bone_map[j]
        p = P[b]
        out[j] = ((p[0] - hips[0]) / 1000.0, (p[1] - hips[1]) / 1000.0, (p[2] - hips[2]) / 1000.0)
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--curves', required=True)
    ap.add_argument('--bank', required=True)
    ap.add_argument('--ref', default='gym_ozb3_greaction2.dat')
    ap.add_argument('--pack', default=None,
                    help='one pack file to check (default: every moves.*.pack.json in the bank dir)')
    args = ap.parse_args()

    with open(args.curves) as f:
        curves = json.load(f)
    byname = {c['source_file']: c for c in curves['clips']}
    if args.pack:
        pack_files = [args.pack]
    else:
        pack_files = sorted(fn for fn in os.listdir(args.bank)
                            if fn.startswith('moves.') and fn.endswith('.pack.json'))
    skel = json.load(open(os.path.join(args.bank, 'skeleton.json')))
    rest = {j['name']: tuple(j['rest']) for j in skel['joints']}

    worst_all = 0.0
    for pack_file in pack_files:
        pack = json.load(open(os.path.join(args.bank, pack_file)))
        worst_pack = 0.0
        for cname, clip in pack['clips'].items():
            src = clip['dw_source']
            dw = byname[src]
            parent = PARENT35 if dw['bones'] == 35 else PARENT27
            offset = OFFSET35 if dw['bones'] == 35 else OFFSET27
            bone_map = CANON_DW_BONE_35 if dw['bones'] == 35 else CANON_DW_BONE_27
            worst = 0.0
            worst_joint = None
            n = len(clip['root_t'])
            for ki in range(n):
                P = fk_positions(rest, clip['rot_xyzw'], ki, clip['root_t'][ki])
                T = true_positions(dw, ki, parent, offset, bone_map)
                hips_b = P['Hips']
                for j in MEASURED:
                    pb = (P[j][0] - hips_b[0], P[j][1] - hips_b[1], P[j][2] - hips_b[2])
                    tb = T[j]
                    d = math.sqrt(sum((pb[i] - tb[i]) ** 2 for i in range(3))) * 1000.0
                    if d > worst:
                        worst = d
                        worst_joint = j
            print(f'{cname}: worst position error {worst:.1f} mm ({worst_joint})')
            worst_pack = max(worst_pack, worst)
        print(f'{pack_file}: worst {worst_pack:.1f} mm ({len(pack["clips"])} clips)')
        worst_all = max(worst_all, worst_pack)
    print(f'OVERALL worst: {worst_all:.1f} mm')

if __name__ == '__main__':
    main()
