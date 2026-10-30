# KINPO BATCH 1 — LP1/RP2-only strings: step plans (2026-10-25)

Batch 1 of the locked kinpo order (Pantera → burger → demonio → diablo →
kinpo → phantom → scimitar → skull). Same verified pipeline as Pantera
Batches 1–4, burger Batches 1–4, demonio Batches 1–4, diablo Batches 1–4.
This doc is the full gate evidence for the 47 wired plan keys. T3 rows here
are FALLBACK (docs/anim/PROCEDURAL_AUDIT.md Kinpo-Batch-1 entry), never the
correct mapping, to be re-matched to T7 Asuka rows when decode lands.

## 0. Bank — VERIFIED, not assumed

Kinpo's T3 bank is **jin**, by four-way file evidence:

1. `kinpo.json` `t3_source` = `jin`, `t3_bank` = `moveset_jin.json`, on
   BOTH the #1096 branch (blob e69c5640…) and current main (blob 614c1e0a…).
2. `game/assets/anim/t3/` on main contains a `jin` directory
   (`hit_frames.json` + `rows.pack.json` + `skeleton.json` + the t3_* clips).
3. Job 1 bank `jin`: 220 rows.
4. Job 2 kinpo entries: 525, ALL bank `jin` (525 = the #1096 moves count).
5. Job 4 jin candidates: 47.

Bank resolution, documented not assumed: kinpo's T7/T8 base IS Asuka
(`tekken_base` `Asuka`, `merge_sources` bases t8/t7 `asuka`), but Asuka
debuted in Tekken 5 and has NO T3 bank in this repo (no `asuka` dir under
`t3/`), so the file's T3 fallback bank is jin, consistently applied
everywhere: `t3_source`, `t3_bank`, every `anim_ref` (`t3:jin:row:N`),
every move name (e.g. `KINPO 2 (T3 jin r220)`), Job 2 bank. Same shape as
burger (Bob → bryan, because Bob has no T3 bank). The T7-Asuka re-match is
future work; this batch adjudicates against jin as the file declares.

Jin-bank rules, per-bank evidence (never a cross-bank blanket ban):

- Row 35 EXISTS here: hit_frames `[11,12,39,535,0,1]` (LP1, throw 0),
  Job 1 stance `starts-airborne` (y0 1.769 vs standingY 1.027). NOT
  blanket-banned by number — the stance gate rejects it for ground steps.
  Kinpo's own LP1 move `1` carries `t3_row` 35 (same class as Pantera
  LP1 → king row 38, jumping). Row 35 is NOT jin's standing row, NOT
  king's jumping chord row, NOT bryan's button-0 row, NOT heihachi's
  nonexistent row — it is jin's starts-airborne LP1 row.
- Row 220 EXISTS as a STANDING RP2 row here: hit_frames
  `[12,12,41,1042,0,2]`, Job 1 stance standing, travel 0.216.
  Gate-adjudicated like any row, never blanket-banned. Kinpo's own RP2
  move `2` carries `t3_row` 220 — clean. Row 220 is NOT king's jumping
  chord row, NOT bryan's button-0 row, NOT heihachi's jump RK4 row.
- Jin row 216 is a JUMP row (demonio Batch 3 warning) — NOT king row
  216's dash Konvict Kick. It appears in this batch only as a Job 4
  orphan (no kinpo Job 2 move carries it), never as a candidate.
- Jin Job 1 carries a `duck-dip` stance (16 rows: 123, 189, 192, 210, 211,
  212, 213, 235, 257, 367, 377, 381, 385, 387, 389, 397), handled like
  crouch: STANCE-SOFT (review) for non-crouch contexts. No Batch 1 step
  hits a duck-dip candidate, so no review step arises from it.

Gap-1 (diablo method): main jin `hit_frames.json` blob `54b38e63…` and
`skeleton.json` blob `26f72eb7…` are IDENTICAL on #1096 and current main.
Main jin `rows.pack.json` blob `7bafa36a…` (226 rows) DIFFERS from #1096's
`141fbc8d…` (220 rows) — the 6 extra rows are exactly the #1109 bake's jin
rows (89/112/247/288/339/357); the main pack is a SUPERSET of the #1096
pack (0 rows removed). Gates use hit_frames (identical) + Job 1 profiles,
NOT the pack, so no suspension follows from the pack drift — and every
wired row (92/93/183/220/221/222/223) is verified present in BOTH packs.

