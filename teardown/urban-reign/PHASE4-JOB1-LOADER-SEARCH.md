# Urban Reign Phase 4 — Job 1: pool assignment via loader evidence (CLOSED SEARCH)

Question: how does the game decide which general-pool motions belong to a
fighter without a pmot bank (the 41 proxy fighters)? Rule required from
loader code or a file table — never motion-content similarity.

## Verdict

**No per-character assignment table exists in the shipped data for the 41.**
Every file-level source that could carry one was read this phase; all of
them either (a) cover only the 31 pmot fighters, or (b) contain no
character dimension at all. The evidence points the other way: fighters
without pmot banks have no individual move lists in the shipped data —
they draw on the shared general pools wholesale, selected at runtime by
global motion ID (the same ID space the motdat records and the
`general_index` files use). **Native count unchanged: 31/72.** No clips
were assigned, per the no-guessing rule.

## Evidence (all byte-level, this phase)

1. **gyuindex.bin** (8,284 B, fetched fresh from the ISO release
   `urban-reign-iso-v1` and verified byte-identical to the phase-2 repo
   copy): 109 fixed 76-byte entries `[32B gyu name][32B pmotID name]
   [u32 size][u32 offset][u32 flags]`. Entries are populated ONLY for
   the 31 pmot characters (001–005, 016, 020–022, 030–032, 041–046,
   054–063, 070–072 — with 064–069 carrying a shared dummy tail
   `dc7a0600 202a0000` and no PPK in the AFS) and 10 tmot entries.
   **All 41 proxy fighters' slots are all-zero** (empty names, zero
   tail). There is no hidden per-character bank reference for them.
2. **gyuindex_ppk.bin** (3,467 B, byte-identical to repo copy): same
   structure in PPK form; same 31 + 10 populated, rest empty.
3. **general_index files** (`tec/motion/{normal,30frame,weapon}/
   general_index`, fetched fresh): exactly one u32 per bank motion
   (342 / 373 / 114 — count parity with the banks), strictly increasing
   global motion IDs (normal 10..1054, 30frame 0..767, weapon 0..168).
   They map bank slot ↔ global ID. **No character field exists.**
4. **motdat census** (DVD000 AFS map, 2,431 entries): per-player
   `motdatP<N>` lists exist ONLY for N in the pmot set (1–5, 16, 20–22,
   30–32, 41–46, 54–63) plus `motdatT1..T11` for tmot — in all three
   test trees (test / test30 / wptest). No `motdatP` list exists for
   any of the 41 proxy fighters. Per-player move lists were only ever
   authored where pmot banks exist.
5. **SLUS_212.09 strings** (MD5 `0fa29bd55638f9ebe49feb494d4decd5`):
   `kg_human.cpp` / `kg_objdata.cpp` / `you_motdat.cpp` appear only as
   debug source-path strings. A separate table of named `.gyu` files
   exists (`000_BRAD1.gyu`, `003_GLENN.gyu`, … `061_BORDIN2.gyu`,
   `069_KG.gyu`, `070_KIDNAPPER_A.gyu`, `071_KIDNAPPER_B.gyu`,
   `096_97.gyu`…; 66 names) — **none of these files exist in the
   DVD000 or DVD001 AFS maps**, so they are not a shipped per-fighter
   motion source for the 41 (they belong to a non-AFS context, e.g.
   the demo/facial tooling whose data does ship under `tec/demo/`).
6. **Loader-code xref scan** (byte-level MIPS scan of the ELF,
   performed this phase after two Ghidra headless attempts failed in
   this environment — run 1 OOM-killed during auto-analysis, run 2
   import failure): `lui`+`addiu`/`lw` pairs referencing the
   `tec/motion` filename-string page (vaddr `0x6fd4xx`: `general.gyu`,
   `general_index`, `motdat`, `gyuindex.bin` neighbours) cluster at
   file offsets `0x1a8e38–0x1a91c0` (vaddr ≈ `0x2A7E38`). This is the
   filename-table loading path for the shared pools; at string level
   it references the pool filenames as a set, with no per-character
   filename construction (`pmot%03d`-style) anywhere in the string
   table — pmot loading is driven by the gyuindex slot table (item 1).

## What was NOT obtained

A Ghidra decompilation of the `kg_human` motion-selection function:
both headless attempts died in this VM (7.9 GB RAM, ~1.2 GB free;
auto-analysis OOM-killed, second import failed on the packed-db
cache). The file-table evidence above is complete without it, but the
decompile remains the one loader-code read not landed.

## Exact remaining evidence source (spec)

Runtime selection (which global IDs a proxy fighter actually uses) is
only observable in a running game. Spec: PCSX2 with the retail disc
image (ISO release `urban-reign-iso-v1`, SLUS_212.09 MD5 above) →
select a proxy fighter (e.g. CHAR006) in versus/training → attach the
PCSX2 debugger / use a Lua memory reader → break on the `.gyu` sampler
entry (phase-2: `FUN_00292670` in SLUS vaddr space; root-track getter
`FUN_00299130`) → for each distinct move the fighter performs, record
the bank pointer + motion index argument at sampler entry → map bank
pointer to {pmot / general_normal / general_30frame / general_weapon}
by the pointer's source buffer, and motion index through
`general_index` to the global ID. One full movelist pass per fighter
yields its true assignment set — that capture, and only that capture,
can promote a proxy fighter to native. Estimated one fighter ≈ one
session; the 41 share archetype pools, so capturing ~6 archetype
representatives first would bound the rest.
