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
- TRANSLATIONS PUSHED (continuation lane, 2026-11-19 ~19:25):
  western-heart muse/koc2 commit e121077d (Mars approved) — the 3
  translators + 02008 patch + 01999 surveyor + all 3 translation
  JSONs + moves-02008.json + roster/survey data + WORKLOG.
- BUILDERS DONE (continuation lane, 2026-11-19 ~19:30):
  tools/koc2_strings_build_02008.py (mirrors the 02010 builder:
  header 0x10 + 85x8B cat index + 3022x12B records + string table;
  only the u32 @0x00 offset is recomputed, the other two record
  fields are metadata copied verbatim — the translator docstring's
  'index / 0' guess was wrong) and
  tools/koc2_file01999_build.py (in-place fixed-width writes, only
  field bytes touched, NUL-pad; verifies the Japanese input matches
  before writing and re-parses after). Both proven: no-op builds
  are BYTE-IDENTICAL to the originals. Built files in
  work/built/: file02010-en.bin (202,850 B, 4,018 changed),
  file02008-en.bin (90,955 B, 3,019 changed),
  file01999-en.bin (1,252,521 B, 1,733 fields).
  Gotcha found while building: 5 em dashes (U+2014) in 02010
  WHOLE entries can't encode as Shift-JIS — replaced with ASCII
  ' - ' in koc2_translate_02010.py at the source and regenerated
  the JSON (still 4,018/4,021, 0 failed). 02008 + 01999 are pure
  ASCII. Rule: translations must stay ASCII-only.
- PATCHED ISO BUILT + VERIFIED (continuation lane, 2026-11-19 ~19:45):
  work/built/King of Colosseum II (English).iso (4,593,778,688 B,
  same size as the original). Rebuilt KC2FIRE.000 via
  kc2_rebuild.py with manifest work/rebuild-manifest.json, then
  koc2_iso_patch.py (streaming). SIZE TRAP: the first rebuild was
  +2,048 B (02010 stored +6,144, 02008 stored -4,096) and the ISO
  is fully packed — KC2FIRE.001 starts immediately after
  KC2FIRE.000's extent, zero slack — so the archive MUST fit the
  original size. Fixed by trimming 7 long 02010 announcement
  sentences in the translator source (171 B total across repeats);
  rebuilt archive is now EXACTLY 244,441,088 B (delta +0).
  Verification: prefix hash identical, suffix hash identical
  (incl. the 4096-B tail), embedded archive SHA-256 matches the
  built KC2FIRE-en.000 (fd888ba7...), all diffs inside the extent
  only. (One false alarm during verification: an arithmetic slip
  put the extent start 245,760 B too far — the 'outside' diff was
  the container's own entry table shifting. Always recompute
  1965965*2048 = 4026296320.)
- BUILDERS PUSHED (continuation lane, 2026-11-19 ~19:50):
  western-heart muse/koc2 commit 2b8dfd90 (Mars approved) — the two
  builders + the fixed 02010 translator/JSON + rebuild manifest.
- BIOS + PCSX2 SETUP (continuation lane, 2026-11-19 ~19:55):
  BIOS scph39001.bin (USA) sourced from archive.org item
  ps2_bios_official (zip MD5 00d88b02bc3aada70498ec421092c04b,
  matches archive.org; BIOS MD5 d5ce2c7d119f563ce04bc04dbc3a323e,
  SHA-1 f9a5d629a036b99128f7cb530c6e3ca016e9c8b7, 4,194,304 B,
  ROMVER marker present). PCSX2 v2.8.2 AppImage from GitHub
  releases (60,119,544 B), extracted with --appimage-extract.
  BOOT TEST RUNS ON THIS BOX, not the Oracle VM: the VM disk is
  99% full (3.6 GB free) and the 4.6 GB patched ISO won't fit
  there. The patched ISO + BIOS live in
  ~/workspace/koc2-english/pcsx2/ (BIOS) and work/built/ (ISO)
  on this box; moving them to /home/ubuntu/koc2-english/ on the
  VM waits on VM disk space being freed.
