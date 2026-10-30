# Burger Batch 4 — step plans (triples/quads/rest strings) — 2026-10-25

Button law: LP1 = Left Punch = Tekken 1, RP2 = Right Punch = Tekken 2, LK3 = Left Kick = Tekken 3, RK4 = Right Kick = Tekken 4.

> **Stack note:** this PR is stacked on burger Batch 3 (`feat/burger-batch3-step-plans-20261025`,
> PR #1105, head `7a768194591e76bd5f366c50287b43b34529608e`), which stacks on burger Batch 2
> (`feat/burger-batch2-step-plans-20261025`, PR #1104, head `4ffd320933455d2db36710abb9a6151c1ab6822d`),
> which stacks on burger Batch 1 (`feat/burger-batch1-step-plans-20261025`, PR #1103,
> head `2c130b93720406a0f4cf6ebc6731f637e4abec11`), which stacks on #1096 (Batch 1 step-plan
> engine branch `feat/batch1-step-plans-pantera-20261024`). It does NOT stack on any Pantera
> plan branch (#1099/#1101/#1102): burger.json plans do not conflict with pantera.json plans,
> and this PR touches only burger.json (+ doc + tests + audit append). It merges AFTER burger
> Batch 3 (which merges after #1104, after #1103, after #1096, itself blocked on 12 pre-existing
> test failures / a gate decision owed) and after a rebase onto main at that time. It does NOT
> include #1097's Pantera Batch 1 follow-up fills (Pantera-specific, and its row-49 SOFT fill is
> still unapproved): no SOFT fill is inherited here. This PR does not touch `fighter.js`: #1096's
> merge onto post-#1078 main must reconcile #1078's `fighter.js` changes with #1096's engine
> branch, and that belongs to #1096's merge, not this PR. It does not touch pantera.json.
> Audit-append merge note: the Pantera stack and burger Batches 1–3 also append to
> `docs/anim/PROCEDURAL_AUDIT.md`; if any merges first, this branch rebases its audit
> append after their entries (never overwriting them) — the audit diff here is
> append-only against the Batch 3 branch base, so a rebase keeps all sections.
>
> **Test-evolution note (why the Batch 1, Batch 2, and Batch 3 test files are modified):** plans are
> cumulative in one `string_step_plans` block (88 Batch 1 + 67 Batch 2 + 49 Batch 3 + 15 Batch 4 = 219).
> The earlier test files' exact-204 / extra-keys assertions would fail on any cumulative tree, so
> this PR updates all three files to cumulative assertions (total 219; extra keys exactly the
> documented Batch 4 15). Every Batch 1, Batch 2, and Batch 3 CONTENT assertion — flagships,
> verified-last-step sets, row/button checks — is preserved verbatim. This is not a weakening: it is
> the tests tracking the data they guard. (Batches 2–3 test-evolution notes, same rule.)
>
> **BURGER STRING COVERAGE COMPLETE (classification, not "every step verified"):** Batches 1–4
> together classify every canonical comma key in the Batch 3 base file: 159 canonicals = 104 planned
> (219 plan keys: Batch 1 40/88, Batch 2 33/67, Batch 3 22/49, Batch 4 9/15) + 55 CSV-only (Batch 1
> 3 TACKLE, Batch 2 0, Batch 3 0, Batch 4 52 rest). Proof: the union of the four batch universes
> equals the set of all canonical comma keys in the base file's moves + main's strings list
> (159 = 159, uncovered [], extra []). "Complete" does NOT mean every step plays a verified row:
> burger-wide planned steps are 39 verified / 10 review / 202 unmapped (251 total). The next work
> is filling unmapped steps from real clips, not re-classifying strings.

## What this is

Burger Batch 4 of the locked batch order (Pantera first — complete across
#1096/#1099/#1101/#1102 — then burger, demonio, diablo, kinpo, phantom, scimitar,
skull; per character: Batch 1 LP1/RP2-only strings FIRST, then Batch 2 LK3/RK4-only,
then Batch 3 mixed pairs, then Batch 4 triples/quads/rest). The same step-plan engine from #1096
(`game/js/fighter.js` `_attackClipPlan` step-plan branch + `_stepChain`) plus
`string_step_plans` data in `game/assets/movesets/burger.json`. A planned string
move plays per-STEP rows, never one row for the whole string. Only a step with
status `verified` plays its row. A `review`/`unmapped` step plays NO bank row —
the existing procedural fallback in `_animate` — and is flagged in
`_atkPlan.unmapped` with a `[WH-STEP-PLAN]` console line. Donor, match, and
generic tiers are bypassed for planned strings, so a planned string can never
silently donor-fall-back. No blend is added: step-to-step pose continuity is
UNPROVEN, and a blend ships only if play shows a snap.

## Universe (measured, not assumed)

Base file = the Batch 3 branch burger.json (552 moves, 107 strings entries;
its non-plan keys are proven identical to the #1096 file, so the universe
derived from the #1096 file applies unchanged). Batches 1–3 covered every
all-buttoned string with button-union size ≤ 2 (B1: subsets of {LP1,RP2};
B2: subsets of {LK3,RK4}; B3: the four mixed pairs). Batch 4 is everything
else, derived explicitly (the "rest" is open-ended, so deriving it explicitly
IS the scoping step): **61 canonicals** = 9 triples/quads + 52 rest.

- **Triples/quads (planned scope): 9 canonicals** — every step buttoned,
  button union of 3–4 distinct buttons: `2,1,4` (union {RP2,LP1,RK4}),
  `1+2+3+4,1+2` and `1+2+3+4,4` (union {LP1,RP2,LK3,RK4}, incl. a 4-button
  chord step), `3+4,4,2` (union {LK3,RK4,RP2}), `FC.d/f+2,4,1+2`
  (union {RP2,RK4,LP1}), `u+1+2,4` and `u/f+1+2,4` (union {LP1,RP2,RK4}),
  `u/f+2,3,3+4,4` (union {RP2,LK3,RK4}), and the 10-hit string
  `u/f+2,1,2,2,1,1+2,3,1,2,3+4` (union {RP2,LP1,LK3,RK4}).
- **Rest (CSV-audited only, never planned): 52 canonicals** — at least one
  buttonless step: dash sequences (`f,F+1+2`, `f,F+2`, `f,F+3`, `f,F+3+4`,
  `f,F+4`, `f,F+4,4`, `f,f,F`, `f,f,F+3`, `f,f,F+3+4`, `f,f,f+3`,
  `f,f,f+3+4`), crouch-dash sequences (`f,n,d,D/F`, `f,n,d,DF+4`,
  `f,n,d,DF+4,1+2`, `f,n,d,d/f+1`, `f,n,d,d/f+1+2`, `f,n,d,d/f+2`,
  `f,n,d,d/f+3`, `f,n,d,d/f+3,2`, `f,n,d,d/f+3,4`, `f,n,d,d/f+4`,
  `f,n,d,d/f+4,1+2`, `f,n,d,df`, `f,n,d,df+1`, `f,n,d,df+1+2`,
  `f,n,d,df+2`, `f,n,d,df+3`, `f,n,d,df+3,2`, `f,n,d,df+3,4`,
  `n,d/b,n,f+1+2`, `d,d/f,d,d/f+1+2`), backdash sequences (`b,B+1+4`,
  `b,B+1+4,2`, `b,B+2+3`, `b,B+3+4,2`, `b,B+3+4,D/B`, `b,B+4`, `b,f+1`),
  wall/balcony sequences (`(back to wall).b,b,UB`, `WALL.b,b,u/b`,
  `BAL.3+4,B`), stance/whiff sequences (`1+2,B`, `1+2,F`, `u+1+2,B`,
  `u+1+2,F`, `u/f+1+2,B`, `u/f+1+2,F`, `R.f+2+3,F`, `FC.d/f,d,d/f+1+2`,
  `d+1+2,2,1,D`, `d/b+4,4,4,D`, `uf,n,4`). Their non-attack steps have no
  attack row; planning them needs engine support for non-attack prefix
  steps — future work, named, not guessed. Rest keys get NO plan, so their
  current whole-string clips stand (documented in the CSV, not hidden) —
  this PR does not fix rest keys' clips.
- **Pure single-button: 1 canonical** (`2,1,4` — all steps single-button,
  union size 3). **Chord-involved: 60 canonicals.**
- **Contexts:** 47 standing / 9 jump / 5 crouch / 0 ws.
- **Provenance:** 54 in main moves / 7 quarantined-only (plans live on the
  Batch 3 base, go live when #988 merges: `(back to wall).b,b,UB`,
  `3+4,4,2`, `b,B+1+4`, `b,B+1+4,2`, `f,n,d,df+3,4`, `u+1+2,4`, `uf,n,4`)
  / 0 in #1096 only (all 61 canonicals are in the #1096 file).
- **CSV-only: 52 canonicals, ALL rest keys.** No throw/grapple-only
  canonicals in this scope — the 2 throw-class rest strings
  (`d,d/f,d,d/f+1+2`, `n,d/b,n,f+1+2`) are rest either way (dual reason,
  same outcome). No Batch 4 planned canonical carries a throw-named chain
  with move_class string (unlike Pantera Batch 4): all 9 planned canonicals
  are move_class `string`.
- **Disjointness vs Batches 1–3: asserted, no overlap.** The four batch
  universes partition the 159 canonical comma keys exactly (see the
  coverage-complete note above).
- **Plan keys: 15** (9 planned canonicals + 6 twins/variants inheriting
  steps verbatim: `2,1,4` → 3 variants, `FC.d/f+2,4,1+2` → 2 variants,
  `u/f+1+2,4` → 1 variant). **CSV rows: 79** (61 canonical + 18 variants:
  12 rest variants + 6 planned variants).

## Bank correction (verified, not assumed — carried from Batches 1–3)

Burger's T3 fallback bank is BRYAN, not bob. Evidence (Batch 1, re-verified
every batch): burger.json `t3_source: 'bryan'`, `t3_bank:
'moveset_bryan.json'`; `game/assets/anim/t3/` contains NO bob directory
(22 banks); Job 1/2/4 banks for burger are all bryan (Job 1: 160 bryan rows;
Job 2: 552 burger entries, bank bryan; Job 4: 27 bryan candidates). Burger's
T7 base IS Bob — but Bob did not exist in Tekken 3, so he has no T3 bank.
All gates ran against bryan rows. Bryan specifics: row 35 is ABSENT from
Job 1 + hit_frames; row 220 exists in hit_frames with button 0, failing
every strike button gate — so the 35/220 rejection is belt-and-braces, with
stance + button + throw as the operative gates. Bryan Job 1 also carries a
`duck-dip` stance (6 rows), handled like crouch: STANCE-SOFT (review) for
non-crouch contexts.

## Gates per step (Burger Batches 1–3 gates, unchanged)

Candidate = recorded path row (strings-list full-path index, or dest-only
for the last step) else prefix move's t3_row else none. HARD = hit_frames
button == step bits (LP1=1, RP2=2, LK3=4, RK4=8, chords OR-ed) + throw 0 for
strike steps + stance (jump/starts-airborne rows fail ground-context steps
and pass jump-context steps; crouch/duck-dip rows pass only crouch-context
steps, else STANCE-SOFT review; ground rows fail all; ws→standing is
review) + rows 35/220 rejected for ground steps. SOFT = Job 1 peakF proxy
(window = stream active window / 2, ±2 frames; chord steps need ≥1 limb peak
in window), VALIDATED 13/13 on Pantera Batch 1's verified steps,
conservative (proxy-fail = review, never false verify), waived for jump
strings (Batch 1 precedent: FK systematically silent on jumping rows).
Job 3 fills (exact-prefix rule): wired ONLY on exact level (filed ==
played, filed non-empty) + FULL provenance (row in job3.log provenance
list AND top10 provenance non-empty) + step HARD gates pass + SOFT proxy
pass (burger refinement, stricter than Pantera Batch 4's HARD-only fill
rule — carried from Batches 1–3; no Batch 4 fill exists to be affected by
the stricter rule either way). SOFT (soft-filed / soft-nofiled) and
ROW-ONLY candidates are documented, NEVER wired. A gate-verified
own/recorded candidate beats a disagreeing Job 3 candidate (own row is
stronger file evidence); the disagreement is documented, not silently
resolved. Job 4 joins (CORRECT method only: burger-only, BANK_DIR bryan,
join iff Job 2 has burger entry key == step prefix, row == candidate row,
step == own; prefix vs `__main` duplicate pass-all rows deduped, Batch 2
cleanup): a join NEVER promotes a step by itself. Orphans = bryan
candidates no burger Job 2 move carries (any step). T3 rows are FALLBACK
matches (docs/anim/PROCEDURAL_AUDIT.md Burger-Batch-4 entry), never the
correct mapping, to be re-matched to T7 Bob rows when decode lands.

## Tallies

- Planned-string steps (31): **5 verified / 0 review / 26 unmapped**.
- All steps (198): 5 verified / 0 review / 193 unmapped (167 rest steps +
  26 planned unmapped).
- Planned canonicals: **0 verified-all / 4 partial / 5 unmapped-all /
  0 review-only**.
- Plan-key last-step: **4 verified / 11 unmapped** (no review last steps).
- Verified-last-step keys (4): `u+1+2,4`, `u/f+1+2,4`, `u/f+1+2,4~t7.bob`,
  `u/f+2,3,3+4,4`.
- Job 3 fills wired: **0**. Job 4 joins: **0** (no Batch 4 prefix carries a
  bryan Job 4 candidate as an own row). Orphans: 6 (110, 157, 171, 200,
  203, 207 — identical to Batches 1–3). Row-220 exclusions: 0.
  Suspended-drift steps: **0**.

## Verified steps (all gate-checked: hit_frames button == step bits, throw 0, never 35/220)

- `2,1,4` step 1 (`2`, RP2) ← bryan row **100** (prefix-move own row:
  hit_frames [10,10,39,1042,0,2] — button 2 == RP2 bits, throw 0;
  Job 1 standing, active [10,10], level h; SOFT proxy passes outright:
  window [3.0,7.0], armR peakF 5 in window; drift damage-only).
- `2,1,4` step 2 (`1`, LP1) ← bryan row **153** (prefix-move own row:
  hit_frames [19,19,58,1042,0,1] — button 1 == LP1 bits, throw 0;
  Job 1 standing, active [19,19], level h; SOFT proxy passes outright:
  window [7.5,11.5], armL peakF 10 in window; drift damage-only).
  Note: rows 100/153 are the Batch 3 `2,4` step-1 row and the Batch 1
  `2,1` step-2 row respectively — same rows, different strings/claims,
  each gate-checked for this string. No contradiction: a row is verified
  per step, not per string globally.
- `u+1+2,4` step 2 (`4`, RK4) ← bryan row **183** (prefix-move own row:
  hit_frames [24,26,60,535,0,8] — button 8 == RK4 bits, throw 0;
  Job 1 jump, active [24,26], level m; SOFT gate waived, jump context,
  Batch 1 precedent noted; drift same).
- `u/f+1+2,4` step 2 (`4`, RK4) ← bryan row **183** (same row evidence as
  above; SOFT waived, jump context; drift damage-only).
- `u/f+2,3,3+4,4` step 4 (`4`, RK4) ← bryan row **183** (same row
  evidence; SOFT waived, jump context; drift damage-only).
  Note: row 183 is also Batch 2's `u/f+4,4` row (183/183) and Batch 3's
  `u/f+3+4,4` step-2 row — again, per-step verification, not a global
  claim. Every verified row's hit_frames button == its step bits and
  throw == 0; no verified row is 35 or 220.

## Review steps (candidate documented, row null, never played)

**None.** Batch 4 has zero review steps: every planned step is either
verified (5) or unmapped (26). No STANCE-SOFT holds, no SOFT-proxy holds,
no Job 3/Job 4 candidate holds at review in this batch.

## Suspended steps (stale data documented, row null, never wired)

**None.** No Batch 4 string carries prefix `3` or `b_c36_r65` as a step
prefix — the drift check ran over all 198 steps and the two row-changed
moves (see Re-baseline) suspend nothing here. (Batches 2–3 suspended
`3,3`/`3,4` and `3,1`/`3,1,1`/`3,2` on prefix `3`; Batch 4's `3+4,4,2`
carries prefix `3+4`, a different move, and is unmapped for lack of a
candidate, not suspended.)

## Rejected / unmapped honesty

**26 planned unmapped steps, ALL with NO candidate at all** — zero carry
a rejected gate candidate. Every one: recorded path + prefix move both
absent (their intermediate prefixes are T8-sourced strings with no T3
row, e.g. `1+2+3+4`, `3+4`, `FC.d/f+2`, `u+1+2`, `u/f+1+2`, `u/f+2` and
all 10-hit-string intermediate prefixes `u/f+2,1`, `u/f+2,1,2`, … carry
T8/T7-source anim_refs and `t3_row` null in both files). Their correct
clips come from #988 Step 2 (original T8 refs) or future extraction —
never from a T3 row recorded as correct. Job 3 candidates documented,
never wired (all fail the fill rule — soft, row-only, or rest-key):
`u/f+1+2` step 1: rows 41/42/43 soft-nofiled FULL (+ 53/54/55
soft-nofiled ROW-ONLY) — soft, never wired; `u/f+2` step 1 (both the
10-hit string and `u/f+2,3,3+4,4`): rows 60/61/62/96 soft-filed ROW-ONLY
— soft + row-only, never wired; `2,1,4` step 2: rows 101/105/106 exact
ROW-ONLY (+ 126 unknown/not-in-top10 ROW-ONLY) — row-only, never wired,
and the gate-verified row 153 stands; rest-key Job 3 candidates
documented in the step table but never wired because rest keys get no
plan at all: `f,n,d,d/f+4` family exact+FULL row 119 (+ exact ROW-ONLY
131), `1+2,B`/`1+2,F` exact ROW-ONLY 129, `d+1+2,2,1,D` soft-filed
ROW-ONLY 114 + exact ROW-ONLY 167, `d/b+4,4,4,D` exact ROW-ONLY 117.
Job 4: 0 joined steps, so no join adjudication arises; orphans 6
(identical to Batches 1–3: 110, 157, 171, 200, 203, 207).
Two rest strings carry move_class `throw` (`d,d/f,d,d/f+1+2`,
`n,d/b,n,f+1+2`) — they are CSV-only as rest keys regardless; the throw
class is a second reason, not a separate exclusion.

## Current picks (Job 2 audited resolution, burger_batch4_triples_quads_rest.csv, 79 rows)

Donor-dominated: **68 donor / 7 own / 4 match**. Verdicts: CLEAN 54 /
HARD stance 21 / HARD level 3 / HARD limb 1. Pick rows: 100 ×27, 104
×14, 41 ×8, 183 ×5, 65 ×4, 191 ×4, 61 ×4, 211 ×2, 150 ×2, 172 ×2,
96/178/146/149/129 ×1. Sharpest wrong clips (all ground strings):
jumping bryan row 41 (LP1+RP2 chord row) as the whole-string clip for
ground 1+2 enders (`f,n,d,DF+4,1+2`, `f,n,d,d/f+4,1+2`,
`FC.d/f+2,4,1+2`, `1+2+3+4,1+2` families); jumping row 65 (LK3) for ground
LK3 strings (`f,n,d,d/f+3`, `f,n,d,df+3`, `b,B+2+3` families); jumping
row 61 (3+4 chord row) for ground 3+4 chord enders (`f,f,F+3+4`,
`f,F+3+4`, `f,f,f+3+4` families); standing row 104 as a whole-string
clip for strings it cannot represent (`2,1,4`, `f,F+4`, `f,n,d,DF+4`
families — note `2,1,4`'s planned steps now play verified rows 100/153
for steps 1–2 and NO row for step 3, retiring donor 104 for that string).
Plans retire whole-string donors even where the row itself is
standing-correct (row 100 step 1s now play as VERIFIED STEP rows, later
steps play NO row). Rest keys' current picks stand (no plan): their
wrong clips are documented here, not hidden, and not fixed by this PR —
the unblock is engine support for non-attack prefix steps, not a plan.

## Re-baseline (Batch 1 section-0 rule, recomputed for Batch 4)

Every prefix move compared #1096-file vs current main (main moves, else
main quarantine). Full drift census over all burger moves, reported BOTH
ways (Batch 2 reconciliation — both counts true under their
definitions): **230 same / 211 damage-only / 109 anim_ref-changed /
2 row-changed**. Damage differs on **260 moves total, 259 with
unchanged t3_row** (the 1 remaining is row-changed move `3`, damage
15→14; the other row-changed move `b_c36_r65` is damage-unchanged
15→15). Batch 1's "259" was the damage-differs-plus-unchanged-row count;
"260" is the total. Damage-only drift is noted, NOT suspending (damage
is not animation). The 2 row-changed moves suspend NOTHING in Batch 4
scope (see Suspended). Main burger.json is unchanged since Batches
1–3's baseline (blob `463730d7656e`, 1,229,310 bytes, API-confirmed on
current main `00b07cf1`); the #1096 file is unchanged. Main moved
`a4b78e2a` → `00b07cf1` during this batch (13 commits, UI files only —
no burger file, no bank file touched; proven by compare, not assumed).

