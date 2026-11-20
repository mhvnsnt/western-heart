# SKULL BATCH 3 — STEP PLANS (mixed-pair strings, 2026-10-25)

Stack: branch from skull Batch 2's branch `feat/skull-batch2-step-plans-20261025`
(PR #1130, head ffa15d704d86bc1f2560dd81b05ccd9b2c5a9c96, re-verified before
branching). Merges AFTER #1130 (which merges after #1129, which merges after
#1096, itself blocked on 12 pre-existing failures / a gate decision owed —
this lane fixes neither and merges nothing itself). Plans accumulate: #1096
engine → skull B1 (91 keys) → skull B2 (29 keys) → skull B3 (78 keys) = 198
keys total. This PR does not touch fighter.js, pantera.json, burger.json,
demonio.json, diablo.json, kinpo.json, phantom.json, or scimitar.json. No
T8 content touched.

## Bank — VERIFIED, not assumed (four-way file evidence, carried from Batches 1–2)

Skull's T3 bank is BRYAN — NATIVE, not a fallback. skull.json t3_source
'bryan', t3_bank 'moveset_bryan.json' on BOTH the Batch 2 branch file and
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
  (review) for non-crouch contexts. One Batch 3 step cites a duck-dip row
  as a candidate (b+2,4 step 1, row 158 — held at review, never wired).

### Skull's own basics (file evidence)

- LP1 move 1 → row 172 (standing LP1, [10,10,45,1042,0,1]) and RP2 move 2 →
  row 100 (standing RP2, [10,10,39,1042,0,2]) — both unchanged on main
  (damage-only drift 11→9, 12→13), NOT suspending. Both verified in
  Batch 3 strings (1,4 step 1 and f+1,4 step 1 ← 172; 2,3 step 1 and 2,4
  step 1 ← 100).
- LK3 move 3 → row 63 on #1096 (a JUMP row, hit_frames [9,9,52,535,0,4],
  Job 1 jump) and ROW-CHANGED 63→None on main — Batch 2's problem, and
  Batch 3's problem too: Batch 3 strings CAN contain LK3 (mixed pairs
  include LK3), so the row-change re-check was run explicitly and it
  FIRED here (see Suspended-drift). This is the check that mattered in
  Batch 3 — unlike scimitar Batch 3, where the move-1 check came back
  clean, skull Batch 3's check fires on three steps.
- RK4 move 4 → row 104 both files (standing RK4, [12,12,50,1042,0,8]) —
  verified in one Batch 3 string (4,1 step 1).

### Gap-1 (Batch 1 method, replicated)

Bryan hit_frames blob 7ffea6b998d6…, rows.pack blob 1e22a8832b2c…,
skeleton blob 32d521db0921… are IDENTICAL on the Batch 2 branch and
current main — ZERO bank drift (same blobs as Batch 1's gap-1, re-verified
here). No phantom-Batch-4-style re-bake signature change. No fill is
suspended on bank drift. Every wired row is verified present in the
CURRENT main bryan rows.pack (160 rows) at wire time.

## Baseline

