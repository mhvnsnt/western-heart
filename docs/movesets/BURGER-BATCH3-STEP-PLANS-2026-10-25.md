# Burger Batch 3 — step plans (mixed-pair strings) — 2026-10-25

Button law: LP1 = Left Punch = Tekken 1, RP2 = Right Punch = Tekken 2, LK3 = Left Kick = Tekken 3, RK4 = Right Kick = Tekken 4.

> **Stack note:** this PR is stacked on burger Batch 2 (`feat/burger-batch2-step-plans-20261025`,
> PR #1104, head `4ffd320933455d2db36710abb9a6151c1ab6822d`), which stacks on burger Batch 1
> (`feat/burger-batch1-step-plans-20261025`, PR #1103, head `2c130b93720406a0f4cf6ebc6731f637e4abec11`),
> which stacks on #1096 (Batch 1 step-plan engine branch `feat/batch1-step-plans-pantera-20261024`).
> It does NOT stack on any Pantera plan branch (#1099/#1101/#1102): burger.json plans
> do not conflict with pantera.json plans, and this PR touches only burger.json
> (+ doc + tests + audit append). It merges AFTER burger Batch 2 (which merges after
> #1103, after #1096, itself blocked on 12 pre-existing test failures / a gate decision owed)
> and after a rebase onto main at that time. It does NOT include #1097's Pantera Batch 1
> follow-up fills (Pantera-specific, and its row-49 SOFT fill is still unapproved): no
> SOFT fill is inherited here. This PR does not touch `fighter.js`: #1096's merge onto
> post-#1078 main must reconcile #1078's `fighter.js` changes with #1096's engine branch,
> and that belongs to #1096's merge, not this PR. It does not touch pantera.json.
> Audit-append merge note: the Pantera stack and burger Batches 1–2 also append to
> `docs/anim/PROCEDURAL_AUDIT.md`; if any merges first, this branch rebases its audit
> append after their entries (never overwriting them) — the audit diff here is
> append-only against the Batch 2 branch base, so a rebase keeps all sections.
>
> **Test-evolution note (why the Batch 1 and Batch 2 test files are modified):** plans are
> cumulative in one `string_step_plans` block (88 Batch 1 + 67 Batch 2 + 49 Batch 3 = 204).
> The Batch 1 test's exact-155 / extra-keys assertions and the Batch 2 test's exact-155 /
> no-extra-keys assertions would fail on any cumulative tree, so this PR updates both files
> to cumulative assertions (total 204; extra keys exactly the documented Batch 3 49).
> Every Batch 1 and Batch 2 CONTENT assertion — flagships, verified-last-step sets,
> row/button checks — is preserved verbatim. This is not a weakening: it is the tests
> tracking the data they guard. (Batch 2's test-evolution note, same rule.)

## What this is

Burger Batch 3 of the locked batch order (Pantera first — complete across
#1096/#1099/#1101/#1102 — then burger, demonio, diablo, kinpo, phantom, scimitar,
skull; per character: Batch 1 LP1/RP2-only strings FIRST, then Batch 2 LK3/RK4-only,
then Batch 3+ mixed pairs). The same step-plan engine from #1096
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

Base file = the Batch 2 branch burger.json (552 moves, 107 strings entries;
its non-plan keys are proven identical to the #1096 file, so the universe
derived from the #1096 file applies unchanged). Canonical mixed-pair comma
keys in that file + main's strings list: **22 canonicals** — every step
carries buttons and the all-button union is exactly one punch + one kick
pair ({LP1,LK3}, {LP1,RK4}, {RP2,LK3}, {RP2,RK4}), any directionals.

- **Pure single-button: 22 canonicals** — every step is one button.
  **Chord-involved: 0 canonicals.** Burger carries no mixed-pair chord
  step (no `1+3`, `1+4`, `2+3`, `2+4` step) among its canonical comma
  keys: the mixed pairs here are sequences that alternate punch and kick
  across steps (e.g. `1,3`, `2,4`, `3,1`), not chords within a step.
  This is a measured property of burger's moveset, not a scoping
  assumption — a chord step with union {1,3} etc. would have been
  included by the filter.
- **Plan keys: 49 = 22 planned canonicals + 27 twins/variants**
  (`~t7.bob` / `~t7.bob.2` / `~t7.bob.3` / `~t7.bob.4` suffixes; twins inherit canonical
  steps verbatim, Batch 1 twin precedent). CSV rows: 49 (22 canonical +
  27 variants), pure first (all Batch 3 canonicals are pure, so the CSV
  is a single pure block).
- **Contexts over the 22:** 14 standing, 6 crouch, 1 jump (`ub+4,1`),
  1 ws (`WS.1,3`).
- **Provenance:** 17 canonical in current main moves/, 5 quarantined-only
  (in main's `t8_quarantine_20261024`, restored to playable by #988 Option B;
  their plans live on the Batch 2 base where the moves exist and become live
  when #988 merges: `3,1`, `3,1,1`, `3,2`, `BAL.1,H.4`, `ub+4,1`), 0 in #1096 only.
- **CSV-only, never planned: 0 canonicals.** No mixed-pair string carries
  a throw/grapple move class, and none carries a narrow grapple-chain label
  ({PILE_DRIVER, ARM_BREAKER, TACKLE} — Batch 3 rule). Every Batch 3
  canonical is a planned strike string.
- **Stored-spelling notes (Batch 1 precedent: keys are used exactly as
  stored, not merged):** `ws1,3` (no dot, T8-sourced) is a distinct stored
  key from `WS.1,3` (dotted); the Batch 1 context function classifies
  the undotted `ws1` spelling as standing, and that classification
  changes no Batch 3 outcome — both `ws1,3` steps are unmapped with no
  candidate regardless. `BAL.1,H.4` carries a BAL (balance?) stance
  prefix on step 1; its steps are unmapped with no candidate regardless.

## Bank correction (verified, not assumed — carried from Batches 1–2)

The original burger brief assumed burger's T3 bank was "bob" /
`bob_on_burger`. Batches 1–2 proved otherwise, and Batch 3 re-verifies it:

- burger.json: `t3_source: 'bryan'`, `t3_bank: 'moveset_bryan.json'`.
- `game/assets/anim/t3/` contains NO bob directory (22 banks).
- Job 1 / Job 2 / Job 4 banks for burger are all `bryan` (Job 1: 160
  bryan rows; Job 2: 552 burger entries, bank bryan; Job 4: 27 bryan
  candidates).
- Burger's T7 base IS Bob (roster base map Bob→Burger, T7 block
  burger→Bob) — but Bob has no T3 bank, because Bob did not exist in
  Tekken 3. The T3 fallback bank is BRYAN. All gates below run against
  bryan rows. This correction changes no user instruction (the user
  never specified the bank).

Bryan bank specifics (vs the king-bank precedent): bryan row 35 is
ABSENT from Job 1 profiles and from hit_frames; bryan row 220 exists in
hit_frames (`[25, 26, 65, 271, 0, 0]` — button 0) but not in Job 1, so it
fails every strike button gate. The explicit 35/220 rejection is kept
as belt-and-braces; the operative gates are stance + button + throw.
Bryan Job 1 carries a stance value king did not: `duck-dip` (6 rows:
157, 158, 166, 178, 179, 351). Duck-dip is handled like crouch:
STANCE-SOFT (review) for non-crouch contexts, pass for crouch
contexts — conservative, same as the crouch precedent; review, never
false verify. (One Batch 3 review step turns on duck-dip: `b+2,2,4` /
`b+2,2,4,4` step 1, row 158, below.)

## Gates per step (Burger Batches 1–2 gates, unchanged)

- Candidate = recorded path row (strings-list `t3_rows` full-path index,
  or dest-only for the last step) else prefix move's `t3_row` else none.
  Recorded paths in scope: exactly one — `2,4` → [182] (dest-only,
  last step). Every other Batch 3 candidate stands on a prefix-move row
  or on a Job 3 fill. Candidate sources over the 50 steps: 7
  prefix-move, 1 recorded-dest, 1 Job 3 fill, 41 none.
- HARD = button bitmask (LP1=1, RP2=2, LK3=4, RK4=8, chords OR-ed) + throw 0 for
  strike steps + stance (jump/starts-airborne fail ground steps, pass
  jump steps; crouch/duck-dip rows pass only crouch steps, else
  STANCE-SOFT review; ground rows fail all; ws→standing is review) +
  rows 35/220 rejected for ground steps.
- SOFT = Job 1 peakF proxy (window = stream active window / 2, ±2
  frames; chord steps need ≥1 limb peak in window), VALIDATED 13/13 on
  Pantera Batch 1's verified steps, conservative (proxy-fail = review,
  never false verify), waived for jump strings.
- Job 3 fills (exact-prefix rule: target key == step prefix): wired
  ONLY on exact level (filed == played, filed non-empty) + FULL
  provenance (row in job3.log provenance list AND top10 provenance
  non-empty) + step HARD gates + SOFT proxy pass (the Batch 1 fill-rule
  refinement, stricter than Pantera Batch 4's HARD-only fill rule —
  carried forward unchanged). Batch 3 wires ONE fill (see below).
- Job 3 dedupe note (Batch 2 cleanup, carried): prefix vs `__main`
  duplicate pass-all rows are deduped; adjudication reasons are not
  duplicated.
- Job 4 joins (CORRECT method only: burger-only, BANK_DIR bryan, one
  row per step, join iff Job 2 has a burger entry key == step prefix,
  row == candidate row, step == 'own'): a join NEVER promotes a step.
- Re-baseline per prefix move, #1096-file vs current main (moves else
  quarantine): row-changed → SUSPENDED (never wired on stale data);
  damage-only → noted, not suspending (damage is not animation);
  T8-sourced prefixes (no T3 row in either file) get candidates only
  via recorded path / Job 3 / Job 4, and their correct clips come from
  #988 Step 2 (original T8 refs), never from a T3 row recorded as
  correct.

## Tallies

- Planned-string steps (50 — all Batch 3 steps are planned-string steps):
  **8 verified / 4 review / 38 unmapped**.
- Planned canonical string_status: **1 verified-all / 9 partial /
  12 unmapped-all / 0 review-only**.
- Plan-key last-step: **3 verified / 1 review / 45 unmapped**
  (the 1 review last-step key is `2,4`; the other 3 review steps are
  first steps inside partials).
- Suspended-drift steps: **3** (all prefix move `3` — see below).
- Job 3 fills wired: **1**. Job 4 joined steps: **4**, none promoting.
  Orphans: **6** (same set as Batches 1–2 — Job 4 data unchanged).
- Main moves 502 + quarantine 50 = 552 = #1096 moves (burger's #1039
  quarantine count is 50, matching the Option B set).

## Verified steps (all gate-checked: hit_frames button == step bits, throw 0, never 35/220)

- `1,d+4` — verified-all: step 1 row 172 (prefix-move own row,
  button 1 = LP1, stance standing), step 2 row 119 (Job 3 fill —
  exact level filed l / played l, FULL provenance
  `['moveset_skull:4~t3.bryan.2(RK)']`, target `1,d+4`, timing 1.2,
  stance standing; SOFT limb-peak proxy passes: window [4.0, 8.0]
  (Job 1 active [12, 12] / 2 ± 2), legR peak 5 in window).
- First-step LP1 row 172 (prefix-move own row, button 1, stance
  standing) in `1,3`, `1,3,3`, `1,4`, and `1,d+4` (above).
- First-step RP2 row 100 (prefix-move own row, button 2, stance
  standing) in `2,4`.
- First-step `f+2` row 150 (prefix-move own row, button 2, stance
  standing) in `f+2,3`.
- First-step `ub+4` row 87 (prefix-move own row, button 8 = RK4,
  stance jump, jump context, SOFT waived) in `ub+4,1`.
- Verified-last-step plan keys (3): `1,d+4`, `1,d+4~t7.bob`,
  `1,d+4~t7.bob.2` (twins inherit canonical steps verbatim).
- Note the jump-context SOFT waiver (Batch 1 precedent: FK data is
  systematically silent on jumping rows): the 1 jump-context verified
  step (row 87) carries it. The 7 non-jump verified steps pass the
  SOFT limb-peak proxy outright (they are prefix-move own rows gated
  through the same path as Batches 1–2 verified steps, plus the one
  Job 3 fill whose SOFT proxy pass is documented above).

## Review steps (candidate documented, row null, never played)

- `2,4` step 2 — recorded-dest row 182 (button 8, throw 0, stance
  standing — HARD gates pass) is HELD at review: SOFT limb-peak
  proxy fail — window [9.0, 14.0] (Job 1 active [22, 24] / 2 ± 2),
  legR peak 2 outside the window. Row 182 also appears as a Job 4
  join on this step — documented as CANDIDATE (passes HARD gates,
  NOT wired — a join never promotes by itself). Job 3 candidates for
  prefix `2` (rows 101/105/106 exact ROW-ONLY, row 126 unknown /
  not-in-top10) are documented, never wired. Promotion needs full FK
  threshold-crossing data (named unblock, not guessed).
- `b+2,2,4` and `b+2,2,4,4` step 1 — prefix-move row 158
  (button 2, throw 0) is HELD at review: STANCE-SOFT duck-dip row
  for a standing-context step. Row 158 also appears as a Job 4 join
  on both steps — documented as CANDIDATE (passes HARD gates, NOT
  wired). No Job 3 candidate exists for prefix `b+2`. Promotion
  needs full FK threshold-crossing data (named unblock, not guessed).
- `b+4,1` step 1 — TWO separate reasons, neither wired:
  (a) gate candidate row 111 (prefix-move own row, button 8) is
  REJECTED: Job 1 stance `ground` (downed-foe row) for a standing
  step; (b) Job 3 exact+FULL candidate row 136 (filed m / played m,
  FULL provenance `['moveset_skull:b~t3.bryan.8(4/6+RK)']`, target
  `b+4`, timing 1.36, stance standing) passes HARD gates (button 8,
  throw 0, stance standing) but is HELD at review: SOFT limb-peak
  proxy fail — window [3.5, 8.0] (Job 1 active [11, 12] / 2 ± 2),
  legR peak 2 outside the window. This is the SAME row-136 evidence
  Batch 2 recorded for `b+4,3` / `b+4,4` step 1 — consistent, not a
  new disagreement. Row 111 also appears as a Job 4 join on this
  step — documented, REJECTED on the same ground-row reason, never
  promoting. Under the Batch 1 fill rule (SOFT proxy required for
  fills), a proxy-failing fill is review, never verified.

## Suspended steps (stale data documented, row null, never wired)

- `3,1` step 1, `3,1,1` step 1, and `3,2` step 1 — prefix move `3`
  is ROW-CHANGED (t3_row 65 on #1096 → None on current main). The
  stale candidate row 65 (prefix-move, button 4, stance jump) is
  documented, not wired. These are the 3 steps the Batch 1 note
  warned later batches to check — and they DO fall in Batch 3 scope
  (after Batch 2's `3,3` / `3,4`), so they ARE suspended.
- The other row-changed move, `b_c36_r65` (row 65 → None), was
  checked: NO Batch 3 string carries it as a prefix (it is a single
  coded move, not a string step), so it suspends nothing here.
- Note: row 65's Job 1 stance is `jump` — even absent the suspension,
  it would fail every ground step's stance gate (it is the jumping
  LK3 donor the CSV flags for ground strings). The suspension is
  belt-and-braces on top of a gate that already excludes it.

## Rejected / unmapped honesty

- **38 unmapped planned steps: 35 with NO candidate at all + 3
  suspended-drift (above). ZERO unmapped steps carry a rejected gate
  candidate.** The honest gap is missing rows, not wrong rows: the
  intermediate prefixes are T8-sourced strings with no T3 row (e.g.
  `1,3` step 2, `BAL.1`, `H.4`, `WS.1`, `ws1`, `d+2`, `d/f+3`,
  `FC.d/f+2` carry T8/T7-source anim_refs and `t3_row` null in both
  files). Their correct clips come from #988 Step 2 (original T8
  refs) or future extraction. No gate rejection was needed because
  there was nothing to reject.
- Per-canonical step table (canonical only; twins inherit verbatim):
  `1,3` row 172 | unmapped; `1,3,3` row 172 | unmapped | unmapped;
  `1,4` row 172 | unmapped; `1,d+4` row 172 | row 119
  (verified-all); `2,4` row 100 | review; `3,1`
  unmapped(suspended) | unmapped; `3,1,1` unmapped(suspended) |
  unmapped | unmapped; `3,2` unmapped(suspended) | unmapped;
  `BAL.1,H.4` unmapped | unmapped; `FC.d/f+2,4` unmapped |
  unmapped; `WS.1,3` unmapped | unmapped; `b+2,2,4` review |
  unmapped | unmapped; `b+2,2,4,4` review | unmapped | unmapped |
  unmapped; `b+4,1` review | unmapped; `d+2,3` unmapped |
  unmapped; `d+2,4` unmapped | unmapped; `d/f+3,1` unmapped |
  unmapped; `d/f+3,1,1` unmapped | unmapped | unmapped;
  `d/f+3,2` unmapped | unmapped; `f+2,3` row 150 | unmapped;
  `ub+4,1` row 87 | unmapped; `ws1,3` unmapped | unmapped.
- Job 3 (10 steps carry candidates; all adjudicated, only the one
  fill wired): `1,3` / `1,3,3` / `1,4` / `1,d+4` step 1 (prefix `1`):
  row 99 exact ROW-ONLY + rows 132/146/147/148 soft-filed ROW-ONLY —
  documented, never wired (gate-verified row 172 kept; ROW-ONLY and
  soft candidates never wire). `1,d+4` step 2: fill row 119
  exact+FULL (wired, above) + also-rans rows 121/131 exact ROW-ONLY
  (documented, not picked). `2,4` step 1 (prefix `2`): rows 101/105/
  106 exact ROW-ONLY + row 126 unknown (not in top10) — documented,
  never wired (gate-verified row 100 kept). `b+4,1` step 1: row 136
  exact+FULL HELD at review on SOFT proxy fail (above). `d+2,3` /
  `d+2,4` step 1 (prefix `d+2`): row 114 soft-filed ROW-ONLY + row 167
  exact ROW-ONLY — documented, never wired (no gate candidate;
  ROW-ONLY never wires). `d/f+3,2` step 2 (prefix `2`): row 167
  soft-filed ROW-ONLY — documented, never wired. No SOFT fill is
  inherited from #1097 (Pantera-specific, still unapproved).
- Job 4 (CORRECT join only): 4 joined steps — `2,4` step 2 row 182
  (CANDIDATE, not wired), `b+2,2,4` step 1 row 158 (CANDIDATE, not
  wired), `b+2,2,4,4` step 1 row 158 (CANDIDATE, not wired),
  `b+4,1` step 1 row 111 (REJECTED, ground row). A join never
  promotes a step by itself; zero joins change zero statuses.
  Orphans: 6 bryan candidates no burger Job 2 move carries (rows
  110, 157, 171, 200, 203, 207 — the same set as Batches 1–2, Job 4
  data unchanged). No row-220 exclusion triggered. The naive
  cross-fighter join on key-prefix equality is INVALID and was never
  used.

## Current picks (Job 2 audited resolution, burger_batch3_mixed.csv, 49 rows)

Donor-dominated — the whole-string resolution Batch 3 retires:

- **48 rows pick donor rows** (21 pick standing row 104, 14 pick
  JUMPING row 65, 10 pick standing row 172, 3 pick standing row 100)
  as the whole-string clip; **1 row picks its own row** (`2,4` →
  row 182 — whose step-2 plan entry is nonetheless review on SOFT
  proxy fail, so the plan plays NO row there; the CSV preserves the
  whole-string pick vs step pick distinction).
- **30 rows carry a HARD flag; 14 carry jump-clip-for-ground.**
  The sharpest wrong clips: jumping LK3 row 65 as the whole-string
  clip for ground strings (`d+2,3`, `f+2,3`, `ws1,3` and twins —
  the same jumping-LK3 donor Batch 2 flagged), and standing row 104
  as a whole-string clip for mixed strings it cannot represent
  (`b+2,2,4` family, `d+2,4` family). Note the distinction the CSV
  preserves: `1,d+4`'s whole-string Job 2 pick is donor 172, while
  its step-2 prefix carries the Job 3 fill row 119 (verified) — the
  whole-string pick and the step pick are different evidence, and
  the plan follows the step evidence.
- Donor→plan transition is the designed correction (Pantera +
  Batches 1–2 precedent): wiring a plan replaces single-row
  resolution wholesale, even for CLEAN donors, because one row
  cannot be correct for a multi-hit string.

## Re-baseline (Batch 1 section-0 rule, recomputed for Batch 3)

Per prefix move, #1096-file vs current main (moves else quarantine):

- **Main burger.json is unchanged since Batches 1–2's baseline.**
  Current main is `a4b78e2acc04270232b36b574b6a33e7d7e67ed2` (the
  same tip Batch 2 confirmed); main's burger blob (`463730d7656e`,
  1,229,310 bytes) still stands.
- Full drift census over all 552 moves (#1096 vs main moves else
  quarantine): 230 same / 211 damage-only (drift_of class) / 109
  anim_ref-changed / 2 row-changed. Damage differs on 260 moves
  (259 with unchanged t3_row). **Counting reconciliation (Batch 1's
  "259" figure):** Batch 1's shorthand counted damage-differing
  moves with unchanged t3_row (259). Under the drift_of
  classification those 259 split into 211 damage-only (anim_ref
  unchanged) + 48 anim_ref-changed-with-damage-change; the 260th
  damage-differing move is one of the 2 row-changed moves. Both
  counts are true under their definitions; this doc reports both so
  the figures never silently disagree again.
- Damage-only drift does NOT suspend (damage is not animation) —
  that covers the #1039 MOD damage sync (e.g. burger LP1 11 → 7).
  Only the 2 row-changed moves suspend anything, and only prefix
  `3` falls in Batch 3 scope (3 steps, above). `b_c36_r65`
  suspends nothing here (checked, above).
- anim_ref-changed (109) is the T8/T7-source footprint (no T3 row in
  either file) — those steps get candidates only via recorded path /
  Job 3 / Job 4; their correct clips come from #988 Step 2
  (original T8 refs), never from a T3 row recorded as correct.

## Gap-1 re-verification (Pantera batches' method, replicated)

- Bryan bank files IDENTICAL on current main (`a4b78e2a`,
  API-confirmed via the contents API): hit_frames.json blob
  `7ffea6b998d6`, rows.pack.json blob `1e22a8832b2c`,
  skeleton.json blob `32d521db0921` — the same blobs Batches 1–2
  confirmed, unchanged by any intervening merge.
- Cited-row profiles (Job 1 bryan vs hit_frames, button/throw/
  active/hit): **10/10 MATCH** — rows 65, 87, 100, 111, 119, 136,
  150, 158, 172, 182 (all verified, review-candidate, Job 3, Job 4,
  and suspended rows). No mismatch suspends any fill.

## Wiring

`string_step_plans` in burger.json: Batch 1's 88 plans + Batch 2's 67
plans preserved DEEP-EQUAL (wire-script assertion), Batch 3's 49 plans
ADDED (disjoint keys, asserted), law EXTENDED (Batch 1 + Batch 2
paragraphs kept verbatim, Batch 3 paragraph appended — a Batch-2-only
law would misdescribe a 204-plan block; the law change is metadata
only, no Batch 1/2 plan entry changes). Formatter round-trip reproduces
the Batch 2 branch file byte-identically before changes; structural
diff proves all non-plan top-level keys identical, moves 552 /
strings 107 unchanged, total plans 204.

## Tests

- Minimal-tree `node --test`: **28 pass / 0 fail** (9 updated
  Batch 1 tests + 9 updated Batch 2 tests + 10 new Batch 3 tests:
  counts 552/107/204; Batch 3 keys exactly the documented 49 with
  Batch 1 + Batch 2 keys all present; Batch 3 verified rows non-null
  and never 35/220 with buttons in bryan hit_frames; review/unmapped
  row null; no soft flags; `1,d+4` flagship rows [172,119];
  `2,4` step 2 review row null; `b+2,2,4` step 1 review row null;
  `b+4,1` step 1 review row null; `3,1` step 1 suspended-drift row
  null; verified-last-step Batch 3 keys exactly the 3; Batch 1 +
  Batch 2 flagships undisturbed (`2,1` [152,153], `1,2,1+2`
  [172,null,132], `u/f+3+4,4` [61,183], `u/f+4,4` [183,183],
  `b+4,3` step 1 review null, `3,3` step 1 suspended-drift null);
  fighter.js step-plan markers present). `node --check fighter.js` OK.
- LIMITATION (honest): full 200-test suite comparison vs pristine
  main NOT run — no full current-main checkout exists on this box.
  Blast radius is confined by construction: no engine changes, no
  moves/strings changes, no Batch 1/2 plan changes (deep-equal
  proven), doc + tests + audit-append only. The suite comparison
  must be run before merge (CI will also cover it).

## Play-verify checklist (parent browser delegation, after #1096 + #1103 + #1104 + this PR merge + deploy + sync)

Phone portrait, human sim. Burger vs any fighter.

1. `1,d+4`: verified-all, rows 172/119 — step 1 LP1, step 2 RK4 low;
   the final press must NOT play donor row 172 as a whole-string clip.
2. `1,3` / `1,3,3` / `1,4`: step 1 row 172, later steps NO row.
   `2,4`: step 1 row 100, step 2 NO row (row 182 held on SOFT proxy
   fail — check the second press plays no bank row, not a mistimed kick).
   `f+2,3`: step 1 row 150, step 2 NO row. `ub+4,1`: step 1 row 87
   (jump context, airborne as filed), step 2 NO row.
3. `b+2,2,4` / `b+2,2,4,4`: step 1 NO row (duck-dip row 158 held).
   `b+4,1`: step 1 NO row (rows 111/136 both held, neither wired).
   `3,1` / `3,1,1` / `3,2`: step 1 NO row (suspended-drift).
4. Ground LK3-enders must NOT play jumping row 65 as a whole-string
   clip (`d+2,3`, `f+2,3`, `ws1,3` families). Mixed strings must NOT
   play standing row 104 as a whole-string clip.
5. No step plays rows 35/220 under any input.
6. Burger Batch 1 + Batch 2 spot-checks undisturbed: `2,1` rows
   [152,153]; `1,2,1+2` rows [172,null,132]; `1,1` / `1,2` / `1,2,2`
   step 1 row 172, later steps NO row; `b+1+2,1` / `b+2,1` step 1 NO
   row; TACKLE family unchanged (no plan); `u/f+3+4,4` rows [61,183];
   `u/f+4,4` rows [183,183]; `f+3,4` step 1 row 191, step 2 NO row;
   `4,3` family step 1 row 104, later steps NO row; `b+4,3` /
   `b+4,4` step 1 NO row; `3,3` / `3,4` step 1 NO row (suspended).
7. Quarantined-only strings (`3,1`, `3,1,1`, `3,2`, `BAL.1,H.4`,
   `ub+4,1`) behave per plan ONLY after #988 merges — before that,
   their moves are not on main's playable surface, and their plans
   are inert.

NOT play-verified: no fight played. Nothing here is 'fixed' until
the user plays it.

## Merge order

This PR lands AFTER burger Batch 2 (#1104) merges; rebase onto main
before merging this PR. #1104 lands AFTER #1103 merges; #1103 lands
AFTER #1096 merges; #1096 is itself blocked on 12 pre-existing
failures / a gate decision owed — this lane does not fix those and
does not merge on mergeable:true alone (green + clean + git_merge.py
only). If #1097 merges first, note its guard-map interaction in the
merge (burger has its own guard map; Pantera's SOFT decision does not
transfer). If the Pantera plan stack (#1099/#1101/#1102) merges first,
rebase this branch's audit append after their audit entries (never
overwrite them) — the audit diff here is append-only against the
Batch 2 branch base. fighter.js: this PR does not touch it; #1096's
merge onto post-#1078 main must reconcile #1078's fighter.js changes
with #1096's engine branch — that reconciliation belongs to #1096's
merge, not this PR. No deploy, no gh-pages push from this lane.
