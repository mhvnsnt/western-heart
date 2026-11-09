# Piece 1 re-test follow-ups — worklog

Branch: fix/piece1-retest-followups, from origin/main 15caacbc.
Brief: ~/workspace/western-heart-audit/PIECE1-RETEST-2026-11-08.md (live re-test of build 847a0aa4).
PR: ONE pull request, no merge (Jay or the parent merges).

## Per-bug diagnosis + fix + evidence

### Bug 1 — Break 8, "YOU LOSE" clipped to "YOU L" (CONFIRMED)
- Cause: game/t7-skin.css set #result-title to min(16vw, 20vh, 150px), nowrap — 727 px wide at 1919x998 — while the base .panel (game/styles.css) is max 460 px with overflow-x hidden. The T7 skin also makes the panel invisible, so its overflow rule was meaningless.
- Fix: overflow: visible on #screen-result .panel in game/t7-skin.css (shorthand, both axes); game/t7-skin.css added to screen-result's files in game/ui_sources.json (source already cited there: teardown/tekken7-steam-ui/T7-UI-LAYOUT.md).
- Proof (headless Chromium, real CSS + real markup): before 1919x998 visible text 434/727 px (59.7%) — "YOU L"; after 727/727 px (100%) — "YOU LOSE", right edge 1483 < 1919 viewport. At 390x844 the title already fit (321/359 px) before and after. Screenshots: /tmp/proof-piece1-followups/bug1-result-before-1919x998.png and bug1-result-after-1919x998.png (workspace copy owed — home quota exhausted when they were made).

### Bug 2 — round NEVER ends at 00
- Cause: the display clock ran on wall time (game.js _loop) while the round END ran on sim time only (this.timer in _update). At ~1 fps one sim second takes ~30 wall seconds, so the display hit 00 at 60 s wall while the sim timer still had most of its 60 s left. The post-round 3.0 s lockout was also sim-counted (~90 s wall on a slow machine).
- Grounding: teardown spec (T7 tournament 60 s timer, first to 3 rounds; TIME UP ends the round, higher HP wins) + UR Part C (when the condition expires the mission ENDS). The game's own _timeOut() already implements the TIME UP outcome.
- Fix: game.js _loop calls _timeOut() when the wall limit is reached during 'fight' (roundTime 0 = INFINITY skips it); the 'over' lockout counts down in wall time in _loop; _timeOut() guards on roundState; the sim timer stays as the fast-machine path.
- Proof: new game/tests/round-wall-timeout.test.mjs — 6/6 pass on the fix, 3/6 fail on HEAD (the three wall-timeout/lockout tests fail; the bug reproduced).

### Bug 3 — CLOTHING button dead in the pause menu
- Cause: openClothing() in game/js/menus.js called esc() to escape fighter/layer names, but esc was never defined in menus.js or as a global — first row threw ReferenceError, the async function rejected silently, the sheet never showed. The handler itself was attached (same block as OPTIONS, which worked).
- Fix: esc helper in menus.js next to el, using the game's own escape pattern (game/js/fighter-portraits.js); the sheet now shows before the config load (same as openOptions) so a stall is visible instead of silent.
- Proof: sandbox harness running the real openClothing() with the real config — BEFORE (HEAD): ReferenceError: esc is not defined, sheet shows false; AFTER: no throw, sheet shows true, pause hidden true, name escaped, real layer row rendered. Harness: /tmp/bug3-sandbox/test.mjs.

### Bug 4 — King Tyrant fight fails to load (stalls at 4%)
- Measured (live, 2026-11-09 00:08 UTC): remote Worker serves king-tyrant.glb HTTP 200, 25,643,940 B in 7.8 s, valid glTF v2. Repo file at main is 26,682,804 B (blob b1b93a33) — the bucket copy is the older build (manifest pins 25,643,940 B, blob 456e4d36), a stale copy, not corruption. Local Pages URL 404s (not on the live branch); jsDelivr 403s (over 20 MB). "4%" = the load-progress creep with zero bytes arrived (game/js/load-progress.js). The retry chain re-tries the identical failing fetch (safe load only drops transform/form models, not the base).
- The defect: King Tyrant was the only one of the three re-test fighters with no same-origin copy — Demonio/Pantera are bundled in the shell, he loaded only from the remote Worker. His select portrait's dark + red hazard stripes are the game's own data-attire-state="unavailable" indicator (game/select.css) — the attire warm had already failed at select time.
- Fix: game/assets/models/king-tyrant.glb added to SHELL_BUNDLED_MODELS in game/js/asset-config.js (same mechanism as Demonio/Pantera); tools/deploy/deploy_delta.py now ships bundled models missing from the live branch (same regex-parse pattern as its T7 rules; the 1 GiB CAP check still refuses an over-cap tree). New live total 1,030,554,030 B < 1,073,741,824.
- Proof: resolveAssetCandidates() before = [remote, local, jsDelivr] (remote first); after = [local, remote] — identical order to Demonio. Deploy dry run OWED (home quota exhausted — git fetch fails on EDQUOT; the rule is verified by the regex test + the API-verified main/live membership + the CAP math).

