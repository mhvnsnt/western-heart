# PHANTOM BATCH 2 — LK3/RK4-ONLY STEP PLANS (2026-10-25)

Stack: #1096 engine → phantom Batch 1 (#1121) → **this Batch 2** → Batch 3 (mixed pairs) → Batch 4 (triples/quads/rest).
Base: phantom Batch 1 branch `feat/phantom-batch1-step-plans-20261025` (head `238bbff84325f04f8878d314832e43e48cddd9b2`, re-verified before branching).
This PR merges AFTER #1121 (after #1096) and merges nothing itself.

## Method (phantom Batch 1 + kinpo/diablo/Pantera/burger/demonio precedent)

- Universe: moves-dict keys + strings-list entries whose steps are ALL buttoned
  and whose button union is a subset of {LK3, RK4} = {3, 4}. Pure
  single-button strings first, then chord-involved (LK3+RK4 chords).
- Canonical key = key minus a TRAILING source-variant suffix ONLY (CORRECTED
  rule, demonio Batch 2 finding): strip only `~t[378]\.[a-z]+(\.\d+)?$`, then a
  trailing `*` hold marker. A `~` INSIDE the input is Tekken cancel notation,
  part of the move, never a variant marker. A `__main` record is its OWN
  canonical, not a twin, when the record differs (distinct damage/anim_ref).
  Spelling quirks kept as stored keys (never merged, never smoothed over).
  Corrupted keys are filed verbatim, unmapped, as an open data-quality
  follow-up — never fixed in the lane.
- Step candidate: recorded path row (strings[].t3_rows full-path index, or
  dest-only for the last step), else the prefix move's t3_row, else none.
- HARD gates (fail = unmapped, candidate documented): hit_frames button ==
  step bits (LK3=4, RK4=8, chords OR-ed); throw == 0 for strike steps;
  stance: jump/starts-airborne rows fail ground-context steps and pass
  jump-context steps; crouch/duck-dip rows pass only crouch-context steps
  (else STANCE-SOFT review); ground rows fail all (downed-foe rows);
  ws-context steps matched to standing rows are review (ws->standing
  soft-stance). GATE NOTE (demonio Batch 1 edge): the gate flags crouch rows
  for non-crouch steps, NOT standing rows for crouch steps.
- ROW DUAL-ROLE CAUTION (Pantera Batch 4): a row verified for one
  string/context is NOT globally verified — every step gate-checks its own
  row again.
- SOFT gate (fail = review, candidate documented, row null): Job 1 peakF
  proxy — window = [active_first/2 - 2, active_last/2 + 2]; step limb peakF
  in window passes. WAIVED for jumping-context strings (Batch 1 precedent).
  The proxy is conservative: proxy-fail means review, never a false verify.
- Job 3 fills (exact-prefix rule: target key == step prefix): wired ONLY if
  exact level (filed == played, filed non-empty) + FULL provenance (row in
  job3.log provenance list AND top10 provenance non-empty) + step HARD gates
  pass + SOFT proxy passes (burger refinement, stricter than Pantera Batch 4's
  HARD-only fill rule). DEDUPE (burger Batch 2 cleanup): a prefix__main
  pass-all row identical to a prefix pass-all row is reported once (prefix
  target kept). SOFT (soft-filed / soft-nofiled) and ROW-ONLY candidates are
  documented, NEVER wired. A gate-verified own/recorded candidate beats a
  disagreeing Job 3 candidate (own row is stronger file evidence). JOB 3
  AGREEMENT-NOTE WORDING (demonio Batch 4 fix): the agreement note fires
  ONLY for actually-wired gate candidates — never claim a failed gate
  candidate was "kept".
- Job 4 joins (CORRECTED join only): yoshimitsu candidate joins a step iff Job 2
  has a phantom entry key == step prefix, row == candidate row, step == 'own'.
  A join NEVER promotes a candidate by itself.
- Re-baseline: every prefix move compared Batch 1 branch vs current main
  (main moves, else main quarantine). Row-changed (different t3_row) => step
  SUSPENDED (status unmapped, SUSPENDED-DRIFT reason, never wired on stale
  data). Damage-only drift is noted, NOT suspending (damage is not animation).
- T3 rows are FALLBACK matches (docs/anim/PROCEDURAL_AUDIT.md), never the
  correct mapping, to be re-matched to T7 Yoshimitsu rows when decode lands.
  NO T8 REMOVALS: main's quarantine section is read for classification only
  and never modified. Nothing here touches t8_quarantine_20261024.

## Bank: YOSHIMITSU — NATIVE, not a fallback (re-verified, not assumed)

