# DOA4 Phase 14 — ANM semantic decode from the REAL definition files

Source data: the 26 definition files extracted in phase 13 from the
ISO's actual `anm.afs` (standard AFS container, XDVDFS sector
416009), released as `doa4-anime-definition-20261022`. Local copies
(`p13/definition/`) re-verified at this lane's start against
`phase13/definition-manifest.json`: **all 26 sha256 + sizes match**
(Job 2 step 0). The phases 7–12 "anm.afs" (head `c1ff2852…`) is a
different pressing's file and is NOT used anywhere in this decode
(phase-13 pressing correction; its mirror-vs-ISO quantification is
in `phase14/PROVENANCE.md`).

This doc follows `phase13/ANM-DEFINITION-2.md` §3's five steps.
Every claim is graded: PROVEN (asserted by a tool over all files),
EVIDENCED (direct byte evidence, named scope), or RESIDUAL (not
decoded; exact remainder stated). No semantics are guessed.

## Step (1) — the 34-word fighter header: PROVEN section table

Phase 13 read the header as "34 u32s, word 0 = 136, then section
magnitudes". The magnitudes are **file offsets**, not sizes:

- Header = `u32 header_size` (136 in all 24) + **32 big-endian u32
  file offsets** (w1–w32, the section pointer table) + `u32 0`
  terminator (w33). 1 + 32 + 1 = 34 words = 136 bytes exactly.
- Pointers may be **null** (w22 = 0 in all 24 files; w23 = 0 in
  zack.bin — zack lacks that section) or **aliased** (w9 = w10 =
  w11 = w12 in all 24 files: four pointers at one table).
- Sorting the distinct non-zero pointers (plus 136) **partitions
  [136, filesize) with no gaps and no overlaps in all 24 files** —
  the "boundaries proven by magnitudes summing to file size" test
  the task named, in offset form: section sizes (next-pointer
  minus pointer) sum to filesize − 136 exactly, 24/24.
- Tool: `phase14/tools/anm_parse_p14.py` (report:
  `phase14/tools/anm_parse_p14_report.json`).

### Section map by pointer index (roles; evidence in §"Section evidence")

| ptr | label used here | content (evidence grade) |
|---|---|---|
| w1 | K id table | u32 entries, low u16 stepping +4 — an id series (EVIDENCED) |
| w2 | B keyframe-record stream | interleaved header/payload records, `0xFFFFFFFF` separators, f32 0.3 / 1.0 fields, u16 payloads (EVIDENCED; grammar RESIDUAL, see step 4) |
| w3 | C s16 table | s16 pairs (`00a2 00a6…`); size ∈ {192, 240, 264, 288, 336, 384, 456} (multiples of 24) (EVIDENCED) |
| w4 | E records | small records carrying f32 fields; size ∈ {96…256 step 32} (EVIDENCED) |
| w5 | F u16 id table | ascending u16 ids (head `42ec 42ed 42ee…` in zack/rtm) (EVIDENCED) |
| w6 | G curve section | f32 data, first f32 = 0.9 (`3f666666`) in zack/rtm (EVIDENCED) |
| w7 | H curve section | f32 data, first f32 = 1.1 (`3f8ccccd`) in zack/rtm (EVIDENCED) |
| w8 | I table | head `001e 0000 07ff 0606 00000000 ff000000` in zack/rtm (EVIDENCED) |
| w9–w12 | T offset table | u32 ABSOLUTE file offsets pointing into the w28 span (zack head `0000b058 ×3, 0000bd2c`); span 2,788–3,636 B (PROVEN pointer target range, zack/rtm + parser bounds) |
| w13 | X13 offset table | u32 absolute offsets into the w9 span; 124–216 B (31–54 entries) |
| w14 | X14 offset table | **136 B = 34 u32 in all 24 files** (fixed) |
| w15 | X15 offset table | **64 B = 16 u32 in all 24 files** (fixed) |
| w16 | X16 offset table | **64 B = 16 u32 in all 24 files** (fixed) |
| w17 | X17 offset table | 40/44/48 B = 10/11/12 u32 |
| w18 | X18 offset table | **80 B = 20 u32 in all 24 files** (fixed) |
| w19 | X19 offset table | **456 B = 114 u32 in all 24 files** (fixed) |
| w20 | S sparse section | ~90% zero bytes; 7,744–13,456 B (EVIDENCED) |
| w21 | CLIP command table | **1024 u32 absolute offsets** + command records (PROVEN structure, below) |
| w22 | — | null in all 24 files (PROVEN) |
| w23 | Y23 EOF table | near-EOF table; null in zack.bin only |
| w24 | Y24 EOF section | ends 4–12 B before EOF (the tail word w27 sits inside its end zone in most files; in bayman/sambo/spartan w27 instead points into the w25 cluster — per-file variance recorded in the parser report) |
| w25/w26/w29 | parameter cells | pointers at individual u32 cells inside the small table preceding w28 (rtm: four consecutive cells 18284/18288/18292 with w28 at 18296); values are per-fighter parameters (`ffff0000` sentinels; zack w29 cell = `02780014`) (EVIDENCED) |
| w28 | L curve-pair stream | `(u32 flag, f32 value)` pairs, head `0000ff00 3f8ccccd` (flag + 1.1) in zack/rtm; 72 B – 17,332 B (EVIDENCED) |
| w30 | T sub-table | u16-pair sub-table INSIDE the w9 span (zack head `01f0 00fc 01f1 00fc…` = (496, 252), (497, 252)…) (EVIDENCED) |
| w31 | J token stream | command tokens sharing the `0x22xx` id namespace with anime_cm.bin (zack head carries `2210`, `5000` tokens) (EVIDENCED) |
| w32 | D s16 table | s16 pairs (`00aa 00aa 00ae 00ae…`), 392–1,208 B (EVIDENCED) |

