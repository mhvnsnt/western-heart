# FREE GPU + FREE ASSETS — Western Heart lane catalog

Researched and pulled 2026-10-24/25 (CDT). No keys, no credentials, no
GitHub-connector use, nothing pushed to any repo. All files live in this
folder. Total pulled assets: **7,263,927 bytes (~7.3 MB, under the 50 MB cap)**.

Reading guide: **VERIFIED** = checked against docs/API output during this
task. **UNVERIFIED** = widely reported but not confirmed in the provider's
own current docs by this agent (no sign-in, no live browser). Treat every
UNVERIFIED number as "check at sign-in time" — free tiers change without notice.

---

## 1. GPU options

### 1.1 Kaggle Notebooks — PRIMARY, VERIFIED free (brief-given, not re-verified in-notebook)
- **Free tier:** Free account; GPU/TPU unlock after phone verification (secondary reports).
- **GPU:** GPU T4 x2 (2× Tesla T4, 16 GB each) or P100, chosen in Notebook Settings → Accelerator.
- **Limits (commonly reported, Kaggle's own docs publish NO number — verify in your account settings):** ~30 GPU hours/week; sessions ~12 h (CPU/GPU). Quota is account-visible and floats.
- **What breaks when quota runs out:** Accelerator option greys out / jobs queue; you wait for the weekly reset. Do not burn quota on CPU sessions — see the gate below.
- **How to access:** kaggle.com → New Notebook → Settings → Accelerator → GPU (T4 x2).
- **WH job it runs:** `kaggle_wh_batch.py` — batch texture downscale/convert (≤1024 px, JPEG q=85) + GLB size report (meshes/images/materials/buffers). Prints `nvidia-smi` + `torch.cuda.is_available()` FIRST and exits code 2 with a loud error if no CUDA device is present. CPU logic is testable only with `WH_CPU_SELFTEST=1`, which prints an unmissable banner and records `cpu_selftest: true` in report.json — never use that flag in Kaggle.
- **Tested here (no GPU on this VM):** non-selftest run exits 2 loudly; selftest run on a synthetic 2048×1024 PNG + synthetic GLB produced `test_tex_1k.jpg` (1024×512) and a correct GLB report, then test files were deleted. The Kaggle-side GPU run itself is **NOT tested** (needs a signed-in Kaggle account; this agent cannot sign in).

### 1.2 Google Colab free — BACKUP / OVERFLOW, VERIFIED as "no published quota"
- **Free tier:** Free with a Google account. No card required for the free tier.
- **GPU (Google's own FAQ wording):** GPU/TPU types "vary over time"; usage limits "can vary over time" and "are not published". Free notebooks run "at most 12 hours, depending on availability and your usage patterns". Runtimes time out when idle. Paid users whose compute-unit balance runs out revert to free-tier restrictions.
- **UNVERIFIED (community reports only):** usually a T4 (~16 GB); ~90 min idle timeout; ~12 h session ceiling; fair-use cooldowns of hours–days after heavy use. Do NOT plan a job around these numbers.
- **What breaks when quota/limits hit:** GPU becomes unavailable ("no backend with GPU available"), runtime disconnects, VM disk wiped on session end. There is no free-tier appeal or reservation.
- **How to access:** colab.research.google.com → Runtime → Change runtime type → Hardware accelerator → GPU.
- **WH job it runs:** `colab_wh_asset_optimize.py` — same GPU gate as Kaggle; batch optimize to WebP q=85 (+ JPEG fallback) at ≤1024 px, GLB size report with a >25 MB warning, and a one-click `wh-out.zip`. Download the zip immediately — Colab VM storage does not persist.
- **Tested here:** same as Kaggle — loud exit 2 without CUDA; selftest produced WebP (1,016 bytes) + JPEG from the synthetic PNG and a GLB report. The live Colab GPU run is **NOT tested** (needs sign-in).

### 1.3 Hugging Face ZeroGPU (Spaces) — VERIFIED free, but DEMO-ONLY — not a batch lane
- **Free tier:** Genuinely free for Gradio Spaces. No card for the free tier; over-quota billing exists only if you add prepaid credits (do not, if the goal is strictly free).
- **GPU:** Shared NVIDIA RTX Pro 6000 Blackwell (older docs said A100/H200 — hardware naming has changed over time; current HF docs describe the Blackwell pool). Default size `large` = half GPU, 48 GB; `xlarge` = full GPU, 2× quota burn.
- **Limits (HF docs, current):** daily quota — unauthenticated 2 min, **free signed-in account 3.5 min/day**, PRO 25 min/day, Team/Enterprise higher; resets 24 h after first GPU use. **Charged on declared duration, not actual runtime:** default `@spaces.GPU` reserves 60 s per call, even if the function finishes in seconds, and failed calls can consume the reservation. So a free account gets roughly 3 default calls/day. Shorter declared durations get better queue priority. No `torch.compile` on ZeroGPU. GPU is allocated per decorated call and released on return.
- **Discrepancy flagged honestly:** some secondary write-ups still quote 5 min/day for free accounts (the older figure). This catalog uses the current docs figure (3.5 min) and says to re-check https://huggingface.co/docs/hub/spaces-zerogpu at deploy time. A separate per-day run-count limit (3/day, reported by HF staff in April 2026 forum answers) is **UNVERIFIED** in current docs — do not rely on it either way.
- **Hosting limits:** Gradio Spaces ONLY (Docker/Streamlit cannot use ZeroGPU); free personal accounts max 2 ZeroGPU Spaces (verified email, account >30 days, good standing, per docs summaries).
- **What breaks when quota runs out:** calls are rejected/queued until the 24 h reset; buying credits is the only same-day continuation ($1 per 10 min, per docs).
- **WH job it runs:** `hf_space_app.py` — a minimal Gradio demo ONLY: upload one texture → ≤1024 px JPEG back, plus one trivial torch GPU probe (`sum(arange(1024)*2)`). It is **not** a batch pipeline and must not be used as one. ZeroGPU hardware is chosen in the Space's settings UI, not in code; `requirements.txt` for the Space is `gradio, pillow, torch, spaces`.
- **Tested here:** import + resize works without gradio/torch installed (probe degrades to a plain message); the live ZeroGPU run is **NOT tested** (needs an HF account + Space creation; this agent cannot sign in).

### 1.4 Other free GPU options — honestly classified

| Provider | Genuinely free? | What it actually is | WH verdict |
|---|---|---|---|
| **Modal (Starter)** | YES — recurring credit, not a trial | $30/month free compute credits, per-second serverless billing; T4 ~$0.59/h, A100 40 GB ~$2.78/h (third-party rate summaries; verify on modal.com/pricing). Past the credit, it bills — set a budget cap. No notebook IDE; Python-function based. | Best overflow after Kaggle+Colab for scripted batch jobs. **No script included** — Modal needs an account + API key setup, which this agent cannot do; do not claim a Modal run until one is actually configured. |
| **Paperspace Gradient (Free plan, now under DigitalOcean)** | YES — documented free machine | Free GPU (Quadro M4000, 8 GB) for notebooks in private workspaces, 5 GB storage; free notebooks are public and auto-shut down after at most 6 h; free capacity is subject to availability (often queued at peak times). Old hardware, but a real CUDA device at $0. | Usable third overflow for small jobs. **UNVERIFIED live availability** — not tested here (needs sign-in; DigitalOcean-era pricing pages should be re-checked). |
| **Lightning AI (free plan)** | PARTLY — free tier exists, credit amount unconfirmed | "1 free active Studio (4 h restarts)", 50 GB storage; free Studios become paid after 4 h. Monthly free credit amount could not be confirmed from public summaries. | Possible, but do not budget around it until confirmed in-app. |
| **Replicate** | NO — paid-only | Pay-per-second, no free tier (multiple 2026 pricing summaries agree: "No free tier or trial credits" on the pricing page; one secondary page claiming "free credits for new accounts" contradicts the pricing page and is NOT relied on here). T4 ~$0.81/h. | Do NOT list as free. Useful only as a paid inference API. |
| **RunPod** | NO — paid-only (self-serve) | Pay-as-you-go from ~$0.20/h; no automatic free credit. A $1,000 "Starter credit" is an application-based startup tier, not a signup bonus. | Do NOT list as free. |
| **Lambda** | NO — paid-only | On-demand A100 40 GB ~$1.99/h, H100 from ~$3.29/h, per-minute billing, no free tier found. | Do NOT list as free. |
| **Amazon SageMaker Studio Lab** | CLOSED to new users | Was free T4, 4 h sessions; AWS docs now say "no longer open to new customers". | Dead end for new signups. Listed so nobody wastes time on it. |
| **Hyperscaler trials (GCP/Azure/AWS/Oracle)** | NO — trial credit, GPU-blocked | GCP blocks GPUs during trial; Azure documents GPU SKUs at zero quota for trial subscriptions; AWS free plan omits GPU instances; Oracle Always Free has no GPU. | Do NOT list as free GPU. The dollar headline does not buy GPU minutes. |

### 1.5 WebGPU (player's own device GPU) — VERIFIED concept, demo included
- **What it is:** Not cloud compute at all. WebGPU lets a Three.js game's own page run compute shaders on the player's GPU — no account, no quota, no cost. It is the only "free GPU" in this lane that scales with players instead of with a cloud budget.
- **What it can accelerate in a Three.js game:** particle systems (hit sparks, dust, embers — thousands to millions of particles updated on GPU instead of in JS loops), post-processing passes (bloom, blur, colour grading via compute/render passes), skinning-adjacent vertex work, and image/buffer transforms. It cannot replace cloud batch jobs (texture baking at scale, model training) and it cannot be assumed present: availability depends on the player's browser + device + drivers.
- **What it cannot do / limits:** no guaranteed presence (older browsers/devices lack it); mobile GPUs are weaker and power-constrained; compute work still competes with rendering on the same GPU; a WebGL2 fallback path is mandatory for a shipped game.
- **Demo:** `webgpu_demo.html` — dependency-free, no build step. Open it in a WebGPU browser and click Run: it runs a real WGSL compute shader doing (1) vector-add over 4096 floats, verified element-by-element against CPU expectations, and (2) a 4096-particle gravity + floor-bounce update animated on canvas. If `navigator.gpu` is missing, it prints a plain "WebGPU is NOT available" message and does **not** claim a CPU fallback is GPU compute.
- **Tested here:** JavaScript extracted from the HTML passes `node --check`; WGSL workgroup math checks out (4096 / 64 = 64 workgroups, exact). The actual GPU execution is **NOT tested** on this VM (no browser GPU here) — run the HTML in Chrome/Edge on a real device and confirm the PASS line before reusing the shader pattern.

---

## 2. Free assets pulled (all in `assets/`, manifest in `assets-manifest.json`)

### 2.1 CC0 textures — Poly Haven (https://polyhaven.com)
All Poly Haven assets are CC0 (public domain, no attribution required), downloaded
via the no-key public API (`api.polyhaven.com`). Every file below was verified:
all 10 texture files are 1024×1024, and **11/11 MD5 checksums match the Poly Haven
API values exactly** (10 textures + HDRI). Downloaded sizes match the API's
advertised sizes byte-for-byte. Only Diffuse + Rough maps at 1K JPG were pulled
to stay small — the full PBR sets (Normal, AO, Displacement) are available from
the same Poly Haven pages at 1K–8K when a stage needs them.

| File | Material | Suggested WH use |
|---|---|---|
| `concrete_wall_001_diff_1k.jpg` (79,320 B) + `concrete_wall_001_rough_1k.jpg` (156,479 B) | Concrete | Arena wall / concrete stage surround |
| `wood_floor_deck_diff_1k.jpg` (925,789 B) + `wood_floor_deck_rough_1k.jpg` (658,448 B) | Wood deck | Dojo / wooden stage floor |
| `metal_plate_diff_1k.jpg` (692,234 B) + `metal_plate_rough_1k.jpg` (775,206 B) | Metal plate | Industrial / cage / metal stage trim |
| `rocky_terrain_02_diff_1k.jpg` (843,188 B) + `rocky_terrain_02_rough_1k.jpg` (437,094 B) | Rocky ground | Outdoor rocky stage ground |
| `dry_ground_01_diff_1k.jpg` (604,799 B) + `dry_ground_01_rough_1k.jpg` (336,234 B) | Dry dirt ground | Dry outdoor arena ground |

Source pages: `https://polyhaven.com/a/<slug>` for each slug above. Licence: CC0.

### 2.2 CC0 HDRI — Poly Haven
| File | Size | Suggested WH use |
|---|---|---|
| `studio_small_09_1k.hdr` | 1,615,248 B | Stage lighting test / environment map (Three.js PMREM). 1K is a lighting test only — use 2K+ for any final look. Header verified (`#?RA…` Radiance HDR magic). |

Source: https://polyhaven.com/a/studio_small_09 — licence CC0. Smallest resolution
offered by Poly Haven (1K) was chosen deliberately; the 2K version is 6.3 MB and
the 8K version is 95 MB, so do not "upgrade" this file casually in the web build.

### 2.3 Fonts — Google Fonts (OFL, NOT CC0 — read this)
| File | Licence | Suggested WH use |
|---|---|---|
| `BebasNeue-Regular.ttf` (61,400 B) | SIL OFL 1.1 | Display: fighter names, VS screen, big headings |
| `ChakraPetch-Regular.ttf` (78,488 B) | SIL OFL 1.1 | UI body: HUD, menus, health-bar labels |

Both downloaded from the `google/fonts` repo (raw.githubusercontent.com) and
verified as TrueType (`00 01 00 00` magic). OFL permits commercial use, but it
is **not** CC0/public-domain: keep the licence with the fonts and do not
re-label them CC0. `fonts.css` in this folder has the `@font-face` blocks and
`.wh-display` / `.wh-ui` classes. Note: the brief's first font pick (Rajdhani)
was dropped because its repo filename did not resolve (404 on both encoded and
unencoded variable-font paths); Chakra Petch was substituted — same OFL terms,
same game-UI role — and its URL returned HTTP 200 before download.

### 2.4 Skipped on purpose (licence not CC0 / not clearly free)
- Anything on Sketchfab/Fab without a per-model CC0 check — licences vary per model; skipped rather than guessed.
- FreePBR — "custom" licence, commercial use paid; skipped.
- HDRMaps/OpenHDRI freebies — mixed royalty-free/CC0, not uniformly CC0; skipped in favour of Poly Haven's uniform CC0.
- AmbientCG was researched as a CC0 alternative (2,013 materials, also no account) but no files were pulled from it — Poly Haven alone already covered all five material slots, and pulling duplicates would only have added size.

---

## 3. File inventory (this folder)

| File | What it is | Tested how |
|---|---|---|
| `catalog-gpu-assets.md` (this file) | GPU + asset catalog | — |
| `kaggle_wh_batch.py` | Kaggle GPU batch job (texture + GLB report, hard GPU gate) | Loud exit 2 without CUDA; selftest OK on synthetic PNG+GLB |
| `colab_wh_asset_optimize.py` | Colab overflow job (WebP+JPEG optimize + GLB report, hard GPU gate) | Loud exit 2 without CUDA; selftest OK (WebP+JPEG+zip) |
| `webgpu_demo.html` | Dependency-free WebGPU compute demo (vector-add + particles) | `node --check` OK on extracted JS; GPU execution NOT tested on this VM |
| `hf_space_app.py` | HF ZeroGPU Gradio demo sketch (demo only) | Import + resize OK without gradio/torch; live Space NOT tested |
| `fonts.css` | `@font-face` + utility classes for the two OFL fonts | — |
| `download_assets.py` | Re-runnable downloader for the pulled assets | Textures/HDRI/Bebas verified at download; Chakra entry patched to the working URL (HTTP 200 verified) and downloaded from it |
| `assets-manifest.json` | Machine-readable manifest (file, source, licence, bytes, API MD5, use) | 11/11 MD5 matches |
| `assets/` (13 files, 7,263,927 B) | 10 texture maps + 1 HDRI + 2 fonts | PIL: all textures 1024×1024; HDR magic + TTF magic verified |

## 4. What was NOT verified (honest gaps)
1. No live Kaggle, Colab, or HF GPU run — all three need a signed-in account, and this agent cannot sign in or operate a live browser. The scripts are written for those environments and logic-tested here, but the first real run must be watched and its PASS/output lines confirmed.
2. No live WebGPU execution — this VM has no browser GPU. Open `webgpu_demo.html` on a real device and confirm the vector-add PASS line.
3. Colab free numbers (T4, 90 min idle, 12 h ceiling) and Paperspace live availability are community/doc-summary reports, not first-hand checks — flagged UNVERIFIED above.
4. ZeroGPU quota figure conflict (3.5 vs 5 min/day) — docs figure used, re-check at deploy time.
5. Modal/Paperspace hourly rates are third-party summaries — verify on the provider pricing page before spending credits.
6. No GitHub connector was used and nothing was pushed anywhere, per the brief.

---

## 5. GPU JOB QUEUE (added 2026-10-24, user directive 19:55 CDT)

The runnable queue lives in `gpu-queue/` in this folder — it is additional
to this catalog, not a replacement for it:

- `gpu-queue/README-job-queue.md` — queue order + universal run rules.
- `gpu-queue/job-a-nosferatu-run-guide.md` — cut 25 tracks (script
  `tools/music/kaggle-cut-tracks.py`, PR #1030; workspace copy verified
  at `nosferatu-tracks/kaggle-cut-tracks.py`; input `nosferatu-exact.mp3`
  78 MB verified present at `nosferatu/nosferatu-exact.mp3`).
- `gpu-queue/job-b-unirig-run-guide.md` — UniRig rigging
  (`unirig/kaggle_unirig_notebook.py`, 1,075 lines, verified present;
  GPU gate exits 2 with no CUDA; skin-OOM + upstream-URL gaps flagged).
- `gpu-queue/job-c-realesrgan-run-guide.md` — Real-ESRGAN batch
  (`studio-pipeline/kaggle-jobs/02-realesrgan-batch.py` +
  `audio-middleware-research/texture-upscale.sh`; gap flagged: neither
  has a GPU gate, so nvidia-smi must be captured manually).
- `gpu-queue/job-d-gltfpack-run-guide.md` — gltfpack batch
  (`studio-pipeline/wh-asset-pipeline.sh`; CPU tool by design — GPU
  value is batch parallelism only; tool verified working here:
  162 MB Tripo preview GLB 169,162,708 → 121,950,744 bytes, −28%,
  vs the script header's −54%/−59% on other files — savings vary).
- `gpu-queue/job-e-prerender.py` + `job-e-prerender-run-guide.md` —
  NEW character-card/stage-preview renderer (Cycles GPU first,
  Cycles CPU fallback, EEVEE deliberately not attempted — headless
  EEVEE needs OpenGL/display; Cycles CUDA works headless).
- `gpu-queue/results-template.md` — one filled copy per run
  (GPU proof verbatim, time, before/after sizes, output list, quality
  check, landing, failover used).
- `gpu-queue/gpu-failover.md` — switch order: Kaggle 2×T4 → Colab free
  → WebGPU on-device (game-side only, not a batch replacement) →
  CPU fallback (stamped; jobs A/B wait for quota rather than running
  silently on CPU).

**Queue status: ALL FIVE JOBS NOT RUN.** This agent cannot operate a
live browser or run notebooks; execution belongs to the parent's
browser lane, which must fill in `results-template.md` with real
output + nvidia-smi proof per job. Nothing in `gpu-queue/` claims a
notebook execution.
