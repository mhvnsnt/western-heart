# Lars motion bank — precise gap (2026-10-23)

**Source priority (owner standing directive 2026-10-23): TTT2/T6 FIRST,
T3 LAST (fallback only).** Lars debuted in Tekken 6 — T3 has no Lars
stream and can never fill this gap. A dedicated extraction coordinator
is driving T5/T6/TTT2/T7 to 100%; this doc is the intake manifest for
that lane — pull what exists now, fill the precise gaps below rather
than settling for substitutes.

Chordz's canon base is Lars Alexandersson (Tekken 6 debut, 2007). His
MOVESET data is now complete on Lars's own tables (469 moves, T7+T8 merged —
see `game/assets/movesets/chordz.json` `merge_sources.added.lars_pull_20261023`).
His MOTION is not: he still binds the flagged `jin` substitution bank
(`t3_source: 'jin'` → `SOURCE_TO_BANK` → `assets/anim/t3/jin/`), so his
stance/idle, intro, win pose, round-win pose, and generic actions are Jin's
T3 clips today. This doc records exactly what is missing and what unblocks it.
Nothing here is stubbed — per the isolation doctrine a fighter is never
animated with another character's clips, and no fake bank is shipped.

## The missing bank — FIGHT vs SHOW (SHOW-ANIMATION LOCK, owner 2026-10-23)

Show animations and fight moves are SEPARATE LOCKED SETS. When Lars motion
is decoded, its clips are tagged at intake and the two sets never mix:

- **FIGHT** — moveset moves, stances used in combat → the moveset
  (`game/assets/movesets/chordz.json`) and the combat animation bank.
- **SHOW** — win poses, intro poses, taunts, cutscene animations → the
  intro/win slots (`T3_CLIP_DEFS` `intro`/`win` entries) and cutscenes ONLY.
  SHOW clips must NEVER enter Chordz's moveset without the user's explicit
  approval. The game-code lock enforces this; this doc is the intake manifest
  it reads.

Target: `game/assets/anim/t3/lars/` registered in `game/js/t3anims.js`
`T3_BANKS` as `lars: 'assets/anim/t3/lars/'`, plus `lars: 'lars'` in
`SOURCE_TO_BANK` so `bankIdFor('chordz')` binds it.
Required files (wh-anim/1 schema — see `game/assets/anim/t3/paul/`):

### FIGHT clips → combat bank + moveset
- `t3_neutral.json` (stance/idle — Lars's signature stance, used in combat),
  `t3_stance_b/c.json` (DEN/SEN stance idles — combat stances)
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

## Source A — TTT2 (best modern source; FIRST priority)

**Extraction coordinator: Lars's TTT2 motion is a named target for the
T5/T6/TTT2/T7 100% lane — the blockers below are what that lane must
clear, in order.** Lars's TTT2 motion lives inside the Xbox 360 STFS containers:
`0000000000000000/4E4D0859/00007000/392CFF5C9DB17CCAEBC3.data/`
(Data0000–Data0051, 52 × ~170MB chunks, ~8.86GB) plus the 7 large
`0000000000000000/4E4D0859/00000002/` blobs. Status
(`teardown/tekken-tag-tournament-2/TEARDOWN.md`, 2026-10-13):
only the 13 sub-10MB files are extracted (`extracted-small/` — avatar-item
LIVE packages + container descriptor, no game data).

Blockers, in order:
1. **Disk space** — full extraction needs ~27GB (13.3GB archive + 13.45GB
   extracted); /home/hatch has ~11GB free with an 88% hard ceiling.
2. **Safe storage** — the 13.3GB archive is being uploaded to a western-heart
   GitHub Release in 500MB chunks (5/26 verified 2026-10-13); per the
   no-delete-before-safe-storage law the local 7z stays until verified.
3. **STFS decrypt tooling** — needs an Xbox 360 STFS parser
   (Velocity/Xbox 360 Content Manager equivalent for Linux).
4. **Format RE** — Namco's proprietary console motion format; no plaintext
   manifest exists, so the character→offset mapping (which blob holds Lars,
   roster slot 34) must be recovered after decryption.

## Source B — T6 PSP (Lars's debut game; FIRST priority with TTT2)

**Extraction coordinator: Lars's T6 PSP motion is the debut-game source —
same lane, same priority as TTT2.** Motion lives in the encrypted DATA401
bulk region
(`teardown/tekken6/`). Status (`TEARDOWN.md`, 2026-10-15): EBOOT decrypted,
sector cipher 0x8AA2CA8 fully reversed — but the bulk data region
(sectors 230256+, entropy 7.90–7.92) is covered by an UNKNOWN transform.
Candidates: custom decompressor near ktRead callers, IDX-driven per-file
keys, or unicorn-emulating the real PAC open. The decrypt lane works on
branch `feature/tekken6-100-teardown` (unmerged until models land).

## Why T3 can't fill it (LAST priority — fallback only, and empty here)

Lars did not exist in Tekken 3 (1997). There is no Lars divmot stream;
`teardown/tekken3/animations/` has 20 character streams and none is his.
Per the owner's source-priority directive, T3 is fallback only — and for
Lars the fallback is empty. Do not settle for a T3 substitution.

## Unblock sequence (for the lane that cracks either source)

1. Decode Lars's motion stream → convert to wh-anim/1
   (`fps: 30`, `rot_xyzw` per bone, `root_t`, 22 canonical bones —
   same shape `jsonToClip` reads in `game/js/t3anims.js`).
2. **Tag every clip FIGHT or SHOW** per the intake manifest above before
   anything lands (SHOW-ANIMATION LOCK).
3. Bake: `python3 tools/anim/t3_row_bake.py --bank lars` (FIGHT action
   clips + full move-index `rows.pack.json`; SHOW clips bake to the
   intro/win slots only).
4. Register `lars` in `T3_BANKS` + `SOURCE_TO_BANK`; Chordz binds his own
   bank — combat stance, per-move rows go live with no further wiring
   (the 469 moves already carry `anim_ref`s); intro/win poses wire to
   their slots, never the moveset.

## Moveset status (done this pass)

`game/assets/movesets/chordz.json`: 452 → **469 moves** (+17 from the
T7/T8 frame-data diff: `f,f+2`, `f,f+3`, `f,f+4`, `f,f+4,3`, `f,f+1+2`,
`f,f+3+4`, `WR.4`, `WS.1,F`, `WS.2,F`, `f,f+2,F`, `GROUNDED.d+3+4`,
`GROUNDED.d+3+4,F`, `FUFT.d+4`, `FUFT.d+3+4`, `TACKLE.2`,
`R.d/f+1+2` (Rage Art), `AIR.DEN.2+4` (Rejection alias)); strings 66 → 71.
All 17 resolve through the game's own `resolveMove`. Verified:
`node --test game/tests/fighter-completeness.test.mjs` green;
`bankIdFor('chordz')` → `jin` bank, all 22 clips present and valid.

**SHOW-ANIMATION LOCK (owner 2026-10-23):** every move in
`game/assets/movesets/chordz.json` is tagged `"set": "FIGHT"` at file
level (`anim_set_lock`) and per-move on the 17 pulled this pass. SHOW
animations (win/intro poses, taunts, cutscenes) are tracked in the
FIGHT/SHOW sections above — they wire to intro/win slots and cutscenes
only and must NEVER enter the moveset without the user's explicit
approval.
