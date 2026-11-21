#!/usr/bin/env python3
"""Check whether a code region is a safe cave: no reference from OUTSIDE the
region may point into it (internal branches don't matter), and no code may
fall through into it from the word before its start.

Usage: cave_check.py <elf> <start_hex> <size>
"""
import struct
import sys

sys.path.insert(0, '/home/hatch/workspace/koc2-english/work/m3/sources/kactusken/repo/tools')
from elf import Elf  # noqa: E402


def s16(x):
    return x - 0x10000 if x & 0x8000 else x


def main():
    path, start, size = sys.argv[1], int(sys.argv[2], 16), int(sys.argv[3])
    end = start + size
    data = open(path, 'rb').read()
    e = Elf(data)
    (cv, coff, cfs, _), (dv, doff, dfs, _) = e.segments[0], e.segments[1]
    code = data[coff:coff + cfs]
    n = len(code) // 4
    words = struct.unpack_from(f'<{n}I', code, 0)

    def inside(a):
        return start <= a < end

    ext = []  # (source addr, target, kind)
    for i, w in enumerate(words):
        op = w >> 26
        pc = cv + i * 4
        if inside(pc):
            continue  # internal reference: irrelevant
        tgt = None
        kind = None
        if op in (2, 3):
            tgt = ((pc + 4) & 0xF0000000) | ((w & 0x3FFFFFF) << 2)
            kind = 'jal' if op == 3 else 'j'
        elif op in (1, 4, 5, 6, 7, 20, 21, 22, 23):
            tgt = (pc + 4 + (s16(w & 0xFFFF) << 2)) & 0xFFFFFFFF
            kind = 'branch'
        if tgt is not None and inside(tgt):
            ext.append((pc, tgt, kind))
    # data-segment words pointing into the region
    dwords = struct.unpack_from(f'<{dfs // 4}I', data, doff)
    for k, w in enumerate(dwords):
        if inside(w):
            ext.append((dv + k * 4, w, 'data-ptr'))
    # lui-built addresses (source outside the region)
    for i, w in enumerate(words):
        pc = cv + i * 4
        if inside(pc) or w >> 26 != 15:
            continue
        rt = (w >> 16) & 31
        hi = (w & 0xFFFF) << 16
        for j in range(i + 1, min(i + 4, n)):
            w2 = words[j]
            op2 = w2 >> 26
            if op2 in (9, 13) and ((w2 >> 21) & 31) == rt and ((w2 >> 16) & 31) == rt:
                lo = s16(w2 & 0xFFFF) if op2 == 9 else (w2 & 0xFFFF)
                a = (hi + lo) & 0xFFFFFFFF
                if inside(a):
                    ext.append((pc, a, 'lui-built'))
                break
    # fall-through: the 2 words before the region start
    bi = (start - cv) // 4
    before = [f'0x{words[bi - 2]:08x}', f'0x{words[bi - 1]:08x}'] if bi >= 2 else ['<start>']
    print(f'region 0x{start:x}-0x{end:x} ({size} bytes)')
    print(f'  words before: {" ".join(before)}'
          f'{"  <- jr ra + delay: no fall-through" if before[0] == "0x03e00008" else ""}')
    if ext:
        print(f'  EXTERNAL REFERENCES INTO REGION: {len(ext)}')
        for pc, tgt, kind in ext[:20]:
            print(f'    {kind} from 0x{pc:x} -> 0x{tgt:x}')
    else:
        print('  no external references into the region: SAFE as a cave')


if __name__ == '__main__':
    main()
