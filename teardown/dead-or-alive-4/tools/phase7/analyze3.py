import struct, math
from collections import Counter
D='/home/hatch/workspace/_doa4p2-scratch/p7/data/'
def load(n): return open(D+n,'rb').read()
def ent(b):
    c=Counter(b); n=len(b)
    return -sum((v/n)*math.log2(v/n) for v in c.values())
def plaus(seg):
    vals=struct.unpack(f'>{len(seg)//4}I', seg[:len(seg)//4*4])
    ok=0
    for v in vals:
        f=struct.unpack('>f', struct.pack('>I', v))[0]
        if f==f and abs(f)<=2.0 and f!=0.0: ok+=1
    return ok/len(vals)
files={'anm':'anm.afs','chrone':'chrone.head256k.bin','chrtwo':'chrtwo.head256k.bin','chrthree':'chrthree.head256k.bin','mot':'mot.head256k.bin'}
for k,fn in files.items():
    d=load(fn)
    print(f"== {k}: entropy/plausibility per 16KB window (first 256KB) ==")
    for w in range(0, min(len(d),262144), 16384):
        seg=d[w:w+16384]
        print(f"  @{w:#08x} ent={ent(seg):.2f} plaus={plaus(seg):.3f} zero={seg.count(0)/len(seg):.3f}")
