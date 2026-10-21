#!/usr/bin/env python3
"""EA RefPack / QFS decompression for Def Jam: Fight for NY (EAGL) files.

Every Def Jam FFNY game file sampled (CAW part `.o` objects and `.ssh`
textures in mhvnsnt/wrestling-game, teardown/def-jam-fight-for-ny/models/)
is wrapped in EA RefPack compression: signature ``10 FB`` followed by a
3-byte big-endian decompressed size (header byte 0 flags: bit 7 = 4-byte
size fields, bit 0 = compressed-size field present; neither flag is set
in the FFNY samples).

Decompression algorithm follows the published QFS/RefPack spec as
implemented in DBPFSharp (MIT, adapted from the zlib QFS code):
https://github.com/0xC0000054/DBPFSharp -- QfsCompression.Decompress,
and the reference description at http://wiki.niotso.org/RefPack.

Verified 2026-10-20 (J4 Phase R): decompressing
``V2CP_110_0001_A.o`` yields exactly the header-declared 38,144 bytes
beginning with a standard ELF32 header; decompressing
``V2CP_111_0001_A01_01.ssh`` yields exactly 67,024 bytes beginning with
``SHPS``. See teardown/def-jam-fight-for-ny/EAGL-FORMAT-SPEC.md.
"""

from __future__ import annotations


class RefPackError(ValueError):
    pass


def refpack_decompress(data: bytes) -> bytes:
    """Decompress one RefPack stream. Raises RefPackError on bad input."""
    if len(data) < 5:
        raise RefPackError("too short for a RefPack header")
    if (data[0] & ~(128 | 64 | 1)) != 0x10 or data[1] != 0xFB:
        raise RefPackError("missing 10 FB RefPack signature")
    large_size_fields = bool(data[0] & 128)
    compressed_size_present = bool(data[0] & 1)
    idx = 2
    if compressed_size_present:
        idx += 4 if large_size_fields else 3
    if large_size_fields:
        out_len = int.from_bytes(data[idx:idx + 4], "big")
        idx += 4
    else:
        out_len = int.from_bytes(data[idx:idx + 3], "big")
        idx += 3

    out = bytearray()
    n = len(data)
    while idx < n and data[idx] < 0xFC:
        b1 = data[idx]
        idx += 1
        if b1 >= 0xE0:  # literal run
            plain = ((b1 & 0x1F) << 2) + 4
            copy_count = 0
            copy_offset = 0
        elif b1 >= 0xC0:  # 4-byte pointer op
            b2, b3, b4 = data[idx], data[idx + 1], data[idx + 2]
            idx += 3
            plain = b1 & 3
            copy_count = ((b1 & 0x0C) << 6) + b4 + 5
            copy_offset = (((b1 & 0x10) << 12) + (b2 << 8)) + b3 + 1
        elif b1 >= 0x80:  # 3-byte pointer op
            b2, b3 = data[idx], data[idx + 1]
            idx += 2
            plain = (b2 & 0xC0) >> 6
            copy_count = (b1 & 0x3F) + 4
            copy_offset = ((b2 & 0x3F) << 8) + b3 + 1
        else:  # 2-byte pointer op
            b2 = data[idx]
            idx += 1
            plain = b1 & 3
            copy_count = ((b1 & 0x1C) >> 2) + 3
            copy_offset = ((b1 & 0x60) << 3) + b2 + 1
        out += data[idx:idx + plain]
        idx += plain
        if copy_count:
            src = len(out) - copy_offset
            if src < 0:
                raise RefPackError("back-reference before start of output")
            for _ in range(copy_count):
                out.append(out[src])
                src += 1
    if idx < n and len(out) < out_len:  # stop code 0xFC-0xFF + trailing literals
        plain = data[idx] & 3
        idx += 1
        out += data[idx:idx + plain]
        idx += plain
    if len(out) != out_len:
        raise RefPackError(
            f"decompressed {len(out)} bytes, header declares {out_len}")
    return bytes(out)


def find_refpack_offset(data: bytes) -> int:
    """Offset of the first RefPack record, or -1.

    Most FFNY records start at 0; some `.o` variants (e.g. the `_C`
    files) carry an 8-byte prefix before the ``10 FB`` record.
    """
    for off in range(0, min(len(data) - 5, 4096)):
        if data[off] & ~(128 | 64 | 1) == 0x10 and data[off + 1] == 0xFB:
            declared = int.from_bytes(data[off + 2:off + 5], "big")
            if 0 < declared <= 64 * 1024 * 1024:
                return off
    return -1


if __name__ == "__main__":
    import sys

    for path in sys.argv[1:]:
        raw = open(path, "rb").read()
        off = find_refpack_offset(raw)
        if off < 0:
            print(f"{path}: no RefPack record found")
            continue
        out = refpack_decompress(raw[off:])
        print(f"{path}: offset={off} {len(raw)} -> {len(out)} bytes, "
              f"head={out[:8].hex(' ')}")
