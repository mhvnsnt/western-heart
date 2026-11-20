# Tekken 6 PSP — ROUND 10 JOB 3 (NTPP pixels) + JOB 5 (stage slot-9): status

Date: 2026-10-22, round 10. Both jobs advanced one proven
level and stop at honest residuals — no guessed pixel formats,
no faked stage geometry.

## JOB 3 (B2) — GIDX "format word" IDENTIFIED as chunk tag + serial; pixels NOT decoded

New this round (byte-proven across all top-76 NTPP packages):

- The `0x1040xxxx` word in GIDX blocks is NOT a pixel-format
  word. Its low 16 bits are a per-chunk serial: idx06's three
  blocks carry 0x0121, 0x0122, 0x0123 in order; 17 packages
  share 0x0ba3; the same word family heads the NDPP per-unit
  bbox blocks (0x1040059d…) and the stage slot-9 embedded NTPP.
  It is the file format's generic chunk tag (0x1040) + ID.
  The round-8/9 hunt for a format in this word was chasing a
  serial number — the pixel format lives elsewhere (NTPP
  section header fields and/or the slot-4 directory records).
- NTPP package layout (idx02, complete): slot0 NTPP section
  5,360 B (GIDX blocks), slots 1–3 = 352 B sub-headers
  (u32 42 then (0, 0x160) pairs — a 42-entry table stub),
  **slot4 = 70,880 B payload**: a directory headed
  (42, 0x160) followed by (type 0x10, offset, size 0x460)
  records stepping 0x470 — 1,120 B items (the 1,136 B-spaced
  NTPP sub-entries round 7 saw in the slice). Slot5 = 256 B
  NTPP trailer (single GIDX block, tag 0x104005ba).
- Decode attempts on idx02 slot0 block 1 (3,136 B data;
  arithmetic fits 16 B header + 64 B CLUT + 3,072 B pixels):
  4bpp CLUT16 at 128×48, CLUT at data head and tail, CLUT
  RGBA8888 and RGBA5551, both nibble orders, linear and PSP
  block-unswizzled — 16 variants rendered and VIEWED: all
  noise (contact sheets kept in the lane scratch, not
  shipped). The block data may be a mip/descriptor stream
  rather than pixels; slot4's 1,120 B items are the untested
  pixel candidates.
- Pairing/baking: NOT done. No proven image → no textured
  GLBs (textures-baked-in law). Pairing evidence stands from
  round 7 (entry-order interleave: character A-package and
  B-texture package share entry numbers, e.g. idx00/idx01 =
  entry 454/457 A-parts with idx02 = entry 457 B-part) but is
  NOT exercised until a pixel decode proves out.

Exact next step: decode one slot-4 item (1,120 B: 16 B header
+ 1,104 B? = e.g. 64×34 @4bpp + CLUT, or 32×34 @8bpp…) with
the same variant matrix, and/or the capped-heap targeted
decompile of FUN_0892f99c / FUN_0892fac0 / FUN_0892f6c4 /
FUN_08930440 / FUN_089304a4 (still the code route of record).

## JOB 5 (B5) — idx24 slot-9 layout pushed one level: page directory + embedded NTPP

idx24 slot 9 (88,768 B, big-endian control stream):

- Head = BE directory of 0x20 B records: [count 2, 0x20,
  0x40, 0x60, payload−64 = 0x15a60, 0, 0, 0], then records
  [2, 0x20, 0x10, 0x30, 0x10, 0…], [1, 0x10, 0, 0],
  [1, 0x10, 0x15a50, 0, 0x28, 0x150, …].
- At +0x78: a page table of **40 × (size 0x8a0, offset) BE
  pairs**, offsets stepping exactly 0x8a0 from 0x9f0;
  40 × 0x8a0 = 88,320 = payload − 448: the pages tile the
  payload to EOF after a 448 B head region.
- At +0x1c0 (inside the head region): an embedded `NTPP`
  section magic — the stage payload carries its own texture
  section, consistent with the stage/object class.
- Page at 0x9f0: 60 B zero head, then data; the payload is
  95% big-endian-float-sane (|v| < 1e6 test) — a BE float
  geometry stream, a different encoding family from the LE
  NDPP character sections.

Residual (exact): the per-page record format (vertex stride /
index scheme inside the BE float stream) is not yet decoded,
so no stage GLB is shipped. Stage slot-0 (624 B) re-confirmed
as a transform node, not geometry: NDPP header + descriptor
floats with quaternion-like values (0.707, ±0.5) — it decodes
as placement data only. Slot 7 (2,384 B) = u32 table headed
(0x14, 0xb0, 0x8a0, 0x950) with 0x950-stride pair records;
slot 8 (896 B) = BE directory headed (5, 0x30, 0xe0, 0x110,
0x30, 0x140…) — same BE directory family as slot 9.
