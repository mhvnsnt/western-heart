# Katarina motion bank — precise gap (2026-10-23)

**Source priority (owner standing directive 2026-10-23): T7 FIRST
(Katarina debuted in Tekken 7 — no earlier source exists), T3 LAST
(fallback only, and empty here).** A dedicated extraction coordinator
is driving T5/T6/TTT2/T7 to 100%; this doc is the intake manifest for
that lane — pull what exists now, fill the precise gaps below rather
than settling for substitutes.

Michiko's canon base is Katarina Alves (Tekken 7 debut, 2015). Her
MOVESET data is now complete on Katarina's own tables (344 moves, T7 —
see `game/assets/movesets/michiko.json`
`merge_sources.added.katarina_pull_20261023`: 189/189 T7 `katarina` rows
by id, 0 genuinely-missing; T8 has no Katarina — verified in
`game/data/t8_frame_tables.json`). Her MOTION is not: she still binds
the flagged `jin` substitution bank (`t3_source: 'jin'` →
`SOURCE_TO_BANK` → `assets/anim/t3/jin/`), so her stance/idle, intro,
win pose, round-win pose, and generic actions are Jin's T3 clips today.
This doc records exactly what is missing and what unblocks it.
Nothing here is stubbed — per the isolation doctrine a fighter is never
animated with another character's clips, and no fake bank is shipped.

## The missing bank — FIGHT vs SHOW (SHOW-ANIMATION LOCK, owner 2026-10-23)

Show animations and fight moves are SEPARATE LOCKED SETS. When Katarina
motion is decoded, its clips are tagged at intake and the two sets never
mix:

- **FIGHT** — moveset moves, stances used in combat → the moveset
  (`game/assets/movesets/michiko.json`) and the combat animation bank.
- **SHOW** — win poses, intro poses, taunts, cutscene animations → the
  intro/win slots (`T3_CLIP_DEFS` `intro`/`win` entries) and cutscenes ONLY.
  SHOW clips must NEVER enter Michiko's moveset without the user's
  explicit approval. The game-code lock enforces this; this doc is the
  intake manifest it reads.

Target: `game/assets/anim/t3/katarina/` registered in
`game/js/t3anims.js` `T3_BANKS` as `katarina: 'assets/anim/t3/katarina/'`,
plus `katarina: 'katarina'` in `SOURCE_TO_BANK` so
`bankIdFor('michiko')` binds it.
Required files (wh-anim/1 schema — see `game/assets/anim/t3/paul/`):

### FIGHT clips → combat bank + moveset
- `t3_neutral.json` (stance/idle — Katarina's signature stance, used in
  combat)
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

## Source A — T7 (Katarina's debut game; FIRST and ONLY priority)

**Extraction coordinator: Katarina's T7 motion is a named target for the
T5/T6/TTT2/T7 100% lane.** Katarina debuted in Tekken 7 (2015) — no
T5/T6/TTT2/T3 source exists for her, so T7 is first, last, and only.
Her T7 motion must come from the T7 extraction work (same lane that is
driving T7 to 100%).

## Why T3 can't fill it (LAST priority — fallback only, and empty here)

Katarina did not exist before Tekken 7 (2015). There is no Katarina
divmot stream; `teardown/tekken3/animations/` has no stream for her.
Per the owner's source-priority directive, T3 is fallback only — and
for Katarina the fallback is empty. Do not settle for a T3 substitution
(the current `jin` proxy is flagged, not blessed).

## Unblock sequence (for the lane that cracks the T7 source)

1. Decode Katarina's T7 motion stream → convert to wh-anim/1
   (`fps: 30`, `rot_xyzw` per bone, `root_t`, 22 canonical bones —
   same shape `jsonToClip` reads in `game/js/t3anims.js`).
2. **Tag every clip FIGHT or SHOW** per the intake manifest above before
   anything lands (SHOW-ANIMATION LOCK).
3. Bake: `python3 tools/anim/t3_row_bake.py --bank katarina` (FIGHT action
   clips + full move-index `rows.pack.json`; SHOW clips bake to the
   intro/win slots only).
4. Register `katarina` in `T3_BANKS` + `SOURCE_TO_BANK`; Michiko binds
   her own bank — combat stance, per-move rows go live with no further
   wiring (the 344 moves already carry `anim_ref`s); intro/win poses wire
   to their slots, never the moveset.

## Moveset status (done this pass)

`game/assets/movesets/michiko.json`: 344 → **344 moves** (+0 — the T7
frame-data diff found 0 genuinely-missing moves: 189/189 T7 `katarina`
rows already by id; T8 has no Katarina; nothing re-added). Verified:
`node --test game/tests/fighter-completeness.test.mjs` green.

**SHOW-ANIMATION LOCK (owner 2026-10-23):** the file carries
`anim_set_lock` at file level — every move in
`game/assets/movesets/michiko.json` is the FIGHT set. SHOW animations
(win/intro poses, taunts, cutscenes) are tracked in the FIGHT/SHOW
sections above — they wire to intro/win slots and cutscenes only and
must NEVER enter the moveset without the user's explicit approval.
