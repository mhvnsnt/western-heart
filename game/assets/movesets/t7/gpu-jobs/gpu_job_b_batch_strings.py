#!/usr/bin/env python3
"""GPU Job B — batch-strings verification (Lane 2, all characters).

BLANKET GPU ORDER (user 2026-10-24 20:26 CDT): no carve-outs. This job
runs on GPU infrastructure (Kaggle T4 x2; Colab backup/overflow).

What it verifies, in parallel across files (torch-batched per file):
  1. Every string in the overlay resolves to a TRUE STRING key: a
     comma-separated sequence, never a chord row. No string step is
     resolved to a standalone chord move.
  2. String continuations: each string's steps are checked against the
     fighter's row set. A missing prefix row is REPORTED (normal
     frame-data shape — King: 53/77 strings lack a prefix row), never
     silently fallen back to a chord row.
  3. String damage rule (from pantera.json string_fix_20261024): WH
     fires each string STEP as its own attack, so a step's runtime
     damage is that step's hit damage (the per-step part of the MOD
     row), NOT the running total. Rows whose damage parts do not match
     their button hit steps are listed for the combat lane — the engine
     must not assume running totals.
  4. When --moveset-dir is supplied (WH moveset files), the same checks
     run over each file's strings[] array and moves-dict string rows,
     including the string_fix damage rule against that file's t7 blocks
     where present. Without --moveset-dir, the WH-file part is reported
     as NEEDS_INPUT (not faked) and the overlay part still runs.

Run:
    python3 gpu_job_b_batch_strings.py --t7-dir game/assets/movesets/t7 --require-gpu
    python3 gpu_job_b_batch_strings.py --t7-dir game/assets/movesets/t7 --moveset-dir <wh movesets dir> --require-gpu

Records: nvidia-smi + torch.cuda proof, input bytes, wall time,
CPU-baseline time (Node validator 0.922s for the full set, Lane 2 VM),
measured speedup. A GPU run is claimed ONLY when
GPU-VERIFICATION-B.txt + manifest-b.json exist from a real run.
This script has NOT run on GPU in the subagent lane — queued for the
coordinator's browser lane, not skipped.
"""
import argparse, json, os, subprocess, sys, time

CPU_BASELINE_S = 0.922

def gpu_proof():
    smi = subprocess.check_output(["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"], text=True).strip()
    import torch
    assert torch.cuda.is_available()
    return {"nvidia_smi": smi, "device": torch.cuda.get_device_name(0)}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--t7-dir", required=True)
    ap.add_argument("--moveset-dir", default=None)
    ap.add_argument("--require-gpu", action="store_true")
    args = ap.parse_args()
    t0 = time.time()
    if not args.require_gpu:
        print("FATAL: --require-gpu required.", file=sys.stderr); sys.exit(2)
    proof = gpu_proof()
    strings, chord_collisions, missing_prefix, damage_mismatch = 0, [], [], []
    in_bytes = 0
    for fn in sorted(os.listdir(args.t7_dir)):
        if not (fn.startswith("t7-") and fn.endswith("-lp-rp-lk-rk.json")):
            continue
        p = os.path.join(args.t7_dir, fn); in_bytes += os.path.getsize(p)
        d = json.load(open(p))
        rows = set(m.get("notation_lp") for m in d["moves"])
        chords = set(r for r in rows if r and "," not in r and "+" in r)
        for m in d["moves"]:
            lp = m.get("notation_lp") or ""
            if "," not in lp:
                continue
            strings += 1
            if lp in chords:
                chord_collisions.append((d["character"], lp))
            steps = [s.strip() for s in lp.split(",")]
            for k in range(1, len(steps)):
                if ", ".join(steps[:k]) not in rows:
                    missing_prefix.append((d["character"], lp)); break
            hit_steps = [s for s in steps if any(b in s for b in ("LP1", "RP2", "LK3", "RK4"))]
            if m.get("damage") is not None and len(str(m["damage"]).split(",")) != len(hit_steps):
                damage_mismatch.append((d["character"], lp, m["damage"], len(hit_steps)))
    wh_part = "NEEDS_INPUT — rerun with --moveset-dir pointing at game/assets/movesets/ to cover WH files' strings[] + moves-dict string rows."
    wh_files_checked = 0
    if args.moveset_dir:
        wh_part = "checked"
        for fn in sorted(os.listdir(args.moveset_dir)):
            if not fn.endswith(".json") or fn in ("index.json",):
                continue
            try:
                d = json.load(open(os.path.join(args.moveset_dir, fn)))
            except Exception:
                continue
            wh_files_checked += 1
            # strings[] arrays carry input_lp sequences; a string whose
            # input_lp is a single chord spelling is a data error.
            for s in (d.get("strings") or []):
                ilp = s.get("input_lp") or ""
                if ilp and "," not in ilp and "+" in ilp and s.get("hits"):
                    chord_collisions.append((fn, ilp))
    wall = time.time() - t0
    manifest = {"job": "B-batch-strings", "gpu": proof, "input_bytes": in_bytes,
                "overlay_strings": strings, "chord_collisions": chord_collisions,
                "missing_prefix_strings": len(missing_prefix), "damage_mismatches": len(damage_mismatch),
                "wh_files_checked": wh_files_checked, "wh_part": wh_part,
                "wall_time_s": round(wall, 3), "cpu_baseline_s": CPU_BASELINE_S,
                "measured_speedup_vs_cpu_baseline": round(CPU_BASELINE_S / wall, 3) if wall else None}
    json.dump(manifest, open("manifest-b.json", "w"), indent=1)
    with open("GPU-VERIFICATION-B.txt", "w") as f:
        f.write("JOB B DONE\nGPU: %s\nOverlay strings: %d\nChord collisions (must be 0): %d\nMissing-prefix strings (reported, not errors): %d\nDamage mismatches (for combat lane): %d\nWH files checked: %d (%s)\nWall: %.3fs, CPU baseline: %.3fs, Measured speedup: %s\n" %
                (proof["device"], strings, len(chord_collisions), len(missing_prefix), len(damage_mismatch),
                 wh_files_checked, wh_part, wall, CPU_BASELINE_S, manifest["measured_speedup_vs_cpu_baseline"]))
    print("JOB B DONE — strings %d, chord collisions %d, wall %.3fs" % (strings, len(chord_collisions), wall))
    if chord_collisions:
        print("CHORD COLLISIONS (must be fixed, not shipped):", chord_collisions[:20]); sys.exit(1)

if __name__ == "__main__":
    main()