## 1. Universe (derived FIRST, measured from the file)

Base = #1096 kinpo.json: 525 moves / 101 strings entries. Main = 482 moves
+ 43 quarantined = 525 exactly; 0 main-only moves; strings lists identical
(101/101) between #1096 and main.

Batch 1 scope = every step buttoned, all-button union ⊆ {LP1, RP2}:

- **32 canonicals**: 24 pure single-button + 8 chord-involved.
- 27 planned (strike) + 5 CSV-only (throw/grapple, audited, never planned).
- Provenance: 25 in main moves, 7 quarantined-only (live when #988
  merges), 0 in-1096-only.
- Contexts: standing 16, crouch 7, ws 7, jump 2.
- CSV rows: 52 = 32 canonicals + 20 source-variant twins.
- Plan keys: **47** = 27 planned canonicals + 20 twins.

CSV-only keys (5): `TACKLE.1,1`, `TACKLE.1,1,1`, `TACKLE.1,1,1,1`
(narrow-rule grapple label TACKLE, class string), `df+1,2` (class throw,
T8 Asuka `Falling Tower`), `ws2,1+2` (class throw, T8 Asuka `Kohaku`).

Canonicalization (CORRECTED rule, mandatory): strip ONLY a trailing
`~t[378].[a-z]+(.N)?$` suffix, then a trailing `*` hold marker.

- **Input-~ canonicals in Batch 1 scope: 0.** Kinpo's inventory is inert
  on this axis, like Pantera/burger — unlike demonio/diablo.
- The file's ONLY old-vs-corrected diff is one key, `3~4,D/F`, which is
  OUTSIDE Batch 1 scope (step `3~4` is an LK3 cancel, step `D/F` is
  buttonless). Under the old rule it would have collapsed to a bogus
  single `3`; under the corrected rule it stays its own key for a later
  batch. No Batch 1 plan is affected by the correction.
- `__main` canonicals in Batch 1 scope: 0. (Job 3 log kinpo `__main`
  targets `1+2__main`, `f+1__main`, `d+1+2__main` all have EMPTY pass-all
  lists, so the burger Batch 2 prefix-vs-`__main` dedupe fires zero times
  here — the dedupe code is present, the duplicate count is 0.)
- Corrupted keys in Batch 1 scope: 0 (no diablo-style `df+1,&#58;2` key).

Spelling quirks KEPT (diablo Batches 2–3 / burger Batch 2 precedent):
`df+1,2` (throw, CSV-only) vs `d/f+1,2` (planned string) are distinct
canonicals; `db+1,2` vs `d/b+1,2` are distinct; `WS.2,1` vs `ws2,1` are
distinct canonicals (both ws context after this lane's `ws2` fix — see
§5). Nothing is merged or smoothed over.

Near-miss grapple labels (narrow rule applied literally, documented not
hidden): `NANIWA_ULTIMATE_TACKLE.2,1,1,2` and
`NANIWA_ULTIMATE_TACKLE.2,1,2,1` (label `NANIWA_ULTIMATE_TACKLE` ≠
`TACKLE`) and `Tackle.2,1,2,1` (label `Tackle` ≠ `TACKLE`,
case-sensitive) stay PLANNED but are unmapped-all — every step has no
candidate, no row is wired, so no throw clip is ever played as a strike.
The plan's observable behaviour (no row plays) is identical to CSV-only;
only plan-key presence differs, and that presence is the precedent-correct
filing.

## 2. Drift census (1096 vs current main, BOTH ways)

Full file, 525 keys: same 253 / damage-only 168 / anim_ref-changed 103 /
ROW-CHANGED 1. No main-only keys, no absent-on-main keys.

- Damage differs (ALL moves where damage differs, any row status): **227**.
- Damage-only (damage differs AND row + anim_ref same): **168**.
- Both figures are true under their definitions; never silently pick one.
  The 59-move gap = moves whose damage differs AND whose row or anim_ref
  also changed (the 1 row-changed move + 58 of the anim_ref-changed moves
  also carry damage changes). Damage-only drift does NOT suspend (damage
  ≠ animation).

