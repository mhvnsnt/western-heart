import struct, json
S='/home/hatch/workspace/_doa4p2-scratch/'
d=open(S+'p4/chrone_head.bin','rb').read()+open(S+'p4/chrone_mid.bin','rb').read()
g=json.load(open(S+'work/chrone_pkg00_graph.json'))
xp=g['xpr2_offset']
def u32(o): return struct.unpack('>I', d[o:o+4])[0]
recs=[]; pos=xp
while True:
    m=d[pos:pos+4]
    if m in (b'XPR2',b'USER',b'TX2D',b'VBUF',b'IBUF'):
        f1,f2,f3=struct.unpack('>3I', d[pos+4:pos+16]); recs.append((m.decode(),f1)); pos+=16
    elif m==b'\0\0\0\0': pos+=16
    else: break
def desc(f1): return struct.unpack('>5I', d[xp+f1:xp+f1+20])
vb=[desc(r[1]) for r in recs if r[0]=='VBUF']
decls=[]
for obj in g['objects']:
    og=obj['objgeo']['offset']; gd=og+obj['objgeo']['geodecl_off']
    gcnt=u32(gd+0x14); gtab=u32(gd+0x20)
    for i in range(gcnt):
        rec=gd+u32(gd+gtab+i*4); nelem=u32(rec+0x10)
        elems=[struct.unpack('>3I', d[rec+0x30+e*12:rec+0x30+e*12+12]) for e in range(nelem)]
        usages=[e[2]>>16 for e in elems if e[1]!=0xFFFFFFFF]
        decls.append((u32(rec+8),obj['index'],u32(rec+0x18),u32(rec+0x14),1 in usages))
vtxset={dd[3]:dd for dd in decls}
for i,v in enumerate(vb):
    size=v[2]
    hits=[]
    for cand in (size, size-2, size+2):
        for vtx,dd in vtxset.items():
            if cand%vtx==0 and 1<=cand//vtx<=80: hits.append((cand,vtx,cand//vtx,dd[0],dd[4]))
    if hits: print(i, 'addr',hex(v[1]),'size',size,'->',hits[:6])
    else: print(i, 'addr',hex(v[1]),'size',size,'-> NO vtx divisor')
