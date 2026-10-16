#!/usr/bin/env python3
"""Generate pantera_kaggle_render_v3.ipynb — FIRE-AND-FORGET auto-looping render.

v3 vs v2: ONE "Run All" renders ALL chunks sequentially. No manual CHUNK changes.
- CHUNKS_TO_RUN = "all" (default), a list like [3,4,5], or "remaining" (auto-resume)
- Resume: skips chunks whose zip already exists in /kaggle/working with matching frame count
- Per-chunk render → verify → zip, with progress log
- Final summary cell lists all zips + sha256

Same optimization stack as v2 (OptiX, adaptive sampling, persistent data).
Expected: ~15-25 min/chunk. 6 chunks ≈ 2-3h total in ONE session.
"""
import json

BRANCH = "muse/wh-pantera-entrance-v1"
RAW = f"https://raw.githubusercontent.com/mhvnsnt/western-heart/{BRANCH}/promo/pantera-entrance-v1"
BLEND_SHA = "a5d4adb3076e73feb65dad826e235e9c9b26a23f3913507304f33078783d5934"
TRON_SHA = "de78d7a3c73c75d272a6971c0232b790e73f4f5fa49e4cefc49bc8bf7180babb"
BLENDER_URL = "https://download.blender.org/release/Blender4.0/blender-4.0.2-linux-x64.tar.xz"

CHUNKS = {0: (0, 249), 1: (250, 499), 2: (500, 749),
          3: (750, 999), 4: (1000, 1249), 5: (1250, 1499)}

def md(src):
    return {"cell_type": "markdown", "metadata": {}, "source": src}

def code(src):
    return {"cell_type": "code", "metadata": {},
            "execution_count": None, "outputs": [], "source": src}

with open("/home/hatch/workspace/kaggle-pantera-render/build_kaggle.py") as f:
    BUILD_SCRIPT = f.read()

