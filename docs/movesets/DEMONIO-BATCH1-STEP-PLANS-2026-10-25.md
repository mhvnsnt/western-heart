# Demonio Batch 1 — step plans (LP1/RP2-only strings) — 2026-10-25

## What this is

Demonio Batch 1 after burger's completion (PR #1107), same verified pipeline
(Pantera Batches 1–4 + burger Batches 1–4): each move mapped to its EXACT
animation from the actual Tekken files; strings wired as step-plans (one
verified row per prefix step + hit-window timing) via the #1096 engine path,
or left UNMAPPED. Never invented anim refs, damage, slot counts, or names.
A single row is NEVER a correct multi-hit string — wiring a plan replaces
single-row resolution wholesale, even for CLEAN donors, because one row
cannot be correct for a multi-hit string.

## Universe (measured, not assumed)

Base = #1096's demonio.json (764 moves, 156 strings entries) plus current
main's strings-list entries. **41 canonical LP1/RP2-only strings** (button
union subset of {LP1, RP2}, every step buttoned, any directionals): **32 pure
single-button + 9 chord-involved** (at least one LP1+RP2 step). **59 plan
keys** (34 planned canonicals + 25 twins/variants inheriting canonical steps
verbatim, Batch 1 twin precedent); **66 CSV rows** (41 canonical + 25
variants), pure first, then chord-involved. Contexts over the 41: 26
standing, 7 crouch, 6 jump, 2 ws. Provenance: 35 canonical in current main
moves/, 6 quarantined-only (in main's t8_quarantine_20261024, restored to
playable by #988 Option B; their plans live on the #1096 base where the
moves exist and become live when #988 merges), 0 in #1096 only. This PR does
not touch the quarantine section.

Planned = LP1/RP2 strike strings only (34 canonicals). CSV-only, never
planned (7 canonicals): the TACKLE family (`TACKLE.1,1`, `TACKLE.1,1,1`,
`TACKLE.1,1,1,1`, `TACKLE.2,2`, `TACKLE.2,2,2`, `TACKLE.2,2,2,2` — first-step
label in the narrow grapple set {PILE_DRIVER, ARM_BREAKER, TACKLE}) plus
`b+2,1:u/f` (its OWN move entry's move_class is `throw`, while plain
`b+2,1` is `string` — a per-key exclusion, not a canonicalization error).
Their steps are strike-gate-excluded; throw-row verification for them is
owed separately, not a step-plan.

## Bank verification (verified, not assumed)

Demonio's T3 bank is **JIN** — verified four ways, not assumed (burger's
bob/bryan correction is the cautionary tale): demonio.json `t3_source:
'jin'`, `t3_bank: 'moveset_jin.json'` (BOTH the #1096 file and current
main); `game/assets/anim/t3/` on main contains a `jin` directory (22 banks);
Job 1 / Job 2 / Job 4 banks for demonio are all `jin` (Job 1: 220 jin rows;
Job 2: 764 demonio entries, bank jin; Job 4: 47 jin candidates). Demonio's
T7 base IS Jin (roster base map Jin→Demonio) and Jin exists in Tekken 3, so
unlike burger (T7 base Bob has no T3 bank, falls back to bryan) demonio
needs no bank substitution. All gates run against jin rows.

Jin-bank rule change vs the king/bryan batches (documented, evidence-based,
not a silent divergence): jin row 220 is a **STANDING RP2 row**
(hit_frames `[12,12,41,1042,0,2]`, Job 1 stance standing, travel 0.216) —
NOT king's jumping chord row 220 and NOT bryan's button-0 row 220 — so it is
NOT blanket-banned here. It is adjudicated by the normal gates (button +
throw + stance + SOFT) like any other jin row, and it verifies for the 2,1
family step 1 (recorded-path row 220, button 2, throw 0, SOFT pass). Under
the old blanket ban, demonio's flagship 2,1 string would have lost its
verified step 1 despite passing every gate — the bank-specific rule is what
the files justify. Jin row 35 IS starts-airborne (Job 1: feet lifts
0.43/0.54, y0 1.769), so the row-35 rejection for ground steps stands; row
35 verifies ONLY in jump context (u+1,1 step 2). Jin Job 1 also carries a
`duck-dip` stance (16 rows: 123, 189, 192, 210, 211, 212, 213, 235, 257, 367,
377, 381, 385, 387, 389, 397), handled like crouch: STANCE-SOFT (review) for
non-crouch contexts, pass for crouch contexts.

## Gates per step (Pantera/burger gates, unchanged except the row-220 rule above)

