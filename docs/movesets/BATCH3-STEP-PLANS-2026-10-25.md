# Pantera Batch 3 — step plans (mixed-pair strings) — 2026-10-25

Button law: LP1 = Left Punch = Tekken 1, RP2 = Right Punch = Tekken 2, LK3 = Left Kick = Tekken 3, RK4 = Right Kick = Tekken 4.

> **Stack note:** this PR is stacked on #1099 (Batch 2 step-plan branch
> `feat/batch2-step-plans-pantera-20261025` @ `a0b6dc36`). Plans accumulate:
> #1096 (engine) → #1099 (Batch 2) → this Batch 3. It merges AFTER #1099
> (which merges after #1096, itself blocked on 12 pre-existing test failures
> / a gate decision owed) and after a rebase onto main at that time. It is
> NOT stacked on #1097 (which carries the unapproved SOFT row-49 fill):
> Batch 1 tallies below are #1096's record and Batch 2 tallies are #1099's
> record, NOT #1097's updated tallies. If #1097 merges first, this branch
> rebases onto the merged state and the Batch 1 guard map in
> `game/tests/batch3-step-plans.test.mjs` must be updated to #1097's Batch 1
> statuses (b+2,1+2 family → verified, u/b+1,1 and u/b+1,2 first steps →
> verified-SOFT). This PR does not touch `fighter.js`: #1096's merge onto
> post-#1078 main must reconcile #1078's `fighter.js` changes with #1096's
> engine branch, and that belongs to #1096's merge, not this PR.

## What this is

Batch 3 of the locked batch order (Batch 1 LP1/RP2 → Batch 2 LK3/RK4 →
Batch 3 mixed pairs → follow-up triples/quads/rest). The same step-plan
engine from #1096 (`game/js/fighter.js` `_attackClipPlan` step-plan branch +
`_stepChain`) plus `string_step_plans` data in
`game/assets/movesets/pantera.json`. A planned string move plays per-STEP
rows, never one row for the whole string. Only a step with status `verified`
plays its row. A `review`/`unmapped` step plays NO bank row — the existing
procedural fallback in `_animate` — and is flagged in `_atkPlan.unmapped`
with a `[WH-STEP-PLAN]` console line. Donor, match, and generic tiers are
bypassed for planned strings, so a planned string can never silently
donor-fall-back. No blend is added: step-to-step pose continuity is
UNPROVEN, and a blend ships only if play shows a snap.

## Universe (measured, not assumed)

Batch 1 measured 57 strings (40 pure + 17 chord). Batch 2 measured 15
canonical (11 pure + 4 chord). Batch 3 measures **18 canonical strings
(11 pure single-button + 7 chord-involved)**, from moves-dict keys ∪
strings-list entries whose button SET mixes punches and kicks in exactly
one pair: {LP1, LK3} (6), {LP1, RK4} (6), {RP2, LK3} (3), {RP2, RK4} (3),
any directionals. The four pair types are all present. Triples/quads
(3–4 distinct buttons, including 3-button chords) are the FOLLOW-UP batch,
not this one — e.g. a string whose steps use {1, 2, 3} is excluded here
even if it opens with a mixed pair. Plan keys: **49 = 17 planned canonical
+ 32 twins/variants** (`~t7.king` / `~t3.king` suffixes and the `3,2,2*`
hold variant; twins inherit canonical steps verbatim with canonical
prefixes, Batch 1 twin precedent). CSV rows: **50** (49 plan keys + the
CSV-only throw key below).

One canonical is throw class and gets NO plan: `AB1.2,4,2+4`
(move_class `throw`, T8-sourced) — CSV-audited only, per the Batch 1
precedent (throw-class twin `b+1+2,1+2~t7.king` likewise unplanned). All
other canonicals and all 32 variants are strike/string/special class and
are planned. Contexts: 9 standing, 6 jump, 3 crouch.

