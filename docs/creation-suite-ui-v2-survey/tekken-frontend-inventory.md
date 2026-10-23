# Tekken Front-End Asset Inventory — Creation Suite UI v2

**Survey date:** 2026-10-21 (CDT). **Mode:** READ-ONLY — nothing extracted, nothing modified except this file + its JSON sibling.
**Disk at survey:** `/dev/mapper/rv 100G, 95G used, 97%` — no large extraction attempted.
**Bottom line up front:** There is **no extracted Tekken panel/frame/cursor/icon sprite set anywhere in holdings.** The only already-extracted Tekken PNGs usable as skin reference are the 2 PSP system images. Everything else Tekken-front-end lives (a) still inside the decrypted bulk / GZIP containers, un-decoded at the UI level, (b) as text/data tables (item names, NTXL UI strings) with no art, or (c) as documentation/schema only. Details + exact paths below. Every claim names a path actually listed/read in this survey.

---

## Answers to the three explicit questions

### (a) Does any held teardown contain T6 PSP customization-screen layout/menu data (positions, menu item lists)?
**No pixel layout / positions data — YES to menu item *lists* as text, in two forms:**
1. **Item names (the menu's item list content):** `~/workspace/_w7b-wh/customization/parts/tekken/tekken6-item-names.json` — 9,440 records shipped (runs of ≥4), 11,053 valid record starts found; record = `u32 rec_size + u8 item_idx (1–160) + ASCII name`, extracted from `bulk_decrypted.bin`. Samples seen in the catalog: `Bandana`, `Triceratops Helmet` (first two records), plus research-doc samples `Sledgehammer, Japanese Sword, Leather Pants, Long Jin Bangs, Ki (Pink), Aura (Red), SP Rage (Lightning/Ice/Fire/…)`.
2. **UI strings + slot categories:** 120 `NTXL` string tables in the bulk, documented in `~/workspace/_w7b-wh/customization/parts/tekken/tekken6-item-catalog.json` → `ntxl_string_tables`: entry-82 English table spot-verified at bulk offset `0x1AB2000`; strings include `Select item to equip.`, `Purchase item?`, `Equip item?`, `Sell item?`, `The hair item must be removed to equip this item.`; categories include `Hair - Back`, `Hair - Front (Right)`, `Face - Other`. The `(msg_id → string)` mapping inside NTXL is still TBD.
3. **What is MISSING (the blocker):** the `sbcustomize_item_t` **definition array** (per-item slot/price/character/pack) is `NOT_LOCATED` per `tekken6-item-catalog.json` → `blocker_definition_array` / `status: NAME_TABLES_FOUND_DEFINITION_ARRAY_MISSING`. Without it, names cannot be honestly joined to slots/prices/characters. **No file contains screen X/Y positions, panel rects, or cursor coordinates for any Tekken game** — searched: EBOOT strings, all teardown docs, `_fighter-completeness/main/`, `_w7b-wh/customization/parts/tekken/*`. The EBOOT proves the screens *exist in code* only: `tcb_customize_mode_t`, `tcb_gamemode_customize_t`, `tcb_CustomizePSP_Manager`, `tcb_customizemode_t`, `tcb_swg_customize_t`, `O2MenuDataKeeper`, `O2Menu / Level0Menu / Level1Menu / Level2Menu`, `_CURSORMOVE` — all in `~/workspace/_t6r4-work/wh/teardown/tekken6/decrypted/EBOOT.DECRYPTED.ELF` (offsets in the item catalog, e.g. CustomizePSP_Manager at file offset `0x3B3F48`).

### (b) Is there a usable FONT extracted from any Tekken game?
**No.** No Tekken font file (`.fnt/.ntx/.pgf/.ttf/.gim` font) exists extracted anywhere searched.
- T6 PSP's font is *referenced in code only*: EBOOT strings `owfont_fnt_t`, `owfont_ntx_t`, `tcb_owfont_t`, `tcb_owfonttex_t`, `tcb_owfont_draw_t` in `EBOOT.DECRYPTED.ELF` — i.e. a proprietary `owfont` (`.fnt` metrics + `.ntx` texture) pair that must live inside the un-decoded bulk/GZIP data. No `.fnt`/`.ntx` file was found on disk.
- **Do NOT mistake these for Tekken fonts:** `~/workspace/_t6r4-work/ppsspp/AppDir/bin/assets/flash0/font/*.pgf` (18 PSP *system* fonts, e.g. `ltn0.pgf`, `jpn0.pgf`) and `.../assets/Inconsolata-Regular.ttf`, `Roboto_Condensed-*.ttf` are **PPSSPP emulator assets**, not Tekken assets.
- T7/T5/TTT2: no font file found either (see per-source sections). Verdict: **fonts category = EMPTY (code references only).**

### (c) Do Tekken 7's own UI sprite files exist anywhere in holdings?
**No — confirmed by search, one line:** No T7 game `.pak`/`.uasset` UI sprites exist in holdings (the only `.pak` hits in `~/workspace` are CUE4Parse/repak *test fixtures* under `~/workspace/tools/tekken-decrypt/t7/`; the T7 parts survey at `~/workspace/_fighter-completeness/main/customization/parts/tekken7/T7-CUSTOMIZATION-PARTS-SURVEY-2026-10-21.md` independently records 0 meshes / paks never acquired, ~47 GB download blocked).

---

## Source 1 — `~/workspace/_t6r4-work/` (Tekken 6 PSP teardown lane)

### 1.1 The workdir as found
- `wh/` = a western-heart checkout (branch `teardown`); the teardown proper is `wh/teardown/tekken6/` — **114 files, 9.1 MB total** (no extracted game-data tree).
- `dumps/` and `dumps_auto/` are **EMPTY (0 files each)** at survey time.
- `iso/tekken6-psp.iso` — 816 MB (855,638,016 B per `TEARDOWN.md`).
- `recon/` holds only a split backup tar: `t6-recon-backup.tar.part-aa` (524,288,000 B) + `.part-ab` (524,288,000 B) + `.part-ac` (82,708,480 B) + `tarlist.txt` (5,830 lines / 583,283 B) + `recon/x/tekken6/work/decrypt3/` (see §1.4). The tar itself was **not** opened (read-only + disk).
- Emulator screenshots: 51 PNGs at the lane root (`shot*.png`, `shotP*.png`) + 20 in `auto_shots/stage*.png` — see §1.6.

### 1.2 ISO file table (listed this survey, Python ISO9660 walk, no extraction)
Complete listing — this is the *entire* filesystem; there are no loose UI files:
```
/PSP_GAME/ICON0.PNG            LBA 55344   17,590 B      FILE
/PSP_GAME/ICON1.PMF            LBA 55488  221,184 B      FILE
/PSP_GAME/PARAM.SFO            LBA 55328      560 B      FILE
/PSP_GAME/PIC1.PNG             LBA 55360  251,946 B      FILE
/PSP_GAME/SND0.AT3             LBA 55600  275,444 B      FILE
/PSP_GAME/SYSDIR/BOOT.BIN      LBA 55744 4,158,144 B     FILE (= EBOOT size)
/PSP_GAME/SYSDIR/EBOOT.BIN     LBA   544 4,158,480 B     FILE (~PSP encrypted)
/PSP_GAME/SYSDIR/OPNSSMP.BIN   LBA    32      752 B      FILE
/PSP_GAME/SYSDIR/UPDATE/{DATA.BIN 23,223,168 B; EBOOT.BIN 5,550,208 B; PARAM.SFO 2,080 B}
/PSP_GAME/USRDIR/DATA401.IDX   LBA 230240  26,028 B     FILE
/PSP_GAME/USRDIR/DINF_400.BIN  LBA 230192     120 B      FILE
/PSP_GAME/USRDIR/modules/{libpsmfplayer.prx 32,144 B; psmf.prx 6,800 B}
/PSP_GAME/USRDIR/movie/        46 × .pmf (618,496 B title.pmf … 36,304,896 B opening.pmf)
/UMD_DATA.BIN                  LBA    30       48 B      FILE
```
Plus the decisive fact from `wh/teardown/tekken6/DATA401-RE-NOTES.md` §1: **all filesystem files end at sector 230253; sectors 230253–417792 = 384.1 MB of unlisted raw-sector tail** — that tail *is* the game data (models/textures/UI/audio). The game reads it via `disc0:/sce_lbn0x%x_size0x%llx` (EBOOT string). **There is no `cus/custom/menu/font/2d/sprite/icon/cursor/frame` filename anywhere in the ISO table** — the filename search the task asked for returns only `ICON0.PNG / ICON1.PMF / PIC1.PNG` above, because all real UI art is nameless inside the tail.

### 1.3 `wh/teardown/tekken6/ui/` — the only extracted UI folder (3 files)
| File | Format / size | What it is |
|---|---|---|
| `ui/psp_ICON0.png` | PNG 144×80, 17,590 B | PSP XMB icon — byte-identical to ISO `ICON0.PNG`. Extracted, shippable as-is. |
| `ui/psp_PIC1.png` | PNG 480×272, 251,946 B | PSP XMB background — key art (Kazuya/Heihachi/Jin + TEKKEN 6 logo, viewed this survey). Extracted. This is cover art, **not** a menu panel/frame. |
| `ui/README.md` | Markdown, 1,065 B | States plainly: *"all UI assets, character portraits, menu art, and customization assets are locked behind PSP ~PSP encryption"* and lists the wanted extractions (select portraits, customization menu assets, versus art, stage-select art, HUD) as **future** work. |

**Panel/frame art: EMPTY beyond PIC1. Icons: 1 (ICON0). Cursors/arrows: EMPTY. Button glyphs: EMPTY. Fonts: EMPTY.** Searched: full `find` of `wh/teardown/tekken6/` (114 files listed) + filename grep for `cus|custom|menu|title|font|2d|sprite|icon|cursor|frame|gim|tm2|tim` — hits were only `ui/*` above, `ref_frames/*` (§1.6), and tooling.

### 1.4 The decrypted bulk — where the UI art actually is (still containerised)
- `~/workspace/_t6r4-work/recon/x/tekken6/work/decrypt3/bulk_decrypted.bin` — sector-cipher-decrypted bulk (367 M on disk; a second identical-path copy at `~/workspace/_w7a-work/extract/tekken6/work/decrypt3/bulk_decrypted.bin`). Sibling docs: `IDX-FORMAT.md`, `GZIP-FORMAT.md`, `full_bulk_decrypt.py`, `manifest.json`.
- `manifest.json` (read this survey): **478 files, 195,578,491 B accounted**, layouts `H1: 216 / relaxed: 262`; magics: `NTPP: 52, GZIP: 41, GZIP+prefix16: 35`, remainder opaque `bin_e*` (entropy-class labels, e.g. `bin_e6.2: 51`). File sizes 80 B … 81,591,641 B (the 81 MB file = the NDPP archive, entry 87).
- Full-bulk magic scan run this survey (streaming count over the whole file): `NTPP ×599, NDPP ×1,375, GIM ×65, TIM2 ×0, MIG.00.1PSP ×0`. **Interpretation, stated carefully:** the 65 `GIM` byte hits are *not* validated GIM headers (proper GIM magic `MIG.00.1PSP` = 0 hits) — they are almost certainly coincidental bytes inside compressed/NTPP data. **No standalone `.gim/.tm2/.tim` texture file has ever been carved out of this bulk.** Per `models/NDPP-FORMAT.md`, GMO magic also has 0 hits in the bulk; NDPP sections are metadata + bounding volumes + normals, not render meshes.
- GZIP layer state (`WIRING-INVENTORY.md` + `tools/round3-evidence/scoreboard_strict.txt`, both read this survey): **76 GZIP containers, only 20/76 byte-exact** (the 20 are small: mostly 1,088 B records + 960 B / 336 B / 416 B files); **56 fail** with `distance too far back`, and round-3 proved by Unicorn emulation that *the game's own inflate rejects them too* — an encode-context/dictionary is still missing. The 18 `COM` containers (gzip idx 58–75, entries 709–735) are all in the failing set. **Any UI texture pack inside a GZIP/COM container is therefore not yet extractable.**
- Extractability verdict for bulk UI art: **needs two more steps, neither done** — (1) crack the GZIP encode context / identify which of the 478 entries are the `CUSTOMIZEPACK%d_%d` / sprite packs (EBOOT pack names, §a), (2) then carve GIM/TIM2-equivalent textures and convert GIM→PNG. No PNG conversion of a game UI texture exists yet anywhere (searched: every PNG under the teardown is ICON0/PIC1, previews, proof renders, or screenshots).

### 1.5 Decrypted EBOOT — code-level UI evidence (no art, real structure)
`wh/teardown/tekken6/decrypted/EBOOT.DECRYPTED.ELF` — 4,158,144 B, MIPS32 LE (decryption documented in `decrypted/README.md`: KIRK/`pspc`, tag `0xD91612F0`). `strings` run this survey (16,150 strings) found, verbatim:
- Font system: `owfont_fnt_t, owfont_ntx_t, tcb_owfont_t, tcb_owfonttex_t, tcb_owfont_draw_t, tcb_owfont_appfileinfo_t`
- Customize: `CUSTOMIZEPACK%d_%d, HAIRCUSTOMIZEPACK%d, DEFAULTPACK%d` (from item catalog), `CUSTOMIZE, tcb_customize_mode_t, tcb_gamemode_customize_t, tcb_CustomizePSP_Manager, tcb_customizemode_t, tcb_swg_customize_t, sbcustomize_item_t` (RTTI ×6), `tcb_camera_custom_t`, 12 × `tcb_kkItemMotionTick*` handlers
- Menus: `TOPMENU, MAINMENU, PAUSEMENU, TIME_ATTACK, DEBUG_MAINMENU, RETURN_TO_MAIN_MENU, exit_to_topmenu, exit_to_menu, O2Menu, O2MenuDataKeeper, O2_NodeTreeGen_Menu, Level0Menu/Level1Menu/Level2Menu, CSimpleMenu, _CURSORMOVE, DialogWindow`
- Sprites/HUD: `tk6sprite::battle::CMainTcb_t / CGaugeTcb_t / CGaugeRageTcb_t, tk6sprite::always::CUpperTcb_t / CLowerTcb_t / CManagerTcb_t, tk6sprite::fade::CMainTcb_t, tcb_battle2d_roulette_t, tcb_scene_object_2deffect_t`
- Data refs: `DINF_400.BIN, %s/DATA401.IDX, KEY.DAT, TEKKEN6.BIN`
These are **layout-data-by-code only**: class names + pack-name formats. No coordinates, no textures.

### 1.6 Non-UI images in the lane (inventoried so they are not miscounted)
- `wh/teardown/tekken6/ref_frames/` — **42 JPGs** (`ending_*.jpg`, 480×272, ~18–24 KB each): one frame per ending video. Video frames, not UI.
- `wh/teardown/tekken6/videos/README.md` — the 46 PMFs themselves live on GitHub Release `tekken6-endings-v1`, **not** on disk in this lane.
- `wh/teardown/tekken6/models/previews/preview_grid.png` (1.7 MB) + `preview_closeup.png` (1.3 MB), `models/ndpp_bounding_volumes.glb` (282,532 B), `tools/proof/cloud_front.png` (230 KB) — NDPP bounding-volume / sample-GMO renders. Not UI.
- Lane-root screenshots (71 PNGs total): `shot1–31.png, shotP1–21.png` + `auto_shots/stage1–20.png`. One was viewed this survey (`shot21.png`): an in-game snowy stage/cinematic frame with a small `×` marker — i.e. **PPSSPP gameplay captures, useful as visual reference for how the game looks, but they are photographs of the game, not extractable panel/icon assets**, and none was verified in this survey to show the customization screen specifically.

### 1.7 Tooling already held (for a future extraction, not assets)
In `recon/tarlist.txt` (the backup tar's listing, read this survey): `tekken6/work/tooling/sources/puyotools/` (full GIM encode/decode source, e.g. `PuyoTools.Core/Textures/Gim/GimTextureDecoder.cs`) and `tekken6/work/tooling/sources/PSP-GMO-Loader/` (GimDataStructures + sample Dissidia PNGs — **those PNGs are Dissidia sample data, not Tekken**). Plus on-disk: `wh/teardown/tekken6/tools/sector_cipher.py`, `tools/tekken6_gzip.py`, `tools/k1k2_extract.py`. So a GIM→PNG converter *is* in holdings (inside the tar) — there is just no carved GIM to feed it yet.

---

## Source 2 — `~/workspace/_fighter-completeness/main/` (western-heart main copy)

238 files total (`find` this survey). **There is no `teardown/` directory in this copy at all** (`ls` → No such file or directory).
- `customization/` contains: `PARTS-REGISTRY.json` (1,222,194 B), `tools/apply_customization.py`, `profiles/pantera.json`, `eye-library/eye-classic-original.png` (WH asset), `parts/no-mercy/` (WWF No Mercy catalog + 1 GLB) and `parts/tekken7/` (below). **No Tekken UI texture, panel, icon, or font file.**
- `customization/parts/tekken7/` — 4 files, all data/docs, **zero assets**:
  - `CATALOG.json` (5,440 B): `_meta.status` = *"EMPTY — SURVEYED, NOT IN HOLDINGS"*, `parts: []`, all 16 slot counts 0, plus 2 `named_gaps` (generic skull mask `tekken7:cmn:full_head:skull-mask`; the full T7 set).
  - `T7-CUSTOMIZATION-PARTS-SURVEY-2026-10-21.md` (11,467 B): the 2026-10-21 survey — 0 part meshes in every holding checked, acquisition route = Steam paks + `umodel_linux` (held inside release `tekken7-full-v1`).
  - `README.md` (1,645 B), `catalog.test.mjs` (3,812 B).
- `docs/` = only `FIGHTER-COMPLETENESS-AUDIT-2026-10-21.md`. `game/js/menus.js` (22 KB) and `game/js/select-screen.js` (27 KB) are **Western Heart's own hand-written menus** — relevant as the v2 skin's *target*, not a Tekken source.
- Note: the fuller Tekken data lives in the sibling copy `~/workspace/_w7b-wh/customization/parts/tekken/` (same repo, different worktree — inventoried in Source 3/§a because the task's Source-2 copy lacks `parts/tekken/` entirely; `_fighter-completeness/main/customization/parts/` has only `no-mercy/` + `tekken7/`).

---

## Source 3 — tekkenmods documentation (T7 customization UI structure, docs only)

**Locations found by `find ~/workspace -iname "*tekkenmod*"`:** exactly one hit —
`~/workspace/agent-ops/w1-allstars-work/gre/tekken7/tekkenmods-docs/` — which is an **EMPTY directory (0 files)** in that worktree. The docs' *content* survives in two derived holdings, both read this survey:
1. `~/workspace/tekken-customization-extraction/REPORT.md` (15,732 B, 2026-10-16) — the extraction report built from `tekkenmods-docs/files/en/Tekken_7/TKDataPatcher/index.md` + `.../Basic_Information/Overview/{Assets,Characters}/index.md` (those original paths, under the now-missing `~/workspace/game-reverse-engineering/tekken7/`, do **not** exist on disk today — `ls` confirmed).
2. `~/workspace/_w7b-wh/customization/parts/tekken/tekken7-slot-catalog.json` (9,803 B) + `MANIFEST.json` + `PARTS-INDEX.json` (26 parts, all full-character FBXs, no UI).

**What the docs document about the T7 customization UI (structure/flow, no art):**
- **16 equipment slots** (slotId 1–15 + 17; 16 skipped): HEAD, HAIR, FULL_HEAD, HAIR_ACC, GLA (glasses), FACE, FACE_HAIR, MAKE_UP (texture class), UPPER, FULL_BODY, LOWER, UPPER_ACC, LOWER_ACC, EXTRA, Effects, Aura — each with UI title + asset type (`CharacterCustomizeItem` / `CharacterItemTex` / `EffectCharacterItem` / `AuraCharacterItem`) + game path `Character/Item/Customize` (Effects→`Item/EffectItem`, Aura→`Item/AuraItem`).
- **UI organisation = Slot Group IDs** (−236 Mirroring … −254 Head; full table in REPORT.md §2.2) — this is the closest thing in holdings to a *menu grouping/flow* spec.
- **Item record = 21-field CSV** (ShopID … AdditionalText; full spec REPORT.md §3, incl. `SlotColors 0–5`, `PlayerCusID 0=generic/1=1P/2=2P`, `ItemCost`, `Rarity`, CCI reference path `TekkenGame/Content/<Path>/<CHAR_ABBR>/<SLOT_TITLE>/<NAME>`).
- **Asset prefixes:** SK/SKT/SM/BP/EI/ECI/ACI/CS/CCI/CI/M/MI/T/PA (REPORT.md §4). **57 character IDs** (0–56, REPORT.md §5). **Slot conflicts:** FULL_HEAD ⊃ HEAD+HAIR+FACE+…, FULL_BODY ⊃ UPPER+LOWER (REPORT.md §10). **Positioning paradigm:** bone sockets + XYZ offset / pitch-yaw-roll / scale, min-max ranges **not** documented.
- **Explicitly NOT documented / not held** (REPORT.md §8/§11): *"Actual UI .uasset files (menu layouts, textures) — ❌; exact screen positions or dimensions — ❌; font data — ❌."* In-pak UI/part layout for a future pull (from the T7 parts survey): meshes `Game/Character/Items/Mesh/{cmn,<CHAR>}/…`, records `Game/Character/Items/{CharacterItem,Customization,Sets,AuraItem,EffectItem}`.
- T6/TTT2 schemas from the same documentation effort: `_w7b-wh/customization/parts/tekken/tekken6-slot-catalog.json` (4 slots: Head/Upper/Lower/Other, anchors, conflicts) and `ttt2-slot-catalog.json` — both state their source as *public documentation*, item meshes not extracted.

---

## Source 4 — Tekken 5 / TTT2 teardowns (brief)

### Tekken 5 (PS2) — the one with a real, cracked UI/video archive (but no UI sprites extracted)
- Status doc: `~/workspace/agent-ops/w1-allstars-work/gre/tekken5/TEARDOWN-STATUS.md` (read this survey). `TK5DATA5.BIN` entry **E7 = a 72-file UI/video archive, header format CRACKED** (`[u32 count=72]` + 24 B records `[hdr][name[12]][offset][size]`): `mask.bin` (7,115,252 B), `flash.bin` (3,360,416 B), `NAMCO.ipu`, `charipu.arc` (17 × IPU character videos), `sedat.bin`, `KAZ_OP.ipu`, `###.ovb` voice banks. Stored on GitHub Release `tekken5-tk5data5-v1`.
- Held locally (samples only): `~/workspace/tk5-lanes/research/proofs/{NAMCO.ipu, char00.ipu, sedat.bin, namco_frame*.png, char00_frame15.png}` and `e5_embedded.tm2` — **288 bytes, a fragment, not a usable texture/font**. `TK5DATA0.BIN` (2.07 GB, character/model/stage data) remains encrypted (entropy 8.00). **No T5 panel/icon/font extraction exists** — E7's `mask.bin`/`flash.bin` are undecoded binaries (names suggest screen overlays, contents unverified — do not claim them as UI art).

### Tekken Tag Tournament 2 (Xbox 360) — nothing UI-shaped extracted
- `~/workspace/wh-ttt2/teardown/tekken-tag-tournament-2/{TEARDOWN.md, INVENTORY.md, ROSTER.md, STAGES.md, HEADER-LISTING.txt}`: the game is a 13,363,624,393 B 7z / STFS package; all content (incl. any UI) is inside 52 × 170,459,136 B `Data0000–Data0051` chunks + 7 large blobs, **STFS still encrypted, no inner file ever listed by name**.
- `.../extracted-small/` — 13 files only (45,056 B STFS descriptor + 12 title-update blobs 98–340 KB, opaque hex names). **UI categories: all EMPTY.**

---

## Category roll-up (Tekken front-end, all sources)

| Category | Verdict | Best real holdings |
|---|---|---|
| Panel / frame art | **EMPTY as sprites** | Only `psp_PIC1.png` (key art, 480×272) + `title.pmf` in-ISO (618,496 B). Real panels are inside `bulk_decrypted.bin` GZIP/COM containers, un-decoded. |
| Borders | **EMPTY** | No file found in any source. |
| Menu cursors / arrows | **EMPTY as files** | Code proof only: `_CURSORMOVE`, `O2Menu*` in `EBOOT.DECRYPTED.ELF`. |
| Icons | **1 extracted** | `ui/psp_ICON0.png` (144×80). (+ `ICON1.PMF` in-ISO.) T7 King costume PNGs in `gre/tekken7/king/` are character textures, not UI icons. |
| Button glyphs | **EMPTY** | No Tekken glyph sheet found. (PPSSPP's `assets/ui_images/buttons.svg` is the emulator's, not Tekken's.) |
| Fonts | **EMPTY** | `owfont` `.fnt/.ntx` referenced in EBOOT only; no extracted font for T5/T6/T7/TTT2. |
| Customization-screen textures | **EMPTY as textures** | Blocked behind GZIP decode (20/76) + GIM carving (0 carved). |
| Layout / menu data (text) | **REAL — the strongest holding** | T6: 9,440 item-name records + 120 NTXL tables (UI strings + slot categories) + 4-slot schema. T7: 16-slot schema + 21-field CSV spec + group IDs + conflicts. No pixel positions for any game. |
| Docs | **REAL** | `TEARDOWN.md`, `WIRING-INVENTORY.md`, `ui/README.md`, `tekken-customization-extraction/REPORT.md`, T7 parts survey, T6 item-table search report. |

**What a v2 builder can use TODAY:** the T7 slot/group/CSV/conflict schema + T6 item names & UI strings (real Tekken menu *content and structure*), PIC1/ICON0 as reference art, and the PPSSPP screenshots as look-reference. **What does not exist to ship:** any Tekken panel, border, cursor, glyph, font, or customization-screen texture as a file.
