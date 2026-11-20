# Lane 5 — Stages + Loading + Performance (2026-10-24)

Owner task (lane brief): stage systems, asset streaming, optimization
pipeline for Western Heart. This PR is the stages/geometry + loading +
gltfpack half of that brief. It does NOT touch fighter combat logic,
moveset JSONs, animation banks, menus/HTML, music files, or story
files, and it does NOT touch break STATE in stagebreaks.js (combat
lane owns that); it owns stage GEOMETRY/transitions, loading/
streaming, and the optimization pipeline.

## 1. Stage audit — what the files actually say

Stage registry: game/js/stages.js. Counted from the registry itself:

- 8 canon lands: shrine, tong-nou, tree-of-life, plains-of-chi-u,
  octagonal-shrine, helix-palace, palace-of-dreaming,
  phantom-marketplace. All share dims width 16.8 / depth 6.0 /
  wallDistance 8.4, spawns P1 −3.5 / P2 +3.5.
- 15 Tekken 3 retro stages (letters a, b, c, d, e, f, g, i, j, k, l,
  m, n, t, u): real TMD panorama geometry + decoded texture atlases
  (teardown/tekken3/stages/<letter>/). No breakables declared.
- 17 WWF No Mercy arenas (11 show/PPV + cage + 6 backstage areas):
  real AkiModel geometry. No breakables declared.
- 1 boss stage (sunra). No breakables declared.
- 1 Tekken 7 stage (t7-mishima-dojo): PRIVATE BUILD ONLY — pushed
  only when globalThis.__WH_PRIVATE_ASSETS is set; its GLB is not in
  the public repo. No breakables declared.

Declared breakables on main (the only multi-level geometry the repo
actually defines):

| Stage | Breakable | Lower level (new geometry data) |
|---|---|---|
| shrine | floor, x 0, z 0, r 2.6, depth 6 | groundY −6 |
| plains-of-chi-u | floor, x 2.5, z 0.5, r 2.4, depth 6 | groundY −6 |
| helix-palace | balcony, x 5.5, z 0, r 2.2, w 4.5, depth 6 | groundY −6 |

Plus the stagebreaks.js default: EVERY stage without noWallBreak
gets breakable walls at ±wallDistance, extending bounds by 4.5 on a
break (8.4 → 12.9). That is now expressed as data, not just behavior.

### New geometry module: game/js/stage-levels.js

Pure, dependency-free, testable in Node (test/stage-levels.test.mjs,
5 tests passing):

- resolveStageLevels(def): upper + wall-broken (unless noWallBreak)
  + one lower level per declared floor/balcony breakable.
- levelAfterBreak(def, breakable): destination level for one break,
  or null (unknown type, wall break on a noWallBreak stage).
- composeLevel(def, broken[]): groundY = deepest declared drop,
  wallDistance = wall-broken bound when a wall broke.
- WALL_BREAK_EXTEND = 4.5, mirroring stagebreaks.js WALL_EXTEND.

### Tekken multi-level structures — honest sourcing

- T7 archetypes named in the stagebreaks.js header (Forgotten Realm
  / Brimstone & Fire / Devil's Pit floor breaks; Jungle Outpost 2
  balcony break) are the MODELS for the shapes above. WH ships no T7
  stage geometry for them, so no T7 level is claimed as a WH file
  extraction. T7/T6/T5 multi-level structures beyond these archetypes
  are UNVERIFIED for WH stages.
- T3 retro stages: whether the T3 originals had floor breaks is
  UNVERIFIED (their WH form is a panorama shell). They get upper +
  wall-broken only, per the stagebreaks.js wall default.
- Arena laws honored: no colors, sky tints, or canon look changed
  anywhere in this PR. Tree of Life's washed-out sky, lighting rigs,
  and floor tints are untouched. The "blocky prototype" geometry
  question is a builder/visual pass, not a data pass — this PR adds
  level data under the existing builders; it does not remodel any
  arena. Sequencing honored: this is polish data on top of working
  combat, not a replacement for it.

## 2. Loading / streaming — what existed, what this PR adds

Already on main (verified by reading, not assumed):

