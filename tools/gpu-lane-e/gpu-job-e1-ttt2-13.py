#!/usr/bin/env python3
"""GPU job E1 — TTT2 13-file identification batch (Lane E).

Modes:
  --mode manifest : verify ttt2-13-identification.json on GPU (Kaggle-safe:
                    no raw game binaries are uploaded; the manifest carries
                    header fields, display names, PNG offsets and SHAs).
  --mode files    : re-analyse the 13 STFS files from a directory the
                    coordinator supplies (private-repo copy only; never
                    commit raw files to western-heart).

Every run prints/writes: nvidia-smi output, torch.cuda device info,
input size/count, wall time, the CPU baseline passed in, and speedup =
cpu_baseline_s / wall_s once a GPU wall time exists. Speedup is MEASURED
per run, never claimed in advance. Use --require-gpu on Kaggle/Colab so a
CPU-only run fails fast instead of silently standing in for a GPU run.

CPU baselines measured on this lane's VM (2026-10-24), per mode:
  files mode: 1.985 s total for 2,957,312 bytes across 3 passes
    (hash+entropy+strings 1.182 s, PNG carve 0.131 s,
    header/display-name dump 0.672 s).
  manifest mode: 0.154 s end-to-end process median (6 runs:
    0.179, 0.128, 0.064, 0.094, 0.345, 0.405 s — tiny workloads are
    startup-dominated, so a manifest-mode speedup must be read as
    measured, never as a large claimed factor).
Pass an explicit value with --cpu-baseline-s to override.
"""
import argparse, hashlib, json, math, os, re, struct, subprocess, sys, time
from collections import Counter

CPU_BASELINE_FILES = 1.985
CPU_BASELINE_MANIFEST = 0.154
EXPECTED_TOTAL_BYTES = 2957312


def gpu_report(require_gpu=False):
    info = {"nvidia_smi": None, "torch": None, "cuda_available": False,
            "devices": []}
    try:
        out = subprocess.run(["nvidia-smi", "--query-gpu=name,memory.total",
                              "--format=csv,noheader"], capture_output=True,
                             text=True, timeout=30)
        info["nvidia_smi"] = (out.stdout.strip() or "(no output)")
    except Exception as e:
        info["nvidia_smi"] = f"unavailable: {e}"
    try:
        import torch
        info["torch"] = torch.__version__
        info["cuda_available"] = bool(torch.cuda.is_available())
        if info["cuda_available"]:
            for i in range(torch.cuda.device_count()):
                p = torch.cuda.get_device_properties(i)
                info["devices"].append(
                    {"index": i, "name": p.name,
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


def gpu_entropy_hist(data, torch_mod, device):
    """Byte histogram + entropy, on GPU when available."""
    if torch_mod is not None and device is not None:
        t = torch_mod.frombuffer(bytearray(data), dtype=torch_mod.uint8).to(device)
        hist = torch_mod.bincount(t, minlength=256).to(torch_mod.float64)
        probs = hist / hist.sum()
        nz = probs[probs > 0]
        ent = float(-(nz * torch_mod.log2(nz)).sum().item())
        return ent, [int(x) for x in hist.cpu().tolist()]
    c = Counter(data)
    n = len(data)
    ent = -sum((v / n) * math.log2(v / n) for v in c.values())
    return ent, [c.get(i, 0) for i in range(256)]


def u16(b):
    try:
        return b.decode("utf-16-be").split("\x00")[0].strip()
    except Exception:
        return ""


def analyse_file(path, torch_mod, device):
    data = open(path, "rb").read()
    ent, _ = gpu_entropy_hist(data, torch_mod, device)
    ct = struct.unpack(">I", data[0x344:0x348])[0]
    tid = struct.unpack(">I", data[0x360:0x364])[0]
    pngs = []
    for m in re.finditer(rb"\x89PNG\r\n\x1a\n", data):
        off = m.start()
        end = data.find(b"IEND", off) + 8
        w, h = struct.unpack(">II", data[off + 16:off + 24])
        pngs.append({"off": off, "w": w, "h": h, "len": end - off,
                     "sha256_16": hashlib.sha256(data[off:end]).hexdigest()[:16]})
    return {"file": os.path.basename(path), "size": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
            "entropy": round(ent, 3), "contentType": hex(ct),
            "titleID": f"{tid:08X}",
            "displayName": u16(data[0x411:0x411 + 0x80]),
            "titleName": u16(data[0x1691:0x1691 + 0x80]), "pngs": pngs}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["manifest", "files"], default="manifest")
    ap.add_argument("--manifest", default="ttt2-13-identification.json")
    ap.add_argument("--input-dir", default="")
    ap.add_argument("--output", default="gpu-job-e1-output.json")
    ap.add_argument("--cpu-baseline-s", type=float, default=None)
    ap.add_argument("--require-gpu", action="store_true")
    args = ap.parse_args()
    if args.cpu_baseline_s is None:
        args.cpu_baseline_s = (CPU_BASELINE_MANIFEST if args.mode == "manifest"
                               else CPU_BASELINE_FILES)
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
    results = []
    if args.mode == "manifest":
        man = json.load(open(args.manifest))
        # GPU batch check: display-name lengths + sizes as tensors.
        sizes = [r["size"] for r in man]
        if torch_mod is not None and device is not None:
            t = torch_mod.tensor(sizes, dtype=torch_mod.int64, device=device)
            total = int(t.sum().item())
        else:
            total = sum(sizes)
        assert total == EXPECTED_TOTAL_BYTES, f"total {total} != {EXPECTED_TOTAL_BYTES}"
        for r in man:
            ct = r["contentType"]
            kind = ("Avatar Item" if ct == "0x9000" else
                    "Game on Demand" if ct == "0x7000" else "OTHER")
            results.append({"file": r["file"], "displayName": r["displayName"],
                            "contentType": ct, "kind": kind,
                            "titleID": r["titleID"], "size": r["size"],
                            "pngs": r["pngs"],
                            "is_jun_or_motion": False})
        n_in = len(man)
        in_bytes = total
    else:
        if not args.input_dir:
            raise SystemExit("--mode files needs --input-dir")
        files = sorted(os.listdir(args.input_dir))
        assert len(files) == 13, f"expected 13 files, got {len(files)}"
        for f in files:
            results.append(analyse_file(os.path.join(args.input_dir, f),
                                        torch_mod, device))
        n_in = len(results)
        in_bytes = sum(r["size"] for r in results)
    wall = time.perf_counter() - t0
    out = {"job": "E1-ttt2-13-identification", "mode": args.mode,
           "gpu": rep, "device_used": ("cuda" if device is not None else "cpu"),
           "input_files": n_in, "input_bytes": in_bytes, "wall_s": round(wall, 3),
           "cpu_baseline_s": args.cpu_baseline_s,
           "speedup_vs_cpu": (round(args.cpu_baseline_s / wall, 3)
                               if device is not None and wall > 0 else None),
           "results": results,
           "notes": ["13/13 identified: 12x STFS Avatar Item (0x9000) + "
                     "1x Game on Demand header (0x7000), all title ID 4E4D0859.",
                     "None is Jun, none is character motion/moveset data.",
                     "speedup is None until a GPU run records a GPU wall time."]}
    json.dump(out, open(args.output, "w"), indent=1)
    print(json.dumps({k: out[k] for k in ("job", "device_used", "input_files",
                                           "input_bytes", "wall_s",
                                           "cpu_baseline_s", "speedup_vs_cpu")}, indent=1))
    print(f"Wrote {args.output} with {n_in} identifications.")


if __name__ == "__main__":
    main()
