#!/usr/bin/env python3
"""Bind normalization for a GLB whose IBM accessor lives in a meshopt-
compressed bufferView. Takes the DECODED IBM bytes (via meshoptimizer JS)
as a separate file. The fixed IBMs are appended to the BIN buffer as a new
PLAIN bufferView; the old compressed view is left orphaned (harmless).
Node TRS rewrite identical to fix_binds.py.
Usage: fix_binds_meshopt.py in.glb decoded_ibm.bin out.glb
"""
import json, struct, sys
import numpy as np
from fix_binds import quat_to_mat, mat_to_quat, node_local

def main(path_in, ibm_path, path_out):
    data = open(path_in, 'rb').read()
    assert data[:4] == b'glTF'
    jlen = struct.unpack('<I', data[12:16])[0]
    js = json.loads(data[20:20+jlen])
    boff = 20 + jlen
    blen, _ = struct.unpack('<I4s', data[boff:boff+8])
    bin_data = bytearray(data[boff+8:boff+8+blen])
    nodes = js['nodes']

    parent = {}
    for i, n in enumerate(nodes):
        for c in n.get('children', []):
            parent[c] = i
    world = {}
    def compute(i, pw):
        w = pw @ node_local(nodes[i])
        world[i] = w
        for c in nodes[i].get('children', []):
            compute(c, w)
    ident = np.eye(4)
    for sc in js.get('scenes', []):
        for r in sc.get('nodes', []):
            compute(r, ident)

    skin = js['skins'][0]
    joints = skin['joints']
    jset = set(joints)
    raw = np.frombuffer(open(ibm_path, 'rb').read(), dtype='<f4')
    assert len(raw) == 16 * len(joints), (len(raw), len(joints))
    ibms = np.array([raw[k*16:(k+1)*16].reshape((4, 4), order='F').astype(np.float64)
                     for k in range(len(joints))])

    roots = [j for j in joints if parent.get(j) not in jset]
    assert len(roots) == 1
    root = roots[0]
    keepers = [j for j in joints if nodes[j].get('name', '').strip().lower() in ('hips', 'root hips')]
    assert len(keepers) == 1
    keeper = keepers[0]
    ROT180Z = quat_to_mat([0.0, 0.0, 1.0, 0.0])
    target_rot = {j: (ROT180Z if j == keeper else np.eye(4)) for j in joints}

    new_world = {}
    order = [root]
    for j in order:
        pw = new_world[parent[j]] if parent.get(j) in jset else (world[parent[j]] if parent.get(j) is not None else ident)
        W = np.eye(4)
        W[:3, :3] = pw[:3, :3] @ target_rot[j][:3, :3]
        W[:3, 3] = world[j][:3, 3]
        new_world[j] = W
        order += [c for c in nodes[j].get('children', []) if c in jset]

    for j in joints:
        pw = new_world[parent[j]] if parent.get(j) in jset else (world[parent[j]] if parent.get(j) is not None else ident)
        L = np.linalg.inv(pw) @ new_world[j]
        n = nodes[j]
        n.pop('matrix', None)
        n['rotation'] = [float(x) for x in mat_to_quat(L)]
        n['translation'] = [float(x) for x in L[:3, 3]]
        n.pop('scale', None)

    max_dev = 0.0
    new_raw = np.zeros(16 * len(joints), dtype='<f4')
    for k, j in enumerate(joints):
        newIBM = np.linalg.inv(new_world[j]) @ world[j] @ ibms[k]
        dev = np.abs(new_world[j] @ newIBM - world[j] @ ibms[k]).max()
        max_dev = max(max_dev, dev)
        new_raw[k*16:(k+1)*16] = newIBM.astype('<f4').reshape(16, order='F')
    ibm_bytes = new_raw.tobytes()

    # append IBMs as a plain bufferView at the end of the BIN buffer
    pad = (4 - len(bin_data) % 4) % 4
    bin_data += b'\x00' * pad
    new_off = len(bin_data)
    bin_data += ibm_bytes
    js['bufferViews'].append({'buffer': 0, 'byteOffset': new_off, 'byteLength': len(ibm_bytes)})
    acc = js['accessors'][skin['inverseBindMatrices']]
    acc['bufferView'] = len(js['bufferViews']) - 1
    acc['byteOffset'] = 0
    js['buffers'][0]['byteLength'] = len(bin_data)

    jbytes = json.dumps(js, separators=(',', ':')).encode()
    jbytes += b' ' * ((4 - len(jbytes) % 4) % 4)
    bpad = (4 - len(bin_data) % 4) % 4
    out = bytearray()
    out += b'glTF' + struct.pack('<II', 2, 12 + 8 + len(jbytes) + 8 + len(bin_data) + bpad)
    out += struct.pack('<I', len(jbytes)) + b'JSON' + jbytes
    out += struct.pack('<I', len(bin_data) + bpad) + b'BIN\x00' + bytes(bin_data) + b'\x00' * bpad
    open(path_out, 'wb').write(bytes(out))
    print(json.dumps({'keeper': nodes[keeper].get('name'), 'joints': len(joints),
                      'max_skin_dev': float(max_dev), 'ibm_view': acc['bufferView']}))

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3])
