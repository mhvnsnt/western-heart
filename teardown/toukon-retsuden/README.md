# Toukon Retsuden — English Version (TR1)

**Shin Nihon Pro Wrestling — Toukon Retsuden** (PS1, Yuke's, 1995, Japan-only).
Game ID SLPS-00084. No English patch exists anywhere — this lane builds it ourselves.

## Status (2026-11-20)

**PARTIAL PATCH DELIVERED AND QA-PASSED.** The full 100% English version is blocked
by two uncracked problems (documented below). What works is proven in-game.

### What works (QA-passed, boots to main menu, no hang)
- **Wrestler names (16)** — English in full-width Latin Shift-JIS in the EXE,
  same method Activision used for the US version (Power Move Pro Wrestling).
  Names: Fujinami, Chosyu, Mutoh, Chono, Hashimoto, Hase, Sasaki, Koshinaka,
  Thunder Lyger, Tenzan, Kanemoto, Norton, Great Muta, Warrior, Tanaka, Hattori.
  Verified in RAM (Fujinami/Chono/Hashimoto at 0x80010514+); JP names gone.
- **"The End" screen** — US TIM_END swapped in (same size, 8,256 B). Proven safe.

### What is blocked
1. **BPE banners + name sheet (14 banners + 16-name graphic).** The in-match
   banners and the VS-screen name sheet are BPE-compressed TIMs in PAC_GAME_MES.
   English replacements were built (from the US version's official banners +
   a redrawn name sheet) but the game HANGS on any substantially-changed BPE
   block data — even when the decompressed TIM is byte-identical to the
   original (test BQ). The game's MIPS BPE decoder was emulated (Unicorn) and
   provably produces correct output for the hanging data, so the hang is
   post-decompression, mechanism unknown after 70+ tests, full disassembly,
   and save-state forensics. See WORKLOG.md "BPE HANG: PARKED".
2. **Menu strings.** Main menu (開場, 戦いの軌跡, ベストバウト, カードロード)
   and all other menu text is NOT stored as Shift-JIS (or EUC/JIS/UTF-16)
   anywhere on the disc. Likely glyph indices or another encoding. The text
   renderer and the small kanji font were not found. See WORKLOG.md "MENU
   STRINGS: PARKED".

### What is still Japanese
- Menus, in-match banners (WINNER, TIME-UP DRAW, GIVE UP, etc.), VS-screen
  name sheet, staff credits (TIM_STAFF 1–4), title logo (kept intentionally —
  it already says "TOUKON RETSUDEN" in English).

## Files

- `tools/` — pure-Python PS1/BPE toolchain (no game data):
  - `psx_iso.py` — PS1 BIN/CUE reader (ISO9660 extract).
  - `dpac.py` — Yuke's DPAC archive parser/extractor.
  - `bpe.py` — BPE decompressor (GROOVE multi-block).
  - `bpe_compress.py` — BPE compressor (Gage byte-pair encoder) + dummy-block
    padding for exact-length sections. NOTE: its dictionaries hang the game
    on changed data; see `yukes_encode.py`.
  - `yukes_encode.py` — re-encode a TIM with Yuke's ORIGINAL dictionaries
    (byte-identical) + DP shortest-path block data.
  - `emu_bpe.py` — Unicorn MIPS emulator for the game's BPE decoder
    (0x80048a20). Proves the decoder is correct.
  - `tim2png.py` — PS1 TIM → PNG renderer.
  - `exe_names.py` — patch EXE wrestler names (full-width Latin).
  - `name_sheet.py` — build the English name sheet TIM.
  - `ringout_banner.py` — build the "Ring Out!" banner TIM.
  - `rebuild_gamemes.py` — rebuild PAC_GAME_MES (in-place, exact lengths).
  - `rebuild_dpac.py` — rebuild DTPAC.PAC (sector-preserving).
  - `patch_iso.py` — patch the disc image in place.
  - `build_all.py` — end-to-end pipeline (needs JP + US disc images).
  - `sjis_strings.py`, `zstd_unzip.py` — helpers.
- `docs/faq-wbaker.txt` — WBaker's GameFAQs FAQ (menu/move reference).
- `WORKLOG.md` — full session log (616 lines): survey, all 70+ hang tests,
  disassembly findings, blockers.

## Build (final patch: names + "The End")

Input: original TR1 Track 1 BIN + US Power Move TIM_END.
Output: patched Track 1 BIN (SHA-1 `17050fec804b94661892ae35cece7ae167d1f952`).

```bash
python3 tools/exe_names.py            # -> work/SLPS_000.84.en
# DTPAC: original + US TIM_END at sector 199 (see WORKLOG 2026-11-20 final patch)
python3 tools/patch_iso.py            # patches EXE (LBA 24) + DTPAC (LBA 229)
```

## Sources (no game data in this repo)

- TR1 (Japan): archive.org `2024-sony-playstation-jap-hearto-1g1r-collection`,
  SHA-1 `a63d2bf861cb5b3f60fc54df7e50a116b8ee8260`.
- Power Move Pro Wrestling (USA): archive.org `psx_pmpwrest`,
  SHA-1 `bb9639d052365a9e31e06afcb07e2f176032107c`.
- Game files live on the Oracle VM under `/home/ubuntu/toukon-english/`
  (never in a repo).

## Next steps for a future lane

1. **BPE hang:** run the loader (0x800187DC) under Unicorn with mocked
   malloc/GPU to find where it diverges on DP block data; or test the
   BQ disc in PCSX ReARMed (the console's core) — the hang may be
   mednafen-specific.
2. **Menu strings:** find the text renderer via dynamic tracing (mednafen
   debugger or a full-system MIPS emulator); the renderer reveals the font
   and the string encoding.
3. **CHD:** re-download the TR1 zip for the real audio tracks (local copies
   were deleted for quota), then `chdman createcd` on the Oracle VM.
