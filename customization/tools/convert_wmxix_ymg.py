#!/usr/bin/env python3
"""convert_wmxix_ymg.py — WMXIX CAW part (.ymg / YOBJ) -> GLB converter.

Creation Suite gap-fill JOB 3 (2026-10-20). Converts the 998 WMXIX
create-a-wrestler part files that customization/tools/convert_caw_parts.py
cataloged as "blocked_ymg_decode" into GLBs under
customization/parts-converted/wmxix/<category>/<...>/<part>.glb and
stamps the converted entries in customization/parts-converted/CATALOG.json.

FORMAT (researched from the in-repo teardown record — no guessing):
  * YOBJ container, big-endian. Header fields used here (all measured in
    teardown/wwe-wrestlemania-xix/docs/WMXIX-TEARDOWN.md v2/v3):
    [0x08] version (0x00030001 x754, 0x00040001 x175, 0x00040002 x32,
    0x00040003 x31, + 6 minor variants), [0x14] skeleton section offset,
    [0x38] GCTC section offset, [0x5C] Table1 offset, [0x60] skin-batch
    table offset, [0x54] data base (0x80).
  * Vertex positions are s16x3 big-endian triplets, scale /64 (GX s16
    with 6 fraction bits), stored as ONE strip-ordered pool that starts
    immediately after the skin-batch descriptor table (header record +
    one 8-byte record per batch + a terminator record with count byte 0)
    and ends at the GCTC section [0x38].
    Ground truth: edit_data Man/Elbow me0_000/l0.ymg -> 145 position
    verts, 14 strips, 113 tris (tools/yobj_strips.py, teardown doc v3;
    the doc's "148 verts" count includes 3 GCTC-header words past the
    pool end, which form no triangles. Reproduced exactly here.)
  * Connectivity: there are NO index buffers. Vertices are triangle-strip
    ordered; strip boundaries are found by the measured edge-length
    bimodality (yobj_strips.py): split where the consecutive-vertex step
    exceeds max(400, 4x median step). Separator verts (near-origin) end
    up as strip ends / dropped short runs.
  * CAW parts are RIGID (one part, no per-vertex skinning in the part's
    own frame), so no skeleton transform is applied — positions are
    exported in the part's native frame at /64 scale, the same
    convention convert_caw_parts.py / convert_no_mercy_parts.py use
    (final rig placement is the bake lane's step).
  * UVs: the source UV streams (Table1/Table2 payloads, 12-bit /4096)
    are NOT yet decoded to a proven per-vertex mapping, and the part's
    decoded texture (parts-converted/wmxix-textures/, Worker A) is named
    in a parallel TEX tree whose per-part assignment is index-based, not
    proven per file. Binding a guessed texture/UV would fake data, so
    GLBs ship with a plain Principled material and NO texture. The
    textures remain available as separate catalog texture parts.

VALIDATION GATE (a file converts only if its pool passes all checks —
the same discipline as Worker A's "no fake GLBs"):
  pool_verts >= 10, >= 85% of consecutive steps <= 700 raw units,
  <= 2% outlier verts (|coord| > 2600), >= 80% of verts land in strips
  of >= 3, >= 4 triangles, <= 5% of triangles with an edge > the split
  threshold, AND — decisive — after welding duplicate positions, >= 75%
  of triangles must sit in ONE connected component. A rigid CAW part is
  a single shell; the 2026-10-20 sample renders (10 parts, Blender
  Workbench, viewed by the converting agent) showed the strip pool
  alone assembles into disconnected fragments (7-44 components, largest
  14-68% of triangles): the per-strip-group placement transform is the
  same unsolved piece documented for wrestler assembly in
  WMXIX-ASSEMBLY-SOLUTION.md / YOBJ-SKINNING-SOLUTION.md, so files that
  fail connectivity keep status "blocked_ymg_decode" with the precise
  reason recorded — no fragment GLBs are shipped as if they were parts.
  NOTE: the numeric gate is necessary, not sufficient — in the
  2026-10-20 batch, 77 files passed every numeric check and were STILL
  revoked after their Blender renders failed eye validation. Any future
  run of this tool must eye-validate renders per class before the
  `catalog` step stamps anything.
  See customization/parts-converted/wmxix-conversion-report.json and
  customization/WORKLOG-WMXIX-YMG.md for the full evidence and the
  next-step research path (DOL ring-buffer reindexing in
  teardown/wwe-wrestlemania-xix/docs/YOBJ-DOL-DECODER-REPORT.md).

Resumable: existing GLBs are skipped (pass --force to redo).
Per-file results are appended to
customization/parts-converted/wmxix-conversion-log.jsonl and summarized
in customization/parts-converted/wmxix-conversion-report.json.

Usage:
  python3 convert_wmxix_ymg.py list [--versions 0x30001,...]
  python3 convert_wmxix_ymg.py convert [--limit N] [--offset K] [--force]
  python3 convert_wmxix_ymg.py catalog     # stamp CATALOG.json from log
  python3 convert_wmxix_ymg.py report      # (re)write the report JSON

Requires: numpy (system python3 has 1.26.4 on this VM).
"""
import glob
import json
import math
import os
import struct
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CUSTOM = os.path.dirname(HERE)                      # customization/
REPO = os.path.dirname(CUSTOM)
PARTS = os.path.join(CUSTOM, 'parts', 'wmxix')
OUT = os.path.join(CUSTOM, 'parts-converted')
OUT_WMXIX = os.path.join(OUT, 'wmxix')
LOG = os.path.join(OUT, 'wmxix-conversion-log.jsonl')
REPORT = os.path.join(OUT, 'wmxix-conversion-report.json')
CATALOG = os.path.join(OUT, 'CATALOG.json')

