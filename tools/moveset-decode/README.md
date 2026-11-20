# moveset-decode — TKM2 (.tkmvst) moveset decoder for Western Heart

A stdlib-only Python decoder for moveset files produced by **TKMovesets2**
(Kiloutre, GPL-3.0, vendored at `tools/open-source/tkmovesets/`). It turns a
`.tkmvst` extraction into readable JSON the teardown and moveset lanes can
consume directly (move names, startup/active frames, damage, hitbox data,
cancel/requirement links).

```bash
python3 tools/moveset-decode/tkm2_decode.py <file.tkmvst> --out decoded.json
python3 tools/moveset-decode/tkm2_decode.py <file.tkmvst> --max-moves 20   # trimmed stdout
```

## Why this exists

TKMovesets2 is a Windows/C++ live-memory tool: it extracts a moveset from a
running game and writes a `.tkmvst` file. Western Heart's lanes run on
Linux and need the *data*, not the GUI. This decoder re-implements the
file-format read path in Python, grounded field-for-field in the vendored
sources — no format guessing:

| Decoder piece | Grounding source (vendored) |
|---|---|
| `TKMovesetHeader` parse + `ValidateHeader()` checks | `TKMovesets2/LocalStorage/MovesetStructs.h` |
| game id enum (0=T7, 1=T8, 2=TTT2, 3=TREV, 4=T6, 5=T5) | `TKMovesets2/GameSpecific/GameIDs.hpp` |
| block list, block order, file assembly, CRC block set | `TKMovesets2/GameSpecific/Extractors/Extractor_t7/Extractor_t7.cpp`, `Extractor.cpp` |
| pointer→index conversion (`TO_INDEX`) | `TKMovesets2/GameSpecific/Extractors/Extractor.hpp` |
| T7 inner structs (`Move`, `HitCondition`, …) | `TKMovesets2/GameSpecific/Structures/Structs_t7.h` (`StructsT7` + `StructsT7_gameAddr`) |
| `.tkmvst` extension, `extracted_chars` dir | `TKMovesets2/Utils/constants.h` |

## TKM2 container format

All integers little-endian. File layout (uncompressed):

```
offset 0    TKMovesetHeader (256 bytes, see table below)
offset 256  TKMovesetProperty[]  {int32 id; int32 value}, terminated by id == 0 (END)
            ... 8-byte aligned (extractor pads with 0xDD) ...
            block offset list: block_list_size × uint64, offsets relative to moveset_data_start
            ... 8-byte aligned ...
            moveset data: the blocks below, each 8-byte aligned
```

### TKMovesetHeader (MovesetStructs.h, 256 bytes)

| Offset | Type | Field | Notes |
|---:|---|---|---|
| 0 | char[4] | `_signature` | always `TKM2` |
| 4 | char[28] | `version_string` | extractor version (`"1.0"` in current builds) |
| 32 | Byte[32] | `gameVersionHash` | game-version fingerprint |
| 64 | uint16 | `gameId` | GameIDs.hpp enum |
| 66 | uint16 | `minorVersion` | per-game variant (conversions, RPCS3 builds…) |
| 68 | uint32 | `header_size` | `align8(sizeof(header))` = 256 |
| 72 | uint32 | `block_list` | absolute offset of the block offset list |
| 76 | uint32 | `block_list_size` | 8 for T7 |
| 80 | uint32 | `moveset_data_start` | absolute offset of moveset data |
| 88 | uint64 | `moveset_data_size` | uncompressed data size; **0 if not compressed** |
| 96 | uint8 | `compressionType` | 0=None, 1=LZ4, 2=LZMA |
| 100 | uint32 | `crc32` | CRC32 over the hashed block set (see below) |
| 104 | uint32 | `orig_crc32` | CRC32 at extraction time |
| 112 | uint64 | `date` | last modification, unix seconds |
| 120 | uint64 | `extraction_date` | unix seconds |
| 128 | uint32 | `characterId` | in-game character id |
| 136 | uint64 | `flags` | bit0 MovesetModified, bit1 Debug |
| 144 | char[32] | `origin` | game name, e.g. `Tekken 7` |
| 176 | char[32] | `target_character` | |
| 208 | char[32] | `orig_character_name` | (introduced in extractor 0.6) |
| 240 | uint64 | `game_specific_flags` | |
| 248 | uint16 | `conversion_origin` | |

