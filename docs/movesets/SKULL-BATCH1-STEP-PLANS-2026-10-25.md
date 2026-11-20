# SKULL BATCH 1 — STEP PLANS (LP1/RP2-only strings, 2026-10-25)

Skull's FIRST batch in the locked fighter order (Pantera → burger → demonio →
diablo → kinpo → phantom → scimitar → skull). Skull is the LAST fighter.
Scope: strings whose steps are ALL buttoned and whose button union is exactly
{LP1, RP2} (any directionals, any contexts: standing/crouch/jump/ws). Pure
single-button strings first, then chord-involved strings (chords containing
only LP1/RP2 buttons).

## Bank — VERIFIED, not assumed (four-way file evidence)

1. **skull.json t3_source + t3_bank on BOTH #1096 and main:** `bryan` /
   `moveset_bryan.json` on both files (blob 4293b305… on #1096,
   6cfe81ed… on main). tekken_base `Bryan Fury`; merge_sources
   t8/t7/t3 all `bryan`.
2. **t3/ directory presence:** `game/assets/anim/t3/bryan/` exists with
   `hit_frames.json` + `rows.pack.json` + `skeleton.json` (plus the full
   t3_* slot set). Pack bank: `teardown/tekken3/animations/divmot12_bryan.bin`.
3. **Job 1 row count for the resolved bank:** bryan 160 rows.
4. **Job 2 skull entries' bank consistency:** ALL 688 skull entries bank
   bryan, zero exceptions. Job 4 bryan candidates: 27.

The pack dir does NOT differ from the moveset bank name (unlike diablo's
heihachi/heihachi_on_jin split). This bank is **NATIVE, not a fallback**:
Bryan debuted in Tekken 3, and this is the character's own T3 bank. It is
the SAME bank as burger's fallback — but skull's row identities below were
re-derived from the files, not copied from burger's adjudication (and the
gap-1 check below re-verifies the blobs independently).

### Bryan-bank row rules (per-bank evidence — never a cross-bank blanket ban)

- **Row 35 does NOT EXIST in this bank** (absent from hit_frames AND Job 1).
  No row-35 rule applies at all; any candidate citing 35 for skull would be
  a data error, never a gate decision.
- **Row 220 EXISTS in hit_frames ([25,26,65,271,0,0], button 0) but is
  ABSENT from Job 1.** It fails every single-button gate (button 0) and has
  no stance profile. It is NOT jin's standing RP2 row 220, NOT king's
  jumping chord row, NOT heihachi's jump RK4 row.
- **Row 216 EXISTS in hit_frames ([20,21,30,271,0,0], button 0) but is
  ABSENT from Job 1.** Same treatment: fails every single-button gate.
  It is NOT king row 216's dash Konvict Kick, NOT jin row 216's jump row.
- **Duck-dip rows (Job 1, 6):** 157, 158, 166, 178, 179, 351 — handled like
  crouch: STANCE-SOFT (review) for non-crouch contexts.
- **Job 1 covers 160 of the 210 hit_frames rows.** A candidate row present
  in hit_frames but absent from Job 1 is documented as such (no stance
  profile), never assumed standing.
- **Job 1 stance census:** standing 85, starts-airborne 30, jump 23,
  crouch 11, duck-dip 6, ground 5 = 160.

### Skull's own basics (file evidence)

- LP1 move `1`: t3_row **172** on #1096 (standing LP1, hit_frames
  [10,10,45,1042,0,1], Job 1 standing, armL, level h) — **unchanged on main**
  (damage-only drift 11→9), NOT suspending.
- RP2 move `2`: t3_row **100** on #1096 (standing RP2, hit_frames
  [10,10,39,1042,0,2], Job 1 standing, armR, level h) — **unchanged on main**
  (damage-only drift 12→13), NOT suspending.
- LK3 move `3`: t3_row **63** on #1096 (a JUMP row, hit_frames
  [9,9,52,535,0,4], Job 1 jump) and **ROW-CHANGED on main (63→None,
  anim_ref None)** — Batch 2's problem, not Batch 1's, but recorded here
  because it confirms the prior note's "skull LK3 (jump clips)" from file
  evidence.
- RK4 move `4`: t3_row **104** both files (standing RK4, hit_frames
  [12,12,50,1042,0,8]).

