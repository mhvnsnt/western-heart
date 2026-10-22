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
  + pushed (pending — updated next commit).
