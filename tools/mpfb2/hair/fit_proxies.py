#!/usr/bin/env python3
"""Fit MakeHuman / MPFB2 CC0 proxy assets (hair, eyebrows, eyelashes) and
procedural CC0 beard shells onto the creation-suite template bodies.

Pure numpy/scipy (no Blender needed). Pipeline per asset x template:
 1. MakeHuman fit: every proxy vertex = sum(w_i * basemesh[v_i]) + offset * scale
    (the .mhclo formula MakeHuman / MPFB2 use), on the CC0 MakeHuman base mesh.
 2. Head transfer: affine A (eye-landmark init + ICP over the head surface) maps the
    MakeHuman head onto the template's head (bind pose, world space).
 3. Surface-relative correction: vertices near the skin keep their height above the
    skin (closest-point + normal on each mesh), fading to the plain affine 6 cm out,
    then a scalp push-out so no vertex sits inside the template head.
 4. Output in HEAD-BONE-LOCAL space (inverse(head joint world matrix) at bind), so the
    runtime parents the mesh to the head bone with an identity transform; plus the
    template's face/head morph deltas resampled onto the part (k-NN over head-weighted
    skin) under the SAME target names, so face sliders move brows/lashes/beards/hair.

Inputs: dumps/<template>.json (dump.mjs), base.obj (MPFB2 data/3dobjs, CC0),
mh/<type>/<name>/<name>.{mhclo,obj} (makehuman_system_assets_cc0.zip).
Output: fit/<asset>/<template>.json (consumed by build_glb.mjs).
"""
import json, os, sys, re
import numpy as np
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATES = ['super-heavyweight', 'powerhouse', 'showman', 'technician', 'highflyer', 'luchador',
             'powerhouse-w', 'athletic-w', 'striker-w']


# ---------------- MakeHuman base mesh ----------------
def load_base(path):
    V, groups, faces_body = [], {}, []
    cur = None
    for line in open(path):
        if line.startswith('v '):
            V.append([float(x) for x in line.split()[1:4]])
        elif line.startswith('g '):
            cur = line.split()[1]
        elif line.startswith('f '):
            idx = [int(t.split('/')[0]) - 1 for t in line.split()[1:]]
            groups.setdefault(cur, set()).update(idx)
            if cur == 'body':
                for k in range(1, len(idx) - 1):
                    faces_body.append([idx[0], idx[k], idx[k + 1]])
    V = np.array(V) * 0.1  # MakeHuman decimetres -> metres
    return V, groups, np.array(faces_body)


def vertex_normals(V, F):
    n = np.zeros_like(V)
    fn = np.cross(V[F[:, 1]] - V[F[:, 0]], V[F[:, 2]] - V[F[:, 0]])
    for k in range(3):
        np.add.at(n, F[:, k], fn)
    l = np.linalg.norm(n, axis=1, keepdims=True); l[l == 0] = 1
    return n / l


# ---------------- proxy (.mhclo + .obj) ----------------
def load_mhclo(path):
    refs, scales, in_verts = [], {}, False
    for line in open(path):
        s = line.strip()
        if not s or s.startswith('#'):
            continue
        tok = s.split()
        if tok[0] in ('x_scale', 'y_scale', 'z_scale'):
            scales[tok[0][0]] = (int(tok[1]), int(tok[2]), float(tok[3]))
            continue
        if tok[0] == 'verts':
            in_verts = True; continue
        if in_verts:
            if re.match(r'^-?\d', tok[0]) and len(tok) in (1, 9):
                if len(tok) == 1:
                    refs.append(([int(tok[0])] * 3, [1.0, 0, 0], [0, 0, 0]))
                else:
                    refs.append(([int(t) for t in tok[0:3]], [float(t) for t in tok[3:6]], [float(t) for t in tok[6:9]]))
            elif tok[0] in ('delete_verts', 'weights'):
                in_verts = False
            # other keyword lines inside the verts block (e.g. 'material ...') are skipped
    return refs, scales


