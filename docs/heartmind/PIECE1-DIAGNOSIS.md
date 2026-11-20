# Western Heart — Piece 1 diagnosis (read-only)

**Repo:** `mhvnsnt/western-heart`, web build in `game/`
**Method:** read repo code only with the GitHub connector. No code edited, nothing pushed, no browser opened.
**Sources:** `~/workspace/western-heart-audit/PLAYTEST-PIECE1.md` (run 2026-11-07, site build Nov 5, commit `2aebf11`) and `AUDIT.md` (2026-11-06).
**Build drift warning:** the repo has moved since the playtest. Current HEAD at diagnosis time is `3334ebf` (merge PR #1639, 2026-11-07 22:17 UTC). Line numbers below are from that HEAD. Where a fix already landed after the playtest build, it is named instead of re-diagnosed.

**Headline: 6 of 9 have a found cause in code, 1 is partial, 2 are still unknown.**
- Found: 1, 2, 3, 4, 7, 9.
- Partial: 5 (damage and Surge found; the grab half has candidates only).
- Unknown: 6, 8.

**Names:** Pantera is male — he/him. Every other fighter is referred to by name only, no pronouns.

---

## 1. Select timer overwrites a picked P2 fighter at 0 — FOUND

**Cause file:** `game/js/main.js`, lines 621–657 (the 99-second timer); `game/js/select-screen.js`, lines 824–860 (`highlight` / `selectById`).

**Likely cause, in plain words:** the timer does not know P2 has already picked. At 0 it builds a pool of every fighter except the P1 pick (`main.js:644`) and calls `selectScreen.selectById(pick.id)` (`main.js:646`). That lands on whichever side is currently active — including P2 — and `highlight` overwrites that side's pick without checking whether a pick is already there (`select-screen.js:836–838`: it only refuses when the side is *locked*, not when it is *picked*). The timer is also never stopped when a fighter is confirmed: `confirmSelection` (`main.js:901–919`) never calls `stopSelectTimer`. The only places the timer stops are leaving the select screen (`main.js:94`) and firing at 0. So the countdown keeps running through both confirms, and at 0 it replaces the live P2 highlight with a random fighter.

**Minimal fix:** stop the timer the moment either side locks, and at 0 only fill a side that has no pick yet — never overwrite an existing highlight.

---

## 2. Confirmed P2 Demonio replaced by King Tyrant by fight start — FOUND (most likely)

**Cause files:** `game/js/modes.js`, lines 508–540 (`onConfirm`), 719–739 (`_arcadeNext`), 1375–1382 (`_pickFoe`); `game/js/roster-full.js`, line 110 (King Tyrant is a normal roster entry, model `king-tyrant`).

**Likely cause, in plain words:** in Arcade mode there is no P2 pick at all. `onConfirm` in Arcade takes one fighter only and starts the ladder (`modes.js:534–536`). `_arcadeNext` then picks the foe at random from the *whole* roster — `_pickFoe` (`modes.js:1375–1382`) filters out only the player and `custom`, with no stage pool on rung 1 — and King Tyrant is in that pool. So a player who picks Pantera, then spends time picking Demonio on the select screen, is picking a fighter Arcade never uses; the ladder foe is a random draw, and King Tyrant was the draw. In Versus the code passes both locked picks straight through (`_beginVersus`, `modes.js:613–637`), and no Versus path swaps a locked P2 for a random fighter — the only random-opponent paths are the timer overwriting the highlight before confirm (Break 1) and the `startFight` fallback (`main.js:1272–1273`, only when the enemy entry has no model; Demonio has one). One caveat: the playtest notes do not record which mode the Tyrant fight was in, so this is the most likely cause, not a proven one — but no code path supports a silent Versus swap.

**Minimal fix:** in Arcade, say on screen that the foe is random (show the drawn foe's name/card before the fight starts), and never let the select screen look like a P2 pick exists in a one-player mode.

---

## 3. King Tyrant spawns T-posed, sunk waist-deep, slowly sinking — FOUND (already fixed after the playtest build — needs a live re-check)

**Cause files:** `game/js/fighter.js`, lines 94 and 176/210 (conflicting bank maps: moveset `xiaoyu`, bank `eddy`); `game/assets/models/MODEL-STATUS.md` (King Tyrant: 24 skinned meshes, 50 bones, 1.95 m, auto-rigged onto the WH skeleton — so the model itself is rigged, not a static); `game/js/assets.js`, lines 1565–1583 (floor height is measured from skinned meshes only).

**Likely cause, in plain words:** King Tyrant's animation bank was broken at playtest time. The very next day's commit `e8147929` (2026-11-07, "Xiaoyu-bank fighters stood in a T-pose guard") says the Xiaoyu bank's skeleton file had been rewritten to a neutral T-pose on 2026-10-22, and every clip composed on it spread the arms and locked the knees — the T-pose the playtest saw. That fix regenerated the bank, but it landed *after* the Nov 5 playtest build, so the playtest result is stale for this break. The waist-deep spawn fits the same bank fault: the idle clip's hip-height track rides the wrong rest pose, so the body renders sunk while the fighter's root stands on the floor (`fighter.js:752`, root starts at ground level). The slow sinking drift itself has no separate cause found in code — no gravity path sinks a grounded fighter (`fighter.js:3910–3911` clamps a grounded fighter to the floor) — so it is most likely the same bad hip track drifting as clips loop and blend, not a second bug.

**Minimal fix:** none in code until a live re-check on the current build confirms the Nov 7 bank fix actually cured King Tyrant; if the sink survives, measure the hip-track height in the bank data next.

---

## 4. Pantera loses health passively in the Tyrant fight — FOUND (no passive drain exists; the damage is invisible attacks)

**Cause files:** `game/js/modes.js`, line 148 (King Tyrant AI: grapple 0.8); `game/js/ai.js`, lines 325–327 (grapple machine commits throws) and 364–372 (command grab at chest-to-chest range); `game/js/fighter.js`, lines 3456–3465 (`getHitbox` falls back to a frame-data box when a fighter has no usable bones); `game/js/game.js`, lines 708–762 (hit resolution is data-driven, not animation-driven).

**Likely cause, in plain words:** there is no health drain anywhere in the code — the only health change over time in `fighter.js` `update` is healing (`fighter.js:3520–3521`, a regen stat Pantera does not have). What the playtest called "passive" loss is King Tyrant attacking with no visible animation. Combat in this game is decided by frame data and reach numbers, not by what the model is seen doing, and the hitbox code explicitly falls back to a frame-data box for a T-posed fighter. So King Tyrant's grabs and strikes still connect on paper while the model stands still — Pantera's health drops in chunks from throws Pantera never sees coming. The 13-minute length is Break 9 (the slow sim), not a slow drain.

**Minimal fix:** fix Break 3 first (the bank), then re-check: a fighter with no working animation must never be fielded as a foe — gate ladder foes on a working bank, the way model-pending fighters are already gated out of fights (`main.js:1266–1273`).

---

## 5. Vs Demonio: Pantera hits ~1%, Demonio counters ~20%; Surge does nothing; grab never lands — PARTIAL

### 5a. Damage asymmetry — FOUND

**Cause files:** `game/js/fighter.js`, lines 3055 (clean-hit damage), 3020 (blocked-hit chip), 3064–3068 (counter-hit bonus); `game/js/roster-full.js`, lines 62 and 89 (Pantera power 1.3 / defense 1.2; Demonio power 1.05 / defense 1.0); `game/js/fighter.js`, lines 77–80 (fallback move damage: punch 7, kick 15).

**Likely cause, in plain words:** the stats do not nerf Pantera — Pantera hits *harder* on paper (1.3 power vs Demonio 1.0 defense). The numbers fit blocked hits, not clean ones. A clean Pantera jab is 7 × 1.3 / 1.0 ≈ 9 health, about 5% of 180. A *blocked* jab chips at 12%: about 1 health, about 0.6% — and 20 such hits land Demonio at ~93%, exactly what the playtest saw. Demonio's AI blocks reactively (`game/js/ai.js`, lines 284–300), so Pantera was mostly chipping a guarding Demonio. Demonio's counters are the other side of the same formula: a counter hit during Pantera's own attack startup adds Pantera's own move damage plus a ×1.2 multiplier (`fighter.js:3064–3068`), and Demonio's knockdown moves carry big base damage — ~36 health, ~20%, is a normal counter launcher, not a bug in the formula.

**Minimal fix:** no formula change yet — first make blocked vs clean hits look different on screen (the block spark and the hit flinch read the same), and tune the AI's block rate down so a player can tell a blocked jab from a whiffed one.

### 5b. Surge (L) does nothing with a full meter — FOUND

**Cause files:** `game/js/input.js`, line 317 (L pushes `surge`); `game/js/game.js`, lines 559–566 (L runs `tryAttack('surge')`); `game/js/fighter.js`, lines 79 (the `surge` move: damage 18, cost 100) and 2643 (`_tryAttackFresh` refuses when Pantera cannot act) and 2728–2730 (cost check); `game/js/soul-systems.js`, lines 3–4 and 34–41 (the full-meter super is Nine-Soul Release on 1+2+3+4, not on L).

**Likely cause, in plain words:** L is not the full-meter super. L fires a plain strike (damage 18) that costs the whole meter, while the real super — Nine-Soul Release, 30 unblockable damage — only fires on the 1+2+3+4 chord (`game.js:543`). And the L strike fails silently in the two most common situations: while Pantera is in hitstun, blockstun, or a move's recovery (`_tryAttackFresh` returns false with no message), and when Demonio is out of the strike's reach (it whiffs, leaving only a 0.7-second aura flash as feedback). A player pressing L mid-fight, mostly while being countered, sees nothing happen and the meter stays full.

**Minimal fix:** show a failed-surge cue (a short "BLOCKED / TOO LATE" note, or a meter shake) instead of failing silently, and put the real input for the full-meter super on the button hint itself.

### 5c. Grab (U) never lands as a throw — CANDIDATES ONLY, no single cause found

**Cause files:** `game/js/fighter.js`, line 340 (`grab` maps to the `1+3` throw), lines 1927–1938 (`canBeHitBy`: a standing throw whiffs a crouching or airborne foe); `game/js/combat-core.js`, lines 229–240 (throw reach 1.7 m; bodies separate at 1.45 m — `fighter.js:1855` — leaving a ~0.25 m window).

**Likely cause, in plain words:** the grab has a very small window and several quiet ways to miss — Demonio crouching, Demonio airborne, Demonio just outside 1.7 m, or Pantera not free to act when U is pressed — and every one of those fails silently, exactly like Surge. No code was found that blocks grabs outright.

**Minimal fix:** same as Surge — a visible whiff/miss cue — plus widen the grab's connect window a little, since 0.25 m of usable range is unforgiving at the slow sim speed (Break 9).

---

## 6. "BREAK THE THROW — TAP LP" stuck on screen — UNKNOWN (full cause not found in code)

**Cause files checked:** `game/js/main.js`, lines 254–274 (`throwBreakPrompt`); `game/js/game.js`, lines 782 (shows it) and 607 (hides it); `game/js/fighter.js`, lines 2056–2062 (`startThrowLock`, paired-throw path); `game/styles.css`, lines 476–484 (the prompt is invisible unless it has the `show` class).

**What the code says:** the prompt is *supposed* to hide itself after 900 ms — `throwBreakPrompt` sets a 900 ms timer that removes the `show` class (`main.js:263`). There is one element only (`game/index.html`, line 479), and no other code touches it. Two gaps were found, but neither alone explains a permanently stuck prompt: (a) the paired-throw path never calls the hide — `game.js:607` hides the prompt only for legacy throw locks, and paired throws skip that loop by design; (b) every fresh grab re-shows the prompt and *resets* the 900 ms timer, so repeated grabs keep it alive. For the prompt to stay up in every frame of a long fight, grabs would have to connect at least once every 900 ms, which the playtest does not support for the Demonio fight (Pantera's grabs never landed; Demonio's grab rate is low). A live check is needed — watch whether the prompt's timer is being reset, and whether the `show` class is stuck on the element.

**Minimal fix:** hide the prompt on every throw resolution path (paired throws included) and on round end, and never re-show it within 900 ms of a hide.

---

## 7. Pause unclickable, Escape does nothing, Clothing Back unclickable — FOUND

**Cause files:** `game/styles.css`, line 27 (`.screen.hud` has `pointer-events: none`) and lines 708–711 (the training-quit button explicitly re-enables itself with `pointer-events: auto` — the code knows this pattern); `game/menus.css`, lines 96–102 (`#wh-pause-btn` has no such re-enable, so it inherits `none` and can never receive a click); `game/js/menus.js`, lines 501–509 (the button is created inside `#hud`); Escape: no key handler for pausing exists anywhere in `game/js` (the only Escape binding is `main.js:1599`, exiting replay view); Clothing: `game/js/menus.js`, lines 465–471 (dialog markup) and 316–360 (`openClothing` adds a `show` class) — but there is **no CSS rule at all** for `#wh-clothing` in `styles.css` or `menus.css`, unlike its siblings `#wh-options` / `#wh-records` (`menus.css:124–130`, fixed position, z-index 205, shown on `.show`) and `#wh-pause` (`menus.css:104–109`, z-index 210). The clothing dialog is therefore never positioned as a dialog; its Back button sits underneath the fixed full-screen layers.

**Likely cause, in plain words:** three small omissions, not one overlay. The pause button is inside a container that takes no clicks, and unlike the quit button nobody gave it its clicks back. Escape was simply never wired to pause. The clothing dialog was never given the positioning rules its sibling dialogs have.

**Minimal fix:** give `#wh-pause-btn` `pointer-events: auto`; add an Escape key handler that opens pause; give `#wh-clothing` the same fixed-position/z-index/show rules as `#wh-options`.

---

## 8. Result "YOU LOSE" heading clipped to "YOU L…" — UNKNOWN

**Cause files checked:** `game/js/main.js`, line 293 (`matchOver` sets `YOU LOSE`); `game/index.html`, line 604 (`#result-title` inside `.panel`); `game/styles.css`, lines 76–84 (`.panel` is 460 px max, `.panel h2` is capped at 32 px) — "YOU LOSE" at 32 px fits that panel several times over, and no ellipsis/nowrap rule touches the result title.

**What the code says:** no clipping cause exists in the current code. The most likely explanations are outside it: the playtest ran the Nov 5 build (`2aebf11`), and the stylesheet has changed since, or the clipped heading was a different element (the round banner, `styles.css:287`, renders at up to 120 px). This needs a live check of the heading's computed size at 1919 px on the current build before any fix is written.

**Minimal fix:** none until a live repro — first inspect `#result-title` at 1919 px and diff `styles.css` at the playtest commit.

---

## 9. HIGH graphics: ~1 timer tick per 30 s; LOW: ~1 per 7–20 s — FOUND

**Cause files:** `game/js/game.js`, lines 64 (fixed step = 1/120 s), 427–449 (the loop: frame time is clamped to 0.05 s, then drained at most 4 fixed steps per render frame, and any leftover time is *dropped*); `game/js/frame-step.js`, lines 22–33 (`MAX_FIXED_STEPS = 4`, excess dropped by design to avoid a spiral); `game/js/game.js`, lines 484–486 (the fight timer only moves inside those sim steps); `game/js/menus.js`, lines 57–66 (LOW = 0.75× pixel ratio, shadows off; HIGH = up to 2× pixel ratio, shadows on).

**Likely cause, in plain words:** the game clock is the simulation, and the simulation is capped at 4 steps of 1/120 s per rendered frame — at most 1/30 s of game time per frame. When rendering is slow, game time runs slower than wall time. At HIGH the machine rendered about 1 frame per second, so 30 frames (one game second) took ~30 wall seconds — exactly the playtest number. At LOW the renderer ran faster (~1.5–4 frames per second), so a game second took 7–20 wall seconds. The timer is not broken; the renderer is too slow at 1919 px on that machine, and the fixed-step cap turns slow rendering into slow time. (The Shrine rendering as a dark box on LOW is the same trade: shadows off, flat light.)

**Minimal fix:** do not raise the step cap blindly (the cap exists to stop a spiral) — instead make HIGH cheaper at big widths (cap pixel ratio at 1 above phone widths, or drop shadows first), and separately drive the *displayed* timer from wall time so the clock never lies about how long a round has lasted.

---

## Shared root cause

The biggest shared thread is Breaks 3, 4, and 5: **combat is decided by frame data, not by animation.** A fighter with a broken animation bank still attacks, grabs, and takes hits on paper (`fighter.js` falls back to frame-data hitboxes and hurtboxes), so a broken model fights invisibly — Pantera loses health to attacks that are never seen, and grabs and surges fail silently. Break 9 makes every other break worse, because at ~1 frame per second the whole fight stretches out and every silent failure repeats for minutes. Fix order should stay as the playtest listed them: select first (Breaks 1–2), then the bank (Break 3), then the silent-failure feedback (Breaks 5–6), then the clicks (Break 7), then the speed (Break 9). Breaks 6 and 8 need a live repro before a fix is written.
