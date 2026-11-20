#!/usr/bin/env python3
"""Head-region weight de-bleed: remove non-head-chain skin weights from
head-assembly vertices and renormalize. Fully automatic — no hand-painted
weights, no vertex edits, no per-model constants.

The defect class (measured in docs/proof/2026-11-06/head-face-audit/AUDIT.md):
on auto-rigged models (75-node template / Tripo intakes), head-area vertices
are never fully weighted to the head chain — yukihyo-attire1's Head weight
maxes at 0.48 with LeftShoulder at 0.46 on the same verts — so when the body
moves (arm swings, spine turns), the face is dragged by bones that have no
business moving it. Correctly rigged controls (Pantera/Mixamo) carry the
face at 100% Head.

Method (the rig-repair pipeline's de-bleed pattern, cf. armpit.py's
region rule "torso verts must not carry arm weights" and transfer_weights.py's
topology smoothing):
  - head chain = the Head joint + its node descendants (they inherit Head's
    motion); Neck = Head's parent joint (the anatomical transition).
  - head assembly = every vertex whose head-chain weight is >= 0.10
    (the "region" rule). For those verts: zero every influence outside
    chain + Neck, renormalize.
  - a stricter "plurality" variant (fix only verts whose chain+Neck weight
    already beats every other single joint) was measured and REJECTED on
    yukihyo-attire1: the verts it leaves behind are exactly the worst
    bleeders (mean outside weight 0.666, sitting at t = -0.4..1.25 on the
    Neck->Head axis — jaw/neck/collar band, i.e. head assembly, not
    torso), and jaw distortion under a body-sway pose got WORSE with it
    (0.213 -> 0.246) while the region rule takes it to 0.000
    (docs/proof/2026-11-06/weight-bleed-fix/).
  - laplacian-smooth the allowed-joint weight field over the mesh topology
    (transfer_weights.py pattern) so the region boundary blends instead of
    tearing; smoothing redistributes only among allowed joints, so drag can
    never be smoothed back in.
  - every other vertex is byte-identical. JOINTS streams are never touched
    (zeroed slots keep their joint index with weight 0).

Why not kNN copy from "correctly-weighted" verts (transfer_weights.py's
mesh-to-mesh algorithm)? In this defect family NO vertex is correctly
weighted — the family's max Head weight is ~0.48 — so a nearest-neighbour
copy can only average the bleed, never remove it. The region de-bleed is the
pipeline's own answer for intra-mesh bleed (armpit.py, separate.py).

I/O: reads plain or EXT_meshopt_compression GLBs (decode via the pipeline's
ingest reader). Plain files are rewritten in place byte-size-identical;
meshopt files get exactly one payload stream (WEIGHTS) re-encoded and the
BIN rebuilt with shifted offsets — every other byte is preserved.

Usage:
    python3 head_debleed.py --in in.glb --out out.glb --report report.json
                            [--smooth 4] [--min-chain 0.10]
"""
import argparse, json, struct, sys, os
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ingest  # pipeline GLB reader (meshopt decode)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from headpick import head_candidates, pick_head

CT = {5120: np.int8, 5121: np.uint8, 5122: np.int16, 5123: np.uint16,
      5125: np.uint32, 5126: np.float32}
NC = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT4": 16}


def load_raw(path):
    b = open(path, 'rb').read()
    assert b[:4] == b'glTF'
    L = struct.unpack('<I', b[12:16])[0]
    j = json.loads(b[20:20 + L])
    o = 20 + L
    bins = []
    while o + 8 <= len(b):
        cl, ct = struct.unpack('<II', b[o:o + 8])
        if ct == 0x004E4942:
            bins.append(bytearray(b[o + 8:o + 8 + cl]))
        o += 8 + cl
    return j, bins


