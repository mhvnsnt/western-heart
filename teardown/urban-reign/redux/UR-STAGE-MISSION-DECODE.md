# Urban Reign — Stage / Mission decode log (Lane 4, HeartMind 100% program)

**Date:** 2026-11-08 ~02:40 CST
**Lane:** 4 — Urban Reign stages / missions decode
**Follow-ons (2026-11-08, DONE except stage020):** `UR-STAGE-MISSION-DECODE-FOLLOWON.md` — full 100-mission census (87 DECODED / 4 no stage-candidate / 9 NOT DECODED), .bin semantics proven from the SLUS_212.09 disassembly, stage-name table (ids 0–54), mission→stage PPK mapping completed (stage003 ← 30/35/42/54; stage004 ← 9/20/24/44/48/66/82; stage020 ← 99; stage028/029/030/031 ← none; place→PPK has NO 1:1 map), and 6 arenas registered in the game (PR #1650). stage020 geometry still blocked (Editor on Windows is the named route).

**Tools used (only these — no hand-written parsers):** Redux Editor 0.5's own
`Source/vendor/roster-lib/` — `toolnative/ppk_index.py` (`ppk_entries`),
`toolnative/vmd_structure.py` (`parse_vmd`), `toolnative/vmd_mesh.py`
(`read_mesh`), `toolnative/stage_preview.py` (`room_preview`), plus the
Editor's own `Source/editor/meshes.py` (`meshes.load`, which itself runs
`read_mesh` + `native/bind.py:bind_matrices` + the exporter's strip rule +
`native/texture.py:parse_texture`). The Editor zip is on disk at
`~/workspace/urban-reign-redux/Urban.Reign.Redux.Editor.0.5.zip`
(SHA-256 `883387a9…`, verified). Roster-lib now also lives at
`~/workspace/urban-reign-redux/work/tools/vendor/roster-lib/` (moved there by
a sibling lane during this pass; the decode below ran against both paths —
same files, same results).
**Inputs:** the 7 stage PPKs + 256 mission `.bin` files + 3 sampled mission
PPKs, fetched from Jay's own repo (`mhvnsnt/western-heart`, `main`,
`teardown/urban-reign/`). No ISO downloaded; no piracy/ROM/leak sites.
**Rules:** `docs/RULES_NO_GUESSING.md` read first. No field meaning is
asserted unless the bytes prove it. Pantera is male (he/him); every other
fighter is named only, no guessed pronouns.

## 1. Stage PPKs — 7/7 containers decoded, 6/7 geometry decoded

| File | Size (B) | SHA-256 (first 16) | `ppk_index` | VMD entry (key / size) | `read_mesh` | `meshes.load` (world space) |
|---|---|---|---|---|---|---|
| stage003.ppk | 5,406,080 | `a75175ef851d87ea` | DECODED, 48 entries | fff0 / 3,986,192 | DECODED | 57,621 verts, 36,953 tris, 135 textures |
| stage004.ppk | 4,492,928 | `9bae645f188bc057` | DECODED, 46 entries | 1eb9 / 3,119,520 | DECODED | 38,747 verts, 22,769 tris, 103 textures |
| stage020.ppk | 3,571,328 | `137f756419606868` | DECODED, 23 entries | bd01 / 2,528,444 | **NOT DECODED** | **NOT DECODED** |
| stage028.ppk | 3,470,464 | `518e86aa5c37c5db` | DECODED, 36 entries | d863 / 2,190,784 | DECODED | 26,759 verts, 16,117 tris, 93 textures |
| stage029.ppk | 6,991,232 | `aad8082f2e2c4b4e` | DECODED, 44 entries | 96cb / 5,651,184 | DECODED | 77,032 verts, 49,442 tris, 98 textures |
| stage030.ppk | 4,794,624 | `f4bb723d878f4de2` | DECODED, 30 entries | 718d / 3,573,184 | DECODED | 34,873 verts, 20,757 tris, 52 textures |
| stage031.ppk | 5,175,168 | `725c8014b44146e5` | DECODED, 41 entries | 3f25 / 3,898,752 | DECODED | 46,941 verts, 28,017 tris, 75 textures |

Full per-entry tables (key, size, SHA-256, magic, VMD node lists) are in
`decoded/stages/stageNNN.json`. Per-VMD group/draw/vertex censuses and
raw (bone-local) bounds are in `decoded/stages/stageNNN.vmd.json`.
World-space bounds, triangle counts and texture counts are in
`decoded/stages/stageNNN.mesh.json`.

