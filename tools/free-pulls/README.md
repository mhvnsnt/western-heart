# Free pulls for Western Heart — open source, experimental, industry-standard, free APIs, free GPU

One-pass pull kit: every script here was verified by a real call or a real
run on 2026-10-24/25. Nothing in this directory needs a key to read, and
nothing here prints or embeds a credential. Anything that needs sign-in is
marked, with the exact step, and is never faked as working.

## What is here

- `apis/` — working clients for free APIs, each verified live:
  - `polyhaven.py` — Poly Haven, CC0 textures/HDRIs/models. Correct host
    is api.polyhaven.com (api.polyhaven.org returned HTTP 522). No auth.
  - `ambientcg.py` — AmbientCG v3 API, CC0 materials. No auth.
  - `google_fonts.py` — Google Fonts CSS endpoint, no key. Writes woff2
    plus a CSS file. Note: plain UA returns TTF, browser UA returns WOFF2;
    Inter/Oswald are variable fonts (one file per family).
  - `huggingface.py` — Hugging Face metadata search (models/datasets).
    Metadata only. No weights are downloaded by any script here.
  - `sketchfab.py` — Sketchfab search works without auth, but download
    returns HTTP 401 without a token. The script stops cleanly (exit 2)
    and never prints a token.
  - `fma.py` — Free Music Archive API is DEAD (HTTP 404; FMA's own
    developer page says the API had to shut down). The script probes the
    dead endpoint and prints curated candidate metadata only. No audio
    is pulled from FMA by any script here.
  - `opengameart.py` — OpenGameArt has NO JSON API (the format=json
    URL returns the HTML search page). Records here are manually
    curated from detail pages, labeled as such.
  - `kaggle.py` — Kaggle is auth-only. The script defaults to check-only
    (verifies kaggle.json exists at mode 600 without reading it). Live
    calls need the official kaggle CLI plus that auth file.
  - `catalog-apis.md` — full per-API endpoint, license, limits, auth,
    WH use, and verification log.
  - `samples-manifest.json` — exact byte sizes of the proof samples
    pulled during verification (workspace copies; see binary policy).
- `gpu/` — free GPU options plus the runnable GPU job queue:
  - `kaggle_wh_batch.py` — Kaggle notebook job (texture downscale/convert
    + GLB size report). Prints nvidia-smi + torch.cuda first, exits 2
    loudly with no CUDA device. CPU self-test only via WH_CPU_SELFTEST=1.
  - `colab_wh_asset_optimize.py` — Colab backup/overflow job (WebP
    optimize + GLB report + one-click zip). Same GPU gate. Colab VM
    storage does not persist: download the zip immediately.
  - `hf_space_app.py` — Hugging Face ZeroGPU demo sketch. Demo-only:
    free signed-in quota is about 3.5 min/day, so this is NOT a batch lane.
  - `webgpu_demo.html` — dependency-free WebGPU compute demo for the
    game itself (runs on the player's own device GPU, with a fallback
    message when WebGPU is unavailable).
  - `catalog-gpu-assets.md` — per-GPU free tier, limits, and what breaks
    when quota runs out. Kaggle 2x T4 ~30 hrs/week is primary; Colab
    free is backup; ZeroGPU is demo-only.
  - `assets-manifest.json` — CC0 textures + HDRI + OFL fonts pulled
    during verification (re-pullable with the scripts in `apis/`).
  - `gpu-queue/` — the ordered GPU job queue, ready for the browser
    lane to execute (see below). Run-guides, failover order, and a
    results template. NO queue job has run yet: a job counts as run
    only when its output plus verbatim nvidia-smi proof exist.
- `tools/` — partial delivery from the tools lane (honest scope note
  below): `wh_audio_loudnorm.sh` (ffmpeg loudnorm to -14 LUFS +
  WAV to Opus, tested on a generated tone) and `wh_glb_audit.py`
  (GLB audit). Remaining tools-lane items were NOT delivered and are
  listed under Scope gaps, not faked.
- `assets/fonts/` — Bebas Neue 400, Inter variable, Oswald variable
  (woff2, OFL) plus `fonts.css`, pulled via `apis/google_fonts.py`.
  Small enough to vendor (about 84 KB total). Game CSS can reference
  these directly when the UI lane wires them in.
