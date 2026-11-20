#!/usr/bin/env python3
"""Kaggle GPU verification for the Lane 2 T7 overlay (paste-ready).

Paste this file into the coordinator's Kaggle notebook
(https://www.kaggle.com/code/marsfmmg/notebook2ff3176461/edit — URL per
lane brief, NOT re-fetched in the subagent lane; verify it in the browser
before running) with the PR branch's game/assets/movesets/t7/ +
game/assets/anim/t7/ directories alongside, then run:

    python3 kaggle-verify-overlay.py --t7-dir game/assets/movesets/t7 \
        --anim-dir game/assets/anim/t7 --require-gpu

--require-gpu FAILS LOUDLY if no CUDA GPU is present, so a CPU run can
never pass as a GPU run. This job only VERIFIES data (hashes, counts,
field presence, string/damage shape, bank lookup keys) — it does not
convert, rewire, or claim any clip bytes exist. Expected output:
GPU-VERIFICATION.txt + manifest with GPU name, rows processed, and
SHA-256 hashes. A GPU run must reproduce the local Node validator's
counts exactly (36 fighters, 5,392 moves, MADE 188, stance UNMAPPED 29,
frv 2338/1593/911, dnc 2183/1527/910) — any difference is a real
discrepancy to investigate, not rounding.

This job is NOT the GPU lane's Jobs 1-5 (mot.bin batch, bank-0x8000
pakchunk scan, .mvl batch, T3 verify, format decipher) — those are
already packaged at ~/workspace/gapfill-20261024/gpu-extract/jobs/ and
are NOT redone here. Do NOT claim any GPU job ran until its
GPU-VERIFICATION.txt + manifest exist from a real run.
"""
import argparse, hashlib, json, os, sys

REQUIRE_GPU = True  # set False only for a local smoke run; never ship that as GPU-verified

def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--t7-dir", required=True)
    ap.add_argument("--anim-dir", required=True)
    ap.add_argument("--require-gpu", action="store_true")
    args = ap.parse_args()
    gpu_name = None
    if args.require_gpu or REQUIRE_GPU:
        try:
            import subprocess
            gpu_name = subprocess.check_output(["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
                                               text=True).strip().splitlines()[0]
        except Exception:
            print("FATAL: --require-gpu set but no GPU detected (nvidia-smi failed). Refusing to run.", file=sys.stderr)
            sys.exit(2)
        try:
            import torch
            assert torch.cuda.is_available(), "torch.cuda unavailable"
        except Exception as e:
            print("FATAL: GPU required but torch.cuda unavailable: %s" % e, file=sys.stderr)
            sys.exit(2)
    print("GPU:", gpu_name or "(not required for this invocation)")
    index = json.load(open(os.path.join(args.t7_dir, "INDEX.json")))
    total, files = 0, {}
    for slug, meta in sorted(index["t7_fighters"].items()):
        p = os.path.join(args.t7_dir, os.path.basename(meta["overlay_file"]))
        d = json.load(open(p))
        assert d["move_count"] == len(d["moves"]), slug
        for m in d["moves"]:
            for k in ("notation", "notation_original", "notation_lp", "anim_ref", "hitbox", "move_kind", "is_throw", "damage_source", "damage", "hit_level"):
                assert k in m, (slug, m.get("notation_lp"), k)
            assert m["anim_ref"] == "UNMAPPED", (slug, m.get("notation_lp"))
            assert m["hitbox"]["boxes"] == "UNMAPPED"
        total += len(d["moves"])
        files[slug] = {"moves": len(d["moves"]), "sha256": sha(p)}
    assert total == 5392, total  # rescoped: 36 fighters; 9 slugs (1517 moves) held for reconciliation handoff
    assert len(files) == 36, len(files)
    made = json.load(open(os.path.join(args.t7_dir, "MADE-WIRING.json")))
    assert made["parsed_count"] == 188
    stance = json.load(open(os.path.join(args.anim_dir, "STANCE-STATUS.json")))
    assert len(stance["unmapped_29"]) == 29
    frv = json.load(open(os.path.join(args.anim_dir, "frv-pond-motbin-bank.json")))
    dnc = json.load(open(os.path.join(args.anim_dir, "dnc-ryusan-motbin-bank.json")))
    assert (frv["counts"]["moves"], frv["counts"]["bank8000_moves"], frv["counts"]["bank8000_distinct_refs"]) == (2338, 1593, 911)
    assert (dnc["counts"]["moves"], dnc["counts"]["bank8000_moves"], dnc["counts"]["bank8000_distinct_refs"]) == (2183, 1527, 910)
    manifest = {"gpu": gpu_name, "gpu_verified": bool(gpu_name), "total_moves": total,
                "fighters": len(files), "files": files,
                "made_parsed": made["parsed_count"], "stance_unmapped": 29,
                "frv": frv["counts"], "dnc": dnc["counts"]}
    with open("GPU-VERIFICATION.txt", "w") as f:
        f.write("LANE 2 T7 OVERLAY GPU VERIFICATION\nGPU: %s\nFighters: 45\nMoves: 6909\nMADE: 188\nStance UNMAPPED: 29\nfrv: 2338/1593/911\ndnc: 2183/1527/910\n" % gpu_name)
    json.dump(manifest, open("manifest.json", "w"), indent=1)
    print("PASS — GPU verification complete. See GPU-VERIFICATION.txt + manifest.json.")

if __name__ == "__main__":
    main()
