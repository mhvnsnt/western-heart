# WWF No Mercy (N64, 2000) — Full-ROM File-Table Catalogue

Survey + extraction of **everything except the animation bank** (handled by a
separate agent). ROM: `WWF No Mercy (USA) (Rev-A).z64`, 33,554,432 bytes,
CRC32 `BACEEA13`. All paths below are under
`/home/hatch/workspace/no-mercy-reextract/full-rom/` unless stated otherwise.
The ROM was never modified or copied; all extraction used the W3c-corrected
file-table constants (table @ `0x16C31D8`, data base `0x1BD150`, 1-based IDs).

> **One-line summary:** 19,458 files catalogued, **12,642 files extracted
> (90 MB)** — every model, texture, arena, sound, font, menu background, move
> table, wrestler definition, costume, and shop item in the game, plus the
> hidden wrestlers and the full move universe. The repo model pool was
> **off by one file ID** (see §2); the ROM has 3,586 models, all parseable.

---

## 1. ROM layout map

| ROM range | Size | Contents |
|---|---|---|
| `0x000000`–`0x1BD14F` | ~1.8 MB | Boot code, game code, embedded data tables (incl. WrestlerDefs @ `0x465B8`, CAW tables @ `0x168D790`+, move-attr records @ `0x13E000`) |
| `0x1BD150`–`0x16C31D7` | 22,044,808 B | **File data** — 19,458 files, contiguous |
| `0x16C31D8`–`0x16D61E3` | 77,836 B | **File table** — 19,459 u32be entries (last = end sentinel) |
| `0x16D61E4`–`0x1FFFFFF` | 9,608,732 B | **Tail** — non-file data: 3 N64 sound banks (PtrTablesV2), 2 "Binary FX" sequence blobs, high-entropy sample data, `0xFF` padding at the end |

File access: `file(fid) = ROM[0x1BD150 + (table[fid-1] & ~1) :
0x1BD150 + (table[fid] & ~1)]`, IDs 1-based; low bit of the table entry =
LZSS-encoded flag. **8,250 files are LZSS-encoded; 0 animations are.**

## 2. File-table census (19,458 files, by VPWStudio DB type)

| Type | Count | Notes |
|---|---|---|
| AkiAnimation | 5,787 | **Not this task** (other agent). All verify `(len−4)%98==0`. File `0x4473` DOES parse (10 frames) — corrects TEARDOWN.md's "doesn't parse" claim (a shifted-window artifact). |
| Ci4Palette | 3,601 | 1,716 true 32 B palettes; 1,884 × 64 B (16-color palette + 32 B secondary table, shade/remap semantics TBD); 1 × 1,024 B ("Default Colors", fid `0x10F5`, 512×u16 value 1) |
| AkiModel | 3,586 | **All parseable** (see §3) |
| Ci4Texture | 3,531 | |
| Binary | 895 | 624 menu-background chunks + 99 movesets + 99 params + 6 reversals + damage/anim/prop tables + costumes + story font + 10 Sng sequences + a few unidentified (see §8) |
| AkiTexture | 833 | |
| Ci8Texture | 400 | |
| Ci8Palette | 387 | |
| I4Texture | 228 | |
| MenuItems_Moves | 138 | Move-menu files → 1,682 entries (see §5) |
| AkiText | 32 | 6,658 strings |
| MenuBackground | 16 | Each = 32 B palette + ONE 64×30 chunk; full background = 1 file + 39 following Binary chunks (see §6) |
| AkiLargeFont | 10 | 110 glyphs each, 24×22 1bpp |
| Ci4Background | 4 | 8 B header + 38,400 B raw CI4 320×240 |
| MenuItems_Shop | 3 | 161 shop items (see §6) |
| MenuItems_NoGroup | 3 | 50 theme songs, 42 titantrons, 100 pictures |
| AkiSmallFont | 2 | 112 glyphs each, 16×14 1bpp |
| RawCi4TexPal | 1 | |
| AkiArchive | 1 | fid `0x00F7`: 4 × 2,048 B entries, 54–76% `0xFF` (see §8) |

Machine-readable: [`file-table.csv`](file-table.csv) — one row per file
(fid, offset, length, encoded, decoded_len, db_type, db_label, magic8,
verified, verify_note).

