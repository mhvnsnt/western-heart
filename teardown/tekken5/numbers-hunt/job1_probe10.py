#!/usr/bin/env python3
"""JOB 1 probe 10: seed=1 is the key (record 1's stored header == LCG
keystream(seed=1) XOR a mostly-zero plaintext header). Test seed 1 on ALL
records, then entry-level: full entry 0 decrypt (reset + continuing
keystream) vs checksum; small entry 1 decrypt vs its checksum.
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

def decrypt_continuing(data, seed):
    """LCG keystream advancing across 2048-byte blocks (key advances
    512 steps per block), unlike decrypt_sector_data_fast which resets
    the keystream each block."""
    out = bytearray(data)
    key = seed & 0xFFFFFFFF
    for off in range(0, len(out), 2048):
        ks = [0] * 512
        for i in range(512):
            ks[i] = key
            key = (key * 5 + 3) & 0xFFFFFFFF
        kb = struct.pack("<512I", *ks)
        blk = out[off:off + 2048]
        n = len(blk)
        dec = int.from_bytes(blk, "little") ^ int.from_bytes(kb[:n], "little")
        out[off:off + n] = dec.to_bytes(n, "little")
    return bytes(out)

CODE = open("/tmp/dec_code.bin", "rb").read()
T0 = [struct.unpack_from("<II", CODE, 0x27E6D0 + 8 * i) for i in range(44)]
CK = [struct.unpack_from("<I", CODE, 0x27FEC4 + 4 * i)[0] for i in range(44)]

with open("../raw/TK5DATA0.BIN", "rb") as f:
    d = f.read(2 * 1024 * 1024)
REC = 18432
print("== records 0..5 decrypted with seed 1 ==")
for r in range(6):
    buf = bytearray(d[r * REC:(r + 1) * REC])
    tk5psp_crypt.decrypt_sector_data_fast(buf, 1, REC)
    hdr = struct.unpack("<8I", bytes(buf[:32]))
    pay = bytes(buf[32:])
    pr = sum(1 for b in pay if 32 <= b < 127) / len(pay)
    ze = sum(1 for b in pay if b == 0) / len(pay)
    print(f"  rec{r}: hdr={[hex(v) for v in hdr]} pay printable={pr:.3f} zero={ze:.3f}")
    print(f"    pay[0:32]={pay[:32].hex()}")
    for m in [b"TK5RESU1", b"TIM2", b"GYM1", b"BDPK", b"NUDP", b"COM "]:
        i = pay.find(m)
        if i != -1:
            print(f"    magic {m} at payload+{i}")
    try:
        out = decNLZ1.unpack_sc3game(pay)
        print(f"    NLZ1(pay) out_len={len(out)} head={bytes(out[:16]).hex()}")
    except Exception as e:
        print(f"    NLZ1(pay) FAIL {str(e)[:40]}")

print("\n== entry 0 full decrypt, seed 1, reset vs continuing ==")
with open("../raw/TK5DATA0.BIN", "rb") as f:
    e0 = f.read(T0[0][1])
print(f"read {len(e0)} bytes; ck[0]={CK[0]:#010x}")
buf = bytearray(e0)
tk5psp_crypt.decrypt_sector_data_fast(buf, 1, len(buf))
print(f"  reset-ks seed1 word_sum={word_sum(bytes(buf)):#010x} match={word_sum(bytes(buf)) == CK[0]}")
dec_c = decrypt_continuing(e0, 1)
print(f"  continuing-ks seed1 word_sum={word_sum(dec_c):#010x} match={word_sum(dec_c) == CK[0]}")
# how many record headers in the reset-decrypted entry match the [0,0,0x4400,0,*,0,0,0] pattern?
ok = 0
for r in range(0, 8891, 997):
    h = struct.unpack("<8I", bytes(buf[r * REC:r * REC + 32]))
    if h[0] in (0, 1) and h[1] == 0 and h[2] == 0x4400 and h[3] == 0 and h[5] == 0 and h[6] == 0 and h[7] == 0:
        ok += 1
print(f"  reset-decrypted entry: {ok}/9 sampled record headers match the seed-1 plaintext pattern")

print("\n== entry 1 (2,691,072 B @ 163878912, local) seed 1 ==")
with open("../raw/TK5DATA0.BIN", "rb") as f:
    f.seek(T0[1][0] * 2048)
    e1 = f.read(T0[1][1])
print(f"read {len(e1)} bytes; ck[1]={CK[1]:#010x}")
b1 = bytearray(e1)
tk5psp_crypt.decrypt_sector_data_fast(b1, 1, len(b1))
print(f"  reset-ks seed1 word_sum={word_sum(bytes(b1)):#010x} match={word_sum(bytes(b1)) == CK[1]}")
print(f"  reset-ks seed1 head={bytes(b1[:32]).hex()}")
c1 = decrypt_continuing(e1, 1)
print(f"  continuing-ks seed1 word_sum={word_sum(c1):#010x} match={word_sum(c1) == CK[1]}")
