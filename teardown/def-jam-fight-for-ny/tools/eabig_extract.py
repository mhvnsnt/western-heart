#!/usr/bin/env python3
"""Extract EA .big archives (Def Jam: Fight for NY, PS2). BIGF big-endian format."""
import struct, sys, os

def list_big(path):
    with open(path, 'rb') as f:
        data = f.read()
    if data[:4] != b'BIGF':
        raise ValueError(f"{path}: not a BIGF archive (magic={data[:4]!r})")
    total, count = struct.unpack('>II', data[8:16])
    entries = []
    pos = 16
    for _ in range(count):
        off, size = struct.unpack('>II', data[pos:pos+8]); pos += 8
        end = data.index(b'\x00', pos); name = data[pos:end].decode('latin1'); pos = end + 1
        entries.append((name, off, size))
    return entries

def extract(big_path, outdir, only=None):
    os.makedirs(outdir, exist_ok=True)
    entries = list_big(big_path)
    with open(big_path, 'rb') as f:
        data = f.read()
    for name, off, size in entries:
        if only and name.lower() not in only:
            continue
        dest = os.path.join(outdir, name.replace('\\', '/'))
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, 'wb') as o:
            o.write(data[off:off+size])
    return entries

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("usage: eabig_extract.py <file.big> <outdir> [filter...]"); sys.exit(1)
    filt = set(a.lower() for a in sys.argv[3:]) or None
    entries = extract(sys.argv[1], sys.argv[2], filt)
    total = sum(s for _,_,s in entries)
    print(f"extracted {len(entries)} entries, {total/1e6:.1f} MB")
    for name, off, size in sorted(entries, key=lambda e: -e[2])[:15]:
        print(f"  {size:>10}  {name}")
