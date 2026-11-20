# Zafina motion bank — precise gap (2026-10-23)

**Source priority (owner standing directive 2026-10-23): TTT2/T6/T7 FIRST,
T3 LAST (fallback only).** Zafina debuted in Tekken 6 — T3 has no Zafina
stream and can never fill this gap. A dedicated extraction coordinator
is driving T5/T6/TTT2/T7 to 100%; this doc is the intake manifest for
that lane — pull what exists now, fill the precise gaps below rather
than settling for substitutes.

Mariposa Monarch's canon base is Zafina (Tekken 6 debut, 2007). Her
MOVESET data is now complete on Zafina's own tables (518 moves, T7+T8 merged —
see `game/assets/movesets/mariposa-monarch.json`
`merge_sources.added.zafina_pull_20261023`). Her MOTION is not: she still binds
the flagged `xiaoyu` substitution bank (`t3_source: 'xiaoyu'` →
`SOURCE_TO_BANK` → `assets/anim/t3/xiaoyu/`), so her stance/idle, intro,
win pose, round-win pose, and generic actions are Xiaoyu's T3 clips today.
This doc records exactly what is missing and what unblocks it.
Nothing here is stubbed — per the isolation doctrine a fighter is never
animated with another character's clips, and no fake bank is shipped.

## The missing bank — FIGHT vs SHOW (SHOW-ANIMATION LOCK, owner 2026-10-23)

Show animations and fight moves are SEPARATE LOCKED SETS. When Zafina motion
is decoded, its clips are tagged at intake and the two sets never mix:

- **FIGHT** — moveset moves, stances used in combat → the moveset
  (`game/assets/movesets/mariposa-monarch.json`) and the combat animation bank.
- **SHOW** — win poses, intro poses, taunts, cutscene animations → the
  intro/win slots (`T3_CLIP_DEFS` `intro`/`win` entries) and cutscenes ONLY.
  SHOW clips must NEVER enter Mariposa Monarch's moveset without the user's
  explicit approval. The game-code lock enforces this; this doc is the intake
  manifest it reads.

Target: `game/assets/anim/t3/zafina/` registered in `game/js/t3anims.js`
`T3_BANKS` as `zafina: 'assets/anim/t3/zafina/'`, plus `zafina: 'zafina'` in
`SOURCE_TO_BANK` so `bankIdFor('mariposa-monarch')` binds it.
Required files (wh-anim/1 schema — see `game/assets/anim/t3/paul/`):

### FIGHT clips → combat bank + moveset
- `t3_neutral.json` (stance/idle — Zafina's signature stance, used in combat),
  `t3_stance_b/c.json` (MNT/SCR/TRT stance idles — combat stances)
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

## Source A — TTT2 / T6 (best modern sources; FIRST priority)

**Extraction coordinator: Zafina's TTT2/T6 motion is a named target for the
T5/T6/TTT2/T7 100% lane — that lane owns the container paths and decrypt
blockers (see `teardown/tekken-tag-tournament-2/TEARDOWN.md` and
`teardown/tekken6/TEARDOWN.md`).** Zafina exists in Tekken 6, TTT2, T7 and
T8 — any of those streams fills this gap; TTT2/T6 are first priority per
the owner's source order.

## Source B — T7 (FIRST priority with TTT2/T6)

Zafina's T7 movelist and frame data are already in-repo
(`docs/t7t8-reference/frame-data-t7/zafina.json`,
`docs/t7t8-reference/frame-data-t8-full/zafina.json`); her T7 motion
stream is the same lane's target. Motion first, frame data already done.

## Why T3 can't fill it (LAST priority — fallback only, and empty here)

Zafina did not exist in Tekken 3 (1997). There is no Zafina divmot stream;
`teardown/tekken3/animations/` has 20 character streams and none is hers.
Per the owner's source-priority directive, T3 is fallback only — and for
Zafina the fallback is empty. Do not settle for a T3 substitution.

## Unblock sequence (for the lane that cracks either source)

1. Decode Zafina's motion stream → convert to wh-anim/1
   (`fps: 30`, `rot_xyzw` per bone, `root_t`, 22 canonical bones —
   same shape `jsonToClip` reads in `game/js/t3anims.js`).
2. **Tag every clip FIGHT or SHOW** per the intake manifest above before
   anything lands (SHOW-ANIMATION LOCK).
3. Bake: `python3 tools/anim/t3_row_bake.py --bank zafina` (FIGHT action
   clips + full move-index `rows.pack.json`; SHOW clips bake to the
   intro/win slots only).
4. Register `zafina` in `T3_BANKS` + `SOURCE_TO_BANK`; Mariposa Monarch binds
   her own bank — combat stance, per-move rows go live with no further wiring
   (the 518 moves already carry `anim_ref`s); intro/win poses wire to
   their slots, never the moveset.

## Moveset status (done this pass)

`game/assets/movesets/mariposa-monarch.json`: 508 → **518 moves** (+10 from the
T7/T8 frame-data diff: `BT.2`, `BT.4`, `FUFT.+3+4`, `FUFT.1+2`, `FUFT.3`,
`FUFT.4`, `FUFT.d+3`, `GROUNDED.3`, `GROUNDED.4`, `TACKLE.2`).
All 10 resolve through the game's own `resolveMove`. Verified:
`_prepare` slot simulation — 10/10 new keys resolve.

**SHOW-ANIMATION LOCK (owner 2026-10-23):** every move in
`game/assets/movesets/mariposa-monarch.json` is tagged `"set": "FIGHT"` at file
level (`anim_set_lock`) and per-move on the 10 pulled this pass. SHOW
animations (win/intro poses, taunts, cutscenes) are tracked in the
FIGHT/SHOW sections above — they wire to intro/win slots and cutscenes
only and must NEVER enter the moveset without the user's explicit
approval.
