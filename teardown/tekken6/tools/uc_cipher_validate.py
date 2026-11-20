#!/usr/bin/env python3
"""Definitive validation: Python sector_cipher model vs REAL EBOOT machine code via unicorn."""
import struct, sys, random
sys.path.insert(0, '/home/hatch/workspace/game-reverse-engineering/tekken6/tools')
from sector_cipher import cipher_block
from unicorn import Uc, UC_ARCH_MIPS, UC_MODE_MIPS64, UC_MODE_LITTLE_ENDIAN
from unicorn.mips_const import *

ELF = '/home/hatch/workspace/game-reverse-engineering/tekken6/decrypted/EBOOT.DECRYPTED.ELF'
LOAD_OFF, LOAD_VA, LOAD_SZ = 0x1018, 0x8804018, 0x386740
CIPHER_VA = 0x8aa2ca8
data = open(ELF, 'rb').read()

STACK_BASE = 0x0FFF0000
BUF = 0x0FC00000
KS = 0x0FB00000
RET = 0x0FA00000

def emu_cipher(K1, K2, words768, length=0x800, t0=0, t1=0):
    mu = Uc(UC_ARCH_MIPS, UC_MODE_MIPS64 | UC_MODE_LITTLE_ENDIAN)
    mu.mem_map(LOAD_VA & ~0xFFF, 0x400000)
    mu.mem_write(LOAD_VA, data[LOAD_OFF:LOAD_OFF+LOAD_SZ])
    mu.mem_map(STACK_BASE - 0x10000, 0x10000)
    mu.mem_map(BUF, 0x4000)
    mu.mem_map(KS, 0x1000)
    mu.mem_map(RET, 0x1000)
    mu.mem_write(BUF, struct.pack('<768I', *words768))
    mu.mem_write(KS, struct.pack('<4I', 0xBCBD1C51, 0xE8BDE039, K1, K2))
    mu.reg_write(UC_MIPS_REG_SP, STACK_BASE - 0x200)
    mu.reg_write(UC_MIPS_REG_A0, KS)
    mu.reg_write(UC_MIPS_REG_A1, BUF)
    mu.reg_write(UC_MIPS_REG_A2, length)
    mu.reg_write(UC_MIPS_REG_T0, t0)
    mu.reg_write(UC_MIPS_REG_T1, t1)
    mu.reg_write(UC_MIPS_REG_RA, RET)
    mu.emu_start(CIPHER_VA, RET)
    return list(struct.unpack('<768I', mu.mem_read(BUF, 768*4)))

rnd = random.Random(999)
bad = 0
for trial in range(5):
    w = [rnd.getrandbits(32) for _ in range(768)]
    K1, K2 = rnd.getrandbits(32), rnd.getrandbits(32)
    py = list(w); cipher_block(K1, K2, py, 0x800)
    try:
        uc = emu_cipher(K1, K2, w)
    except Exception as e:
        print(f"trial {trial}: EMU FAILED: {e}"); bad += 1; continue
    if py == uc:
        print(f"trial {trial}: MODEL MATCHES MACHINE CODE (768/768)")
    else:
        bad += 1
        d = sum(1 for a, b in zip(py, uc) if a != b)
        print(f"trial {trial}: MISMATCH {d}/768")
print("RESULT:", "MODEL VALID" if bad == 0 else f"MODEL BROKEN ({bad} fails)")
