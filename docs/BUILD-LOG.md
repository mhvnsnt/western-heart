# BUILD-LOG — Western Heart (resume point for Muse / any agent)

Lane ownership is claimed on #866. MoneyManBusch owns: Pantera and the core-8 chat-owned animation wiring, the Tekken 7 bank extraction (`tools/anim/t7_*`), OpenKumite/FE adoption, moveset-template inventory, and the PR queue. Muse owns #1096 and its stack, the moves audit, and `tools/auto_rig`.

## 2026-11-05 — t383u: Ryusan card live + True Ogre/Chloe sources located (MoneyManBusch / Grok)

- **#1588 MERGED** `a2aa63e8` — Ryusan select card (521-joint) + POSE-BLOCKERS.
- **Pages:** `gh-pages-m1-20261029` `cd2905e2` — ryusan.png + manifest (net −3 KB).
- **Chatur True Ogre FOUND in WH:** `game/assets/anim/t3/ogre/` + `FIGHTER_BANK.chatur='ogre'` + `chatur.json` 281 rows (`ed16dd6c`). Template `t3-ogre-bank` → `attached-existing`.
- **Ryusan multi-hit sources FOUND:** reverse-engineering `dncmot.bin` + `dncrotsm.arc`. Pack skips until multi-hit bake.
- **Next:** per-hit bake; Chatur card 264-joint; B2 Ryusan GLB refresh; Aotsuki/Awapop.
- **Do not:** #1569; invent mappings; T3 King on Pantera; arena sky/lighting/colors.

## 2026-11-05 — Ryusan Phase 3: card recapture + anim gaps named-unmapped (MoneyManBusch / Grok) (t377u/t378u)

- **Card DONE:** `tools/portraits/capture.mjs ryusan` → `game/assets/portraits/ryusan.png` (select path `assets/portraits/${id}.png`). Manifest `bones:521`, `framed:true`. sha256 `82ed443be85d61e976adeb07a7a3ea1598b6cc215b8cb1161473a4c81f63c290` (was stale 90289 B `f156bf5e…`). Proof: `docs/proof/2026-11-05/ryusan-phase3/`.
- **Capture note:** B2 remote still hosts a stale ~2.1 MB / ~73-bone `model-rerig.glb`; capture forced local 521-joint file via temporary `remoteBase` placeholder (not committed). **Re-upload B2 from main** so live Pages loads fidelity model.
- **Stance:** luckychloe bank stance fails fit on 521-bone rig (Left shoulder ~1.23 rad) — card is bind/aim framed, not invented pose.
- **Anims LEFT UNMAPPED (no invent):** pack skips `1+2`, `u+3+4`, `f+3+4`, `b+1+2` (one-clip-one-hit); SHOW `intro`/`win` (`t3_stance.json`/`t3_win_rp.json`) — no body-clip in motbin. Sequenced-press probe = tooling follow-up.
- **Re-rank:** Ryusan card axis closed; not 100% (multi-hit/SHOW/stance-fit/B2). Next finishable: Aotsuki/Awapop when anim GRE is blocked — or multi-hit bake when real T7 rows exist.
- **Do not:** merge #1569; invent True Ogre for Chatur; touch arena sky/lighting/colors; Muse #1096 / auto_rig; #1566.

## 2026-11-05 — Roster closest-first ranking + SmutBase 6 bone verify (MoneyManBusch / Grok) (t377u/t378u)

