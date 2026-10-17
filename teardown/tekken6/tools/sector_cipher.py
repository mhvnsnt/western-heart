#!/usr/bin/env python3
"""Python reference model of Tekken 6 PSP sector cipher (EBOOT 0x8AA2CA8).

Transliterated instruction-by-instruction from EBOOT.DECRYPTED.ELF.
All arithmetic is 32-bit wraparound (MIPS semantics). daddu->addu (values fit).

Call convention (from caller 0x8AA305C):
    cipher(K1, K2, dst_words, length_bytes, t0=0, t1=0)
where K1=[struct+8], K2=[struct+12] (the per-sector crypto header words).

Algorithm:
  keystream k evolves as: k = 5*rotr(k,29) + 1   (per word)
  seed per block:  r = (3*a0) mod 29   (via reciprocal-mult magic 0x8D3DCB09)
                   s = rotr((t4+K1) + bitrev(t4+K1), r+2)
                   k0 = s ^ K2
  dst[i] ^= k
"""
MASK = 0xFFFFFFFF

def u32(x): return x & MASK
def s32(x):
    x &= MASK
    return x - 0x100000000 if x & 0x80000000 else x
def sra(x, n):
    return u32(s32(x) >> n)
def rotr(x, n):
    n &= 31; x = u32(x)
    return u32((x >> n) | (x << (32 - n))) if n else x
def bitrev(x):
    x = u32(x); r = 0
    for i in range(32):
        r = (r << 1) | ((x >> i) & 1)
    return r

# tail byte-mask table @0x8BCE7A4 (from ELF)
TAIL_MASKS = [0xffffff00, 0xffff0000, 0xff000000]

def cipher_block(K1, K2, dst, length, t0_in=0, t1_in=0):
    """dst: list of 32-bit words (mutable). length: byte length. Returns words processed."""
    t9 = length
    t4 = u32(t0_in)
    v0 = u32(t1_in << 22)
    a0 = u32(t4 >> 10)          # logical
    t0 = u32(length + 3)
    a0 = u32(v0 | a0)
    a2f = u32(t1_in << 30)
    v0 = u32(t4 >> 2)           # logical
    v0 = u32(a2f | v0)
    t1 = v0 & 0xFF
    a3 = u32(t9 + 6)
    t3 = u32(0x100 - t1)
    neg = s32(t0) < 0
    t5 = t9 & 3
    if neg:
        t0 = a3
    t4 = a0
    t0 = sra(t0, 2)
    a0 = u32(a0 << 1)
    t3 = u32(t3 + t0)           # daddu
    a3 = u32(a0 + t4)
    t7 = 0x8D3DCB09
    t8 = 0x100
    words_done = 0

    while True:  # loop1 @0x8aa2d2c
        prod = s32(a3) * s32(t7)
        hi = u32(prod >> 32)
        v0 = sra(a3, 31)
        v1 = hi
        v1 = u32(v1 + a3)
        v1 = sra(v1, 4)
        v1 = u32(v1 - v0)
        a1x = u32(v1 << 2)
        v0 = u32(v1 << 5)
        v0 = u32(v0 - a1x)
        v0 = u32(v0 + v1)
        a0 = u32(t4 + K1)
        v0 = u32(a3 - v0)       # a3 mod 29
        v1 = bitrev(a0)
        a0 = u32(a0 + v1)
        v0 = u32(v0 + 2)
        a0 = rotr(a0, v0)
        if s32(t1) > 0:
            # warm-up loop @0x8aa2e20
            a1 = u32(a0 ^ K2)    # delay slot of bgtz
            aa0 = 0
            while True:
                vv1 = rotr(a1, 29)
                vv0 = u32((vv1 << 2) + vv1)
                aa0 = u32(aa0 + 1)
                aa1 = u32(vv0 + 1)   # delay slot of bne
                if s32(t1) == s32(aa0):
                    break
                a1 = aa1
            a1 = aa1
        else:
            a1 = u32(a0 ^ K2)    # delay slot of bgtz
        # bgtzl t3 @0x8aa2d7c
        if s32(t3) > 0:
            a2c = 0
            while True:          # block2 @0x8aa2dbc
                w = dst[a2c]
                vv1 = rotr(a1, 29)
                vv0 = u32((vv1 << 2) + vv1)
                dst[a2c] = u32(a1 ^ w)
                words_done += 1
                a2c += 1
                vv0 = u32(vv0 + 1)
                if s32(t3) == s32(a2c):
                    break
                a1 = vv0
            t0 = u32(t0 - t3)
            if s32(t0) != 0:     # bnel @0x8aa2dec
                t4 = u32(t4 + 1)  # delay
                a3 = u32(a3 + 3)
                t3 = u32(t0 + t8)  # daddu
                if s32(t0) > 0:  # bgtz @0x8aa2d9c
                    t1 = 0       # delay
                    continue     # loop1
                # mult a3,t7 (delay of bgtz t5) - no visible effect here
                if s32(t5) > 0:  # bgtz @0x8aa2da4
                    continue     # loop1 mid (HI already recomputed)
                return words_done, 'ret-t5le0'
            # t0 == 0 -> tail
        else:
            t0 = u32(t0 - t3)
            if s32(t0) == 0:     # beqz @0x8aa2d88
                pass             # -> tail
            else:
                t4 = u32(t4 + 1)
                a3 = u32(a3 + 3)
                t3 = u32(t0 + t8)
                if s32(t0) > 0:
                    t1 = 0
                    continue
                if s32(t5) > 0:
                    continue
                return words_done, 'ret-t5le0-b'
        # tail @0x8aa2df4
        if s32(t5) <= 0:         # blezl
            return words_done, 'ret-ok'
        # tail mask apply
        mask = TAIL_MASKS[(t5 - 1)] if 1 <= t5 <= 3 else 0
        last = len(dst) - 1
        # note: real code uses s0-4 table addr and t2-4; model: apply to last word
        v0m = u32(mask & a1)
        dst[last] = u32(dst[last] ^ v0m)
        return words_done, 'ret-tail'

if __name__ == '__main__':
    import random
    # NOTE: with length=0x800 the real machine code provably processes
    # 768 words (0xC00 bytes): t3 = 256 - t1 + ((len+3)>>2) = 768.
    # Confirmed by unicorn emulation of the actual EBOOT bytes (768 stores).
    # Allocate 768 words so the test exercises the real call exactly.
    # Do NOT "fix" cipher_block to stop at 512 — the model is bit-exact to ROM.
    rnd = random.Random(42)
    for trial in range(5):
        n = 768
        data = [rnd.getrandbits(32) for _ in range(n)]
        orig = list(data)
        K1 = rnd.getrandbits(32); K2 = rnd.getrandbits(32)
        w1, r1 = cipher_block(K1, K2, data, 0x800)
        assert data != orig, "cipher did not change data!"
        w2, r2 = cipher_block(K1, K2, data, 0x800)
        assert data == orig, f"NOT an involution on trial {trial}!"
        print(f"trial {trial}: words={w1} ret={r1} involution OK")