Base moves = Batch 2 branch file (verified: its moves dict and strings
list are deep-equal to the #1096 file's — Batches 1–2 added plans only, so
the drift census below is identical to Batches 1–2's). Re-baselined against
current main (main head at fetch: 956d6a1d0b7564a4fc69fe8b64b7f754a671a365;
main moves 634 + quarantine 54 = 688).

Full-file drift census (688 keys, both ways — both figures true under
their definitions, never silently pick one): 336 same / 237 damage-only /
112 anim_ref-changed / 3 ROW-CHANGED (3, 3_c36, u+1,3 — all 63→None).
Damage differs on 307 moves; damage-only (damage differs AND row +
anim_ref same) is 237. Damage-only drift does NOT suspend (damage ≠
animation); row-changed moves SUSPEND their steps.

## Universe (measured first, never assumed)

31 canonicals: 30 pure single-button + 1 chord-involved (1+3,1, a
LP1+LK3 chord). 31 planned (strike) + 0 CSV-only. 78 CSV rows → 78 plan
keys (31 canonicals + 47 twins). Pair split: {LP1,RK4} 11, {RP2,LK3} 11,
{RP2,RK4} 5, {LP1,LK3} 4. Contexts: standing 19, jump 8, crouch 4.
Provenance: 24 in main moves, 7 quarantined-only (4,1; SLS.2,4; SLS.4,1;
SLS.4,1,4; SWA.2,4; uf+2,2,2,3; uf+2,2,2,SNE.2,2,3 — live when #988
merges), 0 Batch 2-branch-only.

Canonicals and twins (twins inherit canonical steps verbatim):

- 1+3,1 (chord) — twins: 1+3,1~t3.bryan, 1+3,1~t3.bryan.2,
  1+3,1~t3.bryan.3, 1+3,1~t3.bryan.4
- 1,4 — twins: 1,4~t7.bryan, 1,4~t7.bryan.2
- 2,3 — twins: 2,3~t7.bryan, 2,3~t7.bryan.2
- 2,4 — no twins
- 3,2 — twins: 3,2~t7.bryan, 3,2~t7.bryan.2
- 3,3,2 — twins: 3,3,2~t7.bryan, 3,3,2~t7.bryan.2, 3,3,2~t7.bryan.3
- 4,1 (quarantined-only) — no twins
- SLS.2,4 (quarantined-only) — no twins
- SLS.4,1 (quarantined-only) — no twins
- SLS.4,1,4 (quarantined-only) — no twins
- SS.2,3 — twin: SS.2,3~t7.bryan
- SWA.2,4 (quarantined-only) — no twins
- b+2,4 — twins: b+2,4~t7.bryan, b+2,4~t7.bryan.2
- b+3,2 — twins: b+3,2~t7.bryan, b+3,2~t7.bryan.2
- d+2,3 — twins: d+2,3~t7.bryan, d+2,3~t7.bryan.2
- d+3,2 — twins: d+3,2~t7.bryan, d+3,2~t7.bryan.2
- d/f+2,3 — twin: d/f+2,3~t7.bryan
- df+2,3 — no twins
- f+1,4 — no twins
- f+4,1 — twins: f+4,1~t7.bryan, f+4,1~t7.bryan.2
- qcb+2,4 — twin: qcb+2,4~t7.bryan
- qcf+4,1 — twin: qcf+4,1~t7.bryan
- qcf+4,1,4 — twins: qcf+4,1,4~t7.bryan, qcf+4,1,4~t7.bryan.2
- u+1,3 — twins: u+1,3~t3.bryan, u+1,3~t3.bryan.2, u+1,3~t3.bryan.3
- u+1,4 — twins: u+1,4~t3.bryan, u+1,4~t3.bryan.2, u+1,4~t3.bryan.3
- u/b+1,3 — twins: u/b+1,3~t3.bryan, u/b+1,3~t3.bryan.2,
  u/b+1,3~t3.bryan.3
- u/b+1,4 — twins: u/b+1,4~t3.bryan, u/b+1,4~t3.bryan.2,
  u/b+1,4~t3.bryan.3
- u/f+1,3 — twins: u/f+1,3~t3.bryan, u/f+1,3~t3.bryan.2,
  u/f+1,3~t3.bryan.3
- u/f+1,4 — twins: u/f+1,4~t3.bryan, u/f+1,4~t3.bryan.2,
  u/f+1,4~t3.bryan.3
- uf+2,2,2,3 (quarantined-only) — no twins
- uf+2,2,2,SNE.2,2,3 (quarantined-only) — no twins

Canonicalization (CORRECTED rule, mandatory): strip ONLY a trailing
~t[378].[a-z]+(.\d+)?$ suffix; a ~ INSIDE the input is part of the move.
Batch 3 scope checked, not copied: 0 input-~ canonicals, 0 corrupted
keys, 0 __main canonicals in Batch 3 scope. Spelling quirks kept
distinct: d/f+2,3 (verified step 1 row 149) vs df+2,3 (unmapped-all,
different step-1 evidence); WS-context fix applied (no wiring change —
Batch 3 has no ws-context canonicals).

## Steps: 71 = 71 planned + 0 CSV-only

Planned steps: 12 verified / 2 review / 57 unmapped.
Unmapped split: 48 no-candidate / 6 rejected-candidate / 3 suspended-drift.
Canonical status: 1 verified-all / 11 partial / 19 unmapped-all /
0 review-only.
Plan-key last-step: 21 verified / 1 review / 56 unmapped.

## Wired fills (all VERIFIED, gate-verified own/recorded-path rows, T3 FALLBACK)

T3 rows here are FALLBACK (see docs/anim/PROCEDURAL_AUDIT.md Skull-Batch-3
entry), never recorded as the correct mapping, to be re-matched to T7
Bryan rows when decode lands. Verified = hit_frames button == step bits
+ throw flag 0 + stance gate + SOFT limb-peak proxy pass (waived for
jump-context steps, Batch 1 precedent).

- 1,4 step 1 → row 172: standing LP1, hf [10,10,45,1042,0,1], Job 1
  standing, armL, level h, active [10,10]. (Also f+1,4 step 1 — same own
  LP1 row, each step gate-checked again per the row dual-role caution.)
- 2,3 step 1 → row 100: standing RP2, hf [10,10,39,1042,0,2], Job 1
  standing, armR, level h, active [10,10]. (Also 2,4 step 1.)
- 4,1 step 1 → row 104: standing RK4, hf [12,12,50,1042,0,8], Job 1
  standing, legR, level h, active [12,12]. (Quarantined-only — live when
  #988 merges.)
- d/f+2,3 step 1 → row 149: standing RP2, hf [23,23,61,535,0,2], Job 1
  standing, armR, level m, active [23,23]. GATE-NOTE: standing row
  verified for a crouch-context step (demonio Batch 1 precedent — the
  gate flags crouch rows for non-crouch steps, not standing rows for
  crouch steps; re-adjudicate if the gate is ever tightened). Same
  row/result as Batch 1's d/f+2,1 step 1 hold, independently re-derived
  in this context.
- f+1,4 step 2 → row 187: standing RK4, hf [15,15,53,1042,0,8], Job 1
  standing, legR, level h, active [15,15]. (With step 1 row 172, f+1,4 is
  Batch 3's only verified-all string.)
- u+1,4 step 2 → row 76: starts-airborne RK4, hf [8,9,46,535,0,8], Job 1
  starts-airborne, legR, level m. SOFT waived (jump context).
- u/b+1,3 step 2 → row 65: jump LK3, hf [9,9,52,535,0,4], Job 1 jump,
  legL, level m. SOFT waived (jump context).
- u/b+1,4 step 2 → row 78: starts-airborne RK4, hf [8,9,46,535,0,8],
  Job 1 starts-airborne, legR, level m. SOFT waived (jump context).
- u/f+1,3 step 2 → row 64: jump LK3, hf [9,9,52,535,0,4], Job 1 jump,
  legL, level m. SOFT waived (jump context).
- u/f+1,4 step 2 → row 77: starts-airborne RK4, hf [8,9,46,535,0,8],
  Job 1 starts-airborne, legR, level m. SOFT waived (jump context).

No step plays a bryan airborne/jump row for a ground step; no step plays
a row from another bank; no step plays row 220, 216 (button-0 rows) or
row 35 (does not exist in this bank).

## Suspended-drift (3)

- 3,2 step 1 and 3,3,2 step 1: prefix move 3 ROW-CHANGED 63→None on main.
  Stale candidate row 63 (prefix-move, jump row [9,9,52,535,0,4])
  documented, never wired. Later steps of those strings are NOT suspended
  (their prefixes are not row-changed moves) — they are unmapped for
  lack of a candidate, not for drift.
- u+1,3 step 2: prefix move u+1,3 itself is ROW-CHANGED 63→None on main
  (the file's third row-changed move). Stale candidate row 63 documented,
  never wired. Step 1 (prefix u+1) is unmapped for lack of a candidate,
  not for drift — the suspension attaches to the step whose prefix is
  row-changed, nothing else.

## Review steps (2)

- 2,4 step 2, candidate row 182 (own row, recorded-dest, standing RK4,
  hf [24,24,61,1042,0,8], level m): SOFT limb-peak proxy fail — window
  [9.0,14.0], legR peak 2 (outside the window). Row null in plan, never
  wired. Job 4 join confirms row 182 passes HARD gates, but a join never
  promotes a candidate by itself.
- b+2,4 step 1, candidate row 158 (own row, duck-dip RK4, level m):
  STANCE-SOFT duck-dip row for a standing-context step. Row null in
  plan, never wired. Job 4 join confirms row 158 passes HARD gates, but
  a join never promotes — same row/result as Batch 1's b+2 holds,
  independently re-derived.

## Rejected-candidate (6)

- 1+3,1 step 1, candidate row 137 (prefix-move): throw flag 1 (row is a
  throw row) for a strike step.
- 1+3,1 step 2, candidate row 351 (prefix-move): button 0 ≠ step bits 1
  AND throw flag 1.
- u/b+1,3 step 1 and u/b+1,4 step 1, candidate row 43 (prefix-move):
  button 3 ≠ step bits 1 — same row/result as Batch 1's u/b+1
  rejections, independently re-derived.
- u/f+1,3 step 1 and u/f+1,4 step 1, candidate row 42 (prefix-move):
  button 3 ≠ step bits 1 — same row/result as Batch 1's u/f+1
  rejections, independently re-derived.

## No-candidate (48)

1,4 step 2; 2,3 step 2; 3,2 step 2; 3,3,2 steps 2–3; 4,1 step 2; SLS.2,4
steps 1–2; SLS.4,1 steps 1–2; SLS.4,1,4 steps 1–3; SS.2,3 steps 1–2;
SWA.2,4 steps 1–2; b+2,4 step 2; b+3,2 steps 1–2; d+2,3 steps 1–2;
d+3,2 steps 1–2; d/f+2,3 step 2; df+2,3 steps 1–2; f+4,1 steps 1–2;
qcb+2,4 steps 1–2; qcf+4,1 steps 1–2; qcf+4,1,4 steps 1–3; u+1,3 step 1;
u+1,4 step 1; uf+2,2,2,3 steps 1–4; uf+2,2,2,SNE.2,2,3 steps 1–6.
Intermediate prefixes are T8-sourced strings with no T3 row — correct
clips come from #988 Step 2 (original T8 refs) or future extraction,
never from a T3 row recorded as correct. Donor rows documented in the
CSV (e.g. donor row 104 for 1,4's whole-string pick, donor row 100 for
3,2, donor row 172 for 4,1, donor row 63 jump row for 2,3 and d/f+2,3)
are never wired as step rows.

## Job 3 (6 report entries, 0 fills wired)

All candidates ROW-ONLY or soft, documented never wired: prefix 1 rows
99 (exact ROW-ONLY) / 132 / 146 / 147 / 148 (soft-filed ROW-ONLY) for
1,4 step 1 (already verified — no agreement note fires because no
exact+FULL candidate exists for any verified step); prefix 2 rows 101 /
105 / 106 (exact ROW-ONLY) / 126 (unknown, not in top10) for 2,3 step 1
and 2,4 step 1 (both already verified); prefix d+2 rows 114 (soft-filed
ROW-ONLY) / 167 (exact ROW-ONLY) for d+2,3 step 1; prefix d+3 row 167
(soft-filed ROW-ONLY) for d+3,2 step 2; prefix d/f+2 rows 114
(soft-filed ROW-ONLY) / 167 (exact ROW-ONLY) for d/f+2,3 step 1 (already
verified). No exact+FULL candidate exists for any step, so the
agreement note (demonio Batch 4 wording: fires ONLY for actually-wired
gate candidates) does not fire anywhere. Dedupe fires 0 times: no Batch
3 step prefix has a __main Job 3 target at all. No SOFT fill inherited
from #1097.

## Job 4 (corrected join only: 3 joins, 0 promotions, 0 orphans)

- Row 351 joined for 1+3,1 step 2 — REJECTED (button 0 ≠ bits 1, throw
  flag 1).
- Row 182 joined for 2,4 step 2 — CANDIDATE (passes HARD gates, NOT
  wired — a join never promotes by itself; step stays review on the
  SOFT fail).
- Row 158 joined for b+2,4 step 1 — CANDIDATE (passes HARD gates, NOT
  wired — a join never promotes by itself; step stays review on the
  STANCE-SOFT duck-dip hold).
Naive cross-fighter join not used. Orphans: 0 — every bryan Job 4
candidate is carried by a skull Job 2 move.

## Donor rows documented, never wired

Job 2 whole-string picks for Batch 3 strings (CSV): 104 (1,4, b+2,4),
63 jump row (2,3, d/f+2,3), 100 (3,2), 172 (4,1), 182 own (2,4 — held at
review, not wired as verified), 187 own (f+1,4 — wired as step 2 only,
not as a whole-string clip), 351/343/347/349 (1+3,1 family throw rows).
Wiring plans replaces single-row resolution wholesale, even for CLEAN
donors — one row cannot be correct for a multi-hit string.

## Tests

Minimal-tree node --test game/tests/skull-batch3-step-plans.test.mjs:
33/33 pass (13 Batch 1 tests + 8 Batch 2 tests + 12 Batch 3 tests,
Batch 1–2 content assertions preserved verbatim). node --check
fighter.js OK (fighter.js unchanged). Formatter round-trips the Batch 2
branch file byte-identically; all non-plan keys identical; all 120
Batches 1–2 plans deep-equal; plan count 120 → 198 (78 Batch 3 keys,
0 collisions). LIMITATION (stated in the PR body): full 200-test suite
comparison NOT run — no full current-main checkout on this box; CI must
cover it before merge. No play verification claimed — tests + file
evidence only; playing is the parent's step after merge + deploy.

## Play-verify checklist (parent browser delegation, after #1129 + #1130 + this PR merge + deploy + sync, phone portrait)

- f+1,4 [172,187] — verified-all, both steps grounded, no jumping row.
- 1,4 [172,NO row]; 2,3 [100,NO row]; 2,4 [100,review-NO row] (review row
  182 held, must NOT play); 4,1 [104,NO row] (quarantined-only — per plan
  ONLY after #988 merges).
- d/f+2,3 [149 GATE-NOTE,NO row] — step 1 grounded standing RP2 row for
  a crouch step (verify it reads as a crouch-context strike); step 2 NO
  row.
- 3,2 / 3,3,2 — step 1 NO row (stale row 63 must NOT play); later steps
  NO row.
- u+1,3 — step 1 NO row; step 2 NO row (stale row 63 must NOT play).
- u+1,4 [NO row,76]; u/b+1,3 [NO row,65]; u/b+1,4 [NO row,78];
  u/f+1,3 [NO row,64]; u/f+1,4 [NO row,77] — jump lasts only; step 1 NO
  row (rejected rows 42/43 must NOT play).
- b+2,4 [review-NO row,NO row] — review row 158 held, must NOT play.
- 1+3,1 — NO row any step (throw rows 137/351 must NOT play).
- All other Batch 3 canonicals — NO row any step (donor rows 63/100/
  104/172 must NOT appear as whole-string clips).
- No step plays a bryan airborne/jump row for a ground step; no step
  plays a row from another bank; no step plays row 220, 216, or 35.
- Batches 1–2 spot-checks undisturbed: 2,1 [152,153]; 2,1,2 [152,153,151];
  f+1,2 [172,173]; d/f+1+2 family [113,149]/[113,146]/[113,146,147]/
  [113,146,147,148]; 1,2 [172,NO row]; b+1,2 [NO row,145]; b+2,f+1,2 step 3
  row 151; jump step-2 rows 44/56/46/58/45/57; 4,3 [104,NO row];
  b+3+4,4 [199,NO row]; d/f+3+4,3 [103 GATE-NOTE,NO row]; f+4,3
  [NO row,193]; f+4,3,4 [NO row,193,194]; 3,3/3,3,4 NO row (stale 63).
- Quarantined-only Batch 3 strings behave per plan ONLY after #988
  merges (4,1; SLS.2,4; SLS.4,1; SLS.4,1,4; SWA.2,4; uf+2,2,2,3;
  uf+2,2,2,SNE.2,2,3).