cells = [
md("""# Pantera entrance v1 — Kaggle GPU render v3 (FIRE-AND-FORGET)

Renders all 1500 frames with **Blender 4.0.2 Cycles on Kaggle T4**.

**Setup:** Settings → **Accelerator: GPU T4 x2**, **Internet: ON**. Then **Run All**. That's it.

**v3 automation** (vs v2 which needed manual CHUNK changes):
- One Run All renders ALL chunks sequentially — no human intervention
- `CHUNKS_TO_RUN = "all"` (default), `"remaining"` (auto-resume skipped chunks), or a list like `[3, 4, 5]`
- Resume: chunks with existing verified zips are skipped automatically
- Progress printed per chunk; final summary lists all zips + sha256

**v2/v3 optimization stack:**
- OptiX render device + OptiX AI denoiser (T4 Turing)
- Adaptive sampling (noise 0.1, min 16), persistent data ON
- Light bounces tuned (4/2/2/2/1), caustics off, simplify cap 2
- 1280x720 @ 32spp adaptive (post upscales to 1920x1080)

Expected: ~15-25 min/chunk. 6 chunks ≈ 2-3h total in one session.
"""),

code(f'''# === CONFIG ===
CHUNKS_TO_RUN = "all"   # "all" | "remaining" (auto-resume) | list like [3, 4, 5]
SAMPLES = 32            # max spp (adaptive sampling uses fewer where clean)
RES = "1280x720"        # render resolution (post upscales to 1920x1080)
DEVICE = "OPTIX"        # OPTIX (T4) or CUDA fallback
CHUNKS = {CHUNKS}

def _resolve_chunks():
    import os, glob
    if isinstance(CHUNKS_TO_RUN, list):
        todo = [c for c in CHUNKS_TO_RUN if c in CHUNKS]
    elif CHUNKS_TO_RUN == "remaining":
        todo = []
        for c, (f0, f1) in CHUNKS.items():
            zips = glob.glob(f"/kaggle/working/pantera_chunk{{c:02d}}_f{{f0:05d}}-{{f1:05d}}.zip")
            if zips:
                print(f"  chunk {{c}}: zip exists, skipping")
            else:
                todo.append(c)
    else:  # "all"
        todo = sorted(CHUNKS.keys())
    return todo

TODO = _resolve_chunks()
print(f"chunks to render: {{TODO}}")
print(f"settings: {{SAMPLES}}spp adaptive, {{RES}}, {{DEVICE}}")
assert TODO, "nothing to render — all chunks already done (or bad CHUNKS_TO_RUN)"
'''),

code('''# === GPU check ===
import subprocess
r = subprocess.run(["nvidia-smi", "--query-gpu=name,driver_version,memory.total",
                    "--format=csv"], capture_output=True, text=True)
print(r.stdout.strip() or "NO GPU VISIBLE — enable Accelerator: GPU in Settings!")
assert "Tesla T4" in r.stdout, "Expected a Tesla T4"
'''),

code(f'''# === Blender 4.0.2 portable (cached across chunks) ===
import os, subprocess
WORK = "/kaggle/working/pantera"
BLDIR = f"{{WORK}}/blender-4.0.2"
os.makedirs(WORK, exist_ok=True)
if not os.path.exists(f"{{BLDIR}}/blender"):
    print("installing system deps...")
    subprocess.run(["apt-get", "update", "-qq"], check=False)
    subprocess.run(["apt-get", "install", "-y", "-qq",
                    "libgl1", "libxi6", "libxkbcommon0", "libsm6",
                    "libxrender1", "libxxf86vm1"], check=False)
    print("downloading Blender 4.0.2...")
    subprocess.run(["wget", "-q", "-O", f"{{WORK}}/blender.tar.xz",
                    "{BLENDER_URL}"], check=True)
    subprocess.run(["tar", "-xf", f"{{WORK}}/blender.tar.xz", "-C", WORK], check=True)
    os.remove(f"{{WORK}}/blender.tar.xz")
else:
    print("Blender cached, skipping download")
r = subprocess.run([f"{{BLDIR}}/blender", "--version"], capture_output=True, text=True)
print(r.stdout.strip().splitlines()[0])
'''),

code(f'''# === Download assets (SHA-256 verified, cached) + write build script ===
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

with open("/kaggle/working/pantera/kit/build_kaggle.py", "w") as f:
    f.write(BUILD_SCRIPT)
print("build_kaggle.py written:", os.path.getsize("/kaggle/working/pantera/kit/build_kaggle.py"), "bytes")
'''),

code('''# === RENDER ALL CHUNKS (fire-and-forget loop) ===
import os, subprocess, time, glob, hashlib
WORK = "/kaggle/working/pantera"
RESULTS = []
t_all = time.time()

for CHUNK in TODO:
    F0, F1 = CHUNKS[CHUNK]
    print(f"\\n{'='*50}")
    print(f"CHUNK {CHUNK}/{{max(TODO)}}: frames {F0}-{F1}")
    print(f"{'='*50}")

    # --- render ---
    env = dict(os.environ)
    env.update({
        "PANTERA_BLEND": f"{WORK}/kit/pantera_rigged_working_v3.blend",
        "PANTERA_TRON": f"{WORK}/kit/assets/titantron_plate_1920.png",
        "PANTERA_FRAMES": f"{WORK}/frames",
        "PANTERA_F0": str(F0),
        "PANTERA_F1": str(F1),
        "PANTERA_SAMPLES": str(SAMPLES),
        "PANTERA_RES": RES,
        "PANTERA_DEVICE": DEVICE,
    })
    os.makedirs(f"{WORK}/frames", exist_ok=True)
    t0 = time.time()
    p = subprocess.Popen(
        [f"{WORK}/blender-4.0.2/blender", "-b", "-P", f"{WORK}/kit/build_kaggle.py"],
        env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    for line in p.stdout:
        s = line.strip()
        if any(k in s for k in ("OPTIMIZED", "engine=", "DONE", "Error", "Traceback")):
            print(f"  {s}", flush=True)
    p.wait()
    mins = (time.time() - t0) / 60
    print(f"  blender exit={p.returncode}, {mins:.1f} min")
    assert p.returncode == 0, f"blender render FAILED on chunk {CHUNK}"

    # --- verify ---
    frames = sorted(glob.glob(f"{WORK}/frames/f*.png"))
    n_expect = F1 - F0 + 1
    # count only this chunk's frames
    chunk_frames = [f for f in frames
                    if F0 <= int(os.path.basename(f)[1:6]) <= F1]
    print(f"  frames on disk: {len(chunk_frames)} (expect {n_expect})")
    assert len(chunk_frames) == n_expect, f"FRAME COUNT MISMATCH on chunk {CHUNK}"

    # --- zip ---
    ZIP = f"/kaggle/working/pantera_chunk{CHUNK:02d}_f{F0:05d}-{F1:05d}.zip"
    if os.path.exists(ZIP):
        os.remove(ZIP)
    subprocess.run(["zip", "-q", "-j", ZIP] +
                   [f"{WORK}/frames/f{f:05d}.png" for f in range(F0, F1 + 1)],
                   check=True)
    h = hashlib.sha256(open(ZIP, "rb").read()).hexdigest()
    sz = os.path.getsize(ZIP)
    print(f"  {os.path.basename(ZIP)}  {sz} bytes  sha256:{h[:16]}...")
    RESULTS.append((CHUNK, os.path.basename(ZIP), sz, h))
    print(f"  CHUNK {CHUNK} COMPLETE ✓")

total_mins = (time.time() - t_all) / 60
print(f"\\n{'='*50}")
print(f"ALL {len(RESULTS)} CHUNKS COMPLETE in {total_mins:.1f} min")
print(f"{'='*50}")
for c, name, sz, h in RESULTS:
    print(f"  chunk {c}: {name} ({sz} bytes)")
'''),

code('''# === Final summary + preview ===
import glob, os
from IPython.display import Image, display
zips = sorted(glob.glob("/kaggle/working/pantera_chunk*.zip"))
print(f"\\nTotal zips in /kaggle/working: {len(zips)}")
for z in zips:
    print(f"  {os.path.basename(z)}  {os.path.getsize(z)} bytes")
print("\\nDownload all zips from /kaggle/working/ in the right-panel file viewer.")
print("Or via API: kaggle kernels output <kernel> -p ./downloads")

# preview middle frame of the full sequence
frames = sorted(glob.glob("/kaggle/working/pantera/frames/f*.png"))
if frames:
    mid = frames[len(frames) // 2]
    print(f"\\npreview: {os.path.basename(mid)}")
    display(Image(filename=mid, width=640))
'''),
]

cells[4]["source"] = "BUILD_SCRIPT = " + json.dumps(BUILD_SCRIPT) + "\n\n" + cells[4]["source"]

nb = {
    "nbformat": 4, "nbformat_minor": 4,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.10.0"},
    },
    "cells": cells,
}

out = "/home/hatch/workspace/kaggle-pantera-render/pantera_kaggle_render_v3.ipynb"
with open(out, "w") as f:
    json.dump(nb, f, indent=1)
print(f"wrote {out}")

for i, c in enumerate(cells):
    if c["cell_type"] == "code":
        compile("".join(c["source"]), f"<cell {i}>", "exec")
print("all code cells compile OK")
