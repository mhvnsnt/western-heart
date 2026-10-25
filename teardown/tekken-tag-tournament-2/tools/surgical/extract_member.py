#!/usr/bin/env python3
"""Surgical 7z member extraction over the HTTP virtual file.

Usage:
    ./venv/bin/python extract_member.py <7z-member-path> <out-path>
Writes the decompressed member to out-path. Prints bytes fetched.
"""
import io
import sys

sys.path.insert(0, '.')
import fetch_assets as dl
import vfile
import py7zr


class MemWriterFactory(py7zr.WriterFactory):
    def __init__(self):
        self.products = {}

    def create(self, path):
        buf = io.BytesIO()
        self.products[path] = buf
        return buf


def main():
    target = sys.argv[1]
    out = sys.argv[2]
    vf = vfile.PartVirtualFile(dl.ASSETS[:26])
    with py7zr.SevenZipFile(vf, mode='r') as z:
        wf = MemWriterFactory()
        z.extract(targets=[target], factory=wf)
    data = wf.products[target].getvalue()
    with open(out, 'wb') as f:
        f.write(data)
    print(f"extracted {len(data)} bytes -> {out}; http fetched {vf.bytes_fetched}")


if __name__ == '__main__':
    main()
