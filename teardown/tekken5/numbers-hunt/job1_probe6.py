#!/usr/bin/env python3
"""JOB 1 probe 6: TK5DATA0 record structure. Records are 18432 bytes
(9 sectors); header 32B = [1, 8, 17451, 218, X, 5468, 27855, 136974]
with X varying per record. Tests: (a) is X a word-sum checksum of the
record? (b) is X the LCG seed for the record payload?
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

with open("../raw/TK5DATA0.BIN", "rb") as f:
    d = f.read(262144)

REC = 18432
for r in [0, 1, 4]:  # records at sectors 0, 9, 36
    base = r * REC
    hdr = d[base:base + 32]
    vals = struct.unpack("<8I", hdr)
    print(f"record {r} (@{base:#x}) header u32s: {[hex(v) for v in vals]}")
    X = vals[4]
    # (a) checksum hypotheses
    cands = {
        "payload[32:REC]": word_sum(d[base + 32:base + REC]),
        "whole-rec-minus-X": word_sum(d[base:base + 16] + b"\0\0\0\0" + d[base + 20:base + REC]),
        "whole-record": word_sum(d[base:base + REC]),
        "payload[16:REC]": word_sum(d[base + 16:base + REC]),
    }
    for k, v in cands.items():
        print(f"    X={X:#010x} vs word_sum({k})={v:#010x} match={v == X}")
    # (b) seed hypothesis: decrypt whole record from offset 0 with seed X
    buf = bytearray(d[base:base + REC])
    tk5psp_crypt.decrypt_sector_data_fast(buf, X, REC)
    print(f"    decrypt(seed=X) payload[32:96]: {bytes(buf[32:96]).hex()}")
    print(f"    decrypt(seed=X) payload head as u32: {[hex(v) for v in struct.unpack('<8I', bytes(buf[32:64]))]}")
    for m in [b"TK5RESU1", b"TIM2", b"GYM1", b"BDPK", b"NUDP", b"COM "]:
        i = bytes(buf).find(m)
        if i != -1:
            print(f"    magic {m} at {i}")
    try:
        out = decNLZ1.unpack_sc3game(bytes(buf[32:]))
        print(f"    NLZ1(payload) out_len={len(out)} head={bytes(out[:16]).hex()}")
    except Exception as e:
        print(f"    NLZ1(payload) FAIL {str(e)[:50]}")