- Select-screen highlight ALREADY prefetches the highlighted
  fighter's model (select-screen.js highlight + applyAttire call
  assets.prefetch). The lane brief's "hover/tap preload" is therefore
  PARTIAL, not missing: it covers fighters on highlight, not stages.
- assets.js ALREADY loads only the fight's 2 fighters (+ transform /
  form targets) at FIGHT press, with byte-level progress, abortable
  idle warm lane, and an in-flight join (no double downloads).
- load-progress.js ALREADY maps fighter bytes to 0–85% of the bar
  with a creep to 97% and names the current asset.
- PR #1041 MERGED DURING THIS LANE (merge b509f179, 2026-10-24):
  it adds preload.js (instant select-card images + warmLockedFighters
  for locked fighters' GLBs on stage-screen dwell) + the Kaggle card
  factory. This PR does NOT duplicate it: preload.js warms CARDS and
  FIGHTERS, preloadStage warms STAGE assets — the two meet at FIGHT
  but cover different bytes. This lane re-synced main.js onto the
  merged #1041 version (its show() stage-dwell fighter warming is
  preserved untouched) and re-applied only the Lane 5 preloadStage
  calls on top.

Gaps this PR closes:

- Stage assets previously loaded ONLY at arena-build time, AFTER the
  fighter loads, inside builders (GLTFLoader.loadAsync / fetchStageOBJ
  at build). New: stages.js preloadStage(stageId) warms a stage's OBJ,
  GLB (fetched + cached, not parsed), atlas, and pano in parallel,
  never throws, and shares one in-flight promise per stage.
- main.js now kicks preloadStage off (a) when the versus stage screen
  opens and (b) at startFight, in parallel with the fighter loads —
  fire-and-forget both times, so a slow stage fetch can never block
  a screen or a fight. The builder's own loads remain as fallback.
- Persistent caching is NEW: game/js/asset-cache.js wraps the Cache
  API (wh-assets-v1, same-origin/relative URLs only, 100 MB cap,
  silent no-op without `caches`). assets.js reads cached model bytes
  before fetching and stores successful downloads; stages.js does the
  same for OBJs and preloaded GLB/atlas/pano bytes. Stage GLBs loaded
  via GLTFLoader.loadAsync at build time still go through the HTTP
  cache only — wiring those through the Cache API is a follow-up
  (see Gaps).
- Honest progress extended: load-progress.js gains
  window.__whStageProgress(stageId, frac), mapping stage warming to
  85–97% of the same bar. The bar never moves backwards and never
  passes the creep cap on a guess.

### Load-time numbers — NOT claimed here

Menu → select loaded time, tap fighter → card shown time, and
FIGHT → fight starts time were NOT measured in this lane: they need
a live browser play pass (phone portrait, human navigation), which
the lane brief explicitly hands to the coordinator. The code paths
above are the mechanism; the timings must come from that pass, with
before/after on the same device and build. Any PR claiming those
numbers without that pass would be guessing. loadperf.js already
defines the marks (boot/menu/select/stage/preview) that pass should
read; preloadStage also records window.__whStagePreload
({stage, warmed[], failed[]}) for it to inspect.

## 3. Optimization pipeline — measured, pinned, gated

Tool dir tools/gltfpack/ already existed on main (fetch script +
job runner); this PR extends it, it does not duplicate it, and it
creates no tools/optimize-models.sh.

Flag policy (pinned in run_gltfpack_job.py, batch-optimize.py, and
the README — all three must agree):

- -cc always (assets.js sets MeshoptDecoder — verified at
  assets.js line ~1117, so -cc outputs load as-is; never bare -c).
- -kn for skinned fighters only (bone names load-bearing).
- -tc OPT-IN per asset with measurement only (it GREW one textured
  model +7%, 483,820 → 519,344 bytes, per the lane brief; the
  three.js Basis transcoder (WASM) must be wired before any -tc
  asset ships — that wiring is NOT in this PR, see Gaps).
- -si OFF by default; allow-list only; a skinned fighter needs an
  explicit approved entry (owner eye-check). LOD is stages/props
  only.

Measured 2026-10-24 (gltfpack 1.3, local runs, real files):

