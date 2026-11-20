#!/usr/bin/env python3
"""JOB 1 probe 3: sector-header census, NLZ1-at-header-offsets, seed sweep
decrypt-then-unpack on TK5DATA0 sector 0, filename-table dump, TK5DATA0-only
LUT-run check. Read-only on big files.
"""
import struct, sys
sys.path.insert(0, "tools-Tekken5_Tools")
import decNLZ1
import tk5psp_crypt

with open("../raw/TK5DATA0.BIN", "rb") as f:
    d = f.read(262144)  # first 256 KiB local

HDR = bytes.fromhex("0100000008000000")
print("== sector-header census (128 sectors in first 256KiB) ==")
match = []
for s in range(128):
    if d[s * 2048:s * 2048 + 8] == HDR:
        match.append(s)
print(f"sectors starting with 01 00 00 00 08 00 00 00: {match}")
for s in match[:6]:
    print(f"  sector {s} (@{s*2048:#x}) first 32B: {d[s*2048:s*2048+32].hex()}")
    print(f"    as u32: {[hex(struct.unpack('<I', d[s*2048+4*i:s*2048+4*i+4])[0]) for i in range(8)]}")

print("\n== NLZ1 unpack at header offsets (sectors 0 and 9) ==")
for s in [0, 9]:
    for off in [8, 12, 16, 20, 24, 32, 64, 128]:
        try:
            out = decNLZ1.unpack_sc3game(d[s * 2048 + off:s * 2048 + 2048])
            print(f"  sector {s} +{off}: out_len={len(out)} head={bytes(out[:16]).hex()}")
        except Exception as e:
            print(f"  sector {s} +{off}: FAIL {str(e)[:60]}")

print("\n== seed sweep: decrypt sector 0 then NLZ1-unpack (seeds 0..50000) ==")
sec0 = bytes(d[:2048])
best = []
for seed in range(50001):
    buf = bytearray(sec0)
    tk5psp_crypt.decrypt_sector_data_fast(buf, seed, 2048)
    try:
        out = decNLZ1.unpack_sc3game(bytes(buf))
        if len(out) > 100:
            best.append((seed, len(out), bytes(out[:16]).hex()))
            print(f"  CANDIDATE seed={seed} out_len={len(out)} head={bytes(out[:16]).hex()}")
    except Exception:
        pass
print(f"sweep done: {len(best)} candidates with out_len>100")

print("\n== code filename table around TK5DATA1/0 strings ==")
CODE = open("/tmp/dec_code.bin", "rb").read()
seg = CODE[2602300:2602500]
print(repr(seg))
print("hex:", seg.hex())

print("\n== LUT runs with max sector > 633539 (TK5DATA0-only candidates) ==")
FS = 2072586240
found = 0
off = 0
n = len(CODE)
while off + 16 <= n:
    s0, z0 = struct.unpack_from("<II", CODE, off)
    s1, z1 = struct.unpack_from("<II", CODE, off + 8)
    if (0 <= s0 < 1011937 and 0 < z0 <= 300_000_000
            and 0 <= s1 < 1011937 and 0 < z1 <= 300_000_000 and s1 > s0):
        run = [(s0, z0), (s1, z1)]
        p = off + 16
        while p + 8 <= n:
            s, z = struct.unpack_from("<II", CODE, p)
            if 0 <= s < 1011937 and 0 < z <= 300_000_000 and s > run[-1][0]:
                run.append((s, z)); p += 8
            else:
                break
        if len(run) >= 6 and run[-1][0] > 633539:
            print(f"  len={len(run)} code_off={off:#x} first={run[0]} last={run[-1]}")
            found += 1
    off += 4
print(f"TK5DATA0-only runs: {found}")
