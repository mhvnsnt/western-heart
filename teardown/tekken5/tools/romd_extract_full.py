#!/usr/bin/env python3
"""Full romD extraction v3 (GRID): the directory is a fixed array of
128-byte BD records at payload+116 + i*128 (i=0..A-1).
Slot real: starts 'BD' + plausible name. Slot empty: all zeros.
Validate: Y-sum of real entries == data region - 12 (12-byte trailer).
Extract real entries in grid order at data_start + cumulative Y.
Duplicates across containers hash-compared. Output: raw/romd_out/."""
import struct, json, hashlib, re
from pathlib import Path

RAW = Path('/home/hatch/workspace/devil-within-decode/raw')
data = open(RAW / 'TK5DATA2.BIN', 'rb').read()
chunks = json.load(open(RAW / 'romd_bdpk_chunks.json'))
OUT = RAW / 'romd_out'
OUT.mkdir(parents=True, exist_ok=True)

names = set()
for line in open('/home/hatch/workspace/devil-within-decode/repo/teardown/tekken5/t5_motion_manifest.txt'):
    names.add(line.strip())
blocks = json.load(open(RAW / 'romd_blocks.json'))
for b in blocks:
    names.update(b['names'])

NAME_RE = re.compile(r'^[A-Za-z0-9_][A-Za-z0-9_.\-]{2,59}$')

def out_name(nm):
    return nm + '.dat' if nm + '.dat' in names else nm

seen = {}
report = {'containers': [], 'files': 0, 'bytes': 0, 'bad': [], 'dup_diff': [], 'empty_containers': []}
for ci, c in enumerate(chunks):
    off, a, b = c['off'], c['a'], c['b']
    pstart, pend = off+12, off+12+b
    rec = {'chunk': ci, 'off': off, 'A': a, 'B': b}
    if a == 0:
        rec['status'] = 'OK-EMPTY'; report['containers'].append(rec); continue
    entries, empty, garbage = [], 0, []
    for i in range(a):
        p = pstart + 116 + i*128
        if p+20 > pend:
            garbage.append(i); continue
        slot = data[p:p+128]
        if slot == b'\x00'*128:
            empty += 1; continue
        if slot[:2] != b'BD':
            garbage.append(i); continue
        typ = struct.unpack_from('<H', data, p+2)[0]
        x, y = struct.unpack_from('<II', data, p+4)
        nul = data.find(b'\x00', p+20, min(p+128, pend))
        nm = data[p+20:nul].decode('ascii', 'replace') if nul > p+20 else ''
        if not NAME_RE.match(nm):
            garbage.append(i); continue
        entries.append({'i': i, 'bd': p, 'type': typ, 'x': x, 'y': y, 'name': nm})
    data_start = pstart + 116 + a*128
    ysum = sum(e['y'] for e in entries)
    slack = (pend - data_start) - ysum
    rec.update({'entries': len(entries), 'empty_slots': empty, 'garbage_slots': garbage,
                'ysum': ysum, 'slack': slack})
    if garbage or slack != 12:
        rec['status'] = f'SKIP (garbage={garbage}, slack={slack})'
        report['bad'].append(rec); report['containers'].append(rec)
        print(f"chunk {ci} @{off:#x}: SKIP garbage={garbage} slack={slack} entries={len(entries)}/{a}")
        continue
    rec['status'] = 'OK'
    if not entries:
        report['empty_containers'].append(ci)
    cur = data_start
    for e in entries:
        fn = out_name(e['name'])
        blob = data[cur:cur+e['y']]
        assert len(blob) == e['y'], f'short read {fn} chunk {ci}'
        h = hashlib.sha256(blob).hexdigest()
        if fn in seen and seen[fn] != h:
            report['dup_diff'].append({'file': fn, 'chunk': ci})
        elif fn not in seen:
            seen[fn] = h
            (OUT / fn).write_bytes(blob)
            report['files'] += 1
            report['bytes'] += e['y']
        cur += e['y']
    report['containers'].append(rec)
    print(f"chunk {ci} @{off:#x}: A={a} entries={len(entries)} empty={empty} slack={slack} OK")
print(f"\nTOTAL unique files: {report['files']}, {report['bytes']} bytes -> {OUT}")
print(f"duplicate-content conflicts: {len(report['dup_diff'])}")
print(f"containers skipped: {len(report['bad'])}; empty containers: {report['empty_containers']}")
json.dump(report, open(RAW / 'romd_extract_report.json', 'w'), indent=1)
idx = json.load(open('/home/hatch/workspace/devil-within-decode/repo/teardown/tekken5/dw-motion-index.json'))
dw = [f['name'] for g in idx['groups'] for f in g['files']]
missing = [n for n in dw if not (OUT / n).exists()]
print(f'DW coverage: {len(dw)-len(missing)}/{len(dw)} extracted')
print(f'missing DW: {missing}')
