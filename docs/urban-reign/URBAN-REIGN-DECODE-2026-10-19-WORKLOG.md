# Urban Reign Character Model Decode — WORKLOG (2026-10-19)

**Owner order:** "Get all that decoding cracked and everything else." (2026-10-19 ~03:18 CDT)
**Lane:** ur-decode (re-dispatch after daemon restart killed 7df1efd0)

## What was accomplished

### 1. PS2 executable surgically extracted from ISO
- **SLUS_212.09** (6,366,044 bytes, MIPS ELF) downloaded from GitHub release
  `urban-reign-iso-v1` via HTTP Range requests (no 4GB download needed).
- Method: parsed ISO9660 PVD → root directory → file extent LBA 878039 →
  absolute byte 0x6b2eb800. Script: `extract_elf.py`.
- Binary contains debug strings (`../../prog/game/kg_human.cpp`,
  `kg_objdata.cpp`, etc.) — the "kg" engine character/mesh loading code.
- **This is the key enabler for Ghidra analysis** (not installed in this VM).

### 2. Mesh topology CRACKED: non-indexed triangle list
- **Duplicate vertices prove per-face storage.** In char001, verts 2 and 3
  are byte-identical (same position, weights, UV) — the same vertex stored
  twice because it's shared by two triangles.
- **NO index buffer needed.** Every 3 consecutive vertices = 1 triangle.
- This resolves open item #3 from PPK-GEOMETRY.md ("Index/topology").

### 3. 024_BONES is facial bones only (negative result)
- File `tec/demo/facial/yarare/024_BONES` (744 bytes) extracted from ISO.
- Contains 13 bones (44-byte records), but it's from the **facial** directory
  ("yarare" = damage reaction) — facial animation bones, NOT the body skeleton.
- Body skeleton bind matrices remain unfound.

### 4. ae00 chunk structure mapped
- Contains bone index arrays: `01 03 <count> 00` + count bytes of bone indices.
- char001: 27-index palette [1,8,9,43,10,11,44,45,4,5,6,7,46,47,48,2,3,49,50,
  12,17,51,13,52,53,54,0] (max bone 54).
- Also has `ff`-separated bone groups and u32 tables mirroring header words.
- Full structure decode still open.

### 5. .gyu motion files surveyed
- Headers: (motion_count, 21, 0, 1×20, 0, 135, 0, offset_table...).
- general_30frame.gyu: 373 motions, 20 track offsets. general_normal.gyu: 342.
- Track data is compressed/quantized (not plain floats). No bone names
  (ASCII strings are float-byte false positives, same as before).
- "21" may be bone count, but 20 track offsets found in debug file.

## What's still blocked

1. **Body skeleton bind matrices** — not in char PPKs, not in .gyu headers,
   024_BONES is facial only. Needed to transform bone-local verts to model space.
2. **Per-vertex bone index mapping** — ae00 has the data but the exact
   vertex→bone assignment formula is not yet reverse-engineered.
3. **Full mesh assembly** — blocked on (1) and (2).

## Next steps (for future lane)
1. Install Ghidra, load SLUS_212.09, find `kg_human.cpp`/`kg_objdata.cpp`
   character loading functions (search for chunk types 0x8001/0xae00 or
   the 128.0f vertex separator constant 0x43000000).
2. The vertex parsing code will reveal the bone index mapping and matrix layout.
3. Alternatively: empirical approach — cluster rigid verts by ae00 bone
   palettes and solve for bone transforms via the 2-influence constraints.

## Files
- `extract_elf.py` — surgical ISO range-request extraction script
- `SLUS_212.09` — PS2 executable (6.3MB, MIPS ELF) [not in PR, use script]
- `024_BONES` — facial skeleton file (744 bytes)
- Analysis notes in this worklog
