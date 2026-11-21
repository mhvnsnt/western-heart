# VPW2 English — Completion

Finishes the Virtual Pro Wrestling 2 (N64, AKI, Japan-only) English
translation on top of the Beta 3 fan translation (S.K. Stylez /
AKIClub64). Beta 3 covered menus, create-a-wrestler, names, the Royal
Road Succession main screen, post-match comments, most move names, and
mic appeals — but left the **help screens**, most of **Royal Road
Succession** (career mode text), the **credits**, and a set of move
names in Japanese. This completes all of it: **634 translated strings
across 16 text files**, built into a patched ROM.

**No ROM is stored in this repo, ever.** The build takes the Beta 3
ROM as its base (source: archive.org item `n64patchedwrestlingroms`)
and produces the patched ROM locally. The patched ROM lives server-side
only.

## What was translated (634 strings)

| File | Content | Strings |
|------|---------|---------|
| 000A | Options Help (32 rule/option help screens) | 32 |
| 000B | Edit Parameters Help | 28 |
| 0009 | Edit Mode item descriptions | 21 |
| 0008 | Mode/menu descriptions + Controller Pak help | 29 |
| 000D | Royal Road Succession bulletin board (notices + fan gossip) | 82 |
| 000E | Credits roll (romanizations verified against MobyGames) | 87 |
| 000C | Misc UI + league tie-breakers + Controller Pak fragments | 20 |
| 0005 | Edit Mode strings (incl. 2 Beta 3 mistranslation fixes) | 13 |
| 0063–0067 | Move names (reactions/counters/guards) | 308 |
| 0068 | Move types | 7 |
| 0069 | Finish move names | 4 |
| 006A | Costume names (T-Shirts) | 3 |

Also fixed two Beta 3 mistranslations: 0005[370] パワー "Wrestling" →
"Power", 0005[371] 技巧 "Shoot Wrestling" → "Technique".

## Still Japanese (intentional, 40 strings)

- 0005[403–420]: the kana input-keyboard rows — they ARE the character
  picker; translating them would break text entry.
- 000C[188–209]: "Tokyo・" city prefixes — Beta 3 kept the ・ separator
  and so do we.

Everything else in all 19 AkiText files is English. (Curly quotes ’ “ ”
and U+3000 ideographic-space indentation in English text are Beta 3's
own style, kept as-is.)

## How to build

```sh
# 1. Place the Beta 3 ROM here, named exactly:
#    Virtual Pro Wrestling 2 - Oudou Keishou (Japan)(English Patch).z64
#    SHA-1 967e5239ca44fff2271d0971d9300f27f75560ee, 33,554,432 bytes.
# 2. Compile the LZSS tool:
gcc -O2 -o tools/aki_lzss tools/aki_lzss.c
# 3. Build + verify:
python3 tools/build_patched.py
python3 tools/verify_patched.py
```

Expected output: `vpw2-english-complete.z64`, 33,554,432 bytes,
SHA-1 `303c699157e8489c7f9eae47503f2b7427113606`.

## Method (the short version)

- **AkiText format**: `[N × u16be offsets][NUL-terminated Shift_JIS
  strings]`. Strings are looked up by table index, so the table size
  and every slot's position must be preserved. Offset 0 = unused slot.
  `tools/akitext_py.py` is the index-preserving parser/builder
  (round-trips all 19 clean files byte-identically, modulo one
  trailing pad NUL in 006C). Do NOT derive N from offsets[0] — Beta 3's
  builder points empty strings at EOF, which breaks that rule.
- **Build mirrors Beta 3's own rebuild**: Beta 3 rebuilt the 106 files
  in IDs 0x0005–0x006E and preserved that group's stored total exactly
  (219,458 bytes), so every file after the group kept its original
  offset. We do the same — the 16 rebuilt files shrink the group by
  1,450 bytes and file 006A (LZSS) absorbs the slack as trailing zeros
  after its stream (both decoders stop at the stream's end marker and
  ignore trailing zeros — verified). Only 98 file-table entries change,
  all within 0x0005–0x006A. The data region cannot grow past the fixed
  file table at 0x1310F40.
- **Dedup**: the builder shares identical strings AND suffixes, like
  Beta 3's builder (e.g. "Tenzan" points inside "Hiroyoshi Tenzan").
- **0068 cleanup**: the clean file's 40 degenerate table slots (offsets
  pointing inside the table / out of range — the game never reads them)
  are rebuilt as 0, matching the clean ROM. Beta 3's builder mis-packed
  offset-table bytes as garbage strings at those slots; they are gone
  in this build. The 40 indices are embedded in `build_patched.py`.
- **Verification** (`tools/verify_patched.py`): all 634 translations
  present; the patched ROM differs from Beta 3 ONLY in the translated
  strings (+ file-table updates + the 006A padding); untouched files
  (0006, 0007, 006C) byte-identical; file table sane; ROM diff is 200
  changed 1 KB blocks, all inside the rebuilt group span + file table.

## Files

- `tools/build_patched.py` — the build (Beta 3 ROM + translations →
  patched ROM).
- `tools/verify_patched.py` — structural verification of the patched ROM.
- `tools/validate_translations.py` — validates the translation tables
  (line length ≤ 55, @/$/% codes preserved, ASCII except U+3000).
- `tools/akitext_py.py` — AkiText parser/builder.
- `tools/lzss.py` — Python AKI LZSS decoder (from the VPW2 decomp).
- `tools/aki_lzss.c`, `tools/akitext.c` — C LZSS encoder/decoder and
  AkiText tool (from the VPW2 decomp tools).
- `tools/survey_beta3.py`, `tools/dump_still_jp.py` — survey helpers
  that mapped what Beta 3 left in Japanese.
- `tools/gen_move_translations.py` — generated the move-name tables
  (0063–006A) from JP→English maps.
- `translations/*.json` — the translation tables (index → English text).
- `WORKLOG.md` — full work log, including terminology decisions and
  references (GameFAQs IceMaster guide, MobyGames credits).

## Status

Built and structurally verified 2026-11-19. Boot-testing in the
browser emulator is done separately (by the console lane) — this build
has not been boot-tested here.

---

## VM sweep note (2026-11-21)

- `vpw2-english-complete.z64` (33,554,432 B) - the complete English-patched
  N64 ROM, landed by VM sweep Lane B.
  SHA-1 `303c699157e8489c7f9eae47503f2b7427113606`, header `80 37 12 40`.

The `.zip` that sat next to this ROM on the VM (25,954,991 B, SHA-1
`3b90d3e03649e9159326390bcb804dcf2fcdd6dd`) held only this `.z64` and was
deleted as redundant - this file is its full contents.
