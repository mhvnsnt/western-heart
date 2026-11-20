# WWE + Def Jam Front-End Asset Inventory — for Western Heart Creation Suite UI v2

Survey date: 2026-10-21 · READ-ONLY survey (nothing copied, nothing modified except this file + its JSON twin)
Disk at survey time: 95% used (5.2G free on /home/hatch) — all counts are listings, no bulk copies were made.

## Bottom line (read this first)

| Game | Front-end / menu / CAW-screen art actually held | Verdict for skinning the WWE side of CSUI v2 |
|---|---|---|
| **WWF No Mercy (N64)** | **429 menu/UI PNGs** in one named ROM texture dump + 64 menu-scene textures + 6 CAW edit-mode tab icons — **repo-only, not on local disk** | **THE source.** Real main-menu, character-select, match-menu, arena-menu, edit-mode (CAW) tab, portrait/icon, HUD and message art. Must be pulled from `mhvnsnt/western-heart` `teardown/wwf-no-mercy/textures/rom/…` — it is in neither local WH copy checked. |
| **WrestleMania XIX (GC)** | **0 front-end files out of 1,477 decoded textures.** All 1,477 are Create-A-Wrestler *part* textures (face/hair/clothes). Separate arena set (1,167 PNG) contains only 7 arena-signage `logo_*.png`, no menus/fonts/icons/cursors. | Nothing to skin a menu with. Its value to the suite is part textures + face-paint/makeup overlays (`Face_op`, 208) as *content*, not chrome. |
| **Def Jam: Fight for NY (PS2)** | **0 front-end files extracted anywhere.** The ISO has `SCREENS/` + `FONTS/` root folders (documented), but they were **never extracted**; the ISO itself is not on local disk. Everything extracted/converted is fighter + create-player *part* data. | EMPTY for front-end. Extraction is possible in principle (surgical range extraction was used for the rest; tools in `defjam-work/tools/`) but is new work, not an inventory pull. |
| General packs | No standalone wrestling UI font/icon pack exists in the searched places. Only: No Mercy **recomp-project** icons/fonts (not original game assets) and Western Heart's own Oswald font. | `promptfont.ttf` (button-prompt glyphs, recomp) is the only button-glyph font found anywhere. |

Corroboration from the suite's own log (`_w7b-wh/customization/creation-suite-ui/UI-EXTRACTION-LOG.md`, §4–§6): *"The actual `.uasset` menu-layout binaries and UI pixel layouts are NOT in any teardown we hold… WWE 2K game files are NOT on disk… The UI's visual design is original."* That remains true for Tekken/WWE 2K — but the No Mercy ROM dump below **is** real menu pixel art and predates/postdates that log's IA-only use of No Mercy (it only cited the re-docs menu descriptions).

---

## How everything was counted

