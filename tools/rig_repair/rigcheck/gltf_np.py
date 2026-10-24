"""Minimal numpy glTF 2.0 (GLB) reader + glTF-semantics animation sampler + linear blend skinning.
Matches three.js/glTF rules: animation channels REPLACE node local T/R/S (absolute, not deltas);
skinned vertex = sum_i w_i * (jointWorld_i * IBM_i) * v. Input must be meshopt-decoded (scripts/decode.mjs)."""
import json, struct, numpy as np

CT = {5120: np.int8, 5121: np.uint8, 5122: np.int16, 5123: np.uint16, 5125: np.uint32, 5126: np.float32}
NC = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4, 'MAT4': 16}

def qmat(q):
    x, y, z, w = q
    return np.array([[1-2*(y*y+z*z), 2*(x*y-z*w), 2*(x*z+y*w)],
                     [2*(x*y+z*w), 1-2*(x*x+z*z), 2*(y*z-x*w)],
                     [2*(x*z-y*w), 2*(y*z+x*w), 1-2*(x*x+y*y)]])
def mat_to_q(m):
    m = np.asarray(m, float)[:3, :3]; t = np.trace(m)
    if t > 0:
        s = np.sqrt(t+1.0)*2; w = 0.25*s; x = (m[2,1]-m[1,2])/s; y = (m[0,2]-m[2,0])/s; z = (m[1,0]-m[0,1])/s
    elif m[0,0] > m[1,1] and m[0,0] > m[2,2]:
        s = np.sqrt(1.0+m[0,0]-m[1,1]-m[2,2])*2; w = (m[2,1]-m[1,2])/s; x = 0.25*s; y = (m[0,1]+m[1,0])/s; z = (m[0,2]+m[2,0])/s
    elif m[1,1] > m[2,2]:
        s = np.sqrt(1.0+m[1,1]-m[0,0]-m[2,2])*2; w = (m[0,2]-m[2,0])/s; x = (m[0,1]+m[1,0])/s; y = 0.25*s; z = (m[1,2]+m[2,1])/s
    else:
        s = np.sqrt(1.0+m[2,2]-m[0,0]-m[1,1])*2; w = (m[1,0]-m[0,1])/s; x = (m[0,2]+m[2,0])/s; y = (m[1,2]+m[2,1])/s; z = 0.25*s
    q = np.array([x, y, z, w]); return q/np.linalg.norm(q)
def trs(t, r, s):
    m = np.eye(4); m[:3, :3] = qmat(r) * np.asarray(s)[None, :]; m[:3, 3] = t; return m
def slerp(a, b, u):
    a = np.asarray(a, float); b = np.asarray(b, float); d = np.dot(a, b)
    if d < 0: b = -b; d = -d
    if d > 0.9995: q = a + u*(b-a); return q/np.linalg.norm(q)
    th = np.arccos(d); return (np.sin((1-u)*th)*a + np.sin(u*th)*b)/np.sin(th)

class GLB:
    def __init__(self, path):
        data = open(path, 'rb').read()
        assert data[:4] == b'glTF', 'not a GLB: ' + path
        jl = struct.unpack('<I', data[12:16])[0]
        self.j = json.loads(data[20:20+jl])
        off = 20 + jl
        self.bin = data[off+8:off+8+struct.unpack('<I', data[off:off+4])[0]] if off < len(data) else b''
        self.nodes = self.j.get('nodes', [])
        self.parent = [-1]*len(self.nodes)
        for i, n in enumerate(self.nodes):
            for c in n.get('children', []): self.parent[c] = i
        self.name = [n.get('name', f'node{i}') for i, n in enumerate(self.nodes)]
        self.byname = {n: i for i, n in enumerate(self.name)}
        self.rest = [self._rest(n) for n in self.nodes]
    def acc(self, i):
        a = self.j['accessors'][i]; dt = CT[a['componentType']]; nc = NC[a['type']]; cnt = a['count']
        if 'bufferView' not in a: return np.zeros((cnt, nc), np.float32)
        bv = self.j['bufferViews'][a['bufferView']]; start = bv.get('byteOffset', 0) + a.get('byteOffset', 0)
        stride = bv.get('byteStride', 0); isz = np.dtype(dt).itemsize
        if stride and stride != nc*isz:
            raw = np.frombuffer(self.bin, np.uint8, count=stride*(cnt-1)+nc*isz, offset=start)
            out = np.stack([np.frombuffer(raw[k*stride:k*stride+nc*isz].tobytes(), dt) for k in range(cnt)])
        else:
            out = np.frombuffer(self.bin, dt, count=cnt*nc, offset=start).reshape(cnt, nc)
        out = out.astype(np.float64) if dt == np.float32 else out
        if a.get('normalized'):
            mx = {np.int8: 127, np.uint8: 255, np.int16: 32767, np.uint16: 65535}[dt]; out = np.maximum(out.astype(np.float64)/mx, -1)
        return out
    def _rest(self, n):
        if 'matrix' in n:
            m = np.array(n['matrix'], float).reshape(4, 4).T
            t = m[:3, 3].copy(); s = np.linalg.norm(m[:3, :3], axis=0); r = mat_to_q(m[:3, :3]/s); return [t, r, s]
        return [np.array(n.get('translation', [0, 0, 0]), float), np.array(n.get('rotation', [0, 0, 0, 1]), float), np.array(n.get('scale', [1, 1, 1]), float)]
    def world(self, local):
        W = [None]*len(self.nodes)
        def w(i):
            if W[i] is None:
                L = trs(*local[i]); W[i] = L if self.parent[i] < 0 else w(self.parent[i]) @ L
            return W[i]
        for i in range(len(self.nodes)): w(i)
        return W
    # ---- animation ----
    def anim_names(self): return [a.get('name', f'anim{i}') for i, a in enumerate(self.j.get('animations', []))]
    def anim(self, name_or_idx):
        A = self.j['animations']; a = A[name_or_idx] if isinstance(name_or_idx, int) else next(x for x in A if x.get('name') == name_or_idx)
        tracks = []
        for ch in a['channels']:
            s = a['samplers'][ch['sampler']]; tgt = ch['target']
            if 'node' not in tgt or tgt['path'] not in ('translation', 'rotation', 'scale'): continue
            times = self.acc(s['input'])[:, 0]; vals = self.acc(s['output'])
            interp = s.get('interpolation', 'LINEAR')
            if interp == 'CUBICSPLINE': vals = vals.reshape(len(times), 3, -1)[:, 1, :]
            tracks.append(dict(node=self.name[tgt['node']], path=tgt['path'], t=times, v=vals, step=interp == 'STEP'))
        dur = max((tr['t'][-1] for tr in tracks), default=0)
        return dict(name=a.get('name'), tracks=tracks, duration=float(dur))

