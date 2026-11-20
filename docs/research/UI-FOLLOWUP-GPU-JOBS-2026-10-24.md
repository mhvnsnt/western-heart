# UI follow-up GPU jobs — runbook for the coordinator browser lane (2026-10-24)

## Jobs (scripts + inputs are in this PR)

Script: `tools/gpu/ui-followup-gpu-jobs.py` (stdlib + PIL + Playwright).
It prints a JSON report to stdout (authoritative) and best-effort
writes `report.json` next to it. Every run records nvidia-smi +
torch.cuda proof (or their honest absence), input sizes, outputs, and
wall time per step. Speedup is NEVER claimed by the script: compare a
run's `total_wall_s` against a CPU-baseline run's `total_wall_s` for
the same inputs.

### Job A — visual regression (Playwright + pixelmatch)

```sh
git clone https://github.com/mhvnsnt/western-heart.git wh && cd wh
# baseline captures (first run on the coordinator host):
python3 tools/gpu/ui-followup-gpu-jobs.py regression --repo . --out out/ui-reg-base
# after any UI change, with pixelmatch diff vs the baseline:
python3 tools/gpu/ui-followup-gpu-jobs.py regression --repo . --out out/ui-reg --baseline out/ui-reg-base
```

Screens (12): `screen-online`, `screen-collection`, `screen-daily`,
`screen-howto`, `screen-movelist`, `screen-modewin`,
`screen-reincarnate`, `screen-menu`, `screen-select`, `screen-result`,
`screen-stage`, `screen-vssetup` — each at phone portrait 390x844 and
landscape 844x390 (24 captures). Sections are activated by class:
this is a markup + CSS render check, NOT a playthrough. Live phone
playtesting stays with the coordinator's browser lane (see the
decision doc's playtest list). If pixelmatch is absent, captures are
recorded as the baseline — no fake diff is ever produced.

### Job B — T3 UI assets (contact sheet + phone crops + optional img2img)

```sh
python3 tools/gpu/ui-followup-gpu-jobs.py t3-assets --repo . --out out/t3-ui
# img2img only when a model is actually present on the host:
python3 tools/gpu/ui-followup-gpu-jobs.py t3-assets --repo . --out out/t3-ui --img2img
```

Inputs: `game/data/t3-ui-art.json` (11 TIM+PNG pairs, 150,367 total
preview bytes). Outputs: `t3-ui-contact-sheet.png` (1230x710 at the
measured baseline) + 11 phone-width (390px) crops. Without torch +
diffusers, img2img is recorded as skipped — the sheet + crops are the
deliverable, and generated art ships ONLY after an owner eye-check of
the sheet. Raw T3 pixels never ship.

### Select renders — GATED (Lane H spec, PR #1070)

T8-select-framed renders (P1-left red wash / P2-right blue wash, idle
stance, front + 3/4, 1080x2400 stage + square face-card crop) are
DIAGNOSTIC ONLY until the model's texture gate passes + owner
eye-check. Until then both select slots stay on the existing "model
coming" placeholder per the TEXTURE ELIMINATION law. Do not ship
select renders from this job. Model status for planning: Yoshimitsu
GLB BLOCKED (107 external .tga textures missing from the archive —
no live GLB until the author's CommonTexture folder is recovered via
TekkenMods/community with source recorded); Asuka GLB pending GPU run
(textures present: 30 .vtf + 17 .vmt; VTF→PNG conversion + Blender
Source Tools import are GPU-job steps; attire is the AsukaBikini
variant — it must NOT become a default attire by silence; owner
eye-check + attire decision required).

## Hosts

Primary: Kaggle T4 x2 notebook
(https://www.kaggle.com/code/marsfmmg/notebook2ff3176461/edit).
Backup/overflow: Colab — switch, never stop; the session stays open
and jobs queue continuously. Sign-ins via GitHub/Google tap sign-in
only (GitHub mhvnsnt, Google fmmg.mars@gmail.com); never solicit
credentials.

## Measured local baselines (this VM, CPU — read before comparing)

| Job | Local result | Wall time | Notes |
|---|---|---|---|
| Regression | 0 shots; browser launch failed on BOTH Playwright channels (headless shell + full Chromium crash on launch in this VM) | 1.414 s total (step 1.412 s) | Environment-limited baseline, NOT a screenshot baseline. GPU proof on this host: no nvidia-smi, no torch, cuda false. The Kaggle/Colab run is the first real capture run; compare ITS wall time against a same-host CPU run, not against 1.414 s. |
| T3 assets (in-memory, real inputs) | 11 assets decoded + 1230x710 sheet composed | compose 0.109 s; API-fetch-inclusive 12.211 s | The 12.101 s decode figure is API round-trip time (11 GitHub API fetches), NOT compute — it is network-bound and must not be compared against a cloned-repo run. The comparable CPU figure is compose 0.109 s + local disk reads. Sheet bytes were composed in memory; no file was saved (see sandbox note). |

## GPU times to record (coordinator lane fills these in — none claimed yet)

| Job | Host | nvidia-smi | torch.cuda | Inputs | Outputs | Wall time | CPU-baseline wall time | Speedup (measured) |
|---|---|---|---|---|---|---|---|---|
| Regression | (Kaggle/Colab) | | | 12 screens x 2 viewports | 24 captures (+ diffs) | | | |
| T3 assets | (Kaggle/Colab) | | | 11 pairs, 150,367 bytes | sheet + 11 crops (+ img2img if model present) | | | |
| Select renders (gated) | (Kaggle/Colab) | | | per-gate models only | diagnostic only | | | |

## Sandbox notes (this VM — do not mistake for script bugs)

- Python file writes are blocked in this VM's exec sandbox
  (observed from ~01:56 CDT: `open(..., "w")` raises
  PermissionError, or silently yields 0-byte files, while shell
  redirects and pipes work). The script therefore prints the report
  to stdout FIRST and treats the file write as best-effort. On
  Kaggle/Colab (normal Python) both work.
- Chromium cannot launch in this VM (both Playwright builds crash).
  That is why the local regression baseline has 0 shots. It is not a
  script defect: the script falls back across both channels and
  still emits a report with the launch error recorded.
- Sparse-checkout promisor fetch failed for
  `teardown/tekken3/ui/` blobs in this VM (`index-pack failed`),
  while the same files read fine via the GitHub API. The Kaggle lane
  clones the full repo, so it is unaffected; this VM's T3 baseline
  used in-memory API inputs instead.
