import struct, json
from collections import defaultdict
S='/home/hatch/workspace/_doa4p2-scratch/'
d=open(S+'p4/chrone_head.bin','rb').read()+open(S+'p4/chrone_mid.bin','rb').read()
g=json.load(open(S+'work/chrone_pkg00_graph.json'))
def u32(o): return struct.unpack('>I', d[o:o+4])[0]
for obj in g['objects'][:6]:
    og=obj['objgeo']['offset']; gd=og+obj['objgeo']['geodecl_off']
    gcnt=u32(gd+0x14); gtab=u32(gd+0x20)
    offs=[u32(gd+gtab+i*4) for i in range(gcnt)]
    print(f"obj{obj['index']} GeoDecl hdr: name={d[gd:gd+8]} cnt={gcnt} tab={gtab:#x} offs={[hex(x) for x in offs]} gdsize={u32(gd+0x10):#x}")
    for i,ro in enumerate(offs):
        rec=gd+ro; nelem=u32(rec+0x10)
        elems=[struct.unpack('>3I', d[rec+0x30+e*12:rec+0x30+e*12+12]) for e in range(nelem)]
        usages=[(e[2]>>16) for e in elems if e[1]!=0xFFFFFFFF]
        span=(offs[i+1]-ro) if i+1<len(offs) else None
        after=rec+0x30+nelem*12
        tail_bytes=d[after:rec+ (span if span else u32(rec)+0x10)]
        print(f"  decl{u32(rec+8)} stream{u32(rec+0x18)} vtx{u32(rec+0x14)} idx{u32(rec+0xc)} nelem{nelem} usages{usages} payload{u32(rec)} span{span} tail_after_elems({len(tail_bytes)}B)={tail_bytes.hex()}")
