#!/usr/bin/env python3
"""Survey KoC2 MVS motion files (kc2firemvs/fileNNNNN.bin).

Structural findings (2026-11-19, lane W2) — see MVS-FORMAT.md:
  * 16,660 files, but only 8,205 distinct contents (heavy duplication:
    shared motions stored per (wrestler, move) slot, max 36 copies).
  * Two families by bytes 2-3: A = (0x00,0x02), 15,822 files;
    B = (0x01,0x00), 838 files, much larger on average.
  * Byte 1 correlates with file size at r=0.83 (dominant combo):
    size ~= 596 + 16.1 * byte1 — byte 1 is very likely a frame
    (or keyframe) count, 5..255.
  * All sampled files end with a 0x00 byte (bitstream zero padding).
  * No size alignment (mod 4 uniform) — consistent with a bitstream.

Usage: koc2_mvs_survey.py [mvs_dir] — prints family/header stats.
"""
import glob
import hashlib
import os
import statistics
import sys
from collections import Counter, defaultdict


def survey(mvs_dir):
    files = sorted(glob.glob(os.path.join(mvs_dir, "file*.bin")))
    print(f"MVS files: {len(files)}")
    fams = Counter()
    combos = Counter()
    sizes = []
    hashes = Counter()
    for f in files:
        d = open(f, "rb").read()
        sizes.append(len(d))
        hashes[hashlib.md5(d).hexdigest()] += 1
        fams[(d[2], d[3])] += 1
        combos[(d[0], d[2], d[3], d[4], d[6], d[7])] += 1
    print(f"distinct contents: {len(hashes)} "
          f"(max copies of one motion: {max(hashes.values())})")
    print(f"sizes: min={min(sizes)} max={max(sizes)} "
          f"mean={statistics.mean(sizes):.0f} median={statistics.median(sizes):.0f}")
    print(f"families (bytes 2-3): {fams}")
    print("top header combos (off0,off2,off3,off4,off6,off7):")
    for k, v in combos.most_common(8):
        print(f"  {[hex(x) for x in k]}: {v}")
    # frame-count correlation in the dominant combo
    xs, ys = [], []
    for f in files:
        d = open(f, "rb").read()
        if d[0] == 0x6B and d[4] == 0 and d[6] == 2 and d[7] == 0x10:
            xs.append(d[1])
            ys.append(len(d))
    n = len(xs)
    mx, my = statistics.mean(xs), statistics.mean(ys)
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / n
    r = cov / (statistics.pstdev(xs) * statistics.pstdev(ys))
    b = cov / statistics.pstdev(xs) ** 2
    print(f"dominant combo n={n}: corr(byte1, size)={r:.3f}; "
          f"size ~= {my - b * mx:.0f} + {b:.1f}*byte1")


if __name__ == "__main__":
    survey(sys.argv[1] if len(sys.argv) > 1 else ".")
