# WWF No Mercy — CAW / edit_data tables (ROM-verified)

Source ROM: `WWF No Mercy (USA) (Rev-A).z64` (32,554,432 bytes, CRC32 `BACEEA13`).
Parser: `../tools/caw_parse.py` (regenerates `caw-name-table.json`,
`caw-categories.json`). All offsets are ROM file offsets.

## 1. Entrance-music track table — `0x168D790` (corrects earlier `0x168D885` note)

50 entries, format `[u8 music_id][coded track title]00`. Entries run in the
same alphabetical order as the wrestler table (`0x168D930`), then extra
non-wrestler tracks. This is the table a created wrestler's entrance-music
choice indexes into.

Verified entries (music_id → title, codes stripped):

| ID | Title | ID | Title | ID | Title |
|----|-------|----|-------|----|-------|
| 0x26 | ACOLYTES | 0x03 | N.A.O. | 0x04 | SHAMROCK (+T&A, see open) |
| 0x08 | AL | 0x13 | RAW | 0x20 | TAKA |
| 0x2D | ANGLE | 0x22 | REAL AMERICAN! | 0x21 | TAZZ |
| 0x24 | AUSTIN | 0x1B | RIOS | 0x28 | TOO COOL |
| 0x2F | BENOIT | 0x25 | ROCK | 0x05 | VENIS |
| 0x0A | BLACKMAN | 0x32 | SATURN | 0x1A | VISCERA |
| 0x09 | BOSS / BULLDOG (see open) | 0x20 | TAKA | 0x06 | X-PAC |
| 0x29 | CACTUS | 0x33 | ORIGINAL 1 | 0x34–0x39 | ORIGINAL 2–7 |
| 0x1C | CHYNA | 0x0C | CORPORATE | 0x0D | D'LO |
| 0x18 | DUDLEY BOYZ | 0x0E | DX | 0x0F | EDGE |
| 0x10 | GODFATHER | 0x31 | GUERRERO | 0x11 | HENRY |
| 0x23 | HHH | 0x16 | HOLLYS | 0x2C | JERICHO |
| 0x01 | KANE | 0x1E | MALENKO | 0x14 | MR. ASS |

- `ORIGINAL 1`–`ORIGINAL 7` = music_ids `0x33`–`0x39` (51–57): the CAW
  "original theme" slots. (Earlier note said "IDs 52–57" — full run is 51–57.)
- `RAW` (`0x13`) and `REAL AMERICAN!` (`0x22`) are show/Hogan tracks, proving
  this table is music, not wrestler names.
- Track titles carry the same inline text codes as the part strings (§3).

**Open:** a few entries don't segment cleanly as `[id][title]00` and need the
text engine to resolve: the `FF`-prefixed ids (ACOLYTES, EDGE, D'LO, GUERRERO,
MALENKO, MR. ASS, TOO COOL), the `DD`-prefixed ORIGINAL 3/5, the
`0x168D877`–`0x168D87A` `27 20 00 4B IND 00` region (sits where MANKIND's theme
should be), the `0x168D8A5` `F9…` / `0x168D8AB` `53…` placeholder entries, the
`0x168D838` HARDY entry, the `0x168D7CF` BOSS/BULLDOG double-name entry, and
the `0x168D8C4` SHAMROCK entry's extra `0` + `T&A` bytes. Raw forms are all in
`caw-name-table.json`.

## 2. Creation-suite part-string regions — `0x168DD89`+

Category regions (boundaries by inspection; full string runs in
`caw-categories.json`):

| Region | Contents |
|--------|----------|
| `0x168DD89`–`0x168DE5D` | Body types: Male, Skinny 1, Medium, Thick, Fat, Austin, HBK, Rikishi, Rock, Hairy … Female, Chyna, Fit, Grannie, Jackie … |
| `0x168DE5D`–`0x168DEB4` | Elbow pads: None, Angle, Elbow Brace, Hardyz 1, Hardyz 2, Pad, People's Elbow, Supporter |
| `0x168DEB4`–`0x168DF05` | Masks/Etc set 1 + accessories |
| `0x168DF05`–`0x168E038` | Entrance attire (accessories / hats / costumes) |
| `0x168E038`–`0x168E2E6` | Gloves |
| `0x168E2E6`–`0x168E4D5` | Feet (boots / pads / pull-ons / athletic) |
| `0x168E4D5`–`0x168E586` | Wrist bands |
| `0x168E586`–`0x168E696` | Hair (Bald, Shaved, Short 1-3, Middle 1-4, Long 1-3, Afro, Braided, Cleancut, Curly Hair, Dreads, Mohawk 1-2, Ponytail 1-2, Shocked) |
| `0x168E696`–`0x168E86F` | Front hair (mostly binary records — generated "Front Hair N" names) |
| `0x168E86F`–`0x168E877` | Facial hair |
| `0x168E877`–`0x168E8D1` | Hats / caps |
| `0x168E8D1`–`0x168E9D7` | Knee pads |
| `0x168E9D7`–`0x168EA6A` | Masks |
| `0x168EA6A`–`0x168EB20` | Accessories |
| `0x168EB20`–`0x168F800` | Ring attire (short / long / wrestling / pants / full-body) |

