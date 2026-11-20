#!/usr/bin/env python3
"""Emulate 0x8aa2e88 (CRC+key extract) via unicorn. No Allegrex insns. Validates K1/K2."""
import struct, sys
sys.path.insert(0, '/home/hatch/workspace/game-reverse-engineering/tekken6/tools')
from k1k2_extract import extract_k1k2
from unicorn import Uc, UC_ARCH_MIPS, UC_MODE_MIPS32, UC_MODE_LITTLE_ENDIAN
from unicorn.mips_const import *

ELF = '/home/hatch/workspace/game-reverse-engineering/tekken6/decrypted/EBOOT.DECRYPTED.ELF'
LOAD_OFF, LOAD_VA, LOAD_SZ = 0x1018, 0x8804018, 0x386740
FN = 0x8aa2e88
data = open(ELF, 'rb').read()
iso = open('/home/hatch/workspace/game-reverse-engineering/tekken6/tekken6-psp.iso','rb')
iso.seek(230256*2048); sec = iso.read(2048)

def crc32_table(poly=0xEDB88320):
    t = []
    for i in range(256):
        c = i
        for _ in range(8):
            c = (c >> 1) ^ poly if c & 1 else c >> 1
        t.append(c & 0xFFFFFFFF)
    return t

mu = Uc(UC_ARCH_MIPS, UC_MODE_MIPS32 | UC_MODE_LITTLE_ENDIAN)
mu.mem_map(0x8804000, 0x390000)
mu.mem_write(LOAD_VA, data[LOAD_OFF:LOAD_OFF+LOAD_SZ])
mu.mem_map(0x8C2B000, 0x10000)
mu.mem_write(0x8C2BA00, struct.pack('<256I', *crc32_table()))
mu.mem_map(0x8BCE000, 0x10000)
mu.mem_write(0x8BCE780, struct.pack('<2I', 0x38BFE591, 0xD3610818))
mu.mem_write(0x8BCE788, struct.pack('<2I', 0xF1, 0x1AB))
mu.mem_map(0x0FFE0000, 0x10000)   # stack
mu.mem_map(0x0FC00000, 0x3000)    # sector buf
mu.mem_write(0x0FC00000, sec)
mu.mem_map(0x0FB00000, 0x2000)    # out
mu.mem_map(0x0FA00000, 0x1000)    # ret
mu.reg_write(UC_MIPS_REG_SP, 0x0FFF0000 - 0x100)
mu.reg_write(UC_MIPS_REG_A0, 0)
mu.reg_write(UC_MIPS_REG_A1, 0x0FC00000)
mu.reg_write(UC_MIPS_REG_A2, 0x0FB00000)
mu.reg_write(UC_MIPS_REG_A3, 0x0FB00004)
mu.reg_write(UC_MIPS_REG_RA, 0x0FA00000)
try:
    mu.emu_start(FN, 0x0FA00000)
    v0 = mu.reg_read(UC_MIPS_REG_V0)
    k1, k2 = struct.unpack('<2I', mu.mem_read(0x0FB00000, 8))
    print(f"EMULATED: v0={v0} K1={k1:#010x} K2={k2:#010x}")
except Exception as e:
    print(f"EMU FAULT: {e} pc={mu.reg_read(UC_MIPS_REG_PC):#x}")

ok, pk1, pk2, reason = extract_k1k2(sec)
print(f"PYTHON:   ok={ok} K1={pk1:#010x} K2={pk2:#010x}")
