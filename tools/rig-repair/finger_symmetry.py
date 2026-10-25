#!/usr/bin/env python3
"""Finger-chain symmetry check + repair for WH rigged GLBs.

Tekken 7 convention (the house standard):
    thumb/index/middle/ring = 3 segments, pinky = 2 segments, mirrored L/R.
The true defect class is L/R ASYMMETRY (e.g. LeftHandThumb3 missing while
RightHandThumb3 exists). A symmetric 2-segment pinky is CORRECT - do not
"fix" it into a 3-segment pinky.

Detect mode (default): reports per-hand digit segment counts vs the T7
convention, parenting-chain integrity, and L/R asymmetry. Exit 1 on defects.

Fix mode (--fix): for each missing segment whose mirror exists, adds the
bone (mirrored placement across the armature's sagittal plane, parented into
the deficient chain) and mirrors the mirror bone's skin weights onto the
matching verts. Exit 1 if anything could not be fixed.

Usage:
    finger_symmetry.py model.glb [--json] [--fix -o fixed.glb]
"""
import sys
import os
import json
import argparse
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import (Glb, node_world_matrices, skin_joints, skeleton_root,
                     detect_side, detect_digit, seg_num, mirror_name,
                     skinned_meshes, normalize_cap, nearest_neighbors,
                     mirror_rigid_x)

T7_CONVENTION = {'thumb': 3, 'index': 3, 'middle': 3, 'ring': 3, 'pinky': 2}


def analyze(g):
    joints = skin_joints(g)
    jset = set(joints)
    parent = {}
    for ni, node in enumerate(g['nodes']):
        for c in node.get('children', []):
            cname = g['nodes'][c].get('name')
            if cname:
                parent[cname] = node.get('name')
    fingers = {}
    for name in joints:
        side = detect_side(name)
        dig = detect_digit(name)
        if not side or not dig:
            continue
        fingers.setdefault((side, dig), []).append(name)
    report = {'hands': {}, 'asymmetric': [], 'parenting': []}
    for (side, dig), names in sorted(fingers.items()):
        segs = sorted((seg_num(n), n) for n in names if seg_num(n))
        have = [s for s, _ in segs]
        want = T7_CONVENTION[dig]
        ok_chain = True
        for i, (s, n) in enumerate(segs):
            if i == 0:
                continue
            if parent.get(n) != segs[i - 1][1]:
                ok_chain = False
                report['parenting'].append(
                    f"{n} parent={parent.get(n)} want={segs[i - 1][1]}")
        key = f"{side}-{dig}"
        report['hands'][key] = {
            'have': have, 'want_3seg': want,
            'names': [n for _, n in segs],
            'chain_ok': ok_chain,
        }
        if have != list(range(1, want + 1)):
            # missing or extra vs convention; asymmetry check below decides
            pass
    # L/R asymmetry: every joint must have its mirror
    for name in joints:
        m = mirror_name(name)
        if m and m not in jset:
            report['asymmetric'].append(f"{m} missing (mirror of {name})")
    return report


def is_defect(report):
    return bool(report['asymmetric'] or report['parenting'])


def fit_mirror_plane(world, joints, name_to_node):
    """Fit the body's sagittal mirror plane from L/R joint correspondences.

    Returns (n, d) with plane n.p = d, or None if too few pairs.
    """
    diffs = []
    mids = []
    for name in joints:
        m = mirror_name(name)
        if m and m in name_to_node and name in name_to_node:
            # only pair each once (keep the Right->Left direction)
            if name.startswith('Right'):
                pr = world[name_to_node[name]][:3, 3]
                pl = world[name_to_node[m]][:3, 3]
                v = pl - pr
                nv = np.linalg.norm(v)
                if nv > 1e-6:
                    diffs.append(v / nv)
                    mids.append((pl + pr) / 2)
    if len(diffs) < 3:
        return None
    diffs = np.array(diffs)
    # sign-consistent mean direction
    n = diffs[0].copy()
    for v in diffs[1:]:
        n += v if v @ n > 0 else -v
    n /= np.linalg.norm(n)
    mids = np.array(mids)
    d = float((mids @ n).mean())
    # sanity: residuals should be small for a symmetric rig
    resid = float(np.abs(mids @ n - d).max())
    return (n, d, resid)


