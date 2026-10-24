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
