#!/usr/bin/env python3
"""merge_splits.py — Merge parallel render split zips into one complete set.

After render_parallel.py splits complete, this downloads (if needed) and
merges the per-split zips into a single output directory with all frames.

Usage:
  python3 merge_splits.py --group par-20261016-120000
  python3 merge_splits.py --group par-20261016-120000 --output-dir ./pantera-final
"""
import argparse
import glob
import json
import os
import shutil
import sys
import zipfile

sys.path.insert(0, os.path.expanduser("~/workspace/tools/kaggle-queue"))
import importlib.util
spec = importlib.util.spec_from_file_location(
    "kq", os.path.expanduser("~/workspace/tools/kaggle-queue/kaggle_queue.py"))
kq = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kq)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--group", required=True, help="Parallel group ID")
    ap.add_argument("--output-dir", default=None,
                    help="Output dir (default: ~/workspace/kaggle-queue-output/<group>-merged)")
    args = ap.parse_args()

    q = kq.load_queue()
    jobs = [j for j in q.get("jobs", []) if j.get("group") == args.group]
    if not jobs:
        print(f"No jobs found for group {args.group}")
        sys.exit(1)

    jobs.sort(key=lambda j: j.get("group_index", 0))
    print(f"Group {args.group}: {len(jobs)} splits")

    # Check all done
    not_done = [j for j in jobs if j.get("status") != "done"]
    if not_done:
        print(f"WARNING: {len(not_done)} splits not done yet:")
        for j in not_done:
            print(f"  {j['id']}: {j.get('status')}")
        print("Merge will include only completed splits.")
    
    outdir = os.path.expanduser(args.output_dir or
                                f"~/workspace/kaggle-queue-output/{args.group}-merged")
    frames_dir = os.path.join(outdir, "frames")
    os.makedirs(frames_dir, exist_ok=True)

    total_frames = 0
    for j in jobs:
        if j.get("status") != "done":
            continue
        s0, s1 = j["frame_start"], j["frame_end"]
        expected_zip = f"pantera_v4_f{s0:05d}-{s1:05d}.zip"
        
        # Find the zip (in job's output_dir or /kaggle/working via API)
        job_out = os.path.expanduser(j.get("output_dir", ""))
        zpath = os.path.join(job_out, expected_zip)
        if not os.path.exists(zpath):
            # Try to find it in the downloaded outputs
            cands = glob.glob(os.path.join(job_out, "**", expected_zip), recursive=True)
            if cands:
                zpath = cands[0]
        
        if not os.path.exists(zpath):
            print(f"  split {j['group_index']}: zip not found locally ({expected_zip})")
            print(f"    (may need manual download via: kaggle kernels output {j.get('kernel_slug')})")
            continue
        
        with zipfile.ZipFile(zpath) as zf:
            names = [n for n in zf.namelist() if n.endswith(".png")]
            zf.extractall(frames_dir)
            total_frames += len(names)
            print(f"  split {j['group_index']}: {len(names)} frames from {os.path.basename(zpath)}")

    # Verify continuity
    frames = sorted(glob.glob(os.path.join(frames_dir, "f*.png")))
    print(f"\nTotal frames merged: {len(frames)}")
    if frames:
        fnums = sorted(int(os.path.basename(f)[1:6]) for f in frames)
        expected = list(range(fnums[0], fnums[-1] + 1))
        missing = set(expected) - set(fnums)
        if missing:
            print(f"WARNING: {len(missing)} frames missing: {sorted(missing)[:10]}...")
        else:
            print(f"Frame range {fnums[0]}-{fnums[-1]}: COMPLETE, no gaps ✓")
    
    print(f"\nMerged frames in: {frames_dir}")


if __name__ == "__main__":
    main()
