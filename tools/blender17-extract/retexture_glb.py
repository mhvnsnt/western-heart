#!/usr/bin/env python3
"""Re-texture a GLB from a blender17-extract output folder.

  python3 retexture_glb.py <in.glb> <extract_dir> <out.glb> [--uvs] [--report r.json]

Fixes the BLENDER17-01 "material collapse": old extract.py looked each poly's
mat_nr up in the FILE-WIDE material list, so every exported part got the first
few file materials (e.g. "boots"/"eyes"). This tool matches every GLB triangle
back to its source face (nearest-vertex match after a fitted similarity
transform), then rebuilds primitives grouped by the source face's REAL
per-mesh material, with the textures extract.py now resolves via node trees.
--uvs also recovers TEXCOORD_0 from the matched source loops (for GLBs whose
UVs were dropped, e.g. a re-rig); otherwise existing UVs are kept.
No geometry is removed: every input triangle is written to the output.
"""
import json, os, struct, sys, itertools
import numpy as np
from scipy.spatial import cKDTree

CT = {5126: np.float32, 5125: np.uint32, 5123: np.uint16, 5121: np.uint8,
      5122: np.int16, 5120: np.int8}
NC = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4, 'MAT4': 16}


def read_glb(path):
    b = open(path, 'rb').read()
    jl = struct.unpack('<I', b[12:16])[0]
    j = json.loads(b[20:20 + jl])
    o = 20 + jl
    bl = struct.unpack('<I', b[o:o + 4])[0]
    return j, b[o + 8:o + 8 + bl]


def acc(j, binb, i):
    a = j['accessors'][i]
    bv = j['bufferViews'][a['bufferView']]
    n, dt = NC[a['type']], np.dtype(CT[a['componentType']])
    st = bv.get('byteStride', 0) or n * dt.itemsize
    o = bv.get('byteOffset', 0) + a.get('byteOffset', 0)
    raw = np.frombuffer(binb, np.uint8, (a['count'] - 1) * st + n * dt.itemsize, o)
    rows = np.lib.stride_tricks.as_strided(raw, (a['count'], n * dt.itemsize), (st, 1))
    return np.ascontiguousarray(rows).view(dt).reshape(a['count'], n), a


def parse_extract(d):
    """-> verts (N,3 blender), faces [(mesh, mat, [vi], [uv])], mtls."""
    V, F, mtls = [], [], {}
    for fn in sorted(os.listdir(d)):
        if fn.endswith('.mtl'):
            cur = None
            for line in open(os.path.join(d, fn)):
                p = line.split(None, 1)
                if not p:
                    continue
                if p[0] == 'newmtl':
                    cur = p[1].strip(); mtls.setdefault(cur, {})
                elif cur and len(p) > 1:
                    mtls[cur].setdefault(p[0], p[1].strip())
    for fn in sorted(os.listdir(d)):
        if not fn.endswith('.obj') or fn.startswith('WGT'):
            continue
        base, vt, mat = len(V), [], 'default'
        for line in open(os.path.join(d, fn)):
            if line.startswith('v '):
                V.append([float(x) for x in line.split()[1:4]])
            elif line.startswith('vt '):
                vt.append([float(x) for x in line.split()[1:3]])
            elif line.startswith('usemtl '):
                mat = line.split(None, 1)[1].strip()
            elif line.startswith('f '):
                vi, uv = [], []
                for c in line.split()[1:]:
                    s = c.split('/')
                    vi.append(base + int(s[0]) - 1)
                    uv.append(vt[int(s[1]) - 1] if len(s) > 1 and s[1] else [0, 0])
                F.append((fn[:-4], mat, vi, uv))
    return np.array(V, float), F, mtls


def rotations():
    out = []
    for perm in itertools.permutations(range(3)):
        for sg in itertools.product([1, -1], repeat=3):
            R = np.zeros((3, 3))
            for r, (c, s) in enumerate(zip(perm, sg)):
                R[r, c] = s
            if np.linalg.det(R) > 0:
                out.append(R)
    return out


