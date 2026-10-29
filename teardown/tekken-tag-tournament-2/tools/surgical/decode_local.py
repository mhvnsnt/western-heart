#!/usr/bin/env python3
"""Decode TTT2 7z members from LOCALLY STAGED stream-prefix segments.

Segments are produced by seg_dl.py (each seg_XX.bin holds a contiguous
absolute range of the concatenated 7z, in order). This script concatenates
them, LZMA-decodes from archive offset 32, and writes wanted members —
no network needed, re-runnable.

Usage:
    decode_local.py <segdir> <outdir> <member-idx> [<member-idx> ...]
Member indices are 7z header order (see tools/surgical/README.md).
"""
import hashlib
import lzma
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from stream_decode import member_table  # noqa: E402


class SegReader:
    """Sequential reader over seg_XX.bin files in order."""

    def __init__(self, segdir, start):
        self.segs = sorted(
            os.path.join(segdir, f) for f in os.listdir(segdir)
            if f.startswith("seg_") and f.endswith(".bin"))
        assert self.segs, "no segments"
        self.fh = [open(s, "rb") for s in self.segs]
        self.idx = 0
        self.pos = 0
        # seek to absolute `start`
        need = start
        for i, fh in enumerate(self.fh):
            sz = os.path.getsize(self.segs[i])
            if need < sz:
                fh.seek(need)
                self.idx = i
                break
            need -= sz
        self.pos = start

    def read(self, n):
        out = bytearray()
        while n > 0 and self.idx < len(self.fh):
            chunk = self.fh[self.idx].read(n)
            if not chunk:
                self.fh[self.idx].close()
                self.idx += 1
                continue
            out += chunk
            n -= len(chunk)
            self.pos += len(chunk)
        return bytes(out)

    def close(self):
        for fh in self.fh:
            try:
                fh.close()
            except Exception:
                pass


def main():
    segdir, outdir = sys.argv[1], sys.argv[2]
    want = set(int(x) for x in sys.argv[3:])
    os.makedirs(outdir, exist_ok=True)

    table = member_table()
    spans = {}
    off = 0
    for idx, name, size in table:
        if size and idx in want:
            spans[idx] = (off, off + size, name.rsplit("/", 1)[-1])
        if size:
            off += size
    max_end = max(e for _, e, _ in spans.values())
    print(f"[local] need output bytes [0, {max_end})", flush=True)

    rdr = SegReader(segdir, 32)
    decomp = lzma.LZMADecompressor(
        format=lzma.FORMAT_RAW,
        filters=[{"id": lzma.FILTER_LZMA1, "dict_size": 8 * 1024 * 1024,
                  "lc": 3, "lp": 0, "pb": 2}],
    )
    outs = {i: open(os.path.join(outdir, f"member_{i:02d}.bin"), "wb") for i in want}
    hashes = {i: hashlib.sha256() for i in want}
    produced = 0
    try:
        while produced < max_end:
            chunk = rdr.read(4 * 1024 * 1024)
            if not chunk:
                raise IOError("segments ended before target decoded")
            data = decomp.decompress(chunk)
            start = produced
            for i, (s, e, _) in sorted(spans.items(), key=lambda kv: kv[1][0]):
                lo = max(s, start)
                hi = min(e, start + len(data))
                if hi > lo:
                    piece = data[lo - start:hi - start]
                    outs[i].write(piece)
                    hashes[i].update(piece)
            produced += len(data)
    finally:
        for f in outs.values():
            f.close()
        rdr.close()
    for i, (s, e, short) in sorted(spans.items()):
        p = os.path.join(outdir, f"member_{i:02d}.bin")
        sz = os.path.getsize(p)
        print(f"{i:02d} {short} {sz} sha256={hashes[i].hexdigest()} "
              f"expect={e - s} {'OK' if sz == e - s else 'SHORT'}", flush=True)


if __name__ == "__main__":
    main()
