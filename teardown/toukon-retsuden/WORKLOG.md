# WORKLOG — Toukon Retsuden (TR1) English version, built ourselves

Lane: build a complete patched English Toukon Retsuden (PS1, Yuke's, 1995,
Japan-only) — extract text, translate, build patched disc image, QA by
booting. The game has NO English patch anywhere; WE make the English version.
Workdir: ~/workspace/toukon-english/. Game files live on the Oracle VM under
/home/ubuntu/toukon-english/ — NEVER in a repo. Tools + translation tables +
build script go to western-heart, branch muse/toukon-english.

## Game facts
- Full title: Shin Nihon Pro Wrestling — Toukon Retsuden (新日本プロレスリング 闘魂烈伝)
- Publisher Tomy, developer Yuke's. Released 1995-09-29 (Japan). PS1, NTSC-J.
- Game ID: SLPS-00084. Barcode 4904810778110. 12 NJPW wrestlers. 2 players.
- First pro wrestling game for the PlayStation.
- US version: Power Move Pro Wrestling (SLUS-00408, Activision, Nov 1996) —
  SAME engine, fictional wrestlers instead of the NJPW roster. Its English
  menu text is the official English localization of the same game: the
  primary translation reference, and the US executable is the comparison
  point for finding the text tables + font in the Japanese build.
- TR2 (SLPS-00637, Dec 1996) has an active WIP translation thread on
  Romhack Plaza — NOT this lane's scope (TR1 only). TR3 (SLPS-01366).

## Sourcing (2026-11-19 ~19:10 EST)
- TR1 (Japan): archive.org item 2024-sony-playstation-jap-hearto-1g1r-collection
  (Hearto's 2024 Redump clean set, JAP 1G1R), file
  "Shin Nihon Pro Wrestling - Toukon Retsuden (Japan).zip", 456,447,924 B,
  SHA-1 a63d2bf861cb5b3f60fc54df7e50a116b8ee8260.
  (Myrient is DEAD — farewell page; R-Cade PSX packs are US-set only.)
- Power Move Pro Wrestling (USA): archive.org item psx_pmpwrest, file
  playstationdisc.chd, 150,380,461 B, SHA-1 bb9639d052365a9e31e06afcb07e2f176032107c.
- Both downloads VERIFIED 2026-11-20 00:35 UTC (exec proc_f13a8079d24b):
  TR1 zip 456,447,924 B SHA-1 a63d2bf8…8260 ✓; US CHD 150,380,461 B
  SHA-1 bb9639d0…107c ✓ (both match archive.org metadata exactly).
- TR1 zip uses method 93 (Zstandard) — Python zipfile + 7-Zip 23.01 can't
  read it. Fixed with tools/zstd_unzip.py (pip --user zstandard) — all 7
  tracks + .cue extracted, sizes match. Track 1 = data (MODE2/2352),
  tracks 2–7 = CD audio.
- US CHD extracted locally with chdman 0.264 (mame-tools): single
  pmpw-usa.bin 340,306,176 B + .cue, 7 tracks.
- VM REPLACED 2026-11-20 ~01:35 UTC (uptime reset): apt-installed tools
  (mednafen, 7z, chdman, imagemagick, xdotool) are GONE — reinstall as
  needed. ~/.local pip packages (zstandard, pillow) + all workspace files
  survived. ~/.ssh/known_hosts wiped — use StrictHostKeyChecking=accept-new
  on next Oracle SSH.

## Reference material (saved)
- WBaker's GameFAQs FAQ v1.1 (docs/faq-wbaker.txt, 50,014 chars, 1,748
  lines): main menu (4 items), game menu (10 items), game options (7
  items), full roster (12 + 4 hidden: Great Muta, Power Warrior, Kero-Chan
  ring announcer, Tiger Hattori referee), per-wrestler move lists with
  English move names. Source: GameFAQs faqs/4670, via the cheatcodes.com
  mirror (GameFAQs blocks curl).
- Roster: Tatsumi Fujinami, Riki Chosyu, Keiji Mutoh, Masahiro Chono,
  Shinya Hashimoto, Hiroshi Hase, Kensuke Sasaki, Shiro Koshinaka,
  Jyushin "Thunder" Lyger, Hiroyoshi Tenzan, Kohji Kanemoto, Scott Norton.

## Tools (tools/)
- psx_iso.py — pure-Python PS1 BIN/CUE reader: list + extract ISO9660
  files (handles raw 2352-byte Mode 2 Form 1 sectors). Written because the
  sandbox has no 7z/bchunk/isoinfo and apt is locked by another lane's
  Blender install.
- sjis_strings.py — scan a file for Shift-JIS text runs (+ ASCII).
- zstd_unzip.py — extract ZIPs with method-93 (Zstandard) entries via the
  `zstandard` pip package (zipfile + 7-Zip 23.01 can't).
- dpac.py — parse + extract Yuke's DPAC archives (list/json/extract/
  extract-all). Format: header 0x800 (magic DPAC, ver 0x100, count,
  table size, data size); 32-byte entries (16-byte SJIS name, size,
  start sector, sector count, 0); data at sector*0x800.
- bpe.py — decompress Yuke's "BPE " sections (GROOVE-style multi-block:
  dictionary, then 2-byte LITTLE-ENDIAN block length, then data; blocks
  repeat to end of input; output length checked vs header). Header:
  "BPE ", ver 0x100, compressed size, decompressed size. All 19 JP
  GAME_MES + 22 JP COMMON + 7 US GAME_MES + 18 US COMMON sections
  decompress cleanly, all to TIMs. (psx-spx documents the dict scheme;
  the doc's "dict2[i]=a" is a typo — it's dict2[i]=b. Yuke's length is
  LE, not BE as in GROOVE.)
- tim2png.py — render PS1 TIMs (4/8/15/24bpp + CLUT) to PNG.

## SURVEY findings (2026-11-20 ~00:40–01:35 UTC)
### Disc layout (TR1, Track 1)
- SLPS_000.84 (417,792 B, PS-X EXE, .text @ 0x80010000), SYSTEM.CNF
  (BOOT = cdrom:\SLPS_000.84;1), TOK/DTPAC.PAC (2,955,264 B),
  TOK/DMY. (8,256 B TIM), TOK/XA0–XA8.XA (audio), OPEN.DAT (83.9 MB
  opening movie), END.DAT (24.8 MB ending movie), BGM1–4.DAT.
- US disc is near-identical: SLUS_004.08 (same 417,792 B), TOK/DTPAC.PAC
  (2,621,440 B), same XA layout, OPEN.DA/END.DA/BGM*.DA + DUMMY.WAV.

### DTPAC.PAC (JP: 145 entries; US: 106)
- 31 TIMs (arena/body textures + TIM_文字 font + TIM_TITLE + TIM_START +
  TIM_STAFF 1–4 + TIM_END + TIM_TIMER), 15 YMD models, 17 PAC_* nested
  WRES containers, SE00–18 (sfx), REP00–15 / OP00–11 / END00–15 (small
  binary script tables, no text).
- WRES container: magic "WRES", ver 0x100, count 0x20 (32), total size;
  32 records × 0x40 at 0x10 (PAC_WRES records = wrestler slots:
  FUJINAMI, TYOUSYUU, MUTOU, CHONO, HASIMOTO, HASE, KENSUKE, KOSINAKA,
  LYGER, TENZAN, KENEMOTO, NORTON, MUTA, POWER, BKERO, POWER, [empty],
  [empty], KERO, TIGER + move-index bytes); data area from 0x810.
- PAC_ACT is "ACTP" magic with animation names (OKIA8, OKIUT, AO_DOWN…).

### Text: where it lives
- EXE (JP): ONLY the 16 wrestler names as SJIS (0xD14–0xE34, 16-byte
  fields, full-width-space padded) + title 闘魂烈伝 (0xE38) + subtitle
  闘魂烈伝 戦いの軌跡 (0xF54). NO menu strings anywhere in the EXE.
- EXE (US): names as FULL-WIDTH Latin SJIS (Ｄａ’Ｊｕｄｇｅ, Ｄａｎｎｙ…),
  title ＰＰＷ, subtitle ＰＰＷ Ｂｏｕｔ Ｓａｖｅ. So the engine renders
  full-width Latin — replacing JP names with full-width Latin SJIS is
  the PROVEN approach (same as Activision did).
- FONT (TIM_文字, 256×48 4bpp): full ASCII set already — digits, A–Z,
  a–z, punctuation, arrows, PS buttons (○×△□). NO font work needed for
  Latin. (How kanji renders in-game is still open — names appear via
  the pre-rendered name sheet; see below.)
- MENUS: NOT FOUND as text. Byte-searched the whole disc for 会場,
  戦いの軌跡, 難易度, はい, いいえ, 試練, 再開 as SJIS — ZERO hits
  (except the EXE subtitle). Menus are NOT SJIS strings anywhere. They
  must be font-rendered from glyph-index tables or pre-rendered graphics
  not yet located. Next step: BOOT the game and look at the menus.
- PAC_GAME_MES (JP, 19 BPE→TIM): in-match message banners + name sheet:
  bpe00 16×16 color tile (skip); bpe01 ALL 16 NAMES as one 128×256
  graphic (needs English redraw); bpe02 "VS" (already EN); bpe03 勝者
  WINNER; bpe04 時間切れ引き分け TIME-UP DRAW; bpe05 ギブアップ GIVE UP;
  bpe06 レフェリーストップ REFEREE STOP; bpe07 リングアウト RING OUT;
  bpe08 両者リングアウト DOUBLE RING OUT; bpe09 時間無制限 NO TIME LIMIT;
  bpe10 反則勝ち WIN BY DQ; bpe11 digits 1–12 (skip); bpe12 王座奪取
  TITLE WON; bpe13 王座防衛 TITLE DEFENDED; bpe14 優勝 CHAMPION;
  bpe15 決勝戦 FINAL MATCH; bpe16 本部席裁定 OFFICIAL DECISION;
  bpe17/18 big digits 0–9 (skip).
- US PAC_BIG_MES (12 raw TIMs) = official English banners, SAME sizes
  as the JP ones: "and still champion", "and new champion", "Time's up !",
  "Opponent gives up !", "Disqualification !" (×2), "Final Match !",
  "Double Ring Out !", "Referee stops match!", "by split decision",
  "Winner", "The Winner". US GAME_MES has "NO LIMIT" (704 B = JP bpe09)
  + the PMPW name sheet (same 128×256 layout, block caps).
  Mapping is 1:1 EXCEPT single "Ring Out" — the US set has NO single
  ring-out banner (only Double). Will need to create "Ring Out !" from
  harvested US-banner glyphs (all letters present across banners).
- US name sheet font: block caps, ~10px/char, 16 rows. JP names in
  English must fit 128px width — long ones (JYUSHIN THUNDER LYGER,
  21 chars) need a narrower rendering.
- PAC_COMMON (JP 22 BPE→TIM, US 18): ring/costume textures, TOMY +
  Yuke's logos, "Push Start Button", "© NJPW © 1995 TOMY", timer digit
  strip, face textures, a Japanese event poster (bpe15 JP = bpe12 US —
  the US version KEPT it in Japanese; leave as-is, low priority).
- Title screen (TIM_TITLE): 闘魂烈伝 kanji logo + "TOUKON RETSUDEN"
  already in English + NJPW logo. KEEP as-is (it's the game's logo).
  TIM_START "Push Start Button" already English. TIM_END = 完 kanji
  ("The End") — check US TIM_END for its equivalent.
  TIM_STAFF 1–4: Japanese staff-roll credits; US has same-size STAFF
  TIMs — check what Activision did (likely English credits).

