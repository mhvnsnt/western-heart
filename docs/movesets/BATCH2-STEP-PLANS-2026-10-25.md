# Pantera Batch 2 — step plans (LK3/RK4-only strings) — 2026-10-25

Button law: LP1 = Left Punch = Tekken 1, RP2 = Right Punch = Tekken 2, LK3 = Left Kick = Tekken 3, RK4 = Right Kick = Tekken 4.

> **Stack note:** this PR is stacked on #1096 (step-plan engine branch
> `feat/batch1-step-plans-pantera-20261024`). It merges AFTER #1096 (which is
> itself blocked on 12 pre-existing test failures / a gate decision owed) and
> after a rebase onto main at that time. It is NOT stacked on #1097 (which
> carries the unapproved SOFT row-49 fill): Batch 1 tallies below are #1096's
> record (27 verified / 7 review / 39 unmapped over 73 steps), NOT #1097's
> updated tallies. If #1097 merges first, this branch rebases onto the merged
> state and the Batch 1 guard map in `game/tests/batch2-step-plans.test.mjs`
> must be updated to #1097's Batch 1 statuses (b+2,1+2 family → verified,
> u/b+1,1 and u/b+1,2 first steps → verified-SOFT).

## What this is

Batch 2 of the locked batch order (Batch 1 LP1/RP2 → Batch 2 LK3/RK4 → Batch 3+
mixed pairs). The same step-plan engine from #1096
(`game/js/fighter.js` `_attackClipPlan` step-plan branch + `_stepChain`) plus
`string_step_plans` data in `game/assets/movesets/pantera.json`. A planned
string move plays per-STEP rows, never one row for the whole string. Only a
step with status `verified` plays its row. A `review`/`unmapped` step plays NO
bank row — the existing procedural fallback in `_animate` — and is flagged in
`_atkPlan.unmapped` with a `[WH-STEP-PLAN]` console line. Donor, match, and
generic tiers are bypassed for planned strings, so a planned string can never
silently donor-fall-back. No blend is added: step-to-step pose continuity is
UNPROVEN, and a blend ships only if play shows a snap.

## Universe (measured, not assumed)

Batch 1 measured 57 strings (40 pure + 17 chord). Batch 2 measures
**15 canonical strings (11 pure single-button + 4 chord-involved)**, from
moves-dict keys ∪ strings-list entries whose buttons are ONLY LK3 and/or RK4,
any directionals. Pantera's kick strings are few because most King kick
strings mix with punches (e.g. `3,2`, `3,2,2` are LK3+RP2 → Batch 3+ mixed
pairs, NOT Batch 2). The `df` vs `d/f` spellings are SEPARATE moves entries
(the `df` forms are T8-sourced, the `d/f` forms T3-sourced) and are planned
separately, as in Batch 1. Plan keys: **27 = 15 canonical + 12 twins/variants**
(`~t7.king` / `~t3.king` suffixes; twins inherit canonical steps verbatim
with canonical prefixes, Batch 1 twin precedent). All 15 canonical are strike
class and all 12 variants string/strike class, so unlike Batch 1 (which left
throw-class chains CSV-only), Batch 2 has ZERO CSV-only strings — every
Batch 2 string is planned. No Batch 2 string is a grapple chain (every
LK3/RK4-only grapple-chain candidate mixes punches and falls in later
batches).

