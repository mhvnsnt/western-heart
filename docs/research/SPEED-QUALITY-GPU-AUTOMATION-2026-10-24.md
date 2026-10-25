# Speed / Quality / GPU / Automation / One-Pass Tools — Research + Wiring

Date: 2026-10-24. User directives: 2026-10-24 19:31 CDT (do not filter pulls;
turn around speed AND quality), 19:33 CDT (speed/quality/GPU/automation/
one-pass tools), 19:34 CDT (pull maximum, wire fully into the repo, keep
working on all complaints + logged items, GPU always).

Status legend (used everywhere below, no exceptions):
- PROVEN = installed and run on a real WH asset/task this session, numbers below.
- READY = script written and logic-tested on CPU; the GPU/CI run itself has
  NOT happened yet and is named as a parent delegation, not claimed.
- DOC = researched from source-read pages; install/wiring documented, not run.
- CI-SIDE = wiring lives in the GitHub Actions workflow, not on this VM.

## 1. Measured proof (all numbers from this session, real WH data)

Dataset: `mvlt-community-pull/t7-all/` — 35 T7 character files, 5,648 moves.
Grounding scan of that data (measured, not assumed):
- damage: string 5,103, None 545. None is a REAL GAP, reported, never filled.
- hit_level: raw strings (h/m/l/Sm/TJ/TC/throws/stance tags, ~600 distinct
  values) or None (12). It is NOT a small enum; no enum assertion is made.
- notation_lp vs notation_original digit-replacement: 0 mismatches / 5,648.
  The LP1/RP2/LK3/RK4 conversion is perfectly consistent on this dataset.

| Run | Result |
|---|---|
| One-pass validator, sequential, 35 files / 5,648 moves | 0.509 s, 0 errors, 0 warnings, 545 null-damage gaps reported, 130 duplicate notations counted |
| One-pass validator, parallel (joblib, 2 workers), same data | 5.006 s, identical totals — SLOWER than sequential |
| One-pass validator, second run, cache hit (35/35 reused) | 0.000 s validation time, identical totals |
| Hypothesis property tests (5 properties) | ALL PASS (determinism, null-never-invented, button-map injective, cache-key content-sensitive, notation round-trip) |
| pixelmatch compare, same PNG vs itself (1,048,576 px) | 0.00% mismatch, exit 0 |
| pixelmatch compare, buffalo-bill-a1 vs a2 | 10.88% mismatch (114,114 px), exit 1, diff PNG written |
| Kaggle GPU script, CPU fallback (stdlib, no pandas) | 5,648 rows, 35 chars, 545 gaps, 0.003 s; top hit levels m 1034, h 651, m (TJ) 426, l (TC) 283, m,m 230 — matches the grounding scan |
| joblib 1.6.0 + hypothesis 6.170.9 install | PROVEN (pip, TMPDIR workaround — see §6) |
| pixelmatch + pngjs install | PROVEN (npm, 11 s, 2 packages) |
| cuDF GPU path | READY, NOT RUN — VM has no NVIDIA GPU; needs Kaggle T4 (see §4) |
| ccache / GNU parallel apt install | PENDING at report time — apt-get update still running after 10+ min; documented as CI-side, not gating |

### The honest parallel finding (do not hide it)

Parallel validation was 10x SLOWER than sequential on this dataset
(5.006 s vs 0.509 s) because process-spawn overhead dominates tiny JSON
parsing on a 2-core box. The lesson, stated plainly:
- Parallel pays off on BIG jobs (clip analysis, image processing, Kaggle
  many-core runs), not on 5 KB JSON files.
- The cache win is the real one-pass win here: second run 0.000 s, zero
  rework. Hash-keyed reuse (the ccache/Turborepo idea applied to game
  data) beats parallelism for small repeated jobs.
- The script therefore defaults to parallel but supports --sequential,
  and joblib is an optional accelerator, never a hard requirement: with
  no joblib it falls back to stdlib concurrent.futures, and with neither
  it still runs sequentially. A pipeline that requires installs to run at
  all is a pipeline that breaks CI.

### Two bugs found and fixed during this work (proof the gates work)

1. Hypothesis `fixed_dictionaries` optional syntax: optional values must
   be strategies, not booleans. Fixed; all 5 properties pass.
