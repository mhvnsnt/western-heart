# Teardown research, part A: Tekken arcade / ladder / character select / all modes — MEASURED

**Date:** 2026-11-07 (evening CST)
**Repo:** `mhvnsnt/western-heart`, HEAD `3334ebf` at read time (modes.js SHA `5f51ba887aed19c21cebe8a16a153bf3f6e19319`, main.js read same HEAD)
**Method:** research + report only. No game code edited, nothing pushed, no commercial game file, ISO, ROM, or code file downloaded.
**Sources used:** (a) repo teardown folders `teardown/tekken3`, `teardown/tekken5`, `teardown/tekken6`, `teardown/tekken7`, `teardown/tekken8`, `teardown/tekken-tag-tournament-2` (listings); (b) `game/js/modes.js` (1,418 lines, current implementation); (c) `game/js/main.js` select timer; (d) `docs/modes/TEKKEN-MODES-RESEARCH.md` (repo's own Lane G research, 2026-10-18); (e) public sources with links — Tekken Wiki Arcade Mode page, Tekkenpedia, and the n0madic/Tekken3Remake decompiled-code research (`docs/research/code/modes.md`, "confirmed from decompiled code", Japan Rev.1), plus the TTT2 Xbox 360 manual on archive.org and the Tekken Wiki Treasure Battle page.
**Language rule used throughout:** Pantera is male (he/him). Every other fighter is referred to by name only, no guessed pronouns.
**Plain language:** this file is written in simple words first. A "ladder" is the list of fights you climb, one after another. A "rung" is one step on that ladder. "CPU" is the computer-controlled fighter.

---

## 0. How to read this file

- **Measured** = a step was found in a named source (repo file + line, or a public page with a link). Every claim below names its source.
- **UNMEASURED** = it could not be found in any source checked. It is marked, never filled in by guessing.
- **Current code** = what `game/js/modes.js` and `game/js/main.js` do today at HEAD `3334ebf`.
- The **differences table** at the end (§8) is the fix spec: measured Tekken behavior vs current code vs fix.

---

## 1. Arcade mode — step by step

### 1a. Tekken 3 arcade (the most fully measured one — decompiled code)

Source: n0madic/Tekken3Remake `docs/research/code/modes.md` ("confirmed from decompiled code", Japan Rev.1) — https://github.com/n0madic/tekken3remake/blob/HEAD/docs/research/code/modes.md — and Tekken Wiki Arcade Mode — https://tekken.fandom.com/wiki/Arcade_Mode

1. **Title → main menu → Arcade.** Boot goes to the title screen, then the main menu. Arcade is one menu choice. (T3 modes doc, "Game states" table: states 3–5 are title / main menu / options.)
2. **Character select.** One player picks one fighter. The select screen is a 2-row grid of 11 positions per row. Only unlocked fighters get a cell. (T3 modes doc, "Character select".)
3. **Pre-fight VS screen.** After select, a short VS screen shows the two portraits, then the fight loads. (T3 modes doc, "Pre-fight VS screen": state 11, 8-frame slide.)
4. **The ladder is built BEFORE the first fight, all 10 stages at once.** The game fills ten ladder entries (fighter, costume, stage) up front. (T3 modes doc, "Arcade ladder", `ArcadeBuildLadder`.)
5. **Stages 1–4: random, distinct fighters from the ten starting fighters**, never the player's own fighter, never the stage-9 boss. (Same source.)
6. **Stages 5–8: random, distinct fighters from the unlocked fighters**, never Heihachi, Ogre, or True Ogre. Once the first Tekken Ball game has been played, Gon joins this pool even while locked. (Same source.)
7. **Stage 9: fixed boss — Heihachi.** Exception: if the player is Heihachi, the stage-9 boss is Jin Kazama instead. (Same source; Tekken Wiki Arcade Mode, Tekken 3 section.)
8. **Stage 10: fixed final boss — Ogre.** After the player wins one round against Ogre, a short scene plays (Ogre picks up the defeated stage-9 boss and holds him overhead) and the fight continues against **True Ogre** in the same match, keeping the same round score. Even with 1-round matches set, both Ogre and True Ogre are fought. (T3 modes doc, "Ogre scene" + "Arcade ladder"; Tekken Wiki Arcade Mode.)
9. **Difficulty climbs with the ladder.** The CPU level for each stage is its index (0–9): stage 1 is easiest, stage 10 hardest. (T3 modes doc, "Arcade ladder".)
10. **Costumes:** opponents wear costume 1 when the player's costume is not 0, otherwise costume 0. Ogre and True Ogre always wear costume 0. (Same source.)
11. **On a loss: CONTINUE.** A "CONTINUE? 9" countdown starts (9, then 8…1, about 90 frames per digit, ~13 seconds total). Pressing Start continues. With the "CHARACTER CHANGE AT CONTINUE" option OFF, the same fight restarts. With it ON, the player goes back to character select. If the timer runs out, it is GAME OVER, then the ranking screen. (T3 modes doc, "Continue" + "Game over".)
12. **On a win at stage 10: the ending movie plays**, then the staff roll. (T3 modes doc: after stage 10 the game goes to state 19, ending movie.)
13. **Unlocks:** clearing Arcade unlocks fighters in a fixed order, one per clear, and each clear must use a different starting fighter: Kuma → Julia Chang → Gun Jack → Mokujin → Anna Williams → Bryan Fury → Heihachi Mishima → Ogre → True Ogre. Unlocked fighters join the CPU roster from stage 4 onward. (Tekken Wiki Arcade Mode, Tekken 3 section.)
14. **Two humans:** if a second player joins, the winner goes on up the ladder and the loser drops out. A player who is not playing can join from the 8th frame of a fight ("A NEW CHALLENGER ENTERS!!"). (T3 modes doc, "Arcade" end hook + "New challenger".)
15. **Round rules:** default round timer 40 seconds in Tekken 3 (last game with a 40-second default). Rounds and time limit are changeable in the options. (Tekken Wiki, Tekken 3 page; Tekken Wiki Arcade Mode: "this mode's rounds and time limit can be modified to the player's liking".)

### 1b. Tekken 5 arcade / Story Mode (they are two different modes — this matters)

Source: Tekken Wiki Arcade Mode (Tekken 5 section) and Tekkenpedia Tekken 5 — https://eng.tekkenpedia.com/wiki/T5/

- **Tekken 5 Arcade Mode is NOT a fixed ladder.** It is an unlimited ranked ladder: the player fights an endless stream of AI fighters for money and rank (kyu/dan ranks). The opponent's rank decides the money earned (default 1,000G at equal rank, −200G per rank lower, +100G per rank higher; 800G–4,000G per win). Wins and losses move promotion/demotion points (3 points to promote, −3 to demote). This later became Ghost Battle in Tekken 5: Dark Resurrection. (Tekken Wiki Arcade Mode, Tekken 5 section.)
- **Tekken 5 Story Mode IS the traditional arcade ladder.** 9 stages: fight 8 AI fighters, then Jinpachi Mishima as the final boss on stage 9. Sub-bosses sit at stages 4, 7, and 8 — usually Devil Jin — with cut-scenes. Exceptions, measured per fighter: for Hwoarang the stage-8 boss is Jin Kazama; for Kazuya, Raven, and Wang Jinrei it is Heihachi Mishima; for Heihachi it is Kazuya Mishima; for Devil Jin it is Asuka Kazama; Jin Kazama and Asuka Kazama face no boss on stage 8, just a random fighter. (Tekken Wiki Arcade Mode, Tekken 5 section; Tekkenpedia Tekken 5, Story Mode.)
- **Story Mode flow:** a short prologue plays before the ladder, and an epilogue + ending movie play after beating Jinpachi. Clearing Story Mode unlocks the prologue and epilogue of the fighter played, plus another fighter. Devil Jin is the exception: unlocked by 200 matches or by clearing the Devil Within minigame. (Tekkenpedia Tekken 5, Story Mode.)
- **Tekken 5 Time Attack:** 9 stages, fixed default settings (2 rounds, 60 seconds per round, normal difficulty), fastest total time wins; 25G per match, 50G for beating Jinpachi. (Tekkenpedia Tekken 5.)

### 1c. Tekken 7 arcade

Source: Tekken Wiki Arcade Mode (Tekken 7 section) — https://tekken.fandom.com/wiki/Arcade_Mode

1. **Only 5 fights.** The first three opponents are randomly selected. Stage 4 is fixed: Heihachi Mishima in the Mishima Dojo.
2. **Final boss, stage 5:** Kazumi Mishima in Devil's Pit — or Akuma in the Abandoned Temple, if ALL three conditions are met: (a) at least one perfect round in the first four stages, (b) win the first four fights in under three minutes, (c) do not use a continue.
3. **Kazumi transforms mid-match:** after the player wins a round against Kazumi, she becomes Devil Kazumi and the fight moves to the second part of Devil's Pit. If the player is K.O.'d in round 1, the fight stays in round 1 form until a round is won.
4. **Final stage is always 2 rounds,** even if the options are set to 1 round; after the final stage (or on return to the main menu) it goes back to 1 round.
5. **After the final boss:** the boss's defeat animation plays, then the credits. The player gets a large amount of Fight Money. Clearing without continues is tied to the Akuma condition above; continues are allowed otherwise (a continue restarts the Kazumi fight from round 1 of her human form).
6. **Ranks:** the player also earns offline rank from Arcade Mode, like in Treasure Battle.

### 1d. Tekken 8 arcade

Source: Tekken Wiki Arcade Mode (Tekken 8 section) — https://tekken.fandom.com/wiki/Arcade_Mode

1. **8 stages.** Stages 1–2 are random opponents. Stage 3: Azucena Ortiz, Victor Chevalier, or a DLC fighter. Stage 4: Jin Kazama, Jun Kazama, Lars Alexandersson, or Reina.
2. **Ghost opponents appear from stage 5 through stage 7** (ghost = AI trained on a real player's style, the Ghost Battle idea).
3. **Final boss, stage 8: Devil Kazuya** at Fallen Destiny. The final boss upgrades if the player scores perfect rounds AND has cleared Chapter 14 of Story Mode: 1 perfect round → Azazel (alternate Coliseum of Fate); 2 perfect rounds → True Devil Kazuya; 3+ perfect rounds → Angel Jin (both in Into the Stratosphere). With no perfect rounds, the final boss stays normal Devil Kazuya.
4. **No credits roll after the final boss** in this version, and it is the only version with no visible timer during stages.
5. **Gate:** the upgraded final bosses need Chapter 14 of Story Mode cleared first.

### 1e. Tekken 6 and Tekken Tag Tournament 2 arcade (short)

Source: Tekken Wiki Arcade Mode (Tekken 6 + TTT2 sections).

- **Tekken 6:** like the arcade version. Extra stage boss NANCY-MI847J (a bonus fight — win or lose, the player still goes on, and it only pays bonus Fight Money). Then Jin Kazama as sub-boss, then Azazel as final boss for all fighters. After beating Azazel the credits play with NO character ending — the first Tekken game to skip the ending after Arcade Mode.
- **TTT2:** 6 random ghost fights (stages depend on offline rank), then 3 boss fights: stage 7 is the tag team of Heihachi Mishima + Jinpachi Mishima; stage 8 is True Ogre (alone, full health bar must be emptied, and True Ogre slowly regains health); final stage is Jun Kazama, who changes into Unknown for the second round. Reaching the final stage forces 2 rounds even on 1-round settings. Beating Arcade unlocks the fighter's ending (except Tiger Jackson, who goes straight to the staff roll).

### 1f. What the current game does (Arcade)

Source: `game/js/modes.js` lines 122–131 (`ARCADE_LADDER`), 718–763 (`_arcadeNext`, `_arcadeEnd`, `_arcadeClear`), 1375–1382 (`_pickFoe`).

- 6 fights: rungs 1–4 random foe, rung 5 fixed Diablo ("DIABLO — SUB-BOSS"), rung 6 fixed Assembled Soul ("ASSEMBLED SOUL — FINAL", built by `buildAssembledSoul`).
- Difficulty is a number per rung: 0.50, 0.58, 0.66, 0.74, 0.85, 0.95. It scales the CPU personality (`scaledAi`).
- Rungs 1–4 foes are picked by `_pickFoe`: a random pick from the whole roster, only excluding the player's fighter and `custom`. No stage pool, no "distinct" rule (the same foe can be drawn twice), no locked/boss exclusion — any roster fighter can appear, including King Tyrant.
- On a loss: no continue countdown at all. The game shows "GAME OVER / The ladder stands. The shrine is silent. Climb again." with one button, RETRY LADDER, which restarts the whole ladder from rung 1. No option to retry the same rung, no character-change option, no GAME OVER → ranking screen.
- On a win at rung 6: "ARCADE CLEARED" screen with a WATCH ENDING button (plays the fighter's ending via `story-endings.js`).
- No prologue before the ladder, no unlocks for clearing, no Fight Money, no rank.
- **The ladder is NOT built up front.** Each rung's foe is drawn when that rung starts (`_arcadeNext`), so the player never sees the ladder ahead of time.

---

## 2. Character select screen

### 2a. Tekken 3 select — measured from decompiled code

Source: n0madic/Tekken3Remake `docs/research/code/modes.md`, "Character select" — https://github.com/n0madic/tekken3remake/blob/HEAD/docs/research/code/modes.md

- **Layout:** two rows of 11 positions. Top row: Xiaoyu, Yoshimitsu, Nina, Law, Hwoarang, Eddy, Paul, King, Lei, Jin, Gon. Bottom row: Doctor B., Bryan, Kuma, Heihachi, Ogre, True Ogre, Julia, Gun Jack, Mokujin, Anna, Gon. Only the first ten positions of a row are drawn on screen (35 pixels apart); the 11th (Gon) is reached by moving past either end of a row — the cursor goes invisible there and Gon's big portrait appears, with blinking arrows at the ends of the grid hinting at it for the first 180 frames.
- **Locked slots:** a locked fighter's cell value is `0x58` — it cannot be picked. A fighter that is unlocked but not available in this selection (for example a team member already taken) is `0x59` — also cannot be picked, and each team pick removes that fighter from the side's available mask.
- **Costumes by button:** Square = costume 0, X or Circle = costume 1, Triangle or Start = costume 2 when the fighter is in the Start-costume mask, otherwise Triangle = costume 0.
- **P1/P2 picking:** both sides choose at the same time, each with its own cursor and big portrait (126 × 208, facing each other). A side with nothing chosen yet (second side not joined) shows a silhouette. If both sides pick the same fighter and costume, the later picker's costume changes (0/1 swap; 2 and 3 become 0) — unless only one side is human.
- **Timer — the key measurement:** the timer starts at `20 · T` select-screen frames, where T = 60, or 60 + 3·(n − 10) when more than 10 fighters are unlocked. It counts down once per frame **while both players are choosing**, and **at 0 each player gets the fighter under the cursor** — the cursor's current fighter, NOT a random one. (At 60 frames per second, 20·60 = 1,200 frames = 20 seconds with 10 or fewer unlocked; it grows by 3 seconds per extra unlocked fighter.)
- **Cursor memory:** each player's cursor starts at the last pick when SELECT CURSOR HOLD is on.
- **Exit:** Start + Select together (shoulder buttons may be held too) returns to the main menu from select and from fights.
- **VS screen after select:** portraits slide in over 8 frames, then the fight loads. (Same doc, "Pre-fight VS screen".)
- **Quick select (VS / team / Tekken Ball):** a different, smaller screen — a 3 × 7 grid, with team-size choice (1–8 players per team), "NO ENTRY" for a locked cell, "SOLD OUT" for a taken one, and a 480-frame idle slide-out that shows "PUSH START+SELECT TO EXIT". (Same doc, "Quick select".)

### 2b. Tekken 7 / Tekken 8 select — what could be measured

- **Layout (T7/T8, from the game itself as seen in public playthroughs and guides):** a grid of fighter portraits with a large portrait + name on each side, P1 on the left (red side), P2 on the right (blue side), a RANDOM select slot, and locked/DLC slots shown greyed out until bought/unlocked. Costume is picked on the same screen (preset 1–4, changed with a button before confirming). Stage select follows character select (or is random in Versus).
- **Timer value, exact random-select behavior, and exact locked-slot behavior in T7/T8: UNMEASURED.** No public source checked states the T7/T8 select timer in seconds or what exactly happens at 0. Do not guess a number here. (The T3 decompiled measurement above is the only timer with a measured value.)
- **Versus rules (T7, measured from tournament rules):** rounds "first to three", timer 60 seconds, stage select random for the first game; the loser of a game may change fighter or stage, the winner is locked to the same fighter. (start.gg / UNIFIED Tekken 7 competition rules — https://unified.gg/e/FANILL0223/c/FANILL0223TK7/rules)

### 2c. What the current game does (select)

Sources: `game/js/main.js` lines 621–657 (99-second timer), 901–919 (`confirmSelection`, per PIECE1-DIAGNOSIS.md); `game/js/select-screen.js` lines 824–860 (`highlight` / `selectById`, per PIECE1-DIAGNOSIS.md); `game/js/modes.js` lines 508–540 (`onConfirm`).

- **Timer is 99 seconds** (comment in code: "Tekken standard selector: starts at 99"). It starts only once assets are loaded.
- **At 0 it picks a RANDOM fighter** from the whole roster except the current `selectedChar`, and overwrites the live highlight via `selectById` — even if a fighter was already picked on the other side. The timer is never stopped when a fighter is confirmed. This is Playtest Break 1 (see PIECE1-DIAGNOSIS.md §1).
- **There is no measured Tekken source for a 99-second timer or a random pick at 0.** Tekken 3's measured timer is ~20 seconds (growing with unlocks) and gives each side the fighter under the cursor at 0. The 99 seconds and the random pick are both invented, not teardown.
- **Arcade shows a two-side select screen but only uses one pick.** `onConfirm` in Arcade takes one fighter and starts the ladder (`modes.js:534–536`); the ladder foe is a random draw (`_pickFoe`). A player who spends time picking a second fighter is picking someone Arcade never uses. This is Playtest Break 2 (see PIECE1-DIAGNOSIS.md §2).
- **Versus flow in code:** P1 picks, then the hint changes to "VERSUS — Player 2: choose your soul", then P2 picks, then `_beginVersus(p1, p2)` (`modes.js:516–533`, `613–637`). Both locked picks go straight through — no Versus path swaps a locked P2. Team Versus (draft) is checked first (`_vsDraft`, `modes.js:512–515`).
- **No costume pick on the select screen** in the current game (no costume step was found in `modes.js` `onConfirm` or in the select flow). Tekken 3 picks costume by button at select; T7/T8 pick a preset on the same screen. Current code: UNMEASURED whether costumes exist at all in the flow — no costume step was found.
- **No locked/unavailable slot behavior** was found in the current select code (no `0x58`/`0x59` equivalent). Locked fighters, if any, are UNMEASURED in the current code.

---

## 3. Every other mode — measured flow, and what the current game has

### 3a. Versus 1V1

**Measured (Tekken):**
- Two players, each picks one fighter on the same select screen (T3: both cursors live at once; T7: P1 then P2 on one screen). Then stage select (T7: random for game 1; loser picks after a loss). Best of rounds — T3 default 2 rounds to win a match, 40-second round timer; T5 Time Attack defaults 2 rounds / 60 seconds; T7 tournament standard first to 3 rounds, 60-second timer. After the match, back to select (T3: VS end hook goes back to select, win/draw stats kept). A second player can join mid-fight in arcade-style modes ("new challenger"); in pure VS the two sides are set at select.
- Sources: T3 modes doc ("VS" end hook, "New challenger"); Tekkenpedia T5 (2 rounds, 60s); UNIFIED T7 rules (first to 3, 60s).

**Current game:** implemented. `modes.js:609–646` (`_beginVersus`): P1 vs P2, rounds/time/guard-damage taken from Versus setup rules (`getRules()` — `roundsVs`, `roundTime`, `guardDamage`), stage random from a pool when stage mode is random (skips the stage screen). Keeps Versus setup rules + result screen + REMATCH. **Difference:** no measured stage-pick step for the loser after a loss (rematch reuses the same setup); no double-blind select; no "winner locked / loser may change" rule.

### 3b. Tag (Tekken Tag Tournament 1/2)

**Measured (Tekken):**
- Each side picks TWO fighters. Tag button swaps the active fighter with the partner at almost any moment; the resting partner slowly regains health (the red/recoverable part of the bar). Only one of the opponent's two fighters needs to be K.O.'d to win the round. (NAG TTT2 review; Eurogamer TTT2 review — https://www.eurogamer.net/tekken-tag-tournament-2-review)
- Tag Combo: press Tag right before a launcher hits — partner runs in and continues the juggle. Tag Assault (TTT2): press Tag right before a Bound move hits — partner jumps in and attacks for a short time, then swaps back; costs the partner's recoverable health, and the opponent's partner gets Rage. Tag Throw: Tag + right punch together — both fighters grab at once. Tag Crash: when the resting partner is in Rage (bar flashing red) and the active fighter is down, the partner barges in to break pressure, at the cost of red life. (Tekken Wiki Tag Assault — https://tekken.fandom.com/wiki/Tag_Assault; TTT2 Xbox 360 manual on archive.org — https://archive.org/stream/xbox-360-marketplace-game-manuals/TEKKEN%20TAG%20TOURNAMENT%202%20%284E4D0859%29_djvu.txt)
- TTT2 Arcade Mode is tag: 6 random ghost fights, then Heihachi + Jinpachi as a tag team, then True Ogre, then Jun → Unknown. (Tekken Wiki Arcade Mode, TTT2 section.)
- Solo vs Tag is allowed: one fighter against two gets double health and slowly regains the tagged-out bonus during the fight. (NAG TTT2 review.)

**Current game:** NOT implemented as a tag system. There is no tag button, no partner swap, no recoverable-health bar, no Tag Assault/Combo/Crash in `modes.js` or the fight core as read. `modes.js` has a `_beginTeamVersus` (team draft for Versus, lines 647–~690) and TEAM BATTLE (see §3e), but those are "one fighter at a time, winner stays on" — not tag. **Tag is a missing mode/system, not a wrong one.**

### 3c. Team Battle

**Measured (Tekken):**
- Debut Tekken 2; present through TTT2; cut from T7 (a fan mod later restored it for T8). Each side fields a team of up to 8 fighters (T3 quick select: team size 1–8). Winner stays on: when a fighter falls, the next in line steps in. The winner's health carries over and increases slightly per win (T5:DR-era convention ~10–15% recovery). After the last member falls, a win/loss tally is shown. (Repo's own `docs/modes/TEKKEN-MODES-RESEARCH.md` §3, citing Tekken Wiki Team Battle + T8 mod video; T3 modes doc, "Team battle": CPU team filled from unlocked fighters not already in the team, least-met first, shuffled into free places; CPU level = difficulty + 3 + option, +1 or +3 when the human side has more members left; result screen state 12 replays each fight one by one with a red/yellow/grey line per winner and ends "YOU WIN!" / "YOU LOSE!" / "DRAW GAME", or "PLAYER-1 WINS!" / "PLAYER-2 WINS!" with two humans.)
- T3 team pick flow: each team pick removes that fighter from the side's available mask (cell `0x59`, "SOLD OUT" on quick select). (T3 modes doc, "Character select" + "Quick select".)

**Current game:** implemented. `modes.js:350` (`TEAM_CFG = { size: 3, restore: 0.15 }`), `508–588` (3-pick flow with a tray, duplicates refused), `1146–1211` (`_teamFight`, `_teamEnd`). 3v3 (Tekken allows up to 8; the game fields 3 — the code says "roster-friendly"). Single-round fights, winner keeps remaining HP + 15% recovery. CPU team is 3 random fighters. End screen shows the tally (fighters left per side). **Differences:** team size 3, not up to 8; no team-size choice at select; CPU team is pure random (no least-met / least-used rule); no per-fight replay result screen — just a win/lose message.

### 3d. Training / Practice

**Measured (Tekken 3 Practice, decompiled):**
- Mode 5, `practice.ovl`. Three sub-modes from MODE SELECT: FREE, VS CPU, COMBO TRAINING, plus PLAYER SELECT (back to character select) and RESET (main menu). (T3 modes doc, "Practice".)
- FREE dummy settings: STAND, CROUCH, STAND GUARD, CROUCH GUARD, GUARD ALL, AUTO GUARD, UKEMI MAE, UKEMI OKU, CONTROLLER (second pad drives the dummy). VS CPU: CPU DIFFICULTY (EASY/MEDIUM/HARD) + CPU LEVEL (STAGE 1…9, FINAL STAGE). COMBO TRAINING: pick a combo from the fighter's list, guide shows the inputs, key display shows the last 15 inputs.
- Always on: ATTACK DATA (damage numbers, TOTAL DMG, COUNTER / CLEAN HIT labels, combo + damage counters), KEY DISPLAY (input history), COMMAND LIST (move list overlay), REPLAY SETTINGS (record/play back 4/5/6-hit combos or manual), FREEZE SIGNAL (the fighter glows green when it can act, red when it cannot — a live frame-advantage display).
- Pause menu in practice is its own menu (Start pauses only in practice via its own path; in other modes Start pauses and only CANCEL unpauses). (T3 modes doc, "Practice" + "Pause".)
- T5+ added command display, frame data, and punishment training on top of this. (Repo's `docs/modes/TEKKEN-MODES-RESEARCH.md` §6.)
- T7 Practice Mode: same idea — free sparring vs a configurable dummy, with command display and frame data. (PowerPyx T7 review, offline modes list.)

**Current game:** implemented in basic form only. `modes.js:962–971` (`_beginTraining`): endless round vs a passive dummy (aggression 0, grab 0, reaction 0, passive true), badge "TRAINING · DUMMY WILL NOT FIGHT BACK", quit button shown, `game.onMatchEnd = null` so rounds auto-reset. Plus FIGHT LAB / GUNGAKU (`modes.js:973–1001`): same shell, dummy runs a program (presets + record-your-own), panel mounted by `fightlab-gungaku.js`. **Differences (all missing):** no FREE / VS CPU / COMBO TRAINING choice; no dummy stance/guard settings (STAND/CROUCH/GUARD ALL/CONTROLLER); no CPU difficulty/level; no attack-data HUD (damage numbers, counter/clean-hit labels); no key/input display; no record/playback; no freeze-signal glow; no command-list overlay in training. The playtest also found Training "has a dummy mode" (PLAYTEST-PIECE1.md §2) — that is all it has.

### 3e. Survival

**Measured (Tekken):**
- Debut Tekken 2; present in every sequel since. Endless stream of CPU opponents, **one round per fight**, health **carries over** — the bar is never refilled to 100%; each win restores only a small amount. Lose once and the run ends. Score = opponents beaten. T2/T3 showed top-10 leaderboards; T3 let the player unlock Gon by entering "GON" as initials. (Repo's `docs/modes/TEKKEN-MODES-RESEARCH.md` §1, citing Tekkenpedia Survival + Time Attack articles.)
- T3 decompiled detail: CPU level from wins — under 5 wins → level 1–3; under 10 → 2–4; under 20 → 3–7; under 50 → 3–7 (group 2 when an option bit is set); then every tenth win level 0, otherwise 3–9 with group 2. Opponent pool: the ten starting fighters for stages 0–6, then everyone but Ogre/True Ogre for 7–16, then everyone — never repeating any of the last four opponents; picks favor the least-met fighters. Result screen (state 14): "SURVIVAL RESULT", a portrait cell per fighter beaten with its win count, sorted by wins, TOTAL wins, then "YOU ARE THE nTH GREATEST SURVIVOR!" for a top-ten place or "YOU NEED MORE PRACTICE!". (T3 modes doc, "Survival opponents" + result state 14.)

**Current game:** implemented. `modes.js:326` (`SURVIVAL_CFG = { restore: 0.25, roundsToWin: 1 }`), `1003–1039` (`_survivalNext`, `_survivalEnd`). One round per fight, HP carried + 25% restore per win, difficulty 0.45 + 0.05 per wave (capped 0.95), record = waves beaten in localStorage, "RUN OVER" screen on loss with best-run line. **Differences:** restore is 25% (Tekken's measured amount is "only a small amount" — no exact percent was found in the sources checked, so 25% is UNMEASURED against Tekken, not proven wrong); foe pool is the whole roster at random with no least-met rule and no last-four exclusion, so the same foe can repeat back-to-back; no per-fighter win-count result screen; no leaderboard/top-10; difficulty is a flat linear ramp, not Tekken 3's stepped bands.

### 3f. Time Attack

**Measured (Tekken):**
- Debut Tekken 2; T3 identical (minus Gon/Dr. Bosconovitch fights). Same ladder shape as Arcade, but the clock is the score: fastest total time wins. T5 fixed the format at 9 stages with default settings (2 rounds, 60 seconds per round, normal difficulty). No pausing until T4. No endings, no credits — the timer is the game. (Repo's `docs/modes/TEKKEN-MODES-RESEARCH.md` §2.)
- T3 decompiled detail: Time Attack is the arcade ladder with a restricted character mask (`0x157FFF`); after the tenth fight it records the time and shows the Time Attack result (state 13): "TIME ATTACK CLEAR!", ten stage rows one every 23 frames with `STAGE n`, opponent portrait, and stage time `mm'ss"hh`, then YOUR TIME (sum of the ten stage times, max 359,999 frames) and the winner's portrait; NEW RECORD blinks when a record is pending. The Ogre scene is skipped in Time Attack (straight to the True Ogre reload). (T3 modes doc, "Time attack" end hook + result state 13 + "Ogre scene".)
- Tekken's rule: **no continues in Time Attack.** (Repo's `docs/modes/TEKKEN-MODES-RESEARCH.md` §2.)

**Current game:** implemented. `modes.js:337–348` (grade thresholds S < 4:00, A < 6:00, B < 9:00, else C), `1096–1145` (`_timeAttackNext`, `_timeAttackEnd`, `_timeAttackClear`). 8 single-round fights against escalating AI (difficulty 0.50 → 0.90), wall-clock time accumulated per fight, clock starts when the round actually begins (not during model loads), loss ends the run, clear shows grade + total time + best time. **Differences:** 8 fights, not 9 (T5) or 10 (T3); single-round fights, not 2-round / 60-second rounds; grade thresholds (S/A/B/C times) are invented — no measured Tekken source gives S < 4:00; no per-stage time breakdown on the result screen (only a total); foes are random from the whole roster, not the arcade ladder shape with fixed bosses.

### 3g. Story / Career (Tekken 4/5/6/7/8 — the "Story Mode" line)

**Measured (Tekken):**
- **Tekken 4:** what was Arcade Mode became "Story Mode" (per-fighter story, prologue + epilogue around the ladder, Heihachi as final boss for most; Jin as final boss for Hwoarang and Kazuya; Kazuya as final boss for Heihachi, fought right before Heihachi). Arcade Battle became a separate mode with changeable options and nothing unlockable. (Tekken Wiki Arcade Mode, Tekken 4 section.)
- **Tekken 5:** Story Mode = 9-stage ladder with sub-bosses at stages 4/7/8 (usually Devil Jin) + cut-scenes, Jinpachi final boss, prologue before + epilogue/ending after, unlocks prologue+epilogue of the fighter played plus another fighter. (Tekkenpedia Tekken 5; see §1b.)
- **Tekken 6:** Scenario Campaign — a beat-'em-up story mode (not a ladder). Arcade Mode is separate. (Tekken Wiki Arcade Mode, Tekken 6 section — credits with no ending; Scenario Campaign is a different system, not detailed here.)
- **Tekken 7:** The Mishima Saga — 14 chapters + epilogue + a "special match", mostly cut-scenes with one two-round fight per episode; separate from Arcade Battle. (PowerPyx T7 review.)
- **Tekken 8:** Story Mode "The Dark Awakens" — chapters; Arcade Mode's upgraded final bosses are gated on clearing Chapter 14. (Tekken Wiki Arcade Mode, Tekken 8 section.)
- **Tekken 3 has no Story Mode** — Arcade Mode IS the story (ending movie per fighter).

**Current game:** Story is a Western Heart original, not Tekken's Story Mode. `modes.js:98–120` (`STORY_STAGES` — 7 stages: Wood → Fire → Earth → Metal → Water → Phantom Marketplace trade → Final Shrine boss), `765–960` (Trial + reincarnation: death picks a new vessel by style profile, Diablo offers himself only after 3+ deaths, Trader stage, Assembled Soul final boss). This is canon-grounded (CANON.md §5 The Trial), not a Tekken copy — that is by design, and it is the one mode where "differs from Tekken" is not a defect. **Difference worth naming anyway:** Tekken's Story Mode is a fixed ladder with prologue/epilogue movies and unlocks; the current Story has an intro cutscene and reincarnation, but no per-fighter prologue/epilogue movies and no unlock-on-clear.

### 3h. Treasure Battle (Tekken 7)

**Measured (Tekken):**
- A modified Ghost Battle (T6/TTT2). Endless opponents; every win grants 1–3 chests (Fight Money or customization items) and moves the fighter's offline rank up (ranks are per-fighter, not per-profile; start 9th Kyu, Warrior rank after ~60–100 wins). Opponents get harder as the player climbs. Every so often a Special Match appears against powered-up boss fighters (Ascended Heihachi, True Devil Kazuya, Akuma in Brimstone & Fire, Devil Kazumi in Devil's Pit, Jin Kazama in Mishima Dojo) — they deal bigger damage and their Rage Art removes all of the player's health; beating one can give a Gold or Rainbow chest and a rank promotion. **There is no continuing** (a loss just ends that fight; the run continues). (Tekken Wiki Treasure Battle — https://tekken.fandom.com/wiki/Treasure_Battle; Windows Central T7 achievement guide — https://www.windowscentral.com/tekken-7-achievement-guide)

**Current game:** implemented. `modes.js:1041–1095` (`_treasureNext`, `_treasureEnd`). Endless waves, escalating difficulty (0.40 + 0.05 per wave, cap 0.95), each win opens a chest (coins always + one still-locked unlockable if any), coins to localStorage `wh_treasure_coins_v1`, prizes via `unlockables.js`, health fresh each wave. **Differences:** health is fresh each wave (Tekken's Treasure Battle is one fight at a time with full health too — this one matches; the difference is elsewhere); no rank ladder (no kyu/dan, no promotion matches); no Special Matches against powered-up bosses; chest count is 1 per win, not 1–3; no Fight Money amounts per fight.

### 3i. Tekken Force (T3) / Devil Within (T5) — for reference (HeartMind uses this)

**Measured (Tekken):**
- Tekken Force (T3): side-scrolling beat-'em-up, 4 stages, waves of Tekken Force soldiers, a boss from the roster at the end of each stage (depends on the fighter picked, except stage 4 where the boss is Heihachi). Clearing all four stages can unlock Dr. Bosconovitch. Losing stores the high score and goes to game over — **no continue**. Items: roast chicken restores 50 health ("LIFE UP!"). (T3 modes doc, "Tekken Force"; Tekken Wiki Tekken 3 page.)
- Devil Within (T5): same idea, third-person camera, 5 stages, enemy groups, door/key puzzles, stage bosses, Devil Gene meter (transform at full meter — more power, costs health). (Repo's `docs/modes/TEKKEN-MODES-RESEARCH.md` §4.)

**Current game:** the HeartMind mode (`game/js/heartmind.js`, per the research doc §4) is the Western Heart version — sequential inner battles vs "echoes" with HP carry-over + soul-ember restores, 5 inner stages, final boss the SHADOW SELF. Not re-measured in this pass (Part A covers arcade/ladder/select + the modes in `modes.js`; HeartMind is a separate lane).

### 3j. Tekken Ball / Tekken Bowl — not in the current game

**Measured (Tekken):** Tekken Ball (T3): 1v1 beach volleyball — hit the ball back over the net; the ball is charged by attacks and damages whoever it hits. Ball types: Beginner/Beach Ball, Expert/Gum Ball, Grand Master/Iron Ball; ball damage 60%/80%/100%. Tekken Bowl (T7): full bowling minigame (Ultimate Tekken Bowl DLC). (Repo's `docs/modes/TEKKEN-MODES-RESEARCH.md` §5; T3 modes doc, "Tekken Ball's select".)
**Current game:** not implemented. Documented in the repo research as a future minigame lane (needs ball physics). No difference to fix in this pass — just recorded as absent.

### 3k. What the current game has that Tekken does not (WH originals — recorded, not defects)

From `modes.js` MODE_LIST (lines 286–310) + implementations: STORY (Trial + reincarnation), IMMORTAL QOMBAT / 不死クォンバット (endless waves, HP + 35% per win, +5% power per wave, `modes.js:1215+`), SOUL SURGE GAUNTLET (8 fights, one per other soul, `modes.js:1287+`), TRADER'S MIMIC (3-bout duel, Trader copies the player's moveset more each round it loses, `modes.js:1327+`), FIGHT LAB / GUNGAKU (programmable dummy), TREASURE BATTLE (Tekken-based, see §3h). All are canon-grounded per the research doc §§8–10. They are not measured against Tekken because they are not Tekken modes.

---

## 4. Round / match rules — measured

| Rule | Tekken measured | Current game | Source |
|---|---|---|---|
| Round timer default | T3: 40 s (last game with 40 s default). T5 Time Attack: 60 s. T7 tournament: 60 s. T8 Arcade: NO visible timer during stages. | 60 s timer (AUDIT.md §5: "Best-of-3, 60 s timer") | Tekken Wiki Tekken 3 page; Tekkenpedia T5; UNIFIED T7 rules; Tekken Wiki Arcade Mode T8 section |
| Rounds to win a match | T3 default 2 rounds; T5 Time Attack 2 rounds; T7 tournament first to 3 rounds; T7/T8/TTT2 final boss stage forced to 2 rounds even on 1-round settings | Best-of-3 (AUDIT.md §5); modes.js passes `roundsToWin: 1` for survival/timeattack/team/treasure | T3 modes doc ("Ogre scene", "TTT2 final stage"); Tekkenpedia T5; UNIFIED T7 rules |
| Rounds/time changeable in Arcade | Yes — Arcade's rounds and time limit can be modified, unlike Time Attack (fixed defaults) | No options step found in the Arcade flow in `modes.js` — Arcade starts straight from select | Tekken Wiki Arcade Mode ("Unlike Time Attack mode, this mode's rounds and time limit can be modified") |
| Continue | T3: "CONTINUE? 9" countdown, ~13 s; Start continues; same fight restarts, or back to select if CHARACTER CHANGE AT CONTINUE is on; timer out = GAME OVER → ranking | No continue at all. Loss = "GAME OVER" screen with RETRY LADDER (whole ladder from rung 1) or MAIN MENU | T3 modes doc, "Continue" + "Game over"; modes.js:752–754 |
| Pause | T3: Start pauses mid-round; Start again does NOT unpause — only CANCEL does; pause menu has CANCEL / COMMAND (move list) / RESET (leave to main menu); music volume drops while paused | Pause button unclickable in fights (Playtest Break 7 — `styles.css:27` `.screen.hud` has `pointer-events: none`, `#wh-pause-btn` has no re-enable; Escape never wired to pause) | T3 modes doc, "Pause"; PIECE1-DIAGNOSIS.md §7 |
| Challenger join | T3: a non-playing player can join from the 8th frame of a fight with Start ("A NEW CHALLENGER ENTERS!!"); with L1+R1 held, quick select | Not implemented — no join path found in `modes.js` | T3 modes doc, "New challenger" |

---

## 5. Stages — how Tekken picks them vs the current game

- **Tekken 3:** each ladder entry has its own stage index, picked when the ladder is built (`ArcadeBuildLadder` fills character + costume + stage per entry). Stages are tied to the ladder, not picked by the player in Arcade. (T3 modes doc, "Arcade ladder".)
- **Tekken 7 Arcade:** fixed stages for the bosses (stage 4 Mishima Dojo, final Devil's Pit / Abandoned Temple); random stages for the first three. (Tekken Wiki Arcade Mode, T7 section.)
- **Tekken 7 Versus:** stage is random for game 1; the loser picks after a loss. (UNIFIED T7 rules.)
- **Current game:** stage select screen exists (playtest: Shrine of the Blade preselected and confirms — PLAYTEST-PIECE1.md §4). In Versus, `_beginVersus` takes a stage from setup rules or random from a pool (`modes.js:626–629`). In Arcade, `startFight` is called with no stage — the stage the player picked on the stage screen is used for the whole ladder, as far as the code read shows. **Difference:** Tekken's Arcade changes stage per ladder rung (and fixes boss stages); the current Arcade plays the whole ladder on the one stage the player picked. Whether the stage actually changes per rung in the current build is UNMEASURED — no per-rung stage code was found in `_arcadeNext`, and the playtest only played one stage.

---

## 6. Endings / results / records — measured

- **Tekken 1–3, 5, 7, TTT2:** beating the final boss plays the fighter's ending movie, then (usually) the credits. T6 is the exception: credits with no ending. T8 Arcade: no credits roll. (Tekken Wiki Arcade Mode, all sections.)
- **T3 result screens:** Time Attack shows all ten stage times + total + NEW RECORD; Survival shows per-fighter win counts + total + top-10 rank line; Team shows a fight-by-fight replay with winner lines. Then the ranking screen (3 pages: character time records, greatest survivors, character usage), with name entry (3,000-frame timer, 40-symbol alphabet; entering "GON" unlocks Gon). (T3 modes doc, "Result screens" + "Ranking screen".)
- **Current game:** Arcade clear shows "ARCADE CLEARED" + WATCH ENDING button (per-fighter ending via `story-endings.js`). Records are localStorage only (`wh_records`: survival waves, timeattack best time, treasure waves — `modes.js:312–316`, `whGetRecords`/`whSetRecord`). No per-stage time breakdown, no per-fighter win counts, no ranking pages, no name entry, no top-10. (AUDIT.md §12: no save system found; records exist but no save/progress system.)

---

## 7. Teardown data already in the repo (what was checked)

- `teardown/tekken3/` — TEARDOWN.md, CANON-CONVERSION.md, WIRING-INVENTORY.md, BODY-EXTRACTION.json, model-inventory.csv/json, tim-inventory.json, bns-table.pkl, plus dirs: animations, disc, docs, models, movesets, renders, rigging-reference, stages, tim-output, tools, ui.
- `teardown/tekken5/` — TEARDOWN.md, DEVIL-WITHIN-DATA.md, INVENTORY.md, ROSTER.md, STAGES.md, t5_char_codes.txt, t5_motion_manifest.txt, plus dirs: rigging-reference, tools, ui.
- `teardown/tekken6/` — folder exists (contents not listed in this pass — see §9).
- `teardown/tekken7/` — T7-STEAM-EXTRACTION.md, TEKKEN7-ROSTER-COVERAGE.md, TEKKEN7-ROSTER-MAPPING.md, tekken-model-catalog.md, tekken-model-pull-all.md, tekken-missing4-catalog.md, facepaint-reference.json, plus dirs: arenas, king, models, rigging-reference, tekkenmods-docs, tools, ui.
- `teardown/tekken8/` — only two dirs so far: models, ui (thinnest Tekken folder in the repo).
- `teardown/tekken-tag-tournament-2/` — TEARDOWN.md, TEARDOWN-STATUS-20261025.md, INVENTORY.md, ROSTER.md, STAGES.md, CONTAINER-ANALYSIS-20261025.md, DATA000/DATA001-DATA028 decode docs + section-table JSONs, EXTRACTION-RUNBOOK.md, TTT2-PC-PORT-ASSESSMENT.md, plus dirs: extracted-small, pulls, rigging-reference, tools, ui.
- `teardown/tekken7-steam-ui/` — folder exists (contents not listed in this pass — see §9).
- `game/data/t7-frame-data/` — 40+ Tekken 7 fighters' frame data (AUDIT.md §6).
- `game/data/t8_frame_tables.json` — 326 KB of Tekken 8 frame tables (AUDIT.md §6).
- `game/assets/movesets/` — 60+ moveset JSONs, some multi-MB (AUDIT.md §6).
- `docs/modes/TEKKEN-MODES-RESEARCH.md` — the repo's own Lane G mode research (2026-10-18), already covering Survival / Time Attack / Team / Tekken Force / Tekken Ball / Practice / Treasure / Qombat / Surge Gauntlet / Trader's Mimic. This Part A file re-measures the same ground from the primary sources and adds the arcade-ladder, select-screen, and continue measurements that the Lane G doc did not pin down.
- Note: the repo's teardown folders hold extracted commercial-game material in a public repo, against the repo's own AGENTS.md line 78 rule (AUDIT.md, "Commercial game files — flagged, not copied"). Nothing from those folders was copied into this report beyond measured behavior descriptions, and no game file was downloaded in this pass.

---

## 8. Differences table — the fix spec

Each row: measured Tekken behavior → current code → fix. "Fix" here means what to change, not a code edit (no code was edited in this pass).

| # | Measured Tekken behavior | Current code | Fix |
|---|---|---|---|
| D1 | **Select timer at 0 gives each side the fighter under the cursor** (T3 decompiled: timer `20·T` frames, T=60 or 60+3(n−10); at 0 each player gets the cursor fighter). No random pick. | **99-second timer; at 0 picks a RANDOM fighter** and overwrites the live highlight, even a confirmed pick; timer never stops on confirm. `main.js:621–657`; `select-screen.js:824–860`. Playtest Break 1. | At 0, confirm the fighter under each side's cursor; never overwrite an existing pick/highlight. Stop the timer the moment either side locks. (Exact fix already in PIECE1-DIAGNOSIS.md §1.) |
| D2 | **Arcade is one-player: one pick, then the ladder.** The second side never picks in Arcade. (T3: one human → ladder; two humans → winner goes on, loser drops out.) | **Arcade shows a two-side select screen but uses only one pick;** the ladder foe is a random draw from the whole roster. A player picking a second fighter is picking someone Arcade never uses. `modes.js:534–536`, `1375–1382`. Playtest Break 2. | In Arcade, show one pick only (or label the second side "CPU — random ladder foe"), and show the drawn foe's name/card before each fight starts. (Per PIECE1-DIAGNOSIS.md §2.) |
| D3 | **Ladder is built up front, all stages at once, with fixed bosses at fixed rungs** (T3: stages 1–4 from starters, 5–8 from unlocked, 9 Heihachi, 10 Ogre→True Ogre; T7: 5 fights, stage 4 Heihachi, stage 5 Kazumi/Akuma; T8: 8 fights, fixed stage 3/4 pools, final Devil Kazuya with perfect-round upgrades). Early foes are random but DISTINCT — never repeated, never the player's fighter, never a boss. | **Each rung's foe is drawn when the rung starts,** random from the whole roster minus player/`custom` — no distinct rule, no stage pools, no boss exclusion (King Tyrant can be drawn on rung 1), no up-front ladder shown. `modes.js:719–740`, `1375–1382`. | Build the ladder up front; draw rungs 1–4 from a non-boss pool with no repeats and never the player's fighter; keep fixed sub-boss (rung 5 Diablo — WH original, keep) and final boss (rung 6 Assembled Soul — WH original, keep); show the ladder to the player before fight 1. Gate ladder foes on a working animation bank (per PIECE1-DIAGNOSIS.md §4). |
| D4 | **On loss: CONTINUE countdown** ("CONTINUE? 9", ~13 s; Start continues; same fight restarts, or back to select if character-change is on; timer out = GAME OVER → ranking). (T3 decompiled.) | **No continue at all.** Loss = "GAME OVER" screen; only RETRY LADDER (whole ladder from rung 1) or MAIN MENU. `modes.js:752–754`. | Add a continue countdown on loss (9→1, Start = retry the SAME rung), then GAME OVER only when it runs out. Keep RETRY LADDER as the post-game-over option. Time Attack keeps its no-continues rule (already the case — loss ends the run). |
| D5 | **Endings + unlocks:** beating the final boss plays the fighter's ending movie; clears unlock fighters in a fixed order (T3) or prologue/epilogue + another fighter (T5 Story). | **Arcade clear shows WATCH ENDING** (`modes.js:758–763`) — the ending path exists — **but no unlocks, no Fight Money, no rank.** | Wire clear → unlock (next fighter in a fixed order, or a WH equivalent) and show it on the clear screen. Do not invent Tekken's exact unlock order for WH fighters — use the WH roster order. |
| D6 | **Costume is picked at select by button** (T3: Square = costume 0, X/Circle = costume 1, Triangle/Start = costume 2). | **No costume step found** in the select flow (`modes.js` `onConfirm`, select screen). | Add a costume pick at select (button-cycled, like T3) or mark costumes as a separate lane. UNMEASURED whether costumes exist anywhere in the current build — check before building. |
| D7 | **Locked slots cannot be picked; taken slots show as taken** (T3: locked = `0x58`, taken = `0x59` / "SOLD OUT" on quick select; team picks remove the fighter from the side's mask). | **No locked/taken slot behavior found** in the current select code. | Show locked fighters greyed out and unpickable; in Team Battle, mark already-picked fighters as taken on the same screen. |
| D8 | **Versus: stage random for game 1; loser picks stage / may change fighter after a loss; winner locked to the same fighter** (T7 tournament rules). | **Versus reuses the same setup on rematch;** no loser-picks-stage step, no winner-lock rule. `modes.js:613–646`. | After a Versus loss, offer the loser: same fighter + same stage, same fighter + new stage, or new fighter + random stage. Lock the winner's fighter until a loss. |
| D9 | **Tag (TTT2):** two fighters per side, Tag button swaps mid-fight, resting partner regains recoverable health, Tag Combo / Tag Assault / Tag Throw / Tag Crash, one K.O. wins the round. | **No tag system at all** — no tag button, no partner swap, no recoverable health. Team Battle exists but is winner-stays-on, not tag. | Tag is a new system, not a fix — schedule as its own lane. Do not bolt tag onto Team Battle; the two modes have different rules. |
| D10 | **Team Battle: up to 8 per side** (T3 quick select: team size 1–8); CPU team filled least-met first, shuffled; result screen replays each fight with winner lines. | **3v3 only, no size choice;** CPU team pure random; end screen is a one-line tally. `modes.js:350`, `1160–1174`, `1203–1211`. | Add team-size choice (1–8, or at least 3/5/8); fill the CPU team least-used first instead of pure random; add the per-fight replay result screen. |
| D11 | **Training/Practice:** FREE / VS CPU / COMBO TRAINING sub-modes; dummy STAND/CROUCH/GUARD ALL/CONTROLLER; CPU difficulty + level; attack-data HUD; key display; record/playback; freeze-signal glow (green = can act, red = cannot). (T3 decompiled.) | **Passive dummy only** (+ Gungaku programmable dummy). No sub-modes, no dummy settings, no attack data, no key display, no record/playback. `modes.js:962–1001`. | Add, in order: dummy stance/guard settings, then attack-data HUD (damage + counter/clean-hit labels), then VS CPU difficulty/level, then record/playback. Gungaku already covers the programmable half. |
| D12 | **Survival: CPU level in stepped bands by wins** (T3: <5 → 1–3, <10 → 2–4, <20 → 3–7, then 3–9); **never repeats any of the last four opponents; favors least-met fighters;** result screen shows per-fighter win counts + top-10 rank line. | **Flat linear difficulty** (0.45 + 0.05/wave); **pure random foe, repeats allowed;** result is one line ("Fell at wave N. Best run: M"). `modes.js:1003–1039`. | Use stepped difficulty bands; exclude the last four foes; prefer least-met foes; add the per-fighter win-count result screen. (The 25% restore per win is UNMEASURED against Tekken — "a small amount" is all the sources say — so do not change it on this evidence alone.) |
| D13 | **Time Attack: 9 stages (T5) / 10 stages (T3), 2-round 60-second fights, fixed defaults; result shows every stage time + total + NEW RECORD; no continues; no endings.** | **8 single-round fights;** result shows total time + grade only (S < 4:00, A < 6:00, B < 9:00 — invented thresholds); no per-stage times. `modes.js:1096–1145`. | Use 9 or 10 fights of 2 rounds / 60 seconds (pick one and say which); show per-stage times + total on the result screen; keep no-continues (already correct). Grade thresholds need a measured source or must be labeled WH-original. |
| D14 | **Treasure Battle (T7):** endless fights, 1–3 chests per win, per-fighter rank ladder (9th Kyu → Warrior), random Special Matches vs powered-up bosses (bigger damage, Rage Art = instant loss). | **1 chest per win, no rank ladder, no Special Matches;** health fresh each wave. `modes.js:1041–1095`. | Add the rank ladder with promotion matches; add Special Matches (powered-up boss foe, better chest); chests 1–3 per win instead of exactly 1. |
| D15 | **Pause: Start pauses mid-round; only CANCEL unpauses; menu = CANCEL / COMMAND (move list) / RESET; music volume drops.** (T3 decompiled.) | **Pause button unclickable in fights; Escape does nothing.** (Playtest Break 7; PIECE1-DIAGNOSIS.md §7.) | Fix per diagnosis §7 (pointer-events on `#wh-pause-btn`, Escape handler, pause menu with CANCEL / COMMAND / RESET). |
| D16 | **Stages change per ladder rung; boss stages are fixed** (T7: stage 4 Mishima Dojo, final Devil's Pit / Abandoned Temple). | **Whole Arcade ladder plays on the one stage picked at stage select,** as far as the code read shows — no per-rung stage in `_arcadeNext`. | Assign a stage per rung when the ladder is built (D3); fix boss stages (rung 5 / rung 6) to their own stages. |
| D17 | **Arcade rounds/time are changeable in options; Time Attack uses fixed defaults.** (Tekken Wiki Arcade Mode.) | **No options step in the Arcade flow;** Arcade starts straight from select. | Add a pre-ladder options step (rounds, round time, difficulty) for Arcade; keep Time Attack fixed. |

---

## 9. Still UNMEASURED (do not guess — measure next)

1. **T7/T8 select timer:** exact seconds on the character-select countdown in Tekken 7 and Tekken 8, and exactly what happens at 0 (cursor pick? random? auto-confirm?). No public source checked states it. The only measured timer is Tekken 3's (~20 s, grows with unlocks, cursor pick at 0).
2. **T7/T8 locked/DLC slot behavior:** exactly how locked and unpurchased-DLC slots look and behave on the T7/T8 select screen (greyed? hidden? "SOLD OUT"?). T3's locked (`0x58`) / taken (`0x59`) values are measured; T7/T8 equivalents are not.
3. **T7/T8 continue rules in detail:** exact continue countdown length and options in Tekken 7/8 Arcade (the T3 "CONTINUE? 9" is measured; T7's is only known as "you can continue, restart from round 1 of Kazumi's human form").
4. **Survival restore amount:** Tekken's sources say only "a small amount" of health back per win. No exact percent was found, so the current game's 25% cannot be confirmed or denied.
5. **Tekken 5/6/7 stage order in Arcade:** which stage each early ladder rung uses in T5/T6/T7 (only the boss stages are pinned: T7 stage 4 Mishima Dojo, final Devil's Pit/Abandoned Temple).
6. **Costumes in the current build:** whether any costume system exists at all in Western Heart (no costume step was found in `modes.js`/`main.js` select flow). Check `game/js/attires.js` + `customization/` before building D6.
7. **Stage-per-rung in the current build:** whether the stage actually stays the same through the whole Arcade ladder in the live build (no per-rung stage code was found, but the playtest only played one stage — needs a live check).
8. **Repo teardown folder contents (top level only):** the file listings in §7 are top-level names only. What is *inside* the subfolders (e.g. `teardown/tekken3/movesets`, `teardown/tekken7/models`, `teardown/tekken6/` and `teardown/tekken7-steam-ui/` entirely) is UNMEASURED here. Pull the next level before Part B.
9. **Tekken 6 Scenario Campaign and Tekken 8 Story Mode detail:** named but not measured step-by-step (they are beat-'em-up / chapter systems, not ladders, and are outside the arcade/ladder scope of this pass).
10. **T7/T8 Versus stage-select flow in-game:** the loser-picks-stage rule is from tournament rules; the in-game casual Versus flow (who picks the stage, when) is UNMEASURED.

---

## 10. Sources (every claim traces to one of these)

**Repo files (HEAD `3334ebf`):**
- `game/js/modes.js` (1,418 lines) — MODE_LIST lines 286–310; ARCADE_LADDER 122–131; STORY_STAGES 98–120; `_arcadeNext`/`_arcadeEnd`/`_arcadeClear` 718–763; `_beginVersus` 609–646; `_beginTraining` 962–971; `_survivalNext`/`_survivalEnd` 1003–1039; `_treasureNext`/`_treasureEnd` 1041–1095; `_timeAttackNext`/`_timeAttackEnd`/`_timeAttackClear` 1096–1145; `_teamFight`/`_teamEnd` 1146–1211; `_pickFoe` 1375–1382; `SURVIVAL_CFG` 326; `TEAM_CFG` 350; grade thresholds 337–348.
- `game/js/main.js` — select timer lines 621–657 (99 seconds, random pick at 0, never stopped on confirm).
- `game/js/select-screen.js` — lines 824–860 (highlight overwrites a pick unless locked), via PIECE1-DIAGNOSIS.md §1.
- `docs/modes/TEKKEN-MODES-RESEARCH.md` — repo Lane G research (2026-10-18): Survival §1, Time Attack §2, Team §3, Tekken Force/Devil Within §4, Tekken Ball/Bowl §5, Practice §6, Treasure §7, Qombat §8, Surge Gauntlet §9, Trader's Mimic §10.
- `~/workspace/western-heart-audit/PLAYTEST-PIECE1.md` — 9 breaks, live playtest 2026-11-07.
- `~/workspace/western-heart-audit/PIECE1-DIAGNOSIS.md` — causes found in code (Breaks 1, 2, 7 cited here).
- `~/workspace/western-heart-audit/AUDIT.md` — repo audit 2026-11-06 (frame data, movesets, best-of-3/60 s, no save system).

**Public sources (links):**
- Tekken Wiki, Arcade Mode — https://tekken.fandom.com/wiki/Arcade_Mode (T1/T2/T3/T5/T6/TTT2/T7/T8 arcade ladders, bosses, endings, ranks, money)
- Tekkenpedia, Tekken 5 — https://eng.tekkenpedia.com/wiki/T5/ (Story Mode 9 stages, sub-bosses, Devil Within, Time Attack 9 stages / 2 rounds / 60 s)
- n0madic/Tekken3Remake, `docs/research/code/modes.md` — https://github.com/n0madic/tekken3remake/blob/HEAD/docs/research/code/modes.md (decompiled T3: arcade ladder build, select screen + timer, continue, pause, challenger, practice, survival/team/time-attack results, Ogre scene)
- Tekken Wiki, Treasure Battle — https://tekken.fandom.com/wiki/Treasure_Battle (endless fights, 1–3 chests, per-fighter ranks, Special Matches)
- Tekken Wiki, Tag Assault — https://tekken.fandom.com/wiki/Tag_Assault (TTT2 tag mechanics)
- Tekken Tag Tournament 2 Xbox 360 manual (archive.org) — https://archive.org/stream/xbox-360-marketplace-game-manuals/TEKKEN%20TAG%20TOURNAMENT%202%20%284E4D0859%29_djvu.txt (tag features, Arcade Battle, Ghost Battle)
- UNIFIED Tekken 7 competition rules — https://unified.gg/e/FANILL0223/c/FANILL0223TK7/rules (first to 3 rounds, 60 s timer, random stage game 1, winner locked / loser may change)
- Windows Central, Tekken 7 Xbox One Achievement Guide — https://www.windowscentral.com/tekken-7-achievement-guide (Arcade Akuma conditions, Treasure Battle no-continue, Special Matches)
- Eurogamer, Tekken Tag Tournament 2 review — https://www.eurogamer.net/tekken-tag-tournament-2-review (tag swap, recoverable health, Tag Assault/Crash/Throws)
- PowerPyx, Tekken 7 review — https://www.powerpyx.com/tekken-7-review (offline modes list: Arcade 5 opponents, Treasure Battle endless, VS Battle, Practice Mode; Story 14 chapters + epilogue + special match)