### Emulator / QA setup
- Mednafen 1.29 works: TR1 boots to the Sony BIOS logo (verified
  2026-11-20 01:33 UTC, screenshot work/boot2.png). BIOS: scph1000.bin
  (JP, MD5 239665b1…) + scph1001.bin (MD5 924e392e…) from archive.org
  item bios-for-retroarch, in ~/.mednafen/firmware/; mednafen.cfg needs
  `psx.bios_jp scph1000.bin` (else it wants scph5500.bin). Xvfb :99 +
  `import -window root` screenshots + xdotool keys.
- VM replacement 2026-11-20 ~01:35 UTC killed the running session —
  reinstall mednafen/imagemagick/xdotool/mame-tools/p7zip-full, then
  re-boot and screenshot the menus.
- UPDATE 2026-11-20 ~02:05 UTC: the os-intent replay IS restoring them
  (ledger includes mednafen, imagemagick, xdotool, mame-tools,
  7zip/p7zip-full); 7z already back, replay still working through the
  ledger (on mesa-vulkan-drivers at 02:04). Don't fight the apt lock —
  check periodically.

### WRES section table — DECODED (2026-11-20 ~01:50 UTC)
- Data area layout (PAC_GAME_MES, PAC_BIG_MES, US GAME_MES — same):
  0x810-0x880 zeros; 0x880 u32 0; 0x884 u32 total data size (from 0xC80
  to EOF); 0x888 table of (u16 offset/4, u16 size/4) pairs relative to
  0xC80, one per item at a FIXED slot (32 slots max, gaps = zeros for
  unused item IDs); 0xC80 data items start.
- JP GAME_MES slots: bpe00-02 @ slots 0-2, bpe03-16 @ slots 10-23,
  bpe17-18 @ slots 30-31. Verified every entry against the real BPE
  section offsets/sizes. US GAME_MES slot 0 = an UNCOMPRESSED TIM
  (the color tile, 532 B) followed by 7 BPE sections.
- Rebuild rule: keep each item in its JP slot, update (offset/4,
  size/4) + the 0x884 total. Sections pack contiguously from 0xC80.

### BPE COMPRESSOR — DONE + PROVEN (2026-11-20 ~02:05 UTC)
- tools/bpe_compress.py: Gage BPE encoder, GROOVE multi-block sections.
  Roundtrip vs bpe.py decoder: 78/78 OK (JP GAME_MES 19/19, JP COMMON
  22/22, US GAME_MES 7/7, US COMMON 18/18, US BIG_MES 12/12).
  Competitive with the original encoder (name sheet 2530 B vs orig
  2703 B; US banners compress to 8-17%).
- Three real bugs found + fixed along the way:
  1. Reusing a dead pair code creates decoder cycles (infinite
     expansion / OOM) — never reuse a code in `pairs`.
  2. Redefining a byte that is a COMPONENT of an existing pair
     rewrites that pair's expansion (decoder uses final dict) —
     track `referenced` components, never use them as codes.
  3. emit_dict: a literal run of exactly 128/256 left `remaining==0`
     and emitted 0x7F (a 128-entry group byte) — must emit a 1-entry
     group (0x00) instead.
- Constraints honored: pair code c needs a != c; nesting depth cap 10
  (matches the original's max); block input chunks <= 8192 B (orig
  max 8500); new block when no code byte remains.
- Speed: C-speed Counter(zip) counting + bytearray.replace — full
  19-section GAME_MES roundtrip in ~5 s (was minutes with naive loops).

### Build size estimate (2026-11-20 ~02:05 UTC)
- New PAC_GAME_MES data area ≈ 11.3 KB vs original 20.6 KB (US
  banners compress far better than JP ones). Rebuilt DTPAC.PAC ≈
  2,946 KB < original 2,955,264 B → IN-PLACE ISO PATCH feasible:
  rewrite DTPAC.PAC in its ISO extent, pad tail with zeros to the
  original size, keep the ISO dir record (LBA + size) UNCHANGED.
  DPAC table updated for entries shifting after PAC_GAME_MES.

### Translation built (2026-11-20 ~02:10–02:25 UTC)
- NAME SHEET (tools/name_sheet.py): harvested the 25 block-caps
  glyphs from the US sheet (segmentation by blank columns + targeted
  splits for touching glyphs); built F from E (bottom bar removed)
  and a hyphen bar; rendered all 16 NJPW FULL names condensed 2:1
  horizontally (OR-sampled), variable width + 1px spacing, centered.
  Longest (JYUSHIN THUNDER LYGER) 115px, fits. Verified visually —
  all names readable, authentic US style. TIM = JP header/palette.
- RING OUT banner (tools/ringout_banner.py): cropped "Ring Out!"
  (x118-234) from the US "Double Ring Out!" banner (word gaps are
  11px, letter gaps 3-5px), centered on a fresh 256x32 canvas.
  Verified visually. (First attempt caught "le Ring Out!" — the
  gap inside "Double" is 4px; word gaps are 11px.)
- EXE NAMES (tools/exe_names.py): pointer table found at 0x5D7B0
  (16 pointers; JP names @ 0xD14-0xE38, 292 B; each string 00 00
  terminated + zero-padded to a multiple of 4). Repacked with
  Title Case full-width Latin surnames/ring names (Fujinami, Chosyu,
  Mutoh, Chono, Hashimoto, Hase, Sasaki, Koshinaka, Thunder Lyger,
  Tenzan, Kanemoto, Norton, Great Muta, Warrior, Tanaka, Hattori),
  NO leading/trailing spaces (needed to fit: 280/292 B, 12 spare),
  16 pointers updated. Verified: all decode via new pointers;
  bytes outside name area + pointer table identical.
- BANNER MAPPING confirmed visually (work/us-bigmes-sheet.png):
  big00 and still champion / big01 and new champion / big02 Time's
  up! / big03 Opponent gives up! / big04 Disqualification! /
  big05 Final Match! (128x32) / big06 Disqualification! (dup) /
  big07 Double Ring Out! / big08 Referee stops match! / big09 by
  split decision (128x32) / big10 Winner (32x16) / big11 The Winner
  (128x64). All 14 replacements have IDENTICAL size + VRAM coords
  to their JP counterparts — drop-in safe.
- PAC_GAME_MES rebuilt (tools/rebuild_gamemes.py): 13,848 B (was
  23,772); slots 0,2,18,30,31 kept byte-identical; 19/19 sections
  verified byte-exact on decompress. SLOT NUMBERING CORRECTION:
  slots are 0-2, 10-23, 30-31 (NOT 11-24/26-27 as first recorded).
- DTPAC.PAC rebuilt (tools/rebuild_dpac.py): 2,945,024 B, 1438
  sectors (was 2,955,264 / 1443). DPAC header: total = data-area
  size (file_size - 0x2000); entries in sector order, contiguous,
  sector-padded. 143/143 unchanged entries byte-identical.
  TIM_END swapped to the US "The End" (same 8256 B, 128x128, same
  VRAM (992,128)).
- ISO PATCHED (tools/patch_iso.py): work/tr1-en-track1.bin +
  work/tr1-en/ full disc set (patched track 1 + original tracks
  2-7 + new .cue). Verified: ISO directory identical; ONLY
  SLPS_000.84 + TOK/DTPAC.PAC differ; patched files read back
  byte-exact. EDC/ECC NOT recomputed (emulators don't verify;
  noted as a caveat, real hardware would flag it).

## Status
- [x] 1. SOURCE — both discs verified (SHA-1 ✓), extracted
- [~] 2. SURVEY — disc + PAC/BPE/TIM formats cracked; banners + names +
  font mapped; MENUS still not located (boot + look next)
- [~] 3. TRANSLATE — DONE except menus/title/staff: name sheet
  (tools/name_sheet.py, US block-caps glyphs condensed, all 16 full
  names fit, verified visually); "Ring Out!" banner
  (tools/ringout_banner.py, cropped from US "Double Ring Out!");
  EXE names (tools/exe_names.py, Title Case full-width Latin,
  repacked 280/292 B, pointers updated); 12 US banner TIMs mapped
  1:1 (all same size + same VRAM coords as JP). LEFT: menus (need
  mednafen boot), title/subtitle strings (decide after boot),
  TIM_STAFF 1-4 redraw (low priority), event poster (US kept it JP).
- [~] 4. BUILD — BPE COMPRESSOR DONE + proven 78/78; WRES section table
  decoded (slots 0-2, 10-23, 30-31); PAC_GAME_MES rebuilt (13,848 B,
  was 23,772; 19/19 sections verified byte-exact on decompress);
  DTPAC.PAC rebuilt (2,945,024 B, 1438 sectors; 143/143 unchanged
  entries byte-identical, TIM_END swapped to US "The End"); ISO
  patched in place (work/tr1-en-track1.bin + work/tr1-en/ disc set,
  verified: only SLPS_000.84 + DTPAC.PAC differ). LEFT: CHD
  conversion (needs chdman), build-all script, western-heart push.
- [ ] 5. QA — boot patched image in mednafen, verify English
- [ ] 6. DELIVER — finals to Oracle VM, tools/tables to western-heart


## 2026-11-20 ~03:00-03:30 UTC — MENU FONT HUNT (save-state + disassembly)
- Parsed mednafen save state (work/savestate.bin, 4,244,464 B, magic
  MDFNSVST): sections have ASCII names (MainRAM.data8 @ 0x385A7,
  SysControl.Regs, PixelBuffer.pix32 @ 0x242DD5). RAM base (0x80000000)
  at save offset 0x385B8 (verified: EXE .text matches at 0x485B8).
  VRAM = PixelBuffer.pix32, 1024x512 16-bit, data @ 0x242DEB (1 MB).
  Rendered to work/vram.png: framebuffers (2x match scene, timer 00:40,
  HUD names), big digits, banner TIMs, YUKE'S logo, brown 4bpp/8bpp
  texture blocks (misrendered as 16-bit = noise; NOT readable this way).
- CORRECTION: name pointer table is at RAM 0x8006CFB0 (file 0x5D7B0),
  NOT 0x8005CFB0 (arithmetic error in earlier notes). EXE IS loaded
  contiguously (verified at 13 anchor points). The EXE patch is
  unaffected (file offsets + pointer VALUES were correct).
- Name table referenced via lui 0x8007 + addiu -0x3050 at RAM 0x8003C130
  + 0x8003C168 (in a records-screen function). Digit table 0x8006CFF0
  referenced at 0x8003BF68/0x8003BFEC/0x8003C0AC/0x8003C0F8. Function
  0x80066BC8 = string append (strcat-like); callers build composite
  Shift-JIS strings: [digit][秒][name1][対][name2][spaces] for records.
- Found strings: 秒 (seconds) @ RAM 0x80074F24, 対 (vs) @ 0x80074F28,
  full-width digits ０-９ @ 0x80074EEC+, full-width space @ 0x80074F14.
  Memory-card save names: "BISLPS-00084BBOUT-00" + "BISLPS-00084KISEKI"
  (US: "BASLUS-00408..."). Table region 0x8006CE00-0x8006D200 = menu
  layout coords + function-pointer menu records + save names + name/
  digit tables. NOT the menu strings themselves.
