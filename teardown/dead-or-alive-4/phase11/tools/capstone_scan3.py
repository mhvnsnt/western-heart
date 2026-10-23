#!/usr/bin/env python3
"""Phase 11 scan v3 — TRUE VAs (load base 0x82000000).

Ghidra project base is 0x400000, so phase-10 addresses are RVA+0x400000;
code constants are true VAs. Section map (from the PE header):
  .rdata RVA 0x400    raw 0x400    size 0x2B3C00
  .text  RVA 0x2E0000 raw 0x2D1800 size 0x86AE00
  .data  RVA 0xB60000 raw 0xB42200 size 0x3F7C00
VA(fileoff) = 0x82000000 + RVA.
Watch:
  A) file table 0x8221E800-0x8221EA20, exact anm 0x8221E940
  B) .data slots storing &"d:\\anm.afs" (found by byte search):
     0x82C4902C 0x82C6802C 0x82C6CBDC 0x82C6E714 0x82C8AC04 0x82C8C73C
  C) anm strings 0x82285F3C / 0x822784A3 / 0x8227867F
  D) phase-10 descriptor byte-pattern locs as true VAs (completeness)
Engine: per-lis 32-insn linear const-prop with addi/addis/ori/oris/mr
completion + memory disp(base) effective-address computation."""
import struct, sys, csv, re
from capstone import Cs, CS_ARCH_PPC, CS_MODE_BIG_ENDIAN, CS_MODE_32

SRC = '/home/hatch/workspace/_doa4p8-clone/teardown/dead-or-alive-4/workdir/default_pe.bin'
d = open(SRC, 'rb').read()
SECS = [(0x400, 0x400, 0x2B3C00), (0x2D1800, 0x2E0000, 0x86AE00), (0xB42200, 0xB60000, 0x3F7C00)]
def va(off):
    for raw, rva, size in SECS:
        if raw <= off < raw + size:
            return 0x82000000 + rva + (off - raw)
    return 0x82000000 + off

SLOTS = [0x82C4902C, 0x82C6802C, 0x82C6CBDC, 0x82C6E714, 0x82C8AC04, 0x82C8C73C]
DESC = [0x820766B1, 0x8207A5CD, 0x820808CD, 0x8209276D, 0x82183B49]
def tag(v):
    if v == 0x8221E940: return 'ANM_TABLE_EXACT'
    if v in SLOTS: return 'ANM_PTR_SLOT'
    if 0x8221E800 <= v < 0x8221EA20: return 'FILE_TABLE'
    for x in DESC:
        if abs(v - x) <= 0x10: return 'DESCRIPTOR_PATTERN_LOC'
    if v == 0x82285F3C: return 'ANM_FMT_STR'
    if v == 0x822784A3: return 'ANIME_CM_STR'
    if v == 0x8227867F: return 'ANM_VERSION_STR'
    return None

HI = set()
for lo, hi in [(0x8221E800, 0x8221EA20)] + [(s, s + 1) for s in SLOTS + DESC] + \
              [(0x82285F3C, 0x82285F3D), (0x822784A3, 0x822784A4), (0x8227867F, 0x82278680)]:
    for b in range(lo - 0x8000, hi + 0x8000, 0x10000):
        HI.add((b >> 16) & 0xFFFF)
    HI.add((lo >> 16) & 0xFFFF); HI.add((hi >> 16) & 0xFFFF)
print('HI:', sorted(hex(x) for x in HI))

words = struct.unpack('>%dI' % (len(d) // 4), d[:len(d) // 4 * 4])
TEXT_LO, TEXT_HI = 0x2D1800, 0x2D1800 + 0x86AE00
md = Cs(CS_ARCH_PPC, CS_MODE_BIG_ENDIAN | CS_MODE_32)
mem_re = re.compile(r'^(-?\d+|0x[0-9a-f]+|\-0x[0-9a-f]+)\((r\d+)\)$')
rows = []
nlis = 0
for off in range(TEXT_LO, TEXT_HI, 4):
    w = words[off // 4]
    if (w >> 26) != 15 or ((w >> 16) & 0x1F) != 0:
        continue
    imm = w & 0xFFFF
    if imm not in HI:
        continue
    nlis += 1
    rd = (w >> 21) & 0x1F
    lisva = va(off)
    hi_val = ((imm - 0x10000) << 16) & 0xFFFFFFFF if imm > 0x7FFF else (imm << 16)
    regs = {'r%d' % rd: hi_val}
    for ins in md.disasm(d[off:off + 4 * 33], lisva):
        if ins.address == lisva:
            continue
        m, s = ins.mnemonic, ins.op_str
        parts = [p.strip() for p in s.split(',')]
        for p in parts:
            mm = mem_re.match(p)
            if mm and mm.group(2) in regs:
                disp = int(mm.group(1), 0)
                if disp > 0x7FFF: disp -= 0x10000
                ea = (regs[mm.group(2)] + disp) & 0xFFFFFFFF
                t = tag(ea)
                if t:
                    rows.append((hex(lisva), hex(ins.address), hex(ea), t, 'lis r%d,0x%x -> %s %s' % (rd, imm, m, s)))
        if len(parts) >= 3 and parts[1] in regs and m in ('addi', 'ori', 'oris', 'addis'):
            try: simm = int(parts[2], 0)
            except ValueError: continue
            base = regs[parts[1]]
            if m == 'addi': v = (base + (simm if simm < 0x8000 else simm - 0x10000)) & 0xFFFFFFFF
            elif m == 'addis': v = (base + ((simm if simm < 0x8000 else simm - 0x10000) << 16)) & 0xFFFFFFFF
            elif m == 'ori': v = (base | (simm & 0xFFFF)) & 0xFFFFFFFF
            else: v = (base | ((simm & 0xFFFF) << 16)) & 0xFFFFFFFF
            t = tag(v)
            if t:
                rows.append((hex(lisva), hex(ins.address), hex(v), t, 'lis r%d,0x%x -> %s %s' % (rd, imm, m, s)))
            regs[parts[0]] = v
        elif m in ('or', 'mr') and len(parts) >= 2 and parts[-1] in regs:
            regs[parts[0]] = regs[parts[-1]]
print('candidate lis tracked:', nlis)
print('v3 hits:', len(rows))
for r in rows: print(r)
with open('/home/hatch/workspace/_doa4p2-scratch/p11/scan/capstone_hits3.csv', 'w', newline='') as f:
    wcsv = csv.writer(f); wcsv.writerow(['lis_va', 'use_va', 'ea', 'tag', 'text']); wcsv.writerows(rows)
