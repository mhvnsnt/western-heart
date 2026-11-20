#!/usr/bin/env python3
"""Enumerate BD directory entries inside one BDPK container.
BD entry: magic 'BD' + u16 type + u32 X + u32 Y + up to 12 bytes, then a
filename (from the known name set) + NUL. Name location found by search.
Usage: bd_enumerate.py <chunk_offset_hex>"""
import struct, sys, json
data = open('/home/hatch/workspace/devil-within-decode/raw/TK5DATA2.BIN','rb').read()
names = set()
for line in open('/home/hatch/workspace/devil-within-decode/repo/teardown/tekken5/t5_motion_manifest.txt'):
    names.add(line.strip())
blocks = json.load(open('/home/hatch/workspace/devil-within-decode/raw/romd_blocks.json'))
for b in blocks:
    names.update(b['names'])
bare = set(n[:-4] if n.endswith('.dat') else n for n in names)
off = int(sys.argv[1], 16)
assert data[off:off+4] == b'BDPK', f'no BDPK magic at {off:#x}: {data[off:off+4]!r}'
a, b = struct.unpack_from('<II', data, off+4)
print(f'container @{off:#x} A={a} B={b} payload {off+12:#x}..{off+12+b:#x}')
pstart, pend = off+12, off+12+b
entries = []
pos = pstart
while True:
    p = data.find(b'BD', pos, pend)
    if p < 0: break
    if p+12 <= pend:
        typ = struct.unpack_from('<H', data, p+2)[0]
        x, y = struct.unpack_from('<II', data, p+4)
        # search for a known bare name + NUL starting within [p+12, p+40)
        for q in range(p+12, min(p+40, pend)):
            if data[q] == 0:
                continue  # zero padding / header zeros
            nul = data.find(b'\x00', q, min(q+64, pend))
            if nul < 0: break
            nm_b = data[q:nul]
            if len(nm_b) < 3:
                continue  # short fragment, header/binary
            if not all(32 <= ch < 127 for ch in nm_b):
                continue  # binary fragment, keep looking
            nm = nm_b.decode('ascii')
            if nm in bare:
                entries.append({'bd': p, 'name_off': q, 'type': typ, 'x': x, 'y': y, 'name': nm})
                break
            break  # long printable run, not a known name: not this BD's name
    pos = p+1
print(f'validated BD entries: {len(entries)} (A={a})')
for i, e in enumerate(entries):
    nxt = entries[i+1]['bd'] if i+1 < len(entries) else pend
    print(f"  BD @{e['bd']:#x} name@{e['name_off']:#x} hdr={e['name_off']-e['bd']} type={e['type']} X={e['x']} Y={e['y']} name={e['name']} span_to_next={nxt-e['bd']}")
