import struct, json, sys, os
def load(p):
    d=open(p,'rb').read()
    ln=struct.unpack_from('<I',d,12)[0]
    j=json.loads(d[20:20+ln])
    binofs=20+ln+8
    return j,d,binofs
def acc(j,d,binofs,ai):
    a=j['accessors'][ai]; bv=j['bufferViews'][a.get('bufferView',0)]
    off=binofs+bv.get('byteOffset',0)+a.get('byteOffset',0)
    n=a['count']; t=a['type']; ct=a['componentType']
    fmt={5126:'f',5123:'H',5125:'I'}[ct]; sz={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[t]
    stride=bv.get('byteStride') or sz*struct.calcsize(fmt)
    out=[]
    for i in range(n):
        out.append(struct.unpack_from('<'+fmt*sz, d, off+i*stride))
    return out
for p in sys.argv[1:]:
    j,d,bo=load(p)
    allv=[]
    for m in j['meshes']:
        for pr in m['primitives']:
            allv+=acc(j,d,bo,pr['attributes']['POSITION'])
    xs=[v[0] for v in allv]; ys=[v[1] for v in allv]; zs=[v[2] for v in allv]
    # GLB up axis = Y. bands along Y in 10 slices: vertex share + XZ width
    lo,hi=min(ys),max(ys); h=hi-lo or 1
    bands=[]
    for b in range(10):
        sel=[v for v in allv if lo+h*b/10 <= v[1] < lo+h*(b+1)/10]
        w=(max((v[0] for v in sel),default=0)-min((v[0] for v in sel),default=0))
        bands.append(f'{len(sel)/len(allv):.2f}/{w:.2f}')
    nj=len(j['skins'][0]['joints']) if j.get('skins') else 0
    print(f"{os.path.basename(p)}: verts={len(allv)} joints={nj} X[{min(xs):.2f},{max(xs):.2f}] Y[{lo:.2f},{hi:.2f}] Z[{min(zs):.2f},{max(zs):.2f}] bands(share/xwidth)={' '.join(bands)}")
