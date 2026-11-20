#!/usr/bin/env python3
"""WH Kaggle GPU batch job: GPU-accelerated moveset analytics (READY, NOT RUN).

Status honesty, stated at the top so nobody mistakes it:
- The GPU path (cuDF) has NOT run on this VM: the VM has no NVIDIA GPU.
- It is written to run on the Kaggle notebook (2x Tesla T4, CUDA 13.0,
  https://www.kaggle.com/code/marsfmmg/notebook2ff3176461/edit) where
  cuDF/RAPIDS is installable via pip/conda.
- The CPU fallback (pandas) runs anywhere and proves the LOGIC on this VM;
  it does not prove GPU speed. GPU speed is proven only when a Kaggle run
  reports its own timings.
- Parent browser delegation needed: paste this file into one Kaggle
  notebook cell (or upload + run) with GPU T4 x2 enabled, and record the
  printed timings + nvidia-smi output.

What it does (same job, GPU or CPU):
- Loads every t7-*.json moveset in a directory.
- Counts moves, null-damage gaps, and per-hit-level totals.
- The cuDF path does the groupby on GPU memory (pandas-compatible API,
  zero code change in spirit: same operations, different engine).

Kaggle cell setup (run first in the notebook):
  !pip install -q cudf-cu12 pandas   # cudf-cu12 matches CUDA 12 wheels
  # then upload this file + the t7-all JSONs, or paste the code below
"""

import glob
import json
import os
import sys
import time

MOVE_DIR = os.environ.get("WH_MOVES_DIR", "t7-all")


def load_moves(directory):
    rows = []
    for path in sorted(glob.glob(os.path.join(directory, "t7-*.json"))):
        data = json.load(open(path))
        char = data.get("source", {}).get("character", os.path.basename(path))
        for move in data.get("moves", []):
            rows.append({
                "character": char,
                "notation_lp": move.get("notation_lp") or "",
                "hit_level": move.get("hit_level") or "MISSING",
                "damage_null": 1 if move.get("damage") is None else 0,
            })
    return rows


def run_cpu(rows):
    # Stdlib-only fallback: no pandas required. (This VM's system pandas is
    # broken against its numpy: "numpy.dtype size changed" binary
    # incompatibility, so the fallback must not depend on it.)
    from collections import Counter
    t0 = time.perf_counter()
    chars = Counter(r["character"] for r in rows)
    gaps = sum(r["damage_null"] for r in rows)
    top_levels = Counter(r["hit_level"] for r in rows).most_common(5)
    elapsed = time.perf_counter() - t0
    return {"engine": "stdlib-CPU", "rows": len(rows), "chars": len(chars),
            "null_damage_gaps": gaps, "elapsed_sec": round(elapsed, 3),
            "top_hit_levels": dict(top_levels)}


def run_gpu(rows):
    import cudf
    df = cudf.DataFrame(rows)
    t0 = time.perf_counter()
    by_char = df.groupby("character").size()
    gaps = int(df["damage_null"].sum())
    top_levels = df.groupby("hit_level").size().sort_values(ascending=False).head(5)
    elapsed = time.perf_counter() - t0
    return {"engine": "cuDF-GPU", "rows": len(df), "chars": len(by_char),
            "null_damage_gaps": gaps, "elapsed_sec": round(elapsed, 3),
            "top_hit_levels": top_levels.to_dict()}


def main():
    rows = load_moves(MOVE_DIR)
    print("loaded %d move rows from %s" % (len(rows), MOVE_DIR))
    try:
        import cudf  # noqa: F401
        print(run_gpu(rows))
    except ImportError:
        print("cuDF not available here (no GPU on this box) -> CPU fallback:")
        print(run_cpu(rows))
        print("TO PROVE GPU SPEED: run this file on Kaggle T4 and record "
              "the cuDF-GPU elapsed_sec + nvidia-smi output.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