Provenance: 14 canonical in current main `moves/` (playable),
4 quarantined-only (`3,2`, `3,2,2`, `AB1.2,4,2+4`, `JGS.3,2+3` — in main's
`t8_quarantine_20261024`, restored to playable by #988 Option B; their
plans live on the #1099 base where the moves exist and become live when
#988 merges). Note the `3,2`/`3,2,2` plans do not depend on the quarantined
string entries themselves: their verified step 1 row comes from the single
`3` move, which IS in main `moves/`.

Grapple-label refinement (Batch 3 only, documented): Batch 2's heuristic
(any uppercase non-stance first-step label = grapple) would misclassify
`JGS` (Jaguar Step, a stance) in `JGS.3,2+3`. Batch 3 counts only the
Batch 1 known grapple-chain set {PILE_DRIVER, ARM_BREAKER, TACKLE} as
grapple labels, so `JGS.3,2+3` (move_class `string`) is planned. Batch 2
had no labeled strings, so no Batch 2 result changes. `AB1.2,4,2+4` is
excluded by move_class `throw` in any case.

## Gates (per step candidate, in order)

1. Candidate source: recorded path row (`strings[].t3_rows` full-path, or
   dest-only for the last step), else the prefix move's `t3_row`, else none.
   Only ONE Batch 3 string has a recorded path: `d/f+4,2` → `[196]`
   (dest-only). All other Batch 3 strings are plain-string entries (no
   `t3_rows`) or dicts without `t3_rows`. Recorded paths are NOT trusted
   blindly: a recorded row still faces every gate below.
2. HARD gates (fail = `unmapped`, candidate documented): button bitmask
   (`hit_frames.json` button field == step chord bits, LP1=1, RP2=2, LK3=4,
   RK4=8, chords OR-ed) + throw flag == 0 for strike steps + stance (see
   rule 4) + rows 35/220 rejected for ground steps always (they also fail
   button for mixed steps: both are button 3, the 1+2 chord).
3. SOFT gate (fail = `review`, not played): Job 1 peakF proxy for the Batch 1
   FK gate — window = stream active window / 2, +/-2 frames (Batch 1's rule);
   a step limb's Job 1 `peakF` inside the window passes. Chord steps: at
   least one limb peak in window. VALIDATED 13/13 on Batch 1's verified
   steps (correct limbs). The proxy is CONSERVATIVE: a max peak inside the
   window implies a threshold crossing inside, but a max outside can hide
   a secondary peak inside — so proxy-fail means review, never a false
   verify. WAIVED for jumping-context strings (Batch 1 precedent); all 6
   jump canonicals verify with the waiver noted in their reasons.
4. Stance gate: jump/starts-airborne rows fail ground-context steps and pass
   jump-context steps; crouch rows pass ONLY crouch-context steps; ground
   rows (downed-foe rows) fail all; ws-context steps matched to standing
   rows are review (ws→standing soft-stance, mirrors the Job 3 flag).
   Standing/duck-dip rows pass ground contexts (Batch 1 verified duck-dip
   rows for standing and crouch strings).
5. A gate-verified own/recorded candidate beats a disagreeing Job 3 candidate
   (own row is stronger file evidence); the disagreement is documented, not
   silently resolved. No such disagreement occurs in Batch 3 (the only
   Job 3 candidates are SOFT — see below — and no verified step has a Job 3
   candidate at all).
6. Donor→plan transition (Batches 1–2 precedent, stated plainly): 10 of 50
   Batch 3 CSV keys play a DONOR row today (Job 2 step `donor`), 40 play
   own rows, 0 play `anim` rows. Wiring a plan replaces that single-row
   resolution wholesale — even for CLEAN-donor strings — because one row
   cannot be correct for a multi-hit string. An unmapped step plays NO bank
   row (procedural fallback + flag), never the old donor row. This is the
   designed correction, not a regression: the string-level HARD/MED verdicts
   below are what the plans retire. Sharpest cases: `3,2`/`3,2,2` play
   donor row 99 today and their plans verify step 1 on row 264 while the
   last steps go unmapped (row 99 plays for neither step); `b+1,4`/`b+2,4`
   play donor row 216 today and their plans are unmapped-all. Row 264's
   dual role is NOT a contradiction: Batch 2 retired 264 as a whole-string
   donor row for `d/f+4,3`-family strings, while Batch 3 verifies 264 as
   the STEP row for the single LK3 step of `3,2`/`3,2,2` — different
   strings, different claims, both gate-checked.

## Gap-1 re-verification (Batches 1–2 method, replicated)

- King bank files IDENTICAL across the #1099 branch (`a0b6dc36`) and
  current main (`15c63a89`, re-checked at filing):
  `hit_frames.json` blob `7390cf4a4160e9d9bbe236d082a48f878bf5fabe`
  (API-confirmed on main), `rows.pack.json`
  `ac0cea0a649262908c75ad6fc246df1f4c76b6e5`,
  `skeleton.json` `156c8cbe2899fe62a29d08830ae4c0746a8e3458`. Local
  working copy sha256 matches main's blob content (valtree
  `hit_frames.json` sha256 `7bfd091b378e3796…` == main's). Bank-side
  evidence (Job 1 profiles, Job 3/4 candidates) applies cleanly to current
  main.
- Cited-row profile cross-check (Job 1 vs hit_frames, button/throw/active):
  rows 36, 54, 55, 56, 72, 73, 74, 264, 135, 196, 37, 127, 233, 234, 277,
  415, 478, 482 — 18/18 MATCH (the three throw rows 415/478/482 carry
  active None in Job 1 with HF active [0, 0] and throw flag agreeing).
  No cited row mismatches; nothing suspended on profile grounds.
- Main pantera.json blob UNCHANGED since Batch 2's fetch (sha256
  `a3f76a0d65ad0ed7cadc9cf7bb25c435c2d25a8a05aa8615e794d6bac0d62a8b`),
  so the re-baseline below stands on current main even though main itself
  moved (15c63a89).

## Re-baseline (Batch 1 section-0 rule, per prefix move)

Every Batch 3 step prefix compared #1099-file vs current main (main `moves/`,
else main quarantine). Result: **0 suspended**. Classes seen:
- `same` — identical row (or no row in either file).
- `damage-only` — damage value differs, row identical. NOT suspending:
  damage is not animation. (Prefixes: `3` 15→33, `d/f+4` 8→13,
  `u/b+1` 7→40. The `3` and `d/f+4` rows still verify/review as below;
  plans govern clip resolution only, never damage.)
