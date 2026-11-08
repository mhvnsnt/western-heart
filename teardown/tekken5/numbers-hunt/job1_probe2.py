#!/usr/bin/env python3
"""JOB 1 probe 2: TK5DATA0 head structure + systematic TK5DATA0-LUT hunt
in the decompressed code (/tmp/dec_code.bin). Read-only on big files.
"""
import struct

CODE = open("/tmp/dec_code.bin", "rb").read()
print(f"code len={len(CODE)}")

# --- A. filename strings in code (positive control: TK5DATA1 must appear) ---
for name in [b"TK5DATA0", b"TK5DATA1", b"TK5DATA2", b"TK5DATA3", b"TK5DATA4",
             b"TK5DATA", b"DATA0", b"romD", b"romd"]:
    offs = []
    i = CODE.find(name)
    while i != -1:
        offs.append(i)
        i = CODE.find(name, i + 1)
    print(f"  {name}: {offs[:10]}{'...' if len(offs) > 10 else ''} (n={len(offs)})")

# --- B. TK5DATA0 head hexdump ---
with open("../raw/TK5DATA0.BIN", "rb") as f:
    head = f.read(512)
print("\nTK5DATA0[0:512] as u32 LE:")
for i in range(0, 128, 8):
    print("  " + " ".join(f"{struct.unpack('<I', head[j:j+4])[0]:#010x}" for j in range(i * 4, (i + 8) * 4, 4)))
print("TK5DATA0[0:64] hex:", head[:64].hex())
# entropy-ish: printable + zero fraction per 2KB block, first 256KB
with open("../raw/TK5DATA0.BIN", "rb") as f:
    d = f.read(262144)
print("per-2KB printable/zero fractions, first 32KB:")
for off in range(0, 32768, 2048):
    blk = d[off:off + 2048]
    pr = sum(1 for b in blk if 32 <= b < 127) / len(blk)
    ze = sum(1 for b in blk if b == 0) / len(blk)
    print(f"  @{off:#06x} printable={pr:.3f} zero={ze:.3f} head={blk[:8].hex()}")

# --- C. systematic TK5DATA0 LUT hunt in code ---
# A LUT entry is (sector u32, size u32); sector*2048 is the file offset.
# TK5DATA0 size = 2072586240 -> max sector = 1011936.
# Filter: run of >=6 consecutive pairs, sectors strictly increasing,
# sizes in (0, 300_000_000], sector*2048 < filesize, and the run's
# covered span (last sector*2048 + last size) - first sector*2048
# is a large fraction of the file, OR the sizes sum to ~filesize.
FS = 2072586240
print("\nLUT hunt: scanning code for runs of (sector,size) pairs ...")
best = []
n = len(CODE)
i = 0
# scan 4-byte aligned offsets
import sys
count_checked = 0
off = 0
while off + 16 <= n:
    s0, z0 = struct.unpack_from("<II", CODE, off)
    s1, z1 = struct.unpack_from("<II", CODE, off + 8)
    # quick pair filter
    if (0 <= s0 < 1011937 and 0 < z0 <= 300_000_000
            and 0 <= s1 < 1011937 and 0 < z1 <= 300_000_000
            and s1 > s0):
        # extend run
        run = [(s0, z0), (s1, z1)]
        p = off + 16
        while p + 8 <= n:
            s, z = struct.unpack_from("<II", CODE, p)
            if 0 <= s < 1011937 and 0 < z <= 300_000_000 and s > run[-1][0]:
                run.append((s, z))
                p += 8
            else:
                break
        if len(run) >= 6:
            span = run[-1][0] * 2048 + run[-1][1] - run[0][0] * 2048
            total = sum(z for _, z in run)
            best.append((len(run), off, run[0], run[-1], span, total))
    off += 4
print(f"  runs >=6 pairs: {len(best)}")
for r in sorted(best, key=lambda x: -x[0])[:15]:
    print(f"  len={r[0]} code_off={r[1]:#x} first={r[2]} last={r[3]} span={r[4]} sumsize={r[5]}")
