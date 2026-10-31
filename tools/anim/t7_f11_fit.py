"""F11 fit: per bone, find (order, signs, A, B) with  basis_C8 ~= A . Euler_order(signs * v_0x64) . B
using King's 0x64 attack FIRST frames (attacks start from the stance) against King's 0xC8 stance (exact local
rotations the community applier writes on the mannequin). A, B range over the 24 rotations of the cube.
Result 2026-10-31 (docs/anim/T7-0x64-FRAME-RESEARCH-2026-10-30.md, Rejected): best median 10.3-66.9 deg per bone,
no bone under 10 deg, runner-up ties everywhere - not decisive.
usage: python3 t7_f11_fit.py <GRE tkdata/mothead dir> <stance_basis.json from t7_bl_basis.py> <out.pkl>"""
import itertools, json, math, pickle, re, sys
import numpy as np
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from t7_anim64 import Anim64, mota_anims

# usage: python3 t7_f11_fit.py <GRE tkdata/mothead dir> <stance_basis.json from t7_bl_basis.py> <out.pkl>
G = (sys.argv[1].rstrip('/') + '/') if len(sys.argv) > 3 else None
SLOT = {'Spine1': 4, 'Hip': 5, 'Neck': 7, 'Head': 8, 'R_Shoulder': 9, 'R_Arm': 10, 'R_ForeArm': 11, 'R_Hand': 12,
        'L_Shoulder': 13, 'L_Arm': 14, 'L_ForeArm': 15, 'L_Hand': 16, 'R_UpLeg': 17, 'R_Leg': 18, 'R_Foot': 19,
        'L_UpLeg': 20, 'L_Leg': 21, 'L_Foot': 22}


def first_frames(code, motjson):
    mv = json.load(open(motjson))['moves']
    d = open(G + 'mask/%srotsm.arc' % code, 'rb').read()
    m0 = re.search(b'MOTA', d).start(); offs = mota_anims(d, m0)
    seen, out = set(), []
    for m in mv:
        if not m.get('damage') or (m['anim_id'] & 0xC000) != 0x4000: continue
        i = m['anim_id'] & 0x3FFF
        if i in seen: continue
        seen.add(i)
        o = m0 + offs[i]
        t = d[o + 1] if d[o] == 0 else d[o]
        if t != 0x64: continue
        a = Anim64(d, o)
        if a.nb < 23: continue
        out.append(sum((b for b in a.frame(1)[:23]), []))
    return np.array(out)


def Rx(a): c, s = np.cos(a), np.sin(a); z, o = np.zeros_like(a), np.ones_like(a); return np.stack([np.stack([o, z, z], -1), np.stack([z, c, -s], -1), np.stack([z, s, c], -1)], -2)
def Ry(a): c, s = np.cos(a), np.sin(a); z, o = np.zeros_like(a), np.ones_like(a); return np.stack([np.stack([c, z, s], -1), np.stack([z, o, z], -1), np.stack([-s, z, c], -1)], -2)
def Rz(a): c, s = np.cos(a), np.sin(a); z, o = np.zeros_like(a), np.ones_like(a); return np.stack([np.stack([c, -s, z], -1), np.stack([s, c, z], -1), np.stack([z, z, o], -1)], -2)
AX = (Rx, Ry, Rz)
CUBE = []
for perm in itertools.permutations(range(3)):
    for sg in itertools.product((1, -1), repeat=3):
        M = np.zeros((3, 3))
        for r, c in enumerate(perm): M[r, c] = sg[r]
        if abs(np.linalg.det(M) - 1) < 1e-9: CUBE.append(M)


def euler(order, v):  # v: (N,3); first axis in `order` applied first (column vectors)
    m = np.broadcast_to(np.eye(3), (len(v), 3, 3)).copy()
    for k in order: m = AX[k](v[:, k]) @ m
    return m


def mean_rot(Ms):
    u, _, vt = np.linalg.svd(np.mean(Ms, 0)); r = u @ vt
    return r if np.linalg.det(r) > 0 else u @ np.diag([1, 1, -1]) @ vt


def fit_bone(T, V):
    """T: target 3x3, V: (N,3) 0x64 values -> list of (median deg, frac<10deg, order, signs, ia, ib) best first."""
    res = []
    for order in itertools.permutations(range(3)):
        for signs in itertools.product((1, -1), repeat=3):
            E = euler(order, V * np.array(signs))
            for ia, A in enumerate(CUBE):
                for ib, B in enumerate(CUBE):
                    M = B @ T.T @ A                      # trace(T^T A E B) = trace(M E)
                    tr = np.einsum('jk,ikj->i', M, E)
                    ang = np.degrees(np.arccos(np.clip((tr - 1) / 2, -1, 1)))
                    res.append((float(np.median(ang)), float(np.mean(ang < 10)), order, signs, ia, ib))
    res.sort(key=lambda r: r[0])
    return res


if __name__ == '__main__':
    if G is None: raise SystemExit(__doc__)
    basis = json.load(open(sys.argv[2]))
    V = first_frames('kin', G + 'json/kinmot.json')
    print('King 0x64 attack first frames:', len(V))
    out = {}
    for bone, s in SLOT.items():
        T = mean_rot(np.array([fr[bone] for fr in basis['frames']]))
        res = fit_bone(T, V[:, 3 * s:3 * s + 3])
        best = res[0]
        # distinct runner-up: a candidate whose predicted rotation for the median sample differs from the best's
        print('%-10s best med %5.1f deg (%3.0f%% <10deg) order %s signs %s A%-2d B%-2d | 2nd %5.1f | 10th %5.1f' % (
            bone, best[0], 100 * best[1], best[2], best[3], best[4], best[5], res[1][0], res[9][0]))
        out[bone] = res[:20]
    pickle.dump(out, open(sys.argv[3], 'wb'))