### Gap-1 (diablo/kinpo method)

Main bryan hit_frames blob `7ffea6b998d6…`, rows.pack blob
`1e22a8832b2c…`, and skeleton blob `32d521db0921…` are **IDENTICAL on #1096
and current main — ZERO bank drift** (the same blobs as burger Batch 1's
gap-1, independently re-verified here). No phantom-Batch-4-style re-bake
signature change: no drift to report, no fill suspended on bank drift.
Every wired row is present in the current main pack (160 rows) at wire time.

## Baseline

- #1096 skull: 688 moves / 109 strings, no `string_step_plans`.
- Current main skull: 634 moves + 54 quarantined-only = 688 exactly;
  0 main-only moves; 109 strings (identical list).
- Full-file drift census (1096 vs current main, 688 keys): **336 same /
  237 damage-only / 112 anim_ref-changed / 3 ROW-CHANGED** (3, 3_c36,
  u+1,3 — all 63→None). Damage differs on **307** moves (237 damage-only +
  70 in the anim_ref-changed/row-changed gap). Both damage figures are
  true under their definitions; neither is silently picked.
- Row-change re-check against Batch 1 scope: the 3 row-changed moves are
  all LK3-family (button 3) — **none is a Batch 1 step prefix** (Batch 1
  strings carry only LP1/RP2 buttons). **Suspended-drift steps: 0.**
