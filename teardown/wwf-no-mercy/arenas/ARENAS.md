# WWF No Mercy — Ring / Arena Geometry Extraction

Source ROM: `WWF No Mercy (USA) (Rev-A).z64` (CRC32 BACEEA13).
Method: `tools/assemble_arenas.py` groups the already-extracted per-piece
AkiModel OBJs (`models/`, from `extract_all_models.py` + `NoMercy-FileTableDB.txt`)
into per-arena combined OBJs. Each output uses `g <file_id>_<label>` groups,
preserves v/vt/f, and ships a sidecar `.vc` with per-vertex RGB.

## Arenas extracted (17 assemblies)

| File | Contents |
|---|---|
| `arena_raw.obj` | RAW is WAR — 219 pieces (shared ring + crowd bowl + RAW stage/trons/ramp) |
| `arena_smackdown.obj` | SmackDown — 130 pieces |
| `arena_royal_rumble.obj` | Royal Rumble — 129 pieces |
| `arena_wrestlemania.obj` | WrestleMania — 126 pieces |
| `arena_king_of_the_ring.obj` | King of the Ring — 132 pieces |
| `arena_summerslam.obj` | SummerSlam — 132 pieces |
| `arena_survivor_series.obj` | Survivor Series — 128 pieces |
| `arena_backlash.obj` | Backlash — 131 pieces |
| `arena_armageddon.obj` | Armageddon — 131 pieces |
| `arena_no_mercy.obj` | No Mercy PPV — 130 pieces |
| `arena_cage.obj` | Cage-match ring + cage walls + shared bowl — 120 pieces |
| `backstage_bar_lounge.obj` | 74 pieces |
| `backstage_boiler_room.obj` | 73 pieces |
| `backstage_hallway.obj` | 75 pieces |
| `backstage_locker_room.obj` | 94 pieces |
| `backstage_parking_lot.obj` | 74 pieces |
| `lobby.obj` | Lobby/gorilla area — 79 pieces |

Piece → arena mapping comes from the community FileTableDB labels
(`[Arena] <Name> - ...`, `[Stage] <Name> - ...`, `[Backstage] <Area> - ...`).

## Extraction-method notes

1. **No separate arena display-list section exists.** A full type census of
   the 19,462-entry ROM file table shows arena data is *only* AkiModel files
   (838 of them) + textures. There is no F3D display-list section and no
   arena layout/placement section in the ROM.
2. **Mixed coordinate frames (honest caveat).** Big structures (crowd bowl,
   stage sets, trons, ramps, barricades, announce table) are stored in world
   coordinates and assemble into coherent scenes (verified by top-down/front
   renders). Small parts the game instances in code — ring posts,
   turnbuckles, apron skirts, cage pieces — are stored as local templates
   (e.g. all 8 apron skirts sit near the origin) with no placement data in
   the ROM. They are included in stored coordinates; exact runtime placement
   needs the arena rendering code (not yet reversed).
3. **No rope geometry in the ROM.** A label scan of the entire file table
   finds zero rope meshes — AKI games generate ropes procedurally at runtime.
4. **Texture pairing is not in the data.** Pieces carry UVs (normalized by
   the model's TextureSize nibbles) but the ROM/DB stores no model→texture
   link; pair via the `textures/` lane by TextureSize match.

## Stats

- 838 arena/stage/backstage/lobby AkiModels identified in file table
- 17 combined assemblies, all index-validated (0 bad indices, .vc counts match)
- Assembly manifest: `assembly_manifest.json`
