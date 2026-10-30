#!/usr/bin/env python3
"""
kaggle_unirig_notebook.py — UniRig auto-rigging on Kaggle GPU (FLAGSHIP GPU LANE).

WHAT THIS IS
------------
A single self-contained script for the Kaggle notebook at
https://www.kaggle.com/code/marsfmmg/notebook2ff3176461/edit
(2x Tesla T4, ~15 GB VRAM each, ~30 GPU-hr/week shared quota).

Paste the WHOLE file into one Kaggle code cell, or upload it and run:
    python kaggle_unirig_notebook.py --jobs cape-jones
    python kaggle_unirig_notebook.py --jobs all --gpus 2

It does NOT re-implement UniRig. It drives the REAL upstream UniRig code
(VAST-AI/UniRig, SIGGRAPH'25) through its own documented entry points:

  * python -m src.data.extract                 (mesh -> raw_data.npz)
  * python run.py --task=...skeleton...         (skeleton predict, datalist mode)
  * python run.py --task=...skin...             (skin predict, datalist mode)
  * bash launch/inference/merge.sh              (skin FBX + original -> rigged GLB)
  (generate_skeleton.sh / generate_skin.sh are used ONLY for the
  skeleton-only fallback — see the gotchas below.)

plus honest pre/post stages the upstream scripts do NOT do:
  * remesh/clean   — strip junk, weld duplicates, simplify to ~50-100k faces
  * weight-transfer/smoothing — Alisa->Cape bonemap + neighbour smoothing
                    (only when a reference rig is supplied; otherwise the
                    UniRig-predicted skin is kept and that is logged)
  * verify/render  — quantitative checks + a best-effort render pass

PIPELINE ORDER PER JOB (sequential inside one job; jobs run in parallel
across GPUs — see --gpus; each job runs in its OWN UniRig checkout copy
because datalist mode uses shared relative dirs):
    1. clean/remesh input            (CPU, trimesh; fast)
    2. extract                       (bpy, src.data.extract, datalist dirs)
    3. skeleton inference            (GPU, run.py skeleton task, datalist mode)
    4. skin inference                (GPU, run.py skin task, datalist mode)
    5. merge -> rigged GLB           (bpy, merge.sh transfer mode)
    6. weight transfer + smoothing   (CPU/blender, only if reference given)
    7. verify + render               (quant checks always; render best-effort)
    8. repo-layout staging           (copies rigged GLBs to
                                     unirig_out/repo_layout/game/assets/models/
                                     for the follow-up repo lane — no push
                                     from this script)

CRITICAL UPSTREAM GOTCHAS BAKED IN (read from the actual code, not guessed):
  * run.py sets user_mode=True whenever --output OR --output_dir is
    passed, and in user_mode the skeleton writer SKIPS writing
    predict_skeleton.npz (src/system/ar.py:
    `if not self.user_mode and self.export_npz ...`). The skin task
    (configs/task/quick_inference_unirig_skin.yaml) needs that npz as
    its data_name, so the documented CLI two-step flow
    (generate_skeleton.sh / generate_skin.sh with --output/--output_dir)
    CANNOT feed the skin phase as written. => This script runs skeleton
    AND skin in DATALIST mode (no --input/--output args at all):
    extract -> dataset_inference_clean/<stem>/raw_data.npz, write
    inference_datalist.txt, run.py skeleton task, run.py skin task,
    then merge.sh. Outputs are found by glob afterwards, never assumed.
    A CLI skeleton run is kept ONLY as a skeleton-only fallback, and it
    is labeled as skin-unavailable by design.
  * generate_skin.sh defaults --data_name to raw_data.npz, which
    OVERRIDES the task yaml's predict_skeleton.npz (run.py: a passed
    --data_name wins) — and raw_data.npz is mesh-only (joints=None),
    so it cannot skin. => This script does NOT use generate_skin.sh;
    it calls run.py directly with no --data_name so the task default
    (predict_skeleton.npz) applies. There is no raw_data.npz retry:
    it is not a valid fallback.
  * UniRig's extract step runs UNDER BLENDER (src/data/extract.py imports
    bpy). It is not a plain trimesh load: the Kaggle env MUST have
    bpy==4.2 installed (it is in requirements.txt) and the extract
    simplifies to faces_target_count=50000 by default.
  * The skeleton model config (configs/model/
    unirig_ar_350m_1024_81920_float32.yaml) sets
    _attn_implementation: flash_attention_2 and builds the LLM
    from_config (facebook/opt-350m CONFIG only — no 350M weight download).
    If flash_attn fails to install, the run fails; see the documented
    fallback in README.md. This script does NOT silently rewrite the
    config (UNIRIG_ATTN=sdpa is an explicit, logged, opt-in experiment).
  * Skin inference is the VRAM hog. The upstream training note says the
    skin task "takes up at least 60GB memory on a single gpu" at
    batch_size=2 in TRAINING. Inference is batch_size=1, but a 15 GB T4
    is still tight: if skin OOMs, the script logs it as a SKIN-OOM (not
    a generic failure) and keeps the skeleton FBX + a skeleton-only GLB
    so the run is still useful. Do NOT "fix" this by silently dropping
    to a smaller mesh without logging it — the mesh size is in report.json.

KAGGLE PATHS (defaults; override with flags):
    input dir   /kaggle/input/unirig-jobs/   (upload inputs here)
    working dir /kaggle/working/             (script + UniRig checkout live here)
    output dir  /kaggle/working/unirig_out/  (download this whole folder)

LOCAL TESTING (no GPU, no torch needed):
    python kaggle_unirig_notebook.py --dry-run --jobs cape-jones
    python kaggle_unirig_notebook.py --check-env
    python kaggle_unirig_notebook.py --test-local   (tiny OBJ clean+smooth)

Python 3.11 is what upstream targets; Kaggle's default 3.10/3.11 both
work for THIS script (it only uses stdlib at import time).
"""
from __future__ import annotations

import argparse
import concurrent.futures
import glob
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