- Canonicalization is the CORRECTED rule (strip ONLY a trailing
  `~t[378]\.[a-z]+(\.\d+)?$` suffix): skull Batch 1 contains **ZERO
  input-~ canonicals**, and skull is **INERT file-wide** — all 372 comma
  keys checked, 181 carry a `~`, 0 carry a non-trailing `~` (suffixes
  `~t3.bryan[.2/.3/.4]` / `~t7.bryan[.2/.3/.4/.5]`; no `~t8.*` suffixes
  exist in skull). Old canonical == corrected canonical for all 372 keys.
  No input-~ canonical exists in any skull batch scope (contrast phantom
  Batch 4's 3 input-~ canonicals).
- `__main` records in Batch 1 scope: **none** (no `__main` canonical filed;
  the demonio Batch 4 filing rule was checked and did not fire).
- Corrupted keys in Batch 1 scope: **none** (no diablo/phantom-style
  `&#58;` key found).
- Spelling quirks kept (distinct canonicals, never merged): **D/F+1,1
  family vs DF+1,1 family** (both unmapped-all); **FC.d/f+2,1 vs FC.df+2,1**
  (both unmapped-all).
- WS-context fix (kinpo Batch 1): checked — Batch 1 scope contains **zero
  ws-context canonicals** (contexts: standing 22, jump 19, crouch 16, ws 0),
  so the fix changes no wiring here.

## Universe (measured first, never assumed)

- **57 canonicals: 41 pure single-button + 16 chord-involved.**
- **54 planned (strike) + 3 CSV-only (throw/grapple):** TACKLE.1,1,
  TACKLE.1,1,1, TACKLE.1,1,1,1 — CSV-audited only, never planned (narrow
  grapple label: only {PILE_DRIVER, ARM_BREAKER, TACKLE} count).
- 94 CSV rows (57 canonicals + 37 variants) → **91 plan keys** (54 planned
  canonicals + 37 twins; the 3 CSV-only canonicals have 0 variants).
- Provenance: 49 canonicals in main moves, 8 quarantined-only (live when
  #988 merges: SLS.2,1; SLS.2,2; SS.2,1; f+2,1,SNE.2; uf+2,2; uf+2,2,2;
  uf+2,2,2,SNE.2; uf+2,2,2,SNE.2,2), 0 in-1096-only.
- Longest Batch 1 string: ub+1+2,1,2,1,2,1,2,1,2,1 (10 steps, all unmapped).

## Steps: 173 = 164 planned + 9 CSV-only

Planned steps: **32 verified / 5 review / 127 unmapped** (0 suspended).
Unmapped split: **122 no-candidate / 5 rejected-candidate / 0 suspended**.
Canonical string_status (54 planned): **7 verified-all / 18 partial /
29 unmapped-all** (the 18 partials = 14 with ≥1 verified step + 4
review+unmapped). Plan-key last-step: 26 verified / 65 unmapped.

## Wired fills (all VERIFIED, gate-verified own/recorded-path rows, T3 FALLBACK)

32 verified steps, 18 distinct rows, all present in the current main bryan
pack. Every verified row passes: hit_frames button == step bits, throw 0,
stance gate, and the Job 1 limb-peak SOFT proxy (window = [active_first/2
− 2, active_last/2 + 2]; jump-context steps SOFT-waived per Batch 1
precedent).

| String | Steps (rows) | Source |
|---|---|---|
| 2,1 | [152, 153] | recorded-path |
| 2,1,2 | [152, 153, 151] | recorded-path |
| f+1,2 | [172, 173] | prefix-move (own LP1 row + own RP2 row) |
| d/f+1+2,2 | [113, 149] | prefix-move (chord row 113 crouch; 149 GATE-NOTE) |
| d/f+1+2,d/f+1 | [113, 146] | prefix-move (146 GATE-NOTE) |
| d/f+1+2,d/f+1,d/f+1 | [113, 146, 147] | prefix-move (146/147 GATE-NOTE) |
| d/f+1+2,d/f+1,d/f+1,d/f+1 | [113, 146, 147, 148] | prefix-move (146/147/148 GATE-NOTE) |
| 1,2 (step 1 only) | [172, —] | prefix-move (own LP1 row; step 2 no candidate) |
| 1,2,1 (step 1 only) | [172, —, —] | prefix-move |
| b+1,2 (step 2 only) | [—, 145] | prefix-move |
| b+2,f+1,2 (step 3 only) | [—, —, 151] | prefix-move |
| d/f+1,2 (step 1 only) | [146, —] | prefix-move (146 GATE-NOTE) |
| d/f+2,1 (step 1 only) | [149, —] | prefix-move (149 GATE-NOTE) |
| f+2,1 (step 1 only) | [150, —] | prefix-move |
| f+2,1,SNE.2 (step 1 only) | [150, —, —] | prefix-move |
| u+1,1 / u+1,2 (step 2 only) | [—, 44 / 56] | prefix-move (jump, SOFT-waived) |
| u/b+1,1 / u/b+1,2 (step 2 only) | [—, 46 / 58] | prefix-move (jump, SOFT-waived) |
| u/f+1,1 / u/f+1,2 (step 2 only) | [—, 45 / 57] | prefix-move (jump, SOFT-waived) |

Verified-row profiles (hit_frames [first, last, frames, word, throw,
button] / Job 1 stance / active window / step-limb peak):
- 152 [17,17,56,1042,0,2] standing, window [6.5,10.5], armR 9 ✓
- 153 [19,19,58,1042,0,1] standing, window [7.5,11.5], armL 10 ✓
- 151 [13,13,60,1042,0,2] standing, window [4.5,8.5], armR 8 ✓
- 172 [10,10,45,1042,0,1] standing, window [3,7], armL 5 ✓
- 173 [10,10,45,1042,0,2] standing, window [3,7], armR 3 ✓ (boundary)
- 113 [8,8,37,799,0,3] crouch, window [2,6], chord armL 4 ✓ (armR 1)
- 149 [23,23,61,535,0,2] standing, window [9.5,13.5], armR 13 ✓
- 146/147/148 [10,10,41,535,0,1] standing, window [3,7], armL 5 ✓
- 145 [12,12,41,1042,0,2] standing, window [4,8], armR 6 ✓
- 150 [13,13,60,1042,0,2] standing, window [4.5,8.5], armR 8 ✓
- 44/46/45 [11,12,39,535,0,1] starts-airborne, jump, SOFT-waived
- 56/58/57 [11,13,53,535,0,2] starts-airborne, jump, SOFT-waived

**GATE-NOTE (demonio Batch 1 edge, carried here):** the gate flags crouch
rows for non-crouch steps, NOT standing rows for crouch steps. The
following verified steps use a standing row for a crouch-context step
and carry the GATE-NOTE, with the re-adjudication note if the gate is
ever tightened: d/f+1+2,2 step 2 (149); d/f+1+2,d/f+1 step 2 (146);
d/f+1+2,d/f+1,d/f+1 steps 2 (146), 3 (147);
d/f+1+2,d/f+1,d/f+1,d/f+1 steps 2 (146), 3 (147), 4 (148); d/f+1,2 step 1
(146); d/f+2,1 step 1 (149). Step 1 of the d/f+1+2 family (row 113) is a
crouch row for a crouch step and carries NO gate note.

**ROW DUAL-ROLE CAUTION (Pantera Batch 4):** a row verified for one
string/context is NOT globally verified — every step gate-checks its own
row again. Rows 146/147/148 are three distinct rows with identical
profiles; each was gated per step, not inherited.

## Suspended-drift (0)

None. The file's only row-changed moves (3, 3_c36, u+1,3 — all 63→None)
are not Batch 1 step prefixes. No stale row is wired anywhere in this batch.

## Review steps (5)

- b+1+2,1 step b+1+2: candidate **167** (prefix-move), STANCE-SOFT crouch
  row for a standing-context step — review, row null.
- b+2,1 / b+2,1,2 / b+2,f+1 / b+2,f+1,2 step b+2: candidate **158**
  (prefix-move), STANCE-SOFT duck-dip row for a standing-context step —
  review, row null. (Row 158 is also the Job 4 join for these steps; see
  Job 4 — a join never promotes, so the steps stay review.)

## Rejected-candidate (5)

- b+1+2,1 step 1: candidate **168** (prefix-move), button 0 != step bits 1.
- u/b+1,1 / u/b+1,2 step u/b+1: candidate **43** (prefix-move), button 3
  != step bits 1 (a kick row offered for a punch step).
- u/f+1,1 / u/f+1,2 step u/f+1: candidate **42** (prefix-move), button 3
  != step bits 1.

## No-candidate (122)

The expected pattern (scimitar/phantom precedent): intermediate prefixes
are T8-sourced strings with no T3 row. Their correct clips come from #988
Step 2 (original T8 refs) or future extraction — never from a T3 row
recorded as correct. Notable no-candidate families: the entire D/F+1,1 /
DF+1,1 / FC.d/f+2,1 / FC.df+2,1 crouch families (no row for any step);
the 1+2 chord family (step 1+2 has no row — Job 3's row 136 is ROW-ONLY,
see below); the ub+1+2 10-hit jump family (no row for any step);
SLS/SS stance families; qcf+2,1; uf+2,2 family (quarantined-only).

## Job 3 (8 report entries, 0 fills wired)

All candidates are ROW-ONLY or soft — documented, NEVER wired (burger
refinement: a fill additionally requires the SOFT proxy to pass; no
candidate here reaches exact+FULL at all):

| Step | Candidates |
|---|---|
| 1+2,1 step 1+2 | row 136 exact ROW-ONLY (target 1+2) |
| 1+2,2 step 1+2 | row 136 exact ROW-ONLY (target 1+2) |
| 1,2 / 1,2,1 step 1 (verified, own row 172) | row 99 exact ROW-ONLY; rows 132/146/147/148 soft-filed ROW-ONLY (target 1) — the own row 172 is stronger file evidence; disagreement documented, not silently resolved |
| 2,1 / 2,1,2 step 2 (verified, recorded-path row 152) | rows 101/105/106 exact ROW-ONLY; row 126 unknown (not in top10) ROW-ONLY (target 2) — recorded-path row 152 is stronger file evidence |
| d/f+1,2 step 2 (unmapped) | row 114 soft-filed ROW-ONLY; row 167 exact ROW-ONLY (target d/f+1,2) |
| d/f+2,1 step d/f+2 (verified, own row 149) | row 114 soft-filed ROW-ONLY; row 167 exact ROW-ONLY (target d/f+2) — own row 149 is stronger file evidence |

**No agreement note fires:** the note fires ONLY for actually-wired gate
candidates disagreeing with an exact+FULL Job 3 candidate, and no
exact+FULL Job 3 candidate exists for any verified step.
**Dedupe fires zero times:** the only Batch 1 prefix with a __main Job 3
target (1+2) has an EMPTY __main pass-all list, so no pass-all row is
shared between plain and __main targets.
No SOFT fill is inherited from #1097 (Pantera-specific, still unapproved,
does not transfer to skull). SOFT proxy: proxy-fail = review, never false
verify — no SOFT candidate was wired on proxy grounds.

