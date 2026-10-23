# DOA4 Phase 15 — Job 2: .mot stream census + decode (toward gate 2)

Source bytes: `mot.afs` from release `doa4-iso-extracts-20261022`
(container sha256
`5329bc059f52e1662dc1bbeb0541a675fa806f4f6e14cdc8c666b079d411e97a`,
re-verified at extraction). All 197 entries extracted; per-file
sha256 manifest: `phase15/mot-entries-manifest.json`; the entries
themselves are released as `doa4-mot-20261022` (see
`phase15/PHASE15-STATE.md` log). Tools:
`phase15/tools/mot_extract_census_p15.py`,
`phase15/tools/mot_census_p15.py`. Grades: PROVEN = asserted by a
tool over the stated scope; EVIDENCED = direct byte evidence,
named scope; RESIDUAL = not decoded, exact remainder stated.

## Container accounting (PROVEN, 197/197)
- `mot_version.bin` (16 B): u32 BE 1 + zeros — same shape as
  `anm_version.bin`.
- 72 fighter files: 24 basenames × (plain, `m_`, `c_`). The TOC's
  rtm plain/`c_` slots are NAMED `kasumi.mot`/`c_kasumi.mot` and
  are byte-identical copies of kasumi's (manifest hashes both TOC
  indices independently; phase-14 finding, re-verified here).
  `leifang` is spelled `leifan.*` in the attribute block.
- 124 `t_*` tag-motion files (single-clip format, §4).

## §1 The fighter .mot layout (EVIDENCED; zack triple deep-dived, census over all 72)
Every fighter .mot file is laid out as:

1. **Table A** — u32 BE ABSOLUTE file offsets at offset 0.
   Entry counts by file class (census, 72/72): plain .mot =
   **1000**, `m_` = **1004**, `c_` = **400** (24/24 exact).
   Unused slots carry the data-start offset (the "default"):
   zack 22,936 / m_zack 22,952 / c_zack 20,536. Followed by
   **8 zero bytes**.
2. **Per-fighter front block** — the span between table A + 8 and
   data-start. Byte-identical between a fighter's plain and `m_`
   files (all groups probed); the `c_` block matches in most
   fighters and is slightly shorter in some (tina: 34,200 vs
   34,224 B). Size varies per fighter (zack 18,928 B incl. the
   trailing descriptor word region; janlee 2,912 B; tina
   34,224 B). Head words are fighter-specific
   (zack `001c0000 f526ffff…`, tina `002c0000 f68f00ff…`,
   janlee `00ad0000 00000000…`). Content: RESIDUAL (packed
   sub-block data in the same encoding family as the record
   payloads, §3 — the block is shared per-fighter data, plausibly
   the track/bone layout the records reference; not decoded).
3. **Record area** — [data-start, EOF), tiled by table A's
   distinct targets (zack: 376 distinct of 1000 slots, 625 at the
   default; m_zack: 26 distinct; c_zack: 2 distinct — default +
   32,192). Record sizes from consecutive-target deltas
   (zack.mot): min 528 B, median 4,584 B, max 30,904 B.

## §2 The record descriptor: 44 channel offsets (EVIDENCED pattern)
Immediately BEFORE each table-A target sits a table of **44 u32
BE absolute offsets** (exact 44-run at 271/376 zack.mot records;
most others 39–46 by the monotonic-run probe — boundary noise
where a sub-block offset coincides with the run rule; the modal
and by-far dominant length is 44). The 44 offsets point at 44
sub-blocks tiling the span before the descriptor; sub-block sizes
run ~20–672 B. The table-A target itself is the descriptor's end
plus a small tail gap (52–88 B in the probed records). Reading:
**each record = 44 per-channel sub-blocks + a 44-entry offset
descriptor + a tail**; table A points just past the descriptor.
The default (empty) record's descriptor, at data-start−4, holds
0-based values (0, 4008, 4248, …, 22,488 — 45 words including the
leading 0): the degenerate form. Exact framing of the tail gap
and of the default descriptor: RESIDUAL.

## §3 Record payload encoding (EVIDENCED character, grammar RESIDUAL)
Sub-block payloads are packed data in a consistent encoding
family: dense bytes with frequent `ff`/`00` runs and small
delta-like fields (e.g. zack record payload at 24,844:
`00000000 000af075 fdfcf000 fdfc0000 0050264c…`; the t_* stream
at §4 shows the same texture: `00140000 0005ff00 9bc5f00c
fd45af9f ffff3e63…`). Whole-file f32 plausibility is low
(zack.mot BE 0.061 / LE 0.083) — the payloads are NOT raw f32
keyframe arrays; they are a packed/delta encoding. Decoding that
encoding is the remaining grammar work; no semantics are guessed
here.

## §4 The t_* tag-motion files (EVIDENCED head format)
`t_al_ks.mot` (31,184 B) head: `(id, offset)` u32 BE pairs —
(0x2BC, 0x2468), (0x2BD, 0x5860), (0x2BE, 0x7920) — then
`0xFFFFFFFF` separator, 4 zero bytes, then the packed stream in
the §3 encoding family. So a t_* file = a small (id → offset)
index of a few clips + their packed streams, in ONE file with no
table A / front block / descriptor layer. Census scope note: the
table-A scan over the 124 t_* files returns small counts (2–24)
because their layout is this one, not the fighter layout.

## §5 Cross-reference: .mot records vs the .bin side (PROVEN non-correspondence by count)
- zack.bin w21 clip table: **1024 entries, 584 distinct**
  targets, dominant target 435 slots, record sizes 12–588 B
  (phase-14 parser report).
- zack.mot table A: **1000 entries, 376 distinct**, 625 default,
  record sizes 528–30,904 B.
- The two tables do NOT correspond 1:1 by count, distinct count,
  or size profile: the .bin table indexes small u16 command
  scripts; the .mot table indexes large per-clip motion records.
  The engine-side link is the registry/index path proven in
  `phase15/XEX-HUNT.md` (per-fighter file set opened together;
  runtime records with id@+0x30 dispatched in the 0x22xx
  namespace). A static slot-to-slot mapping between w21 entries
  and .mot records is NOT evidenced by anything in the file
  bytes and is not claimed.
- w2/w6/w7/w28 (.bin in-file curve sections) vs .mot records:
  no offset, size, or count relation found (w-sections are
  per-fighter curve data inside the .bin; .mot records are
  1–2 orders of magnitude larger). RESIDUAL: which of the two
  data locations a given in-game clip plays from is decided by
  the loader at runtime (phase-14 step-3 verdict stands).

## §6 Gate-2 statement (honest)
**First clip NOT assembled — exact residual.** What is missing
is the §3 packed-encoding grammar: how a record's 44 sub-blocks
expand into per-track keyframe values (times + rotations/
translations). Everything AROUND that grammar is now proven:
container, tables, record framing, descriptor shape, the
engine's registry/loader mechanism (XEX-HUNT.md), and the
runtime record dispatch. Posing a skeleton from the packed bytes
today would require inventing the expansion — refused per the
no-guessed-semantics rule. Named next steps for the clip lane:
(1) expand one t_* file first (smallest grammar surface: one
index, one stream, no descriptor layer); (2) correlate a
sub-block's byte length against its key count by comparing
records for the same clip slot across the plain/`m_` pair;
(3) trace the loader-side expansion in the XEX from the
0x823FA430 cluster forward (XEX-HUNT.md §3).
