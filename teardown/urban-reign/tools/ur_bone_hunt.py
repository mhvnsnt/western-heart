#!/usr/bin/env python3
"""Bone-translation hunt for Urban Reign char PPKs (OPEN item 1).

Negative-result tooling from watchdog attempt 3 (2026-10-14). Run:
    ur_bone_hunt.py <charXXX.ppk>
Prints: tag-table chunk inventory, identity-4x4 census (4-aligned),
two-bone translation-constraint test, cross notes on false leads.

FINDINGS (char001.ppk):
  - No bone-name strings: b'__L_' / b'__R_' count = 0 in ALL 72 char PPKs.
    (The "863 strings" in earlier notes were float bytes misread as ASCII.)
  - Only 3-4 identity 4x4 matrices in the whole file (at 0x670, 0x780,
    0x850, 0xbf0), each preceded by 28 zero floats -- NOT a per-bone table.
  - Two-bone constraint test REFUTES the pure-translation model: for a
    2-influence vertex, d = pos_a - pos_b should be constant per bone pair
    (T_b - T_a). Observed: 615 distinct d vectors over 1555 verts
    (top cluster only 6). The two positions are NOT the same rest point
    in two translated bone frames.
  - Chunk 7 (0x8001@0x2971): no int32 67s, no 96-byte record structure;
    mostly noise. Chunk 9 (0x865@0x8001): denormal noise. Chunk 8
    (0x8@0x6880): additional vertex blob (128-sep format), not bone data.
  - Cross-fighter census (72 PPKs): no constant-size shared-skeleton chunk;
    tag types vary per fighter -- detect chunks by content, never by type.
NEXT: parse .gyu motion files for skeleton (bone count/names), or check
stage PPKs / ISO for a shared rig; topology (index order) needed before
per-bone rigid alignment can be attempted.
"""
import struct, math, sys, re
from collections import Counter

def parse_tags(d):
    e = []; o = 0x20
    while o < 0x200:
        v = struct.unpack('<I', d[o:o+4])[0]
        if v == 0:
            break
        e.append((v >> 16, v & 0xFFFF)); o += 4
    return e

def main():
    path = sys.argv[1]
    d = open(path, 'rb').read(); n = len(d)
    print(f"{path}: {n} bytes")
    print("bone-name markers: __L_ =", d.count(b'__L_'), "__R_ =", d.count(b'__R_'))

    tags = parse_tags(d)
    offs = sorted(set(o for _, o in tags))
    print(f"tag entries: {len(tags)}")
    for typ, off in tags:
        i = offs.index(off)
        end = offs[i+1] if i+1 < len(offs) else n
        print(f"  type={hex(typ)} off={hex(off)} size={end-off}")

    # identity 4x4 census, 4-aligned
    ids = []
    off = 0
    while off + 64 <= n:
        fl = struct.unpack('<16f', d[off:off+64])
        if all(abs(fl[i] - (1.0 if i in (0, 5, 10, 15) else 0.0)) < 1e-9
               for i in range(16)):
            ids.append(off)
        off += 4
    print("identity 4x4 matrices (4-aligned):", len(ids), [hex(h) for h in ids])

    # two-bone constraint test on float vertex chunks
    def is_sep(fl, i):
        return all(abs(fl[i+k] - 128.0) < 0.01 for k in range(4))
    two = []
    for typ, off in tags:
        i = offs.index(off)
        end = offs[i+1] if i+1 < len(offs) else n
        size = end - off
        if size < 64 or off < 0x80:
            continue
        probe = struct.unpack('<8f', d[off:off+32])
        if not all(math.isfinite(v) and abs(v) < 1e7 for v in probe):
            continue
        nf = size // 4
        fl = struct.unpack(f'<{nf}f', d[off:off+nf*4])
        seps = []; j = 0
        while j < nf - 4:
            if is_sep(fl, j):
                seps.append(j); j += 4
            else:
                j += 1
        prev = 0
        for s in seps:
            blen = s - prev
            if blen == 20:
                rows = fl[prev:s]
                wsum = rows[3] + rows[11]
                if abs(wsum - 1.0) < 0.02:
                    two.append(((rows[0], rows[1], rows[2]),
                                (rows[8], rows[9], rows[10])))
            prev = s + 4
    c = Counter()
    for pa, pb in two:
        c[(pa[0]-pb[0], pa[1]-pb[1], pa[2]-pb[2])] += 1
    print(f"two-bone verts: {len(two)}, distinct exact d vectors: {len(c)}")
    for dd, nn in c.most_common(5):
        print(f"  d=({dd[0]:.6f},{dd[1]:.6f},{dd[2]:.6f}) x{nn}")

if __name__ == '__main__':
    main()
