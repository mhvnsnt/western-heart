# Alisa motion bank — precise gap (2026-10-23)

**Source priority (owner standing directive 2026-10-23): T8 → T7 → TTT2/T6 → T3 LAST (fallback only).** Alisa debuted in Tekken 6: Bloodline Rebellion — T3 has no Alisa stream and can never fill this gap. A dedicated extraction coordinator is driving T5/T6/TTT2/T7 to 100%; this doc is the intake manifest for that lane — pull what exists now, fill the precise gaps below rather than settling for substitutes.

Cyborg X's canon base is Alisa Bosconovitch (Tekken 6 debut, 2007). Her MOVESET data is now complete on Alisa's own tables — 624 moves, T7+T8 merged (see `game/assets/movesets/cyborgx.json` `merge_sources.added.batch5_pull_20261023`). The T8 diff in this pull found **0 genuinely-missing inputs**: every T8 Alisa input already exists in the moveset. Her MOTION is not hers: she still binds the flagged `gunjack` substitution bank (`t3_source: 'gunjack'` → `SOURCE_TO_BANK` → `assets/anim/t3/gunjack/`), so her stance/idle, intro, win pose, round-win pose, and generic actions are Gun Jack's T3 clips today. This doc records exactly what is missing and what unblocks it. Nothing here is stubbed — per the isolation doctrine a fighter is never animated with another character's clips, and no fake bank is shipped.

## The missing bank — FIGHT vs SHOW (SHOW-ANIMATION LOCK, owner 2026-10-23)

Show animations and fight moves are SEPARATE LOCKED SETS. When Alisa motion is decoded, its clips are tagged at intake and the two sets never mix:

- **FIGHT** — moveset moves, stances used in combat → the moveset (`game/assets/movesets/cyborgx.json`) and the combat animation bank.
- **SHOW** — win poses, intro poses, taunts, cutscene animations → the intro/win slots (`T3_CLIP_DEFS` `intro`/`win` entries) and cutscenes ONLY. SHOW clips must NEVER enter Cyborg X's moveset without the user's explicit approval. The game-code lock enforces this; this doc is the intake manifest it reads.

Target: `game/assets/anim/t3/alisa/` registered in `game/js/t3anims.js` `T3_BANKS` as `alisa: 'assets/anim/t3/alisa/'`, plus `alisa: 'alisa'` in `SOURCE_TO_BANK` so `bankIdFor('cyborgx')` binds it. Required files (wh-anim/1 schema — see `game/assets/anim/t3/paul/`):

### FIGHT clips → combat bank + moveset
- `t3_neutral.json` (stance/idle — Alisa's signature stance, used in combat), `t3_stance_b/c.json` (her stance transitions — combat stances)
- `t3_light.json`, `t3_medium.json`, `t3_heavy.json`, `t3_grab.json`
- `t3_block.json`, `t3_block_b.json`, `t3_hit.json`, `t3_hit_launch.json`, `t3_ko.json`
- `t3_walk_fwd.json`, `t3_walk_back.json`, `t3_dash_fwd.json`, `t3_backdash.json`, `t3_crouch.json`, `t3_crouch_hold.json`, `t3_jump_fwd/back/up.json`, `t3_sidestep_a/b/c/d.json`
- `rows.pack.json` — per-move clips baked with `tools/anim/t3_row_bake.py` (same pipeline as the 9 remainder banks, PR #405)
- `skeleton.json`

### SHOW clips → intro/win slots + cutscenes ONLY (never the moveset)
- `t3_stance.json` — intro pose → wires to the `intro` slot only
- `t3_win_rp.json` — win pose → wires to the `win` slot only (`t3_win_lp/lk/rk.json` optional alternates, same slot)
- Future: taunts, cutscene animations — cutscene/intro system only.

No clip ships untagged: the intake lane stamps every file FIGHT or SHOW here before it lands, and the moveset lane rejects SHOW-tagged clips.

## Source A — TTT2/T6 (best modern source; FIRST priority)

**Extraction coordinator: Alisa's TTT2/T6 motion is a named target for the T5/T6/TTT2/T7 100% lane — clear the TTT2 blockers (STFS decrypt, disk, safe storage, format RE) documented in the Lars manifest's Source A section rather than settling for the gunjack substitution.** Her T8 moveset data is complete and waiting; motion is the only gap.