- RULED OUT: menu strings are NOT in the EXE in Shift-JIS/EUC-JP/
  JIS/UTF-16 (whole-disc search, 2 false positives in movie data);
  NOT in the US EXE as ASCII (no menu strings there either); NOT in
  any of the 656 BPE sections (all TIMs except 18 WMD models in
  PAC_WRES); NOT in any DPAC TIM. The 0x8006CE00+ table region + the
  0x5D380 ASCII-punct table are SHARED JP/US data (107 diff bytes,
  mostly +0x1C pointer relocations) — UI layout, not font/strings.
- NEXT for menus: find the Shift-JIS text RENDERER in code (the
  function that draws the built strings — likely called from the
  records/menu code with (x, y, string, color)). Its font-base address
  reveals the font location. Fallback: BIOS font check (scph1000.bin).

## 2026-11-20 ~03:10-03:35 UTC — QA: PATCHED DISC HANGS (debugging)
- Full patched disc boots to title fine, but pressing Start -> BLACK
  screen, hung (mednafen still running, no new CD reads). Original JP
  disc: Start -> main menu works (verified 03:29 UTC).
- FIRST SUSPECT (ruled out as sole cause): rebuild_dpac.py repacked
  entries after PAC_GAME_MES down 5 sectors (86 entries: KYAKU0-3,
  all SE banks, REP/END/OP). Rewrote it to PRESERVE original sectors
  (PAC_GAME_MES zero-padded to its 12 orig sectors; file stays
  2,955,264 B; only the 2 replaced entries' ranges differ). Rebuilt +
  re-patched (0 zero-fill tail bytes now). STILL hung at Start->black.
  (Sector preservation kept anyway — safest rebuild.)
- ISOLATION TEST (EXE-only, original DTPAC): boots to title, but Start
  x3 did NOT advance (stayed on title, not black). DIFFERENT symptom
  from full patch (black). EXE-only ISO verified: EXE reads back
  byte-exact via psx_iso.py extract-file. Patched EXE verified: all 16
  pointers decode to correct English names; all 280 diff bytes within
  name area (0xD14-0xE38) + pointer table (0x5D7B0-0x5D7F0); title
  intact; NO second name-pointer table exists in the EXE.
- EDC/ECC: mednafen logs "Uncorrectable error(s)" for patched sectors
  (EXE sector 27 = PSY-Q CD debug strings only, harmless; DTPAC
  sectors 1063-1073 = PAC_GAME_MES range). Mednafen returns the data
  anyway (game boots + shows title), so EDC is likely NOT the hang
  cause. Still, EDC/ECC recomputation is TODO for a clean final disc.
- OPEN QUESTION: does the patched EXE really freeze at title, or was
  the EXE-only Start failure an input fluke? Re-test needed with fresh
  mednafen. If real: the game must touch the name strings/pointers
  during boot/title (before any name is displayed) — mechanism TBD
  (save-state PC diagnostic: save state while frozen, read CPU PC).
- VM REPLACED again ~03:33 UTC (uptime reset). mednafen/xdotool gone;
  os-intent replay restoring. Xvfb present. ~/.mednafen (BIOS+config)
  intact. /tmp/mednafen-x gone (re-extract after replay if needed).
- DISK: quota errors (Errno 122) hit during test-ISO writes despite
  48G free (group quota?). Freed ~800MB: deleted work/pac-tim/*
  (regenerable), work/pac-all/* (regenerable), tr1-jp audio tracks
  2-7 (byte-identical copies in tr1-en/), the TR1 zip (re-downloadable,
  SHA-1 recorded). toukon-english now 1.5G. Test ISOs: test-exe-only.bin
  kept; test-dtpac-only.bin NOT yet built (write failed on quota).
  NOTE: original JP cue now broken (audio tracks deleted) — use
  work/test-orig.cue (orig track1 + tr1-en audio) for the original.

## 2026-11-20 ~04:00-05:15 UTC — Hang bisection, tests E-T (BREAKTHROUGH x2 + new blocker)
- Test E (US names + [1] Hase): MENU. 'H' fine.
- Test F (my names slots 0-7, US ptrs): MENU. Test G (US 0-7 + my 8-15
  shortened): MENU. Test H (US + full "Thunder Lyger" + "Great Muta"):
  MENU. All 16 names proven good individually/in groups.
- Test I (my full EXE + 12-byte name-area gap filled with 81 40 spaces):
  MENU — **ROOT CAUSE #1 FOUND**: the zero gap after the last name read
  as an empty string and froze the title->menu transition. Fixed in
  tools/exe_names.py (fill remainder with full-width spaces). Output
  byte-identical to proven test7 EXE.
- Full patched disc STILL hung (black after Start) -> second hang in DTPAC.
- Test J (EXE fix + TIM_END only): MENU. Test K (EXE fix + PAC_GAME_MES
  only): BLACK. PAC_GAME_MES is the culprit.
- Test L (GAME_MES with equal-size BPE blocks, no 2-byte tail): FROZEN TITLE.
  Test M (GAME_MES, size field left at orig 23772): BLACK. Test N (repack +
  Yuke's US section in slot 16): FROZEN TITLE. Test O (in-place GAME_MES,
  my sections, zero pad): FROZEN TITLE. Test P (in-place, Yuke's US section
  in slot 16, zero pad): FROZEN TITLE. Test S (US section, orig-bytes pad):
  BLACK. Test T (only 3 padding bytes 00->FF in slot 16): MENU.
- Test R (no-op DTPAC rebuild, byte-identical): MENU. Rebuild process OK.
- EDC RULED OUT: save-state RAM inspection proves mednafen returns CORRECT
  data for EDC-failed sectors (English "Fujinami" in RAM at 0x80010514
  despite sector 27 EDC error). Original disc has ZERO EDC errors; patched
  discs error exactly in modified sectors (mednafen sector# = LBA+2).
- No checksums of PAC_GAME_MES/DTPAC/slot16/TIM in the EXE (CRC32/Adler/
  sum/XOR all absent). Nesting depth max 10 both (orig max 10). Heap max:
  US slot16 = 7, JP max = 11 (within range). Dict skip encoding same.
- CURRENT STATE: padding bytes are safe (test T); ANY change to a BPE
  section's compressed content hangs the game, even a genuine Yuke's US
  section. Cause unknown. Next: frozen-state forensics (test P save state:
  RAM/VRAM/CPU) or disassemble the game's BPE decoder to find how it
  differs from bpe.py.
- Quota: severe. Deleted pmpw-usa.bin/.chd (re-downloadable, SHA-1 in
  summary), tr1-en-track1.bin, tr1-en Track 1, all test ISOs except one at
  a time. Mednafen HOME moved to /tmp/mhome (BIOS + cfg copied) so saves/
  snaps/sav bypass quota. Input broken post-VM-replacement: Return (Start)
  + F9/F5 work, but S (Down) / KP_6 (Circle) do NOT register (keymap is us,
  setxkbmap done, --window flag tried). Navigation past main menu BLOCKED
  until input is fixed.
- BPE compressor fixed: equal-size blocks (no tiny tail). rebuild_gamemes.py
  rewritten to IN-PLACE replacement (no repack; header/table byte-identical).

## 2026-11-20 ~05:15-07:05 UTC — hang bisection, tests U-AW (the name-sheet/banner hang)

### The sequential-read rule (test AD) — ROOT CAUSE #2 FOUND
- Test U (test P rebuild, frozen-state forensics): US slot 16 TIM fully
  decompressed in RAM at 0x800828EC; PAC_GAME_MES in RAM at 0x801F6258;
  VRAM NOT updated (zeros at TIM location). Hang is AFTER decompression,
  BEFORE VRAM upload. Frozen RAM has 149 BPE sections vs working 120.
- Tests V/W INVALID (single-track cue artifact — see below).
- Test X (control): known-working EXE-only disc with SINGLE-TRACK cue =
  BLACK. PROVED the single-track cue itself causes black-screen hangs.
  ALL tests must use multi-track cues. Dummy silent audio tracks in
  work/dummy-audio/ (sparse, 60s each, 0 disk).
- Test W2 (my encoder slot 4, multi-track cue): FROZEN TITLE. My
  encoder's output genuinely hangs (before the length fix).
- Dictionary analysis: original has forward refs + literals in groups;
  mine has neither. My re-emitted dict parses to IDENTICAL pairs.
- Test Z (orig dict re-emitted with my emit_dict, 1919B): BLACK.
- Test AA (one 3-entry group split into three 1-entry groups, 1919B):
  FROZEN TITLE. (Both later explained by the length rule: 1919 != 1917.)
- Test AB (cnt>=3, 2 blocks, 1919B): BLACK. (Length rule.)
- Test AC (genuine Yuke's slot 5 section in slot 4's area, 813B in
  1920B slot): BLACK. LED TO THE SEQUENTIAL-READ HYPOTHESIS.
- **Test AD (slot 4 JP TIM, my encoder, 1 block 1888B + 29B dummy =
  EXACTLY 1917B): REACHES THE MENU. ROOT CAUSE #2: the game reads BPE
  sections SEQUENTIALLY by csize. A rebuilt section MUST be EXACTLY
  the original's total length. Dummy zero-output blocks (all-literal
  dictionary + u16 blen=0) pad to the exact length.**
- bpe_compress.py: added dummy_block(), split_padding(), pad_payload(),
  compress_section_exact(). rebuild_gamemes.py uses compress_section_exact.

### The name-sheet hang (tests AE-AJ)
- Full patch boot: FROZEN TITLE, then BLACK (after dummy cap).
- Test AE (Group A: slots 1,10-15): BLACK. Problem in Group A.
- Test AF (slot 1 EN name sheet alone, thr=3, 3 real + 6 dummy = 9
  blocks): FROZEN TITLE. Slot 1 alone hangs.
- Test AG (slot 1, thr=9, 3 real + 1 dummy = 4 blocks): BLACK.
- Test AH: my encoder CANNOT fit JP TIM in 3 blocks (2710B > 2687B).
- Test AH2 (US name sheet TIM, my encoder): BLACK. Not specific to my TIM.
- Test AI (slot 1, thr=12, 2 real + 1 dummy = 3 blocks): BLACK.
- **Test AJ (JP name sheet TIM, my encoder, 2 real + 1 dummy (195B) =
  3 blocks): REACHES THE MENU (52,289B screenshot). JP pixels WORK;
  English/US pixels HANG. Encoder + dummy padding proven good.**

### Red-shadow hypothesis (test AK) — RULED OUT
- JP TIM uses palette index 2 (red shadow, 1827px); EN/US TIMs use NO
  index 2. Added (1,1)-offset red shadow to name_sheet.py (3543px).
- Test AK (EN+red, thr=3, 2 blocks + 1 dummy 23B): BLACK. Red is NOT
  the fix. Reverted the red shadow.
- AK's dicts were 366/376B (vs AJ 256/251B, orig max 228B) — led to
  the dictionary-size hypothesis (below).

### Dictionary-size hypothesis (tests AL, AM) — RULED OUT
- compress_section_exact updated to auto-select block count keeping
  dicts <= 256B; split_padding MAX_BLOCK raised to 199B.
- Test AL (EN name sheet, 4 real blocks, dicts <=219B, 3 dummies =
  7 blocks): FROZEN TITLE. Small dicts don't fix it.
- **Test AM (JP TIM + ONE PIXEL flipped, 2 real + 1 dummy, dicts
  256/251 — same as AJ): BLACK. A single pixel change hangs it.**
  AJ vs AM: same pair codes (119), 52 codes have different (a,b)
  values; block 1 identical; max heap identical (8,9); max expansion
  identical (96B). The game is sensitive to the specific pair
  assignments / block data, not sizes.

### Yuke's-style grouping (test AN) — RULED OUT, and it BROKE slot 11
- Rewrote emit_dict to match Yuke's grouping (literals inside groups;
  byte-identical to Yuke's for the same pairs, verified).
- Test AN (EN name sheet, new emit_dict, 3 real + 4 dummy): BLACK.
- **Test AQ (slot 11 JP TIM, NEW emit_dict — the test AD case):
  BLACK. The new emit_dict BROKE the previously-working case.**
  AQ had 1 real + 2 dummies (5B + 15B) vs AD's 1 real + 1 dummy (29B).
- REVERTED emit_dict to the old split-group version (proven in AD/AJ).
  Also fixed split_padding to avoid 5-byte dummies (splits even needs
  into two roughly-equal odd parts).

### Full patch is blocked beyond slot 1 (tests AO, AP, AR)
- Test AO (full EN patch, slot 1 = ORIGINAL JP): FROZEN TITLE.
  Slot 1 is NOT the only blocker.
- Test AP (slots 10-15 EN, rest JP, new emit_dict): BLACK.
- Test AR (slots 10-15 EN, OLD emit_dict): BLACK. Emit_dict version
  doesn't matter for the banners.

### CLUT/VRAM transplant (tests AS, AT) — RULED OUT
- US banner TIMs use CLUT at (240,480-491) + white/black/red palette;
  JP banners use CLUT at (736,256) + 16-color gradient palette.
  Image VRAM (640,256) + dimensions are IDENTICAL.
- Added transplant_jp_header() to rebuild_gamemes.py: JP header +
  palette (CLUT[2] set to pure red 0x001F) + US pixels remapped
  (swap indices 0<->1). Verified headers match JP.
- Test AS (slots 10-15 EN, transplanted): BLACK.
- Test AT (slot 11 EN ONLY, transplanted): BLACK. A single EN banner
  hangs. The transplant didn't fix it.

### Dummy-block-count hypothesis (tests AU, AV) — RULED OUT
- Test AT's section has 10 blocks (1 real + 9 dummies) — the EN TIM
  compresses to 356B, needing 1545B padding. Threshold/pair-cap
  tuning can't inflate the payload (max ~990B with 5 pairs).
- Test AU (slot 11 EN, 2 real + 3 dummies of 491B = 5 blocks): BLACK.
- **Test AV (slot 11 JP TIM, 1 real + 3 dummies (9+9+11B) = 4 blocks):
  REACHES THE MENU (39,310B). 4 blocks work for the JP TIM. Block
  count is NOT the issue.**

### Save-state forensics (test AT hung state)
- PAC_GAME_MES in RAM at 0x801F6280. 149 BPE sections in RAM.
- EN slot 11 TIM NOT in RAM at all (not even the first 64B).
  Compressed section IS in RAM. Hang is DURING (or before)
  decompression of slot 11 — no output produced.
- Slot 1 (name sheet) FULLY decompressed in RAM at 0x801AB408.
- Slot 2's head (304B) in the decompression buffer at 0x800828EC
  (then diverges — buffer partially overwritten or incomplete).
- Slots 0, 10 not in RAM. Game stopped after slot 1/2, before slot 11.

### Genuine US section + dummy (test AW) — HANGS DURING BOOT
- Test AW (slot 16 = genuine Yuke's US "NO LIMIT" section 218B +
  1 dummy 79B = exactly 297B): BLACK DURING BOOT (before title).
  Save state: PAC_GAME_MES NOT in RAM at all. Game hung BEFORE
  loading PAC_GAME_MES. ISO verified byte-correct (DTPAC + EXE
  read back exact). The dummy appended to a Yuke's section breaks
  boot; the same dummy approach works after MY sections (AD/AJ/AV).
  Cause unknown.

### Current status (2026-11-20 ~07:05 UTC)
- WORKING (proven): EXE English names; TIM_END swap; recompressing JP
  TIMs with my encoder at exact length (slots 1, 11 — tests AJ, AD, AV).
- HANGING: ANY English/US TIM content in PAC_GAME_MES (name sheet +
  all banners), even with JP headers/palettes transplanted, even as
  genuine Yuke's sections with dummy padding (test AW).
- RULED OUT: EDC, checksums, dict size, dict grouping, block count,
  red pixels, CLUT/VRAM location, emit_dict version, TIM content
  checksum, heap depth, max expansion.
- OPEN HYPOTHESES: (1) the game's BPE decoder has a bug/limitation
  with certain pair assignments or block-data byte patterns that my
  encoder produces but Yuke's doesn't (test AM: 1 pixel -> 52 pair
  reassignments -> hang); (2) the dummy-block dictionary layout
  interacts badly with the game's decoder state after a Yuke's block
  (test AW); (3) the game does something pixel-dependent with the
  decompressed TIMs that English text breaks (but test AT shows the
  hang is BEFORE any slot 11 output is produced, so this is unlikely
  for slot 11).
- NEXT: find the BPE decoder in the EXE (disassembly) and understand
  its exact dictionary/block parsing; OR try compressing the EN TIMs
  with Yuke's exact block split points + pair assignment order.

## 2026-11-20 ~07:05-07:42 UTC — THE BREAKTHROUGH (tests AX-BE)
- Test AX (slot 16 EN transplanted, my encoder, 313B): BLACK. Hangs.
- Test AY (genuine US slot 16 section + 95B dummy = 313B CORRECT length; test AW had wrong 297B target): FROZEN TITLE. Even genuine Yuke's section hangs. My encoder ruled out for slot 16.
- Ink bbox: JP slot 16 ink touches edges (x0..78, y0..13); US ink inset (x6..73, y2..13). Test AZ (US TIM + white edge ink): BLACK (1583B). Edge-touching NOT the fix.
- Test BA (slot 11 EN, partial-raw, 4 blocks): BLACK. Block count definitively ruled out.
- BPE decoder FOUND in EXE at 0x80048a20 (via "BPE " magic lui 0x2045/ori 0x5042). Disassembled fully: uses scratchpad dict1 @0x1F800100, dict2 @0x1F800200, heap @0x1F800300 (256B max). Logic matches bpe.py exactly (LIFO heap, blen countdown, dummy blen=0 skip). Decoder is CORRECT.
- TIM processor 0x8004a7fc just uploads to VRAM (no pixel scan). Loader loop 0x800187dc processes 19 slots. Section pointers from PAC table (preserved).
- Save-state CPU forensics (test BC): GPR section at 0x23867B. Hung in GPU/DMA wait loop 0x8005475c: counter A (0x8007500C)=0 != counter B (0x80075010)=1. Working AJ2: A=B=3. Stack shows TIM upload path (RAs 0x800527FC, 0x80049DBC, 0x80049CC8, 0x8004A120).
- Test BB (slot 11 JP + 1px): BLACK. Test BC (name sheet JP + 1px in BLANK row): BLACK. Any pixel change hangs.
- Test BD (JP slot 12 TIM in slot 11): BLACK. Even JP<->JP swap hangs. NOT about EN vs JP pixels.
- **Test BE (slot 11 JP + 1px, ORIGINAL Yuke's dictionaries byte-identical, block data re-encoded via DP shortest-path, 868 codes = orig, 0 padding): WORKS!** Screenshot shows a live MATCH (Sasaki vs Hashimoto, 00:03). **THE ISSUE WAS MY ENCODER'S DICTIONARY BYTES, NOT THE PIXELS.** The game's decoder mishandles my emit_dict's byte-level encoding for changed data (though it handles it for original data). FIX: reuse Yuke's original dictionaries, re-encode only block data via DP. Block split for slot 11 is 2085/2075 (NOT even halves).
- VM replaced 4th time ~07:10 UTC (service restart during test AZ wait). Rebuilt mednafen/xdotool/Xvfb from apt cache.

## 2026-11-20 ~07:46-08:18 UTC — Tests BF-BM: the change-threshold bisection
- Test BF (slot 11 JP+1px, my encoder, forced 2-block split): INVALID — section 1930B, 13B over target. All 2-block splits overflow (1905-1928B). Killed, not trusted.
- AV vs BB deep comparison: dictionaries IDENTICAL (0 differing codes), max heap identical (6), output identical except 1px. Only block data differs (blen 1770 vs 1773, first diff src 69: AV=0x43, BB=0x16). Both expand to zeros. Heap empty at divergence. Block data contains all 256 byte values in both.
- Test BB2 save state: CPU in/near BPE decoder ($t2/$t3/$t4 = dict1/heap/dict2, $t5=0x100, $t7=0xFFFF, $k0=0x80048B1C). Scratchpad dict has 14 pairs (matches slot 0, NOT BB's block 0 with 33 pairs) — stale or early-load state. Modified TIM NOT in RAM. Counters A=B=39 (not the wait-loop hang).
- Dummy blocks verified OK: all sizes 5-491B parse to exactly i=256 under game logic. Scratchpad offset verified (single occurrence, size 1024).
- EN banner fitting with JP dicts via DP: FITS slots 10 (189/255), 11 (1257/1901), 21 (1192/1946), 22 (915/1060), 23 (955/1052). OVER slots 12 (+1007), 13 (+972), 14 (+3237), 15 (+435), 16 (+114), 17 (+641), 19 (+295), 20 (+591). Name sheet OVER by 3662B (JP) / 1644B (US).
- Test BG (slots 10,11,21,22,23 EN, Yuke's dicts + DP): BLACK during boot. HANGS.
- Test BH (slot 11 EN alone, Yuke's dicts + DP, 6 blocks): BLACK. HANGS.
- Test BI (JP slot 12 TIM in slot 11, Yuke's dicts): UNENCODABLE (DP returns None — slot 12 TIM has byte patterns not representable with slot 11 dicts).
- Test BI2 (slot 11 EN, Yuke's dicts + DP, 2 real + 2 large dummy = 4 blocks): BLACK. Block count NOT the issue.
- Test BJ (slot 11 JP + 100 bytes EN at 0x200-0x263, Yuke's dicts + DP): BLACK. HANGS. Save state: TIM NOT in RAM, decomp buffer matches only 24 bytes (mid-CLUT), $ra=0x80048674, $t4=dict2. Changed region present at 0x801AB608 (heap area).
- Decoder disassembly re-read: delay slot at 0x80048b80 (`move $v0, $t0`) means push IS to heap[$t0] — proper LIFO stack. My earlier "heap[a]" reading was WRONG (missed the delay slot). Decoder is CORRECT. Faithful simulation with wrong heap logic OOM'd (infinite loop) — discarded.
- Max heap identical (9) and max expansion identical (64B) for JP orig, BE, BJ. Heap NOT the issue.
- No checksums of slot 11 TIM/section in DTPAC or EXE (CRC32/Adler/sum32/sum16/XOR32, LE+BE). No checksum validation.
- DP vs Yuke encoder (US slot 16 "NO LIMIT"): DP produces DIFFERENT block data (122 vs 124 bytes, first diff byte 16: Yuke `e6 e6 e6 f4`, DP `f4 e6 e6 e6`). Yuke's encoder is NOT optimal. Both decompress to same TIM.
- **CHANGE-THRESHOLD BISECTION (Yuke's dicts + DP, slot 11, change at TIM 0x200):**
  - BE (1 pixel): WORKS (live match).
  - BK (10 bytes, 6 diffs, 3 blocks blen 859/721/0): WORKS — live match screenshot (Fujinami vs Fujinami, 01:50, 59,116B).
  - BM (25 bytes, 12 diffs, 4 blocks blen 852/721/0/0): BLACK (1,677B). HANGS.
  - BL (50 bytes, 3 blocks blen 853/721/0): BLACK (275B). HANGS.
  - BJ (100 bytes, 3 blocks blen 843/721/0): BLACK. HANGS.
  - Threshold between 10 and 25 bytes (6-12 differing bytes). All changes JP ink -> EN zeros.
  - BK vs BM block 0 divergence: src 129, output 503 (just before change at 512), heap empty. BK code 0xB0 (pair, 12 zeros, depth 4), BM code 0xF3 (pair, 7 zeros, depth 3). Both trivial zero-runs. Decoder handles both fine.
- **CONCLUSION: the hang is NOT in the BPE decoder (proven correct), NOT the dictionary (identical for Yuke's method), NOT the heap (identical), NOT the block count, NOT the dummy blocks, NOT checksums. The game tolerates <=10-byte changes but hangs on >=25-byte changes to slot 11's TIM. The trigger is downstream of decompression (TIM processing/VRAM/game logic) OR in a decoder subtlety not yet found. NEXT: try replicating Yuke's ENCODER (greedy, not DP) — DP's optimal-but-different block data may be the issue; OR test whether change LOCATION matters (25 bytes elsewhere); OR investigate post-decompression TIM handling.**

## 2026-11-20 ~08:18-08:40 UTC — Tests BN-BS2: the block-data sensitivity
- Test BN (slot 11 EN banner + EXACT JP CLUT, header byte-identical, Yuke's dicts + DP, 6 blocks): BLACK. CLUT is NOT the issue.
- Test BO (17 bytes, 9 diffs): BLACK. Threshold between 6 diffs (BK works) and 9 diffs (BO hangs).
- Test BP (3 bytes at 0x20A-0x20C ONLY, DP both blocks, 2 dummies 5+7B): BLACK. Location matters, not just count. BUT confounded: BP DP-encoded block 1 (unlike BK which kept original block 1).
- Test BQ — DECISIVE (slot 11 JP TIM UNCHANGED, both blocks DP-encoded, blens 865/715 vs orig 868/721, 1 dummy 9B): BLACK. **DP's block data hangs the game even with byte-identical TIM output.** BE worked because DP's output matched original blen (868/721) for the 1px change. The game is sensitive to BLOCK-DATA BYTES, not just the TIM.
- BQ vs JP block 0 first diff at src 53: JP `e6 e6 f7 61` vs BQ `61 f7 e6 e6` — SAME codes reordered, both expand to 94 identical zeros. Block 1 first diff src 34: JP `fe 90` vs BQ `00 9a`.
- Max heap identical (9) for JP and BQ. Heap depth NOT the issue.
- No hardcoded blen/csize in EXE (868 hits at 0xDA84/0xDA98 are MIPS instruction offsets, false positives).
- Test BR (4-byte reorder ONLY: JP `e6 e6 f7 61` -> `61 f7 e6 e6` at src 53, output TIM byte-identical): WORKS — live match (56,088B). Small reorder is fine. Trigger is elsewhere in BQ's data.
- PAC loader (0x800187DC) calls the SAME decoder 0x80048a20 (verified). Mallocs dsize, decodes, calls TIM processor 0x8004a7fc, frees. No separate decoder.
- JP EXE has NO PAC_BIG_MES reference (US EXE has it at 0x11AC). US uncompressed-banner approach would need major EXE hacking.
- Test BS (JP blk0 + BQ blk1 DP +1B split, 5B dummy): BLACK. Confounded by 5B dummy (suspect from AQ/AN).
- Test BS2 (JP blk0 + BQ blk1, merge attempt): FAILED TO BUILD — no mergeable adjacent literals, need 6B unbuildable. Not tested.
- **CURRENT STATUS: the game accepts Yuke's ORIGINAL block data (+ tiny changes, BE/BK/BR) but hangs on DP-re-optimized block data (BQ/BS), even with identical TIM output. The decoder is proven correct (proper LIFO stack, delay slot accounted for). The sensitivity mechanism is UNKNOWN — not heap, not blen, not checksums, not dictionary, not CLUT. NEXT: surgical-patch approach (keep Yuke's block data for unchanged regions, re-encode only changed regions) OR pivot to menu font + partial delivery.**

## 2026-11-20 ~08:40-08:50 UTC — Tests BT + MIPS emulation: the BPE paradox
- **MIPS EMULATOR BUILT (tools/emu_bpe.py, Unicorn 2.1.4).** Emulates the game's actual BPE decoder (0x80048a20). Unicorn quirk: cannot fetch from KSEG0 (0x80000000+) — must map code at PHYSICAL addresses (0x80000000 -> 0x00000000). JP slot 11: MIPS output == Python output (4160B, match). BQ slot 11: MIPS output == Python output (4160B, match). **THE DECODER IS PROVEN CORRECT FOR BQ.** Instruction counts: JP 114,652, BQ 115,291 (0.6% difference, not a timeout).
- Test BT (BQ section + ORIGINAL EXE): BLACK (275B), still black after Start. **The hang is purely from BQ's section bytes, NOT an EXE interaction.**
- BT save state (08:45 + 08:47, 2 min apart): only 2/32 GPRs differ. $k0=0x80048b0c, $ra=0x80048674, $sp=0x801f6238 IDENTICAL. CPU truly stuck. $ra=0x80048674 is just after malloc in the BPE loader (0x80048668 lw dsize, 0x8004866c jal malloc, 0x80048674 move $a0,$s0, 0x8004867c jal decoder). $k0 may be an interrupt artifact, not the true PC.
- BT RAM: PAC_GAME_MES NOT in RAM. Only one WRES (0x8008DF14) — NOT PAC_GAME_MES (zeros, table slot 11 = (4,0), total 0x20202020). BQ section head NOT in RAM. TIM NOT in RAM. 149 BPE sections in RAM. But mednafen log shows sectors 1065/1066 read (LBA 1063/1064 = slot 11's area). **The game READ PAC_GAME_MES but it's GONE from RAM — suggests a retry loop (read -> fail -> free -> repeat) OR the PAC was freed after a failed load.**
- Stale-dict2 test (MIPS emu, dict2[131]=5 pre-loaded): BOTH JP and BQ produce CORRECT output. Stale dict2 is NOT the mechanism. (BQ block 0 uses skipped code 131, JP doesn't — but it doesn't matter.)
- **BPE HANG: PARKED as uncracked.** Paradox: decoder provably correct (MIPS emu), TIM byte-identical, yet game hangs on DP block data. Mechanism unknown despite 70+ tests, full disassembly, MIPS emulation, and save-state forensics. Possible: a retry loop in the loader, a post-decode validation, or a mednafen-specific behavior. NOT worth more time now — pivoting to menu font hunt. If menus crack, ship EN menus + EN names + EN "The End" and document the banner blocker.

## 2026-11-20 ~08:50-09:00 UTC — Menu font hunt: strings not findable, font not in VRAM
- Main menu (from menu-main.png): 開場, 戦いの軌跡, ベストバウト, カードロード. Searched EXE + DTPAC + Track 1 for these in Shift-JIS: ONLY 戦いの軌跡 found (EXE subtitle at 0xF58, already known). 開場, ベストバウト, カードロード, 難易度, はい: NOT FOUND anywhere as Shift-JIS. (Earlier EUC-JP/JIS/UTF-16 searches also negative.) Menu strings are NOT stored as text — likely glyph indices or another encoding.
- VRAM (match save state): banners ARE in VRAM (vertical Japanese text, right side). Small menu font NOT visible as a texture — likely drawn from RAM bitmaps, not a VRAM texture. Left-edge "glyph grid" is indexed texture noise, not a font.
- HUD names (Fujinami vs Mutoh) render in ~10px kanji with color + outline. Font is NOT the BIOS font: EXE's 5 BIOS ROM references (0x8004E7A4-0x8004E800) are version-check/boot code (reads 0xBFC00100/0xBFC00104, calls 0xBFCE228 if version matches), not font access.
- Records function (0x8003BF00-0x8003C200) calls strcat (0x80066BC8) 10x, struct copy (0x8004B878), free (0x8004928C) 3x, 0x80066E18, 0x80047DCC. 0x8004928C is a FREE function (calls 0x8004e658 3x), NOT the renderer. The text RENDERER is still not found.
- **MENU STRINGS: PARKED as uncracked.** Strings aren't stored as text anywhere findable; font location unknown; renderer not found. Would need: find renderer via dynamic tracing (not available in this environment) or extensive static analysis of the UI code region.
- **DECISION: deliver what works (EN EXE names + EN "The End") + full blocker documentation. The BPE banners/name sheet and the menu strings are documented blockers for a future lane with more time/tools.**

## 2026-11-20 ~08:54-08:56 UTC — FINAL PATCH QA: PASSED
- **Final patch = EN EXE names + EN "The End" (TIM_END) only. No BPE changes.**
- Built: work/tr1-en-final-track1.bin (209,861,904B, SHA-1 17050fec804b94661892ae35cece7ae167d1f952).
- DTPAC.final.PAC: only TIM_END differs from original (3,181 bytes, all within TIM_END range).
- QA boot (testFINAL): boots to title (109,573B), Start -> main menu (39,310B), demo match plays live (59,197B, Fujinami vs Mutoh, 02:31). NO HANG.
- RAM proof: EN names Ｆｕｊｉｎａｍｉ (0x80010514), Ｃｈｏｎｏ (0x80010544), Ｈａｓｈｉｍｏｔｏ (0x80010550) in RAM. JP names 藤波辰爾, 武藤敬司 NOT in RAM.
- Note: HUD in demo mode still shows kanji (demo uses its own name source). EN names will show on character select / VS screens (EXE strings). Input problem (S/KP_6) blocks navigating to character select for visual confirmation.
- **DELIVERABLE: partial English patch (names + "The End"). Banners + name sheet + menus remain Japanese (documented blockers).**

## 2026-11-20 ~09:00-09:10 UTC — DELIVERY
- western-heart: commit 68ed4654 on branch muse/toukon-english (19 files,
  4815 insertions, 0 deletions). Tools + docs + WORKLOG + README.
  NOT PUSHED — no git credentials in this environment (HTTPS needs auth,
  SSH to GitHub blocked by proxy). Parent agent to push via GitHub connector.
  Note: western-heart-coverage is a SPARSE checkout; committed with
  `git add --sparse` after verifying index == HEAD (86,432 files).
  gitleaks not installed; files manually checked (no secrets).
- Oracle VM /home/ubuntu/toukon-english/: tr1-en-final-track1.bin
  (SHA-1 17050fec804b94661892ae35cece7ae167d1f952, verified),
  tr1-jp-track1.bin (SHA-1 284fd4f27d08556326a163f177923f92202e4cc4),
  testFINAL.cue, toukon-README.txt. VM disk now 1.4GB free (100% used).
- CHD NOT built (needs real audio tracks re-downloaded + chdman on VM).
- LANE COMPLETE (partial delivery). See README.md for next steps.

## 2026-11-20 ~14:00-14:25 UTC — M2 lane: PCSX control test + menu RE breakthrough

### PCSX ReARMed control test — BPE HANG IS MEDNAFEN-SPECIFIC (BLOCKER 1 CRACKED)
- Full-EN disc (all 14 banner/name-sheet replacements + EN EXE names) in PCSX ReARMed
  on the Oracle VM: boots, title, plays LIVE demo matches for 60+ s with ENGLISH HUD
  names (JYUSHIN THUNDER LYGER, TATSUMI FUJINAMI, KENSUKE SASAKI, KEIJI MUTOH).
  Screenshots: work/pcsx-fe-after10.png (02:23), pcsx-fe-after30.png (pin count "1"),
  pcsx-fe-after60.png (04:34). JP control matches (kanji HUD) in pcsx-jp-after*.png.
- The first run's "Yuke's logo after Start" was NOT a crash: pressing Start during the
  DEMO exits to the Yuke's logo (part of the attract loop: Yuke's logo -> title ->
  demo -> Start -> Yuke's logo). Confirmed in mednafen too (jp-demoexit3.png).
- Title times out to demo after ~20-30 s idle. Mednafen input: instant `key Return`
  does NOT register; must use keydown + 0.3 s hold + keyup (emu.sh pattern).
  F5 save-state does NOT work in this mednafen setup (no .nc file created).
- CONCLUSION: the BPE banner/name-sheet patch WORKS in the console's core
  (PCSX ReARMed). The 70+ test Mednafen hang is an emulator-specific artifact.
  Banners + name sheet + EXE names + TIM_END are DONE for the console.
- Demo HUD names are ENGLISH in the full-EN build (previous lane's "demo uses its own
  name source" note is explained: demo HUD uses the NAME SHEET, which is EN now).

### JP vs US EXE diff — WORKLOG CORRECTION
- JP vs US EXE: 293,154 / 417,792 bytes differ (70%). NOT near-identical as recorded
  earlier. The 0x8006CE00+ "shared table region" claim is also wrong (inside a
  12,847-byte diff block). Align by function/structure, not byte diff.
- PS-X EXE file offset = RAM - 0x80010000 + 0x800 (0x800-byte header). Earlier
  disassembly in this session used the wrong offset (off by 0x800) — corrected.
  Verified: name pointer table RAM 0x8006CFB0 = file 0x5D7B0.

### Menu text system — CRACKED (disassembly, capstone MIPS)
- 0x80011AE8(a0=x, a1=y, a2=?, a3=glyph_code) = glyph/text draw dispatcher.
  60 callers. a3 selects one of THREE texture-rect tables (8-byte entries =
  u16 tex_x, u16 tex_y, u16 w, u16 h):
  - T1 (a3 0-99): base RAM 0x8006A8F8, 65 entries (a3=65 is terminator 0xFFFF).
    Variable-width 16px-tall rects (16-208 px wide). VRAM x=512-576, y=0-240.
    => a 256x256 px 4bpp TEXT ATLAS at VRAM (512,0). THE MENU TEXT LIVES HERE.
  - T2 (a3 100-199): base 0x8006AB08. 16x16 glyphs (digits etc.), U steps of 4.
  - T3 (a3 200+): base 0x8006AB98. 256x16 full-width strips at VRAM (768,256+16k)
    => TIM_STAFF2's VRAM slot (768,256). T3 draws STAFF CREDIT lines, not menus.
    (Confirmed: TIM_STAFF2 JP = kanji staff names, US = English staff names.)
- 0x80047078 = number-drawing fn (div by 10, calls 0x80011AE8 with a3=digit+100).
- 0x80049964 = GPU packet builder (textured sprite, 0x2D000000). Table coords are
  VRAM coords; it splits them into texture-page + offset (x mod 64, y mod 256) and
  scales U by 4/2/1 depending on texture bpp (struct field +0x18 bits 7+).
  Texture structs are runtime pointers in globals [0x80079F6C] (T1), [0x8007A14C]
  (T2), [0x80079F1C] (T3).
- Menu strings are NOT text anywhere because they are PRE-RENDERED TEXT LINES in
  the T1 atlas texture. Translation = redraw the atlas in English.
- T1 atlas is NOT embedded in the EXE (no TIM found). NOT a top-level DTPAC TIM
  (no 64x256 TIM at VRAM (512,0); TIM_マット is only 32x128 there). Source file
  still to find: likely a BPE section in a WRES container, loaded at menu time
  (VRAM (512,0) is reused: wrestler body textures at match time, atlas at menu time).
- TIM_STAFF2 JP vs US rendered (work/font-hunt/): both are staff credits; US is
  English — drop-in replacement for the credits is available.
- PAC_COMMON sheet re-checked: costumes/poster/digits only, no menu text.
- NEXT: find the T1 atlas source file (string-draw wrapper hunt: callers with
  variable a3 at 0x800472f4/0x80047364; or search WRES containers for a 256x256
  4bpp TIM); then redraw in English (port US atlas if it exists) and re-test.

### MENU ATLAS SOURCE — FOUND (2026-11-20 ~15:30 UTC) — BLOCKER 2 CRACKED
- Full loader chain traced by disassembly (capstone MIPS):
  - Startup 0x80012120: 0x8004AD10(a1=0x8001000C="\\TOK\\DTPAC.PAC;1", a2=1)
    creates the DTPAC file record -> global [0x80079F54].
  - 0x80011F24: 0x800482AC(a0=malloc(0x18), a1=0x80010000="PAC_WRES").
    NOTE: RAM 0x80010000 holds "PAC_WRES\0" (file 0x800) and 0x8001000C holds
    the DTPAC path (file 0x80C) — the EXE's first bytes are data, not code.
  - 0x800482AC: 0x8004AF80(a0=DTPAC record, a1="PAC_WRES") -> 0x8004AE8C looks
    up "PAC_WRES" by 16-byte name in DTPAC's 145-entry table, reads its sectors
    from CD into RAM -> 0x8004840c inits the WRES container struct ->
    global [0x8007B1DC] = PAC_WRES container.
  - Texture init 0x800119B4: calls 0x800486e0 FOUR times with (a0=[0x8007B1DC]):
    a1=0xC8 (200) -> [0x8007B03C] (4th texture); a1=0xCA (202) -> T1ptr;
    a1=0xCB (203) -> T2ptr; a1=0xCC (204) -> T3ptr.
  - 0x800486e0(a0=container, a1=slot): 0x800483ec = slot DATA POINTER
    (data_base + u16(table+slot*4+8)*4); 0x800483d4 = slot SIZE
    (u16(table+slot*4+10)*4). If data starts with "BPE ", decompresses via
    0x80048a20 into a 0xEAA8-byte stack buffer; else memcpy. Then mallocs a
    0x1C-byte texture struct and calls 0x800492e4 (TIM parse + VRAM upload).
  - WRES container struct (0x8004840c): +0=base, +4=base+0x810,
    +8 (table_ptr)=base+0x880+*(base+0x814), +0xC=base+0x880,
    +0x10 (data_base)=table_ptr+0x400.
    PAC_WRES: *(0x814)=169580 (0x2966C), table_ptr=0x29EEC, data_base=0x2A2EC.
    (PAC_GAME_MES has *(0x814)=0, table 0x888, data 0xC80 — same formula.)
- PAC_WRES slots (JP, 310,164 B; 102 BPE slots total):
  - Slot 200: 28,336 B -> TIM 512x216 (55,360 B). = NJPW "KING OF SPORTS /
    NEW JAPAN PRO-WRESTLING" lion logo on dark texture. ALREADY ENGLISH.
    (work/font-hunt/tex200.png). No translation needed.
  - Slot 202 (T1 MENU ATLAS): 7,388 B -> TIM 256x256 4bpp (32,832 B).
    (work/t1-atlas.bin, work/font-hunt/t1-atlas.png). ALL menu text lines.
  - Slot 203 (T2 digits): 2,684 B -> TIM 256x128 (16,448 B).
  - Slot 204 (T3 staff lines): 4,644 B -> TIM 256x256 (32,832 B).
- US PAC_WRES slots (326,560 B; work/us-pac_wres.bin): SAME decompressed sizes:
  slot 200 512x216, slot 202 256x256 (32,832 B), slot 203 256x128 (16,448 B),
  slot 204 256x256 (32,832 B). US slot 202 = ENGLISH menu atlas
  (work/font-hunt/us-slot202.png): "12 Man Gauntlet", "PPW LEAGUE",
  "PPW TOURNAMENT", "CHAMPIONSHIP", "BEST BOUTS", "1 PLAYER", "2 PLAYER",
  "DEMO MATCH", "NO LIMIT", "VENUE", "SAVED GAME", "1st FLOOR", "2nd FLOOR",
  "DOME", "VITO'S", "SLAM ROCK", "STEREO", "MONO", "EASY", "MEDIUM", "HARD",
  "GO!", "TIME", "SOUND", "on/off", "WOW! LEVEL", "(cont)", "CROCK".
- JP T1 atlas text (read from work/font-hunt/t1-atlas.png):
  y=0: 試練の十二番勝負 | ベストバウト; y=16: G1クライマックス | リーグ戦 | オフ;
  y=32: G1クライマックス | トーナメント戦 | オン; y=48: IWGP選手権試合 | 試合開始 | BVD;
  y=64: 戦いの軌跡 | カードロード | 引き分け; y=80: VS プレイヤー2 | セメント | 難易度 | /;
  y=96: VS コンピュータ | (再開); y=112: 観戦席 | コンピュータ観戦 | モノラル;
  y=128: NJPW1 NJPW2 NJPW3 | 第 | 時間無制限 | 大阪会場; y=144: (red) 代;
  y=160: 試合会場 | シリーズ開催中 | リング | 特別リングサイド | ○×□ | スピーカー;
  y=176: ステレオ | ストロング | 試合時間 | 敗分数 | 東京会場A | 東京会場B | トレーニング;
  y=192: 2F特別席 | NJPW4 | 初代 | 勝対 | 分; y=208: 屋外特設リング | 開場 | スパーリング | 秒;
  y=224: 観戦席 | コンピュータ ... (work/font-hunt/jp-bottom.png); y=240: TBD.
- T1 TABLE = 65 rects (file 0x5B0F8; RAM 0x8006A8F8). Full list in session notes
  / tools (rect i: atlas_x, atlas_y, w, h — all h=16). Key: 33=(0,0,128) 試練の
  十二番勝負; 35=(0,16,208); 36=(0,32,208); 37=(0,48,144); 40=(0,64,80);
  42=(0,80,128); 43=(0,96,144); 30=(0,224,160); 32=(0,240,112). MANY RECTs
  OVERLAP (substrings / composite drawing, e.g. 34=(32,0,96) inside 33).
- CAUTION — US atlas is NOT a blind drop-in: the US and JP atlases pack DIFFERENT
  text at the same rect indices for some rects (verified: rect 33 matches —
  JP 試練の十二番勝負 = US "12 Man Gauntlet" — but rects 30/32 differ: JP 観戦席/
  ベストバウト vs US "2nd FLOOR"/"SLAM ROCK"). Activision rearranged the menu.
  The CORRECT English atlas keeps the JP rect layout and renders NJPW-correct
  English text per rect (harvest US glyphs for the font). Contact sheets:
  work/font-hunt/t1-map-*.png (JP vs US per rect), t1-jp-*.png (JP 3x).
  The 60 callers of 0x80011AE8 (tools/find_menu_calls.py) set a3 via registers/
  tables, not immediates — per-screen rect mapping needs data-flow tracing.
- Tools added: tools/scan_atlas.py, tools/scan_atlas_file.py (raw-4bpp atlas
  scans — EXE: no hit; DTPAC: 15,856 false positives, top hits are STAFF
  textures), tools/find_texptr_writes.py (lui 0x8008 + negative-offset pattern),
  tools/find_menu_calls.py (60 jal sites for 0x80011AE8).
- NEXT: (1) map all 65 JP rects -> English text (FAQ + atlas reading);
  (2) harvest US font glyphs, render English atlas (same TIM header/palette);
  (3) rebuild PAC_WRES slot 202 (BPE recompress; US slot 202 is SMALLER than JP
  — rebuild table offsets or pad to exact size); (4) rebuild DTPAC + ISO;
  (5) verify menus in PCSX ReARMed (needs input fix, see below).
  T3 (slot 204): swap US English staff atlas the same way. T2: digits, likely
  fine as-is (verify). Slot 200: already English, no change.

### RetroArch input — BROKEN on the VM (2026-11-20 ~15:00 UTC)
- Keyboard input does NOT reach RetroArch in the Xvfb setup. Proven: xdotool
  keydown/keyup Return, xdotool key --window, xte (XTest) Return, and xte F1
  (menu toggle) ALL fail — JP disc (known good, reaches menu in mednafen) goes
  title -> demo every time. Focus is correct (getwindowfocus == RetroArch window);
  input_driver="x", mappings correct (enter=Start, x=A, z=B). F1 not opening the
  RA menu proves input never arrives (not a game issue). xte installed via apt
  (/usr/bin/xte). NEXT: virtual gamepad via uinput (sudo available, /dev/uinput
  exists, root-only) + RetroArch udev joypad driver — untested. Without input,
  menu/character-select/VS navigation CANNOT be verified in RetroArch.
  Mednafen input WORKS (Return hold -> menu) but mednafen HANGS on any BPE-changed
  disc at title->menu, so it cannot verify the full-EN build either.

### VM disk — CHD BLOCKED (2026-11-20 ~15:17 UTC)
- VM disk 2.2G free (99%) as of ~10:17 EST (parent heads-up): PPP runner _work
  re-checked out 12G for a RUNNING job — DO NOT clean while it runs. Do not delete
  anything to make room without checking with the parent first. CHD build needs
  ~456MB TR1 zip re-download + ~400MB extraction + ~200MB CHD output — BLOCKED
  until disk relief. Check df -h before any big VM-side write.
- Local quota also tight (EDQUOT on small writes); workdir kept small (405M);
  local .bin copies deleted (all on VM or re-downloadable).

### Full-EN build status (2026-11-20 ~15:30 UTC)
- Build cf9f6bd6 (on VM /home/ubuntu/toukon-english/tr1-fullen-track1.bin):
  ENGLISH: EXE names, 14 banners + name sheet, TIM_END, US staff TIMs 1-4.
  STILL JAPANESE: menus (T1 atlas — source now FOUND, English atlas not yet
  built), T3 staff lines (US swap pending), JP event poster in PAC_COMMON
  (US kept it JP too — low priority). CHD not built (disk-blocked).
- PMPW LESSON (Mars, 2026-11-20 ~09:49, via MEMORY.md): lane 1 burned effort
  cracking JP menus/banners from scratch instead of porting ALL of PMPW's English
  assets first. M2 does PMPW-first: US banners, US TIM_END, US staff TIMs, US
  name-sheet font, US atlas glyphs. Rule: when an official other-language version
  of the same game exists, port EVERYTHING portable before from-scratch decoding.

## M2 — RetroArch input: FAILED, mednafen navigation: WORKS (2026-11-20 ~15:45–17:05 UTC)

### RetroArch/PCSX input — ALL PATHS FAILED (abandoned)
- Virtual gamepad (uinput, tools/vgamepad.py): device created (/dev/input/event6),
  events PROVEN via evtest (BTN_START 315, BTN_EAST 305). RetroArch detects it
  ("Pad #0", "Virtual Gamepad configured in port 1"). BUT no button reaches the
  game: tried udev driver with ordinal (0-15), raw-code (304-315/544-547), and
  SDL2 joypad driver — Start at title never advances; Start+Select menu combo
  (input_menu_toggle_gamepad_combo=1) never opens the RA menu. Keyboard (xdotool,
  xte, Return/F1) also fails, with and without openbox WM, with input_driver x
  AND sdl2. CONCLUSION: RetroArch on headless Xvfb accepts NO input at all.
  Do not waste more time on it. vgamepad.py gained combo/down/up commands
  (kept for future use). RA config left with input_driver=sdl2,
  input_joypad_driver=sdl2, menu combo=1 — harmless, game still boots/plays demos.
- NOTE: pad6 "Start exits demo to logo" was MISREAD — the logo/title appearances
  were natural attract-loop cycling, not input. No RA input was ever proven.

### Mednafen navigation — FULLY WORKS (the QA path)
- Mednafen wiped by VM replacement; reinstalled (apt). Xvfb :99 is the KoC2
  lane's (PCSX2) — DO NOT touch. Use :98 for mednafen. Launch with
  DISPLAY=:98 explicitly (forgot once: mednafen opened on a phantom 1024x768
  display, no window on :98). Boot is SLOW under load (title ~75-135s).
- Key remap (in ~/.mednafen/mednafen.cfg): circle=X(27), cross=Z(29),
  square=C(6), triangle=U(24). WASD = D-pad (up=W26, down=S22, left=A4,
  right=D7), start=Return(40). The numpad defaults (KP_6=circle etc.) do NOT
  register via xdotool — that's why lane 1's S/KP_6 failed. Use keydown +
  0.3s hold + keyup (emu.sh pattern); instant `key` does not register.
- FULL PATH PROVEN (JP disc, screenshots in work/nav2-*.png + nav4-*.png):
  Title -> Return -> Main menu (4 items: 開場/戦いの軌跡/ベストバウト/
  カードロード) -> X on 開場 -> Game menu (10 items) -> X on VS Computer ->
  Options (7 rows: 難易度/試合時間/引き分け/試合会場/リング/観戦席/
  スピーカー; W/S rows, A/D values, D changed 30分->35分) -> X -> Character
  select (12 names each side, P1 red when picked, P2 yellow) -> X (P1) ->
  S,S,X (P2) -> MATCH (Fujinami vs Mutoh, 00:00, nav4-vs2.png).
- Notes: X (Circle) is confirm; Start does NOT confirm in menus. Best Bout
  with no saved replays does nothing on confirm (not an input failure).
  Options screen wraps (7x Down = back to row 1). Character-select names are
  FULL names (藤波 辰爾) — rendered from the name sheet or T2 glyphs (TBD
  which; EN name sheet is already in the full-EN build).
- JP baseline screenshots: nav4-title3 (title), nav2-menu2/nav2-confirm2
  (main menu), nav2-kaijo/nav4-charsel (game menu), nav4-charsel2/nav4-optright
  (options), nav4-afterx/nav4-p1pick (char select), nav4-vs2 (match start).

### Next: build the EN T1 atlas
- Map all 65 JP rects -> NJPW-correct English (FAQ + atlas reading + the
  JP baseline screenshots above, which show exactly which rects appear where).
- Harvest US font glyphs from the US atlas (work/font-hunt/us-slot202.png),
  render EN text into each JP rect (same TIM header/palette as JP slot 202).
- Rebuild PAC_WRES slot 202 (BPE recompress; US slot 202 is SMALLER than JP,
  4636 vs 7388 B — update table offsets or pad to exact size; sequential-read
  rule applies). Also swap US T3 (slot 204, English staff lines).
- TEST IN MEDNAFEN FIRST (atlas-only build, no PAC_GAME_MES changes): if
  mednafen does NOT hang on PAC_WRES BPE changes, the EN menus are verifiable
  there. Then combine atlas + banners for the full build; verify banners in
  PCSX demos (already proven) + menus in mednafen (atlas-only build).

## 2026-11-20 — FULL ENGLISH v6 COMPLETE (M2 lane, DuckStation QA)

### EN T1 atlas built (tools/build_en_atlas.py)
- Font harvested from the US atlas, WORD-LEVEL with explicit x-ranges
  (gap-based grouping fails: word gaps 7-15px overlap the "!" gap 8px and
  paren gaps 7px). 47 glyphs; X, J, `.`, `#`, `/`, `l` drawn in matching
  style; L/M/W fixed via manual x-range harvest; "m" via manual harvest
  (y=192, x=227-236). JP-style red shadow (+1x, idx 2). OXO symbols were
  copied from JP at first — REMOVED in v6 (see below).
- TRUE T1 row layout (corrected from the JP atlas + US atlas):
  y=0 12/MAN GAUNTLET/BEST BOUTS; y=16 G1 CLIMAX/LEAGUE/OFF;
  y=32 G1 CLIMAX/TOURNAMENT/ON; y=48 IWGP CHAMPIONSHIP/START;
  y=64 RESULTS/LOAD/DRAWS; y=80 VS PLAYER 2/CEMENT/LEVEL;
  y=96 VS COMPUTER/(cont.); y=112 VIEW/DEMO MATCH/MONO;
  y=128 ring digits 1/2/3/#; y=144 NO LIMIT/OSAKA; y=160 VENUE/RING;
  y=176 RINGSIDE/SOUND; y=192 STEREO/STRONG/TIME/L/m;
  y=208 TOKYO A/TOKYO B/TRAINING; y=224 2nd FLOOR/4/1st/W vs/D;
  y=240 OUTDOOR/GO!/SPARRING/s.
- Options-screen rect model: the options screen does NOT use the 65-rect
  table at EXE 0x5B0F8 (only two rect tables exist in the EXE: 0x5B0F8
  with 65 rects and 0x5B308 with 17). It uses JP word-bounds rects
  (x = JP word start, w = JP word width in 16px kanji units), computed
  at runtime. The US EXE rect table is IDENTICAL to the JP one — Activision
  changed no rects; they positioned US words to fit the JP rects.
- Key positioning fixes (all proven in DuckStation): TIME at x=144 (the
  options label rect starts ~144; at 128 it showed only "ME"); RING at
  x=208 (label rect starts ~208; at 192 it showed only "NG"); TRAINING
  at x=180 spacing 1 (ends 251; x=192 overflowed past 256); CEMENT
  spacing 0 at x=128 (ends 176, stays out of game-menu rect 42);
  "MAN GAUNTLET" at x=28 spacing 0 (ends exactly 128, so the game menu
  shows "12 MAN GAUNTLET"); X glyph redrawn (8 wide, 2px diagonals —
  the first X read as "Y": "G1 CLIMAY"); I glyph redrawn (5px serif bar —
  the harvested ~3px I vanished at spacing 0: "TRANNG").

### EN T2 atlas (tools/build_en_t2.py, slot 203)
- T2 (256x128 TIM) holds digits 0-9, results headers, "( save enabled )",
  LOAD/SAVE FAILED, FORMATTING. US T2 verbatim except row y=48 re-rendered
  as "IWGP CHAMPS" (not "PPW CHAMPIONS" — this game is NJPW/IWGP).
- "IWGP CHAMPIONS" (145px, centered) clipped to "IWGP CHAMPIC" on the
  results menu; "IWGP CHAMPS" centered (117px, x=69-188) clipped to
  "IWGP CHAMP" — the results-menu rect's right edge is ~x=176. FIX:
  "IWGP CHAMPS" LEFT-ALIGNED at x=21 (matching the US rows' left edge),
  ends x=140, fully visible (v4).
- rebuild_wres.py replaces slots 202+203+204 (exact-size BPE, roundtrip
  verified). Slot 204 = US T3 staff lines verbatim (padded to JP size).

### Mednafen hang — concluded (do NOT re-investigate)
- Mednafen hangs on ANY PAC_WRES slot 202 change (atlas-only build boots
  to title, black after Start; JP disc reaches the menu fine). Staff TIMs
  are INNOCENT (staff-only build reaches the menu). The GENUINE US slot
  202 blob ALSO hangs (freezes on the zoomed title-transition screen).
  Same unsolved BPE hang mechanism as PAC_GAME_MES. Mednafen CANNOT verify
  the EN menus. DuckStation does NOT hang on any of these changes.

### DuckStation QA setup (2026-11-20)
- AppImage from github.com/stenzek/duckstation (latest, 91.5 MB) at
  ~/workspace/duckstation/; NO FUSE here — extract with --appimage-extract;
  binary squashfs-root/AppRun. BIOS scph1001.bin in
  ~/.local/share/duckstation/bios/. Launch: DISPLAY=:98 ./AppRun -batch
  <cue>. Boot is slow (title ~45-90s; Sony -> TOMY -> Yuke's -> title).
- Keys (Pad1): Start=Return, Cross=K, Circle=L, Square=J, Triangle=I,
  D-pad=arrows. Use keydown + 0.3-0.5s hold + keyup. Circle (L) is
  CONFIRM in menus; Cross (K) is BACK. First Return after a focus-click
  often fails — press twice. Click the game area to focus first; an open
  menu eats keypresses. Triangle (I) did NOT register in this setup
  (binding is correct in settings.ini — input flakiness, not the game).
  Attract demo starts ~3 min idle at the title; Start during it RESETS
  the game to the boot logos. pkill/pgrep MUST use the bracket trick
  ([A]ppRun) and the command must not contain the literal text — and
  pkill -f on AppRun is unreliable here; kill by PID (kill -9 $(pgrep
  -f 'AppRu[n]' | head -1)).
- NO CPU DEBUGGER in this DuckStation build (Tools menu has Memory
  Editor/Scanner, ISO Browser, Media Capture, Free Camera, Capture GPU
  Frame — no debugger). The options-screen split was diagnosed with a
  DIAGNOSTIC ATLAS instead (EN_ATLAS_DIAG=1 renders NJPW2/NJPW3 as
  ABCDE/FGHIJ).

### RING-row split + row-2 fragments (diagnosed + fixed)
- Diagnostic build (SHA-1 9b7ce427...) proved: the options RING row draws
  y=128 in 80px chunks, so any word straddling x=80 or x=160 splits:
  "ABCDE" -> "AB"+"CDE" (break x=80), "FGHIJ" -> "FGHI"+"J" (break x=160).
  In the real build: "NJ"+"PW2", "NJP"+"V3". FIX (v2): ring numbers as
  bare digits at the US positions ("1" x=37, "2" x=116, "3" x=198,
  "4" x=117 y=224) — single digits can't straddle; matches the US release.
- Row 2 "TIME LC 3 0 ES": "ES" was the tail of LOSSES (the minutes-unit
  rect at ~x=224 on y=192 showed LOSSES's last 2 letters); "LC" vanished
  with the same fix. FIX (v2): LOSSES dropped (as in the US release),
  "L" at x=209 and "m" at x=227 on y=192 (US positions) — the time now
  reads "3 0 m".
- SEATS-row red fragment (v2-v5): a small red glyph between RINGSIDE and
  2nd FLOOR. Red-pixel scan put it at screenshot x=387-397 = atlas
  x~125-131, y=176. Blanking "1st" (v5, SHA-1 00f2a495...) did NOT remove
  it ("1st" innocent, restored). Removing the OXO copy (v6) DID remove
  it — the fragment was the left edge of the JP ○×□ symbols (copied at
  y=176, x=112-176), caught by the wide RINGSIDE rect. OXO is now LEFT
  OUT of the atlas; no verified screen uses it. If a future screen needs
  ○×□, reposition them off y=176.

### Build history (Track 1 SHA-1s)
- v1 full+atlas 4eb38716... (atlas-only a0aab0a4..., diag 9b7ce427...)
- v2 b641a055... (digits RING row, L/m units, X/I redraws, positions)
- v3 8bfd45ee... ("IWGP CHAMPS" centered — STILL clipped to "IWGP CHAMP")
- v4 a6b9be21... ("IWGP CHAMPS" left-aligned x=21 — FIXED)
- v5 00f2a495... (test: "1st" blanked — fragment persisted, "1st" innocent)
- v6 07f08608fadab90b7998ab740e36d0f49a8390f2 (FINAL: OXO removed, "1st"
  restored, options screen 100% clean)

### v6 verification (DuckStation, all screenshots work/nav5-v6-*.png + nav5-v2/v4-*.png)
- Title, main menu (GO!/RESULTS/BEST BOUTS/LOAD), game menu (VS COMPUTER,
  VS PLAYER 2, 12 MAN GAUNTLET, IWGP CHAMPIONSHIP, G1 CLIMAX LEAGUE,
  G1 CLIMAX TOURNAMENT, DEMO MATCH), options (all 7 rows clean),
  char select (12 EN names both sides), VS screen (Fujinami vs Mutoh),
  match HUD (EN names + timer), demo HUD (EN), attract-demo HUD (EN),
  RESULTS menu (GAUNTLET RESULTS / IWGP CHAMPS / TOURNAMENT RESULTS),
  GAUNTLET RESULTS header, IWGP CHAMPS screen ("# 17  KEIJI MUTOH  W
  SHINYA HASHIMOTO  21m13s" — proves #, W vs, m, s, T2 digits all work),
  SAVE MATCH? (X = YES / Δ = NO), SAVING, DATA SAVED, BEST BOUTS
  (empty list, no text). Memory-card save works (DATA SAVED).
- NOT re-verified in v6: the staff-credits roll + The End (US TIMs in
  place; The End was verified in the hybrid build; the credits roll
  needs a championship win). Ring apron + event poster stay Japanese
  (NJPW branding, as in the US release — intentional).

### Delivery (2026-11-20 ~19:30 UTC, Oracle VM /home/ubuntu/toukon-english/)
- tr1-fullen-track1.bin = v6 (SHA-1 07f08608...), CUE test-fullen.cue.
- tr1-fullen.chd (372,039,105 B, SHA-1 1b8217e39f1104ff40d9b9546477fbd7c91d0e1e,
  Data SHA-1 d5a20ab676a24e1a4590d3ad8b26325518737f00) — full disc, 7
  tracks, 58:07, EN Track 1 + REAL audio tracks 2-7 (FLAC), chdman 0.264,
  verify passed (raw + overall). Built from the re-downloaded JP zip
  (SHA-1 a63d2bf8... verified); the archive.org file lives under a DOUBLED
  item path: .../2024-sony-playstation-jap-hearto-1g1r-collection/
  2024-sony-playstation-jap-hearto-1g1r-collection/Sony - Playstation -
  JAP/Shin Nihon Pro Wrestling - Toukon Retsuden (Japan).zip (the single
  path 404s). Zip is Zstd method 93 — 7z cannot extract it; used
  tools/zstd_unzip.py (pip install --user --break-system-packages
  zstandard on the VM). Intermediates deleted after the CHD verified.
  VM disk 12G free after delivery.
- Hybrid build kept as the HYBRID option (tr1-en-final-track1.bin,
  SHA-1 17050fec..., CUE testFINAL.cue). README updated on the VM.
- OPEN: PCSX ReARMed (the console's core) has NOT tested the full-EN
  build — test tr1-fullen.chd there before flipping the console card
  from coming_soon to playable. Mednafen is NOT usable for this build
  (hangs — see above).

## Console test prep (2026-11-20 ~14:40 EST, arcade lane)

Goal: test tr1-fullen.chd in PCSX ReARMed (the console's PS1 core) via the
live arcade, flip the Toukon card to playable if it runs.

### Findings
- Local arcade source ~/workspace/bannon-arcade-push/ is GONE (no such dir).
  Worked from the deployed site on the VM (/var/www/arcade) + the repo
  branch muse/wrestling-arcade via the GitHub API instead. Deployed
  games.json is byte-identical to the repo's (SHA-256 da4946e5..., blob
  9049f2e8, commit e37efffb) — no drift.
- play.html GATES on status: if game.status !== 'playable' it shows
  "not playable in a phone browser yet" and never creates the START button
  (the ?rom= override only works after the gate). So the live test REQUIRES
  the deployed card flipped first — the flip-then-test order is forced by
  the player, not a choice.
- CHD integrity: chdman verify PASSED on the VM (raw + overall SHA-1).
  NOTE on hashes: 1b8217e3... is the CHD's INTERNAL raw SHA-1 (chdman);
  the FILE-level SHA-1 is 6e2b31dc418a2f1134f93ebbc77603c8d6246390.
  games.json romSha1 uses the file hash (matches the tekken3 convention —
  verified: tekken3.chd file sha1sum == its romSha1 a47acb93...).
- Precedent: Tekken 3 + SF EX2 Plus CHDs already run in this console via
  the same psx core, so CHD loading through the WASM core is proven here.
  The Toukon-specific risk is the PAC_WRES slot-202 change that hangs
  Mednafen — PCSX ReARMed is a different core, DuckStation runs it fine.

### What was done (all verified)
- nginx (sites-available/arcade, backed up to arcade.bak-toukon): 4 new
  locations serving IN PLACE from /home/ubuntu/toukon-english/ (no copies):
  /roms/toukon-fullen.chd, /roms/toukon-hybrid.cue,
  /roms/tr1-en-final-track1.bin, /roms/dummy-audio/ (prefix). Headers mirror
  the /roms/ block. chmod o+r on dummy-audio/*.bin (were 660). nginx -t
  passed, reloaded. (First attempt dropped the closing brace — nginx -t
  caught it, restored from backup, redid correctly. Running config was
  never broken: the failed test blocked the reload.)
- Deployed games.json flipped (VM-only, PROVISIONAL test flip; backup at
  games.json.bak-toukon-test): toukon -> playable, core psx,
  rom roms/toukon-fullen.chd, romSha1 6e2b31dc..., romSize 372039105;
  toukon-hybrid card ADDED as coming_soon (staged, not yet tested in the
  console core). New file SHA-256 44c295eb...; byte-diff confirms only the
  Toukon entries changed. Repo branch UNCHANGED (still coming_soon).
- Serving verified (VM + external): CHD HEAD 200 / 372039105 /
  Accept-Ranges; ranged SHA head/mid/tail all MATCH the file; CUE served
  == file (SHA-256 05df453a...); BIN + dummy-audio 200 with correct
  lengths; live games.json shows toukon playable; arcade root 200;
  external ranged head hash matches (ccd45612...).

### Remaining: the live browser test (needs the parent — subagents have no browser)
- Test spec: ~/workspace/toukon-english/BROWSER-QUEUE.md
  (URL http://132.145.194.139/play.html?game=toukon; boot -> title EN ->
  menu EN -> VS COMPUTER -> char select -> match; check sound, controls,
  speed honestly; screenshots each step).
- On PASS: commit games.json.new to arcade/games.json on branch
  muse/wrestling-arcade (base blob 9049f2e8) via the GitHub API. No merges
  without Mars's visual confirmation.
- On FAIL: revert deployed games.json from games.json.bak-toukon-test;
  do NOT commit. Report exactly what screen/error at what step.
- Hybrid card still needs its own PCSX ReARMed test before ITS flip
  (needs a deployed status flip first — follow-up).
