#!/usr/bin/env python3
"""List CRIWARE AFS contents in-place inside a PS2 ISO (no extraction).
Usage: python3 afs_list_iso.py "Urban Reign (USA).iso"
"""
import struct, sys, os
import pycdlib

SECTOR = 2048

class SubReader:
    """File-like reader over a byte range of a larger file."""
    def __init__(self, fp, base, size):
        self.fp = fp; self.base = base; self.size = size; self.pos = 0
    def seek(self, off, whence=0):
        if whence == 0: self.pos = off
        elif whence == 1: self.pos += off
        elif whence == 2: self.pos = self.size + off
        self.pos = max(0, min(self.pos, self.size))
        return self.pos
    def read(self, n=-1):
        if n is None or n < 0: n = self.size - self.pos
        n = min(n, self.size - self.pos)
        self.fp.seek(self.base + self.pos)
        data = self.fp.read(n)
        self.pos += len(data)
        return data
    def tell(self): return self.pos

def parse_afs(r):
    magic = r.read(4)
    if magic != b'AFS\x00':
        return None, f'bad magic {magic!r}'
    count = struct.unpack('<I', r.read(4))[0]
    if count > 100000:
        return None, f'implausible count {count}'
    entries = [struct.unpack('<II', r.read(8)) for _ in range(count)]
    nt_off, nt_size = struct.unpack('<II', r.read(8))
    names = []
    if nt_off and nt_size and nt_size < 10_000_000:
        r.seek(nt_off); raw = r.read(nt_size)
        # name field is 32 or 48 bytes; detect by table size
        field = nt_size // count if count else 32
        field = 48 if abs(field - 48) < abs(field - 32) else 32
        for i in range(count):
            chunk = raw[i*field:(i+1)*field]
            names.append(chunk.split(b'\x00')[0].decode('ascii', 'replace') or f'file_{i:05d}.bin')
    else:
        names = [f'file_{i:05d}.bin' for i in range(count)]
    return [(names[i] if i < len(names) else f'file_{i:05d}.bin', e[0], e[1])
            for i, e in enumerate(entries)], None

def main():
    iso_path = sys.argv[1]
    iso = pycdlib.PyCdlib(); iso.open(iso_path)
    fp = open(iso_path, 'rb')
    outdir = os.path.dirname(os.path.abspath(iso_path))
    all_entries = {}
    for afs in ['/DVD000.AFS;1', '/DVD001.AFS;1']:
        rec = iso.get_record(iso_path=afs)
        base = rec.extent_location() * SECTOR
        size = rec.get_data_length()
        r = SubReader(fp, base, size)
        entries, err = parse_afs(r)
        short = afs.strip('/').split(';')[0]
        if err:
            print(f'{short}: {err}'); continue
        print(f'{short}: {len(entries)} files')
        all_entries[short] = entries
        with open(os.path.join(outdir, short.lower().replace('.afs','') + '-contents.txt'), 'w') as fh:
            fh.write(f'# {short} — {len(entries)} files\n\n')
            for name, off, sz in sorted(entries, key=lambda x: x[0]):
                fh.write(f'{sz:>12,}  {name}\n')
        # top 25 largest
        print('  25 largest:')
        for name, off, sz in sorted(entries, key=lambda x: -x[2])[:25]:
            print(f'    {sz:>12,}  {name}')
    iso.close(); fp.close()

if __name__ == '__main__':
    main()