def load_obj(path):
    V, VT, F = [], [], []
    for line in open(path):
        if line.startswith('v '):
            V.append([float(x) for x in line.split()[1:4]])
        elif line.startswith('vt '):
            VT.append([float(x) for x in line.split()[1:3]])
        elif line.startswith('f '):
            corners = []
            for t in line.split()[1:]:
                p = t.split('/')
                corners.append((int(p[0]) - 1, int(p[1]) - 1 if len(p) > 1 and p[1] else -1))
            for k in range(1, len(corners) - 1):
                F.append([corners[0], corners[k], corners[k + 1]])
    return np.array(V), np.array(VT) if VT else np.zeros((0, 2)), F


def fit_on_base(base_dm, refs, scales):
    """MakeHuman's proxy fit, on the base mesh in its native decimetres; returns metres."""
    sc = {}
    for ax, (a, b, d) in scales.items():
        k = 'xyz'.index(ax)
        sc[k] = abs(base_dm[a, k] - base_dm[b, k]) / d if d else 1.0
    out = np.zeros((len(refs), 3))
    for i, (vi, w, off) in enumerate(refs):
        p = w[0] * base_dm[vi[0]] + w[1] * base_dm[vi[1]] + w[2] * base_dm[vi[2]]
        out[i] = p + np.array([off[0] * sc.get(0, 1), off[1] * sc.get(1, 1), off[2] * sc.get(2, 1)])
    return out * 0.1


def split_uv(Vfit, VT, F):
    """obj corners (v, vt) -> unique glTF vertices."""
    key2i, pos, uv, tris = {}, [], [], []
    for tri in F:
        t = []
        for (v, vt) in tri:
            k = (v, vt)
            if k not in key2i:
                key2i[k] = len(pos); pos.append(v)
                uv.append(VT[vt] if vt >= 0 else [0, 0])
            t.append(key2i[k])
        tris.append(t)
    return np.array(pos), np.array(uv), np.array(tris)


# ---------------- template ----------------
def load_template(name):
    d = json.load(open(os.path.join(HERE, 'dumps', name + '.json')))
    D = np.array(d['node_matrix']).reshape(4, 4).T
    to_w = lambda P: (D[:3, :3] @ P.T).T + D[:3, 3]
    sk = d['prims']['skin']
    P = to_w(np.array(sk['pos']).reshape(-1, 3))
    F = np.array(sk['idx']).reshape(-1, 3)
    E = to_w(np.array(d['prims']['eyes']['pos']).reshape(-1, 3))
    H = np.array(d['head_world']).reshape(4, 4).T
    T = [(D[:3, :3] @ np.array(t).reshape(-1, 3).T).T for t in sk['targets']]
    return dict(P=P, F=F, N=vertex_normals(P, F), headw=np.array(sk['headw']),
                eyeL=E[E[:, 0] > 0].mean(0), eyeR=E[E[:, 0] < 0].mean(0),
                Hinv=np.linalg.inv(H), T=T, names=d['targetNames'])


def head_region(P, eyeL, eyeR):
    eye = (eyeL + eyeR) / 2
    top = P[:, 1].max()
    h = top - eye[1]
    m = (P[:, 1] > eye[1] - 0.95 * h) & (np.abs(P[:, 0]) < 1.6 * h) & (np.abs(P[:, 2] - eye[2]) < 2.2 * h)
    return m


def solve_affine(X, Y, reg, s0):
    """least squares Y ~ X @ M.T + t, regularised toward uniform scale s0 * I."""
    Xh = np.hstack([X, np.ones((len(X), 1))])
    A = Xh.T @ Xh + reg * np.diag([1, 1, 1, 0])
    B = Xh.T @ Y + reg * np.vstack([np.eye(3) * s0, np.zeros((1, 3))])
    sol = np.linalg.solve(A, B)
    return sol[:3].T, sol[3]


