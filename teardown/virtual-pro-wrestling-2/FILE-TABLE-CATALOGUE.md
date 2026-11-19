# Virtual Pro Wrestling 2 — Full-ROM Catalogue

AKI Corporation, Nintendo 64, 2000, Japan-only. The game AJ Styles calls
the best wrestling game ever; Cagematch rates it #1 of all wrestling games
(9.75). Same AKI engine as WWF No Mercy / WrestleMania 2000 — the No Mercy
lane's methods transfer directly, and this pull reuses them.

Extracted 2026-11-19 by Lane D (Mars's priority-1 instruction: pull
literally everything, decode/decrypt whatever it takes). The ROM itself is
never committed to any repo — extracted files and data only.

## Source ROM (FETCH-VERIFIED)

- File: `Virtual Pro Wrestling 2 - Oudou Keishou (Japan).z64`
- Size: 33,554,432 bytes
- SHA1: `82dd25a044689eab57ab362fe10c0da6388c217a` (matches
  AKI-Club/vpw2 `vpw2.sha1` exactly)
- SHA256: `358e9a345438155c6bd57da4bbf0f7a9fa1b4f7d5b1b726e8076c38f0f987e52`
- Source: archive.org item `virtual-pro-wrestling-2-freem-edition-20210128`,
  file `Virtual Pro Wrestling 2 - Oudou Keishou (Japan).zip` (25,952,680 B)

## ROM layout (measured, cross-checked 3 ways)

| Item | Offset | Notes |
|---|---|---|
| File table | `0x1310F40` | 13,091 u32be entries (13,090 files + end sentinel) |
| File data base | `0x152DF0` | First file starts here |
| File IDs | 1-based | Low bit of each table entry = LZSS-encoded flag |
| File data size | `0x11BE150` | Last table entry = end sentinel = size exactly |

Offsets agree across VPWStudio `DefaultGameData.cs` (VPW2_NTSC_J),
VPWStudio `LocationFiles/NA2J.txt`, and AKI-Club/vpw2
`extract_baserom.sh`. 3,668 files are LZSS-encoded; 0 animations are.

**The 0-based trap (proven, not assumed):** the No Mercy lane found the
repos' models/textures were 0-based — every file labeled N held game file
N+1. This pull uses the corrected 1-based decode throughout, verified by
`tools/vpw2_verify.py` (ALL CHECKS PASSED): 1-based type verification
passes 8,872/8,872; 0-based reads fail 36 type checks at type boundaries
and 5/5 sampled files are provably shifted (0-based fid N == 1-based fid
N+1). The Emerald Flowsion clips decode smooth (max per-frame joint step
~2,050, mean ~45–62), not the 74–109°/frame garbage a wrong decode gives.

## Census: 13,090 files, 21,895,527 decoded bytes, 13,090/13,090 verified

| Type | Files | Decoded bytes |
|---|---|---|
| AkiAnimation | 6,291 | 15,048,564 |
| AkiModel | 2,470 | 687,836 |
| Ci4Texture | 1,543 | 2,533,612 |
| Ci4Palette | 1,431 | 78,240 |
| Binary | 549 | 1,008,763 |
| Ci8Texture | 376 | 726,976 |
| I4Texture | 116 | 238,592 |
| Ci8Palette | 116 | 59,392 |
| AkiTexture | 111 | 389,232 |
| AkiArchive | 56 | 679,368 |
| AkiText | 19 | 123,441 |
| MenuBackground | 8 | 7,936 |
| AkiLargeFont | 1 | 215,163 |
| AkiSmallFont | 1 | 91,392 |
| AkiFontChars | 1 | 6,508 |
| RawCi4TexPal | 1 | 512 |

Full per-file table: `file-table.csv`. Census summary: `census.json`.

Gotcha found during the census: the Asmik LZSS decoder misfires on
animation files (the Toki2 header starts `00 00 00 xx`, which looks like
an LZSS marker) — only LZSS-decode when the file-table encoded bit is set.

