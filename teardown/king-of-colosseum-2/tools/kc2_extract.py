#!/usr/bin/env python3
"""Extract Spike's KC2 container archives (King of Colosseum II).

Format (reverse-engineered 2026-11-19 from KC2FIRE.000/.001/.MVS and
MODULES/MODULES.BIN — validated: offset chains are perfect on all four
files, sum(stored)+table == file size modulo trailing padding):

  Header (8 bytes): u32 0x800 (block size?), u32 file_count
  Entry table: file_count x 16-byte entries, little-endian:
      u32 offset            (relative to the data region start)
      u32 stored_size       (bytes as stored; 32-byte aligned)
      u32 decompressed_size (bytes after decompression)
      u32 flags             bit 0 = valid; bit 16 = LZSS-compressed
                            (.000/.001 use 0x00010001; .MVS/MODULES.BIN
                            use 0x00000001 = stored raw)
  Zero padding from the end of the table up to the next 2048-byte
  boundary; the data region starts there and files are packed
  contiguously. (Verified: data_start + sum(stored_size) == file size
  exactly, on all four archives.)

Files are extracted with numeric names (fileNNNN) — the container carries
no filenames. Compressed files are decompressed in place with
koc2_lzss.py (Spike LZSS, reverse-engineered 2026-11-19); raw files are
written as-is. The stored_size field is padded up to a 2048-byte
boundary with zero bytes; the decompressor stops at decomp_size.

Usage:
  kc2_extract.py <archive> <outdir> [--index-only] [--keep-compressed]
  --index-only writes only index.csv (offset, stored, decomp, flags).
  --keep-compressed writes the raw stored blobs instead of decompressing.

Lane E (KoC2), 2026-11-19.
"""
import csv
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from koc2_lzss import decompress  # noqa: E402


def parse_index(data: bytes):
    block, count = struct.unpack_from("<II", data, 0)
    assert block == 0x800, f"unexpected block size 0x{block:x}"
    table_end = 8 + count * 16
    base = (table_end + 2047) & ~2047  # data region: next 2048 boundary
    entries = []
    for i in range(count):
        off, size, decomp, flags = struct.unpack_from("<IIII", data, 8 + i * 16)
        entries.append({
            "id": i, "offset": off, "stored_size": size,
            "decomp_size": decomp, "flags": flags,
            "compressed": bool(flags & 0x10000),
            "abs_offset": base + off,
        })
    return base, entries


def extract(archive: Path, outdir: Path, index_only: bool = False,
            keep_compressed: bool = False):
    data = archive.read_bytes()
    base, entries = parse_index(data)
    outdir.mkdir(parents=True, exist_ok=True)
    with open(outdir / "index.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["id", "offset", "stored_size", "decomp_size",
                    "flags", "compressed", "abs_offset"])
        for e in entries:
            w.writerow([e["id"], e["offset"], e["stored_size"],
                        e["decomp_size"], f"0x{e['flags']:08x}",
                        int(e["compressed"]), e["abs_offset"]])
    n_comp = sum(1 for e in entries if e["compressed"])
    print(f"{archive.name}: {len(entries)} files, {n_comp} compressed, "
          f"table ends at 0x{base:x}")
    if index_only:
        return entries
    failed = []
    for n, e in enumerate(entries):
        blob = data[e["abs_offset"]: e["abs_offset"] + e["stored_size"]]
        if e["compressed"] and not keep_compressed:
            try:
                blob = decompress(blob, e["decomp_size"])
            except ValueError as exc:
                failed.append((e["id"], str(exc)))
                continue
        else:
            blob = blob[:e["decomp_size"]]
        (outdir / f"file{e['id']:05d}.bin").write_bytes(blob)
        if (n + 1) % 2000 == 0:
            print(f"  ... {n + 1}/{len(entries)}")
    print(f"  extracted {len(entries) - len(failed)} files to {outdir}")
    if failed:
        print(f"  FAILED to decompress {len(failed)} files:")
        for fid, why in failed[:20]:
            print(f"    file{fid:05d}: {why}")
    return entries


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 2
    extract(Path(argv[1]), Path(argv[2]), "--index-only" in argv,
            "--keep-compressed" in argv)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
