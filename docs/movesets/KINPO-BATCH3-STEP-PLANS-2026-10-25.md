# KINPO BATCH 3 STEP PLANS — mixed-pair strings (2026-10-25)

Stack: kinpo Batch 3, stacked on kinpo Batch 2 (PR #1118), which stacks on
kinpo Batch 1 (PR #1117), which stacks on #1096 (the step-playback engine).
Merges AFTER #1118 (after #1117, after #1096 — itself blocked on 12
pre-existing failures / a gate decision owed; this lane fixes neither and
merges nothing itself). This PR does not touch fighter.js, pantera.json,
burger.json, demonio.json, or diablo.json. Nothing touches
`t8_quarantine_20261024`. No T8 removals anywhere in this lane.

## Scope

Kinpo strings whose steps are ALL buttoned and whose button union is
exactly one punch button + one kick button: {LP1,LK3}, {LP1,RK4}, {RP2,LK3},
{RP2,RK4} (LP1 = Left Punch = Tekken 1, RP2 = Right Punch = Tekken 2,
LK3 = Left Kick = Tekken 3, RK4 = Right Kick = Tekken 4). Any directionals,
any contexts. Pure single-button strings first, then chord-involved.
Measured from the file, not assumed.

## Bank (verified, not assumed)

Kinpo's T3 bank is JIN, four-way file evidence (kinpo Batches 1–2
re-verified, not re-assumed): kinpo.json `t3_source: 'jin'`,
`t3_bank: 'moveset_jin.json'` on BOTH the Batch 2 branch and current main;
`game/assets/anim/t3/` on main contains a `jin` dir (hit_frames +
rows.pack + skeleton) and NO `asuka` dir; Job 1 bank jin (220 rows);
Job 2 kinpo entries all bank jin (525); Job 4 jin candidates (47).
Kinpo's T7/T8 base IS Asuka (`tekken_base` Asuka, merge_sources t8/t7
asuka), but Asuka debuted in Tekken 5 and has NO T3 bank in this repo, so
the file's T3 fallback bank is jin, consistently applied everywhere
(`t3_source`, `t3_bank`, every `anim_ref` `t3:jin:row:N`, every move name
like `KINPO 2 (T3 jin r220)`, Job 2 bank) — the burger pattern (Bob →
bryan). The T7-Asuka re-match is future work; this batch adjudicates
against jin as the file declares. The pack dir does NOT differ from the
moveset bank name here (unlike diablo's heihachi/heihachi_on_jin split).

Bank-specific row rules (per-bank evidence, never a cross-bank blanket
ban): row 35 EXISTS here (hit_frames [11,12,39,535,0,1], Job 1 stance
starts-airborne) — not blanket-banned by number, but the stance gate
rejects it for ground steps; kinpo's own LP1 move `1` carries `t3_row`
35. Row 220 is a STANDING RP2 row here (hit_frames [12,12,41,1042,0,2],
Job 1 standing) — gate-adjudicated, NOT king's jumping chord row, NOT
bryan's button-0 row, NOT heihachi's jump RK4 row. Jin row 216 is a JUMP
row, NOT king row 216's dash Konvict Kick (it appears only as a Job 4
orphan in Batches 1–3).

Gap-1 (diablo method, re-verified): main jin hit_frames blob
`54b38e63…` and skeleton blob `26f72eb7…` are IDENTICAL on the Batch 2
branch and current main; main jin rows.pack blob `7bafa36a…` (226 rows)
differs from the Batch 2 branch's `141fbc8d…` (220 rows) — EXPLAINED:
the 6 extra rows are exactly the #1109 bake's jin rows
(89/112/247/288/339/357); main's pack is a SUPERSET (0 removed).
Cited-row profiles MATCH Job 1 vs hit_frames for every verified + review
row (195/199/220). Every wired row is present in BOTH packs (verified at
wire time). Main kinpo.json blob `614c1e0a…` UNCHANGED since the Batch 1
baseline.

