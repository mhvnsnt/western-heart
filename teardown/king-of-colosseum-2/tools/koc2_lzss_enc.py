#!/usr/bin/env python3
"""koc2_lzss_enc.py — COMPRESS with Spike's LZSS variant (KoC2).

Encoder companion to koc2_lzss.py (the decoder, cracked 2026-11-19).
Format recap (all from the decoder):
  Stream = groups of 1 flag byte + 8 items, LSB-first.
    bit 1 -> literal: 1 byte.
    bit 0 -> match: 2 bytes (b1, b2).
      stored = b1 | ((b2 & 0x0F) << 8)   (1-based ring position)
      ring offset = (stored - 1) & 0xFFF
      length = (b2 >> 4) + 2             (2..17)
  Ring buffer: 4096 bytes, zero-filled, write pos starts at 0. Matches
  may overlap the write position (runs). The decoder stops after exactly
  `expected_size` output bytes, so the encoder's trailing group may be
  padded with dummy literal items that are never consumed.

Encoder: greedy longest-match with a 3-byte hash table over the last
4096 output bytes. Correctness is what matters (a literals-only stream
is always valid); matches are accepted when length >= 2. The ring is
simulated so overlap matches (distance <= 17, incl. distance-1 runs)
are validated exactly the way the decoder will reproduce them.

Verified 2026-11-19: round-trip (encode -> koc2_lzss.decompress) is
byte-exact on <see test results in WORKLOG>.

Usage:
  koc2_lzss_enc.py <input.bin> [output.bin]
  Without an output path, the compressed bytes go to stdout.

KoC2 English lane, 2026-11-19.
"""
import sys
from pathlib import Path

RING_SIZE = 4096
RING_MASK = RING_SIZE - 1
MIN_MATCH = 2
MAX_MATCH = 17


def compress(data: bytes) -> bytes:
    """Compress `data` into Spike's LZSS format."""
    n = len(data)
    # Hash table: 3-byte sequence -> list of absolute positions where
    # it occurred (most recent last). Positions older than the 4096
    # window are dropped lazily on lookup.
    table = {}
    out = bytearray()
    # Current group: flag bits + item bytes.
    flag = 0
    items = bytearray()
    n_items = 0

    def flush_group():
        nonlocal flag, items, n_items
        if n_items == 0:
            return
        # Pad the group to 8 items with dummy literals (flag bit 1).
        # The decoder stops at expected_size and never consumes them.
        while n_items < 8:
            flag |= 1 << n_items
            items.append(0)
            n_items += 1
        out.append(flag)
        out.extend(items)
        flag = 0
        items = bytearray()
        n_items = 0

    def emit_literal(b):
        nonlocal flag, n_items
        flag |= 1 << n_items
        items.append(b)
        n_items += 1
        if n_items == 8:
            flush_group()

    def emit_match(ring_off, length):
        nonlocal n_items
        stored = (ring_off + 1) & 0xFFF
        b1 = stored & 0xFF
        b2 = ((stored >> 8) & 0x0F) | ((length - 2) << 4)
        items.append(b1)
        items.append(b2)
        n_items += 1
        if n_items == 8:
            flush_group()

    def add_pos(p):
        # Index the 3-byte sequence at absolute position p.
        if p + 3 <= n:
            key = data[p:p + 3]
            lst = table.get(key)
            if lst is None:
                table[key] = [p]
            else:
                lst.append(p)

    p = 0
    while p < n:
        best_len = 0
        best_dist = 0
        if p + MIN_MATCH <= n:
            # Candidate source positions from the hash table.
            cands = table.get(data[p:p + 3]) if p + 3 <= n else None
            if cands:
                # Newest first; prune positions outside the window.
                lo = p - RING_SIZE
                for q in reversed(cands):
                    if q < lo:
                        break
                    dist = p - q
                    # Max length for this candidate (cap 17, cap at
                    # remaining input).
                    maxlen = min(MAX_MATCH, n - p)
                    if dist >= maxlen:
                        # No overlap: straight compare.
                        ln = 0
                        while ln < maxlen and data[q + ln] == data[p + ln]:
                            ln += 1
                    else:
                        # Overlap: the match repeats with period dist
                        # (the decoder copies byte-by-byte from the
                        # ring, so out[p+i] == out[p+i-dist]).
                        ln = 0
                        while ln < maxlen and data[p + ln] == data[p + ln - dist]:
                            ln += 1
                    if ln > best_len:
                        best_len = ln
                        best_dist = dist
                        if ln >= MAX_MATCH:
                            break
            # Distance-1 run check (covers runs the hash table can't
            # see yet, e.g. a run starting at p after a different byte):
            # if data[p] == data[p-1], a run of that byte may beat the
            # hash candidates.
            if p > 0 and data[p] == data[p - 1]:
                maxlen = min(MAX_MATCH, n - p)
                ln = 0
                while ln < maxlen and data[p + ln] == data[p - 1]:
                    ln += 1
                if ln > best_len:
                    best_len = ln
                    best_dist = 1
        if best_len >= MIN_MATCH:
            ring_off = (p - best_dist) & RING_MASK
            emit_match(ring_off, best_len)
            # Index every position the match covers.
            for k in range(best_len):
                add_pos(p + k)
            p += best_len
        else:
            emit_literal(data[p])
            add_pos(p)
            p += 1
    flush_group()
    return bytes(out)


def main(argv):
    if len(argv) < 2:
        print(__doc__.split("Usage:")[1].strip(), file=sys.stderr)
        return 2
    data = Path(argv[1]).read_bytes()
    out = compress(data)
    if len(argv) > 2:
        Path(argv[2]).write_bytes(out)
        print(f"{argv[1]}: {len(data)} -> {len(out)} bytes "
              f"({100.0 * len(out) / max(len(data), 1):.1f}%)")
    else:
        sys.stdout.buffer.write(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
