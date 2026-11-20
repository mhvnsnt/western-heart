# KoC2 English — WORKLOG

Owner: Mars (mhvnsnt). Lane: Muse subagent, 2026-11-19.
Goal: a patched English King of Colosseum 2 (PS2, Japan-only) that plays in
PCSX2, English by default in the Universal Console; Japanese original stays
as an option. KoC2 is first (Toukon Retsuden + VPW2-completion are separate
later lanes — NOT this lane).
Workdir: `~/workspace/koc2-english/`.
Repo home (tools + translation tables only, never ROMs/ISOs): western-heart,
branch TBD (extraction lane used `muse/koc2`).
Patched ISO home: Oracle VM `/home/ubuntu/koc2-english/` (never in git).

## Starting point (from Lane E, extraction — WORKLOG in
## ~/workspace/grok-declined-items/lane-koc2/WORKLOG.md, complete 2026-11-19)
- ISO + full extraction on disk: `~/workspace/grok-declined-items/lane-koc2/extract/`
  (49,214 files; ISO 4,593,778,688 B, sha256 7daa1f8c...).
- Parsed text (copied to `data/`): koc2-strings.json (file 02010, 4,021
  strings), koc2-commentary.json (file 02030, 8,983 lines), koc2-music.json.
- Tools (copied to `tools/`): kc2_extract.py, koc2_lzss.py (decoder),
  koc2_strings.py, koc2_text.py, koc2_tables.py, kc2_afs.py,
  tim2_decode.py, kc2fire_inspect.py.
