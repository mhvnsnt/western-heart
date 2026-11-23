# Steve motion bank — precise gap (2026-10-23)

**Source priority (owner standing directive 2026-10-23): T8 frame data FIRST,
then T7, then TTT2/T6/T5, T3 LAST (fallback only).** Steve debuted in
Tekken 4 (2001) — T3 has no Steve stream and can never fill this gap.
This doc is the intake manifest for the motion lane: pull what exists now,
fill the precise gaps below rather than settling for substitutes.

Zui's canon base is Steve Fox. His MOVESET data is now complete on Steve's
own tables (661 moves, T7+T8 merged — see
`game/assets/movesets/zui.json`
`merge_sources.added.batch2_pull_20261023`; the 2026-10-23 T8 diff added the
7 genuinely-missing moves: Back/Left/Right throw, TFA.1, TFA.2, H.LNH.P,
after_2steps+1). His MOTION is not: he still binds the flagged `jin`
substitution bank (`t3_source: 'jin'` → `SOURCE_TO_BANK` →
`assets/anim/t3/jin/`), so his stance/idle, intro, win pose, round-win pose,
and generic actions are Jin's T3 clips today. This doc records exactly what
is missing and what unblocks it. Nothing here is stubbed — per the
isolation doctrine a fighter is never animated with another character's
clips, and no fake bank is shipped.

## The missing bank — FIGHT vs SHOW (SHOW-ANIMATION LOCK, owner 2026-10-23)

Show animations and fight moves are SEPARATE LOCKED SETS. When Steve motion
is decoded, its clips are tagged at intake and the two sets never mix:

- **FIGHT** — moveset moves, stances used in combat → the moveset
  (`game/assets/movesets/zui.json`) and the combat animation bank.
- **SHOW** — win poses, intro poses, taunts, cutscene animations → the
  intro/win slots (`T3_CLIP_DEFS` `intro`/`win` entries) and cutscenes ONLY.
  SHOW clips must NEVER enter Zui's moveset without the user's explicit
  approval. The game-code lock enforces this; this doc is the intake manifest
  it reads.

Target: `game/assets/anim/t3/steve/` registered in `game/js/t3anims.js`
`T3_BANKS` as `steve: 'assets/anim/t3/steve/'`, plus `steve: 'steve'` in
`SOURCE_TO_BANK` so `bankIdFor('zui')` binds it.
Required files (wh-anim/1 schema — see `game/assets/anim/t3/paul/`):

### FIGHT clips → combat bank + moveset
- `t3_neutral.json` (stance/idle — Steve's signature stance, used in combat),
  `t3_stance_b/c/d/e.json` (PAB/FLK/LNH/DCK/SWY stance idles — combat stances)
- `t3_light.json`, `t3_medium.json`, `t3_heavy.json`, `t3_grab.json`
- `t3_block.json`, `t3_block_b.json`, `t3_hit.json`, `t3_hit_launch.json`,
  `t3_ko.json`
- `t3_walk_fwd.json`, `t3_walk_back.json`, `t3_dash_fwd.json`,
  `t3_backdash.json`, `t3_crouch.json`, `t3_crouch_hold.json`,
  `t3_jump_fwd/back/up.json`, `t3_sidestep_a/b/c/d.json`
- `rows.pack.json` — per-move clips baked with `tools/anim/t3_row_bake.py`
- `skeleton.json`

### SHOW clips → intro/win slots + cutscenes ONLY (never the moveset)
- `t3_stance.json` — intro pose → wires to the `intro` slot only
- `t3_win_rp.json` — win pose → wires to the `win` slot only
- Future: taunts, cutscene animations — cutscene/intro system only.

No clip ships untagged: the intake lane stamps every file FIGHT or SHOW
here before it lands, and the moveset lane rejects SHOW-tagged clips.

## Source lanes (in priority order)

1. **T8** — Steve is current in T8; motion extraction from the T8 lane
   is the first-choice source when its tooling lands.
2. **T7** — full Steve move/motion set present.
3. **TTT2 / T6 / T5** — fallback only if T7/T8 lanes stall.
4. **T3** — never: no Steve stream exists.

## Unblock checklist
- [ ] T7 or T8 Steve motion extracted to `game/assets/anim/t3/steve/`
- [ ] Every clip tagged FIGHT or SHOW at intake
- [ ] `T3_BANKS` + `SOURCE_TO_BANK` wiring in `game/js/t3anims.js`
- [ ] `t3_source: 'jin'` substitution retired for zui
- [ ] FIGHT-vs-SHOW automated test passes (no SHOW clip in combat)
