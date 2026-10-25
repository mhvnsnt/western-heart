# Pantera Batch 1 — step plans (LP1/RP2-only strings) — 2026-10-24

Button law: LP1 = Left Punch = Tekken 1, RP2 = Right Punch = Tekken 2, LK3 = Left Kick = Tekken 3, RK4 = Right Kick = Tekken 4.

> **Follow-up note (2026-10-25, Batch 1 follow-up PR):** the sections below are the #1096 Stage 1 record.
> The follow-up section ('Batch 1 follow-up (Job 3 / Job 4, 2026-10-25)') records the Job 3 fills (Fill 1
> VERIFIED row 97; Fill 2 SOFT row 49) and the Job 4 adjudications, and supersedes the tallies where stated:
> 73 steps now 28 verified-exact / 2 soft-verified / 7 review / 36 unmapped; 60 plan keys now 14
> verified-last-step / 4 review / 42 unmapped. #1096's dated statements (e.g. 'NOT LANDED') are preserved as
> history with dated updates, not silently rewritten.

## What this is

The engine change in this PR (`game/js/fighter.js` `_attackClipPlan` step-plan branch + `_stepChain`) plus the
`string_step_plans` data in `game/assets/movesets/pantera.json`. A planned string move plays per-STEP rows, never one
row for the whole string. Only a step with status `verified` plays its row. A `review`/`unmapped` step plays NO bank
row — the existing procedural fallback in `_animate` — and is flagged in `_atkPlan.unmapped` with a `[WH-STEP-PLAN]`
console line. Donor, match, and generic tiers are bypassed for planned strings, so a planned string can never
silently donor-fall-back. This is the faster-methods prime candidate (step-based string playback) as REFRAMED by
the batch-research second validation: the per-press (`_pressV2`) path already fires one move per press, so for that
path the plan corrects the LAST step's row selection; the whole-string path (a full notation fired at once by AI /
trials / movelist demo / buffered input) plays as a `_stepChain` of prefix moves through `_fireNotation`.
No blend is added: step-to-step pose continuity is UNPROVEN (end-to-start gaps 0.2-0.9 m+ in the research), and a
blend ships only if play shows a snap.

## Gates (per step candidate, in order)

1. Candidate source: recorded path row (`strings[].t3_rows` full-path, or dest-only for the last step), else the
   prefix move's `t3_row`, else none. Recorded paths are NOT trusted blindly: `2,1`'s recorded path `[203, 220]`
   fails the gates at step 2, so the path is recorded as evidence and the step is UNMAPPED, not wired.
2. HARD gates (fail = `unmapped`): button bitmask (`hit_frames.json` button field == step chord bits, LP1=1, RP2=2) +
   throw flag == 0 + stance (an airborne row fails a standing-context string; airborne PASSES a jumping-context string).
3. SOFT gate (fail = `review`, not played): in-window limb extension peak (FK, npz window = stream active window / 2,
   +/-2 frames). The stream-to-npz decimation is UNCONFIRMED, so this gate never hard-fails a step. For
   jumping-context strings it is WAIVED: the FK extension metric is systematically silent on jumping rows 38/39/40
   (zero limb peaks at threshold), while button + stance pass and the focus Stage 1 resolution (row 38 = Pantera
   jumping `u+1,1`, row 39 = `u/f+1,1`, row 40 = `u/b+1,1`) stands. Play-verify remains the check for those rows.
4. Rejected for ground steps, always: jumping rows 35 and 220. Row 220 is a shared LP1+RP2 chord/jump-family clip
   (byte-identical to row 221, also serves `1+2~t3.king`), not a `2,1` ender. Row 35 is the same failure class for chord enders.
5. Shared-clip note: rows 97 = 110 and 220 = 221 are byte-identical (quats + root_t). FK cannot distinguish shared-clip
   context variants; shared verified rows still need play-verify.

## Canonical step table (31 triage keys, 73 steps: 28 verified-exact, 2 soft-verified, 7 review, 36 unmapped — follow-up 2026-10-25; #1096 record was 27/7/39)

