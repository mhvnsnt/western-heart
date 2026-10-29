#!/usr/bin/env python3
"""Round 4 (recovery lane): container header/manifest field test.
Compares all 76 GZIP containers, PASS (byte-exact idx set from round 3)
vs FAIL, across: header words w[0..4], prefix16 presence/values, zlib
header bytes, manifest layout/magic, compressed/uncompressed sizes.
Verdict (2026-10-21): NO field separates PASS from FAIL. w[1]=w[2]=1 and
zlib header 78da for all 76; prefix16 and layout occur in both sets.
The ONLY systematic split is SIZE: every PASS container is tiny
(uncompressed 336..1088, file 80..144 bytes); every FAIL container is
>=9,040 uncompressed / >=7,104 file bytes. Full per-index table was
printed by this script during the run (see ROUND4-STATUS.md F4).
"""
import json, struct, collections
ROOT = '/home/hatch/workspace/_t6r4-work/recon/x/tekken6/work/decrypt3'
man = json.load(open(f'{ROOT}/manifest.json'))
bulk = open(f'{ROOT}/bulk_decrypted.bin', 'rb')
gz = [f for f in man['files'] if f['magic'].startswith('GZIP')]
exact = {19, 23, 25, 27, 29, 31, 33, 35, 37, 39, 41, 43, 45, 47, 49, 51, 53, 55, 56, 57}
for i, f in enumerate(gz):
    bulk.seek(f['start_rel'] * 2048); d = bulk.read(f['size'])
    pre = None
    if f['magic'] == 'GZIP+prefix16':
        pre = struct.unpack('<4I', d[:16]); d = d[16:]
    w = struct.unpack('<5I', d[:20])
    print(f"idx{i:2d} {'PASS' if i in exact else 'FAIL'} entry{f['entry']} sub{f['sub']} "
          f"magic={f['magic']} layout={f['layout']} size={f['size']} w={w} pre={pre} zh={d[20:22].hex()}")
