#!/usr/bin/env python3
"""Stream-scan ONLY the not-yet-downloaded TK5DATA0 chunks (95..197) via
HTTP Range-fetch + discard. Complements the local scan of chunks 0..94
(scan_local.py on the partial file). Same patterns as tk5data0_stream.py.
Output: small JSON only, to /tmp (workspace quota is exhausted).
Usage: tk5data0_stream_missing.py <out.json> [nstreams] [first_chunk]
"""
import json, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor
URL = "https://ia601004.us.archive.org/8/items/slus-210.59.-tekken-5/SLUS_210.59.Tekken%205.ISO"
ISO_OFF = 1716224
SIZE = 2072586240
PATTERNS = [
    b'item_force', b'force', b'Force', b'FORCE',
    b'gem', b'Gem', b'GEM', b'symbol', b'Symbol', b'SYMBOL',
    b'laser', b'Laser', b'rank', b'Rank', b'gauge', b'Gauge',
    b'drain', b'Drain', b'heal', b'Heal',
    b'devil', b'Devil', b'DEVIL', b'door', b'Door', b'DOOR',
    b'gym_', b'mon_', b'romD', b'moj_stg', b'gym_init_obj',
    b'DEVILJIN', b'deviljin', b'RankingMode',
    b'gym_ozhe_1ckj66a', b'katgym_Bbr_bbblow', b'katgym_Gan_mekin',
    b'testchr1', b'testchr2', b'testchr3',
    b'GYM1', b'BDPK', b'TK5RESU1', b'TIM2', b'NUDP', b'MIF\x00', b'P3Dp', b'COM ',
]
def scan_chunk(start, end):
    iso_start, iso_end = ISO_OFF + start, ISO_OFF + end
    hits = []
    for attempt in range(4):
        try:
            req = urllib.request.Request(URL, headers={"Range": f"bytes={iso_start}-{iso_end-1}"})
            with urllib.request.urlopen(req, timeout=120) as r:
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
            if j < 0: break
            abs_off = start + j
            ctx = data[max(0, j-16):j+len(pat)+32]
            hits.append({'offset': abs_off, 'pattern': pat.decode('ascii', 'replace'),
                         'context_hex': ctx.hex(),
                         'context_ascii': ''.join(chr(c) if 32 <= c < 127 else '.' for c in ctx)})
            idx = j + 1
            if len(hits) > 20000: break
    return {'chunk': (start, end), 'error': None, 'hits': hits}
def main():
    out_path = sys.argv[1]
    nstreams = int(sys.argv[2]) if len(sys.argv) > 2 else 8
    first = int(sys.argv[3]) if len(sys.argv) > 3 else 95
    chunk_mb = 10
    chunk = chunk_mb * 1024 * 1024
    bounds = [(s, min(s + chunk, SIZE)) for s in range(0, SIZE, chunk)][first:]
    print(f"scanning TK5DATA0 chunks {first}..197 ({len(bounds)} chunks x {chunk_mb}MB, {nstreams} streams)", flush=True)
    all_hits, errors, done = [], [], 0
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=nstreams) as ex:
        for res in ex.map(lambda b: scan_chunk(b[0], b[1]), bounds):
            done += 1
            if res['error']: errors.append(res)
            all_hits.extend(res['hits'])
            if done % 10 == 0:
                print(f"  {done}/{len(bounds)} chunks, {len(all_hits)} hits, {time.time()-t0:.0f}s", flush=True)
    result = {'source': 'TK5DATA0.BIN (ISO offset 1716224, 2072586240 bytes), Internet Archive item slus-210.59.-tekken-5',
              'chunks_scanned': f'{first}..197', 'patterns': [p.decode('ascii') for p in PATTERNS],
              'errors': errors, 'hits_total': len(all_hits), 'hits': all_hits}
    with open(out_path, 'w') as f:
        json.dump(result, f, indent=1)
    print(f"done: {len(all_hits)} hits, {len(errors)} chunk errors -> {out_path}", flush=True)
if __name__ == '__main__':
    main()
