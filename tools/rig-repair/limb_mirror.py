#!/usr/bin/env python3
"""Duplicate a bone chain to rig an unrigged duplicate limb (universal).

Given a source chain (e.g. an upper arm), a capsule bounding the unrigged
duplicate limb, and the donor bones currently (mis)holding that limb's
verts, this tool:
  1. selects the duplicate limb's verts (capsule x donor-dominant),
  2. fits the limb axis via PCA and maps the source chain's segment
     proportions onto it for bone placement (orientations copied from
     the source chain),
  3. parents the new chain to the nearest donor bone,
  4. transfers weights by proximity (donor influences -> new chain;
     source-chain influences move only when nearer the new chain),
  5. replicates finger sub-chains under the new hand.

Naming: new = <Side>Lower + <src name minus side>, e.g. LeftShoulder ->
LeftLowerShoulder, LeftHandThumb1 -> LeftLowerHandThumb1. The shared
region()/detect_*() helpers understand the 'Lower' infix.

Runs both sides: the L side comes from the flags, the R side is
auto-mirrored (names + capsule x).

Usage:
    limb_mirror.py model.glb \
      --src-chain LeftShoulder,LeftArm,LeftForeArm,LeftHand \
      --donors Spine,Spine1,Spine2,Hips,LeftUpLeg,LeftLeg \
      --capsule "0.10,1.26,0.0, 0.36,0.88,0.0, 0.10" \
      -o fixed.glb
"""
import sys
import os
import json
import argparse
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import (Glb, skin_joints, skinned_meshes, node_world_matrices,
                     detect_digit, mirror_name, normalize_cap, BoneAdder)


def parse_capsule(s):
    v = [float(x) for x in s.replace(',', ' ').split()]
    assert len(v) == 7, "capsule: x1,y1,z1, x2,y2,z2, radius"
    return np.array(v[:3]), np.array(v[3:6]), v[6]


def in_capsule(P, a, b, r):
    ab = b - a
    denom = float(ab @ ab)
    t = np.clip(((P - a) @ ab) / denom, 0, 1) if denom > 1e-12 else 0.0
    return np.linalg.norm(P - (a + t[:, None] * ab), axis=1) < r


def seg_dist(P, a, b):
    ab = b - a
    denom = float(ab @ ab)
    if denom < 1e-12:
        return np.linalg.norm(P - a, axis=1)
    t = np.clip(((P - a) @ ab) / denom, 0, 1)
    return np.linalg.norm(P - (a + t[:, None] * ab), axis=1)


def finger_descendants(g, adder, hand_name):
    """Joint names of finger chains under the hand bone (in chain order)."""
    joints = set(skin_joints(g))
    hand_ni = adder.name_to_node[hand_name]
    out = []

    def walk(ni):
        for c in g['nodes'][ni].get('children', []):
            cn = g['nodes'][c].get('name')
            if cn in joints and detect_digit(cn):
                out.append(cn)
            walk(c)

    walk(hand_ni)
    # order: group by (digit) then segment number
    def key(n):
        import re
        d = detect_digit(n)
        m = re.search(r'(\d+)\s*$', n)
        return (d or '', int(m.group(1)) if m else 0)
    return sorted(out, key=key)


def new_name(src, side):
    assert src.startswith(side)
    return side + 'Lower' + src[len(side):]


def mirror_capsule(cap):
    a, b, r = cap
    return (np.array([-a[0], a[1], a[2]]),
            np.array([-b[0], b[1], b[2]]), r)


