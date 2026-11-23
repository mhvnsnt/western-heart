#!/usr/bin/env python3
"""akitext_py.py — AkiText archive parser + builder (index-preserving).

AkiText format (verified against VPW2 clean ROM + Beta 3 ROM):
  [N x u16be offsets][string data]
  - offsets[0] is normally 2*N (the string area starts right after the
    table), but Beta 3's builder points EMPTY strings at the file's final
    NUL byte instead, so offsets[0] can be EOF. Do NOT derive N from
    offsets[0] alone (akitext's rule — it mis-parses Beta 3 files,
    reporting thousands of bogus strings). Try offsets[0]//2 first and
    validate (all non-zero entries must be in range); fall back to the
    minimum sane offset (the first non-empty string is packed first,
    right after the table).
  - offset 0 = unused slot. Offsets pointing INSIDE the table (< 2N) or
    out of range are degenerate/garbage (clean 0068 has ~40 entries with
    values like 0x0101/0x0200 in slots the game never looks up — likely
    a second data structure sharing the table area, or leftover bytes).
    They parse as None (unused); the game never dereferences them.
  - A non-zero offset pointing at a NUL byte = an EMPTY string (b'').
    Zero entries and empty strings are different and both are preserved
    in place — the game looks strings up by table index.
  - Strings are NUL-terminated Shift_JIS (or ASCII) byte strings; they
    may contain embedded newlines and @B/@D control codes.

parse(blob) -> (strings, degenerate)
  strings: list of bytes|None (None = unused slot)
  degenerate: list of indices whose offsets were < 2N or out of range
build(strings) -> bytes (offsets recomputed, zero slots kept zero)

Round-trip: build(parse(blob)[0]) == blob for clean files, except
clean 006C drops one trailing pad NUL (no offset points at it — harmless).
Beta 3 files rebuild LARGER (their builder deduplicates identical strings;
this builder does not — output is still valid, just bigger).
"""
import struct


def _entries_in_range(blob, count):
    """True if every non-zero entry in the first `count` is < len(blob)."""
    if 2 * count > len(blob):
        return False
    for i in range(count):
        e = struct.unpack('>H', blob[2 * i:2 * i + 2])[0]
        if e != 0 and e >= len(blob):
            return False
    return True


def parse(blob):
    first = struct.unpack('>H', blob[:2])[0]
    count = None
    if first % 2 == 0 and 2 <= first <= len(blob):
        if _entries_in_range(blob, first // 2):
            count = first // 2
    if count is None:
        # Beta 3 files: offsets[0] points at EOF (empty string 0).
        # Derive N from the minimum sane offset.
        n = 0
        min_off = None
        while True:
            if 2 * n + 2 > len(blob):
                raise ValueError('no string area found (ran off end)')
            v = struct.unpack('>H', blob[2 * n:2 * n + 2])[0]
            if v >= 2 and (min_off is None or v < min_off):
                min_off = v
            n += 1
            if min_off is not None and 2 * n >= min_off:
                break
        if min_off % 2 != 0 or not _entries_in_range(blob, min_off // 2):
            raise ValueError(f'cannot determine table size (min_off={min_off})')
        count = min_off // 2
    table_end = 2 * count
    offsets = struct.unpack(f'>{count}H', blob[:table_end])
    strings = []
    degenerate = []
    for i, off in enumerate(offsets):
        if off == 0 or off < table_end or off >= len(blob):
            strings.append(None)
            if off != 0:
                degenerate.append(i)
            continue
        end = blob.index(b'\x00', off)
        strings.append(blob[off:end])
    return strings, degenerate


def build(strings, dedup=False):
    """Rebuild an AkiText blob from a parsed string list.

    dedup=False (default): pack every string separately — byte-identical
    round-trip for clean files (which don't dedup).
    dedup=True: share identical strings AND suffixes (what Beta 3's
    builder does — e.g. "Tenzan" points inside "Hiroyoshi Tenzan").
    Smaller output; use for the patched ROM build, where total data
    size is capped by the fixed file-table address.
    """
    count = len(strings)
    table_len = 2 * count
    offsets = []
    data = bytearray()
    # suffix_map: every suffix of every packed string -> its offset.
    # (Includes exact matches: a string is its own suffix.)
    suffix_map = {}
    for s in strings:
        if s is None:
            offsets.append(0)
        elif dedup and s in suffix_map:
            offsets.append(suffix_map[s])
        else:
            off = table_len + len(data)
            offsets.append(off)
            if dedup:
                # register all suffixes of this string (incl. itself)
                for k in range(len(s) + 1):
                    suffix_map.setdefault(s[k:], off + k)
            data += s + b'\x00'
    out = bytearray()
    for off in offsets:
        out += struct.pack('>H', off)
    out += data
    return bytes(out)