def reflect_rigid(w, n, d):
    """Reflect a rigid transform across plane n.p = d."""
    w = np.asarray(w, dtype=np.float64)
    q = np.eye(3) - 2.0 * np.outer(n, n)
    out = np.eye(4)
    out[:3, :3] = q @ w[:3, :3] @ q
    out[:3, 3] = q @ w[:3, 3] + 2.0 * d * n
    return out


def fix(glb, out_path):
    g = glb.g
    joints = skin_joints(g)
    jset = set(joints)
    name_to_node = {}
    for ni, node in enumerate(g['nodes']):
        if node.get('name'):
            name_to_node[node['name']] = ni
    world = node_world_matrices(g)
    root = skeleton_root(g)
    root_w = world[root]
    root_wi = np.linalg.inv(root_w)
    plane = fit_mirror_plane(world, joints, name_to_node)

    # sanity: IBM convention holds
    skin = g['skins'][0]
    ibm = glb.decode(skin['inverseBindMatrices'],
                     normalize=False).reshape(-1, 4, 4).transpose(0, 2, 1)
    worst = max(float(np.abs(np.linalg.inv(world[ni]) - ibm[k]).max())
                for k, ni in enumerate(skin['joints']))
    if worst > 1e-3:
        raise RuntimeError(f"IBM convention check failed (max err {worst})")

    # work out which bones to add: mirror of every asymmetric-missing joint
    # that is a finger segment (digit bone whose mirror exists as a joint)
    to_add = []
    for name in joints:
        m = mirror_name(name)
        if m and m not in jset and detect_digit(m):
            to_add.append((m, name))  # (new, mirror)
    if not to_add:
        glb.save(out_path)
        return {'added': [], 'note': 'nothing to add'}

    # parent lookup: node -> parent node index
    node_parent = {}
    for ni, node in enumerate(g['nodes']):
        for c in node.get('children', []):
            node_parent[c] = ni

    added = []
    new_worlds = []
    for new_name, mirror_bone in sorted(to_add):
        m_ni = name_to_node[mirror_bone]
        m_world = world[m_ni]
        if plane is not None:
            n, d, resid = plane
            new_world = reflect_rigid(m_world, n, d)
        else:
            # fallback: mirror across the armature root's YZ plane
            m_root = root_wi @ m_world
            new_world = root_w @ mirror_rigid_x(m_root)
        # parent: mirror of the mirror bone's parent
        p_ni = node_parent.get(m_ni)
        if p_ni is None:
            raise RuntimeError(f"cannot place {new_name}: "
                               f"{mirror_bone} has no parent node")
        p_name = g['nodes'][p_ni].get('name')
        new_parent_name = mirror_name(p_name)
        if new_parent_name not in name_to_node:
            raise RuntimeError(f"cannot place {new_name}: parent mirror "
                               f"{new_parent_name} not a node")
        new_p_ni = name_to_node[new_parent_name]
        local = np.linalg.inv(world[new_p_ni]) @ new_world

        new_ni = len(g['nodes'])
        g['nodes'].append({
            'name': new_name,
            'matrix': [float(v) for v in local.T.reshape(-1)],
            'children': [],
        })
        g['nodes'][new_p_ni].setdefault('children', []).append(new_ni)
        name_to_node[new_name] = new_ni

        new_joint_idx = len(skin['joints'])
        skin['joints'].append(new_ni)
        ibm_new = np.linalg.inv(new_world)
        new_worlds.append(ibm_new)
        ibm = np.concatenate([ibm, ibm_new[None, :, :]], axis=0)
        jset.add(new_name)
        joints.append(new_name)

        # mirror weights from the mirror joint onto matching verts
        mirror_joint_idx = skin['joints'].index(m_ni)
        n_mirrored = mirror_weights(glb, world, plane, root_wi,
                                    mirror_joint_idx, new_joint_idx)
        src_has_weights = n_mirrored > 0
        added.append({'bone': new_name, 'mirror_of': mirror_bone,
                      'joint_index': new_joint_idx,
                      'verts_mirrored': n_mirrored,
                      'mirror_unweighted': not src_has_weights})
    # single new IBM accessor covering originals + additions
    if new_worlds:
        ibm_all = np.concatenate(
            [ibm[:len(ibm) - len(new_worlds)].transpose(0, 2, 1)
             .reshape(-1, 16)] +
            [w.T.reshape(1, 16) for w in new_worlds], axis=0)
        skin['inverseBindMatrices'] = glb.add_accessor(ibm_all, 5126, 'MAT4')
    glb.save(out_path)
    return {'added': added}


