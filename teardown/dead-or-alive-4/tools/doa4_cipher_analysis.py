#!/usr/bin/env python3
"""
DOA4 AFS Cipher Analysis Tools.
Characterizes the custom Team Ninja table obfuscation used in the 6 encrypted AFS archives.

Findings (2026-10-17):
- 16-byte periodic stream-like cipher, per-file keys
- File DATA is PLAINTEXT (XPR2 textures, floats, etc.)
- Only the header/file table is obfuscated
- NOT simple XOR (4/8/16-byte repeating ruled out via cribs)

Usage:
  python3 doa4_cipher_analysis.py <archive.afs> [--scan|--autocorr|--carve-xpr2]
"""
import struct, math, os, sys
from collections import Counter

def entropy(data):
    c = Counter(data); n = len(data)
    return -sum((v/n)*math.log2(v/n) for v in c.values())

def scan_regions(path, window=0x4000):
    """Scan file in windows, report entropy and zero fraction to find encrypted vs plaintext regions."""
    size = os.path.getsize(path)
    with open(path, 'rb') as f:
        d = f.read()
    print(f'{path}: size={size:#x}')
    prev = None
    for wstart in range(0, size, window):
        w = d[wstart:wstart+window]
        e = entropy(w); zf = w.count(0)/len(w)
        cat = 'ENC' if e > 6.8 and zf < 0.02 else ('ZERO' if zf > 0.3 else 'DATA')
        if cat != prev:
            print(f'  @{wstart:08x}: entropy={e:.2f} zerofrac={zf:.3f} [{cat}]')
            prev = cat

def autocorr(path, n=65536):
    """Byte-match autocorrelation for periods 1..64 to find cipher period."""
    with open(path, 'rb') as f:
        data = f.read(n)
    best = []
    for P in range(1, 65):
        m = sum(1 for i in range(len(data)-P) if data[i] == data[i+P])
        best.append((m/(len(data)-P), P))
    best.sort(reverse=True)
    print(f'Autocorrelation (top 8 periods) for {path}:')
    for frac, P in best[:8]:
        print(f'  P={P:3d} match_frac={frac:.4f}')

def carve_xpr2(path, outdir):
    """Carve plaintext XPR2 textures from mixed-region AFS."""
    with open(path, 'rb') as f:
        d = f.read()
    os.makedirs(outdir, exist_ok=True)
    name = os.path.splitext(os.path.basename(path))[0]
    idx, count = 0, 0
    while True:
        idx = d.find(b'XPR2', idx)
        if idx < 0: break
        if idx + 12 <= len(d):
            size = struct.unpack('<I', d[idx+8:idx+12])[0]
            if 1024 <= size <= 50*1024*1024 and idx + size <= len(d):
                out = os.path.join(outdir, f'{name}_xpr2_{count:03d}.xpr')
                open(out, 'wb').write(d[idx:idx+size])
                count += 1
        idx += 4
    print(f'Carved {count} XPR2 from {path} to {outdir}/')
    return count

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    path, cmd = sys.argv[1], sys.argv[2]
    if cmd == '--scan':
        scan_regions(path)
    elif cmd == '--autocorr':
        autocorr(path)
    elif cmd == '--carve-xpr2':
        outdir = sys.argv[3] if len(sys.argv) > 3 else './carved'
        carve_xpr2(path, outdir)
    else:
        print(f'Unknown command: {cmd}')
