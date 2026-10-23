#!/usr/bin/env python3
"""DOA4 phase 15 Job 3: bounded Capstone hunt in default_pe.bin for
the consumers of the REAL ANM structures:
 (a) lis/addi (and lis/ori) pairs resolving into the D:\\bin registry
     string ranges (.bin registry VA range given; .mot registry is
     located by string scan first);
 (b) cmpwi/cmplwi immediates of interest: 0x400 (1024-entry tables),
     0x3e8/0x3ec/0x190 (mot table A counts 1000/1004/400), 0x2c (44,
     the .mot record descriptor length), 0x22xx token namespace
     compares (0x2200-0x22ff as immediate or masked compares);
 (c) lwz loads at header offsets +0x08 (w2), +0x54 (w21), +0x70 (w28)
     that sit within 64 B after a resolved registry reference is NOT
     required — reported as raw candidates with context counts.
PPC BE; .text raw 0x2d1800, VA = fileoff + 0x82000000 + 0xE800.
Output: JSON of hits with VA + disassembly context."""
import json, struct, sys
from capstone import Cs, CS_ARCH_PPC, CS_MODE_BIG_ENDIAN

PE = '/home/hatch/workspace/_doa4p8-clone/teardown/dead-or-alive-4/workdir/default_pe.bin'
d = open(PE, 'rb').read()
TEXT_RAW, TEXT_VSZ = 0x2d1800, 0x86ae00
VA = lambda fo: fo + 0x82000000 + 0xE800

# locate .mot registry strings
mot_str = d.find(b'D:\\bin\\zack.mot')
bin_str = d.find(b'D:\\bin\\anime_cm.bin')
print('zack.mot string file off', hex(mot_str), '; anime_cm.bin at', hex(bin_str))
# registry spans: walk NUL-separated D:\bin strings around the hits
def span(center):
    lo = center
    while lo > 0 and d[lo-1:lo] != b'\x00' or (lo >= 7 and d[lo-7:lo-1] == b'D:\\bin'):
        lo -= 1
        if center - lo > 0x2000: break
    # simpler: expand while the region parses as strings
    lo = center
    while True:
        p = d.rfind(b'D:\\bin\\', max(0, center - 0x3000), center)
        if p < 0: break
        center = p; lo = p
        if d[p:p+7] != b'D:\\bin\\': break
        center = p - 1
        if center < 0: break
        # stop when previous chunk is not a string ending near p
        q = d.rfind(b'\x00', max(0, p - 64), p)
        if q < 0 or p - q > 40: break
    return lo
mot_lo = span(mot_str)
print('mot registry approx start', hex(mot_lo))

BIN_REG = (0x27849c, 0x278670)
MOT_REG = (mot_lo, mot_lo + 0x3000)
def in_reg(va, reg):
    return 0x82000000 + reg[0] <= va < 0x82000000 + reg[1]

md = Cs(CS_ARCH_PPC, CS_MODE_BIG_ENDIAN)
md.detail = False
code = d[TEXT_RAW:TEXT_RAW + TEXT_VSZ]
base_va = VA(TEXT_RAW)

hits = {'lis_addi_registry': [], 'cmp_imm': [], 'lwz_hdr': []}
lis_reg = {}   # reg -> (hi_value, va)
INTEREST = {0x400, 0x3e8, 0x3ec, 0x190, 0x2c}
for ins in md.disasm(code, base_va):
    m, ops = ins.mnemonic, ins.op_str
    if m == 'lis':
        try:
            r, v = ops.split(', ')
            lis_reg[r] = (int(v, 0) & 0xffff, ins.address)
        except Exception: pass
    elif m in ('addi', 'ori') and ',' in ops:
        parts = [p.strip() for p in ops.split(',')]
        if len(parts) == 3 and parts[1] in lis_reg:
            hi, hva = lis_reg[parts[1]]
            lo = int(parts[2], 0) & 0xffff
            if m == 'addi' and lo >= 0x8000: lo -= 0x10000
            addr = ((hi << 16) + lo) & 0xffffffff
            if in_reg(addr, BIN_REG) or in_reg(addr, MOT_REG):
                hits['lis_addi_registry'].append({'va': hex(ins.address), 'lis_va': hex(hva),
                    'target': hex(addr), 'reg': parts[0], 'kind': 'bin' if in_reg(addr, BIN_REG) else 'mot'})
    elif m in ('cmpwi', 'cmplwi'):
        parts = [p.strip() for p in ops.split(',')]
        try: imm = int(parts[-1], 0) & 0xffff
        except Exception: continue
        if imm in INTEREST or 0x2200 <= imm <= 0x22ff:
            hits['cmp_imm'].append({'va': hex(ins.address), 'ins': f'{m} {ops}'})
    elif m == 'lwz':
        parts = [p.strip() for p in ops.split(',')]
        if len(parts) == 2 and '(' in parts[1]:
            off = parts[1].split('(')[0]
            try: offv = int(off, 0)
            except Exception: continue
            if offv in (0x08, 0x54, 0x70):
                hits['lwz_hdr'].append({'va': hex(ins.address), 'ins': f'{m} {ops}'})
print('registry refs:', len(hits['lis_addi_registry']))
for h in hits['lis_addi_registry'][:40]: print('  ', h)
print('cmp imm hits:', len(hits['cmp_imm']))
for h in hits['cmp_imm'][:60]: print('  ', h)
print('lwz hdr-offset raw candidates:', len(hits['lwz_hdr']))
json.dump(hits, open('/home/hatch/workspace/_doa4p2-scratch/p15/xex_hunt1.json', 'w'), indent=1)
print('WROTE xex_hunt1.json')
