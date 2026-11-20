"""LASH-FIX builder v7 — fan + curl + true clumps on the VISIBLE margin.

Parent gate failures addressed (see PROGRESS.md v7 section):
1. CURTAIN: v6 grew every strand along world-up on skin-hugging paths.
   v7: per-station growth direction ROTATES with station position
   (fan: outer +54deg toward the wing, centre ~0, inner -36deg), and the
   path is a curl bezier — emerge forward off the lid, sweep up/out,
   forward bow 0.36x rise at mid, 0.30x at tip. The skin surface is used
   ONLY as a minimum forward-clearance floor (surf grid + 0.9mm).
2. NO CLUMPS: v7 emits ONE clump per station = 6 strands sharing a root
   (root jitter sigma 0.05mm), per-strand direction jitter +-5deg and
   length jitter, so tips splay while roots stay a tight bundle; gaps
   fall between stations (pitch ~0.71mm).
3. DETACHED WING: v7 wing stations CONTINUE the lid sequence past the
   corner — roots step along the temple from the corner itself with
   gradually growing spacing/rise, fan angle continuing 54->92deg.
   No separate anchor curve.
4. ROOT SEAT: roots sit on the VISIBLE lash line extracted by
   lash_margin_visible.py (front-ray ball-visibility boundary), NOT the
   hidden Face/EyeSocket seam loop (occluded in renders — proven).
   A thin falsie STRIP ribbon on the margin makes the root line read
   as one dense dark line; strand roots (+0.55mm along margin normal,
   the spec base offset) sit inside the strip band.
Colour: RGB 0.012, alpha 1.0 everywhere except the tip point (0.85) —
v6's 0.80 top ring was the grey wash; feathering is taper + splay.
Spec unchanged: 27 lid + 8 wing stations, band rise 1.05 iris O above
the margin (up-component held constant across the fan), wing 0.60
eye-widths rising 0.55 iris O, base offset 0.55mm.
Output: work/lashes_megami_geom7.npz
"""
import sys, json
sys.path.insert(0, 'scripts')
import numpy as np
from lash_glb_lib import load_glb, accessor, skinned_positions
from scipy.spatial import cKDTree

SPEC = dict(band_rise_iris=1.05, wing_eyewidths=0.60, wing_rise_iris=0.55,
            base_off_m=0.00055, hug_clear_m=0.0009,
            prof_mid=1.0, prof_inner=0.88, prof_outer=1.10,
            strands_per_clump=6, strand_r0_m=0.000058)

rng = np.random.default_rng(20261110)

geo = np.load('work/lash_megami_geometry.npz', allow_pickle=True)
meta = json.loads(str(geo['meta']))
vis = np.load('work/lash_visible_margin.npz', allow_pickle=True)
g, b, _ = load_glb('work/megami-angel-gnmface-v2.glb')
matnames = [m.get('name') for m in g['materials']]
mesh10 = skinned_positions(g, b, 10, {'AngelFace': 1.0, 'AngelBody': 1.0})
skin_prims = [p for p in mesh10 if matnames[p['mat']] in ('Face-2', 'EyeSocket-2')]
skin_V = np.vstack([p['pos'] for p in skin_prims])
skin_F = []
off = 0
for p in skin_prims:
    skin_F.append(p['idx'].reshape(-1, 3) + off)
    off += len(p['pos'])
skin_F = np.vstack(skin_F)
skin_tree = cKDTree(skin_V)
TA = skin_V[skin_F[:, 0]]; TB = skin_V[skin_F[:, 1]]; TC = skin_V[skin_F[:, 2]]
E1 = TB - TA; E2 = TC - TA


