# DOA4 Phase 17 — Job 2: the file-side writer (w21 table -> 0x9C records)

Binary and method as in `phase17/GHIDRA-PROJECT.md` (faithful
Ghidra project at base 0x82000000 + full-.text Capstone sweep,
2,206,592 instructions; function boundaries from the .pdata map,
`phase17/tools/pdata_parse_p17.py`). Phase-16 ground is NOT
re-derived; this trace starts from its §3 frontier: "find
writers of the 0x9C array base and walk back to the load-time
caller". Grades as before.

## §1 The 0x9C arena bases (PROVEN, from the initializer's own code)

Disassembly of the initializer entry 0x82406E48 (in function
824069D0–82406F5C) materializes every parallel-array base as a
lis/addi constant:

| array | base VA | stride | evidence at 0x82406E48 |
|---|---|---|---|
| token records (phase-16 "0x9C records") | **0x83020188** | 0x9C | `addi r5, r11(0x83020000), 0x188`; `add r16, r6(idx*0x9C), r5` |
| id records | **0x830A7C20** | 0x34 | `addi r14, r11(0x830A0000), 0x7C20`; fields +0x00/+0x04/+0x08 f32, +0x30 id zeroed |
| value-copy array A | 0x830A7DBC | 0x44 | `lwzx r5, r10(idx*0x44), r28(0x830A7DBC)` |
| value-copy array B | 0x830A7DC0 | 0x44 | `stwx r5, r10(idx*0x44), r6(0x830A7DC0)` |
| per-index byte table | 0x83022D10 | 1 | `lbzx r9, r9(0x83022D10), r30` |
| per-index u16 table | 0x830A6B58 | 2 | `lhzx r8, r31(idx*2), r8(0x830A6B58)` |
| per-index u16 array | 0x830A7AC0 | 2 | `sthx r8, r31, r4(0x830A7AC0)` |

All bases are in the UNINITIALIZED part of .data (past the
initialized span ending 0x82F57C00): runtime state, zero at
boot. 491 code sites materialize 0x83020188 — it is the base of
a hot arena (the command system's per-index state lives at
small offsets from it: the token decode's per-player byte flags
sit at 0x830201A9.., stepped 0x9C per player in FUN_823F6CE8's
decompile, `phase17/data/decompile/pdata_823F6CE8.c`).

## §2 The record-pointer globals (PROVEN)

The token decode (FUN_823F6CE8) does NOT index the arena
directly: it reads two POINTER globals, `DAT_83099E04` (player
A) and `DAT_83099BA8` (player B), and dereferences u16s at
+0x00/+0x02 of the pointed-to records (decompile banked; it
independently reproduces phase 16's bitfield read: bit 0, bits
0xC00 -> classes 1/2/3/5, xor-compare across the two u16s).
The ONLY stores to those two cells in all of .text are at
0x823F61B0 / 0x823F61B8, in a reset function at 0x823F6170
(pdata 823F5F80–823F61DC region): it stores the SAME fixed
address 0x83099BB8 into both cells (and into 0x83099E0C). Note
0x83099E04 − 0x83099BB8 = 0x24C ≈ the 0x250 generation stride:
the reset points both players at a shared default record block.
Per-clip playback therefore REPOINTS these cells (or their
successors) at a clip's record stream — the repointing store
was not isolated (it may go through a computed pointer or a
different cell pair per context; the two cells above are the
only DIRECTLY addressed pair).

## §3 An arena writer (PROVEN, runtime-side)

FUN_824000B0 (callers: 0x824004E8, 0x82400D18, 0x8240114C)
writes the arena: byte tables at 0x830A5268/0x830A526C/
0x830A5278/0x830A5288, a 4×11-entry u32 table at 0x83022D38
(stride 0x2C), and a per-player clear loop over the 0x9C arena
(`mulli r8, r11, 0x9C; stbx r7, r8, r9(0x83020188)` for indices
0..1). It is a mode/state reset in the command cluster — a
WRITER of the arena, but runtime-side, not file-side.

## §4 The file-side writer hunt (method + result)

Candidate signatures were swept over all 2,206,592 instructions
with .pdata function attribution:

1. **(lwz +0x54 -> indexed load)**: 61 sites where a non-stack
   `lwz rX, 0x54(rY)` result becomes an indexed-load base within
   40 instructions. None is in a function that also stores u16s
   into 0x9C-strided records.
2. **(mulli 0x9C ∧ sth +0 ∧ sth +2)**: exactly 19 functions
   contain a 0x9C multiply AND u16 stores at displacements 0
   and 2 (the token slots). NONE of the 19 contains a non-stack
   `lwz +0x54` or a call to the open helper 0x8238ED10. The
   heaviest (FUN_822F0300: 30 sth+0 / 26 sth+2) is a global
   -1-pattern reset of 0x82FCxxxx state; FUN_822EF4F8
   (sthx×24, lhzx×16) is a record transformer in the framework
   cluster. Full candidate list is reproducible with the sweep
   (scratch tooling described in PHASE17-STATE.md).
3. **Direct bl graph**: the initializer entry 0x82406E48 has
   exactly one caller (0x824131E8, in the per-frame manager
   FUN_82412F48); the translator entry 0x823F6FA0 has two
   (0x82411F0C/0x82411F14, per-player calls in FUN_82411EA8);
   the registry helper 0x8238AC90 has four (loader cluster +
   0x82391DE0, 0x82392FF4, 0x8239314C). No load-time call chain
   from the loader cluster reaches any §4.2 candidate.

## §5 Verdict: FRONTIER (advanced, exact)

The writer is NOT isolated, and no offline expander is
claimed. What changed vs phase 16: the arena is no longer an
anonymous global — its bases, its pointer-global indirection,
its reset/setter functions, and its runtime-side writers are
all pinned to VAs (§1–§3), and the two natural static
signatures for the file-side step are now EXHAUSTED with
negative results (§4). The missing link, stated exactly: **no
function in .text both dereferences a fighter .bin buffer
(w21 at +0x54, non-stack) and stores u16s into 0x9C-strided
records.** The evidence now points to the expansion NOT being
a direct buffer->record copy in one function: the .bin is
opened by archive id into loader-struct destinations (phase 16
§1 + phase 17 GHIDRA-PROJECT §3.2), so the writer most likely
consumes a SECTIONED pointer (w21 delivered as its own base,
indexed ×4 with no +0x54 deref at the writer) or an
intermediate token queue filled by the archive layer. The two
named next steps: (a) trace the open helper FUN_8238EA20's
destination map — which loader-struct slots (+0x3C/+0x54/+0x68/
+0x6C/+0x70/+0x74) receive which section pointers, then follow
the w21 slot's readers; (b) a dynamic trace (Xenia) breaking on
stores to 0x83020188+0/+2 during a zack clip load — the same
capture session specified for item 1 in
`phase17/XENIA-TRACE-SPEC.md` closes this item too (watchpoint
W3 there).
