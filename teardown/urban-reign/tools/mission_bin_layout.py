#!/usr/bin/env python3
"""Lane 4 — mission .bin field-layout analysis. Pure measurement: per-file
u8/u16/u32/ float32 histograms, constant-vs-varying columns across all 256
files, ASCII strings, and pairwise diffs. No field meanings are asserted
unless the bytes prove them (a column that is constant in 255 files and
differs in one is a candidate, not a conclusion).
"""
import struct, json, hashlib, collections
from pathlib import Path

D = Path.home()/"workspace/urban-reign-redux/decoded/inputs/mission_defs"
OUT = Path.home()/"workspace/urban-reign-redux/decoded/missions"
OUT.mkdir(parents=True, exist_ok=True)

files = sorted(D.glob("mission*.bin"))
print("files:", len(files))
sizes = collections.Counter(f.stat().st_size for f in files)
print("sizes:", dict(sizes))
data = {f.name: f.read_bytes() for f in files}
for name, b in list(data.items())[:1]:
    print(name, len(b), "sha256", hashlib.sha256(b).hexdigest()[:16])

# u32 column census: for each 4-byte-aligned offset, how many distinct values across all files
n = min(len(b) for b in data.values())
u32_distinct = []
for off in range(0, n, 4):
    vals = {struct.unpack_from("<I", b, off)[0] for b in data.values()}
    u32_distinct.append((off, len(vals)))
const_offs = [off for off, d in u32_distinct if d == 1]
var_offs = [(off, d) for off, d in u32_distinct if d > 1]
print("u32 columns:", len(u32_distinct), "constant:", len(const_offs), "varying:", len(var_offs))
# constant column values (first file)
b0 = data[files[0].name]
const_vals = {off: struct.unpack_from("<I", b0, off)[0] for off in const_offs}
print("constant u32 columns (first 40):", {hex(k): hex(v) for k, v in list(const_vals.items())[:40]})

# u16 column census
u16_distinct = []
for off in range(0, n, 2):
    vals = {struct.unpack_from("<H", b, off)[0] for b in data.values()}
    u16_distinct.append((off, len(vals)))
print("u16 columns constant:", sum(1 for _, d in u16_distinct if d == 1), "of", len(u16_distinct))

# ASCII strings anywhere
def strings(b, minlen=4):
    out, cur = [], b""
    for ch in b:
        if 32 <= ch < 127: cur += bytes([ch])
        else:
            if len(cur) >= minlen: out.append(cur.decode())
            cur = b""
    if len(cur) >= minlen: out.append(cur.decode())
    return out
all_str = collections.Counter()
for name, b in data.items():
    for s in set(strings(b)):
        all_str[s] += 1
print("distinct ASCII strings (>=4) across all files:", len(all_str))
print("strings in >200 files:", [s for s, c in all_str.items() if c > 200][:30])
print("strings in 1-5 files (sample):", [s for s, c in all_str.items() if c <= 5][:30])

# header of mission000 vs mission100 vs mission255
for name in ("mission000.bin", "mission001.bin", "mission099.bin", "mission100.bin", "mission255.bin"):
    b = data[name]
    print(name, "u32[0:16]:", [hex(x) for x in struct.unpack_from("<16I", b, 0)])
    print(name, "first 64 bytes hex:", b[:64].hex())

# How different are consecutive files? (byte-diff counts)
import itertools
diffs = []
names = sorted(data)
for a, bb in zip(names, names[1:]):
    d = sum(1 for x, y in zip(data[a], data[bb]) if x != y)
    diffs.append(d)
print("consecutive-file byte diffs: min", min(diffs), "max", max(diffs), "mean", sum(diffs)/len(diffs))

# varying u32 columns: value ranges
var_summary = []
for off, d in var_offs:
    vals = [struct.unpack_from("<I", b, off)[0] for b in data.values()]
    var_summary.append({"offset": off, "offset_hex": hex(off), "distinct": d,
                        "min": min(vals), "max": max(vals)})
(OUT/"mission_bin_layout.json").write_text(json.dumps({
    "file_count": len(files), "sizes": {str(k): v for k, v in sizes.items()},
    "sha256_first": hashlib.sha256(data["mission000.bin"]).hexdigest(),
    "constant_u32_columns": {str(k): v for k, v in const_vals.items()},
    "varying_u32_columns": var_summary,
    "strings_in_gt200_files": [s for s, c in all_str.items() if c > 200],
    "strings_sample_rare": [s for s, c in all_str.items() if c <= 5][:100],
    "consecutive_diff_min": min(diffs), "consecutive_diff_max": max(diffs),
    "consecutive_diff_mean": sum(diffs)/len(diffs),
}, indent=2))
print("wrote mission_bin_layout.json")
