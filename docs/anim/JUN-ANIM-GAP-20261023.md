# Jun Kazama motion bank — precise gap (2026-10-23)

**Source priority (owner standing directive 2026-10-23): TTT2/T8 FIRST,
T3 LAST (fallback only).** Jun Kazama was not in Tekken 3 — T3 has no Jun
stream and can never fill this gap. She returned in Tekken Tag
Tournament 2 and Tekken 8, which are the FIRST-priority sources. A
dedicated extraction coordinator is driving T5/T6/TTT2/T7 to 100%; this
doc is the intake manifest for that lane — pull what exists now, fill the
precise gaps below rather than settling for substitutes.

Megami's canon base is Jun Kazama (Tekken Tag Tournament 2). Her MOVESET
data is now complete on Jun's own tables (299 moves, TTT2-documented +
T8 merged — see `game/assets/movesets/megami.json`
`merge_sources.added.t8_pull_20261023`). Her MOTION is not: no
`game/assets/anim/t3/jun/` bank exists, so her stance/idle, intro, win
pose, round-win pose, and generic actions have no Jun clips today. This
doc records exactly what is missing and what unblocks it. Nothing here is
stubbed — per the isolation doctrine a fighter is never animated with
another character's clips, and no fake bank is shipped. Do NOT
substitute a wrong bank — file the gap, don't fill it with someone
else's motion.

## The missing bank — FIGHT vs SHOW (SHOW-ANIMATION LOCK, owner 2026-10-23)

Show animations and fight moves are SEPARATE LOCKED SETS. When Jun motion
is decoded, its clips are tagged at intake and the two sets never mix:

- **FIGHT** — moveset moves, stances used in combat → the moveset
  (`game/assets/movesets/megami.json`) and the combat animation bank.
- **SHOW** — win poses, intro poses, taunts, cutscene animations → the
  intro/win slots (`T3_CLIP_DEFS` `intro`/`win` entries) and cutscenes ONLY.
  SHOW clips must NEVER enter Megami's moveset without the user's explicit
  approval. The game-code lock enforces this; this doc is the intake manifest
  it reads.

Target: `game/assets/anim/t3/jun/` registered in `game/js/t3anims.js`
`T3_BANKS` as `jun: 'assets/anim/t3/jun/'`, plus `jun: 'jun'` in
`SOURCE_TO_BANK` so `bankIdFor('megami')` binds it.
Required files (wh-anim/1 schema — see `game/assets/anim/t3/paul/`):

### FIGHT clips → combat bank + moveset
- `t3_neutral.json` (stance/idle — Jun's Kazama-style stance, used in combat),
  `t3_stance_b/c.json` (Genjitsu/Izumo stance idles — combat stances)
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

## Source A — TTT2 (Jun's return game; FIRST priority)

**Extraction coordinator: Jun's TTT2 motion is a named target for the
T5/T6/TTT2/T7 100% lane.** Megami's kit is documented from the TTT2 Jun
movelist — the motion for those same moves is the first pull target.
Same blockers as the Lars TTT2 lane (STFS containers, format RE) — see
`docs/anim/LARS-ANIM-GAP-20261023.md` for the standing blocker list.

## Source B — T8 (newest data; FIRST priority)

T8 ships Jun Kazama with a full movelist (149 moves in
`docs/t7t8-reference/frame-data-t8-full/jun.json`, merged into Megami's
moveset this pass). T8 motion extraction is future work — same priority
as TTT2, behind no other source.

## Why T3 can't fill it (LAST priority — fallback only, and empty here)

Jun Kazama was not in Tekken 3 (1997). There is no Jun divmot stream;
`teardown/tekken3/animations/` has 20 character streams and none is hers.
Per the owner's source-priority directive, T3 is fallback only — and for
Jun the fallback is empty. Do not settle for a T3 substitution.

## Unblock sequence (for the lane that cracks either source)

1. Decode Jun's motion stream → convert to wh-anim/1
   (`fps: 30`, `rot_xyzw` per bone, `root_t`, 22 canonical bones —
   same shape `jsonToClip` reads in `game/js/t3anims.js`).
2. **Tag every clip FIGHT or SHOW** per the intake manifest above before
   anything lands (SHOW-ANIMATION LOCK).
3. Bake: `python3 tools/anim/t3_row_bake.py --bank jun` (FIGHT action
   clips + full move-index `rows.pack.json`; SHOW clips bake to the
   intro/win slots only).
4. Register `jun` in `T3_BANKS` + `SOURCE_TO_BANK`; Megami binds her own
   bank — combat stance, per-move rows go live with no further wiring
   (the 299 moves already carry `anim_ref`s); intro/win poses wire to
   their slots, never the moveset.

## Moveset status (done this pass)

`game/assets/movesets/megami.json`: 150 → **299 moves** (+149 from the
T8 frame-data diff — every T8 Jun move genuinely missing; keyed by
notation when free, else `<notation>~t8.jun` per
`tools/moveset-merge/merge_sources.py`). Strings 0 → 18, specials 0 → 7.
All 149 resolve through the game's own `resolveMove`. TTT2-documented
kit (150 moves) untouched.

**SHOW-ANIMATION LOCK (owner 2026-10-23):** every move in
`game/assets/movesets/megami.json` is tagged at file level
(`anim_set_lock`) and per-move on the 149 pulled this pass
(`"set": "FIGHT"`). SHOW animations (win/intro poses, taunts,
cutscenes) are tracked in the FIGHT/SHOW sections above — they wire to
intro/win slots and cutscenes only and must NEVER enter the moveset
without the user's explicit approval.
