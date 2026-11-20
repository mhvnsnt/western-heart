# Tekken 6 PSP — ROUND 8 JOB 1 VERDICT + remaining jobs status

Date: 2026-10-21, round 8. Evidence docs this round:
`JOB1-NDPP-INTERIOR-MAP.md`, `JOB1-UNIT-MODEL-AND-BONE.md`,
this file. Renders: `renders/r8_cloud_idx00_body_candA.png`
(VIEWED, negative proof — see below).

## JOB 1 (B1) — PARTIAL: unit model + stride PROVEN, 12-byte packing NOT proven

PROVEN this round (arithmetic, multiple units/sections):

- NDPP section = header + descriptor (duplicated 48 B float
  block; `[y_center, z_center, f2, xmin, xmax, ymin, ymax,
  zmin, zmax, ymax, 0, 0]`) + a series of submesh UNITS +
  other streams (float3 streams; one byte-sparse block that is
  BYTE-IDENTICAL across sections — a shared/default block).
- Unit = 20 B header `(20, 16, 12 B data)` + strip table
  (8 B records: `0x01000000+offset`, `0x04040000+count`,
  offsets relative to unit-header start) + marker
  `(u32 0x13, u32 0x0b)` + packed vertex stream.
  `offset[k+1]-offset[k] == count[k]*12` on every record
  sampled across 4 tables in 2 sections → **stride 12 B**,
  strips contiguous, first strip right after the marker.
- Small-section complete map (idx04 slot0, 896 B, 1 unit,
  6 strips x 4 verts): header/descs 0-175, float3 stream
  176-271 (near-unit vectors, component-permuted — a rotation/
  direction set), u8-ish block 272-287, `(0x54, 0x0b)` word
  pair at 284, zeros, shared byte-sparse block 320-399,
  `(0, 0x0b)` at 400, float3 stream again 416-527 (preceded
  by `(480, 1, 0x180001)`), unit at 528, stream 604-891.

NOT proven — the 12-byte record packing:

- Candidate A (bytes 6..11 = 3x u16 LE affine-mapped to the
  descriptor bbox; bytes 0..5 = s16 normal candidate) was
  rendered as a point cloud over all parsed units of idx00's
  body section (42 units / 116 strips / 685 verts) and VIEWED:
  `renders/r8_cloud_idx00_body_candA.png`. It is NOT a body:
  points pile up on the bbox walls/floor/ceiling — the classic
  signature of a wrong channel mapping (one channel is
  near-constant ~30652 in the first unit and the mapping
  saturates). Candidate A is REFUTED as stated.
- The record's byte alphabet is small and token-like
  (recurring `80 xx`, `3f 7e`, `ff 7f`, `01 6b/87/ae` tokens
  in the small section's stream), consistent with a packed
  fixed-point scheme whose scale/origin comes from data the
  arithmetic pass has not identified (per-unit header 12 B,
  the float3 streams, or the shared byte-sparse block are the
  candidates) — OR with a VFPU unpack in the loader.
- Ghidra pass 1 (this round, project in lane scratch):
  NTPP ctor + sibling decompiled; NTPP template dumped from
  the ELF (Job-2 seed below); BONE template xrefs are memcpy
  defaults inside character/entity ctors (`FUN_0886fe88`,
  `FUN_089d73c4`), not parsers; no `NDPP` string in the ELF
  (raw scan, confirming slot dispatch).
- EXACT remaining asm step (scoped, not vague): decompile the
  model-class vtable methods — the class whose ctor is
  `FUN_0886fe88` (vtable `0x08b918b8`) — and the NTPP-class
  methods `FUN_0892f99c / FUN_0892fac0 / FUN_0892f6c4 /
  FUN_08930440 / FUN_089304a4` for the shared chunk-walker
  pattern; the walker that consumes `(0x13, 0x0b)` unit
  markers and the strip table (`0x01000000`-masked offsets)
  contains the 12-byte unpack (likely VFPU `lv.q`/`vhtfm`
  style transforms given the token-like bytes). Until that
  unpack is read from asm, NO character GLB is shipped —
  shipping the refuted candidate would be faked geometry.

## JOB 2 (B2) — SEEDED, not decoded

NTPP template dumped from the ELF (file offset 3773872,
immediately after the NTPP-class vtable words
`0x08930498 / 0x08930434`): header fields in order —
magic `NTPP`, u32 `0x00010001`, 0, 0, **0x110, 0x40, 0x80,
0x100050, 0x84030100, 0x80020**, then zeros. A second `NTPP`
site (file offset 3983348) sits in a string/struct table
containing the literal `GIDXexT` — GIDX is the PSP texture
index chunk name, tying NTPP payloads to GIDX/CLUT layout.
Interior decode (pixel format from `0x84030100`, CLUT) is the
next lane's Job-2 entry point. No textures baked (no proven
mesh to bake into, and no decoded image yet) — stated, not
hidden.

## JOB 3 (B6+B3) — BONE structure CRACKED (see interim doc 2)

BONE = parallel arrays, not interleaved records: header 20 B
+ float + offset table `[64, 64+4N, 64+16N, 64+28N, ...]`
verified exactly for N=110 (EBOOT template), N=146 (idx04
body), N=22 (head chunks). Remaining: name each array's role
from the consumers, decode the post-`64+28N` sections, and
assemble skeleton JSON/GLB per character package. Skeleton
files NOT shipped this round (array roles unproven — the
4 B array as parent indices is a hypothesis, not yet
cross-checked against the consumers' asm).

## JOB 4 (B5) — SEEDED, not decoded

Stage slot-9 (idx24, 88,768 B) opens with BIG-ENDIAN words:
`00000002 00000020 00000040 00000060 00015a60 00000000 ...`
then `00000002 00000020 00000010 00000030 ...` — a BE offset
table (entries stepping 0x20 = 32 B records; 0x15a60 =
88,704 = payload size - 64) followed by the float stream.
Layout decode not attempted beyond this head map this round.

## JOB 5 (B4) — not attempted (Jobs 1-4 did not all land)

## Bottom line for the sweep

Round 8 moves B1 from "completely unknown interior" to
"unit/strip/stride proven, one 12-byte unpack between here
and the first character GLB", cracks B6's array structure,
and seeds B2/B5 with byte-exact entry points. The first
character GLB remains honestly blocked on the loader unpack.