def fit(src, dst_tree, dst, parts=()):
    """similarity x -> s*R@x+t mapping src (GLB) onto dst (source).
    parts: vertex-index arrays of the big source meshes; bbox candidates are
    tried against each (scene helpers like huge cubes skew a global bbox)."""
    rng = np.random.default_rng(0)
    smp = src[rng.choice(len(src), min(4000, len(src)), replace=False)]
    best = None
    sd = np.linalg.norm(np.ptp(dst, 0))
    targets = [dst] + [dst[p] for p in parts]
    for R in rotations():
        x = smp @ R.T
        cands = [(np.eye(3) * 1.0, np.zeros(3))] if np.allclose(R, np.eye(3)) else []
        for tg in targets:
            s = np.linalg.norm(np.ptp(tg, 0)) / max(np.linalg.norm(np.ptp(x, 0)), 1e-9)
            t = (tg.min(0) + tg.max(0)) / 2 - s * (x.min(0) + x.max(0)) / 2
            cands.append((s * R, t))
        for A_, t_ in cands:
            err = np.median(dst_tree.query(smp @ A_.T + t_)[0])
            if best is None or err < best[0]:
                best = (err, A_, t_)
    _, A, t = best
    for _ in range(15):  # ICP refine (Umeyama, inlier-trimmed)
        y = smp @ A.T + t
        dd, ii = dst_tree.query(y)
        keep = dd <= np.percentile(dd, 80)
        P, Q = smp[keep], dst[ii[keep]]
        mp, mq = P.mean(0), Q.mean(0)
        U, S, Vt = np.linalg.svd((Q - mq).T @ (P - mp))
        D = np.diag([1, 1, np.sign(np.linalg.det(U @ Vt))])
        R = U @ D @ Vt
        s = (S * np.diag(D)).sum() / ((P - mp) ** 2).sum()
        A, t = s * R, mq - s * R @ mp
    err = np.median(dst_tree.query(smp @ A.T + t)[0])
    return A, t, err / np.linalg.norm(np.ptp(smp @ A.T + t, 0))


