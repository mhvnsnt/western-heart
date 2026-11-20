# Anim-index join hunt — ROUND 2: per-character containers (2026-11-03/04)

Question (unchanged): where is the table mapping a character move
(rog.json / jun.json row) to an index into data004's big MOTA table
(0..1874)? Round 1 excluded data000/001/002/004/018/052. This round:
**data007–data017, data025, data027, data034–data047 — all 27 containers
scanned in their true content form. Verdict: EXHAUSTIVE NEGATIVE — no
MOTA table, no moveset section, no per-move index table in any of them.**

Per-container scan JSONs: `join-round2/dataNNN-scan.json` and
`dataNNN-true-scan.json`; scanner: `join-round2/scan_container.py`
(single-pass census of MOTA/bxml/mvlt/BXML/MVLT/NTXR/GIDX/NSXR/MBB/PCTB/
MCAM + MOTA-table parse attempts + BE-u16 index-run detection, values in
1..1874, run ≥24). Every download was sha256-verified against
`MANIFEST-ttt2.json` (release `ttt2-work-archive-2026-10-30`,
mhvnsnt/western-heart) before scanning — two truncated downloads were
caught by this check and retried. Decoded/raw copies were deleted after
scanning; the release assets are the store copies, hashes below.

## Method discovery — two container families + a passthrough trap

- **Family A — `0ff512ed` section-compressed** (head table after a
  12-byte header; BE u32 decoded size per 128 KB section). data007–017
  and data025 were genuinely decoded by the prior lane; their decoded
  forms differ from raw (verified by sha) and were scanned directly.
- **Family B — plain NRFI, stored uncompressed.** data027 and
  data034–data047 start with the NRFI `ftyp` box and walk exactly to
  EOF. For these, the release's "decoded" assets are **byte-identical
  passthroughs of the raw files** (sha256 equality proven for 027 and
  034; asset sizes equal for the rest) — there was nothing to decode.
  Proof for 027: forcing it through the section decoder produced
  garbage (600/4,678 sections EXACT, 50 MB non-NRFI output).
- The section decoder itself (`tools/ttt2-section-decode/batchdec3.c`
  from western-heart, built here with minimal windef/winbase shims —
  only `ULONG`/`LONG`/`HeapAlloc` needed) was **validated bit-exact**
  before use: data028 → 120,285,856 B, sha256
  `45e0bed0d23d8d005534168e0750be7822a020462573db7d2fe89348da2868d2`,
  780/780 sections EXACT, matching the repo decode doc exactly
  (log: `join-round2/batchdec-data028-validation.log`).

## Per-container results (true content form)

