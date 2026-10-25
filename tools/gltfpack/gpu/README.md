# Lane 5 GPU jobs (blanket GPU order, 2026-10-24)

User order, verbatim intent: "Everything that we've been talking
about today get the GPU working on it. Everything we've been
talking about for the last 24 hours get the GPU working on it
because it's going to cut all of that down by 70 times whatever.
Like it's going to be 70 times the speed."

NO CARVE-OUTS: no workstream in this lane is excused from the GPU
session on "it doesn't need GPU" reasoning. Everything below runs
through the GPU notebook session, in queue order, with measured
proof — including steps whose inner algorithm is CPU-bound (PIL
WebP, gltfpack): those run ON the GPU machine, inside the GPU job,
labelled CPU-bound in the manifest, timed against a CPU baseline.
What is never claimed: a "70x speedup" for any step until its
manifest shows a measured baseline-vs-GPU wall time. Speedup is
MEASURED per job, never just claimed.

## Workstreams in this pack

| Step | What runs | GPU / CPU | Reuse, not duplicate |
|---|---|---|---|
| esrgan | Real-ESRGAN upscaling of stage textures + card images | CUDA (required) | New in this pack (the card factory has no upscaler) |
| gltfpack | batch-optimize.py over models + stages, pinned flags | Runs on the GPU machine, timed | tools/gltfpack/batch-optimize.py |
| lod | batch-optimize.py with a stages/props-only simplify allow file | Runs on the GPU machine, timed | Same batch runner; never a skinned fighter without approved=true |
| webp | WebP ship-if-smaller + gltfpack -tc measured | PIL WebP is CPU-bound, labelled as such, inside the GPU job | New batch script in this pack |
| cards | Blender EEVEE-GPU select-screen renders + menu assets | EEVEE on GPU | tools/kaggle-gpu-pipeline/kaggle_card_factory.py — REUSED, not reimplemented |

Boundary (coordinator, 2026-10-24): T8 SFM model archives (83 MB
Yoshimitsu + 30 MB Asuka) and T8 select-reference work belong to
the dedicated T8 lane — this pack does NOT duplicate them. If the
T8 lane hands this lane converted models, they go through the
gltfpack step above like any other model (coordination, not
duplication).

## Running (coordinator's browser lane owns execution)

1. Open the Kaggle notebook (T4 x2) and keep the session OPEN —
   jobs queue continuously; do not close the session between steps.
2. Attach the repo (or upload tools/gltfpack/ + tools/kaggle-gpu-pipeline/
   + a card manifest) and install once per session:
   `pip install basicsr facexlib gfpgan realesrgan pillow`
   plus the Real-ESRGAN weights (see esrgan-upscale.py header) and
   the gltfpack binary (`bash tools/gltfpack/fetch-gltfpack.sh`).
3. Run the queue:
   `python3 tools/gltfpack/gpu/lane5-gpu-jobs.py --root . --out wh-gpu-out --cpu-baseline`
   (`--cpu-baseline` measures a 1-item CPU baseline per step first,
   then runs the GPU steps. The full batch never runs on CPU.)
4. Download `wh-gpu-out/` (GPU-PROOF.txt + lane5-gpu-manifest.json +
   per-step manifests + outputs) and open a PR with ONLY the real
   outputs (upscales that landed, GLBs that shrank, WebP/-tc files
   that shrank, renders that rendered) — never pending/grew rows.
5. Colab fallback: when Kaggle quota runs low, SWITCH to Colab
   (same commands, same out dir layout) — never stop the queue.
   Record which session ran each step in the manifest notes.

## CPU baselines measured locally (this VM, no GPU, no torch)

These are the baselines the GPU runs beat — or don't, honestly:

| Operation | Input | CPU wall | Result |
|---|---|---|---|
| gltfpack -cc (Jungle Outpost) | 1,669,744 bytes | 0.126 s | 219,160 bytes |
| gltfpack -cc -kn (burger re-export) | 19,919,212 bytes | 4.252 s | 19,905,572 bytes (2nd pass; input already meshopt) |
| PIL WebP q90 (tree-of-life pano, 580x183 palette PNG) | 39,344 bytes | 0.349 s | 45,028 bytes — GREW +14%, discarded by the ship-if-smaller rule |

Not measured locally (no torch / Real-ESRGAN / Blender on this VM):
Real-ESRGAN upscale times and EEVEE render times. Those baselines
are measured inside the notebook by `--cpu-baseline` (ESRGAN subset)
and by the card factory's own manifest (renders), and must appear
in the GPU manifest before any speedup is reported for them.

## What this pack does NOT do

- No live GPU acceleration of the phone game is claimed anywhere:
  the phone browser never talks to Kaggle's GPU. These are
  BUILD-TIME jobs; their outputs are committed into the repo and
  the shipped game loads those outputs fast. (Same honest
  architecture as tools/kaggle-gpu-pipeline/kaggle_card_factory.py.)
- No -tc output ships without the three.js Basis transcoder (WASM)
  wired, and no WebP/-tc output ships when it grew.
- No LOD simplification of a skinned fighter without an explicit
  approved entry (owner eye-check per asset).
