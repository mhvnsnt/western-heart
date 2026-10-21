#!/usr/bin/env python3
"""Normalize a GLB's skin bind locals to the standard convention.

Standard convention (Pantera/Steve Fox, proven in DIAGNOSIS.md): every joint's
bind local rotation is identity EXCEPT the skeleton root joint (Hips), which
carries 180 deg about Z. fighter.js stage-2 premultiplies tracks by bind
locals, so any other non-identity bind corrupts the pose.

Method (bind-pose invariant by construction):
  - Keep every joint's world bind POSITION.
  - Set new world bind rotation = accumulated new locals (root: 180Z,
    all other joints: identity), translations re-expressed per joint.
  - IBM'_j = W'_j^-1 * W_j * IBM_j  =>  W'_j * IBM'_j == W_j * IBM_j,
    so skinned vertices at bind pose are bit-identical.
Only node TRS of joints + the IBM accessor bytes change. Mesh data,
textures, materials, weights are untouched.
"""
import json, struct, sys
import numpy as np

def quat_to_mat(q):
    x, y, z, w = q
    return np.array([
        [1-2*(y*y+z*z), 2*(x*y-z*w),   2*(x*z+y*w),   0],
        [2*(x*y+z*w),   1-2*(x*x+z*z), 2*(y*z-x*w),   0],
        [2*(x*z-y*w),   2*(y*z+x*w),   1-2*(x*x+y*y), 0],
        [0, 0, 0, 1]], dtype=np.float64)

def mat_to_quat(m):
    R = m[:3, :3]
    t = np.trace(R)
    if t > 0:
        s = np.sqrt(t + 1.0) * 2
        w = 0.25 * s
        x = (R[2, 1] - R[1, 2]) / s
        y = (R[0, 2] - R[2, 0]) / s
        z = (R[1, 0] - R[0, 1]) / s
    elif R[0, 0] > R[1, 1] and R[0, 0] > R[2, 2]:
        s = np.sqrt(1.0 + R[0, 0] - R[1, 1] - R[2, 2]) * 2
        w = (R[2, 1] - R[1, 2]) / s
        x = 0.25 * s
        y = (R[0, 1] + R[1, 0]) / s
        z = (R[0, 2] + R[2, 0]) / s
    elif R[1, 1] > R[2, 2]:
        s = np.sqrt(1.0 + R[1, 1] - R[0, 0] - R[2, 2]) * 2
        w = (R[0, 2] - R[2, 0]) / s
        x = (R[0, 1] + R[1, 0]) / s
        y = 0.25 * s
        z = (R[1, 2] + R[2, 1]) / s
    else:
        s = np.sqrt(1.0 + R[2, 2] - R[0, 0] - R[1, 1]) * 2
        w = (R[1, 0] - R[0, 1]) / s
        x = (R[0, 2] + R[2, 0]) / s
        y = (R[1, 2] + R[2, 1]) / s
        z = 0.25 * s
    q = np.array([x, y, z, w])
    return q / np.linalg.norm(q)

def node_local(n):
    if 'matrix' in n:
        return np.array(n['matrix'], dtype=np.float64).reshape((4, 4), order='F')
    T = np.eye(4)
    if 'translation' in n:
        T[:3, 3] = n['translation']
    R = quat_to_mat(n['rotation']) if 'rotation' in n else np.eye(4)
    S = np.diag([*(n.get('scale', [1, 1, 1])), 1.0])
    return T @ R @ S

