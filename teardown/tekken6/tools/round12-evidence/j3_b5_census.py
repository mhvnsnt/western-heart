#!/usr/bin/env python3
import struct, os, glob, json, collections
import numpy as np
DEC='/home/hatch/workspace/_t6r4-work/decoded76'
def slots_of(data):
    n, hs = struct.unpack_from('<II', data, 0)
    out=[]; start=hs
    for i in range(n):
        sz, end = struct.unpack_from('<II', data, 8+i*8)
        out.append((start, sz)); start = end if end else start
    return out
f=glob.glob(os.path.join(DEC,'idx24_*.bin'))[0]
data=open(f,'rb').read()
off, sz = slots_of(data)[9]
slot9=data[off:off+sz]
A=np.frombuffer(slot9[448:], dtype=np.uint8).reshape(40,138,16)
print('A grid records:', A.shape)
# header records identical?
for r in range(8):
    same=all(bytes(A[p,r])==bytes(A[0,r]) for p in range(40))
    print(f'rec{r}: identical across 40 pages = {same}  {bytes(A[0,r]).hex()}')
# where do pages start differing?
diff_at=[]
for r in range(138):
    if not all(bytes(A[p,r])==bytes(A[0,r]) for p in range(40)): diff_at.append(r)
print('records that differ across pages: first', diff_at[:5], 'count', len(diff_at), 'of 138')
# 0x800 hunt: LE u32 == 0x800 positions within A pages
pos=collections.Counter()
arr32=np.frombuffer(slot9[448:], dtype='<u4').reshape(40,552)
for p in range(40):
    for i,v in enumerate(arr32[p]):
        if v==0x800: pos[i*4]+=1
print('LE u32==0x800 in-page byte offsets (offset:pagecount):', dict(pos))
# same for BE
posb=collections.Counter()
arr32b=np.frombuffer(slot9[448:], dtype='>u4').reshape(40,552)
for p in range(40):
    for i,v in enumerate(arr32b[p]):
        if v==0x800: posb[i*4]+=1
print('BE u32==0x800 in-page byte offsets:', dict(posb))
# census over data records (rec >= 6)
D=A[:,6:,:].reshape(-1,16)
print('data records:', len(D), 'populated:', int((D!=0).any(axis=1).sum()))
def ent(col):
    v,c=np.unique(col, return_counts=True); p=c/len(col)
    return float(-(p*np.log2(p)).sum()), len(v), [(int(v[k]),int(c[k])) for k in np.argsort(-c)[:4]]
print('pos | entropy | distinct | top')
fm={}
for i in range(16):
    H,nv,top=ent(D[:,i]); fm[i]={'entropy':round(H,3),'distinct':nv,'top':top}
    print(f'{i:3d} | {H:6.3f} | {nv:4d} | {top}')
# GIDX block: rec5 says GIDX; dump records 5..10 of page 0 and page 1
for pg in (0,1):
    print(f'--- page {pg} records 5..12 ---')
    for r in range(5,13): print(r, bytes(A[pg,r]).hex())
# u16 pair structure in data records: are data records pairs of u16 directory-like (0x4060,0x4090)?
cnt=collections.Counter()
for r in D: cnt[bytes(r)]+=1
print('distinct data records:', len(cnt), 'most common:', [(k.hex(),v) for k,v in cnt.most_common(6)])
json.dump({'fieldmap_data_records':{str(k):v for k,v in fm.items()}}, open('/tmp/r12/b5_census2.json','w'), indent=1)
