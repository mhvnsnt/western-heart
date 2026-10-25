#!/usr/bin/env python3
"""Tekken 6 PSP — DATA401 "GZIP" container decoder (custom DEFLATE variant).

ROUND 2 UPDATE (2026-10-20, sweep lane 2). Supersedes the decrypt10 copy of
tekken6_inflate.py. One format bug is FIXED here (CL repeat-zero semantics);
one remains open (main-loop length composition). Status: 20/76 containers
decode byte-exact (size AND adler32 verified); the 56 dynamic-block
containers parse cleanly through their headers and fail only at the first
distance that exceeds the output produced so far.

FORMAT (all facts below are from the EBOOT, re-verified 2026-10-20 by
Ghidra 12.1.4 headless decompilation of the decrypted EBOOT region
0x8b54000-0x8b57000; see ROUND2-DECRYPT-GMO-STATUS.md for the evidence):

- Container: 20-byte header, magic "GZIP" (some files carry a 16-byte
  prefix before the magic), u32 fields; w[3] = uncompressed size; then a
  zlib stream (0x78 0xda) whose 4-byte trailer is the adler32 of the
  plaintext. The adler32 is the byte-exactness oracle.
- The game-side entry point is the zlib wrapper at EBOOT vaddr 0x8b559c8:
  it validates the 2-byte zlib header via 0x8b55ab0 (CMF/FLG mod-31 check),
  REJECTS FDICT (FLG & 0x20), requires CM=8, calls the inflate at
  0x8b55bf0, and returns the adler32 trailer through its out-param.
  => No preset dictionary is used. (This kills the old "dictionary"
  theories: priming the window only masks the real length defect.)
- Inflate 0x8b55bf0 keeps its tables on the stack, seeded from the table
  block at 0x8bd6340:
    ORDER        @ 0x8bd6346: [16,19,27,0,8,7,9,6,10,5,11,4,12,3,13,2,14,1,15]
                 (byte-exact in the binary; differs from RFC1951 order at
                 positions 1,2 — symbols 19 and 27 replace 17 and 18)
    LENGTH table @ 0x8bd637c: 32 signed halfwords (packed, see below)
    DIST table   @ 0x8bd63bc: 30 halfwords = standard DBASE - 1
- Code lengths are read by the routine at 0x8b55fa8, which falls through
  into the table builder at 0x8b560b4. The builder's input contract is
  halfwords of (code_length << 9) | symbol for nonzero lengths only, in
  symbol order; it stores NEGATED lengths while constructing codes.
- DISTANCE (proven from the tables + Ghidra listing of the match path):
    dist = DBASE_EBOOT[dsym] + extra + 1
    extra = the next (30 - clz32(DBASE_EBOOT[dsym])) bits if base >= 4
            else 0 bits.
  The match path counts leading zeros of the table value with the
  Allegrex CLZ instruction at 0x8b55e08 and subtracts 0x1e (30) at
  0x8b55e0c. This is mathematically identical to standard deflate
  distances. The decoder errors (returns 0x80000104/0x80000108) if a
  distance exceeds the output produced so far — so a too-far distance in
  our decode PROVES an upstream defect, never a format feature.

FIXED IN ROUND 2 — CL repeat-zero semantics:
  Rounds 4-11 read the EBOOT as giving repeat symbols 19 and 27 extra-bit
  counts of 10 and 18 (bases 3 and 11). That reading is WRONG. With
  standard-deflate counts — 19 = (3 extra bits, base 3), 27 = (7 extra
  bits, base 11), i.e. exactly RFC1951 symbols 17/18 renumbered — every
  dynamic header in all 76 containers parses to an exactly Kraft-complete
  code (sum 2^-len == 1.0 for both lit and dist tables), and the 56
  dynamic files then fail ONLY at a distance check, never in a header.
  With the old counts, headers overran (e.g. container 3 produced 1236
  code lengths for a 315-length table). Symbol 16 = repeat-previous,
  3 + getbits(2), is confirmed in the Ghidra decompilation of 0x8b55fa4.

STILL OPEN — main-loop length composition:
  Lengths are NOT plain LBASE+extra in the game's loop. The length table
  entries are packed signed halfwords; the loop arithmetic-shifts the
  entry right by 4 (0x8b55de8: sra s4, v0, 4) after a BITREV (Allegrex,
  0x8b55de4) and obtains the extra bits through the shared getbits at
  0x8b55e70/0x8b55e8c, which derives its bit count from the descriptor
  (sra t2, t2, 0x1c at 0x8b55e8c). Net effect measured on container 0 with
  standard LBASE/LEXT: output is 1,418 bytes SHORT over 9,460 matches
  (some files overshoot instead — container 4 by 508), so distances
  eventually exceed the produced output and the strict decoder stops.
  Emulating the four direct readings of the shift/subtract composition
  (-(X>>4) +/- extra, +/- 1) all desync container 0 within the first
  matches, so the getbits contract itself is part of the formula.
  Next step (documented in the ROUND2 doc): a live PPSSPP trace of
  0x8b55bf0 on container 0, or an Allegrex-capable Ghidra Sleigh so the
  decompiler stops truncating at the BITREV.

Usage:
  tekken6_gzip.py <bulk_decrypted.bin> <manifest.json> <gzip_index>
Prints size/adler verdict; exit 0 only on byte-exact decode.

ROUND 5 RESOLUTION (2026-10-21, PR #446) — the "STILL OPEN" item above
is CLOSED, and it was never in this decoder: the input bytes were
corrupt. The round-3 bulk decryptor called the sector cipher once per
2048-byte sector; the game calls it once per 1024-byte block. Every
odd 1024-byte block of bulk_decrypted.bin was therefore garbage, and
any stream spanning one desynced exactly as documented above (short
output, too-far distances, apparent length-composition defect). With
per-1024 decryption (tools/bulk_decrypt.py) this UNMODIFIED decoder
scores 76/76 byte-exact (size + adler32), and tools/decode_all76.py
reproduces the same 76/76 with plain zlib — the game's inflate is
standard, as the live PPSSPP trace proved (game dest == zlib output,
byte-for-byte). The EBOOT quirks documented above (symbol order,
dist = std − 1 + 1) are real but mathematically equivalent to RFC1951.
There is no custom DEFLATE variant and no encode context. See
ROUND5-STATUS.md F12/F13. NOTE: this script reads a bulk file — only
trust bulks produced by tools/bulk_decrypt.py, NOT the round-3
bulk_decrypted.bin.
"""
import json
import struct
import sys
import zlib