Fixed-size tables (w14 = 34, w15/w16 = 16, w18 = 20, w19 = 114
entries in EVERY fighter) are the strongest skeleton-correlation
candidates (track/joint-group counts); no joint assignment is
claimed from counts alone.

### The w21 clip table (PROVEN structure)

- 1024 entries × u32 = 4,096 B at w21; **every entry is an absolute
  file offset ≥ w21 + 4096** (asserted 24/24 by the parser), i.e.
  the table indexes records in its own section's data area.
- Distinct targets per fighter: 14 (rtm) – 743 (alpha); one target
  dominates (rtm: 1,011/1,024 entries at the first data record —
  the default/empty record; alpha: 263/1,024). Record sizes
  (next-distinct-target deltas): min 12 B, median 72 B, max 588 B.
- Records are u16 token scripts. Alpha record 0 (20 B):
  `00000000 0001 0002 000a 0001 02b3 0046 0083 ffff`; the 400 B
  record is a repeated instruction pattern
  (`000a 0000 0001 XXXX 0001 YYYY` × many, terminated `ffff 0000`).
  Opcode-level semantics: RESIDUAL (step 4).

## Step (2) — .bin ↔ fighter identity

- **File identity: PROVEN.** The 24 basenames are the AFS filename
  block entries AND the XEX `D:\bin\*.bin` registry strings
  (file offsets 0x27849c–0x278670 in `default_pe.bin`). The XEX
  registry order is the exact reverse of the AFS entry order
  (anime_cm first ↔ last), an independent cross-check of the set.
- **Character identity: direct-name subset PROVEN-grade, style
  names TENTATIVE.** Direct: zack, tina, janlee, ryu, kasumi,
  genfu, bayman, bass, leifang, ayane, lisa, tengu, spartan,
  alpha. Style/system names (the file names a fighting style or
  system slot, not a person): karate, ninja, suiken, sambo,
  hakyo, gokei, koryu, hika, boy, rtm. Cross-evidence for the
  tentative set: the XEX `SOUND\voice_*_stream.xwb` roster codes
  (bay, kor, cri, bra, spa, tng, alp, lis, boy, aya, lei, hyt,
  hak, bas, leo, hel, gen, kas, ryu, ein, jan, tin, zac) — e.g.
  suiken (drunken fist) ↔ bra (Brad Wong), hakyo ↔ hak,
  koryu ↔ kor are correlations, NOT proofs, and are labeled
  tentative wherever used. `rtm` is the smallest file (61,844 B,
  14 distinct clip targets) and has no voice stream — consistent
  with a system/attract entry, stated as correlation only.
- **Package identity: NOT resolved by this lane.** Which chr
  package renders which fighter remains the phases 8–12 state
  (0 certain names; tentative families) — the .bin decode does
  not change it, and no package↔.bin pairing is claimed.

## Step (3) — where the animation data lives

Three data locations, each EVIDENCED:

1. **Inside the .bin files themselves**: the B stream (w2), the
   G/H curve sections (w6/w7), and the L curve-pair stream (w28)
   carry the per-fighter keyframe/curve data; the T/X offset
   tables (w9, w13–w19, w30) index shared curve blocks by
   absolute file offset (a pointer web inside the file — target
   ranges verified for zack/rtm, bounds asserted 24/24 for w21).
2. **anime_cm.bin** (177,580 B): the COMMON definition file.
   Sparse 136 B header — nonzero BE u32 words only at +4 (3592),
   +0x20 (3744), +0x50 (116,112), +0x54 (116,752) — then a token
   stream in the same `0x22xx` id namespace as the fighters' J
   sections (byte-equality 0.813 at lag 16, phase 13). It pairs
   with `comon.mot` the way each fighter .bin pairs with its
   .mot files (below). Record-level grammar: RESIDUAL.
