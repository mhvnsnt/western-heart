#!/usr/bin/env python3
"""BPE COMPRESSOR for Yuke's 'BPE ' sections (Toukon Retsuden DTPAC.PAC).

Companion to bpe.py (the decoder). Implements classic Gage byte-pair
encoding producing GROOVE-style multi-block sections the game's decoder
can read:

  Section header (16 bytes, little-endian):
    0x00 "BPE " magic
    0x04 u32 version (0x100)
    0x08 u32 compressed size (payload bytes, exact; 4-byte padded after)
    0x0C u32 decompressed size

  Payload: one or more blocks. Each block:
    - dictionary (run-length encoded, see emit_dict)
    - u16 little-endian compressed data length
    - compressed data bytes

Decoder constraints honored here (from bpe.py / psx-spx):
  - A pair code c mapping to (a, b) requires a != c (else the decoder
    treats c as a literal). b != c follows automatically because c is
    unused in the current data.
  - Pair nesting depth capped at MAX_DEPTH (10) to stay inside the
    envelope the original encoder used (max observed depth in the
    original JP GAME_MES sections is 10) and the game's heap budget.
  - Block input chunks capped at MAX_BLOCK_IN (8192 bytes); the
    original's largest block decompressed to 8500 bytes.
  - A new block starts when no unused code byte remains for a new pair,
    or the compressed block data would exceed the u16 length field.

Usage:
  python3 bpe_compress.py <in.bin> <out.bpe>   # compress one file
  python3 bpe_compress.py --roundtrip <dir>    # compress every .bin in dir,
                                               # decompress with bpe.py,
                                               # verify byte-exact
"""
import struct
import sys
from collections import Counter
from pathlib import Path

MAX_DEPTH = 10
MAX_BLOCK_IN = 8192


def emit_dict(pairs):
    """Encode the pair dictionary in the GROOVE run-length format.

    pairs: dict code -> (a, b). Codes not in pairs are literals.
    Decoder token rules (see bpe.py decompress_block):
      - byte n <= 0x7F: next n+1 codes each get an 'a' byte (plus a 'b'
        byte when a != code).
      - byte 0x80+k (k=1..128): skip k codes, then ONE entry is read
        for the next code -- UNLESS the skip lands exactly on 256,
        in which case the dictionary ends.

    Groups contain ONLY pair codes; literal runs are skipped. This is
    the version proven to work in-game (tests AD/AJ, 2026-11-20). A
    Yuke's-style variant that includes short literal runs inside groups
    (byte-identical to Yuke's output for the same pairs) HUNG the game
    on the same TIM (test AQ vs AD, 2026-11-20) -- the game's decoder
    evidently does not handle grouped literals the way bpe.py does.
    Do not "improve" this without re-testing test AD's exact case.
    """
    out = bytearray()
    i = 0
    while i < 256:
        if i in pairs:
            # run of pair codes, emitted in groups of <= 128
            j = i
            while j < 256 and j in pairs:
                j += 1
            k = i
            while k < j:
                n = min(j - k, 128)
                out.append(n - 1)
                for c in range(k, k + n):
                    a, b = pairs[c]
                    out.append(a)
                    out.append(b)
                k += n
            i = j
        else:
            # run of literal codes
            j = i
            while j < 256 and j not in pairs:
                j += 1
            if j == 256:
                # final literal run: skip in chunks; each non-final
                # chunk is followed by a forced literal entry read
                while i < 256:
                    rem = 256 - i
                    if rem <= 128:
                        out.append(0x7F + rem)
                        i = 256
                    else:
                        out.append(0x7F + 127)
                        i += 127
                        out.append(i)  # literal entry: a == code
                        i += 1
            else:
                # literal run followed by a pair: skip it in chunks
                # of <= 127 (each followed by a literal entry read),
                # then the final skip's forced entry read defines the
                # pair code itself.
                remaining = j - i
                while remaining > 127:
                    out.append(0x7F + 127)
                    i += 127
                    remaining -= 127
                    out.append(i)  # literal entry
                    i += 1
                    remaining -= 1
                if remaining == 0:
                    # chunking landed exactly on the pair code: the
                    # decoder is at a token boundary, so define the
                    # pair with a 1-entry group (a skip byte of 0
                    # would be 0x7F, i.e. a 128-entry group -- wrong).
                    out.append(0)
                else:
                    out.append(0x7F + remaining)
                    i += remaining
                # entry read for code i (the pair)
                a, b = pairs[i]
                out.append(a)
                out.append(b)
                i += 1
    return bytes(out)


