#!/usr/bin/env python3
"""List contents of CRIWARE AFS archives (PS2-era). Read-only.
Usage: python3 afs_list.py <file.afs> [out.txt]
"""
import sys, struct, os

def parse_afs(path):
    size = os.path.getsize(path)
    with open(path, 'rb') as f:
        magic = f.read(4)
        if magic != b'AFS\x00':
            raise ValueError(f'{path}: not an AFS archive (magic={magic!r})')
        count = struct.unpack('<I', f.read(4))[0]
        entries = []
        for _ in range(count):
            off, sz = struct.unpack('<II', f.read(8))
            entries.append((off, sz))
        # filename table pointer
        nt_off, nt_size = struct.unpack('<II', f.read(8))
        names = []
        if nt_off and nt_size:
            f.seek(nt_off)
            raw = f.read(nt_size)
            for i in range(count):
                chunk = raw[i*48:(i+1)*48] if len(raw) >= (i+1)*48 else raw[i*32:(i+1)*32]
                # try 48-byte then 32-byte name fields
                nm = chunk.split(b'\x00')[0].decode('ascii', 'replace')
                names.append(nm)
        else:
            names = [f'file_{i:05d}.bin' for i in range(count)]
        return [(names[i] if i < len(names) else f'file_{i:05d}.bin', e[0], e[1])
                for i, e in enumerate(entries)], size, count

def main():
    path = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else None
    entries, fsize, count = parse_afs(path)
    lines = [f'# AFS: {path}', f'# archive size: {fsize:,} bytes, files: {count}', '']
    total = 0
    for name, off, sz in entries:
        total += sz
        lines.append(f'{sz:>12,}  @{off:>12,}  {name}')
    lines.append('')
    lines.append(f'# payload total: {total:,} bytes')
    text = '\n'.join(lines)
    if out:
        open(out, 'w').write(text)
        print(f'Wrote {out} ({count} files)')
    else:
        # print summary + top 30 largest
        print(f'{path}: {count} files, {fsize:,} bytes')
        print('--- 30 largest ---')
        for name, off, sz in sorted(entries, key=lambda x: -x[2])[:30]:
            print(f'{sz:>12,}  {name}')
        print('--- name sample ---')
        for name, off, sz in entries[:15]:
            print(f'  {name}')

if __name__ == '__main__':
    main()
