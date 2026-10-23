#!/usr/bin/env python3
"""DOA4 phase 16 Job 1: deterministic item-parse tester.

Parses every sub-block (zack triple + all t_* records) with a
tag->k rule (item = u16 tag + k data u16s; block must be consumed
exactly). Reports: exact-tile rate, failure tags (the tag at the
offset where the parse ran off the end / misaligned), and the
first-item (header) tag census. Rule variants selectable by argv.
"""
import struct, sys, os
from collections import Counter
sys.path.insert(0, '/home/hatch/workspace/_doa4p16-clone/teardown/dead-or-alive-4/phase16/tools')
from mot_parse_p16 import parse_fighter, parse_t

MOT = '/home/hatch/workspace/_doa4p16-scratch/mot'

def blocks():
    for name in ('zack.mot', 'm_zack.mot', 'c_zack.mot'):
        b, tab, ds, recs = parse_fighter(os.path.join(MOT, name))
        for r in recs:
            for ch, (off, sz) in enumerate(r['subs']):
                yield name, b[off:off+sz]
    for name in sorted(os.listdir(MOT)):
        if name.startswith('t_'):
            b, pairs, recs = parse_t(os.path.join(MOT, name))
            for r in recs:
                for ch, (off, sz) in enumerate(r['subs']):
                    yield name, b[off:off+sz]

K2_LOW = {0x0c, 0x0e, 0x10, 0x14, 0x18, 0x1c, 0x20, 0x24, 0x28, 0x2c, 0x30, 0x34, 0x38, 0x3c}

def k_of(tag):
    return 2 if (tag & 0xFF) in K2_LOW else 1

def parse(blk):
    n = len(blk); i = 0; items = []
    while i < n:
        if i + 4 > n: return None
        tag = struct.unpack_from('>H', blk, i)[0]
        k = k_of(tag)
        if i + 2 + 2 * k > n: return None
        items.append((tag, [struct.unpack_from('>H', blk, i + 2 + 2 * j)[0] for j in range(k)]))
        i += 2 + 2 * k
    return items if i == n else None

def main():
    tot = 0; ok = 0; fail_tags = Counter(); first_tags = Counter()
    fail_examples = []
    for name, blk in blocks():
        tot += 1
        if blk:
            first_tags[struct.unpack_from('>H', blk, 0)[0]] += 1
        it = parse(blk)
        if it is not None:
            ok += 1
        else:
            # locate failure: reparse and record the tag where it breaks
            n = len(blk); i = 0
            while i + 4 <= n:
                tag = struct.unpack_from('>H', blk, i)[0]
                k = k_of(tag)
                if i + 2 + 2 * k > n:
                    fail_tags[tag] += 1
                    if len(fail_examples) < 8: fail_examples.append((name, tag, blk.hex()))
                    break
                i += 2 + 2 * k
            else:
                fail_tags['<misalign>'] += 1
                if len(fail_examples) < 8: fail_examples.append((name, None, blk.hex()))
    print(f'blocks {tot}, exact-tile {ok} ({100*ok/tot:.2f}%)')
    print('failure tags:', fail_tags.most_common(12))
    for e in fail_examples: print('FAIL', e[0], hex(e[1]) if e[1] is not None else None, e[2][:96])
    print('first-tag top:', [(hex(t), c) for t, c in first_tags.most_common(12)])

if __name__ == '__main__':
    main()
