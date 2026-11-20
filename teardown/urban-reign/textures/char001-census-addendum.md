# char001 tail census — ADDENDUM: THE CRACK (Attempt 6, later same day)

The census's §6 verdict ("no self-contained GIF stream, register
traffic absent") was WRONG in one specific way, and the correction
cracked the format. Recorded here so nobody re-derives it:

## What the census missed

The census's A+D scan required the register-address byte at qword
offset **+12**. The PPK's descriptor packets use the other A+D
framing: data u64, addr u32, pad u32 — address byte at offset **+8**.
All "TEX0 = 0 sightings" conclusions from the +12 framing are void.
(Phase 2's "VIF-walk dies" result stands for the bulk tail — the
descriptors are a TABLE, not an interleaved stream.)

## The actual structure (all offsets char001)

Post-vertex region of the type-0x0002 chunk contains TWO tables:

1. **Upload descriptor table** (~0x576B0): 128-byte packets ×56
   (two identical copies of 28), each a literal DMA/GIF upload
   program: DMA CNT (QWC=6) → GIFtag PACKED A+D ×4 (BITBLTBUF,
   TRXPOS=0, TRXREG w×h, TRXDIR=0) → GIFtag IMAGE → DMA REF
   (QWC, src_addr). All uploads PSMCT32-shaped (DPSM=0); invariant
   w·h·4 == IMAGE bytes == REF bytes holds for all 28. REF addrs
   tile a contiguous pool with zero gaps (28 uploads, 0x2A70..0x2EDF0).
2. **Draw descriptor table** (~0x59480, stride 0x60): TEX1_1/TEX0_1
   A+D pairs ×28. TEX0.PSM = 19 (PSMT8) or 20 (PSMT4): the real
   textures are INDEXED. TEX0.TBP0 == image upload DBP; TEX0.CBP ==
   CLUT upload DBP (16×16 uploads = 256-entry PSMT8 CLUTs; 8×2 =
   16-entry PSMT4 CLUTs; CLUT entries stored linear RGBA).

## Pool base

REF src_addr is relative to a per-file pool base (char001:
0x57480; char002: 0x57800). Discovered by CLUT-likeness slide
(alpha byte ∈ {0xFF, 0x80}); at the true base a CLUT starts exactly
at base+0x2A70 with a smooth RGBA ramp. `ur_tex_extract.py`
auto-discovers it per file.

## Decode (the composed mapping — this is the key insight)

Naive reads all fail for a reason: the loader uploads index bytes
through a **CT32-shaped transfer** (stream word → CT32-swizzled VRAM
address), and the draw samples the same VRAM as **PSMT8/PSMT4**.
Correct pixel = CLUT[ stream[ invCT32( PSMaddr(x,y) ) ] ], with
image width = TBW*64. Pure-linear and pure-PSM reads both produce
striped noise; the composition produces the art.

## Proof (viewed own-eyes, this lane)

- tex14 pair → `char001_tex00_psmt8_128x128_tbp11328.png`:
  two hands, fingers/palms, real skin tones.
- tex19 pair → `char001_tex04_psmt8_256x256_tbp11559.png`:
  the fighter's face — eye, stubble, ear, hair — real colors.
- PSMT4 pairs decode too: snakeskin (tex01), snakeskin jacket
  panel with belt (tex02), black leather pants (tex07).
- char002 runs through the same extractor unchanged: identical
  table structure, own base 0x57800. 8/10 of its decoded textures
  are byte-identical to char001's; hands (tex00) and tex08 differ
  — char001/char002 are costume-variant PPKs at the SOURCE level
  (vertex data and file size also differ; no cross-file bleed —
  extraction is per-file isolated).

## Open edges (recorded, not hidden)

- 1 of 14 TEX0 records (PSMT4, TBW=1, narrow buffer) fails the
  composed-geometry check — narrow-buffer page layout differs;
  recorded as `undecoded` in the inventory.
- 3 TEX0 records have no upload at their TBP0/CBP (template/dup
  variants of the two table copies) — unpaired, recorded.
- TEX0 TW/TH are template max (mostly 10/10); true dims come from
  TRXREG/TBW as documented in the extractor.
