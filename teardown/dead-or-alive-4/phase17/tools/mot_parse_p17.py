#!/usr/bin/env python3
"""DOA4 phase 17 (copied from phase 16 Job 1): .mot record-layer parser (fighter + t_*).

Unified record grammar (phase 16, correcting the phase-15
framing direction): EVERY .mot record = 44 sub-blocks followed
by a 44-entry descriptor (u32 BE ABSOLUTE sub-block offsets, in
CHANNEL order — not necessarily sorted; proven on t_kl_gy rec
661, where channel 33's block sits second in the span). The
table-A target (fighter) / index offset (t_*) = DESCRIPTOR
START. Record k's sub-blocks tile [prev descriptor end,
desc_k start); the last descriptor ends at EOF. Sub-block size
for channel j = (next larger descriptor value, or descriptor
start) - desc[j]. The fighter default record's sub-block span
is the per-fighter shared front block, described by the
descriptor AT data_start (values absolute, from the shared
block's start).

This module exposes parse_fighter(path) / parse_t(path) ->
list of records: {target/id, desc_start, desc[44], subs: list of
44 (file_offset, size) in channel order, span_start}.
"""
import struct

def _desc_at(b, off):
    return [struct.unpack_from('>I', b, off + 4 * j)[0] for j in range(44)]

def _subs(b, desc, desc_start, span_start):
    order = sorted(range(44), key=lambda j: desc[j])
    sizes = {}
    for k, j in enumerate(order):
        nxt = desc[order[k + 1]] if k + 1 < 44 else desc_start
        sizes[j] = nxt - desc[j]
    return [(desc[j], sizes[j]) for j in range(44)]

MANIFEST = None

def table_a(b, name=None):
    # Ground truth for counts/data_start: phase15 mot-entries-manifest.json
    # (asserted against the file bytes below).
    global MANIFEST
    import json, os
    if MANIFEST is None:
        mp = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..',
                          'phase15', 'mot-entries-manifest.json')
        MANIFEST = {e['name']: e for e in json.load(open(mp))['entries']}
    if name is not None and name in MANIFEST and 'tableA' in MANIFEST[name]:
        ta = MANIFEST[name]['tableA']
        n, ds = ta['entries'], ta['data_start']
        vals = [struct.unpack_from('>I', b, 4 * i)[0] for i in range(n)]
        assert sorted(set(vals))[-1] < len(b)
        return vals, ds
    raise ValueError('fighter table A needs the phase-15 manifest entry')

def parse_fighter(path):
    b = open(path, 'rb').read()
    import os
    tab, ds = table_a(b, os.path.basename(path))
    targets = sorted(set(tab))
    recs = []
    prev_end = None
    for t in targets:
        desc = _desc_at(b, t)
        if t == ds:
            span_start = desc[0]  # shared front block start (absolute)
        else:
            span_start = prev_end
        recs.append({'target': t, 'desc_start': t, 'desc': desc,
                     'subs': _subs(b, desc, t, span_start),
                     'span_start': span_start, 'default': t == ds})
        prev_end = t + 176
    return b, tab, ds, recs

def parse_t(path):
    b = open(path, 'rb').read()
    pairs = []
    i = 0
    while True:
        a, c = struct.unpack_from('>II', b, i)
        if a == 0xFFFFFFFF: break
        pairs.append((a, c)); i += 8
    recs = []
    prev_end = None
    for k, (cid, doff) in enumerate(pairs):
        desc = _desc_at(b, doff)
        span_start = desc[0] if k == 0 else prev_end
        # span start is actually the min descriptor value for rec 0;
        # for k>0 sub-blocks start right after previous descriptor
        recs.append({'id': cid, 'desc_start': doff, 'desc': desc,
                     'subs': _subs(b, desc, doff, span_start), 'span_start': span_start})
        prev_end = doff + 176
    return b, pairs, recs

if __name__ == '__main__':
    import sys
    kind, path = sys.argv[1], sys.argv[2]
    if kind == 't':
        b, pairs, recs = parse_t(path)
        print(f'{path}: {len(recs)} records')
        for r in recs:
            szs = [s for _, s in r['subs']]
            print(f"  id {r['id']:#x} desc@{r['desc_start']} span_start {r['span_start']} "
                  f"sub sizes min {min(szs)} max {max(szs)} total {sum(szs)}")
    else:
        b, tab, ds, recs = parse_fighter(path)
        print(f'{path}: tableA {len(tab)} entries, data_start {ds}, {len(recs)} distinct records')
        for r in recs[:5]:
            szs = [s for _, s in r['subs']]
            print(f"  target {r['target']} sub sizes min {min(szs)} max {max(szs)} total {sum(szs)}")