- `anim_ref-changed (T8/T7 source; row N/A)` — the #1039 footprint:
  #1099 `t8:king:*` vs main `UNMAPPED:t7-clip-pending` (kept playable).
  NOT suspending: no T3 row exists in either file, so no T3 candidate is
  stale. (Prefixes: `b+1`, `b+2`, `b+1,4`, `b+2,4`, `d+1+3`.) These steps
  get candidates only via recorded path / Job 3 / Job 4; their CORRECT
  clips come from #988 Step 2 (original T8 refs), never from a T3 row
  recorded as correct.
- `no-1099-move` — prefix absent from #1099 moves (`u+1`): no candidate
  by construction, not drift. (The `u/f+1` and `u/b+1` singles exist; the
  bare `u+1` single does not.)
No prefix move changed its `t3_row` between #1099 and main, so no step is
SUSPENDED-DRIFT in Batch 3.

## Canonical step table (17 planned strings, 36 steps: 10 verified / 2 review / 24 unmapped)

| String | Steps (verified row, else status) | String status |
|---|---|---|
| `1+3,1` | 1+3 = UNMAPPED (cand 127: button 3 ≠ bits 5, throw row) \| 1 = UNMAPPED (cand 415: button 0, throw row, airborne) | unmapped-all |
| `1+4,1` | 1+4 = UNMAPPED (no candidate) \| 1 = UNMAPPED (cand 233: button 0, airborne) | unmapped-all |
| `1+4,1,1` | 1+4 = UNMAPPED \| 1 = UNMAPPED (cand 233) \| 1 = UNMAPPED (cand 234: button 0, airborne) | unmapped-all |
| `3,2` | 3 = row 264 VERIFIED (prefix-move own row) \| 2 = UNMAPPED (no candidate: string T8-sourced, no t3_row) | partial |
| `3,2,2` | 3 = row 264 VERIFIED \| 2 = UNMAPPED \| 2 = UNMAPPED | partial |
| `AB1.2,4,2+4` | CSV-ONLY (throw class): all steps unmapped, grapple-chain reasons, NO plan | (no plan) |
| `JGS.3,2+3` | JGS.3 = UNMAPPED (no candidate: stance-transition single has no t3_row) \| 2+3 = UNMAPPED (no candidate: string T8-sourced) | unmapped-all |
| `b+1,4` | b+1 = UNMAPPED (no candidate: T8 single, #1039 footprint) \| 4 = UNMAPPED (no candidate) | unmapped-all |
| `b+2,4` | b+2 = UNMAPPED \| 4 = UNMAPPED | unmapped-all |
| `d+1+3,1` | d+1+3 = UNMAPPED (no candidate: T8 single, #1039 footprint) \| 1 = UNMAPPED (cand 478: button 0, throw row, airborne) | unmapped-all |
| `d/b+1+3,1` | d/b+1+3 = UNMAPPED (cand 277: button 5 matches, but throw row) \| 1 = UNMAPPED (cand 482: button 0, throw row) | unmapped-all |
| `d/f+4,2` | d/f+4 = REVIEW cand row 135 (SOFT proxy fail, see below) \| 2 = REVIEW cand row 196 recorded-dest (SOFT proxy fail, see below) | review-only |
| `u+1,3` | u+1 = UNMAPPED (no candidate: bare u+1 single does not exist) \| 3 = row 54 VERIFIED (SOFT waived, jump context) | partial |
| `u+1,4` | u+1 = UNMAPPED \| 4 = row 72 VERIFIED (SOFT waived) | partial |
| `u/b+1,3` | u/b+1 = UNMAPPED (cand 37: button 3 ≠ bits 1; Job 3 soft candidates NOT wired) \| 3 = row 56 VERIFIED (SOFT waived) | partial |
| `u/b+1,4` | u/b+1 = UNMAPPED (cand 37) \| 4 = row 74 VERIFIED (SOFT waived) | partial |
| `u/f+1,3` | u/f+1 = row 36 VERIFIED (SOFT waived) \| 3 = row 55 VERIFIED (SOFT waived) | verified-all |
| `u/f+1,4` | u/f+1 = row 36 VERIFIED (SOFT waived) \| 4 = row 73 VERIFIED (SOFT waived) | verified-all |

Plan keys (49): canonical tallies above, plus twins inheriting canonical
steps. Plan-key steps: **102 = 35 verified / 2 review / 65 unmapped**.
Plan-key string statuses: 21 unmapped-all / 19 partial / 8 verified-all /
1 review-only. Verified-last-step keys: exactly the 24 jump-string keys
(6 canonical jump strings × 4 keys each). Verified-all keys: exactly the
8 `u/f+1,3` / `u/f+1,4` family keys.

### The verified steps

**`3,2` / `3,2,2` step 1 ← row 264** (prefix-move own row of the single
`3` move). HARD gates: button 4 == step bits 4 (LK3) ✓; throw 0 ✓;
stance standing for a standing-context step ✓. SOFT proxy: legL peakF 13
inside window [11, 15] (active [26, 26] / 2 ± 2) ✓; legL ext 0.550, dominant
legL. This is the single LK3 clip, gate-verified as the LK3 step — not the
Batch 2 donor verdict: Batch 2's `d/f+4,3` family never plays 264 as a
step, and this plan does not change any Batch 2 plan. The per-press path
uses the last step, so the final presses of `3,2`/`3,2,2` play NO bank row
(unmapped last steps) — only the whole-string chain path plays 264 for
step 1.

**Jump last steps ← rows 54, 72, 56, 74, 55, 73** (prefix-move own rows of
the full strings). HARD gates per step: button == step bits (54/55/56
button 4 = LK3; 72/73/74 button 8 = RK4) ✓; throw 0 ✓; stance jump /
starts-airborne for jump-context steps ✓. SOFT waived (Batch 1 precedent:
FK systematically silent on jumping rows) — the waiver is noted in each
step's reasons, not hidden. **Jump first step ← row 36** (`u/f+1,3` /
`u/f+1,4` step 1, prefix-move own row of the single `u/f+1` move): button 1
== bits 1 (LP1) ✓; throw 0 ✓; stance jump for jump context ✓; SOFT waived.
The `u+1` first steps have no candidate at all (bare `u+1` single absent)
and the `u/b+1` first steps fail on candidate 37 (button 3 ≠ bits 1) —
their plans are partial, not verified-all, and no soft substitute is wired
for them.

### The review steps: `d/f+4,2` (both steps)

Step 1 `d/f+4` ← row 135 (prefix-move row, same candidate as Batch 2's
`d/f+4,4` step 1): HARD gates pass (button 8 == bits 8 ✓; throw 0 ✓;
stance crouch for crouch-context ✓). SOFT proxy FAILS: legR peakF 4
outside window [6, 10] (active [16, 16] / 2 ± 2). Identical evidence to
Batch 2's review — same prefix, same candidate, same proxy fail — so the
step is REVIEW here too (candidate documented, row null), not verified
and not rejected. Step 2 `2` ← row 196 (recorded-dest): HARD gates pass
(button 2 == bits 2 ✓; throw 0 ✓; stance crouch for crouch-context ✓).
SOFT proxy FAILS: armR peakF 0 outside window [1, 5] (active [6, 6] / 2 ±
2). The proxy is conservative — a secondary arm peak inside [1, 5]
cannot be ruled out from the single max frame — so the step is REVIEW.
Job 2's string-level HARD limb verdict on `d/f+4,2` (own row 196) is NOT a
contradiction: a single row cannot satisfy a 2-hit string at string level;
the plan retires that verdict by holding 196 as an unplayed review
candidate for step 2 only. Play-verify cannot promote either step:
review steps play no bank row by design; promotion needs the full FK
threshold-crossing data (named unblock, not guessed here).

### Rejected candidates (notable; full reasons in the step table)

- Row 127 for `1+3` step 1: button 3 ≠ bits 5 (1+3) AND throw flag 1 — a
  1+2 throw row, not a 1+3 strike. Rejected on both gates.
- Rows 415 (`1+3,1` step 2), 233 (`1+4,1` step 2), 234 (`1+4,1,1` step 3),
  478 (`d+1+3,1` step 2), 482 (`d/b+1+3,1` step 2): button 0, throw flag 1,
  airborne (415/233/234/478) or duck-dip (482) — whole-string throw rows
  standing in for ground/crouch LP1 enders. All rejected; their Job 4
  joins (where present) are rejected with the same reasons, never promoted.
- Row 277 for `d/b+1+3` step 1: button 5 MATCHES bits 5 (1+3) but throw
  flag 1 — a matching-buttons throw row is still not a strike step.
  Rejected on the throw gate alone.
- Row 37 for `u/b+1` step 1: button 3 ≠ bits 1 — the single `u/b+1` move's
  own row is a 1+2-chord row, not the LP1 step. Rejected; the Job 3 soft
  alternatives (36/47/48/49) are documented, never wired (see Job 3).

## Job 3 — zero fills (9 pantera targets; 8 empty, 1 soft-only)

9 Batch 3 step prefixes are Job 3 targets: `d/f+4`, `u/b+1`, `d/f+4,2`,
`d+1+3`, `1+4,1`, `1+4,1,1`, `1+3,1`, `d+1+3,1`, `d/b+1+3,1`. EIGHT have
EMPTY pass-all lists in `job3.log` (e.g. `pantera d/f+4: top row 266,
pass-all: []`). ONE has candidates: `u/b+1` → pass-all [36, 47, 48, 49],
all SOFT-filed with FULL provenance (filed h / played m, jump→jump,
timing 1.11 — the same 4-way SOFT tie Batch 1 recorded). All four are
documented in the `u/b+1,3` / `u/b+1,4` step 1 reasons and NONE is wired:
SOFT candidates are never wired, and no SOFT fill is inherited from #1097
— the candidate set is the same set #1097 soft-wired for Batch 1's
`u/b+1,1` family (row 49), whose approval is still pending. If #1097's
Fill 2 is approved, a follow-up can align these steps; this PR does not
decide that, and its `u/b+1` first steps stay unmapped with row null.
Result: **0 Job 3 fills wired**. No verified step is contradicted by Job 3
(no verified step has a Job 3 candidate at all).

## Job 4 — six joins, all rejected (CORRECT method)

Correct join (pantera-only, BANK_DIR king→king_on_pantera_leoman, one row
per step; a candidate joins a step iff Job 2 has a pantera entry key ==
step prefix, row == candidate row, step == `own`): **6 Batch 3 steps
joined** — rows 415 (`1+3,1` step 2), 233 (`1+4,1` step 2; `1+4,1,1`
step 2), 234 (`1+4,1,1` step 3), 478 (`d+1+3,1` step 2), 482 (`d/b+1+3,1`
step 2). EVERY joined candidate is REJECTED on the step HARD gates
(button/throw/stance reasons above). A join never promotes by itself, so
zero joins change zero statuses. Orphans: **7** (rows 88, 96, 154, 230,
236, 248, 342 — identical to Batches 1–2 orphan sets). Row 220: joined to
Batch 1's `2,1` only; no Batch 3 exclusion triggered (no Batch 3 step
joins 220).

