# AKI Gen-1 N64 Preview Clips — Lane Report

Workdir: `~/workspace/preview-clips/aki-n64/`
Date: 2026-11-21. Parent: preview-clips orchestrator.

## Phase 1 — Extraction: COMPLETE, 21,498/21,498 anims

Cracked the `.npy` bank format by comparing VPW2 ROM anim 0x27E8
against the wh-jp-clone teardown's `anim_27E8.npy`. Decoder:
`aki_npy.py`, **byte-exact on 37/37 VPW2 clips** (incl. 30 random bank
samples). Frame = 19 BE u32 rotation words + translation blocks
(76 + 4 + 6×3 = 98B). Rotation word →
`[s12(bits31-20), u10(bits19-10), s10(bits9-0)]`.

Banks: `banks/<game>/clips/anim_XXXX.npy` + `manifest.json` +
`extract-report.json` (~124MB total):

| game | anims | failures |
|------|-------|----------|
| nomercy | 5,789 | 0 |
| wm2k | 4,671 | 0 |
| worldtour | 2,598 | 0 |
| revenge | 4,017 | 0 |
| vpw64 | 4,423 | 0 |

No container differences: all five games parse with the same Monero
format (4B header + 98B frames, 19 bones). Only anomaly: WM2K 0x2667
'Sliding attack' had 2 trailing all-zero padding frames; `decode_anim`
truncates trailing zero frames when header duration matches
(dur=24 → 13 frames). Revenge ROM is the "(Unlocked)" hack — parsed
cleanly.

## Phase 2 — Mapping: COMPLETE

Maps: `maps/<game>-map.json` + `<game>-gaps.json` + `build-report.json`.
Move universe: Tier 0b `move_library.json` (9,890 moves) + No Mercy
library ids.

| game | moves | with P2 | NEEDS-P2 | SOLO | P2-UNKNOWN |
|------|-------|---------|----------|------|------------|
| nomercy | 1,395 | 609 | 220 | 405 | 24 |
| wm2k | 665 | 271 | 224 | 89 | 81 |
| revenge | 2,842 | 807 | 836 | 486 | 713 |
| vpw64 | 3,282 | 439 | 428 | 126 | 2,289 |
| worldtour | 1,969 | 127 | 309 | 43 | 1,490 |
| **total** | **10,153** | **2,253** | **2,017** | **1,149** | **4,597** |

P2 rule (validated on VPW2 vs the main lane's vpw2-map.json:
precision 0.981, recall 1.000 — 512/512 TP, 10 FP all unnamed):
(1) +1 label `(P2)` with matching name → accept; (2) +1 `(P1)` →
reject; (3) +1 missing/attacker-referenced → reject; (4) +1 names a
different move or is taunt/stance/entrance → reject; (5) P1 solo kind
→ reject; (6) else accept P1+1. Role-based `recv_anim_file_id` from
Tier 0b pooling takes precedence (50 role-vs-rule conflicts flagged,
role kept). Fix applied late: for unnamed moves the P1 *label's* name
is the match name (recovered VPW64's Double German P2 + 25 more pairs).

No Mercy library ids: **1,175/1,255 matched (93.6%)** — 1,021
label-unique, 105 H3-numbered, 49 label-stripnum. H3 numbering rule
(pool by (cat, name); group by base name; descending P1 fid; first
keeps the name, collisions get bare numbers 2,3,4...) validated
628/628, 0 diffs vs independently-confident matches. Remaining 80
unmatched: 74 have candidate pools recorded in
`maps/nomercy-gaps.json` (bare-numbered families whose numbering order
differs per family — Elbow Drop 2–14, Chop 2–7, Stomp 2–7, etc.;
their anims ARE in the map under move_library ids, so clips exist —
only the library-id key is unresolved); 6 have no candidate pool at
all (EMPTY ×2 placeholders, Grapple Release 2, Grapple Reverse/Switch
2, Guillotine 2, Small Package 2 — menu-only names with no anim).

## Phase 3 — Conversion: IN PROGRESS (full run)

Driver: `convert_batch.py` — imports the FIXED v1.3 converter as a
module, untouched. Pairs via its `convert_pair()` (fitted grapple
offset + shared pair lift + Mixamo REST), singles via `fk_clip()` +
`author_clip()`. One StanceRef per game (stance = first anim:
nomercy 2DD9, wm2k 1609, revenge 0E39, vpw64 1347, worldtour 0B55).

**Deviation from the task brief (report to parent):** the brief said
"use batch mode (pair lift)", but v1.3's `--batch` mode does NOT apply
the pair lift and ignores `--rest` (it builds a Bannon-REST stance).
Only `--pair-convert` delivers pair lift + fitted offset + Mixamo
REST — the mode the main lane used for the proven VPW2 German pair.
This driver is a loop over `convert_pair()` calls, one shared
StanceRef per game. No converter code copied or changed.

Fit calibration: the hand-to-belly metric is only meaningful for
waistlock-family moves; the proven VPW2 German pair scores 0.187 m
with the Mixamo REST (WM2K German: 0.187 m, NM German: 0.223 m), so
the raw 0.15 m G7 bar is NOT the bar for this REST. Flags use 0.30 m
(the G7 waist-centre bar) for waistlock moves only, excluding
fragment variants (Break Up/Release/Repeat/Reversal/Counter — no
lock-up window). Proof set: 2 flags (NM + Revenge Back Body Flip,
0.31/0.35 m — slightly loose lock-up).

Outputs: `clips/<game>/<move_id>__P1.json` (+ `__P2.json`).
Progress: `clips/<game>/convert-progress.json` (checkpointed,
resume-safe; per-pair offset + hand-to-belly + pair lift recorded).

## Phase 4 — Proof sets: COMPLETE, 50/50

`proof-sets.json` — German Suplex (or closest equivalent) + 9 spread
moves per game (strike, dive, front grapple, back grapple, submission,
throw, taunt, Irish whip, finisher). Germans: NM 38AA/38AB
(bone-identical to VPW2 27E8/27E9), WM2000 1E9D/1E9E (bone-identical),
VPW64 1B30/1B31 'Double German Suplex', Revenge 14AF/14B1 'Belly to
Back Flip Suplex (Reversal 1)', WorldTour ECC/ECD 'Fisherman Suplex
(Break Up)'.

- Conversion: 50/50, 0 failed.
- Export (Blender, `export_preview.py`): 50/50, CALIB clean —
  R_bt exact, R_cm max deviation 1e-6, q_clip vs apply() max diff
  0.0396° (worst: mixamorig:LeftHandRing2).
- Assembly: 50/50, **0 contract violations** (52 bones, quaternion
  norms 0.99–1.01, finite bounded Hips tracks).
- Cross-validation: the WM2K German preview is EXACTLY identical to
  the main lane's proven VPW2 German preview (Hips Y ranges match to
  3 decimals); NM German near-identical (small stance difference).

