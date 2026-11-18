#!/usr/bin/env python3
"""Fill-3 stage 1 (v3): generalized TTT2 motbin parser -> ttt2-join/1 tables.

Reproduces the shipped Roger/Jun/Unknown joins (gate) and parses all 66
motbin blocks in data006-decoded.bin.

Facts established by measurement (see PROGRESS.md):
- Every block's string pool starts AT the bracketed name string (name is
  pool string 0). Pool span = header pair-0 ptr - 0x20C when header sane.
- The join triple is layout-invariant: (name, anim, ref) always sit at
  (X, X+4, X+8) for X = the record's name-field offset. "Rotated" vs
  "unrotated" only changes where X sits inside the 0x70 record. A block's
  movelist is therefore a grid of triples: name fields at
  section_start + q + k*0x70, q in [0, 0x70).
- q is found per block by scanning q in steps of 4 and scoring grids by
  records whose anim ends with '(DVD)', tie-broken by valid count and
  motOrigin presence. Known: Paul/LAW/Roger q=0x4C (record phase 0,
  name@+0x4C); Jun/Dragunov q=0x5C; Unknown q=0x2C.
- Numbering: if a motOrigin record is on the grid and q != 0x4C-phase-0
  convention applies -- precisely: ROT phase-0 blocks (q == 0x4C and the
  pair-12 grid starts at the section start) number i = k. All other
  blocks: motOrigin is numbered i=4 and i counts from there (Jun); if
  no motOrigin is on the grid, i = k from the section start (Unknown).
- A record is emitted iff name and anim resolve to pool strings
  (NUL-preceded, 2..80 bytes) and ref < 0x10000.
  anim_ref = (bank << 14) | index.
- Blocks whose header does not validate (YOSHIMITSU) are anchored on
  the pool's motOrigin -> Bco_newjump2(DVD) byte pattern instead.
"""
import struct, re, json, os
from collections import defaultdict

D6_PATH = os.path.expanduser('~/workspace/_ttt2-motion-20261103/join-cont/data006-decoded.bin')
OUT_DIR = os.path.expanduser('~/workspace/_fill3-ttt2-20261106/work/joins')

d6 = open(D6_PATH, 'rb').read()
u32 = lambda o: struct.unpack('>I', d6[o:o + 4])[0]

def find_blocks():
    seen = {}
    for m in re.finditer(rb'\[([A-Za-z0-9_\- ]{2,24})\]\x00', d6):
        nm = m.group(1).decode('ascii', 'replace')
        if nm not in seen:
            seen[nm] = m.start()
    return sorted(seen.items(), key=lambda kv: kv[1])

def build_pool(bracket, span):
    """All NUL-preceded strings in [bracket, bracket+span): {rel: str}."""
    pool = {}
    limit = bracket + span
    off = bracket
    while off < limit:
        end = d6.index(b'\x00', off)
        t = d6[off:end]
        pool[off - bracket] = t.decode('ascii', 'replace')
        off = end + 1
    return pool

def pstr(pool, rel):
    s = pool.get(rel)
    if s is None or not (2 <= len(s) <= 80):
        return None
    return s

def scan_triples(pool, s_off, limit_off):
    """Name-field grid at s_off + k*0x70 while the triple fits before limit_off."""
    recs, dvd = [], 0
    k = 0
    while s_off + k * 0x70 + 12 <= limit_off:
        p = s_off + k * 0x70
        nm, an, ref = pstr(pool, u32(p)), pstr(pool, u32(p + 4)), u32(p + 8)
        if nm and an and ref < 0x10000:
            recs.append((k, nm, an, ref))
            if an.endswith('(DVD)'):
                dvd += 1
        k += 1
    return recs, dvd, k

