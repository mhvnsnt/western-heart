#!/usr/bin/env python3
"""Embed decoded .gyu motions into a character GLB as glTF animations.

Per animated node (motion bone b -> GLB node index b, H-index mapping):
  rotation channel = q_bindlocal (x) q_euler(t)   [delta composition,
  bind locals from inv(IBM) world matrices over the GLB hierarchy;
  verified: all bind matrices are pure rotation+translation]
  node 12 (motion bone 0) also gets a translation channel =
  bind local translation + root delta (game delta x 0.1 x char scale
  4.034 ~= 0.4034, axis map (x,y,z)->(x,z,-y) per the pose evaluator
  FUN_002918xx position path).
Key times = key_index * fpk / 60 (the game samples at 60 Hz).
Clips are named ur_m<idx>; the first clip also gets the alias the game
engine auto-plays: a separate animation named 'Idle' duplicating
motion 0 (assets.js createInstance plays embedded 'Idle').
"""
import json, struct, sys
import numpy as np
sys.path.insert(0, '/home/hatch/workspace/ur-phase2-work/tools')
from ur_gyu import Bank, load_tables
from ur_skin_bake import load_glb, eul2mat, MB2NODE

FPS = 60.0

def mat2quat(R):
    t = np.trace(R)
    if t > 0:
        s = np.sqrt(t + 1.0) * 2
        return np.array([0.25 * s, (R[2,1]-R[1,2])/s, (R[0,2]-R[2,0])/s, (R[1,0]-R[0,1])/s])
    i = int(np.argmax(np.diag(R)))
    if i == 0:
        s = np.sqrt(1.0 + R[0,0] - R[1,1] - R[2,2]) * 2
        return np.array([(R[2,1]-R[1,2])/s, 0.25*s, (R[0,1]+R[1,0])/s, (R[0,2]+R[2,0])/s])
    if i == 1:
        s = np.sqrt(1.0 + R[1,1] - R[0,0] - R[2,2]) * 2
        return np.array([(R[0,2]-R[2,0])/s, (R[0,1]+R[1,0])/s, 0.25*s, (R[1,2]+R[2,1])/s])
    s = np.sqrt(1.0 + R[2,2] - R[0,0] - R[1,1]) * 2
    return np.array([(R[1,0]-R[0,1])/s, (R[0,2]+R[2,0])/s, (R[1,2]+R[2,1])/s, 0.25*s])

def qmul(a, b):  # (w,x,y,z) Hamilton product a*b
    w1,x1,y1,z1 = a; w2,x2,y2,z2 = b
    return np.array([w1*w2-x1*x2-y1*y2-z1*z2, w1*x2+x1*w2+y1*z2-z1*y2,
                     w1*y2-x1*z2+y1*w2+z1*x2, w1*z2+x1*y2-y1*x2+z1*w2])

def embed(gyu_path, glb_in, glb_out, order='RzRyRx', max_motions=None):
    set1, set2 = load_tables('/home/hatch/workspace/ur-decode/work/SLUS_212.09')
    bank = Bank(gyu_path)
    g, skin, W, glb_parent, pos, jts, wts, idx = load_glb(glb_in)
    joints = skin['joints']
    Lbind = {}
    for ji in joints:
        par = glb_parent.get(ji)
        Lbind[ji] = W[ji].copy() if par is None else np.linalg.inv(W[par]) @ W[ji]
    qbind = {ji: mat2quat(Lbind[ji][:3,:3]) for ji in joints}
    node2mb = {v: k for k, v in MB2NODE.items()}

    data = open(glb_in, 'rb').read()
    ln = struct.unpack('<I', data[12:16])[0]
    gltf = json.loads(data[20:20+ln])
    off = 20 + ln; bln = struct.unpack('<I', data[off:off+4])[0]
    binx = bytearray(data[off+8:off+8+bln])
    while len(binx) % 4: binx.append(0)

    def add_accessor(arr, comp_type, acc_type, minmax=False):
        raw = arr.astype('<f4' if comp_type == 5126 else '<u2').tobytes()
        while len(binx) % 4: binx.append(0)
        bv = {'buffer': 0, 'byteOffset': len(binx), 'byteLength': len(raw)}
        binx.extend(raw)
        gltf['bufferViews'].append(bv)
        nc = {'SCALAR': 1, 'VEC3': 3, 'VEC4': 4}[acc_type]
        a = {'bufferView': len(gltf['bufferViews']) - 1, 'componentType': comp_type,
             'count': len(arr), 'type': acc_type}
        if minmax:
            a['min'] = [float(arr.min())]; a['max'] = [float(arr.max())]
        gltf['accessors'].append(a)
        return len(gltf['accessors']) - 1

    animations = []
    n_mot = bank.n_motions if max_motions is None else min(max_motions, bank.n_motions)
    for mi in range(n_mot):
        trs = bank.tracks(mi)
        dec = [t.decode(bank.d, set1, set2) for t in trs]
        channels, samplers = [], []
        root0 = dec[0][0]
        for ji in joints:
            if ji not in node2mb: continue
            mb = node2mb[ji]
            tr = trs[mb]
            times = np.array([k * tr.fpk / FPS for k in range(tr.nkeys)], dtype=np.float64)
            t_acc = add_accessor(times, 5126, 'SCALAR', minmax=True)
            if mb == 0:
                # translation channel on node 12: bind local + root delta
                base_t = Lbind[ji][:3, 3]
                vals = []
                for k in range(tr.nkeys):
                    rp = dec[0][k]
                    delta = np.array([rp[c] - root0[c] for c in range(3)]) * 0.4034
                    vals.append(base_t + np.array([delta[0], delta[2], -delta[1]]))
                v_acc = add_accessor(np.array(vals), 5126, 'VEC3')
                samplers.append({'input': t_acc, 'output': v_acc, 'interpolation': 'LINEAR'})
                channels.append({'sampler': len(samplers) - 1,
                                 'target': {'node': ji, 'path': 'translation'}})
                continue
            quats = []
            for k in range(tr.nkeys):
                e = dec[mb][k]
                qe = mat2quat(eul2mat(e[0], e[1], e[2], order))
                q = qmul(qbind[ji], qe)
                quats.append([q[1], q[2], q[3], q[0]])  # xyzw
            v_acc = add_accessor(np.array(quats), 5126, 'VEC4')
            samplers.append({'input': t_acc, 'output': v_acc, 'interpolation': 'LINEAR'})
            channels.append({'sampler': len(samplers) - 1,
                             'target': {'node': ji, 'path': 'rotation'}})
        animations.append({'name': f'ur_m{mi:03d}', 'channels': channels, 'samplers': samplers})
    # Idle alias = copy of motion 0
    if animations:
        idle = json.loads(json.dumps(animations[0])); idle['name'] = 'Idle'
        animations.append(idle)
    gltf['animations'] = animations
    gltf['buffers'][0]['byteLength'] = len(binx)
    js = json.dumps(gltf, separators=(',', ':')).encode()
    while len(js) % 4: js += b' '
    out = bytearray()
    out += struct.pack('<III', 0x46546C67, 2, 12 + 8 + len(js) + 8 + len(binx))
    out += struct.pack('<I', len(js)) + b'JSON' + js
    out += struct.pack('<I', len(binx)) + b'BIN\x00' + binx
    open(glb_out, 'wb').write(out)
    print(f'{glb_out}: {n_mot} motions embedded, {len(out)} bytes')

if __name__ == '__main__':
    embed(sys.argv[1], sys.argv[2], sys.argv[3])
