# Procedural / hand-made animation & pose audit (2026-10-14)

Owner rule: procedural, hand-keyed or IK-authored animation and poses get replaced with REAL animation
decoded from the owner's own teardown files. This file lists every non-real clip/pose in Western Heart,
its real counterpart (if decoded), and what is still missing. Rules: [RULES_NO_GUESSING.md](../RULES_NO_GUESSING.md).

## 1. Inventory of procedural / authored animation

| # | Where | What | How it was made | Real counterpart | Status |
|---|---|---|---|---|---|
| 1 | `lab/tools/clips.py` -> `lab/game/assets/pantera_leoman.glb` (11 clips) | idle, walk_fwd, walk_back, light, medium, heavy, grab, hit, block, ko, win | **Authored** world-space targets + analytic 2-bone IK (`clips.py` docstring). Not decoded motion. | T3 King bank `divmot03_king.bin` | **Partly replaced**: `pantera_leoman_t3real.glb` adds real `t3_stance`, `t3_stance_b/c`, `t3_win_lp/rp/lk/rk`, `t3_heavy`, `t3_grab`. Old clips kept (nothing deleted). |
| 2 | same, `lab/game/assets/t3_king.glb` | same 11 clips | same authored IK | same bank, exact rig (bind = T3 stance) | **Partly replaced**: `t3_king_t3real.glb` (same clip list). |
| 3 | `lab/game/scripts/fighter.gd` | state machine plays clips by name; attacks seek a normalised 0..1 authored clip | n/a (player) | — | **Wired**: `REAL` map prefers `t3_*` clips (idle->t3_stance_b, win->t3_win_lp, heavy/grab->t3_heavy/t3_grab, attacks seek real 60 fps frames). `main.gd` loads `*_t3real.glb`; `--anim=authored` restores old files. |
| 4 | `assets/poses/pantera/folded.json`, `lunge.json`; title v1/v2/v3 heroes | bone poses for title/cards | sampled from the authored clips of #1 (idle@0.0, grab@0.35) -> **procedural by inheritance** | T3 King win/intro frames | v4 title made from a REAL pose (below). v1–v3 kept unchanged (sha256 verified). |
| 5 | `game/js/fighter.js` (browser build) | Mixamo/Quaternius mocap base (Idle/Walk/Run) + **procedural CCD-IK** punches/kicks/lean, sin() wobble/aura | procedural IK + third-party free mocap (not teardown) | T3 King/Jin/Xiaoyu/Bryan/Heihachi/Gun Jack/Yoshimitsu banks in `teardown/tekken3/animations/` | **Not replaced yet** (needs the same bake onto the Mixamo-49 rigs of `game/assets/models/*.glb`; map in `lab/skeleton/retarget_maps.json` mixamo49). |
| 6 | `game/assets/models/pantera.glb` Mixamo Idle | cm-scale mis-retargeted Mixamo Idle (rig_check: stretch x21) | third-party Mixamo | T3 stance | Not replaced yet. |
| 7 | `docs/ANIMATION-PIPELINE.md` plan | Quaternius + CMU BVH + "Path C IK procedural" | plan to use non-teardown + procedural | — | **Superseded** by this audit: teardown motion first. |
| 8 | `customization/create-fighter/` preview poses | creation suite (Repo Co Dev) | — | — | **Out of scope** (not edited by this lane). |
| 9 | physics sandbox (Jigglebot) | physics | — | — | **Out of scope**. |

