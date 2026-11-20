# Burger Batch 1 — step plans (LP1/RP2-only strings) — 2026-10-25

Button law: LP1 = Left Punch = Tekken 1, RP2 = Right Punch = Tekken 2, LK3 = Left Kick = Tekken 3, RK4 = Right Kick = Tekken 4.

> **Stack note:** this PR is stacked on #1096 (Batch 1 step-plan engine branch
> `feat/batch1-step-plans-pantera-20261024` @ `e2ae41432a207ea8e68453a3fe09d208ca05d8f4`).
> It does NOT stack on the Pantera plan branches (#1099/#1101/#1102):
> burger.json plans do not conflict with pantera.json plans, and this PR
> touches only burger.json (+ doc + test + audit append). It merges AFTER
> #1096 (itself blocked on 12 pre-existing test failures / a gate decision
> owed) and after a rebase onto main at that time. It does NOT include
> #1097's Pantera Batch 1 follow-up fills (Pantera-specific, and its row-49
> SOFT fill is still unapproved): no SOFT fill is inherited here, and
> burger has its own guard map (this test file), so #1097's decision does
> not transfer. This PR does not touch `fighter.js`: #1096's merge onto
> post-#1078 main must reconcile #1078's `fighter.js` changes with #1096's
> engine branch, and that belongs to #1096's merge, not this PR. It does
> not touch pantera.json. Audit-append merge note: the Pantera stack also
> appends to `docs/anim/PROCEDURAL_AUDIT.md`; if that stack merges first,
> this branch rebases its audit append after theirs (never overwriting
> their entries) — the audit diff here is append-only against the #1096
> base, so a rebase keeps both sections.

## What this is

Burger Batch 1 of the locked batch order (Pantera first — now complete
across #1096/#1099/#1101/#1102 — then burger, demonio, diablo, kinpo,
phantom, scimitar, skull; per character: Batch 1 LP1/RP2-only strings
FIRST, then Batch 2 LK3/RK4-only, then Batch 3+ mixed pairs). The same
step-plan engine from #1096 (`game/js/fighter.js` `_attackClipPlan`
step-plan branch + `_stepChain`) plus `string_step_plans` data in
`game/assets/movesets/burger.json`. A planned string move plays per-STEP
rows, never one row for the whole string. Only a step with status
`verified` plays its row. A `review`/`unmapped` step plays NO bank row —
the existing procedural fallback in `_animate` — and is flagged in
`_atkPlan.unmapped` with a `[WH-STEP-PLAN]` console line. Donor, match,
and generic tiers are bypassed for planned strings, so a planned string
can never silently donor-fall-back. No blend is added: step-to-step pose
continuity is UNPROVEN, and a blend ships only if play shows a snap.

## Universe (measured, not assumed)

Base file = #1096 branch burger.json (552 moves, 107 strings entries).
Canonical LP1/RP2-only comma keys in that file + main's strings list:
**43 canonicals** — every step carries buttons and the all-button union
is a subset of {LP1, RP2}, any directionals.

- **Pure single-button: 29 canonicals** — every step is one button
  (LP1 or RP2 alone).
- **Chord-involved: 14 canonicals** — at least one step is a chord
  (LP1+RP2, written `1+2`), e.g. `1,2,1+2`, `b+1+2,1`, `d+1+2,2,1`.
- **Plan keys: 88 = 40 planned canonicals + 48 twins/variants**
  (`~t7.bob` / `~t8.bob` suffixes; twins inherit canonical steps verbatim,
  Batch 1 twin precedent). CSV rows: 91 (43 canonical + 48 variants),
  pure first, then chord-involved.
- **Contexts over the 43:** 22 standing, 13 crouch, 5 jump, 3 ws
  (`WS.1,2`, `WS.2,1`, `WS.2,2`).