Provenance: 14 canonical in current main `moves/` (playable), 1 quarantined-
only (`df+4,3,d+4` — in main's `t8_quarantine_20261024`, restored to playable
by #988 Option B; its plan lives on the #1096 base where the move exists and
becomes live when #988 merges). Contexts: 14 crouch, 1 standing
(`CH.d+3+4,4,4,4` — counter-hit, not a stance). No jump-context Batch 2
strings exist (no Pantera LK3/RK4 string opens with u/u/f/u/b).

## Gates (per step candidate, in order)

1. Candidate source: recorded path row (`strings[].t3_rows` full-path, or
   dest-only for the last step), else the prefix move's `t3_row`, else none.
   Only ONE Batch 2 string has a recorded path: `d/f+4,4` → `[197]`
   (dest-only). All other Batch 2 strings are plain-string entries (no
   `t3_rows`) or dicts without `t3_rows`. Recorded paths are NOT trusted
   blindly: a recorded row still faces every gate below.
2. HARD gates (fail = `unmapped`, candidate documented): button bitmask
   (`hit_frames.json` button field == step chord bits, LK3=4, RK4=8, 3+4=12)
   + throw flag == 0 + stance (see rule 4) + rows 35/220 rejected for ground
   steps always (they also fail button for kick steps: both are button 3).
3. SOFT gate (fail = `review`, not played): Job 1 peakF proxy for the Batch 1
   FK gate — window = stream active window / 2, +/-2 frames (Batch 1's rule);
   the step limb's Job 1 `peakF` inside the window passes. Chord steps
   (3+4): at least one leg peak in window. VALIDATED 13/13 on Batch 1's
   verified steps (correct limbs). The proxy is CONSERVATIVE: a max peak
   inside the window implies a threshold crossing inside, but a max outside
   can hide a secondary peak inside — so proxy-fail means review, never a
   false verify. WAIVED for jumping-context strings (Batch 1 precedent);
   Batch 2 has no jump strings, so no waiver applies here.
4. Stance gate: jump/starts-airborne rows fail ground-context steps and pass
   jump-context steps; crouch rows pass ONLY crouch-context steps; ground
   rows (downed-foe rows) fail all; ws-context steps matched to standing
   rows are review (ws→standing soft-stance, mirrors the Job 3 flag).
   Standing/duck-dip rows pass ground contexts (Batch 1 verified duck-dip
   rows for standing and crouch strings).
5. A gate-verified own/recorded candidate beats a disagreeing Job 3 candidate
   (own row is stronger file evidence); the disagreement is documented, not
   silently resolved. No such disagreement occurs in Batch 2 (Job 3 has zero
   Batch 2 candidates at all — see below).
6. Donor→plan transition (Batch 1 precedent, stated plainly): 23 of 27 Batch
   2 plan keys play a DONOR row today (Job 2 step `donor`), 2 play own rows,
   2 play `anim` rows. Wiring a plan replaces that single-row resolution
   wholesale — even for CLEAN-donor strings (e.g. the `df` spellings, Job 2
   CLEAN) — because one row cannot be correct for a multi-hit string. An
   unmapped step plays NO bank row (procedural fallback + flag), never the
   old donor row. This is the designed correction, not a regression: the
   string-level HARD/MED verdicts below are what the plans retire.
   Sharpest case: `d+3+4,4~t3.king` plays own row 197 today (Job 2 HARD
   limb) and its plan is unmapped-all — the variant's own row is a
   whole-string row, not a step row, so it never enters the step plan
   (Batch 1 twin precedent: `2,1~t7.king` own row 97 likewise never entered
   its steps).

## Gap-1 re-verification (Batch 1 method, replicated)

- King bank files IDENTICAL across the #1096 branch and current main
  (bae2be3b, re-checked at filing; pantera.json blob unchanged between
  57261ce6 and bae2be3b, sha256 `a3f76a0d…6bac0d62a8b`): `hit_frames.json` blob
  `7390cf4a4160e9d9bbe236d082a48f878bf5fabe` (API-confirmed on main),
  `rows.pack.json` `ac0cea0a649262908c75ad6fc246df1f4c76b6e5`,
  `skeleton.json` `156c8cbe2899fe62a29d08830ae4c0746a8e3458`. Local
  working copy sha256 matches main's blob content. Bank-side evidence
  (Job 1 profiles, Job 3/4 candidates) applies cleanly to current main.
- Cited-row profile cross-check (Job 1 vs hit_frames, button/throw/active):
  rows 135, 197, 216, 264 — 4/4 MATCH. No cited row mismatches; nothing
  suspended on profile grounds.
- Main pantera.json blob unchanged between 7fef69b8 and bae2be3b
  (sha256 `a3f76a0d65ad0ed7cadc9cf7bb25c435c2d25a8a05aa8615e794d6bac0d62a8b`),
  so the re-baseline below stands on current main.

## Re-baseline (Batch 1 section-0 rule, per prefix move)

Every Batch 2 step prefix compared #1096-file vs current main (main `moves/`,
else main quarantine). Result: **0 suspended**. Classes seen:
- `same` — identical row (or no row in either file).
- `damage-only` — damage value differs (MOD sync from #1039/#1059), row
  identical. NOT suspending: damage is not animation. (Prefixes: `d/f+4`,
  `d/f+4,3`.)
- `anim_ref-changed (T8/T7 source; row N/A)` — the #1039 footprint:
  #1096 `t8:king:*` vs main `UNMAPPED:t7-clip-pending` (kept playable) or
  quarantine. NOT suspending: no T3 row exists in either file, so no T3
  candidate is stale. These steps get candidates only via recorded path /
  Job 3 / Job 4; their CORRECT clips come from #988 Step 2 (original T8
  refs), never from a T3 row recorded as correct.
- `no-1096-move` — prefix absent from #1096 moves (`CH.d+3+4` and its
  extensions): no candidate by construction, not drift.
