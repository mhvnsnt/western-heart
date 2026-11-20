# Tekken 6 PSP — ROUND 9 STATE (THE 12-BYTE UNPACK, blocker B1′)

Date: 2026-10-21. Branch: `teardown/tekken6-round9-ndpp-unpack`,
stacked on `teardown/tekken6-round8-ndpp-vertex` @ 78f04cb
(PRs #489/#501 rounds 7–8 COMPLETE).

## Inherited verified state (rounds 7–8, not re-derived)

- NDPP submesh UNIT = 20B header + strip table (8B records:
  `0x01000000+offset` / `0x04040000+count`, offsets from
  unit-header start) + marker `(u32 0x13, u32 0x0b)` + packed
  vertex stream, **stride EXACTLY 12 bytes**
  (`offset[k+1]-offset[k] == count[k]*12` on every sampled record).
- Descriptors `[y_center, z_center, f2, xmin..zmax]` proven.
- Candidate A packing (bytes 6–11 = 3×u16 affine-to-bbox)
  REFUTED by viewed render — do not revive.
- 12B records have a token-like byte alphabet → packed
  fixed-point; scale/origin may come from the per-unit header,
  companion float3 streams, or the cross-section-identical
  byte-sparse block.
- Loader facts: no NDPP string in the ELF (slot dispatch);
  NTPP ctor `FUN_0892fdf0` decompiled (round 8); BONE template
  xrefs are memcpy defaults only.
- BONE = parallel arrays (offsets `[64, 64+4N, 64+16N,
  64+28N…]` exact for N=110/146/22) = one 4B array + two
  float3 arrays per bone; roles unproven.
- Sample set: idx00 body section, 42 units / 685 verts (round 8).
- Workdir retained: `~/workspace/_t6r4-work/` (3.2GB, NEVER
  delete). Ghidra at `~/workspace/tools/ghidra/`.
- Round 8's Ghidra scratch was in /tmp and is GONE — round 9
  rebuilds the EBOOT import in the WORKDIR:
  `~/workspace/_t6r4-work/ghidra-r9/`.

## Scoped target (B1′)

The model-class vtable methods (ctor `FUN_0886fe88`, vtable @
`0x08b918b8`) and/or the shared chunk walker that consumes the
`(0x13, 0x0b)` marker and the `0x01000000`-masked strip offsets
— that code holds the unpack. PSP VFPU instructions
(`lv.q`/`sv.q`, `vfim`, conversions like `vcvt`) are prime
suspects for a packed→float expansion.

## Jobs (in order)

1. JOB 1 (B1′): decompile vtable methods + chunk walker in
   Ghidra (MIPS LE); extract EXACT 12-byte record semantics
   (field layout, fixed-point scales, origin/scale source,
   strip connectivity). Cross-validate vs idx00 body bytes +
   a second section. PROOF GATE: decode full unit set →
   point cloud → strip triangle mesh → FRONT render VIEWED;
   body coherent (limb-like clusters inside section bbox,
   NOT wall-piled), proportions match the section box of
   `ndpp_bounding_volumes_r7.glb`. Pass → first character GLB
   + batch remaining character packages' body sections.
   Fail → land decompiled walker + exact ambiguous asm.
2. JOB 2 (B6′): BONE array roles from template @0x08bdaab0
   data + skinning-adjacent consumers from Job 1; assemble
   ONE character package skeleton (146 body bones); bind-check
   vs mesh if Job 1 passed.
3. JOB 3 (B2): NTPP interior from round-8 byte-exact template
   (fields 0x110, 0x40, 0x80, 0x100050, 0x84030100, 0x80020)
   + GIDX string-table site → PNGs (viewed, real colors),
   pair to character packages with evidence, bake into GLBs.
4. JOB 4 (B5, if time): stage slot-9 stream (idx24 head map:
   BE offset table stepping 0x20, 0x15a60 = payload−64) →
   first stage GLB + viewed render.

## Results

- BOOTSTRAP: branch created from 78f04cb, this file committed
  + pushed (76d54c6, API-verified).
- JOB 1 (B1′) **CRACKED + PROOF GATE PASSED**: NDPP units are
  embedded GE display lists (VTYPE 0x12 header command; strip
  table = VADDR/PRIM command pairs; terminator 0x13/0x0B).
  Vertex layout from VTYPE: weights u8 (sum 128) + UV u8 +
  normal s8 + position s16; stride 12/14/16 by weight count.
  Scale: world = raw x descriptor_ymax/32767 (4 sections,
  2 files). First character GLB shipped
  (`models/idx00_slot0_r9.glb`, head section, 3,217 verts /
  1,897 tris, bbox match <=0.03) + FRONT render VIEWED
  (coherent human head). Evidence:
  `round9-evidence/JOB1-UNPACK-CRACKED.md`. Ghidra import was
  OOM-killed on this VM; vtable/ctor read via capstone
  disassembler instead (documented in the evidence doc).
- JOB 1 BATCH: all 24 NDPP sections of the 12 character
  packages decoded to GLBs in `models/` (idx00/01/04/05/08/
  09/12/13/16/17/20/21 x slot0+slot10). Second character's
  face render VIEWED (idx01 slot0, coherent). idx00 slot10 =
  T-pose full body (scatter VIEWED; its Blender frame came
  back blank - triangles verified healthy, median area 5606,
  framing issue only). Stage packages (idx24+) fail the
  character-package parse as expected (no BONE; B5 scope).
- JOB 2 (B6') DONE: BONE roles PROVEN from data (parents /
  local translations / Euler rotations Rz*Ry*Rx / scales /
  32B name table). Skeletons assembled + shipped:
  `models/idx00_skeleton_r9.glb` (110 bones) +
  `models/idx04_skeleton_r9.glb` (146 bones); bind-check vs
  meshes PASSED (overlay render VIEWED). Remaining sub-item:
  per-unit bone palette for skinned GLBs (unit header words
  3-4, unproven - stated in JOB2-BONE-ROLES.md).
- JOB 3 (B2) PARTIAL: NTPP interior MAPPED byte-exact (idx02:
  section header fields confirmed vs ELF template; +16 =
  first-block size; two GIDX blocks @+80/+3232 with format
  words 0x10400612/0x10400610). Pixel format NOT decoded -
  candidate renders rejected as unproven, nothing baked,
  no pairings invented. Evidence: round9-evidence/
  JOB3-JOB4-STATUS.md (exact next step: targeted decompile
  of the five NTPP-class methods, capped-heap).
- JOB 4 (B5) SEED RE-VERIFIED: idx24 slot-9 BE head matches
  round 8 (0x15a60 = payload-64). Layout not decoded, no
  stage GLB (Jobs 1-3 took the lane).