2. pixelmatch v5+ is ESM-only: `require('pixelmatch')` returns
   `{default: fn}`. Fixed with a CJS/ESM interop fallback in compare.js.

## 2. The one-pass pipeline (what ships in this PR)

Repo paths (all NEW files — no existing file touched, no clobber risk):
- `tools/wh-onepass/wh_onepass.py` — batch validator (parallel + hash cache)
- `tools/wh-onepass/wh-property-tests.py` — Hypothesis invariants
- `tools/wh-onepass/compare.js` — pixelmatch visual-compare CLI
- `tools/wh-onepass/package.json` — npm deps for compare.js
- `tools/wh-onepass/kaggle-gpu-batch.py` — Kaggle GPU job (READY, §4)
- `.github/workflows/wh-speed-quality.yml` — CI gates (CI-SIDE)
- `docs/research/SPEED-QUALITY-GPU-AUTOMATION-2026-10-24.md` — this file

Why this shape instead of adopting a big framework today:
- WH's batch jobs are scripts + JSON, not a DAG estate. A 300-line script
  with hash caching IS the pipeline; Prefect/Kestra/Airflow are the
  upgrade path if pipelines grow past script scale (see §3.3).
- Zero-install core (stdlib fallback) means CI never breaks on a missing
  package. Accelerators (joblib, hypothesis, pixelmatch) add speed and
  proof but are never load-bearing.

## 3. Catalog (do-not-filter: everything relevant, including niche items)

License column: "verified" only where a source-read page stated it;
otherwise "see repo" — never guessed.

### 3.1 GPU compute + acceleration

| Tool | License | What it does / WH use | Status |
|---|---|---|---|
| RAPIDS cuDF / cuML / cuGraph (now CUDA-X Data Science) | Apache 2.0 (verified) | GPU DataFrames (pandas API) / GPU ML (scikit-learn API) / GPU graphs. WH use: batch moveset analytics on Kaggle T4 (pandas-compatible, near-zero code change). Requires NVIDIA GPU, compute capability 7.0+ (T4 = 7.5, qualifies). Reported ~70x on UMAP/DBSCAN workloads elsewhere — WH must measure its own job, not borrow that number. | READY (script) |
| Ray (UC Berkeley RISELab, Anyscale) | Apache 2.0 (verified) | Distributed Python: @ray.remote tasks, Ray Data batch processing, multi-GPU scaling. WH use: scale batch jobs from this 2-core VM to Kaggle multi-GPU. 34.8k+ stars, 1,000+ contributors per project pages. | DOC (upgrade path) |
| Vulkan Compute / WebGPU Compute | see repo | GPU compute shaders for native/browser. WH use (experimental): move the one-pass validation or clip analysis into compute shaders for the web build. No implementation yet — experimental use, not a claim. | DOC (experimental) |
| FFmpeg NVENC / OpenCV CUDA | see repo | GPU video encode / GPU image ops. WH use (experimental): GPU video rendering for show proofs, GPU texture processing. Requires NVIDIA GPU; Kaggle job pattern same as cuDF. | DOC (experimental) |
| meshoptimizer / gltfpack | MIT (per sibling lane 2026-10-24) | Mesh optimization + GLB compression. PROVEN by sibling lane on real WH files: Cape hand stance -54%, IK stance -65%, Jungle Outpost -59% + meshes 203->111. This lane reuses that result; it does not re-claim it. | PROVEN (sibling) |
| Real-ESRGAN | BSD-3-Clause v0.3.0 (per sibling lane) | GPU super-resolution upscaling for textures. Code pulled by sibling lane; full stack needs torch + GPU = Kaggle job, not this VM. | READY (sibling) |

### 3.2 Batch + parallel processing (one-pass)

