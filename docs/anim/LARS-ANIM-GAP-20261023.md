# Lars motion bank — precise gap (2026-10-23)

Chordz's canon base is Lars Alexandersson (Tekken 6 debut, 2007). His
MOVESET data is now complete on Lars's own tables (469 moves, T7+T8 merged —
see `game/assets/movesets/chordz.json` `merge_sources.added.lars_pull_20261023`).
His MOTION is not: he still binds the flagged `jin` substitution bank
(`t3_source: 'jin'` → `SOURCE_TO_BANK` → `assets/anim/t3/jin/`), so his
stance/idle, intro, win pose, round-win pose, and generic actions are Jin's
T3 clips today. This doc records exactly what is missing and what unblocks it.
Nothing here is stubbed — per the isolation doctrine a fighter is never
animated with another character's clips, and no fake bank is shipped.

## The missing bank

Target (when Lars motion is decoded): `game/assets/anim/t3/lars/` registered
in `game/js/t3anims.js` `T3_BANKS` as `lars: 'assets/anim/t3/lars/'`, plus
`lars: 'lars'` in `SOURCE_TO_BANK` so `bankIdFor('chordz')` binds it.
Required files (wh-anim/1 schema — see `game/assets/anim/t3/paul/`):

- Action clips (22): `t3_neutral.json` (stance/idle — Lars's signature stance),
  `t3_stance.json` (intro pose), `t3_light.json`, `t3_medium.json`,
  `t3_heavy.json`, `t3_grab.json`, `t3_block.json`, `t3_block_b.json`,
  `t3_hit.json`, `t3_hit_launch.json`, `t3_ko.json`, `t3_win_rp.json`
  (win pose; `t3_win_lp/lk/rk.json` optional), `t3_walk_fwd.json`,
  `t3_walk_back.json`, `t3_dash_fwd.json`, `t3_backdash.json`,
  `t3_crouch.json`, `t3_crouch_hold.json`, `t3_jump_fwd/back/up.json`,
  `t3_sidestep_a/b/c/d.json`, `t3_stance_b/c.json` (DEN/SEN stance idles)
- `rows.pack.json` — per-move clips baked with `tools/anim/t3_row_bake.py`
  (same pipeline as the 9 remainder banks, PR #405)
- `skeleton.json`

## Source A — TTT2 (best modern source)

Lars's TTT2 motion lives inside the Xbox 360 STFS containers:
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

## Source B — T6 PSP (Lars's debut game)

Motion lives in the encrypted DATA401 bulk region
(`teardown/tekken6/`). Status (`TEARDOWN.md`, 2026-10-15): EBOOT decrypted,
sector cipher 0x8AA2CA8 fully reversed — but the bulk data region
(sectors 230256+, entropy 7.90–7.92) is covered by an UNKNOWN transform.
Candidates: custom decompressor near ktRead callers, IDX-driven per-file
keys, or unicorn-emulating the real PAC open. The decrypt lane works on
branch `feature/tekken6-100-teardown` (unmerged until models land).

## Why T3 can't fill it

Lars did not exist in Tekken 3 (1997). There is no Lars divmot stream;
`teardown/tekken3/animations/` has 20 character streams and none is his.

## Unblock sequence (for the lane that cracks either source)

1. Decode Lars's motion stream → convert to wh-anim/1
   (`fps: 30`, `rot_xyzw` per bone, `root_t`, 22 canonical bones —
   same shape `jsonToClip` reads in `game/js/t3anims.js`).
2. Bake: `python3 tools/anim/t3_row_bake.py --bank lars` (action clips +
   full move-index `rows.pack.json`).
3. Register `lars` in `T3_BANKS` + `SOURCE_TO_BANK`; Chordz binds his own
   bank — stance, intro, win/round-win poses, and per-move rows all go live
   with no further wiring (the 469 moves already carry `anim_ref`s).

## Moveset status (done this pass)

`game/assets/movesets/chordz.json`: 452 → **469 moves** (+17 from the
T7/T8 frame-data diff: `f,f+2`, `f,f+3`, `f,f+4`, `f,f+4,3`, `f,f+1+2`,
`f,f+3+4`, `WR.4`, `WS.1,F`, `WS.2,F`, `f,f+2,F`, `GROUNDED.d+3+4`,
`GROUNDED.d+3+4,F`, `FUFT.d+4`, `FUFT.d+3+4`, `TACKLE.2`,
`R.d/f+1+2` (Rage Art), `AIR.DEN.2+4` (Rejection alias)); strings 66 → 71.
All 17 resolve through the game's own `resolveMove`. Verified:
`node --test game/tests/fighter-completeness.test.mjs` green;
`bankIdFor('chordz')` → `jin` bank, all 22 clips present and valid.