- BOOT TEST RUN 2 (continuation lane, 2026-11-20 ~04:45-05:00 EST):
  Runtime restart wiped /tmp screenshots + apt packages; reinstalled
  (imagemagick x11-apps xdotool libgl1 libegl1 libglvnd0 libglu1-mesa
  libxcb-xinerama0 libxcb-cursor0 libpulse0 libasound2t64 — apt update
  took 5min11s via the slow proxy mirror). Xvfb :99 restarted.
  Patched ISO booted clean: memcard dialog -> Spike logo -> opening
  movie -> title screen -> MODE SELECT -> EXHIBITION MATCH submenu
  (no Sony-logo reset this run; the run-1 reset was CPU starvation,
  not the patch) -> Single Match -> 1P vs COM -> SELECT WRESTLER.
  Save states: slot 1 = mode select, slot 2 = wrestler select
  (~/.config/PCSX2/sstates/SLPM-65602 (9F4A4C47).0[12].p2s).
  Screenshots in pcsx2/shots/boot*.png (NOT /tmp).
- BLANK NAMES — FONT FINDING (2026-11-20 ~05:00 EST, the big one):
  On SELECT WRESTLER the patched ISO shows the wrestler model, stats
  (186cm 108kg), birthday — but NAME, NICK NAME, SPECIAL MOVES and
  the whole roster list are BLANK. Moving the cursor changes the
  wrestler (stats update) but text stays blank — not a loading issue.
  CONTROL (original ISO, same path, shots/control*.png): names render
  fine in Japanese — roster 蝶野/永田/天山/中西/西村/中邑/安田,
  NAME 蝶野 正洋, NICK NAME 黒の総帥, SPECIAL MOVES Ｓ・Ｔ・Ｆ.
  DIAGNOSIS: the game's font is a JIS X 0208 FULL-WIDTH font — it
  renders full-width Latin (Ｓ・Ｔ・Ｆ, ＭドラゴンＶｅｒ, ０２Ｖｅｒ;
  1,290 of 4,021 original 02010 strings use full-width alphanumerics)
  but NOT half-width ASCII (only 2 real half-width chars in the whole
  original 02010 table: 'D' in アマレスDシルバー, '2' in 健介スパッツ2).
  Our half-width ASCII translations render as blanks. 01999 proves it
  independently: same fixed format, only the characters changed, and
  the text went blank — so it is the CHARACTERS, not our rebuild.
  Chono's original finisher bytes confirm full-width: 82 72 81 45 82
  73 81 45 82 65 = Ｓ・Ｔ・Ｆ (NOT half-width as first guessed from
  pixels — always verify from DATA, not screenshots).
  FIX (in progress): convert ALL translations to FULL-WIDTH, ALL
  UPPERCASE (original data proves all 26 full-width capitals + all 10
  digits; only 15/26 lowercase letters appear, so lowercase is NOT
  safe). Proven punctuation: \u3000 ！ ＆ （ ） ＋ － ． ＝ ～ ・
  (・ from Ｓ・Ｔ・Ｆ). Unproven punctuation is dropped/mapped:
  apostrophe dropped, comma/colon/slash -> space, ? -> ！, quotes
  dropped; initials S.T.F. -> Ｓ・Ｔ・Ｆ. Full-width doubles byte
  length, so 02010/02008 must be stored LZSS-COMPRESSED in the
  archive (4,167 of 7,519 original entries are compressed — the game
  loads compressed files fine; kc2_rebuild.py already supports
  "compress": true, flags bit 16). 01999 fixed-width fields halve in
  capacity (family/given 6 chars, nickname/finisher 16) — needs an
  abbreviation pass (165 family + 182 given + 146 nickname + 201
  finisher fields over-limit). The ISO patcher already handles a
  SMALLER archive (zero-fills the leftover extent, updates the dir
  record size), so compressed files fitting under the original total
  is enough. FOLLOW-UP (not this lane): a real font patch adding
  half-width Latin glyphs would restore full-length names; needs
  font-format RE (ELF symbols pgSysFontD/L, pgDojoFontD/L,
  pgESBFontD/L, pgFontData).

