# Pantera Batch 4 — step plans (triples/quads/rest strings) — 2026-10-25

Button law: LP1 = Left Punch = Tekken 1, RP2 = Right Punch = Tekken 2, LK3 = Left Kick = Tekken 3, RK4 = Right Kick = Tekken 4.

> **Stack note:** this PR is stacked on #1101 (Batch 3 step-plan branch
> `feat/batch3-step-plans-pantera-20261025` @ `a3570ca59f327fe8d0bc1caf7e00d3b360fdd35a`).
> Plans accumulate: #1096 (engine) → #1099 (Batch 2) → #1101 (Batch 3) →
> this Batch 4. It merges AFTER #1101 (which merges after #1099, which
> merges after #1096, itself blocked on 12 pre-existing test failures /
> a gate decision owed) and after a rebase onto main at that time. It is
> NOT stacked on #1097 (which carries the unapproved SOFT row-49 fill):
> Batch 1 tallies below are #1096's record, Batch 2 are #1099's, Batch 3
> are #1101's, NOT #1097's updated tallies. If #1097 merges first, this
> branch rebases onto the merged state and the Batch 1 guard map in
> `game/tests/batch4-step-plans.test.mjs` must be updated to #1097's Batch 1
> statuses (b+2,1+2 family → verified, u/b+1,1 and u/b+1,2 first steps →
> verified-SOFT). This PR does not touch `fighter.js`: #1096's merge onto
> post-#1078 main must reconcile #1078's `fighter.js` changes with #1096's
> engine branch, and that belongs to #1096's merge, not this PR.

## What this is