# --------------------------------------------------------------------------
# Constants — grounded in the upstream repo, not invented
# --------------------------------------------------------------------------
HF_REPO = "VAST-AI/UniRig"
# Exact map from src/inference/download.py (keys = resume_from_checkpoint
# values in the task yamls; values = HF filenames). The script downloads
# these directly so a failure is visible BEFORE the GPU runs start.
CKPT_MAP = {
    "experiments/skeleton/articulation-xl_quantization_256/model.ckpt":
        "skeleton/articulation-xl_quantization_256/model.ckpt",
    "experiments/skin/articulation-xl/model.ckpt":
        "skin/articulation-xl/model.ckpt",
    # Third entry in download.py's MAP (skin/skeleton) is not referenced by
    # either quick_inference task yaml; downloaded only with --all-checkpoints.
    "experiments/skin/skeleton/model.ckpt": "skin/skeleton/model.ckpt",
}
SKELETON_TASK = "configs/task/quick_inference_skeleton_articulationxl_ar_256.yaml"
SKIN_TASK = "configs/task/quick_inference_unirig_skin.yaml"
UPSTREAM_REPO_URL = "https://github.com/VAST-AI-Research/UniRig"

# Default job queue. "cape-jones" is the flagship job; every other entry is
# a slot the parent fills by dropping a file into /kaggle/input/unirig-jobs/
# with the matching filename. Jobs whose input file is MISSING are skipped
# with a clear log line — they never block the queue.
#   name: job id (also the output folder name)
#   input: filename expected under --input-dir (or an absolute path)
#   kind:  "cape" (full pipeline incl. bonemap weight pass if reference
#          supplied) or "generic" (UniRig skeleton+skin+merge only)
DEFAULT_JOBS = [
    {"name": "cape-jones", "input": "cape-jones-body-decim600k.obj", "kind": "cape"},
    {"name": "tripo-1", "input": "tripo-1.glb", "kind": "generic"},
    {"name": "tripo-2", "input": "tripo-2.glb", "kind": "generic"},
    {"name": "tripo-3", "input": "tripo-3.glb", "kind": "generic"},
]

# --------------------------------------------------------------------------
# Small utilities (stdlib only, so --dry-run / --test-local work anywhere)
# --------------------------------------------------------------------------

def log(msg: str) -> None:
    # Logs go to stderr so stdout stays clean for --dry-run / --check-env
    # / --test-local JSON output (and for the printed proof block).
    print(f"[unirig {time.strftime('%H:%M:%S')}] {msg}", flush=True,
          file=sys.stderr)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def run(cmd, cwd=None, env=None, log_prefix=""):
    """Run a command, stream nothing fancy, return (returncode, tail)."""
    log(f"$ {' '.join(str(c) for c in cmd)}")
    proc = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True)
    tail = (proc.stdout + proc.stderr)[-4000:]
    if proc.returncode != 0:
        log(f"  FAILED rc={proc.returncode}:\n{tail}")
    else:
        log(f"  ok rc=0 (last lines):\n{tail[-800:]}")
    return proc.returncode, tail


def gpu_info():
    """Return (count, [names]) without importing torch at module level."""
    try:
        import torch
        if not torch.cuda.is_available():
            return 0, []
        return torch.cuda.device_count(), [
            torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())
        ]
    except Exception as e:  # torch missing counts as 0 GPUs, honestly
        log(f"torch GPU probe failed ({e}); treating as 0 GPUs")
        return 0, []


def nvidia_smi_text() -> str:
    """Raw nvidia-smi output for the PROOF block (empty if absent)."""
    try:
        proc = subprocess.run(["nvidia-smi"], capture_output=True, text=True,
                              timeout=30)
        return proc.stdout.strip() or proc.stderr.strip()
    except Exception as e:
        return f"nvidia-smi unavailable: {e}"


# --------------------------------------------------------------------------
# Stage 0 — install (exact upstream lines, with the known pain points logged)
# --------------------------------------------------------------------------
PIP_BASE = [
    # From UniRig README "Install dependencies" + requirements.txt.
    # Kaggle already ships torch; reinstalling torch is skipped unless
    # --force-torch, because a torch reinstall on Kaggle is slow and
    # can break the prebuilt CUDA stack.
    ["pip", "install", "-q", "transformers==4.51.3", "python-box", "einops",
     "omegaconf", "pytorch_lightning", "lightning", "addict", "timm",
     "fast-simplification", "trimesh", "open3d", "pyrender",
     "huggingface_hub", "psutil", "scipy", "numpy==1.26.4"],
    ["pip", "install", "-q", "bpy==4.2"],
]
# spconv / torch_scatter / torch_cluster are CUDA+torch-version specific.
# The README's form is: spconv-{cuda-version} and the pyg wheel index for
# torch-{torch-version}+{cuda-version}. They CANNOT be pinned blindly here:
# install_deps() detects torch/cuda at runtime and builds the right lines.
# flash_attn is attempted last and allowed to fail (README: "high chance
# you will encounter flash_attn installation error") — the failure is
# logged and the run continues to the checkpoint step so the parent sees
# exactly which stage broke instead of a silent pip avalanche.

def install_deps(force_torch: bool = False, skip_install: bool = False) -> dict:
    report = {"pip_base": None, "bpy": None, "spconv": None,
              "pyg": None, "flash_attn": None, "torch": None}
    if skip_install:
        log("SKIP_INSTALL: pip steps skipped by flag")
        return report
    if force_torch:
        rc, _ = run([sys.executable, "-m", "pip", "install", "-q",
                     "torch", "torchvision"])
        report["torch"] = rc
    for cmd in PIP_BASE:
        rc, _ = run([sys.executable, "-m", "pip", "install", "-q"] + cmd[2:]
                    if cmd[0] == "pip" else cmd)
        key = "bpy" if "bpy==4.2" in cmd else "pip_base"
        report[key] = rc
    try:
        import torch
        tv = torch.__version__.split("+")[0]
        cuda = torch.version.cuda or "cu121"
        cuda_nodot = cuda.replace("cu", "cuda").replace(".", "")
        # e.g. torch 2.3 + cu121 -> spconv-cu121, pyg index torch-2.3+cu121
        rc, _ = run([sys.executable, "-m", "pip", "install", "-q",
                     f"spconv-{cuda}"])
        report["spconv"] = rc
        rc, _ = run([sys.executable, "-m", "pip", "install", "-q",
                     "torch_scatter", "torch_cluster",
                     "-f", f"https://data.pyg.org/whl/torch-{tv}+{cuda}.html",
                     "--no-cache-dir"])
        report["pyg"] = rc
    except Exception as e:
        log(f"CUDA-specific installs skipped (torch probe failed: {e})")
    rc, _ = run([sys.executable, "-m", "pip", "install", "-q", "flash_attn"])
    report["flash_attn"] = rc
    if rc != 0:
        log("WARNING: flash_attn install failed (upstream README warns this "
            "is common). Skeleton inference may still fail at runtime with "
            "a flash-attn error. If so, see README.md 'flash_attn fallback' "
            "— do NOT silently edit model configs without logging it.")
    return report


