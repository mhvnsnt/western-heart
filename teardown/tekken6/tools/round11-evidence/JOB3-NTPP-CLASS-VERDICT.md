# Tekken 6 PSP — ROUND 11 JOB 3 (NTPP): the NTPP class is fully read — it contains NO pixel path; item decode under code-derived parameters is impossible from this class

Date: 2026-10-22, round 11. Disassemblies (Capstone via the
round-9 `t6dis.py`, word-exact) in `round11-evidence/dis/`:
`dis_0892f99c.txt`, `dis_0892fac0.txt`, `dis_0892f6c4.txt`,
`dis_08930440.txt`, `dis_089304a4.txt`, `dis_0892fdf0.txt`.

## (a) What the five named methods + ctor actually are

The class IS named NTPP — the RTTI/type record at **0x08b9c5b0**
carries the name string "NTPP" with pointers to this class's
thunk (0x08930498) and method (0x08930434), and its vtable at
**0x08b9c568** contains exactly: [3] 0x089304a4, [4] 0x08930440
(the two ctors), [6] 0x0892f99c, [8] 0x0892fac0, [9] 0x0892f6c4,
[13] 0x08930498 (this−0x5c thunk), [14] 0x08930434, over shared
base entries. The named set is the COMPLETE class. But the
class is a small texture placement/animation OBJECT, not a
pixel decoder:

- **FUN_0892fdf0 (ctor)**: installs vtables 0x08b9c568 (@+0)
  and 0x08b9c59c (@+0x5c), zeroes +0x64..+0x77 fields, masks
  the flag word +0x44 against a global (~mask at 0x08b8fc24),
  sets **+0x98 = 1** and **+0x9c = 110.0f** (0x42dc0000).
- **FUN_08930440 / FUN_089304a4**: alternate ctor variants
  installing the same two vtables and chaining a base ctor
  (0x885f3e0) on the +0x64 sub-object.
- **FUN_0892f99c**: state/flag update — reads the state word
  +0x4c; on state 1 it adds the floats at +0x88/+0x8c, moves
  state to +0x84, and masks +0x44 with the same global mask.
  Float/timer bookkeeping.
- **FUN_0892fac0**: float computation over +0x98/+0x9c against
  constants 640.0 / 22.5 / 60.0 / 0.0078125 (lui immediates
  0x4420 / 0x41b4 / 0x4270 / 0x3d00) — a normalized progress /
  coordinate computation (the +0x98/+0x9c pair reads as
  (count, range) with default (1, 110.0)).
- **FUN_0892f6c4** region: a predicate comparing the float
  argument $f12 against a rodata constant (0x08be113c) through
  a global object chain (0x08c0daf0 → +0x2ac → +0x84), and an
  init method at 0x0892f708 writing the same defaults
  (+0x98 = 1, +0x9c = 110.0f, +0x7c/+0x4c/+0x88..+0xb0 zeroed).

Object layout (all six functions agree): +0x44 flags, +0x4c
state, +0x5c secondary vtable, +0x64 sub-object, +0x7c, +0x84,
+0x88/+0x8c float pair, +0x98/+0x9c (int, float), +0xb0.

## Pixel-path facts (the brief's question) — NONE EXIST in this class

Across all six functions: **no byte or nibble manipulation
loops, no swizzle address arithmetic, no CLUT indexing, no GE
texture-command construction (no 0xC0–0xE9 command words), no
calls to GE/display submit functions.** Incidental-match grep
over the six disassemblies: `lbu`/`sb`/`andi 0xf`-class hits =
1 / 1 / 9 (all in flag/test code in FUN_0892f6c4's region) /
0 / 0 / — none in a data loop. The swizzle/CLUT/format
constants the brief asked to extract are not present because
the pixel path is not in this class.

Consequence for (b): **the prescribed test — decode one slot-4
item using ONLY code-derived parameters — cannot be run**: the
NTPP class yields no pixel parameters at all (no width, no
format, no CLUT location, no swizzle flag). Running another
blind variant sweep is exactly what the brief forbids and what
round 10 already exhausted on block 1. No textured GLBs.

## What the slot-4 items measurably are (statistics, as briefed)

- idx02 slot 4 (70,880 B) opens with count 42 + header size
  0x160, then directory records (round-10 map). The item at
  slot4+0x160 is itself an **embedded NTPP section**: magic
  `NTPP`, version 1, then header words 4, 0x30, and word pairs
  (0x4060, 0x4090), (0x4060, 0x80f0), (0x4060, 0xc150) — a
  u16-pair directory shape ((0x60,0x40),(0x90,0x40),(0xf0,0x80),
  (0x50,0xc1)…) recorded here uninterpreted.
- Item byte statistics: entropy 5.51 bits/byte, 9.9% zero
  bytes, 109 distinct byte values — DENSE data (contrast the
  B5 stage pages at 80% zeros). Consistent with encoded/
  compressed pixel data, not with any raw CLUT layout at the
  geometries arithmetic allows (round 10).

## Exact residual

The file-format NTPP sections are consumed by the game's
generic data/texture layer — RTTI places a
`tcb_datatextureroot_t` type at 0x08b94044 — and the GE texture
upload must happen in the render library, keyed off the GIDX /
section-header fields (rounds 9–10 mapped those byte-exact).
The next code step is the datatextureroot class's load path
and its GE texture-command emission (0xC0–0xE9 family), NOT
the NTPP placement class above. Until a pixel format is
proven there, textures stay unbaked (textures-baked-in gate
upheld by not baking).