def head_transfer(base, mhgroups, tpl):
    V, Fb = base['V'], base['F']
    eyeL = V[list(mhgroups['helper-l-eye'])].mean(0)
    eyeR = V[list(mhgroups['helper-r-eye'])].mean(0)
    bodyv = np.array(sorted(mhgroups['body']))
    mmh = np.zeros(len(V), bool); mmh[bodyv] = True
    mmh &= head_region(V, eyeL, eyeR)
    mtp = head_region(tpl['P'], tpl['eyeL'], tpl['eyeR']) & (tpl['headw'] > 0.2)
    X0, Y = V[mmh], tpl['P'][mtp]
    # init: eye midpoint + eye spacing / head height scale
    s_eye = np.linalg.norm(tpl['eyeL'] - tpl['eyeR']) / np.linalg.norm(eyeL - eyeR)
    s_h = (Y[:, 1].max() - tpl['eyeL'][1]) / (X0[:, 1].max() - eyeL[1])
    s0 = 0.5 * (s_eye + s_h)
    M = np.eye(3) * s0
    t = (tpl['eyeL'] + tpl['eyeR']) / 2 - M @ ((eyeL + eyeR) / 2)
    tree = cKDTree(Y)
    treeX = None
    for it in range(25):
        XT = X0 @ M.T + t
        d1, j1 = tree.query(XT)
        treeX = cKDTree(XT); d2, j2 = treeX.query(Y)
        keep1 = d1 < np.percentile(d1, 90); keep2 = d2 < np.percentile(d2, 90)
        Xs = np.vstack([X0[keep1], X0[j2[keep2]], np.repeat([eyeL, eyeR], 200, axis=0)])
        Ys = np.vstack([Y[j1[keep1]], Y[keep2], np.repeat([tpl['eyeL'], tpl['eyeR']], 200, axis=0)])
        M, t = solve_affine(Xs, Ys, reg=len(Xs) * 0.02, s0=s0)
    XT = X0 @ M.T + t
    rms = float(np.sqrt((tree.query(XT)[0] ** 2).mean()))
    eye_err = float(max(np.linalg.norm(M @ eyeL + t - tpl['eyeL']), np.linalg.norm(M @ eyeR + t - tpl['eyeR'])))
    return M, t, dict(rms_m=rms, eye_err_m=eye_err, scale=float(np.cbrt(abs(np.linalg.det(M)))),
                      eyes_mh=(eyeL, eyeR))


def transfer(points, kind, base, tpl, M, t, info):
    """map MakeHuman-space points onto the template head (world bind space)."""
    V, NV = base['V'], base['N']
    head_skin = base['head_skin']
    treeMH = cKDTree(V[head_skin])
    tmask = np.where(tpl['headw'] > 0.05)[0]
    treeT = cKDTree(tpl['P'][tmask])
    s = info['scale']
    A = points @ M.T + t
    # eye landmark residual (exact eyes for lashes / brows)
    eL, eR = info['eyes_mh']
    resL = tpl['eyeL'] - (M @ eL + t); resR = tpl['eyeR'] - (M @ eR + t)
    def field(X):  # smooth landmark residual: eyes land exactly on the template eyes
        wl = np.exp(-np.sum((X - (M @ eL + t)) ** 2, 1) / (0.04 ** 2))
        wr = np.exp(-np.sum((X - (M @ eR + t)) ** 2, 1) / (0.04 ** 2))
        return wl[:, None] * resL + wr[:, None] * resR
    if kind == 'eyelashes':
        return A + field(A)
    A = A + field(A)
    _, j = treeMH.query(points)
    q = V[head_skin][j]; n = NV[head_skin][j]
    h = np.einsum('ij,ij->i', points - q, n)          # height above MakeHuman skin
    qa = q @ M.T + t
    qa = qa + field(qa)
    _, k = treeT.query(qa)
    qt = tpl['P'][tmask][k]; nt = tpl['N'][tmask][k]
    surf = qt + nt * (h * s)[:, None]
    w = np.clip(1.0 - (np.abs(h * s) - 0.015) / 0.045, 0, 1)
    out = w[:, None] * surf + (1 - w)[:, None] * A
    # scalp push-out: nothing inside the template head skin (min clearance per kind)
    clear = {'hair': 0.004, 'eyebrows': 0.0012, 'beard': 0.0015}.get(kind, 0.002)
    for _ in range(2):
        dd, k2 = treeT.query(out)
        q2 = tpl['P'][tmask][k2]; n2 = tpl['N'][tmask][k2]
        hh = np.einsum('ij,ij->i', out - q2, n2)
        onhead = (tpl['headw'][tmask][k2] > 0.5) & (dd < 0.03)   # never push off the neck / shoulders
        push = np.where((hh < clear) & onhead, clear - hh, 0)
        out = out + n2 * push[:, None]
    return out


