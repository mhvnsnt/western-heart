# tools/t7-extract — T7 extraction pipeline (TRACK 1)

Wrapper + validator for pulling Tekken 7 assets into Western Heart.
Full pipeline doc: `docs/research/T7-EXTRACTION-PIPELINE-2026-10-23.md`.

## Files

- `run_pipeline.py` — runs the pipeline on the credentialed (Steam-logged-in)
  machine. Windows-primary, cross-platform Python.
- `validate.py` — validates tool installs and extracted-output structure.
  Runs with NO game files.
- `run_pipeline.bat` — Windows shim (calls `run_pipeline.py`).

## Quick start (extraction machine)

```bat
REM 0. sanity: tools + T7 paths, no game launch
python tools\t7-extract\run_pipeline.py --t7-dir "C:\Program Files (x86)\Steam\steamapps\common\TEKKEN 7" --out "D:\t7out" --check-only

REM 1. unpack paks (no game needed)
python tools\t7-extract\run_pipeline.py --t7-dir "<T7>" --out "D:\t7out" --stage unpack

REM 2. movesets: launch T7, load Law/Lars, extract with TKMovesets2
REM    (interactive — the script prints the click-path), then:
python tools\t7-extract\run_pipeline.py --t7-dir "<T7>" --out "D:\t7out" --stage movesets

REM 3. validate before anything lands in game/assets/
python tools\t7-extract\validate.py --check-output "D:\t7out"
```

## Stages

| Stage | Needs game running? | Tool |
|---|---|---|
| `check` | no | path + tool verification |
| `unpack` | no | repak (primary) / umodel / QuickBMS scripts |
| `movesets` | YES | TKMovesets2 (memory extraction, interactive) |
| `anims` | YES (for export) | motbinExport / TKMovesets2 anims + Blender addon |
| `convert` | no | umodel/Blender/wwiseutil mapping into `game/assets/` |

`--dry-run` prints commands without executing. `--stage all` runs everything
in order (movesets stage still needs the manual in-game extraction first).

## Status

- [WIRED] scripts + validation (this PR)
- [AWAITS FILE PULL] actual T7 runs on the credentialed machine
