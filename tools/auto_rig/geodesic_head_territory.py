#!/usr/bin/env python3
"""Geodesic head territory for Negativo's GameRig re-rig (PR #1461 recipe step 2).

Weld UV seams by position, seed above the Head joint, grow along mesh edges,
block the neck cylinder / arm+clavicle flesh / anything below Spine2, and set
every claimed vert to Head 1.0 — so hair spikes that hang below the neck stay
whole on the head instead of tearing (the 2026-10-31 height-cutoff failure).
Blocked verts may be traversed only when already Head/HeadTop-dominant (hair).
Patches JOINTS_0/WEIGHTS_0 in place; geometry untouched.
"""
import json, struct, sys
from collections import deque
import numpy as np

SRC, DST = sys.argv[1], sys.argv[2]
raw = bytearray(open(SRC, 'rb').read())
jlen = struct.unpack('<I', raw[12:16])[0]
js = json.loads(raw[20:20 + jlen])
boff = 20 + jlen + 8
blen = struct.unpack('<I', raw[20 + jlen:24 + jlen])[0]
bdat = memoryview(raw)[boff:boff + blen]

COMP = {5121: ('B', 1), 5123: ('H', 2), 5125: ('I', 4), 5126: ('f', 4)}
NCOMP = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4, 'MAT4': 16}

def acc_arr(ai):
    acc = js['accessors'][ai]
    bv = js['bufferViews'][acc['bufferView']]
    off = bv.get('byteOffset', 0) + acc.get('byteOffset', 0)
    fmt, sz = COMP[acc['componentType']]
    n = NCOMP[acc['type']]
    stride = bv.get('byteStride', sz * n)
    cnt = acc['count']
    if stride == sz * n:
        return np.frombuffer(bdat, dtype=np.dtype(fmt), count=cnt * n,
                             offset=off).reshape(cnt, n).copy(), acc, off, fmt, sz, n, stride
    out = np.empty((cnt, n), dtype=np.dtype(fmt))
    for i in range(cnt):
        out[i] = np.frombuffer(bdat, dtype=np.dtype(fmt), count=n,
                               offset=off + i * stride)
    return out, acc, off, fmt, sz, n, stride

def node_worlds():
    import math
    def local(n):
        if 'matrix' in n:
            return np.array(n['matrix'], dtype=np.float64).reshape(4, 4).T
        t = n.get('translation', [0, 0, 0]); s = n.get('scale', [1, 1, 1])
        q = n.get('rotation', [0, 0, 0, 1])
        x, y, z, w = q
        R = np.array([
            [1-2*(y*y+z*z), 2*(x*y-z*w), 2*(x*z+y*w)],
            [2*(x*y+z*w), 1-2*(x*x+z*z), 2*(y*z-x*w)],
            [2*(x*z-y*w), 2*(y*z+x*w), 1-2*(x*x+y*y)]], dtype=np.float64)
        M = np.eye(4); M[:3, :3] = R * np.array(s); M[:3, 3] = t
        return M
    worlds = {}
    def walk(idx, parent):
        w = parent @ local(js['nodes'][idx])
        worlds[idx] = w
        for c in js['nodes'][idx].get('children', []):
            walk(c, w)
    for s in js['scenes'][js.get('scene', 0)]['nodes']:
        walk(s, np.eye(4))
    return worlds

worlds = node_worlds()
skin = js['skins'][0]
names = [js['nodes'][j].get('name', '') for j in skin['joints']]
jpos = {}
mesh_node = None
for mi, m in enumerate(js['meshes']):
    for ni, n in enumerate(js['nodes']):
        if n.get('mesh') == mi and 'skin' in n:
            mesh_node = ni
minv = np.linalg.inv(worlds[mesh_node])
for nm, j in zip(names, skin['joints']):
    p = (minv @ worlds[j])[:3, 3]
    jpos[nm] = p
print('joints:', {k: np.round(v, 3).tolist() for k, v in jpos.items()
                  if k in ('Hips', 'Spine2', 'Neck', 'Head', 'HeadTop',
                           'LeftShoulder', 'RightShoulder', 'LeftArm', 'RightArm')})

prim = js['meshes'][0]['primitives'][0]
pos, *_ = acc_arr(prim['attributes']['POSITION'])
jnts, jacc, joff, jfmt, jsz, jn, jstride = acc_arr(prim['attributes']['JOINTS_0'])
wgts, wacc, woff, wfmt, wsz, wn, wstride = acc_arr(prim['attributes']['WEIGHTS_0'])
idx, *_ = acc_arr(prim['indices']) if 'indices' in prim else (None,)
idx = idx.reshape(-1)
wnorm = wgts.astype(np.float64)
if wfmt == 'B': wnorm /= 255.0
elif wfmt == 'H': wnorm /= 65535.0
dom = jnts[np.arange(len(jnts)), np.argmax(wnorm, axis=1)]
name_of = np.array(names)

