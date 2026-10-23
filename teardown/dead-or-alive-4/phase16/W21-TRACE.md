# DOA4 Phase 16 — Job 2: w21 token -> runtime-record expansion trace

Binary: `default.xex` retail, sha256
`56b68dec68991f007639d796b04cb88c9aa7b484c1fce54641cdda5de4f2b98f`
(release `doa4-iso-extracts-20261022`, re-verified this lane),
analyzed as `teardown/dead-or-alive-4/workdir/default_pe.bin`
(23,068,672 B, sha256 eaa1885a…). Method: word-level scans
(`phase16/tools/xex_scan_p16.py`) + targeted Capstone (BE|32,
skipdata) windows (`phase16/tools/xex_disas_p16.py`). VA
convention: .text file offset f -> VA f + 0x8200E800 (phase 15).
Grades: PROVEN / EVIDENCED / RESIDUAL as in earlier phases.

## Assignment
Trace FORWARD from the .bin loader cluster at VA 0x823FA430:
how a fighter .bin's sections (esp. the w21 table + the w31 J
token stream in the 0x22xx namespace) become runtime records,
and how those records reach the classifier (0x82408290) /
dispatcher (0x824F388C) proven in phase 15.

## §1 The file-open layer (EVIDENCED)
- VA 0x823FA430 itself is a small helper (string copy + a
  10-entry x 0x1C-stride list walk ending in two helper calls) —
  it is NOT the section consumer; it sits in the loader
  neighborhood phase 14 named.
- The archive file-open helper at VA 0x8238ED10 has exactly 27
  `bl` call sites in .text (full census this lane). They cluster
  at 0x823918E8–0x82391B2C (13 sites), 0x82392F78–0x82393028,
  0x82393B10–0x82393BD8, 0x82395B7C–0x82395BA4. The first cluster
  is the per-fighter file-set loader: it walks a per-fighter
  struct (r31) reading u16 fields at +0x20/+0x22 (archive/entry
  ids passed to the open helper), pointer fields at +0x54 and
  +0x70, and at 0x82391AD4 calls a registry helper
  (0x8238AC90) whose return value is scaled `mulli r7, r3, 0x6C`
  — the .mot registry record stride proven in phase 15. So the
  .bin/.mot file set is opened through archive ids, not through
  the section pointers: **no code at the open layer reads the
  .bin header's +0x08/+0x54/+0x70 section offsets as file
  offsets** (the +0x54/+0x70 loads in this cluster read the
  loader STRUCT, not a .bin buffer — register provenance is the
  struct walk starting at 0x82391868, `mulli r9, r11, 0x8C`).

## §2 The runtime-record layer (EVIDENCED, field level)
The records the phase-15 classifier/dispatcher consume are
written and translated by a function group at
0x823F6Cxx–0x823F71xx + 0x82406Exx–0x82409xxx:

- **Record initializer (VA 0x82406E48)**: for an index in r30 it
  computes THREE parallel-array addresses with strides 0x44,
  0x9C and 0x34 (`mulli r10, r30, 0x44`, `mulli r6, r30, 0x9C`,
  `mulli r15, r30, 0x34`), then initializes the 0x34-stride
  record: f32 constant at +0x00/+0x04/+0x08, u32 1 at
  +0x0C/+0x10/+0x14/+0x18/+0x1C, u16 0 at +0x20/+0x22, u32 0 at
  +0x2C and **+0x30** (the id field, zeroed here). It then calls
  the classifier-family functions at 0x82408170 and 0x824091F0.
  So the +0x30-id records are a 0x34-stride array, initialized
  per-index by this function; the phase-15 classifier
  (0x82408290) has **zero direct `bl` callers** in .text (full
  census this lane) — it is reached indirectly (function
  pointer / bctr), consistent with a callback table.
- **Command validator (VA 0x824091F0)**, called from the
  initializer: unpacks a command into fields (low byte via
  `clrlwi 0x18`, low u16s via `clrlwi 0x10`) and range-checks
  field pairs against the bands [0x15,0x1C], [0x1D,0x24],
  [0x25,0x2C], ==0x14, ==0x12, and command ids
  0x10A/0x10B/0x10C, 0x139–0x147, returning a class code 1–7.
  The phase-15-noted 0x2C compares at 0x82409604/0x824097E0/
  0x82409804 are the [0x25,0x2C] band edge of THIS validator —
  a field-value band (37–44), NOT a 44-entry descriptor walk.
  That candidate is hereby resolved NEGATIVE.
