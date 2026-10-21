import struct
from collections import Counter
D='/home/hatch/workspace/_doa4p2-scratch/p7/data/'
def load(n): return open(D+n,'rb').read()
files={'anm':'anm.afs','chrone':'chrone.head256k.bin','chrtwo':'chrtwo.head256k.bin','chrthree':'chrthree.head256k.bin','mot':'mot.head256k.bin'}
data={k:load(v) for k,v in files.items()}
print("== markers in heads ==")
for k,d in data.items():
    hits={}
    for m in (b'XPR2',b'USER',b'VBUF',b'IBUF',b'TX2D',b'MdlGeo'):
        i=[]; s=0
        while True:
            j=d.find(m,s)
            if j<0: break
            i.append(j); s=j+4
            if len(i)>=4: break
        if i: hits[m.decode('latin1')]=[hex(x) for x in i]
    print(k, hits)
print("\n== repeated 16B blocks at 16-aligned offsets (first 64KB) ==")
for k,d in data.items():
    seg=d[:65536]
    c=Counter(seg[i:i+16] for i in range(0,len(seg)-16,16))
    print(k, [(blk.hex(), n) for blk,n in c.most_common(3) if n>1])
print("\n== repeated 8B blocks at 8-aligned offsets (first 64KB) ==")
for k,d in data.items():
    seg=d[:65536]
    c=Counter(seg[i:i+8] for i in range(0,len(seg)-8,8))
    print(k, [(blk.hex(), n) for blk,n in c.most_common(3) if n>2])
print("\n== anm BE-f32 plausibility in [-2,2] nonzero, by 64KB region ==")
d=data['anm']
for w in range(0, len(d), 0x10000):
    seg=d[w:w+0x10000]
    vals=struct.unpack(f'>{len(seg)//4}I', seg[:len(seg)//4*4])
    ok=0
    for v in vals:
        f=struct.unpack('>f', struct.pack('>I', v))[0]
        if f==f and abs(f)<=2.0 and f!=0.0: ok+=1
    print(f"  @{w:#08x} plausible={ok/len(vals):.3f}")
