# Tekken 6 PSP — ROUND 12 JOB 1 (PALETTE): the registry trace is CLOSED; the caller is an inlined builder in the same object class — index rule PROVEN at the library layer; unit→bone selection is game-side and stays CAPTURE-ONLY

Date: 2026-10-22, round 12. Disassemblies (Capstone, VFPU-tolerant)
in `round12-evidence/dis/`: `dis_08ad1890_builder.txt`,
`dis_08ad161c_1724_emitters.txt`, `dis_08ad1490_via_cell.txt`.
Registry dump script: `round12-evidence/j1_registry_dump.py`.
EBOOT: `~/workspace/_t6r4-work/ghidra-r9/EBOOT.DECRYPTED.ELF`
(vaddr = file offset + 0x08803000).

## The registry zone, dumped in full (0x08bcfc00–0x08bcff00)

It is NOT one table. At 4-byte word granularity it holds, in order:

1. **Switch jump tables** (from ~0x08bcf800): dense code-pointer
   runs for the 0x08acxxxx dispatcher library; the table base
   0x08bcfc88 is referenced by lui/addiu from 0x08ac12dc,
   0x08acf26c, 0x08acf498, 0x08acf9c0, 0x08acf9dc.
2. **Default-filled pointer arrays** (0x08bcfd00–0x08bcfdbc):
   ~50 words of 0x08b60054 (a shared stub) with zero gaps.
3. **Two indirection cells**: word at **0x08bcfdc8 = 0x08ad1614**
   and word at **0x08bcfde8 = 0x08ad160c** — the ONLY two
   0x08adxxxx values in the whole zone. Both are 8-byte thunks:
   0x08ad160c: `j 0x08acfa5c; move $a0,$a1` and
   0x08ad1614: `j 0x08acfbc0; move $a0,$a1`.
4. **The identity template at 0x08bcfdf0** (0x2A000000 BOFS +
   identity 0x2B rows), immediately after the second cell.

**(a) Which entry references the emitter @0x08ad161c? NONE.**
Exhaustive negative, all mechanisms checked over the whole EBOOT:
no data word equals 0x08ad161c; no `jal`/`j` target; no branch
target; no lui/addiu pair computing it; no lui+lw [base+0x161c];
no relocation addend (value−0x08803000 or −0x08800000) anywhere.
The same exhaustive negative holds for the builder @0x08ad1890
and the second emitter @0x08ad1724. These functions have NO
static caller of any kind in this ELF — they are reached only
through the owning object's vtable, whose pointer words are not
present in the static image (the class is instantiated outside
this ELF's static data; the two cells above are the visible,
mutable part of that dispatch: function-pointer variables
initialised to the thunks).

**The cells' actual consumers (read, not guessed):**
- Cell @0x08bcfde8 is consumed by the method @0x08ad1490
  (`dis_08ad1490_via_cell.txt`): it walks the intrusive list at
  obj+0x410/+0x414 (guard: obj+0x424), loads the cell's value
  (the 0x08ad160c thunk), and `jalr`s it per node with
  $a1 = node->[8]. A list for-each destructor/visitor — the
  emitter's own object class (same +0x410/+0x418/+0x424 layout
  as the builder below), but a container callback, NOT a
  fragment caller.
- Cell @0x08bcfdc8 is referenced at 0x08ad08f8, in the same
  library's container code (thunk → 0x08acfbc0).
- The template @0x08bcfdf0 is consumed at 0x08ad1854 by a small
  node-builder (@~0x08ad1850, tail of the @0x08ad17e0 function):
  it emits GE words 0x10400000-masked and 0x0A000000 |
  (template & 0xFFFFFF) — a display-list node that points at
  the identity fragment (the unskinned/default draw).

## (b) The caller — it is INLINED, at 0x08ad1890

The brief's target shape ("a function that LOOPS and calls
through a register with an index argument") does not exist for
this emitter because the compiler inlined it. The builder
**@0x08ad1890** (`dis_08ad1890_builder.txt`) is a method of the
same object class, and its main loop (0x08ad199c–0x08ad1ab0)
contains the emitter body VERBATIM — identical instruction
sequence to 0x08ad161c, including the obj+0x418 computation —
with the index as its loop counter:

