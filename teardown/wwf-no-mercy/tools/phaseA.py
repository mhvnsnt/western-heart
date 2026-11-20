#!/usr/bin/env python3
"""Phase A: No Mercy file-table structural survey (fast, no decoding)."""
import struct, zlib, re, json
from collections import Counter

import os
# Repo layout: FR is the teardown dir (parent of tools/). The ROM is never
# committed; place WWF No Mercy (USA) (Rev-A).z64 next to tools/.
FR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROM = os.path.join(FR, "WWF No Mercy (USA) (Rev-A).z64")
FT = 0x16C31D8
FIRST = 0x1BD150
NENT = 19459
DB = os.path.join(FR, "tools", "NoMercy-FileTableDB.txt")

d = open(ROM, "rb").read()
print(f"ROM size: {len(d)} bytes, CRC32: {zlib.crc32(d) & 0xFFFFFFFF:08X}")
table = struct.unpack(f">{NENT}I", d[FT:FT + NENT * 4])
# entries just past the game's 19,459 (VPWStudio claims 19,462)
tail = struct.unpack(">6I", d[FT + NENT * 4:FT + NENT * 4 + 24])
print("table[0] =", hex(table[0]), " table[19458] =", hex(table[19458]),
      " (end of last file)")
print("u32s past entry 19459:", [hex(x) for x in tail])
# monotonicity
mono = all((table[i] & ~1) <= (table[i + 1] & ~1) for i in range(NENT - 1))
print("monotonic (masked):", mono)
enc = sum(t & 1 for t in table[:19458])
print(f"encoded-flag files (fid 1..19458): {enc} of 19458")
lens = [(table[i + 1] & ~1) - (table[i] & ~1) for i in range(19458)]
print(f"total file bytes: {sum(lens)}  (FIRST..EOF span: {len(d) - FIRST})")
print(f"zero-length files: {sum(1 for L in lens if L == 0)}")
print(f"file 0x4C02 end offset: 0x{FIRST + (table[19458] & ~1):X} (ROM len 0x{len(d):X})")
print(f"max len: {max(lens)} (fid {lens.index(max(lens)) + 1:#x}), "
      f"min nonzero: {min(L for L in lens if L)}")

# DB parse
db = {}
for line in open(DB):
    s = line.strip()
    if not s or s.startswith("#"):
        continue
    m = re.match(r'([0-9A-Fa-f]{2,})=([A-Za-z0-9_]+);(.*)$', s)
    if m:
        db[int(m.group(1), 16)] = (m.group(2), m.group(3))
print(f"DB entries: {len(db)}, fid range {min(db):#x}..{max(db):#x}")
print("DB fids beyond 0x4C02:", sorted(f for f in db if f > 0x4C02))
print("ROM fids missing from DB:", sorted(set(range(1, 19459)) - set(db))[:20],
      "count:", len(set(range(1, 19459)) - set(db)))
print("DB type census:", Counter(t for t, _ in db.values()).most_common())

# per-type length stats + encoded counts
bytype = {}
for fid in range(1, 19459):
    t = db.get(fid, ("<no-db>", ""))[0]
    bytype.setdefault(t, []).append((fid, lens[fid - 1], table[fid - 1] & 1))
for t, rows in sorted(bytype.items(), key=lambda kv: -len(kv[1])):
    tot = sum(r[1] for r in rows)
    nenc = sum(r[2] for r in rows)
    print(f"{t:20s} n={len(rows):5d} bytes={tot:9d} encoded={nenc:5d} "
          f"len range {min(r[1] for r in rows)}..{max(r[1] for r in rows)}")
json.dump({"rom_crc32": f"{zlib.crc32(d) & 0xFFFFFFFF:08X}", "rom_size": len(d),
           "encoded_files": enc, "zero_len": sum(1 for L in lens if L == 0),
           "db_entries": len(db)},
          open(os.path.join(FR, "phaseA.json"), "w"))