| Tool | License | What it does / WH use | Status |
|---|---|---|---|
| Python stdlib multiprocessing / concurrent.futures | PSF (stdlib) | Zero-install parallelism. WH use: the fallback engine inside wh_onepass.py. PROVEN: the script runs with it when joblib is absent (design), and sequentially with neither. | PROVEN (design) |
| joblib 1.6.0 | see repo | loky process backend, n_jobs=-1 uses all CPUs, dask/ray backends if installed. WH use: parallel engine inside wh_onepass.py. PROVEN installed + used (5.006 s run — slower here, honestly reported in §1). | PROVEN |
| Dask | see repo | Parallel arrays/DataFrames/bags, chunked larger-than-memory compute, distributed scheduler. WH use: scale the one-pass validator past single-machine memory (e.g., full animation-bank analysis). Not installed here — upgrade path, not claimed. | DOC |
| GNU Parallel | see repo | Shell-level parallelization (one job per CPU, --jobs, --pipe). WH use: parallelize shell asset steps (gltfpack over a directory, ffmpeg over clips). apt install PENDING (§1); CI-side fallback documented. | PENDING |
| Apache Beam | see repo | Unified batch + streaming model. WH use: overkill for WH's script-scale jobs today; listed per do-not-filter, not recommended now. | DOC (not recommended now) |
| Ray Data | Apache 2.0 (verified, via Ray) | Distributed batch data processing. WH use: same as Ray above, data-parallel flavor. | DOC |

### 3.3 Pipeline automation (no manual steps)

| Tool | License | What it does / WH use | Status |
|---|---|---|---|
| WH one-pass script itself (this PR) | repo license | Hash-cache + parallel + report in one command. This IS the automation for WH's current scale. Retries: not built in — a failed file is reported, not retried; add retry only if flaky steps appear. | PROVEN |
| Prefect 3.0 | Apache 2.0 (verified) | Python-native orchestration: @flow/@task, retries, caching, state tracking, event-driven runs, self-hosted server or Cloud. 23.6k stars, 13M monthly PyPI downloads per source pages. WH use: the upgrade path when WH pipelines outgrow a script (multi-step asset pipeline with retries + scheduling). | DOC (upgrade path) |
| Kestra | Apache 2.0 (verified) | Declarative YAML orchestrator, language-agnostic, low self-host complexity, event-driven. WH use: alternative upgrade path if WH wants YAML-defined pipelines instead of Python-defined ones. | DOC (upgrade path) |
| Dagster | see repo | Asset-based orchestration (assets, not tasks), lineage, dbt integration. WH use: if WH pipelines become asset-centric (model -> rig -> anim -> game), Dagster's model fits. | DOC |
| Apache Airflow | Apache 2.0 (verified) | Mature DAG orchestrator, 104 providers, 1,600+ modules. WH use: only if WH grows a large DAG estate; highest self-host complexity of the Python options. Not recommended now. | DOC (not recommended now) |
| Argo Workflows | Apache 2.0 (verified) | Kubernetes-native YAML workflows. WH use: none today — WH runs no Kubernetes. Listed per do-not-filter; do not adopt without K8s. | DOC (not applicable) |
| Temporal | MIT (verified) | Durable stateful workflows (code SDKs). WH use (experimental): long-running multi-hour batch jobs that must survive restarts (full-roster extraction). Overkill today; noted. | DOC (experimental) |
| Metaflow | see repo | Low-complexity step-based ML pipelines (Netflix origin). WH use (experimental): versioned batch experiments (e.g., animation retarget variants). | DOC (experimental) |
| GitHub Actions (already used by WH) | n/a (platform) | CI gates in this PR: syntax, property tests, pixelmatch self-test, with pip/npm caching. WH already uses Actions + Netlify deploys from gh-pages. This PR extends, not replaces, that setup. | CI-SIDE |

### 3.4 One-pass build systems (single command builds everything)

| Tool | License | What it does / WH use | Status |
|---|---|---|---|
| Turborepo | see repo (free to use; remote cache free on Vercel plans) | JS/TS monorepo builds: task pipeline in turbo.json, parallel execution, local + remote caching ("never rebuild what hasn't changed"). Reported example: 12-package monorepo CI 8 min -> 45 s with remote cache. WH use: orchestrate the repo's JS packages (game + creation-suite + moveset-parser) with cached parallel tasks. Ceiling below Nx/Bazel, but on-ramp is one turbo.json. | DOC (adoptable) |
| Nx | see repo | Monorepo builds + code generation + affected-only testing. WH use: if WH wants affected-only test runs (only test what changed) plus generation. Heavier on-ramp than Turborepo. | DOC |
| Bazel | see repo | Fine-grained hermetic builds (Google scale). WH use: only if WH needs hermetic reproducible builds across languages; BUILD-file overhead is steep for this repo size. Not recommended now. | DOC (not recommended now) |
| Pants 2.x | see repo | Rust rewrite, dependency inference, Python-first, hermetic resolves + lockfiles. WH use: the Python-heavy alternative to Bazel if WH's Python pipeline grows. | DOC |
| CMake + Ninja | see repo | Fast native builds (cmake present on this VM). WH use: only if native code (C/C++ tools) enters the pipeline; the game itself is JS/Python. | DOC |

