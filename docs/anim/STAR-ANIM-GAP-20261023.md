# Star motion bank — precise gap (2026-10-23)

**Source priority (owner standing directive 2026-10-23, INSTRUCTION GATE
2:19 PM CT): T5/T6/T7/T8/TTT2 FIRST, T3 LAST (fallback only, every use
logged).** Christie debuted in Tekken 4 — T3 has no Christie stream and
can never fill this gap; she was cut from T7 and T8. A dedicated
extraction coordinator is driving T5/T6/TTT2/T7 to 100%; this doc is the
intake manifest for that lane.

Star's canon base is Christie Monteiro (`tekken_base: 'Christie'` in
`game/assets/movesets/star.json`). Her MOTION does not exist: she binds
the flagged `xiaoyu` substitution bank (`anim_bank: 'xiaoyu'` →
`SOURCE_TO_BANK` → `assets/anim/t3/xiaoyu/`), so her stance/idle, intro,
win pose, and generic actions are Xiaoyu's T3 clips today. This doc
records exactly what is missing and what unblocks it. Nothing here is
stubbed — per the isolation doctrine a fighter is never animated with
another character's clips, and no fake bank is shipped.

**Owner decision needed (flagged, not guessed):** `tools/moveset-merge/bases.json`
carries a 2026-10-20 owner override — *"Xiaoyu's moveset goes to Star"* —
so Star's current 908-move file is built on Xiaoyu's T8/T7/T3 tables.
The batch8 task (2026-10-23) names Christie (TTT2/T5) as her source.
Both cannot be her permanent moveset. Until the owner decides, the
Xiaoyu data stays untouched (nothing deleted, nothing re-based) and the
Christie pull below is filed as the pending lane.

## The missing bank — FIGHT vs SHOW (SHOW-ANIMATION LOCK, owner 2026-10-23)

Show animations and fight moves are SEPARATE LOCKED SETS. When Christie
motion is decoded, its clips are tagged at intake and the two sets never
mix:

- **FIGHT** — moveset moves, stances used in combat → the moveset
  (`game/assets/movesets/star.json`) and the combat animation bank.
- **SHOW** — win poses, intro poses, taunts, cutscene animations → the
  intro/win slots (`T3_CLIP_DEFS` `intro`/`win` entries) and cutscenes
  ONLY. SHOW clips must NEVER enter Star's moveset without the user's
  explicit approval. The game-code lock (`game/js/anim-gate.js`) enforces
  this; this doc is the intake manifest it reads.

Target: `game/assets/anim/t3/christie/` registered in
`game/js/t3anims.js` `T3_BANKS` as `christie: 'assets/anim/t3/christie/'`,
plus `christie: 'christie'` in `SOURCE_TO_BANK`, and Star's `anim_bank`
repointed from `xiaoyu` → `christie` so `bankIdFor('star')` binds it.
Required files (wh-anim/1 schema — see `game/assets/anim/t3/paul/`):

### FIGHT clips → combat bank + moveset
- `t3_neutral.json` (stance/idle — Christie's capoeira stance, used in combat)
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

## Source A — TTT2 (Christie playable; FIRST priority)

**Extraction coordinator: Christie's TTT2 motion AND movelist are named
targets for the T5/T6/TTT2/T7 100% lane — the blockers below are what
that lane must clear, in order.** Christie's TTT2 motion lives inside the
Xbox 360 STFS containers. Status
(`teardown/tekken-tag-tournament-2/TEARDOWN.md`, 2026-10-13): only the 13
sub-10MB files are extracted (no game data).

Blockers, in order:
1. **Disk space** — full extraction needs ~27GB; ~11GB free with an 88%
   hard ceiling.
2. **Safe storage** — the 13.3GB archive is being uploaded to a
   western-heart GitHub Release in 500MB chunks (5/26 verified
   2026-10-13); per the no-delete-before-safe-storage law the local 7z
   stays until verified.
3. **STFS decrypt tooling** — Xbox 360 STFS parser for Linux.
4. **Format RE** — Namco's proprietary console motion format; the
   character→offset mapping (Christie's roster slot) must be recovered
   after decryption. No TTT2 movelist table exists either — the movelist
   pull rides the same extraction.

## Source B — Tekken 5 (Christie playable; FIRST priority with TTT2)

**Extraction coordinator: Christie's T5 motion/movelist — same lane, same
priority as TTT2.** Status: `teardown/tekken5/t5_motion_manifest.txt`
exists (motion inventory), but no movelist table has been extracted and
no motion decoder is wired. The T5 lane owns this.

## Source C — none (logged per the INSTRUCTION GATE)

Christie is not in T6 (not on the roster), T7 (cut), T8 (cut), or T3
(T4 debut — predates her). The `xiaoyu` T3 stand-in bank stays flagged as
a proxy until Source A or B lands — per the isolation doctrine it is
never presented as Christie's motion.

## Moveset status (for the record)

`game/assets/movesets/star.json`: 908 moves on Xiaoyu's T8/T7/T3 tables
(owner override 2026-10-20), `anim_set_lock` filed batch8 2026-10-23.
Christie's own T5/TTT2 movelist is unavailable (no data on disk; TTT2
extraction blocked) — 0 Christie moves could be pulled this lane. When
the T5/TTT2 movelist lands AND the owner resolves the Xiaoyu-vs-Christie
question above, her file re-bases onto it.
