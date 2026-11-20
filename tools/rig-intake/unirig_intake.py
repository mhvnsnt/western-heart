#!/usr/bin/env python3
"""Western Heart UniRig auto-rig intake wrapper.

Takes an UNRIGGED mesh (GLB/OBJ/FBX) and produces a RIGGED GLB using UniRig
(SIGGRAPH 2025, MIT license, https://github.com/VAST-AI-Research/UniRig):
  stage 1 - skeleton prediction (autoregressive transformer)
  stage 2 - skinning weight prediction (bone-point cross-attention)
  stage 3 - merge predicted skin back onto the source mesh (bpy)

This wrapper is designed to run on a CUDA GPU machine (8GB+ VRAM).
The Tripo intake pipeline (tools/import_model.py) calls maybe_autorig():
when GPU + UniRig are present the mesh is rigged in place; otherwise it
returns None and the intake falls back to its existing behavior
(existing fail message / Tripo-Mixamo manual route).

Env:
  UNIRIG_ROOT        path to the UniRig repo clone (validated by run.py)
  WH_UNIRIG          "1" (default) / "0" -- master enable switch
  WH_UNIRIG_SEED     random seed for skeleton sampling (default 12345)

Usage:
  python3 tools/rig-intake/unirig_intake.py <input.glb> --out rigged.glb
  python3 tools/rig-intake/unirig_intake.py <input.glb> --out rigged.glb --workdir tmp/unirig
  python3 tools/rig-intake/unirig_intake.py --check     # env readiness probe, exit 0/1
"""
import argparse
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile

REPO = pathlib.Path("https://github.com/VAST-AI-Research/UniRig")
DEFAULT_SEED = int(os.environ.get("WH_UNIRIG_SEED", "12345"))
SUPPORTED_SUFFIXES = {".glb", ".gltf", ".obj", ".fbx", ".dae", ".vrm"}


def unirig_root():
    """Locate the UniRig checkout. Returns Path or None."""
    env = os.environ.get("UNIRIG_ROOT")
    candidates = []
    if env:
        candidates.append(pathlib.Path(env))
    # repo-relative default used by the crew's research checkout
    # (WH_UNIRIG_SKIP_DEFAULT=1 disables it -- used by tests)
    if os.environ.get("WH_UNIRIG_SKIP_DEFAULT", "0") != "1":
        candidates.append(pathlib.Path.home() / "workspace" / "research-pull" / "unirig" / "UniRig")
    for c in candidates:
        if (c / "run.py").exists() and (c / "launch" / "inference" / "generate_skeleton.sh").exists():
            return c
    return None


def gpu_available():
    """True when a CUDA GPU is visible. Never raises."""
    try:
        r = subprocess.run(["nvidia-smi", "-L"], capture_output=True, text=True, timeout=15)
        if r.returncode == 0 and r.stdout.strip():
            return True
    except Exception:
        pass
    try:
        import torch
        return bool(torch.cuda.is_available())
    except Exception:
        return False
    return False


def check_env(verbose=True):
    """Readiness probe. Returns (ok: bool, report: dict)."""
    report = {}
    report["wh_unirig_enabled"] = os.environ.get("WH_UNIRIG", "1") != "0"
    root = unirig_root()
    report["unirig_root"] = str(root) if root else None
    report["gpu_available"] = gpu_available()
    report["python_ok"] = sys.version_info[:2] >= (3, 10)
    ok = report["wh_unirig_enabled"] and root is not None and report["gpu_available"]
    report["ready"] = ok
    if verbose:
        for k, v in report.items():
            print(f"  {k}: {v}")
    return ok, report


