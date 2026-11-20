"""V7: extract the VISIBLE lash line — the skin curve at the edge of the
visible eyeball, per eye. Method: in the eye-local frame (lat/up/fwd),
cast a dense grid of parallel rays (dir = -fwd) at the head; classify
each ray ball-first vs skin-first; per lateral column the upper (lower)
boundary of the ball-visible run gives the margin point on the SKIN hit
just outside the boundary. Roots seated there sit on the visible lid
edge, not on the hidden Face/EyeSocket seam (the old loop).
Saves work/lash_visible_margin.npz: positions, normals, barycentric
JOINTS/WEIGHTS per margin point (top + bot, both eyes), dense in x."""
import sys, json
sys.path.insert(0, 'scripts')
import numpy as np
from lash_glb_lib import load_glb, accessor, skinned_positions

g, b, _ = load_glb('work/megami-angel-gnmface-v2.glb')
matnames = [m.get('name') for m in g['materials']]
mesh10 = skinned_positions(g, b, 10, {'AngelFace': 1.0, 'AngelBody': 1.0})
geo = np.load('work/lash_megami_geometry.npz', allow_pickle=True)
meta = json.loads(str(geo['meta']))

prim_jw = {}
for pi, p in enumerate(g['meshes'][10]['primitives']):
    at = p['attributes']
    if 'JOINTS_0' in at:
        prim_jw[pi] = (accessor(g, b, at['JOINTS_0']).astype(int),
                       accessor(g, b, at['WEIGHTS_0']).astype(np.float64))

SKIN_MATS = ('Face-2', 'EyeSocket-2')
BALL_MATS = ('Sclera-2', 'Cornea-2', 'Irises-2', 'Pupils-2')


def collect(mats, with_jw=False):
    V, F, J, W = [], [], [], []
    off = 0
    for pi, p in enumerate(mesh10):
        if matnames[p['mat']] not in mats:
            continue
        V.append(p['pos'])
        F.append(p['idx'].reshape(-1, 3) + off)
        if with_jw:
            J.append(prim_jw[pi][0]); W.append(prim_jw[pi][1])
        off += len(p['pos'])
    if with_jw:
        return np.vstack(V), np.vstack(F), np.vstack(J), np.vstack(W)
    return np.vstack(V), np.vstack(F)


skinV, skinF, skinJ, skinW = collect(SKIN_MATS, with_jw=True)
ballV, ballF = collect(BALL_MATS)
print('skin tris', len(skinF), 'ball tris', len(ballF))


def ray_grid(origins, dirv, V, F):
    A = V[F[:, 0]]; Bv = V[F[:, 1]]; C = V[F[:, 2]]
    E1 = Bv - A; E2 = C - A
    best_t = np.full(len(origins), np.inf)
    best_tri = np.full(len(origins), -1)
    best_uv = np.zeros((len(origins), 2))
    P = np.cross(dirv, E2)
    det = (E1 * P).sum(1)
    ok = np.abs(det) > 1e-12
    inv = np.where(ok, 1.0 / np.where(ok, det, 1.0), 0.0)
    for s in range(0, len(origins), 256):
        O = origins[s:s + 256]
        Tv = O[:, None, :] - A[None, :, :]
        u = (Tv * P[None, :, :]).sum(2) * inv[None, :]
        Q = np.cross(Tv, E1[None, :, :])
        v = (Q * dirv[None, None, :]).sum(2) * inv[None, :]
        t = (E2[None, :, :] * Q).sum(2) * inv[None, :]
        hit = ok[None, :] & (u >= -1e-6) & (v >= -1e-6) & (u + v <= 1 + 1e-6) & (t > 1e-6)
        t = np.where(hit, t, np.inf)
        k = np.argmin(t, axis=1)
        tk = t[np.arange(len(O)), k]
        m = tk < best_t[s:s + 256]
        idx = np.where(m)[0]
        best_t[s + idx] = tk[idx]
        best_tri[s + idx] = k[idx]
        best_uv[s + idx] = np.stack([u[idx, k[idx]], v[idx, k[idx]]], axis=1)
    return best_t, best_tri, best_uv