## Universe (measured first)

Base = Batch 2 branch kinpo.json: 525 moves / 101 strings / 67 plans.
Batch 2 branch moves == #1096 moves exactly (verified); strings
identical. Current main: 482 moves + 43 quarantined = 525, 0 main-only
moves, strings 101/101.

- **21 canonicals** (19 pure single-button + 2 chord-involved:
  `b+1+4,4`, `db+4,1+4`); **ALL 21 planned, 0 CSV-only**; 48 CSV rows
  (21 canonicals + 27 twins); **48 plan keys**.
- Pair split: {LP1,LK3} 6 (1,1,3; 1,3; 3,1; d/f+1,3; f+1,3; f+1,3,1),
  {LP1,RK4} 11 (1,4; 4,1; WS.1,4; ws1,4; b+1+4,4; d/f+1,4; db+1,4;
  db+4,1+4; df+1,4; f+1,4; f+1,d+4), {RP2,LK3} 2 (2,3; b+3,2),
  {RP2,RK4} 2 (b+2,4; b+4,2).
- Contexts: standing 14, crouch 5, ws 2, jump 0.
- Provenance: 19 in main moves, 2 quarantined-only (1,1,3; db+1,4 — live
  when #988 merges), 0 Batch 2-branch-only.
- Overlap vs Batch 1 universe: []. Overlap vs Batch 2 universe: [].
- Input-~ canonicals in Batch 3 scope: **0** — kinpo inert on this axis,
  like Pantera/burger/Batches 1–2. __main records: 0. Corrupted keys: 0.
- The file's ONLY old-vs-corrected diff is one key, `3~4,D/F`, which is
  NOT Batch 3 scope (steps `3~4` LK3 cancel + `D/F` buttonless direction
  step — because D/F carries no button, the key is not all-buttoned, so
  it is a rest key, Batch 4 scope). Under the old rule it would collapse
  to a bogus single `3`; under the corrected rule it stays its own key
  for Batch 4. It gets NO plan in this PR (asserted in the Batch 3 test).
- Spelling quirks kept: `d/f+1,4` vs `df+1,4` are distinct canonicals
  (different step-1 evidence: the `d/f+1` step's jump row 179 rejected
  vs no candidate for the `df+1` step) — not merged, not smoothed over.
  WS-context fix (Batch 1): lowercase no-dot while-standing spellings
  (`ws1,4`) are WS context, not standing; changes NO wiring.

## Step tallies

44 steps, all planned: **2 verified / 1 review / 41 unmapped /
0 suspended-drift as a status** (3 steps carry SUSPENDED-DRIFT reasons
inside status unmapped — see below).

Unmapped split: **3 suspended-drift + 6 rejected-candidate +
32 no-candidate**.

Canonical status: 0 verified-all / 3 partial (2,3; 3,1; 4,1) /
18 unmapped-all / 0 review-only. Plan-key last-step: **0 verified /
0 review / 48 unmapped** — Batch 3 wires first steps only; NO
verified-last-step plan keys.

Verified rows (2 distinct, all baked in main's jin pack AND the Batch 2
branch pack): 195, 220.

## Every wired fill (verified only, T3 FALLBACK)

- `2,3` (partial): step 1 ← **220** (prefix-move own row, Job 2 CLEAN,
  standing RP2, hit_frames [12,12,41,1042,0,2], SOFT window [4,8] armR
  peak 6); step 2 unmapped (no candidate).
- `3,1` (partial): step 1 ← **195** (prefix-move own row, Job 2 CLEAN,
  standing LK3, hit_frames [19,23,61,535,0,4], SOFT window [7.5,13.5]
  legL peak 10); step 2 unmapped (no candidate).
- Twins inherit canonical steps verbatim (Batch 1 twin precedent).

No gate-note cases in Batch 3: both verified steps are standing-context
steps on standing rows. No standing-row-for-crouch-step verification
this batch.

## Review holds (1 step, row null, NOT wired)

- `4,1` step 1: candidate **199** (recorded-path, Job 2 CLEAN own row
  for move `4`, standing RK4, hit_frames [11,11,49,535,0,8]) passes HARD
  for standing, then SOFT limb-peak proxy FAILS (window [3.5,7.5], legR
  peak 3) — held at review, never wired. Note: row 199 is also the
  whole-string donor row for the `4,1` family in the CSV (Job 2 donor
  pick); the step-plan correctly does NOT wire it as a verified row.

## Suspended-drift (3 steps, row null, never wired)

- `1,1,3` step 1, `1,3` step 1, `1,4` step 1 — prefix move `1` is the
  file's ONLY row-changed move (35→None, Batch 2 branch vs current
  main). Stale row 35 documented, never wired (it would fail the stance
  gate for ground steps regardless — starts-airborne per jin Job 1).

