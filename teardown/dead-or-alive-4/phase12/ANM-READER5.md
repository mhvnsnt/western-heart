# DOA4 Phase 12 — Job 1: the 16 tag handlers read raw; the translator family is a (tag, key, value) command layer — the anm 16B-record consumer is NOT in it (exact residual)

Continuation of `phase11/ANM-READER4.md` (authoritative), executing its
"next steps" 1–2: read the jump-table handlers raw (Capstone) and trace
the payload writers / output readers. **No parser is claimed and no
clips shipped** — the handler read closes the named route with a
proven negative, and the residual below is exact (gate discipline).

Tools: `phase12/tools/dump_handlers_p12.py` (addressing frame + case
feature extraction), `phase12/tools/scan_ring_writers.py` (ring-writer
census + descriptor-type scan). Full listings in scratch
`p12/translator_full.txt` (1,939 lines), `p12/builder.txt`,
`p12/writers.txt` (rebuildable from `default_pe.bin` with the tools).

## §0 Frame correction (proven this phase; read every phase-11 VA with it)

Phase-11 .text VAs are PE-frame labels (Ghidra project base artifact,
same class as phase 10's wrong-base bug): they sit **+0xE800 above**
the true VAs. Proof, all from the instruction stream itself:

- The translator's dispatch computes its jump-table base from
  `lis r12, 0x8243; addi r12, r12, −0xA08` = **0x8242F5F8** (absolute,
  frame-independent) — and the 16 handler addresses are stored at
  file offset 0x42F5F8, i.e. true VA 0x8242F5F8 iff
  `VA = 0x82000000 + fileoff` for .text. Under the PE mapping
  (fileoff = RVA − 0xE800) that base lands mid-function in .rdata —
  impossible.
- The case body at table-listed VA 0x8242F638 (fileoff 0x42F638) uses
  exactly the translator prologue's register setup (r30 = ring entry,
  r31 = stream object 0x833FA3D0, r20 = flag 0x2009, r27 = 5, r28 = 1)
  and calls the record emitter at 0x8242EFB8 (phase-11 PE label
  0x8243D7B8). Every absolute reference is consistent in the true
  frame and inconsistent in the PE frame.

So: **true VA = phase-11 PE VA − 0xE800** for all .text addresses in
the phase-11 docs. .rdata/.data addresses (strings, the stream object
0x833FA3D0, stored table contents) are unaffected — which is why the
phase-11 semantics survived: the table *contents* it quoted are
absolute addresses and were always in the true frame. Consequences:
the translator is at true VA **0x8242F508**; the ring helpers at
**0x8242EF58 / 0x8242EF80**; the jump table at **0x8242F5F8** sits
inline at translator+0xF0, and the 13 distinct case bodies
(0x8242F638…0x82431184) are the translator's OWN inline case blocks
inside one ~0x1E00-byte mega-function — not separate functions in a
different region. That is the mechanical reason Ghidra's per-function
decompiles failed on this code in phases 10–11.

## §1 The case bodies — what each tag actually does (raw read, all 13)

