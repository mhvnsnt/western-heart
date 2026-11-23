#!/usr/bin/env python3
"""W6 probe: map ring.ymg / 00.ymg structure — header, vert arrays,
20-byte face-record locations, other separator patterns."""
import sys, struct
sys.path.insert(0, '/data/wmxix/tools-src/tools')
from yobj_arena_extract import find_vert_arrays

BG = '/data/wmxix/extracted/bg'


def u16(d, o):
    return struct.unpack('>H', d[o:o + 2])[0]


def u32(d, o):
    return struct.unpack('>I', d[o:o + 4])[0]


def f32(d, o):
    return struct.unpack('>f', d[o:o + 4])[0]


def probe(name):
    with open(f'{BG}/{name}', 'rb') as f:
        d = f.read()
    size = len(d)
    print(f'=== {name} size={size} magic={d[:4]!r} ver={u32(d, 8):#x}')
    if d[:4] == b'YOBJ':
        for off, lbl in ((0x10, 'bones'), (0x14, 'skel'), (0x18, 'mats'),
                         (0x54, 'base'), (0x5c, 't1'), (0x60, 'skin')):
            print(f'  {lbl} @0x{off:x} = {u32(d, off):#x}')
        # header strings at 0x20..0x54?
        print(f'  hdr 0x20..0x54: {d[0x20:0x54]!r}')
    arrays = find_vert_arrays(d, size)
    print(f'  vert arrays: {len(arrays)} total={sum(n for _, n in arrays)}')
    for s, n in arrays[:12]:
        print(f'    @0x{s:x} n={n}')
    # where are the 20-byte face records?
    recs = []
    o = 0x80
    while o < size - 20:
        if (u32(d, o + 6) == 0xFFFFFFFF and u32(d, o + 16) == 0xFFFFFFFF):
            recs.append(o)
            o += 20
        else:
            o += 2
    print(f'  20-byte records: {len(recs)}')
    if recs:
        print(f'    first @0x{recs[0]:x} last @0x{recs[-1]:x}')
        # cluster them
        clusters = [[recs[0]]]
        for r in recs[1:]:
            if r - clusters[-1][-1] <= 40:
                clusters[-1].append(r)
            else:
                clusters.append([r])
        print(f'    clusters: {len(clusters)} sizes='
              f'{[len(c) for c in clusters][:20]}')
        for c in clusters[:6]:
            print(f'      cluster @0x{c[0]:x}..0x{c[-1]:x} n={len(c)}')
    # other separator candidates: count FFFFFFFF occurrences
    ff = d.count(b'\xff\xff\xff\xff')
    print(f'  total 0xFFFFFFFF occurrences: {ff}')
    # count 0x00000000 runs >= 8 bytes (possible separators)
    z = d.count(b'\x00' * 8)
    print(f'  8-zero-byte runs: {z}')
    # sample the bytes right after the last vert array and before first record
    if arrays and recs:
        print(f'  gap bytes vert_end..first_rec: '
              f'{d[arrays[0][0] + arrays[0][1] * 12:arrays[0][0] + arrays[0][1] * 12 + 64].hex()}')
    # print a few raw records
    for r in recs[:3]:
        print(f'  rec @0x{r:x}: {d[r:r + 20].hex()} '
              f'a={u16(d, r)} b={u16(d, r + 2)} c={u16(d, r + 4)} '
              f'base={u16(d, r + 10)} d={u16(d, r + 12)} e={u16(d, r + 14)}')


if __name__ == '__main__':
    for name in sys.argv[1:] or ['ring.ymg']:
        probe(name)
