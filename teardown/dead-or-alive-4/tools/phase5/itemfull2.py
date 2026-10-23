import struct, json
from collections import Counter
S='/home/hatch/workspace/_doa4p2-scratch/'
d=open(S+'p4/chrone_head.bin','rb').read()+open(S+'p4/chrone_mid.bin','rb').read()
g=json.load(open(S+'work/chrone_pkg00_graph.json'))
def u32(o): return struct.unpack('>I', d[o:o+4])[0]
# blend decl streams per obj: decl stream dstream; item stream = dstream+1 if dstream<3 else 3
blend_stream={}
for obj in g['objects']:
    og=obj['objgeo']['offset']; gd=og+obj['objgeo']['geodecl_off']
    gcnt=u32(gd+0x14); gtab=u32(gd+0x20)
    for i in range(gcnt):
        rec=gd+u32(gd+gtab+i*4); nelem=u32(rec+0x10)
        elems=[struct.unpack('>3I', d[rec+0x30+e*12:rec+0x30+e*12+12]) for e in range(nelem)]
        usages=[e[2]>>16 for e in elems if e[1]!=0xFFFFFFFF]
        if 1 in usages:
            ds=u32(rec+0x18); blend_stream.setdefault(obj['index'],set()).add(ds+1 if ds<3 else 3)
items=[]
for obj in g['objects']:
    og=obj['objgeo']['offset']; tab=u32(og+0x20)
    for j in range(obj['objgeo']['count']):
        it=og+u32(og+tab+j*4); raw=d[it:it+0x140]
        st=struct.unpack('>I', raw[0x18:0x1c])[0]
        items.append((obj['index'],j,raw, st in blend_stream.get(obj['index'],set())))
print('items total',len(items),'blend-stream items',sum(1 for x in items if x[3]))
# hex dump two items: first blend-stream item, first non-blend, both stream3 obj with many items: obj0 items are non-blend s3
for name,pick in [('BLEND item example', next(x for x in items if x[3])), ('NONBLEND item example', next(x for x in items if not x[3] and x[2][0x18:0x1c]==b'\0\0\0\3'))]:
    oi,j,raw,bl=pick
    print(f'--- {name}: obj{oi} item{j}')
    for off in range(0,0x140,16):
        print(f'  +0x{off:03x}:', raw[off:off+16].hex(' '))
# per-byte offset stats blend vs non for offsets where distribution differs strongly
import math
for off in range(0x140):
    bv=Counter(x[2][off] for x in items if x[3]); nv=Counter(x[2][off] for x in items if not x[3])
    if set(bv) != set(nv) or len(bv)!=len(nv):
        print(f'byte+0x{off:03x}: blend distinct={sorted(bv)[:12]} nonblend distinct={sorted(nv)[:12]}')
