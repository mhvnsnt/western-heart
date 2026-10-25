# Baek Doo San motion bank — precise gap (2026-10-23)

**Source priority (owner standing directive 2026-10-23): TTT2/T5 FIRST,
T3 LAST (fallback only).** Baek has no T3 divmot stream in the 20 extracted
banks (`docs/anim/BANK-TABLE-2026-10-20.md`), so T3 can never fill this gap.
A dedicated extraction coordinator is driving T5/T6/TTT2/T7 to 100%; this
doc is the intake manifest for that lane.

Baek Master White's canon base is Baek Doo San. His MOVESET data is now
substantially complete on Baek's own tables:
`game/assets/movesets/baek-master-white.json` went 138 → 291 moves in this
pull — 153 TTT2-documented Baek moves added in Tekken notation with
`"set": "FIGHT"` (full Flamingo stance system: Butterfly Kicks, Black
Widow, Break Blade, Sandstorm Kicks, Hunting Hawk; 14 throws incl. Hammer
Head, Swordfish Catch, Cobra Bite, Cannonball; Mantis Rush; parries).
Prior to this pull his file was 107 Bryan-placeholder moves + WH signature
moves — the Bryan moves remain as PROVISIONAL placeholders pending the
TTT2/T5 extraction, not removed, not trusted as Baek data. His MOTION is
not done: he still binds the flagged `bryan` substitution bank, so his
clips are Bryan's T3 motion today.

## The missing bank — FIGHT vs SHOW (SHOW-ANIMATION LOCK, owner 2026-10-23)

Show animations and fight moves are SEPARATE LOCKED SETS. When Baek motion
is decoded, its clips are tagged at intake and the two sets never mix:

- **FIGHT** — moveset moves, stances used in combat → the moveset
  (`game/assets/movesets/baek-master-white.json`) and the combat animation
  bank.
- **SHOW** — win poses, intro poses, taunts, cutscene animations → the
  intro/win slots and cutscenes ONLY. SHOW clips must NEVER enter his
  moveset without the user's explicit approval.

Target: `game/assets/anim/ttt2/baek/` registered in `game/js/t3anims.js`
`T3_BANKS` as `baek: 'assets/anim/ttt2/baek/'`, plus `baek: 'baek'` in
`SOURCE_TO_BANK` so `bankIdFor('baek-master-white')` binds it. Required
files (wh-anim/1 schema — see `game/assets/anim/t3/paul/`):

### FIGHT clips → combat bank + moveset
- `t3_neutral.json` (stance/idle), Flamingo stance idle — combat stances
- `t3_light.json`, `t3_medium.json`, `t3_heavy.json`, `t3_grab.json`
- `t3_block.json`, `t3_hit.json`, `t3_hit_launch.json`, `t3_ko.json`
- locomotion: walk/dash/backdash/crouch/jump/sidestep set
- `rows.pack.json` — per-move clips for the 153 TTT2-documented additions
- `skeleton.json`

### SHOW clips → intro/win slots + cutscenes ONLY (never the moveset)
- intro pose → `intro` slot only; win pose → `win` slot only
- Future: taunts, cutscene animations — cutscene/intro system only.

## Source A — TTT2 (best modern source; FIRST priority)

Baek's TTT2 motion lives in the Xbox 360 STFS containers
(`teardown/tekken-tag-tournament-2/TEARDOWN.md`, 2026-10-13): only the
13 sub-10MB files are extracted; the ~8.86GB game-data chunks are not.
Blockers: disk space (~27GB needed), safe storage (Release upload in
progress), STFS decrypt tooling, Namco console motion format RE.
**Extraction coordinator lane owns this.**

## Source B — Tekken 5 (SECOND priority)

Baek is a T5 returnee. T5 extraction has not started on disk. Same
coordinator lane.

## Source C — T3 (LAST resort; known-empty)

Baek has no T3 divmot stream in the extracted 20. Do not substitute
another character's bank — per the isolation doctrine a fighter is never
animated with another character's clips.

## Moveset status (this pull, 2026-10-23)

- `game/assets/movesets/baek-master-white.json`: 138 → 291 moves. 153
  added, all `"set": "FIGHT"`, `ttt2_source: 'baek'`,
  `merge_source: 'ttt2:baek'`. Documented-not-extracted: no fabricated
  frame data on the added moves.
- `anim_set_lock` metadata stamped at file level.
- Remaining moveset gap: TTT2 frame data for the 153 — fills when the
  TTT2/T5 extraction lane lands.