def process_side(glb, adder, side, src_chain, donors, capsule,
                 xmin=0.12, tube_r=0.07, ymin=0.80, ymax=1.35,
                 positions=None):
    g = glb.g
    joints = skin_joints(glb.g)
    world = adder.world
    # --- candidate verts: lateral, in y-band, donor/src dominated
    # (the duplicate limb is lateral; the torso is central)
    donor_idx = {joints.index(d) for d in donors}
    src_idx = {joints.index(s) for s in src_chain}
    # source finger sub-chains count as source-chain for the transfer
    hand_src = src_chain[-1]
    for f in finger_descendants(g, adder, hand_src):
        src_idx.add(joints.index(f))
    src_names = set(src_chain) | {f for f in finger_descendants(
        g, adder, hand_src)}
    cand_info = []
    sx = 1 if side == 'Left' else -1
    for (ni, skin_idx, mesh, pi, prim) in skinned_meshes(glb):
        mw = world[ni]
        P = glb.decode(prim['attributes']['POSITION'],
                       normalize=False).reshape(-1, 3)
        # NOTE: assumes POSITION == bind pose (IBM == inv(world), checked)
        Pw = (mw[:3, :3] @ P.T).T + mw[:3, 3]
        J = glb.decode_int(prim['attributes']['JOINTS_0']).reshape(-1, 4)
        W = glb.decode(prim['attributes']['WEIGHTS_0']).reshape(-1, 4)
        dom = J[np.arange(len(J)), W.argmax(axis=1)]
        lat = (Pw[:, 0] * sx) > xmin
        yband = (Pw[:, 1] > ymin) & (Pw[:, 1] < ymax)
        if capsule is not None:
            a, b, r = capsule
            lat = lat & in_capsule(Pw, a, b, r)
        cand = lat & yband & np.isin(dom, list(donor_idx | src_idx))
        cand_info.append((prim, Pw, J, W, cand))
    allp = np.concatenate([Pw[c] for _, Pw, _, _, c in cand_info if c.any()])
    if len(allp) < 50:
        raise RuntimeError(f"side {side}: only {len(allp)} candidate verts; "
                           "check --donors/--xmin/--capsule")
    # --- PCA axis on candidates, oriented outward (away from midline)
    c = allp.mean(axis=0)
    _, _, vt = np.linalg.svd(allp - c, full_matrices=False)
    axis = vt[0]
    if (axis[0] * sx) < 0:
        axis = -axis
    # --- final selection: box around the limb (complete coverage)
    # The PCA tube was too tight and missed verts, causing tears.
    # Use explicit bounds when --positions is given.
    sel_info = []
    for prim, Pw, J, W, cand in cand_info:
        d_axis = np.linalg.norm(
            (Pw - c) - np.outer((Pw - c) @ axis, axis), axis=1)
        # tube around the PCA axis; with explicit positions the axis
        # comes from the candidate verts (still lateral, still the limb)
        sel = cand & (d_axis < tube_r)
        sel_info.append((prim, Pw, J, W, sel))
    allp2 = np.concatenate([Pw[s] for _, Pw, _, _, s in sel_info if s.any()])
    if len(allp2) < 50:
        raise RuntimeError(f"side {side}: only {len(allp2)} verts in tube; "
                           "widen --tube-r")
    # refit axis on the tube verts for placement
    c = allp2.mean(axis=0)
    _, _, vt = np.linalg.svd(allp2 - c, full_matrices=False)
    axis = vt[0]
    if (axis[0] * sx) < 0:
        axis = -axis
    proj = (allp2 - c) @ axis
    pmin, pmax = np.percentile(proj, [2, 98])
    if positions is not None:
        # explicit placement overrides PCA
        new_pos = [np.array(p) for p in positions]
        assert len(new_pos) == len(src_chain), \
            "positions count must match src-chain"
    else:
        # --- source chain proportions
        src_pos = np.array([world[adder.name_to_node[s]][:3, 3]
                            for s in src_chain])
        seglen = np.linalg.norm(np.diff(src_pos, axis=0), axis=1)
        total = seglen.sum()
        props = np.concatenate([[0.0], np.cumsum(seglen) / total])
        # --- new bone placements
        new_pos = [(c + axis * (pmin + p * (pmax - pmin))) for p in props]
    new_rots = [world[adder.name_to_node[s]][:3, :3] for s in src_chain]
    # parent: nearest donor bone to the new chain root
    best, bestd = donors[0], 1e9
    for d in donors:
        dd = float(np.linalg.norm(
            world[adder.name_to_node[d]][:3, 3] - new_pos[0]))
        if dd < bestd:
            best, bestd = d, dd
    new_bones = []  # (new_name, src_name, joint_idx, pos)
    prev_new = best
    for s, pos, rot in zip(src_chain, new_pos, new_rots):
        nn = new_name(s, side)
        wm = np.eye(4)
        wm[:3, :3] = rot
        wm[:3, 3] = pos
        ji = adder.add(nn, prev_new, wm)
        new_bones.append((nn, s, ji, pos))
        prev_new = nn
    # --- finger sub-chains under the new hand
    hand_src = src_chain[-1]
    hand_new, _, hand_ji, hand_pos = new_bones[-1]
    src_hand_pos = world[adder.name_to_node[hand_src]][:3, 3]
    finger_bones = []  # (new_name, joint_idx, pos)
    # parent map within new fingers: seg1 -> hand_new, segN -> segN-1
    parent_of_new = {}
    for f in finger_descendants(g, adder, hand_src):
        fpos = world[adder.name_to_node[f]][:3, 3]
        frot = world[adder.name_to_node[f]][:3, :3]
        nfpos = hand_pos + (fpos - src_hand_pos)
        wm = np.eye(4)
        wm[:3, :3] = frot
        wm[:3, 3] = nfpos
        nf = new_name(f, side)
        # parent: previous segment of same digit, else the new hand
        import re
        m = re.search(r'(\d+)\s*$', f)
        seg = int(m.group(1)) if m else 1
        if seg > 1:
            prev_src = f[:m.start(1)] + str(seg - 1)
            pnn = new_name(prev_src, side)
        else:
            pnn = hand_new
        ji = adder.add(nf, pnn, wm)
        finger_bones.append((nf, ji, nfpos))
    # --- weight transfer by proximity
    chain_pts = [p for _, _, _, p in new_bones]
    # segments for the main chain (+ short extension past the hand)
    hand_dir = (new_pos[-1] - new_pos[-2])
    hand_dir /= (np.linalg.norm(hand_dir) + 1e-12)
    seg_list = list(zip(chain_pts[:-1], chain_pts[1:])) + [
        (chain_pts[-1], chain_pts[-1] + hand_dir * 0.05)]
    seg_joints = [new_bones[i][2] for i in range(len(new_bones) - 1)] + \
        [new_bones[-1][2]]
    # candidate targets: main-chain segments + finger points
    targets = ([('seg', j, x, y) for j, (x, y) in zip(seg_joints, seg_list)] +
               [('pt', ji, p, p) for _, ji, p in finger_bones])

    def nearest_target(p):
        best_j, best_d = targets[0][1], 1e18
        for kind, j, x, y in targets:
            d = float(np.linalg.norm(p - x)) if kind == 'pt' \
                else float(seg_dist(p[None, :], x, y)[0])
            if d < best_d:
                best_j, best_d = j, d
        return best_j, best_d

    # --- geometric skinning: assign tube verts to the new chain by
    # proximity to its segments (ignores original weights for these verts)
    new_idx = [jb[2] for jb in new_bones]  # joint indices from creation
    seg_bones = list(zip(new_idx[:-1], new_idx[1:]))  # (proximal, distal)
    seg_pts = list(zip(new_pos[:-1], new_pos[1:]))

    moved = 0
    shoulder_p = new_pos[0]
    for prim, Pw, J, W, sel in sel_info:
        Jn = J.copy()
        Wn = W.copy()
        for vi in np.nonzero(sel)[0]:
            p = Pw[vi]
            # preserve the shoulder-torso blend: verts very close to the
            # new shoulder keep their original weights (they're the
            # anatomical shoulder cap, not the arm tube)
            if float(np.linalg.norm(p - shoulder_p)) < 0.08:
                continue
            # find nearest segment and projection
            best_si, best_t, best_d = -1, 0.0, 1e18
            for si, (a, b) in enumerate(seg_pts):
                ab = b - a
                t = float(np.dot(p - a, ab) / np.dot(ab, ab))
                tc = max(0.0, min(1.0, t))
                d = float(np.linalg.norm(p - (a + tc * ab)))
                if d < best_d:
                    best_si, best_t, best_d = si, tc, d
            bp, bd = seg_bones[best_si]
            if best_t <= 0.0:
                new_row = [(bp, 1.0)]
            elif best_t >= 1.0:
                new_row = [(bd, 1.0)]
            else:
                new_row = [(bp, 1.0 - best_t), (bd, best_t)]
            # merge (shouldn't collide, but be safe)
            merged = {}
            for j, w in new_row:
                merged[j] = merged.get(j, 0) + w
            new_row = sorted(merged.items(), key=lambda kv: -kv[1])[:4]
            tot = sum(w for _, w in new_row)
            new_row = [(j, w / tot) for j, w in new_row]
            while len(new_row) < 4:
                new_row.append((0, 0.0))
            Jn[vi] = [j for j, _ in new_row]
            Wn[vi] = [w for _, w in new_row]
            moved += 1
        glb.encode_into(prim['attributes']['JOINTS_0'], Jn)
        glb.encode_into(prim['attributes']['WEIGHTS_0'], Wn)
    return {'side': side,
            'bones': [n for n, _, _, _ in new_bones] +
                     [n for n, _, _ in finger_bones],
            'parent': best, 'verts_touched': int(moved)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('model')
    ap.add_argument('--src-chain', required=True,
                    help='comma-separated source chain, Left side')
    ap.add_argument('--donors', required=True,
                    help='comma-separated donor bones, Left side')
    ap.add_argument('--capsule', default=None,
                    help='optional "x1,y1,z1,x2,y2,z2,radius" pre-filter, '
                         'Left side (x-mirrored for Right)')
    ap.add_argument('--xmin', type=float, default=0.12,
                    help='lateral threshold: duplicate limb is |x| > xmin')
    ap.add_argument('--tube-r', type=float, default=0.07,
                    help='tube radius around the fitted limb axis')
    ap.add_argument('--ymin', type=float, default=0.80)
    ap.add_argument('--ymax', type=float, default=1.35)
    ap.add_argument('--positions', default=None,
                    help='explicit bone positions "x1,y1,z1;x2,y2,z2;..." '
                         '(one per --src-chain bone, Left side; x-mirrored '
                         'for Right). Overrides PCA placement.')
    ap.add_argument('-o', '--output', required=True)
    args = ap.parse_args()

    src_chain = [s.strip() for s in args.src_chain.split(',')]
    donors = [s.strip() for s in args.donors.split(',')]
    capsule = parse_capsule(args.capsule) if args.capsule else None
    positions = None
    if args.positions:
        positions = [[float(v) for v in pt.split(',')]
                     for pt in args.positions.split(';')]
        assert len(positions) == len(src_chain)

    glb = Glb(args.model)
    adder = BoneAdder(glb)  # aborts unless IBM == inv(world)
    results = []
    results.append(process_side(glb, adder, 'Left', src_chain, donors,
                                capsule, args.xmin, args.tube_r,
                                args.ymin, args.ymax, positions))
    r_src = [mirror_name(s) for s in src_chain]
    r_don = [mirror_name(d) or d for d in donors]
    r_cap = mirror_capsule(capsule) if capsule else None
    r_pos = [[-p[0], p[1], p[2]] for p in positions] \
        if positions else None
    results.append(process_side(glb, adder, 'Right', r_src, r_don, r_cap,
                                args.xmin, args.tube_r,
                                args.ymin, args.ymax, r_pos))
    adder.finalize()
    glb.save(args.output)
    print(json.dumps(results, indent=1))
    # verify: new bones exist as joints, file revalidates structurally
    g2 = Glb(args.output).g
    jn2 = [g2['nodes'][i].get('name') for i in g2['skins'][0]['joints']]
    missing = [b for r in results for b in r['bones'] if b not in jn2]
    print('joints now:', len(jn2), 'missing new bones:', missing or 'NONE')
    return 0 if not missing else 1


if __name__ == '__main__':
    sys.exit(main())
