#!/usr/bin/env python3
"""Round 11 Job 5b: scan all 40 idx24 slot-9 pages: density, structure."""
import struct, os, glob
import numpy as np

DEC = '/home/hatch/workspace/_t6r4-work/decoded76'

def slots_of(data):
    n, hs = struct.unpack_from('<II', data, 0)
    out = []; start = hs
    for i in range(n):
        sz, end = struct.unpack_from('<II', data, 8 + i * 8)
        out.append((start, sz)); start = end if end else start
    return out

f = glob.glob(os.path.join(DEC, 'idx24_*.bin'))[0]
data = open(f, 'rb').read()
off, sz = slots_of(data)[9]
slot9 = data[off:off + sz]
pairs = [struct.unpack_from('>II', slot9, 0x78 + 8 * i) for i in range(40)]
pages = [slot9[o:o + s] for s, o in pairs]
for i, pg in enumerate(pages):
    nz = np.count_nonzero(np.frombuffer(pg, dtype=np.uint8))
    u = np.frombuffer(pg, dtype='>u4')
    fnz = next((j for j, b in enumerate(pg) if b != 0), -1)
    print(f'page {i:2d}: nonzero bytes {nz:4d}/2208 ({nz/2208:.0%}) first_nz={fnz} u32[13:17]={[hex(x) for x in u[13:17]]}')
# identical pages?
import collections
h = collections.Counter(hash(p) for p in pages)
print('unique pages:', len(h))
# where is the bulk of nonzero data in slot9 overall?
arr = np.frombuffer(slot9, dtype=np.uint8)
print('slot9 nonzero fraction:', np.count_nonzero(arr) / len(arr))
# check the 448B head region and embedded NTPP
print('head hex 0x1b0..0x200:', slot9[0x1b0:0x200].hex())
print('NTPP magic at:', slot9.find(b'NTPP'))
