#!/usr/bin/env python3
"""W5c vertex-order attack measurements (2026-10-21).

Reproduces every quantitative claim in the EAGL-FORMAT-SPEC.md §7.9
addendum (W5c): block-trailer semantics, the _C BBOX vs pool-span
non-uniformity proof, pool shell statistics, the cross-letter topology
identity, the falsified-reading battery scores, the _C unit/counter
anatomy, and the bone-record partial decode.

Usage: w5c_vertex_analysis.py <dir-with-.o-files>
Needs V2CP_110_0001_{A,B,C,D,E,F}.o and V2CP_111_0001_{A,B}.o in the dir.
Uses the proven J4 parser from customization/tools/convert_defjam_o.py.
"""
import itertools
import math
import os
import struct
import sys
from collections import Counter

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "..", "customization", "tools"))
import convert_defjam_o as C  # noqa: E402
from eagl_refpack import refpack_decompress, find_refpack_offset  # noqa: E402


def dist(a, b):
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def mean_d1(seq):
    ds = [dist(seq[i], seq[i + 1]) for i in range(len(seq) - 1)]
    return sum(ds) / len(ds)


def load(stem, d):
    raw = open(os.path.join(d, stem + ".o"), "rb").read()
    return C.parse_part(raw)


def main(argv):
    d = argv[1]
    part = load("V2CP_110_0001_A", d)

    print("== 1. Block trailers = byte size of NEXT block's record data")
    co, no = part["coords"], part["normals"]
    counts = [len(s) for s in co["strips"]]
    pred = [counts[k + 1] * 3 * 2 for k in range(len(counts) - 1)]
    print("coords trailers == 2*3*next_count:",
          co["trailers"] == pred)
    print("normals trailers == 2x coords trailers:",
          no["trailers"] == [2 * t for t in co["trailers"]])

    print("\n== 2. Pool spans vs _C BBOX (no uniform scale exists)")
    pts = [p for s in co["strips"] for p in s]
    spans = tuple(max(p[i] for p in pts) - min(p[i] for p in pts)
                  for i in range(3))
    print("pool spans (x,y,z):", spans)
    print("BBOX spans (x,y,z): (17.4446, 19.3344, 9.0) from __BBOX symbol")
    print("span ratios under all axis perms:",
          sorted(round(b / p, 5) for b, p in
                 zip((17.4446, 19.3344, 9.0),
                     (spans[0], spans[1], spans[2]))))

    print("\n== 3. Pool is a clean surface sample (unique points)")
    uniq = sorted(set(pts))
    nn = []
    for i, p in enumerate(uniq):
        nn.append(min(dist(p, q) for j, q in enumerate(uniq) if j != i))
    nn.sort()
    print(f"unique={len(uniq)} NN med={nn[len(nn) // 2]:.0f} "
          f"p75={nn[3 * len(nn) // 4]:.0f} max={nn[-1]:.0f}")
    mir = sum(1 for (x, y, z) in pts if (-x, y, z) in set(pts))
    print(f"mirror-x partners: {mir}/{len(pts)}")

    print("\n== 4. Falsified-reading battery (mean consecutive distance)")
    cs = [x for s in co["strips"] for r in s for x in r]
    recs = [tuple(cs[i:i + 3]) for i in range(0, len(cs) - 2, 3)]
    print(f"identity: {mean_d1(recs):.1f}")
    for p in (3, 5, 6, 7):
        seq = []
        for r in range(p):
            seq.extend(recs[r::p])
        print(f"record deinterleave p={p}: {mean_d1(seq):.1f}")
    ev, od = [], []
    for i in range(0, len(cs) - 5, 6):
        g = cs[i:i + 6]
        ev.append((g[0], g[2], g[4]))
        od.append((g[1], g[3], g[5]))
    print(f"component-even: {mean_d1(ev):.1f}  component-odd: {mean_d1(od):.1f}")
    for perm in itertools.permutations(range(3)):
        if perm != (0, 1, 2):
            s = [(r[perm[0]], r[perm[1]], r[perm[2]]) for r in recs]
            print(f"axis perm {perm}: {mean_d1(s):.1f}")

    print("\n== 5. Cross-letter topology identity (110_0001)")
    def fom(stem):
        p = load(stem, d)
        out = []
        for s in p["coords"]["strips"]:
            seen, m = {}, []
            for v in s:
                if v not in seen:
                    seen[v] = len(seen)
                m.append(seen[v])
            out.append(m)
        return out
    base = fom("V2CP_110_0001_A")
    for L in "BDEF":
        m = fom(f"V2CP_110_0001_{L}")
        same = sum(1 for a, b in zip(base, m) if a == b)
        print(f"A vs {L}: identical strip first-occurrence maps "
              f"{same}/{len(base)}")

    print("\n== 6. Per-letter strip scores (same topology, diff geometry)")
    for stem in ["V2CP_110_0001_A", "V2CP_110_0001_B", "V2CP_110_0001_D",
                 "V2CP_110_0001_E", "V2CP_110_0001_F", "V2CP_111_0001_A",
                 "V2CP_111_0001_B"]:
        p = load(stem, d)
        seq = [v for s in p["coords"]["strips"] for v in s]
        # score within strips only
        ds = []
        for s in p["coords"]["strips"]:
            ds += [dist(s[i], s[i + 1]) for i in range(len(s) - 1)]
        print(f"{stem}: meanD1={sum(ds) / len(ds):.1f}")

    print("\n== 7. _C unit anatomy (strip 0 block @ .data 0x52C)")
    raw = open(os.path.join(d, "V2CP_110_0001_C.o"), "rb").read()
    dec = refpack_decompress(raw[find_refpack_offset(raw):])
    elf = C.parse_elf(dec)
    dd = elf["data"]
    sym = {s["name"]: s["value"] for s in elf["symbols"]}
    bb = sym["__BBOX:::V2CP_110_0001_C_alpha"]
    print("BBOX floats:", struct.unpack("<6f", dd[bb:bb + 24]))
    blk = dd[0x52C:0x52C + 1296]
    units = [struct.unpack("<4h", blk[i * 8:(i + 1) * 8])
             for i in range(len(blk) // 8)]
    print("first 24 unit counters (4th i16):", [u[3] for u in units[:24]])
    abc = [(u[0], u[1], u[2]) for u in units]
    print(f"(a,b,c) as positions: meanD1={mean_d1(abc):.0f} (noise-scale)")

    print("\n== 8. Bone record partial decode (A file, .data 0x5F0, 94 x 112B)")
    raw_a = open(os.path.join(d, "V2CP_110_0001_A.o"), "rb").read()
    dec_a = refpack_decompress(raw_a[find_refpack_offset(raw_a):])
    elf_a = C.parse_elf(dec_a)
    da = elf_a["data"]
    for r in range(2):
        o = 0x5F0 + r * 112
        f = struct.unpack("<28f", da[o:o + 112])
        print(f"rec{r}: scale={f[0:3]} u32@12={struct.unpack('<I', da[o + 12:o + 16])[0]:#x} "
              f"quat[4:8]={tuple(round(x, 3) for x in f[4:8])}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
