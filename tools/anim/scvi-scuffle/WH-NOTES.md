# WH-NOTES — FottenSC/Scuffle (vendored)

## What this is

SCUFFLE — "Soulcalibur frame data": a live frame-data reader for
SoulCalibur VI (PC) plus a **working parser for the game's movelist
bytecode** and 22 fighters' movelist dumps. Upstream:
https://github.com/FottenSC/Scuffle — "Soul Calibur 6 Live Frame Data
Reader — based on the useful parts of the popular Tekken Bot Prime."

## Pin

- Upstream commit `b8e8129b58417b8b71189f05ea3e789b09493f10` (main,
  2026-06-06, "Small fixes").
- Licence: **MIT** (`LICENSE`).
- Fetched 2026-11-21 as codeload tarball (24,361,125 B, sha256
  `3cf5b7a7ffd638331e5c12cb1d36847581010d5f6d8c07b97e8a9ba88feea501`).
- **127/127 vendored files byte-verified against upstream git blob SHAs**
  at the pinned commit. Plus 3 local `.gitkeep` files (see below).

## What is vendored / excluded

Vendored (this directory, upstream layout preserved):
- Root Python source: `MovelistParser.py` (the parser — 141,689 B),
  `MovelistEnums.py`, `GameplayEnums.py`, `AddressMap.py`, `ByteTools.py`,
  GUI modules (`GUI_MoveViewer.py` etc.), `main.py`, build scripts.
- `Config/` (address map, HowTo, overlay configs).
- `movelists/*.sc6_movelist` — 22 fighters' movelist bytecode dumps from
  live game memory (~0.9–1.1 MB each).
- `Data/Character/*/Scripts/` + `Data/Common/` — parsed script definitions
  and value-type dictionaries the parser reads.
- `README.md`, `__HowTheMovelistBytesWork.md` (the format doc), `LICENSE`,
  `SoulcaliburVI_SCUFFLE.CT` (Cheat Engine table), `pyproject.toml`,
  `uv.lock`, specs.

Excluded deliberately:
- `build/` — PyInstaller output (`SCUFFLE.exe` etc.). Rebuildable from the
  vendored source; binaries are not vendored.
- `ENVsc6/` — vendored Python venv (thousands of files).
- `Data/Tools/` — prebuilt `VV_MovelistViewer` (`Movelist Viewer.exe`,
  `UAssetAPI.dll` 7,288,320 B). Source-only pull; get the prebuilt viewer
  from upstream releases if needed.
- `nuitka-crash-report.xml`, `.devin/wiki.json` — crash log / agent config.

## Local additions (3 files)

- `Data/Custom/Value_Types/.gitkeep`, `Data/Custom/Scripts/A5/.gitkeep`,
  `Data/Custom/Scripts/25/.gitkeep` — the parser's `load_json()` does an
  unconditional `os.listdir('./Data/Custom/Value_Types/')`, so it crashes
  if the (empty, untracked) upstream `Data/Custom/` dirs are missing.
  These empty dirs fix that; they add no data.

## How the lane used it (offline, no game needed)

```sh
# from this repo root, with python3:
SCUFFLE_DIR=tools/anim/scvi-scuffle python3 teardown/soulcalibur-6/run_parser.py
# -> teardown/soulcalibur-6/parsed/<fighter>.json (22 files)
python3 teardown/soulcalibur-6/convert_banks.py
# -> game/assets/movesets/scvi-<fighter>.json (22 banks, 5,360 moves)
```

Result (2026-11-21 run): 22 fighters, 64,311 moves, 6,348 attacks,
5,360 attack moves. The parser runs offline in ~5–18 s per fighter.

Live use (needs the game + Windows, per upstream README): download the
latest release from https://github.com/FottenSC/Scuffle/releases/, run the
`.exe` alongside SoulCalibur VI (PC, windowed/borderless — no fullscreen).

## Caveats (upstream's own words)

- Upstream README: "Some of the frame data is even correct." The parser is
  the best available; its outputs are reproduced verbatim in
  `teardown/soulcalibur-6/parsed/` with no hand correction.
- The movelist contains no move names and no character name; commands are
  the parser's raw neutral-parse output (may contain `.`/`?`
  placeholders). Hitbox placement lives (at least partly) in the `.mot`
  animation files, which are NOT cracked — see
  `teardown/soulcalibur-6/MOT-FORK-20261121.md`.
- Movelist format (from `__HowTheMovelistBytesWork.md`): 30-byte header,
  magic `KH11`; ~3,000 moves/fighter × 72 bytes (animation/.mot id @0x00,
  multipliers, total frames @0x34, cancel-block address @0x38, up to 6
  attack indexes @0x3C); attacks × 112 bytes (startup @0x36, active @0x38,
  damage @0x3A, stuns @0x44/46/48); cancel blocks are a bytecode FSM
  (cancels, TC/TJ/REV/GI frames, recovery, button commands, lethal hits).
