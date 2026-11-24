"""Validate qe recovery: the packer fed the root POSITION track through
eul2mat for node 12's quat. So recovered qe(0,t) should equal
eul2mat(root position values). root_t gives positions (GLB-mapped);
invert the map to get game-space positions, then compare angles."""
import json, struct, base64, math
import numpy as np

GLB = '/home/hatch/workspace/preview-clips/urban-reign/wh/teardown/urban-reign/models/char001/char001.glb'
BANK = '/home/hatch/workspace/wrestling-full-pull/other-games/urban-reign/anim-banks/ur-general-normal'

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
def eul2mat(x, y, z, order='RzRyRx'):
    cx,sx,cy,sy,cz,sz = np.cos(x),np.sin(x),np.cos(y),np.sin(y),np.cos(z),np.sin(z)
    Rx = np.array([[1,0,0],[0,cx,-sx],[0,sx,cx]],float)
    Ry = np.array([[cy,0,sy],[0,1,0],[-sy,0,cy]],float)
    Rz = np.array([[cz,-sz,0],[sz,cz,0],[0,0,1]],float)
    return Rz @ Ry @ Rx
def q2R(q):
    w,x,y,z = q / np.linalg.norm(q)
    return np.array([[1-2*(y*y+z*z), 2*(x*y-z*w), 2*(x*z+y*w)],
                     [2*(x*y+z*w), 1-2*(x*x+z*z), 2*(y*z-x*w)],
                     [2*(x*z-y*w), 2*(y*z+x*w), 1-2*(x*x+y*y)]])
def geodesic_deg(R1, R2):
    c = np.clip((np.trace(R1.T @ R2) - 1) / 2, -1, 1)
    return float(np.degrees(np.arccos(c)))

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

clips = json.load(open(f'{BANK}/clips.json'))['clips']
pack = json.load(open(f'{BANK}/rows.pack.json'))
# test on a few clips: recovered qe(0) vs eul2mat of game-space root pos.
# root_t = base_t + [dx, dz, -dy]*0.4034 where (dx,dy,dz) = game pos - root0.
# So game pos (relative) = [rt_x/0.4034, -rt_z/0.4034, rt_y/0.4034] + root0.
# root0 (absolute game pos at f0) is UNKNOWN, but qe uses ABSOLUTE dec[0]
# values, not deltas. So: qe(0,t) = eul2mat(root0 + rel(t)). root0 unknown
# -> fit: find root0 (3 params) minimizing geodesic error over frames.
from scipy.optimize import minimize
for meta in clips[:3]:
    name = meta['name']
    frames = decode_rows(pack['rows'][name], meta['frames'], 21)
    rt = np.array(pack['root_t'][name])
    rel = np.stack([rt[:,0]/0.4034, -rt[:,2]/0.4034, rt[:,1]/0.4034], axis=1)
    qe_rec = [qmul(qinv(qbind_glb[12]), frames[f][12]) for f in range(meta['frames'])]
    R_rec = [q2R(q) for q in qe_rec]
    def err(r0):
        tot = 0.0
        for f in range(meta['frames']):
            Rp = eul2mat(*(rel[f] + r0))
            tot += geodesic_deg(R_rec[f], Rp) ** 2
        return tot / meta['frames']
    res = minimize(err, np.zeros(3), method='Nelder-Mead',
                   options={'maxiter': 2000, 'xatol': 1e-4, 'fatol': 1e-6})
    rms = math.sqrt(res.fun)
    print(f"{name}: fitted root0={np.round(res.x,4)} RMS geodesic err={rms:.4f} deg over {meta['frames']}f")
    # also: what are the recovered qe(0) angle magnitudes?
    angs = [math.degrees(2*math.acos(min(1, abs(q[0])))) for q in qe_rec]
    print(f"   recovered qe(0) angle: min {min(angs):.1f} max {max(angs):.1f} deg")
