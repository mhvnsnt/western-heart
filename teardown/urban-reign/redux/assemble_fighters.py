#!/usr/bin/env python3
"""Assemble the 50 still-missing Redux fighter files directly from the
author's .urmod parts + the verified source ISO — WITHOUT building the full
4.6 GB output disc (the quota died on that write; this needs only ~70 MB).

Per file (model VMD / package PPK, output-disc offset from dvd000_table.json):
- covered ranges: read from the SHA-verified part files (extract_a.py, 0 bad)
- gap ranges: read from the source ISO via the manifest's copies.
  CORRECTION (measured this lane, 2026-11-08): the manifest stores copies
  as [output_offset, source_offset, length] — NOT [src, dst, length] as
  extract_a.py's docstring says. Proof: with [dst, src, len], parts+copies
  tile the output disc exactly (merged coverage 4,606,052,352 B, 0 holes,
  0 overlap, 1 interval; max copy src+len 4,140,806,144 stays inside the
  source ISO). With the docstring's order, 5,841 copies read past the end
  of the source ISO and 409,282,560 B of holes appear. A copy therefore
  means: output[dst:dst+len] = source ISO bytes [src:src+len].
- every gap byte must be covered by a copy record; a file with an uncovered
  gap is NOT written (no invented bytes, ever)

Inputs (all author-verified):
- extracted/core/manifest.json (parts + copies)
- extracted/core/parts/*.bin (3,639 parts, SHA-verified)
- iso/urban-reign-usa.iso (SHA-256 c22209ee... verified this lane)
- extracted/core/fighter_entries.json (per-file gaps, file-relative)
- extracted/core/dvd000_table.json (index -> output-disc offset/size)

Outputs:
- extracted/fighters/<Name>/{model.vmd,package.ppk} + .sha256 sidecars
- extracted/core/fighter_entries.json updated (extracted: "model.vmd" /
  "package.ppk" where completed)
- extracted/fighters/REDUX-0.5-COMPLETION-MANIFEST.json (per-file bytes + SHA-256)

Verification available per file: parts SHA-verified individually, the source
ISO SHA-verified as a whole. The author's SHA256SUMS.json does NOT contain
fighter VMD/PPK entries (70 entries: Launcher.exe + config PNGs only), so
there is no per-file author hash to compare against — the proof chain is
parts-SHA + ISO-SHA + copy-map. Do not claim otherwise. (The full output-disc
SHA check remains owed for end-to-end proof; it needs a 4.6 GB write the
quota would not hold — see build_output_disc.py.)
"""
import bisect
import hashlib
import json
from pathlib import Path

ROOT = Path.home() / "workspace" / "urban-reign-redux"
CORE = ROOT / "extracted" / "core"
ISO = ROOT / "iso" / "urban-reign-usa.iso"
H = lambda b: hashlib.sha256(b).hexdigest()


