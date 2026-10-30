# Zui Batch 1 step plans (LP1/RP2-only strings, 2026-10-25)

Stack: #1096 engine → zui B1 → B2 → B3 → B4. Branch from #1096's head, re-verified before branching: `e2ae41432a` (unchanged from inventory time). Merges AFTER #1096 (itself blocked on pre-existing failures / a gate decision — this lane does not fix those and does not merge on mergeable:true alone). This PR merges nothing itself. It does not touch `fighter.js`, `pantera.json`, `burger.json`, `demonio.json`, `diablo.json`, `kinpo.json`, `phantom.json`, `scimitar.json`, `skull.json`, or `torch.json`.

## Scope and universe (measured, not assumed)

- Scope: zui strings whose steps are ALL buttoned and whose button union is exactly {LP1, RP2} (any directionals, any contexts: standing/crouch/jump/ws). Pure single-button strings first, then chord-involved strings (chords containing only LP1/RP2 buttons).
- Measured universe: **175 canonicals** — exactly the inventory estimate (293 total canonicals; B1 estimate 175), derived fresh from current main, not assumed. 136 pure single-button + 39 chord-involved. Contexts: standing 146, crouch 26, ws 3, jump 0 (zui has no jump-context LP1/RP2 string in Batch 1 scope — unlike torch's 7).
- Plan keys: **194** = 175 canonicals + 19 variants. All 19 variants are `~t8.steve` twins (T8 Steve source records) of string-class canonicals; every variant inherits its canonical's steps verbatim (Batch 1 twin precedent) plus `twin_of` + `twin_move_class`.
- CSV-only canonicals: **0**. Every Batch 1 canonical is planned (move_class: string 174 + special 1). The `(During Tackle) 1/2` family (3 keys) carries move_class `string`, not throw/grapple, and is planned like any other string; all its steps are unmapped (no candidate rows). No throw/grapple canonical exists in zui LP1/RP2 scope, so no CSV-only exclusion arises here.
- Sources: 113 canonicals from moves (both #1096 and main) only; 62 from moves + strings-list. 0 strings-list-only canonicals. All 175 canonicals exist in both #1096 and main moves.
- Strings list: 87 entries, 29 carry `t3_rows`. Only 6 of those 29 are Batch 1 strings with recorded rows (f+2,1; d+1+2,1; d+1+2,2; f+2,1,2; d+1+2,1,2; f+2,1,2,2) — the rest of the recorded-row strings are kick/mixed strings outside Batch 1 scope. The other Batch 1 strings-list entries carry `t3_rows: null`.

## Resolved bank (four-way evidence)

1. **zui.json file level, BOTH #1096 and main:** `t3_source: jin`, `t3_bank: moveset_jin.json`, `anim_bank: null` (absent as a value, not a different bank).
2. **Per-move:** t3_source jin 152 / none 502 on BOTH files, identical. All 152 t3_row moves carry t3_source jin (0 row-without-source). Distinct t3_source values file-wide: {None, jin} only — no second bank exists in the file.
3. **t3/ directory (main):** `game/assets/anim/t3/jin/` carries hit_frames.json + rows.pack.json + skeleton.json (+ reactions.pack.json and the locomotion set). Pack dir = bank name (jin), no alias split.
4. **Job 1:** jin 220 rows of 277 hit_frames rows (stances: standing 115, jump 43, starts-airborne 30, duck-dip 16, crouch 10, ground 6). Job 2 zui entries: **0** (of 5445) — that check is vacuous for zui, stated honestly, not claimed as coverage. Job 3 zui entries: 0 (of 2315). job3.log zui lines: 0. Job 4 jin bank-level candidates: 47 (unjoinable without Job 2 zui entries).
- **Bound bank = jin.** Zui has NO FIGHTER_BANK override in fighter.js #1096 (the override list names torch→anna and others, never zui), so the engine's `bankIdFor` falls back to `anim_bank || t3_source` = jin. There is NO bank-blocked category for zui (that was torch's dual-bank variant only): jin gate-verified steps wire directly as playable.

## Jin row identities (freshly derived for zui, never copied)

- **Row 35 EXISTS:** starts-airborne, btn 1, hf [11,12,39,535,0,1], level m, Job 1 armL peakF 6. Airborne — fails every ground step. Never wired in Batch 1 (no Batch 1 candidate is row 35).
- **Row 220 EXISTS:** standing RP2, btn 2, hf [12,12,41,1042,0,2], level h, Job 1 armR peakF 6. NOT king's jumping chord row, NOT bryan's button-0 row 220, NOT heihachi's jump RK4 row — zui's jin row 220 is a standing RP2 row. Never wired in Batch 1 (no Batch 1 candidate is row 220).
- **Row 216 EXISTS:** jump, btn 0, hf [63,64,117,1543,0,0], level u, Job 1 armR peakF 33. Fails every single-button gate. Never wired in Batch 1.
- **Row 41 EXISTS:** starts-airborne, btn 1, hf [7,7,35,535,0,1]. Airborne — fails ground steps. Never wired in Batch 1.
- Duck-dip jin rows (16): 123, 189, 192, 210, 211, 212, 213, 235, 257, 367, 377, 381, 385, 387, 389, 397. No Batch 1 candidate is a duck-dip row.

## Zui basics (verified here — DIFFER from torch, do not import torch's rows)

- LP1 move `1`: damage 7, anim_ref `t7:steve:1`, move_class strike, **no t3_row** on either file.
- RP2 move `2`: damage 12, anim_ref `t7:steve:2`, move_class strike, **no t3_row** on either file.
- LK3 move `3`: damage 0, special (Ducking Left), anim_ref `t7:steve:ducking_left`, **no t3_row**.
- RK4 move `4`: damage 0, special (Ducking Right), anim_ref `t7:steve:ducking_right`, **no t3_row**.
- Zui's basics are T7-sourced and carry no T3 row at all. Torch's basics (jin r248/r220/r195/r199) are torch's rows, not zui's — importing them would be a wrong-bank/wrong-fighter error. Consequence: the famous `1,2` / `2,1` families have NO candidate rows in this batch (their prefixes are T7/T8-sourced with no T3 row), so they are unmapped-all, honestly, not wired to any donor row.

## Re-baseline #1096 vs current main (drift census, both ways)

- Full-file census over all 654 moves: **654 same / 0 row-changed / 0 damage-only / 0 anim_ref-changed**. Damage differs on **0** moves. Damage-only drift noted, NOT suspending (damage ≠ animation) — vacuous here.
- Moves deep-equal: true. Strings deep-equal: true (87/87). Only top-level diff: main's added `t7_motbin` section (16 keys) — no move/string content changed.
- Step-prefix census: 0 row-changed moves affect Batch 1 scope → **0 suspended-drift steps**. No stale row is wired anywhere in this batch.
- Quarantine: `t8_quarantine_20261024` key ABSENT on both files — zui was never quarantined, no #988 dependency. T8 layer KEPT: mix_20261024 counts_keys t8:126 (merge_sources added t8:171 records). No T8 removals, no UNMAPPED:t7-clip-pending marker stripping.

## Gap-1 (jin bank, #1096 vs main)

- hit_frames.json: IDENTICAL (blob 54b38e635bb815db00b764cc10675a6bffb489d0 both sides).
- skeleton.json: IDENTICAL (blob 26f72eb7e31d4047596d043e832c02ee6dba83ed both sides).
- rows.pack.json: DRIFT by blob (141fbc8db374ef3031fe408ba8a597054abeb249 → 7bafa36a76ce1bc89d46ebd3c13efd0a6260f192) — but row-content comparison proves **ADDITIVE-ONLY**: all 220 b1096 rows present unchanged on main; main ADDS 6 rows (89, 112, 247, 288, 339, 357); 0 changed, 0 removed. Affected fills = 0. No Batch 1 candidate is a main-only pack row, so no MAIN-ONLY-PACK flag fires.
- Gates use hit_frames (identical) + Job 1, and every wired row is verified present in the CURRENT main jin pack at wire time (226 rows) — the game plays from the pack.

## MIX note (PR #1017, per canon — stance unchanged)

- Zui = Steve Fox T7 base + Lei Wulong drunken fist (Tekken 6 / TTT2, shared via Rave's Lei set; Rave keeps his full Lei moveset) + 2 WH-original canon moves (Bottle's Honest Truth, Beautiful Stumble). Mix counts (mix_20261024 counts_keys): steve 345, lei 40, wh 4, t3 139, t8 126, other 0.
- KEEP the hands-up drunken stagger stance — this lane changes no stance, no move, no mix entry, no stance list. The DRU stance correction (BOX → DRU metadata, entry move f+3+4, exit DRU b) is untouched. MIX is per canon authorized where canon demands, documented per move in the file's own mix_note_20261024 / mix_20261024 records.
- T7 block: 305 moves carry a `t7` key (one of the corrected 10-file T7 list). Zui was simply NOT named in the user-specified batch order — no exclusion marker exists.

## Step tallies

- 484 steps total (all planned-string steps; 0 CSV-only steps): **9 verified / 0 review / 475 unmapped** (472 no-candidate + 3 rejected-candidate + 0 suspended-drift + 0 ambiguous-bank).
- Canonical status (175 planned): **169 unmapped-all / 5 partial / 1 verified-all / 0 review-only**.
- Plan-key last-step: 6 verified / 188 unmapped (5 canonicals + 1 twin: the twin f+2,1~t8.steve inherits f+2,1's verified last step).
- Step banks: (jin, verified) 9; (jin, unmapped) 3; (None, unmapped) 472 (no candidate, bank moot).
- Job 3 fills wired: 0. Job 4 joins: 0. SOFT fills: 0. No agreement note fires (it fires ONLY for actually-wired gate candidates disagreeing with an exact+FULL Job 3 candidate, and no such candidate exists for any step). No SOFT fill inherited from #1097 (Pantera-specific, unapproved, does not transfer).
- The 0-review result is real, not a gate skip: every candidate that passed HARD gates also passed the SOFT limb-peak proxy (or the jump waiver, which fires 0 times — there are no jump-context Batch 1 strings). The 3 rejected candidates failed HARD gates (button mismatch), and the 472 no-candidate steps have no row to gate at all.

## Wired fills (verified only — T3 FALLBACK, never recorded as the correct mapping)

All 9 verified steps are jin-bank, button == step bits, throw flag 0, standing stance, Job 1 limb-peak proxy passed. Correct clips for unwired steps come from #988 Step 2 (original T8 refs) or future extraction — never from a T3 row recorded as correct.

- d+1+2,1 step 1 (d+1+2, chord LP1+RP2) ← jin row **92**: hf [10,10,39,1042,0,3], standing, level h, SOFT window [3,7], armL peak 5 / armR peak 3. GATE-NOTE: standing row verified for a crouch-context step (demonio Batch 1 / diablo Batch 1 precedent — re-adjudicate if the gate tightens).
- d+1+2,1,2 step 1 (d+1+2) ← jin row **92** (same evidence, GATE-NOTE).
- d+1+2,1,2 step 3 (RP2) ← jin row **183**: hf [13,13,60,535,0,2], standing, level m, SOFT window [4.5,8.5], armR peak 6. GATE-NOTE (standing row, crouch context).
- d+1+2,2 step 1 (d+1+2) ← jin row **92** (GATE-NOTE). Step 2 (RP2) ← jin row **93**: hf [10,10,39,1042,0,2], standing, level h, SOFT window [3,7], armR peak 3. GATE-NOTE. This is the batch's only verified-all string: d+1+2,2 = [92, 93].
- f+2,1 step 2 (LP1) ← jin row **221**: hf [14,14,43,1042,0,1], standing, level h, SOFT window [5,9], armL peak 7. SINGLE-BANK-FALLBACK (see below).
- f+2,1,2 step 3 (RP2) ← jin row **222**: hf [10,10,39,1042,0,2], standing, level h, SOFT window [3,7], armR peak 5.
- f+2,1,2,2 step 3 (RP2) ← jin row **222** (same evidence). Step 4 (RP2) ← jin row **223**: hf [17,17,60,1042,0,2], standing, level h, SOFT window [6.5,10.5], armR peak 8.
- 6 distinct wired rows (92/93/183/221/222/223), all present in the current main jin pack (226 rows). No verified step uses a jin airborne/jump row for a ground step. No verified step uses jin row 35, 220, 216, or 41. No step carries a soft flag.

### SINGLE-BANK-FALLBACK (lane decision, flagged for the coordinator — NOT hidden, NOT an owner approval)

f+2,1 step 2 (row 221) is the one step whose bank is resolved from the file-level bank rather than from a move's t3_source: neither the prefix move (f+2,1, T7-sourced, no t3_row) nor the first-step move (f+2, T8-sourced, no t3_row) carries t3_source, so the inherited prefix-else-first-step rule yields no bank. The fallback is evidence-based, not an assumption: (1) zui is verified single-bank — distinct move t3_source values file-wide are {None, jin} only; (2) ALL 35 recorded strings-list rows and ALL 152 move t3_rows exist in the jin hit_frames and in Job 1 jin profiles, so a recorded row for this fighter can only be a jin row; (3) the row is independently proven jin by the sibling variant key f+2,1_r221, which carries t3_source jin + t3_row 221 + anim_ref t3:jin:row:221 for this very string. The step then gates clean against jin (button 1 == bits 1, throw 0, standing, SOFT window [5,9] armL peak 7). The fallback is recorded in the step's reasons, so the coordinator can revert it mechanically (flip the step to unmapped, row null) if they reject it — the string f+2,1 would then be unmapped-all instead of partial, and the plan-key verified-last count would drop from 6 to 5. This is NOT a torch-style BANK-BLOCKED case: there is no second bank for the row to belong to, and the dual-bank caution (never assume the file-level bank) does not apply where the file has exactly one bank. If the coordinator prefers the strict prefix-else-first-step rule with no fallback, that is a one-step revert from evidence already in the file.

### GATE-NOTE steps (standing rows for crouch-context steps)

All 5 d+1+2-family verified steps use standing jin rows for crouch-context strings (first step d+1+2). The pipeline stance gate flags crouch rows for non-crouch steps, NOT standing rows for crouch steps (demonio Batch 1 edge) — so these verify with a GATE-NOTE, not a rejection. Re-adjudicate if the gate is ever tightened. Play-verify must confirm these read as crouch-context strikes, not standing strikes, when played.

## Rejected candidates (3, with reason)

- d+1+2,1 step 2 (LP1) and d+1+2,1,2 step 2 (LP1): candidate jin row **177** (prefix-move row for d+1+2,1; recorded-dest for d+1+2,1) — hf [15,15,44,1042,0,12], standing, but button **12 != step bits 1**. Multi-button clip rejected for a single-LP1 step under exact-equality (demonio row 177 btn-12 + scimitar row 184 btn-9 precedent — note: jin row 177 here is the same row number as demonio's rejected row 177, but the rejection is derived fresh from zui's own jin hit_frames, not copied).
- f+2,1_r221 step 2 (key step `1_r221`): candidate jin row **221** (prefix-move row) — button **1 != step bits 3**. The bits-3 reading comes from the `_r221` row-suffix digits inside the key segment (`1_r221` contains digits 1, 2, 2, 1), not from the LP1 input. This is a key-shape artifact of the standardized button rule (digits anywhere in the segment), which is also what the inventory used to count B1 = 175 — changing the rule would change the universe count, so the artifact is documented, not fixed, in this lane. The underlying LP1 step's row evidence lives on the f+2,1 canonical (see SINGLE-BANK-FALLBACK).

## No-candidate steps (472) — the expected pattern

Intermediate prefixes are T8/T7-sourced strings with no T3 row (zui's T3 rows cover only 152 moves, and the LP1/RP2 string prefixes are overwhelmingly T7/T8 Steve records). Notable families: the whole `1,2` / `2,1` / `1,1` / `2,2` families (basics carry no T3 row); FLK / LWV / RWV / PAB / DCK / DRU stance families; WS.1,1 / WS.1,2 / WS.2,2 (WS context, unmapped — no WS-context row candidate exists); the 23 input-~ families (cancel notation); the `(1)` / `(2)` parenthesized families. Their correct clips come from #988 Step 2 (original T8 refs) or future extraction — never from a T3 row recorded as correct. Donor retirement is DESIGNED, not a regression: wiring plans replaces single-row resolution wholesale, even for CLEAN donors, because one row cannot be correct for a multi-hit string.

## Canonicalization audit (CORRECTED rule, mandatory)

- Rule: strip ONLY a trailing `~t[378]\.[a-z]+(\.\d+)?$` suffix, then a trailing `*` hold marker. A `~` INSIDE the input is part of the move (Tekken cancel notation).
- Input-~ canonicals in Batch 1 scope: **23**, all kept as their OWN keys (never variants of the stripped key): (d/f+1),2~1; (d/f+1),2~2; (d/f+1),2~f+1+2; (d/f+1),2~f+1+2_r56; (f+2),1~2; LWV.1,2~1; PAB.d/f+1,2~1; RWV.1,2~1; b+1,2~1; d+2~n~(1),2; d+2~n~(1),f+2; d+2~n~1,2; d+2~n~1,f+2; d/f+1,2~1; d/f+1,2~2; d/f+1,2~f+1+2; d/f+1,2~f+1+2,1; d/f+1,2~f+1+2,1,1; d/f+1,2~f+1+2,1,1,2; d/f+1,2~f+1+2,1,1,2,1; d/f+1,2~f+1+2,1,1,2,1,1,2,1,2; d/f+1,2~f+1+2,1,1,2,1,1,2,1,b+2; f+2,1~2.
- File-wide `~` audit (comma keys): suffix forms `~t8.steve` (44) + INPUT-~ (56). The 19 Batch 1 variants are all `~t8.steve` twins. No `~t7`/`~t3` suffix forms exist in zui (unlike torch's `~t7.anna`/`~t3.anna` families).
- `__main` canonicals in Batch 1 scope: 0. Corrupted keys in Batch 1 scope: 0 (no `&#` / `&amp;` / `&#58;` keys — the diablo/phantom corrupted-key filing does not arise here).
- Spelling quirks kept distinct (never merged/smoothed): `d/f` vs `df` forms, `WS.` vs `ws` forms, `u/f` vs `uf` families, parenthesized `(1)`/`(2)` forms, space-separated stance forms (`FLK 1,1` vs `FLK.1,1` vs `FLK (1),1`), and the `_r221` / `_r56` row-suffixed keys. WS-context fix applied: lowercase no-dot `ws` spellings are WS context, not standing (zui's WS canonicals are the uppercase-dot `WS.1,1` / `WS.1,2` / `WS.2,2` forms, context ws via the stance-token rule).
- ROW DUAL-ROLE CAUTION applied: a row verified for one string/context is NOT globally verified — every step gate-checks its own row again (e.g. jin row 221 verifies for f+2,1 step 2 but is rejected for f+2,1_r221 step 2 under that key's bits reading; jin row 222 verifies for f+2,1,2 step 3 and f+2,1,2,2 step 3 independently).

## Job 3 / Job 4 (corrected procedures, skull Batch 1 method — honestly 0)

- Job 3: 0 report entries, 0 fills wired. No zui entries exist in match_search.json or job3.log. Nothing to fill from, nothing hunted, nothing invented. The stricter fill rule (SOFT proxy required), dedupe (prefix vs __main duplicates), and agreement-note wording apply formally and are vacuous here.
- Job 4: 0 joined steps, corrected join ONLY (fighter-only, BANK_DIR jin, join iff Job 2 entry key == step prefix, row == candidate row, step == own). With zero Job 2 zui entries this yields no joins. The naive cross-fighter join is INVALID and was never used. Bank-level Job 4 jin candidates (47) are documented as unjoinable, never promoted — and a join never promotes anyway.
- No SOFT fill inherited from #1097 (Pantera-specific, still unapproved, does not transfer).

## Formatter deviation (evidence-based, stated — not hidden)

The generic prescription (json.dumps(indent=2, ensure_ascii=False) + "\n") does NOT reproduce zui-1096.json byte-identically — and neither does any other json.dumps variant. The base file is not dumps-canonical: it carries 7 hand-formatted lines (a separator comma on its own line before `canon_moves`, triple-space colons on `canon_moves` / `canon_wiring`). Forcing re-serialization would rewrite those lines — a non-surgical diff. The governing rule is 'reproduce the base except the surgical diff', so this lane inserts the string_step_plans block as raw text after the opening brace and leaves every other byte untouched. Verified with diff: 0 removed lines, 9217 added lines (the plans block only). All non-plan top-level keys deep-equal the input on parse-back. Future zui batches should do the same (or accept a one-time normalization, called out in their PR).

## Tests

- Minimal-tree node --test: **11 pass / 0 fail** (counts 654/87/194; Batch 1 keys exactly the 194; verified rows non-null with jin buttons and throw 0, review/unmapped row null; no soft flags; no bank_verified_row anywhere; jin row 35/220/216 identities + never wired; flagships d+1+2,2 / f+2,1 / f+2,1,2,2 / d+1+2,1 / f+2,1_r221; verified-last-step set exactly the 6; fighter.js step-plan markers present). node --check fighter.js OK.
- This is zui's BASELINE test file — later zui batches accumulate cumulatively with every Batch 1 CONTENT assertion preserved verbatim (TEST-EVOLUTION RULE; Pantera's latent break NOT copied).
- LIMITATION (honest): full 200-test suite comparison vs pristine main NOT run — no full current-main checkout exists on this box. Blast radius is confined by construction: no engine changes, no moves/strings changes, no prior-plan changes (zui had none), doc + test + audit-append only. The suite comparison must be run before merge (CI will also cover it).
- NOT play-verified: no fight played. Nothing here is 'fixed' until the user plays it.

## Canonical table (all 175; steps show status + row or candidate)

- `(1),(1),2` [standing] → unmapped-all: (1)=unmapped | (1)=unmapped | 2=unmapped
- `(1),(1),d+1` [standing] → unmapped-all: (1)=unmapped | (1)=unmapped | d+1=unmapped
- `(1),(2),(1),2` [standing] → unmapped-all: (1)=unmapped | (2)=unmapped | (1)=unmapped | 2=unmapped
- `(1),(2),(1),d+2` [standing] → unmapped-all: (1)=unmapped | (2)=unmapped | (1)=unmapped | d+2=unmapped
- `(1),(2),1` [standing] → unmapped-all: (1)=unmapped | (2)=unmapped | 1=unmapped
- `(1),(2),1,2` [standing] → unmapped-all: (1)=unmapped | (2)=unmapped | 1=unmapped | 2=unmapped
- `(1),(2),1,d+2` [standing] → unmapped-all: (1)=unmapped | (2)=unmapped | 1=unmapped | d+2=unmapped
- `(1),1` [standing] → unmapped-all: (1)=unmapped | 1=unmapped
- `(1),1,2` [standing] → unmapped-all: (1)=unmapped | 1=unmapped | 2=unmapped
- `(1),1,d+1` [standing] → unmapped-all: (1)=unmapped | 1=unmapped | d+1=unmapped
- `(1),2` [standing] → unmapped-all: (1)=unmapped | 2=unmapped
- `(1),2,1` [standing] → unmapped-all: (1)=unmapped | 2=unmapped | 1=unmapped
- `(1),2,1,2` [standing] → unmapped-all: (1)=unmapped | 2=unmapped | 1=unmapped | 2=unmapped
- `(1),2,1,d+2` [standing] → unmapped-all: (1)=unmapped | 2=unmapped | 1=unmapped | d+2=unmapped
- `(1),d+1` [standing] → unmapped-all: (1)=unmapped | d+1=unmapped
- `(2),(1),2` [standing] → unmapped-all: (2)=unmapped | (1)=unmapped | 2=unmapped
- `(2),1,2` [standing] → unmapped-all: (2)=unmapped | 1=unmapped | 2=unmapped
- `(D+2),(1),2` [standing] → unmapped-all: (D+2)=unmapped | (1)=unmapped | 2=unmapped
- `(D+2),1` [standing] → unmapped-all: (D+2)=unmapped | 1=unmapped
- `(D+2),1,2` [standing] → unmapped-all: (D+2)=unmapped | 1=unmapped | 2=unmapped
- `(During Tackle) 1/2,1/2` [standing, chord] → unmapped-all: (During Tackle) 1/2=unmapped | 1/2=unmapped
- `(During Tackle) 1/2,1/2,1/2` [standing, chord] → unmapped-all: (During Tackle) 1/2=unmapped | 1/2=unmapped | 1/2=unmapped
- `(During Tackle) 1/2,1/2,1/2,1/2` [standing, chord] → unmapped-all: (During Tackle) 1/2=unmapped | 1/2=unmapped | 1/2=unmapped | 1/2=unmapped
- `(b+1),(d+2),1` [standing] → unmapped-all: (b+1)=unmapped | (d+2)=unmapped | 1=unmapped
- `(b+1),2` [standing] → unmapped-all: (b+1)=unmapped | 2=unmapped
- `(b+1),d+2` [standing] → unmapped-all: (b+1)=unmapped | d+2=unmapped
- `(b+1),d+2,1` [standing] → unmapped-all: (b+1)=unmapped | d+2=unmapped | 1=unmapped
- `(d/f+1),2` [standing] → unmapped-all: (d/f+1)=unmapped | 2=unmapped
- `(d/f+1),2~1` [standing, chord] → unmapped-all: (d/f+1)=unmapped | 2~1=unmapped
- `(d/f+1),2~2` [standing] → unmapped-all: (d/f+1)=unmapped | 2~2=unmapped
- `(d/f+1),2~f+1+2` [standing, chord] → unmapped-all: (d/f+1)=unmapped | 2~f+1+2=unmapped
- `(d/f+1),2~f+1+2_r56` [standing, chord] → unmapped-all: (d/f+1)=unmapped | 2~f+1+2_r56=unmapped
- `(f+1+2),2` [standing, chord] → unmapped-all: (f+1+2)=unmapped | 2=unmapped
- `(f+2),1` [standing] → unmapped-all: (f+2)=unmapped | 1=unmapped
- `(f+2),1~2` [standing, chord] → unmapped-all: (f+2)=unmapped | 1~2=unmapped
- `1,1` [standing] → unmapped-all: 1=unmapped | 1=unmapped
- `1,1,2` [standing] → unmapped-all: 1=unmapped | 1=unmapped | 2=unmapped
- `1,1,d+1` [standing] → unmapped-all: 1=unmapped | 1=unmapped | d+1=unmapped
- `1,2` [standing] → unmapped-all: 1=unmapped | 2=unmapped
- `1,2,1` [standing] → unmapped-all: 1=unmapped | 2=unmapped | 1=unmapped
- `1,2,1,2` [standing] → unmapped-all: 1=unmapped | 2=unmapped | 1=unmapped | 2=unmapped
- `1,2,1,d+2` [standing] → unmapped-all: 1=unmapped | 2=unmapped | 1=unmapped | d+2=unmapped
- `1,d+1` [standing] → unmapped-all: 1=unmapped | d+1=unmapped
- `2,1` [standing] → unmapped-all: 2=unmapped | 1=unmapped
- `2,1,2` [standing] → unmapped-all: 2=unmapped | 1=unmapped | 2=unmapped
- `2,2` [standing] → unmapped-all: 2=unmapped | 2=unmapped
- `D+2,1` [crouch] → unmapped-all: D+2=unmapped | 1=unmapped
- `D+2,1,2` [crouch] → unmapped-all: D+2=unmapped | 1=unmapped | 2=unmapped
- `DCK 1+2,1,2,1,2,1,2,1,2,1` [standing, chord] → unmapped-all: DCK 1+2=unmapped | 1=unmapped | 2=unmapped | 1=unmapped | 2=unmapped | 1=unmapped | 2=unmapped | 1=unmapped | 2=unmapped | 1=unmapped
- `DCK.1+2,1+2` [standing, chord] → unmapped-all: DCK.1+2=unmapped | 1+2=unmapped
- `DCK.1+2,1+2,1+2` [standing, chord] → unmapped-all: DCK.1+2=unmapped | 1+2=unmapped | 1+2=unmapped
- `DCK.1+2,1+2,1+2,1+2` [standing, chord] → unmapped-all: DCK.1+2=unmapped | 1+2=unmapped | 1+2=unmapped | 1+2=unmapped
- `DRU (2),2` [standing] → unmapped-all: DRU (2)=unmapped | 2=unmapped
- `DRU 1+2,1+2` [standing, chord] → unmapped-all: DRU 1+2=unmapped | 1+2=unmapped
- `DRU 1+2,1+2,1+2` [standing, chord] → unmapped-all: DRU 1+2=unmapped | 1+2=unmapped | 1+2=unmapped
- `DRU 2,2` [standing] → unmapped-all: DRU 2=unmapped | 2=unmapped
- `DRU u/b+1+2,1` [standing, chord] → unmapped-all: DRU u/b+1+2=unmapped | 1=unmapped
- `FLK (1),(1),(1),2` [standing] → unmapped-all: FLK (1)=unmapped | (1)=unmapped | (1)=unmapped | 2=unmapped
- `FLK (1),(1),1` [standing] → unmapped-all: FLK (1)=unmapped | (1)=unmapped | 1=unmapped
- `FLK (1),(1),1,2` [standing] → unmapped-all: FLK (1)=unmapped | (1)=unmapped | 1=unmapped | 2=unmapped
- `FLK (1),1` [standing] → unmapped-all: FLK (1)=unmapped | 1=unmapped
- `FLK (1),1,1` [standing] → unmapped-all: FLK (1)=unmapped | 1=unmapped | 1=unmapped
- `FLK (1),1,1,2` [standing] → unmapped-all: FLK (1)=unmapped | 1=unmapped | 1=unmapped | 2=unmapped
- `FLK (1),d+1` [standing] → unmapped-all: FLK (1)=unmapped | d+1=unmapped
- `FLK (1),f+1` [standing] → unmapped-all: FLK (1)=unmapped | f+1=unmapped
- `FLK 1,1` [standing] → unmapped-all: FLK 1=unmapped | 1=unmapped
- `FLK 1,1,1` [standing] → unmapped-all: FLK 1=unmapped | 1=unmapped | 1=unmapped
- `FLK 1,1,1,2` [standing] → unmapped-all: FLK 1=unmapped | 1=unmapped | 1=unmapped | 2=unmapped
- `FLK 1,d+1` [standing] → unmapped-all: FLK 1=unmapped | d+1=unmapped
- `FLK 1,f+1` [standing] → unmapped-all: FLK 1=unmapped | f+1=unmapped
- `FLK.1,1` [standing] → unmapped-all: FLK.1=unmapped | 1=unmapped
- `FLK.1,1,1` [standing] → unmapped-all: FLK.1=unmapped | 1=unmapped | 1=unmapped
- `FLK.1,1,1,2` [standing] → unmapped-all: FLK.1=unmapped | 1=unmapped | 1=unmapped | 2=unmapped
- `FLK.1,1,2` [standing] → unmapped-all: FLK.1=unmapped | 1=unmapped | 2=unmapped
- `FLK.1,1,d+1` [standing] → unmapped-all: FLK.1=unmapped | 1=unmapped | d+1=unmapped
- `FLK.1,1,f+1` [standing] → unmapped-all: FLK.1=unmapped | 1=unmapped | f+1=unmapped
- `FLK.1,2` [standing] → unmapped-all: FLK.1=unmapped | 2=unmapped
- `FLK.1,d+1` [standing] → unmapped-all: FLK.1=unmapped | d+1=unmapped
- `FLK.1,f+1` [standing] → unmapped-all: FLK.1=unmapped | f+1=unmapped
- `LWV (1),(f+1),1` [standing] → unmapped-all: LWV (1)=unmapped | (f+1)=unmapped | 1=unmapped
- `LWV (1),1` [standing] → unmapped-all: LWV (1)=unmapped | 1=unmapped
- `LWV (1),f+1` [standing] → unmapped-all: LWV (1)=unmapped | f+1=unmapped
- `LWV (1),f+1,1` [standing] → unmapped-all: LWV (1)=unmapped | f+1=unmapped | 1=unmapped
- `LWV (2),1` [standing] → unmapped-all: LWV (2)=unmapped | 1=unmapped
- `LWV 1,1` [standing] → unmapped-all: LWV 1=unmapped | 1=unmapped
- `LWV 1,f+1` [standing] → unmapped-all: LWV 1=unmapped | f+1=unmapped
- `LWV 1,f+1,1` [standing] → unmapped-all: LWV 1=unmapped | f+1=unmapped | 1=unmapped
- `LWV 2,1` [standing] → unmapped-all: LWV 2=unmapped | 1=unmapped
- `LWV.1,1` [standing] → unmapped-all: LWV.1=unmapped | 1=unmapped
- `LWV.1,2` [standing] → unmapped-all: LWV.1=unmapped | 2=unmapped
- `LWV.1,2~1` [standing, chord] → unmapped-all: LWV.1=unmapped | 2~1=unmapped
- `LWV.1,f+1` [standing] → unmapped-all: LWV.1=unmapped | f+1=unmapped
- `LWV.1,f+1,1` [standing] → unmapped-all: LWV.1=unmapped | f+1=unmapped | 1=unmapped
- `LWV.2,1` [standing] → unmapped-all: LWV.2=unmapped | 1=unmapped
- `PAB (1),(2),1` [standing] → unmapped-all: PAB (1)=unmapped | (2)=unmapped | 1=unmapped
- `PAB (1),2` [standing] → unmapped-all: PAB (1)=unmapped | 2=unmapped
- `PAB (1),2,1` [standing] → unmapped-all: PAB (1)=unmapped | 2=unmapped | 1=unmapped
- `PAB (b+1),(1),(2),1` [standing] → unmapped-all: PAB (b+1)=unmapped | (1)=unmapped | (2)=unmapped | 1=unmapped
- `PAB (b+1),(1),2` [standing] → unmapped-all: PAB (b+1)=unmapped | (1)=unmapped | 2=unmapped
- `PAB (b+1),(1),2,1` [standing] → unmapped-all: PAB (b+1)=unmapped | (1)=unmapped | 2=unmapped | 1=unmapped
- `PAB (b+1),1` [standing] → unmapped-all: PAB (b+1)=unmapped | 1=unmapped
- `PAB (b+1),1,2` [standing] → unmapped-all: PAB (b+1)=unmapped | 1=unmapped | 2=unmapped
- `PAB (b+1),1,2,1` [standing] → unmapped-all: PAB (b+1)=unmapped | 1=unmapped | 2=unmapped | 1=unmapped
- `PAB (d/f+1),(1),(2),1` [standing] → unmapped-all: PAB (d/f+1)=unmapped | (1)=unmapped | (2)=unmapped | 1=unmapped
- `PAB (d/f+1),(1),2` [standing] → unmapped-all: PAB (d/f+1)=unmapped | (1)=unmapped | 2=unmapped
- `PAB (d/f+1),(1),2,1` [standing] → unmapped-all: PAB (d/f+1)=unmapped | (1)=unmapped | 2=unmapped | 1=unmapped
- `PAB (d/f+1),1` [standing] → unmapped-all: PAB (d/f+1)=unmapped | 1=unmapped
- `PAB (d/f+1),1,2` [standing] → unmapped-all: PAB (d/f+1)=unmapped | 1=unmapped | 2=unmapped
- `PAB (d/f+1),1,2,1` [standing] → unmapped-all: PAB (d/f+1)=unmapped | 1=unmapped | 2=unmapped | 1=unmapped
- `PAB (d/f+1),2` [standing] → unmapped-all: PAB (d/f+1)=unmapped | 2=unmapped
- `PAB (f+2),1` [standing] → unmapped-all: PAB (f+2)=unmapped | 1=unmapped
- `PAB 1,2` [standing] → unmapped-all: PAB 1=unmapped | 2=unmapped
- `PAB 1,2,1` [standing] → unmapped-all: PAB 1=unmapped | 2=unmapped | 1=unmapped
- `PAB b+1,1` [standing] → unmapped-all: PAB b+1=unmapped | 1=unmapped
- `PAB b+1,1,2` [standing] → unmapped-all: PAB b+1=unmapped | 1=unmapped | 2=unmapped
- `PAB b+1,1,2,1` [standing] → unmapped-all: PAB b+1=unmapped | 1=unmapped | 2=unmapped | 1=unmapped
- `PAB d/f+1,1` [standing] → unmapped-all: PAB d/f+1=unmapped | 1=unmapped
- `PAB d/f+1,1,2` [standing] → unmapped-all: PAB d/f+1=unmapped | 1=unmapped | 2=unmapped
- `PAB d/f+1,1,2,1` [standing] → unmapped-all: PAB d/f+1=unmapped | 1=unmapped | 2=unmapped | 1=unmapped
- `PAB d/f+1,2` [standing] → unmapped-all: PAB d/f+1=unmapped | 2=unmapped
- `PAB f+2,1` [standing] → unmapped-all: PAB f+2=unmapped | 1=unmapped
- `PAB.1,2` [standing] → unmapped-all: PAB.1=unmapped | 2=unmapped
- `PAB.1,2,1` [standing] → unmapped-all: PAB.1=unmapped | 2=unmapped | 1=unmapped
- `PAB.b+1,1` [standing] → unmapped-all: PAB.b+1=unmapped | 1=unmapped
- `PAB.b+1,1,2` [standing] → unmapped-all: PAB.b+1=unmapped | 1=unmapped | 2=unmapped
- `PAB.b+1,1,2,1` [standing] → unmapped-all: PAB.b+1=unmapped | 1=unmapped | 2=unmapped | 1=unmapped
- `PAB.d/f+1,1` [crouch] → unmapped-all: PAB.d/f+1=unmapped | 1=unmapped
- `PAB.d/f+1,1,2` [crouch] → unmapped-all: PAB.d/f+1=unmapped | 1=unmapped | 2=unmapped
- `PAB.d/f+1,1,2,1` [crouch] → unmapped-all: PAB.d/f+1=unmapped | 1=unmapped | 2=unmapped | 1=unmapped
- `PAB.d/f+1,2` [crouch] → unmapped-all: PAB.d/f+1=unmapped | 2=unmapped
- `PAB.d/f+1,2~1` [crouch, chord] → unmapped-all: PAB.d/f+1=unmapped | 2~1=unmapped
- `PAB.f+2,1` [standing] → unmapped-all: PAB.f+2=unmapped | 1=unmapped
- `RWV (1),2` [standing] → unmapped-all: RWV (1)=unmapped | 2=unmapped
- `RWV 1,2` [standing] → unmapped-all: RWV 1=unmapped | 2=unmapped
- `RWV.1,2` [standing] → unmapped-all: RWV.1=unmapped | 2=unmapped
- `RWV.1,2~1` [standing, chord] → unmapped-all: RWV.1=unmapped | 2~1=unmapped
- `WS (1),1` [standing] → unmapped-all: WS (1)=unmapped | 1=unmapped
- `WS (1),2` [standing] → unmapped-all: WS (1)=unmapped | 2=unmapped
- `WS 1,1` [standing] → unmapped-all: WS 1=unmapped | 1=unmapped
- `WS 1,2` [standing] → unmapped-all: WS 1=unmapped | 2=unmapped
- `WS.1,1` [ws] → unmapped-all: WS.1=unmapped | 1=unmapped
- `WS.1,2` [ws] → unmapped-all: WS.1=unmapped | 2=unmapped
- `WS.2,2` [ws] → unmapped-all: WS.2=unmapped | 2=unmapped
- `b+1+2,H.1+2` [standing, chord] → unmapped-all: b+1+2=unmapped | H.1+2=unmapped
- `b+1,2` [standing] → unmapped-all: b+1=unmapped | 2=unmapped
- `b+1,2~1` [standing, chord] → unmapped-all: b+1=unmapped | 2~1=unmapped
- `b+1,d+2` [standing] → unmapped-all: b+1=unmapped | d+2=unmapped
- `b+1,d+2,1` [standing] → unmapped-all: b+1=unmapped | d+2=unmapped | 1=unmapped
- `d+1+2,1` [crouch, chord] → partial: d+1+2=row 92 | 1=unmapped (cand 177)
- `d+1+2,1,2` [crouch, chord] → partial: d+1+2=row 92 | 1=unmapped (cand 177) | 2=row 183
- `d+1+2,2` [crouch, chord] → verified-all: d+1+2=row 92 | 2=row 93
- `d+2,1` [crouch] → unmapped-all: d+2=unmapped | 1=unmapped
- `d+2,1,2` [crouch] → unmapped-all: d+2=unmapped | 1=unmapped | 2=unmapped
- `d+2~n~(1),2` [crouch, chord] → unmapped-all: d+2~n~(1)=unmapped | 2=unmapped
- `d+2~n~(1),f+2` [crouch, chord] → unmapped-all: d+2~n~(1)=unmapped | f+2=unmapped
- `d+2~n~1,2` [crouch, chord] → unmapped-all: d+2~n~1=unmapped | 2=unmapped
- `d+2~n~1,f+2` [crouch, chord] → unmapped-all: d+2~n~1=unmapped | f+2=unmapped
- `d/f+1,2` [crouch] → unmapped-all: d/f+1=unmapped | 2=unmapped
- `d/f+1,2~1` [crouch, chord] → unmapped-all: d/f+1=unmapped | 2~1=unmapped
- `d/f+1,2~2` [crouch] → unmapped-all: d/f+1=unmapped | 2~2=unmapped
- `d/f+1,2~f+1+2` [crouch, chord] → unmapped-all: d/f+1=unmapped | 2~f+1+2=unmapped
- `d/f+1,2~f+1+2,1` [crouch, chord] → unmapped-all: d/f+1=unmapped | 2~f+1+2=unmapped | 1=unmapped
- `d/f+1,2~f+1+2,1,1` [crouch, chord] → unmapped-all: d/f+1=unmapped | 2~f+1+2=unmapped | 1=unmapped | 1=unmapped
- `d/f+1,2~f+1+2,1,1,2` [crouch, chord] → unmapped-all: d/f+1=unmapped | 2~f+1+2=unmapped | 1=unmapped | 1=unmapped | 2=unmapped
- `d/f+1,2~f+1+2,1,1,2,1` [crouch, chord] → unmapped-all: d/f+1=unmapped | 2~f+1+2=unmapped | 1=unmapped | 1=unmapped | 2=unmapped | 1=unmapped
- `d/f+1,2~f+1+2,1,1,2,1,1,2,1,2` [crouch, chord] → unmapped-all: d/f+1=unmapped | 2~f+1+2=unmapped | 1=unmapped | 1=unmapped | 2=unmapped | 1=unmapped | 1=unmapped | 2=unmapped | 1=unmapped | 2=unmapped
- `d/f+1,2~f+1+2,1,1,2,1,1,2,1,b+2` [crouch, chord] → unmapped-all: d/f+1=unmapped | 2~f+1+2=unmapped | 1=unmapped | 1=unmapped | 2=unmapped | 1=unmapped | 1=unmapped | 2=unmapped | 1=unmapped | b+2=unmapped
- `f+1+2,2` [standing, chord] → unmapped-all: f+1+2=unmapped | 2=unmapped
- `f+2,1` [standing] → partial: f+2=unmapped | 1=row 221
- `f+2,1,2` [standing] → partial: f+2=unmapped | 1=unmapped | 2=row 222
- `f+2,1,2,2` [standing] → partial: f+2=unmapped | 1=unmapped | 2=row 222 | 2=row 223
- `f+2,1_r221` [standing, chord] → unmapped-all: f+2=unmapped | 1_r221=unmapped (cand 221)
- `f+2,1~2` [standing, chord] → unmapped-all: f+2=unmapped | 1~2=unmapped
- `f+2,2` [standing] → unmapped-all: f+2=unmapped | 2=unmapped
- `f+2,2,1+2` [standing, chord] → unmapped-all: f+2=unmapped | 2=unmapped | 1+2=unmapped

## Play-verify checklist (parent delegation — phone portrait, human simulation, after #1096 + this PR merge + deploy + sync)

Zui vs any fighter. Feet grounded where the step is grounded; no jumping row for a ground step; no row from another bank; no T8 content removed.

1. d+1+2,2 [jin 92, jin 93] — the batch's only verified-all string. Both steps grounded standing jin rows (GATE-NOTE: verify they read as crouch-context strikes, not standing strikes, when played). Step 1 is the LP1+RP2 chord row 92; step 2 is the RP2 row 93.
2. d+1+2,1 [jin 92, NO row] — step 1 grounded jin chord row 92 (GATE-NOTE as above); step 2 NO row (jin row 177 button-12 clip must NOT play as an LP1 jab).
3. d+1+2,1,2 [jin 92, NO row, jin 183] — steps 1 and 3 grounded jin rows (GATE-NOTE); step 2 NO row (row 177 must NOT play).
4. f+2,1 [NO row, jin 221] — step 1 NO row (no candidate); step 2 grounded standing jin LP1 row 221. If the coordinator rejects the SINGLE-BANK-FALLBACK, this string must play NO row on step 2 instead — re-check the PR decision before playing.
5. f+2,1,2 [NO row, NO row, jin 222] and f+2,1,2,2 [NO row, NO row, jin 222, jin 223] — steps 1–2 NO rows; later steps grounded standing jin RP2 rows 222/223.
6. f+2,1_r221 [NO row, NO row] — step 2 NO row (row 221 must NOT play under this key's bits-3 reading; the row-221 playback belongs to the f+2,1 canonical, item 4).
7. 1,2 / 2,1 / 1,1 / 2,2 families — NO row on any step (zui's basics carry no T3 row; no donor row may stand in for the LP1/RP2 basics).
8. No step plays jin row 35 (starts-airborne), 216 (jump, button 0), 220 (standing RP2 but never a Batch 1 candidate), or 41 (starts-airborne) for any Batch 1 string.
9. No step plays a row from another bank — zui has only the jin bank, so any non-jin clip (or any clip that is not rows 92/93/183/221/222/223 for the strings above) is a guard failure.
10. No T8 content removed: zui's T8 Steve layer (126 mix keys) and all T8-sourced strings remain in the file, unmapped where unproven — unmapped means 'no row yet', never 'move deleted'.
11. Stance check: Zui's hands-up drunken stagger stance is unchanged — no stance, mix, or move entry was touched by this lane.
