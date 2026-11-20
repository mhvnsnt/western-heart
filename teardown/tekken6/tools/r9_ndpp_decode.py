#!/usr/bin/env python3
"""Tekken 6 PSP NDPP decoder (round 9) - GE display-list units.
Usage: r9_ndpp_decode.py <container.bin> <slot_index> <out.glb>
Decodes one NDPP section of a decoded76 container to a static GLB
(positions+normals). Record semantics: see round9-evidence/JOB1-UNPACK-CRACKED.md
"""
import struct

TC_SZ=[0,2,4,8]; COL_SZ=[0,2,2,2,4]; V3_SZ=[0,3,6,12]; W_SZ=[0,1,2,4]
COMP_SZ=[0,1,2,4]  # per-component byte size by format code

def vtype_layout(vt):
    tc=vt&3; col=(vt>>2)&7; nrm=(vt>>5)&3; pos=(vt>>7)&3; wf=(vt>>9)&3; nw=((vt>>14)&7)+1
    fields=[]; off=0
    def add(name,size,align):
        nonlocal off
        off=(off+align-1)&~(align-1)
        fields.append((name,off,size)); off+=size
    if wf: add('weights', nw*W_SZ[wf], COMP_SZ[wf])
    if tc: add('uv', TC_SZ[tc], COMP_SZ[tc])
    if col: add('color', COL_SZ[col], COMP_SZ[col] if col<4 else 4)
    if nrm: add('normal', V3_SZ[nrm], COMP_SZ[nrm])
    if pos: add('pos', V3_SZ[pos], COMP_SZ[pos])
    stride=(off+3)&~3 if pos==3 else off
    # GE vertex size: total rounded up to position component alignment
    return fields, off, nw, (tc,col,nrm,pos,wf)

def parse_units(sec):
    units=[]; o=0
    while o < len(sec)-8:
        w0,w1=struct.unpack_from('<II',sec,o)
        if (w0>>24)==0x01 and (w1>>16) in (0x0404,0x0403):
            pairs=[]; p=o
            while p < len(sec)-8:
                a,b=struct.unpack_from('<II',sec,p)
                if (a>>24)==0x01 and (b>>16) in (0x0404,0x0403): pairs.append((a&0xffffff,b&0xffff,(b>>16)&0xff)); p+=8
                else: break
            units.append({'off':o-20,'hdr':struct.unpack_from('<IIIII',sec,o-20),'pairs':pairs}); o=p; continue
        o+=4
    return units

def decode_section(sec):
    """returns list of verts: dict(pos=(x,y,z) raw s16, weights, uv, normal, unit, strip)"""
    out=[]
    for u in parse_units(sec):
        vt=u['hdr'][2]&0xffffff
        fields,size,nw,fmt=vtype_layout(vt)
        fd={name:(o,s) for name,o,s in fields}
        # verify stride against table deltas
        for k in range(len(u['pairs'])-1):
            d=u['pairs'][k+1][0]-u['pairs'][k][0]
            assert u['pairs'][k][1]==0 or d==u['pairs'][k][1]*size, (u['off'],k,d,u['pairs'][k][1],size)
        for si,(off,cnt,flag) in enumerate(u['pairs']):
            base=u['off']+off
            for i in range(cnt):
                r=sec[base+i*size: base+i*size+size]
                v={'unit':u['off'],'strip':si,'vtype':vt}
                if 'pos' in fd: v['pos']=struct.unpack_from('<hhh',r,fd['pos'][0])
                if 'weights' in fd: v['weights']=tuple(r[fd['weights'][0]:fd['weights'][0]+fd['weights'][1]])
                if 'uv' in fd: v['uv']=tuple(r[fd['uv'][0]:fd['uv'][0]+fd['uv'][1]])
                if 'normal' in fd: v['normal']=struct.unpack_from('<bbb',r,fd['normal'][0])
                out.append(v)
    return out

def parse_container(data):
    n,hs=struct.unpack_from('<II',data,0)
    chunks=[]; start=hs
    for i in range(n):
        sz,end=struct.unpack_from('<II',data,8+i*8)
        chunks.append((start,sz,data[start:start+4] if sz else b''))
        start=end if end else start
    return chunks
import struct, sys, json

