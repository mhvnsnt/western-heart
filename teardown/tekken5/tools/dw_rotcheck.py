#!/usr/bin/env python3
"""dw_rotcheck.py — rotation round-trip check for a baked DW bank.
Recomputes the true DW world delta for each canonical joint at each keyframe
(W_c(k) * W_c(ref)^-1, in the bank frame) and compares it to the world delta
the retarget will compose from the baked locals (G = prod of baked locals
down the canonical hierarchy). Reports the worst angle error per clip.
The baked rotations reproduce the DW motion essentially exactly if the worst
error is ~0.2 deg (the rounding from 6-decimal quat storage).
Usage: python3 dw_rotcheck.py --curves <dw-motion-curves.json> --bank <dir>
       --ref <reference clip>
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
    quat_mul, quat_conj, quat_norm, quat_angle_deg,
    world_rotations,
)
from dw_curve_bake import (
    CANON, CANON_PARENT, CANON_DW_BONE_35, CANON_DW_BONE_27,
    reference_frame, rot_y_deg,
)

def compose_baked(rot_xyzw, joint, ki):
    """Compose the baked locals down the canonical hierarchy to get G(joint)."""
    chain = []
    j = joint
    while j is not None:
        chain.append(j)
        j = CANON_PARENT[j]
    chain.reverse()
    G = (0.0, 0.0, 0.0, 1.0)
    for c in chain:
        q = rot_xyzw[c][ki]
        G = quat_mul(G, (q[0], q[1], q[2], q[3]))
    return G

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--curves', required=True)
    ap.add_argument('--bank', required=True)
    ap.add_argument('--ref', default='gym_ozb3_greaction2.dat')
    args = ap.parse_args()

    with open(args.curves) as f:
        curves = json.load(f)
    byname = {c['source_file']: c for c in curves['clips']}
    pack = json.load(open(os.path.join(args.bank, 'moves.pantera.pack.json')))
    W_ref, P_ref, facing, _ = reference_frame(curves, args.ref)
    Ry = rot_y_deg(-facing)
    # Reference canonical world rotations (35-bone map, reference clip).
    Wc_ref = {j: W_ref[CANON_DW_BONE_35[j]] for j in CANON_PARENT}

    worst_all = 0.0
    for cname, clip in pack['clips'].items():
        src = clip['dw_source']
        dw = byname[src]
        parent = PARENT35 if dw['bones'] == 35 else PARENT27
        bone_map = CANON_DW_BONE_35 if dw['bones'] == 35 else CANON_DW_BONE_27
        worst = 0.0
        worst_joint = None
        for ki in range(clip['root_t'].__len__()):
            Wdw = world_rotations(dw, ki, parent)
            Wc = {j: Wdw[bone_map[j]] for j in CANON_PARENT}
            for j in CANON_PARENT:
                # True world delta, in the bank frame: R_y * (Wc(k)*Wc(ref)^-1) * R_y^-1
                true_d = quat_mul(Wc[j], quat_conj(Wc_ref[j]))
                true_d = quat_mul(Ry, quat_mul(true_d, quat_conj(Ry)))
                G = compose_baked(clip['rot_xyzw'], j, ki)
                e = quat_angle_deg(G, true_d)
                if e > worst:
                    worst = e
                    worst_joint = j
        print(f'{cname}: worst rotation error {worst:.2f} deg ({worst_joint})')
        worst_all = max(worst_all, worst)
    print(f'OVERALL worst: {worst_all:.2f} deg')

if __name__ == '__main__':
    main()