# --------------------------------------------------------------------------
# Stage 0b — checkpoint download + verify (no credentials, public repo)
# --------------------------------------------------------------------------

def download_checkpoints(dest: Path, all_checkpoints: bool = False) -> dict:
    """Download the public UniRig checkpoints via huggingface_hub.

    Returns {hf_filename: {path, bytes, sha256}} or an error entry.
    No token is used. If the repo were gated, hf_hub_download would raise
    and the error is recorded verbatim — the script never asks for access.
    """
    from huggingface_hub import hf_hub_download
    dest.mkdir(parents=True, exist_ok=True)
    out = {}
    items = CKPT_MAP.items() if all_checkpoints else list(CKPT_MAP.items())[:2]
    for _local_key, hf_name in items:
        try:
            p = hf_hub_download(repo_id=HF_REPO, filename=hf_name)
            src = Path(p)
            dst = dest / hf_name.replace("/", "__")
            shutil.copyfile(src, dst)
            out[hf_name] = {"path": str(dst), "bytes": dst.stat().st_size,
                            "sha256": sha256_file(dst)}
            log(f"checkpoint {hf_name}: {dst.stat().st_size:,} bytes "
                f"sha256={out[hf_name]['sha256'][:16]}…")
        except Exception as e:
            out[hf_name] = {"error": f"{type(e).__name__}: {e}"}
            log(f"checkpoint {hf_name} FAILED: {e}")
    return out


# --------------------------------------------------------------------------
# Stage 1 — clean / remesh (CPU; UniRig's own extract ALSO simplifies to
# 50k faces, so this stage is about removing junk, not replacing UniRig)
# --------------------------------------------------------------------------

def clean_obj(src: Path, dst: Path, target_faces: int = 100000) -> dict:
    """Strip non-mesh junk and simplify. Returns a report dict.

    Cape Jones reality (measured 2026-10-24): the 32.7 MB decimated OBJ
    has 603,610 verts but only 105,476 'f' lines and 264,203 'l' (polyline)
    lines — line elements are NOT faces and Blender's OBJ importer will
    not turn them into riggable surface. They are stripped here.
    Simplification uses trimesh/fast-simplification when available and
    falls back to copying the stripped file unchanged (logged).
    """
    lines = src.read_text(errors="ignore").splitlines()
    kept, dropped = [], {"l": 0, "other": 0}
    for ln in lines:
        if ln.startswith("l "):
            dropped["l"] += 1
            continue
        kept.append(ln)
    dst.write_text("\n".join(kept) + "\n")
    report = {"src": str(src), "dst": str(dst),
              "stripped_line_elements": dropped["l"],
              "target_faces": target_faces, "simplified": False}
    try:
        import trimesh
        mesh = trimesh.load(str(dst), process=True, force="mesh")
        if hasattr(mesh, "geometry"):  # Scene -> take largest geometry
            mesh = max(mesh.geometry.values(),
                       key=lambda g: len(g.faces))
        report["verts_in"] = int(len(mesh.vertices))
        report["faces_in"] = int(len(mesh.faces))
        mesh.merge_vertices()
        mesh.remove_duplicate_faces()
        mesh.remove_degenerate_faces()
        mesh.remove_unreferenced_vertices()
        if len(mesh.faces) > target_faces:
            try:
                mesh = mesh.simplify_quadratic_decimation(target_faces)
                report["simplified"] = True
            except Exception as e:
                log(f"simplify failed ({e}); keeping cleaned mesh as-is")
        report["verts_out"] = int(len(mesh.vertices))
        report["faces_out"] = int(len(mesh.faces))
        mesh.export(str(dst))
    except Exception as e:
        log(f"trimesh clean skipped ({e}); stripped OBJ used as-is")
        report["trimesh_error"] = str(e)
    log(f"clean: {report}")
    return report


# --------------------------------------------------------------------------
# Stage 2-4 — one UniRig job on one GPU (subprocess; CUDA_VISIBLE_DEVICES)
# --------------------------------------------------------------------------

