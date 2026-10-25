# T8 SFM GPU job — coordinator browser delegation (2026-10-24)

**Do not run this on the VM and call it done.** The VM has no GPU
(`nvidia-smi` absent, `torch` absent), no Blender binary, no `7z`,
and no `unrar`. The conversion runs on GPU in the coordinator's
browser lane. This note is the exact delegation.

## Where

- Primary: Kaggle T4 x2 notebook:
  `https://www.kaggle.com/code/marsfmmg/notebook2ff3176461/edit`
  (Kaggle session stays open; jobs queue continuously.)
- Backup / overflow: Colab, ONLY when Kaggle quota runs low — switch,
  never stop.

## Steps (coordinator, in order)

1. Open the Kaggle notebook above. Upload
   `tools/gpu-jobs/t8-sfm-gpu-job.py` from this PR (or paste it into
   a notebook cell — the file is the canonical copy).
2. Cell 0 — install tools, then confirm:
   `apt-get update -qq && apt-get install -y -qq p7zip-full unrar`
   plus Blender 4.0+ for the notebook image (apt if the image
   provides it, otherwise the official Blender tarball), then
   `blender --version` and `nvidia-smi`. If `nvidia-smi` shows no
   GPU, STOP — that run cannot count as a GPU run.
3. Run: `python3 t8-sfm-gpu-job.py --out ./t8-sfm-out`
4. Asuka Blender Source Tools step (manual, in-notebook): import
   the Asuka MDL into Blender with Blender Source Tools, save the
   result, then re-run with
   `python3 t8-sfm-gpu-job.py --out ./t8-sfm-out --asuka-blend <file>.blend`.
   Do NOT guess an addon download URL in the script — install the
   addon through the notebook/Blender UI from its official source
   and record the version used in the run report.
5. Yoshimitsu textures: the `.blend` references 107 distinct
   external `.tga` basenames (T_CH_cml_* + malebody hand sets) and
   packs none of them. The job will report the texture gate as
   FAIL-MISSING unless a texture folder is supplied. If the
   coordinator recovers the author's CommonTexture folder (via
   TekkenMods / the modding community — T8 mod stuff is authorized,
   the user owns T8), place it where the job can find it, re-run,
   and RECORD THE SOURCE in the report. No source recorded = gate
   stays failed.
6. Collect `t8-sfm-out/t8-sfm-gpu-report.json` (GPU proof, per-stage
   wall times, gate results, GLB paths if gates passed) plus any
   GLB/PNG outputs, and return them to Lane H. Lane H then wires
   ONLY gate-passed, owner-eye-checked models into a roster/attire
   slot via the UI lane.

## Expected outputs (and what counts as done)

- `t8-sfm-gpu-report.json` with `gpu_available: true`,
  `nvidia-smi` device string, `torch.cuda` device/count, per-stage
  seconds, and measured speedups (paired CPU/GPU numbers only).
- Yoshimitsu: Blender dump JSON (objects, armature bones,
  materials, image paths), EEVEE-GPU diagnostic frames, and — ONLY
  if the texture gate passes — a GLB.
- Asuka: VTF→PNG batch inventory, MDL bone dump, and — ONLY if the
  VMT texture gate passes and the Source Tools import ran — a GLB.
- Select renders (workstream 4): T8-select-framed EEVEE-GPU views
  (P1-left red wash / P2-right blue wash, idle stance, front + 3/4,
  1080×2400 stage + square face-card crop) for each gate-passed
  model. Before gate + owner eye-check, renders are diagnostic only.

## Never

- Never present a CPU run as a GPU run, and never claim the user's
  "70x" intent line as a measured speedup. Speedup is computed from
  paired numbers in the report or reported as NOT-YET-MEASURED.
- Never export or ship an untextured GLB as a live model.
- Never write T8 data into T7 files (never into Pantera/king.json).
- Never make the Asuka bikini-variant attire a default by silence —
  the owner decides attire at eye-check.
- Never add new raw commercial archives to the public repo. Note:
  the two source archives already sit on public main
  (`teardown/tekken8/models/`, audit §15 item 14) — that predates
  this lane. The coordinator should consider moving the raw archives
  to the private `mhvnsnt/game-reverse-engineering` repo; this lane
  does not move or delete them unilaterally.

## Owner eye-check (after the GPU run, before any live wire-in)

1. Review GLB loads, rig joint maps, textures present, no broken /
   untextured output.
2. View GPU renders + in-game "model coming" → model proof.
3. Decide Asuka attire; confirm Yoshimitsu texture source.
4. UI lane wires the approved GLB into the roster/attire slot;
   only then does the select slot switch from placeholder to model.
