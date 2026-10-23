import struct, json
S='/home/hatch/workspace/_doa4p2-scratch/'
d=open(S+'p4/chrone_head.bin','rb').read()+open(S+'p4/chrone_mid.bin','rb').read()
g=json.load(open(S+'work/chrone_pkg00_graph.json'))
def u32(o): return struct.unpack('>I', d[o:o+4])[0]
def u16(o): return struct.unpack('>H', d[o:o+2])[0]
blend_objs=set()
for obj in g['objects']:
    og=obj['objgeo']['offset']; gd=og+obj['objgeo']['geodecl_off']
    gcnt=u32(gd+0x14); gtab=u32(gd+0x20)
    for i in range(gcnt):
        rec=gd+u32(gd+gtab+i*4); nelem=u32(rec+0x10)
        elems=[struct.unpack('>3I', d[rec+0x30+e*12:rec+0x30+e*12+12]) for e in range(nelem)]
        if 1 in [e[2]>>16 for e in elems if e[1]!=0xFFFFFFFF]: blend_objs.add(obj['index'])
for o in g['objects']:
    off=o['objinfo']['offset']; tab=u32(off+0x20)
    print(f"obj{o['index']:2d} blend={o['index'] in blend_objs} parent={o['hie_node']['parent']:3d} tab={tab:#x} hdr+0x30..tab: ", d[off+0x30:off+tab].hex(' '))