def decode_mesh(sec):
    desc=struct.unpack_from('<12f',sec,20)
    ymax=desc[6]; s=ymax/32767.0
    verts=[]; tris=[]; nrms=[]; uvs=[]; wgts=[]
    for u in parse_units(sec):
        vt=u['hdr'][2]&0xffffff
        fields,size,nw,fmt=vtype_layout(vt)
        fd={n:(o,sz) for n,o,sz in fields}
        for off,cnt,prim in u['pairs']:
            base=u['off']+off; start=len(verts)
            for i in range(cnt):
                r=sec[base+i*size: base+i*size+size]
                x,y,z=struct.unpack_from('<hhh',r,fd['pos'][0])
                verts.append((x*s, y*s, z*s))
                if 'normal' in fd:
                    nx,ny,nz=struct.unpack_from('<bbb',r,fd['normal'][0]); nrms.append((nx/127,ny/127,nz/127))
                else: nrms.append((0,1,0))
                if 'uv' in fd: uvs.append((r[fd['uv'][0]]/255, r[fd['uv'][0]+1]/255))
                else: uvs.append((0,0))
                if 'weights' in fd: wgts.append(tuple(b/128 for b in r[fd['weights'][0]:fd['weights'][0]+fd['weights'][1]]))
            idx=list(range(start,start+cnt))
            if prim==4:  # triangle strip
                for k in range(cnt-2):
                    a,b,c=idx[k],idx[k+1],idx[k+2]
                    tris.append((a,b,c) if k%2==0 else (b,a,c))
            elif prim==3:  # triangle list
                for k in range(0,cnt-2,3): tris.append((idx[k],idx[k+1],idx[k+2]))
            else:
                raise ValueError(f'prim {prim}')
    return verts,tris,nrms,uvs,wgts,desc

def write_glb(path, verts, tris, nrms, name):
    import array
    pos=array.array('f'); [pos.extend(v) for v in verts]
    nor=array.array('f'); [nor.extend(n) for n in nrms]
    idx=array.array('I'); [idx.extend(t) for t in tris]
    mins=[min(v[a] for v in verts) for a in range(3)]; maxs=[max(v[a] for v in verts) for a in range(3)]
    binparts=[pos.tobytes(), nor.tobytes(), idx.tobytes()]
    offs=[]; o=0
    for b in binparts: offs.append(o); o+=len(b)
    gltf={"asset":{"version":"2.0","generator":"t6r9 ndpp decode"},
      "scene":0,"scenes":[{"nodes":[0]}],"nodes":[{"mesh":0,"name":name}],
      "meshes":[{"name":name,"primitives":[{"attributes":{"POSITION":0,"NORMAL":1},"indices":2,"mode":4}]}],
      "accessors":[
        {"bufferView":0,"componentType":5126,"count":len(verts),"type":"VEC3","min":mins,"max":maxs},
        {"bufferView":1,"componentType":5126,"count":len(verts),"type":"VEC3"},
        {"bufferView":2,"componentType":5125,"count":len(tris)*3,"type":"SCALAR"}],
      "bufferViews":[
        {"buffer":0,"byteOffset":offs[0],"byteLength":len(binparts[0])},
        {"buffer":0,"byteOffset":offs[1],"byteLength":len(binparts[1])},
        {"buffer":0,"byteOffset":offs[2],"byteLength":len(binparts[2])}],
      "buffers":[{"byteLength":o}]}
    js=json.dumps(gltf).encode(); js+=b' '*( (4-len(js)%4)%4 )
    binb=b''.join(binparts); binb+=b'\x00'*((4-len(binb)%4)%4)
    out=struct.pack('<III',0x46546C67,2,12+8+len(js)+8+len(binb))
    out+=struct.pack('<II',len(js),0x4E4F534A)+js
    out+=struct.pack('<II',len(binb),0x004E4942)+binb
    open(path,'wb').write(out)
    return mins,maxs

if __name__=='__main__':
    d=open(sys.argv[1],'rb').read()
    _n,_hs=struct.unpack_from('<II',d,0); _start=_hs; sec=None
    for _i in range(_n):
        _sz,_end=struct.unpack_from('<II',d,8+_i*8)
        if _i==int(sys.argv[2]): sec=d[_start:_start+_sz]
        _start=_end if _end else _start
    assert sec is not None and sec[:4]==b'NDPP', 'slot is not NDPP'
    verts,tris,nrms,uvs,wgts,desc=decode_mesh(sec)
    print('verts',len(verts),'tris',len(tris))
    mins,maxs=write_glb(sys.argv[3],verts,tris,nrms,'ndpp_section')
    print('glb bbox min',[round(x,2) for x in mins],'max',[round(x,2) for x in maxs])
    print('desc bbox x[%.2f,%.2f] y[%.2f,%.2f] z[%.2f,%.2f]'%(desc[3],desc[4],desc[5],desc[6],desc[7],desc[8]))
