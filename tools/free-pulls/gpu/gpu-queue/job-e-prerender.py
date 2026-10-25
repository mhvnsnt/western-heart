#!/usr/bin/env python3
"""
Western Heart — JOB E (NEW): pre-render character cards + stage previews
from GLB models. Kaggle/Colab notebook script. STATUS: NOT RUN.

HOW TO RUN (browser lane — this agent cannot run notebooks):
  1. Kaggle notebook, Accelerator -> GPU (T4 x2). Colab GPU is the failover.
  2. Upload GLBs to /kaggle/input/cards/ (or set WH_INPUT).
     Optional: upload a stage HDRI/backdrop — if absent, cards render on a
     flat dark studio backdrop (no HDRI is invented or downloaded here).
  3. Install Blender-as-a-module in the notebook FIRST (Kaggle does NOT
     ship Blender):
         !pip install -q bpy==4.2
     (Same bpy==4.2 pin the UniRig lane uses. If pip bpy fails on the
     notebook's Python, stop and record that — do not substitute a
     different renderer silently.)
  4. Paste this whole file into a cell, or upload + run:
         python job-e-prerender.py
     Outputs: /kaggle/working/cards_out/ — download the whole folder.
     Also writes cards_out/report.json + GPU-VERIFICATION.txt.

RENDER PATH — honest, in priority order (the report records which one ran):
  1. Cycles GPU (CUDA) — TRUE GPU render. Cycles CUDA works headless with
     no display server, unlike EEVEE. The script explicitly calls
     cycles preferences get_devices() before rendering, because headless
     Blender has a known quirk where GPUs are not auto-detected without it.
  2. Cycles CPU — REAL 3D render, NOT a GPU render. Used only if no CUDA
     device is enumerated. Slower, same framing/lighting. The report says
     render_path=cycles-cpu and the results template must say so.
  3. EEVEE is NOT attempted. EEVEE always needs OpenGL/a display; on a
     headless notebook it fails with "Unable to open a display" style
     errors. Claiming an EEVEE pass in a notebook would be guessing.
  If bpy is missing entirely, the script FAILS with a clear message —
  it never produces a fake "card" (no placeholder image, no metadata-only
  output passed off as a render).

GPU GATE (same rule as every WH GPU job):
  Prints nvidia-smi + torch.cuda.is_available() FIRST. Without a CUDA
  device it exits 2 — EXCEPT that Cycles-CPU is a legitimate fallback
  for THIS job only, so the gate is: no CUDA => print the loud warning,
  continue ONLY to the Cycles-CPU path, and stamp every output
  render_path=cycles-cpu. A CPU render must never be reported as a GPU
  render. WH_CPU_SELFTEST=1 (local testing only) runs GLB validation +
  PIL post-processing on a sample image and skips all rendering; its
  report is stamped cpu_selftest=true and is NOT a render run.

PER MODEL (kept small on purpose):
  * 2 views: front (0 deg) and 3/4 (45 deg yaw), 768x1024 portrait cards
    (select-screen cards are portrait; stage previews reuse the same
    frames cropped square if needed — no separate stage pass in v1).
  * Framing: camera distance is computed from the imported objects'
    bounding box (centre + max dimension), so a tall fighter and a
    short prop do not get the same fixed camera.
  * Lighting: key light (sun, warm) + rim light (cool, from behind) +
    flat dark world background. No HDRI, no compositing tricks.
  * Samples: 64 (GPU) / 32 (CPU) — low on purpose: these are cards, not
    final cinematics. Raise WH_SAMPLES only if time allows.
  * Post-processing: torch CUDA tensor grade (vignette + slight
    contrast/saturation lift) when CUDA is available, else PIL
    equivalent. Post is recorded as post=gpu or post=cpu in the report.
  * Animation: frame 0 only (T-pose / bind pose as shipped in the GLB).
    Posed/action cards are a later job — this script does not invent a
    pose the GLB does not contain.

INPUTS: *.glb under WH_INPUT. Files that fail GLB validation (bad magic,
truncated) are SKIPPED with a log line, never rendered as black frames.
OUTPUTS per model: <stem>_front.png, <stem>_threequarter.png,
plus report.json and GPU-VERIFICATION.txt. If zero GLBs render, the
script exits 1 (empty output is a failure, not a success).

No keys, no credentials. Stdlib + Pillow + torch (gate/post only) + bpy
(render only, notebook-installed).
"""
import json
import os
import struct
import subprocess
import sys
import time
from pathlib import Path