## Rejected-candidate (6 steps, row null)

- `4,1` step 2: row **184** (recorded-path) — button 9 != step bits 1
  (a chord row, LP1+RK4, for a single LP1 step; Job 2 verdict HARD
  string-ender-on-chord, consistent). Note: row 184 is also `4,1`'s own
  Job 2 pick (own:row:184) — the whole-string own pick is retired by the
  step plan, which is the designed donor retirement, not a regression.
- `d/f+1,3` step 1 + `d/f+1,4` step 1: row **179** (prefix-move) —
  airborne jump row (stance jump; y0 0.943 ymax 1.519 vs standingY
  1.027). Also Batch 1's only Job 4 join, rejected for the same reason.
- `d/f+1,3` step 2: row **197** (recorded-dest) — airborne jump row
  (y0 0.943 ymax 1.525 vs standingY 1.027).
- `d/f+1,4` step 2 + `df+1,4` step 2: row **204** (recorded-dest) —
  airborne jump row (y0 0.943 ymax 1.531 vs standingY 1.027).

## No-candidate (32 steps)

`1,1,3` steps 2–3; `1,3` step 2; `1,4` step 2; `2,3` step 2; `3,1`
step 2; `WS.1,4` steps 1–2; `b+1+4,4` steps 1–2; `b+2,4` steps 1–2;
`b+3,2` steps 1–2; `b+4,2` steps 1–2; `db+1,4` steps 1–2; `db+4,1+4`
steps 1–2; `df+1,4` step 1; `f+1,3` steps 1–2; `f+1,3,1` steps 1–3;
`f+1,4` steps 1–2; `f+1,d+4` steps 1–2; `ws1,4` steps 1–2.
Recorded path + prefix move both absent — T8-sourced prefixes with no
T3 row; correct clips come from #988 Step 2 (original T8 refs) or
future extraction. Whole-string donor rows documented in the CSV, never
wired: row 195 (`1,1,3` / `1,3` / `2,3` / `f+1,3` families), row 199
(`1,4` / `WS.1,4` / `b+2,4` / `db+1,4` / `df+1,4` / `f+1,4` / `f+1,d+4`
/ `ws1,4` / `b+1+4,4` / `db+4,1+4` families), row 220 (`b+3,2` /
`b+4,2` families), row 35 (`3,1` / `f+1,3,1` families — starts-airborne,
HARD stance).

## Job 3 / Job 4

- Job 3 fills wired: **0**. Report entries: 4. `1,1,3` / `1,3` / `1,4`
  step 1 — rows 92/105 exact ROW-ONLY (target `1`), plus suspension
  blocks fills. `3,1` step `3,1` — rows 92/105 soft-nofiled ROW-ONLY.
  No agreement note fires: the note fires ONLY for actually-wired gate
  candidates disagreeing with an exact+FULL Job 3 candidate, and no
  exact+FULL Job 3 candidate exists for any Batch 3 step (the wired gate
  rows 195/220 face only soft-nofiled ROW-ONLY candidates, which are
  documented, not agreed or disagreed with). Dedupe fires zero times
  (no prefix__main duplicate pass-all rows in scope).