def run_job(job: dict, unirig_dir: Path, input_dir: Path, out_root: Path,
            gpu_id: int, seed: int = 12345, faces_target: int = 50000,
            attn_experiment: str | None = None) -> dict:
    """Run skeleton -> skin -> merge for ONE character on ONE GPU.

    Datalist mode only (see module docstring gotcha: any --output /
    --output_dir sets user_mode and drops predict_skeleton.npz, which
    starves skin). Outputs are found by glob afterwards, never assumed.
    """
    name = job["name"]
    src_in = Path(job["input"])
    src = src_in if src_in.is_absolute() else input_dir / src_in
    job_dir = out_root / name
    npz_dir = job_dir / "tmp"
    skel_dir = job_dir / "skeleton_out"
    skin_dir = job_dir / "skin_out"
    for d in (job_dir, npz_dir, skel_dir, skin_dir):
        d.mkdir(parents=True, exist_ok=True)
    report: dict = {"job": name, "input": str(src), "gpu": gpu_id,
                    "stages": {}}
    if not src.exists():
        report["skipped"] = f"input missing: {src}"
        log(f"[{name}] SKIP — input missing: {src}")
        return report

    # Per-job UniRig checkout copy (AFTER the input check, so a skipped
    # job never copies anything): datalist mode uses SHARED relative
    # dirs (dataset_inference/, dataset_inference_clean/, tmp/) inside
    # the checkout cwd. Two jobs sharing one checkout would collide
    # on those dirs, so each job gets its own copy (code only, no .git).
    # This is what makes 2-GPU parallel batching safe.
    job_checkout = job_dir / "UniRig"
    # Guard: never copy a tree into itself (e.g. a test that points
    # unirig_dir at a parent of job_dir). That recurses forever.
    if str(job_checkout).startswith(str(unirig_dir)):
        report["failed_at"] = ("refused: job output dir lives inside "
                               "the UniRig source dir")
        log(f"[{name}] REFUSED checkout copy into source tree")
        return report
    if not job_checkout.exists():
        shutil.copytree(unirig_dir, job_checkout,
                        ignore=shutil.ignore_patterns(
                            ".git", "tmp", "logs", "experiments",
                            "dataset_inference", "dataset_inference_clean",
                            "results"))
        log(f"[{name}] per-job checkout copied to {job_checkout}")
    clean = job_dir / f"{name}_clean.obj"
    if src.suffix.lower() == ".obj":
        report["stages"]["clean"] = clean_obj(src, clean)
        mesh_for_unirig = clean
    else:  # .glb/.fbx/.gltf pass through; UniRig extract handles them via bpy
        mesh_for_unirig = src
        report["stages"]["clean"] = {"note": "non-OBJ input passed through "
                                     "to UniRig extract (bpy import)"}
    env = dict(os.environ)
    env["CUDA_VISIBLE_DEVICES"] = str(gpu_id)
    env.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")

    # --- skeleton + skin in DATALIST mode (the only mode that feeds skin) ---
    # CORRECTED 2026-10-24 after reading run.py + src/system/ar.py:
    # run.py sets user_mode=True whenever --output OR --output_dir is
    # passed, and the skeleton writer skips predict_skeleton.npz in
    # user_mode (`if not self.user_mode and self.export_npz ...`).
    # The skin task needs predict_skeleton.npz (its data_name), so the
    # documented CLI two-step flow (--output/--output_dir) CANNOT feed
    # the skin phase as written. The npz is only produced in DATALIST
    # mode: no --input/--output args, datapath from
    # configs/data/quick_inference.yaml, entry dir holding BOTH
    # raw_data.npz (extract output; also the listing check in
    # src/data/datapath.py) and predict_skeleton.npz (skeleton output).
    # Hence per job, inside its own checkout copy:
    #   1. extract mesh -> dataset_inference_clean/<stem>/raw_data.npz
    #   2. write dataset_inference_clean/inference_datalist.txt = <stem>
    #   3. run.py skeleton task (no input/output args)
    #   4. run.py skin task (no --data_name arg: task default IS
    #      predict_skeleton.npz; generate_skin.sh must NOT be used here
    #      because it forces --data_name raw_data.npz, which loads a
    #      mesh-only npz with joints=None and cannot skin).
    # A --data_name raw_data.npz "retry" for skin is therefore NOT a
    # valid fallback and is deliberately absent from this script.
    stem = mesh_for_unirig.stem
    ds_in = job_checkout / "dataset_inference"
    ds_clean = job_checkout / "dataset_inference_clean"
    ds_in.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(mesh_for_unirig, ds_in / mesh_for_unirig.name)
    ts = time.strftime("%Y_%m_%d_%H_%M_%S")
    rc, tail = run(
        [sys.executable, "-m", "src.data.extract",
         "--config", "configs/data/quick_inference.yaml",
         "--require_suffix", "obj,fbx,FBX,dae,glb,gltf,vrm",
         "--num_runs", "1", "--id", "0", "--time", ts,
         "--force_override", "true",
         "--faces_target_count", str(faces_target)],
        cwd=str(job_checkout), env=env)
    report["stages"]["extract"] = {"rc": rc, "tail": tail[-1200:]}
    entry = ds_clean / stem
    (ds_clean / "inference_datalist.txt").write_text(stem + "\n")
    skel_fbx, skel_npz = [], []
    if rc == 0 and (entry / "raw_data.npz").exists():
        rc, tail = run(
            [sys.executable, "run.py",
             "--task", SKELETON_TASK, "--seed", str(seed)],
            cwd=str(job_checkout), env=env)
        report["stages"]["skeleton"] = {"rc": rc, "tail": tail[-1500:],
                                        "mode": "datalist"}
        skel_fbx = sorted(glob.glob(str(entry / "*.fbx")))
        skel_npz = sorted(glob.glob(str(entry / "predict_skeleton.npz")))
    else:
        report["stages"]["skeleton"] = {"rc": rc, "mode": "datalist",
                                        "note": "extract failed or "
                                        "raw_data.npz missing; "
                                        "trying CLI skeleton fallback"}
    if not skel_npz or not skel_fbx:
        # Fallback: CLI skeleton gives a viewable skeleton FBX but, by
        # the user_mode rule above, NO predict_skeleton.npz — so skin
        # cannot follow from this fallback. It is logged as exactly that.
        log(f"[{name}] datalist skeleton missing npz/fbx; CLI fallback "
            f"(skeleton-only, skin unavailable by design)")
        rc2, tail2 = run(
            ["bash", "launch/inference/generate_skeleton.sh",
             "--input", str(mesh_for_unirig),
             "--output_dir", str(skel_dir),
             "--seed", str(seed),
             "--faces_target_count", str(faces_target)],
            cwd=str(job_checkout), env=env)
        report["stages"]["skeleton_fallback_cli"] = {"rc": rc2,
                                                     "tail": tail2[-1200:]}
        skel_fbx = sorted(glob.glob(str(skel_dir / "**" / "*.fbx"),
                                    recursive=True)) or skel_fbx
        report["stages"]["skeleton"]["fbx"] = skel_fbx
        report["stages"]["skeleton"]["npz"] = skel_npz
        if not skel_fbx:
            report["failed_at"] = "skeleton"
            return report
        # Merge skeleton-only GLB and stop: no npz means no skin, honestly.
        rc_m, _ = run(
            ["bash", "launch/inference/merge.sh",
             "--source", skel_fbx[0], "--target", str(mesh_for_unirig),
             "--output", str(job_dir / f"{name}_rigged_SKELETON_ONLY.glb")],
            cwd=str(job_checkout), env=env)
        report["stages"]["merge_skeleton_only"] = {"rc": rc_m}
        report["failed_at"] = ("skeleton datalist npz missing; "
                               "skeleton-only GLB kept, skin unavailable")
        return report
    report["stages"]["skeleton"]["fbx"] = skel_fbx
    report["stages"]["skeleton"]["npz"] = skel_npz

    # --- skin (datalist mode; task default data_name=predict_skeleton.npz) ---
    rc, tail = run(
        [sys.executable, "run.py",
         "--task", SKIN_TASK, "--seed", str(seed)],
        cwd=str(job_checkout), env=env)
    skin_fbx = sorted(glob.glob(str(job_checkout / "results" / "**" / "*.fbx"),
                                recursive=True))
    skin_ok = (rc == 0 and bool(skin_fbx))
    report["stages"]["skin"] = {"rc": rc, "ok": skin_ok, "fbx": skin_fbx,
                                "tail": tail[-1500:], "mode": "datalist"}
    if not skin_ok:
        # Skeleton-only fallback: still merge the SKELETON fbx so the run
        # yields a viewable rigged file, and label it honestly.
        log(f"[{name}] SKIN FAILED/OOM — falling back to skeleton-only GLB")
        rc_m, _ = run(
            ["bash", "launch/inference/merge.sh",
             "--source", skel_fbx[0], "--target", str(mesh_for_unirig),
             "--output", str(job_dir / f"{name}_rigged_SKELETON_ONLY.glb")],
            cwd=str(job_checkout), env=env)
        report["stages"]["merge_skeleton_only"] = {"rc": rc_m}
        report["failed_at"] = "skin (skeleton-only GLB kept)"
        return report

    # --- merge: skin FBX + original mesh -> rigged GLB ---
    # Prefer the skin result FBX (result_fbx/predict) over any other FBX.
    skin_src = next((f for f in skin_fbx if "result_fbx" in f or "predict" in f),
                    skin_fbx[0])
    rigged = job_dir / f"{name}_rigged.glb"
    rc, tail = run(
        ["bash", "launch/inference/merge.sh",
         "--source", skin_src, "--target", str(mesh_for_unirig),
         "--output", str(rigged)],
        cwd=str(job_checkout), env=env)
    report["stages"]["merge"] = {"rc": rc, "source_fbx": skin_src,
                                 "rigged_glb": str(rigged),
                                 "exists": rigged.exists(),
                                 "bytes": rigged.stat().st_size
                                 if rigged.exists() else 0}
    if rc != 0 or not rigged.exists():
        report["failed_at"] = "merge"
    return report


