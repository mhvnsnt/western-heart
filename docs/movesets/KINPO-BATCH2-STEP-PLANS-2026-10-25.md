# Kinpo Batch 2 step plans (LK3/RK4-only strings, 2026-10-25)

Stack: kinpo Batch 1 branch `feat/kinpo-batch1-step-plans-20261025` (PR #1117,
head `3218a58fdaed5aecada6d75b96fb20f670ac87e7`, re-verified before branching)
→ this branch `feat/kinpo-batch2-step-plans-20261025`. Merges AFTER #1117
(which merges after #1096, itself blocked on 12 pre-existing failures / a gate
decision owed — this lane fixes neither and merges nothing itself).

## Scope

Kinpo strings whose steps are ALL LK3/RK4-only (any directionals, any
contexts: standing/crouch/jump/ws). Pure single-button first, then
chord-involved (LK3+RK4 chords). Measured from the file, not assumed.

## Universe (measured first)

- Base = Batch 1 branch kinpo.json: 525 moves / 101 strings / 47 plans.
  Batch 1 branch moves == #1096 moves exactly (verified); Batch 1 branch
  strings == #1096 strings exactly (verified).
- Current main: 482 moves + 43 quarantined = 525 exactly; 0 main-only moves;
  strings lists identical (101/101). Main kinpo.json blob `614c1e0a…` is
  UNCHANGED since Batch 1's baseline.
- **12 canonicals** (11 pure + 1 chord-involved: `FC.3+4,3`); **all 12
  planned, 0 CSV-only**; 20 CSV rows (12 canonicals + 8 twins); **20 plan
  keys** (12 planned canonicals + 8 twins inheriting canonical steps
  verbatim). Contexts: standing 1, crouch 7, jump 4, ws 0. Provenance: 12 in
  main moves, 0 quarantined-only, 0 Batch 1-branch-only.
- Canonicals: `FC.3+4,3`, `b+3,4`, `d/b+4,4`, `d/b+4,4,4`, `d/f+4,4`,
  `db+4,3`, `db+4,4`, `db+4,4,4`, `u/f+4,3`, `u/f+4,4`, `u/f+4,4,4`,
  `u/f+4,4,4,4`.
- Variants (8, all class `string`, all planned): `FC.3+4,3` has 3 twins
  (`~t7.asuka`, `~t7.asuka.2`, `~t7.asuka.3`); `b+3,4` has 2; `d/b+4,4` has 1;
  `d/b+4,4,4` has 2; the other 8 canonicals have 0 twins.
- Sources: 8 canonicals carry strings-list entries; `d/b+4,4` and
  `d/b+4,4,4` are moves-only (no strings-list entry) — noted, not a problem:
  their steps are adjudicated from prefix moves alone.

## Bank (verified, carried forward — not re-assumed)

Kinpo's T3 bank is JIN (Batch 1 four-way proof, re-verified here):
kinpo.json `t3_source: 'jin'`, `t3_bank: 'moveset_jin.json'` on BOTH the
Batch 1 branch and current main; `game/assets/anim/t3/` on main contains a
`jin` dir (hit_frames + rows.pack + skeleton); Job 1 bank jin (220 rows);
Job 2 kinpo entries all bank jin (525); Job 4 jin candidates (47).
Kinpo's T7/T8 base IS Asuka (`tekken_base` Asuka, merge_sources t8/t7
asuka), but Asuka has NO T3 bank in this repo (no `asuka` dir under `t3/` —
she debuted in Tekken 5), so the file's T3 fallback bank is jin,
consistently applied everywhere — the burger pattern (Bob → bryan). The
T7-Asuka re-match is future work; this batch adjudicates against jin as
the file declares. The pack dir does NOT differ from the moveset bank name
here (unlike diablo's heihachi/heihachi_on_jin split).

Bank-specific row rules (never cross-bank): row 35 EXISTS here
(hit_frames `[11,12,39,535,0,1]`, Job 1 stance starts-airborne) — not
blanket-banned by number, but the stance gate rejects it for ground steps;
kinpo's own LP1 move `1` carries `t3_row` 35. Row 220 is a STANDING RP2 row
here (hit_frames `[12,12,41,1042,0,2]`, Job 1 standing) — gate-adjudicated,
NOT king's jumping chord row, NOT bryan's button-0 row, NOT heihachi's
jump RK4 row. Jin row 216 is a JUMP row, NOT king row 216's dash Konvict
Kick (it appears only as a Job 4 orphan).

Gap-1 (diablo method, replicated): Batch 1 branch vs main — jin
hit_frames blob `54b38e63…` IDENTICAL, jin skeleton blob `26f72eb7…`
IDENTICAL. Jin rows.pack.json DIFFERS (Batch 1 branch `141fbc8d…`, 220
rows, vs main `7bafa36a…`, 226 rows) — EXPLAINED, not drift: the 6 extra
rows are exactly the #1109 bake's jin rows (89/112/247/288/339/357); main's
pack is a SUPERSET (0 rows removed). The Batch 1 branch changed only 4
files, none of them bank files, so its bank blobs equal #1096's (verified
by fetch). Cited-row profiles MATCH Job 1 vs hit_frames for every verified
+ review row (80/193/205/207/210/211/212 — button, throw, stance all
agree). Every wired row is present in the CURRENT main jin pack (226 rows).