def main():
    manifest = json.loads((CORE / "manifest.json").read_text())
    entries = json.loads((CORE / "fighter_entries.json").read_text())
    d0 = json.load(open(CORE / "dvd000_table.json"))
    by_idx = {r["index"]: r for r in d0}
    # Table offsets are AFS-relative; output-disc offset = DVD000 layout
    # offset + table offset (extract_c.py read_entry_bytes / gaps_for).
    dvd000_base = manifest["layout"]["DVD000"]["offset"]

    parts = sorted((p["offset"], p["length"], CORE / "parts" / Path(p["entry"]).name)
                   for p in manifest["parts"])
    poff = [p[0] for p in parts]
    copies = sorted((c[0], c[0] + c[2], c[1]) for c in manifest["copies"])  # (out_off, out_off+n, src_off)
    coff = [c[0] for c in copies]

    part_cache = {}

    def part_bytes(pf):
        if pf not in part_cache:
            part_cache[pf] = pf.read_bytes()
        return part_cache[pf]

    def read_parts(a, b):
        """Output-disc bytes [a,b) from parts; returns (buf, gaps list of (start,len) absolute)."""
        n = b - a
        buf = bytearray(n)
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
                    gaps.append((cur, lo - cur))
                data = part_bytes(pf)
                buf[lo - a:hi - a] = data[lo - pa:hi - pa]
                cur = max(cur, hi)
            i += 1
        if cur < b:
            gaps.append((cur, b - cur))
        return buf, gaps

    def fill_gap_from_iso(f, a, n):
        """Read n bytes at output-disc offset a from the source ISO via copies."""
        out = bytearray()
        cur = a
        end = a + n
        i = bisect.bisect_right(coff, cur) - 1
        if i < 0:
            i = 0
        while cur < end:
            if i >= len(copies) or copies[i][0] > cur:
                return None  # uncovered gap byte
            d0_, d1_, s0 = copies[i]
            lo = max(cur, d0_)
            hi = min(end, d1_)
            if lo < hi:
                f.seek(s0 + (lo - d0_))
                out += f.read(hi - lo)
                cur = hi
            i += 1
        return bytes(out)

    # --- pre-pass: every gap of every missing file must be copy-covered ---
    todo = []
    for name in sorted(entries):
        e = entries[name]
        for kind in ("model", "package"):
            f = e[kind]
            if f.get("extracted"):
                continue
            todo.append((name, kind, f))
    print(f"files to complete: {len(todo)} (target 50)")
    with open(ISO, "rb") as isof:
        uncovered = []
        for name, kind, f in todo:
            table = by_idx[f["index"]]
            assert table["size"] == f["size"], f"{name}/{kind} size mismatch"
            base = dvd000_base + table["offset"]
            for gs, gl in f["gaps"]:
                if fill_gap_from_iso(isof, base + gs, gl) is None:
                    uncovered.append((name, kind, gs, gl))
        print(f"uncovered gap ranges: {len(uncovered)}")
        if uncovered:
            for u in uncovered:
                print("  UNCOVERED:", u)
            raise SystemExit("some gaps have no copy record — STOP, nothing written")

        # --- assemble + write ---
        done = []
        for name, kind, f in todo:
            table = by_idx[f["index"]]
            base, size = dvd000_base + table["offset"], f["size"]
            buf, gaps = read_parts(base, base + size)
            # gaps from read_parts must match the recorded file-relative gaps
            rec = [(gs, gl) for gs, gl in f["gaps"]]
            got = [(a - base, n) for a, n in gaps]
            assert got == rec, f"{name}/{kind}: gap mismatch {got} vs {rec}"
            for (a, n) in gaps:
                chunk = fill_gap_from_iso(isof, a, n)
                assert chunk is not None and len(chunk) == n
                buf[a - base:a - base + n] = chunk
            data = bytes(buf)
            assert len(data) == size
            dest_dir = ROOT / "extracted" / "fighters" / name
            dest_dir.mkdir(parents=True, exist_ok=True)
            fname = "model.vmd" if kind == "model" else "package.ppk"
            dest = dest_dir / fname
            dest.write_bytes(data)
            (dest_dir / (fname + ".sha256")).write_text(H(data) + "\n")
            f["extracted"] = fname
            done.append({"fighter": name, "kind": kind, "file": fname,
                         "bytes": len(data), "sha256": H(data),
                         "dvd000_index": f["index"], "source_name": f["name"]})
            print(f"  {name}/{kind}: {len(data)} B sha256={H(data)[:16]}…", flush=True)
    (CORE / "fighter_entries.json").write_text(json.dumps(entries, indent=1))
    (ROOT / "extracted" / "fighters" / "REDUX-0.5-COMPLETION-MANIFEST.json").write_text(
        json.dumps({"files": done, "count": len(done),
                    "proof": "parts SHA-verified + source ISO SHA-256 verified + "
                             "gaps filled only via manifest copy records; "
                             "no per-file author hash exists in SHA256SUMS.json"},
                   indent=1))
    print(f"completed files: {len(done)} (target 50)")


if __name__ == "__main__":
    main()
