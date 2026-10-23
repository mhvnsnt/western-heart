#!/usr/bin/env python3
"""Tekken 6 PSP round-13 batches.

Job 2 (stage): enumerate every slot of the 16 stage/object packages
from the round-10 inventory; run the round-9 NDPP decoder on every
NDPP section; write stage GLBs for any section that decodes.

Job 3 (parts): stream the entry-87 slice of the CLEAN bulk in bulk
order; for every container the round-11 B3 assignment classes as
boned-part or rigid-part, decode every NDPP slot with the round-9
decoder and write one GLB per package-section under
<out>/seg{NN}/. Failures are recorded per package with the decoder's
reason and the offending VTYPE when one can be isolated.

Usage:
  r13_batches.py stage <decoded76_dir> <out_dir> <inventory_json>
  r13_batches.py parts <bulk_bin> <assignment_json> <out_dir> <manifest_json>
"""
import struct, sys, os, json, zlib, glob, hashlib, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib.util
_spec = importlib.util.spec_from_file_location(
    'r9', os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       'r9_ndpp_decode.py'))
r9 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(r9)

STAGE_IDX = [24, 26, 28, 30, 32, 34, 36, 38, 40, 42, 44, 46, 48, 50, 52, 54]


def slots_of(data):
    n, hs = struct.unpack_from('<II', data, 0)
    if n > 64 or hs > len(data) or 8 + n * 8 > len(data):
        return []
    out = []
    start = hs
    for i in range(n):
        sz, end = struct.unpack_from('<II', data, 8 + i * 8)
        out.append({'slot': i, 'off': start, 'size': sz,
                    'magic': data[start:start + 4].decode('latin1') if sz else ''})
        start = end if end else start
    return out


def get_slot(data, k):
    n, hs = struct.unpack_from('<II', data, 0)
    start = hs
    for i in range(n):
        sz, end = struct.unpack_from('<II', data, 8 + i * 8)
        if i == k:
            return data[start:start + sz]
        start = end if end else start
    return b''


def bad_vtype(sec):
    """Return the first VTYPE whose layout the r9 decoder cannot size."""
    for u in r9.parse_units(sec):
        vt = u['hdr'][2] & 0xffffff
        try:
            r9.vtype_layout(vt)
        except Exception:
            return vt
    return None


def stage(decoded76, out_dir, inv_path):
    os.makedirs(out_dir, exist_ok=True)
    inv = {'packages': []}
    for idx in STAGE_IDX:
        f = sorted(glob.glob(os.path.join(decoded76, f'idx{idx:02d}_*.bin')))[0]
        data = open(f, 'rb').read()
        pkg = {'idx': idx, 'file': os.path.basename(f), 'size': len(data),
               'slots': [], 'ndpp_decoded': [], 'ndpp_failures': []}
        for s in slots_of(data):
            if s['size'] == 0:
                continue
            sec = get_slot(data, s['slot'])
            entry = {'slot': s['slot'], 'size': s['size'], 'magic': s['magic'],
                     'ndpp_occurrences': sec.count(b'NDPP'),
                     'ntpp_occurrences': sec.count(b'NTPP')}
            pkg['slots'].append(entry)
            if s['magic'] != 'NDPP':
                entry['ndpp_decode'] = 'not an NDPP section (magic above)'
                continue
            try:
                verts, tris, nrms, uvs, wgts, desc = r9.decode_mesh(sec)
            except Exception as e:
                vt = bad_vtype(sec)
                pkg['ndpp_failures'].append(
                    {'slot': s['slot'],
                     'reason': f'{type(e).__name__}: {e}'[:120],
                     'bad_vtype': hex(vt) if vt is not None else None,
                     'units_found': len(r9.parse_units(sec))})
                entry['ndpp_decode'] = 'FAILED (see ndpp_failures)'
                continue
            out = os.path.join(out_dir, f"idx{idx:02d}_slot{s['slot']}_r13.glb")
            r9.write_glb(out, verts, tris, nrms, f"idx{idx:02d}_slot{s['slot']}")
            pkg['ndpp_decoded'].append(
                {'slot': s['slot'], 'verts': len(verts), 'tris': len(tris),
                 'glb': os.path.basename(out)})
            entry['ndpp_decode'] = 'decoded'
        inv['packages'].append(pkg)
        print(f"stage idx{idx:02d}: slots={len(pkg['slots'])} "
              f"decoded={pkg['ndpp_decoded']} failures={pkg['ndpp_failures']}")
    json.dump(inv, open(inv_path, 'w'), indent=1)
    print('wrote', inv_path)


