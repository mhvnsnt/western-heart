#!/usr/bin/env python3
"""Generate pantera_kaggle_render_v4.ipynb — FIRE-AND-FORGET, no chunks.

v4 vs v3:
- Blender 4.5.12 LTS (not 4.0.2) — enables GPU OIDN via denoising_use_gpu
- 16spp + adaptive threshold 0.05 + GPU OIDN (v4 optimization stack)
- NO CHUNKS: renders FRAME_START to FRAME_END in ONE Blender invocation
- FRAME_START/FRAME_END configurable via pre_cells (for parallel splits)
- Resume: skips existing frames, skips if output zip is complete
- Expected: ~60 min for all 1500 frames on one T4 (vs ~2h on v3)

Usage:
  python3 gen_notebook_v4.py
  # → pantera_kaggle_render_v4.ipynb

For parallel: use render_parallel.py to split across N kernels.
"""
import json

BRANCH = "muse/wh-pantera-entrance-v1"
RAW = f"https://raw.githubusercontent.com/mhvnsnt/western-heart/{BRANCH}/promo/pantera-entrance-v1"
BLEND_SHA = "a5d4adb3076e73feb65dad826e235e9c9b26a23f3913507304f33078783d5934"
TRON_SHA = "de78d7a3c73c75d272a6971c0232b790e73f4f5fa49e4cefc49bc8bf7180babb"

# Blender 4.5.12 LTS — verified SHA-256 from official build (2026-07-21)
BLENDER_VER = "4.5.12"
BLENDER_URL = f"https://download.blender.org/release/Blender4.5/blender-{BLENDER_VER}-linux-x64.tar.xz"
BLENDER_SHA = "95e3a2dfedba3bd32ca54fc355eac6b15a11986954ccb02815a07535d0120a25"

TOTAL_FRAMES = 1500

def md(src):
    return {"cell_type": "markdown", "metadata": {}, "source": src}

def code(src):
    return {"cell_type": "code", "metadata": {},
            "execution_count": None, "outputs": [], "source": src}

with open("/home/hatch/workspace/kaggle-pantera-render/build_kaggle_v4.py") as f:
    BUILD_SCRIPT_V4 = f.read()