## CSV: `batch3_pantera_mixed.csv` (50 rows, Batches 1–2 style)

Current picks (Job 2 step + row): donor 10, own 40, anim 0. String-level
verdicts: HARD on 16 rows — HARD limb on the `1+3,1` / `1+4,1` /
`d+1+3,1` / `d/b+1+3,1` families (whole-string throw/jump rows for
ground/crouch LP1 enders) and on `d/f+4,2` (own row 196, retired to review
above); CLEAN-donor on the `3,2` / `b+1,4` / `b+2,4` / `JGS.3,2+3` rows
(INFO:fallback-clip only). 6 rows carry jump-clip-for-ground-move flags
(the `1+3,1` / `1+4,1` families + `d+1+3,1` — today's whole-string rows
are airborne for standing/crouch strings; the plans retire all of them).
Played profiles come from Job 1 King rows (stance/btn_limb-or-dominant/
level); pick definition is Job 2's audited resolution, not a runtime claim
— the engine's live resolution is verified by the play checklist below,
not by this CSV.

## T3 fallback log (PROCEDURAL_AUDIT.md Batch-3 entry)

Rows wired or held as candidates here are T3 FALLBACK, never the correct
mapping: verified rows 264 (`3,2`/`3,2,2` step 1), 36 (`u/f+1,3`/`u/f+1,4`
step 1), 54/72/56/74/55/73 (jump last steps); review candidates held
unplayed: 135 (`d/f+4` step 1), 196 (`d/f+4,2` step 2). Re-match all of
them to T7 King rows when T7 clip extraction lands (0x8000-bank bytes +
requirement codes unresolved). Rejected rows (127/415/233/234/277/478/482/
37) are NOT fallback — they are rejected evidence, not wired or held.
Rows 35/220 appear in NO Batch 3 plan step (verified or candidate) — the
Batch 1 ground-step exclusion holds here (both fail button for mixed steps
in any case).