## 3. Model-pool verdict — the repos are off by one file ID

**Proven finding:** the western-heart and wwe-wrestler-models repos' extracted
models/textures were built with the correct table constants but **0-based
indexing**. Every OBJ/PNG labeled fid N actually contains game file N+1
(correctly aligned, no splice — different from the animation bank's +0x19
splice bug).

- Proof: repo OBJ `model_11EE.obj` is byte-identical to fresh `model_11EF.obj`;
  `repo[fid] == fresh[fid+1]` geometry for 3,570/3,570 models; texture kinds
  match 5,029/5,029 under the same +1 shift.
- Consequence: the repos' "16 unparseable models" were never unparseable —
  under the shift they read palette/texture files. **Fresh extraction parses
  ALL 3,586 AkiModel files.**

| Pool | Models | Verdict |
|---|---|---|
| ROM (fresh extraction) | **3,586** | Complete, all parseable |
| western-heart repo | 3,570 | Missing 16, all shifted +1 |
| wwe-wrestler-models repo | 2,700 | **Missing 870** (arena 263, backstage 402, stage 92, weapon 34, lobby 79); its `manifest.json` is a stale copy of WH's claiming 3,570. WH and WM manifests are byte-identical. |

Textures: fresh **5,035 PNGs** vs repo 5,029 (6 more: I4 files whose label
dims failed under the shift). Kind counts otherwise identical.

## 4. What was extracted (12,642 files, 90 MB)

| Area | Count | Path | Contents |
|---|---|---|---|
| Models | 3,586 OBJs + 3,586 `.vc` sidecars + manifest | `extracted/models/` | Every AkiModel, correct window |
| Textures | 5,035 PNGs + manifest | `extracted/textures/` | Every texture (CI4/CI8/I4/AKI) |
| Arenas | 17 assembled OBJs + `.vc` + manifest | `extracted/arenas/` | 10 PPV arenas, ring_cage, 5 backstage, lobby |
| CAW | 3 JSONs | `extracted/caw/` | Name table (50 music entries), categories (15, 243 runs), **default costumes** (260 × 38 B records, 65 slots × 4 attires, all 38 fields named per VPWStudio `DefaultCostumeData.cs`) |
| Moves | 6 files | `extracted/moves/` | See §5 |
| Sound | 293 WAVs + 29 sequences + manifest | `extracted/sound/` | See §7 |
| UI | 41 files | `extracted/ui/` | See §6 |
| Misc | 25 files | `extracted/misc/` | Wrestler defs, movesets/params, reversals (in `moves/`), archive, fonts (in `ui/fonts/`), logs |

## 5. Move tables — the full move universe

### 5.1 Menu entries (what the player sees)
- **1,682 entries** in 138 MenuItems_Moves files: name, damage_info (raw
  flags byte — NOT a damage index), preview_pos, move_link, anim_id,
  anim_file_id, repeat_anim_id, master_move_id.
- `moves.json` + `moves.csv` (raw), `moves-enriched.json` + `moves-enriched.csv`
  (with joins, below).
- Cross-checked vs the mat-kings clip DB (4,409 clip entries): 1,177 menu
  names overlap; 1,723 mk-only are clip variants (P1/P2, Repeat, Break Up,
  Release, Win suffixes); 44 menu-only (mostly no-name placeholders +
  "Chokeslam from Hell", "DX", "Edge", "Elbow Smash").
- "Rock Bottom" is spelled **"Rockbottom"** in the menu (one word): anim 1240
  (= file `0x37FA`, matches the W3b doc), damage 35.

### 5.2 The joins (data-proven, VPWStudio does NOT document these)
- **MasterMoveID → animation:** files `0x01F0`/`0x01F1` are 16,820-entry u16
  arrays (Animations / Properties). `Animations[MasterMoveID] == menu AnimID`
  for 1,642/1,681 (39 mismatches off by ±1–2, all in a stride-10 block 3130+).
- **MasterMoveID → damage:** `Properties[MasterMoveID]` values are ALL in
  0..2135 = index into the damage table (file `0x01EF`, 2,136 × 36 B entries).
  Spot checks sensible: Stone Cold Stunner → damage 40, KO 5, head 5;
  Stomp 01 → damage 2; Punch 01 → damage 5, spirit gain 3; People's Elbow →
  damage 6.