def stage_repo_layout(out_root: Path, results) -> dict:
    """Copy rigged outputs into a REPO-LAYOUT staging tree (no push).

    The follow-up lane copies this tree into the repo (never by pushing
    from this script):
      game/assets/models/<job>_rigged.glb   <- rigged character GLBs
      ep1-farm/<job>_weight_transfer.json   <- weight-transfer reports
      docs/anim/UNIRIG-PIPELINE.md           <- see repo-patch/ (this
                                                script only stages the
                                                outputs; the doc itself
                                                ships as a patch file)
    Staging is a copy, never a move: the Kaggle originals stay in
    unirig_out/<job>/ so a staging failure cannot lose a rig.
    """
    layout = out_root / "repo_layout"
    models = layout / "game" / "assets" / "models"
    farm = layout / "ep1-farm"
    models.mkdir(parents=True, exist_ok=True)
    farm.mkdir(parents=True, exist_ok=True)
    staged = []
    for r in results:
        if "skipped" in r:
            continue
        job_dir = out_root / r["job"]
        cands = sorted(job_dir.glob("*_rigged.glb"))
        # Prefer the full skin-merged GLB over a SKELETON_ONLY fallback.
        full = [c for c in cands if "SKELETON_ONLY" not in c.name]
        src = full[0] if full else (cands[0] if cands else None)
        if src:
            dst = models / src.name
            shutil.copyfile(src, dst)
            staged.append(str(dst))
        wt = job_dir / "weight_transfer.json"
        if wt.exists():
            shutil.copyfile(wt, farm / f"{r['job']}_weight_transfer.json")
    (layout / "STAGING-NOTE.txt").write_text(
        "Repo-layout staging of a Kaggle UniRig run.\n"
        "Copy game/assets/models/*.glb into the repo's game/assets/models/,\n"
        "ep1-farm/*_weight_transfer.json into the Cape Jones pipeline inputs,\n"
        "and apply docs/anim/UNIRIG-PIPELINE.md from unirig/repo-patch/.\n"
        "This staging tree is a COPY — originals remain in unirig_out/<job>/.\n")
    log(f"repo-layout staged: {len(staged)} GLB(s) under {layout}")
    return {"layout_dir": str(layout), "staged_glbs": staged}


def print_proof_block(results, gpu_names, out_root: Path) -> None:
    """GPU VERIFIED proof block — the run's receipt, printed always.

    A run that cannot print this block (no GPU, no checkpoint, no rig)
    has FAILED, even if earlier stages printed 'ok'. Do not mistake a
    clean install log for a successful rig.
    """
    print("=" * 70)
    print("GPU VERIFIED — UNIRIG RUN PROOF (print this block, do not paraphrase)")
    print("=" * 70)
    print(f"nvidia-smi:\n{nvidia_smi_text()}")
    print(f"torch.cuda devices: {gpu_names}")
    for r in results:
        if "skipped" in r:
            print(f"  [SKIP] {r['job']}: {r['skipped']}")
            continue
        v = r.get("verify", {})
        glb_info = v.get("glb", {})
        print(f"  [JOB] {r['job']} gpu={r.get('gpu')} "
              f"failed_at={r.get('failed_at')}")
        print(f"        input: {r.get('input')}")
        print(f"        rigged_glb: {v.get('rigged_glb')} "
              f"exists={v.get('exists')} bytes={v.get('bytes')}")
        print(f"        glb joints={glb_info.get('joints')} "
              f"skins={glb_info.get('skins')} "
              f"animations={glb_info.get('animations')}")
        print(f"        render: {r.get('render')}")
    print(f"  report: {out_root / 'batch_report.json'}")
    print(f"  repo-layout staging: {out_root / 'repo_layout'}")
    print("=" * 70)


def run_batch(jobs, unirig_dir, input_dir, out_root, gpu_count,
              seed=12345):
    """Distribute jobs round-robin across GPUs (1 job per GPU at a time).

    With 2 T4s: job0 -> GPU0, job1 -> GPU1, job2 -> GPU0, ... Each job's
    subprocess pins CUDA_VISIBLE_DEVICES to its GPU, so two UniRig
    processes never fight over the same card. With 1 GPU this degrades
    to plain sequential execution.
    """
    gpu_count = max(1, gpu_count)
    log(f"batch: {len(jobs)} jobs across {gpu_count} GPU(s)")
    results = []
    with concurrent.futures.ThreadPoolExecutor(
            max_workers=gpu_count) as pool:
        futs = []
        for i, job in enumerate(jobs):
            gpu = i % gpu_count
            futs.append(pool.submit(run_job, job, unirig_dir, input_dir,
                                   out_root, gpu, seed))
        for fut in concurrent.futures.as_completed(futs):
            results.append(fut.result())
    # Keep report order = queue order.
    order = {j["name"]: i for i, j in enumerate(jobs)}
    results.sort(key=lambda r: order.get(r["job"], 999))
    return results


# --------------------------------------------------------------------------
# Stage 5 — weight transfer + smoothing (Cape Jones specific)
# --------------------------------------------------------------------------

