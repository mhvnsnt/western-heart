import struct, math
from collections import Counter
D='/home/hatch/workspace/_doa4p2-scratch/p7/data/'
d=open(D+'anm.afs','rb').read()
def ent(b):
    c=Counter(b); n=len(b)
    return -sum((v/n)*math.log2(v/n) for v in c.values())
def plaus(seg):
    n=len(seg)//4; ok=0
    for i in range(n):
        v=struct.unpack('>I', seg[i*4:i*4+4])[0]
        f=struct.unpack('>f', seg[i*4:i*4+4])[0]
        if f==f and abs(f)<=2.0 and f!=0.0: ok+=1
    return ok/n
prev=None
for w in range(0, len(d), 4096):
    seg=d[w:w+4096]
    e=ent(seg); pl=plaus(seg); rz=seg.count(0)/len(seg)
    cat='FLOAT' if pl>0.85 else ('ZERO' if rz>0.45 else 'OTHER')
    if cat!=prev:
        print(f"@{w:#08x} ent={e:.2f} plaus={pl:.2f} rawzero={rz:.2f} [{cat}]")
        prev=cat
print("\nsample floats @0x70000 (first 48):")
vals=struct.unpack('>48f', d[0x70000:0x70000+192])
print([round(v,4) for v in vals])
print("\nsample floats @0x2b0000 (first 48):")
vals=struct.unpack('>48f', d[0x2b0000:0x2b0000+192])
print([round(v,4) for v in vals])
print("\nbytes @0x6c000 (transition):", d[0x6c000:0x6c040].hex())
print("bytes @0x6b000:", d[0x6b000:0x6b040].hex())
