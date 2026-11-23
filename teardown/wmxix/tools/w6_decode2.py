#!/usr/bin/env python3
"""W6: CAW .ymg decoder v2 — batch path (v4) + table-end run path (v3).

Rules (measured on the ISO):
- v3.0001 (754 files): single vertex run starting at skin_off+24, extending
  toward skel_off while triples stay bounded (|coord| <= 4096) and steps
  stay < 3000 (strip jumps allowed). Proven on the elbow (148v/113f).
- v4/v3.0002: multi-batch tables (wrestler-style); use find_batch_table.
- DUMY: try stripping the 0x18 wrapper; if the remainder is YOBJ, decode it.
"""
import sys, struct, math
sys.path.insert(0, '/data/wmxix/tools-src/tools')
sys.path.insert(0, '/data/wmxix/tools-src')
import extract_wrestlers as ew

def s16(b, i): return struct.unpack('>h', b[i:i + 2])[0]
def u32(b, i): return struct.unpack('>I', b[i:i + 4])[0]

def dist(a, b):
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))

def median(xs):
    xs = sorted(xs)
    return xs[len(xs) // 2] if xs else 9999

def extend_run(d, start, end_limit, maxcoord=4096, maxstep=3000):
    triples = []
    o = start
    prev = None
    while o + 6 <= end_limit:
        t = (s16(d, o), s16(d, o + 2), s16(d, o + 4))
        if max(abs(x) for x in t) > maxcoord:
            break
        if prev is not None and dist(prev, t) > maxstep:
            break
        triples.append(t)
        prev = t
        o += 6
    return triples

def table_end(d, skin):
    """Scan 8-byte records from skin_off while they match the batch-table
    pattern (all-zero header, or [bone][count][00][count][u32 off] with a
    sane offset). Returns the offset just past the last matching record."""
    base = u32(d, 0x54)
    o = skin
    while o + 8 <= len(d):
        rec = d[o:o + 8]
        if rec == b'\x00' * 8:
            o += 8
            continue
        if (rec[2] == 0 and rec[1] == rec[3] and 3 <= rec[1] <= 255
                and base + u32(d, o + 4) + rec[1] * 6 <= len(d)):
            o += 8
            continue
        break
    return o


def run_path(d):
    """Single-run decode. Returns (triples, start) or (None, None).
    The run starts just past the skin batch table (table_end, or +8 when a
    mystery record sits between the table and the run — the elbow case).
    Candidates are tried in a small window past the table end; the winner
    is the longest valid run, with near-ties (<=2 verts) going to the
    later start (drops junk table bytes, keeps real verts)."""
    if len(d) < 0x64 or d[:4] != b'YOBJ':
        return None, None
    skin = u32(d, 0x60)
    skel = u32(d, 0x14)
    if not (0x80 <= skin < len(d)) or not (skin < skel <= len(d)):
        return None, None
    tend = table_end(d, skin)
    cands = []
    for k in range(5):
        start = tend + 8 * k
        if start + 6 > skel:
            break
        tris = extend_run(d, start, skel)
        if len(tris) < 20:
            continue
        steps = [dist(tris[i], tris[i + 1]) for i in range(len(tris) - 1)]
        if median(steps) > 400:
            continue
        cands.append((start, tris))
    if not cands:
        return None, None
    best_len = max(len(t) for _, t in cands)
    # latest start within 2 verts of the longest (junk-prefix trim)
    for start, tris in reversed(cands):
        if len(tris) >= best_len - 2:
            return tris, start
    return cands[0][1], cands[0][0]

def small_batch_path(d):
    """Parse batch records directly from skin_off, accepting 1+ records.
    For tiny Gears parts whose table is too short for the >=3-run heuristic.
    Validates each batch's verts as smooth strip data."""
    if len(d) < 0x64 or d[:4] != b'YOBJ':
        return None
    skin = u32(d, 0x60)
    base = u32(d, 0x54)
    batches = []
    o = skin
    skipped = 0
    while o + 8 <= len(d):
        rec = d[o:o + 8]
        if rec == b'\x00' * 8:
            o += 8
            continue
        if rec[2] == 0 and rec[1] == rec[3] and 3 <= rec[1] <= 255:
            off = u32(d, o + 4)
            b0 = base + off
            if b0 + rec[1] * 6 <= len(d):
                verts = [(s16(d, b0 + i * 6), s16(d, b0 + i * 6 + 2),
                          s16(d, b0 + i * 6 + 4)) for i in range(rec[1])]
                steps = [dist(verts[i], verts[i + 1])
                         for i in range(len(verts) - 1)]
                if len(verts) >= 3 and median(steps) < 800:
                    batches.append(verts)
                    skipped = 0
                    o += 8
                    continue
        # Non-matching record: skip a few (float/mystery records sit between
        # the table start and the first batch record in tiny Gears files),
        # but stop after 3 consecutive misses once we've found batches.
        skipped += 1
        o += 8
        if batches and skipped >= 3:
            break
        if not batches and skipped >= 4:
            break
    if batches and sum(len(b) for b in batches) >= 8:
        return batches
    return None


def decode_ymg_v2(data):
    """Returns dict(status, method, batches(list of vert lists), detail)."""
    if data[:4] == b'DUMY':
        inner = data[0x18:]
        if inner[:4] == b'YOBJ':
            r = decode_ymg_v2(inner)
            r['dumy_wrapper'] = True
            return r
        return {'status': 'DUMY', 'size': len(data)}
    if data[:4] != b'YOBJ':
        return {'status': 'NOT-YOBJ', 'size': len(data),
                'magic': data[:4].decode('ascii', 'replace')}
    ver = u32(data, 0x08)
    # Version-gated paths (proven: batch path on v4 wrestlers, run path on
    # the v3 elbow; v3 batch records point into the run misaligned = bogus).
    if ver >= 0x40000:
        bs = ew.extract_batches(data)
        if bs is not None:
            batches, stats = bs
            tot = sum(len(b) for b in batches)
            if tot >= 20 and median([s for s in stats]) < 800:
                return {'status': 'ok', 'method': 'batches', 'version': ver,
                        'batches': batches, 'stats': stats}
        tris, start = run_path(data)
        if tris is not None:
            return {'status': 'ok', 'method': 'run', 'version': ver,
                    'batches': [tris], 'run_start': start}
    else:
        tris, start = run_path(data)
        if tris is not None:
            return {'status': 'ok', 'method': 'run', 'version': ver,
                    'batches': [tris], 'run_start': start}
        bs = ew.extract_batches(data)
        if bs is not None:
            batches, stats = bs
            tot = sum(len(b) for b in batches)
            if tot >= 20 and median([s for s in stats]) < 800:
                return {'status': 'ok', 'method': 'batches', 'version': ver,
                        'batches': batches, 'stats': stats}
    # 2b) small-batch path (tiny Gears parts: 1-2 table records).
    sb = small_batch_path(data)
    if sb:
        return {'status': 'ok', 'method': 'small-batches', 'version': ver,
                'batches': sb}
    # 3) pool-scan fallback (last resort)
    pools = ew.extract_pools(data)
    if pools:
        return {'status': 'pool-scan', 'method': 'pool-scan', 'version': ver,
                'batches': pools}
    return {'status': 'NO-GEOMETRY', 'version': ver, 'size': len(data)}

def main():
    import w6_extract as w  # lazy: avoids a circular import with the driver
    iso = w.ISOFile()
    tests = [
        ('edit_data/MODEL/Man/Elbow/me0_000/l0.ymg', 'elbow (expect 148v/113f)'),
        ('edit_data/MODEL/Woman/Hair/mk0_024/c0.ymg', 'v4 hair'),
        ('edit_data/MODEL/Woman/Face/mq0_014/c4.ymg', 'v4 face (no batch tbl)'),
        ('edit_data/MODEL/Woman/Face/mq0_000/c4.ymg', 'v3 face (bad coords)'),
        ('edit_data/MODEL/Man/Upper_Body/mu0_014/c6.ymg', 'v3 upper (expect ~982v run)'),
        ('edit_data/MODEL/Man/Gears/mz0_122/g0.ymg', 'v3 gears (med 1023)'),
    ]
    for p, note in tests:
        d = iso.read(p)
        r = decode_ymg_v2(d)
        if r['status'] == 'ok' or r['status'] == 'pool-scan':
            nv = sum(len(b) for b in r['batches'])
            nt = 0
            for b in r['batches']:
                for s in ew.split_strips(b):
                    nt += max(0, len(s) - 2)
            print(f'{note}: {r["status"]}/{r["method"]} '
                  f'ver={r.get("version", 0):#x} batches={len(r["batches"])} '
                  f'verts={nv} tris={nt}')
        else:
            print(f'{note}: {r["status"]} {r}')
    # DUMY census: how many DUMY files actually contain a decodable YOBJ?
    ndumy = nok = 0
    dumy_verts = 0
    for p in sorted(iso.files):
        if p.startswith('edit_data/MODEL/') and p.endswith('.ymg'):
            d = iso.read(p)
            if d[:4] == b'DUMY':
                ndumy += 1
                r = decode_ymg_v2(d)
                if r['status'] == 'ok':
                    nok += 1
                    dumy_verts += sum(len(b) for b in r['batches'])
    print(f'DUMY census: {nok}/{ndumy} DUMY files decode to real geometry '
          f'({dumy_verts} verts total)')
    iso.close()

if __name__ == '__main__':
    main()