def parse_block(name, bracket, next_bracket):
    base = bracket - 0x20C
    header_sane = (u32(base + 8) == 0 and 0x1000 < u32(base + 0x140) < 0x40000
                   and u32(base + 0x1A0) < 0x400000 and 0 < u32(base + 0x1A4) < 20000
                   and u32(base + 0x1A8) > u32(base + 0x1A0))
    pool_span = u32(base + 0x140) if header_sane else min(0x14000, next_bracket - bracket)
    pool = build_pool(bracket, pool_span)
    info = {'character': name, 'bracket': bracket, 'base': base,
            'header_sane': header_sane, 'pool_strings': len(pool)}
    mo_rel = next((r for r, s in pool.items() if s == 'motOrigin'), None)
    info['motorigin_rel'] = mo_rel
    candidates = []
    if header_sane:
        ml, cnt, sec_end = u32(base + 0x1A0), u32(base + 0x1A4), u32(base + 0x1A8)
        info.update({'pair12_ptr': ml, 'pair12_cnt': cnt, 'pair13_ptr': sec_end})
        sec_start = base + ml
        sec_limit = min(base + sec_end, len(d6))
        for q in range(0, 0x70, 4):
            if q == 0x4C:
                lim = sec_start + q + cnt * 0x70
            else:
                lim = sec_start + q + ((sec_end - (ml + q)) // 0x70) * 0x70
            recs, dvd, n = scan_triples(pool, sec_start + q, min(lim, len(d6)))
            has_mo = any(nm == 'motOrigin' for _, nm, _, _ in recs)
            candidates.append((dvd, len(recs), q, recs, has_mo))
    else:
        bco_rel = next((r for r, s in pool.items() if s == 'Bco_newjump2(DVD)'), None)
        info['bco_rel'] = bco_rel
        pat = struct.pack('>II', mo_rel, bco_rel)
        hits, start = [], bracket
        while True:
            j = d6.find(pat, start, next_bracket + 0x100000)
            if j < 0:
                break
            hits.append(j)
            start = j + 1
        info['mo_pattern_hits'] = hits
        for j in hits:
            recs, dvd, n = scan_triples(pool, j - 900 * 0x70, j + 2600 * 0x70)
            recs = [(k - 900, nm, an, ref) for (k, nm, an, ref) in recs]
            has_mo = any(nm == 'motOrigin' for _, nm, _, _ in recs)
            candidates.append((dvd, len(recs), f'anchor@{j}', recs, has_mo))
    if not candidates:
        info['layout'] = None
        info['records'] = []
        return info
    candidates.sort(key=lambda c: (c[0], c[1], c[4]), reverse=True)
    dvd, nvalid, q, recs, has_mo = candidates[0]
    info.update({'name_phase': q, 'dvd_score': dvd, 'valid': nvalid,
                 'has_motorigin': has_mo})
    mo_k = [k for (k, nm, _, _) in recs if nm == 'motOrigin']
    # ROT phase-0 convention: name grid at section+0x4C, records start at
    # the section start -> i = k (motOrigin lands at k=4 naturally).
    if q == 0x4C and mo_k and mo_k[0] == 4:
        origin = 0
        info['numbering'] = 'grid (rot phase 0)'
    elif mo_k:
        origin = mo_k[0] - 4
        info['numbering'] = 'motOrigin anchored at i=4'
    else:
        origin = 0
        info['numbering'] = 'grid (no motOrigin on grid)'
    info['origin_k'] = origin
    info['motorigin_k'] = mo_k[0] if mo_k else None
    info['records'] = [(k - origin, nm, an, ref) for (k, nm, an, ref) in recs if k >= origin]
    return info

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    blocks = find_blocks()
    print(f"blocks found: {len(blocks)}")
    census = {}
    for idx, (name, bracket) in enumerate(blocks):
        nxt = blocks[idx + 1][1] if idx + 1 < len(blocks) else len(d6)
        info = parse_block(name, bracket, nxt)
        recs = info.pop('records')
        banks = defaultdict(set)
        anim2ref = defaultdict(set)
        for (i, nm, an, ref) in recs:
            banks[ref >> 14].add(ref & 0x3FFF)
            anim2ref[an].add(ref)
        entry = dict(info)
        entry.update({
            'n_records': len(recs),
            'banks': {str(b): {'n': len(v), 'max': max(v) if v else -1}
                      for b, v in sorted(banks.items())},
            'distinct_anims': len(anim2ref),
            'multi_ref_anims': sum(1 for v in anim2ref.values() if len(v) > 1),
            'motorigin_i': [i for (i, nm, an, ref) in recs if nm == 'motOrigin'],
            'i_range': [recs[0][0], recs[-1][0]] if recs else None,
        })
        census[name] = entry
        join = {
            'format': 'ttt2-join/1',
            'character': name,
            'motbin': f"data006-decoded.bin, block base {info['base']} (file offset of [{name}] name at {bracket})",
            'record_layout': (f"name/anim/ref triple grid at section_ptr + {info.get('name_phase')}, "
                              f"record size 0x70, numbering: {info.get('numbering')}"),
            'anim_ref': "(bank << 14) | index; bank 0 = own trailing MOTA table in data006, bank 1 = data005 table (see bank-tables), bank 2 = data004 table @0x100 (1875 entries)",
            'records': [{'i': i, 'name': nm, 'anim': an, 'ref': ref,
                         'bank': ref >> 14, 'idx': ref & 0x3FFF}
                        for (i, nm, an, ref) in recs],
        }
        fn = os.path.join(OUT_DIR, name.lower().replace(' ', '_') + '-join.json')
        json.dump(join, open(fn, 'w'), indent=1)
        print(f"{name:>14}: sane={info['header_sane']} q={info.get('name_phase')} "
              f"recs={len(recs):>5} anims={len(anim2ref):>5} multi={entry['multi_ref_anims']} "
              f"motOrigin_i={entry['motorigin_i']} banks=" +
              " ".join(f"{b}:{v['n']}/{v['max']}" for b, v in entry['banks'].items()))
    json.dump(census, open(os.path.join(OUT_DIR, '..', 'census-parse.json'), 'w'), indent=1)
    print("wrote joins + census-parse.json")

if __name__ == '__main__':
    main()
