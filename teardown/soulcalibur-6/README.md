# Soulcalibur VI — Teardown (Lane 1C, 2026-11-21)

**Status: MOVESET TEARDOWN COMPLETE (bytecode level). ANIMATION (.mot) STILL UNCRACKED.**

This folder now holds the closest thing to a complete SoulCalibur VI teardown
that exists anywhere public (verified live 2026-11-21 — see
`SCVI-TEARDOWN-HUNT-20261121.md`):

| What | Where | Size / count |
|---|---|---|
| Scuffle — working SCVI movelist-bytecode parser + live frame-data tool (MIT, vendored whole minus build junk) | `tools/anim/scvi-scuffle/` | 130 files |
| Per-fighter movelist bytecode dumps, straight from live game memory (upstream) | `tools/anim/scvi-scuffle/movelists/` | 22 files, 21,159,556 B |
| Full parsed move tables (every move, attack, throw, cancel-derived frame data) | `teardown/soulcalibur-6/parsed/` | 22 files, ~24 MB |
| Western Heart moveset banks (schema v2, wired in) | `game/assets/movesets/scvi-*.json` | 22 files, 5,360 attack moves |
| Hunt record + sources | `SCVI-TEARDOWN-HUNT-20261121.md`, `SOURCES.md` | — |
| Why .mot animations are NOT here | `MOT-FORK-20261121.md` | — |

## Totals (verified by running the upstream parser offline, 2026-11-21)

- **22 fighters** (full base + DLC cast present in Scuffle's dumps, incl. 2B and Geralt)
- **64,311 moves** parsed (72-byte records: animation/.mot id, multipliers, total frames, cancel-block address, up to 6 attack indexes)
- **6,348 attacks** (112-byte records: startup, active, damage, block/hit/counter stun, hit level, physics, launch types)
- **5,360 attack moves** wired into WH banks (one bank entry per attack move)
- **~330 throws** (moves whose attacks are all throws; counted per bank)

## What each move carries into Western Heart

Every bank entry has the **extracted** frame data (startup/active/recovery in
seconds, damage, stuns, hit level) plus `anim_ref: "scvi:<fighter>/anim-<id>"`
— the **.mot animation id** that move plays. The .mot *motion data itself* is
not extracted (format uncracked — see `MOT-FORK-20261121.md`), but every move
already points at its animation file, so the day .mot is cracked the mapping
is done.

Honesty notes (also in every bank header): the movelist contains **no move
names** — bank entries are keyed by SCVI move id (`m214`, …). Commands are the
parser's raw output (may contain `.`/`?` placeholders) — not cleaned engine
inputs. `limb` is `"unknown"` (hitbox limb bytes are undecoded upstream).
`knock`/`soulGain` are 0 (no SCVI source basis). Frame data is **extracted,
not estimated** — strictly better than the repo's community-transcribed banks.

## What is still missing

1. **.mot animation motion data** — the format is uncracked community-wide
   (umodel: Anim = No; "nobody has cracked that yet, only meshes and
   textures"). No public converter exists. See `MOT-FORK-20261121.md` for the
   evidence and exactly what cracking it requires.
2. **Hitbox placement** — per Scuffle's own doc, hitbox location/placement is
   "stored at least partly with the move animation" — i.e. in the .mot, so it
   arrives with the .mot crack.
3. **Move names** — not in the movelist; they live in the game's UI strings
   (not dumped here). A future pass can join names from community movelists.

## Pre-existing files in this folder (untouched by Lane 1C)

- `HOLDINGS-INDEX-2026-11-06.md` — the raw PC game in-repo (release
  `soulcalibur6-archiveorg-20261106`, 7×1.9 GB parts, verified).
- `TEARDOWN.md` — 2026-10-13 teardown plan; its "extraction pending
  (FreeArc .dxn + staged disk space)" line is now partly answered by this
  lane (movelist extraction done from Scuffle's dumps; full-game extraction
  still blocked as documented in `MOT-FORK-20261121.md`).
- `docs/SCVI-MECHANICS.md` — community mechanics reference (SuperCombo Wiki,
  Frame Calibur / Dustloop). Still the mechanics companion to this data.