| Asset | Before | After | Flags |
|---|---|---|---|
| Jungle Outpost stage | 1,669,744 | 680,460 (−59%) | default |
| Jungle Outpost stage | 1,669,744 | 219,160 (−87%) | -cc, unskinned, no -kn |
| Jungle Outpost stage | 1,669,744 | 284,540 | -cc -kn (the -kn cost on an unskinned prop: +30%) |
| Jungle Outpost stage | 1,669,744 | 284,540 | -cc -tc -kn (no texture change on this asset) |
| burger re-export (from 81,416,552-byte intermediate) | 81,416,552 | 19,919,212 (−76%) | -cc -kn, 50 joints / 1 skin intact |

New tooling:

- batch-optimize.py: manifest-driven batch (game/assets/models +
  game/assets/stages by default, roster opt-in). Validates every GLB
  (header, JSON chunk, BIN length, bufferView ranges, with the
  meshopt carve-out: meshopt views' byteLength is the DECODED size,
  the stored extent is the extension's byteLength — a valid -cc
  output was falsely flagged before this fix), refuses to overwrite
  inputs, writes a manifest JSON with per-asset sizes/flags/status.
  --dry-run plans without a binary.
- check-budgets.py: fails on output > input, output over cap
  (fighter 40,000,000 / stage 5,000,000 / default 10,000,000 bytes),
  -tc without tc_measured, simplified skinned without approval.
- test_gltfpack_pipeline.py: 10 unit tests, no binary needed
  (validation, flags, budgets, runner -tc opt-in). CI workflow
  .github/workflows/gltfpack-budget.yml runs them on PRs touching
  tools/gltfpack/.
- run_gltfpack_job.py: -tc changed from unconditional default to
  opt-in (params.tc); -kn default true (EXPORT panel optimizes
  fighters); simplification refused without simplify_approved.

### burger-fixed.glb — blocker + re-export (full note: tools/gltfpack/BURGER-REEXPORT.md)

- Reproduced: gltfpack 1.3 rejects burger-fixed.glb (31,495,968
  bytes) with "buffer too short". Outer header is consistent
  (header = file size; buffer byteLength = BIN chunk = 31,412,552);
  the inconsistency is inside the EXT_meshopt_compression payloads
  (7 meshopt bufferViews). The batch validator correctly passes it
  and the gltfpack stage then fails it — surfaced, exit 1, nothing
  shipped. The broken file is NOT shipped as "optimized".
- Re-export verified: the 81,416,552-byte uncompressed intermediate
  optimizes cleanly with -cc -kn to 19,919,212 bytes, 50 joints / 1
  skin intact, re-parses, passes the batch + budget check.
- The regenerated 19.9 MB binary is NOT committed in this PR: it is
  a fighter body that belongs to the rig lane with an owner
  eye-check, not smuggled inside a stages/loading PR. It is staged
  in the lane workspace with its batch manifest for that lane.

### Cape body topology (context)

1,638,010 verts / 1,045,182 non-manifold edges (33%): weight
smoothing and this optimizer cannot fix it. Documented path is a
remesh to clean manifold ~50–100k with Alisa weight transfer (Cape
rig lane). When that output lands, it goes through batch-optimize.py
as a skinned fighter (-cc -kn, no -si without approval).

## 4. GPU jobs — blanket GPU order (user 2026-10-24 20:26 CDT)

"Everything that we've been talking about today get the GPU working
on it" — no carve-outs. This lane's GPU workstreams are PREPARED in
tools/gltfpack/gpu/ (the lane cannot execute a Kaggle/Colab browser
session itself, so execution is a coordinator delegation — see §5
item 2). No GPU run is claimed anywhere in this PR; every number
below is a local CPU baseline, and GPU speedups will be measured
per job in the notebook manifest, never asserted in advance.

- Orchestrator: lane5-gpu-jobs.py — queue esrgan → gltfpack → lod →
  webp → cards, writes GPU-PROOF.txt (nvidia-smi + torch.cuda),
  per-step wall seconds, and (with --cpu-baseline) a subset CPU
  baseline before the GPU step. --require-gpu by default: no CUDA
  means exit 2, never a silent CPU run. Kaggle T4 x2 first, Colab
  as backup/overflow — switch, never stop; the session stays open
  and jobs queue continuously.
