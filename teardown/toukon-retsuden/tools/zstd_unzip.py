#!/usr/bin/env python3
"""Extract a ZIP whose entries use method 93 (Zstandard), which neither
Python's zipfile nor 7-Zip 23.01 supports. Reads each entry's raw compressed
bytes from the local header and decompresses with the `zstandard` package.
Falls back to zipfile for stored/deflate/bzip2/lzma entries.

Usage: python3 zstd_unzip.py <archive.zip> <outdir>
"""
import struct
import sys
import zipfile
from pathlib import Path

import zstandard


def extract(archive: str, outdir: str) -> None:
    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)
    zf = zipfile.ZipFile(archive)
    with open(archive, "rb") as fh:
        for info in zf.infolist():
            dest = out / info.filename
            dest.parent.mkdir(parents=True, exist_ok=True)
            if info.compress_type == 93:
                # Local file header: sig(4) ver(2) flags(2) method(2) time(2)
                # date(2) crc(4) csize(4) usize(4) fnlen(2) extralen(2)
                fh.seek(info.header_offset)
                hdr = fh.read(30)
                sig, _ver, _flags, _method, _t, _d, _crc, _cs, _us, fnlen, extralen = struct.unpack("<IHHHHHIIIHH", hdr)
                assert sig == 0x04034B50, f"bad local header sig for {info.filename}"
                data_start = info.header_offset + 30 + fnlen + extralen
                fh.seek(data_start)
                comp = fh.read(info.compress_size)
                dctx = zstandard.ZstdDecompressor()
                with open(dest, "wb") as out_fh:
                    dctx.stream_reader(__import__("io").BytesIO(comp)).read1  # noqa
                    # stream via copy_stream for low memory
                    import io
                    dctx.copy_stream(io.BytesIO(comp), out_fh)
                print(f"{info.filename}: {info.file_size} bytes (zstd)")
            else:
                with zf.open(info) as src, open(dest, "wb") as dst:
                    while True:
                        chunk = src.read(1 << 20)
                        if not chunk:
                            break
                        dst.write(chunk)
                print(f"{info.filename}: {info.file_size} bytes (method {info.compress_type})")
    print("done")


if __name__ == "__main__":
    extract(sys.argv[1], sys.argv[2])
