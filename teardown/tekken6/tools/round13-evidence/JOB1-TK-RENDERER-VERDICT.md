# Tekken 6 PSP — ROUND 13 JOB 1 (NTPP PIXELS): the `tk` renderer IS located and its upload builders ARE fully read — the pixel contract is proven at the descriptor level; the NTPP-section → descriptor population is NOT in this hop (exact residual named, stopped per brief)

Date: 2026-10-22, round 13. Disassemblies (Capstone, word-exact) in
`round13-evidence/dis/`: `dis_08acd030_texbind.txt`,
`dis_08acce14_clut.txt`, `dis_08ac7bc8_sprite_state.txt`,
`dis_08ac76dc_gestate_ctor.txt`, `dis_08ac79ac_transfer.txt`.
EBOOT: `~/workspace/_t6r4-work/ghidra-r9/EBOOT.DECRYPTED.ELF`
(VA = fileoff + 0x8803000).

## How the renderer was located (the brief's two routes, both used)

1. **RTTI neighbourhood**: the NTPP template's neighbouring vtable
   RTTI is `N2tk6sprite4fade10CMainTcb_tE` (round 12 precision note).
   The `tk` library lives in the 0x08ac–0x08ad code pages, with its
   class/handler tables in the 0x08bcf6xx–0x08bcfbxx registry zone
   (the same zone as the round-12 palette identity template).
   Data-word xrefs place the upload builders in those tables:
   0x08bcf618 → 0x08ac7bc8, 0x08bcf61c → 0x08ac76dc,
   0x08bcf940 / 0x08bcfa40 / 0x08bcfa80 / 0x08bcfac0 → 0x08acce50,
   0x08bcfaf0 → 0x08acd030. A registry chunk-type entry at
   0x08bcf7e0–0x08bcf7f8 lists the magics `GIDX`, `eXt\0`, `NTPP`
   together (the NTPP/GIDX handler class, methods 0x08acc214–0x08acc760).
2. **GE texture-command code scan**: raw scan for `lui` immediates
   whose high byte is a GE command (0xA0–0xE9 << 8) and for
   `li`-form command constants 0xC0–0xE9. The dense, genuine hits
   are in the 0x08ac pages (float-constant lookalikes 0xC049/0xC2B4
   elsewhere were checked and rejected). The functions emitting
   them are the upload path below.

GE command numbers used below are the PSP GE opcodes (ScePSP
GpuOpCodes): TBP0 0xA0, TBW0 0xA8, CBP 0xB0, CBPH 0xB1, TSIZE0 0xB8,
TMAP 0xC0, TMODE 0xC2, TPSM 0xC3, CLOAD 0xC4, CMODE 0xC5,
TFLT 0xC6, TWRAP 0xC7, TFLUSH 0xCB; transfer set TRXSBP 0xB2,
TRXSBW 0xB3, TRXDBP 0xB4, TRXDBW 0xB5, TRXKICK 0xEA, TRXSPOS 0xEB,
TRXDPOS 0xEC, TRXSIZE 0xEE, FBP 0x9C, FBW 0x9D.

## The shared image descriptor (the contract every builder consumes)

All upload builders consume one descriptor struct shape:

| Field | Type | Meaning (proven by use) |
|---|---|---|
| +0x08 | u16 | **format word**: low nibble = GE TPSM pixel-format enum; bit 7 (0x80) = swizzled flag |
| +0x0a | u16 | **width** in pixels (TBW0 argument, raw) |
| +0x0c | u16 | **height** in pixels |
| +0x28 | ptr | **pixel data pointer** (becomes TBP0 after the 0x8b890f8 address conversion) |

The NTPP/GIDX handler methods (0x08acc318, 0x08acc480, 0x08acc534,
0x08accf0c, …) all read exactly `lhu +8 / lhu +0xa / lhu +0xc` from
a descriptor argument and forward (format, width, height) — with
width/height arithmetic-right-shifted by the mip level — into the
bind methods. The descriptor is a standalone runtime struct.

## Upload builder 1 — texture bind, FUN_08acd030 (the upload path)

Called via vtable (no direct `jal` xrefs — exhaustive scan).
Args: a0 = texture object, a1 = width, a2 = height.
Pixel pointer = `[[a0+4] + 0x28]`, passed through the address
converter at 0x8b890f8. It builds an 8-word GE list in a rotating
8-slot pool (counter at 0x08c53a08, slot stride 0x20) and stores
the list pointer at obj+0xc:

| List off | Word | Construction (byte-exact from the disassembly) |
|---|---|---|
| +0x00 | TMODE 0xC2000000 \| sw | sw = 1 iff descriptor format word (u16 @ desc+8 of the [[a0+4]] descriptor) has bit 0x80 set, else 0 — **swizzle flag = format-word bit 7** |
| +0x04 | TPSM 0xC3000100 \| (fmt & 0xF) | **pixel format = format-word low nibble** (GE TPSM enum: 0=5650, 1=5551, 2=4444, 3=8888, 4=T4, 5=T8, 6=T16, 7=T32, 8=DXT1, …); the 0x100 bit is a constant OR |
| +0x08 | TBP0 0xA0000000 \| (pixels & 0xFFFFFF) | pixel pointer, top byte cleared |
| +0x0c | TBW0 0xA8000000 \| (addr[27:24] << 16) \| width | width = the a1 argument |
| +0x10 | TSIZE0 0xB8000000 \| (log2(height−1) << 8) \| log2(width−1) | log2 computed by a shift-count loop over (dim−1) — TSIZE carries log2 dimensions, so width/height are powers of two in this path |
| +0x14 | TFLUSH 0xCB000000 | constant |
| +0x18 | 0x1E000001 | constant tail word |
| +0x1c | 0x0B000000 | constant tail word |

