#!/usr/bin/env python3
"""Western Heart reference ISO9660 reader.

Reads the file listing (and, on request, the files) of a plain ISO9660
CD-ROM image. It understands two layouts:

* 2048-byte logical sectors (a plain .iso), and
* 2352-byte raw Mode-2 sectors (a .bin), where the 2048 data bytes start
  at offset 24 inside each sector.

This is a Western Heart clean implementation written for this repo. It
is reference tooling only: it is not a game, it contains no game data,
and it must never be pointed at a commercial disc image whose output
would then be committed to this public repo. Raw extracted output
belongs in a PRIVATE location only (see README.md).

Usage:
    python3 iso9660_extract.py IMAGE --list-only
    python3 iso9660_extract.py IMAGE --outdir /private/path/out
"""

import argparse
import os
import struct
import sys

SECTOR_DATA = 2048
RAW_SECTOR = 2352
RAW_DATA_OFFSET = 24
SYNC = b"\x00\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00"
PVD_SECTOR = 16


class IsoError(Exception):
    """Raised when the image is not a readable ISO9660 image."""


def _read_at(f, offset, length):
    f.seek(offset)
    data = f.read(length)
    if len(data) != length:
        raise IsoError("short read at offset %d" % offset)
    return data


def detect_layout(f):
    """Return 'iso' (2048-byte sectors) or 'raw' (2352-byte sectors)."""
    f.seek(0, os.SEEK_END)
    size = f.tell()
    for layout, sector in (("iso", SECTOR_DATA), ("raw", RAW_SECTOR)):
        offset = PVD_SECTOR * sector
        if offset + sector > size:
            continue
        raw = _read_at(f, offset, sector)
        if layout == "iso":
            candidate = raw[:SECTOR_DATA]
        else:
            if raw[:12] != SYNC or raw[15] != 2:
                continue
            candidate = raw[RAW_DATA_OFFSET:RAW_DATA_OFFSET + SECTOR_DATA]
        if candidate[1:6] == b"CD001":
            return layout
    raise IsoError("no ISO9660 primary volume descriptor at sector 16")


def logical_sector(f, layout, number):
    """Return the 2048 data bytes of logical sector `number`."""
    if layout == "iso":
        return _read_at(f, number * SECTOR_DATA, SECTOR_DATA)
    raw = _read_at(f, number * RAW_SECTOR, RAW_SECTOR)
    if raw[:12] != SYNC:
        # Tolerate a raw image whose later sectors lost the sync header
        # by falling back to the first 2048 bytes.
        return raw[:SECTOR_DATA]
    if raw[15] == 2:
        return raw[RAW_DATA_OFFSET:RAW_DATA_OFFSET + SECTOR_DATA]
    return raw[:SECTOR_DATA]


def sector_span(f, layout, extent, size):
    """Yield the logical-sector bytes covering `size` bytes at `extent`."""
    remaining = size
    sector = extent
    while remaining > 0:
        chunk = logical_sector(f, layout, sector)
        yield chunk[: min(remaining, SECTOR_DATA)]
        remaining -= len(chunk[: min(remaining, SECTOR_DATA)])
        sector += 1


class Record:
    def __init__(self, extent, size, is_dir, name):
        self.extent = extent
        self.size = size
        self.is_dir = is_dir
        self.name = name


def parse_record(buf, offset):
    """Parse one directory record at `offset`; return (Record, length)."""
    if offset >= len(buf) or buf[offset] == 0:
        return None, 0
    length = buf[offset]
    if length < 34 or offset + length > len(buf):
        return None, 0
    rec = buf[offset:offset + length]
    extent = struct.unpack_from("<I", rec, 2)[0]
    size = struct.unpack_from("<I", rec, 10)[0]
    is_dir = bool(rec[25] & 0x02)
    name_len = rec[32]
    raw_name = rec[33:33 + name_len]
    if raw_name == b"\x00":
        name = "."
    elif raw_name == b"\x01":
        name = ".."
    else:
        name = raw_name.split(b";")[0].decode("ascii", errors="replace")
    return Record(extent, size, is_dir, name), length


def read_directory(f, layout, extent, size):
    """Return the records of the directory at `extent` (skipping . / ..)."""
    blob = b"".join(sector_span(f, layout, extent, size))
    records = []
    offset = 0
    while offset < len(blob):
        if blob[offset] == 0:
            # Zero padding: skip to the next sector boundary.
            offset = ((offset // SECTOR_DATA) + 1) * SECTOR_DATA
            continue
        record, length = parse_record(blob, offset)
        if record is None or length == 0:
            break
        if record.name not in (".", ".."):
            records.append(record)
        offset += length
    return records


def safe_child(name):
    """Reject names that could escape the output directory, else return it."""
    if not name or name in (".", ".."):
        return None
    if "/" in name or "\\" in name or "\x00" in name:
        return None
    return name


def walk(f, layout, root):
    """Yield (relative_path, Record) for every entry, depth-first."""
    stack = [("", root)]
    while stack:
        prefix, directory = stack.pop()
        for record in reversed(read_directory(f, layout, directory.extent,
                                             directory.size)):
            name = safe_child(record.name)
            if name is None:
                continue
            path = os.path.join(prefix, name) if prefix else name
            yield path, record
            if record.is_dir:
                stack.append((path, record))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", help="ISO9660 image file (.iso or raw .bin)")
    parser.add_argument("--list-only", action="store_true",
                        help="print the listing and extract nothing")
    parser.add_argument("--outdir", default=None,
                        help="output directory for extraction "
                             "(PRIVATE location only, never this repo)")
    args = parser.parse_args(argv)

    if not args.list_only and not args.outdir:
        parser.error("--outdir is required unless --list-only is given")

    with open(args.image, "rb") as f:
        layout = detect_layout(f)
        pvd = logical_sector(f, layout, PVD_SECTOR)
        volume = pvd[40:72].decode("ascii", errors="replace").strip()
        print("Volume: %s" % volume)
        root, _ = parse_record(pvd, 156)
        if root is None:
            raise IsoError("primary volume descriptor has no root record")
        entries = list(walk(f, layout, root))
        print("Entries: %d" % len(entries))

        if args.list_only:
            for path, record in entries:
                suffix = "/" if record.is_dir else ""
                print("%s%s  [%dB]" % (path, suffix, record.size))
            return 0

        for path, record in entries:
            if record.is_dir:
                os.makedirs(os.path.join(args.outdir, path), exist_ok=True)
                continue
            dest = os.path.join(args.outdir, path)
            os.makedirs(os.path.dirname(dest) or args.outdir, exist_ok=True)
            with open(dest, "wb") as out:
                for chunk in sector_span(f, layout, record.extent,
                                         record.size):
                    out.write(chunk)
        print("Extraction complete -> %s" % args.outdir)
        return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except IsoError as exc:
        print("error: %s" % exc, file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError as exc:
        print("error: %s" % exc, file=sys.stderr)
        sys.exit(1)
