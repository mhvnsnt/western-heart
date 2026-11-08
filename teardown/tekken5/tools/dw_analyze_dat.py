#!/usr/bin/env python3
"""Analyse extracted romD .dat files: headers, magics, entropy, sizes.

Usage: dw_analyze_dat.py <extracted_dir> [--index dw-motion-index.json]
Prints a per-file table (size, first-16-bytes hex, ascii, known magic,
entropy) and a summary of magic hits + size stats per group. Read-only.
"""
import argparse
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

KNOWN_MAGICS = {
    b"NUDP": "NUDP model container",
    b"TIM2": "TIM2 texture",
    b"MIF\x00": "MIF bone data?",
    b"MIF": "MIF bone data?",
    b"\x7fELF": "ELF",
    b"VAGp": "VAGp audio",
    b"pDAT": "pDAT container",
    b"IECS": "IECS container",
}


def entropy(data):
    if not data:
        return 0.0
    c = Counter(data)
    n = len(data)
    return -sum((v / n) * math.log2(v / n) for v in c.values())


def magic_of(head):
    for m, name in KNOWN_MAGICS.items():
        if head.startswith(m):
            return name
    return ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dir")
    ap.add_argument("--index")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    d = Path(args.dir)
    files = sorted(p for p in d.iterdir() if p.is_file() and p.suffix == ".dat")
    print(f"{len(files)} .dat files in {d}")
    groups = {}
    if args.index:
        idx = json.loads(Path(args.index).read_text())
        for g in idx["groups"]:
            for f in g["files"]:
                groups[f["name"]] = (g["id"], f.get("gloss", ""), f.get("confidence", ""))

    magic_hits = Counter()
    size_by_group = defaultdict(list)
    rows = []
    for p in files:
        data = p.read_bytes()
        head = data[:16]
        mg = magic_of(data[:8])
        magic_hits[mg or "(none)"] += 1
        gid = groups.get(p.name, ("?", "", ""))[0]
        size_by_group[gid].append(len(data))
        rows.append((p.name, len(data), head.hex(), "".join(
            chr(b) if 32 <= b < 127 else "." for b in head),
            mg, round(entropy(data[:65536]), 2),
            groups.get(p.name, ("?", "", ""))[1][:40]))
    n = len(rows) if not args.limit else min(args.limit, len(rows))
    print(f"{'name':32s} {'size':>8s} {'head16 hex':34s} {'ascii':18s} {'magic':22s} {'ent':>5s}  gloss")
    for r in rows[:n]:
        print(f"{r[0]:32s} {r[1]:8d} {r[2]:34s} {r[3]:18s} {r[4]:22s} {r[5]:5.2f}  {r[6]}")
    print("\nmagic hits:", dict(magic_hits))
    print("\nsize stats per group (count, min, median, max, total):")
    for gid, sizes in sorted(size_by_group.items()):
        sizes = sorted(sizes)
        med = sizes[len(sizes) // 2]
        print(f"  {gid:10s} n={len(sizes):3d} min={sizes[0]:7d} "
              f"med={med:7d} max={sizes[-1]:7d} total={sum(sizes)}")
    total = sum(r[1] for r in rows)
    print(f"\ntotal extracted bytes: {total}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