- **Owner supersede:** fix model → card → moveset → animations by **closest-to-done first**. SmutBase 6 need full blend armatures (not 48/52 conversions). Pantera still not 100% (55 r17 `Kg_*`).
- **Phase 1 RANK landed:** `docs/handoffs/ROSTER-CLOSEST-FIRST-2026-11-05.md` (+ `.json`). Score = BASICS probe + r17 fails + moveset density + card placeholder + material gate + SmutBase full-rig bonus. Sources listed in that doc.
- **Closest:** **ryusan** (score 115; 9/10 probe; live joints **521**). Then aotsuki/awapop; pond; megami/menajerii/tobi; pantera (55 r17) is not closest.
- **Phase 2 VERIFY (no redo of #1570–#1577):** parsed live GLB JSON chunks from main `assets.js` paths — Pond 224, Ryusan 521, Tobi 255, Chatur 264 (master 984), Megami 469, Menajerii 450. **None** are the stripped 48/52 conversions on the live keys. Blends found in-repo for Pond/Ryusan/Tobi/Chatur; Megami/Menajerii blends recovered (#1575) kept out of public intake (README only) — shipped game GLBs already carry full bone counts.
- **DO NOT MERGE #1569** as written: it grafts Pond onto 52-joint `WH_Skeleton` and would undo #1571.
- **Phase 3 next:** start Ryusan (recapture stale card; finish remaining Lucky Chloe teardown rows from real reverse-engineering-repo data only — no donor/procedural as real moves). Re-rank when finished.
- **Out of scope this pass:** arena sky/lighting/colors; Muse #1096 / auto_rig; #1566 ASSET-PIPELINE; FE showcase names; Pages republish (docs-only).

## 2026-11-05 — Pantera A1/C1/RC4 + live Pages republish (MoneyManBusch / Grok)

- **A1 FIXED:** `fighter.js` clears `_throwHitDone` in `_enterThrownExec` and `startThrowLock`. Probe pattern (first throw damages, later throws 0) was stale flag on the victim — not missing JSON damage.
- **C1 FIXED (class only):** `pantera.json` `1+3,1` / `2+4,1` → `move_class: throw` + `isGrab`/`throw` + `throw_chain_follow` (diagnosis rows 415/417). No new anim wiring / no T3-as-T7 swap.
- **RC4 CLOSED:** `CHORD_WINDOW_MS` stays 50; touch throws use the existing 0.14 s chord rescue in `tryAttack` (video handoff). Widening the window would regress strings.
- **r17:** 55 slots remain named-open (clipmap is `Kg_*`; no notation bridge this pass; no GRE pac hunt).
- **Pages:** delta-deploy `gh-pages-m1-20261029` so main `#1578` (camera/debris/air-blend/PWA/templates) is playable live under the 1 GB cap. Arena sky/lighting/colors untouched.
- **Claim:** #866 MoneyManBusch. No Muse #1096 / `tools/auto_rig`. No FE leak / new imports.

## 2026-11-05 — OpenKumite v0.1.2 + FE public rules + template layer + first-play (MoneyManBusch / Grok)

- **Law:** `docs/PIPELINE-LAW.md` (OK/FE rails, FE embargo until 2026-12-25, Tag Battle demo ban, WWE-style template layer, Steam/GRE pointer rules, first-play camera/debris).
- **Handoff:** `docs/handoffs/OPENKUMITE-FIGHTINGENGINE-ADOPTION-2026-11-05.md`.
- **Templates:** `docs/movesets/MOVESET-TEMPLATE-INVENTORY-2026-11-05.md` + `game/data/moveset-templates/index.json`. Pantera → `t7-grappler-jaguar-mask` (exact King T7). No franchise roster names.
- **Combat:** `game/js/air-reaction-blend.js` (FE public 0.758 catch-height) + fighter hook + `node --test` ; hit/push debug F4.
- **Camera:** `fightCameraDolly` / `fightCameraCenterX` — landscape no longer forces 10.5 m into walls; FOV widens instead (`scene.js`).
- **Debris:** wall-break breach chunks join `_debris` gravity/settle (no more static floating chunks).
- **PWA shell:** `game/manifest.webmanifest` + `game/sw.js` (shell only; no `/assets/` pack cache). Android APK later (OK packaging pattern).
- **Pantera audit:** `docs/movesets/PANTERA-KING-T7-AUDIT-2026-11-05.md` — A1/C1/RC4 + 55 r17 slots remain; not 100% yet.
- **Do not:** hunt FE leaks; add Tag Battle/WWE superstar names to roster; touch Muse #1096 / `tools/auto_rig`.

## 2026-10-31 (evening) — Negativo plays Negan's real T7 attacks; rig checkpoint (Claude)

- **First fighter with real Tekken 7 ATTACK animations:**
  - Negativo's 26 single-input moves (1, 2, 3, 4, b+1–4, d/f+1–4, d+2–4, f+2/f+3, u/f+3/4, u+2, ...) play Negan's own 0xC8 clips (`game/assets/anim/t7/negan/moves.pack.json`).
  - Each row was mapped by the game's cancel graph plus exact frame data (`tools/anim/t7_move_resolve.py`) and baked by `tools/anim/t7_move_bake.py`.
  - Wiring: `T7_MOVES` / `ensureT7Moves` / `t7MoveClip` / `t7MoveRetarget` in t3anims.js, plus the `_attackClipPlan` t7 pick, `_attackClip` action and `_rootMotionApply` t7 track in fighter.js.
  - Test: `test/t7-moves.test.mjs`.
- **Rig checkpoint:** the GameRig re-rigs of Burger and Negativo did not reach the 2.5 stretch gate, so they were not shipped. Numbers and next steps are in the handoff, section 6.

## 2026-10-31 (later) — rig triage, FREE CAMERA behind PAUSE, full handoff (Claude)

- **Handoff (read first):** `docs/handoff/HANDOFF-CLAUDE-2026-10-31.md`.
- **Burger's wired model is broken:** the skeleton is a T-pose facing -Z while the mesh is an A-pose facing +X, so every weight is wrong (`anim_check` edge stretch p99.9 = 42.6, gate 2.5). Re-rig running through `tools/auto_rig/rig_tripo_static.py`, which fits the skeleton to the A-pose and then applies bone heat.
- **Negativo:** cone face and crushed arms, from a broken bind/weights in `negativo-a1-rigged.glb`. Same re-rig path next.
- **FREE CAMERA** is now an entry of the fight PAUSE menu; there's no floating button over the menus/HUD.

## 2026-10-31 — 12 more T7 stances live; Pantera's moves wait on 0x64 (Claude)

- **Live:** #1368 merged (main `19f5ac0c4`) and deployed to the live Pages branch `gh-pages-m1-20261029` (`e3ce10739`).
  - Manifest: commit `19f5ac0c4`, 2,101 files, 989.0 MB.
  - Added the 18 stance files; updated 48 files that were on main but not yet live; removed 0.
  - Module graph checked on the assembled tree; all new stance files serve 200.
- **3 more stances (next PR):**
  - Purple Rain on Lee (`kole_kamae`), Chordz on Lars (`amla_kamae`), Negativo on Negan (`nass_kamae`). All three are 0xC8 and baked with the same tool.
  - They were never bank-less: their movesets bind proxy banks (jin / jin / bryan), so they shared Demonio's / Skull's T3 stance until now.
- **Live check:** Burger (Bob stance) idles in `t7_burger_stance@burger` at weight 1 in a live fight, and Pantera's King stance is still bound.
- **Model hosting gap:** on the live build, only Pantera and Burger have their fight models served. Diablo, Skull, Sakura, Phantom and Nightwolf models are on main but over 20 MB, so they 404 live (jsDelivr refuses them too). Their stances show up live when Muse's Backblaze + Worker model hosting lands.
- **Pantera's moves past the stance:** King's moves resolved by `tools/anim/t7_clip_formats.py`:
  - All 552 damaging moves are 0x64.
  - The only 0xC8 clips are the stance and 108 round cinematics.
  - So the stance is everything the 0xC8 path can give him. Walks, dashes, throws, reactions and attacks need the 0x64 joint frame.
- **F11:** the per-bone fit on King's attack first frames is rejected (best median 10.3°–66.9° per bone, no winner; `tools/anim/t7_f11_fit.py`). Routes left (research doc, Next):
  - the game exe;
  - a live capture on the owner's PC;
  - TTT2 same-motion pairs once the TTT2 lane extracts motion data.

## 2026-10-30 — King's real T7 stance on Pantera (Claude, owner-approved mannequin run)

- **Shipped first real T7 clip in the game.** Pantera idles in King's actual Tekken 7 stance (kinrotsm clip 132 `nakg_kg2kam`, 0xC8), not the T3 slot-3 stance.
- **Bake path:** `tools/anim/t7_c8_stance_bake.py` runs Koenji's mannequin plus Kiloutre's `applyRotationFromAnimdata` (the 18:00 control path), then converts to `wh-anim/1`. FK self-check: 0.000000 m.
- **Data:** `game/assets/anim/t7/king/`. **Wiring:** `game/js/t3anims.js` `T7_STANCES` / `applyT7Stance()`, Pantera only.
- **2026-10-31:** 12 more fighters on their bases' real T7 stances (Diablo, Skull, Retsu, Burger, Saku Ra, Sha, Phantom, Gyou, Tobi, Gashadokuro, Aotsuki, Nightwolf). The table is in the research doc.
- **Reusable for any 0xC8 clip.** 0x64 (all attacks) still needs the joint frame; see `docs/anim/T7-0x64-FRAME-RESEARCH-2026-10-30.md`.

## 2026-10-29 — T7 0x64 animation decoder (MoneyManBusch)

- **What landed:** `tools/anim/t7_anim64.py` is a pure-Python decoder for Tekken 7 compressed (0x64) animations inside MOTA blocks, big- or little-endian.
  - It's a port of the TKMovesets2 `Utils/Animations_T_x64.cpp` `ParseAnimation0x64` routine (Kiloutre, GPL-3.0), which is a decompilation of the T7 runtime routine.
  - The Blender Tekken importer only reads 0xC8, and no other public 0x64 decoder exists.
- **Fix over upstream:** the keyframe table holds `(len+14)>>4` entries. Upstream reads one past the table on the last frame when `(len-1)%16==0`; the decoder clamps it.
- **Proof** (`docs/proof/t7-anim64-king-rotsm.json`): King `kinrotsm.arc` (GRE `teardown/tekken7-steam/tkdata/mothead/mask/`):
  - 6 MOTA blocks
  - 1031 0x64 clips plus 123 0xC8 clips
  - 150,531 frames
  - 0 decode errors
  - Every clip is a full-body, 23-bone clip. Bones 0–1 are float root translations (mm, height ~1100); the rest are short Euler rotations.
- **Caveat:** 0.43% of frame steps exceed 0.5 rad. All of them are on the Y axis of end bones (hands and feet) at ±π/2, which is gimbal, not corruption. The bake stage must convert to quaternions and spike-filter.
- **How to run:** `python3 tools/anim/t7_anim64.py <file-with-MOTA> [report.json]`. It exits non-zero on any decode error. Raw game files stay in GRE.

## Bank coverage (motbin move+0x10 anim id)

| Bank | Source | Status |
|---|---|---|
| 0x0000 | `mot.bin` MotaList slot 0 | decodable with this tool |
| 0x4000 | `<code>rotsm.arc` | decodable with this tool; 22–37% of moves for the measured characters |
| 0x8000 | main character anims; not in tkdata (pakchunk / live memory only) | gap. Plan: best community-extracted alternative, then T3/VF5 fill, documented here |

## Next steps

1. T7 23-bone to WH rig bone map, then bake to `wh-anim/1` (quaternion + spike filter).
2. Wire the baked clips into `_attackClipPlan` ahead of donor/match, for core-8 chat-owned fighters only.
3. Pipeline script that regenerates and validates (decode, then bake, then skin-deformation check).

## 2026-10-29 17:50 CDT: move → real T7 clip map (Pantera/King)
- #1226 (decoder) merged.
- `tools/anim/t7_clipmap.py` joins the motbin JSON with `<code>rotsm.arc`: `anim_id & 0xC000 == 0x4000` gives `rotsm.arc` MOTA block 0, index `anim_id & 0x3FFF`.
- King: 467 of 552 attacks (85%) resolve to real decodable clips, with 0 errors. The other 71 attacks use the 0x8000 common bank and 14 use the inline bank. Those are gaps, filled with T3/VF5.
- Kinematic check: the 1,2 jab clip 315 has its arm peak at frame 8 (active frame 10). The 1+2 arm peak is at frame 10 (active 12). Right kick 318 is leg-dominant with its peak at frame 11 (active 13).
- GRE has no 0x8000 character bank (only Mob/Demo motion). Confirmed gap.
- Proof: `docs/proof/t7-clipmap-king-pantera.json`.
- Next: bake (quaternions + spike filter) to `wh-anim/1` on the WH rig and wire it for Pantera. After that: first-play gaps (stages, flow, HUD, results, rematch, sound) per owner t358u.
- Muse: moves lane and tools/auto_rig untouched.

## 2026-10-29 18:00 CDT: 0xC8 vs 0x64 pose finding (MoneyManBusch)

- **Control:** King `kinrotsm.arc` 0xC8 clips (raw floats), applied with the community `applyRotationFromAnimdata` onto Koenji's TekkenMannequin in headless Blender, give a correct upright pose. So the importer and mannequin path is fine.
- **Problem:** 0x64 clips (all attacks), decoded with `tools/anim/t7_anim64.py`, come out crumpled. That includes frame 1, the base pose, where no bitstream is involved.
- **Already ruled out:** descriptor layout (the first 23 bones are identical in both formats; 0x64 only appends bones), endianness (matches TKMovesets `Byteswap64Animation`), Euler order, inverse rotation, axis signs and permutations, rotvec. The best fit is still ~54° mean error.
- **Clues:** the hinge sign is flipped (slot 11: 0xC8 −1.56 vs 0x64 +1.61); slot 6 is a length-400 vector in both formats but in a different direction. The likely cause is a per-bone reference frame that 0x64 is stored relative to.
- **UE AnimSequences:** GRE pakchunk1 has none for King or any fighter move (only story/cloth/mob), so that route can't supply attacks.
- **Next:** find the community-documented 0x64 joint frame (TKMovesets / BlenderTekkenDirect / modding notes) and apply it. No guessed rotations ship.
