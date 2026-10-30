# Bryan motion bank — precise gap (2026-10-23)

**Source priority (owner standing directive 2026-10-23): T8 → T7 → TTT2/T6/T5 → T3 LAST (fallback only).**

Retsu's canon base is Bryan Fury (Tekken 3 debut, 1997). His MOVESET data is now complete on Bryan's own tables — 739 moves, T3+T7+T8 merged (see `game/assets/movesets/retsu.json` `merge_sources.added.batch5_pull_20261023`). The T8 diff in this pull added **54 genuinely-missing inputs** (all stamped `set: FIGHT`). His MOTION binds `game/assets/anim/t3/bryan/` (32 files: `rows.pack.json`, `skeleton.json`, stance/idle, locomotion, block/hit/ko, grab clips — present).

## The missing bank — FIGHT vs SHOW (SHOW-ANIMATION LOCK, owner 2026-10-23)

Show animations and fight moves are SEPARATE LOCKED SETS. When Bryan motion is decoded, its clips are tagged at intake and the two sets never mix:

- **FIGHT** — moveset moves, stances used in combat → the moveset (`game/assets/movesets/retsu.json`) and the combat animation bank.
- **SHOW** — win poses, intro poses, taunts, cutscene animations → the intro/win slots (`T3_CLIP_DEFS` `intro`/`win` entries) and cutscenes ONLY. SHOW clips must NEVER enter Retsu's moveset without the user's explicit approval. The game-code lock enforces this; this doc is the intake manifest it reads.

### FIGHT clips → combat bank + moveset
- Present: `t3_neutral.json`, `t3_stance_b/c.json`, `t3_light/medium/heavy/grab.json`, `t3_block/block_b/hit/hit_launch/ko.json`, `t3_walk_fwd/back.json`, `t3_dash_fwd.json`, `t3_backdash.json`, `t3_crouch/crouch_hold.json`, `t3_jump_fwd/back/up.json`, `t3_sidestep_a/b/c/d.json`, `rows.pack.json`, `skeleton.json`.
- **FIGHT motion gap — 54 T8-only moves with no banked clip.** These entered the moveset in this pull (`set: FIGHT`, `anim_ref: t8:bryan:…`) but no T3 row exists to wire them; until the T5/T6/TTT2/T7 extraction lane banks their motion they bind the bank's generic strike/grab clips. Named target for the extraction coordinator 100% lane: `Back throw`, `(Back to wall).b,b,UB`, `b,df+4`, `db+1+2`, `db+2`, `db+3`, `DF+1`, `DF+1,1`, `DF+1,1,1`, `DF+1,1,1,1`, `DF+1,2`, `df+2`, `df+2,1`, `df+2,3`, `df+3`, `df+4`, `FC.db+1+2`, `FC.df+2`, `FC.df+2,1`, `FC.df+4`, `Left throw`, `R.df+1+2`, `Right throw`, `SNE.FC.df+3`, `SNE.f,F+1+2,P`, `ub+1+2`, `ub+1+2,1`, `ub+1+2,1,2`, `ub+1+2,1,2,1`, `ub+1+2,1,2,1,2`, `ub+1+2,1,2,1,2,1`, `ub+1+2,1,2,1,2,1,2`, `ub+1+2,1,2,1,2,1,2,1`, `ub+1+2,1,2,1,2,1,2,1,2`, `ub+1+2,1,2,1,2,1,2,1,2,1`, `ub+1+2,1,2,1,2,1,2,1,2,1,4`, `uf+1`, `uf+1+2`, `uf+2`, `uf+2,2`, `uf+2,2,2`, `uf+2,2,2,3`, `uf+2,2,2,SNE.2`, `uf+2,2,2,SNE.2,2`, `uf+2,2,2,SNE.2,2,3`, `uf+3`, `uf+3+4`, `uf+4`, `uf,n,4`, `ws1`, `ws2`, `ws3`, `ws3,4`, `ws4`.
- Skipped (not attacks, no move entry, no gap): `d,db,b` — empty motion-transition input in the T8 table.

### SHOW clips → intro/win slots + cutscenes ONLY (never the moveset)
- Gap: Bryan's intro pose and win poses are not banked as separate SHOW clips. Intake lane: when T5/T6/TTT2/T7 Bryan motion lands, tag his intro (`t3_stance.json` equivalent) and win poses (`t3_win_rp/lp/lk/rk.json`) SHOW and wire to the `intro`/`win` slots only.
- Future: taunts, cutscene animations — cutscene/intro system only.

No clip ships untagged: the intake lane stamps every file FIGHT or SHOW here before it lands, and the moveset lane rejects SHOW-tagged clips.