## 1. Animations (`animations/`, 6,291 NPY clips)

Same 26-joint AKI system as No Mercy: `4 + N*98` byte clips, int16
`(nframes, 26, 3)`. FirstAnimationFileID `0x1A90`, FirstMoveAnimationID
`0x2056`. AnimID = file_id − 0x2056.

- 1,478 system animations (0x1A90–0x2055): locomotion, idles, taunts.
- 4,813 move animations (0x2056–0x3322), 4,079 named in the VPWStudio DB
  labels across 102 categories (Front Strong Grapple 514, Combo Strike
  414, Front Special Grapple 306, ...).
- `moveset/move_anim_map.json` + `.csv`: every animation with category,
  move name, AnimID, and Toki1 timing joined. Emerald Flowsion (Misawa's
  finisher) = AnimID 1740/1741.

## 2. Models (`models/`, 2,470 OBJs + .vc sidecars, 0 unparseable)

Organized by part: `face/`, `head/`, `neck/` (120 variants each — 5 head
shapes × 12 hair variants × 2 body-type groups), `mask_face/` (24),
`mask_sides/` (41), `mask_neck/` (12), hands, ring attire, arena, weapons.
1,589 body-part models are unlabeled in the DB (torso/limbs/hair) — all
extracted; the per-wrestler selection table lives in game code VPWStudio
does not document (see §9).

## 3. Textures (`textures/`, 2,146 PNGs, 0 skipped)

CI4/CI8/I4 + AkiTexture decoded with palettes. Includes face textures,
attire textures, UI, and arena textures.

## 4. Text (`text/`, 5,848 strings, UTF-8 JSON)

19 AkiText files decoded with `akitext` (AKI-Club/vpw2 tools) and
re-decoded from Shift_JIS to UTF-8. File 0x006C holds the default strings:
wrestler names (full + short pairs), stable names, arena names, mic-appeal
lines. 0x006A holds the 714 edit-mode costume option names (in enum order
— used to resolve costume fields). 0x0063–0x0066 hold 512 strings each.

## 5. Archives + arenas (`archives/`, `arenas/`, `arena-textures/`)

56 AkiArchives, 947 entries. Arena format cracked in this pull: arena
"Models" archives are alternating index/vertex buffer pairs in EITHER
order; index buffers are (u8,u8,u8,0x00) triangle quads with an optional
`FF FF FF FF` terminator; vertex buffers are F3DEX2 16-byte vertices.
9 arena/stage OBJs assembled: Budokan, Tokyo Dome, AKI Hall, Stadium,
Dome Road Stage, Checks and Trophy, VPW2 Stage (Game Intro), Locker Room
(Game Intro), Locker Room (Match Intro). 230 archive textures decoded to
PNG. UVs are emitted in texel space (u/32, v/32) — per-piece texture
assignment lives in game code. 4 unpaired vertex buffers in archive 00A1
(Checks and Trophy) are kept as point groups: no index buffer exists in
the archive, so their topology is implicit in game code.

Also in archives: lightning (22 AkiTextures + 41 blank 0xFF entries),
referee frames (32B palette + 5 raw CI4 128×128 frames), pyro (152 raw
I4 64×64 grayscale frames, inferred).

## 6. Menu backgrounds (`menubg/`, 8 PNGs, 320×240)

Main Menu, Event, Secondary/Blue, Royal Road Succession, Edit Mode,
Options, Pre-Match, Post-Match — via `menubg` (AKI-Club/vpw2 tools,
`-t new`). Pre-Match and Post-Match are byte-identical images.

## 7. Sound (`sound/`, 516 WAVs, 1,008.2 s)

8 N64 PtrTablesV2 banks (offsets from AKI-Club/vpw2 `extract_baserom.sh`,
confirmed by VPWStudio `soundtool.txt`). VADPCM decode ported from the No
Mercy lane's `full_pass.py` (itself a port of SubDrag's N64SoundLibrary).
Waves are 22,050 Hz mono s16.