Record shape (best current model, verified on hair + elbow-pad sections):

    [u8 part_id][display name + inline codes][attr bytes][terminator]

- Terminator is `00` for bare/category records, or a 2-byte code for items:
  `FD F0` (hair: Short 1-3, Afro, Cleancut, Curly Hair, Dreads),
  `FB F0` (elbow pads: Hardyz 1/2, Pad, People's Elbow, Supporter;
  gloves; masks), `FA F1` (elbow: Angle, Elbow Brace), `F1 F1`, `FE…`.
- Between records sit 1–4 attribute bytes (e.g. hair `Short 1` →
  `03 0B 03` before `Short 2`; `05` before `Middle`; `10 02` before numbered
  variants). Semantics TBD — plausibly color-mask / body-fit / front-hair-
  pairing flags.
- Front-hair entries (`0x168E696`+) are near-pure binary records of the form
  `[u8 id][2–3 code bytes][u8 a][u8 b]00` — the "Front Hair N" names are
  generated, not stored.

**Western Heart use:** part_ids are the values a CAW save record stores per
slot; music_ids (§1) are what its entrance-music field stores. A No Mercy
save-file dump (from an emulator) is still needed to fix the exact byte
offsets of the save record — the ROM side here gives you every id→name
mapping the save references.

## 3. Inline text-engine codes (semantics — two classes, 2026-10-13)

Every name/title string in §1–§2 contains inline single-byte codes. They are
**not one thing** — measured evidence shows two semantic classes:

**Class A — zero-width codes (verified).** Deleting them yields clean English,
verified word-for-word against the community option lists
(`re-docs/docs/ui/menus/edit-a-superstar.md`): `BLA<FF>CKMAN`→BLACKMAN,
`AN<FF>GLE`→ANGLE, `<FF>ACOLYTES<FF>`→ACOLYTES, `JERICH<FF>O`→JERICHO,
`Skinn<7F>y 1`→Skinny 1, `Middl<25>e`→Middle, `E<FF>lbow Bra<FD>c`→Elbow
Brace, `Bo<BF>ss Man`→Boss Man, `D<F7>-Vo…`→D-Von…, `ORIGIN<DF>AL 1`→ORIGINAL
1. `FF` (47× in clean strings) occurs between 20+ distinct letter pairs —
**not kerning-pair-specific**, not Shift-JIS (illegal byte), not positional.
Likely style/placeholder bytes emitted by AKI's text tools. Other verified
zero-width: `EF 01 19 7F DF F7 FB BF`.

**Class B — dictionary-expansion tokens (verified ×2).** These EXPAND to
text; deleting them truncates the name:
- `REAL AM<AA><01>!` → **"REAL AMERICAN!"**: `AA 01` expands to `"ERICAN"`
  (ROM `0x168D899`: `52 3F 45 41 4C 20 41 4D AA 01 21 00`).
- `Buh <1C>` → **"Buh Buh"**: `1C` expands to `"Buh"` (ROM `0x168DEEA`;
  matches the community "Buh Buh" option).
The dictionary itself is not yet located (candidates: a token table near the
text banks; NOT the GlobalText bank at `0x703B0`, which uses vram pointers).
Single-byte tokens `01`–`1F` are usually zero-width, so the expansion
trigger is token-specific, not range-based.

**Traps:** (1) bytes that look like text codes in the music table are
usually the `music_id` byte (`<1C>CHYNA`, `<1E>FAAROOQ`, `<1D>JEFF` =
ids 0x1C/0x1E/0x1D, not tokens); (2) literal `0x3F '?'` in the
"R?EAL AM" title (single occurrence, ROM `0x168D89A`) — possibly an AKI
typo; (3) multi-byte sequences (`FD F0`, `FB F0`, `FA F1`, `F8 F0`) are
record terminators/attributes (§2), not text codes.

**Open:** full per-code table (needs the AKI text renderer or the
dictionary); `AA` escape semantics (dict-index byte follows?).

## 4. edit_data save-format status

ROM-side reference tables (music ids, part ids, wrestler ids) are now
documented. The live save-record byte layout (created-wrestler struct in
EEPROM/Controller Pak) is NOT yet decoded — it requires a real save file.
Recommended next step: generate a save in an emulator with a known CAW
(e.g. all parts = first option, music = ORIGINAL 1) and diff against these
id tables.
