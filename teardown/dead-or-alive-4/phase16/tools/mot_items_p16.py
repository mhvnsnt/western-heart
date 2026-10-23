#!/usr/bin/env python3
"""DOA4 phase 16 Job 1: learn the .mot sub-block item grammar.

Hypothesis (from hand parses): a sub-block is a stream of items;
item = u16 BE tag + k data u16s, total length 4 B (k=1) or 6 B
(k=2); k depends only on the tag. This tool:
1. For every sub-block of zack.mot / m_zack.mot / c_zack.mot and
   every t_* record, runs a DP tiling (items of 4/6 B) and records,
   for each tag value, which k values occur in SOME exact tiling.
2. Reports tags whose k is ambiguous across the corpus, and the
   fraction of blocks that tile exactly.
3. With the majority mapping frozen, re-parses every block and
   reports the exact-consumption rate (the grammar's proof metric).
Output: JSON report to argv[1]; summary on stdout.
"""
import json, struct, sys
sys.path.insert(0, '/home/hatch/workspace/_doa4p16-clone/teardown/dead-or-alive-4/phase16/tools')
from mot_parse_p16 import parse_fighter, parse_t
import os

MOT = '/home/hatch/workspace/_doa4p16-scratch/mot'

def blocks():
    for name in ('zack.mot', 'm_zack.mot', 'c_zack.mot'):
        b, tab, ds, recs = parse_fighter(os.path.join(MOT, name))
        for r in recs:
            for ch, (off, sz) in enumerate(r['subs']):
                yield name, r.get('target'), ch, b[off:off+sz]
    for name in sorted(os.listdir(MOT)):
        if name.startswith('t_'):
            b, pairs, recs = parse_t(os.path.join(MOT, name))
            for r in recs:
                for ch, (off, sz) in enumerate(r['subs']):
                    yield name, r['id'], ch, b[off:off+sz]

def tilings(blk):
    """All exact tilings as sets of (tag, k) used; DP over offsets."""
    n = len(blk)
    if n % 2: return None
    # dp[pos] = set of frozenset((tag,k)) partial assignments reachable
    from functools import lru_cache
    tags = [struct.unpack_from('>H', blk, i)[0] for i in range(0, n, 2)]
    m = n // 2
    reach = [set() for _ in range(m + 1)]
    reach[0].add(frozenset())
    for i in range(m):
        if not reach[i]: continue
        for k in (1, 2):
            j = i + 1 + k
            if j <= m:
                t = tags[i]
                for a in reach[i]:
                    reach[j].add(a | {(t, k)})
    return reach[m]

def main():
    tagk = {}
    nblocks = 0; tiled = 0
    corpus = list(blocks())
    for name, rid, ch, blk in corpus:
        nblocks += 1
        ts = tilings(blk)
        if ts:
            tiled += 1
            # merge: tag -> set of k over all tilings of this block
            local = {}
            for a in ts:
                for (t, k) in a:
                    local.setdefault(t, set()).add(k)
            for t, ks in local.items():
                tagk.setdefault(t, set()).update(ks)
    ambiguous = {t: sorted(ks) for t, ks in tagk.items() if len(ks) > 1}
    mapping = {t: sorted(ks)[0] for t, ks in tagk.items() if len(ks) == 1}
    print(f'blocks {nblocks}, exactly tileable (4/6B items): {tiled}')
    print(f'distinct tags seen: {len(tagk)}, unambiguous: {len(mapping)}, ambiguous: {len(ambiguous)}')
    # freeze mapping: ambiguous tags resolved by majority over tilings later;
    # first report the mapping by low byte
    by_low = {}
    for t, k in mapping.items():
        by_low.setdefault(t & 0xFF, set()).add((t >> 8, k))
    rep = {'blocks': nblocks, 'tileable': tiled,
           'mapping_by_tag': {hex(t): k for t, k in sorted(mapping.items())},
           'ambiguous_tags': {hex(t): ks for t, ks in sorted(ambiguous.items())},
           'by_low_byte': {hex(lb): sorted(v) for lb, v in sorted(by_low.items())}}
    json.dump(rep, open(sys.argv[1], 'w'), indent=1)
    for lb, v in sorted(by_low.items()):
        print(f'low {lb:#04x}: {v}')

if __name__ == '__main__':
    main()