## Play-verify checklist (parent browser delegation — NOT claimed here)

After #1096 + #1099 + this PR merge + deploy, on phone portrait, human
simulation (screenshot, look, scroll, tap — never selectors), Pantera vs
any fighter. Scope note (Batch 1 engine semantics): a plan governs the
STRING move's resolution and the whole-string chain path. The per-press
path fires one move per press, so an intermediate press resolves its
single move through the normal tiers (unchanged by this PR); only the
FINAL press of a string uses the plan's last step. The checks below are
scoped accordingly — "no row" means the string move's last step / the
chain step, not the intermediate single presses.
1. `3,2` / `3,2,2`: whole-string path step 1 plays row 264, feet grounded,
   standing LK3 — NOT donor row 99. Final press plays NO bank row
   (unmapped last step) — donor 99 must NOT play for the string move.
2. Jump families: `u/f+1,3` / `u/f+1,4` verified-all — first step plays
   row 36 (airborne LP1), final press plays 55/73 (airborne LK3/RK4).
   `u+1,3` / `u+1,4` / `u/b+1,3` / `u/b+1,4`: final press plays the
   last-step row (54/72/56/74, airborne kick); first step plays NO bank
   row (u+1 missing / u/b+1 candidate 37 rejected) — the old whole-string
   rows must NOT play for first steps, and no SOFT row (36/47/48/49) may
   appear for `u/b+1` first steps unless #1097's Fill 2 is approved and a
   follow-up wires it.
3. `d/f+4,2`: final press plays NO bank row (review last step);
   whole-string path plays NO bank row on any step (review + review) —
   the old own row 196 must NOT play for the string move.
4. Unmapped-all families (`1+3,1`, `1+4,1`, `1+4,1,1`, `b+1,4`, `b+2,4`,
   `d+1+3,1`, `d/b+1+3,1`, `JGS.3,2+3`): final press plays NO bank row;
   whole-string path plays NO bank row on any step — old donor rows
   216/264 and own throw rows 415/233/234/478/482 must NOT play for the
   string moves.
5. No plan step (chain step or string-move last step) plays rows 35 or 220
   under any input.
6. Batch 1 + Batch 2 strings still behave per #1096/#1099 (spot-check
   `2,1`: step 1 row 203, step 2 no row 220; `d/f+4,4`: final press row
   197) — Batch 3 adds keys only and must not disturb them.
If any check plays a donor/whole-string row for the string move, the plan
is wrong and the PR's step rows revert — play is the verdict, not this doc.