Common shape (cases 0–6): take the entry's payload1 (`ld r4,
0x10(r30)`) **by value**, call the emitter 0x8242EFB8 with
(obj, payload1, flag 0x2009, extra), then append output record(s) to
the +0x818… arrays **only if** the emitter's result equals the
entry's payload0, pre-stored by the translator at obj+0x758
(`cmpld` gate). The appends write, at output index obj+0xBDC with the
×24 index idiom: a u32 tag, a flag byte, and a value from obj+0xF70.

| tag | VA (true) | insns | behaviour (raw read) |
|---|---|---|---|
| 0 | 0x8242F638 | 228 | emitter-gated append; then walks a ×4 table at entry-owner +0x1DC matching u64 keys against the +0x818 output array (dedup/insert) |
| 1 | 0x8242F9C8 | 193 | same family as 0, different key-table walk |
| 2 | 0x8242FCCC | 193 | same as 1 (byte-parallel) |
| 3 | 0x8242FFD0 | 228 | same as 0 (byte-parallel) |
| 4 | 0x82430360 | 193 | same as 1 (byte-parallel) |
| 5 | 0x82430664 | 246 | emitter-gated append ×2 key tables |
| 6 | 0x82430A3C | 119 | NO emitter call: payload1 used directly as the append value, same gate shape |
| 7–10 (shared) | 0x82430C18 | 54 | calls helper 0x8242F0D8 (the emitter's second half: appends the {0x2000B, byte 2, u64 −1} record), then appends |
| 11 | 0x82430CF0 | 109 | different family: calls 0x82420E18 + list ops 0x8242C988/0x8242C9F0 (insert/remove on a linked list rooted via obj+0x758) |
| 12 | 0x82430EA4 | 78 | twin of 13: reads tag + payload1 twice, calls 0x8242F228 + SDK 0x82B49ED4; the family's only `rlwinm` extraction acts on a call's RETURN status word, not on payload data |
| 13 | 0x82430FDC | 78 | byte-identical twin of 12 |
| 14 | 0x82431114 | 28 | minimal: payload1 → helper 0x8242F360 (single append) |
| 15 | 0x82431184 | 114 | the drain/finalize case: touches obj+0x740/+0xF6C, calls both ring helpers, exits the translate loop to the handoff (§3) |

**The decisive negative:** across all 13 case bodies (~1,900
instructions) there is **no shift/mask/rotate extraction on payload
data** — every `slwi`/`rlwinm` is index math (×24 record stride, ×4
table stride, ×2) or, in cases 12/13, a status-byte extract on a
return value. **No case dereferences payload0 or payload1 as a
pointer to a record buffer**; payloads are compared for equality
(payload0 as key) and copied whole (payload1 as value). Nothing in
this family walks a byte stream with a stride, and nothing touches
floating point.

## §2 The emitter at 0x8242EFB8 (phase-11 "record builder" — read raw)

It is an **output-record emitter**, not a payload parser. On entry it
ignores any input buffer and appends one fixed-shape record to the
output arrays at the current output counter obj+0xBDC (×24 idiom):
{u32 = 0x2000C, byte = 2, u64 = arg r4, u32 = arg r5, byte = 2,
u64 = 1} across the parallel arrays obj+0x818/+0x820/+0x828/+0x830/
+0x838/+0x840; when arg r6 == 0x2000B it appends a second record
{u32 = 0x2000B, byte = 2, u64 = −1} at +0x848/+0x850/+0x858. (This is
the source of the "+0x818…+0x858 output arrays" span: nine parallel
field arrays, one 24B-strided index space.) It reads no file data,
extracts no fields, and returns a status the cases gate on.

## §3 Payload writers — census complete (4 writers; tags 5, 6, 7, 8)

Const-prop scan for stores through the stream-object ring bases
(+0xBE8/+0xBF0/+0xBF8) over all of .text
(`phase12/tools/scan_ring_writers.py`) finds exactly **four** writer
functions (plus the emitter's output-side stores, a false-positive
class the scan separates by base):

| writer (true VA) | tag | payload0 | payload1 |
|---|---|---|---|
| 0x823D8F88 | **5** | r30 (a matched struct ptr) | r7 (a matched struct field) |
| 0x8249D2AC | **6** | r28 | r29 (posted only when r28 equals a callee's return — a match event) |
| 0x82436444 | **7** | r31 (arg) | r28 (arg) |
| 0x8241AF4C | **8** | r31 (arg) | 0 — and it first increments a counter in the array at obj+0x70 indexed by a cntlzw-derived slot |

All four post **engine-internal scalars/pointers** (match results,
counters, caller arguments). None of them reads anm file data, an
AFS buffer, or a 16B-record stream; the tag-8 writer's payload0 is a
function argument incremented from an internal counter table.
**Tags 0–4 and 9–15 have no writer anywhere in the image** under this
scan (caveat: a writer that obtained the object pointer without
materializing 0x833FA3D0 within the 48-instruction window would be
missed; both known writers and both new writers do materialize it,
so the method is calibrated on 4/4 known positives).

Output readers / handoff: the translator's finalize tail (true VA
~0x824312E4, phase-11 "sibling" region) builds a descriptor at
obj+0x740: {+0x28 = output count +0xBD8, +0x34 = &obj+0x760,
+0x38 = &obj+0x758, +0x40 = the current entry's payload0} and calls
0x8242D1C0-family consumers — i.e. translated records are handed to
the loader's task struct, not to a renderer or a skeleton.

## §4 Verdict — residual, exact (supersedes ANM-READER4's next steps 1–2)

Proven this phase: the frame correction (§0); all 13 case bodies read
(§1); the emitter read (§2); the complete ring-writer census with
payload provenance (§3). The conclusion is forced:

**The ring + translator family is a (tag, key, value) command/event
translation layer. The anm 16B records do not flow through it, are
not unpacked by any of its handlers, and cannot be reached from its
payloads.** ANM-READER4's next step 1 ("find which handler walks a
payload with shift/mask extraction") is therefore EXHAUSTED with a
negative — no such handler exists. **No bit layout is proven, no
parser is shipped, no clips are shipped** (the job's G2/G3 gate lands
as this exact residual, per its terms; no guessed layout).

What remains open, named precisely (NOT done this phase):
1. ANM-READER4/READER3 step 3: parse `D:\bin\anime_cm.bin` + one
   per-fighter `.bin` from the ISO — the per-fighter animation-
   definition layer the loader pairs with the anm files, and now the
   ONLY named route to the record→stream mapping. **Not pulled this
   phase**: the handler verdict above was reached without it, so its
   absence blocked no gated step (the job's pull condition). The ISO
   release `doa4-iso-v1` is 30 × 250MB parts; extracting one file
   needs the assembled ISO (~7.5GB) + an XISO pass — a lane of its
   own, recorded here as the standing next step, not silently
   skipped.
2. Who consumes the loader task's +0x740 output descriptor
   downstream of the finalize handoff (§3) — the loader state
   machine's caller, not yet read. It consumes translated commands,
   so it is a route to the anm *file-selection* logic (which
   `anm%d.afs` / which `.bin`), not to record bit fields.
3. The 27,392 16B head records themselves (phase-10 facts stand:
   135 distinct u32s, ch4/ch5 quantized pair) still have no proven
   field layout from any code read to date (phases 10–12).

## Job 4 note
Unchanged: material setup is not in this family (the translator,
emitter, writers and finalize touch no shader/texture state — one
more negative data point for `phase12/BINDING-DRAWPATH.md`).