phantom.json `t3_source` 'yoshimitsu', `t3_bank` 'moveset_yoshimitsu.json' on
BOTH the Batch 1 branch and main. `game/assets/anim/t3/` on main contains a
`yoshimitsu` dir (hit_frames + rows.pack + skeleton). Job 1 bank yoshimitsu:
215 rows. Job 2 phantom entries: 1019, ALL bank yoshimitsu. Job 4 yoshimitsu
candidates: 47. Phantom's T7/T8 base IS Yoshimitsu, so no fallback resolution
was needed (contrast burger Bob→bryan, kinpo Asuka→jin); pack dir does NOT
differ from the moveset bank name (no diablo-style split).

Bank-specific row rules (never cross-bank): rows 35 and 220 do NOT EXIST in
this bank (absent from hit_frames AND Job 1) — no row-35/row-220 rule applies
at all. Row 216 is a STANDING LP1 row here ([11,11,26,1042,0,1], Job 1
standing) — NOT king row 216's dash Konvict Kick, NOT jin row 216's jump row.
Row 243 is a CHORD row (button 9 = LP1+RK4) failing every single-button gate.

Gap-1: ZERO bank drift — hit_frames dfc15d71…, rows.pack cb2a81f… (215 rows),
skeleton 82d2546e… identical on the Batch 1 branch and main (same blobs as
the Batch 1 baseline). Every wired row is present in the CURRENT main pack
(the game plays from the pack).

## Universe (measured first, not assumed)

- Base = Batch 1 branch phantom.json: 1019 moves / 191 strings / 186 plans.
  Batch 1 branch moves == #1096 moves exactly (verified); strings identical.
  Current main: 834 moves + 185 quarantined = 1019 exactly; 0 main-only moves;
  strings 191/191. Main phantom.json blob 4afcf4d2… UNCHANGED since the Batch 1
  baseline.