- Entry: count_hi = byte @obj+0x41f, count_lo = byte
  @obj+0x41e. If count_hi < count_lo → clear path (memset
  obj+0x18, 0x400 B = 256 pointers, via 0x8b7a3bc).
- Fragment storage is bump-allocated from a global cursor at
  0x08c466c0+0x18 (cursor −= count×52); per-fragment pointers
  are stored to the pointer table at **obj+0x18[i]** (stride 4).
- **Path A** (byte @obj+0x41d == 0), loop i = 0…count_hi−1:
  element = obj->[0] + i×48 (sll6−sll4); VFPU-load the 3×4
  matrix (ldc2 at +1/+0x11/+0x21); emit 12× 0x2B + 0x0B at
  out+0x30; out += 0x34 (52). **The standalone emitter
  @0x08ad161c is this path's leaf twin** (same 48 B stride).
- **Path B** (byte @obj+0x41d != 0), loop at 0x08ad1b30: same
  loop over 64 B-stride elements (i×64), reading a 3×3 from
  16 B-stride rows (9× 0x2B), then the shared translation
  computation at 0x08ad1ac4 writes out+0x24/+0x28 + 0x0B.
  **The standalone emitter @0x08ad1724 is this path's leaf
  twin** (index<<6 source stride).
- A second, unrelated emitter family exists at 0x08aac794+
  (global pool at 0x08c3bf00, index×52, commands 0x3B/0x2B —
  world/bone matrix upload helpers of another library page);
  it has no obj+0x418 logic and is not the per-object path.

### The index rule (PROVEN at this layer)

**Fragment i ↔ pose-matrix i, sequentially, with no index
table anywhere**: the builder iterates the object's own matrix
array at obj->[0] in order and writes fragment i for matrix i,
recording its pointer at obj+0x18[i]. Indices below count_lo
(byte @obj+0x41e) are zero-filled in the pointer table first
(the loops at 0x08ad1908–0x08ad1980). Count is capped at 256
(sltiu 0x100). This kills the "per-part bone-index table"
hypothesis at the library layer: there is no table; the index
IS the ordinal in the object's pose array.

### The obj+0x418 extra computation (read exactly)

In all four copies (emit @161c, emit2 @1724, builder paths A/B)
the elements stored at out+0x24 / out+0x28 — the translation
row's first two components — are NOT copied from the source
matrix. They are produced by two VFPU words (0x60999b1a,
0x657a9a1b) combining (i) a matrix loaded with ldc2 from
**obj->[1]** (the object's second pointer field) and (ii) a
vector loaded with lwc2 from **obj+0x418+3**, while the third
component (out+0x2c) IS copied raw from the source element.
Reading: the fragment's translation is composed at build time
from the object's obj->[1] matrix and its +0x418 field (the
object's world/parent transform), i.e. fragments are built in
world-composed form, not raw local pose form. (Stated at
instruction precision; the VFPU ops themselves are not
symbolically decoded — Capstone does not decode this VFPU
group, the operand flow is what is proven.)

## Verdict — palette stays CAPTURE-ONLY for unit→bone, reason narrowed to one hop

What is now PROVEN: the registry trace is closed (no entry
references the emitter; the cells + template consumers are all
identified); the caller exists as the inlined builder
@0x08ad1890; its index rule is sequential identity over the
object's pose array; the obj+0x418 composition is read.

What is still NOT proven — and is the exact reason no skinned
GLBs are shipped: **which pose-array index the game-side NDPP
renderer selects for each NDPP unit when it builds the master
GE list** (the CALL that consumes obj+0x18[k]). That selection
lives in the game model code (the FUN_0886fe88 class, vtable
0x08b918b8), which is outside the registry route this round
was scoped to, and no static xref of any kind connects it to
the builder (exhaustive negative above). The round-11 RAM
ground truth (110 fragments = 110 bones, fragment index ↔ bone
index within the pose array) plus this round's sequential rule
make "unit palette = the bone whose index the renderer stored
for that unit's part object" the only consistent reading — but
the per-unit assignment itself is only observable in a live
GE capture (round 11's route-2 note: versus/practice with a
known package + GE dump). **The static palette hunt is hereby
CLOSED with this trace: palette = CAPTURE-ONLY.** No guessed
skinning was substituted; G3 stays PARTIAL.
