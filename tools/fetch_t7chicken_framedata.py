#!/usr/bin/env python3
"""Vendor the public Tekken 7 frame data (t7chicken, TekkenBot-extracted) into the repo.

Source: https://github.com/dayhaysoos/t7chickenplus-graphql (ISC, package.json), folder
assets/characters/<label>.json, one file per T7 character (47 files, 11,137 movelist rows).
Muse's 2026-10-20 "FULL MOVESET LAW cluster B" import (74efb3fb) used the same dataset but
the import script never landed in the repo; this makes the pull reproducible.

The clone is pinned to the commit the vendored copy was taken from, and every file's
SHA-256 is written to SOURCE.json next to the data, so a re-run can prove the bytes match.

Usage:
  python3 tools/fetch_t7chicken_framedata.py                 # clone pinned commit, copy, write SOURCE.json
  python3 tools/fetch_t7chicken_framedata.py --check         # verify vendored files against SOURCE.json
"""
import argparse, hashlib, json, pathlib, shutil, subprocess, sys, tempfile

REPO = pathlib.Path(__file__).resolve().parents[1]
URL = "https://github.com/dayhaysoos/t7chickenplus-graphql"
PIN = "91a054e880f2a977bf285b48860accfed701c13e"  # HEAD on 2026-10-21 (last upstream commit 2020-05-11)
OUT = REPO / "docs/t7t8-reference/frame-data-t7"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    if a.check:
        src = json.loads((OUT / "SOURCE.json").read_text())
        bad = [f for f, h in src["files"].items() if sha(OUT / f) != h]
        print(f"{len(src['files'])} files, {len(bad)} mismatched", *bad)
        sys.exit(1 if bad else 0)
    with tempfile.TemporaryDirectory() as td:
        subprocess.run(["git", "clone", "--quiet", URL, td + "/t7c"], check=True)
        subprocess.run(["git", "-C", td + "/t7c", "checkout", "--quiet", PIN], check=True)
        OUT.mkdir(parents=True, exist_ok=True)
        files, rows = {}, 0
        for f in sorted(pathlib.Path(td, "t7c/assets/characters").glob("*.json")):
            shutil.copyfile(f, OUT / f.name)
            files[f.name] = sha(OUT / f.name)
            d = json.loads(f.read_text())
            rows += len(d["movelist"] if isinstance(d, dict) else d)
    (OUT / "SOURCE.json").write_text(json.dumps({
        "source": URL, "commit": PIN, "path": "assets/characters/*.json",
        "license": "ISC (upstream package.json); data extracted with TekkenBot",
        "game": "Tekken 7", "characters": len(files), "movelist_rows": rows,
        "tool": "tools/fetch_t7chicken_framedata.py", "files": files}, indent=1) + "\n")
    print(f"{len(files)} characters, {rows} rows -> {OUT.relative_to(REPO)}")


if __name__ == "__main__":
    main()
