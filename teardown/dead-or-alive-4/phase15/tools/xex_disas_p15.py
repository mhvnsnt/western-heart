#!/usr/bin/env python3
"""DOA4 phase 15 Job 3 (v3): disassemble the token-dispatch regions
found by xex_hunt2 and find code loading the registry pointer tables
(.mot table VA 0x82C69A70, .bin table VA 0x82C6B38C) via lis/addi
tracking (word-level candidate search, Capstone for readability)."""
import struct, sys
from capstone import Cs, CS_ARCH_PPC, CS_MODE_BIG_ENDIAN, CS_MODE_32

PE = '/home/hatch/workspace/_doa4p8-clone/teardown/dead-or-alive-4/workdir/default_pe.bin'
d = open(PE, 'rb').read()
VA = lambda fo: fo + 0x82000000 + 0xE800
md = Cs(CS_ARCH_PPC, CS_MODE_BIG_ENDIAN | CS_MODE_32)

def dump(lo, hi, label):
    print(f'===== {label} fileoff {hex(lo)}-{hex(hi)} VA {hex(VA(lo))} =====')
    for ins in md.disasm(d[lo:hi], VA(lo)):
        print(f'{ins.address:08x}  {ins.mnemonic:8s} {ins.op_str}')

if __name__ == '__main__':
    which = sys.argv[1]
    if which == 'a': dump(0x3f9a60, 0x3f9b40, 'token cluster A (bin-loader neighborhood)')
    elif which == 'b': dump(0x4e5040, 0x4e5140, 'token cluster B1')
    elif which == 'c': dump(0x4e7010, 0x4e7110, 'token cluster B2')
    elif which == 'd': dump(0x4e8e80, 0x4e8fa0, 'token cluster B3')
    elif which == 'tables':
        words = struct.unpack('>%dI' % (len(d) // 4), d[:len(d) // 4 * 4])
        TEXT_LO, TEXT_HI = 0x2d1800 // 4, (0x2d1800 + 0x86ae00) // 4
        targets = {0x82C69A70: 'mot_ptr_table', 0x82C6B38C: 'bin_ptr_table'}
        lis_at = {}
        for i in range(TEXT_LO, TEXT_HI):
            w = words[i]
            if (w >> 26) == 15 and ((w >> 16) & 0x1F) == 0:
                lis_at[i] = ((w >> 21) & 0x1F, w & 0xFFFF)
        for i, (rd, imm) in lis_at.items():
            hi = (imm << 16) & 0xFFFFFFFF
            for j in range(i + 1, min(i + 9, TEXT_HI)):
                w = words[j]
                op = w >> 26
                if op in (14, 24) and ((w >> 21) & 0x1F) == rd and ((w >> 16) & 0x1F) == rd:
                    lo = w & 0xFFFF
                    if op == 14 and lo >= 0x8000: lo -= 0x10000
                    addr = (hi + lo) & 0xFFFFFFFF
                    for t, tag in targets.items():
                        if t - 0x40 <= addr <= t + 0x40:
                            print(f'{tag}: lis@{hex(i*4)} addi@{hex(j*4)} -> {hex(addr)}')
                    break
