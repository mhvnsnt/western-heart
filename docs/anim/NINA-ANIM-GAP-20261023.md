# Nina motion bank — precise gap (2026-10-23)

**Source priority (owner standing directive 2026-10-23): T8 → T7 → TTT2/T6/T5 → T3 LAST (fallback only).**

Awa Pop's canon base is Nina Williams (Tekken 1 debut, 1994). Her MOVESET data is now complete on Nina's own tables — 909 moves, T3+T7+T8 merged (see `game/assets/movesets/awapop.json` `merge_sources.added.batch5_pull_20261023`). The T8 diff in this pull found **0 genuinely-missing inputs**: every T8 Nina input already exists in the moveset. Her MOTION binds `game/assets/anim/t3/nina/` (32 files: `rows.pack.json`, `skeleton.json`, stance/idle, locomotion, block/hit/ko, grab clips — all present).

## The missing bank — FIGHT vs SHOW (SHOW-ANIMATION LOCK, owner 2026-10-23)

Show animations and fight moves are SEPARATE LOCKED SETS. When Nina motion is decoded, its clips are tagged at intake and the two sets never mix:

- **FIGHT** — moveset moves, stances used in combat → the moveset (`game/assets/movesets/awapop.json`) and the combat animation bank.
- **SHOW** — win poses, intro poses, taunts, cutscene animations → the intro/win slots (`T3_CLIP_DEFS` `intro`/`win` entries) and cutscenes ONLY. SHOW clips must NEVER enter Awa Pop's moveset without the user's explicit approval. The game-code lock enforces this; this doc is the intake manifest it reads.

### FIGHT clips → combat bank + moveset
- Present: `t3_neutral.json`, `t3_stance_b/c.json`, `t3_light/medium/heavy/grab.json`, `t3_block/block_b/hit/hit_launch/ko.json`, `t3_walk_fwd/back.json`, `t3_dash_fwd.json`, `t3_backdash.json`, `t3_crouch/crouch_hold.json`, `t3_jump_fwd/back/up.json`, `t3_sidestep_a/b/c/d.json`, `rows.pack.json`, `skeleton.json`.
- No T8-only FIGHT motion gap: all 191 T8 Nina inputs map to existing banked rows.

### SHOW clips → intro/win slots + cutscenes ONLY (never the moveset)
- Gap: Nina's intro pose and win poses are not banked as separate SHOW clips. Intake lane: when T5/T6/TTT2/T7 Nina motion lands, tag her intro (`t3_stance.json` equivalent) and win poses (`t3_win_rp/lp/lk/rk.json`) SHOW and wire to the `intro`/`win` slots only.
- Future: taunts, cutscene animations — cutscene/intro system only.

No clip ships untagged: the intake lane stamps every file FIGHT or SHOW here before it lands, and the moveset lane rejects SHOW-tagged clips.
