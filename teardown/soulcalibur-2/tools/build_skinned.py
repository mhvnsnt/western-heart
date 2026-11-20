#!/usr/bin/env python3
"""SCII phase-5: skinned GLB builder for one fighter VMX.
Pipeline (all steps evidence-based, no guessed data):
 1. Parse VMX (rec28 counts/src/dst, nodes, parts) — same layout as phase-4 decoder.
 2. Solve per-bone bind matrices from sections 0-2 (fixed 1/2/3-influence
    grouping; exact, residual ~1e-6, validated vs node file matrices).
 3. Segment section 3 by dynamic programming (group sizes 1..6, cost =
    prediction error under step-2 matrices + weight-sum constraint).
 4. Joint re-solve with all sections (section 3 on DP groups).
 5. Export GLB: geometry from dst (world/bind) stream, JOINTS_0/WEIGHTS_0
    per vertex (max 4 influences; 5-influence verts keep top-4 renormalized,
    counted in report), skeleton = one joint per bone, IBM = inverse(bind),
    joints flat under scene root with matrix = bind (glTF-valid).
    Rigid parts included placed (as phase-4 _placed); sheet parts excluded.
Usage: build_skinned.py <bundle.bin> <vmx_off> <out.glb> <report.json>"""
import struct, sys, json, io, math
import numpy as np
from functools import lru_cache

def parse(bundle_path, V):
    d = open(bundle_path, 'rb').read()
    def u32(o): return struct.unpack_from('<I', d, V + o)[0]
    def u16(o): return struct.unpack_from('<H', d, V + o)[0]
    assert d[V:V + 4] == b'VMX.'
    b28 = u32(0x38)
    r28 = struct.unpack_from('<7I', d, V + b28)
    counts = list(r28[0:4]); src = r28[4]; dst = r28[5]
    NB = u32(0x24); NN = u16(0x0A)
    nodeM = {}
    nodes = []
    for i in range(NN):
        base = NB + i * 400; dw0 = u32(base)
        M = list(struct.unpack_from('<16f', d, V + base + 0x10))
        nodeM[(dw0 >> 8) & 0xFF] = M
        Mw = list(M); Mw[12] *= 0.1; Mw[13] *= 0.1; Mw[14] *= 0.1
        nodes.append({'type': dw0 & 0xFF, 'bone': (dw0 >> 8) & 0xFF, 'M': Mw})
    return d, V, counts, src, dst, nodeM, nodes, NB

def read_rec(d, V, base, ri):
    s = struct.unpack_from('<8f', d, V + base + ri * 32)
    bone = struct.unpack_from('<I', d, V + base + ri * 32 + 0x1C)[0]
    return bone, s[3], np.array(s[0:3]), np.array(s[4:7])

