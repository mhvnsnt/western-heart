#!/usr/bin/env python3
"""JOB 1 probe: is TK5DATA0 NLZ1-compressed (decNLZ1/tk5psp_dec) and/or
LCG-sector-encrypted? Tests on bytes already on disk (local 95 chunks).
Also identifies TK5DATA3_code.bin (PKG archive vs compressed code vs
decompressed code) and scans the decompressed code for a TK5DATA0 LUT.
Read-only on the big files; writes only stdout.
"""
import struct, sys
sys.path.insert(0, "tools-Tekken5_Tools")
import decNLZ1
import tk5psp_dec
import tk5psp_crypt

RAW = "../raw/"
MAGICS = [b"TK5RESU1", b"TIM2", b"GYM1", b"BDPK", b"NUDP", b"COM ", b"PK",
          b"\x7fELF", b"TK5DATA", b"PS2", b"item_force", b"RankingMode"]

def magicscan(b, label):
    hits = []
    for m in MAGICS:
        i = b.find(m)
        while i != -1:
            hits.append((m.decode("latin1"), i))
            i = b.find(m, i + 1)
    print(f"  [{label}] len={len(b)} magics={hits[:12]} head={b[:32]!r}")
    return hits

# --- 1. What is TK5DATA3_code.bin? ---
with open(RAW + "TK5DATA3_code.bin", "rb") as f:
    code_raw = f.read()
print(f"TK5DATA3_code.bin len={len(code_raw)} head={code_raw[:16].hex()}")
cnt = struct.unpack("<I", code_raw[:4])[0]
print(f"  first u32 (PKG count if archive) = {cnt}")
# LUT check at 0x27B5B0 in this file
LUT = 0x27B5B0
ents = [struct.unpack("<II", code_raw[LUT + 8 * i: LUT + 8 * i + 8]) for i in range(5)]
print(f"  LUT@0x27B5B0 first 5 (sector,size) = {ents}")
# If this file is the PKG archive, unpack file[5]
if cnt < 30:
    maps = [struct.unpack("<II", code_raw[4 + 8 * i: 12 + 8 * i]) for i in range(cnt)]
    print(f"  PKG mappings (off,size) first 6 = {maps[:6]}")
    off, sz = maps[5]
    cmp_code = code_raw[off:off + sz]
    print(f"  file[5] len={len(cmp_code)} head={cmp_code[:16].hex()}")
    try:
        dec = decNLZ1.unpack_sc3game(cmp_code)
        print(f"  file[5] NLZ1-unpacked len={len(dec)}")
        magicscan(dec[:4096], "dec-code head")
        ents2 = [struct.unpack("<II", dec[LUT + 8 * i: LUT + 8 * i + 8]) for i in range(5)]
        print(f"  dec-code LUT@0x27B5B0 first 5 = {ents2}")
        open("/tmp/dec_code.bin", "wb").write(dec)
        print("  dec code saved to /tmp/dec_code.bin")
    except Exception as e:
        print(f"  file[5] NLZ1-unpack FAILED: {e!r}")
else:
    print("  NOT a PKG archive (count>=30); treating as code blob as-is")
    open("/tmp/dec_code.bin", "wb").write(code_raw)
    print("  saved copy to /tmp/dec_code.bin")

# --- 2. NLZ1 test on TK5DATA0 ---
with open(RAW + "TK5DATA0.BIN", "rb") as f:
    f.seek(0)
    d0 = f.read(262144)  # first 256 KiB, local
print(f"\nTK5DATA0[0:256K] head={d0[:16].hex()}")
for name, fn in [("decNLZ1.unpack_sc3game", decNLZ1.unpack_sc3game),
                 ("tk5psp_dec.decompress_blob", tk5psp_dec.decompress_blob)]:
    try:
        out = fn(d0)
        print(f"  {name}: OK out_len={len(out)}")
        magicscan(bytes(out[:4096]), name + " head")
    except Exception as e:
        print(f"  {name}: FAILED {e!r}")

# sector-start sweep: try unpacking at each 2048-byte boundary in first 64K
print("\nsector-start NLZ1 sweep (8KB windows, first 64K of TK5DATA0):")
ok = 0
for off in range(0, 65536, 2048):
    try:
        out = decNLZ1.unpack_sc3game(d0[off:off + 8192])
        if len(out) > 100:
            print(f"  off {off}: out_len={len(out)} head={bytes(out[:16]).hex()}")
            ok += 1
    except Exception:
        pass
print(f"  sweep: {ok} sector starts produced >100B output")

# --- 3. decrypt-then-unpack (seed = sector index hypothesis) ---
print("\ndecrypt-then-unpack, sector 0, seeds 0..3:")
for seed in range(4):
    buf = bytearray(d0[:2048])
    tk5psp_crypt.decrypt_sector_data_fast(buf, seed, 2048)
    try:
        out = decNLZ1.unpack_sc3game(bytes(buf))
        print(f"  seed {seed}: unpack OK out_len={len(out)} head={bytes(out[:32])!r}")
        magicscan(bytes(out[:4096]), f"seed{seed} head")
    except Exception as e:
        print(f"  seed {seed}: unpack FAILED {e!r} dec-head={bytes(buf[:16]).hex()}")
