# Street Fighter IV — teardown

Scope: Street Fighter IV (vanilla), Super Street Fighter IV, Super Street
Fighter IV: Arcade Edition (incl. v2012), Ultra Street Fighter IV. All four
share the same Capcom MT Framework file formats (`.bac` move scripts,
`.bcm` input/cancel data, `.emo`/`.emz` models, `.emm` materials), so one
toolchain covers the whole SFIV family — including Street Fighter X Tekken,
which reuses these formats (see `../street-fighter-x-tekken/`).

## What is in this directory

- `tools/sf4tools/` — Dantarion's `sf4tools` vendored WHOLE (MIT, source
  commit `e5c17132f3b6e63f66150c3a347a9e8f6e0d73a4`, 2015-05-06). The
  `SFUltraDiff/src/` Python code (`bac.py`, `bcm.py`, `diff.py`, `util.py`)
  parses `#BAC` moveset files and `.bcm` files and dumps them as JSON. This
  is the moveset format as cracked by the SFIV modding community — the code
  that reads the actual move data (scripts, inputs, cancels, charge times).
  See `SOURCES.md` for the per-file sha256 manifest.
- `sf4-nx.md` — record of `jvankooo/sf4-nx`, the working static-recomp port
  of Street Fighter IV (Xbox 360) to Nintendo Switch (GPL-3.0). The port
  framework is recorded, not vendored — see that file for why.
- `SOURCES.md` — every source, licence, commit, and sha256 for this dir.
- `SFIV-TEARDOWN-STATUS.md` — what exists, what was pulled, what is still
  missing, per game.

## What is NOT here (read this before assuming)

- NO extracted movesets, NO extracted animations, NO extracted models.
  No complete extracted SFIV/SFxT/USFIV moveset pack was found anywhere
  (archive.org checked live, modding communities, GitHub, Models Resource).
  What was pulled is the toolchain that READS the formats, not the data.
- NO game files. The toolchain needs a SF4 PC install (or the Xbox 360
  disc files) to run against. The owner owns these games on Xbox.
- NO WH bank converter for bac/bcm yet. Same gap as the SF EX `PL/*.PAC`
  clips: clips/data held, converter not built. Building a bac/bcm → WH bank
  converter is the next step, and it starts from `tools/sf4tools/` here.

## How to use

1. Take `.bac` / `.bcm` files from a SF4 PC install
   (`resource/battle/chara/<CODE>/`, e.g. `RYU`, `KEN`).
2. Run the `SFUltraDiff/src/*.py` parsers to dump each moveset as JSON.
3. Feed that JSON into a WH bank converter (to be built) — same pattern as
   `../street-fighter-3d-games/tools/build_sf_movesets.py` does for SF EX.

## Licences

- `tools/sf4tools/` — MIT (Dantarion). Licence file vendored at
  `tools/sf4tools/LICENSE`.
- `sf4-nx` (record only, not vendored) — GPL-3.0.
- Game data itself (movesets, models, animations) remains Capcom's.
  Licence status never gated this pull; sources are logged honestly in
  `SOURCES.md`.
