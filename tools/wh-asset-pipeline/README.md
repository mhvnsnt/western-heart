# tools/wh-asset-pipeline — studio asset pipeline (2026-10-24)

Provenance: workspace studio-pipeline work, 2026-10-24. Shipped verbatim
except this README. Nothing here is wired into the live game yet — this is
the pipeline + its inputs, not a gameplay change.

## wh-asset-pipeline.sh + tools/gltfpack

gltfpack 1.3 (meshoptimizer, MIT). Verified on real Western Heart assets:

- Cape hand stance GLB: 158,884 -> 72,812 bytes (-54%), nodes 95->95,
  animations 1->1, skins 1->1.
- Jungle Outpost: 1,669,744 -> 680,460 bytes (-59%), materials 15->15,
  meshes merged 203->111.

Standing rules (also in the script header):

- ALWAYS `-kn` (keep node names): bone/node names are load-bearing.
- NEVER `-c` (meshopt compression) until the game loader calls
  `setMeshoptDecoder`; default output loads in any three.js GLTFLoader
  (r111+ KHR_mesh_quantization).
- NEVER overwrite sources: outputs go to a separate dir.
- Simplification OFF by default. A simplify ratio is stages/props ONLY,
  with an owner eye-check per asset — never a skinned fighter blind.

Usage: `./wh-asset-pipeline.sh <input-dir-or-file> <output-dir> [simplify-ratio]`
The script resolves gltfpack from `tools/gltfpack` next to itself.

## floor-detect.js — NOT wired into fighter.js yet

5-ray median grid sensor (three.js Raycaster, no new dependency) that
grounds a fighter so feet sit on the floor instead of floating. Status:
module written, game hook NOT applied. Integration point, when a playtest
lane takes it: `game/js/fighter.js`, once per tick, AFTER root-motion,
BEFORE arena clamp + pushout. No-hit holds the last good height, never
void-snaps. Do not wire it without a live playtest (Alisa/Cape feet on
floor on Jungle Outpost + a flat arena, no jitter). See the file header.

## kaggle-jobs/ — READY, NOT RUN

- `01-unirig-setup.py`: UniRig auto-rig GPU cells.
- `02-realesrgan-batch.py`: Real-ESRGAN texture batch upscale GPU cells.
- Both target the Kaggle notebook (2x T4):
  https://www.kaggle.com/code/marsfmmg/notebook2ff3176461/edit
- GPU use is a parent-browser delegation: this lane cannot execute the
  notebook. Confirm UniRig CLI flags from its README before executing;
  the setup cell says so itself — do not guess flags.

## What is deliberately NOT in this PR

- No sampler MP3s, no `test-out/`, `batch-test/`, `batch-in/`,
  `batch-out/` artifacts, no checkpoint files, no credentials or tokens.
- The audio engine + events table live under `game/js/audio/` and
  `game/assets/audio/`; the UniRig GPU lane lives under `tools/unirig/`.
