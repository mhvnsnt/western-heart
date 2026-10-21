import struct, json
from collections import Counter, defaultdict
S='/home/hatch/workspace/_doa4p2-scratch/'
d=open(S+'p4/chrone_head.bin','rb').read()+open(S+'p4/chrone_mid.bin','rb').read()
g=json.load(open(S+'work/chrone_pkg00_graph.json'))
xp=g['xpr2_offset']
def u32(o): return struct.unpack('>I', d[o:o+4])[0]
# directory
recs=[]; pos=xp
while True:
    m=d[pos:pos+4]
    if m in (b'XPR2',b'USER',b'TX2D',b'VBUF',b'IBUF'):
        f1,f2,f3=struct.unpack('>3I', d[pos+4:pos+16]); recs.append((m.decode(),f1,f2,f3)); pos+=16
    elif m==b'\0\0\0\0': pos+=16
    else: break
def desc(f1,n=20): return struct.unpack('>5I', d[xp+f1:xp+f1+20])
vb=[desc(r[1]) for r in recs if r[0]=='VBUF']
ib=[desc(r[1]) for r in recs if r[0]=='IBUF']
tx=[desc(r[1],40) if False else struct.unpack('>10I', d[xp+r[1]:xp+r[1]+40]) for r in recs if r[0]=='TX2D']
print('VBUF descs',len(vb),'IBUF',len(ib),'TX2D',len(tx))
# decl vtx/stride
decls=[]
for obj in g['objects']:
    og=obj['objgeo']['offset']; gd=og+obj['objgeo']['geodecl_off']
    gcnt=u32(gd+0x14); gtab=u32(gd+0x20)
    for i in range(gcnt):
        rec=gd+u32(gd+gtab+i*4); nelem=u32(rec+0x10)
        elems=[struct.unpack('>3I', d[rec+0x30+e*12:rec+0x30+e*12+12]) for e in range(nelem)]
        usages=[(e[0],e[2]>>16) for e in elems if e[1]!=0xFFFFFFFF]
        decls.append((u32(rec+8), obj['index'], u32(rec+0x18), u32(rec+0x14), 1 in [u for _,u in usages], usages))
sizes=Counter(v[2] for v in vb)
print('VBUF size histogram (top):', sizes.most_common(12))
# expected vertex-data sizes
exp={}
for did,oi,st,vtx,blend,us in decls:
    for stride in (12,32,40,44,60,68,72):
        exp.setdefault(vtx*stride+2, []).append((did,stride))
matched=0; unmatched=[]
for i,v in enumerate(vb):
    if v[2] in exp: matched+=1
    else: unmatched.append((i,v[1],v[2],v[3]))
print('VBUF descs matching vtx*stride+2:', matched, '/', len(vb))
print('UNMATCHED VBUF descs (idx, addr, size, type):')
for u in unmatched: print(' ',u)
# check unmatched sizes against vtx*4+2, vtx*2+2, vtx+2 for blend decls
bvtx={vtx for *_,vtx,blend,_u in [(d[0],d[1],d[2],d[3],d[4],d[5]) for d in decls] if blend}
bvtxs={d[3] for d in decls if d[4]}
print('blend vtx counts:', sorted(bvtxs))
for i,addr,size,typ in unmatched:
    for v in sorted(bvtxs):
        if size-2 in (v*4, v*2, v*1, v*8): print(f'  desc{i} size {size} == blendvtx {v} * {(size-2)//v} +2')
