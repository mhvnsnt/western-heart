# Tekken 6 PSP — ROUND 10 JOB 1 (BONE PALETTE): words 3–4 PROVEN = USCALE/VSCALE; palette is runtime-built, not file data

Date: 2026-10-22, round 10. Decoder evidence from file bytes
(`~/workspace/_t6r4-work/decoded76/`), the round-5 PPSSPP RAM
dump (`dumps_r5/ram_attract.bin`, 32 MB), and the published PSP
GE opcode table (ScePSP `GpuOpCodes.cs`, via DeepWiki's GPU
Instruction Set page — industry documentation, not a guess).

## Verdict (proven): unit header words 3–4 are NOT a bone palette

The standing round-9 candidate — unit header words 3–4 as
per-unit bone binding — is REFUTED, and the words are positively
identified:

| Word | Value form | GE command | Meaning |
|---|---|---|---|
| word 3 | `0x48xxxxxx` | 0x48 USCALE | texture U scale, imm24 float |
| word 4 | `0x49xxxxxx` | 0x49 VSCALE | texture V scale, imm24 float |

Proof chain:

1. Top byte is constant per word across every sampled unit in
   idx00/01/04 (slots 0 and 10): word 3 always `0x48`, word 4
   always `0x49`. Bone indices would vary in the top byte.
2. The GE opcode table assigns 0x42–0x4D to viewport/texture
   transform: 0x42–0x44 X/Y/ZSCALE, 0x45–0x47 X/Y/ZPOS,
   **0x48 USCALE, 0x49 VSCALE, 0x4A UOFFSET, 0x4B VOFFSET**,
   0x4C–0x4D OFFSETX/Y. Bone commands are 0x2A (BOFS) /
   0x2B (BONE matrix upload) — never present in unit headers.
3. Read as GE imm24 floats (`float32((arg & 0xFFFFFF) << 8)`,
   the standard GE float-argument encoding), the values land
   in [0.12, 0.51] — texture-scale range. Samples:
   `0x483f00a8` → 0.50256, `0x493e8105` → 0.25199,
   `0x483e8081`/`0x493e8081` → 0.25098/0.25098 (a unit whose
   U and V scales are equal — the pair shares its low 24 bits,
   impossible for two independent bone-index words).
4. Consistency: VTYPE 0x301/0x321 vertices carry u8 UVs whose
   per-unit maxima are always 255 (full range) — exactly what
   a per-unit USCALE/VSCALE atlas mapping expects (raw UV ×
   scale, offsets defaulting to 0 in these units; 0x4A/0x4B
   offset commands are absent).

## Every other file location tested — also not a palette

- **Per-unit prefix blocks (~112–126 B before each unit; a
  section-tail offset directory points at them, entry =
  unit_offset − 0x70)**: PROVEN bounding-box records:
  word 0 = the unit's total span in bytes (640 for idx00
  slot10 unit 0 = 0x490−0x210 exactly), word 1 high half =
  the unit's vertex count (43 = the unit's strip-count sum),
  then 24 floats = the 8 corners of the unit's axis-aligned
  bbox in descriptor-normalized space (idx00 slot10 unit 0:
  x∈[−0.108,0.108], y∈[0.4975,0.7179], z∈[−0.1045,0.0805]).
  The 144 B `0x104005xx` blocks in slot-0 sections are the
  same record family (header + offset + 24-float bbox).
- **Section state lists** (e.g. idx00 slot10 @0x110): GE state
  fragments (0x54–0x5B patch/shading, 0xC6–0xE9 texture/light
  state, terminator 0x0B) — material state, no bone data.
- **BONE chunk small section** (offset table[4] region):
  idx00 = character dims (253.1, 130, 130, 50, 50 floats);
  idx04 = string-offset lists (0x262…, 0x4b0…) + same dims.
  Not per-unit data.
- **Slot 6 (48 B)**: count 5 + five (0, 48) pairs. Not a palette.
- **Vertex streams**: weights only (round-9 proven); the GE
  vertex format has no bone-index field by design.

## Runtime mechanism (RAM ground truth)

The attract-mode RAM dump contains the engine's runtime bone
path: a pool of single-bone display-list fragments, each =
`0x2A000000` (BOFS, in the template instance) or a bare run of
12 × `0x2B` words (one 3×4 bone matrix, imm24 floats) +
`0x0B000000` terminator, stride 52 B (520+ fragments in the
0x15f37dc region alone; an 8-matrix identity template sits in
the EBOOT image at dump offset 0x3cfdf4). The engine builds
these fragments per frame from the ANIMATION pose and CALLs
them in palette order before each unit's PRIM — the palette
order exists only in the per-frame master list the CPU
builds, driven by code, not by a file table found in the
character packages. RAM copies of NDPP units are byte-identical
in form to the file units (headers and USCALE/VSCALE words
intact) — the engine does not rewrite units at load.

## What this means / exact remaining hypothesis space

No guessed skinning is shipped (per the brief's proof
standard: a palette rule must put every vertex's weights on
bones near that vertex; no file rule found passes or can even
be stated). Remaining routes, in order:

1. **Code route (not run to completion this round)**: find the
   EBOOT function that walks a section's units at draw time
   and emits the fragment CALLs — its per-unit bone selection
   input (a part→bone map keyed by unit ordinal, bone-name
   hash, or the moveset/part system) is the palette source.
   Entry points: xref the fragment-pool writer (writes
   0x2B000000-pattern words), or the model-class draw method
   under ctor `FUN_0886fe88` / vtable `0x08b918b8`. Capped-heap
   Ghidra or Capstone on those targets only.
2. **Live-capture route**: PPSSPP GE dump of a frame drawing
   a KNOWN character (one of the 12 packages), read the master
   list's CALL order against that package's units + identify
   each fragment's matrix against the character's inverse-bind
   set (posed skin matrix M = W·IB ⇒ W translation = joint
   world position; the posed skeleton must be coherent).
   The attract dump's units match none of the top-76 files
   byte-exactly, so this needs a fresh capture in a mode that
   loads a top-76 character.
3. **Animation-data route**: the palette may be implied by the
   round-7 moveset/part data (per-part bone assignment). Not
   yet cross-read against unit ordinals.

Delivered instead this round (all proven layers): the
USCALE/VSCALE identification (feeds Job 3 texture mapping),
the per-unit bbox-block + section-directory layout, skeletons
for all 12 character packages (Job 2), and the full-section
unskinned batch in the round-9 format.
