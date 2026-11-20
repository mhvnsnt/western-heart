#!/usr/bin/env python3
"""Round 4 static loader-chain trace (code evidence, no guessing).

Disassembles from the decrypted EBOOT (VA->fileoff = VA-0x8803000):
 1. Every jal/j target scan in the whole image for the wrapper 0x8b559c8,
    inflate 0x8b55bf0, the alt uncompress caller region 0x8b55728, and the
    loader 0x89d27a0 (find ALL callers, not just known ones).
 2. Any 32-bit data word anywhere in the image equal to those addresses
    (function-pointer / vtable references).
 3. Disassembly of: wrapper, loader function containing 0x89d27a0, its three
    known callers' neighbourhoods, and 0x8b55728's function.
"""
import struct, sys
from capstone import Cs, CS_ARCH_MIPS, CS_MODE_MIPS32, CS_MODE_LITTLE_ENDIAN

ELF = sys.argv[1] if len(sys.argv) > 1 else '/home/hatch/workspace/game-reverse-engineering/tekken6/decrypted/EBOOT.DECRYPTED.ELF'
img = open(ELF, 'rb').read()
BASE_VA = 0x8804018
BASE_OFF = 0x1018
FILESZ = 0x3F62A8
code = img[BASE_OFF:BASE_OFF + FILESZ]

def va2off(va): return va - 0x8803000
def off2va(off): return off + 0x8803000

TARGETS = {
    0x8B559C8: 'wrapper',
    0x8B55BF0: 'inflate',
    0x89D27A0: 'loader-call-site',
    0x8B55728: 'alt-uncompress-callsite',
}

print('=== 1. jal/j scan for targets ===')
for i in range(0, len(code) - 3, 4):
    w = struct.unpack_from('<I', code, i)[0]
    op = w >> 26
    if op in (2, 3):  # j / jal
        tgt = 0x80000000 | ((w & 0x3FFFFFF) << 2) if False else ((code and 0) or ((0x88000000 & 0xF0000000) | ((w & 0x3FFFFFF) << 2)))
        # PSP user addresses are 0x08xxxxxx; reconstruct with PC high nibble
        pc_va = off2va(BASE_OFF + i - BASE_OFF) if False else (BASE_VA + i)
        tgt = (pc_va & 0xF0000000) | ((w & 0x3FFFFFF) << 2)
        if tgt in TARGETS:
            print(f'  {"jal" if op==3 else "j  "} at {pc_va:#010x} -> {TARGETS[tgt]} {tgt:#010x}')

print('=== 2. data-word references to targets ===')
for i in range(0, len(code) - 3, 4):
    w = struct.unpack_from('<I', code, i)[0]
    if w in TARGETS:
        print(f'  word ref at {BASE_VA + i:#010x} -> {TARGETS[w]} {w:#010x}')

md = Cs(CS_ARCH_MIPS, CS_MODE_MIPS32 + CS_MODE_LITTLE_ENDIAN)
md.detail = False

def dis(va_start, va_end, label):
    print(f'=== disasm {label}: {va_start:#x}..{va_end:#x} ===')
    off = va2off(va_start)
    blob = img[off:off + (va_end - va_start)]
    for ins in md.disasm(blob, va_start):
        print(f'  {ins.address:#010x}: {ins.mnemonic:8s} {ins.op_str}')

# Wrapper: from entry until well past; find its extent by scanning for jr $ra
dis(0x8B559C8, 0x8B55BF0, 'wrapper 0x8b559c8')
# Loader neighbourhood around the call site
dis(0x89D2680, 0x89D2900, 'loader around 0x89d27a0')
# Known caller neighbourhoods
dis(0x887E480, 0x887E620, 'caller A around 0x887e56c')
dis(0x887E700, 0x887E8B0, 'caller B around 0x887e7fc')
dis(0x89DAA80, 0x89DAC80, 'caller C around 0x89dab8c')
# Alt uncompress function containing 0x8b55728
dis(0x8B55680, 0x8B559C8, 'alt uncompress fn containing 0x8b55728')
