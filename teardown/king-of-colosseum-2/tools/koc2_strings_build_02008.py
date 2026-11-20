#!/usr/bin/env python3
"""koc2_strings_build_02008.py — rebuild KoC2's move-name table (file 02008).

Mirror of koc2_strings_build.py for the 02008 layout (verified
2026-11-19 from the raw file):
  Header (16 bytes): u32 category_count (85), u32 total_strings
      (3022), u32 string_table_bytes, u32 0.
  Category index (85 x 8 bytes at 0x10): (u16 type, u16 count,
      u32 first_index). Counts sum to 3022; first values tile.
  Record table (0x2B8..0x9060): 3022 x 12-byte records, one per
      string, in order. Record field u32 @0x00 = byte offset of the
      string in the string table (verified 3022/3022: offsets are
      strictly increasing and tile the table exactly, one segment
      per record — no sharing, unlike 02010). The other two fields
      are metadata (u32 @0x04: 267 distinct values, 0..65691; u32
      @0x08: nonzero in exactly 85 records) and are copied verbatim
      — ONLY the offset field is recomputed. (An earlier docstring
      guessed these were "index" and "0"; that was wrong.)
  String table (last string_table_bytes bytes): 3022 NUL-terminated
      Shift-JIS strings, in record order.

Translation input: a JSON object mapping RECORD index (as a string)
to the new text. Records not in the map are kept verbatim. New text
is encoded as Shift-JIS (plain ASCII is a subset, so English text
encodes directly). The header's category_count and total_strings
are kept as-is; string_table_bytes is updated to the new table size.
After building, the output is re-parsed and every record offset is
verified against the new table.

Usage:
  koc2_strings_build_02008.py <file02008.bin> <translations.json> <output.bin>
  translations.json: {"0": "Do Nothing", "1": "...", ...}
  (keys are RECORD indices; work/translations-02008.json)

KoC2 English lane, 2026-11-19.
"""
import json
import struct
import sys
from pathlib import Path

N_CAT = 85
N_STR = 3022
CAT_BASE = 0x10
REC_BASE = 0x10 + N_CAT * 8  # 0x2B8
REC_SIZE = 12


def parse_segments(data: bytes):
    n_cat, n_str, str_bytes = struct.unpack_from("<III", data, 0)
    assert n_cat == N_CAT and n_str == N_STR, \
        f"unexpected header: {n_cat} cats, {n_str} strings"
    str_base = len(data) - str_bytes
    assert str_base == REC_BASE + N_STR * REC_SIZE, \
        f"string table base {str_base:#x} != records end"
    segments = []
    i = str_base
    while i < len(data):
        j = data.find(b"\x00", i)
        if j == -1:
            raise ValueError("unterminated string in table")
        segments.append(data[i:j])
        i = j + 1
    return n_cat, n_str, str_bytes, str_base, segments


def build(data: bytes, translations: dict) -> bytes:
    n_cat, n_str, str_bytes, str_base, segments = parse_segments(data)
    assert len(segments) == N_STR, \
        f"expected {N_STR} segments, got {len(segments)}"
    # Verify the input record offsets tile the table (1:1 with segments).
    for k in range(N_STR):
        off = struct.unpack_from("<I", data, REC_BASE + k * REC_SIZE)[0]
        want = sum(len(s) + 1 for s in segments[:k])
        assert off == want, f"record {k}: offset {off} != {want}"
    new_segments = []
    n_changed = 0
    for idx, seg in enumerate(segments):
        key = str(idx)
        if key in translations:
            new_segments.append(translations[key].encode("shift_jis"))
            n_changed += 1
        else:
            new_segments.append(seg)
    new_offsets = []
    off = 0
    for seg in new_segments:
        new_offsets.append(off)
        off += len(seg) + 1
    new_table = b"".join(s + b"\x00" for s in new_segments)
    assert len(new_table) == off
    out = bytearray()
    out += data[:0x10]
    struct.pack_into("<III", out, 0, n_cat, n_str, len(new_table))
    out += data[0x10:REC_BASE]  # category index, verbatim
    # Record table: copy verbatim, then rewrite each offset field.
    records = bytearray(data[REC_BASE:str_base])
    assert len(records) == N_STR * REC_SIZE
    for k in range(N_STR):
        struct.pack_into("<I", records, k * REC_SIZE, new_offsets[k])
    out += records
    out += new_table
    print(f"segments: {len(segments)}, changed: {n_changed}, "
          f"table {str_bytes} -> {len(new_table)} bytes, "
          f"file {len(data)} -> {len(out)} bytes")
    # Self-check: re-parse the output and verify every record offset.
    _, _, _, new_base, new_segs = parse_segments(bytes(out))
    check_offs = []
    o = 0
    for seg in new_segs:
        check_offs.append(o)
        o += len(seg) + 1
    for k in range(N_STR):
        got = struct.unpack_from("<I", out, REC_BASE + k * REC_SIZE)[0]
        assert got == check_offs[k], f"record {k}: offset {got} != {check_offs[k]}"
    print(f"self-check OK: all {N_STR} record offsets verified")
    return bytes(out)


def main(argv):
    if len(argv) < 4:
        print(__doc__.split("Usage:")[1].strip(), file=sys.stderr)
        return 2
    data = Path(argv[1]).read_bytes()
    translations = json.loads(Path(argv[2]).read_text(encoding="utf-8"))
    out = build(data, translations)
    Path(argv[3]).write_bytes(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
