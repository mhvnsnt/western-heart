#!/usr/bin/env python3
"""koc2_file01999.py — survey King of Colosseum II's WrestlerData file.

KC2FIRE.000 file 01999 (1,252,521 bytes) is the file the ELF's data
loader (0x1164d0) loads for the "WrestlerData" chunk (file id 0x7CF =
1999; sibling files 2000/2001 hold "PartyData"/"TeamData"). Layout
(reverse-engineered 2026-11-19, lane W2):

  Header (16 bytes): u32 table_count (= 255), u32 ??? (= 541),
      u32 0, u32 0.
  Move-group table (255 x 64 bytes at 0x10..0x3FD0): record i starts
      with u16 i, then 4 move/motion IDs (usually 4 consecutive IDs),
      u16 count (= 4), u16 ???, u16 flags (0x0204 common; 104 records
      have the alternate shape u16@10 = 0x2801, u16@14 = 1). The rest
      of each 64-byte record is zero except at most 1 nonzero byte.
  Wrestler records (441 x 2285 bytes at 0x3FD0..0xFA015): one record
      per wrestler COSTUME (190 distinct name+nickname triples, 1-4
      records each — "up to 4 costume sets per wrestler"). Located
      fields (interior layout still open):
        +0x00  u32 ??? (varies; first record 0x06000000)
        +0x04  family name, Shift-JIS, NUL-padded (12 bytes shown)
        +0x13  given name, Shift-JIS, NUL-padded
        +0x28  nickname, Shift-JIS, NUL-padded
        +0x48  finisher name, Shift-JIS (e.g. Dragon Suplex for Fujinami)
        +0x80  stat bytes (0-12 range) and u16 tables (0-8 range)
        +0x118 move IDs / flags region
      The last 4 records (437-440) are the generic trainees
      (練習生, 練習生２号..４号).
  Tail (0xFA015..EOF): sparse, mostly zero (a mostly-empty table).

Usage:
  koc2_file01999.py <file01999.bin> [output.json]

Lane W2 (VPW2 + KoC2 RE), 2026-11-19.
"""
import json
import struct
import sys
from collections import Counter
from pathlib import Path

HEADER_SIZE = 0x10
GROUP_COUNT = 255
GROUP_SIZE = 64
WRESTLER_BASE = 0x3FD0
WRESTLER_STRIDE = 2285
WRESTLER_COUNT = 441


def sjis(raw):
    return raw.split(b"\x00")[0].decode("cp932", "replace")


def parse(path):
    d = Path(path).read_bytes()
    count, unk = struct.unpack_from("<II", d, 0)
    groups = []
    for i in range(count):
        r = d[HEADER_SIZE + i * GROUP_SIZE:
              HEADER_SIZE + (i + 1) * GROUP_SIZE]
        u16 = struct.unpack_from("<8H", r, 0)
        groups.append({
            "index": i,
            "u16_0_index": u16[0],
            "move_ids": list(u16[1:5]),
            "u16_10": u16[5],
            "u16_12": u16[6],
            "u16_14": u16[7],
            "nonzero_beyond_16": sum(1 for b in r[16:] if b),
        })
    wrestlers = []
    for i in range(WRESTLER_COUNT):
        o = WRESTLER_BASE + i * WRESTLER_STRIDE
        r = d[o:o + WRESTLER_STRIDE]
        wrestlers.append({
            "record": i,
            "offset": o,
            "u32_0": struct.unpack_from("<I", r, 0)[0],
            "family": sjis(r[4:16]),
            "given": sjis(r[0x13:0x1F]),
            "nickname": sjis(r[0x28:0x48]),
            "finisher": sjis(r[0x49:0x69]),
        })
    triples = Counter((w["family"], w["given"], w["nickname"])
                      for w in wrestlers)
    return {
        "file": Path(path).name,
        "size": len(d),
        "header": {"group_count": count, "unknown_u32_4": unk},
        "move_groups": groups,
        "wrestler_records": wrestlers,
        "wrestler_record_count": WRESTLER_COUNT,
        "wrestler_record_stride": WRESTLER_STRIDE,
        "distinct_wrestlers": len(triples),
        "costume_count_distribution":
            {str(k): v for k, v in Counter(triples.values()).items()},
        "tail_offset": WRESTLER_BASE + WRESTLER_COUNT * WRESTLER_STRIDE,
        "tail_bytes": len(d) - (WRESTLER_BASE +
                                WRESTLER_COUNT * WRESTLER_STRIDE),
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
