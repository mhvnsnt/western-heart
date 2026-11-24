"""Verify H1 FK: full ur_m001 stance pose + qe angles + sweep all 3 banks."""
import json, struct, base64, math
import numpy as np
exec(open('/home/hatch/workspace/preview-clips/urban-reign/fk_test2.py').read().split("# candidate GLB->clip")[0])

A = np.array([[1,0,0],[0,0,-1],[0,-1,0]], float)
Ai = A.T
rest_glb = {j: Ai @ np.array(v) for j, v in REST.items()}
off_local = {}
for n in range(21):
    par = PARENT_GAME.get(n)
    if par is None: continue
    d_glb = rest_glb[UR2REST[n]] - rest_glb[UR2REST[par]]
    off_local[n] = W_R[par].T @ d_glb

def fk_frame(frames, rt, f):
    Rw = {}; P = {}
    for n in BODY_ORDER:
        par = PARENT_GAME.get(n)
        if n == 12:
            Rw[n] = W_R[12]
            P[n] = rest_glb['pelvis'] + rt[f]
        else:
            qe = qmul(qinv(qbind_glb[n]), frames[f][n])
            Rw[n] = Rw[par] @ LB_game_R[n] @ q2R(qe)
            P[n] = P[par] + Rw[par] @ off_local[n]
    return {n: A @ P[n] for n in P}, Rw

# 1. full ur_m001 frame-0 pose
clipsN = json.load(open(f'{BANK}/clips.json'))['clips']
packN = json.load(open(f'{BANK}/rows.pack.json'))
m1 = [c for c in clipsN if c['name']=='ur_m001'][0]
fr = decode_rows(packN['rows']['ur_m001'], m1['frames'], 21)
rt = np.array(packN['root_t']['ur_m001'])
P0, Rw0 = fk_frame(fr, rt, 0)
print("ur_m001 frame-0 full pose (clip space x=fwd y=up z=left):")
for n in BODY_ORDER:
    print(f"  node {n:2d} {UR2REST[n]:8s}: {np.round(P0[n],3)}")
print("ur_m001 frame-0 qe angles:")
for n in range(21):
    q = qmul(qinv(qbind_glb[n]), fr[0][n])
    print(f"  node {n:2d} {UR2REST[n]:8s}: {math.degrees(2*math.acos(min(1,abs(q[0])))):6.1f}")
# facing check: chest forward = ? use shoulder line + head offset from neck
print("head-neck offset:", np.round(P0[3]-P0[2],3), " (forward should be +x)")
print("shoulder line shL-shR:", np.round(P0[5]-P0[9],3), " (L-R should be +z)")
print("hip line hipL-hipR:", np.round(P0[13]-P0[17],3))

# 2. sweep all banks: frame-0 sanity + min ankle height per clip
import glob as gb
for bdir in ('ur-general-normal','ur-general-30frame','ur-general-weapon'):
    B = f'/home/hatch/workspace/wrestling-full-pull/other-games/urban-reign/anim-banks/{bdir}'
    cl = json.load(open(f'{B}/clips.json'))['clips']
    pk = json.load(open(f'{B}/rows.pack.json'))
    sane = 0; tot = 0; bad = []
    min_ank_all = []
    for meta in cl:
        frames = decode_rows(pk['rows'][meta['name']], meta['frames'], 21)
        rt = np.array(pk['root_t'][meta['name']])
        tot += 1
        # sample frames
        idxs = list(range(0, meta['frames'], max(1, meta['frames']//8)))
        min_ank = 1e9
        for f in idxs:
            P, _ = fk_frame(frames, rt, f)
            min_ank = min(min_ank, P[15][1], P[19][1])
        min_ank_all.append(min_ank)
        P0, _ = fk_frame(frames, rt, 0)
        if 1.45 < P0[3][1] < 1.80 and 0.0 < P0[15][1] < 0.35 and 0.0 < P0[19][1] < 0.35:
            sane += 1
        else:
            bad.append((meta['name'], round(P0[3][1],2), round(P0[15][1],2), round(P0[19][1],2)))
    print(f"{bdir}: {sane}/{tot} sane stance at f0; min-ankle distribution: "
          f"min {min(min_ank_all):.2f} p10 {sorted(min_ank_all)[len(min_ank_all)//10]:.2f} "
          f"median {sorted(min_ank_all)[len(min_ank_all)//2]:.2f}")
    print(f"   f0-unsane examples: {bad[:8]}")
