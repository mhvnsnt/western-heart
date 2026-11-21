# Project-G1M — vendored (Dead or Alive 6 toolchain)

Native Noesis C++ plugin for Koei Tecmo Katana-engine files: `.g1m`
(models), `.g1t` (textures), `.g1a` / `.g2a` (skeletal animations). This
is the DOA6 animation extractor: it turns the `.g1a` / `.g2a` clips inside
`root.rdb` into viewable, exportable (FBX) animations.

Upstream: https://github.com/Joschuka/Project-G1M — by Joschuka (Dimy).
Licence: GNU General Public License v2.0 (GPL-2.0) — see `LICENSE`.

## Version pinned

- Vendored source: upstream `main` at commit
  `d69a6d053ab9f038f4961e694a3a62a2aa2f689b` (33 files, 264,157 B).
- Upstream main tarball sha256:
  `589f63ccf2c813b23d11a436d06154b8e7dc5ffb8cad0ae36ee19c76f6856b92`
  (fetched 2026-11-20; per-file sizes verified against the tarball listing).
- Latest upstream release: v1.8.2, tag `191825b` (28 Sep 2026) — "Put Soft
  loading as option"; removes the VBuffer assertion; fixes animation length
  and foot sliding from a missing last frame when not explicitly keyframed.
  Main HEAD here is one commit past that release.
- Prebuilt DLL: fetch `ProjectG1M.dll` from the v1.8.2 release page
  (https://github.com/Joschuka/Project-G1M/releases/tag/v1.8.2) — the DLL
  itself is NOT vendored here (source-only pull; build it or take the
  release asset).

Note: the upstream README still carries an "Archiving this project…"
note. It is stale — it predates the author's return (v1.7.5, v1.8.1 in Feb
2026 with a same-day crash fix, v1.8.2 in Sep 2026, active issue replies
Feb 2026). The project is maintained as of Sep 2026. "Copter" in that note
is collaborator hearhellacopters, whose fork carries fixes.

## Build

Visual Studio solution `ProjectG1M.sln` (VS16) — build Release|x64. The
output `ProjectG1M.dll` is a Noesis plugin: drop it in Noesis' `plugins/`
folder next to the others. Options live under Noesis' Tools tab.

## Use (DOA6)

1. Extract the game archive first (see `../doa6-rdbexplorer/README.md`):
   `root.rdb` → `.g1m` / `.g1t` / `.g1a` / `.g2a` files.
2. In Noesis, open a `.g1m` model (provide its external skeleton `.g1m`
   when asked, or enable auto-load of the first `.g1m` in the folder), then
   open the matching `.g1a` / `.g2a` animation. Export FBX from Noesis.
3. Cloth meshes are simulated by physics at runtime, so they stay at
   T-pose in the export — rig them to the driver bones, use cloth
   simulation, or transfer data from the driver meshes (per the author's
   2020 thread).

## DOA6 evidence

- Joschuka's thread (Mar 2020) lists Dead or Alive 6 among the supported
  games; DOA6 models were tested extensively after the last updates
  ("with doa6 it seems that updating the script worked").
- The awesome-game-file-format-reversing index lists Project-G1M for the
  Katana engine across Nioh, DOA5/6, Warriors, Atelier, Toukiden, Fire
  Emblem: Three Houses, Persona 5 Scramble.
- Independent corroboration: community members extracted full per-character
  DOA6 animation sets through this toolchain (e.g. the GTAinside
  Kasumi/Rig/Kokoro/Momiji/NiCO/Zack/Diego/Lisa/Leifang packs — GTA format,
  cited in `teardown/doa6/SOURCES.md`, not pulled).
