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
