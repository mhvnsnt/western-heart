#!/usr/bin/env python3
"""Repair SmutBase 'BLENDER17-01' variant .blend files so stock Blender can open them.

Pipeline these files went through before reaching us:
  1. Original Blender 4.5.x scene authored/saved by the uploader.
  2. Packed with a non-standard container ("BLENDER17-01" variant):
     - 12-byte file header: b'BLENDER17-01' (bytes 7-11 mangled; the real
       pointer-size/endianness/version fields are NOT valid Blender values)
     - 5-byte marker: b'v0500' / b'v0501' (variant revision tag)
     - 32-byte block headers: code(4), sdna_index(4), ptr(8), size(4),
       unk(4), count(4), pad(4)
       (verified by walking blocks: REND -> TEST -> GLOB -> WM -> DATA ...;
       sdna_index matches vanilla Blender, e.g. REND=0, TEST=0, GLOB=171,
       so the embedded SDNA/DNA block itself is intact and standard)
  3. Whole thing zstd-compressed (magic 28 B5 2F FD) and mislabeled ".blend".

What this script does:
  a. If the input starts with the zstd magic, decompress it first
     (handles single- and multi-frame streams).
  b. Rewrites the 12-byte header to b'BLENDER-v402'.
  c. Converts every 32-byte variant block header to the standard 24-byte
     layout: code(4), size(4), ptr(8), sdna_index(4), count(4).
  d. Patches FileGlobal.minversion/minsubversion 405/85 -> 402/0 so the
     version check does not refuse the file outright.

IMPORTANT - Blender version requirement:
  These files were authored in Blender 4.5.x. Even after repair, Blender 4.0.2
  REFUSES them with "The file was saved by a newer version, open it with
  Blender 4.2 (sub 0) or later" — the DNA contains 4.2+-era structs that 4.0.2
  cannot parse, and no header patch can fix that. OPEN THE REPAIRED FILES WITH
  BLENDER >= 4.2 (tested good: 4.5.3). Trying 2.x/3.x is pointless.

Usage:
  python3 blend17_to_standard.py <in.blend> <out.blend>
  (input may be the raw .blend variant OR the zstd-compressed mislabeled file)

Verified 2026-10-22 on: Rahkasa/Chatur, Mina Ashido/Ryusan, Lily/Birodo,
Mirko/Tobi (in-repo blob) — all open in Blender 4.5.3 after repair.
"""
import struct
import sys

ZSTD_MAGIC = b"\x28\xb5\x2f\xfd"


def maybe_zstd_decompress(data: bytes) -> bytes:
    if data[:4] != ZSTD_MAGIC:
        return data
    try:
        import zstandard
    except ImportError:
        raise SystemExit(
            "input is zstd-compressed but the 'zstandard' package is not installed "
            "(pip install zstandard)")
    dctx = zstandard.ZstdDecompressor()
    out = bytearray()
    # stream_reader handles multi-frame streams and trailing data gracefully
    with dctx.stream_reader(_BytesReader(data)) as reader:
        while True:
            chunk = reader.read(8 * 1024 * 1024)
            if not chunk:
                break
            out += chunk
    print(f"  zstd decompressed: {len(data)} -> {len(out)} bytes")
    return bytes(out)


class _BytesReader:
    """Minimal file-like wrapper so stream_reader accepts bytes."""
    def __init__(self, data: bytes):
        self._data = data
        self._pos = 0

    def read(self, n=-1):
        if n is None or n < 0:
            n = len(self._data) - self._pos
        chunk = self._data[self._pos:self._pos + n]
        self._pos += len(chunk)
        return chunk

    def readable(self):
        return True

    def seekable(self):
        return False


def convert(data: bytes) -> bytes:
    if data[:7] != b"BLENDER":
        raise ValueError("not a BLENDER file (bad magic)")
    if data[12:15] != b"v05":
        raise ValueError("missing v05xx marker; not the 17-01 variant")
    out = bytearray()
    out += b"BLENDER-v402"
    off = 17  # skip 12-byte header + 5-byte v05xx marker
    nblocks = 0
    while True:
        if off + 32 > len(data):
            raise ValueError(f"truncated block header at offset {off}")
        code = data[off:off + 4]
        sdna = struct.unpack("<I", data[off + 4:off + 8])[0]
        ptr = data[off + 8:off + 16]
        size = struct.unpack("<I", data[off + 16:off + 20])[0]
        count = struct.unpack("<I", data[off + 24:off + 28])[0]
        # standard 24-byte block header: code, size, ptr, sdna_index, count
        out += code
        out += struct.pack("<I", size)
        out += ptr
        out += struct.pack("<I", sdna)
        out += struct.pack("<I", count)
        nblocks += 1
        off += 32
        if off + size > len(data):
            raise ValueError(f"truncated block data at offset {off} (need {size})")
        out += data[off:off + size]
        off += size
        if code == b"ENDB":
            break
        if nblocks > 10_000_000:
            raise ValueError("runaway block walk (>10M blocks)")
    out += data[off:]  # preserve any trailing bytes
    print(f"  converted {nblocks} blocks (32-byte -> 24-byte headers)")

    # Patch FileGlobal.minversion/minsubversion so the version gate passes.
    # FileGlobal layout: char subvstr[4] @0, short subversion @4,
    #                    short minversion @6, short minsubversion @8.
    b = bytearray(out)
    boff = 12
    while True:
        code = bytes(b[boff:boff + 4])
        size = struct.unpack("<I", b[boff + 4:boff + 8])[0]
        if code == b"GLOB":
            gstart = boff + 24
            mv = struct.unpack("<h", b[gstart + 6:gstart + 8])[0]
            msv = struct.unpack("<h", b[gstart + 8:gstart + 10])[0]
            print(f"  GLOB minversion={mv} minsubversion={msv} -> 402/0")
            struct.pack_into("<h", b, gstart + 6, 402)
            struct.pack_into("<h", b, gstart + 8, 0)
            break
        boff += 24 + size
        if code == b"ENDB":
            print("  WARNING: no GLOB block found; version patch skipped")
            break
    return bytes(b)


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("usage: blend17_to_standard.py <in.blend> <out.blend>")
    src, dst = sys.argv[1], sys.argv[2]
    raw = open(src, "rb").read()
    print(f"in: {src} ({len(raw)} bytes, header={raw[:12]!r})")
    raw = maybe_zstd_decompress(raw)
    conv = convert(raw)
    open(dst, "wb").write(conv)
    print(f"out: {dst} ({len(conv)} bytes)")
    print("done. Open the output with Blender >= 4.2 (4.5.3 tested).")


if __name__ == "__main__":
    main()
