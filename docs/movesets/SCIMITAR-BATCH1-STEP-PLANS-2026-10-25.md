# SCIMITAR BATCH 1 — STEP PLANS (LP1/RP2-only strings, 2026-10-25)

Stack: #1096 engine → scimitar Batch 1 (this PR). Merges AFTER #1096.
Touches nothing else: no fighter.js, pantera.json, burger.json, demonio.json,
diablo.json, kinpo.json, phantom.json. No T8 content touched.

## Bank — VERIFIED, not assumed (four-way file evidence)

- scimitar.json `t3_source`: 'jin', `t3_bank`: 'moveset_jin.json' — on BOTH
  #1096 (blob 13bfd9ce…) and current main (blob 64b707f4…).
- game/assets/anim/t3/ on main contains a `jin` dir (hit_frames +
  rows.pack + skeleton). NO `shaheen` dir exists under t3/.
- Job 1 bank jin: 220 rows. Job 2 scimitar entries: 362, ALL bank jin.
  Job 4 jin candidates: 47.
- Resolution: scimitar's T7/T8 base is Shaheen (tekken_base 'Shaheen',
  merge_sources t8/t7 shaheen) and Shaheen debuted in Tekken 7, so this
  bank is a FALLBACK, not native — the kinpo pattern (Asuka → jin;
  contrast phantom Yoshimitsu → yoshimitsu native, burger Bob → bryan).
- Pack dir = bank name (jin). No diablo-style split
  (heihachi / heihachi_on_jin).

### Jin-bank row rules (per-bank evidence — never a cross-bank blanket ban)

Demonio/kinpo adjudicated this same bank independently; this lane
re-derives from the files:

- Row 35 EXISTS: hit_frames [11,12,39,535,0,1]; Job 1 starts-airborne
  (y0 1.769 vs standingY 1.027, armL, level m) — ground-rejected,
  jump-context only.
- Row 220 is a STANDING RP2 row: hit_frames [12,12,41,1042,0,2]; Job 1
  standing (armR, level h) — NOT king's jumping chord row, NOT bryan's
  button-0 row, NOT heihachi's jump RK4 row. Gate-adjudicated like any row.
- Row 216 is a JUMP row: hit_frames [63,64,117,1543,0,0]; Job 1 jump,
  button 0, level u — fails every single-button gate.
- Row 41 is a starts-airborne LP1 row: hit_frames [7,7,35,535,0,1];
  Job 1 starts-airborne (y0 1.695) — ground-rejected, jump-context only.
- Jin Job 1 duck-dip rows (16): 123, 189, 192, 210, 211, 212, 213, 235,
  257, 367, 377, 381, 385, 387, 389, 397 — handled like crouch
  (STANCE-SOFT for non-crouch contexts).

### Scimitar's own basics (file evidence)

- LP1 move `1`: #1096 t3_row 184 (standing LP1 row; hit_frames
  [12,13,64,799,0,9] — button 9 = LP1+RK4 chord, level s). On current main:
  t3_row None, anim_ref None — ROW-CHANGED 184→None. Both Batch 1 steps
  with prefix `1` (1,2 step 1, 1,2,2 step 1) are SUSPENDED-DRIFT; the stale
  row 184 is documented, never wired — and it would fail the LP1 button
  gate regardless (9 ≠ 1).
- RP2 move `2`: #1096 t3_row 220 (the standing RP2 row above), main
  t3_row 220 — damage-only drift (4→10), NOT suspending.
- LK3 move `3`: 195 both files, damage-only (14→20). RK4 move `4`: 199
  both files, damage-only (7→16).

### Gap-1 (diablo/kinpo method)

- jin hit_frames blob 54b38e63… IDENTICAL on #1096 and main.
- jin skeleton blob 26f72eb7… IDENTICAL on #1096 and main.
- jin rows.pack: main blob 7bafa36a… (226 rows) = #1096 blob
  141fbc8d… (220 rows) + exactly the 6 #1109 bake jin rows
  (89/112/247/288/339/357), SUPERSET, 0 removed (same as kinpo Batch 1).
- Every wired row verified present in the CURRENT main pack at wire time.

## Baseline

- #1096: 362 moves, 50 strings, no string_step_plans.
- Main: 329 moves + 33 t8_quarantine_20261024 = 362. Strings lists
  identical (50/50). 0 main-only moves.
- Full-file drift census (1096 vs current main, 362 keys): 220 same /
  84 damage-only / 57 anim_ref-changed / 1 ROW-CHANGED (1: 184→None).
  Damage differs on 116 moves (84 damage-only + 32 gap). Both damage
  figures are true under their definitions; never silently pick one.
  Damage-only drift does NOT suspend (damage ≠ animation).

## Universe (measured first, never assumed)

- 14 canonicals: 11 pure single-button + 3 chord-involved.
- 11 planned (strike) + 3 CSV-only (TACKLE.1,1 family — narrow grapple
  label, audited, never planned).
- 24 CSV rows (14 canonicals + 10 variants) → 21 plan keys (11 planned
  canonicals + 10 twins inheriting canonical steps verbatim).