## Step tallies

29 steps, all planned-string steps (0 CSV-only steps):
**9 verified / 4 review / 16 unmapped / 0 suspended-drift.**
Unmapped split: **16 no-candidate + 0 rejected-candidate + 0 suspended.**
Canonical status (planned): 2 verified-all / 3 partial / 7 unmapped-all /
0 review-only. Plan-key last-step: 2 verified / 3 review / 15 unmapped.

## Every wired fill (verified only, all gate-verified own/recorded-path rows, T3 FALLBACK)

- `u/f+4,3` verified-all: step `u/f+4` ← **80** (prefix-move, jump RK4,
  hit_frames `[25,25,66,535,0,8]`, Job 1 stance jump); step `3` ← **193**
  (recorded-dest, jump LK3, hit_frames `[35,37,65,535,0,4]`, Job 1 stance
  jump). SOFT gate waived (jump context, Batch 1 precedent).
- `u/f+4,4` verified-all: step `u/f+4` ← **80** (prefix-move, jump RK4);
  step `4` ← **207** (recorded-dest, jump RK4, hit_frames
  `[47,47,86,271,0,8]`, Job 1 stance jump). SOFT gate waived (jump context).
- `u/f+4,4,4` partial: steps 1–2 ← **80/207** (prefix-move); step 3
  review (candidate 210 held, see below).
- `u/f+4,4,4,4` partial: steps 1–2 ← **80/207** (prefix-move); steps 3–4
  review (candidates 210/211 held, see below).
- `d/f+4,4` partial: step `d/f+4` ← **205** (prefix-move, crouch RK4,
  hit_frames `[16,16,62,271,0,8]`, Job 1 stance crouch). This is NOT a
  gate-note case: row 205's Job 1 stance IS crouch, so it passes for
  crouch outright (contrast Batch 1's d+1+2 family, where standing rows
  92/93/183 verified for crouch steps under the demonio Batch 1
  precedent). Step 2 review (candidate 212 held, see below).
- The u/f+4 family matches demonio Batch 2's u/f+4 family row-for-row
  (80/193/207/210/211) — same jin bank, same inputs, independently
  re-derived for kinpo; not copied.

## Review holds (4 steps, row null, NOT wired)

- `d/f+4,4` step 2: candidate **212** (recorded-dest, duck-dip RK4,
  hit_frames `[13,13,70,271,0,8]`) passes HARD gates for crouch, then
  SOFT limb-peak proxy FAILS: window `[4.5,8.5]` (active `[13,13]` / 2 ± 2),
  legR peak 12 outside. Held at review, never wired. Same row, same result
  as demonio Batch 2's `d/f+4,4` step 2.
- `u/f+4,4,4` step 3: candidate **210** (recorded-dest, duck-dip RK4,
  hit_frames `[24,24,70,271,0,8]`) STANCE-SOFT for a jump-context step.
  Held at review. Same row, same result as demonio Batch 2's `u/f+4,4,4`
  step 3.
- `u/f+4,4,4,4` step 3: candidate **210** (prefix-move) STANCE-SOFT
  duck-dip for a jump-context step. Held at review.
- `u/f+4,4,4,4` step 4: candidate **211** (recorded-dest, duck-dip RK4,
  hit_frames `[22,22,70,535,0,8]`) STANCE-SOFT for a jump-context step.
  Held at review.

## Unmapped steps (16, all no-candidate)

Every unmapped step has NO candidate row at all (recorded path + prefix
move both absent): `FC.3+4,3` steps 1–2; `b+3,4` steps 1–2; `d/b+4,4`
steps 1–2; `d/b+4,4,4` steps 1–3; `db+4,3` steps 1–2; `db+4,4` steps 1–2;
`db+4,4,4` steps 1–3. These are T8-sourced prefixes with no T3 row; their
correct clips come from #988 Step 2 (original T8 refs) or future
extraction — never from a T3 row recorded as correct. Zero
rejected-candidate steps, zero suspended steps.

Whole-string donor rows documented in the CSV (never wired — donor
retirement is designed): row 199 for the `b+3,4`, `d/b+4,4`, `d/b+4,4,4`,
`db+4,4`, `db+4,4,4` families; row 195 for `db+4,3` and `FC.3+4,3`.
The whole-string moves' own rows 212/210/211 (for `d/f+4,4`,
`u/f+4,4,4`, `u/f+4,4,4,4`) are the review-held candidates above, not
wired. The plans replace single-row resolution wholesale, even for CLEAN
donors, because one row cannot be correct for a multi-hit string.

## Job 3 (0 report entries — honestly empty, not missing)

