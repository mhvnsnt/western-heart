# Soulcalibur II (Xbox) — VMX v2 / v3 Stage Layouts (Phase 14, JOB 1)

The two phase-13 stage exceptions are resolved from the file bytes
themselves, cross-checked against the proven fighter decoder
(`vmx_decode_v2.py`, phases 3–4, whose part-record classes are the
same). Every claim below was measured, not inferred: stream tiling,
unit-normal walks, size accounting, and byte-identity checks all ran
on the real `m000.bin` / `m120.bin` from the v404 archive. Tool:
`tools/build_stage2.py`. The XBE loader read the phase-13 report
named was not needed in the end: the on-disk layout is fully
self-describing once the v2 record size is recognised, and every
extent is verified by exact tiling (below). No guessed geometry.

## VMX v2 (m000) — 36-byte part records, node-shared streams

Header (offsets from `VMX.`): part counts u16 @+0x0C/+0x0E/+0x10
(196/69/0), part-array bases u32 @+0x2C/+0x30/+0x34, node count u16
@+0x0A (58), node array u32 @+0x24 (400 B records, matrix f32x16
@+0x10, same as fighters), rec80 base u32 @+0x1C (87 records),
VXT u32 @+0x18.

Part record (36 B, 9 dwords):

| Off | Field | Evidence |
|---|---|---|
| +0x00 | type (0 = rigid, 4 = skinned-pool class) | same class byte as fighter parts (`vmx_decode_v2`: w0 byte0 == 4 ⇒ skinned) |
| +0x04 | index count | index reads at +0x10 stay in-file, maxidx < stream verts for all 265 parts |
| +0x08 | node pointer | 58 distinct values, exactly the node array (base + k·400) |
| +0x0C | rec80 material pointer | (ptr − rec80 base) divisible by 80, in range, for 265/265 parts |
| +0x10 | index stream pointer | 265 distinct values |
| +0x14 | vertex stream base | 58 distinct values = one per node (1:1 with +0x08) |
| +0x18/+0x1C/+0x20 | extra stream pointers (type 4 only; 0 otherwise) | see type-4 layout |

Type 0 (262 parts): interleaved 40 B vertex stream at +0x14
(pos f32x3 @+0, normal @+12, color u32 @+24, uv f32x2 @+28 — the
stage/fighter rigid format). Streams are SHARED by every part of a
node. Stream vertex count = max(maxidx)+1 over its parts. Tiling
proof: sorting all stream bases + index pointers + VXT base, every
stream's block span is exactly `nv·40` or `nv·40+8` (the +8 is a
trailer: vertex data starts AT the base — unit-normal fraction 1.000
at base vs ≈0 at base+8, measured on every +8 stream). Parts are
PLACED by their node matrix (row-vector convention of
`vmx_decode_v2`: p' = p·R + T, normals rotated only) with translation
scale ×1.0 (stage units): under ×1.0 the 88-vertex colonnade streams
(nodes 46–57) tile at x=±13, z ∈ {−5.8,−3,0,3,5.8} with piece-sized
spacing; under the fighter ×0.1 convention they would collapse into
each other at the origin. 23/58 nodes carry non-identity matrices;
the rest are identity (the large world streams, incl. the node-10
environment shell).

Type 4 (3 parts, g0p121–123, node 28): the fighter skinned-pool
layout in stage form — color+UV stream at +0x14 (12 B/vert: u32
color — all 0xFFFFFFFF here — then f32x2 uv, all in [0,1]) and
pos+normal stream at +0x18 (32 B/vert: pos f32x3 @+0, 1.0,
normal f32x3 @+16, 1.0; normals 156/156 unit). +0x1C and +0x20 point
at two further copies of the pos+normal stream; all three copies are
byte-identical (sha256-checked over the full 156×32 B). Vertex count
156; the three parts' index ranges partition it (0–51, 52–103,
104–155). Node 28's matrix is identity, so no placement question
arises. (The 28 B record at header +0x38 also lists these pool
pointers — corroborating, not needed.)

VXT v1 (m000): header version byte 1, texture count u16 @+0x08 (86),
record pointer u32 @+0x0C (=0x14). Records are 32 B:

| Off | Field |
|---|---|
| +0x00 | palette-struct pointer or 0 (struct = {data ptr, count, ?}, same as v2) |
| +0x04 | common dword (0x241b/0x251b) |
| +0x08 | flags (0xa0+mips for multi-level records in the sample) |
| +0x0C | pixel-data offset, VXT-relative |
| +0x10 | Xbox D3DFORMAT (11 P8 / 12 DXT1 / 14 DXT3 / 15 DXT5) |
| +0x14 | width, height (u16 pair) |
| +0x18 | mip levels present (1–5) |

Size accounting: all 86 records' data offsets tile exactly by full
mip-chain sizes (level sizes as in `VXT-FORMAT.md`; P8 = w·h per
level). Pixel storage rules are unchanged (DXT linear, P8
Xbox-swizzled + BGRA palette — the single P8 record decodes through
the proven `decode_texture`). Material chain unchanged
(part +0x0C → rec80 → +0x08 primary VXT record), record stride 32:
84 of 87 materials carry valid texture pointers, 84 distinct
textures used.

Result (m000): 265/265 parts assembled, 0 skipped; 40,065 unique
stream verts (505,744 verts as stored in the GLB, where shared
streams are emitted per part, as the v4 builder emitted per-part
streams); 18,959 tris; 84 embedded images; topology strip 102 /
list 163 (per-part normal-agreement winners, recorded by the tool).
Proof (viewed): `phase14-proof/stage-m000-arena.png` (lit) and
`stage-m000-arena-flat.png` (unlit emission) — marble floor, white
temple facade with gold gable, teal pillars, colonnades and side
shrines coherent and textured; `stage-m000-plan.png` is the
outside-of-shell plan (the stage is enclosed by its node-10
environment shell, so the plan shows the shell's outer facets).
The shell's large facets are source geometry: its color-only parts
carry white/gray/sky-blue vertex colors (0xffffffff dominant,
0xff99bfe5 sky) and render dark only where the single proof sun
faces away — the game's own lighting/fog is not part of a GLB dump.

## VMX v3 (m120) — sentinel-terminated single part

Standard 40 B part record (one part, group 0): icnt 984, node ptr =
node 0 (identity matrix), material = rec80[0] (color-only: all
texture pointers 0), index stream @0x47a0, vertex stream @0x8f0,
vend field (+0x24) = 0xFFFFFFFF sentinel. Vertex count =
maxidx+1 = 401; verified (iptr − vptr) = 401·40 + 8 (same +8
trailer as v2; data at vptr — unit normals 11/11 sampled at skip 0,
0/11 at skip 8). VXT section present but holds 0 texture records;
the part's vertex colors are uniformly 0xffffffff.

Result (m120): 1/1 part assembled: 401 verts, 760 tris (strip,
measured), 0 images (source has no textures for it). The geometry
is a unit sphere (all positions in [−1,1]³, radius ≈ 1) — a bare
white ball as stored in the archive; no stage dressing exists in
this entry's bytes. Proof (viewed): `phase14-proof/stage-m120-plan.png`
(smooth disc from above) and `stage-m120-arena.png` (the sphere at
the arena camera, small in frame at unit scale).
