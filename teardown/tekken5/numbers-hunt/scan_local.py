#!/usr/bin/env python3
"""Local scan of a (possibly partially downloaded) BIN file.

Scans only the byte ranges marked complete in <file>.ranges.json (or the
whole file with --all), for DW-relevant strings, magic numbers and the
6 missing filenames. Records offset + pattern + 48-byte context per hit.
Also emits a per-16MB window profile (fraction printable-ASCII, fraction
zero) to map plaintext vs encrypted/compressed regions.

Usage: scan_local.py <binfile> <out.json> [--all]
"""
import json
import struct
import sys

PATTERNS = [
    # DW-relevant strings (same set as the stream scans, + extras)
    b'item_force', b'force', b'Force', b'FORCE',
    b'gem', b'Gem', b'GEM',
    b'symbol', b'Symbol', b'SYMBOL',
    b'laser', b'Laser', b'rank', b'Rank', b'gauge', b'Gauge',
    b'drain', b'Drain', b'heal', b'Heal',
    b'devil', b'Devil', b'DEVIL', b'door', b'Door', b'DOOR',
    b'gym_', b'mon_', b'romD', b'moj_stg', b'gym_init_obj',
    b'DEVILJIN', b'deviljin', b'RankingMode',
    # the 6 missing filenames (without .dat, and with)
    b'gym_ozhe_1ckj66a', b'katgym_Bbr_bbblow', b'katgym_Gan_mekin',
    b'testchr1', b'testchr2', b'testchr3',
    # magics / container markers
    b'GYM1', b'BDPK', b'TK5RESU1', b'TIM2', b'NUDP', b'MIF\x00',
    b'P3Dp', b'COM ',
]

CHUNK = 10 * 1024 * 1024  # must match fetch_range.py chunk size


def scan_range(d, base, out_hits):
    for pat in PATTERNS:
        idx = 0
        while True:
            j = d.find(pat, idx)
            if j < 0:
                break
            abs_off = base + j
            ctx = d[max(0, j - 16):j + len(pat) + 32]
            out_hits.append({
                'offset': abs_off,
                'pattern': pat.decode('ascii', 'replace'),
                'context_hex': ctx.hex(),
                'context_ascii': ''.join(chr(c) if 32 <= c < 127 else '.' for c in ctx),
            })
            idx = j + 1
            if len(out_hits) > 200000:
                return


def main():
    path, out_path = sys.argv[1], sys.argv[2]
    scan_all = '--all' in sys.argv
    size = __import__('os').path.getsize(path)
    nchunks = (size + CHUNK - 1) // CHUNK
    done = [True] * nchunks
    if not scan_all:
        try:
            with open(path + '.ranges.json') as f:
                st = json.load(f)
            done = st['done']
        except OSError:
            print('no ranges.json; use --all to scan the whole file', file=sys.stderr)
            return 1
    hits = []
    profile = []
    with open(path, 'rb') as f:
        for i, is_done in enumerate(done):
            if not is_done:
                continue
            f.seek(i * CHUNK)
            d = f.read(CHUNK)
            if not d:
                break
            scan_range(d, i * CHUNK, hits)
            # 16MB window profile (chunk is 10MB; profile per chunk)
            printable = sum(1 for c in d if 32 <= c < 127 or c in (10, 13, 9))
            zeros = d.count(0)
            profile.append({
                'chunk': i, 'offset': i * CHUNK,
                'printable_frac': round(printable / len(d), 4),
                'zero_frac': round(zeros / len(d), 4),
            })
    result = {
        'source': path, 'size_bytes': size,
        'chunks_scanned': sum(done), 'chunks_total': nchunks,
        'patterns': [p.decode('ascii') for p in PATTERNS],
        'hits_total': len(hits), 'hits': hits,
        'profile': profile,
    }
    with open(out_path, 'w') as f:
        json.dump(result, f, indent=1)
    from collections import Counter
    print(f"scanned {sum(done)}/{nchunks} chunks, {len(hits)} hits -> {out_path}")
    print(Counter(h['pattern'] for h in hits).most_common(25))
    return 0


if __name__ == '__main__':
    sys.exit(main())