def build_pipeline_commands(root, src, out, workdir, seed=DEFAULT_SEED):
    """Return the 3 UniRig stage commands (pure function, no side effects)."""
    root = str(root)
    src = str(src)
    out = str(out)
    workdir = str(workdir)
    npz_dir = os.path.join(workdir, "npz")
    skeleton_fbx = os.path.join(workdir, "skeleton.fbx")
    skin_fbx = os.path.join(workdir, "skin.fbx")
    stage1 = [
        "bash", os.path.join(root, "launch/inference/generate_skeleton.sh"),
        "--input", src, "--output", skeleton_fbx,
        "--npz_dir", npz_dir, "--seed", str(seed),
    ]
    stage2 = [
        "bash", os.path.join(root, "launch/inference/generate_skin.sh"),
        "--input", skeleton_fbx, "--output", skin_fbx,
        "--npz_dir", npz_dir, "--data_name", "raw_data.npz",
        "--seed", str(seed),
    ]
    stage3 = [
        "bash", os.path.join(root, "launch/inference/merge.sh"),
        "--source", skin_fbx, "--target", src, "--output", out,
    ]
    return [("skeleton", stage1), ("skin", stage2), ("merge", stage3)]


def rig_model(src, out, workdir=None, seed=DEFAULT_SEED, timeout_s=3600):
    """Run the full UniRig pipeline. Returns out path on success, raises on failure."""
    src = pathlib.Path(src)
    if not src.exists():
        raise FileNotFoundError(f"input not found: {src}")
    if src.suffix.lower() not in SUPPORTED_SUFFIXES:
        raise ValueError(f"unsupported input {src.suffix}; supported: {sorted(SUPPORTED_SUFFIXES)}")
    if os.environ.get("WH_UNIRIG", "1") == "0":
        raise RuntimeError("UniRig disabled via WH_UNIRIG=0")
    root = unirig_root()
    if root is None:
        raise RuntimeError(
            "UniRig checkout not found. Set UNIRIG_ROOT to the UniRig repo "
            f"({REPO}); setup: tools/rig-intake/UNIRIG-SETUP.md")
    if not gpu_available():
        raise RuntimeError("no CUDA GPU detected (UniRig needs 8GB+ VRAM)")
    workdir = pathlib.Path(workdir) if workdir else pathlib.Path(tempfile.mkdtemp(prefix="unirig_"))
    workdir.mkdir(parents=True, exist_ok=True)
    out = pathlib.Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    for name, cmd in build_pipeline_commands(root, src, out, workdir, seed):
        print(f"[unirig] stage: {name}")
        print("  " + " ".join(cmd))
        r = subprocess.run(cmd, cwd=str(root), timeout=timeout_s)
        if r.returncode != 0:
            raise RuntimeError(f"UniRig stage '{name}' failed (exit {r.returncode})")
    if not out.exists():
        raise RuntimeError(f"UniRig pipeline finished but output missing: {out}")
    print(f"[unirig] rigged: {out}")
    return str(out)


def maybe_autorig(src, workdir=None):
    """Graceful entry point for tools/import_model.py.

    Returns the rigged GLB path when UniRig is ready and succeeds,
    else None. NEVER raises -- the intake pipeline must not break
    because the GPU rig is unavailable.
    """
    try:
        tmp = pathlib.Path(workdir) if workdir else pathlib.Path(tempfile.mkdtemp(prefix="unirig_"))
        tmp.mkdir(parents=True, exist_ok=True)
        out = tmp / (pathlib.Path(src).stem + "_unirig_rigged.glb")
        return rig_model(src, out, workdir=tmp)
    except Exception as e:
        print(f"[unirig] auto-rig unavailable, falling back: {e}")
        return None


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("src", nargs="?", help="input mesh (.glb/.obj/.fbx)")
    ap.add_argument("--out", help="output rigged .glb path")
    ap.add_argument("--workdir", default=None, help="working dir (default: temp)")
    ap.add_argument("--seed", type=int, default=DEFAULT_SEED)
    ap.add_argument("--check", action="store_true", help="env readiness probe")
    a = ap.parse_args(argv)
    if a.check:
        ok, _ = check_env()
        print("UNIRIG READY" if ok else "UNIRIG NOT READY (see tools/rig-intake/UNIRIG-SETUP.md)")
        return 0 if ok else 1
    if not a.src or not a.out:
        ap.error("src and --out are required (or use --check)")
    print(rig_model(a.src, a.out, workdir=a.workdir, seed=a.seed))
    return 0


if __name__ == "__main__":
    sys.exit(main())
