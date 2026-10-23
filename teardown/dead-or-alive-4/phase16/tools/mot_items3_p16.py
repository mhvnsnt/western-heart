#!/usr/bin/env python3
"""DOA4 phase 16 Job 1: tag->k constraint propagation.

Items: u16 tag + k data u16s (item = 2+k u16s, k in {1,2}).
For each sub-block, forward/backward bool DP over u16 positions
gives, for every item-start position, the set of k values used by
SOME exact tiling. Intersecting over the whole corpus yields each
tag's possible-k set; iterate to a fixpoint (shrinking sets can
only remove tilings). Reports the surviving mapping, ambiguous
tags, and blocks that stop tiling (rule falsification signal).
Corpus: zack triple + all t_* records (41,096 sub-blocks).
"""
import json, struct, sys, os
sys.path.insert(0, '/home/hatch/workspace/_doa4p16-clone/teardown/dead-or-alive-4/phase16/tools')
from mot_parse_p16 import parse_fighter, parse_t

MOT = '/home/hatch/workspace/_doa4p16-scratch/mot'

def blocks():
    for name in ('zack.mot', 'm_zack.mot', 'c_zack.mot'):
        b, tab, ds, recs = parse_fighter(os.path.join(MOT, name))
        for r in recs:
            for ch, (off, sz) in enumerate(r['subs']):
                yield b[off:off+sz]
    for name in sorted(os.listdir(MOT)):
        if name.startswith('t_'):
            b, pairs, recs = parse_t(os.path.join(MOT, name))
            for r in recs:
                for ch, (off, sz) in enumerate(r['subs']):
                    yield b[off:off+sz]

def used_k(blk, possible):
    """Return dict tag->set(k) used in some exact tiling under
    the current possible-k sets, or None if the block cannot tile."""
    w = struct.unpack(f'>{len(blk)//2}H', blk)
    m = len(w)
    fwd = [False] * (m + 1); fwd[0] = True
    for i in range(m):
        if fwd[i]:
            for k in possible.get(w[i], (1, 2)):
                if i + 1 + k <= m: fwd[i + 1 + k] = True
    if not fwd[m]: return None
    bwd = [False] * (m + 1); bwd[m] = True
    for i in range(m - 1, -1, -1):
        for k in possible.get(w[i], (1, 2)):
            if i + 1 + k <= m and bwd[i + 1 + k]:
                bwd[i] = True; break
    used = {}
    for i in range(m):
        if fwd[i] and bwd[i]:
            for k in possible.get(w[i], (1, 2)):
                if i + 1 + k <= m and bwd[i + 1 + k]:
                    used.setdefault(w[i], set()).add(k)
    return used

def main():
    corpus = [b for b in blocks() if len(b) >= 4]
    print('corpus blocks:', len(corpus))
    possible = {}
    for it in range(12):
        changed = False; dead = 0
        newposs = {}
        for blk in corpus:
            u = used_k(blk, possible)
            if u is None:
                dead += 1; continue
            for t, ks in u.items():
                cur = newposs.get(t)
                newposs[t] = ks if cur is None else (cur & ks)
        # tags never constrained keep {1,2}
        for t, ks in newposs.items():
            if possible.get(t) != ks: changed = True
        possible = newposs
        amb = {t: ks for t, ks in possible.items() if len(ks) > 1}
        print(f'iter {it}: tags {len(possible)}, ambiguous {len(amb)}, dead blocks {dead}')
        if not changed: break
    mapping = {t: next(iter(ks)) for t, ks in possible.items() if len(ks) == 1}
    amb = {t: sorted(ks) for t, ks in possible.items() if len(ks) > 1}
    json.dump({'mapping': {hex(t): k for t, k in sorted(mapping.items())},
               'ambiguous': {hex(t): ks for t, ks in sorted(amb.items())}},
              open(sys.argv[1], 'w'), indent=1)
    print('final mapping size:', len(mapping), 'ambiguous:', len(amb))
    for t, ks in sorted(amb.items())[:40]:
        print('AMB', hex(t), ks)

if __name__ == '__main__':
    main()
