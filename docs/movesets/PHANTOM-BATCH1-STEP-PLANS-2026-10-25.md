# PHANTOM BATCH 1 — LP1/RP2-only strings: step plans (2026-10-25)

Stack: #1096 (engine) → this PR (phantom Batch 1). Merges AFTER #1096.
Branch: `feat/phantom-batch1-step-plans-20261025`, base
`feat/batch1-step-plans-pantera-20261024` (#1096's engine branch).
Does NOT stack on any Pantera/burger/demonio/diablo/kinpo plan branch.
Does NOT touch fighter.js, pantera.json, burger.json, demonio.json,
diablo.json, or kinpo.json. Merges nothing itself.

Button names: LP1 = Left Punch = Tekken 1, RP2 = Right Punch = Tekken 2,
LK3 = Left Kick = Tekken 3, RK4 = Right Kick = Tekken 4.

All T3 rows wired here are FALLBACK, never the correct mapping — logged in
docs/anim/PROCEDURAL_AUDIT.md, to be re-matched to T7 Yoshimitsu rows when
decode lands. No T8 content touched: nothing in t8_quarantine_20261024
changed, no UNMAPPED:t7-clip-pending marker stripped.

## 0. Bank — VERIFIED, not assumed

Phantom's T3 bank is YOSHIMITSU, by four-way file evidence:

1. phantom.json `t3_source` = `yoshimitsu`, `t3_bank` =
   `moveset_yoshimitsu.json`, on BOTH the #1096 branch (blob
   7441ecbab97472a75febcf2fb2282cf9edd49bb3) and current main (blob
   4afcf4d2a896f3f0d3d89c24719916051df5e0ff).
2. `game/assets/anim/t3/` on main contains a `yoshimitsu` dir
   (hit_frames + rows.pack + skeleton).
3. Job 1 bank yoshimitsu: 215 rows.
4. Job 2 phantom entries: 1019, ALL bank yoshimitsu.
5. Job 4 yoshimitsu candidates: 47.

Bank resolution, documented not assumed: phantom's T7/T8 base IS Yoshimitsu
(tekken_base Yoshimitsu, merge_sources t8/t7/t3 yoshimitsu) — this bank is
NATIVE, not a fallback (contrast burger Bob → bryan, kinpo Asuka → jin:
Bob and Asuka have no T3 bank; Yoshimitsu does). The pack dir does NOT
differ from the moveset bank name here (unlike diablo's
heihachi/heihachi_on_jin split).

Gap-1, ZERO bank drift: main yoshimitsu hit_frames blob dfc15d71…,
rows.pack blob cb2a81f… (215 rows), skeleton blob 82d2546e… are IDENTICAL
on #1096 and main.

Yoshimitsu-bank rules, per-bank evidence (never a cross-bank blanket ban):

- Rows 35 and 220 do NOT EXIST in this bank (absent from hit_frames AND
  Job 1) — no row-35/row-220 rule applies at all. Any candidate citing
  35/220 for phantom would be a data error, never a gate decision.
- Row 216 is a STANDING LP1 row here (hit_frames [11,11,26,1042,0,1],
  Job 1 standing) — NOT king row 216's dash Konvict Kick, NOT jin row
  216's jump row (demonio Batch 3's warning, applied).
- Row 243 is a CHORD row (hit_frames [4,12,40,1543,0,9] = bits LP1+RK4,
  throw 0; Job 1 standing, dominant armL, level u) — it fails every
  single-button gate (9 ≠ 1, 9 ≠ 8, 9 ≠ 2, 9 ≠ 4). This is the prior
  note's "RK4 chord-arm row 243", adjudicated here from file evidence,
  not from the note.
- Yoshimitsu Job 1 stances: standing 83, crouch 37, starts-airborne 36,
  jump 33, ground 14, duck-dip 12 (duck-dip rows: 127, 148, 221, 236, 242,
  274, 297, 300, 304, 305, 311, 425 — handled like crouch: STANCE-SOFT
  review for non-crouch contexts).

