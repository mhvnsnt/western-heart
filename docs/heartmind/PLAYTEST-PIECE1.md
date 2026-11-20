# Western Heart — Piece 1 playtest (2026-11-07)

**Site:** https://mhvnsnt.github.io/western-heart/ (redirects to /game/, build "Nov 5, 2026", commit 2aebf11)
**Run:** 2026-11-07 17:26–18:24 CST (58 min), live headed browser task
**Fighters:** Pantera vs Demonio, stage Shrine of the Blade
**Verdict: NOT PASSED.** The old Oct 22 crash is fixed, but no player K.O. was ever reached in 3 fights.

## Two honest limits on this run

1. **No video.** This browser run had no screen-recording tool — only screenshots and a PDF snapshot. There is no gameplay video to show Jay yet. That is still owed.
2. **Not a phone.** The viewport was 1919×998 desktop, not 390×844 phone — the browser could not be resized here. The on-screen joystick and LP/RP/LK/RK touch buttons never appeared; only keyboard hints showed (J punch, K kick, U grab, L surge, Space block, Shift dodge, A/D move). Played with keyboard as a proxy for touch. A real phone-size run with video is still owed.

## Per-step verdicts

1. **Load — PASS.** Menu loads in seconds. Fight assets stream ~29 MB ("Entering the arena… 1.0/29.0 MB", ~20 s).
2. **Main menu — PASS.** Arcade, Versus, Training, Options all open. Arcade shows a ladder, Versus 1V1/TEAM, Training has a dummy mode, Options has sound/graphics/controls.
3. **Character select — BROKEN.** The ~98 s select countdown overwrites a picked fighter with a random one at 0 — Demonio was replaced by MARIPOSA, then by AOTSUKI ("TIME UP — random fighter picked"). Workaround: re-pick Demonio after the timeout and confirm fast. Previews render but are empty until a fighter is clicked.
4. **Stage — PASS (caveat).** Shrine of the Blade is preselected and confirms. Other stages not tested.
5. **Fight — BROKEN.**
   - Wrong opponent: confirming Demonio at timer 14 loaded KING TYRANT instead. King Tyrant spawns T-posed, sunk waist-deep in the floor, slowly sinking, takes no visible damage.
   - Pantera loses health passively in the Tyrant fight (100% → 0 over ~13 min with no attacking), ending in "YOU LOSE" with no K.O. shown.
   - Vs Demonio (correct matchup, LOW graphics): Pantera's hits connect (sparks, Demonio bends over) but do ~1% each; Demonio's counters knock Pantera down for ~20% a hit. After ~20 Pantera hits: Demonio ~93%, Pantera ~55%, timer 34, fight still running.
   - Surge (L) does nothing visible even with a full NINE-SOUL meter. Grab (U) never lands as a throw.
   - "BREAK THE THROW — TAP LP" prompt is stuck on screen in every fight frame, never clears.
   - Pause (top-right) is unclickable — every click refused as "covered" by an invisible overlay. Escape does nothing. Clothing dialog Back button also "covered". Only way out is letting the fight end or reloading the page.
   - Speed: HIGH graphics = ~1 timer tick per 30 s wall time. LOW = ~1 tick per 7–20 s. At LOW the Shrine renders as a dark box with flat lighting. Camera/arena appears to rotate around the ring during fights.
6. **Result screen — PARTIAL.** Reached once (loss to King Tyrant): "YOU LOSE" heading clipped — renders as "YOU L…" at 1919 px — subtitle "THE SHRINE IS SILENT. RUN IT BACK.", buttons REMATCH / CHANGE FIGHTER / REPLAYS / MAIN MENU. REMATCH works (back to stage select, Shrine preselected); BACK returns to character select. MAIN MENU button NOT clicked — untested, not passed. No player-win K.O. or result screen was reached at all.

## What IS fixed

The Oct 22 duplicate `id="screen-stage"` show() crash: FIXED (behavioural verdict — ~25 navigations, no tap ever threw, froze, or produced an error; no console-error text seen, but this environment gives no direct console access, so that part is behavioural, not a console read).

## Breaks in player order (fix in this order)

1. Select timer overwrites the P2 pick on expiry.
2. Confirmed P2 silently replaced by King Tyrant by fight start.
3. King Tyrant loads T-posed and sunk in the floor.
4. Pantera takes passive damage in the Tyrant fight.
5. Damage wildly asymmetric vs Demonio (~1% per Pantera hit vs ~20% per counter); Surge does nothing visible — a player K.O. is not achievable as-is.
6. "BREAK THE THROW — TAP LP" never clears.
7. Pause/Escape and Clothing Back button unclickable in every fight.
8. Result "YOU LOSE" heading clipped.
9. HIGH graphics runs at ~2 fps-equivalent (~1 timer tick / 30 s).

## Evidence

- PDF snapshot of the final fight page: PLAYTEST-PIECE1-final-fight.pdf (same dir, 146,881 bytes, from the browser run).
- Screenshots live in the browser task record (menu, Arcade, select, stage select, Arcade fight, King Tyrant fight, YOU LOSE result, Demonio fight final state Pantera ~55% vs Demonio ~93%, timer 34). The live Demonio fight was left open on the browser tab at end of run.
- No code was changed in this run. Nothing pushed.
