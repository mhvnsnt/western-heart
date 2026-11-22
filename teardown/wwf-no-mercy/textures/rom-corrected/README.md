# Textures re-extracted with the W3c-corrected decode (2026-11-19)

This directory holds the full No Mercy texture set re-extracted from the
Rev-A ROM with the game-exact FileTable window (FileTable `0x16C31D8`,
FirstFile `0x1BD150`, **1-based** file IDs). Every PNG is named
`<subject>/<Descriptive_Name>_<fid>.png` where `<fid>` is the file's real
game file ID. 5,035 PNGs + `manifest.json`.

## Why a second copy exists

The sibling `rom/` directory holds the OLD extraction, built with the
correct table constants but **0-based indexing**: every file labeled N
actually contains game file N+1 (same content, wrong name — the file
`rom/arena/ArenaAnnouncer_Table_Sides_07B3.png` holds game file `0x07B4`,
which lives here as `arena/ArenaAnnouncer_Table_Sides_07B4.png`). The old
layout's names are therefore off by one everywhere and cannot be fixed by
replacing contents in place — the corrected files have different names.

`rom/` is kept for now only because removing 5,030 files needs the owner's
`owner-approved-deletion` label (repo law: agents never self-apply it). The
follow-up deletion PR removes `rom/` once the owner taps the label; until
then, **this directory is the correct texture set — use it, not `rom/`**.

The `characters/` and `environments/` directories are NOT part of the ROM
extraction (their textures come from GLB models) and are unaffected.

## Provenance

Extracted 2026-11-19 by the full-ROM survey (`tools/full_pass.py` +
`tools/fixups.py`, W3c-correct window). Full file table:
`../file-table.csv`; catalogue: `../FILE-TABLE-CATALOGUE.md`. The ROM
itself is never committed.
