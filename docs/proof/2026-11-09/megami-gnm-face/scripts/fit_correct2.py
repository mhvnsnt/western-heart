"""Stage-2 multi-view projection correction.

Observations: the gate's own per-landmark deltas from BOTH matched
cameras (front + 3/4) of the current candidate -- the 2D moves the
matched-camera measurement asks for, converted to camera-plane 3D
moves exactly as the repos' gate defines them (delta x subject face
width in metres, along camera right/up). Solved for the smoothest
3D field explaining both views at once:

  min sum_cams sum_i w_i |(I - f f^T)(B dF_i - m_i)|^2
      + alpha |L dF|^2 + beta |dF|^2

Rigid landmarks full weight; expression-bearing landmarks 0.35 (their
placement still carries identity; their expression content is damped).
dF lives on face+lips prims (block-diagonal Laplacians); other prims
inherit by nearest-vertex sampling with a distance fade, as before.
Usage: fit_correct2.py <base_key.npz> <front_deltas.json> <q34_deltas.json> <alpha> <beta> <out.npz>
"""
import json, sys
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla
from scipy.spatial import cKDTree
sys.path.insert(0, '/home/hatch/workspace/_gnmface-20261109/scripts')
from glb_lib import load_glb, acc_array

BASE_KEY, FD, QD, ALPHA, BETA, OUT = sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4]), float(sys.argv[5]), sys.argv[6]
W = '/home/hatch/workspace/_gnmface-20261109/work'
V2 = '/home/hatch/workspace/_pilot2-v2-20261108'

g, buf = load_glb(f'{W}/megami-angel-pilot2-v3.glb')
names10 = g['meshes'][10]['extras']['targetNames']

def prim_M0(mi, pi):
    pr = g['meshes'][mi]['primitives'][pi]
    B = acc_array(g, buf, pr['attributes']['POSITION']).astype(np.float64)
    DB = acc_array(g, buf, pr['targets'][names10.index('AngelBody')]['POSITION']).astype(np.float64)
    T = acc_array(g, buf, pr['indices']).reshape(-1, 3).astype(int)
    return B + DB, T

PRIMS = [(10, 1), (10, 2)]
M0s, Ts, offsets = {}, {}, {}
off = 0
for k in PRIMS:
    M0s[k], Ts[k] = prim_M0(*k)
    offsets[k] = off
    off += len(M0s[k])
NV = off

def raycast(M0, T, origin, dirn):
    A = M0[T[:, 0]]; B = M0[T[:, 1]]; C = M0[T[:, 2]]
    e1 = B - A; e2 = C - A
    pvec = np.cross(dirn, e2)
    det = np.einsum('ij,ij->i', e1, pvec)
    ok = np.abs(det) > 1e-12
    inv = np.zeros(len(T)); inv[ok] = 1.0 / det[ok]
    tvec = origin - A
    u = np.einsum('ij,ij->i', tvec, pvec) * inv
    qvec = np.cross(tvec, e1)
    v = np.einsum('j,ij->i', dirn, qvec) * inv
    t = np.einsum('ij,ij->i', e2, qvec) * inv
    valid = ok & (u >= -1e-9) & (v >= -1e-9) & (u + v <= 1 + 1e-9) & (t > 0)
    if not valid.any():
        return None
    idx = np.where(valid)[0]
    j = idx[np.argmin(t[idx])]
    A_, B_, C_ = A[j], B[j], C[j]
    n = np.cross(B_ - A_, C_ - A_)
    if n @ dirn >= 0:
        return None
    return t[j], T[j], (1 - u[j] - v[j], u[j], v[j])

CAMS = {
    'front': {'pos': np.array([0.0, 1.4980212458513713, 0.6639610483488484]),
              'tgt': np.array([0.0, 1.5526, 0.014]), 'fov': 55.0},
    'q34': {'pos': np.array([0.4515403599816252, 1.5526, 0.3667819930413128]),
            'tgt': np.array([0.0, 1.5526, 0.014]), 'fov': 55.0},
}
for c in CAMS.values():
    fwd = (c['tgt'] - c['pos']); fwd /= np.linalg.norm(fwd)
    right = np.cross(fwd, [0, 1, 0]); right /= np.linalg.norm(right)
    up = np.cross(right, fwd)
    c.update({'fwd': fwd, 'right': right, 'up': up, 'tanf': np.tan(np.radians(c['fov']) / 2), 'aspect': 540 / 960})

def ray_for(cam, u, v):
    ndc_x = (2 * u - 1) * cam['tanf'] * cam['aspect']
    ndc_y = (1 - 2 * v) * cam['tanf']
    d = cam['fwd'] + cam['right'] * ndc_x + cam['up'] * ndc_y
    return d / np.linalg.norm(d)

fd = json.load(open(FD)); qd = json.load(open(QD))
warp_lms = sorted(set(int(k) for k in fd['deltas']) | set(int(k) for k in qd['deltas']))
corr = np.load(f'{W}/correspondence.npz')
LMIDX, RIGID = corr['landmarks'], corr['rigid'].astype(bool)
rigid_set = set(int(LMIDX[r]) for r in np.where(RIGID)[0])

