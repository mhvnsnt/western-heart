# Bruno motion bank — precise gap (2026-10-23)

**Source priority (owner standing directive 2026-10-23, INSTRUCTION GATE
2:19 PM CT): T5/T6/T7/T8/TTT2 FIRST, T3 LAST (fallback only, every use
logged).** Miguel debuted in Tekken 7 — T3 has no Miguel stream and can
never fill this gap. A dedicated extraction coordinator is driving
T5/T6/TTT2/T7 to 100%; this doc is the intake manifest for that lane.

Bruno's canon base is Miguel Caballero Rojo (Tekken 7 debut, 2015; cut
from Tekken 8). His MOVESET data is complete on Miguel's own T7 tables
(219/219 rows, `docs/t7t8-reference/frame-data-t7/miguel.json` via
t7chicken — see `game/assets/movesets/bruno.json`
`merge_sources.bases.t7: ["miguel"]`; batch8 2026-10-23 verified 0 rows
missing). His MOTION is not: he still binds the flagged `bryan`
substitution bank (`t3_source: 'bryan'` → `SOURCE_TO_BANK` →
`assets/anim/t3/bryan/`), so his stance/idle, intro, win pose, and
generic actions are Bryan's T3 clips today. This doc records exactly
what is missing and what unblocks it. Nothing here is stubbed — per the
isolation doctrine a fighter is never animated with another character's
clips, and no fake bank is shipped.

## The missing bank — FIGHT vs SHOW (SHOW-ANIMATION LOCK, owner 2026-10-23)

Show animations and fight moves are SEPARATE LOCKED SETS. When Miguel
motion is decoded, its clips are tagged at intake and the two sets never
mix:

- **FIGHT** — moveset moves, stances used in combat → the moveset
  (`game/assets/movesets/bruno.json`) and the combat animation bank.
- **SHOW** — win poses, intro poses, taunts, cutscene animations → the
  intro/win slots (`T3_CLIP_DEFS` `intro`/`win` entries) and cutscenes
  ONLY. SHOW clips must NEVER enter Bruno's moveset without the user's
  explicit approval. The game-code lock (`game/js/anim-gate.js`) enforces
  this; this doc is the intake manifest it reads.

Target: `game/assets/anim/t3/miguel/` registered in `game/js/t3anims.js`
`T3_BANKS` as `miguel: 'assets/anim/t3/miguel/'`, plus `miguel: 'miguel'`
in `SOURCE_TO_BANK`, and Bruno's `t3_source`/`anim_bank` repointed from
`bryan` → `miguel` so `bankIdFor('bruno')` binds it. Required files
(wh-anim/1 schema — see `game/assets/anim/t3/paul/`):

### FIGHT clips → combat bank + moveset
- `t3_neutral.json` (stance/idle — Miguel's signature stance, used in combat)
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

## Source A — Tekken 7 (Miguel's debut and only game; FIRST priority)

**Extraction coordinator: Miguel's T7 motion is a named target for the
T5/T6/TTT2/T7 100% lane — the blockers below are what that lane must
clear, in order.** The owner is purchasing Tekken 7 on Steam (2026-10-23);
the file pull happens the day they confirm the purchase. Miguel's motion
lives in the T7 PC data. Status (`teardown/tekken7/`): meshes only, no
animation — full game not yet acquired.

Blockers, in order:
1. **Game acquisition** — owner confirms the Steam purchase of Tekken 7.
2. **File pull** — pull the T7 data archives on purchase confirmation
   (per the game-ownership rule: owner says they bought it → pull
   immediately, no proof requests).
3. **Format RE** — Namco's T7 motion format; character→offset mapping for
   Miguel must be recovered after the pull.
4. **Bake** — `tools/anim/t3_bake_bank.py` pattern onto Miguel's rig,
   wh-anim/1 schema, FIGHT/SHOW tagging at intake.

## Source B — none (logged per the INSTRUCTION GATE)

Miguel appears in no other Tekken: not in T3 (predates him), not in T5/T6
(T7 debut), not in TTT2, cut from T8. There is no fallback source. The
`bryan` T3 stand-in bank stays flagged as a proxy until Source A lands —
per the isolation doctrine it is never presented as Miguel's motion.

## Moveset status (for the record)

`game/assets/movesets/bruno.json`: 328 moves, 219/219 T7 Miguel rows
merged (206 curated with Miguel's real move names — e.g. Chulería — plus
13 `t7:miguel_*` tool merges), `anim_set_lock` filed batch8 2026-10-23.
No T3 fallback was used for the moveset (T7 is the primary and complete).