ORDER = [16, 19, 27, 0, 8, 7, 9, 6, 10, 5, 11, 4, 12, 3, 13, 2, 14, 1, 15]

LBASE = [3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 15, 17, 19, 23, 27, 31, 35, 43, 51,
         59, 67, 83, 99, 115, 131, 163, 195, 227, 258]
LEXT = [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4,
        4, 5, 5, 5, 5, 0]
# EBOOT DIST table @ 0x8bd63bc = standard DBASE - 1
DBASE_EBOOT = [0, 1, 2, 3, 4, 6, 8, 12, 16, 24, 32, 48, 64, 96, 128, 192,
               256, 384, 512, 768, 1024, 1536, 2048, 3072, 4096, 6144, 8192,
               12288, 16384, 24576]
DBASE_STD = [1, 2, 3, 4, 5, 7, 9, 13, 17, 25, 33, 49, 65, 97, 129, 193, 257,
             385, 513, 769, 1025, 1537, 2049, 3073, 4097, 6145, 8193, 12289,
             16385, 24577]
DEXT_STD = [0, 0, 0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9,
            10, 10, 11, 11, 12, 12, 13, 13]


def clz32(x):
    return 32 - x.bit_length() if x else 32


class BitReader:
    def __init__(self, data):
        self.d = data
        self.pos = 0

    def bits(self, n):
        v = 0
        for i in range(n):
            byte = self.d[self.pos >> 3]
            v |= ((byte >> (self.pos & 7)) & 1) << i
            self.pos += 1
        return v


def build_huffman(lengths):
    maxlen = max(lengths) if lengths else 0
    bl_count = [0] * (maxlen + 1)
    for length in lengths:
        if length:
            bl_count[length] += 1
    code = 0
    next_code = [0] * (maxlen + 1)
    for b in range(1, maxlen + 1):
        code = (code + bl_count[b - 1]) << 1
        next_code[b] = code
    table = {}
    for sym, length in enumerate(lengths):
        if length:
            c = next_code[length]
            next_code[length] += 1
            rc = 0
            for i in range(length):
                rc = (rc << 1) | ((c >> i) & 1)
            table[(rc, length)] = sym
    return table


def decode_symbol(br, table):
    code = 0
    for length in range(1, 16):
        byte = br.d[br.pos >> 3]
        bit = (byte >> (br.pos & 7)) & 1
        br.pos += 1
        code |= bit << (length - 1)
        if (code, length) in table:
            return table[(code, length)]
    raise ValueError("invalid huffman code")


