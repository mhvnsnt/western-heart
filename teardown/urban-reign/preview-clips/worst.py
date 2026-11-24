"""Find the worst-ankle clips and inspect their pelvis/root trajectories."""
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
            Rw[n] = W_R[12]; P[n] = rest_glb['pelvis'] + rt[f]
        else:
            qe = qmul(qinv(qbind_glb[n]), frames[f][n])
            Rw[n] = Rw[par] @ LB_game_R[n] @ q2R(qe)
            P[n] = P[par] + Rw[par] @ off_local[n]
    return {n: A @ P[n] for n in P}
worst = []
for bdir in ('ur-general-normal','ur-general-30frame','ur-general-weapon'):
    B = f'/home/hatch/workspace/wrestling-full-pull/other-games/urban-reign/anim-banks/{bdir}'
    cl = json.load(open(f'{B}/clips.json'))['clips']
    pk = json.load(open(f'{B}/rows.pack.json'))
    for meta in cl:
        frames = decode_rows(pk['rows'][meta['name']], meta['frames'], 21)
        rt = np.array(pk['root_t'][meta['name']])
        mn = 1e9; mnf = 0
        for f in range(meta['frames']):
            P = fk_frame(frames, rt, f)
            lo = min(P[15][1], P[19][1])
            if lo < mn: mn, mnf = lo, f
        if mn < -0.5:
            worst.append((mn, bdir, meta['name'], meta['frames'], mnf))
worst.sort()
print(f"{len(worst)} clips with min ankle < -0.5m:")
for mn, bdir, name, nf, mnf in worst[:12]:
    B = f'/home/hatch/workspace/wrestling-full-pull/other-games/urban-reign/anim-banks/{bdir}'
    pk = json.load(open(f'{B}/rows.pack.json'))
    cl = json.load(open(f'{B}/clips.json'))['clips']
    meta = [c for c in cl if c['name']==name][0]
    frames = decode_rows(pk['rows'][name], meta['frames'], 21)
    rt = np.array(pk['root_t'][name])
    # pelvis height + root_t clip-y over time
    pels = []
    for f in range(0, meta['frames'], max(1, meta['frames']//6)):
        P = fk_frame(frames, rt, f)
        pels.append((f, round(P[12][1],2), round(P[3][1],2), round(min(P[15][1],P[19][1]),2)))
    rtclip = rt @ A.T
    print(f"  {bdir}/{name} ({nf}f): min ank {mn:.2f} @f{mnf}; root_t clip-y range [{rtclip[:,1].min():.2f}, {rtclip[:,1].max():.2f}]; (f,pel,head,minank) {pels}")