| Bank | Slots | WAVs | Seconds |
|---|---|---|---|
| bank1 | 46 | 46 | 90.2 |
| bank2 | 119 | 119 | 93.0 |
| bank3 (music) | 10 | 10 | 605.0 |
| bank4 | 92 | 92 | 36.4 |
| bank5 | 87 | 87 | 103.1 |
| bank6 | 36 | 36 | 23.1 |
| bank7 | 63 | 63 | 24.1 |
| bank8 | 63 | 63 | 33.3 |

0 empty slots, 0 missing predictor books. Raw ptr/wbk/tbl blobs kept in
`sound/` (23 files, 13 MB) — table 8 has no .tbl blob. The .tbl blobs'
role is not decoded. 19 music sequences (files 0x034C–0x035E) dumped raw
as `.sng`; Sng→MIDI needs SubDrag's N64MidiTool (Windows GUI) — same gap
as the No Mercy lane.

## 8. Roster, stables, costumes, moveset data

- `roster/roster.json`: 130 wrestler definitions @ ROM `0x3FBE4`
  (VPWStudio `WrestlerDefinition`, 20 bytes each) — all 130 named.
  ProfileIndex is a STRING index into AkiText 006C (always even: full
  name at that index, short name at the next). Heights/weights validated
  (Misawa 185 cm/115 kg, Taue 192 cm/122 kg). 98 default + 16 edit + 16
  controller-pak.
- `roster/stables.json`: 17 stables @ ROM `0x408BC`. Member bytes are
  1-BASED ROSTER SLOT numbers (verified against all 3 AJPW stables and
  the contemporary 2000 FAQ roster columns — NOT ID2s as VPWStudio's
  field name suggests).
- `roster/costumes.json`: 396 costume entries (file 0x006B, 49 bytes
  each). Each default wrestler has 4 costume slots (AppearanceIndex =
  first slot); all edit/controller-pak wrestlers share slot 392. Option
  names resolved from AkiText 006A.
