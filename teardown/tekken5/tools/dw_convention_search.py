#!/usr/bin/env python3
"""Brute-force the DW gym rotation convention.

dw_dir_probe.py showed BOTH local/global fail (30-88 deg mean error) under
the decode's stated convention R = Ry(t0)*Rx(t1)*Rz(t2). The decode itself
says the convention is "determined up to a global axis relabeling" — so the
axis assignment may be permuted. This script searches:
  * 6 axis permutations: file (t0,t1,t2) -> axes (a,b,c)
  * 2 application orders: R = Ra(t0)*Rb(t1)*Rc(t2) and the reverse
  * 2 frames: local (W = W_parent * q) vs global (W = q)
scored by the direction test: for the limb segments elbow->hand and
knee->foot (both endpoints are position bones), the segment direction
must equal W_driver * e for one constant unit vector e. The right
convention gives ~0 deg; wrong ones give tens of degrees.

Usage: python3 dw_convention_search.py <dw-motion-curves.json> [source_file ...]
"""
import json, math, sys, itertools
import numpy as np

def ax_quat(axis, deg):
    a = math.radians(deg) / 2.0
    s, c = math.sin(a), math.cos(a)
    return {'x': (s, 0, 0, c), 'y': (0, s, 0, c), 'z': (0, 0, s, c)}[axis]

def qmul(a, b):
    ax_, ay, az, aw = a; bx, by, bz, bw = b
    return (aw*bx + ax_*bw + ay*bz - az*by,
            aw*by - ax_*bz + ay*bw + az*bx,
            aw*bz + ax_*by - ay*bx + az*bw,
            aw*bw - ax_*bx - ay*by - az*bz)

def qmat(q):
    x, y, z, w = q
    return np.array([
        [1-2*(y*y+z*z), 2*(x*y-z*w),   2*(x*z+y*w)],
        [2*(x*y+z*w),   1-2*(x*x+z*z), 2*(y*z-x*w)],
        [2*(x*z-y*w),   2*(y*z+x*w),   1-2*(x*x+y*y)]])

def make_quat(triple, perm, reverse):
    a, b, c = perm
    qs = [ax_quat(a, triple[0]), ax_quat(b, triple[1]), ax_quat(c, triple[2])]
    if reverse:
        qs = qs[::-1]
    return qmul(qmul(qs[0], qs[1]), qs[2])

SEGMENTS = [
    ('armL 25->27', 25, 27), ('armR 26->28', 26, 28),
    ('legL 29->31', 29, 31), ('legR 30->32', 30, 32),
]

def score_clip(clip, perm, reverse, hyp):
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
            Q[b] = [make_quat(k, perm, reverse) for k in c['keys']]
        else:
            Q[b] = [(0.0, 0.0, 0.0, 1.0)] * nk
    W = {}
    for b in order:
        ws = []
        for k in range(nk):
            if hyp == 'local':
                ws.append(qmul(W[parent[b]][k], Q[b][k]) if b in parent else Q[b][k])
            else:
                ws.append(Q[b][k])
        W[b] = ws
    pos = {}
    for b in range(bones):
        c = curves.get(b)
        if c and c['channel'] == 'position_mm':
            pos[b] = np.array(c['keys'], dtype=float)
    # best driver per segment (any rotation bone), mean angular error
    total, count = 0.0, 0
    per_seg = {}
    for label, fb, tb in SEGMENTS:
        if fb not in pos or tb not in pos:
            continue
        seg = pos[tb] - pos[fb]
        ln = np.linalg.norm(seg, axis=1)
        ok = ln > 1.0
        u = seg[ok] / ln[ok, None]
        ks = np.where(ok)[0]
        best = (1e9, None)
        for d in range(bones):
            if d not in W:
                continue
            A = np.zeros((3, 3)); rhs = np.zeros(3)
            for i, k in enumerate(ks):
                M = qmat(W[d][k])
                A += M.T @ M
                rhs += M.T @ u[i]
            e, *_ = np.linalg.lstsq(A, rhs, rcond=None)
            en = np.linalg.norm(e)
            if en < 1e-9:
                continue
            e = e / en
            errs = []
            for i, k in enumerate(ks):
                v = qmat(W[d][k]) @ e
                errs.append(math.degrees(math.acos(float(np.clip(np.dot(v, u[i]), -1, 1)))))
            m = float(np.mean(errs))
            if m < best[0]:
                best = (m, d)
        per_seg[label] = best
        total += best[0]; count += 1
    return (total / count if count else 1e9), per_seg

def main():
    path, names = sys.argv[1], sys.argv[2:]
    d = json.load(open(path))
    clips = {c['source_file']: c for c in d['clips'] if c.get('status') == 'decoded'}
    if not names:
        names = ['gym_ikdv_36_nage_f.dat']
    perms = list(itertools.permutations('xyz'))
    results = []
    for name in names:
        clip = clips.get(name)
        if not clip:
            print(f"{name}: not found"); continue
        print(f"== {name}")
        for perm in perms:
            for reverse in (False, True):
                for hyp in ('local', 'global'):
                    mean, per_seg = score_clip(clip, perm, reverse, hyp)
                    results.append((mean, name, ''.join(perm), reverse, hyp, per_seg))
        results.sort(key=lambda r: r[0])
        for mean, nm, perm, rev, hyp, per_seg in results[:6]:
            print(f"  {mean:6.2f} deg  axes={perm} reverse={int(rev)} {hyp}  " +
                  ', '.join(f"{k}: {v[0]:.1f}deg/b{v[1]}" for k, v in per_seg.items()))

if __name__ == '__main__':
    main()
