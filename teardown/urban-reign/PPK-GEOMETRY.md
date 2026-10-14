# URBAN REIGN — PPK Character Geometry Decode (work in progress)

Source: `ppks/chars/char001.ppk` (776,960 bytes). Tool: `tools/ur_extract_meshes.py`.

## PROVEN

### 1. Header tag table (offset 0x20)
Null-terminated list of u32 entries, each `(type << 16) | offset` (offsets are
file-relative). char001's table (terminator at 0x58):

| Type | Offset | Content |
|------|--------|---------|
| 0x8001 | 0x2971 | 344KB s16-dense region (NOT plain positions — see §4) |
| 0xa000 | 0x0a4f | zeros (padding) |
| 0xae00 | 0x017d | byte/integer patterns (bone indices?) |
| 0x0000 | 0x013f | tiny ints |
| 0x6502 | 0x0000 | — |
| 0x4d5c | 0x0008 | — |
| 0x0865 | 0x8001 | — |
| 0x0002 | 0xe800 | float pre-header (128.0 quads, small floats) |
| 0x0154 | 0xc500 | float pre-header + `0x00008004` marker |
| 0x0008 | 0x6880 | float pre-header + `0x00008014` marker |
| 0x0001 | 0xe6d8 | mixed int/float |
| 0x8001 | 0x8b78 | float region (1.0, 0, 128.0×4, small floats) |
| 0xa800 | 0x0bcd | zeros |
| 0x0000 | 0x000c | — |

Table layout varies per character (char002/char003 have different entries) —
it is per-file, not a fixed template.

### 2. Bind pose — identity quaternions at ~0x660
`(0,0,0,1)` repeated — bone bind-pose rotations.

### 3. Normal vectors — float32 xyz, stride 12, EXACT unit length
Found runs (char001): 68 verts @0x362e4, 70 @0x36de4, 50 @0x377d4,
70 @0x38384, 56 @0x38eb4. Every triplet has length exactly 1.000.
Positions should pair 1:1 with these — same counts should appear in the
position decode when found.

### 4. Bone-name strings
863 ASCII strings in char001, e.g. near 0x86500:
`MOM_DM_O__L_prot05x5` / `MOM_DM_O__R_prot05x5` — left/right bone pairs
(`__L_` / `__R_` markers).

### 5. Mesh pre-headers
Float chunks with `0x00008004` / `0x00008014` markers and `128.0` quads,
e.g. before 0x2971 (0x2900–0x2970) and at 0xc500 / 0x6880 / 0xe800.

## NEGATIVE RESULTS (documented so the next pass doesn't redo them)

- **Non-normal xyz float runs are NOT vertex positions.** They are mostly
  denormal/zero floats (integer data misread as float) — e.g. 707 triplets
  @0x96ad0 collapse to a handful of distinct values; XY projections show
  sparse dots, not surfaces.
- **The 0x2971 s16 region (344KB) is not plain s16 positions** at any stride
  3–16: no spatial coherence (median consecutive hop ~8m at /4096 scale),
  bbox always full ±32768. Byte entropy 5.99 bits/byte (structured, not
  encrypted) with 0x00 the dominant byte (27.7%). Packing TBD —
  candidates: delta-coded, interleaved heterogeneous fields, or non-geometry
  data entirely.
- **Index buffers not yet located.** u16 scans find only float-aliasing
  false positives (low 16 bits of float data).

## STILL OPEN

1. Vertex position decode (location + packing + scale).
2. Index buffers (topology).
3. UVs, textures, material assignment.
4. Mesh ↔ bone assembly (skinning).
5. Per-fighter organization into `urban-reign/models/<fighter>/`.

## Next steps
- Pair with the proven normal runs: find same-count (68/70/50/70/56)
  position runs nearby.
- Attack the 0x2971 region as delta-coded or record-structured s16.
- Cross-check char002/char003: same structure at shifted offsets confirms
  the format vs per-character quirks.
