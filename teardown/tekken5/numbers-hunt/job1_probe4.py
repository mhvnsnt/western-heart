#!/usr/bin/env python3
"""JOB 1 probe 4: verify the TK5DATA0 LUT at code 0x27E6B8 (48 entries),
its checksum table, and decrypt-verify entry 0 (seed = entry index).
Read-only on the big files; reads 156 MB of local TK5DATA0 bytes.
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
FS0 = 2072586240

print("== TK5DATA0 LUT @ code 0x27E6B8 (48 x (sector,size)) ==")
entries = []
for i in range(48):
    s, z = struct.unpack_from("<II", CODE, 0x27E6B8 + 8 * i)
    entries.append((s, z))
    print(f"  [{i:2d}] sector={s:7d} off={s*2048:12d} size={z:12d} end={s*2048+z:12d}")
# tiling check
ok = True
for i in range(47):
    if entries[i + 1][0] * 2048 != entries[i][0] * 2048 + entries[i][1]:
        print(f"  TILE BREAK between entry {i} and {i+1}")
        ok = False
print(f"  tiling contiguous: {ok}")
print(f"  first start: {entries[0][0]*2048}, last end: {entries[-1][0]*2048+entries[-1][1]}, file size: {FS0}")
print(f"  sum sizes: {sum(z for _, z in entries)}")

print("\n== TK5DATA0 checksums @ code 0x27FEC4 (48 x u32) ==")
cks = [struct.unpack_from("<I", CODE, 0x27FEC4 + 4 * i)[0] for i in range(48)]
print(f"  {['%08x' % c for c in cks]}")

print("\n== entry 0 verify (TK5DATA0[0:163878912], local) ==")
with open("../raw/TK5DATA0.BIN", "rb") as f:
    e0 = f.read(entries[0][1])
print(f"  read {len(e0)} bytes")
raw_sum = compute_word_sum_fast(e0, len(e0))
print(f"  word_sum(raw)     = {raw_sum:#010x}  checksum[0] = {cks[0]:#010x}  match={raw_sum == cks[0]}")
if raw_sum != cks[0]:
    for seed in [0, 1]:
        buf = bytearray(e0)
        tk5psp_crypt.decrypt_sector_data_fast(buf, seed, len(buf))
        s = compute_word_sum_fast(bytes(buf), len(buf))
        print(f"  word_sum(dec seed={seed}) = {s:#010x}  match={s == cks[0]}")
        if s == cks[0]:
            print(f"  *** ENTRY 0 DECRYPTS WITH SEED {seed} ***")
            magics = [b"TK5RESU1", b"TIM2", b"GYM1", b"BDPK", b"NUDP", b"COM ",
                      b"item_force", b"RankingMode", b"TK5DATA", b"PS2"]
            for m in magics:
                idxs = []
                i = bytes(buf).find(m)
                while i != -1 and len(idxs) < 5:
                    idxs.append(i); i = bytes(buf).find(m, i + 1)
                if idxs:
                    print(f"    magic {m}: {idxs}")
            print(f"    head: {bytes(buf[:64]).hex()}")
            open("/tmp/tk5data0_entry0_dec.bin", "wb").write(bytes(buf))
            print("    decrypted entry 0 saved to /tmp/tk5data0_entry0_dec.bin (156MB)")
            break