- **The Properties table is stored twice:** file `0x0069` is **byte-identical**
  to `0x01F1` (verified). File `0x0069` was labeled "???" in the DB.
- **Full move universe is 2,875 moves**, not 1,682: 2,875 MasterMoveIDs have
  nonzero damage indices; only 1,681 appear in menus. The other ~1,194 are
  hidden/CAW-only moves (no menu entry). Animations array has 2,785 nonzero.

### 5.3 Damage table (2,136 entries, `moves/move-damage.json`)
36 B per entry, fields named per VPWStudio `MoveDamageTestDialog.cs`
`ShowData_NoMercy`: flying target body part, link (0..244, 18 distinct
values — likely follow-up/combo link into the damage table), damage (0–45,
mean 8.4; 1,375 nonzero), spirit gain, spirit drain (s8), blood chance,
KO chance, offensive/defensive params (Head/Body/Arms/Legs/Flying), attack
with/to, head/body/arm/leg damage, speed/flying damage, strike reaction,
special damage, previous move, move type (0: 1,925; 4: 176; 8: 26; 1: 9),
additional properties, plus 8 undocumented bytes kept raw.

### 5.4 Reversals (`moves/reversals.json`)
6 files `0x01F2`–`0x01F7`, 534 B each (Heavyweight, Heavy Special, Junior,
Junior Special, Martial Arts, Heel). No VPWStudio format exists — dumped as
raw hex + u16 arrays.

### 5.5 Movesets & params — bit-packed, raw dumps only
- **99 moveset files** (184 B) + **99 params files** (32 B) in
  `misc/wrestler-movesets-params.json` (raw hex + u16/byte arrays).
- 73 named wrestlers + **25 hidden wrestlers** (Raven, Vader, Big Show,
  Misawa, Kobashi, Tenryu, Onita, Hayabusa, Mil Mascaras, Great Sasuke,
  CIMA, etc. — VPW2 leftovers, fids `0x028D`–`0x02BE`) + 1 Default CAW.
- NOT plain u16 MasterMoveID arrays: Rock's moveset has values up to 57,520,
  only 11/92 resolve via MasterMoveID (likely coincidental), many values are
  bit flags (0,1,16,32,128,192,256,512). The key is VPWStudio's BitPacking
  tables (DefaultGameData: BitPacking_MainTable `0x44EE4`/278 B,
  BitPacking_MoveGroup_Wrestling `0x44270`/1,580 B,
  BitPacking_MoveGroup_Combo `0x4489C`/1,600 B) — decoding them is the open
  step (see §8).

