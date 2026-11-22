#!/usr/bin/env python3
"""build_patched.py — build the completed VPW2 English ROM.

Base: the Beta 3 English ROM (keeps Beta 3's code patches, redrawn
textures, and translated strings). Applies translations/*.json to the
16 AkiText files they cover, rebuilds those files (suffix-sharing dedup,
like Beta 3's builder), LZSS-re-encodes them, and repacks them IN PLACE
inside Beta 3's text/texture group (file IDs 0x0005-0x006E).

Method (mirrors Beta 3's own rebuild, proven safe): Beta 3 rebuilt the
106 files in IDs 0x0005-0x006E and preserved that group's stored total
EXACTLY (219,458 bytes in both clean and Beta 3), so every file after
the group kept its original offset. We do the same: the 16 rebuilt
files shrink the group by 1,450 bytes, and file 006A (the last rebuilt
file, LZSS) absorbs the slack as trailing zero bytes after its LZSS
stream — both decoders stop at the stream's end marker and ignore
trailing zeros (verified). Files 0x006B and later keep their original
bytes AND offsets; only table entries for 0x0005-0x006A change.

0068 special case: the clean file's 40 degenerate table slots (offsets
pointing inside the table / out of range) are rebuilt as 0 (unused),
matching the clean ROM. Beta 3's builder mis-packed offset-table bytes
as garbage strings at those slots; the game never reads them.

Usage: python3 tools/build_patched.py [output.z64]
  Default output: vpw2-english-complete.z64 in the workdir.
"""
import hashlib
import json
import os
import struct
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from lzss import asmik_decode
from akitext_py import parse as akitext_parse, build as akitext_build

FT, FIRST = 0x1310F40, 0x152DF0
BETA3 = ('Virtual Pro Wrestling 2 - Oudou Keishou (Japan)(English Patch).z64')
TRANSLATED = ['0005', '0008', '0009', '000A', '000B', '000C', '000D', '000E',
              '0063', '0064', '0065', '0066', '0067', '0068', '0069', '006A']
GROUP_FIRST, GROUP_LAST = 0x0005, 0x006E  # Beta 3's rebuilt group
PAD_FILE = 0x006A  # last rebuilt file; absorbs the group's slack
# Clean ROM file 0068's degenerate table slots (offsets pointing inside
# the table or out of range — a second data structure or leftover bytes
# the game never reads). Rebuilt as 0 (unused), matching the clean ROM.
# Beta 3's builder mis-packed offset-table bytes as garbage strings at
# these slots; verified by parsing the clean ROM's 0068 with
# akitext_py.parse.
CLEAN_0068_DEGENERATE = frozenset([
    260, 261, 262, 263, 264, 265, 266, 267, 268, 271, 272, 273, 274,
    276, 277, 281, 282, 284, 285, 288, 290, 300, 301, 303, 304, 305,
    307, 308, 312, 313, 314, 320, 325, 326, 327, 328, 329, 330, 337,
    338])


def lzss_encode(blob):
    open('/tmp/vpw2-enc-in.bin', 'wb').write(blob)
    r = subprocess.run(['tools/aki_lzss', '-e', '/tmp/vpw2-enc-in.bin',
                        '/tmp/vpw2-enc-out.bin'],
                       cwd=ROOT, capture_output=True)
    assert r.returncode == 0, r.stderr.decode()
    return open('/tmp/vpw2-enc-out.bin', 'rb').read()


