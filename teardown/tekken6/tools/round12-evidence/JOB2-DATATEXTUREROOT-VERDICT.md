# Tekken 6 PSP — ROUND 12 JOB 2 (NTPP PIXEL CONSUMER): `tcb_datatextureroot_t` also carries NO pixel path — full read landed; residual chain named and stopped at one hop

Date: 2026-10-22, round 12. Disassemblies in
`round12-evidence/dis/`: `dis_08893e80_tcb_methods.txt`
(the complete tcb method span), `dis_0892fc40_ntpp_init.txt`.
EBOOT: `~/workspace/_t6r4-work/ghidra-r9/EBOOT.DECRYPTED.ELF`.

## How datatextureroot was hunted (same method as round 11's NTPP)

String/RTTI scan for the type names, then vtable → method set:

- The name `21tcb_datatextureroot_t` exists in the image ONLY
  as a substring of the pointer-type name
  `13tcb_pointer_tI21tcb_datatextureroot_tE` at 0x08b94054.
  **There is no standalone class type_info and no class vtable
  for `tcb_datatextureroot_t` itself in this ELF.**
- What exists is a family of `tcb_pointer_t<T>` smart-pointer
  instantiations in the 0x08b93fxx–0x08b941xx data block:
  - vtable **0x08b94028** → RTTI → type_info whose name is the
    datatextureroot pointer type. Methods:
    [0] 0x08893f14, [1] 0x08893fb4, [2] 0x08893f74, [3] 0.
  - vtable **0x08b94078** → tcb_pointer_t<tcb_datamemoryroot_t>.
    Methods: [0] 0x08893f04, [1] 0x08893fa4, [2] 0x08893f64, [3] 0.
  - vtable **0x08b93fc4-area / 0x08b940c8** → the datamemoryroot
    pointer sibling set (0x08893ef4 / 0x08893f94 / 0x08893f54).
  - Root type_info records sit alongside (names
    `20tcb_datamemoryroot_t` @0x08b94004 and the pointer-type
    records @0x08b94038/0x08b94088/0x08b940d8).
- The COMPLETE method span 0x08893e80–0x08894080 was
  disassembled and read (`dis_08893e80_tcb_methods.txt`).
  Every method of every one of these vtables is a ≤5-instruction
  thunk: install a vtable pointer (lui 0x8b9 + addiu) and tail
  into the shared base ctor 0x885f3e0, or zero the fields
  +0x4/+0x10/+0x14 (dtor/reset thunks @0x08893f44–0x08893f90),
  or route through the allocator 0x887c640 / release 0x88789c8
  pair (@0x08893e80–0x08893ef0). Compound ctors (@0x08893fe4,
  @0x08894044) install the primary vtable at +0 and the two
  secondary vtables (0x08b93e48 / 0x08b93e98 family) at
  +0x5c/+0x74, chaining the base ctor on each sub-object.

## Pixel-path facts — NONE EXIST here either

Across the complete tcb method set: **no load/upload method,
no GE texture commands (no 0xC0–0xE9 command words), no byte
loops, no swizzle arithmetic, no CLUT handling, no reference
to any NTPP/GIDX file data at all.** The `tcb_*root_t` types
are the data-archive roots of the tcb library and, in this
ELF, only their smart-pointer wrappers are present — pure
pointer bookkeeping (construct / destruct / reset / refcount
release). There are no code-derived pixel parameters to
extract, so the prescribed one-item decode cannot be run —
the same terminal situation as the NTPP class in round 11,
now proven for the named successor as well. No blind sweep
was substituted; no textured GLBs.

Corroborating reads from this round:
- The NTPP template's consumers in the EBOOT are exactly the
  three lui/addiu xrefs to 0x08b9c5b0 (0x0892fc58, 0x0892fe70,
  0x0892ff74). The first, in the init method @0x0892fc40
  (`dis_0892fc40_ntpp_init.txt`), sets the round-11 defaults
  (+0x98=1, +0x9c=110.0f) and passes the template address to a
  registration helper (jal 0x885f17c, a1=0x10) — section
  factory/initialisation, no pixel work. (Precision note on
  round 11: the "NTPP RTTI record" at 0x08b9c5b0 is the file
  section TEMPLATE object itself — magic + header fields
  0x110/0x40/0x80/0x100050/0x84030100/0x80020; the neighbouring
  vtable 0x08b9c568's RTTI slot points at 0x08b9c51c, whose
  name is `N2tk6sprite4fade10CMainTcb_tE` — a tk sprite/fade
  class. Round 11's functional verdict is unchanged: none of
  its six methods has a pixel path.)
- The 0x08adefxx–0x08adf0xx functions that build GE-family
  words 0xCD/0xCE/0xCF in the palette object's library are a
  **state-cache** (compare cached word at obj+4/+8/+0xc,
  store on change, clear dirty @+0x1c; values are float-derived
  state, e.g. colour/offset quantities) — state setters, not
  texture upload, and they never touch section data.

## The next consumer (one hop, per brief) + residual chain

From the tcb call graph, the hop after the roots is the
**DATA401 archive loader that instantiates the roots and hands
section pointers out** (the code calling the 0x08893xxx thunks
and the 0x887c640/0x88789c8 alloc/release pair) — and after it,
the consumer of the NTPP *sections* is the tk library's
sprite/texture render path that owns the template's class
(tk::sprite::fade::CMainTcb_t and its render siblings in the
0x08ac–0x08ad library pages). Neither contains a statically
readable pixel decode in the parts read across rounds 11–12.

**Residual chain, declared and stopped here (per the brief's
one-more-hop rule):** NTPP placement class (r11: no pixel
path) → tcb_datatextureroot pointer machinery (r12: no pixel
path, no load method present in this ELF) → archive loader →
tk sprite/texture renderer (unread). Until the renderer's
upload is read — or a live GE capture is taken (the same
capture lane as Job 1's route 2) — **no code-derived pixel
format exists, textures stay unbaked, and the
textures-baked-in gate is upheld by not baking.** This closes
the static NTPP hunt at the named residual.
