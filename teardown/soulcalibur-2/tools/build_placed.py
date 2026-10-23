#!/usr/bin/env python3
"""SCII phase-17: placed (rigid, unskinned) GLB builder for one fighter VMX.

This is the placement path that produced the phase-3 `models/`
placed GLBs (generator `scii-phase4-decoder-v2`): bind matrix = the
file 4x4 node matrix, translation x0.1. There was never a separate
placed script in the repo — the geometry logic lived inside
`tools/build_skinned.py` ("Rigid parts included placed (as phase-4
_placed)"), which is why this tool mirrors that code exactly:

  - type-4 (skinned) parts: geometry from the shared dst world/bind
    stream (positions are already in placed/world space), one mesh
    per part over shared attribute accessors;
  - rigid parts: per-part vertex stream at rec[5], transformed by
    the part's node world matrix, mesh name suffixed `_r`.

THE FIX (phase 15/16, applied here identically): rigid vertex
streams always start at rec[5] — the old "+8 start shift" for
trailer-span parts (span = count*40 + 8) was a misread that dropped
those parts as a fake "sheet class". At +0 alignment all rigid
parts have unit normals and 0xFF-alpha colors (725-part census,
PHASE15-PROBES.md job 1). Finite assertions before all packing.

Difference from build_skinned.py: no skin solving, no JOINTS_0 /
WEIGHTS_0, no skins, no bone nodes — placed GLBs are rigid: one
scene node per mesh. Verified at phase-17 lane start: all 891 old
placed meshes are byte-identical (POSITION/NORMAL/TEXCOORD_0/
COLOR_0/index) to the same-named meshes in the fixed-reader
skinned GLBs, so this path reproduces the old placed set exactly
where the old reader was correct, and adds the trailer-span rigid
parts it dropped.

Usage: build_placed.py <bundle.bin> <vmx_off> <out.glb> <report.json>
"""
import struct, sys, json, io, math


