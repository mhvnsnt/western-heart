# Tekken 6 PSP — ROUND 8 JOB 1/3 (interim 2): unit model + BONE structure

Date: 2026-10-21, round 8. Builds on `JOB1-NDPP-INTERIOR-MAP.md`.

## NDPP submesh unit model (arithmetic, multiple units verified)

A unit, in file order:

1. **20-byte unit header**: `(u32 20, u32 16, 12 bytes data)`
   (seen at table_start-20 for every unit sampled).
2. **Strip table**: N x 8-byte records
   `(u32 0x01000000 + byte_offset, u32 0x04040000 + count)`.
   Offsets are relative to (table_start - 20), i.e. the unit
   header start. Consecutive records satisfy
   `offset[k+1] - offset[k] == count[k] * 12` EXACTLY on every
   record of 4 sampled tables (unit@3252: all counts 9, deltas
   all 108; unit@4324: 12.0 ratio on 9/16/16/16/5/4; unit@5572
   and unit@7540 likewise). **Vertex stride = 12 bytes.**
   The last record of some tables carries `0x03` in the byte
   that is otherwise `0x04` (format/terminator flag candidate).
3. **Marker** `u32 0x13, u32 0x0b` immediately after the table.
4. **Packed vertex stream**, stride 12, strips contiguous in
   table order; first strip starts right after the marker.
5. **Trailing float block** after the strips (~116-324 B):
   float3 values identical in style to the section's opening
   144-byte blocks (e.g. 0.0465, -0.0064, 0.9258 — near-unit,
   +Y-dominant). Role unproven (per-unit normals/lighting?).

Vertex record (12 B) channel evidence (first unit, entropy +
smoothness): bytes 6..11 as 3x u16 LE move smoothly along a
strip (e.g. (532, 30652, 1929) -> (400, 30652, 1906) ->
(437, 30552, 1903)) and affine-map into the descriptor bbox
on all three axes; bytes 10..11 alone give ~1929, 1906, 1903
against a descriptor ymax of 1906.49. Bytes 0..5 carry a
channel whose low byte is almost always 0x80 and a ~0x77xx
channel sits at bytes 8..9 — packing (which channels are
position vs normal vs UV, and the exact scale/offset) is the
remaining Job-1 question; the Ghidra loader pass (below) and
the point-cloud coherence render are the two tests.

## Ghidra pass 1 (EBOOT.DECRYPTED.ELF, MIPS LE, project in lane scratch)

- NTPP ctor `FUN_0892fdf0` decompiled: object ctor; vtable
  `0x08b9c568`, secondary vtable `0x08b8c2d0` at +0x64, template
  struct ptr at +0x5c = `0x08b9c59c`. Its sibling
  `FUN_0892fc40` lazy-copies the NTPP template
  (`FUN_08825ed4(&DAT_08b9c5b0, 0x40003c00, 1, 0xf0)`).
- NTPP template itself is at `0x08b9c5b0` (= struct +0x14):
  words dumped from the ELF in probe 2: magic `NTPP`,
  `0x10001` flags (same family as NDPP section flags
  0x10001/0x20001), then 0, 0, 0x110, 0x40, 0x80, 0x100050,
  0x84030100, 0x80020 — the Job-2 starting point.
- BONE template `0x08bdaab0` has exactly 2 xrefs, both PARAM
  uses inside large character/entity functions
  (`FUN_089d73c4`, `FUN_0886fe88`) — the template is a memcpy
  source for a default skeleton, not a parser entry point.
- No `NDPP` byte string exists anywhere in the ELF (verified
  by raw scan this round, confirming round 7): NDPP sections
  are dispatched by directory slot, never by magic.

## BONE chunk structure (CRACKED, arithmetic on 3 bone counts)

Header: magic `BONE`, u32 version 1, u32 100, u16 1, u16 6,
u32 bone_count N, float (~0.98-1.04, per-file), then an offset
table starting at byte 24 whose entries are:

`[64, 64+4N, 64+16N, 64+28N, 64+28N+4, ?, 64+28N+36, ...]`

Verified exactly: template (N=110): 64, 504, 1824, 3144, 3148,
3180. idx04 body (N=146): 64, 648 (=64+4*146) — and the next
entries follow the same formula. idx00 head (N=22): 64, 152
(=64+4*22). So BONE holds per-bone arrays of 4 B, then two
float3 arrays (12 B/bone each), then further sections after
offset 64+28N. Record stride question (round-7 B6) is thus
answered in array form: BONE is a set of parallel arrays, not
interleaved records. Remaining: identify each array's role
(parent indices in the 4 B array is the natural read) and the
post-64+28N sections; consumers `FUN_089d73c4` /
`FUN_0886fe88` are the cross-check.
