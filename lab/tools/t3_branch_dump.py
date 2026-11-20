#!/usr/bin/env python3
"""Dump a T3 USA move slot's branch list (bank rows + divmot99/EXE common rows, CALL 0xC00C / RETURN 0xC00D as BranchFind 0x8002E078).
Run from teardown/tekken3:  python3 ../../lab/tools/t3_branch_dump.py 3 59 127"""
import struct,sys
EXEP="disc/files/TEKKEN3/SLUS_004.02"
exe=open(EXEP,'rb').read()
def eo(a): return a-0x80010000+0x800
def load(p):
    d=open(p,'rb').read(); b=struct.unpack_from('<15I',d,4); return d,b
K,kb=load('animations/divmot03_king.bin'); C,cb=load('animations/divmot99_common.bin')
def row(slot):
    v=struct.unpack_from('<I',K,kb[2]+4*slot)[0]
    if v==0x3FFFFFFF: return None
    if v>=0x40000000: d,b,r=C,cb,v-0x40000000
    else: d,b,r=K,kb,v
    return d,b,b[1]+56*r
def dump(slot):
    d,b,o=row(slot); br=struct.unpack_from('<I',d,o+12)[0]; n=d[o+0x18]
    print(f'slot {slot} frames {n} stance {struct.unpack_from("<H",d,o+16)[0]} air {d[o+0x19]}-{d[o+0x1a]}')
    p=b[0]+12*br
    for k in range(80):
        cmd,res,cond,par,tgt,fl,f0,f1,fe=struct.unpack_from('<HBBHHBBBB',d,p+12*k)
        src='bank'
        if cmd==0xC000: break
        if cmd==0xC00C:
            q=eo(0x80017C78)+12*tgt
            for m in range(40):
                c2,_,cd,_,t2,_,a0,a1,_=struct.unpack_from('<HBBHHBBBB',exe,q+12*m)
                if c2 in (0xC000,0xC00D): break
                print(f'  common[{tgt}+{m}] cmd {c2:04x} dirs {[dd for dd in range(1,10) if c2<0xC000 and c2&(1<<(dd+4))]} cond {cd} -> {t2} win {a0}-{a1}')
            continue
        dirs=[dd for dd in range(1,10) if cmd<0xC000 and cmd&(1<<(dd+4))]
        print(f'  {src:6} cmd {cmd:04x} btn {cmd&0xf:x} dirs {dirs} cond {cond} par {par} -> {tgt} win {f0}-{f1}')
for s in map(int,sys.argv[1:]): dump(s)
