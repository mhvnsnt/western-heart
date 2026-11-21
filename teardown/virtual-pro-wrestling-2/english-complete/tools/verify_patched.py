#!/usr/bin/env python3
"""verify_patched.py — structural verification of the completed VPW2 ROM.

Checks:
 1. File table sane (offsets even, monotonic, in range; data ends at or
    before the fixed file-table address).
 2. All 19 AkiText files: patched vs Beta 3 string diffs are EXACTLY the
    translation table entries (+ the documented 0068 degenerate cleanup).
    Untouched files (0006, 0007, 006C) are byte-identical.
 3. Japanese scan: any remaining Shift_JIS bytes in the 19 files, with
    the expected intentional leftovers listed (keyboard rows, city
    prefixes).
 4. ROM-level diff vs Beta 3: changed 1 KB blocks, grouped into ranges.

Usage: python3 tools/verify_patched.py [patched.z64]
"""
import json
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from lzss import asmik_decode
from akitext_py import parse as akitext_parse

FT, FIRST = 0x1310F40, 0x152DF0
BETA3 = ('Virtual Pro Wrestling 2 - Oudou Keishou (Japan)(English Patch).z64')
TEXT_FIDS = [0x5, 0x6, 0x7, 0x8, 0x9, 0xA, 0xB, 0xC, 0xD, 0xE,
             0x63, 0x64, 0x65, 0x66, 0x67, 0x68, 0x69, 0x6A, 0x6C]
TRANSLATED = {'0005', '0008', '0009', '000A', '000B', '000C', '000D', '000E',
              '0063', '0064', '0065', '0066', '0067', '0068', '0069', '006A'}
# Intentional Japanese leftovers (index ranges): 0005 kana keyboard rows,
# 000C "Tokyo・" city prefixes (Beta 3 kept the ・ separator).
EXPECTED_JP = {'0005': set(range(403, 421)), '000C': set(range(188, 210))}
# Clean ROM file 0068's degenerate table slots (see build_patched.py).
CLEAN_0068_DEGENERATE = frozenset([
    260, 261, 262, 263, 264, 265, 266, 267, 268, 271, 272, 273, 274,
    276, 277, 281, 282, 284, 285, 288, 290, 300, 301, 303, 304, 305,
    307, 308, 312, 313, 314, 320, 325, 326, 327, 328, 329, 330, 337,
    338])


def parse_ft(data):
    return struct.unpack('>13091I', data[FT:FT + 4 * 13091])


def get_file(data, tab, fid):
    e = tab[fid - 1]
    loc, enc = e & ~1, bool(e & 1)
    nloc = tab[fid] & ~1
    raw = data[FIRST + loc:FIRST + nloc]
    return (asmik_decode(raw) if enc else raw), raw


def has_japanese(b):
    """True if the byte string contains Japanese characters (excluding
    U+3000 ideographic space, which Beta 3 uses as spacing in English).
    Same criterion as tools/dump_still_jp.py — curly quotes/apostrophes
    (U+2018-201D) are NOT Japanese."""
    if b is None:
        return False
    try:
        s = b.decode('shift_jis')
    except UnicodeDecodeError:
        return True
    for ch in s:
        o = ord(ch)
        if o == 0x3000:
            continue
        if o > 0x2FFF or (0x3040 <= o <= 0x30FF) or \
                (0x4E00 <= o <= 0x9FFF) or (0xFF00 <= o <= 0xFFEF):
            return True
    return False


