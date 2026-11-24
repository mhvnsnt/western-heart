"""FK test 3: qe-variant x clip sweep under axis map A1. Prints per-joint
qe angles at frame 0 + foot/pelvis heights across frames, for H1 (qbind_glb),
H2 (qbind_game), H0 (packed direct)."""
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

qbind_game = {ji: mat2quat(LB_game_R[ji]) for ji in range(21)}

def fk_clip(meta, qe_map, frames_sel):
    frames = decode_rows(pack['rows'][meta['name']], meta['frames'], 21)
    rt = np.array(pack['root_t'][meta['name']])
    out = {}
    for f in frames_sel:
        Rw = {}; P = {}
        for n in BODY_ORDER:
            par = PARENT_GAME.get(n)
            if n == 12:
                Rw[n] = W_R[12]
                P[n] = rest_glb['pelvis'] + rt[f]
            else:
                Rw[n] = Rw[par] @ LB_game_R[n] @ q2R(qe_map(n, f, frames))
                P[n] = P[par] + Rw[par] @ off_local[n]
        out[f] = {n: A @ P[n] for n in P}
    return out

def qe_h1(n, f, frames):
    return qmul(qinv(qbind_glb[n]), frames[f][n])
def qe_h2(n, f, frames):
    return qmul(qinv(qbind_game[n]), frames[f][n])
def qe_h0(n, f, frames):
    return frames[f][n]

# per-joint qe angles at frame 0 for ur_m000 (H1): which joints move?
frames0 = decode_rows(pack['rows']['ur_m000'], 60, 21)
print("ur_m000 frame-0 qe angles (deg), H1:")
for n in range(21):
    q = qe_h1(n, 0, frames0)
    ang = math.degrees(2*math.acos(min(1, abs(q[0]))))
    print(f"  node {n:2d} {UR2REST[n]:8s}: {ang:6.1f}")
print("ur_m000 frame-0 qe angles (deg), H2:")
for n in range(21):
    q = qe_h2(n, 0, frames0)
    ang = math.degrees(2*math.acos(min(1, abs(q[0]))))
    print(f"  node {n:2d} {UR2REST[n]:8s}: {ang:6.1f}")

for meta in clips[:4]:
    sel = list(range(0, meta['frames'], max(1, meta['frames']//6)))
    for nm, qm in (("H1", qe_h1), ("H2", qe_h2), ("H0", qe_h0)):
        poses = fk_clip(meta, qm, sel)
        print(f"\n{meta['name']} {nm}: " + " | ".join(
            f"f{f}: pel_y={p[12][1]:.2f} head_y={p[3][1]:.2f} ankL_y={p[15][1]:.2f} ankR_y={p[19][1]:.2f} wrL={np.round(p[7],2).tolist()}"
            for f, p in poses.items()))