### What each stage PPK contains
- Exactly **one VMD entry each** — the stage geometry (node names
  `MODEL1_EXB1`, `MODEL2_EXB1…`, `polySurface…__EXB__FUNC`, `kanban__EXB`
  in stage003; `MODEL1/2/3/4` variants elsewhere). Node counts:
  003: 51, 004: 251, 020: 2, 028: 100, 029: 162, 030: 100, 031: 112.
- **Shared entries, identical across all 7 stages:** keys `58da`
  (453,620 B), `2995` (309,552 B), `e7eb` (167,148 B) — all magic
  `03 08 04 00`, i.e. VGS UI tiles (same magic as the repo's VGS header doc).
  Plus 4–16 `P3Dp` entries and one `OBPS` entry each, and 11–17
  zero-magic entries.
- **World-space bounds (from `meshes.load`, bind matrices applied):**
  - stage003: x/z ±215.92, y −8.34…97.60
  - stage004: x −14.61…19.20, y −0.44…14.03, z −15.84…7.06
  - stage028: x −8.00…8.24, y −1.07…10.44, z −10.74…10.20
  - stage029: x/z ±539.80, y −2.00…244.00
  - stage030: x ±539.80, y −49.68…209.32, z −172.61…518.37
  - stage031: x ±73.47, y −0.26…60.75, z ±69.88
  - The ±539.80 x/z + y-to-244 shell in stage029/030 (and in the mission
    VMDs below) is a shared far backdrop/sky shell, not the fight floor —
    bounds alone do not identify a stage. The fight floor is the small
    shell inside it (see stage004 room preview).
- **stage004 room-only preview (roster-lib's own `room_preview`):**
  22,769 source tris → **5,327 room tris, 15,833 room verts, 91 draws**,
  parts floor / north / south / east / west / light, room bounds
  x −10…10, y −0.1…10.1, z −8…7, centre (0, 0, −0.5).
  Full per-part breakdown: `decoded/stages/stage004.room.json`.
  Notes: `room_preview` needs a faces-shaped mesh dict, which no shipped
  tool builds — the adapter in `decoded/stage004_room.py` reshapes
  `read_mesh` + `meshes.load` outputs into that shape (thin glue, no byte
  parsing of its own). It runs only for stage004: the tool's SHELL/LIGHTS
  group maps are measured for stage004 only. Light-shaft groups are
  retained unclipped by the tool's design; shell polys are clipped to
  BOUNDS by construction.

### stage020 — NOT DECODED (exact blocker)
- `ppk_index` decodes the container (23 entries) and `parse_vmd` accepts
  its VMD entry (key `bd01`, 2,528,444 B, **only 2 nodes, both
  `BUKI_1__EXB`** — a weapon model, not a stage shell).
- `read_mesh` fails at `toolnative/vmd_mesh.py:21`: the chain command walk
  reads past end-of-file (`b[p:p+4]` empty — no op-0 terminator found
  within file bounds).
- The Editor's own fallback (`retrofit_blend.mesh_view` →
  `compact_reader.expand_for_read`) fails the same way at
  `compact_reader.py:14` (op/size read past EOF).
- **Best existing tool that could:** the Redux Editor itself on Windows
  (its `.exe` runtime; cannot run on this Linux VM), or the author's
  `native/native/vmd_mesh.py` copy — which differs from roster-lib's only
  in the influence-count assert (≤32 vs <10) and does NOT touch the
  command-walk failure, so it was not expected to help and was not run as a
  substitute. No homebrew parser was written.
- Open question (not a claim): whether stage020's playable geometry lives
  in a different entry of the same PPK, or the `bd01` VMD really is only
  the weapon prop. The other 22 entries were indexed but their payloads
  were not VMD-decoded (no VMD among them per `parse_vmd`).

## 2. Mission definition files — 256/256 read, field layout structurally mapped, semantics NOT decoded

Files: `missions/definitions/mission000.bin`–`mission255.bin`, **all exactly
8,300 B**. Full census: `decoded/missions/mission_bin_layout.json`.

### Measured structure
- **2,075 u32 columns: 1,725 constant across all 256 files, 350 varying.**
  3,635 of 4,150 u16 columns constant. The files are **97% zero bytes**
  (mission001: 8,077/8,300 zero). No float32 data: every
  plausibly-ranged float32 read is 0.0. **No ASCII strings of length ≥4
  shared across files** (6 garbage strings total) — no mission/stage/
  fighter names live in these files.
- **Varying u32 columns cluster in 94 contiguous runs,** mostly in
  0x0000–0x0570, plus sparse singles at 0x0998, 0x09b0, 0x1050, 0x1068,
  0x1708, 0x1720, a dense block at 0x1754–0x186c, and a **stride-24 table
  at 0x1884–0x1a64: 22 records × 24 B**, first u32 of each record taking
  6 distinct values across files. In mission001 the table is 21 identical
  records `(0, 0x4d0000, 0, 0, 0, 0)` + 1 all-zero record.
  The constant marker `0x4d0000` also appears at 0x00f8 and 0x011c.
- **Duplicates (measured, SHA-256): 117 of 256 files are byte-identical
  to one of two templates** — missions 120/126/127 share one file;
  missions 129–198, 207–249 and 253 share another (114 files). Only ~139
  distinct `.bin` contents exist across the 256 files.
- Header sample (mission001): u32[0..15] =
  `0x0, 0x4dffff, 0x36e2, 0xffffefca, 0x3e825b0, 0x6ea, 0x232, 0x3e8d777,
  0xffff, 0x2, 0x0, 0x0, …`. u32[1] is `0x4dffff` in most files
  (`0x4d0065` in mission255). u32[0] takes 45 distinct values; the most
  common is `0x1` (115 files — the duplicate groups).
- mission000 vs mission100 differ in only 43 bytes, at u32 columns
  0x10, 0x1c, 0x15c, 0x160, 0x1d4, 0x1e8, 0x1f8, 0x200–0x20c, 0x280,
  0x294, 0x2a4–0x2c0, 0x2d0, 0x2d4, 0x1754–0x1764.

### What this does NOT establish
No field meaning is proven: no column is identified as stage id, enemy
count, partner id, objective, timer, or reward. Candidates exist (e.g.
columns with exactly 7 distinct values, matching the 7 stage PPKs) but a
7-value column could equally be chapter, difficulty, or something else —
**naming one would be guessing, so none is named.** The exact unblocker
for semantics is the game's executable `SLUS_212.09` mission-load code
(the same executable roster-lib's `gyu_decode.py` cites for codec 8):
disassembling which offsets the mission loader reads would name the
fields. That ELF was not pulled in this lane (it lives inside Jay's own
ISO/release; no ISO was downloaded).

## 3. Mission PPKs — 3/100 sampled and decoded, 97/100 not fetched

Sampled: mission001.ppk (6,719,744 B), mission002.ppk (8,896,128 B),
mission100.ppk (7,139,072 B). Full entry tables in
`decoded/missions/missionNNN.ppk.json`. The other 97 were not downloaded
(821 MB total for 100; sampling was the honest scope for one lane).

| File | `ppk_index` | Entries | VMD entries |
|---|---|---|---|
| mission001.ppk | DECODED | 83 | 3: ae2c 3,173,696 B (32 nodes, stage geometry); 580a 486,127 B (57 nodes, fighter); 7fdf 469,836 B (59 nodes, fighter) |
| mission002.ppk | DECODED | 87 | 3: 62a0 5,114,624 B (42 nodes, stage geometry); 54d6 501,453 B (55 nodes, fighter); cb83 544,501 B (55 nodes, fighter) |
| mission100.ppk | DECODED | 89 | 2: 2051 3,872,176 B (188 nodes, stage geometry); eb5b 528,757 B (55 nodes, fighter) |

### Measured findings
- **Each mission PPK embeds its own stage-geometry VMD** (node names
  `MODEL1_EXB1`, `MODEL2_EXB1…`, same naming as the stage PPKs) — decoded
  to world space with `meshes.load`:
  - mission001 ae2c: 25,346 verts, 15,532 tris, bounds x/z ±539.80,
    y −11.24…244.00, 90 textures.
  - mission002 62a0: 50,494 verts, 28,356 tris, bounds x/z ±539.80,
    y −6.40…244.00, 227 textures.
  - mission100 2051: 58,346 verts, 37,270 tris, bounds x −275.75…211.46,
    y −76.43…58.91, z −270.22…313.63, 123 textures. Its node list also
    carries `BUKI_1`, `flowerbase`, `joint1`–`joint7`.
- **Each mission PPK embeds fighter VMDs for its enemies.** Mission001's
  580a/7fdf carry Japanese bone names (`MUNE1`, `MUNE2`, `KUBI`,
  `ATAMA`, `SAKOTSU_R/L`, `KATA_R/L`, `UDE_R/L`, `TE_R/L`, `KOSHI`,
  `MOMO_R/L`, `HIZA_R/L`, `ASHI_R/L`, `TSUMASAKI_R/L`, `MIKEN_R`,
  `MAYU_R`, `EYE_R`, `MABUTA_UP_R`, …) — two fighter models, matching the
  FAQ's Mission 1 opponents (Em Cee and Real Deal, 2 enemies). Which VMD
  is which fighter is **not** established (no names in the files).
- **Shared entries across mission PPKs:** keys `01ad` (32,528 B), `0595`
  (19,039 B), `0794` (1,160 B), `0e98` (8,736 B), `28a1` (18,080 B),
  `3d1b` (26,304 B), `58da`/`2995`/`e7eb` (the same VGS tiles as the
  stage PPKs), `a8c7` (644,680 B, VGS magic — present in mission PPKs,
  absent from stage PPKs), and many more — a shared base library plus
  per-mission entries.
- **Mission→stage link test (measured, negative):** world-space rounded
  position-set overlap between the 3 mission stage VMDs and all 6 decoded
  stage PPK VMDs is **0.0–3.0%** (best: mission002 vs stage004, 414 shared
  positions = 3.0% of mission002 — the shared sky/backdrop points).
  Method + numbers: `decoded/mission_stage_link.py`,
  `decoded/missions/posset_sizes.json`. **Conclusion: no sampled mission
  plays on any of the 7 stage PPKs' geometry as stored.** Either the
  mission PPKs carry per-mission stage variants, or the 7 stage PPKs are
  the multiplayer/versus stages while missions use separate geometry.
  Either way the PPK-id → mission link is NOT established by geometry.
- No entry in any sampled mission PPK is byte-identical (SHA-256) to any
  stage PPK VMD entry.

## 4. Stage place names — inventory from public sources, NO PPK-id mapping

The `.bin` files contain no names and the mission→stage geometry link is
negative (above), so **no stage PPK id has a measured place name.** What
exists is a place-name inventory per *mission* from public sources, to be
matched to PPK ids once the link is decoded:

- **All 100 mission titles + opponents + partner status + objectives**
  (SuperCheats FAQ v2.6, Kevin Dinglasan): `decoded/missions/mission-list-faq.txt`.
  Mission 1 "Warming Up" (Em Cee + Real Deal), mission 100 "The Mastermind"
  (William Bordin). Full FAQ text saved at `decoded/inputs/urban-reign-faq.txt`.
- **Places named per mission** (RetroAchievements set + FAQ strategies +
  USA manual, archive.org): Back Alley, Bar, Warehouse, Motel, Southend,
  Scrapyard, Abandoned Basement, Subway Station, Underground Parking,
  Chinatown, Green Hill, Apartment Rooftop, Bordin's Main Gate, Bordin's
  Building, Hideout, Slum, Kadonashi Dojo, Basketball Court, City Park,
  Chinese Market, Restaurant, Junkyard, Abandoned Theater. (The fan-made
  "Urban Reign: Chaotic Streets" stage list — Construction Site, The
  Jungle, Old Tire Warehouse — was found and EXCLUDED: it is a fan game,
  not the real game's stages.)
- **Mission 01's place is "BACK ALLEY"** per the game's own title screen
  ("BACK ALLEY — Warming Up", cited in TEARDOWN-PART-C) — but mission001's
  geometry does not match any stage PPK, so this does NOT name a stage PPK.
- The 7 `mc_stage00`–`mc_stage06.vgs` mission-stage art files exist in
  the repo but their tile payload is still undecodable (proprietary Namco
  encoding, per `UI-SYSTEM.md`), so they name nothing yet.
- **Unblocker for the mapping:** the `.bin` field semantics (needs
  `SLUS_212.09`, §2) or the full 100-mission-PPK geometry census (match
  every mission's stage VMD against every stage PPK the same measured way
  §3 did for 3 missions — 97 PPKs still to fetch, ~800 MB).

## 5. What is still blocked (exact blockers)

1. **stage020 geometry** — `read_mesh` command-walk runs past EOF;
   `compact_reader` fallback fails identically. Needs the Editor on
   Windows, or the author's `native/` VMD reader run against it (expected
   not to help — see §1).
2. **Mission `.bin` field meanings** — needs `SLUS_212.09` mission-load
   code (disassembly), or a second independent source that reads the same
   offsets. No guessing allowed.
3. **Mission PPKs 004–099 + 97 others (97/100)** — not downloaded
   (~800 MB). Sampling was this lane's scope; a full census is mechanical
   from here (`ppk_index` + `parse_vmd` + `meshes.load` per file).
4. **Stage place names per PPK id** — needs blocker 2 or 3 resolved.
5. **No stage-registry entries in `game/js/stages.js`** — registration is
   a build step for a later lane; this lane decoded data only, per the
   task. Nothing was registered or wired into the game.
6. **Repo landing deferred, not attempted:** a full clone of
   `mhvnsnt/western-heart` is 13.4 GB (`gh api` repo size 14,052,439 KB)
   and the workspace hit a disk-quota write failure once during this pass
   (recovered). The decoded JSONs below are small and ready to land by a
   lane with a full clone; no sparse checkout was used anywhere in this
   lane.

## 6. Deliverables (all under `~/workspace/urban-reign-redux/decoded/`)

- This log: `UR-STAGE-MISSION-DECODE.md` (this file's workspace copy is
  `~/workspace/urban-reign-redux/UR-STAGE-MISSION-DECODE.md`)
- `decoded/stages/stage003.json` … `stage031.json` — `ppk_index` entry
  tables + VMD node lists (7 files)
- `decoded/stages/stageNNN.vmd.json` — `read_mesh` group/draw/vertex
  census + raw bounds (6 decoded; stage020 records the exact failure)
- `decoded/stages/stageNNN.mesh.json` — `meshes.load` world-space
  verts/tris/bounds/textures (6 decoded; stage020 records the failure)
- `decoded/stages/stage004.room.json` — `room_preview` room-only geometry
- `decoded/missions/mission_bin_layout.json` — 256-file `.bin` census
  (constant/varying columns, duplicate groups, string census, diff stats)
- `decoded/missions/mission001.ppk.json`, `mission002.ppk.json`,
  `mission100.ppk.json` — sampled mission PPK entry tables
- `decoded/missions/mission-list-faq.txt` — all 100 missions (title,
  opponents, partner, objective) from the public FAQ
- `decoded/missions/posset_sizes.json` — position-set sizes for the
  mission↔stage link test
- Scripts (reproducibility): `decoded/stage_ppk_decode.py`,
  `decoded/stage_vmd_decode.py`, `decoded/stage004_room.py`,
  `decoded/mission_bin_layout.py`, `decoded/mission_stage_link.py`
- Inputs kept: `decoded/inputs/stage*.ppk` (7, 34 MB),
  `decoded/inputs/mission_defs/mission*.bin` (256, 2.1 MB),
  `decoded/inputs/mission001.ppk`, `mission002.ppk`, `mission100.ppk`
  (~22 MB), `decoded/inputs/urban-reign-faq.txt`,
  `decoded/inputs/PPK-FORMAT.md`, `PPK-GEOMETRY.md`, `UI-SYSTEM.md`
- Editor source re-extracted for the run (read-only reference):
  `decoded/editor-src/` (roster-lib path moved by a sibling lane to
  `~/workspace/urban-reign-redux/work/tools/vendor/roster-lib/`)

## 7. C4 re-score (for the coordinator — applied in HEARTMIND-COMPLETION.md)

Piece C4 was 10% ("files exist, nothing decoded"). Measured now:
stage geometry decoded 6/7 with world-space verts/tris/bounds/textures
+ stage004 room-only preview; mission `.bin` layout structurally mapped
(256/256 read, duplicates + slot table found) but semantically undecoded;
mission PPKs decoded 3/100 sampled with container + stage + fighter VMDs
identified; place names inventoried per mission but unmapped per PPK id;
no stage registration done. **C4: 10% → 45%.**
Bucket C mean 37.9% → 42.9% (~38% → ~43%); overall simple mean
(761 + 15 + 300)/27 = 39.9% (~39% → ~40%); bucket-weighted headline,
using the doc's own rounded bucket means (A 76, B 2, C 38 → 43):
0.40×76 + 0.35×2 + 0.25×38 = 40.6% (~41%) before →
0.40×76 + 0.35×2 + 0.25×43 = 41.8% (~42%) after.
(Arithmetic shown in the completion doc; only C4's row and the derived
totals were touched.)
