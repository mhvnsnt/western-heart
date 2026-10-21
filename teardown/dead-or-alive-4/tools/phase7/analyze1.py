import math, struct
from collections import Counter
D='/home/hatch/workspace/_doa4p2-scratch/p7/data/'
def ent(b):
    c=Counter(b); n=len(b)
    return -sum((v/n)*math.log2(v/n) for v in c.values())
def load(n):
    return open(D+n,'rb').read()
files={'anm':'anm.afs','chrone':'chrone.head256k.bin','chrtwo':'chrtwo.head256k.bin','chrthree':'chrthree.head256k.bin','mot':'mot.head256k.bin'}
data={k:load(v) for k,v in files.items()}
print("== first 64 bytes ==")
for k,d in data.items(): print(k, d[:64].hex())
print("\n== anm entropy map (16KB windows, first 1MB + samples) ==")
d=data['anm']
for w in range(0, len(d), 16384):
    seg=d[w:w+16384]
    if w<0x110000 or w%0x100000<16384:
        print(f"  @{w:#08x} ent={ent(seg):.2f} zerofrac={seg.count(0)/len(seg):.3f}")
print("\n== autocorrelation (byte-match fraction), head 64KB ==")
for k,d in data.items():
    seg=d[:65536]
    res=[]
    for P in range(1,65):
        m=sum(1 for i in range(len(seg)-P) if seg[i]==seg[i+P])/(len(seg)-P)
        res.append((m,P))
    res.sort(reverse=True)
    print(k, ' '.join(f"P{p}={m:.3f}" for m,p in res[:6]), f" baseline~{1/256:.3f} P16={dict((p,m) for m,p in res)[16]:.3f}")
print("\n== mod-16 position byte-frequency (TOC heads, first 8192 bytes) ==")
for k,d in data.items():
    seg=d[:8192]
    tops=[]
    for pos in range(16):
        c=Counter(seg[pos::16])
        b,n=c.most_common(1)[0]
        tops.append(f"{b:02x}:{n/len(seg[pos::16]):.2f}")
    print(k, ' '.join(tops))