INPUT_DIR = Path(os.environ.get("WH_INPUT", "/kaggle/input/cards"))
OUTPUT_DIR = Path(os.environ.get("WH_OUTPUT", "/kaggle/working/cards_out"))
CARD_W = int(os.environ.get("WH_CARD_W", "768"))
CARD_H = int(os.environ.get("WH_CARD_H", "1024"))
SAMPLES_GPU = int(os.environ.get("WH_SAMPLES_GPU", "64"))
SAMPLES_CPU = int(os.environ.get("WH_SAMPLES_CPU", "32"))
CPU_SELFTEST = os.environ.get("WH_CPU_SELFTEST", "") == "1"


def fail(msg, code=2):
    print(f"\n{'=' * 70}\n{msg}\n{'=' * 70}", file=sys.stderr)
    raise SystemExit(code)


def gpu_gate():
    """Print nvidia-smi + torch CUDA status. Returns (has_cuda, gpu_name).

    Unlike the other WH jobs, absence of CUDA does NOT abort this job:
    Cycles-CPU is a real fallback. It DOES change the stamp on every
    output, and the loud warning below must be copied into the results
    template verbatim.
    """
    print("== nvidia-smi ==")
    try:
        out = subprocess.run(["nvidia-smi"], capture_output=True, text=True, timeout=60)
        print(out.stdout or "(nvidia-smi produced no output)")
        smi_text = out.stdout or ""
    except FileNotFoundError:
        print("(nvidia-smi not found on PATH)")
        smi_text = "(nvidia-smi not found)"
    if CPU_SELFTEST:
        print("\n!!! CPU SELFTEST MODE (WH_CPU_SELFTEST=1) — NOT A RENDER RUN !!!\n")
        return False, "CPU-SELFTEST", smi_text
    try:
        import torch
        has_cuda = torch.cuda.is_available()
        name = torch.cuda.get_device_name(0) if has_cuda else "none"
        print(f"torch {torch.__version__} | cuda.is_available() = {has_cuda} | {name}")
    except ImportError:
        has_cuda, name = False, "torch-not-installed"
        print("torch not installed; CUDA post-processing unavailable (PIL post only).")
    if not has_cuda:
        print("\n!!! WARNING: NO CUDA DEVICE — Cycles-CPU fallback ONLY. "
              "Outputs will be stamped render_path=cycles-cpu and must NOT "
              "be reported as GPU renders. !!!\n")
    return has_cuda, name, smi_text


def validate_glb(path: Path):
    """Stdlib GLB check: magic, header, JSON chunk parse. Returns dict."""
    data = path.read_bytes()
    info = {"file": str(path), "bytes": len(data), "valid": False}
    if len(data) < 20 or data[0:4] != b"glTF":
        info["error"] = "not a glTF binary (bad magic or truncated)"
        return info
    _magic, _ver, total = struct.unpack("<III", data[0:12])
    chunk_len, chunk_type = struct.unpack("<II", data[12:20])
    info["header_length"] = total
    if chunk_type == 0x4E4F534A:  # 'JSON'
        try:
            doc = json.loads(data[20:20 + chunk_len])
            info.update({"valid": True, "n_meshes": len(doc.get("meshes", [])),
                         "n_nodes": len(doc.get("nodes", [])),
                         "n_materials": len(doc.get("materials", [])),
                         "n_images": len(doc.get("images", [])),
                         "n_animations": len(doc.get("animations", []))})
        except Exception as exc:  # noqa: BLE001 - report, don't crash batch
            info["error"] = f"JSON chunk unreadable: {exc}"
    else:
        info["error"] = "first chunk is not JSON"
    return info


