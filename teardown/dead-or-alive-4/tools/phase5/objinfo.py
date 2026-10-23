import struct, json
from collections import Counter
S='/home/hatch/workspace/_doa4p2-scratch/'
d=open(S+'p4/chrone_head.bin','rb').read()+open(S+'p4/chrone_mid.bin','rb').read()
g=json.load(open(S+'work/chrone_pkg00_graph.json'))
def u32(o): return struct.unpack('>I', d[o:o+4])[0]
# ObjInfo structure: header? parse: name at offset, +0x10 size, +0x14 count, +0x20 table_off?
for oi in (0,2,7):
    o=g['objects'][oi]; off=o['objinfo']['offset']
    print(f"obj{oi} ObjInfo @{off:#x} size={o['objinfo']['size']} hdr:", d[off:off+16], [hex(u32(off+i*4)) for i in range(16)])
    print('   bytes 0x40..end:', d[off+0x40:off+o['objinfo']['size']].hex(' '))
# guess item table like named block: +0x20 table offset
items=[]
for o in g['objects']:
    off=o['objinfo']['offset']; cnt=o['objinfo']['count']; tab=u32(off+0x20)
    offs=[u32(off+tab+j*4) for j in range(cnt)]
    steps=[b-a for a,b in zip(offs,offs[1:])]
    for j,ro in enumerate(offs):
        items.append((o['index'],j,off+ro))
    if o['index']<6: print(f"obj{o['index']} tab={tab:#x} offs={[hex(x) for x in offs]} steps={set(steps)}")
print('total objinfo items', len(items))
for oi,j,it in items[:4]:
    print(f'obj{oi} item{j}:', d[it:it+0x50].hex(' '))
# per u32 offset stats
for off in range(0,0x50,4):
    vals=[struct.unpack('>I', d[it+off:it+off+4])[0] for _,_,it in items]
    c=Counter(vals)
    print(f'+0x{off:02x}: distinct={len(c)} common={c.most_common(4)}')