No prefix move changed its `t3_row` between #1096 and main, so no step is
SUSPENDED-DRIFT in Batch 2.

## Canonical step table (15 strings, 40 steps: 1 verified / 4 review / 35 unmapped)

| String | Steps (verified row, else status) | String status |
|---|---|---|
| `CH.d+3+4,4,4,4` | CH.d+3+4 = UNMAPPED (no candidate) \| 4 = UNMAPPED (no candidate) \| 4 = UNMAPPED (no candidate) \| 4 = UNMAPPED (no candidate) | unmapped-all |
| `FC.d/f+4,4` | FC.d/f+4 = UNMAPPED (no candidate: FC opener is T7-sourced, no t3_row) \| 4 = UNMAPPED (no candidate: full string T7-sourced, no t3_row) | unmapped-all |
| `FC.d/f+4,4,4` | FC.d/f+4 = UNMAPPED \| 4 = UNMAPPED \| 4 = UNMAPPED | unmapped-all |
| `d+3+4,4` | d+3+4 = UNMAPPED (T8 single, no t3_row) \| 4 = UNMAPPED (T8 string, no t3_row) | unmapped-all |
| `d+3+4,4,4` | d+3+4 = UNMAPPED \| 4 = UNMAPPED \| 4 = UNMAPPED | unmapped-all |
| `d+3+4,4,4,4` | d+3+4 = UNMAPPED \| 4 = UNMAPPED \| 4 = UNMAPPED \| 4 = UNMAPPED | unmapped-all |
| `d/f+3,4` | d/f+3 = UNMAPPED (no t3_row; Job 2 notation row 129 is an engine-tier pick, never a step candidate) \| 4 = UNMAPPED | unmapped-all |
| `d/f+4,3` | d/f+4 = REVIEW cand row 135 (SOFT proxy fail, see below) \| 3 = UNMAPPED (no candidate) | partial |
| `d/f+4,3,4` | d/f+4 = REVIEW cand row 135 \| 3 = UNMAPPED \| 4 = UNMAPPED | partial |
| `d/f+4,3,d+4` | d/f+4 = REVIEW cand row 135 \| 3 = UNMAPPED \| d+4 = UNMAPPED | partial |
| `d/f+4,4` | d/f+4 = REVIEW cand row 135 \| 4 = row 197 VERIFIED (recorded-dest) | partial |
| `df+3,4` | df+3 = UNMAPPED (df-spelling single is T8-sourced, no t3_row) \| 4 = UNMAPPED | unmapped-all |
| `df+4,3` | df+4 = UNMAPPED (df-spelling single is T8-sourced, no t3_row) \| 3 = UNMAPPED | unmapped-all |
| `df+4,3,4` | df+4 = UNMAPPED \| 3 = UNMAPPED \| 4 = UNMAPPED | unmapped-all |
| `df+4,3,d+4` | df+4 = UNMAPPED \| 3 = UNMAPPED \| d+4 = UNMAPPED | unmapped-all |

