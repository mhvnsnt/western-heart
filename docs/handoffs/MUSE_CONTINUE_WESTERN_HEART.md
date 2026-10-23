# Muse: continue Western Heart (handoff 2026-10-14)

Read first: [AGENTS.md](../../AGENTS.md), [RULES_NO_GUESSING.md](../RULES_NO_GUESSING.md), [anim/PROCEDURAL_AUDIT.md](../anim/PROCEDURAL_AUDIT.md). Your fan-asset lane ([MUSE_FAN_ASSETS_HANDOFF.md](MUSE_FAN_ASSETS_HANDOFF.md)) continues in parallel; this doc is the core-game priority order.

**Do not edit** creation suite files (Repo Co Dev: `customization/`, `docs/creation-suite/`) or physics files (Jigglebot: physics sandbox repos, `lab-jiggle*`). Small PRs, merge only when clean, delete nothing.

## Priority order (do not reorder)

### 1. Real teardown animations everywhere (replace procedural)
State: `docs/anim/PROCEDURAL_AUDIT.md` sections 1 and 5. Done so far: T3 King stances + 4 win poses + heavy/grab baked onto Pantera P1 and T3 King (`lab/game/assets/*_t3real.glb`), wired in `lab/game/scripts/fighter.gd`.
Next, in order:
1. Common-bank anims: make `pose_assemble.assemble` read anim words `>= motion.COMMON_FLAG` from `teardown/tekken3/animations/divmot99_common.bin`; re-bake `t3_light` (slot 0xD06) and `t3_medium` (0xD2F).
2. Identify locomotion/reaction slots (walk_fwd, walk_back, crouch, jump, sidestep, hit, block, ko) from `movesets/moveset_king.csv` (`step_per_frame`, `stance_slot`, branch inputs `f,f`/`b,b`) and n0madic `docs/research/code/fighter.md`; bake them; add to the `REAL` map.
3. Bake the other 6 T3 banks (jin, xiaoyu, bryan, heihachi, gunjack, yoshimitsu) for the fighters mapped to them (`docs/t7t8-reference/` fighter->body map).
4. Browser build `game/js/fighter.js`: bake onto the Mixamo-49 rigs (needs rest-orientation conversion), then switch the CCD-IK layer off where a real clip exists.
5. Arms-folded: no source in T3 King. Search WWF No Mercy anims (`teardown/wwf-no-mercy`), WMXIX YANM (`teardown/wwe-wrestlemania-xix`), TTT2 (release `ttt2-7z-v1`) and T6 (PPSSPP dump) for a real crossed-arms taunt/intro; log MISSING if not found.

Commands:
```
git clone --depth 1 --filter=blob:none --sparse https://github.com/n0madic/Tekken3Remake /workspace/t3anim/t3r && (cd /workspace/t3anim/t3r && git sparse-checkout set tools/research docs)
export T3REMAKE_RESEARCH=/workspace/t3anim/t3r/tools/research
python3 lab/tools/t3_motion_bake.py <in.glb> <out_t3real.glb> --clips name=slot,... [--json-dir assets/anim/t3/<fighter>]
godot --headless --path lab/game -s res://tests/test_move_table.gd
sh lab/game/tests/run_match_headless.sh            # must print MATCH TEST: PASS
xvfb-run -a godot --rendering-driver opengl3 --path lab/game -s res://tools/render_title_hero_real.gd -- /tmp/out <clip> <sec> 180
```
Proof each PR: clip list from `animations[].extras`, a contact sheet you actually viewed, SHA-256s.

### 2. Make every in-game character proprietary (kitbash, rescan, retexture)
For each roster fighter (`ROSTER.md`, `roster/`, 24 characters, checklist in agent-ops board note PR #17): kitbash from owned teardown parts + owner originals, rescan/retopo, retexture into the Eastern Mind / Western Heart universe look (`CANON.md`, `DESIGN.md`). Keep originals; write to new files; rig with `lab/tools/autorig.py`; check with `python3 lab/tests/test_rig_check.py`. Weight-paint/hole fixes: use the rig-repair pipeline (`/workspace/rig-repair`, see its README) before any render.

### 3. Renders and character art cards
Only after 1 and 2 for that character. Poses must come from REAL baked clips (`t3_*`), never authored clips. Tools: `lab/game/tools/render_title_hero_real.gd`, `lab/game/tools/render_ui_portraits.gd`, `game/ui-wh/tools/make_wallpaper.py`, T-pose sheets in `docs/tpose-refs/`. Title variants: v1–v3 legacy, v4 = real T3 win pose (`?title=v4`); default stays v3 until the owner picks.

### 4. Everything else Western Heart
Menus (`game/ui-wh`, `?ui=wh`), move-set editor using `docs/t7t8-reference/` frame data, stages, audio, playtests (`docs/PLAYTEST-METHOD.md`).

## Disk rules (box disk is nearly full)
Sparse clones only (`git clone --filter=blob:none --sparse`, `git sparse-checkout set <dirs>`); delete scratch when done; offload to box storage only after `sha256sum` matches on both sides.

## Progress 2026-10-14 (round 2)
- Done: T3 common-bank decode, so light and medium attacks are baked (PR #136). King walk, crouch, jump, sidestep, hit, block and KO baked and wired with `--anim=authored` as fallback (PR #136). Jin, Xiaoyu, Bryan, Gun Jack and Yoshimitsu baked (PR #137).
- MISSING: Heihachi (heihachi191 KMD has no hip or shoulder vertex data) and a real arms-folded pose (see the audit, Update 4), so there is no title v5.
- Browser build: the `pantera.glb` L/R skin swap is fixed as `pantera_fixed.glb` (tools/rig_repair case 1). For demonio, the Godot render ignores the arm tracks even though the CPU skin is correct. See `docs/anim/PROCEDURAL_AUDIT.md` Update 4.
- Lab crouch, jump and sidestep states: DONE (audit Update 5). Stand-up slot 60, jump displacement and evasion are still missing.


## INSTRUCTION GATE: Owner law, data source priority (Oct 23, 2026, 2:19 PM CT)

> **Western Heart data (moves, animations, frame data, menus, character select) comes from Tekken 5, 6, 7, 8 and TTT2. Tekken 3 is only a last-resort fallback, and every T3 use must be logged with the reason no T5/6/7/8/TTT2 source was available.**

- Search T5/T6/T7/T8/TTT2 teardowns first. Use T3 only when none of them has the data, and log the T3 use (file, clip, reason) in `docs/anim/PROCEDURAL_AUDIT.md`.
