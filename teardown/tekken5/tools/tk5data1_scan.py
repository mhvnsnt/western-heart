#!/usr/bin/env python3
"""Stream-scan TK5DATA1.BIN (inside the Tekken 5 ISO) for DW-relevant markers.

TK5DATA1.BIN is 1,297,731,584 bytes — too big to hold on this VM's disk
(quota). This script fetches it in parallel HTTP Range chunks, scans each
chunk IN MEMORY for byte patterns, records hits (offset + pattern + a small
context snippet), and DISCARDS the chunk. Only the small hit log is written
to disk.

Patterns: DW-relevant strings (force/gem/symbol/laser/rank/gauge/drain/
heal/devil, item_force, gym_, mon_, romD). A hit does NOT mean a value was
found — it means the region contains the string, and the region must then
be fetched + parsed in detail.

Usage: python3 tk5data1_scan.py <out_json> [nstreams] [chunk_mb]
"""
import json, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor

URL = "https://ia601004.us.archive.org/8/items/slus-210.59.-tekken-5/SLUS_210.59.Tekken%205.ISO"
ISO_OFF = 2074302464          # TK5DATA1.BIN start in the ISO
SIZE = 1297731584             # TK5DATA1.BIN size

PATTERNS = [
    b'item_force', b'force', b'Force', b'FORCE',
    b'gem', b'Gem', b'GEM',
    b'symbol', b'Symbol', b'SYMBOL',
    b'laser', b'Laser',
    b'rank', b'Rank',
    b'gauge', b'Gauge',
    b'drain', b'Drain',
    b'heal', b'Heal',
    b'devil', b'Devil', b'DEVIL',
    b'gym_', b'mon_', b'romD',
    b'DEVILJIN', b'deviljin',
]

def scan_chunk(start, end):
    """Fetch [start,end) of TK5DATA1, scan for patterns, return hits."""
    iso_start = ISO_OFF + start
    iso_end = ISO_OFF + end
    hits = []
    for attempt in range(4):
        try:
            req = urllib.request.Request(
                URL, headers={"Range": f"bytes={iso_start}-{iso_end-1}"})
            with urllib.request.urlopen(req, timeout=90) as r:
                if r.status not in (200, 206):
                    raise RuntimeError(f"HTTP {r.status}")
                data = r.read()
            if len(data) != end - start:
                raise RuntimeError(f"short read {len(data)} != {end-start}")
            break
        except Exception as e:
            if attempt == 3:
                return {'chunk': (start, end), 'error': str(e), 'hits': []}
            time.sleep(5)
    for pat in PATTERNS:
        idx = 0
        while True:
            j = data.find(pat, idx)
            if j < 0:
                break
            abs_off = start + j
            ctx = data[max(0, j-16):j+len(pat)+16]
            hits.append({
                'offset': abs_off,
                'pattern': pat.decode('ascii', 'replace'),
                'context_hex': ctx.hex(),
                'context_ascii': ''.join(chr(c) if 32 <= c < 127 else '.' for c in ctx),
            })
            idx = j + 1
            if len(hits) > 5000:
                break
    return {'chunk': (start, end), 'error': None, 'hits': hits}

def main():
    out_path = sys.argv[1]
    nstreams = int(sys.argv[2]) if len(sys.argv) > 2 else 8
    chunk_mb = int(sys.argv[3]) if len(sys.argv) > 3 else 10
    chunk = chunk_mb * 1024 * 1024
    bounds = [(s, min(s + chunk, SIZE)) for s in range(0, SIZE, chunk)]
    print(f"scanning TK5DATA1 ({SIZE} bytes) in {len(bounds)} chunks x {chunk_mb}MB, {nstreams} streams", flush=True)
    all_hits = []
    errors = []
    done = 0
    with ThreadPoolExecutor(max_workers=nstreams) as ex:
        for res in ex.map(lambda b: scan_chunk(b[0], b[1]), bounds):
            done += 1
            if res['error']:
                errors.append(res)
            all_hits.extend(res['hits'])
            if done % 20 == 0:
                print(f"  {done}/{len(bounds)} chunks, {len(all_hits)} hits so far", flush=True)
    result = {
        'source': 'TK5DATA1.BIN (ISO offset 2074302464, 1297731584 bytes), Internet Archive item slus-210.59.-tekken-5',
        'patterns': [p.decode('ascii') for p in PATTERNS],
        'chunks': len(bounds), 'errors': errors,
        'hits_total': len(all_hits), 'hits': all_hits,
    }
    with open(out_path, 'w') as f:
        json.dump(result, f, indent=1)
    print(f"done: {len(all_hits)} hits, {len(errors)} chunk errors -> {out_path}", flush=True)

if __name__ == '__main__':
    main()
