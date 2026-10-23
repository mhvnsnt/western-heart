# DOA4 Phase 11 — Job 1 continuation: stream-object address CORRECTED, ring structure PROVEN, consumer body read raw, stream-build decompiled at the correct seed

Continuation of `ANM-READER3.md` (PR #525), executing its "exact next
steps" 1–2. Written by the parallel continuation lane; the primary
lane's addendum to ANM-READER3 (commit ae2bd66) already folds in this
lane's Ghidra outputs with attribution — this doc adds the raw-byte
analysis that addendum did not have, and corrects two addresses that
both docs previously carried wrong. **No parser is claimed and no
clips shipped** — the bit layout of the 16B head records is still not
proven (gate discipline, unchanged).

## Correction 1 — the global stream object is at 0x833FA3D0, not 0x82C3A3D0

ANM-READER3 §"stream advance" and the phase-11 STATE file name the
global stream object **0x82C3A3D0**. The raw bytes say otherwise.
The advance helper at true VA 0x8243D758:

```
8243d758  lis      r11, 0x8340        ; word 0x3D608340 — imm is 0x8340
8243d75c  addi     r10, r11, -0x5c30  ; word 0x394BA3D0
8243d760  lwz      r11, 0xbe0(r10)
8243d764  lwz      r10, 0xbe4(r10)
```

0x83400000 − 0x5C30 = **0x833FA3D0**. This is inside `.data`
(VA 0x82B60000–0x835A18B8 per the PE section table read this session),
so the address is structurally valid; 0x82C3A3D0 would also fall in
`.data`, which is presumably how the slip survived. Every other
reference to the stream object in the phase-11 docs should be read
with this correction. Proof is reproducible from
`teardown/dead-or-alive-4/workdir/default_pe.bin` at file offset
0x8243D758 − 0x82000000 − 0x2E0000 + 0x2D1800.

## The ring structure — PROVEN from three independent code sites

With the corrected address, a Capstone constant-propagation scan
(same engine as `capstone_scan3.py`; script:
`phase11/tools/scan_streamobj.py`; filtered hits:
`phase11/tools/streamobj_cursor_hits.csv`) finds:

- **358 distinct sites** materialize the exact value 0x833FA3D0 —
  it is one of the engine's central globals.
- The only sites touching the cursor pair (+0xBE0/+0xBE4) are the
  loader's own neighbourhood (0x8243D758–0x8243D78C) and two writer
  functions at ~0x824297xx and ~0x82444Cxx.

Raw disassembly of the writers + the entry-pointer helper
(0x8243D780) proves the structure:

- Three parallel arrays at **+0xBE8, +0xBF0, +0xBF8**; element index
  = the u32 at **+0xBE0** (write cursor) / **+0xBE4** (read cursor);
  index math `idx*3*8 = idx*24` at every site → the three arrays are
  one **32-slot ring of 24-byte entries** {u32 tag @+0xBE8, u64
  payload @+0xBF0, u64 payload @+0xBF8}, slots addressed
  `base + 0xBE8 + idx*24 (+8/+16)`.
- Writer at 0x8242974C stores tag **8**, payload0 = a counter value,
  payload1 = 0; writer at 0x82444C44 stores tag **7**, payloads =
  two registers. Both then do `cursor = (cursor+1) mod 0x20`.
- Helper 0x8243D780 returns `&entry[read_cursor]` when the cursors
  differ, else 0. Helper 0x8243D758 returns the wraparound distance
  between the cursors (the `+0x20` in it is the ring size 32, **not**
  a byte stride).

**Consequence for ANM-READER3:** its "0x20-byte-strided stream"
reading is superseded — +0x20 is the ring depth. The ring is a
tagged command/event queue (tags 7 and 8 proven at the two writers),
i.e. the loader's completion path posts and consumes *commands*,
not raw anm record bytes. The 16B anm records do not flow through
this ring as data; their consumer must be reached through the
payload pointers the commands carry.

## The consumer at 0x8243DD08 — NOT a mere thunk; body read raw

The primary lane's addendum (ae2bd66) reports 0x8243DD08 as "a thunk
to undecodable 0x829FD490" based on the Ghidra decompile
(`phase11/decomp2/func_0083dd08_FUN_0083dd08.c`, 111 chars,
"subroutine does not return"). That decompile is a Ghidra
function-boundary artifact: the function's first two instructions
are the standard XDK prologue (`mflr r12; bl 0x829FD490` — a
register-save helper), after which the real body follows in the same
bytes. Raw Capstone disassembly of 0x8243DD08 onward shows:

- zeroes obj+0xBD8/+0xBDC (the output-list counters), calls the
  distance helper 0x8243D758; if the ring is empty, exits to
  0x8243FB28;
- fetches the next entry via helper 0x8243D780 (r30 = entry ptr),
  loads **payload0 (`ld r3, 8(r30)`)** → stored to obj+0x758, and
  the **tag (`lwz r4, 0(r30)`)** → bounds-checked ≤ 0xF and
  dispatched through a **16-entry jump table at 0x8242F5F8** whose
  entries are absolute handler addresses:
  0:0x8242F638 1:0x8242F9C8 2:0x8242FCCC 3:0x8242FFD0 4:0x82430360
  5:0x82430664 6:0x82430A3C 7:0x82430C18 8:0x82430C18 9:0x82430C18
  10:0x82430C18 11:0x82430CF0 12:0x82430EA4 13:0x82430FDC
  14:0x82431114 15:0x82431184 (cases 7–10 share one handler);
- one case path (fall-through at 0x8243DE38) calls the record
  builder at **0x8243D7B8** with (obj, entry+0x10 payload, flag
  0x2009) and then appends to the function's OWN output arrays at
  obj+0x818…+0x858 indexed by obj+0xBDC, writing tag 5, a flag byte
  and a value from obj+0xF70 per record.

So 0x8243DD08 is a **command translator**: ring entries in,
tag-dispatched, emitted records out (arrays at +0x760…+0x860 of the
same global). The only callers of the ring helpers in the whole
image are this function and one sibling at ~0x8243FA2C/0x8243FA78
(same pattern). Whether any of the 16 tag handlers unpacks anm
16B-record payloads is the open question — the handlers live at
0x8242F638+ (a different code region from the translator, which is
why Ghidra's per-function decompile never reaches them).

## Stream-build 0x8295F7D0 — decompiled at the CORRECT seed

ANM-READER3 gives its Ghidra address as 0xDF57D0 and the primary
lane's addendum as 0xD75F7D0; both are transcription slips.
0x8295F7D0 − 0x81C00000 = **0xD5F7D0**. Decompile (Ghidra, with the
`.pdata` create-function fallback in `DecompileCandidates.java`):
`phase11/decomp2/func_00d5f7d0_FUN_00d5f7d0.c` — again only the
prologue lifts in Ghidra, so the characterization here is from raw
disassembly: it is a thin wrapper that builds a 0x18-byte request
struct on the stack and calls SDK routines at 0x82B591A4 /
0x82B58784 / 0x82B58B14, returning **0x3E5** on the failure path
(the same 0x3E5 sentinel the loader's state 8 polls) and 0x65B on
another. It is a file/stream **handle opener**, not a record
unpacker. (The two wrong-seed decompiles are kept in scratch and
labelled here so nobody re-reads them as targets:
`func_00df57d0` = true VA 0x829F57D0, a jump-table fragment;
`func_00d757d0` = true VA 0x829757D0, VMX fixed-point vector math.)

## Job 1 verdict — residual, exact (supersedes ANM-READER3's next steps)

Proven this continuation: the corrected stream-object address; the
32×24B tagged command ring and its two writers; the translator
function 0x8243DD08 with its 16-case dispatch table and output
arrays; stream-build = SDK handle opener. Still NOT proven: the
bit-level field layout of the 16B anm head records and the
record→stream mapping; **no parser, no clips** (the G2 gate lands
as an exact residual, per the job's terms).

Next steps, in order:
1. Read the 12 distinct jump-table handlers at 0x8242F638…
   0x82431184 raw (Capstone linear, as here — Ghidra function
   boundaries fail on this code) and find which handler, if any,
   walks a payload with shift/mask extraction; the payload pointers
   in ring entries are the thread to the anm record buffer.
2. Trace what writes payload0/payload1 for the tags the translator
   actually consumes (writers beyond the tag-7/tag-8 pair above —
   same scan, tag stores to +0xBE8).
3. `D:\bin\anime_cm.bin` + one per-fighter `.bin` from the ISO
   (step 3 of ANM-READER3) — still not on local disk; the ISO is
   not in this clone's workdir, so this needs a pull lane.

## Job 4 note

Unchanged from ANM-READER3 §4: material setup is not in this
family; the proven decl→texture set stays exactly 3. This
continuation's scan adds one more negative data point: the
0x833FA3D0 global's cursor neighbourhood (358 materializer sites
sampled via the cursor-pair filter) contains no texture/shader
setup — the consumer family is command translation only.
