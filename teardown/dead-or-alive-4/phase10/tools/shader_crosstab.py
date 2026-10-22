#!/usr/bin/env python3
"""Phase 10 Job 4a: shader-class cross-tab for chrone pkg00.
Re-parses ObjGeo item records (+0x030 shader class) and GeoDecl records from
the phase-4 chrone head+mid bins + phase-3 assembly graph; joins decl->item
by (object, stream, index_count) exact, else (object, stream) containment of
the decl index range in the item range; cross-tabs class vs the 3 proven
assignments and the phase-6 UV top-1 (tex_assign.json)."""
import struct, json
from collections import defaultdict, Counter
S='/home/hatch/workspace/_doa4p2-scratch/'
d=open(S+'p4/chrone_head.bin','rb').read()+open(S+'p4/chrone_mid.bin','rb').read()
g=json.load(open(S+'work/chrone_pkg00_graph.json'))
def u32(o): return struct.unpack('>I', d[o:o+4])[0]
items={}   # obj -> [(start,count,stream,cls)]
decls=[]   # (global_id, obj, local_idx, stream, vtx, idxcount)
gid=0
for obj in g['objects']:
    oi=obj['index']; og=obj['objgeo']['offset']; cnt=obj['objgeo']['count']; tab=u32(og+0x20)
    il=[]
    for j in range(cnt):
        it=og+u32(og+tab+j*4)
        il.append((u32(it+0x10), u32(it+0x14), u32(it+0x18), u32(it+0x30)))
    items[oi]=il
    gd=og+obj['objgeo']['geodecl_off']; gcnt=u32(gd+0x14); gtab=u32(gd+0x20)
    for i in range(gcnt):
        rec=gd+u32(gd+gtab+i*4)
        decls.append((gid, oi, i, u32(rec+0x18), u32(rec+0x14), u32(rec+0xc)))
        gid+=1
print('items total', sum(len(v) for v in items.values()), 'decls', len(decls))
print('class census (items):', Counter(c for v in items.values() for _,_,_,c in v))
ta=json.load(open(S+'p6/tex_assign.json'))
proven={1:30, 12:40, 30:40}
join={}
for (did, oi, li, stream, vtx, idxc) in decls:
    cand=[it for it in items[oi] if it[2]==stream and it[1]==idxc]
    if not cand: cand=[it for it in items[oi] if it[2]==stream]
    join[did]=cand[0][3] if cand else None
print('decl->class for proven:', {k: join.get(k) for k in proven})
ct=defaultdict(Counter)
for did,cls in join.items():
    if cls is None or str(did) not in ta: continue
    ct[cls][ta[str(did)][0][1]]+=1
for cls in sorted(ct, key=lambda x: (x is None, x)):
    print('class', cls, 'UV-top1 tex counts:', dict(ct[cls].most_common(6)))
# gate: does any class->tex rule reproduce all 3 proven?
byclass={}
ok=True
for did,tex in proven.items():
    c=join.get(did)
    if c in byclass and byclass[c]!=tex: ok=False
    byclass[c]=tex
print('class->tex consistent with all 3 proven:', ok, byclass)
json.dump({str(k):v for k,v in join.items()}, open('/home/hatch/workspace/_doa4p2-scratch/p10/decl_class.json','w'), indent=0)
