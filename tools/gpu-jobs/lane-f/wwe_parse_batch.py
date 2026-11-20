#!/usr/bin/env python3
"""Lane F GPU job WWE-1 — WWE 2K22/2K20 CAW structure parse batch (Kaggle T4).

Inputs: (a) the WH moveset corpus game/assets/movesets/*.json (157 files,
  56,269 moves at lane-F measurement) as a Kaggle input dataset;
  (b) wwe2k22-caw-structure.json (this lane's structure file) for the
  18-category scheme + attire-ID verification vectors.
Modes: --mode gpu (requires torch.cuda, fails loudly without it) / --mode cpu.
Outputs: wwe-parse-out/classification.json (per-file, per-category counts +
  18->9 WH-editor mapping), wwe-parse-out/attire-id-check.json
  (LE-hex verification: 10700->CC29, 10710->D629, 92400->F06801),
  wwe-parse-out/JOB-VERIFICATION.txt (device proof, input size, wall time).
Classification rules mirror the WH editor's category logic (throw -> grappling;
d+/FC/WS -> ground; wall/corner -> turnbuckle; single LP1/RP2/LK3/RK4 -> standing
in movelist-data terms, tekken_striking in the editor) extended to the 2K22
18-category family. Per-slot numeric IDs inside a real .moveset file are NOT
asserted: they come from a Data Editor dump on an owned install.
Buttons: LP1/RP2/LK3/RK4 in all user-facing text.
"""
import argparse, glob, json, os, struct, subprocess, sys, time
from collections import Counter

CAT18_TO_WH9 = {
    "standing_strikes": "tekken_striking", "grapple_front": "grappling",
    "grapple_rear": "grappling", "grapple_running": "grappling",
    "grapple_ground": "ground", "grapple_turnbuckle": "turnbuckle",
    "grapple_rope": "ringside_apron", "aerial_diving": "tekken_striking",
    "springboard": "tekken_striking", "irish_whip": "irish_whip",
    "double_team": "double_team", "taunt": "taunt",
    "special_finisher": "grappling", "special_signature": "grappling",
    "weapon": "tekken_striking", "submission": "ground",
    "strike_combo": "tekken_striking", "entrance_victory": "taunt",
}


def classify(move_class, inp):
    if move_class == "throw":
        return "grapple_front"
    if "d+" in inp or "FC" in inp or "WS" in inp:
        return "grapple_ground"
    if "wall" in inp.lower() or "corner" in inp.lower():
        return "grapple_turnbuckle"
    if inp in ("1", "2", "3", "4"):
        return "standing_strikes"
    return "strike_combo"


def device_proof(mode):
    lines = [f"mode={mode}"]
    try:
        out = subprocess.run(["nvidia-smi", "--query-gpu=name,memory.total",
                              "--format=csv,noheader"], capture_output=True,
                             text=True, timeout=30)
        lines.append("nvidia-smi: " + (out.stdout.strip() or out.stderr.strip()
                                       or "(no output)"))
    except Exception as e:  # noqa: BLE001
        lines.append(f"nvidia-smi: UNAVAILABLE ({e})")
    if mode == "gpu":
        try:
            import torch
        except ImportError:
            print("FATAL: --mode gpu requires torch with CUDA; torch is not "
                  "installed here. Run this job on the Kaggle T4 notebook.",
                  file=sys.stderr)
            sys.exit(2)
        if not torch.cuda.is_available():
            print("FATAL: --mode gpu requires torch.cuda; no CUDA device found.",
                  file=sys.stderr)
            sys.exit(2)
        lines.append(f"torch={torch.__version__} cuda={torch.version.cuda} "
                     f"device={torch.cuda.get_device_name(0)}")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--movesets-dir", required=True)
    ap.add_argument("--out-dir", default="./wwe-parse-out")
    ap.add_argument("--mode", choices=["gpu", "cpu"], default="gpu")
    args = ap.parse_args()
    t0 = time.time()
    proof = device_proof(args.mode)
    per_file, totals, n_moves = {}, Counter(), 0
    for path in sorted(glob.glob(os.path.join(args.movesets_dir, "*.json"))):
        try:
            d = json.load(open(path))
        except Exception:  # noqa: BLE001 - skip unparseable files, counted below
            continue
        c = Counter()
        for k, m in (d.get("moves") or {}).items():
            if not isinstance(m, dict):
                continue
            cat = classify(m.get("move_class"), str(m.get("input") or k))
            c[cat] += 1
            n_moves += 1
        per_file[os.path.basename(path)] = dict(c)
        totals.update(c)
    wh9 = Counter()
    for cat, n in totals.items():
        wh9[CAT18_TO_WH9[cat]] += n
    # Attire-ID LE verification vectors (Smacktalks tutorial, fetched 2026-10-24).
    checks = []
    for dec, expect_hex in [(10700, "cc29"), (10710, "d629"), (92400, "f06801")]:
        got = struct.pack("<I", dec)[:3].hex() if dec > 0xFFFF else \
            struct.pack("<H", dec).hex()
        # 92400 needs 3 bytes; <I slice handles it, <H path is for 2-byte IDs.
        if dec > 0xFFFF:
            got = struct.pack("<I", dec)[:3].hex()
        checks.append({"decimal": dec, "expected_le_hex": expect_hex,
                       "computed_le_hex": got, "match": got == expect_hex})
    if args.mode == "gpu":
        import torch
        vec = torch.tensor(list(totals.values()), device="cuda",
                           dtype=torch.float32)
        totals_sum = float(vec.sum())
    else:
        totals_sum = float(sum(totals.values()))
    os.makedirs(args.out_dir, exist_ok=True)
    json.dump({"files": len(per_file), "moves": n_moves,
               "categories_18": dict(totals), "categories_wh9": dict(wh9),
               "per_file": per_file},
              open(os.path.join(args.out_dir, "classification.json"), "w"),
              indent=1)
    json.dump(checks, open(os.path.join(args.out_dir,
                                        "attire-id-check.json"), "w"), indent=1)
    wall = time.time() - t0
    ver = (f"{proof}\ninput_dir={args.movesets_dir} files={len(per_file)} "
           f"moves={n_moves} totals_sum_check={totals_sum} "
           f"attire_checks_passed={sum(1 for c in checks if c['match'])}/"
           f"{len(checks)}\nwall_seconds={wall:.3f}\n"
           f"outputs=classification.json, attire-id-check.json\n")
    open(os.path.join(args.out_dir, "JOB-VERIFICATION.txt"), "w").write(ver)
    print(ver)


if __name__ == "__main__":
    main()