- `roster/hidden25.json`: the 25 wrestlers No Mercy carries as
  moveset+params only — 23 mapped to VPW2 slots (7 direct real-name, 16
  via stable order + FAQ columns, corroborated by the pun fake-names:
  "Hayate" ~ Hayabusa, "King Kong Freddy" ~ King Kong Brody, "El
  Mascaredo" ~ Mil Mascaras). Raven and Big Show are NOT in VPW2 — no
  FAQ/Wikipedia roster entry; recorded unmapped with the reason. Head
  models (face/neck/head triples) matched by DB label and verified on
  disk for all 23; mask files listed for the 4 masked wrestlers.
- `moveset/toki1.json`: 6,291 per-animation timing entries (file 0x034B,
  36 bytes each) — damage windows, reversal frames, vulnerable frames,
  breakaway frames, effects. Entry i = anim file 0x1A90+i.
- `moveset/move_damage.json`: 2,302 records (file 0x0277, 32 bytes each,
  VPWStudio `docs/movedamage.txt` layout). `weapon_damage.json`: 100.
  `edit_move_damage.json`: 1,010.
- `moveset/reversals.json`: 6 reversal tables (0x027A–0x027F, 576 B
  each) — bit-packed, dumped raw + u16; no decoder exists.
- `moveset/edit_mode_moves.json`: file 0x0061, u16 array (header 133 +
  1007 pairs, pairing is a hypothesis).
- `moveset/params_moveset_manifest.json`: 101 params/moveset file pairs
  (0x0281+), 98/130 wrestlers linked by ID4. Bit-packed; no parser
  exists in VPWStudio (same gap as No Mercy).
- `moveset/code_tables.json` + 7 `.bin` blobs: BitPacking tables +
  MasterMoveMods from the ROM code segment.
- `roster/blood.json` + 4 PNGs: blood 1bpp masks (256 B each, decoded as
  64×32 — dimensions inferred).

## 9. Fonts (`fonts/`)

- Large font (file 0x0001): 3,260 glyphs, 24×21, 3-byte header + 63 B
  1bpp each; terminator lands exactly at EOF (3,260×66 + 3 = 215,163).
- Small font (file 0x0002): 3,264 glyphs, 16×13, 2-byte header + 26 B
  each (3,264×28 = 91,392, exact).
- Font characters (file 0x0003): 3,254 u16 Shift_JIS codes; 3,253 decode
  (matches VPWStudio's "VPW2 Actual font characters: 3253" comment).
- Atlas PNGs + per-glyph header JSONs included.

## 10. Raw decoded files (`raw/`, 13,090 .bin files, 57 MB)

Every file in the ROM, LZSS-decoded where flagged, named by 1-based file
ID. The complete source from which everything above derives.

## Tools (`tools/`)

All extractors, adapted from the No Mercy lane's tools with VPW2 constants
patched in (same AKI engine, different offsets):

- `vpw2_census.py` — file-table census + verification
- `extract_all_anims_w3c.py`, `extract_all_models.py`,
  `extract_textures.py` — bulk extractors
- `vpw2_archives.py` — archive parser + arena assembler (custom: VPW2
  arenas are F3DEX2 chunks, not AkiModel pieces like No Mercy's)
- `vpw2_sound.py` — PtrTablesV2 + VADPCM → WAVs
- `vpw2_roster.py` — roster/stables/Toki1/damage/costumes/text
- `vpw2_hidden25.py` — costumes + Hidden 25 mapping
- `vpw2_fonts.py` — font atlases
- `vpw2_movemap.py` — move→AnimID map
- `vpw2_verify.py` — 1-based verification (ALL CHECKS PASSED)
- `lzss.py` — Asmik LZSS (ported from VPWStudio)

C tools (compiled from AKI-Club/vpw2 `tools/`, Unlicense) were used for
text/archives/menu backgrounds: `akitext`, `akiarc`, `menubg`,
`aki_lzss`. Binaries are not committed; rebuild from the decomp repo.

## Gaps — what could NOT be fully extracted

| Gap | Status | What it would take |
|---|---|---|
| Moveset/params bit-packing | Raw dumps + manifest only | Decode the BitPacking tables (ROM 0x3D4E0–0x3E63C), write a decoder, validate against known wrestlers. Would also give per-wrestler move lists and settle Raven/Big Show. |
| Sng → MIDI/audio | 19 raw `.sng` files | Run SubDrag's N64MidiTool (Windows GUI) on the sequences + bank samples, or port its sequence parser. |
| .tbl sound blobs | Raw only | Reverse the table format (looks like (offset, len) pairs). |
| Per-wrestler body-part model selection | Face/head/neck/mask/attire matched; torso/limbs/hair unmapped per wrestler | Reverse the game-code selection tables (not in VPWStudio; decomp is mostly asm). |
| Arena texture↔piece assignment | UVs in texel space | Read the game code that binds textures to arena pieces. |
| 734 move anims unlabeled | Labels empty in VPWStudio DB | Community labeling or move-content analysis. |

## References

- VPWStudio (AKI-Club, MIT): `AKI-Club/VPWStudio`, HEAD `a6452ff3`
  — file formats, FileTableDB/VPW2.txt, DefaultGameData.cs, docs.
- vpw2 decomp (AKI-Club): `AKI-Club/vpw2`, HEAD `bc8d5795` —
  `extract_baserom.sh` offsets, `tools/` (Unlicense).
- No Mercy re-extraction (western-heart main `11ebc898`): methods,
  VADPCM decoder, 0-based trap finding, Hidden 25 list.
- Cheaters Heaven VPW2 FAQ (2000): roster columns used for the
  stable-order mapping.
