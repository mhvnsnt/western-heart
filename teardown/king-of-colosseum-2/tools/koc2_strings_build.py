#!/usr/bin/env python3
"""koc2_strings_build.py — rebuild KoC2's master string table (file 02010).

Inverse of koc2_strings.py. The file layout (validated 2026-11-19,
record table cracked by lane W2 — see docs/FILE-02010-FORMAT.md):
  Header (12 bytes): u32 category_count (25), u32 total_logical_strings
      (4021), u32 string_table_bytes.
  Category index (25 x 8 bytes at 0x10): (u16 id, u16 count,
      u32 first_logical_index). Categories tile LOGICAL indices 0..4020.
  Record table (0xD8..0x1F778): 4021 x 32-byte records, one per LOGICAL
      string, in order. Record field u32 @0x00 = byte offset of the
      string in the PHYSICAL string table (verified 4021/4021). All
      other record fields are metadata (person id, federation,
      bitfields, ratings, index-within-category) and are copied
      verbatim — ONLY the offset field is recomputed.
  String table (last string_table_bytes bytes): NUL-terminated
      Shift-JIS strings. The physical table holds 4023 segments; the
      logical numbering has 4021 because two empty physical strings
      (indices 581 and 1354) are skipped:
          logical i -> physical i       (i < 581)
          logical i -> physical i + 1   (581 <= i < 1353)
          logical i -> physical i + 2   (i >= 1353)
      A third empty string (physical 2285) IS logical 2283. Two
      trailing strings (physical 4021, 4022: "Edit Wrestler" /
      "Original Wrestler") are beyond the logical range but are
      preserved in order like all other segments.

Translation input: a JSON object mapping PHYSICAL segment index (as a
string) to the new text. Segments not in the map are kept verbatim.
New text is encoded as Shift-JIS (plain ASCII is a subset, so English
text encodes directly). The header's category_count and
total_logical_strings are kept as-is; string_table_bytes is updated
to the new table size. After building, the output is re-parsed and
every record offset is verified against the new table.

Usage:
  koc2_strings_build.py <file02010.bin> <translations.json> <output.bin>
  translations.json: {"0": "Tatsumi Fujinami", "1": "...", ...}
  (keys are PHYSICAL segment indices)

KoC2 English lane, 2026-11-19.
"""
import json
import struct
import sys
from pathlib import Path

N_LOGICAL = 4021
SKIP_PHYSICAL = (581, 1354)  # empty physical strings, not logical


def logical_to_physical(logical: int) -> int:
    if logical < 581:
        return logical
    if logical < 1353:
        return logical + 1
    return logical + 2


def parse_segments(data: bytes):
    n_cat, n_str, str_bytes = struct.unpack_from("<III", data, 0)
    str_base = len(data) - str_bytes
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
    assert len(segments) == 4023, f"expected 4023 segments, got {len(segments)}"
    new_segments = []
    n_changed = 0
    for idx, seg in enumerate(segments):
        key = str(idx)
        if key in translations:
            new_segments.append(translations[key].encode("shift_jis"))
            n_changed += 1
        else:
            new_segments.append(seg)
    # New physical offsets (cumulative byte offsets in the new table).
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
    out += data[0x10:0xD8]  # category index, verbatim
    # Record table: copy verbatim, then rewrite each offset field.
    records = bytearray(data[0xD8:str_base])
    assert len(records) == N_LOGICAL * 32
    for logical in range(N_LOGICAL):
        phys = logical_to_physical(logical)
        struct.pack_into("<I", records, logical * 32, new_offsets[phys])
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
    for logical in range(N_LOGICAL):
        got = struct.unpack_from("<I", out, 0xD8 + logical * 32)[0]
        want = check_offs[logical_to_physical(logical)]
        assert got == want, f"record {logical}: offset {got} != {want}"
    print(f"self-check OK: all {N_LOGICAL} record offsets verified")
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
