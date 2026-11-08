#!/usr/bin/env python3
"""FK probe for decoded Devil Within gym curves — is the rotation LOCAL?

The decode (tools/gym_keyframes.py, commit 1beffd1) gives per-bone curves:
each bone carries ONE channel — position_mm (absolute, Y-up) or
rotation_deg (Euler (t0,t1,t2), R = Ry(t0)*Rx(t1)*Rz(t2)) — plus the
hierarchy as chains from the bone table. It does NOT say whether the
rotations are parent-relative (local) or world (global), and the files
carry no rest pose.

This probe decides it by forward kinematics, with NOTHING guessed:
  * rest offsets (parent->child vectors, in the parent's local frame)
    are solved by least squares from the recorded absolute positions
    of the position-channel bones across all keyframes. Given the
    rotations, the system is LINEAR in the offsets.
  * H1 (local):  W_j = W_parent * q_j; pos_j = pos_parent + W_parent * off_j
  * H2 (global): W_j = q_j;        pos_j = pos_parent + W_parent * off_j
  The hypothesis with ~0 residual (mm) is the file's convention.
  Wrong conventions give large, structured residuals.

Also reports: which bones are identifiable (on a path to a position
bone), the solved rest offsets, and the odd bones (bone 2 lone chain,
bone 8 at [-400,0,0]).

Usage: python3 dw_fk_probe.py <dw-motion-curves.json> [source_file ...]
"""
import json, math, sys
import numpy as np

def euler_quat(t0, t1, t2):
    """R = Rz(t2) * Ry(t1) * Rx(t0), angles in degrees -> (x,y,z,w).
    CRACKED 2026-11-08 by dw_convention_search.py (direction test):
    axes=xyz reverse=1 local scores 9.2 deg mean vs 35.9 deg for the
    next-best convention; the decode's stated Ry*Rx*Rz was wrong."""
    def ax(axis, deg):
        a = math.radians(deg) / 2.0
        s, c = math.sin(a), math.cos(a)
        return {'x': (s, 0, 0, c), 'y': (0, s, 0, c), 'z': (0, 0, s, c)}[axis]
    def mul(a, b):
        ax_, ay, az, aw = a; bx, by, bz, bw = b
        return (aw*bx + ax_*bw + ay*bz - az*by,
                aw*by - ax_*bz + ay*bw + az*bx,
                aw*bz + ax_*by - ay*bx + az*bw,
                aw*bw - ax_*bx - ay*by - az*bz)
    return mul(mul(ax('z', t2), ax('y', t1)), ax('x', t0))

def quat_to_mat(q):
    x, y, z, w = q
    return np.array([
        [1-2*(y*y+z*z), 2*(x*y-z*w),   2*(x*z+y*w)],
        [2*(x*y+z*w),   1-2*(x*x+z*z), 2*(y*z-x*w)],
        [2*(x*z-y*w),   2*(y*z+x*w),   1-2*(x*x+y*y)]])

def quat_mul(a, b):
    ax_, ay, az, aw = a; bx, by, bz, bw = b
    return (aw*bx + ax_*bw + ay*bz - az*by,
            aw*by - ax_*bz + ay*bw + az*bx,
            aw*bz + ax_*by - ay*bx + az*bw,
            aw*bw - ax_*bx - ay*by - az*bz)

