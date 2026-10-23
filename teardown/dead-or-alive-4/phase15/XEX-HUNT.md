# DOA4 Phase 15 — Job 3: w21 opcode semantics via the REAL XEX (bounded hunt)

Binary: `default.xex` retail, sha256
`56b68dec68991f007639d796b04cb88c9aa7b484c1fce54641cdda5de4f2b98f`
(release `doa4-iso-extracts-20261022`), analyzed as
`teardown/dead-or-alive-4/workdir/default_pe.bin` (23,068,672 B).
Method: word-level instruction scan (the phase-11 proven method —
raw opcode decode over the whole file, no linear-disasm
assumptions) for pointer words, `lis`+`addi`/`ori` completions,
`cmpwi`/`cmplwi` immediates, then targeted Capstone
(BE|32) disassembly of the hit neighborhoods. Tools:
`phase15/tools/xex_hunt2_p15.py`, `phase15/tools/xex_disas_p15.py`
(first-pass `xex_hunt_p15.py` linear sweep returned zero hits —
wrong method for this binary; superseded by the word-level scan).
VA convention: true XEX base 0x82000000; .text file offset f →
VA f + 0x8200E800; .rdata f → VA 0x82000000 + f; .data f →
VA 0x82000000 + f + 0x1DE00.

## What was found (EVIDENCED from code)

### 1. The registries are data tables, not code references
- **Zero** `lis`/`addi` pairs in .text resolve into either
  registry string range — the loaders never reference the
  filename strings directly. (Exact negative, full .text scope.)
- **.mot registry table**: 196 records of **stride 0x6C (108 B)**
  at VA 0x82C69A70 (file offset 0xC4BC58); the filename `char*`
  sits at **+0x18** in each record (the 196 aligned pointer words
  at file offsets 0xC4BC70–0xC4BF7C, descending string addresses —
  reverse registry order, same as the .bin side). 196 records ==
  the 196 .mot entries of mot.afs (phase 14 accounting).
- **.bin registry table**: 25 consecutive `char*` at VA
  0x82C6B38C (file offset 0xC4D58C) — 24 fighters + anime_cm.
  No `lis`/`addi` reference to its base (±0x40) exists in .text;
  it is reached through a loaded base register (loader struct),
  consistent with phase 14's bin-table consumer cluster.
- **The .mot loader**: three code sites (file offsets 0x3832D8,
  0x3835E8, 0x384954) compute `table + 0x18` and index it with
  `mulli rX, idx, 0x6C`. The site at file offset 0x3832D8 sits in
  a loader function (VA ≈ 0x82391A80) that opens four files in
  sequence from a per-fighter struct (fields at +0x68/+0x6C/
  +0x70/+0x74, call ids 0x1EC/0x1DB/0x1DD/0x1ED into the file-open
  helper at VA 0x8238ED10), the third being the .mot name taken
  from the registry record — i.e. **the engine opens the
  .bin/.mot/m_.mot/c_.mot set per fighter through this table**,
  and .mot selection is by runtime index into the 196-record
  table, NOT by any static offset inside the .bin files. This
  closes the phase-14 open point ("the pairing is by NAME
  through the engine's registry") with the mechanism: index →
  0x6C record → name at +0x18 → open.

### 2. The 0x22xx token namespace IS dispatched in code — on runtime records
`cmplwi`/`cmpwi` against 0x22xx immediates occur at exactly 15
sites (full .text census; immediates seen: 0x2211 ×5, 0x2212 ×3,
0x2213 ×4, 0x2227, 0x2228, 0x2257, 0x227A, 0x227B). Two dispatch
neighborhoods:

- **Classifier at VA 0x82408290** (file offset 0x3F9A90, the
  bin-loader neighborhood): reads a record pointer with a type
  byte at **+0x37**, a u16 id at **+0x30**, a second u16 at
  **+0x32**. If type == 9 and id ∈ {0x2257, 0x227A, 0x227B} it
  writes marker byte 0x0A into a parallel byte map. Type 0x0C /
  0x0F, or type 9 with the +0x32 u16 in [0x4379, 0x439A], sets a
  flag byte at record +0x4E. So 0x2257/0x227A/0x227B are
  **special-marked command ids** in a ≥0x4F-byte runtime record
  format — not raw file tokens.
- **Dispatcher at VA 0x824F388C** (file offset 0x4E508C; a twin
  copy at 0x4E7068): u16 id at record +0x30 compared against
  **0x2213, 0x2212, 0x202C, 0x202D, 0x2211** — all five route to
  one handler call (VA 0x824F76E0, argument = a context pointer).
  Non-matching ids fall through to record math with strides
  **0x9C (156)** and **0x250 (592)** and a byte-class table
  lookup. So 0x2211/0x2212/0x2213 (and the 0x202C/0x202D pair)
  form one **command family handled by a single routine** in the
  in-game animation player region (0x824Fxxxx).

### 3. What this means for the w21 token scripts (graded)
- PROVEN: the engine expands .bin/.mot data into runtime records
  carrying (type@+0x37, id@+0x30, sub@+0x32); the 0x22xx ids are
  dispatched there. The w21 u16 token streams in the .bin files
  share the 0x22xx namespace with these runtime ids (phase 14),
  so the token→record expansion happens in the loader path
  between the file bytes and these dispatchers.
- NOT proven (exact residual): the per-opcode semantics of the
  w21 token script itself (which token writes which runtime
  record field; the operand grammar after each 0x22xx token).
  The compares found name only a handful of distinguished ids
  (0x2211–0x2213, 0x2227, 0x2228, 0x2257, 0x227A, 0x227B) — the
  bulk of the namespace is handled by table-driven code (the
  byte-class/stride math in the dispatcher), not by per-opcode
  compares, so a compare census cannot enumerate the grammar.
  The next bounded step (named, not done here): trace the
  loader-side expansion — the function that reads a w21 record
  and emits +0x30/+0x37 records — from the .bin loader cluster
  (VA 0x823FA430 neighborhood, phase 14) forward.

## Search scope (for the negative claims)
Whole .text (0x86AE00 B) word-scanned for: pointer words into
both registry ranges (221 found, all in the two tables above);
`lis`(op15,rA=0) = 109,600 sites, each completed over the next 8
words for addi/ori into the registry ranges (0 hits) and into
the two table bases ±0x40 (3 hits, all .mot table +0x18);
`cmpwi`/`cmplwi` immediates in {0x400, 0x3E8, 0x3EC, 0x190, 0x2C}
∪ [0x2200, 0x22FF] (115 hits; the 0x22xx subset is the 15 sites
above; 0x400 ×39, 0x3E8 ×20, 0x2C ×35, 0x190 ×6 are generic —
none sits inside the two dispatch neighborhoods except the
0x2C compares at file offsets 0x3FAE04/0x3FAFE0/0x3FB004, in the
bin-loader neighborhood, noted as candidates for the
44-entry-descriptor walk but NOT claimed as such).
