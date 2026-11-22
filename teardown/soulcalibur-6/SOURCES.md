# Soulcalibur VI — Sources (Lane 1C, 2026-11-21)

Licence/source is logged honestly next to every item (LICENCE-NOT-A-GATE:
licence never blocks, never leaves a gap). No game files are vendored in this
PR — only open-source tooling, extracted movelist data, and docs.

## 1. FottenSC/Scuffle — THE pull (vendored, MIT)

- Upstream: https://github.com/FottenSC/Scuffle
- Description (upstream): "Soulcalibur frame data" — live frame-data reader
  for SCVI (PC), built from the useful parts of Tekken Bot Prime. Includes a
  working movelist-bytecode parser and 22 fighters' movelist dumps.
- Licence: **MIT** (`LICENSE`, vendored).
- Pinned commit: `b8e8129b58417b8b71189f05ea3e789b09493f10`
  (main, 2026-06-06, "Small fixes").
- Fetched: codeload tarball
  `https://codeload.github.com/FottenSC/Scuffle/tar.gz/refs/heads/main`,
  24,361,125 B,
  sha256 `3cf5b7a7ffd638331e5c12cb1d36847581010d5f6d8c07b97e8a9ba88feea501`.
- Vendored: 127 files, **byte-verified 127/127 against upstream git blob
  SHAs** at the pinned commit (see `verify_upstream.py` in the lane workdir;
  lane record kept at
  `~/workspace/_xbox-teardown-pull-20261120/lane-1c-scvi-complete/`).
  Plus 3 local `.gitkeep` files (empty `Data/Custom/*` dirs the parser
  requires; git cannot track empty dirs — see WH-NOTES.md).
- Path: `tools/anim/scvi-scuffle/`.
- Excluded (deliberately, documented in WH-NOTES.md): `build/` (PyInstaller
  output incl. `SCUFFLE.exe`, rebuilt from the vendored source),
  `ENVsc6/` (vendored Python venv), `Data/Tools/` (prebuilt
  `VV_MovelistViewer` incl. `UAssetAPI.dll` + `Movelist Viewer.exe`),
  `nuitka-crash-report.xml`, `.devin/wiki.json` (agent config).
  Prebuilt binaries are NOT vendored — source only + upstream release
  instructions, per the DOA6-lane precedent.
- The author's own caveat (upstream README, quoted): "Some of the frame data
  is even correct." The parser is the best available; its outputs are
  reproduced verbatim in `parsed/` with no hand correction.

## 2. The raw PC game (NOT pulled by this lane — already in-repo)

- archive.org item `dixen-18-soulcalibur-vi`, "Soulcalibur VI (PC)",
  file `[dixen18] Soulcalibur VI.zip`, 11,441,266,068 B,
  md5 `55259ff04257400d1d0e23df4d8e05a1`,
  sha1 `feac0ac177d9dbcdeb2be1c49d0c147eb00f51e3`.
- Already stored: WH+GRE release `soulcalibur6-archiveorg-20261106`
  (7×1.9 GB parts, whole md5/sha1 verified, pull-back verified, 2026-11-06).
- This lane did NOT re-download it. Its internal structure was verified live
  via HTTP range requests against the archive.org zip central directory
  (2026-11-21): 5 entries — `[dixen18] Soulcalibur VI/Data01.dxn`
  (deflate, 11,131,847,685 B compressed / 11,135,021,218 B uncompressed),
  `Data02.dxn` (281,191,686 B), `Data03.dxn` (21,014,493 B),
  `Setup.exe` (4,037,453 B). It is a FreeArc (.dxn) repack inside a deflate
  zip — see `MOT-FORK-20261121.md` for why that blocks .mot extraction here.

## 3. umodel / Gildor — SCVI mesh/texture support, animations NOT supported

- Thread: https://www.gildor.org/smf/index.php?action=printpage;topic=6384.0
  (last crawled 12 days ago; unchanged since 2018).
- AES key is public in that thread; UE 4.17 loads meshes/textures. Animations
  are `.mot` files inside the `.pak` (per the thread: "if you extract the pak
  with quickbms, then you will see that the animations are actually .mot
  flies [sic]") and umodel does not support them: "nobody has cracked that
  yet, only meshes and textures" — Anim = No in the UE Viewer table.
- No code taken from umodel. Cited as the negative result only.

## 4. FluffyQuack SCVI mods — animation-ID swaps, no extraction

- Nexus Mods, SoulCalibur VI section, author FluffyQuack — e.g. "Nightmare's
  SC3 Idle Animation" (mod 21, last updated 12 Aug 2019): swaps in an
  animation already present in the game by numeric id (notes list ids 620
  Taunt, 689 SC3 Nightmare idle, 768 Idle). Author: "I've been looking into
  it replacing animations but there's little to no documentation" / "That
  might not happen anytime soon."
- Fluffy Manager 5000 (mod manager) + SC6 savegame tool (CaS PNG
  import/export) — no moveset/animation extraction. Nothing pulled.

## 5. Nexus Mods Skyrim ports — partial, Skyrim-format, NOT SCVI-native

- "Sophitia Animations (Soulcalibur VI) MCO" by lingyt11 (mod 88175, v1.2,
  updated 05 May 2025) and "SoulCalibur VI Kilik Quarterstaff moveset
  (MCO/SCAR/BFCO)" by LilBadJj (mod 112109, v1.0, 16 Dec 2024, 97 KB +
  233 KB). Recreated/converted Skyrim animations inspired by SCVI, not
  extracted SCVI data. Nothing pulled.

## 6. Checked and NOT a solution

- **Bigchillghost/ARC** (https://github.com/Bigchillghost/ARC) — "Animation
  Recipe Cracker", a generic animation-format RE helper (C-like layout
  definitions, FBX export), 4 stars, 6 commits, 2023, Windows-only. No SCVI
  .mot definition. Recorded only.
- **iniGlowee/nier-mot-extractor** — bulk-extracts NieR:Automata `.mot`
  files via the NieR2Blender2NieR add-on. Different game, different format.
  Not applicable to SCVI. Recorded only.
- **SoulTools-1/2/3/4** (awesome-game-file-format-reversing, Bandai Namco
  section) — Soulcalibur I–IV tooling (models, motions, PKG/SPD). SCVI is
  UE4 + .mot; these tools do not cover it. The in-repo SC2 teardown
  (`teardown/soulcalibur-2/`, 270 files) is a different game, used only as a
  structural reference.
- **archive.org** (live advancedsearch 2026-11-21, `title:soulcalibur AND
  mediatype:software`, 28 hits): no SCVI teardown/converter/extraction item
  exists — only raw games, prototypes, and unrelated items.

## 7. Generated by this lane (from the sources above)

- `teardown/soulcalibur-6/parsed/*.json` — 22 fighters, produced by running
  the vendored Scuffle `MovelistParser.py` offline (driver
  `teardown/soulcalibur-6/run_parser.py`). Totals: 64,311 moves, 6,348
  attacks, 5,360 attack moves.
- `game/assets/movesets/scvi-*.json` — 22 WH schema-v2 banks, produced by
  `teardown/soulcalibur-6/convert_banks.py` from the parsed tables
  (5,360 moves). Conversion rules are documented in the converter header and
  in every bank's `honesty` field.
