# SKULL BATCH 4 — STEP PLANS (triples/quads/rest strings, 2026-10-25)

Stack: branch from skull Batch 3's branch `feat/skull-batch3-step-plans-20261025`
(PR #1131, head 32ade7bebb3bd846cec23ce3dafaef516762a857, re-verified before
branching). Merges AFTER #1131 (which merges after #1130, which merges after
#1129, which merges after #1096, itself blocked on 12 pre-existing failures /
a gate decision owed — this lane fixes neither and merges nothing itself).
Plans accumulate: #1096 engine → skull B1 (91 keys) → skull B2 (29 keys) →
skull B3 (78 keys) → skull B4 (130 keys) = 328 keys total. This PR does not
touch fighter.js, pantera.json, burger.json, demonio.json, diablo.json,
kinpo.json, phantom.json, or scimitar.json. No T8 content touched.

## Bank — VERIFIED, not assumed (four-way file evidence, carried from Batches 1–3)

Skull's T3 bank is BRYAN — NATIVE, not a fallback. skull.json t3_source
'bryan', t3_bank 'moveset_bryan.json' on BOTH the Batch 3 branch file and
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
  (review) for non-crouch contexts. One Batch 4 step cites a duck-dip row
  as a candidate (b+2,1,4 step 1, row 158 — held at review, never wired).

### Skull's own basics (file evidence)

- LP1 move 1 → row 172 (standing LP1, [10,10,45,1042,0,1]) and RP2 move 2 →
  row 100 (standing RP2, [10,10,39,1042,0,2]) — both unchanged on main
  (damage-only drift 11→9, 12→13), NOT suspending. Row 172 verified in
  Batch 4 strings (1,4,2 family step 1s; f+1,4,2 / f+1,4,3 step 1s).
- LK3 move 3 → row 63 on #1096 (a JUMP row, hit_frames [9,9,52,535,0,4],
  Job 1 jump) and ROW-CHANGED 63→None on main — Batch 2's problem, Batch
  3's problem, and Batch 4's problem too: Batch 4 strings CAN start with
  3, so the row-change re-check was run explicitly and it FIRED here
  (see Suspended-drift). This is the check that mattered in Batch 4 —
  like Batches 2–3, unlike scimitar Batch 3, where the move-1 check came
  back clean.
- RK4 move 4 → row 104 both files (standing RK4, [12,12,50,1042,0,8]).

### Gap-1 (Batch 1 method, replicated)

Bryan hit_frames blob 7ffea6b998d6…, rows.pack blob 1e22a8832b2c…,
skeleton blob 32d521db0921… are IDENTICAL on the Batch 3 branch and
current main — ZERO bank drift (same blobs as burger Batch 1's gap-1,
independently re-verified here). No phantom-Batch-4-style re-bake
signature change. Gates use hit_frames (identical) + Job 1 profiles, and
every wired row is verified present in the CURRENT main pack at wire
time (the game plays from the pack).

## Baseline

Batch 3 branch moves dict and strings list are deep-equal to the #1096
file's, so the drift census is identical to Batches 1–3's. Main moves
(634) + main quarantine (54) = #1096 moves (688) exactly; 0 main-only
moves. Drift census (688 keys, both ways): 336 same / 237 damage-only /
112 anim_ref-changed / 3 ROW-CHANGED (3, 3_c36, u+1,3 — all 63→None).
Damage differs on 307 (damage-only count is 237 — both figures true
under their definitions; never silently pick one). Damage-only drift
does NOT suspend (damage is not animation); row-changed moves SUSPEND
their steps.

## Universe (measured first, never assumed)

