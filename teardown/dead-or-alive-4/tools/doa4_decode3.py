#!/usr/bin/env python3
"""
DOA4 triangulated mesh decoder v3 — for the chrthree tables (and any XPR2
table) whose IBUF layout defeats doa4_decode.py + batch_decode2.py:

- batch_decode2's discover_base() required base >= 0, a single base for the
  whole table, and strips starting with the exact pattern (0,1,2). The
  remaining chrthree tables use a relative-offset sub-layout (GPU addr <
  file offset, i.e. negative base) and/or per-descriptor bases, so discovery
  failed (2026-10-19 continuation doc).
- 2026-10-20 byte-level note (SWEEP-AUDIT-2026-10-20.md): the chrthree
  chunks at batch indices 09-33 contain NO VBUF/IBUF records at all
  (sub-packages: XPR2 + TX2D records only). v3's discovery applies to
  tables that DO carry IBUF descriptors with undiscovered bases; the
  09-33 sub-package layout needs its own RE pass before any decoder run.

v3 changes:
1. Candidate strip starts are searched only inside the table's own chunk
   region [table_offset, next_table_offset) — index data for a table lives
   in its own chunk; this kills false candidates from other tables.
2. Negative bases are allowed.
3. If no single base validates across all IBUF descriptors, fall back to
   per-descriptor offsets (each descriptor gets its own discovered ioff).
4. write_glb FIXED: TEXCOORD_0 accessor byteOffset is 12 (interleaved
   pos12+uv8, stride 20). doa4_decode.write_glb wrote n*12, which makes
   Blender's glTF importer fail ("buffer is smaller than requested size")
   on all 165 previously shipped GLBs.
5. Quality gate: GLB is only written when the mesh has no NaN positions
   and <=5% degenerate triangles; the gate result is printed per table.

Vertex format (unchanged, established): 20-byte BE records, float3 pos +
float2 uv. IBUF descriptor: 20-byte BE (flags, addr, size, type=0x20001, 0);
index data = BE u16 triangle strips, 0xFFFF restart.

Per-character isolation: each table is decoded independently into its own
GLB; no shared state between tables.

Usage: doa4_decode3.py <afs_path> <out_dir> [only_indices_comma_separated]
"""
import json
import math
import os
import re
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from doa4_decode import parse_xpr2, strip_to_tris  # noqa: E402


def find_tables(data):
    tables = []
    for m in re.finditer(rb'XPR2', data):
        xp = m.start()
        if xp % 4 != 0:
            continue
        recs = parse_xpr2(data, xp)
        if sum(1 for r in recs if r[0] == 'VBUF') >= 1 and len(recs) >= 4:
            tables.append(xp)
    out = []
    for xp in tables:
        if not out or xp - out[-1] > 64:
            out.append(xp)
    return out


def get_pool(data, xp):
    """Return (verts, uvs, vcount) using doa4_decode's pool heuristic."""
    recs = parse_xpr2(data, xp)
    vbufs = [(f1, f2, f3) for m, f1, f2, f3 in recs if m == 'VBUF']
    if not vbufs:
        return None
    from collections import defaultdict
    groups = defaultdict(list)
    for f1, f2, f3 in vbufs:
        groups[(f2, f3)].append(f1)
    (stride, vcount), f1s = max(groups.items(), key=lambda x: len(x[1]))
    if stride != 20 or not (100 < vcount < 100000):
        return None
    voff = min(f1s)
    verts, uvs = [], []
    for i in range(vcount):
        o = voff + i * stride
        x, y, z = struct.unpack('>3f', data[o:o + 12])
        u, v = struct.unpack('>2f', data[o + 12:o + 20])
        verts.append((x, y, z))
        uvs.append((u, v))
    return verts, uvs, voff, stride


def get_descs(data, xp):
    recs = parse_xpr2(data, xp)
    descs = []
    for m, f1, f2, f3 in recs:
        if m != 'IBUF':
            continue
        doff = xp + f1
        if doff + 20 > len(data):
            continue
        flags, addr, size, typ, _ = struct.unpack('>5I', data[doff:doff + 20])
        if typ == 0x20001 and size > 0:
            descs.append((addr & ~3, size))
    return descs


