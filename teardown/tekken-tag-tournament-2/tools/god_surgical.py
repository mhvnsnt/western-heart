#!/usr/bin/env python3
"""
TTT2 GoD surgical extractor.

Pulls specific files from the TTT2 Xbox 360 Games-on-Demand package WITHOUT
reassembling the full 13.3GB 7z or rebuilding the 8.86GB XDVDFS image.

How it works:
 1. Opens the 7z (py7zr) and extracts ONLY the GoD header (45KB) + the
    DataXXXX files needed for the requested sectors, on demand.
 2. Uses zarmanager's GodPackage.read_sector() for GoD block geometry.
 3. Uses xdvdfs_reader.XdvdfsReader to walk the Xbox 360 filesystem.
 4. Streams requested inner files to disk, then deletes the DataXXXX
    files used (they're reproducible from the 7z).

Disk budget: 7z (13.3GB, retained per never-delete law) + a few DataXXXX
files at a time (170MB each) + outputs. Stays under the lane budget.

Usage:
    python3 god_surgical.py --sevenz /path/to/TekkenTag2.7z --work /tmp/ttt2god \
        --list                        # print full inner file listing
    python3 god_surgical.py --sevenz ... --work ... \
        --pull "chara/*" --out ./ttt2-chara/
"""
from __future__ import annotations
import argparse
import fnmatch
import os
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, "/home/hatch/workspace/tools/zarmanager")

from xdvdfs_reader import XdvdfsReader

SEVENZ_PREFIX = "Tekken Tag Tournament 2 (EU)/4E4D0859/00007000"
GOD_HEADER_NAME = "392CFF5C9DB17CCAEBC3"
N_DATA_FILES = 52  # Data0000..Data0051

# Filled in after probe()
_SECTORS_PER_FILE = 0x14388


class SurgicalGod:
    def __init__(self, sevenz_path: Path, work_dir: Path):
        self.sevenz_path = Path(sevenz_path)
        self.work = Path(work_dir)
        self.work.mkdir(parents=True, exist_ok=True)
        self.header_path = self.work / GOD_HEADER_NAME
        self.data_dir = self.work / (GOD_HEADER_NAME + ".data")
        self.data_dir.mkdir(exist_ok=True)
        self._sevenz = None
        self._pkg = None
        self._names = None

    # ---- 7z access ----
    def _open_7z(self):
        if self._sevenz is None:
            import py7zr
            self._sevenz = py7zr.SevenZipFile(self.sevenz_path, mode="r")
            self._names = self._sevenz.getnames()
        return self._sevenz

    def _extract_member(self, member, dest: Path):
        """Extract one 7z member to dest (only if dest missing)."""
        if dest.exists():
            return dest
        z = self._open_7z()
        # py7zr extract: use factory to write single file
        tmpdir = dest.parent / (dest.name + ".extract_tmp")
        tmpdir.mkdir(exist_ok=True)
        z.extract(path=str(tmpdir), targets=[member])
        # find the extracted file (py7zr recreates subdirs)
        candidates = list(tmpdir.rglob(dest.name))
        if not candidates:
            raise RuntimeError(f"7z member not extracted: {member}")
        shutil.move(str(candidates[0]), str(dest))
        shutil.rmtree(tmpdir, ignore_errors=True)
        return dest

    def _data_member(self, index: int) -> str:
        return f"{SEVENZ_PREFIX}/{GOD_HEADER_NAME}.data/Data{index:04d}"

    def ensure_data_file(self, index: int) -> Path:
        dest = self.data_dir / f"Data{index:04d}"
        if not dest.exists():
            print(f"[god] extracting Data{index:04d} from 7z...", flush=True)
            self._extract_member(self._data_member(index), dest)
        return dest

    # ---- GoD package ----
    def open(self):
        from core.xbox.god import GodPackage
        if not self.header_path.exists():
            print("[god] extracting GoD header from 7z...", flush=True)
            self._extract_member(f"{SEVENZ_PREFIX}/{GOD_HEADER_NAME}",
                                 self.header_path)
        # Data0000 needed for probe()
        self.ensure_data_file(0)
        pkg = GodPackage(self.header_path)
        pkg._read_header()
        # Pretend all 52 data files exist; _handle() opens on demand and
        # raises GodError if a needed one is missing -> we extract & retry.
        pkg.data_files = [self.data_dir / f"Data{i:04d}" for i in range(N_DATA_FILES)]
        pkg.layout = pkg.probe()
        self._pkg = pkg
        lead = pkg.layout.lead_sectors or 0
        print(f"[god] probe ok: title={pkg.title_id:08X} "
              f"lead_sectors={lead} base={hex(pkg.layout.base)}", flush=True)
        return self

    def _sector_to_data_index(self, sector: int) -> int:
        lead = self._pkg.layout.lead_sectors or 0
        position = sector - lead
        if position < 0:
            return 0
        return position // _SECTORS_PER_FILE

    def read_sector(self, sector: int) -> bytes:
        from core.xbox.god import GodError
        idx = self._sector_to_data_index(sector)
        try:
            return self._pkg.read_sector(sector)
        except GodError:
            # missing data file -> extract and retry once
            self.ensure_data_file(idx)
            # drop cached handle so it reopens
            self._pkg._handles.pop(idx, None)
            return self._pkg.read_sector(sector)

    def close_data_files(self, keep=()):
        """Delete extracted DataXXXX files except indices in `keep`."""
        for p in sorted(self.data_dir.glob("Data*")):
            m = re.search(r"(\d{4})$", p.name)
            if m and int(m.group(1)) not in keep:
                p.unlink()
        self._pkg._handles.clear()

    # ---- XDVDFS ----
    def file_listing(self):
        reader = XdvdfsReader(self.read_sector)
        return reader.list_files(), reader

    def pull(self, pattern: str, out_dir: Path, reader=None):
        files, reader = (None, reader) if reader else self.file_listing()
        if files is None:
            files, reader = self.file_listing()
        out_dir = Path(out_dir)
        pulled = []
        for path, sector, size in files:
            if not fnmatch.fnmatch(path, pattern):
                continue
            dest = out_dir / path
            dest.parent.mkdir(parents=True, exist_ok=True)
            print(f"[pull] {path} ({size} bytes)...", flush=True)
            reader.read_file_to(sector, size, str(dest))
            pulled.append((path, size))
        return pulled


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sevenz", required=True)
    ap.add_argument("--work", required=True)
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--pull", default=None, help="fnmatch pattern, e.g. 'chara/*'")
    ap.add_argument("--out", default="ttt2-pulled")
    args = ap.parse_args()

    god = SurgicalGod(Path(args.sevenz), Path(args.work))
    god.open()
    try:
        if args.list or args.pull:
            files, reader = god.file_listing()
            print(f"[info] {len(files)} files in XDVDFS image")
            if args.list:
                for path, sector, size in sorted(files):
                    print(f"{size:12d}  {path}")
            if args.pull:
                pulled = god.pull(args.pull, Path(args.out), reader)
                total = sum(s for _, s in pulled)
                print(f"[done] pulled {len(pulled)} files, {total} bytes -> {args.out}")
    finally:
        god.close_data_files()


if __name__ == "__main__":
    main()
