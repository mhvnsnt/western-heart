from collections import Counter
D='/home/hatch/workspace/_doa4p2-scratch/p7/data/'
d=open(D+'anm.afs','rb').read()
for name, seg in [('anm[0:0x68000]', d[:0x68000]), ('anm[0x68000:0x6c000]', d[0x68000:0x6c000]), ('anm[0x70000:0x170000]', d[0x70000:0x170000])]:
    c=Counter(seg)
    print(f"{name}: distinct bytes={len(c)} top10={[(hex(b), round(n/len(seg),3)) for b,n in c.most_common(10)]}")
# u16 BE histogram on head
seg=d[:0x68000]
import struct
vals=struct.unpack(f'>{len(seg)//2}H', seg)
c=Counter(vals)
print("head u16 distinct:", len(c), "top:", [(hex(v), n) for v,n in c.most_common(10)])
# check 16B record field constancy: records from 0x68000, field at +8
recs=[d[0x68000+i*16:0x68000+(i+1)*16] for i in range(2000)]
for fpos in range(0,16,4):
    c=Counter(r[fpos:fpos+4] for r in recs)
    print(f"field@{fpos}: distinct={len(c)} top={[(v.hex(),n) for v,n in c.most_common(3)]}")
# same for head records (offset 0)
recs0=[d[i*16:(i+1)*16] for i in range(2000)]
for fpos in range(0,16,4):
    c=Counter(r[fpos:fpos+4] for r in recs0)
    print(f"head field@{fpos}: distinct={len(c)} top={[(v.hex(),n) for v,n in c.most_common(3)]}")