- `MEASURED-OPTIMIZATION.md` — fresh gltfpack proof from this session
  (main stance GLB 128,296 -> 53,828 bytes, -58%, bone names kept)
  plus prior-lane figures cited, not re-run.

## Binary policy

Large binaries are NOT vendored in this directory. Textures, HDRIs, and
model samples are re-pulled on demand with the scripts above (one
command each; manifests record exact URLs, sizes, and licenses). The
proof samples pulled during verification live in the agent workspace
and are reproducible with those same commands. Fonts are the exception:
they are tiny and directly game-usable, so they are vendored under
`assets/fonts/`.

## One-pass runner

- `run-free-pulls.sh --check` — no network. Syntax-checks every script
  and validates every JSON file. This is the safe CI-style gate.
- `run-free-pulls.sh --pull` — small live list/search calls against the
  no-auth APIs (Poly Haven, AmbientCG, Hugging Face, Sketchfab search,
  Google Fonts CSS fetch). No downloads except the font files, which
  land in a local out dir, never over sources. Auth-gated and dead
  endpoints (Kaggle, FMA) run their honest check/probe paths only.

## GPU job queue (browser lane owns execution)

Order, from `gpu/gpu-queue/README-job-queue.md`:

1. Job A — Nosferatu cut into 25 tracks. Script already merged at
   `tools/music/kaggle-cut-tracks.py` (PR #1030, merged). The browser
   lane runs it in the Kaggle notebook, downloads the 25 mp3s plus
   manifest plus GPU-VERIFICATION.txt, and lands the mp3s in
   `game/assets/music/`. Live main already carries the 44-track music
   library (verified 2026-10-24: 44 tracks, Nosferatu entries present),
   so no code change is needed once the mp3s land. The 1980s VHS
   synth score is NOT automatically public domain: do not label it PD.
2. Job B — UniRig auto-rigging (Cape Jones + Tripo models). Driver
   script verified present and paste-into-Kaggle ready. Known gaps are
   in its run-guide (upstream org-name mismatch to check on clone
   failure, 15 GB T4 skin VRAM risk, flash_attn install risk, Cape
   input OBJ source to confirm, render is best-effort only).
3. Job C — Real-ESRGAN texture upscale. Two skeletons exist (notebook
   cells + shell photo/anime split); use the cells as the run sheet
   and the shell split as the batch rule, never both on one input.
   Neither skeleton has a GPU gate: capture nvidia-smi + torch CUDA
   manually, sort inputs first, eye-check one output per batch.
4. Job D — gltfpack batch. The tool is CPU-runnable; its GPU value is
   batch parallelism only. Never report its outputs as GPU-optimised
   in the compute sense. Rules: `-kn` always, never `-c` without a
   MeshoptDecoder, never overwrite sources, no fighter simplification
   without an owner eye-check.
5. Job E — Pre-render character cards + stage previews. New script
   `gpu/gpu-queue/job-e-prerender.py` (Cycles CUDA first, Cycles CPU
   fallback stamped, never reported as GPU; EEVEE deliberately not
   attempted headless). First notebook run must be ONE small GLB as a
   smoke test before batching.

Failover order (from `gpu/gpu-queue/gpu-failover.md`): Kaggle 2x T4,
then Colab free, then WebGPU on-device (game-side only, never a batch
replacement), then CPU fallback stamped as such. Jobs A/B wait for
quota reset rather than running silently on CPU.

## Scope gaps (honest, not hidden)

- No GPU queue job has executed yet. Execution needs a live-browser
  notebook run, which this lane cannot do. The scripts, run-guides,
  failover order, and results template are done; the runs themselves
  are the parent's browser delegation.
- Tools lane partial: the Blender pipeline script, WASM integration
  sketch, Stable Diffusion Kaggle skeleton, Tripo/Meshy client
  skeletons, Wwise/FMOD tier facts, and university/experimental repo
  picks from that lane's brief were NOT delivered. They are not in
  this PR and are not claimed anywhere in it. A follow-up PR can add
  them when that lane reports.
- Ghost Surf Rock (Cape Jones theme) is NOT in this PR: it belongs to
  the Cape theme lane. Live main's music library currently has zero
  Ghost Surf Rock mentions (verified 2026-10-24).
- FMA has no working API and OpenGameArt has no JSON API. Both are
  documented as such instead of being papered over with scraped data.
