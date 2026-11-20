#!/usr/bin/env python3
"""Patch JOINTS_0/WEIGHTS_0 of a GLB in place from diffuse_weights.py
banks (<prefix>.joints.npy / <prefix>.weights.npy). Byte-level: only
the two attribute arrays are rewritten; nodes, animations, geometry
untouched. Usage: patch_skin.py <in.glb> <bankprefix> <out.glb>"""
import json
import struct
import sys

import numpy as np


def main():
    inp, prefix, outp = sys.argv[1], sys.argv[2], sys.argv[3]
    joints = np.load(prefix + '.joints.npy')
    weights = np.load(prefix + '.weights.npy')
    d = bytearray(open(inp, 'rb').read())
    ln = struct.unpack('<I', d[12:16])[0]
    js = json.loads(bytes(d[20:20 + ln]))
    bin_off = 20 + ln + 8
    prim = js['meshes'][0]['primitives'][0]

    def patch(attr, arr, dtype):
        ai = prim['attributes'][attr]
        a = js['accessors'][ai]
        bv = js['bufferViews'][a['bufferView']]
        o = bin_off + bv.get('byteOffset', 0) + a.get('byteOffset', 0)
        stride = bv.get('byteStride')
        flat = arr.astype(dtype).reshape(-1)
        if stride and stride != arr.dtype.itemsize * arr.shape[1]:
            # interleaved: write row by row
            row = arr.astype(dtype)
            rb = row.tobytes()
            rlen = row.shape[1] * row.dtype.itemsize
            for i in range(len(row)):
                d[o + i * stride:o + i * stride + rlen] = \
                    rb[i * rlen:(i + 1) * rlen]
        else:
            b = flat.tobytes()
            d[o:o + len(b)] = b
        print('patched', attr, 'count', a['count'], 'at', o)

    ja = js['accessors'][prim['attributes']['JOINTS_0']]
    jdt = {5121: np.uint8, 5123: np.uint16, 5125: np.uint32}[
        ja['componentType']]
    patch('JOINTS_0', joints, jdt)
    patch('WEIGHTS_0', weights, np.float32)
    open(outp, 'wb').write(bytes(d))
    print('PATCH_OK', outp)


if __name__ == '__main__':
    main()