- **Provenance:** 34 canonical in current main moves/, 9
  quarantined-only (in main's `t8_quarantine_20261024`, restored to
  playable by #988 Option B; their plans live on the #1096 base where the
  moves exist and become live when #988 merges), 0 in #1096 only.
- **CSV-only, never planned (3 canonicals):** the TACKLE family
  (`TACKLE.1,1`, `TACKLE.1,1,1`, `TACKLE.1,1,1,1`) — first-step label in
  the narrow grapple set {PILE_DRIVER, ARM_BREAKER, TACKLE} (Batch 3
  rule). Their steps are strike-gate-excluded; throw-row verification
  for them is owed separately, not a step-plan.

## Bank correction (verified, not assumed)

The lane brief assumed burger's T3 bank was "bob" / `bob_on_burger`.
Verification against the repo and the GPU-job data proves otherwise:

- burger.json: `t3_source: 'bryan'`, `t3_bank: 'moveset_bryan.json'`.
- `game/assets/anim/t3/` contains NO bob directory (22 banks: anna,
  armorking, bosconovitch, bryan, eddy, forestlaw_on_law, gon, gunjack,
  heihachi, heihachi_on_jin, hwoarang, jin, julia,
  king_on_pantera_leoman, kuma, law, lei, nina, ogre, paul, xiaoyu,
  yoshimitsu).
- Job 1 / Job 2 / Job 4 banks for burger are all `bryan` (Job 1: 160
  bryan rows; Job 2: 552 burger entries, bank bryan; Job 4: 27 bryan
  candidates).
- Burger's T7 base IS Bob (roster base map Bob→Burger, T7 block
  burger→Bob) — but Bob has no T3 bank, because Bob did not exist in
  Tekken 3. The T3 fallback bank is BRYAN. All gates below run against
  bryan rows. This correction changes no user instruction (the user
  never specified the bank); it follows the brief's own rule to verify
  the bank from the layout, not guess it.

Bryan bank specifics (vs the king-bank precedent): bryan row 35 is
ABSENT from Job 1 profiles and from hit_frames; bryan row 220 exists in
hit_frames (`[25, 26, 65, 271, 0, 0]` — button 0) but not in Job 1, so it
fails every strike button gate. The explicit 35/220 rejection is kept
as belt-and-braces; the operative gates are stance + button + throw.
Bryan Job 1 carries a stance value king did not: `duck-dip` (6 rows:
157, 158, 166, 178, 179, 351). Duck-dip is handled like crouch:
STANCE-SOFT (review) for non-crouch contexts, pass for crouch
contexts — conservative, same as the crouch precedent; review, never
false verify.

## Gates per step (Pantera batches' gates, unchanged except noted)

- Candidate = recorded path row (strings-list `t3_rows` full-path index,
  or dest-only for the last step) else prefix move's `t3_row` else none.
  Recorded paths exist for only 3 main strings-list entries
  (`2,1` → [152,153], `2,1,2` → [152,153,151], `2,4` → [182] — the last
  is mixed, out of scope); everything else stands on prefix-move rows.
- HARD = button bitmask (LP1=1, RP2=2, chords OR-ed) + throw 0 for
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
  non-empty) + step HARD gates + SOFT proxy pass. The SOFT-proxy
  requirement on fills is STRICTER than Batch 4's documented fill rule
  (HARD gates only); no Batch 4 fill existed to be affected (Batch 4
  wired zero fills), and this batch's single fill passes the proxy
  anyway, so the stricter rule changes no outcome here — it is
  documented, not hidden.
- Job 4 joins (CORRECT method only: burger-only, BANK_DIR bryan, one
  row per step, join iff Job 2 has a burger entry key == step prefix,
  row == candidate row, step == 'own'): a join NEVER promotes a step.
- Re-baseline per prefix move, #1096-file vs current main (5e1b900b):
  row-changed → SUSPENDED (never wired on stale data); damage-only →
  noted, not suspending (damage is not animation); T8-sourced prefixes
  (no T3 row in either file) get candidates only via recorded path /
  Job 3 / Job 4, and their correct clips come from #988 Step 2
  (original T8 refs), never from a T3 row recorded as correct.

## Tallies

- Planned-string steps (93): **15 verified / 4 review / 74 unmapped**.
- All steps (102): 15 verified / 4 review / 83 unmapped (9 CSV-only
  TACKLE steps included in the 83).
- Planned canonical string_status: **2 verified-all / 13 partial /
  25 unmapped-all / 0 review-only**.
- Plan-key last-step: **8 verified / 80 unmapped** (no review
  last-steps: the 4 review steps are all first steps inside partials).
