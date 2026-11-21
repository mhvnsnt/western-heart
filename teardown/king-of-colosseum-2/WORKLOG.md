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

## Milestone 3 — HYBRID JP/EN TOGGLE + FULL ENGLISH (in progress, M3 lane, 2026-11-20)
Mars ordered 2026-11-20 ~08:38 EST: (1) a JP/EN LANGUAGE TOGGLE (hybrid
version, switchable between Japanese and English); (2) FULL English —
every remaining Japanese bit on screen (menu TIM2 textures, profile
enums, commentary 02030) + fix the Appearance truncations if cheap.
- CORRECTION — WE ARE NOT FIRST (found 2026-11-20 ~08:45, parent
  lane): an English KoC2 patch PREDATES ours — kactusken/
  King-of-Colosseum-II-English (GitHub, MIT), v0.1 2026-10-17, v0.2
  2026-11-01. Our M2 build is INDEPENDENT work (built without
  knowledge of it) but NOT the first English KoC2. Never claim
  first-ever again without a GitHub check (AGENTS.md rule).
  Per Mars's PRE-DECODED FIRST rule, M3 evaluates kactusken FIRST
  as the pre-done source. Their repo (cloned to
  work/m3/sources/kactusken/repo, 31M) is a complete open-source
  translation project: full docs (TECHNICAL/PATCHES/EDITING/
  TRANSLATION/BUILDING), Python toolchain (extract/build/pak/tim2/
  gfx/render/textpatch/codepatch/elf/mipsdis/dojo/mmtalk/records/
  teamdata/mmdata), translated text (16,997 entries) + 292 menu
  graphics. v0.2 xdelta also downloaded (work/m3/sources/kactusken/
  v0.2.zip, 6.6MB). Provenance: see work/m3/SOURCES.md.
- KEY FINDINGS from their docs (read 2026-11-20, TECHNICAL.md +
  PATCHES.md + EDITING.md + TRANSLATION.md + BUILDING.md):
  * ASCII FONT PATCH (PATCHES.md): the renderer only draws 2-byte
    Shift-JIS — their ELF patch hooks the formatter (0x10c65c) +
    glyph lookup/width (0x10cc20/0x10ccf0) with cave routines at
    0x31e2b8 (unreferenced 520B lib routine) converting printable
    ASCII to full-width codes. Text can be stored as ASCII and drawn
    with the game's own proportional font — this FIXES our
    truncation problem at the root (15-byte surname field holds 15
    ASCII chars, not 7 full-width). Verified in game 2026-10-15.
  * PACK FORMAT corrections: flags low u16 = GROUP SIZE (the loader
    reads whole groups in one read); groups start on sectors + span
    whole sectors (their pak.layout_errors checks this; a build
    that broke it crashed at boot). LZSS ring is written from
    position 1, copy-from-0 is the end marker (our encoder works
    in-game anyway — CHEST SLAP proved it — but their pak.py is the
    proven-correct implementation; prefer it going forward).
  * DISC HAS ROOM TO GROW: ~100MB free at the end (DVD-5); their
    disc.py grows KC2FIRE.000 by moving .001/.MVS forward + cutting
    LAST.DAY padding. Game finds files via sceCdSearchFile (no LBAs
    in ELF). Both layouts verified in game. THIS ENABLES THE TOGGLE
    (append EN variants as new archive entries).
  * TIM2 SOLVED: types 9/10 (4/8bpp) are SWIZZLED (GS memory
    layout); their tim2.py/gfx.py/render.py decode + re-encode with
    byte-identical round-trip (gfx.py verify). 292 menu graphics
    translated + verified in game (70 + 251 + 41 pictures).
  * PROFILE ENUMS live in entry 1441 (messages pool: weight
    classes etc.) — their translation/text/messages.txt covers it.
    Enums are message IDs in the variant block (+0xf weight class,
    +0x80 nationality, +0x81 build, +0x88-0x8a styles).
  * COMMENTARY 02030 IS A DEV FILE: entries 2029/2030/2031 are
    developer source files — "no loader call or data table refers
    to them" (from the code). 02030 is the transcript script for
    the ADX clips, NOT loaded by the game. If verified, there is NO
    commentary translation to do in-game (no subtitles exist).
  * SIX roster copies: 1999/2016 (base), 2002/2018 (Match Maker),
    2004/2019 (Survival Road) — real-wrestler blocks byte-identical.
    We only did 1999. True layout: index records + packed variant
    blocks (0x8ed), NOT our fixed 2285B records (ours works because
    blocks are contiguous; their records.py is the clean tool).
  * MORE TEXT FILES than M2 covered: 1448 (appearance cats), 1450
    (move slots), 1451 (CPU logic), 1452 (wrestler types/samples),
    1453 (voices), 1454 (music), 1455 (Dojo dialogue, 1495 recs),
    2000-2020 (teams/promotions), 2005 (edit templates), 2396-2400
    (shop), 2797-2844 + 2853-2884 + 2901 (Match Maker), 2011
    (second move list). Their translation/ covers all of it.
  * Their scope keeps Japanese BY DESIGN: title/promotion/belt
    logos, costumes, ring art, movies, audio, kana/kanji keyboards,
    staff credits (3133/3134), save title (1432), debug screens
    (02033-02040). Mars wants ALL Japanese gone from screen — the
    toggle + full-English scope may go further than theirs on
    credits/debug screens if feasible.
