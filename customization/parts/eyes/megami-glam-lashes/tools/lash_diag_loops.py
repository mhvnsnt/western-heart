"""V7 diagnostic 2: boundary loops of the COMBINED Face-2 + EyeSocket-2
surface (mesh 10, AngelFace=1/AngelBody=1 skinned). The Face-prim-only
loop gave aperture 16.2mm on posx vs a ~11mm visible opening. A combined
-boundary loop with a smaller aperture near the eye = the visible
opening rim (the true lash line). Also tries EyeSocket-2 alone."""
import sys
sys.path.insert(0, 'scripts')
import numpy as np, json
from lash_glb_lib import load_glb, skinned_positions
from collections import defaultdict

g, b, _ = load_glb('work/megami-angel-gnmface-v2.glb')
matnames = [m.get('name') for m in g['materials']]
mesh10 = skinned_positions(g, b, 10, {'AngelFace': 1.0, 'AngelBody': 1.0})
geo = np.load('work/lash_megami_geometry.npz', allow_pickle=True)


def boundary_loops(prims):
    # weld by rounded position (prims share verts by position in bind state)
    V = np.vstack([p['pos'] for p in prims])
    key = {}
    remap = []
    for p in prims:
        r = []
        for v in p['pos']:
            k = tuple(np.round(v, 6))
            if k not in key:
                key[k] = len(key)
            r.append(key[k])
        remap.append(np.array(r))
    edge_count = defaultdict(int)
    edge_verts = []
    for p, r in zip(prims, remap):
        F = p['idx'].reshape(-1, 3)
        for tri in F:
            w = r[tri]
            for a, bb in ((0, 1), (1, 2), (2, 0)):
                e = (int(min(w[a], w[bb])), int(max(w[a], w[bb])))
                edge_count[e] += 1
                edge_verts.append(e)
    bnd = [e for e, c in edge_count.items() if c == 1]
    # chain into loops
    adj = defaultdict(list)
    for a, bb in bnd:
        adj[a].append(bb); adj[bb].append(a)
    inv = {v: k for k, v in key.items()}
    P = np.array([inv[i] for i in range(len(key))])
    seen = set(); loops = []
    for s in list(adj):
        if s in seen:
            continue
        loop = [s]; seen.add(s); cur = s; prev = -1
        while True:
            nxt = [x for x in adj[cur] if x != prev]
            if not nxt:
                break
            nx = nxt[0]
            if nx == s:
                break
            if nx in seen:
                break
            loop.append(nx); seen.add(nx); prev, cur = cur, nx
        if len(loop) >= 8:
            loops.append(P[loop])
    return loops


for label, mats in (('Face-2 only', ('Face-2',)),
                    ('EyeSocket-2 only', ('EyeSocket-2',)),
                    ('Face+EyeSocket', ('Face-2', 'EyeSocket-2'))):
    prims = [p for p in mesh10 if matnames[p['mat']] in mats]
    loops = boundary_loops(prims)
    print(f'== {label}: {len(loops)} boundary loops >= 8 pts')
    for L in loops:
        c = L.mean(0)
        for s in ('posx', 'negx'):
            iris = geo[f'{s}_iris_c']
            if abs(c[0] - iris[0]) < 0.008 and abs(c[1] - iris[1]) < 0.008:
                top = L[L[:, 1].argsort()[len(L)//2:]]
                print(f'   eye loop {s}: n={len(L)} x-span {L[:,0].ptp()*1000:.1f}mm '
                      f'y-span {L[:,1].ptp()*1000:.1f}mm z {L[:,2].min():.4f}..{L[:,2].max():.4f} '
                      f'centre=({c[0]:+.4f},{c[1]:.4f},{c[2]:.4f})')
