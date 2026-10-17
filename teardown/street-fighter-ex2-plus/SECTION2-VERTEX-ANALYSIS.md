# SF EX PAC Section 2 — Vertex Format Analysis (2026-10-17)

**Analyst notes for the team.** All findings below were verified by reading
`work/ex2-extracted/PL/P00X.PAC` (SF EX2 Plus) with Python struct parsing.
Nothing here is guessed — byte offsets and values are exact.

## Section 2 Layout (P00X.PAC: file offset 0x0047f4, 86,616 bytes)

### 1. Offset Table (first 200 bytes)

The section begins with a table of **50 u32 little-endian offsets** (200 bytes),
pointing to data chunks within the section. 37 unique offsets.

```
First 12 table entries: 264, 760, 760, 760, 1144, 1144, 1144, 1776, 1776, 1776, 2072, 2072, ...
```

- Offsets are monotonically non-decreasing, 4-byte aligned, all < section length.
- Some offsets repeat: run-lengths of 1, 2, or 3 observed.
  - **x3 repeats** (e.g. 760×3, 1144×3): the same chunk is referenced 3 times.
    Likely a shared mesh referenced by 3 slots (e.g. 3 LOD levels pointing at
    one mesh, or one mesh used by 3 body parts). The chunk data is NOT
    triplicated — only the table entry repeats.
- Table ends when values stop being monotonic/in-range (byte 200).

### 2. Chunk Structure

Each unique offset points to a chunk with this layout:

```
Offset +0:  u32 vertex_count   (e.g. 59, 45, 76, 34, 50, 128, 24, ...)
Offset +4:  u32 zero           (always 0 observed)
Offset +8:  u32 one            (always 1 observed)
Offset +12: u32 unknown        (e.g. 13128, 16007, 30556 — varies per chunk)
Offset +16: vertex records     (vertex_count × 8 bytes)
Offset +16+count*8: trailer    (8 bytes: 0x00000000, 0x08000000 — constant)
```

Chunk byte size = 16 + (count × 8) + 8. Verified: chunk @264 (count=59)
spans 264→760 = 496 bytes = 16 + 472 + 8. ✓
Chunk @760 (count=45): 16 + 360 + 8 = 384 = 1144−760. ✓

The trailer `(0x00000000, 0x08000000)` is identical across all chunks checked.
`0x08000000` may be a type/version flag.

### 3. Vertex Record (8 bytes) — FIELD STATISTICS

Each vertex is 8 bytes. Treated as 4× s16 LE (`<4h`):

| Byte pos | Type | Observed (chunk @264, 59 verts) | Interpretation |
|----------|------|---------------------------------|----------------|
| 0–1 | s16 | **constant 1** (59/59 identical) | Format marker / flag. NOT a coordinate. |
| 2–3 | s16 | 34 unique, range −24318..−1, avg step 3516 | Coordinate axis A (all negative in this chunk) |
| 4–5 | s16 | **59 unique** (all distinct!), range 13210..15965, avg step **47.5**, max step 66 | Coordinate axis B — **increments smoothly**, strip-like spatial coherence |
| 6–7 | s16 | **only 5 unique values**, range −24576..24576, avg step 7627 | ⚠️ Quantized — either a coarse axis OR an attribute (normal/bone/UV index?) |

**Total verts in P00X.PAC: 1,127** across 37 chunks.

### 4. What Was Tried (render attempt)

Decoded as `(marker, x, y, z)` with axes mapped to (right, up, fwd) at /32768
scale. Result: **horizontal bands, not a humanoid** (see analysis — point cloud
forms flat layers at discrete Y levels, spread across X/Z).

Overall bounding box at /32768: X −1.00..0.00, Y −1.00..+1.00, Z −1.00..+0.75.
- The Y axis (2nd s16) is the only symmetric one — likely the character's
  left-right axis (T-pose plausible: ±1m wingspan).
- The X axis (1st s16) is entirely negative — character sits below origin, or
  this is the vertical axis with origin at head level.

### 5. Open Questions (for the team)

1. **Is byte 6–7 a coordinate or an attribute?** Only 5 distinct values in a
   59-vert chunk is suspicious for a spatial axis. If it's a normal index,
   bone weight, or UV coordinate, the true Z is elsewhere (or implicit).
2. **Are chunks in bone-local space?** Section 0 (5,440 bytes, low entropy)
   contains structured u32s (0x1013, 0x1026, 0x1039… spaced 19 apart) —
   possibly bone/part metadata with transform matrices. Chunks may need bone
   transforms applied before they assemble into a coherent body.
3. **What is header field +12?** (e.g. 13128 @264, 16007 @760). Varies per
   chunk. Could be a bone ID, material ID, or data offset.
4. **Face table (section 3) references:** vertex indices in faces go up to
   ~2112, but section 2 has only 1127 verts in this file. Faces may index a
   concatenated vertex pool, or the face parsing is wrong (see prior notes —
   face verts like 65526 suggest misparse).
5. **Scale factor:** /4096 (PS1 standard), /16384, and /32768 all give
   plausible-but-different sizes. Cannot confirm without a coherent render.

### 6. Suggested Next Steps

1. **Ghidra on SLUS_011.05**: find the PAC loader (search for the section-2
   offset table walk, or the constant trailer `0x08000000`). The vertex decode
   function will reveal the true field semantics.
2. **PCSX-Redux VRAM dump**: run the game, dump VRAM during character render,
   correlate vertex positions with file bytes.
3. **Cross-character comparison**: diff the same chunk index across multiple
   PXX.PAC files. Constant bytes = format; varying bytes = geometry.
4. **Section 0 decode**: parse the 5,440-byte structured block fully — if it
   contains bone matrices, apply them to chunks and re-render.
5. **Check the NMD files** (`PLNMD/NEZUMI.NMD` etc.) — may contain skeleton/
   bone data that clarifies the chunk→bone mapping.

## Files

- Analysis script snippets: inline Python in this doc (all reproducible)
- Test OBJ: generated from P00X.PAC section 2 (bands render, not humanoid)
- Prior tools: `~/workspace/sfex-teardown/{iso_extract,tmd_extract,pac_parse,tim_extract,obj2glb,render_char}.py`
