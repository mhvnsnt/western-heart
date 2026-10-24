#!/usr/bin/env python3
"""
TTT2 00000002/ STFS blob lister/extractor.

The 7 title-data blobs (51MB..2.03GB) in
  Tekken Tag Tournament 2 (EU)/0000000000000000/4E4D0859/00000002/
are standard Xbox 360 STFS packages (DLC / title-update content).
This lists their inner files via zarmanager's StfsPackage and extracts
on demand — one blob at a time from the 7z, deleted after use.

Usage:
    python3 stfs_blobs.py --sevenz /path/to.7z --work /tmp/ttt2stfs --list
    python3 stfs_blobs.py --sevenz /path/to.7z --work /tmp/ttt2stfs \
        --pull "pattern" --out ./ttt2-dlc/
"""
from __future__ import annotations
import argparse
import fnmatch
import shutil
import sys
from pathlib import Path

sys.path.insert(0, "/home/hatch/workspace/tools/zarmanager")

SEVENZ_PREFIX = "Tekken Tag Tournament 2 (EU)/0000000000000000/4E4D0859/00000002"
BLOBS = [
    # (7z member suffix, size) — from INVENTORY.md
    ("869D8990CC6F0B041AC60DA3A0D8C0DA02E9B4144E", 51_015_680),
    ("CA05E23233AFFE81C0981C4679C00A0B09C06ED14E", 79_253_504),
    ("81048E1CD581F1B23355ACEAF1E9F58581AC8C814E", 80_576_512),
    ("3FADC8AF15DE90375EC378F1ACD16F90B8C4A3034E", 155_930_624),
    ("86EC81D48AE0C295E0A0EFB227BCFF41F90B680B4E", 357_920_768),
    ("FC2BA3B334AC3E4F46E2A576EEF41F1EE268F5C44E", 1_942_929_408),
    ("98D464B93A3BA14D4C4CB7E24BB661FA6E70C9424E", 2_034_626_560),
]


def extract_blob(sevenz_path: Path, work: Path, suffix: str) -> Path:
    import py7zr
    dest = work / (suffix + ".stfs")
    if dest.exists() and dest.stat().st_size > 0:
        return dest
    member = f"{SEVENZ_PREFIX}/{suffix}"
    print(f"[stfs] extracting blob {suffix[:12]}... from 7z", flush=True)
    tmpdir = work / (suffix + ".extract_tmp")
    tmpdir.mkdir(exist_ok=True)
    with py7zr.SevenZipFile(sevenz_path, mode="r") as z:
        z.extract(path=str(tmpdir), targets=[member])
    cands = list(tmpdir.rglob(suffix))
    if not cands:
        raise RuntimeError(f"blob not extracted: {suffix}")
    shutil.move(str(cands[0]), str(dest))
    shutil.rmtree(tmpdir, ignore_errors=True)
    return dest


def list_blob(blob_path: Path):
    from core.xbox.stfs import StfsPackage
    with StfsPackage(blob_path) as pkg:
        return [(e.path, e.size, e.is_directory) for e in pkg.files()]


def pull_from_blob(blob_path: Path, pattern: str, out_dir: Path):
    from core.xbox.stfs import StfsPackage
    out_dir.mkdir(parents=True, exist_ok=True)
    pulled = []
    with StfsPackage(blob_path) as pkg:
        for e in pkg.files():
            if e.is_directory or not fnmatch.fnmatch(e.path, pattern):
                continue
            dest = out_dir / e.path
            dest.parent.mkdir(parents=True, exist_ok=True)
            with dest.open("wb") as f:
                for chunk in pkg.read_file(e):
                    f.write(chunk)
            pulled.append((e.path, e.size))
    return pulled


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sevenz", required=True)
    ap.add_argument("--work", required=True)
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--pull", default=None)
    ap.add_argument("--out", default="ttt2-dlc-pulled")
    ap.add_argument("--blobs", default="all",
                    help="comma-separated blob indices 0-6, or 'all'")
    args = ap.parse_args()
    sevenz = Path(args.sevenz)
    work = Path(args.work)
    work.mkdir(parents=True, exist_ok=True)

    idxs = range(len(BLOBS)) if args.blobs == "all" else [int(i) for i in args.blobs.split(",")]
    for i in idxs:
        suffix, size = BLOBS[i]
        blob = extract_blob(sevenz, work, suffix)
        try:
            if args.list:
                print(f"=== blob[{i}] {suffix[:16]}... ({size} bytes) ===")
                for path, sz, is_dir in sorted(list_blob(blob)):
                    print(f"{'d' if is_dir else 'f'} {sz:12d}  {path}")
            if args.pull:
                pulled = pull_from_blob(blob, args.pull, Path(args.out) / f"blob{i}")
                for p, s in pulled:
                    print(f"[pull] blob{i}: {p} ({s})")
        finally:
            # delete blob after use — reproducible from 7z
            blob.unlink(missing_ok=True)
    print("[done]")


if __name__ == "__main__":
    main()