def parts(bulk_path, assignment_path, out_dir, manifest_path):
    assign = json.load(open(assignment_path))
    amap = {a['n']: a for a in assign['assignments']}
    OFF = 38592 * 2048
    SIZE = 81591641
    with open(bulk_path, 'rb') as f:
        f.seek(OFF)
        data = f.read(SIZE)
    print('slice bytes', len(data))
    os.makedirs(out_dir, exist_ok=True)
    manifest = {'source_bulk': 'bulk_decrypted_r6.bin (CLEAN, round 6 verified)',
                'slice': {'offset': OFF, 'size': SIZE},
                'assignment': 'round11-evidence/r11_b3_assignment.json',
                'confidence_note': 'segment assignment for slice parts is '
                                   'contiguity-INFERRED (round 11); anchor '
                                   'packages are anchor-proven. No fighter '
                                   'names are claimed for segments.',
                'segments': {}, 'totals': {}}
    seg_stats = {}
    fails_by_reason = {}
    t0 = time.time()
    i = 0
    idx = 0
    total_glb_bytes = 0
    while True:
        j = data.find(b'GZIP', i)
        if j < 0:
            break
        i = j + 4
        if j + 20 > len(data):
            continue
        w = struct.unpack('<5I', data[j:j + 20])
        if not (w[1] == 1 and w[2] == 1 and 0 < w[4] <= len(data) - j - 20
                and 0 < w[3] < 50_000_000):
            continue
        body = data[j + 20:j + 20 + w[4]]
        if body[:2] != b'\x78\xda':
            continue
        try:
            out = zlib.decompress(body)
        except Exception:
            continue
        if len(out) != w[3] or zlib.adler32(out) != struct.unpack('>I', body[-4:])[0]:
            continue
        a = amap.get(idx)
        if a and a['class'] in ('boned-part', 'rigid-part'):
            seg = a['segment']
            st = seg_stats.setdefault(seg, {
                'segment': seg, 'packages': 0, 'sections_decoded': 0,
                'sections_failed': 0, 'verts': 0, 'tris': 0,
                'glb_bytes': 0, 'glbs': [], 'failures': []})
            st['packages'] += 1
            # slot parse (type-A directory, 13 slots)
            if len(out) >= 8:
                cnt, hs = struct.unpack_from('<II', out, 0)
                if cnt == 13 and hs in (8 + 8 * cnt, 16 + 8 * cnt):
                    pairs = [struct.unpack_from('<II', out, 8 + k * 8)
                             for k in range(cnt)]
                    pos = hs
                    for k, (s, e) in enumerate(pairs):
                        if s and out[pos:pos + 4] == b'NDPP':
                            sec = out[pos:pos + s]
                            name = f'bulk{idx:04d}_slot{k}_r13.glb'
                            path = os.path.join(out_dir, f'seg{seg:02d}', name)
                            try:
                                verts, tris, nrms, uvs, wgts, desc = \
                                    r9.decode_mesh(sec)
                            except Exception as ex:
                                vt = bad_vtype(sec)
                                reason = (f'{type(ex).__name__}: {ex}'[:100]
                                          + (f' (bad VTYPE {vt:#x})'
                                             if vt is not None else ''))
                                st['sections_failed'] += 1
                                st['failures'].append(
                                    {'bulk': idx, 'slot': k, 'reason': reason})
                                key = reason.split(' (bad')[0]
                                fails_by_reason[key] = \
                                    fails_by_reason.get(key, 0) + 1
                            else:
                                os.makedirs(os.path.dirname(path), exist_ok=True)
                                r9.write_glb(path, verts, tris, nrms,
                                             f'bulk{idx:04d}_slot{k}')
                                sz = os.path.getsize(path)
                                total_glb_bytes += sz
                                st['sections_decoded'] += 1
                                st['verts'] += len(verts)
                                st['tris'] += len(tris)
                                st['glb_bytes'] += sz
                                st['glbs'].append(
                                    {'bulk': idx, 'slot': k, 'file': name,
                                     'verts': len(verts), 'tris': len(tris),
                                     'bytes': sz,
                                     'sha256': hashlib.sha256(
                                         open(path, 'rb').read()).hexdigest()})
                        pos += s
        idx += 1
        if idx % 1000 == 0:
            print(f'  containers {idx} t={time.time()-t0:.0f}s '
                  f'glb_bytes={total_glb_bytes}')
    manifest['segments'] = {f'seg{k:02d}': seg_stats[k]
                            for k in sorted(seg_stats)}
    manifest['totals'] = {
        'containers_scanned': idx,
        'part_packages': sum(s['packages'] for s in seg_stats.values()),
        'sections_decoded': sum(s['sections_decoded'] for s in seg_stats.values()),
        'sections_failed': sum(s['sections_failed'] for s in seg_stats.values()),
        'verts': sum(s['verts'] for s in seg_stats.values()),
        'tris': sum(s['tris'] for s in seg_stats.values()),
        'glb_bytes': total_glb_bytes,
        'failures_by_reason': fails_by_reason,
        'elapsed_s': round(time.time() - t0, 1)}
    json.dump(manifest, open(manifest_path, 'w'), indent=1)
    print(json.dumps(manifest['totals'], indent=1))
    print('wrote', manifest_path)


if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'stage':
        stage(sys.argv[2], sys.argv[3], sys.argv[4])
    elif mode == 'parts':
        parts(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
    else:
        raise SystemExit(f'unknown mode {mode}')
