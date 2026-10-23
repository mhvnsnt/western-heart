import struct, json
from collections import Counter
S='/home/hatch/workspace/_doa4p2-scratch/'
d=open(S+'p4/chrone_head.bin','rb').read()+open(S+'p4/chrone_mid.bin','rb').read()
g=json.load(open(S+'work/chrone_pkg00_graph.json'))
def u32(o): return struct.unpack('>I', d[o:o+4])[0]
c=Counter()
for obj in g['objects']:
    og=obj['objgeo']['offset']; gd=og+obj['objgeo']['geodecl_off']
    gcnt=u32(gd+0x14); gtab=u32(gd+0x20)
    for i in range(gcnt):
        rec=gd+u32(gd+gtab+i*4); nelem=u32(rec+0x10)
        for e in range(nelem):
            bo,tag,packed=struct.unpack('>3I', d[rec+0x30+e*12:rec+0x30+e*12+12])
            if tag!=0xFFFFFFFF: c[(tag, packed>>16)]+=1
for k,v in sorted(c.items()): print(f'tag={k[0]:#010x} usage={k[1]} count={v}')
# bytes at file offsets equal to tags?
for t in (0x2A23B9,0x2C23A5,0x1A2360):
    print(hex(t), d[t:t+32].hex())
