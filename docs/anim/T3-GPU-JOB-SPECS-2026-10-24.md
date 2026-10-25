# GPU Job Specs — T3 Verification + Community Pulls — 2026-10-24

Button names: LP1 = Left Punch = Tekken 1, RP2 = Right Punch = Tekken 2,
LK3 = Left Kick = Tekken 3, RK4 = Right Kick = Tekken 4.

## Honest GPU / CPU split (read first)

These specs were PREPARED, not run. This agent cannot operate a live
browser session, so it cannot execute the Kaggle notebook. Nothing in
this document claims a Kaggle run happened, and no number in the two
companion reports comes from a GPU run — every count in them comes from
CPU file reads (GitHub API / raw file parsing) and from the quoted
2026-10-24 motion audit document.

- GPU-ACCELERATABLE (offload): batch clip analysis across all 22 T3
  banks, batch T3-row vs T7-property cross-checking across the roster,
  animation retargeting / format conversion math, render proofs.
  Reason: these are vectorized, embarrassingly parallel numeric jobs
  over thousands of clips / tens of thousands of vertices.
- CPU-BOUND (stays on this VM — do NOT waste GPU quota on it): GitHub
  API fetches, web text-fetch research, JSON verification, PR creation.
  These are I/O-bound; a GPU gives zero benefit. Saying otherwise would
  be pretending CPU work is GPU work, and this document does not do that.
- Execution route: parent browser delegation on the user's Kaggle
  notebook (2x Tesla T4, 15 GB each, ~30 hrs/week remaining at
  2026-10-24):
  https://www.kaggle.com/code/marsfmmg/notebook2ff3176461/edit
  The notebook owner runs the jobs below; this agent prepared the specs
  so that run is copy-paste, not re-research.

## Common setup for every job

- Runtime: Kaggle notebook, GPU accelerator on (T4). One T4 (15 GB) is
  enough for every job below; the second T4 is spare / for parallel
  shards, not a requirement.
- Inputs: upload as a Kaggle dataset, or clone the repo files listed per
  job into the notebook working directory. Inputs are REPO PATHS on
  `mhvnsnt/western-heart` main — no new download, no repack, no T8 data.
- Outputs: write to the notebook output directory with the exact names
  below, then attach the output files to the follow-up verification PR.
  Outputs are JSON + PNG only — no model binaries, no game files.
- Determinism rule (carries over from the verification report): a row
  maps to a move ONLY where a file attaches it. GPU jobs MEASURE clips;
  they do not invent mappings. Any job output that suggests a mapping
  must be checked against the file row before it is used, and anything
  unverified stays UNMAPPED.
- Memory estimates below are planning estimates from the file sizes
  measured 2026-10-24 (row packs ~0.9–3.6 MB each, 4,685 row clips across
  21 packs; reaction packs ~1.7–6.6 MB each), not measured GPU runs.
  If a job OOMs on a T4, shard by bank (one bank per run) before
  requesting more memory — do not silently downsample frames.

## Job 1 — Batch clip analysis, all 22 T3 banks (HIGHEST VALUE)

- Script name (to create in the notebook, or as
  `tools/gpu/t3_batch_clip_analysis.py` in a follow-up PR):
  `t3_batch_clip_analysis.py`
- Purpose: extend the 2026-10-24 motion audit — which covered only the
  king, bryan, jin, heihachi_on_jin and yoshimitsu banks — to the other
  17 bank directories, with the same forward-kinematics measures, so
  every bank gets a hip-Y / limb / foot / root verdict instead of
  "UNVERIFIED FOR MOTION".
- Inputs (repo paths, main):
  - `game/assets/anim/t3/*/rows.pack.json` (21 packs; `heihachi/` has
    none — see Job 1 note)
  - `game/assets/anim/t3/*/skeleton.json` (22 files)
  - `game/assets/anim/t3/*/t3_*.json` action clips (30 per bank)
  - `tools/combat-qa/anim_motion_audit.py` (the audit's own method:
    hip-Y vs bank neutral median, limb extension, foot lift, root
    travel, stance classification) — reuse its thresholds, do not
    invent new ones in the GPU job.
- Method (GPU part): load every row clip's joint tracks into batched
  tensors (rows × frames × joints), run forward kinematics in batch,
  compute per row: hip-Y min/max/mean vs neutral median, start frame
  height, peak height, armL/armR extension at active frame, footL/footR
  lift at active frame, root travel, duration. This is the vectorized
  part that is slow in a per-row CPU loop and fast batched on GPU.