## Gap-1 re-verification (Pantera batches' method, replicated)

Bryan bank files IDENTICAL across the Batch 3 branch and current main
`00b07cf1` (hit_frames.json blob `7ffea6b998d6`, rows.pack.json blob
`1e22a8832b2c`, skeleton.json blob `32d521db0921`, API-confirmed on
main). Cited-row profiles (Job 1 vs hit_frames on button/throw/active):
**23/23 MATCH** (verified rows 100, 153, 183; Job 3 candidate rows 41,
42, 43, 53, 54, 55, 60, 61, 62, 96, 101, 105, 106, 114, 117, 119, 126,
129, 131, 167). Re-baseline 0 suspended (see above).

## Wiring

15 plan keys added to `string_step_plans` (204 → 219); Batches 1–3 law
verbatim + Batch 4 addendum; formatter round-trip reproduces the Batch 3
branch file byte-identically before changes; structural diff proves all
non-plan top-level keys identical and all 204 Batches 1–3 plans identical
(deep-equal). Moves 552 / strings 107 unchanged. No engine changed, no
moves/strings changed, no prior-plan changed, doc + tests + audit only.

## Tests

Minimal-tree `node --test` on all four burger test files: **38 pass /
0 fail** (9 updated Batch 1 + 9 updated Batch 2 + 10 updated Batch 3 +
10 new Batch 4) + `node --check fighter.js` OK. Tests assert: counts
552/107/219; Batch 4 keys exactly the documented 15 (plus Batches 1–3
keys all present, cumulative); Batch 4 verified steps carry rows (never
35/220, buttons in bryan hit_frames, throw 0), review/unmapped carry row
null, no soft flags; flagships `2,1,4` [100,153,null], `u+1+2,4`
[null,183], `u/f+1+2,4` [null,183], `u/f+2,3,3+4,4`
[null,null,null,183]; rest keys (`f,F+2`, `f,n,d,d/f+4`, `WALL.b,b,u/b`,
`f,f,F`, `b,B+1+4`, `uf,n,4`) have NO plan key; verified-last-step set
exactly the 4; fighter.js step-plan markers present. LIMITATION (honest):
full 200-test suite comparison vs pristine main NOT run — no full
current-main checkout exists on this box. Blast
radius is confined by construction: no engine changes, no moves/strings
changes, no prior-plan changes, doc + tests + audit only. The suite
comparison must be run before merge (CI will also cover it).
NOT play-verified: no fight played. Play checklist below (each wired
Batch 4 string on phone portrait — feet grounded where the step is
grounded, no step playing a jumping row for a ground step, no step
playing rows 35/220 unless genuinely airborne; Batches 1–3 spot-checks
undisturbed). Nothing here is 'fixed' until the user plays it.

