"""Search channel->axis permutation x signs x euler order x compose mode for T7 anim channels on King's T7 skeleton.
Scores physical plausibility of stance frames (first frames of 0x64 attacks / C8 clips). King faces +Z, Y up."""
import sys, itertools, pickle, math
sys.path.insert(0, '/tmp/claude-0/-home-user-western-heart/0e2ac5b9-e898-5469-94b9-4c1c13f1e581/scratchpad/t7probe')
from fk import SK, ORDER, BIND, T, BONE_SLOT, Rx, Ry, Rz, P
import numpy as np
AXF = (Rx, Ry, Rz)

def rot(order_perm, perm, signs, e):
    # channel k drives local axis perm[k] with sign signs[k]; apply in order_perm (sequence of channel indices)
    m = np.eye(3)
    for k in order_perm:
        m = AXF[perm[k]](signs[k] * e[k]) @ m
    return m

def fk(frame, perm, signs, order, mode, skip_base=True):
    W = {}
    for b in ORDER:
        p = SK[b]['parent']; Rl = BIND[b]
        if b in BONE_SLOT and not (skip_base and b == 'BASE'):
            s = BONE_SLOT[b]; Re = rot(order, perm, signs, frame[3*s:3*s+3])
            Rl = BIND[b] @ Re if mode == 0 else Re @ BIND[b]
        if p in W: PR, PP = W[p]; W[b] = (PR @ Rl, PP + PR @ T[b])
        else: W[b] = (Rl, T[b].copy())
    return {b: W[b][1] for b in W}

def score(pos):
    y = lambda b: pos[b][1]; z = lambda b: pos[b][2]
    s = 0.0
    lowest = min(y(b) for b in pos if b not in ('MODEL_00', 'BODY_SCALE__group'))
    s += max(0, min(y('R_Foot'), y('L_Foot')) - lowest - 0.03)
    s += max(0, abs(y('R_Foot') - y('L_Foot')) - 0.25)                      # both feet near the floor in stance
    s += max(0, y('Hip') - y('Neck') + 0.3)                                   # torso upright-ish
    s += max(0, y('Neck') - y('Head') + 0.05)
    for side in 'RL':
        s += max(0, y(side+'_Leg') - y('Hip') + 0.15)                       # knee below hip
        s += max(0, y(side+'_Foot') - y(side+'_Leg') + 0.15)                # foot below knee
        # knee flexion pushes the knee forward of the hip->foot line (King faces +Z)
        mid = (pos[side+'_UpLeg'] + pos[side+'_Foot']) / 2
        s += max(0, mid[2] - z(side+'_Leg') + 0.02)
        s += max(0, y('Hip') - 0.25 - y(side+'_Hand'))                     # guard: hands above the hips
        s += max(0, z('Spine2') - z(side+'_Hand'))                          # guard: hands in front of the chest
    return s

def frames_of(clips, which):
    out = []
    for c in clips:
        fr = c['fr']
        out.append(fr[0] if which == 'first' else fr[len(fr)//2])
    return out

if __name__ == '__main__':
    C8k, Ak = pickle.load(open(P + 'kin.pkl', 'rb'))
    sets = {'64first': frames_of([a for a in Ak if len(a['fr']) > 20][:160], 'first'),
            'C8first': frames_of(C8k, 'first')}
    which = sys.argv[1] if len(sys.argv) > 1 else '64first'
    fr = sets[which]
    res = []
    for perm in itertools.permutations(range(3)):
        for signs in itertools.product((1, -1), repeat=3):
            for order in itertools.permutations(range(3)):
                for mode in (0, 1):
                    sc = [score(fk(f, perm, signs, order, mode)) for f in fr[:40]]
                    res.append((float(np.mean([v < 0.05 for v in sc])), -float(np.mean(sc)), perm, signs, order, mode))
    res.sort(reverse=True)
    top = res[:12]
    print('==', which, 'coarse (40 frames) top:')
    for r in top:
        sc = [score(fk(f, r[2], r[3], r[4], r[5])) for f in fr]
        print('  plausible %5.1f%%  mean-bad %.3f  perm(ch->axis)=%s signs=%s order=%s mode=%s' % (
            100*np.mean([v < 0.05 for v in sc]), np.mean(sc), r[2], r[3], r[4], ('bind*R', 'R*bind')[r[5]]))
