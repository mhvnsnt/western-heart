#!/usr/bin/env python3
"""Fetch one ISO byte-range in parallel slices (stdlib only).

Usage: parallel_range.py <range_start> <range_end> <outfile> <nstreams>
Resumes: keeps <outfile> prefix already downloaded; fetches only the
remaining tail [range_start+have, range_end) in N parallel slices,
appends them in order. Verifies final size.
"""
import os, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor

URL = "https://ia601004.us.archive.org/8/items/slus-210.59.-tekken-5/SLUS_210.59.Tekken%205.ISO"

def fetch_slice(i, start, end, tmp):
    expect = end - start
    for attempt in range(5):
        try:
            req = urllib.request.Request(URL, headers={"Range": f"bytes={start}-{end-1}"})
            with urllib.request.urlopen(req, timeout=60) as r:
                if r.status not in (200, 206):
                    raise RuntimeError(f"HTTP {r.status}")
                data = r.read()
            if len(data) == expect:
                with open(tmp, "wb") as f:
                    f.write(data)
                print(f"slice {i}: {expect} bytes OK", flush=True)
                return True
            print(f"slice {i}: got {len(data)} want {expect}, retry {attempt+1}", flush=True)
        except Exception as e:
            print(f"slice {i}: {e}, retry {attempt+1}", flush=True)
            time.sleep(5)
    print(f"slice {i}: FAILED", flush=True)
    return False

def main():
    rs, re_, out, n = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3], int(sys.argv[4])
    have = os.path.getsize(out) if os.path.exists(out) else 0
    total = re_ - rs
    assert have <= total, f"have {have} > total {total}"
    if have == total:
        print("already complete"); return 0
    rem_start = rs + have
    rem = re_ - rem_start
    print(f"have {have}/{total}, fetching remaining {rem} bytes in {n} slices", flush=True)
    bounds = []
    base = rem // n
    for i in range(n):
        s = rem_start + i * base
        e = rem_start + (i + 1) * base if i < n - 1 else re_
        bounds.append((s, e))
    tmps = [f"{out}.part{i}" for i in range(n)]
    with ThreadPoolExecutor(max_workers=n) as ex:
        results = list(ex.map(lambda t: fetch_slice(t[0], t[1], t[2], t[3]),
                              [(i, s, e, tmps[i]) for i, (s, e) in enumerate(bounds)]))
    if not all(results):
        print("FAILED: some slices missing", flush=True)
        return 1
    with open(out, "ab") as f:
        for i, tmp in enumerate(tmps):
            with open(tmp, "rb") as pf:
                f.write(pf.read())
            os.unlink(tmp)
    final = os.path.getsize(out)
    print(f"done: {out} = {final} bytes (want {total})", flush=True)
    return 0 if final == total else 1

if __name__ == "__main__":
    sys.exit(main())
