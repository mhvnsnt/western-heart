# SF 3D Teardown — Pull Status (owner order 2026-10-19 ~20:26 CDT)

"Pull models from the 3D SF games, get their moves and arenas, translate SF moves to Tekken-style
gameplay like Tekken 7 did with Akuma, then make proprietary Eastern Mind versions of them."

## Archive.org catalog state (from street-fighter-3d-games/CATALOG.md)

| # | Game | Size | File (verified via archive.org metadata API) | State |
|---|------|------|---------------------------------------------|-------|
| 1 | SF EX2 Plus (PS1) | 198 MB | `Street Fighter EX2 Plus.7z` | NOT on disk — downloadable, blocked on disk space |
| 2 | SF EX Plus Alpha (PS1) | 252 MB | `Street Fighter EX Plus Alpha.7z` | NOT on disk — downloadable, blocked on disk space |
| 3 | SF EX3 (PS2) | 669 MB | BIN image | NOT on disk — blocked |
| 4 | SFIV PC (Build 3584) | 4.18 GB | 7z | NOT on disk — blocked |
| 5 | SF X Tekken (PS3) | 12.99 GB | PS3 ISO | NOT on disk — blocked |
| 6 | Ultra SFIV (PS3) | 16.61 GB | PS3 ISO | NOT on disk — blocked |

**No SF game ISOs/discs are on local disk right now.** A prior extraction (2026-10-14, deleted by
disk-space-guardian) only ever covered EX2 Plus + EX Plus Alpha into
`game-reverse-engineering/street-fighter-3d-games/extracted/`; the re-extractable sources were
also cleaned off disk. ISO listings survive in `work/ex-plus-alpha-iso-listing.txt` (245 entries)
and `work/ex3-iso-listing.txt`.

## What is known from the prior listings (no re-guessing)

SF EX Plus Alpha ISO (volume `SFEXPLUSALPHA`) character model data lives in:
- `/PL/P00.PAC` … `/PL/P19.PAC` (~26 files, ~300 KB each) — character packages = **the model source**
- `/OVL/PLxx_*.OVL` — player overlays; `/TMD/*.LMD` (e.g. `VEGADAMA.LMD`) — PS1 TMD models
- `/STG/SxxT.PAC` (~135 KB each) — stage textures; `/STG2/SxxD.PAC` (~83 KB each) — stage geometry
- `/TIM/`, `/TEX/`, `/MOV/`, `/MUS/`, `/SND/` — textures, movies, music, per-character sounds

EX3 (PS2, volume `STREET_FIGHTER_EX3`) is a single `/PS2.DAT` (604,702,720 bytes) + `/SLUS_201.30`
— an Arika packed container, needs dedicated PS2 unpacking (different lane).

## What IS wired in the repo today (main)

Sketchfab intake models (owner 2026-10-19) — internet models for quality, per the order's
"Internet models OK for quality, game files are source of truth for moves/animations":

| Fighter | roster dir | Model | Textures/UV | Rig |
|---------|-----------|-------|-------------|-----|
| Zangief | `roster/zangief/attires/attire1/model.glb` (20.1 MB) | CC-BY johnny136 | 3 images, TEXCOORD_0 ✓ | static (no skin) |
| Blanka | `roster/blanka/attires/attire1/model.glb` (4.6 MB) | Free Standard allanromanreyes | 12 images, TEXCOORD_0 ✓ | static (no skin) |
| Vega | `roster/vega/attires/attire1/model.glb` (1.6 MB) | CC-BY pierodsoto01 | 4 images, TEXCOORD_0 ✓ | 1 skin, 385 nodes ✓ |

All three validate as real glTF, have UV-mapped textures (NO-UNTEXTURED-MODELS-law compliant).
Wired in `game/js/assets.js` MODEL_URLS, `game/js/fighter.js` MOVESET_MAP (King/Bryan/Xiaoyu
anim proxies), `game/js/movesets.js` MOVESET_IDS; 12-move proxy movesets
(`game/assets/movesets/{zangief,blanka,vega}.json`) are Tekken-3-bank proxies — **real SF move
translations land in PR 2.**

## Blocker (honest)

**Model extraction from the actual game discs is blocked on disk space.** 2026-10-20 ~02:30 CDT
a re-pull of items #1/#2 was attempted: `/dev/mapper/rv` sits at 100% (was 97% → 100% while
concurrent lanes wrote; concurrent CloudDog cleanup lane active). The ~450 MB staging cannot
land. Nothing else on disk was touched; own corrupt partial downloads were removed.

**Resume path (no re-guessing):** `~/workspace/_sf-scratch/dl.sh` holds the exact download URLs
resolved via the archive.org metadata API:
- `https://archive.org/download/street-fighter-ex-plus-alpha.-7z/Street%20Fighter%20EX%20Plus%20Alpha.7z`
- `https://archive.org/download/street-fighter-ex-2-plus.-7z/Street%20Fighter%20EX2%20Plus.7z`
Run it when the disk drops below ~90%. After that, walk the ISOs with
`game-reverse-engineering/street-fighter-3d-games/work/iso9660_walk.py` (existing tool, not new
hand-tooling) and pull `/PL/*.PAC` (~8 MB total — Git-safe) into `extracted/ex-plus-alpha/`.
Suggested decode stack per the NO-HAND-TOOLING law: **jPSXdec** for ISO/TIM/XA extraction,
then a community TMD→OBJ pipeline for the model data inside the PACs (PS1 TMD format). Arika's
PAC is a proprietary container — cracking it belongs to a dedicated RE pass, not this PR.

## Eastern Mind versions (proprietary takes)

Design docs in `eastern-mind/` (this folder): proprietary WH takes of the SF fighters — same
archetype, our own identity. **WH names are pending the owner's pick** (per the intake pattern:
never invent canon names). Game-file moves are the source of truth; the Tekken-style translation
(Akuma-in-T7 pattern) and the real movelists land in PR 2.

## PR staging

- **PR 1 (this PR):** inventory (this doc) + extracted-archive audit + Eastern Mind design docs.
- **PR 2:** real SF movelists translated to Tekken notation (`game/assets/movesets/sf-*.json`,
  schema v2, Akuma pattern: qcf/dp/charge motions mapped to Tekken input slots) + arenas
  (`game/assets/stages/sf-*`) once game-file move/anim data is in hand.
