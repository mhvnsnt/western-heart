#!/usr/bin/env python3
"""koc2_lzss.py — decompress Spike's LZSS variant used in King of Colosseum II.

King of Colosseum II stores most of its files LZSS-compressed inside the
KC2FIRE.000 / KC2FIRE.001 archives (see kc2_extract.py). The variant was
reverse-engineered from the game's own data on 2026-11-19: a compressed
TIM2 texture whose decompressed form was already known (a neighbouring
uncompressed TIM2 of the same size) gave known plaintext, and the token
stream was solved from it.

Format (all integers little-endian):
  The stream is a sequence of groups. Each group starts with one flag
  byte, then 8 items, one per flag bit, LSB first:
    bit = 1 -> literal: 1 byte copied straight to the output.
    bit = 0 -> match: 2 bytes (b1, b2).
  Match: offset = (b1 | ((b2 & 0x0F) << 8)) - 1
         length = (b2 >> 4) + 2            (so lengths 2..17)
  The offset is an ABSOLUTE position in a 4096-byte ring buffer (the
  stored value is offset+1, i.e. 1-based). The buffer starts zero-filled
  and the write position starts at 0. Matches may overlap the write
  position (that is how runs are encoded: offset == pos-1 repeats the
  last byte).
  The decoder stops after exactly `expected_size` output bytes. The
  stored stream is usually padded with zero bytes up to a 2048-byte
  boundary, so trailing input past the end of the stream is ignored.
  NOTE (found 2026-11-19): about 6% of files end with a run of (0,0)
  matches — all-zero token bytes — and the stored blob is cut short by
  a few bytes mid-run (the archive's stored size truncates the final
  zero bytes). The decoder therefore treats the input as zero-extended
  past its end: reading past the end of the blob yields 0x00, which
  reconstitutes the truncated (0,0) matches and lands exactly on
  expected_size. Verified on all 1,492 files that failed without it.

Verified 2026-11-19: files 15972/15973/15975 of KC2FIRE.001 decode to
exactly their catalogued sizes, start with the TIM2 magic, and their
TIM2 total_size fields are consistent with the decoded length; 15972
and 15973 reproduce the known TIM2 header byte-for-byte.

Usage:
  koc2_lzss.py <compressed.bin> <expected_size> [output.bin]
  Without an output path, the decompressed bytes go to stdout.
"""

import struct
import sys
from pathlib import Path

RING_SIZE = 4096
RING_MASK = RING_SIZE - 1


def decompress(src: bytes, expected_size: int) -> bytes:
    """Decompress one blob. Returns exactly expected_size bytes.

    The input is treated as zero-extended past its end (see module
    docstring): some stored blobs are truncated a few bytes into a
    trailing run of (0,0) matches, and the missing bytes are zeros.
    """
    # Zero-extend: enough to cover any truncated trailing (0,0) run
    # (observed shortfalls are <= 76 output bytes; 4096 is ample).
    src = src + b"\x00" * 4096
    buf = bytearray(RING_SIZE)
    pos = 0
    out = bytearray()
    i = 0
    n = len(src)
    append = out.append
    while i < n and len(out) < expected_size:
        flag = src[i]
        i += 1
        for bit in range(8):
            if len(out) >= expected_size or i >= n:
                break
            if (flag >> bit) & 1:
                c = src[i]
                i += 1
                append(c)
                buf[pos] = c
                pos = (pos + 1) & RING_MASK
            else:
                if i + 1 >= n:
                    break
                b1, b2 = src[i], src[i + 1]
                i += 2
                # Stored offset is 1-based; mask so a stored 0 (offset -1)
                # becomes ring position 4095 instead of a negative index.
                off = ((b1 | ((b2 & 0x0F) << 8)) - 1) & RING_MASK
                ln = (b2 >> 4) + 2
                ln = min(ln, expected_size - len(out))
                # Fast path: source fully behind the write position and
                # not wrapping -- copy in bulk.
                if off + ln <= pos and off + ln <= RING_SIZE and pos + ln <= RING_SIZE:
                    chunk = bytes(buf[off:off + ln])
                    out += chunk
                    buf[pos:pos + ln] = chunk
                    pos = (pos + ln) & RING_MASK
                elif off == (pos - 1) & RING_MASK:
                    # Run: repeat the last byte.
                    c = buf[off]
                    out += bytes([c]) * ln
                    for _ in range(ln):
                        buf[pos] = c
                        pos = (pos + 1) & RING_MASK
                else:
                    for _ in range(ln):
                        c = buf[off & RING_MASK]
                        append(c)
                        buf[pos] = c
                        pos = (pos + 1) & RING_MASK
                        off = (off + 1) & RING_MASK
    if len(out) != expected_size:
        raise ValueError(
            f"decompressed {len(out)} bytes, expected {expected_size}")
    return bytes(out)


def main(argv):
    if len(argv) < 3:
        print(__doc__.split("Usage:")[1].strip(), file=sys.stderr)
        return 2
    src = Path(argv[1]).read_bytes()
    expected = int(argv[2])
    out = decompress(src, expected)
    if len(argv) > 3:
        Path(argv[3]).write_bytes(out)
    else:
        sys.stdout.buffer.write(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
