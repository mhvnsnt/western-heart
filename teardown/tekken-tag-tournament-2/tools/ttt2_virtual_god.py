#!/usr/bin/env python3
"""
TTT2 GoD inner-listing driver over the VIRTUAL 7z (attempt-3, fixed).

Opens release ttt2-7z-v1 through tools/remote7z.py ChunkedRemoteFile
(spool bounded by REMOTE7Z_MAX_SPOOL, never reassembles 13.36GB) and:

  --list   extract ONLY the 45KB GoD header + Data0000 (+Data0001 on
           demand) from the solid stream, then walk the XDVDFS GAME
           partition (sector 129856 = (0xFD90000+0x10000)//0x800) via
           zarmanager GodPackage + xdvdfs_reader, and save the full
           inner file listing.

Disk budget: spool (<=2x500MB) + tail cache (2MB) + header (45KB) +
Data0000/0001 (2x170MB) + listing JSON. Data files deleted after the
walk (reproducible from the release at any time).

Key fixes vs first draft:
- XdvdfsReader hardcoded sector 32 = the VIDEO partition descriptor.
  The game files live in the XGD2 game partition at sector 129856.
- py7zr needs the 7z EndHeader (last chunk, 256MB download). A 2MB
  HTTP-range tail cache serves it without spooling chunk 26.
"""
from __future__ import annotations
import io
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, "/home/hatch/workspace/tools/zarmanager")

from remote7z import ChunkedRemoteFile, load_asset_ids, REPO, TAG, TOTAL
from xdvdfs_reader import XdvdfsReader

WORK = HERE.parent
SPOOL = WORK / "spool"
SEVENZ_PREFIX = "Tekken Tag Tournament 2 (EU)/4E4D0859/00007000"
GOD_HEADER_NAME = "392CFF5C9DB17CCAEBC3"
GAME_PARTITION_SECTOR = (0xFD90000 + 0x10000) // 0x800  # 129856
TAIL_SIZE = 2 * 1024 * 1024


class OutOfRange(Exception):
    pass


class TailCachedFile(io.RawIOBase):
    """ChunkedRemoteFile + a small HTTP-range tail cache.

    py7zr reads the 7z EndHeader from the archive tail. Without this,
    that single read would spool the whole 256MB last chunk. The tail
    cache serves any read at offset >= TOTAL - TAIL_SIZE from a 2MB
    range download; everything else delegates to ChunkedRemoteFile.
    """

    def __init__(self, spool_dir: Path, asset_ids: dict):
        self.vf = ChunkedRemoteFile(spool_dir, asset_ids)
        self.tail_path = Path(spool_dir) / "tail_cache.bin"
        self._tail: bytes | None = None

    def _ensure_tail(self):
        if self._tail is not None:
            return
        if self.tail_path.exists() and self.tail_path.stat().st_size == TAIL_SIZE:
            self._tail = self.tail_path.read_bytes()
            return
        url = f"https://github.com/{REPO}/releases/download/{TAG}/ttt2-500m.part_26"
        start = (256_424_393 - TAIL_SIZE)
        print(f"[tail] range-fetch last {TAIL_SIZE} bytes of part_26...", flush=True)
        r = subprocess.run(
            ["curl", "-sS", "-L", "-r", f"{start}-",
             "--retry", "3", "--retry-all-errors", "-o", str(self.tail_path), url],
            capture_output=True)
        if r.returncode != 0:
            raise IOError(f"tail range fetch failed: {r.stderr.decode()[:200]}")
        self._tail = self.tail_path.read_bytes()
        if len(self._tail) != TAIL_SIZE:
            raise IOError(f"tail cache short: {len(self._tail)}")

    def _in_tail(self, pos: int) -> bool:
        return pos >= TOTAL - TAIL_SIZE

    def read(self, n: int = -1) -> bytes:
        pos = self.vf.tell()
        if self._in_tail(pos):
            self._ensure_tail()
            if n is None or n < 0:
                n = TOTAL - pos
            n = min(n, TOTAL - pos)
            off = pos - (TOTAL - TAIL_SIZE)
            data = self._tail[off:off + n]
            self.vf.seek(pos + len(data))
            return data
        return self.vf.read(n)

    def readinto(self, b) -> int:
        data = self.read(len(b))
        b[:len(data)] = data
        return len(data)

    def seek(self, offset: int, whence: int = os.SEEK_SET) -> int:
        return self.vf.seek(offset, whence)

    def tell(self) -> int:
        return self.vf.tell()

    def seekable(self) -> bool:
        return True

    def readable(self) -> bool:
        return True

    @property
    def bytes_downloaded(self):
        return self.vf.bytes_downloaded


def open_virtual_7z():
    ids = load_asset_ids(WORK / "asset_ids.json")
    vf = TailCachedFile(SPOOL, ids)
    import py7zr
    return py7zr.SevenZipFile(vf, mode="r"), vf


