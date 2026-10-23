# Tekken 6 PSP — ROUND 11 JOB 1 (PALETTE): fragment BUILDER found in the EBOOT; per-unit index caller is the exact remaining ambiguity

Date: 2026-10-22, round 11. Disassembly:
`round11-evidence/dis/dis_08ad161c_emitter.txt` (Capstone, via the
round-9 `t6dis.py`); anchors script `round11-evidence/j1_anchors.py`.
EBOOT: `~/workspace/_t6r4-work/ghidra-r9/EBOOT.DECRYPTED.ELF`
(vaddr = file offset + 0x08803000). RAM ground truth: round-5
attract dump `dumps_r5/ram_attract.bin`.

## The builder (PROVEN — byte-exact against the RAM fragments)

Function at **0x08ad161c** is the runtime GE bone-fragment
emitter. Read from the disassembly:

- Signature: `emit(obj=$a0, out=$a1, index=$a2)`.
- Source: `$a3 = obj->[0]` (a base pointer stored in the object's
  first word); the element address is `base + index*48`
  (computed as `(index<<6) − (index<<4)` = 48 B stride — a CPU-side
  3×4 float matrix array).
- It loads the 12 matrix floats with three VFPU quad loads at
  byte offsets +1 / +0x11 / +0x21 from the element (unaligned
  loads: the array elements are 48 B of floats starting 1 byte
  after the stride base).
- Each float is converted to GE imm24 form (`float32 >> 8`,
  via VFPU extract + `srl 8`) and OR'd with `lui 0x2b00`
  → GE word `0x2B000000 | imm24`. Twelve stores land at
  out+0x00 … out+0x2c.
- Final store: `lui $v1, 0x0b00` → **0x0B000000 at out+0x30**.
  Total output = 13 words = **52 B** — byte-for-byte the RAM
  fragment shape (12× 0x2B + 0x0B, 52 B stride) from round 10.
- One complication, recorded exactly: after the first six
  stores, the code computes with `obj+0x418` and `obj->[1]`
  (VFPU ops at 0x08ad16d0–0x08ad16e4) before storing the
  elements at out+0x24 / out+0x28. The third row's leading
  elements therefore pass through an extra computation
  involving a second object field at +0x418 (plausibly a
  world/view matrix held by the same object) — observed, not
  decoded to semantics this round.
- The identity template in the EBOOT image at **0x08bcfdf0**
  (`0x2A000000` BOFS + identity 0x2B rows, dump offset
  0x3cfdf4 in round 10's terms) sits in a registry/table region
  (0x08bcfd00–0x08bcfe00) that also holds function pointers
  0x08ad160c / 0x08ad1614 — tail-thunks of the same 0x08ad1xxx
  library as the emitter. Consistent with the template being
  the library's default fragment / registration data.

## RAM pool check (new measurement)

The attract dump's fragment pool at dump offset 0x15f37dc holds
**exactly 110 consecutive fragments** (52 B stride, ending
0x15f4e34) — the 110-bone skeleton size of the character
packages. The matrices are posed rotations (orthonormal rows,
56 distinct translation triples across 110). Reading: the pool
is ONE character's per-frame bone set — fragment index ↔ bone
index within the skeleton is the pool's organizing principle,
and the emitter's `index` argument is a bone index into the
48 B-stride pose-matrix array.

## The exact remaining ambiguity (why no skinned GLBs)

The emitter takes the bone index as an argument — the palette
rule ("which bone for NDPP unit u") lives in its CALLER, and
the caller was not identified in this pass:

- There is **no `jal` and no data xref to 0x08ad161c anywhere
  in the EBOOT** (full-binary scans, recorded in
  `j1_anchors.py` output): it is reached via `jalr` through a
  class vtable/registry or by fall-through — the same pattern
  as its sibling thunks at 0x08ad160c/0x08ad1614, which are
  referenced only from the 0x08bcfdxx registry table.
- Two candidate index sources remain, not decidable from the
  emitter alone: (a) the unit's ordinal within its NDPP
  section (units drawn in order, one fragment CALL each), or
  (b) a per-part bone index carried by the part/mesh object
  that owns the emitter's `obj` (the obj's extra fields —
  matrix array at [0], a second matrix/field at +0x418, a
  list at +0x410/+0x414 in sibling methods — look like a
  part-instance object, which favors (b)-style indices).
- The proof standard (bind-pose coherence gate on a built
  skinned GLB) cannot be run honestly until the caller's
  index rule is read. NO skinned GLBs are shipped — same
  discipline as rounds 9–10. Next step for a future round:
  decompile the registry-referenced methods around the
  emitter (0x08acfa5c / 0x08acfbc0 thunk targets and the
  0x08ad0370 / 0x08ad07e0 library functions its siblings call)
  and find the loop that calls emit() per unit.

## Route 3 (COM tables + part census) — run, negative

Cross-read as briefed (details in `JOB4-B3-ASSIGNMENT.md`):
the COM moveset files' tables and the slice census yield
per-character PART references (the Job-4 assignment), but
neither contains a per-unit or per-part bone-index table.
No palette evidence there.

## Route 2 feasibility note (for the coordinator — no session run)

Round 5's scripted PPSSPP (autopilot in the retained workdir)
booted headlessly to ATTRACT mode and produced the 32 MB RAM
dump used above. Its limits, measured: the attract-mode units
in RAM match NO top-76 file byte-exactly (attract loads menu /
demo assets, not any of the 12 character packages), so a CALL-
order read from that dump cannot be tied to a known package's
unit list. A decisive capture needs three things round 5 did
not have: (1) a scripted path into a mode that loads a KNOWN
package — versus/practice with a fixed character, via input
scripting past the menus or a pre-made save state at a fight;
(2) a GE display-list dump (PPSSPP GE debugger / frame dump)
rather than a flat RAM dump, so the master list's CALL order
(fragment i → unit j) survives with addresses intact; (3) the
candidate character's BONE inverse-bind set, to identify each
fragment's matrix against the posed skeleton (posed skin
matrix M = W·IB ⇒ W's translation = the joint's world
position; the recovered W set must form a coherent pose).
With (1)–(3) the palette falls out directly: for each unit,
the fragment CALLed immediately before its PRIM names its
bone. Feasibility: PPSSPP supports headless boot + GE dumps;
the open work is the input/save-state path to a fight — a
lane of its own, not an interactive session here.