## Job 4 (corrected join only: 4 joins, none promoting)

Corrected join (demonio Batch 2 method): skull-only, BANK_DIR bryan, join
iff Job 2 has a skull entry key == step prefix, row == candidate row,
step == own. The naive cross-fighter join on key-prefix equality is
INVALID and was never used.

- **4 joins, all CANDIDATE, NOT wired:** row 158 joined for the b+2 step
  in b+2,1 / b+2,1,2 / b+2,f+1 / b+2,f+1,2 (peaks armL 1, armR 2, legL 0,
  legR 0). A join NEVER promotes a candidate by itself; the steps stay
  review (STANCE-SOFT duck-dip row for standing-context steps).
- **0 orphans:** every bryan Job 4 candidate is carried by a skull Job 2
  move (any step).

## Donor rows documented, never wired

Wiring plans replaces single-row resolution wholesale, even for CLEAN
donors, because one row cannot be correct for a multi-hit string (donor
retirement is DESIGNED, not a regression). Donor rows visible in the CSV
(e.g. 1,2 donor row 100, 1,2,1 donor row 172, D/F+1,1 donor row 172 with a
HARD stance flag) are documented in `skull_batch1_lp_rp.csv` and are NOT
played: the step plans govern. No step in this batch plays a jumping row
for a ground step, and no step plays a row from another bank.

