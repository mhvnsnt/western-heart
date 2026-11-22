# SoulCalibur VI — Teardown Hunt Record (Lane 1C, 2026-11-21)

Owner order (2026-11-21): do ALL the complete work/teardowns for all six Xbox
games, or find the CLOSEST things to complete work/teardowns — get all the
rips, whatever you can, the closest thing, so we don't start from scratch.
Finish it, make the complete ones, put the complete ones to the side in their
own repos, and wire them up 100% into Western Heart.

Starting state (SYNTHESIS.md, Lane 2, 2026-11-21 ~02:45 EST): NO complete
working SCVI teardown exists. The `.mot` animation format is uncracked.

## Verdict after live re-search (2026-11-21)

**No complete SCVI teardown with animations exists. The closest complete
thing — a full moveset teardown — DOES exist and was pulled whole:
FottenSC/Scuffle** (movelist bytecode for 22 fighters + a working parser +
frame data). The `.mot` animation format itself remains uncracked (see
`MOT-FORK-20261121.md`); that is the one remaining gap, reported as a fork
with evidence, not faked.

## What was searched live (2026-11-21, all checks same-day)

### archive.org — FIRST, live, files inspected

- Advanced search `title:soulcalibur AND mediatype:software`, 28 hits:
  SCII/SCIII/SCIV/SCV items, prototypes, mobile ports — **no SCVI teardown,
  converter, or extraction item**.
- Item `dixen-18-soulcalibur-vi` re-verified live: single file
  `[dixen18] Soulcalibur VI.zip`, 11,441,266,068 B, md5
  `55259ff04257400d1d0e23df4d8e05a1`, sha1
  `feac0ac177d9dbcdeb2be1c49d0c147eb00f51e3` — raw full PC game repack, NOT a
  teardown. Already stored in-repo (release
  `soulcalibur6-archiveorg-20261106`); not re-downloaded.
- Zip central directory fetched live via HTTP range requests: 5 entries —
  `Data01.dxn` (FreeArc, 11,131,847,685 B compressed), `Data02.dxn`
  (281,191,686 B), `Data03.dxn` (21,014,493 B), `Setup.exe` (4,037,453 B).

### umodel / Gildor

- Thread https://www.gildor.org/smf/index.php?action=printpage;topic=6384.0
  (crawled 12 days ago): unchanged since 2018. AES key public, UE 4.17 loads
  meshes/textures. Animations are `.mot` files inside the `.pak`; umodel
  Anim = No. Quote: "nobody has cracked that yet, only meshes and textures."

### GitHub (code + repo search, live)

- `soulcalibur mot` repo search: **no SCVI .mot tool**. Only hit of note:
  `iniGlowee/nier-mot-extractor` — NieR:Automata `.mot`, different game and
  format, not applicable.
- `ARC animation recipe cracker`: **Bigchillghost/ARC** — generic animation
  RE helper (C-like layout definitions, FBX export), 4 stars, 6 commits,
  2023, Windows-only. No SCVI .mot definition. Not a solution.
- **FottenSC/Scuffle** — FOUND, pulled: "Soulcalibur frame data", MIT,
  main `b8e8129b58417b8b71189f05ea3e789b09493f10` (2026-06-06). Working
  movelist-bytecode parser (`MovelistParser.py`, 141,689 B) + 22 fighters'
  movelist dumps + parsed script JSONs + format doc
  (`__HowTheMovelistBytesWork.md`).

### Nexus Mods

- SoulCalibur VI section: FluffyQuack animation-ID swap mods only (e.g.
  Nightmare SC3 idle, mod 21, 2019) + save tools. No extraction.
- Skyrim SE section: Sophitia MCO v1.2 by lingyt11 (mod 88175, updated
  05 May 2025) and Kilik MCO v1.0 by LilBadJj (mod 112109, 16 Dec 2024) —
  recreated Skyrim animations, partial, not SCVI-native. Not pulled.

### Community / forums

- Steam SCVI discussions: moveset/moveset-swap talk is hex-editing pak
  chunks to swap numeric animation IDs between characters — confirms the
  numeric animation-id system Scuffle documents, but is not an extraction.
- awesome-game-file-format-reversing (Bandai Namco section): SoulTools-1–4
  cover SCI–IV only; no SCVI entry. SC2 in-repo teardown
  (`teardown/soulcalibur-2/`, 270 files) is a different game.

## What was pulled (whole, never rebuilt from scratch)

1. **Scuffle, vendored**: `tools/anim/scvi-scuffle/` — 127 files byte-verified
   127/127 vs upstream blobs at the pinned commit, + 3 local `.gitkeep`
   files. Excluded: `build/`, `ENVsc6/`, `Data/Tools/` binaries,
   `nuitka-crash-report.xml`, `.devin/wiki.json`.
2. **Movelist data, run**: the vendored parser was run offline against all
   22 `movelists/*.sc6_movelist` dumps → `teardown/soulcalibur-6/parsed/`
   (64,311 moves, 6,348 attacks, 5,360 attack moves).
3. **WH banks, wired**: `game/assets/movesets/scvi-*.json` (22 banks, 5,360
   moves, schema v2) — every move carries extracted frame data + its .mot
   animation id (`anim_ref`).

## Still missing (exact gap)

- **.mot animation motion data** — uncracked; see `MOT-FORK-20261121.md`.
- **Hitbox placement** — lives (at least partly) in the .mot, per Scuffle's
  own doc; arrives with the .mot crack.
- **Move names** — not in the movelist; live in the game's UI strings.