| String | Steps (verified row, else status) | String status |
|---|---|---|
| `1+2,1` | 1+2 = UNMAPPED (no candidate) \| 1 = UNMAPPED (no candidate) | unmapped-all |
| `1,1` | 1 = row 110 \| 1 = UNMAPPED (cand row 584 rejected: button 0 != step bits 1; throw flag 1 (row 584); no in-window peak on ['armL'] in approx npz window [0,2] (peaks {'armL': [83], 'armR': [4, 77, 85], 'legL': [], 'legR': []})) | partial |
| `1,2` | 1 = row 110 \| 2 = UNMAPPED (no candidate) | partial |
| `1,2,1` | 1 = row 110 \| 2 = UNMAPPED (no candidate) \| 1 = UNMAPPED (no candidate) | partial |
| `2,1` | 2 = row 203 \| 1 = UNMAPPED (cand row 220 rejected: button 3 != step bits 1; airborne (y0 0.952 ymax 1.649 vs standingY 0.892)) | partial |
| `FC.1,2` | 1 = row 110 \| 2 = UNMAPPED (no candidate) | partial |
| `WS.2,2` | WS.2 = UNMAPPED (no candidate) \| 2 = UNMAPPED (no candidate) | unmapped-all |
| `b+1+2,1+2` | b+1+2 = UNMAPPED (cand row 279 rejected: throw flag 1 (row 279)) \| 1+2 = UNMAPPED (no candidate) | unmapped-all |
| `b+1+2,2` | b+1+2 = UNMAPPED (cand row 279 rejected: throw flag 1 (row 279)) \| 2 = row 98 | partial |
| `b+1,2` | b+1 = UNMAPPED (no candidate) \| 2 = UNMAPPED (no candidate) | unmapped-all |
| `b+2,1` | b+2 = UNMAPPED (no candidate) \| 1 = UNMAPPED (no candidate) | unmapped-all |
| `b+2,1+2` | b+2 = UNMAPPED (no candidate) \| 1+2 = row 97 VERIFIED (Job 3 exact + full provenance; d+1+2 caveat; also-ran 143 SOFT loses) | partial |
| `d+1+2,2` | d+1+2 = row 97 \| 2 = row 98 | verified-all |
| `d+1+2,2,1` | d+1+2 = row 97 \| 2 = row 98 \| 1 = row 198 | verified-all |
| `d+1+2,2,1,1` | d+1+2 = row 97 \| 2 = row 98 \| 1 = row 198 \| 1 = REVIEW cand row 257 (recorded-dest) | partial |
| `d+1+2,2,1,1,2` | d+1+2 = row 97 \| 2 = row 98 \| 1 = row 198 \| 1 = REVIEW cand row 257 (prefix-move) \| 2 = REVIEW cand row 258 (recorded-dest) | partial |
| `d+1,2` | d+1 = UNMAPPED (no candidate) \| 2 = UNMAPPED (no candidate) | unmapped-all |
| `d/b+1+2,2` | d/b+1+2 = UNMAPPED (cand row 286 rejected: throw flag 1 (row 286)) \| 2 = row 200 | partial |
| `d/f+1,2` | d/f+1 = REVIEW cand row 117 (prefix-move) \| 2 = UNMAPPED (no candidate) | review-only |
| `d/f+2,1` | d/f+2 = row 202 \| 1 = UNMAPPED (no candidate) | partial |
| `f+2,1` | f+2 = UNMAPPED (no candidate) \| 1 = UNMAPPED (no candidate) | unmapped-all |
| `f+2,1,1` | f+2 = UNMAPPED (no candidate) \| 1 = UNMAPPED (no candidate) \| 1 = REVIEW cand row 257 (prefix-move) | review-only |
| `f+2,1,1,2` | f+2 = UNMAPPED (no candidate) \| 1 = UNMAPPED (no candidate) \| 1 = REVIEW cand row 257 (prefix-move) \| 2 = REVIEW cand row 258 (prefix-move) | review-only |
| `f+2,d+1` | f+2 = UNMAPPED (no candidate) \| d+1 = UNMAPPED (no candidate) | unmapped-all |
| `f+2,d+1,2` | f+2 = UNMAPPED (no candidate) \| d+1 = UNMAPPED (no candidate) \| 2 = UNMAPPED (no candidate) | unmapped-all |
| `u+1,1` | u+1 = UNMAPPED (no candidate) \| 1 = row 38 | partial |
| `u+1,2` | u+1 = UNMAPPED (no candidate) \| 2 = row 50 | partial |
| `u/b+1,1` | u/b+1 = row 49 VERIFIED-SOFT (Job 3 4-way SOFT tie, strongest provenance; never exact) \| 1 = row 40 | verified-all (soft first step) |
| `u/b+1,2` | u/b+1 = row 49 VERIFIED-SOFT (Job 3 4-way SOFT tie, strongest provenance; never exact) \| 2 = row 52 | verified-all (soft first step) |
| `u/f+1,1` | u/f+1 = row 36 \| 1 = row 39 | verified-all |
| `u/f+1,2` | u/f+1 = row 36 \| 2 = row 51 | verified-all |