Plan keys (27): canonical tallies above, plus twins inheriting canonical
steps. Plan-key steps: **71 = 1 verified / 9 review / 61 unmapped**.
Plan-key string statuses: 18 unmapped-all / 9 partial / 0 verified-all /
0 review-only. Verified-last-step keys: exactly [`d/f+4,4`].
The 9 review steps are all the same prefix step (`d/f+4`, candidate row 135)
repeated across 4 canonical strings + 5 twins.

### The one verified step: `d/f+4,4` step 2 ← row 197

Recorded-dest row 197 (strings `t3_rows: [197]`). HARD gates: button 8 ==
step bits 8 (RK4) ✓; throw 0 ✓; stance crouch for a crouch-context step ✓.
SOFT proxy: legR peakF 3 inside window [1, 5] (active [6, 6] / 2 ± 2) ✓.
Job 2's string-level HARD limb verdict on `d/f+4,4` (own row 197) is NOT a
contradiction: a single row cannot satisfy a 2-hit string at string level;
the plan retires that verdict by attributing row 197 to step 2 only. The
per-press path uses the last step, so the final press still plays 197 —
same as today, now correctly attributed.

### The review step: `d/f+4` ← row 135 (4 canonical + 5 twin instances)

Prefix-move row 135 (T3 king r135, "3+RK"). HARD gates pass: button 8 ==
bits 8 ✓; throw 0 ✓; stance crouch for crouch-context ✓. SOFT proxy FAILS:
legR peakF 4 outside window [6, 10] (active [16, 16] / 2 ± 2); legR ext is
only 0.178 (the clip's dominant motion is armR ext 0.542). The proxy is
conservative — a secondary leg peak inside [6, 10] cannot be ruled out
from the single max frame — so the step is REVIEW (candidate documented,
row null), not verified and not rejected. Promoting it needs the full FK
threshold-crossing data (named unblock, not guessed here). Play-verify
cannot promote it either: review steps play no bank row by design.

## Job 3 — zero fills (targets exist, pass-all lists empty)

10 Batch 2 step prefixes are Job 3 targets (own-step HARD or donor-step
HARD moves): `d/f+4`, `d/f+4,4`, `d/f+4,3`, `d/f+4,3,4`, `d/f+3,4`,
`d+3+4,4`, `d+3+4,4,4`, `d+3+4,4,4,4`, `FC.d/f+4`, `FC.d/f+4,4`.
EVERY one has an EMPTY pass-all list in `job3.log`
(e.g. `pantera d/f+4: top row 266, pass-all: []`). The remaining Batch 2
prefixes are not Job 3 targets at all (`3`, `4` are CLEAN; the `df`/CH/FC
donor-MED/CLEAN entries are not HARD targets). Result: **0 Job 3 fills
wired, 0 SOFT candidates, 0 ROW-ONLY candidates** — there is nothing to
adjudicate, and this lane wires no SOFT fill (contrast #1097, whose SOFT
row-49 fill is still awaiting user approval and is NOT inherited here).
No verified step is contradicted by Job 3 (vacuously: no Job 3 candidates
exist for any Batch 2 prefix).

## Job 4 — zero joins (CORRECT method)

Correct join (pantera-only, BANK_DIR king→king_on_pantera_leoman, one row
per step; a candidate joins a step iff Job 2 has a pantera entry key ==
step prefix, row == candidate row, step == `own`): **0 Batch 2 steps
joined**. The 68 king Job 4 candidates are carried by Batch 1/mixed/other
moves (`d+1+2,2,1`, `2,1`, `3+4`, `u+1,3~t3.king.2`, variant keys like
`3_r60`, …) — none is a Batch 2 step prefix. Orphans: **7** (rows 88, 96,
154, 230, 236, 248, 342 — identical to Batch 1's orphan set). Row 218 is
NOT an orphan: it is carried by pantera `ss3+4` (Job 2 step `match`) —
Batch 1's orphan definition uses any Job 2 step, and this lane matches it
(an earlier own-only count of 8 was corrected to 7 on this evidence).
Row 220: joined to Batch 1's `2,1` only; no Batch 2 exclusion triggered.
A join never promotes by itself, so zero joins change zero statuses.

## CSV: `batch2_pantera_lk_rk.csv` (27 rows, Batch 1 style)

Current picks (Job 2 step + row): donor 24, own 2 (`d/f+4,4` → 197;
`d+3+4,4~t3.king` → 197), anim 2 (`d+3+4,4~t7.king` / `.2` → 197).
String-level verdicts: HARD on 15 rows (HARD limb: `FC.d/f+4,4`,
`d+3+4,4~t3.king`, `d+3+4,4~t7.king` / `.2`, `d/f+4,4`; HARD stance:
`d+3+4,4`, `d+3+4,4,4`, `d+3+4,4,4,4`, `d/f+3,4` / twin, `d/f+4,3` /
twin, `d/f+4,3,4` / twins), MED on 8 rows (MED level), CLEAN-donor on the
4 `df` spellings (INFO:fallback-clip only). No Batch 2 string plays a
jumping row today (no jump-clip-for-ground-move flags fire — the Batch 1
worst cases, rows 35/220 for ground enders, have no Batch 2 analogue in
today's picks; the risk in Batch 2 is donor rows 216/264 standing in for
crouch strings, which the plans retire). Played profiles come from Job 1
King rows (stance/btn_limb-or-dominant/level); pick definition is Job 2's
audited resolution, not a runtime claim — the engine's live resolution is
verified by the play checklist below, not by this CSV.

## T3 fallback log (PROCEDURAL_AUDIT.md Batch-2 entry)

Rows wired or held as candidates here are T3 FALLBACK, never the correct
mapping: row 197 (verified step `d/f+4,4` step 2) and row 135 (review
candidate for `d/f+4` step 1). Re-match both to T7 King rows when T7 clip
extraction lands (0x8000-bank bytes + requirement codes unresolved). No
other T3 row is wired or held in Batch 2. Rows 35/220 appear in NO Batch 2
plan step (verified or candidate) — the Batch 1 ground-step exclusion
holds vacuously here.

## Play-verify checklist (parent browser delegation — NOT claimed here)

After #1096 + this PR merge + deploy, on phone portrait, human simulation
(screenshot, look, scroll, tap — never selectors), Pantera vs any fighter.
Scope note (Batch 1 engine semantics): a plan governs the STRING move's
resolution and the whole-string chain path. The per-press path fires one
move per press, so an intermediate press resolves its single move through
the normal tiers (unchanged by this PR); only the FINAL press of a string
uses the plan's last step. The checks below are scoped accordingly —
"no row" means the string move's last step / the chain step, not the
intermediate single presses.
1. `d/f+4,4`: final press plays row 197, feet grounded, crouching low RK4
   — NOT a jumping row, NOT row 216/264. Whole-string path: step 1
   (review) plays NO bank row, step 2 plays 197.
2. `d/f+4,3` family (`d/f+4,3`, `d/f+4,3,4`, `d/f+4,3,d+4` + twins):
   final press plays NO bank row (unmapped last step); whole-string path
   plays NO bank row on any step (review opener + unmapped rest) — the
   old donor rows 264/216 must NOT play for the string move.
3. `d+3+4,4` family + `FC.d/f+4,4` family + `df` spellings + `CH` string:
   final press plays NO bank row (all unmapped last steps); whole-string
   path plays NO bank row on any step — old donor rows 216/264/197 must
   NOT play for the string moves.
4. No plan step (chain step or string-move last step) plays rows 35 or 220
   under any input.
5. Batch 1 strings still behave per #1096 (spot-check `2,1`: step 1 row 203,
   step 2 no row 220) — Batch 2 adds keys only and must not disturb them.
If check 1's ender is not row 197 grounded, or any check plays a donor row
for the string move, the plan is wrong and the PR's step rows revert —
play is the verdict, not this doc.
