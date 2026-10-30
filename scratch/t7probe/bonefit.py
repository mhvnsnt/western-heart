"""Per-bone fit: find Euler order o and cube-group rotations A, B with  R_c8(stance) = A . R_64(stance) . B .
Pairs: King C8 stance (Kg_sKAM00_ -> nakg_kg2kam frame 1) vs 0x64 first frames of King attacks (median / jab)."""
import json, itertools, math, sys
import numpy as np
P = '/tmp/claude-0/-home-user-western-heart/0e2ac5b9-e898-5469-94b9-4c1c13f1e581/scratchpad/t7probe/'
d = json.load(open(P + 'stancepair.json'))
c8, s64 = d['stance_c8_f1'], d['atk64_first_median']

def Rx(a): c, s = math.cos(a), math.sin(a); return np.array([[1,0,0],[0,c,-s],[0,s,c]])
def Ry(a): c, s = math.cos(a), math.sin(a); return np.array([[c,0,s],[0,1,0],[-s,0,c]])
def Rz(a): c, s = math.cos(a), math.sin(a); return np.array([[c,-s,0],[s,c,0],[0,0,1]])
AX = (Rx, Ry, Rz)
def eul(order, e):
    m = np.eye(3)
    for k in order: m = AX[k](e[k]) @ m
    return m
# the 24 proper rotations of the cube
G = []
for perm in itertools.permutations(range(3)):
    for sg in itertools.product((1, -1), repeat=3):
        M = np.zeros((3, 3))
        for i, j in enumerate(perm): M[i, j] = sg[i]
        if abs(np.linalg.det(M) - 1) < 1e-9: G.append(M)
assert len(G) == 24
def ang(R):
    return math.degrees(math.acos(max(-1, min(1, (np.trace(R) - 1) / 2))))
BONES = {4: 'Spine1', 5: 'Hip', 7: 'Neck', 8: 'Head', 9: 'R_Shoulder', 10: 'R_Arm', 12: 'R_Hand', 13: 'L_Shoulder',
         14: 'L_Arm', 16: 'L_Hand', 17: 'R_UpLeg', 19: 'R_Foot', 20: 'L_UpLeg', 22: 'L_Foot'}
for slot, name in BONES.items():
    e8, e6 = c8[3*slot:3*slot+3], s64[3*slot:3*slot+3]
    best = []
    for order in itertools.permutations(range(3)):
        R8, R6 = eul(order, e8), eul(order, e6)
        for ia, A in enumerate(G):
            for ib, B in enumerate(G):
                best.append((ang(R8.T @ A @ R6 @ B), order, ia, ib))
    best.sort()
    # how many distinct (A,B) within 6 degrees, per order
    print('%-10s best %.1f deg order %s A%d B%d | 2nd %.1f | 3rd %.1f  | n<6deg %d' % (
        name, best[0][0], best[0][1], best[0][2], best[0][3], best[1][0], best[2][0], sum(1 for b in best if b[0] < 6)))