## 2. Real sources found and used
- Tekken 3 (owner's disc): `teardown/tekken3/animations/divmot03_king.bin` (+6 other fighters + `divmot99_common.bin`), decoder `teardown/tekken3/tools/local/pose_assemble.py` + `usa_motion.py` + `usa_tables.py` (bit-exact USA ports), needs `n0madic/Tekken3Remake tools/research/motion.py` (public; sparse clone, see below).
- Slots (n0madic `docs/research/formats/divmot-banks.md`, `code/fight-frame.md`): 0–2 = round-start stances, `0xD67–0xD6A` = the 4 victory poses (LP/RP/LK/RK).
- Exhaustive search for a real **arms-folded** frame: every unique move row of King's bank (652 rows) sampled every 8 frames with a metric (each wrist near the opposite elbow + forearms horizontal + upright). Result: **no crossed-arms frame exists in T3 King**. Closest real frames: win RP (0xD68) 2.5–3.3 s (one forearm across the chest, roar) and win LP (0xD67) 0–1 s (fists at chest).

## 3. Title before/after
- BEFORE v3: `game/ui-wh/art/wallpaper_wh_v3.png` (authored idle clip, procedural).
- AFTER v4 (new, not default): `game/ui-wh/art/wallpaper_wh_v4.png`, hero `game/ui-wh/portraits/pantera_hero_t3real_win_rp.png` = REAL T3 King win pose 0xD68 @3.3 s on Pantera P1. Select with `?title=v4` / `?title=t3real`.
- Side by side: `docs/qa/ui-title/before_after_v3_v4_t3real.jpg`. Decoded win-pose grid: `docs/qa/ui-title/t3_king_win_poses_decoded_grid.png`.
- v4 is **not** an arms-folded pose — that source is missing (section 5). Default stays v3 until the owner picks.

## 4. How to reproduce
```
git clone --depth 1 --filter=blob:none --sparse https://github.com/n0madic/Tekken3Remake /workspace/t3anim/t3r && (cd /workspace/t3anim/t3r && git sparse-checkout set tools/research docs)
export T3REMAKE_RESEARCH=/workspace/t3anim/t3r/tools/research
CL="t3_stance=0,t3_stance_b=1,t3_stance_c=2,t3_win_lp=0xD67,t3_win_rp=0xD68,t3_win_lk=0xD69,t3_win_rk=0xD6A,t3_light=0xD06,t3_medium=0xD2F,t3_heavy=0x412,t3_grab=0x412"
python3 lab/tools/t3_motion_bake.py lab/game/assets/pantera_leoman.glb lab/game/assets/pantera_leoman_t3real.glb --clips $CL --json-dir assets/anim/t3/king_on_pantera_leoman
python3 lab/tools/t3_motion_bake.py lab/game/assets/t3_king.glb lab/game/assets/t3_king_t3real.glb --clips $CL
xvfb-run -a godot --rendering-driver opengl3 --path lab/game -s res://tools/render_title_hero_real.gd -- /tmp/out t3_win_rp 3.3 180
cp /tmp/out/pantera_hero_t3_win_rp_3.30.png game/ui-wh/portraits/pantera_hero_t3real_win_rp.png && python3 game/ui-wh/tools/make_wallpaper.py v4
```
Retarget method: per-part rigid Kabsch fit of the decoded posed T3 parts against the T3 stance -> world rotation delta -> glTF space (same transform as `t3_to_gltf.py`) -> `G_target = G_t3 . S_bone` (S = swing from the target's rest bone direction to the T3 stance bone direction). No keys typed by hand. Spine = halfway Hips->Chest, Neck = Chest, Toe = Foot (T3 has no such bones).

Tests run (Godot 4.3): `tests/test_move_table.gd` PASS; headless CPU-vs-CPU match with real clips: `MATCH RESULT wins=[1, 2] rounds=3 hits=35 blocks=32` (PASS criterion of run_match_headless.sh).

## 5. MISSING real sources (reported, not faked)
| Need | Why missing | Unblock |
|---|---|---|
| True **arms-folded** pose/intro for Pantera | Not in T3 King bank (exhaustive scan). King/Armor King intros in TTT2/T6/T7 not decoded. | TTT2: release `ttt2-7z-v1` downloaded+STFS-extracted, then decode TTT2 motion (no decoder yet). T6: `DATA401` encrypted (PPSSPP live dump, `teardown/tekken6/PPSSPP-LIVE-RUN-GUIDE.md`). T7: `teardown/tekken7/king/*` are meshes only, no anim; full game not acquired. WWF No Mercy (5,787 anims, 100% teardown) / WMXIX YANM (170) taunts likely include arms-crossed; need a retarget from their rigs. |
| Real clips for the other 22 roster fighters | only 7 T3 banks; other bodies come from TTT2/T6/T7/SC/DOA/VF5 teardowns without motion decoders | per-game motion decoder work (see TEARDOWN-STATUS.md). |
| Browser build (`game/js`) real clips | Mixamo-49 retarget of the bake not done | run the bake against Mixamo rigs (non-identity rest -> needs rest-orientation conversion). |
| **Blanka / Zangief / Vega clips** (CHARGER, KRONOS-line, KORESHI + SF guests) — added 2026-10-20, anim-bank wiring lane | No decoded SF animation data exists in any store (ANIMATION-INDEX lists no SF source; the SF cast models are static Sketchfab intakes). Raw per-character animation data sits UNDECODED inside the SF EX Plus Alpha PAC packs (`teardown/street-fighter-3d-games/extracted/ex-plus-alpha/PL/P00–P19.PAC`). | PAC container decode (44-entry chunk table anomalous — dedicated RE pass, idle-queued) + P-slot→character mapping (SEL2 cross-check) + PS1 segmented-TMD animation decode/retarget. Full register: `docs/anim/BANK-TABLE-2026-10-20.md` §G-SF. CHARGER keeps the flagged bryan substitution until then. |
| **Iori clips** (DEATHFANG) | No King of Fighters game exists in any teardown store; only a Sketchfab Iori model + frame-data movesets are held. | Acquire + extract a 3D KOF entry (XIV/XV) motion data. §G-KOF. Flagged heihachi substitution meanwhile. |
| **Virtua Fighter clips** (NIGHTWOLF←Wolf per owner 2026-10-20; REALIZZT, KUTZ, VF guests) | VF5 extraction is models-only; VF motion containers were never RE'd by any lane. | VF5 motion decode + VF→canonical retarget. §G-VF. Nightwolf interim-bound to his CANON base Julia (flagged). |
| **DOA clips** (DOA guests; VAIN ABEL's Bass attires) | DOA4 teardown is model-side; the animation/keystream side is undecoded (PR #381 audit; five-oracle protocol, gate G5 with the sweep lane). | DOA4 .anm decode (sweep lane phase-3). §G-DOA. No substitution bound (isolation doctrine). |
| **Tekken 6 (PSP) clips** (ZUI←Steve, CYBORG X←Alisa, KINPO←Asuka, BURGER←Bob, STAR←Christie, SLICE, THOR, CHORDZ, BRUNO, LILI, MARIPOSA, MARDUK, BAEK) | T6 PSP animation data is encrypted; only 46 ending cinematics decoded (ANIMATION-INDEX). | PPSSPP decrypted-EBOOT dump → debugger trace → fit formula → known-plaintext verify (PR #388 line). §G-T6 — the single biggest bank unlock (13 bases). |
| **Tekken 7 clips** (MICHIKO←Katarina, SCIMITAR←Shaheen, N3GΔTIV0←Negan, T7-era banks for Diablo/Kinpo/Bruno/Yukihyō) | "Full game never acquired. Individual model rips have no animation data." (ANIMATION-INDEX) | T7 acquisition + UE4-era animation format RE. §G-T7. |
| **Mokujin clips** (DXMMII) | divmot15 is absent from the owner's T3 disc — BNS record 295 has size 0 (proven, T3-REMAINDER-BANKS §4). | TTT1/T5 Mokujin data from a future teardown. §G-T5. Flagged jin substitution meanwhile. |
| **Undertaker / Kane clips** (CAINELIAS, VAIN ABEL) | The motion data EXISTS and is decoded (5,787 No Mercy NPY clips; 170 WMXIX JSON clips; AKI→T3 retarget proven for King) but the per-character retarget to the WH bank format was never run for these two. | Conversion work on held data (no new extraction): retarget the Undertaker/Kane clip sets via the aki_to_tekken3 pattern into banks. §G-WRESTLE. |

## Update 2 (2026-10-14 evening): common bank + King locomotion/reactions — RESOLVED
- `teardown/tekken3/tools/local/pose_assemble.py` now resolves move-index values and anim words `>= COMMON_FLAG` from `divmot99_common.bin` (n0madic `divmot-banks.md`). `t3_light` (slot 0xD06) and `t3_medium` (0xD2F) bake.
- Slots identified from King's own branch lists + the EXE common-branch table `0x80017C78` (12-byte rows; low-5 bits `0x10` = direction only) + the reaction records `0x80010CE8` (42 bytes):

| Clip | Slot | Evidence |
|---|---|---|
| t3_walk_fwd / _b | 21 / 22 | stance row 0 branch `6 (no button) -> 21`; row 1 stance -> 22 |
| t3_walk_back / _b | 24 / 26 | `4 -> 24`; row 5 stance -> 26 |
| t3_dash_fwd, t3_backdash | 27, 30 | `f,f -> 27`, `b,b -> 30` |
| t3_crouch, t3_crouch_hold | 59, 40 | common row 477 `2 -> 59` (stance 40 = crouching, n0madic) |
| t3_jump_up / fwd / back | 127 / 129 / 131 | common row 557 `8/9/7 -> 127/129/131` |
| t3_sidestep_a..d | 283, 285, 287, 289 | common rows 492–495: flag `0x1C` (side step, `moves.md`) neutral-return after a 2/8 tap |
| t3_hit, t3_hit_launch | 2466, 2556 | reaction records of King's medium (idx 0x16D) and jab (0xCD): front-standing slots |
| t3_block, t3_block_b | 2693, 2705 | same records `+0x14` standing guard |
| t3_ko | 0xD66 | KO collapse slot (`combat.md`, `FUN_8002DA80`) |

- Heading normalisation added to the bake: each clip's first frame is yawed to face +Z (T3 stores world heading per move). Pure yaw, no reshaping. xz root travel is measured from the clip start.
- `fighter.gd` `REAL` map now also covers walk_fwd, walk_back, hit, block, ko (crouch/jump/sidestep clips are baked; the Lab state machine has no such states yet). `--anim=authored` still restores the old files.
- Proof: `docs/qa/anim/t3_king_moves_on_pantera.jpg` (rendered Godot frames, viewed), `docs/qa/anim/t3_king_moves_decoded_sticks.png` (decoded skeletons, 6 frames per clip). Headless CPU-vs-CPU match: `MATCH RESULT wins=[1, 2] rounds=3 hits=35 blocks=32` (PASS; 3 pre-existing `Parameter "m" is null` lines, same as authored).
- Note: v4 title (`wallpaper_wh_v4.png`) was rendered before heading normalisation with yaw 180; the file is unchanged and still correct.

## Update 3: the other T3 fighters (real clips on their own T3 bodies)
- New: `lab/game/assets/t3_{jin,xiaoyu,bryan,gunjack,yoshimitsu}.glb` (t3_to_gltf.py from each KMD + decoded stance `teardown/tekken3/renders/pose-check/<f>_stance75.obj` = slot 0 frame 75) and `..._t3real.glb` with 29 real clips each: stances, 4 wins, walk/dash/crouch/jump/sidestep, hit/block/KO, and light/medium/heavy/grab from each fighter's `lab/game/data/moves/<f>.json` t3_row -> slot. Global slot numbering is shared across banks (n0madic divmot-banks.md).
- WH counterparts (game/js/fighter.js T3_BODY map): demonio/rin/kai/zui/... -> jin; sakura/sha/nightwolf -> xiaoyu; skull/retsu/burger/... -> bryan; samura1/cyborgx/docfrank -> gunjack; phantom/jin_soul -> yoshimitsu. None of them except Demonio has an own WH model in the repo yet, so the clips live on the T3 bodies and in the bake JSON format for later retarget.
- **Heihachi: MISSING.** `models/heihachi191/heihachi.kmd` has no vertex data for several parts (hips, shoulder chain; stance OBJ only 490 lines), so the Kabsch pivot recovery cannot run. Unblock: find a complete Heihachi KMD record in `TEKKEN3.BNS` (`model-inventory.csv`) and re-run.
- Proof: `docs/qa/anim/t3_roster_real_clips.jpg` (Godot renders viewed: stance_b, light, crouch, win_lp per fighter; wins travel off-frame because the real root motion is kept).

## SHA-256 (new files)
```
5a8b9ce65b62244ef8bbd53737e3956732e99afe5653b268b10b0696d62f5a9b  lab/game/assets/pantera_leoman_t3real.glb
a107c3b888ba6683b063cbbc54cfa242d2b01289721ccd6a45d2244dbc0c8a70  lab/game/assets/t3_king_t3real.glb
bfa17192cf35b502caa21c36d7a0d74f62f8b412f687aafc503adbd9de7bcee7  game/ui-wh/art/wallpaper_wh_v4.png
85f6f701406d4ccc32eb366a54d4d8bf5f792d6e0b7eac4ddf6323a3bdb95d30  game/ui-wh/portraits/pantera_hero_t3real_win_rp.png
97a86b22706b9a724fb61392b9ebf7ec5237c4a8eeebeb16d72c86c154cbad10  docs/qa/ui-title/before_after_v3_v4_t3real.jpg
8ae24919a89ac81adc6d34f1ef35cbb3ccafd19c55dafe820c923bbd638da899  teardown/tekken3/animations/divmot03_king.bin
c84a320e323efda740547589608fab6500ed5c367d4486d5c3b89afe2eeb594f  teardown/tekken3/disc/files/TEKKEN3/SLUS_004.02
3b280fa477eff73cf76f1729e6c34366135e5d5e988a1a713abce49f1bde6a4c  teardown/tekken3/models/king95/king95.kmd
```

## Update 4 (2026-10-14) — arms-folded source search, browser build

### Item 3: real arms-folded pose — MISSING (no title v5)
Nothing was rendered, because no real source exists yet:
- WWE WrestleMania XIX YANM: the anatomy mapping is still marked UNRESOLVED / LOW confidence in the teardown notes.
- WWF No Mercy AKI clips: the joints are 1-DOF hinges on provisional axes, so a true FK arms-folded pose can't be trusted.
- TTT2: not extracted (about 13 GB of chunks on release `ttt2-7z-v1`). Public tools (TekkenMovesetExtractor) read from live memory, and there is no file decoder.
- T6 DATA401: still encrypted.
Title v4 stays the current version.

### Item 5: browser build (`game/js`, Mixamo GLBs) — BLOCKED, nothing wired
`lab/tools/t3_motion_bake.py` now has a generalized `TargetRig`: full node-tree world rest, non-identity rest, a Mixamo-49 canonical map, and -Z facing. The regression on `pantera_leoman` is bit-identical.
Findings (the GLBs are not committed):
- `game/assets/models/pantera.glb`: 5,805 of 5,805 side-weighted vertices are skinned to the opposite-side bone (left-side mesh on Right* joints). The asset's skin is mirrored, so ANY clip tears the arms, including its own Idle. The asset needs a re-skin or re-export. Swapping the weights would be a guess, so it was not done.
- `game/assets/models/demonio.glb`: the weights are correct. Numeric CPU skinning of the baked `t3_stance_b` gives a sane guard pose, but the Godot 4.3 render still shows the arms in T-pose while the legs move. Next step: check how Godot names and imports the 49 Mixamo bones (track paths vs `Skeleton3D` bone names) and test in the three.js runtime directly.
- `game/js/assets.js` and `fighter.js` are unchanged. The authored, procedural and CCD-IK path is still live there.

## Update 5 (2026-10-14): Lab crouch, jump and sidestep states
The inputs and timing come from King's decoded branch lists (`lab/tools/t3_branch_dump.py`, which follows BranchFind's CALL 0xC00C / RETURN 0xC00D rules; dump in `docs/anim/t3_king_branches_slot3_59_127.txt`):
- From standing (slot 3): 8 → 127 jump_up, 9 → 129 jump_fwd, 7 → 131 jump_back, 2 → 59 crouch.
- From 127 (air window 9–38, 48-frame clip): returning to neutral in frames 1–8 → sidestep 283 when sideFlag is clear, 285 when it is set.
- From 59 (8-frame entry): returning to neutral in frames 1–8 → sidestep 285 when sideFlag is clear, 283 when set. Holding down → 40 crouch_hold.
- sideFlag is set on the right-hand side because it mirrors the stick (`fighter.md +0xC6`).

Wired in `lab/game/scripts/fighter.gd` and played with the baked `t3_*` clips. The headless autoplay match passes: `MATCH RESULT wins=[2, 1] rounds=3 hits=43 blocks=37 frames=7420 moves={jump_up:18, crouch:11, crouch_hold:5, sidestep_a:6, sidestep_b:6}`. Proof frames: `docs/qa/anim/lab_movement_states.jpg`.

Still missing or not decoded:
- Stand-up slot 60 is not baked, so release after frame 8 goes straight to idle.
- Jump x-displacement is not applied (move-row `+0x16` step displacement is not read yet).
- Sidestep and jump evasion are not in hit tests.
- The touch HUD has no up/down buttons.
- jump_fwd and jump_back are wired but the CPU did not use them in this match.

## Update 6 (2026-10-14): pantera.glb L/R skin swap fixed as a new file
Added `game/assets/models/pantera_fixed.glb`; the original is kept. Tool, proof and remaining authored-weight defects are in `tools/rig_repair/README.md` (case 1). The arms no longer tear across the body.
Remaining defects:
- The wrist cuffs float because they are weighted to Spine/Spine1.
- The logo and pants weighting stretches in wide stances.


## INSTRUCTION GATE: Owner law, data source priority (Oct 23, 2026, 2:19 PM CT)

> **Western Heart data (moves, animations, frame data, menus, character select) comes from Tekken 5, 6, 7, 8 and TTT2. Tekken 3 is only a last-resort fallback, and every T3 use must be logged with the reason no T5/6/7/8/TTT2 source was available.**

- Search T5/T6/T7/T8/TTT2 teardowns first. Use T3 only when none of them has the data, and log the T3 use (file, clip, reason) in `docs/anim/PROCEDURAL_AUDIT.md`.

### Status of existing T3-baked clips under this law

All T3-baked clips already in the repo are **fallback, to be replaced from T5/6/7/8/TTT2**. Nothing is deleted; they stay until a replacement is baked and verified.

| Asset | T3 clips | Status | Reason T3 was used |
|---|---|---|---|
| `lab/game/assets/pantera_leoman_t3real.glb` | all 31 `t3_*` clips (stances, wins, light/medium/heavy/grab, walk, dash, crouch, jump, sidestep, hit, block, KO) | fallback, to be replaced from T5/6/7/8/TTT2 | Only decoded motion bank at bake time; TTT2 motion not decoded, T6 `DATA401` encrypted, T7 meshes only, T5/T8 motion not acquired. |
| `lab/game/assets/t3_king_t3real.glb` | same clip list | fallback, to be replaced from T5/6/7/8/TTT2 | same |
| `lab/game/assets/t3_{jin,xiaoyu,bryan,gunjack,yoshimitsu}_t3real.glb` | 29 `t3_*` clips each | fallback, to be replaced from T5/6/7/8/TTT2 | same |
| `assets/anim/t3/**` bake JSON, `fighter.gd` `REAL` map, v4 title hero (`t3_win_rp`) | derived from the above | fallback, to be replaced from T5/6/7/8/TTT2 | same |
| `game/assets/anim/t3/{ogre,kuma,gon,law,forestlaw_on_law}/` + `lab/game/assets/t3_{ogre,kuma,gon,law,forestlaw_on_law}_t3real.glb` (Claude, 2026-10-23, `tools/anim/t3_bake_bank.py`; proof `docs/proof/claude-2026-10-23/t3-banks/`) | 26 universal slots + light/medium/heavy, and every row the WH movesets reference in `rows.pack.json` (ogre 187, gon 147, kuma 161, law 216, forestlaw 198) | fallback, to be replaced from T5/6/7/8/TTT2 | Chatur (True Ogre), Menajerii (Kuma), Dorowani (Gon) and Buffalo Bill (Marshall Law + Forest Law) had movesets but no animation bank, so they stood rigid in fights. No T5/T6/T7/T8/TTT2 animation is decoded in the repo for any fighter: `teardown/tekken7/TEKKEN7-ROSTER-COVERAGE.md` records T7 moveset/animation coverage at 0 of 51 (needs the 47 GB Steam paks, `teardown/tekken7/T7-STEAM-EXTRACTION.md`); T6 is encrypted; TTT2 needs a ~40 GB extraction; T5/T8 animation data is not in the repo. T7/T8 frame data (startup, hit level, damage) is used where the game reads timing. |
| `game/assets/anim/t3/reactions.json` + `game/assets/anim/t3/<22 banks>/reactions.pack.json` (Claude lane E, 2026-10-24, `tools/anim/t3_reaction_tables.py` + `tools/anim/t3_reaction_bake.py`; contract `docs/anim/T3-REACTIONS.md`) | hit reactions (front/side/back × standing/crouching, counter hit, guard, down), air kinds `0xD56`–`0xD64`, KO collapse `0xD66`, throw-victim moves, thrower throw moves, throw escapes and their default continuations: 7,368 clips, 0 missing; the EXE tables `g_reactionRecords` `0x80010CE8`, `g_throwVictimSlots` `0x800174C4`, `g_closeReactions`, `g_airKinds`, `g_pushTables` from `SLUS_004.02` | fallback, to be replaced from T5/6/7/8/TTT2 | Every bank played one generic `t3_hit` (slot `0x9a2`) for every hitstun and for being thrown, and `t3_grab` was a copy of `t3_heavy`. No reaction or throw data from T5/T6/T7/T8/TTT2 is decoded in the repo. T7 fighter animation is 0 of 51 (`teardown/tekken7/TEKKEN7-ROSTER-COVERAGE.md`). T6 `DATA401` is still encrypted (`teardown/tekken6/MOTION-UNBLOCK-2026-10-23.md`). T5 `TK5DATA2` motions are only named, not extracted (`teardown/tekken5/t5_motion_manifest.txt`). TTT2 is not extracted, and T8 has models and UI only. |
| `game/assets/movesets/{pantera,burger,skull,diablo,phantom}.json` rewires + bindings (anim-motion audit 2026-10-24, `docs/anim/ANIM-MOTION-AUDIT-2026-10-24.md`, tool `tools/combat-qa/anim_motion_audit.py`) | 11 basic rewires — king 110 (pantera LP1), 99 (pantera RP2), 264 (pantera LK3); bryan 172 (burger/skull LP1), 100 (burger/skull RP2), 104 (burger/skull RK4); heihachi 104 (diablo RK4); yoshimitsu 123 (phantom LK3) — and 22 jumping-move bindings — bryan 183/87 (burger), heihachi 74 (diablo), yoshimitsu 73 (phantom), bryan 76 (skull) | fallback, to be replaced from T5/6/7/8/TTT2 | The previous rows were airborne/jump/wrong-limb clips (e.g. pantera LP1 row 44 starts airborne, RP2 row 203 duck-dips + travels 0.95 m, LK3 row 54 is a jump clip); the replacements are the only decoded in-bank rows passing limb/level/stance/foot checks for those moves. No T5/T6/T7/T8/TTT2 animation is decoded in the repo for any of these fighters (T7 0 of 51, T6 encrypted, TTT2 not extracted, T5/T8 motion not acquired); T7/T8 frame data carries timing/level only, no motion bytes. Kept rows (pantera RK4 216, burger/skull/diablo RP2, demonio/kinpo/scimitar RP2/LK3/RK4, diablo LK3) are likewise T3 fallback, not T7 motion. |
| `game/assets/movesets/{demonio,diablo}.json` 1+2 rewires (anim-motion audit follow-up 2026-10-24, `docs/anim/ANIM-MOTION-AUDIT-2026-10-24.md`, tool `tools/combat-qa/anim_motion_audit.py`) | 2 chord rewires — jin 92 (demonio LP1+RP2), heihachi 133 (diablo LP1+RP2) | fallback, to be replaced from T5/6/7/8/TTT2 | The previous rows were jump clips (jin 32, heihachi 37 — T3's own 1+2 attachments, but jumping motions for standing strikes); the replacements are the only decoded in-bank rows passing limb/level/stance/travel/provenance checks for those moves (jin 92: demonio `d+1+2` + `1+2~t3.jin` variant; heihachi 133: T3 table `b_r133` directional LP+RP). No T5/T6/T7/T8/TTT2 animation is decoded in the repo for these fighters (T7 0 of 51, T6 encrypted, TTT2 not extracted, T5/T8 motion not acquired); T7/T8 frame data carries timing/level only, no motion bytes. |

### T3 moveset-data use under this law (batch8, 2026-10-23)

| Asset | T3 data | Status | Reason T3 was used (no T5/6/7/8/TTT2 source available) |
|---|---|---|---|
| `game/assets/movesets/chatur.json` +129 moves (`merge_source: t3:ogre:row:N`, tagged `"set": "FIGHT"`) | True Ogre rows from `teardown/tekken3/movesets/moveset_ogre.json` (divmot14, 330 rows) via `tools/moveset-merge/merge_sources.py` | fallback, to be replaced from T5/6/7/8/TTT2 if True Ogre data ever surfaces | True Ogre is T3-only: cut from every later Tekken (not in T5/T6/T7/T8/TTT2 rosters). No newer movelist exists anywhere. T3 is the only source, not a fallback of convenience. |
| `game/assets/movesets/bruno.json` (0 added), `docfrank.json` (0 added), `samura1.json` (0 added), `star.json` (0 added) | none — pulls verified complete from newer sources | n/a | bruno: T7 Miguel complete (219/219, `docs/t7t8-reference/frame-data-t7/miguel.json`). docfrank: T3 Bosconovitch rows all covered (TTT2 Bosconovitch movelist pending extraction lane — no data to pull). samura1: T8 Jack-8 + T7 Jack-7 + T3 Gun Jack complete. star: Christie T5/TTT2 movelist unavailable (no data on disk; TTT2 extraction blocked) — see `docs/anim/STAR-ANIM-GAP-20261023.md`. |

## INSTRUCTION GATE: Owner law, no hand-made menus (Oct 23, 2026, 2:21 PM CT)

> **NO hand-made menus. Every Western Heart menu, character select and customization screen must be built from the actual teardown files (Tekken 5/6/7/8/TTT2 and other game teardowns). Every UI change must cite its teardown source files.**

### Status of existing hand-made UI under this law

| Asset | Status | Action |
|---|---|---|
| `game/ui-wh/` HTML UI (`index.html`, `cards.html`, `cards.css`, `cards.js`, `roster.js`, `imports.json`, `art/`, `fonts/`, `portraits/`) | **hand-made, NON-COMPLIANT** | Slated for rebuild from teardown UI files (T5/T6/T7/T8/TTT2 menu/char-select/customize layouts, then other game teardowns). Kept as a **fallback**; do NOT delete. Replace only in a reviewed PR that cites its teardown source files. |

### Batch 1 step plans (Pantera LP1/RP2 strings, 2026-10-24, docs/movesets/BATCH1-STEP-PLANS-2026-10-24.md)

| Asset | T3 data | Status | Reason T3 was used (no T5/6/7/8/TTT2 source available) |
|---|---|---|---|
| `game/assets/movesets/pantera.json` `string_step_plans` (60 keys: 31 canonical LP1/RP2 strings + 26 twins + 3 spelling variants) + `game/js/fighter.js` step-plan branch | King T3 bank rows for verified steps only (rows 36, 38, 39, 40, 50, 51, 52, 97, 98, 198, 200, 202, 203, 110) | fallback, to be replaced from T7 King extraction when clip bytes land | T7 King (`kinmot.bin`, 2,787 moves) is decoded, but 0x8000-bank clip bytes are not in tkdata (pakchunk/live-memory only) and requirement codes (636/811/80/81/72/217) + the aliases table are unresolved, so no T7 step clip can be wired yet. T3 step rows stand in for verified steps only; review/unmapped steps play no bank row. Re-match against T7 King rows when extraction lands. Rows 35/220 are never used for standing steps. |
## Pantera dash inputs f,F+RP2 / f,F+RK4 — anim_t3 REMOVED, donor stand-ins (2026-10-25, PR #988 revert)

**Status: TEMPORARY fallback, to be superseded. This is a regression-revert, NOT a correctness fix.**

- What was removed and why: PR #988 mapped Pantera `f,F+2` (Beast Elbow, RP2 dash elbow) to T3 king row 0 and `f,F+4` (Konvict Kick, RK4 dash kick) to T3 king row 69. File evidence proved both wrong (dash-row evidence 2026-10-25, `~/workspace/dash-row-evidence/DASH-ROW-EVIDENCE-2026-10-25.md`): row 0 is a **non-strike clip** (Job 1 profile hit null, active null, all limb extensions 0.0, btn 0; harness 0.027 m net / 0.067 m peak — it cannot be a mid elbow strike); row 69 is the **u+4 jump kick in place** (Job 1 stance jump, legR foot lift 1.912 m, hip rise to 1.329 m, travel 0.000 m; mid RK4 active 15–17). CORRECTION: row 69 is the u+4 jump kick, NOT standing 4 (standing 4 rows are 106/124/216). The revert deletes exactly those two `anim_t3` fields (structural diff proves only 2 keys changed in `game/assets/movesets/pantera.json`; move count 874 unchanged; quarantine section untouched; no T8 content touched).
- What plays now: donor rows **111** (T3 `f+2`, standing armR punch, HIGH, active 10, travel 0.151 m net / 0.301 m peak) for `f,F+2` and **114** (T3 `f+4`, standing legR kick, HIGH, active 14, travel 0.479 m) for `f,F+4`. These are **traveling STAND-INS, never the correct dash mapping**: T7's `f,F+RP2` is mid, 31f; T7's `f,F+RK4` Konvict Kick is mid, 15f; a high kick is duckable, Konvict Kick is mid. Level + name evidence affirmatively rule 111/114 out as the dash rows.
- Why T3 is used at all (instruction-gate law): no T5/T6/T7/T8/TTT2 animation is decoded for these dash moves — T7 king_49/king_52 motion is not decoded, T6 `DATA401` is encrypted, TTT2 is not extracted, T5/T8 motion is not acquired. The donor stand-ins restore the pre-#988 traveling behavior while the true rows are hunted.
- Settling evidence owed (in order): (1) a T3 motion-table source for `divmot03_king.bin` giving row numbers for `f,f+2` (K's Flicker, mid) and `f,f+4` (Konvict Kick, mid) — neither row number appears in the wired 355-entry T3 input→row map, and no dash row exists in the playable bank (zero dash inputs in the wired map; full scan of baked king standing strikes with travel ≥ 0.15 m returns only non-dash identities); (2) bake those rows if unbaked (256/652 baked today); (3) profile-verify: mid level, traveling, correct limb (armR / legR), dash-appropriate timing; (4) T7 King kinmot.bin decode (king_49/king_52) for animation identity — the only proof justifying calling a T3 row "the" dash row for the T7 move. Until then, any T3 row for a T7 dash move is a FALLBACK, not a verified mapping.
- Test honesty: `test/root-motion.test.mjs` passes 9/9 on the reverted file (baseline 7/9 — the two dash tests failed on rows 0/69). The test encodes DONOR behavior (plan row:111/114, kind `donor`, plus travel bounds), so green proves travel restored, NOT that the animation is the dash move. Do not mistake a green test for a correct dash animation.
- Untouched known-wrong mappings (out of this revert's scope, flagged not hidden): `f,F+2~t7.king` → row 260 (a 10-hit string step); `f,F+4~t7.king` → row 69 (same jump kick); `CH.f,F+4` → row 69 (same jump kick). These still need the same settling evidence.

## Pantera dash inputs — TRUE T3 dash rows 203/216 (settling evidence 2026-10-25, supersedes the donor stand-in revert)

**Status: T3 FALLBACK, to be replaced from T5/6/7/8/TTT2 when T7 king_49/king_52 motion is decoded.** This supersedes the 2026-10-25 donor stand-in revert (rows 111/114) — the stand-ins are retired; the dash inputs now play T3's own dash rows. The rows below are proven T3 dash rows, NOT proven T7 dash animations: until T7 King kinmot.bin decode (king_49/king_52) proves animation identity vs the T3 row, any T3 row for a T7 dash move is a fallback, not a verified mapping.

- Motion-table source (the settling evidence the revert entry called for): `teardown/tekken3/animations/divmot03_king.bin` branch graph, decoded with `teardown/tekken3/tools/local/moveset_extract.py` + the `motion` module (`~/workspace/tools/tekken3remake/tools/research/motion.py`). All f,f branches in the bank (7: from rows 0, 31, 32, 33, 34, 189, 190) target slot 27 → row 3, the dash state. Row 3's branches: RP → row 203 (window 1–20), RK → row 216 (window 1–20). No other row is reachable from dash via RP/RK. Row 4 (run state) also branches RK → 216 (running kick = Konvict Kick).
- Row 203 = T3 f,f+2 K's Flicker: branch damage 20, attack_word 0x217 = mid, button RP2, limb armR; hit_frames [16,16,58,535,0,2]; Job 1 (king_on_pantera_leoman): stance duck-dip (deep lunge pose, feet grounded — lifts 0.07/0.08 m), dominant armR ext 1.091 at peakF 8, travel 0.936 m; engine harness (_attackClipPlan + _rootMotionApply): 0.847 m forward, 0.864 m peak, −0.399 m lateral. T3 movelist: K's Flicker, f,f+2, 20 dmg, Mid — exact match on damage + level + dash-only access.
- Row 216 = T3 f,f+4 Konvict Kick: branch damage 30, attack_word 0x217 = mid, button RK4, limb legR; hit_frames [15,15,54,535,0,8]; Job 1: stance standing, legR lift 1.183 m, travel 0.455 m; harness: 0.411 m forward, 0.604 m peak, −0.196 m lateral. T3 movelist: Konvict Kick, f,f+4, 30 dmg, Mid — exact match on damage + level + dash/run access. Harness active 15 also matches T7 Konvict Kick 15f startup (king_52); row 203's T3 active 16 differs from T7 Rolling Elbow 31f, as expected across games — the T3-internal evidence (branch + damage + level + button + limb + travel) is what identifies it.
- Both rows were already baked in rows.pack.json (256/652 baked) — no bake run needed.
- Mappings changed (5, all in game/assets/movesets/pantera.json): f,F+2 → 203 (was removed by the revert; donor 111 retired); f,F+4 → 216 (was removed; donor 114 retired); f,F+2~t7.king → 203 (field was row 260, a 10-hit string step); f,F+4~t7.king → 216 (field was row 69, the u+4 jump kick); CH.f,F+4 → 216 (field was row 69). The shadows' old field rows never actually played: their 'nearest' matches defer the anim tier past the donor tier in _attackClipPlan, so baseline playback for all three shadows was donors 111/114 — stand-ins either way. The new 'dash-branch' match label contains no 'nearest', so the anim tier fires before donor and the remapped rows play (proven by the shadow-only mutation run + the updated test). CH.f,F+4's row covers the Konvict Kick first hit; the DDT follow-up is a separate mapping question, not claimed solved here.
- Why T3 is used at all (instruction-gate law): no T5/T6/T7/T8/TTT2 animation is decoded for these dash moves — T7 king_49/king_52 motion is not decoded, T6 DATA401 is encrypted, TTT2 is not extracted, T5/T8 motion is not acquired. T7/T8 frame data carries timing/level only, no motion bytes.
- Test honesty: test/root-motion.test.mjs now asserts the TRUE rows (row:203/row:216, kind anim) with measured travel bounds — it no longer encodes donor behavior. Green now proves the dash inputs play their own T3 dash rows and travel; it does NOT prove T7 animation identity (see fallback status above).
- Flagged, NOT changed (out of this PR's scope, follow-up owed): pantera.json entries "4" and "4_r216" point at row 216 — WRONG for a standing input (the branch graph proves row 216 is reached ONLY from dash row 3 and run row 4, never from standing; the "true-map" matcher mislabeled the dash kick as standing 4). Standing 4's true rows need their own adjudication (the earlier audit listed 106/124 alongside the now-disproven 216; neither 106 nor 124 is verified here); this PR does not touch "4"/"4_r216".

## Torch Batch 1 fallback (LP1/RP2-only strings, 2026-10-25)
Verified rows 32/33/34/44/45/46/171/174/355/356 are FALLBACK
(T3 anna rows, bank anna / BOUND bank: torch's in-game bank is anna
per fighter.js #1096 FIGHTER_BANK torch->anna + moveset anim_bank
anna), to be re-matched to T7 Anna rows when extraction lands.
Torch is the FIRST dual-bank fighter in the pipeline: its T3 moves
carry jin (145) AND anna (224) banks, and every step adjudicates
against ITS OWN move's bank (file-level t3_source jin is never
assumed for all moves). Jin-bank gate-verified rows 92/93/183/220/
221/222/223/249 are BANK-BLOCKED, NOT fallback-wired: the #1096
step-plan branch resolves row:N against the bound anna bank only,
so wiring a jin row would play anna row N - a wrong-bank clip.
They are recorded as bank_verified_row on review steps, to be
promoted mechanically when per-step-bank engine support lands.
Rejected rows are NOT fallback - rejected evidence, not wired or
held. Jin-bank rules, per-bank evidence (documented in
docs/movesets/TORCH-BATCH1-STEP-PLANS-2026-10-25.md): row 35 EXISTS
(starts-airborne, btn 1) - airborne, fails ground steps; row 220
EXISTS (standing RP2, btn 2) - torch RP2 move 2's own row, NOT
bryan's button-0 row 220; row 216 EXISTS (jump, btn 0) - fails
every single-button gate. Jin row 248 (torch LP1 move 1's own row)
is STANDING but button 12 - it FAILS every single-LP1 step under
exact-equality (demonio row 177 btn-12 + scimitar row 184 btn-9
precedent). Anna-bank rules, per-bank evidence (first-ever anna
adjudication): row 35 EXISTS (starts-airborne, btn 1) - airborne,
fails ground steps; row 220 EXISTS in hit_frames (button 0) but is
ABSENT from Job 1 - fails every single-button gate; row 216 EXISTS
in hit_frames (button 0) but is ABSENT from Job 1 - same treatment.
Torch basics unchanged #1096 vs main (LP1 move 1 jin r248, RP2 move 2
jin r220, LK3 move 3 jin r195, RK4 move 4 jin r199); re-baseline
moves + strings deep-equal, row-changed 0, damage-only 0, so
suspended-drift steps are 0. Torch was NEVER purged by #1039
(t8_quarantine_20261024 key ABSENT) - no #988 dependency. Gap-1:
jin hit_frames + skeleton IDENTICAL, rows.pack ADDITIVE-ONLY drift
(220 b1096 rows unchanged on main, main adds 6 rows, 0 changed, 0
removed - affected fills 0); anna all three blobs IDENTICAL.
GATE-ONLY batch: Job 2 torch entries 0, Job 3 torch entries 0 -
Job 3 fills 0 and Job 4 joins 0 by data absence (bank-level Job 4
candidates jin 47 / anna 45 cannot join without Job 2 torch
entries; a join never promotes anyway). Standing rows verified for
crouch-context steps (d/f+1+2,2 step 2 anna row 174; d+1+2 family
jin rows 92/93/183 BANK-BLOCKED) follow the demonio Batch 1
precedent: the gate flags crouch rows for non-crouch steps, not
standing rows for crouch steps. Canonicalization is the CORRECTED
rule (strip only a trailing ~t[378] source-variant suffix): Torch
Batch 1 contains ZERO input-~ canonicals; file-wide exactly ONE
input-~ comma key exists, d+4,1~4 (T8 Anna, LP1+RK4 - later-batch
scope). T8-sourced prefixes with no T3 row get their correct clips
from #988 Step 2 (original T8 refs), never from a T3 row recorded
as correct. Formatter note: torch-1096.json round-trips ONLY as
json.dumps(indent=2) with no trailing newline (ensure_ascii=True);
the generic ensure_ascii=False + newline prescription would
rewrite the whole file, so this lane uses the file's own formatter
and the committed diff is exactly 1 addition.