88 canonicals: 33 pure single-button + 55 chord-involved. 55 planned
triples/quads (strike) + 33 CSV-only rest keys + 0 throw/grapple
triples/quads (none exist under the narrow label rule — only
{PILE_DRIVER, ARM_BREAKER, TACKLE} count as grapple labels, and no
Batch 4 triple/quad carries one). 171 CSV rows → 130 plan keys (55
planned canonicals + 75 twins). Contexts: standing 73, crouch 12, jump
3. Provenance: 72 in main moves, 16 quarantined-only (12 planned +
4 rest — live when #988 merges), 0 Batch 3-branch-only.

COVERAGE-COMPLETE PROOF: full inventory 188 canonical comma keys =
B1 57 + B2 12 + B3 31 + B4 88, pairwise overlaps 0 (EXCLUDED filter),
uncovered [] extra [] — verified independently against the moves dict
+ strings list, canonicalized with the corrected rule. Leftover
all-buttoned union-<=2 canonicals (a Batches 1–3 miss) = []. Plan keys
total 328 = 91 + 29 + 78 + 130. CSV-only canonicals total 36 = B1 3
(TACKLE.1,1 family) + B4 33 rest. Skull is the EIGHTH and LAST fighter
coverage-complete (after Pantera 240, burger 159, demonio 271, diablo
201, kinpo 135, phantom 321, scimitar 74).

Canonicals and twins (twins inherit canonical steps verbatim):

- (Back to wall).b,b,UB (chord-involved, standing, quarantined-only, rest CSV-only) — twins: none
- 1,2,3 (pure, standing, main, planned triple/quad) — twins: 1,2,3~t7.bryan, 1,2,3~t7.bryan.2, 1,2,3~t7.bryan.3
- 1,2,4 (pure, standing, main, planned triple/quad) — twins: 1,2,4~t7.bryan, 1,2,4~t7.bryan.2, 1,2,4~t7.bryan.3
- 1,4,2 (pure, standing, main, planned triple/quad) — twins: 1,4,2~t7.bryan, 1,4,2~t7.bryan.2, 1,4,2~t7.bryan.3
- 1,4,2,1 (pure, standing, main, planned triple/quad) — twins: 1,4,2,1~t7.bryan, 1,4,2,1~t7.bryan.2, 1,4,2,1~t7.bryan.3, 1,4,2,1~t7.bryan.4
- 1,4,2,1,2 (pure, standing, main, planned triple/quad) — twins: 1,4,2,1,2~t7.bryan, 1,4,2,1,2~t7.bryan.2, 1,4,2,1,2~t7.bryan.3, 1,4,2,1,2~t7.bryan.4, 1,4,2,1,2~t7.bryan.5
- 1,4,2,1,4 (pure, standing, main, planned triple/quad) — twins: 1,4,2,1,4~t7.bryan, 1,4,2,1,4~t7.bryan.2, 1,4,2,1,4~t7.bryan.3, 1,4,2,1,4~t7.bryan.4, 1,4,2,1,4~t7.bryan.5
- 1,4,2,1,u,u (chord-involved, standing, main, rest CSV-only) — twins: none
- 1,4,2,4 (pure, standing, main, planned triple/quad) — twins: 1,4,2,4~t7.bryan, 1,4,2,4~t7.bryan.2, 1,4,2,4~t7.bryan.3, 1,4,2,4~t7.bryan.4
- 1,4,2,f+1 (pure, standing, main, planned triple/quad) — twins: none
- 1,4,3 (pure, standing, main, planned triple/quad) — twins: 1,4,3~t7.bryan, 1,4,3~t7.bryan.2, 1,4,3~t7.bryan.3
- 1,4,3,3 (pure, standing, main, planned triple/quad) — twins: 1,4,3,3~t7.bryan, 1,4,3,3~t7.bryan.2, 1,4,3,3~t7.bryan.3, 1,4,3,3~t7.bryan.4
- 2+4,1 (chord-involved, standing, main, planned triple/quad) — twins: 2+4,1~t3.bryan
- 3+4,SNE.2 (chord-involved, standing, quarantined-only, planned triple/quad) — twins: 3+4,SNE.2*
- 3,2,1 (pure, standing, main, planned triple/quad) — twins: 3,2,1~t7.bryan, 3,2,1~t7.bryan.2, 3,2,1~t7.bryan.3
- 3,2,1,2 (pure, standing, main, planned triple/quad) — twins: 3,2,1,2~t7.bryan, 3,2,1,2~t7.bryan.2, 3,2,1,2~t7.bryan.3, 3,2,1,2~t7.bryan.4
- 3,2,1,4 (pure, standing, main, planned triple/quad) — twins: 3,2,1,4~t7.bryan, 3,2,1,4~t7.bryan.2, 3,2,1,4~t7.bryan.3, 3,2,1,4~t7.bryan.4
- FC.d/f,d,d/f+1+2 (chord-involved, crouch, main, rest CSV-only) — twins: none
- SLS.4,1,2 (pure, standing, quarantined-only, planned triple/quad) — twins: none
- SNE.f,F+1+2 (chord-involved, standing, main, rest CSV-only) — twins: none
- SNE.f,F+1+2,P (chord-involved, standing, quarantined-only, rest CSV-only) — twins: none
- WALL.b,b,u/b (chord-involved, standing, main, rest CSV-only) — twins: none
- b+1+3,P.2 (chord-involved, standing, quarantined-only, planned triple/quad) — twins: none
- b+2,1,4 (pure, standing, main, planned triple/quad) — twins: b+2,1,4~t7.bryan, b+2,1,4~t7.bryan.2, b+2,1,4~t7.bryan.3
- b+2,1,u,u (chord-involved, standing, main, rest CSV-only) — twins: none
- b+3+4,2 (chord-involved, standing, main, planned triple/quad) — twins: none
- b+3+4,2,1 (chord-involved, standing, main, planned triple/quad) — twins: none
- b+3+4,4,1 (chord-involved, standing, main, planned triple/quad) — twins: none
- b+3+4,4,1,2 (chord-involved, standing, main, planned triple/quad) — twins: none
- b+3+4,4,1,2,1 (chord-involved, standing, main, planned triple/quad) — twins: none
- b+3+4,4,1,2,1,4 (chord-involved, standing, main, planned triple/quad) — twins: none
- b+3+4,4,1,2,1,4,2 (chord-involved, standing, main, planned triple/quad) — twins: none
- b+3+4,4,1,2,1,4,2,1 (chord-involved, standing, main, planned triple/quad) — twins: none
- b+3+4,4,1,2,1,4,2,1,4 (chord-involved, standing, main, planned triple/quad) — twins: none
- b+3+4,4,1,2,1,4,2,1,4,2 (chord-involved, standing, main, planned triple/quad) — twins: none
- b+3,1+2 (chord-involved, standing, main, planned triple/quad) — twins: b+3,1+2~t7.bryan, b+3,1+2~t7.bryan.2
- b+3,1+2,D (chord-involved, standing, main, rest CSV-only) — twins: none
- b+3,2,1 (pure, standing, main, planned triple/quad) — twins: b+3,2,1~t7.bryan, b+3,2,1~t7.bryan.2, b+3,2,1~t7.bryan.3
- b+3,2,1,2 (pure, standing, main, planned triple/quad) — twins: b+3,2,1,2~t7.bryan, b+3,2,1,2~t7.bryan.2, b+3,2,1,2~t7.bryan.3, b+3,2,1,2~t7.bryan.4
- b+3,2,1,4 (pure, standing, main, planned triple/quad) — twins: b+3,2,1,4~t7.bryan, b+3,2,1,4~t7.bryan.2, b+3,2,1,4~t7.bryan.3, b+3,2,1,4~t7.bryan.4
- b+3,4,1 (pure, standing, quarantined-only, planned triple/quad) — twins: none
- b+3,4,1,2 (pure, standing, quarantined-only, planned triple/quad) — twins: none
- b+3,4,1,2,1 (pure, standing, quarantined-only, planned triple/quad) — twins: none
- b+3,4,1,2,1,4 (pure, standing, quarantined-only, planned triple/quad) — twins: none
- b+3,4,1,2,1,4,2 (pure, standing, quarantined-only, planned triple/quad) — twins: none
- b+3,4,1,2,1,4,2,1 (pure, standing, quarantined-only, planned triple/quad) — twins: none
- b+3,4,1,2,1,4,2,1,4 (pure, standing, quarantined-only, planned triple/quad) — twins: none
- b+3,4,1,2,1,4,2,1,4,2 (pure, standing, main, planned triple/quad) — twins: b+3,4,1,2,1,4,2,1,4,2~t7.bryan
- b+3,4,1,2,1,4,3,3,2 (pure, standing, main, planned triple/quad) — twins: none
- b+3,F (chord-involved, standing, main, rest CSV-only) — twins: none
- b,4 (chord-involved, standing, main, rest CSV-only) — twins: none
- b,B+4 (chord-involved, standing, main, rest CSV-only) — twins: b,B+4~t7.bryan
- b,d/f+4 (chord-involved, standing, main, rest CSV-only) — twins: none
- b,d/f+4,B (chord-involved, standing, main, rest CSV-only) — twins: none
- b,df+4 (chord-involved, standing, main, rest CSV-only) — twins: none
- b,f+2 (chord-involved, standing, main, rest CSV-only) — twins: none
- b,f+2,1 (chord-involved, standing, main, rest CSV-only) — twins: none
- d+1+2,3 (chord-involved, crouch, main, planned triple/quad) — twins: d+1+2,3~t7.bryan, d+1+2,3~t7.bryan.2, d+1+2,3~t7.bryan.3
- d+1+2,B (chord-involved, crouch, main, rest CSV-only) — twins: none
- d+1+2,F (chord-involved, crouch, main, rest CSV-only) — twins: none
- d+3+4,2 (chord-involved, crouch, main, planned triple/quad) — twins: d+3+4,2~t7.bryan, d+3+4,2~t7.bryan.2
- d+3+4,2,d/b (chord-involved, crouch, main, rest CSV-only) — twins: none
- d,d/f,d,d/f+1+2 (chord-involved, crouch, main, rest CSV-only) — twins: d,d/f,d,d/f+1+2~t3.bryan
- d,db,b (chord-involved, crouch, quarantined-only, rest CSV-only) — twins: none
- d/f+3+4,2 (chord-involved, crouch, main, planned triple/quad) — twins: none
- d/f+3+4,2,1 (chord-involved, crouch, main, planned triple/quad) — twins: none
- d/f+3+4,2,1,2 (chord-involved, crouch, main, planned triple/quad) — twins: none
- d/f+3+4,2,1,4 (chord-involved, crouch, main, planned triple/quad) — twins: none
- f+1,4,2 (pure, standing, main, planned triple/quad) — twins: f+1,4,2~t3.bryan
- f+1,4,3 (pure, standing, main, planned triple/quad) — twins: none
- f+2,1,4 (pure, standing, main, planned triple/quad) — twins: f+2,1,4~t7.bryan, f+2,1,4~t7.bryan.2, f+2,1,4~t7.bryan.3
- f+2,1,SNE.2,3 (pure, standing, quarantined-only, planned triple/quad) — twins: none
- f+2,1,SNE.2,3,2 (pure, standing, quarantined-only, planned triple/quad) — twins: none
- f,F+1+2 (chord-involved, standing, main, rest CSV-only) — twins: none
- f,F+2 (chord-involved, standing, main, rest CSV-only) — twins: f,F+2~t7.bryan
- f,F+3 (chord-involved, standing, main, rest CSV-only) — twins: f,F+3*, f,F+3*~t7.bryan, f,F+3~t7.bryan
- f,F+4 (chord-involved, standing, main, rest CSV-only) — twins: f,F+4~t7.bryan
- f,b+2 (chord-involved, standing, main, rest CSV-only) — twins: none
- f,f,F (chord-involved, standing, main, rest CSV-only) — twins: f,f,F~t7.bryan
- f,f,F+3 (chord-involved, standing, main, rest CSV-only) — twins: none
- f,f,f+3 (chord-involved, standing, main, rest CSV-only) — twins: none
- f,n,b+2 (chord-involved, standing, main, rest CSV-only) — twins: none
- n,d/b,n,f+1+2 (chord-involved, standing, main, rest CSV-only) — twins: none
- qcf+4,1,2 (pure, standing, main, planned triple/quad) — twins: qcf+4,1,2~t7.bryan, qcf+4,1,2~t7.bryan.2
- qcf+4,1,u,u (chord-involved, standing, main, rest CSV-only) — twins: none
- u/b+1+2,1,2,1,2,1,2,1,2,1,4 (chord-involved, jump, main, planned triple/quad) — twins: none
- ub+1+2,1,2,1,2,1,2,1,2,1,4 (chord-involved, jump, main, planned triple/quad) — twins: none
- uf,n,4 (chord-involved, jump, quarantined-only, rest CSV-only) — twins: none


Canonicalization (CORRECTED rule, mandatory): strip ONLY a trailing
~t[378].[a-z]+(.\d+)?$ suffix; a ~ INSIDE the input is part of the move.
Batch 4 scope checked, not copied: 0 input-~ canonicals, 0 corrupted
keys, 0 __main canonicals in Batch 4 scope. Spelling quirks kept
distinct: u/b+1+2,1,2,1,2,1,2,1,2,1,4 (step 1 verified row 43) vs
ub+1+2,1,2,1,2,1,2,1,2,1,4 (step 1 no candidate — different step-1
evidence, same last step row 76); WS-context fix applied (no wiring
change).

## Steps: 344 = 252 planned + 92 CSV-only

Planned steps: 83 verified / 11 review / 158 unmapped.
Unmapped split: 153 no-candidate / 2 rejected-candidate / 3 suspended-drift.
Canonical status (planned): 8 verified-all / 25 partial / 22 unmapped-all /
0 review-only.
Plan-key last-step: 23 verified / 1 review / 106 unmapped.

Per-string step detail (planned canonicals; twins inherit verbatim):

- 1,2,3 [standing] -> partial: 1=row 172; 2=unmapped; 3=unmapped
- 1,2,4 [standing] -> partial: 1=row 172; 2=unmapped; 4=unmapped
- 1,4,2 [standing] -> partial: 1=row 172; 4=unmapped; 2=unmapped
- 1,4,2,1 [standing] -> partial: 1=row 172; 4=unmapped; 2=unmapped; 1=unmapped
- 1,4,2,1,2 [standing] -> partial: 1=row 172; 4=unmapped; 2=unmapped; 1=unmapped; 2=unmapped
- 1,4,2,1,4 [standing] -> partial: 1=row 172; 4=unmapped; 2=unmapped; 1=unmapped; 4=unmapped
- 1,4,2,4 [standing] -> partial: 1=row 172; 4=unmapped; 2=unmapped; 4=unmapped
- 1,4,2,f+1 [standing] -> partial: 1=row 172; 4=unmapped; 2=unmapped; f+1=unmapped
- 1,4,3 [standing] -> partial: 1=row 172; 4=unmapped; 3=unmapped
- 1,4,3,3 [standing] -> partial: 1=row 172; 4=unmapped; 3=unmapped; 3=unmapped
- 2+4,1 [standing] -> unmapped-all: 2+4=unmapped (cand 138); 1=unmapped (cand 345)
- 3+4,SNE.2 [standing] -> unmapped-all: 3+4=unmapped; SNE.2=unmapped
- 3,2,1 [standing] -> unmapped-all: 3=unmapped (cand 63); 2=unmapped; 1=unmapped
- 3,2,1,2 [standing] -> unmapped-all: 3=unmapped (cand 63); 2=unmapped; 1=unmapped; 2=unmapped
- 3,2,1,4 [standing] -> partial: 3=unmapped (cand 63); 2=unmapped; 1=unmapped; 4=row 119
- SLS.4,1,2 [standing] -> unmapped-all: SLS.4=unmapped; 1=unmapped; 2=unmapped
- b+1+3,P.2 [standing] -> unmapped-all: b+1+3=unmapped; P.2=unmapped
- b+2,1,4 [standing] -> partial: b+2=review (cand 158); 1=unmapped; 4=unmapped
- b+3+4,2 [standing] -> verified-all: b+3+4=row 199; 2=row 171
- b+3+4,2,1 [standing] -> verified-all: b+3+4=row 199; 2=row 171; 1=row 176
- b+3+4,4,1 [standing] -> partial: b+3+4=row 199; 4=review (cand 200); 1=row 201
- b+3+4,4,1,2 [standing] -> partial: b+3+4=row 199; 4=review (cand 200); 1=row 201; 2=row 202
- b+3+4,4,1,2,1 [standing] -> partial: b+3+4=row 199; 4=review (cand 200); 1=row 201; 2=row 202; 1=row 203
- b+3+4,4,1,2,1,4 [standing] -> partial: b+3+4=row 199; 4=review (cand 200); 1=row 201; 2=row 202; 1=row 203; 4=row 204
- b+3+4,4,1,2,1,4,2 [standing] -> partial: b+3+4=row 199; 4=review (cand 200); 1=row 201; 2=row 202; 1=row 203; 4=row 204; 2=row 205
- b+3+4,4,1,2,1,4,2,1 [standing] -> partial: b+3+4=row 199; 4=review (cand 200); 1=row 201; 2=row 202; 1=row 203; 4=row 204; 2=row 205; 1=row 206
- b+3+4,4,1,2,1,4,2,1,4 [standing] -> partial: b+3+4=row 199; 4=review (cand 200); 1=row 201; 2=row 202; 1=row 203; 4=row 204; 2=row 205; 1=row 206; 4=review (cand 207)
- b+3+4,4,1,2,1,4,2,1,4,2 [standing] -> partial: b+3+4=row 199; 4=review (cand 200); 1=row 201; 2=row 202; 1=row 203; 4=row 204; 2=row 205; 1=row 206; 4=review (cand 207); 2=row 208
- b+3,1+2 [standing] -> unmapped-all: b+3=unmapped; 1+2=unmapped
- b+3,2,1 [standing] -> unmapped-all: b+3=unmapped; 2=unmapped; 1=unmapped
- b+3,2,1,2 [standing] -> unmapped-all: b+3=unmapped; 2=unmapped; 1=unmapped; 2=unmapped
- b+3,2,1,4 [standing] -> unmapped-all: b+3=unmapped; 2=unmapped; 1=unmapped; 4=unmapped
- b+3,4,1 [standing] -> unmapped-all: b+3=unmapped; 4=unmapped; 1=unmapped
- b+3,4,1,2 [standing] -> unmapped-all: b+3=unmapped; 4=unmapped; 1=unmapped; 2=unmapped
- b+3,4,1,2,1 [standing] -> unmapped-all: b+3=unmapped; 4=unmapped; 1=unmapped; 2=unmapped; 1=unmapped
- b+3,4,1,2,1,4 [standing] -> unmapped-all: b+3=unmapped; 4=unmapped; 1=unmapped; 2=unmapped; 1=unmapped; 4=unmapped
- b+3,4,1,2,1,4,2 [standing] -> unmapped-all: b+3=unmapped; 4=unmapped; 1=unmapped; 2=unmapped; 1=unmapped; 4=unmapped; 2=unmapped
- b+3,4,1,2,1,4,2,1 [standing] -> unmapped-all: b+3=unmapped; 4=unmapped; 1=unmapped; 2=unmapped; 1=unmapped; 4=unmapped; 2=unmapped; 1=unmapped
- b+3,4,1,2,1,4,2,1,4 [standing] -> unmapped-all: b+3=unmapped; 4=unmapped; 1=unmapped; 2=unmapped; 1=unmapped; 4=unmapped; 2=unmapped; 1=unmapped; 4=unmapped
- b+3,4,1,2,1,4,2,1,4,2 [standing] -> unmapped-all: b+3=unmapped; 4=unmapped; 1=unmapped; 2=unmapped; 1=unmapped; 4=unmapped; 2=unmapped; 1=unmapped; 4=unmapped; 2=unmapped
- b+3,4,1,2,1,4,3,3,2 [standing] -> unmapped-all: b+3=unmapped; 4=unmapped; 1=unmapped; 2=unmapped; 1=unmapped; 4=unmapped; 3=unmapped; 3=unmapped; 2=unmapped
- d+1+2,3 [crouch] -> unmapped-all: d+1+2=unmapped; 3=unmapped
- d+3+4,2 [crouch] -> unmapped-all: d+3+4=unmapped; 2=unmapped
- d/f+3+4,2 [crouch] -> verified-all: d/f+3+4=row 103; 2=row 169
- d/f+3+4,2,1 [crouch] -> verified-all: d/f+3+4=row 103; 2=row 169; 1=row 170
- d/f+3+4,2,1,2 [crouch] -> verified-all: d/f+3+4=row 103; 2=row 169; 1=row 170; 2=row 177
- d/f+3+4,2,1,4 [crouch] -> verified-all: d/f+3+4=row 103; 2=row 169; 1=row 170; 4=row 180
- f+1,4,2 [standing] -> verified-all: f+1=row 172; 4=row 187; 2=row 154
- f+1,4,3 [standing] -> verified-all: f+1=row 172; 4=row 187; 3=row 188
- f+2,1,4 [standing] -> partial: f+2=row 150; 1=unmapped; 4=unmapped
- f+2,1,SNE.2,3 [standing] -> partial: f+2=row 150; 1=unmapped; SNE.2=unmapped; 3=unmapped
- f+2,1,SNE.2,3,2 [standing] -> partial: f+2=row 150; 1=unmapped; SNE.2=unmapped; 3=unmapped; 2=unmapped
- qcf+4,1,2 [standing] -> unmapped-all: qcf+4=unmapped; 1=unmapped; 2=unmapped
- u/b+1+2,1,2,1,2,1,2,1,2,1,4 [jump] -> partial: u/b+1+2=row 43; 1=unmapped; 2=unmapped; 1=unmapped; 2=unmapped; 1=unmapped; 2=unmapped; 1=unmapped; 2=unmapped; 1=unmapped; 4=row 76
- ub+1+2,1,2,1,2,1,2,1,2,1,4 [jump] -> partial: ub+1+2=unmapped; 1=unmapped; 2=unmapped; 1=unmapped; 2=unmapped; 1=unmapped; 2=unmapped; 1=unmapped; 2=unmapped; 1=unmapped; 4=row 76

## Wired fills (all VERIFIED, gate-verified own/recorded-path rows, T3 FALLBACK)

23 distinct rows, all present in the current main bryan rows.pack (160
rows): 43, 76, 103, 119, 150, 154, 169, 170, 171, 172, 176, 177, 180, 187,
188, 199, 201, 202, 203, 204, 205, 206, 208.

- Verified-all (8): b+3+4,2 [199,171]; b+3+4,2,1 [199,171,176];
  d/f+3+4,2 [103,169]; d/f+3+4,2,1 [103,169,170]; d/f+3+4,2,1,2
  [103,169,170,177]; d/f+3+4,2,1,4 [103,169,170,180]; f+1,4,2
  [172,187,154]; f+1,4,3 [172,187,188].
- GATE-NOTE (standing rows for crouch-context steps, demonio Batch 1
  precedent — re-adjudicate if the gate is ever tightened): the whole
  d/f+3+4,2 family (13 steps: rows 103/169/170/177/180). Row 103 is the
  same row as Batch 2's d/f+3+4,3 step 1 hold, independently re-derived.
- Jump-context verified steps carry the SOFT waiver per Batch 1
  precedent: u/b+1+2,1,2,1,2,1,2,1,2,1,4 step 1 row 43 + last step row
  76; ub+1+2 twin last step row 76 (step 1 unmapped — different step-1
  evidence, spelling quirk kept).
- ONE Job 3 fill (see Job 3): 3,2,1,4 step 4 <- row 119.

## Suspended-drift (3)

3,2,1 step 1, 3,2,1,2 step 1, 3,2,1,4 step 1 — prefix move 3
ROW-CHANGED 63→None on main. Stale jump row 63 ([9,9,52,535,0,4])
documented, never wired. Suspension comes first, before any stance
question (row 63 would fail ground gates regardless). This is the check
that mattered in Batch 4: Batch 4 strings CAN start with 3, so the
row-change re-check was run explicitly and it FIRED.

## Review steps (11)

- b+2,1,4 step 1 — candidate 158, STANCE-SOFT duck-dip row for a
  standing-context step. Same row/result as Batch 1's b+2 holds,
  independently re-derived. Job 4 join confirms HARD gates pass, but a
  join never promotes.
- b+3+4,4,1 family step 2s (8 strings) — candidate 200, SOFT limb-peak
  proxy fail, window [3.5,7.5] legR peak 26. Same row/result as Batch
  2's b+3+4,4 hold, independently re-derived. Job 4 joins confirm HARD
  gates pass, but a join never promotes.
- b+3+4,4,1,2,1,4,2,1,4 step 9 + b+3+4,4,1,2,1,4,2,1,4,2 step 9 —
  candidate 207, SOFT limb-peak proxy fail, window [9.0,14.0] legR
  peak 2. Job 4 joins confirm HARD gates pass, but a join never
  promotes.

## Rejected-candidate (2)

- 2+4,1 step 1 — candidate 138, button 5 != step bits 10 + throw flag
  1 (row is a throw row).
- 2+4,1 step 2 — candidate 345, button 0 != step bits 1 + throw flag
  1 + ground row (downed-foe row) for a standing string step. (Row 345
  also a Job 4 join, REJECTED on the same grounds.)

## No-candidate (153)

Intermediate prefixes are T8-sourced strings with no T3 row — correct
clips come from #988 Step 2 (original T8 refs) or future extraction,
never from a T3 row recorded as correct. Donor rows documented in the
CSV, never wired as whole-string clips.

## Job 3 (15 report entries, 1 fill wired)

- FILL: 3,2,1,4 step 4 <- row 119 (exact level, FULL provenance
  moveset_skull:4~t3.bryan.2(RK), timing 1.33, HARD + SOFT pass under
  the stricter burger fill rule). Steps 1–3 of that string stay
  unmapped (step 1 suspended, steps 2–3 no candidate). The only other
  exact+FULL-adjacent candidate, row 131 (exact, ROW-ONLY) for the same
  step, was not picked.
- All other candidates ROW-ONLY or soft, never wired (e.g. row 99 exact
  ROW-ONLY + rows 132/146/147/148 soft-filed ROW-ONLY for the 1,4,2
  family step 1s; rows 117/167 soft-nofiled ROW-ONLY for d+1+2,F; row
  167 exact ROW-ONLY for d+3+4,2 step 2s). No agreement note fires —
  no exact+FULL candidate disagrees with a wired gate candidate.
- Dedupe fires 0 times (no Batch 4 step prefix has a __main Job 3
  target at all). No SOFT fill inherited from #1097.

## Job 4 (corrected join only: 24 joins, 0 promotions, 0 orphans)

8 no-action (verified steps: rows 171, 203), 11 CANDIDATE-not-wired
(rows 158, 200, 207 — a join never promotes by itself), 1 REJECTED
(row 345, throw + ground), 4 rest-key joins documented, not
adjudicated for wiring (a bits-0 rest step would otherwise match
button-0 rows — rest steps are never gate-adjudicated). Naive
cross-fighter join not used.

## Donor rows documented, never wired

63 (stale jump row, suspended), 100/104/172 (own basics, appear as
whole-string donors for unmapped strings), 137/138/345/351 (throw
rows), 158/200/207 (review holds), 42/43 (u/b+1/u/f+1 first-step
rejects in earlier batches — Batch 4's u/b+1+2 family step 1 row 43 is
a VERIFIED jump-context row, not the Batch 1 ground-step rejection;
context adjudicated per step, per the dual-role caution).

## Tests

Minimal-tree node --test: 47/47 pass (13 Batch 1 tests + 8 Batch 2
tests + 12 Batch 3 tests + 14 Batch 4 tests, Batch 1–3 content
assertions diff-verified preserved verbatim — only the header note,
B4 const, count 198→328, rule-2 count line, and the three cumulative
extra-keys assertions changed). node --check fighter.js OK (fighter.js
unchanged). Formatter round-trips the Batch 3 branch file
byte-identically; structural diff: all non-plan keys identical, all
198 Batches 1–3 plans deep-equal, plan count 198 → 328 (130 Batch 4
keys, 0 collisions). Limitation (stated in the PR body): full 200-test
suite comparison NOT run — no full current-main checkout on this box;
CI must cover it before merge.

## Play-verify checklist (parent browser delegation, after #1129 + #1130 + #1131 + this PR merge + deploy + sync, phone portrait)

- b+3+4,2 [199,171]; b+3+4,2,1 [199,171,176] — verified-all, all steps
  grounded.
- d/f+3+4,2 [103,169]; d/f+3+4,2,1 [103,169,170]; d/f+3+4,2,1,2
  [103,169,170,177]; d/f+3+4,2,1,4 [103,169,170,180] — verified-all,
  GATE-NOTE crouch family (verify the standing rows read as
  crouch-context strikes).
- f+1,4,2 [172,187,154]; f+1,4,3 [172,187,188] — verified-all, all
  steps grounded.
- 3,2,1,4 [NO row,NO row,NO row,119] — step 4 Job 3 fill row 119
  grounded RK4; step 1 NO row (stale row 63 must NOT play).
- 3,2,1 / 3,2,1,2 — step 1 NO row (stale row 63 must NOT play); later
  steps NO row.
- b+2,1,4 [review-NO row,NO row,NO row] — review row 158 held, must
  NOT play.
- b+3+4,4,1 family — step 2 NO row (review row 200 held, must NOT
  play); step 9 NO row where present (review row 207 held, must NOT
  play).
- 2+4,1 — NO row any step (throw rows 138/345 must NOT play).
- u/b+1+2,1,2,1,2,1,2,1,2,1,4 — first step row 43 + last step row 76
  (jump family, SOFT waived); middle steps NO row. ub+1+2 twin — step
  1 NO row, last step row 76.
- All other Batch 4 planned canonicals — NO row except where listed
  above (donor rows 63/100/104/172 must NOT appear as whole-string
  clips).
- Rest keys unchanged — donor clips, NOT per plan (incl. f,F+2,
  f,F+3, f,F+4, b,4, WALL.b,b,u/b, uf,n,4).
- No step plays a bryan airborne/jump row for a ground step; no step
  plays a row from another bank; no step plays row 220, 216, or 35.
- Batches 1–3 spot-checks undisturbed: 2,1 [152,153]; 2,1,2
  [152,153,151]; f+1,2 [172,173]; d/f+1+2 family
  [113,149]/[113,146]/[113,146,147]/[113,146,147,148]; 1,2
  [172,NO row]; b+1,2 [NO row,145]; b+2,f+1,2 step 3 row 151; jump
  step-2 rows 44/56/46/58/45/57; 4,3 [104,NO row]; b+3+4,4
  [199,NO row]; d/f+3+4,3 [103 GATE-NOTE,NO row]; f+4,3 [NO row,193];
  f+4,3,4 [NO row,193,194]; 3,3/3,3,4 NO row (stale 63); f+1,4
  [172,187]; 2,3 [100,NO row]; 2,4 [100,review-NO row]; 4,1
  [104,NO row]; d/f+2,3 [149 GATE-NOTE,NO row]; 3,2/3,3,2 NO row
  (stale 63); u+1,3 step 2 NO row (stale 63); u+1,4 [NO row,76];
  u/b+1,3 [NO row,65]; u/b+1,4 [NO row,78]; u/f+1,3 [NO row,64];
  u/f+1,4 [NO row,77]; b+2,4 [review-NO row,NO row]; 1+3,1 NO row
  (throw 137/351).
- Quarantined-only Batch 4 strings behave per plan ONLY after #988
  merges (12 planned: 3+4,SNE.2; SLS.4,1,2; b+1+3,P.2; b+3,4,1 family
  x8; f+2,1,SNE.2,3 family x2; + 4 rest: (Back to wall).b,b,UB;
  SNE.f,F+1+2,P; d,db,b; uf,n,4).
