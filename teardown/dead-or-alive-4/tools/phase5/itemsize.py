import struct, json
S='/home/hatch/workspace/_doa4p2-scratch/'
d=open(S+'p4/chrone_head.bin','rb').read()+open(S+'p4/chrone_mid.bin','rb').read()
g=json.load(open(S+'work/chrone_pkg00_graph.json'))
def u32(o): return struct.unpack('>I', d[o:o+4])[0]
blend_stream={}
declmap={}
for obj in g['objects']:
    og=obj['objgeo']['offset']; gd=og+obj['objgeo']['geodecl_off']
    gcnt=u32(gd+0x14); gtab=u32(gd+0x20)
    for i in range(gcnt):
        rec=gd+u32(gd+gtab+i*4); nelem=u32(rec+0x10)
        elems=[struct.unpack('>3I', d[rec+0x30+e*12:rec+0x30+e*12+12]) for e in range(nelem)]
        usages=[e[2]>>16 for e in elems if e[1]!=0xFFFFFFFF]
        ds=u32(rec+0x18); declmap[(obj['index'],ds)]=1 in usages
        if 1 in usages: blend_stream.setdefault(obj['index'],set()).add(ds+1 if ds<3 else 3)
rows=[]
for obj in g['objects']:
    og=obj['objgeo']['offset']; tab=u32(og+0x20); cnt=obj['objgeo']['count']
    offs=[u32(og+tab+j*4) for j in range(cnt)]
    for j,ro in enumerate(offs):
        size=(offs[j+1]-ro) if j+1<len(offs) else obj['objgeo']['size']-ro
        it=og+ro; st=u32(it+0x18)
        bl = st in blend_stream.get(obj['index'],set())
        rows.append((obj['index'],j,size,st,bl,it))
from collections import Counter
print(Counter((r[2],r[4]) for r in rows))
print(Counter((r[3],r[2],r[4]) for r in rows))
# dump extra region of first few 0x190 items, blend and not
for want_blend in (True,False):
    ex=[r for r in rows if r[2]==0x190 and r[4]==want_blend][:2]
    for oi,j,size,st,bl,it in ex:
        print(f'--- 0x190 item obj{oi} item{j} stream{st} blend={bl} extra +0x140..0x190:')
        print('   ', d[it+0x140:it+0x190].hex(' '))
        print('    as u16:', struct.unpack('>40H', d[it+0x140:it+0x190]))
        print('    as u32:', struct.unpack('>20I', d[it+0x140:it+0x190]))
