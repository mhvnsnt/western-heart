#!/usr/bin/env python3
"""Fill 3 stage 1 v2: build final TTT2 joins for every non-shipped block.

Proven facts this version rests on:
- Roger's +0x10 chain (lo>=0 extents, triples at record+0x4C) agrees with his
  SHIPPED pair-12 join 2160/2160, same numbering i = lo + 23, for i >= 23.
- Wrapped runs (lo > 60000, length == char_id) are an artifact array, NOT
  movelist heads. Chain joins therefore cover i >= 23; i < 23 comes only
  from a genuine pair-12 parse.
- All-zero triples (name_rel == anim_rel == 0) are poison and are rejected.
- Extent quality is scored by the fraction of anims ending in '(DVD)'.

Per block: pair-12 join is final when it is genuine (motOrigin at i=4,
anim->ref near-pure). Chain records are merged in only when a shift search
aligns them to the pair-12 numbering with >=98% agreement on the overlap.
When pair-12 is junk/absent, the chain join stands alone (numbering i=lo+23,
head i<23 an explicitly documented gap).
"""
import struct, json, pickle, os
from collections import defaultdict

W = os.path.expanduser('~/workspace/_fill3-ttt2-20261106/work')
d6 = open(os.path.expanduser('~/workspace/_ttt2-motion-20261103/join-cont/data006-decoded.bin'), 'rb').read()
u32 = lambda o: struct.unpack('>I', d6[o:o + 4])[0]
pools = pickle.load(open(os.path.join(W, 'pools.pkl'), 'rb'))['pools']
runs_all = json.load(open(os.path.join(W, 'grid-runs-all.json')))

CHAR_ID = {
    'Paul': 0, 'LAW': 1, 'Lei_Wulong': 2, 'KING': 3, 'YOSHIMITSU': 4, 'NINA': 5,
    'HWOARANG': 6, 'Lin_Xiaoyu': 7, 'CHRISTIE': 8, 'JIN': 9, 'JULIA': 10,
    'Kuma': 11, 'Bryan': 12, 'HEIHACHI': 13, 'KAZUYA': 14, 'LEE': 15,
    'Steve_Fox': 16, 'MARDUK': 17, 'Jack': 18, 'ROGER': 19, 'ANNA': 20,
    'Wang': 21, 'GANRYU': 22, 'Asuka': 23, 'BRUCE': 24, 'BAEK_DOO_SAN': 25,
    'DEVIL_JIN': 26, 'RAVEN': 27, 'FENG': 28, 'ARMOR_KING': 29, 'EMILIE': 30,
    'Dragunov': 31, 'PANDA': 32, 'EDDY': 33, 'BOB_SATSUMA': 34, 'ZAFINA': 35,
    'Miguel': 36, 'Eleonor': 37, 'Lars': 38, 'Alisa': 39, 'Jinpachi': 40,
    'Ogre': 41, 'JUN_KAZAMA': 42, 'Unknown': 43, 'Kunimitsu': 44, 'SlimBob': 45,
    'Forest': 46, 'Miharu': 47, 'ANGEL': 48, 'Michelle': 49, 'P-JACK': 50,
    'ALEX': 51, 'GreenOgre': 52, 'VIOLET': 53, 'Bosconovitch': 54,
    'Sebastian': 55, 'TIGER': 56, 'Combot': 57, 'Zako00': 58, 'Zako01': 59,
    'Zako02': 60, 'Zako03': 61, 'Zako04': 62, 'Zako05': 63, 'Zako06': 64,
    'Zako07': 65,
}
SHIPPED = {'ROGER', 'JUN_KAZAMA', 'Unknown'}

def pstr(pool, rel):
    s = pool.get(rel)
    return s if s and 2 <= len(s) <= 80 else None

def read_triple(pool, rec_off, name_off):
    p = rec_off + name_off
    nr, ar, ref = u32(p), u32(p + 4), u32(p + 8)
    if nr == 0 and ar == 0:
        return None
    a, b = pstr(pool, nr), pstr(pool, ar)
    if a and b and ref < 0x10000 and (ref >> 14) <= 2 and (ref & 0x3FFF) < 4096:
        return (a, b, ref)
    return None

def extent_records(pool, ext):
    """Return (records {i: triple}, dvd_frac) using the better of rot/unrot."""
    best = None
    for off in (0x4C, 0x00):
        recs, dvd = {}, 0
        for j in range(ext['n']):
            t = read_triple(pool, ext['rec0_off'] + j * 0x70, off)
            if t:
                recs[ext['lo_first'] + 23 + j] = t
                if t[1].endswith('(DVD)'): dvd += 1
        frac = dvd / ext['n'] if ext['n'] else 0
        if best is None or frac > best[1]:
            best = (recs, frac)
    return best

