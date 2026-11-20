# Urban Reign — char001 PPK tail census (Phase 3, Attempt 6)

Byte-level census of the char001 PPK "tail" (the type-`0x0002` chunk),
produced by `teardown/urban-reign/tools/ur_tail_census.py` (stdlib only).
Full machine-readable results: `char001-tail-census.json` (same folder).
Reproduce: `ur_tail_census.py <char001.ppk> <dvd000_afs_map.json> <outdir>`
(also writes the extracted `<name>_tail.bin` there; the .bin is a
regenerable intermediate and is not committed).

## Source verification (against the AFS, not trust)

| Check | Value |
|---|---|
| AFS entry | `afs/safe/ppk/char001.ppk`, afs_off 1032468480, size 776960 |
| Local copies | `ur-decode/work`, `ur-texture/work`, `ur-texcrack/work` — all 776960 B, all MD5 `c97d831572d3e51c7295a3f9eeb6a32a` (identical) |
| Census copy SHA256 | in JSON (`sha256` field) |
| PPK header | magic `ppk\0` OK; total field 776952 (= size − 8); data-offset field 128 |
| Tail identity | tag table at 0x20 → type `0x0002` @ **0xE800**, size **717568** (= EOF − 0xE800), tail SHA256 in JSON |

## What the tail actually is (measured)

1. **Head = proven vertex-record framing, not packets.** 3,615 ×
   `128.0×4` float separators; record lengths concentrate exactly on the
   phase-1 vertex grammar (12 floats ×1,774; 20 ×1,414; 28 ×132 —
   1/2/3-influence vertex records + UV row). Vertex region:
   0xE800–0x56600. VIF CMD-position bytes there are IEEE-754 exponent
   bytes (0x43 ×13,948; 0x3F ×13,219; 0x3E ×9,428; 0x3D ×7,517;
   0xBD/0xBE/0xBC negatives) — float payload, not opcodes.
2. **Post-vertex region = 423,168 B (0x56600–EOF), a mosaic, not a
   stream.** 4 KiB segmentation (176 blocks): structured ×105,
   high-entropy ×42, zero-heavy ×29, interleaved along the whole region
   (full segment table in JSON). It opens with float records carrying
   incrementing pointer-like u32 words (0x00086298, 0x000862A4,
   0x000862AF, …) — descriptor/table-shaped, not packet-shaped.
   It contains 25 monotonic u16 ramp runs (≥64 long, e.g. 403 × step-15
   at 0x869A4) — structured tables. Mesh markers u32 `0x00008004` ×607
   and `0x00008014` ×228 occur across the tail.
3. **VIF: no sync anywhere.** Strict VIF walks (NOP/STCYCL/…/MSCAL
   family/MPG/DIRECT/DIRECTHL/UNPACK with documented lengths) from 14
   candidate starts (tail start, post-vertex start, 12 segment starts):
   11 die on the **first word** (e.g. tail start word `0x43000000` =
   float 128.0, CMD byte 0x43 invalid; post-vertex start CMD 0xB3
   invalid). The three non-zero runs (2,736 B / 2,672 B / 28 B) are
   NOP/STCYCL-shaped words inside zero-heavy pads — zero bytes walk as
   NOPs; they end at the first real payload word. **Zero DIRECT
   packets were ever framed, so zero GIF payloads were ever reached.**
4. **GIF: no framed register writes of any texture kind.** Naive
   GIFtag-shape matches flood (18,812 qwords fit NLOOP>0/FLG≤2 — a
   false-positive metric in float/record data). The discriminating
   test is the PACKED A+D scan: qword-aligned A+D-shaped qwords total
   1,535, breaking down as **PRIM ×1,533 + RGBAQ ×2 — TEX0_1 ×0,
   TEX0_2 ×0, BITBLTBUF ×0, TRXPOS ×0, TRXREG ×0, TRXDIR ×0**. (PRIM
   "hits" are zero/run-shaped qwords: an A+D PRIM write and a zero pad
   are bit-identical when data=0; the non-zero ones sit at record
   stride inside tables, e.g. the 0x574A0 series.) At any alignment
   there are 28,313 A+D-shaped positions spread across **all 16**
   alignment classes (~1,400–5,000 each) — i.e. unframed record
   coincidences, not a qword stream.