def compress_block(data):
    """Compress one block of input with Gage BPE.

    Returns (pairs, compressed_bytes). Greedy: repeatedly replace the
    most frequent adjacent pair with an unused code byte, subject to
    the depth cap. Stops when no pair occurs twice, no unused code
    remains, or every remaining pair would exceed the depth cap.
    """
    cur = bytearray(data)
    pairs = {}
    depth = [0] * 256
    # Bytes referenced as pair components: a component byte must keep
    # the meaning it had when the pair was created, so it can never
    # later become a pair code itself (that would rewrite the earlier
    # pair's expansion -- the decoder uses the final dictionary).
    referenced = set()
    while len(cur) >= 2:
        # count adjacent pairs (C-speed via zip + Counter)
        counts = Counter(zip(cur, cur[1:]))
        if not counts:
            break
        used = set(cur)
        chosen = None
        # most_common(32) bounds the fallback scan; the depth cap and
        # code availability rarely reject the top candidates
        for (a, b), cnt in counts.most_common(32):
            if cnt < 3:
                break
            if max(depth[a], depth[b]) + 1 > MAX_DEPTH:
                continue
            # find an unused code byte: not in the current data, not
            # already a pair code, not referenced as a component of
            # any existing pair, and c != a (decoder treats a == c
            # as a literal). Never reuse a pair code: other pairs may
            # still reference it, and redefining it creates cycles
            # (decoder expands forever / explodes). Never use a
            # referenced component byte either: redefining it rewrites
            # the earlier pair's expansion.
            for c in range(256):
                if (c not in used and c not in pairs
                        and c not in referenced and c != a):
                    chosen = (a, b, c)
                    break
            if chosen:
                break
        if not chosen:
            break
        a, b, c = chosen
        # replace all non-overlapping occurrences of (a, b) with c
        # (bytearray.replace has exactly these semantics, in C)
        cur = cur.replace(bytes((a, b)), bytes((c,)))
        pairs[c] = (a, b)
        referenced.add(a)
        referenced.add(b)
        depth[c] = max(depth[a], depth[b]) + 1
    return pairs, bytes(cur)


