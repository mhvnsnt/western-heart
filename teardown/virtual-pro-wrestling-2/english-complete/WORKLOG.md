# WORKLOG — VPW2 English translation COMPLETION lane

Goal: finish the VPW2 English translation — help screens + Royal Road
Succession (+ credits if feasible) — on top of the Beta 3 fan translation
(S.K. Stylez / AKIClub64). Deliverable: a patched ROM that is fully
English, served by the Universal Console as the default VPW2 entry.
Workdir: ~/workspace/vpw2-english-complete/
Push target: western-heart branch muse/vpw2-english-complete (tools +
translation tables + build script only — NEVER the ROM).

## 2026-11-19 ~19:06 — lane spawned

## Starting points (verified)
- Clean ROM: `vpw2-clean.z64`, 33,554,432 B, SHA-1
  82dd25a044689eab57ab362fe10c0da6388c217a (copied from
  lane-jp-sourcing/vpw2-rom/).
- Beta 3 ROM: `Virtual Pro Wrestling 2 - Oudou Keishou (Japan)(English
  Patch).z64`, 33,554,432 B, SHA-1
  967e5239ca44fff2271d0971d9300f27f75560ee (from archive.org item
  n64patchedwrestlingroms, zip SHA-1
  92d701e96307cea44a3a39c9ed5972df36a6315f — matches IA metadata).