def extract_targets(z, members: list[str], dest_dir: Path):
    """Extract named members; py7zr streams the solid block, writes only targets."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    tmpdir = dest_dir / ".extract_tmp"
    tmpdir.mkdir(exist_ok=True)
    print(f"[v7z] streaming solid block for {len(members)} target(s)...", flush=True)
    z.extract(path=str(tmpdir), targets=members)
    got = []
    for m in members:
        leaf = m.rsplit("/", 1)[-1]
        cands = list(tmpdir.rglob(leaf))
        if not cands:
            raise RuntimeError(f"target not extracted: {m}")
        dest = dest_dir / leaf
        if dest.exists():
            dest.unlink()
        shutil.move(str(cands[0]), str(dest))
        got.append(dest)
        print(f"[v7z] got {leaf} ({dest.stat().st_size} bytes)", flush=True)
    shutil.rmtree(tmpdir, ignore_errors=True)
    return got


class GodWalk:
    """GoD header + on-demand DataXXXX extraction driving an XDVDFS walk."""

    def __init__(self, work_dir: Path):
        from core.xbox.god import GodPackage, GodError, SECTORS_PER_FILE
        self.work_dir = work_dir
        self.GodPackage = GodPackage
        self.GodError = GodError
        self.SECTORS_PER_FILE = SECTORS_PER_FILE
        self.z, self.vf = open_virtual_7z()
        self.pkg = None
        self.lead = 0
        self.extracted: dict[int, Path] = {}

    def _data_member(self, i: int) -> str:
        return f"{SEVENZ_PREFIX}/{GOD_HEADER_NAME}.data/Data{i:04d}"

    def open(self):
        # ONE extract() call for header + Data0000 + Data0001: each call
        # re-streams the whole solid block, so batch all known targets.
        hdr = self.work_dir / GOD_HEADER_NAME
        members = []
        if not hdr.exists():
            members.append(f"{SEVENZ_PREFIX}/{GOD_HEADER_NAME}")
        members += [self._data_member(0), self._data_member(1)]
        extract_targets(self.z, members, self.work_dir)
        for i in (0, 1):
            self.extracted[i] = self.work_dir / f"Data{i:04d}"
        pkg = self.GodPackage(hdr)
        pkg._read_header()
        pkg.data_files = [self.extracted[0], self.extracted[1]]
        pkg.layout = pkg.probe()
        self.pkg = pkg
        self.lead = pkg.layout.lead_sectors or 0
        print(f"[god] probe ok: title={pkg.title_id:08X} lead={self.lead} "
              f"base={hex(pkg.layout.base)}", flush=True)
        return self

    def read_sector(self, sector: int) -> bytes:
        position = sector - self.lead
        idx = 0 if position < 0 else position // self.SECTORS_PER_FILE
        if idx not in self.extracted:
            # Listing phase: only Data0000/0001 were streamed. Report
            # exactly which Data file a second pass would need.
            raise OutOfRange(
                f"sector {sector} needs Data{idx:04d}: "
                f"re-run with targets extended (second solid-stream pass)")
        try:
            return self.pkg.read_sector(sector)
        except self.GodError as e:
            raise OutOfRange(f"sector {sector}: {e}")

    def cleanup_data(self):
        for p in self.extracted.values():
            try:
                p.unlink()
            except OSError:
                pass
        self.extracted.clear()


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--work", default=str(WORK / "godwork"))
    ap.add_argument("--out", default=str(WORK / "ttt2-inner-listing.json"))
    args = ap.parse_args()

    work_dir = Path(args.work)
    free = shutil.disk_usage(str(WORK)).free
    print(f"[disk] free={free/1e9:.2f}GB (need ~1.5GB peak)", flush=True)
    if free < 1_500_000_000:
        print("[disk] ABORT: <1.5GB free, unsafe to proceed", flush=True)
        sys.exit(2)

    walk = GodWalk(work_dir).open()
    try:
        reader = XdvdfsReader(walk.read_sector, volume_sector=GAME_PARTITION_SECTOR)
        files = reader.list_files()
    finally:
        pass
    print(f"[xdvdfs] {len(files)} files in TTT2 game partition", flush=True)
    rows = sorted(files)
    Path(args.out).write_text(json.dumps(
        [{"path": p, "sector": s, "size": sz} for p, s, sz in rows], indent=1))
    print(f"[ok] wrote {args.out}", flush=True)
    if args.list:
        for p, s, sz in rows:
            print(f"{sz:12d}  {p}")
    dirs: dict[str, int] = {}
    for p, _, _ in rows:
        d = p.rsplit("/", 1)[0] if "/" in p else "/"
        dirs[d] = dirs.get(d, 0) + 1
    print(f"[summary] files={len(rows)} dirs={len(dirs)}", flush=True)
    for d in sorted(dirs)[:50]:
        print(f"  {dirs[d]:5d}  {d}", flush=True)
    walk.cleanup_data()
    print("[ok] extracted Data files deleted (reproducible from release)", flush=True)


if __name__ == "__main__":
    main()
