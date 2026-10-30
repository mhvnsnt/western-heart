# Demonio Batch 2 step plans — LK3/RK4-only strings (2026-10-25)

Batch 2 of the locked batch order for Demonio (Jin / Devil Jin base):
Batch 1 LP1/RP2-only (PR #1108) → **Batch 2 LK3/RK4-only (this PR)** →
Batch 3 mixed pairs → Batch 4 triples/quads/rest.

Scope: Demonio strings whose buttons are ONLY LK3 (Tekken 3) and/or RK4
(Tekken 4), any directionals. Pure single-button strings first, then
chord-involved — measured, not assumed: **all 17 Batch 2 canonicals are
pure single-button; demonio carries no LK3/RK4 chord step among its
canonical comma keys** (Batch 1's 32-pure/9-chord split does not repeat
here). Throw-class canonicals get NO plan (CSV-audited only); Batch 2 has
zero throw/grapple canonicals, so zero CSV-only keys.

## Stack

- Base: demonio Batch 1 branch `feat/demonio-batch1-step-plans-20261025`
  (PR #1108, head f298ec019ed6b2d899096aa7586c53824c9fe48f), NOT #1096
  directly and NOT any Pantera or burger plan branch. Plans accumulate:
  59 Batch 1 keys + 25 Batch 2 keys = 84.
- Merges AFTER #1108 (which merges after #1096, itself blocked on
  12 pre-existing failures / a gate decision owed — this lane does not
  fix those and does not merge on mergeable:true alone).
- This PR does not touch `fighter.js`, `pantera.json`, or `burger.json`.
- The audit append (`docs/anim/PROCEDURAL_AUDIT.md`) is append-only; if
  the Pantera or burger stacks or demonio Batch 1 merge first, the audit
  append rebases after their entries (never overwrites them).
- No T8 content touched: `t8_quarantine_20261024` untouched, no
  `UNMAPPED:t7-clip-pending` markers stripped.

## Bank (verified, carried forward — not re-litigated)

Demonio's T3 bank is JIN: `demonio.json` `t3_source: 'jin'`,
`t3_bank: 'moveset_jin.json'` on both #1096 and main; `t3/` contains a
jin dir; Job 1 = 220 jin rows, Job 2 = 764 demonio entries bank jin,
Job 4 = 47 jin candidates. Jin exists in Tekken 3, so no substitution
(unlike burger's bryan fallback).

Jin-bank row rules (Batch 1's documented correction, per-bank evidence,
never a cross-bank blanket ban):

- Jin row 220 is a STANDING RP2 row (hit_frames [12,12,41,1042,0,2],
  Job 1 stance standing, travel 0.216) — NOT king's jumping chord row or
  bryan's button-0 row — so it is NOT blanket-banned; it is
  gate-adjudicated per step like any row. **No Batch 2 step uses row 220**
  (Batch 2 is LK3/RK4-only), so the rule is carried but not exercised here.
- Jin row 35 IS starts-airborne, so the row-35 rejection for ground steps
  stands, and row 35 verifies ONLY in jump context. **No Batch 2 step
  uses row 35 at all.**

## HEADLINE: canonicalization correction (Batch 1's canonical() was wrong for input-`~` keys)

Batch 1's `canonical()` stripped at the FIRST `~`, treating every `~`
suffix as a source-variant marker. That is wrong for Tekken cancel
notation: a `~` inside the input (e.g. `f+3~3`, `d+3,4~4`, `4~3,H.1+2`)
is part of the move's input, NOT a variant marker. The old definition
created two bogus single-move "canonicals" in Batch 2 scope and misfiled
two genuine strings as variants:

| Key | Old canonical() | Correct canonical() | Evidence |
|---|---|---|---|
| `4~3,H.1+2` | `4` (bogus single) | `4~3,H.1+2` (own string) | "Wheel of Pain > Annihilation Beam", T8 Devil Jin, move_class string |
| `f+3~3,d/f+3` + `f+3~3,d/f+3~t7.jin` | `f+3` (bogus single) | `f+3~3,d/f+3` (own string) | "Heat Seeker", T7 Jin, move_class string; `f+3` alone is a real single move ("Left Sidekick", T8 Jin) |
| `d+3,4~4` | variant of `d+3,4` | own canonical | "Mid Sidekick", T8 Jin, move_class string, strings-list entry |
| `f+3~3` | variant of `f+3` | own single move (not a string) | T7 Jin move, no comma → correctly excluded from string scope |

Correct handling, used by this lane's derive + build scripts: strip ONLY
a trailing source-variant suffix matching `~t[378]\.[a-z]+(\.\d+)?$`
(`~t3.jin`, `~t7.jin[.N]`, `~t8.jin`). A `~3`, `~4`, `~3,d/f+3`,
`~3,H.1+2` suffix is input notation and is preserved. Steps are
comma-split; a `~` inside a step token denotes a cancel follow-up
(buttons = digits in the step token, e.g. step `4~4` → RK4).

Corrected Batch 2 universe: **17 canonicals** (the pre-fix count was
also 17 by coincidence: −2 bogus singles `4`/`f+3`, +2 genuine
`f+3~3,d/f+3`/`d+3,4~4`). The two new canonicals are both unmapped-all
(their prefixes are T8-sourced with no T3 row), so the correction changes
no verified row — but it changes the string inventory, which is what
Batch 3/4 build on.

**Batch 1 is provably unaffected.** Every input-`~` key in demonio's
moves was checked against Batch 1's universe: NO input-`~` key
old-canonicalizes into a Batch 1 canonical (all `~3`/`~4` keys are
mixed-pair, triple, or quad scope; there are no `~1`/`~2` input-cancel
keys in demonio's moves at all). Batch 1's 41 strings stand as filed.

**Carry-forward (mandatory, not optional):**

- Demonio Batch 3 (mixed pairs) and Batch 4 (triples/quads/rest) MUST use
  the corrected definition, or they will misfile `1,3~3`, `1,3~3,d/f+3`,
  `WS.1,3~3`, `ws1,3~3`, `d/f+1,4~4`, `df+1,4~4` (Batch 3 scope) and
  `2,1,4~4`, `4~3,H.1+2` (Batch 4 scope) as variants of shorter strings.
- Pantera and burger batches used the SAME old canonical() (strip at
  first `~`). Their lanes should be audited for the same misfiling:
  any key with an input-`~` whose old-canonical collides with a filed
  canonical is a misfiled distinct string, not a variant. This lane did
  not touch Pantera or burger files; the flag is for their lanes.

## Tallies

- Canonical strings: **17** (17 pure, 0 chord).
- Plan keys: **25** (17 canonicals + 8 twins). Twins inherit the
  canonical plan verbatim.
- CSV rows: **25** (17 canonicals + 8 twins). CSV-only keys: **0**.
- Steps (canonicals): **38 = 11 verified / 5 review / 22 unmapped**.
- Plan-key last-step: **5 verified / 6 review / 14 unmapped**.
- Canonical string_status: **3 verified-all / 4 partial / 10 unmapped-all**.
- Suspended-drift steps: **0** (see drift census — none of the 3
  row-changed moves falls in Batch 2 scope).
- Job 3 fills wired: **0**. Job 4 joins: **5, all no-action, none
  promoting**. Orphans: **2** (jin rows 85, 91 — same set as Batch 1).
- In main moves: 12 canonicals; quarantined-only: 5 canonicals
  (`d+3,4`, `d+3,4,3`, `d+3,4~4`, `DVS.4,4`, `WS.4,4` — Batch 2 plans
  cover quarantined-only strings the same as playable ones, since the
  plan block is additive data, not a playability change).

## Step table (canonicals; twins inherit verbatim)

| Canonical | Context | Step 1 | Step 2 | Step 3 | Step 4 | Status |
|---|---|---|---|---|---|---|
| DVS.4,4 | standing | unmapped | unmapped | | | unmapped-all |
| WS.4,4 | ws | unmapped | unmapped | | | unmapped-all |
| d+3,3 | crouch | unmapped | unmapped | | | unmapped-all |
| d+3,4 | crouch | unmapped | unmapped | | | unmapped-all |
| d+3,4,3 | crouch | unmapped | unmapped | unmapped | | unmapped-all |
| d+3,4~4 | crouch | unmapped | unmapped | | | unmapped-all |
| d/f+3,3 | crouch | unmapped | unmapped | | | unmapped-all |
| d/f+4,4 | crouch | **205 verified** | review | | | partial |
| f+3,3 | standing | unmapped | unmapped | | | unmapped-all |
| f+3~3,d/f+3 | standing | unmapped | unmapped | | | unmapped-all |
| f+4,3 | standing | review | unmapped | | | partial |
| u+4,4 | jump | **79 verified** | **209 verified** | | | verified-all |
| u/f+4,3 | jump | **80 verified** | **193 verified** | | | verified-all |
| u/f+4,4 | jump | **80 verified** | **207 verified** | | | verified-all |
| u/f+4,4,4 | jump | **80 verified** | **207 verified** | review | | partial |
| u/f+4,4,4,4 | jump | **80 verified** | **207 verified** | review | review | partial |
| ws4,4 | standing | unmapped | unmapped | | | unmapped-all |

## Verified steps (11) — file evidence

All verified rows are jin hit_frames button == step bits, throw flag 0.
No verified step plays row 35 or row 220. T3-row matches are FALLBACK
matches logged in `docs/anim/PROCEDURAL_AUDIT.md`, never recorded as the
correct mapping, to be re-matched to T7 Jin rows when decode lands.

| Step | Row | hit_frames | Job 1 jin stance | Path |
|---|---|---|---|---|
| u+4,4 step 1 (u+4) | 79 | [25,25,66,535,0,8] RK4 | jump | prefix move own row |
| u+4,4 step 2 (4) | 209 | [47,47,86,271,0,8] RK4 | jump | recorded path |
| u/f+4,3 step 1 (u/f+4) | 80 | [25,25,66,535,0,8] RK4 | jump | prefix move own row |
| u/f+4,3 step 2 (3) | 193 | [35,37,65,535,0,4] LK3 | jump | recorded path |
| u/f+4,4 step 1 (u/f+4) | 80 | [25,25,66,535,0,8] RK4 | jump | prefix move own row |
| u/f+4,4 step 2 (4) | 207 | [47,47,86,271,0,8] RK4 | jump | recorded path |
| u/f+4,4,4 steps 1–2 | 80 / 207 | as above | jump | as above |
| u/f+4,4,4,4 steps 1–2 | 80 / 207 | as above | jump | as above |
| d/f+4,4 step 1 (d/f+4) | 205 | [16,16,62,271,0,8] RK4 | crouch | prefix move own row |

Jump-context verified steps carry the Batch 1 precedent note: "SOFT gate
waived (jump context)". d/f+4,4 step 1 (row 205, crouch row for a
crouch-context step) passed the SOFT proxy outright — no waiver, no
gate-note case. **No Batch 2 verified step needs Batch 1's
standing-row-for-crouch-step gate note** (the gate flags crouch rows for
non-crouch steps, not standing rows for crouch steps, and no such step
is verified here).

## Review steps (5) — row null, never played

| Step | Candidate row | Reason |
|---|---|---|
| d/f+4,4 step 2 (4) | 212 (recorded path, jin duck-dip) | SOFT limb-peak proxy fail: window [4.5,8.5], legR peak 12 |
| f+4,3 step 1 (f+4) | 214 (prefix move own row, jin standing) | SOFT limb-peak proxy fail: window [13.0,18.0], legR peak 3 |
| u/f+4,4,4 step 3 (4) | 210 (jin duck-dip) | STANCE-SOFT: duck-dip row for a jump-context step |
| u/f+4,4,4,4 step 3 (4) | 210 (jin duck-dip) | STANCE-SOFT: duck-dip row for a jump-context step |
| u/f+4,4,4,4 step 4 (4) | 211 (jin duck-dip) | STANCE-SOFT: duck-dip row for a jump-context step |

SOFT proxy (validated 13/13 on Pantera Batch 1's verified steps) is used
conservatively: proxy-fail = review, never false verify. SOFT candidates
are documented as candidates with softness stated and are NOT wired —
no SOFT fill is inherited from #1097 (Pantera-specific, still unapproved,
does not transfer to demonio).

## Unmapped steps (22) — all no-candidate, zero rejected

Every unmapped step's reason is identical: "no candidate row (recorded
path + prefix move both absent)". **Batch 2 has ZERO rejected-candidate
steps** (unlike Batch 1's 10): no candidate exists to reject. The
intermediate prefixes are T8-sourced moves with no T3 row (e.g. `d+3`,
`DVS.4`, `WS.4`, `f+3`, `f+3~3`, `ws4`, and the full-string prefixes
`DVS.4,4`, `d+3,3`, `d+3,4,3`, `f+3~3,d/f+3`). Correct clips that don't
exist in T3 files come from #988 Step 2 (original T8 refs) or future
extraction — never from a T3 row recorded as correct.

## Job 3 fills: 0 (precisely: 9 prefixes in the log, all empty pass-all)

9 Batch 2 step prefixes appear in `job3.log` — `d+3`, `d+3,3`, `d+3,4`,
`d+3,4,3`, `d+3,4~4`, `d/f+3`, `d/f+3,3`, `u/f+4,4,4`, `u/f+4,4,4,4` —
ALL with EMPTY pass-all lists. The remaining 19 prefixes do not appear
in the log at all. Result: 0 candidates, 0 fills. (The burger-refinement
fill rule — a Job 3 fill additionally requires the SOFT proxy to pass —
is therefore not exercised here; it is carried forward, not dropped.)
Dedupe note: no prefix-vs-`__main` duplicate pass-all rows exist for
Batch 2 (there are no pass-all rows to dedupe).

Every cited bank hash and cited-row profile was re-verified against
current main before wiring (Batch 1 gap-1 method): jin bank blobs
identical across the Batch 1 branch and main (API-confirmed in Batch 1;
re-confirmed here — see drift census), cited-row profiles MATCH Job 1 vs
hit_frames on button/throw/active/hit. Any mismatch would have suspended
the fill; there were no fills to suspend.

## Job 4 joins: 5, all no-action, none promoting

Corrected join only (demonio-only, BANK_DIR jin, join iff Job 2 has
demonio entry key == step prefix, row == candidate row, step == own).
The naive cross-fighter join on key-prefix equality is INVALID and was
not used. A join NEVER promotes a candidate by itself.

| Step | Joined row | Outcome |
|---|---|---|
| u+4,4 step 4 | 209 | no action — step already verified |
| u/f+4,3 step 3 | 193 | no action — step already verified |
| u/f+4,4 step 4 | 207 | no action — step already verified |
| u/f+4,4,4 step 4 | 207 | no action — step already verified |
| u/f+4,4,4,4 step 4 | 207 | no action — step already verified |

Orphans: 2 — jin rows 85, 91 (same set as Batch 1; Job 4 candidates with
no demonio step to join to).

## Drift census (Batch 1 file vs current main — re-baselined, both counts)

Census over all 764 Batch 1-file moves vs current main (moves 671 +
quarantine 93 = 764 = Batch 1-file moves):

- same: 517
- damage-only (damage differs, row + anim_ref unchanged): 164
- anim_ref-changed (row unchanged): 80
- ROW-CHANGED: 3 — `1` (41→None), `1_r41` (41→None),
  `u+1,1~t3.jin.2` (41→None)

Damage differs on **195** moves (194 unchanged-row + 1 row-changed `1`,
11→7). Both counts are true under their definitions (burger Batch 2
reconciliation): 164 is the damage-only count (row + anim_ref
unchanged); 195 is the damage-differs-plus-unchanged-row count plus the
one row-changed move whose damage also differs. Damage-only drift does
NOT suspend (damage ≠ animation). **Suspended-drift steps: 0** — none of
the 3 row-changed moves falls in Batch 2 scope (Batch 1's suspended
`1,1`-family step 1s are LP1/RP2 scope, not LK3/RK4).

## Donor retirement (designed, not a regression)

Wiring plans replaces single-row resolution wholesale, even for CLEAN
donors, because one row cannot be correct for a multi-hit string. Batch 2
donors retired by plan wiring include the single-row resolutions for
`u+4,4` (row 209), `u/f+4,3` (row 193), `u/f+4,4` (row 207),
`u/f+4,4,4` (row 210), `u/f+4,4,4,4` (row 211), and the fallback-clip
donors for the unmapped-all strings (rows 195/199/132). The plans, not
the donors, are the string truth.

## Tests

Minimal-tree `node --test` (from the Batch 1 branch checkout + this PR's
files): **24 pass / 0 fail** — 12 Batch 1 cumulative tests (every Batch 1
content assertion preserved verbatim; only the plan-count assertion
59→84 and the extra-keys assertion changed, per the burger Batches 2–4
test-evolution rule) + 12 Batch 2 tests (keys, verified-step gates,
5 flagships, canonicalization guard, verified-last list, fighter.js
markers). `node --check fighter.js` OK.

Limitation (stated, not hidden): the full 200-test suite comparison was
NOT run by this lane (no full current-main checkout on this box). CI
must cover it before merge.

## Play-verify checklist (parent browser delegation — NOT claimed here)

After merge + deploy, on phone portrait, each wired Batch 2 string played:

- [ ] `u+4,4`: both steps grounded-jump correct (jump context), rows 79/209, no ground-context row 35 anywhere.
- [ ] `u/f+4,3`: rows 80/193, jump context, LK3 second step (not a punch row).
- [ ] `u/f+4,4`: rows 80/207, jump context.
- [ ] `u/f+4,4,4` / `u/f+4,4,4,4`: first two steps play 80/207; later steps stay UNMAPPED (no duck-dip row 210/211 played for a jump step).
- [ ] `d/f+4,4`: step 1 plays row 205 (crouch); step 2 stays UNMAPPED (no row 212 played on SOFT fail).
- [ ] `f+4,3`: step 1 stays UNMAPPED (no row 214 played on SOFT fail).
- [ ] Unmapped-all strings (`DVS.4,4`, `WS.4,4`, `d+3,3`, `d+3,4`, `d+3,4,3`,
      `d+3,4~4`, `d/f+3,3`, `f+3,3`, `f+3~3,d/f+3`, `ws4,4`): no step plays
      a jumping row for a ground step; no step plays rows 35/220 unless
      genuinely airborne per the jin-bank profiles.
- [ ] Demonio Batch 1 spot-checks undisturbed (2,1 family 220/221, d+1+2,2
      92/93, u+1,1 step 2 row 35 jump-only, 1,1 step 1 still suspended).

## Files changed (this PR, 4 files, all additions to the plans block)

- `game/assets/movesets/demonio.json` — string_step_plans 59 → 84 keys
  (+25 Batch 2), law extended with the Batch 2 addendum. No other key
  changed (structural diff: all non-plan keys identical, all Batch 1
  plans deep-equal).
- `docs/movesets/DEMONIO-BATCH2-STEP-PLANS-2026-10-25.md` — this doc.
- `game/tests/demonio-batch2-step-plans.test.mjs` — new, 12 tests.
- `game/tests/demonio-batch1-step-plans.test.mjs` — cumulative update
  only (count 59→84, extra-keys assertion; all Batch 1 content
  assertions verbatim).
- `docs/anim/PROCEDURAL_AUDIT.md` — append-only entry (shared file).
