#!/usr/bin/env python3
"""W6: WMXIX arena facing — turn bg/*.ymg point clouds into faced OBJs.

Methods (in order):
  A. 20-byte index records (CRACKED 2026-10-13): [u16 a][u16 b][u16 c]
     [u32 FFFFFFFF][u16 base][u16 d][u16 e][u32 FFFFFFFF]; tri=(b+base,
     c+base, e+base). Validated by edge length.
  B. Plain u16 index runs (multiples of 3), tried as global indices AND as
     per-array indices (base = each vert array's global start). Every
     candidate triangle is geometrically validated (2 smallest edges
     < MAX_EDGE) before acceptance, so garbage runs self-reject.
  C. (fallback, not yet implemented) Blender Poisson reconstruction.

Reads .ymg bytes from /data/wmxix/extracted/bg/ (local files, no ISO stream).
Writes faced OBJs to /data/wmxix/out/arena-faced/ + arena-manifest.json.
"""
import sys, os, struct, math, json
sys.path.insert(0, '/data/wmxix/tools-src/tools')
from yobj_arena_extract import find_vert_arrays

BG = '/data/wmxix/extracted/bg'
OUT = '/data/wmxix/out/arena-faced'
MAX_EDGE = 200.0  # arena verts span ~5000 units; real edges are small


def u16(d, o):
    return struct.unpack('>H', d[o:o + 2])[0]


def f32(d, o):
    return struct.unpack('>f', d[o:o + 4])[0]


def edge_ok(verts, a, b, c):
    """True if the 2 smallest edges are < MAX_EDGE (kills garbage tris)."""
    def el(p, q):
        return math.sqrt(sum((x - y) ** 2 for x, y in zip(verts[p], verts[q])))
    l = sorted((el(a, b), el(b, c), el(c, a)))
    return l[0] < MAX_EDGE and l[1] < MAX_EDGE


def method_a(data, size, verts, varray_ranges):
    """20-byte records."""
    NV = len(verts)

    def in_varray(o):
        for s, e in varray_ranges:
            if s - 20 <= o < e:
                return True
        return False

    tris = []
    o = 0x80
    while o < size - 20:
        if in_varray(o):
            o += 2
            continue
        b, c = u16(data, o + 2), u16(data, o + 4)
        sep1 = struct.unpack('>I', data[o + 6:o + 10])[0]
        base, e = u16(data, o + 10), u16(data, o + 14)
        sep2 = struct.unpack('>I', data[o + 16:o + 20])[0]
        if sep1 == 0xFFFFFFFF and sep2 == 0xFFFFFFFF:
            B, C, E = b + base, c + base, e + base
            if B < NV and C < NV and E < NV and len({B, C, E}) == 3:
                if edge_ok(verts, B, C, E):
                    tris.append((B, C, E))
                    o += 20
                    continue
        o += 2
    return tris


def method_b(data, size, verts, array_bases):
    """Plain u16 index runs. Each run is tried globally and per-array;
    the interpretation with the most geometrically-valid triangles wins
    (a run must validate >=50% of its triangles to be accepted at all)."""
    NV = len(verts)
    tris = []
    o = 0x80
    while o < size - 22:
        vals = [u16(data, o + i * 2) for i in range(10)]
        if all(v < NV for v in vals) and any(v > 0 for v in vals):
            e = o
            while e + 2 < size and u16(data, e) < NV:
                e += 2
                if e - o > 200000:
                    break
            n = (e - o) // 2
            if n >= 6 and n % 3 == 0:
                idx = [u16(data, o + i * 2) for i in range(n)]
                # global interpretation
                g = [(idx[i], idx[i + 1], idx[i + 2])
                     for i in range(0, n, 3)
                     if len({idx[i], idx[i + 1], idx[i + 2]}) == 3]
                gv = [t for t in g if edge_ok(verts, *t)]
                best, best_n = gv, len(gv)
                # per-array interpretations
                for base in array_bases:
                    p = [(idx[i] + base, idx[i + 1] + base,
                          idx[i + 2] + base) for i in range(0, n, 3)
                         if len({idx[i], idx[i + 1], idx[i + 2]}) == 3
                         and idx[i] + base < NV and idx[i + 1] + base < NV
                         and idx[i + 2] + base < NV]
                    pv = [t for t in p if edge_ok(verts, *t)]
                    if len(pv) > best_n:
                        best, best_n = pv, len(pv)
                if best_n >= max(2, (n // 3) // 2):
                    tris.extend(best)
                o = e
                continue
        o += 2
    return tris


def face_arena(name):
    path = os.path.join(BG, name)
    with open(path, 'rb') as f:
        data = f.read()
    size = len(data)
    arrays = find_vert_arrays(data, size)
    verts = []
    array_bases = []
    for start, n in arrays:
        array_bases.append(len(verts))
        for i in range(n):
            verts.append((f32(data, start + i * 12),
                          f32(data, start + i * 12 + 4),
                          f32(data, start + i * 12 + 8)))
    varray_ranges = [(s, s + n * 12) for s, n in arrays]
    ta = method_a(data, size, verts, varray_ranges)
    tb = method_b(data, size, verts, array_bases)
    # merge + dedupe (canonical orientation-independent key)
    seen = set()
    tris = []
    for t in ta + tb:
        k = tuple(sorted(t))
        if k not in seen:
            seen.add(k)
            tris.append(t)
    covered = set()
    for t in tris:
        covered.update(t)
    return {'name': name, 'size': size, 'arrays': len(arrays),
            'verts': len(verts), 'faces_a': len(ta), 'faces_b': len(tb),
            'faces': len(tris),
            'coverage': len(covered) / max(1, len(verts))}, verts, tris


def write_obj(name, verts, tris):
    os.makedirs(OUT, exist_ok=True)
    out = os.path.join(OUT, name.replace('.ymg', '.obj'))
    with open(out, 'w') as f:
        f.write(f'# {name} - WMXIX arena, faced (W6)\n')
        f.write(f'# {len(verts)} verts, {len(tris)} faces\n')
        for x, y, z in verts:
            f.write(f'v {x:.2f} {y:.2f} {z:.2f}\n')
        for a, b, c in tris:
            f.write(f'f {a + 1} {b + 1} {c + 1}\n')
    return out


def main():
    targets = sys.argv[1:] or ['ring.ymg']
    manifest = {}
    for name in targets:
        try:
            info, verts, tris = face_arena(name)
        except FileNotFoundError:
            print(f'{name}: not in {BG}')
            continue
        manifest[name] = info
        if tris:
            write_obj(name, verts, tris)
        print(f"{name}: {info['verts']} verts, {info['faces']} faces "
              f"(A={info['faces_a']} B={info['faces_b']}), "
              f"coverage={info['coverage']:.1%}")
    if len(targets) > 1 or targets == ['all']:
        with open(os.path.join(OUT, 'arena-manifest.json'), 'w') as f:
            json.dump(manifest, f, indent=1, sort_keys=True)


if __name__ == '__main__':
    if sys.argv[1:] == ['all']:
        names = sorted(n for n in os.listdir(BG) if n.endswith('.ymg'))
        sys.argv = [sys.argv[0]] + names
    main()
