# Pantera Batch 1 — step plans (LP1/RP2-only strings) — 2026-10-24

Button law: LP1 = Left Punch = Tekken 1, RP2 = Right Punch = Tekken 2, LK3 = Left Kick = Tekken 3, RK4 = Right Kick = Tekken 4.

## What this is

The engine change in this PR (`game/js/fighter.js` `_attackClipPlan` step-plan branch + `_stepChain`) plus the
`string_step_plans` data in `game/assets/movesets/pantera.json`. A planned string move plays per-STEP rows, never one
row for the whole string. Only a step with status `verified` plays its row. A `review`/`unmapped` step plays NO bank
row — the existing procedural fallback in `_animate` — and is flagged in `_atkPlan.unmapped` with a `[WH-STEP-PLAN]`
console line. Donor, match, and generic tiers are bypassed for planned strings, so a planned string can never
silently donor-fall-back. This is the faster-methods prime candidate (step-based string playback) as REFRAMED by
the batch-research second validation: the per-press (`_pressV2`) path already fires one move per press, so for that
path the plan corrects the LAST step's row selection; the whole-string path (a full notation fired at once by AI /
trials / movelist demo / buffered input) plays as a `_stepChain` of prefix moves through `_fireNotation`.
No blend is added: step-to-step pose continuity is UNPROVEN (end-to-start gaps 0.2-0.9 m+ in the research), and a
blend ships only if play shows a snap.

## Gates (per step candidate, in order)

1. Candidate source: recorded path row (`strings[].t3_rows` full-path, or dest-only for the last step), else the
   prefix move's `t3_row`, else none. Recorded paths are NOT trusted blindly: `2,1`'s recorded path `[203, 220]`
   fails the gates at step 2, so the path is recorded as evidence and the step is UNMAPPED, not wired.
2. HARD gates (fail = `unmapped`): button bitmask (`hit_frames.json` button field == step chord bits, LP1=1, RP2=2) +
   throw flag == 0 + stance (an airborne row fails a standing-context string; airborne PASSES a jumping-context string).
3. SOFT gate (fail = `review`, not played): in-window limb extension peak (FK, npz window = stream active window / 2,
   +/-2 frames). The stream-to-npz decimation is UNCONFIRMED, so this gate never hard-fails a step. For
   jumping-context strings it is WAIVED: the FK extension metric is systematically silent on jumping rows 38/39/40
   (zero limb peaks at threshold), while button + stance pass and the focus Stage 1 resolution (row 38 = Pantera
   jumping `u+1,1`, row 39 = `u/f+1,1`, row 40 = `u/b+1,1`) stands. Play-verify remains the check for those rows.
4. Rejected for ground steps, always: jumping rows 35 and 220. Row 220 is a shared LP1+RP2 chord/jump-family clip
   (byte-identical to row 221, also serves `1+2~t3.king`), not a `2,1` ender. Row 35 is the same failure class for chord enders.
5. Shared-clip note: rows 97 = 110 and 220 = 221 are byte-identical (quats + root_t). FK cannot distinguish shared-clip
   context variants; shared verified rows still need play-verify.

## Canonical step table (31 triage keys, 73 steps: 27 verified, 7 review, 39 unmapped)

