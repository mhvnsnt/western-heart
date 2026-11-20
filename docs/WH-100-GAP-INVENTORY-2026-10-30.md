# WH-100 Gap Inventory — 2026-10-30

Owner order (2026-10-30 ~18:44 CDT): get Western Heart working 100% — a real fight
between ALL fighters with working movesets/animations, a working in-game
customization suite, building outward from that core using the teardown files.
Itch is explicitly out of scope. This doc is the burn-down list: every concrete
gap between today and that definition, each with verified evidence, the fill
source (owner's source order: Tekken teardowns first → his other Steam-library
game teardowns → modding community → open internet), and the lane that owns it.
It is updated as gaps close.

## Verification method (read this before quoting any number)

- Moveset totals were **re-verified by full re-parse** of all 163 files in
  `game/assets/movesets/` (129 moves-bearing, 56,527 moves) from the on-disk
  snapshot at main `1447e15` (PR #1262). Every headline figure from
  `docs/movesets/REAL-MOVES-AUDIT-2026-10-29.md` was reproduced exactly by an
  independent counter (see per-gap notes). Post-#1262, the only moveset changes
  on main are the provenance lane's Phase 1 `anim_t3` corrections (PRs
  #1266–#1291+), which shrink the guess-grade pool (F3) per-PR and do not touch
  the structural totals (F1/F2/F4).
- T7 clip-map totals (F1) and TTT2 supply totals (F10) were re-counted from
  current main (`e3e84a5`, PR #1291 merge) files on 2026-10-30.
- Fighter classification (which source each fighter may fill from) is owned by
  `docs/movesets/MOVESET-PROVENANCE-2026-10-30.md`: 34 files class 1-W
  (Phase 1 workable), 28 class 1-C (complete), 49 class 1-S (source-pending),
  6 class 2 (owner-approved mixes, untouched), 1 class 3 whole file plus named
  class-3 layers, 7 files + 3 extra items on the Owner Decision List
  (untouched), 34 DATA files.

## FIGHT gaps

| ID | Gap | Verified evidence | Fill source (in owner's order) | Owner lane |
|---|---|---|---|---|
| F1 | **256 of the 781 T7-join moves still unmapped** (525 mapped) — updated 2026-10-31 by the burn-down continuation lane, see Progress section | At inventory open: 481 mapped / 300 unmapped, re-counted exactly from `game/assets/anim/t7/clip-maps/*.json`. B2b/c then landed (PR #1311): requirements pool 29/39 resolved, ambiguous pool 1/91 resolved by the v2 graph (90 held with fingerprint scores recorded; the damage+startup fingerprint rule calibrated as unreliable — it would err on ~35% of known pools — so it promoted none on its own), +2 decided from the other pool. Buckets remaining: 81 T8-only candidates, 90 ambiguous-held, 10 requirement-held (per-entry diagnoses in the clip-maps), ~85 other-held. Continuation lane (2026-10-31): the v2 sequence/pass-through re-run over the 89-entry other-held pool promoted 11 (unique graph terminal + concrete clip locator) and recorded v2 findings on the 78 still held (PRs #1318, #1320-#1326, #1329); graph sanity = 48/48 sample re-derivation and 511/514 all-mapped membership; the ambiguous, requirement-held, and T8-only buckets were not touched by the re-run | T7/T8 teardowns first: T8 pieces for the 81; the v2 sequence/pass-through graph channels (proven in B2b/c) re-run systematically over the held pools is the named next pass | 81 → T8 community-pull lane (running). Held pools → named follow-up from this lane's B2 (see Progress) |
| F2 | **31 moves are move-mapped but their clips sit in the un-located bank-0x0000 file** — hunt COMPLETE at lane close: the bank is NOT held anywhere in GRE; see Progress | B2a census (GRE PR #75, merged): all 58 mask archives (343 sections, 63,104 entries), the rest of tkdata, pakchunk0_P, and pakchunk1/decrypted (8,392 entries, zero mothead paths) — bank 0 is absent; the 31 targets are ordinary attack anims at keys 101–121, fully listed in the hunt doc. Prime suspect: `pakchunk1_P-WindowsNoEditor.pak` (18.2 GB, never extracted) | A vault-flow-capable lane (or the owner's Steam Guard tap) pulls pakchunk1_P's FILE LIST first, then the bank file; runtime-trace spec is written in the hunt doc as the parallel path | **Blocked on the vault/Steam-Guard step** — named for the parent; no locators fabricated |
| F3 | **12,684 of 30,291 `anim_t3` mappings are guess-grade** (10,221 `nearest (approximate)` + 2,463 `same-notation`) | Re-verified exactly by re-parse. Per-fighter distribution in the provenance doc | Each fighter's own T3 bank branch graph (branch-walk proofs). Stance/directional first steps mostly do NOT prove yet — their T3 identity runs through branch **condition codes that are not decoded**; that decode is the named unblocking research | Guess-grade corrections → provenance lane Phase 1 (34 1-W files; PRs landing now). Condition-code decode → un-owned research, named here |
| F4 | **7,032 moves carry donor/stand-in marks in the data** (6,782 with a `donor_fighter` key) | Re-verified exactly (donor 6,782 + standin/fallback/placeholder/generic = 7,032). Worst: kronos-attire2 2,458 (class 2, approved — stays), koreshi 751, kronos 650 (class 2, approved — stays), demonio-human 581 (self-inheritance, not foreign) | Provenance rules: class 2 stays; class-3 layers (koreshi 312-move Yoshimitsu layer, demonio 34 devil_jin rows, gyou 47 paul rows) replaced from each fighter's own source in Phase 2; what the own source lacks stays UNMAPPED by name | Provenance lane (Phase 2, after Phase 1) |
| F5 | **453 moves have no anim mapping of any kind** — updated at lane close (was 487: 476 with no row at all + 11 with a bare `t3_row` only) | Re-verified at inventory open with the definitional split resolved (476 + 11 = the audit's 487 exactly). B1 then wired 34 of them from the decoded TTT2 layer (megami 15 of 20, menajerii 19 of 51). Remainder concentrated in 1-S files: baek-master-white 153/291, pond 151/620, thor 78/322, menajerii 32, megami 5. TRIAGE LANDED 2026-10-31 (PR #1316, `docs/movesets/F5-NO-ANIM-TRIAGE-2026-10-30.md`): recount confirms 453 = 442 strict + 11 bare-t3_row; megami 5 + menajerii 32 re-examined under the strict B1 method — zero fills, all stay UNMAPPED by name with per-move reasons; baek-master-white and pond are class 1-S, so their TTT2 joins were analyzed but NOT applied (baek-master-white 35 unique / 1 ambiguous / 117 none against bae.json; pond 50 unique / 13 ambiguous / 88 none against rav.json); thor is Tekken Ganryu class 1-S (not DOA/VF) — blocker: no decoded Ganryu fight motion bank in-repo (T6 STFS lane or the walk-verified T7 motbin input-key join). Remainder stands at 453 | Each fighter's own source: T7 Steam extraction preferred for T7 bases (pond/Raven, baek-master-white/Baek), DOA/VF programs for the DOA/VF data files | Source lanes per fighter |
| F6 | **184 strike/throw identity mismatches** (175 moves carry throw flags with a non-throw class; 9 strike-class moves point at named throw anims) | 175 re-verified exactly. The 9 verified under the audit's strike-class-only definition (kingtyrant ×3 + scimitar/star sets); a wider net finds 16 including special-class `throw_escape` entries — definitional, recorded here so nobody quotes 16 | Settling source is each bank's `hit_frames.json` throw flags (held, in-repo) + own-bank anim replacement where the anim itself is wrong. SETTLED 2026-10-31 (continuation lane): 84 corrected (78 same-bank throw re-picks settled on hit_frames throw flags + rows.pack playability, plus 6 move_class fixes), 46 settled-consistent with evidence and no change, 37 held (11 repick-ambiguous with tied candidates recorded; 26 in banks with no data held in-repo: baek/dxmmii/demonio), 17 owner-gated and untouched (star x3, cainelias x4, demonio-winged x10). Full record: `docs/movesets/F6-THROW-SETTLEMENT-2026-10-30.md` (PRs #1315-#1362, doc #1363, scimitar #1364, addendum #1365). Post-settlement census: every non-gated, non-held entry with a bank row points at a hit_frames throw=1 row | Settled by the continuation lane (2026-10-31) |
| F7 | **13 No Mercy-sourced rows are SUSPECT** (wrong FileTable window extraction) | Re-verified exactly: cainelias ×5 pointing at wrong-window bank clips; ryuji-rock ×7 Rock specials (refs `mk:MK-*` named "(NO MERCY)"); negativo's `u/f+1+2` is a move NAME only (ref `t7:negan:`), not NM-sourced | True-window re-extraction of the No Mercy banks (separate owed program). The ryuji-rock seven are additionally gated on the owner's Dolphin Route 3 call; cainelias's base choice is Owner Decision List item 8 | Flagged, NOT fixed — NM re-extraction program + owner items. No lane edits these rows meanwhile |
| F8 | **4 strings whose notation has no move entry** (orphan strings) | Re-verified: chatur `d/b+1,2` and `1,2,1+2`; pond `MIST 1,2`; ryusan `WR f,f,F (Mid Screen)`. (A rawer counter finds 7 first-step misses; the 3 extra burger-file strings resolve through their `hits` arrays and are NOT orphans — definitional, resolved) | chatur's two from the T3 Ogre branch graph (held); pond/ryusan stay UNMAPPED by name until their T7 sources (Raven / Lucky Chloe) land | chatur CHECKED at lane close: the Ogre graph's rows carry no notation labels (branches encode Tekken button-code commands with condition fields), so proving the follow-up rows needs the branch-walk proof machinery — anchors recorded: `d/b+1` = row 127, the `1,2,1` chain ends at row 56. Both strings stay UNMAPPED by name; unblock = the branch-walk/condition-code research (same family as F3). pond/ryusan → source-pending |
| F9 | **Pantera step-plan REVIEW candidates (57) not promoted**; 41 step occurrences UNMAPPED by name | PR #1232 record: last-step verified 11 / review 25 / unmapped 24 across 60 keys; promotion requires the FK soft gate + play-verify video | T3 King branch graph (held) for data; video evidence from the play-verify lane | Play-verify lane (video, running) + provenance lane (data). Not this lane |
| F10 | **TTT2 integration: megami + menajerii CONSUMED at lane close**; buffalo-bill application is the remaining step | Supply re-counted at current main: `game/assets/ttt2/` = 57 character files, **6,559 records exactly** (6,122 moves + 399 sample combos + 38 stance separators), each with `anim_ref` `ttt2:{char}:row:{n}`. B1 wired megami (15 fills) and menajerii (19 fills) from their own characters' records (PRs #1306/#1307, merged + deployed); the buffalo-bill join table (PR #1309) stands at 76 unique / 29 ambiguous / 22 unmatched-by-name, and the provenance Law-group correction it was sequenced behind has landed. APPLICATION LANDED 2026-10-31 (PR #1317): all 76 unique matches recorded in buffalo-bill.json as ttt2_ref cross-references on 206 entries plus a ttt2_integration section (no existing anim_ref displaced — every entry already carried one); the 29 ambiguous and 22 unmatched stay untouched and UNMAPPED by name. Disclosed overlap: TTT2 rows 82/83 share the same two entry keys; the entries carry row 82 and both rows are recorded in the integration section | The TTT2 layer itself (held, in-repo) | **DONE 2026-10-31 (continuation lane, PR #1317)** |
| F11 | **T7 format-100 (0x64) clip bodies not yet convertible** — the 450 byte-exact-located clips cannot play in-engine until the rotation convention is solved; format-200 (0xC8) bodies ARE decoded | PR #1281 (merged): probe tool + findings — hinge axis solved (bind-local Y, sign flips between formats), per-bone basis fit not settled; King's stance is a 0xC8 clip (`nakg_kg2kam`) | Modding-community tooling (Kiloutre path) + the game's own skeleton data (held) | Claude Code session (research, running) + 0xC8 stance-bake lane (running). This lane consumes the result when it lands |
| F12 | **Hit-reaction coverage: 17,500 of 47,987 damaging strikes (36.5%) can pick their own T3 hit reaction; the rest fall back to the generic hit/launch clips** — first reactions audit (owner I-lane, 2026-10-31); full record in the F12 detail section at the end of this doc | Re-parse of all 129 moves-bearing files (56,527 moves) against the engine's own rules (`game/js/fighter.js` `_pickReaction`, `game/js/t3-reaction-select.js`), classifier cross-verified 24/24 against the shipped `selectReactionSlot` run under node. Remainder: 27,904 strikes carry no `t3_row` at all (12,912 of them hold a pickable row in their own `anim_t3` — 0 at proven grades; the proven-grade slice was wired 2026-10-31, see follow-up 1 in the F12 detail section); 1,211 strikes' `t3_row` misses their bound bank's reaction table (zen 570 of 570 — bank UNMAPPED by owner decision); 21 chatur string moves carry list-valued `t3_row` the pick can never match; 1,807 picks read the bound bank's row at an index authored for another bank (proxy tables). Verified complete, NOT gaps: reaction packs baked 7,368/7,368 slots across all 22 banks; zero dangling reaction indexes among 18,371 referenced rows; zero picked slots undefined in any bank | Proven-grade `t3_row` wiring DONE 2026-10-31 (65 per-fighter PRs, #1380-#1456, 2,120 strikes, coverage 32.1% -> 36.5%); mid/guess grades stay in the F3 pool; rebuild proxy-table rows on the bound bank (moveset lane); zen stays gated on the owner's Zen base call / the private Dural bank | Moveset/provenance lane (follow-ups logged in the F12 detail section). This audit changed no moveset data; the follow-up wiring lane's 65 PRs did (F12 detail, follow-up 1) |

## CUSTOMIZATION gaps

| ID | Gap | Verified evidence | Fill source | Owner lane |
|---|---|---|---|---|
| C1 | **Anatomy-layer data exists for 1 of 73 roster fighters** — `game/js/xray.js` loads `roster/<fighter>/anatomy/anatomy-layers.json` per fighter; only Pantera's exists; Demonio's fetch 404'd in the Oct-25 play run | Counted on current main: exactly 1 `anatomy-layers.json` in the repo (`roster/pantera/anatomy/`); 73 roster dirs | The held spec `docs/research/ANATOMY-LAYERS-SPEC-2026-10-23.md` + per-fighter models (held) — data derived from the fighters' own models, not invented | **This lane (queued after B1–B3)** |
| C2 | **Parts catalog holes**: Def Jam parts are preview-only; T7 contributes a skull mask only; DOA parts not in catalogs; WWE 2K parts not held | Standing verified state (Oct-21 fighter-completeness pass) against `customization/` on current main: `parts/` 4,300 files, `parts-converted/` 5,189 files; create-fighter `PARTS-INDEX.json` totals 7,960 parts from 7 sources | The respective teardown/converter programs (Def Jam converter, DOA extraction, T7 pakchunk — PR #863 open) | Those programs; this lane inventories only |
| C3 | **Suite flow unfinished**: Mixamo Soldier still in the create-fighter flow, templates/nested menus/universal rigs unwired | PR #1057 open (Creation Suite rework, another lane). Suite-layout lane is parked `needs_owner` (re-arm-or-park is already an open owner item) | In-repo code + held templates | PR #1057's lane; layout = owner item already on his list |
| C4 | **Customized-fighter-in-fight on the CURRENT build is not yet re-verified** — the in-fight consumer was wired Oct-21 (PRs #444/#461: 58 roster fighters resolve models on both loading paths; Creation Suite consumer live) | Wiring state from merged PRs; current-build behavior evidence is being produced now | — (verification, not a fill) | Play-verify lane (running) + WH triage chat |
| C5 | **Eye library is thin**: 5 files in `customization/eye-library/` | Counted on current main. (The Oct-25 missing `eye-classic-original.png` now exists — see L3) | Held face/texture extractions (T7 pakchunk, Tripo intakes) | **This lane (queued, low priority)** |

## CORE LOOP gaps

| ID | Gap | Verified evidence | Fill source | Owner lane |
|---|---|---|---|---|
| L1 | **Load time ~126 s** (Oct-25 play run) — too slow for a player loop | Oct-25 run record; current-build measurement is being taken by the play-verify lane now | Asset-base/deploy mechanism (republish path documented in PR #1282) + lazy loading | Play-verify lane (evidence) + deploy lane (mechanism) |
| L2 | **FREE CAMERA overlay overlaps the top-right meter** | Oct-25 run record; code at `game/js/free-camera.js`, `game/js/scene.js`, `game/js/main.js` on current main | In-repo UI code | WH triage chat (owns UI fixes; not duplicated here) |
| L3 | **Oct-25 missing assets: 2 of 4 resolved, 1 stale, 1 open** | Re-checked on current main: `customization/parts/no-mercy/glb/body_parts/model_1171.glb` EXISTS; `customization/eye-library/eye-classic-original.png` EXISTS; `intro-interactions.js` has NO reference anywhere in current `game/js/` (stale path from the pre-restructure build — closed as stale); `roster/demonio/anatomy/anatomy-layers.json` still missing → that is C1 | — | Closed here except C1 |
| L4 | **Deployable build currency** — was frozen on the Oct-24 build | FIXED 2026-10-30: live build at main `adf15d61` (2,068 files, 18 bundled models verified live), republish path documented (PR #1282). Itch upload is OUT of scope per the owner's 2026-10-30 order | — | Deploy lane (done); every lane republishes via the documented path |

## CONTENT gaps (TTT2 extraction remainders that block fighter/stage use)

| ID | Gap | Evidence | Owner lane |
|---|---|---|---|
| T1 | data001 NTXR per-texture extraction (joins the data002 NSXR texture program) — decoded stream held (`decoded-data001-full.bin`, 851,749,584 B, sha-verified), textures not yet split per-file | PR #1262 decode record; checkpoint `ttt2-resume-100.json` (running) | TTT2 lane |
| T2 | data028 NUS3BANK per-clip audio extraction — decoded stream held (120,285,856 B, sha-verified) | Same | TTT2 lane |
| T3 | BXML node-tree decode; data004 MOTA full parse; data000 PCTB/MCAM gap + menu-script region; per-character model/anim container mapping (data007–017/025/027/034–047) | Same. These gate TTT2-native animation playback; the MVLT move-list layer (F10) is complete independently | TTT2 lane |

## Owner decisions that gate specific gaps (already enumerated — not re-asked here)

The provenance doc's Owner Decision List gates: star (base: Christie vs Xiaoyu
data), byou (base unrecorded), jin_soul (identity), demonio-winged (Devil Jin
layer), gyou-spirit-body (base), charger ×2 (base), street-reign (existence +
base), cainelias (base — also gates F7's cainelias five), Echo (copy-moveset
existence), koreshi Phase 2 (confirmation reading). Those fighters stay
untouched until the owner rules. Full text:
`docs/movesets/MOVESET-PROVENANCE-2026-10-30.md`, "Owner Decision List".

## Burn-down summary (gap units at inventory open, 2026-10-30)

| Pool | Units | Owned by |
|---|---|---|
| T7-join unmapped moves | 256 (updated 2026-10-31; was 267) | T8-only pool -> T8 lane; ambiguous (90) + requirement-held (10) untouched; other-held pool re-run DONE 2026-10-31 (11 promoted, 78 held with v2 findings) (F1) |
| Mapped moves with un-located clips (bank-0x0000) | 31 | Blocked: vault-flow pakchunk1_P pull (F2) |
| No-anim moves | 453 (triage landed 2026-10-31, PR #1316; zero fills — remainder stands, pools are 1-S/source-gated) | Source lanes per fighter (F5) |
| Guess-grade `anim_t3` | 12,684 (shrinking per provenance PR) | Provenance Phase 1 (F3) |
| Donor-marked moves awaiting Phase 2 replacement | 439 class-3 layer rows (312 + 34 + 47 + residues) of 7,032 marked (rest = approved class 2 / self-inheritance) | Provenance Phase 2 (F4) |
| Throw-identity mismatches | 184 SETTLED 2026-10-31: 84 corrected / 46 settled-consistent / 37 held / 17 owner-gated | Continuation lane (F6) |
| SUSPECT No Mercy rows | 13 | Blocked: re-extraction program + owner items (F7) |
| Orphan strings | 4 (2 fillable now) | This lane / source-pending (F8) |
| TTT2-source fighters unwired | 0 — megami + menajerii WIRED at lane close (PRs #1306/#1307, deployed); buffalo-bill join table landed (#1309) and the provenance Law group has since landed, and the TTT2 application LANDED 2026-10-31 (PR #1317: 76 unique matches cross-referenced on 206 entries) | Continuation lane (F10) |
| Fighters missing anatomy data | 72 of 73 | This lane, queued (C1) |
| Roster rig-audit coverage | 66 of 247 GLBs audited at lane close (1 clean PASS, 3 PASS-after-fix, 39 FAIL, 19 AUDIT-ERROR, 20 deferred-for-size, 165 not-yet) — full table in `docs/RIG-AUDIT-SWEEP-2026-10-30.md` (PR #1312) | **This lane (B3)** — Baek fix landed (PR #1313); next fix target: demonio bloodline-ember (37.875% contamination); meshopt decode stage is the named blocker for 17 AUDIT-ERROR rigs |

## This lane's execution order

B1 — TTT2 fighter integration (F10, plus chatur's F8 strings). **DONE at lane close.**
B2 — T7 follow-ons: bank-0x0000 hunt (F2), requirements-table decode (F1-39),
fingerprint pass over the ambiguous pools (F1-91), re-examination of the 89. **DONE at lane close.**
B3 — Full-roster rig batch (skin_audit sweep + per-character fix PRs, Baek first). **DONE at lane close (sweep + first fix).**
Then F6 and C1/C5 as the queue clears. Every landed piece republishes the
deployable build via the PR #1282 path. Progress updates land in this doc.

## Progress — 2026-10-30 lane close (WH-100 burn-down, first pass)

Landed and deployed (live build manifest = main `a3ef5e60` at this update's
writing, 2,082 files / 961,665,599 B, spot sizes verified):

- **B1 (PRs #1306, #1307, #1309 — merged + deployed).** Megami: 15 of 20
  no-anim moves wired to Jun's decoded TTT2 records; 5 UNMAPPED by name.
  Menajerii: 19 of 51 wired to Roger Jr.'s records (6 are notation-unique
  matches whose document-sourced names differ from the game's MVLT names —
  disclosed per-fill in PR #1307); 32 UNMAPPED by name. Buffalo-bill join
  table: 76 unique / 29 ambiguous / 22 unmatched-by-name. Chatur: checked,
  stays UNMAPPED by name (anchors + unblock recorded in F8).
- **B2a (GRE PR #75 — merged).** Bank-0x0000 hunt: full census, bank proven
  NOT held in GRE; the 31 targets are named in
  `teardown/tekken7-steam/tkdata/mothead/mask/BANK-0000-HUNT-2026-10-30.md`
  (GRE) with the pakchunk1_P gate and a runtime-trace spec. F2 is blocked on
  a vault-flow Steam pull, named for the parent — not on research.
- **B2b/c (GRE PR #76 + WH PR #1311 — merged + deployed).** Requirements
  table DECODED (flat `(condition, param)` rows, runs terminated by
  condition 881; decode doc + `t7_req_graph.py` on GRE). The v2 cancel
  graph (input-sequence commands + pass-through auto-cancels + bound-class
  terminals restored) re-derived 479/481 prior mappings identically and
  resolved 29 of the 39 requirement-gated moves; 10 held with per-entry
  diagnoses. Ambiguous pool: fingerprint pass scored all 91 but promoted
  none by itself — calibration on known pools showed a unique-exact
  damage+startup rule errs ~35% (WH frame data diverges systematically
  from motbin), so fingerprints served as corroboration only; 1 pool move
  resolved by the v2 graph, 90 held with scores recorded. **Net F1:
  514 mapped / 267 unmapped (was 481/300).** One open adjudication:
  pantera `f,f,n,1+2` (Lay Off) — the mapped Co_Fcross kept; the v2 graph
  surfaces Kg_BodyAt00 as a competitor and WH startup (9) matches BodyAt00;
  flagged in the clip-map and `game/assets/anim/t7/INDEX.json` for a
  decider with better evidence. Named follow-up: re-run the v2
  sequence/pass-through channels systematically over the ~85 "other" held
  pool (only 4 incidental resolutions were taken there, per scope).
- **B3 (PRs #1312, #1313 — merged).** Baek: all 3 skinned master-white GLBs
  FAIL→PASS (dead Hand joints revived; contamination 0.083–0.087% →
  0.001–0.003%; weights only; fix record in
  `docs/handoffs/RIGFIX-BAEK-2026-10-30.md`). The Oct-29 proof file is
  `game/assets/models/baek.glb` (byte-identical on main, same failure —
  the identical cleanup applies; game-assets scope, flagged in the record).
  Sweep: 66/247 roster GLBs audited (`docs/RIG-AUDIT-SWEEP-2026-10-30.md`)
  — next fix target demonio bloodline-ember (37.875% contamination, dead
  leg joints); the meshopt decode stage is the named blocker for 17
  AUDIT-ERROR rigs (incl. Baek attire1, which decodes to 1.6M verts and
  times out the pure-Python audit); deathfang attire3 needs a skeleton
  rename/retemplate stage, not weight cleanup (cleanup attempt recorded,
  0 verts revived).

Player-visible deltas from this pass: Megami and Menajerii now play 34 more
of their real moves with their own characters' TTT2 animations; 33 more T7
moves across 8 fighters have proven clip identities in the clip-maps (the
0x64 conversion, F11, is what turns located clips into in-engine playback);
Baek's in-game models carry fixed hand weights; Pantera's real T7 King
stance (landed by the 0xC8 lane, PRs #1296/#1300) is on the live build.

Still open after this pass (owners in the tables above): F1 held pools
(256 after the 2026-10-31 continuation), F2 (31, vault-gated), F3 (provenance Phase 1 + condition-code
research), F4 (provenance Phase 2), F5 remainder (453, triage landed 2026-10-31 — pools are 1-S/source-gated), F6 SETTLED 2026-10-31 (184: 84 corrected / 46 settled-consistent / 37 held / 17 owner-gated), F7 (13, blocked on the NM program + owner items), F9, F11, C1–C5,
L1–L2, T1–T3.

## Progress — 2026-10-31 burn-down continuation lane

All four queued items worked; every count below was re-verified by the
coordinator by re-parse against final main after the merges.

- **F6 (throw mismatches) — SETTLED.** 84 corrected (78 deterministic
  same-bank throw re-picks: same attack-class/button profile as the prior
  row, hit_frames throw=1, present in the bank rows.pack, closest
  stream_frames with a unique minimum required, signature twins taking
  their P+K primary's pick; plus 6 move_class strike->throw fixes —
  kingtyrant x3 with an eddy 26->148 re-pick, scimitar x3 class-only),
  46 settled-consistent with evidence and no change, 37 held (11
  repick-ambiguous with tied candidates recorded; 26 in the baek/dxmmii/
  demonio banks, which hold no data in-repo), 17 owner-gated and untouched
  (star x3, cainelias x4, demonio-winged x10). PRs #1315, #1319, #1327,
  #1328, #1330-#1337, #1339-#1362 (35 per-file), settlement doc #1363,
  scimitar moves-scoped pass #1364, addendum #1365. Record:
  `docs/movesets/F6-THROW-SETTLEMENT-2026-10-30.md`.
- **F10 (Buffalo Bill x Law) — APPLICATION LANDED.** PR #1317: the 76
  unique join matches recorded as ttt2_ref cross-references on 206
  entries plus a ttt2_integration section; 29 ambiguous and 22 unmatched
  untouched (UNMAPPED by name). No anim_ref was displaced anywhere.
- **F1 (T7 join) — v2 re-run DONE.** PRs #1318, #1320-#1326, #1329: the
  sequence/pass-through channels run systematically over the 89-entry
  other-held pool — 11 promoted with graph-unique terminals and concrete
  clip locators, 78 held with v2 findings recorded in the clip-maps.
  Graph sanity: 48/48 sample re-derivation, 511/514 all-mapped
  membership. **Net F1: 525 mapped / 256 unmapped (was 514/267).**
- **F5 (no-anim) — TRIAGE LANDED, remainder stands at 453.** PR #1316
  (`docs/movesets/F5-NO-ANIM-TRIAGE-2026-10-30.md`): 453 = 442 strict +
  11 bare-t3_row; megami/menajerii remainders re-examined — zero fills;
  baek-master-white/pond TTT2 joins analyzed, NOT applied (class 1-S);
  thor's blocker named (no decoded Ganryu motion bank in-repo).

Deployable build: this lane's merges are game data (movesets, clip-maps)
plus docs on main. The republish step itself was not executed by this
lane and is flagged for the parent/deploy lane — the next republish
carries all of it, and the live manifest should then read the main
commit that includes PR #1365.

## F12 detail — hit-reaction coverage audit (2026-10-31, owner I-lane "reactions")

**Update (2026-10-31, I follow-up wiring lane):** follow-up 1 below is DONE —
the proven-grade slice of G-R1 was wired (65 per-fighter PRs, #1380–#1456;
2,120 strikes). All counts in this section were re-measured with
`tools/audit_reactions.py` on main `104d9c9a`: damaging-strike picks
15,380 (32.1%) -> **17,500 (36.5%)**; strikes with no `t3_row`
30,024 -> 27,904; proven-grade fillable remainder 0. The closing re-run
reproduced the audit's verified-complete results (reaction packs complete,
zero dangling reaction indexes). G-R2/G-R3/G-R4 are unchanged; G-R5's
proxy-pick count rose during the day from other lanes' merges and is
restated as measured.

### What the engine actually requires (read from the shipped code, main `f2137c06`)

A defender ALWAYS reacts at the state level: `receiveHit` in `game/js/fighter.js`
puts it into block / hitstun / knockdown, and the state machine plays the generic
bank clips (`hit` for hitstun, `launch` for knockdown — fighter.js animation
switch, hitstun/knockdown cases) or a procedural fallback when no bank is bound.
The MOVE-SPECIFIC T3 reaction — the stagger/counter/down/air reaction T3 picked
for that exact move — is a separate pick, `_pickReaction` (fighter.js), and it
needs ALL of:

1. `game/assets/anim/t3/reactions.json` loaded (633 records x 21 words, 22 bank
   tables, 34 common rows; fetched by `ensureT3Reactions` in
   `game/js/t3anims.js`).
2. The attacking move to carry `t3_row` (moveset field `t3_row`, surfaced as
   `move.t3row` by `getRealMove` in fighter.js).
3. That row to exist in the ATTACKER's bound bank table
   (`bankIdFor(charId, movesetId)` in fighter.js resolves the bound bank:
   FIGHTER_BANK overrides, else the moveset index's `anim_bank`/`t3_source`
   through `SOURCE_TO_BANK` in t3anims.js) or in `common_rows`.
4. The row to survive `selectReactionSlot` (`game/js/t3-reaction-select.js`):
   attack class 1/3 never reacts; class 2 reacts only on a grounded standing
   defender; a reaction value of 0 or in the 0x1nnn range picks nothing
   (0x1nnn acts only through a throw).
5. For playback, the picked slot to be defined in the defender's or attacker's
   bank slot table (`reactionSlotBank`) and baked in that bank's
   `reactions.pack.json` (`loadT3ReactionClip` in t3anims.js); otherwise the
   generic clip plays.

Throws are a separate system (throw-pair clips via `game/js/t3-throw.js` and
the banks' throw tables), not strike reactions; the 5,110 throw-class moves
are excluded from the strike coverage below.

### Method

`tools/audit_reactions.py` (landed with this section) re-parses all 129
moves-bearing files in `game/assets/movesets/` (56,527 moves — the same
census this inventory's verification method reproduces), replicates
`bankIdFor` and the `selectReactionSlot` decision order exactly, and
classifies every move. The classifier was cross-verified against the shipped
`selectReactionSlot` itself, run under node on 24 sampled moves spanning
every class: 24/24 agree. Playback completeness was checked against the
per-bank `coverage` block inside reactions.json and spot-verified against a
real pack file (king_on_pantera_leoman: pack rows 568 = slot table 568,
0 missing). Population exclusions, with cause: `index.json`,
`ur-native-index.json`, `t3_input_tables.json` (index/table files) and the
31 `ur-charNNN.json` files (schema-2 Urban Reign native banks — no `moves`
dict, no `t3_row` fields, and no reference in fighter.js/characters.js; they
are not wired fighters in this engine).

### Headline counts

| Pool | Count |
|---|---|
| Moves total (129 files) | 56,527 |
| Damaging strikes (damage > 0, not throw-class) | 47,987 |
| Damaging strikes that pick their own T3 reaction | **17,500 (36.5%)** |
| — of those, picks reading the bound bank's row at an index authored for a different source bank (proxy tables; a reaction plays, but it is T3's reaction for another move) | 1,807 |
| Damaging strikes with no `t3_row` at all | 27,904 |
| Damaging strikes whose `t3_row` misses the bound bank table and `common_rows` | 1,211 |
| Damaging strikes pointing at a throw-range reaction value (by T3 design — they act through the throw system, not the strike pick) | 1,338 |
| Damaging strikes on never-react attack-class rows (by T3 design) | 34 |
| Moves with list-valued `t3_row` (all in chatur.json) | 21 |

### Verified complete — NOT gaps

- **Reaction packs: 7,368 of 7,368 slots baked across all 22 bank dirs**
  (per-bank `coverage` in reactions.json: wanted = baked, missing = 0 for
  every bank; spot-verified on king_on_pantera_leoman above). Every bank dir
  in reactions.json also has its `reactions.pack.json` on disk (22/22).
- **Zero dangling data:** of 18,371 moves whose `t3_row` resolves to a table
  row, zero reference a missing reaction record, zero carry a reaction value
  of 0, and zero picked front slots are undefined in every bank's slot table.
- **Attack-class distribution** of referenced rows: class 0 = 17,659,
  class 1 = 712, class 2 = 0 (the grounded-only class never occurs in the
  wired data), class 3 = 0.
- Air reactions (6 kinds), the KO collapse slot (3430) and the throw-victim
  slot table (418 entries) ship in reactions.json; per-bank coverage records
  throw/victim clips complete alongside the strike slots.

### The gaps, named

**G-R1 — no `t3_row` (27,904 damaging strikes).** The move can land and the
defender plays the generic clip, but no move-specific reaction can ever be
picked. Split by what the fighter's OWN data already holds (the move's
`anim_t3` clip mapping, in the bound bank, pointing at a pickable row):
0 strikes remain at proven grades (`true-map branch-graph` / `true-map exact` /
`class-verified remap`) — the audit found 2,098; re-measured at wiring time
the slice was 2,120 (the G lane's pantera corrections had added 18 and 4
late fills surfaced in kai/kingtyrant), and all 2,120 were wired
2026-10-31 (follow-up 1 below); 4,500 at mid grades (`true-map class+limb`,
`true-map class-only`, `true-map input+class`, `same-notation`); 8,412 at
guess grade (`nearest limb/class/startup` — the F3 pool's standard applies:
not landable without branch-walk proof); 9,985 whose `anim_t3` sits in a
different bank than the bound bank (the pick reads the bound bank only);
428 whose own anim row is itself not pickable; 4,579 with no `anim_t3` at
all. Worst files by no-row strikes: kronos-attire2 1,292 of 1,412,
koreshi 722 of 850, demonio-winged 613 of 937, gyou 512 of 901,
phantom 552 of 883, jin_soul 570 of 864, byou 521 of 661, star 490 of 790.

**G-R2 — `t3_row` misses the bound bank's table (1,410 moves / 1,211
strikes).** The row index was authored against a different table than the
one the engine reads. Largest: zen 644 of 644 (its `t3_row` values are
synthetic 20000-series ids, e.g. `1` -> 20000, `2` -> 20099, and zen's bank
is UNMAPPED by the owner's 2026-10-24 decision — public builds get no
specific reactions for zen; the private Dural bank carries its own tables
and is not auditable from the public tree), nightwolf 68 (e.g. `3` -> row
278, `1+3` -> row 361 against the bound julia table), kai 63, doc-frank-
machine-shop 62, rave 57, koreshi 54, awapop 52, gyou 46, doc-frank-hood /
doc-frank-wowomomo / doc-frank-frankenstein 40 each, torch 27, chatur 25,
buffalo-bill 25, kingtyrant 24, tou 20.

**G-R3 — list-valued `t3_row` (21 moves, all chatur).** `_pickReaction`
uses the raw value as the table key; a list keys as "38,50" and can never
match, so these strings never pick — while the clip path (`_ownRow`) plays
the LAST element's row. All 21 last rows are pickable in chatur's bound
ogre table:

| File | Move | `t3_row` | Last row pickable |
|---|---|---|---|
| chatur | 1,2 | [38, 50] | yes |
| chatur | 3,4 | [57, 74] | yes |
| chatur | 2,2 | [50, 101] | yes |
| chatur | f+2,2 | [110, 153] | yes |
| chatur | f+4,4 | [106, 165] | yes |
| chatur | 3,3 | [57, 166] | yes |
| chatur | d/f+3,3 | [135, 195] | yes |
| chatur | d+4,3 | [131, 194] | yes |
| chatur | b+3,3 | [182, 198] | yes |
| chatur | f+3,3 | [191, 201] | yes |
| chatur | d/f+3+4,3+4 | [124, 137] | yes |
| chatur | 1,1 | [38, 120] | yes |
| chatur | 2,3 | [50, 118] | yes |
| chatur | u+3,3 | [54, 200] | yes |
| chatur | 1,2,1 | [38, 50, 56] | yes |
| chatur | 3,4,3 | [57, 74, 58] | yes |
| chatur | f+1,1 | [189, 59] | yes |
| chatur | f+2,1 | [110, 60] | yes |
| chatur | f+4,3 | [106, 61] | yes |
| chatur | d/f+2,1 | [114, 62] | yes |
| chatur | b+2,1 | [112, 63] | yes |

**G-R4 — fighters with no bound T3 bank (29 files).** `bankIdFor` returns
null, so their moves can only ever pick through `common_rows` (none of
their rows hit it) and their defenders resolve slots from the attacker's
bank only: burger-demon (466 moves), burger-speed-demon (454),
burger-the-mouth (454), mariposa (372), megami (304 — class 1-S,
source-pending, see F5), pond (620 — class 1-S, see F5), ryuji (127),
ryusan (211), vainabel (60), street-reign (5 — Owner Decision List item,
existence unruled; audited read-only), zen (644 — owner-decided UNMAPPED,
see G-R2), and the DOA/SF/VF guest data files (doa-ayane/bass/hayabusa/
jannlee/kasumi/tina, sf-cammy/chunli/dhalsim/guile/mbison/sagat,
vf-akira/elblaze/jeffry/kage/sarah/wolf — 18 files, 10-28 moves each;
their home-game reaction data is not T3 data and no T3 bank binds them).

**G-R5 — proxy-table picks (1,889 moves / 1,807 strikes).** For fighters
whose moveset data was built on a proxy source's table but who bind a
different canon bank (awapop, torch, kai, gyou, rave, koreshi and others),
the pick reads the BOUND bank's row at the source bank's index: a reaction
plays, but it is the reaction T3 assigned to a different move. Counted
separately from missing coverage; the fix is the moveset lane's
rebuild-on-true-base work already described in fighter.js's `bankIdFor`
comments. Strike picks on the fighter's own table: 17,500 - 1,807 =
15,693 (32.7%).

### Follow-ups logged (own-data fillable; NOT fixed by this audit)

1. **Wire `t3_row` from each fighter's own proven-grade `anim_t3`** —
   **DONE 2026-10-31** (I follow-up lane): 2,120 damaging strikes wired
   across 65 per-fighter PRs (#1380-#1456), one file per PR, additions
   only. Every wired row was verified pickable by the shipped
   `selectReactionSlot` under node before landing (2,120/2,120).
   Closing audit re-run (main `104d9c9a`): coverage 15,380 (32.1%) ->
   17,500 (36.5%); proven-grade remainder 0. Mid grades (4,500) after
   branch-walk proof; guess grades (8,412) stay in the F3 pool until
   proven.
2. **Chatur's 21 list-valued `t3_row`** — decide the reaction row per
   string (the clip convention is the last row; all 21 pickable) in the
   moveset lane, noting per-step picks are the full form under the
   step-plan engine.
3. **Rebuild proxy-table `t3_row` values on the bound bank's table**
   (G-R2/G-R5 files: nightwolf, kai, rave, koreshi, awapop, gyou, torch,
   the doc-frank formes, tou, kingtyrant, chatur, buffalo-bill) —
   per-fighter, moveset lane, same family as F3/F4.
4. **zen** stays as-is until the owner's Zen base call or the private
   Dural bank lands in public builds (G-R2/G-R4).

### Per-fighter strike-reaction coverage (all 129 moves-bearing files)

| File | Bound bank | Moves | Damaging strikes | Picks | Pick % | Largest remainder |
|---|---|---|---|---|---|---|
| aotsuki | kuma | 530 | 473 | 229 | 48% | no t3_row 243 |
| armor-king | armorking | 500 | 412 | 104 | 25% | no t3_row 278 |
| awapop | nina | 909 | 813 | 310 | 38% | no t3_row 397 |
| baek | bryan | 111 | 99 | 97 | 98% | no t3_row 2 |
| baek-master-white | bryan | 291 | 116 | 104 | 90% | no t3_row 12 |
| blanka | bryan | 199 | 166 | 84 | 51% | no t3_row 80 |
| bob | jin | 557 | 519 | 86 | 17% | no t3_row 411 |
| bruno | bryan | 328 | 306 | 97 | 32% | no t3_row 209 |
| buffalo-bill | law | 796 | 728 | 332 | 46% | no t3_row 337 |
| burger | bryan | 552 | 512 | 103 | 20% | no t3_row 409 |
| burger-demon | — none | 466 | 431 | 0 | 0% | no t3_row 431 |
| burger-speed-demon | — none | 454 | 422 | 0 | 0% | no t3_row 422 |
| burger-the-mouth | — none | 454 | 423 | 0 | 0% | no t3_row 423 |
| byou | jin | 728 | 661 | 123 | 19% | no t3_row 521 |
| cainelias | king | 46 | 23 | 22 | 96% | no t3_row 1 |
| charger | bryan | 203 | 170 | 84 | 49% | no t3_row 84 |
| charger-attire2 | bryan | 199 | 166 | 84 | 51% | no t3_row 80 |
| chatur | ogre | 281 | 263 | 234 | 89% | row miss 21 |
| chordz | jin | 469 | 415 | 113 | 27% | no t3_row 285 |
| cyborgx | gunjack | 624 | 549 | 125 | 23% | no t3_row 423 |
| deathfang | heihachi | 127 | 106 | 24 | 23% | no t3_row 80 |
| deathfang-werewolf | heihachi | 127 | 106 | 24 | 23% | no t3_row 80 |
| demonio | jin | 764 | 687 | 299 | 44% | no t3_row 368 |
| demonio-bloodline-ember | jin | 686 | 608 | 313 | 51% | no t3_row 275 |
| demonio-human | jin | 683 | 608 | 299 | 49% | no t3_row 289 |
| demonio-winged | jin | 1063 | 937 | 304 | 32% | no t3_row 613 |
| diablo | heihachi | 661 | 585 | 297 | 51% | no t3_row 281 |
| dio | heihachi | 275 | 256 | 124 | 48% | no t3_row 130 |
| doa-ayane | — none | 23 | 14 | 0 | 0% | no t3_row 14 |
| doa-bass | — none | 22 | 17 | 0 | 0% | no t3_row 17 |
| doa-hayabusa | — none | 18 | 17 | 0 | 0% | no t3_row 17 |
| doa-jannlee | — none | 21 | 15 | 0 | 0% | no t3_row 15 |
| doa-kasumi | — none | 20 | 18 | 0 | 0% | no t3_row 18 |
| doa-tina | — none | 26 | 16 | 0 | 0% | no t3_row 16 |
| doc-frank-frankenstein | bosconovitch | 788 | 589 | 338 | 57% | no t3_row 196 |
| doc-frank-hood | bosconovitch | 892 | 651 | 351 | 54% | no t3_row 245 |
| doc-frank-machine-shop | bosconovitch | 933 | 682 | 365 | 54% | no t3_row 247 |
| doc-frank-wowomomo | bosconovitch | 892 | 651 | 351 | 54% | no t3_row 245 |
| docfrank | bosconovitch | 380 | 316 | 239 | 76% | no t3_row 54 |
| dorowani | gon | 175 | 156 | 150 | 96% | throw-range value 6 |
| dxmmii | jin | 150 | 135 | 116 | 86% | throw-range value 17 |
| dxmmii-patchwork | jin | 170 | 145 | 116 | 80% | throw-range value 17 |
| gashadokuro | kuma | 530 | 473 | 229 | 48% | no t3_row 243 |
| gyou | hwoarang | 1005 | 901 | 330 | 37% | no t3_row 512 |
| gyou-spirit-body | paul | 567 | 492 | 198 | 40% | no t3_row 271 |
| hugo | king | 130 | 108 | 73 | 68% | throw-range value 26 |
| iori | heihachi | 196 | 175 | 95 | 54% | no t3_row 76 |
| jin_soul | yoshimitsu | 1012 | 864 | 275 | 32% | no t3_row 572 |
| kai | eddy | 877 | 796 | 349 | 44% | no t3_row 382 |
| kingtyrant | eddy | 848 | 779 | 363 | 47% | no t3_row 389 |
| kinpo | jin | 525 | 471 | 114 | 24% | no t3_row 340 |
| koreshi | heihachi | 1080 | 850 | 81 | 10% | no t3_row 722 |
| kronos | king | 900 | 525 | 91 | 17% | no t3_row 398 |
| kronos-attire2 | king | 2600 | 1412 | 85 | 6% | no t3_row 1292 |
| kutz | king | 160 | 122 | 96 | 79% | throw-range value 24 |
| lili | xiaoyu | 508 | 466 | 122 | 26% | no t3_row 344 |
| marduk | king | 340 | 284 | 67 | 24% | no t3_row 177 |
| mariposa | — none | 372 | 342 | 0 | 0% | no t3_row 342 |
| mariposa-monarch | xiaoyu | 518 | 475 | 122 | 26% | no t3_row 353 |
| megami | — none | 304 | 259 | 0 | 0% | no t3_row 259 |
| menajerii | kuma | 193 | 137 | 3 | 2% | no t3_row 134 |
| michiko | jin | 344 | 319 | 122 | 38% | no t3_row 180 |
| negativo | bryan | 292 | 275 | 97 | 35% | no t3_row 178 |
| nightwolf | julia | 567 | 528 | 233 | 44% | no t3_row 215 |
| pantera | king | 874 | 634 | 249 | 39% | no t3_row 341 |
| phantom | yoshimitsu | 1019 | 883 | 314 | 36% | no t3_row 552 |
| pond | — none | 620 | 552 | 0 | 0% | no t3_row 552 |
| purplerain | jin | 569 | 514 | 115 | 22% | no t3_row 382 |
| raiden | gunjack | 114 | 100 | 95 | 95% | row miss 4 |
| rave | lei | 1086 | 991 | 418 | 42% | no t3_row 484 |
| realizzt | jin | 156 | 141 | 122 | 87% | throw-range value 17 |
| retsu | bryan | 739 | 625 | 260 | 42% | no t3_row 360 |
| rin | jin | 710 | 592 | 316 | 53% | no t3_row 256 |
| ryuji | — none | 127 | 94 | 0 | 0% | no t3_row 83 |
| ryuji-rock | king | 129 | 94 | 13 | 14% | no t3_row 81 |
| ryusan | — none | 211 | 197 | 0 | 0% | no t3_row 197 |
| sakura | xiaoyu | 764 | 655 | 290 | 44% | no t3_row 338 |
| samura1 | gunjack | 860 | 741 | 329 | 44% | no t3_row 409 |
| scimitar | jin | 362 | 323 | 112 | 35% | no t3_row 194 |
| sf-akuma | heihachi | 168 | 156 | 8 | 5% | no t3_row 148 |
| sf-blanka | bryan | 37 | 34 | 11 | 32% | no t3_row 23 |
| sf-cammy | — none | 10 | 9 | 0 | 0% | no t3_row 9 |
| sf-chunli | — none | 10 | 9 | 0 | 0% | no t3_row 9 |
| sf-dhalsim | — none | 10 | 8 | 0 | 0% | no t3_row 8 |
| sf-guile | — none | 11 | 10 | 0 | 0% | no t3_row 10 |
| sf-ken | jin | 32 | 30 | 9 | 30% | no t3_row 21 |
| sf-mbison | — none | 12 | 10 | 0 | 0% | no t3_row 10 |
| sf-ryu | jin | 34 | 33 | 9 | 27% | no t3_row 24 |
| sf-sagat | — none | 10 | 9 | 0 | 0% | no t3_row 9 |
| sf-vega | xiaoyu | 36 | 28 | 9 | 32% | no t3_row 19 |
| sf-zangief | king | 36 | 25 | 9 | 36% | no t3_row 16 |
| sha | xiaoyu | 785 | 674 | 291 | 43% | no t3_row 356 |
| silvertongue | xiaoyu | 508 | 466 | 122 | 26% | no t3_row 344 |
| skull | bryan | 688 | 632 | 251 | 40% | no t3_row 376 |
| slice | bryan | 486 | 415 | 97 | 23% | no t3_row 318 |
| star | xiaoyu | 908 | 790 | 273 | 35% | no t3_row 490 |
| street-reign | — none | 5 | 4 | 0 | 0% | no t3_row 4 |
| sunra | heihachi | 139 | 130 | 124 | 95% | no t3_row 4 |
| t3-anna | anna | 743 | 679 | 248 | 37% | no t3_row 389 |
| t3-bosconovitch | bosconovitch | 266 | 250 | 229 | 92% | throw-range value 21 |
| t3-eddy | eddy | 707 | 644 | 282 | 44% | no t3_row 356 |
| t3-forestlaw | forestlaw | 102 | 98 | 98 | 100% | no t3_row 0 |
| t3-gon | gon | 151 | 134 | 130 | 97% | throw-range value 4 |
| t3-hwoarang | hwoarang | 723 | 658 | 251 | 38% | no t3_row 394 |
| t3-julia | julia | 419 | 390 | 179 | 46% | no t3_row 196 |
| t3-kuma | kuma | 530 | 473 | 229 | 48% | no t3_row 243 |
| t3-law | law | 693 | 629 | 269 | 43% | no t3_row 334 |
| t3-lei | lei | 790 | 719 | 254 | 35% | no t3_row 438 |
| t3-nina | nina | 754 | 671 | 260 | 39% | no t3_row 374 |
| t3-ogre | ogre | 161 | 153 | 146 | 95% | throw-range value 7 |
| t3-paul | paul | 497 | 425 | 181 | 43% | no t3_row 227 |
| thor | bryan | 322 | 225 | 97 | 43% | no t3_row 128 |
| tobi | hwoarang | 729 | 664 | 251 | 38% | no t3_row 400 |
| torch | anna | 892 | 824 | 326 | 40% | no t3_row 421 |
| tou | paul | 681 | 583 | 275 | 47% | no t3_row 258 |
| vainabel | — none | 60 | 42 | 0 | 0% | no t3_row 38 |
| vega | xiaoyu | 207 | 174 | 109 | 63% | no t3_row 63 |
| vf-akira | — none | 20 | 17 | 0 | 0% | no t3_row 17 |
| vf-elblaze | — none | 28 | 25 | 0 | 0% | no t3_row 25 |
| vf-jeffry | — none | 25 | 23 | 0 | 0% | no t3_row 23 |
| vf-kage | — none | 14 | 10 | 0 | 0% | no t3_row 10 |
| vf-leifei | lei | 812 | 739 | 222 | 30% | no t3_row 490 |
| vf-sarah | — none | 14 | 12 | 0 | 0% | no t3_row 12 |
| vf-wolf | — none | 21 | 18 | 0 | 0% | no t3_row 18 |
| waterfall | jin | 365 | 338 | 115 | 34% | no t3_row 206 |
| yukihyo | armorking | 560 | 445 | 115 | 26% | no t3_row 306 |
| zangief | king | 217 | 150 | 77 | 51% | no t3_row 46 |
| zen | — none | 644 | 570 | 0 | 0% | row miss 570 |
| zui | jin | 654 | 562 | 123 | 22% | no t3_row 422 |
