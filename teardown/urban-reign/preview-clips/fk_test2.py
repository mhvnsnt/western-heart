"""FK test 2: UR rotations (qe recovered via qbind_glb) onto the Bannon REST
skeleton, GLB space, with candidate GLB->clip axis maps. Prints frame-0
poses; the right map yields a standing human (pelvis ~0.9, head ~1.67,
feet ~0.05)."""
import json, struct, base64, math
import numpy as np

GLB = '/home/hatch/workspace/preview-clips/urban-reign/wh/teardown/urban-reign/models/char001/char001.glb'
BANK = '/home/hatch/workspace/wrestling-full-pull/other-games/urban-reign/anim-banks/ur-general-normal'

PARENT_GAME = {12: None, 0: 12, 1: 0, 2: 1, 3: 2, 4: 1, 5: 4, 6: 5, 7: 6,
               8: 1, 9: 8, 10: 9, 11: 10, 13: 12, 14: 13, 15: 14, 16: 15,
               17: 12, 18: 17, 19: 18, 20: 19}
BODY_ORDER = [12, 0, 13, 17, 1, 14, 18, 2, 4, 8, 15, 19, 3, 5, 9, 16, 20, 6, 10, 7, 11]

# Bannon REST (vpw2_to_bannon_v13.py), clip space x=fwd y=up z=left
REST = {
 'pelvis': [0, 0.90, 0], 'spineLow': [0, 1.05, 0], 'spineMid': [0.04, 1.22, 0],
 'chest': [0, 1.30, 0], 'neck': [0.01, 1.49, 0], 'head': [0, 1.67, 0],
 'clavL': [0.02, 1.33, 0.13], 'clavR': [0.02, 1.33, -0.13],
 'shL': [0.04, 1.36, 0.22], 'shR': [0.04, 1.36, -0.22],
 'elL': [0.14, 1.024, 0.232], 'elR': [0.14, 0.968, -0.232],
 'wrL': [0.28, 0.758, 0.162], 'wrR': [0.28, 0.758, -0.162],
 'haL': [0.308, 0.688, 0.148], 'haR': [0.308, 0.688, -0.148],
 'hipL': [0, 0.885, 0.175], 'hipR': [0, 0.885, -0.175],
 'knL': [0.04, 0.46, 0.16], 'knR': [0.04, 0.46, -0.16],
 'ankL': [0.06, 0.12, 0.17], 'ankR': [0.06, 0.12, -0.17],
 'ftL': [0.06, 0.05, 0.17], 'ftR': [0.06, 0.05, -0.17],
 'fiL': [0.3409, 0.6058, 0.1316], 'fiR': [0.3409, 0.6058, -0.1316],
 'toL': [0.1597, 0.042, 0.17], 'toR': [0.1597, 0.042, -0.17],
}
# UR node -> REST joint (position anchor). UR-A chain (4-7, 13-16) -> L, B -> R (to verify).
UR2REST = {12: 'pelvis', 0: 'spineLow', 1: 'spineMid', 2: 'neck', 3: 'head',
           4: 'clavL', 5: 'shL', 6: 'elL', 7: 'wrL',
           8: 'clavR', 9: 'shR', 10: 'elR', 11: 'wrR',
           13: 'hipL', 14: 'knL', 15: 'ankL', 16: 'toL',
           17: 'hipR', 18: 'knR', 19: 'ankR', 20: 'toR'}

def load_W(glb_path):
    data = open(glb_path, 'rb').read()
    ln = struct.unpack('<I', data[12:16])[0]
    g = json.loads(data[20:20+ln])
    off = 20 + ln; bln = struct.unpack('<I', data[off:off+4])[0]
    binx = data[off+8:off+8+bln]
    def acc(ai):
        a = g['accessors'][ai]; bv = g['bufferViews'][a['bufferView']]
        o = bv.get('byteOffset', 0) + a.get('byteOffset', 0)
        ct = {5126: '<f4', 5123: '<u2', 5125: '<u4', 5121: '<u1'}[a['componentType']]
        nc = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4, 'MAT4': 16}[a['type']]
        arr = np.frombuffer(binx, dtype=ct, count=a['count'] * nc, offset=o)
        return arr.reshape(a['count'], nc) if nc > 1 else arr
    skin = g['skins'][0]
    ibm = [np.array(m).reshape(4, 4).T for m in acc(skin['inverseBindMatrices'])]
    W = {ji: np.linalg.inv(ibm[k]) for k, ji in enumerate(skin['joints'])}
    parent = {}
    for i, n in enumerate(g['nodes']):
        for c in n.get('children', []):
            parent[c] = i
    return g, W, parent

def mat2quat(R):
    t = np.trace(R)
    if t > 0:
        s = np.sqrt(t + 1.0) * 2
        return np.array([0.25*s, (R[2,1]-R[1,2])/s, (R[0,2]-R[2,0])/s, (R[1,0]-R[0,1])/s])
    i = int(np.argmax(np.diag(R)))
    if i == 0:
        s = np.sqrt(1.0 + R[0,0] - R[1,1] - R[2,2]) * 2
        return np.array([(R[2,1]-R[1,2])/s, 0.25*s, (R[0,1]+R[1,0])/s, (R[0,2]+R[2,0])/s])
    if i == 1:
        s = np.sqrt(1.0 + R[1,1] - R[0,0] - R[2,2]) * 2
        return np.array([(R[0,2]-R[2,0])/s, (R[0,1]+R[1,0])/s, 0.25*s, (R[1,2]+R[2,1])/s])
    s = np.sqrt(1.0 + R[2,2] - R[0,0] - R[1,1]) * 2
    return np.array([(R[1,0]-R[0,1])/s, (R[0,2]+R[2,0])/s, (R[1,2]+R[2,1])/s, 0.25*s])
