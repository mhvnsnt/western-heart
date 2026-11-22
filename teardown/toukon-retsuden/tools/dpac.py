#!/usr/bin/env python3
"""Parse a Yuke's DPAC archive (Toukon Retsuden DTPAC.PAC).

Header (observed):
  0x00 "DPAC" magic
  0x04 u32 version? (0x00000100)
  0x08 u32 entry count (0x91 = 145)
  0x0C u32 first-data offset? (0x1220)
  0x10 u32 total size? (0x2CF800)
  0x14..0x800 padding
  0x800 entry table: 32 bytes each:
    0x00 name, 16 bytes (Shift-JIS, space-padded)
    0x10 u32 field A
    0x14 u32 field B
    0x18 u32 field C
    0x1C u32 field D
Usage:
  python3 dpac.py list <file.pac>            # list entries
  python3 dpac.py extract <file.pac> <outdir>  # extract entries (needs offset/size mapping)
"""
import json
import struct
import sys
from pathlib import Path

HEADER_SIZE = 0x800
ENTRY_SIZE = 0x20


def parse_table(path):
    data = Path(path).read_bytes()
    assert data[:4] == b"DPAC", "not a DPAC file"
    version, count, first, total = struct.unpack_from("<IIII", data, 4)
    entries = []
    for i in range(count):
        off = HEADER_SIZE + i * ENTRY_SIZE
        raw = data[off:off + ENTRY_SIZE]
        name = raw[:16].rstrip(b" \x00")
        a, b, c, d = struct.unpack_from("<IIII", raw, 16)
        try:
            name_s = name.decode("shift_jis")
        except UnicodeDecodeError:
            name_s = name.decode("shift_jis", errors="replace")
        entries.append({"index": i, "name": name_s, "a": a, "b": b, "c": c, "d": d})
    return {"version": version, "count": count, "first": first, "total": total,
            "file_size": len(data), "entries": entries}


def extract_entry(data, entry, outdir):
    """Data area: file offset = b * 0x800 (b = absolute 2048-byte sector)."""
    off = entry["b"] * 0x800
    blob = data[off:off + entry["a"]]
    dest = Path(outdir) / (entry["name"] + ".bin")
    dest.write_bytes(blob)
    return dest


if __name__ == "__main__":
    cmd, path = sys.argv[1], sys.argv[2]
    info = parse_table(path)
    if cmd == "list":
        print(f"version={info['version']:#x} count={info['count']} "
              f"first={info['first']:#x} total={info['total']:#x} "
              f"file_size={info['file_size']:#x}")
        for e in info["entries"]:
            print(f"{e['index']:3d} {e['name']!r:24s} a={e['a']:#010x} b={e['b']:#010x} "
                  f"c={e['c']:#010x} d={e['d']:#010x}")
    elif cmd == "json":
        out = sys.argv[3]
        Path(out).write_text(json.dumps(info, ensure_ascii=False, indent=1))
        print(f"wrote {out}")
    elif cmd == "extract":
        outdir = sys.argv[3]
        names = sys.argv[4:]  # optional: only these entries
        data = Path(path).read_bytes()
        for e in info["entries"]:
            if names and e["name"] not in names:
                continue
            dest = extract_entry(data, e, outdir)
            print(f"{e['name']}: {e['a']} bytes -> {dest}")
    elif cmd == "extract-all":
        outdir = sys.argv[3]
        data = Path(path).read_bytes()
        for e in info["entries"]:
            dest = extract_entry(data, e, outdir)
            print(f"{e['name']}: {e['a']} bytes")
