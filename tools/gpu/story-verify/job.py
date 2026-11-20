#!/usr/bin/env python3
"""Story-verify GPU job (Lane 6, story workstream 9 + Shrine support 11).

Canon-anchor verification batch for Heart and Mind Within content:
every story beat (heartmind.js dialogue + Yarn/Ink story lines) is
checked against every CANON.md paragraph, and beats with no anchor
above threshold are flagged NEEDS-ANCHOR-REVIEW for a human.

MEASUREMENT CONTRACT (blanket GPU order 2026-10-24): every run
records nvidia-smi + torch.cuda proof, input sizes, output,
wall time, AND a CPU-baseline time for the SAME algorithm.
Speedup is MEASURED per job, never claimed. No run may report
a speedup without both timings present.

Algorithm (same code, two devices — fair comparison):
  TF-IDF vectors (log IDF) over a shared vocabulary, L2-normalized,
  cosine matrix = beats @ paragraphs.T, computed with torch tensors
  on device='cpu' (baseline) and device='cuda' (GPU path).
Optional embedding path (only if sentence-transformers is installed):
  all-MiniLM-L6-v2 embeddings on cuda, cosine matrix on GPU, timed
  separately as emb_gpu_time_s. It is a SECOND signal, not the
  speedup basis (different algorithm from the CPU baseline).

Shrine support: inputs/shrine-subset.json (shrine/still-point
beats + shrine canon paragraphs) is verified in the same run and
reported under shrine_subset. This job verifies Shrine-related
story content only — it generates NO Shrine assets (asset lane)
and does NOT touch Shrine mode credits (standing requirement:
end credits MUST say "In memory of Terry Davis, RIP" — Shrine
lane implements that in the mode itself).

Usage (Kaggle T4 x2 notebook or Colab — see README.md):
  python3 job.py --beats inputs/heartmind-beats.json \
      --canon inputs/canon-paragraphs.json \
      --shrine inputs/shrine-subset.json \
      --out results/story-verify-results.json
Exit code 0 even when flags exist (flags are output, not failure).
Exit code 2 on missing inputs. Requires: torch, numpy.
"""
import argparse
import json
import re
import subprocess
import sys
import time

import numpy as np


def tokenize(text):
    return re.findall(r"[a-z0-9]+", text.lower())


def build_vocab(paras):
    vocab = {}
    for p in paras:
        for w in set(tokenize(p["text"])):
            if w not in vocab:
                vocab[w] = len(vocab)
    return vocab


def tfidf_matrix(docs, vocab, device):
    import torch

    n, v = len(docs), len(vocab)
    mat = torch.zeros((n, v), dtype=torch.float32, device=device)
    for i, d in enumerate(docs):
        for w in tokenize(d["text"]):
            j = vocab.get(w)
            if j is not None:
                mat[i, j] += 1
    df = (mat > 0).sum(dim=0).clamp(min=1)
    idf = torch.log((n + 1) / df) + 1
    mat = mat * idf
    norms = mat.norm(dim=1, keepdim=True).clamp(min=1e-9)
    return mat / norms


def run_tfidf(beats, paras, vocab, device):
    import torch

    t0 = time.perf_counter()
    b = tfidf_matrix(beats, vocab, device)
    p = tfidf_matrix(paras, vocab, device)
    sims = b @ p.T
    if device == "cuda":
        torch.cuda.synchronize()
    t1 = time.perf_counter()
    best, arg = sims.max(dim=1)
    return best.cpu().numpy(), arg.cpu().numpy(), t1 - t0


