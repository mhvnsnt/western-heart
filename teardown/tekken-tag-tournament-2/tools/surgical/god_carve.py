#!/usr/bin/env python3
"""Carve files out of the TTT2 Xbox 360 Games-on-Demand package using
LOCALLY DECODED Data members (no local 7z needed).

Pipeline:
    seg_dl.py [0, 5.2GB) -> work/prefix/
    decode_local.py work/prefix work/god 20 [21 ...]   # Data0000, Data0001...
    # rename member_20.bin -> work/god/Data0000 etc.
    god_carve.py --header work/god-header.bin --data-dir work/god --list
    god_carve.py --header work/god-header.bin --data-dir work/god \\
        --pull "*/law/*,*/lars/*" --out work/law-lars/

Missing Data members abort with the 7z member index to decode next
(member index = 20 + data index; see tools/surgical/README.md).

Writes MANIFEST.txt (path, bytes, sha256) next to pulled files.
Game binaries >50MB are NOT committed to the repo — see the runbook.
"""
from __future__ import annotations
import argparse
import fnmatch
import hashlib
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))          # stream_decode etc.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))    # xdvdfs_reader

MEMBER_BASE = 20  # 7z header index of Data0000


def zarmanager_path(explicit: str | None) -> str:
    """Locate core/xbox/{god,stfs}.py (never vendored: upstream license unverified)."""
    candidates = []
    if explicit:
        candidates.append(explicit)
    candidates.append(os.environ.get("ZARM_DIR", ""))
    here = Path(__file__).resolve().parent
    candidates.append(str(here / "zarmanager"))
    candidates.append(os.path.expanduser("~/tools/zarmanager"))
    for c in candidates:
        if c and (Path(c) / "core" / "xbox" / "god.py").exists():
            return c
    raise SystemExit(
        "[carve] ZarManager modules not found. Run:\n"
        "    python3 fetch_zarmanager.py <destdir>\n"
        "  then pass --zarm-dir <destdir> (or set ZARM_DIR).")


def open_pkg(header: Path, data_dir: Path, zarm_dir: str | None):
    sys.path.insert(0, zarmanager_path(zarm_dir))
    from core.xbox.god import GodPackage, GodError
    pkg = GodPackage(header)
    pkg._read_header()
    files = sorted(data_dir.glob("Data[0-9][0-9][0-9][0-9]"))
    idx = {int(p.name[4:]): p for p in files}
    n = max(idx) + 1 if idx else 0
    pkg.data_files = [idx.get(i, data_dir / f"Data{i:04d}") for i in range(n)]
    try:
        pkg.layout = pkg.probe()
    except GodError as e:
        raise SystemExit(f"[carve] probe failed: {e}\n"
                         f"  (need Data0000 decoded at least; have: {sorted(idx)})")
    print(f"[carve] title={pkg.title_id:08X} data_files={n} "
          f"base={hex(pkg.layout.base)} lead={pkg.layout.lead_sectors}", flush=True)
    return pkg


def make_reader(pkg):
    from core.xbox.god import GodError
    from xdvdfs_reader import XdvdfsReader

    def read_sector(sector: int) -> bytes:
        try:
            return pkg.read_sector(sector)
        except GodError as e:
            m = re.search(r"data(\d{4})", str(e))
            hint = ""
            if m:
                di = int(m.group(1))
                hint = (f" -> decode 7z member {MEMBER_BASE + di} "
                        f"(Data{di:04d}) and retry")
            raise SystemExit(f"[carve] missing data for sector {sector}: {e}{hint}")
    return XdvdfsReader(read_sector)


def cmd_list(pkg, out: str | None):
    reader = make_reader(pkg)
    files = reader.list_files()
    lines = [f"{size:12d}  {path}" for path, _, size in sorted(files)]
    text = "\n".join(lines) + "\n"
    print(f"[carve] {len(files)} files in XDVDFS image")
    if out:
        Path(out).write_text(text)
        print(f"[carve] listing -> {out}")
    else:
        print(text)


def cmd_pull(pkg, patterns: list[str], out_dir: Path):
    from xdvdfs_reader import XdvdfsReader  # noqa
    reader = make_reader(pkg)
    files = reader.list_files()
    out_dir = Path(out_dir)
    manifest = []
    total = 0
    for path, sector, size in sorted(files):
        low = path.lower()
        if not any(fnmatch.fnmatch(low, p) for p in patterns):
            continue
        dest = out_dir / path
        dest.parent.mkdir(parents=True, exist_ok=True)
        print(f"[pull] {path} ({size} bytes)...", flush=True)
        h = hashlib.sha256()
        with open(dest, "wb") as f:
            remaining, sec = size, sector
            while remaining > 0:
                data = reader._sector(sec)
                take = min(len(data), remaining)
                f.write(data[:take])
                h.update(data[:take])
                remaining -= take
                sec += 1
        manifest.append(f"{h.hexdigest()}  {size:12d}  {path}")
        total += size
    (out_dir / "MANIFEST.txt").write_text("\n".join(manifest) + "\n")
    print(f"[done] pulled {len(manifest)} files, {total} bytes -> {out_dir}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--header", required=True)
    ap.add_argument("--data-dir", required=True)
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--listing-out", default=None)
    ap.add_argument("--pull", default=None,
                    help="comma-separated fnmatch patterns (matched lowercased), e.g. '*/law/*,*/lars/*'")
    ap.add_argument("--out", default="carved")
    ap.add_argument("--zarm-dir", default=None,
                    help="dir holding core/xbox/{god,stfs}.py (see fetch_zarmanager.py)")
    args = ap.parse_args()

    pkg = open_pkg(Path(args.header), Path(args.data_dir), args.zarm_dir)
    if args.list or not args.pull:
        cmd_list(pkg, args.listing_out)
    if args.pull:
        patterns = [p.strip().lower() for p in args.pull.split(",") if p.strip()]
        cmd_pull(pkg, patterns, Path(args.out))


if __name__ == "__main__":
    main()