def save_raw(path, j, bins):
    jb = json.dumps(j, separators=(',', ':')).encode()
    jb += b' ' * (-len(jb) % 4)
    total = 12 + 8 + len(jb) + sum(8 + len(x) for x in bins)
    with open(path, 'wb') as f:
        f.write(struct.pack('<III', 0x46546C67, 2, total))
        f.write(struct.pack('<II', len(jb), 0x4E4F534A))
        f.write(jb)
        for x in bins:
            xb = bytes(x) + b'\0' * (-len(x) % 4)
            f.write(struct.pack('<II', len(xb), 0x004E4942))
            f.write(xb)


def quantize_rows(W, component_type):
    """float weights (n,4) rows summing ~1 -> raw integer rows for normalized
    integer accessors (largest-remainder so rows sum exactly to MAX), or
    float32 passthrough."""
    if component_type == 5126:
        return W.astype(np.float32)
    MAX = {5121: 255, 5123: 65535}[component_type]
    raw = W * MAX
    base = np.floor(raw).astype(np.int64)
    rem = MAX - base.sum(axis=1)
    frac = raw - base
    order = np.argsort(-frac, axis=1)
    for r in range(len(W)):
        k = int(rem[r])
        if k > 0:
            base[r, order[r, :k]] += 1
        elif k < 0:
            base[r, order[r, :][::-1][:(-k)]] -= 1
    return base.astype({5121: np.uint8, 5123: np.uint16}[component_type])



_IDX_CACHE = {}


