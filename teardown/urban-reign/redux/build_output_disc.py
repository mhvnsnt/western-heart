#!/usr/bin/env python3
"""Build the Redux 0.5 output disc from the author's own .urmod diff + the
verified source ISO, then slice out the 50 still-missing fighter files.

This is NOT the Windows Launcher build (no Wine, no Launcher.exe): it applies
the author's published urr-base-1 diff format (manifest parts + copies) with
plain Python. The output disc it produces is checked byte-for-byte against
the author's own output_sha256 in the manifest.

Inputs (all author-verified):
- extracted/core/manifest.json (parts + copies + output_sha256)
- extracted/core/parts/*.bin (3,639 parts, SHA-verified by extract_a.py)
- iso/urban-reign-usa.iso (source ISO, SHA-256 c22209ee... verified this lane)

Outputs:
- iso/urban-reign-redux-0.5.iso (4,606,052,352 B, SHA-256 must equal
  cc2312c1909cec438b8971133445eb7e2bfc7eecf03bdd0fed01cbefd7134541)
- extracted/fighters/<Name>/{model.vmd,package.ppk} + .sha256 sidecars
  for the 50 files whose gaps are filled from the source ISO
- extracted/core/fighter_entries.json updated (extracted: "model.vmd" /
  "package.ppk" where completed)
- extracted/fighters/REDUX-0.5-COMPLETION-MANIFEST.json (per-file bytes + SHA-256)

Verification available per file: parts are SHA-verified individually, the
source ISO is SHA-verified as a whole, and the built output disc is
SHA-verified as a whole. The author's SHA256SUMS.json does NOT contain
fighter VMD/PPK entries (70 entries: Launcher.exe + config PNGs only), so
there is no per-file author hash to compare against — the end-to-end
output-disc SHA is the proof. Do not claim otherwise.
"""
import hashlib
import json
from pathlib import Path

ROOT = Path.home() / "workspace" / "urban-reign-redux"
CORE = ROOT / "extracted" / "core"
ISO = ROOT / "iso" / "urban-reign-usa.iso"
OUT = ROOT / "iso" / "urban-reign-redux-0.5.iso"
H = lambda b: hashlib.sha256(b).hexdigest()
CHUNK = 1 << 22


def main():
    manifest = json.loads((CORE / "manifest.json").read_text())
    parts = manifest["parts"]
    copies = manifest["copies"]
    out_size = manifest["output_size"]
    out_sha = manifest["output_sha256"]
    print(f"parts={len(parts)} copies={len(copies)} output_size={out_size}")

    # --- build the output disc ---
    with open(ISO, "rb") as src, open(OUT, "wb") as dst:
        dst.truncate(out_size)
        # parts first (author bytes for the output disc)
        for i, p in enumerate(parts):
            data = (CORE / "parts" / Path(p["entry"]).name).read_bytes()
            assert len(data) == p["length"] and H(data) == p["sha256"], \
                f"BAD PART {p['entry']}"
            dst.seek(p["offset"])
            dst.write(data)
            if i % 1000 == 0:
                print(f"  parts {i}/{len(parts)}", flush=True)
        print("parts written, all SHA-verified")
        # copies: verbatim ranges from the source ISO.
        # CORRECTION: manifest copies are [output_offset, source_offset,
        # length] (see assemble_fighters.py — the docstring order is wrong).
        for i, (d, s, n) in enumerate(copies):
            src.seek(s)
            dst.seek(d)
            remaining = n
            while remaining > 0:
                chunk = src.read(min(remaining, CHUNK))
                if not chunk:
                    raise IOError(f"short read at ISO offset {s}")
                dst.write(chunk)
                remaining -= len(chunk)
            if i % 2000 == 0:
                print(f"  copies {i}/{len(copies)}", flush=True)
        print("copies written")
        dst.flush()

    # --- verify the built disc ---
    h = hashlib.sha256()
    with open(OUT, "rb") as f:
        while True:
            b = f.read(CHUNK)
            if not b:
                break
            h.update(b)
    got = h.hexdigest()
    print(f"output size: {OUT.stat().st_size} (target {out_size})")
    print(f"output sha256: {got}")
    print(f"target sha256: {out_sha}")
    print("OUTPUT DISC MATCH:", got == out_sha)
    if got != out_sha:
        raise SystemExit("output disc SHA mismatch — STOP, do not extract files")

    # --- slice the 50 fighter files out of the verified disc ---
    entries = json.loads((CORE / "fighter_entries.json").read_text())
    d0 = json.load(open(CORE / "dvd000_table.json"))
    by_idx = {r["index"]: r for r in d0}
    done = []
    with open(OUT, "rb") as disc:
        for name in sorted(entries):
            e = entries[name]
            for kind in ("model", "package"):
                f = e[kind]
                if f.get("extracted"):
                    continue
                table = by_idx[f["index"]]
                assert table["size"] == f["size"], \
                    f"{name}/{kind}: table size {table['size']} vs entry {f['size']}"
                disc.seek(table["offset"])
                data = disc.read(f["size"])
                assert len(data) == f["size"]
                dest_dir = ROOT / "extracted" / "fighters" / name
                dest_dir.mkdir(parents=True, exist_ok=True)
                fname = "model.vmd" if kind == "model" else "package.ppk"
                dest = dest_dir / fname
                dest.write_bytes(data)
                (dest_dir / (fname + ".sha256")).write_text(H(data) + "\n")
                f["extracted"] = fname
                done.append({
                    "fighter": name, "kind": kind, "file": fname,
                    "bytes": len(data), "sha256": H(data),
                    "dvd000_index": f["index"],
                    "source_name": f["name"],
                })
                print(f"  {name}/{kind}: {len(data)} B sha256={H(data)[:16]}…")
    (CORE / "fighter_entries.json").write_text(
        json.dumps(entries, indent=1))
    (ROOT / "extracted" / "fighters" / "REDUX-0.5-COMPLETION-MANIFEST.json").write_text(
        json.dumps({"output_disc_sha256": got, "files": done,
                    "count": len(done)}, indent=1))
    print(f"completed files: {len(done)} (target 50)")


if __name__ == "__main__":
    main()
