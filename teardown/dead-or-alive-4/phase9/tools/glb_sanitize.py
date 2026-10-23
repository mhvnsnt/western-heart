#!/usr/bin/env python3
"""Phase 9: render-copy sanitizer for phase-6 GLBs whose JOINTS_0 contains
out-of-range indices (Blender's glTF importer crashes on them: IndexError
65535 vs skin joint count). Reads stride-aware, clamps any joint index
>= skin joint count to 0 IN A COPY (source GLBs untouched), reports how
many entries were clamped and their total weight (proof the clamped
entries carried no real skinning). Usage: glb_sanitize.py in.glb out.glb"""
import json, struct, sys
import numpy as np

src, dst = sys.argv[1], sys.argv[2]
d = bytearray(open(src, 'rb').read())
jlen = struct.unpack_from('<I', d, 12)[0]
g = json.loads(d[20:20+jlen])
off = 20 + jlen
blen = struct.unpack_from('<I', d, off)[0]
bin_start = off + 8
bin_ = bytes(d[bin_start:bin_start+blen])
njoints = len(g['skins'][0]['joints'])

def acc_view(idx):
    a = g['accessors'][idx]
    bv = g['bufferViews'][a['bufferView']]
    start = bv.get('byteOffset', 0) + a.get('byteOffset', 0)
    ncomp = {'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']]
    dt = {5126:np.float32,5123:np.uint16,5125:np.uint32,5121:np.uint8}[a['componentType']]
    stride = bv.get('byteStride')
    raw = np.frombuffer(bin_, dtype=dt, count=a['count']*ncomp, offset=start)
    if stride and stride != ncomp*np.dtype(dt).itemsize:
        raw = np.lib.stride_tricks.as_strided(
            np.frombuffer(bin_, dtype=np.uint8, offset=start),
            shape=(a['count'], ncomp), strides=(stride, np.dtype(dt).itemsize)).copy().ravel()
    return a, bv, start, raw.reshape(a['count'], ncomp), np.dtype(dt), stride

total_clamped = 0
total_weight = 0.0
for m in g['meshes']:
    for pr in m['primitives']:
        ja, jbv, jstart, J, jdt, jstride = acc_view(pr['attributes']['JOINTS_0'])
        wa, wbv, wstart, W, wdt, wstride = acc_view(pr['attributes']['WEIGHTS_0'])
        bad = J >= njoints
        if bad.any():
            total_clamped += int(bad.sum())
            total_weight += float(W[bad].sum())
            J2 = J.copy(); J2[bad] = 0
            # write back respecting stride
            if jstride and jstride != J2.shape[1]*jdt.itemsize:
                buf = np.frombuffer(d, dtype=np.uint8, count=jbv['byteLength'], offset=bin_start + jbv.get('byteOffset',0)).copy()
                view = np.lib.stride_tricks.as_strided(buf, shape=J2.shape, strides=(jstride, jdt.itemsize))
                view[...] = J2.astype(jdt)
                d[bin_start + jbv.get('byteOffset',0): bin_start + jbv.get('byteOffset',0) + jbv['byteLength']] = buf.tobytes()
            else:
                d[bin_start+jstart: bin_start+jstart + J2.size*jdt.itemsize] = J2.astype(jdt).tobytes()
print(f"joints={njoints} clamped_entries={total_clamped} clamped_weight_sum={total_weight:.6f}")
open(dst, 'wb').write(bytes(d))
print("wrote", dst)
