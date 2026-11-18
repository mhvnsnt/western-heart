#!/usr/bin/env python3
"""Identify orphan char_id grids (3,4,5,41) and verify problem blocks'
true grids by pool resolution of their (name, anim, ref) triples."""
import struct, json, pickle, os
from collections import defaultdict

W = os.path.expanduser('~/workspace/_fill3-ttt2-20261106/work')
d6 = open(os.path.expanduser('~/workspace/_ttt2-motion-20261103/join-cont/data006-decoded.bin'), 'rb').read()
u32 = lambda o: struct.unpack('>I', d6[o:o + 4])[0]
pools = pickle.load(open(os.path.join(W, 'pools.pkl'), 'rb'))['pools']
runs = json.load(open(os.path.join(W, 'grid-runs.json')))

def chain(char_id):
    rs = sorted([r for r in runs if r['char_id'] == char_id], key=lambda r: r['idx_lo'])
    out, cur_hi = [], 22
    for r in rs:
        if r['idx_lo'] <= cur_hi + 2:
            out.append(r)
            cur_hi = max(cur_hi, r['idx_hi'])
    return out

def sample_records(extents, step_target=600):
    recs = []
    total = sum(e['n'] for e in extents)
    step = max(1, total // step_target)
    for e in extents:
        for j in range(0, e['n'], step):
            recs.append(e['rec0_off'] + j * 0x70)
    return recs

def pstr(pool, rel):
    s = pool.get(rel)
    return s if s and 2 <= len(s) <= 80 else None

def score(extents, name_off, pool):
    recs = sample_records(extents)
    ok = dvd = 0
    anims = set()
    for ro in recs:
        p = ro + name_off
        a, b, ref = pstr(pool, u32(p)), pstr(pool, u32(p + 4)), u32(p + 8)
        if a and b and ref < 0x10000:
            ok += 1
            anims.add(b)
            if b.endswith('(DVD)'):
                dvd += 1
    return ok, dvd, anims, len(recs)

for cid in (3, 4, 5, 41, 26, 27, 28, 29, 30, 6, 50, 57, 64):
    ext = chain(cid)
    if not ext:
        print(f'char {cid}: NO chained extents')
        continue
    results = []
    for name_off, tag in ((0x4C, 'rot'), (0, 'unrot')):
        for pname, pool in pools.items():
            ok, dvd, anims, n = score(ext, name_off, pool)
            if n and ok / n > 0.5:
                results.append((ok / n, dvd, pname, tag, len(anims)))
    results.sort(reverse=True)
    print(f'char {cid}: extents={len(ext)} records={sum(e["n"] for e in ext)}')
    for r in results[:3]:
        print(f'    res={r[0]:.3f} dvd={r[1]} pool={r[2]} layout={r[3]} distinct_anims={r[4]}')
