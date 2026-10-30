# Kaggle GPU runbook — what the parent must run (subagent cannot open the notebook)

Notebook: https://www.kaggle.com/code/marsfmmg/notebook2ff3176461/edit
Accelerator: GPU (2x Tesla T4), ~30 hrs/week budget. GPU time is precious:
batch roster jobs, don't run one file per session.

## Cell order
1. Upload to the notebook working dir: `kaggle_gpu_animation.py`,
   `kaggle_blender_cycles_gpu.py`, `kaggle_batch_gltf.py`, plus the
   .glb files to process (to `/kaggle/working/glb-in/` for script 3,
   or to `/kaggle/input/` for script 1 — edit GLB_PATH in script 1).
2. Script 1 (torch CUDA animation quantize):
   `!python kaggle_gpu_animation.py`
   Expect GPU_PROOF lines: device cuda, gpu_name Tesla T4, torch
   version, glb_bytes, rotation in/out bytes, output_sha256, COMPLETE.
   If device prints cpu, the accelerator is OFF — stop, turn GPU on,
   re-run. A cpu print is NOT a GPU verification.
3. Script 2 (Blender Cycles GPU render):
   `!wget -q https://download.blender.org/release/Blender4.5/blender-4.5.3-linux-x64.tar.xz`
   `!tar -xf blender-4.5.3-linux-x64.tar.xz`
   `!./blender-4.5.3-linux-x64/blender --background --python kaggle_blender_cycles_gpu.py`
   Expect GPU_PROOF lines: cuda_devices [Tesla T4...], output PNG bytes
   + sha256, COMPLETE. The PNG is the render proof — view it before
   trusting the hash.
4. Script 3 (batch GLB optimize):
   `!npm install -g @gltf-transform/cli gltfpack`
   `!python kaggle_batch_gltf.py`
   Expect one GPU_PROOF line per file with before/after bytes and sha256.

## What to paste back to the agent
The full GPU_PROOF blocks from all three scripts, plus any FAILED lines.
The agent records them in INDEX.md as the GPU verification record. Until
then, INDEX.md honestly marks these three scripts "GPU script delivered,
T4 run PENDING (parent step)" — not "GPU verified".

## Budget note
Script 1 + 2 are minutes each. Script 3 scales with roster size; run it
once per roster batch, not per file. The game itself runs on the
player's phone GPU (WebGPU/WebGL) — Kaggle T4s are for the OFFLINE
pipeline only and never ship in the game.