- **41 canonicals** (27 pure + 14 chord-involved); **ALL 41 planned, 0 CSV-only**;
  49 CSV rows (41 canonicals + 8 twins); **49 plan keys**.
  Contexts: standing 22, crouch 15, jump 4, ws 0.
  Provenance: 33 in main moves, 8 quarantined-only (IND.3,3+4; b+3,3; b+3,3,3;
  b+3,3,3,3; b+3,3,3,3,3; b+3,3,3,3,3,3; db+3,3,3,3,3,4; uf+3+4,3 — live when
  #988 merges), 0 Batch 1-branch-only.
- Overlap vs Batch 1 universe: []. Overlap vs Batch 1 plans: [].
- **Input-~ canonicals in Batch 2 scope: 0** — phantom inert on this axis, like
  Pantera/burger/kinpo/Batch 1. The file's ONLY old-vs-corrected diffs are
  `3~4,U` (rest key, buttonless U step), `4,4,2,2,1,~1` and `4,4,2,2,NSS.1,~1`
  (triples, union {1,2,4} → Batch 4 scope) — none falls in Batch 2 scope;
  all stay their own keys for later batches, never variants.
- **__main canonicals in scope: 0; corrupted keys in scope: 0** (no
  diablo-style escaped-colon key).
- **Spelling quirks kept:** `D/B+3` vs `d/b+3` vs `db+3` families are distinct
  canonicals (different step evidence: the `d/b+3,d/b+3` family is review-held
  on SOFT fails, while the `D/B+3,3` and `db+3,3` families have no candidate
  at all) — not merged, not smoothed over. `u/f+3+4` vs `uf+3+4` are distinct
  canonicals (different step evidence: `u/f+3+4` step 1 verified row 291 vs
  `uf+3+4` step 1 no candidate). WS-context fix (kinpo Batch 1): lowercase
  no-dot while-standing spellings are WS context, not standing; changes NO
  wiring (Batch 2 has no ws-context canonicals).

## Step tallies

- **129 steps, all planned: 3 verified / 19 review / 107 unmapped /
  0 suspended-drift as a status** (2 steps carry SUSPENDED-DRIFT reasons inside
  status unmapped).
- Unmapped split: **90 no-candidate + 15 rejected-candidate + 2 suspended-drift**.
- Canonical status: 0 verified-all / 5 partial / 6 review-only / 30 unmapped-all.
- Plan-key last-step: 1 verified / 7 review / 41 unmapped.
- Verified rows (2 distinct, all baked in main's yoshimitsu pack): 73, 291.

## Every wired fill (verified only, all gate-verified prefix-move own rows, T3 FALLBACK)

- **u/f+3+4,3+4 (partial):** step 1 ← **291** (prefix-move own row, jump chord
  LK3+RK4, hit_frames [31,35,87,535,0,12], Job 1 stance jump, SOFT waived jump
  context); step 2 unmapped (no candidate).
- **u/f+3+4,u+3+4 (partial):** step 1 ← **291** (same row, same evidence, own
  step prefix); step 2 unmapped (no candidate).
- **uf+3+4,3 (partial):** step 1 unmapped (no candidate); step 2 ← **73**
  (prefix-move own row, jump LK3, hit_frames [9,9,52,535,0,4], Job 1 stance
  jump, SOFT waived jump context).
- No gate-note cases this batch (all verified steps are jump-context on jump
  rows). Both wired rows verified present in the CURRENT main yoshimitsu pack
  at wire time.

## Review holds (19 steps, row null, NOT wired)

All 19 pass HARD gates and fail the SOFT limb-peak proxy (conservative:
proxy-fail = review, never a false verify):

- d/b+3 family (12 steps): row 245 (steps d/b+3, window [7.5,11.5], legL peak
  27); row 246 (steps d/b+3,d/b+3, window [3.0,11.0], legL peak 22); row 247
  (steps d/b+3,d/b+3,d/b+3, window [3.0,11.0], legL peak 22); row 248 (step
  d/b+3,d/b+3,d/b+3,d/b+3, window [3.0,11.0], legL peak 22); row 257 (step
  d/b+3,d/b+3,4, window [4.0,8.5], legR peak 22; also a Job 4 CANDIDATE,
  never promoted).
- f+4 family (6 steps): row 258 (steps f+4, window [1.5,6.0], legR peak 10);
  row 255 (steps f+4,4 / f+4,4,4, window [14.5,18.5], legR peak 38; also a
  Job 4 CANDIDATE, never promoted); row 256 (step f+4,4,4, window
  [14.5,19.0], legR peak 38).
- f+3+4,4 step 2 (1 step): row 254 (window [3.0,7.5], legR peak 26).

## Suspended-drift (2 steps, row null, never wired)

- 4,4 step 1 and 4,4,4 step 1 — prefix move `4` is row-changed on main
  (243→None). Stale row 243 documented, never wired (it is a chord row,
  button 9 = LP1+RK4, and would fail every single-button gate regardless).
- The other 4 row-changed moves (1, 1_r62, 2, u+1,1~t3.yoshimitsu.2) are NOT
  Batch 2 step prefixes — hence no further suspensions. (Batch 1's
  suspensions were prefix 1 / prefix 2 steps; this batch's prefixes are
  kick-only, so only prefix 4 suspends.)

## Rejected-candidate (15 steps, row null)

- b+3+4 family (14 steps): rows 191/192/193/194 — throw flag 1 (row is a throw
  row) for strike steps. The b+3+4 moves carry move_class string (not throw),
  so the strings ARE planned, but their prefix-move rows are throw rows and
  fail the strike HARD gates — unmapped, never wired as strikes. (Same
  pattern as other batches' throw-named chains with move_class string.)
  Steps: b+3+4,b+3+4 steps 1–2 (rows 194/191); b+3+4,b+3+4,b+3+4 steps 1–3
  (194/191/192); b+3+4,b+3+4,b+3+4,b+3+4 steps 1–4 (194/191/192/193);
  b+3+4,b+3+4,b+3+4,b+3+4,b+3+4 steps 1–5 (194/191/192/193/194).
- f+4,3 step 2 (1 step): row 275 (recorded-dest) — ground row (downed-foe row)
  for a standing string step; also a Job 4 join, REJECTED for the same reason.

## No-candidate (90 steps)

Recorded path + prefix move both absent — T8-sourced prefixes with no T3 row;
correct clips come from #988 Step 2 (original T8 refs) or future extraction:

- 4,4 steps 2; 4,4,4 steps 2–3 (prefix 4 suspended; later steps no candidate).
- D/B+3,3 family (D/B+3,3; D/B+3,3,3; D/B+3,3,3,3; D/B+3,3,3,3,3;
  D/B+3,3,3,3,3,3) all steps — recorded path + prefix move both absent.
- IND.3,3+4; INS.3,3+4; KIN.4,3+4; SS.4,3+4 all steps (stance-token steps with
  no T3 row for the stance prefix).
- b+3,3 family (b+3,3; b+3,3,3; b+3,3,3,3; b+3,3,3,3,3; b+3,3,3,3,3,3) all
  steps — quarantined-only strings, clips from #988 Step 2.
- db+3,3 family (db+3,3; db+3,3,3; db+3,3,3,3; db+3,3,3,3,3;
  db+3,3,3,3,3,3; db+3,3,3,3,3,4) all steps.
- f+3+4,4 step 1; f+3,3 steps 1–2; f+3,3,d+3+4 steps 1–3; f+3,4 steps 1–2;
  u/f+3+4,3+4 step 2; u/f+3+4,u+3+4 step 2; uf+3+4,3 step 1; uf+3+4,3+4
  steps 1–2. (f+4,3 is NOT no-candidate: its step 1 is review row 258 and
  its step 2 is the rejected ground row 275 above.)
- Whole-string donor rows documented in the CSV, never wired: row 309 (4,4
  family, jump, HARD stance); row 277 (u/f+3+4,3+4 / uf+3+4,3+4 families,
  ground, HARD stance); row 87 (f+3,3,d+3+4, jump); row 85 (u/f+3+4,u+3+4
  family, jump).

## Job 3 / Job 4

- Job 3 fills wired: **0**. Report entries: 3. f+3,3 step 2 — row 163
  soft-nofiled ROW-ONLY (target f+3,3); f+3,3,d+3+4 step 2 — same row 163
  soft-nofiled ROW-ONLY (same target f+3,3, the shared step prefix);
  u/f+3+4,3+4 step 2 — row 86 exact ROW-ONLY (target u/f+3+4,3+4). ROW-ONLY
  and soft candidates are documented, NEVER wired. No agreement note fires:
  the note fires ONLY for actually-wired gate candidates disagreeing with an
  exact+FULL Job 3 candidate, and no exact+FULL Job 3 candidate exists for
  any verified step (the verified steps' prefixes u/f+3+4 and uf+3+4,3 have
  no Job 3 entry at all). Dedupe fires zero times: the only Batch 2 step
  prefix with a __main Job 3 target (f+4) shares no pass-all row with the
  plain prefix target.
- Job 4 joins (CORRECTED join only, BANK_DIR yoshimitsu): **6, none
  promoting** — row 291 no-action on both verified steps (u/f+3+4,3+4 and
  u/f+3+4,u+3+4 step u/f+3+4); rows 257/255/255 CANDIDATE-not-wired (a join
  never promotes by itself); row 275 REJECTED (ground row). Orphans: **0** —
  all 47 yoshimitsu Job 4 candidates are carried by some phantom Job 2 move
  (same as Batch 1).

## Drift census (both ways)

Full file (B1 branch vs current main, 1019 keys), identical to Batch 1's:
670 same / 218 damage-only / 126 anim_ref-changed / 5 ROW-CHANGED
(1: 62→None, 1_r62: 62→None, 2: 307→None, 4: 243→None,
u+1,1~t3.yoshimitsu.2: 62→None). Damage differs on 281 moves (218 damage-only
+ 63 gap). Both damage figures are true under their definitions; never
silently pick one. Damage-only drift does NOT suspend.

## Tests (file evidence only — NOT play-verified)

Minimal-tree `node --test` (see test files in this PR): Batch 1 cumulative +
Batch 2 assertions; `node --check fighter.js` OK. Formatter round-trips the
Batch 1 branch file byte-identically; all non-plan keys identical; all 186
Batch 1 plans deep-equal; moves 1019 / strings 191 unchanged. The Batch 1
test diff proves every CONTENT assertion preserved verbatim (only counts,
extra-keys/complement counts, const additions, header notes changed — the
burger Batches 2–4 fix; Pantera's latent break NOT copied).

**Limitation (honest):** full 200-test suite comparison NOT run — no full
current-main checkout on this box; CI must cover before merge.

## Play-verify checklist (parent browser delegation, after #1096 + #1121 + #1122 merge + deploy + sync, phone portrait)

- u/f+3+4,3+4 [291, NO row] and u/f+3+4,u+3+4 [291, NO row] — jump context,
  airborne row 291 correct here; donor ground row 277 must NOT play.
- uf+3+4,3 [NO row, 73] — jump context, airborne row 73 correct here; first
  step NO row.
- uf+3+4,3+4: NO row any step (donor ground row 277 must NOT play).
- 4,4 / 4,4,4: NO row any step (stale chord row 243 must NOT play; donor jump
  row 309 must NOT play).
- d/b+3,d/b+3 family / f+4 family / f+3+4,4 step 2: NO row any step (review
  rows 245/246/247/248/257/258/255/256/254 held, must NOT play).
- b+3+4 family: NO row any step (throw rows 191/192/193/194 must NOT play).
- f+4,3: NO row any step (ground row 275 must NOT play).
- All other Batch 2 strings (D/B+3,3 family; IND.3,3+4; INS.3,3+4; KIN.4,3+4;
  SS.4,3+4; b+3,3 family; db+3,3 family; f+3,3; f+3,3,d+3+4; f+3,4): NO row any
  step (donor rows 309/277/87/85 must NOT appear as whole-string clips).
- No step plays rows 35/220 (they do not exist in this bank). No step plays a
  row from another bank.
- Phantom Batch 1 spot-checks undisturbed (d/f+1,1 [223,224], d/f+1,1,1,1
  [223,224,225,226], u/b+1,1 [55,58], u/f+1,2 [66,70], 1,1 step 1 still
  suspended, 2,2 step 1 still suspended). Quarantined-only strings behave
  per plan ONLY after #988 merges (Batch 2: IND.3,3+4; b+3,3 family;
  db+3,3,3,3,3,4; uf+3+4,3).

**No play verification is claimed** — tests + file evidence only; playing is
the parent's step after merge + deploy.
