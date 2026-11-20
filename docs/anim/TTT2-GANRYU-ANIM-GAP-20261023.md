# Ganryu motion bank — precise gap (2026-10-23)

**Source priority (owner standing directive 2026-10-23): TTT2/T6 FIRST,
T3 LAST (fallback only).** Ganryu has no T3 divmot stream in the 20
extracted banks (`docs/anim/BANK-TABLE-2026-10-20.md`), so T3 can never
fill this gap. A dedicated extraction coordinator is driving T5/T6/TTT2/T7
to 100%; this doc is the intake manifest for that lane.

Thor's canon base is Ganryu (sumo grappler). His MOVESET data is now
substantially complete on Ganryu's own tables: `game/assets/movesets/thor.json`
went 244 → 322 moves in this pull — 78 TTT2-documented Ganryu moves added
in Tekken notation with `"set": "FIGHT"` (13 throws incl. Jizo Hug, Face
Slam, Giant Tackle; Devil Thrusts; Sumo Rush + L/M/H endings; Kabuki
Slaps chain; sit-down options; Earthquake unblockable). Source: TTT2
Ganryu movelist (Catlord v1.12, cross-checked). His MOTION is not: he
still binds the flagged `bryan` substitution bank (`t3_source: 'bryan'` →
`SOURCE_TO_BANK` → `assets/anim/t3/bryan/`), so his stance/idle and
generic actions are Bryan's T3 clips today. The 107 bryan-sourced moves
already in his file remain as PROVISIONAL placeholders pending the
T6/TTT2 extraction — not removed, not trusted as Ganryu data.

## The missing bank — FIGHT vs SHOW (SHOW-ANIMATION LOCK, owner 2026-10-23)

Show animations and fight moves are SEPARATE LOCKED SETS. When Ganryu
motion is decoded, its clips are tagged at intake and the two sets never
mix:

- **FIGHT** — moveset moves, stances used in combat → the moveset
  (`game/assets/movesets/thor.json`) and the combat animation bank.
- **SHOW** — win poses, intro poses, taunts, cutscene animations → the
  intro/win slots and cutscenes ONLY. SHOW clips must NEVER enter Thor's
  moveset without the user's explicit approval.

Target: `game/assets/anim/t6/ganryu/` (or `t3/`-style bank dir) registered
in `game/js/t3anims.js` `T3_BANKS` as `ganryu: 'assets/anim/t6/ganryu/'`,
plus `ganryu: 'ganryu'` in `SOURCE_TO_BANK` so `bankIdFor('thor')` binds
it. Required files (wh-anim/1 schema — see `game/assets/anim/t3/paul/`):

### FIGHT clips → combat bank + moveset
- `t3_neutral.json` (sumo stance/idle), `t3_crouch.json` (sit-down stance)
- `t3_light.json`, `t3_medium.json`, `t3_heavy.json`, `t3_grab.json`
  (sumo throws: Body Drop, Hip Roll, Jizo Hug, Face Slam, Giant Tackle)
- `t3_block.json`, `t3_hit.json`, `t3_hit_launch.json`, `t3_ko.json`
- locomotion: walk/dash/backdash/crouch/jump/sidestep set
- `rows.pack.json` — per-move clips for the 78 TTT2-documented rows
- `skeleton.json`

### SHOW clips → intro/win slots + cutscenes ONLY (never the moveset)
- intro pose → `intro` slot only; win pose → `win` slot only
- Future: taunts, cutscene animations — cutscene/intro system only.

## Source A — TTT2 (best modern source; FIRST priority)

Ganryu's TTT2 motion lives in the Xbox 360 STFS containers
(`teardown/tekken-tag-tournament-2/TEARDOWN.md`, 2026-10-13): only the
13 sub-10MB files are extracted; the ~8.86GB game-data chunks are not.
Blockers: disk space (~27GB needed), safe storage (Release upload in
progress), STFS decrypt tooling, Namco console motion format RE.
**Extraction coordinator lane owns this.**

## Source B — Tekken 6 (SECOND priority)

Ganryu is a T6 returnee. T6 extraction has not started on disk. Same
coordinator lane.

## Source C — T3 (LAST resort; known-empty)

Ganryu has no T3 divmot stream in the extracted 20. Do not substitute
another character's bank — per the isolation doctrine a fighter is never
animated with another character's clips.

## Moveset status (this pull, 2026-10-23)

- `game/assets/movesets/thor.json`: 244 → 322 moves. 78 added, all
  `"set": "FIGHT"`, `ttt2_source: 'ganryu'`, `merge_source: 'ttt2:ganryu'`.
  Documented-not-extracted: no fabricated frame data on the added moves.
- `anim_set_lock` metadata stamped at file level.
- Remaining moveset gap: TTT2 frame data (startup/damage) for the 78 —
  fills when the T6/TTT2 extraction lane lands; the movelist lane does
  not invent it.