HAIR_TARGETS = re.compile(r'^(f_head_[wh]|f_fh_|f_temples|f_round|f_square|f_tri|f_ear_size|f_ear_w|f_ear_angle|b_head_size)[+-]$')


def resample_targets(pos_w, tpl, kind='hair', min_delta=0.0006):
    """template morph deltas (world, bind) -> per part vertex, k-NN over head skin; returned head-local."""
    m = np.where(tpl['headw'] > 0.3)[0]
    tree = cKDTree(tpl['P'][m])
    dist, j = tree.query(pos_w, k=4)
    w = 1.0 / np.maximum(dist, 1e-4); w /= w.sum(1, keepdims=True)
    R = tpl['Hinv'][:3, :3]
    out = {}
    if kind == 'hair':
        min_delta = 0.0015  # hair follows head shape (face/head targets) only; keeps files small
    for name, T in zip(tpl['names'], tpl['T']):
        if kind == 'hair' and not HAIR_TARGETS.match(name):
            continue
        Tm = T[m]
        d = np.einsum('ik,ikj->ij', w, Tm[j])
        if np.abs(d).max() < min_delta:
            continue
        out[name] = (d @ R.T)
    return out


# ---------------- procedural beard shells (cut from the CC0 base mesh) ----------------
def _face(x, y, z):
    full = ((y < -0.05) | ((y < -0.022) & (np.abs(x) > 0.042))) & (y > -0.14) & (z > -0.045) & (np.abs(x) < 0.075)
    lips = (np.abs(x) < 0.028) & (y < -0.061) & (y > -0.081) & (z > 0.012)
    return full & ~lips


def _moustache(x, y, z):
    return (y < -0.046) & (y > -0.063) & (np.abs(x) < 0.031) & (z > 0.012)


BEARDS = {
    # name: region over MakeHuman head coords (x, y, z) relative to the eye midpoint, metres
    # (MakeHuman base profile: nose base y=-0.045, upper lip -0.057, mouth -0.066, lower lip -0.075, chin -0.11)
    'beard-full':      dict(offset=0.004, region=_face),
    'beard-goatee':    dict(offset=0.004, region=lambda x, y, z: (_face(x, y, z) & (np.abs(x) < 0.026) & (y < -0.079) & (y > -0.125) & (z > -0.01)) | _moustache(x, y, z)),
    'beard-moustache': dict(offset=0.003, region=_moustache),
    'beard-chinstrap': dict(offset=0.003, region=lambda x, y, z: _face(x, y, z) & ~((np.abs(x) < 0.05) & (y > -0.098) & (z > -0.005))),
    'beard-stubble':   dict(offset=0.0015, region=_face),
}


