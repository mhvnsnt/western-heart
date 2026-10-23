#!/usr/bin/env python3
"""DOA4 phase 13: who references the D:\\bin\\ path table?
Table at file 0x278480 (.rdata, raw==RVA) -> true VA 0x82278480;
anime_cm string 0x8227849C; table spans to ~0x82278690 (anm_version).
Phase 11 scan3 watched only 0x822784A3 (string+7) and found nothing;
it never watched the table base or the string starts.
Two passes:
 1. byte-search for BE u32 stored pointers into the table range.
 2. Capstone lis + 32-insn const-prop (phase-11 scan3 engine) for
    any materialized address inside the range.
"""
import struct, sys
sys.path.insert(0, '/home/hatch/workspace/_doa4p8-clone/teardown/dead-or-alive-4/phase11/tools')
SRC = '/home/hatch/workspace/_doa4p8-clone/teardown/dead-or-alive-4/workdir/default_pe.bin'
d = open(SRC, 'rb').read()
LO, HI = 0x82278480, 0x82278690

# pass 1: stored pointers
print('== stored BE u32 pointers into bin table ==')
for off in range(0, len(d) - 4, 4):
    v = struct.unpack_from('>I', d, off)[0]
    if LO <= v < HI:
        print(f'  file 0x{off:X} (VA ~0x{0x82000000 + off:X}) -> 0x{v:08X}')

# pass 2: reuse scan3 engine by importing its machinery inline
import importlib.util
spec = importlib.util.spec_from_file_location(
    'scan3', '/home/hatch/workspace/_doa4p8-clone/teardown/dead-or-alive-4/phase11/tools/capstone_scan3.py')
# scan3 runs at import; instead re-implement the prop loop briefly:
from capstone import Cs, CS_ARCH_PPC, CS_MODE_BIG_ENDIAN, CS_MODE_32
TEXT_RAW, TEXT_RVA, TEXT_SIZE = 0x2D1800, 0x2E0000, 0x86AE00
md = Cs(CS_ARCH_PPC, CS_MODE_BIG_ENDIAN + CS_MODE_32)
md.detail = False
print('== lis const-prop materializations into bin table ==')
hits = 0
words = struct.unpack('>%dI' % (TEXT_SIZE // 4), d[TEXT_RAW:TEXT_RAW + TEXT_SIZE])
for i, w in enumerate(words):
    if (w >> 26) != 15:  # addis/lis opcode
        continue
    rt = (w >> 21) & 31; ra = (w >> 16) & 31; imm = w & 0xFFFF
    if ra != 0:
        continue
    hi = imm - 0x10000 if imm & 0x8000 else imm
    base = (hi << 16) & 0xFFFFFFFF
    if not (LO - 0x10000 <= base <= HI + 0x10000):
        continue
    # prop forward 32 insns tracking rt
    val = base
    va0 = 0x82000000 + TEXT_RVA + i * 4
    for j in range(i, min(i + 33, len(words))):
        w2 = words[j]
        op = w2 >> 26
        rD = (w2 >> 21) & 31; rA = (w2 >> 16) & 31; simm = w2 & 0xFFFF
        if simm & 0x8000: simm -= 0x10000
        if j == i:
            continue
        if rA == rt and op == 14:      # addi
            v = (val + simm) & 0xFFFFFFFF
            if LO <= v < HI:
                print(f'  lis@0x{va0:08X} -> 0x{v:08X}'); hits += 1
            val = v; rt = rD
        elif rA == rt and op == 24:    # ori
            v = (val & 0xFFFF0000) | (w2 & 0xFFFF)
            if LO <= v < HI:
                print(f'  lis@0x{va0:08X} -> 0x{v:08X} (ori)'); hits += 1
            val = v; rt = rD
        elif rD == rt and op not in (14, 24):
            break
print('hits:', hits)
