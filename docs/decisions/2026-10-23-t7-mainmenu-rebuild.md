# T7 main menu rebuild — decision log (2026-10-23)

## Owner directive
MAJOR SHIFT: T7 is the source for the main menu (not T8). Measure T7's
actual main menu from its layout data. Phone-first (portrait + landscape),
44px tap targets, Pointer Events touch. 7 options: Fight, Story/Arcade,
Training/Gungaku, Customization, Gallery, Options, Online — each wired to
a real destination, no dead ends. Verify by playing.

## T7 source data (measured, not guessed)
- `teardown/tekken7-steam/tkdata/list/SW_UI_MainMenu.bin` (7773 bytes) from
  PR #863 branch `feat/t7-steam-extraction` (T7 Steam depot 389731):
  14 Main buttons (`_root.Menu_mc.MainMenu_mc.Main0..13`, each Style +
  Text + Glow variant), 10 Sub buttons (`SubMenu_mc.Sub0..9`),
  News panel (`News_mc`: News_L large + News_S small).
  Navigation flow: Main -> SubMenu -> destination.
- `teardown/tekken7-steam/pakchunk0/textures/UI_common/flash/SW_UI_MainMenu/Base_OnlineMenu.png`
  (572x1080): dark glass column, core RGB(33,71,88)@93%, feathered to
  transparent edges, rounded corners. "Soft blue core."
- Full measurements: `teardown/tekken7-steam-ui/T7-MAINMENU-MEASUREMENTS.md`.

## Deviation: tekken7-full-v1 release not downloaded
The task named the 3.29GB `tekken7-full-v1` release as the source. Its
release notes list contents as models/arenas/king/tools/docs — no UI
layout data. The PR #863 Steam pakchunk0 extraction IS T7's real files
(owner's Steam purchase) and contains the actual menu layout (.bin) and
textures, so it was used instead. No 3.29GB download was needed.

## Design decisions
1. **7 top-level items** per the task: FIGHT (versus), STORY·ARCADE,
   TRAINING·GUNGAKU, CUSTOMIZATION (creation suite), GALLERY,
   OPTIONS, ONLINE. Arcade + side-games cards merged into the story
   submenu (T7's SubMenu has 10 slots; story uses 9). Daily Challenges
   (forge-only) dropped from the rail — not a real destination.
2. **T7 Main->Sub flow**: FIGHT and CUSTOMIZATION go direct (FIGHT ->
   character select, preserving the e2e contract); the other five open
   T7-style glass submenus. Fixed the main.js data-mm router which was
   firing direct navigation alongside the submenu controller (the bug
   that made submenus unseeable).
3. **Visual**: T7 blue glass (measured #214758 core, #0a1420 abyss,
   #7fb8d9 glow) replaces T8 crimson. Selection = glow variant
   (brighter core + blue outer glow), per T7's Button_Main_Style_Glow.
4. **Touch**: Pointer Events press feedback (pointerdown/up/cancel +
   setPointerCapture, `.pressing` class) on all menu controls;
   activation on click with `touch-action: manipulation`. No
   preventDefault on pointerdown (scroll gestures preserved via
   pointercancel). No hover UI. 44px+ targets (52px rail, 48px+ controls).
5. **Phone**: portrait = full-width glass column; landscape = T7 left
   column (min(46vw, 430px), T7's 0.53 aspect).

## Files
- game/index.html — 7-item nav, T7 section comment
- game/mainmenu.css — T7 blue-glass re-skin (class names unchanged)
- game/js/mainmenu.js — consolidated SUBMENUS, pointerPress helper
- game/js/main.js — data-mm router: only versus navigates direct
- game/ui_sources.json — screen-menu cites T7-MAINMENU-MEASUREMENTS.md
- teardown/tekken7-steam-ui/T7-MAINMENU-MEASUREMENTS.md — new
- docs/decisions/2026-10-23-t7-mainmenu-rebuild.md — this file

## Verification
- node --check on both JS files: clean.
- ui-sources gate: screen-menu sourced, all changed UI files listed.
- Playwright touch e2e (iPhone 13, 390x844, hasTouch): tap every item,
  screenshot every screen — see PR proof.
