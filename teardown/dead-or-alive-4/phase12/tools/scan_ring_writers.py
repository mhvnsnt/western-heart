#!/usr/bin/env python3
"""Phase 12 scans (true frame VA=0x82000000+fileoff for .text):
A) every store site targeting the ring tag array (stream obj +0xBE8 idiom):
   const-prop from lis materializing 0x8340 hi, track addi -0x5C30 -> obj base,
   then addi +0xBE8/+0xBF0/+0xBF8 array bases, then stwx/stdx/stw/std nearby.
B) materializations of TX2D/VBUF/IBUF descriptor TYPE constants 0x30001/0x20001/0x10001.
"""
import struct, re
from capstone import Cs, CS_ARCH_PPC, CS_MODE_BIG_ENDIAN, CS_MODE_32
d=open('/home/hatch/workspace/_doa4p8-clone/teardown/dead-or-alive-4/workdir/default_pe.bin','rb').read()
md=Cs(CS_ARCH_PPC, CS_MODE_BIG_ENDIAN|CS_MODE_32)
TEXT_LO, TEXT_HI = 0x2D1800, 0x2D1800+0x86AE00
def VA(o): return 0x82000000+o
words=struct.unpack('>%dI'%(len(d)//4), d[:len(d)//4*4])
# --- Scan B first (simple): lis/ori or li sequences building 0x30001 etc.
targets={0x30001:'TX2D',0x20001:'IBUF',0x10001:'VBUF'}
hitsB=[]
for o in range(TEXT_LO, TEXT_HI, 4):
    w=words[o//4]
    # ori rD, rA, 0x0001 with rA holding 0x30000/0x20000/0x10000 from lis/addis: check prev word
    if (w>>26)==24 and (w&0xFFFF)==1:  # ori
        prev=words[o//4-1]
        if (prev>>26) in (15,17):  # lis/addis
            hi=(prev&0xFFFF)<<16
            if hi in (0x30000,0x20000,0x10000):
                hitsB.append((VA(o), targets[hi+1], hex(hi+1)))
print("Scan B (descriptor type materializations):", len(hitsB))
for h in hitsB[:40]: print("  ", hex(h[0]), h[1], h[2])
# --- Scan A: stream-obj materialization sites + nearby ring stores
sites=[]
for o in range(TEXT_LO, TEXT_HI, 4):
    w=words[o//4]
    if (w>>26)!=15 or (w&0xFFFF)!=0x8340: continue
    # disasm 48 insns, const-prop
    regs={}
    ringstore=[]
    for ins in md.disasm(d[o:o+4*48], VA(o)):
        parts=[p.strip() for p in ins.op_str.split(',')]
        m=ins.mnemonic
        def rn(s):
            try: return int(s[1:])
            except: return None
        def vl(s):
            try: return int(s,0)
            except: return None
        if m=='lis' and len(parts)==2:
            r,v=rn(parts[0]),vl(parts[1])
            if r is not None and v is not None: regs[r]=((v&0xFFFF)<<16)
        elif m in ('addi','addis') and len(parts)==3:
            rd,ra,v=rn(parts[0]),rn(parts[1]),vl(parts[2])
            if rd is not None and ra in regs and v is not None:
                regs[rd]=(regs[ra]+(v<<16 if m=='addis' else v))&0xFFFFFFFF
        elif m in ('ori','oris') and len(parts)==3:
            rd,ra,v=rn(parts[0]),rn(parts[1]),vl(parts[2])
            if rd is not None and ra in regs and v is not None:
                regs[rd]=(regs[ra]|(v<<16 if m=='oris' else v))&0xFFFFFFFF
        elif m=='mr' and len(parts)==2:
            rd,ra=rn(parts[0]),rn(parts[1])
            if rd is not None and ra in regs: regs[rd]=regs[ra]
        if m in ('stw','std','stwx','stdx','stb','stbx'):
            for r,v in regs.items():
                if v in (0x833FA3D0+0xBE8, 0x833FA3D0+0xBF0, 0x833FA3D0+0xBF8):
                    ringstore.append((hex(ins.address), m, ins.op_str, hex(v-0x833FA3D0)))
        # also direct disp stores: stw rX, 0xBE8(rB) where rB==obj
        mm=re.match(r'^-?(0x[0-9a-f]+|\d+)\((r\d+)\)$', parts[-1]) if parts else None
        if mm and m in ('stw','std','stb'):
            disp=vl(mm.group(1)); base=rn(mm.group(2))
            if disp in (0xBE8,0xBF0,0xBF8) and base in regs and regs[base]==0x833FA3D0:
                ringstore.append((hex(ins.address), m, ins.op_str, hex(disp)))
    if ringstore:
        sites.append((VA(o), ringstore))
print("\nScan A (ring-store sites):", len(sites))
for va,rs in sites:
    print("  site", hex(va))
    for r in rs: print("    ", r)
