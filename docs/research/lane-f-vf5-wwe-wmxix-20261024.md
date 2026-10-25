# Lane F — VF5 Dural format + WWE 2K22/2K20 CAW structure + WMXIX verification + GPU pack (2026-10-24)

This PR is additive only: new files, no edits to existing files, no deletions.
The bank `game/data/moveset-library/banks/wmxix.json` is UNEDITED; the
verification product is the overlay `game/data/moveset-library/wmxix-verified.json`.

## 1. VF5 — motion format cracked to record level (real file)
- File: `mot_DUR.bin` (from `mot_DUR.farc`), 8,078,704 bytes.
- Little-endian u32 offset table (10,592 bytes, 2,648 entries, 2,644 in range)
  + 661 records x 4 entries: segA 4 B, segB 116 B, segC 708–87,128 B
  (median 10,496), segD 300–312 B.
- segC = `[u32 track_count][u16 track_ids...]` for 652/661 records; 9 records
  are float-led variants. segB first field parses as big-endian f32
  (0.5000 / 1.5000 vocabulary). segD = u16 index table (150–156 entries).
- Full measured analysis: `docs/research/lane-f-vf5-format-20261024.json`.
- Stance NOT identified: the job outputs a candidate screen only (smallest
  segC + fewest tracks: groups 208, 98, 251, 119, 231/232). Identification
  needs key-stream decode + loop/root-motion measurement (GPU jobs below).
- Zen binding: `bankIdFor('zen')` binds `dural` when the base layer activates;
  interim bank stays T3 Heihachi; sources never mixed in one moveset.
  Twelve's dancing idle is a separate 2D→3D conversion dependency.
- No community VF5 PS3 motion decoder was found by web search; the decode
  path is this lane's own record parser + GPU batch.

## 2. WWE 2K22 / 2K20 — CAW structure (verified sources)
- File: `docs/research/wwe-2k22-caw-structure.json` (moved out of game/ — the canon-names gate scans game/** for source-game names, and this structure doc necessarily names the source game; content byte-identical).
- Sources fetched and cited in-file: Smacktalks charactermapping tutorial
  (bakedfile00.cak → Characters/charactermapping.jsfb via Caketools; attire
  scheme XXX00/XXX10/XXX20/XXX40; record = attire-ID LE + 8-byte main-folder
  hash + 8-byte attire-folder hash; no append tool), Genesis 2K19 suite
  (18 move categories), steam-lane spec packs (#1052, spec-only).
- 2K19 vs 2K20/2K22: .pac + CCT + chunk0.def regen vs CAK folders +
  charactermapping hashes; .pofo (profile) + .moveset (moveset + entrance +
  victory + manager/team/attire) via Data Editor.
- 4 neutral CAW base templates (balanced / power / cruiser / giant) from the
  creation-suite MPFB morph pipeline. NO Mixamo soldier mesh/rig/textures
  anywhere in the chain; no famous names; no real-wrestler likeness.
- 2K20 = same schema with a flagged delta (exact 2K20 baked-file split
  pending an owned-install Caketools run).
- Editor verification (live Node run, this lane): 2K22-structured fixture →
  `listAllMoves` 6 rows (LP1/RP2/LK3/RK4 singles → tekken_striking;
  LP1+LK3 / RP2+RK4 throws → grappling); `swapMove` BLOCKS a limb-mismatched
  swap (LP1 slot rejects RP2 armR, status wrong); `serializeMoveset` +
  `createSavePayload` produce the `game/assets/movesets/caw-neutral-2k22.json`
  payload. The editor does NOT rewrite the opaque slots index — in-game
  slot-index behavior is a loader-verification item for the suite lane.
- Suite-lane boundary: this lane owns structure data + templates; menus are
  the creation-suite fix lane's. No menu code changed here.
- Honest blocker: no owned-install 2K22/2K20 files are reachable from this
  VM (phone-only; Steam remote unreachable). Per-slot numeric IDs inside real
  .moveset files are NOT asserted; active path = Caketools + Data Editor on
  an owned install, raw files to the PRIVATE game-reverse-engineering repo
  only.

## 3. WMXIX — 169-row verification (overlay, not a bank edit)
- File: `game/data/moveset-library/wmxix-verified.json`.
- Bank rows are YANM clip registry labels (codes a000–d107), NOT move names.
  Join by motion CODE from `anim_ref` (canon_id collapses C200/C224 variants).
- Result: 115 WIRED_SHOW (ENTRANCE 43, TAUNT 52, WIN_TAUNT 15, BASIC 5) —
  SHOW slots only (intro/win/taunt), NEVER combat. 54 PROVISIONAL_HIDDEN
  (51 EMotName-blank + 3 series-header rows). 0 WIRED_COMBAT.
- No bank row is a sourced gameplay grapple with a combat input, so none
  graduates to combat. The bank's uniform grapple typing + 26-slot
  eligibility are UNSOURCED and are NOT carried into the verified file.
- Public cross-check (both pages fetched): GameSpot walkthrough + GameFAQs
  Cionyl Hurricane guide document the gameplay SLOT system (Light/Heavy
  Front/Rear Grapple × [N]/[D]/[<]/[>]/[^]/[v]; A=grapple, B=strike,
  [S]=Special) and special names — but give NO ringmotion clip-code mapping,
  so they graduate 0 rows. Gameplay animations live in motion/*.mpc under a
  numeric index (undecoded); menu.mpq's 99 named specials likewise identify
  0 clips. caws.ws preset sets found are SmackDown vs Raw 2006/2007 sets,
  NOT WrestleMania XIX sets — caws.ws is NOT a WMXIX verification source.
- Editor rule: PROVISIONAL rows hidden from editor, suite, and combat; SHOW
  rows offered only in intro/win/taunt slots.

## 4. GPU pack (Kaggle delegation)
- Files: `tools/gpu-jobs/lane-f/` — `vf5_decode_batch.py`,
  `wwe_parse_batch.py`, `suite_morph_batch.py`, `JOB-MANIFEST.md`,
  `CPU-BASELINES.md`.
- Notebook (coordinator browser lane): Kaggle T4 x2 (notebook in manifest);
  Colab = backup/overflow when Kaggle quota runs low.
- CPU baselines measured this lane (local VM has no nvidia-smi, no torch;
  GPU-mode scripts exit 2 with FATAL there — verified, no silent fallback):
  VF5 full job 1.237 s; WWE parse 4.390 s (157 files, 56,269 moves; attire-ID
  checks 3/3); morph grid 1.067 s (1,240 evaluations); editor test 42.0 ms.
- Speedup = CPU wall / Kaggle GPU wall from both JOB-VERIFICATION.txt files
  — pending the coordinator run, never asserted here.

## 5. Parent browser delegations (coordinator lane)
1. Kaggle GPU runs (3 jobs, both modes, verification files) — see manifest.
2. Live play verification when VF5 key decode lands: Dural stance on Zen
   (simulation + measurements first, then phone-portrait play-through).
3. Owned-install runs when files become accessible: 2K22/2K20 Caketools +
   Data Editor dumps; WMXIX .mpc container decode + 91xx sheet mapping.
