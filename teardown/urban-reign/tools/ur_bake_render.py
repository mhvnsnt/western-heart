#!/usr/bin/env python3
"""Front render of a textured skinned GLB with skinning BAKED (glTF semantics)."""
import json, struct, sys
import numpy as np
sys.path.insert(0, __file__.rsplit('/',1)[0])
import ur_tex_extract as tx
sys.argv = sys.argv
path, outp = sys.argv[1], sys.argv[2]
S = int(sys.argv[3]) if len(sys.argv) > 3 else 640
az = float(sys.argv[4]) if len(sys.argv) > 4 else 0.0  # azimuth deg, 0=front(+Z)
d = open(path, 'rb').read()
ln = struct.unpack('<I', d[12:16])[0]
j = json.loads(d[20:20+ln])
bofs = 20 + ln; bln = struct.unpack('<I', d[bofs:bofs+4])[0]
bin_ = d[bofs+8:bofs+8+bln]
def acc(ai):
    a = j['accessors'][ai]; bv = j['bufferViews'][a['bufferView']]
    off = bv.get('byteOffset', 0) + a.get('byteOffset', 0)
    n = a['count']; t = {'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}[a['type']]
    dt = {5126: np.float32, 5123: np.uint16, 5125: np.uint32, 5121: np.uint8, 5122: np.int16}[a['componentType']]
    arr = np.frombuffer(bin_, dtype=dt, count=n*t, offset=off)
    return arr.reshape(n, t) if t > 1 else arr
def node_mat(n):
    if 'matrix' in n: return np.array(n['matrix'], dtype=np.float64).reshape(4,4).T
    M = np.eye(4)
    if 'translation' in n: M[:3,3] = n['translation']
    if 'rotation' in n:
        x,y,z,w = n['rotation']; R = np.array([
          [1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])
        M[:3,:3] = R @ M[:3,:3]
    if 'scale' in n: M[:3,:3] = M[:3,:3] @ np.diag(n['scale'])
    return M
nodes = j['nodes']; parent = {}
for i,n in enumerate(nodes):
    for c in n.get('children',[]): parent[c] = i
from functools import lru_cache
import sys as _s; _s.setrecursionlimit(10000)
def glob(i):
    M = node_mat(nodes[i])
    return glob(parent[i]) @ M if i in parent else M
skin = j['skins'][0]
ibm = acc(skin['inverseBindMatrices']).reshape(-1,4,4).transpose(0,2,1)
jm = np.stack([glob(jn) @ ibm[k] for k, jn in enumerate(skin['joints'])])
prims = j['meshes'][0]['primitives']
p0 = prims[0]
pos = acc(p0['attributes']['POSITION']).astype(np.float64)
jnts = acc(p0['attributes']['JOINTS_0']).astype(int)
wts = acc(p0['attributes']['WEIGHTS_0']).astype(np.float64)
hom = np.concatenate([pos, np.ones((len(pos),1))], axis=1)
sk = np.zeros((len(pos),4))
for k in range(4):
    sk += wts[:,k:k+1] * np.einsum('nij,nj->ni', jm[jnts[:,k]], hom)
pos = sk[:,:3]
uv = acc(p0['attributes']['TEXCOORD_0']).astype(np.float64)
# rotate azimuth around Y (up = Y? check extents: use Y up)
th = np.radians(az); R = np.array([[np.cos(th),0,np.sin(th)],[0,1,0],[-np.sin(th),0,np.cos(th)]])
pos = pos @ R.T
def img_arr(src):
    bv = j['bufferViews'][j['images'][src]['bufferView']]
    off = bv.get('byteOffset', 0)
    data = bin_[off:off+bv['byteLength']]
    import zlib
    assert data[:8] == b'\x89PNG\r\n\x1a\n'
    p = 8; idat = b''; w=h=None; ctype=None; bitd=None
    while p < len(data):
        L = struct.unpack('>I', data[p:p+4])[0]; typ = data[p+4:p+8]; chunk = data[p+8:p+8+L]
        if typ == b'IHDR': w, h, bitd, ctype = struct.unpack('>IIBB', chunk[:10])
        elif typ == b'IDAT': idat += chunk
        p += 12 + L
    raw = zlib.decompress(idat)
    ch = {6:4, 2:3, 0:1, 3:1}[ctype]
    stride = w*ch*(bitd//8)
    img = np.zeros((h, w, ch), dtype=np.uint8)
    prev = np.zeros(stride, dtype=np.uint8); q = 0
    for y in range(h):
        f = raw[q]; q += 1
        line = np.frombuffer(raw[q:q+stride], dtype=np.uint8).copy(); q += stride
        if f == 1:
            for i in range(ch, stride): line[i] = (int(line[i]) + int(line[i-ch])) & 0xFF
        elif f == 2: line = ((line.astype(int) + prev.astype(int)) & 0xFF).astype(np.uint8)
        elif f == 3:
            for i in range(stride):
                a = int(line[i-ch]) if i >= ch else 0
                line[i] = (int(line[i]) + ((a + int(prev[i])) >> 1)) & 0xFF
        elif f == 4:
            for i in range(stride):
                a = int(line[i-ch]) if i >= ch else 0
                b = int(prev[i]); c = int(prev[i-ch]) if i >= ch else 0
                pp = a + b - c; pa, pb, pc = abs(pp-a), abs(pp-b), abs(pp-c)
                pr = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                line[i] = (int(line[i]) + pr) & 0xFF
        img[y] = line.reshape(w, ch); prev = line
    if ch == 4: return img.astype(np.float64)
    o = np.zeros((h, w, 4)); o[:,:,:3] = img[:,:,:3] if ch==3 else img[:,:,:1]; o[:,:,3] = 255
    return o
ctr = (pos.max(0) + pos.min(0)) / 2
ext = (pos.max(0) - pos.min(0)).max()
P = (pos - ctr) / ext
img = np.full((S, S, 4), 30, dtype=np.uint8); img[:,:,3] = 255
zbuf = np.full((S, S), -1e9)
light = np.array([0.3, 0.5, 0.8]); light /= np.linalg.norm(light)
texcache = {}
def get_tex(mat_i):
    if mat_i is None: return None
    ti = j['materials'][mat_i]['pbrMetallicRoughness']['baseColorTexture']['index']
    src = j['textures'][ti]['source']
    if src not in texcache: texcache[src] = img_arr(src)
    return texcache[src]
for pr in prims:
    idx = acc(pr['indices']).reshape(-1, 3).astype(int)
    tex = get_tex(pr.get('material'))
    for (a, b, c) in idx:
        pts = P[[a, b, c]]
        xs = (pts[:,0] + 0.5) * (S-1); ys = (0.5 - pts[:,1]) * (S-1); zs = pts[:,2]
        minx, maxx = max(0, int(xs.min())), min(S-1, int(xs.max()))
        miny, maxy = max(0, int(ys.min())), min(S-1, int(ys.max()))
        if maxx <= minx or maxy <= miny: continue
        dd = (xs[1]-xs[0])*(ys[2]-ys[0]) - (ys[1]-ys[0])*(xs[2]-xs[0])
        if dd == 0: continue
        fn = np.cross(pos[b]-pos[a], pos[c]-pos[a]); nl = np.linalg.norm(fn)
        shade = 0.72 + 0.28*abs(float(fn @ light)/nl) if nl else 0.5
        for yy in range(miny, maxy+1):
            for xx in range(minx, maxx+1):
                w0 = ((xs[1]-xx)*(ys[2]-yy) - (ys[1]-yy)*(xs[2]-xx)) / dd
                w1 = ((xs[2]-xx)*(ys[0]-yy) - (ys[2]-yy)*(xs[0]-xx)) / dd
                w2 = 1 - w0 - w1
                if w0 < 0 or w1 < 0 or w2 < 0: continue
                z = w0*zs[0] + w1*zs[1] + w2*zs[2]
                if z <= zbuf[yy, xx]: continue
                zbuf[yy, xx] = z
                if tex is not None:
                    u = w0*uv[a,0] + w1*uv[b,0] + w2*uv[c,0]
                    v = w0*uv[a,1] + w1*uv[b,1] + w2*uv[c,1]
                    ih, iw = tex.shape[:2]
                    col = tex[int(np.mod(v,1.0)*ih) % ih, int(np.mod(u,1.0)*iw) % iw, :3]
                else: col = np.array([140., 140., 150.])
                img[yy, xx, :3] = np.clip(col*shade, 0, 255)
tx.write_png(outp, S, S, img.tobytes())
print('wrote', outp, 'extents', (pos.max(0)-pos.min(0)).round(2))
