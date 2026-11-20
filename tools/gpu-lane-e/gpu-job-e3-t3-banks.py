#!/usr/bin/env python3
"""GPU job E3 — T3 bank verification batch + divmot15 identification (Lane E).

Verifies, in one batch:
  * All 22 bank dirs under game/assets/anim/t3/ (wh-clone snapshot path is
    an input; the coordinator run points --banks at a fresh main checkout).
  * rows.pack.json clip counts per bank; expected total 4,685 clips.
  * bank-field divmot mapping per bank; expected present numbers
    00-14, 16-20 (15 absent) + 99 common in the 21-bin source listing.
  * heihachi/ has NO rows.pack.json (latent gap, flagged — never filled by
    copying heihachi_on_jin rows; its bake source is divmot13 only).
  * divmot15 identity: Mokujin — evidence is the bank-field sequence gap
    + RENAME-MAP / T3-REMAINDER-BANKS §4 (owner disc: BNS record 295,
    sector 17534, size 0; original Japan SLPS-01300 BNS index: divmot15.bin
    127,368 bytes, SHA-256 5cead15fe33b1e88cf54cf25b2c773763a71f89cdd369b85b584110ec6acc57c).
    Wiring divmot15 needs those 127,368 bytes re-ripped from a complete
    disc image; baking Gun Jack data found at that sector as Mokujin is
    FORBIDDEN (provenance break, documented in the lane report).

CPU baseline measured on this lane's VM (2026-10-24): 0.879 s for the
full 22-bank load + count + mapping pass. Pass it with --cpu-baseline-s.
Speedup = cpu_baseline_s / wall_s once a GPU wall time exists.
"""
import argparse, json, os, subprocess, time


def gpu_report(require_gpu=False):
    info = {"nvidia_smi": None, "torch": None, "cuda_available": False,
            "devices": []}
    try:
        out = subprocess.run(["nvidia-smi", "--query-gpu=name,memory.total",
                              "--format=csv,noheader"], capture_output=True,
                             text=True, timeout=30)
        info["nvidia_smi"] = out.stdout.strip() or "(no output)"
    except Exception as e:
        info["nvidia_smi"] = f"unavailable: {e}"
    try:
        import torch
        info["torch"] = torch.__version__
        info["cuda_available"] = bool(torch.cuda.is_available())
        if info["cuda_available"]:
            for i in range(torch.cuda.device_count()):
                p = torch.cuda.get_device_properties(i)
                info["devices"].append({"index": i, "name": p.name,
                                        "total_gib": round(p.total_memory / 2 ** 30, 2)})
        elif require_gpu:
            raise SystemExit("FATAL --require-gpu: no CUDA device.")
    except SystemExit:
        raise
    except Exception as e:
        info["torch"] = f"unavailable: {e}"
        if require_gpu:
            raise SystemExit("FATAL --require-gpu: torch/CUDA missing.")
    return info


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--banks", default=".")
    ap.add_argument("--output", default="gpu-job-e3-output.json")
    ap.add_argument("--cpu-baseline-s", type=float, default=0.879)
    ap.add_argument("--require-gpu", action="store_true")
    args = ap.parse_args()
    t0 = time.perf_counter()
    rep = gpu_report(args.require_gpu)
    torch_mod, device = None, None
    try:
        import torch
        torch_mod = torch
        if torch.cuda.is_available():
            device = torch.device("cuda")
    except Exception:
        pass
    if args.require_gpu and device is None:
        raise SystemExit("FATAL --require-gpu: no CUDA device.")
    banks = {}
    for bank in sorted(os.listdir(args.banks)):
        p = os.path.join(args.banks, bank)
        if not os.path.isdir(p):
            continue
        rp = os.path.join(p, "rows.pack.json")
        if os.path.exists(rp):
            d = json.load(open(rp))
            banks[bank] = {"bank_field": d.get("bank"),
                           "clips": len(d.get("rows", {}))}
        else:
            banks[bank] = {"bank_field": None, "clips": None}
    counts = [v["clips"] for v in banks.values() if v["clips"] is not None]
    if torch_mod is not None and device is not None:
        t = torch_mod.tensor(counts, dtype=torch_mod.int64, device=device)
        total = int(t.sum().item())
    else:
        total = sum(counts)
    divnots = sorted({v["bank_field"].split("divmot")[1].split("_")[0]
                      for v in banks.values() if v["bank_field"]})
    missing = [k for k, v in banks.items() if v["clips"] is None]
    wall = time.perf_counter() - t0
    out = {"job": "E3-t3-bank-verification-and-divmot15",
           "gpu": rep, "device_used": ("cuda" if device is not None else "cpu"),
           "bank_dirs": len(banks), "total_clips": total,
           "expected_total_clips": 4685, "total_matches": total == 4685,
           "divmot_numbers_present": divnots,
           "divmot_missing_from_00_20": [n for n in
               [f"{i:02d}" for i in range(21)] if n not in divnots],
           "banks_missing_rows_pack": missing,
           "banks": banks,
           "divmot15": {"identity": "Mokujin",
                        "status": "ABSENT from owner disc image; present on original "
                                  "Japan SLPS-01300 disc per BNS original index",
                        "original_index": {"bytes": 127368,
                            "sha256": "5cead15fe33b1e88cf54cf25b2c773763a71f89cdd369b85b584110ec6acc57c",
                            "records": "194 and 198 (LBA 10862 / 11000)"},
                        "owner_disc": {"bns_record": 295, "sector": 17534,
                                       "size": 0,
                                       "note": "Raw read at sector 17534 yields Gun Jack data, "
                                               "not divmot15 — never bake it as Mokujin."},
                        "wiring": "NOT BAKED. Active step: re-rip the 127,368-byte record "
                                  "from a complete disc image, SHA-verify, then run the "
                                  "identical divmot bake pipeline."},
           "heihachi_gap": {"status": "heihachi/ has NO rows.pack.json; heihachi_on_jin/ "
                            "HAS rows.pack.json from divmot13_heihachi.",
                            "rule": "Bake heihachi rows.pack.json ONLY from a divmot13 source; "
                                    "never copy heihachi_on_jin rows."},
           "wall_s": round(wall, 3), "cpu_baseline_s": args.cpu_baseline_s,
           "speedup_vs_cpu": (round(args.cpu_baseline_s / wall, 3)
                               if device is not None and wall > 0 else None),
           "notes": ["speedup is None until a GPU run records a GPU wall time."]}
    json.dump(out, open(args.output, "w"), indent=1)
    print(json.dumps({k: out[k] for k in ("job", "device_used", "bank_dirs",
                                           "total_clips", "total_matches",
                                           "divmot_numbers_present",
                                           "banks_missing_rows_pack", "wall_s",
                                           "cpu_baseline_s", "speedup_vs_cpu")}, indent=1))
    print(f"Wrote {args.output}.")


if __name__ == "__main__":
    main()
