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

## 4. G3 — POSE TEST RUN, VIEWED: **PASS** (with two stated caveats)

Pose test executed (`tools/phase5/posetest_build.py`): chrone pkg00's 64
meshes rebuilt from the phase-4 segment walk; every blend decl skinned with
its file BLENDWEIGHT columns paired to its object's ObjInfo palette slots
(slot k → palette[k], a Hie node); one joint bent 40°; rendered in Blender
(Cycles, `p4/render.py` camera) and VIEWED by this lane:

- Bend node 14 about Z (`phase5-posetest-bend14z.png` vs
  `phase5-posetest-bind.png`): the character's image-right arm/sleeve
  cylinder + the gown region weighted to palette nodes {8, 12} swung up as
  one connected region with smooth blend falloff. Head, torso, opposite
  arm and the visible leg stayed exactly in place. Nothing exploded, no
  scattered patches — with a wrong/permuted palette, one joint bend would
  tear patches from all over the model.
- Bend node 28 about Z (`phase5-posetest-bend28z.png`): the MIRROR chain
  (28 → 22 → 18) swung the image-left arm/gown region — the exact
  opposite side, symmetric with the node-14 result. Numeric sweep
  (`tools/phase5/sweep.py`, all 46 nodes): displacement is always confined
  to decls whose palettes intersect the bent node's subtree, and the
  14/28 chains displace mirror-image decl sets (decl9/10/20 vs
  decl27/28/38) with near-identical counts.
- Cross-checks that predicted this: decl5 slot0 → node 13 min-vert-dist
  0.017 (closest joint); decl23 slot0 → node 27, 0.017; displaced-vertex
  counts under bends of nodes 11 and 13 are identical (2400/2404 verts —
  nodes 11/13 share a bind position, a duplicate-joint pair).

**G3 VERDICT: PASSED.** Weights (vertex streams) + bone indices (ObjInfo
palette) are both real, correctly paired, and produce coherent, localized,
symmetric deformation of the assembled character.

Caveats (honest, do not over-read the pass):
1. The test harness composes the bend as a pivot rotation about the bent
   joint applied per palette node in its subtree — it proves palette
   MEMBERSHIP and weight pairing. The game's full per-node matrix chain
   (bind-pose inverse composition) is not yet replicated; that is
   animation-pipeline work, not an index-source question.
2. The phase-3 graph's Hie world matrices are X-MIRRORED relative to
   vertex bind space (graph node 14's chain drives the image-right side;
   same mirror seen in the decl16/34 pure clusters). Poses will need the
   mirror accounted for when animation is wired.

## 5. Job 2 — BATCH ASSEMBLY (in progress)

Tooling: `tools/phase5/batch_build.py` — assemble2's exact decl/stride/
validate logic, with strip pairing generalized: this package family's IBUF
descriptor base is NOT portable across packages (chrone pkg01's descriptors
admit no subtractive base mapping onto strip starts — swept exhaustively,
`tools/phase5/ibufbase3.py`-style), so strips are paired by scanning
index-like pages directly with the phase-4 signal (full vertex coverage
first, geometry score second). Package bytes range-pulled from the
doa4-mirror-20261017 release (extracted tar member map recovered by
`tools/phase5/tarwalk.py`: chrone.afs data @ tar 1212324864 ✓ matches
phase-4's recorded offset; chrtwo.afs @ 1578419712, 548,042,752 B;
chrthree.afs @ 2135433728).

### chrone pkg01 — ASSEMBLED (chrone_pkg01_v2.glb, 71 meshes)
- XPR2 at chrone 0xF98000; graph = 60 objects; segments located 71/71.
- Per-decl quality (geometry score of chosen strip): clean 37 /
  moderate 28 / poor 6. The 6 poor are all small s0/s1 decls (21, 39, 47,
  53, 61, 67; scores 0.26–0.49, coverage still 1.00 — right strip family,
  rough geometry fit, same part-reuse ambiguity documented in phase 4).
- Front render VIEWED (`chrone-pkg01-assembled-v1-front.png`): coherent
  complete character — bow collar, ruffled chest, wide gown, front pouch,
  one leg below the hem. Sleeve cuffs show checker-shard patches (the
  moderate/poor small decls). Overall: moderate, a step below pkg00 v4.

### chrone pkg00 — assembled in phase 4 (PR #427), pose-test renders §4.
### chrtwo pkg00 — ASSEMBLED, PARTIAL (chrtwo_pkg00_v1.glb, 59 meshes)
- XPR2 @ chrtwo 0x1DF000; graph = 59 objects; segments located 59/59
  (bytes = chrtwo.afs [0, 0x1400000) range-pulled from mirror part-03).
- Quality: clean 7 / moderate 43 / poor 9 — the weakest of the three.
- Front render VIEWED (`chrtwo-pkg00-assembled-v1-front.png`): the torso
  is a smooth coherent shell (sleeveless top, collar opening, chest
  emblem, arm stubs) but the lower body collapses into crumpled shards —
  lower decls mis-paired under part reuse. Stated plainly: chrtwo pkg00
  is a torso-grade assembly, NOT a clean character yet. (First pairing
  attempt was also killed by a VM restart mid-run; the landed build uses
  coverage-first top-3 candidate pruning, `batch_build_chrtwo.py`, which
  may itself cost some geometry-score accuracy vs full scoring.)

Characters assembled this phase: chrone pkg01 (complete, moderate) +
chrtwo pkg00 (partial) — plus chrone pkg00 from phase 4 = 3 characters.
Viewed front renders: pkg00 bind, pkg00 bend14z, pkg00 bend28z, pkg01
front, chrtwo front = 5.

## 6. Job 3 — TX2D (stretch): NOT COMPLETED — narrowed lead, no guessing

chrone pkg00 carries 42 TX2D descriptors (40 B each). Partial decode
(`tools/phase5/tx2d.py`): word2 is a monotonic data offset within the
package texture pool (steps = per-texture sizes); word3 = 0x30001 (type);
word9 packs two 13-bit fields that read exactly as
`(h_blocks−1)<<13 | (w_blocks−1)` on multiple descriptors (e.g. 0x3e01f =
32×32 blocks, 0x7e03f = 64×64 blocks). NOT yet pinned: the pool's file base,
the DXT variant (word0 alternates 0xc14/0xd10), and the Xbox 360 tile
swizzle. No PNG produced and no texture claimed — per the no-guessing rule
this stays flagged as the top TX2D lead for the next lane rather than a
fabricated decode. The XEX skinning-consumer Ghidra cross-check (job 1
optional step) was likewise not needed: the pose test was decisive.
