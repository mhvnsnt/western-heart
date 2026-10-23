# CRITICAL-PATH STATUS — Western Heart playable loop
Worker 52 (flow QA) · started 2026-10-22 ~15:44 CDT · main @ 2af4328 (merge of #657)

Playable path: MAIN MENU → character select → stage select → fight boots →
fight plays (rounds) → result → back to menu / rematch.

## Legend
- 🟢 GREEN — verified on current main (code-read + logic proof; live-browser steps below for a browser-capable agent)
- 🔴 RED — broken on current main, blocks the path
- 🟡 YELLOW — gap / risk, not currently blocking
- ⬜ TOMORROW — off the playable path (PLAYABLE TODAY directive 15:42 CDT)

## Status board (2026-10-22 ~16:00 CDT)

| Leg | Status | Notes |
|-----|--------|-------|
| Main menu renders (styled, tappable) | 🟡 PARTIAL | `mainmenu.css` link fixed by #677 (merged); `show()` throw still kills all taps (P0-1 below) |
| Menu → VERSUS submenu | 🔴 RED | Blocked by `show()` throw (`startMode` → `this.show('select')`) |
| Character select (grid, preview, confirm) | 🔴 RED | Blocked by `show()` throw; code + CSS otherwise coherent |
| Stage select (grid, random, confirm) | 🔴 RED | Blocked by `show()` throw; `updateStagePreview` targets preview-pane IDs absent from markup (🟡 no crash — null-guarded) |
| Fight boots (models, movesets, HUD) | 🔴 RED | Blocked by `show()` throw; `startFight` load chain coherent, error surfaces on stage hint |
| Fight plays (rounds, timer, K.O.) | 🟡* | `game.js` round arbiter coherent; *unreachable until P0s fixed |
| Result screen → REMATCH / MAIN MENU | 🟡* | Wiring coherent (`rematch` → stage select; `back-menu` → `leaveFight` + `show('menu')`); *unreachable until P0s fixed |
| Touch controls (joystick + LP/RP/LK/RK/S/B/D/V) | 🟡* | `input.js` binds `.act-btn` touch/pointer; *unreachable until P0s fixed |

## P0 findings

### P0-1 · `show()` throws TypeError on EVERY screen navigation — the "NOTHING is tappable" root cause (STILL OPEN on main)
- **File/line:** `game/js/main.js:38` — `stageIntro: document.getElementById('screen-stage-intro')` → **null**
- **Why null:** `game/index.html` has TWO `<section id="screen-stage">` (line 214 = Lane-4 stage select, line 320 = story stage intro). PR #666 renamed the story one to `screen-stage-intro`; PR #657's stale-base merge reintroduced the duplicate (the PR-#579 clobber pattern).
- **Blast radius:** `show()` runs `Object.values(screens).forEach(s => s.classList.remove('active'))` → throws on the null entry → every `show()` call dies: menu→select, select→stage, stage→HUD, HUD→result, result→menu, story intro. The static menu still renders (it's `active` in HTML) but no tap can ever navigate.
- **Fix (1 line, worker-52 PR):** `game/index.html:320` `<section id="screen-stage" class="screen">` → `<section id="screen-stage-intro" class="screen">` (restores #666).

### P0-2 · Main menu rendered unstyled — FIXED on main by PR #677
- `game/mainmenu.css` (14 KB, all `.mm-*` T8 menu styles from #655) existed but was never linked → browser-default buttons ("white text boxes").
- Fixed 2026-10-22 by PR #677 (`fix/mainmenu-css-link-20261022`): added `<link rel="stylesheet" href="mainmenu.css" />`. Verified present on current main.

## P1/YELLOW (not blocking the path — lane owners, no action taken)

1. **Stage-select preview pane absent.** `main.js` `updateStagePreview()` targets `#stage-preview-img`, `#stage-preview-swatch`, `#stage-preview-name`, `#stage-preview-universe`, `#stage-preview-desc` — none exist in `index.html`. All calls null-guarded → no crash, but the "large preview pane" the comments describe isn't in the markup. → worker 51 (stage lane).
2. **Versus REMATCH routes through stage select** (`modes.js` `rematch()` → `_beginVersus` → `startFightViaStage`). Tekken convention is instant rematch; current behavior is a deliberate-looking flow, not a bug. Flagging for owner preference.
3. **PR #676** (`worker36/menu-fix`, open, `mergeable_state: dirty`) attempted a full rewrite of the menu to fix the same symptoms. It conflicts with main; the worker-52 2-line PR supersedes its intent. Worker 36 should close/rebase #676.
4. **DOUBLE K.O. edge:** `game.js` `_endRound` increments both wins; `playerWon = wins.p1 > wins.p2` → false → "YOU LOSE" on a simultaneous double-K.O. at match point. Rare; rules call needed, not a crash.

## Verified coherent (no findings)

- Static import graph of `game/js/main.js` (15 modules): all files exist, all named imports resolve (`Game`, `InputManager`, `audio`, `assets`, `ROSTER`/`getCharacter`, `lazy`/`warmIdle`, `mark`, `whUiEnabled`/`mountWhUi`, `getCustomFighter`/`customFighterToRoster`, `resolveFighterAttire`, `createSelectScreen`, `STAGES`/`STAGE_TIERS`/`getStage`/`randomStageId`, `initMenus`).
- `mainmenu.js` (T8 menu): imported via `menus.js` → `initMenus()` → `initMainMenu()`; all 10 sections wired (submenu cards carry `data-action`, routed by main.js's delegated listener; unbuilt modes open the "IN THE FORGE" panel — no silent dead ends).
- `select-screen.js`: grid build, P1/P2 two-step lock (`notifyConfirm`), attire chips, timer, random slot, keyboard parity — coherent.
- `modes.js` versus: `startMode('versus')` → select; `onConfirm` two-step → `_beginVersus` → `startFightViaStage` → stage select → `confirm-stage` → `startFight` (with retry-safe `pendingFight` handling).
- `game.js`: `startMatch` (lazy fighter/movesets/T3, stage from select), `_endRound`/`_afterRound` (best-of-3), `onMatchEnd` → `_versusEnd` → `ui.matchOver` → result screen; `leaveFight` resets state.
- `select.css` (linked) covers the full select-screen class set; `styles.css` covers stage cards, HUD, touch controls.
- All 4 stylesheets + importmap vendor files referenced by `index.html` exist in the repo (except the unlinked `mainmenu.css` — P0-2).

## Tomorrow list (off playable path — PLAYABLE TODAY directive)

- Full 10-section menu audit beyond VERSUS entry: Story submenu (Trial intro → `screen-stage-intro` → reincarnate → trader), Online (ranked/rank hall/tournament), Arcade ladder, Side Games (Qombat/Trader's Mimic), Training/Gungaku, Creation Suite (external page round-trip), Collection (forge panels), Daily Challenges (forge panel), Options (settings/records/howto) — each landing screen needs tap-through verification.
- Story-mode stage intro flow end-to-end (was unreachable due to the duplicate id).
- `?fighter=` / `?stage=` deep links, `?demo=1` AI-vs-AI.
- Menu load-speed (owner: menus load too slow — research exists at `docs/research/menu-load-speed-2026-10-22.md`).

## Live-browser verification steps (for a browser-capable agent)

After the worker-52 PR merges and deploys to https://mhvnsnt.github.io/western-heart/:
1. Phone portrait 390×844, open `game/index.html`. Expect: styled T8 menu (hero art, 10 italic rail items, top player bar), no console errors.
2. Tap VERSUS → submenu slides in (1V1 VERSUS / TEAM BATTLE). Tap 1V1 VERSUS → character select: portrait grid, P1/P2 panes, hints bar.
3. Tap a fighter card → live 3D preview on P1 side, name/facts/stats plate. Tap CONFIRM → P2 cursor activates. Tap another card → CONFIRM → stage select.
4. Stage select: arena cards (thumbs or swatches), tier headers. Tap a card → CONFIRM enables. Tap CONFIRM → "Entering the arena…" → fight HUD boots, fighters spawn, timer counts down from 60.
5. Fight: joystick moves P1; LP/RP/LK/RK buttons fire moves; S/B/D work. Play to K.O. → ROUND 2 → play to 2 round wins → result screen (YOU WIN/YOU LOSE).
6. Tap REMATCH → back at stage select. Tap MAIN MENU → menu. No red console errors at any step.

## Changelog
- 2026-10-22 ~16:00 CDT: created by worker 52. P0-1 + P0-2 found by code audit of main @ 2af4328.
- 2026-10-22 ~16:10 CDT: P0-2 fixed on main by PR #677 (mainmenu.css link). P0-1 (duplicate screen-stage id) still open — shipped as worker-52 PR (1 line in `game/index.html`).
