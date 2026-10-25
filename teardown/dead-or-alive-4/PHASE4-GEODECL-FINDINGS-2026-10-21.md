# DOA4 Phase 4 — GeoDecl vertex-pool crack + first assembled character

Follow-on to PR #402 (phase 3: assembly graph). Phase 3 ended with the graph
parsed (ObjGeo / ObjInfo / Hie) and the vertex pools undecoded: the phase-2
format assumptions produced the ±3e38 spiked pools. Phase 4 settles the real
format from the GeoDecl records themselves and lands the first assembled
character: `models/chrone-pkg00-assembled-v1.glb` (64 meshes, 58 objects;
front render `chrone-pkg00-assembled-v1-front.png`, viewed by the author —
reads as one coherent character in bind pose: bow collar, dress/gown body,
sleeve/arm cylinders, legs).

Tool: `tools/doa4_assemble2.py` (decode3/assemble lineage).

## 1. The descriptor layer (the phase-2/3 bug)

XPR2 directory records are 16 bytes `(magic, f1, f2, f3)`. **f1 is the
XPR2-relative byte offset of a 20-byte descriptor**
`(flags, addr, size, type, 0)` — type `0x10001`=VBUF, `0x20001`=IBUF,
`0x30001`=TX2D — **not** a vertex-data offset. Phase 2/3 read f1 as a data
offset; every pool built on that reading is invalid. Corroboration:

- stg pkg00: XPR2 @ file `0x258800`, 517 records; every record's f3 = 8260,
  a package tag, not a vertex count.
- chrone pkg00: XPR2 @ `0x357000`, directory = XPR2 + USER×4 + TX2D×42 +
  VBUF×96 + IBUF×68 (211 records). XPR2 header record: f1=106484,
  f2=11622400 (≈ the GPU image size), f3=210 (= record count − 1).
- Descriptor `addr` fields form a perfect sequential GPU allocation in
  directory order (step = align(size, 0x1000)); descriptor `size` is exact
  for IBUF and for most VBUF records. The descriptor addr does **not** map
  to a file offset by any single base (VBUF and IBUF evidence contradict a
  shared base; see §3 for the mapping that does hold).

## 2. GeoDecl format (ground truth)

GeoDecl is a named sub-chunk inside ObjGeo (offset from ObjGeo header
+0x28; +0x20 = item-table offset, +0x38 = object index). Standard 0x30
named-block header + u32 offset table → records:

| offset | field |
|---|---|
| +0x00 | payload size |
| +0x04 | = 1 |
| +0x08 | global decl index (sequential across the package) |
| +0x0c | **segment index count** (== sum of the decl's ObjGeo item index counts) |
| +0x10 | element count **including** the END terminator |
| +0x14 | **segment vertex count** |
| +0x18 | decl stream (0, 1, 3) |
| +0x20 | flag (0/1) |

Elements at +0x30, **12 bytes each**: `(byte_offset_in_vertex, buffer_tag,
packed_usage)`.

- `buffer_tag` ∈ {`0x2A23B9`, `0x2C23A5`} — identical in stg and chrone →
  two global attribute planes (A/B), not addresses.
- `packed_usage`: hi u16 = D3D usage (0=POSITION, 1=BLENDWEIGHT, 3=NORMAL,
  5=TEXCOORD, 6=TANGENT); next byte = usage index (TEXCOORD 0/1/2 seen).
- END element = `(0x00FF0000, 0xFFFFFFFF, 0)`.
- Element byte sizes: POSITION 12, NORMAL 12, TANGENT 12, TEXCOORD 8,
  **BLENDWEIGHT 8 (2 floats) or 12 (3 floats) — varies per decl**; the
  segment validator arbitrates. Where the phase-2 assumed format and
  GeoDecl disagree, GeoDecl wins (phase 2's uniform stride guess is the
  direct cause of the spiked pools in blend decls).
- The 16-byte record tail carries the segment's VBUF descriptor counter
  (descriptor index = counter + 1; verified by 36 exact size matches +
  the full decl-order walk in §3). Which tail slot holds it rotates with
  the decl's element count (4 elems → slot 0; 5 → slot 1; 2 → slot 2;
  7 → slot 3). The tail carries **no** IBUF link.
