#!/usr/bin/env python3
"""Classify every PS2 LUT entry in TK5DATA1.BIN by its decrypted head.

The prior lut_gym_scan.py sampled all 1571 entries' first 2048 bytes but
only checked for GYM1. This pass classifies WHAT each entry is: magic,
printable fraction, any DW-relevant strings in the decrypted head, and
any u32 == 1,000,000 (the one Force-candidate immediate from the code
sweep). Goal: find the meter/gem/Force/rank/symbol tables, if any entry
holds them, or exhaust the LUT inventory with per-entry evidence.

Method (stream-scan, no whole-file download, no big disk writes):
  - Read the PS2 LUT from the local Code blob (TABLESTART 0x0027B5B0,
    1571 entries: offset u32 (sector x 0x800), size u32).
  - For each entry (size != 0xFFFFFFFF, size >= 104): HTTP Range-fetch
    only the first min(size, 2048) bytes from TK5DATA1 inside the ISO,
    in parallel, discard after classification.
  - Try raw, then sector-cipher decrypt (seed = entry index, same
    2048-byte keystream per block, via romd_extract.decrypt_sector_data_fast).
  - Classify the winning buffer: known magics anywhere in first 64
    bytes, printable fraction, DW string hits, u32 1000000 hits.
Output: small JSON only (per-entry rows + summary counts).
Usage: python3 lut_classify.py <TK5DATA3_code.bin> <out.json> [nstreams]
"""
import json, struct, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, '/home/hatch/workspace/devil-within-decode/repo/teardown/tekken5/tools')
from romd_extract import decrypt_sector_data_fast

URL = "https://ia601004.us.archive.org/8/items/slus-210.59.-tekken-5/SLUS_210.59.Tekken%205.ISO"
ISO_OFF = 2074302464
TABLESTART = 0x0027B5B0
TABLECOUNT = 1571
SECTOR = 0x800

MAGICS = [b'TK5RESU1', b'TIM2', b'COM ', b'GYM1', b'BDPK', b'NUDP', b'MIF\x00',
          b'P3Dp', b'BHEV', b'UPDT', b'\x00\x00\x00\x00']
STRINGS = [b'item_force', b'RankingMode', b'gauge', b'Gauge', b'symbol',
           b'gem', b'Gem', b'force', b'Force', b'rank', b'Rank', b'laser',
           b'devil', b'Devil', b'gym_', b'mon_', b'DEVILJIN', b'moj_stg',
           b'door', b'heal', b'drain']
ONE_MILLION = 1000000

def fetch(iso_start, nbytes, retries=4):
    for attempt in range(retries):
        try:
            req = urllib.request.Request(
                URL, headers={"Range": f"bytes={iso_start}-{iso_start + nbytes - 1}"})
            with urllib.request.urlopen(req, timeout=60) as r:
                if r.status not in (200, 206):
                    raise RuntimeError(f"HTTP {r.status}")
                data = r.read()
            if len(data) != nbytes:
                raise RuntimeError(f"short read {len(data)} != {nbytes}")
            return data
        except Exception:
            if attempt == retries - 1:
                raise
            time.sleep(5)

def classify(buf):
    magic = None
    for m in MAGICS:
        if m in buf[:64]:
            magic = m.decode('ascii', 'replace').strip('\x00') or 'zero-head'
            break
    printable = sum(1 for c in buf if 32 <= c < 127 or c in (10, 13, 9))
    pfrac = round(printable / max(1, len(buf)), 4)
    str_hits = []
    for s in STRINGS:
        j = buf.find(s)
        if j >= 0:
            str_hits.append({'s': s.decode(), 'off': j})
    m1 = []
    for (v,) in struct.iter_unpack('<I', buf[:len(buf) // 4 * 4]):
        if v == ONE_MILLION:
            m1.append(1)
    return {'magic': magic, 'printable_frac': pfrac,
            'string_hits': str_hits, 'u32_1M_count': len(m1)}

def scan_entry(args):
    indx, sector, size = args
    if size == 0xFFFFFFFF or size < 104:
        return {'index': indx, 'sector': sector, 'size': size, 'status': 'skipped'}
    nbytes = min(size, 2048)
    try:
        raw = fetch(ISO_OFF + sector * SECTOR, nbytes)
    except Exception as e:
        return {'index': indx, 'sector': sector, 'size': size,
                'status': 'fetch_error', 'error': str(e)[:200]}
    for mode in ('raw', 'decrypted'):
        b = raw
        if mode == 'decrypted':
            b = bytearray(raw)
            decrypt_sector_data_fast(b, indx, len(b))
            b = bytes(b)
        c = classify(b)
        # accept this buffer if it has a magic, or is strongly printable
        if c['magic'] or c['printable_frac'] > 0.85 or c['string_hits']:
            return {'index': indx, 'sector': sector, 'size': size,
                    'status': 'classified', 'crypto': mode, **c}
    # neither buffer looked structured: report the decrypted one as binary
    b = bytearray(raw)
    decrypt_sector_data_fast(b, indx, len(b))
    c = classify(bytes(b))
    return {'index': indx, 'sector': sector, 'size': size,
            'status': 'binary', 'crypto': 'decrypted', **c}

def main():
    code_path, out_path = sys.argv[1], sys.argv[2]
    nstreams = int(sys.argv[3]) if len(sys.argv) > 3 else 16
    with open(code_path, 'rb') as f:
        f.seek(TABLESTART)
        lut = f.read(TABLECOUNT * 8)
    entries = [struct.unpack_from('<II', lut, i * 8) for i in range(TABLECOUNT)]
    print(f"LUT: {len(entries)} entries", flush=True)
    rows, t0 = [], time.time()
    with ThreadPoolExecutor(max_workers=nstreams) as ex:
        for i, row in enumerate(ex.map(scan_entry, [(i, s, z) for i, (s, z) in enumerate(entries)])):
            rows.append(row)
            if (i + 1) % 200 == 0:
                print(f"  {i+1}/{len(entries)} entries, {time.time()-t0:.0f}s", flush=True)
    from collections import Counter
    summary = {'total': len(rows),
               'by_status': dict(Counter(r['status'] for r in rows)),
               'by_magic': dict(Counter(r.get('magic') for r in rows if r.get('magic'))),
               'with_string_hits': sum(1 for r in rows if r.get('string_hits')),
               'with_u32_1M': sum(1 for r in rows if r.get('u32_1M_count'))}
    result = {'source': 'TK5DATA1.BIN via PS2 LUT (Code blob TABLESTART 0x0027B5B0), Internet Archive item slus-210.59.-tekken-5',
              'method': 'first min(size,2048) bytes per entry, raw then sector-cipher (seed = entry index)',
              'summary': summary, 'entries': rows}
    with open(out_path, 'w') as f:
        json.dump(result, f, indent=1)
    print(f"done: {summary} -> {out_path}", flush=True)

if __name__ == '__main__':
    main()