| String | Steps (verified row, else status) | String status |
|---|---|---|
| `1+2,1` | 1+2 = UNMAPPED (no candidate) \| 1 = UNMAPPED (no candidate) | unmapped-all |
| `1,1` | 1 = row 110 \| 1 = UNMAPPED (cand row 584 rejected: button 0 != step bits 1; throw flag 1 (row 584); no in-window peak on ['armL'] in approx npz window [0,2] (peaks {'armL': [83], 'armR': [4, 77, 85], 'legL': [], 'legR': []})) | partial |
| `1,2` | 1 = row 110 \| 2 = UNMAPPED (no candidate) | partial |
| `1,2,1` | 1 = row 110 \| 2 = UNMAPPED (no candidate) \| 1 = UNMAPPED (no candidate) | partial |
| `2,1` | 2 = row 203 \| 1 = UNMAPPED (cand row 220 rejected: button 3 != step bits 1; airborne (y0 0.952 ymax 1.649 vs standingY 0.892)) | partial |
| `FC.1,2` | 1 = row 110 \| 2 = UNMAPPED (no candidate) | partial |
| `WS.2,2` | WS.2 = UNMAPPED (no candidate) \| 2 = UNMAPPED (no candidate) | unmapped-all |
| `b+1+2,1+2` | b+1+2 = UNMAPPED (cand row 279 rejected: throw flag 1 (row 279)) \| 1+2 = UNMAPPED (no candidate) | unmapped-all |
| `b+1+2,2` | b+1+2 = UNMAPPED (cand row 279 rejected: throw flag 1 (row 279)) \| 2 = row 98 | partial |
| `b+1,2` | b+1 = UNMAPPED (no candidate) \| 2 = UNMAPPED (no candidate) | unmapped-all |
| `b+2,1` | b+2 = UNMAPPED (no candidate) \| 1 = UNMAPPED (no candidate) | unmapped-all |
| `b+2,1+2` | b+2 = UNMAPPED (no candidate) \| 1+2 = UNMAPPED (no candidate) | unmapped-all |
| `d+1+2,2` | d+1+2 = row 97 \| 2 = row 98 | verified-all |
| `d+1+2,2,1` | d+1+2 = row 97 \| 2 = row 98 \| 1 = row 198 | verified-all |
| `d+1+2,2,1,1` | d+1+2 = row 97 \| 2 = row 98 \| 1 = row 198 \| 1 = REVIEW cand row 257 (recorded-dest) | partial |
| `d+1+2,2,1,1,2` | d+1+2 = row 97 \| 2 = row 98 \| 1 = row 198 \| 1 = REVIEW cand row 257 (prefix-move) \| 2 = REVIEW cand row 258 (recorded-dest) | partial |
| `d+1,2` | d+1 = UNMAPPED (no candidate) \| 2 = UNMAPPED (no candidate) | unmapped-all |
| `d/b+1+2,2` | d/b+1+2 = UNMAPPED (cand row 286 rejected: throw flag 1 (row 286)) \| 2 = row 200 | partial |
| `d/f+1,2` | d/f+1 = REVIEW cand row 117 (prefix-move) \| 2 = UNMAPPED (no candidate) | review-only |
| `d/f+2,1` | d/f+2 = row 202 \| 1 = UNMAPPED (no candidate) | partial |
| `f+2,1` | f+2 = UNMAPPED (no candidate) \| 1 = UNMAPPED (no candidate) | unmapped-all |
| `f+2,1,1` | f+2 = UNMAPPED (no candidate) \| 1 = UNMAPPED (no candidate) \| 1 = REVIEW cand row 257 (prefix-move) | review-only |
| `f+2,1,1,2` | f+2 = UNMAPPED (no candidate) \| 1 = UNMAPPED (no candidate) \| 1 = REVIEW cand row 257 (prefix-move) \| 2 = REVIEW cand row 258 (prefix-move) | review-only |
| `f+2,d+1` | f+2 = UNMAPPED (no candidate) \| d+1 = UNMAPPED (no candidate) | unmapped-all |
| `f+2,d+1,2` | f+2 = UNMAPPED (no candidate) \| d+1 = UNMAPPED (no candidate) \| 2 = UNMAPPED (no candidate) | unmapped-all |
| `u+1,1` | u+1 = UNMAPPED (no candidate) \| 1 = row 38 | partial |
| `u+1,2` | u+1 = UNMAPPED (no candidate) \| 2 = row 50 | partial |
| `u/b+1,1` | u/b+1 = UNMAPPED (cand row 37 rejected: button 3 != step bits 1) \| 1 = row 40 | partial |
| `u/b+1,2` | u/b+1 = UNMAPPED (cand row 37 rejected: button 3 != step bits 1) \| 2 = row 52 | partial |
| `u/f+1,1` | u/f+1 = row 36 \| 1 = row 39 | verified-all |
| `u/f+1,2` | u/f+1 = row 36 \| 2 = row 51 | verified-all |

