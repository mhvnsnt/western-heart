# Diablo Batch 1 step plans (LP1/RP2-only strings, 2026-10-25)

Stack: #1096 engine → Diablo Batch 1 (this PR). This branch is stacked on
#1096 (`feat/batch1-step-plans-pantera-20261024`, the step-playback engine).
It does NOT stack on the Pantera plan branches (#1099/#1101/#1102), the
burger plan branches (#1103/#1104/#1105/#1107), or the demonio plan
branches (#1108/#1110/#1111/#1112): diablo.json plans do not conflict with
pantera.json, burger.json, or demonio.json plans. It does NOT include
#1097's Pantera Batch 1 follow-up fills (Pantera-specific, and its row-49
SOFT fill is still unapproved); no SOFT fill is inherited here. This PR
does not touch `fighter.js`: #1096's merge onto post-#1078 main must
reconcile #1078's `fighter.js` changes with #1096's engine branch, and
that belongs to #1096's merge, not this PR. No T8 content touched.

## 0. Bank — verified, not assumed

Diablo's T3 bank is HEIHACHI, established four ways:

1. `diablo.json` `t3_source: 'heihachi'`, `t3_bank: 'moveset_heihachi.json'`
   on BOTH #1096 (blob d44eef74…) and main (blob ad22b2d8…).
2. `game/assets/anim/t3/` on main contains BOTH a `heihachi` dir
   (hit_frames + skeleton, NO rows.pack.json — the known 404 gap) and a
   `heihachi_on_jin` dir (hit_frames + rows.pack.json + skeleton).
3. Job 1 / Job 4 banks for diablo are `heihachi_on_jin` (Job 1: 195 rows;
   Job 4: 49 candidates); Job 2 bank is `heihachi` (661 diablo entries).
4. The two hit_frames.json files are the SAME blob
   (a87184616ab95c52234db1f489c1315a9defcc0c), bank field
   `teardown/tekken3/animations/divmot13_heihachi.bin`, source
   `teardown/tekken3/movesets/moveset_heihachi.json`.

Bank resolution, documented not assumed: moveset/Job 2 bank `heihachi` <->
Job 1/Job 4/pack bank `heihachi_on_jin` <-> divmot13_heihachi.bin on the
jin rig (the bake lane's table says the same: heihachi rows baked into the
heihachi_on_jin pack because heihachi191 KMD has no hip/shoulder vertex
data). All gates below run against heihachi hit_frames (identical blob in
both dirs) + heihachi_on_jin Job 1 profiles.

Heihachi-bank rules, per-bank evidence (never a cross-bank blanket ban):

- Row 35 does NOT EXIST in this bank (absent from both hit_frames and
  Job 1 heihachi_on_jin) — no row-35 rule applies; any candidate row 35
  would fail the generic "absent from hit_frames" gate.
- Row 220 IS a JUMP RK4 row here (hit_frames [39,39,88,535,0,8], Job 1
  stance jump, y0 0.669 / ymax 1.435 vs standingY 0.955) — NOT jin's
  standing RP2 row, NOT king's jumping chord row, NOT bryan's button-0
  row. It is gate-adjudicated like any row (and its button 8 never matches
  an LP1/RP2 step's bits in this batch anyway).
- heihachi_on_jin row 216 is a DUCK-DIP row, NOT jin row 216's jump row
  and NOT king row 216's dash Konvict Kick. Same number, different bank,
  different move — never cite another bank's row identity.
- heihachi_on_jin Job 1 carries a `duck-dip` stance (14 rows: 192, 204,
  207, 209, 214, 216, 222, 225, 233, 237, 264, 344, 346, 348), handled like
  crouch: STANCE-SOFT (review) for non-crouch contexts, pass for crouch.
- Diablo's own LP1 move carries t3_row 46 — and Job 1 row 46 is
  STARTS-AIRBORNE (y0 1.695 vs standingY 0.955), the same class as Pantera
  LP1→king row 38 (jumping). Every ground-context step with candidate row
  46 fails the stance gate. Diablo's RP2 own row 157 is a standing row
  (Job 1 standing, armR ext 1.028) — clean.
- Rows 205/211/335 exist ONLY via the #1109 bake (pack entries): they are
  absent from BOTH main hit_frames and Job 1. A candidate row 205/211/335
  therefore FAILS the hit_frames gate here — it cannot verify on
  hit_frames evidence (the bake-lane decode is a different evidence class,
  not used by this lane's gates). No Batch 1 step cites them.

Gap-1 re-verification: #1096-branch bank blobs vs main — heihachi
hit_frames a87184616… IDENTICAL, heihachi_on_jin hit_frames a87184616…
IDENTICAL, heihachi_on_jin skeleton 7fa83b40… IDENTICAL. The
heihachi_on_jin rows.pack.json DIFFERS (#1096 a320210d… vs main
9e59dfe5…) — EXPLAINED, not drift: PR #1109 (bake 33 rows) merged to main
after #1096 branched; main's pack now contains MORE rows (baked), which
only helps playability. Cited-row profiles MATCH Job 1 vs hit_frames for
all 19 distinct verified rows + all review rows. All 19 distinct verified
rows are baked in main's heihachi_on_jin rows.pack.json (blob 9e59dfe5…,
= #1109's baked pack).

## 1. Universe (measured, not assumed)

Base: #1096 diablo.json (661 moves, 90 strings). Main diablo.json: 595
moves + 66 quarantine = 661 exactly; 0 main-only moves, 0 main-only comma
keys — the #1039 purge moved exactly 66 diablo moves to quarantine and
added nothing.

66 canonical LP1/RP2-only strings (45 pure single-button + 21
chord-involved — measured, not demonio Batch 1's 32+9). 111 plan keys (60
planned canonicals + 51 twins). 117 CSV rows (111 + 6 CSV-only TACKLE
keys, which carry no variants). Contexts: standing 49, crouch 10, jump 7,
ws 0 (diablo Batch 1 has no ws-context strings — measured). Provenance:
55 in main moves, 10 quarantined-only (live when #988 merges), 0 in
#1096-only. CSV-only (throw/grapple, no plan): TACKLE.1,1, TACKLE.1,1,1,
TACKLE.1,1,1,1, TACKLE.2,2, TACKLE.2,2,2, TACKLE.2,2,2,2.

### Corrected canonicalization — diablo DOES contain input-~ canonicals

This lane uses the CORRECTED rule (demonio Batch 2's finding): strip ONLY
a trailing source-variant suffix `~t[378]\.[a-z]+(\.\d+)?$`
(~t3.heihachi, ~t7.heihachi[.N], ~t8.heihachi). A `~` INSIDE the input is
Tekken cancel notation, part of the move. Diablo's inventory is NOT inert
like Pantera's/burger's (whose audit proved zero cancel-notation keys):
diablo contains 6 input-~ canonicals, all OWN canonicals in Batch 1
scope (button union ⊆ {1,2}):

- `1,2,2~1`, `1,2,2~1+2`, `1,2,2~1,1+2`, `2,2~1+2`, `b+1,2~1+2`,
  `f+2~1,1+2`

Cancel steps (`2~1`, `2~1+2`, `f+2~1`) are buttoned as the union of their
cancel components and land in Batch 1 scope by the button-union rule; all
6 canonicals are unmapped-all (no candidate rows), so no verification
claim rests on the union interpretation.

Old-rule recount (split at first `~`): 61 canonicals vs corrected 66.
The old rule would have created ONE bogus single-move canonical, `f+2`
(from `f+2~1,1+2` collapsing to `f+2`), and misfiled cancel strings as
variants of real canonicals: `1,2,2` would have absorbed 6 extra keys
(`1,2,2~1`, `1,2,2~1+2`, `1,2,2~1+2,u`, `1,2,2~1+2~t7.heihachi`,
`1,2,2~1+2~t7.heihachi.2`, `1,2,2~1,1+2`); `2,2` would have absorbed 3
(`2,2~1+2`, `2,2~1+2,u`, `2,2~1+2~t7.heihachi`); `b+1,2` would have
absorbed 3 (`b+1,2~1+2`, `b+1,2~1+2,u`, `b+1,2~1+2~t7.heihachi`). The
`,u` keys are rest keys (buttonless `u` step) — under the old rule they
would have been misfiled into Batch 1; under the corrected rule they are
their own rest canonicals (Batch 4 scope).

Wired-plan impact of the correction: NONE on verified rows. All misfiled
strings are unmapped-all under the corrected rule, and the wrongly
absorbing canonicals (`1,2,2`, `2,2`, `b+1,2`) are unmapped-all either
way. The only plan-status effect is the `f+2~1,1+2` family (old: review
via bogus `f+2`; corrected: unmapped-all). No verified row changes.

### __main records are their own canonicals (demonio Batch 4 rule)

`d+1,2__main` is its OWN canonical, not a twin of `d+1,2` (distinct
record, different damage/anim_ref) — partial [123, None], does NOT
inherit `d+1,2`'s step-2 review. Twins inherit canonical steps verbatim;
`__main` records do not inherit another record's rows.

### Corrupted key, recorded not fixed

`df+1,&amp;#58;2` is stored with an HTML-escaped colon (`&#58;` = `:`).
It is filed verbatim as a Batch 1 canonical (steps `df+1`, `&#58;2` —
the second step buttons as {2} since only `2` is a button digit) and is
unmapped-all (its step-2 prefix is a no-1096-move). Fixing the key
spelling is a data-quality follow-up for a later lane, NOT done here —
this lane never rewrites moveset keys.

## 2. Tallies

160 steps total = 142 planned-string steps + 18 CSV-only steps.
Planned steps: **44 verified / 11 review / 87 unmapped** (13
suspended-drift + 11 rejected-candidate + 63 no-candidate).
Planned canonicals: 8 verified-all / 20 partial / 30 unmapped-all / 2
review-only. Plan-key last-step: 29 verified / 10 review / 72 unmapped.
Job 3 fills wired: 0. Job 4 joins: 10, none promoting. Orphans: 3
(heihachi_on_jin rows 90, 96, 201).

Drift census, BOTH ways (1096 vs main, all 661 moves): 429 same / 151
damage-only / 78 anim_ref-changed / 3 ROW-CHANGED. Damage differs on 187
moves = 186 damage-differs-plus-unchanged-row + 1 row-changed move (`1`,
11→7). Both counts are true under their definitions; damage-only drift
does NOT suspend. The 3 ROW-CHANGED moves are `1` (46→None), `1_r46`
(46→None), `u+1,1~t3.heihachi.2` (46→None) — but only `1` is a Batch 1
step prefix, so only `1` suspends anything (13 steps). `1_r46` is not a
step prefix of any Batch 1 string; `u+1,1~t3.heihachi.2` is a twin key,
and twins inherit canonical steps (prefixes `u+1`, `u+1,1`), so it
suspends nothing.

Step-prefix drift census (91 distinct prefixes): same 53 / damage-only
16 / anim_ref-changed 16 / no-1096-move 5 / ROW-CHANGED 1. No-1096-move
prefixes: `R.1`, `R.1,b+2`, `R.b+2`, `u+1`, and the corrupted key itself
as a prefix (`df+1,&amp;#58;2`) — 6 steps, all no-candidate unmapped.

## 3. Every wired fill (verified only)

All verified rows: heihachi hit_frames button == step bits, throw 0,
T3 FALLBACK logged in the audit (never recorded as correct). 19 distinct
rows, 44 step-records, all baked on main (see §0).

Verified-all (8): **2,1** [157,158], **2,1,2** [157,158,159],
**2,1,2,2** [157,158,159,160] (recorded-path rows), **b+1+2,2** [98,99],
**b+1+2,2,2** [98,99,147], **d/f+1+2,2** [110,204] (crouch context),
**f+1+2,2** [223,99], **f+1+2,2,2** [223,99,147].

Other verified steps: b+1+2 family step 1 ← 98 (6 strings); b+1+2,1,2
step 3 ← 149; f+1+2 family step 1 ← 223 (6 strings); f+1+2,1,2 step 3 ← 149;
b+2,2 step 2 ← 146; d+1,2 step 1 ← 123; d+1,2__main step 1 ← 123;
jump lasts, SOFT waived per Batch 1 precedent (waiver noted in each
step's reasons): u+1,1 step 2 ← 40, u+1,2 step 2 ← 52, u/b+1,1 step 2 ←
42, u/b+1,2 step 2 ← 54, u/f+1,1 step 2 ← 41, u/f+1,2 step 2 ← 53.

Standing-row-for-crouch verified steps (demonio Batch 1 gate note,
carried): d+1,2 / d+1,2__main step 1 row 123 (standing row for a crouch
step) and d/f+1+2,2 step 1 row 110 (standing row for a crouch step) —
the gate flags crouch rows for non-crouch steps, not standing rows for
crouch steps. d/f+1+2,2 step 2 row 204 is duck-dip, which passes for
crouch context outright. If the gate is ever tightened, rows 123/110 for
these crouch steps must be re-adjudicated. No verified step uses row 35
(it does not exist in this bank) or row 220. No step carries a soft flag.

Hit_frames buttons for the 19 verified rows: 40:1, 41:1, 42:1, 52:2,
53:2, 54:2, 98:3 (LP1+RP2 chord row), 99:2, 110:3, 123:1, 146:2, 147:2,
149:2, 157:2, 158:1, 159:2, 160:2, 204:2, 223:3.

## 4. Every rejected / held candidate (row null, never played)

Review (11): b+1+2,2,2,1 step 4, candidate 224 (recorded-dest), SOFT fail
window [4.0,8.5], armL peakF 24; b+2,1 step 1, candidate 207
(prefix-move), STANCE-SOFT duck-dip for standing; b+2,1 step 2,
candidate 216 (recorded-dest), STANCE-SOFT duck-dip for standing; b+2,2
step 1, candidate 207, STANCE-SOFT duck-dip for standing; d+1,2 step 2,
candidate 240 (recorded-dest), SOFT fail window [12.5,16.5], armR peakF
21; f+1+2,b+2 step 2, candidate 207, STANCE-SOFT duck-dip for standing;
f+1+2,b+2,1 step 2, candidate 207, STANCE-SOFT duck-dip for standing;
f+1+2,b+2,1 step 3, candidate 216 (prefix-move), STANCE-SOFT duck-dip for
standing; f+2,1 step 1, candidate 178 (prefix-move), SOFT fail window
[4.5,9.0], armR peakF 10; f+2,1 step 2, candidate 224 (prefix-move), SOFT
fail window [4.0,8.5], armL peakF 24; f+2,2 step 1, candidate 178, SOFT
fail window [4.5,9.0], armR peakF 10. Promotion of any review step needs
full FK threshold-crossing data (SOFT fails) or a stance-rule change
(STANCE-SOFT) — named unblocks, not guessed.

Rejected candidates (11): 1,1,1 step 3, candidate 369 (prefix-move),
button 0 ≠ bits 1; b+1+2,1 step 2 / b+1+2,1,2 step 2 / f+1+2,1 step 2 /
f+1+2,1,2 step 2, candidate 145 (recorded-dest / prefix-move), button 12
(LP1+RP2 chord row) ≠ bits 1 — this is today's whole-string pick for
those enders (Job 2 verdict HARD string-ender-on-chord), correctly
retired as a step row; d/f+1,1 step 1 / d/f+1,2 step 1, candidate 173
(prefix-move), airborne jump row (y0 0.943 / ymax 1.519 vs standingY
0.955) for crouch steps; u/b+1,1 step 1 / u/b+1,2 step 1, candidate 39
(prefix-move), button 3 (LP1+RP2 chord row) ≠ bits 1 — why the u/b jump
family is partial; u/f+1,1 step 1 / u/f+1,2 step 1, candidate 38
(prefix-move), button 3 ≠ bits 1 — why the u/f jump family is partial.
u+1,1 / u+1,2 first steps have NO candidate at all (prefix `u+1` is a
no-1096-move) — different from the u/b and u/f families.

Suspended (13): step-1 prefixes `1` — 1,1 / 1,1,1 / 1,1,2 / 1,1,WAR.2 /
1,2 / 1,2,2 / 1,2,2~1 / 1,2,2~1+2 / 1,2,2~1,1+2 / 1,b+2 / 1,b+2,1 /
1,b+2,2 / 1,b+2,WAR.2 (prefix move `1` ROW-CHANGED 46→None; stale row 46
documented, never wired — row 46 is starts-airborne anyway, so it would
fail the stance gate for ground steps regardless of the suspension).

Job 3 (26 report entries, 0 fills): suspended 1-family step 1s carry
target-`1` candidates (98/107 exact ROW-ONLY, 110/122 soft-filed
ROW-ONLY, 133 soft-filed FULL) — documented in the Job 3 report, never
wired (suspension takes precedence; and none is exact+FULL anyway).
1,1-family step 2s carry target-`1,1` candidates (same set, none
exact+FULL) — never wired. f+1+2-family steps are already verified via
gate candidates (row 223); their target-`f+1+2__main` exact+FULL candidate
row 107 DISAGREES with wired 223 — the agreement note fires ONLY for
actually-wired gate candidates (demonio Batch 4 wording fix; exactly 6
DISAGREES notes, all on verified f+1+2-family step 1s, none on failed
steps). b+1-family steps carry target-`b+1` candidates (98/107 exact
ROW-ONLY, 133 soft-filed FULL) — never wired. Dedupe (prefix vs __main
duplicate pass-all rows, burger Batch 2 cleanup) is carried but not
exercised: no prefix and its __main twin both carry pass-all rows here.
No SOFT fill inherited from #1097.

Job 4 (10 joined steps, corrected join only, none promoting): b+2,1 /
b+2,2 / f+1+2,b+2 / f+1+2,b+2,1 step b+2 row 207 joined CANDIDATE (passes
HARD gates, NOT wired — a join never promotes); b+2,1 step 1 / f+1+2,b+2,1
step 1 row 216 joined CANDIDATE (same); d+1,2 / d+1,2__main step d+1 row
123 joined no-action (already verified); d/f+1,1 / d/f+1,2 step d/f+1 row
173 joined REJECTED (jump row for crouch steps). Orphans: heihachi_on_jin
rows 90, 96, 201 (no diablo Job 2 move carries them, any step).

Unmapped with NO candidate (63 planned steps): intermediate prefixes are
T8-sourced with no T3 row; correct clips come from #988 Step 2 or future
extraction, never from a T3 row recorded as correct.

## 5. Current picks retired (donor retirement is designed)

CSV (117 rows): donor picks 67, own picks 43, HARD-flagged 32,
jump-clip-for-ground-move 20. Sharpest retired clips: the f+1+2,b+2,1
twin (`f+1+2,b+2,1~t3.heihachi`) plays JUMPING row 221 as its whole-string
clip for a ground string (HARD stance + jump-clip-for-ground-move);
b+1+2,1 / f+1+2,1 enders play chord row 145 as whole-string clips (Job 2
verdict HARD string-ender-on-chord) — the plans correctly play NO row
for those ender steps. Donor retirement is DESIGNED: wiring plans
replaces single-row resolution wholesale, even for CLEAN donors, because
one row cannot be correct for a multi-hit string.

## 6. Tests + limitations

Minimal-tree `node --test`: 13 pass / 0 fail; `node --check fighter.js`
OK. Formatter round-trips the #1096 file byte-identically; structural
diff shows exactly 1 diff (the `string_step_plans` addition); all
non-plan keys identical; moves 661 / strings 90 unchanged. This Batch 1
test sets the baseline (later diablo batches go cumulative — Pantera's
latent break NOT copied). Limitation (stated, not hidden): full 200-test
suite comparison NOT run (no full current-main checkout on this box) —
CI must cover before merge. NOT play-verified (tests + file evidence
only; playing is the parent's step after merge + deploy).

## 7. Play-verify checklist (parent browser delegation, after #1096 + this PR merge + deploy + sync, phone portrait)

- 2,1 / 2,1,2 / 2,1,2,2 verified-all, rows 157/158/(159)/(160), feet
  grounded; old whole-string donors must NOT appear as whole-string
  clips.
- b+1+2,2 [98,99], b+1+2,2,2 [98,99,147], f+1+2,2 [223,99],
  f+1+2,2,2 [223,99,147], d/f+1+2,2 [110,204] (crouch) — grounded.
- u+1,1 step 1 NO row, step 2 row 40 (airborne); u/f+1,1 / u/b+1,1 first
  steps NO row (own rows 38/39 are chord rows, rejected), last steps
  rows 41/42.
- 1,1 / 1,2 / 1,b+2 families: step 1 NO row (suspended — stale
  row 46 must NOT play, and it is a jumping clip anyway).
- b+2,1 / b+2,2 step 1 NO row (duck-dip 207 held); f+2,1 both steps NO
  row (SOFT fails 178/224 held); b+1+2,1 / f+1+2,1 step 2 NO row (chord
  row 145 must NOT play as a step row).
- TACKLE family unchanged (no plan).
- No ground-context step plays a jumping row for a ground step; no step
  plays row 35 (it does not exist in this bank) or row 220 unless
  genuinely airborne per the heihachi_on_jin profiles.
- Quarantined-only strings behave per plan ONLY after #988 merges.