## Plan keys in the moveset (60)

- 31 canonical triage keys (table above).
- 26 twin keys (`~t7.king` / `~t8.king` / `~t3.king` variants sharing a canonical input): same steps as their canonical
  key, except `f+2,1~t3.king`, whose own `t3_row` 198 passes all gates for its last LP1 step and is therefore its
  verified last-step row (its `move_class` is `strike`, so the chain branch does not fire for it — the clip branch does).
- 3 spelling-variant keys (`df+1,2`, `df+2,1`, `ws2,2`): same steps/evidence as `d/f+1,2`, `d/f+2,1`, `WS.2,2`.
- EXCLUDED: `b+1+2,1+2~t7.king` — its `move_class` is `throw`, so a punch-string plan must not govern its clip
  selection; it stays on the existing tiers.
- Last-step status over the 60 plan keys: verified 14, review 4, unmapped 42. The 14 verified-last-step keys are:
  `b+1+2,2` (row 98), `b+2,1+2` (97), `b+2,1+2~t7.king` (97), `b+2,1+2~t7.king.2` (97), `d+1+2,2` (98), `d+1+2,2,1` (198), `d/b+1+2,2` (200), `f+2,1~t3.king` (198), `u+1,1` (38),
  `u+1,2` (50), `u/b+1,1` (40), `u/b+1,2` (52), `u/f+1,1` (39), `u/f+1,2` (51). For the original 11, the verified row equals
  the move's previous own `t3_row` — the visible clip does not change, but it is now plan-guaranteed (donor tier bypassed).
  For the 3 new `b+2,1+2` keys, row 97 is a Job 3 fill (not a previous own row) — the visible last-step clip CHANGES
  (donor jumping row 35 gone; standing chord row 97 plays).
- Last-step review keys (4): `d+1+2,2,1,1` (cand 257), `d+1+2,2,1,1,2` (cand 258), `f+2,1,1` (cand 257), `f+2,1,1,2`
  (cand 258) — limb-peak evidence short (257: armR-dominant FK vs LP1 button; 258: armR peak 1 frame outside the
  approximate window). These rows are NOT played until adjudication + play-verify promote them.
- Flagship: `2,1` — step 1 row 203 verified (RP2, standing, single peak); step 2 UNMAPPED (recorded row 220 fails button
  bitmask 3 != LP1 bits 1 AND airborne for a standing string). All `2,1` twins share the plan, so row 220 no longer
  plays for any `2,1` key. The true LP1-context ender row is still UNMAPPED pending `match_search` candidates or MADE.
- `1,2` boundary (honest): step 1 row 110 verified; step 2 UNMAPPED pending candidates. Its move damage 20 is the
  multi-hit total [5, 15]; last-hit normalisation (15) is NOT applied in this PR because no step is wired for it yet —
  it applies when step 2 lands. `2,1` damage is untouched (Stage 1 damage ruling pending: body 9 vs 15 vs 16).

## Batch 1 follow-up (Job 3 / Job 4, 2026-10-25)

This section supersedes the #1096 tallies where stated. Ingest: GPU jobs 1–6 outputs (2026-10-24, Kaggle
notebook `notebook2ff3176461`, account `marsfmmg`), ingested 2026-10-25 (ingest package
`~/workspace/gpu-jobs-1-6-ingest/` — workspace path, not repo).

