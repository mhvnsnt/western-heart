"""Probe: FK the packed UR quats under competing conventions and print
frame-0 joint positions + trajectories. Decides the bone-map/FK approach."""
import json, struct, base64
import numpy as np

GLB = '/home/hatch/workspace/preview-clips/urban-reign/wh/teardown/urban-reign/models/char001/char001.glb'
BANK = '/home/hatch/workspace/wrestling-full-pull/other-games/urban-reign/anim-banks/ur-general-normal'

PARENT_GAME = {12: None, 0: 12, 1: 0, 2: 1, 3: 2, 4: 1, 5: 4, 6: 5, 7: 6,
               8: 1, 9: 8, 10: 9, 11: 10, 13: 12, 14: 13, 15: 14, 16: 15,
               17: 12, 18: 17, 19: 18, 20: 19}
BODY_ORDER = [12, 0, 13, 17, 1, 14, 18, 2, 4, 8, 15, 19, 3, 5, 9, 16, 20, 6, 10, 7, 11]
MB2NODE = {0: 12, 1: 0, 2: 1, 3: 2, 4: 3, 5: 4, 6: 5, 7: 6, 8: 7, 9: 8,
           10: 9, 11: 10, 12: 11, 13: 13, 14: 14, 15: 15, 16: 16, 17: 17,
           18: 18, 19: 19, 20: 20}
NODE2MB = {v: k for k, v in MB2NODE.items()}

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
            q = [vals[i+k]/32767.0 for k in range(4)]  # xyzw
            i += 4
            fr.append(np.array([q[3], q[0], q[1], q[2]]))  # wxyz
        frames.append(fr)
    return frames

g, W, glb_parent = load_W(GLB)
# bind locals under both hierarchies
def lbind(parent_map):
    out = {}
    for ji in range(21):
        par = parent_map.get(ji)
        out[ji] = W[ji].copy() if par is None else np.linalg.inv(W[par]) @ W[ji]
    return out
LB_game = lbind(PARENT_GAME)
LB_glb = lbind(glb_parent)
print("Lbind_game translations (parent->joint offsets):")
for ji in range(21):
    print(f"  node {ji:2d} par={str(PARENT_GAME.get(ji)):>4}: t={np.round(LB_game[ji][:3,3],3)}")
print("Lbind_glb translations:")
for ji in range(21):
    print(f"  node {ji:2d} par={str(glb_parent.get(ji)):>4}: t={np.round(LB_glb[ji][:3,3],3)}")

qbind_glb = {ji: mat2quat(LB_glb[ji][:3,:3]) for ji in range(21)}
qbind_game = {ji: mat2quat(LB_game[ji][:3,:3]) for ji in range(21)}

# load a clip
clips = json.load(open(f'{BANK}/clips.json'))['clips']
pack = json.load(open(f'{BANK}/rows.pack.json'))
meta = clips[0]
print("\nclip:", meta, "root_t[0]:", pack['root_t'][meta['name']][0], "root_t mid:", pack['root_t'][meta['name']][len(pack['root_t'][meta['name']])//2])
frames = decode_rows(pack['rows'][meta['name']], meta['frames'], 21)
rt = pack['root_t'][meta['name']]

def fk(frame_idx, qe_of, lbind, parent_map, order):
    JW = {}
    for n in order:
        par = parent_map.get(n)
        L = lbind[n].copy()
        if n == 12:
            L[:3, 3] = rt[frame_idx]
            # root rotation: bind only (bake convention) -> keep L rotation
        else:
            R = np.eye(4); R[:3,:3] = q2R(qe_of(n, frame_idx))
            L = L @ R
        JW[n] = L if par is None else JW[par] @ L
    return {n: JW[n][:3,3] for n in JW}

# H1: qe recovered via qbind_glb, FK via PARENT_GAME + LB_game
def qe_h1(n, f):
    return qmul(qinv(qbind_glb[n]), frames[f][n])
# H2: qe recovered via qbind_game, FK via PARENT_GAME + LB_game
def qe_h2(n, f):
    return qmul(qinv(qbind_game[n]), frames[f][n])
# H0: packed quats used directly as game locals (no qbind removal; L rotation replaced)
def fk_h0(f):
    JW = {}
    for n in BODY_ORDER:
        par = PARENT_GAME.get(n)
        L = np.eye(4); L[:3,3] = LB_game[n][:3,3] if n != 12 else rt[f]
        L[:3,:3] = q2R(frames[f][n])
        JW[n] = L if par is None else JW[par] @ L
    return {n: JW[n][:3,3] for n in JW}

for name, fn in (("H1 qe via qbind_glb", lambda f: fk(f, qe_h1, LB_game, PARENT_GAME, BODY_ORDER)),
                 ("H2 qe via qbind_game", lambda f: fk(f, qe_h2, LB_game, PARENT_GAME, BODY_ORDER)),
                 ("H0 packed direct", fk_h0)):
    print(f"\n=== {name} : frame-0 joint positions ===")
    P0 = fn(0)
    for n in BODY_ORDER:
        print(f"  node {n:2d}: {np.round(P0[n],3)}")
    # trajectory sanity: pelvis + feet over clip
    pel = [fn(f)[12] for f in range(0, meta['frames'], 10)]
    ft16 = [fn(f)[16] for f in range(0, meta['frames'], 10)]
    print("  pelvis f0,10,...:", [np.round(p,2).tolist() for p in pel])
    print("  node16 f0,10,...:", [np.round(p,2).tolist() for p in ft16])
