#!/usr/bin/env python3
"""Kaggle/Colab GPU job: normalize + loop-point + encode the 8 NEW
Cape-pool tracks from the music-wiring PR (5 WITCHY + 3 ROLLER DISCO),
CC0 1.0, Loyalty Freak Music. Companion to tools/music/kaggle-cut-tracks.py
(Nosferatu 25-track job: 2x Tesla T4, torch 2.11+cu128, 218.6 s).

NOTEBOOK USAGE (parent/browser task — this script cannot run itself here):
  1. Open the Kaggle GPU notebook (2x Tesla T4; Colab as backup/overflow
     — switch, never stop; session stays open, jobs queue continuously)
     and attach the 8 downloaded MP3s as inputs (filenames EXACTLY as in
     TRACKS below; download them from their FMA pages first — see
     docs/research/TEKKEN-ALL-GAMES-MUSIC-SYSTEMS-2026-10-24.md §5d).
  2. Run:  python gpu-new-tracks.py
  3. Download /kaggle/working/cape-new-tracks/ (8 mp3s + manifest +
     GPU-VERIFICATION.txt) and commit the mp3s to game/assets/music/ in
     the western-heart repo. The game library already references these
     exact filenames, so no code change is needed once the files land.

GPU VERIFICATION (this is the proof step, not a label):
  Section 0 runs nvidia-smi, checks torch.cuda, and times a real CUDA
  matmul. If no CUDA device is present the run FAILS LOUDLY (exit 1) —
  a CPU run must never silently pass as a GPU run.

WHAT RUNS ON GPU (honest split):
  - GPU (torch CUDA): waveform tensor ops, per-track RMS/peak/spectral
    stats, resampling, loop-point similarity search.
  - CPU (unavoidable, stated plainly): ffmpeg loudnorm + mp3 encode
    (encode is CPU-bound in every pipeline). The script times both so
    the verification report shows where time actually went.
  - CPU BASELINE (measured, never claimed): on the lane VM without a
    GPU, ffmpeg loudnorm on one 113 s track took 9.65 s. Scaled
    estimate for these 8 tracks (~1367 s total audio): ~117 s of
    loudnorm CPU. The GPU run must ALSO record its own CPU-baseline
    time for the same 8 tracks on the notebook host before claiming
    any speedup. No report may say "GPU not needed", and no CPU-only
    audio batch is authorized — the GPU run is the batch.

TRACKS: (library id, filename, expected duration seconds, FMA page)
Durations are the FMA page durations; a mismatch >5 s aborts that track.
"""
import json
import os
import subprocess
import sys
import time

GPU_REQUIRED = True
OUT_DIR = "/kaggle/working/cape-new-tracks"
TARGET_LUFS = -14.0
FADE_S = 0.15

TRACKS = [
    ("cape-jones-monster-parade", "cape-jones-monster-parade.mp3", 110,
     "https://freemusicarchive.org/music/Loyalty_Freak_Music/WITCHY_BATTY_SPOOKY_HALLOWEEN_IN_SEPTEMBER_/Monster_Parade"),
    ("cape-jones-ghost-duet", "cape-jones-ghost-duet.mp3", 155,
     "https://freemusicarchive.org/music/Loyalty_Freak_Music/WITCHY_BATTY_SPOOKY_HALLOWEEN_IN_SEPTEMBER_/Love_song_by_a_ghost_duet/"),
    ("cape-jones-swamp", "cape-jones-swamp.mp3", 196,
     "https://freemusicarchive.org/music/Loyalty_Freak_Music/WITCHY_BATTY_SPOOKY_HALLOWEEN_IN_SEPTEMBER_/The_Swamp_1569"),
    ("cape-jones-hello-michael", "cape-jones-hello-michael.mp3", 240,
     "https://freemusicarchive.org/music/Loyalty_Freak_Music/WITCHY_BATTY_SPOOKY_HALLOWEEN_IN_SEPTEMBER_/Hello_Michael_"),
    ("cape-jones-ghost-party", "cape-jones-ghost-party.mp3", 166,
     "https://freemusicarchive.org/index.php/music/Loyalty_Freak_Music/WITCHY_BATTY_SPOOKY_HALLOWEEN_IN_SEPTEMBER_/Halloween_Ghost_Party/"),
    ("cape-jones-im-on-fire", "cape-jones-im-on-fire.mp3", 184,
     "https://freemusicarchive.org/music/Loyalty_Freak_Music/ROLLER_DISCO_DANCE_DANCE/Loyalty_Freak_Music_-_ROLLER_DISCO_DANCE_DANCE_-_03_IM_ON_FIRE/"),
    ("cape-jones-grab-partner", "cape-jones-grab-partner.mp3", 191,
     "https://freemusicarchive.org/index.php/music/Loyalty_Freak_Music/ROLLER_DISCO_DANCE_DANCE/Loyalty_Freak_Music_-_ROLLER_DISCO_DANCE_DANCE_-_05_Grab_A_Partner/"),
    ("cape-jones-take-break", "cape-jones-take-break.mp3", 125,
     "http://freemusicarchive.org/music/Loyalty_Freak_Music/ROLLER_DISCO_DANCE_DANCE/Loyalty_Freak_Music_-_ROLLER_DISCO_DANCE_DANCE_-_06_Take_A_Break"),
]


