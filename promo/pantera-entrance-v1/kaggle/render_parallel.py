#!/usr/bin/env python3
"""render_parallel.py — Split a Blender render across N parallel Kaggle kernels.

Uses the v4 notebook (gen_notebook_v4.py) with FRAME_START/FRAME_END injected
via pre_cells. Each split renders its own frame range on a separate T4.

Usage:
  # Split 1500 frames across 2 kernels (~30 min wall time)
  python3 render_parallel.py --frames 0-1499 --splits 2 --title "pantera-v4"

  # Split across 3 kernels (~20 min wall time)
  python3 render_parallel.py --frames 0-1499 --splits 3 --title "pantera-v4"

  # Dry run (show splits without queueing)
  python3 render_parallel.py --frames 0-1499 --splits 2 --dry-run

How it works:
  1. Splits the frame range into N contiguous chunks
  2. Adds N jobs to kaggle_queue with pre_cells setting FRAME_START/FRAME_END
  3. Queue runs up to max_parallel jobs concurrently (set in kaggle-queue.json)
  4. Each job outputs pantera_v4_f{START:05d}-{END:05d}.zip
  5. Use merge_splits.py to combine the zips after all complete

Quota note: N parallel kernels burn quota Nx faster but finish in ~1/N the time.
Total GPU-minutes is the same. Only use parallel when wall-clock speed matters.
"""
import argparse
import json
import os
import sys
import uuid
from datetime import datetime, timezone

sys.path.insert(0, os.path.expanduser("~/workspace/tools/kaggle-queue"))
# Import queue functions without running main
import importlib.util
spec = importlib.util.spec_from_file_location(
    "kq", os.path.expanduser("~/workspace/tools/kaggle-queue/kaggle_queue.py"))
kq = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kq)

NOTEBOOK = os.path.expanduser(
    "~/workspace/kaggle-pantera-render/pantera_kaggle_render_v4.ipynb")
QUEUE_FILE = os.path.expanduser("~/workspace/agent-ops/kaggle-queue.json")
OUTPUT_BASE = os.path.expanduser("~/workspace/kaggle-queue-output")


def parse_range(s):
    a, b = s.split("-")
    return int(a), int(b)


def split_range(f0, f1, n):
    total = f1 - f0 + 1
    base = total // n
    rem = total % n
    splits = []
    cur = f0
    for i in range(n):
        size = base + (1 if i < rem else 0)
        splits.append((cur, cur + size - 1))
        cur += size
    return splits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frames", default="0-1499",
                    help="Frame range, e.g. 0-1499")
    ap.add_argument("--splits", type=int, default=2,
                    help="Number of parallel kernels")
    ap.add_argument("--title", default="pantera-v4",
                    help="Job title prefix")
    ap.add_argument("--datasets", default="",
                    help="Comma-separated Kaggle dataset slugs to attach")
    ap.add_argument("--dry-run", action="store_true",
                    help="Show splits without queueing")
    ap.add_argument("--max-parallel", type=int, default=None,
                    help="Set queue max_parallel (default: leave unchanged)")
    args = ap.parse_args()

    if not os.path.exists(NOTEBOOK):
        print(f"ERROR: v4 notebook not found: {NOTEBOOK}")
        print("Run gen_notebook_v4.py first.")
        sys.exit(1)

    f0, f1 = parse_range(args.frames)
    splits = split_range(f0, f1, args.splits)
    group_id = f"par-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"

    print(f"Parallel render: {args.splits} splits, frames {f0}-{f1}")
    print(f"Group ID: {group_id}")
    for i, (s0, s1) in enumerate(splits):
        print(f"  split {i}: frames {s0}-{s1} ({s1 - s0 + 1} frames)")

    if args.dry_run:
        print("\n(dry run — nothing queued)")
        return

    # Optionally set max_parallel
    q = kq.load_queue()
    if args.max_parallel is not None:
        q["max_parallel"] = args.max_parallel
        print(f"\nqueue max_parallel set to {args.max_parallel}")
    elif "max_parallel" not in q:
        q["max_parallel"] = args.splits
        print(f"\nqueue max_parallel set to {args.splits} (matches splits)")
    else:
        print(f"\nqueue max_parallel already {q['max_parallel']}")

    # Add one job per split
    for i, (s0, s1) in enumerate(splits):
        job_id = f"{group_id}-s{i}"
        pre_cells = [
            f"# === PARALLEL SPLIT {i} (injected by render_parallel.py) ===\n"
            f"FRAME_START = {s0}\n"
            f"FRAME_END = {s1}\n"
            f'print(f\"parallel split {i}: frames {{FRAME_START}}-{{FRAME_END}}\")\n'
        ]
        job = {
            "id": job_id,
            "title": f"{args.title} split {i}/{args.splits} (f{s0:05d}-{s1:05d})",
            "notebook_path": NOTEBOOK,
            "status": "pending",
            "gpu": True,
            "internet": True,
            "datasets": [d for d in args.datasets.split(",") if d],
            "pre_cells": pre_cells,
            "output_dir": os.path.join(OUTPUT_BASE, job_id),
            "expected_outputs": [f"pantera_v4_f{s0:05d}-{s1:05d}.zip"],
            "group": group_id,
            "group_size": args.splits,
            "group_index": i,
            "frame_start": s0,
            "frame_end": s1,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        q.setdefault("jobs", []).append(job)
        print(f"  queued: {job_id}")

    kq.save_queue(q)
    print(f"\n{args.splits} jobs queued in group {group_id}")
    print("The queue will run up to max_parallel concurrently.")
    print(f"Monitor: python3 ~/workspace/tools/kaggle-queue/kaggle_queue.py status")
    print(f"After all complete, merge with:")
    print(f"  python3 ~/workspace/kaggle-pantera-render/merge_splits.py --group {group_id}")


if __name__ == "__main__":
    main()