`ValidateHeader()` (re-implemented in the decoder): signature must be
`TKM2`, `block_list_size != 0`, `block_list >= header_size`,
`moveset_data_start > block_list`.

CRC32 note: the extractor hashes only the editable blocks (properties,
movesetInfo, table, motalist, moveset, animation, mota — *not* the name
block, movelist block, or offset list), in that order, with the standard
CRC32 (poly `0xEDB88320`, init/final XOR `0xFFFFFFFF` — same as
`zlib.crc32`). The decoder reports the stored CRC; exact re-verification
from file bytes alone is not always possible because inter-block padding
(0xDD to 8-byte alignment) makes some block lengths ambiguous from the
file layout (see Limits).

### Moveset data blocks (T7: `StructsT7::TKMovesetHeaderBlocks`)

| # | Block | Contents |
|---:|---|---|
| 0 | movesetInfoBlock | `MovesetInfo` prefix (336 bytes up to `table`): init flag, 4 string offsets, 56+56 move-id aliases, 36 unknown values |
| 1 | tableBlock | `MovesetTable` (304 bytes): 19 × (uint64 offset, uint64 count) |
| 2 | motalistsBlock | `MotaList`: 13 × uint64 offsets into the mota block (`-1` = not extracted) |
| 3 | nameBlock | move + animation name strings (NUL-terminated, packed) |
| 4 | movesetBlock | all structure lists below, contiguous |
| 5 | animationBlock | concatenated animations (custom-built by extractor) |
| 6 | motaBlock | concatenated MOTA animation files |
| 7 | movelistBlock | `.mvl` displayable movelist for training mode |

### The moveset block and the table (T7)

`MovesetTable` offsets are **relative to the start of the moveset block**
(the extractor subtracts the first list's game address from every entry).
Entries, in declaration order, with struct sizes from `Structs_t7.h`:

`reactions`(112), `requirement`(8), `hitCondition`(24), `projectile`(168),
`pushback`(16), `pushbackExtradata`(2), `cancel`(40), `groupCancel`(40),
`cancelExtradata`(4), `extraMoveProperty`(12), `moveBeginningProp`(16),
`moveEndingProp`(16), **`move`(176)**, `voiceclip`(4), `inputSequence`(16),
`input`(8), `unknownParryRelated`(4), `cameraData`(12), `throwCameras`(16).

**Pointer semantics in files (critical):** before writing, the extractor
converts every in-structure pointer with `TO_INDEX` — the stored value is a
**list index** (`(addr - list_start) / sizeof(struct)`), or `-1` for null.
Two fields are exceptions in `Move`:

* `name_addr` / `anim_name_addr` → **byte offsets into the name block**
  (relative to the name block's extraction start, game address
  `movesetAddr + 0x2E5`; `ExtractorT7::CopyNameBlock`).
* `anim_addr` → **byte offset into the animation block**.

`MovesetInfo`'s four string pointers stay offsets relative to the in-game
moveset base; the decoder resolves them through the name block base above
and validates that the result is printable text.

### StructsT7::Move (176 bytes) — fields the decoder emits

| Offset | Field | Meaning |
|---:|---|---|
| 0 | `name_addr` | → name block offset (move name) |
| 8 | `anim_name_addr` | → name block offset (animation name) |
| 16 | `anim_addr` | → animation block offset |
| 24 | `vuln` | vulnerability flags |
| 28 | `hitlevel` | hit level bitfield |
| 32 | `cancel_addr` | → index into `cancel` list |
| 84 | `transition` | transition target |
| 88 / 90 | `moveId_val1` / `moveId_val2` | move-id / character-id related |
| 96 | `hit_condition_addr` | → index into `hitCondition` list (**damage lives there**) |
| 104 | `anim_len` | animation length, frames |
| 108 / 112 / 116 | `airborne_start` / `airborne_end` / `ground_fall` | |
| 120 | `voicelip_addr` | → index into `voiceclip` list (name as in header) |
| 128 | `extra_move_property_addr` | → index into `extraMoveProperty` |
| 156 | `hitbox_location` | hitbox id/location |
| 160 | `first_active_frame` | first active frame (startup = this value) |
| 164 | `last_active_frame` | last active frame |
| 170 | `distance` | |

`HitCondition` (24 bytes): `requirement` index @0, **`damage` @8**,
`_0xC_int` @12, `reactions` index @16.
`Requirement` (8 bytes): `condition` @0, param @4 (union: unsigned /
signed / float views all emitted).
`Cancel` (40), `Reactions` (112: 7 pushback indexes, 6 directions,
16 reaction move-ids), `Pushback` (16), `Projectile` (168),
`ExtraMoveProperty` (12), `OtherMoveProperty` (16), `InputSequence` (16),
`Input` (8), `Voiceclip` (4), `CameraData` (12), `ThrowCamera` (16) are
all laid out in `tkm2_decode.py` next to their format strings, each citing
the header field order.

## Which games / layouts this covers

* **Container (header, properties, block list): all gameIds** — T7, T8,
  TTT2, TREV, T6, T5 — because every extractor writes the same
  `TKMovesetHeader`.
* **Full inner decode: Tekken 7 only** (`gameId 0`, `Structs_t7.h`),
  including T7 files converted from T5/T5DR/T6/TTT2/TREV by TKMovesets'
  own converters (those are written in T7 layout with a `minorVersion`
  marking the source game).
* T8 / TTT2 / T6 / T5 native extractions use their own struct headers
  (`Structs_t8.h`, `Structs_ttt2.h`, `Structs_t6.h`, `Structs_t5.h`,
  plus `Structs_t5dr.h` including `Structs_t5.h`). The decoder emits the
  container decode for them and stops with an explicit message — adding a
  game = adding its table entry sizes + `Move` layout next to the T7 one.

## How the teardown lanes should use it

1. Extract with TKMovesets2 on a Windows/game machine into
   `extracted_chars/*.tkmvst` (uncompressed, or note the compression).
2. Copy the `.tkmvst` into the lane's teardown folder (it is a derived
   extraction artifact; keep the filename — it encodes the character).
