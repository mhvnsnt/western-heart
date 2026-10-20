#!/usr/bin/env python3
"""Emulate 0x8aa2e88 (CRC+key extract) via unicorn on real sector 230256.
Compares emulated K1/K2 against Python k1k2_extract."""
import struct, sys
sys.path.insert(0, '/home/hatch/workspace/game-reverse-engineering/tekken6/tools')
from k1k2_extract import extract_k1k2

from unicorn import Uc, UC_ARCH_MIPS, UC_MODE_MIPS64, UC_MODE_LITTLE_ENDIAN
from unicorn.mips_const import *

ELF = '/home/hatch/workspace/game-reverse-engineering/tekken6/decrypted/EBOOT.DECRYPTED.ELF'
LOAD_OFF, LOAD_VA, LOAD_SZ = 0x1018, 0x8804018, 0x386740
FN = 0x8aa2e88

data = open(ELF, 'rb').read()
iso = open('/home/hatch/workspace/game-reverse-engineering/tekken6/tekken6-psp.iso','rb')
iso.seek(230256*2048); sec = iso.read(2048)

# standard CRC32 table (poly 0xEDB88320)
def make_crc32_table(poly=0xEDB88320):
    tbl = []
    for i in range(256):
        c = i
        for _ in range(8):
            c = (c >> 1) ^ poly if c & 1 else c >> 1
        tbl.append(c & 0xFFFFFFFF)
    return tbl
CRC_TBL = make_crc32_table()

mu = Uc(UC_ARCH_MIPS, UC_MODE_MIPS64 | UC_MODE_LITTLE_ENDIAN)
mu.mem_map(LOAD_VA & ~0xFFF, 0x400000)
mu.mem_write(LOAD_VA, data[LOAD_OFF:LOAD_OFF+LOAD_SZ])
# place CRC table at 0x8C2BA00 and off/mask tables at 0x8BCE780
mu.mem_map(0x8C2B000, 0x10000)
mu.mem_write(0x8C2BA00, struct.pack('<256I', *CRC_TBL))
mu.mem_map(0x8BCE000, 0x10000)
mu.mem_write(0x8BCE780, struct.pack('<2I', 0x38BFE591, 0xD3610818))
mu.mem_write(0x8BCE788, struct.pack('<2I', 0xF1, 0x1AB))
# stack + buffers
STACK = 0x0FFF0000
mu.mem_map(STACK - 0x10000, 0x10000)
SECBUF = 0x0FE00000
mu.mem_map(SECBUF - 0x1000, 0x3000)
mu.mem_write(SECBUF, sec)
OUT = 0x0FD00000
mu.mem_map(OUT - 0x1000, 0x2000)
RET = 0x0FC00000
mu.mem_map(RET, 0x1000)

mu.reg_write(UC_MIPS_REG_SP, STACK - 0x100)
mu.reg_write(UC_MIPS_REG_A0, 0)
mu.reg_write(UC_MIPS_REG_A1, SECBUF)
mu.reg_write(UC_MIPS_REG_A2, OUT)      # &K1
mu.reg_write(UC_MIPS_REG_A3, OUT + 4)  # &K2
mu.reg_write(UC_MIPS_REG_RA, RET)
mu.emu_start(FN, RET)
v0 = mu.reg_read(UC_MIPS_REG_V0)
k1, k2 = struct.unpack('<2I', mu.mem_read(OUT, 8))
print(f"emulated: v0={v0} K1={k1:#010x} K2={k2:#010x}")

ok, pk1, pk2, reason = extract_k1k2(sec)
print(f"python:   ok={ok} K1={pk1:#010x} K2={pk2:#010x} ({reason})")
print("MATCH" if (k1 == pk1 and k2 == pk2 and v0 == 1) else "MISMATCH")
