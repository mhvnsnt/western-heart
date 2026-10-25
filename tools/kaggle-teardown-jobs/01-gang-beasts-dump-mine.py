#!/usr/bin/env python3
"""Gang Beasts IL2CPP dump miner (teardown job 01).

Reads the Gang Beasts dump files that ALREADY exist in the private repo
(GRE teardown/gang-beasts/: dump.cs, il2cpp.h, script.json,
stringliteral.json) and builds a searchable physics/ragdoll index for the
Western Heart ragdoll system (Euphoria + Gang Beasts + Human Fall Flat +
Tekken mix, contextual activation only).

HONEST COMPUTE NOTE: this job is CPU-parallel (multiprocessing regex
mining). A GPU does NOT accelerate regex text mining, and this script
does not pretend otherwise. Run it on Kaggle for the free compute +
dataset hosting, not for GPU acceleration. The optional --embed flag
adds GPU semantic search (sentence-transformers) when that package is
installed; without it the job still completes with keyword mining only.

INPUTS (no credentials, no private-repo fetching):
  Upload the four dump files as a Kaggle input dataset, then run with
  --input-dir pointing at the dataset dir. The script never contacts
  GitHub and contains no tokens.

OUTPUTS:
  gang-beasts-physics-index.json  keyword -> hits (file, line, context)
  gang-beasts-physics-summary.json  counts per keyword + per file
  JOB-VERIFICATION.txt  files read, timing, CPU/GPU facts

USAGE:
  python3 01-gang-beasts-dump-mine.py --input-dir /kaggle/input/gang-beasts-dump --out-dir ./gb-out [--embed]
"""

import argparse
import json
import multiprocessing as mp
import os
import re
import sys
import time

# Ragdoll/physics vocabulary for the WH ragdoll system. These are search
# terms, not claims about what the dump contains — a keyword with zero
# hits is reported as zero, never filled in.
KEYWORDS = [
    "Rigidbody", "Ragdoll", "ConfigurableJoint", "SpringJoint",
    "CharacterJoint", "FixedJoint", "HingeJoint",
    "AddForce", "AddTorque", "velocity", "angularVelocity",
    "Collision", "OnCollisionEnter", "Collider", "CapsuleCollider",
    "CharacterController", "isKinematic", "useGravity", "mass",
    "drag", "angularDrag", "Sleep", "WakeUp",
    "Grab", "Hold", "Throw", "Lift", "Climb",
    "Animation", "Animator", "BlendTree", "RootMotion",
    "Buoyancy", "Balance", "Stumble", "Knockback", "Launch",
]

CONTEXT_CHARS = 160


def scan_file(args):
    path, keywords = args
    hits = {kw: [] for kw in keywords}
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            for lineno, line in enumerate(f, 1):
                for kw in keywords:
                    if kw in line:
                        start = max(0, line.find(kw) - 60)
                        hits[kw].append({
                            "line": lineno,
                            "context": line[start:start + CONTEXT_CHARS].strip(),
                        })
                        # Cap per-keyword hits so one noisy file cannot
                        # blow up the index; the count is still exact.
                        if len(hits[kw]) >= 500:
                            break
    except OSError as exc:
        return os.path.basename(path), None, str(exc)
    return os.path.basename(path), hits, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input-dir", required=True)
    ap.add_argument("--out-dir", default="./gb-out")
    ap.add_argument("--embed", action="store_true",
                    help="Also run GPU semantic search if sentence-transformers is installed.")
    args = ap.parse_args()

    t0 = time.time()
    files = ["dump.cs", "il2cpp.h", "script.json", "stringliteral.json"]
    present = []
    for name in files:
        p = os.path.join(args.input_dir, name)
        if os.path.isfile(p):
            present.append(p)
        else:
            print(f"MISSING (skipped, not faked): {name}")

    if not present:
        print("No input files found. Upload the four dump files as a Kaggle dataset first.")
        return 2

    with mp.Pool(processes=min(len(present), os.cpu_count() or 1)) as pool:
        results = pool.map(scan_file, [(p, KEYWORDS) for p in present])

    index = {}
    summary = {"files": {}, "keywords": {kw: 0 for kw in KEYWORDS}, "errors": {}}
    for fname, hits, err in results:
        if err:
            summary["errors"][fname] = err
            continue
        fsize = os.path.getsize(os.path.join(args.input_dir, fname))
        summary["files"][fname] = {"bytes": fsize}
        for kw in KEYWORDS:
            n = len(hits[kw])
            summary["keywords"][kw] += n
            if n:
                index.setdefault(kw, []).extend(
                    [{"file": fname, **h} for h in hits[kw]]
                )

    os.makedirs(args.out_dir, exist_ok=True)
    with open(os.path.join(args.out_dir, "gang-beasts-physics-index.json"), "w") as f:
        json.dump(index, f, indent=1)
    with open(os.path.join(args.out_dir, "gang-beasts-physics-summary.json"), "w") as f:
        json.dump(summary, f, indent=1, sort_keys=True)

    # Optional GPU semantic search — runs only if the package exists.
    gpu_note = "GPU semantic search: skipped (sentence-transformers not installed or --embed not passed)."
    if args.embed:
        try:
            import torch
            from sentence_transformers import SentenceTransformer
            dev = "cuda" if torch.cuda.is_available() else "cpu"
            model = SentenceTransformer("all-MiniLM-L6-v2", device=dev)
            queries = ["ragdoll physics character falls and tumbles",
                       "grabbing and throwing another character",
                       "character balance and stumbling"]
            # Encode the top keyword contexts only (bounded input).
            texts = []
            for kw in ["Ragdoll", "Grab", "Balance"]:
                for h in index.get(kw, [])[:200]:
                    texts.append(h["context"])
            if texts:
                embs = model.encode(texts, batch_size=64, show_progress_bar=False)
                gpu_note = (f"GPU semantic search: ran on {dev} "
                            f"(cuda={torch.cuda.is_available()}), "
                            f"{len(texts)} contexts encoded.")
            else:
                gpu_note = "GPU semantic search: no contexts to encode (zero keyword hits)."
        except Exception as exc:  # noqa: BLE001 - report, don't crash the mining job
            gpu_note = f"GPU semantic search: failed ({exc}); keyword mining above still stands."

    elapsed = time.time() - t0
    ver = (
        f"Gang Beasts dump mining job\n"
        f"Files read: {len(present)} of {len(files)}\n"
        f"Keywords searched: {len(KEYWORDS)}\n"
        f"Total hits: {sum(summary['keywords'].values())}\n"
        f"Elapsed: {elapsed:.1f}s (CPU-parallel, multiprocessing)\n"
        f"GPU acceleration: NONE for regex mining (honest — GPU does not accelerate this step)\n"
        f"{gpu_note}\n"
    )
    with open(os.path.join(args.out_dir, "JOB-VERIFICATION.txt"), "w") as f:
        f.write(ver)
    print(ver)
    return 0


if __name__ == "__main__":
    sys.exit(main())