- **Per-player token decode (VA ~0x823F6D2C–0x823F6F9C)**:
  loops over 2 players (r30 = 0..1), walking records of stride
  **0x9C** (r31 += 0x9C). For each record it decodes the u16 at
  +0x00 and the u16 at +0x02: bit 0 (clrlwi 0x1F), a 2-bit field
  at bits 0x14–0x15 (rlwinm) whose values 0x000/0x400/0x800/
  0xC00 map to classes 1/2/3/5 stored per record, a 4-bit field
  (rlwinm 0x1C) compared across the two u16s (xor + class
  bytes), and further bit slices written as flag bytes — i.e.
  **the u16 token stream survives into runtime records of
  stride 0x9C with the token u16s at +0x00/+0x02**, and this
  function is a consumer that re-decodes their bitfields every
  frame (it is a state/compare pass, not the loader).
- **Record translator (VA 0x823F6FA0)**: for index r3 it reads
  a source record via BOTH strides (`mulli r8, r3, 0x9C`,
  `mulli r28, r3, 0x250` — the two dispatcher strides of phase
  15) and writes a destination record (base + idx*40 + 0x44):
  - +0x0C <- packed bits from source +0x36 (byte), +0x37
    (byte), +0x32 (u16 — the phase-15 "sub" field) masked
    0x47FF and recombined (rlwimi chains);
  - +0x10 <- packed bits from source +0x44, +0x4F, +0x54,
    +0x55 bytes;
  - +0x00/+0x04/+0x08 <- three f32s copied verbatim from the
    0x250-stride source record +0x00/+0x04/+0x08;
  - +0x14 <- (clamp(source +0x24 u16, 0x1FF) ) |
    (clamp(source +0x2C u16, 0x1FF) << 9), with a table-driven
    variant path (0x4D-stride byte table + u16 table lookup)
    when a global flag byte is set.
  So the runtime pipeline is at least TWO record generations:
  0x9C/0x250-stride records (token-bearing, +0x30 id / +0x32
  sub / +0x36/+0x37 / +0x44 / +0x4F / +0x54/+0x55 / +0x65
  fields) -> translated 0x28+-byte records with packed fields;
  the phase-15 dispatcher (0x824F388C) consumes the first
  generation (+0x30 id dispatch, 0x9C/0x250 fall-through math).

## §3 The frontier (exact)
What is PROVEN end-to-end: file set opened by archive id
(§1) -> runtime records exist in the layouts of §2 -> the
token u16s are present at +0x00/+0x02 of the 0x9C records ->
classifier/dispatcher consume +0x30/+0x32/+0x37.
What is NOT isolated this lane (the exact residual): **the
file-side writer** — the function that, at load time, reads a
.bin buffer's w21 table (the 1024 u32 offsets at header +0x54)
and the w31 token stream and WRITES the 0x9C-stride records.
Evidence missing: a code site that (a) loads a base+0x54 word,
(b) indexes it by a clip id, and (c) stores u16s into a
0x9C-stride array. The displacement census (lwz +0x54: 1,119
sites; sth +0x30/+0x32: ZERO sites in all .text — the +0x30 id
is written as part of a u32 store or via indexed stores) does
not isolate it by constants alone; the next step is a
data-flow hunt: find writers of the 0x9C array base (the global
the §2 functions load via lis/addi bases in the 0x8302xxxx
data region) and walk back to the load-time caller. That is a
Ghidra-grade whole-program pass and is named, not done, here.
Consequently **no offline w21 expander is claimed**: §2 is
enough to parse RUNTIME records if they are ever dumped, but
the file->record step remains unproven, and any token
semantics assigned today would be guesses.

## §3b Ghidra cross-check (attempted, blocked by the PE reconstruction)
A bounded Ghidra 12.1.4 headless pass (JAVA_HOME per phase 15,
-Xmx1024M) was run this lane: auto-analysis of
`workdir/default_pe.bin` SUCCEEDED, but the reconstructed PE
imports at image base 0 with an address space ending at
0x10FFEF, so the registry VAs (0x82C69A70 / 0x82C6B38C) are out
of bounds and no data xrefs could be collected (script error
AddressOutOfBoundsException, on record in the lane log). The
PE's three section mappings (.text +0x8200E800, .rdata
+0x82000000, .data +0x8201DE00) cannot be reproduced by a
single-base raw load either. Rebuilding a faithful Ghidra
project (per-section memory blocks at the true VAs) is the
named prerequisite for the data-flow hunt of §3 — noted, not
done in this lane's budget; the Capstone evidence above is
unaffected.

## §4 Feed into Job 1
Nothing in §2 decodes the .mot packed sub-block payload (the
.mot side's expansion is a different consumer than the w21
token path traced here); Job 1 proceeds on file-byte evidence
alone. One cross-link IS banked: the validator's field bands
([0x15,0x1C] / [0x1D,0x24] / [0x25,0x2C] = 21–28 / 29–36 /
37–44) partition a 44-wide field space — the same 44 as the
.mot record descriptor's channel count. Graded as a
CORRELATION (both are 44-wide partitions in the animation
command system), not as proof that validator fields are .mot
channels.
