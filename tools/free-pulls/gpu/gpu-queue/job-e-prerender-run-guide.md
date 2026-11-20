# JOB E — Asset pre-render (character cards + stage previews) — RUN GUIDE

**Status: NOT RUN. Script is NEW in this folder and has never rendered a
real model anywhere.**

## Script (new — the only job-E file)

- `gpu-queue/job-e-prerender.py` (in this folder). Read its header
  before running: it contains the full render-path honesty table.
- It is a Kaggle/Colab notebook script: paste the whole file into a
  cell, or upload + run `python job-e-prerender.py`.

## Inputs (exact)

- GLBs in `/kaggle/input/cards/` (override: `WH_INPUT` env var).
- Stage previews reuse the same renders in v1 (front + 3/4 frames,
  cropped square if needed) — there is no separate stage-render pass
  yet. Do not claim stage previews as a separate output until that
  pass exists.
- Optional: a stage HDRI/backdrop upload is NOT used by v1 — cards
  render on a flat dark studio backdrop. Do not upload an HDRI
  expecting it to appear in the cards.

## Run steps (browser lane)

1. Kaggle notebook, Accelerator → GPU (T4 x2). Colab GPU is the failover.
2. **Install Blender-as-a-module FIRST** (Kaggle does NOT ship Blender):
   `!pip install -q bpy==4.2` — same pin the UniRig lane uses.
   If pip bpy fails on the notebook's Python, STOP and record that
   failure. Do not substitute another renderer silently.
3. Upload GLBs to `/kaggle/input/cards/`.
4. Run the script. Outputs: `/kaggle/working/cards_out/`:
   `<stem>_front.png`, `<stem>_threequarter.png` per model,
   plus `report.json` + `GPU-VERIFICATION.txt`.
5. Download the whole output folder before the session ends.
6. Eye-check every card: model fully in frame, not clipped, not a
   black frame, materials visible. A black frame is a failed render,
   not a "dark card" — the script only counts renders that bpy
   completed, but a completed render can still be badly framed, so
   the eye-check is mandatory.

## Render path — what actually happened (record exactly this)

| Path recorded in report.json | What it means | How to report it |
|---|---|---|
| `cycles-gpu` | Cycles with a CUDA device enumerated via `get_devices()` | "GPU render" — legitimate |
| `cycles-cpu` | No CUDA device enumerated; Cycles CPU fallback | "CPU render (fallback)" — NEVER "GPU render" |
| (script fails, no PNGs) | bpy missing or render error | "NOT RUN / FAILED" with the error verbatim |

**Why Cycles, not EEVEE:** Cycles CUDA works headless with no display
server; EEVEE always needs OpenGL/a display and fails headless on a
notebook ("Unable to open a display" class errors). The script does
not attempt EEVEE at all — that is a deliberate, documented choice,
not a missing feature to paper over. Headless GPU detection quirk:
the script calls `get_devices()` before rendering because headless
Blender does not always auto-detect GPUs without it.

## Per-model defaults (v1, kept small on purpose)

- 2 views: front (0°) + 3/4 (45° yaw). Card size 768×1024 portrait
  (select-screen cards are portrait). Override: `WH_CARD_W` / `WH_CARD_H`.
- Framing from the imported meshes' bounding box (centre + max
  dimension) — no fixed camera distance, so tall/short models both fit.
- Lighting: key sun (warm) + rim sun (cool, behind) + flat dark world.
- Samples: 64 (GPU) / 32 (CPU). These are cards, not cinematics.
  Raise `WH_SAMPLES_GPU` only if time allows.
- Post: torch CUDA vignette + contrast/saturation lift when CUDA is
  available (`post=gpu`), else PIL equivalent (`post=cpu`). Record it.
- Pose: frame 0 / bind pose as shipped in the GLB. Posed/action cards
  are a later job — this script does not invent a pose.

## Gaps / limits (honest, read before running)

1. **Never rendered a real model.** The script's bpy path (import,
   framing, Cycles device setup, camera tracking) is written from the
   Blender Python API as documented, but it has NOT been executed
   against a real GLB in any environment — this VM has no bpy, no
   Blender binary, and no GPU. The first notebook run is a smoke test:
   run ONE small GLB first, eye-check both views, and only then run
   the batch. If the first render fails, fix the script (and record
   the fix) — do not run the whole roster into the same failure.
2. **Local testing done here covers only:** syntax (`py_compile`),
   GPU-gate behaviour (loud warning without CUDA; selftest banner),
   GLB validation (stdlib parse), and the PIL post path on a synthetic
   image. Torch post, bpy import, framing, and Cycles rendering are
   all UNTESTED and must be confirmed on the notebook.
3. **GLB validation is shallow.** It checks magic + JSON chunk +
   counts (meshes/nodes/materials/images/animations). It does not
   validate geometry, skins, or textures. A "valid" GLB can still
   render badly — hence the mandatory eye-check.
4. **No stage-preview pass, no posed cards, no turntable.** v1 scope
   is front + 3/4 stills only. Do not expand scope mid-batch.
5. **If bpy is missing, the script fails loudly** (no PNGs, exit 1
   when zero GLBs render). That is correct behaviour — a missing
   renderer must never become a folder of placeholder images.

## Landing (after download — separate step)

- Land approved cards into the select-screen card assets through the
  normal reviewed merge path. Keep the report.json + GPU-VERIFICATION
  with the batch record (not in the game assets dir).

## Metrics to record (see results-template.md)

Per model: input GLB bytes + mesh/material counts, render_path,
post (gpu/cpu), per-view PNG bytes + px, render seconds, eye-check
result (pass/fail + what was wrong if fail), plus the GPU-VERIFICATION
block.
