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

---

## Worker 54 — FIGHT-LOOP CRASH REPAIR (2026-10-22 ~16:20–16:40 CDT, main @ 6b3b69d)

Fight-path audit results: the core loop (fight boots → moves fire → hits register → rounds end → winner → rematch/menu) is GREEN by code read + Node-verified, EXCEPT three breaks below (all fixed in this worker's PR, unmerged due to merge freeze).

### Fight-path findings (blocking → fixed)

| # | Finding | Status | Fix |
|---|---------|--------|-----|
| F1 | **`game/js/hitfx.js` deleted by stale-base clobber.** #616 (merged 17:47 UTC) added `game/js/hitfx.js` (Tekken hit-effect stack: spark/debris/ring/flash, the owner's "prototype bullshitty" hit-FX replacement) + wired it into `game.js`. Current main has the file GONE and `game.js` reverted to prototype sphere-bursts — the PR #579 clobber pattern. | 🔴→🟢 fixed | Restored `game/js/hitfx.js` byte-identical from the #616 merge tree; re-applied the #616 `game.js` wiring surgically (import, `this.hitfx = new HitFX(...)` in constructor, `hitfx.update(dt=0 during hitstop)` in `_loop`, `hitfx.spawn(...)` at all hit sites, `_spawnImpact` → legacy shim). V-System's later `_spawnImpact` calls route through the shim. |
| F2 | **`js/integration.js` merged but NEVER LOADED.** Its header says "Loaded from game/index.html as a plain module script AFTER main.js" — index.html had no such tag. The three-mesh-bvh hit-verify layer, springbones jiggle, troika nameplates/damage numbers, cannon-es KO tumble, nebula hit-FX layering, lip-sync, cam director were all dead code. | 🔴→🟢 fixed | Added `<script type="module" src="js/integration.js">` to `game/index.html` after `main.js`, per the module's own header. Every system init is try/catch — a failing vendor module stays absent, never breaks the fight. |
| F3 | **`await game.startMatch(...)` ran OUTSIDE the try/catch in `startFight`.** Any throw inside startMatch (Fighter build edge, arena.setStage, AI wiring) was an unhandled promise rejection: the player sat on the stage screen forever with "Entering the arena…", no error, no way back. | 🔴→🟢 fixed | Wrapped in try/catch with an error surface on the stage + select hints, re-enabled confirm buttons, `show('stage')`, `return false`. |

### Verified GREEN (fight itself — no changes needed)

- **Fighter loading:** all 49 roster entries' `model` ids + all 16 transform `target:` models resolve in `MODEL_URLS` (script-verified against main). `loadModels` failures surface on the hints (startFight's existing catch); `createInstance` throws only on unknown keys (now guarded by F3).
- **Inputs fire moves:** `input.js` (touch 1/2/3/4 + chords, joystick untouched) → `TekkenBuffer.press/pressChord` → real T3 moves. Node-verified against the real `pantera.json` (784 KB): all 10 inputs (`1,2,3,4,1+3,2+4,1+2,3+4,1+4,2+3`) resolve to real T3 moves (`3+4` = Jaguar Step, 0-dmg stance — correct Tekken behavior, not a bug). Every limb has the last-resort base-move fallback → no dead buttons.
- **Hits register:** the #616 sphere-test hit authority (`game.js` `_resolveCombat` + `fighter.js` getHitbox/getHurtboxes, `canBeHitBy` posture rules) is LIVE — that half of #616 was never clobbered. The BVH verify layer becomes live via F2.
- **Rounds end, winner declared:** `_endRound` → `_afterRound` (best-of-3, `roundsToWin` honored) → `onMatchEnd` → `ui.matchOver` → result screen. All `ui.*` methods called by `game.js` exist in main.js's `ui` object (verified). REMATCH → `modes.rematch()` → stage select; MAIN MENU → `leaveFight()` + `show('menu')`. `getStage` always returns a stage (STAGES[0] fallback); `selectedStage` defaults to `'shrine'`.
- **Side-switch (Claude's lane — NOT touched):** PR #653 replaced #587's smooth Y-rotation tween with an instant flip (`fighter.js` `update()` ≈line 1066: `if (want !== this.facing) this.facing = want`, applied instantly in `_animate` ≈line 1247 `this.lean.rotation.y = this.facing * Math.PI / 2`; `_faceY` is gone, and `game.js` `_startRound`'s `_faceY` assignment is a harmless dead property). Instant flip only runs when `canAct()` — no crash vector found on the fight path. Visual feel changed (smooth → snap); Claude owns it until Oct 23 11 AM.

### Live-browser steps for the fight (after merge + deploy)

7. Versus fight boots: "Entering the arena…" → HUD (health bars, 60s timer, soul meters), two fighters spawn facing each other (instant side-switch snap, no crash).
8. Joystick moves P1; tap 1/2/3/4 → real T3 moves fire every time; hits show Tekken gold spark + debris (heavy: ring; KO: flash + ring); block shows pale-blue spark; timer counts; HP bars drain.
9. K.O. → "K.O." banner → ROUND 2 → 2 round wins → result screen (YOU WIN/YOU LOSE). REMATCH → stage select; MAIN MENU → menu. Console: no red errors; `[WHIntegration] ... ready` lines appear (fail-silent skips logged as warnings only).

### Changelog (append)

- 2026-10-22 ~16:45 CDT: worker 54 fight-loop repair. F1 (hitfx.js clobber restore + re-wire), F2 (integration.js script tag), F3 (startMatch try/catch). Input→move pipeline Node-verified 10/10. Side-switch state flagged (Claude's lane). PR open, NOT merged — merge freeze in effect.
