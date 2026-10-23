import struct, json, sys
from collections import Counter, defaultdict
S='/home/hatch/workspace/_doa4p2-scratch/'
d=open(S+'p4/chrone_head.bin','rb').read()+open(S+'p4/chrone_mid.bin','rb').read()
g=json.load(open(S+'work/chrone_pkg00_graph.json'))
def u32(o): return struct.unpack('>I', d[o:o+4])[0]
def u16(o): return struct.unpack('>H', d[o:o+2])[0]

# decls per obj, blend flag
decls=defaultdict(list)
for obj in g['objects']:
    og=obj['objgeo']['offset']; gd=og+obj['objgeo']['geodecl_off']
    gcnt=u32(gd+0x14); gtab=u32(gd+0x20)
    for i in range(gcnt):
        rec=gd+u32(gd+gtab+i*4); nelem=u32(rec+0x10)
        elems=[struct.unpack('>3I', d[rec+0x30+e*12:rec+0x30+e*12+12]) for e in range(nelem)]
        usages=[(e[2]>>16) for e in elems if e[1]!=0xFFFFFFFF]
        decls[obj['index']].append(dict(id=u32(rec+8), stream=u32(rec+0x18), vtx=u32(rec+0x14), idx=u32(rec+0xc), blend=1 in usages, usages=usages, payload=u32(rec), recsize=None))
blend_objs={k for k,v in decls.items() if any(x['blend'] for x in v)}
print('blend objs:', sorted(blend_objs))
print('decl payload sizes sample:', [(x['id'],x['payload']) for v in decls.values() for x in v][:10])

# ObjGeo header full dump obj0 and a blend obj
for oi in [0, sorted(blend_objs)[0]]:
    og=g['objects'][oi]['objgeo']['offset']
    print(f'--- ObjGeo obj{oi} hdr 0x00-0x80 u32s:')
    print([hex(u32(og+i*4)) for i in range(32)])

# ITEM records full: collect all, per-offset stats
items=[]
for obj in g['objects']:
    og=obj['objgeo']['offset']; cnt=obj['objgeo']['count']; tab=u32(og+0x20)
    for j in range(cnt):
        it=og+u32(og+tab+j*4)
        raw=d[it:it+0x140]
        items.append((obj['index'], j, it, raw, obj['index'] in blend_objs))
print('total items', len(items))
# per u32 offset: distinct values, range, differs blend vs non?
for off in range(0,0x140,4):
    vals=[struct.unpack('>I', r[3][off:off+4])[0] for r in items]
    c=Counter(vals)
    bv={struct.unpack('>I', r[3][off:off+4])[0] for r in items if r[4]}
    nbv={struct.unpack('>I', r[3][off:off+4])[0] for r in items if not r[4]}
    tag=''
    if len(c)<=20: tag=f' vals={sorted(c)[:20]}'
    print(f'item+0x{off:03x}: distinct={len(c)} min={min(vals)} max={max(vals)} blendonly={sorted(bv-nbv)[:8]} nononly={sorted(nbv-bv)[:8]}{tag}')
