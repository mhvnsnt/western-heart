#!/usr/bin/env python3
"""koc2_file02010.py — parse King of Colosseum II's master data file 02010.

Layout (reverse-engineered 2026-11-19, lane W2):

  Header (12 bytes): u32 category_count (= 25),
      u32 total_string_count (= 4021 logical strings),
      u32 string_table_bytes (= 68237).
  Category index (25 x 8 bytes at 0x10): per category,
      (u16 id, u16 string_count, u32 first_string_index).
      Indices are LOGICAL string numbers (see below).
  Record table (4021 x 32 bytes at 0xD8..0x1F778): one record per
      logical string, in logical order. Verified 4021/4021:
        u32 @0   = byte offset of the string in the physical string table
        u8  @6   = category index (0..24)
        u8  @28  = index within the category (0-based)
      Other fields are per-category metadata (see FILE-02010-FORMAT.md);
      category 0 (wrestler names) carries per-wrestler enums/flags.
  String table (68237 bytes at 0x1F778): NUL-terminated Shift-JIS strings.

  Logical vs physical strings: the physical table holds 4023 strings,
  but two of them are empty placeholders (physical 581 and 1354) that
  the game's logical numbering SKIPS. A third empty string (physical
  2285) IS a logical entry (logical 2283, last entry of category 14).
  Logical i -> physical i (i < 581), i+1 (581 <= i < 1353), i+2 (i >= 1353).

Usage:
  koc2_file02010.py <file02010.bin> [output.json]
  Without an output path, JSON goes to stdout.

Lane W2 (VPW2 + KoC2 RE), 2026-11-19.
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

# Physical string indices skipped by the logical numbering (empty strings).
SKIPPED_PHYSICAL = (581, 1354)

RECORD_TABLE_OFF = 0xD8
RECORD_SIZE = 32


def parse_physical_strings(table):
    """Return (offsets, texts) for every NUL-terminated string in table."""
    offsets, texts = [], []
    o = 0
    while o < len(table):
        offsets.append(o)
        j = table.find(b"\x00", o)
        if j < 0:
            break
        texts.append(table[o:j].decode("cp932", "replace"))
        o = j + 1
    return offsets, texts


def parse(path):
    d = Path(path).read_bytes()
    cat_count, total_strings, stb = struct.unpack_from("<III", d, 0)
    assert cat_count == 25, cat_count
    cats = []
    for i in range(cat_count):
        cid, cnt, first = struct.unpack_from("<HHI", d, 0x10 + 8 * i)
        cats.append({"id": cid, "count": cnt, "first": first,
                     "label": CATEGORY_LABELS[cid]})
    str_off = RECORD_TABLE_OFF + total_strings * RECORD_SIZE
    assert str_off == 0x1F778, hex(str_off)
    assert len(d) - str_off == stb, (len(d) - str_off, stb)
    poffs, ptexts = parse_physical_strings(d[str_off:])
    # logical -> physical offset, using the skip rule
    def phys_off(i):
        # physical index of logical i
        p = i
        for s in SKIPPED_PHYSICAL:
            if s <= p:
                p += 1
        return poffs[p]

    records = []
    verified_offset = 0
    verified_cat = 0
    verified_idx = 0
    for i in range(total_strings):
        r = d[RECORD_TABLE_OFF + i * RECORD_SIZE:
              RECORD_TABLE_OFF + (i + 1) * RECORD_SIZE]
        f0, = struct.unpack_from("<I", r, 0)
        cat = r[6]
        idx_in_cat = r[28]
        # category of logical string i (from the header index)
        cat_i = next(c["id"] for c in cats
                     if c["first"] <= i < c["first"] + c["count"])
        if f0 == phys_off(i):
            verified_offset += 1
        if cat == cat_i:
            verified_cat += 1
        if idx_in_cat == i - next(c["first"] for c in cats
                                  if c["id"] == cat_i):
            verified_idx += 1
        p = i
        for s in SKIPPED_PHYSICAL:
            if s <= p:
                p += 1
        records.append({
            "index": i,
            "physical_index": p,
            "category": cat_i,
            "category_label": CATEGORY_LABELS[cat_i],
            "index_in_category": idx_in_cat,
            "string": ptexts[p],
            "string_offset": f0,
            "u16_4": struct.unpack_from("<H", r, 4)[0],
            "byte_5": r[5],
            "byte_7": r[7],
            "u32_8": struct.unpack_from("<I", r, 8)[0],
            "byte_12": r[12],
            "byte_13": r[13],
            "byte_14": r[14],
            "byte_15": r[15],
            "u16_16": struct.unpack_from("<H", r, 16)[0],
            "u16_18": struct.unpack_from("<H", r, 18)[0],
            "bytes_20_24": list(r[20:25]),
            "byte_25": r[25],
            "byte_26": r[26],
            "byte_27": r[27],
            "byte_29": r[29],
            "byte_30": r[30],
            "byte_31": r[31],
        })
    return {
        "file": Path(path).name,
        "category_count": cat_count,
        "total_logical_strings": total_strings,
        "total_physical_strings": len(ptexts),
        "skipped_physical_indices": list(SKIPPED_PHYSICAL),
        "string_table_bytes": stb,
        "categories": cats,
        "verification": {
            "u32_0_is_string_offset": f"{verified_offset}/{total_strings}",
            "byte_6_is_category": f"{verified_cat}/{total_strings}",
            "byte_28_is_index_in_category":
                f"{verified_idx}/{total_strings}",
        },
        "records": records,
    }


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    out = parse(sys.argv[1])
    text = json.dumps(out, ensure_ascii=False, indent=1)
    if len(sys.argv) > 2:
        Path(sys.argv[2]).write_text(text, encoding="utf-8")
    else:
        print(text)


if __name__ == "__main__":
    main()
