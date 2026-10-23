import numpy as np, struct, json, sys
ELEM_SIZE = {0: 12, 3: 12, 6: 12, 5: 8, 2: 4}
def u32(d,o): return struct.unpack('>I', d[o:o+4])[0]
def parse_decls(d, g):
    decls=[]
    for obj in g['objects']:
        og=obj['objgeo']['offset']; gd=og+obj['objgeo']['geodecl_off']
        gcnt=u32(d,gd+0x14); gtab=u32(d,gd+0x20)
        for i in range(gcnt):
            rec=gd+u32(d,gd+gtab+i*4); nelem=u32(d,rec+0x10)
            elems=[struct.unpack('>3I', d[rec+0x30+e*12:rec+0x30+e*12+12]) for e in range(nelem)]
            real=[(e[0], e[2]>>16, (e[2]>>8)&0xFF) for e in elems if e[1]!=0xFFFFFFFF]
            decls.append(dict(decl_id=u32(d,rec+0x08), obj=obj['index'], stream=u32(d,rec+0x18), vtx=u32(d,rec+0x14), idx=u32(d,rec+0x0c), elems=real))
    return decls
def strides(dd):
    out=set()
    for bw in (8,12):
        sizes=dict(ELEM_SIZE); sizes[1]=bw
        out.add(max(boff+sizes.get(u,4) for (boff,u,ui) in dd['elems']))
    return sorted(out)