- Job 4 joins (CORRECTED join only, BANK_DIR jin): **4, all REJECTED**
  (rows 179/197/204 airborne — the same rows rejected on gates above),
  0 promoting. Orphans: jin rows 85, 91, 99, 100, 104, 127, 170, 171,
  172, 209, 216, 226, 239, 250, 256, 262 (same set as Batches 1–2,
  independently re-derived). Row 216 is jin's jump row, NOT king row
  216's dash Konvict Kick.

## Drift census (both ways — identical to Batches 1–2)

Full file (525 keys, Batch 2 branch vs current main): 253 same /
168 damage-only / 103 anim_ref-changed / 1 row-changed (`1`: 35→None).
Damage differs on 227 moves (all-status) vs 168 damage-only — both true
under their definitions; the 59 gap = damage differs AND row/anim_ref
also changed. Damage-only drift does NOT suspend.

## Tests (file evidence only — NOT play-verified)

Minimal-tree `node --test`: **35 pass / 0 fail** (13 Batch 1 cumulative +
11 Batch 2 + 11 Batch 3). `node --check fighter.js` OK. Formatter
round-trips the Batch 2 branch file byte-identically; all non-plan keys
identical; all 67 Batches 1–2 plans deep-equal; moves 525 / strings 101
unchanged. Batch 1 + Batch 2 test diffs prove every CONTENT assertion
preserved verbatim (only counts, extra-keys/complement counts, const
additions, header notes changed — the burger Batches 2–4 fix; Pantera's
latent break NOT copied).

**Limitation (honest):** full 200-test suite comparison NOT run — no
full current-main checkout on this box; CI must cover before merge.

## Play-verify checklist (parent browser delegation, after #1096 + #1117
+ #1118 + this PR merge + deploy + sync, phone portrait)

- `2,3`: row 220, then NO row (donor row 195 must NOT appear as a
  whole-string clip for the second step).
- `3,1`: row 195, then NO row (donor row 35 must NOT play — it is
  starts-airborne per jin Job 1 and is the whole-string donor for `3,1`).
- `4,1`: NO row any step (candidate 199 SOFT-held, candidate 184
  chord-rejected — neither must play).
- `1,3` / `1,4` / `1,1,3` + twins: NO row any step (stale row 35 must NOT
  play).
- `d/f+1,3` / `d/f+1,4` + twins: NO row any step (jump rows 179/197/204
  must NOT play). `df+1,4`: NO row any step (jump row 204 must NOT play).
- `WS.1,4` + twin, `ws1,4`, `b+1+4,4` + twins, `b+2,4` + twins, `b+3,2` +
  twins, `b+4,2` + twins, `db+1,4`, `db+4,1+4`, `f+1,3` + twins,
  `f+1,3,1` + twins, `f+1,4` + twins, `f+1,d+4` + twin: NO row any step
  (donor rows 195/199/220/35 must NOT appear as whole-string clips).
- No step plays row 35 for a ground step (starts-airborne per jin Job 1).
  Row 220 plays ONLY for RP2 steps (standing RP2 row in this bank —
  grounded, not airborne). No step plays a row from another bank.
- Kinpo Batches 1–2 spot-checks undisturbed (2,1 [220,221], 2,1,2,2
  [220,221,222,223], d+1+2,2 [92,93], b+2,1+2 last step 92, 1,1 step 1
  still suspended; u/f+4,3 [80,193], u/f+4,4 [80,207], d/f+4,4 [205, NO
  row] with review 212 held, u/f+4,4,4 [80,207, NO row] with review 210
  held). Quarantined-only strings behave per plan ONLY after #988
  merges (Batch 3: 1,1,3, db+1,4).

**No play verification is claimed here** — tests + file evidence only;
playing is the parent's step after merge + deploy.
