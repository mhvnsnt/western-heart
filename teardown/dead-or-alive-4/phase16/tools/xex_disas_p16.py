#!/usr/bin/env python3
"""DOA4 phase 16 Job 2: targeted Capstone disassembly of default_pe.bin.

VA convention (phase 15, proven): .text file offset f -> VA f + 0x8200E800.
Usage: xex_disas_p16.py VA_HEX LEN_HEX [outfile]
Prints (and optionally writes) a linear disassembly window. Callers must
treat function boundaries as unproven until established by branch analysis.
"""
import sys
from capstone import Cs, CS_ARCH_PPC, CS_MODE_BIG_ENDIAN, CS_MODE_32

PE = '/home/hatch/workspace/_doa4p16-clone/teardown/dead-or-alive-4/workdir/default_pe.bin'
TEXT_BASE = 0x8200E800

def main():
    va = int(sys.argv[1], 16); ln = int(sys.argv[2], 16)
    out = open(sys.argv[3], 'w') if len(sys.argv) > 3 else sys.stdout
    b = open(PE, 'rb').read()
    f = va - TEXT_BASE
    assert 0 <= f and f + ln <= len(b), (hex(f), hex(ln))
    md = Cs(CS_ARCH_PPC, CS_MODE_BIG_ENDIAN | CS_MODE_32)
    md.skipdata = True
    for ins in md.disasm(b[f:f+ln], va):
        out.write(f'{ins.address:08x}  {ins.bytes.hex()}  {ins.mnemonic:10s} {ins.op_str}\n')
    if out is not sys.stdout: out.close()

if __name__ == '__main__':
    main()