- Reference: docs/faq-koc2-jerrold.txt + docs/faq-neoseeker.html
  (Jerrold Ng's FAQ/Movelist — already translates menus + movelist).

## Milestones
1. PIPELINE PROOF — LZSS encoder + container rebuild + ISO rebuild, proven
   by round-trips (rebuilt untouched archive byte-identical; modified
   archive re-extracts correctly). Boot verification path TBD.
2. PLAYABILITY TRANSLATION — menus, move names, wrestler names, mode text.
3. FIRST PATCHED ISO — English-by-default ISO, verified booting if possible.
4. COMMENTARY (phase 2) — 8,983 lines translated, added to the patch.

## 2026-11-19 (evening)
- Lane start. Read Lane E WORKLOG + koc2_lzss.py + kc2_extract.py +
  koc2_strings.py + koc2_text.py. Copied tools + parsed data + FAQ refs
  into this workdir (Lane E's files untouched).
- KEY FINDING: the text files are stored RAW, not LZSS-compressed.
  KC2FIRE.000 index: file 02010 (strings) flags 0x00000001, stored
  198,656 / decomp 197,125; file 02030 (commentary) flags 0x00000001,
  stored 331,776 / decomp 331,155; file 01454 (music) same, flags 0x1.
  So the string-table re-insertion does NOT need the LZSS encoder —
  only the container rebuild. The encoder is still built (milestone 1
  asks for it; needed later if a compressed file ever needs replacing,
  e.g. TIM2 menu textures).
- Container facts (from kc2fire000/index.csv): all 7,519 stored_sizes
  are multiples of 32; 1,620 are also multiples of 2048 (incl. the
  text files: 02010 = 97x2048, 02030 = 162x2048, 01454 = 12x2048).
  Offsets are perfectly contiguous (0 gaps); data_start 120,832 +
  span 244,320,256 = archive size 244,441,088 exactly. Flags have
  many low-bit variants (type field?) + bit 16 = LZSS; text files are
  0x00000001. Changed files keep their original flags.
- ISO facts: 12 files + 2 folders; ONLY a primary volume descriptor
  (sector 16) + terminator (sector 17) — no Joliet/SVD, so a surgical
  ISO patch touches one directory tree. SYSTEM.CNF: BOOT2 =
  cdrom0:\SLPM_656.02;1, VER 1.03, VMODE NTSC. KC2FIRE.DIR is 52 bytes
  (contents TBD — see below). ISO has a 4096-byte tail past the
  ISO9660 end (preserve it; patch in place, don't rebuild the ISO).
- String table structure (file 02010): header (25 cats, 4,021 strings,
  68,237 table bytes) + category index (25 x 8 B) + data region
  (records reference strings BY INDEX) + string table (NUL-terminated
  Shift-JIS, last 68,237 bytes). Rebuild = same segment count/order,
  translated strings, updated string_table_bytes. Categories tile the
  index space, so byte offsets may move freely.
- Commentary (file 02030): 20 ADX names (CRLF lines) + 8,984 lines,
  each "code＿text" (full-width underscore separator). Audio stays
  Japanese (ADX); only subtitle text translates. Phase 2.

## Milestone 1 — PIPELINE PROOF (done 2026-11-19 evening)
- LZSS ENCODER (tools/koc2_lzss_enc.py, new): greedy longest-match,
  3-byte hash table, ring simulated for overlap matches. Round-trip
  (encode -> koc2_lzss.decompress) byte-exact on: synthetic edge cases
  (empty, 1-2 bytes, random 1KB/100KB, zero runs 10KB/100KB, runs,
  ABAB, repeated text, mixed), the real file02010 (197,125 B ->
  77,713 B) + file02030 (331,155 B -> 129,273 B), and 100 sampled
  real compressed game files (60 from KC2FIRE.000 + 40 from .001,
  45.7%/47.3% ratios). Encoder is proven; note the text files are
  stored RAW so the patch doesn't need it — it's for future
  compressed-file replacement (e.g. TIM2 menu textures).
- CONTAINER REBUILD (tools/kc2_rebuild.py, new): reuses original
  stored blobs verbatim for unchanged files; re-encodes replaced
  files (raw -> 2048-pad, compressed -> LZSS + 32-pad); recomputes
  offsets. TEST 1 PASS: empty-manifest rebuild of KC2FIRE.000 is
  byte-identical to the original (sha256 0beeb52a...).
- STRING-TABLE REBUILD (tools/koc2_strings_build.py, new).
  *** CRITICAL CORRECTION found via lane W2's work (see below): the
  first version kept the record table verbatim — WRONG. Record field
  u32 @0x00 is the BYTE OFFSET of the string in the physical string
  table, so it MUST be recomputed when string lengths change. The
  fixed builder recomputes all 4,021 offsets (logical->physical map:
  skip empty physical strings 581 + 1354) and self-checks them.
  NO-OP CHECK PASS: empty translation map reproduces file02010
  byte-for-byte. TEST 2 (fixed builder) PASS: re-extracted archive
  matches the original everywhere except file02010 (= new data);
  independent offset check on the re-extracted file: 0 mismatches
  in 4,021 records; re-parsed strings show English at the right
  indices (Fujinami/Chono, Strong/Technique/...).
- PUSHED + VERIFIED LIVE 2026-11-19 evening: western-heart
  `muse/koc2`, commit 9d84de38 (Mars approved the card) — the 4 new
  tools + TEARDOWN.md (§8 table + §9 boot-verification note + new
  §11 English patch pipeline). Base verified byte-identical first
  (git blob SHA 7f23da3d… matches remote). Sync record:
  ~/workspace/koc2-english-push.muse-github-snapshot-sync.json.
- ISO PATCH (tools/koc2_iso_patch.py, new): streaming (the first
  version loaded the 4.6 GB ISO into RAM and got OOM-killed — lesson:
  never read_bytes() a PS2 ISO). Finds KC2FIRE.000's directory
  record (offset 538900, LBA 1965965, size 244,441,088), copies the
  ISO in chunks, writes the new archive at the same LBA, zero-fills
  the leftover extent, updates the both-endian data_length. TEST 3
  PASS: patched ISO differs from the original ONLY in the KC2FIRE.000
  extent + its directory record; KC2FIRE.000 extracted from the
  patched ISO with 7z is byte-identical to the rebuilt archive.
- KC2FIRE.DIR is just 4 archive filenames (CRLF) — no sizes, no
  update needed. ISO has PVD only (no Joliet) — one directory tree.
- BOOT VERIFICATION — BLOCKED, stated plainly: no PS2 BIOS anywhere
  in the workspace and no PCSX2 installed; PCSX2 requires a BIOS to
  boot anything. Headless boot would need: a BIOS dump + PCSX2
  (AppImage) + Xvfb + software rendering, on the Oracle VM or this
  box. NOT attempted — needs a decision on sourcing a BIOS. What IS
  verified: every structural layer (encoder, container, string table
  + record offsets, ISO patch). The realistic verifier is Mars's PC
  with PCSX2 (the console guide already tells him to install it).

## Lane W2 findings folded in (2026-11-19 evening)
- western-heart branch muse/koc2 advanced past Lane E: head 097b33a8.
  New commits: abac329a (romanize 363 roster names), e8395070 (crack
  file 02010 record table + survey file 01999), 097b33a8 (TIM2/MVS/MDL
  surveys). Their workdir is on disk:
  ~/workspace/bannon-verify-and-complete/lanes/w2-jp-re/work/
  (copied the key files into data/ + tools/ + docs/ here).
- FILE-02010-FORMAT.md (docs/): record table = 4021 x 32 B, one per
  LOGICAL string; field u32 @0x00 = string offset (4021/4021
  verified — independently re-verified here, 0 mismatches); @0x04 =
  person id, @0x07 = federation (8 runs: NJPW/NOAH/AJPW/ZERO-ONE/WJ/
  Pancrase/FREE+officials/ORIGINALS), @0x08 = 0xFFF wrestler vs 0
  staff, @0x1C = index within category. Logical vs physical: 4023
  physical strings, 4021 logical (empties at physical 581 + 1354
  skipped; physical 2285 IS logical 2283).
- WARNING for Milestone 2: koc2-strings.json's category slices are
  PHYSICAL-indexed while the header's category boundaries are
  LOGICAL — so category assignments in that JSON are shifted by 1
  past physical 581 and by 2 past physical 1354. Translate by
  PHYSICAL index; compute logical categories from the header + map.
- File 01999 (WrestlerData, 1,252,521 B, stored RAW flags 0x1):
  441 x 2285-byte wrestler records with embedded Shift-JIS text —
  family (+0x04, 12 B), given (+0x13), nickname (+0x28, 32 B),
  finisher (+0x49) — FIXED-WIDTH fields, translate in place
  (shorter + NUL-pad). 190 distinct wrestlers. Milestone 2 scope
  includes this file (names in matches come from here).
- Romanized roster (data/koc2-roster-romanized.json): 363 names —
  faq_full 94, faq_family 16, faq_fuzzy 21, override 46, machine 186.
  Machine readings are often wrong on given names (see
  romanize_report.txt) — review the 186 machine ones in Milestone 2.

## Milestone 2 — PLAYABILITY TRANSLATION (in progress, continuation lane)
- LANE RESTART 2026-11-19 ~19:02: the first M2 lane died on an output
  token cap, but all its work was on disk — recovered, nothing redone.
  Lesson carried forward: work in small chunks, never dump big dicts
  in replies, update this WORKLOG as you go.
- MOVE NAMES FOUND (first M2 lane): file 02008 is the move-name table
  — 3,022 entries, 85 categories. Layout cracked (see
  tools/koc2_translate_02008.py docstring): header (u32 ncat=85, u32
  nstr=3022, u32 table_bytes) + 85 x 8B category index (u16 type, u16
  count, u32 first) + 3022 x 12B records (u32 str_offset, u32 index,
  u32 0) + string table. 1,823 unique names.
- FILE 02010 TRANSLATION: DONE (first M2 lane) — 4,018/4,021 physical
  strings, 0 failed (work/translations-02010.json).
- FILE 02008 TRANSLATION: DONE (continuation lane, 2026-11-19 ~19:06)
  — 3,019/3,022 strings, 0 failed; the 3 untranslated are '－' dash
  placeholders (indices 1704, 1886, 1887), correctly skipped.
  Method: the base segmenter (WHOLE 565 + TERM 1074) plus
  tools/koc2_translate_02008_patch.py (4 rounds, ~350 added entries;
  failures 1011 -> 507 -> 472 -> 226 -> 7 -> 0). Two segmenter bugs
  fixed along the way: (1) full-width Latin normalization must be a
  FALLBACK only — normalizing first broke the base's full-width keys
  ('DDT' -> 'D D T', 58 regressions); (2) ASCII passthrough now
  groups letter/digit runs into whole words — paren-inserted English
  used to come out as spaced single letters ('N o r t o n A p p e a l',
  22 entries). Every round diff-checked: no previously successful
  translation changed except deliberate improvements (e.g. 延髄 ->
  'Medulla' instead of 'Back-of-Head').
- FAQ DEAD END: the local "Jerrold FAQ" file
  (lane-koc2/faq-koc2-jerrold.txt, 1086 B) is a Neoseeker
  security-check page, NOT the FAQ — no movelist reference on disk.
  02008 translations were done from Japanese + wrestling knowledge.
- 01999 (WrestlerData): next. 02008 rebuilder (koc2_strings_build_
  02008.py) still to write; then rebuild + patched ISO + BIOS/boot.
- FILE 01999 TRANSLATION: DONE (continuation lane, 2026-11-19 ~19:20)
  — 1,733/1,733 fields across 441 records, 0 failed, 0 overflow.
  tools/koc2_translate_01999.py + work/translations-01999.json.
  Family/given via 02010 PARTS + PARTS_ADD (50 family + 45 given
  missing parts, mostly katakana foreign names, hand-translated);
  nicknames via a 183-entry hand NICK dict (the 02010 segmenter only
  covered 13/183 — nicknames are idiomatic phrases); finishers via
  the patched 02008 move translator + 17 FIN_OVERRIDE entries.
  Field limits verified from raw bytes: family/given strictly 12 B,
  nickname/finisher strictly 32 B (gap bytes are non-zero data, no
  overflow allowed); 11 records use the full 12 B with no NUL, so
  the game reads fixed-width. Two width fixes: 獣神サンダー -> 'Jushin'
  (14-char 'Jushin Thunder' wouldn't fit); Vertical Drop Reverse
  Brainbuster -> 'Vert. Drop Reverse Brainbuster' (33 -> 30 chars).
  Seven finisher strings are TRUNCATED in the game data (32-byte
  field ran out of room); English is 1 byte/char so FIN_OVERRIDE
  restores the full name, verified against the 02008 table (e.g.
  'ノーザンライトスープレックスホー' -> 'Northern Lights Suplex
  Hold', which the raw translator had rendered as '...Suplex Ho').
  Display order: fields stay semantically correct (family=family)
  even though the game displays family-first — match screens read
  'Fujinami Tatsumi' (Japanese order) while the 02010 roster lists
  read Western order. Accepted inconsistency; swapping fields per
  wrestler would mislabel the data.
