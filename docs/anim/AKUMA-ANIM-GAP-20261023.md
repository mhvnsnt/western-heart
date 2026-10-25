# Akuma motion bank — precise gap (2026-10-23)

**Source priority (owner standing directive 2026-10-23): TTT2/T6 FIRST,
T3 LAST (fallback only).** Akuma debuted as a guest in Tekken 7 — T3 has
no Akuma stream and can never fill this gap. A dedicated extraction
coordinator is driving T5/T6/TTT2/T7 to 100%; this doc is the intake
manifest for that lane — pull what exists now, fill the precise gaps below
rather than settling for substitutes.

Dio's canon base is Akuma (Tekken 7 guest, 2015). His MOVESET data is now
complete on Akuma's own T7 tables (275 moves, full t7chicken import — see
`game/assets/movesets/dio.json` `t7_import_note`). His MOTION is not: he
still binds the flagged `heihachi` substitution bank (`t3_source:
'heihachi'` → `SOURCE_TO_BANK` → `assets/anim/t3/heihachi/`), so his
stance/idle, intro, win pose, round-win pose, and generic actions are
Heihachi's T3 clips today. This doc records exactly what is missing and
what unblocks it. Nothing here is stubbed — per the isolation doctrine a
fighter is never animated with another character's clips, and no fake
bank is shipped.

## The missing bank — FIGHT vs SHOW (SHOW-ANIMATION LOCK, owner 2026-10-23)

Show animations and fight moves are SEPARATE LOCKED SETS. When Akuma
motion is decoded, its clips are tagged at intake and the two sets never
mix:

- **FIGHT** — moveset moves, stances used in combat → the moveset
  (`game/assets/movesets/dio.json`) and the combat animation bank.
- **SHOW** — win poses, intro poses, taunts, cutscene animations → the
  intro/win slots (`T3_CLIP_DEFS` `intro`/`win` entries) and cutscenes ONLY.
  SHOW clips must NEVER enter Dio's moveset without the user's explicit
  approval. The game-code lock enforces this; this doc is the intake manifest
  it reads.

Target: `game/assets/anim/t3/akuma/` registered in `game/js/t3anims.js`
`T3_BANKS` as `akuma: 'assets/anim/t3/akuma/'`, plus `akuma: 'akuma'` in
`SOURCE_TO_BANK` so `bankIdFor('dio')` binds it.
Required files (wh-anim/1 schema — see `game/assets/anim/t3/paul/`):

### FIGHT clips → combat bank + moveset
- `t3_neutral.json` (stance/idle — Akuma's signature stance, used in combat)
- `t3_light.json`, `t3_medium.json`, `t3_heavy.json`, `t3_grab.json`
- `t3_block.json`, `t3_block_b.json`, `t3_hit.json`, `t3_hit_launch.json`,
  `t3_ko.json`
- `t3_walk_fwd.json`, `t3_walk_back.json`, `t3_dash_fwd.json`,
  `t3_backdash.json`, `t3_crouch.json`, `t3_crouch_hold.json`,
  `t3_jump_fwd/back/up.json`, `t3_sidestep_a/b/c/d.json`
- `rows.pack.json` — per-move clips baked with `tools/anim/t3_row_bake.py`
  (same pipeline as the 9 remainder banks, PR #405)
- `skeleton.json`

### SHOW clips → intro/win slots + cutscenes ONLY (never the moveset)
- `t3_stance.json` — intro pose → wires to the `intro` slot only
- `t3_win_rp.json` — win pose → wires to the `win` slot only
  (`t3_win_lp/lk/rk.json` optional alternates, same slot)
- Future: taunts, cutscene animations — cutscene/intro system only.

No clip ships untagged: the intake lane stamps every file FIGHT or SHOW
here before it lands, and the moveset lane rejects SHOW-tagged clips.

## Source A — Tekken 7 (only modern source; FIRST priority)

**Extraction coordinator: Akuma's T7 motion is a named target for the
T5/T6/TTT2/T7 100% lane — the blockers below are what that lane must
clear, in order.** Akuma's T7 motion lives in the Tekken 7 PC pak files
(Steam build; the user owns T7 — see game-ownership rule). Status: T7
frame data is fully extracted (`docs/t7t8-reference/frame-data-t7/akuma.json`,
47 characters, TekkenBot-extracted via t7chickenplus-graphql); motion
extraction is the open lane.

Blockers, in order:
1. **Pak extraction** — T7 Steam paks need uasset/uexp parsing (FModel
   route per `repo-FMODEL.md`) or the existing cue4parse pipeline.
2. **Format RE** — UE4 skeletal animation assets; retarget to the WH rig.
3. **wh-anim/1 conformance** — bake to the schema in `game/assets/anim/t3/paul/`
   and register in `T3_BANKS` + `SOURCE_TO_BANK`.

## Source B — TTT2/T6 (fallback)

Akuma does not appear in TTT2 or T6. No fallback exists below T7 for his
motion. Do not substitute another character's bank.

## What is NOT missing

- Moveset frame data: COMPLETE (275 moves, genuine T7 frame data).
- FIGHT/SHOW tagging: the moveset file carries `anim_set_lock` and every
  move is stamped `set: FIGHT` (SHOW-ANIMATION LOCK, owner 2026-10-23).
