# Western Heart studio-standard workflow — research + wiring (2026-10-24)

Goal (user directive 2026-10-24 19:20–19:21 CDT): pull in + wire up, 100% not pieces,
in the best places, GPU verified — so the workflow runs at actual game-dev studio and
industry standard: faster, better, more optimized, higher quality, expanding horizontally
(breadth) and vertically (depth).

Standing rules honored: no guesses (every number below was measured, every price/license
claim comes from a source read this session); no waiting on anyone; work done via
browser/VM/Kaggle GPU by this crew; LP1/RP2/LK3/RK4 naming; never push main directly —
this package ships as a PR (payload manifest at the bottom).

## 1. PULLED + TESTED (measured, not claimed)

### 1a. gltfpack 1.3 (meshoptimizer, MIT) — PULLED, TESTED, SCRIPTED
- Binary: `tools/gltfpack` in this directory (meshoptimizer v1.3 release,
  gltfpack-ubuntu.zip, 4.1MB). `gltfpack 1.3` confirmed via help output.
- Measured on real WH assets (2026-10-24):
  - Cape hand stance GLB: 158,884 → 72,812 bytes (**-54%**). Nodes 95→95,
    animations 1→1, skins 1→1 preserved. Safe for skinned rigs with `-kn`.
  - Jungle Outpost stage: 1,669,744 → 680,460 bytes (**-59%**). Materials 15→15;
    meshes merged 203→111 (fewer draw calls — the perf win, not just bytes).
  - Pipeline script end-to-end: `wh-asset-pipeline.sh` reproduces the hand-stance
    result exactly (158,884 → 72,812) with a `_pipeline-report.txt`.
- Script: `wh-asset-pipeline.sh <input> <output-dir> [simplify-ratio]`
  - ALWAYS `-kn` (keep node names — bone names are load-bearing for fighter rigs).
  - NEVER `-c` (meshopt compression) until the game loader calls
    `GLTFLoader.setMeshoptDecoder` — default output loads in any three.js loader
    (r111+ `KHR_mesh_quantization`).
  - NEVER overwrite sources; outputs go to a separate dir.
  - `-si` simplification: default OFF. On the hand-stance asset `-si 0.5` produced a
    byte-identical file (no effect on that asset) — LOD simplification is therefore
    STAGES/PROPS ONLY, and only with an owner eye-check per asset. Never simplify a
    skinned fighter blind.
- Pipeline order (meshoptimizer docs): index → simplify (optional) → vertex-cache
  optimize → overdraw optimize → vertex-fetch optimize → quantize → compress (optional).
  gltfpack applies this internally; the script pins the safe subset above.

### 1b. Texture compression — TESTED, honest mixed result
- gltfpack `-tc` (KTX2/BasisU, `KHR_texture_basisu`) on AARON_RUBEN.glb (3 embedded
  images): 483,820 → 519,344 bytes (**+7%, GREW**). Output carries
  `KHR_texture_basisu` + `EXT_texture_webp`, images as `image/webp`.
- Lesson, stated plainly: BasisU/KTX2 is a GPU-memory + upload-speed win, NOT a
  guaranteed download-size win. Small textured models can grow. Rule: measure per
  asset; `-tc` is OPT-IN, and it additionally requires the three.js loader to wire
  the Basis transcoder (WASM) before any `-tc` asset ships to players.
- Jungle Outpost `-tc` run: no-op (0 embedded images — materials reference nothing
  embedded). Texture work there means finding/attaching the real textures first.
- Staging rule (from pipeline research): keep canonical uncompressed sources
  (PNG/EXR) as the authority; cache outputs keyed on (file-hash, encoder-version,
  flags); iteration builds use fast presets, final builds use exhaustive encodes with
  PSNR/SSIM recorded.

### 1c. Kaggle GPU — VERIFIED LIVE (parent browser task), jobs READY (not yet run)
- Notebook: https://www.kaggle.com/code/marsfmmg/notebook2ff3176461/edit
- Verified: 2x Tesla T4, 15GB each, driver 580.178.04, CUDA 13.0, `nvidia-smi` clean,
  quota ~30 hrs/week (~29h59m remaining at check). Session left running — quota counts
  while open, close when idle.
