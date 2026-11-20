# JOB C — Real-ESRGAN texture upscaling (batch) — RUN GUIDE

**Status: NOT RUN (by this agent). Skeleton scripts exist, outputs do not.**

## Scripts — do NOT duplicate blindly (there are two, and they differ)

- `studio-pipeline/kaggle-jobs/02-realesrgan-batch.py` — 19 lines, a
  **comment-only notebook cell set** (setup cells + one batch command).
  It is READY TO RUN but contains no Python logic of its own: the real
  work is the upstream `inference_realesrgan.py` it calls.
- `audio-middleware-research/texture-upscale.sh` — 26 lines, a batch
  shell sketch: photo dir + anime dir, separate models per dir, WebP
  conversion step commented out at the end, OIDN denoise step commented
  out (for Cycles lightmaps only, NOT for photos/ESRGAN outputs).
- **Use the 02 script's cell set as the run sheet and the .sh's
  photo/anime split as the batch rule.** Do not run both as separate
  jobs on the same inputs — that would upscale everything twice.
  Pick one entry point per batch and record which one in the results.

## Tool + models (upstream, open source)

- Tool: xinntao/Real-ESRGAN (BSD-3-Clause). Needs PyTorch + CUDA;
  a Kaggle T4 fits (tiling keeps VRAM bounded).
- Models (weights are small — ~64 MB x4plus, ~18 MB anime_6B — fetch
  them on the notebook, never on this VM):
  - `RealESRGAN_x4plus` — photos / AI images / screenshots / realistic
    surfaces.
  - `RealESRGAN_x4plus_anime_6B` — anime / line-art / flat-shaded
    textures (keeps clean edges).
- **Model-swap rule (from both scripts, do not break it):** NEVER run
  the photo model on cel art (it invents photo grain); NEVER run the
  anime model on photos (it flattens detail). Sort inputs into
  `photo/` and `anime/` dirs BEFORE running.

## Inputs (exact)

- 02 script: inputs in `/kaggle/input/textures/`, outputs in
  `/kaggle/working/upscaled/` (single dir, single model per run — run
  twice, once per model, if the batch mixes photo + anime).
- .sh version: inputs `textures/photo/` + `textures/anime/`, outputs
  `textures_out/photo/` + `textures_out/anime/` (same filenames, PNG).
- **Batch rule (from the 02 script):** upscale ONLY textures below the
  target resolution. Never upscale an already-clean 2K texture —
  it wastes GPU and risks over-smoothing. `--outscale 4` on a 1K
  texture gives 4K; the .sh notes to use `--outscale 2` if the texture
  is already 1K+ (4× of 2K = 8K is wasteful for a web game).
- First batch suggestion (small, high value): the five 1K CC0 stage
  textures pulled in the free-assets lane (`free-pulls/gpu-assets/assets/`,
  Diffuse maps only for v1) at `--outscale 2` → 2K stage textures.
  Do not upscale the Rough maps in v1 unless a stage actually needs them.

## Run steps (browser lane)

1. Kaggle notebook, Accelerator → GPU (T4 x2). Run `!nvidia-smi` in a
   cell FIRST and save the output — the 02 skeleton has NO GPU gate
   of its own (see gaps), so the proof is manual for this job.
2. Cell set (02 script, verbatim intent):
   - `git clone https://github.com/xinntao/Real-ESRGAN.git`
   - `pip install -q basicsr facexlib gfpgan` + Real-ESRGAN requirements
   - `python Real-ESRGAN/setup.py develop`
   - Fetch weights into `Real-ESRGAN/weights/` (x4plus v0.1.0,
     x4plus_anime_6B v0.2.2.4).
3. Batch (photo example — swap `-n` for anime):
   `python Real-ESRGAN/inference_realesrgan.py -n RealESRGAN_x4plus -i /kaggle/input/textures -o /kaggle/working/upscaled --suffix 4x --tile 512 --tile_pad 16 --fp32`
   (.sh variant uses `--tile 400 --tile_pad 10 --outscale 4 --ext png`
   and no suffix. Either tiling is fine; record which was used. If VRAM
   OOMs, lower `--tile` before anything else.)
4. **Eye-check one output per batch** (mandatory, from the 02 script):
   open an upscaled texture and confirm detail is real, not invented
   grain / halo / over-smoothing. A batch that was never looked at is
   not a finished batch.
5. Download ONLY `/kaggle/working/upscaled/` (or `textures_out/`)
   before the session ends. Do not download the weights or the repo.

## Gaps found — read before running (honest, not blocking)

1. **No GPU gate in either script.** Neither the 02 cell set nor the
   .sh prints nvidia-smi, checks torch.cuda, or fails without a GPU.
   The browser lane MUST run `!nvidia-smi` + a torch CUDA check
   manually in the first cell and paste both into the results file.
   Without that, this job's "GPU" claim is unverified even if it runs.
2. **No timing / report / manifest.** Neither script writes a report
   file. The browser lane must record time + before/after sizes +
   file list by hand in `results-template.md` (the template has a
   section for this job's manual proof).
3. **No input-size guard.** Neither script skips already-large textures
   automatically — the "upscale only below target" rule is a human
   sorting step. Sort first, or the GPU time is wasted.
4. **WebP conversion is commented out in the .sh.** Masters stay PNG;
   the game ships WebP. After download, convert (`cwebp -q 90`) as a
   separate landing step and record both sizes.
5. **OIDN step is commented out for a reason.** Only for Cycles-rendered
   lightmaps/renders with noise + Blender AOVs. Skip it for photos
   and ESRGAN outputs — running it on textures would be a mistake.
6. **fp32 vs speed:** the 02 command uses `--fp32` (safer quality,
   slower). If a batch is too slow, dropping fp32 is a legitimate
   experiment — record it, and eye-check the outputs again.

## Landing (after download — separate step)

- Convert masters to WebP for the web build; keep PNG masters.
- Replace/upgrade stage textures only where the eye-check passed;
  keep the 1K originals until the 2K versions are confirmed in-game.

## Metrics to record (see results-template.md)

Per texture: input px + bytes, model used, outscale, tile, output px +
bytes, run time for the batch, GPU name (manual nvidia-smi), eye-check
result (pass/fail + which file was checked), any OOM + tile change.
