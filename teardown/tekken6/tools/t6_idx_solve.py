#!/usr/bin/env python3
"""T6 PSP DATA401.IDX — SOLVED mapping (verified 2026-10-24, lane D).
Cipher: EBOOT 0x8AA2CA8 stream-cipher model, keyset A from EBOOT 0x8898404
  K1=0xe11cf772 K2=0xa0dc9eb4, applied per 1024-byte block with
  t0 = block byte offset within IDX, t1 = 0. (Single-call and per-2048
  variants FAIL: first divergence at byte 1024; per-1024 tiles exactly.)
Entry: 12 bytes LE: (sector_offset_u32, size_u32, tag_u32).
  sector_offset in 2048-byte sectors relative to DATA401 region start
  (ISO sector 230256; relative sector 0 = key sector, data starts at 1).
  size in bytes; size==0xFFFFFFFF and tag==0 => sentinel (0 sectors,
  shares the next entry's offset). size==0 => empty file (0 sectors).
Verification (reproduced in idx_verify + tiling runs):
  26028/12 = 2169 = DINF entries field. Sentinel-aware tiling: 0 fails.
  First offset 1, last end 187525 = DINF data_bytes/2048 exactly.
  File starts land on MOTA/NTPP/NTXL/GZIP magics in bulk_decrypted.bin.
Usage: python3 t6_idx_solve.py <DATA401.IDX> [--out decrypted.bin] [--verify]
  (cipher model embedded; no external deps beyond stdlib)
"""
import struct, sys, math
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
    t9 = length
    t4 = u32(t0_in); v0 = u32(t1_in << 22); a0 = u32(t4 >> 10)
    t0 = u32(length + 3); a0 = u32(v0 | a0)
    a2f = u32(t1_in << 30); v0 = u32(t4 >> 2); v0 = u32(a2f | v0)
    t1 = v0 & 0xFF; a3 = u32(t9 + 6); t3 = u32(0x100 - t1)
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
K1A, K2A = 0xe11cf772, 0xa0dc9eb4
def decrypt_idx(blob):
    out = bytearray()
    for off in range(0, len(blob), 1024):
        blk = blob[off:off+1024]
        nw = (len(blk)+3)//4; tot = 256 + ((len(blk)+3)>>2) + 4
        w = list(struct.unpack('<%dI' % nw, blk)) + [0]*(tot-nw)
        cipher_block(K1A, K2A, w, len(blk), off, 0)
        out += struct.pack('<%dI' % nw, *w[:nw])
    return bytes(out[:len(blob)])
def parse(raw):
    e = struct.unpack('<%dI' % (len(raw)//4), raw)
    return [(e[i], e[i+1], e[i+2]) for i in range(0, len(e)-2, 3)]
def verify(rows, total_sectors=187525):
    fails = []
    for i in range(len(rows)-1):
        occ = 0 if rows[i][1] == 0xFFFFFFFF else math.ceil(rows[i][1]/2048)
        if rows[i][0] + occ != rows[i+1][0]: fails.append(i)
    last = rows[-1][0] + (0 if rows[-1][1] == 0xFFFFFFFF else math.ceil(rows[-1][1]/2048))
    return fails, last
if __name__ == '__main__':
    blob = open(sys.argv[1], 'rb').read()
    raw = decrypt_idx(blob)
    rows = parse(raw)
    fails, last = verify(rows)
    print(f'entries={len(rows)} tile_fails={len(fails)} first_off={rows[0][0]} last_end={last}')
    print(f'sentinels={sum(1 for r in rows if r[1]==0xFFFFFFFF)} real={sum(1 for r in rows if r[1]!=0xFFFFFFFF)}')
    if '--out' in sys.argv: open(sys.argv[sys.argv.index('--out')+1], 'wb').write(raw)
    assert not fails and last == 187525, 'TILING VERIFICATION FAILED'
    print('IDX MAPPING VERIFIED')
