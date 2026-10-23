#!/usr/bin/env python3
"""DOA4 phase 13: raw Capstone dump of the bin-table consumer cluster
0x823FA430-0x823FB600 (true VAs) from default_pe.bin.
.text: raw 0x2D1800 = RVA 0x2E0000; VA = 0x82000000 + RVA.
Frame note (READER5): these VAs are OUTSIDE the phase-11/12 anm
region; treat VA=fileoff+0x82000000 mapping as the working frame and
say so in the doc.
"""
import struct, sys
from capstone import Cs, CS_ARCH_PPC, CS_MODE_BIG_ENDIAN, CS_MODE_32

SRC = '/home/hatch/workspace/_doa4p8-clone/teardown/dead-or-alive-4/workdir/default_pe.bin'
d = open(SRC, 'rb').read()
TEXT_RAW, TEXT_RVA = 0x2D1800, 0x2E0000

def va2off(va):
    return va - 0x82000000 - TEXT_RVA + TEXT_RAW

md = Cs(CS_ARCH_PPC, CS_MODE_BIG_ENDIAN + CS_MODE_32)
start, end = int(sys.argv[1], 16), int(sys.argv[2], 16)
code = d[va2off(start):va2off(end)]
for ins in md.disasm(code, start):
    print(f'0x{ins.address:08X}  {ins.mnemonic:8s} {ins.op_str}')