## Play-verify checklist (parent browser delegation, after #1096 + #1103 + #1104 + #1105 + this PR merge + deploy + sync)

Phone portrait, human sim, Burger vs any fighter: (1) `2,1,4` rows
100/153, step 3 NO row; old whole-string donor 104 must NOT appear as a
whole-string clip. (2) `u+1+2,4` step 1 NO row, step 2 row 183 (airborne
as filed); `u/f+1+2,4` same; `u/f+2,3,3+4,4` steps 1–3 NO row, step 4 row
183. (3) `1+2+3+4,1+2` / `1+2+3+4,4` / `3+4,4,2` / `FC.d/f+2,4,1+2` /
the 10-hit string `u/f+2,1,2,2,1,1+2,3,1,2,3+4`: NO row on any step.
(4) Rest keys unchanged (no plan): `f,F+2`, `f,n,d,d/f+4` family,
`WALL.b,b,u/b`, `b,B+1+4` behave as before (donor clips), NOT per plan.
(5) No step plays rows 35/220. (6) Batches 1–3 spot-checks undisturbed
(`2,1` [152,153]; `1,2,1+2` [172,null,132]; `u/f+3+4,4` [61,183];
`u/f+4,4` [183,183]; `f+3,4` step 1 row 191, step 2 NO row; `4,3` family
step 1 row 104, later steps NO row; `b+4,3`/`b+4,4` step 1 NO row;
`3,3`/`3,4` step 1 NO row (suspended); `1,d+4` [172,119]; `2,4` step 1
row 100, step 2 NO row; `f+2,3` step 1 row 150, step 2 NO row; `ub+4,1`
step 1 row 87, step 2 NO row; `b+2,2,4` step 1 NO row; `b+4,1` step 1 NO
row; `3,1`/`3,1,1`/`3,2` step 1 NO row (suspended)). (7)
Quarantined-only strings (`3+4,4,2`, `u+1+2,4`, `f,n,d,df+3,4`,
`(back to wall).b,b,UB`, `b,B+1+4`, `b,B+1+4,2`, `uf,n,4`) behave per
plan ONLY after #988 merges.

## Merge order

Merges AFTER #1105 (which merges after #1104, after #1103, after #1096,
itself blocked on 12 pre-existing failures / a gate decision owed);
rebase onto main before merging; git_merge.py only when green + clean.
Audit append is append-only vs the Batch 3 base — rebase after
Pantera/Batch 1/2/3 audit entries if they merge first, never overwrite.
If #1097 merges first, note its guard-map interaction (burger has its
own guard map; Pantera's SOFT decision does not transfer).