### 5.6 Wrestler definitions (`misc/wrestler-defs.json`)
293 records × **20 B** (18 B fields + 2 B pad — the pad is in
VPWStudio's `WrestlerDefinition.ReadData` as "prepare for another possible
read") at ROM `0x465B8`: count = 64 wrestlers × 4 attires + 0x25 (37) edit /
controller-pak / GBC slots. Fields: wrestler_id4, wrestler_id2, theme_song,
entrance_video, height, unknown, weight (87–503 lb), moveset_file,
params_file, appearance_index, profile_index. **256 records named** via
moveset-file labels (64 distinct wrestlers); record 0 = The Rock (moveset
`0x1FA`, params `0x1F9`, weight 175, theme 37).

## 6. UI / menu assets (`extracted/ui/`)

- **Menu backgrounds** (`ui/menubg/`, 16 PNGs 320×240): each background = 1
  MenuBackground file (32 B palette + chunk 01) + 39 following Binary files
  (960 B chunks 02–40), row-major 5 cols × 8 rows per VPWStudio
  `MenuBackground.cs`. **Visually verified** — Character Select renders the
  WWF scratch logo on dark metal, chunks in correct order.
- **Ci4Backgrounds** (4 PNGs 320×240): 8 B fixed header
  (`3F EF 00 20 00 00 08 07`) + 38,400 B raw CI4. **Visually verified** —
  Mall Data background reads "DATA" / "World Wrestling Federation".
- **Fonts** (`ui/fonts/`, 12 files + story font): AkiLargeFont 10 × 110
  glyphs (24×22 1bpp) + AkiSmallFont 2 × 112 glyphs (16×14 1bpp), rendered
  as glyph sheets per VPWStudio `AkiFont.cs` (`ReadFontData_Large/Small`,
  3-byte / 2-byte headers, 1bpp packed pixels). **Visually verified** —
  font `0x4477` renders clean A–Z, a–z, 0–9, punctuation.
  - **Story-mode title font** (file `0x01DA`, 23,364 B): raw CI4, **24 px
    wide × 1,947 tall vertical strip**, 81 cells at 24-row pitch, **76
    glyphs** (decorative serif: `? $ % &`, 0–9, A–Z, a–z, `, . : ; " / !`).
    Width proven by vertical-correlation peak (CI4 W=24: 0.72 vs 0.64 for
    neighbours; 1bpp W=96 = same 12-byte row stride). Rendered as full strip
    + glyph sheet (`story_01DA_ci4_w24.png`, `story_font_01DA_glyphs.png`).
    Grayscale palette (index×17); true palette unknown. The DB label's
    "w:24,h:1024" is wrong on height (1024 → 1947).
  - Font texture `0x4A50` (256×264 CI4, palette `0x4A4F`) rendered as
    `menubg/font_4A50_mall_large.png`.
- **Shop** (`ui/shop.json`, re-parsed correctly with the leading u8 count
  byte): **161 items** — 100 attire (500–80,000), 19 other (5 wrestlers,
  12 attire, 2 unknown type `0x41`; 1,000–500,000), 42 moves (800–10,000).
  Fields: price, unlock_id, item_type, item_data, name, description
  (e.g. "Basket shorts", "[Ring Attire]", 800).
- **NoGroup** (`ui/nogroup.json`): 50 theme songs, 42 titantrons, 100 pictures.
- **AkiText** (`ui/akitext.json`): 32 files, 6,658 strings.
- **CAW text tables** (`caw/`): entrance-music table @ `0x168D790` (50
  entries; ORIGINAL 1–7 = `0x33`–`0x39`), part strings @ `0x168DD89`+ in 15
  categories; inline text codes are two classes (Class A zero-width; Class B
  dictionary-expansion, e.g. `AA 01` → "ERICAN", `1C` → "Buh"). Wrestler
  table @ `0x168D930`: 42 entries. Full details in
  `reference/wh_CAW-EDIT-DATA.md` and `reference/wh_CHARACTER-DATA.md`
  (incl. `0x13E000` data segment: move-attr records, float table @
  `0x13E2BC`, RAM pointer table @ `0x13E4A0`, u16 index run @ `0x13E4D4`).

## 7. Sound (`extracted/sound/`, 293 WAVs + 29 sequences)

- **3 N64 PtrTablesV2 banks**, located by magic-string scan and independently
  confirmed by `gameconfigsound.ini` [WWF No Mercy (U) (V1.1)]: ptr
  `0x16F32A0`/`0x1858030`/`0x1967410`, wave tables `0x16F6F10`/`0x185EDB0`/
  `0x1969880` (each exactly `0x60` before the V1.0 US offsets in VPWStudio
  soundtool.txt). Format from `N64AIFCAudio.cpp` `ReadAudioN64PtrWavetableV2`:
  `0x30` header (count @`0x20`, volumes @`0x24`, pans @`0x28`, instrument
  ptr table @`0x2C`); instrument record: wav.base/len, loop start/end/count
  + 16 s16 state, predictor order/npreditors/coefs. Waves are VADPCM @
  22,050 Hz mono s16 (decoder ported from `decode()`/`decode_8()`).
  Bank names in the ROM header are empty strings — the bank dirs are named
  neutrally `bank1`/`bank2`/`bank3` (earlier "proset"/"sepack" labels were
  Revenge names from soundtool.txt, not verified No Mercy names).
- **bank1: 85 waves, 115.9 s, 22 looped. bank2: 165 waves, 86.7 s, 2 looped.
  bank3: 43 waves, 527.4 s, 42 looped. Total 730.0 s**, peak amplitudes
  4,352–32,768, zero silent files. Manifest `sound.json` (per-wave base/len/
  loop/volume/pan/samples/duration/ADPCM order/npredictors).
- **Music sequences: 29 `.sng` files** — 27 in file IDs `0x2C0`–`0x2DA`
  (each starting `00 00 02 15`, exactly matching `gameconfigmidi.ini`
  [WWF No Mercy (U) (V1.1)] ranges) + 2 "Binary FX" tail blobs
  (`0x1855F90`–`0x185802A` starting `0000011e`,
  `0x1965C50`–`0x196740C` starting `000000c8`). 15 have DB labels
  (scratching / Smackdown Mall / match / saxophone / intro / credits music).
  Sng→MIDI conversion needs SubDrag's N64MidiTool (Windows GUI, cloned in
  `reference/n64-tools/`; config already has U V1.1 entries) — not attempted
  (see §8).