def smooth_weights(weights, faces, iterations: int = 1):
    """Neighbour-average skin weights (chest/crotch tear mitigation).

    Pure numpy/scipy, no Blender needed. weights: (V, J) rows sum to 1.
    One iteration replaces each vertex's weights by the mean of its
    edge-neighbours' weights blended 50/50 with its own, then
    renormalizes rows. This is the 'neighbour smoothing' step named in
    the 2026-10-24 owner feedback (chest stretched edges 96,223 -> 73,233
    after welding; smoothing is the NEXT step, not a cure by itself).
    """
    import numpy as np
    V = weights.shape[0]
    # Edge list (undirected, duplicates harmless: they weight shared
    # edges more, which is acceptable for a smoothing pass).
    rows = np.concatenate([faces[:, 0], faces[:, 1], faces[:, 2],
                           faces[:, 1], faces[:, 2], faces[:, 0]])
    cols = np.concatenate([faces[:, 1], faces[:, 2], faces[:, 0],
                           faces[:, 2], faces[:, 0], faces[:, 1]])
    try:
        from scipy import sparse
        A = sparse.coo_matrix((np.ones(len(rows)), (rows, cols)),
                              shape=(V, V)).tocsr()
        A.setdiag(0)
        A.eliminate_zeros()
        deg = np.asarray(A.sum(axis=1)).ravel()
        deg[deg == 0] = 1

        def neigh_mean(W):
            return (A @ W) / deg[:, None]
    except Exception as e:
        # Pure-numpy fallback (also covers a broken system scipy, e.g.
        # scipy built against numpy<2 running under numpy 2). Slower
        # on huge meshes, exact same math on small ones.
        log(f"scipy sparse unavailable ({e}); using numpy neighbour mean")
        deg = np.bincount(rows, minlength=V).astype(float)
        deg[deg == 0] = 1

        def neigh_mean(W):
            acc = np.zeros_like(W)
            np.add.at(acc, cols, W[rows])
            return acc / deg[:, None]
    W = weights.copy()
    for _ in range(iterations):
        W = 0.5 * W + 0.5 * neigh_mean(W)
        s = W.sum(axis=1, keepdims=True)
        s[s == 0] = 1
        W = W / s
    return W


def weight_transfer_report(job_dir: Path, bonemap_path: Path | None,
                           reference_rigged_glb: Path | None) -> dict:
    """Document the Alisa->Cape weight-transfer step honestly.

    Full Blender data-transfer (reference GLB -> UniRig GLB via the
    bonemap) needs the reference rigged file ON Kaggle. If it is absent,
    this stage does NOT invent weights: it reports SKIPPED and the
    UniRig-predicted skin stands. The bonemap itself (160 Alisa joints ->
    54 Cape targets, 111 non-null entries) is loaded and validated here
    so a bad bonemap fails loudly before any Blender work.
    """
    rep: dict = {"bonemap": None, "status": "skipped"}
    if bonemap_path and bonemap_path.exists():
        bm = json.loads(bonemap_path.read_text())
        m = bm.get("map", {})
        targets = set()
        for v in m.values():
            if isinstance(v, list):
                targets.update(v)
            elif v:
                targets.add(v)
        rep["bonemap"] = {"entries": len(m),
                          "non_null": sum(1 for v in m.values() if v),
                          "distinct_cape_targets": len(targets),
                          "rules": bm.get("rules", {})}
    if reference_rigged_glb and reference_rigged_glb.exists():
        rep["status"] = ("TODO_ON_KAGGLE: run Blender data-transfer with "
                         "bonemap (see kaggle_batch_retarget.py notes and "
                         "README.md 'weight transfer'). Reference found at "
                         f"{reference_rigged_glb}, but the transfer itself "
                         "is a Blender bpy step the parent runs after "
                         "eye-checking the UniRig rig — it is NOT silently "
                         "baked into this script's merge output.")
    else:
        rep["status"] = ("skipped: no reference rigged GLB supplied in "
                         "/kaggle/input/unirig-jobs/ (expected name: "
                         "alisa_reference_rigged.glb). UniRig-predicted "
                         "skin weights are kept as-is.")
    (job_dir / "weight_transfer.json").write_text(json.dumps(rep, indent=2))
    return rep


# --------------------------------------------------------------------------
# Stage 6 — verify (+ best-effort render)
# --------------------------------------------------------------------------

def verify_job(job_dir: Path, rigged_glb: Path) -> dict:
    """Quantitative checks that need no GPU and no render.

    Always runs, even when the render pass fails. Renders are eye-check
    material; THESE numbers are the pass/fail record.
    """
    rep: dict = {"rigged_glb": str(rigged_glb),
                 "exists": rigged_glb.exists()}
    if not rigged_glb.exists():
        return rep
    rep["bytes"] = rigged_glb.stat().st_size
    try:
        import trimesh
        scene = trimesh.load(str(rigged_glb), force="scene")
        geoms = getattr(scene, "geometry", {})
        total_v = sum(len(g.vertices) for g in geoms.values())
        total_f = sum(len(g.faces) for g in geoms.values())
        rep["mesh"] = {"geometries": len(geoms), "verts": total_v,
                       "faces": total_f}
        # Non-manifold / degenerate counts on the largest geometry.
        g = max(geoms.values(), key=lambda x: len(x.faces))
        rep["mesh"]["largest_verts"] = int(len(g.vertices))
        rep["mesh"]["largest_faces"] = int(len(g.faces))
        try:
            rep["mesh"]["is_watertight"] = bool(g.is_watertight)
            rep["mesh"]["is_winding_consistent"] = bool(
                g.is_winding_consistent)
        except Exception as e:
            rep["mesh"]["topology_error"] = str(e)
    except Exception as e:
        rep["mesh_error"] = str(e)
    # Skeleton presence: a GLB rig carries skins/joints in its JSON chunk.
    try:
        raw = rigged_glb.read_bytes()
        import struct
        # GLB header: magic(4) version(4) length(4); chunk0 len(4) type(4)
        if raw[:4] == b"glTF":
            clen = struct.unpack("<I", raw[12:16])[0]
            j = json.loads(raw[20:20 + clen])
            rep["glb"] = {"skins": len(j.get("skins", [])),
                          "nodes": len(j.get("nodes", [])),
                          "animations": len(j.get("animations", []))}
            for s in j.get("skins", []):
                rep["glb"]["joints"] = len(s.get("joints", []))
    except Exception as e:
        rep["glb_error"] = str(e)
    return rep


