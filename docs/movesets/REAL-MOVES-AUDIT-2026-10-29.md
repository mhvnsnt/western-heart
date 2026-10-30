# Real Moves / Animations Audit — 2026-10-29

Owner order (2026-10-29): "Get the real moves and animations and rows and combo strings and correct the incorrect animations."

Audited tree: `main` @ `1fa7d25fe85ef361719a59aba3acfad8254bfbf9`. The landing PR is
based on `main` @ `32a6c691ffcec40ca12ada256f2412da3c4895a0` (main moved during the
lane: a health-180 + direction-hold change to `fighter.js` only; every other audited
file is blob-identical between the two commits, and the step-plan engine changes were
re-applied onto the newer `fighter.js` and re-tested green). Method: every
`game/assets/movesets/*.json` parsed — all 163 files (129 carry a `moves` dict; 56,527 moves total;
the other 34 are Urban Reign motion banks, the index, and input tables). Counts in the
findings table combine the coordinator pass and a second independent deep pass over every
file; where the two disagreed, the deep pass (two self-agreeing counts) wins and the row
says CORRECTED 2026-10-30. Counts below are computed from the files, never estimated.
Full per-fighter table: Appendix A. TTT2-derived rows are owned by the separate TTT2
wiring lane; nothing in this audit blocks on TTT2, and no step's only source was TTT2.

## What "incorrect" means here (the runtime truth)

On main before this pass, `game/js/fighter.js` `_attackClipPlan` resolved a move's clip
through: own row → same-notation row → `anim_t3` (non-`nearest`) → **donor tier**
(closest animated move in the same moveset) → button/limb **match tier** → **generic
tier** (`light`/`medium`/`heavy`). Every move therefore played *something* — and
`test/attack-anim.test.mjs` passes 9/9 on main — but donor/match/generic picks are
wrong animations by definition: a different move's row standing in for the real one.
The incorrect-animation surface is exactly the set of moves that reach those tiers,
plus rows whose recorded mapping is approximate or disproven.

## Findings (repo-wide)

