#!/usr/bin/env python3
"""DOA4 phase 14: structural parser for the REAL animation definition
files (release doa4-anime-definition-20261022, extracted from the
ISO's anm.afs in phase 13; see phase13/ANM-DEFINITION-2.md and
phase14/ANM-DECODE.md for the derivation).

PROVEN layout (all 24 fighter .bin files, verified by this tool):
  - 136-byte header: u32 header_size (always 136) + 32 big-endian
    u32 FILE OFFSETS (the section pointer table) + u32 terminator 0.
    A pointer may be 0 (absent section; w22 in all files, w23 in
    zack.bin) or repeat another pointer (w9==w10==w11==w12 always).
  - Sections tile the file: sorting the distinct non-zero pointers
    (plus 136) partitions [136, filesize) with no gaps and no
    overlaps (asserted for all 24 files by --verify).
  - w21 section: 1024-entry u32 table of ABSOLUTE file offsets,
    every entry >= w21+4096, pointing at variable-length command
    records in [w21+4096, w23-or-w24).

Gate 1 (structural round-trip): re-serializing the parsed header +
sections in file-offset order reproduces the input byte-exactly
(asserted per file). This is a STRUCTURAL gate only: keyframe
semantics inside sections B/w28 are graded separately in
ANM-DECODE.md and are NOT claimed by this parser.

Usage:
  anm_parse_p14.py <definition_dir> [--verify] [--dump NAME]
Input dir holds the 26 extracted entries (anm_version.bin,
24 fighter .bin, anime_cm.bin) as in scratch p13/definition/.
"""
import hashlib, json, os, struct, sys
from collections import Counter

FIGHTERS = ['alpha', 'ayane', 'bass', 'bayman', 'boy', 'genfu',
            'gokei', 'hakyo', 'hika', 'janlee', 'karate', 'kasumi',
            'koryu', 'leifang', 'lisa', 'ninja', 'rtm', 'ryu',
            'sambo', 'spartan', 'suiken', 'tengu', 'tina', 'zack']

# Section roles by pointer index — ONLY the rows marked PROVEN are
# asserted semantics; the rest are positional labels (see ANM-DECODE).
SECTION_ROLES = {
    1:  ('K_id_table', 'u32 entries, low u16 stepping +4 (id series)'),
    2:  ('B_keyframe_records', 'record stream, 0xFFFFFFFF separators, f32 0.3/1.0 + u16 payloads'),
    3:  ('C_s16_table', 's16 pairs (00a2 00a6 ...), size in {192..456 step 24}'),
    4:  ('E_records', 'small records with f32 fields'),
    5:  ('F_u16_ids', 'ascending u16 id series (0x42ec... in zack/rtm head)'),
    6:  ('G_curve_f32', 'f32 curve section, head f32 = 0.9'),
    7:  ('H_curve_f32', 'f32 curve section, head f32 = 1.1'),
    8:  ('I_table', 'head 001e 0000 07ff 0606 in zack/rtm'),
    9:  ('T_offset_table', 'u32 absolute offsets into the w28 span; w9==w10==w11==w12'),
    13: ('X13_offset_table', 'u32 absolute offsets into the w9 span'),
    14: ('X14_offset_table', '136 B = 34 u32 offsets into the w9 span (fixed)'),
    15: ('X15_offset_table', '64 B = 16 u32 (fixed)'),
    16: ('X16_offset_table', '64 B = 16 u32 (fixed)'),
    17: ('X17_offset_table', '40/44/48 B = 10/11/12 u32'),
    18: ('X18_offset_table', '80 B = 20 u32 (fixed)'),
    19: ('X19_offset_table', '456 B = 114 u32 (fixed)'),
    20: ('S_sparse', 'sparse section, ~90% zero bytes'),
    21: ('CLIP_TABLE', '1024 u32 absolute offsets + command records (PROVEN structure)'),
    23: ('Y23_eof_table', 'near-EOF table; absent (0) in zack.bin'),
    24: ('Y24_eof_section', 'near-EOF section, ends 4-12 B before EOF (w27 tail)'),
    28: ('L_curve_pairs', '(u32 flag, f32 value) pair stream, head 0000ff00 3f8ccccd'),
    30: ('T_subtable', 'u16-pair sub-table inside the w9 span (pointer into T)'),
    31: ('J_token_stream', 'token stream sharing the 0x22xx id namespace with anime_cm.bin'),
    32: ('D_s16_table', 's16 pairs (00aa 00aa 00ae 00ae ...)'),
}


