#!/usr/bin/env python3
"""Dead-code scan for KoC2's ELF: find unreferenced functions (cave candidates).

A function is "referenced" if its start address is:
  - a jal/j target anywhere in the code, or
  - a word in the data segment (function pointer / jump-table entry), or
  - built by a lui + addiu/ori pair in the code.
Function boundaries are heuristic: a function ends at `jr ra` + delay slot;
the next word starts a new function. jal targets are always function starts.

Usage: deadcode_scan.py <elf> [min_size]
"""
import struct
import sys

sys.path.insert(0, '/home/hatch/workspace/koc2-english/work/m3/sources/kactusken/repo/tools')
from elf import Elf  # noqa: E402


def s16(x):
    return x - 0x10000 if x & 0x8000 else x


def main():
    path = sys.argv[1]
    min_size = int(sys.argv[2]) if len(sys.argv) > 2 else 100
    data = open(path, 'rb').read()
    e = Elf(data)
    # code segment: first PT_LOAD (text); data segment: second PT_LOAD
    (cv, coff, cfs, _), (dv, doff, dfs, _) = e.segments[0], e.segments[1]
    code = data[coff:coff + cfs]
    n = len(code) // 4
    words = struct.unpack_from(f'<{n}I', code, 0)
    code_lo, code_hi = cv, cv + cfs

    refs = set()
    # jal (op 3) and j (op 2) targets, plus all conditional branch targets
    for i, w in enumerate(words):
        op = w >> 26
        pc = cv + i * 4
        if op in (2, 3):
            refs.add(((pc + 4) & 0xF0000000) | ((w & 0x3FFFFFF) << 2))
        elif op in (1, 4, 5, 6, 7, 20, 21, 22, 23):
            refs.add((pc + 4 + (s16(w & 0xFFFF) << 2)) & 0xFFFFFFFF)
    # words in the data segment pointing into the code segment
    dwords = struct.unpack_from(f'<{dfs // 4}I', data, doff)
    for w in dwords:
        if code_lo <= w < code_hi:
            refs.add(w)
    # lui-built addresses in the code segment
    for i, w in enumerate(words):
        if w >> 26 != 15:  # lui
            continue
        rt = (w >> 16) & 31
        hi = (w & 0xFFFF) << 16
        for j in range(i + 1, min(i + 4, n)):
            w2 = words[j]
            op2 = w2 >> 26
            if op2 in (9, 13) and ((w2 >> 21) & 31) == rt and ((w2 >> 16) & 31) == rt:
                # addiu / ori rt, rt, imm
                lo = s16(w2 & 0xFFFF) if op2 == 9 else (w2 & 0xFFFF)
                a = (hi + lo) & 0xFFFFFFFF
                if code_lo <= a < code_hi:
                    refs.add(a)
                break

    # function starts: after every `jr ra` (+ delay slot), plus entry, plus jal targets
    starts = {e.entry}
    for i, w in enumerate(words):
        if w == 0x03E00008:  # jr ra
            nxt = cv + (i + 2) * 4
            if nxt < code_hi:
                starts.add(nxt)
    starts |= {r for r in refs if code_lo <= r < code_hi}
    starts = sorted(starts)

    # unreferenced functions with size
    out = []
    for k, s in enumerate(starts):
        end = starts[k + 1] if k + 1 < len(starts) else code_hi
        size = end - s
        if size < min_size:
            continue
        if s in refs:
            continue
        # no reference may fall inside the function either
        if any(s < r < end for r in refs):
            continue
        # clean entry boundary: the two words before must be `jr ra` + delay slot
        # (so no code falls through into the cave), unless the start is the entry point
        bi = (s - cv) // 4
        if bi >= 2 and words[bi - 2] != 0x03E00008:
            continue
        first = words[(s - cv) // 4]
        out.append((s, size, first))
    out.sort(key=lambda t: -t[1])
    print(f'code {code_lo:#x}-{code_hi:#x} ({cfs} bytes), {len(refs)} referenced addrs, '
          f'{len(starts)} function starts')
    print(f'unreferenced functions >= {min_size} bytes: {len(out)}')
    for s, size, first in out[:40]:
        print(f'  0x{s:08x}  {size:5d} bytes  first word 0x{first:08x}')


if __name__ == '__main__':
    main()