- ObjGeo item record (+0xC8 per-item texture index; material floats at
  +0x80) carries no vertex base and no strip link.

Stream shapes (chrone pkg00 census, 68 decls):

| stream | elements | stride |
|---|---|---|
| 0 | POSITION | 12 |
| 1 | POS + NORMAL + TEXCOORD0 | 32 |
| 1 | + BLENDWEIGHT | 40 / 44 |
| 3 | POS + NORMAL + TEXCOORD0/1/2 + TANGENT | 60 |
| 3 | + BLENDWEIGHT | 68 / 72 |

## 3. Where the bytes actually live

**Vertex segments**: replicated in “sets” in decl order, each in a slot of
`align(vtx_count × stride, 0x1000)`. A candidate verifies when ≥99.5% of
its vertices have unit-length normals **and** lie inside the object's
ObjInfo bounds — segment bboxes share exact planes with the bounds
(e.g. decl13: bbox = bounds on x-min, y-min, z-max simultaneously).

- Set B (chrone pkg00, data1) is complete: decl11 @ `0xCCC000` … decl67 @
  `0xE2F000`, walked in order with small resync gaps (foreign resources
  sit between some segments). decl1 @ `0xAD4000`. Set A (data0) covers
  decl11–18 from `0xC1000` before diverging.
- **Positions are stored in model bind space** — the space ObjInfo bounds
  describe. Applying the Hie world matrices on top pulls the assembled
  figure apart (rendered and viewed); the Hie is the skinning skeleton,
  not bind placement.
- decl0 (obj0 stream 1, 638 verts) is the one segment not yet located: it
  is not at its set-B slot (texture data lives there) and no scanall
  candidate beat the foreign-resource false positives. Obj0 renders from
  decl1 alone.
- Foreign (non-decl) geometry exists in the package: a 574-vert stride-60
  segment at set A's decl19 slot (`0xE6000`, strip = IBUF desc #12,
  max index 573 / 574 distinct) and a ~1332-vert resource whose strip is
  IBUF desc #3. Not part of the character's GeoDecl table.

**Index buffers**: file = `(addr & ~3) − 0x8C4000` (chrone pkg00), one
0x1000 slot per descriptor in an index area at files `[0x1FA000, 0x250000)`.

- Stream-3 strips are **sequential triangle lists** `(0,1,2,FFFF,
  3,4,5,FFFF,…)` — vertices are stored in triangle order.
- Stream-1/0 strips are **genuine strip walks** with FFFF restarts.
- Pairing strips to decls: full vertex coverage (distinct == vtx,
  max == vtx−1) is the trustworthy signal; geometry score alone is
  compromised because the model reuses parts (identical parts appear at
  many objects, and a reused part's strip scores well against all of
  them). Confirmed pairs include decl7→#18, decl12→#6, decl21→#14,
  decl25→#18, decl42→#36, decl48→#36, decl56→#49, decl62→#49,
  decl59→#52, decl60→#53, decl30→#23, decl10/28/38→#30.
