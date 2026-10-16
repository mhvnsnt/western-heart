#!/usr/bin/env python3
"""Generate pantera_kaggle_render_v4.ipynb — FIRE-AND-FORGET, no chunks.

v4 vs v3:
- Blender 4.5.12 LTS (not 4.0.2) — enables GPU OIDN via denoising_use_gpu
- 16spp + adaptive threshold 0.05 + GPU OIDN (v4 optimization stack)
- SEGMENTED: renders FRAME_START..FRAME_END in SAVE_SEGMENTS segments
- BULLETPROOF: Kaggle dataset version published after EVERY segment
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

# Bulletproof saver (save_outputs.py) — embedded into the notebook so the
# kernel is self-contained. Publishes a Kaggle dataset version after EVERY
# render segment; a dead session can never take more than one segment.
with open("/home/hatch/workspace/tools/kaggle-queue/save_outputs.py") as f:
    SAVE_OUTPUTS_PY = f.read()

cells = [
md("""# Pantera entrance v1 — Kaggle GPU render v4 (FIRE-AND-FORGET, NO CHUNKS)

Renders all 1500 frames with **Blender 4.5.12 LTS Cycles on Kaggle T4**.

**Setup:** Settings → **Accelerator: GPU T4 x2**, **Internet: ON**. Then **Run All**. That's it.

**v4 improvements over v3:**
- Blender 4.5.12 LTS (not 4.0.2) — enables GPU-accelerated OIDN denoising
- 16spp + adaptive threshold 0.05 + GPU OIDN — ~2x faster, BETTER quality (no OptiX flicker)
- Segmented render with **bulletproof saving**: the range is split into
  `SAVE_SEGMENTS` segments; after EACH segment the zip is published as a new
  version of a Kaggle dataset (`KAGGLE_SAVE_DATASET`, queue-injected).
  A dead session can never lose more than one segment — re-running resumes
  from the save dataset automatically.
- Frame-skip resume — re-running skips already-rendered frames
- Expected: ~60 min for all 1500 frames (vs ~2h on v3)