def mirror_weights(glb, world, plane, root_wi,
                   src_joint, dst_joint, thresh=0.005):
    """Copy src_joint's weights to dst_joint on geometrically mirrored verts.

    Mirroring is done in scene/world space across the fitted sagittal plane
    (or the armature root's YZ plane if no plane was fit). Returns the
    number of verts that received the new influence.
    """
    g = glb.g
    prims = []
    for (ni, skin_idx, mesh, pi, prim) in skinned_meshes(glb):
        P = glb.decode(prim['attributes']['POSITION'],
                       normalize=False).reshape(-1, 3)
        mw = world[ni]
        Pw = (mw[:3, :3] @ P.T).T + mw[:3, 3]
        J = glb.decode_int(prim['attributes']['JOINTS_0']).reshape(-1, 4)
        W = glb.decode(prim['attributes']['WEIGHTS_0']).reshape(-1, 4)
        prims.append((prim, Pw, J, W))

    def reflect_pts(pts):
        if plane is not None:
            n, d, _ = plane
            q = np.eye(3) - 2.0 * np.outer(n, n)
            return pts @ q.T + 2.0 * d * n
        # fallback: mirror x in armature-root space
        Pr = (root_wi[:3, :3] @ pts.T).T + root_wi[:3, 3]
        Pr[:, 0] *= -1
        return (np.linalg.inv(root_wi)[:3, :3] @ Pr.T).T + \
            np.linalg.inv(root_wi)[:3, 3]

    # model scale for the match gate
    allp = np.concatenate([Pw for _, Pw, _, _ in prims])
    diag = float(np.linalg.norm(allp.max(axis=0) - allp.min(axis=0)))
    gate = 0.02 * diag
    total = 0
    for prim, Pw, J, W in prims:
        src_w = np.where(J == src_joint, W, 0.0).max(axis=1)
        cand = np.nonzero(src_w > thresh)[0]
        if len(cand) == 0:
            continue
        mirrored = reflect_pts(Pw[cand])
        idx, dist = nearest_neighbors(mirrored, Pw)
        ok = dist < gate
        # never mirror a vert onto itself or onto a vert already carrying dst
        ok = ok & (idx != cand)
        targets = idx[ok]
        wts = src_w[cand[ok]]
        Jn = J.copy()
        Wn = W.copy()
        for t, w in zip(targets, wts):
            row_j = list(Jn[t])
            row_w = list(Wn[t])
            if dst_joint in row_j:
                row_w[row_j.index(dst_joint)] += float(w)
            else:
                row_j.append(dst_joint)
                row_w.append(float(w))
            nj, nw = normalize_cap(row_j, row_w)
            Jn[t, :] = 0
            Wn[t, :] = 0.0
            Jn[t, :len(nj)] = nj
            Wn[t, :len(nw)] = nw
            total += 1
        # write back in place (same dtype/count -> same byte length)
        glb.encode_into(prim['attributes']['JOINTS_0'],
                        Jn.reshape(-1, 4))
        glb.encode_into(prim['attributes']['WEIGHTS_0'],
                        Wn.reshape(-1, 4))
    return total


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('model')
    ap.add_argument('--json', action='store_true')
    ap.add_argument('--fix', action='store_true')
    ap.add_argument('-o', '--output')
    args = ap.parse_args()

    glb = Glb(args.model)
    report = analyze(glb.g)
    if args.json:
        print(json.dumps(report, indent=1))
    else:
        for k, v in sorted(report['hands'].items()):
            flag = '' if v['have'] == list(range(1, v['want_3seg'] + 1)) \
                else '  <-- DEVIATES'
            print(f"{k}: segs={v['have']} want=1..{v['want_3seg']}"
                  f" chain_ok={v['chain_ok']}{flag}")
        for a in report['asymmetric']:
            print("ASYMMETRIC:", a)
        for p in report['parenting']:
            print("PARENTING:", p)
    if args.fix:
        if not args.output:
            ap.error("--fix requires -o/--output")
        res = fix(glb, args.output)
        print(json.dumps(res, indent=1))
        # re-analyze the fixed file
        rep2 = analyze(Glb(args.output).g)
        if is_defect(rep2):
            print("STILL DEFECTIVE:", rep2['asymmetric'],
                  rep2['parenting'])
            return 1
        print("FIX VERIFIED: no asymmetry, chains intact")
        return 0
    return 1 if is_defect(report) else 0


if __name__ == '__main__':
    sys.exit(main())
