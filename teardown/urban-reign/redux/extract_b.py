#!/usr/bin/env python3
"""Lane 2 extraction step B: rebuild the DVD000/DVD001 AFS tables from the core
.urmod parts (author's own layout: Source/vendor/mod-manager/urrlayout.py afs()),
resolve every fighter's model/package entry, and extract the fully-covered ones.

Reads ONLY:
- ~/workspace/urban-reign-redux/extracted/core/manifest.json (urr-base-1)
- ~/workspace/urban-reign-redux/extracted/core/parts/data/*.bin (sha-verified parts)
- ~/workspace/urban-reign-redux/extracted/core/coverage.json (merged intervals)

Writes:
- extracted/core/dvd000_table.json, dvd001_table.json (index, name, offset, size, coverage)
- extracted/fighters/<Name>/model.vmd, package.ppk (+ .sha256 sidecars) where 100% covered
- extracted/core/fighter_entries.json (per-fighter entry resolution + coverage)
"""
import bisect, hashlib, json, struct, sys
from pathlib import Path

ROOT = Path.home() / "workspace" / "urban-reign-redux"
CORE = ROOT / "extracted" / "core"
H = lambda b: hashlib.sha256(b).hexdigest()

manifest = json.loads((CORE / "manifest.json").read_text())
layout = manifest["layout"]
merged = [tuple(x) for x in json.loads((CORE / "coverage.json").read_text())["merged_intervals"]]
starts = [a for a, _ in merged]

PARTS = CORE / "parts"
# part index: output offset -> (length, file)
parts = []
for p in manifest["parts"]:
    parts.append((p["offset"], p["length"], PARTS / Path(p["entry"]).name))
parts.sort()
poff = [p[0] for p in parts]


def read_range(a, b):
    """Read output-disc bytes [a,b) from parts; returns (bytes, covered_frac, gaps)."""
    n = b - a
    buf = bytearray(n)
    got = 0
    gaps = []
    i = bisect.bisect_right(poff, a) - 1
    if i < 0:
        i = 0
    cur = a
    while i < len(parts) and parts[i][0] < b:
        pa, pl, pf = parts[i]
        lo, hi = max(pa, a), min(pa + pl, b)
        if lo < hi:
            if lo > cur:
                gaps.append((cur, lo))
            data = pf.read_bytes()
            buf[lo - a:hi - a] = data[lo - pa:hi - pa]
            got += hi - lo
            cur = max(cur, hi)
        i += 1
    if cur < b:
        gaps.append((cur, b))
    return bytes(buf), (got / n if n else 1.0), gaps


def afs_table(arch):
    L = layout[arch]
    base = L["offset"]
    head_len = 8 + 8 * L["count"] + 8
    head, cov, gaps = read_range(base, base + head_len)
    assert cov == 1.0, f"{arch} header not fully covered: {cov}"
    magic, count = struct.unpack_from("<4sI", head, 0)
    assert magic == b"AFS\0", f"{arch} bad magic {magic}"
    assert count == L["count"], f"{arch} count {count} != {L['count']}"
    names_at, names_size = struct.unpack_from("<II", head, 8 + 8 * count)
    assert names_at == L["names_at"] and names_size == L["names_size"]
    entries = [struct.unpack_from("<II", head, 8 + 8 * i) for i in range(count)]
    nb, ncov, _ = read_range(base + names_at, base + names_at + names_size)
    assert ncov == 1.0, f"{arch} names not fully covered: {ncov}"
    names = [nb[48 * i:48 * i + 44].split(b"\0")[0].decode("latin1") for i in range(count)]
    # per-entry coverage
    rows = []
    for i, ((off, size), name) in enumerate(zip(entries, names)):
        if size == 0:
            rows.append(dict(index=i, name=name, offset=off, size=0, coverage=1.0))
            continue
        _, c, _ = read_range(base + off, base + off + size)
        rows.append(dict(index=i, name=name, offset=off, size=size, coverage=c))
    return rows


def extract_entry(arch, row, dest):
    L = layout[arch]
    base = L["offset"]
    data, cov, gaps = read_range(base + row["offset"], base + row["offset"] + row["size"])
    if cov < 1.0:
        return None, cov, gaps
    dest.write_bytes(data)
    (dest.parent / (dest.name + ".sha256")).write_text(H(data) + f"  {dest.name}\n")
    return data, cov, gaps


def main():
    out_tables = {}
    for arch in ("DVD000", "DVD001"):
        rows = afs_table(arch)
        out_tables[arch] = rows
        json.dump(rows, open(CORE / f"{arch.lower()}_table.json", "w"), indent=1)
        nz = [r for r in rows if r["size"] > 0]
        full = [r for r in nz if r["coverage"] == 1.0]
        part = [r for r in nz if 0 < r["coverage"] < 1.0]
        zero = [r for r in nz if r["coverage"] == 0.0]
        print(f"{arch}: {len(rows)} entries, {len(nz)} non-empty; fully covered by parts: {len(full)}, "
              f"partial: {len(part)}, zero: {len(zero)}")
    # name lookup
    d0 = out_tables["DVD000"]
    by_name = {r["name"]: r for r in d0}
    # show naming pattern around fighter packages
    print("\nSample DVD000 names:")
    for r in d0[:6]:
        print("  ", r["index"], r["name"], r["size"])
    hits = [r for r in d0 if "char" in r["name"].lower() and r["name"].endswith(".ppk")]
    print(f"\ncharNNN.ppk entries: {len(hits)}")
    for r in hits[:12]:
        print("  ", r["index"], r["name"], r["size"], f"cov={r['coverage']:.3f}")
    # model naming: look for .vmd entries
    vmds = [r for r in d0 if r["name"].lower().endswith(".vmd")]
    print(f"\n.vmd entries: {len(vmds)}")
    for r in vmds[:12]:
        print("  ", r["index"], r["name"], r["size"], f"cov={r['coverage']:.3f}")
    json.dump({"by_name_sample": "see tables"}, open(CORE / "step_b_note.json", "w"))


if __name__ == "__main__":
    main()
