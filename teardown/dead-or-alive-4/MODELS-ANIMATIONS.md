# DOA4 Models & Animations — Carving Report

**Date:** 2026-10-17  
**Status:** PARTIAL — Vertex buffers extracted (105 models), index buffers NOT decoded

## Summary

Following the texture breakthrough (219 XPR2 textures carved), we extracted **105 vertex buffers** from the 6 "encrypted" AFS archives. The vertex data is plaintext and well-understood. The index buffer format remains undecoded, so meshes are currently point clouds, not triangulated surfaces.

## Extracted

| File | Models | Verts (range) | Notes |
|------|--------|---------------|-------|
| chrone.afs | 21 | 3,364–5,940 | Character models |
| chrtwo.afs | 25 | 3,284–5,668 | Character models |
| chrthree.afs | 39 | 3,284–5,940 | Character models |
| mot.afs | 2 | 4,020–5,428 | Motion-related models |
| stg.afs | 18 | 4,820–5,108 | Stage geometry |
| **Total** | **105** | | |

All saved as GLB point clouds in `carved_models/` with manifests.

## Vertex Format (DECODED)

**20 bytes per vertex, big-endian:**
```
[0:12]   float3  Position (x, y, z)
[12:20]  float2  UV coordinates (u, v)
```

- Positions are in [-1, 1] range (normalized or local space)
- UVs in [0, 1] range
- No normals in vertex data (computed or stored separately)

## Resource Table Structure (DECODED)

Each model package has a resource directory starting with `XPR2`:

```
Offset  Type   Description
------  -----  -----------
0x00    XPR2   Texture package header
...     USER   Texture sub-resources (4 per package)
...     TX2D   2D texture entries
...     VBUF   Vertex buffer entries
...     IBUF   Index buffer entries
```

**Record format (16 bytes, big-endian):**
```
[0:4]   char[4]  Magic ("XPR2", "USER", "TX2D", "VBUF", "IBUF")
[4:8]   uint32   Field1 (see below)
[8:12]  uint32   Field2 (see below)  
[12:16] uint32   Field3 (see below)
```

**VBUF record:**
- Field1: Byte offset of vertex data in file
- Field2: Vertex stride (always 20)
- Field3: Vertex count

**IBUF record:**
- Field1: ??? (does NOT point to valid index data)
- Field2: 20 (unknown meaning)
- Field3: ??? (matches VBUF count, but data not found)

## The IBUF Mystery (BLOCKED)

The index buffer records exist (2,404 in chrone.afs alone), but Field1 does not point to valid triangle index data. Investigations:

1. **Field1 as file offset:** Points into vertex data region, not indices. ❌
2. **As BE uint16 indices:** Values exceed vertex count, no triangle pattern. ❌
3. **As LE uint16 indices:** Same problem. ❌
4. **As BE uint32 indices:** Values are float bit patterns, not indices. ❌
5. **Data after vertex buffer:** More vertex data, not indices. ❌

**Hypotheses:**
- IBUF Field1 is a GPU virtual address (not file offset)
- Index data is stored in a separate section not yet located
- Indices use a compressed/packed format
- The "IBUF" records are actually something else (draw commands?)

**Next steps to decode:**
- Ghidra analysis of mesh rendering code in default_pe.bin
- Xenia emulator: breakpoint on DrawIndexed and dump index buffers from GPU memory
- Compare with Ninja Gaiden 2 (same engine) modding documentation

## Animation Data (NOT STARTED)

- `anm.afs` (2.9MB): No VBUF/IBUF/TX2D markers. Likely contains animation keyframes in a custom format. Header is encrypted; data may be plaintext after header.
- `mot.afs` (71MB): Contains VBUF/IBUF markers (435/219) — has embedded models, not just motions. The actual motion data format is unknown.

Animation decoding requires:
1. Decrypting anm.afs header to find file boundaries, OR
2. Carving animation data by pattern matching
3. Understanding Team Ninja's bone animation format (likely quaternion + position keyframes)

## Files

- **Extractor:** `tools/carve_models.py`
- **Models:** `carved_models/*/*.glb` (105 files)
- **Manifests:** `carved_models/*/*_manifest.json`
- **This doc:** `MODELS-ANIMATIONS.md`

## For Western Heart

The vertex buffers are a starting point but not yet usable as game assets:
- ✅ Vertex positions extracted (accurate)
- ✅ UV coordinates extracted (accurate)
- ❌ Triangle topology (indices) — BLOCKED on IBUF decode
- ❌ Normals — not in vertex data, need computation or separate source
- ❌ Skeletons/bone weights — not yet located
- ❌ Animations — format unknown

**To make these game-ready:**
1. Decode IBUF to get triangles
2. Compute normals from triangulated mesh
3. Locate skeleton and skinning weights
4. Decode animations from anm.afs/mot.afs