def ray_fwd_t(origin, dirv):
    """first-hit distance along dirv for ONE origin (v6-style)."""
    P = np.cross(dirv, E2)
    det = (E1 * P).sum(1)
    ok = np.abs(det) > 1e-10
    inv = np.where(ok, 1.0 / np.where(ok, det, 1.0), 0.0)
    Tv = origin - TA
    u = (Tv * P).sum(1) * inv
    Q = np.cross(Tv, E1)
    v = (Q * dirv).sum(1) * inv
    t = (E2 * Q).sum(1) * inv
    hit = ok & (u >= -1e-6) & (v >= -1e-6) & (u + v <= 1 + 1e-6) & (t > 1e-6)
    if not hit.any():
        return None
    return float(t[hit].min())


def nearest_on_surface(pt):
    _, cand = skin_tree.query(pt, k=24)
    mask = np.isin(skin_F, cand)
    sel = skin_F[mask.any(axis=1)]
    A = skin_V[sel[:, 0]]; Bv = skin_V[sel[:, 1]]; C = skin_V[sel[:, 2]]
    AP = pt - A; AB = Bv - A; AC = C - A
    d1 = (AB * AP).sum(1); d2 = (AC * AP).sum(1)
    D = (AB * AB).sum(1) * (AC * AC).sum(1) - (AB * AC).sum(1) ** 2
    D = np.where(np.abs(D) < 1e-14, 1e-14, D)
    s = np.clip(((AC * AC).sum(1) * d1 - (AB * AC).sum(1) * d2) / D, 0, 1)
    t = np.clip(((AB * AB).sum(1) * d2 - (AB * AC).sum(1) * d1) / D, 0, 1)
    s = np.minimum(s, 1 - t)
    q = A + s[:, None] * AB + t[:, None] * AC
    dist = np.linalg.norm(q - pt, axis=1)
    k = int(np.argmin(dist))
    n = np.cross(AB[k], AC[k]); n /= (np.linalg.norm(n) + 1e-12)
    return q[k], float(dist[k]), n


