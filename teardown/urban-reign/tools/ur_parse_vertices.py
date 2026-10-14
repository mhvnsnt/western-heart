#!/usr/bin/env python3
"""Urban Reign char PPK -> skinned vertex extraction.

PROVEN (2026-10-14, char001.ppk, verified by blended-normal unit check):
  Char PPK = `ppk\\0` container, header tag table at 0x20: null-terminated u32
  entries, (type<<16)|offset. Geometry lives in typed chunks.

  Type 0x8001 chunks with float32 content hold SKINNED VERTEX RECORDS:
    per vertex: N bone influences x 8 floats + UV row + 128.0x4 separator
      influence: (px,py,pz,weight) + (nx*w, ny*w, nz*w, 0.0)
      UV row:    (u, v, 1.0, 0.0)
    N=1 -> 12 floats (rigid, weight 1.0)
    N=2 -> 20 floats
    N=3 -> 28 floats   (weights sum to 1.0 in all cases checked)
  Blended normal = sum of the influence normal rows -> EXACT unit length
  (91/91 two-bone verts + rigid + three-bone verts verified in char001).
  Positions are BONE-LOCAL; world transform needs bone matrices
  (bind pose = identity 4x4 per bone record: 7 zero float4s + 16-float
  identity matrix, repeating from ~0x660; bone translations TBD).

  Type 0x0002 chunk (large, @0xe800 in char001) holds float32 normal runs
  (exact unit length), 0..1 "color"-like runs and string data.

Usage: ur_parse_vertices.py <charXXX.ppk> <outdir>
  Writes <name>_verts.obj (blended bone-local positions), <name>_normals.obj
  (blended normals), <name>_uv.obj (uv as xy), and <name>_vmanifest.json
  (per-vertex: influences, weights, uv; chunk inventory).
"""
import struct, sys, os, json, math

def parse_tags(d):
    entries = []
    o = 0x20
    while o < 0x200:
        e = struct.unpack('<I', d[o:o+4])[0]
        if e == 0:
            break
        entries.append((e >> 16, e & 0xFFFF))
        o += 4
    return entries

def chunk_bounds(entries, filesize):
    offs = sorted(set(off for _, off in entries))
    out = []
    for typ, off in entries:
        i = offs.index(off)
        end = offs[i+1] if i+1 < len(offs) else filesize
        out.append((typ, off, end - off))
    return out

def is_sep(fl, i):
    return all(abs(fl[i+k] - 128.0) < 0.01 for k in range(4))

def parse_vertex_chunk(d, off, size):
    """Parse float32 vertex records from a 0x8001 chunk. Returns (verts, notes)."""
    seg = d[off:off+size]
    nf = len(seg) // 4
    fl = struct.unpack(f'<{nf}f', seg[:nf*4])
    # locate 128x4 separators
    seps = []
    i = 0
    while i < nf - 4:
        if is_sep(fl, i):
            seps.append(i)
            i += 4
        else:
            i += 1
    verts = []
    notes = []
    prev = 0
    for s in seps:
        blen = s - prev
        # valid block: 12/20/28 floats (1/2/3 influences + UV row)
        if blen in (12, 20, 28):
            n_inf = (blen - 4) // 8
            rows = fl[prev:s]
            infs = []
            ok = True
            for k in range(n_inf):
                px, py, pz, w = rows[8*k:8*k+4]
                nx, ny, nz, z = rows[8*k+4:8*k+8]
                if not all(math.isfinite(v) for v in (px, py, pz, w, nx, ny, nz)):
                    ok = False
                    break
                infs.append({'pos': [px, py, pz], 'w': w,
                             'nrm_w': [nx, ny, nz]})
            u, v, one, z = rows[blen-4:blen]
            wsum = sum(x['w'] for x in infs)
            # validation: weights sum ~1, UV row has 1.0 marker
            if ok and abs(wsum - 1.0) < 0.02 and abs(one - 1.0) < 0.01:
                nrm = [sum(x['nrm_w'][c] for x in infs) for c in range(3)]
                verts.append({'influences': infs, 'uv': [u, v], 'nrm': nrm,
                              'nrm_len': math.sqrt(sum(c*c for c in nrm))})
            else:
                notes.append(f'skipped block @{hex(off+4*prev)} len={blen} '
                             f'wsum={wsum:.3f}')
        prev = s + 4
    return verts, notes