def decode_dynamic(br, hlit_n, hdist_n):
    """Dynamic block header. Repeat semantics per ROUND 2 fix (see header):
    16 = repeat previous (3 + 2 bits), 19 = zeros (3 + 3 bits),
    27 = zeros (11 + 7 bits)."""
    hclen = br.bits(4)
    cl_lens = [0] * 28
    for i in range(hclen + 4):
        cl_lens[ORDER[i]] = br.bits(3)
    cl_table = build_huffman(cl_lens)
    total = hlit_n + hdist_n
    lens = []
    while len(lens) < total:
        sym = decode_symbol(br, cl_table)
        if sym <= 15:
            lens.append(sym)
        elif sym == 16:
            rep = 3 + br.bits(2)
            prev = lens[-1] if lens else 0
            lens.extend([prev] * rep)
        elif sym == 19:
            rep = 3 + br.bits(3)
            lens.extend([0] * rep)
        elif sym == 27:
            rep = 11 + br.bits(7)
            lens.extend([0] * rep)
        else:
            raise ValueError(f"unexpected repeat symbol {sym}")
    return lens[:hlit_n], lens[hlit_n:hlit_n + hdist_n]


def decompress(data, max_out=64 * 1024 * 1024):
    """Strict decode (EBOOT-faithful): raises on dist > out_len.
    Returns (plaintext, bits_used)."""
    br = BitReader(data)
    out = bytearray()
    while True:
        bfinal = br.bits(1)
        btype = br.bits(2)
        if btype == 0:
            br.pos = (br.pos + 7) & ~7
            ln = struct.unpack('<H', data[br.pos >> 3:(br.pos >> 3) + 2])[0]
            br.pos += 16
            nln = struct.unpack('<H', data[br.pos >> 3:(br.pos >> 3) + 2])[0]
            br.pos += 16
            assert ln ^ 0xFFFF == nln
            out.extend(data[br.pos >> 3:(br.pos >> 3) + ln])
            br.pos += ln * 8
        elif btype in (1, 2):
            if btype == 2:
                hlit = br.bits(5)
                hdist = br.bits(5)
                lit_lens, dist_lens = decode_dynamic(br, hlit + 257, hdist + 1)
                lit_t = build_huffman(lit_lens)
                dist_t = build_huffman(dist_lens)
            else:
                lit_t = build_huffman([8] * 144 + [9] * 112 + [7] * 24 + [8] * 8)
                dist_t = build_huffman([5] * 32)
            while True:
                sym = decode_symbol(br, lit_t)
                if sym < 256:
                    out.append(sym)
                elif sym == 256:
                    break
                else:
                    li = sym - 257
                    length = LBASE[li] + br.bits(LEXT[li])
                    dsym = decode_symbol(br, dist_t)
                    if btype == 1:
                        dist = DBASE_STD[dsym] + br.bits(DEXT_STD[dsym])
                    else:
                        base = DBASE_EBOOT[dsym]
                        extra = br.bits(30 - clz32(base)) if base >= 4 else 0
                        dist = base + extra + 1
                    if dist > len(out):
                        raise ValueError(
                            f"dist {dist} > out_len {len(out)} (EBOOT would error)")
                    for _ in range(length):
                        out.append(out[-dist])
                if len(out) > max_out:
                    raise ValueError("output too big")
        else:
            raise ValueError("reserved btype")
        if bfinal:
            break
    return bytes(out), br.pos


def main():
    bulk_path, manifest_path, idx = sys.argv[1], sys.argv[2], int(sys.argv[3])
    manifest = json.load(open(manifest_path))
    gz = [f for f in manifest['files'] if f['magic'].startswith('GZIP')]
    entry = gz[idx]
    with open(bulk_path, 'rb') as bulk:
        bulk.seek(entry['start_rel'] * 2048)
        fdata = bulk.read(entry['size'])
    if entry['magic'] == 'GZIP+prefix16':
        fdata = fdata[16:]
    w = struct.unpack('<5I', fdata[:20])
    body = fdata[20:]
    expect = w[3]
    data = body[2:]
    try:
        out, bits_used = decompress(data)
    except ValueError as exc:
        print(f"idx{idx} entry{entry['entry']}: FAIL {exc} (expect {expect})")
        return 1
    # The adler32 trailer sits immediately after the final deflate block
    # (containers may carry padding after it, so body[-4:] is wrong).
    adler_off = (bits_used + 7) // 8
    trailer = struct.unpack('>I', data[adler_off:adler_off + 4])[0]
    ok = len(out) == expect and zlib.adler32(out) == trailer
    print(f"idx{idx} entry{entry['entry']}: out={len(out)} expect={expect} "
          f"adler_ok={zlib.adler32(out) == trailer} BYTE-EXACT={ok}")
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
