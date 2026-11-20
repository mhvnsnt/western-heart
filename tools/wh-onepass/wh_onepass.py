#!/usr/bin/env python3
"""WH one-pass batch validator: speed + quality + caching in a single run.

One command validates every T7 moveset JSON in a directory, in parallel,
skipping files whose content hash has not changed since the last run.

Design (why this shape, not a fancier framework):
- Parallel engine: joblib if installed, else stdlib concurrent.futures.
  joblib is an accelerator, never a hard requirement, so this script runs
  on a bare CI runner with zero installs.
- Cache: SHA-256 of each file. Unchanged file -> result reused, no rework.
  This is the same idea as ccache/Turborepo (hash-keyed reuse), applied
  to game data instead of compiler outputs.
- Checks are grounded in the real T7 data shape (measured 2026-10-24 on
  35 files / 5,648 moves):
  - every move carries notation_lp (LP1/RP2/LK3/RK4 format)
  - damage is a string or None; None is a REAL GAP, reported, never filled
  - hit_level is a raw string (h/m/l/Sm/TJ/TC/throws/stance tags, ...) or
    None; it is NOT a small enum, so no enum assertion is made
  - notation_lp must equal notation_original with digits 1-4 replaced by
    LP1/RP2/LK3/RK4 (0 mismatches across all 5,648 moves on 2026-10-24)
- Exit code: 0 when no errors; 1 when any file has errors. Warnings
  (null damage gaps, notation mismatches, duplicates) never fail the run,
  they are reported honestly.

Usage:
  python3 wh_onepass.py --dir ~/workspace/mvlt-community-pull/t7-all
  python3 wh_onepass.py --dir <dir> --sequential        # timing comparison
  python3 wh_onepass.py --dir <dir> --report report.json
  python3 wh_onepass.py --dir <dir> --no-cache          # force full rework
"""

import argparse
import hashlib
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor

BUTTON_MAP = {"1": "LP1", "2": "RP2", "3": "LK3", "4": "RK4"}

import re

_DIGIT_RE = re.compile(r"(?<![A-Za-z0-9])([1234])(?![0-9])")


def expected_notation_lp(notation_original):
    """Digit -> LP1/RP2/LK3/RK4 replacement, exactly as the converter does."""
    if not notation_original:
        return ""
    return _DIGIT_RE.sub(lambda m: BUTTON_MAP[m.group(1)], notation_original)


def validate_move(move):
    """Validate one move record. Returns (errors, warnings, null_damage)."""
    errors = []
    warnings = []
    null_damage = 0
    lp = move.get("notation_lp")
    if not isinstance(lp, str) or not lp.strip():
        errors.append("missing notation_lp")
    else:
        orig = move.get("notation_original")
        if isinstance(orig, str) and orig:
            if expected_notation_lp(orig) != lp:
                warnings.append("notation_lp mismatch vs notation_original")
    dmg = move.get("damage")
    if dmg is None:
        null_damage = 1  # real gap: reported, NEVER filled with a guess
    elif not isinstance(dmg, str):
        errors.append("damage not str-or-None: %r" % type(dmg).__name__)
    hl = move.get("hit_level")
    if hl is not None and not isinstance(hl, str):
        errors.append("hit_level not str-or-None")
    return errors, warnings, null_damage


def validate_file(path):
    """Validate one moveset JSON file. Returns a summary dict."""
    with open(path, "rb") as fh:
        raw = fh.read()
    sha = hashlib.sha256(raw).hexdigest()
    try:
        data = json.loads(raw.decode("utf-8"))
    except Exception as exc:  # noqa: BLE001 - report, don't crash the batch
        return {"file": os.path.basename(path), "sha256": sha,
                "error": "unparseable JSON: %s" % exc}
    moves = data.get("moves", [])
    if not isinstance(moves, list):
        return {"file": os.path.basename(path), "sha256": sha,
                "error": "moves is not a list"}
    errors = 0
    warnings = 0
    null_damage = 0
    seen = set()
    dupes = 0
    for move in moves:
        if not isinstance(move, dict):
            errors += 1
            continue
        errs, warns, nd = validate_move(move)
        errors += len(errs)
        warnings += len(warns)
        null_damage += nd
        lp = move.get("notation_lp")
        if isinstance(lp, str):
            if lp in seen:
                dupes += 1
            seen.add(lp)
    return {"file": os.path.basename(path), "sha256": sha,
            "moves": len(moves), "errors": errors, "warnings": warnings,
            "null_damage_gaps": null_damage, "duplicate_notations": dupes}