- Job scripts in `kaggle-jobs/` (ready-to-paste cells, NOT yet executed — no claim
  otherwise): 01 UniRig auto-rig, 02 Real-ESRGAN batch upscale. Each downloads ONLY
  outputs back to the repo pipeline. Per-job GPU verification = nvidia-smi + job
  metrics in the run log.
- SUPERSEDING (parallel lane, 2026-10-24 ~00:21–00:25): `~/workspace/unirig/` holds
  the fuller GPU lane — `kaggle_unirig_notebook.py` (full UniRig driver: clean →
  skeleton GPU → skin GPU → merge → weight transfer → verify/render, `--gpus 2`
  parallel) and `kaggle_batch_retarget.py` (retarget skeleton, honestly NOT finished:
  writes no retargeted GLBs until the first UniRig run returns real joint names).
  `checkpoint/` is EMPTY (download at Kaggle runtime). The PR payload should ship
  the unirig/ scripts as authoritative, not this doc's starter cell.
- GPU verification standard adopted: a tool is "GPU-verified" only when a real job's
  output + metrics exist — setup alone never counts. UniRig and Real-ESRGAN are
  therefore "GPU-ready", not "GPU-verified", until their first cells run.

### 1d. Floor detection — CODE WRITTEN (side-chat pull, game PR owed)
- `floor-detect.js`: 5-ray median grid sensor (Three.js Raycaster, no new dependency).
  Requirement came from side chat "Cape Jones 3D work" (floating character — detect
  floor "like a grid sensor ... so you can get her feet on the [floor]").
- Integration point: `game/js/fighter.js`, once per tick, AFTER root-motion, BEFORE
  arena clamp + pushout. No-hit behavior: hold last good height, never void-snap.
- Status: MODULE WRITTEN, NOT MERGED — needs game PR + live playtest.

### 1e. Side-chat work — PULLED (manifest, no private data copied)
- Full mapping in `SIDE-CHAT-PULL-MANIFEST.md`: Kaggle API token pattern (token NEVER
  in files — placement via browser/Secure Vault owed), Cape/Alisa rig work (bone map
  160/160, IK bake, weld/smoothing, topology audit → remesh plan), floor detection,
  3D-fighter research targets (DOA/VF5/KOF 3D, Bass Armstrong used, Theory Attire 4
  Tripo link — needs owner fighter mapping before archiving), Pantera voice (already
  in main, no action), Nosferatu M4 (music lane owns it), Kaggle notebook backend.

## 2. HORIZONTAL EXPANSION — breadth (research findings, wiring status each)

### 2a. Asset pipeline automation (WIRED: script + rules above; NEXT: CI step)
Studio pattern (GDC 2015 next-gen pipelines; modular pipeline research): high-res →
game-res → bake → assemble → import, with glue code handing files between tools, plus
gates: validate (corrupt/format/naming) → track (status/version/deps) → process per
type (polycount, LOD, UV, rig for models; compress, mipmaps, channel-pack for
textures; framerate, skeleton, root-motion for animation) → validate budgets →
engine import (settings, placement, material links). WH mapping: gltfpack script =
process step; missing and owed: validate gate (naming/polycount/budget checks as a
CI script) and engine-import step (loader + deploy). No manual steps once both land.