### Gap closure before wiring
- Gap 1 (Job 1 row-for-row diff, checklist Step 4): CLOSED. Against current main `462a8475`: all 5 cited banks'
  files byte-identical to the pack snapshot (20/20 file hashes); rebuilt .npz arrays identical for all 14 arrays × 5
  banks (70/70); all 31 cited rows (14 KNOWN + king 97/143/36/47/48/49/584/198/257/220 + 7 orphans
  88/96/154/230/236/248/342) profile-identical (categorical fields exact; max float diff 2.4e-07, float32 rounding
  only). No cited row differs → no fill suspended. Evidence: `~/workspace/batch1-followup/gap1_diff.py`,
  `gap1_diff.json`. (Full 87-bank-file re-check at `462a8475`: see PR body; cited-bank result stands regardless.)
- Gap 2 (re-baseline vs current main pantera.json): CLOSED. Both fill prefix moves are FIELD-IDENTICAL between the
  pack snapshot and current main pantera.json (same sha `63811b920695` at `8607514d` and `462a8475` — pantera.json
  unchanged between those commits): `b+2,1+2` (no t3_row; still plays donor row 35 + still fails the HARD stance gate
  → Fill 1 wireable) and `u/b+1` (t3_row 37; still HARD limb → Fill 2 wireable as SOFT). Context strings `u/b+1,1`
  (row 40) and `u/b+1,2` (row 52) also identical. Main's drift (PR #1048 top-level sections) did not touch these
  entries. Verdicts are a function of (move row, bank profile); both unchanged → verdicts unchanged. No fill suspended.

### Fill 1 (VERIFIED): `b+2,1+2` step 1+2 ← king row 97
- Step: `b+2,1+2` step 2 (1+2, prefix `b+2,1+2`), prior UNMAPPED. Twins `b+2,1+2~t7.king` and `b+2,1+2~t7.king.2` inherit.
- Evidence: Job 3 match_search, king row 97, EXACT level (filed h, played h), stance standing→standing, FULL
  provenance. Also-ran king row 143 SOFT-filed (filed h, played m) loses on exact-level priority (its timing passes
  the 1.55× bar for this target — it is an also-ran on level, not a timing reject).
- Provenance caveat (verbatim): row 97's visible provenance string is `moveset_pantera:d+1+2(2+LP+RP)` — a different
  chord input (d+1+2, not b+2,1+2), matching by button class (LP1+RP2 chord) per the match_search provenance rule.
  Step identity rests on the target key (b+2,1+2) matching the step prefix exactly, not on the provenance input.
- T3 FALLBACK row (PROCEDURAL_AUDIT.md); re-match to T7 King row when extraction lands.
- Damage/startup: NO changes. Move damage 29 already equals last-hit MOD damage (16,29 → last 29). Startup 0.2 vs
  row 97 active-first 10/60 = 0.167 differs by 2 frames, but first step b+2 is unwired, so string-level startup
  semantics for a partially-wired string are unconfirmed — changing startup to the last-step value while the first
  hit has no row would misstate first-hit timing. Revisit when step 1 lands.

### Fill 2 (SOFT, flagged everywhere): `u/b+1,1` + `u/b+1,2` step u/b+1 ← king row 49
- Steps: both strings' step 1 (u/b+1, prefix `u/b+1`), prior UNMAPPED (both share this prefix step). No twins.
- Evidence: Job 3 match_search 4-way SOFT tie — king rows 36/47/48/49, all SOFT-filed (filed h, played m), stance
  jump→jump (correct for this jumping step), all FULL provenance. Row 49 recommended: strongest provenance
  (`u/b+1,1~t3.king.3` — a move with u/b+1 as first step); rows 47/48 cite different directionals (u+1, u/f+1), row 36
  cites u/f+1 and f. Rows 47/48/49 have IDENTICAL motion profiles (the tie is on provenance, not motion); row 36
  differs in dominant arm.
