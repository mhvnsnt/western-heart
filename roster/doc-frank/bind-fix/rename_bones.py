#!/usr/bin/env python3
"""Rename skin-joint nodes in a GLB to the canonical names of its verified
structural twin (same skeleton, index-aligned). BIN chunk untouched.
usage: rename_bones.py <target.glb> <twin.glb>"""
import json, struct, sys

def load(path):
    d = open(path, 'rb').read()
    assert d[:4] == b'glTF'
    jlen = struct.unpack('<I', d[12:16])[0]
    gltf = json.loads(d[20:20 + jlen])
    off = 20 + jlen
    blen = struct.unpack('<I', d[off:off + 4])[0]
    return gltf, bytearray(d[off + 8: off + 8 + blen]), d

tgt_path, twin_path = sys.argv[1], sys.argv[2]
a, bin_chunk, orig = load(tgt_path)
b, _, _ = load(twin_path)
ja, jb = a['skins'][0]['joints'], b['skins'][0]['joints']
assert len(ja) == len(jb)
renamed = []
for x, y in zip(ja, jb):
    old, new = a['nodes'][x].get('name'), b['nodes'][y].get('name')
    if old != new:
        renamed.append((old, new))
        a['nodes'][x]['name'] = new
print(f"renamed {len(renamed)} joint nodes")
for o, n in renamed[:8]: print(f"  {o!r} -> {n!r}")

js = json.dumps(a, separators=(',', ':')).encode('utf8')
js += b' ' * ((4 - len(js) % 4) % 4)
total = 12 + 8 + len(js) + 8 + len(bin_chunk)
out = bytearray()
out += b'glTF' + struct.pack('<II', 2, total)
out += struct.pack('<I', len(js)) + b'JSON' + js
out += struct.pack('<I', len(bin_chunk)) + b'BIN\x00' + bin_chunk
open(tgt_path, 'wb').write(bytes(out))
print("wrote", tgt_path, len(out), "bytes (orig", len(orig), ")")