- FULL-WIDTH FIX DONE (2026-11-20 ~05:30 EST):
  tools/koc2_fullwidth.py (to_fullwidth: uppercase, initials -> ・,
  ASCII -> full-width, space -> U+3000; validate against the proven
  charset) + tools/koc2_abbrev_01999.py (NAME_SPECIAL 9, NICK 67, FIN
  63 rewordings; family/given truncate to 6 chars; 694 over-limit
  fields covered, list in work/overlimit-01999.txt). cp932 gotcha:
  Python shift_jis cannot encode U+FF0D (－) — all three builders now
  encode cp932. Builders apply conversion at build time; the JSONs
  stay readable ASCII.
  Full-width builds: 02010 271,910 B, 02008 141,846 B, 01999
  1,252,521 B (1,713 fields written). LZSS: 02010 -> 85,542 B,
  02008 -> 42,224 B. Archive KC2FIRE-fw.000 244,273,984 B (delta
  -167,104), manifest work/rebuild-manifest-fw.json. ISO re-patched
  (streaming); archive SHA-256
  61719b2526328744b0a91ec9c78256da20afdf2ffba373f441b865fedf506724.
  Verified: prefix differs in exactly the 6 dir-record size bytes,
  suffix identical, embedded archive hash matches, zero-fill clean.
- BOOT RUN 3 — ENGLISH PROVEN (2026-11-20 ~10:00 UTC, shots/fw*.png):
  SELECT WRESTLER: roster CHONO/NAGATA/TENZAN/NAKANI/NISHIM/NAKAMU/
  YASUDA, NICK NAME BLACK COMMANDER, NAME CHONO MASAHI, SPECIAL
  MOVES S・T・F. (fw8, fw9). EDIT -> MOVES -> Strikes: CHEST SLAP
  renders (02008 compressed proven in-game, fw18). PROFILE: CHONO
  MASAHI / BLACK COMMANDER (fw21). Profile enums (ヘビー級/日本/アメ
  リカン/テクニシャン) still Japanese — NOT in 02010 (verified by
  search); they live in another file (later phase).
- APPEARANCE SCREEN SAGA (2026-11-20 ~10:30-12:00 UTC) — the FW ISO
  hung on EDIT -> Wrestler Make -> APPEARANCE (blank value column, no
  model, input dead, TLB misses in emulog, shots fw25-fw28). Control
  (original ISO, same path, c2-7): screen works fully (values 蝶野
  正洋/パワー/ノーマル(中)/M/ノーマル/なし/蝶野ベルトボディ2/裸/裸/
  蝶野リスト2 + model). Our patch broke it. Bisection:
  Test A (02010 ORIGINAL + 01999/02008 fw): hung at NOW LOADING
  (200s+, clean emulog — no TLB misses, game waiting, not faulting).
  Entry-table verification: the rebuilt archive is PERFECT (no chain
  breaks, only 2008/2010 sizes differ, shifts exactly as designed) —
  so the game must address some files by ABSOLUTE POSITION, not via
  the entry table; shifting files breaks those loads.
  Test B (zero-shift: pad_to_original on all three, NEW kc2_rebuild
  option; archive delta +0, zero shifts): Appearance LOADS, model
  renders, screen responsive — but the value column is BLANK
  (tb5-tb7). Face list opens and shows promotion names (Japanese +
  half-width ZERO-ONE/WJ/FREE), proving the screen reads lists fine.
  Font theory KILLED by data: costume categories contain 100s of
  original full-width strings (cat 6: 111, cat 9/10: 64 each, cat 11:
  175), so the Appearance font HAS full-width Latin.
  Test C (02010 = ORIGINAL content, COMPRESSED, zero-shift): values
  show GARBAGE single kanji (体型 詰, 特殊衣装 煒, rest blank, tc4).
  CONCLUSION: the 02010 loader reads RAW — it does NOT decompress.
  The 02008 loader DOES (CHEST SLAP proved it). Different loaders
  per file. 02010 MUST be stored raw.
  Test D (02010 raw + 01999 compressed to fund the +73,728 B growth,
  net delta +0, 11 files shifted): hangs entering Default Wrestler
  Edit (menu draws, input dies). Either the 01999 loader is ALSO
  raw-only, or shifting files 2000-2010 breaks the edit load — both
  branches lead to the same fix (no room for 02010-raw except by
  shortening it), so no further bisection was run.
  FIX: shorten 02010 to fit raw in its original slot (198,656 B).
  tools/koc2_abbrev_02010.py — two-pass fit: pass 1 caps each string
  at its ORIGINAL byte length (word-boundary truncation); pass 2
  restores word-by-word by category priority (costume > names >
  styles > nicknames > music > entrance > staff/titles > narration),
  30-char display cap, budget 69,568 B. Tape variants rewritten to
  short codes (H/F/B/HF/HB) so 6 variants of one part stay distinct.
  Result: table 69,429 B, file 198,317 B (fits 198,656 slot).
  koc2_strings_build.py now applies shorten_all() at build time.
  Test F (01999 raw + 02008 compressed/padded + 02010 raw/padded,
  ALL zero-shift, archive delta +0, SHA-256
  a0ade9d4b496dc238a271c8dd3ea207c695c1cc1bf120ddf3927cea90129e12e):
  SHIPPING. Roster English (tf6), Appearance values ENGLISH (tf7):
  MASAH / POW / NORMAL / M / NORM / NO / CHONO BELT BODY 2 / B / B /
  CHONO WRISTBAND 2 + model, screen responsive. Known cosmetic cost
  of the raw-slot constraint: short-original strings truncate hard
  (face 'MASAH' = Masahiro cut to 5 chars, stance 'POW', costume
  'NORM', elbows 'B' = Bare cut to 1 char). Costume part names
  restored in full. Rebalancing restore priority (names before
  costume) is a possible follow-up polish, not a blocker.
