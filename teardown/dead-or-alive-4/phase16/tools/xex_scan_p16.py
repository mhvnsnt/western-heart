#!/usr/bin/env python3
"""DOA4 phase 16 Job 2: word-level scans of default_pe.bin .text.

Scans (phase-15 proven method; VA = fileoff + 0x8200E800, .text span
[0, 0x86AE00)):
1. lwz/lwzu with a chosen displacement set (the .bin header section
   offsets: w2 +0x08, w21 +0x54, w28 +0x70, w31 +0x7C, w1 +0x04).
2. bl call sites targeting a chosen VA set (classifier, dispatcher,
   handler, loader cluster).
3. cmpwi/cmplwi against 0x2C (44, the descriptor count) — full list.
Output: JSON report to argv[1]; counts on stdout.
"""
import json, struct, sys
from collections import defaultdict

PE = '/home/hatch/workspace/_doa4p16-clone/teardown/dead-or-alive-4/workdir/default_pe.bin'
BASE = 0x8200E800
TEXT = 0x86AE00

def s16(x): return x - 0x10000 if x & 0x8000 else x
def s24(x):
    x &= 0xFFFFFF
    return x - 0x1000000 if x & 0x800000 else x

def main():
    b = open(PE, 'rb').read()
    words = struct.unpack(f'>{TEXT//4}I', b[:TEXT])
    disps = {0x04, 0x08, 0x54, 0x70, 0x7C}
    lwz_hits = defaultdict(list)
    targets = {0x82408290: 'classifier', 0x824F388C: 'dispatcher',
               0x824F76E0: 'handler_2211', 0x82391A80: 'mot_loader_approx'}
    bl_hits = defaultdict(list)
    cmp2c = []
    for i, w in enumerate(words):
        va = BASE + 4 * i
        op = w >> 26
        if op in (32, 33):  # lwz / lwzu
            d = s16(w & 0xFFFF)
            if d in disps:
                lwz_hits[d].append(va)
        elif op == 18 and (w & 1):  # bl
            tgt = va + (s24(w >> 2) << 2)
            if tgt in targets:
                bl_hits[targets[tgt]].append(va)
        elif op in (10, 11):  # cmplwi / cmpwi (extended op check loose)
            if (w & 0xFFFF) == 0x2C:
                cmp2c.append(va)
    rep = {'lwz_disp_sites': {hex(k): [hex(v) for v in vs] for k, vs in sorted(lwz_hits.items())},
           'bl_sites': {k: [hex(v) for v in vs] for k, vs in bl_hits.items()},
           'cmpwi_0x2C_sites': [hex(v) for v in cmp2c]}
    json.dump(rep, open(sys.argv[1], 'w'), indent=1)
    for k, vs in sorted(lwz_hits.items()):
        print(f'lwz disp {k:#x}: {len(vs)} sites')
    for k, vs in bl_hits.items():
        print(f'bl -> {k}: {len(vs)} sites', [hex(v) for v in vs[:12]])
    print('cmpwi/cmplwi 0x2C sites:', len(cmp2c), [hex(v) for v in cmp2c])

if __name__ == '__main__':
    main()
