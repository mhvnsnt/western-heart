#!/usr/bin/env python3
"""Round 3 Unicorn harness: execute the game's own inflate (wrapper
0x8b559c8) on a GZIP container body and dump the plaintext it produces.
Mapping follows the decrypted ELF's single PT_LOAD (vaddr 0x08804018,
file offset 0x1018). Usage: emu3.py <idx> [out.bin]"""
import json, struct, sys, zlib
from unicorn import Uc, UC_ARCH_MIPS, UC_MODE_MIPS32, UC_MODE_LITTLE_ENDIAN, UcError, UC_HOOK_CODE
from unicorn.mips_const import (UC_MIPS_REG_SP, UC_MIPS_REG_RA, UC_MIPS_REG_A0,
                                UC_MIPS_REG_A1, UC_MIPS_REG_A2, UC_MIPS_REG_A3,
                                UC_MIPS_REG_V0, UC_MIPS_REG_PC)

REG_BY_NUM = {}
def _init_regs():
    import unicorn.mips_const as mc
    names = ['ZERO', 'AT', 'V0', 'V1', 'A0', 'A1', 'A2', 'A3',
             'T0', 'T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7',
             'S0', 'S1', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7',
             'T8', 'T9', 'K0', 'K1', 'GP', 'SP', 'FP', 'RA']
    for i, n in enumerate(names):
        REG_BY_NUM[i] = getattr(mc, 'UC_MIPS_REG_' + n)
_init_regs()

def bitrev32(v):
    return int(f'{v:032b}'[::-1], 2)

PATCH_SITES = {}  # addr -> (kind, rd, src); filled by scan_and_patch()

def scan_and_patch(mu):
    """Find Allegrex-only words in the inflate code region of the loaded
    image, replace them with NOPs in emulated memory, and record their
    register effects for the code hook. Patching (not PC-skipping) keeps
    MIPS delay-slot semantics intact (0x8b55de4 sits in a bgez delay slot).
    Patterns: BITREV = SPECIAL3 funct 0x20 sa 20 (rd = bitrev32(rt));
    CLZ = SPECIAL funct 0x16 (rd = clz32(rs))."""
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
            kind = 'max' if (w & 63) == 0x2C else 'min'
            PATCH_SITES[addr] = (kind, (w >> 11) & 31, ((w >> 21) & 31, (w >> 16) & 31))
            mu.mem_write(addr, struct.pack('<I', 0))
    return PATCH_SITES

def _s32(v):
    return v - 2**32 if v >= 2**31 else v

def hook_code_bitrev(uc, address, size, user_data):
    site = PATCH_SITES.get(address)
    if site is not None:
        kind, rd, src = site
        if kind in ('max', 'min'):
            a = _s32(uc.reg_read(REG_BY_NUM[src[0]]))
            b = _s32(uc.reg_read(REG_BY_NUM[src[1]]))
            r = max(a, b) if kind == 'max' else min(a, b)
            uc.reg_write(REG_BY_NUM[rd], r & 0xFFFFFFFF)
            return
        val = uc.reg_read(REG_BY_NUM[src])
        if kind == 'bitrev':
            uc.reg_write(REG_BY_NUM[rd], bitrev32(val))
        elif kind == 'clz':
            uc.reg_write(REG_BY_NUM[rd], 32 - val.bit_length() if val else 32)

W = 'work/tekken6/work/'
m = json.load(open(W + 'decrypt3/manifest.json'))
bulk = open(W + 'decrypt3/bulk_decrypted.bin', 'rb')
gz = [f for f in m['files'] if f['magic'].startswith('GZIP')]

def readdata(f):
    bulk.seek(f['start_rel'] * 2048)
    return bulk.read(f['size'])

elf = open('work/tekken6/decrypted/EBOOT.DECRYPTED.ELF', 'rb').read()
IMG_VADDR = 0x08804018
IMG_FILEOFF = 0x1018
IMG_FILESZ = 0x3F62A8
IMG = elf[IMG_FILEOFF:IMG_FILEOFF + IMG_FILESZ]

def run_inflate(idx):
    t = gz[idx]
    fd = readdata(t)
    if t['magic'] == 'GZIP+prefix16':
        fd = fd[16:]
    w = struct.unpack('<5I', fd[:20])
    body = fd[20:]
    expect = w[3]
    mu = Uc(UC_ARCH_MIPS, UC_MODE_MIPS32 + UC_MODE_LITTLE_ENDIAN)
    mu.mem_map(0x08800000, 0x800000)
    mu.mem_write(IMG_VADDR, IMG)
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
    mu.mem_write(TRAP, struct.pack('<I', 0x03E00008))  # jr $ra (ra=TRAP: self-loop exit)
    mu.mem_write(TRAP + 4, struct.pack('<I', 0))       # nop delay slot
    mu.reg_write(UC_MIPS_REG_SP, STK + 0x80000)
    mu.reg_write(UC_MIPS_REG_RA, TRAP)
    mu.reg_write(UC_MIPS_REG_A0, OUT)
    mu.reg_write(UC_MIPS_REG_A1, expect + 65536)
    mu.reg_write(UC_MIPS_REG_A2, INP)
    mu.reg_write(UC_MIPS_REG_A3, ADLERP)
    mu.hook_add(UC_HOOK_CODE, hook_code_bitrev)
    sites = scan_and_patch(mu)
    print(f'  patched {len(sites)} Allegrex sites: {[hex(a) for a in sorted(sites)]}', flush=True)
    try:
        mu.emu_start(0x8B559C8, TRAP, timeout=30 * 1000000, count=500_000_000)
        status = 'returned'
    except UcError as e:
        status = f'UcError: {e} pc={mu.reg_read(UC_MIPS_REG_PC):#x}'
    v0 = mu.reg_read(UC_MIPS_REG_V0)
    sv0 = v0 - 2**32 if v0 >= 2**31 else v0
    adler_out = struct.unpack('<I', mu.mem_read(ADLERP, 4))[0]
    print(f'idx{idx} status={status} v0={sv0} ({v0:#x}) expect={expect} adler_out={adler_out:#010x}', flush=True)
    out = bytes(mu.mem_read(OUT, expect))
    if sv0 == expect:
        print(f'  adler(emu_out)={zlib.adler32(out[:expect]):#010x} trailer_match={zlib.adler32(out[:expect]) == adler_out}', flush=True)
    return out, sv0, expect

if __name__ == '__main__':
    idx = int(sys.argv[1])
    out, sv0, expect = run_inflate(idx)
    if len(sys.argv) > 2:
        open(sys.argv[2], 'wb').write(out[:expect])
        print('wrote', sys.argv[2], expect, 'bytes (buffer dump, valid prefix unknown)')
