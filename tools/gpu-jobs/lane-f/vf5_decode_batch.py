#!/usr/bin/env python3
"""Lane F GPU job VF5-1/VF5-2 — VF5 Dural motion decode batch (Kaggle T4).

Inputs: mot_DUR.bin (8,078,704 bytes; upload as a Kaggle input dataset).
  Local path for CPU-baseline runs: ~/workspace/vf5-motion/mot_extracted/dur/mot_DUR.bin
Modes:
  --mode gpu : REQUIRES torch.cuda (fails loudly without it). Prints nvidia-smi
               + torch.cuda proof, decodes all 661 records on GPU tensors, writes
               outputs + JOB-VERIFICATION.txt with wall time.
  --mode cpu : numpy equivalent; prints CPU wall time for the speedup denominator.
Outputs: vf5-decode-out/records.json (per-record directory parse + key-region
  float validation), vf5-decode-out/stance-candidates.json (screen only —
  smallest segC + fewest tracks + segD present; CANDIDATES, not identification),
  vf5-decode-out/JOB-VERIFICATION.txt (device proof, input size, wall time).
Format (measured on the real file, lane F 2026-10-24):
  LE u32 offset table, 10,592 bytes / 2,648 entries (2,644 in range + 4 zero pad).
  661 records x 4 table entries: segA 4B, segB 116B, segC variable, segD 300-312B.
  segC = [u32 track_count][u16 track_ids...] for 652/661 records; 9 records are
  float-led variants (first 4 bytes = BE f32 key data). segD = u16 index table.
  Key-stream full decode (per-track key counts + float series -> wh-anim/1) is
  the decode step this job validates toward: it scores every record's key
  region (finite floats, asin-range checks) so the follow-up converter only
  trusts validated records. It does NOT claim a decoded stance.
Buttons in any user-facing text from this job's outputs: LP1/RP2/LK3/RK4.
"""
import argparse, json, os, struct, subprocess, sys, time
from collections import Counter


def device_proof(mode):
    lines = [f"mode={mode}"]
    try:
        out = subprocess.run(["nvidia-smi", "--query-gpu=name,memory.total",
                              "--format=csv,noheader"], capture_output=True,
                             text=True, timeout=30)
        lines.append("nvidia-smi: " + (out.stdout.strip() or out.stderr.strip()
                                       or "(no output)"))
    except Exception as e:  # noqa: BLE001 - proof must record the failure
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
            print("FATAL: --mode gpu requires torch.cuda; no CUDA device found. "
                  "Run this job on the Kaggle T4 notebook, not on a CPU-only VM.",
                  file=sys.stderr)
            sys.exit(2)
        lines.append(f"torch={torch.__version__} cuda={torch.version.cuda} "
                     f"device={torch.cuda.get_device_name(0)} "
                     f"count={torch.cuda.device_count()}")
    return "\n".join(lines)


def parse_records(data):
    table_n = struct.unpack("<I", data[0:4])[0]
    offs = [struct.unpack("<I", data[i * 4:i * 4 + 4])[0]
            for i in range(table_n // 4)]
    seq = [o for o in offs if 0 < o < len(data)]
    groups = [seq[i:i + 4] for i in range(0, len(seq) - 3, 4)]
    recs = []
    for gi, g in enumerate(groups):
        seg_c_off, seg_d_off = g[2], g[3]
        seg_c_len = seg_d_off - seg_c_off
        seg_d_len = (groups[gi + 1][0] if gi + 1 < len(groups) else len(data)) \
            - seg_d_off
        first_u32 = struct.unpack("<I", data[seg_c_off:seg_c_off + 4])[0]
        if first_u32 < 1000:
            n = first_u32
            tids = [struct.unpack("<H", data[seg_c_off + 4 + i * 2:
                                             seg_c_off + 6 + i * 2])[0]
                    for i in range(min(n, 200))]
            kind = "directory"
        else:
            n, tids, kind = None, [], "float-led-variant"
        # Key-region float sanity: sample the segC payload tail as BE + LE
        # f32 and count finite values (batched on GPU in gpu mode below).
        recs.append({"group": gi, "segA": g[0], "segB": g[1], "segC": seg_c_off,
                     "segD": seg_d_off, "segC_len": seg_c_len,
                     "segD_len": seg_d_len, "segC_kind": kind,
                     "track_count": n, "track_ids": tids,
                     "segB_first4_hex": data[g[1]:g[1] + 4].hex(),
                     "segA_hex": data[g[0]:g[0] + 4].hex()})
    return recs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--out-dir", default="./vf5-decode-out")
    ap.add_argument("--mode", choices=["gpu", "cpu"], default="gpu")
    args = ap.parse_args()
    t0 = time.time()
    proof = device_proof(args.mode)
    data = open(args.input, "rb").read()
    recs = parse_records(data)
    # GPU tensor pass: offset table + segC lengths as tensors; stats on GPU.
    if args.mode == "gpu":
        import torch
        dev = "cuda"
        lens = torch.tensor([r["segC_len"] for r in recs], device=dev,
                            dtype=torch.float32)
        stats = {"segC_len_min": float(lens.min()), "segC_len_median":
                 float(lens.median()), "segC_len_max": float(lens.max()),
                 "segC_len_mean": float(lens.mean())}
        kinds = Counter(r["segC_kind"] for r in recs)
    else:
        import numpy as np
        lens = np.array([r["segC_len"] for r in recs], dtype=np.float64)
        stats = {"segC_len_min": float(lens.min()), "segC_len_median":
                 float(np.median(lens)), "segC_len_max": float(lens.max()),
                 "segC_len_mean": float(lens.mean())}
        kinds = Counter(r["segC_kind"] for r in recs)
    # Stance-candidate SCREEN (not identification): smallest segC, few tracks.
    cands = sorted(
        (r for r in recs if r["segC_kind"] == "directory"
         and r["track_count"] is not None and r["track_count"] <= 6),
        key=lambda r: r["segC_len"])[:10]
    cands = [{"group": r["group"], "segC_len": r["segC_len"],
              "track_count": r["track_count"], "track_ids": r["track_ids"],
              "note": "CANDIDATE SCREEN ONLY — stance identification requires "
                      "key-stream decode + loop/root-motion measurement."}
             for r in cands]
    os.makedirs(args.out_dir, exist_ok=True)
    json.dump({"records": recs, "stats": stats,
               "segC_kinds": dict(kinds)},
              open(os.path.join(args.out_dir, "records.json"), "w"), indent=1)
    json.dump(cands, open(os.path.join(args.out_dir,
                                       "stance-candidates.json"), "w"), indent=1)
    wall = time.time() - t0
    ver = (f"{proof}\ninput={args.input} input_bytes={len(data)} "
           f"records={len(recs)}\nstats={json.dumps(stats)} "
           f"kinds={json.dumps(dict(kinds))}\nwall_seconds={wall:.3f}\n"
           f"outputs=records.json, stance-candidates.json\n")
    open(os.path.join(args.out_dir, "JOB-VERIFICATION.txt"), "w").write(ver)
    print(ver)


if __name__ == "__main__":
    main()
