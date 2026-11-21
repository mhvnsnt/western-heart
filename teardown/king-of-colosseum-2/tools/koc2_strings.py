#!/usr/bin/env python3
"""koc2_strings.py — parse King of Colosseum II's master string table.

The game's text lives in KC2FIRE.000 file 02010 (197,125 bytes), a
master data file with this layout (reverse-engineered 2026-11-19):

  Header (12 bytes): u32 category_count (= 25),
      u32 total_string_count (= 4021, includes one empty entry),
      u32 string_table_bytes (= 68237).
  Category index (25 x 8 bytes at 0x10): per category,
      (u16 id, u16 string_count, u32 first_string_index).
      The categories tile the string table: category 0 holds strings
      0..428 (wrestler names), category 1 holds 429..441 (styles),
      and so on through category 24 (entrance narration).
  Data region (0xD8..0x1F778): binary records that reference strings
      by index. Record layout is only partially mapped (see TEARDOWN.md
      "file 02010" section): 32-byte records occur throughout, one
      family starting with bytes 04 04 05 05 00 00 00 <index>.
  String table (last 68237 bytes, at 0x1F778): NUL-terminated
      Shift-JIS strings, 4,020 of them (plus empty entries).

The 25 categories (labels assigned from content, 2026-11-19):
  0 wrestler names (429)         13 costume parts: tights B (258)
  1 wrestle styles (13)          14 costume parts: feet (137)
  2 body types (13)              15 wrestler names, 2nd list (429)
  3 size classes (5)             16 staff / referees (23)
  4 costume types (11)           17 entrance attire (185)
  5 boolean none/exists (2)      18 gowns (2)
  6 body parts (234)             19 booleans (31)
  7 costume parts: upper A (52)  20 title names (12)
  8 costume parts: upper B (52)  21 entrance items (133)
  9 costume parts: arms A (207)  22 nicknames / catchphrases (241)
  10 costume parts: arms B (207) 23 music themes (336)
  11 costume parts: tights (406) 24 entrance narration (345)
  12 costume parts: tights A (258)

Usage:
  koc2_strings.py <file02010.bin> [output.json]
  Without an output path, JSON goes to stdout.

Lane E (KoC2), 2026-11-19.
"""
import json
import struct
import sys
from pathlib import Path

CATEGORY_LABELS = [
    "wrestler_names", "wrestle_styles", "body_types", "size_classes",
    "costume_types", "boolean", "body_parts",
    "costume_upper_a", "costume_upper_b",
    "costume_arms_a", "costume_arms_b",
    "costume_tights", "costume_tights_a", "costume_tights_b",
    "costume_feet", "wrestler_names_2", "staff_referees",
    "entrance_attire", "gowns", "booleans", "title_names",
    "entrance_items", "nicknames", "music_themes",
    "entrance_narration",
]


def parse_strings(data: bytes):
    """Parse the master string file. Returns (categories, strings)."""
    n_cat, n_str, str_bytes = struct.unpack_from("<III", data, 0)
    str_base = len(data) - str_bytes
    strings = []
    i = str_base
    while i < len(data):
        j = data.find(b"\x00", i)
        if j == -1:
            break
        raw = data[i:j]
        try:
            strings.append(raw.decode("shift_jis") if raw else "")
        except UnicodeDecodeError:
            strings.append("<0x" + raw.hex() + ">")
        i = j + 1
    categories = []
    for c in range(n_cat):
        cid, count, first = struct.unpack_from("<HHI", data, 0x10 + c * 8)
        label = CATEGORY_LABELS[cid] if cid < len(CATEGORY_LABELS) else f"cat{cid}"
        categories.append({
            "id": cid,
            "label": label,
            "first_string": first,
            "count": count,
            "strings": strings[first:first + count],
        })
    return {
        "source": "KC2FIRE.000 file 02010",
        "category_count": n_cat,
        "total_strings": n_str,
        "string_table_bytes": str_bytes,
        "strings_found": len(strings),
        "categories": categories,
    }


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    data = Path(argv[1]).read_bytes()
    result = parse_strings(data)
    text = json.dumps(result, ensure_ascii=False, indent=1)
    if len(argv) > 2:
        Path(argv[2]).write_text(text, encoding="utf-8")
        print(f"wrote {argv[2]}: {result['strings_found']} strings, "
              f"{result['category_count']} categories")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
