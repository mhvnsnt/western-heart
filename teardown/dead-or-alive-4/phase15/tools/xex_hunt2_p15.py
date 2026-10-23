#!/usr/bin/env python3
"""DOA4 phase 15 Job 3 (v2, word-level — the phase-11 proven method):
scan default_pe.bin instruction/data words directly (no linear
disasm). Targets:
 (a) aligned u32 words anywhere == pointers into the .bin / .mot
     registry string ranges (pointer tables);
 (b) lis (op15, rA=0) + addi/ori completion within the next 8 words
     resolving into the registry ranges (either 0x400000-based PE
     convention — phase-11 verified — or 0x82000000-based);
 (c) cmpwi (op11) / cmplwi (op10) with immediate in {0x400, 0x3e8,
     0x3ec, 0x190, 0x2c} or 0x2200-0x22ff (token namespace);
 (d) lwz (op32) with displacement 0x08/0x54/0x70 within 0x400 bytes
     after a type-(b) hit (context filter, not raw census).
Registries (file offsets): .bin 0x27849c-0x278670; .mot strings found
by scan (zack.mot at 0x2848d4; span walked below)."""
import json, struct
from collections import Counter

PE = '/home/hatch/workspace/_doa4p8-clone/teardown/dead-or-alive-4/workdir/default_pe.bin'
d = open(PE, 'rb').read()
words = struct.unpack('>%dI' % (len(d) // 4), d[:len(d) // 4 * 4])
TEXT_LO, TEXT_HI = 0x2d1800 // 4, (0x2d1800 + 0x86ae00) // 4

# registry spans
def reg_span(first_str_off):
    lo = first_str_off
    # walk backwards over consecutive D:\bin strings
    while True:
        p = d.rfind(b'D:\\bin\\', max(0, lo - 0x200), lo)
        if p < 0 or lo - p > 48: break
        lo = p
    hi = lo
    while True:
        p = d.find(b'D:\\bin\\', hi, hi + 0x200)
        if p < 0: break
        e = d.find(b'\x00', p)
        hi = e + 1
        nxt = d.find(b'D:\\bin\\', hi, hi + 48)
        if nxt < 0: break
    return lo, hi

BIN = reg_span(0x27849c)
mot_first = d.find(b'D:\\bin\\', 0x283000)
MOT = reg_span(mot_first)
print('BIN registry span', hex(BIN[0]), hex(BIN[1]), '; MOT span', hex(MOT[0]), hex(MOT[1]))

def ptr_targets(w):
    out = []
    for base, reg, tag in ((0x400000, BIN, 'bin'), (0x400000, MOT, 'mot'),
                           (0x82000000, BIN, 'bin82'), (0x82000000, MOT, 'mot82')):
        if base + reg[0] <= w < base + reg[1]:
            out.append(tag)
    return out

hits = {'ptr_words': [], 'lis_addi': [], 'cmp': [], 'lwz_ctx': []}
for i, w in enumerate(words):
    t = ptr_targets(w)
    if t:
        hits['ptr_words'].append({'fileoff': hex(i * 4), 'value': hex(w), 'tags': t})
# lis scan
lis_at = {}
for i in range(TEXT_LO, TEXT_HI):
    w = words[i]
    if (w >> 26) == 15 and ((w >> 16) & 0x1F) == 0:
        lis_at[i] = ((w >> 21) & 0x1F, w & 0xFFFF)
print('lis count in .text:', len(lis_at))
for i, (rd, imm) in lis_at.items():
    hi = (imm << 16) & 0xFFFFFFFF
    for j in range(i + 1, min(i + 9, TEXT_HI)):
        w = words[j]
        op = w >> 26
        if op in (14, 24) and ((w >> 21) & 0x1F) == rd and ((w >> 16) & 0x1F) == rd:
            lo = w & 0xFFFF
            if op == 14 and lo >= 0x8000: lo -= 0x10000
            addr = (hi + lo) & 0xFFFFFFFF
            for base, reg, tag in ((0x400000, BIN, 'bin'), (0x400000, MOT, 'mot'),
                                   (0x82000000, BIN, 'bin82'), (0x82000000, MOT, 'mot82')):
                if base + reg[0] <= addr < base + reg[1]:
                    hits['lis_addi'].append({'fileoff': hex(j * 4), 'addr': hex(addr), 'tag': tag})
            break
# cmp scan
INTEREST = {0x400, 0x3e8, 0x3ec, 0x190, 0x2c}
for i in range(TEXT_LO, TEXT_HI):
    w = words[i]
    if (w >> 26) in (10, 11):
        imm = w & 0xFFFF
        if imm in INTEREST or 0x2200 <= imm <= 0x22FF:
            hits['cmp'].append({'fileoff': hex(i * 4), 'op': w >> 26, 'imm': hex(imm)})
# lwz near lis_addi hits
near = set()
for h in hits['lis_addi']:
    c = int(h['fileoff'], 16) // 4
    for k in range(c, c + 0x100): near.add(k)
for i in sorted(near):
    if TEXT_LO <= i < TEXT_HI:
        w = words[i]
        if (w >> 26) == 32:
            disp = w & 0xFFFF
            if disp in (0x08, 0x54, 0x70):
                hits['lwz_ctx'].append({'fileoff': hex(i * 4), 'disp': hex(disp)})
print('ptr_words:', len(hits['ptr_words']), 'lis_addi:', len(hits['lis_addi']),
      'cmp:', len(hits['cmp']), 'lwz_ctx:', len(hits['lwz_ctx']))
for k in ('ptr_words', 'lis_addi', 'cmp'):
    for h in hits[k][:30]: print(' ', k, h)
json.dump({'BIN': BIN, 'MOT': MOT, 'hits': hits},
          open('/home/hatch/workspace/_doa4p2-scratch/p15/xex_hunt2.json', 'w'), indent=1)
print('WROTE xex_hunt2.json')
