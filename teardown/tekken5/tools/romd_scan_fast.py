#!/usr/bin/env python3
"""Fast LUT-table hunter for Tekken 5 (PS2) TK5DATA2.BIN (romD archive).

Why this exists: romd_extract.py's --scan walks the file 4 bytes at a
time in pure Python (61M positions on a 244 MB file) — far too slow.
This tool does the same structural hunt vectorised with numpy
(seconds) and tries THREE candidate entry layouts, not two:

  generic 40-byte entries (10 x u32, FileTableGet.py LUT.read):
      sector, size, crc[5], unk0, id, unk1
  ps2     8-byte entries (2 x u32, FileTableGetPS2.py):
      sector, size            (checksums live in a separate array)
  2x6    24-byte entries (6 x u32, FileTableGet2x6.py LUT.read):
      sector, size, crc, unk0, id, unk1

A candidate is STRUCTURAL only: a run of consecutive entries with
sane sizes, in-bounds offsets, strictly ascending offsets. Candidates
are clustered (one report per table) and ranked by run length; for
generic/2x6 the id==index match count is printed as an extra signal
(FileTableGet names outputs %04i_%04x = index_id). Confirm by
extracting a known file (romd_extract.py --extract) and checking its
content before trusting any table.

Usage:
  python3 romd_scan_fast.py TK5DATA2.BIN [--count 498] [--min-run 8]
"""
import argparse
import sys

import numpy as np

SECTOR = 0x800
MAGIC = b"romD"
BDPK = b"BDPK"

FORMATS = {
    "generic": {"stride_words": 10, "id_w": 8},
    "ps2": {"stride_words": 2, "id_w": None},
    "2x6": {"stride_words": 6, "id_w": 4},
}

FILTER_ENTRIES = 4  # vectorised pre-filter: first N entries must be plausible
CHUNK = 4_000_000  # positions per numpy chunk


def check_run(words, pos, stride, count, filesize, id_w):
    """Full run check at word position `pos`. Returns (good, id_matches)."""
    prev = -1
    good = 0
    id_matches = 0
    for i in range(count):
        p = pos + i * stride
        if p + 1 >= len(words):
            break
        sector = int(words[p])
        size = int(words[p + 1])
        if size == 0xFFFFFFFF or size <= 0 or size > filesize:
            break
        off = sector * SECTOR
        if off < 0 or off + size > filesize:
            break
        if off <= prev:
            break
        prev = off
        good += 1
        if id_w is not None and p + id_w < len(words) and int(words[p + id_w]) == i:
            id_matches += 1
    return good, id_matches


def hunt(words, filesize, fmt, count, min_run=8):
    """Vectorised hunt for one entry format. Returns clustered
    [(byte_offset, good, id_matches)] best-first."""
    cfg = FORMATS[fmt]
    s = cfg["stride_words"]
    id_w = cfg["id_w"]
    n_words = len(words)
    survivors = []
    # Vectorised pre-filter over 4-entry windows, in chunks.
    for base in range(0, n_words - 1, CHUNK):
        p = np.arange(base, min(base + CHUNK, n_words - 1), dtype=np.int64)
        ok = np.ones(len(p), dtype=bool)
        prev_sec = None
        for j in range(FILTER_ENTRIES):
            idx = p + j * s
            valid = idx + 1 < n_words
            sec = np.where(valid, words[np.minimum(idx, n_words - 2)].astype(np.uint64), 0)
            siz = np.where(valid, words[np.minimum(idx + 1, n_words - 1)].astype(np.uint64), 0)
            ok &= valid
            ok &= (siz > 0) & (siz != 0xFFFFFFFF) & (siz <= filesize) & \
                (sec * SECTOR + siz <= filesize)
            if prev_sec is not None:
                ok &= sec > prev_sec
            prev_sec = sec
        survivors.extend(p[ok].tolist())
    results = []
    for pos in survivors:
        good, idm = check_run(words, int(pos), s, count, filesize, id_w)
        if good >= min_run:
            results.append((int(pos) * 4, good, idm))
    # Cluster: one report per table (candidates within one table-length
    # of a better candidate are the same table shifted by entries).
    results.sort(key=lambda c: (-c[1], c[0]))
    span = count * s * 4
    kept = []
    for cand in results:
        if all(abs(cand[0] - k[0]) > span for k in kept):
            kept.append(cand)
        if len(kept) >= 10:
            break
    return kept


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("archive")
    ap.add_argument("--count", type=int, default=498)
    ap.add_argument("--min-run", type=int, default=8)
    args = ap.parse_args()

    with open(args.archive, "rb") as f:
        buf = f.read()
    print(f"archive: {args.archive} ({len(buf)} bytes)")
    if buf[:4] != MAGIC:
        print(f"FAIL: magic at 0 is {buf[:4]!r}, expected {MAGIC!r}")
        return 1
    print("magic: romD OK at offset 0")
    print(f"BDPK markers: {buf.count(BDPK)}")
    words = np.frombuffer(buf[:len(buf) // 4 * 4], dtype="<u4")
    for fmt in ("generic", "ps2", "2x6"):
        cands = hunt(words, len(buf), fmt, args.count, args.min_run)
        print(f"{fmt}: {len(cands)} table cluster(s)")
        for off, good, idm in cands[:5]:
            extra = f", id==index {idm}/{good}" if FORMATS[fmt]["id_w"] is not None else ""
            print(f"  table at {hex(off)}: {good}/{args.count} plausible entries{extra}")
    print("NOTE: candidates are structural only. Confirm by extracting a "
          "known file before trusting any table.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
