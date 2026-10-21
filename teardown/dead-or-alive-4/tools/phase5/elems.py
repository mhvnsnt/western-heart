import struct, json
S='/home/hatch/workspace/_doa4p2-scratch/'
d=open(S+'p4/chrone_head.bin','rb').read()+open(S+'p4/chrone_mid.bin','rb').read()
g=json.load(open(S+'work/chrone_pkg00_graph.json'))
def u32(o): return struct.unpack('>I', d[o:o+4])[0]
walk={int(k):v for k,v in json.load(open(S+'p4/segmap_walk.json')).items()}
for obj in g['objects']:
    og=obj['objgeo']['offset']; gd=og+obj['objgeo']['geodecl_off']
    gcnt=u32(gd+0x14); gtab=u32(gd+0x20)
    for i in range(gcnt):
        rec=gd+u32(gd+gtab+i*4); nelem=u32(rec+0x10)
        elems=[struct.unpack('>3I', d[rec+0x30+e*12:rec+0x30+e*12+12]) for e in range(nelem)]
        usages=[e[2]>>16 for e in elems if e[1]!=0xFFFFFFFF]
        if 1 in usages:
            did=u32(rec+8)
            print(f"decl{did} obj{obj['index']} stream{u32(rec+0x18)} vtx{u32(rec+0x14)} walkstride={walk.get(did)}")
            for e in elems: print(f"   elem off={e[0]} tag={e[1]:#010x} packed={e[2]:#010x} usage={e[2]>>16} uidx={(e[2]>>8)&0xff} low={e[2]&0xff}")
