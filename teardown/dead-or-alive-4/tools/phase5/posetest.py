import struct, json, numpy as np
S='/home/hatch/workspace/_doa4p2-scratch/'
d=open(S+'p4/chrone_head.bin','rb').read()+open(S+'p4/chrone_mid.bin','rb').read()
g=json.load(open(S+'work/chrone_pkg00_graph.json'))
def u32(o): return struct.unpack('>I', d[o:o+4])[0]
walk={int(k):tuple(v) for k,v in json.load(open(S+'p4/segmap_walk.json')).items()}
W={o['index']: np.array(o['world_matrix']) for o in g['objects']}
parents={o['index']: o['hie_node']['parent'] for o in g['objects']}
def palette(oi):
    off=g['objects'][oi]['objinfo']['offset']; cnt=u32(off+0x3c)
    return list(struct.unpack(f'>{cnt}H', d[off+0x90:off+0x90+2*cnt]))
def subtree(j):
    out=set()
    for k in parents:
        x=k
        while x!=-1:
            if x==j: out.add(k); break
            x=parents[x]
    return out
def bend(j, deg, axis=0):
    tj=W[j][3,:3]; th=np.radians(deg); c,s=np.cos(th),np.sin(th)
    R=np.eye(4)
    if axis==0: R[1,1],R[1,2],R[2,1],R[2,2]=c,s,-s,c
    elif axis==2: R[0,0],R[0,1],R[1,0],R[1,1]=c,s,-s,c
    Tm=np.eye(4); Tm[3,:3]=-tj; Tp=np.eye(4); Tp[3,:3]=tj
    return Tm@R@Tp
def skin(P, Wt, pal, assign, bendnode, deg, axis=0):
    M=bend(bendnode,deg,axis); sub=subtree(bendnode)
    out=np.zeros_like(P)
    for k,node in enumerate(pal):
        src = pal[k] if assign=='A' else pal[len(pal)-1-k]
        Wp = W[src]@M if src in sub else W[src]
        S = np.linalg.inv(W[src])@Wp
        out += Wt[:,k:k+1] * (np.c_[P, np.ones(len(P))] @ S)[:,:3]
    return out
def get_decl(did):
    # find obj/elems
    for obj in g['objects']:
        og=obj['objgeo']['offset']; gd=og+obj['objgeo']['geodecl_off']
        gcnt=u32(gd+0x14); gtab=u32(gd+0x20)
        for i in range(gcnt):
            rec=gd+u32(gd+gtab+i*4)
            if u32(rec+8)!=did: continue
            nelem=u32(rec+0x10)
            elems=[struct.unpack('>3I', d[rec+0x30+e*12:rec+0x30+e*12+12]) for e in range(nelem)]
            bw_off=[e[0] for e in elems if e[1]!=0xFFFFFFFF and (e[2]>>16)==1][0]
            off,st=walk[did]; vtx=u32(rec+0x14)
            raw=np.frombuffer(d[off:off+vtx*st],dtype='>f4').astype(np.float32).reshape(vtx,st//4)
            nbw=(st-bw_off)//4
            return obj['index'], raw[:,:3].astype(np.float64), raw[:,bw_off//4:bw_off//4+nbw].astype(np.float64)
    raise KeyError(did)

for did, bendnode, deg in [(5,13,40),(5,0,40),(9,13,40),(9,8,40),(4,6,40),(4,12,40)]:
    oi,P,Wt=get_decl(did); pal=palette(oi)
    print(f"\ndecl{did} obj{oi} palette={pal} bend node {bendnode} by {deg}deg about X")
    for assign in ('A','B'):
        Q=skin(P,Wt,pal,assign,bendnode,deg)
        disp=np.linalg.norm(Q-P,axis=1)
        line=f"  assign {assign}: "
        for k in range(Wt.shape[1]):
            pure=Wt[:,k]>0.98
            if pure.sum(): line+=f"w{k}-pure(n={pure.sum()}) meanDisp={disp[pure].mean():.4f} maxDisp={disp[pure].max():.4f} | "
        line+=f"allmax={disp.max():.4f}"
        print(line)
