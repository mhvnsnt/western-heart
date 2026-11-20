#!/usr/bin/env python3
"""Fast batch MIPS disassembler for the T6 EBOOT (single capstone pass).
Usage: fastdis.py 0xSTART 0xEND [outfile]"""
import struct, sys
from capstone import Cs, CS_ARCH_MIPS, CS_MODE_MIPS32, CS_MODE_LITTLE_ENDIAN

ELF = '/home/hatch/workspace/_t6r4-work/ghidra-r9/EBOOT.DECRYPTED.ELF'
data = open(ELF, 'rb').read()
BASE = 0x08803000
md = Cs(CS_ARCH_MIPS, CS_MODE_MIPS32 | CS_MODE_LITTLE_ENDIAN)

def dis(start, end):
    off = start - BASE
    lines = []
    for i in md.disasm(data[off:off + (end - start)], start):
        w = struct.unpack_from('<I', data, i.address - BASE)[0]
        lines.append(f'{i.address:#010x}: {w:08x}  {i.mnemonic:12s} {i.op_str}')
    return lines

if __name__ == '__main__':
    start = int(sys.argv[1], 16); end = int(sys.argv[2], 16)
    out = '\n'.join(dis(start, end))
    if len(sys.argv) > 3:
        open(sys.argv[3], 'w').write(out + '\n')
    print(out)
