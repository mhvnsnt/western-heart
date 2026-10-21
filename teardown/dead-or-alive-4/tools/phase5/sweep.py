import numpy as np, struct, json
BASE='/home/hatch/workspace/_doa4p2-scratch/p4/'
S='/home/hatch/workspace/_doa4p2-scratch/'
d=open(BASE+'chrone_head.bin','rb').read()+open(BASE+'chrone_mid.bin','rb').read()
g=json.load(open(S+'work/chrone_pkg00_graph.json'))
decls={dd['decl_id']:dd for dd in json.load(open(BASE+'decls_full.json'))}
walk={int(k):tuple(v) for k,v in json.load(open(BASE+'segmap_walk.json')).items()}
def u32(o): return struct.unpack('>I', d[o:o+4])[0]
def palette(oi):
    off=g['objects'][oi]['objinfo']['offset']; cnt=u32(off+0x3c)
    return list(struct.unpack(f'>{cnt}H', d[off+0x90:off+0x90+2*cnt])) if cnt else []
def parse_bw(dd, off, st):
    nv=dd['vtx']
    raw=np.frombuffer(d[off:off+nv*st], dtype='>f4').astype(np.float32).reshape(nv, st//4)
    out={}
    for (boff, usage, uidx) in dd['elems']:
        fo=boff//4
        if usage==0: out['pos']=raw[:,fo:fo+3].astype(np.float64)
        elif usage==1: out['bw']=raw[:,fo:fo+3].astype(np.float64) if st-boff>=12 else raw[:,fo:fo+2].astype(np.float64)
    return out
W={o['index']: np.array(o['world_matrix'], dtype=np.float64) for o in g['objects']}
parents={o['index']: o['hie_node']['parent'] for o in g['objects']}
def subtree(j):
    out=set()
    for k in parents:
        x=k
        while x!=-1:
            if x==j: out.add(k); break
            x=parents[x]
    return out
segs={}
for did, dd in sorted(decls.items()):
    if did not in walk: continue
    off, st = walk[did]
    seg=parse_bw(dd, off, st)
    if 'bw' in seg:
        Wt=seg['bw']; Wt=Wt/Wt.sum(axis=1,keepdims=True)
        segs[did]=(dd['obj'], seg['pos'], Wt, palette(dd['obj']))
for bend in range(46):
    sub=subtree(bend)
    if not any(node in sub for _,_,_,pal in segs.values() for node in pal): continue
    tj=W[bend][3,:3]; th=np.radians(40); c,s=np.cos(th),np.sin(th)
    R=np.eye(4); R[0,0],R[0,1],R[1,0],R[1,1]=c,-s,s,c
    Tm=np.eye(4); Tm[3,:3]=-tj; Tp=np.eye(4); Tp[3,:3]=tj; M=Tm@R@Tp
    moved=[]
    for did,(oi,P,Wt,pal) in segs.items():
        out=np.zeros_like(P)
        for k,node in enumerate(pal):
            Wp=W[node]@M if node in sub else W[node]
            Sm=np.linalg.inv(W[node])@Wp
            out+=Wt[:,k:k+1]*(np.c_[P,np.ones(len(P))]@Sm)[:,:3]
        disp=np.linalg.norm(out-P,axis=1)
        sel=disp>0.05
        if sel.sum()>20: moved.append((did, int(sel.sum()), np.round(P[sel].mean(axis=0),2).tolist()))
    if moved:
        allc=np.average([m[2] for m in moved], axis=0, weights=[m[1] for m in moved])
        print(f'bend node {bend} (worldT {np.round(W[bend][3,:3],2).tolist()} parent {parents[bend]}): displaced centroid {np.round(allc,2).tolist()} decls={[(m[0],m[1]) for m in moved]}')
