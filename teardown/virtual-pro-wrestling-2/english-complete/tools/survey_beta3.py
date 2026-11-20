#!/usr/bin/env python3
"""survey_beta3.py — compare the Beta 3 English ROM's AkiText files against
the clean Japanese ROM, string by string.

Parses each ROM's own file table (Beta 3 rebuilt files, so offsets moved),
extracts + LZSS-decodes the 19 AkiText files from both, runs akitext -e,
and reports per file: how many strings Beta 3 translated, how many are
still Japanese, how many are ASCII-only (numbers, punctuation, already
English).

Usage: python3 tools/survey_beta3.py
  Inputs (workdir): vpw2-clean.z64, the Beta 3 .z64, tools/akitext,
  tools/lzss.py (asmik_decode).
  Outputs: work/beta3-survey.json (per-file counts + per-string status),
  work/beta3-text/<fid>.txt + work/clean-text/<fid>.txt (akitext dumps).
"""
import json
import os
import re
import struct
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from lzss import asmik_decode
from akitext_py import parse as akitext_parse

FT, FIRST = 0x1310F40, 0x152DF0
TEXT_FIDS = [0x5, 0x6, 0x7, 0x8, 0x9, 0xA, 0xB, 0xC, 0xD, 0xE,
             0x63, 0x64, 0x65, 0x66, 0x67, 0x68, 0x69, 0x6A, 0x6C]
LABELS = {
    0x5: 'Edit Mode strings', 0x6: 'Unlock messages?', 0x7: 'Match/Event result phrases',
    0x8: 'AkiText 03', 0x9: 'AkiText 04', 0xA: 'Options Help', 0xB: 'Parameters Help',
    0xC: 'AkiText 07', 0xD: 'RRS/KRS messages', 0xE: 'Credits',
    0x63: 'Move Names 1', 0x64: 'Move Names 2', 0x65: 'Move Names 3',
    0x66: 'Move Names 4', 0x67: 'Move Names 5', 0x68: 'Edit Mode Move Types',
    0x69: 'Match Finish Move Names', 0x6A: 'Edit Mode Costume Names',
    0x6C: 'Default Strings (Characters, Stables, Arenas, Mic Appeal)',
}


def parse_ft(data):
    return struct.unpack('>13091I', data[FT:FT + 4 * 13091])


def get_file(data, tab, fid):
    e = tab[fid - 1]
    loc, enc = e & ~1, bool(e & 1)
    nloc = tab[fid] & ~1
    raw = data[FIRST + loc:FIRST + nloc]
    return (asmik_decode(raw) if enc else raw)


def akitext_extract(blob_path, out_path):
    # Parse with the index-preserving parser (akitext's own -e mis-parses
    # Beta 3 files: it derives the table size from offsets[0], which Beta
    # 3's builder points at EOF for empty strings). Still write the
    # akitext-style .txt dump for eyeballing.
    blob = open(blob_path, 'rb').read()
    strings, degenerate = akitext_parse(blob)
    with open(out_path, 'wb') as f:
        for s in strings:
            if s is None:
                continue
            f.write(b'{"' + s + b'"}\n')
    return strings


def has_japanese(b):
    """True if the byte string contains any Shift_JIS non-ASCII byte."""
    return any(x >= 0x80 for x in b)


def main():
    clean = open(os.path.join(ROOT, 'vpw2-clean.z64'), 'rb').read()
    beta = open(os.path.join(
        ROOT, 'Virtual Pro Wrestling 2 - Oudou Keishou (Japan)(English Patch).z64'),
        'rb').read()
    tc, tb = parse_ft(clean), parse_ft(beta)
    os.makedirs(os.path.join(ROOT, 'work', 'clean-text'), exist_ok=True)
    os.makedirs(os.path.join(ROOT, 'work', 'beta3-text'), exist_ok=True)

    survey = {}
    for fid in TEXT_FIDS:
        hexid = f'{fid:04X}'
        cb = get_file(clean, tc, fid)
        bb = get_file(beta, tb, fid)
        cbin = os.path.join(ROOT, 'work', f'clean-{hexid}.bin')
        bbin = os.path.join(ROOT, 'work', f'beta3-{hexid}.bin')
        open(cbin, 'wb').write(cb)
        open(bbin, 'wb').write(bb)
        cs = akitext_extract(cbin, os.path.join(ROOT, 'work', 'clean-text', hexid + '.txt'))
        bs = akitext_extract(bbin, os.path.join(ROOT, 'work', 'beta3-text', hexid + '.txt'))
        same_blob = (cb == bb)
        status = []
        n_translated = n_still_jp = n_ascii = n_unused = 0
        for i in range(max(len(cs), len(bs))):
            c = cs[i] if i < len(cs) else None
            b = bs[i] if i < len(bs) else None
            if c is None and b is None:
                status.append('unused')
                n_unused += 1
            elif c != b:
                status.append('translated')
                n_translated += 1
            elif has_japanese(c):
                status.append('still-japanese')
                n_still_jp += 1
            else:
                status.append('ascii')
                n_ascii += 1
        survey[hexid] = {
            'label': LABELS[fid],
            'clean_entries': len(cs),
            'beta3_entries': len(bs),
            'clean_strings': sum(1 for s in cs if s is not None),
            'beta3_strings': sum(1 for s in bs if s is not None),
            'same_blob': same_blob,
            'translated': n_translated,
            'still_japanese': n_still_jp,
            'ascii': n_ascii,
            'unused': n_unused,
            'status': status,
        }
        print(f'{hexid} {LABELS[fid]:55s} entries={len(cs):4d}/{len(bs):4d} '
              f'same_blob={same_blob!s:5s} translated={n_translated:4d} '
              f'still_jp={n_still_jp:4d} ascii={n_ascii:4d} unused={n_unused:4d}')
    json.dump(survey, open(os.path.join(ROOT, 'work', 'beta3-survey.json'), 'w'),
              indent=1)
    tot_t = sum(v['translated'] for v in survey.values())
    tot_j = sum(v['still_japanese'] for v in survey.values())
    tot_a = sum(v['ascii'] for v in survey.values())
    print(f'\nTOTAL translated={tot_t} still_japanese={tot_j} ascii={tot_a}')


if __name__ == '__main__':
    main()
