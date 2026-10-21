import struct, json, numpy as np
S='/home/hatch/workspace/_doa4p2-scratch/'
d=open(S+'p4/chrone_head.bin','rb').read()+open(S+'p4/chrone_mid.bin','rb').read()
g=json.load(open(S+'work/chrone_pkg00_graph.json'))
def u32(o): return struct.unpack('>I', d[o:o+4])[0]
walk={int(k):tuple(v) for k,v in json.load(open(S+'p4/segmap_walk.json')).items()}
joints={o['index']: np.array(o['world_matrix'][3][:3]) for o in g['objects']}
parents={o['index']: o['hie_node']['parent'] for o in g['objects']}
decls={}
for obj in g['objects']:
    og=obj['objgeo']['offset']; gd=og+obj['objgeo']['geodecl_off']
    gcnt=u32(gd+0x14); gtab=u32(gd+0x20)
    for i in range(gcnt):
        rec=gd+u32(gd+gtab+i*4); nelem=u32(rec+0x10)
        elems=[struct.unpack('>3I', d[rec+0x30+e*12:rec+0x30+e*12+12]) for e in range(nelem)]
        real=[(e[0],e[2]>>16) for e in elems if e[1]!=0xFFFFFFFF]
        if 1 in [u for _,u in real]:
            decls[u32(rec+8)]=(obj['index'], u32(rec+0x18), u32(rec+0x14), dict(real))
for did,(oi,st,vtx,elems) in sorted(decls.items()):
    if did not in walk: print(did,'no walk'); continue
    off,stride=walk[did]
    raw=np.frombuffer(d[off:off+vtx*stride],dtype='>f4').astype(np.float32).reshape(vtx,stride//4)
    P=raw[:,:3].astype(np.float64)
    bwoff=[o for o,u in elems.items() if u==1][0] if False else [o for o,u in [(e[0],e[1]) for e in [(k,v) for k,v in elems.items()]]]
    # elems is dict offset->usage? we built dict(real) offset:usage reversed? real was (boff,usage) so dict maps boff->usage
    bw_off=[bo for bo,us in elems.items() if us==1][0]
    nbw=(stride-bw_off)//4
    W=raw[:, bw_off//4:bw_off//4+nbw].astype(np.float64)
    print(f"\ndecl{did} obj{oi} (parent {parents[oi]}) vtx{vtx} stride{stride} bw@{bw_off} n={nbw} wsum err max={np.abs(W.sum(1)-1).max():.3f} wrange=[{W.min():.3f},{W.max():.3f}]")
    # pure clusters
    for k in range(nbw):
        pure=np.where(W[:,k]>0.98)[0]
        if len(pure):
            c=P[pure].mean(axis=0)
            dists=sorted(((np.linalg.norm(c-joints[j]),j) for j in joints))[:3]
            print(f"  w{k} pure n={len(pure)} centroid={np.round(c,3)} nearest joints={[(j,round(dd,3)) for dd,j in dists]}")
    # weight value histogram for k=0
    hist=np.histogram(W[:,0],bins=[0,.01,.25,.5,.75,.99,1.01])[0]
    print(f"  w0 hist [0,.01,.25,.5,.75,.99,1]: {hist}")