def main():
    bundle, V, out_glb, out_rep = sys.argv[1], int(sys.argv[2], 0), sys.argv[3], sys.argv[4]
    d = open(bundle, 'rb').read()
    def u32(o): return struct.unpack_from('<I', d, V + o)[0]
    def u16(o): return struct.unpack_from('<H', d, V + o)[0]
    assert d[V:V + 4] == b'VMX.'
    b28 = u32(0x38)
    r28 = struct.unpack_from('<7I', d, V + b28)
    counts = list(r28[0:4]); dst = r28[5]
    NB = u32(0x24); NN = u16(0x0A)
    nodes = []
    for i in range(NN):
        base = NB + i * 400; dw0 = u32(base)
        M = list(struct.unpack_from('<16f', d, V + base + 0x10))
        Mw = list(M); Mw[12] *= 0.1; Mw[13] *= 0.1; Mw[14] *= 0.1
        nodes.append({'type': dw0 & 0xFF, 'bone': (dw0 >> 8) & 0xFF, 'M': Mw})
    pcounts = [u16(0x0C), u16(0x0E), u16(0x10)]
    skinned_parts = []; rigid_parts = []
    uv_base = None
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
    # shared dst world/bind stream (skinned parts' placed geometry)
    NV = sum(counts)
    pos = []; nrm = []; uv = []; col = []
    for k in range(NV):
        f = struct.unpack_from('<8f', d, V + dst + k * 32)
        pos.append(f[0:3]); nrm.append(f[4:7])
        c, uu, vv = struct.unpack_from('<Iff', d, V + uv_base + k * 12)
        col.append(((c >> 16 & 255) / 255, (c >> 8 & 255) / 255, (c & 255) / 255, (c >> 24 & 255) / 255))
        uv.append((uu, vv))
    assert all(math.isfinite(x) for p in pos for x in p), 'non-finite dst position at export'
    assert all(math.isfinite(x) for n in nrm for x in n), 'non-finite dst normal at export'

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

    # skinned-type parts: placed via the dst world stream, shared attributes
    pa = add_acc(add_view(b''.join(struct.pack('<3f', *p) for p in pos), 34962), 5126, "VEC3", NV,
                 [min(p[i] for p in pos) for i in range(3)], [max(p[i] for p in pos) for i in range(3)])
    na = add_acc(add_view(b''.join(struct.pack('<3f', *n) for n in nrm), 34962), 5126, "VEC3", NV)
    ta = add_acc(add_view(b''.join(struct.pack('<2f', *t) for t in uv), 34962), 5126, "VEC2", NV)
    ca = add_acc(add_view(b''.join(struct.pack('<4f', *c) for c in col), 34962), 5126, "VEC4", NV)
    for name, rec, idx in skinned_parts:
        st = strip_to_tris(idx); lt = list_to_tris(idx)
        tris = st if score(st, pos, nrm) >= score(lt, pos, nrm) else lt
        ia = add_acc(add_view(b''.join(struct.pack('<3I', *t) for t in tris), 34963), 5125, "SCALAR", len(tris) * 3)
        meshes.append({"name": name, "primitives": [{"attributes": {"POSITION": pa, "NORMAL": na, "TEXCOORD_0": ta, "COLOR_0": ca}, "indices": ia, "mode": 4}]})
        gltf_nodes.append({"mesh": len(meshes) - 1, "name": name})
    # rigid parts placed by node world matrix (no +8 shift — fixed reader)
    for name, rec, idx in rigid_parts:
        nidx = (rec[2] - NB) // 400
        if nidx < 0 or nidx >= len(nodes): continue
        M = nodes[nidx]['M']
        mxv = max(idx) + 1; start = rec[5]
        rp = []; rn = []; ru = []; rc = []
        for k in range(mxv):
            f = struct.unpack_from('<10f', d, V + start + k * 40)
            rp.append(f[0:3]); rn.append(f[3:6])
            cu = struct.unpack_from('<I', d, V + start + k * 40 + 24)[0]
            rc.append(((cu >> 16 & 255) / 255, (cu >> 8 & 255) / 255, (cu & 255) / 255, (cu >> 24 & 255) / 255))
            ru.append((f[7], f[8]))
        pp = [(x * M[0] + y * M[4] + z * M[8] + M[12], x * M[1] + y * M[5] + z * M[9] + M[13], x * M[2] + y * M[6] + z * M[10] + M[14]) for (x, y, z) in rp]
        pn = [(x * M[0] + y * M[4] + z * M[8], x * M[1] + y * M[5] + z * M[9], x * M[2] + y * M[6] + z * M[10]) for (x, y, z) in rn]
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
    gltf = {"asset": {"version": "2.0", "generator": "scii-phase17-placed-fixed-reader"},
            "scene": 0, "scenes": [{"nodes": list(range(len(gltf_nodes)))}],
            "nodes": gltf_nodes, "meshes": meshes,
            "accessors": accessors, "bufferViews": bufferViews,
            "buffers": [{"byteLength": len(binbuf.getvalue())}]}
    js = json.dumps(gltf).encode()
    while len(js) % 4: js += b' '
    bindata = binbuf.getvalue()
    with open(out_glb, 'wb') as fh:
        fh.write(struct.pack('<III', 0x46546C67, 2, 12 + 8 + len(js) + 8 + len(bindata)))
        fh.write(struct.pack('<II', len(js), 0x4E4F534A)); fh.write(js)
        fh.write(struct.pack('<II', len(bindata), 0x004E4942)); fh.write(bindata)
    rep = {'glb': out_glb, 'meshes': len(meshes),
           'skinned_type_parts': len(skinned_parts), 'rigid_parts': len(rigid_parts),
           'verts_dst': NV}
    with open(out_rep, 'w') as fh: fh.write(json.dumps(rep, indent=1))
    print(json.dumps(rep))


if __name__ == '__main__':
    main()
