#!/usr/bin/env python3
"""Phase 11 Job 2d: neck-junction measurement from the GLBs themselves.
headBottom = low percentile Y of dominant-joint verts in the center
column (|x|<=0.04). bodyTop = high percentile Y of body verts in the
center column (|x|<=0.06). anchor = bodyTop - headBottom + overlap.
Validated against the phase-10 seated pairs before use on floaters."""
import json, struct, os
import numpy as np

def load_glb(path):
    d = open(path, 'rb').read()
    jlen = struct.unpack_from('<I', d, 12)[0]
    g = json.loads(d[20:20 + jlen])
    off = 20 + jlen
    blen = struct.unpack_from('<I', d, off)[0]
    return g, d[off + 8: off + 8 + blen]

def acc(g, bin_, idx):
    a = g['accessors'][idx]
    bv = g['bufferViews'][a['bufferView']]
    start = bv.get('byteOffset', 0) + a.get('byteOffset', 0)
    ncomp = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4, 'MAT4': 16}[a['type']]
    dt = {5126: np.float32, 5123: np.uint16, 5125: np.uint32, 5121: np.uint8}[a['componentType']]
    stride = bv.get('byteStride')
    raw = np.frombuffer(bin_, dtype=dt, offset=start, count=a['count'] * ncomp)
    if stride and stride != ncomp * np.dtype(dt).itemsize:
        raw = np.lib.stride_tricks.as_strided(
            np.frombuffer(bin_, dtype=np.uint8, offset=start),
            shape=(a['count'], ncomp), strides=(stride, np.dtype(dt).itemsize)).copy().ravel()
    return raw.reshape(a['count'], ncomp)

def head_bottom(path):
    g, bin_ = load_glb(path)
    joints = g['skins'][0]['joints']
    mass = np.zeros(len(joints))
    chunks = []
    for m in g.get('meshes', []):
        for pr in m['primitives']:
            J = acc(g, bin_, pr['attributes']['JOINTS_0']).astype(np.int64)
            W = acc(g, bin_, pr['attributes']['WEIGHTS_0']).astype(np.float64)
            for k in range(4):
                ok = J[:, k] < len(joints)
                np.add.at(mass, J[ok, k], W[ok, k])
    dom = int(np.argmax(mass))
    ys = []
    for m in g.get('meshes', []):
        for pr in m['primitives']:
            P = acc(g, bin_, pr['attributes']['POSITION']).astype(np.float64)
            J = acc(g, bin_, pr['attributes']['JOINTS_0']).astype(np.int64)
            W = acc(g, bin_, pr['attributes']['WEIGHTS_0']).astype(np.float64)
            okp = np.isfinite(P).all(axis=1) & (np.abs(P) < 10).all(axis=1)
            wdom = np.zeros(len(P))
            for k in range(4):
                sel = (J[:, k] == dom)
                wdom[sel] = np.maximum(wdom[sel], W[sel, k])
            sel = okp & (wdom >= 0.5) & (np.abs(P[:, 0]) <= 0.04)
            ys.append(P[sel, 1])
    ys = np.concatenate(ys)
    return float(np.percentile(ys, 1)), float(np.percentile(ys, 5)), len(ys)

def body_top(path):
    g, bin_ = load_glb(path)
    ys = []
    for m in g.get('meshes', []):
        for pr in m['primitives']:
            P = acc(g, bin_, pr['attributes']['POSITION']).astype(np.float64)
            okp = np.isfinite(P).all(axis=1) & (np.abs(P) < 10).all(axis=1)
            sel = okp & (np.abs(P[:, 0]) <= 0.06)
            ys.append(P[sel, 1])
    ys = np.concatenate(ys)
    return float(np.percentile(ys, 99)), float(np.percentile(ys, 99.9)), float(ys.max()), len(ys)

HD = '/home/hatch/workspace/_doa4p2-scratch/p9/glb-chrtwo/extracted'
B1 = '/home/hatch/workspace/_doa4p2-scratch/p8/glb-chrone/extracted'
B2 = HD
pairs = [  # body, head, phase10 anchorY (nb), verdict
    ('chrone-pkg00', 'chrtwo-pkg29', 0.406, 'SEATED'), ('chrone-pkg00', 'chrtwo-pkg17', 0.406, 'SEATED'),
    ('chrone-pkg10', 'chrtwo-pkg08', 0.398, 'SEATED'), ('chrone-pkg17', 'chrtwo-pkg04', 0.388, 'SEATED'),
    ('chrtwo-pkg50', 'chrtwo-pkg41', 0.397, 'SEATED'), ('chrone-pkg14', 'chrtwo-pkg11', 0.501, 'SEATED'),
    ('chrone-pkg10', 'chrtwo-pkg09', 0.398, 'FLOAT'), ('chrone-pkg10', 'chrtwo-pkg33', 0.398, 'FLOAT'),
    ('chrone-pkg00', 'chrtwo-pkg18', 0.406, 'FLOAT'), ('chrone-pkg00', 'chrtwo-pkg20', 0.406, 'FLOAT'),
    ('chrone-pkg17', 'chrtwo-pkg21', 0.388, 'FLOAT'), ('chrtwo-pkg50', 'chrtwo-pkg25', 0.397, 'FLOAT'),
    ('chrone-pkg17', 'chrtwo-pkg07', 0.388, 'MARG'),
]
tops = {}
for body, head, nb, verdict in pairs:
    bp = os.path.join(B1, body + '-skinned.glb')
    if not os.path.exists(bp): bp = os.path.join(B2, body + '-skinned.glb')
    if body not in tops: tops[body] = body_top(bp)
    hb1, hb5, nh = head_bottom(os.path.join(HD, head + '-skinned.glb'))
    bt99, bt999, btmax, nb_ = tops[body]
    anchor = bt999 - hb1
    print('%-28s %-13s %-6s bodyTop99.9=%.3f headBot1=%.3f headBot5=%.3f -> anchor=%.3f (phase10 nb=%.3f, delta=%+.3f)' % (
        body + '+' + head, head, verdict, bt999, hb1, hb5, anchor, nb, anchor - nb))
