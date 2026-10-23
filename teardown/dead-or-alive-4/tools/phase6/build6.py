"""DOA4 Phase 6 batch builder: assemble one package window -> static GLB + SKINNED GLB.
Reuses phase-5 batch_build logic (decl parse, bounds-validated segment walk,
coverage-first strip pairing) and adds:
  - BLENDWEIGHT parsing (usage 1) per decl
  - ObjInfo bone palette per object (phase-5 G3 source)
  - skinned glTF export: Hie skeleton (local TRS from local matrices),
    JOINTS_0 from palette (blend decls) or own object node (rigid decls),
    WEIGHTS_0 from BLENDWEIGHT, inverseBindMatrices from Hie world matrices.
Per-character/package isolation: one window, one package, no shared state.
"""
import numpy as np, struct, json, sys
sys.path.insert(0, '/home/hatch/workspace/_doa4p2-scratch/p6')
ELEM_SIZE = {0: 12, 3: 12, 6: 12, 5: 8, 2: 4}
def u32(d, o): return struct.unpack('>I', d[o:o + 4])[0]

def parse_decls(d, g):
    decls = []
    for obj in g['objects']:
        og = obj['objgeo']['offset']; gd = og + obj['objgeo']['geodecl_off']
        gcnt = u32(d, gd + 0x14); gtab = u32(d, gd + 0x20)
        for i in range(gcnt):
            rec = gd + u32(d, gd + gtab + i * 4); nelem = u32(d, rec + 0x10)
            elems = [struct.unpack('>3I', d[rec + 0x30 + e * 12:rec + 0x30 + e * 12 + 12]) for e in range(nelem)]
            real = [(e[0], e[2] >> 16, (e[2] >> 8) & 0xFF) for e in elems if e[1] != 0xFFFFFFFF]
            decls.append(dict(decl_id=u32(d, rec + 0x08), obj=obj['index'], stream=u32(d, rec + 0x18), vtx=u32(d, rec + 0x14), idx=u32(d, rec + 0x0c), elems=real))
    return decls

def strides(dd):
    out = set()
    for bw in (8, 12):
        sizes = dict(ELEM_SIZE); sizes[1] = bw
        out.add(max(boff + sizes.get(u, 4) for (boff, u, ui) in dd['elems']))
    return sorted(out)