- Flag: steps carry `"soft": true` + `soft_note` ("SOFT: filed h / played m; 4-way tie broken on provenance only;
  not verified-exact. Reverts to UNMAPPED if play-verify fails."); this doc and the test assert the soft set exactly.
  This is NEVER presented as verified-exact. If play-verify fails, the steps revert to UNMAPPED (row 49 does not stay
  as a silent default).
- Rejected prefix-move candidate row 37 (button 3 != step bits 1) is retained in the step's reasons history.
- T3 FALLBACK row; re-match to T7 King row when extraction lands. No damage/startup changes (both strings' damages
  unchanged; last steps 40/52 already verified).

### No other Job 3 fills
The other 43 unmapped/review steps have NO Job 3 candidate under the exact-prefix rule and stay UNMAPPED/REVIEW.
Notably: `1,2` step 2 and `2,1` step 1 gain nothing from Job 3. Rows 35/220 appear in NO Pantera Job 3 pass-all list —
zero triggers.

### Job 4 adjudication (sequence-shape EVIDENCE, never auto-fills)
Correct join only (pantera-only moves, documented BANK_DIR mapping, one row per step): 73 steps — 11 with ≥1 valid
Job 4 candidate, 62 NONE. King row 35 absent (exclusion holds). The raw job4_join.py output is INVALID for Batch 1
(cross-fighter joins); raw outputs preserved for audit only.
- `1,1` step 2 ← row 584: REJECTED. Fails HARD gates (button 0 != LP1 bits 1; throw flag 1; no in-window armL peak).
  Step stays UNMAPPED — a missing clip, not a gate failure on an already-played row (the step plays no bank row).
  Job 2 move `1,1` verdict HARD limb is consistent (different gate, same rejection direction).
- `f+2,1` step 2, `f+2,1,1` step 2, `f+2,1,1,2` step 2 ← row 198: CANDIDATE passing HARD gates (btn 1, throw 0,
  duck-dip stance not airborne, armL peakF 13 ext 0.813, sequence-shaped armL 2 peaks). Row 198 is the move `f+2,1`'s
  current CLEAN row via the notation tier, which #1096's candidate sources (recorded path row, else prefix-move
  t3_row, else none) missed. NOT wired in this PR: a Job 4 join NEVER promotes a step to VERIFIED by itself; needs
  play-verify promotion per the review-promotion rule. Documented as candidate-for-future-wiring.