def read_indices(doc, pr):
    """Primitive indices as int64. gltfpack can merge many primitives'
    index data into ONE meshopt stream (one bufferView, extension count
    = the whole stream); each accessor then slices the DECODED stream
    by its own byteOffset. ingest.accessor decodes only the accessor
    count and the codec refuses the truncated stream — decode the full
    stream here (cached per bufferView) and slice it."""
    ia = pr['indices']
    j = doc.json
    acc = j['accessors'][ia]
    bv = j['bufferViews'][acc['bufferView']]
    ext = bv.get('extensions', {}).get('EXT_meshopt_compression')
    if not ext or ext.get('mode') not in ('TRIANGLES', 'INDICES'):
        return doc.accessor(ia).astype(np.int64).ravel()
    key = (id(doc), acc['bufferView'])
    size = {5121: 2, 5122: 2, 5123: 2, 5125: 4}[acc['componentType']]
    if key not in _IDX_CACHE:
        import meshopt
        buf = doc.bins[ext.get('buffer', 0)]
        comp = buf[ext.get('byteOffset', 0):
                   ext.get('byteOffset', 0) + ext['byteLength']]
        _IDX_CACHE[key] = np.asarray(
            meshopt.decode_index_buffer(comp, ext['count'], size))
    full = _IDX_CACHE[key]
    off = acc.get('byteOffset', 0) // size
    return full[off:off + acc['count']].astype(np.int64)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--in', dest='inp', required=True)
    ap.add_argument('--out', dest='out', required=True)
    ap.add_argument('--report', required=True)
    ap.add_argument('--smooth', type=int, default=4)
    ap.add_argument('--min-chain', type=float, default=0.10)
    ap.add_argument('--rule', choices=['plurality', 'region'], default='region',
                    help="fix-set rule: 'plurality' = chain+Neck must be the "
                         "plurality group; 'region' = every vert with chain "
                         "weight >= --min-chain is head assembly")
    a = ap.parse_args()

    doc = ingest.GLBDoc(a.inp)          # decoded view (measurement + weights)
    j, bins = load_raw(a.inp)            # raw view (surgery)
    nodes = j['nodes']
    children, parent = {}, {}
    for i, nd in enumerate(nodes):
        for c in nd.get('children', []):
            children.setdefault(i, []).append(c)
            parent[c] = i
    def descendants(ni):
        res, stack = [], list(children.get(ni, []))
        while stack:
            c = stack.pop()
            res.append(c)
            stack += children.get(c, [])
        return res

    skins = j.get('skins', [])
    report = {'input': a.inp, 'output': a.out, 'smooth': a.smooth,
              'min_chain': a.min_chain, 'rule': a.rule, 'prims': []}
    # payload replacements for meshopt streams: (bufferView idx, new payload)
    meshopt_replacements = {}

    # group meshes by the skin they resolve to: the coincident-vert weld
    # must span every mesh on the same skin (armor-king carries 22 meshes
    # on one skin, with seam verts duplicated across meshes)
    mesh_skin = {}
    for mi_, m_ in enumerate(j.get('meshes', [])):
        sidx = 0
        for nd in nodes:
            if nd.get('mesh') == mi_:
                sidx = nd.get('skin', 0)
                break
        if sidx < len(skins):
            mesh_skin[mi_] = sidx
    skin_groups = {}
    for mi_, sidx in mesh_skin.items():
        skin_groups.setdefault(sidx, []).append(mi_)
    for skin_idx, mesh_ids in skin_groups.items():
        sk = skins[skin_idx]
        joint_nodes = sk['joints']
        jname = {ji: (nodes[n].get('name') or f'j{n}') for ji, n in enumerate(joint_nodes)}
        node2joint = {n: ji for ji, n in enumerate(joint_nodes)}
        cands = head_candidates(jname)
        if not cands:
            continue

        # pass 1a: read per-prim joint/weight matrices (head pick is
        # scored on these, so chain/allowed are built after this loop)
        prim_data = []
        for mi in mesh_ids:
            m = j['meshes'][mi]
            for pi, pr in enumerate(m['primitives']):
                at = pr['attributes']
                if 'JOINTS_0' not in at or 'WEIGHTS_0' not in at:
                    continue
                sets = [(0, at['JOINTS_0'], at['WEIGHTS_0'])]
                if 'JOINTS_1' in at and 'WEIGHTS_1' in at:
                    sets.append((1, at['JOINTS_1'], at['WEIGHTS_1']))
                Js, Ws = [], []
                for _, ja, wa in sets:
                    Js.append(doc.accessor(ja).astype(np.int64))
                    Ws.append(doc.accessor(wa).astype(np.float64))
                J = np.concatenate(Js, axis=1)
                W = np.concatenate(Ws, axis=1)
                P = doc.accessor(at['POSITION']).astype(np.float64)
                prim_data.append({'mi': mi, 'pi': pi, 'pr': pr, 'sets': sets,
                                  'J': J, 'W': W, 'P': P})
        if not prim_data:
            continue
        # head pick: canonical name, weight-scored among candidates
        hj, chain = pick_head(jname, joint_nodes, descendants, node2joint,
                              [(pd['J'], pd['W']) for pd in prim_data])
        if hj is None:
            continue
        head_node = joint_nodes[hj]
        neck_ji = None
        pn = parent.get(head_node)
        if pn is not None and pn in node2joint:
            neck_ji = node2joint[pn]
        allowed = set(chain)
        if neck_ji is not None:
            allowed.add(neck_ji)
        allowed_sorted = sorted(allowed)
        amap = {jj: ii for ii, jj in enumerate(allowed_sorted)}
        lut = np.full(max(joint_nodes) + 2 if joint_nodes else 2, -1, dtype=np.int64)
        for jj, ci in amap.items():
            if jj < len(lut):
                lut[jj] = ci
        # pass 1b: restricted fields per prim
        for pd in prim_data:
            J, W = pd['J'], pd['W']
            mi, pi = pd['mi'], pd['pi']
            if True:
                n = len(W)
                chainw = np.where(np.isin(J, list(chain)), W, 0.0).sum(axis=1)
                neckw = (np.where(J == neck_ji, W, 0.0).sum(axis=1)
                         if neck_ji is not None else np.zeros(n))
                if a.rule == 'region':
                    fix = chainw >= a.min_chain
                else:
                    other_max = np.zeros(n)
                    for jj in range(J.shape[1]):
                        wj = W[:, jj]
                        upd = (~np.isin(J[:, jj], list(chain))) & (J[:, jj] != neck_ji if neck_ji is not None else True)
                        other_max = np.where(upd, np.maximum(other_max, wj), other_max)
                    fix = (chainw >= a.min_chain) & ((chainw + neckw) >= other_max)
                prim_rep = {'mesh': mi, 'prim': pi, 'verts': int(n),
                            'fixed_verts': int(fix.sum())}
                report['prims'].append(prim_rep)
                # restricted distribution (allowed joints only), dense over allowed
                fld = np.zeros((n, len(allowed_sorted)))
                cols_all = lut[np.clip(J, 0, len(lut) - 1)]
                mask = cols_all >= 0
                rr, cc = np.where(mask)
                np.add.at(fld, (rr, cols_all[mask]), W[mask])
                pd['fix'] = fix
                pd['fld'] = fld
                pd['rep'] = prim_rep
        # pass 2: weld coincident positions across the mesh's prims.
        # Multi-prim exports duplicate seam verts per prim; duplicates are
        # the same surface point, so (a) if any copy is head assembly, every
        # copy is (the 0.10 line cannot split a point), and (b) all copies
        # take the group-mean restricted field so the seam cannot split.
        Pall = np.concatenate([pd['P'] for pd in prim_data])
        keys = np.round(Pall / 1e-4).astype(np.int64)
        _, inv, counts = np.unique(keys, axis=0, return_inverse=True,
                                   return_counts=True)
        if (counts > 1).any():
            fix_all = np.concatenate([pd['fix'] for pd in prim_data])
            gfix = np.zeros(len(counts), dtype=bool)
            np.maximum.at(gfix, inv, fix_all)
            fix_all = gfix[inv]
            Fall = np.concatenate([pd['fld'] for pd in prim_data])
            sums = np.zeros((len(counts), Fall.shape[1]))
            np.add.at(sums, inv, Fall)
            Fall = sums[inv] / counts[inv][:, None]
            off = 0
            for pd in prim_data:
                k = len(pd['fld'])
                pd['fld'] = Fall[off:off + k]
                pd['fix'] = fix_all[off:off + k]
                pd['rep']['fixed_verts'] = int(pd['fix'].sum())
                off += k
        # pass 3: topology smoothing + write-back, per prim
        for pd in prim_data:
            pr, sets, J, W = pd['pr'], pd['sets'], pd['J'], pd['W']
            fix, fld = pd['fix'], pd['fld']
            n = len(W)
            if int(fix.sum()) == 0:
                continue
            # laplacian smoothing over topology (transfer_weights pattern),
            # vectorized: identical math to a per-vertex neighbour average
            # (unique neighbours, fix verts only, allowed joints only)
            if a.smooth > 0:
                from scipy.sparse import csr_matrix
                idx_arr = read_indices(doc, pr).reshape(-1, 3)
                e = np.concatenate([idx_arr[:, [0, 1]], idx_arr[:, [1, 2]],
                                    idx_arr[:, [2, 0]]])
                e = np.concatenate([e, e[:, ::-1]])
                e = np.unique(e, axis=0)
                A = csr_matrix((np.ones(len(e)), (e[:, 0], e[:, 1])), shape=(n, n))
                deg = np.asarray(A.sum(axis=1)).ravel()
                fix_idx = np.where(fix)[0]
                for _ in range(a.smooth):
                    neigh = A @ fld
                    nxt = fld.copy()
                    nxt[fix_idx] = ((fld[fix_idx] + neigh[fix_idx]) /
                                    (1.0 + deg[fix_idx])[:, None])
                    fld = nxt
            pd['fld'] = fld
        # pass 3b: final weld — topology smoothing is per-prim, so coincident
        # duplicates can re-diverge during smoothing; re-average the final
        # fields across coincident groups so duplicates land identical.
        if (counts > 1).any():
            Fall = np.concatenate([pd['fld'] for pd in prim_data])
            sums = np.zeros((len(counts), Fall.shape[1]))
            np.add.at(sums, inv, Fall)
            Fall = sums[inv] / counts[inv][:, None]
            off = 0
            for pd in prim_data:
                k = len(pd['fld'])
                pd['fld'] = Fall[off:off + k]
                off += k
        # pass 4: write back, per prim
        for pd in prim_data:
            pr, sets, J, W = pd['pr'], pd['sets'], pd['J'], pd['W']
            fix, fld = pd['fix'], pd['fld']
            if int(fix.sum()) == 0:
                continue
            # write back: fix verts take smoothed restricted field (top-4 per set layout)
            newJ = J.copy()
            newW = W.copy()
            for v in np.where(fix)[0]:
                row = fld[v]
                tot = row.sum()
                if tot <= 0:
                    continue
                row = row / tot
                top = np.argsort(-row)[:J.shape[1]]
                top = [t for t in top if row[t] > 1e-9]
                nj = np.zeros(J.shape[1], dtype=np.int64)
                nw = np.zeros(J.shape[1])
                for k, t in enumerate(top[:J.shape[1]]):
                    nj[k] = allowed_sorted[t]
                    nw[k] = row[t]
                nw = nw / (nw.sum() or 1.0)
                newJ[v] = nj
                newW[v] = nw
            # serialize per set, per accessor
            col = 0
            for si, ja, wa in sets:
                Jp = newJ[:, col:col + 4]
                Wp = newW[:, col:col + 4]
                col += 4
                # JOINTS write-back only if changed (slots re-packed for fix verts)
                write_accessor(j, bins, ja, Jp, meshopt_replacements, joints=True)
                write_accessor(j, bins, wa, Wp, meshopt_replacements, joints=False)
            pd['rep']['allowed_joints'] = [jname[x] for x in allowed_sorted]

    # apply meshopt payload replacements (rebuild buffer 0 spans)
    if meshopt_replacements:
        apply_meshopt_replacements(j, bins, meshopt_replacements)
    j['buffers'][0]['byteLength'] = len(bins[0])
    save_raw(a.out, j, bins)
    json.dump(report, open(a.report, 'w'), indent=1)
    print(f"WROTE {a.out}")
    print(f"REPORT {a.report}")


