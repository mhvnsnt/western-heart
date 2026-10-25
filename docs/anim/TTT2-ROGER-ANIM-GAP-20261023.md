# Roger Jr. motion bank — precise gap (2026-10-23)

**Source priority (owner standing directive 2026-10-23): TTT2/T6/T5 FIRST,
T3 LAST (fallback only).** Roger Jr. debuted after T3 — T3 has no Roger
stream and can never fill this gap. A dedicated extraction coordinator is
driving T5/T6/TTT2/T7 to 100%; this doc is the intake manifest for that
lane.

Menajerii's canon base is Roger Jr. (Tekken Tag Tournament 2). Her MOVESET
data is now substantially complete on Roger's own tables:
`game/assets/movesets/menajerii.json` went 154 → 193 moves in this pull —
39 TTT2-documented Roger Jr. moves added in Tekken notation with
`"set": "FIGHT"` (Animal Rush/Hush strings, Roo Rage, Helicopter Kicks,
Bomb Stomp, Satellite Dropkick, Ali Kick chain, Rocket Stance extensions,
Bobbin Dance charge-ups). Roger's 14 TTT2 throws were already authored
into her file under WH names (Head Stomp, Tasmanian Doormat, Animal Face
Crusher, etc.) — verified throw-by-throw, not re-added. Her MOTION is not
done: no Roger teardown bank exists anywhere on disk, so her clips are
unwired/procedural today. This doc records exactly what is missing.

## The missing bank — FIGHT vs SHOW (SHOW-ANIMATION LOCK, owner 2026-10-23)

Show animations and fight moves are SEPARATE LOCKED SETS. When Roger Jr.
motion is decoded, its clips are tagged at intake and the two sets never
mix:

- **FIGHT** — moveset moves, stances used in combat → the moveset
  (`game/assets/movesets/menajerii.json`) and the combat animation bank.
- **SHOW** — win poses, intro poses, taunts, cutscene animations → the
  intro/win slots and cutscenes ONLY. SHOW clips must NEVER enter
  Menajerii's moveset without the user's explicit approval.

Target: `game/assets/anim/ttt2/roger/` registered in `game/js/t3anims.js`
`T3_BANKS` as `roger: 'assets/anim/ttt2/roger/'`, plus `roger: 'roger'`
in `SOURCE_TO_BANK` so `bankIdFor('menajerii')` binds it. Required files
(wh-anim/1 schema — see `game/assets/anim/t3/paul/`):

### FIGHT clips → combat bank + moveset
- `t3_neutral.json` (kangaroo boxing stance/idle), Rocket Stance idle,
  Bobbin Dance idle — combat stances
- `t3_light.json`, `t3_medium.json`, `t3_heavy.json`, `t3_grab.json`
  (Animal Driver, Animal Swing, DDT, Tombstone)
- `t3_block.json`, `t3_hit.json`, `t3_hit_launch.json`, `t3_ko.json`
- locomotion: walk/dash/backdash/crouch/jump/sidestep set
- `rows.pack.json` — per-move clips for the 39 TTT2-documented additions
- `skeleton.json`

### SHOW clips → intro/win slots + cutscenes ONLY (never the moveset)
- intro pose → `intro` slot only; win pose → `win` slot only
- Future: taunts, cutscene animations — cutscene/intro system only.

## Source A — TTT2 (best source; FIRST priority)

Roger Jr.'s TTT2 motion lives in the Xbox 360 STFS containers
(`teardown/tekken-tag-tournament-2/TEARDOWN.md`, 2026-10-13): only the
13 sub-10MB files are extracted; the ~8.86GB game-data chunks are not.
Blockers: disk space (~27GB needed), safe storage (Release upload in
progress), STFS decrypt tooling, Namco console motion format RE.
**Extraction coordinator lane owns this.**

## Source B — Tekken 6 / Tekken 5 (SECOND priority)

Roger Jr. appears in T6 (and T5). Neither extraction has started on disk.
Same coordinator lane.

## Source C — T3 (LAST resort; known-empty)

Roger Jr. did not exist in T3. Do not substitute another character's
bank — per the isolation doctrine a fighter is never animated with
another character's clips.

## Moveset status (this pull, 2026-10-23)

- `game/assets/movesets/menajerii.json`: 154 → 193 moves. 39 added, all
  `"set": "FIGHT"`, `ttt2_source: 'roger'`, `merge_source: 'ttt2:roger'`.
  14 TTT2 throws verified already-present (WH names), skipped as
  duplicates. Documented-not-extracted: no fabricated frame data.
- `anim_set_lock` metadata stamped at file level.
- Remaining moveset gap: TTT2 frame data for the 39 — fills when the
  T6/T5/TTT2 extraction lane lands.
