#!/usr/bin/env python3
"""Urban Reign char PPK -> xyz-run census OBJs (geometry decode work-in-progress).

PROVEN (2026-10-13, char001.ppk):
  - Header tag table at 0x20: null-terminated u32 entries, (type<<16)|offset.
  - Normal vectors: float32 xyz runs with EXACT unit length (1.000).
  - Bone-name ASCII strings (with __L_/__R_ pairs) live near mesh data.
  - Identity quats (bind pose) at ~0x660.
  - Mesh pre-headers: float chunks with 0x00008004/0x00008014 markers + 128.0 quads.

NOT PROVEN: vertex positions, index buffers, UVs, textures, mesh assembly.
  The non-normal xyz runs are mostly denormal/zero floats (integer data or
  sparse records misread as float) — they are NOT vertex positions.
  The big s16 region @0x2971 (344KB) is not plain s16 positions at any stride
  (no spatial coherence; bbox always full +-32768). Position decode is open.

Usage: ur_extract_meshes.py <charXXX.ppk> <outdir>
"""
import struct, sys, os, json, re, math

def find_position_runs(d):
    """Scan for runs of plausible float32 xyz triplets (|v|<=3, non-degenerate).
    Classifies each run: 'normals' if all unit-length, else 'xyz_unclassified'."""
    n = len(d)
    runs = []
    i = 0
    while i < n - 12:
        if i % 4:
            i += 1
            continue
        x, y, z = struct.unpack('<3f', d[i:i+12])
        if abs(x) <= 3.0 and abs(y) <= 3.0 and abs(z) <= 3.0:
            j, pts = i, []
            while j < n - 12:
                x, y, z = struct.unpack('<3f', d[j:j+12])
                if not (abs(x) <= 3.0 and abs(y) <= 3.0 and abs(z) <= 3.0):
                    break
                pts.append((x, y, z))
                j += 12
            if len(pts) >= 50:
                # reject degenerate runs (all zeros / near-zero volume)
                xs = [p[0] for p in pts]; ys = [p[1] for p in pts]; zs = [p[2] for p in pts]
                span = max(max(xs)-min(xs), max(ys)-min(ys), max(zs)-min(zs))
                if span > 0.05:
                    unit = all(abs(math.sqrt(x*x+y*y+z*z) - 1.0) < 0.01 for x, y, z in pts)
                    # non-unit xyz runs are NOT proven positions (mostly denormal/
                    # zero floats); label them by what they are: unclassified.
                    runs.append((i, pts, 'normals' if unit else 'xyz_unclassified'))
            i = j
        else:
            i += 4
    return runs

def find_bone_names(d):
    """ASCII strings >=4 chars containing __L_ or __R_ (or long alpha runs)."""
    out = []
    for m in re.finditer(rb'[\x20-\x7e]{4,}', d):
        s = m.group().decode('ascii')
        if '__L_' in s or '__R_' in s or len(s) >= 12:
            out.append((m.start(), s))
    return out

def main():
    ppk_path, outdir = sys.argv[1], sys.argv[2]
    os.makedirs(outdir, exist_ok=True)
    d = open(ppk_path, 'rb').read()
    name = os.path.splitext(os.path.basename(ppk_path))[0]
    manifest = {'ppk': os.path.basename(ppk_path), 'size': len(d), 'meshes': []}
    runs = find_position_runs(d)
    print(f'{name}: {len(runs)} xyz runs found')
    for k, (off, pts, kind) in enumerate(runs):
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]; zs = [p[2] for p in pts]
        bbox = [[min(xs), min(ys), min(zs)], [max(xs), max(ys), max(zs)]]
        obj = os.path.join(outdir, f'{name}_{kind}{k:02d}.obj')
        with open(obj, 'w') as f:
            f.write(f'# {name} {kind} {k} @ {hex(off)} — point cloud (indices TBD)\n')
            for x, y, z in pts:
                f.write(f'v {x:.6f} {y:.6f} {z:.6f}\n')
        manifest['meshes'].append({'part': k, 'kind': kind, 'offset': hex(off),
                                   'verts': len(pts), 'bbox': bbox, 'obj': os.path.basename(obj)})
        print(f'  {kind:9s}{k:02d} @{hex(off)} verts={len(pts)} '
              f'bbox x[{bbox[0][0]:.2f},{bbox[1][0]:.2f}] '
              f'y[{bbox[0][1]:.2f},{bbox[1][1]:.2f}] z[{bbox[0][2]:.2f},{bbox[1][2]:.2f}]')
    bones = find_bone_names(d)
    manifest['bone_name_strings'] = [{'offset': hex(o), 'name': s} for o, s in bones[:200]]
    print(f'  bone-name strings: {len(bones)}')
    json.dump(manifest, open(os.path.join(outdir, f'{name}_manifest.json'), 'w'), indent=1)
    print('manifest written')

if __name__ == '__main__':
    main()