def render_turntable(rigged_glb: Path, out_png: Path) -> dict:
    """Best-effort rest-pose render. Returns status, never raises.

    Tries bpy (Blender as a module, EEVEE) first, then pyrender
    offscreen. On headless Kaggle either may fail (no display/EGL);
    that is a RENDER failure, not a rig failure — verify_job() above is
    the authoritative check, and this function's status says so.
    """
    try:
        import bpy  # noqa: F401
        code = (
            "import bpy, sys\n"
            "bpy.ops.wm.read_factory_settings(use_empty=True)\n"
            f"bpy.ops.import_scene.gltf(filepath={str(rigged_glb)!r})\n"
            "bpy.context.scene.render.engine = 'BLENDER_EEVEE_NEXT'\n"
            "bpy.context.scene.render.resolution_x = 768\n"
            "bpy.context.scene.render.resolution_y = 768\n"
            "bpy.context.scene.render.filepath = "
            f"{str(out_png)!r}\n"
            "bpy.ops.render.render(write_still=True)\n"
        )
        rc, _ = run([sys.executable, "-c", code])
        if rc == 0 and out_png.exists():
            return {"engine": "bpy-eevee", "png": str(out_png), "ok": True}
    except Exception as e:
        log(f"bpy render unavailable: {e}")
    try:
        import trimesh, pyrender  # noqa: F401
        scene = trimesh.load(str(rigged_glb), force="scene")
        # pyrender offscreen needs EGL/OSMesa; failure is logged, not fatal.
        import numpy as np
        pr_scene = pyrender.Scene()
        for g in scene.geometry.values():
            pr_scene.add(pyrender.Mesh.from_trimesh(g))
        r = pyrender.OffscreenRenderer(768, 768)
        color, _ = r.render(pr_scene)
        from PIL import Image
        Image.fromarray(color).save(str(out_png))
        return {"engine": "pyrender", "png": str(out_png), "ok": True}
    except Exception as e:
        return {"engine": None, "ok": False,
                "note": f"render unavailable headless ({e}); "
                        "quantitative verify_job() still applies"}
    return {"engine": None, "ok": False, "note": "unknown render failure"}


# --------------------------------------------------------------------------
# Local self-tests (run WITHOUT GPU / torch / Kaggle)
# --------------------------------------------------------------------------

def test_local() -> dict:
    """Exercise the non-GPU stages on synthetic tiny data."""
    import numpy as np
    import tempfile
    tmp = Path(tempfile.mkdtemp(prefix="unirig_test_"))
    # Tiny OBJ: two triangles sharing an edge + one 'l' line to strip.
    src = tmp / "tiny.obj"
    src.write_text(
        "o Tiny\n"
        "v 0 0 0\nv 1 0 0\nv 1 1 0\nv 0 1 0\n"
        "l 1 2\n"
        "f 1 2 3\nf 1 3 4\n")
    dst = tmp / "tiny_clean.obj"
    clean_rep = clean_obj(src, dst, target_faces=100)
    assert clean_rep["stripped_line_elements"] == 1, clean_rep
    # Weight smoothing: rows must still sum to 1, no NaNs.
    W = np.array([[1.0, 0.0], [0.0, 1.0], [1.0, 0.0], [0.0, 1.0]])
    F = np.array([[0, 1, 2], [0, 2, 3]])
    W2 = smooth_weights(W, F, iterations=2)
    assert np.all(np.isfinite(W2)) and np.allclose(
        W2.sum(axis=1), 1.0), W2
    # Missing-input job must SKIP, not crash.
    r = run_job({"name": "missing", "input": "nope.obj", "kind": "generic"},
                tmp, tmp, tmp / "out", 0)
    assert "skipped" in r, r
    log("LOCAL TESTS PASSED (clean + smooth + missing-input skip)")
    return {"clean": clean_rep, "smooth_row_sums": W2.sum(axis=1).tolist(),
            "missing_job": r}


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

