# Bob motion bank — precise gap (2026-10-23)

**Source priority (owner standing directive 2026-10-23): TTT2/T6 FIRST,
T3 LAST (fallback only).** Bob Richards debuted in Tekken 6 — T3 has no Bob
stream and can never fill this gap. A dedicated extraction coordinator
is driving T5/T6/TTT2/T7 to 100%; this doc is the intake manifest for
that lane — pull what exists now, fill the precise gaps below rather
than settling for substitutes.

Burger's canon base is Bob Richards (Tekken 6 debut, 2007). His
MOVESET data is now complete on Bob's own tables (552 moves, T7+T8 merged —
see `game/assets/movesets/burger.json` `merge_sources.added.burger_pull_20261023`:
161/161 T8 inputs reachable, 281/281 T7 rows by id, 0 genuinely-missing).
His MOTION is not: he still binds the `bryan` proxy bank
(`t3_source: 'bryan'` → `SOURCE_TO_BANK` → `assets/anim/t3/bryan/`), so his
stance/idle, intro, win pose, round-win pose, and generic actions are Bryan's
T3 clips today. This doc records exactly what is missing and what unblocks it.
Nothing here is stubbed — per the isolation doctrine a fighter is never
animated with another character's clips, and no fake bank is shipped.

## The missing bank — FIGHT vs SHOW (SHOW-ANIMATION LOCK, owner 2026-10-23)

Show animations and fight moves are SEPARATE LOCKED SETS. When Bob motion
is decoded, its clips are tagged at intake and the two sets never mix:

- **FIGHT** — moveset moves, stances used in combat → the moveset
  (`game/assets/movesets/burger.json`) and the combat animation bank.
- **SHOW** — win poses, intro poses, taunts, cutscene animations → the
  intro/win slots (`T3_CLIP_DEFS` `intro`/`win` entries) and cutscenes ONLY.
  SHOW clips must NEVER enter Burger's moveset without the user's explicit
  approval. The game-code lock enforces this; this doc is the intake manifest
  it reads.

Target: `game/assets/anim/t3/bob/` registered in `game/js/t3anims.js`
`T3_BANKS` as `bob: 'assets/anim/t3/bob/'`, plus `bob: 'bob'` in
`SOURCE_TO_BANK` so `bankIdFor('burger')` binds it.
Required files (wh-anim/1 schema — see `game/assets/anim/t3/paul/`):

### FIGHT clips → combat bank + moveset
- `t3_neutral.json` (stance/idle — Bob's signature stance, used in combat)
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

## Source A — TTT2 (best modern source; FIRST priority)

**Extraction coordinator: Bob's TTT2 motion is a named target for the
T5/T6/TTT2/T7 100% lane — the blockers below are what that lane must
clear, in order.** Bob's TTT2 motion lives inside the Xbox 360 STFS
containers (`teardown/tekken-tag-tournament-2/`). Status (2026-10-23):
TTT2 teardown ~15% — 26/26 chunks downloaded, STFS extraction pending;
no Bob moveset or motion bank on disk yet.

## Source B — T6 (Bob's debut game; FIRST priority with TTT2)

**Extraction coordinator: Bob's T6 motion is the debut-game source —
same lane, same priority as TTT2.** Motion lives in the encrypted
bulk data region (`teardown/tekken6/`); the decrypt lane works on
branch `feature/tekken6-100-teardown`.

## Why T3 can't fill it (LAST priority — fallback only, and empty here)

Bob did not exist in Tekken 3 (1997; he debuted in Tekken 6, 2007).
There is no Bob divmot stream; `teardown/tekken3/animations/` has no
stream for him. Per the owner's source-priority directive, T3 is
fallback only — and for Bob the fallback is empty. Do not settle for
a T3 substitution (the current `bryan` proxy is flagged, not blessed).

## Unblock sequence (for the lane that cracks either source)

1. Decode Bob's motion stream → convert to wh-anim/1
   (`fps: 30`, `rot_xyzw` per bone, `root_t`, 22 canonical bones —
   same shape `jsonToClip` reads in `game/js/t3anims.js`).
2. **Tag every clip FIGHT or SHOW** per the intake manifest above before
   anything lands (SHOW-ANIMATION LOCK).
3. Bake: `python3 tools/anim/t3_row_bake.py --bank bob` (FIGHT action
   clips + full move-index `rows.pack.json`; SHOW clips bake to the
   intro/win slots only).
4. Register `bob` in `T3_BANKS` + `SOURCE_TO_BANK`; Burger binds his own
   bank — combat stance, per-move rows go live with no further wiring
   (the 552 moves already carry `anim_ref`s); intro/win poses wire to
   their slots, never the moveset.

## Moveset status (done this pass)

`game/assets/movesets/burger.json`: 552 → **552 moves** (+0 — the T8/T7
frame-data diff found 0 genuinely-missing inputs: 161/161 T8 `bob`
inputs and 281/281 T7 `bob` rows already reachable; nothing re-added).
Verified: `node --test game/tests/fighter-completeness.test.mjs` green.

**SHOW-ANIMATION LOCK (owner 2026-10-23):** the file carries
`anim_set_lock` at file level — every move in
`game/assets/movesets/burger.json` is the FIGHT set. SHOW animations
(win/intro poses, taunts, cutscenes) are tracked in the FIGHT/SHOW
sections above — they wire to intro/win slots and cutscenes only and
must NEVER enter the moveset without the user's explicit approval.