def fix(path_in, path_out):
    data = open(path_in, 'rb').read()
    assert data[:4] == b'glTF'
    jlen = struct.unpack('<I', data[12:16])[0]
    js = json.loads(data[20:20+jlen])
    boff = 20 + jlen
    blen, btyp = struct.unpack('<I4s', data[boff:boff+8])
    bin_data = bytearray(data[boff+8:boff+8+blen])
    nodes = js['nodes']

    # parent map
    parent = {}
    for i, n in enumerate(nodes):
        for c in n.get('children', []):
            parent[c] = i

    # old world matrices for all nodes (DFS over scenes)
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

    skins = js.get('skins', [])
    assert skins, 'no skins'
    report = {}
    for skin in skins:
        joints = skin['joints']
        jset = set(joints)
        # assert: every descendant of a joint is a joint; joints form one tree
        for j in joints:
            stack = list(nodes[j].get('children', []))
            while stack:
                c = stack.pop()
                assert c in jset, f'non-joint descendant {c} of joint {j}'
                stack += nodes[c].get('children', [])
        roots = [j for j in joints if parent.get(j) not in jset]
        assert len(roots) == 1, f'expected 1 skeleton root, got {roots}'
        root = roots[0]

        # The convention keeper is the HIPS joint (the pelvis root the game
        # treats as its standard bone). Auto-rig wrappers may sit ABOVE it
        # (e.g. 'leg left butt', 'root ground') — they get zeroed like
        # everything else; only Hips keeps the 180Z convention rotation.
        keepers = [j for j in joints
                   if nodes[j].get('name', '').strip().lower() in ('hips', 'root hips')]
        assert len(keepers) == 1, f'expected 1 Hips keeper, got {[nodes[k].get("name") for k in keepers]}'
        keeper = keepers[0]

        # target local rotations
        ROT180Z = quat_to_mat([0.0, 0.0, 1.0, 0.0])
        target_rot = {j: (ROT180Z if j == keeper else np.eye(4)) for j in joints}

        # new world matrices for joints, BFS from root
        new_world = {}
        order = [root]
        for j in order:
            pw = new_world[parent[j]] if parent.get(j) in jset else world[parent[j]] if parent.get(j) is not None else ident
            rot = pw[:3, :3] @ target_rot[j][:3, :3]
            W = np.eye(4)
            W[:3, :3] = rot
            W[:3, 3] = world[j][:3, 3]
            new_world[j] = W
            order += [c for c in nodes[j].get('children', []) if c in jset]

        # rewrite joint locals: L' = W'parent^-1 * W'
        for j in joints:
            pw = new_world[parent[j]] if parent.get(j) in jset else (world[parent[j]] if parent.get(j) is not None else ident)
            L = np.linalg.inv(pw) @ new_world[j]
            q = mat_to_quat(L)
            t = L[:3, 3]
            n = nodes[j]
            n.pop('matrix', None)
            n['rotation'] = [float(x) for x in q]
            n['translation'] = [float(x) for x in t]
            n.pop('scale', None)

        # IBM rewrite
        ibm_acc_idx = skin['inverseBindMatrices']
        acc = js['accessors'][ibm_acc_idx]
        bv = js['bufferViews'][acc['bufferView']]
        base = bv.get('byteOffset', 0) + acc.get('byteOffset', 0)
        raw = np.frombuffer(bytes(bin_data[base:base + 16*4*len(joints)]),
                            dtype='<f4').reshape(len(joints), 16).copy()
        max_dev = 0.0
        for k, j in enumerate(joints):
            IBM = raw[k].reshape((4, 4), order='F').astype(np.float64)
            newIBM = np.linalg.inv(new_world[j]) @ world[j] @ IBM
            # invariance check: W' * IBM' == W * IBM
            dev = np.abs(new_world[j] @ newIBM - world[j] @ IBM).max()
            max_dev = max(max_dev, dev)
            raw[k] = newIBM.astype('<f4').reshape(16, order='F')
        bin_data[base:base + 16*4*len(joints)] = raw.tobytes()
        report[nodes[keeper].get('name', str(keeper))] = {
            'root': nodes[root].get('name', str(root)),
            'joints': len(joints), 'max_skin_dev': float(max_dev)}

    # serialize: JSON chunk (pad spaces), BIN chunk (pad zeros)
    jbytes = json.dumps(js, separators=(',', ':')).encode()
    jpad = (4 - len(jbytes) % 4) % 4
    jbytes += b' ' * jpad
    bpad = (4 - len(bin_data) % 4) % 4
    out = bytearray()
    out += b'glTF' + struct.pack('<II', 2, 12 + 8 + len(jbytes) + 8 + len(bin_data) + bpad)
    out += struct.pack('<I', len(jbytes)) + b'JSON' + jbytes
    out += struct.pack('<I', len(bin_data) + bpad) + b'BIN\x00' + bytes(bin_data) + b'\x00' * bpad
    open(path_out, 'wb').write(bytes(out))
    return report

if __name__ == '__main__':
    rep = fix(sys.argv[1], sys.argv[2])
    print(json.dumps(rep, indent=1))
