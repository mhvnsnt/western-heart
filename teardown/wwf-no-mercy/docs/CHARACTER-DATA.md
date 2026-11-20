# WWF No Mercy — Character Data Tables (ROM-verified)

Source ROM: `WWF No Mercy (USA) (Rev-A).z64` (32,554,432 bytes, CRC32 `BACEEA13`).
All offsets are ROM file offsets. Analysis script: `../tools/analyze_nomercy.py`
(re-runnable; regenerates `wrestler-id-table.json`).

## 1. Wrestler display-name / internal-ID table — `0x168D930`

Format: 2 pad bytes (`00 00`), 1 count byte (`0x2A` = 42 entries), then per entry:
`u8 wrestler_id` + null-terminated ASCII name. Table is alphabetical by name;
IDs are NOT sequential — gaps at 5 and 37 (hidden/unused roster slots).

Full mapping (also in `wrestler-id-table.json`):

| ID | Name | ID | Name | ID | Name |
|----|------|----|------|----|------|
| 0 | None | 15 | EDGE | 29 | ROCK |
| 1 | ACOLYTES | 16 | RIOS | 30 | SHAMROCK |
| 2 | AL | 17 | GODFATHER | 31 | TAKA |
| 3 | ANGLE | 18 | HARDY BOYZ | 32 | TAZZ |
| 4 | AUSTIN | 19 | HBK | 33 | TOO COOL |
| 6 | BLACKMAN | 20 | HHH | 34 | VENIS |
| 7 | BOSS MAN | 21 | HOLLYS | 35 | VISCERA |
| 8 | BULLDOG | 22 | JERICHO | 36 | X-PAC |
| 9 | CACTUS | 23 | KANE | 38 | UNDERTAKER |
| 10 | CHYNA | 24 | MANKIND | 39 | BENOIT |
| 11 | CORPORATE | 25 | HENRY | 40 | T&A |
| 12 | D'LO | 26 | MR. ASS | 41 | GUERRERO |
| 13 | DUDLEY BOYZ | 27 | N.A.O. | 42 | SATURN |
| 14 | DX | 28 | MALENKO | 43 | RICHARDS |

**Western Heart use:** these IDs are what move-slot assignments, AI tables, and
save files reference. Any system that assigns moves/attires per wrestler keys on
this ID, not the name.

## 2. Data segment — `0x13E000` (mixed tables, `FF FF FF FF`-separated)

Not a single "move slot table" — it is a data segment of several tables:

- `0x13E008`–`0x13E0BC`: 8 records, each = list of small u32 values. First value
  of each record increments (0x0B, 0x0C, 0x0D, 0x0E, 0x0F, 0x17, 0x13, 0x14…),
  i.e. **record = [move_id, attr…]**. Plausibly move attribute/parameter lists.
- `0x13E0D0` (340 B): mixed flag/ID words (`FFFFFFEC`, `FFFFFFDF` sentinels).
- `0x13E2BC` (468 B): **float table** — e.g. `42B00000` (88.0), `42C80000`
  (100.0). Plausibly hitbox extents or animation key values.
- `0x13E4A0` (44 B): **RAM pointer table** — `0x8014CD5C`, `0x8014CD50`, …
  (N64 KSEG0 cached addresses, 8-byte stride). Points at runtime data
  (animation or display-list data); ROM-file equivalents need overlay mapping.
- `0x13E4D4` (15,148 B): **sequential u16 index run** `0x324D, 0x324E, …`
  (~7,500 indices). Plausibly a triangle-index buffer or move-index remap.

**Open:** float-table semantics, pointer→ROM-offset resolution (needs the
recomp project's overlay map), u16 run purpose.

## 3. Adjacent name tables (partially decoded)

- `0x168D8B4`: ~20-entry table (ROCK, SATURN, SHAMROCK, T&A, TAKA, TAZZ,
  TOO COOL, VENIS, VISCERA, X-PAC, ORIGINAL 1, then IDs 52–57 with coded text).
  Entries carry embedded control bytes (`FF`, `BF`, `DF`, `0x15`) — likely the
  AKI text engine's style/line codes. Probably entrance/theme or preset names.
- `0x168D885`: entry = `u8 id` + optional `FF` + name (may itself contain `FF`)
  + `00`. ~21 entries: ROCK, AUSTIN, UNDERTAKER, KANE, MANKIND, CACTUS, HBK,
  HHH, X-PAC, MR. ASS, ROAD DOGG, BENOIT, MALENKO, SATURN, GUERRERO, JERICHO,
  ANGLE, TAZZ, TEST, GODFATHER, D'LO… Probably create-a-wrestler default
  presets. `FF` semantics TBD (candidate: line-break or case-shift code in the
  AKI text engine — mid-word splits observed, so not confirmed).
- `0x168DD89`+: creation-suite part strings — body types (Male Skinny / Medium
  / Thick / Fat), face presets (Austin, HBK, Rikishi…), hair, accessories,
  attire pieces. Full parse pending.

## 4. Retargeting notes (for Western Heart / Tekken animation work)

- Wrestler animation data has NOT yet been isolated to extractable clips; the
  pointer table at `0x13E4A0` is the lead for locating it.
- The `recomp/` project (Gadge64/WWFNoMercyRecomp) has labeled symbols that
  can resolve these ROM offsets to functions — next step is cross-referencing
  `recomp/syms/` against the offsets above.
- No Mercy character models are reserved for the wrestling-game lane (Bannon /
  wrestling game six); Western Heart takes ANIMATIONS + SYSTEMS only.