### 3.5 Caching + speed (never redo work)

| Tool | License | What it does / WH use | Status |
|---|---|---|---|
| Hash-keyed asset cache (this PR) | repo license | SHA-256 per file; unchanged -> reused. PROVEN: 0.509 s -> 0.000 s on rerun (§1). This is the WH implementation of the ccache/Turborepo idea for game data. | PROVEN |
| ccache | see repo | C/C++ compiler cache; reported 50-90% rebuild reductions, 85%+ in build-farm cases. WH use: CI-side, only if native builds appear. apt install PENDING (§1). | PENDING |
| sccache | see repo | ccache-compatible + Rust + cloud backends (S3/GCS/Redis/Azure) + distributed compilation. WH use: shared cache across CI + dev machines if native builds appear. | DOC |
| GitHub Actions cache | n/a (platform) | pip + npm caching in the new workflow (actions/setup-python cache: pip, setup-node cache: npm). CI-SIDE, ships in this PR. | CI-SIDE |
| BuildKit | see repo | Docker build caching. WH use: only if WH containerizes builds; not today. | DOC |
| Turborepo/Nx remote cache | see repo | Shared build cache across team + CI. WH use: with Turborepo/Nx adoption (§3.4). | DOC |

### 3.6 Quality automation (verification, not manual checking)