5. **TEX0 sightings: ZERO (framed).** Unframed TEX0-value plausibility
   scan over the post-vertex region finds 1,403 loose / 99 strict
   (TW,TH ≥ 5) 64-bit words that merely *decode* as a TEX0 — recorded
   in the JSON as **candidates only**. With no GIF framing anywhere,
   none of them is a sighting, and no texture geometry (TBP0/TBW/PSM/
   dims) can be claimed from this stream.

## Verdict on the Phase-2 §6 hypothesis

Phase 2 §6 said the tail "is ONE interleaved VIF/GIF stream" whose
texture uploads "ride inside it as GIF packets (BITBLTBUF/TEX0 +
image data)", and named the route: VIF/GIF walker → virtual GS memory
→ deswizzle from stream-declared TEX0. **That framing is not supported
by the bytes at any tested alignment or start offset.** The §6
entropy observation itself was real (structured regions, then
high-entropy candidate payload ≈ 90 KB: this census measures 42
high-entropy 4 KiB blocks ≈ 172 KB scattered through the post-vertex
mosaic), but entropy cannot declare a packet format, and every
packet-level test fails. Recording this as a proven negative so the
next attempt does not re-walk the same ground.

## What this does NOT rule out (named next tests, in order)

1. **DMA-tagged VIF**: a stored DMA chain (CNT/REF/CALL/RET tags)
   wrapping VIF/GIF payloads would defeat a raw VIF walk.
   **TESTED (this census, `dma_chain_probe`): NEGATIVE.** All 26,447
   qword-aligned starts in the post-vertex region were chain-walked
   (CNT-following): longest chain anywhere = 5 steps; 277 starts reach
   ≥3 steps scattered as chance coincidences; the ID histogram over
   QWC-plausible qwords is near-uniform across all 8 DMA IDs (random
   signature). No anchored DMA chain exists in this region.
2. **Loader-built uploads**: the post-vertex descriptor records
   (float rows + incrementing pointer words at 0x56600+) may be the
   game's own texture/material descriptors, with GS uploads built by
   SLUS_212.09 code at load time. Next test: Ghidra trace of the
   PPK chunk-type-`0x0002` consumer in SLUS_212.09 (MD5
   `0fa29bd55638f9ebe49feb494d4decd5`; Ghidra at
   `~/workspace/tools/ghidra/`).
3. **Payload-without-TEX0**: the high-entropy blocks may still be
   pixel payloads whose TEX0 lives in code/descriptors (test 2
   decides their PSM/dims). Do NOT deswizzle-guess them before that.
4. **Textures outside char PPKs**: the DVD000 AFS census (2,431
   entries) contains no texture-named archive; stage/mission PPKs use
   the same container and remain untested for texture chunks.

## Research / pull-in notes (Job 1, first pass)

- **Formats**: EE User's Manual VIF code table and GS User's Manual
  GIFtag / A+D / TEX0 layouts, as encoded in the census tool (facts,
  no code copied). Cross-checked against the Linux kernel's
  `gif_tag` struct (NREG field 0 = 16 registers; A+D = data u64 +
  addr byte) and the RenderWare PS2 whitepaper's worked UNPACK
  example (`0x64040000` = UNPACK V2-32, NUM=4).
- **PCSX2 GS-dump tooling**: operates on emulator-captured GS dumps,
  not on file-native PPK data — useful only if a live PCSX2 capture
  lane is run; not pulled in (no dump exists in this lane's sources).
- **GS deswizzle**: the phase-1 lane already extracted PSMT8
  block/column tables from urban-reign-recomp's `ps2_gs_memory.cpp`
  into `ur-texcrack/work/deswizzle8.py` (recon dir, verified present
  this attempt). It stays the deswizzle candidate for step 3 of the
  §6 route IF a TEX0 source is ever proven; copying it into
  `teardown/urban-reign/tools/` is deferred until a framed TEX0 or a
  code-proven PSM exists — pulling it in now would wire a decoder to
  parameters nobody has proven.
- **Namco-PS2 texture research**: phase-1 worklogs (repo docs
  `URBAN-REIGN-TEXTURE-CRACK-2026-10-19.md`, issue #306) stand: no
  TIM2 signatures in char001, no texture-named AFS entries, standard
  PSMT8/4 tests on candidate regions produced noise. This census adds
  the packet-level negative above.