def compress_section(data):
    """Compress a full input buffer into one BPE section (bytes).

    The input is split into EQUAL-SIZE blocks (nblocks = ceil(len / 8192)):
    fixed 8192-byte chunks left a tiny tail block (64 bytes in -> 2 bytes
    compressed) for the 16,448-byte name sheet, and the game's decoder
    hangs on that degenerate block (bisected 2026-11-20, tests J/K).
    Equal chunks keep every block substantial.
    """
    nblocks = max(1, (len(data) + MAX_BLOCK_IN - 1) // MAX_BLOCK_IN)
    chunk_size = (len(data) + nblocks - 1) // nblocks
    payload = bytearray()
    off = 0
    while off < len(data):
        chunk = data[off:off + chunk_size]
        off += len(chunk)
        pairs, cdata = compress_block(chunk)
        if len(cdata) > 0xFFFF:
            raise ValueError("compressed block too large for u16 length")
        payload += emit_dict(pairs)
        payload += struct.pack("<H", len(cdata))
        payload += cdata
    header = b"BPE " + struct.pack("<III", 0x100, len(payload), len(data))
    return header + bytes(payload)


def main():
    if len(sys.argv) >= 2 and sys.argv[1] == "--roundtrip":
        sys.path.insert(0, str(Path(__file__).parent))
        from bpe import decompress_section
        d = Path(sys.argv[2])
        ok = fail = 0
        for f in sorted(d.glob("*.bin")):
            raw = f.read_bytes()
            comp = compress_section(raw)
            try:
                dec = decompress_section(comp)
            except Exception as e:
                print(f"{f.name}: DECODE FAIL: {e}")
                fail += 1
                continue
            if dec == raw:
                print(f"{f.name}: OK  {len(raw)} -> {len(comp)} "
                      f"({100 * len(comp) / len(raw):.1f}%)")
                ok += 1
            else:
                print(f"{f.name}: MISMATCH ({len(dec)} vs {len(raw)})")
                fail += 1
        print(f"roundtrip: {ok} ok, {fail} failed")
        return 0 if fail == 0 else 1
    if len(sys.argv) != 3:
        print(__doc__)
        return 2
    data = Path(sys.argv[1]).read_bytes()
    comp = compress_section(data)
    Path(sys.argv[2]).write_bytes(comp)
    print(f"{len(data)} -> {len(comp)} bytes "
          f"({100 * len(comp) / len(data):.1f}%)")
    return 0


if __name__ == "__main__":
    sys.exit(main())


def dummy_block(size):
    """Build a BPE block that decompresses to zero bytes, of exactly `size` bytes.

    The block is a dictionary covering all 256 codes as literals, followed by
    a u16 block length of 0. Used to pad a section to an exact total length:
    the game reads BPE sections SEQUENTIALLY (advancing by each section's
    csize), so a rebuilt section MUST be exactly the original's length or
    every following section desyncs and the game hangs (bisected 2026-11-20,
    tests W2/Z/AA/AB/AC/AD).

    Only odd sizes >= 5 are directly buildable (each single-entry group adds
    2 bytes). Even sizes are built by the caller from two odd blocks.
    Returns None if the size cannot be built.
    """
    dsize = size - 2
    if dsize < 3:
        return None
    for g in range(0, 256):
        out = bytearray()
        for c in range(g):
            out.append(0)  # group of 1 entry
            out.append(c)  # literal: a == code
        i = g
        while i < 256:
            rem = 256 - i
            if rem <= 128:
                out.append(0x7F + rem)  # skip lands exactly on 256
                i = 256
            else:
                out.append(0x7F + 127)  # skip 127
                i += 127
                out.append(i)  # forced literal entry
                i += 1
        if len(out) == dsize:
            return bytes(out) + b"\x00\x00"
        if len(out) > dsize:
            break
    return None


def split_padding(need):
    """Split `need` bytes into dummy-block sizes (each odd, 5..199).

    Dummy blocks are capped at 199 bytes (dictionary <= 197 bytes) because
    the game's decoder has a fixed-size dictionary buffer around 256 bytes:
    a 366-byte dictionary hung the game (test AK, 2026-11-20) while 256-byte
    dictionaries work (test AJ). The largest dictionary in any original
    section is 228 bytes; 197 stays safely under both limits.

    Returns a list of sizes summing to `need`, or None if impossible
    (need < 5, or need in {6, 8} with no room to borrow -- the caller
    should adjust the compression to avoid those gaps).
    """
    MAX_BLOCK = 199
    if need < 5:
        return None
    if need % 2 == 0 and need < 10:
        return None
    parts = []
    remaining = need
    while remaining > MAX_BLOCK:
        parts.append(MAX_BLOCK - 2)  # 99, leaves room to fix the remainder
        remaining -= (MAX_BLOCK - 2)
    # Fix up an unbuildable remainder by shrinking the last big block.
    while remaining in (1, 2, 3, 4, 6, 8):
        if not parts:
            return None
        parts[-1] -= 2
        remaining += 2
        if parts[-1] < 5:
            return None
    if remaining == 0:
        pass
    elif remaining % 2 == 1:
        parts.append(remaining)
    else:
        # even remainder >= 10: split into two roughly-equal odd parts,
        # both >= 5. (Avoid a 5-byte dummy: its 3-byte dictionary
        # correlated with hangs in tests AQ/AN, 2026-11-20.)
        half = remaining // 2
        if half % 2 == 0:
            half -= 1
        parts.append(half)
        parts.append(remaining - half)
    assert sum(parts) == need
    assert all(5 <= p <= MAX_BLOCK and p % 2 == 1 for p in parts)
    return parts


def pad_payload(payload, target_len):
    """Pad a BPE payload to exactly `target_len` bytes with dummy blocks.

    `payload` is the section payload WITHOUT the 16-byte header.
    Raises ValueError if the payload is already longer than the target,
    or if the padding cannot be built (needs 1, 2, 3, 4, 6 or 8 bytes --
    caller should adjust the compression to avoid those gaps).
    """
    need = target_len - len(payload)
    if need < 0:
        raise ValueError(f"payload {len(payload)}B already exceeds target {target_len}B")
    if need == 0:
        return bytes(payload)
    parts = split_padding(need)
    if parts is None:
        raise ValueError(f"cannot pad {need} bytes")
    out = bytearray(payload)
    for s in parts:
        b = dummy_block(s)
        if b is None:
            raise ValueError(f"cannot build dummy block of {s} bytes")
        out += b
    assert len(out) == target_len
    return bytes(out)


def compress_section_exact(data, target_total_len):
    """Compress `data` into a BPE section of EXACTLY `target_total_len` bytes.

    Compresses normally, then pads the payload with dummy zero-output blocks
    so the section total (16-byte header + payload) equals the target.
    The target is the ORIGINAL section's total length -- required because the
    game reads sections sequentially by csize (see dummy_block).

    Tries increasing block counts (starting from the default ceil(len/8192))
    and picks the first where the payload fits AND every real block's
    dictionary is <= 256 bytes (the game's dictionary buffer is ~256 bytes;
    a 366-byte dictionary hung the game, test AK 2026-11-20, while a
    256-byte dictionary works, test AJ).

    Raises ValueError if no block count fits, or if the padding gap is
    unbuildable (0/1/2/3/4/6/8 bytes).
    """
    import math
    target_payload = target_total_len - 16
    base_nblocks = max(1, (len(data) + MAX_BLOCK_IN - 1) // MAX_BLOCK_IN)
    last_err = None
    # Try from 1 block upward: fewer blocks = smaller payload (less
    # dictionary overhead) but larger dictionaries; more blocks = smaller
    # dictionaries but larger payload. Pick the smallest block count that
    # satisfies both the payload and dictionary limits.
    for nblocks in range(1, base_nblocks + 6):
        chunk_size = (len(data) + nblocks - 1) // nblocks
        payload = bytearray()
        max_dict = 0
        for off in range(0, len(data), chunk_size):
            chunk = data[off:off + chunk_size]
            pairs, cdata = compress_block(chunk)
            d = emit_dict(pairs)
            max_dict = max(max_dict, len(d))
            if len(cdata) > 0xFFFF:
                raise ValueError("compressed block too large for u16 length")
            payload += d
            payload += struct.pack("<H", len(cdata))
            payload += cdata
        if len(payload) > target_payload:
            last_err = (f"nblocks={nblocks}: payload {len(payload)}B "
                        f"exceeds target {target_payload}B")
            continue
        if max_dict > 256:
            last_err = (f"nblocks={nblocks}: max dict {max_dict}B > 256B")
            continue
        try:
            padded = pad_payload(bytes(payload), target_payload)
        except ValueError as e:
            last_err = f"nblocks={nblocks}: {e}"
            continue
        return (b"BPE " + struct.pack("<III", 0x100, len(padded), len(data))
                + padded)
    raise ValueError(f"compress_section_exact failed for target "
                     f"{target_total_len}B: {last_err}")
