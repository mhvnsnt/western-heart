# DOA4 IBUF Index Buffer — DECODED

**Date:** 2026-10-18
**Lane:** 6 (Gap-filling)
**Status:** DECODED — triangulated meshes produced

## Summary

The DOA4 "IBUF" index buffers are **fully decoded**. The 105 vertex point clouds can now be triangulated into usable meshes. 30/30 chrone.afs character models decoded and verified (0 degenerate triangles).

## Format

### XPR2 Resource Table
Each AFS archive contains XPR2 resource tables. Each table is an array of 16-byte records:
```
[0:4]   magic  "XPR2", "USER", "TX2D", "VBUF", "IBUF"
[4:8]   f1     (see below)
[8:12]  f2
[12:16] f3
```

### VBUF Records (Vertex Buffers)
- **f1** = ABSOLUTE file offset of vertex data
- **f2** = stride (20 bytes)
- **f3** = vertex count (hint; actual pool may be larger)

Vertex format (20 bytes, big-endian):
```
[0:12]  float3  Position (x, y, z)
[12:20] float2  UV (u, v)
```

### IBUF Records (Index Buffers) — THE BREAKTHROUGH
- **f1** = TABLE-RELATIVE offset to a 20-byte **descriptor** (NOT direct data offset!)

Descriptor (20 bytes, big-endian):
```
[0:4]   flags  0xFFFF0000
[4:8]   addr   GPU address (low 2 bits are flags)
[8:12]  size   Byte size of index buffer
[12:16] type   0x20001 (index buffer)
[16:20] 0
```

**File offset = (addr & ~3) - IBUF_BASE**, where IBUF_BASE is per-table (not per-file!).

Index data format:
- **u16** triangle strips
- **0xFFFF** = strip restart primitive
- Convert strips to triangle lists (alternating winding)

### IBUF_BASE Discovery
The base varies per XPR2 table. Discovered values:
- chrone.afs: 0x8c2000, 0x8da000, 0x502000, 0x6b0000, 0x721000, 0x981000, 0xe1e000, 0xe60000, 0xf52000, 0xecb000, 0x567000, 0x83e000, 0x8ae000, 0x299000, 0x2c9000, 0x3df000, 0x4b0000, 0x2f8000, 0x402000, 0x53f000, 0xa56000, 0xf24000, 0xc8f000, 0x57b000, 0x10ad000, 0xb68000, 0xc33000, 0x31f000, ...
- mot.afs: 0x5e0000
- chrtwo.afs: 0x57000
- chrthree.afs: 0xe73000

**Auto-discovery method:** Search file for u16 strip pattern `(0,1,2,1,3)` or `(0,1,2,3,4,5)`, verify `size` bytes are valid indices (<6000 or 0xFFFF), compute `base = addr - found_offset`.

## Decoder
`tools/doa4_decode.py` — Full decoder with auto base discovery.
- `decode_table(afs_path, table_offset, ibuf_base)` → {verts, uvs, tris}
- `write_glb(verts, uvs, tris, path)` → triangulated GLB
- `batch_all.py` — Batch process all tables in an AFS.

## Assets Produced
`models/triangulated/chrone/` — 30 triangulated character models from chrone.afs:
- 7,861–16,845 verts, 11,228–22,934 tris per model
- 0 degenerate triangles (verified)
- Total: 11MB

## What This Unblocks
- **Fighter-integration lane:** Can now use triangulated DOA4 character meshes (instead of point clouds).
- **Moveset-wiring lane:** Mesh topology available for skinning/retargeting.

## Remaining Work
- chrtwo.afs (25 models), chrthree.afs (39 models), mot.afs (2 models): Same decoder applies, need batch runs.
- stg.afs (18 stage models): IBUF base not yet discovered (file is 777MB, scan is slow).
- anm.afs (animations): Format still unknown. No VBUF/IBUF markers. Needs separate RE.
- Vertex normals: Not in vertex data; compute from triangles (or find in separate stream).
- Skeletons/bone weights: In MdlGeo ObjGeo chunks (not yet parsed).
- Tekken 6 PSP DATA401: Still blocked (needs ISO re-download, owner action).

## Key Insights
1. The "IBUF" XPR2 records do NOT point directly to index data — they point to descriptors.
2. The descriptor `addr` is a GPU address, not a file offset. Subtract per-table base.
3. Index data is triangle strips with 0xFFFF restart, not indexed triangle lists.
4. Vertex pools may be larger than VBUF f3 suggests — size from max index.
5. The 0x20001 descriptor type was misidentified as "float data" — it's actually the index buffer descriptor; the float-like data at `addr` (without base subtraction) was a red herring.
