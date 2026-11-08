#!/usr/bin/env python3
"""Lane 2 extraction step A: verify + extract the core .urmod parts and HD packs.

Uses ONLY the author's own tools/formats:
- .urmod = ZIP + manifest.json (Source/vendor/mod-manager/urrpack.py: check/write_fighter/write_hd)
- parts = (entry, offset, length, sha256) byte ranges of the OUTPUT disc (urr-base-1)
- copies = [src, dst, length] ranges copied from the source ISO (not on this VM)

Outputs under ~/workspace/urban-reign-redux/extracted/:
  core/manifest.json, core/parts/data/NNNNNN.bin (sha-verified), core/coverage.json
  hd-main/, hd-full/ (PNGs + manifest.json, sha-verified)
"""
import hashlib, json, sys, zipfile
from pathlib import Path

ROOT = Path.home() / "workspace" / "urban-reign-redux"
MM = ROOT / "work" / "mm" / "Urban Reign Redux Mod Manager 0.5" / "mods"
OUT = ROOT / "extracted"
CORE = OUT / "core"
H = lambda b: hashlib.sha256(b).hexdigest()

def verify_and_extract(zip_path, dest, manifest_name="manifest.json"):
    dest.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path) as z:
        m = json.loads(z.read(manifest_name))
        (dest / "manifest.json").write_text(json.dumps(m, indent=1))
        return z, m

def main():
    core_zip = MM / "Urban Reign Redux 0.5 V97.urmod"
    CORE.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(core_zip) as z:
        m = json.loads(z.read("manifest.json"))
        (CORE / "manifest.json").write_text(json.dumps(m, indent=1))
        parts = m["parts"]
        print(f"core manifest: format={m['format']} id={m['id']} parts={len(parts)} copies={len(m['copies'])}")
        print(f"output disc: size={m['output_size']} sha={m['output_sha256']} crc={m['pcsx2_crc']}")
        print(f"source disc: size={m['source_size']} sha={m['source_sha256'][0]}")
        total = sum(p["length"] for p in parts)
        print(f"parts total bytes: {total}")
        bad = 0
        pdir = CORE / "parts"
        pdir.mkdir(parents=True, exist_ok=True)
        for i, p in enumerate(parts):
            b = z.read(p["entry"])
            if len(b) != p["length"] or H(b) != p["sha256"]:
                bad += 1
                print(f"  BAD PART {p['entry']}: len {len(b)} vs {p['length']}, sha ok={H(b)==p['sha256']}")
                continue
            (pdir / Path(p["entry"]).name).write_bytes(b)
            if i % 1000 == 0:
                print(f"  ...{i}/{len(parts)} parts verified+extracted")
        print(f"parts bad: {bad}")
        # coverage intervals over output-disc coordinates
        ivs = sorted((p["offset"], p["offset"] + p["length"]) for p in parts)
        merged = []
        for a, b in ivs:
            if merged and a <= merged[-1][1]:
                merged[-1] = (merged[-1][0], max(merged[-1][1], b))
            else:
                merged.append((a, b))
        cov = sum(b - a for a, b in merged)
        print(f"merged intervals: {len(merged)}  covered bytes: {cov} / {m['output_size']} ({100*cov/m['output_size']:.2f}%)")
        json.dump({"merged_intervals": merged, "covered_bytes": cov,
                   "output_size": m["output_size"]},
                  open(CORE / "coverage.json", "w"), indent=1)
        # region coverage helper
        import bisect
        starts = [a for a, _ in merged]
        def covered_frac(a, b):
            n = b - a; got = 0
            i = bisect.bisect_right(starts, a) - 1
            if i < 0: i = 0
            while i < len(merged) and merged[i][0] < b:
                lo, hi = merged[i]
                got += max(0, min(hi, b) - max(lo, a))
                i += 1
            return got / n if n else 1.0
        lay = m["layout"]
        for arch in ("DVD000", "DVD001"):
            L = lay[arch]
            base = L["offset"]
            hdr = (base, base + 8 + 8 * L["count"] + 8)
            names = (base + L["names_at"], base + L["names_at"] + L["names_size"])
            data = (base + L["first"], base + L["bytes"])
            print(f"{arch}: header/table coverage {covered_frac(*hdr):.3f}  names coverage {covered_frac(*names):.3f}  data-region coverage {covered_frac(*data):.3f}")
        elf = lay["ELF"]
        print(f"ELF: coverage {covered_frac(elf['offset'], elf['offset']+elf['bytes']):.3f}  (offset {elf['offset']}, {elf['bytes']} B)")
        json.dump({"layout": lay}, open(CORE / "layout.json", "w"), indent=1)

    # HD packs
    for zipname, sub in [("Urban Reign Redux 0.5 V97 HD textures.urmod", "hd-main"),
                         ("Urban Reign Redux 0.5 V97 HD textures, full set.urmod", "hd-full")]:
        dest = OUT / sub
        dest.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(MM / zipname) as z:
            m = json.loads(z.read("manifest.json"))
            (dest / "manifest.json").write_text(json.dumps(m, indent=1))
            bad = 0; total = 0
            for f in m["files"]:
                b = z.read(f["file"])
                total += len(b)
                if H(b) != f["sha256"]:
                    bad += 1; print(f"  BAD HD {f['file']}")
                    continue
                (dest / Path(f["file"]).name).write_bytes(b)
            print(f"{sub}: {len(m['files'])} files, {total} bytes, bad={bad}, folder={m.get('folder')}")
    print("DONE step A")

if __name__ == "__main__":
    main()
