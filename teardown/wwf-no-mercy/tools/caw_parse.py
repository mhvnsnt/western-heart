#!/usr/bin/env python3
"""No Mercy CAW / edit-data string tables parser.

ROM: WWF No Mercy (USA) (Rev-A).z64 (32MB, big-endian .z64).

Tables covered:
  A. Name table @0x168D790: [u8 id][coded-name]00, ~60 entries
     (wrestler/theme/CAW-preset names with inline text-engine codes).
  B. Creation-suite part strings @0x168DD89+: per-category option records
     [u8 id][name+inline codes][attr bytes][terminator].

Inline codes: single bytes (incl. some printable-range bytes like 0x55 'U',
0x57 'W', 0x25 '%') that render zero-width. Stripping them yields clean
English, verified against community option lists
(re-docs/docs/ui/menus/edit-a-superstar.md). Exact per-code meaning
(color/font/kern/dictionary) needs the AKI text engine - marked OPEN.

Usage: python3 caw_parse.py [--names] [--cats] [--codes]
Outputs JSON next to the docs dir.
"""
import json, os, struct, sys

ROM = os.path.join(os.path.dirname(__file__), "..", "WWF No Mercy (USA) (Rev-A).z64")
DOCS = os.path.join(os.path.dirname(__file__), "..", "docs")

def load():
    with open(ROM, "rb") as f:
        return f.read()

def strip_codes(raw: bytes) -> str:
    """Remove inline text-engine codes -> clean display string."""
    return "".join(chr(c) for c in raw if 32 <= c < 127)

def show_codes(raw: bytes) -> str:
    return "".join(chr(c) if 32 <= c < 127 else "<%02X>" % c for c in raw)

# --- Table A: name table @0x168D790 ---
NAME_TABLE = 0x168D790
NAME_TABLE_END = 0x168D930  # wrestler table starts here

def parse_name_table(d):
    i = NAME_TABLE
    entries = []
    while i < NAME_TABLE_END - 1:
        wid = d[i]
        j = d.find(b"\x00", i + 1)
        if j < 0 or j > NAME_TABLE_END:
            break
        raw = d[i + 1:j]
        entries.append({
            "offset": "0x%08X" % i,
            "id": wid,
            "raw": show_codes(raw),
            "clean": strip_codes(raw),
        })
        i = j + 1
    return entries

# --- Table B: creation-suite strings ---
# Category boundaries found by manual inspection; each category is a run of
# records. Record shape (best current model):
#   [u8 id][name bytes + inline codes][attr bytes][terminator]
# where terminator is 00 or a 2-byte code (FB F0, FD F0, FA F1, F1 F1, ...).
# Category header records look like [u8 a][u8 b][u8 c][name]00.
CATS = [
    ("body_type",      0x168DD89, 0x168DE5D, "Body / skin-tone option strings"),
    ("elbow_pad",      0x168DE5D, 0x168DEB4, "Elbow Pad L/R options"),
    ("masks_etc_1",    0x168DEB4, 0x168DF05, "Masks/Etc + accessories (set 1)"),
    ("entrance_attire",0x168DF05, 0x168E038, "Entrance attire (accessories/hats/costumes)"),
    ("gloves",         0x168E038, 0x168E2E6, "Gloves options"),
    ("feet",           0x168E2E6, 0x168E4D5, "Feet options (boots/pads/pull-ons/athletic)"),
    ("wrist_band",     0x168E4D5, 0x168E586, "Wrist band options"),
    ("hair",           0x168E586, 0x168E696, "Hair styles"),
    ("front_hair",     0x168E696, 0x168E86F, "Front hair (mostly binary records)"),
    ("facial_hair",    0x168E86F, 0x168E877, "Facial hair"),
    ("hats_caps",      0x168E877, 0x168E8D1, "Hats / caps"),
    ("knee_pad",       0x168E8D1, 0x168E9D7, "Knee Pad L/R options"),
    ("masks",          0x168E9D7, 0x168EA6A, "Masks"),
    ("accessories",    0x168EA6A, 0x168EB20, "Accessories"),
    ("ring_attire",    0x168EB20, 0x168F800, "Ring attire (short/long/wrestling/pants/full)"),
]

def dump_cat(d, start, end):
    """Dump every 00-terminated printable run in [start,end) with raw bytes."""
    runs = []
    i = start
    while i < end:
        j = d.find(b"\x00", i)
        if j < 0 or j >= end:
            break
        raw = d[i:j]
        txt = bytes(c for c in raw if 32 <= c < 127)
        if len(txt) >= 2 and len(txt) >= len(raw) * 0.4:
            runs.append({"offset": "0x%08X" % i, "len": j - i,
                         "raw": show_codes(raw), "clean": strip_codes(raw)})
            i = j + 1
        else:
            i += 1
    return runs

def main():
    d = load()
    print("ROM size %d, CRC32 %08X" % (len(d), __import__("zlib").crc32(d) & 0xFFFFFFFF))
    if "--names" in sys.argv or len(sys.argv) == 1:
        entries = parse_name_table(d)
        print("%d name-table entries" % len(entries))
        out = os.path.join(DOCS, "caw-name-table.json")
        json.dump(entries, open(out, "w"), indent=1)
        print("wrote", out)
        for e in entries:
            print("  id=0x%02X %-28s %s" % (e["id"], e["clean"], e["offset"]))
    if "--cats" in sys.argv or len(sys.argv) == 1:
        allcats = {}
        for name, s, e, desc in CATS:
            runs = dump_cat(d, s, e)
            allcats[name] = {"desc": desc, "range": ["0x%08X" % s, "0x%08X" % e],
                             "runs": runs}
            print("%-15s 0x%08X-0x%08X  %d runs" % (name, s, e, len(runs)))
        out = os.path.join(DOCS, "caw-categories.json")
        json.dump(allcats, open(out, "w"), indent=1)
        print("wrote", out)
    if "--codes" in sys.argv or len(sys.argv) == 1:
        # inventory of non-printable bytes inside the string regions
        from collections import Counter
        cnt = Counter()
        for _, s, e, _ in CATS:
            seg = d[s:e]
            for c in seg:
                if not (32 <= c < 127) and c != 0:
                    cnt[c] += 1
        seg = d[NAME_TABLE:NAME_TABLE_END]
        for c in seg:
            if not (32 <= c < 127) and c != 0:
                cnt[c] += 1
        print("code-byte inventory (byte: count):")
        for c, n in cnt.most_common():
            print("  0x%02X: %d" % (c, n))

if __name__ == "__main__":
    main()
