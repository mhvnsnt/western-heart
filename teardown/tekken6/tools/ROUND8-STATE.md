# Tekken 6 PSP — ROUND 8 STATE (NDPP vertex crack + textures + skeletons)

Date: 2026-10-21. Branch: `teardown/tekken6-round8-ndpp-vertex`,
stacked on `teardown/tekken6-round7-ndpp-movesets` @ 9510e06 (PR #489).

## Inherited verified state (round 7, not re-derived)

- Container directory SOLVED: (slot_count, header_size) +
  (chunk_size, cumulative_end_offset) tiling to EOF.
- Top-76: 12 CHARACTER packages (NDPP body + BONE 8,032B +
  NDPP head ~17KB + name kao_/MODEL_HEAD + BONE head 1,664B),
  16 stage/object (slot-9 BE float stream 61-218KB),
  29 NTPP texture packages.
- Census: 5,470 containers = 3,702 A / 1,432 B / 336 other;
  1,565 NDPP occurrences.
- NDPP interior: 20B header + 2x64B descriptors (bbox validated)
  + count word (3120 in idx00) + dense interleaved UNIT-NORMAL
  stream with ~48B block headers; NO plain float3 positions.
- EBOOT: NDPP dispatched by slot (no magic/string); NTPP ctor
  xref @ 0x892fdf0; BONE template VA 0x08bdaab0 (110 bones;
  file counts 146 body / 22 head; stride unproven).
- Movesets: 18/18 JSONs shipped round 7.
- Workdir retained: ~/workspace/_t6r4-work/ (3.2GB, NEVER delete).
  Ghidra at ~/workspace/tools/ghidra/ (+ GhidraMCP).

## Jobs (in order)

1. JOB 1 (B1, critical): NDPP loader in EBOOT via Ghidra ->
   vertex/index layout. Proof: first character GLB + FRONT
   render viewed + bbox-integrity comparison.
2. JOB 2 (B2): NTPP decode from ctor @0x892fdf0 -> PNGs, pair
   to characters with evidence, bake into GLBs.
3. JOB 3 (B6+B3): BONE stride -> skeletons for 12 packages
   (146+22), skin if weights present.
4. JOB 4 (B5): stage slot-9 BE stream -> stage GLBs, render viewed.
5. JOB 5 (B4, if 1-4 land): COM binary command encoding.

## Results

- BOOTSTRAP: branch created, this file committed + pushed
  (972076d, API-verified).
- JOB 1 PARTIAL: NDPP unit model + stride 12 PROVEN
  (strip-table deltas == count*12 exact); descriptor re-read
  proven; candidate-A packing REFUTED by viewed point-cloud
  render (bbox-wall pile-up). First character GLB NOT shipped
  — remaining step is the loader's 12-byte unpack in the
  model-class vtable methods, asm-scoped in
  `round8-evidence/JOB1-VERDICT-AND-BLOCKER.md`. Ghidra pass 1
  done (NTPP ctor/template, BONE xrefs = memcpy defaults).
- JOB 2 SEEDED: NTPP template dumped from ELF + GIDX tie-in;
  interior not decoded, nothing baked.
- JOB 3 PARTIAL: BONE parallel-array structure CRACKED
  (offsets 64/64+4N/64+16N/64+28N verified N=110/146/22);
  array roles + skeleton assembly remain.
- JOB 4 SEEDED: stage slot-9 BE offset-table head mapped
  (idx24); layout not decoded, no stage GLB.
- JOB 5: not attempted (Jobs 1-4 did not all land).