### 2b. Audio middleware — BROWSER TRUTH (see also child audio report)
WH is a browser/Three.js game: native Wwise/FMOD SDKs do NOT drop into it. The
industry-standard move is a Wwise-STYLE event system on WebAudio (events, switches,
states, RTPCs), not an SDK install. FMOD vs Wwise research (G2 + 2026 guides):
FMOD free under $200k–$500k budget (sources disagree — verify current terms before
any commercial decision), DAW-like timeline, indie/mid-tier (Hollow Knight, Celeste);
Wwise free one project/platform under $200k, state/switch/RTPC system, AAA standard
(Assassin's Creed, God of War), steeper learning curve, better profiler. CRI ADX is
the voice/streaming specialist (Japanese production alignment). For WH: adopt FMOD's
timeline concepts for adaptive music + Wwise's state/switch/RTPC concepts for combat
audio, implemented on WebAudio. Native profiler live-update has no browser equivalent
— alternative is in-game audio debug overlay + recorded session logs.
(Full engine design with file layout + tables: child audio report, merged at delivery.)

### 2c. Animation / motion tools (truth table — free tiers that CANNOT ship are flagged)
- Cascadeur: free tier = full toolset BUT exports ONLY .casc, non-commercial. It
  CANNOT feed the game on free tier. Indie ~$8/mo annual adds FBX/DAE export +
  commercial under $100k revenue; Pro ~$33/mo annual, full commercial. AI posing,
  inbetweening, AutoPhysics, Python API, Quick Rig (Mixamo/Metahuman/Daz skeletons).
  Verdict: Indie tier is the minimum viable entry for WH canon MADE animation polish.
- DeepMotion (Animate 3D): video → retargetable 3D. Free ~60 sec/mo, personal
  non-commercial. Cheap test path for canon moves; paid needed to ship.
- Move.ai: markerless mocap from video, professional tier, pay-as-you-go from ~$0.01/s
  reported — professional product, not consumer; use only if a canon move needs it.
- Rokoko Studio: mocap cleanup/retarget hub; pairs with Cascadeur polish step.
- Blender Auto-Rig Pro: paid Blender rigging addon — candidate for the rigging
  pipeline alongside UniRig (UniRig first: already in repo, GPU-ready).
- Mixamo: batch download + GPU retarget automation (already in scope — automate, don't
  hand-download).

### 2d. AI / ML tools
- Real-ESRGAN (xinntao/Real-ESRGAN, BSD-3-Clause, 37k+ stars): 2x/4x/8x, photo model
  RealESRGAN_x4plus, anime model RealESRGAN_x4plus_anime_6B (clean edges on
  line-art/flat-shaded textures). Needs PyTorch + CUDA → Kaggle job 02. Batch rule:
  upscale only below-target textures; eye-check one output per batch (over-smoothing
  and tile seams are the known failure modes).
- Stable Diffusion / ControlNet: texture/concept generation — Kaggle-GPU path, paid
  API otherwise; wire AFTER Real-ESRGAN proves out (don't stack unproven AI steps).
- OpenImageDenoise: render denoising — candidate for the show-render pipeline, not
  the game runtime.
- Meshy / Tripo: 3D generation already in use (Tripo); automate batch generation via
  API instead of one-off web drops.

### 2e. Performance / profiling
- Proven: draw-call merging via gltfpack (203→111 on Jungle Outpost), quantization
  (-54%/−59% sizes). Next: per-asset budgets (polycount, texture res, draw calls)
  enforced by the validate gate; occlusion culling research only if a stage proves
  overdraw-bound (no evidence yet — don't implement blind).
- RenderDoc (open source GPU profiler): document a capture workflow for the desktop
  build; for the browser build, use browser GPU profiling + frame-time logging
  (RenderDoc does not capture WebGL in the same way — state this, don't pretend).
- GPU profiling via Kaggle: Nsight-style profiling belongs on the Kaggle job runs
  (record per-job GPU time/memory), not on the VM.

## 3. VERTICAL EXPANSION — depth (what "studio" actually means beyond tools)

### 3a. CI/CD (existing WH gates + owed additions)
- Existing (proven in recent PRs): instruction-gate, game-unit-tests, menu-touch-e2e,
  ui-sources, 12/12-checks merges via git_merge.py, Netlify auto-deploy from gh-pages.
- Owed, in priority order: (1) asset-pipeline CI step (run wh-asset-pipeline.sh on
  changed GLBs, fail on budget breach); (2) performance regression check (load-time +
  frame-time smoke on every build, alert on regression); (3) visual regression
  (automated screenshot comparison for select/fight screens); (4) playtest bot
  (automated fight simulation: every string fires, every input maps, no string→chord
  mapping — the batch-strings test is the seed for this).

### 3b. Documentation + knowledge (this package is part of it)
- Auto-generated docs from code (JSDoc) for game/js — owed, low cost.
- Pipeline runbooks: asset, animation, audio, build — this doc + the scripts are the
  start; each pipeline gets a one-page runbook before it is called "done".
- Decision logs: docs/decisions/ already exists — every major tool adoption gets one
  (this doc's PR carries one).

### 3c. Quality gates (no more "less broken")
- Pre-merge: animation verification (exact clip or UNMAPPED), moveset verification
  (input/damage/anim present), performance check, visual proof. The batch-strings PR
  (#1024) is the template: simulation green + user playtest still owed before "fixed".
- Automated playtesting catches bugs before the user does; user playtest loop stays
  (user plays → reports → fix from files → redeploy → repeat) and gets formalized
  with a structured report template, not chat fragments.

### 3d. Studio workflow (process, not just tools)
- GitHub Issues/Projects for all work (not just chat): every task tracked, assigned,
  status visible. Side-chat work proves why: work done in side chats was invisible to
  main until explicitly pulled — the manifest exists to close that gap permanently.
- Code review: every PR reviewed by another agent before merge (already the norm via
  checks; make review explicit).
- Asset review: every new model/animation/audio gets visual/audio proof before merge.

## 4. Git LFS — HONEST CALL (do NOT blanket-migrate)
- GitHub free LFS: ~1GB storage + 1GB/mo bandwidth. WH's deploy set alone was 5.7GB;
  a blanket LFS migration would blow the free quota immediately and LFS pointers do
  NOT mix with the Git Data API merge flow this repo relies on.
- Correct wiring: LFS opt-in ONLY for the PRIVATE game-reverse-engineering repo and
  for narrow new asset dirs, with quota monitoring + `GIT_LFS_SKIP_SMUDGE=1` in CI
  for jobs that don't need assets. Track narrowly (`assets/` only), prune monthly,
  never prune tagged objects. A `.gitattributes` template is owed with the LFS PR,
  not a migration.

## 5. PR PAYLOAD MANIFEST (for parent to push — surgical, no clobber)
Target repo: mhvnsnt/western-heart, feature branch, PR with instruction-gate sections.
Files (from `~/workspace/studio-pipeline/`):
- `tools/wh-asset-pipeline/wh-asset-pipeline.sh` ← `wh-asset-pipeline.sh`
- `tools/wh-asset-pipeline/tools/gltfpack` (binary, v1.3) + `tools/wh-asset-pipeline/tools/gltfpack-ubuntu.zip`
- `tools/wh-asset-pipeline/floor-detect.js` (game integration: copy to `game/js/` in the
  same PR only with the fighter.js hook + playtest note; otherwise ship as tool doc)
- `tools/wh-asset-pipeline/kaggle-jobs/01-unirig-setup.py`, `02-realesrgan-batch.py`
- `docs/research/STUDIO-WORKFLOW-2026-10-24.md` ← this doc
- `docs/research/SIDE-CHAT-PULL-2026-10-24.md` ← `SIDE-CHAT-PULL-MANIFEST.md`
- `docs/decisions/2026-10-24-studio-workflow-tools.md` (decision log — parent drafts
  from this doc at PR time)
NOT shipped: `test-out/`, `batch-test/` (proof artifacts only, stay in workspace).
Pre-merge checks required: instruction-gate body, game-unit-tests, plus the new
asset-pipeline script's own proof (hand-stance 158,884 → 72,812 reproduced).

## 6. PARENT BROWSER DELEGATIONS (subagent cannot do these — do not fake them)
1. Kaggle API token placement into automation host kaggle.json (side chat generated it;
   value never in chat/files) + read-only verification call.
2. Kaggle notebook execution of job cells 01 (UniRig) + 02 (Real-ESRGAN) — first real
   GPU jobs; record nvidia-smi + outputs to convert "GPU-ready" → "GPU-verified".
3. Account downloads/sign-ins: Cascadeur Indie (paid, FBX export required), FMOD/Wwise
   evaluations (only if a native-tool evaluation is wanted — browser engine design
   above is the no-SDK path), Mixamo/Tripo batch API keys if batch automation is used.
4. Full main→gh-pages sync (owed from earlier work) so Netlify picks up everything at once.

## 7. ADDENDUM — visual regression design + 3D-fighter extraction gap (researched 2026-10-24)

### 7a. Visual regression for a WebGL game (concrete design, not a vendor pitch)
- Tool: Playwright Test (free, self-hosted) + pixelmatch — `expect(await page.screenshot()).toMatchSnapshot('golden.png', { threshold: 0.2 })`.
  Percy (BrowserStack) free tier is 5,000 snapshots/mo, but cloud + usage pricing +
  no self-host is a worse fit than Playwright for WH; Percy is the fallback, not the plan.
- WebGL-specific gotcha (from web-game testing research): `canvas.toDataURL()` must run
  immediately after the render call, OR the context needs `preserveDrawingBuffer: true`
  (small perf cost — enable it in test builds only, never in the shipped build).
- Determinism rules: disable animations for captures, mask dynamic regions (timers,
  random select), run baselines + CI in the same Playwright Docker container, update
  baselines ONLY via a deliberate CI job (`--update-snapshots changed`), never blanket
  overwrite from a laptop (different OS rendering would silently re-baseline everything).
- Scope for WH v1: select screen, main menu, fight frame-30 pose per fighter — the
  screens that already have proof renders today. This turns today's manual proof
  screenshots into a gate.
- Playtest bot (game-logic side, separate from pixels): drive the game headlessly,
  assert every string fires, every input maps, no string→chord mapping, damage values
  present. The batch-strings Node test is the seed; the bot is its headless-runner form.

### 7b. 3D-fighter extraction — honest gap, direction only
- Context confirmed: VF (1993, AM2/Yu Suzuki, Model 1) is the first polygon fighter;
  Dural is the VF boss (Zen's base lineage). VF5FS animation is widely praised over
  Tekken's for fluidity (e.g., Wolf's Giant Swing vs King's, VF wavedash vs Tekken
  wavedash). DOA's Triangle System (strikes > throws > holds > strikes), counter-holds,
  and Free Step 3D movement are its signature systems; DOA6 post-launch support ended 2020.
- Gap stated plainly: this session found NO verified DOA/VF5/KOF-3D extraction tool
  chain (model/animation formats + extractor) from public search. Do NOT claim one
  exists. Next research step (extraction lane): target VF5FS + DOA6 modding wikis and
  file-format docs specifically, and check what the repo's existing VF/DOA teardown
  dirs already contain before any new pull. The side-chat target list (Section 1e /
  manifest §4) stands as the target list, not as proof of availability.

## Sources read this session (grounding, not guesses)
- GDC 2015 next-gen pipelines (polycount write-up): automation robots handle naming,
  folders, baked maps; high-res → game-res → bake → assemble → import.
- Modular asset pipeline (prolificstudio): validate → track → process → validate →
  engine import modules.
- meshoptimizer/gltfpack docs (meshoptimizer.org, DeepWiki): pipeline order, -c/-cc/-tc
  semantics, KHR_mesh_quantization / EXT_meshopt_compression loader requirements.
- FMOD vs Wwise (G2 compare; generalistprogrammer 2026 guide; dev.to CRI/Wwise/FMOD):
  licensing bands, timeline vs state/switch/RTPC, AAA vs indie usage.
- Cascadeur pricing (aiquiks, aitools.fyi, creatify): free .casc-only lock, Indie
  ~$8/mo annual, Pro ~$33/mo annual; DeepMotion free ~60s/mo.
- Real-ESRGAN (modelslab, ai-review, wavespeed): BSD-3-Clause, models, anime variant,
  tiling/GPU notes.
- Basis/KTX2 (beefed.ai, webcodingcenter, Khronos docs): ETC1S vs UASTC, toktx/basisu
  commands, KHR_texture_basisu, GPU-memory vs file-size distinction.
- Git LFS (geeksforgeeks, medium practical guide, deepwiki): setup, quotas, narrow
  tracking, SKIP_SMUDGE CI pattern.