- decl1 (obj0 stream 3, 15,640 verts) breaks the sequential rule: its
  strip (IBUF desc #2, 20,984 slots) is a real walk referencing 7,861
  distinct verts — the segment is a merged multi-island pool. Its
  triangles are currently emitted sequentially (winding agreement 0.738,
  big-edge fraction 0.013); the walk does worse (0.58). Open item.

## 4. Assembly result + per-decl quality

64 of 68 decls assembled (decl0 no segment; decl54/57/63 no strip above
the coverage bar). Exported triangles are **winding-normalized** against
the file's vertex normals: garment pieces carry inner+outer surfaces with
mixed winding (game renders double-sided; glTF consumers shade
single-sided — before this fix the render read as black shards; after, as
a coherent figure).

Per-decl triangle quality (big-edge fraction = share of triangles with
mean edge > 0.25 × segment diagonal; ≤0.05 is clean):

- Clean (27 decls): 1, 5, 6, 7, 9, 13, 14, 17, 19, 21, 24, 25, 27, 31,
  32, 35, 37, 42, 46, 52, 55, 56, 59, 60, 62, 65, 66.
- Moderate (18): 2, 3, 4, 8, 11, 12, 16, 22, 23, 26, 34, 38, 39, 41, 43,
  48, 49, 51.
- Poor (19, mostly small stream-1/0 parts whose strips are still
  mis-paired; they render as crumpled patches, not spikes): 10, 15, 18,
  20, 28, 29, 30, 33, 36, 40, 44, 45, 47, 50, 53, 58, 61, 64, 67.

## 5. G3 (skinning) standing — weights yes, indices no

- **BLENDWEIGHT (usage 1) is located and verified as skinning data**:
  20/68 decls carry it; values ∈ [0, 1]; per-vertex rows sum to 1.000
  (measured on walk-verified segments: decl15 sample (0.99, 0.01),
  decl20 (0.344, 0.656), decl6 3-influence (0, 0.602, 0.398)). 8-byte
  elements = 2 influences, 12-byte = 3 influences.
- **BLENDINDICES (usage 2) occurs in ZERO of the 68 decls.** The bone
  indices are not in the vertex streams; no pose test is run and no
  weights are guessed. The index source must be elsewhere (per-item /
  per-object data is the open lead). G3 stays ADVANCED, NOT PASSED.

## 6. XEX corroboration (Ghidra, targeted)

- XPR2 magic is built at `0x007B613C–0x007B6148` (`lis r8,0x5850;
  ori r7,r8,0x5232`). The function @ `0x7B6120` is a bundle validator +
  handle builder over a package-registry table at `0x82C66740` (30 slots
  × 8B; checks first word == 'XPR2').
- The named-block finder @ `0x7B5E00` builds "USER" (`0x55534552`), walks
  (name, offset) pairs at struct +0x10/+0x14 stride 0x10, block pointer =
  package_base + entry_offset + 0xC, type/version word == `0x28000102` —
  matches the phase-3 graph mechanics exactly.
- The descriptor→memory registration function was not identified; the
  format crack above made it unnecessary for assembly.

## 7. Gates (per PR #397 standard; cf. PR #402)

- **G1 (decryption) — NOT advanced.** No cipher work this phase; chr/mot/
  stg payloads parse plaintext (41 packages, phase 3). Cipher covers AFS
  TOCs + anm.afs body only.
- **G2 (extraction completeness) — NOT advanced.** No new AFS extraction;
  worked from the phase-3 spans.
- **G3 (rigging/skinning) — ADVANCED, NOT PASSED.** Blendweights located
  and verified (§5); blend indices absent from all vertex streams;
  Hie parsed (phase 3). No pose test possible yet.
- **G4 (animation) — NOT started.** Blocked on G1 keystream work for
  anm.afs (phase 3 note stands).
- **G5 (QuickBMS .bms) — N/A this phase.**
- **G6 (assembled models) — ADVANCED.** First assembled character GLB
  landed (this PR): 64/68 decls, front render viewed, silhouette and
  majority surfaces coherent; per-decl defect list in §4. Nothing is
  wired into `game/` yet — teardown-side landing, not a playable-build
  finish (owner acceptance target, 2026-10-20 ~20:57 CDT).

## 8. What remains before DOA4 content is playable

1. decl0's segment + the 19 poorly-paired small strips (strip↔decl
   pairing needs a stronger key than coverage+score — the ObjGeo item
   texture index or a per-item field is the lead).
2. decl1's merged-pool index space (7,861 referenced of 15,640 verts).
3. Textures: TX2D descriptors + the 20B D3D texture headers after them
   are mapped as records but not decoded into the GLB (the landed GLB
   is untextured geometry; per-item texture indices are parsed).
4. Blend-index source → pose test → G3 pass; then animation (G4) and
   game-side wiring per PR #397.
5. Batch: the pipeline is package-generic (same code path); chrone
   pkg01+ and chrtwo tables are the immediate follow-on.