def smooth(P, w=5):
    if len(P) < w:
        return P
    ker = np.hanning(w); ker /= ker.sum()
    pad = np.vstack([np.repeat(P[:1], w // 2, 0), P, np.repeat(P[-1:], w // 2, 0)])
    return np.stack([np.convolve(pad[:, c], ker, 'valid') for c in range(3)], axis=1)


def resample(P, step):
    seg = np.linalg.norm(np.diff(P, axis=0), axis=1)
    cum = np.r_[0, np.cumsum(seg)]
    tot = cum[-1]
    n = max(2, int(tot / step) + 1)
    s = np.linspace(0, tot, n)
    out = np.stack([np.interp(s, cum, P[:, c]) for c in range(3)], axis=1)
    return out, tot


verts, cols, tris, jts, wts = [], [], [], [], []
voff = 0
RING_FR = (0.0, 0.18, 0.38, 0.58, 0.78, 0.92)
root_records = []   # (root_pt, margin_pt) for measurement


def emit_strand(path_pts, tang0, fwd, jw_J, jw_W, r0, shade=0.012):
    """Tapered tube along an explicit path (list of 3D points)."""
    global voff, tris
    # resample path to ring fractions by arc length
    seg = np.linalg.norm(np.diff(path_pts, axis=0), axis=1)
    cum = np.r_[0, np.cumsum(seg)]
    tot = cum[-1] if cum[-1] > 0 else 1.0
    ring0 = voff
    centres = []
    for fr in RING_FR:
        s = fr * tot
        j = int(np.searchsorted(cum, s) - 1)
        j = min(max(j, 0), len(path_pts) - 2)
        f = (s - cum[j]) / max(seg[j], 1e-12) if seg[j] > 0 else 0.0
        c = path_pts[j] * (1 - f) + path_pts[j + 1] * f
        centres.append(c)
        r = r0 * (1 - fr) ** 1.1 + 0.000006
        # ring frame: one axis along margin tangent, other = tangent x path dir
        j2 = min(j + 1, len(path_pts) - 1)
        tg = path_pts[j2] - path_pts[max(j - 1, 0)]
        tg = tg / (np.linalg.norm(tg) + 1e-12)
        bn = np.cross(tg, tang0); bn /= (np.linalg.norm(bn) + 1e-12)
        ax = np.cross(bn, tg); ax /= (np.linalg.norm(ax) + 1e-12)
        for a_vec, a_sgn in ((ax, 1), (bn, 1), (ax, -1), (bn, -1)):
            verts.append(c + a_vec * r * a_sgn)
            cols.append([shade, shade, shade, 1.0])
            jts.append(jw_J); wts.append(jw_W)
            voff += 1
    tip = path_pts[-1]
    verts.append(tip)
    cols.append([shade, shade, shade, 0.85])
    jts.append(jw_J); wts.append(jw_W)
    tip_i = voff; voff += 1
    nr = len(RING_FR)
    for k in range(nr - 1):
        a0 = ring0 + k * 4; b0 = a0 + 4
        for q in range(4):
            q2 = (q + 1) % 4
            tris += [[a0 + q, a0 + q2, b0 + q], [a0 + q2, b0 + q2, b0 + q]]
    last = ring0 + (nr - 1) * 4
    for q in range(4):
        q2 = (q + 1) % 4
        tris += [[last + q, last + q2, tip_i]]


def bezier_path(root, e0, gdir, fwd, rise, out_dir, fan_drift):
    """Curl path: emerge along e0 (forward off the lid), sweep to gdir,
    forward bow 0.36x rise mid / 0.30x at tip, tips drift further out."""
    C0 = root
    C1 = root + e0 * (rise * 0.42)
    tip = root + gdir * rise + fwd * (0.30 * rise) + out_dir * fan_drift
    C2 = root + gdir * (rise * 0.86) + fwd * (0.36 * rise) + out_dir * (fan_drift * 0.8)
    K = 14
    pts = []
    for k in range(K + 1):
        t = k / K
        p = ((1 - t) ** 3 * C0 + 3 * (1 - t) ** 2 * t * C1
             + 3 * (1 - t) * t ** 2 * C2 + t ** 3 * tip)
        pts.append(p)
    return np.array(pts)


THETA_PTS = [(0.0, 54.0), (0.25, 30.0), (0.5, 6.0), (0.75, -16.0), (1.0, -36.0)]


def theta_of(u):
    xs = [p[0] for p in THETA_PTS]; ys = [p[1] for p in THETA_PTS]
    return np.radians(float(np.interp(u, xs, ys)))


for side, sgn in (('posx', 1), ('negx', -1)):
    iris_d = float(meta[side]['iris_d'])
    eye_w = float(meta[side]['eye_w'])
    ball_c = geo[f'{side}_ball_c']
    outer = geo[f'{side}_outer']; inner = geo[f'{side}_inner']
    lat = (inner - outer) / eye_w
    up = np.array([0.0, 1.0, 0.0]); up = up - lat * (up @ lat); up /= np.linalg.norm(up)
    fwd = np.cross(lat, up)
    if fwd @ (outer - ball_c) < 0:
        fwd = -fwd
    out_dir = -lat

    # ---- visible margin curves (dense, ordered outer -> inner by x) ----
    mt = vis[f'{side}_top_pts']; mn = vis[f'{side}_top_n']
    mJ = vis[f'{side}_top_J']; mW = vis[f'{side}_top_W']
    mx = vis[f'{side}_top_x']
    order = np.argsort(mx) if sgn > 0 else np.argsort(-mx)
    # x measured along lat from ball_c; outer = smaller projection on lat
    proj = (mt - ball_c) @ lat
    order = np.argsort(proj)
    mt, mn, mJ, mW = mt[order], mn[order], mJ[order], mW[order]
    mt_s = smooth(mt, 7)
    mn_s = smooth(mn, 7); mn_s /= (np.linalg.norm(mn_s, axis=1, keepdims=True) + 1e-12)
    curve, curve_len = resample(mt_s, 0.00025)
    # per-curve-point J/W + normal by nearest dense sample
    _, near = cKDTree(mt_s).query(curve)
    cJ, cW, cN = mJ[near], mW[near], mn_s[near]
    pitch = curve_len / 26.0

    # ---- forward-clearance floor: surf fwd-depth grid over eye+temple ----
    gx = np.arange(-(eye_w / 2 + SPEC['wing_eyewidths'] * eye_w + 0.002),
                   eye_w / 2 + 0.002, 0.0004)
    gy = np.arange(-0.004, 0.017, 0.0004)
    surf = np.full((len(gx), len(gy)), -1e9)
    for i, xx in enumerate(gx):
        for j, yy in enumerate(gy):
            org = ball_c + lat * xx + up * yy + fwd * 0.05
            th = ray_fwd_t(org, -fwd)
            if th is not None:
                surf[i, j] = 0.05 - th

    def clearance(pts, skip=1):
        """push path points (except first `skip`) forward of the skin."""
        out = pts.copy()
        for k in range(skip, len(pts)):
            p = pts[k]
            rel = p - ball_c
            xx, yy = rel @ lat, rel @ up
            i = int(np.clip((xx - gx[0]) / 0.0004, 0, len(gx) - 1))
            j = int(np.clip((yy - gy[0]) / 0.0004, 0, len(gy) - 1))
            need = surf[i, j] + SPEC['hug_clear_m']
            have = rel @ fwd
            if have < need:
                out[k] = p + fwd * (need - have)
        return out

    def station_frame(idx_f):
        """margin point, normal, J/W, tangent at curve fraction idx_f."""
        j = int(np.clip(round(idx_f), 0, len(curve) - 1))
        p = curve[j]
        tang = curve[min(j + 2, len(curve) - 1)] - curve[max(j - 2, 0)]
        tang /= (np.linalg.norm(tang) + 1e-12)
        return p, cN[j], cJ[j], cW[j], tang

    RISE0 = SPEC['band_rise_iris'] * iris_d

    def emit_clump(root_m, nrm, tang, jw_J, jw_W, theta, rise_along_g,
                   e0_mix=(0.80, 0.55, 0.20), seed=0, drift_scale=1.0,
                   contain=None):
        """One clump: strands_per_clump strands sharing the root."""
        gdir = up * np.cos(theta) + out_dir * np.sin(theta)
        gdir /= np.linalg.norm(gdir)
        root = root_m + nrm * SPEC['base_off_m']
        root_records.append((root.copy(), root_m.copy()))
        e0 = fwd * e0_mix[0] + gdir * e0_mix[1] + nrm * e0_mix[2]
        e0 /= np.linalg.norm(e0)
        fan_drift = np.sin(theta) * rise_along_g * 0.35 * drift_scale
        base_path = bezier_path(root, e0, gdir, fwd, rise_along_g, out_dir, fan_drift)
        base_path = clearance(base_path, skip=1)
        if contain is not None:
            # wing containment: no path point may hover > contain mm off
            # the skin — far-temple points get pulled back to the head
            for k2 in range(1, len(base_path)):
                q, dist, _n = nearest_on_surface(base_path[k2])
                if dist > contain:
                    base_path[k2] = q + (base_path[k2] - q) * (contain / dist)
        S = SPEC['strands_per_clump']
        rseed = rng.random(4 * S + 4)
        for sj in range(S):
            dth = np.radians((rseed[sj * 4] - 0.5) * 10.0)       # +-5 deg fan jitter
            dph = np.radians((rseed[sj * 4 + 1] - 0.5) * 8.0)    # +-4 deg fwd jitter
            lj = 1.0 - 0.16 * rseed[sj * 4 + 2]
            rj = (rseed[sj * 4 + 3] - 0.5) * 0.00012
            # rotate base path around root: fan-plane then fwd-plane, scale by lj
            rel = base_path - root
            c1, s1 = np.cos(dth), np.sin(dth)
            rel2 = rel.copy()
            a = rel @ up; o = rel @ out_dir; f = rel @ fwd
            a2 = a * c1 - o * s1; o2 = a * s1 + o * c1
            c2, s2 = np.cos(dph), np.sin(dph)
            a3 = a2 * c2 - f * s2; f3 = a2 * s2 + f * c2
            tt = np.linspace(0, 1, len(base_path))
            sc = 1.0 - (1.0 - lj) * tt
            rel3 = (up[None, :] * (a3 * sc)[:, None] + out_dir[None, :] * (o2 * sc)[:, None]
                    + fwd[None, :] * (f3 * sc)[:, None])
            sp = root + tang * rj + rel3
            sp[0] = root + tang * rj
            emit_strand(sp, tang, fwd, jw_J, jw_W, SPEC['strand_r0_m'])

    # ---- lid stations: 27 across the visible margin ----
    n_st = 27
    for i in range(n_st):
        u = i / (n_st - 1.0)
        p, nrm, jJ, jW, tang = station_frame(u * (len(curve) - 1))
        theta = theta_of(u)
        prof = SPEC['prof_mid'] + (SPEC['prof_inner'] - SPEC['prof_mid']) * max(0.0, (u - 0.55) / 0.45) \
            + (SPEC['prof_outer'] - SPEC['prof_mid']) * max(0.0, (0.3 - u) / 0.3)
        # sqrt-cos compensation: outer strands lengthen modestly (1.3x at
        # 54deg) instead of the 1.87x a constant up-rise would force
        rise = RISE0 * prof / np.sqrt(max(np.cos(theta), 0.35))
        emit_clump(p, nrm, tang, jJ, jW, theta, rise, seed=i)

    # ---- wing: continuation past the OUTER corner (curve index 0 end) ----
    corner = curve[0]
    ctang = curve[0] - curve[3]
    ctang /= (np.linalg.norm(ctang) + 1e-12)   # points outward along margin
    WING_LEN = SPEC['wing_eyewidths'] * eye_w
    for k in range(1, 9):
        f = k / 8.0
        d_k = WING_LEN * f ** 1.25
        rise_k = SPEC['wing_rise_iris'] * iris_d * f ** 1.6
        anchor = corner + ctang * d_k + up * rise_k
        q, dist, nrm = nearest_on_surface(anchor)
        theta = np.radians(54.0 + 26.0 * f)   # caps at 80deg (v7a hit 92:
        # far-wing strands left the head and streaked past the silhouette)
        # wing strands TAPER along the sweep (no cos compensation — at
        # 92deg that would make 20mm horizontal spikes off the temple)
        rise = RISE0 * (1.0 - 0.55 * f)
        # wing J/W: nearest margin J/W (corner)
        emit_clump(q, nrm, ctang, cJ[0], cW[0], theta, rise,
                   e0_mix=(0.40, 0.60, 0.30), seed=900 + k,
                   drift_scale=0.45, contain=0.0012)

    # ---- falsie strip: ribbon on the visible margin ----
    sdir = up - lat * (up @ lat); sdir /= np.linalg.norm(sdir)
    strip0 = voff
    nseg = len(curve)
    for j in range(nseg):
        p = curve[j]; nrm = cN[j]
        lo = p - sdir * 0.00015 + nrm * 0.00028
        hi = p + sdir * 0.00075 + nrm * 0.00042
        for vtx in (lo, hi):
            verts.append(vtx)
            cols.append([0.012, 0.012, 0.012, 1.0])
            jts.append(cJ[j]); wts.append(cW[j])
            voff += 1
    for j in range(nseg - 1):
        a0 = strip0 + j * 2
        tris += [[a0, a0 + 1, a0 + 2], [a0 + 1, a0 + 3, a0 + 2]]

    # ---- lower lashes on the visible BOT margin ----
    bt = vis[f'{side}_bot_pts']; bn = vis[f'{side}_bot_n']
    bJ = vis[f'{side}_bot_J']; bW = vis[f'{side}_bot_W']
    projb = (bt - ball_c) @ lat
    orderb = np.argsort(projb)
    bt, bn, bJ, bW = bt[orderb], bn[orderb], bJ[orderb], bW[orderb]
    bt_s = smooth(bt, 7)
    bcurve, blen = resample(bt_s, 0.00025)
    _, nearb = cKDTree(bt_s).query(bcurve)
    aperture = float(meta[side]['aperture_mid'])
    max_len = 0.11 * aperture
    nb = len(bcurve)
    for i in range(0, nb, 24):
        p = bcurve[i]
        nrm = bn[nearb[i]]
        tang = bcurve[min(i + 2, nb - 1)] - bcurve[max(i - 2, 0)]
        tang /= (np.linalg.norm(tang) + 1e-12)
        d = np.cross(tang, nrm); d /= (np.linalg.norm(d) + 1e-12)
        if d[1] > 0:
            d = -d
        s = i / (nb - 1)
        prof = np.sin(np.pi * np.clip(s, 0, 1)) ** 0.8
        L = max_len * max(prof, 0.05)
        base = p + nrm * SPEC['base_off_m']
        mini = np.array([base, base + d * (L * 0.52) + nrm * 0.00105,
                         base + d * L + nrm * 0.00095])
        for sj in range(3):
            off_t = (sj - 1) * 0.00007
            emit_strand(mini + tang * off_t, tang, nrm, bJ[nearb[i]], bW[nearb[i]], 0.000040)
    print(side, 'built v7')

V = np.array(verts); T = np.array(tris); C = np.array(cols)
J = np.array(jts); W = np.array(wts)

geo2 = geo
cent = V[T].mean(axis=1)
fn = np.cross(V[T[:, 1]] - V[T[:, 0]], V[T[:, 2]] - V[T[:, 0]])
ball = np.where((cent[:, 0] >= 0)[:, None], geo2['posx_ball_c'], geo2['negx_ball_c'])
bad = (fn * (cent - ball)).sum(1) < 0
T[bad] = T[bad][:, [0, 2, 1]]
print('winding flips:', int(bad.sum()), '/', len(T))

Nr = np.zeros_like(V)
tv = V[T]
fn = np.cross(tv[:, 1] - tv[:, 0], tv[:, 2] - tv[:, 0])
for k in range(3):
    np.add.at(Nr, T[:, k], fn)
Nr /= (np.linalg.norm(Nr, axis=1, keepdims=True) + 1e-12)

# ---- measurements: strand roots vs VISIBLE margin and vs OLD seam loop ----
R = np.array([r for r, m in root_records])
M = np.array([m for r, m in root_records])
d_vis = np.linalg.norm(R - M, axis=1) * 1000
old_top = np.vstack([geo['posx_top'], geo['negx_top']])
dd, _ = cKDTree(old_top).query(R)
d_old = dd * 1000
print(f'root-to-VISIBLE-margin: mean {d_vis.mean():.3f} max {d_vis.max():.3f} mm (n={len(R)})')
print(f'root-to-OLD-seam-loop : mean {d_old.mean():.3f} max {d_old.max():.3f} mm')
np.savez('work/lashes_megami_geom7.npz', V=V, T=T, C=C, N=Nr, J=J, W=W,
         measure=json.dumps({'builder': 'v7 fan/curl/clumps on visible margin',
                             'root_to_visible_margin_mm': [float(d_vis.mean()), float(d_vis.max())],
                             'root_to_old_seam_mm': [float(d_old.mean()), float(d_old.max())],
                             'n_roots': len(R)}))
print('lash geom v7:', V.shape, T.shape)
