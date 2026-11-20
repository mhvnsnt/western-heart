#!/usr/bin/env python3
"""Minimal ISO9660 extractor (stdlib only) for PS2 ISOs.

Usage: iso9660_extract.py <iso> <outdir>

Reads the PVD at sector 16, walks directory records, extracts files by
extent LBA. Handles standard ISO9660 (Rock Ridge/Joliet not required for
file extraction).
"""
import os
import struct
import sys

SECTOR = 2048


def read_sector(f, lba, n=1):
    f.seek(lba * SECTOR)
    return f.read(n * SECTOR)


def parse_dir_records(data):
    """Yield (name, extent_lba, size, is_dir) for each record in a directory sector run."""
    off = 0
    while off < len(data):
        reclen = data[off]
        if reclen == 0:
            # pad to next sector boundary
            off = ((off // SECTOR) + 1) * SECTOR
            continue
        rec = data[off:off + reclen]
        if len(rec) < 33:
            break
        extent = struct.unpack("<I", rec[2:6])[0]
        size = struct.unpack("<I", rec[10:14])[0]
        flags = rec[25]
        namelen = rec[32]
        name = rec[33:33 + namelen]
        is_dir = bool(flags & 0x02)
        yield name, extent, size, is_dir
        off += reclen


def clean_name(raw):
    # raw is bytes; strip version suffix ";1", handle \x00 (root) and \x01 (parent)
    if raw == b"\x00":
        return None  # self
    if raw == b"\x01":
        return None  # parent
    s = raw.decode("ascii", "replace").split(";")[0]
    return s


def main(iso_path, outdir):
    with open(iso_path, "rb") as f:
        pvd = read_sector(f, 16)
        assert pvd[0] == 1 and pvd[1:6] == b"CD001", "not ISO9660"
        root_rec = pvd[156:156 + 34]
        root_extent = struct.unpack("<I", root_rec[2:6])[0]
        root_size = struct.unpack("<I", root_rec[10:14])[0]
        print(f"root extent LBA={root_extent} size={root_size}")

        # BFS walk
        stack = [("", root_extent, root_size)]
        nfiles = 0
        nbytes = 0
        while stack:
            rel, extent, size = stack.pop()
            data = read_sector(f, extent, (size + SECTOR - 1) // SECTOR)[:size]
            for raw, ext, sz, is_dir in parse_dir_records(data):
                name = clean_name(raw)
                if name is None:
                    continue
                child_rel = os.path.join(rel, name) if rel else name
                if is_dir:
                    stack.append((child_rel, ext, sz))
                else:
                    dest = os.path.join(outdir, child_rel)
                    os.makedirs(os.path.dirname(dest) or outdir, exist_ok=True)
                    with open(dest, "wb") as out:
                        remaining = sz
                        lba = ext
                        while remaining > 0:
                            chunk = read_sector(f, lba)
                            take = min(remaining, SECTOR)
                            out.write(chunk[:take])
                            remaining -= take
                            lba += 1
                    nfiles += 1
                    nbytes += sz
                    if nfiles % 100 == 0:
                        print(f"  {nfiles} files, {nbytes/1e9:.2f} GB", flush=True)
        print(f"done: {nfiles} files, {nbytes/1e9:.2f} GB -> {outdir}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
