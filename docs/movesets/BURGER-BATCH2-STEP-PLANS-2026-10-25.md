# Burger Batch 2 — step plans (LK3/RK4-only strings) — 2026-10-25

Button law: LP1 = Left Punch = Tekken 1, RP2 = Right Punch = Tekken 2, LK3 = Left Kick = Tekken 3, RK4 = Right Kick = Tekken 4.

> **Stack note:** this PR is stacked on burger Batch 1 (`feat/burger-batch1-step-plans-20261025`,
> PR #1103, head `2c130b93720406a0f4cf6ebc6731f637e4abec11`), which stacks on #1096
> (Batch 1 step-plan engine branch `feat/batch1-step-plans-pantera-20261024`).
> It does NOT stack on any Pantera plan branch (#1099/#1101/#1102): burger.json plans
> do not conflict with pantera.json plans, and this PR touches only burger.json
> (+ doc + tests + audit append). It merges AFTER burger Batch 1 (which merges after
> #1096, itself blocked on 12 pre-existing test failures / a gate decision owed) and
> after a rebase onto main at that time. It does NOT include #1097's Pantera Batch 1
> follow-up fills (Pantera-specific, and its row-49 SOFT fill is still unapproved): no
> SOFT fill is inherited here, and Batch 2 wires ZERO Job 3 fills. This PR does not
> touch `fighter.js`: #1096's merge onto post-#1078 main must reconcile #1078's
> `fighter.js` changes with #1096's engine branch, and that belongs to #1096's merge,
> not this PR. It does not touch pantera.json. Audit-append merge note: the Pantera
> stack and burger Batch 1 also append to `docs/anim/PROCEDURAL_AUDIT.md`; if either
> merges first, this branch rebases its audit append after their entries (never
> overwriting them) — the audit diff here is append-only against the Batch 1 branch
> base, so a rebase keeps all sections.
>
> **Test-evolution note (why the Batch 1 test file is modified):** plans are
> cumulative in one `string_step_plans` block (88 Batch 1 + 67 Batch 2 = 155). The
> Batch 1 test's exact-88 / no-extra-keys assertions would fail on any cumulative
> tree, so this PR updates that file to cumulative assertions (total 155;
> extra keys exactly the documented Batch 2 67). Every Batch 1 CONTENT assertion —
> flagships, verified-last-step set, row/button checks — is preserved verbatim.
> This is not a weakening: it is the test tracking the data it guards. (Pantera's
> batches left their Batch 1 test's exact-count assertion in place while adding
> plans; this lane does not copy that latent break.)

## What this is

Burger Batch 2 of the locked batch order (Pantera first — complete across
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

Base file = the Batch 1 branch burger.json (552 moves, 107 strings entries;
its non-plan keys are proven identical to the #1096 file, so the universe
derived from the #1096 file applies unchanged). Canonical LK3/RK4-only comma
keys in that file + main's strings list: **33 canonicals** — every step
carries buttons and the all-button union is a subset of {LK3, RK4}, any
directionals.

- **Pure single-button: 23 canonicals** — every step is one button
  (LK3 or RK4 alone).
- **Chord-involved: 10 canonicals** — at least one step is a chord
  (LK3+RK4, written `3+4`), e.g. `4,3,3+4`, `WS.3,3+4`, `u/f+3+4,4`.
- **Plan keys: 67 = 33 planned canonicals + 34 twins/variants**
  (`~t7.bob` / `~t7.bob.2` / `~t7.bob.3` suffixes; twins inherit canonical
  steps verbatim, Batch 1 twin precedent). CSV rows: 67 (33 canonical +
  34 variants), pure first, then chord-involved.
- **Contexts over the 33:** 17 crouch, 11 standing, 4 jump, 1 ws
  (`WS.3,3+4`).
- **Provenance:** 25 canonical in current main moves/, 8 quarantined-only
  (in main's `t8_quarantine_20261024`, restored to playable by #988 Option B;
  their plans live on the Batch 1 base where the moves exist and become live
  when #988 merges: `3+4,4`, `3,3`, `4,3,4`, `4,4`, `b+4,3`, `df+4,3`,
  `df+4,4`, `ub+3+4,4`), 0 in #1096 only.
- **CSV-only, never planned: 0 canonicals.** No LK3/RK4-only string carries
  a throw/grapple move class, and none carries a narrow grapple-chain label
  ({PILE_DRIVER, ARM_BREAKER, TACKLE} — Batch 3 rule). Every Batch 2
  canonical is a planned strike string.
- **Stored-spelling notes (Batch 1 precedent: keys are used exactly as
  stored, not merged):** `db+4,4` and `d/b+4,4` (likewise `df+` vs `d/f+`,
  `ub+` vs `u/b+`, `uf+` vs `u/f+`) are distinct stored keys and stay
  distinct canonicals. `ws3,3+4` (no dot, T8-sourced, "Brioche Star",
  damage 17) is a distinct stored key from `WS.3,3+4` (dotted, damage 26);
  the Batch 1 context function classifies the undotted `ws3` spelling as
  standing, and that classification changes no Batch 2 outcome — both
  `ws3,3+4` steps are unmapped with no candidate regardless.

## Bank correction (verified, not assumed — carried from Batch 1)

The original burger brief assumed burger's T3 bank was "bob" /
`bob_on_burger`. Batch 1 proved otherwise, and Batch 2 re-verifies it:

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
false verify. (No Batch 2 step's outcome turns on duck-dip: the only
Batch 2 review steps turn on a ground row and a SOFT-proxy fail, below.)

## Gates per step (Burger Batch 1's gates, unchanged except the dedupe note)

- Candidate = recorded path row (strings-list `t3_rows` full-path index,
  or dest-only for the last step) else prefix move's `t3_row` else none.
  Recorded paths exist for NO Batch 2 string (the only recorded paths in
  main's strings list are `2,1` → [152,153], `2,1,2` → [152,153,151],
  `2,4` → [182] mixed, all out of scope); every Batch 2 candidate stands
  on a prefix-move row. Candidate sources over the 77 steps: 15
  prefix-move, 62 none.
- HARD = button bitmask (LK3=4, RK4=8, chords OR-ed) + throw 0 for
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
  carried forward unchanged). Batch 2 wires ZERO fills (see below).
- Job 3 dedupe note (Batch 2 cleanup, no outcome change): the Batch 1
  script looped targets `[prefix, prefix__main]`, and Job 3 carries
  identical pass-all rows under both keys, so Batch 1's job3 lists
  carried duplicates. Batch 2 dedupes identical (row, exactness,
  provenance) candidates, keeping the first — adjudication reasons are
  no longer duplicated. No status changes: the only duplicated
  candidate (b+4 row 136) is held at review either way.
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

- Planned-string steps (77 — all Batch 2 steps are planned-string steps):
  **11 verified / 2 review / 64 unmapped**.
- Planned canonical string_status: **2 verified-all / 9 partial /
  22 unmapped-all / 0 review-only**.
- Plan-key last-step: **7 verified / 60 unmapped / 0 review**
  (the 2 review steps are both first steps inside partials).
- Suspended-drift steps: **2** (both prefix move `3` — see below).
- Job 3 fills wired: **0**. Job 4 joined steps: **3**, none promoting.
  Orphans: **6** (same set as Batch 1 — Job 4 data unchanged).
- Main moves 502 + quarantine 50 = 552 = #1096 moves (burger's #1039
  quarantine count is 50, matching the Option B set).

## Verified steps (all gate-checked: hit_frames button == step bits, throw 0, never 35/220)

- `u/f+3+4,4` — verified-all: step 1 row 61 (prefix-move own row,
  button 12 = LK3+RK4 chord, stance jump, jump context, SOFT waived),
  step 2 row 183 (prefix-move own row, button 8 = RK4, stance jump,
  jump context, SOFT waived).
- `u/f+4,4` — verified-all: step 1 row 183 and step 2 row 183
  (prefix-move own rows, button 8 = RK4, stance jump, jump context,
  SOFT waived). The same row twice is what the files say: `u/f+4` and
  `u/f+4,4` both carry `t3_row` 183 — documented, not smoothed over.
- First-step RK4 row 104 (prefix-move own row, button 8, stance
  standing) in `4,3`, `4,3,3+4`, `4,3,4`, `4,4`.
- First-step `f+3` row 191 (prefix-move own row, button 4 = LK3, stance
  standing) in `f+3,4`.
- Last-step RK4 row 87 (prefix-move own row, button 8, stance jump,
  jump context, SOFT waived) in `ub+3+4,4`.
- Last-step RK4 row 183 (prefix-move own row, button 8, stance jump,
  jump context, SOFT waived) in `uf+3+4,4`.
- Verified-last-step plan keys (7): `u/f+3+4,4`, `u/f+3+4,4~t7.bob`,
  `u/f+3+4,4~t7.bob.2`, `u/f+4,4`, `u/f+4,4~t7.bob`, `ub+3+4,4`,
  `uf+3+4,4` (twins inherit canonical steps verbatim).
- Note the jump-context SOFT waiver (Batch 1 precedent: FK data is
  systematically silent on jumping rows): all 6 jump-context verified
  steps carry it. The 5 non-jump verified steps (rows 104 ×4, 191)
  pass the SOFT limb-peak proxy outright (they are prefix-move own
  rows gated through the same path as Batch 1's verified steps).

## Review steps (candidate documented, row null, never played)

- `b+4,3` and `b+4,4` step 1 — TWO separate reasons, neither wired:
  (a) gate candidate row 111 (prefix-move own row, button 8) is
  REJECTED: Job 1 stance `ground` (downed-foe row) for a standing
  step; (b) Job 3 exact+FULL candidate row 136 (filed m / played m,
  FULL provenance `['moveset_skull:b~t3.bryan.8(4/6+RK)']`, target
  `b+4`, timing per match_search) passes HARD gates (button 8,
  throw 0, stance standing) but is HELD at review: SOFT limb-peak
  proxy fail — window [3.5, 8.0] (Job 1 active [11, 12] / 2 ± 2),
  legR peak 2 outside the window. Under the Batch 1 fill rule
  (SOFT proxy required for fills), a proxy-failing fill is review,
  never verified. Promotion needs full FK threshold-crossing data
  (named unblock, not guessed). Row 111 also appears as a Job 4 join
  on both steps — documented, REJECTED on the same ground-row reason,
  never promoting.

## Suspended steps (stale data documented, row null, never wired)

- `3,3` step 1 and `3,4` step 1 — prefix move `3` is ROW-CHANGED
  (t3_row 65 on #1096 → None on current main). The stale candidate
  row 65 (prefix-move, button 4, stance jump) is documented, not
  wired. These are the 2 steps the Batch 1 note warned Batch 2 to
  check — and they DO fall in Batch 2 scope, so they ARE suspended.
- The other row-changed move, `b_c36_r65` (row 65 → None), was
  checked: NO Batch 2 string carries it as a prefix (it is a single
  coded move, not a string step), so it suspends nothing here.
- Note: row 65's Job 1 stance is `jump` — even absent the suspension,
  it would fail every ground step's stance gate (it is the jumping
  LK3 donor the CSV flags for ground strings). The suspension is
  belt-and-braces on top of a gate that already excludes it.

## Rejected / unmapped honesty

- **64 unmapped planned steps: 62 with NO candidate at all + 2
  suspended-drift (above). ZERO unmapped steps carry a rejected gate
  candidate.** The honest gap is missing rows, not wrong rows: the
  intermediate prefixes are T8-sourced strings with no T3 row (e.g.
  `3,4`, `d+3`, `d+4`, `d/b+4`, `d/f+3`, `WS.3`, `ws3`, `uf+3+4`,
  `ub+3+4` carry T8/T7-source anim_refs and `t3_row` null in both
  files). Their correct clips come from #988 Step 2 (original T8
  refs) or future extraction. No gate rejection was needed because
  there was nothing to reject.
- Per-canonical step table (canonical only; twins inherit verbatim):
  `3+4,4` unmapped | unmapped; `3,3` unmapped(suspended) | unmapped;
  `3,4` unmapped(suspended) | unmapped; `4,3` row 104 | unmapped;
  `4,3,3+4` row 104 | unmapped | unmapped; `4,3,4` row 104 |
  unmapped | unmapped; `4,4` row 104 | unmapped; `WS.3,3+4`
  unmapped | unmapped; `b+4,3` review | unmapped; `b+4,4` review |
  unmapped; `d+3,4` unmapped | unmapped; `d+4,3` unmapped |
  unmapped; `d+4,3,4` unmapped | unmapped | unmapped;
  `d/b+3+4,4` unmapped | unmapped; `d/b+4,4` unmapped | unmapped;
  `d/b+4,4,3` unmapped | unmapped | unmapped; `d/b+4,4,3,3`
  unmapped | unmapped | unmapped | unmapped; `d/b+4,4,4` unmapped
  | unmapped | unmapped; `d/f+3+4,4` unmapped | unmapped;
  `d/f+3,4` unmapped | unmapped; `d/f+3,4,4` unmapped | unmapped |
  unmapped; `db+3+4,4` unmapped | unmapped; `db+4,4` unmapped |
  unmapped; `db+4,4,3` unmapped | unmapped | unmapped;
  `db+4,4,3,3` unmapped | unmapped | unmapped | unmapped;
  `df+4,3` unmapped | unmapped; `df+4,4` unmapped | unmapped;
  `f+3,4` row 191 | unmapped; `u/f+3+4,4` row 61 | row 183
  (verified-all); `u/f+4,4` row 183 | row 183 (verified-all);
  `ub+3+4,4` unmapped | row 87; `uf+3+4,4` unmapped | row 183;
  `ws3,3+4` unmapped | unmapped.
- Job 3: burger targets adjudicated per step prefix; besides the
  `b+4` row 136 candidate (exact+FULL, HELD at review on SOFT proxy
  fail — above), NO other Batch 2 step prefix has a Job 3 pass-all
  candidate at all. No SOFT fill is inherited from #1097
  (Pantera-specific, still unapproved). Batch 2 wires zero fills.
- Job 4 (CORRECT join only): 3 joined steps — `b+4,3` step 1 row 111
  (REJECTED, ground row), `b+4,4` step 1 row 111 (REJECTED, ground
  row), `f+3,4` step 1 row 191 (no action, step already verified).
  A join never promotes a step by itself; zero joins change zero
  statuses. Orphans: 6 bryan candidates no burger Job 2 move carries
  (rows 110, 157, 171, 200, 203, 207 — the same set as Batch 1, Job 4
  data unchanged). No row-220 exclusion triggered. The naive
  cross-fighter join on key-prefix equality is INVALID and was never
  used.

## Current picks (Job 2 audited resolution, burger_batch2_lk_rk.csv, 67 rows)

Donor-dominated — the whole-string resolution Batch 2 retires:

- **36 rows pick donor row 104** (standing RK4) as the whole-string
  clip. Row 104 is a correct standing RK4 row — and it IS the
  verified step-1 row for the `4,·` family — but as a whole-string
  donor it still plays one row for a multi-hit string. Plans retire
  it as a whole-string clip; step 1 of `4,3` / `4,3,3+4` / `4,3,4` /
  `4,4` still plays row 104, now as a VERIFIED STEP row, with later
  steps playing NO row until real clips land.
- **18 rows pick donor row 65** (JUMPING LK3, Job 1 stance jump) as
  the whole-string clip for ground strings (`3,3`, `4,3`, `b+4,3`,
  `d+4,3`, `db+4,4,3`, `df+4,3`, and their twins) — HARD
  jump-clip-for-ground-move. 24 CSV rows carry the
  jump-clip-for-ground flag in total (row 65 enders + row 60 chord
  enders, below); 46 rows carry some HARD flag.
- **6 rows pick donor row 60** (JUMPING, Job 1 dominant armR) as the
  whole-string clip for ground chord strings (`4,3,3+4`, `WS.3,3+4`,
  `ws3,3+4` and twins) — a jumping ARM row for a ground KICK-chord
  ender: limb mismatch on top of the jump. This is Batch 2's sharpest
  wrong-clip case, the LK3/RK4 analogue of Batch 1's jumping row 41
  for 1+2 chord enders.
- **7 rows pick own rows** — only the jump strings (`u/f+4,4` +
  twin, `u/f+3+4,4` + 2 twins, `ub+3+4,4`, `uf+3+4,4`), whose own rows
  are the verified step rows above. Note the distinction the CSV
  preserves: `f+3,4`'s whole-string Job 2 pick is donor 104, while
  its step-1 prefix move `f+3` carries own row 191 (verified) — the
  whole-string pick and the step pick are different evidence, and
  the plan follows the step evidence.
- Donor→plan transition is the designed correction (Pantera +
  Batch 1 precedent): wiring a plan replaces single-row resolution
  wholesale, even for CLEAN donors, because one row cannot be
  correct for a multi-hit string.

## Re-baseline (Batch 1 section-0 rule, recomputed for Batch 2)

Per prefix move, #1096-file vs current main (moves else quarantine):

- **Main burger.json is unchanged since Batch 1's baseline.**
  Current main is `a4b78e2acc04270232b36b574b6a33e7d7e67ed2`; its
  parent is Batch 1's baseline main `5e1b900b`, and the intervening
  merge (PR #1074, Cape Jones arenas) touches no burger file (its
  11 files are arena/docs/config/test files). Batch 1's main burger
  blob (`463730d7656e`, 1,229,310 bytes) therefore still stands.
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
  `3` falls in Batch 2 scope (2 steps, above). `b_c36_r65`
  suspends nothing here (checked, above).
- anim_ref-changed (109) is the T8/T7-source footprint (no T3 row in
  either file) — those steps get candidates only via recorded path /
  Job 3 / Job 4; their correct clips come from #988 Step 2
  (original T8 refs), never from a T3 row recorded as correct.

## Gap-1 re-verification (Pantera batches' method, replicated)

- Bryan bank files IDENTICAL on current main (`a4b78e2a`,
  API-confirmed via the contents API): hit_frames.json blob
  `7ffea6b998d6`, rows.pack.json blob `1e22a8832b2c`,
  skeleton.json blob `32d521db0921` — the same blobs Batch 1
  confirmed on `5e1b900b`, unchanged by the intervening merge.
- Cited-row profiles (Job 1 bryan vs hit_frames, button/throw/
  active/hit): **8/8 MATCH** — rows 61, 65, 87, 104, 111, 136, 183,
  191 (all verified, review-candidate, Job 3, Job 4, and suspended
  rows). No mismatch suspends any fill.

## Wiring

`string_step_plans` in burger.json: Batch 1's 88 plans preserved
DEEP-EQUAL (wire-script assertion), Batch 2's 67 plans ADDED
(disjoint keys, asserted), law EXTENDED (Batch 1 paragraph kept
verbatim, Batch 2 paragraph appended — a Batch-1-only law would
misdescribe a 155-plan block; the law change is metadata only, no
Batch 1 plan entry changes). Formatter round-trip reproduces the
Batch 1 branch file byte-identically before changes; structural
diff proves all non-plan top-level keys identical, moves 552 /
strings 107 unchanged, total plans 155.

## Tests

- Minimal-tree `node --test`: **18 pass / 0 fail** (9 updated
  Batch 1 tests + 9 new Batch 2 tests: counts 552/107/155; Batch 2
  keys exactly the documented 67 with Batch 1 keys all present;
  Batch 2 verified rows non-null and never 35/220 with buttons in
  bryan hit_frames; review/unmapped row null; no soft flags;
  `u/f+3+4,4` flagship rows [61,183]; `u/f+4,4` flagship rows
  [183,183]; `b+4,3` step 1 review row null; `3,3` step 1
  suspended-drift row null; verified-last-step Batch 2 keys exactly
  the 7; Batch 1 flagships undisturbed (`2,1` [152,153],
  `1,2,1+2` [172,null,132]); fighter.js step-plan markers
  present). `node --check fighter.js` OK.
- LIMITATION (honest): full 200-test suite comparison vs pristine
  main NOT run — no full current-main checkout exists on this box.
  Blast radius is confined by construction: no engine changes, no
  moves/strings changes, no Batch 1 plan changes (deep-equal
  proven), doc + tests + audit-append only. The suite comparison
  must be run before merge (CI will also cover it).

## Play-verify checklist (parent browser delegation, after #1096 + #1103 + this PR merge + deploy + sync)

Phone portrait, human sim. Burger vs any fighter.

1. `u/f+3+4,4`: verified-all, rows 61/183 — a jump string; both
   steps airborne as the files say (NOT a ground string playing a
   jump row).
2. `u/f+4,4`: verified-all, rows 183/183 — same row twice, per the
   files; check it reads as two kicks, not a stuck pose.
3. `f+3,4`: step 1 row 191, step 2 NO row. `4,3` / `4,3,3+4` /
   `4,3,4` / `4,4`: step 1 row 104, later steps NO row.
4. `b+4,3` / `b+4,4`: step 1 NO row (rows 111/136 both held, neither
   wired). `3,3` / `3,4`: step 1 NO row (suspended-drift).
5. Chord enders (`4,3,3+4`, `WS.3,3+4`, `ws3,3+4`): the final press
   must NOT play jumping arm row 60. LK3-enders on ground strings
   must NOT play jumping row 65 as a whole-string clip.
6. No step plays rows 35/220 under any input.
7. Burger Batch 1 spot-checks undisturbed: `2,1` rows [152,153];
   `1,2,1+2` rows [172,null,132]; `1,1` / `1,2` / `1,2,2` step 1
   row 172, later steps NO row; `b+1+2,1` / `b+2,1` step 1 NO row;
   TACKLE family unchanged (no plan).
8. Quarantined-only strings (`3+4,4`, `3,3`, `4,3,4`, `4,4`,
   `b+4,3`, `df+4,3`, `df+4,4`, `ub+3+4,4`) behave per plan ONLY
   after #988 merges — before that, their moves are not on main's
   playable surface, and their plans are inert.

NOT play-verified: no fight played. Nothing here is 'fixed' until
the user plays it.

## Merge order

This PR lands AFTER burger Batch 1 (#1103) merges; rebase onto main
before merging this PR. #1103 lands AFTER #1096 merges; #1096 is
itself blocked on 12 pre-existing failures / a gate decision owed —
this lane does not fix those and does not merge on mergeable:true
alone (green + clean + git_merge.py only). If #1097 merges first,
note its guard-map interaction in the merge (burger has its own
guard map; Pantera's SOFT decision does not transfer). If the
Pantera plan stack (#1099/#1101/#1102) merges first, rebase this
branch's audit append after their audit entries (never overwrite
them) — the audit diff here is append-only against the Batch 1
branch base. fighter.js: this PR does not touch it; #1096's merge
onto post-#1078 main must reconcile #1078's fighter.js changes with
#1096's engine branch — that reconciliation belongs to #1096's
merge, not this PR. No deploy, no gh-pages push from this lane.