# weld by position (1e-4)
key = np.round(pos / 1e-4).astype(np.int64)
_, rep, winv = np.unique(key, axis=0, return_index=True, return_inverse=True)
if winv.ndim > 1:  # numpy>=2 returns inverse shaped like input rows
    winv = winv.reshape(-1)
wpos = pos[rep]
nw = len(wpos)
print(f'verts {len(pos)} -> welded {nw}')
wdom = dom[rep].copy()

# edges on welded ids
tris = idx.reshape(-1, 3)
wt = winv[tris]
e = np.concatenate([wt[:, [0, 1]], wt[:, [1, 2]], wt[:, [2, 0]]])
e = np.unique(np.sort(e, axis=1), axis=0)
adj = [[] for _ in range(nw)]
for a, b in e:
    adj[a].append(b); adj[b].append(a)

head = names.index('Head'); headtop = names.index('HeadTop')
neck_i = names.index('Neck')
up = jpos['Head'] - jpos['Neck']; up /= np.linalg.norm(up)
spine2 = jpos['Spine2']
# NOTE: this skeleton's Shoulder (clavicle) joints sit at x +/-0.017 (sternum);
# the recipe's "half shoulder span" is measured on the Arm joints (x +/-0.179),
# giving a usable neck radius (~0.063 m) instead of a useless 6 mm.
half_span = np.linalg.norm(jpos['LeftArm'] - jpos['RightArm']) / 2.0
neck_r = 0.35 * half_span
ua_l = np.linalg.norm(jpos['LeftForeArm'] - jpos['LeftArm'])
ua_r = np.linalg.norm(jpos['RightForeArm'] - jpos['RightArm'])
arm_r = 0.35 * max(ua_l, ua_r)

def seg_dist(p, a, b):
    ab = b - a; t = np.clip(np.dot(p - a, ab) / np.dot(ab, ab), 0, 1)
    return np.linalg.norm(p - (a + t * ab))

blocked = np.zeros(nw, dtype=bool)
for i, p in enumerate(wpos):
    if np.dot(p - spine2, up) < 0:
        blocked[i] = True; continue
    if np.dot(p - jpos['Neck'], up) < 0:
        d = seg_dist(p, spine2, jpos['HeadTop'])
        if d < neck_r:
            blocked[i] = True; continue
    if seg_dist(p, jpos['LeftShoulder'], jpos['LeftForeArm']) < arm_r or \
       seg_dist(p, jpos['RightShoulder'], jpos['RightForeArm']) < arm_r:
        blocked[i] = True; continue
    if name_of[wdom[i]] in ('LeftShoulder', 'RightShoulder', 'LeftArm', 'RightArm',
                            'LeftForeArm', 'RightForeArm', 'LeftBreast', 'RightBreast'):
        blocked[i] = True

seed = np.zeros(nw, dtype=bool)
for i, p in enumerate(wpos):
    if np.dot(p - jpos['Head'], up) > -0.01 or wdom[i] in (head, headtop):
        seed[i] = True
seed &= ~blocked | np.isin(wdom, [head, headtop])

terr = np.zeros(nw, dtype=bool)
dq = deque()
for i in np.nonzero(seed)[0]:
    terr[i] = True; dq.append(i)
while dq:
    i = dq.popleft()
    for j in adj[i]:
        if terr[j]:
            continue
        if blocked[j] and wdom[j] not in (head, headtop):
            continue
        terr[j] = True; dq.append(j)
print(f'territory welded verts: {terr.sum()} ({100.0 * terr.sum() / nw:.2f}%)')

newj = jnts.copy(); neww = wnorm.copy()
claim = terr[winv]
newj[claim] = 0
newj[claim, 0] = head
neww[claim] = 0.0; neww[claim, 0] = 1.0
rs = neww.sum(axis=1, keepdims=True); rs[rs == 0] = 1
neww /= rs
# top-4 already satisfied (<=4 influences by construction)

def write_back(arr, off, fmt, sz, n, stride, cnt, scale=None):
    vals = arr
    if scale:
        vals = np.round(arr * scale)
    vals = vals.astype(np.dtype(fmt))
    base = boff + off
    if stride == sz * n:
        raw[base:base + cnt * n * sz] = vals.tobytes()
    else:
        for i in range(cnt):
            raw[base + i * stride: base + i * stride + n * sz] = vals[i].tobytes()

scale = 255.0 if wfmt == 'B' else (65535.0 if wfmt == 'H' else None)
write_back(newj, joff, jfmt, jsz, jn, jstride, len(newj))
write_back(neww, woff, wfmt, wsz, wn, wstride, len(neww), scale)
open(DST, 'wb').write(bytes(raw))
print('wrote', DST)
