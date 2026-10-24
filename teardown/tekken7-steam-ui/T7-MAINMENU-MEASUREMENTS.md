# T7 Main Menu — measured layout data

Source: Tekken 7 Steam extraction, PR #863 branch `feat/t7-steam-extraction`
(Steam depot 389731, owner's purchase; repak + t7_decrypt.py + UModel).
Paths below are on that branch under `teardown/tekken7-steam/`.

Note on `tekken7-full-v1` release: that 3.29GB archive is a curated
models/arenas/king/tools/docs pack — it contains no UI layout data.
The Steam pakchunk0 extraction is the authoritative T7 UI source.

## 1. Menu structure — `tkdata/list/SW_UI_MainMenu.bin` (7773 bytes)

Binary string-offset table (u32 offset + u32 pad per entry) of
Scaleform/Flash display paths. Parsed 2026-10-23.

- Scene root: `_root.Menu_mc`
- **14 main buttons**: `_root.Menu_mc.MainMenu_mc.Main0` … `Main13`
  - Each: `Button_Main_Style_mc` (chrome) +
    `Button_Main_Text_mc` → dynamic text `DT_Button_MainN`
  - Each has a selected-state variant:
    `Button_Main_Style_Glow_mc` + `Button_Main_Text_Glow_mc`
    → `DT_Button_Glow_MainN`
- **10 submenu buttons**: `_root.Menu_mc.SubMenu_mc.SubMenu_Base_mc.Sub0` … `Sub9`
  - Each: `Button_Sub_Text_mc` → dynamic text `DT_Button_SubN`
  - Each has a glow variant `DT_Button_Glow_SubN`
- **News panel**: `_root.News_mc`
  - `News_L_mc`: `DT_News_L_Title`, `DT_News_L_Body`,
    `DT_News_L_Body_1line`, `DT_News_L_URL`
  - `News_S_mc`: `DT_News_S_Title`, `DT_News_S_Body`

Navigation flow (from the display list): Main menu → SubMenu →
destination, with a News panel alongside. Main items carry dynamic
text (labels are set at runtime, not baked in).

## 2. Menu column — `pakchunk0/textures/UI_common/flash/SW_UI_MainMenu/Base_OnlineMenu.png`

- Size: **572 × 1080** (aspect 0.5296 — tall left column on a 1080p frame)
- Sampled (RGBA):
  - center (286,540): `(33, 71, 88, 238)` — deep blue-teal core, ~93% opaque
  - top-center (286,30): `(30, 70, 84, 58)` — fades toward top edge
  - bottom-center (286,1050): `(0, 44, 43, 6)` — fully faded at bottom
  - left-mid (15,540): `(16, 45, 66, 9)` — faded at side edges
  - corner (40,40): `(8, 36, 66, 8)` — rounded corners, ~transparent
- Rule: **soft vertical glass column** — opaque deep blue-teal core band,
  feathered to transparent on all four edges, rounded corners.
  No hard border. The "soft blue core" is the menu's luminous center.

## 3. Companion textures (same dir)

- `GlassFlare_Blue_Line2.png`, `GlassFlare_Blue_Volume2.png` — blue
  glass highlight streaks (selection glow language)
- `Rep_BTN_S_LT_ON.png`, `Rep_BTN_S_RT_ON.png` — small button chrome caps
- `PageMark_Off.png` — page indicator dot (unselected state)

## 4. Visual grammar (measured, no Namco pixels)

- Palette: near-black blue `#0a1420` → deep teal `#214758` core →
  soft blue glow. Accent blue (select glow), white italic type.
- Type: bold italic condensed (T7's menu type is a heavy italic grotesque).
- Buttons: text-first rows; selected state = glow variant (brighter core
  + blue outer glow), not a color swap.
- Layout: left glass column holds the button list; news panel sits
  alongside; submenus replace/extend the column (SubMenu_Base).

## 5. Phone adaptation rules used by the WH rebuild

- T7's 572×1080 column (0.53 aspect) → portrait: full-width vertical
  glass column; landscape: left column at ~min(46vw, 430px).
- 14 main-button capacity → WH uses 7 (Fight, Story·Arcade,
  Training·Gungaku, Customization, Gallery, Options, Online).
- 10 sub-button capacity → WH submenus (story ≤ 8 cards, others ≤ 4).
- 44px minimum tap target (phone law) applied to every button.
- Touch: Pointer Events (`pointerdown`/`pointerup` + `setPointerCapture`,
  `touch-action: manipulation`). No hover-dependent UI.