## 8. Gaps — what could NOT be fully extracted, and what it would take

| Gap | Status | What it would take |
|---|---|---|
| Moveset/params bit-packing | Raw dumps only (99+99 files). Format is bit-packed per VPWStudio's BitPacking tables; no parser exists in VPWStudio. | Decode the BitPacking tables (`0x44EE4`, `0x44270`, `0x4489C`) — read the bit layout, then write a decoder and validate against known wrestlers (e.g. Rock's moveset should contain his signature moves). |
| Sng → MIDI/audio | 29 raw `.sng` files extracted; not converted. | Run SubDrag's N64MidiTool (Windows GUI, in `reference/n64-tools/`) on the sequences + sound-bank samples, or port its sequence parser. |
| AkiArchive `0x00F7` | 4 × 2,048 B entries, 54–76% `0xFF`, rest unanalyzed. | Inspect the non-`0xFF` regions for structure; may be placeholder/reserved slots. |
| Binary `0x0068` (4,192 B) | 2,096 u16s, values to 16,810 (MasterMoveID range); first values look like (key, MasterMoveID) pairs. Undocumented. | Compare against the move tables for a join (e.g. is it a sorted index into the 2,875 moves?). |
| Binary `0x01EE` (9,216 B) | 4,608 u16s, 1,787 nonzero, values to `0xFF00` (bitfield-like). Undocumented. | Pattern analysis; no VPWStudio reference. |
| Binary `0x01F8` (19,224 B) | List of `N####-A` codes ("ZZZZZZZZ" header, then `N0339-A`, `N0347-A`…). Looks like an asset/part catalogue or debug leftover. | Cataloguing only; no known consumer in VPWStudio. |
| 64 B palettes (1,884) | 16-color palette + 32 B secondary table; shade/remap semantics TBD. | Compare secondary tables across palettes sharing a base palette. |
| Story font palette | Rendered grayscale; true palette unknown. | Find the palette file the game pairs with `0x01DA` (no `\|p:` reference in the DB label). |
| Shop item type `0x41` | 2 items in Shop 2 have unknown type `0x41` (vs `0x43` attire, `0x57` wrestler, `0x4D` move). | Read VPWStudio's `MenuItems_Shop` item-type enum fully. |
| Damage "link" field | 18 distinct values 0..244, presumed combo/follow-up link into the damage table; unconfirmed. | Trace in-game or cross-check against known combos. |
| AnimID mismatches | 39 menu entries where `Animations[MasterMoveID]` ≠ menu AnimID (off by ±1–2, stride-10 block 3130+). | Likely a second anim slot (repeat/variant); check against the animation bank's clip labels when the other agent finishes. |

**Resolved during this pass (no longer gaps):** WrestlerDefs stride (20 B, not
18 — the 2 B pad is in VPWStudio's `ReadData`); shop parse (leading count
byte); story font `0x01DA` (CI4 24×1947 strip, 76 glyphs); props-table
duplicate (`0x0069` == `0x01F1`); hidden wrestlers (25 movesets + 25 params);
sequence magics (27 × `00000215` + 2 FX blobs); font glyph rendering (all 12
fonts + story font verified visually); menu backgrounds (chunk order +
palettes verified visually).

## 9. Bannon wiring flags

Which extracted assets plug directly into Bannon's creation suite / move
system / arenas, and which need conversion first.

