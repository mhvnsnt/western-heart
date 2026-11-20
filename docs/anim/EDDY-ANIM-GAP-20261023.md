# Eddy motion bank — precise gap (2026-10-23)

**Source priority (owner standing directive 2026-10-23): T8 → T7 → TTT2/T6/T5 → T3 LAST (fallback only).**

King Tyrant's canon base is Eddy Gordo (Tekken 3 debut, 1997). His MOVESET data is now complete on Eddy's own tables — 848 moves, T3+T7+T8 merged (see `game/assets/movesets/kingtyrant.json` `merge_sources.added.batch5_pull_20261023`). The T8 diff in this pull found **0 genuinely-missing inputs**: every T8 Eddy input already exists in the moveset. His MOTION binds `game/assets/anim/t3/eddy/` (32 files: `rows.pack.json`, `skeleton.json`, stance/idle, locomotion, block/hit/ko, grab clips — all present).

## The missing bank — FIGHT vs SHOW (SHOW-ANIMATION LOCK, owner 2026-10-23)

Show animations and fight moves are SEPARATE LOCKED SETS. When Eddy motion is decoded, its clips are tagged at intake and the two sets never mix:

- **FIGHT** — moveset moves, stances used in combat → the moveset (`game/assets/movesets/kingtyrant.json`) and the combat animation bank.
- **SHOW** — win poses, intro poses, taunts, cutscene animations → the intro/win slots (`T3_CLIP_DEFS` `intro`/`win` entries) and cutscenes ONLY. SHOW clips must NEVER enter King Tyrant's moveset without the user's explicit approval. The game-code lock enforces this; this doc is the intake manifest it reads.

### FIGHT clips → combat bank + moveset
- Present: `t3_neutral.json`, `t3_stance_b/c.json`, `t3_light/medium/heavy/grab.json`, `t3_block/block_b/hit/hit_launch/ko.json`, `t3_walk_fwd/back.json`, `t3_dash_fwd.json`, `t3_backdash.json`, `t3_crouch/crouch_hold.json`, `t3_jump_fwd/back/up.json`, `t3_sidestep_a/b/c/d.json`, `rows.pack.json`, `skeleton.json`.
- No T8-only FIGHT motion gap: all 152 T8 Eddy inputs map to existing banked rows.

### SHOW clips → intro/win slots + cutscenes ONLY (never the moveset)
- Gap: Eddy's T3 intro pose and win poses are not banked as separate SHOW clips — the generic `t3_stance.json`/`t3_win_rp.json` in the bank are FIGHT-tagged stance material, not SHOW. Intake lane: when T5/T6/TTT2/T7 Eddy motion lands, tag his intro (`t3_stance.json` equivalent) and win poses (`t3_win_rp/lp/lk/rk.json`) SHOW and wire to the `intro`/`win` slots only.
- Future: taunts, cutscene animations — cutscene/intro system only.

No clip ships untagged: the intake lane stamps every file FIGHT or SHOW here before it lands, and the moveset lane rejects SHOW-tagged clips.