Batch 4 of the locked batch order (Batch 1 LP1/RP2 → Batch 2 LK3/RK4 →
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

Base file = #1101 branch pantera.json (874 moves, 81 strings entries).
Canonical comma keys in that file: **240**. Batches 1–3 covered every
canonical whose steps all carry buttons and whose button union has size
≤ 2 (B1: ⊆ {LP1,RP2}; B2: ⊆ {LK3,RK4}; B3: exactly one punch + one kick).
This batch covers **everything else — 158 canonicals**:

- **Triples/quads: 95 canonicals** — every step carries buttons and the
  button union spans 3–4 distinct buttons (incl. 3-button chords such as
  `1+2+3`, `1+2+3+4`, and the long 10-hit strings `f+2,1,1,2,4,4,4,1,3`
  and `f+2,1,1,3,3,4,3,2,1+2,1`). 18 pure single-button, 77 chord-involved
  (by the Batch 1/2/3 pure definition over the 95; the 158-key total is
  18 pure + 140 chord-involved because rest keys count as chord-involved
  when any step is buttonless or multi-button).
- **Rest: 63 canonicals** — at least one step carries no button: dash /
  movement / stance-prefix sequences (`f,F+1`, `f,f,n,2`, `n,d/f,f+1,1`,
  `UT,1+2`, `WALL.b,b,u/b`, `ss2+4,b/db`, `uf,n,4`, …). These are NOT
  multi-hit attack strings in the step-plan sense: their non-attack steps
  have no attack row. They are CSV-audited only, never planned — planning
  them would need engine support for non-attack prefix steps, which is
  future work, not guessed here.

Plan keys: **72 = 65 planned canonical triples/quads + 7 twins/variants**
(`~t7.king` / `~t3.king` suffixes; twins inherit canonical steps verbatim
with canonical prefixes, Batch 1 twin precedent). CSV rows: **203**
(158 canonical + 45 variants). Contexts over the 158: 130 standing,
25 crouch, 3 jump.

CSV-only canonicals (93 = 30 triple-quad + 63 rest), never planned:

- Throw class (28 triple-quad): `1,2,1,2+4`, `1,2,1,d+2+4`, `1,2,2+4`,
  `1,2,d+2+4`, `3+4,1+4`, `AB1.2,1,1+3`, `AB2b.3,4,3+4,1+2`,
  `AB2c.1,3,4,2,1+2`, `AB2c.2,1,3,1+2`, `BT.3,&amp;#58;1+2`, `DHH.2,1,3,4`,
  `MMD1.1,4,2,3`, `MMD2.1,1+3/ MMD2.2,2+4`,
  `MMD3.1+2,1,1+3/ MMD3.1+2,2,2+4`, `MMD3.2,3,1,1+2`, `MMD4.3+4,1+2`,
  `MMD5.1+2,3,1+3/ MMD5.1+2,4,2+4`, `MMD5.1+2,4,2,1+2`,
  `MMD6.2,4,3,1,1+3/ MMD6.2,4,3,1,2+4`, `PD.1+2,3,4,1+2`,
  `SHH1.1+2,1,3`, `SHH1.2,1,1+3`, `SHH2c.3,4,1+2,3+4`, `b+1+2,1+3`,
  `b+1+2,2+4`, `b+1+2,3+4`, `b+3,&amp;#58;1+2`, `f+3,1+2`.
- Grapple label (2 triple-quad, move_class string but first-step label in
  the Batch 1 known grapple-chain set {PILE_DRIVER, ARM_BREAKER, TACKLE}):
  `ARM_BREAKER.1+2,4,2+4`, `PILE_DRIVER.1+2,3,4,1+2`.
- Rest (63): all movement/stance sequences listed above.

Other throw-named chains with move_class `string` (BACKDROP, POWER_BOMB,
COBRA_CLUTCH, GERMAN_SUPLEX, VICTORY_BOMB, SLEEPER, STANDING_HEEL_HOLD,
etc.) ARE planned under the narrow Batch 3 label rule — but their steps
fail the strike HARD gates (throw flag) and land unmapped, never wired
as strikes. That is the documented consequence of the narrow rule, not a
silent promotion of throws to strikes.

Provenance: 126 canonical in current main `moves/`, 32 quarantined-only
(in main's `t8_quarantine_20261024`, restored to playable by #988
Option B; their plans live on the #1101 base where the moves exist and
become live when #988 merges), 0 in #1101 only. This PR does not touch
the quarantine section.

## Gates (per step candidate, in order)

1. Candidate source: recorded path row (`strings[].t3_rows` full-path, or
   dest-only for the last step), else the prefix move's `t3_row`, else none.
   Recorded paths are NOT trusted blindly: a recorded row still faces
   every gate below.
2. HARD gates (fail = `unmapped`, candidate documented): button bitmask
   (`hit_frames.json` button field == step chord bits, LP1=1, RP2=2, LK3=4,
   RK4=8, chords OR-ed) + throw flag == 0 for strike steps + stance (see
   rule 4) + rows 35/220 rejected for ground steps always.
3. SOFT gate (fail = `review`, not played): Job 1 peakF proxy for the Batch 1
   FK gate — window = stream active window / 2, +/-2 frames; a step limb's
   Job 1 `peakF` inside the window passes. Chord steps: at least one limb
   peak in window. VALIDATED 13/13 on Batch 1's verified steps. The proxy
   is CONSERVATIVE: a max peak outside the window can hide a secondary
   peak inside — so proxy-fail means review, never a false verify. WAIVED
   for jumping-context strings (Batch 1 precedent); Batch 4's 2 jump
   verified steps carry the waiver noted in their reasons.
4. Stance gate: jump/starts-airborne rows fail ground-context steps and pass
   jump-context steps; crouch rows pass ONLY crouch-context steps; ground
   rows (downed-foe rows) fail all; ws-context steps matched to standing
   rows are review (ws→standing soft-stance, mirrors the Job 3 flag).
   Standing/duck-dip rows pass ground contexts (Batch 1 verified duck-dip
   rows for standing and crouch strings).
5. A gate-verified own/recorded candidate beats a disagreeing Job 3 candidate
   (own row is stronger file evidence); the disagreement is documented, not
   silently resolved. One such agreement occurs in Batch 4: Job 3
   exact+FULL row 110 agrees with the gate-verified step-1 row 110 of the
   two 10-hit strings — no disagreement to resolve.
6. Donor→plan transition (Batches 1–3 precedent, stated plainly): 138 of
   203 Batch 4 CSV keys play a DONOR row today (Job 2 step `donor`),
   61 play own rows, 4 play `match` rows. Wiring a plan replaces that
   single-row resolution wholesale — even for CLEAN-donor strings —
   because one row cannot be correct for a multi-hit string. An unmapped
   step plays NO bank row (procedural fallback + flag), never the old
   donor row. This is the designed correction, not a regression.
   Sharpest cases: `f,f,n,1+2` plays jumping row 35 today (HARD stance +
   jump-clip-for-ground-move) and gets NO plan (rest key); `uf,n,4` plays
   row 216 today (HARD stance) and gets NO plan (rest key); the 10-hit
   strings play donor rows today and their plans verify only the steps
   listed below.

## Tallies

Planned-string steps (292): **36 verified / 49 review / 207 unmapped**.
All steps (604, incl. CSV-only): 36 verified / 49 review / 519 unmapped.
Planned canonical string_status: **0 verified-all / 25 partial /
40 unmapped-all / 0 review-only**. Plan-key last-step: **12 verified /
6 review / 54 unmapped**. Verified-last-step plan keys (12):
`d+1+2,2,1,1,2,4`, `d+1+2,2,1,1,3`, `d+3+4,4,1,4`, `d+3+4,4,1,4,4`,
`d+3+4,4,1,4~t3.king`, `f+2,1,1,2,4,4,4,1`, `f+2,1,1,3`,
`f+2,1,1,3,3,4,3,2`, `f+2,1,1,3,3,4,3,2,1+2`,
`f+2,1,1,3,3,4,3,2,1+2~t3.king`, `u+1,2+4`, `u/b+1,2+4`.

## Wired fills (all VERIFIED, all prefix-move own rows or recorded-dest rows, no Job 3 fills)

| Step family | Verified rows |
|---|---|
| `1,2,1,1,2,4,4,4,1,3` step 1 (LP1) | row 110 (single LP1 move's own row: button 1, throw 0, standing) |
| `1,2,1,1,3,3,4,3,2,1+2` step 1 (LP1) | row 110 (same) |
| `d+1+2,2,1,1,2,4` / `d+1+2,2,1,1,3` / `d+1+2,2,1,1,3,3` steps 1–3 | rows 97 (d+1+2 chord, button 3) / 98 (RP2, button 2) / 198 (LP1, button 1) |
| `d+1+2,2,1,1,2,4` last step (RK4) | row 259 (recorded-dest; button 8, crouch-context step) |
| `d+1+2,2,1,1,3` / `d+1+2,2,1,1,3,3` last steps (LK3) | row 264 (recorded-dest for the 5-step string; prefix-move for the 6-step string; button 4) |
| `d+3+4,4,1,4` family steps 4–5 (RK4) | rows 212 / 214 (button 8) |
| `f+2,1,1,2,4,4,4,1` family step 8 (LP1) | row 262 (button 1) |
| `f+2,1,1,3` family step 4 (LK3) | row 264 (button 4) |
| `f+2,1,1,3,3,4,3,2` family steps 8 (RP2) / 9 (LP1+RP2) | rows 268 (button 2) / 269 (button 3) |
| `u+1,2+4` / `u/b+1,2+4` last steps (RP2+RK4) | rows 243 / 246 (button 10, jump context, SOFT waived with waiver noted) |

Row 264's dual role is NOT a contradiction: Batch 2 retired 264 as a
whole-string donor row for `d/f+4,3`-family strings, Batch 3 verified it
as the STEP row for the single LK3 step of `3,2`/`3,2,2`, and Batch 4
verifies it again as the STEP row for single LK3 steps — different
strings, different claims, each gate-checked. Row 259's dual role is
likewise contextual: verified as the recorded-dest last step of the
crouch-context `d+1+2` family, review-only as the prefix-move step of
the standing-context `f+2` family (crouch row for a standing step).

## Review steps (candidate documented, row null, never played)

- SOFT limb-peak proxy fails (single-limb peaks outside the window):
  row 257 (LP1 steps of the `d+1+2` and `f+2` families: peakF 9 outside
  [11,15]), row 258 (RP2 steps: peakF 5 outside [6.5,11.5]), row 196
  (`d+3+4,2` family RP2 step: peakF 0 outside [1,5] — the same evidence
  Batch 3 recorded for `d/f+4,2` step 2).
- STANCE-SOFT crouch rows for standing-context steps: rows 259, 260, 261
  (`f+2,1,1,2,4` family RK4 steps), rows 266, 267
  (`f+2,1,1,3,3,4,3` family RK4/LK3 steps). Promotion needs full FK
  threshold-crossing data (named unblock, not guessed).

## Rejected (all documented, none wired)

- Most unmapped planned steps (173 of 207) have NO candidate at all:
  their intermediate prefixes are T8-sourced strings with no T3 row
  (e.g. `1,2`, `1,2,1`, `f+2,1` carry `anim_ref` `t8:king:*` and
  `t3_row` null). Their correct clips come from #988 Step 2 (original
  T8 refs) or future extraction — never from a T3 row recorded as correct.
- 34 unmapped planned steps have a documented rejected candidate (button
  mismatch, throw flag, airborne/crouch/ground stance, or row 35/220
  exclusion); the step table records each reason verbatim.
- Job 4 joins (46 steps): all rejected on step gates (mostly whole-string
  throw rows: button 0, throw flag 1) or no-action on already-verified
  steps (rows 198, 257 noted as candidates that never promote). Orphans:
  7 (88, 96, 154, 230, 236, 248, 342 — identical to Batches 1–3). No
  row-220 exclusion triggered in Batch 4.

## Job 3 / Job 4 (CORRECT join only; a join never promotes)

Job 3: 10 pantera targets among Batch 4 prefixes; **0 fills wired**.
- The two 10-hit strings' step-1 Job 3 exact+FULL row 110 agrees with the
  gate-verified row 110 (no action needed).
- `u/b+1` (step 1 of `u/b+1,2+4`) carries the same 4-way SOFT tie Batch 1
  and Batch 3 recorded (rows 36/47/48/49, filed h / played m, jump→jump,
  timing 1.11) — documented, never wired, and no SOFT fill is inherited
  from #1097 (its row-49 fill for Batch 1's `u/b+1,1` family is still
  unapproved; if approved, a follow-up can align these steps — this PR
  does not decide that).
- `f,f,n,1+2` (rest key) step `1+2` carries an exact+FULL Job 3 row 143 —
  documented, never wired (rest keys get no plan).
- `f,n,d,D/F+4` (rest key) carries 5 soft-nofiled candidates — documented,
  never wired.
- CSV-only triple-quad keys' Job 3 candidates (exact+FULL row 110 for
  the `1,2,…` throw family step 1) are documented in `batch4_job3.json`,
  never wired (throw keys get no plan).