Candidate = recorded path row (full-path, or dest-only for the last step)
else prefix move's `t3_row` else none. HARD = button bitmask (LP1=1, RP2=2,
chords OR-ed) + throw 0 for strike steps + stance (jump/starts-airborne fail
ground steps, pass jump steps; crouch/duck-dip rows pass only crouch steps,
else STANCE-SOFT review; ground rows fail all; ws→standing is review) +
row 35 rejected for ground steps. SOFT = Job 1 peakF proxy (window = stream
active window / 2, ±2 frames; chord steps need ≥1 limb peak in window),
VALIDATED 13/13 on Pantera Batch 1's verified steps, conservative
(proxy-fail = review, never false verify), waived for jump strings.

Job 3 (exact-prefix rule: target key == step prefix): wired ONLY on exact
level (filed == played, filed non-empty) + FULL provenance (row in
job3.log provenance list AND top10 provenance non-empty) + step HARD gates
+ SOFT proxy pass (burger refinement — stricter than Pantera Batch 4's
HARD-only fill rule). Prefix vs `__main` duplicate pass-all rows deduped
(burger Batch 2 cleanup). Job 4 (CORRECT join only: demonio-only, BANK_DIR
jin, one row per step, join iff Job 2 has a demonio entry key == step
prefix, row == candidate row, step == 'own'): a join NEVER promotes a step
by itself. The naive cross-fighter join on key-prefix equality is INVALID
and was never used.

## Tallies

- Planned steps (77): **27 verified / 1 review / 49 unmapped**.
- All steps (97): 27 / 1 / 69 (20 CSV-only steps).
- Planned canonicals: **5 verified-all / 13 partial / 16 unmapped-all /
  0 review-only**.
- Plan-key last-step: **32 verified / 25 unmapped / 2 review**.
- Verified-last-step keys (32): `1+2,2`, `1+2,2~t3.jin`, `2,1`, `2,1,2`,
  `2,1,2,2`, `2,1,2,2~t3.jin`, `2,1,2~t3.jin`, `2,1~t3.jin`, `2,1~t7.jin`,
  `2,1~t7.jin.2`, `2,1~t8.jin`, `2,2`, `b+1+2,1,2`, `b+1+2,2`, `b+1+2,2,2`,
  `d+1+2,1,2`, `d+1+2,2`, `u+1,1`, `u+1,1~t3.jin`, `u+1,1~t3.jin.2`,
  `u+1,1~t3.jin.3`, `u+1,2`, `u/b+1,1`, `u/b+1,1~t3.jin`,
  `u/b+1,1~t3.jin.2`, `u/b+1,1~t3.jin.3`, `u/b+1,2`, `u/f+1,1`,
  `u/f+1,1~t3.jin`, `u/f+1,1~t3.jin.2`, `u/f+1,1~t3.jin.3`, `u/f+1,2`.
- Job 3 fills wired: **0**. Job 4 joins: 2, none promoting. Orphans: 2
  (jin rows 85, 91 — no demonio Job 2 move carries them).
- Suspended-drift steps: **5** (all prefix move `1`, below).

## Verified steps (all gate-checked: hit_frames button == step bits, throw 0)

- `2,1` verified-all: rows 220/221 (recorded-path). `2,1,2` verified-all:
  rows 220/221/222 (recorded-path). `2,1,2,2` verified-all: rows
  220/221/222/223 (prefix-move + recorded-dest last step). `2,2`
  verified-all: rows 220/180 (prefix-move). `d+1+2,2` verified-all: rows
  92/93 (prefix-move + recorded-dest).
- First-step / single verified steps: `1+2,2` step 2 ← row 93;
  `b+1+2,1,2` step 2 ← row 183; `b+1+2,2` step 2 ← row 94; `b+1+2,2,2`
  steps 2–3 ← rows 94/181; `d+1+2,1` step 1 ← row 92; `d+1+2,1,2` step 1
  ← row 92, step 3 ← row 183.
- Jump strings (SOFT waived per Batch 1 precedent): `u+1,1` step 2 ← row 35
  (starts-airborne, correct plane for a jump step); `u+1,2` step 2 ← row 47;
  `u/b+1,1` step 2 ← row 37; `u/b+1,2` step 2 ← row 49; `u/f+1,1` step 2
  ← row 36; `u/f+1,2` step 2 ← row 48. Every jump verified row: hit_frames
  button == step bits, throw 0.
- All 21 non-jump verified steps pass the SOFT proxy outright (no waivers,
  no review holds). Verified rows (16 distinct): 35, 36, 37, 47, 48, 49, 92,
  93, 94, 180, 181, 183, 220, 221, 222, 223 — each gate-checked again per step,
  not globally (a row verified for one string/claim is not assumed verified
  for another).