Row-change re-check (EVERY row-changed move vs Batch 1 scope): the full
file contains exactly ONE row-changed move, `1` (35 → None). Its Batch 1
impact is exactly 2 steps, both SUSPENDED-DRIFT (see §4). No other Batch 1
prefix is row-changed.

## 3. Step table

89 steps total (76 planned-string steps + 13 CSV-only steps).

- Planned steps: **19 verified / 0 review / 57 unmapped**.
- Unmapped split (planned): **2 suspended-drift + 3 rejected-candidate +
  52 no-candidate**.
- Canonical status (planned only): 4 verified-all / 5 partial /
  18 unmapped-all / 0 review-only.
- Plan-key last-step: 12 verified / 35 unmapped.
- Verified rows (7 distinct, all in main's jin pack): 92, 93, 183, 220,
  221, 222, 223. Hit_frames buttons: 92→3 (LP1+RP2 chord), 93→2, 183→2,
  220→2, 221→1, 222→2, 223→2; all throw flag 0; all Job 1 stance standing.

Verified-all strings (4): `2,1` [220,221], `2,1,2` [220,221,222],
`2,1,2,2` [220,221,222,223], `d+1+2,2` [92,93] (crouch, GATE-NOTE).

Partial strings (5): `2,1,1+2` [220,221,unmapped],
`2,1,d+1+2` [220,221,unmapped], `b+2,1+2` [unmapped,92-fill],
`d+1+2,1` [92,unmapped], `d+1+2,1,2` [92,unmapped,183].

## 4. Every wired fill (verified only)

1. `2,1` family (recorded-path + prefix-move): step RP2 ← jin row 220
   (standing, hf [12,12,41,1042,0,2], SOFT window [4,8] armR peak 6);
   step LP1 ← row 221 (standing, hf [14,14,43,1042,0,1], SOFT window
   [5,9] armL peak 7); step RP2 ← row 222 (standing, hf
   [10,10,39,1042,0,2], SOFT window [3,7] armR peak 5); step RP2 ← row 223
   (standing, hf [17,17,60,1042,0,2], SOFT window [6.5,10.5] armR peak 8).
   Wired in: `2,1`, `2,1,2`, `2,1,2,2` (verified-all) + twins
   `2,1~t7.asuka`, `2,1~t7.asuka.2`, `2,1~t8.asuka`, `2,1,2~t8.asuka`;
   first two steps of `2,1,1+2` + twins and `2,1,d+1+2` + twins.
2. `d+1+2` family (prefix-move + recorded-dest): step d+1+2 ← row 92
   (standing chord, hf [10,10,39,1042,0,3], SOFT window [3,7] armL peak 5
   / armR peak 3); step RP2 ← row 93 (standing, hf
   [10,10,39,1042,0,2], SOFT window [3,7] armR peak 3); step RP2 ← row 183
   (standing, hf [13,13,60,535,0,2], SOFT window [4.5,8.5] armR peak 6).
   Wired in: `d+1+2,2` (verified-all) + `d+1+2,1` step 1 +
   `d+1+2,1,2` steps 1 and 3. GATE-NOTE on all five: standing rows
   verified for crouch-context steps (demonio Batch 1 / diablo Batch 1
   precedent — the gate flags crouch rows for non-crouch steps, not
   standing rows for crouch steps; re-adjudicate if the gate tightens).
   Job 2 flags rows 93/183 `HARD stance` — that divergence is documented
   here, and the precedent is followed, not silently overridden.
3. `b+2,1+2` last step 1+2 ← **Job 3 fill row 92** (the batch's only Job 3
   fill): target `b+2,1+2`, exact level (filed h == played h), FULL
   provenance (`moveset_demonio:1+2__main(LP+RP)`,
   `moveset_demonio:d+1+2(2+LP+RP)`, `moveset_demonio:1+2~t3.jin(LP+RP)`,
   `moveset_scimitar:d+1+2(2+LP+RP)`, `moveset_kinpo:d+1+2(2+LP+RP)`),
   timing 1.5, HARD gates pass (button 3 == bits 3, throw 0, standing for
   standing context), SOFT proxy passes (window [3.0,7.0], armL peak 5 /
   armR peak 3). The Job 2 donor row 32 (jump clip) is NOT wired — donor
   retirement is designed: the plan replaces single-row resolution
   wholesale. Row 105 (exact, ROW-ONLY) documented, not wired.
   Wired in: `b+2,1+2` + twins `b+2,1+2~t7.asuka`,
   `b+2,1+2~t7.asuka.2` (partial, last step verified).

## 5. Rejected / suspended / held candidates (every one)

SUSPENDED-DRIFT (2 steps, never wired on stale data): `1,1` step 1 and
`1,2` step 1 — prefix move `1` ROW-CHANGED 35 → None (#1096 vs current
main). Stale candidate row 35 (prefix-move) documented. Row 35 would fail
the stance gate for ground steps regardless (starts-airborne).

Rejected candidates (3 planned steps):

- `d+1+2,1` step 2 (prefix `d+1+2,1`): candidate row 177
  (recorded-dest, the whole-string move's own row) REJECTED: button 12
  ≠ step bits 1. Row 177 is a chord/kick row (hf
  [15,15,44,1042,0,12]), not an LP1 row. Job 2 verdict for `d+1+2,1` is
  `HARD string-ender-on-chord` — consistent.
- `d+1+2,1,2` step 2 (prefix `d+1+2,1`): candidate row 177
  (prefix-move) REJECTED: same button 12 ≠ 1 reason.
- `d/f+1,2` step 1 (prefix `d/f+1`): candidate row 179 (prefix-move)
  REJECTED: airborne row (stance jump; y0 0.943 ymax 1.519 vs standingY
  1.027). Job 4 independently joins the same row 179 for this step and
  rejects it for the same reason (see §6).

Held (review, row null — none in this batch): 0 review steps. In
particular, no STANCE-SOFT and no SOFT-proxy-fail steps occur in Batch 1
scope. The ws-context steps (`WS.2,1`, `ws2,1` family) have no candidates
at all, so the ws→standing soft-stance rule never fires.

No-candidate steps (52 planned steps): every intermediate prefix is
T8-sourced with no T3 row and no recorded path, and no Job 3 exact-prefix
target covers it. Their correct clips come from #988 Step 2 (original T8
refs) or future extraction — never from a T3 row recorded as correct.
Notable no-candidate families: `b+2,1` (both steps), `d/b+1,2`,
`d/f+1,2` step 2, `db+1,2`, `f+2,NWG.1+2`, `uf+1,2`, `uf+1,NWG.2`,
`ws2,1` family (all steps), `WS.2,1` (both steps).

Job 3 candidates documented but NOT wired (all of them):

- `2,1,1+2` last step: row 92 soft-nofiled FULL (filed_level null),
  row 105 soft-nofiled ROW-ONLY, row 110 soft-nofiled ROW-ONLY — soft ≠
  exact, never wired, even though row 92 is the same row wired for
  `b+2,1+2` (different target, different exactness — no cross-target
  inheritance).
- `2,1,d+1+2` last step: NO Job 3 target at all (exact-prefix rule —
  no inheritance from the `d+1+2` or `b+2,1+2` targets).
- `1,1` / `1,2` step 1: rows 92/105 exact ROW-ONLY — documented, and
  suspension blocks fills regardless.
- `d/b+1,2` step 2: row 108 soft-filed ROW-ONLY, row 111 exact ROW-ONLY,
  row 122 soft-filed ROW-ONLY — ROW-ONLY never wires.
- `ws2,1` step 1 (reported on all 5 ws2-family strings sharing the
  prefix): rows 92/105 exact ROW-ONLY — documented, not wired.

## 6. Job 4 (CORRECTED join only)

Join rule: jin candidate joins a step iff Job 2 has a kinpo entry key ==
step prefix, row == candidate row, step == `own`. The naive cross-fighter
join on key-prefix equality is INVALID and was never used. A join NEVER
promotes a candidate by itself.

- Joined steps: **1** — `d/f+1,2` step `d/f+1`, row 179 (peaks armL 1 /
  armR 2), REJECTED (airborne jump row, same reason as the step's own
  candidate). No step is promoted by Job 4 in this batch.
- Orphans (jin candidates no kinpo Job 2 move carries, any step): **16** —
  rows 85, 91, 99, 100, 104, 127, 170, 171, 172, 209, 216, 226, 239, 250,
  256, 262. (Rows 85/91 were also demonio's orphans — same bank, same
  finding, independently re-derived for kinpo. Row 216 here is jin's jump
  row, not king's dash row.)

## 7. Pipeline notes specific to this lane

- `ws2` context fix: lowercase no-dot while-standing spellings (`ws2`,
  `ws1+2`, …) are WS context, not standing — same move as `WS.2`,
  spelled differently. The spelling quirk is kept (distinct canonicals),
  the context is consistent. This changes the recorded context of the
  `ws2,1` family from standing to ws; it changes NO wiring (all those
  steps are unmapped with no candidates).
- Row dual-role caution (Pantera Batch 4): row 92 is verified for
  `d+1+2` steps, for `d+1+2,1`/`d+1+2,1,2` steps, AND as a Job 3 fill for
  `b+2,1+2` — each verification is its own gate pass (button + stance +
  throw + SOFT proxy for that step's bits/context), never inherited from
  another string. Row 92's Job 3 candidacy for `2,1,1+2` (soft-nofiled)
  does NOT transfer to a verification.
- Donor retirement is designed: `b+2,1+2`'s Job 2 donor row 32 (jump clip
  for a ground move) and `2,1,d+1+2`'s Job 2 donor row 92 are replaced by
  the step plans wholesale — even where a donor row coincides with a
  verified step row (row 92), the plan, not the donor, is the wiring.
- Full 200-test suite comparison: NOT run by this lane (no full
  current-main checkout on this box — stated as a limitation in the PR
  body; CI must cover before merge). Minimal-tree node --test passes;
  node --check fighter.js OK.
- NO T8 content touched: nothing in `t8_quarantine_20261024` is modified;
  the quarantine section is read for classification only.

## 8. Play-verify checklist (parent browser delegation, AFTER merge + deploy + sync, phone portrait)

Play each wired kinpo Batch 1 string; feet grounded where the step is
grounded; no step plays a jumping row for a ground step; no step plays
row 35 or row 220 unless genuinely airborne per the JIN bank's profiles
(row 220 here is a STANDING RP2 row — it SHOULD play for RP2 steps):

- `2,1`: rows 220/221, both standing, grounded.
- `2,1,2`: rows 220/221/222, all standing, grounded.
- `2,1,2,2`: rows 220/221/222/223, all standing, grounded.
- `2,1,1+2` + twins: rows 220/221, then NO row (last step unmapped —
  the donor jump row 32 must NOT play).
- `2,1,d+1+2` + twins: rows 220/221, then NO row (last step unmapped —
  no row 92 as a whole-string clip).
- `d+1+2,2`: rows 92/93, crouch context (standing rows, GATE-NOTE).
- `d+1+2,1`: row 92, then NO row (recorded-dest row 177 must NOT play
  for the LP1 step).
- `d+1+2,1,2`: row 92 / NO row / row 183.
- `b+2,1+2` + twins: NO row (first step), then row 92 (Job 3 fill chord).
- `1,1` + twins, `1,2` + twins: NO row any step (stale row 35 must NOT
  play; step 1 suspended-drift).
- `d/f+1,2` + twin: NO row any step (jump row 179 must NOT play for the
  crouch-context first step).
- `b+2,1`: NO row any step (donor row 35 must NOT play).
- `ws2,1` family, `WS.2,1` + twin, `d/b+1,2` + twin, `db+1,2`,
  `f+2,NWG.1+2`, `uf+1,2`, `uf+1,NWG.2`: NO row any step (donor rows
  35/220/221/92/93/277 must NOT appear as whole-string clips).
- No step in any Batch 1 string plays row 35 (starts-airborne per jin
  Job 1) for a ground step. Row 220 plays ONLY for RP2 steps (it is a
  standing RP2 row in this bank — grounded, not airborne).
- No step plays a row from another bank (king/bryan/heihachi rows are
  never kinpo rows).
- Kinpo Batch 1 spot-checks undisturbed: none (this is kinpo's first
  batch; later batches go cumulative on this test).

This lane claims NO play verification — tests + file evidence only.
Playing is the parent's step after merge + deploy.
