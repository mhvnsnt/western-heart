# Western Heart — Progression Plan (player-order build)

Owner direction (2026-10-29): build in the order a player experiences the game, so every milestone is a complete, playable, testable slice. Menus and select are mostly done; the focus now is **the fight itself**: stages, fighters, combat and the round/KO flow.

**Live link:** https://mhvnsnt.github.io/western-heart/ redirects to `/game/`. It loads with no console errors, **but the footer says `BUILD 2026-10-22`, a week behind `main`**, and the latest Pages build has sat at `building` since 2026-10-29 02:25 CDT. The owner is playing old code.

## Audit: one match, in play order (from `main`, the live link and the 2026-10-29 sweep)

| # | Step | Status | Notes |
|---|---|---|---|
| 0 | Live link up to date | **BROKEN** | Stale Oct 22 build. The QA hook `window.__startFight` is on `main` but missing live, which proves it. |
| 1 | Main menu | Works | Story / Versus / Online / Arcade / Side Games / Training / Creation / Collection / Challenges / Options. Ten items is a lot for a first-time player. |
| 2 | Character select | Works | 129 roster entries in the sweep; **31 have no model** (DOA ×5, SF ×10, VF ×7, Sun Rā, Hugo, Kutz, Marduk, Raiden, Realizzt, Forest Law, plus Megami and Menajerii quarantined by the material gate). Picking them gives a fighter with no body. |
| 3 | Stage load | Works, uneven quality | 150 arena folders plus generated packs (T3 Retro, No Mercy, Tekken 7 Mishima Dojo), but only ~10 hand-made "Canon Lands" / Cape Jones stages. Quality varies a lot between packs; a 2026-10-22 note found `screen-stage-intro` missing from index.html and crashing `show()` (patched null-safe). |
| 4 | Fighters spawn | Works for 98 | Fighters with models spawn into their stance (sweep fight shots `sweep-*.png`). |
| 5 | Movement | Works | Walk, dash and KOF dash/roll rows. |
| 6 | Attacks / moves | **~86% pass** | 55,986 moves tested: 48,415 pass, 6,168 fail, 1,403 n/a. Worst: Buffalo Bill 112 fails, Byou 117, Demonio-winged 97, Awapop 92, Diablo 86, Baek Master White 81. Juggle routes are often low (e.g. Diablo 1/25). |
| 7 | Hits + damage | Works | `game.js` hit path with KO audio, hit effects and the rage KO hook. |
| 8 | KO + round end | Wired | `_endRound()` fires when HP hits 0. Not yet re-checked as a full best-of-3 to the win screen on the live link. |

**Combat-feel gaps:** failing moves (whiff, wrong animation, or no hit), few juggle routes, uneven stage art across packs, and a 31-fighter hole in the select screen.
**Crash risks:** model-less fighters picked in select, any stage missing assets in the stale build, and the very large repo (58k files) slowing deploys.

## Milestones

### Milestone 1 — "One clean fight on the live link"
**Owner test (exit criteria):**
1. Open the link; the footer shows today's build date.
2. Versus, then pick from a **curated starter set** (e.g. 8 core fighters: Bruno, Pantera, Demonio, Cyborg X, Burger, Chatur, Deathfang, Dio) on **3 polished stages**.
3. The stage loads within 10 s and both fighters stand in their stance, with no T-pose and no invisible fighter.
4. Walk, dash, jab, kick and do a special. Hits land, the health bar drops, and you hear hit sounds.
5. Win round 1 by KO, then round 2. The "K.O." / "You Win" screen shows and you return to select. Nothing freezes.
6. Do it again on a phone with the touch stick.

**Fixes, smallest first:**
1. Unstick the Pages deploy and put the build date on screen. Add a `?quick=p1,p2,stage` URL that opens straight into a fight for testing.
2. Hide the 31 fighters with no model from select (move them to a "coming soon" list) so nobody picks an empty fighter.
3. Pick the 8 starter fighters and 3 best stages; mark them "Core" in select.
4. Get those 8 to 100% in the moveset sweep (fix their failing moves first, using roster-wide fix batches).
5. Run an automated best-of-3 for every pair of the 8 fighters on all 3 stages: round start, KO, round end, match end, and back to select, with no console errors. Save the proof in `docs/proof/`.
6. Do a phone/touch pass on the same flow.
7. Record the owner test as a video.

### Milestone 2 — "Arcade run"
- **Exit criteria:** Arcade with the 8 core fighters, about 6 CPU fights in a row, a boss, and an ending card.
- **Fixes:** AI difficulty ramp, continue screen and per-fighter ending stubs.

### Milestone 3 — "Training + combo feel"
- **Exit criteria:** Training mode shows the move list for the core 8; every listed move works; juggles connect.
- **Fixes:** juggle-route coverage for the core 8 and hit-feel tuning (hitstop, pushback).

### Milestone 4 — "Full roster to 100%"
- Bring each next batch of fighters to 100% moves and give them models (roster-wide batches, not one fighter at a time). Add them to select as they pass. Bring in more stages to the same polish bar.

### Milestone 5 — "Story mode chapter 1"
- The first story chapter played end to end (cutscene, fights, ending).

### Milestone 6 — Online, Side Games, Creation Suite, Collection, Challenges
- Each turned on only once it's playable end to end.

## Parked — after the base game is 100%
- The **MochiiQombat Pack DLC** (`docs/dlc/MOCHIIQOMBAT-PACK.md`).
- Crossover packs without models (DOA, SF, VF) until their models are sourced.
- Mochiichao crossover canon (Region 4 tournament, Sun Rā, Chao-Rangers): that's the Mochiichao repo's later regions.
