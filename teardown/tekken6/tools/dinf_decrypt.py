#!/usr/bin/env python3
"""Decrypt Tekken 6 PSP DINF_400.BIN with the fixed keyset from EBOOT 0x88985BC.

Key recovery: EBOOT 0x88985BC builds a 16-byte crypto header via 0x8AA3298 with
hardcoded K1=0xebcf9603, K2=0xb3bef6a4, then decrypts via 0x8AA2E58 -> 0x8AA2CA8
(the stream cipher). Plaintext = "DINF" pack manifest (see DINF-400-DECRYPTED.md).

Self-contained: embeds the instruction-exact cipher model (no external deps).
"""
import struct, sys

MASK = 0xFFFFFFFF
def u32(x): return x & MASK
def sra(x, n):
    x = u32(x); return u32((x - 0x100000000 if x & 0x80000000 else x) >> n)
def rotr(x, n):
    n &= 31; x = u32(x)
    return u32((x >> n) | (x << (32 - n))) if n else x
def bitrev(x):
    x = u32(x); r = 0
    for i in range(32): r = (r << 1) | ((x >> i) & 1)
    return r

TAIL_MASKS = [0xffffff00, 0xffff0000, 0xff000000]

def cipher_block(K1, K2, dst, length, t0_in=0, t1_in=0):
    """Instruction-exact model of EBOOT 0x8AA2CA8. dst: mutable word list."""
    t9 = length
    t4 = u32(t0_in); v0 = u32(t1_in << 22); a0 = u32(t4 >> 10)
    t0 = u32(length + 3); a0 = u32(v0 | a0)
    a2f = u32(t1_in << 30); v0 = u32(t4 >> 2); v0 = u32(a2f | v0)
    t1 = v0 & 0xFF; a3 = u32(t9 + 6); t3 = u32(0x100 - t1)
    from functools import reduce
    neg = (t0 & 0x80000000) != 0
    t5 = t9 & 3
    if neg: t0 = a3
    t4 = a0; t0 = sra(t0, 2); a0 = u32(a0 << 1)
    t3 = u32(t3 + t0); a3 = u32(a0 + t4)
    t7 = 0x8D3DCB09; t8 = 0x100
    while True:
        prod = (a3 - 0x100000000 if a3 & 0x80000000 else a3) * (t7 - 0x100000000 if t7 & 0x80000000 else t7)
        hi = u32(prod >> 32)
        v0 = sra(a3, 31); v1 = hi; v1 = u32(v1 + a3); v1 = sra(v1, 4); v1 = u32(v1 - v0)
        a1x = u32(v1 << 2); v0 = u32(v1 << 5); v0 = u32(v0 - a1x); v0 = u32(v0 + v1)
        a0 = u32(t4 + K1); v0 = u32(a3 - v0)
        v1 = bitrev(a0); a0 = u32(a0 + v1); v0 = u32(v0 + 2); a0 = rotr(a0, v0)
        a1 = u32(a0 ^ K2)
        if (t1 & 0x80000000) == 0 and t1 > 0:
            aa0 = 0
            while True:
                vv1 = rotr(a1, 29); vv0 = u32((u32(vv1 << 2) + vv1))
                aa0 = u32(aa0 + 1); aa1 = u32(vv0 + 1)
                if t1 == aa0: break
                a1 = aa1
            a1 = aa1
        if (t3 & 0x80000000) == 0 and t3 > 0:
            a2c = 0
            while True:
                w = dst[a2c]; vv1 = rotr(a1, 29); vv0 = u32(u32(vv1 << 2) + vv1)
                dst[a2c] = u32(a1 ^ w); a2c += 1; vv0 = u32(vv0 + 1)
                if t3 == a2c: break
                a1 = vv0
            t0 = u32(t0 - t3)
            if t0 != 0:
                t4 = u32(t4 + 1); a3 = u32(a3 + 3); t3 = u32(t0 + t8)
                if (t0 & 0x80000000) == 0 and t0 > 0:
                    t1 = 0; continue
                if (t5 & 0x80000000) == 0 and t5 > 0: continue
                return
            # fallthrough to tail
        else:
            t0 = u32(t0 - t3)
            if t0 != 0:
                t4 = u32(t4 + 1); a3 = u32(a3 + 3); t3 = u32(t0 + t8)
                if (t0 & 0x80000000) == 0 and t0 > 0:
                    t1 = 0; continue
                if (t5 & 0x80000000) == 0 and t5 > 0: continue
                return
        if (t5 & 0x80000000) == 0 and t5 <= 0: return
        mask = TAIL_MASKS[t5 - 1] if 1 <= t5 <= 3 else 0
        dst[len(dst) - 1] = u32(dst[len(dst) - 1] ^ u32(mask & a1))
        return

K1, K2 = 0xebcf9603, 0xb3bef6a4

def main():
    p = sys.argv[1] if len(sys.argv) > 1 else \
        '/home/hatch/workspace/game-reverse-engineering/tekken6/extracted/DINF_400.BIN'
    blob = open(p, 'rb').read()
    ln = len(blob); nwords = (ln + 3) // 4
    total = 256 + ((ln + 3) >> 2) + 4
    w = list(struct.unpack('<%dI' % nwords, blob)) + [0] * (total - nwords)
    cipher_block(K1, K2, w, ln)
    raw = struct.pack('<%dI' % nwords, *w[:nwords])
    assert raw[:4] == b'DINF', f'bad magic: {raw[:4]!r}'
    print(f'DINF_400.BIN decrypted OK ({ln} bytes), magic=DINF')
    print(f'  version={struct.unpack("<I", raw[4:8])[0]} unit={struct.unpack("<I", raw[8:12])[0]}')
    print(f'  entries={struct.unpack("<I", raw[0x24:0x28])[0]} data_bytes={struct.unpack("<I", raw[0x28:0x2C])[0]}')
    print(f'  names: {raw[0x30:0x3C].split(bchr(0))[0]!r}, {raw[0x40:0x4C].split(bchr(0))[0]!r}')
    print(f'  build_path: {raw[0x50:0x78].split(bchr(0))[0]!r}')

def bchr(n): return bytes((n,))
main()