## Tests

Minimal-tree `node --test`: **12/12 pass**; `node --check fighter.js` OK.
Formatter round-trips the #1096 branch file byte-identically; all
non-plan keys identical; moves 688 / strings 109 unchanged; 91 plan keys
added; CSV-only TACKLE keys gain no plan. This is skull's BASELINE test
file — later skull batches accumulate cumulatively with every Batch 1
CONTENT assertion preserved verbatim (TEST-EVOLUTION RULE).

**Limitation (stated in the PR body):** full 200-test suite comparison
NOT run — no full current-main checkout on this box; CI must cover
before merge.

## Play-verify checklist (parent browser delegation, after #1096 + this PR merge + deploy + sync, phone portrait)

- **2,1 [152,153]** and **2,1,2 [152,153,151]** — all steps grounded
  (standing RP2/LP1 and RP2/LP1/RP2), no jumping row, no cross-bank row.
- **f+1,2 [172,173]** — step 1 skull's own standing LP1 row 172, step 2
  standing RP2 row 173.
- **d/f+1+2,2 [113,149]**, **d/f+1+2,d/f+1 [113,146]**,
  **d/f+1+2,d/f+1,d/f+1 [113,146,147]**,
  **d/f+1+2,d/f+1,d/f+1,d/f+1 [113,146,147,148]** — crouch-context
  family; step 1 crouch chord row 113, later steps standing rows
  (GATE-NOTE — verify they read as crouch-context strikes, not standing
  strikes, when played).
- **1,2 [172,NO row]** — step 1 grounded LP1 row 172; step 2 NO row
  (must NOT fall back to any donor row, e.g. the CSV's donor row 100).
- **1,2,1 [172,NO row,NO row]** — same, steps 2–3 silent.
- **b+1,2 [NO row,145]** — step 1 NO row (review candidate 167 must NOT
  play); step 2 grounded RP2 row 145.
- **b+2,1 / b+2,1,2 / b+2,f+1 / b+2,f+1,2** — step b+2 NO row (review
  candidate 158 / Job 4 join must NOT play); b+2,f+1,2 step 3 grounded
  row 151.
- **u+1,1 [NO row,44]**, **u+1,2 [NO row,56]**, **u/b+1,1 [NO row,46]**,
  **u/b+1,2 [NO row,58]**, **u/f+1,1 [NO row,45]**, **u/f+1,2 [NO row,57]**
  — jump-context families; step 1 NO row (rejected candidates 42/43
  must NOT play); step 2 starts-airborne rows grounded-in-context only.
- **1+2,1 / 1+2,2** — NO row any step (Job 3 row 136 ROW-ONLY must NOT play).
- **TACKLE.1,1 family** — no plan, CSV-only (grapple, out of scope for
  step playback).
- **No step plays a bryan airborne/jump row for a ground step.** No step
  plays a row from another bank. No step plays row 220 or 216 (both
  button-0 rows in this bank) or row 35 (does not exist in this bank).

No play verification claimed — tests + file evidence only; playing is
the parent's step after merge + deploy.
