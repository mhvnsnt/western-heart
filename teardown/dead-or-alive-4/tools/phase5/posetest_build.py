import numpy as np, struct, json, sys
BASE='/home/hatch/workspace/_doa4p2-scratch/p4/'
S='/home/hatch/workspace/_doa4p2-scratch/'
d=open(BASE+'chrone_head.bin','rb').read()+open(BASE+'chrone_mid.bin','rb').read()
g=json.load(open(S+'work/chrone_pkg00_graph.json'))
decls={dd['decl_id']:dd for dd in json.load(open(BASE+'decls_full.json'))}
walk={int(k):tuple(v) for k,v in json.load(open(BASE+'segmap_walk.json')).items()}
xp=3502080
def u32(o): return struct.unpack('>I', d[o:o+4])[0]
recs=[]; pos=xp
while pos < len(d)-16:
    magic=d[pos:pos+4]
    if magic in (b'XPR2',b'USER',b'TX2D',b'VBUF',b'IBUF'):
        f1,f2,f3=struct.unpack('>3I', d[pos+4:pos+16]); recs.append((magic.decode(),f1)); pos+=16
    elif magic==b'\x00\x00\x00\x00': pos+=16
    else: break
def desc(f1): return struct.unpack('>5I', d[xp+f1:xp+f1+20])
ibd=[desc(r[1]) for r in recs if r[0]=='IBUF']
IB=0x8C4000
def desc_full(di):
    w0,addr,size,typ,_=ibd[di]
    f=(addr&~3)-IB
    return np.frombuffer(d[f:f+size], dtype='>u2').astype(np.int64)
def palette(oi):
    off=g['objects'][oi]['objinfo']['offset']; cnt=u32(off+0x3c)
    if cnt==0: return []
    return list(struct.unpack(f'>{cnt}H', d[off+0x90:off+0x90+2*cnt]))