def assemble_chain(name):
    pool = pools[name]
    cand = [r for r in runs_all if r['char_id'] == CHAR_ID[name]
            and r['n'] >= 8 and r['lo_first'] < 60000]
    scored = []
    for r in cand:
        recs, frac = extent_records(pool, r)
        scored.append((r['lo_first'], r, recs, frac))
    scored.sort(key=lambda x: x[0])
    records, expect, used = {}, None, set()
    while True:
        pick = None
        for lo, r, recs, frac in scored:
            if id(r) in used or frac < 0.5: continue
            if expect is None or lo <= expect + 2:
                if pick is None or frac > pick[3]:
                    pick = (lo, r, recs, frac)
        if pick is None: break
        lo, r, recs, frac = pick
        used.add(id(r))
        for i, t in recs.items(): records[i] = t
        expect = lo + r['n'] if expect is None else max(expect, lo + r['n'])
    return records

def stats(recs):
    a2r = defaultdict(set)
    for t in recs.values(): a2r[t[1]].add(t[2])
    return {'n': len(recs), 'anims': len(a2r),
            'multi_ref': sum(1 for v in a2r.values() if len(v) > 1),
            'motorigin_i': [i for i, t in recs.items() if t[0] == 'motOrigin']}

def load_pair12(name):
    p = os.path.join(W, 'joins', name.lower() + '-join.json')
    if not os.path.exists(p): return {}
    j = json.load(open(p))
    return {r['i']: (r['name'], r['anim'], r['ref']) for r in j['records']}

def align_shift(a, b):
    """Find shift s (b_i + s = a_i) maximizing exact agreement on overlap."""
    best = (0, 0, 0)
    for s in range(-800, 801):
        agree = dis = 0
        for i, t in b.items():
            if i + s in a:
                if a[i + s] == t: agree += 1
                else: dis += 1
        if agree > best[1]: best = (s, agree, dis)
    return best

def main():
    outdir = os.path.join(W, 'joins-final'); os.makedirs(outdir, exist_ok=True)
    verdicts = {}
    for name in sorted(CHAR_ID):
        if name in SHIPPED: continue
        a = load_pair12(name)
        b = assemble_chain(name)
        sa, sb = stats(a), stats(b)
        shift, agree, dis = align_shift(a, b) if a and b else (0, 0, 0)
        overlap = agree + dis
        pair_good = (4 in sa['motorigin_i'] and sa['multi_ref'] <= 3 and sa['n'] >= 250)
        chain_good = (sb['n'] >= 1500 and sb['anims'] >= 800 and sb['multi_ref'] <= 5)
        final, source = {}, None
        if pair_good:
            final = dict(a); source = 'pair12'
            if overlap >= 20 and agree >= 0.98 * overlap:
                added = 0
                for i, t in b.items():
                    if i + shift not in final: final[i + shift] = t; added += 1
                source = 'pair12+chain(shift=%d, +%d)' % (shift, added)
        elif chain_good:
            final = dict(b); source = 'chain'
        elif sa['n'] >= sb['n']:
            final = dict(a); source = 'pair12-REVIEW'
        else:
            final = dict(b); source = 'chain-REVIEW'
        sf = stats(final)
        recs = [{'i': i, 'name': t[0], 'anim': t[1], 'ref': t[2],
                 'bank': t[2] >> 14, 'idx': t[2] & 0x3FFF}
                for i, t in sorted(final.items())]
        json.dump({'format': 'ttt2-join/1', 'character': name,
                   'motbin': 'data006-decoded.bin [%s] motbin' % name,
                   'records': recs},
                  open(os.path.join(outdir, name.lower() + '-join.json'), 'w'), indent=1)
        verdicts[name] = {'source': source, 'pair12': sa, 'chain': sb,
                          'shift': shift, 'overlap_agree': agree, 'overlap_dis': dis,
                          'final': sf}
        print('%-14s %-26s final=%5d anims=%5d multi=%d mo=%s (pair %d/%d, chain %d/%d, shift %d agree %d/%d)'
              % (name, source, sf['n'], sf['anims'], sf['multi_ref'], sf['motorigin_i'],
                 sa['n'], sa['anims'], sb['n'], sb['anims'], shift, agree, overlap))
    json.dump(verdicts, open(os.path.join(W, 'join-verdicts.json'), 'w'), indent=1, default=str)

if __name__ == '__main__':
    main()