Job 4: 46 joined steps (CORRECT method only: pantera-only, BANK_DIR
king→king_on_pantera_leoman, join iff Job 2 has a pantera entry key ==
step prefix, row == candidate row, step == own). The naive cross-fighter
join on key-prefix equality is INVALID and was never used. Joined
candidates that pass HARD gates are documented candidates (row 257
noted), never wired.

## Gap-1 re-verification (Batches 1–3 method, replicated)

King bank files IDENTICAL #1101 branch vs current main 77b5a230
(hit_frames blob 7390cf4a4160…, rows.pack ac0cea0a6492…, skeleton
156c8cbe2899…, all API-confirmed). Local valtree hit_frames sha256 ==
main's, byte-identical. Cited-row profiles (Job 1 `hit` vs hit_frames,
button/throw/active): **70/70 MATCH** (all verified, review-candidate,
Job 3, and Job 4 rows). Re-baseline #1101 vs main: **0 SUSPENDED** (no
prefix changed its t3_row). Damage-only noted, not suspending (17 steps;
damage ≠ animation). anim_ref-changed = #1039 footprint (t8:king:* vs
UNMAPPED:t7-clip-pending for T8-sourced prefixes) — correct clips come
from #988 Step 2, never from a T3 row recorded as correct.
no-1101-move (251 steps) = movement prefixes and intermediate string
prefixes with no single-move entry — documented, not an error.

