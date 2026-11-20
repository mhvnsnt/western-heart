#!/usr/bin/env python3
"""JOB 1 probe 11 (lean): examine the seed-1-decrypted record layout
(17408 boundary? tail? X'?) and scan decrypted records for DW content;
streaming word-sum variants over entry 0 vs CK[0].
"""
import struct, sys
sys.path.insert(0, "tools-Tekken5_Tools")
import tk5psp_crypt

def word_sum(data):
    n = len(data) // 4
    words = memoryview(data)[:n * 4].cast("I")
    acc = sum(words) & 0xFFFFFFFF
    return (acc - 0x100000000 if acc >= 0x80000000 else acc) & 0xFFFFFFFF

CODE = open("../raw/TK5DATA3_code.bin", "rb").read()  # = decompressed code (LUT reads correctly in it)
T0 = [struct.unpack_from("<II", CODE, 0x27E6D0 + 8 * i) for i in range(44)]
CK = [struct.unpack_from("<I", CODE, 0x27FEC4 + 4 * i)[0] for i in range(44)]
REC = 18432

with open("../raw/TK5DATA0.BIN", "rb") as f:
    d = f.read(2 * 1024 * 1024)

# --- 1. decrypted record 0 layout ---
buf = bytearray(d[:REC])
tk5psp_crypt.decrypt_sector_data_fast(buf, 1, REC)
dec = bytes(buf)
print("decrypted rec0 header:", [hex(v) for v in struct.unpack("<8I", dec[:32])])
# first non-zero after the 32 zero bytes at payload start
i = 32
while i < len(dec) and dec[i] == 0:
    i += 1
print(f"first non-zero byte in dec rec0 at offset {i} (payload+{i-32})")
print(f"dec rec0[{i-16}:{i+48}] = {dec[max(0,i-16):i+48].hex()}")
print(f"dec rec0 u32s [32:96]: {[hex(v) for v in struct.unpack('<16I', dec[32:96])]}")
# zero count per 1KB block
for off in range(0, REC, 1024):
    blk = dec[off:off + 1024]
    print(f"  block @{off:#06x} zeros={blk.count(0)} printable={sum(1 for b in blk if 32 <= b < 127)}")
print(f"dec rec0 tail[-64:] = {dec[-64:].hex()}")
print(f"dec rec0 bytes around 17408 boundary [17400:17480] = {dec[17400:17480].hex()}")

# --- 2. scan decrypted first 2MB for DW content ---
print("\n== scan decrypted records 0..113 (2MB) ==")
plain = bytearray()
for r in range(114):
    b = bytearray(d[r * REC:(r + 1) * REC])
    tk5psp_crypt.decrypt_sector_data_fast(b, 1, REC)
    plain += b
plain = bytes(plain)
for m in [b"TK5RESU1", b"GYM1", b"BDPK", b"NUDP", b"item_force", b"RankingMode",
          b"Force", b"COM ", b"TIM2"]:
    idxs = []
    i = plain.find(m)
    while i != -1 and len(idxs) < 5:
        idxs.append(i); i = plain.find(m, i + 1)
    print(f"  {m}: {idxs if idxs else 'none'}")
# u32 1000000 occurrences
cnt = 0
for off in range(0, len(plain) - 4, 4):
    if struct.unpack_from("<I", plain, off)[0] == 1000000:
        cnt += 1
        if cnt <= 5:
            print(f"  u32 1000000 at plain+{off}")
print(f"  u32 1000000 total count: {cnt}")
# float 1.0 / common floats?
import collections
fl = collections.Counter()
for off in range(0, len(plain) - 4, 4):
    v = struct.unpack_from("<f", plain, off)[0]
    if v == 1.0:
        fl["1.0"] += 1
print(f"  float 1.0 count: {fl['1.0']}")

# --- 3. streaming word-sum variants over entry 0 ---
print("\n== streaming word-sum variants over entry 0 (seed 1) ==")
print(f"entry 0: size={T0[0][1]} ck[0]={CK[0]:#010x}")
acc_full = 0
acc_nohdr = 0
acc_data = 0  # only [32:32+17408] per record
with open("../raw/TK5DATA0.BIN", "rb") as f:
    remaining = T0[0][1]
    while remaining > 0:
        chunk = f.read(min(REC, remaining))
        remaining -= len(chunk)
        b = bytearray(chunk)
        tk5psp_crypt.decrypt_sector_data_fast(b, 1, len(b))
        bb = bytes(b)
        acc_full = (acc_full + sum(memoryview(bb).cast("I"))) & 0xFFFFFFFF
        acc_nohdr = (acc_nohdr + sum(memoryview(bb[32:]).cast("I"))) & 0xFFFFFFFF
        acc_data = (acc_data + sum(memoryview(bb[32:32 + 17408]).cast("I"))) & 0xFFFFFFFF
for name, v in [("full", acc_full), ("no-headers", acc_nohdr), ("data-only[32:17440]", acc_data)]:
    vv = (v - 0x100000000 if v >= 0x80000000 else v) & 0xFFFFFFFF
    print(f"  {name}: {vv:#010x} match={vv == CK[0]}")
