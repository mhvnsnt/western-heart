# Tekken 6 PSP — ROUND 8 JOB 1 (interim): NDPP interior map from clean bytes

Date: 2026-10-21, round 8. Inputs: verified clean `decoded76/`
(retained workdir `~/workspace/_t6r4-work/`). Scripts: lane scratch
`/tmp/t6r8/an*.py` (analysis), Ghidra project `/tmp/t6r8/ghidraproj`.
This doc is the arithmetic cross-check for the Ghidra loader pass;
no vertex layout is claimed proven here.

## Descriptor re-read (corrects the round-7 grouping)

Descriptor = 20B header + 2x64B records. Record floats, in order:
`[y_center, z_center, f2, xmin, xmax, ymin, ymax, zmin, zmax,
ymax_copy, 0, 0]` + 4 words. Proven by arithmetic on 4 sections:
y_center == (ymin+ymax)/2 and z_center == (zmin+zmax)/2 exactly
(idx00 body: 1782.12 / 34.49; idx00 head: 1011.03 / 14.87;
idx04 slot0: 1115.28 / 9.68; idx04 head: 903.73 / 373.77).
`f2` is NOT the half-diagonal (body 154.88 vs 191.5 computed) —
unresolved. Word after the 2 records (offset 148): body 3120,
head 16832 (== section_size-192), idx04 slot0 416 — NOT a plain
vertex count; likely a size/offset field. Round-7's "count word
3120 anchor" is therefore a size-like field, not a count.

## Section interior: three region types (idx00 body, 78,560 B)

1. **144-byte blocks** from offset 152: 16B zeros + ~112B of
   near-unit floats (norms 0.89-0.95, mostly +Y) + 16B trailer
   containing words (2832, 2784, 0x11000000, 0x10100, 4192+).
   17 trailers (`0x11000000` at stride exactly 144), then the
   pattern breaks. Head/small sections have NO such blocks.
2. **Byte-sparse region** (~2828-3250 in body): sparse nonzero
   bytes at word-tail positions (sequences e7,e8,e9 / de,df,e0,e1
   / c6,c7,c8,c9 — signed-byte runs), ending in a float 1.0 word
   (`00 80 3f d0` region) — encoding unresolved.
3. **Submesh units** (the bulk, ~3250-EOF): repeating unit =
   table of 8-byte records + packed vertex stream, terminated by
   the 8-byte marker `00 00 00 13 00 00 00 0b` (176 markers in
   body, 46 in head, 48 in idx04 head, 1 in idx04 slot0).
   - Record = `(u32 0x01000000 + offset, u32 0x0404xxxx)`:
     offsets strictly increase within a unit; the low byte of
     word1 varies per record (4..15).
   - Offset deltas vs word1 low byte: in the 9540 table most
     deltas == 14 x low_byte; in the 3252 table all deltas are
     108 with low_byte 9 (108 == 12 x 9). Hypothesis: low_byte =
     vertex count of a strip, delta = count x stride, and the
     STRIDE VARIES PER UNIT (12 vs 14 seen) — i.e. per-submesh
     vertex formats, GU-style. The `04 04`/`03 04` tail bytes are
     format-code candidates.
   - Packed stream: byte-position entropy scan over the first
     stream (3324-4360) gives a decisive stride-12 phase-0 win
     (avg per-position entropy 3.70 vs ~5.0 for neighbours;
     stride 24 also low as 2x12). Column signatures at stride
     12: pos0 ~0x80 (72/86), pos1 ~0xbf, pos2 ~0x80,
     pos7 in {1,2}, pos9 in {0x76,0x77,0x78}, pos11 in {6,7}.
     Bytes (10,11) as LE u16 give ~1929, 1906, 1903... — the
     descriptor ymax for this package is 1906.49, so a
     coordinate channel near the bbox max is present in the
     stream; exact packing (fixed-point scale / split bytes)
     is what the loader must confirm.

## What this rules in / out

- Positions are NOT plain float3 (round-7 cell map) and NOT a
  single fixed stride for the whole section: per-unit tables
  with count x stride deltas say the loader walks units,
  reading a format/stride per unit — consistent with PSP GU
  vertex-type switching per draw call.
- The `0x13`/`0x0b` marker pair and the `0x01000000+offset`
  table word are the loader-recognition anchors to search for
  in the EBOOT (immediates 0x13 / 0x0b / 0x01000000, and the
  BONE-template consumers for the skinning side).

## Next (in progress)

Ghidra headless import of EBOOT.DECRYPTED.ELF (MIPS LE) —
decompile NTPP ctor @0x0892fdf0 neighbourhood, BONE template
@0x08bdaab0 consumers, and functions comparing against the
unit marker / table-word constants above.