def build_groups(d, V, counts, src, dst, mats=None):
    """Returns per-dst-vert influence lists [(bone, w, q, n)].
    Sections 0-2 fixed grouping; section 3 DP-segmented if mats given,
    else fixed-4 fallback."""
    src_off = [0]
    for si, c in enumerate(counts): src_off.append(src_off[-1] + c * (si + 1))
    dst_off = [0]
    for c in counts: dst_off.append(dst_off[-1] + c)
    groups = [None] * sum(counts)
    for si in (0, 1, 2):
        ninf = si + 1
        for k in range(dst_off[si], dst_off[si + 1]):
            groups[k] = [read_rec(d, V, src, src_off[si] + (k - dst_off[si]) * ninf + j) for j in range(ninf)]
    si = 3
    if counts[3] == 0:
        return groups, None
    if mats is None:
        for k in range(dst_off[3], dst_off[3] + counts[3]):
            groups[k] = [read_rec(d, V, src, src_off[3] + (k - dst_off[3]) * 4 + j) for j in range(4)]
        return groups, 'fixed4'
    # DP segmentation of section 3
    MAXREC = counts[3] * 6
    recs = [read_rec(d, V, src, src_off[3] + i) for i in range(MAXREC)]
    worlds = [np.array(struct.unpack_from('<3f', d, V + dst + (dst_off[3] + k) * 32)) for k in range(counts[3])]
    def cost(i, j, k):
        wsum = sum(recs[t][1] for t in range(i, j))
        if abs(wsum - 1.0) > 0.03: return 10.0 + abs(wsum - 1.0)
        pred = np.zeros(3)
        for t in range(i, j):
            bone, w, q, n = recs[t]
            if bone not in mats: return 0.01 + abs(wsum - 1.0)
            M = mats[bone]
            pred += M[0:9].reshape(3, 3) @ q + w * M[9:12]
        return float(np.abs(pred - worlds[k]).max())
    sys.setrecursionlimit(100000)
    @lru_cache(maxsize=None)
    def dp(i, k):
        if k == counts[3]: return (0.0, ())
        best = (float('inf'), None)
        for sz in (2, 3, 4, 5, 6, 7, 8, 9, 10, 1):
            j = i + sz
            if j > MAXREC: break
            c = cost(i, j, k)
            if c >= 10.0: continue
            sub = dp(j, k + 1)
            if sub[1] is None: continue
            if c + sub[0] < best[0]: best = (c + sub[0], (sz,) + sub[1])
        return best
    tot, sizes = dp(0, 0)
    if sizes is None:  # DP failed: fixed-4 fallback
        for k in range(dst_off[3], dst_off[3] + counts[3]):
            groups[k] = [read_rec(d, V, src, src_off[3] + (k - dst_off[3]) * 4 + j) for j in range(4)]
        return groups, 'fixed4-fallback'
    i = 0
    for k, sz in enumerate(sizes):
        groups[dst_off[3] + k] = recs[i:i + sz]
        i += sz
    return groups, {'sizes': {int(s): int(sizes.count(s)) for s in set(sizes)}, 'dp_cost': float(tot)}

def solve_mats(d, V, counts, src, dst, groups, fixed=None):
    bones = set()
    for g in groups:
        if g:
            for (bone, w, q, n) in g: bones.add(bone)
    bl = sorted(bones); bidx = {b: i for i, b in enumerate(bl)}
    N = len(bl) * 12
    AtA = np.zeros((N, N)); Atb = np.zeros(N)
    known = {}
    if fixed:
        for b, M in fixed.items():
            if b in bidx: known[b] = M
    for k, g in enumerate(groups):
        if not g: continue
        wpos = np.array(struct.unpack_from('<3f', d, V + dst + k * 32))
        # subtract known-bone contributions
        rhs = wpos.copy()
        infl = []
        for (bone, w, q, n) in g:
            if bone in known:
                M = known[bone]
                rhs -= M[0:9].reshape(3, 3) @ q + w * M[9:12]
            else:
                infl.append((bone, w, q))
        if not infl: continue
        for r in range(3):
            row = {}
            for (bone, w, q) in infl:
                base = bidx[bone] * 12
                for c in range(3):
                    row[base + r * 3 + c] = row.get(base + r * 3 + c, 0.0) + q[c]
                row[base + 9 + r] = row.get(base + 9 + r, 0.0) + w
            items = list(row.items())
            for (c1, v1) in items:
                Atb[c1] += v1 * rhs[r]
                for (c2, v2) in items:
                    AtA[c1, c2] += v1 * v2
        # normal equations: sum_i R_i @ n_i = world normal (R-only constraints;
        # known-bone contributions subtracted like positions)
        wnrm = np.array(struct.unpack_from('<3f', d, V + dst + k * 32 + 16))
        nrhs = wnrm.copy()
        ninfl = []
        for (bone, w, q, nn) in g:
            if bone in known:
                M = known[bone]
                nrhs -= M[0:9].reshape(3, 3) @ nn
            else:
                ninfl.append((bone, nn))
        for r in range(3):
            row = {}
            for (bone, nn) in ninfl:
                base = bidx[bone] * 12
                for c in range(3):
                    row[base + r * 3 + c] = row.get(base + r * 3 + c, 0.0) + nn[c]
            items = list(row.items())
            for (c1, v1) in items:
                Atb[c1] += v1 * nrhs[r]
                for (c2, v2) in items:
                    AtA[c1, c2] += v1 * v2
    # zero rows for known bones -> identity placeholder (unused; we overwrite)
    x = np.linalg.solve(AtA + 1e-9 * np.eye(N), Atb)
    mats = {}
    for b in bl:
        i = bidx[b] * 12
        mats[b] = x[i:i + 12].copy()
    for b, M in known.items(): mats[b] = M
    # residuals
    mx = 0.0; ss = 0.0; n = 0
    for k, g in enumerate(groups):
        if not g: continue
        wpos = np.array(struct.unpack_from('<3f', d, V + dst + k * 32))
        pred = np.zeros(3)
        for (bone, w, q, nn) in g:
            M = mats[bone]
            pred += M[0:9].reshape(3, 3) @ q + w * M[9:12]
        e = np.abs(pred - wpos); mx = max(mx, float(e.max())); ss += float((e ** 2).sum()); n += 3
    return mats, bl, float(mx), float(np.sqrt(ss / max(n, 1)))