def beard_shell(base, groups, spec, uv_all, uv_faces):
    V, F, N = base['V'], base['F'], base['N']
    eye = (V[list(groups['helper-l-eye'])].mean(0) + V[list(groups['helper-r-eye'])].mean(0)) / 2
    R = V - eye
    sel = spec['region'](R[:, 0], R[:, 1], R[:, 2])
    bodym = np.zeros(len(V), bool); bodym[sorted(groups['body'])] = True
    ctr = eye + np.array([0, -0.02, -0.06])
    sel &= bodym & (np.einsum('ij,ij->i', N, V - ctr) > 0)
    fsel = sel[F].all(1)
    Fs = F[fsel]
    used = np.unique(Fs)
    remap = -np.ones(len(V), int); remap[used] = np.arange(len(used))
    pos = V[used] + N[used] * spec['offset']
    # planar cylindrical UV around the face (texture is a tiling strand mask)
    ang = np.arctan2(R[used, 0], R[used, 2])
    uv = np.stack([ang * 2.5, R[used, 1] * 25.0], 1)
    return pos, uv, remap[Fs]


def main():
    out_root = os.path.join(HERE, 'fit')
    base_dm = None
    Vm, groups, Fb = load_base(os.path.join(HERE, 'base.obj'))
    base_dm = Vm * 10
    base = dict(V=Vm, F=Fb, N=vertex_normals(Vm, Fb))
    eyeL = Vm[list(groups['helper-l-eye'])].mean(0); eyeR = Vm[list(groups['helper-r-eye'])].mean(0)
    hs = np.zeros(len(Vm), bool); hs[sorted(groups['body'])] = True
    hs &= head_region(Vm, eyeL, eyeR)
    base['head_skin'] = np.where(hs)[0]

    assets = json.load(open(os.path.join(HERE, 'assets.json')))
    only = set(sys.argv[1:])
    tpls = {n: load_template(n) for n in TEMPLATES}
    xf = {n: head_transfer(base, groups, tpls[n]) for n in TEMPLATES}
    report = {'templates': {n: xf[n][2] | {'eyes_mh': None} for n in TEMPLATES}, 'assets': {}}
    for a in assets:
        if only and a['id'] not in only:
            continue
        if a['kind'] == 'beard':
            pos_mh, uv, tris = beard_shell(base, groups, BEARDS[a['src']], None, None)
        else:
            d = os.path.join(HERE, 'mh', a['src'])
            nm = os.path.basename(a['src'])
            refs, scales = load_mhclo(os.path.join(d, nm + '.mhclo'))
            V, VT, F = load_obj(os.path.join(d, nm + '.obj'))
            assert len(refs) == len(V), (a['id'], len(refs), len(V))
            Vfit = fit_on_base(base_dm, refs, scales)
            pos_idx, uv, tris = split_uv(Vfit, VT, F)
            pos_mh = Vfit[pos_idx]
        rep = {}
        for n in TEMPLATES:
            M, t, info = xf[n]
            tpl = tpls[n]
            pw = transfer(pos_mh, a['kind'], base, tpl, M, t, info)
            Hi = tpl['Hinv']
            pl = (Hi[:3, :3] @ pw.T).T + Hi[:3, 3]
            targets = resample_targets(pw, tpl, a['kind'])
            od = os.path.join(out_root, a['id']); os.makedirs(od, exist_ok=True)
            json.dump(dict(id=a['id'], template=n, kind=a['kind'], pos=pl.round(6).ravel().tolist(),
                           uv=np.asarray(uv).round(5).ravel().tolist(), idx=np.asarray(tris).ravel().tolist(),
                           targets={k: v.round(6).ravel().tolist() for k, v in targets.items()}),
                      open(os.path.join(od, n + '.json'), 'w'))
            rep[n] = dict(verts=len(pl), targets=len(targets), bbox_head_local=[pl.min(0).round(4).tolist(), pl.max(0).round(4).tolist()])
        report['assets'][a['id']] = rep
        print(a['id'], {k: (v['verts'], v['targets']) for k, v in rep.items()}, flush=True)
    for n in TEMPLATES:
        print('xf', n, {k: round(v, 4) for k, v in xf[n][2].items() if isinstance(v, float)})
    json.dump(report, open(os.path.join(out_root, 'fit-report.json'), 'w'), indent=1, default=str)


if __name__ == '__main__':
    main()