def nvidia_smi():
    try:
        out = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,memory.total",
             "--format=csv,noheader"],
            capture_output=True, text=True, timeout=30)
        return out.stdout.strip() or "nvidia-smi returned empty"
    except Exception as e:  # noqa: BLE001 — record, don't crash
        return f"nvidia-smi unavailable: {e}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--beats", required=True)
    ap.add_argument("--canon", required=True)
    ap.add_argument("--shrine", default=None)
    ap.add_argument("--out", required=True)
    ap.add_argument("--threshold", type=float, default=0.15)
    args = ap.parse_args()

    import torch

    wall0 = time.perf_counter()
    try:
        beats = json.load(open(args.beats))
        paras = json.load(open(args.canon))
    except FileNotFoundError as e:
        print(f"missing input: {e}", file=sys.stderr)
        return 2
    vocab = build_vocab(paras)

    # CPU baseline FIRST (same algorithm, device='cpu').
    best_cpu, arg_cpu, cpu_time = run_tfidf(beats, paras, vocab, "cpu")

    # GPU path (same algorithm, device='cuda') — only if CUDA exists.
    cuda = torch.cuda.is_available()
    gpu_time, best, arg = None, best_cpu, arg_cpu
    device_name = None
    if cuda:
        device_name = torch.cuda.get_device_name(0)
        best, arg, gpu_time = run_tfidf(beats, paras, vocab, "cuda")

    speedup = (cpu_time / gpu_time) if gpu_time else None

    results = []
    for i, b in enumerate(beats):
        score = float(best[i])
        results.append({
            "beat_id": b["id"],
            "text_excerpt": b["text"][:160],
            "best_paragraph": paras[int(arg[i])]["id"],
            "best_score": round(score, 4),
            "flag": score < args.threshold,
        })

    # Optional embedding signal on GPU (different algorithm — timed
    # separately, never used as the speedup basis).
    emb = None
    if cuda:
        try:
            from sentence_transformers import SentenceTransformer

            t0 = time.perf_counter()
            model = SentenceTransformer("all-MiniLM-L6-v2", device="cuda")
            eb = model.encode([b["text"] for b in beats],
                              convert_to_tensor=True, show_progress_bar=False)
            ep = model.encode([p["text"] for p in paras],
                              convert_to_tensor=True, show_progress_bar=False)
            import torch.nn.functional as F

            sims = F.cosine_similarity(
                eb.unsqueeze(1), ep.unsqueeze(0), dim=2)
            torch.cuda.synchronize()
            emb = {
                "model": "all-MiniLM-L6-v2",
                "gpu_time_s": round(time.perf_counter() - t0, 3),
                "mean_best": round(float(sims.max(dim=1).values.mean()), 4),
            }
        except Exception as e:  # noqa: BLE001 — optional path
            emb = {"error": str(e)}

    # Shrine subset, same TF-IDF gate, reported separately.
    shrine_out = None
    if args.shrine:
        try:
            sub = json.load(open(args.shrine))
            sv = build_vocab(sub["paragraphs"])
            sb, sa, _ = run_tfidf(sub["beats"], sub["paragraphs"], sv,
                                  "cuda" if cuda else "cpu")
            shrine_out = {
                "beats": len(sub["beats"]),
                "paragraphs": len(sub["paragraphs"]),
                "flagged": int((sb < args.threshold).sum()),
                "mean_best": round(float(sb.mean()), 4),
            }
        except FileNotFoundError:
            shrine_out = {"error": "shrine input not found"}

    out = {
        "nvidia_smi": nvidia_smi(),
        "torch_version": torch.__version__,
        "cuda_available": cuda,
        "device": device_name,
        "input_size": {
            "beats": len(beats),
            "canon_paragraphs": len(paras),
            "vocab": len(vocab),
        },
        "cpu_time_s": round(cpu_time, 3),
        "gpu_time_s": round(gpu_time, 3) if gpu_time else None,
        "speedup": round(speedup, 2) if speedup else None,
        "embedding_gpu": emb,
        "threshold": args.threshold,
        "flagged": sum(1 for r in results if r["flag"]),
        "results": results,
        "shrine_subset": shrine_out,
        "wall_time_s": round(time.perf_counter() - wall0, 3),
    }
    with open(args.out, "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps({k: out[k] for k in (
        "cuda_available", "device", "input_size", "cpu_time_s",
        "gpu_time_s", "speedup", "flagged", "wall_time_s")}, indent=1))
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
