#!/usr/bin/env python3
"""Decompress Yuke's 'BPE ' sections (Toukon Retsuden DTPAC.PAC).

Yuke's BPE section header (16 bytes, little-endian):
  0x00 "BPE " magic
  0x04 u32 version (0x100)
  0x08 u32 compressed size (exact; data is 4-byte padded after)
  0x0C u32 decompressed size

The block payload follows the classic BPE scheme documented on psx-spx
(Bust-A-Groove / Legend of Dragoon variant): a dictionary section, then
compressed data. Dictionary entries map a code byte to a byte pair;
codes that map to themselves are literals. End condition: output reaches
the decompressed size from the header.

Usage:
  python3 bpe.py <file> [offset]     # decompress one section, print info
  python3 bpe.py --all <file> <outdir>  # decompress every BPE section found
"""
import re
import struct
import sys
from pathlib import Path


def decompress_block(data: bytes, out_len: int) -> bytes:
    """Decompress one BPE section payload (one or more GROOVE-style blocks).

    Each block: dictionary, then a 2-byte little-endian length (remaining
    compressed data bytes for this block), then the compressed data.
    Blocks repeat until the input is consumed; total output must equal
    out_len (the decompressed size from the section header).
    """
    src = 0
    out = bytearray()
    while src < len(data):
        # --- dictionary ---
        dict1 = list(range(256))
        dict2 = list(range(256))
        i = 0
        while i < 0x100:
            num = data[src]
            src += 1
            if num > 0x7F:
                i += num - 0x7F
                num = 0
                if i == 0x100:
                    break
            for _ in range(num + 1):
                a = data[src]
                src += 1
                if a != i:
                    b = data[src]
                    src += 1
                    dict1[i] = a
                    dict2[i] = b
                i += 1
                if i >= 0x100:
                    break
        # --- block length (little-endian, bytes of compressed data) ---
        blk_len = data[src] | (data[src + 1] << 8)
        src += 2
        src_end = src + blk_len
        # --- data ---
        heap = []
        while src < src_end or heap:
            if heap:
                x = heap.pop()
            else:
                x = data[src]
                src += 1
            a = dict1[x]
            if a == x:
                out.append(x)
            else:
                heap.append(dict2[x])
                heap.append(a)
    if len(out) != out_len:
        raise ValueError(f"output length {len(out)} != expected {out_len}")
    return bytes(out)


def decompress_section(section: bytes) -> bytes:
    """Decompress a full BPE section (header + payload)."""
    assert section[:4] == b"BPE ", "bad magic"
    _ver, comp_size, decomp_size = struct.unpack_from("<III", section, 4)
    payload = section[16:16 + comp_size]
    return decompress_block(payload, decomp_size)


def find_sections(data: bytes):
    return [m.start() for m in re.finditer(rb"BPE ", data)]


if __name__ == "__main__":
    if sys.argv[1] == "--all":
        data = Path(sys.argv[2]).read_bytes()
        outdir = Path(sys.argv[3])
        outdir.mkdir(parents=True, exist_ok=True)
        for n, off in enumerate(find_sections(data)):
            _ver, comp_size, decomp_size = struct.unpack_from("<III", data, off + 4)
            section = data[off:off + 16 + comp_size]
            try:
                dec = decompress_section(section)
                dest = outdir / f"bpe{n:02d}_{off:#x}.bin"
                dest.write_bytes(dec)
                magic = dec[:4].hex()
                print(f"{off:#06x}: {comp_size} -> {len(dec)} bytes, head={magic} -> {dest.name}")
            except Exception as e:
                print(f"{off:#06x}: FAILED: {e}")
    else:
        data = Path(sys.argv[1]).read_bytes()
        off = int(sys.argv[2], 0) if len(sys.argv) > 2 else data.find(b"BPE ")
        _ver, comp_size, decomp_size = struct.unpack_from("<III", data, off + 4)
        dec = decompress_section(data[off:off + 16 + comp_size])
        print(f"offset {off:#x}: {comp_size} -> {len(dec)} (expected {decomp_size})")
        print("head:", dec[:32].hex(" "))
        print("ascii:", "".join(chr(c) if 32 <= c < 127 else "." for c in dec[:64]))
