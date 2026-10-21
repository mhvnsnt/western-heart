import struct, json
S='/home/hatch/workspace/_doa4p2-scratch/'
d=open(S+'p4/chrone_head.bin','rb').read()+open(S+'p4/chrone_mid.bin','rb').read()
g=json.load(open(S+'work/chrone_pkg00_graph.json'))
def u32(o): return struct.unpack('>I', d[o:o+4])[0]
def u16(o): return struct.unpack('>H', d[o:o+2])[0]
for o in g['objects']:
    off=o['objinfo']['offset']; tab=u32(off+0x20)
    if tab!=0xa0: continue
    raw=d[off+0x90:off+0xa0]
    print(f"obj{o['index']:2d} parent={o['hie_node']['parent']:3d} +0x90..a0={raw.hex(' ')} u16s={struct.unpack('>8H', raw)} hdr3c={u32(off+0x3c)}")
# also non-blend: check +0x3c values and any tail
print('--- non-blend +0x3c:', [(o['index'], u32(o['objinfo']['offset']+0x3c)) for o in g['objects'] if u32(o['objinfo']['offset']+0x20)==0x90][:20])
# Hie tree + joint positions for context
for o in g['objects'][:32]:
    t=o['world_matrix'][3]
    print(f"node{o['index']:2d} parent={o['hie_node']['parent']:3d} worldT=({t[0]:+.3f},{t[1]:+.3f},{t[2]:+.3f}) links={o['hie_node']['links']}")
