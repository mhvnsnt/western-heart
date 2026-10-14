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