3. **mot.afs** (75,393,024 B, XDVDFS sector 417449): the motion
   stream volume — and, contrary to the phase-13 description
   ("float data from byte 0, no filename block", which must
   have sampled past the header or a non-ISO copy), **the ISO's
   mot.afs is a standard AFS container with 197 NAMED entries**
   (magic `AFS\0`, count 197, attribute block at 75,382,784;
   TOC parsed this phase, `phase14/tools/mot_toc_p14.json`):
   `mot_version.bin` (16 B) + per-fighter triples
   (`<name>.mot`, `m_<name>.mot`, `c_<name>.mot` for all 24 .bin
   basenames; e.g. zack.mot = 2,097,528 B, m_zack.mot =
   676,120 B) + 124 `t_*` tag-motion files (`t_tn_*`, `t_ha_*`,
   `t_bo_*`, `t_go_*`…). Accounting against the XEX registry's
   195 distinct `D:\bin\*.mot` names: mot.afs holds 196 .mot
   entries; the registry's `comon.mot` is NOT among them — it
   lives in **cmn.afs** (7 entries: cmn_version.bin, comon.mot
   3,189,024 B, efc0.tpr, rtmlight.bin, rtmwatch.bin, dmy.bin,
   cam_raw.bin — TOC read this phase from the phase-13 whole
   extraction). Two container quirks, both byte-verified:
   (i) the leifang triple is spelled `leifan.*` in the
   attribute block; (ii) rtm's plain and `c_` slots (TOC
   indices 67/69, labeled `kasumi.mot`/`c_kasumi.mot`) are
   **byte-identical copies of kasumi's entries** (sha256
   9e440be07a41… / ec163cdaec35…, sizes 2,380,944 / 84,696) —
   only `m_rtm.mot` is rtm's own data; the engine addresses
   AFS entries by index, so the name labels are informational.
   So the per-file framing the task asked to name is the
   standard AFS framing itself: each .mot is directly
   extractable by TOC offset/size (done for the zack triple in
   this lane's scratch). The .bin definitions still contain
   no static offset into mot.afs — the pairing is by NAME
   through the engine's registry — and the .mot INTERNAL
   stream grammar is the remaining decode (step 4 residual;
   zack.mot head: u16 pair (24, 1391), then f32 −128.0, a
   zero field, and a record stream carrying clean f32 values
   85.0 / 3.375 — grammar not yet proven). Extracted whole
   from the assembled ISO in this phase (sha256 in
   PHASE14-STATE.md Job 1 extracts) and released so the
   stream decode has its bytes outside the ISO.

So the answer to the task's (c) is dual: the definition files
carry their own curve data (in-file), AND the per-move motion
streams live in mot.afs under the 195-name registry. Which of
the two a given clip plays from is decided by the engine's
.bin/.mot loaders at runtime; the static split proven here is
the in-file pointer web + the registry↔volume pairing.

## Step (4) — parser + gates

- **Parser**: `phase14/tools/anm_parse_p14.py` — parses the
  header pointer table, tiles sections, decodes the w21 clip
  table bounds, parses the anime_cm header words.
- **Gate 1 (structural round-trip): PASS, 24/24.** Re-serializing
  header + sections in offset order reproduces every fighter
  file byte-exactly; section sizes sum to filesize − 136 in
  every file; all 1024 clip-table targets per file lie inside
  the w21 data range. (Report:
  `phase14/tools/anm_parse_p14_report.json`.)
- **Gate 2 (first clips on a phase-6 skeleton): NOT CLAIMED —
  exact residual.** What is missing is the keyframe grammar:
  (i) the B-stream record grammar (header fields ↔ joint/track
  index ↔ key times/values — the stream interleaves 56–172 B
  header blocks carrying f32 0.3/1.0 fields and u16 payload
  blocks terminated by `0xFFFFFFFF`, and the split rule is not
  yet proven); (ii) the mot.afs per-file framing (the 195-name
  registry has no static offsets); (iii) the joint order that
  the fixed tables (34/16/16/20/114 entries) index. Posing a
  skeleton from any of these today would be guessing values
  into joints — refused per the no-guessed-semantics rule.
  Named next steps for the clip lane: (1) recover the .bin
  loader's section dispatch in the XEX (the bin-table consumer
  cluster at 0x823FA430+ reads the registry; the section-pointer
  consumers are the next Capstone target — header offsets give
  the immediate constants to hunt: loads at +0x08 (w2), +0x54
  (w21), +0x70 (w28) from a file base); (2) frame mot.afs by
  correlating its float-stream boundaries with the .mot
  registry order and the .bin clip counts; (3) only then map
  B-stream records to skeleton tracks and pose gate 2.

## Anime_cm header residual (exact)

Nonzero words {+4: 3592, +0x20: 3744, +0x50: 116112, +0x54:
116752}. 3744 − 3592 = 152; 116752 − 116112 = 640. Whether these
are two (offset) pairs into its token stream is UNPROVEN — the
fighter-file header grammar (32 pointers) does NOT transfer
(anime_cm's header is sparse by construction). Landed as values
only.
