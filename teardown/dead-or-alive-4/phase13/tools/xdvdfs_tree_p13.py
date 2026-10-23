#!/usr/bin/env python3
"""DOA4 phase 13 Job 1: dump the FULL XDVDFS tree of the assembled ISO
(or of part_01 alone — the directory region sits at the partition
start). Uses the documented DOA4 layout (tools/extract_iso.py):
partition base 0x390000, magic at +0x10000, sector 2048.
Outputs a JSON tree with {path, sector, size, is_dir, iso_offset} and
prints every entry. Read-only.
"""
import json, struct, sys

SECTOR = 2048
MAGIC = b'MICROSOFT*XBOX*MEDIA'

def parse_dir(data):
    entries = []
    stack = [0]; visited = set()
    while stack:
        off = stack.pop()
        if off in visited or off + 14 > len(data):
            continue
        visited.add(off)
        left, right = struct.unpack_from('<HH', data, off)
        start, size = struct.unpack_from('<II', data, off + 4)
        attrs = data[off + 12]; nlen = data[off + 13]
        if nlen == 0 or off + 14 + nlen > len(data):
            continue
        name = data[off + 14:off + 14 + nlen].decode('ascii', 'replace')
        entries.append({'name': name, 'sector': start, 'size': size,
                        'is_dir': bool(attrs & 0x10), 'attrs': attrs})
        if left and left * 4 < len(data):
            stack.append(left * 4)
        if right and right * 4 < len(data):
            stack.append(right * 4)
    return entries

def walk(f, base, sector, size, prefix, out):
    f.seek(base + sector * SECTOR)
    data = f.read(size)
    for e in parse_dir(data):
        path = f"{prefix}{e['name']}"
        e['path'] = path
        e['iso_offset'] = base + e['sector'] * SECTOR
        out.append(e)
        if e['is_dir']:
            walk(f, base, e['sector'], e['size'], path + '/', out)

def find_magic(f):
    """Scan the first 512MB for the XDVDFS volume descriptor magic.
    Phase-13 correction: the early-phase docs place the partition at
    0x390000 (magic 0x3A0000), but the verified part_01 bytes carry
    DVD-video data there and NO magic in [0, 262MB) — the standard
    XGD2 game partition (base 0x0FD90000, magic at +0x10000 =
    0x0FDA0000, just past part_01's end) is the layout to test."""
    f.seek(0)
    pos = 0
    while pos < (1 << 29):
        chunk = f.read(1 << 22)
        if not chunk:
            return None
        i = chunk.find(MAGIC)
        if i >= 0:
            return pos + i
        pos += len(chunk) - 20
        f.seek(pos)
    return None

def main():
    path = sys.argv[1]
    with open(path, 'rb') as f:
        moff = find_magic(f)
        assert moff is not None, 'MAGIC not found in scanned span'
        base = moff - 0x10000
        f.seek(moff + 20)
        root_sector, root_size = struct.unpack('<II', f.read(8))
        print(f'MAGIC at 0x{moff:X}; partition base 0x{base:X} root sector {root_sector} size {root_size}')
        out = []
        walk(f, base, root_sector, root_size, '', out)
        for e in out:
            kind = 'DIR ' if e['is_dir'] else 'FILE'
            print(f"{kind} {e['path']}  size={e['size']} sector={e['sector']} iso_off=0x{e['iso_offset']:X}")
        print('TOTAL entries:', len(out))
        json.dump(out, open('/home/hatch/workspace/_doa4p2-scratch/p13/xdvdfs_tree.json', 'w'), indent=1)

if __name__ == '__main__':
    main()
