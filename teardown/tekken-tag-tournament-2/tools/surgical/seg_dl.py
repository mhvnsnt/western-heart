#!/usr/bin/env python3
"""Parallel segmented download of the TTT2 7z compressed stream.

Each worker fetches a disjoint absolute byte range [start, end) of the
concatenated 7z (i.e. of the reassembled archive) via Range requests,
mapping to release parts internally. Workers write segment files;
concatenating them in order reproduces the stream prefix.

Usage:
    seg_dl.py <start> <end> <nworkers> <outdir>
Prints aggregate MB/s. Resume-safe per segment file.
"""
import os
import sys
import time
import threading

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fetch_assets as dl  # noqa: E402
import vfile  # noqa: E402

CHUNK = 4 * 1024 * 1024


def worker(vf, abs_start, abs_end, seg_path, progress, wid):
    # resume: skip bytes already in seg file
    have = os.path.getsize(seg_path) if os.path.exists(seg_path) else 0
    pos = abs_start + have
    mode = "ab" if have else "wb"
    with open(seg_path, mode) as f:
        while pos < abs_end:
            idx = vf._part_index(pos)
            part_lo = pos - vf.starts[idx]
            part_hi = min(vf.starts[idx] + vf.sizes[idx], abs_end) - vf.starts[idx]
            # fetch in CHUNK pieces
            while part_lo < part_hi:
                step = min(CHUNK, part_hi - part_lo)
                data = vf._fetch(idx, int(part_lo), int(part_lo + step))
                f.write(data)
                f.flush()
                part_lo += step
                pos += step
                progress[wid] = progress.get(wid, 0) + len(data)


def main():
    start, end, nworkers, outdir = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
    os.makedirs(outdir, exist_ok=True)
    total = end - start
    seg = total // nworkers
    vf = vfile.PartVirtualFile(dl.ASSETS[:26])
    # pre-resolve all part urls once (fast api calls)
    for i in range(26):
        vf._url(i)
    print(f"[seg] {total / 1e9:.2f}GB in {nworkers} workers", flush=True)
    progress = {}
    threads = []
    t0 = time.time()
    for w in range(nworkers):
        s = start + w * seg
        e = start + (w + 1) * seg if w < nworkers - 1 else end
        seg_path = os.path.join(outdir, f"seg_{w:02d}.bin")
        th = threading.Thread(target=worker, args=(vf, s, e, seg_path, progress, w),
                              daemon=True)
        th.start()
        threads.append(th)
    last = 0
    while any(th.is_alive() for th in threads):
        time.sleep(10)
        done = sum(progress.values())
        dt = time.time() - t0
        rate = (done - last) / 10 / 1e6
        print(f"[seg] {done / 1e9:.2f}/{total / 1e9:.2f}GB "
              f"({100 * done / total:.1f}%) {rate:.2f}MB/s agg", flush=True)
        last = done
    for th in threads:
        th.join()
    dt = time.time() - t0
    done = sum(os.path.getsize(os.path.join(outdir, f"seg_{w:02d}.bin")) for w in range(nworkers))
    print(f"[seg] done {done} bytes in {dt:.0f}s ({done / dt / 1e6:.2f}MB/s avg)", flush=True)


if __name__ == "__main__":
    main()
