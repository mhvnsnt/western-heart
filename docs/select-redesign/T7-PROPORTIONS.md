# Tekken 7 select proportions (measured, 2026-10-23)
Source: real T7 Scaleform textures decoded in the private repo (SW_UI_CharacterSelect / SW_UI_MainMenu / SW_UI_StageSelect, 1920x1080 authoring). No textures live in this repo.

| Element | Size (px @1080p) | Use |
|---|---|---|
| Rep_CS_CH_PANEL card | 96x148 tex, 91x129 drawn | card aspect 0.705 |
| SlotRed/Blue_OnGradient | 208x336 | P1/P2 cursor frame |
| FrontPanel | 184x316 | |
| Hatena | 68x68 | random card |
| MainMenu Base | 572x1080 | menu column = 29.8% width |
| StageSelect Base | 1920x604 | stage band = 56% height |

Phone port: `game/js/select-t7-layout.js` picks the column count giving the largest 91:129 card with all cards on screen (no scroll). Landscape = T7's 2-row full-width band; portrait = stacked block under the stage. CONFIRM is pinned in the hint bar. Last confirmed fighter per side is stored in `wh.select.last.v1` and restored on open (attire already remembered per fighter by attires.js). The base-pak SWF (layout timeline) was not pulled: 8.5 GB > free disk.

## Menus (main menu, mode select, options) — measured 2026-10-23

Structure from the T7 tkdata list tables (private repo, `teardown/tekken7-steam/tkdata/list/`):
`SW_UI_MainMenu.bin` → `MainMenu_mc.Main0..Main13` (14 text+glow slots) and `SubMenu_mc.SubMenu_Base_mc.Sub0..Sub9` (mode submenu);
`SW_UI_Option.bin` → `ListArea_mc` Title1/Title2 tabs + `List1_Panel_mc.Panel0..11` (OptionName | OptionValue).

| Element | Size (px @1080p) | Use |
|---|---|---|
| MainMenu Base_OnlineMenu | 572x1080, drawn rows 0–1004 | column 29.8% W; slot pitch 1004/14 = 71.7 px |
| PauseMenu_Replay Cursor_Sub | 688x80 | submenu 35.8% W, row 80 px (7.4% H) |
| NavigationBar_Waku | 1264x48 | help bar 48 px (4.4% H) |
| ControllerSetup PanelBase1 | 560x40 | option row 40 px |
| StoryMode_Option Win_3line | 1168x372 | option window 60.8% W |

Phone port (`game/js/menu-t7-layout.js` + `game/menu-t7.css`): landscape scales by height (s = H/1080) and keeps the column on the left at 29.8% W with the submenu beside it at 35.8% W; portrait has no 16:9 frame, and the 572x1080 column (aspect 0.53) is near a portrait phone's (0.46), so it is scaled to the full width (s = W/572). A 44 px touch floor can only grow a row. Rail items open their submenu (T7 SubMenu_mc) instead of jumping straight into a mode.

Landscape select: the fighter panes run full height behind the roster band and the body is framed to ~88% of the pane (T7 renders stand behind the cards). With no saved pick the P1 cursor starts on the first slot (Pantera, attire 1 Leo man).
