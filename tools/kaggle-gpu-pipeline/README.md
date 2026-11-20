# Kaggle GPU pipeline — Western Heart build-time asset factory

## Honest architecture (read first)

Kaggle's GPU is a cloud notebook GPU. It **cannot** accelerate the phone
game at runtime — the phone browser never talks to Kaggle's GPU. Anyone
claiming live Kaggle acceleration of phone rendering is wrong.

What this pipeline **is**: a **build-time factory**. Kaggle GPU jobs
process assets, and the optimized / pre-rendered outputs are committed
**into the repo**. The shipped game then loads those fast outputs.
That is "Kaggle GPU hooked into the repo" in the only real sense:

```
repo models ──► Kaggle GPU notebook ──► optimized / pre-rendered outputs
                                                     │
                                              committed to repo
                                                     ▼
                              shipped game loads fast outputs (no Kaggle at runtime)
```

Runtime speed on the phone comes from `game/js/preload.js` (card
preloading, fight warming, instant portrait placeholders) plus these
build-time outputs — not from any live Kaggle connection.

## What the factory produces

| Output | Tool | Safety rule |
|---|---|---|
| Pre-rendered character cards (`assets/cards/`) | Blender EEVEE on GPU | No Blender = `pending-render`, **no placeholder written** |
| Optimized models | gltfpack | Always `-kn` (bone names are load-bearing); never `-c` until the loader calls `setMeshoptDecoder`; never `-si` on a skinned fighter unless that fighter is owner eye-checked |
| WebP UI images | PIL (CPU-bound, labelled as such) | Quality 90 default |
| Basis/KTX2 textures | basisu, only if present **and** smaller | An earlier WH test **grew** a model +7% under `-tc` — growth is reported, not shipped, unless `--force-basis` is passed with a reason |
| LODs | Decimation, non-skinned meshes only | Skinned fighters = `skipped-pending-eye-check` (blind decimation changes a fight silhouette) |

Proven gltfpack results on real WH files (studio pipeline, 2026-10-24):
Cape hand stance 158,884 → 72,812 bytes (−54%), IK stance 131,240 →
45,904 (−65%), Jungle Outpost 1,669,744 → 680,460 (−59%, meshes merged
203 → 111, fewer draw calls — the real perf win, not just bytes).

## How to run it (Kaggle, GPU session)

Notebook (already GPU-enabled, 2x Tesla T4, ~30 hrs/week at last check):
https://www.kaggle.com/code/marsfmmg/notebook2ff3176461/edit

1. Attach the repo (or upload this folder + a manifest JSON).
2. Run, with GPU proof enforced:
   `!python3 kaggle_card_factory.py --manifest manifest.json --out out --require-gpu`
3. `--require-gpu` fails loudly with no CUDA device, so a CPU run can
   never silently pass as a GPU run. `out/GPU-VERIFICATION.txt` is the proof.
4. Download `out/`, open a PR with **only real outputs** (renders,
   optimized GLBs that shrank, WebP images) — never the pending rows.
5. **Close the Kaggle session when idle** — quota counts while it is open.

Manifest format: see the script docstring
(`{"fighters": [{"id", "glb", "attires": [{"label", "glb"}]}],
  "stages": [{"id", "glb"}]}`).

## What this PR does NOT claim

- No pre-rendered cards ship in this PR: renders need a Blender GPU
  run on Kaggle (a browser/notebook delegation — subagents cannot run
  the live notebook). The runtime preload in this PR works today on
  the existing `assets/portraits/<id>.png` files, which are the same
  URLs the card DOM already renders — so preloading them is a real
  cache win now, and the factory cards swap in later in one PR.
- No browser load-time numbers are claimed here: live Netlify timing
  needs a live-browser playtest. `game/js/preload.js` records
  `window.__whCardsPreloaded` and the `cards-preloaded` /
  `fight-warmed` loadperf marks so that playtest can report real
  before/after numbers instead of guesses.
- No whole-roster GLB bulk warm: the old `preloadAll()` saturated the
  pipe the first preview tap needed. Cards (2D, small) preload in
  bulk; GLBs warm per highlight and per lock only.