save = {}
for side, sgn in (('posx', 1), ('negx', -1)):
    iris_c = geo[f'{side}_iris_c']; ball_c = geo[f'{side}_ball_c']
    outer = geo[f'{side}_outer']; inner = geo[f'{side}_inner']
    eye_w = meta[side]['eye_w']
    lat = (inner - outer) / np.linalg.norm(inner - outer)
    up = np.array([0., 1., 0.]); up = up - lat * (up @ lat); up /= np.linalg.norm(up)
    fwd = np.cross(lat, up)
    if fwd @ (outer - ball_c) < 0:
        fwd = -fwd
    xs = np.arange(-eye_w / 2 - 0.0015, eye_w / 2 + 0.0016, 0.0002)
    ys = np.arange(-0.013, 0.0131, 0.0002)
    O = (ball_c[None, None, :] + lat[None, None, :] * xs[:, None, None]
         + up[None, None, :] * ys[None, :, None] + fwd[None, None, :] * 0.06)
    O = O.reshape(-1, 3)
    ts, tris_s, uv_s = ray_grid(O, -fwd, skinV, skinF)
    tb, tris_b, uv_b = ray_grid(O, -fwd, ballV, ballF)
    ballvis = (tb < ts).reshape(len(xs), len(ys))
    for which in ('top', 'bot'):
        pts, nrms, js, ws, colx = [], [], [], [], []
        for i, x in enumerate(xs):
            col = ballvis[i]
            if col.sum() < 3:
                continue
            yi = np.where(col)[0]
            # use the contiguous run containing the iris-centre row
            mid = len(ys) // 2
            if not col[mid]:
                # fall back: the longest run
                runs = np.split(yi, np.where(np.diff(yi) > 1)[0] + 1)
                yi = max(runs, key=len)
            else:
                runs = np.split(yi, np.where(np.diff(yi) > 1)[0] + 1)
                yi = [r for r in runs if r.min() <= mid <= r.max()][0]
            j = yi.max() if which == 'top' else yi.min()
            jj = j + 1 if which == 'top' else j - 1
            if jj < 0 or jj >= len(ys):
                continue
            lin = i * len(ys) + jj
            tri = tris_s[lin]
            if tri < 0:
                continue
            ia, ib, ic = skinF[tri]
            A = skinV[ia]; Bv = skinV[ib]; C = skinV[ic]
            u_, v_ = uv_s[lin]
            w0 = 1 - u_ - v_
            pts.append(A * w0 + Bv * u_ + C * v_)
            n = np.cross(Bv - A, C - A); n /= (np.linalg.norm(n) + 1e-12)
            if n @ fwd < 0:
                n = -n
            nrms.append(n)
            # blend WEIGHTS per joint id (indices cannot be interpolated):
            # accumulate the 3 verts' (joint -> weight) into one vector
            acc = {}
            for vert_i, bw in ((ia, w0), (ib, u_), (ic, v_)):
                for jj, ww in zip(skinJ[vert_i], skinW[vert_i]):
                    if ww > 0:
                        acc[int(jj)] = acc.get(int(jj), 0.0) + float(ww) * bw
            js.append(acc)
            colx.append(x)
        P = np.array(pts); N = np.array(nrms)
        # top-4 joints per margin point from the accumulated weight dicts
        Jn = np.zeros((len(js), 4), dtype=int); Wn = np.zeros((len(js), 4))
        for r, acc in enumerate(js):
            top = sorted(acc.items(), key=lambda kv: -kv[1])[:4]
            for c, (jj, ww) in enumerate(top):
                Jn[r, c] = jj; Wn[r, c] = ww
            ssum = Wn[r].sum()
            if ssum > 0:
                Wn[r] /= ssum
        save[f'{side}_{which}_pts'] = P
        save[f'{side}_{which}_n'] = N
        save[f'{side}_{which}_J'] = Jn.astype(int)
        save[f'{side}_{which}_W'] = Wn
        save[f'{side}_{which}_x'] = np.array(colx)
        print(side, which, 'margin pts:', len(P))
    tm = save[f'{side}_top_pts']; bm = save[f'{side}_bot_pts']
    if len(tm) and len(bm):
        # mid-column aperture: match nearest x
        xt = save[f'{side}_top_x']; xb = save[f'{side}_bot_x']
        i0 = np.argmin(np.abs(xt)); j0 = np.argmin(np.abs(xb))
        print(f'  {side} VISIBLE aperture near centre column: '
              f'{(tm[i0][1]-bm[j0][1])*1000:.2f} mm (old loop {meta[side]["aperture_mid"]*1000:.2f})')

np.savez('work/lash_visible_margin.npz', **save)
print('saved work/lash_visible_margin.npz')