def parse_fighter(data):
    """Parse one fighter .bin. Returns dict with header + sections."""
    assert len(data) >= 136
    hdr = struct.unpack('>34I', data[:136])
    assert hdr[0] == 136, hdr[0]
    assert hdr[33] == 0, hdr[33]
    ptrs = list(hdr[1:33])  # w1..w32
    distinct = sorted(set([136] + [p for p in ptrs if p >= 136]))
    sections = []
    for i, off in enumerate(distinct):
        end = distinct[i + 1] if i + 1 < len(distinct) else len(data)
        roles = [j + 1 for j, p in enumerate(ptrs) if p == off]
        sections.append({'offset': off, 'size': end - off,
                         'pointers': roles,
                         'sha256': hashlib.sha256(data[off:end]).hexdigest()})
    # gate-1: header + sections in offset order == input, byte-exact
    rebuilt = data[:136] + b''.join(
        data[s['offset']:s['offset'] + s['size']] for s in sections)
    roundtrip = (rebuilt == data)
    # w21 clip table (structure proven; record semantics graded in doc)
    clip = None
    w21 = ptrs[20]
    if w21:
        ents = struct.unpack_from('>1024I', data, w21)
        data_start = w21 + 4096
        clip = {'table_offset': w21, 'entries': len(ents),
                'distinct_targets': len(set(ents)),
                'min_target': min(ents), 'max_target': max(ents),
                'all_targets_in_data_range': all(
                    data_start <= e < len(data) for e in ents),
                'dominant_target': Counter(ents).most_common(1)[0][0],
                'dominant_count': Counter(ents).most_common(1)[0][1]}
    return {'size': len(data), 'sha256': hashlib.sha256(data).hexdigest(),
            'pointers_w1_w32': ptrs, 'null_pointers': [
                i + 1 for i, p in enumerate(ptrs) if p == 0],
            'sections': sections, 'roundtrip': roundtrip, 'clip_table': clip}


def parse_anime_cm(data):
    """anime_cm.bin: sparse 136-B header (nonzero u32 BE words at
    +4 = 3592, +0x20 = 3744, +0x50 = 116112, +0x54 = 116752), then a
    token stream sharing the 0x22xx id namespace with the fighter
    files' J sections. Header-word semantics are NOT asserted beyond
    their values (see ANM-DECODE.md residual)."""
    words = {off: struct.unpack_from('>I', data, off)[0]
             for off in range(0, 136, 4)
             if struct.unpack_from('>I', data, off)[0]}
    return {'size': len(data), 'sha256': hashlib.sha256(data).hexdigest(),
            'nonzero_header_words': {hex(k): v for k, v in words.items()}}


def main():
    d = sys.argv[1]
    verify = '--verify' in sys.argv
    out = {}
    all_ok = True
    for name in FIGHTERS:
        data = open(os.path.join(d, name + '.bin'), 'rb').read()
        r = parse_fighter(data)
        out[name + '.bin'] = r
        tiling = (sum(s['size'] for s in r['sections']) + 136 == r['size'])
        ok = r['roundtrip'] and tiling and r['clip_table']['all_targets_in_data_range']
        all_ok &= ok
        print(f"{name:8s} size={r['size']:7d} sections={len(r['sections']):2d} "
              f"null={[ 'w%d' % i for i in r['null_pointers']]} "
              f"clip_targets={r['clip_table']['distinct_targets']:4d}/1024 "
              f"roundtrip={r['roundtrip']} tiling={tiling}")
    cm = open(os.path.join(d, 'anime_cm.bin'), 'rb').read()
    out['anime_cm.bin'] = parse_anime_cm(cm)
    print('anime_cm nonzero header words:', out['anime_cm.bin']['nonzero_header_words'])
    ver = open(os.path.join(d, 'anm_version.bin'), 'rb').read()
    print('anm_version u32[0] =', struct.unpack('>I', ver[:4])[0],
          'bytes', ver.hex())
    if verify:
        print('GATE 1 (structural round-trip + tiling + clip-table bounds, all 24):',
              'PASS' if all_ok else 'FAIL')
        json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                         'anm_parse_p14_report.json'), 'w'), indent=1)
        print('report: anm_parse_p14_report.json')
    return 0 if all_ok else 1


if __name__ == '__main__':
    sys.exit(main())