| Tool | License | What it does / WH use | Status |
|---|---|---|---|
| Hypothesis 6.170.9 | see repo | Property-based testing for Python: generates hundreds of inputs per property, shrinks failures to minimal cases. PROVEN: 5 WH invariants pass (§1). WH use: validator invariants + moveset invariants (determinism, null-never-invented, injective button map). | PROVEN |
| fast-check | see repo | Property-based testing for JavaScript (standard since 2017, shrinking, TypeScript support). WH use: the JS mirror of Hypothesis for game/js logic (input parsing, string resolution, damage wiring). Not installed here — next wiring step, same pattern as the Python tests. | DOC (next step) |
| pixelmatch + pngjs | see repo | Pixel-level image diff (Playwright's own comparison engine) + PNG read/write. PROVEN: 0.00% self, 10.88% a1-vs-a2 (§1). WH use: visual regression for menu/select/fight frames (baseline -> current -> diff.png, threshold 3%). | PROVEN |
| Playwright Test | see repo | Browser automation + toHaveScreenshot visual assertions (pixelmatch under the hood), threshold tuning, mask option for dynamic regions, Docker-pinned baselines for CI determinism. WH use: full visual-gate upgrade from the compare.js CLI (screenshot capture + compare in one framework). WebGL gotcha: capture immediately after render or preserveDrawingBuffer:true in TEST builds only. | DOC (upgrade path) |
| Jest / Vitest / pytest | see repo | Unit/integration test runners (JS/Python). WH use: WH already has game-unit-tests + batch-strings.test.mjs; this PR's property tests extend that gate, not replace it. | DOC (existing gate) |
| Fuzzing (Hypothesis/HypoFuzz, fast-check) | see repo | Coverage-guided fuzzing from the same property decorators. WH use (experimental): fuzz move parsers + input handlers with generated edge cases (empty strings, surrogates, deep nesting) to find crashers before users do. | DOC (experimental) |

### 3.7 Game-specific automation (adapted patterns)

| Pattern | Source | WH adaptation | Status |
|---|---|---|---|
| Godot headless CI (xvfb-run + --run-tests + --quit-on-finish, Mesa Vulkan drivers, matrix over render drivers) | Godot community CI docs (source-read) | WH is Three.js/web, not Godot — but the PATTERN ports: headless run + virtual display + matrix over renderers + coverage-gated exit codes. The new WH workflow is the web-shaped version of this. | DOC (pattern ported) |
| Godot multi-platform build matrix (linux/windows/macos/web via one workflow, artifacts per platform) | Godot community CI docs (source-read) | WH ships one web build (Netlify from gh-pages). Matrix idea ports to: one workflow, parallel jobs (syntax / property / visual), artifacts (reports + diffs). | DOC (pattern ported) |
| Unreal Automation Tool concepts | industry knowledge | Build/test automation as a first-class tool, not an afterthought. WH adaptation: tools/wh-onepass IS WH's automation tool; keep it maintained like a product, not a scratch script. | DOC (concept) |
| Unity Cloud Build concepts | industry knowledge | Every push builds + deploys a playable build automatically. WH already does this via Netlify auto-deploy from gh-pages; the gap is the full main->gh-pages sync (owed, parent lane), not the concept. | DOC (existing) |

### 3.8 University + experimental (do-not-filter: pulled, use found)

| Project / idea | Source | WH use (including experimental) | Status |
|---|---|---|---|
| NeRF + 3D Gaussian Splatting pipelines for game engines (SIGGRAPH course, Mirocha) | SIGGRAPH History Archives (source-read) | Near-production pipelines for capturing real objects/locations into Unity/Unreal from photos/video, codeless or minimally-coded. WH experimental use: 3DGS environment/asset capture for arenas + props as an alternative to hand-built geometry — aligns with "kill the blocky prototype geometry" arena law. No implementation yet; research-grade, not a claim. | DOC (experimental) |
| MIT faster-graphics research (efficient motion blur, SIGGRAPH papers) | MIT CSAIL via press (source-read) | Cheaper blur computation for games/film. WH experimental use: post-process motion blur at lower cost IF a blur pass is ever added; no current use. Listed per do-not-filter. | DOC (experimental) |
| SIGGRAPH 2026 real-time rendering (ReSTIR, MegaLights, scalable hardware-conscious pipelines) | SIGGRAPH 2026 (source-read) | Direction of travel: scalable fidelity across hardware generations + generative AI disruption. WH use: principle only — build WH's renderer scaling (quality tiers) so phone + desktop both hold frame rate. No code pulled. | DOC (principle) |
| ISTA deformable-surface texturing (cheap "allowed feature" preservation) | ACM Transactions on Graphics via press (source-read) | Cheaper realistic deformation for cloth/soft bodies. WH experimental use: cape/cloth deformation quality at lower cost — relevant to the Cape Jones cape-tearing work (mesh + weights, sibling lane). Research-grade. | DOC (experimental) |
| CMU robust planar maps for 3D vectorization (SIGGRAPH 2026 Best Paper) | SIGGRAPH 2026 (source-read) | Orders-of-magnitude faster 3D-scene-to-vector conversion. WH experimental use: vector-style UI/menu art generation from 3D scenes. Research-grade. | DOC (experimental) |

## 4. GPU: what is proven, what is ready, what the parent must run

- PROVEN: Kaggle notebook GPU itself (parent browser task 2026-10-24:
  2x Tesla T4, 15 GB each, driver 580.178.04, CUDA 13.0, ~30 hrs/week).
- READY (this PR): `tools/wh-onepass/kaggle-gpu-batch.py` — cuDF GPU path
  + stdlib CPU fallback. CPU fallback PROVEN on this VM (5,648 rows,
  0.003 s, totals match the grounding scan). GPU path NOT run anywhere yet.
- PARENT BROWSER DELEGATION (subagent cannot do this): open the Kaggle
  notebook with GPU T4 x2 enabled, upload `kaggle-gpu-batch.py` + the
  t7-all JSONs (or paste the file into a cell), `pip install cudf-cu12`,
  run it, and record the printed cuDF-GPU elapsed_sec + `nvidia-smi`
  output. Until that happens, no GPU speedup number is claimed for WH.
- Close the Kaggle session when idle: quota counts while open.

## 5. CI wiring (ships in this PR)

`.github/workflows/wh-speed-quality.yml`: on pull_request + manual dispatch.
Jobs: syntax gates (py_compile + node --check), Hypothesis property tests,
pixelmatch self-test (two identical generated 1x1 PNGs -> 0.00%, exit 0),
with pip + npm caching. Deliberate scope: the full 5,648-move batch run is
NOT in CI because that dataset lives in workspace, not in the repo. CI
proves the TOOLS; local/Kaggle runs prove the DATA. Conflating the two
would make CI depend on data it does not have.

## 6. Environment findings (affect all speed work on this VM)

- /tmp is a 512 MB tmpfs, 100% full at session start. pip, npm, and any
  tool that stages in /tmp fails with "No space left on device" until
  TMPDIR is pointed at workspace (23 GB free on /home/hatch). Fix used:
  TMPDIR=~/workspace/.tmp-pip for pip. Never stage pulls in /tmp.
- pip is PEP 668 externally-managed: installs need --break-system-packages
  (with --user) or a venv. Used --user + --break-system-packages.
- This VM's system pandas is broken against its numpy (binary
  incompatibility: "numpy.dtype size changed"). The Kaggle script's CPU
  fallback is therefore stdlib-only by design, not by preference. Any
  pipeline that hard-requires pandas breaks on this box.