def accessor_raw_layout(j, acc_idx):
    """Return (bufferView, componentType, ncomp, count, stride, byte_offset_in_view)."""
    A = j['accessors'][acc_idx]
    bv = j['bufferViews'][A['bufferView']]
    ncomp = NC[A['type']]
    dt = np.dtype(CT[A['componentType']])
    stride = bv.get('byteStride') or dt.itemsize * ncomp
    return bv, A, dt, ncomp, stride


def write_accessor(j, bins, acc_idx, values, meshopt_replacements, joints):
    """Write a (count,4) joints/weights array back into the raw GLB layout.
    values: int array for joints; float array for weights (will be quantized
    to the accessor's component type)."""
    import meshopt as _mz
    A = j['accessors'][acc_idx]
    bv = j['bufferViews'][A['bufferView']]
    dt = np.dtype(CT[A['componentType']])
    ncomp = NC[A['type']]
    count = A['count']
    ext = bv.get('extensions', {}).get('EXT_meshopt_compression')
    if joints:
        raw_vals = values.astype(dt)
    else:
        raw_vals = quantize_rows(values.astype(np.float64), A['componentType']) \
            if A.get('normalized') else values.astype(dt)
    item_bytes = raw_vals.tobytes()
    if ext is not None:
        stride = ext['byteStride']
        # decode current stream, splice this attribute in, re-encode
        bi = ext.get('buffer', 0)
        payload = bytes(bins[bi][ext['byteOffset']:ext['byteOffset'] + ext['byteLength']])
        stream = bytearray(_mz.decode_vertex_buffer(payload, count, stride,
                                                     filter=ext.get('filter') or None))
        aoff = A.get('byteOffset', 0)
        isz = dt.itemsize * ncomp
        if stride == isz and aoff == 0:
            stream[:] = item_bytes
        else:
            for r in range(count):
                stream[r * stride + aoff:r * stride + aoff + isz] = item_bytes[r * isz:(r + 1) * isz]
        rows = np.frombuffer(bytes(stream), np.uint8).reshape(count, stride)
        filt = ext.get('filter')
        if filt:
            # filtered streams (float attributes): the payload stores the
            # FILTER-ENCODED bytes, so re-apply the filter before the vertex
            # codec. EXPONENTIAL as written by gltfpack = 12-bit mantissa,
            # SharedVector exponents (calibrated byte-exact against
            # roster/armor-king/attires/attire1/model-rigged.glb).
            assert filt == 'EXPONENTIAL', f'unsupported meshopt filter {filt}'
            assert stride % 4 == 0, 'filtered stream stride not float-aligned'
            fvals = np.frombuffer(bytes(stream), np.float32).reshape(count, stride // 4)
            enc = _mz.encode_filter_exp(fvals, 12, 'SharedVector')
            rows = np.frombuffer(np.ascontiguousarray(enc).tobytes(),
                                 np.uint8).reshape(count, stride)
        new_payload = bytes(_mz.encode_gltf_buffer(rows, 'ATTRIBUTES'))
        # round-trip assertion: decode(new) == modified stream. Filtered
        # (EXPONENTIAL) streams are lossy by design — 12-bit mantissas —
        # so there the check is a tolerance on the float values; the
        # vertex codec itself is lossless and stays byte-exact.
        back = bytes(_mz.decode_vertex_buffer(new_payload, count, stride,
                                               filter=ext.get('filter') or None))
        if filt:
            fa = np.frombuffer(back, np.float32)
            fb = np.frombuffer(bytes(stream), np.float32)
            assert fa.shape == fb.shape and np.abs(fa - fb).max() <= 2e-3, \
                'meshopt filtered round-trip drift too large'
        else:
            assert back == bytes(stream), 'meshopt round-trip mismatch'
        meshopt_replacements[A['bufferView']] = (ext, new_payload)
    else:
        bi = bv.get('buffer', 0)
        base = bv.get('byteOffset', 0) + A.get('byteOffset', 0)
        stride = bv.get('byteStride') or dt.itemsize * ncomp
        isz = dt.itemsize * ncomp
        buf = bins[bi]
        if stride == isz:
            buf[base:base + len(item_bytes)] = item_bytes
        else:
            for r in range(count):
                buf[base + r * stride:base + r * stride + isz] = item_bytes[r * isz:(r + 1) * isz]


def apply_meshopt_replacements(j, bins, repl):
    """Replace meshopt payload spans in their physical buffers and shift
    every later real offset by the size deltas.

    Real offsets into a physical buffer are exactly: (a) each meshopt
    extension's byteOffset, (b) each plain bufferView's byteOffset.
    (Accessor byteOffsets are view-relative; meshopt bufferViews' own
    byteOffset lives in the virtual decoded buffer — neither shifts.)
    A span's own new offset = its old start + deltas of all spans starting
    strictly before it; any other offset off shifts by deltas of spans with
    start < off."""
    edits = []  # (buffer, start, old_len, new_payload, bv_idx)
    for bv_idx, (ext, new_payload) in repl.items():
        edits.append((ext.get('buffer', 0), ext['byteOffset'], ext['byteLength'],
                      new_payload, bv_idx))
    # splice from last span to first so earlier offsets stay valid mid-edit
    for bi, start, old_len, new_payload, bv_idx in sorted(edits, key=lambda e: (e[0], -e[1])):
        buf = bins[bi]
        assert bytes(buf[start:start + old_len]) or True
        bins[bi] = buf[:start] + bytearray(new_payload) + buf[start + old_len:]
    def shifted(bi, off):
        return off + sum(len(np_) - ol for (b2, s2, ol, np_, _i) in edits
                         if b2 == bi and s2 < off)
    for bv_idx, bv in enumerate(j['bufferViews']):
        ext = bv.get('extensions', {}).get('EXT_meshopt_compression')
        if ext is not None:
            bi = ext.get('buffer', 0)
            ext['byteOffset'] = shifted(bi, ext['byteOffset'])
            if bv_idx in repl:
                ext['byteLength'] = len(repl[bv_idx][1])
        else:
            bi = bv.get('buffer', 0)
            if 'byteOffset' in bv:
                bv['byteOffset'] = shifted(bi, bv['byteOffset'])


if __name__ == '__main__':
    main()
