# DOA4 Phase 11 — Job 1: PPC constant scan → ANM reader family FOUND (G4 narrowed to the record consumer)

## The phase-10 blocker was a wrong image base — root cause found and proven

Phase 10 concluded "ZERO code xrefs exist (PPC computed addressing); xref hunting is EXHAUSTED."
That was an artifact. The Ghidra project loads `default_pe.bin` at image base **0x400000**
(the value stored in this decrypted PE's header), so every address phase 10 quoted is
`RVA + 0x400000`. The game's code materializes **true VAs at load base 0x82000000**
(standard Xbox 360). Conversion: `true VA = Ghidra address + 0x81C00000`;
`true VA = file offset + 0x400000` inside `.rdata` (raw == RVA there).

Proof, all re-verified this session from the raw file
(`teardown/dead-or-alive-4/workdir/default_pe.bin`, 23,068,672 bytes):

- `d:\anm.afs` string at file **0x21E940** = Ghidra 0x61E940 = true VA **0x8221E940**.
- PE sections: `.rdata` RVA 0x400 raw 0x400; `.text` RVA 0x2E0000 raw 0x2D1800;
  `.data` RVA 0xB60000 raw 0xB42200. `VA(fileoff) = 0x82000000 + RVA`.
- lis census over the whole file: 125,718 lis instructions; the top immediates are
  0x822B (21,205), 0x8302, 0x8218, 0x8205… — code lives at 0x82xxxxxx, as expected.
  With phase-10 (rebased) watch values the scan finds **0** pairs; with true VAs it
  finds **22** (below). A Ghidra-side scan would have needed the same correction:
  the constants in the instruction stream are true VAs regardless of project base.
- Phase 10's "5 data-side descriptor pointers" (e.g. bytes `00 61 E9 61` at file
  0x766B1) are **false positives** of the unaligned byte scan: the same locations are
  float-constant-pool data (code loads them with `lfs`), and no aligned stored
  pointer to any table entry exists anywhere in the file. The one real stored-pointer
  fact: the value **0x8221E940** (&"d:\anm.afs", true VA) is stored at six `.data`
  file offsets (0xC2B22C, 0xC4A22C, 0xC4EDDC, 0xC50914, 0xC6CE04, 0xC6E93C →
  true VAs 0x82C4902C, 0x82C6802C, 0x82C6CBDC, 0x82C6E714, 0x82C8AC04, 0x82C8C73C) —
  per-file descriptor structs referencing the anm path string.

## Scan method (the deliverable scan)

`phase11/tools/capstone_scan.py` (v1, rebased values — negative, kept for the record),
`phase11/tools/capstone_scan3.py` (v3, true VAs, section-aware): prefilter on raw BE
words for `lis` (opcode 15, rA = 0) with a watch-reaching high half, then a 32-instruction
linear constant-propagation (addi/addis/ori/oris/mr + memory `disp(base)` effective
addresses) per lis. `phase11/tools/PpcConstantScan.java` is the Ghidra twin (its watch
table is stated in true VAs in this doc; the committed script predates the base fix —
use the Capstone numbers as canonical). Full hit list: `phase11/tools/capstone_hits3.csv`.

## Scan yield — the reader family (true VAs; Ghidra = true − 0x81C00000)

