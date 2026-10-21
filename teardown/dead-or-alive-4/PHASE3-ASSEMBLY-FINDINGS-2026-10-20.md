# DOA4 Phase 3 — MdlGeo/ObjGeo Assembly — Findings (2026-10-20)

Lane: DOA4 PHASE 3 recovery attempt 3. Goal: pools → assembled characters
via MdlGeo ObjGeo transforms. **Result: the assembly graph is fully
reverse-engineered and parsed (`tools/doa4_assemble.py`, verified on 41
packages across chrone/mot/stg). End-to-end assembly is blocked on one
precisely identified piece: the vertex-pool location/format (evidence
below). No assembled character GLB is claimed by this lane.**

## Research first (performed this run)

- Web/GitHub search for published MdlGeo/ObjGeo format work, DOA4 Noesis
  plugins, XPR2-in-DOA4 tooling: **nothing exists** (consistent with PR
  #381's RESEARCH-PULLINS-2026-10-20.md: no community tool or format doc
  covers DOA4's chr*/mot/stg packages; DOA5-era TMC tooling does not
  apply). The MdlGeo/ObjGeo names were known only as strings this
  project found in the XEX on 2026-10-18.
- The format below was reversed from the real bytes this run: stg.afs
  (480MB partial already on disk from the phase-2 lane's release pull),
  mot.afs (75,393,024B, range-pulled from release
  `doa4-mirror-20261017`, extracted-tar part-02 asset), chrone.afs head
  (32MB range pull; member verified: `extracted/chrone.afs`,
  366,094,336B).

## The package format (SOLVED)

Every model package is one AFS file laid out as:

```
[data section: strips / textures / per-object data]
[XPR2 directory: 16B records XPR2/USER/TX2D/VBUF/IBUF]
[MdlGeo] [MdlInfo] [Hie]
```

- **XPR2 directory**: header record f3 = record count. The four USER
  records are a block directory — (offset−12, size) for the header
  block, MdlGeo, MdlInfo, Hie; each block's name string sits 12 bytes
  after the USER offset. All other record types also carry the
  package-wide f3 tag (e.g. 3364 for chrone pkg0) — f3 is NOT a
  per-record count.
- **Named blocks** (MdlGeo/MdlInfo/ObjGeo/ObjInfo/GeoDecl/Hie) share a
  header: 8B name, `ff 00 01 00`, u32 header size 0x30, u32 total
  size, u32 count, u32 count, u32 zero, u32 offset-table offset,
  u32 zero, u32 zero, u32 zero. MdlGeo/MdlInfo/Hie then hold a u32
  offset table (block-relative) to their sub-blocks.
- **ObjGeo** (per object, inside MdlGeo): item-offset table at header
  +0x20, GeoDecl sub-chunk at +0x28. Item records are 0x140 bytes:
  +0x10 index_start, +0x14 index_count, +0x18 stream (1/2/3),
  +0x80.. material floats. **Items are index ranges into
  per-(object,stream) IBUF strips** — verified numerically: chrone
  pkg0 obj0's stream-3 items sum to 20,983 indices; its descriptor
  strip has 20,984 indices and max vertex index 7,860. Obj1: stream-3
  items 4,102 vs strip 4,104 indices; stream-2 items 1,785 vs strip
  1,792. (Small deltas = strip restart/end padding.)
- **ObjInfo** (per object, inside MdlInfo): bounds, NOT transforms.
  Block +0x60 and each 0x50-byte item at +0x20 carry
  (center.xyz, sphere_radius), (center.xyz, 1.0), (extents.xyz, 0)
  with radius == |extents| — verified numerically (mot pkg0 obj0:
  extents (0.11620, 0.29571, 0.13210), |e| = 0.34409 == stored radius).
- **Hie** (one per package): the hierarchy. Node count == object
  count in all 41 packages checked. Node record = 0x50 bytes: 4×4
  row-major local matrix (translation in row 3) + u16 links at +0x40
  (parent index at +0x42; 0xFFFF = root; other fields are
  child/sibling lists). World = local × parent_world (row-vector
  convention). chrone pkg0 composes into character-scale chains:
  root objects at T≈0; obj4 world T (0.078, −0.845, −0.026) via parent
  obj8 (0, −0.416, 0); mirrored L/R node pairs (T ±0.247 on X) appear
  throughout. Multiple roots = body + hair/cloth sub-hierarchies.

## The blocker (exact evidence)

Assembly needs, per (object, stream), the vertex segment its strip
indexes. That segment's location/format is **not** what the shipped
decoder assumes:

1. **VBUF f1 is not a file offset.** In every package, VBUF record f1
   values step by exactly 20 (the vertex stride) across records — a
   sequential resource-space offset. (Same for IBUF record f1 before
   its descriptor.)
2. **The absolute-f1 pools are not positions.** `doa4_decode.py` /
   `doa4_decode3.py` read the pool at min(f1) as absolute file offset.
   Those bytes are bounded float streams with all components in
   [−1, 1] whose values repeat across consecutive 20-byte records
   (e.g. chrone 0x1896c: records share components in a rolling
   pattern). Point clouds of them have no silhouette (SWEEP-AUDIT
   2026-10-20 own-eyes finding, re-confirmed analytically here). For
   chrone table 0 the absolute reading happened to stay inside the
   archive's lead-in data region; for mot tables 9/10 it reads mot's
   replicated lead-in float data — the shipped mot_09/mot_10 GLBs are
   therefore suspect as well. **The 165 shipped triangulated GLBs
   should be treated as unassembled index/stream artifacts, not
   character geometry, until pools are re-located.** (Their strip
   topology may still be valid — the strips are real: chrone pkg0
   desc-at-0xac0000 holds 20,984 u16 indices, all < 7,861, matching
   obj0's stream-3 items.)
3. **Pool scans came back negative.** NumPy scans of chrone's lead-in
   (0..0x357000) and pkg0 data section (0x36F2E8..0xF8C000) for
   stride-{12,16,20,24,32} vertex layouts (pos, pos+uv, pos+normal+uv;
   plain and 16-bit-byte-swapped floats; ≥98% purity over ≥6,000-vert
   windows; UV required in [0,1] where present) found **no** position
   pool. The only ≥98% hits are the same bounded [−1,1] float-stream
   data (bbox exactly ±1 — normalized data, not character space).

## Next steps (for the following lane)

1. Parse **GeoDecl** fully (per-stream element layout: stream, offset,
   type, usage). It defines where positions live per stream and in
   what component format (possibly half-float or GPU fetch-swizzled
   streams, which the scans above would not match).
2. Re-locate pools via the XEX: the loader code that consumes the
   XPR2 directory (CRI adxf is table-indirect per Audit 19; the
   resource upload path in the XDK XGraphics layer handles VBUF/IBUF
   resources) — Ghidra project `~/workspace/ghidra-projects/doa4/`.
3. Once one (object, stream) segment is located, verify against its
   strip (indices < segment count; triangles coherent), then
   `doa4_assemble.py` already provides the graph + world matrices to
   emit the assembled GLB. The strip→(object, stream) assignment
   order also needs one confirmation pass (descriptors are in
   directory order; items are per object/stream).

## Landed by this lane

- `tools/doa4_assemble.py` — package/assembly-graph parser + Hie
  world-matrix composition (runs on chrone/mot/stg packages).
- `assembly-graphs/` — parser output for chrone pkg0 (58 objects),
  mot pkg9 (67 objects), stg pkg0 (134 objects), incl. per-object
  items, bounds, local + world matrices.
- This findings doc.

## Data / footprint

- Pulled targeted ranges only: mot.afs 75,393,024B + chrone head
  33,554,432B + five small seam reads (<1MB total) from release
  `doa4-mirror-20261017` extracted-tar part-02 (asset 651173731).
- stg partial (503,316,480B) pre-existed in the phase-2 scratch.
- All pulls are scratch-local to `~/workspace/_doa4p2-scratch/` and
  re-fetchable from the release; nothing game-file was deleted.

## Addendum 2026-10-20 ~21:45 CDT — gate citation (PR #29 / PR #397)

Required reading landed after this PR opened: game-reverse-engineering
PR #29 (`docs/research/teardown-completion-2026-10-20/doa4.md`) and
western-heart PR #397 (`docs/research/TEARDOWN-WIRING-STANDARD-2026-10-20.md`).
The DOA4 completion gates from those docs, and this PR's standing
against each:

- **G1 Keystream proof (five-oracle protocol on full payloads, all six
  containers)** — NOT this phase. Per the lane order, keystream work
  comes after MdlGeo assembly. When it runs, it closes by the
  five-oracle protocol (XPR2 texture decode / table self-consistency /
  anim float plausibility / cross-container consistency / entropy),
  not by header evidence. One factual note for that lane: this run and
  PR #381's audit both establish that chr/mot/stg *payloads* parse as
  plaintext (this doc's 41 packages were parsed with no decryption);
  the cipher covers the AFS TOCs and anm.afs's body. The oracles
  should be aimed there.
- **G2 chrthree completeness (75/75)** — NOT satisfied by this PR
  (56/75 shipped previously; this lane converted no tables).
- **G3 Skeleton/weights (real skeleton export + Blender pose test)** —
  ADVANCED, NOT PASSED. This lane located and parsed the skeleton
  hierarchy (the Hie block: per-object 4×4 local matrices + parent
  links, world composition verified) — the structure G3's skeleton is
  built from. Per-vertex weights are still unlocated (they ride on
  the open vertex-format question), and no pose test was run. No G3
  claim is made.
- **G4 Animation (anm.afs clips play on chr skeletons)** — NOT
  started; depends on G1 for anm.afs plus G3.
- **G5 Reproducibility (proven decryption published as QuickBMS
  `.bms`)** — NOT APPLICABLE yet: this lane proves no decryption and
  publishes none. The `.bms` is the required delivery form when G1
  passes.
- **G6 Import-verify count (baseline PR #386: 165)** — NOT advanced:
  this PR adds 0 assembled GLBs. Per this lane's evidence the 165
  shipped GLBs are unassembled index/stream artifacts (their "pools"
  are not position data), so the count must not be read as assembled
  or wired models.

**Owner acceptance target (2026-10-20 ~20:57 CDT) — DOA4 status in
those terms:** assembled characters: **0**. Wired into the playable
build (`game/`): **nothing from this lane** — no DOA4 fighter, moveset,
or animation is live in a fight or the customization suite.
Dependency chain remaining: vertex-pool format (GeoDecl) → assembled
GLBs → skeletons/weights + pose test (G3) → animations via the
five-oracle keystream work (G1/G4) → QuickBMS publication (G5) →
wiring per the PR #397 standard (WIRING-INVENTORY with
WIRED/FLAGGED per file, canon conversion logged, moveset-library data
with Tekken inputs, independent verification). This PR is the
assembly-graph foundation of that chain — not a playable-content
claim.
