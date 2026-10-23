import struct, json
S='/home/hatch/workspace/_doa4p2-scratch/'
d=open(S+'p4/chrone_head.bin','rb').read()+open(S+'p4/chrone_mid.bin','rb').read()
g=json.load(open(S+'work/chrone_pkg00_graph.json'))
def u32(o): return struct.unpack('>I', d[o:o+4])[0]
for obj in g['objects']:
    og=obj['objgeo']['offset']; tab=u32(og+0x20); cnt=obj['objgeo']['count']
    offs=[u32(og+tab+j*4) for j in range(cnt)]
    steps=[b-a for a,b in zip(offs,offs[1:])]
    gd=og+obj['objgeo']['geodecl_off']
    print(f"obj{obj['index']} size={obj['objgeo']['size']:#x} cnt={cnt} first={offs[0]:#x} steps={set(steps)} geodecl_at={obj['objgeo']['geodecl_off']:#x} gdsize={u32(gd+0x10):#x} end_items={(offs[-1]+0x140 if offs else 0):#x}")
