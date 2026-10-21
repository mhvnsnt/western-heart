# DOA4 Phase 5 — Blend-Index Source Hunt (INTERIM, landed early)

Recovery lane for predecessor a9bdf298 (killed by daemon restart ~50 min in,
zero pushes). This document is landed EARLY with the first hard findings and
will be updated in place as the lane progresses. Branch:
`feat/doa4-phase5-blendidx-batch-20261021` (off PR #427's
`feat/doa4-phase4-geodecl-assembly-20261021`). All analysis scripts in
`tools/phase5/`, run against chrone pkg00 (`p4/chrone_head.bin` +
`p4/chrone_mid.bin` = package span [0, 0x1000000), graph from PR #402).

## 1. ObjGeo item record (0x140) — FULLY DUMPED. NO blend indices there.

Job 1 step 1 executed (`tools/phase5/itemfull.py`, `itemfull2.py`,
`itemsize.py`): all 150 ObjGeo items in chrone pkg00 dumped across the full
record. Item record size varies by stream: 0x100 (stream 1), 0x140 (stream 2),
0x190 (stream 3). Per-u32-offset census across all items, split blend-object
vs non-blend-object:

- The ONLY offsets whose value sets differ between blend and non-blend items
  are `+0x10` / `+0x14` (index/vertex counts — expected, not indices).
- `+0x00` = object-local id (0..13), `+0x18` = stream (1..3), `+0x1c` ∈
  {192, 208}, `+0x80..0x88` = 1.0f constants, `+0xa0..0xa8` = float bounds,
  `+0x0c8` is the only other blend-touching offset (values {10, 15} appear
  only in blend items) — a small count/flag, not an index array.
- The stream-3 extra region `+0x140..0x190` is near-zero padding carrying
  three small counters (2, 6, and a per-item ordinal 21/23/27/29...) in both
  blend and non-blend items identically. Not bone data.

**Verdict: the ObjGeo item record carries NO blend-index source.**

## 2. No hidden index stream after blend vertex segments; no per-vertex
## index array among VBUF descriptors.

- `tools/phase5/gaps.py`: in the set-B decl-order segment walk, the gap after
  nearly every BLEND decl is exactly 0 (segments are tightly packed) — there
  is no companion index stream parked after blend vertex data.
- `tools/phase5/vbufcensus.py`: 96 VBUF descriptors; 59 match a decl's
  `vtx*stride+2` exactly. NONE of the 37 unmatched descriptor sizes equals
  `blend_vtx * {1,2,4,8} + 2` for any blend decl's vertex count — no
  per-vertex byte/short index buffer exists in the package descriptor table.

## 3. THE PALETTE: bone indices live in ObjInfo, not in the geometry streams.

`tools/phase5/palette.py` + `objinfo2.py` — the per-object ObjInfo block
carries, at fixed offsets:

- `+0x3c` (u32): palette size. **0 for every non-blend object; 2 or 3 for
  every blend object — exactly equal to that object's BLENDWEIGHT column
  count** (verified across all 46 objects; blend objects =
  {2,3,4,7,10,11,14,15,16,17,18,21,24,25,28,29}).
- `+0x90`: u16 array of that many Hie node indices — the object's bone
  palette. Examples: obj2 = [6, 12], obj4 = [7, 13, 4], obj7 = [8, 13],
  obj11 = [9, 1], obj16 = [20, 26], obj18 = [21, 27, 18].

This is the classic DOA per-object palette design: vertex streams carry only
weights (2–3 columns); the palette slot k for every vertex of the object is
palette[k]. It explains G3's phase-4 result (BLENDWEIGHT in 20/68 decls,
BLENDINDICES in 0/68) completely: there are no per-vertex indices to find.

Geometric cross-checks (`weightgeo.py`, `idxspace.py`, `chain2.py`):
pure-weight (w>0.98) vertex clusters were compared against Hie joint world
positions under (a) direct palette mapping and (b) the Hie links-ring
ordering. Direct mapping is exact for the large torso decls (decl5 slot0 →
node 13 min-vert-dist 0.017; decl23 slot0 → node 27, 0.017; decl9/27 slot1 →
0.154 = closest joint). Some small/rigid decls are ambiguous under both
mappings (duplicate joint positions at origin; mirrored-pair decls 16/34) —
the discriminating proof is the pose test below, not centroid metrics.

## 4. G3 standing (honest, interim)

BLENDWEIGHT verified real (phase 4). Blend-index SOURCE identified with
structural proof: **ObjInfo palette (+0x3c count, +0x90 u16 node array),
count == weight columns for every object, zero for every non-blend object.**
G3 is NOT yet called passed: the acceptance proof is the pose test (weights +
palette applied to chrone pkg00, one Hie joint bent, rendered, viewed).
Pose test: IN PROGRESS (numeric harness `tools/phase5/posetest.py` written;
Blender render proof to follow in the next update of this doc).

## 5. Remaining jobs

- Job 1: pose-test render (direct palette), viewed. XEX skinning-consumer
  cross-check in Ghidra if the render is ambiguous.
- Job 2: batch assembly (remaining chrone packages + chrtwo) via
  `tools/doa4_assemble2.py`, coverage-based pairing, per-character quality
  table, ≥4 viewed front renders.
- Job 3 (stretch): TX2D → PNG → textured chrone pkg00 GLB → viewed render.
  Package carries 42 TX2D descriptors (vbufcensus count).
