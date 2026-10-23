import struct, json
S='/home/hatch/workspace/_doa4p2-scratch/'
d=open(S+'p4/chrone_head.bin','rb').read()+open(S+'p4/chrone_mid.bin','rb').read()
g=json.load(open(S+'work/chrone_pkg00_graph.json'))
def u32(o): return struct.unpack('>I', d[o:o+4])[0]
decls={}
for obj in g['objects']:
    og=obj['objgeo']['offset']; gd=og+obj['objgeo']['geodecl_off']
    gcnt=u32(gd+0x14); gtab=u32(gd+0x20)
    for i in range(gcnt):
        rec=gd+u32(gd+gtab+i*4); nelem=u32(rec+0x10)
        elems=[struct.unpack('>3I', d[rec+0x30+e*12:rec+0x30+e*12+12]) for e in range(nelem)]
        usages=[e[2]>>16 for e in elems if e[1]!=0xFFFFFFFF]
        decls[u32(rec+8)]=dict(obj=obj['index'],stream=u32(rec+0x18),vtx=u32(rec+0x14),blend=1 in usages)
walk={int(k):v for k,v in json.load(open(S+'p4/segmap_walk.json')).items()}
ids=sorted(walk)
for a,b in zip(ids, ids[1:]):
    off,st=walk[a]; end=off+decls[a]['vtx']*st; slot=(end+0xFFF)&~0xFFF
    gap=walk[b][0]-slot
    if gap or decls[a]['blend']:
        print(f"decl{a} obj{decls[a]['obj']} blend={decls[a]['blend']} vtx={decls[a]['vtx']} stride={st} gap_after={gap:#x} ({gap}) gap/vtx={gap/decls[a]['vtx']:.2f}")
    # dump gap bytes head for blend decls
    if decls[a]['blend'] and gap>0:
        print('   gap bytes[:64]:', d[slot:slot+64].hex())