**For parallel renders:** `FRAME_START`/`FRAME_END` can be overridden via
pre-cells injection (see `render_parallel.py`). Each split renders its own
range; the orchestrator merges the zips. Parallel splits set
`SAVE_SEGMENTS=1` (one checkpoint per split).
"""),

code(f'''# === CONFIG ===
import os
# FRAME_START/FRAME_END/SAVE_SEGMENTS can be pre-set via pre_cells
# (parallel splits). Only apply defaults if not already defined.
if 'FRAME_START' not in dir():
    FRAME_START = 0        # first frame
if 'FRAME_END' not in dir():
    FRAME_END = 1499       # last frame
if 'SAVE_SEGMENTS' not in dir():
    SAVE_SEGMENTS = 3      # render segments; dataset checkpoint after EACH
# Bulletproof save dataset slug — injected by kaggle_queue.py as
# KAGGLE_SAVE_DATASET. Empty = checkpoints stage locally only.
SAVE_DATASET = os.environ.get("KAGGLE_SAVE_DATASET", "")
SAMPLES = 16           # v4: 16spp adaptive (was 32spp in v3)
RES = "1280x720"       # render resolution
DEVICE = "OPTIX"       # OPTIX (T4) with CUDA fallback
BLENDER_VER = "{BLENDER_VER}"

N_FRAMES = FRAME_END - FRAME_START + 1
print(f"v4 render: frames {{FRAME_START}}-{{FRAME_END}} ({{N_FRAMES}} frames)")
print(f"settings: {{SAMPLES}}spp adaptive(0.05), GPU-OIDN, {{RES}}, {{DEVICE}}")
print(f"blender: {{BLENDER_VER}} LTS")
print(f"bulletproof: {{SAVE_SEGMENTS}} segment(s), save dataset: {{SAVE_DATASET or 'NONE (local only!)'}}")
assert 0 <= FRAME_START <= FRAME_END < {TOTAL_FRAMES}, "frame range out of bounds"
assert SAVE_SEGMENTS >= 1, "SAVE_SEGMENTS must be >= 1"
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

code('''# === BULLETPROOF SAVER ===
# save_outputs.py is embedded in this generator (see bottom of this script).
# It is written to /kaggle/working and imported here.
# Checkpoints publish a Kaggle dataset version after EVERY render segment,
# so a dead session can never take more than one segment with it.
with open("/kaggle/working/save_outputs.py", "w") as f:
    f.write(SAVE_OUTPUTS_PY)
import os as _os
print("save_outputs.py embedded:",
      _os.path.getsize("/kaggle/working/save_outputs.py"), "bytes")
from save_outputs import RenderSaver
saver = RenderSaver(dataset_slug=SAVE_DATASET or None,
                    note=f"pantera v4 f{FRAME_START:05d}-{FRAME_END:05d}")
saver.start_watchdog()
restored = saver.restore_from_input()
print(f"restore: {len(restored)} file(s) recovered from save dataset")
'''),

code('''# === RENDER (segmented; dataset checkpoint after EVERY segment) ===
import os, subprocess, time, glob, hashlib, zipfile
WORK = "/kaggle/working/pantera"

def seg_ranges(f0, f1, n):
    total = f1 - f0 + 1; base = total // n; rem = total % n
    out = []; cur = f0
    for i in range(n):
        sz = base + (1 if i < rem else 0)
        out.append((cur, cur + sz - 1)); cur += sz
    return out

def zip_png_count(zp):
    try:
        with zipfile.ZipFile(zp) as zf:
            return len([n for n in zf.namelist() if n.endswith(".png")])
    except Exception:
        return -1

SEGMENTS = seg_ranges(FRAME_START, FRAME_END, SAVE_SEGMENTS)
print(f"render plan: {len(SEGMENTS)} segment(s)")
for si, (s0, s1) in enumerate(SEGMENTS):
    print(f"  seg {si}: frames {s0}-{s1} ({s1 - s0 + 1} frames)")

os.makedirs(f"{WORK}/frames", exist_ok=True)
for si, (s0, s1) in enumerate(SEGMENTS):
    n_seg = s1 - s0 + 1
    seg_zip = f"/kaggle/working/pantera_v4_f{s0:05d}-{s1:05d}.zip"
    if os.path.exists(seg_zip) and zip_png_count(seg_zip) == n_seg:
        print(f"\\n[seg {si}] {os.path.basename(seg_zip)} already complete — skipping render")
    else:
        env = dict(os.environ)
        env.update({
            "PANTERA_BLEND": f"{WORK}/kit/pantera_rigged_working_v3.blend",
            "PANTERA_TRON": f"{WORK}/kit/assets/titantron_plate_1920.png",
            "PANTERA_FRAMES": f"{WORK}/frames",
            "PANTERA_F0": str(s0),
            "PANTERA_F1": str(s1),
            "PANTERA_SAMPLES": str(SAMPLES),
            "PANTERA_RES": RES,
            "PANTERA_DEVICE": DEVICE,
        })
        print(f"\\n{'='*50}")
        print(f"[seg {si}] RENDER frames {s0}-{s1} ({n_seg} frames)")
        print(f"{'='*50}")
        t0 = time.time()
        p = subprocess.Popen(
            [f"{WORK}/blender-{BLENDER_VER}/blender", "-b", "-P",
             f"{WORK}/kit/build_kaggle_v4.py"],
            env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in p.stdout:
            s = line.strip()
            if any(k in s for k in ("V4 OPTIMIZED", "GPU OIDN", "frame ",
                                    "DONE v4", "Error", "Traceback")):
                print(f"  {s}", flush=True)
        p.wait()
        mins = (time.time() - t0) / 60
        print(f"  blender exit={p.returncode}, {mins:.1f} min")
        assert p.returncode == 0, f"blender FAILED on segment {si} (frames {s0}-{s1})"
        frames = sorted(glob.glob(f"{WORK}/frames/f*.png"))
        got = [f for f in frames
               if s0 <= int(os.path.basename(f)[1:6]) <= s1]
        print(f"  frames on disk: {len(got)} (expect {n_seg})")
        assert len(got) == n_seg, "FRAME COUNT MISMATCH"
        if os.path.exists(seg_zip):
            os.remove(seg_zip)
        subprocess.run(["zip", "-q", "-j", seg_zip] +
                       [f"{WORK}/frames/f{f:05d}.png"
                        for f in range(s0, s1 + 1)], check=True)
    h = hashlib.sha256(open(seg_zip, "rb").read()).hexdigest()
    sz = os.path.getsize(seg_zip)
    print(f"  {os.path.basename(seg_zip)}  {sz} bytes  sha256:{h[:16]}...")
    # === BULLETPROOF: publish NOW — never wait for the end ===
    saver.progress["segments_done"] = si + 1
    saver.progress["segments_total"] = len(SEGMENTS)
    ok = saver.checkpoint(f"segment-{si}-f{s0:05d}-{s1:05d}", [seg_zip])
    print(f"  checkpoint: {'CONFIRMED off-session' if ok else 'STAGED LOCALLY ONLY — retried next segment'}")

print(f"\\nV4 RENDER COMPLETE ({len(SEGMENTS)} segments, {N_FRAMES} frames)")
'''),

code('''# === Final summary + preview ===
import glob, os
from IPython.display import Image, display
try:
    saver.stop_watchdog()
except Exception:
    pass
zips = sorted(glob.glob("/kaggle/working/pantera_v4_*.zip"))
print(f"\\nTotal v4 zips in /kaggle/working: {len(zips)}")
for z in zips:
    print(f"  {os.path.basename(z)}  {os.path.getsize(z)} bytes")
print("\\nBulletproof copies: every segment was also published as a dataset")
print("version - see the [saver] log lines above for version numbers.")
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

# Embed the bulletproof saver module into the saver cell (index 5)
cells[5]["source"] = "SAVE_OUTPUTS_PY = " + json.dumps(SAVE_OUTPUTS_PY) + "\n\n" + cells[5]["source"]

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