def probe(clip, verbose=True):
    bones = clip['bones']
    chains = clip['chains']
    parent = {}
    for ch in chains:
        for i in range(1, len(ch)):
            parent[ch[i]] = ch[i-1]
    curves = {c['bone']: c for c in clip['curves']}
    nk = clip['n_keyframes']
    # local rotation quats per bone per keyframe (identity if no rotation curve)
    Q = {}
    for b in range(bones):
        c = curves.get(b)
        if c and c['channel'] == 'rotation_deg':
            Q[b] = [euler_quat(*k) for k in c['keys']]
        else:
            Q[b] = [(0.0, 0.0, 0.0, 1.0)] * nk
    pos = {}
    for b in range(bones):
        c = curves.get(b)
        if c and c['channel'] == 'position_mm':
            pos[b] = np.array(c['keys'], dtype=float)
    # Bone 8 is a FIXED marker ([-400,0,0] every frame) — not a joint; exclude.
    # Fit RELATIVE to bone 0 (the root ground travel, Y always 0), NOT bone 1:
    # bone 1's height varies (800-1055 mm), so using it as the reference would
    # make the solved rest offsets absorb the varying hips height. (A REF=1
    # patch did this and was reverted 2026-11-08; the convention patch below
    # — Rz*Ry*Rx — is kept, it is correct.)
    pos_bones = sorted(b for b in pos.keys() if b != 8)
    REF = 1 if 1 in pos else 0
    # world rotations under each hypothesis
    def world_rots(hyp):
        W = {}
        # chain order, not index order: a parent can have a higher
        # index than its child (bone 13's parent is 25).
        order = []
        for ch in chains:
            for b in ch:
                if b not in order:
                    order.append(b)
        for b in range(bones):
            if b not in order:
                order.append(b)
        for b in order:
            ws = []
            for k in range(nk):
                if hyp == 'local':
                    if b in parent:
                        ws.append(quat_mul(W[parent[b]][k], Q[b][k]))
                    else:
                        ws.append(Q[b][k])
                else:  # global
                    ws.append(Q[b][k])
            W[b] = ws
        return W
    results = {}
    for hyp in ('local', 'global'):
        W = world_rots(hyp)
        # unknowns: off_a for every bone except root(s); only bones on a
        # path to a position bone appear in equations.
        unknowns = []
        for j in pos_bones:
            if j == REF:
                continue
            a = j
            while a in parent and a != REF:
                if a not in unknowns:
                    unknowns.append(a)
                a = parent[a]
        idx = {a: i for i, a in enumerate(unknowns)}
        rows, rhs = [], []
        for j in pos_bones:
            if j == REF:
                continue
            path = []
            a = j
            while a in parent and a != REF:
                path.append(a)
                a = parent[a]
            for k in range(nk):
                for c in range(3):
                    row = np.zeros(3 * len(unknowns))
                    for a in path:
                        M = quat_to_mat(W[parent[a]][k])
                        row[3*idx[a]:3*idx[a]+3] = M[c, :]
                    rows.append(row)
                    rhs.append(pos[j][k, c] - pos[REF][k, c])
        A = np.array(rows); y = np.array(rhs)
        sol, *_ = np.linalg.lstsq(A, y, rcond=None)
        pred = A @ sol
        resid = pred - y
        offs = {a: sol[3*idx[a]:3*idx[a]+3] for a in unknowns}
        # per-bone residual RMS (mm)
        per = {}
        eq = 0
        for j in pos_bones:
            if j == REF:
                continue
            n_eq = nk * 3
            r = resid[eq:eq+n_eq]; eq += n_eq
            per[j] = float(np.sqrt(np.mean(r**2)))
        results[hyp] = {'offs': offs, 'per_bone_rms_mm': per,
                        'overall_rms_mm': float(np.sqrt(np.mean(resid**2))),
                        'max_abs_mm': float(np.max(np.abs(resid)))}
    if verbose:
        print(f"== {clip['source_file']}  bones={bones} keyframes={nk} "
              f"pos_bones={pos_bones}")
        print(f"   parent map: {parent}")
        for hyp in ('local', 'global'):
            r = results[hyp]
            print(f"   H-{hyp}: overall RMS {r['overall_rms_mm']:.3f} mm, "
                  f"max |resid| {r['max_abs_mm']:.3f} mm")
            print(f"          per-bone RMS: " +
                  ', '.join(f"b{b}:{v:.2f}" for b, v in r['per_bone_rms_mm'].items()))
        best = min(results, key=lambda h: results[h]['overall_rms_mm'])
        print(f"   VERDICT: {best} (RMS {results[best]['overall_rms_mm']:.3f} mm)")
        print("   solved rest offsets (mm, parent-local frame):")
        for a in sorted(results[best]['offs']):
            o = results[best]['offs'][a]
            print(f"     bone {a:2d} (parent {parent.get(a)}): "
                  f"[{o[0]:8.1f}, {o[1]:8.1f}, {o[2]:8.1f}]  |o|={np.linalg.norm(o):7.1f}")
        # odd bones
        if 8 in pos:
            p8 = pos[8]
            print(f"   bone 8 position range: X [{p8[:,0].min():.1f},{p8[:,0].max():.1f}] "
                  f"Y [{p8[:,1].min():.1f},{p8[:,1].max():.1f}] "
                  f"Z [{p8[:,2].min():.1f},{p8[:,2].max():.1f}]")
        c2 = curves.get(2)
        if c2:
            print(f"   bone 2 channel: {c2['channel']}, first keys: {c2['keys'][:2]}")
    return results

def main():
    path, names = sys.argv[1], sys.argv[2:]
    d = json.load(open(path))
    clips = {c['source_file']: c for c in d['clips'] if c.get('status') == 'decoded'}
    if not names:
        names = ['gym_ikdv_36_nage_f.dat']
    for n in names:
        if n not in clips:
            print(f"{n}: not decoded / not found")
            continue
        probe(clips[n])

if __name__ == '__main__':
    main()
