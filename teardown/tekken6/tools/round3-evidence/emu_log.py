#!/usr/bin/env python3
"""Emu match logger: hook the copy-loop entry (0x8b55e20 is delay slot of
the bounds beqz; use 0x8b55e24 loop head instead) and the error exit
0x8b56198 to record (out_len, length, dist) per match from the game's
own inflate running container idx (argv[1]). Copy loop mechanics:
at entry to copy (after e1c check, e20 executed): a0 = cur+1,
s4 = src, $at = end (cur + length). We hook 0x8b55e20 itself BEFORE it
executes: at that moment a0 = cur, s4 = src, $at = cur+length."""
import json, struct, sys
from unicorn import Uc, UC_ARCH_MIPS, UC_MODE_MIPS32, UC_MODE_LITTLE_ENDIAN, UcError, UC_HOOK_CODE
from unicorn.mips_const import *

W = 'work/tekken6/work/'
m = json.load(open(W + 'decrypt3/manifest.json'))
bulk = open(W + 'decrypt3/bulk_decrypted.bin', 'rb')
gz = [f for f in m['files'] if f['magic'].startswith('GZIP')]
def readdata(f):
    bulk.seek(f['start_rel'] * 2048)
    return bulk.read(f['size'])
elf = open('work/tekken6/decrypted/EBOOT.DECRYPTED.ELF', 'rb').read()
IMG = elf[0x1018:0x1018 + 0x3F62A8]


REG_BY_NUM = {}
import unicorn.mips_const as mc
for i, n in enumerate(['ZERO', 'AT', 'V0', 'V1', 'A0', 'A1', 'A2', 'A3',
                       'T0', 'T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7',
                       'S0', 'S1', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7',
                       'T8', 'T9', 'K0', 'K1', 'GP', 'SP', 'FP', 'RA']):
    REG_BY_NUM[i] = getattr(mc, 'UC_MIPS_REG_' + n)

def bitrev32(v):
    return int(f'{v:032b}'[::-1], 2)

PATCH_SITES = {}
def scan_and_patch(mu):
    lo, hi = 0x8B54000, 0x8B57000
    img = bytes(mu.mem_read(lo, hi - lo))
    for off in range(0, len(img) - 3, 4):
        w = struct.unpack_from('<I', img, off)[0]
        addr = lo + off
        if (w >> 26) == 0x1F and (w & 63) == 0x20 and ((w >> 6) & 31) == 20:
            PATCH_SITES[addr] = ('bitrev', (w >> 11) & 31, (w >> 16) & 31)
            mu.mem_write(addr, struct.pack('<I', 0))
        elif (w >> 26) == 0 and (w & 63) == 0x16 and ((w >> 16) & 31) == 0:
            PATCH_SITES[addr] = ('clz', (w >> 11) & 31, (w >> 21) & 31)
            mu.mem_write(addr, struct.pack('<I', 0))
        elif (w >> 26) == 0 and (w & 63) in (0x2C, 0x2D):
            PATCH_SITES[addr] = ('max' if (w & 63) == 0x2C else 'min',
                                 (w >> 11) & 31, ((w >> 21) & 31, (w >> 16) & 31))
            mu.mem_write(addr, struct.pack('<I', 0))

def s32(v):
    return v - 2**32 if v >= 2**31 else v

matches = []
descs = []
def hook(uc, address, size, ud):
    site = PATCH_SITES.get(address)
    if site is not None:
        kind, rd, src = site
        if kind in ('max', 'min'):
            a = s32(uc.reg_read(REG_BY_NUM[src[0]]))
            b = s32(uc.reg_read(REG_BY_NUM[src[1]]))
            uc.reg_write(REG_BY_NUM[rd], (max(a, b) if kind == 'max' else min(a, b)) & 0xFFFFFFFF)
        elif kind == 'bitrev':
            uc.reg_write(REG_BY_NUM[rd], bitrev32(uc.reg_read(REG_BY_NUM[src])))
        elif kind == 'clz':
            val = uc.reg_read(REG_BY_NUM[src])
            uc.reg_write(REG_BY_NUM[rd], 32 - val.bit_length() if val else 32)
        return
    if address == 0x8B55DE8:
        # sra s4, v0, 4 about to execute: v0 = lit descriptor
        descs.append(('litdesc', uc.reg_read(UC_MIPS_REG_V0)))
    elif address == 0x8B55E20:
        a0 = uc.reg_read(UC_MIPS_REG_A0)
        at = uc.reg_read(UC_MIPS_REG_AT)
        s4 = uc.reg_read(UC_MIPS_REG_S4)
        t6 = uc.reg_read(UC_MIPS_REG_T6)
        matches.append((a0 - t6, at - a0, a0 - s4))
    elif address == 0x8B56198:
        a0 = uc.reg_read(UC_MIPS_REG_A0)  # already +1 (delay slot executed)
        at = uc.reg_read(UC_MIPS_REG_AT)
        s4 = uc.reg_read(UC_MIPS_REG_S4)
        t6 = uc.reg_read(UC_MIPS_REG_T6)
        matches.append(('FAIL', (a0 - 1) - t6, at - (a0 - 1), (a0 - 1) - s4))

idx = int(sys.argv[1]) if len(sys.argv) > 1 else 0
t = gz[idx]
fd = readdata(t)
if t['magic'] == 'GZIP+prefix16':
    fd = fd[16:]
w = struct.unpack('<5I', fd[:20])
body = fd[20:]
expect = w[3]
mu = Uc(UC_ARCH_MIPS, UC_MODE_MIPS32 + UC_MODE_LITTLE_ENDIAN)
mu.mem_map(0x08800000, 0x800000)
mu.mem_write(0x08804018, IMG)
OUT = 0x20000000
mu.mem_map(OUT, 0x1000000)
INP = 0x30000000
mu.mem_map(INP, 0x400000)
mu.mem_write(INP, body)
ADLERP = 0x38000000
mu.mem_map(ADLERP, 0x1000)
STK = 0x7F000000
mu.mem_map(STK, 0x100000)
TRAP = 0x40000000
mu.mem_map(TRAP, 0x1000)
mu.mem_write(TRAP, struct.pack('<I', 0x03E00008))
mu.mem_write(TRAP + 4, struct.pack('<I', 0))
mu.reg_write(UC_MIPS_REG_SP, STK + 0x80000)
mu.reg_write(UC_MIPS_REG_RA, TRAP)
mu.reg_write(UC_MIPS_REG_A0, OUT)
mu.reg_write(UC_MIPS_REG_A1, expect + 65536)
mu.reg_write(UC_MIPS_REG_A2, INP)
mu.reg_write(UC_MIPS_REG_A3, ADLERP)
mu.hook_add(UC_HOOK_CODE, hook)
scan_and_patch(mu)
try:
    mu.emu_start(0x8B559C8, TRAP, timeout=60 * 1000000, count=500_000_000)
    print('returned v0=', mu.reg_read(UC_MIPS_REG_V0))
except UcError as e:
    print(f'UcError {e} pc={mu.reg_read(UC_MIPS_REG_PC):#x}')
print(f'emu matches logged: {len(matches)}')
for i, mm in enumerate(matches):
    print(i, mm)
