#!/usr/bin/env python3
"""kc2_afs.py — extract the standard AFS archive KC2FIRE.AFS (King of Colosseum II).

AFS is CRI's archive format (also used by many PS2 games). Layout,
verified against KC2FIRE.AFS 2026-11-19:

  Header: magic "AFS\\0" (4 B), file_count u32 LE.
  Entry table: file_count x 8-byte entries: (u32 offset, u32 size).
    File data starts at the first entry's offset (0x12000 here); the
    region between the table end and the first file holds the name
    table pointer: (u32 name_table_offset, u32 name_table_size).
  Name table: file_count x 48-byte records: 32-byte NUL-padded filename
    + 16 bytes of metadata (file date + an unknown u32; the metadata is
    not needed for extraction). Names are in entry-table order.
    The table is padded with zeros to a 2048-byte boundary at EOF.

KoC2's AFS holds 9,003 files, mostly .adx audio (CRI ADX, magic 0x8000)
plus other assets; the name table gives every file its real name.

Usage:
  kc2_afs.py <archive.afs> <outdir> [--index-only]
  --index-only writes only index.csv (id, offset, size, name).
  Files are extracted under their real names (sanitised); a manifest
  index.csv records the id -> name mapping.

Lane E (KoC2), 2026-11-19.
"""
import csv
import mmap
import struct
import sys
from pathlib import Path


def parse_index(data: bytes):
    if data[:4] != b"AFS\x00":
        raise ValueError("not an AFS archive (bad magic)")
    (count,) = struct.unpack_from("<I", data, 4)
    entries = []
    for i in range(count):
        off, size = struct.unpack_from("<II", data, 8 + i * 8)
        entries.append({"id": i, "offset": off, "size": size, "name": None})
    nt_off, nt_size = struct.unpack_from("<II", data, 8 + count * 8)
    if nt_off and nt_off + count * 48 <= len(data):
        for i in range(count):
            raw = data[nt_off + i * 48: nt_off + i * 48 + 32]
            name = raw.split(b"\x00", 1)[0].decode("ascii", "replace")
            entries[i]["name"] = name
    return entries


def safe_name(name: str, fid: int) -> str:
    """Sanitise an archive filename for extraction."""
    keep = name.replace("\\", "/").strip("/")
    parts = [p for p in keep.split("/") if p not in ("", ".", "..")]
    if not parts:
        return f"file{fid:05d}.bin"
    return "/".join(parts)


def extract(archive: Path, outdir: Path, index_only: bool = False):
    with open(archive, "rb") as fh:
        data = mmap.mmap(fh.fileno(), 0, access=mmap.ACCESS_READ)
        entries = parse_index(data)
        outdir.mkdir(parents=True, exist_ok=True)
        named = sum(1 for e in entries if e["name"])
        print(f"{archive.name}: {len(entries)} files, {named} named")
        # Deduplicate identical names BEFORE writing anything: KoC2's
        # name table genuinely repeats names (e.g. on0232.adx x158,
        # oc0234.adx x156 — distinct files, same name). The Nth copy
        # gets "~N-1" appended to the stem (1st copy keeps the plain
        # name). The counter lives on the ORIGINAL name, so a 3rd+
        # copy never overwrites the 2nd (a bug in the first version
        # of this tool lost 321 files that way; found + fixed
        # 2026-11-19).
        seen = {}
        for e in entries:
            base = safe_name(e["name"] or f"file{e['id']:05d}.bin", e["id"])
            k = seen.get(base, 0)
            seen[base] = k + 1
            if k:
                stem, dot, ext = base.rpartition(".")
                e["disk_name"] = f"{stem}~{k}.{ext}" if dot else f"{base}~{k}"
            else:
                e["disk_name"] = base
        with open(outdir / "index.csv", "w", newline="") as csvfh:
            w = csv.writer(csvfh)
            w.writerow(["id", "offset", "size", "name", "disk_name"])
            for e in entries:
                w.writerow([e["id"], e["offset"], e["size"],
                            e["name"] or "", e["disk_name"]])
        if index_only:
            return entries
        for n, e in enumerate(entries):
            blob = data[e["offset"]: e["offset"] + e["size"]]
            dest = outdir / e["disk_name"]
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(blob)
            if (n + 1) % 2000 == 0:
                print(f"  ... {n + 1}/{len(entries)}")
        print(f"  extracted {len(entries)} files to {outdir}")
        return entries


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 2
    extract(Path(argv[1]), Path(argv[2]), "--index-only" in argv)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