def main():
    bundle, V, out_glb, out_rep = sys.argv[1], int(sys.argv[2], 0), sys.argv[3], sys.argv[4]
    d, V, counts, src, dst, nodeM, nodes, NB = parse(bundle, V)
    # step 2: solve sections 0-2
    g012, _ = build_groups(d, V, counts, src, dst, mats=None)
    g012_only = [g if (g is not None) else None for g in g012]
    # restrict to secs 0-2 verts for the preliminary solve
    NV012 = sum(counts[:3])
    mats_pre, bl_pre, mx_pre, rms_pre = solve_mats(d, V, counts, src, dst, g012[:NV012] + [None] * counts[3])
    # step 3: DP segmentation for section 3
    groups, seg_info = build_groups(d, V, counts, src, dst, mats=mats_pre)
    # step 4: joint solve
    mats, bl, mx, rms = solve_mats(d, V, counts, src, dst, groups)
    # underdetermined bones (1-2 verts, rank-deficient R): complete R with its
    # polar orthonormal factor (preserves R on the data-determined subspace);
    # flagged in the report, never hidden.
    ortho_bones = []
    for b in bl:
        R = mats[b][0:9].reshape(3, 3)
        if abs(np.linalg.det(R)) < 0.5:
            U, S, Vt = np.linalg.svd(R)
            mats[b][0:9] = (U @ Vt).reshape(9)
            ortho_bones.append(int(b))
    # node validation
    node_err = {}
    for b, M in nodeM.items():
        if b not in mats: continue
        Mm = mats[b]
        R = Mm[0:9].reshape(3, 3); T = Mm[9:12]
        Mexp = np.array([[M[0], M[4], M[8]], [M[1], M[5], M[9]], [M[2], M[6], M[10]]])
        Texp = np.array([M[12] * 0.1, M[13] * 0.1, M[14] * 0.1])
        node_err[int(b)] = float(max(np.abs(R - Mexp).max(), np.abs(T - Texp).max()))
    with open(out_rep.replace('.json','') + '_binds.json', 'w') as fh:
        fh.write(json.dumps({'bones': [int(b) for b in bl],
               'mats': {int(b): [float(x) for x in mats[b]] for b in bl},
               'counts': counts, 'seg3': seg_info,
               'res_max': mx, 'res_rms': rms,
               'pre_res_max': mx_pre, 'node_err': node_err}, indent=1))
    print(f"bones={len(bl)} joint res_max={mx:.3e} rms={rms:.3e} pre(0-2)={mx_pre:.3e} seg3={seg_info}")
    print(f"node_err: max={max(node_err.values()):.3e} median={sorted(node_err.values())[len(node_err)//2]:.3e}")
    # step 5: GLB export — geometry/topology from phase-4 decoder logic
    # (phase-15: dead p4 import removed on repo landing; the geometry
    # read below was always a self-contained reimplementation.)
    def u32(o): return struct.unpack_from('<I', d, V + o)[0]
    def u16(o): return struct.unpack_from('<H', d, V + o)[0]
    NV = sum(counts)
    pos = []; nrm = []; uv = []; col = []
    uv_base = None
    pcounts = [u16(0x0C), u16(0x0E), u16(0x10)]
    skinned_parts = []; rigid_parts = []
    for gi, bo in enumerate([0x2C, 0x30, 0x34]):
        base = u32(bo)
        for i in range(pcounts[gi]):
            rec = struct.unpack_from('<10I', d, V + base + i * 40)
            idx = list(struct.unpack_from(f'<{rec[1]}H', d, V + rec[4]))
            if rec[0] & 0xFF == 4:
                skinned_parts.append((f"g{gi}p{i:02d}", rec, idx))
                if uv_base is None: uv_base = rec[5]
            else:
                rigid_parts.append((f"g{gi}p{i:02d}", rec, idx))
    for k in range(NV):
        f = struct.unpack_from('<8f', d, V + dst + k * 32)
        pos.append(f[0:3]); nrm.append(f[4:7])
        c, uu, vv = struct.unpack_from('<Iff', d, V + uv_base + k * 12)
        col.append(((c >> 16 & 255) / 255, (c >> 8 & 255) / 255, (c & 255) / 255, (c >> 24 & 255) / 255))
        uv.append((uu, vv))
    def strip_to_tris(idx):
        tris = []
        for i in range(len(idx) - 2):
            a, b, c = idx[i], idx[i + 1], idx[i + 2]
            if a == b or b == c or a == c: continue
            if i % 2 == 1: a, c = c, a
            tris.append((a, b, c))
        return tris
    def list_to_tris(idx):
        return [(idx[i], idx[i + 1], idx[i + 2]) for i in range(0, len(idx) - 2, 3)
                if len({idx[i], idx[i + 1], idx[i + 2]}) == 3]
    def score(tris, P, N):
        if not tris: return 0.0
        tot = 0.0; nn = 0
        for a, b, c in tris:
            pa, pb, pc = P[a], P[b], P[c]
            ux, uy, uz = pb[0] - pa[0], pb[1] - pa[1], pb[2] - pa[2]
            vx, vy, vz = pc[0] - pa[0], pc[1] - pa[1], pc[2] - pa[2]
            gx, gy, gz = uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx
            gl = math.sqrt(gx * gx + gy * gy + gz * gz)
            if gl < 1e-12: continue
            gx, gy, gz = gx / gl, gy / gl, gz / gl
            for vi in (a, b, c):
                nv = N[vi]
                tot += gx * nv[0] + gy * nv[1] + gz * nv[2]; nn += 1
        return tot / nn if nn else 0.0
    # joints/weights per vertex
    bidx = {b: i for i, b in enumerate(bl)}
    JOINTS = []; WEIGHTS = []; trunc = 0
    for k in range(NV):
        g = groups[k] or []
        infl = sorted(((w, bidx[bone]) for (bone, w, q, n) in g), reverse=True)
        if len(infl) > 4:
            trunc += 1
            infl = infl[:4]
            ssum = sum(w for w, _ in infl)
            infl = [(w / ssum, j) for (w, j) in infl]
        while len(infl) < 4: infl.append((0.0, 0))
        JOINTS.append(tuple(j for (_, j) in infl))
        WEIGHTS.append(tuple(w for (w, _) in infl))
    # bind matrices as glTF column-major 4x4 (row-vector conv: world = q . M, M stored rows)
    def gltf_mat(M12):
        R = M12[0:9].reshape(3, 3); T = M12[9:12]
        # our convention: world_r = sum_c q_c * R[r,c] + T_r  (R as stored, row r)
        # glTF matrix is column-major with column-vector convention v' = M v.
        # Equivalent M: rows of M = columns... v'_r = sum_c R[r,c] q_c + T_r -> matrix elements M4[c*4+r] = R[r,c], M4[12+r]=T_r
        m = [0.0] * 16
        for r in range(3):
            for c in range(3): m[c * 4 + r] = float(R[r, c])
            m[12 + r] = float(T[r])
        m[15] = 1.0
        return m
    def inv_mat(M12):
        R = M12[0:9].reshape(3, 3); T = M12[9:12]
        N = np.eye(4)
        N[0:3, 0:3] = R; N[0:3, 3] = T
        Ai = np.linalg.inv(N) if abs(np.linalg.det(N)) > 1e-8 else np.linalg.pinv(N)
        # glTF storage: element (r,c) lives at list index c*4+r
        return [float(Ai[r, c]) for c in range(4) for r in range(4)]
    binbuf = io.BytesIO(); accessors = []; bufferViews = []; meshes = []; gltf_nodes = []
    def add_view(data, target):
        off = len(binbuf.getvalue()); binbuf.write(data)
        while len(binbuf.getvalue()) % 4: binbuf.write(b'\0')
        bufferViews.append({"buffer": 0, "byteOffset": off, "byteLength": len(data), "target": target})
        return len(bufferViews) - 1
    def add_acc(view, ct, at, count, mn=None, mx=None):
        a = {"bufferView": view, "componentType": ct, "type": at, "count": count}
        if mn is not None: a["min"] = mn; a["max"] = mx
        accessors.append(a); return len(accessors) - 1
    # skinned mesh (single merged primitive set: one mesh per part, shared attributes)
    # phase-15 gate: every exported skinned position/normal must be finite
    assert all(math.isfinite(x) for p in pos for x in p), 'non-finite skinned position at export'
    assert all(math.isfinite(x) for n in nrm for x in n), 'non-finite skinned normal at export'
    pa = add_acc(add_view(b''.join(struct.pack('<3f', *p) for p in pos), 34962), 5126, "VEC3", NV,
                 [min(p[i] for p in pos) for i in range(3)], [max(p[i] for p in pos) for i in range(3)])
    na = add_acc(add_view(b''.join(struct.pack('<3f', *n) for n in nrm), 34962), 5126, "VEC3", NV)
    ta = add_acc(add_view(b''.join(struct.pack('<2f', *t) for t in uv), 34962), 5126, "VEC2", NV)
    ca = add_acc(add_view(b''.join(struct.pack('<4f', *c) for c in col), 34962), 5126, "VEC4", NV)
    ja = add_acc(add_view(b''.join(struct.pack('<4H', *j) for j in JOINTS), 34962), 5123, "VEC4", NV)
    wa = add_acc(add_view(b''.join(struct.pack('<4f', *w) for w in WEIGHTS), 34962), 5126, "VEC4", NV)
    for name, rec, idx in skinned_parts:
        st = strip_to_tris(idx); lt = list_to_tris(idx)
        tris = st if score(st, pos, nrm) >= score(lt, pos, nrm) else lt
        ia = add_acc(add_view(b''.join(struct.pack('<3I', *t) for t in tris), 34963), 5125, "SCALAR", len(tris) * 3)
        meshes.append({"name": name, "primitives": [{"attributes": {"POSITION": pa, "NORMAL": na, "TEXCOORD_0": ta, "COLOR_0": ca, "JOINTS_0": ja, "WEIGHTS_0": wa}, "indices": ia, "mode": 4}]})
        gltf_nodes.append({"mesh": len(meshes) - 1, "name": name, "skin": 0})
    # rigid parts placed (no skin)
    for name, rec, idx in rigid_parts:
        nidx = (rec[2] - NB) // 400
        if nidx < 0 or nidx >= len(nodes): continue
        M = nodes[nidx]['M']
        span = rec[9] - rec[5]; mxv = max(idx) + 1; start = rec[5]
        # Phase-15 ROOT FIX (proven in PHASE15-PROBES.md job 1): the old
        # "+8 when (span-8)//40 == vertex count" start shift is WRONG.
        # Those parts carry an 8-byte TRAILER after their vertex stream
        # (span = count*40 + 8); their vertices start at rec[5] in the
        # standard format like every other part. The shift moved the
        # +0x18 ARGB color word into the +0x10 normal-Y slot: white
        # colors (0xFFFFFFFF) read as NaN and the part was silently
        # excluded as a "sheet" (the phase-4 "sheet class" is this
        # artifact — it does not exist in the rigid streams), while
        # grey colors (0xFF7F7F7F etc.) read as ~-3.4e38 floats, passed
        # the isnan check, and the node transform pushed them past
        # FLT_MAX -> struct.pack OverflowError (idx283/idx291 Ivy).
        # Census proof: at +0 alignment, all 725 rigid parts in 25
        # bundles have unit normals (|n|-1 < 0.05) and 0xFF-alpha
        # colors at +0x18 for every vertex. Vertex streams always
        # start at rec[5]; no shift, no sheet exclusion.
        rp = []; rn = []; ru = []; rc = []
        for k in range(mxv):
            f = struct.unpack_from('<10f', d, V + start + k * 40)
            rp.append(f[0:3]); rn.append(f[3:6])
            cu = struct.unpack_from('<I', d, V + start + k * 40 + 24)[0]
            rc.append(((cu >> 16 & 255) / 255, (cu >> 8 & 255) / 255, (cu & 255) / 255, (cu >> 24 & 255) / 255))
            ru.append((f[7], f[8]))
        pp = [(x * M[0] + y * M[4] + z * M[8] + M[12], x * M[1] + y * M[5] + z * M[9] + M[13], x * M[2] + y * M[6] + z * M[10] + M[14]) for (x, y, z) in rp]
        pn = [(x * M[0] + y * M[4] + z * M[8], x * M[1] + y * M[5] + z * M[9], x * M[2] + y * M[6] + z * M[10]) for (x, y, z) in rn]
        # phase-15 gate: rigid positions/normals finite before packing
        assert all(math.isfinite(x) for p in pp for x in p), f'non-finite rigid position in {name}'
        assert all(math.isfinite(x) for n in pn for x in n), f'non-finite rigid normal in {name}'
        st = strip_to_tris(idx); lt = list_to_tris(idx)
        tris = st if score(st, pp, pn) >= score(lt, pp, pn) else lt
        pa2 = add_acc(add_view(b''.join(struct.pack('<3f', *p) for p in pp), 34962), 5126, "VEC3", len(pp),
                      [min(p[i] for p in pp) for i in range(3)], [max(p[i] for p in pp) for i in range(3)])
        na2 = add_acc(add_view(b''.join(struct.pack('<3f', *n) for n in pn), 34962), 5126, "VEC3", len(pn))
        ta2 = add_acc(add_view(b''.join(struct.pack('<2f', *t) for t in ru), 34962), 5126, "VEC2", len(ru))
        ca2 = add_acc(add_view(b''.join(struct.pack('<4f', *c) for c in rc), 34962), 5126, "VEC4", len(rc))
        ia2 = add_acc(add_view(b''.join(struct.pack('<3I', *t) for t in tris), 34963), 5125, "SCALAR", len(tris) * 3)
        meshes.append({"name": name + "_r", "primitives": [{"attributes": {"POSITION": pa2, "NORMAL": na2, "TEXCOORD_0": ta2, "COLOR_0": ca2}, "indices": ia2, "mode": 4}]})
        gltf_nodes.append({"mesh": len(meshes) - 1, "name": name + "_r"})
    # skeleton: joint nodes flat under root
    joint_node_ids = []
    root_children = list(range(len(gltf_nodes)))
    for i, b in enumerate(bl):
        gltf_nodes.append({"name": f"bone_{b}", "matrix": gltf_mat(mats[b])})
        joint_node_ids.append(len(gltf_nodes) - 1)
    ibm = []
    for b in bl: ibm.extend(inv_mat(mats[b]))
    ibm_acc = add_acc(add_view(b''.join(struct.pack('<f', x) for x in ibm), None), 5126, "MAT4", len(bl))
    gltf = {"asset": {"version": "2.0", "generator": "scii-phase5-skinned"},
            "scene": 0, "scenes": [{"nodes": root_children + joint_node_ids}],
            "nodes": gltf_nodes, "meshes": meshes,
            "skins": [{"name": "scii_skin", "joints": joint_node_ids, "inverseBindMatrices": ibm_acc}],
            "accessors": accessors, "bufferViews": bufferViews,
            "buffers": [{"byteLength": len(binbuf.getvalue())}]}
    js = json.dumps(gltf).encode()
    while len(js) % 4: js += b' '
    bindata = binbuf.getvalue()
    with open(out_glb, 'wb') as fh:
        fh.write(struct.pack('<III', 0x46546C67, 2, 12 + 8 + len(js) + 8 + len(bindata)))
        fh.write(struct.pack('<II', len(js), 0x4E4F534A)); fh.write(js)
        fh.write(struct.pack('<II', len(bindata), 0x004E4942)); fh.write(bindata)
    rep = {'glb': out_glb, 'bones': len(bl), 'verts': NV, 'truncated_verts': trunc,
           'orthonormalized_bones': ortho_bones,
           'res_max': mx, 'res_rms': rms, 'seg3': seg_info,
           'node_err_max': max(node_err.values()) if node_err else None}
    with open(out_rep, 'w') as fh: fh.write(json.dumps(rep, indent=1))
    print(json.dumps(rep))

if __name__ == '__main__':
    main()