Crouch-context note (documented, not hidden): the d+1+2 family's verified
rows 92/93/183 are Job 1 `standing` rows (row 92: y0 1.089 throughout, feet
on ground — a genuine standing clip, not a mislabeled crouch clip; crouch
rows sit at y0 ~0.847). This follows the burger Batch 1 precedent (d/f+1
steps verified row 146, standing): the pipeline's stance gate flags crouch
rows for non-crouch steps, not standing rows for crouch steps. The rows
pass button + throw + SOFT, and d+1+2's own moveset entry names row 92
("DEMONIO d+1+2 (T3 jin r92)", button 3 = LP1+RP2, throw 0; T7 hit_level
"(Special) (TC)(CDS)"). No new gate was invented here; if the pipeline's
stance gate is ever tightened to reject standing rows for crouch steps,
these three steps must be re-adjudicated — the observation is recorded so
that tightening is a deliberate decision, not a surprise.

## Review steps (candidate documented, row null, never played)

- `d/f+1,2` step 2: candidate row 129 (prefix-move) HELD on SOFT proxy fail
  (window [4.5, 9.0], armR peakF 3 outside). Promotion needs full FK
  threshold-crossing data (named unblock, not guessed).

## Rejected / unmapped honesty

Planned unmapped 49 = **5 suspended + 10 rejected-candidate + 34
no-candidate**.

- Suspended (never wired on stale data): all 5 are prefix move `1`
  ROW-CHANGED 41→None (#1096 vs current main) — the `1,1`, `1,1,2`, `1,2`,
  `1,2,1`, `1,2,2` step 1s. Stale candidate row 41 documented, never wired.
  Note the stakes: row 41 is a starts-airborne row — wiring it would play a
  jumping clip for ground strings (it is exactly what those strings' donor
  resolution plays today; see "Current picks"). The other 2 row-changed
  moves (`1_r41`, `u+1,1~t3.jin.2`, both 41→None) suspend nothing: neither
  is a Batch 1 string prefix.
- Rejected candidates (gate reasons verbatim): `b+1+2,1` / `b+1+2,1,2` /
  `d+1+2,1` / `d+1+2,1,2` step 1 — row 177, button 12 != step bits 1 (a
  chord row for a single-LP1 step); `b+1,2` step `b+1` — row 216, button 0
  != bits 1 AND airborne (stance jump); `d/f+1,2` step `d/f+1` — row 179,
  airborne (stance jump); `u/b+1,1` / `u/b+1,2` step `u/b+1` — row 34,
  button 3 != bits 1 (the single `u/b+1` move's own row is a 1+2-chord row);
  `u/f+1,1` / `u/f+1,2` step `u/f+1` — row 33, button 3 != bits 1 (same
  chord-row situation as `u/b+1`).
- No-candidate steps (34): intermediate prefixes are T8-sourced strings
  with no T3 row (e.g. `1,1`, `1,2`, `b+1`, `d+2`, `WS.1`, `uf+1` carry
  T8/T7-source anim_refs and `t3_row` null in both files). Their correct
  clips come from #988 Step 2 (original T8 refs) or future extraction —
  never from a T3 row recorded as correct.
- Job 3 candidates documented, never wired: `1+2` soft-nofiled FULL row 92
  (+ ROW-ONLY 105/110, target `1+2__main`); prefix `1` exact ROW-ONLY rows
  92/105 (×5 strings — ROW-ONLY, not FULL, and the steps are suspended
  anyway). No SOFT fill is inherited from #1097 (Pantera-specific, still
  unapproved, does not transfer to demonio).
- Job 4 joins documented, never promoting: `b+1,2` step `b+1` — row 216
  REJECTED (button 0 + airborne); `d/f+1,2` step `d/f+1` — row 179 REJECTED
  (airborne). Orphans: jin rows 85, 91.

## Current picks (Job 2 audited resolution, demonio_batch1_lp_rp.csv, 66 rows)

Pick kinds: own 33 / donor 29 / notation 3 / match 1. HARD-flagged: 19
rows. Donor-dominated, as in every batch so far. Sharpest wrong clips this
batch retires:

- Jumping jin row 41 (starts-airborne) as the whole-string clip for ground
  strings: `1,1`, `1,2,1`, the TACKLE family, `WS.1,1`, the `b+2,1` family
  (9 of the 10 jump-clip-for-ground-move rows). The 10th is `df+2,H.1+2`
  playing match row 32 (jump) for a crouch string.
- Standing RP2 HIGH row 220 as the whole-string clip for crouch strings
  (`d/b+2,2`, `db+2,2` — Job 2 HARD stance) and for `ws1,2`. Note the
  distinction: row 220 IS a legitimate verified step row for the standing
  2,1 family (button 2, SOFT pass) — it is the WHOLE-STRING use for crouch
  strings that is wrong, not the row itself. Plans retire whole-string
  donors even where the row itself is standing-correct.
- Donor retirement is the designed correction: step 1 of the 2,1 family
  still plays row 220, but now as a VERIFIED STEP row, not as a
  whole-string donor; later steps play their own verified rows or NO row.

## Re-baseline (Batch 1 section-0 rule, both counts)

Per prefix move, #1096-file vs current main (main moves, else main
quarantine). Full census over all 764 #1096 moves: 517 same / 164
damage-only / 80 anim_ref-changed / 3 ROW-CHANGED (`1`, `1_r41`,
`u+1,1~t3.jin.2`, all 41→None). Damage differs on 195 moves (194 with
unchanged t3_row + 1 row-changed move `1`, 11→7). The 194 splits into 164
damage-only + 30 anim_ref-changed-with-damage-change; both counts are true
under their definitions (burger Batch 2 reconciliation pattern). Damage-only
drift is noted, NOT suspending (damage is not animation; the #1039 MOD
sync, e.g. demonio LP1 damage 11→7). Main moves 671 + quarantine 93 = 764 =
#1096 moves. anim_ref-changed class is the T8/T7-source footprint (no T3 row
in either file) — those steps get candidates only via recorded path /
Job 3 / Job 4; their correct clips come from #988 Step 2.

