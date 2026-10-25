#!/usr/bin/env python3
"""Skin-weight validator + universal repair for WH rigged GLBs.

Checks every skinned vertex for:
  * cross-region mis-weights: hand/arm <-> leg, hand/arm <-> tail,
    core <-> tail, leg -> tail, L <-> R limb bleed (influence > 0.12)
  * non-normalized weights (|sum-1| > 0.02)
  * more than 4 influences per vertex

Check mode (default): prints a report, writes JSON with --json, exits 1
when any violation is found.

Fix mode (--fix): applies the universal repair policy and writes a new GLB:
  For each vertex, the dominant (highest-weight) bone defines the vertex's
  home region. Any other influence above 0.12 whose (home-region, region)
  pair is in the suspicious set is bleed: its weight is moved onto the
  dominant bone. Afterwards every vertex is renormalized and capped at 4
  influences. This is a pipeline-level rule - no per-model special cases.

Usage:
    weight_validate.py model.glb [--json] [--fix -o fixed.glb]
"""
import sys
import os
import json
import argparse
import numpy as np
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import (Glb, skin_joints, skinned_meshes, region, SUSPICIOUS,
                     FLAG_T, normalize_cap, tail_root_joints,
                     is_suspicious_pair)

NORM_TOL = 0.02


def validate(glb):
    g = glb.g
    joints = skin_joints(g)
    jregion = [region(j) for j in joints]
    troots = tail_root_joints(g, joints)
    rep = {'models': {}, 'totals': Counter(),
           'violations': []}
    for (ni, skin_idx, mesh, pi, prim) in skinned_meshes(glb):
        J = glb.decode_int(prim['attributes']['JOINTS_0']).reshape(-1, 4)
        W = glb.decode(prim['attributes']['WEIGHTS_0']).reshape(-1, 4)
        n = len(J)
        key = f"mesh{mesh['name'] if 'name' in mesh else ni}.prim{pi}"
        stats = Counter()
        examples = {}
        nz = (W > 1e-9).sum(axis=1)
        sums = W.sum(axis=1)
        stats['verts'] = n
        stats['not_normalized'] = int(
            ((np.abs(sums - 1.0) > NORM_TOL) & (sums > 1e-9)).sum())
        stats['infl_gt4'] = int((nz > 4).sum())
        dom = J[np.arange(n), W.argmax(axis=1)]  # joint indices
        for vi in range(n):
            d = int(dom[vi])
            if d >= len(joints):
                continue
            dreg = jregion[d]
            row_has = False
            for k in range(4):
                w = float(W[vi, k])
                if w <= FLAG_T:
                    continue
                row_has = True
            if not row_has:
                continue
            for k in range(4):
                w = float(W[vi, k])
                ji = int(J[vi, k])
                if w <= FLAG_T or ji == d or ji >= len(joints):
                    continue
                oreg = jregion[ji]
                if is_suspicious_pair(dreg, oreg, joints[d], joints[ji],
                                      troots):
                    label = (f"{dreg}->{oreg}: {joints[d]} + "
                             f"{joints[ji]} @{w:.2f}")
                    stats[(dreg, oreg)] += 1
                    if label not in examples and len(examples) < 40:
                        examples[label] = vi
        rep['models'][key] = {'stats': dict(stats), 'examples': examples}
        for k, v in stats.items():
            rep['totals'][k] += v
    bad = any(v > 0 for k, v in rep['totals'].items()
              if k in ('not_normalized', 'infl_gt4'))
    bad = bad or any(isinstance(k, tuple) for k in rep['totals'])
    rep['has_violations'] = bad
    return rep


def repair(glb, out_path):
    g = glb.g
    joints = skin_joints(g)
    jregion = [region(j) for j in joints]
    troots = tail_root_joints(g, joints)
    total = Counter()
    for (ni, skin_idx, mesh, pi, prim) in skinned_meshes(glb):
        J = glb.decode_int(prim['attributes']['JOINTS_0']).reshape(-1, 4)
        W = glb.decode(prim['attributes']['WEIGHTS_0']).reshape(-1, 4)
        Jn = J.copy()
        Wn = W.copy()
        n = len(J)
        for vi in range(n):
            row_j = [int(x) for x in Jn[vi]]
            row_w = [float(x) for x in Wn[vi]]
            pairs = [(j, w) for j, w in zip(row_j, row_w) if w > 1e-9]
            if not pairs:
                continue
            dom_j = max(pairs, key=lambda t: t[1])[0]
            if dom_j >= len(joints):
                continue
            dreg = jregion[dom_j]
            moved = False
            new_pairs = []
            for j, w in pairs:
                if j == dom_j or j >= len(joints):
                    new_pairs.append((j, w))
                    continue
                oreg = jregion[j]
                if w > FLAG_T and is_suspicious_pair(
                        dreg, oreg, joints[dom_j], joints[j], troots):
                    total[(dreg, oreg, joints[dom_j], joints[j])] += 1
                    moved = True
                    continue  # drop; weight goes to dominant below
                new_pairs.append((j, w))
            if moved:
                kept_w = sum(w for _, w in new_pairs)
                dropped_w = sum(w for _, w in pairs) - kept_w
                new_pairs = [(j, w + dropped_w if j == dom_j else w)
                             for j, w in new_pairs]
            nj, nw = normalize_cap([j for j, _ in new_pairs],
                                   [w for _, w in new_pairs])
            Jn[vi, :] = 0
            Wn[vi, :] = 0.0
            if nj:
                Jn[vi, :len(nj)] = nj
                Wn[vi, :len(nw)] = nw
        glb.encode_into(prim['attributes']['JOINTS_0'], Jn)
        glb.encode_into(prim['attributes']['WEIGHTS_0'], Wn)
    glb.save(out_path)
    return total


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('model')
    ap.add_argument('--json', action='store_true')
    ap.add_argument('--fix', action='store_true')
    ap.add_argument('-o', '--output')
    args = ap.parse_args()

    glb = Glb(args.model)
    if args.fix:
        if not args.output:
            ap.error("--fix requires -o/--output")
        moved = repair(glb, args.output)
        print("repaired influences (home->bad : dom+bone : count):")
        for k, v in moved.most_common():
            print(f"  {k[0]}->{k[1]}: {k[2]} + {k[3]} : {v} verts")
        if not moved:
            print("  (none)")
        # re-validate the fixed file
        rep = validate(Glb(args.output))
        left = {str(k): v for k, v in rep['totals'].items()
                if (isinstance(k, tuple) or k in ('not_normalized',
                                                 'infl_gt4')) and v}
        print("residual violations:", left if left else "NONE")
        return 0 if not left else 1
    rep = validate(glb)
    if args.json:
        out = dict(rep)
        out['totals'] = {str(k): v for k, v in rep['totals'].items()}
        for m in out['models'].values():
            m['stats'] = {str(k): v for k, v in m['stats'].items()}
        print(json.dumps(out, indent=1))
    else:
        for key, m in rep['models'].items():
            print(f"[{key}] verts={m['stats'].get('verts')}")
            for k, v in sorted(m['stats'].items(), key=lambda t: str(t[0])):
                if k == 'verts' or not v:
                    continue
                print(f"    {k}: {v}")
            for ex in list(m['examples'])[:8]:
                print(f"      e.g. {ex}")
        print("VIOLATIONS FOUND" if rep['has_violations'] else "CLEAN")
    return 1 if rep['has_violations'] else 0


if __name__ == '__main__':
    sys.exit(main())