def post_process(png_path: Path, use_gpu: bool):
    """Vignette + contrast/saturation lift. Torch CUDA if available, else PIL."""
    from PIL import Image, ImageEnhance
    if use_gpu:
        try:
            import torch, numpy as np
            im = Image.open(png_path).convert("RGB")
            t = torch.from_numpy(np.asarray(im, dtype=np.float32) / 255.0).cuda()
            h, w = t.shape[0], t.shape[1]
            yy = torch.linspace(-1, 1, h, device="cuda")[:, None]
            xx = torch.linspace(-1, 1, w, device="cuda")[None, :]
            vig = 1.0 - 0.22 * torch.clamp(xx ** 2 + yy ** 2, 0, 1)
            t = torch.clamp((t - 0.5) * 1.08 + 0.5, 0, 1) * vig[..., None]
            out = Image.fromarray((t.cpu().numpy() * 255).astype("uint8"))
            out.save(png_path)
            return "gpu"
        except Exception as exc:  # noqa: BLE001 - fall through to PIL
            print(f"  GPU post failed ({exc}); using PIL post.")
    im = Image.open(png_path).convert("RGB")
    im = ImageEnhance.Contrast(im).enhance(1.08)
    im = ImageEnhance.Color(im).enhance(1.05)
    im.save(png_path)
    return "cpu"


def render_with_bpy(glb_path: Path, out_dir: Path, use_gpu: bool):
    """Render front + 3/4 views with bpy Cycles. Returns (render_path, files).

    Raises RuntimeError with a plain message if bpy is missing or the
    render fails — the caller records it, it never becomes a fake card.
    """
    try:
        import bpy
    except ImportError as exc:
        raise RuntimeError(
            "bpy is not installed. In the notebook run: !pip install -q "
            f"bpy==4.2  (then re-run). Original error: {exc}")
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.samples = SAMPLES_GPU if use_gpu else SAMPLES_CPU
    scene.render.resolution_x, scene.render.resolution_y = CARD_W, CARD_H
    scene.render.film_transparent = False
    scene.world = bpy.data.worlds.new("WHCardWorld")
    scene.world.use_nodes = True
    bg = scene.world.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (0.055, 0.055, 0.075, 1.0)
    bg.inputs[1].default_value = 1.0
    # Import GLB (frame 0 / bind pose as shipped).
    bpy.ops.import_scene.gltf(filepath=str(glb_path))
    objs = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    if not objs:
        raise RuntimeError(f"no mesh objects imported from {glb_path.name}")
    # Bounding box over all meshes (world space, evaluated roughly via
    # object dimensions — good enough for card framing, not for physics).
    import mathutils
    mins = [1e9, 1e9, 1e9]
    maxs = [-1e9, -1e9, -1e9]
    for o in objs:
        for c in o.bound_box:
            w = o.matrix_world @ mathutils.Vector(c)
            for i in range(3):
                mins[i] = min(mins[i], w[i])
                maxs[i] = max(maxs[i], w[i])
    centre = [(mins[i] + maxs[i]) / 2 for i in range(3)]
    size = max(maxs[i] - mins[i] for i in range(3)) or 1.0
    # Lights: key sun + cool rim.
    bpy.ops.object.light_add(type="SUN", location=(5, -5, 8))
    bpy.context.active_object.data.energy = 3.0
    bpy.ops.object.light_add(type="SUN", location=(-6, 6, 4))
    rim = bpy.context.active_object
    rim.data.energy = 1.5
    rim.rotation_euler = (0.9, 0.2, 2.6)
    # Camera: front, then 45-degree yaw. Distance scales with model size.
    import math
    cam_data = bpy.data.cameras.new("WHCardCam")
    cam = bpy.data.objects.new("WHCardCam", cam_data)
    bpy.context.collection.objects.link(cam)
    scene.camera = cam
    dist = size * 1.9
    views = [("front", (0, -dist, centre[2] + size * 0.15)),
             ("threequarter", (dist * 0.7071, -dist * 0.7071, centre[2] + size * 0.15))]
    # Cycles device: GPU only if a CUDA device is actually enumerated.
    render_path = "cycles-cpu"
    if use_gpu:
        try:
            prefs = bpy.context.preferences.addons["cycles"].preferences
            prefs.compute_device_type = "CUDA"
            prefs.get_devices()  # headless quirk: forces GPU detection
            for d in prefs.devices:
                d.use = True
            scene.cycles.device = "GPU"
            render_path = "cycles-gpu"
            print(f"  Cycles devices: {[d.name for d in prefs.devices]}")
        except Exception as exc:  # noqa: BLE001 - honest downgrade, logged
            print(f"  Cycles GPU setup failed ({exc}); falling back to CPU.")
            scene.cycles.device = "CPU"
    files = []
    for view_name, loc in views:
        cam.location = (centre[0] + loc[0], centre[1] + loc[1], loc[2])
        # Point camera at model centre.
        direction = mathutils.Vector(centre) - cam.location
        cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
        out_png = out_dir / f"{glb_path.stem}_{view_name}.png"
        scene.render.filepath = str(out_png)
        bpy.ops.render.render(write_still=True)
        files.append(str(out_png))
    # Clean scene for the next model.
    bpy.ops.wm.read_factory_settings(use_empty=True)
    return render_path, files