def sample_track(tr, t):
    T = tr['t']; V = tr['v']
    if t <= T[0] or len(T) == 1: return V[0]
    if t >= T[-1]: return V[-1]
    k = np.searchsorted(T, t) - 1; u = (t - T[k]) / max(T[k+1] - T[k], 1e-9)
    if tr['step']: return V[k]
    if tr['path'] == 'rotation': return slerp(V[k], V[k+1], u)
    return V[k]*(1-u) + V[k+1]*u

class SkinnedModel:
    """Character GLB: rest nodes + skinned primitives (positions in bind space)."""
    def __init__(self, path):
        self.g = g = GLB(path)
        self.skins = g.j.get('skins', [])
        self.prims = []  # dict(pos, J, W, idx, skin, node)
        for ni, n in enumerate(g.nodes):
            if 'mesh' not in n: continue
            for p in g.j['meshes'][n['mesh']]['primitives']:
                at = p['attributes']; pos = g.acc(at['POSITION'])
                d = dict(node=ni, pos=pos, idx=g.acc(p['indices']).astype(np.int64).reshape(-1, 3) if 'indices' in p else np.arange(len(pos)).reshape(-1, 3),
                         skin=n.get('skin'), mat=p.get('material'))
                if 'JOINTS_0' in at and n.get('skin') is not None:
                    d['J'] = g.acc(at['JOINTS_0']).astype(np.int64); d['W'] = g.acc(at['WEIGHTS_0']).astype(np.float64)
                    if 'JOINTS_1' in at:
                        d['J'] = np.concatenate([d['J'], g.acc(at['JOINTS_1']).astype(np.int64)], 1); d['W'] = np.concatenate([d['W'], g.acc(at['WEIGHTS_1'])], 1)
                if 'TEXCOORD_0' in at: d['uv'] = g.acc(at['TEXCOORD_0'])
                self.prims.append(d)
        self.ibm = [g.acc(s['inverseBindMatrices']).reshape(-1, 4, 4).transpose(0, 2, 1) if 'inverseBindMatrices' in s else np.tile(np.eye(4), (len(s['joints']), 1, 1)) for s in self.skins]
    def local_at(self, clip=None, t=0.0, name_map=None, hips_scale=None, hips_name=None, tracks_filter=None):
        """Node locals with a clip applied by node NAME (glTF/three semantics). name_map: clipBone->modelBone."""
        g = self.g; local = [[x.copy() for x in r] for r in g.rest]
        if clip:
            for tr in clip['tracks']:
                nm = name_map.get(tr['node'], None) if name_map is not None else tr['node']
                if nm is None or nm not in g.byname: continue
                if tracks_filter and not tracks_filter(tr, nm): continue
                v = np.array(sample_track(tr, t), float)
                i = g.byname[nm]
                if tr['path'] == 'translation':
                    if hips_scale is not None and nm == hips_name: v = v * hips_scale
                    local[i][0] = v
                elif tr['path'] == 'rotation': local[i][1] = v/np.linalg.norm(v)
                else: local[i][2] = v
        return local
    def skin_verts(self, local):
        W = self.g.world(local); out = []
        for d in self.prims:
            if 'J' in d:
                s = self.skins[d['skin']]; M = np.stack([W[j] for j in s['joints']]) @ self.ibm[d['skin']]
                Wt = d['W'] / np.maximum(d['W'].sum(1, keepdims=True), 1e-9)
                Mv = np.einsum('vk,vkij->vij', Wt, M[d['J']])
                p = np.einsum('vij,vj->vi', Mv[:, :3, :3], d['pos']) + Mv[:, :3, 3]
            else:
                M = W[d['node']]; p = d['pos'] @ M[:3, :3].T + M[:3, 3]
            out.append(p)
        return out, W