### Bug 5 — camera clips inside/behind pillars and walls after 00
- Cause: the impact shake is added AFTER the wall clamp in game/js/scene.js update(), with no clamp on the shaken position. A heavy hit (mag 0.6, dur 0.5) shoves the camera up to +/-2.1 m sideways/down. At the stage edge the camera already sits at its clamped corner (Shrine: 12.73 m from center vs the panel ring's 13.25 m inner face — 0.5 m clearance), so the shake pushed it through the shell, behind the wood panels. After 00 the fight ran ~25 min with the fighters piled at the walls, so the camera sat at that corner for minutes with every heavy hit shaking it through. Stage geometry measured from buildShrine in game/js/stages.js (panels r=13.5, lantern posts r=11.4, toro lanterns at +/-9.4/+/-2.6).
- Fix: re-clamp the shaken camera X with the same fightCameraCenterX the unshaken position uses, and keep Y above the current floor (groundY + 0.5 m); guarded by if (!camAng) so the explicit camPos stages (nm-parking-lot, nm-lobby-glb — both orbited) are untouched. Look target keeps its counter-shake.
- Proof: fight-camera tests 16/16 pass; node --check passes. Live-browser re-check owed (parent lane).

### Bug 6 — Stage SELECT button does nothing visible
- Cause: SELECT is the default stageMode (game/js/rules.js), so tapping it re-applied the same value — the only feedback was the already-lit highlight — and nothing said the arena list comes later, on CHOOSE YOUR ARENA after picking fighters (game/js/modes.js: the arena screen shows unless stageMode is 'random').
- Fix: the STAGE row's sub-label in game/js/versus-setup.js now says what each choice does ("Pick your arena on the next screen, after choosing fighters" / "A random arena is picked for you") and follows the pick via an optional subFor on the existing segRow builder.
- Proof: sandbox harness — BEFORE: sub stays "Arena for the bout" through every tap; AFTER: sub changes with the pick as above. Harness: /tmp/bug6-sandbox/test.mjs.

### Break 6 — "BREAK THE THROW — TAP LP" never appeared
- Finding (no code change): the trigger is LIVE — game/js/game.js calls throwBreakPrompt unconditionally after startThrowLock on a CONNECTED grab on the grounded player; the throw-pair being UNMAPPED does not block it (startThrowLock falls back to the legacy lock and the prompt still fires). No grab connected on the player in either re-test fight, so the prompt correctly never appeared. The old stuck bug is gone (900 ms auto-hide exists in game/js/main.js). The re-test's sparse screenshots could not have caught a 900 ms prompt anyway. Open question for the parent's live lane: whether Demonio's AI grabs ever connect on the player.

## Tests run (local head, after the fixes)
- node --check: game/js/game.js, menus.js, scene.js, versus-setup.js, asset-config.js — all OK.
- game/tests/fight-camera-level.test.mjs 16/16, game/tests/asset-cache.test.mjs 7/7, game/tests/stagerage.test.mjs 15/15, test/snow-leopard-bucket-routing.test.mjs 2/2, test/free-camera-placement.test.mjs 3/3 — 43 pass, 0 fail.
- New game/tests/round-wall-timeout.test.mjs 6/6 (3/6 on HEAD).
- gitleaks 8.28.0 on all changed files: no leaks found.
- Full suite NOT run locally (no valid baseline — the sparse checkout is missing files the suite needs; 52 files fail on ENOENT before any change). CI on the PR is the full-suite check.

## Open / owed (not in this PR)
- Live playthrough proof, phone-size video (parent lane — this environment has no live browser).
- Deploy dry run for the deploy_delta.py rule (home quota exhausted).
- Workspace copies of the Bug 1 screenshots (home quota exhausted when made; originals in /tmp/proof-piece1-followups/).
- Break 6 live observation (does a Demonio grab ever connect on the player?).
- The remote Worker still serves the OLDER king-tyrant build (25,643,940 B vs repo 26,682,804 B) — the bucket copy is stale; the bundling fix makes the shell copy authoritative, but a bucket re-upload to match main is owed.
- King Tyrant's select portrait content itself was not visually inspected (PNG bytes verified valid, 320x320); the stripes are explained by the unavailable-attire indicator, not by the PNG.