Special case at entry: if `[[a0+4] + 4] == -14` (0xFFFFFFF2), the
pixel pointer is adjusted by +0x200000 / +0x400000-class offsets
selected by the format word (<3 / ==3 / other) before the same
list is built — a VRAM-resident variant path, noted not decoded
further (it does not change the format contract).

## Upload builder 2 — CLUT load, FUN_08acce14 / FUN_08acce50

Two sibling forms of one builder (registry tables above). Inputs:
obj+4 → descriptor (its u16 @+8 is read), obj+8 = CLUT pointer,
obj+0xc = destination list (0x20 B):

| List off | Word | Construction |
|---|---|---|
| +0x00 | CMODE 0xC500FF00 \| fmt_u16 | **CLUT format = the descriptor format word itself** (u16 @ desc+8), OR'd with the constant 0xFF00 |
| +0x04 | CBP 0xB0000000 \| (clut & 0xFFFFFF) | CLUT pointer from obj+8 |
| +0x08 | CBPH 0xB1000000 \| (clut[27:24] << 16) | |
| +0x0c | CLOAD 0xC4000000 \| (n >> 4) | only when fmt ≥ 3 and fmt ≠ 3 path… precisely: skipped when fmt < 3 (sltiu), skipped when fmt == 3; otherwise CLOAD with count n>>4 at +0x0c and a second word 0x0B000000 at +0x10; in the 0x08acce50 form the CLOAD count is (a1 >> 4) with a1 the caller's CLUT-size argument, and a variant at +0x0c uses (clut_size >> 3) |
| tail | — | list submitted via the (ptr, 0x20) routine at 0x8b88fc8 |

So **the CLUT is read from a pointer carried beside the texture
object (obj+8), in the same format word as the pixels** — for an
indexed format (T4/T8), palette and pixels travel as two pointers
on the same resource object, not inline in one byte stream.

## Corroborating builders (same descriptor, same library)

- **Sprite/texture state builder FUN_08ac7bc8**: builds a full
  0x40-word state block for a textured draw: FBP 0x9C / FBW 0x9D
  from a destination-surface descriptor (+0x28 ptr, +0xa width,
  +0xc height), TPSM 0xC3000000 | (src_desc+8 & 0xF) and
  TBP0/TBW0 from a source descriptor (+0x28 / +0xa) — the same
  descriptor contract, independently confirming every field.
- **Transfer (blit) builder at 0x08ac79ac–0x08ac7bc4**: emits
  TRXSBP/TRXSBW/TRXDBP/TRXDBW/TRXSPOS/TRXDPOS/TRXSIZE from two
  descriptors (+8 format — with <3 / ==3 branching on the format
  value, +0xa/+0xc dims, +0x28 ptrs) and TRXKICK 0xEA000000
  (|1 when format == 3).
- **GE state-object ctor FUN_08ac76dc**: default state words prove
  the field-per-command cache layout (TFLT 0xC6000000 @+0x1c,
  TWRAP 0xC7000101 @+0x18, TFLUSH-class 0xDF0001A6, ATST 0xDB…,
  ZTST 0xDE…, PMSK 0xE7/E8/E9…), i.e. this library owns the game's
  GE state cache that the palette library (round 12, 0x08adefxx)
  mirrors.

## What this does NOT give — the exact residual (one hop, stopped)

The builders consume a **runtime descriptor**; nothing in the
three hops read across rounds 11–13 (NTPP placement class →
datatextureroot pointers → tk upload builders) **populates that
descriptor from NTPP section bytes**: no function in the read set
reads a section's GIDX block or header and writes desc+8 (format),
desc+0xa (width), desc+0xc (height), desc+0x28 (pixels) together.
A targeted store-cluster scan for that population pattern across
the whole EBOOT found only a descriptor *destructor* (zeroing, at
0x08a350d8, a different 0x460-stride atlas object) — the population
site is not in the tk pages and was not identified in this hop.

Consequences, stated plainly:
- The brief's one-item decode requires **only code-derived
  parameters**. The code-derived contract above fixes *how* a
  descriptor's fields map to GE state, but the per-section field
  VALUES (which NTPP header/GIDX field is the format word, which
  are width/height, where the CLUT pointer comes from for a
  section) are **not** established by any code read so far.
  Guessing them from the header bytes (several mutually
  inconsistent byte readings fit) would be the blind sweep rounds
  10–12 forbade. **No decode was run, no PNGs, no textured GLBs.**
- **Residual (one hop further, named, then stopped per brief):**
  the archive-loader-side **descriptor factory** — the code that
  instantiates the NTPP/GIDX handler class's resource objects
  (registry table 0x08bcf800, methods 0x08acc214–0x08acc760 are
  handle wrappers, not the factory) and fills the image descriptor
  from a section. Candidates not yet read: the factory/ctor that
  installs those registry entries, and the live-GE-capture lane
  (round 11 route 2), which would observe TBP0/TPSM/TMODE/CLUT
  words for a known section directly and settle every field at
  once.
- Stage idx24's 40 NTPP sections inherit this residual: they are
  NTPP sections (round 12), so no stage textures are decoded in
  Job 2 either; the stage batch ships untextured with the pairing
  noted there.

## Verdict

tk renderer: **LOCATED, upload path FULLY READ, pixel contract
PROVEN at the descriptor level** (format = desc+8 low nibble,
swizzle = desc+8 bit 7, width/height = desc+0xa/+0xc, pixels =
desc+0x28, CLUT = sibling pointer with CMODE = desc+8 word).
NTPP pixels: **NOT DECODED** — section→descriptor population is
the named residual; textures-baked-in gate upheld by not baking.
