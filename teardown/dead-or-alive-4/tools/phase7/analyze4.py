import struct, math
from collections import Counter
D='/home/hatch/workspace/_doa4p2-scratch/p7/data/'
d=open(D+'anm.afs','rb').read()
def ent(b):
    c=Counter(b); n=len(b)
    return -sum((v/n)*math.log2(v/n) for v in c.values())
def strict_plaus(seg):
    # fraction of BE u32s that are 'normal-looking' floats: exponent byte patterns
    # first byte in 0x3d..0x40 / 0xbd..0xc0 (values ~0.03..8) or 0x00 (zero/small int)
    n=len(seg)//4; ok=0; zero=0
    for i in range(n):
        b0=seg[i*4]
        if b0==0: zero+=1
        if b0 in (0x3d,0x3e,0x3f,0x40,0xbd,0xbe,0xbf,0xc0): ok+=1
    return ok/n, zero/n
print("anm 4KB map: off ent strictfloat zerofrac rawzero")
prev=None
for w in range(0, len(d), 4096):
    seg=d[w:w+4096]
    e=ent(seg); sp,zf=strict_plaus(seg); rz=seg.count(0)/len(seg)
    cat='FLOAT' if sp>0.6 else ('ZERO' if rz>0.5 else 'OTHER')
    if cat!=prev:
        print(f"  @{w:#08x} ent={e:.2f} strict={sp:.2f} u32zero={zf:.2f} rawzero={rz:.3f} [{cat}]")
        prev=cat
print("\nboundary detail 0x68000-0x70000 (256B windows ent):")
for w in range(0x68000,0x70000,256):
    seg=d[w:w+256]
    print(f"  @{w:#08x} ent={ent(seg):.2f} rawzero={seg.count(0)/len(seg):.2f} head={seg[:16].hex()}")
