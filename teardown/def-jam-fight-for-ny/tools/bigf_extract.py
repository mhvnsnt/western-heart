#!/usr/bin/env python3
"""Extract Def Jam: FFNY BIGF-variant archives (mixed-endian EA BIG).

Header: 'BIGF' + LE32 total_size + BE32 file_count
Entry: BE32 offset + BE32 size + C-string name
(entry0 may have 4 anomalous bytes before its name - handled)
"""
import struct, sys, os

def parse_big(path, table_limit=4*1024*1024):
    with open(path, 'rb') as f:
        magic = f.read(4)
        assert magic == b'BIGF', f"bad magic {magic!r}"
        total = struct.unpack('<I', f.read(4))[0]
        count = struct.unpack('>I', f.read(4))[0]
        entries = []
        for _ in range(count):
            off, size = struct.unpack('>II', f.read(8))
            # read name: C-string, but tolerate up to 4 leading anomalous bytes
            name_bytes = b''
            while True:
                b = f.read(1)
                if b == b'\x00' or b == b'':
                    break
                name_bytes += b
            name = name_bytes.decode('latin1')
            if not name or len(name) > 128:
                # entry0 anomaly: skip 4 bytes, re-read
                f.seek(-len(name_bytes) - 1 + 4, 1)
                name_bytes = b''
                while True:
                    b = f.read(1)
                    if b == b'\x00' or b == b'':
                        break
                    name_bytes += b
                name = name_bytes.decode('latin1')
            entries.append((name, off, size))
    return entries, total, count

def extract(path, outdir, only_ext=None):
    entries, total, count = parse_big(path)
    os.makedirs(outdir, exist_ok=True)
    with open(path, 'rb') as f:
        data = f.read()
    n = 0
    for name, off, size in entries:
        if only_ext and not name.lower().endswith(only_ext):
            continue
        dest = os.path.join(outdir, name.replace('\\', '/'))
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, 'wb') as o:
            o.write(data[off:off+size])
        n += 1
    return entries

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("usage: bigf_extract.py <file> [outdir] [--list]"); sys.exit(1)
    if '--list' in sys.argv:
        entries, total, count = parse_big(sys.argv[1])
        print(f"count={count} total={total}")
        for name, off, size in sorted(entries, key=lambda e: -e[2])[:30]:
            print(f"  {size:>10}  {name}")
        print(f"... {len(entries)} entries")
    else:
        outdir = sys.argv[2] if len(sys.argv) > 2 else sys.argv[1] + '.extracted'
        entries = extract(sys.argv[1], outdir)
        print(f"extracted {len(entries)} entries to {outdir}")