- M3 PLAN: (1) build their English ISO + boot-test (validate the
  pre-done source); (2) M3 full-English build on their pipeline
  (their toolchain + graphics/text where we lack it, our M2
  translations credited as independent work); (3) toggle: hybrid
  archive (JP originals at their indices + EN variants appended
  after the last group) + ELF loader-remap hook + language flag
  (byte-flip in the ISO and/or pnach; in-game options-menu toggle
  attempted if tractable); (4) verify both languages boot + play,
  screenshots; (5) report (no repo pushes — parent handles them).

- 2026-11-20 ~13:50-14:15 UTC (M3, kactusken validation + toggle design):
  * build.py --unlocks none COMPLETED in 52s (text steps all ran:
    messages 569, actions 528, matches 69, moves 3022, wrestlers 4020,
    movelist 4209, roster 13373 fields, fields 1934, dojo 602 pages,
    mmtalk 525, teamdata 526, mmdata 52/60, elf 379; code patches:
    Dojo quotes + ASCII text; KC2FIRE.000 grew 253 sectors into
    LAST.DAY). BUT the first build imported ZERO images: the image
    dirs (images-rendered/approved/handmade) are GAME ART, NOT IN GIT
    (paths.py) — the clone has only the generators (graphics.csv,
    renders.json, translation/hand/*.py scripts, fonts).
  * v0.2 xdelta (plain English) applied to a clean ISO copy -> SHA-256
    8184f07a...; my first build fe6eb279... (differ: 11,620,214 bytes,
    ALL inside KC2FIRE.000; ELF region byte-identical). Cause = the
    missing renders, not the text/code.
  * tools/render.py regenerated all 262 automatic renders (~7.7 min,
    Pillow 10.2.0 + Barlow Condensed); tools/hand.py regenerates the
    30 hand-approved images from translation/hand/*.py scripts
    (running at time of writing). Rebuild + hash-compare vs v0.2 next.
  * v0.2 .000 vs original .000 diff (via disc.py + pak.py): 454
    changed entries in 392 groups (604 entries total in those groups);
    mirror data 42,809,344 B sector-aligned; changed range 1441-3131.
    Disc has ~106 MB free -> mirror fits.
  * TOGGLE DESIGN DECIDED (loader-remap hook + byte-flip flag):
    - Pack loader is THE choke point: 0x28b178 (load; a0=pack idx,
      a1=dest, a2=entry idx, a3=flag; 40+ callers) + 0x28b0a0/0x28b0b8
      (size calcs, index in a1; external callers incl. roster loader
      0x1164d0 -> MUST also be hooked or EN entries overflow JP-sized
      buffers). 0x28aff8/0x28b0d0 have NO direct callers. Pack struct
      lookup 0x28aea0: struct = 0x408c10 + idx*36. Pack order (from
      the open routine 0x296f70 + filename strings): 0=kc2fire.mvs,
      1=kc2fire.000, 2=kc2fire.001. Hook checks a0==1.
    - Non-first group entries ALL have flags low-u16 == 1 (4,367/4,367),
      so entry-level translation inside a mirrored group is safe.
    - Mirror: EN variants of the 392 affected groups appended after
      the last group of KC2FIRE.000 (same entry order/flags, EN bytes
      for translated entries, JP bytes verbatim for the rest).
      Table = 392 x (orig_start u16, mirror_start u16) = 1,568 B.
    - CAVE FOUND + VERIFIED: 0x285464, 1,956 bytes, no external
      references (jal/j/branch/data-ptr/lui all checked from outside
      the region), clean jr-ra boundary before it. Holds hook code
      (~200 B) + flag word + 1,568 B table. Camera viewer (0x286108,
      3,784 B) also safe but LEFT ALONE (debugview feature preserved).
      Scan tools: work/m3/tools/deadcode_scan.py + cave_check.py.
      NOTE: 0x2c66fc (2,492 B) is NOT safe (branch from 0x2c66e4 in).
    - ELF strings (379, elf.txt: menu strings, title histories,
      results, messages, match settings) CANNOT be remapped by the
      pack hook (they live in the ELF). Solution: the FLIP SCRIPT
      rewrites the 379 ELF string slots in the ISO file (JP<->EN bytes
      from embedded blobs) AND flips the 1-byte pack flag together.
      Also flips the Dojo quote token tables back for JP mode.
      The ASCII text patch stays ON in both modes (JP two-byte codes
      unaffected; half-width ASCII in JP text renders full-width
      instead of being skipped - verify by screenshot vs original).
    - In-game menu option (task option a) NOT attempted this
      milestone: needs menu-code RE + save-format work (unbounded);
      the script+hook hybrid delivers the same outcome (one ISO,
      switchable language, default EN). Documented as future work.

  v0.2 REFERENCE BOOT TEST (2026-11-20 ~15:00-15:15 UTC, PCSX2 2.8.2,
  squashfs-root/AppRun -batch, DISPLAY=:99) - the pre-done source WORKS:
    - Memcard dialog in English ("No data for this game on memory card
      (PS2)... Start anyway?"). Spike logo, title "KING OF COLOSSEUM".
    - MODE SELECT fully English: EXHIBITION MATCH / SURVIVAL ROAD /
      MATCH MAKER / TITLE MATCH / SERIES MODE / EDIT / DO-JO / OPTION /
      SAVE/LOAD + help line. EXHIBITION submenu fully English (7 match
      types, o OK / x Back legends). Player select: Red Corner 1P /
      Blue Corner COM.
    - SELECT WRESTLER fully English, NO truncations: Chono, Nagata,
      Tenzan, Nakanishi, Nishimura, Nakamura, Yasuda; profile card
      "Commander in Black", "Chono Masahiro", "186cm 108kg",
      "1963.9.17", "STF" (M2 had BLACK COMMANDER / CHONO MASAHI /
      S.T.F). 3D model renders. Save state slot 1 at wrestler select:
      ~/.config/PCSX2/sstates/SLPM-65602 (0C2228C7).01.p2s (13,983,353 B).
    - Screenshots: /tmp/m3-v02-*.png (quota forced /tmp; copy keepers
      to pcsx2/shots/ when the quota allows).
  COMMENTARY 02030 CONFIRMED DEV-ONLY (static ELF scan 2026-11-20):
    zero references to entry indices 2029/2030/2031 anywhere in the
    ELF code segment (no immediate loads at all; none near any of the
    65 loader call sites). The game has no code path to load or show
    02030 - there are NO subtitles to translate. Task evaporates.
  PCSX2 INPUT RECIPE (this box, Xvfb :99, no window manager):
    - Launch from the EXTRACTED tree (AppImage FUSE mount fails):
      ./squashfs-root/AppRun -batch <iso>. Kill by AppRun PID.
    - Audio dialog (no audio device): click OK at (713,348).
    - Game window title is "キング オブ コロシアムⅡ" - find it with
      xdotool search --name 'コロシアム'. windowactivate FAILS (no WM);
      use windowfocus + plain xdotool key/keydown/keyup (XTEST).
      xdotool key --window (XSendEvent) does NOT reach the game.
    - JAPANESE BUTTONS: Circle (L) = confirm/OK, Cross (K) = back.
      Pressing Cross on a Yes/No dialog moves the cursor to No.
    - At 1-6% speed (box load 20-66 from sibling blender/ffmpeg jobs),
      single 2s holds often miss the input poll: send 2-5 repeated
      3s holds, then wait 40-50s. Turbo (Tab) is on.
    - Disk quota trips intermittently (EDQUOT, errno 122) near ~103G
      usage despite 48G free on df - retry writes; use /tmp for
      working screenshots. Freed 5.1G 2026-11-20 (deleted my rebuild
      ISO + extracted .bin copies; v0.2 reference is the EN source).
  HYBRID BUILD (2026-11-20 ~15:15 UTC):
    - tools/build_hybrid.py: copies the v0.2 reference ISO, applies
      the toggle patch to its ELF (hook sites + cave verified first),
      writes back the hybrid .000 + patched ELF via disc.write_file
      (relocate/donors/shift_into), generates toggle_data.json
      (flag ISO offset, 379 ELF slots JP/EN bytes, Dojo tokens).
    - tools/koc2_lang_toggle.py: flips a hybrid ISO en|jp|status -
      writes the flag byte + 379 slots + 2 Dojo tokens; refuses to
      touch a non-hybrid ISO (hook check).

  HYBRID BUILD COMPLETE (2026-11-20 ~15:15 UTC, tools/build_hybrid.py):
    - Output: work/m3/work/King of Colosseum II (Hybrid JP-EN).iso,
      4,593,778,688 B, SHA-256
      e0e61a503c6b9276876da75f20bb024bb68a33ce9eb05801a4629a741877019e
    - Base = v0.2 reference ISO (author's released build). Hook sites +
      cave verified against the EN ELF, then patched: cave 1,456/1,956
      bytes, FLAG at 0x285558 (default 1 = English), TABLE at 0x28555c.
    - .000 relocated LBA 1965965 -> 910413 (140,264 sectors taken from
      GOOD.BYE zero padding); ELF stays at LBA 285. Disc check:
      ISO9660 and UDF agree. Pack count 8123, layout clean.
    - toggle_data.json: flag ISO offset 2,182,488; 436 ELF slots
      (379 differ JP vs EN, 57 identical - kept JP by design, matches
      elftext.step's 379); 2 Dojo tokens.
    - FLIP ROUND-TRIP VERIFIED: status EN -> flip jp (hash a9da902c...)
      -> flip en -> SHA-256 back to e0e61a50... exactly.
  VM RESTART ~15:12 UTC: PCSX2 + Xvfb died, /tmp screenshots wiped
    (v0.2 title/mode/exhib/roster shots lost; 9 shots survive in
    pcsx2/shots/; v0.2 save state slot 1 survives). Workspace files
    intact. Xvfb restarted (:99). apt is locked by the boot-time
    os-intent replay (pid 786, reinstalling recorded packages incl.
    imagemagick/xdotool/libGL) - WAIT for it; do not kill it.
    AppRun needs libOpenGL.so.0 (wiped by the restart) - the replay
    should restore it; if not, apt-get install libgl1 imagemagick
    xdotool x11-apps after the replay finishes.
  VM DISK WARNING (parent, 2026-11-20 ~10:17 EST): Oracle VM 2.2G free
    (99% used) - PPP runner _work re-checked out 12G for a RUNNING job.
    Do NOT clean it. The 4.6G hybrid ISO CANNOT copy to the VM until
    disk frees up - report as blocked, do not delete anything.

  RESTART RECOVERY (2026-11-20 ~15:25-15:50 UTC):
    - Xvfb restarted (:99). import restored (sibling's bulk dpkg -i
      of /var/cache/apt/archives). libOpenGL.so.0 present.
    - PCSX2 exited 0 on launch: emulog shows BIOS found, hybrid ISO
      opened (DVD, 2243056 sectors, SLPM-65602, CRC E75E36C6), then
      "GS failed to open" - EGL eglGetDisplay() failed. Cause: the
      Mesa libs (libgl1-mesa-dri, libegl-mesa0, libglx-mesa0) were
      left UNPACKED (not configured) by the interrupted bulk dpkg,
      and Xvfb started before the Mesa libs landed (no GLX).
      Fix: dpkg --configure -a / apt-get install -f, then RESTART
      Xvfb so it picks up GLX, then relaunch PCSX2.
    - FALSE ALARM: BIOS looked missing from ~/.config/PCSX2/bios/
      (ls piped to head -8 cut the .bin line) - it was there all
      along (also at pcsx2/bios/scph39001.bin + ps2_bios_official.zip).

  HYBRID BOOT TEST 1 FAILED - hook bug found + fixed (2026-11-20 ~16:00 UTC):
    - Symptom: game booted (BIOS found, ISO opened, SLPM-65602,
      CRC E75E36C6) then at ~87s the EE trapped: "Unknown R5900
      SPECIAL: 000E0E0E", "EE: Unrecognized op e0e0e", "Trap
      exception at 0x00082460" - the CPU was executing garbage.
    - ROOT CAUSE (hook_load in toggle_patch.py): the stub did
      `move $a1, $a2` to feed translate the index, but $a1 is the
      loader's DEST BUFFER. translate never writes $a1, so after
      the call $a1 still held the index - the loader then wrote
      the loaded entry to address (index) instead of the dest
      buffer, corrupting low RAM (exception vectors). The size
      stubs were fine ($a1 IS the index there).
    - FIX: hook_load now saves $a1 at 4($sp) before the call and
      restores it after (`sw $a1, 4($sp)` / `lw $a1, 4($sp)`).
      Cave grows 1,456 -> 1,464 bytes; FLAG/TABLE shift +8.
      Rebuilt via build_hybrid.py (same command, re-verifies
      hook sites + cave SHA-1 against the v0.2 ELF).

  HYBRID BOOT TEST 2 (fixed hook) - EN MODE VERIFIED (2026-11-20 ~16:05-17:12 UTC):
    - New hybrid SHA-256 4519330547d1974a7f5a40cb4731885a86522129dad6d063e6803c836a082d5c,
      FLAG ISO offset 2182496. CRC E4BD98EE.
    - Memcard dialog EN ("No data for this game on memory card..."),
      Spike logo, title "KING OF COLOSSEUM II / PUSH START", MODE
      SELECT fully EN (Exhibition/Survival Road/Match Maker/Title
      Match/Series Mode/Edit/Do-Jo/Option/Save/Load), Exhibition
      submenu EN (Single/Seconds/Tag/Handicap/Triple Threat/Battle
      Royal/Elimination), SELECT WRESTLER EN (Chono/Nagata/Tenzan/
      Nakanishi/Nishimura/Nakamura/Yasuda; profile "Commander in
      Black", "Chono Masahiro", 186cm 108kg, 1963.9.17, STF),
      CONFIGURATION EN (Pro Wrestling Rules, 3 Count, 30 min, One
      Fall, CPU Level 4, 100%, Plain (Blue)), ring announcer in
      the ring, NO subtitles on screen (02030 dev-only confirmed
      in-game). Screenshots in pcsx2/shots/m3-hybrid-en-*.
    - Save states: slot 1 = MODE SELECT, slot 4 = roster
      (~/.config/PCSX2/sstates/SLPM-65602 (E4BD98EE).0{1,4}.p2s).
      NOTE: F2 cycled 1->4 on one 2s hold (key repeat) - track the
      slot number, don't assume.
    - Appearance screen MISSED (5x Circle blew past it + COM pick
      to Configuration). Re-capture from slot 4 with ONE Circle.
    - In-match HUD shot MISSED (reboot hit during match load).
    - SECOND VM RESTART ~17:12 UTC (uptime 0 min) - Xvfb/PCSX2/
      tools wiped again. The earlier "mystery deaths" were
      probably restarts too. Recovery recipe: restart Xvfb, wait
      for os-intent replay / install imagemagick xdotool x11-apps
      libgl1-mesa-dri libegl-mesa0 libglx-mesa0, RESTART Xvfb
      after Mesa lands (GLX), relaunch PCSX2, F3 loads the state.
    - Keep exec yields <= 120s; a 240s yield got interrupted.

  HYBRID BOOT TEST 3 - JP MODE VERIFIED (2026-11-20 ~17:45-18:05 UTC):
    - Flipped to JP (status JAPANESE flag=0, hash 68b4ca8ca29cfdea...),
      booted: memcard dialog fully JP (メモリーカード(PS2)に...),
      MODE SELECT help line JP, roster fully JP (蝶野/永田/天山/
      中西/西村/中邑/安田, 黒の総帥, 蝶野 正洋, S・T・F, ○決定/
      ✕戻る/△ランダム, レスラータイプを選択してください).
    - Menu labels/headers/field labels stay ENGLISH in JP mode -
      NOT a bug: kactusken's graphics.csv proves the ORIGINAL game
      shipped them in English (000_01497 "already English; mode
      select menu", 000_01503 "SELECT WRESTLER title above is
      already English", 000_01504 "NICK NAME/NAME/... already
      English", 000_01659 "already English; italic teal plates").
      The katakana mode names beside the EN labels (エキシビション
      マッチ) are the original's own atlas text (entry 1498) - JP
      mode is faithful to the 2004 original. Toggle is COMPLETE.
    - EN-mode Appearance/TYPE: costume select is ON the roster
      screen (Left/Right cycles "TYPE 1/2/..." - numeric labels,
      no names). The M2 truncations (MASAH/POW/NORM/B) do NOT
      exist in the hybrid (kactusken's TYPE N design). Tenzan
      TYPE 2 verified (red trunks in-match).
    - In-match HUD EN verified (Chono vs Tenzan, 00:04, Caller
      Yoshinari Tsuji / Color Kazuo Yamazaki, no subtitles).
    - ROUND-TRIP RE-VERIFIED on the fixed build: JP -> EN returns
      SHA-256 4519330547d1974a... exactly. ISO left in EN mode.
    - Save states (EN, CRC E4BD98EE): slot 1 MODE SELECT, slot 4
      roster, slot 5 in-match (Chono vs Tenzan).
    - THIRD VM restart ~17:12 UTC wiped tools again. Full restore
      list for PCSX2: imagemagick xdotool x11-apps libgl1-mesa-dri
      libegl-mesa0 libglx-mesa0 libopengl0 libgl1 libegl1 libglx0
      (libopengl0/libegl1/libglx0 are the easy-to-miss dispatch
      libs - AppRun fails without them). Restart Xvfb AFTER Mesa
      lands or GLX is missing and GS fails to open.
