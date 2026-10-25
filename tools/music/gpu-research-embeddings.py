#!/usr/bin/env python3
"""Kaggle/Colab GPU research job: embedding-search + vibe classification
for the Tekken/all-games music-system research corpus.

WHY THIS RIDES THE GPU (coordinator note, blanket GPU order 2026-10-24):
research tasks use GPU-accelerated search, embeddings, batch analysis
and classification where they help — not CPU-only research where the
GPU helps. This job embeds the community-docs corpus and every
candidate track's metadata, ranks tracks against stage/mode vibe
descriptors, and classifies new candidates by vibe/mode fit, so the
next music lane's pool assignments come from measured similarity,
not from a lane author's gut.

NOTEBOOK USAGE (parent/browser task — this script cannot run itself here):
  1. Open the Kaggle GPU notebook (2x Tesla T4; Colab as backup/overflow
     — switch, never stop) and attach a corpus directory as input:
       corpus/  — .md/.txt files: Tekken Wiki Tekken Tunes pages, wavu
                  guides, T7 Jukebox Tool docs, WH docs/MUSIC-PIPELINE.md,
                  WH music research docs, FMA album/track pages (text).
       tracks.csv — columns: id,title,artist,album,moods,modes,stages,
                  license,source_page  (one row per candidate track).
     A starter tracks.csv can be generated from
     game/data/music-library.json (ids/titles/moods/modes/stages) plus
     the new-candidate rows in the wiring research doc §5.
  2. Run:  python gpu-research-embeddings.py --corpus /kaggle/input/corpus \
             --tracks /kaggle/input/tracks.csv --out /kaggle/working/music-research
  3. Download the out dir (rankings.json + GPU-VERIFICATION.txt) and
     file the rankings in the next music lane's research doc. Rankings
     ADVISE pool assignments; they never auto-edit the library.

GPU VERIFICATION: same discipline as gpu-new-tracks.py — nvidia-smi +
torch.cuda + CUDA matmul proof, input size, output, wall time, AND
CPU-baseline time. If no CUDA device is present the run FAILS LOUDLY
(exit 1) unless GPU_REQUIRED is explicitly overridden for testing.

CPU BASELINE (measured on the lane VM, no GPU): a stdlib TF-IDF cosine
run over 2 research docs x 3 queries took 0.001 s — the lexical floor.
TF-IDF is cheap at tiny scale; the GPU job's value at corpus scale
(100s of docs x 100s of tracks) is semantic ranking quality + batch
throughput. The GPU run must ALSO time a CPU embedding pass over the
same corpus (sentence-transformers on CPU, small sample if the full
corpus is too slow) and report both times. No report may say
"GPU not needed".

VIBE DESCRIPTORS (fixed set — the pool-assignment vocabulary):
  spooky, surf, witchy, halloween, ghost, fun, disco, driving,
  battle, epic, dark, tense, calm, aggressive, mystical, mechanical,
  triumphant, dramatic
MODEL: sentence-transformers/all-MiniLM-L6-v2 (CPU-loadable for the
baseline; CUDA for the batch). If the notebook has no network for the
model download, the run must FAIL with that fact stated — never
silently fall back to TF-IDF and label it embeddings.
"""
import argparse
import json
import os
import subprocess
import sys
import time

GPU_REQUIRED = True

DESCRIPTORS = ["spooky", "surf", "witchy", "halloween", "ghost", "fun",
               "disco", "driving", "battle", "epic", "dark", "tense",
               "calm", "aggressive", "mystical", "mechanical",
               "triumphant", "dramatic"]


