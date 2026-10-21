import struct, json, numpy as np
S='/home/hatch/workspace/_doa4p2-scratch/'
d=open(S+'p4/chrone_head.bin','rb').read()+open(S+'p4/chrone_mid.bin','rb').read()
g=json.load(open(S+'work/chrone_pkg00_graph.json'))
def u32(o): return struct.unpack('>I', d[o:o+4])[0]
walk={int(k):tuple(v) for k,v in json.load(open(S+'p4/segmap_walk.json')).items()}
joints={o['index']: np.array(o['world_matrix'][3][:3]) for o in g['objects']}
def palette(oi):
    off=g['objects'][oi]['objinfo']['offset']; cnt=u32(off+0x3c)
    return list(struct.unpack(f'>{cnt}H', d[off+0x90:off+0x90+2*cnt]))
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
            # min distance from any joint to the pure set (Hausdorff-ish): use centroid dist + closest joint by min-vertex-dist
            mind=sorted(((np.linalg.norm(pure-jp,axis=1).min(), j) for j,jp in joints.items()))[:3]
            palj = np.linalg.norm(pure-joints[pal[k]],axis=1).min() if pal[k] in joints else -1
            print(f"decl{did} obj{obj['index']} slot{k} pal={pal[k]} pureN={len(pure)} closest joints(min-vert-dist)={[(j,round(float(dd),3)) for dd,j in mind]} palJointMinDist={palj:.3f}")