# physical face width (234<->454) on the composed mesh, from front anchors
anch_file = json.load(open(f'{W}/anchors_mine.json'))
# (anchors_mine covers rigid only; 234/454 are rigid oval points)
p234 = np.array(anch_file['234']['point']); p454 = np.array(anch_file['454']['point'])
FW = float(np.linalg.norm(p234 - p454))
print('physical face width m:', round(FW, 4))

# ---- anchors for warp landmarks: front cam first, else q34 cam ----
anchors = {}   # mp -> (prim_key, tri_global_ids, bary)
for mp_i in warp_lms:
    got = None
    for cam_name, dj in [('front', fd), ('q34', qd)]:
        cam = CAMS[cam_name]
        u, v = dj['landmarks'][mp_i]
        d = ray_for(cam, u, v)
        for k in PRIMS:
            hit = raycast(M0s[k], Ts[k], cam['pos'], d)
            if hit:
                _, tri, bary = hit
                got = (k, [int(x) + offsets[k] for x in tri], bary)
                break
        if got:
            break
    if got:
        anchors[mp_i] = got
print(f'stage-2 anchors: {len(anchors)} / {len(warp_lms)} warp landmarks')

# ---- build the system over dF ( NV x 3 ) ----
A_list = sorted(anchors.keys())
na = len(A_list)
Bmat = sp.lil_matrix((na, NV))
for i, mp_i in enumerate(A_list):
    _, tri_g, bary = anchors[mp_i]
    for wgt, gv in zip(bary, tri_g):
        Bmat[i, gv] = wgt
Bmat = Bmat.tocsr()

def laplacian(T, n):
    rows, cols = [], []
    for a, b, cc in T:
        for uu, vv in [(a, b), (b, a), (b, cc), (cc, b), (a, cc), (cc, a)]:
            rows.append(uu); cols.append(vv)
    A = sp.coo_matrix((np.ones(len(rows)), (rows, cols)), shape=(n, n)).tocsr()
    A.data[:] = 1
    return sp.diags(np.asarray(A.sum(1)).ravel()) - A

L = sp.block_diag([laplacian(Ts[k], len(M0s[k])) for k in PRIMS]).tocsr()
LtL = (L.T @ L).tocsr()

# observations per camera
I3 = np.eye(3)
Adata = sp.csr_matrix((3 * NV, 3 * NV))
rhs = np.zeros(3 * NV)
for cam_name, dj in [('front', fd), ('q34', qd)]:
    cam = CAMS[cam_name]
    Pc = I3 - np.outer(cam['fwd'], cam['fwd'])
    w = np.zeros(na)
    m = np.zeros((na, 3))
    for i, mp_i in enumerate(A_list):
        dk = dj['deltas'].get(str(mp_i))
        if dk is None:
            continue
        dx, dy = dk
        m[i] = (cam['right'] * dx + cam['up'] * (-dy)) * FW
        w[i] = 1.0 if mp_i in rigid_set else 0.35
    Wm = sp.diags(w)
    BtWB = (Bmat.T @ Wm @ Bmat).tocsr()
    Adata += sp.kron(BtWB, Pc, format='csr')
    r = (Bmat.T @ (w[:, None] * m))          # (NV, 3)
    rhs += (Pc @ r.T).T.reshape(-1) if False else np.einsum('ij,vj->vi', Pc, r).reshape(-1)
print('system built; solving...')
M = Adata + ALPHA * sp.kron(LtL, I3, format='csr') + BETA * sp.eye(3 * NV, format='csr')
sol = spla.spsolve(M.tocsc(), rhs)
dF = sol.reshape(NV, 3)
print(f'|dF| mean {np.linalg.norm(dF, axis=1).mean() * 1000:.2f} mm max {np.linalg.norm(dF, axis=1).max() * 1000:.2f} mm')

# ---- assemble ----
F0 = np.load(BASE_KEY)
out = {}
face_tree = cKDTree(M0s[(10, 1)])
for tag in F0.files:
    base = F0[tag].astype(np.float64)
    mi, pi = map(int, tag.split(':'))
    if (mi, pi) in PRIMS:
        o = offsets[(mi, pi)]
        out[tag] = (base + dF[o:o + len(base)]).astype(np.float32)
        continue
    pr = g['meshes'][mi]['primitives'][pi]
    B = acc_array(g, buf, pr['attributes']['POSITION']).astype(np.float64)
    nm = g['meshes'][mi]['extras']['targetNames']
    DB = acc_array(g, buf, pr['targets'][nm.index('AngelBody')]['POSITION']).astype(np.float64)
    M0p = B + DB
    dist, nn = face_tree.query(M0p)
    u = np.clip(1 - (dist - 0.004) / 0.010, 0, 1)
    fade = u * u * (3 - 2 * u)
    corr_face = dF[offsets[(10, 1)]:offsets[(10, 1)] + len(M0s[(10, 1)])]
    out[tag] = (base + corr_face[nn] * fade[:, None]).astype(np.float32)
    print(f'{tag}: inherited correction, max total {np.abs(out[tag]).max() * 1000:.2f} mm')
np.savez(OUT, **out)
print('wrote', OUT)