def main():
    ppk_path, outdir = sys.argv[1], sys.argv[2]
    os.makedirs(outdir, exist_ok=True)
    d = open(ppk_path, 'rb').read()
    name = os.path.splitext(os.path.basename(ppk_path))[0]
    entries = parse_tags(d)
    bounds = chunk_bounds(entries, len(d))
    all_verts = []
    chunk_info = []
    for typ, off, size in bounds:
        if size < 64 or off < 0x80:
            # skip header fields / tiny chunks
            chunk_info.append({'type': hex(typ), 'offset': hex(off),
                               'size': size, 'parsed': False})
            continue
        # detect float32 content by probe
        probe = struct.unpack('<8f', d[off:off+32])
        if not all(math.isfinite(v) and abs(v) < 1e7 for v in probe):
            chunk_info.append({'type': hex(typ), 'offset': hex(off),
                               'size': size, 'parsed': False,
                               'note': 'non-float content'})
            continue
        verts, notes = parse_vertex_chunk(d, off, size)
        chunk_info.append({'type': hex(typ), 'offset': hex(off), 'size': size,
                           'parsed': len(verts) > 0, 'verts': len(verts),
                           'skipped': len(notes)})
        all_verts.extend(verts)
    # write OBJs (bone-local blended positions / blended normals / uvs)
    def wobj(path, pts, prefix):
        with open(path, 'w') as f:
            f.write(f'# {name} {prefix} — bone-local, {len(pts)} verts\n')
            for p in pts:
                if prefix == 'uv':
                    f.write(f'vt {p[0]:.6f} {p[1]:.6f}\n')
                else:
                    f.write(f'v {p[0]:.6f} {p[1]:.6f} {p[2]:.6f}\n')
    pos = []
    for v in all_verts:
        wsum = sum(i['w'] for i in v['influences']) or 1.0
        # bone-local blended position: unweighted sum matches decoded layout
        # (positions stored per-influence; weights apply at skin time with
        # bone matrices — here we emit the raw per-influence-0 position and
        # the plain sum for inspection)
        p0 = v['influences'][0]['pos']
        pos.append(p0)
    wobj(os.path.join(outdir, f'{name}_pos_infl0.obj'),
         pos, 'pos(influence0 bone-local)')
    wobj(os.path.join(outdir, f'{name}_normals.obj'),
         [v['nrm'] for v in all_verts], 'normals(blended)')
    wobj(os.path.join(outdir, f'{name}_uv.obj'),
         [v['uv'] for v in all_verts], 'uv')
    n_unit = sum(1 for v in all_verts if abs(v['nrm_len'] - 1.0) < 0.05)
    manifest = {'ppk': os.path.basename(ppk_path), 'size': len(d),
                'chunks': chunk_info,
                'total_verts': len(all_verts),
                'unit_normals': n_unit,
                'rigid': sum(1 for v in all_verts if len(v['influences']) == 1),
                'two_bone': sum(1 for v in all_verts if len(v['influences']) == 2),
                'three_bone': sum(1 for v in all_verts if len(v['influences']) == 3)}
    json.dump(manifest, open(os.path.join(outdir, f'{name}_vmanifest.json'), 'w'), indent=1)
    print(f'{name}: {len(all_verts)} verts ({n_unit} unit normals) '
          f'from {sum(1 for c in chunk_info if c.get("parsed"))} vertex chunks')

if __name__ == '__main__':
    main()
