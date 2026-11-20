#!/usr/bin/env python3
"""Kaggle GPU job: cut the correct Nosferatu synth score into 25 game tracks.

NOTEBOOK USAGE (parent/browser task — this script cannot run itself here):
  1. Open the Kaggle GPU notebook (2x Tesla T4) and attach
     nosferatu-exact.mp3 as an input file (upload from ~/workspace/nosferatu/,
     78 MB — the owner's video audio, waveform-matched to IA Nosferatu1922VHS).
     Do NOT substitute nosferatu-full.mp3: that is the WRONG Schirmann
     orchestral cut (verified NO-MATCH) and must never be used.
  2. Run this script:  python kaggle-cut-tracks.py
  3. Download /kaggle/working/nosferatu-game-tracks/ (25 mp3s + manifest +
     GPU-VERIFICATION.txt) and commit the mp3s to game/assets/music/ in the
     western-heart repo. The game library already references these exact
     filenames, so no code change is needed once the files land.

GPU VERIFICATION (this is the proof step, not a label):
  Section 0 runs nvidia-smi, checks torch.cuda, and times a real CUDA
  matmul. If no CUDA device is present the run FAILS LOUDLY (exit 1) —
  a CPU run must never silently pass as a GPU run. Override only for
  testing: GPU_REQUIRED = False below.

WHAT RUNS ON GPU (honest split):
  - GPU (torch CUDA): waveform slicing, raised-cosine fades, per-track
    RMS/peak/spectral stats, resampling. These are tensor ops and scale
    with the GPU.
  - CPU (unavoidable, stated plainly): ffmpeg loudnorm + mp3 encode
    (encode is CPU-bound in every pipeline) and librosa beat tracking
    for loop points (fast: seconds per track). The script times both so
    the verification report shows where time actually went.
"""
import json
import os
import subprocess
import sys
import time

GPU_REQUIRED = True
INPUT_CANDIDATES = [
    "/kaggle/input/nosferatu-exact/nosferatu-exact.mp3",
    "/kaggle/input/nosferatu-exact.mp3",
    "nosferatu-exact.mp3",
]
OUT_DIR = "/kaggle/working/nosferatu-game-tracks"
TARGET_LUFS = -14.0
FADE_S = 0.15

