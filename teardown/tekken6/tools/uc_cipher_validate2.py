#!/usr/bin/env python3
"""Definitive cipher validation: unicorn + manual bitrev hook vs Python model."""
import struct, sys, random
sys.path.insert(0, '/home/hatch/workspace/game-reverse-engineering/tekken6/tools')
from sector_cipher import cipher_block
from unicorn import Uc, UC_ARCH_MIPS, UC_MODE_MIPS64, UC_MODE_LITTLE_ENDIAN, UC_HOOK_CODE
from unicorn.mips_const import *

ELF = '/home/hatch/workspace/game-reverse-engineering/tekken6/decrypted/EBOOT.DECRYPTED.ELF'
LOAD_OFF, LOAD_VA, LOAD_SZ = 0x1018, 0x8804018, 0x386740
CIPHER_VA = 0x8aa2ca8
data = open(ELF, 'rb').read()

def bitrev32(x):
    r = 0
    for i in range(32):
        r = (r << 1) | ((x >> i) & 1)
    return r & 0xFFFFFFFF

def emu_cipher(K1, K2, words768):
    mu = Uc(UC_ARCH_MIPS, UC_MODE_MIPS64 | UC_MODE_LITTLE_ENDIAN)
    mu.mem_map(0x8804000, 0x390000)
    mu.mem_write(LOAD_VA, data[LOAD_OFF:LOAD_OFF+LOAD_SZ])
    mu.mem_map(0x0FFE0000, 0x10000)
    mu.mem_map(0x0FC00000, 0x4000)
    mu.mem_write(0x0FC00000, struct.pack('<768I', *words768))
    mu.mem_map(0x0FB00000, 0x1000)
    mu.mem_write(0x0FB00000, struct.pack('<4I', 0xBCBD1C51, 0xE8BDE039, K1, K2))
    mu.mem_map(0x0FA00000, 0x1000)
    # hook bitrev (0x7C041D20 = bitrev $v1,$a0; also general 0x1F opcode with funct 0x20)
    def hook(uc, addr, size, ud):
        w = struct.unpack('<I', uc.mem_read(addr, 4))[0]
        if (w >> 26) == 0x1F and (w & 0x3F) == 0x20:
            sub = (w >> 6) & 0x1F
            if 20 <= sub < 24 or sub >= 28:  # bitrev variants
                rt = (w >> 16) & 0x1F; rd = (w >> 11) & 0x1F
                # map reg index to UC const
                regmap = [UC_MIPS_REG_ZERO, UC_MIPS_REG_AT, UC_MIPS_REG_V0, UC_MIPS_REG_V1,
                          UC_MIPS_REG_A0, UC_MIPS_REG_A1, UC_MIPS_REG_A2, UC_MIPS_REG_A3,
                          UC_MIPS_REG_T0, UC_MIPS_REG_T1, UC_MIPS_REG_T2, UC_MIPS_REG_T3,
                          UC_MIPS_REG_T4, UC_MIPS_REG_T5, UC_MIPS_REG_T6, UC_MIPS_REG_T7,
                          UC_MIPS_REG_S0, UC_MIPS_REG_S1, UC_MIPS_REG_S2, UC_MIPS_REG_S3,
                          UC_MIPS_REG_S4, UC_MIPS_REG_S5, UC_MIPS_REG_S6, UC_MIPS_REG_S7,
                          UC_MIPS_REG_T8, UC_MIPS_REG_T9, UC_MIPS_REG_K0, UC_MIPS_REG_K1,
                          UC_MIPS_REG_GP, UC_MIPS_REG_SP, UC_MIPS_REG_FP, UC_MIPS_REG_RA]
                v = uc.reg_read(regmap[rt])
                uc.reg_write(regmap[rd], bitrev32(v))
                uc.reg_write(UC_MIPS_REG_PC, addr + 4)
    mu.hook_add(UC_HOOK_CODE, hook, begin=CIPHER_VA, end=CIPHER_VA+0x400)
    mu.reg_write(UC_MIPS_REG_SP, 0x0FFF0000 - 0x200)
    mu.reg_write(UC_MIPS_REG_A0, 0x0FB00000)
    mu.reg_write(UC_MIPS_REG_A1, 0x0FC00000)
    mu.reg_write(UC_MIPS_REG_A2, 0x800)
    mu.reg_write(UC_MIPS_REG_T0, 0)
    mu.reg_write(UC_MIPS_REG_T1, 0)
    mu.reg_write(UC_MIPS_REG_RA, 0x0FA00000)
    mu.emu_start(CIPHER_VA, 0x0FA00000)
    return list(struct.unpack('<768I', mu.mem_read(0x0FC00000, 768*4)))

rnd = random.Random(777)
bad = 0
for trial in range(3):
    w = [rnd.getrandbits(32) for _ in range(768)]
    K1, K2 = rnd.getrandbits(32), rnd.getrandbits(32)
    py = list(w); cipher_block(K1, K2, py, 0x800)
    try:
        uc = emu_cipher(K1, K2, w)
    except Exception as e:
        print(f"trial {trial}: EMU FAULT {e}"); bad += 1; continue
    if py == uc:
        print(f"trial {trial}: MODEL MATCHES MACHINE CODE")
    else:
        bad += 1
        d = sum(1 for a, b in zip(py, uc) if a != b)
        print(f"trial {trial}: MISMATCH {d}/768")
print("RESULT:", "MODEL VALID" if bad == 0 else "MODEL BROKEN")
