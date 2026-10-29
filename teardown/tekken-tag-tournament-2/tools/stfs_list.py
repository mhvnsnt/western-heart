#!/usr/bin/env python3
"""Parse STFS file table (Free60 spec) and print inner listing."""
import struct, sys

def parse_stfs_table(path, verbose=True):
    d = open(path,'rb').read()
    if d[0:4] not in (b'LIVE', b'PIRS', b'CON '):
        print(f'{path}: not STFS (magic {d[0:4]})'); return []
    hdr_size = struct.unpack('>I', d[0x340:0x344])[0]
    ctype = struct.unpack('>i', d[0x344:0x348])[0]
    vd = 0x379
    ft_count = struct.unpack('<H', d[vd+3:vd+5])[0]
    ft_block = int.from_bytes(d[vd+5:vd+8], 'little')
    # physical: header (rounded) + hash tables interleaved every 0xAA blocks.
    # For ft_block=0: header_end + 0x1000 (first hash table)
    hdr_end = (hdr_size + 0xFFF) & 0xF000
    # hash tables: 1 per 0xAA blocks; blocks before ft_block need their tables
    # simple general: tables_before = ft_block // 0xAA  (+1 for the table covering block 0 if ft_block < 0xAA)
    if ft_block < 0xAA:
        tables = 1
    else:
        tables = 1 + ft_block // 0xAA  # approx; level-1 tables ignored (fine for small tables)
    base = hdr_end + tables*0x1000 + ft_block*0x1000
    if verbose:
        print(f'{path}: len={len(d)} hdr={hdr_size:#x} ctype={ctype:#x} fttable_blocks={ft_count} ft_block={ft_block} table_off={base:#x}')
    entries = []
    i = 0
    while True:
        e = d[base+i*0x40:base+(i+1)*0x40]
        if len(e) < 0x40 or e == b'\x00'*0x40: break
        name = e[0:0x28].split(b'\x00')[0]
        try: nm = name.decode('ascii')
        except: break
        if not nm: break
        flaglen = e[0x28]; namelen = flaglen & 0x3F
        if namelen != len(nm): break  # sanity: stop at garbage
        isdir = bool(flaglen & 0x80)
        nblocks = int.from_bytes(e[0x29:0x2C], 'little')
        startblk = int.from_bytes(e[0x2F:0x32], 'little')
        pathind = struct.unpack('>H', e[0x32:0x34])[0]
        size = struct.unpack('>I', e[0x34:0x38])[0]
        entries.append((nm, size, nblocks, startblk, isdir, pathind))
        i += 1
        if i > 5000: break
    return entries

if __name__ == '__main__':
    for p in sys.argv[1:]:
        es = parse_stfs_table(p)
        for nm, size, nb, sb, isdir, pi in es:
            print(f'  {"<DIR>" if isdir else "     "} {nm}  size={size} blocks={nb} start={sb} pathind={pi:#x}')
        print(f'  total entries: {len(es)}')
