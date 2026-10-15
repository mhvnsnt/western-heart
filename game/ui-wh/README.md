# Western Heart menu/UI system (`game/ui-wh/`)

This is Western Heart's own menu and UI. There are 8 screens: title, main menu, mode select, character select, VS, in-fight HUD, pause and results. Open `game/ui-wh/index.html#<screen>` from any static server. Enter moves forward, Esc goes back, and Esc in the HUD opens pause.

## Rules followed
- **Originals untouched.** `game/index.html`, `game/styles.css`, `game/assets/ui/*` and `teardown/**` are not modified. Everything here is new and derived.
- **Base art is the owner's existing menu wallpaper**, `game/assets/ui/title-bg.png`. `tools/make_wallpaper.py` derives `art/wallpaper_wh.png` from it, transformed in these steps:
  1. 16:9 crop that drops the source logo band.
  2. Heavy blur, so the source game's characters become abstract light.
  3. Indigo/crimson/gold duotone and a crimson sun disc.
  4. **Pantera rendered from his own GLB** (`lab/game/assets/pantera_leoman.glb`) as the hero.
  5. Western Heart text in Japanese styling: 西部の心 and 九つの魂・東の心・西の心.
- **No other game's characters and no AI faces.** Portraits are real Godot renders of the owner's GLB (`lab/game/tools/render_ui_portraits.gd`). Fighters without an owner model show the Pantera-GLB silhouette labelled MODEL PENDING.
- **Universe text only.** Names, souls and the Tekken body come from `CANON.md`, through `roster.js`. Canon gives no origin for anyone, so every origin reads **parts unknown**. The results quote is Pantera's line from CANON. The per-fighter kanji and the mode subtitles are UI styling and can be changed by the owner.

## Layout lineage (rebuilt, not copied)
| Screen | Built on |
|---|---|
| Title | TTT2/T6 title: big logo left, hero right, blinking PRESS START |
| Main menu | Urban Reign / TTT2 vertical list with a JP sub-label and a blurb line |
| Mode select | Def Jam / WWE mode cards |
| Character select | T6/TTT2: P1 full body left, P2 right, portrait grid in the middle, timer top right |
| VS | Def Jam / WWE diagonal split with a centre VS mark and the stage name |
| HUD | T6 long skewed bars with recoverable damage, name plates, round pips and clock, plus the Nine-Soul meter from `game/` |
| Pause | Urban Reign / Tekken boxed list |
| Results | WWE / Def Jam winner card with a stats table |

The Urban Reign `teardown/urban-reign/vgs/decoded/*.png` menus are still scrambled, because the stride/swizzle isn't solved. They couldn't be used as pixel bases, only as the layout references above.

## Rebuild and proof
```
xvfb-run -a godot --rendering-driver opengl3 --path lab/game -s res://tools/render_ui_portraits.gd -- $(pwd)/game/ui-wh/portraits
python3 game/ui-wh/tools/make_wallpaper.py
python3 -m http.server 8765 -d game &  node game/ui-wh/tools/capture.mjs docs/qa/ui-wh   # Playwright
```
Not wired into `game/main.js` yet. That's the next PR, so the existing build keeps working unchanged.