## Plan keys in the moveset (60)

- 31 canonical triage keys (table above).
- 26 twin keys (`~t7.king` / `~t8.king` / `~t3.king` variants sharing a canonical input): same steps as their canonical
  key, except `f+2,1~t3.king`, whose own `t3_row` 198 passes all gates for its last LP1 step and is therefore its
  verified last-step row (its `move_class` is `strike`, so the chain branch does not fire for it — the clip branch does).
- 3 spelling-variant keys (`df+1,2`, `df+2,1`, `ws2,2`): same steps/evidence as `d/f+1,2`, `d/f+2,1`, `WS.2,2`.
- EXCLUDED: `b+1+2,1+2~t7.king` — its `move_class` is `throw`, so a punch-string plan must not govern its clip
  selection; it stays on the existing tiers.
- Last-step status over the 60 plan keys: verified 11, review 4, unmapped 45. The 11 verified-last-step keys are:
  `b+1+2,2` (row 98), `d+1+2,2` (98), `d+1+2,2,1` (198), `d/b+1+2,2` (200), `f+2,1~t3.king` (198), `u+1,1` (38),
  `u+1,2` (50), `u/b+1,1` (40), `u/b+1,2` (52), `u/f+1,1` (39), `u/f+1,2` (51). For these 11, the verified row equals
  the move's previous own `t3_row` — the visible clip does not change, but it is now plan-guaranteed (donor tier bypassed).
- Last-step review keys (4): `d+1+2,2,1,1` (cand 257), `d+1+2,2,1,1,2` (cand 258), `f+2,1,1` (cand 257), `f+2,1,1,2`
  (cand 258) — limb-peak evidence short (257: armR-dominant FK vs LP1 button; 258: armR peak 1 frame outside the
  approximate window). These rows are NOT played until adjudication + play-verify promote them.
- Flagship: `2,1` — step 1 row 203 verified (RP2, standing, single peak); step 2 UNMAPPED (recorded row 220 fails button
  bitmask 3 != LP1 bits 1 AND airborne for a standing string). All `2,1` twins share the plan, so row 220 no longer
  plays for any `2,1` key. The true LP1-context ender row is still UNMAPPED pending `match_search` candidates or MADE.
- `1,2` boundary (honest): step 1 row 110 verified; step 2 UNMAPPED pending candidates. Its move damage 20 is the
  multi-hit total [5, 15]; last-hit normalisation (15) is NOT applied in this PR because no step is wired for it yet —
  it applies when step 2 lands. `2,1` damage is untouched (Stage 1 damage ruling pending: body 9 vs 15 vs 16).

## Damage/startup spot-check (criterion 4, wired scope only)

For the 11 verified-last-step keys, the moves already carry last-step damage/startup — no data change needed:
`d+1+2,2` startup 0.200 = row 98 active-first 12/60, damage 9 = row damage 15 scaled 100/170; `d+1+2,2,1` startup 0.400 =
row 198 active-first 24/60, damage 6 = 10 scaled; `b+1+2,2` startup 0.200 = row 98 12/60; `d/b+1+2,2` startup 0.250 =
row 200 15/60; `u+1,2` / `u/b+1,2` / `u/f+1,2` startup 0.183 = rows 50/52/51 active-first 11/60. Other verified-last-step
keys carry single-hit-scale damage (9/11) consistent with last-step, not totals.

## Re-audit (planned keys only; NOT a play claim)

