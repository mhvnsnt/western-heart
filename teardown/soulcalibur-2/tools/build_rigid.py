#!/usr/bin/env python3
"""SCII phase-15: rigid-only VMX bundle -> placed, textured-ready GLB.

For bundles whose VMX contains NO skinned (type-4) parts at all
(idx789: 102/102 parts type 0, rec28 skin pool empty) the skinned
pipeline cannot run. This tool is the rigid path: every part is placed
by its node world matrix (the same transform build_skinned applies to
rigid parts), topology chosen per part by the phase-4 rule.

Vertex format: the standard rigid format (pos, unit normal, ARGB
color, UV, pad) at rec[5] for every part — including parts whose
span carries an 8-byte trailer (count*40 + 8). The phase-4 "+8
start shift" for trailer parts was a misread that manufactured a
fake "sheet class" (see PHASE15-PROBES.md job 1); census proof: all
725 rigid parts in 25 bundles have unit normals and 0xFF-alpha
colors at +0 alignment. Topology per part by normal-agreement
score, as in build_skinned.

Usage: build_rigid.py <bundle.bin> <vmx_off> <out.glb> <report.json>
"""
import struct, sys, json, io, math
import numpy as np


def main():
    bundle, V, out_glb, out_rep = sys.argv[1], int(sys.argv[2], 0), sys.argv[3], sys.argv[4]
    d = open(bundle, 'rb').read()
    def u32(o): return struct.unpack_from('<I', d, V + o)[0]
    def u16(o): return struct.unpack_from('<H', d, V + o)[0]
    assert d[V:V + 4] == b'VMX.'
    NB = u32(0x24); NN = u16(0x0A)
    nodes = []
    for i in range(NN):
        base = NB + i * 400; dw0 = u32(base)
        M = list(struct.unpack_from('<16f', d, V + base + 0x10))
        Mw = list(M); Mw[12] *= 0.1; Mw[13] *= 0.1; Mw[14] *= 0.1
        nodes.append({'type': dw0 & 0xFF, 'bone': (dw0 >> 8) & 0xFF, 'M': Mw})
    pcounts = [u16(0x0C), u16(0x0E), u16(0x10)]

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

    def mean_edge(tris, P):
        if not tris: return 1e30
        tot = 0.0; n = 0
        for a, b, c in tris:
            for x, y in ((a, b), (b, c), (c, a)):
                tot += math.dist(P[x], P[y]); n += 1
        return tot / n if n else 1e30

    def nrm_score(tris, P, N):
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
                nv = N[vi]; tot += gx * nv[0] + gy * nv[1] + gz * nv[2]; nn += 1
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

    report_parts = []
    for gi, bo in enumerate([0x2C, 0x30, 0x34]):
        base = u32(bo)
        for i in range(pcounts[gi]):
            name = f"g{gi}p{i:02d}"
            rec = struct.unpack_from('<10I', d, V + base + i * 40)
            idx = list(struct.unpack_from(f'<{rec[1]}H', d, V + rec[4]))
            nidx = (rec[2] - NB) // 400
            if nidx < 0 or nidx >= len(nodes):
                report_parts.append((name, 'bad-node-index')); continue
            M = nodes[nidx]['M']
            span = rec[9] - rec[5]; mxv = max(idx) + 1; start = rec[5]
            # no +8 shift: trailer parts still start at rec[5] (see header)
            rp = []; rn = []; ru = []; rc = []
            for k in range(mxv):
                f = struct.unpack_from('<10f', d, V + start + k * 40)
                rp.append(f[0:3]); rn.append(f[3:6])
                cu = struct.unpack_from('<I', d, V + start + k * 40 + 24)[0]
                rc.append(((cu >> 16 & 255) / 255, (cu >> 8 & 255) / 255, (cu & 255) / 255, (cu >> 24 & 255) / 255))
                ru.append((f[7], f[8]))
            pp = [(x * M[0] + y * M[4] + z * M[8] + M[12], x * M[1] + y * M[5] + z * M[9] + M[13], x * M[2] + y * M[6] + z * M[10] + M[14]) for (x, y, z) in rp]
            pn = [(x * M[0] + y * M[4] + z * M[8], x * M[1] + y * M[5] + z * M[9], x * M[2] + y * M[6] + z * M[10]) for (x, y, z) in rn]
            st = strip_to_tris(idx); lt = list_to_tris(idx)
            tris = st if nrm_score(st, pp, pn) >= nrm_score(lt, pp, pn) else lt
            assert all(math.isfinite(x) for p in pp for x in p), f'non-finite position in {name}'
            assert all(math.isfinite(x) for n in pn for x in n), f'non-finite normal in {name}'
            pa = add_acc(add_view(b''.join(struct.pack('<3f', *p) for p in pp), 34962), 5126, "VEC3", len(pp),
                         [min(p[j] for p in pp) for j in range(3)], [max(p[j] for p in pp) for j in range(3)])
            na = add_acc(add_view(b''.join(struct.pack('<3f', *n) for n in pn), 34962), 5126, "VEC3", len(pn))
            ta = add_acc(add_view(b''.join(struct.pack('<2f', *t) for t in ru), 34962), 5126, "VEC2", len(ru))
            ca = add_acc(add_view(b''.join(struct.pack('<4f', *c) for c in rc), 34962), 5126, "VEC4", len(rc))
            ia = add_acc(add_view(b''.join(struct.pack('<3I', *t) for t in tris), 34963), 5125, "SCALAR", len(tris) * 3)
            meshes.append({"name": name + "_r", "primitives": [{"attributes": {"POSITION": pa, "NORMAL": na, "TEXCOORD_0": ta, "COLOR_0": ca}, "indices": ia, "mode": 4}]})
            gltf_nodes.append({"mesh": len(meshes) - 1, "name": name + "_r"})
            report_parts.append((name, 'normal', len(pp), len(tris)))
    gltf = {"asset": {"version": "2.0", "generator": "scii-phase15-rigid"},
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
           'verts_total': sum(p[2] for p in report_parts if len(p) > 2),
           'parts': report_parts}
    with open(out_rep, 'w') as fh: fh.write(json.dumps(rep, indent=1))
    print(json.dumps({k: v for k, v in rep.items() if k != 'parts'}))


if __name__ == '__main__':
    main()
