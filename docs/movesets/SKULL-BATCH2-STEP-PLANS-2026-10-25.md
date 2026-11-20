# SKULL BATCH 2 — STEP PLANS (LK3/RK4-only strings, 2026-10-25)

Stack: branch from skull Batch 1's branch `feat/skull-batch1-step-plans-20261025`
(PR #1129, head 59685c7d970e6964b677bd4454a27fb9615da106, re-verified before
branching). Merges AFTER #1129 (which merges after #1096, itself blocked on
12 pre-existing failures / a gate decision owed — this lane fixes neither
and merges nothing itself). Plans accumulate: #1096 engine → skull B1 (91
keys) → skull B2 (29 keys) = 120 keys total. This PR does not touch
fighter.js, pantera.json, burger.json, demonio.json, diablo.json,
kinpo.json, phantom.json, or scimitar.json. No T8 content touched.

## Bank — VERIFIED, not assumed (four-way file evidence, carried from Batch 1)

Skull's T3 bank is BRYAN — NATIVE, not a fallback. skull.json t3_source
'bryan', t3_bank 'moveset_bryan.json' on BOTH the Batch 1 branch file and
current main (main blob 6cfe81ed…); tekken_base Bryan Fury, merge_sources
t8/t7/t3 all bryan. game/assets/anim/t3/bryan/ exists with hit_frames +
rows.pack + skeleton; pack bank divmot12_bryan.bin. Pack dir = bank name
(no diablo-style split). Job 1 bryan: 160 rows (hit_frames has 210 rows;
Job 1 covers 160 of them). Job 2 skull entries: ALL 688 bank bryan, zero
exceptions. Job 4 bryan candidates: 27. Same bank as burger's fallback,
but here it is the character's own T3 bank — row identities re-derived
from the files in Batch 1, not copied from burger.

### Bryan-bank row rules (per-bank evidence — never a cross-bank blanket ban)

- Row 35 DOES NOT EXIST (absent from hit_frames AND Job 1) — no row-35
  rule applies at all.
- Row 220 EXISTS in hit_frames [25,26,65,271,0,0], button 0, ABSENT from
  Job 1 — fails every single-button gate, no stance profile. NOT jin's
  standing RP2 row, NOT king's jumping chord row, NOT heihachi's jump
  RK4 row.
- Row 216 EXISTS in hit_frames [20,21,30,271,0,0], button 0, ABSENT from
  Job 1 — same treatment. NOT king's dash Konvict Kick, NOT jin's jump row.
- Duck-dip rows (Job 1, 6): 157, 158, 166, 178, 179, 351 — STANCE-SOFT
  (review) for non-crouch contexts. No Batch 2 step cites a duck-dip row.

### Skull's own basics (file evidence)

- LP1 move 1 → row 172 (standing LP1) and RP2 move 2 → row 100 (standing
  RP2) — both unchanged on main (damage-only drift 11→9, 12→13), NOT
  suspending (Batch 1, not Batch 2 scope).
- LK3 move 3 → row 63 on #1096 (a JUMP row, hit_frames [9,9,52,535,0,4],
  Job 1 jump) and ROW-CHANGED 63→None on main — Batch 2's problem, and it
  fires here: the two Batch 2 strings starting with plain 3 (3,3 and
  3,3,4) have their step-1 SUSPENDED (stale row 63 documented, never
  wired). Suspension comes first, before any stance question — stale row
  63 is a jump row, so it would fail ground-context gates regardless.
- RK4 move 4 → row 104 both files (standing RK4, [12,12,50,1042,0,8]) —
  verified in three Batch 2 strings (4,3 / 4,3,4 / 4,3,f+4 step 1).

### Gap-1 (Batch 1 method, replicated)

