#!/usr/bin/env python3
"""Parallel range downloader (stdlib only) for a single large file.

Usage: ia_parallel_dl.py <url> <outfile> [--streams N] [--chunk MB]
- Splits the file into N equal ranges, downloads each with HTTP Range
  in a thread pool, writes with os.pwrite at the right offset.
- Resumes: if outfile exists and is a prefix of the target (same size
  prefix bytes), already-complete ranges are skipped. A per-range
  .state file records completed ranges so a re-run skips them.
- Verifies nothing itself; caller runs md5sum/sha1sum afterwards.
"""
import argparse
import hashlib
import json
import os
import sys
import threading
import urllib.request
from concurrent.futures import ThreadPoolExecutor

STATE_SUFFIX = ".ranges.json"


def get_total_size(url):
    req = urllib.request.Request(url, method="HEAD")
    with urllib.request.urlopen(req, timeout=30) as r:
        total = int(r.headers["Content-Length"])
        accept = r.headers.get("Accept-Ranges", "")
    return total, accept


def download_range(url, path, start, end, idx, state, lock, retries=5):
    """Download bytes [start, end] inclusive into path at offset start."""
    size = end - start + 1
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url)
            req.add_header("Range", f"bytes={start}-{end}")
            with urllib.request.urlopen(req, timeout=60) as r:
                if r.status not in (200, 206):
                    raise RuntimeError(f"HTTP {r.status} for range {start}-{end}")
                fd = os.open(path, os.O_WRONLY)
                try:
                    off = start
                    got = 0
                    while True:
                        chunk = r.read(1 << 20)
                        if not chunk:
                            break
                        os.pwrite(fd, chunk, off)
                        off += len(chunk)
                        got += len(chunk)
                finally:
                    os.close(fd)
            if got != size:
                raise RuntimeError(f"range {start}-{end}: got {got}/{size} bytes")
            with lock:
                state["done"][idx] = True
                save_state(path, state)
            return True
        except Exception as e:
            print(f"  range {idx} attempt {attempt+1} failed: {e}", flush=True)
    return False


def save_state(path, state):
    tmp = path + STATE_SUFFIX + ".tmp"
    with open(tmp, "w") as f:
        json.dump(state, f)
    os.replace(tmp, path + STATE_SUFFIX)


def load_state(path, nstreams):
    try:
        with open(path + STATE_SUFFIX) as f:
            st = json.load(f)
        if st.get("nstreams") == nstreams and len(st.get("done", [])) == nstreams:
            return st
    except (OSError, ValueError):
        pass
    return {"nstreams": nstreams, "done": [False] * nstreams}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("outfile")
    ap.add_argument("--streams", type=int, default=16)
    ap.add_argument("--timeout", type=int, default=600)
    args = ap.parse_args()

    total, accept = get_total_size(args.url)
    print(f"total={total} bytes accept-ranges={accept!r}", flush=True)
    if "bytes" not in accept:
        print("server does not advertise Accept-Ranges; trying ranges anyway", flush=True)

    # Pre-allocate the file (sparse) so pwrite offsets are valid.
    if not os.path.exists(args.outfile) or os.path.getsize(args.outfile) != total:
        with open(args.outfile, "wb") as f:
            f.truncate(total)
        state = {"nstreams": args.streams, "done": [False] * args.streams}
        save_state(args.outfile, state)
    else:
        state = load_state(args.outfile, args.streams)

    n = args.streams
    base = total // n
    ranges = []
    for i in range(n):
        s = i * base
        e = total - 1 if i == n - 1 else (i + 1) * base - 1
        ranges.append((s, e))

    todo = [i for i in range(n) if not state["done"][i]]
    print(f"ranges to fetch: {len(todo)}/{n}", flush=True)
    lock = threading.Lock()
    failed = []
    with ThreadPoolExecutor(max_workers=n) as ex:
        futs = {ex.submit(download_range, args.url, args.outfile, ranges[i][0],
                          ranges[i][1], i, state, lock): i for i in todo}
        for fut in futs:
            ok = fut.result()
            print(f"range {futs[fut]}: {'OK' if ok else 'FAILED'}", flush=True)
            if not ok:
                failed.append(futs[fut])
    if failed:
        print(f"FAILED ranges: {failed}", flush=True)
        return 1
    print(f"done: {args.outfile} ({os.path.getsize(args.outfile)} bytes)", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