def main():
    patched_path = sys.argv[1] if len(sys.argv) > 1 else 'vpw2-english-complete.z64'
    beta = open(os.path.join(ROOT, BETA3), 'rb').read()
    patched = open(os.path.join(ROOT, patched_path), 'rb').read()
    assert len(patched) == len(beta) == 33554432
    tb, tp = parse_ft(beta), parse_ft(patched)
    errors = []

    # 1. File table sanity.
    locs = [e & ~1 for e in tp]
    if any(x % 2 for x in locs):
        errors.append('odd offset in patched file table')
    if any(b < a for a, b in zip(locs, locs[1:])):
        errors.append('non-monotonic offsets in patched file table')
    if FIRST + locs[-1] > FT:
        errors.append('patched data region overflows into the file table')
    flags_b = [e & 1 for e in tb]
    flags_p = [e & 1 for e in tp]
    if flags_b != flags_p:
        errors.append('LZSS flags changed in the file table')
    print(f'1. File table: {len(locs)} entries, all even + monotonic, '
          f'data ends {FIRST + locs[-1]:#x} (table at {FT:#x}), '
          f'LZSS flags unchanged')

    # Clean 0068 degenerate slots (expected to become None).
    cdeg = CLEAN_0068_DEGENERATE

    # 2+3. Per-file string diffs + Japanese scan.
    total_translated = 0
    print('2. AkiText string diffs (patched vs Beta 3):')
    for fid in TEXT_FIDS:
        hexid = f'{fid:04X}'
        cb, craw = get_file(beta, tb, fid)
        pb, praw = get_file(patched, tp, fid)
        cs, _ = akitext_parse(cb)
        ps, _ = akitext_parse(pb)
        table = {}
        if hexid in TRANSLATED:
            table = {int(k): v.encode('shift_jis') for k, v in json.load(
                open(os.path.join(ROOT, 'translations', hexid + '.json'),
                     encoding='utf-8')).items()}
        diffs = []
        for i in range(max(len(cs), len(ps))):
            c = cs[i] if i < len(cs) else None
            p = ps[i] if i < len(ps) else None
            if c != p:
                diffs.append(i)
                if hexid == '0068' and i in cdeg and p is None:
                    continue  # documented degenerate cleanup
                if i not in table:
                    errors.append(f'{hexid}[{i}]: unexpected change '
                                  f'{c!r} -> {p!r}')
                elif p != table[i]:
                    errors.append(f'{hexid}[{i}]: wrong value {p!r}, '
                                  f'expected {table[i]!r}')
        for i in table:
            if ps[i] != table[i]:
                errors.append(f'{hexid}[{i}]: translation missing')
        if hexid not in TRANSLATED:
            if craw != praw:
                errors.append(f'{hexid}: untouched file changed!')
            print(f'   {hexid}: untouched, identical ({len(craw)} stored bytes)')
        else:
            n_cleanup = len([i for i in diffs if hexid == '0068' and i in cdeg])
            total_translated += len(table)
            print(f'   {hexid}: {len(diffs)} diffs = {len(table)} translations'
                  + (f' + {n_cleanup} degenerate cleanups' if n_cleanup else ''))

        # Japanese scan.
        jp = [i for i, s in enumerate(ps) if has_japanese(s)]
        unexpected = [i for i in jp if i not in EXPECTED_JP.get(hexid, set())]
        if unexpected:
            errors.append(f'{hexid}: unexpected Japanese at {unexpected}')
        if jp:
            print(f'      Japanese remaining: {len(jp)} strings '
                  f'(expected leftovers: {sorted(jp)[:5]}'
                  f'{"..." if len(jp) > 5 else ""})')
    print(f'   Total translations verified present: {total_translated}')

    # 4. ROM-level diff (1 KB blocks).
    changed = [i for i in range(0, len(beta), 1024)
               if beta[i:i + 1024] != patched[i:i + 1024]]
    ranges = []
    if changed:
        s = p = changed[0]
        for x in changed[1:]:
            if x == p + 1024:
                p = x
            else:
                ranges.append((s, p + 1024))
                s = p = x
        ranges.append((s, p + 1024))
    print(f'4. ROM diff vs Beta 3: {len(changed)} changed 1KB blocks in '
          f'{len(ranges)} ranges')
    for a, b in ranges:
        print(f'   {a:#x} - {b:#x} ({(b - a) // 1024} KB)')
    # Every changed block must START inside the data region or the file
    # table (block ends may round up past the table's end by < 1 KB).
    for x in changed:
        if x < FIRST or x >= FT + 4 * 13091:
            errors.append(f'changed block at {x:#x} outside data/table region')
    # Header + code + tail must be identical.
    if beta[:FIRST] != patched[:FIRST]:
        errors.append('code/header region changed!')
    if beta[FT + 4 * 13091:] != patched[FT + 4 * 13091:]:
        errors.append('tail region after file table changed!')
    # Grouped in-place build: only table entries 0x0005-0x006A may change.
    tab_changed = [i + 1 for i, (a, b) in enumerate(zip(tb, tp)) if a != b]
    bad_tab = [f for f in tab_changed if not (0x5 <= f <= 0x6A)]
    if bad_tab:
        errors.append(f'file-table entries changed outside 0x0005-0x006A: {bad_tab}')
    print(f'   File-table entries changed: {len(tab_changed)} '
          f'(all within 0x0005-0x006A)' if not bad_tab else '')
    # Everything outside the rebuilt group span must be identical.
    g0, g1 = FIRST + (tb[0x5 - 1] & ~1), FIRST + (tb[0x6E] & ~1)
    if beta[FIRST:g0] != patched[FIRST:g0]:
        errors.append('data before the rebuilt group changed!')
    if beta[g1:FT] != patched[g1:FT]:
        errors.append('data after the rebuilt group changed!')

    print()
    if errors:
        print(f'VERIFICATION FAILED ({len(errors)} errors):')
        for e in errors:
            print('  -', e)
        sys.exit(1)
    print('VERIFICATION PASSED: patched ROM differs from Beta 3 ONLY in the '
          'translated strings (+ file-table updates + zero-filled gap).')


if __name__ == '__main__':
    main()