def validate(d, off, dd, st, lo, hi):
    nv = dd['vtx']
    if off < 0 or off + nv * st > len(d): return 0.0
    raw = np.frombuffer(d[off:off + nv * st], dtype='>f4').astype(np.float32)
    A = raw.reshape(nv, st // 4)
    P = A[:, :3].astype(np.float64)
    if not np.isfinite(P).all(): return 0.0
    inside = ((P >= lo - 0.02) & (P <= hi + 0.02)).all(axis=1).mean()
    if inside < 0.99: return float(inside)
    if st > 12:
        N = A[:, 3:6].astype(np.float64)
        nl = np.sqrt((N ** 2).sum(axis=1))
        return float(min(inside, (np.abs(nl - 1) < 0.06).mean()))
    return float(inside)

def validate_bw(d, off, dd, st, pal):
    """Blend decls: BW columns (per stride hypothesis) must equal the ObjInfo
    palette count (phase-5 proven invariant) and rows must be weights in
    [0,1] summing to 1. Returns True/False. Non-blend decls pass."""
    bw_elems = [(boff, u) for (boff, u, ui) in dd['elems'] if u == 1]
    if not bw_elems: return True
    boff = bw_elems[0][0]
    cols = (st - boff) // 4
    if pal and cols != len(pal): return False
    if cols < 1 or cols > 3: return False
    nv = dd['vtx']
    if off + nv * st > len(d): return False
    raw = np.frombuffer(d[off:off + nv * st], dtype='>f4').astype(np.float32).reshape(nv, st // 4)
    bw = raw[:, boff // 4:boff // 4 + cols].astype(np.float64)
    if not np.isfinite(bw).all(): return False
    good = ((bw >= -0.001) & (bw <= 1.001)).all(axis=1) & (np.abs(bw.sum(axis=1) - 1) < 0.01)
    return good.mean() >= 0.99

def find_segments(d, g, decls, pals):
    """Walk-first segment location (phase-4 set layout: segments in decl order,
    slot = align(vtx*stride, 0x1000)); full aligned scan as fallback per decl."""
    bnds = {}
    for obj in g['objects']:
        b = obj['objinfo']; c = np.array(b['bounds_center']); e = np.array(b['bounds_extents'])
        bnds[obj['index']] = (c - e, c + e)
    def ok(dd, off, st):
        lo, hi = bnds[dd['obj']]
        return validate(d, off, dd, st, lo, hi) >= 0.995 and validate_bw(d, off, dd, st, pals[dd['obj']])
    def scan(dd):
        for off in range(0x8000, len(d), 0x1000):
            for st in strides(dd):
                if ok(dd, off, st): return (off, st)
        return None
    seg = {}
    prev = None  # (off, st, vtx) of previous decl's segment
    for dd in sorted(decls, key=lambda x: x['decl_id']):
        got = None
        if prev is not None:
            slot = (prev[2] * prev[1] + 0xFFF) & ~0xFFF
            cand = prev[0] + slot
            for st in strides(dd):
                if ok(dd, cand, st): got = (cand, st); break
        if got is None:
            got = scan(dd)
        if got is not None:
            seg[dd['decl_id']] = got
            prev = (got[0], got[1], dd['vtx'])
    return seg

def strip_tris(s, nv):
    tris = []; run = []
    for v in s:
        if v == 0xFFFF:
            for i in range(len(run) - 2):
                a, b, c = run[i], run[i + 1], run[i + 2]
                if len({a, b, c}) == 3 and max(a, b, c) < nv: tris.append((a, b, c) if i % 2 == 0 else (a, c, b))
            run = []
        else: run.append(int(v))
    for i in range(len(run) - 2):
        a, b, c = run[i], run[i + 1], run[i + 2]
        if len({a, b, c}) == 3 and max(a, b, c) < nv: tris.append((a, b, c) if i % 2 == 0 else (a, c, b))
    return tris

def seq_tris(idx, nv):
    tris = []; cnt = 0; i = 0
    while cnt + 2 < idx and i + 2 < nv:
        tris.append((i, i + 1, i + 2)); i += 3; cnt += 4
    return tris

def palette(d, g, oi):
    off = g['objects'][oi]['objinfo']['offset']; cnt = u32(d, off + 0x3c)
    if cnt == 0: return []
    return list(struct.unpack(f'>{cnt}H', d[off + 0x90:off + 0x90 + 2 * cnt]))

def parse_seg(d, dd, off, st):
    nv = dd['vtx']
    raw = np.frombuffer(d[off:off + nv * st], dtype='>f4').astype(np.float32).reshape(nv, st // 4)
    out = {}
    elems = sorted(dd['elems'])
    for k, (boff, usage, uidx) in enumerate(elems):
        fo = boff // 4
        nxt = elems[k + 1][0] if k + 1 < len(elems) else st
        ncomp = (nxt - boff) // 4
        if usage == 0: out['pos'] = raw[:, fo:fo + 3].astype(np.float64)
        elif usage == 3: out['nrm'] = raw[:, fo:fo + 3].astype(np.float32)
        elif usage == 5: out[f'uv{uidx}'] = raw[:, fo:fo + 2].astype(np.float32)
        elif usage == 1: out['bw'] = raw[:, fo:fo + min(3, ncomp)].astype(np.float32)
    return out

# ---------- glTF skinned writer ----------
def mat_to_trs(M):
    """M: 4x4 column-convention (numpy, M @ v). Returns (t, quat xyzw, s)."""
    t = M[:3, 3].copy(); R = M[:3, :3].copy()
    s = np.linalg.norm(R, axis=0); R = R / s
    # matrix -> quaternion (standard)
    tr = np.trace(R)
    if tr > 0:
        S = np.sqrt(tr + 1.0) * 2; q = np.array([(R[2,1]-R[1,2])/S, (R[0,2]-R[2,0])/S, (R[1,0]-R[0,1])/S, 0.25*S])
    elif R[0,0] > R[1,1] and R[0,0] > R[2,2]:
        S = np.sqrt(1.0 + R[0,0] - R[1,1] - R[2,2]) * 2; q = np.array([0.25*S, (R[0,1]+R[1,0])/S, (R[0,2]+R[2,0])/S, (R[2,1]-R[1,2])/S])
    elif R[1,1] > R[2,2]:
        S = np.sqrt(1.0 + R[1,1] - R[0,0] - R[2,2]) * 2; q = np.array([(R[0,1]+R[1,0])/S, 0.25*S, (R[1,2]+R[2,1])/S, (R[0,2]-R[2,0])/S])
    else:
        S = np.sqrt(1.0 + R[2,2] - R[0,0] - R[1,1]) * 2; q = np.array([(R[0,2]+R[2,0])/S, (R[1,2]+R[2,1])/S, 0.25*S, (R[1,0]-R[0,1])/S])
    q = q / np.linalg.norm(q)
    return t.tolist(), [float(q[0]), float(q[1]), float(q[2]), float(q[3])], s.tolist()

def write_glb_skinned(path, meshes, g, matmap=None):
    """meshes: (name, P, N, UV, T, obj, joints(nv,4)u16, weights(nv,4)f32)
    matmap: optional {mesh_name: png_bytes} -> baseColor texture materials."""
    binparts = []; views = []; accs = []
    def add_view(b, target):
        off = sum(len(p) for p in binparts); pad = (4 - len(b) % 4) % 4
        binparts.append(b + b'\x00' * pad)
        vv = {'buffer': 0, 'byteOffset': off, 'byteLength': len(b)}
        if target: vv['target'] = target
        views.append(vv)
        return len(views) - 1
    def add_acc(view, comp, count, typ, mn=None, mx=None):
        a = {'bufferView': view, 'componentType': comp, 'count': count, 'type': typ}
        if mn is not None: a['min'] = mn
        if mx is not None: a['max'] = mx
        accs.append(a); return len(accs) - 1
    gltf_meshes = []; mesh_nodes = []
    for (name, P, N, UV, T, oi, J, Wt) in meshes:
        pos32 = P.astype(np.float32)
        pv = add_view(pos32.tobytes(), 34962)
        pa = add_acc(pv, 5126, len(pos32), 'VEC3', pos32.min(axis=0).tolist(), pos32.max(axis=0).tolist())
        prim = {'attributes': {'POSITION': pa}}
        if N is not None:
            nv_ = add_view(N.astype(np.float32).tobytes(), 34962)
            prim['attributes']['NORMAL'] = add_acc(nv_, 5126, len(N), 'VEC3')
        if UV is not None:
            uvv = add_view(UV.astype(np.float32).tobytes(), 34962)
            prim['attributes']['TEXCOORD_0'] = add_acc(uvv, 5126, len(UV), 'VEC2')
        jv = add_view(J.astype(np.uint16).tobytes(), 34962)
        prim['attributes']['JOINTS_0'] = add_acc(jv, 5123, len(J), 'VEC4')
        wv = add_view(Wt.astype(np.float32).tobytes(), 34962)
        prim['attributes']['WEIGHTS_0'] = add_acc(wv, 5126, len(Wt), 'VEC4')
        idx32 = T.reshape(-1).astype(np.uint32)
        iv = add_view(idx32.tobytes(), 34963)
        prim['indices'] = add_acc(iv, 5125, len(idx32), 'SCALAR'); prim['mode'] = 4
        gltf_meshes.append({'name': name, 'primitives': [prim]})
        mesh_nodes.append(len(gltf_meshes) - 1)
    # skeleton nodes from Hie locals (row-vector -> column conv = transpose)
    nj = g['object_count']
    children = {k: [] for k in range(nj)}; roots = []
    for o in g['objects']:
        p = o['hie_node']['parent']
        if p < 0 or p >= nj or p == o['index']: roots.append(o['index'])
        else: children[p].append(o['index'])
    joint_nodes = []
    for o in g['objects']:
        L = np.array(o['hie_node']['matrix'], dtype=np.float64)  # row-major, row-vector
        M = L.T  # column convention
        t, q, s = mat_to_trs(M)
        node = {'name': f"node{o['index']}", 'translation': t, 'rotation': q, 'scale': s}
        if children[o['index']]: node['children'] = [len(gltf_meshes) + c for c in children[o['index']]]
        joint_nodes.append(node)
    # inverse bind matrices from world matrices
    ibm = np.zeros((nj, 4, 4), dtype=np.float64)
    for o in g['objects']:
        W = np.array(o['world_matrix'], dtype=np.float64)  # row-vector world
        ibm[o['index']] = np.linalg.inv(W.T)
    ibm_bytes = ibm.astype(np.float32).tobytes()  # column-major order needed: transpose each
    ibm_cm = np.ascontiguousarray(ibm.transpose(0, 2, 1)).astype(np.float32).tobytes()
    ibv = add_view(ibm_cm, None); views[-1].pop('target', None)
    iba = add_acc(ibv, 5126, nj, 'MAT4')
    images = []; textures = []; materials = []
    if matmap:
        img_idx = {}
        for name, val in matmap.items():
            png, blend = val if isinstance(val, tuple) else (val, False)
            if png not in img_idx:
                iv = add_view(png, None)
                images.append({'bufferView': iv, 'mimeType': 'image/png', 'name': name})
                textures.append({'source': len(images) - 1})
                img_idx[png] = len(textures) - 1
            mat = {'name': f'mat-{name}', 'pbrMetallicRoughness':
                   {'baseColorTexture': {'index': img_idx[png]}, 'metallicFactor': 0.0, 'roughnessFactor': 0.9},
                   'doubleSided': True}
            if blend: mat['alphaMode'] = 'BLEND'
            materials.append(mat)
            mi = len(materials) - 1
            for gm in gltf_meshes:
                if gm['name'] == name: gm['primitives'][0]['material'] = mi
    nodes = []
    for i, mn in enumerate(mesh_nodes):
        nodes.append({'mesh': mn, 'name': meshes[i][0], 'skin': 0})
    nodes.extend(joint_nodes)
    gltf = {'asset': {'version': '2.0', 'generator': 'doa4-phase6-skinned'},
            'scene': 0, 'scenes': [{'nodes': list(range(len(mesh_nodes))) + [len(mesh_nodes) + r for r in roots]}],
            'nodes': nodes, 'meshes': gltf_meshes,
            'skins': [{'joints': [len(mesh_nodes) + k for k in range(nj)], 'inverseBindMatrices': iba,
                       'skeleton': len(mesh_nodes) + roots[0]}],
            'buffers': [{'byteLength': sum(len(p) for p in binparts)}], 'bufferViews': views, 'accessors': accs}
    if images:
        gltf['images'] = images; gltf['textures'] = textures; gltf['materials'] = materials
        gltf['samplers'] = [{'wrapS': 10497, 'wrapT': 10497, 'magFilter': 9729, 'minFilter': 9987}]
    blob = b''.join(binparts)
    js = json.dumps(gltf).encode(); js += b' ' * ((4 - len(js) % 4) % 4)
    out = struct.pack('<4sII', b'glTF', 2, 12 + 8 + len(js) + 8 + len(blob))
    out += struct.pack('<II', len(js), 0x4E4F534A) + js
    out += struct.pack('<II', len(blob), 0x004E4942) + blob
    open(path, 'wb').write(out)
    print('wrote', path, len(out), 'bytes')

def build(pkgfile, graphfile, outglb, tag, matmap=None):
    d = open(pkgfile, 'rb').read()
    g = json.load(open(graphfile))
    decls = parse_decls(d, g)
    pals = {oi: palette(d, g, oi) for oi in range(g['object_count'])}
    seg = find_segments(d, g, decls, pals)
    print(f'[{tag}] segments {len(seg)}/{len(decls)}', flush=True)
    json.dump({str(k): v for k, v in seg.items()}, open(f'{tag}_segmap.json', 'w'))
    pages = []
    for off in range(0, len(d) - 0x2000, 0x1000):
        v = np.frombuffer(d[off:off + 512], dtype='>u2').astype(int)
        if ((v < 6000) | (v == 0xFFFF)).all() and v.max() > 50 and (v < 10).sum() > 3:
            pages.append(off)
    print(f'[{tag}] index-like pages {len(pages)}', flush=True)
    meshes = []; report = []
    for dd in sorted(decls, key=lambda x: x['decl_id']):
        did = dd['decl_id']
        if did not in seg:
            report.append(f'decl{did} obj{dd["obj"]}: NO SEGMENT [poor]'); continue
        off, st = seg[did]
        s = parse_seg(d, dd, off, st); P = s['pos']
        if dd['stream'] == 3:
            tris = seq_tris(dd['idx'], dd['vtx']); how = 'seq'; qual = 'clean'
        else:
            diag = np.linalg.norm(P.max(axis=0) - P.min(axis=0))
            cands = []
            for po in pages:
                full = np.frombuffer(d[po:po + min(dd['idx'] * 2, 0x40000)], dtype='>u2').astype(np.int64)
                if len(full) < dd['idx']: continue
                cand = full[:dd['idx']]
                sv = cand[cand != 0xFFFF]
                if not len(sv) or int(sv.max()) >= dd['vtx']: continue
                vals = [int(v) for v in cand if v != 0xFFFF]
                if vals == list(range(len(vals))): continue
                cov = len(set(sv.tolist())) / dd['vtx']
                if cov < 0.70: continue
                cands.append((cov, po, cand))
            cands.sort(key=lambda c: -c[0]); cands = cands[:5]
            best = None
            for cov, po, cand in cands:
                tr = strip_tris(cand, dd['vtx'])
                if len(tr) < 3: continue
                T = P[np.array(tr)]
                e = (np.linalg.norm(T[:, 0] - T[:, 1], axis=1) + np.linalg.norm(T[:, 1] - T[:, 2], axis=1) + np.linalg.norm(T[:, 2] - T[:, 0], axis=1)) / 3
                sc = float(e.mean() / diag)
                key = (cov, -sc)
                if best is None or key > best[0]: best = (key, po, tr, cov, sc)
            if best is None:
                report.append(f'decl{did} obj{dd["obj"]} s{dd["stream"]}: NO STRIP [poor]'); continue
            tris = best[2]; how = f'page {best[1]:#x} cov {best[3]:.2f} score {best[4]:.3f}'
            qual = 'clean' if best[4] < 0.10 else ('moderate' if best[4] < 0.25 else 'poor')
        tris = np.array(tris, dtype=np.int64)
        if 'nrm' in s and len(tris):
            N = s['nrm'].astype(np.float64)
            v0, v1, v2 = P[tris[:, 0]], P[tris[:, 1]], P[tris[:, 2]]
            fn = np.cross(v1 - v0, v2 - v0); vn = N[tris[:, 0]] + N[tris[:, 1]] + N[tris[:, 2]]
            bad = (fn * vn).sum(axis=1) < 0
            tris[bad] = tris[bad][:, [0, 2, 1]]
        nv = dd['vtx']
        J = np.zeros((nv, 4), dtype=np.uint16); Wt = np.zeros((nv, 4), dtype=np.float32)
        if 'bw' in s and pals[dd['obj']]:
            pal = pals[dd['obj']]; bw = s['bw'].astype(np.float64)
            rs = bw.sum(axis=1, keepdims=True)
            ok = (rs[:, 0] > 0.5)
            bw = bw / np.maximum(rs, 1e-9)
            for k in range(bw.shape[1]):
                J[:, k] = pal[k]; Wt[:, k] = bw[:, k]
            if not ok.all():  # degenerate BW rows -> rigid own-node fallback, flagged
                J[~ok] = 0; Wt[~ok] = 0; J[~ok, 0] = dd['obj']; Wt[~ok, 0] = 1.0
                report.append(f'decl{did} obj{dd["obj"]}: BW degenerate rows {int((~ok).sum())}/{nv} -> rigid fallback')
        else:
            J[:, 0] = dd['obj']; Wt[:, 0] = 1.0
        meshes.append((f"obj{dd['obj']}_decl{did}", P, s.get('nrm'), s.get('uv0'), tris, dd['obj'], J, Wt))
        report.append(f'decl{did} obj{dd["obj"]} s{dd["stream"]}: {len(tris)} tris {how} [{qual}]')
    for r in report: print(f'[{tag}] {r}', flush=True)
    print(f'[{tag}] meshes {len(meshes)}', flush=True)
    write_glb_skinned(outglb, meshes, g, matmap=matmap)
    from collections import Counter
    q = Counter(r.split('[')[-1].rstrip(']') for r in report)
    print(f'[{tag}] QUALITY {dict(q)}', flush=True)
    return report

if __name__ == '__main__':
    pkgfile, graphfile, outglb, tag = sys.argv[1:5]
    build(pkgfile, graphfile, outglb, tag)
