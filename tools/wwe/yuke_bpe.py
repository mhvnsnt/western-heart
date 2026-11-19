#!/usr/bin/env python3
"""Yukes BPE decompression (pure Python).

BPE ("byte pair encoding") is the oldest compression the Yukes WWE games
use. This module is an original Python implementation of the decompression
algorithm as publicly documented by Luigi Auriemma's unrrbpe reversal
(asmodean.reverse.net) and the xhp-creations/YukesBPE project, which both
describe the same byte-pair table + stack-expansion scheme. No code was
copied from either project; the algorithm was re-implemented from the
format description.

File layout (16-byte header, then the compressed stream):
    0x00  "BPE " magic
    0x04  u32 LE: ??? (usually 0)
    0x08  u32 LE: compressed size (bytes after the header)
    0x0C  u32 LE: uncompressed size
    0x10  compressed stream

Stream layout: a sequence of blocks. Each block starts with a 256-entry
pair table, then a u16 LE payload length, then that many payload bytes.
The table is run-length coded: a control byte c <= 127 means the next
c+1 entries are explicit pairs (two bytes each, unless the pair is an
identity pair, which stores one byte); a control byte c > 127 means the
next c-127 entries are identity pairs, followed by one explicit pair.
Payload bytes expand through the table with a push-down stack: a byte
whose pair is an identity pair is output as-is; otherwise the pair's two
bytes are pushed and expanded in order.
"""

import struct

MAGIC = b"BPE "
HEADER_LEN = 0x10
_TABLE_SIZE = 256
_STACK_SIZE = 512 + 4096


def parse_header(blob):
    """Return (compressed_size, uncompressed_size) from a BPE blob header."""
    if len(blob) < HEADER_LEN or blob[0:4] != MAGIC:
        raise ValueError("not a BPE blob (bad magic)")
    comp_size = struct.unpack_from("<I", blob, 8)[0]
    out_size = struct.unpack_from("<I", blob, 12)[0]
    return comp_size, out_size


def decompress_stream(comp, out_size, fill=True):
    """Decompress a raw BPE stream (header already stripped).

    comp: the compressed bytes (zsize bytes from after the header).
    out_size: expected uncompressed size.
    fill: zero-pad the output up to out_size (matches the reference
    behaviour: short streams are padded, never truncated).
    Returns bytes of length out_size (when fill=True) or the bytes
    actually produced.
    """
    n = len(comp)
    pos = 0

    # Pair table: pairs[i] = (first, second); identity pairs have first == i.
    first = bytearray(_TABLE_SIZE)
    second = bytearray(_TABLE_SIZE)
    # Expansion stack (push-down, LIFO).
    stack = bytearray(_STACK_SIZE - 512)

    out = bytearray()

    def getc():
        nonlocal pos
        if pos >= n:
            return -1
        b = comp[pos]
        pos += 1
        return b

    while True:
        # --- read the 256-entry pair table ---
        i = 0
        while i < _TABLE_SIZE:
            c = getc()
            if c < 0:
                break
            if c > 127:
                c -= 127
                while c > 0 and i < _TABLE_SIZE:
                    first[i] = i
                    c -= 1
                    i += 1
            c += 1
            while c > 0 and i < _TABLE_SIZE:
                b = getc()
                if b < 0:
                    break
                first[i] = b
                if i != b:
                    b2 = getc()
                    if b2 < 0:
                        break
                    second[i] = b2
                c -= 1
                i += 1
        # --- read this block's payload length (u16 LE) ---
        lo = getc()
        if lo < 0:
            break
        hi = getc()
        if hi < 0:
            break
        size = lo | (hi << 8)
        # --- expand the payload ---
        count = 0
        while size or count:
            if count:
                count -= 1
                b = stack[count]
            else:
                b = getc()
                if b < 0:
                    break
                size -= 1
            c = first[b]
            if b == c:
                out.append(b)
            else:
                if count + 2 > len(stack):
                    raise ValueError("BPE expansion stack overflow")
                stack[count] = second[b]
                stack[count + 1] = c
                count += 2
        if pos >= n:
            break

    if fill and len(out) < out_size:
        out.extend(b"\x00" * (out_size - len(out)))
    return bytes(out)


def decompress(blob):
    """Decompress a full BPE blob (with its 16-byte header)."""
    comp_size, out_size = parse_header(blob)
    stream = blob[HEADER_LEN:HEADER_LEN + comp_size]
    return decompress_stream(stream, out_size)


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        print(f"usage: {sys.argv[0]} <in.bpe> <out.bin>", file=sys.stderr)
        sys.exit(1)
    with open(sys.argv[1], "rb") as f:
        blob = f.read()
    out = decompress(blob)
    with open(sys.argv[2], "wb") as f:
        f.write(out)
    print(f"wrote {len(out)} bytes to {sys.argv[2]}")