SCALE = 1.0 / 64.0
OUTLIER = 2600          # raw units; real part coords stay within ~2100
SMOOTH_STEP = 700       # raw units; intra-strip steps are ~50-400


def rel(p):
    return os.path.relpath(p, REPO).replace(os.sep, '/')


def write_retry(path, data_bytes):
    """The VM intermittently returns EPERM on writes (observed 2026-10-20);
    retry with verification instead of corrupting outputs."""
    import time
    for _ in range(60):
        try:
            with open(path, 'wb') as f:
                f.write(data_bytes)
            if os.path.getsize(path) == len(data_bytes):
                return True
        except PermissionError:
            pass
        time.sleep(2)
    raise PermissionError(f'write blocked after retries: {path}')


def u32(d, o):
    return struct.unpack('>I', d[o:o + 4])[0]


# ------------------------------------------------------------------ decode
def decode_ymg(d):
    """Decode one YOBJ file. Returns (verts, tris, metrics) with verts as
    float64 raw-space (N,3) (divide by 64 at export), tris (M,3) int64,
    or (None, None, metrics) when the file carries no decodable pool."""
    m = {'version': None, 'pool_verts': 0}
    if len(d) < 0x80 or d[:4] != b'YOBJ':
        m['reason'] = 'not_yobj_or_tiny'
        return None, None, m
    m['version'] = u32(d, 0x08)
    skel_off = u32(d, 0x14)
    gctc_off = u32(d, 0x38)
    bt = u32(d, 0x60)
    end = gctc_off if 0 < gctc_off <= len(d) else skel_off
    if bt == 0 or bt + 8 > len(d) or end <= bt or end > len(d):
        m['reason'] = 'no_pool_bounds'
        return None, None, m
    # skin-batch table: header record + batch records + terminator (count 0)
    nrec = 1
    for r in range(1, 64):
        rec = d[bt + r * 8:bt + r * 8 + 8]
        if len(rec) < 8:
            break
        nrec += 1
        if rec[1] == 0:
            break
    start = bt + nrec * 8
    n = (end - start) // 6
    if n < 6:
        m['reason'] = f'pool_too_small:{n}'
        return None, None, m
    v = np.frombuffer(d[start:start + n * 6], dtype='>i2').reshape(-1, 3).astype(np.float64)
    steps = np.linalg.norm(v[1:] - v[:-1], axis=1)
    # strip split (yobj_strips.py, measured): TH = max(400, 4 * median step)
    ds = sorted(float(x) for x in steps)
    th = max(400.0, ds[len(ds) // 2] * 4)
    strips = []
    s0 = 0
    for i in [i for i in range(n - 1) if steps[i] > th] + [n - 1]:
        run = list(range(s0, i + 1))
        if len(run) >= 3:
            strips.append(run)
        s0 = i + 1
    tris = []
    for s in strips:
        for i in range(len(s) - 2):
            a, b, c = s[i], s[i + 1], s[i + 2]
            tris.append((a, b, c) if i % 2 == 0 else (b, a, c))
    tris = np.array(tris, dtype=np.int64) if tris else np.zeros((0, 3), dtype=np.int64)
    long_tris = 0
    if len(tris):
        e = np.stack([
            np.linalg.norm(v[tris[:, 0]] - v[tris[:, 1]], axis=1),
            np.linalg.norm(v[tris[:, 1]] - v[tris[:, 2]], axis=1),
            np.linalg.norm(v[tris[:, 2]] - v[tris[:, 0]], axis=1)], axis=1).max(axis=1)
        long_tris = int((e > th).sum())
    used = sum(len(s) for s in strips)
    # welded connectivity: a rigid part is ONE shell. Weld duplicate
    # positions, drop degenerate tris, size the largest component.
    keys = {}
    remap = np.zeros(n, dtype=np.int64)
    for i in range(n):
        k = (int(v[i, 0]), int(v[i, 1]), int(v[i, 2]))
        if k not in keys:
            keys[k] = len(keys)
        remap[i] = keys[k]
    main_frac = 0.0
    if len(tris):
        wt = remap[tris]
        wt = wt[(wt[:, 0] != wt[:, 1]) & (wt[:, 1] != wt[:, 2])
                & (wt[:, 0] != wt[:, 2])]
        if len(wt):
            parent = list(range(len(keys)))

            def find(x):
                while parent[x] != x:
                    parent[x] = parent[parent[x]]
                    x = parent[x]
                return x
            for a, b, c in wt:
                for x, y in ((a, b), (b, c)):
                    ra, rb = find(int(x)), find(int(y))
                    if ra != rb:
                        parent[ra] = rb
            from collections import Counter
            comp = Counter(find(int(a)) for a, _, _ in wt)
            main_frac = comp.most_common(1)[0][1] / len(wt)
    m.update({
        'pool_verts': int(n),
        'smooth_frac': float(np.mean(steps <= SMOOTH_STEP)) if len(steps) else 0.0,
        'outlier_frac': float(np.mean(np.abs(v).max(axis=1) > OUTLIER)),
        'used_frac': used / n if n else 0.0,
        'strips': len(strips),
        'tris': int(len(tris)),
        'long_tri_frac': (long_tris / len(tris)) if len(tris) else 1.0,
        'split_threshold': th,
        'main_component_frac': float(main_frac),
    })
    return v, tris, m


def gate(m):
    if m.get('reason'):
        return False, m['reason']
    if m['pool_verts'] < 10:
        return False, f"pool_too_small:{m['pool_verts']}"
    if m['smooth_frac'] < 0.85:
        return False, f"pool_steps_incoherent:{m['smooth_frac']:.2f}"
    if m['outlier_frac'] > 0.02:
        return False, f"outlier_segments:{m['outlier_frac']:.2f}"
    if m['used_frac'] < 0.80:
        return False, f"strip_coverage_low:{m['used_frac']:.2f}"
    if m['tris'] < 4:
        return False, f"too_few_tris:{m['tris']}"
    if m['long_tri_frac'] > 0.05:
        return False, f"long_edge_tris:{m['long_tri_frac']:.2f}"
    if m['main_component_frac'] < 0.75:
        return False, f"fragmented_assembly:{m['main_component_frac']:.2f}"
    return True, 'ok'


# --------------------------------------------------------------------- GLB
def write_glb(path, verts, tris, name):
    """Deterministic glTF 2.0 binary: POSITION + computed NORMAL + indices,
    one Principled material (no texture — see module docstring)."""
    used = sorted({int(i) for t in tris for i in t})
    remap = {o: i for i, o in enumerate(used)}
    vv = (verts[used] * SCALE).astype(np.float32)
    tt = np.array([[remap[int(a)], remap[int(b)], remap[int(c)]] for a, b, c in tris],
                  dtype=np.uint32)
    nrm = np.zeros_like(vv)
    if len(tt):
        f0, f1, f2 = vv[tt[:, 0]], vv[tt[:, 1]], vv[tt[:, 2]]
        fn = np.cross(f1 - f0, f2 - f0)
        for i in range(3):
            np.add.at(nrm, tt[:, i], fn)
    ln = np.linalg.norm(nrm, axis=1, keepdims=True)
    ln[ln == 0] = 1
    nrm = (nrm / ln).astype(np.float32)

    bin_parts, views, accessors = [], [], []

    def add_view(data, target):
        off = sum(len(p) for p in bin_parts)
        bin_parts.append(data + b'\x00' * ((-len(data)) % 4))
        views.append({'buffer': 0, 'byteOffset': off, 'byteLength': len(data),
                      'target': target})
        return len(views) - 1

    iv = add_view(tt.tobytes(), 34963)
    accessors.append({'bufferView': iv, 'componentType': 5125,
                      'count': int(tt.size), 'type': 'SCALAR'})
    pv = add_view(vv.tobytes(), 34962)
    accessors.append({'bufferView': pv, 'componentType': 5126, 'count': len(vv),
                      'type': 'VEC3', 'min': vv.min(axis=0).tolist(),
                      'max': vv.max(axis=0).tolist()})
    nv = add_view(nrm.tobytes(), 34962)
    accessors.append({'bufferView': nv, 'componentType': 5126, 'count': len(vv),
                      'type': 'VEC3'})
    gltf = {
        'asset': {'version': '2.0',
                  'generator': 'customization/tools/convert_wmxix_ymg.py'},
        'scene': 0, 'scenes': [{'nodes': [0]}],
        'nodes': [{'mesh': 0, 'name': name}],
        'meshes': [{'name': name, 'primitives': [{
            'attributes': {'POSITION': 1, 'NORMAL': 2}, 'indices': 0,
            'material': 0}]}],
        'materials': [{'name': 'part_mat',
                       'pbrMetallicRoughness': {'metallicFactor': 0.0,
                                                'roughnessFactor': 0.9},
                       'doubleSided': True}],
        'bufferViews': views, 'accessors': accessors,
        'buffers': [{'byteLength': sum(len(p) for p in bin_parts)}],
    }
    js = json.dumps(gltf, separators=(',', ':')).encode()
    js += b' ' * ((-len(js)) % 4)
    bin_data = b''.join(bin_parts)
    total = 12 + 8 + len(js) + 8 + len(bin_data)
    out = struct.pack('<III', 0x46546C67, 2, total)
    out += struct.pack('<II', len(js), 0x4E4F534A) + js
    out += struct.pack('<II', len(bin_data), 0x004E4942) + bin_data
    os.makedirs(os.path.dirname(path), exist_ok=True)
    write_retry(path, out)
    return len(out), len(vv), len(tt)


# ------------------------------------------------------------------- batch
def ymg_files():
    return sorted(glob.glob(os.path.join(PARTS, '**', '*.ymg'), recursive=True))


def glb_path_for(src):
    sub = os.path.relpath(src, PARTS)                       # <cat>/<...>.ymg
    return os.path.join(OUT_WMXIX, os.path.splitext(sub)[0] + '.glb')


def logged():
    done = {}
    if os.path.exists(LOG):
        for line in open(LOG):
            try:
                r = json.loads(line)
            except Exception:
                continue
            done[r['origin_file']] = r
    return done


def log(rec):
    os.makedirs(OUT, exist_ok=True)
    line = (json.dumps(rec) + '\n').encode()
    for _ in range(60):
        try:
            with open(LOG, 'a') as f:
                f.write(line.decode())
            return
        except PermissionError:
            import time
            time.sleep(2)
    raise PermissionError(f'log write blocked: {LOG}')


def run_convert(limit=None, offset=0, force=False):
    done = logged()
    files = ymg_files()
    todo = files[offset:offset + limit if limit else None]
    n_ok = n_fail = n_skip = 0
    for src in todo:
        origin = rel(src)
        dst = glb_path_for(src)
        if not force and origin in done and done[origin].get('status') == 'converted' \
                and os.path.exists(dst):
            n_skip += 1
            continue
        d = open(src, 'rb').read()
        if d[:4] == b'DUMY':
            log({'origin_file': origin, 'status': 'blocked_dumy_placeholder',
                 'detail': 'DUMY placeholder — no geometry by design'})
            n_skip += 1
            continue
        v, tris, m = decode_ymg(d)
        ok, reason = gate(m)
        if not ok:
            log({'origin_file': origin, 'status': 'blocked_ymg_decode',
                 'detail': reason, 'metrics': {k: m[k] for k in
                          ('version', 'pool_verts', 'smooth_frac',
                           'outlier_frac', 'used_frac', 'tris', 'long_tri_frac',
                           'main_component_frac')
                          if k in m}})
            n_fail += 1
            continue
        size, nv, nt = write_glb(dst, v, tris, os.path.splitext(os.path.basename(src))[0])
        log({'origin_file': origin, 'status': 'converted', 'glb': rel(dst),
             'verts': nv, 'tris': nt, 'glb_bytes': size,
             'version': m['version'], 'pool_verts': m['pool_verts'],
             'strips': m['strips']})
        n_ok += 1
    print(f'convert: ok={n_ok} failed_gate={n_fail} skipped={n_skip} '
          f'(window offset={offset} limit={limit})')
    return n_ok, n_fail, n_skip


def run_catalog():
    done = logged()
    cat = json.load(open(CATALOG))
    n = 0
    for e in cat['parts']:
        r = done.get(e['origin_file'])
        if r and r.get('status') == 'converted' and e.get('status') == 'blocked_ymg_decode':
            e['glb'] = r['glb']
            e['status'] = 'converted'
            n += 1
    write_retry(CATALOG, (json.dumps(cat, indent=1) + '\n').encode())
    print(f'catalog: stamped {n} entries converted; total entries={cat["count"]}')


def run_report():
    done = logged()
    from collections import Counter
    by_status = Counter(r.get('status') for r in done.values())
    by_ver = Counter()
    fail_reasons = Counter()
    for r in done.values():
        if r.get('status') == 'converted':
            by_ver[hex(r['version'])] += 1
        elif r.get('status') == 'blocked_ymg_decode':
            fail_reasons[(r.get('detail') or '').split(':')[0]] += 1
    rep = {
        'tool': 'customization/tools/convert_wmxix_ymg.py',
        'generated': '2026-10-20',
        'summary': dict(by_status),
        'converted_by_yobj_version': dict(by_ver),
        'blocked_reasons': dict(fail_reasons),
        'notes': [
            'Decode: s16x3 BE pool after the skin-batch table, /64 scale, '
            'strip split at max(400, 4x median step) (yobj_strips.py '
            'lineage; elbow ground truth 145 position verts / 14 strips / '
            '113 tris reproduced).',
            'Gate failures stay blocked_ymg_decode with the reason in '
            'wmxix-conversion-log.jsonl. Dominant final-gate reason is '
            'fragmented_assembly: strip fragments are internally coherent '
            '(measured per-strip planarity, rail structure) but are not in '
            'one shared frame — welded meshes split into 7-44 components '
            '(largest 14-68% of triangles). Sample Blender renders viewed '
            'by the converting agent confirm fragments, not parts.',
            'The missing piece is the per-strip-group placement transform '
            '(the same open problem as wrestler assembly; see '
            'teardown/wwe-wrestlemania-xix/docs/WMXIX-ASSEMBLY-SOLUTION.md '
            'claims vs YOBJ-DOL-DECODER-REPORT.md ground truth). Next-step '
            'path is documented in customization/WORKLOG-WMXIX-YMG.md.',
            'No texture bound: source per-vertex UV mapping is undecoded '
            'and the TEX-tree assignment is index-based, not per-file '
            'proven; textures remain separate converted catalog parts.',
        ],
        'results': done,
    }
    write_retry(REPORT, (json.dumps(rep, indent=1) + '\n').encode())
    print('report:', dict(by_status), 'by version:', dict(by_ver),
          'fail reasons:', dict(fail_reasons))


def run_list():
    from collections import Counter
    vers = Counter()
    for src in ymg_files():
        d = open(src, 'rb').read()
        if d[:4] == b'YOBJ' and len(d) >= 0x80:
            vers[hex(u32(d, 8))] += 1
        elif d[:4] == b'DUMY':
            vers['DUMY'] += 1
        else:
            vers['tiny/other'] += 1
    print('ymg files:', dict(vers), 'total:', sum(vers.values()))


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'list'
    force = '--force' in sys.argv
    limit = offset = None
    for a in sys.argv[2:]:
        if a.startswith('--limit='):
            limit = int(a.split('=')[1])
        if a.startswith('--offset='):
            offset = int(a.split('=')[1])
    if cmd == 'list':
        run_list()
    elif cmd == 'convert':
        run_convert(limit=limit, offset=offset or 0, force=force)
    elif cmd == 'catalog':
        run_catalog()
    elif cmd == 'report':
        run_report()
    else:
        print(__doc__)
        sys.exit(2)
