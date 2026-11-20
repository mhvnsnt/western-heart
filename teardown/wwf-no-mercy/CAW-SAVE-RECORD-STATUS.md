# CAW save-record layout — status (2026-10-13)

## Blocked on a real save file
The live save-record byte layout (created-wrestler struct in EEPROM/
Controller Pak) CANNOT be decoded from the ROM alone. It requires a real
save file dumped from an emulator.

## What's documented (ROM side)
- Music track table @0x168D790 (50 entries, ids 0x33-0x39 = ORIGINAL 1-7).
- Part-string regions @0x168DD89+ (body types, elbow pads, masks, attire...).
- Wrestler ID table (42 entries).
- Text-code classes (zero-width vs expansion).

These give every id→name mapping the save references, but NOT the byte
offsets or struct layout of the save record itself.

## What's needed
1. Run No Mercy in an emulator (e.g. Project64).
2. Create a CAW with KNOWN values (e.g. all parts = first option,
   music = ORIGINAL 1, name = "TEST").
3. Dump the EEPROM/Controller Pak save.
4. Diff the save against the ROM id tables to fix byte offsets.

## Recomp cross-ref
No EEPROM/save symbols in `recomp/syms/dump.toml` (all nearby functions
are unnamed: `func_8013D630`, etc.). The save/load code is not yet
identified in the decompilation.

## Community docs
`re-docs/docs/ui/menus/` describes the CAW UI (18 save slots in 2 pages
of 3x3 grids) but not the binary save format.