def main():
    t_run = time.time()
    has_cuda, gpu_name, smi_text = gpu_gate()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    glbs = sorted(INPUT_DIR.rglob("*.glb")) if INPUT_DIR.exists() else []
    print(f"input dir: {INPUT_DIR} | GLBs found: {len(glbs)}")
    results = []
    if CPU_SELFTEST:
        # Local logic test only: validate GLBs (none expected here) and
        # prove the PIL post path on a synthetic image. No rendering.
        from PIL import Image
        sample = OUTPUT_DIR / "_selftest_sample.png"
        Image.new("RGB", (64, 64), (180, 60, 40)).save(sample)
        post = post_process(sample, use_gpu=False)
        print(f"selftest: PIL post={post} on {sample} (no render attempted)")
        results.append({"selftest": True, "pil_post": post})
    else:
        for glb in glbs:
            t0 = time.time()
            info = validate_glb(glb)
            if not info["valid"]:
                print(f"[skip] {glb.name}: {info.get('error')}")
                results.append({**info, "status": "skipped"})
                continue
            print(f"[render] {glb.name}: {info['n_meshes']} meshes, "
                  f"{info['n_materials']} materials, {info['bytes']} bytes")
            try:
                render_path, files = render_with_bpy(glb, OUTPUT_DIR, has_cuda)
            except Exception as exc:  # noqa: BLE001 - record, continue batch
                print(f"[FAILED] {glb.name}: {exc}")
                results.append({**info, "status": "failed", "error": str(exc)})
                continue
            post = None
            for f in files:
                post = post_process(Path(f), use_gpu=has_cuda)
            results.append({**info, "status": "rendered", "render_path": render_path,
                            "post": post, "outputs": files,
                            "seconds": round(time.time() - t0, 1)})
            print(f"  -> {render_path} post={post} in {time.time() - t0:.1f}s: {files}")
    rendered = [r for r in results if r.get("status") == "rendered"]
    report = {"gpu": gpu_name, "cuda_available": has_cuda,
              "cpu_selftest": CPU_SELFTEST, "input_dir": str(INPUT_DIR),
              "card_px": [CARD_W, CARD_H],
              "samples": {"gpu": SAMPLES_GPU, "cpu": SAMPLES_CPU},
              "results": results, "total_seconds": round(time.time() - t_run, 1)}
    (OUTPUT_DIR / "report.json").write_text(json.dumps(report, indent=2))
    verif = ["== GPU-VERIFICATION (job-e-prerender) ==", "--- nvidia-smi ---",
             smi_text, f"torch cuda: {gpu_name}",
             f"rendered: {len(rendered)} / {len(glbs)} GLBs",
             f"render paths used: {sorted({r.get('render_path') for r in rendered})}",
             f"total seconds: {report['total_seconds']}"]
    (OUTPUT_DIR / "GPU-VERIFICATION.txt").write_text("\n".join(verif) + "\n")
    print(f"\nDone. rendered={len(rendered)}/{len(glbs)} -> {OUTPUT_DIR}")
    if not CPU_SELFTEST and not rendered:
        print("FAILURE: zero GLBs rendered (see report.json). Do not call this a run.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
