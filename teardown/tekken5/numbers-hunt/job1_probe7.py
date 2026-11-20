#!/usr/bin/env python3
"""JOB 1 probe 7: (1) validate the checksum machinery on TK5DATA1 entries
0 and 148 (known: 148 decrypts to 'TK5RESU1' with seed 148); (2) sector 27
head (the gap in the header census); (3) payload-only decrypt (keystream
phase 0 at payload start) with seed X; (4) record-grid census over 2 MB.
"""
import struct, sys
sys.path.insert(0, "tools-Tekken5_Tools")
import decNLZ1
import tk5psp_crypt

def word_sum(data):
    n = len(data) // 4
    words = memoryview(data)[:n * 4].cast("I")
    acc = sum(words) & 0xFFFFFFFF
    return (acc - 0x100000000 if acc >= 0x80000000 else acc) & 0xFFFFFFFF

CODE = open("/tmp/dec_code.bin", "rb").read()
T1 = [struct.unpack_from("<II", CODE, 0x27B5B0 + 8 * i) for i in range(1571)]
CK1 = [struct.unpack_from("<I", CODE, 0x27E838 + 4 * i)[0] for i in range(1571)]
print("== TK5DATA1 checksum validation ==")
with open("../raw/TK5DATA1.BIN", "rb") as f:
    t1 = f.read(30000000)  # first 30 MB local
for idx in [0, 148]:
    s, z = T1[idx]
    data = t1[s * 2048:s * 2048 + z]
    raw = word_sum(data)
    print(f"  T1[{idx}] sector={s} size={z} ck={CK1[idx]:#010x} "
          f"word_sum(raw)={raw:#010x} match={raw == CK1[idx]} head={data[:16].hex()}")
    if raw != CK1[idx]:
        buf = bytearray(data)
        tk5psp_crypt.decrypt_sector_data_fast(buf, idx, len(buf))
        ds = word_sum(bytes(buf))
        print(f"    dec(seed={idx}) word_sum={ds:#010x} match={ds == CK1[idx]} head={bytes(buf[:16])!r}")

with open("../raw/TK5DATA0.BIN", "rb") as f:
    d = f.read(2 * 1024 * 1024)
print("\n== sector 27 head (census gap) ==")
print(f"  TK5DATA0[27*2048:27*2048+64] = {d[27*2048:27*2048+64].hex()}")
print(f"  as u32: {[hex(v) for v in struct.unpack('<16I', d[27*2048:27*2048+64])]}")
print(f"  sector 26 head: {d[26*2048:26*2048+32].hex()}")
print(f"  sector 28 head: {d[28*2048:28*2048+32].hex()}")

print("\n== payload-only decrypt, record 0 (phase 0 at payload start) ==")
X = struct.unpack("<I", d[16:20])[0]
for seed, label in [(X, "seed=X"), (0, "seed=0")]:
    pay = bytearray(d[32:18432])
    tk5psp_crypt.decrypt_sector_data_fast(pay, seed, len(pay))
    pr = sum(1 for b in pay if 32 <= b < 127) / len(pay)
    ze = sum(1 for b in pay if b == 0) / len(pay)
    print(f"  {label}: printable={pr:.3f} zero={ze:.3f} head={bytes(pay[:32]).hex()}")
    for m in [b"TK5RESU1", b"TIM2", b"GYM1", b"BDPK", b"NUDP"]:
        i = bytes(pay).find(m)
        if i != -1:
            print(f"    magic {m} at {i}")
    try:
        out = decNLZ1.unpack_sc3game(bytes(pay))
        print(f"    NLZ1 out_len={len(out)} head={bytes(out[:16]).hex()}")
    except Exception as e:
        print(f"    NLZ1 FAIL {str(e)[:50]}")

print("\n== record-grid census, first 2 MB (1024 sectors) ==")
HDR = bytes.fromhex("01000000080000002b440000da000000")
hits = [s for s in range(1024) if d[s * 2048:s * 2048 + 16] == HDR]
print(f"  sectors starting with the 16-byte header: {hits[:40]}")
print(f"  count={len(hits)} diffs={[hits[i+1]-hits[i] for i in range(min(20, len(hits)-1))]}")