Phantom basics, prior note CONFIRMED from file evidence (never taken on
faith): LP1 move 1 carries t3_row 62 on #1096 (hit_frames
[7,7,35,535,0,1]; Job 1 stance starts-airborne, y0 0.878 vs standingY
0.220; Job 2 verdict HARD stance) — LP1 IS airborne. RP2 move 2 carries
t3_row 307 on #1096 (hit_frames [10,12,15,535,0,2]; Job 1 stance CROUCH,
y0 -0.010; Job 2 verdict HARD jab) — RP2 IS crouch. BOTH are ALSO
row-changed on current main (see §2), so their steps suspend on drift
before any stance question is reached; stale rows documented, never wired.

## 1. Universe (derived FIRST, measured from the file)

117 canonicals (103 pure + 14 chord-involved); ALL 117 planned, 0 CSV-only;
186 CSV rows (117 canonicals + 69 variants); 186 plan keys.
Contexts: standing 53, crouch 32, ws 20, jump 12.
Provenance: 92 in main moves, 25 quarantined-only (live when #988 merges),
0 in 1096 only.

Input-~ canonicals in Batch 1 scope: ZERO — phantom is inert on this axis,
like Pantera/burger/kinpo. The file's old-vs-corrected canonicalization
diffs are all OUTSIDE Batch 1 scope: `3~4,U` (rest key: buttonless U
step), `4,4,2,2,1,~1` and `4,4,2,2,NSS.1,~1` (triples, union {1,2,4} →
Batch 4 scope) — all filed as their own keys for later batches, never
variants. __main canonicals in scope: 0. Corrupted keys in scope: 0 (no
diablo-style escaped-colon key). Throw/grapple variants: 0 (variant move
classes include 'special' for ~t3.yoshimitsu source-variant twins —
planned, inheriting canonical steps).

Spelling quirks kept (distinct canonicals, verified as pairs): d/f+1,2 vs
df+1,2; f+2,d/b+2 vs f+2,db+2; u/f+1,1 vs uf+1,1; WS.1,1 vs ws1,1;
WS.1,1,1 vs ws1,1,1; WS.1,1,1,1 vs ws1,1,1,1; WS.1,2 vs ws1,2; WS.2,1 vs
ws2,1 (both ws spellings are ws context after the ws2 fix). Trailing-`*`
hold markers (e.g. KIN.2,1+2*) canonicalize to their base key and file as
twins.

## 2. Drift census (1096 vs current main, BOTH ways)

All 1019 keys: same 670 / damage-only 218 / anim_ref-changed 126 /
ROW-CHANGED 5. Damage differs on 281 moves (all-status) vs 218
damage-only — both true under their definitions; the 63 gap = damage
differs AND row/anim_ref also changed. Damage-only drift does NOT suspend.
Main move 1 damage 11→9, move 2 damage 2→13.

ROW-CHANGED 5 (all five suspend-or-noted, never wired on stale data):
1: 62→None, 1_r62: 62→None, 2: 307→None, 4: 243→None,
u+1,1~t3.yoshimitsu.2: 62→None (i.e. 62→None ×3, 307→None ×1, 243→None ×1).
Batch 1 step prefixes hit: 1 (6 steps) and 2 (4 steps). The other
row-changed moves (4, 1_r62, u+1,1~t3.yoshimitsu.2) are NOT Batch 1 step
prefixes.

## 3. Step table

346 steps, all planned, 0 CSV-only: 22 verified / 20 review / 304
unmapped (10 suspended-drift + 6 rejected-candidate + 288 no-candidate).
Canonical status: 7 verified-all / 17 partial / 93 unmapped-all /
0 review-only. Plan-key last-step: 141 unmapped / 23 review / 22 verified.

Verified-all (7): d/f+1,1 [223,224], d/f+1,1,1 [223,224,225],
d/f+1,1,1,1 [223,224,225,226], u/b+1,1 [55,58], u/b+1,2 [55,71],
u/f+1,1 [66,57], u/f+1,2 [66,70].

All verified steps (22, all gate-verified own/recorded-path rows, T3
FALLBACK): d/f+1 family 10 steps (rows 223/224/225/226 — all GATE-NOTE:
standing rows verified for crouch-context steps, demonio Batch 1 / diablo
Batch 1 precedent, re-adjudicate if the gate tightens); f+2,d/b+2 step 2
row 175; jump lasts, SOFT waived (Batch 1 precedent): u+1,1 step 2 row 56,
u+1,2 step 2 row 69, u/b+1+2,1+2 step 1 row 261, u/b+1,1 [55,58], u/b+1,2
[55,71], u/f+1,1 [66,57], u/f+1,2 [66,70].

Verified rows (14 distinct, all present in current main yoshimitsu pack):
223, 224, 225, 226, 175, 55, 56, 57, 58, 66, 69, 70, 71, 261.
Profiles: 223 [14,15,68,535,0,1] standing armL m; 224/225 [18,18,48,1042,0,1]
standing armL h; 226 [25,27,57,535,0,1] standing armL m; 175
[14,14,16,535,0,2] standing armR m; 55/66 [18,18,52,535,0,1] jump armL m;
56/57/58 [11,12,39,535,0,1] starts-airborne armL m; 69/70/71
[11,13,53,535,0,2] starts-airborne armR m; 261 [113,114,134,1543,0,3] jump
chord (LP1+RP2) level u.

## 4. Every wired fill (verified only)

Batch 1 wires ZERO Job 3 fills. All 22 verified steps are gate-verified
own/recorded-path rows (§3) — no fill was needed, and no fill was wired
on anything less than the stricter rule. The two exact+FULL Job 3 row 160
candidates (1,1 step 2; 2,1 step 2) are HELD at review under the stricter
fill rule (SOFT proxy fail, window [4.0,8.5], armL peak 2) — see §5.
No agreement note fires: the note fires ONLY for actually-wired gate
candidates, and no exact+FULL Job 3 candidate exists for any verified step.

## 5. Rejected / suspended / held candidates (every one)

Review holds (20 steps, row null, NOT wired):
- 1+2,2 step 2 row 292 SOFT fail (window [5.5,10.5], armR peak 1);
  1+2,2,1 steps 2–3 rows 292/293 SOFT fail.
- 1,1 step 2 + 2,1 step 2: no gate candidate, Job 3 exact+FULL row 160
  HELD at review under the stricter fill rule (SOFT fail, window
  [4.0,8.5], armL peak 2). Also documented, NOT wired: Job 3 row 157
  (exact, ROW-ONLY) and row 299 (soft-filed, FULL) for both.
- d/b+2 family STANCE-SOFT crouch rows 231/232/233/234 for standing steps
  (10 steps across 1,d/b+2 and its longer chains).
- 2,2 step 2 + 2,2,1+2 step 2 row 308 STANCE-SOFT crouch for standing.
- d/b+1,1 step 1 row 156 SOFT fail (window [10.0,15.5], armL peak 9).
- d/f+1,2 step 2 + df+1,2 step 2 row 244 SOFT fail (window [10.5,15.0],
  armR peak 34).

Rejected-candidate (6 steps, row null):
- b+1 family step 1 row 286 ground row (downed-foe row) for standing steps
  — 5 strings (b+1,1 through b+1,1,1,1,1,1). Job 3 candidates for b+1
  (rows 154/157/160/162/237/299, all ROW-ONLY) NOT wired.
- u/f+1+2,b+1 step 2 row 262 button 0 ≠ step bits 1.

Suspended-drift (10 steps, row null, never wired):
- Prefix 1 (6 steps: 1,1; 1,NSS.1; 1,d/b+2 and its 3 longer chains' step
  1s — stale row 62, prefix-move).
- Prefix 2 (4 steps: 2,1; 2,2 (recorded-path row 307); 2,2,1+2; 2,NSS.1 —
  stale row 307).
- The other row-changed moves (4, 1_r62, u+1,1~t3.yoshimitsu.2) are NOT
  Batch 1 step prefixes.

No-candidate (288 steps): recorded path + prefix move both absent, or
prefix move present with no gate-passing row. Dominated by the long
WS./ws, BT., KIN., NSS., D/B+2, db+2, df+1,2, f+2,D/B+2, d+2,2, b+2
families. Correct clips come from #988 Step 2 (original T8 refs) or
future extraction — never from a T3 row recorded as correct.

## 6. Job 4 (CORRECTED join only)

BANK_DIR = yoshimitsu. 2 joins, none promoting:
- Row 261 on u/b+1+2,1+2 step u/b+1+2 — no action, step already verified.
- Row 262 for u/f+1+2,b+1 step b+1 — REJECTED button 0.
Orphans: 0 — all 47 yoshimitsu Job 4 candidates are carried by some
phantom Job 2 move.

Job 3: 49 report entries, 0 fills wired. Dedupe fires zero times: the
only Batch 1-relevant __main Job 3 target (u+1) has an EMPTY pass-all
list; the one non-empty __main target (d+1+2__main pass-all [137,139,158])
is not a Batch 1 step prefix; other __main targets (f+4, d/f+3) have empty
pass-all lists. All other Job 3 candidates are ROW-ONLY or soft,
documented never wired.

## 7. Pipeline notes specific to this lane

- Donor retirement is DESIGNED: wiring plans replaces single-row
  resolution wholesale, even for CLEAN donors, because one row cannot be
  correct for a multi-hit string. (E.g. 1,1~t3.yoshimitsu's own row 278,
  ground stance, is retired as a string resolution — the plan carries the
  per-step rows, and step 1 is suspended-drift on the canonical's stale
  row 62 regardless.)
- Row dual-role caution (Pantera Batch 4): a row verified for one
  string/context is NOT globally verified — every step gate-checks its own
  row again. Row 55/66/261's jump-context verification does not license
  them for ground steps.
- GATE-NOTE steps (d/f+1 family): standing rows verified for
  crouch-context steps follow the demonio Batch 1 / diablo Batch 1 /
  kinpo Batch 1 precedent — the gate flags crouch rows for non-crouch
  steps, not standing rows for crouch steps. Re-adjudicate if the gate is
  ever tightened.
- Jump-context SOFT waiver (Batch 1 precedent) applies to the u+1, u/b+1,
  u/f+1, u/b+1+2 families only; it is recorded per step, not inherited.
- Tests: minimal-tree node --test 12/12 pass; node --check fighter.js OK.
  Full 200-test suite comparison NOT run — no full current-main checkout
  on this box; CI must cover before merge (stated as a limitation in the
  PR body).
- NO play verification is claimed — tests + file evidence only; playing
  is the parent's step after merge + deploy.

## 8. Play-verify checklist (parent browser delegation, AFTER #1096 + this PR merge + deploy + sync, phone portrait)

- d/f+1,1 [223,224], d/f+1,1,1 [223,224,225], d/f+1,1,1,1 [223,224,225,226]
  — crouch context, standing rows (GATE-NOTE), grounded.
- u/b+1,1 [55,58], u/b+1,2 [55,71], u/f+1,1 [66,57], u/f+1,2 [66,70] —
  jump context, airborne rows correct here.
- u+1,1 step 2 row 56, u+1,2 step 2 row 69 — jump context, first step NO row.
- f+2,d/b+2 step 2 row 175, first step NO row.
- 1,1 / 1,NSS.1 / 1,d/b+2 family step 1s NO row (stale row 62 must NOT play).
- 2,1 / 2,2 / 2,2,1+2 / 2,NSS.1 step 1s NO row (stale row 307 must NOT play).
- 1,1 step 2 + 2,1 step 2 NO row (Job 3 row 160 held, must NOT play).
- b+1 family NO row any step (ground row 286 must NOT play).
- u/f+1+2,b+1 NO row any step (row 262 must NOT play).
- d/b+2 family + 2,2 step 2 NO row (crouch rows 231/232/233/234/308 held
  for standing steps).
- d/f+1,2 + df+1,2 step 2 NO row (row 244 held).
- No step plays rows 35/220 (they do not exist in this bank).
- No step plays a row from another bank.
- Quarantined-only strings behave per plan ONLY after #988 merges
  (Batch 1 has 25 quarantined-only canonicals).
