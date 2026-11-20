#!/usr/bin/env python3
"""glb_full_repair.py — comprehensive teardown-wiring repair for shipped GLBs.

Applies all four repair layers in one pass:
  1. Finger asymmetry: add missing mirror finger bones + distal falloff weights
  2. Jiggle bones: Breast_L/R, Butt_L/R, Belly (+ optional ThighFat_L/R)
     parented to spine/hip bones, with anatomical region weights
  3. Face morphs: 10 morph targets (blink_L/R, jawOpen, browUp/Down,
     mouthSmile/Frown/Open, eyesWide, eyesSquint) via procedural sculpt
  4. Weight hygiene: 4-influence cap, normalize, region rules
     (face->Head/Neck, tail->tail/Hips, paws->Hand)

Works in-memory; caller handles I/O (API-direct for binaries).

Requires: numpy, scipy.
"""
import json
import struct

import numpy as np

CT = {5120: np.int8, 5121: np.uint8, 5122: np.int16, 5123: np.uint16,
      5125: np.uint32, 5126: np.float32}
TYPE_COUNTS = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4, 'MAT4': 16}

# Canonical morph set (must match face_morphs.json)
MORPHS = ['blink_L', 'blink_R', 'jawOpen', 'browUp', 'browDown',
          'mouthSmile', 'mouthFrown', 'mouthOpen', 'eyesWide', 'eyesSquint']


def parse_glb(data):
    if data[:4] != b'glTF':
        raise ValueError('not a GLB')
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


def node_matrix(nd):
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
    sx = np.linalg.norm(rs[:, 0]) or 1.0
    sy = np.linalg.norm(rs[:, 1]) or 1.0
    sz = np.linalg.norm(rs[:, 2]) or 1.0
    r = rs / np.array([sx, sy, sz])
    tr = np.trace(r)
    if tr > 0:
        s = np.sqrt(tr + 1.0) * 2
        w, x = 0.25 * s, (r[2, 1] - r[1, 2]) / s
        y, z = (r[0, 2] - r[2, 0]) / s, (r[1, 0] - r[0, 1]) / s
    else:
        x, y, z, w = 0, 0, 0, 1
    n = np.sqrt(x * x + y * y + z * z + w * w) or 1.0
    return t, np.array([x / n, y / n, z / n, w / n]), np.array([sx, sy, sz])


class GLBRepair:
    """In-memory GLB repair context."""

    def __init__(self, data):
        self.js, self.bdat = parse_glb(data)
        self.nodes = self.js['nodes']
        self.name_to_idx = {nd.get('name'): i for i, nd in enumerate(self.nodes)}
        self.parent = {}
        for i, nd in enumerate(self.nodes):
            for c in nd.get('children', []):
                self.parent[c] = i
        self.skin = self.js['skins'][0]
        self.joints = list(self.skin['joints'])
        self.jnames = [self.nodes[j].get('name', '') for j in self.joints]
        self.jidx = {n: i for i, n in enumerate(self.jnames)}
        self.world = {}
        self.bin_parts = [self.bdat]
        self.bin_off = len(self.bdat)
        self.report = []

    def get_world(self, i):
        if i not in self.world:
            lm = node_matrix(self.nodes[i])
            p = self.parent.get(i)
            self.world[i] = lm if p is None else self.get_world(p) @ lm
        return self.world[i]

    def bone_world_pos(self, name):
        idx = self.name_to_idx.get(name)
        if idx is None:
            return None
        return self.get_world(idx)[:3, 3]

    def add_bone(self, name, parent_name, local_matrix):
        """Add a bone; returns new joint index."""
        pidx = self.name_to_idx.get(parent_name)
        if pidx is None:
            raise ValueError(f'parent {parent_name} not found')
        t, q, s = mat_to_trs(local_matrix)
        nidx = len(self.nodes)
        self.nodes.append({
            'name': name,
            'translation': [float(v) for v in t],
            'rotation': [float(v) for v in q],
            'scale': [float(v) for v in s],
        })
        self.name_to_idx[name] = nidx
        pn = self.nodes[pidx]
        pn['children'] = pn.get('children', []) + [nidx]
        self.parent[nidx] = pidx
        self.world[nidx] = self.get_world(pidx) @ node_matrix(self.nodes[nidx])
        self.joints.append(nidx)
        self.jnames.append(name)
        self.jidx[name] = len(self.joints) - 1
        self.skin['joints'] = self.joints
        return len(self.joints) - 1

    def append_array(self, arr, ctype, atype):
        data = np.ascontiguousarray(arr)
        raw = data.tobytes()
        pad = (-len(raw)) % 4
        self.js['bufferViews'].append({
            'buffer': 0, 'byteOffset': self.bin_off,
            'byteLength': len(raw) + pad})
        self.js['accessors'].append({
            'bufferView': len(self.js['bufferViews']) - 1,
            'componentType': ctype, 'type': atype, 'count': data.shape[0]})
        self.bin_parts.append(raw + b'\x00' * pad)
        self.bin_off += len(raw) + pad
        return len(self.js['accessors']) - 1

    def get_skinned_prims(self):
        out = []
        for mesh in self.js['meshes']:
            for prim in mesh['primitives']:
                at = prim['attributes']
                if all(k in at for k in ('POSITION', 'JOINTS_0', 'WEIGHTS_0')):
                    out.append((prim, at))
        return out

    def finalize(self):
        """Write IBMs and serialize to GLB bytes."""
        # Rebuild IBMs for all joints
        ibms = []
        for jnode in self.joints:
            ibms.append(np.linalg.inv(self.get_world(jnode)))
        ibm_arr = np.stack(ibms).astype(np.float32)
        acc = self.append_array(ibm_arr.reshape(-1, 16), 5126, 'MAT4')
        self.js['accessors'][acc]['count'] = len(ibms)
        self.skin['inverseBindMatrices'] = acc
        # Serialize
        total_bin = b''.join(self.bin_parts)
        self.js['buffers'][0]['byteLength'] = len(total_bin)
        jstr = json.dumps(self.js, separators=(',', ':')).encode()
        jpad = (-len(jstr)) % 4
        return (b'glTF' + struct.pack('<I', 2) +
                struct.pack('<I', len(jstr) + jpad) + jstr + b' ' * jpad +
                struct.pack('<I', len(total_bin)) + b'BIN\x00' + total_bin)