Baseline (faster-methods CSV, 57 audit rows): donor 42, notation 6, own 5, anim 4; 14 limb mismatches, 14 HARD-flagged;
generic rows 99 (14 strings) and 110 (11) dominate; worst repeats: `2,1` enders on jumping row 220, `1+2` enders on jumping row 35.
After this PR, over the 47 CSV rows whose key is a plan key: 2 rows play a verified row (the canonical `d+1+2,2` /
`d+1+2,2,1` keys — their clips are unchanged); 45 rows play NO bank row (procedural fallback) instead of their previous
donor/notation/own row, including all 4 `2,1` rows (row 220 gone) and the planned chord-ender rows that played row 35.
The other 10 CSV rows are grapple chains (7: ARM_BREAKER / DOUBLE_HEEL_HOLD / PILE_DRIVER / REVERSE_ARM_SLAM /
REVERSE_SPECIAL_STRETCH_BOMB / SLEEPER) and TACKLE chains (3) — separate grapple systems, out of Batch 1 scope, untouched.
Donor picks are therefore 0 for planned strings BY CONSTRUCTION (the plan branch bypasses the donor tier); the 45
no-bank-row strings are the honest UNMAPPED/REVIEW remainder, not fixes. No string in this PR is claimed fixed by
inspection: the play handoff below is the remaining gate.

## Three counting units, reconciled (none is 'the' count)

| Unit | Count | What it counts |
|---|---|---|
| Faster-methods CSV worklist | 57 rows | Actually-played clip per Pantera LP1/RP2 move key, counting key variants/twins (40 pure + 17 chord-involved, incl. grapple chains) |
| Batch-research triage | 31 keys, 73 steps | Canonical LP1/RP2-only multi-step keys (every step LP1/RP2/chord after stripping stance/direction prefixes) in the payload moveset |
| Focus Stage 1 strings-list audit | 81 entries, Batch 1 = 19 | Strings-list entries (fired full-input move per entry): 19 Batch-1 entries = 14 T8-fired + 1 T7-only + 4 single-row wired |

Mapping: all 19 focus Batch-1 entries are in the 31 triage keys (after spelling normalisation `df+` -> `d/f+`, `ws2` ->
`WS.`). The 12 triage keys outside focus Batch 1 are `1,1`, `b+1+2,1+2`, `b+1+2,2`, `d/b+1+2,2`, `f+2,1,1`, `f+2,1,1,2`,
and the 6 jumping strings (`u+1,1`, `u+1,2`, `u/b+1,1`, `u/b+1,2`, `u/f+1,1`, `u/f+1,2`) — the focus audit counts fired
strings-list entries, the triage counts canonical keys, and the CSV counts played move keys incl. twins. The 60 plan
keys = 31 canonical + 26 twins + 3 spelling variants (throw twin excluded).

## Switch-criteria checklist (batch-research gate, applied to this PR)

1. T3 source branch JSONs re-pulled — FAIL. No `teardown/tekken3/` directory exists in the private
   game-reverse-engineering repo (its `teardown/` holds firepro, gang-beasts, pakchunk0, tekken7-steam, tkdata,
   wrestling-empire, wwe2k19, yakuza-kiwami only), and the workspace copy (`batch8wt/teardown/tekken3/movesets/`)
   holds only bosconovitch/gunjack/ogre/xiaoyu — no King branch JSON. Step derivations therefore use recorded
   `strings[].t3_rows` + prefix-move rows + gates, with the derivation recorded per step; branch-path re-derivation
   remains open work, NOT claimed.
2. `step_check.py` reproduces PASS 8 / REVIEW 8 / NO-ROW 15 — PASS (re-run this turn on the research inputs: stderr
   `PASS 8 / REVIEW 8 / NO-ROW 15 of 31`). All 31 triage keys are present in fresh-main `pantera.json` moves, and the
   recorded `strings[]` paths match the payload (e.g. `2,1` -> [203, 220], `d+1+2,2` -> [98]).