## Pantera string coverage: COMPLETE

With this batch, every canonical comma key in the #1101 base file is
either planned or CSV-audited — no Pantera string is unclassified:

| Batch | Planned canonicals | Plan keys | CSV-only canonicals |
|---|---|---|---|
| Batch 1 (LP1/RP2) | 34 | 60 | 15 (grapple/throw chains) |
| Batch 2 (LK3/RK4) | 15 | 27 | 0 |
| Batch 3 (mixed pairs) | 17 | 49 | 1 (`AB1.2,4,2+4`) |
| Batch 4 (triples/quads/rest) | 65 | 72 | 93 (30 throw/grapple + 63 rest) |
| **Total** | **131** | **208** | **109** |

131 + 109 = 240 canonical comma keys. "Complete" means classified +
planned-or-audited with file evidence per step — it does NOT mean every
step plays a verified row: across Batch 4's planned steps, 36 play a
verified row, 49 hold a review candidate unplayed, and 207 play NO bank
row (most awaiting #988 Step 2 T8 refs or future extraction). The next
work is filling those unmapped steps from real clips, not re-classifying
strings.

## Verification + limits

- Surgical diff proven (136 → 208 plans; law extended by the Batch 4
  addendum; all non-plan top-level keys identical; all 136 Batches 1–3
  plans identical; formatter round-trips the #1101 file byte-identically).
- Tests: minimal-tree `node --test` **12 pass / 0 fail** (counts 874/81/208;
  Batch 1 keys keep #1096 statuses; Batch 2 keys keep #1099 statuses;
  Batch 3 keys keep #1101 statuses; Batch 4 keys exactly 72; verified
  rows non-null and never 35/220; review/unmapped row null; no soft
  flags; `u+1,2+4`, `d+1+2,2,1,1,2,4`, `f+2,1,1,3,3,4,3,2,1+2`
  flagships; PILE_DRIVER + `f,F+1` no-plan; verified-last-set;
  hit_frames buttons; fighter.js markers). `node --check fighter.js` OK.
- Full 200-test suite comparison: NOT run (no full current-main checkout
  on this box); stated as a limitation here and covered by CI before
  merge. This PR merges only when clean + green.
- NOT play-verified (play handoff checks after merge + deploy + sync):
  each wired Batch 4 string played on phone portrait — feet grounded
  where the step is grounded, no step playing a jumping row for a ground
  step, no step playing rows 35/220 unless genuinely airborne; Batch 1 +
  Batch 2 + Batch 3 spot-checks undisturbed (3,2 step 1 row 264,
  u/f+1,3 rows 36/55, d/f+4,4 step 2 row 197).
