# Raven motion bank — precise gap (2026-10-23)

**Source priority (owner standing directive 2026-10-23): T5/T6/TTT2/T7/T8
FIRST, T3 LAST (fallback only).** Raven debuted in Tekken 5 — T3 has no
Raven stream and can never fill this gap. A dedicated extraction
coordinator is driving T5/T6/TTT2/T7 to 100%; this doc is the intake
manifest for that lane — pull what exists now, fill the precise gaps
below rather than settling for substitutes.

Pond's canon base is Raven (Tekken 5 debut, 2004; Master Raven in T7).
Her MOVESET data is now complete on Raven's own tables (620 moves,
T7+T8 merged — see `game/assets/movesets/pond.json`
`merge_sources.added`). Her MOTION is not: no
`game/assets/anim/t3/raven/` bank exists, so her stance/idle, intro, win
pose, round-win pose, and generic actions have no Raven clips today. This
doc records exactly what is missing and what unblocks it. Nothing here is
stubbed — per the isolation doctrine a fighter is never animated with
another character's clips, and no fake bank is shipped. Do NOT
substitute a wrong bank (e.g. another ninja's) — file the gap, don't
fill it with someone else's motion.

## The missing bank — FIGHT vs SHOW (SHOW-ANIMATION LOCK, owner 2026-10-23)

Show animations and fight moves are SEPARATE LOCKED SETS. When Raven
motion is decoded, its clips are tagged at intake and the two sets never
mix:

- **FIGHT** — moveset moves, stances used in combat → the moveset
  (`game/assets/movesets/pond.json`) and the combat animation bank.
- **SHOW** — win poses, intro poses, taunts, cutscene animations → the
  intro/win slots (`T3_CLIP_DEFS` `intro`/`win` entries) and cutscenes ONLY.
  SHOW clips must NEVER enter Pond's moveset without the user's explicit
  approval. The game-code lock enforces this; this doc is the intake manifest
  it reads.

Target: `game/assets/anim/t3/raven/` registered in `game/js/t3anims.js`
`T3_BANKS` as `raven: 'assets/anim/t3/raven/'`, plus `raven: 'raven'` in
`SOURCE_TO_BANK` so `bankIdFor('pond')` binds it.
Required files (wh-anim/1 schema — see `game/assets/anim/t3/paul/`):

### FIGHT clips → combat bank + moveset
- `t3_neutral.json` (stance/idle — Raven's signature stance, used in combat),
  `t3_stance_b/c.json` (stance idles — combat stances)
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

## Source A — T7 (best modern source with full motion; FIRST priority)

**Extraction coordinator: Raven's T7 motion is a named target for the
T5/T6/TTT2/T7 100% lane.** Pond's kit is built on T7 Master Raven frame
data — the motion for those same moves is the first pull target. Raven
(male) and Master Raven share the moveset; either skeleton's clips
unblock the bank.

## Source B — T5/T6/TTT2 (debut-era sources; FIRST priority with T7)

Raven debuted in Tekken 5; his T5/T6/TTT2 motion is the same lane's
debut-era target. Same blockers as the Lars TTT2 lane (container
decryption, format RE) — see `docs/anim/LARS-ANIM-GAP-20261023.md` for
the standing blocker list.

## Source C — T8 (newest data; FIRST priority)

T8 ships Raven with a full movelist (177 moves in
`docs/t7t8-reference/frame-data-t8-full/raven.json`, already merged into
Pond's moveset). T8 motion extraction is future work — same priority as
T7, behind no other source.

## Why T3 can't fill it (LAST priority — fallback only, and empty here)

Raven did not exist in Tekken 3 (1997). There is no Raven divmot stream;
`teardown/tekken3/animations/` has 20 character streams and none is his.
Per the owner's source-priority directive, T3 is fallback only — and for
Raven the fallback is empty. Do not settle for a T3 substitution.

## Unblock sequence (for the lane that cracks any source)

1. Decode Raven's motion stream → convert to wh-anim/1
   (`fps: 30`, `rot_xyzw` per bone, `root_t`, 22 canonical bones —
   same shape `jsonToClip` reads in `game/js/t3anims.js`).
2. **Tag every clip FIGHT or SHOW** per the intake manifest above before
   anything lands (SHOW-ANIMATION LOCK).
3. Bake: `python3 tools/anim/t3_row_bake.py --bank raven` (FIGHT action
   clips + full move-index `rows.pack.json`; SHOW clips bake to the
   intro/win slots only).
4. Register `raven` in `T3_BANKS` + `SOURCE_TO_BANK`; Pond binds her own
   bank — combat stance, per-move rows go live with no further wiring
   (the 620 moves already carry `anim_ref`s); intro/win poses wire to
   their slots, never the moveset.

## Moveset status (done this pass)

`game/assets/movesets/pond.json`: 620 moves (T7+T8 merged by the
merge lane; batch3 pull worker verified zero T8 Raven moves genuinely
missing — diff clean). File-level `anim_set_lock` added (SHOW-ANIMATION
LOCK, owner 2026-10-23).

**SHOW-ANIMATION LOCK (owner 2026-10-23):** `game/assets/movesets/pond.json`
carries file-level `anim_set_lock`; the file itself is the FIGHT set.
SHOW animations (win/intro poses, taunts, cutscenes) are tracked in the
FIGHT/SHOW sections above — they wire to intro/win slots and cutscenes
only and must NEVER enter the moveset without the user's explicit
approval.
