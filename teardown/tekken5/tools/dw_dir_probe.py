#!/usr/bin/env python3
"""Direction probe for decoded Devil Within gym curves — local vs global rotations.

The FK probe (dw_fk_probe.py) showed position channels do NOT fit a pure
rigid FK model (RMS 323-359 mm under both hypotheses): bone 0 carries
ground-plane travel (Y always 0), bone 1 carries hips height only
(X/Z always 0), so the position bones are character-local IK-style
locators with their own translation — NOT rigid FK positions.

This probe tests ONLY directions, which need no rest offsets and no
translations: for a limb segment whose two endpoints are position
bones (elbow->hand, knee->foot), the segment direction u(k) must equal
W_driver(k) * e for one CONSTANT unit vector e, where W_driver is the
world rotation of the driving joint. Solve e by least squares and
report the mean angular error under each hypothesis:
  H1 local:  W_j = W_parent * q_j (q = recorded Euler -> R=Ry*Rx*Rz)
  H2 global: W_j = q_j
The right hypothesis gives ~0 deg error; the wrong one gives large error.

Usage: python3 dw_dir_probe.py <dw-motion-curves.json> [source_file ...]
"""
import json, math, sys
import numpy as np

def euler_quat(t0, t1, t2):
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
    return mul(mul(ax('y', t0), ax('x', t1)), ax('z', t2))

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

# (segment label, from-bone, to-bone, candidate driver bones)
SEGMENTS = [
    ('armL elbow->hand', 25, 27, [13, 14]),
    ('armR elbow->hand', 26, 28, [17, 18]),
    ('legL knee->foot', 29, 31, [20, 21]),
    ('legR knee->foot', 30, 32, [23, 24]),
]

def probe(clip):
    bones = clip['bones']
    chains = clip['chains']
    parent = {}
    for ch in chains:
        for i in range(1, len(ch)):
            parent[ch[i]] = ch[i-1]
    order = []
    for ch in chains:
        for b in ch:
            if b not in order:
                order.append(b)
    for b in range(bones):
        if b not in order:
            order.append(b)
    curves = {c['bone']: c for c in clip['curves']}
    nk = clip['n_keyframes']
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
    print(f"== {clip['source_file']}  bones={bones} keyframes={nk}")
    for hyp in ('local', 'global'):
        W = {}
        for b in order:
            ws = []
            for k in range(nk):
                if hyp == 'local':
                    ws.append(quat_mul(W[parent[b]][k], Q[b][k]) if b in parent else Q[b][k])
                else:
                    ws.append(Q[b][k])
            W[b] = ws
        print(f"  H-{hyp}:")
        for label, fb, tb, drivers in SEGMENTS:
            if fb not in pos or tb not in pos:
                print(f"    {label}: missing position bones")
                continue
            seg = pos[tb] - pos[fb]
            ln = np.linalg.norm(seg, axis=1)
            ok = ln > 1.0
            u = seg[ok] / ln[ok, None]
            for d in drivers:
                if d not in W:
                    continue
                # solve e: min sum |u_k - M_k e|^2  =>  (sum M_k^T M_k) e = sum M_k^T u_k
                A = np.zeros((3, 3)); rhs = np.zeros(3)
                ks = np.where(ok)[0]
                for k in ks:
                    M = quat_to_mat(W[d][k])
                    A += M.T @ M
                    rhs += M.T @ u[list(ks).index(k)] if False else M.T @ u[np.where(ks == k)[0][0]]
                e, *_ = np.linalg.lstsq(A, rhs, rcond=None)
                en = np.linalg.norm(e)
                e = e / en if en > 1e-9 else e
                errs = []
                for i, k in enumerate(ks):
                    v = quat_to_mat(W[d][k]) @ e
                    c = float(np.clip(np.dot(v, u[i]), -1, 1))
                    errs.append(math.degrees(math.acos(c)))
                print(f"    {label} via bone {d}: mean {np.mean(errs):6.2f} deg, "
                      f"max {np.max(errs):6.2f} deg (n={len(errs)})")
    # bone 2 (lone chain) rotation range — candidate root yaw?
    c2 = curves.get(2)
    if c2 and c2['channel'] == 'rotation_deg':
        arr = np.array(c2['keys'])
        print(f"  bone 2 rotation ranges (deg): t0 [{arr[:,0].min():.1f},{arr[:,0].max():.1f}] "
              f"t1 [{arr[:,1].min():.1f},{arr[:,1].max():.1f}] "
              f"t2 [{arr[:,2].min():.1f},{arr[:,2].max():.1f}]")

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