- SHIPPING ISO (2026-11-20 ~12:11 UTC): work/built/King of Colosseum
  II (English).iso (Test F promoted over the broken FW v1),
  4,593,778,688 B, SHA-256
  e3febfb18878c1c0256e90e4e1bcadee66bfd6b0650739e924a4f5f4c2c398fc.
  Spot-checked in the raw archive region: CHONO BELT BODY 2, CHONO
  WRISTBAND 2, NORMAL, CHONO, S・T・F all present as full-width cp932.
- VM COPY (2026-11-20): first rsync (FW ISO) STALLED at
  1,071,972,352 B — dead socket, no data for ~55 min, process alive
  but idle; killed. Restarted for the Test F ISO with a retry loop
  (6 attempts, --timeout=180, --partial). The runtime restart wiped
  ~/.ssh/known_hosts, so the first attempts failed with "Host key
  verification failed" — re-added with StrictHostKeyChecking=
  accept-new after verifying hostname bannon-oracle-vm. Transfer in
  progress at time of writing; verify size + SHA-256 on the VM after
  it completes.
  COMPLETED 2026-11-20 12:29 UTC: ISO 4,593,778,688 B + BIOS zip +
  scph39001.bin/.NVM/.MEC all on the VM at /home/ubuntu/koc2-english/.
  rsync sent only 277,577,018 B (delta matched the 1.07 GB partial
  prefix, speedup 16.58x). VERIFIED on the VM: ISO SHA-256
  e3febfb18878c1c0256e90e4e1bcadee66bfd6b0650739e924a4f5f4c2c398fc
  (matches local), BIOS MD5 d5ce2c7d119f563ce04bc04dbc3a323e, zip MD5
  00d88b02bc3aada70498ec421092c04b. 15 GB free left on the VM.
- PUSH PENDING (2026-11-20 ~12:45 UTC): the final M2 push (15 paths:
  fullwidth/abbrev tools, modified builders + kc2_rebuild, shipping +
  test manifests, overlimit list, WORKLOG) is STAGED in
  ~/workspace/koc2-english-push with manifest
  ~/workspace/koc2-english-push.paths, but the approval card TIMED
  OUT (30 min, approval_expired) — the push was NOT performed. Re-run
  the push-files command when Mars is available to approve it. Branch
  head is still 2b8dfd90.
- RUNTIME RESTARTS (2026-11-20): two (first ~11:34 UTC, during the
  Test D boot). /tmp wiped, apt packages wiped, Xvfb + PCSX2 killed;
  all ~/workspace + ~/.config state survived. Repair: restart Xvfb
  :99, apt reinstall. LESSON: the cogentco mirror in
  /etc/apt/sources.list.d/ubuntu.sources is the slow one (update took
  314s with it, 40s with azure only) — removed it from the URIs line;
  also the pre-restart apt-get update (PID 794) was stuck and had to
  be killed. Xvfb binary survives restarts (base image); imagemagick/
  xdotool/x11-apps/libs do not.
- WORKING RULES LEARNED (this lane): pkill/pgrep patterns MUST use
  the bracket trick ([r]sync) AND the command must not contain the
  literal match text anywhere else (an unbracketed pgrep later in the
  same command line self-matches and SIGTERMs your own shell). Kill
  PCSX2 by the AppRun PID (pgrep -f 'AppRu[n] -batch'), never by the
  wrapper PID. Never load a save state made with one ISO under a
  different ISO.
