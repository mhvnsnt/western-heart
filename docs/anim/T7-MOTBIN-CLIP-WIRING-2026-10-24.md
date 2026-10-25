# T7 mot.bin clip keys wired into Pond + Ryusan movesets (2026-10-24)

Button naming: LP1 = Left Punch = Tekken 1, RP2 = Right Punch = Tekken 2,
LK3 = Left Kick = Tekken 3, RK4 = Right Kick = Tekken 4.

## What this lane did

Wired the decoded T7 mot.bin clip keys (`anim_ref` = bank + index into the
bank MOTA's offset list) into the Western Heart moveset files as a new
top-level `t7_motbin_clips` table:

- `game/assets/movesets/pond.json` — frv (Master Raven, Pond's Tekken base)
- `game/assets/movesets/ryusan.json` — dnc (Lucky Chloe, Ryusan's Tekken base)

Source decode: `~/workspace/t7-motbin-analysis/` (report
`T7-MOTBIN-FRV-DNC-2026-10-24.md`, CSV maps `frv_move_clip_map.csv` /
`dnc_move_clip_map.csv`). Source JSONs are game-reverse-engineering
PR #61 (OPEN, not merged at wiring time) at
`teardown/tekken7-steam/tkdata/mothead/json/frv.json` + `dnc.json`.
Existing per-move `anim_ref` fields (frame-data IDs such as
`t7:luckychloe:luckychloe_1`) were NOT overwritten — the new table lives
under its own key, so the game's existing animation references are untouched.

## Counts — what was wired, what is UNMAPPED

| Fighter | Total internal moves | Bank 0x0000 wired (clip bytes in tkdata) | Bank 0x4000 wired (clip bytes in tkdata) | Bank 0x8000 UNMAPPED |
|---|---|---|---|---|
| Pond (frv) | 2,338 | 133 | 612 | 1,593 |
| Ryusan (dnc) | 2,183 | 142 | 514 | 1,527 |

- Bank 0x0000 source: mot.bin MotaList slot-0 MOTA (frv absolute 1350136,
  133 clips; dnc absolute 1232264, 142 clips). Every wired clip starts
  `00 64` or `00 C8` (verified in the decode).
- Bank 0x4000 source: `<code>rotsm.arc` section-0 MOTA at offset 64
  (frv 710 clips, dnc 604 clips). Same `00 64` / `00 C8` verification.
- Bank 0x8000: main character MOTA, NOT in tkdata. Every 0x8000 row in
  the tables is marked UNMAPPED with reason "0x8000 clip bytes pending
  Grok pakchunk extraction". The lookup key is already in the table:
  `lookup_key = anim_ref - 0x8000` (verified for every 0x8000 row;
  ranges 0x8000..0x86A5, lookup keys 0..1701, both fighters).
  The extraction request is western-heart issue #866 comment 6390169912
  (prefix [Muse]), asking Grok to pull the frv/dnc main MOTA from
  pakchunk data on his box into private repo mhvnsnt/game-reverse-engineering
  `teardown/tekken7-steam/tkdata/` (suggested `mothead/mota/frv-main-mota.bin`
  + `dnc-main-mota.bin`, or per-clip files keyed by lookup index).

Table layout inside each moveset file: `t7_motbin_clips` carries
`provenance`, `playable_wiring`, `banks`, `counts`, `resolved`
(columns: move_index, move_name, anim_name, anim_ref,
clip_index_or_offset_in_mota, clip_start_bytes) and `unmapped_0x8000`
(columns: move_index, move_name, anim_name, anim_ref,
lookup_key_anim_ref_minus_0x8000). Compact arrays were used so the
files stay under the 1 MB GitHub contents-API read limit
(Pond 629 KB -> 917 KB, Ryusan 184 KB -> 392 KB).

## What was deliberately NOT wired (read before attaching anything playable)

`playable_wiring` in both files is NONE. No WH move was given a mot.bin
clip as its playable animation, and no string continuation was wired.
Reason, from decode report section 7: the display-title to internal-move
join is NOT play-verified. Only 30 frv + 11 dnc display titles walk
deterministically from neutral, and those walks collide and mislead:

- frv collisions on one landing move: Haze / White Hole / Pandora Spin /
  Spinning Middle Kick all land on `Nj_jpRlk00` (0x4201); Alondite /
  Hellhound / Undertaker all land on `Nj_rATE00_` (0x4235); Shadow Spear /
  Buzzsaw both land on `Nj_R_rp00F` (0x4197); Sudden Strike / Poison Needle
  both land on `Nj_R_lk00F` (0x4173); Lance Kick / Iron Maul / Black Hole
  all land on `Nj_R_rk00` (0x6a). At most one title per group can be that
  move; the walk cannot say which.
- frv Elbow Strike lands on `Nj_rk00` (0x416f) only via a step, the same
  move Rising Uppercut reaches directly — the step model is suspect.
- dnc is worse: 8 of 11 OK walks go via a step, and five titles
  (Hopping, Graceful Turn, Cat Stamp, Air Drop Heel, Left Cross Shift)
  land on `Dc_sWALKF` (0x40d1) — a walk-forward state, not an attack.
  Wiring that onto Cat Stamp or Air Drop Heel would be exactly the
  wrong-animation failure this repo keeps getting corrected for.
- frv Orbiting Moon's OK walk lands on a 0x8000 clip (0x82c5) whose bytes
  do not exist in tkdata at all.

A later lane may attach clips to WH moves only after PLAY verification
(phone portrait, human navigation, execute the move in the live build and
confirm the animation played matches the mapped clip), one move at a time.
Until then the tables are keys + provenance, not playable wiring.

## Simulation (not play verification)

A simulation script checked the wired files against the CSV maps and the
pre-change main-branch files. Result: ALL PASS for both fighters.

- Diff shape: pure insertion. Removing the inserted block reproduces the
  old file byte-for-byte — 0 lines removed or changed, 0 existing
  `anim_ref` values changed, 0 moves gained or lost a field.
- Round-trip: resolved rows (Pond 745, Ryusan 656) and unmapped rows
  (Pond 1,593, Ryusan 1,527) match the CSV maps exactly, in order.
- Resolved clips: all start `00 64` / `00 C8`; 0 resolved rows carry a
  0x8000 ref; 0 unmapped rows are marked anything but UNMAPPED.
- Strike/throw/string accounting (the task's simulation bar, applied to
  what this change actually touches): 0 strikes changed on throw rows,
  0 throws changed on strike rows, 0 generic fallbacks introduced —
  because no WH move row was touched at all. Pond: 28 throw rows, 271
  string-class moves, all byte-identical. Ryusan: 10 throw rows, 104
  string-class moves, all byte-identical. String continuations are
  therefore unwired by design, not by omission: no second press can play
  a wrong clip from this change.

Simulation passing does NOT mean play-verified. Nothing in this lane was
verified by playing the live build, and no playable animation claim is
made. Play verification is still owed before any clip becomes a WH move's
animation.

## Next steps

1. Grok extracts the frv/dnc 0x8000 main MOTA (issue #866 comment
   6390169912). On arrival, flip the `unmapped_0x8000` rows to resolved
   (same table, same lookup keys) after the `00 64` / `00 C8` spot check.
2. Game-reverse-engineering PR #61 still needs a lane with checks access
   to confirm green (or mergeable_state resolving to clean). This lane
   did NOT force-merge it and did not touch it.
3. Play-verification lane: execute WALK-MAPPED titles in the live build,
   confirm animations, and only then attach clips per-move.