def qmul(a, b):
    w1,x1,y1,z1 = a; w2,x2,y2,z2 = b
    return np.array([w1*w2-x1*x2-y1*y2-z1*z2, w1*x2+x1*w2+y1*z2-z1*y2,
                     w1*y2-x1*z2+y1*w2+z1*x2, w1*z2+x1*y2-y1*x2+z1*w2])
def qinv(q):
    return np.array([q[0], -q[1], -q[2], -q[3]])
def q2R(q):
    w,x,y,z = q / np.linalg.norm(q)
    return np.array([[1-2*(y*y+z*z), 2*(x*y-z*w), 2*(x*z+y*w)],
                     [2*(x*y+z*w), 1-2*(x*x+z*z), 2*(y*z-x*w)],
                     [2*(x*z-y*w), 2*(y*z+x*w), 1-2*(x*x+y*y)]])
def decode_rows(b64, n_frames, n_bones):
    raw = base64.b64decode(b64)
    vals = struct.unpack(f"<{len(raw)//2}h", raw)
    frames, i = [], 0
    for _ in range(n_frames):
        fr = []
        for _ in range(n_bones):
            q = [vals[i+k]/32767.0 for k in range(4)]
            i += 4
            fr.append(np.array([q[3], q[0], q[1], q[2]]))
        frames.append(fr)
    return frames

g, W, glb_parent = load_W(GLB)
LB_glb = {}
for ji in range(21):
    par = glb_parent.get(ji)
    LB_glb[ji] = W[ji].copy() if par is None else np.linalg.inv(W[par]) @ W[ji]
qbind_glb = {ji: mat2quat(LB_glb[ji][:3,:3]) for ji in range(21)}
# bind local rotations under GAME hierarchy (from W)
LB_game_R = {}
for ji in range(21):
    par = PARENT_GAME.get(ji)
    LB_game_R[ji] = W[ji][:3,:3] if par is None else (np.linalg.inv(W[par]) @ W[ji])[:3,:3]
W_R = {ji: W[ji][:3,:3] for ji in range(21)}

clips = json.load(open(f'{BANK}/clips.json'))['clips']
pack = json.load(open(f'{BANK}/rows.pack.json'))
meta = clips[0]
frames = decode_rows(pack['rows'][meta['name']], meta['frames'], 21)
rt = np.array(pack['root_t'][meta['name']])
# recovered qe per node per frame (GLB frame)
qe = {n: [qmul(qinv(qbind_glb[n]), frames[f][n]) for f in range(meta['frames'])] for n in range(21)}

# candidate GLB->clip axis maps (proper rotations)
CANDS = {
 'A1 (gx,-gz,-gy)': np.array([[1,0,0],[0,0,-1],[0,-1,0]], float),
 'A2 (gx,gy,-gz)': np.array([[1,0,0],[0,1,0],[0,0,-1]], float),
 'A3 (gx,gz,gy)?det-1 skip': None,
 'A4 (-gz,gx,gy)': np.array([[0,0,-1],[1,0,0],[0,1,0]], float),
 'A5 (gz,gy,gx)?': np.array([[0,0,1],[0,1,0],[1,0,0]], float),
}
for name, A in CANDS.items():
    if A is None:
        continue
    pass  # reflections allowed: clip frame is left-handed
    Ai = A.T  # inverse (rotation)
    # bind rest positions in GLB space
    rest_glb = {j: Ai @ np.array(v) for j, v in REST.items()}
    # local offsets in parent bind frame (GLB space)
    off_local = {}
    for n in range(21):
        par = PARENT_GAME.get(n)
        if par is None:
            continue
        d_glb = rest_glb[UR2REST[n]] - rest_glb[UR2REST[par]]
        off_local[n] = W_R[par].T @ d_glb
    # FK frame 0 in GLB space, then map to clip
    Rw = {}; P = {}
    for n in BODY_ORDER:
        par = PARENT_GAME.get(n)
        if n == 12:
            Rw[n] = W_R[12]  # bind only
            # root pos: REST pelvis in GLB + root_t delta (GLB space already)
            P[n] = rest_glb['pelvis'] + rt[0]
        else:
            Rw[n] = Rw[par] @ LB_game_R[n] @ q2R(qe[n][0])
            P[n] = P[par] + Rw[par] @ off_local[n]
    Pc = {n: A @ P[n] for n in P}
    print(f"\n=== {name} frame-0 (clip space) ===")
    for n in (12, 0, 1, 2, 3, 5, 6, 7, 9, 10, 11, 13, 14, 15, 16, 17, 18, 19, 20):
        print(f"  node {n:2d} {UR2REST[n]:8s}: {np.round(Pc[n],3)}")