- Suspended-drift steps: **0** in scope. The only 2 row-changed moves
  between #1096 and main (`3`: row 65 → None; `b_c36_r65`: row 65 →
  None) are LK3-related, out of Batch 1 scope. Damage-only drift: 259
  moves (the #1039 MOD damage sync: e.g. burger LP1 damage 11 → 7) —
  noted, not suspending.
- Main moves 502 + quarantine 50 = 552 = #1096 moves (burger's #1039
  quarantine count is 50, matching the Option B set).

## Verified steps (all gate-checked: hit_frames button == step bits, throw 0, never 35/220)

- `2,1` — verified-all: step 1 row 152 (recorded-path, button 2),
  step 2 row 153 (recorded-path, button 1).
- `2,1,2` — verified-all: rows 152 / 153 / 151 (recorded-path,
  buttons 2 / 1 / 2).
- First-step LP1 row 172 (prefix-move own row, button 1) in `1,1`,
  `1,1,2`, `1,2`, `1,2,1+2`, `1,2,2`.
- First-step `d/f+1` row 146 (prefix-move own row, button 1) in
  `d/f+1,1+2`, `d/f+1,2`.
- First-step `f+2` row 150 (prefix-move own row, button 2) in
  `f+2,H.1+2`, `f+2,H.1+2,1`.
- `1,2,1+2` last step row 132 — the single Job 3 fill (exact level
  filed m / played m, FULL provenance
  `['moveset_skull:b~t3.bryan.4(4/6+LP+RP)']`, target `1,2,1+2`, timing
  1.0, standing; SOFT proxy also passes: window [3.0,7.5], armL peak 6).
  Exact ROW-ONLY also-rans documented, never wired: rows 146 / 147 /
  148 (same target, no provenance).
- Verified-last-step plan keys (8): `1,2,1+2`, `1,2,1+2~t7.bob`,
  `1,2,1+2~t7.bob.2`, `2,1`, `2,1,2`, `2,1~t7.bob`, `2,1~t7.bob.2`,
  `2,1~t8.bob` (twins inherit canonical steps verbatim).

## Review steps (candidate documented, row null, never played)

- `b+1+2,1` and `b+1+2,1,2` step 1: row 167 held — STANCE-SOFT crouch
  row for a standing-context step.
- `b+2,1` and `b+2,2` step 1: row 158 held — STANCE-SOFT duck-dip row
  for a standing-context step. (Row 158 also appears as a Job 4 join on
  both steps — documented candidate, never promoting.)
- Promotion needs full FK threshold-crossing data (named unblock, not
  guessed).

## Rejected / unmapped honesty

- **74 unmapped planned steps, ZERO with a rejected candidate** — every
  one has NO candidate at all. Their intermediate prefixes are
  T8-sourced strings with no T3 row (e.g. `1,1`, `1,2`, `b+1`, `d+2`,
  `WS.1`, `uf+1` carry `anim_ref` T8/T7-source values and `t3_row`
  null in both files). Their correct clips come from #988 Step 2
  (original T8 refs) or future extraction. No gate rejection was
  needed because there was nothing to reject — the honest gap is
  missing rows, not wrong rows.
- Job 3: burger targets adjudicated per step prefix; besides the row
  132 fill, all other burger Job 3 candidates are documented in
  burger_batch1_job3.json and never wired (SOFT-filed / soft-nofiled /
  ROW-ONLY / unknown-not-in-top10). No SOFT fill is inherited from
  #1097 (Pantera-specific, still unapproved).
- Job 4 (CORRECT join only): 2 joined steps (both `b+2` step 1, row
  158 — documented candidate on already-review steps, never
  promoting). Orphans: 6 bryan candidates no burger Job 2 move carries
  (rows 110, 157, 171, 200, 203, 207). No row-220 exclusion triggered.
  The naive cross-fighter join on key-prefix equality is INVALID and
  was never used.
- Current picks (Job 2 audited resolution, burger_batch1_lp_rp.csv, 91
  rows): donor-dominated. Sharpest: chord enders currently play
  JUMPING bryan row 41 (the `1+2` whole-string donor: `1+2,1+2`,
  `1,2,1+2`, `FC.d/f+2,1,1+2`, `d/f+1,1+2`, `f+2,H.1+2`,
  `u+1+2,1+2`, `u/f+1+2,1+2` families); single-button enders play donor
  rows 100 (RP2) / 172 (LP1). Donor→plan transition is the designed
  correction (Pantera precedent): wiring a plan replaces single-row
  resolution wholesale, even for CLEAN donors, because one row cannot
  be correct for a multi-hit string. Step 1 of `1,1`-family strings
  still plays row 172 — but now as a VERIFIED STEP row, not as a
  whole-string donor; step 2 plays NO row until a real clip lands.