- Contexts: standing 8, crouch 6, jump 0, ws 0.
- Provenance: 13 in main moves, 1 quarantined-only, 0 #1096-only.
- Variants: 1,2 → 1,2~t7.shaheen, 1,2~t7.shaheen.2, 1,2~t8.shaheen;
  1,2,2 → 1,2,2~t7.shaheen, 1,2,2~t7.shaheen.2, 1,2,2~t7.shaheen.3;
  2,1 → 2,1~t7.shaheen, 2,1~t7.shaheen.2, 2,1~t8.shaheen;
  d/b+2,1 → d/b+2,1~t7.shaheen.
- Input-~ canonicals in Batch 1 scope: ZERO. Scimitar is INERT file-wide
  on the corrected-rule axis: every ~ in the file is a trailing
  source-variant suffix (~t7.shaheen / ~t8.shaheen, with .2/.3), so old
  canonical == corrected canonical for all 114 comma keys (contrast
  phantom Batch 4's 3 input-~ canonicals). No input-~ canonical exists
  in any scimitar batch scope.
- __main canonicals in Batch 1 scope: 0. Corrupted keys in Batch 1
  scope: 0 (no diablo-style df+1,&#58;2 key, no phantom-style
  f,F+2,&amp;#58;2 key).
- Spelling quirks kept: d/b+2,1 vs db+2,1 are distinct canonicals (both
  unmapped-all, different step-1 drift evidence: damage-only vs
  anim_ref-changed). Trailing-* hold markers (D*,u+2; H.D*,u+2) are rest
  keys (buttonless D step) — Batch 4 scope, not Batch 1.

## Steps: 36 = 27 planned + 9 CSV-only

- Planned: 16 verified / 0 review / 11 unmapped (8 no-candidate +
  1 rejected-candidate + 2 suspended-drift).
- Canonical status (planned): 4 verified-all / 4 partial / 3 unmapped-all
  / 0 review-only. Plan-key last-step: 12 verified / 9 unmapped.
- CSV-only steps (9): TACKLE family — grapple-chain steps, strike clips
  excluded, throw-row verification owed separately (not a step-plan).

## Wired fills (all VERIFIED, gate-verified own/recorded-path rows, T3 FALLBACK)

All 8 distinct rows present in the current main jin pack (226 rows).
SOFT limb-peak proxy passes for all 8 (windows/peaks below).

- 2,1 verified-all [220, 221]: step 1 RP2 row 220 (standing, armR, h,
  hf [12,12,41,1042,0,2], SOFT window [4.0,8.0] armR peak 6); step 2 LP1
  row 221 (standing, armL, h, hf [14,14,43,1042,0,1], window [5.0,9.0]
  armL peak 7). Recorded-path rows.
- 2,1,2 verified-all [220, 221, 222]: step 3 RP2 row 222 (standing, armR,
  h, hf [10,10,39,1042,0,2], window [3.0,7.0] armR peak 5). Recorded-path.
- 2,1,2,2 verified-all [220, 221, 222, 223]: step 4 RP2 row 223
  (standing, armR-dominant, h, hf [17,17,60,1042,0,2], window [6.5,10.5]
  armR peak 8). Recorded-dest row (strings entry carries [223] only).
- 1,2 partial [NO row, 186]: step 2 RP2 row 186 (standing, armR, h, hf
  [27,27,64,1042,0,2], window [11.5,15.5] armR peak 13). Recorded-path.
  Step 1 suspended (see below).
- 1,2,2 partial [NO row, 186, NO row]: step 2 row 186 (prefix-move);
  step 3 (prefix 1,2,2, T8-sourced, no T3 row in either file) has no
  candidate — correct clip comes from #988 Step 2, never from a T3 row
  recorded as correct.
- d+1+2,2 verified-all [92, 93] (crouch context, GATE-NOTE — standing
  rows for crouch steps, demonio Batch 1 precedent; re-adjudicate if the
  gate tightens): step 1 chord LP1+RP2 row 92 (standing, dominant armL,
  h, hf [10,10,39,1042,0,3], window [3.0,7.0] armL peak 5 / armR peak 3);
  step 2 RP2 row 93 (standing, armR, h, hf [10,10,39,1042,0,2], window
  [3.0,7.0] armR peak 3). Prefix-move + recorded-dest.
- d+1+2,1 partial [92, NO row] (crouch, GATE-NOTE on step 1): step 1 row
  92 as above. Step 2 rejected (see below).
- d+1+2,1,2 partial [92, NO row, 183] (crouch, GATE-NOTE on steps 1/3):
  step 3 RP2 row 183 (standing, armR, m, hf [13,13,60,535,0,2], window
  [4.5,8.5] armR peak 6). Recorded-dest.
- No jump-context canonicals in Batch 1, so no SOFT waiver arises.
- No GATE-NOTE arises outside the d+1+2 family (zero crouch planned
  strings beyond it; all other verified steps are standing-context on
  standing rows).

## Suspended-drift (2, row null, stale rows documented, never wired)

- 1,2 step 1 + 1,2,2 step 1 — prefix move `1` ROW-CHANGED 184→None
  (1096 vs current main). Stale candidate row 184 documented (recorded-
  path for 1,2; prefix-move for 1,2,2). Row 184 would fail the LP1 button
  gate regardless (button 9 ≠ bits 1).
- The file's ONLY row-changed move is `1`; no other Batch 1 prefix is
  row-changed.

## Rejected-candidate (1)

- d+1+2,1 step 2 + d+1+2,1,2 step 2 — candidate row 177 (prefix-move /
  recorded-dest), button 12 ≠ step bits 1 (chord row; same row/result as
  kinpo Batch 1's d+1+2,1 step 2 rejection, independently re-derived).
  Row 177 profile: hf [15,15,44,1042,0,12], Job 1 standing, dominant
  armR, level h.

## No-candidate (8)

- SNK.df+1,2 steps 1–2 (prefix SNK.df+1 has no T3 row in either file;
  no strings-list recorded path for this canonical).
- d/b+2,1 steps 1–2; db+2,1 steps 1–2 (prefixes have no T3 row in either
  file; d/b+2 step 1 Job 3 candidates below, not wired).
- 1,2,2 step 3 (prefix 1,2,2 T8-sourced, no T3 row in either file).
- TACKLE-family steps are CSV-only, not counted here (9 steps, grapple
  reason, above).

## Job 3 (3 report entries, 0 fills wired)

- 1,2 step 1 + 1,2,2 step 1: prefix `1` candidates rows 92/105, exact
  level, ROW-ONLY — NOT wired (ROW-ONLY never wires; the steps are
  suspended on drift regardless).
- d/b+2,1 step 1: prefix `d/b+2` candidates rows 108/122, soft-filed,
  ROW-ONLY — NOT wired.
- No agreement note fires: the note fires ONLY for actually-wired gate
  candidates, and no exact+FULL Job 3 candidate exists for any verified
  step.
- Dedupe fires zero times: the only scimitar __main Job 3 target
  (1+2__main) has an EMPTY pass-all list and is not a Batch 1 step
  prefix; no Batch 1 step prefix shares a pass-all row between its plain
  and __main targets.
- No SOFT fill inherited from #1097 (Pantera-specific, still unapproved,
  does not transfer to scimitar).

## Job 4 (corrected join only: 0 joins, none promoting)

- 0 joined steps: no jin Job 4 candidate is carried by a scimitar Job 2
  own-row entry for any Batch 1 step prefix.
- Orphans (15): jin Job 4 candidates no scimitar Job 2 move carries (any
  step): 85, 91, 99, 100, 104, 127, 170, 171, 172, 209, 226, 239, 250, 256,
  262. (Kinpo Batch 1's orphan list was 16 — same list plus 216, which
  some scimitar Job 2 move DOES carry.)

## Donor rows documented, never wired

- 184 (TACKLE-family Job 2 donor; HARD string-ender-on-chord; also the
  stale LP1 row), 177 (button-12 chord row, rejected above), 186
  (1,2,2 Job 2 donor row — wired ONLY as the verified step-2 row for
  1,2 / 1,2,2, never as a whole-string clip).

## Tests

- Minimal-tree node --test: 11/11 pass (counts 362/50/21; Batch 1 keys
  exactly the 21; verified rows non-null with buttons in jin hit_frames
  and throw 0, review/unmapped row null, no soft flags; flagships 2,1 /
  2,1,2,2 / d+1+2,2 / 1,2 / d+1+2,1; TACKLE family gains no plan;
  verified-last-step set exactly the 12; fighter.js step-plan markers
  present). node --check fighter.js OK.
- Formatter round-trips the #1096 file byte-identically; structural
  diff shows exactly 1 diff (the string_step_plans addition); all
  non-plan keys identical; moves 362 / strings 50 unchanged.
- LIMITATION (honest): full 200-test suite comparison NOT run — no full
  current-main checkout on this box; CI must cover before merge.

## Play-verify checklist (parent browser delegation, after #1096 + this PR
merge + deploy + sync, phone portrait)

- 2,1 [220, 221], 2,1,2 [220, 221, 222], 2,1,2,2 [220, 221, 222, 223] —
  grounded standing RP2/LP1 chains; feet grounded.
- 1,2 [NO row, 186], 1,2,2 [NO row, 186, NO row] — first step NO row
  (stale row 184 must NOT play); second step row 186 grounded.
- d+1+2,2 [92, 93] — crouch context, GATE-NOTE standing rows, grounded.
- d+1+2,1 [92, NO row], d+1+2,1,2 [92, NO row, 183] — chord row 177 must
  NOT play for the LP1 middle steps.
- SNK.df+1,2 / d/b+2,1 / db+2,1: NO row any step.
- TACKLE.1,1 / TACKLE.1,1,1 / TACKLE.1,1,1,1: NO step-plan row any step
  (donor row 184 must NOT appear as a whole-string clip).
- No step plays a row from another bank. No step plays jin row 35/216
  (airborne/jump rows) for a ground step.
- Quarantined-only strings behave per plan ONLY after #988 merges
  (Batch 1 has 1 quarantined-only canonical: SNK.df+1,2).
- No play verification is claimed — tests + file evidence only; playing
  is the parent's step after merge + deploy.
