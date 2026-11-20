# Tekken 7 UI layout notes (measured, no Namco pixels)

Source: the Tekken 7 Steam extraction on PR #863 (branch `feat/t7-steam-extraction`),
`teardown/tekken7-steam/pakchunk0/textures/UI_common/flash/` plus
`teardown/tekken7-steam/tkdata/list/SW_UI_*.bin`. The raw textures are Bandai Namco
property: they belong in the private repo `mhvnsnt/game-reverse-engineering`,
NOT in this public repo. This file records only sizes, colours and layout rules,
which `game/t7-skin.css` reproduces with CSS for the public build. Private builds
load the real files via `game/js/t7-ui-private.js` (`__WH_PRIVATE_ASSETS`).

| Texture (flash/...) | Size | Used for | Rule reproduced |
|---|---|---|---|
| SW_UI_CharacterSelect/Rep_CS_CH_PANEL_00..09.png | 96x148 | roster card | card aspect 96:148, portrait bust, number bottom-right |
| SW_UI_CharacterSelect/SlotRed_OnGradient.png | 208x336 | P1 cursor | red (#e0182a) double frame, gradient up from bottom |
| SW_UI_CharacterSelect/SlotBlue_OnGradient.png | 208x336 | P2 cursor | blue (#1a8cff) double frame, gradient up from bottom |
| SW_UI_CharacterSelect/PanelRed_Full_Base.png / PanelBlue_Full_Base.png | 108x292 | side panels | P1 red left, P2 blue right |
| SW_UI_CharacterSelect/Hatena_Red.png | 68x68 | random card | red "?" glyph |
| SW_UI_StageSelect/InfoRed_Base.png | 420x656 | stage info | navy->black gradient panel, red 1px rim, notched corner |
| SW_UI_StageSelect/RedPanel_Base.png | 1180x696 | stage panel (selected) | same gradient, red rim + glow |
| SW_UI_Result_Lightning/Result_Lightning_02.png | 400x580 | win screen | vertical blue-white bolt behind huge italic WIN |
| SW_UI_MainMenu/Base_OnlineMenu.png | 572x1080 | main menu column | dark glass vertical list, soft blue core |

Panel gradient sampled from InfoRed_Base: #1b2740 (top) -> #0d1322 (55%) -> #04060a.