def main():
    a = sys.argv[1:]
    want_uv = '--uvs' in a
    rep_path = a[a.index('--report') + 1] if '--report' in a else None
    a = [x for i, x in enumerate(a) if not x.startswith('--') and
         (i == 0 or a[i - 1] != '--report')]
    inp, xdir, outp = a[:3]
    j, binb = read_glb(inp)
    V, F, mtls = parse_extract(xdir)
    Vg = V[:, [0, 2, 1]] * [1, 1, -1]  # Blender Z-up -> glTF Y-up
    tree = cKDTree(Vg)
    v2f = [[] for _ in range(len(V))]
    for fi, f in enumerate(F):
        for v in f[2]:
            v2f[v].append(fi)
    allpos = np.concatenate([acc(j, binb, p['attributes']['POSITION'])[0]
                             for m in j['meshes'] for p in m['primitives']]).astype(float)
    by_mesh = {}
    for f in F:
        by_mesh.setdefault(f[0], set()).update(f[2])
    parts = [np.array(sorted(v)) for v in by_mesh.values() if len(v) >= 0.05 * len(V)]
    A, t, rel = fit(allpos, tree, Vg, parts)
    print(f"global fit residual (median, rel. to diag): {rel:.5f}")
    glob = (A, t, rel, tree, np.arange(len(V)), 'ALL')
    # source objects are stored in object-local space (object transforms are
    # not applied by the extractor), so also fit every GLB mesh against each
    # single source mesh and keep the best.
    sub = {}
    for nm, vs in by_mesh.items():
        if len(vs) >= 30:
            ids = np.array(sorted(vs)); sub[nm] = (cKDTree(Vg[ids]), ids)
    mesh_fit = {}
    for mi, m in enumerate(j['meshes']):
        mp = np.concatenate([acc(j, binb, p['attributes']['POSITION'])[0]
                             for p in m['primitives']]).astype(float)
        best = glob if len(j['meshes']) == 1 else (*fit(mp, tree, Vg, parts), tree, np.arange(len(V)), 'ALL')
        nm0 = m.get('name', '')
        names = [n for n in sub if n[:40] == nm0[:40]] or list(sub)
        # prefer a single source object when it fits as well: coincident
        # vertices of overlapping objects (suit over body) would otherwise
        # pull faces from the wrong object.
        for n in sorted(names, key=lambda n: -len(sub[n][1])):
                tr, ids = sub[n]
                A_, t_, r_ = fit(mp, tr, Vg[ids])
                if r_ < max(best[2], 2e-5) if best[5] == 'ALL' else r_ < best[2]:
                    best = (A_, t_, r_, tr, ids, n)
        print(f"  {nm0[:50]}: source={best[5][:50]} residual={best[2]:.5f}")
        if best[2] > 0.01:
            sys.exit(f"alignment too poor for {nm0} ({best[2]:.4f}) — refusing to re-texture")
        mesh_fit[mi] = best
    rel = max(b[2] for b in mesh_fit.values())

    out = {'bin': bytearray(), 'bufferViews': [], 'accessors': []}

    def add_view(data, target=None):
        while len(out['bin']) % 4:
            out['bin'] += b'\0'
        bv = {'buffer': 0, 'byteOffset': len(out['bin']), 'byteLength': len(data)}
        if target:
            bv['target'] = target
        out['bin'] += data
        out['bufferViews'].append(bv)
        return len(out['bufferViews']) - 1

    def add_acc(arr, ref=None, ctype=None, target=34962, normalized=False):
        arr = np.ascontiguousarray(arr)
        ctype = ctype or {np.float32: 5126, np.uint32: 5125, np.uint16: 5123,
                          np.uint8: 5121, np.int16: 5122, np.int8: 5120}[arr.dtype.type]
        n = 1 if arr.ndim == 1 else arr.shape[1]
        acc_ = {'bufferView': add_view(arr.tobytes(), target), 'componentType': ctype,
                'count': int(arr.shape[0]), 'type': {1: 'SCALAR', 2: 'VEC2', 3: 'VEC3',
                                                     4: 'VEC4', 16: 'MAT4'}[n]}
        if normalized:
            acc_['normalized'] = True
        if ref is None and ctype == 5126 and target == 34962 and n == 3:
            acc_['min'] = arr.min(0).tolist(); acc_['max'] = arr.max(0).tolist()
        out['accessors'].append(acc_)
        return len(out['accessors']) - 1

    # images / textures / materials
    images, textures, materials, img_idx, mat_idx = [], [], [], {}, {}

    def tex(rel):
        if rel not in img_idx:
            pth = os.path.join(xdir, rel)
            mime = 'image/png' if rel.lower().endswith('.png') else 'image/jpeg'
            images.append({'name': os.path.basename(rel), 'mimeType': mime,
                           'bufferView': add_view(open(pth, 'rb').read())})
            textures.append({'source': len(images) - 1, 'sampler': 0})
            img_idx[rel] = len(textures) - 1
        return {'index': img_idx[rel]}

    def material(name):
        if name not in mat_idx:
            m = mtls.get(name, {})
            kd = [float(x) for x in m.get('Kd', '0.8 0.8 0.8').split()]
            pbr = {'baseColorFactor': kd + [1.0], 'metallicFactor': 0.0,
                   'roughnessFactor': 0.8}
            mat = {'name': name, 'pbrMetallicRoughness': pbr, 'doubleSided': True}
            if m.get('map_Kd') and os.path.isfile(os.path.join(xdir, m['map_Kd'])):
                pbr['baseColorTexture'] = tex(m['map_Kd'])
                pbr['baseColorFactor'] = [1, 1, 1, 1]
            if m.get('map_Ke') and os.path.isfile(os.path.join(xdir, m['map_Ke'])):
                mat['emissiveTexture'] = tex(m['map_Ke']); mat['emissiveFactor'] = [1, 1, 1]
            if m.get('norm') and os.path.isfile(os.path.join(xdir, m['norm'])):
                mat['normalTexture'] = tex(m['norm'])
            materials.append(mat)
            mat_idx[name] = len(materials) - 1
        return mat_idx[name]

    report = {'fit_rel_residual': rel, 'meshes': {}}
    ntri_in = ntri_out = 0
    for mi, m in enumerate(j['meshes']):
        A, t, _r, mtree, ids, _n = mesh_fit[mi]
        prims = []
        for p in m['primitives']:
            attrs = {k: acc(j, binb, v) for k, v in p['attributes'].items()}
            pos = attrs['POSITION'][0].astype(float)
            idx = acc(j, binb, p['indices'])[0].reshape(-1).astype(np.int64) \
                if 'indices' in p else np.arange(len(pos))
            tris = idx.reshape(-1, 3)
            ntri_in += len(tris)
            d, nv = mtree.query(pos @ A.T + t)
            nv = ids[nv]
            # per triangle: source face sharing most matched vertices
            tri_face, tri_uv = [], []
            for tri in tris:
                cnt = {}
                for c in tri:
                    for fi in v2f[nv[c]]:
                        cnt[fi] = cnt.get(fi, 0) + 1
                fi = max(cnt, key=cnt.get) if cnt else v2f[nv[tri[0]]][0] if v2f[nv[tri[0]]] else 0
                f = F[fi]
                uvs = []
                for c in tri:
                    try:
                        k = f[2].index(nv[c])
                    except ValueError:
                        k = int(np.argmin(np.linalg.norm(Vg[f[2]] - (pos[c] @ A.T + t), axis=1)))
                    uvs.append((round(f[3][k][0], 6), round(1.0 - f[3][k][1], 6)))
                tri_face.append(fi); tri_uv.append(uvs)
            groups = {}
            for ti, fi in enumerate(tri_face):
                groups.setdefault(F[fi][1], []).append(ti)
            for mname, tlist in groups.items():
                corners = tris[tlist].reshape(-1)
                if want_uv or 'TEXCOORD_0' not in attrs:
                    keys = [(int(c), tri_uv[ti][k]) for ti in tlist for k, c in
                            enumerate(tris[ti])]
                else:
                    keys = [(int(c), None) for c in corners]
                uniq, remap = {}, []
                for key in keys:
                    if key not in uniq:
                        uniq[key] = len(uniq)
                    remap.append(uniq[key])
                src_v = np.array([k[0] for k in uniq], np.int64)
                na = {}
                for an, (arr, ai) in attrs.items():
                    if an == 'TEXCOORD_0' and (want_uv or keys[0][1] is not None):
                        continue
                    na[an] = add_acc(arr[src_v], ctype=ai['componentType'],
                                     normalized=ai.get('normalized', False))
                if want_uv or 'TEXCOORD_0' not in attrs:
                    na['TEXCOORD_0'] = add_acc(np.array([k[1] for k in uniq], np.float32))
                ii = np.array(remap, np.uint32)
                np_ = {'attributes': na, 'material': material(mname), 'mode': 4,
                       'indices': add_acc(ii, ctype=5125, target=34963)}
                prims.append(np_)
                ntri_out += len(tlist)
                report['meshes'].setdefault(m.get('name', '?'), {})[mname] = len(tlist)
        m['primitives'] = prims
    assert ntri_in == ntri_out, (ntri_in, ntri_out)
    # carry non-mesh accessors (skins IBMs, animations) over
    remap_acc = {}
    def carry(i):
        if i not in remap_acc:
            arr, ai = acc(j, binb, i)
            remap_acc[i] = add_acc(arr, ctype=ai['componentType'], target=None,
                                   normalized=ai.get('normalized', False))
            for k in ('min', 'max'):
                if k in ai:
                    out['accessors'][remap_acc[i]][k] = ai[k]
        return remap_acc[i]
    for s in j.get('skins', []):
        if 'inverseBindMatrices' in s:
            s['inverseBindMatrices'] = carry(s['inverseBindMatrices'])
    for an in j.get('animations', []):
        for sm in an['samplers']:
            sm['input'] = carry(sm['input']); sm['output'] = carry(sm['output'])
    j['accessors'], j['bufferViews'] = out['accessors'], out['bufferViews']
    j['materials'], j['images'], j['textures'] = materials, images, textures
    j['samplers'] = [{'magFilter': 9729, 'minFilter': 9987, 'wrapS': 10497, 'wrapT': 10497}]
    for k in ('extensionsUsed', 'extensionsRequired'):
        j.pop(k, None)  # input must be decoded (gltf-transform dequantize)
    j['buffers'] = [{'byteLength': len(out['bin'])}]
    j['asset']['generator'] = 'western-heart blend17-extract retexture_glb.py'
    js = json.dumps(j, separators=(',', ':')).encode()
    js += b' ' * (-len(js) % 4)
    bn = bytes(out['bin']) + b'\0' * (-len(out['bin']) % 4)
    with open(outp, 'wb') as fo:
        fo.write(struct.pack('<III', 0x46546C67, 2, 28 + len(js) + len(bn)))
        fo.write(struct.pack('<II', len(js), 0x4E4F534A) + js)
        fo.write(struct.pack('<II', len(bn), 0x004E4942) + bn)
    report['triangles'] = ntri_out
    report['materials'] = {m['name']: ('textured' if 'baseColorTexture' in m['pbrMetallicRoughness']
                                       else 'colour-only') for m in materials}
    print(json.dumps(report, indent=1))
    if rep_path:
        json.dump(report, open(rep_path, 'w'), indent=1)


if __name__ == '__main__':
    main()