3. Job-2 `match_search` candidates landed — NOT LANDED (no `match_search` output in the workspace). This PR is
   therefore explicitly scoped to VERIFIED steps only (criterion 3's alternative): NO-ROW/review steps are UNMAPPED,
   never pooled. When job-2 candidates land, they enter as candidates through these same gates, not as assignments.
4. Damage/startup last-hit normalisation implemented + spot-checked — SPOT-CHECKED for the wired scope (above); no
   data change needed for the 11 verified-last-step keys. Unwired strings keep their existing damage (incl. `1,2`'s
   total 20) until their steps land.
5. Play-verification protocol agreed — HANDOFF ISSUED (below + parent report). No 'fixed' claim until the user plays it.
Additional unproven item: pose continuity is UNPROVEN — no blend added; the handoff includes a snap check, and a blend
is added only if play shows a snap.

## Kinmot decode status (step 1 of the 6-step plan)

- File located in the workspace (NOT assumed): `batch-motbin/batch-bin/kinmot.bin`, 2,551,112 bytes,
  SHA-256 `48f9c91fcdbd0519d1ece97ff827001fe1a3155a6dd775d203be93b42952c729`. Already decoded by the parallel
  batch-motbin lane (`batch-motbin/json/kinmot.json`, private-repo PR #63, WH wiring PR #1048 — both still open at
  this PR's base): 2,787 moves, 11,879 cancels counted from move lists (meta count 11,862 — a 17-cancel discrepancy
  between the meta header count and the summed move cancel lists, recorded here, not resolved). Direct 8,627 /
  aliased (>= 0x8000) 3,252 / single-button direct edges 1,493. Aliased cancels use only 20 distinct slots (slot 1 alone:
  2,350) — the '56-entry aliases table' from the research brief is NOT recovered: the converter emits no aliases table,
  and no alias slot -> move resolution is claimed in this PR. The extended-converter job (aliases + MOTA durations)
  is therefore PARTIAL: the decode exists, the extension does not. `anim_len` reads 0 for all sampled raw moves, so
  MOTA durations/bytes remain UNMAPPED (the parallel script's `anim_len` length test is VOID — not used as evidence anywhere here).
- Requirement semantics (codes 636/811/80/81/72/217) remain UNMAPPED; gated T7 cancel edges are not used as string steps.
- King cancel-graph counts differ from the research report's re-derived frv/dnc counts because those are different
  fighters (Raven/Chloe): frv 11,590 cancels (report) vs the earlier record 11,573, dnc 10,051 vs 10,034 — the report's
  re-derived counts are used for frv/dnc; neither is King's graph. King's own step chains are NOT wired in this PR:
  T7 wiring waits on clip bytes + requirement resolution (see PROCEDURAL_AUDIT entry).

## Paths (both step mechanisms, stated per string)

- Per-press path (`_pressV2` -> `tryAttack` -> `_fireNotation` per press): every planned string. The final press fires
  the string move; `_attackClipPlan`'s step-plan branch selects its last step's verified row, or no bank row when the
  last step is review/unmapped. Earlier presses already played their own prefix moves' rows (or their own plans).
- Whole-string path (`_tryAttackFresh` full-notation fire -> `_stepChain` -> `_fireNotation` per prefix): only planned
  string moves whose EVERY prefix is a real move (checked at fire time). Jumping strings have no standalone `u+1` /
  `u/b+1` move, so they never chain — they fire normally and the clip branch governs. `f+2,1~t3.king` (`strike`) never
  chains (chain branch requires `move_class` `string`); its clip branch governs.
- Blend: none in this PR (see above).

## Play handoff (parent browser lane — NOT done by this lane, no live browser here)

Netlify https://endearing-scone-b3d816.netlify.app/ (after this PR merges AND the main -> gh-pages deploy sync runs —
note: the gh-pages sync is separately BLOCKED on the #988 moveset conflict per the complaints-tracker synthesis; do NOT
run a blind full sync, and do NOT use the sync-except-56 workaround without an owner decision). Phone portrait, human
simulation (screenshot, look, scroll, THEN tap; touch taps like the user plays). Menu -> select Pantera -> stage -> FIGHT, then:
1. `1,2` (LP1,RP2): step 1 plays the LP1 jab row 110; step 2 plays NO bank row (procedural) — confirm step 2 is NOT the old donor row 99 and NOT a jump clip.
2. `b+2,1+2` (back + RP2, then LP1+RP2): confirm the ender is NOT the old jumping row 35 (feet stay grounded).
3. `FC.1,2` (crouch + LP1,RP2): confirm step 1 is not an airborne row and step 2 is not donor row 99.
4. `WS.2,2` (while-standing RP2,RP2): confirm neither step plays donor row 99.
5. `2,1` (RP2,LP1) + all its twins: confirm the LP1 ender is NOT jumping row 220 (feet grounded, single LP1 arm) — expect procedural on the ender until its row lands; step 1 must read as RP2 row 203 context.
6. Verified controls (must still play their rows): `d+1+2,2` (rows 97 -> 98), `d+1+2,2,1` (97 -> 98 -> 198), `u+1,1` (jumping row 38).
7. Snap check: on every multi-step string above, record whether the cut between steps visibly snaps. A snap does NOT fail the string — it queues the blend work. A wrong row DOES fail it.
8. Regression: no step silently donor-falls-back — any planned string playing rows 99/110/35/220 other than the verified controls above is a FAIL to report back, not a pass.
Until this pass completes, Batch 1 is wired + re-audited, NOT play-verified, and nothing in it is 'fixed'.

## Still UNMAPPED (after this PR)

- King cancel graph as wired steps (decode exists; aliases + requirements unresolved; clip bytes unresolved).
- Aliases table (converter emits none; 20 distinct King alias slots observed, slot 1 dominant).
- MOTA clip durations/bytes (`anim_len` = 0 everywhere).
- Requirement semantics (636/811/80/81/72/217).
- Kaggle job 1-6 outputs (pending; cross-checks when they land — lane does not wait).
- TKMovesets2 access (PC + running T7; unavailable from the VM).
- Review steps (canonical: rows 257/258/117 cases) pending adjudication + play-verify.
- All HARD moves beyond Batch 1's scope (LK3/RK4 Batch 2, mixed pairs, rest) — same pipeline, later PRs.
- Grapple-chain + TACKLE CSV rows (10) — separate grapple systems, not Batch 1.


## 2026-10-29 update — real-moves correctness lane (supersedes PR #1096)

Owner ruling (2026-10-29): "Get the real moves and animations and rows and combo strings and correct the
incorrect animations." Neither earlier option is the end state — unmapped steps are filled with verified
real rows where they exist; steps with no real row anywhere stay UNMAPPED and are reported by name.

- Switch-criteria item 1 is now CLOSED: the T3 King branch graph exists in the repos — GRE
  `tekken3/movesets/moveset_king.json` (bank `divmot03_king.bin`, 652 moves, `branches[]` + 4,023-entry
  `move_index`), same extraction as this repo's `teardown/tekken3/movesets/`. It reproduces every
  already-verified Batch 1 chain link exactly (97→98, 98→198, 110 jab, 203 RP).
- All 98 unmapped/review step occurrences were researched against it (plus hit_frames HARD gates and
  same-notation `~t3.king`/`~t7.king` records): 57 occurrences have a real row (HARD gates pass) and are
  now recorded as REVIEW candidates with `candidate_source: t3-branch-graph` — they play only after the
  FK soft gate + play-verify promote them to verified. 41 occurrences have no real row in any searched
  source and stay UNMAPPED (named in `docs/movesets/REAL-MOVES-AUDIT-2026-10-29.md`).
- Last-step status over the 60 keys is now: verified 11 / review 25 / unmapped 24 (was 11 / 4 / 45).
  The 11 verified keys are unchanged; no new step was promoted to verified in this pass.
- `2,1` step 2 stays UNMAPPED: the branch graph proves row 220 IS T3's real LP follow-up from row 203,
  and it still fails the HARD gates (button 3 != LP1 bits 1; airborne) — real but not playable for a
  standing string step under the standing law.
- This doc's historical "NOT LANDED" checklist text above describes PR #1096 as opened in 2026-10-24;
  the step plans land via the 2026-10-29 real-moves PR that carries this update. Still NOT play-verified.
