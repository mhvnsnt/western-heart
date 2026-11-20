#!/usr/bin/env python3
"""JOB 1 probe 9: (1) sweep T1[0] seeds 0..5000 vs its checksum (learn the
seed rule — T1[148] used seed=index, T1[0] matched neither raw nor seed 0);
(2) XOR of two record payloads (fixed-keystream evidence); (3) decrypt
full records with seed = record index; (4) numpy availability.
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
print("== sweep T1[0] seeds 0..5000 ==")
s, z = T1[0]
with open("../raw/TK5DATA1.BIN", "rb") as f:
    f.seek(s * 2048)
    e0 = f.read(z)
print(f"T1[0] size={z} ck={CK1[0]:#010x}")
found = []
for seed in range(5001):
    buf = bytearray(e0)
    tk5psp_crypt.decrypt_sector_data_fast(buf, seed, len(buf))
    if word_sum(bytes(buf)) == CK1[0]:
        found.append(seed)
        print(f"  MATCH seed={seed}")
print(f"  sweep done, matches: {found}")
# also: is T1[0] NLZ1 after raw? (checksum over decompressed?)
try:
    out = decNLZ1.unpack_sc3game(e0)
    print(f"  NLZ1(raw T1[0]) out_len={len(out)} head={bytes(out[:16]).hex()}")
    if len(out) > 100:
        print(f"  word_sum(NLZ1 out)={word_sum(bytes(out)):#010x}")
except Exception as e:
    print(f"  NLZ1(raw T1[0]) FAIL {str(e)[:50]}")

with open("../raw/TK5DATA0.BIN", "rb") as f:
    d = f.read(2 * 1024 * 1024)
REC = 18432
print("\n== XOR rec0[32:] ^ rec1[32:] (fixed-keystream test) ==")
x = bytes(a ^ b for a, b in zip(d[32:REC], d[REC + 32:2 * REC]))
print(f"  zero bytes in XOR: {x.count(0)} / {len(x)}")
# longest zero run
best = cur = 0
for b in x:
    cur = cur + 1 if b == 0 else 0
    best = max(best, cur)
print(f"  longest zero run in XOR: {best}")
print(f"  XOR[0:32]: {x[:32].hex()}")

print("\n== decrypt full record with seed = record index ==")
for r in range(4):
    buf = bytearray(d[r * REC:(r + 1) * REC])
    tk5psp_crypt.decrypt_sector_data_fast(buf, r, REC)
    hdr = struct.unpack("<8I", bytes(buf[:32]))
    pay = bytes(buf[32:])
    pr = sum(1 for b in pay if 32 <= b < 127) / len(pay)
    ze = sum(1 for b in pay if b == 0) / len(pay)
    print(f"  rec{r} seed={r}: dec-header={[hex(v) for v in hdr]} payload printable={pr:.3f} zero={ze:.3f}")
    try:
        out = decNLZ1.unpack_sc3game(pay)
        print(f"    NLZ1(payload) out_len={len(out)}")
    except Exception as e:
        print(f"    NLZ1(payload) FAIL {str(e)[:40]}")

print("\n== numpy? ==")
try:
    import numpy
    print(f"  numpy {numpy.__version__} available")
except Exception as e:
    print(f"  numpy NOT available: {e}")
