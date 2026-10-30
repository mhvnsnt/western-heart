"""FK plausibility probe for T7 animation channel conventions on King's own T7 skeleton.
Usage: python3 fk.py  (reads kin.pkl / kinmot.bin.pkl / common.arc.pkl and kin_skel.json from this folder)"""
import json, pickle, itertools, math, sys
import numpy as np
P = '/tmp/claude-0/-home-user-western-heart/0e2ac5b9-e898-5469-94b9-4c1c13f1e581/scratchpad/t7probe/'
SK = json.load(open(P + 'kin_skel.json'))

def qmat(q):
    x, y, z, w = q
    return np.array([[1-2*(y*y+z*z), 2*(x*y-z*w), 2*(x*z+y*w)],
                     [2*(x*y+z*w), 1-2*(x*x+z*z), 2*(y*z-x*w)],
                     [2*(x*z-y*w), 2*(y*z+x*w), 1-2*(x*x+y*y)]])
def Rx(a): c, s = math.cos(a), math.sin(a); return np.array([[1,0,0],[0,c,-s],[0,s,c]])
def Ry(a): c, s = math.cos(a), math.sin(a); return np.array([[c,0,s],[0,1,0],[-s,0,c]])
def Rz(a): c, s = math.cos(a), math.sin(a); return np.array([[c,-s,0],[s,c,0],[0,0,1]])
AX = {'x': Rx, 'y': Ry, 'z': Rz}

# animation slot -> bone (Kiloutre applyRotationFromAnimdata), slot index = channel // 3
SLOT = {3: 'BASE', 4: 'Spine1', 5: 'Hip', 7: 'Neck', 8: 'Head', 9: 'R_Shoulder', 10: 'R_Arm', 11: 'R_ForeArm',
        12: 'R_Hand', 13: 'L_Shoulder', 14: 'L_Arm', 15: 'L_ForeArm', 16: 'L_Hand', 17: 'R_UpLeg', 18: 'R_Leg',
        19: 'R_Foot', 20: 'L_UpLeg', 21: 'L_Leg', 22: 'L_Foot'}
BONE_SLOT = {b: s for s, b in SLOT.items()}
ORDER = ['MODEL_00', 'BODY_SCALE__group', 'BASE', 'Spine1', 'Spine2', 'Neck', 'Head', 'R_Shoulder', 'R_Arm',
         'R_ForeArm', 'R_Hand', 'L_Shoulder', 'L_Arm', 'L_ForeArm', 'L_Hand', 'Hip', 'R_UpLeg', 'R_Leg', 'R_Foot',
         'L_UpLeg', 'L_Leg', 'L_Foot']
BIND = {b: qmat(SK[b]['r']) for b in ORDER}
T = {b: np.array(SK[b]['t'], float) for b in ORDER}

def euler(order, e, signs=(1, 1, 1)):
    # e = (ex, ey, ez); compose in the given order, column-vector convention: first letter applied first
    m = np.eye(3)
    for ax in order:
        i = 'xyz'.index(ax)
        m = AX[ax](signs[i] * e[i]) @ m
    return m

def fk(frame, mode, order, signs=(1, 1, 1)):
    W = {}  # world rotation, world position
    for b in ORDER:
        p = SK[b]['parent']
        R_local = BIND[b]
        if b in BONE_SLOT:
            s = BONE_SLOT[b]; e = frame[3*s:3*s+3]
            if b == 'BASE' and mode != 'none':
                Re = euler(order, e, signs)
            else:
                Re = euler(order, e, signs)
            if mode == 'bind*R': R_local = BIND[b] @ Re
            elif mode == 'R*bind': R_local = Re @ BIND[b]
            elif mode == 'R': R_local = Re
            elif mode == 'none': R_local = BIND[b]
        if p in W:
            PR, PP = W[p]
            W[b] = (PR @ R_local, PP + PR @ T[b])
        else:
            W[b] = (R_local, T[b].copy())
    return {b: W[b][1] for b in W}

def score(pos):
    """0 = physically plausible stance; larger = worse. Y is up (glTF)."""
    y = lambda b: pos[b][1]
    bad = 0.0
    feet = [y('R_Foot'), y('L_Foot')]
    lowest = min(y(b) for b in pos if b not in ('MODEL_00',))
    bad += max(0, min(feet) - lowest - 0.05)             # a foot should be the lowest point
    bad += max(0, y('Hip') - y('Head'))                  # head above hip
    bad += max(0, y('R_Leg') - y('Hip') + 0.1) + max(0, y('L_Leg') - y('Hip') + 0.1)  # knees below hips
    bad += max(0, y('R_Foot') - y('R_Leg')) + max(0, y('L_Foot') - y('L_Leg'))       # feet below knees
    bad += max(0, y('Spine2') - y('Neck') + 0.05)        # neck above upper spine
    return bad

def run(clips, label, nframes=1, which='first'):
    frames = []
    for c in clips:
        fr = c['fr']
        frames.append(fr[0] if which == 'first' else fr[len(fr)//2])
    res = []
    for mode in ('bind*R', 'R*bind', 'R'):
        for order in ('xyz', 'xzy', 'yxz', 'yzx', 'zxy', 'zyx'):
            for signs in itertools.product((1, -1), repeat=3):
                sc = [score(fk(f, mode, order, signs)) for f in frames]
                ok = sum(1 for v in sc if v < 0.02) / len(sc)
                res.append((ok, -float(np.mean(sc)), mode, order, signs))
    res.sort(reverse=True)
    print('==', label, len(frames), 'frames; bind pose score', round(score(fk(frames[0], 'none', 'xyz')), 3))
    for r in res[:8]:
        print('   plausible %5.1f%%  mean-bad %.3f  %-7s %s signs%s' % (100*r[0], -r[1], r[2], r[3], r[4]))
    return res

if __name__ == '__main__':
    C8k, Ak = pickle.load(open(P + 'kin.pkl', 'rb'))
    sel = [a for a in Ak if len(a['fr']) > 20][:400]
    run(sel, '0x64 King attacks, first frame')
    run(C8k, '0xC8 King clips, first frame')
    run(sel, '0x64 King attacks, mid frame', which='mid')