| container | form | size | sha256 (head) | MOTA | bxml/mvlt | BXML/MVLT | content class |
|---|---|---|---|---|---|---|---|
| data007 | A, decoded | 413,424,016 | e614da883f91 | 0 | 0/0 | 0/0 | NTXR×109 GIDX×1707 textures; roster name tables (`chara_rog/jun/ogr`, all chars, 16 B records) |
| data008 | A, decoded | 339,626,352 | ebb7e415f7b8 | 0 | 0/0 | 0/0 | NTXR×63 GIDX×2085 MBB×33 |
| data009 | A, decoded | 448,182,957 | 46d44c6c732f | 0 | 0/0 | 9/0 | NTXR×198 GIDX×2697 |
| data010 | A, decoded | 445,097,788 | 42617d404c16 | 0 | 0/0 | 8/0 | NTXR×193 GIDX×2621 |
| data011 | A, decoded | 524,465,047 | ecbc73cf9b49 | 0 | 0/0 | 8/0 | NTXR×245 GIDX×3053 |
| data012 | A, decoded | 389,484,780 | f34230e25c7f | 0 | 0/0 | 8/0 | NTXR×168 GIDX×2227 |
| data013 | A, decoded | 487,420,820 | 4ca6785276ec | 0 | 0/0 | 8/0 | NTXR×234 GIDX×3053 |
| data014 | A, decoded | 422,069,426 | 37f0c02e3f44 | 0 | 0/0 | 8/0 | NTXR×187 GIDX×2201 |
| data015 | A, decoded | 370,187,449 | 364be2f8a584 | 0 | 0/0 | 8/0 | NTXR×167 GIDX×2081 |
| data016 | A, decoded | 125,722,532 | e088783e89d3 | 0 | 0/0 | 6/0 | NTXR×52 GIDX×614 |
| data017 | A, decoded | 794,397,899 | 2cb2caa1dcb8 | 0 | 0/0 | 0/0 | NTXR×1044 GIDX×6722 |
| data025 | A, decoded | 703,658,432 | f48d16b1163d | 0 | 0/0 | 0/0 | NTXR×1110 GIDX×1470 |
| data027 | B, plain NRFI | 613,117,984 | ea6cc43b1d36 | 1* | 0/0 | 0/0 | MBB×30; *MOTA hit = chance bytes, count field 3,106,717,826 (rejected) |
| data034 | B, plain NRFI | 199,287,232 | 7d02b2633835 | 0 | 0/0 | 0/0 | MBB×10 |
| data035 | B, plain NRFI | 250,237,456 | aa512c807412 | 0 | 0/0 | 0/0 | NSXR×1 MBB×12 |
| data036 | B, plain NRFI | 379,630,736 | ce6e81463140 | 0 | 0/0 | 0/0 | MBB×24 |
| data037 | B, plain NRFI | 305,710,000 | b441e6c2ffb4 | 0 | 0/0 | 0/0 | MBB×20 |
| data038 | B, plain NRFI | 306,422,144 | ff72a1e4eb72 | 0 | 0/0 | 0/0 | MBB×24 GIDX×1 |
| data039 | B, plain NRFI | 464,935,296 | 1044f9acbb26 | 0 | 0/0 | 1/0 | MBB×29 |
| data040 | B, plain NRFI | 255,621,792 | 6daac181b51b | 0 | 0/0 | 1/0 | MBB×15 |
| data041 | B, plain NRFI | 436,231,024 | f14f172b1bdf | 0 | 0/0 | 0/0 | MBB×25 |
| data042 | B, plain NRFI | 326,598,144 | fc28d4085e43 | 0 | 0/0 | 1/0 | MBB×16 |
| data043 | B, plain NRFI | 302,789,856 | e4e7d90b23a0 | 0 | 1/0 | 1/0 | MBB×11; both lone hits context-checked = high-entropy chance bytes |
| data044 | B, plain NRFI | 437,646,976 | afc0757f4a44 | 0 | 0/0 | 0/0 | MBB×25 NTXR×1 |
| data045 | B, plain NRFI | 300,581,968 | 5e270373f059 | 1* | 0/0 | 0/0 | MBB×23; *MOTA hit chance, count 1,490,201,646 (rejected) |
| data046 | B, plain NRFI | 222,882,496 | f4d50b82df69 | 0 | 0/0 | 0/0 | MBB×10 |
| data047 | B, plain NRFI | 429,342,832 | 0ed493fd2049 | 0 | 0/0 | 0/1 | MBB×27; lone MVLT context = high-entropy chance bytes |

## Candidate analysis (why nothing here is the join)

- **BXML×6–9 in data009–016** are real structured subsection tags
  (context-captured in data011: record-like data, `ffffffff` separators,
  spaced ~26–60 MB apart — one per model subsection). But moveset BXML
  never appears without its MVLT partner (data018 carries MVLT×59 in
  3 MB); MVLT is 0 in every container here, and no MOTA/index structure
  accompanies them. They are model/effect parameter blocks, not
  movesets.
- **BE-u16 index runs** (values in 1..1874) occur in every container but
  read as mesh/texture data: in decoded containers the longest runs
  cluster in narrow local ranges with ±1/±2 jitter (vertex-index
  streams, e.g. data011 @146,108,840: 138 values in the 350–406 band);
  in plain containers the runs are short and low-distinct (quantized
  payload). None has the shape of a move table (~84–214 entries
  spanning 0..1874 next to a moveset section) — and there is no
  moveset section anywhere for one to attach to.
- **data007's `chara_rog`/`chara_jun`/`chara_ogr` strings** are a
  global roster name table (every character, fixed 16-byte records) —
  a UI/roster section, not per-character data.

## Verdict + what remains unexamined

The per-move → MOTA-index join is **not in any dataNNN container
examined**: rounds 1+2 together cover 000, 001, 002, 004, 007–018, 025,
027, 028 (audio), 034–047, 052. Still unexamined (small, cheap to
close): data003, 005, 006, 019, 050, 051, 053 (decoded assets already
in the release) and the plain pulls for 020–024, 026, 029–033, 048,
049. Nothing in the examined set suggests they differ in kind, but the
negative is not claimed for them.

The join most likely lives where Kiloutre gets it: the **live-memory
motbin** (`anim_addr` per move record) — i.e. the X360 executable's
loaded moveset structures, not a dataNNN file. Next steps, in order:

1. **Ghidra on default.xex**: find the MOTA loader + the moveset
   (motbin) structure; the per-move `anim_addr`/`anim_name` fields give
   the join directly, and the same binary holds the 0x64 stream
   decompression routine (the other blocker — 1,143 unique clips).
2. **RPCS3 live-memory extraction** (Kiloutre's native route) if the
   game can be run.
3. Close the small-container remainder (003/005/006/019/050/051/053)
   with the same verified scan — completeness only.

For the bank build itself: with no join, today's buildable motion is
the 4 full-body 23-track 0xC8 clips (908 frames, see TYPE-CENSUS.md) —
real TTT2 motion, but not yet assignable to specific Roger Jr./Jun
moves without the join. Do not guess assignments.
