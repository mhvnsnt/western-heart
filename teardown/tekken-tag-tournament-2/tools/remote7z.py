#!/usr/bin/env python3
"""
ChunkedRemoteFile: a seekable read-only file object presenting the
concatenation of GitHub release assets (ttt2-500m.part_01..26) as one
virtual file, spooling chunks to local disk on demand (LRU, bounded).

Downloads go through `gh api` (authenticated) with the octet-stream
Accept header. The local spool never holds more than MAX_SPOOL chunks.
"""
from __future__ import annotations
import io
import json
import os
import subprocess
import sys
from pathlib import Path

REPO = "mhvnsnt/western-heart"
TAG = "ttt2-7z-v1"
CHUNK = 524_288_000
N_CHUNKS = 26
LAST_SIZE = 256_424_393
TOTAL = (N_CHUNKS - 1) * CHUNK + LAST_SIZE  # 13,363,624,393
# Spool cap: env override so disk-critical lanes can run with 1-2 chunks.
MAX_SPOOL = int(os.environ.get("REMOTE7Z_MAX_SPOOL", "3"))


class ChunkedRemoteFile(io.RawIOBase):
    def __init__(self, spool_dir: Path, asset_ids: dict[str, int]):
        self.spool = Path(spool_dir)
        self.spool.mkdir(parents=True, exist_ok=True)
        self.asset_ids = asset_ids  # name -> id
        self._pos = 0
        self._lru: list[int] = []  # chunk indices, most-recent last
        self.bytes_downloaded = 0

    # ---------- chunk management ----------
    def _chunk_name(self, idx: int) -> str:
        return f"ttt2-500m.part_{idx + 1:02d}"

    def _chunk_path(self, idx: int) -> Path:
        return self.spool / f"part_{idx + 1:02d}"

    def _chunk_dl_url(self, name: str) -> str:
        # deterministic release-asset download URL (verified 2026-10-21)
        return f"https://github.com/{REPO}/releases/download/{TAG}/{name}"

    def _download_parallel(self, name: str, dest_tmp: Path, total: int,
                           workers: int = 8) -> None:
        """Download a chunk via parallel curl byte-range requests.

        Resumes an existing partial tmp file: only the missing tail is
        fetched, in `workers` ranges, then concatenated in order.
        """
        url = self._chunk_dl_url(name)
        have = dest_tmp.stat().st_size if dest_tmp.exists() else 0
        if have > total:
            raise IOError(f"oversized partial for {name}: {have} > {total}")
        missing = total - have
        if missing == 0:
            return
        # split the missing tail into worker ranges
        spans = []
        per, rem = divmod(missing, workers)
        off = have
        for w in range(workers):
            ln = per + (1 if w < rem else 0)
            if ln <= 0:
                continue
            spans.append((off, off + ln - 1, w))
            off += ln
        parts = []
        procs = []
        for start, end, w in spans:
            part = dest_tmp.with_name(f"{dest_tmp.name}.r{w}")
            parts.append((w, part))
            procs.append(subprocess.Popen(
                ["curl", "-sS", "-L", "-r", f"{start}-{end}",
                 "--retry", "3", "--retry-all-errors",
                 "-o", str(part), url],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
        for p in procs:
            if p.wait() != 0:
                raise IOError(f"range download failed for {name}")
        for w, part in sorted(parts):
            if not part.exists() or part.stat().st_size == 0:
                raise IOError(f"empty range file for {name} range {w}")
        # append in order
        with open(dest_tmp, "ab") as out:
            for w, part in sorted(parts):
                with open(part, "rb") as f:
                    while True:
                        blk = f.read(8 * 1024 * 1024)
                        if not blk:
                            break
                        out.write(blk)
                part.unlink()
        final = dest_tmp.stat().st_size
        if final != total:
            raise IOError(f"chunk {name} size mismatch: {final} != {total}")

    def _ensure_chunk(self, idx: int) -> Path:
        p = self._chunk_path(idx)
        want = LAST_SIZE if idx == N_CHUNKS - 1 else CHUNK
        if p.exists() and p.stat().st_size == want:
            self._touch(idx)
            return p
        name = self._chunk_name(idx)
        tmp = p.with_suffix(".tmp")
        print(f"[remote7z] downloading chunk {idx + 1}/{N_CHUNKS} "
              f"({name}, {want} bytes, parallel ranges)...", flush=True)
        self._download_parallel(name, tmp, want)
        tmp.rename(p)
        self.bytes_downloaded += want
        self._touch(idx)
        self._evict()
        return p

    def _touch(self, idx: int):
        if idx in self._lru:
            self._lru.remove(idx)
        self._lru.append(idx)

    def _evict(self):
        while len(self._lru) > MAX_SPOOL:
            old = self._lru.pop(0)
            try:
                self._chunk_path(old).unlink()
            except FileNotFoundError:
                pass

    # ---------- file object protocol ----------
    def readinto(self, b) -> int:
        data = self.read(len(b))
        b[:len(data)] = data
        return len(data)

    def read(self, n: int = -1) -> bytes:
        if n is None or n < 0:
            n = TOTAL - self._pos
        out = bytearray()
        while n > 0 and self._pos < TOTAL:
            idx = self._pos // CHUNK
            inner = self._pos % CHUNK
            p = self._ensure_chunk(idx)
            take = min(n, CHUNK - inner)
            with open(p, "rb") as f:
                f.seek(inner)
                data = f.read(take)
            if not data:
                break
            out += data
            self._pos += len(data)
            n -= len(data)
        return bytes(out)

    def seek(self, offset: int, whence: int = os.SEEK_SET) -> int:
        if whence == os.SEEK_SET:
            self._pos = offset
        elif whence == os.SEEK_CUR:
            self._pos += offset
        elif whence == os.SEEK_END:
            self._pos = TOTAL + offset
        if self._pos < 0:
            raise ValueError("negative seek")
        return self._pos

    def tell(self) -> int:
        return self._pos

    def seekable(self) -> bool:
        return True

    def readable(self) -> bool:
        return True

    def close(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *a):
        self.close()


def load_asset_ids(cache: Path) -> dict[str, int]:
    if cache.exists():
        return json.loads(cache.read_text())
    out = subprocess.run(
        ["gh", "api", f"repos/{REPO}/releases/tags/{TAG}",
         "-q", ".assets[] | .name + \" \" + (.id|tostring)"],
        capture_output=True, text=True)
    ids = {}
    for line in out.stdout.splitlines():
        name, _, aid = line.rpartition(" ")
        ids[name] = int(aid)
    cache.write_text(json.dumps(ids, indent=1))
    return ids


if __name__ == "__main__":
    ids = load_asset_ids(Path(sys.argv[1]) if len(sys.argv) > 1
                         else Path("asset_ids.json"))
    print(f"{len(ids)} assets; part_01 id={ids.get('ttt2-500m.part_01')}")