No Batch 2 step prefix has a pass-all candidate at all. The 4
match_search kinpo kick keys (`u/f+4,4,4`, `u/f+4,4,4,4`, `FC.3+4,3`,
`FC.3+4,3~t7.asuka.3`) all carry EMPTY pass-all lists in job3.log, so
they contribute zero candidates. The dedupe (prefix vs `__main`
duplicate pass-all rows) fires zero times — there is nothing to dedupe.
**Job 3 fills wired: 0.** No SOFT fill, no ROW-ONLY fill, no cross-target
inheritance. (Nearby non-targets, correctly NOT consulted: log key `3+4`
pass-all `[131,132,196]` is a single-move key, not a Batch 2 step prefix;
log key `hFC.3+4` pass-all `[]` is a different key from `FC.3+4`.)
The Job 3 agreement note fires zero times — it fires ONLY for
actually-wired gate candidates (demonio Batch 4 wording fix), and no
Batch 2 gate candidate disagrees with a Job 3 candidate because no Job 3
candidate exists.

## Job 4 (4 joins, none promoting — CORRECTED join only)

All 4 joins are no-action on already-verified steps (a join NEVER
promotes by itself): `u/f+4,3` step `3` row 193; `u/f+4,4` step `4` row
207; `u/f+4,4,4` step `4` row 207; `u/f+4,4,4,4` step `4` row 207
(peaks armL 0 / armR 2 / legL 0 / legR 0 in each case). Orphans (16, same
set as Batch 1, independently re-derived): jin rows 85, 91, 99, 100, 104,
127, 170, 171, 172, 209, 216, 226, 239, 250, 256, 262. Row 216 here is
jin's jump row, NOT king row 216's dash Konvict Kick.

## Drift census (both ways — both true under their definitions)

Full file, Batch 1 branch vs current main (525 keys): 253 same / 168
damage-only / 103 anim_ref-changed / 1 ROW-CHANGED. Damage differs on 227
moves (all-status) vs 168 damage-only — the 59 gap = damage differs AND
row or anim_ref also changed. Damage-only drift does NOT suspend (damage
≠ animation). Step-prefix census: the file's ONLY row-changed move is
`1` (35→None, Batch 1 scope), and NO Batch 2 step prefix is row-changed
— so Batch 2 has **0 suspended-drift steps**. Per-prefix drift is
recorded in the step table (`d/b+4` family damage-only; `b+3,4` /
`db+4` families anim_ref-changed (T8/T7 source; row N/A); the rest same
or damage-only).

## Canonicalization, spelling, corrupted keys

- Corrected rule applied throughout (strip ONLY a trailing
  `~t[378]` source-variant suffix, then a trailing `*` hold marker).
- Input-~ canonicals in Batch 2 scope: **0** — kinpo is inert on this
  axis, like Pantera/burger (Batch 1 also 0).
- The file's ONLY old-vs-corrected diff is one key, `3~4,D/F`, and it is
  **NOT Batch 2 scope**: its steps are `3~4` (LK3 cancel) + `D/F`
  (buttonless direction step) — because D/F carries no button, the key
  is not all-buttoned, so it is a rest key (Batch 4 scope). Under the old
  rule it would collapse to a bogus single `3`; under the corrected rule
  it stays its own key for Batch 4. No Batch 2 plan is affected.
- `__main` canonicals in Batch 2 scope: 0. Corrupted keys in Batch 2
  scope: 0 (no diablo-style escaped-colon key).
- Spelling quirks kept as stored keys: `d/b+4,4` vs `db+4,4` and
  `d/b+4,4,4` vs `db+4,4,4` are distinct canonicals with different
  evidence (the `d/b+` spellings are moves-only; the `db+` spellings
  carry strings-list entries) — not merged, not smoothed over.
- WS-context fix (Batch 1): lowercase no-dot while-standing spellings
  are WS context, not standing — no Batch 2 key uses a `ws` spelling
  (contexts here: standing 1, crouch 7, jump 4, ws 0), so the fix changes
  nothing in this batch.

## Tests (file evidence only — NOT play-verified)

Minimal-tree `node --test`: **24 pass / 0 fail** (13 Batch 1 cumulative +
11 Batch 2); `node --check fighter.js` OK. Formatter round-trips the
Batch 1 branch file byte-identically; all non-plan keys identical, all 47
Batch 1 plans deep-equal, moves 525 / strings 101 unchanged. Batch 1 test
diff proves every CONTENT assertion preserved verbatim (only counts,
extra-keys/complement counts, const additions, header notes changed —
the burger Batches 2–4 fix; Pantera's latent break NOT copied).
**Limitation, stated in the PR body:** full 200-test suite comparison
NOT run — no full current-main checkout on this box; CI must cover
before merge.

## Files

- `game/assets/movesets/kinpo.json` (67 plans: 47 Batch 1 + 20 Batch 2)
- `docs/movesets/KINPO-BATCH2-STEP-PLANS-2026-10-25.md` (this doc)
- `game/tests/kinpo-batch2-step-plans.test.mjs` (+ cumulative Batch 1 test)
- `docs/anim/PROCEDURAL_AUDIT.md` (append-only vs the Batch 1 branch base)
- Workspace: `~/workspace/kinpo-batch2/` (derive/build/wire/file_pr scripts,
  universe, step table, Job 3/Job 4 reports, drift census, CSV, plans,
  minimal tree, PR body)