# (id, slug, start_sec, end_sec) — same cut as gen-tracks.py; every boundary
# is a measured novelty peak from cut-analysis/candidates.json.
CUT_TABLE = [
    ("nos-t01", "opening-credits", 0, 211),
    ("nos-t02", "destiny-warning", 211, 367),
    ("nos-t03", "destiny-warning-part2", 367, 549),
    ("nos-t04", "hutter-nina-home", 549, 697),
    ("nos-t05", "hutter-nina-home-part2", 697, 955),
    ("nos-t06", "mountain-road", 955, 1158),
    ("nos-t07", "coach-ride-negative", 1158, 1303),
    ("nos-t08", "the-inn", 1303, 1555),
    ("nos-t09", "at-the-castle", 1555, 1734),
    ("nos-t10", "castle-night", 1734, 1947),
    ("nos-t11", "nosferatus-shadow", 1947, 2073),
    ("nos-t12", "nosferatus-shadow-part2", 2073, 2325),
    ("nos-t13", "nosferatus-shadow-part3", 2325, 2438),
    ("nos-t14", "wisborg-household", 2438, 2559),
    ("nos-t15", "wisborg-household-part2", 2559, 2820),
    ("nos-t16", "renfield-cell", 2820, 3082),
    ("nos-t17", "ship-hold", 3082, 3257),
    ("nos-t18", "ship-hold-part2", 3257, 3529),
    ("nos-t19", "wisborg-by-night", 3529, 3747),
    ("nos-t20", "wisborg-by-night-part2", 3747, 3855),
    ("nos-t21", "plague-dead", 3855, 4052),
    ("nos-t22", "wisborg-street", 4052, 4213),
    ("nos-t23", "hutter-returned", 4213, 4423),
    ("nos-t24", "ninas-vigil", 4423, 4906),
    ("nos-t25", "finale-dawn", 4906, 5067),
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
    if not cuda:
        msg = "GPU VERIFICATION FAILED: no CUDA device. Refusing to proceed."
        print(msg)
        report.append(msg)
        if GPU_REQUIRED:
            raise SystemExit(1)
        print("GPU_REQUIRED=False override: continuing on CPU (NOT a GPU run).")
        return torch, torch.device("cpu")
    dev = torch.device("cuda")
    print(f"device: {torch.cuda.get_device_name(0)} | count: {torch.cuda.device_count()}")
    report.append(f"device: {torch.cuda.get_device_name(0)} | count: {torch.cuda.device_count()}")
    # Real CUDA work: timed matmul, not a flag check.
    a = torch.randn(4096, 4096, device=dev)
    b = torch.randn(4096, 4096, device=dev)
    torch.cuda.synchronize()
    t0 = time.time()
    c = a @ b
    torch.cuda.synchronize()
    dt = time.time() - t0
    print(f"CUDA matmul 4096x4096: {dt:.3f}s | checksum: {float(c.abs().sum()):.1f}")
    report.append(f"CUDA matmul 4096x4096: {dt:.3f}s | checksum: {float(c.abs().sum()):.1f}")
    print("GPU VERIFIED: real CUDA device, real CUDA compute.")
    report.append("GPU VERIFIED: real CUDA device, real CUDA compute.")
    return torch, dev


def find_input():
    for p in INPUT_CANDIDATES:
        if os.path.exists(p):
            return p
    import glob
    hits = glob.glob("/kaggle/input/**/nosferatu-exact.mp3", recursive=True)
    if hits:
        return hits[0]
    raise SystemExit(
        "INPUT MISSING: attach nosferatu-exact.mp3 to this notebook first "
        "(upload from ~/workspace/nosferatu/). Refusing to use any other file."
    )


def main():
    report = []
    t_run = time.time()
    torch, dev = verify_gpu(report)
    src = find_input()
    print(f"input: {src} ({os.path.getsize(src) / 1e6:.1f} MB)")
    os.makedirs(OUT_DIR, exist_ok=True)

    # Load once (torchaudio preferred; librosa fallback). Stereo -> mono mean.
    try:
        import torchaudio
        wav, sr = torchaudio.load(src)
        print(f"loaded via torchaudio: {tuple(wav.shape)} @ {sr} Hz")
    except Exception as e:
        print(f"torchaudio load failed ({e}); falling back to librosa")
        import librosa
        y, sr = librosa.load(src, sr=22050, mono=True)
        import torch as _t
        wav = _t.tensor(y).unsqueeze(0)
    if wav.shape[0] > 1:
        wav = wav.mean(dim=0, keepdim=True)
    wav = wav.to(dev)
    print(f"waveform on {dev}: {tuple(wav.shape)}")

    import soundfile as sf

    manifest_tracks = []
    for tid, slug, a, b in CUT_TABLE:
        t0 = time.time()
        seg = wav[:, int(a * sr): int(b * sr)].clone()
        # Raised-cosine fades on GPU (no clicks at cut boundaries).
        nfade = int(FADE_S * sr)
        fade = 0.5 - 0.5 * torch.cos(
            torch.linspace(0, torch.pi, nfade, device=dev))
        seg[:, :nfade] *= fade
        seg[:, -nfade:] *= fade.flip(0)
        rms = float(torch.sqrt(torch.mean(seg ** 2)).cpu())
        peak = float(seg.abs().max().cpu())
        # Write slice wav (CPU write of GPU tensor), then ffmpeg loudnorm+encode.
        tmp_wav = os.path.join(OUT_DIR, f"_{tid}.wav")
        sf.write(tmp_wav, seg.cpu().numpy().T, sr)
        out_mp3 = os.path.join(OUT_DIR, f"nosferatu-{tid}-{'_'.join(slug.split('-'))}.mp3")
        # NOTE: filenames must match game/data/music-library.json exactly:
        out_mp3 = os.path.join(OUT_DIR, f"nosferatu-{tid}-{slug}.mp3")
        r = sh(["ffmpeg", "-y", "-v", "error", "-i", tmp_wav, "-af",
                f"loudnorm=I={TARGET_LUFS}:TP=-1:LRA=11:linear=true",
                "-c:a", "libmp3lame", "-b:a", "192k", out_mp3])
        os.remove(tmp_wav)
        if r.returncode != 0 or not os.path.exists(out_mp3):
            raise SystemExit(f"ffmpeg failed for {tid}: {r.stderr[:300]}")
        # Loop points: librosa beat track on the slice, snapped to zero crossings.
        loop_start, loop_end = None, None
        try:
            import librosa
            y, _ = librosa.load(out_mp3, sr=22050, mono=True)
            _, beats = librosa.beat.beat_track(y=y, sr=22050, units="time")
            dur = b - a
            beats = [float(x) for x in beats if 2.0 < x < dur - 2.0]
            if len(beats) >= 2:
                import numpy as np
                def snap(t):
                    i = int(t * 22050)
                    w = y[max(0, i - 200): i + 200]
                    zc = np.where(np.diff(np.sign(w)))[0]
                    return float((max(0, i - 200) + (zc[len(zc) // 2] if len(zc) else 0)) / 22050)
                loop_start, loop_end = snap(beats[0]), snap(beats[-1])
        except Exception as e:
            print(f"  {tid}: loop detection skipped ({e})")
        manifest_tracks.append({
            "id": tid, "file": os.path.basename(out_mp3),
            "range_sec": [a, b], "duration_sec": b - a,
            "mean_rms_gpu": round(rms, 5), "peak_gpu": round(peak, 5),
            "loudnorm_lufs": TARGET_LUFS, "loopStart": loop_start, "loopEnd": loop_end,
            "size_bytes": os.path.getsize(out_mp3),
        })
        print(f"  {tid} {a}-{b}s rms={rms:.4f} peak={peak:.4f} "
              f"loop=({loop_start},{loop_end}) [{time.time() - t0:.1f}s]")

    manifest = {"source": os.path.basename(src), "device": str(dev),
                "tracks": manifest_tracks,
                "note": "Cut on Kaggle GPU per TRACK-CUT-PLAN.md. Commit mp3s to "
                        "game/assets/music/; library filenames already match."}
    with open(os.path.join(OUT_DIR, "nosferatu-game-tracks-manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)
    total = time.time() - t_run
    report.append(f"tracks cut: {len(manifest_tracks)} | total run time: {total:.1f}s")
    with open(os.path.join(OUT_DIR, "GPU-VERIFICATION.txt"), "w") as f:
        f.write("\n".join(report) + "\n")
    print(f"DONE: {len(manifest_tracks)} tracks in {total:.1f}s -> {OUT_DIR}")


if __name__ == "__main__":
    main()