- 2 CPUs, 7.7 GB RAM. Parallel claims must be measured here, not assumed:
  §1 shows parallel losing on small JSONs on exactly this hardware.
- sudo works (uid 0). apt package lists were stale (ccache/parallel
  "unable to locate"); apt-get update was still running at report time.
- No `blender` binary on PATH (per sibling lane); Blender-dependent steps
  belong on Kaggle or CI, not this VM.

## 7. Complaint + log map (how this lane touches the full list)

This lane is speed/quality/GPU/automation/one-pass. It does NOT claim
sibling lanes' fixes. Map, honestly:
- "Too slow AND too bad quality" (2026-10-24 19:31) -> THIS LANE: one-pass
  batch + hash cache + property gates + visual gates, measured in §1.
- "Slow hand-tooling back-and-forth" (19:29) -> THIS LANE: one command
  validates 5,648 moves; cached rerun is 0.000 s; CI gates run on every PR.
- "Use the GPU for everything" (19:18-19:22) -> THIS LANE (READY) +
  PARENT DELEGATION (§4) for the actual Kaggle run. GPU setup is proven;
  GPU jobs are not yet run — that distinction is kept everywhere.
- "Do not filter pulls" (19:31) -> THIS LANE: §3 includes niche,
  academic, and not-recommended items with experimental uses, not just
  the top tools.
- Wrong moves / wrong animations / strings / grapples / joystick / menu /
  fight-load / UI popups / proprietary names / music -> SIBLING LANES
  (batch-strings PR #1024 merged; grapple, moveset, music, UI agents
  running). This lane's gates (validator + property tests + visual
  compare) are built to CATCH those classes of bug automatically, not to
  fix each instance by hand.
- Logged items picked up from MEMORY.md during this session (not fixed
  by this lane, noted so they are not lost): Cape Jones theme song =
  "Ghost Surf Rock" by Loyalty Freak (main track if Cape Jones gets an
  arena, rotating tracks around it; vibe: surf + spooky + witchy + batty
  + Halloween); REMOVE tap-for-audio (audio on/off in SETTINGS toggle,
  not a tap unlock; Tekken + MDickey Wrestling Empire as references);
  MOBILE + USER FRIENDLY (phone-first, no dumb friction). Audio-engine
  work should use the settings toggle, not a tap unlock.

## 8. Honest gaps + next steps (in order)

1. Run the Kaggle GPU job (§4, parent browser delegation) and record
   real cuDF timings — converts GPU from READY to PROVEN.
2. Resolve the apt install (ccache/parallel) or confirm CI-side-only.
3. Wire fast-check (JS property tests) mirroring the Python properties,
   for game/js input/string logic.
4. Upgrade Playwright from the compare.js CLI to full screenshot gates
   (menu, select, fight frame-30) once a browser runner exists in CI.
5. Adopt Turborepo or Nx ONLY if the repo's JS packages grow past what
   one workflow + one script handle cleanly — not before.
6. Revisit Ray/Dask/Prefect/Kestra ONLY when a WH pipeline outgrows
   script scale (multi-step, scheduled, retry-dependent). Today they
   are documented upgrade paths, and adopting them now would be
   slower, not faster.