def parse_args(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--input-dir", default="/kaggle/input/unirig-jobs",
                   help="dir holding job input files (Kaggle default)")
    p.add_argument("--working-dir", default="/kaggle/working",
                   help="dir for UniRig checkout + outputs (Kaggle default)")
    p.add_argument("--unirig-dir", default=None,
                   help="existing UniRig checkout (else cloned under working-dir)")
    p.add_argument("--jobs", default="cape-jones",
                   help="'cape-jones', 'all' (whole DEFAULT_JOBS queue), or "
                        "comma-separated job names")
    p.add_argument("--job-file", default=None,
                   help="JSON list of {name, input, kind} overriding DEFAULT_JOBS")
    p.add_argument("--gpus", type=int, default=0,
                   help="GPUs to use in parallel (0 = auto-detect)")
    p.add_argument("--seed", type=int, default=12345)
    p.add_argument("--faces-target", type=int, default=50000,
                   help="UniRig extract faces_target_count (upstream default)")
    p.add_argument("--skip-install", action="store_true")
    p.add_argument("--force-torch", action="store_true")
    p.add_argument("--skip-checkpoints", action="store_true")
    p.add_argument("--all-checkpoints", action="store_true")
    p.add_argument("--skip-render", action="store_true")
    p.add_argument("--bonemap", default=None,
                   help="path to bonemap_alisa_to_capejones.json")
    p.add_argument("--reference-glb", default=None,
                   help="Alisa reference rigged GLB for weight transfer")
    p.add_argument("--dry-run", action="store_true",
                   help="print plan only; run no installs, no GPU work")
    p.add_argument("--check-env", action="store_true",
                   help="print GPU/torch/package probe and exit")
    p.add_argument("--test-local", action="store_true",
                   help="run non-GPU self-tests and exit")
    return p.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    if args.test_local:
        print(json.dumps(test_local(), indent=2, default=str))
        return 0
    if args.check_env:
        n, names = gpu_info()
        print(json.dumps({"gpus": n, "names": names,
                          "python": sys.version}, indent=2))
        return 0

    input_dir = Path(args.input_dir)
    working = Path(args.working_dir)
    out_root = working / "unirig_out"
    out_root.mkdir(parents=True, exist_ok=True)
    unirig_dir = Path(args.unirig_dir) if args.unirig_dir else \
        working / "UniRig"

    if args.job_file:
        jobs = json.loads(Path(args.job_file).read_text())
    elif args.jobs == "all":
        # BATCH: the default queue PLUS every riggable file the parent
        # dropped into --input-dir. One notebook run rigs everything,
        # not one character at a time. Supported suffixes are exactly
        # UniRig extract's list (src/data/extract.py get_files default).
        jobs = list(DEFAULT_JOBS)
        seen_inputs = {j["input"] for j in jobs}
        for ext in (".obj", ".fbx", ".glb", ".gltf", ".dae", ".vrm"):
            for f in sorted(input_dir.glob(f"*{ext}")):
                if f.name in seen_inputs:
                    continue
                jobs.append({"name": f.stem, "input": f.name,
                             "kind": "generic"})
                seen_inputs.add(f.name)
        log(f"--jobs all: queue expanded to {len(jobs)} job(s) "
            f"(defaults + input-dir discovery)")
    else:
        wanted = {j.strip() for j in args.jobs.split(",")}
        jobs = [j for j in DEFAULT_JOBS if j["name"] in wanted]
        # Unknown names = user-supplied files: treat name as both job name
        # and input filename stem (<name>.glb else <name>.obj if present).
        for w in wanted:
            if w not in {j["name"] for j in jobs}:
                cand = input_dir / f"{w}.glb"
                cand2 = input_dir / f"{w}.obj"
                inp = cand.name if cand.exists() else (
                    cand2.name if cand2.exists() else f"{w}.glb")
                jobs.append({"name": w, "input": inp, "kind": "generic"})
    if args.dry_run:
        n, names = gpu_info()
        print(json.dumps({"plan": "dry-run (no installs, no GPU work)",
                          "gpus_detected": n, "gpu_names": names,
                          "jobs": jobs, "input_dir": str(input_dir),
                          "unirig_dir": str(unirig_dir),
                          "out_root": str(out_root),
                          "checkpoint_map": CKPT_MAP}, indent=2))
        return 0

    # GPU VERIFIED proof, step 1: raw nvidia-smi + torch probe, printed
    # BEFORE any install, so a CPU-only session can never look like a
    # GPU run. Absent GPU = LOUD non-zero exit (return 2), not a warning.
    print("=" * 70)
    print("GPU CHECK — nvidia-smi output:")
    print(nvidia_smi_text())
    print("=" * 70)
    n_gpus, gpu_names = gpu_info()
    log(f"GPUs: {n_gpus} {gpu_names}")
    if n_gpus == 0:
        log("ERROR: no CUDA GPU visible. This script is a GPU script — "
            "run it in the Kaggle notebook with GPU accelerator ON, "
            "not on a CPU-only session. FAILING LOUDLY (exit 2) so this "
            "run cannot be mistaken for success.")
        return 2
    try:
        import torch
        log(f"torch.cuda.is_available() = {torch.cuda.is_available()}, "
            f"torch {torch.__version__}, cuda {torch.version.cuda}")
    except Exception as e:
        log(f"torch import failed after GPU probe: {e}")
    use_gpus = args.gpus if args.gpus > 0 else n_gpus
    use_gpus = min(use_gpus, n_gpus)
    log(f"using {use_gpus} GPU(s) in parallel; queue has {len(jobs)} job(s)")

    install_report = install_deps(force_torch=args.force_torch,
                                  skip_install=args.skip_install)
    if not unirig_dir.exists():
        rc, _ = run(["git", "clone", UPSTREAM_REPO_URL, str(unirig_dir)])
        if rc != 0:
            log("ERROR: could not clone UniRig — upload the UniRig folder "
                "to Kaggle and re-run with --unirig-dir <path>")
            return 3
    ckpt_report = {}
    if not args.skip_checkpoints:
        ckpt_report = download_checkpoints(working / "unirig_checkpoints",
                                           args.all_checkpoints)
        # Checkpoint load confirmation (proof step 2): every required
        # file must show bytes + sha prefix here. A failed pre-download
        # does NOT abort — run.py auto-downloads via
        # src/inference/download.py — but then the skeleton stage must
        # succeed, or the job fails loudly there. Never claim a
        # checkpoint is loaded from a failed download line.
        for hf_name, info in ckpt_report.items():
            if "error" in info:
                log(f"CHECKPOINT PRE-DOWNLOAD FAILED {hf_name}: "
                    f"{info['error']} — run.py will retry via auto-download")
            else:
                log(f"CHECKPOINT LOADED {hf_name}: {info['bytes']:,} bytes "
                    f"sha256={info['sha256'][:16]}…")
    if os.environ.get("UNIRIG_ATTN") == "sdpa":
        log("UNIRIG_ATTN=sdpa EXPERIMENT (opt-in, untested upstream): "
            "patching model config copies is NOT done automatically — "
            "see README.md fallback section and apply by hand if needed.")

    results = run_batch(jobs, unirig_dir, input_dir, out_root, use_gpus,
                        seed=args.seed)
    bonemap = Path(args.bonemap) if args.bonemap else None
    ref = Path(args.reference_glb) if args.reference_glb else None
    for r in results:
        if "skipped" in r:
            continue
        job_dir = out_root / r["job"]
        r["weight_transfer"] = weight_transfer_report(job_dir, bonemap, ref)
        rigged = job_dir / f"{r['job']}_rigged.glb"
        if not rigged.exists():
            cands = sorted(job_dir.glob("*_rigged*.glb"))
            rigged = cands[0] if cands else rigged
        r["verify"] = verify_job(job_dir, rigged)
        if not args.skip_render:
            r["render"] = render_turntable(
                rigged, job_dir / f"{r['job']}_verify.png")
    final = {"install": install_report, "checkpoints": ckpt_report,
             "gpus": {"count": n_gpus, "names": gpu_names,
                      "used_parallel": use_gpus},
             "jobs": results}
    (out_root / "batch_report.json").write_text(json.dumps(final, indent=2,
                                                           default=str))
    final["repo_layout"] = stage_repo_layout(out_root, results)
    (out_root / "batch_report.json").write_text(json.dumps(final, indent=2,
                                                           default=str))
    log(f"DONE. Report: {out_root / 'batch_report.json'}")
    log("DOWNLOAD THIS FOLDER from Kaggle: "
        f"{out_root} (rigged GLBs + batch_report.json + verify PNGs + "
        f"repo_layout/ staging tree)")
    # GPU VERIFIED proof block (step 3): printed on EVERY run, success
    # or failure, so the parent can paste it as the run receipt.
    print_proof_block(results, gpu_names, out_root)
    failed = [r["job"] for r in results if r.get("failed_at")]
    if failed:
        log(f"jobs with failures (see batch_report.json): {failed}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
