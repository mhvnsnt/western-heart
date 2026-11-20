#!/usr/bin/env python3
"""fix_finger_asymmetry.py — repair L/R asymmetric finger chains in shipped GLBs.

The shared Tekken-derived skeleton (donor: game/assets/models/pantera.glb)
ships LeftHandThumb3 missing (RightHandThumb3 exists). Every model rigged
from this donor inherits the asymmetry. This script:

1. Detects finger bones missing their L/R mirror.
2. Adds the missing bone as a child of the correct parent, with bind
   transform mirrored from the existing side (mirror across YZ plane).
3. Adds the new joint to the skin (joints + inverseBindMatrices).
4. Transfers weights: verts weighted to the parent bone that lie in the
   distal region (near the new bone) get a smooth falloff transfer to the
   new bone. Normalizes + caps at 4 influences.

Usage:
    python3 fix_finger_asymmetry.py --in MODEL.glb --out FIXED.glb [--dry-run]

Requires: numpy, scipy. Pure-Python GLB I/O (no pygltflib).
"""
import argparse
import copy
import json
import struct
import sys

import numpy as np

CT = {5120: np.int8, 5121: np.uint8, 5122: np.int16, 5123: np.uint16,
      5125: np.uint32, 5126: np.float32}
CTYPE_FOR = {'u8': 5121, 'u16': 5123, 'f32': 5126}
TYPE_COUNTS = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4, 'MAT4': 16}


def read_glb(path):
    with open(path, 'rb') as f:
        data = f.read()
    if data[:4] != b'glTF':
        raise ValueError('not a GLB file')
    jlen = struct.unpack('<I', data[12:16])[0]
    js = json.loads(data[20:20 + jlen])
    boff = 20 + jlen
    bdat = b''
    if len(data) > boff + 8 and data[boff + 4:boff + 8] == b'BIN\x00':
        blen = struct.unpack('<I', data[boff:boff + 4])[0]
        bdat = data[boff + 8:boff + 8 + blen]
    return js, bdat


def get_acc(js, bdat, idx):
    acc = js['accessors'][idx]
    bv = js['bufferViews'][acc['bufferView']]
    comp = CT[acc['componentType']]
    n = TYPE_COUNTS[acc['type']]
    off = bv.get('byteOffset', 0) + acc.get('byteOffset', 0)
    arr = np.frombuffer(bdat, dtype=np.dtype(comp),
                        count=acc['count'] * n, offset=off)
    return arr.reshape(acc['count'], n)


def mirror_name(n):
    if n.startswith('Left'):
        return 'Right' + n[4:]
    if n.startswith('Right'):
        return 'Left' + n[5:]
    return None


def node_matrix(nd):
    """Node local matrix (4x4)."""
    if 'matrix' in nd:
        return np.array(nd['matrix'], dtype=np.float64).reshape(4, 4).T
    m = np.eye(4)
    t = nd.get('translation', [0, 0, 0])
    x, y, z, w = nd.get('rotation', [0, 0, 0, 1])
    s = nd.get('scale', [1, 1, 1])
    xx, yy, zz = x * x, y * y, z * z
    xy, xz, yz = x * y, x * z, y * z
    wx, wy, wz = w * x, w * y, w * z
    rot = np.array([
        [1 - 2 * (yy + zz), 2 * (xy - wz), 2 * (xz + wy)],
        [2 * (xy + wz), 1 - 2 * (xx + zz), 2 * (yz - wx)],
        [2 * (xz - wy), 2 * (yz + wx), 1 - 2 * (xx + yy)]])
    m[:3, :3] = rot * np.array(s)
    m[:3, 3] = t
    return m


