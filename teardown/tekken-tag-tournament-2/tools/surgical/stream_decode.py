#!/usr/bin/env python3
"""Decode the 7z LZMA stream from the start, splitting members by known
uncompressed sizes, and save selected members.

The TTT2 7z is one LZMA folder (lc=3,lp=0,pb=2,dict=8MB) holding all files
concatenated in header order. We stream-decode from offset 32 and carve out
wanted members without downloading the whole 13.36GB.

Usage:
    stream_decode.py <outdir> <member-index> [<member-index> ...]
Member indices are header order (0-based). Saves each as outdir/member_<idx>.bin
plus a manifest with sha256.
"""
import hashlib
import lzma
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fetch_assets as dl  # noqa: E402
import vfile  # noqa: E402

# Member table is built from the live 7z end-header (header order), not hardcoded.


def member_table():
    vf = vfile.PartVirtualFile(dl.ASSETS[:26])
    import py7zr
    with py7zr.SevenZipFile(vf, mode="r") as z:
        files = z.header.files_info.files
    table = []
    for idx, e in enumerate(files):
        name = e["filename"]
        size = e.get("uncompressed")
        if e.get("emptystream"):
            size = None
        table.append((idx, name, size))  # idx = header order; size None = dir
    return table


def main():
    outdir = sys.argv[1]
    want = set(int(x) for x in sys.argv[2:])
    os.makedirs(outdir, exist_ok=True)

    table = member_table()
    ndata = sum(1 for _, _, s in table if s)
    print(f"[dec] {len(table)} entries ({ndata} with data) in stream order", flush=True)
    # byte offsets of wanted members in the decompressed stream
    spans = {}
    off = 0
    for idx, name, size in table:
        if size and idx in want:
            spans[idx] = (off, off + size, name.rsplit("/", 1)[-1])
        if size:
            off += size
    max_end = max(e for _, e, _ in spans.values())
    print(f"[dec] need output bytes [0, {max_end})", flush=True)

    vf = vfile.PartVirtualFile(dl.ASSETS[:26])
    decomp = lzma.LZMADecompressor(
        format=lzma.FORMAT_RAW,
        filters=[{"id": lzma.FILTER_LZMA1, "dict_size": 8 * 1024 * 1024,
                  "lc": 3, "lp": 0, "pb": 2}],
    )
    outs = {i: open(os.path.join(outdir, f"member_{i:02d}.bin"), "wb") for i in want}
    hashes = {i: hashlib.sha256() for i in want}
    produced = 0
    # read compressed stream from offset 32 in 4MB fetches
    vf.seek(32)
    try:
        while produced < max_end:
            chunk = vf.read(4 * 1024 * 1024)
            if not chunk:
                raise IOError("stream ended early")
            data = decomp.decompress(chunk)
            # route `data` bytes [produced, produced+len) to wanted spans
            start = produced
            for i, (s, e, _) in sorted(spans.items(), key=lambda kv: kv[1][0]):
                lo = max(s, start)
                hi = min(e, start + len(data))
                if hi > lo:
                    piece = data[lo - start:hi - start]
                    outs[i].write(piece)
                    hashes[i].update(piece)
            produced += len(data)
            if produced % (512 * 1024 * 1024) < len(data):
                print(f"[dec] produced {produced / 1e9:.2f}GB "
                      f"(http {vf.bytes_fetched / 1e9:.2f}GB)", flush=True)
    finally:
        for f in outs.values():
            f.close()
    manifest = []
    for i, (s, e, short) in sorted(spans.items()):
        p = os.path.join(outdir, f"member_{i:02d}.bin")
        sz = os.path.getsize(p)
        manifest.append(f"{i:02d} {short} {sz} sha256={hashes[i].hexdigest()} "
                        f"expect={e - s} {'OK' if sz == e - s else 'SHORT'}")
    open(os.path.join(outdir, "MANIFEST.txt"), "w").write("\n".join(manifest) + "\n")
    print("\n".join(manifest), flush=True)


if __name__ == "__main__":
    main()