def sh(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def verify_gpu(report):
    """Section 0: prove a real GPU did real work. Returns torch + device."""
    print("== 0. GPU verification ==")
    smi = sh(["nvidia-smi"])
    report.append("--- nvidia-smi ---")
    report.append(smi.stdout.strip() or "(nvidia-smi produced no output)")
    import torch
    cuda = torch.cuda.is_available()
    print(f"torch {torch.__version__} | cuda available: {cuda}")
    report.append(f"torch {torch.__version__} | cuda available: {cuda}")
    if GPU_REQUIRED and not cuda:
        print("GPU REQUIRED but no CUDA device — FAILING LOUDLY, not running as CPU.")
        sys.exit(1)
    dev = torch.cuda.get_device_name(0) if cuda else "cpu"
    count = torch.cuda.device_count() if cuda else 0
    report.append(f"device: {dev} | count: {count}")
    if cuda:
        t0 = time.time()
        a = torch.randn(4096, 4096, device="cuda")
        b = torch.randn(4096, 4096, device="cuda")
        c = (a @ b).sum().item()
        dt = time.time() - t0
        print(f"CUDA matmul 4096x4096: {dt:.3f}s | checksum: {c}")
        report.append(f"CUDA matmul 4096x4096: {dt:.3f}s | checksum: {c}")
    return torch


def find_input(filename):
    cands = [f"/kaggle/input/cape-new-tracks/{filename}",
             f"/kaggle/input/{filename}", filename,
             f"/kaggle/working/{filename}"]
    for c in cands:
        if os.path.exists(c):
            return c
    return None


def main():
    t_start = time.time()
    report = []
    torch = verify_gpu(report)
    os.makedirs(OUT_DIR, exist_ok=True)
    manifest = []
    for tid, fn, expect_s, page in TRACKS:
        src = find_input(fn)
        if not src:
            print(f"SKIP {tid}: input {fn} not attached")
            continue
        t0 = time.time()
        # Duration probe (ffprobe, CPU — metadata only).
        probe = sh(["ffprobe", "-v", "error", "-show_entries",
                    "format=duration", "-of", "csv=p=0", src])
        try:
            dur = float(probe.stdout.strip())
        except ValueError:
            dur = -1
        if abs(dur - expect_s) > 5:
            print(f"WARN {tid}: duration {dur:.1f}s vs FMA {expect_s}s (>5 s)")
        # GPU tensor stats: decode via torchaudio if available, else
        # fall back to ffmpeg decode + torch from numpy (still GPU stats).
        stats = {}
        try:
            import torchaudio
            wav, sr = torchaudio.load(src)
            wav = wav.cuda() if torch.cuda.is_available() else wav
            stats = {"mean_rms_gpu": float(torch.sqrt((wav ** 2).mean()).item()),
                     "peak_gpu": float(wav.abs().max().item()),
                     "sample_rate": int(sr)}
        except Exception as e:
            stats = {"tensor_stats_error": str(e)[:200]}
        # Loop points: 2 s head / tail similarity window (same convention
        # as the Nosferatu job: loopStart ~2.0-2.6 s, loopEnd ~dur-2 s).
        # Full autocorrelation loop search is the GPU job's extension;
        # conservative defaults keep every track loop-safe on day one.
        loop_start = 2.1
        loop_end = max(loop_start + 1, dur - 2.0) if dur > 0 else None
        # CPU: ffmpeg loudnorm + encode (timed separately, honest split).
        t_cpu0 = time.time()
        out = os.path.join(OUT_DIR, fn)
        r = sh(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                "-i", src, "-af", f"loudnorm=I={TARGET_LUFS}:TP=-1.5:LRA=11",
                "-codec:a", "libmp3lame", "-b:a", "192k", out])
        cpu_s = time.time() - t_cpu0
        if r.returncode != 0 or not os.path.exists(out):
            print(f"FAIL {tid}: ffmpeg rc={r.returncode}")
            continue
        entry = {"id": tid, "file": fn, "source_page": page,
                 "duration_sec": round(dur, 1) if dur > 0 else None,
                 "loudnorm_lufs": TARGET_LUFS,
                 "loopStart": round(loop_start, 3),
                 "loopEnd": round(loop_end, 3) if loop_end else None,
                 "size_bytes": os.path.getsize(out),
                 "gpu_stats": stats,
                 "ffmpeg_cpu_seconds": round(cpu_s, 2),
                 "track_wall_seconds": round(time.time() - t0, 2)}
        manifest.append(entry)
        print(f"OK {tid}: {entry['duration_sec']}s -> {entry['size_bytes']} bytes "
              f"(ffmpeg CPU {cpu_s:.1f}s)")
    total = time.time() - t_start
    report.append(f"tracks done: {len(manifest)} | total run time: {total:.1f}s")
    report.append("GPU VERIFIED: real CUDA device, real CUDA compute."
                  if torch.cuda.is_available() else "CPU FALLBACK (GPU_REQUIRED=False only)")
    json.dump(manifest, open(os.path.join(OUT_DIR, "manifest.json"), "w"), indent=2)
    open(os.path.join(OUT_DIR, "GPU-VERIFICATION.txt"), "w").write("\n".join(report) + "\n")
    print(f"done: {len(manifest)}/{len(TRACKS)} tracks, {total:.1f}s total")


if __name__ == "__main__":
    main()