def mat_to_trs(m):
    t = m[:3, 3]
    rs = m[:3, :3]
    sx = np.linalg.norm(rs[:, 0])
    sy = np.linalg.norm(rs[:, 1])
    sz = np.linalg.norm(rs[:, 2])
    sx = sx or 1.0; sy = sy or 1.0; sz = sz or 1.0
    r = rs / np.array([sx, sy, sz])
    tr = np.trace(r)
    if tr > 0:
        s = np.sqrt(tr + 1.0) * 2
        w = 0.25 * s
        x = (r[2, 1] - r[1, 2]) / s
        y = (r[0, 2] - r[2, 0]) / s
        z = (r[1, 0] - r[0, 1]) / s
    elif r[0, 0] > r[1, 1] and r[0, 0] > r[2, 2]:
        s = np.sqrt(1.0 + r[0, 0] - r[1, 1] - r[2, 2]) * 2
        w = (r[2, 1] - r[1, 2]) / s
        x = 0.25 * s
        y = (r[0, 1] + r[1, 0]) / s
        z = (r[0, 2] + r[2, 0]) / s
    elif r[1, 1] > r[2, 2]:
        s = np.sqrt(1.0 + r[1, 1] - r[0, 0] - r[2, 2]) * 2
        w = (r[0, 2] - r[2, 0]) / s
        x = (r[0, 1] + r[1, 0]) / s
        y = 0.25 * s
        z = (r[1, 2] + r[2, 1]) / s
    else:
        s = np.sqrt(1.0 + r[2, 2] - r[0, 0] - r[1, 1]) * 2
        w = (r[1, 0] - r[0, 1]) / s
        x = (r[0, 2] + r[2, 0]) / s
        y = (r[1, 2] + r[2, 1]) / s
        z = 0.25 * s
    n = np.sqrt(x * x + y * y + z * z + w * w) or 1.0
    return t, np.array([x / n, y / n, z / n, w / n]), np.array([sx, sy, sz])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--in', dest='inp', required=True)
    ap.add_argument('--out', dest='out', required=True)
    ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()

    js, bdat = read_glb(a.inp)
    nodes = js['nodes']
    name_to_idx = {nd.get('name'): i for i, nd in enumerate(nodes)}
    parent = {}
    for i, nd in enumerate(nodes):
        for c in nd.get('children', []):
            parent[c] = i

    skins = js.get('skins', [])
    if not skins:
        print('no skins')
        return 1
    skin = skins[0]
    joints = list(skin['joints'])
    jnames = [nodes[j].get('name', '') for j in joints]
    jidx = {n: i for i, n in enumerate(jnames)}

    import re
    finger = [n for n in jnames
              if re.search(r'finger|thumb|index|middle|ring|pinky', n, re.I)]
    missing = []
    seen = set()
    for n in finger:
        m = mirror_name(n)
        if m and m not in jidx and m not in seen:
            missing.append((m, n))
            seen.add(m)
    if not missing:
        print('no asymmetric finger bones')
        return 0
    print(f'missing: {[(m, e) for m, e in missing]}')
    if a.dry_run:
        return 0

    # world matrices
    world = {}
    def get_world(i):
        if i not in world:
            lm = node_matrix(nodes[i])
            p = parent.get(i)
            world[i] = lm if p is None else get_world(p) @ lm
        return world[i]
    for i in range(len(nodes)):
        get_world(i)
    S = np.diag([-1.0, 1.0, 1.0, 1.0])  # YZ mirror

    # existing IBMs
    ibm_acc = skin.get('inverseBindMatrices')
    ibms = []
    if ibm_acc is not None:
        ibm_all = get_acc(js, bdat, ibm_acc).reshape(-1, 4, 4)
        ibms = [ibm_all[i] for i in range(len(joints))]

    added = {}  # mname -> (new_joint_pos, parent_joint_pos, new_head_world)
    for mname, ename in missing:
        eidx = name_to_idx[ename]
        ep = parent.get(eidx)
        epname = nodes[ep].get('name') if ep is not None else None
        mpname = mirror_name(epname) if epname else None
        mpidx = name_to_idx.get(mpname) if mpname else None
        if mpidx is None:
            print(f'  skip {mname}: no parent {mpname}')
            continue
        mworld = S @ world[eidx] @ S
        mlocal = np.linalg.inv(world[mpidx]) @ mworld
        t, q, s = mat_to_trs(mlocal)
        nidx = len(nodes)
        nodes.append({'name': mname,
                      'translation': [float(v) for v in t],
                      'rotation': [float(v) for v in q],
                      'scale': [float(v) for v in s]})
        name_to_idx[mname] = nidx
        pn = nodes[mpidx]
        pn['children'] = pn.get('children', []) + [nidx]
        parent[nidx] = mpidx
        world[nidx] = world[mpidx] @ node_matrix(nodes[nidx])
        joints.append(nidx)
        ibms.append(np.linalg.inv(world[nidx]))
        new_jpos = len(joints) - 1
        parent_jpos = jidx[mpname]
        added[mname] = (new_jpos, parent_jpos, world[nidx][:3, 3])
        print(f'  added {mname} under {mpname}')

    if not added:
        print('nothing added')
        return 1
    skin['joints'] = joints

    # ---- weights: distal falloff transfer from parent bone ----
    # Gather skinned prims
    prims = []
    for mi, mesh in enumerate(js['meshes']):
        for pi, prim in enumerate(mesh['primitives']):
            at = prim['attributes']
            if 'POSITION' in at and 'JOINTS_0' in at and 'WEIGHTS_0' in at:
                prims.append((prim, at))

    # New binary chunks appended
    bin_parts = [bdat]
    bin_off = len(bdat)
    new_bvs = []
    new_accs = []

    def append_array(arr, ctype, atype):
        nonlocal bin_off
        data = np.ascontiguousarray(arr)
        raw = data.tobytes()
        # pad to 4
        pad = (-len(raw)) % 4
        bv = {'buffer': 0, 'byteOffset': bin_off,
              'byteLength': len(raw) + pad}
        js['bufferViews'].append(bv)
        bvi = len(js['bufferViews']) - 1
        acc = {'bufferView': bvi, 'componentType': ctype, 'type': atype,
               'count': data.shape[0]}
        js['accessors'].append(acc)
        bin_parts.append(raw + b'\x00' * pad)
        bin_off += len(raw) + pad
        return len(js['accessors']) - 1

    for prim, at in prims:
        pos = get_acc(js, bdat, at['POSITION'])[:, :3]
        J = get_acc(js, bdat, at['JOINTS_0']).astype(np.int64)
        W = get_acc(js, bdat, at['WEIGHTS_0']).astype(np.float64)
        N = len(pos)
        # per-vertex dict
        # Rebuild with transfers using a different vectorized approach:
        # For each added bone, compute transfer amount per vertex, then merge.
        infl_j = [J[:, k:k+1] for k in range(4)]
        infl_w = [W[:, k:k+1] for k in range(4)]
        for mname, (nj, pj, nhead) in added.items():
            pnode = joints[pj]
            phead = world[pnode][:3, 3]
            blen = np.linalg.norm(nhead - phead) or 0.01
            # total parent weight per vertex
            pw = np.zeros(N)
            pmask = (J == pj)
            pw = (W * pmask).sum(axis=1)
            d = np.linalg.norm(pos - nhead, axis=1)
            f = np.clip(1.0 - d / (blen * 1.5), 0, 1) * 0.85
            move = pw * f
            # subtract from parent influences
            for k in range(4):
                mk = (J[:, k] == pj)
                W[mk, k] -= (W[mk, k] / np.maximum(pw[mk], 1e-9)) * move[mk]
            infl_j.append(np.full((N, 1), nj))
            infl_w.append(move.reshape(N, 1))
        J8 = np.concatenate(infl_j, axis=1)
        W8 = np.concatenate(infl_w, axis=1)
        # keep top 4 by weight, normalize
        order = np.argsort(-W8, axis=1)[:, :4]
        J4 = np.take_along_axis(J8, order, axis=1)
        W4 = np.take_along_axis(W8, order, axis=1)
        s = W4.sum(axis=1, keepdims=True)
        s[s < 1e-9] = 1.0
        W4 /= s
        # zero out negligible
        W4[W4 < 1e-4] = 0
        s = W4.sum(axis=1, keepdims=True); s[s < 1e-9] = 1.0
        W4 /= s
        # write back as u16 joints + float weights
        j_acc = append_array(J4.astype(np.uint16), 5123, 'VEC4')
        w_acc = append_array(W4.astype(np.float32), 5126, 'VEC4')
        at['JOINTS_0'] = j_acc
        at['WEIGHTS_0'] = w_acc

    # new IBM accessor
    ibm_arr = np.stack(ibms).astype(np.float32)
    ibm_new = append_array(ibm_arr.reshape(-1, 16), 5126, 'MAT4')
    # MAT4 accessor count is number of matrices
    js['accessors'][ibm_new]['count'] = len(ibms)
    skin['inverseBindMatrices'] = ibm_new

    # update buffer byteLength
    total_bin = b''.join(bin_parts)
    js['buffers'][0]['byteLength'] = len(total_bin)
    jstr = json.dumps(js, separators=(',', ':')).encode()
    jpad = (-len(jstr)) % 4
    out = (b'glTF' + struct.pack('<I', 2) + struct.pack('<I', len(jstr) + jpad) +
           jstr + b' ' * jpad +
           struct.pack('<I', len(total_bin)) + b'BIN\x00' + total_bin)
    with open(a.out, 'wb') as f:
        f.write(out)
    print(f'wrote {a.out} ({len(out)/1e6:.1f} MB), joints {len(joints)}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