## Gap-1 re-verification (Pantera/burger method, replicated)

Jin bank files IDENTICAL across the #1096 branch and current main
(hit_frames.json blob 54b38e635bb815db00b764cc10675a6bffb489d0,
rows.pack.json blob 141fbc8db374ef3031fe408ba8a597054abeb249,
skeleton.json blob 26f72eb7e31d4047596d043e832c02ee6dba83ed, all
API-confirmed on both refs). Cited-row profiles (Job 1 jin vs hit_frames,
button/throw/active): **25/25 MATCH** (all verified, review-candidate,
Job 3, and Job 4 rows: 33, 34, 35, 36, 37, 41, 47, 48, 49, 92, 93, 94, 105,
110, 129, 177, 179, 180, 181, 183, 216, 220, 221, 222, 223).

## Wiring

`string_step_plans` CREATED in demonio.json (demonio had none on #1096):
law + 59 plan keys. Formatter round-trip reproduces the #1096 file
byte-identically before changes; structural diff proves all non-plan
top-level keys identical, moves 764 / strings 156 unchanged. Tests:
minimal-tree `node --test` 12 pass / 0 fail (counts 764/156/59; Batch 1
keys exactly the documented 59; verified rows non-null with buttons in jin
hit_frames and throw 0, never row 35 on ground steps; review/unmapped row
null; no soft flags; flagships 2,1 / 2,1,2,2 / d+1+2,2 / u+1,1 / 1,1 /
d/f+1,2; TACKLE family + b+2,1:u/f have no plan key; verified-last-step
set exactly the 32; fighter.js step-plan markers present). `node --check
fighter.js` OK.

## Play-verify checklist (parent browser delegation, after #1096 + this PR merge + deploy + sync)

Phone portrait, human simulation. Demonio vs any fighter. (1) `2,1` /
`2,1,2` / `2,1,2,2` / `2,2`: verified-all, rows 220/221/(222)/(223)/(180),
feet grounded; old whole-string donors must NOT appear as whole-string
clips. (2) `d+1+2,2`: rows 92/93, crouching chord then follow-up; `d+1+2,1`
step 1 row 92, step 2 NO row. (3) `u+1,1` step 1 NO row, step 2 row 35
(airborne); `u/f+1,1` / `u/b+1,1` first steps NO row (their own rows 33/34
are chord rows, rejected), last steps rows 36/37. (4) `1,1` / `1,2` /
`1,2,1` / `1,2,2`: step 1 NO row (suspended — stale row 41 must NOT play);
later steps NO row. (5) `d/f+1,2`: step 1 NO row, step 2 NO row (review
candidate 129 held). (6) TACKLE family unchanged (no plan). (7) No
ground-context step plays row 35; no step plays a jumping row for a ground
step. (8) Quarantined-only strings behave per plan ONLY after #988 merges;
before that they remain quarantined on main.

## Merge order + limitations

Merges AFTER #1096 (itself blocked on 12 pre-existing failures / a gate
decision owed — this lane does not fix those and does not merge on
mergeable:true alone); rebase onto main before merging; git_merge.py only
when green + clean. Audit append is append-only vs the #1096 base — rebase
after Pantera/burger audit entries if they merge first, never overwrite.
If #1097 merges first, note its guard-map interaction (demonio has its own
guard map; Pantera's SOFT decision does not transfer). LIMITATION (honest):
full 200-test suite comparison vs pristine main NOT run — no full
current-main checkout exists on this box. Blast radius is confined by
construction: no engine changes, no moves/strings changes, no prior-plan
changes (demonio had none), doc + test + audit-append only. The suite
comparison must be run before merge (CI will also cover it). NOT
play-verified: no fight played. Nothing here is 'fixed' until the user
plays it.
