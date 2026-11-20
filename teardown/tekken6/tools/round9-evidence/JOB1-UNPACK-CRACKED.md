# Tekken 6 PSP — ROUND 9 JOB 1 (B1′): THE 12-BYTE UNPACK — CRACKED

Date: 2026-10-21, round 9. Decoder: `tools/r9_ndpp_decode.py`.
Proof render: `renders/r9_idx00_slot0_front.png` (VIEWED).
First character GLB: `models/idx00_slot0_r9.glb`.

## The crack: NDPP units are embedded PSP GE display lists

Round 8 read the unit header/strip-table words as plain integers
(`20, 16, …`, `0x01000000+offset`, `0x04040000+count`,
`(0x13, 0x0b)`). Read as **GE command words** (opcode in the top
byte, 24-bit argument) every field resolves:

Unit header (20 B = 5 command words):

| Word (u32 LE value) | GE command | Meaning |
|---|---|---|
| `0x14000000` | 0x14 ORIGIN | arg 0 |
| `0x10000000` | 0x10 REGION1 | arg 0 |
| `0x1200xxxx` | **0x12 VTYPE** | arg = vertex type (below) |
| 2 words | unit data | unresolved (per-unit transform/bone binding candidates; identical for units sharing a strip set, vary across units) |

Strip table (8 B records = 2 command words):

| Word | GE command | Meaning |
|---|---|---|
| `0x01000000 + off` | 0x01 VADDR | vertex-data offset, relative to unit-header start |
| `0x04SS0000 + cnt` | 0x04 PRIM | SS bits 16–18 = primitive type: **4 = triangle strip, 3 = triangle list**; low 16 = vertex count |

Terminator after the table: `0x13000000` (0x13 OFFSETADDR, arg 0)
+ `0x0B000000` (0x0B) — the round-8 "(0x13, 0x0b) marker".

First VADDR offset == 20 + 8×nstrips + 8 (header + table +
terminator) exactly → the vertex stream follows the terminator,
strips contiguous, `offset[k+1] − offset[k] == count[k] × stride`
with the stride **from VTYPE** (this is why round 8 measured
12/14/16 on different units — per-unit vertex formats, GE-style).

## VTYPE argument (bits) — the 12-byte record semantics

GE VTYPE layout: bits 0–1 texture format, bits 2–4 color,
bits 5–6 normal, bits 7–8 position, bits 9–10 weight format,
bits 14–16 = weight count − 1. Field order in memory:
**weights, UV, color, normal, position**; each field aligned
to its component size.

Observed VTYPEs (idx00): body section `0x321`, head section
`0x301`, weight-count field 0–4 in both.

`0x321` decodes: UV = u8×2, normal = s8×3, position = s16×3,
weights = u8 × (1..5). Vertex size for weight count nw:
`nw + 2 + 3 + 6` with the s16 position field 2-byte aligned →
nw=1: **12 B**, nw=2,3: 14 B, nw=4,5: 16 B — matching every
measured strip delta in the section (136/93/100/47/7 samples
by weight-count value 0/1/2/3/4, zero exceptions).

Record layout (VTYPE 0x321, nw=1, stride 12):

| Bytes | Field | Semantics |
|---|---|---|
| 0 | weight | u8, **128 = 1.0** (weights in a record sum to 128 — verified: (128,), (115,13), (64,64), (0,128) are the top tuples) |
| 1–2 | UV | u8 ×2 |
| 3–5 | normal | s8 ×3, unit (all 3,217 body verts: \|n\| ∈ [100,155] ≈ 127) |
| 6–11 | position | s16 ×3 LE, world = raw × ymax/32767 |

`0x301` (head section): same minus the normal field
(stride 10 for nw=2 — matches its strip deltas).

## Position scale: world = raw × (descriptor_ymax / 32767)

Per-section uniform scale, no offset, proven on 4 sections in
2 files (idx00 body + head, idx04 slot0 + head): on every axis
the decoded extremes land on the descriptor bbox within
rounding (worst residual 0.05 world units on idx00 body:
raw [−1551, 1551] → [−90.24, 90.24] vs bbox [−90.26, 90.26];
Y raw max is exactly 32767 in every section). The descriptor
is part of the section header (record at +20), so the decode
is fully byte-grounded: **no affine per-axis remap** (that was
Candidate A's error — it also used a fixed 12 B stride for
all units, scrambling every multi-weight unit's fields).

## Proof gate — PASS

- `models/idx00_slot0_r9.glb`: idx00 slot-0 section decoded:
  3,217 verts / 1,897 triangles; GLB bbox
  [−90.24, 1657.76, −79.89]..[90.24, 1906.49, 148.83] vs
  descriptor bbox [−90.26, 1657.76, −79.87]..[90.26, 1906.49,
  148.85] — match ≤0.03 on all axes.
- `renders/r9_idx00_slot0_front.png` VIEWED by the lane: a
  coherent human **head** — forehead, closed eyes, nose,
  mouth, chin, ears, hairline mass on top; limb-free because
  slot 0 of idx00 is the head section (its world Y 1657–1906
  is the head band of a ~1906-unit-tall character). NOT
  wall-piled; proportions match the section box. This is the
  first proven Tekken 6 PSP character mesh.
- Cross-validation: second file (idx04) sections decode with
  the same code path + per-section scale (see scale table in
  the lane state doc).

## Why the loader hunt resolves this way

The file format hands the GE self-contained display-list
fragments; the hardware unpacks VTYPE vertices — there is no
software 12-byte unpack to find in the vtable methods (the
model-class ctor `FUN_0886fe88` / vtable `0x08b918b8` was
disassembled this round: it builds a character entity with
six 0x18 B sub-objects; its +0x18 vtable method `FUN_0886fc7c`
is a state dispatcher, not a parser). The CPU-side walker's
only job is VADDR relocation (offsets are unit-relative).
Ghidra: the round-9 EBOOT import (workdir
`~/workspace/_t6r4-work/ghidra-r9/`, NOT /tmp) was OOM-killed
during decompiler analysis on this 8 GB VM; the vtable + ctor
were read with the lane's capstone disassembler instead
(`t6dis.py` in the workdir). A capped-heap Ghidra pass over
the GE-list submission path remains a follow-up, not a
blocker: the format contract is proven by the renders above.
