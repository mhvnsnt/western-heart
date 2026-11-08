#!/usr/bin/env python3
"""Parallel range-fetcher for one byte-range of the Tekken 5 ISO.

Usage: fetch_range.py <iso_start> <size> <outfile> [--streams N] [--chunk MB]
- Downloads ISO bytes [iso_start, iso_start+size) into outfile via HTTP Range,
  in parallel chunks, with per-chunk resume state (<outfile>.ranges.json).
- Pre-allocates sparse; verifies total size at the end (byte count only).
- Logs progress to stdout (redirect to a log file; safe to re-run to resume).

Source: Internet Archive item slus-210.59.-tekken-5 (md5
5bce17ccabacea46d621d195c4600ebb, sha1
97ca517151229bc1c6a58396ccf470f91676f047). Offsets/sizes confirmed from
the ISO9660 primary volume descriptor in raw/iso_head.bin:
  TK5DATA0.BIN: ISO 1716224, 2072586240 bytes
  TK5DATA1.BIN: ISO 2074302464, 1297731584 bytes
"""
import json
import os
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor

URL = "https://ia601004.us.archive.org/8/items/slus-210.59.-tekken-5/SLUS_210.59.Tekken%205.ISO"


def save_state(path, state):
    tmp = path + ".ranges.json.tmp"
    with open(tmp, "w") as f:
        json.dump(state, f)
    os.replace(tmp, path + ".ranges.json")


def load_state(path, nchunks):
    try:
        with open(path + ".ranges.json") as f:
            st = json.load(f)
        if len(st.get("done", [])) == nchunks:
            return st
    except (OSError, ValueError):
        pass
    return {"done": [False] * nchunks}


def fetch_chunk(iso_start, size, path, idx, cstart, cend, state, retries=5):
    """Fetch outfile bytes [cstart, cend) from ISO [iso_start+cstart, ...)."""
    n = cend - cstart
    for attempt in range(retries):
        try:
            req = urllib.request.Request(
                URL, headers={"Range": f"bytes={iso_start + cstart}-{iso_start + cend - 1}"})
            with urllib.request.urlopen(req, timeout=120) as r:
                if r.status not in (200, 206):
                    raise RuntimeError(f"HTTP {r.status}")
                fd = os.open(path, os.O_WRONLY)
                try:
                    off = cstart
                    got = 0
                    while True:
                        b = r.read(1 << 20)
                        if not b:
                            break
                        os.pwrite(fd, b, off)
                        off += len(b)
                        got += len(b)
                finally:
                    os.close(fd)
            if got != n:
                raise RuntimeError(f"short read {got}/{n}")
            state["done"][idx] = True
            save_state(path, state)
            return True
        except Exception as e:
            print(f"  chunk {idx} attempt {attempt + 1} failed: {e}", flush=True)
            time.sleep(5)
    return False


def main():
    iso_start = int(sys.argv[1])
    size = int(sys.argv[2])
    path = sys.argv[3]
    streams = 16
    chunk_mb = 10
    for a in sys.argv[4:]:
        if a.startswith("--streams="):
            streams = int(a.split("=")[1])
        elif a.startswith("--chunk="):
            chunk_mb = int(a.split("=")[1])
    chunk = chunk_mb * 1024 * 1024
    bounds = [(s, min(s + chunk, size)) for s in range(0, size, chunk)]
    print(f"fetch ISO[{iso_start}:{iso_start + size}) -> {path} "
          f"({size} bytes, {len(bounds)} chunks x {chunk_mb}MB, {streams} streams)", flush=True)
    if not os.path.exists(path) or os.path.getsize(path) != size:
        with open(path, "wb") as f:
            f.truncate(size)
        state = {"done": [False] * len(bounds)}
        save_state(path, state)
    else:
        state = load_state(path, len(bounds))
    todo = [i for i in range(len(bounds)) if not state["done"][i]]
    print(f"chunks to fetch: {len(todo)}/{len(bounds)}", flush=True)
    failed = []
    done = len(bounds) - len(todo)
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=streams) as ex:
        futs = {ex.submit(fetch_chunk, iso_start, size, path, i,
                          bounds[i][0], bounds[i][1], state): i for i in todo}
        for fut in futs:
            ok = fut.result()
            done += 1
            if done % 20 == 0 or not ok:
                el = time.time() - t0
                print(f"  {done}/{len(bounds)} chunks, {el:.0f}s elapsed", flush=True)
            if not ok:
                failed.append(futs[fut])
    if failed:
        print(f"FAILED chunks: {failed}", flush=True)
        return 1
    got = os.path.getsize(path)
    print(f"done: {path} ({got} bytes, expected {size}, "
          f"match={got == size})", flush=True)
    return 0 if got == size else 1


if __name__ == "__main__":
    sys.exit(main())
