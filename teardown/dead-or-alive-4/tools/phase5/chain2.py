import struct, json, numpy as np
S='/home/hatch/workspace/_doa4p2-scratch/'
d=open(S+'p4/chrone_head.bin','rb').read()+open(S+'p4/chrone_mid.bin','rb').read()
g=json.load(open(S+'work/chrone_pkg00_graph.json'))
def u32(o): return struct.unpack('>I', d[o:o+4])[0]
links={o['index']: o['hie_node']['links'] for o in g['objects']}
nxt={}
for i,l in links.items():
    if l[0]<len(links): nxt[l[0]]=i
ring=[]; x=0
for _ in range(len(links)):
    ring.append(x); x=nxt.get(x)
print('ring starting at 0:', ring, 'back to', x)
# test palette mapping v -> ring[v] geometrically
walk={int(k):tuple(v) for k,v in json.load(open(S+'p4/segmap_walk.json')).items()}
joints={o['index']: np.array(o['world_matrix'][3][:3]) for o in g['objects']}
def palette(oi):
    off=g['objects'][oi]['objinfo']['offset']; cnt=u32(off+0x3c)
    return list(struct.unpack(f'>{cnt}H', d[off+0x90:off+0x90+2*cnt]))
score={'direct':[], 'ring':[]}
for obj in g['objects']:
    og=obj['objgeo']['offset']; gd=og+obj['objgeo']['geodecl_off']
    gcnt=u32(gd+0x14); gtab=u32(gd+0x20)
    for i in range(gcnt):
        rec=gd+u32(gd+gtab+i*4); nelem=u32(rec+0x10)
        elems=[struct.unpack('>3I', d[rec+0x30+e*12:rec+0x30+e*12+12]) for e in range(nelem)]
        bw=[e[0] for e in elems if e[1]!=0xFFFFFFFF and (e[2]>>16)==1]
        if not bw or u32(rec+8) not in walk: continue
        did=u32(rec+8); off,st=walk[did]; vtx=u32(rec+0x14)
        raw=np.frombuffer(d[off:off+vtx*st],dtype='>f4').astype(np.float32).reshape(vtx,st//4)
        P=raw[:,:3].astype(np.float64); nbw=(st-bw[0])//4
        Wt=raw[:,bw[0]//4:bw[0]//4+nbw].astype(np.float64)
        pal=palette(obj['index'])
        for k in range(nbw):
            pure=P[Wt[:,k]>0.98]
            if len(pure)<5: continue
            dd=np.linalg.norm(pure-joints[pal[k]],axis=1).min()
            dr=np.linalg.norm(pure-joints[ring[pal[k]]],axis=1).min()
            score['direct'].append(dd); score['ring'].append(dr)
            print(f"decl{did} slot{k} pal={pal[k]} directNode={pal[k]} dist={dd:.3f} ringNode={ring[pal[k]]} dist={dr:.3f}")
print('mean direct', np.mean(score['direct']), 'mean ring', np.mean(score['ring']))
