#!/usr/bin/env python3
"""Phase 11 Job 1 step 2: materializers of the global stream object 0x82C3A3D0.
Same engine as capstone_scan3.py (per-lis 32-insn const-prop, true VAs)."""
import struct, csv, re, sys
sys.path.insert(0, '/home/hatch/workspace/_doa4p8-clone/teardown/dead-or-alive-4/phase11/tools')
SRC = '/home/hatch/workspace/_doa4p8-clone/teardown/dead-or-alive-4/workdir/default_pe.bin'
d = open(SRC, 'rb').read()
SECS = [(0x400, 0x400, 0x2B3C00), (0x2D1800, 0x2E0000, 0x86AE00), (0xB42200, 0xB60000, 0x3F7C00)]
def va(off):
    for raw, rva, size in SECS:
        if raw <= off < raw + size: return 0x82000000 + rva + (off - raw)
    return 0x82000000 + off
TARGET = 0x833FA3D0
def tag(v):
    if v == TARGET: return 'STREAM_OBJ_EXACT'
    if TARGET - 0x8000 < v < TARGET + 0x2000: return 'STREAM_OBJ_FIELD'  # disp(base) reach of cursor/end at +0xBE0/+0xBE4 etc.
    return None
from capstone import Cs, CS_ARCH_PPC, CS_MODE_BIG_ENDIAN, CS_MODE_32
words = struct.unpack('>%dI' % (len(d)//4), d[:len(d)//4*4])
TEXT_LO, TEXT_HI = 0x2D1800, 0x2D1800 + 0x86AE00
md = Cs(CS_ARCH_PPC, CS_MODE_BIG_ENDIAN | CS_MODE_32)
mem_re = re.compile(r'^(-?\d+|0x[0-9a-f]+|\-0x[0-9a-f]+)\((r\d+)\)$')
rows = []
for off in range(TEXT_LO, TEXT_HI, 4):
    w = words[off//4]
    if (w >> 26) != 15 or ((w >> 16) & 0x1F) != 0: continue
    imm = w & 0xFFFF
    if imm != (TARGET >> 16) and imm != ((TARGET >> 16) + 1): continue
    code = d[off:off+4*33]
    regs = {}
    for ins in md.disasm(code, va(off)):
        m, ops = ins.mnemonic, ins.op_str
        parts = [p.strip() for p in ops.split(',')]
        def regnum(r): return int(r[1:]) if r.startswith('r') else None
        def val(s):
            try: return int(s, 0)
            except Exception: return None
        if m == 'lis' and len(parts) == 2:
            rn = regnum(parts[0]); v = val(parts[1])
            if rn is not None and v is not None: regs[rn] = ((v & 0xFFFF) << 16)
        elif m in ('addi','addis') and len(parts) == 3:
            rd, ra, v = regnum(parts[0]), regnum(parts[1]), val(parts[2])
            if rd is not None and ra in regs and v is not None:
                regs[rd] = (regs[ra] + (v << 16 if m=='addis' else v)) & 0xFFFFFFFF
        elif m in ('ori','oris') and len(parts) == 3:
            rd, ra, v = regnum(parts[0]), regnum(parts[1]), val(parts[2])
            if rd is not None and ra in regs and v is not None:
                regs[rd] = (regs[ra] | (v << 16 if m=='oris' else v)) & 0xFFFFFFFF
        elif m == 'mr' and len(parts) == 2:
            rd, ra = regnum(parts[0]), regnum(parts[1])
            if rd is not None and ra in regs: regs[rd] = regs[ra]
        else:
            mm = mem_re.match(parts[-1]) if parts else None
            if mm:
                rn = regnum(mm.group(2))
                if rn is not None and rn in regs:
                    disp = val(mm.group(1))
                    if disp is not None:
                        ea = (regs[rn] + disp) & 0xFFFFFFFF
                        t = tag(ea)
                        if t: rows.append((hex(ins.address), m, hex(ea), t, 'memEA'))
            continue
        for rn, v in list(regs.items()):
            t = tag(v)
            if t: rows.append((hex(ins.address), m, hex(v), t, 'reg r%d' % rn))
seen = set(); out = []
for r in rows:
    k = (r[0], r[2], r[4])
    if k in seen: continue
    seen.add(k); out.append(r)
for r in out: print(r)
print('total unique hits:', len(out))
with open('/home/hatch/workspace/_doa4p2-scratch/p11/streamobj_hits2.csv','w',newline='') as f:
    wcsv = csv.writer(f); wcsv.writerow(['site_va','insn','value','tag','how']); wcsv.writerows(out)
