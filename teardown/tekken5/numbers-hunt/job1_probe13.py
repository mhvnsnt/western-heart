#!/usr/bin/env python3
"""JOB 1 probe 13: decrypt ALL local T0 entries 0..19 (seed = index+1),
verify every record header, word_sum vs CK, content profile + magic/
string/number scan per entry. Streams one entry at a time (low memory).
Saves decrypted small entries 1 and 3 to /tmp for deeper analysis.
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
MAGICS = [b"TK5RESU1", b"GYM1", b"BDPK", b"NUDP", b"TIM2", b"COM ",
          b"item_force", b"RankingMode"]

def pat_ok(h):
    return h[1] == 0 and h[2] == 0x4400 and h[3] == 0 and h[5] == 0 and h[6] == 0 and h[7] == 0

with open("../raw/TK5DATA0.BIN", "rb") as f:
    for ei in range(20):
        s, z = T0[ei]
        seed = ei + 1
        f.seek(s * 2048)
        raw = f.read(z)
        if len(raw) < z:
            print(f"entry {ei}: SHORT READ {len(raw)}/{z} (not fully local) — skipped")
            continue
        dec = bytearray(raw)
        tk5psp_crypt.decrypt_sector_data_fast(dec, seed, len(dec))
        dec = bytes(dec)
        nrec = z // REC
        bad = 0
        types = {}
        for r in range(nrec):
            h = struct.unpack_from("<8I", dec, r * REC)
            if not pat_ok(h):
                bad += 1
            types[h[0]] = types.get(h[0], 0) + 1
        ws = word_sum(dec)
        zero = dec.count(0) / len(dec)
        pr = sum(1 for b in dec if 32 <= b < 127) / len(dec)
        hits = {}
        for m in MAGICS:
            c = dec.count(m)
            if c:
                hits[m.decode("latin1")] = c
        m1m = sum(1 for off in range(0, len(dec) - 4, 4)
                  if struct.unpack_from("<I", dec, off)[0] == 1000000)
        print(f"entry {ei}: size={z} seed={seed} recs={nrec} bad_hdr={bad} "
              f"types={types} ws={ws:#010x} ck={CK[ei]:#010x} ws_match={ws == CK[ei]} "
              f"zero={zero:.3f} print={pr:.3f} magics={hits} u32_1M={m1m}")
        if ei in (1, 3):
            open(f"/tmp/tk5data0_e{ei}_dec.bin", "wb").write(dec)
            print(f"    saved /tmp/tk5data0_e{ei}_dec.bin")
