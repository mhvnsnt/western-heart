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
- **PR 2 (IN PROGRESS, branch `sf/teardown-pr2-movesets-stages-20261019`):** real SF movelists
  translated to Tekken notation — `game/assets/movesets/sf-{ryu,ken,akuma,zangief,blanka,vega}.json`
  (schema v2, Akuma-in-T7 pattern, 173 moves total), wired in `game/js/movesets.js`
  `MOVESET_IDS` — + arenas (`game/assets/stages/sf-ex/stages.json`: 8 EX+α packs by
  STG/STG2 index, 19 EX2 Plus named stages verbatim). Move-name/inputs source-verified:
  SLUS_005.48 binary verbatim list + dlh/megura guides + SuperCombo EX2 wiki.
  Frame data = archetype estimates (honest flag per schema rule; real OVL decode open).

## PR 2 — real SF movelists → Tekken notation (2026-10-20)

Generator: `teardown/street-fighter-3d-games/tools/build_sf_movesets.py` (reproducible).

| File | Moves | Real move data source |
|------|-------|----------------------|
| `game/assets/movesets/sf-ryu.json` | 27 | binary-verbatim names (SLUS_005.48) + dlh EX+α inputs; Shin Sho Ryu Ken / Fire Hado Ken flagged EX2+ |
| `game/assets/movesets/sf-ken.json` | 25 | SuperCombo EX2 Plus wiki (Roll, Shippu Jinrai Kyaku); binary strings for Reppa/Shinryu |
| `game/assets/movesets/sf-akuma.json` | 32 | 12 named specials/supers verified in BOTH binary + dlh guide (Ashura Sen Ku, Shakunetsu, Shun Goku Satsu, …) |
| `game/assets/movesets/sf-zangief.json` | 29 | 8 specials/supers in binary list + Kao_Megura inputs (SPD 360+P, Russian Suplex 360+K, FAB 720, Super Stomping, …) |
| `game/assets/movesets/sf-blanka.json` | 31 | period guides (25th-anniversary/EX2 FAQ) + SuperCombo EX2 wiki; EX2+ supers/meteor flagged |
| `game/assets/movesets/sf-vega.json` | 29 | Capcom Fighting Collection 2 period movelist; wall-dive chain (Flying Barcelona → Izuna Drop / Claw Attack) |

Translation contract (Akuma-in-T7 pattern, per file `sf_translation_contract`):
`1=LP, 2=MP, 1+2=HP, 3=LK, 4=MK, 3+4=HK`; motions (qcf/dp/qcb/hcb/charge/360/720)
preserved literally; mash moves marked; charge moves annotated with charge direction.
Every move carries `sf_move`/`sf_input`/`sf_game`/`sf_source` provenance. `proxy:false`
(real move data); `anim_ref` still points at Tekken-bank proxies until SF animation
data is decoded from `PL/*.PAC`; frame data = archetype estimates, flagged per the
schema honesty rule (real frame data lives in the `OVL/PLxx_*` tables — open RE work,
see TEARDOWN.md 2c).

Stage defs: `game/assets/stages/sf-ex/stages.json` — 20 EX+α packs keyed by
STG/STG2 pack index (names pending game-data cross-check — none invented) + 19
EX2 Plus stages verbatim. Data-only; registration into `game/js/stages.js` is Lane 4's edit surface
(another lane owns that file; not touched here).

Re-pull note (2026-10-20 ~03:33 UTC): the two 7z re-downloads resumed by a prior lane
arrived CORRUPT (over-size appends; both failed py7zr header validation), so they were
re-downloaded CLEAN from scratch (`~/workspace/_sf-scratch/clean-dl.sh`) with
archive.org-metadata size checks + py7zr integrity gates.

**Extraction results (2026-10-20, PR 2):** EX Plus Alpha `.bin` verified
(528,049,872 bytes; jPSXdec v2.0 + Temurin JRE 17; 612 disc items indexed) and
fully extracted — `teardown/street-fighter-3d-games/extracted/ex-plus-alpha/`
holds PL/ (26 PACs), STG/ + STG2/ (20 packs each — CORRECTION: earlier docs said 8),
TMD/ (loose models), and `PAC-CHUNK-INDEX.json`. TIM-chunk finding: the 134
magic-0x10 chunks are NOT standalone TIMs (version field 0x54 ≠ 0x00) — PAC
container decode is a dedicated RE pass, logged on the teardown-idle queue.
EX2 Plus 7z re-download runs a retry loop (archive.org transfer throttling);
its `/PL/*.PAC` extraction follows in PR 3. Stage defs above were corrected
to the real 20-pack count.