- Quarantined-only canonicals with plans (9): `1,2,2`, `BAL.1,2`,
  `b+2,1`, `df+1,d+1`, `f+2,H.1+2`, `f+2,H.1+2,1`, `u+1+2,1+2`,
  `uf+1,2`, `uf+1,2,H.2`. Plans live on the #1096 base and become live
  when #988 merges (Option B restores the 630, burger's 50 among them).

## Gap-1 re-verification (Pantera batches' method, replicated)

- Bryan bank files IDENTICAL across the #1096 branch and current main
  (API-confirmed): hit_frames.json blob 7ffea6b998d6, rows.pack.json
  blob 1e22a8832b2c, skeleton.json blob 32d521db0921. Local valtree
  files are main's blobs (fetched from main 5e1b900b).
- Cited-row profiles (Job 1 bryan vs hit_frames, button/throw/active):
  **24/24 MATCH** (all verified, review-candidate, Job 3, and Job 4
  rows; button, throw flag, and active window all agree).
- Main tip at check: 5e1b900b (re-fetched; no movement since the
  #988 lane's last check).

## Wiring

- `string_step_plans` CREATED in burger.json (burger had none on
  #1096): law + 88 plan keys. Formatter round-trip reproduces the
  #1096 file byte-identically before changes; structural diff proves
  all non-plan top-level keys identical, moves 552 / strings 107
  unchanged.
- Tests: minimal-tree `node --test` 9 pass / 0 fail (counts 552/107/88;
  Batch 1 keys exactly the documented 88; verified rows non-null and
  never 35/220 with buttons in bryan hit_frames; review/unmapped row
  null; no soft flags; flagships 2,1 / 2,1,2 / 1,2,1+2; TACKLE family
  has no plan key; verified-last-step set exactly the 8; fighter.js
  step-plan markers present). `node --check fighter.js` OK.
- LIMITATION (honest): full 200-test suite comparison vs pristine main
  NOT run — no full current-main checkout exists on this box. Blast
  radius is confined by construction: no engine changes, no
  moves/strings changes, no prior-plan changes (burger had none), doc +
  test + audit-append only. The suite comparison must be run before
  merge (CI will also cover it).
- NOT play-verified: no fight played. Nothing here is "fixed" until
  the user plays it.

## Play-verify checklist (parent browser delegation, after #1096 merge + this PR merge + deploy + sync)

Phone portrait, human simulation (screenshot, look, scroll, tap —
never selectors). Burger vs any fighter. Scope: a plan governs the
STRING move's resolution + whole-string chain path; per-press
intermediates resolve single moves through normal tiers (unchanged) —
only the FINAL press uses the plan's last step.

1. `2,1` / `2,1,2`: verified-all — steps play rows 152 / 153 /
   (151), feet grounded, RP2 then LP1 then RP2 reading correctly. The
   old whole-string donor rows (100/172) must NOT appear as
   whole-string clips.
2. `1,2,1+2`: step 1 plays row 172 (grounded LP1), step 2 plays NO
   row, final press plays row 132 (standing LP1+RP2 chord) — NOT the
   old jumping donor row 41.
3. `1,1` / `1,2` / `1,2,2`: step 1 plays row 172; later steps play NO
   row (old donor rows 100/172 must NOT play as whole-string clips).
4. `b+1+2,1` / `b+2,1`: step 1 plays NO row (review candidates 167 /
   158 held, never played).
5. TACKLE family: no plan — chains resolve through normal tiers
   (unchanged by this PR).
6. No plan step plays rows 35 or 220 under any input (bryan row 35
   does not exist; row 220 fails every strike button gate).
7. Quarantined-only strings (`1,2,2`, `BAL.1,2`, `b+2,1`, `df+1,d+1`,
   `f+2,H.1+2`, `u+1+2,1+2`, `uf+1,2`) behave per their plans ONLY
   after #988 merges; before that they remain quarantined on main
   (plans are present on this branch, not yet live).
