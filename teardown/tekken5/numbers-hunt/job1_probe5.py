#!/usr/bin/env python3
"""JOB 1 probe 5 (CORRECTED): TK5DATA0 LUT = 44 entries at code 0x27E6D0
(my probe-4 dump's indices 3..46). Checksums = 44 u32 at code 0x27FEC4
(right after TK5DATA1's 1571 checksums). Verify entry 0 (163,878,912 B
@ file 0, fully local) raw + candidate seeds.
"""
import struct, sys
sys.path.insert(0, "tools-Tekken5_Tools")
import tk5psp_crypt

def compute_word_sum_fast(data, size_bytes):
    # verbatim from Tekken5_Tools FileTableGetPS2.py (author smb123w64gb)
    if size_bytes < 0:
        word_count = (size_bytes + 3) >> 2
    else:
        word_count = size_bytes >> 2
    if word_count <= 0:
        return 0
    num_words = min(word_count, len(data) // 4)
    byte_len = num_words * 4
    words = memoryview(data)[:byte_len].cast("I")
    acc = sum(words) & 0xFFFFFFFF
    return (acc - 0x100000000 if acc >= 0x80000000 else acc) & 0xFFFFFFFF

CODE = open("/tmp/dec_code.bin", "rb").read()
# TK5DATA0 LUT: 44 entries at 0x27E6D0
T0 = [struct.unpack_from("<II", CODE, 0x27E6D0 + 8 * i) for i in range(44)]
# sanity: tiling
tiling = all(T0[i + 1][0] * 2048 == T0[i][0] * 2048 + T0[i][1] for i in range(43))
print(f"T0 LUT: {len(T0)} entries, tiling={tiling}, "
      f"start={T0[0][0]*2048}, end={T0[-1][0]*2048+T0[-1][1]}, sum={sum(z for _, z in T0)}")
# checksums at 0x27FEC4
CK = [struct.unpack_from("<I", CODE, 0x27FEC4 + 4 * i)[0] for i in range(44)]
print(f"T0 checksums[0..3] = {['%08x' % c for c in CK[:4]]}")

print("\n== entry 0: sector=0 size=163878912 (local) ==")
with open("../raw/TK5DATA0.BIN", "rb") as f:
    e0 = f.read(T0[0][1])
print(f"read {len(e0)} bytes")
raw = compute_word_sum_fast(e0, len(e0))
print(f"word_sum(raw) = {raw:#010x}  ck[0] = {CK[0]:#010x}  match={raw == CK[0]}")
if raw != CK[0]:
    for seed in [0, 1, 2, 3, 1571, 1572, 1573, 1574, 1575, 1614, 1615]:
        buf = bytearray(e0)
        tk5psp_crypt.decrypt_sector_data_fast(buf, seed, len(buf))
        s = compute_word_sum_fast(bytes(buf), len(buf))
        print(f"  seed {seed}: word_sum={s:#010x} match={s == CK[0]}")
        if s == CK[0]:
            print(f"  *** ENTRY 0 DECRYPTS WITH SEED {seed} ***")
            b = bytes(buf)
            for m in [b"TK5RESU1", b"TIM2", b"GYM1", b"BDPK", b"NUDP", b"COM ",
                      b"item_force", b"RankingMode", b"TK5DATA"]:
                idxs = []
                i = b.find(m)
                while i != -1 and len(idxs) < 5:
                    idxs.append(i); i = b.find(m, i + 1)
                if idxs:
                    print(f"    magic {m}: {idxs}")
            print(f"    head: {b[:64].hex()}")
            open("/tmp/tk5data0_e0_dec.bin", "wb").write(b)
            print("    saved /tmp/tk5data0_e0_dec.bin")
            break