- Lane D (lane-jp-sourcing) already extracted VPW2 fully: 13,090 files,
  19 AkiText files = 5,848 strings (Shift_JIS), in
  vpw2/extracted/text/*.json. File table @ 0x1310F40 (13,091 u32be,
  last = end sentinel), data base 0x152DF0, 1-based IDs. Entry bit 0 =
  LZSS flag, rest = offset relative to data base.
- akitext (vpw2-decomp tools/) COMPILES and has BOTH modes: `-e`
  extract strings, `-b` build text archive. Round-trip tool exists.

## Beta 3 vs clean diff (1 KB blocks)
- 245 changed blocks in 19 ranges (~245 KB total).
- Header 0x0-0x400 changed (ROM name).
- 15 small ranges in the CODE region (< 0x152DF0) — Beta 3 patched game
  code (purpose TBD — possibly text rendering / font handling).
- ONE big range 0x188C00-0x1BE400 (219,136 B): 107 files — ALL 19
  AkiText files (0005-000E, 0063-006A, 006C), kanji.txt (0004), 82
  AkiTextures (UI/splash/menu textures redrawn in English), 1 I4Texture
  (Buttons), 1 AkiArchive (lightning), 2 Binary (edit-mode moves).
- File table region 0x1310C00-0x1311400 changed — Beta 3 rebuilt files
  with different sizes and updated the table. My build must do the same
  (or keep files the same size).
- 0x1F44400: single changed block, purpose TBD.

## Text file map (from file-table.csv db_label)
- 0005 (437) Edit Mode strings; 0006 (110) Unlock messages?;
  0007 (139) Match/Event result phrases; 0008 (310) AkiText 03;
  0009 (166) AkiText 04; 000A (176) Options Help; 000B (114)
  Parameters Help; 000C (244) AkiText 07; 000D (399) RRS/KRS messages;
  000E (104) Credits; 0063-0067 (512/512/512/512/254) Move Names 1-5;
  0068 (212) Edit Mode Move Types; 0069 (131) Match Finish Move Names;
  006A (714) Edit Mode Costume Names; 006C (290) Default Strings
  (Characters, Stables, Arenas, Mic Appeal).

## Next
- Per-file, per-string Beta 3 vs clean comparison (parse Beta 3's own
  file table — offsets shifted — extract its 19 AkiText files, akitext
  -e, diff against the clean dumps). This maps exactly what Beta 3
  translated and what is still Japanese.

## 2026-11-19 ~19:10–19:15 — survey (corrected parser)

### AkiText format cracked (tools/akitext_py.py)
- Format: [N x u16be offsets][string data]; offsets absolute, strings
  NUL-terminated Shift_JIS/ASCII, may contain \n and @B/@D/@Y/@G/@R/@O/@h
  codes, $N button glyphs, %N name placeholders.
- Do NOT derive N from offsets[0] (akitext's rule): Beta 3's builder
  points empty strings at the file's final NUL byte, so offsets[0] can
  be EOF. Correct rule: try offsets[0]//2, validate (all non-zero
  entries in range); fall back to minimum sane offset.
- Offset 0 = unused slot; offsets inside the table (< 2N) or out of
  range are degenerate (clean 0068 has ~40 entries like 0x0101/0x0200
  in slots the game never reads — a second data structure or leftover
  bytes). Parse as None.
- Round-trip: build(parse(blob)) == blob for ALL 19 clean files except
  006C (drops 1 trailing pad NUL, no offset points at it — harmless)
  and 0068 (degenerate entries zeroed — game never reads them).
- Beta 3 files rebuild LARGER (their builder dedups identical strings;
  mine does not — still valid). 000D round-trips identical; 000E +138 B.

### TRUE remaining scope: 693 JP-containing Beta 3 strings (631 to translate)
- First survey (clean-vs-Beta3 diff) UNDERCOUNTED: Beta 3 "translated"
  000D by only stripping trailing newlines — all 82 RRS strings are
  still Japanese. True criterion = Beta 3 string itself contains JP
  (excluding U+3000 spacing, which Beta 3 uses in English text).
- Per file (JP-containing / to translate): 0005: 29/11 (18 are the kana
  input-keyboard rows 403-420 — LEAVE, they are the character picker);
  0008: 29/29 (24 help + 5 punctuation fixes: full-width （） in 6/11/14,
  ・・・・・・ leaders + → in 15/16); 0009: 21/21; 000A: 32/32; 000B:
  28/28; 000C: 42/20 (22 are "Tokyo・" city prefixes — keep Beta 3's ・);
  000D: 82/82 (ALL — bulletin notices 0-18 + fan gossip 19-81);
  000E: 86/86 (credits); 0063: 113/113; 0064: 127/127 (incl. 415-417,
  which Beta 3 blanked to "なしでＯＫ" — RESTORE from clean text);
  0065: 14/14; 0066: 28/28; 0067: 26/26; 0068: 29/7 (22 are Beta 3
  garbage strings — their builder mis-packed offset-table bytes as
  text at the degenerate indices; LEAVE, game never reads them);
  0069: 4/4; 006A: 3/3 (男前/色男/大味塊 T-Shirt); 006C: 0.
- Unique texts to translate: 476 (move names heavily duplicated).
- Content map: 000A = Options Help (32 rule/option help screens);
  000B = Edit Parameters Help (28); 0009 = Edit Mode item descriptions
  (21); 0008 = mode/menu descriptions + Controller Pak help (24);
  000D = RRS bulletin board (notices + gossip); 000C = misc UI + league
  tie-breakers + Controller Pak fragments; 000E = credits roll.
- Dumps: work/still-jp/<hexid>.txt (index + JP text, duplicates grouped).

### Beta 3 terminology (from its translated labels — match these)
- Options: Format, Time Limit, Ring out, Pin, Submission, TKO,
  Rope Break, Time count, Ring out Title Change, Bloodshed,
  Quick match (= 秒殺), Interference (= 乱入), Time delay, Rounds,
  Lose When (= 持ち点), Rope Escape, Knockdowns, Takedowns,
  Gong Save, Tag Help Time, Lumberjack, No DQ (= エニウェア),
  Lose (= ルーズ), First blood (= レフェリーストップ),
  Tag format, No tag format.
- Weapons: Chair (= パイプイス), Broken Table, Kendo Stick,
  Barbed Wire Bat, Bat, Sickle (= 鎌).
- Events: Champion Carnival, World's Strongest Tag Determination
  League, Summer Action Series, Super Power Series, New Year Giant
  Series, October Giant Series, Excite Series; Triple Crown,
  World Tag Team, All Asia Tag championships.
- "Royal Road" / "Succession" / "Fan Appreciation" appear NOWHERE in
  Beta 3 text — use "Royal Road Succession Mode" (game subtitle) and
  "Fan Appreciation Day".
- Conventions: keep @ codes, $N button codes, %N placeholders
  verbatim; %% = literal %; lines ≤ ~47 chars (Beta 3's max in
  000C/000D); \u3000 for indentation; strip trailing newlines/padding.
- Credits romanizations verified against MobyGames
  (mobygames.com/game/224436/.../credits/n64/): Shika Nakayama,
  Yen Miyairi, Koji Itoh, Ryu Nakata, Yugo Shinogi, Shinya Doinaga,
  Taiji Kawai, Yoshinobu Sato, Maki Kazuno, Masashi Suzuki,
  Mr. Geta (= ゲタさん), "Bar Pro" (= バープロ).

## Next
- Write translations/<hexid>.json (index -> English text) file by
  file: 000A, 000B, 0009, 0008, 000D, 000E, 000C, 0005, then move
  names 0063-0069 + 006A.
- Build tools/build_patched.py (Beta 3 base + translations, rebuild
  file table, LZSS-encode, verify diff vs Beta 3).
- Push tools + tables + build script to western-heart
  muse/vpw2-english-complete; deliver patched ROM to Oracle VM
  /home/ubuntu/vpw2-english-complete/.

## 2026-11-19 ~19:20–19:40 — translations written + validated (ALL DONE)

- Format: translations/<hexid>.json, keys = index strings, values =
  English text (\n line breaks, @ codes / $ codes / %N preserved).
  Validator: tools/validate_translations.py (JSON parses, index in
  range, ASCII-only except \u3000, lines ≤ 55 visible chars, @/$/%
  codes match original, differs from Beta 3 string).
- DONE, all 0 errors, 634 entries total:
  000A 32 (Options Help), 000B 28 (Parameters Help), 0009 21 (Edit
  Mode descriptions), 0008 29 (24 translations + 5 punctuation fixes
  generated programmatically: （）→(), ・→., →→->), 000D 82 (RRS
  bulletin + gossip, written in 2 parts), 000E 87 (86 JP + [25] ”Ben”
  curly-quote normalization), 000C 20, 0005 13 (11 translations + 2
  Beta 3 mistranslation fixes: [370] パワー "Wrestling"→"Power",
  [371] 技巧 "Shoot Wrestling"→"Technique").
- Move names via tools/gen_move_translations.py (JP-text → English
  maps applied to every index holding that text; 0064 restores 415–417
  matched against clean text): 0063 113, 0064 127, 0065 14, 0066 28,
  0067 26, 0068 7, 0069 4, 006A 3. Generator's decode() uses
  errors='replace' — Beta 3's 0068 garbage strings aren't valid
  Shift_JIS.
- Key move-name decisions: なしでＯＫ → "None"; やられ → "Reaction";
  延髄斬り → "Enzui-giri"; 小内刈り → "Kouchi-gari"; アキレス腱固め →
  "Achilles Lock"; エビ固め → "Shrimp Hold"; ツープラ用 → "<2P>";
  かたぐるま式 → "[Fireman's Carry]"; 無間 → "Mugen"; 男前/色男/大味塊
  T-Shirt → "Handsome"/"Ladies' Man"/"Big & Bold" T-Shirt; 0064[38]
  ジャンピングニールキック「%204式」 → "Jumping Knee Kick (%204
  Style)".
- References: GameFAQs IceMaster guide v3.0i (correct URL:
  gamefaqs.gamespot.com/n64/576850-virtual-pro-wrestling-2-oudou-keishou/faqs/6766
  — the 522331 ID redirects to a wrong game); MobyGames VPW2 credits
  for romanizations (incl. the joke credit 料理 = "I got a cute wife
  who's a great cook!" — MobyGames mistranslated it as "science").

## 2026-11-19 ~19:40 — build + verification (DONE)

### Layout constraint found
- Data region is packed right up to the file table (data ends
  0x1310F40 = FT exactly, both clean and Beta 3). The 13.5 MB after
  the table is real data (audio/etc.), NOT free space. Total data
  size CANNOT grow.
- Beta 3's method (proven safe): their 106 changed files are IDs
  0x0005–0x006E (contiguous) and their group total is EXACTLY
  preserved (219,458 B in both clean and Beta 3); file 0x006F's
  offset is identical in both ROMs. They repacked ONLY that group in
  place. No changed lui→data-region instructions in their code
  patches (no evidence of hardcoded data-address fixups).
- LZSS trailing zeros are SAFE: both asmik_decode and aki_lzss -d
  decode a zero-padded stream identically (decoder stops at the
  stream's end marker). So a shrunk file can be zero-padded back to
  its original span.
- aki_lzss usage is positional: `aki_lzss -e infile outfile` (no -o
  flag). Its -e output round-trips exactly (000D re-encodes to the
  identical 4,344 bytes).

### Builder: tools/build_patched.py (Beta 3 base, grouped in-place)
- akitext_py.build() gained dedup=True: exact + SUFFIX sharing, like
  Beta 3's builder (66 suffix-shared strings in 006A alone, e.g.
  "Tenzan" inside "Hiroyoshi Tenzan"). No-translation rebuild is
  within +284 stored bytes of Beta 3's (their builder also optimizes
  packing order slightly).
- 16 files rebuilt; group delta -1,450 bytes (English compresses
  better than Shift_JIS under LZSS). 006A (last rebuilt file, LZSS)
  absorbs the slack as 1,450 trailing zero bytes → group total
  preserved EXACTLY. Files 0x006B+ keep original bytes AND offsets.
  Only 98 file-table entries change (all within 0x0005–0x006A).
- 0068: degenerate slots rebuilt as 0 (clean structure), dropping
  Beta 3's 22 garbage strings — documented intentional cleanup.

### Patched ROM (built 2026-11-19 ~19:40)
- vpw2-english-complete.z64, 33,554,432 B, SHA-1
  303c699157e8489c7f9eae47503f2b7427113606
- tools/verify_patched.py: PASSED. All 634 translations present;
  diffs vs Beta 3 are EXACTLY the translation entries + 40 degenerate
  cleanups in 0068; untouched files (0006, 0007, 006C) byte-identical;
  file table sane (even, monotonic, LZSS flags unchanged, sentinel
  unchanged); ROM diff = 200 changed 1KB blocks in 4 ranges, all
  inside the group span + file table (Beta 3's own diff was 245
  blocks — mine is tighter).
- Remaining Japanese (intentional only): 0005 kana keyboard rows
  403–420 (the character picker) + 000C "Tokyo・" city prefixes
  188–209 (Beta 3's ・ separator kept). Everything else English.
  (Note: verify's first run flagged curly ’/“/” smart punctuation
  and \u3000 indentation as "Japanese" — false positives from a
  byte-level check; fixed by using the survey's decode-based
  criterion.)
- NOT boot-tested — parent agent verifies in the browser emulator.

## Next
- Push tools + tables + build script to western-heart
  muse/vpw2-english-complete (branch only, never main).
- Deliver patched ROM (+ .zip) to Oracle VM
  /home/ubuntu/vpw2-english-complete/.
- Report to parent agent.

## 2026-11-19 ~20:20–20:30 — pushed + delivered (DONE)

- Build made self-contained: the 40 clean-0068 degenerate indices are
  now embedded in build_patched.py / verify_patched.py (no work/
  dependency). Rebuild produces the IDENTICAL SHA-1
  (303c699157e8489c7f9eae47503f2b7427113606).
- PUSHED to western-heart branch muse/vpw2-english-complete (from
  muse/jp-sourcing @ 9b58da0b, Mars approved both cards):
  commit adfeae4cc2f5f61fc3af34701f98650dc5750ad1, 28 files under
  teardown/virtual-pro-wrestling-2/english-complete/ (README,
  WORKLOG, 10 tools incl. aki_lzss.c + akitext.c, 16 translation
  tables). Via github push-files (snapshot-push procedure); sync
  record at ~/workspace/vpw2-english-complete-push.muse-github-snapshot-sync.json.
  Branch head verified by re-reading list_commits.
- DELIVERED to Oracle VM /home/ubuntu/vpw2-english-complete/:
  vpw2-english-complete.z64 (33,554,432 B, SHA-1
  303c699157e8489c7f9eae47503f2b7427113606) + .zip (25,954,991 B,
  SHA-1 3b90d3e03649e9159326390bcb804dcf2fcdd6dd) — SHA-1s verified
  on the server after rsync. Host confirmed bannon-oracle-vm.
- LANE COMPLETE. Boot-testing in the browser emulator is the parent
  agent's step — not done here, not claimed.