- Outputs:
  - `t3_batch_clip_analysis.json` — one entry per bank row: bank, row,
    frames, hip-Y stats, limb extensions, foot lifts, root travel,
    stance class (standing / crouch / duck-dip / jump / starts-airborne
    / ground, same classes as the audit).
  - `t3_batch_clip_analysis_UNMAPPED_candidates.json` — rows whose
    measured motion contradicts their file label or their bound move's
    declared limb/level/stance (candidates for UNMAPPED, NOT automatic
    rewires — a human / file check must confirm each one).
- GPU memory estimate: 4–8 GB on one T4. Batch by bank if needed; a
  single bank's row pack is at most ~3.6 MB on disk and expands to tens
  of MB as tensors — the full 22-bank batch fits comfortably in 15 GB,
  with headroom for FK intermediates.
- CPU fallback: the same computation runs on CPU, bank by bank, slower.
  GPU is a speed win here, not a capability win — do not claim otherwise.
- Note: `heihachi/` (ownrig) has no `rows.pack.json`, so Job 1 skips it
  for rows and covers only its action clips. Bake its row pack first
  (verification report Finding 1) or it stays rows-UNMAPPED.

## Job 2 — Batch T3-row vs T7-property cross-check, full roster

- Script name: `t3_vs_t7_crosscheck.py`
- Purpose: for every WH fighter move that carries a `t3_row` (or an
  `anim_t3` bank+row), compare the Job 1 measured clip against the
  move's Tekken 7 properties (level, limb, stance, startup) in one
  matrix pass, instead of fighter-by-fighter manual checks.
- Inputs (repo paths, main):
  - `t3_batch_clip_analysis.json` (Job 1 output)
  - Per-fighter moveset JSONs under `game/assets/` (`*_moves.json`,
    with `t3_row` / `t3_source` / `anim_t3` fields) and
    `game/js/fighter.js` clip-choice order (own → notation → anim →
    donor → match → generic) — the job must reproduce that order and
    flag which step each move actually reaches. A move reaching
    donor/match/generic is NOT exact, even if its numbers look close.
  - Tekken 7 truth: `docs/t7t8-reference/frame-data-t7/` mirror and/or
    wavu T7 pages (frame data only — properties, not clips).
- Method (GPU part): build a move × feature matrix (measured hip-Y,
  limb, foot, travel vs declared level/limb/stance/startup) and score
  mismatches in batch. Matrix comparison across the whole roster at
  once is the GPU win; per-move scoring is trivially parallel.
- Outputs:
  - `t3_vs_t7_crosscheck.json` — per move: fighter, input (converted to
    LP1/RP2/LK3/RK4 notation by the parser, never re-guessed), file
    row, clip-choice step, measured vs declared verdict
    (CLEAN / HARD limb / HARD level / HARD stance / HARD
    single-on-chord / HARD string-ender-on-chord / UNMAPPED).
  - `t3_vs_t7_hard_list.md` — the HARD list, grouped by fighter, for
    the fix lane. This list replaces hand-maintained wrong-mapping
    lists; it does not replace the file check.
- GPU memory estimate: 1–2 GB on one T4. The roster matrix (audited
  subset alone is 4,696 pressable moves; full roster is larger but still
  tens of thousands of rows × ~20 features) is small; the job is
  bandwidth-light and fits easily.
- Explicit non-goal: this job does NOT rewire anything. Rewires need a
  verified exact row in-bank plus a file edit + PR, as in the
  verification report §8.

## Job 3 — Throw → receiver pairing verification (all 22 banks)

- Script name: `t3_throw_pair_check.py`
- Purpose: verify, from the decoded tables alone, that every throw's
  thrower clip and victim clip pair correctly — no invented receivers.
- Inputs (repo paths, main):
  - `game/assets/anim/t3/reactions.json` (633 records, 418
    throw-victim slots, 58 close reactions)
  - `game/assets/anim/t3/*/reactions.pack.json` (22 packs, 7,368 slots
    counted 2026-10-24)
  - `game/assets/anim/t3/*/hit_frames.json` (throw rows carry reaction
    values at +0x32 / +0x34)
- Method (GPU part, small): batched lookup of every throw row's victim
  slot across all banks, checking (a) the slot exists in the defender's
  bank or the thrower's bank (the documented fallback), (b) the victim
  clip's duration/stance is compatible with the thrower clip's, (c)
  the forestlaw discrepancy is reproduced or resolved (verification
  report Finding 7: bank entry 6 throws vs coverage 0 throws).
  This job is mostly table lookup; GPU batching helps only marginally —
  it is included for completeness and for the forestlaw check, and its
  small size is stated plainly rather than inflated.