- Review steps ← row 257 (`d+1+2,2,1,1` step 4; `d+1+2,2,1,1,2` step 4; `f+2,1,1` step 3; `f+2,1,1,2` step 3): row 257
  passes HARD gates but fails the SOFT limb-peak gate (armR-dominant FK vs LP1 button) → stay REVIEW, not promoted.
  (Job 2 'HARD stance' for move `d+1+2,2,1,1` is about that MOVE's current row, not row 257 — do not conflate.)
- Verified steps ← row 198 (`d+1+2,2,1` step 3; `d+1+2,2,1,1` step 3; `d+1+2,2,1,1,2` step 3): NO ACTION. Job 4 confirms
  sequence shape (armL 2 peaks); steps already play row 198 verified.
- `2,1` step 2: row 220 already excluded (join notes + #1096); no change.
- 7 orphans (king 88, 96, 154, 230, 236, 248, 342): no Pantera Job 2 move carries them; no action.

### Tallies after this follow-up
- 73 steps: verified-exact 28 (was 27), soft-verified 2 (was 0), review 7, unmapped 36 (was 39). 28+2+7+36 = 73.
- 60 plan keys, last step: verified 14 (was 11), review 4, unmapped 42 (was 45). 14+4+42 = 60.
- 31 triage keys, last step: verified 11 (was 10), review 4, unmapped 16 (was 17). 11+4+16 = 31.
- Fill 2 wires FIRST steps, not last steps → last-step tallies unchanged by Fill 2. Triage and plan-key tallies are
  reported separately, never merged.

### Follow-up re-audit (CSV worklist, 57 rows)
- `b+2,1+2` + 2 twins: previously donor row 35 (jump clip for a ground move). After Fill 1, their last steps play
  verified row 97 (standing chord); first steps still procedural. 3 CSV rows improve; the 45 no-bank-row rows from
  #1096's re-audit are otherwise unchanged.
- `u/b+1,1` / `u/b+1,2`: NO CSV rows (direct key lookup confirmed) — no CSV-count change for Fill 2.
- Merge order: this follow-up PR lands AFTER #1096 merges; rebase onto main before merging the follow-up. Do NOT
  merge on mergeable:true alone (green + clean + git_merge.py only).

## Damage/startup spot-check (criterion 4, wired scope only)

For the 11 verified-last-step keys, the moves already carry last-step damage/startup — no data change needed:
`d+1+2,2` startup 0.200 = row 98 active-first 12/60, damage 9 = row damage 15 scaled 100/170; `d+1+2,2,1` startup 0.400 =
row 198 active-first 24/60, damage 6 = 10 scaled; `b+1+2,2` startup 0.200 = row 98 12/60; `d/b+1+2,2` startup 0.250 =
row 200 15/60; `u+1,2` / `u/b+1,2` / `u/f+1,2` startup 0.183 = rows 50/52/51 active-first 11/60. Other verified-last-step
keys carry single-hit-scale damage (9/11) consistent with last-step, not totals.

## Re-audit (planned keys only; NOT a play claim)

Baseline (faster-methods CSV, 57 audit rows): donor 42, notation 6, own 5, anim 4; 14 limb mismatches, 14 HARD-flagged;
generic rows 99 (14 strings) and 110 (11) dominate; worst repeats: `2,1` enders on jumping row 220, `1+2` enders on jumping row 35.
After this PR, over the 47 CSV rows whose key is a plan key: 2 rows play a verified row (the canonical `d+1+2,2` /
`d+1+2,2,1` keys — their clips are unchanged); 45 rows play NO bank row (procedural fallback) instead of their previous
donor/notation/own row, including all 4 `2,1` rows (row 220 gone) and the planned chord-ender rows that played row 35.
The other 10 CSV rows are grapple chains (7: ARM_BREAKER / DOUBLE_HEEL_HOLD / PILE_DRIVER / REVERSE_ARM_SLAM /
REVERSE_SPECIAL_STRETCH_BOMB / SLEEPER) and TACKLE chains (3) — separate grapple systems, out of Batch 1 scope, untouched.
Donor picks are therefore 0 for planned strings BY CONSTRUCTION (the plan branch bypasses the donor tier); the 45
no-bank-row strings are the honest UNMAPPED/REVIEW remainder, not fixes. No string in this PR is claimed fixed by
inspection: the play handoff below is the remaining gate.

## Three counting units, reconciled (none is 'the' count)

| Unit | Count | What it counts |
|---|---|---|
| Faster-methods CSV worklist | 57 rows | Actually-played clip per Pantera LP1/RP2 move key, counting key variants/twins (40 pure + 17 chord-involved, incl. grapple chains) |
| Batch-research triage | 31 keys, 73 steps | Canonical LP1/RP2-only multi-step keys (every step LP1/RP2/chord after stripping stance/direction prefixes) in the payload moveset |
| Focus Stage 1 strings-list audit | 81 entries, Batch 1 = 19 | Strings-list entries (fired full-input move per entry): 19 Batch-1 entries = 14 T8-fired + 1 T7-only + 4 single-row wired |

Mapping: all 19 focus Batch-1 entries are in the 31 triage keys (after spelling normalisation `df+` -> `d/f+`, `ws2` ->
`WS.`). The 12 triage keys outside focus Batch 1 are `1,1`, `b+1+2,1+2`, `b+1+2,2`, `d/b+1+2,2`, `f+2,1,1`, `f+2,1,1,2`,
and the 6 jumping strings (`u+1,1`, `u+1,2`, `u/b+1,1`, `u/b+1,2`, `u/f+1,1`, `u/f+1,2`) — the focus audit counts fired
strings-list entries, the triage counts canonical keys, and the CSV counts played move keys incl. twins. The 60 plan
keys = 31 canonical + 26 twins + 3 spelling variants (throw twin excluded).

## Switch-criteria checklist (batch-research gate, applied to this PR)

1. T3 source branch JSONs re-pulled — FAIL. No `teardown/tekken3/` directory exists in the private
   game-reverse-engineering repo (its `teardown/` holds firepro, gang-beasts, pakchunk0, tekken7-steam, tkdata,
   wrestling-empire, wwe2k19, yakuza-kiwami only), and the workspace copy (`batch8wt/teardown/tekken3/movesets/`)
   holds only bosconovitch/gunjack/ogre/xiaoyu — no King branch JSON. Step derivations therefore use recorded
   `strings[].t3_rows` + prefix-move rows + gates, with the derivation recorded per step; branch-path re-derivation
   remains open work, NOT claimed.
2. `step_check.py` reproduces PASS 8 / REVIEW 8 / NO-ROW 15 — PASS (re-run this turn on the research inputs: stderr
   `PASS 8 / REVIEW 8 / NO-ROW 15 of 31`). All 31 triage keys are present in fresh-main `pantera.json` moves, and the
   recorded `strings[]` paths match the payload (e.g. `2,1` -> [203, 220], `d+1+2,2` -> [98]).
3. Job-2 `match_search` candidates landed — NOT LANDED (no `match_search` output in the workspace). This PR is
   therefore explicitly scoped to VERIFIED steps only (criterion 3's alternative): NO-ROW/review steps are UNMAPPED,
   never pooled. When job-2 candidates land, they enter as candidates through these same gates, not as assignments.

   UPDATE (follow-up PR, 2026-10-25): match_search candidates HAVE now landed via the GPU jobs 1–6 ingest
   (`unzipped/job3-out/match_search.json` + `run-log/batch1_job3_step_map.json` in the ingest package). The two fills
   in the follow-up section entered through these same gates. The remaining NO-ROW/review steps stay
   UNMAPPED/REVIEW, never pooled.
4. Damage/startup last-hit normalisation implemented + spot-checked — SPOT-CHECKED for the wired scope (above); no
   data change needed for the 11 verified-last-step keys. Unwired strings keep their existing damage (incl. `1,2`'s
   total 20) until their steps land.
5. Play-verification protocol agreed — HANDOFF ISSUED (below + parent report). No 'fixed' claim until the user plays it.
Additional unproven item: pose continuity is UNPROVEN — no blend added; the handoff includes a snap check, and a blend
is added only if play shows a snap.

## Kinmot decode status (step 1 of the 6-step plan)

- File located in the workspace (NOT assumed): `batch-motbin/batch-bin/kinmot.bin`, 2,551,112 bytes,
  SHA-256 `48f9c91fcdbd0519d1ece97ff827001fe1a3155a6dd775d203be93b42952c729`. Already decoded by the parallel
  batch-motbin lane (`batch-motbin/json/kinmot.json`, private-repo PR #63, WH wiring PR #1048 — both still open at
  this PR's base): 2,787 moves, 11,879 cancels counted from move lists (meta count 11,862 — a 17-cancel discrepancy
  between the meta header count and the summed move cancel lists, recorded here, not resolved). Direct 8,627 /
  aliased (>= 0x8000) 3,252 / single-button direct edges 1,493. Aliased cancels use only 20 distinct slots (slot 1 alone:
  2,350) — the '56-entry aliases table' from the research brief is NOT recovered: the converter emits no aliases table,
  and no alias slot -> move resolution is claimed in this PR. The extended-converter job (aliases + MOTA durations)
  is therefore PARTIAL: the decode exists, the extension does not. `anim_len` reads 0 for all sampled raw moves, so
  MOTA durations/bytes remain UNMAPPED (the parallel script's `anim_len` length test is VOID — not used as evidence anywhere here).
- Requirement semantics (codes 636/811/80/81/72/217) remain UNMAPPED; gated T7 cancel edges are not used as string steps.
- King cancel-graph counts differ from the research report's re-derived frv/dnc counts because those are different
  fighters (Raven/Chloe): frv 11,590 cancels (report) vs the earlier record 11,573, dnc 10,051 vs 10,034 — the report's
  re-derived counts are used for frv/dnc; neither is King's graph. King's own step chains are NOT wired in this PR:
  T7 wiring waits on clip bytes + requirement resolution (see PROCEDURAL_AUDIT entry).

## Paths (both step mechanisms, stated per string)

- Per-press path (`_pressV2` -> `tryAttack` -> `_fireNotation` per press): every planned string. The final press fires
  the string move; `_attackClipPlan`'s step-plan branch selects its last step's verified row, or no bank row when the
  last step is review/unmapped. Earlier presses already played their own prefix moves' rows (or their own plans).
- Whole-string path (`_tryAttackFresh` full-notation fire -> `_stepChain` -> `_fireNotation` per prefix): only planned
  string moves whose EVERY prefix is a real move (checked at fire time). Jumping strings have no standalone `u+1` /
  `u/b+1` move, so they never chain — they fire normally and the clip branch governs. `f+2,1~t3.king` (`strike`) never
  chains (chain branch requires `move_class` `string`); its clip branch governs.
- Blend: none in this PR (see above).

## Play handoff (parent browser lane — NOT done by this lane, no live browser here)

Netlify https://endearing-scone-b3d816.netlify.app/ (after this PR merges AND the main -> gh-pages deploy sync runs —
note: the gh-pages sync is separately BLOCKED on the #988 moveset conflict per the complaints-tracker synthesis; do NOT
run a blind full sync, and do NOT use the sync-except-56 workaround without an owner decision). Phone portrait, human
simulation (screenshot, look, scroll, THEN tap; touch taps like the user plays). Menu -> select Pantera -> stage -> FIGHT, then:
1. `1,2` (LP1,RP2): step 1 plays the LP1 jab row 110; step 2 plays NO bank row (procedural) — confirm step 2 is NOT the old donor row 99 and NOT a jump clip.
2. `b+2,1+2` (back + RP2, then LP1+RP2): confirm the ender is NOT the old jumping row 35 (feet stay grounded).
3. `FC.1,2` (crouch + LP1,RP2): confirm step 1 is not an airborne row and step 2 is not donor row 99.
4. `WS.2,2` (while-standing RP2,RP2): confirm neither step plays donor row 99.
5. `2,1` (RP2,LP1) + all its twins: confirm the LP1 ender is NOT jumping row 220 (feet grounded, single LP1 arm) — expect procedural on the ender until its row lands; step 1 must read as RP2 row 203 context.
6. Verified controls (must still play their rows): `d+1+2,2` (rows 97 -> 98), `d+1+2,2,1` (97 -> 98 -> 198), `u+1,1` (jumping row 38).
7. Snap check: on every multi-step string above, record whether the cut between steps visibly snaps. A snap does NOT fail the string — it queues the blend work. A wrong row DOES fail it.
8. Regression: no step silently donor-falls-back — any planned string playing rows 99/110/35/220 other than the verified controls above is a FAIL to report back, not a pass.
Follow-up checks (after this PR merges, on top of #1096's pass):
9. `b+2,1+2` (back + RP2, then LP1+RP2) + both twins: confirm the ender plays a STANDING chord clip (row 97), feet grounded — NOT the old jumping donor row 35. First step still procedural.
10. `u/b+1,1` and `u/b+1,2` (up-back + LP1, then LP1/RP2): confirm the first step reads as a JUMPING LP1 (row 49, SOFT). If it does not read as the jumping LP1, the SOFT steps revert to UNMAPPED — report that, do not pass it.
11. Job 4 regression: no step plays row 584 or row 220; review steps (rows 257/258 candidates) still play NO bank row.
Until this pass completes, Batch 1 is wired + re-audited, NOT play-verified, and nothing in it is 'fixed'.

## Still UNMAPPED (after this PR)

- King cancel graph as wired steps (decode exists; aliases + requirements unresolved; clip bytes unresolved).
- Aliases table (converter emits none; 20 distinct King alias slots observed, slot 1 dominant).
- MOTA clip durations/bytes (`anim_len` = 0 everywhere).
- Requirement semantics (636/811/80/81/72/217).
- Kaggle job 1-6 outputs (pending; cross-checks when they land — lane does not wait).
- TKMovesets2 access (PC + running T7; unavailable from the VM).
- Review steps (canonical: rows 257/258/117 cases) pending adjudication + play-verify.
- All HARD moves beyond Batch 1's scope (LK3/RK4 Batch 2, mixed pairs, rest) — same pipeline, later PRs.
- Grapple-chain + TACKLE CSV rows (10) — separate grapple systems, not Batch 1.

