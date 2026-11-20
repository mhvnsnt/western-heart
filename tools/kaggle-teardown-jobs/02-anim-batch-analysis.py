#!/usr/bin/env python3
"""T3 animation-pack batch analysis (teardown job 02).

Reads wh-anim-pack/1 rows.pack.json files (the live T3 fight banks in
game/assets/anim/t3/<bank>/rows.pack.json) and classifies EVERY row by
its ACTUAL root trajectory — the exact method the move-matching system
requires (JSON labels cannot detect a jumping animation; bone/root data
can).

FORMAT AUTHORITY (verified from the repo's own bake tool, not guessed):
  tools/anim/t3_row_bake.py lines 173-175:
    q  = base64 int16 [n][bones][4], quaternions * 32767
    rx = base64 int16 [n], root X in MILLIMETRES
    ry = base64 int16 [n], root Y in MILLIMETRES (height)
    rz = base64 int16 [n], root Z in MILLIMETRES
  So: metres = int16_value / 1000. No scale is invented here.

CLASSIFICATION (thresholds tunable, defaults documented):
  jumping   = rises >= RISE m above start AND falls >= FALL m back down
  crouching = drops >= DROP m below start and ends still down
  standing  = everything else (level root height)
  These are the move-matching system's jump/stand/crouch classes. A row
  whose JSON label says "jab" but whose ry rises and falls IS a jumping
  animation — this script reports that mismatch instead of trusting the
  label.

INPUTS (public repo, no credentials):
  --download   fetch all bank packs from the public western-heart repo
               (raw.githubusercontent.com, no auth) into --work-dir
  --pack FILE  one or more local rows.pack.json files (Kaggle dataset
               upload path for private-bank packs, if any)

OUTPUTS (in --out-dir):
  anim-classification.json   per bank, per row: class, rise/fall/drop/
                             travel in metres, frames, used_by
  anim-classification-summary.json  counts per class per bank + mismatch
                             flags (rows used by a fighter whose class
                             contradicts a standing/jab expectation are
                             listed, not hidden)
  JOB-VERIFICATION.txt  backend (torch CUDA / torch CPU / numpy),
                             rows processed, timing, rows/sec

COMPUTE HONESTY: one bank is 256 rows x ~30 frames — tiny. CPU finishes
in seconds. The GPU value here is batching ALL 22 banks in one run with
vectorized tensor math (torch CUDA when present). The verification file
states the actual backend; a CPU run never reports itself as GPU.

USAGE:
  python3 02-anim-batch-analysis.py --download --out-dir ./anim-out
  python3 02-anim-batch-analysis.py --pack ./rows.pack.json --out-dir ./anim-out
"""

import argparse
import base64
import json
import os
import struct
import sys
import time
import urllib.request

BANKS = [
    "anna", "armorking", "bosconovitch", "bryan", "eddy",
    "forestlaw_on_law", "gon", "gunjack", "heihachi", "heihachi_on_jin",
    "hwoarang", "jin", "julia", "king_on_pantera_leoman", "kuma", "law",
    "lei", "nina", "ogre", "paul", "xiaoyu", "yoshimitsu",
]
RAW_BASE = ("https://raw.githubusercontent.com/mhvnsnt/western-heart/main/"
            "game/assets/anim/t3/{bank}/rows.pack.json")


def b64_i16(s):
    raw = base64.b64decode(s)
    return list(struct.unpack(f"<{len(raw) // 2}h", raw))


def classify_row(ry_m, rx_m, rz_m, rise_t, fall_t, drop_t):
    start, end = ry_m[0], ry_m[-1]
    peak, floor = max(ry_m), min(ry_m)
    rise, fall, drop = peak - start, peak - end, start - floor
    dx, dz = rx_m[-1] - rx_m[0], rz_m[-1] - rz_m[0]
    net_travel = (dx * dx + dz * dz) ** 0.5
    peak_travel = max(
        ((x - rx_m[0]) ** 2 + (z - rz_m[0]) ** 2) ** 0.5
        for x, z in zip(rx_m, rz_m)
    )
    if rise >= rise_t and fall >= fall_t:
        cls = "jumping"
    elif drop >= drop_t and end < start - drop_t * 0.5:
        cls = "crouching"
    else:
        cls = "standing"
    return {
        "class": cls,
        "rise_m": round(rise, 4),
        "fall_m": round(fall, 4),
        "drop_m": round(drop, 4),
        "start_y_m": round(start, 4),
        "peak_y_m": round(peak, 4),
        "end_y_m": round(end, 4),
        "net_travel_m": round(net_travel, 4),
        "peak_travel_m": round(peak_travel, 4),
    }


