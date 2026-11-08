#!/usr/bin/env python3
"""JOB 1 probe 12: (1) is seed 1 global? test entry 1 + entry 3 first
records; (2) decrypt small local entries 1 and 3 fully, scan for DW
numbers/magics/strings; (3) checksum-location search in the code.
"""
import struct, sys
sys.path.insert(0, "tools-Tekken5_Tools")
import tk5psp_crypt

def word_sum(data):
    n = len(data) // 4
    words = memoryview(data)[:n * 4].cast("I")
    acc = sum(words) & 0xFFFFFFFF
    return (acc - 0x100000000 if acc >= 0x80000000 else acc) & 0xFFFFFFFF

CODE = open("../raw/TK5DATA3_code.bin", "rb").read()
T0 = [struct.unpack_from("<II", CODE, 0x27E6D0 + 8 * i) for i in range(44)]
CK = [struct.unpack_from("<I", CODE, 0x27FEC4 + 4 * i)[0] for i in range(44)]
REC = 18432

def dec_records(data):
    out = bytearray(data)
    tk5psp_crypt.decrypt_sector_data_fast(out, 1, len(out))
    return bytes(out)

with open("../raw/TK5DATA0.BIN", "rb") as f:
    print("== seed-1 check on entries 1 and 3 first records ==")
    for ei in [1, 3]:
        s, z = T0[ei]
        f.seek(s * 2048)
        rec = f.read(REC)
        dec = dec_records(rec)
        hdr = struct.unpack("<8I", dec[:32])
        print(f"  entry {ei}: dec-header={[hex(v) for v in hdr]} "
              f"pattern_ok={hdr[1] == 0 and hdr[2] == 0x4400 and hdr[3] == 0 and hdr[5] == 0 and hdr[6] == 0 and hdr[7] == 0}")

    print("\n== decrypt + scan entries 1 and 3 ==")
    for ei in [1, 3]:
        s, z = T0[ei]
        f.seek(s * 2048)
        raw = f.read(z)
        dec = dec_records(raw)
        ws = word_sum(dec)
        print(f"  entry {ei}: size={z} ck[ei]={CK[ei]:#010x} word_sum(dec)={ws:#010x} match={ws == CK[ei]}")
        print(f"    head={dec[:64].hex()}")
        for m in [b"TK5RESU1", b"GYM1", b"BDPK", b"NUDP", b"item_force",
                  b"RankingMode", b"Force", b"COM ", b"TIM2", b"TK5DATA"]:
            idxs = []
            i = dec.find(m)
            while i != -1 and len(idxs) < 5:
                idxs.append(i); i = dec.find(m, i + 1)
            if idxs:
                print(f"    magic {m}: {idxs}")
        # u32 1000000 + small-int runs?
        hits = [off for off in range(0, len(dec) - 4, 4)
                if struct.unpack_from("<I", dec, off)[0] == 1000000]
        print(f"    u32 1000000 count: {len(hits)} {hits[:5]}")
        # printable-string scan: longest printable runs
        best = []
        cur = 0
        start = 0
        for i, b in enumerate(dec):
            if 32 <= b < 127:
                if cur == 0:
                    start = i
                cur += 1
            else:
                if cur >= 12:
                    best.append((cur, start, dec[start:start + cur][:60]))
                cur = 0
        best.sort(reverse=True)
        print(f"    printable runs >=12 chars: {len(best)}")
        for ln, st, txt in best[:8]:
            print(f"      len={ln} @{st}: {txt!r}")

print("\n== checksum-value search in code ==")
for val, label in [(0x6615f44a, "e0 dec word_sum"), (0x5748f144, "e0 raw word_sum"),
                   (0x41c55fea, "CK[0]")]:
    offs = []
    i = CODE.find(struct.pack("<I", val))
    while i != -1:
        offs.append(hex(i)); i = CODE.find(struct.pack("<I", val), i + 1)
    print(f"  {label} {val:#010x} found at: {offs[:5]}")