def valid_strip(data, ioff, size, vcount):
    if ioff < 0 or ioff + size > len(data) or size < 6:
        return False
    idx = struct.unpack('>%dH' % (size // 2), data[ioff:ioff + size])
    good = sum(1 for v in idx if v < vcount * 4 or v == 0xFFFF)
    return good / len(idx) >= 0.98


def strip_candidates(data, lo, hi):
    """Offsets in [lo,hi) where a BE u16 strip plausibly starts."""
    pats = [struct.pack('>5H', 0, 1, 2, 1, 3), struct.pack('>6H', 0, 1, 2, 3, 4, 5),
            struct.pack('>3H', 0, 1, 2)]
    cands = []
    for pat in pats:
        start = lo
        while True:
            i = data.find(pat, start, hi)
            if i < 0:
                break
            cands.append(i)
            start = i + 2
        if cands:
            break
    return cands


def discover(data, xp, region_hi, vcount):
    """Return list of (ioff, size) per descriptor, or None."""
    descs = get_descs(data, xp)
    if not descs:
        return None
    cands = strip_candidates(data, xp, region_hi)
    # single-base attempt (base may be negative)
    seen = set()
    for c in cands:
        base = descs[0][0] - c
        if base in seen:
            continue
        seen.add(base)
        if all(valid_strip(data, addr - base, size, vcount) for addr, size in descs):
            return [(addr - base, size) for addr, size in descs]
    # per-descriptor fallback
    out = []
    for addr, size in descs:
        hit = None
        seen = set()
        for c in cands:
            base = addr - c
            if base in seen:
                continue
            seen.add(base)
            if valid_strip(data, c, size, vcount):
                # prefer the candidate whose start pattern is at c
                hit = (c, size)
                break
        if hit is None:
            return None
        out.append(hit)
    return out


def decode_table3(data, xp, region_hi):
    pool = get_pool(data, xp)
    if pool is None:
        return None
    verts, uvs, voff, stride = pool
    vcount = len(verts)
    iofs = discover(data, xp, region_hi, vcount)
    if iofs is None:
        return None
    # expand pool to cover max index
    max_idx = 0
    strips = []
    for ioff, size in iofs:
        idx = struct.unpack('>%dH' % (size // 2), data[ioff:ioff + size])
        strips.append(idx)
        for v in idx:
            if v != 0xFFFF and v > max_idx:
                max_idx = v
    if max_idx + 1 > vcount:
        for i in range(vcount, max_idx + 1):
            o = voff + i * stride
            if o + 20 > len(data):
                break
            x, y, z = struct.unpack('>3f', data[o:o + 12])
            u, v = struct.unpack('>2f', data[o + 12:o + 20])
            verts.append((x, y, z))
            uvs.append((u, v))
        vcount = len(verts)
    tris = []
    for idx in strips:
        tris.extend(strip_to_tris([v for v in idx if v < vcount or v == 0xFFFF]))
    return {'verts': verts, 'uvs': uvs, 'tris': tris}


def write_glb_fixed(verts, uvs, tris, path):
    n = len(verts)
    bin_data = bytearray()
    for i in range(n):
        bin_data.extend(struct.pack('<3f', *verts[i]))
        bin_data.extend(struct.pack('<2f', *uvs[i]))
    idx_off = len(bin_data)
    for a, b, c in tris:
        bin_data.extend(struct.pack('<3I', a, b, c))
    while len(bin_data) % 4:
        bin_data.append(0)
    json_str = json.dumps({
        "asset": {"version": "2.0", "generator": "doa4-decode3"},
        "accessors": [
            {"bufferView": 0, "componentType": 5126, "count": n, "type": "VEC3",
             "max": [max(v[i] for v in verts) for i in range(3)],
             "min": [min(v[i] for v in verts) for i in range(3)]},
            {"bufferView": 0, "byteOffset": 12, "componentType": 5126, "count": n, "type": "VEC2"},
            {"bufferView": 1, "componentType": 5125, "count": len(tris) * 3, "type": "SCALAR"},
        ],
        "bufferViews": [
            {"buffer": 0, "byteOffset": 0, "byteLength": n * 20, "byteStride": 20},
            {"buffer": 0, "byteOffset": idx_off, "byteLength": len(tris) * 12},
        ],
        "buffers": [{"byteLength": len(bin_data)}],
        "meshes": [{"primitives": [{
            "attributes": {"POSITION": 0, "TEXCOORD_0": 1},
            "indices": 2, "mode": 4,
        }]}],
        "nodes": [{"mesh": 0}],
        "scenes": [{"nodes": [0]}],
        "scene": 0,
    }, separators=(',', ':'))
    jb = json_str.encode()
    while len(jb) % 4:
        jb += b' '
    glb = bytearray()
    glb.extend(struct.pack('<4sII', b'glTF', 2, 12 + 8 + len(jb) + 8 + len(bin_data)))
    glb.extend(struct.pack('<II', len(jb), 0x4E4F534A))
    glb.extend(jb)
    glb.extend(struct.pack('<II', len(bin_data), 0x004E4942))
    glb.extend(bin_data)
    with open(path, 'wb') as f:
        f.write(glb)


def quality(tris, verts):
    if not tris:
        return 1.0, True
    degen = sum(1 for a, b, c in tris if a == b or b == c or a == c)
    nan = any(math.isnan(c) or math.isinf(c) for v in verts for c in v)
    return degen / len(tris), nan


def main():
    afs, outdir = sys.argv[1], sys.argv[2]
    only = set(int(x) for x in sys.argv[3].split(',')) if len(sys.argv) > 3 and sys.argv[3] else None
    stem = os.path.basename(afs).split('.')[0]
    os.makedirs(outdir, exist_ok=True)
    with open(afs, 'rb') as f:
        data = f.read()
    tables = find_tables(data)
    print(f"{stem}: {len(tables)} tables")
    ok = 0
    for idx, xp in enumerate(tables):
        if only is not None and idx not in only:
            continue
        existing = [f for f in os.listdir(outdir) if f.startswith(f"{stem}_{idx:02d}_")]
        if existing:
            print(f"  [{idx:02d}] skip (exists)")
            ok += 1
            continue
        region_hi = tables[idx + 1] if idx + 1 < len(tables) else len(data)
        r = decode_table3(data, xp, region_hi)
        if not r or not r['tris']:
            print(f"  [{idx:02d}] FAIL xp=0x{xp:x}")
            continue
        degen_frac, nan = quality(r['tris'], r['verts'])
        if nan or degen_frac > 0.05:
            print(f"  [{idx:02d}] GATE FAIL degen={degen_frac:.3f} nan={nan}")
            continue
        out = os.path.join(outdir, f"{stem}_{idx:02d}_{len(r['verts'])}v_{len(r['tris'])}t.glb")
        write_glb_fixed(r['verts'], r['uvs'], r['tris'], out)
        print(f"  [{idx:02d}] OK verts={len(r['verts'])} tris={len(r['tris'])} degen={degen_frac:.4f} -> {out}")
        ok += 1
    print(f"{stem}: {ok}/{len(tables)} decoded (incl. pre-existing)")


if __name__ == '__main__':
    main()