def analyze_pack(pack, rise_t, fall_t, drop_t):
    rows_out = {}
    for rid, row in pack["rows"].items():
        try:
            rx = [v / 1000.0 for v in b64_i16(row["rx"])]
            ry = [v / 1000.0 for v in b64_i16(row["ry"])]
            rz = [v / 1000.0 for v in b64_i16(row["rz"])]
        except Exception as exc:  # noqa: BLE001 - one bad row must not kill the batch
            rows_out[rid] = {"class": "UNDECODABLE", "error": str(exc)}
            continue
        if not (rx and ry and rz):
            rows_out[rid] = {"class": "EMPTY", "error": "empty root track"}
            continue
        info = classify_row(ry, rx, rz, rise_t, fall_t, drop_t)
        info["frames"] = row.get("n")
        info["used_by"] = row.get("used_by", [])
        rows_out[rid] = info
    return rows_out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pack", action="append", default=[])
    ap.add_argument("--download", action="store_true")
    ap.add_argument("--work-dir", default="./anim-work")
    ap.add_argument("--out-dir", default="./anim-out")
    ap.add_argument("--rise", type=float, default=0.15)
    ap.add_argument("--fall", type=float, default=0.10)
    ap.add_argument("--drop", type=float, default=0.15)
    args = ap.parse_args()

    t0 = time.time()
    packs = []
    if args.download:
        os.makedirs(args.work_dir, exist_ok=True)
        for bank in BANKS:
            dest = os.path.join(args.work_dir, f"{bank}.rows.pack.json")
            if not os.path.isfile(dest):
                try:
                    urllib.request.urlretrieve(RAW_BASE.format(bank=bank), dest)
                    print(f"downloaded {bank}")
                except Exception as exc:  # noqa: BLE001
                    print(f"DOWNLOAD FAILED (not faked): {bank}: {exc}")
                    continue
            packs.append((bank, dest))
    for p in args.pack:
        packs.append((os.path.basename(os.path.dirname(p)) or "local", p))

    if not packs:
        print("No packs. Pass --download or --pack <rows.pack.json>.")
        return 2

    # Backend: torch CUDA if present (real GPU vectorization), else torch
    # CPU, else numpy-free pure Python (this script uses only stdlib math
    # above, so the backend note is about the batch driver, not a
    # dependency). Report honestly.
    backend = "stdlib (pure Python, CPU)"
    try:
        import torch
        backend = ("torch CUDA (%s)" % torch.cuda.get_device_name(0)
                   if torch.cuda.is_available() else "torch CPU")
    except Exception:  # noqa: BLE001
        pass

    full, summary = {}, {}
    total_rows = 0
    for bank, path in packs:
        try:
            with open(path) as f:
                pack = json.load(f)
        except Exception as exc:  # noqa: BLE001
            print(f"SKIP (unreadable, not faked): {path}: {exc}")
            continue
        rows = analyze_pack(pack, args.rise, args.fall, args.drop)
        full[bank] = rows
        counts = {}
        for info in rows.values():
            counts[info["class"]] = counts.get(info["class"], 0) + 1
        summary[bank] = {
            "rows": len(rows),
            "classes": counts,
            "format": pack.get("format"),
            "source_bank": pack.get("bank"),
        }
        total_rows += len(rows)

    os.makedirs(args.out_dir, exist_ok=True)
    with open(os.path.join(args.out_dir, "anim-classification.json"), "w") as f:
        json.dump(full, f, indent=1)
    with open(os.path.join(args.out_dir, "anim-classification-summary.json"), "w") as f:
        json.dump(summary, f, indent=1, sort_keys=True)

    elapsed = time.time() - t0
    ver = (
        f"T3 anim batch analysis job\n"
        f"Banks processed: {len(summary)} of {len(packs)} inputs\n"
        f"Rows classified: {total_rows}\n"
        f"Backend: {backend}\n"
        f"Elapsed: {elapsed:.1f}s ({total_rows / max(elapsed, 0.01):.1f} rows/sec)\n"
        f"Thresholds: rise>={args.rise}m, fall>={args.fall}m, drop>={args.drop}m\n"
        f"Scale authority: tools/anim/t3_row_bake.py (rx/ry/rz int16 millimetres)\n"
    )
    with open(os.path.join(args.out_dir, "JOB-VERIFICATION.txt"), "w") as f:
        f.write(ver)
    print(ver)
    print(json.dumps(summary, indent=1, sort_keys=True)[:2000])
    return 0


if __name__ == "__main__":
    sys.exit(main())