- esrgan-upscale.py: Real-ESRGAN upscaling of stage textures +
  card images (CUDA required; --cpu exists only for baseline
  subsets; missing weights/install exits 2 with install steps and
  writes no placeholder image).
- webp-basis-batch.py: WebP ship-if-smaller + gltfpack -tc measured
  per asset. Both conversions discard grown outputs (measured:
  tree-of-life pano WebP q90 GREW +14%, 39,344 → 45,028 bytes).
- Cards (Blender EEVEE-GPU renders + menu assets): REUSED from
  tools/kaggle-gpu-pipeline/kaggle_card_factory.py, not
  reimplemented — the orchestrator feeds it a Lane 5 manifest.
- LOD generation: batch-optimize.py with a stages/props-only
  simplify allow file; a skinned fighter without approved=true is
  refused, same as the CPU pipeline.
- CPU baselines measured locally (no GPU/torch on this VM):
  gltfpack -cc Jungle Outpost 0.126 s (1,669,744 → 219,160);
  gltfpack -cc -kn burger re-export 4.252 s
  (19,919,212 → 19,905,572, second pass); PIL WebP q90 pano
  0.349 s (grew, discarded). Real-ESRGAN and EEVEE times are NOT
  measured locally and must be measured in-notebook before any
  speedup is reported for them.

## 5. Gaps, blockers, and delegations (honest list)

1. Live load timings (menu → select, tap → card, FIGHT → fight)
   — BLOCKED on a live browser play pass. Delegate: coordinator
   (phone portrait, human navigation, before/after on one device).
   This PR is measurement-ready (loadperf marks +
   window.__whStagePreload), not measurement-complete.
2. Kaggle GPU batch optimization / pre-rendering — NOT run here.
   The batch script is GPU-job-ready (manifest in, manifest out),
   but the lane brief reserves GPU execution for the coordinator's
   browser session (notebook linked in the brief). Delegate:
   coordinator. No GPU output is claimed.
3. Basis transcoder (WASM) wiring for -tc assets — NOT done. Until
   it lands, -tc stays opt-in and no -tc asset ships. Follow-up for
   the loading lane or a dedicated transcoder pass.
4. Stage GLBs loaded via GLTFLoader.loadAsync at build time bypass
   the new Cache API (HTTP cache only). Follow-up: route those
   through asset-cache.js the way fetchStageOBJ now is.
5. PR #1041 MERGED during this lane (see §2); PR #1046
   (asset-pipeline CI) was still OPEN at last check. This PR neither
   depends on nor duplicates #1046; if it lands, the budget seams
   here (check-budgets.py vs asset-pipeline budgets) should be
   reconciled in a follow-up, not by rewriting either PR.
6. OWNED-GAME RULE (user 2026-10-24 20:21–20:22 CDT, in MEMORY.md):
   full game files for OWNED games are authorized source, not
   piracy; the user's word suffices and proof is never demanded.
   USE, not redistribution: files are extracted and wired into
   Western Heart; the original game is never shipped, and WH ships
   with no famous names. This PR ships no game files at all, so the
   rule changes nothing in its diff — it governs the sourcing of
   future stage/model pulls (T7 stage files, T8 conversions) that
   this pipeline will optimize when they land.
7. T8 BOUNDARY (coordinator, 2026-10-24): T8 SFM model archives
   (83 MB Yoshimitsu + 30 MB Asuka) and T8 select-reference work
   belong to the dedicated T8 lane. This PR does not touch them.
   If that lane hands this lane converted models, they run through
   batch-optimize.py like any other model (coordination, not
   duplication).
6. LOD files: no LOD variants exist in the repo for stages or
   fighters (grep for lod/LOD in stages.js and assets.js: none).
   Simplification stays off by default until LOD assets exist and
   pass an owner eye-check per asset.
7. T7/T6/T5 stage structures beyond the named archetypes:
   UNVERIFIED (see §1). A future teardown pass with actual T7 stage
   files could promote specific levels from UNVERIFIED to sourced;
   this PR invents none of them.