- **Repo (remote) evidence:** `~/workspace/_fighter-completeness/tree.json` — a captured GitHub git-tree listing of `mhvnsnt/western-heart` main, sha `bc37997fe03ace4c384eac4fab180e74f40f1c7b`, 60,836 entries, API flag `truncated: true`. All repo counts below are blob counts from that file, computed with Python `collections.Counter` over path prefixes. Caveat: because the tree is truncated at the API limit, repo counts are a **floor** for the repo as a whole; the subtrees itemised here are internally consistent (e.g. WMXIX decoded count 1,477 matches `WMXIX-TEX-REMAINDER-REPORT-2026-10-20.md` and `CATALOG.json`'s "1,044 → 1,477" exactly).
- **Local-disk evidence:** `os.walk` file counts (excluding `.git`) on each named folder, run 2026-10-21. Local WH copies are **sparse/partial checkouts** — they do not mirror the full repo, which is why "repo" and "on disk" are reported separately throughout.
- Local copies checked in depth: `~/workspace/_fighter-completeness/main/` (195 files total), `~/workspace/_w7b-wh/` (10,342 files, customization/docs/packages only — **no `teardown/`, no `game/`**), `~/workspace/_j3-work/wh/`, `~/workspace/_wh-work/personality-pass/`, `~/workspace/wh-lane2-fighters/`, plus the five Def Jam folders named in the task.

---

## 1. WMXIX — WrestleMania XIX

### 1a. The ~1,477 decoded textures — classification

- **Source (undecoded) in repo:** `customization/parts/wmxix/textures/` — **1,478 files**: 1,470 `.tex` (TPL containers) + 2 `.tga` + 2 `.tpl` + 2 `.psd` + 1 `.tm2` + 1 `.tpg`, same `TEX/<Category>/` layout.
- **Decoded in repo:** `customization/parts-converted/wmxix-textures/` — **1,477 PNG** (1 per source texture; first TPL entry per container, per the remainder report) **+ 1 contact sheet** (`customization/parts-converted/contact-sheet-wmxix-textures.png`) = 1,478 PNG blobs under the `wmxix-textures` search term.
- **On local disk:** the full decoded set **is** present at `~/workspace/_w7b-wh/customization/parts-converted/wmxix-textures/` — counted **1,478 PNG** on disk (9.3 MB). It is **absent** from `~/workspace/_fighter-completeness/main/` (that copy's `customization/parts/` contains only `no-mercy/` and `tekken7/`; total PNGs in that copy = 1, the eye-library sample).
- **Naming pattern:** opaque index codes, no semantic names — `ti0_###` / `tm0_###` (Face), `ta#_###` (Face_op), `tu#_###` (Upper_Body), `tc#_###` (Lower_Body), `tz0_###` (Gears), `ty2_###` (64gara), `tb0_###` / `tt0_###` / `tx0_###` (common).

Decoded PNG breakdown by folder (blob counts from tree.json; sums to 1,477):

| Folder | Count | What it is |
|---|---:|---|
| `TEX/Face/` | 351 | CAW face/skin textures |
| `TEX/Face_op/` | 208 | Face-paint / makeup **overlays** (on-face decals — closest thing to appearance content, still not menu art) |
| `TEX/Upper_Body/` | 218 | CAW tops |
| `TEX/Gears/` | 149 | CAW gear/accessory textures |
| `TEX/Lower_Body/` | 142 | CAW bottoms |
| `TEX/Shoes/` | 84 | CAW footwear |
| `TEX/Hair/` | 70 | CAW hair |
| `TEX/Wrist/` | 60 | CAW wristbands/tape |
| `TEX/Gloves/` | 50 | CAW gloves |
| `TEX/common/` | 50 | Shared: `blood.png`, `gouraud0–4.png` shading ramps, `tb0_*` body, `tt0_*` tattoo, `tx0_*` |
| `TEX/64gara/` | 41 | CAW textures (opaque `ty2_*` codes; the formerly "blocked_no_tpl" C8 set) |
| `TEX/Knee/` | 24 | CAW knee pads |
| `TEX/Elbow/` | 22 | CAW elbow pads |
| `Woman/Face/` | 8 | Female face set (incl. the `tq0_417` TPL/TGA/TM2/PSD decodes) |
| **Total** | **1,477** | |

**Front-end subset (menu backgrounds, panels/frames, CAW-screen art, icons, cursors, button glyphs, fonts, category icons): 0 of 1,477.**
In-ring/character/arena split for this set: character/CAW-part = 1,477 (100%), in-ring/arena = 0, front-end = 0. A keyword sweep (`menu|frontend|front-end|/ui/|font|logo|icon|cursor|hud`) over every WMXIX path in the repo tree returned only the 7 arena logos in §1b.

10 representative decoded files (they demonstrate the classification — there are no front-end files to exemplify):

1. `customization/parts-converted/wmxix-textures/TEX/Face/ti0_000.png`
2. `customization/parts-converted/wmxix-textures/TEX/Face/tm0_000.png`
3. `customization/parts-converted/wmxix-textures/TEX/Face_op/ta0_000.png`
4. `customization/parts-converted/wmxix-textures/TEX/Hair/tk0_000.png`
5. `customization/parts-converted/wmxix-textures/TEX/Upper_Body/tu0_000.png`
6. `customization/parts-converted/wmxix-textures/TEX/Lower_Body/tc0_000.png`
7. `customization/parts-converted/wmxix-textures/TEX/Gears/tz0_000.png`
8. `customization/parts-converted/wmxix-textures/TEX/common/blood.png`
9. `customization/parts-converted/wmxix-textures/TEX/64gara/ty2_000.png`
10. `customization/parts-converted/wmxix-textures/Woman/Face/tq0_417/c3_c_00.png`

(All 10 are verbatim blob paths from the tree listing and are also the WMXIX entries in the JSON twin.)

### 1b. WMXIX arena textures (separate set — not front-end either)

- Repo: `teardown/wmxix/textures/` — **1,169 files** (1,167 PNG + `README.md` + `TEX-MANIFEST.txt`), grouped by arena ID: `00` 75, `02` 54, `0_0` 63, `0_1` 66, `0_2` 73, `0_3` 69, `1_0` 63, `1_1` 76, `1_2` 76, `1_3` 76, `1_4` 76, `2_0` 109, `2_1` 110, `2_2` 98, `5_0` 2, `5_1` 8, `f01` 4, `kaijo_x8` 55, `ring` 14.
- On disk in full at `~/workspace/_j3-work/wh/teardown/wmxix/textures/` (1,169 files counted).
- Only logo-named files (7, all **arena signage**, e.g. entrance/set dressing — not menu art): `teardown/wmxix/textures/0_0/logo_01.png`, `0_1/logo_01.png`, `0_2/logo_01.png`, `0_2/logo_02.png`, `0_2/logo_03.png`, `0_3/logo_01.png`, `2_2/logo.png`. All 7 are listed individually in the JSON twin.
- Also in repo: `customization/parts/wmxix/` holds 1,200 undeciphered `.ymg` CAW meshes + faces/gears/hair/etc. (geometry, not UI) and `teardown/wmxix/` animations/arenas/wrestlers — no UI material.

### 1c. WMXIX fonts / icons / cursors / button glyphs

**EMPTY.** No `.ttf/.otf/.fnt`, no icon, cursor or glyph files under any WMXIX path in the repo tree or on disk.

---

## 2. WWF No Mercy

### 2a. The ROM texture dump — front-end subset (THE find)

Repo path: `teardown/wwf-no-mercy/textures/` — **1,792 files** (1,791 PNG + `inventory.json`):

- `textures/rom/` — 1,441 PNG, organised by **semantic folder name** (human-readable filenames, e.g. `Main_Menu_Exhibition_4487.png` — the trailing hex is the ROM offset)
- `textures/characters/` — 286 PNG (13 wrestlers' in-ring textures)
- `textures/environments/` — 64 PNG = `main-menu-scene/` 32 + `menu_scene/` 32 (generic `Image_N.png` names; textures of the 3D menu/lobby scene)

Front-end classification of the 1,441 `rom/` PNGs:

| Category | Folder | Count | Examples |
|---|---|---:|---|
| Character icons (select-grid faces) | `rom/character_icon/` | 102 | `Character_Icon_Al_Snow_4AF9.png`, `Character_Icon_AKI_man_4B51.png` |
| Character portraits | `rom/character_portrait/` | 101 | `Character_Portrait_Al_Snow_45D9.png` |
| Arena-menu art (PPV/arena pics + names) | `rom/arena_menu/` | 70 | `Arena_Menu_Armageddon_4634.png`, `Arena_Menu_Armageddon_Pic_1_465F.png` |
| Lobby (menu-area scene textures) | `rom/lobby/` | 31 | `Lobby_Black_Box_2D8D.png` |
| HUD large messages (Count Out / Two / … frame anims) | `rom/large_message/` | 28 | `Large_Message_Count_Out_frame_1_037A.png` |
| Character-select UI (1P/2P/CPU markers, glows, squares, VS icon, L/R icons, banners) | `rom/character_select/` | 26 | `Character_Select_1P_45A2.png`, `Character_Select_1P_Glow_45A3.png`, `Character_Select_VS_icon_459E.png`, `Character_Select_Glowing_Character_Square_459D.png` |
| Attitude meter (HUD) | `rom/attitude_meter/` | 14 | `Attitude_Meter_COM_Left_0348.png`, `Attitude_Meter_Danger_0350.png` |
| Lobby TV screen (menu scene) | `rom/lobby_tv_screen/` | 10 | `Lobby_TV_Screen_No_Mercy_Normal_2DD3.png` |
| Championship menu | `rom/championship_menu/` | 10 | `Championship_Menu_Belt_4629.png`, `Championship_Menu_European_461B.png` |
| **Main menu** | `rom/main_menu/` | **8** | `Main_Menu_Exhibition_4487.png`, `Main_Menu_Championship_448E.png`, `Main_Menu_Guest_Referee_448B.png`, `Main_Menu_Ironman_Match_4492.png`, `Main_Menu_King_of_the_Ring_448A.png`, `Main_Menu_Ladder_Match_448C.png`, `Main_Menu_Options_4490.png`, `Main_Menu_Header_border_4483.png` (a panel/border frame) |
| **CAW edit-mode tabs** | `rom/edit_mode_tabs/` | **6** | `Edit_Mode_Tabs_ProfileMusic_4A39.png`, `Edit_Mode_Tabs_Appearance_4A3B.png`, `Edit_Mode_Tabs_Moves_4A3D.png`, `Edit_Mode_Tabs_Fighting_Style_4A3F.png`, `Edit_Mode_Tabs_Parameter_4A41.png`, `Edit_Mode_Tabs_AllyEnemy_4A43.png` — **literal Creation-Suite category icons** |
| Exhibition menu | `rom/exhibition_menu/` | 5 | `Exhibition_Menu_Single_Match_44A1.png`, `Exhibition_Menu_Cage_Match_44A5.png` |
| Ironman match menu | `rom/ironman_match_menu/` | 4 | `Ironman_Match_Menu_Ironman_Single_44AD.png` |
| Ladder match menu | `rom/ladder_match_menu/` | 4 | `Ladder_Match_Menu_Ladder_Single_44A6.png` |
| Guest referee menu | `rom/guest_referee_menu/` | 3 | `Guest_Referee_Menu_Referee_Single_44AA.png` |
| Battle royal menu | `rom/battle_royal_menu/` | 2 | `Battle_Royal_Menu_Select_44B2.png`, `Battle_Royal_Menu_Random_44B1.png` |
| Belt menu | `rom/belt_menu/` | 2 | `Belt_Menu_Non_Title_Match_4628.png`, `belt_menu/champsionship/Belt_MenuChampsionship_Belt_Background_458D.png` (a menu background) |
| Menu backgrounds | `rom/background/` | 2 | `Background_Pay_Per_View_40_4844.png`, `Background_KORTournament_40_457B.png` |
| Font glyph sheet | `rom/large_font/` | 1 | `Large_Font_Backlash_4482.png` (single PPV-name glyph sheet — the only No Mercy "font" texture; no full alphabet/font file) |
| **Front-end subtotal** | | **429** | (388 strict menu/select/icon/HUD/font + 31 lobby + 10 lobby-TV) |
| + menu-scene environment textures | `textures/environments/` | 64 | `main-menu-scene/Image_0.png` … `Image_31.png`, `menu_scene/Image_0.png` … |
| **Front-end total held** | | **493** | all PNG |

The remaining ~1,012 `rom/` PNGs are CAW-part and in-ring content (body 233, face 146, boots 125, arena 127, intro 49, hair 49, front_hair 62, locker_room 31, lounge 38, facial_hair 30, hat 16, elbow_pad 14, gloves 13, hallway 10, belt 9, austin_coin 8, data 8, entrance attire/weapons, pads, clone, king_of_the_ring 1, backstage 1) — content for the suite, not chrome.

**All 429 + 64 front-end PNGs are enumerated individually in the JSON twin.**

### 2b. Where the No Mercy front-end art physically is — LOCAL DISK GAP

- **Repo only.** Neither local WH copy contains it: `_fighter-completeness/main/` has no `teardown/` at all; `_w7b-wh/` has no `teardown/` at all. A coordinator pull must fetch `teardown/wwf-no-mercy/textures/rom/{main_menu,edit_mode_tabs,character_select,character_icon,character_portrait,arena_menu,…}` from `mhvnsnt/western-heart`.
- Partial No Mercy material on local disk at `~/workspace/_wh-work/personality-pass/teardown/wwf-no-mercy/` — **60 files, docs/tools only**: `docs/` (7, incl. `CAW-EDIT-DATA.md`, `caw-categories.json`), `re-docs/docs/ui/menus/{main-menu,edit-a-superstar,superstar-select}.md` + `re-docs/docs/ui/ui.md` (menu *descriptions*, also in repo), `recomp/docs/screenshots/{title,wrestler-select,gameplay}.png` (3 recomp screenshots — reference stills of the title/select screens, not extractable art), `recomp/tools/`, `tools/`. No `textures/`, no `recomp/assets/` in that copy.
- No standalone N64 texture pack exists elsewhere in the workspace: a `*Mercy*` glob at workspace depth 1–2 returned nothing, and every No Mercy path found lives inside a western-heart clone (`teardown/wwf-no-mercy/` or `customization/parts/no-mercy/`).

### 2c. No Mercy CAW parts on local disk (not UI — for completeness)

- `~/workspace/_fighter-completeness/main/customization/parts/no-mercy/` — just 2 files on disk: `CATALOG.json` + `glb/body_parts/model_1171.glb`.
- `~/workspace/_w7b-wh/customization/parts/no-mercy/` — 1,292 files (303 GLB + 303 OBJ + 303 `.vc` + 379 PNG + catalogs); `parts-converted/no-mercy/` — 303 GLB. The 379 PNGs are face/skin part textures (`faces/Face_1E6F.png`, `Face_Austin_1E7F.png`, … in repo layout), **not** UI.
- `~/workspace/wh-lane2-fighters/customization/parts/no-mercy/` — 986 files, same family.

### 2d. No Mercy recomp-project UI assets (in repo — NOT original game assets)

Under `teardown/wwf-no-mercy/recomp/` (the N64-recompilation project's own UI, provenance differs from the ROM dump — flag before reusing as "game art"):

- `recomp/assets/icons/` — **22 SVG icons**: `Arrow, Caret, Cont, Keyboard, Plus, PlusKeyboard, Port, Question, Quit, RecordBorder, RecordSpinner, Reset, Trash, X` + `VizMap/{ButtonLarge, ButtonMedium, ButtonSmall, DPad, DPadArrow, Map, Shield, Target}.svg` (button glyphs / controller-prompt art)
- `recomp/assets/promptfont/promptfont.ttf` — button-prompt glyph font (+ LICENSE/README)
- `recomp/assets/InterVariable.ttf`, `recomp/assets/NotoEmoji-Regular.ttf` — recomp UI fonts
- `recomp/assets/recomp.rcss`, `recomp/icons/{app.ico, app.png, logo.png}`
- `re-docs/assets/3d Assets/environments/{main-menu-scene,menu_scene}.glb` — 2 menu-scene models

All except the 4 re-docs UI markdown files are repo-only in the copies checked. Every one of these is enumerated in the JSON twin.

---

## 3. Def Jam: Fight for NY

### 3a. What was searched (all local, counted with `os.walk`)

| Folder | Files | Contents | Front-end |
|---|---:|---|---|
| `~/workspace/defjam-work/` | 273 | `surgical/chars/` 234 (`.o`+`.ssh` V2IP fighter SHPS/EAGL), `surgical/xml/` 10, `surgical/motion/` 2, `tools/` 9, docs/logs; **`iso/` = 2 log files only — no ISO** | **0** (0 PNG, 0 TXD; filename keyword sweep for menu/ui/font/icon/logo/select/title/hud = 0 real hits) |
| `~/workspace/defjam-lane/` | 75 | 67 `.ssh` in `meta_ssh/` (`V2CP_*` create-player part containers), `PARTS-INDEX.json`, `createplayer_parts.xml.bin`, `cp_def0–3.xml.bin`, `parts-blob.b64` (9.4 MB) | **0** |
| `~/workspace/defjam-repo/` | 8 | `AGENTS.md` + `lane-logs/` only — no assets at all | **0** |
| `~/workspace/urban-reign-defjam-research/` | 1 | `RESEARCH_REPORT.md` only | **0** |
| `~/workspace/wrestling-work/` | 12 | 6 wrestling-move FBX + 6 JSON (animation, not Def Jam UI) | **0** |
| WH repo `teardown/def-jam-fight-for-ny/` | 268 (repo tree) | Same surgical set (234 chars, 10 XML, tools, docs) + 3 `sample-renders/*.png` (failed/point-cloud **model** renders — not FE) | **0** |
| `~/workspace/_w7b-wh/customization/parts-converted/defjam/` (on disk) | **3,402** | 2,182 PNG + 1,218 GLB + `CATALOG.json` + 1 MD: `accessories` 150, `head` 5, `lower_body` 81, `upper_body` 624, `unknown` 2,519, `samples` 22 | **0** — every PNG is a texture paired to a `V2CP_*` create-player part GLB (e.g. `accessories/V2CP_113_0001_A.png` + `.glb`) |

### 3b. The unextracted front-end (the honest gap)

`~/workspace/defjam-work/TEARDOWN.md` (disc layout, from the ISO9660 listing of SLUS_210.04) records the ISO root as containing:

> `SCREENS/` `FONTS/` `IOP/` — "Frontend, fonts, IOP modules"

Neither folder was ever range-extracted (the surgical extraction took fighters, CAW parts `V2CP_*.VIV`, motion, XML, audio tags only), and no file from either folder exists in any folder in §3a or in the WH repo tree. The 4.69 GB ISO is not on local disk (`defjam-work/iso/` holds only `pypdl.log` + `assemble.log`); the teardown doc gives its source as Internet Archive item `slus-210.04.-def-jam-fight-for-ny`. Both folders are carried in the JSON twin as explicit `NOT EXTRACTED` entries so the gap is machine-visible.

**Def Jam front-end verdict: EMPTY (0 files held), with a documented extraction target (`SCREENS/`, `FONTS/` on the FFNY ISO).**

---

## 4. General wrestling-game UI font / icon packs

Searched in all places above plus the full WH repo tree (font extension sweep `.ttf/.otf/.fnt` over 58,392 blobs):

- **No standalone wrestling UI font/icon pack exists** in any searched location.
- Fonts found (none are wrestling-game rips): `western-heart/game/ui-wh/fonts/Oswald-VariableFont_wght.ttf` (Western Heart's **own** UI font, repo-only in the copies checked — `_w7b-wh` has no `game/`), the No Mercy recomp fonts in §2d, and Tekken 3 recomp-project fonts under `teardown/tekken3/tools/…` (not wrestling, not game-original).
- WWE 2K CAW: `customization/wwe2k-caw/` in WH = **9 research documents only** (`CAW-SUITE-BREAKDOWN.md`, `COMBINED-CREATION-SUITE.md`, `PULL-PLAN.md`, etc.) — 0 assets; per `PULL-PLAN.md` / UI-EXTRACTION-LOG §4 the 51 GB game pull never landed, so no WWE 2K menu art, fonts or icons exist anywhere in the repos.
- The existing Creation Suite UI (`customization/creation-suite-ui/`, 26 files on disk in `_w7b-wh`: HTML/CSS/JS + 2 proof screenshots + demo MP4) is **original visual design** with menu *information architecture* transcribed from game data files — it contains no ripped WWE/Wrestling front-end art to reuse as a skin.

---

## 5. Recommendation implied by the inventory (facts only)

1. Skinning material that exists **today, as pixels**: No Mercy only — 429 ROM menu/UI PNGs + 64 menu-scene PNGs, incl. the 6 edit-mode (CAW) tab icons and 8 main-menu tiles that map 1:1 onto Creation Suite sections. All require a pull from `mhvnsnt/western-heart` (`teardown/wwf-no-mercy/textures/…`); they are not in any local checkout surveyed.
2. WMXIX contributes **content, not chrome**: 1,477 CAW part textures already on disk in `_w7b-wh` (incl. 208 face-paint overlays usable as appearance thumbnails/decals).
3. Def Jam front-end is a **new extraction job** (`SCREENS/` + `FONTS/` from the FFNY ISO), not a pull — budget it as such or mark the Def Jam section of CSUI v2 as unskinned.

## Files

- This report: `~/workspace/_csui-v2-work/survey/wwe-defjam-frontend-inventory.md`
- Machine list (546 entries: 524 No Mercy / 18 WMXIX / 4 Def Jam incl. the 2 NOT-EXTRACTED gap entries): `~/workspace/_csui-v2-work/survey/wwe-defjam-frontend-inventory.json`