| Site (lis) | Materializes | Meaning |
|---|---|---|
| 0x8243D650 | **0x82285F3C `anm%d.afs`** | the anm loader (below) |
| 0x824EF3A0 | 0x8221E9D0 `D:\DOA4\` | base-path builder |
| 0x82384180, 0x823FF544 | 0x8221E9DC `cache:\` | cache-path / descriptor-table walkers |
| 0x82563690, 0x825AB6D8, 0x825B5538, 0x825CC900, 0x825E77B0, 0x82647898, 0x826F87B4, 0x82A5E848… | 0x8221E890 (file-table struct base) | file/volume system users (vtable dispatch, struct init) |

File table (true VAs, from `.rdata`): pairs `cache:\X.afs` / `d:\X.afs` for spr, snd,
mot, cmn, avt, stg, chrthree, chrtwo, chrone at 0x8221E8CD–0x8221E9DC; **anm has only
`d:\anm.afs` @ 0x8221E940** (no cache twin), then `D:\DOA4\` @ E9D0 and `cache:\` @ E9DC.

Decompiles of all 13 candidate functions (+ callees, 19 files) are committed in
`phase11/decomp/` (Ghidra-created functions at `.pdata`-derived entries — the project
had NO functions over most of `.text`; `.pdata` here is 8-byte entries
`{begin u32, packed u32}`, 15,054 begins, sorted).

## The anm loader (function fragments around true VA 0x8243D428–0x8243D800)

An asynchronous load state machine over a task struct (r30; state at +0, sub-object
at +0x744, anm index at +0x748, stream descriptors at +0xF74, stream cursor pair at
+0xBE0/+0xBE4). Read from the raw disassembly this session:

- **State 3** (0x8243D5C4): scans a wide-char (UTF-16) file list for the substring
  `anm` (compares lhz against 0x61/0x6E/0x6D), then formats names into a stack buffer:
  `sprintf(buf, "%ls", <matched entry>)` (fmt @ 0x82285F38) and
  `sprintf(buf, "anm%d.afs", index)` (fmt @ 0x82285F3C), where index = task +0x748.
  The pattern string at 0x82285F24 is the UTF-16 wildcard **`anm*.afs`**.
  So at runtime the game enumerates `anm*.afs` files and loads them per index —
  `anm.afs` itself plus per-character `anm%d.afs` siblings.
- **State 4** (0x8243D4A0): when the global engine state (+0x10 of the object at
  0x82E5B450) equals 10 and the task's stream flag (+0xF6C) is set, it zeroes a
  descriptor array at task +0xF74 (count from the loaded header at +0x64) and calls
  the stream-build routine at 0x8295F7D0, then transitions to state 8.
- **Stream advance** (0x8243D758, a standalone helper): over a GLOBAL stream object
  at **0x82C3A3D0**, reads cursor [obj+0xBE0] and end [obj+0xBE4]; if cursor < end,
  **cursor += 0x20** and returns end − cursor. The stream the loader walks is
  **0x20-byte-strided** — consistent with pairs of the 16B head records, or with a
  32B stream element in the payload; the record consumer reads through this cursor.
- **State 8** (0x8243D724): polls a handle at task +0xF74 against sentinel 0x3E5,
  calling the wait/finalize routine at 0x8278A308.
- The state-4/0x8A completion path calls the small routine at **0x8243DD08**
  (bl from 0x8243D6E4) — the first consumer-side candidate not yet read (below).

Supporting cast (decompiled, in `phase11/decomp/`):

- FUN @ 0x82383F28 walks a **file-descriptor table at .data 0x82C6CD7C, stride 0x1C
  (7 u32/entry), up to 0x117 entries**, and opens `cache:\` (FUN_00b8be90) — the
  disc/cache file manager the loader's paths feed into.
- FUN @ 0x823FF420 walks the same 0x82C6CD7C table (10 entries) calling device
  functions, then opens `cache:\` via FUN_00db4468.
- FUN @ 0x82647880 builds a volume/struct whose first field is **0x8221E890** (the
  file-table base) — file-system object init, not animation.
- Per-character animation definition files exist as strings beside the anm strings:
  `D:\bin\anime_cm.bin`, `D:\bin\<fighter>.bin` (sambo, koryu, ryu, kasumi, ayane,
  leifang, bass, bayman, genfu, janlee, tina, zack, lisa, hakyo, hika, ninja, boy,
  tengu, spartan, alpha…) and `D:\dat\version\anm_version.bin` @ 0x82278670. The
  `.bin` set is the per-fighter animation-definition layer paired with the anm files.

## Reader verdict — NOT yet cracked; residual is now one function deep

No parser is claimed and **no clips shipped** (gate discipline: no proven bit layout,
no speculative clips). What is proven: the loader family, its file enumeration, its
stream object and stride, and exactly where the record consumer hangs off it.
What is still unknown: the bit-level field layout of the 16B head records and the
record→stream mapping (phase-10 facts stand: 27,392 records, 135 distinct u32s,
ch4/ch5 quantized pair on a (v+1)%32 grid, BE confirmed, uniform-width bit-unpack
refuted).

Exact next steps, in order:
1. Create + decompile the function at true VA **0x8243DD08** (Ghidra 0x83DD08) and
   the stream-build routine at **0x8295F7D0** (Ghidra 0xDF57D0); read them for the
   shift/mask network over the 0x20-strided stream.
2. Trace writers/readers of the global stream object at **0x82C3A3D0** (+0xBE0
   cursor): every function materializing 0x82C3A3D0 is a consumer candidate
   (same lis/addi scan, one more watch value).
3. Parse `D:\bin\anime_cm.bin` + one per-fighter `.bin` from the ISO: they are the
   definition layer the loader pairs with anm data and may carry the stream table
   (counts/offsets) that the 16B records index.

## Job 4 note (binding, material route)

The constant scan exposed the **file system**, not the renderer's material setup:
none of the 13 candidate functions touches shader/texture state (the two
struct-heavy ones are the volume init @ 0x82647880 and a vtable dispatch through
the table base @ 0x825625A0). Per the job's terms this lands as a **negative**:
the material-setup path is NOT in the file-table/reader family, no decl→texture
rule was read, and the proven set stays exactly 3 (chrone pkg00 decl1→tex30,
decl12→tex40, decl30→tex40). Refuted routes were not re-run.

## ADDENDUM (same session, from the shared scratch — parallel-lane output merged in)

A second lane worked this phase in the same scratch (see PHASE11-STATE.md
collision note). Its Ghidra outputs (`p11/decomp2/`, `p11/decomp3/`) add one
verified step and two warnings:

- **0x8243DD08 is a tail-call thunk** → FUN at true VA **0x829FD490**
  (Ghidra 0xDFD490), which Ghidra cannot decode from that seed
  ("bad instruction data" — the region is data-interleaved or VMX-mixed).
  The anm completion path therefore continues at **0x829FD490**; it needs a
  Capstone linear read, not a Ghidra decompile, as the next step.
- WARNING — two files in `p11/decomp2/` and `p11/decomp3/` are WRONG-ADDRESS
  seeds and must not be cited as the stream-build routine:
  `func_00df57d0` (seeded 0x829F57D0) and `func_00d757d0` (seeded
  0x829757D0, a VMX vector-convert math routine). The loader's stream-build
  call is **0x8295F7D0** → Ghidra address **0xD75F7D0**; it is still unread.
- The parallel lane also ran `p11/scan_streamobj.py` tracing materializations
  of a global at 0x82C374E8 (hits in `p11/streamobj_hits*.csv`) — a different
  global than the loader's stream object 0x82C3A3D0; not yet interpreted.