### Plugs in directly (or nearly)
- **Move library data** — `moves/moves-enriched.json` + `move-damage.json`:
  1,682 named moves with damage, spirit, KO/blood chances, body-part damage,
  and animation IDs. The AnimID joins straight to the AKI animation bank
  (AnimID = file_id − `0x3322`). Bannon's move system can ingest this as
  its data layer; the physics layer (momentum/weight/collision) is Bannon's
  own — the game animations are the choreography, Bannon physics makes them
  real (per Mars's direction).
- **Wrestler definitions** — `misc/wrestler-defs.json`: 64 wrestlers with
  weight, height, theme, entrance video, moveset/params file refs. Direct
  roster data.
- **Default costumes** — `caw/default-costumes.json`: 260 records, 38 named
  fields each (attire, colors, pads, boots, hair, face, masks, hats,
  portrait). Direct creation-suite preset data.
- **Shop catalogue** — `ui/shop.json`: 161 unlockable items with prices and
  categories. Direct economy/progression data.
- **Sound** — 293 WAVs @ 22,050 Hz mono s16: standard WAVs, usable as-is
  for hits, crowd, UI, music beds (may want resampling to 44.1/48 kHz for
  modern engines — trivial).
- **Fonts** — glyph sheets are plain PNGs; the 1bpp glyph data + headers
  are in the JSONs. Usable as bitmap fonts or as reference for a vector
  redraw.
- **Text strings** — `ui/akitext.json` (6,658 strings): menu/UI text corpus.

### Needs conversion first
- **Models (3,586 OBJs)** — N64-era low-poly meshes with vertex colors
  (`.vc` sidecars). Need: UV/texture re-linking (textures are separate
  files; the OBJ↔texture pairing is not yet mapped), up-res/retopology for
  modern standards, and rigging — the four new numbered characters
  (Perk Spangled, Stone Core, O. Godd Damme, Wildebeest) need bones/moves/
  rigs from No Mercy or recent 2K games; the AKI→Tekken3 retarget pipeline
  is proven and the 26-joint system is decoded, but the re-extraction +
  retarget is the other agent's lane.
- **Textures (5,035 PNGs)** — CI4/CI8/I4 paletted textures, N64 resolution
  (many 32×32 / 64×64). Need upscaling/AI-upscale + PBR material authoring
  for modern rendering; palette pairing is by file adjacency, not embedded.
- **Arenas (17 assembled OBJs)** — geometry is assembled and usable, but
  needs the same texture re-linking + modern lighting/materials, and
  reskinning per Mars's direction (official WWE arenas reskinned, Bannon's
  own arenas kept).
- **CAW part strings / categories** — `caw/caw-categories.json` +
  `caw-name-table.json` are the *labels*; the part geometry lives in the
  model pool (body_parts / face / attire) and needs the part↔model mapping
  (the CAW-EDIT-DATA doc has the category structure; the geometry join is
  the remaining step).
- **Movesets/params** — raw bit-packed dumps until the BitPacking tables are
  decoded (see §8). Once decoded, they become per-wrestler move lists that
  plug straight into the move system.
- **Music sequences (29 `.sng`)** — need N64MidiTool conversion to MIDI
  (see §8) before they can be rendered or remixed.
- **Reversals** — raw dumps; format undocumented. Reversal *frames* are
  documented in VPWStudio's Toki1 dialog only.

### Reference material (in `reference/`)
- VPWStudio source (AKI-Club/VPWStudio, public): the format authority for
  move tables, costumes, fonts, backgrounds, wrestler defs, shop, text.
- N64-Tools (jombo23/N64-Tools, SubDrag): N64MidiTool + game configs
  (sound/MIDI ini entries for U V1.1), `N64AIFCAudio.cpp` (VADPCM + bank
  format).
- Western-heart docs (TEARDOWN, CHARACTER-DATA, CAW-EDIT-DATA,
  NOMERCY-TEARDOWN, ANIMATION-ISOLATION, ARENAS, TEXT-CODE-DICTIONARY,
  TOKI2-SEMANTICS, WIRING-INVENTORY), tables, manifests, mat-kings move DB,
  MOVE-DATABASE.json, MOVES-LIBRARY.md.
- `tools/`: local copies of the extraction tools (W3c-corrected constants,
  ROM path via `NOMERCY_ROM`), plus `NoMercy-FileTableDB.txt` (VPWStudio DB).
- `work/`: `phaseA.py`, `full_pass.py`, `fixups.py`, `game_data.py` — the
  scripts that produced this survey (re-runnable).

---

*Survey completed 2026-11-19. Animation bank excluded by design (separate
agent). No repo was modified; nothing was pushed; the ROM was never copied.*