Proof outputs: `intermediates-proof/`, `previews-proof/`,
`jobs-proof.json`.

## Phase 5 — Full conversion + export: COMPLETE, 10,153/10,153

| game | moves | converted | exported | assembled | verified |
|------|-------|-----------|----------|-----------|----------|
| nomercy | 1,395 | 1,395 | 1,395 | 1,395 | 0 violations |
| wm2k | 665 | 665 | 665 | 665 | 0 violations |
| revenge | 2,842 | 2,842 | 2,842 | 2,842 | 0 violations |
| vpw64 | 3,282 | 3,282 | 3,282 | 3,282 | 0 violations |
| worldtour | 1,969 | 1,969 | 1,969 | 1,969 | 0 violations |
| **total** | **10,153** | **10,153** | **10,153** | **10,153** | **0 violations** |

- Conversion: 0 failures across all games. Clip files on disk:
  12,406 (10,153 P1 + 2,253 P2) — exact match to the maps.
- Export (Blender): 0 failures. CALIB clean on all 9 export runs:
  R_bt exact, R_cm max deviation 1e-6, q_clip vs apply() max diff
  0.0396° on every run.
- Assembly: 10,153/10,153. Verification (`verify_previews.py`:
  52 bones, quaternion norms 0.99–1.01, finite Hips `p` within 15 m):
  **0 violations across all 10,153 previews**.
- Fit flags (waistlock-family, > 0.30 m hand-to-belly): 79 total
  (NM 47, WM 27, REV 0, VPW64 3, WT 2), listed in each game's
  `clips/<game>/convert-progress.json` under `fit_flags`. The worst
  numbers (0.97–1.04 m) are all `(Win)` pin-finish fragments, where
  the lock-up window isn't a waistlock at all — the same fragment
  logic as Break Up/Release (the filter just doesn't list 'win');
  genuine full-move flags are 0.31–0.65 m (drop suplexes, double
  underhook suplexes — moderately loose lock-ups, worth a look, not
  broken). The German pairs sit at 0.187–0.223 m, in line with the
  proven VPW2 German (0.187 m).
- Hips `p` sanity: the two longest-travel moves (WM2K Bronco Buster
  ~7 m, Bulldog ~5.2 m) are genuine source root motion (running
  moves), not corruption — the 15 m verifier bound covers them.
- NOT deployed to live (parent deploys). Previews live at
  `previews/<game>/<game>_<move_id>.json`.
- Resilience notes: two runtime restarts SIGTERM'd running jobs
  mid-flight; all stages resumed cleanly from checkpoints (0 corrupt
  files after both restarts). One truncated preview file (Revenge
  Belly to Back Suplex 14B4, from a killed assemble run) was caught
  by the verifier, deleted, and regenerated — final verify clean.
  Revenge's `convert-progress.json` `done` dict undercounts by 29
  (2,813 vs 2,842) because the progress write is every 50 moves and
  the kill landed between writes; the disk count (3,649 clip files)
  is exact and authoritative.
- Disk: workdir total 1.5G (banks 124M, clips 349M, intermediates
  478M, previews 475M, proof 6.6M).

## What's missing + why (honest gaps)

- 80 No Mercy library ids unmatched (74 with candidate pools recorded
  in `maps/nomercy-gaps.json`, 6 with no candidate at all — see
  Phase 2). Their anims are still clipped under move_library ids.
- 2,017 moves NEEDS-P2 (P2 not determinable from labels/roles/rule):
  shipped as P1-only previews; the flag is in the map + gaps files.
- 4,597 P2-UNKNOWN (mostly unnamed early-game moves): shipped as
  P1-only; no invented pairings.
- 0 unextractable anims, 0 container differences, 0 conversion
  failures, 0 export failures.

## Files

- `aki_npy.py` — bank-format decoder (byte-exact on VPW2)
- `extract_bank.py` — ROM → bank extractor
- `build_maps.py` — move → (P1, P2) map builder (incl. H3 NM matcher)
- `convert_batch.py` — v1.3 batch driver
- `banks/<game>/` — 21,498 extracted anims
- `maps/<game>-map.json`, `maps/<game>-gaps.json` — the maps
- `clips/<game>/` — converted converter-clip JSONs
- `previews/<game>/` — assembled preview clips (Phase 5 output)
- `proof-sets.json`, `jobs-proof.json`, `jobs-full-<game>.json`