def validate(d, off, dd, st, lo, hi):
    nv=dd['vtx']
    if off<0 or off+nv*st>len(d): return 0.0
    raw=np.frombuffer(d[off:off+nv*st], dtype='>f4').astype(np.float32)
    A=raw.reshape(nv, st//4)
    P=A[:,:3].astype(np.float64)
    if not np.isfinite(P).all(): return 0.0
    inside=((P>=lo-0.02)&(P<=hi+0.02)).all(axis=1).mean()
    if inside<0.99: return float(inside)
    if st>12:
        N=A[:,3:6].astype(np.float64)
        nl=np.sqrt((N**2).sum(axis=1))
        return float(min(inside, (np.abs(nl-1)<0.06).mean()))
    return float(inside)
def find_segments(d, g, decls):
    bnds={}
    for obj in g['objects']:
        b=obj['objinfo']; c=np.array(b['bounds_center']); e=np.array(b['bounds_extents'])
        bnds[obj['index']]=(c-e, c+e)
    seg={}
    for dd in decls:
        lo,hi=bnds[dd['obj']]
        for off in range(0x8000, len(d), 0x1000):
            for st in strides(dd):
                if validate(d, off, dd, st, lo, hi)>=0.995:
                    seg[dd['decl_id']]=(off,st); break
            if dd['decl_id'] in seg: break
    return seg
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
    while cnt+2<idx and i+2<nv:
        tris.append((i,i+1,i+2)); i+=3; cnt+=4
    return tris

def build(pkgfile, graphfile, outglb, tag):
    d=open(pkgfile,'rb').read()
    g=json.load(open(graphfile))
    decls=parse_decls(d,g)
    seg=find_segments(d,g,decls)
    print(f'[{tag}] segments {len(seg)}/{len(decls)}', flush=True)
    json.dump({str(k):v for k,v in seg.items()}, open(f'{tag}_segmap.json','w'))
    pages=[]
    for off in range(0, len(d)-0x2000, 0x1000):
        v=np.frombuffer(d[off:off+512], dtype='>u2').astype(int)
        if ((v<6000)|(v==0xFFFF)).all() and v.max()>50 and (v<10).sum()>3:
            pages.append(off)
    print(f'[{tag}] index-like pages {len(pages)}', flush=True)
    def parse_seg(dd):
        off,st=seg[dd['decl_id']]; nv=dd['vtx']
        raw=np.frombuffer(d[off:off+nv*st], dtype='>f4').astype(np.float32).reshape(nv, st//4)
        out={}
        for (boff,usage,uidx) in dd['elems']:
            fo=boff//4
            if usage==0: out['pos']=raw[:,fo:fo+3].astype(np.float64)
            elif usage==3: out['nrm']=raw[:,fo:fo+3].astype(np.float32)
            elif usage==5: out[f'uv{uidx}']=raw[:,fo:fo+2].astype(np.float32)
        return out
    meshes=[]; report=[]
    for dd in sorted(decls, key=lambda x:x['decl_id']):
        did=dd['decl_id']
        if did not in seg:
            report.append(f'decl{did} obj{dd["obj"]}: NO SEGMENT [poor]'); continue
        s=parse_seg(dd); P=s['pos']
        if dd['stream']==3:
            tris=seq_tris(dd['idx'], dd['vtx']); how='seq'; qual='clean'
        else:
            diag=np.linalg.norm(P.max(axis=0)-P.min(axis=0)); best=None
            for po in pages:
                full=np.frombuffer(d[po:po+min(dd['idx']*2,0x40000)], dtype='>u2').astype(np.int64)
                if len(full)<dd['idx']: continue
                cand=full[:dd['idx']]
                sv=cand[cand!=0xFFFF]
                if not len(sv) or int(sv.max())>=dd['vtx']: continue
                vals=[int(v) for v in cand if v!=0xFFFF]
                if vals==list(range(len(vals))): continue
                cov=len(set(sv.tolist()))/dd['vtx']
                if cov<0.70: continue
                tr=strip_tris(cand, dd['vtx'])
                if len(tr)<3: continue
                T=P[np.array(tr)]
                e=(np.linalg.norm(T[:,0]-T[:,1],axis=1)+np.linalg.norm(T[:,1]-T[:,2],axis=1)+np.linalg.norm(T[:,2]-T[:,0],axis=1))/3
                sc=float(e.mean()/diag)
                key=(cov,-sc)
                if best is None or key>best[0]: best=(key,po,tr,cov,sc)
            if best is None:
                report.append(f'decl{did} obj{dd["obj"]} s{dd["stream"]}: NO STRIP [poor]'); continue
            tris=best[2]; how=f'page {best[1]:#x} cov {best[3]:.2f} score {best[4]:.3f}'
            qual='clean' if best[4]<0.10 else ('moderate' if best[4]<0.25 else 'poor')
        tris=np.array(tris, dtype=np.int64)
        if 'nrm' in s and len(tris):
            N=s['nrm'].astype(np.float64)
            v0,v1,v2=P[tris[:,0]],P[tris[:,1]],P[tris[:,2]]
            fn=np.cross(v1-v0, v2-v0); vn=N[tris[:,0]]+N[tris[:,1]]+N[tris[:,2]]
            bad=(fn*vn).sum(axis=1)<0
            tris[bad]=tris[bad][:,[0,2,1]]
        meshes.append((f"obj{dd['obj']}_decl{did}", P, s.get('nrm'), s.get('uv0'), tris, dd['obj']))
        report.append(f'decl{did} obj{dd["obj"]} s{dd["stream"]}: {len(tris)} tris {how} [{qual}]')
    for r in report: print(f'[{tag}] {r}', flush=True)
    print(f'[{tag}] meshes {len(meshes)}', flush=True)
    sys.path.insert(0,'.')
    from pkg_glb import write_glb
    write_glb(outglb, meshes)
    # quality summary
    from collections import Counter
    q=Counter(r.split('[')[-1].rstrip(']') for r in report)
    print(f'[{tag}] QUALITY {dict(q)}', flush=True)

if __name__=='__main__':
    build('pkg01_pull.bin', 'pkg01_graph.json', 'chrone_pkg01_v2.glb', 'chrone-pkg01')
    build('chrtwo_head.bin', 'chrtwo_pkg00_graph.json', 'chrtwo_pkg00_v1.glb', 'chrtwo-pkg00')