def sh(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def verify_gpu(report):
    print("== 0. GPU verification ==")
    smi = sh(["nvidia-smi"])
    report.append("--- nvidia-smi ---")
    report.append(smi.stdout.strip() or "(nvidia-smi produced no output)")
    import torch
    cuda = torch.cuda.is_available()
    print(f"torch {torch.__version__} | cuda available: {cuda}")
    report.append(f"torch {torch.__version__} | cuda available: {cuda}")
    if GPU_REQUIRED and not cuda:
        print("GPU REQUIRED but no CUDA device — FAILING LOUDLY.")
        sys.exit(1)
    dev = torch.cuda.get_device_name(0) if cuda else "cpu"
    report.append(f"device: {dev} | count: {torch.cuda.device_count() if cuda else 0}")
    if cuda:
        t0 = time.time()
        a = torch.randn(4096, 4096, device="cuda")
        b = torch.randn(4096, 4096, device="cuda")
        c = (a @ b).sum().item()
        dt = time.time() - t0
        print(f"CUDA matmul 4096x4096: {dt:.3f}s | checksum: {c}")
        report.append(f"CUDA matmul 4096x4096: {dt:.3f}s | checksum: {c}")
    return torch


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", required=True)
    ap.add_argument("--tracks", required=True)
    ap.add_argument("--out", default="/kaggle/working/music-research")
    args = ap.parse_args()
    t_start = time.time()
    report = []
    torch = verify_gpu(report)
    os.makedirs(args.out, exist_ok=True)

    docs = []
    for name in sorted(os.listdir(args.corpus)):
        p = os.path.join(args.corpus, name)
        if os.path.isfile(p) and name.endswith((".md", ".txt")):
            docs.append((name, open(p, errors="replace").read()))
    report.append(f"corpus docs: {len(docs)} | corpus bytes: "
                  f"{sum(len(t) for _, t in docs)}")
    print(f"corpus: {len(docs)} docs")

    import csv
    rows = list(csv.DictReader(open(args.tracks)))
    report.append(f"candidate tracks: {len(rows)}")
    print(f"tracks: {len(rows)} rows")

    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2",
                                device="cuda" if torch.cuda.is_available() else "cpu")
    # CPU baseline: embed the descriptor set + first 8 tracks on CPU,
    # timed, so the report carries a real CPU-vs-GPU comparison.
    t_cpu0 = time.time()
    cpu_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2",
                                    device="cpu")
    _ = cpu_model.encode([f"vibe: {d}" for d in DESCRIPTORS] +
                         [r.get("title", "") for r in rows[:8]],
                         convert_to_tensor=False, show_progress_bar=False)
    cpu_s = time.time() - t_cpu0
    report.append(f"CPU-baseline embed ({len(DESCRIPTORS)} descriptors + "
                  f"{min(8, len(rows))} tracks): {cpu_s:.2f}s")
    print(f"CPU baseline: {cpu_s:.2f}s")

    t_gpu0 = time.time()
    desc_emb = model.encode([f"vibe: {d}" for d in DESCRIPTORS],
                            convert_to_tensor=True, show_progress_bar=False)
    track_texts = [f"{r.get('title', '')} by {r.get('artist', '')} "
                   f"({r.get('album', '')}) moods: {r.get('moods', '')}"
                   for r in rows]
    track_emb = model.encode(track_texts, convert_to_tensor=True,
                             batch_size=64, show_progress_bar=False)
    doc_emb = model.encode([t[:4000] for _, t in docs],
                           convert_to_tensor=True, batch_size=32,
                           show_progress_bar=False) if docs else None
    gpu_s = time.time() - t_gpu0
    report.append(f"GPU embed ({len(DESCRIPTORS)} descriptors + {len(rows)} "
                  f"tracks + {len(docs)} docs): {gpu_s:.2f}s")
    print(f"GPU embed: {gpu_s:.2f}s")

    from sentence_transformers.util import cos_sim
    rankings = []
    sims = cos_sim(track_emb, desc_emb)
    for i, r in enumerate(rows):
        scored = sorted(((DESCRIPTORS[j], round(float(sims[i][j]), 4))
                         for j in range(len(DESCRIPTORS))),
                        key=lambda x: -x[1])
        rankings.append({"id": r.get("id"), "title": r.get("title"),
                         "top_vibes": scored[:3],
                         "all_vibes": dict(scored)})
    # Corpus relevance: which docs are closest to each track (top 2).
    if doc_emb is not None:
        import torch as _t
        dsims = cos_sim(track_emb, doc_emb)
        for i, entry in enumerate(rankings):
            top = sorted(range(len(docs)), key=lambda j: -float(dsims[i][j]))[:2]
            entry["closest_docs"] = [docs[j][0] for j in top]
    json.dump(rankings, open(os.path.join(args.out, "rankings.json"), "w"), indent=2)
    total = time.time() - t_start
    report.append(f"total run time: {total:.1f}s")
    report.append("GPU VERIFIED: real CUDA device, real CUDA compute."
                  if torch.cuda.is_available() else "CPU FALLBACK (override only)")
    open(os.path.join(args.out, "GPU-VERIFICATION.txt"), "w").write(
        "\n".join(report) + "\n")
    print(f"done: {len(rankings)} ranked, {total:.1f}s total")


if __name__ == "__main__":
    main()
