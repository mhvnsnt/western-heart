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
| F1 | **300 of the 781 T7-join moves still unmapped** (481 mapped with evidence: 208 high / 273 medium; 450 have byte-exact clip locators) | Re-counted from `game/assets/anim/t7/clip-maps/*.json` at current main: 481 mapped / 300 unmapped exactly. Buckets per the clip-mapping record: 81 strong T8-only candidates, 91 ambiguous motbin pools, 39 requirement-gated chain throws, 89 other (no MVL corroboration / no cancel-graph terminal). Independent reason-string parse reproduces 91 and 89 exactly | T7/T8 teardowns first: T8 pieces for the 81; requirements-table decode for the 39; fingerprint disambiguation for the 91; the 89 stay logged with per-move reasons where no source proves them | 81 → T8 community-pull lane (running). 91 + 39 + 89 → **this lane (B2)** |
| F2 | **31 moves are move-mapped but their clips sit in the un-located bank-0x0000 file** | Clip-mapping record in `game/assets/anim/t7/INDEX.json` (PR #1275 resolution record): 450/781 byte-exact located; 31 mapped, bank file not in the pulled tree; names are facial/`vlc_`-family | Tekken first: wider search of the owner's own T7 Steam tree (DepotDownloader pull of additional depots if the file lives in an unpulled one); if truly not held, a runtime-trace spec is the named fallback | **This lane (B2a)** |
| F3 | **12,684 of 30,291 `anim_t3` mappings are guess-grade** (10,221 `nearest (approximate)` + 2,463 `same-notation`) | Re-verified exactly by re-parse. Per-fighter distribution in the provenance doc | Each fighter's own T3 bank branch graph (branch-walk proofs). Stance/directional first steps mostly do NOT prove yet — their T3 identity runs through branch **condition codes that are not decoded**; that decode is the named unblocking research | Guess-grade corrections → provenance lane Phase 1 (34 1-W files; PRs landing now). Condition-code decode → un-owned research, named here |
| F4 | **7,032 moves carry donor/stand-in marks in the data** (6,782 with a `donor_fighter` key) | Re-verified exactly (donor 6,782 + standin/fallback/placeholder/generic = 7,032). Worst: kronos-attire2 2,458 (class 2, approved — stays), koreshi 751, kronos 650 (class 2, approved — stays), demonio-human 581 (self-inheritance, not foreign) | Provenance rules: class 2 stays; class-3 layers (koreshi 312-move Yoshimitsu layer, demonio 34 devil_jin rows, gyou 47 paul rows) replaced from each fighter's own source in Phase 2; what the own source lacks stays UNMAPPED by name | Provenance lane (Phase 2, after Phase 1) |
| F5 | **487 moves have no anim mapping of any kind** (476 with no row at all + 11 with a bare `t3_row` only) | Re-verified with the definitional split resolved (476 + 11 = the audit's 487 exactly). Concentrated in 1-S files: baek-master-white 153/291, pond 151/620, thor 78/322, menajerii 51/193, megami 20/304 | Each fighter's own source: T7 Steam extraction preferred for T7 bases (pond/Raven, baek-master-white/Baek), TTT2 decoded data for megami + menajerii (71 of the 487), DOA/VF programs for the DOA/VF data files | Source lanes per fighter; megami/menajerii portion → **this lane (B1)** |
| F6 | **184 strike/throw identity mismatches** (175 moves carry throw flags with a non-throw class; 9 strike-class moves point at named throw anims) | 175 re-verified exactly. The 9 verified under the audit's strike-class-only definition (kingtyrant ×3 + scimitar/star sets); a wider net finds 16 including special-class `throw_escape` entries — definitional, recorded here so nobody quotes 16 | Settling source is each bank's `hit_frames.json` throw flags (held, in-repo) + own-bank anim replacement where the anim itself is wrong | **This lane (queued after B1–B3)** |
| F7 | **13 No Mercy-sourced rows are SUSPECT** (wrong FileTable window extraction) | Re-verified exactly: cainelias ×5 pointing at wrong-window bank clips; ryuji-rock ×7 Rock specials (refs `mk:MK-*` named "(NO MERCY)"); negativo's `u/f+1+2` is a move NAME only (ref `t7:negan:`), not NM-sourced | True-window re-extraction of the No Mercy banks (separate owed program). The ryuji-rock seven are additionally gated on the owner's Dolphin Route 3 call; cainelias's base choice is Owner Decision List item 8 | Flagged, NOT fixed — NM re-extraction program + owner items. No lane edits these rows meanwhile |
| F8 | **4 strings whose notation has no move entry** (orphan strings) | Re-verified: chatur `d/b+1,2` and `1,2,1+2`; pond `MIST 1,2`; ryusan `WR f,f,F (Mid Screen)`. (A rawer counter finds 7 first-step misses; the 3 extra burger-file strings resolve through their `hits` arrays and are NOT orphans — definitional, resolved) | chatur's two from the T3 Ogre branch graph (held); pond/ryusan stay UNMAPPED by name until their T7 sources (Raven / Lucky Chloe) land | chatur → **this lane (with B1)**. pond/ryusan → source-pending |
| F9 | **Pantera step-plan REVIEW candidates (57) not promoted**; 41 step occurrences UNMAPPED by name | PR #1232 record: last-step verified 11 / review 25 / unmapped 24 across 60 keys; promotion requires the FK soft gate + play-verify video | T3 King branch graph (held) for data; video evidence from the play-verify lane | Play-verify lane (video, running) + provenance lane (data). Not this lane |
| F10 | **TTT2 integration not yet consumed**: the decoded TTT2 move-list layer (PR #1235) is supply-only; no fighter file uses it | Supply re-counted at current main: `game/assets/ttt2/` = 57 character files, **6,559 records exactly** (6,122 moves + 399 sample combos + 38 stance separators), each with `anim_ref` `ttt2:{char}:row:{n}` | The TTT2 layer itself (held, in-repo). Per the provenance doc, the fighters whose real source IS this layer: **megami** (TTT2 Jun Kazama, 304 moves, 20 no-anim) and **menajerii** (TTT2 Roger Jr., 193 moves, 51 no-anim), both class 1-S document-sourced today; **buffalo-bill** (Law) is TTT2-primary per the 2026-10-23 canon decision with T3 as provisional fallback | **This lane (B1)**: megami + menajerii wired first; buffalo-bill join table built, application sequenced after the provenance lane's Law-group Phase 1 PR to avoid same-file collisions |
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
| T7-join unmapped moves | 300 | T8 lane 81 / this lane 219 (F1) |
| Mapped moves with un-located clips (bank-0x0000) | 31 | This lane (F2) |
| No-anim moves | 487 | Source lanes per fighter; 71 via this lane's B1 (F5) |
| Guess-grade `anim_t3` | 12,684 (shrinking per provenance PR) | Provenance Phase 1 (F3) |
| Donor-marked moves awaiting Phase 2 replacement | 439 class-3 layer rows (312 + 34 + 47 + residues) of 7,032 marked (rest = approved class 2 / self-inheritance) | Provenance Phase 2 (F4) |
| Throw-identity mismatches | 184 | This lane, queued (F6) |
| SUSPECT No Mercy rows | 13 | Blocked: re-extraction program + owner items (F7) |
| Orphan strings | 4 (2 fillable now) | This lane / source-pending (F8) |
| TTT2-source fighters unwired | 2 (megami, menajerii) + 1 join table (buffalo-bill) | This lane (F10) |
| Fighters missing anatomy data | 72 of 73 | This lane, queued (C1) |
| Roster rig-audit coverage | 0 fighters batch-audited (pipeline proven on Baek only, Oct-29) | **This lane (B3)** — Baek fix lands first |

## This lane's execution order

B1 — TTT2 fighter integration (F10, plus chatur's F8 strings).
B2 — T7 follow-ons: bank-0x0000 hunt (F2), requirements-table decode (F1-39),
fingerprint pass over the ambiguous pools (F1-91), re-examination of the 89.
B3 — Full-roster rig batch (skin_audit sweep + per-character fix PRs, Baek first).
Then F6 and C1/C5 as the queue clears. Every landed piece republishes the
deployable build via the PR #1282 path. Progress updates land in this doc.