def parse_seg(dd, off, st):
    nv=dd['vtx']
    raw=np.frombuffer(d[off:off+nv*st], dtype='>f4').astype(np.float32)
    A=raw.reshape(nv, st//4)
    out={}
    for (boff, usage, uidx) in dd['elems']:
        fo=boff//4
        if usage==0: out['pos']=A[:,fo:fo+3].astype(np.float64)
        elif usage==3: out['nrm']=A[:,fo:fo+3].astype(np.float32)
        elif usage==5: out[f'uv{uidx}']=A[:,fo:fo+2].astype(np.float32)
        elif usage==1: out['bw']=A[:,fo:fo+3].astype(np.float32) if st-boff>=12 else A[:,fo:fo+2].astype(np.float32)
    return out
def strip_tris(s, nv):
    tris=[]; run=[]
    for v in s:
        if v==0xFFFF:
            for i in range(len(run)-2):
                a,b,c=run[i],run[i+1],run[i+2]
                if len({a,b,c})==3 and max(a,b,c)<nv: tris.append((a,b,c) if i%2==0 else (a,c,b))
            run=[]
        else: run.append(int(v))
    for i in range(len(run)-2):
        a,b,c=run[i],run[i+1],run[i+2]
        if len({a,b,c})==3 and max(a,b,c)<nv: tris.append((a,b,c) if i%2==0 else (a,c,b))
    return tris
def seq_tris(idx, nv):
    tris=[]; cnt=0; i=0
    while cnt+2 < idx and i+2 < nv:
        tris.append((i,i+1,i+2)); i+=3; cnt+=4
    return tris
def best_strip(dd, P):
    diag=np.linalg.norm(P.max(axis=0)-P.min(axis=0))
    idx=dd['idx']; best=None
    for di in range(len(ibd)):
        full=desc_full(di)
        if len(full)<idx: continue
        s=full[:idx]
        sv=s[s!=0xFFFF]
        if not len(sv) or int(sv.max())>=dd['vtx']: continue
        vals=[int(v) for v in s if v!=0xFFFF]
        if vals==list(range(len(vals))): continue
        cov=len(set(sv.tolist()))/dd['vtx']
        if cov<0.70: continue
        tris=strip_tris(s, dd['vtx'])
        if len(tris)<3: continue
        T=P[np.array(tris)]
        e=(np.linalg.norm(T[:,0]-T[:,1],axis=1)+np.linalg.norm(T[:,1]-T[:,2],axis=1)+np.linalg.norm(T[:,2]-T[:,0],axis=1))/3
        sc=float(e.mean()/diag)
        key=(cov, -sc)
        if best is None or key>best[0]: best=(key, di, tris, cov, sc)
    return best

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
BEND=int(sys.argv[1]) if len(sys.argv)>1 else 14
DEG=float(sys.argv[2]) if len(sys.argv)>2 else 40.0
OUT=sys.argv[3]
sub=subtree(BEND)
tj=W[BEND][3,:3]; th=np.radians(DEG); c,s=np.cos(th),np.sin(th)
AXIS=int(sys.argv[4]) if len(sys.argv)>4 else 0
R=np.eye(4)
if AXIS==0: R[1,1],R[1,2],R[2,1],R[2,2]=c,-s,s,c
elif AXIS==2: R[0,0],R[0,1],R[1,0],R[1,1]=c,-s,s,c
Tm=np.eye(4); Tm[3,:3]=-tj; Tp=np.eye(4); Tp[3,:3]=tj
M=Tm@R@Tp
def skin(P, Wt, pal):
    out=np.zeros_like(P)
    for k,node in enumerate(pal):
        Wp = W[node]@M if node in sub else W[node]
        Sm = np.linalg.inv(W[node])@Wp
        out += Wt[:,k:k+1] * (np.c_[P, np.ones(len(P))] @ Sm)[:,:3]
    return out

meshes=[]; moved_report=[]
for did, dd in sorted(decls.items()):
    if did not in walk: continue
    off, st = walk[did]
    seg=parse_seg(dd, off, st); P=seg['pos']
    if dd['stream']==3:
        tris=seq_tris(dd['idx'], dd['vtx'])
    else:
        b=best_strip(dd, P)
        if b is None: continue
        tris=b[2]
    tris=np.array(tris, dtype=np.int64)
    if 'nrm' in seg and len(tris):
        N=seg['nrm'].astype(np.float64)
        v0,v1,v2=P[tris[:,0]],P[tris[:,1]],P[tris[:,2]]
        fn=np.cross(v1-v0, v2-v0)
        vn=N[tris[:,0]]+N[tris[:,1]]+N[tris[:,2]]
        bad=(fn*vn).sum(axis=1)<0
        tris[bad]=tris[bad][:,[0,2,1]]
    Pout=P
    if 'bw' in seg:
        pal=palette(dd['obj'])
        Wt=seg['bw'].astype(np.float64)
        # renormalize rows (2-col decls store 2 floats summing to 1; 3-col 3)
        Wt=Wt/Wt.sum(axis=1, keepdims=True)
        assert len(pal)>=Wt.shape[1], f'decl{did} obj{dd["obj"]} pal {pal} vs {Wt.shape[1]} cols'
        Pout=skin(P, Wt, pal)
        disp=np.linalg.norm(Pout-P,axis=1)
        moved_report.append(f'decl{did} obj{dd["obj"]} pal={pal} maxDisp={disp.max():.3f} meanDisp={disp.mean():.3f}')
    meshes.append((f"obj{dd['obj']}_decl{did}", Pout, seg.get('nrm'), seg.get('uv0'), tris, dd['obj']))
for r in moved_report: print(r)
print('meshes:', len(meshes), 'bend node', BEND, 'subtree', sorted(sub))
def write_glb(path, meshes):
    binparts=[]; views=[]; accs=[]; gltf_meshes=[]; nodes=[]
    def add_view(data_bytes, target):
        off=sum(len(p) for p in binparts)
        pad=(4-len(data_bytes)%4)%4
        binparts.append(data_bytes+b'\x00'*pad)
        views.append({'buffer':0,'byteOffset':off,'byteLength':len(data_bytes),'target':target})
        return len(views)-1
    def add_acc(view, comp, count, typ, mn=None, mx=None):
        a={'bufferView':view,'componentType':comp,'count':count,'type':typ}
        if mn is not None: a['min']=mn
        if mx is not None: a['max']=mx
        accs.append(a); return len(accs)-1
    for (name, P, N, UV, T, oi) in meshes:
        pos32=P.astype(np.float32)
        pv=add_view(pos32.tobytes(), 34962)
        pa=add_acc(pv, 5126, len(pos32), 'VEC3', pos32.min(axis=0).tolist(), pos32.max(axis=0).tolist())
        prim={'attributes':{'POSITION':pa}}
        if N is not None:
            nv=add_view(N.astype(np.float32).tobytes(), 34962)
            prim['attributes']['NORMAL']=add_acc(nv, 5126, len(N), 'VEC3')
        if UV is not None:
            uvv=add_view(UV.astype(np.float32).tobytes(), 34962)
            prim['attributes']['TEXCOORD_0']=add_acc(uvv, 5126, len(UV), 'VEC2')
        idx32=T.reshape(-1).astype(np.uint32)
        iv=add_view(idx32.tobytes(), 34963)
        prim['indices']=add_acc(iv, 5125, len(idx32), 'SCALAR')
        prim['mode']=4
        gltf_meshes.append({'name':name,'primitives':[prim]})
        nodes.append({'mesh':len(gltf_meshes)-1,'name':name})
    blob=b''.join(binparts)
    gltf={'asset':{'version':'2.0','generator':'doa4-phase5-posetest'},'scene':0,
          'scenes':[{'nodes':list(range(len(nodes)))}],'nodes':nodes,'meshes':gltf_meshes,
          'buffers':[{'byteLength':len(blob)}],'bufferViews':views,'accessors':accs}
    js=json.dumps(gltf).encode()
    js+=b' ' * ((4-len(js)%4)%4)
    out=struct.pack('<4sII', b'glTF', 2, 12+8+len(js)+8+len(blob))
    out+=struct.pack('<II', len(js), 0x4E4F534A)+js
    out+=struct.pack('<II', len(blob), 0x004E4942)+blob
    open(path,'wb').write(out)
    print('wrote', path, len(out), 'bytes')
write_glb(OUT, meshes)
