# Submenu rebuild: versus setup (2026-10-23)

## Owner instruction (verbatim)
> "NO hand-tooled menus. EVER. Every menu in the game gets rebuilt FROM the teardown files of actual Tekken games (T5/T6/T7/TTT2, T8 when it lands) and other games' teardown UI."
> Task: rebuild ALL submenus from Tekken's actual UI — 1. Versus setup (rules, rounds, time, stage select).

## Source
Tekken 7 / arcade GAME OPTION table (manuals.plus TTT operators manual):
DIFFICULTY LEVEL (EASY/MEDIUM/HARD/VERY HARD/ULTRA HARD), FIGHT COUNT
<1P GAME> 1-5, FIGHT COUNT <VS GAME> 1-5, ROUND TIME 30/40/60/80/90/99,
GUARD DAMAGE ON/OFF. T7 console adds INFINITY round time and VERY EASY.

## What was built (PR #832, branch worker-submenus/versus-setup)
- `game/js/rules.js` — standalone match-rules store `wh_rules_v1`
  (difficulty, rounds1p, roundsVs, roundTime 0=∞, guardDamage, stageMode).
- `game/js/versus-setup.js` + `#screen-vssetup` — T7 option-list screen:
  FIGHT COUNT 1-5, ROUND TIME 30/40/60/90/99/∞, GUARD DAMAGE ON/OFF,
  STAGE SELECT/RANDOM. Shared T7 styles in `game/submenus.css`.
- `modes.js` `_beginVersus` passes roundsToWin/roundTime/guardDamage
  into the fight; STAGE=RANDOM skips the arena screen.
- `game.js` honors per-match roundTime/guardDamage; `fighter.js`
  zeroes chip when guard damage is OFF; round pips rebuild to the
  round target; timer renders ∞.
- Fixed routing conflict: the legacy data-mm router in main.js fired
  on rail taps alongside the T8 submenu controller, making every
  submenu unreachable. Rail items now yield to the submenu controller.

## Verification
- 7/7 menu harness checks (every option tapped, localStorage asserted,
  tap targets ≥48px measured, back navigation).
- 10/10 fight-integration checks (captured fight opts carry the rules;
  HUD pips/∞ timer proven).
- Screenshots viewed: menu, versus submenu, versus setup, all-set, fight.
- gitleaks clean. 8 files modified + 3 new, 0 deletions.

## Follow-ups (own branches)
- PR2: OPTIONS rebuild (T7 GAME OPTION / CONTROLLER SETUP / SOUND / DISPLAY tabs)
- PR3: mode setup sheets (arcade/survival/time attack/team battle options)
- PR4: gallery (T5 theater + TTT2 gallery: movies/art/unlockables)
- PR5: jukebox (TTT2 Tekken Tunes: stage/menu music assignment)
