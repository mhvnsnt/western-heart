"""Per-station root measurement for the lash-fix build.
Root = tt=0 ring centre of each station's clump rows (base = margin curve
point + margin normal x 0.55 mm, +/- row lateral offsets along tangent).
Reports distance to (a) the lid-margin curve polyline, (b) the skin surface.
Also: strand clearance above the rim (min up-coordinate of any lash vertex
relative to its station root) and the BEFORE comparison numbers."""
import sys, json
sys.path.insert(0, 'scripts')
import numpy as np
from lash_glb_lib import load_glb, skinned_positions
from scipy.spatial import cKDTree

SPEC_OFF = 0.00055
geo = np.load('work/lash_megami_geometry.npz', allow_pickle=True)
meta = json.loads(str(geo['meta']))
g, b, _ = load_glb('work/megami-angel-gnmface-v2.glb')
matnames = [m.get('name') for m in g['materials']]
mesh10 = skinned_positions(g, b, 10, {'AngelFace': 1.0, 'AngelBody': 1.0})
skin_prims = [p for p in mesh10 if matnames[p['mat']] in ('Face-2', 'EyeSocket-2')]
skin_V = np.vstack([p['pos'] for p in skin_prims])
skin_F = []; off = 0
for p in skin_prims:
    skin_F.append(p['idx'].reshape(-1, 3) + off); off += len(p['pos'])
skin_F = np.vstack(skin_F); skin_tree = cKDTree(skin_V)

def surf_dist(pt):
    _, cand = skin_tree.query(pt, k=24)
    mask = np.isin(skin_F, cand); sel = skin_F[mask.any(axis=1)]
    A = skin_V[sel[:,0]]; Bv = skin_V[sel[:,1]]; C = skin_V[sel[:,2]]
    AP = pt - A; AB = Bv - A; AC = C - A
    d1 = (AB*AP).sum(1); d2 = (AC*AP).sum(1)
    D = (AB*AB).sum(1)*(AC*AC).sum(1) - (AB*AC).sum(1)**2
    D = np.where(np.abs(D) < 1e-14, 1e-14, D)
    s = np.clip(((AC*AC).sum(1)*d1 - (AB*AC).sum(1)*d2)/D, 0, 1)
    t = np.clip(((AB*AB).sum(1)*d2 - (AB*AC).sum(1)*d1)/D, 0, 1)
    s = np.minimum(s, 1-t)
    q = A + s[:,None]*AB + t[:,None]*AC
    return float(np.linalg.norm(q-pt, axis=1).min())

def catmull(Pt, n_per=24):
    Pt = np.asarray(Pt, float)
    ext = np.vstack([Pt[0]+(Pt[0]-Pt[1]), Pt, Pt[-1]+(Pt[-1]-Pt[-2])])
    out = []
    for i in range(len(Pt)-1):
        p0,p1,p2,p3 = ext[i],ext[i+1],ext[i+2],ext[i+3]
        for t in np.linspace(0,1,n_per,endpoint=False):
            out.append(0.5*((2*p1)+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t**2+(-p0+3*p1-3*p2+p3)*t**3))
    out.append(Pt[-1]); return np.array(out)

def poly_dist(pt, poly):
    A = poly[:-1]; AB = poly[1:] - A
    t = np.clip(((pt-A)*AB).sum(1) / ((AB*AB).sum(1)+1e-14), 0, 1)
    q = A + t[:,None]*AB
    return float(np.linalg.norm(q-pt, axis=1).min())

out = {}
for side in ('posx','negx'):
    top = geo[f'{side}_top']; top_n = geo[f'{side}_top_n']
    tc = catmull(top, 24); tn = catmull(top_n, 24); tn /= (np.linalg.norm(tn,axis=1,keepdims=True)+1e-12)
    seg = np.linalg.norm(np.diff(tc,axis=0),axis=1); cum = np.r_[0,np.cumsum(seg)]; total = cum[-1]
    eye_w = float(meta[side]['eye_w']); pitch = eye_w/26.0
    dm, ds = [], []
    for i in range(27):
        u = i/26.0; j = int(np.argmin(np.abs(cum/total-u)))
        tang = tc[min(j+1,len(tc)-1)] - tc[max(j-1,0)]; tang /= (np.linalg.norm(tang)+1e-12)
        for r in (0, 3, 6):
            root = tc[j] + tn[j]*SPEC_OFF + tang*((r-3)*pitch/7)
            dm.append(poly_dist(root, tc)); ds.append(surf_dist(root))
    out[side] = dict(root_to_margin_mean=float(np.mean(dm)), root_to_margin_max=float(np.max(dm)),
                     root_to_surface_mean=float(np.mean(ds)), root_to_surface_max=float(np.max(ds)))
    print(side, {k: round(v*1000,3) for k,v in out[side].items()}, '(mm)')

# strand clearance: every built lash vertex's up-coordinate vs its eye rim plane
lg = np.load('work/lashes_megami_geom.npz', allow_pickle=True)
V = lg['V']
print('lash verts y range', round(float(V[:,1].min()),4), round(float(V[:,1].max()),4),
      'x span', round(float(V[:,0].min()),4), round(float(V[:,0].max()),4))
json.dump(out, open('work/lash_root_measure.json','w'), indent=1)
print('saved work/lash_root_measure.json')