Bryan hit_frames blob 7ffea6b998d6…, rows.pack blob 1e22a8832b2c…,
skeleton blob 32d521db0921… are IDENTICAL on the Batch 1 branch and
current main — ZERO bank drift (same blobs as Batch 1's gap-1, re-verified
here). No phantom-Batch-4-style re-bake signature change. No fill is
suspended on bank drift. Every wired row is verified present in the
CURRENT main bryan rows.pack (160 rows) at wire time.

## Baseline

Base moves = Batch 1 branch file (verified: its moves dict and strings
list are deep-equal to the #1096 file's — Batch 1 added plans only, so
the drift census below is identical to Batch 1's). Re-baselined against
current main (main head at fetch: 956d6a1d0b7564a4fc69fe8b64b7f754a671a365;
main moves 634 + quarantine 54 = 688).

Full-file drift census (688 keys, both ways — both figures true under
their definitions, never silently pick one): 336 same / 237 damage-only /
112 anim_ref-changed / 3 ROW-CHANGED (3, 3_c36, u+1,3 — all 63→None).
Damage differs on 307 moves; damage-only (damage differs AND row +
anim_ref same) is 237. Damage-only drift does NOT suspend (damage ≠
animation); row-changed moves SUSPEND their steps.

## Universe (measured first, never assumed)

12 canonicals: 10 pure single-button + 2 chord-involved. 12 planned
(strike) + 0 CSV-only. 29 CSV rows → 29 plan keys (12 canonicals + 17
twins). Contexts: standing 9, ws 2, crouch 1. Provenance: 12 in main
moves, 0 quarantined-only, 0 #1096-only.

Canonicals and twins (twins inherit canonical steps verbatim):

- 3,3 — twins: 3,3~t7.bryan, 3,3~t7.bryan.2
- 3,3,4 — twins: 3,3,4~t7.bryan, 3,3,4~t7.bryan.2, 3,3,4~t7.bryan.3
- 4,3 — twins: 4,3~t7.bryan, 4,3~t7.bryan.2
- 4,3,4 — twins: 4,3,4*, 4,3,4*~t7.bryan, 4,3,4~t7.bryan, 4,3,4~t7.bryan.2,
  4,3,4~t7.bryan.3
- 4,3,f+4 — twins: 4,3,f+4~t7.bryan, 4,3,f+4~t7.bryan.2, 4,3,f+4~t7.bryan.3
- WS.3,4 — no twins (moves-dict only)
- b+3+4,4 (chord) — no twins
- b+3,4 — twins: b+3,4~t7.bryan, b+3,4~t7.bryan.2
- d/f+3+4,3 (chord, crouch) — no twins
- f+4,3 — no twins
- f+4,3,4 — no twins
- ws3,4 — no twins (moves-dict + strings-list)

Canonicalization (CORRECTED rule, mandatory): strip ONLY a trailing
~t[378].[a-z]+(.\d+)?$ suffix; a ~ INSIDE the input is part of the move.
Batch 2 scope check: 0 input-~ canonicals, 0 keys where old canonical ≠
corrected canonical, 0 __main canonicals, 0 corrupted keys. (Batch 1
established skull INERT file-wide: all 372 comma keys checked, 181 carry
~, 0 non-trailing ~; Batch 2 re-checked its own scope and found the same
0 — never copied without checking.) Spelling quirks kept distinct:
WS.3,4 vs ws3,4 are distinct canonicals (both unmapped-all); the
kinpo-Batch-1 WS-context fix applies (lowercase no-dot while-standing
spellings are WS context, not standing) and changes no wiring.

## Steps: 28 = 28 planned + 0 CSV-only

Planned steps: 8 verified / 2 review / 18 unmapped.
Unmapped split: 16 no-candidate / 0 rejected-candidate / 2 suspended-drift.
Canonical status: 7 partial / 5 unmapped-all / 0 verified-all.
Plan-key last-step: 2 verified / 2 review / 25 unmapped.

## Wired fills (all VERIFIED, gate-verified own/recorded-path rows, T3 FALLBACK)

T3 rows here are FALLBACK (see docs/anim/PROCEDURAL_AUDIT.md Skull-Batch-2
entry), never recorded as the correct mapping, to be re-matched to T7
Bryan rows when decode lands. Verified = hit_frames button == step bits
+ throw flag 0 + stance gate + SOFT limb-peak proxy pass.

- 4,3 step 1 → row 104: standing RK4, hf [12,12,50,1042,0,8], Job 1
  standing, legR, level h, active [12,12]. (Also 4,3,4 step 1 and 4,3,f+4
  step 1 — same own RK4 row, each step gate-checked again per the row
  dual-role caution.)
- b+3+4,4 step 1 → row 199: standing LK3+RK4 chord, hf [16,16,53,1042,0,12],
  Job 1 standing, level h, active [16,16].
- d/f+3+4,3 step 1 → row 103: standing LK3+RK4 chord, hf [16,16,50,535,0,12],
  Job 1 standing, level m, active [16,16]. GATE-NOTE: standing row
  verified for a crouch-context step (demonio Batch 1 precedent — the
  gate flags crouch rows for non-crouch steps, not standing rows for
  crouch steps; re-adjudicate if the gate is ever tightened).
- f+4,3 step 2 → row 193: standing LK3, hf [24,24,60,535,0,4], Job 1
  standing, legL, level m, active [24,24]. (Also f+4,3,4 step 2.)
- f+4,3,4 step 3 → row 194: standing RK4, hf [24,24,64,1042,0,8], Job 1
  standing, legR, level h, active [24,24].

No step plays a bryan airborne/jump row for a ground step; no step plays
a row from another bank; no step plays row 220, 216 (button-0 rows) or
row 35 (does not exist in this bank).

## Suspended-drift (2)

- 3,3 step 1 and 3,3,4 step 1: prefix move 3 ROW-CHANGED 63→None on main.
  Stale candidate row 63 (prefix-move, jump row [9,9,52,535,0,4])
  documented, never wired. Later steps of those strings are NOT suspended
  (their prefixes are not row-changed moves) — they are unmapped for
  lack of a candidate, not for drift.

## Review steps (2)

- b+3+4,4 step 2, candidate row 200 (own row, standing RK4,
  hf [11,11,61,535,0,8], level m): SOFT limb-peak proxy fail — window
  [3.5,7.5], legR peak 26 (outside the window). Row null in plan, never
  wired. Job 4 join confirms row 200 passes HARD gates, but a join never
  promotes a candidate by itself.
- d/f+3+4,3 step 2, candidate row 192 (own row, standing LK3,
  hf [23,23,60,1042,0,4], level h): SOFT limb-peak proxy fail — window
  [9.5,13.5], legL peak 0. Row null in plan, never wired.

## Rejected-candidate (0)

No unmapped Batch 2 step has a HARD-gate-failed candidate. (The two
review steps above fail only the SOFT proxy, and the two suspended steps
are drift suspensions, not gate rejections.)

## No-candidate (16)

Intermediate prefixes are T8-sourced strings with no T3 row; correct
clips come from #988 Step 2 (original T8 refs) or future extraction —
never from a T3 row recorded as correct:

3,3 step 2; 3,3,4 steps 2–3; 4,3 step 2; 4,3,4 steps 2–3; 4,3,f+4 steps
2–3; WS.3,4 steps 1–2; b+3,4 steps 1–2; f+4,3 step 1; f+4,3,4 step 1;
ws3,4 steps 1–2.

## Job 3 (0 report entries with a pass-all candidate, 0 fills wired)

Job 3 log lines exist for 8 Batch 2 step prefixes (3, 3,3, 4,3, WS.3,
b+3, d/f+3+4, d/f+3+4,3, ws3 — eight lines, each with an EMPTY pass-all
list). Match_search top10 rows for those prefixes all fail at least one
gate or lack full provenance (travel_ok False, stance_ok False, or
provenance empty / from another string), so there is nothing to wire and
nothing to document as a candidate under the stricter fill rule (exact
level + full provenance + HARD gates + SOFT proxy). The fill rule is the
burger refinement: a Job 3 fill additionally requires the SOFT proxy to
pass. Job 3 prefix-vs-__main dedupe fires 0 times (no __main canonicals
in scope). The Job 3 agreement-note wording (demonio Batch 4 fix) is
moot here: no agreement note is claimed, because no gate candidate was
wired from Job 3.

## Job 4 (corrected join only: 1 join, 0 promotions, 0 orphans)

- b+3+4,4 step 2: row 200 joined (Job 2 skull entry key == step prefix
  'b+3+4,4', row == 200, step == own; Job 4 note peaks armL 2 / armR 1 /
  legL 1 / legR 0) — CANDIDATE passing HARD gates, NOT wired (a join
  never promotes by itself; the step stays review on its SOFT fail).
- Orphans: none. The naive cross-fighter join was not used.

## Donor rows documented, never wired

Single-row resolution is retired by design when a plan is wired: wiring
plans replaces single-row resolution wholesale, even for CLEAN donors,
because one row cannot be correct for a multi-hit string. Donor rows
that appear in the CSV (e.g. row 63 for 3,3 variants, row 110 for
4,3,f+4 variants, row 104 for 4,3,4 / WS.3,4 / b+3,4 / ws3,4 last steps)
are audit evidence only — the plans play NO donor row for any step
whose status is not verified.

## Tests

Minimal-tree node --test: 21/21 pass (13 Batch 1 tests preserved verbatim
in content + 8 Batch 2 tests). node --check fighter.js OK (fighter.js
unchanged by this PR). Formatting reproduces the Batch 1 branch file
byte-identically except the surgical diff: json.dumps(indent=2,
ensure_ascii=False) + "\n". Structural diff: all non-plan top-level keys
identical to the Batch 1 branch file; all 91 Batch 1 plans deep-equal;
plan count 91 → 120 (29 Batch 2 keys added, 0 collisions, 0 CSV-only
keys). Full 200-test suite comparison NOT run — no full current-main
checkout on this box; stated as a limitation in the PR body, CI must
cover it before merge.

## Play-verify checklist (parent browser delegation, after #1129 + this PR merge + deploy + sync, phone portrait)

Each wired skull Batch 2 string played: feet grounded where the step is
grounded, no step playing a jumping row for a ground step, no step
playing a row from another bank.

- 4,3 [104, NO row]; 4,3,4 [104, NO row, NO row]; 4,3,f+4 [104, NO row,
  NO row] — step 1 grounded standing RK4 row 104; later steps NO row.
- b+3+4,4 [199, NO row] — step 1 grounded standing chord row 199; step 2
  NO row (review row 200 held, must NOT play).
- d/f+3+4,3 [103, NO row] — step 1 crouch-context chord row 103
  (GATE-NOTE: standing row for a crouch step); step 2 NO row (review
  row 192 held, must NOT play).
- f+4,3 [NO row, 193]; f+4,3,4 [NO row, 193, 194] — step 1 NO row; later
  steps grounded standing rows 193/194.
- Unmapped-all strings — NO row any step: 3,3 and 3,3,4 (stale row 63
  must NOT play); WS.3,4; b+3,4; ws3,4.
- No step plays a bryan airborne/jump row for a ground step; no step
  plays a row from another bank; no step plays row 220, 216 (button-0
  rows) or row 35 (does not exist in this bank).
- Skull Batch 1 spot-checks undisturbed: 2,1 [152,153], 2,1,2
  [152,153,151], f+1,2 [172,173], d/f+1+2 family [113,149] /
  [113,146] / [113,146,147] / [113,146,147,148], 1,2 step 1 row 172,
  b+1,2 step 2 row 145, b+2,f+1,2 step 3 row 151, jump step-2 rows
  44/56/46/58/45/57.
- No play verification claimed — tests + file evidence only; playing is
  the parent's step after merge + deploy.