3. Run `tkm2_decode.py` → JSON. Per move you get name, animation name,
   startup (`first_active_frame`), active window, `anim_len`, damage
   (resolved through `hitCondition`), hitbox location, hit level, cancel
   index. Feed `moves[]` into the Western Heart moveset pipeline; resolve
   cancels/requirements by index into the emitted lists when a lane needs
   full transition graphs.
4. Sanity gates before trusting a decode: header `ValidateHeader` passes
   (decoder enforces it), move names decode as clean text, frame values
   in plausible ranges (startup roughly 5–60, damage 0–~120 for T7).

## Proof / validation status

No real `.tkmvst` sample exists anywhere on this machine — see
`sample/README.md` for the full search evidence. The decoder is therefore
validated by **spec round-trip**: `make_validation_sample.py` builds a
minimal TKM2 file directly from the headers above (independent offset
tables, fictional character/moves), and `tkm2_decode.py` reproduces every
field field-for-field (62/62 checks, run 2026-10-20). Artifacts:
`sample/spec_validation_sample.tkmvst`, `sample/ground_truth.json`,
`sample/decoded.json`. **This is a spec-built validation fixture, not a
game extraction** — the first real `.tkmvst` a lane produces should be
decoded and diffed against the TKMovesets2 editor as the next proof step.

## Limits (honest)

* No real-sample decode yet (above). Struct layouts are taken from the
  vendored headers exactly, but a real extraction may exercise fields /
  variants the fixture does not (e.g. non-empty mota/movelist blocks —
  the decoder currently reports their sizes, not their contents).
* Compressed files: header decodes; payload does not. LZ4 is not in the
  Python stdlib, and the LZMA raw payload layout needs a real compressed
  sample to verify against rather than guess. Extract uncompressed for
  lane work until then.
* Inner decode is T7-layout only (above).
* `.mvl` movelist block and MOTA animation contents are not parsed.
* CRC32 is reported, not re-verified (padding ambiguity, above); for
  files whose block sizes are all 8-aligned (like the fixture) it can be
  re-computed exactly with `zlib.crc32` over the hashed block set.