def main():
    out_name = sys.argv[1] if len(sys.argv) > 1 else 'vpw2-english-complete.z64'
    beta = open(os.path.join(ROOT, BETA3), 'rb').read()
    assert len(beta) == 33554432, f'unexpected Beta 3 size {len(beta)}'
    tab = struct.unpack('>13091I', beta[FT:FT + 4 * 13091])

    group_start = tab[GROUP_FIRST - 1] & ~1
    group_end = tab[GROUP_LAST] & ~1  # = file 0x006F's offset
    group_total = group_end - group_start
    print(f'Group 0x{GROUP_FIRST:04X}-0x{GROUP_LAST:04X}: rel '
          f'{group_start:#x}..{group_end:#x} (abs {FIRST + group_start:#x}..'
          f'{FIRST + group_end:#x}), total {group_total} bytes')

    # Read the group's files (stored bytes + LZSS flags).
    group = {}  # fid -> (stored bytes, lzss flag)
    for fid in range(GROUP_FIRST, GROUP_LAST + 1):
        e, n = tab[fid - 1], tab[fid]
        group[fid] = (beta[FIRST + (e & ~1):FIRST + (n & ~1)], bool(e & 1))

    # Clean 0068 degenerate slots (to zero out, matching the clean ROM).
    cdeg = CLEAN_0068_DEGENERATE

    # Rebuild the 16 translated files.
    total_delta = 0
    for hexid in TRANSLATED:
        fid = int(hexid, 16)
        raw, enc_flag = group[fid]
        assert enc_flag, f'{hexid}: expected LZSS-compressed'
        dec = asmik_decode(raw)
        strings, _ = akitext_parse(dec)
        table = json.load(open(os.path.join(ROOT, 'translations', hexid + '.json'),
                               encoding='utf-8'))
        for k, v in table.items():
            strings[int(k)] = v.encode('shift_jis')
        if hexid == '0068':
            for i in cdeg:
                strings[i] = None
        rebuilt = akitext_build(strings, dedup=True)
        chk, _ = akitext_parse(rebuilt)
        assert chk == strings, f'{hexid}: rebuilt blob parse mismatch'
        stored = lzss_encode(rebuilt)
        assert asmik_decode(stored) == rebuilt, f'{hexid}: LZSS round-trip failed'
        assert len(stored) % 2 == 0, f'{hexid}: odd stored length {len(stored)}'
        group[fid] = (stored, enc_flag)
        total_delta += len(stored) - len(raw)
        print(f'{hexid}: stored {len(raw)} -> {len(stored)} '
              f'({len(stored) - len(raw):+d})')
    print(f'Group delta before padding: {total_delta:+d} bytes')
    assert total_delta <= 0, 'group grew; padding cannot shrink it'

    # Pad 006A with trailing zeros so the group total is preserved exactly.
    pad = -total_delta
    stored, flag = group[PAD_FILE]
    group[PAD_FILE] = (stored + b'\x00' * pad, flag)
    print(f'Padded 006A with {pad} trailing zero bytes '
          f'(stored {len(stored)} -> {len(stored) + pad})')

    # Repack the group contiguously from its original start; write the
    # bytes and the changed table entries (0x0005-0x006A only).
    out = bytearray(beta)
    new_tab = list(tab)
    pos = group_start
    for fid in range(GROUP_FIRST, GROUP_LAST + 1):
        stored, enc_flag = group[fid]
        assert pos % 2 == 0, f'odd offset for file {fid:04X}'
        if fid <= PAD_FILE:
            new_tab[fid - 1] = pos | (1 if enc_flag else 0)
        else:
            # Files after the pad file must land exactly on their
            # original offsets (group total preserved).
            assert pos == (tab[fid - 1] & ~1), \
                f'file {fid:04X} moved: {pos:#x} != {tab[fid - 1] & ~1:#x}'
            assert stored == beta[FIRST + (tab[fid - 1] & ~1):
                                  FIRST + (tab[fid] & ~1)], \
                f'file {fid:04X} bytes changed (should be untouched)'
        out[FIRST + pos:FIRST + pos + len(stored)] = stored
        pos += len(stored)
    assert pos == group_end, f'group end moved: {pos:#x} != {group_end:#x}'
    assert new_tab[13090] == tab[13090], 'end sentinel changed'

    out[FT:FT + 4 * 13091] = struct.pack('>13091I', *new_tab)
    n_tab_changed = sum(1 for a, b in zip(tab, new_tab) if a != b)
    print(f'File-table entries changed: {n_tab_changed} '
          f'(all within 0x{GROUP_FIRST:04X}-0x{PAD_FILE:04X})')

    out_path = os.path.join(ROOT, out_name)
    open(out_path, 'wb').write(bytes(out))
    sha1 = hashlib.sha1(bytes(out)).hexdigest()
    print(f'\nWrote {out_path} ({len(out)} bytes)')
    print(f'SHA-1: {sha1}')


if __name__ == '__main__':
    main()