- Outputs:
  - `t3_throw_pair_check.json` — per bank: throw count, paired count,
    unpaired slots (if any), forestlaw discrepancy verdict.
- GPU memory estimate: <1 GB on one T4. If run on CPU the difference is
  negligible — this job is listed as GPU-eligible, not GPU-needing.

## Job 4 — Animation retargeting / format conversion (community clips only)

- Script name: `community_clip_convert.py`
- Purpose (ONLY after a delegated community download lands and passes
  the inspection protocol in the community report §5): convert
  inspected, mapping-bearing community clips (TekkenMovesetExtractor
  exports, `.bin` animation sets) into WH bank format — vertex/bone
  math, resampling to WH frame rate, bone-name mapping to the
  WH-Canonical-22 set.
- Inputs: the inspected community file set (paths supplied at run time
  — NOT in this repo, NOT downloaded by this agent), plus the target
  WH skeleton (`game/assets/anim/t3/<bank>/skeleton.json` for the
  receiving bank).
- Method (GPU part): batched vertex/bone transforms and frame
  resampling across all clips in the set at once; per-clip conversion
  is independent, so the whole set parallelizes cleanly.
- Outputs:
  - Converted clips in WH `wh-anim-pack/1`-compatible JSON, one pack
    per source character, PLUS a `conversion_map.json` that preserves
    the source file's move→animation pairing exactly (source move input
    → source animation reference → WH row/clip). Any move whose pairing
    cannot be preserved exactly is listed UNMAPPED in the map, not
    filled with a nearest clip.
- GPU memory estimate: 4–12 GB on one T4 depending on model size
  (WH character meshes in prior work run to ~50–100k verts in clean
  topology; unclean source meshes are larger — shard by character if
  needed). This is the only job where vertex count, not clip count,
  drives memory.
- Explicit non-goal: this job does NOT run on any file that has not
  passed inspection, does NOT run on T8 files for T7 characters, and
  does NOT run on full-game repacks (none were found; if one appears,
  skip it).

## Job 5 — Render proofs (comparison renders, GPU rendering)

- Script name: `render_proof_batch.py` (renderer: Blender Cycles GPU or
  equivalent, as available in the notebook environment)
- Purpose (ONLY after Jobs 1–2 produce a fix candidate list): render
  side-by-side comparison frames (source clip pose vs WH retargeted
  pose, same frame) for fix candidates, so a human eye-check can confirm
  or reject a rewire before it ships. Renders are proof, not wiring.
- Inputs: Job 1/Job 2 candidate lists + the corresponding WH character
  models + the clips under review.
- Method (GPU part): batched frame rendering across candidates; GPU
  rendering is the standard GPU win here (raster/ray-trace parallelism).
- Outputs:
  - `render_proofs/*.png` — one comparison image per candidate, named
    by fighter + input (LP1/RP2/LK3/RK4 notation) + row.
  - `render_proofs/index.md` — candidate → image → eye-check verdict
    (blank until a human fills it; the job does not auto-approve).
- GPU memory estimate: 8–12 GB on one T4 for typical WH character
  scenes; reduce resolution / sample count before reducing the
  candidate list if memory is tight.
- Explicit non-goal: a render that "looks right" does not override a
  file mismatch. If the file row and the render disagree, the file wins
  and the candidate stays UNMAPPED pending a file-level fix.

## What stays on CPU (do not put on Kaggle)

- GitHub API reads/writes, branch + PR creation (this PR).
- Web text-fetch research (TekkenMods pages, GitHub repo listings,
  guides).
- JSON verification, row counting, coverage checks (the counts in the
  companion reports).
- Any step whose bottleneck is network, API rate limits, or human
  judgment (eye-checks, owner decisions, UNMAPPED calls).

Putting any of those on a T4 would burn the ~30 hrs/week quota for zero
speed gain. The quota is for Jobs 1, 2, 4 and 5.

## Kaggle execution checklist (for the notebook operator)

1. Open https://www.kaggle.com/code/marsfmmg/notebook2ff3176461/edit ,
   confirm GPU accelerator is ON (T4).
2. Upload / attach the repo inputs listed per job (or clone the repo
   files into the notebook).
3. Run Job 1 first (it feeds Job 2). Run Job 3 any time (independent).
   Run Jobs 4–5 only after their prerequisites land (inspected
   community files; fix candidates).
4. Save every output JSON/PNG from the Outputs lists above; attach them
   to the follow-up verification PR with the job name and the bank(s)
   covered. Do not paste GPU logs as proof in place of the output files.
5. If any job's output contradicts a number in the companion reports,
   the job output (with its input file hashes) wins for that number —
   file a correction, do not silently overwrite.