cells = [
md("""# Pantera entrance v1 — Kaggle GPU render v4 (FIRE-AND-FORGET, NO CHUNKS)

Renders all 1500 frames with **Blender 4.5.12 LTS Cycles on Kaggle T4**.

**Setup:** Settings → **Accelerator: GPU T4 x2**, **Internet: ON**. Then **Run All**. That's it.

**v4 improvements over v3:**
- Blender 4.5.12 LTS (not 4.0.2) — enables GPU-accelerated OIDN denoising
- 16spp + adaptive threshold 0.05 + GPU OIDN — ~2x faster, BETTER quality (no OptiX flicker)
- No chunks — one Blender invocation renders FRAME_START to FRAME_END
- Frame-skip resume — re-running skips already-rendered frames
- Expected: ~60 min for all 1500 frames (vs ~2h on v3)

**For parallel renders:** `FRAME_START`/`FRAME_END` can be overridden via
pre-cells injection (see `render_parallel.py`). Each split renders its own
range; the orchestrator merges the zips.
"""),

code(f'''# === CONFIG ===
# FRAME_START/FRAME_END can be pre-set via pre_cells (parallel splits).
# Only apply defaults if not already defined.
if 'FRAME_START' not in dir():
    FRAME_START = 0        # first frame
if 'FRAME_END' not in dir():
    FRAME_END = 1499       # last frame
SAMPLES = 16           # v4: 16spp adaptive (was 32spp in v3)
RES = "1280x720"       # render resolution
DEVICE = "OPTIX"       # OPTIX (T4) with CUDA fallback
BLENDER_VER = "{BLENDER_VER}"

N_FRAMES = FRAME_END - FRAME_START + 1
print(f"v4 render: frames {{FRAME_START}}-{{FRAME_END}} ({{N_FRAMES}} frames)")
print(f"settings: {{SAMPLES}}spp adaptive(0.05), GPU-OIDN, {{RES}}, {{DEVICE}}")
print(f"blender: {{BLENDER_VER}} LTS")
assert 0 <= FRAME_START <= FRAME_END < {TOTAL_FRAMES}, "frame range out of bounds"
'''),

code('''# === GPU check ===
import subprocess
r = subprocess.run(["nvidia-smi", "--query-gpu=name,driver_version,memory.total",
                    "--format=csv"], capture_output=True, text=True)
print(r.stdout.strip() or "NO GPU VISIBLE — enable Accelerator: GPU in Settings!")
assert "Tesla T4" in r.stdout, "Expected a Tesla T4"
'''),

code(f'''# === Blender 4.5.12 LTS portable (SHA-256 verified, cached) ===
import os, subprocess, hashlib
WORK = "/kaggle/working/pantera"
BLDIR = f"{{WORK}}/blender-{BLENDER_VER}"
os.makedirs(WORK, exist_ok=True)
if not os.path.exists(f"{{BLDIR}}/blender"):
    print("installing system deps...")
    subprocess.run(["apt-get", "update", "-qq"], check=False)
    subprocess.run(["apt-get", "install", "-y", "-qq",
                    "libgl1", "libxi6", "libxkbcommon0", "libsm6",
                    "libxrender1", "libxxf86vm1"], check=False)
    print("downloading Blender {BLENDER_VER} LTS...")
    subprocess.run(["wget", "-q", "-O", f"{{WORK}}/blender.tar.xz",
                    "{BLENDER_URL}"], check=True)
    print("verifying SHA-256...")
    h = hashlib.sha256(open(f"{{WORK}}/blender.tar.xz", "rb").read()).hexdigest()
    assert h == "{BLENDER_SHA}", f"BLENDER SHA MISMATCH: {{h}}"
    print("  SHA OK")
    subprocess.run(["tar", "-xf", f"{{WORK}}/blender.tar.xz", "-C", WORK], check=True)
    os.remove(f"{{WORK}}/blender.tar.xz")
else:
    print("Blender cached, skipping download")
r = subprocess.run([f"{{BLDIR}}/blender", "--version"], capture_output=True, text=True)
print(r.stdout.strip().splitlines()[0])
assert "{BLENDER_VER}" in r.stdout, "wrong Blender version!"
'''),

code(f'''# === Download assets (SHA-256 verified, cached) + write v4 build script ===
import hashlib, os, urllib.request
RAW = "{RAW}"
os.makedirs("/kaggle/working/pantera/kit/assets", exist_ok=True)
ASSETS = {{
    "kit/pantera_rigged_working_v3.blend":
        (f"{{RAW}}/kaggle/pantera_rigged_working_v3.blend", "{BLEND_SHA}"),
    "kit/assets/titantron_plate_1920.png":
        (f"{{RAW}}/assets/titantron_plate_1920.png", "{TRON_SHA}"),
}}
for rel, (url, sha) in ASSETS.items():
    dest = f"/kaggle/working/pantera/{{rel}}"
    if os.path.exists(dest):
        h = hashlib.sha256(open(dest, "rb").read()).hexdigest()
        if h == sha:
            print(f"cached OK: {{rel}}")
            continue
    print(f"downloading {{rel}}...")
    urllib.request.urlretrieve(url, dest)
    h = hashlib.sha256(open(dest, "rb").read()).hexdigest()
    assert h == sha, f"SHA MISMATCH for {{rel}}: {{h}} != {{sha}}"
    print(f"verified: {{rel}}")

with open("/kaggle/working/pantera/kit/build_kaggle_v4.py", "w") as f:
    f.write(BUILD_SCRIPT_V4)
print("build_kaggle_v4.py written:", os.path.getsize("/kaggle/working/pantera/kit/build_kaggle_v4.py"), "bytes")
'''),

code('''# === RENDER (fire-and-forget, single Blender invocation, no chunks) ===
import os, subprocess, time, glob, hashlib
WORK = "/kaggle/working/pantera"
ZIP = f"/kaggle/working/pantera_v4_f{FRAME_START:05d}-{FRAME_END:05d}.zip"

# Resume check: if zip exists with the right frame count, skip entirely
if os.path.exists(ZIP):
    import zipfile
    with zipfile.ZipFile(ZIP) as zf:
        n_in_zip = len([n for n in zf.namelist() if n.endswith(".png")])
    if n_in_zip == N_FRAMES:
        print(f"  {os.path.basename(ZIP)} already complete ({n_in_zip} frames), skipping render")
        DONE = True
    else:
        print(f"  existing zip incomplete ({n_in_zip}/{N_FRAMES}), re-rendering")
        DONE = False
else:
    DONE = False

if not DONE:
    env = dict(os.environ)
    env.update({
        "PANTERA_BLEND": f"{WORK}/kit/pantera_rigged_working_v3.blend",
        "PANTERA_TRON": f"{WORK}/kit/assets/titantron_plate_1920.png",
        "PANTERA_FRAMES": f"{WORK}/frames",
        "PANTERA_F0": str(FRAME_START),
        "PANTERA_F1": str(FRAME_END),
        "PANTERA_SAMPLES": str(SAMPLES),
        "PANTERA_RES": RES,
        "PANTERA_DEVICE": DEVICE,
    })
    os.makedirs(f"{WORK}/frames", exist_ok=True)
    print(f"\\n{'='*50}")
    print(f"V4 RENDER: frames {FRAME_START}-{FRAME_END} ({N_FRAMES} frames)")
    print(f"{'='*50}")
    t0 = time.time()
    p = subprocess.Popen(
        [f"{WORK}/blender-{BLENDER_VER}/blender", "-b", "-P", f"{WORK}/kit/build_kaggle_v4.py"],
        env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    for line in p.stdout:
        s = line.strip()
        if any(k in s for k in ("V4 OPTIMIZED", "GPU OIDN", "frame ", "DONE v4", "Error", "Traceback")):
            print(f"  {s}", flush=True)
    p.wait()
    mins = (time.time() - t0) / 60
    print(f"  blender exit={p.returncode}, {mins:.1f} min")
    assert p.returncode == 0, f"blender render FAILED on frames {FRAME_START}-{FRAME_END}"

    # --- verify ---
    frames = sorted(glob.glob(f"{WORK}/frames/f*.png"))
    range_frames = [f for f in frames
                    if FRAME_START <= int(os.path.basename(f)[1:6]) <= FRAME_END]
    print(f"  frames on disk: {len(range_frames)} (expect {N_FRAMES})")
    assert len(range_frames) == N_FRAMES, f"FRAME COUNT MISMATCH"

    # --- zip ---
    if os.path.exists(ZIP):
        os.remove(ZIP)
    subprocess.run(["zip", "-q", "-j", ZIP] +
                   [f"{WORK}/frames/f{f:05d}.png" for f in range(FRAME_START, FRAME_END + 1)],
                   check=True)
    h = hashlib.sha256(open(ZIP, "rb").read()).hexdigest()
    sz = os.path.getsize(ZIP)
    print(f"  {os.path.basename(ZIP)}  {sz} bytes  sha256:{h[:16]}...")
    print(f"\\nV4 RENDER COMPLETE ✓  ({mins:.1f} min for {N_FRAMES} frames)")
'''),

code('''# === Final summary + preview ===
import glob, os
from IPython.display import Image, display
zips = sorted(glob.glob("/kaggle/working/pantera_v4_*.zip"))
print(f"\\nTotal v4 zips in /kaggle/working: {len(zips)}")
for z in zips:
    print(f"  {os.path.basename(z)}  {os.path.getsize(z)} bytes")
print("\\nDownload zips from /kaggle/working/ in the right-panel file viewer.")
print("Or via API: kaggle kernels output <kernel> -p ./downloads")

frames = sorted(glob.glob("/kaggle/working/pantera/frames/f*.png"))
if frames:
    mid = frames[len(frames) // 2]
    print(f"\\npreview: {os.path.basename(mid)}")
    display(Image(filename=mid, width=640))
'''),
]

# Embed the v4 build script
cells[4]["source"] = "BUILD_SCRIPT_V4 = " + json.dumps(BUILD_SCRIPT_V4) + "\n\n" + cells[4]["source"]

nb = {
    "nbformat": 4, "nbformat_minor": 4,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.10.0"},
    },
    "cells": cells,
}

out = "/home/hatch/workspace/kaggle-pantera-render/pantera_kaggle_render_v4.ipynb"
with open(out, "w") as f:
    json.dump(nb, f, indent=1)
print(f"wrote {out}")

for i, c in enumerate(cells):
    if c["cell_type"] == "code":
        compile("".join(c["source"]), f"<cell {i}>", "exec")
print("all code cells compile OK")