| # | Category | Count | Notes |
|---|---|---|---|
| a1 | Moves with NO T3 row reference (`t3_row` and `anim_t3` both absent) | 6,471 / 56,527 | These resolve only via notation/donor/match/generic tiers at runtime. Worst share (≥100 moves): ryusan 211/211, pond 620/620, mariposa 372/372, burger-demon 466/466, burger-speed-demon 454/454, burger-the-mouth 454/454 (all 100%), ryuji 110/127 (87%), baek-master-white 155/291 (53%). |
| a2 | Moves with `anim_ref: UNMAPPED:*` (explicitly unmapped, mostly `UNMAPPED:t7-clip-pending`) | 781 | Pantera 109, phantom 127, skull 114, burger 111, kinpo 103, demonio 80, diablo 80, scimitar 57. These are T7/T8-sourced moves whose real clip is not wired; at runtime they donor/match-fall-back. Their real source is the T7 clip-extraction lane (`kinmot.bin` decoded; 0x8000-bank clip bytes unresolved) — not TTT2. |
| a3 | Moves whose `anim_t3` mapping is guess-grade by its own `match` label | **12,684 of 30,291 anim_t3** | 10,221 `nearest (approximate)` + 2,463 `same-notation` (fighter.js calls same-notation a merge-time guess; nearest disagrees with the pressed button 43% of slots). CORRECTED/EXTENDED 2026-10-30 per the deep pass. |
| a3x | Moves with cross-bank `anim_t3` (anim bank outside the file's anim_bank/t3_source) | 12,683 | Worst: kronos-attire2 2,112, koreshi 844, kronos 573, byou 571, rave 514. |
| a8 | Moves with NO anim mapping of any kind | 487 | 11 keep a bare t3_row; 18 carry `t3_unmapped_former_*` removed-anim markers (named in workpapers). Worst: baek-master-white 153/291, pond 151/620, thor 78/322, menajerii 51/193. (Distinct from a1: a1 counts moves with no T3-row reference; most still carry a t7:/t8: anim_ref.) |
| a9 | Strike/throw identity mismatches (JSON-internal proxies; bank hit_frames is the settling source) | 9 + 175 | 9 strike-class moves point at named throw anims (kingtyrant/scimitar/star: inputs literally `Back throw`/`Left throw`/`Right throw`); 175 moves carry throw:true/isGrab:true with a non-throw move_class. | The engine defers `nearest` past the donor tier for the same reason. Every one is a candidate incorrect animation until replaced by a true-map row. |
| a4 | Pantera `2,1` playing T3 King row 220 | 1 string (4 keys incl. twins) | Row 220 is branch-proven as T3's real LP follow-up from row 203 — and it is an airborne LP+RP chord clip (button 3, air frames 18–60). For a standing `2,1` step it is the wrong animation. Corrected by the step plans in this pass: planned `2,1` keys no longer play it; the step stays UNMAPPED (no standing LP ender row exists in any searched source). |
| a5 | Pantera standing `4` / `4_r216` pointing at row 216 | 2 moves | Already flagged in `docs/anim/PROCEDURAL_AUDIT.md` (dash-rows entry, on main): the branch graph proves row 216 (Konvict Kick) is reachable ONLY from dash row 3 / run row 4, never standing. True standing-4 rows (candidates 106/124) are unverified — NOT changed in this pass; named here as owed adjudication. |
| a6 | `string_step_plans` on main | 0 fighters | PR #1096 (Pantera, 60 keys) was still open/conflicting; every other step-plan PR (28 in the original stack + Skull/Zui/Torch batches) stacks on it. No fighter on main had step plans, so planned strings donor-fell-back like everything else. |
| a7 | Step-plan steps with no candidate row (Pantera Batch 1) | 89 of 137 steps UNMAPPED + 9 REVIEW at #1096 | Researched in this pass — see Corrections. |
| b | Donor/stand-in explicitly marked in move data | **7,032 moves** | CORRECTED 2026-10-30 (deep pass, two independent counts agreeing): donor 6,783 (a dedicated `donor_fighter` key sits on 6,782 move objects), standin 568, fallback 8, placeholder 1, generic 2; procedural 0. Worst: kronos-attire2 2,458 flagged (donor_fighter kronos ×1,815 / zangief ×463 / sf-zangief ×180), koreshi 751, kronos 650, demonio-human 581, doc-frank-hood/wowomomo 525 each. The first version of this doc wrongly called donor wiring runtime-only — it is recorded in the data and is named per fighter in the audit workpapers (`audit-main-movesets.md`, lane workspace). The runtime donor tier ADDITIONALLY fires for unmarked moves failing the own/notation/anim tiers (a1–a3). |
| c | Strings whose notation has no move entry | **4 repo-wide** | CORRECTED 2026-10-30 (deep pass): chatur `d/b+1,2` and `1,2,1+2`; pond `MIST 1,2`; ryusan `WR f,f,F (Mid Screen)`. Pantera: 0 of 81. |
| f | No Mercy–sourced moves (SUSPECT — wrong FileTable window) | 13 moves | `cainelias`: `2+4`, `f+2+4`, `1+3`, `1+2+3+4_u1`, `1+2+3+4_u2` (anim_refs `teardown/wwf-no-mercy/animations/clips/anim_*.npy`). `negativo`: `u/f+1+2` (name "No Mercy" — a move NAME, its ref is `t7:negan:`, not NM-sourced; listed to prevent a false flag). `ryuji-rock`: `rock_bottom_nm`, `peoples_elbow_nm`, `peoples_elbow_running_nm`, `rock_taunt_nm`, `rock_spinebuster_nm`, `rock_stomp_nm`, `rock_spinning_ddt_nm` (refs `mk:MK-*` named "(NO MERCY)"). The cainelias five point directly at wrong-window bank clips and must be re-checked against the true-window re-extraction (separate owed program — not started here). The ryuji-rock seven are the Route-3-gated Rock specials; their NM clip identity is suspect for the same reason. |

## Corrections landed in this pass (Pantera step plans — supersedes #1096)

Source of record for every fill: the T3 King branch graph — GRE
`tekken3/movesets/moveset_king.json` (`divmot03_king.bin`, 652 moves, per-move
`branches[]`, 4,023-entry `move_index`; the same extraction sits in this repo at
`teardown/tekken3/movesets/`). Validation before use: the graph reproduces every
already-verified Batch 1 chain link exactly (row 97 `RP`→98, row 98 `LP`→198,
row 110 jab, row 203 `2`). Every fill was also cross-checked against
`game/assets/anim/t3/king_on_pantera_leoman/hit_frames.json` HARD gates (button bits
== step bits, throw flag 0) and GRE grounded/air windows. T3 use is logged in
`docs/anim/PROCEDURAL_AUDIT.md` per the data-source law: no T5/T6/T7/T8/TTT2 King
step clip is decoded yet (T7 `kinmot.bin` moves are decoded; the clip bytes are not),
so T3 is the fallback of record for King step identity until the T7 extraction lands.

- All 98 UNMAPPED/REVIEW step occurrences in the 60 Batch 1 plans were researched.
  **57 occurrences have a real row** (rows 97, 98, 99, 111, 117, 131, 198, 199, 209,
  223, 257, 258) and are now recorded as REVIEW candidates with
  `candidate_source: "t3-branch-graph"` and the citation in each step's `reasons`.
  They do NOT play yet: promotion to `verified` still requires the plan's FK soft
  gate (in-window limb-extension peak) + play-verify, per the Batch 1 gate law.
  Distinct fills include: `1,2` step 2 → row 98 (jab row 110 branch `RP` → slot 297);
  `1,2,1` step 3 → row 198; `1+2,1` steps → rows 223, 209; `b+2,1` steps → rows 99,
  199; `b+2,1+2` step 2 → row 97 (PR #1097's Job-3 VERIFIED fill, recorded here as
  review pending this plan's own soft gate); `d/b+1+2,2` step 1 → row 131;
  `f+2` family first steps → row 111, step 2 → row 198; review candidates 117
  (`d/f+1`), 257, 258 branch-confirmed (chain 97→98→198→257→258 fully branch-proven).
- Last-step status over the 60 keys: **verified 11 / review 25 / unmapped 24**
  (was 11 / 4 / 45). No step was promoted to `verified` in this pass.
- **41 step occurrences have no real row in any searched source and stay UNMAPPED**,
  named: `1,1` step 2; `2,1` step 2 (×4 keys incl. twins — row 220 proven real but
  HARD-gate-failed, see a4); `WS.2,2` both steps (×3 keys); `b+1+2,1+2` both steps;
  `b+1+2,2` step 1 (row 97's canonical identity in the same file is `d+1+2` — left
  for owner adjudication, both prior lanes declined it); `b+1,2` both steps (×3 keys);
  `d+1,2` both steps; `d/f+1,2` step 2 (×3 keys); `d/f+2,1` step 2 (×3 keys);
  `f+2,d+1` step 2 and `f+2,d+1,2` steps 2–3 (×5 keys); `u+1,1`/`u+1,2` step 1
  (`u+1`); `u/b+1,1`/`u/b+1,2` step 1 (`u/b+1`; row 49 is a SOFT candidate from
  PR #1097, never verified-exact — not used).
  Their documented future source is T7 King clip extraction, not TTT2.
- Engine: the #1096 step-plan branch (`_resolveStepPlan`, `_stepChain`,
  `_advanceStepChain`) is applied onto current `game/js/fighte
...[truncated 3072 chars]FILES: 129
TOTALS: {'moves': 56527, 'strings': 6989, 'string_notation_no_move': 7, 'plan_keys': 0, 'direct_row': 50453, 'any_mapped': 55156, 'anim_t3': 30291, 'anim_t3_nearest': 10221, 'marked_moves': 7032, 'nm_rows': 13, 'no_anim_row': 1371, 'unmapped_pending': 781, 'row_discrepancy': 13}
NM total rows: 13 sample: [('cainelias', '2+4'), ('cainelias', 'f+2+4'), ('cainelias', '1+3'), ('cainelias', '1+2+3+4_u1'), ('cainelias', '1+2+3+4_u2'), ('negativo', 'u/f+1+2'), ('ryuji-rock', 'rock_bottom_nm'), ('ryuji-rock', 'peoples_elbow_nm'), ('ryuji-rock', 'peoples_elbow_running_nm'), ('ryuji-rock', 'rock_taunt_nm')]

| fighter | moves | any_mapped | no_anim_row | unmapped_pend | marked | discrep | nearest | strings | str_no_move | plans | NM |
| aotsuki | 530 | 530 | 0 | 0 | 3 | 0 | 171 | 108 | 0 | 0 | 0 |
| armor-king | 500 | 500 | 0 | 0 | 11 | 0 | 0 | 57 | 0 | 0 | 0 |
| awapop | 909 | 909 | 0 | 0 | 0 | 0 | 244 | 175 | 0 | 0 | 0 |
| baek-master-white | 291 | 138 | 153 | 0 | 25 | 0 | 0 | 3 | 0 | 0 | 0 |
| baek | 111 | 111 | 0 | 0 | 0 | 0 | 0 | 3 | 0 | 0 | 0 |
| blanka | 199 | 199 | 0 | 0 | 6 | 0 | 0 | 0 | 0 | 0 | 0 |
| bob | 557 | 557 | 0 | 0 | 3 | 0 | 0 | 98 | 0 | 0 | 0 |
| bruno | 328 | 328 | 0 | 0 | 0 | 0 | 0 | 3 | 0 | 0 | 0 |
| buffalo-bill | 796 | 796 | 0 | 0 | 1 | 0 | 311 | 146 | 0 | 0 | 0 |
| burger-demon | 466 | 442 | 24 | 0 | 3 | 0 | 0 | 100 | 2 | 0 | 0 |
| burger-speed-demon | 454 | 442 | 12 | 0 | 3 | 0 | 0 | 99 | 1 | 0 | 0 |
| burger-the-mouth | 454 | 442 | 12 | 0 | 3 | 0 | 0 | 98 | 0 | 0 | 0 |
| burger | 552 | 550 | 2 | 111 | 0 | 10 | 0 | 107 | 0 | 0 | 0 |
| byou | 728 | 728 | 0 | 0 | 0 | 0 | 0 | 29 | 0 | 0 | 0 |
| cainelias | 46 | 41 | 5 | 0 | 0 | 0 | 0 | 3 | 0 | 0 | 5 |
| charger-attire2 | 199 | 199 | 0 | 0 | 6 | 0 | 0 | 0 | 0 | 0 | 0 |
| charger | 203 | 203 | 0 | 0 | 6 | 0 | 0 | 0 | 0 | 0 | 0 |
| chatur | 281 | 281 | 0 | 0 | 1 | 0 | 0 | 7 | 2 | 0 | 0 |
| chordz | 469 | 469 | 0 | 0 | 4 | 0 | 0 | 71 | 0 | 0 | 0 |
| cyborgx | 624 | 624 | 0 | 0 | 0 | 0 | 0 | 116 | 0 | 0 | 0 |
| deathfang-werewolf | 127 | 127 | 0 | 0 | 8 | 0 | 0 | 0 | 0 | 0 | 0 |
| deathfang | 127 | 122 | 5 | 0 | 8 | 0 | 0 | 0 | 0 | 0 | 0 |
| demonio-bloodline-ember | 686 | 686 | 0 | 0 | 33 | 0 | 212 | 73 | 0 | 0 | 0 |
| demonio-human | 683 | 683 | 0 | 0 | 581 | 0 | 124 | 65 | 0 | 0 | 0 |
| demonio-winged | 1063 | 1063 | 0 | 0 | 128 | 0 | 340 | 127 | 0 | 0 | 0 |
| demonio | 764 | 761 | 3 | 80 | 2 | 0 | 124 | 156 | 0 | 0 | 0 |
| diablo | 661 | 658 | 3 | 80 | 0 | 2 | 100 | 90 | 0 | 0 | 0 |
| dio | 275 | 275 | 0 | 0 | 0 | 0 | 0 | 12 | 0 | 0 | 0 |
| doa-ayane | 23 | 0 | 23 | 0 | 0 | 0 | 0 | 3 | 0 | 0 | 0 |
| doa-bass | 22 | 4 | 18 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 0 |
| doa-hayabusa | 18 | 4 | 14 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 0 |
| doa-jannlee | 21 | 0 | 21 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 0 |
| doa-kasumi | 20 | 4 | 16 | 0 | 0 | 0 | 0 | 3 | 0 | 0 | 0 |
| doa-tina | 26 | 0 | 26 | 0 | 0 | 0 | 0 | 4 | 0 | 0 | 0 |
| doc-frank-frankenstein | 788 | 788 | 0 | 0 | 421 | 0 | 186 | 2 | 0 | 0 | 0 |
| doc-frank-hood | 892 | 892 | 0 | 0 | 525 | 0 | 232 | 2 | 0 | 0 | 0 |
| doc-frank-machine-shop | 933 | 933 | 0 | 0 | 520 | 0 | 232 | 13 | 0 | 0 | 0 |
| doc-frank-wowomomo | 892 | 892 | 0 | 0 | 525 | 0 | 232 | 2 | 0 | 0 | 0 |
| docfrank | 380 | 380 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| dorowani | 175 | 175 | 0 | 0 | 0 | 0 | 0 | 3 | 0 | 0 | 0 |
| dxmmii-patchwork | 170 | 170 | 0 | 0 | 20 | 0 | 0 | 22 | 0 | 0 | 0 |
| dxmmii | 150 | 150 | 0 | 0 | 0 | 0 | 0 | 22 | 0 | 0 | 0 |
| gashadokuro | 530 | 530 | 0 | 0 | 3 | 0 | 171 | 108 | 0 | 0 | 0 |
| gyou-spirit-body | 567 | 567 | 0 | 0 | 2 | 0 | 222 | 88 | 0 | 0 | 0 |
| gyou | 1005 | 1005 | 0 | 0 | 2 | 0 | 413 | 198 | 0 | 0 | 0 |
| hugo | 130 | 130 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| iori | 196 | 196 | 0 | 0 | 8 | 0 | 0 | 0 | 0 | 0 | 0 |
| jin_soul | 1012 | 1012 | 0 | 0 | 4 | 0 | 435 | 169 | 0 | 0 | 0 |
| kai | 877 | 877 | 0 | 0 | 0 | 0 | 280 | 156 | 0 | 0 | 0 |
| kingtyrant | 848 | 848 | 0 | 0 | 0 | 0 | 196 | 151 | 0 | 0 | 0 |
| kinpo | 525 | 524 | 1 | 103 | 0 | 0 | 0 | 101 | 0 | 0 | 0 |
| koreshi | 1080 | 1025 | 55 | 0 | 751 | 0 | 0 | 108 | 0 | 0 | 0 |
| kronos-attire2 | 2600 | 2328 | 272 | 0 | 2458 | 0 | 0 | 2 | 0 | 0 | 0 |
| kronos | 900 | 857 | 43 | 0 | 650 | 0 | 0 | 2 | 0 | 0 | 0 |
| kutz | 160 | 160 | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 |
| lili | 508 | 508 | 0 | 0 | 1 | 0 | 0 | 42 | 0 | 0 | 0 |
| marduk | 340 | 340 | 0 | 0 | 0 | 0 | 0 | 43 | 0 | 0 | 0 |
| mariposa-monarch | 518 | 518 | 0 | 0 | 6 | 0 | 0 | 47 | 0 | 0 | 0 |
| mariposa | 372 | 372 | 0 | 0 | 6 | 0 | 0 | 43 | 0 | 0 | 0 |
| megami | 304 | 284 | 20 | 0 | 6 | 0 | 0 | 18 | 0 | 0 | 0 |
| menajerii | 193 | 142 | 51 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| michiko | 344 | 344 | 0 | 0 | 0 | 0 | 0 | 28 | 0 | 0 | 0 |
| negativo | 292 | 292 | 0 | 0 | 0 | 0 | 0 | 4 | 0 | 0 | 1 |
| nightwolf | 567 | 567 | 0 | 0 | 0 | 0 | 151 | 56 | 0 | 0 | 0 |
| pantera | 874 | 874 | 0 | 109 | 8 | 0 | 160 | 81 | 0 | 0 | 0 |
| phantom | 1019 | 1014 | 5 | 127 | 2 | 0 | 255 | 191 | 0 | 0 | 0 |
| pond | 620 | 469 | 151 | 0 | 5 | 0 | 0 | 113 | 1 | 0 | 0 |
| purplerain | 569 | 569 | 0 | 0 | 3 | 0 | 0 | 142 | 0 | 0 | 0 |
| raiden | 114 | 114 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| rave | 1086 | 1086 | 0 | 0 | 158 | 0 | 8 | 31 | 0 | 0 | 0 |
| realizzt | 156 | 156 | 0 | 0 | 0 | 0 | 0 | 28 | 0 | 0 | 0 |
| retsu | 739 | 739 | 0 | 0 | 1 | 0 | 333 | 103 | 0 | 0 | 0 |
| rin | 710 | 710 | 0 | 0 | 3 | 0 | 196 | 75 | 0 | 0 | 0 |
| ryuji-rock | 129 | 129 | 0 | 0 | 15 | 0 | 0 | 0 | 0 | 0 | 7 |
| ryuji | 127 | 24 | 103 | 0 | 8 | 0 | 0 | 0 | 0 | 0 | 0 |
| ryusan | 211 | 211 | 0 | 0 | 0 | 0 | 0 | 103 | 1 | 0 | 0 |
| sakura | 764 | 764 | 0 | 0 | 0 | 0 | 153 | 84 | 0 | 0 | 0 |
| samura1 | 860 | 860 | 0 | 0 | 1 | 0 | 170 | 116 | 0 | 0 | 0 |
| scimitar | 362 | 361 | 1 | 57 | 1 | 0 | 0 | 50 | 0 | 0 | 0 |
| sf-akuma | 168 | 168 | 0 | 0 | 6 | 0 | 0 | 17 | 0 | 0 | 0 |
| sf-blanka | 37 | 37 | 0 | 0 | 6 | 0 | 0 | 0 | 0 | 0 | 0 |
| sf-cammy | 10 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| sf-chunli | 10 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| sf-dhalsim | 10 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| sf-guile | 11 | 0 | 11 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| sf-ken | 32 | 32 | 0 | 0 | 6 | 0 | 0 | 0 | 0 | 0 | 0 |
| sf-mbison | 12 | 0 | 12 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| sf-ryu | 34 | 34 | 0 | 0 | 6 | 0 | 0 | 0 | 0 | 0 | 0 |
| sf-sagat | 10 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| sf-vega | 36 | 36 | 0 | 0 | 4 | 0 | 0 | 0 | 0 | 0 | 0 |
| sf-zangief | 36 | 36 | 0 | 0 | 4 | 0 | 0 | 0 | 0 | 0 | 0 |
| sha | 785 | 785 | 0 | 0 | 0 | 0 | 153 | 84 | 0 | 0 | 0 |
| silvertongue | 508 | 508 | 0 | 0 | 1 | 0 | 0 | 42 | 0 | 0 | 0 |
| skull | 688 | 685 | 3 | 114 | 0 | 1 | 210 | 109 | 0 | 0 | 0 |
| slice | 486 | 486 | 0 | 0 | 2 | 0 | 0 | 45 | 0 | 0 | 0 |
| star | 908 | 908 | 0 | 0 | 6 | 0 | 233 | 134 | 0 | 0 | 0 |
| street-reign | 5 | 0 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| sunra | 139 | 139 | 0 | 0 | 0 | 0 | 0 | 13 | 0 | 0 | 0 |
| t3-anna | 743 | 743 | 0 | 0 | 1 | 0 | 346 | 158 | 0 | 0 | 0 |
| t3-bosconovitch | 266 | 266 | 0 | 0 | 0 | 0 | 0 | 67 | 0 | 0 | 0 |
| t3-eddy | 707 | 707 | 0 | 0 | 0 | 0 | 280 | 185 | 0 | 0 | 0 |
| t3-forestlaw | 102 | 102 | 0 | 0 | 0 | 0 | 0 | 13 | 0 | 0 | 0 |
| t3-gon | 151 | 151 | 0 | 0 | 0 | 0 | 0 | 31 | 0 | 0 | 0 |
| t3-hwoarang | 723 | 723 | 0 | 0 | 2 | 0 | 413 | 146 | 0 | 0 | 0 |
| t3-julia | 419 | 419 | 0 | 0 | 0 | 0 | 151 | 91 | 0 | 0 | 0 |
| t3-kuma | 530 | 530 | 0 | 0 | 3 | 0 | 171 | 108 | 0 | 0 | 0 |
| t3-law | 693 | 693 | 0 | 0 | 1 | 0 | 315 | 146 | 0 | 0 | 0 |
| t3-lei | 790 | 790 | 0 | 0 | 0 | 0 | 424 | 201 | 0 | 0 | 0 |
| t3-nina | 754 | 754 | 0 | 0 | 2 | 0 | 357 | 167 | 0 | 0 | 0 |
| t3-ogre | 161 | 161 | 0 | 0 | 0 | 0 | 0 | 35 | 0 | 0 | 0 |
| t3-paul | 497 | 497 | 0 | 0 | 2 | 0 | 222 | 71 | 0 | 0 | 0 |
| thor | 322 | 244 | 78 | 0 | 0 | 0 | 0 | 3 | 0 | 0 | 0 |
| tobi | 729 | 729 | 0 | 0 | 2 | 0 | 413 | 146 | 0 | 0 | 0 |
| torch | 892 | 892 | 0 | 0 | 0 | 0 | 236 | 155 | 0 | 0 | 0 |
| tou | 681 | 681 | 0 | 0 | 3 | 0 | 222 | 60 | 0 | 0 | 0 |
| vainabel | 60 | 10 | 50 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 |
| vega | 207 | 207 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| vf-akira | 20 | 3 | 17 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 0 |
| vf-elblaze | 28 | 0 | 28 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| vf-jeffry | 25 | 0 | 25 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| vf-kage | 14 | 4 | 10 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 |
| vf-leifei | 812 | 790 | 22 | 0 | 0 | 0 | 424 | 142 | 0 | 0 | 0 |
| vf-sarah | 14 | 4 | 10 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 |
| vf-wolf | 21 | 0 | 21 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| waterfall | 365 | 365 | 0 | 0 | 0 | 0 | 0 | 73 | 0 | 0 | 0 |
| yukihyo | 560 | 560 | 0 | 0 | 11 | 0 | 0 | 55 | 0 | 0 | 0 |
| zangief | 217 | 217 | 0 | 0 | 7 | 0 | 0 | 0 | 0 | 0 | 0 |
| zen | 644 | 644 | 0 | 0 | 0 | 0 | 0 | 72 | 0 | 0 | 0 |
| zui | 654 | 654 | 0 | 0 | 6 | 0 | 0 | 87 | 0 | 0 | 0 |
