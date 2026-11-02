#!/usr/bin/env python3
"""Build a tiny synthetic ISO9660 image for the proof run.

The image is generated from scratch: a primary volume descriptor, a
root directory, one subdirectory, and two small text files with known
contents. It contains no game data, no commercial data, and nothing
copied from any disc. Run it only into /tmp (see run_proof.sh).
"""

import os
import struct
import sys

SECTOR = 2048


def dir_record(extent, size, is_dir, name_bytes):
    """One ISO9660 directory record (both-endian fields, minimal form)."""
    # Fixed part is 33 bytes + name, padded to an even length.
    length = 33 + len(name_bytes)
    if length % 2:
        length += 1
    rec = bytearray(length)
    rec[0] = length
    struct.pack_into("<I", rec, 2, extent)
    struct.pack_into(">I", rec, 6, extent)
    struct.pack_into("<I", rec, 10, size)
    struct.pack_into(">I", rec, 14, size)
    rec[18:25] = b"\x00" * 7  # recording date/time, all zero
    rec[25] = 0x02 if is_dir else 0x00
    rec[26] = 0
    rec[27] = 0
    struct.pack_into("<H", rec, 28, 1)
    struct.pack_into(">H", rec, 30, 1)
    rec[32] = len(name_bytes)
    rec[33:33 + len(name_bytes)] = name_bytes
    return bytes(rec)


def wrap_raw(logical):
    """Wrap each 2048-byte logical sector in a 2352-byte Mode-2 sector."""
    out = bytearray()
    for i in range(0, len(logical), SECTOR):
        chunk = logical[i:i + SECTOR]
        raw = bytearray(2352)
        raw[0:12] = b"\x00\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00"
        raw[15] = 2
        raw[24:24 + len(chunk)] = chunk
        out += raw
    return bytes(out)


def main(out_path, raw=False):
    # Sector layout: 16 = PVD, 17 = root dir, 18 = subdir, 19 = HELLO.TXT,
    # 20 = INNER.TXT. Every other sector is zero-filled.
    root_entries = b"".join([
        dir_record(17, SECTOR, True, b"\x00"),
        dir_record(17, SECTOR, True, b"\x01"),
        dir_record(18, SECTOR, True, b"DOCS"),
        dir_record(19, 13, False, b"HELLO.TXT;1"),
    ])
    sub_entries = b"".join([
        dir_record(18, SECTOR, True, b"\x00"),
        dir_record(18, SECTOR, True, b"\x01"),
        dir_record(20, 11, False, b"INNER.TXT;1"),
    ])
    root_dir = root_entries + b"\x00" * (SECTOR - len(root_entries))
    sub_dir = sub_entries + b"\x00" * (SECTOR - len(sub_entries))

    pvd = bytearray(SECTOR)
    pvd[0] = 1
    pvd[1:6] = b"CD001"
    pvd[6] = 1
    pvd[40:72] = b"WH-TEST".ljust(32)
    pvd[156:156 + len(dir_record(17, SECTOR, True, b"\x00"))] = \
        dir_record(17, SECTOR, True, b"\x00")

    hello = b"hello world!\n" + b"\x00" * (SECTOR - 13)
    inner = b"inner file\n" + b"\x00" * (SECTOR - 11)

    logical = (
        b"\x00" * (16 * SECTOR)
        + bytes(pvd) + root_dir + sub_dir + hello + inner
    )
    with open(out_path, "wb") as f:
        f.write(wrap_raw(logical) if raw else logical)
    print("wrote %s" % out_path)


if __name__ == "__main__":
    main(sys.argv[1], raw="--raw" in sys.argv[2:])