def _run_parallel(paths, workers):
    try:
        from joblib import Parallel, delayed
        return Parallel(n_jobs=workers)(delayed(validate_file)(p) for p in paths)
    except ImportError:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            return list(pool.map(validate_file, paths))


def _run_sequential(paths):
    return [validate_file(p) for p in paths]


def main(argv=None):
    ap = argparse.ArgumentParser(description="WH one-pass moveset validator")
    ap.add_argument("--dir", required=True, help="directory of *.json movesets")
    ap.add_argument("--workers", type=int, default=os.cpu_count() or 2)
    ap.add_argument("--sequential", action="store_true")
    ap.add_argument("--no-cache", action="store_true")
    ap.add_argument("--cache", default=None,
                    help="cache JSON path (default: <dir>/.wh-onepass-cache.json)")
    ap.add_argument("--report", default=None, help="write JSON report here")
    args = ap.parse_args(argv)

    paths = sorted(p for p in os.listdir(args.dir) if p.endswith(".json"))
    paths = [os.path.join(args.dir, p) for p in paths]
    cache_path = args.cache or os.path.join(args.dir, ".wh-onepass-cache.json")
    cache = {}
    if not args.no_cache and os.path.exists(cache_path):
        try:
            cache = json.load(open(cache_path))
        except Exception:  # noqa: BLE001 - corrupt cache means full rework
            cache = {}

    # Hash pass (cheap): decide what actually needs work.
    todo = []
    reused = []
    for path in paths:
        sha = hashlib.sha256(open(path, "rb").read()).hexdigest()
        hit = cache.get(os.path.basename(path))
        if not args.no_cache and hit and hit.get("sha256") == sha:
            reused.append(hit["result"])
        else:
            todo.append(path)

    t0 = time.perf_counter()
    if args.sequential:
        fresh = _run_sequential(todo)
        mode = "sequential"
    else:
        fresh = _run_parallel(todo, args.workers) if todo else []
        mode = "parallel(joblib-or-stdlib, workers=%d)" % args.workers
    elapsed = time.perf_counter() - t0

    results = reused + fresh
    if not args.no_cache:
        new_cache = {r["file"]: {"sha256": r["sha256"], "result": r}
                     for r in results}
        json.dump(new_cache, open(cache_path, "w"), indent=1, sort_keys=True)

    total_moves = sum(r.get("moves", 0) for r in results)
    total_errors = sum(r.get("errors", 0) for r in results)
    total_warnings = sum(r.get("warnings", 0) for r in results)
    total_gaps = sum(r.get("null_damage_gaps", 0) for r in results)
    total_dupes = sum(r.get("duplicate_notations", 0) for r in results)
    unparseable = [r["file"] for r in results if "error" in r]
    report = {"mode": mode, "elapsed_sec": round(elapsed, 3),
              "files_total": len(results), "files_validated": len(fresh),
              "files_cache_reused": len(reused),
              "moves_total": total_moves, "errors": total_errors,
              "warnings": total_warnings, "null_damage_gaps": total_gaps,
              "duplicate_notations": total_dupes,
              "unparseable_files": unparseable, "per_file": results}
    print("mode: %s | elapsed: %.3fs" % (mode, elapsed))
    print("files: %d total, %d validated, %d cache-reused"
          % (len(results), len(fresh), len(reused)))
    print("moves: %d | errors: %d | warnings: %d | null-damage gaps "
          "(reported, never filled): %d | duplicate notations: %d"
          % (total_moves, total_errors, total_warnings, total_gaps,
             total_dupes))
    if unparseable:
        print("unparseable: %s" % ", ".join(unparseable))
    if args.report:
        json.dump(report, open(args.report, "w"), indent=1, sort_keys=True)
        print("report: %s" % args.report)
    return 1 if (total_errors or unparseable) else 0


if __name__ == "__main__":
    sys.exit(main())
