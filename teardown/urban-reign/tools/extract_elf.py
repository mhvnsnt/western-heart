#!/usr/bin/env python3
"""Surgically extract SLUS_212.09 (PS2 executable) from the Urban Reign ISO
on GitHub release urban-reign-iso-v1, without downloading the full 4GB.

Method: ISO9660 PVD -> root dir -> SLUS_212.09 extent LBA -> HTTP Range.
Also extracts tec/demo/facial/yarare/024_BONES from DVD000.AFS via afs-map.

Usage: python3 extract_elf.py [outdir]
"""
import urllib.request, struct, sys, os, json

BASE = 'https://github.com/mhvnsnt/western-heart/releases/download/urban-reign-iso-v1/'
PARTS = ['urban-reign-500m.part_aa','urban-reign-500m.part_ab','urban-reign-500m.part_ac',
         'urban-reign-500m.part_ad','urban-reign-500m.part_ae','urban-reign-500m.part_af',
         'urban-reign-500m.part_ag','urban-reign-500m.part_ah']
PSZ = 524288000

def fetch_range(abs_start, length):
    out = b''
    while length > 0:
        pi = abs_start // PSZ; lo = abs_start % PSZ
        take = min(length, PSZ - lo)
        url = BASE + PARTS[pi]
        req = urllib.request.Request(url,
            headers={'Range': f'bytes={lo}-{lo+take-1}', 'User-Agent': 'Mozilla/5.0'})
        out += urllib.request.urlopen(req, timeout=120).read()
        abs_start += take; length -= take
    return out

def main():
    outdir = sys.argv[1] if len(sys.argv) > 1 else '.'
    os.makedirs(outdir, exist_ok=True)
    # PVD -> root dir -> SLUS_212.09
    pvd = fetch_range(0x8000, 2048)
    assert pvd[1:6] == b'CD001', 'not ISO9660'
    root_ext = struct.unpack('<I', pvd[156+2:156+6])[0]
    root_len = struct.unpack('<I', pvd[156+10:156+14])[0]
    root = fetch_range(root_ext*2048, root_len)
    o = 0
    while o < len(root):
        ln = root[o]
        if ln == 0: break
        ext = struct.unpack('<I', root[o+2:o+6])[0]
        sz = struct.unpack('<I', root[o+10:o+14])[0]
        nl = root[o+32]
        nm = root[o+33:o+33+nl].decode('utf-8', errors='replace').split(';')[0]
        if nm == 'SLUS_212.09':
            print(f'found {nm} LBA={ext} size={sz}')
            data = fetch_range(ext*2048, sz)
            open(os.path.join(outdir, nm), 'wb').write(data)
            print(f'wrote {len(data)} bytes, ELF magic: {data[:4]}')
        o += ln

if __name__ == '__main__':
    main()
