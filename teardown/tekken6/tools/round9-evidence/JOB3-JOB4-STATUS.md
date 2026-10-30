# Tekken 6 PSP — ROUND 9 JOB 3 (B2 NTPP) + JOB 4 (B5 stage): status

Date: 2026-10-21, round 9. Jobs 1–2 consumed the lane's main
effort (both landed, proven). These two are reported honestly
at the depth reached — no guessed pixel formats, no faked stage
geometry.

## JOB 3 (B2) — NTPP interior MAPPED, pixel format NOT decoded

Byte-exact map of idx02 slot-0 NTPP section (5,360 B), a
type-B package (6 slots, 64 B header):

- Section header (matches the round-8 ELF template fields):
  `NTPP`, flags `0x00020001`, 0, 0, **0xc50**, **0x400**,
  **0x800**, `0x01000050`, `0x85030100` (template: `0x84030100`
  — top byte varies 0x84/0x85), `0x00400020`, then zeros to +64.
- **+16 field = size of the first texture block**: 0xc50 =
  3,152 = offset of the second block (3,232) − block start (80).
- Texture blocks start at +80: sub-chunk header `GIDX`,
  u32 0x10 (header size), u32 format word, u32 0; then data.
  - Block 1 @+80: GIDX word `0x10400612`, data 3,136 B.
  - Block 2 @+3232: GIDX word `0x10400610`, data 2,112 B
    (starts with zero padding). Section ends at 5,360.
- Data-size split candidates (arithmetic only): block1
  3,072 + 64, block2 2,048 + 64 (a 16-entry × 4 B CLUT would
  fit the +64, and 2,048 = the section's +24 field) — but the
  bytes at the block head are image-like data, NOT a palette
  (rendered candidate palettes are grey noise), and the byte
  distribution (255 distinct values, 0xff ×259 in block 1)
  does not confirm CLUT8 either. Two 4bpp renders attempted
  and rejected as unproven — NOT shipped.
- Pairing/baking: NOT done (no proven image, and per the
  brief unprovable pairings stay unshipped).

Exact next step (unchanged from round 8, still the right one):
decompile the NTPP-class methods `FUN_0892f99c / FUN_0892fac0 /
FUN_0892f6c4 / FUN_08930440 / FUN_089304a4` — with a
capped-heap Ghidra run (this round's full import was
OOM-killed; a `-noanalysis` import + targeted decompile of
those five functions fits the VM) or a PPSSPP GE texture dump
for ground truth. The GIDX word (`0x104006xx`: shared bytes
06 40 10, last byte 0x10/0x12 varies per block) is the format
carrier to trace.

## JOB 4 (B5) — stage slot-9 head map RE-VERIFIED, layout not decoded

idx24 (stage package): slot 9 @ file 4,064, 88,768 B. BE head
words re-read this round: `00000002 00000020 00000040 00000060
00015a60 00000000 00000000 00000000` — the 0x20-stepping BE
offset table and `0x15a60` = 88,704 = payload − 64, exactly as
round 8 seeded. No stage GLB (layout decode not attempted —
Jobs 1–3 took the lane). Note: stage packages' slot-0 NDPP
(624 B on idx24) does not parse with the character-package
unit scanner; stage NDPP variants are part of B5's remaining
scope.
