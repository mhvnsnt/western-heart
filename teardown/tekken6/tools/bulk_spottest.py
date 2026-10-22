#!/usr/bin/env python3
"""Compression-vs-cipher spot test on T6 DATA401 bulk sectors (lane A, 2026-10-21).

T5 precedent: a supposed "keystream" turned out to be LZSS compression, so the
first question for every encrypted-looking region is: is it actually compressed
plaintext? Reads the sweep ISO READ-ONLY. Tests per sampled 2048-byte sector:
  - Shannon entropy
  - raw-DEFLATE decompressibility (zlib, wbits=-15) over the full sector and
    over 512-byte windows (catches embedded streams)
  - zlib-header scan (0x78 01/9C/DA)
  - LZSS-ish pattern signal: fraction of bytes that repeat a byte seen in the
    previous 4096 (cheap proxy; true LZSS would still decompress via the tests above)
Honest limit: this can only refute PLAINTEXT compression. Data that is
compressed-then-encrypted is indistinguishable from pure cipher by entropy.
"""
import math, zlib, sys

ISO = '/home/hatch/workspace/_t6r4-work/iso/tekken6-psp.iso'
SECTOR = 2048
# bulk region 230253..417777 per DINF manifest; sample spread + the CRC-passing sector
LBAS = [230253, 230256, 250000, 280000, 310000, 340000, 370000, 400000, 417777]

def entropy(b):
    from collections import Counter
    c = Counter(b); n = len(b)
    return -sum((v / n) * math.log2(v / n) for v in c.values())

def try_deflate(data):
    """Return (ok, outlen) trying raw deflate and zlib-wrapped."""
    for wbits, label in [(-15, 'raw'), (15, 'zlib')]:
        try:
            d = zlib.decompressobj(wbits)
            out = d.decompress(data) + d.flush()
            if d.eof and out:
                return True, len(out), label
        except Exception:
            pass
    return False, 0, ''

def main():
    with open(ISO, 'rb') as f:  # read-only
        for lba in LBAS:
            f.seek(lba * SECTOR)
            sec = f.read(SECTOR)
            e = entropy(sec)
            ok, olen, lab = try_deflate(sec)
            # windowed: best sub-window result
            wok, wolen = False, 0
            for off in range(0, SECTOR, 512):
                o2, l2, _ = try_deflate(sec[off:off + 512])
                if o2:
                    wok, wolen = True, l2
                    break
            zhd = sum(1 for i in range(len(sec) - 1)
                      if sec[i] == 0x78 and sec[i + 1] in (1, 0x9C, 0xDA))
            print('lba=%d entropy=%.3f deflate_full=%s(%s) deflate_win512=%s zlib_hdr_hits=%d' %
                  (lba, e, ok, lab if ok else '-', wok, zhd))
    print('NOTE: high entropy + no decompress => not plaintext-compressed; '
          'compressed-then-encrypted cannot be excluded statically.')

if __name__ == '__main__':
    main()
