# Western Heart — Tekken Teardown Spec (the fixes must follow this)

**Date:** 2026-11-08
**Repo:** `mhvnsnt/western-heart`, HEAD `3334ebf`
**Sources:** the five teardown part files in this same folder — Part A Tekken modes (`TEARDOWN-PART-A-TEKKEN-MODES.md`), Part B Devil Within + HeartMind (`TEARDOWN-PART-B-DEVIL-WITHIN.md`), Part C Urban Reign + Redux (`TEARDOWN-PART-C-URBAN-REIGN.md`), Part D roster gating + archive.org (`TEARDOWN-PART-D-ROSTER-ARCHIVE.md`), Part E wireable inventory (`TEARDOWN-PART-E-WIREABLE-INVENTORY.md`) — plus the playtest (`PLAYTEST-PIECE1.md`), the diagnosis (`PIECE1-DIAGNOSIS.md`), and the audit (`AUDIT.md`). Every behavior claim below traces to one of those files, which carry the full links. Anything not measured is marked **UNMEASURED** — never filled in by guessing.
**Names:** Pantera is male (he/him). Every other fighter is named by name only, no guessed pronouns.

## Why this spec exists

Jay's correction, 2026-11-07: stop guessing, hand-tooling, and making up how things should go. Fixes must copy how the actual games work, measured from teardowns — then the chimera order: use the most of the actual code and data possible. The fix team was stopped mid-fix and told to wait for this spec.

Two rules live side by side, both recorded plainly:
- **Jay's order (chimera):** use the most actual code/data possible — repo teardown files, frame data, move tables, banks, stage data, modding-community sources.
- **Standing limit (unchanged):** measure the behavior and rebuild it in our own code. Commercial game code files, models, art, audio, logos, and dialogue are NOT copied into the game, even privately. Jay's contrary position (use the actual files) is recorded as his, not adopted here. §8 inventories everything with an origin flag per item so the line stays visible; inventory is not approval.

---

## 1. Arcade mode — measured, step by step

### 1a. Tekken 3 arcade (most fully measured — decompiled code)

Source: Part A §1a — n0madic/Tekken3Remake `docs/research/code/modes.md` ("confirmed from decompiled code", Japan Rev.1) + Tekken Wiki Arcade Mode.

1. Title → main menu → Arcade. (T3 modes doc, "Game states".)
2. Character select: one player picks one fighter. 2-row grid, 11 positions per row; only unlocked fighters get a cell.
3. Pre-fight VS screen: portraits slide in over 8 frames, then the fight loads.
4. **The ladder is built BEFORE the first fight, all 10 stages at once** — fighter, costume, and stage filled up front (`ArcadeBuildLadder`).
5. Stages 1–4: random, distinct fighters from the ten starting fighters — never the player's own fighter, never the stage-9 boss.
6. Stages 5–8: random, distinct fighters from the unlocked fighters — never Heihachi, Ogre, or True Ogre. (Once Tekken Ball has been played, Gon joins this pool even while locked.)
7. Stage 9: fixed boss — Heihachi. Exception: if the player is Heihachi, the boss is Jin Kazama.
8. Stage 10: fixed final boss — Ogre. After the player wins one round against Ogre, a short scene plays (Ogre picks up the defeated stage-9 boss and holds him overhead) and the fight continues against **True Ogre** in the same match, keeping the same round score. Even with 1-round matches set, both Ogre and True Ogre are fought.
9. Difficulty climbs with the ladder: CPU level for each stage is its index (0–9).
10. Costumes: opponents wear costume 1 when the player's costume is not 0, otherwise costume 0. Ogre and True Ogre always wear costume 0.
11. **On a loss: CONTINUE.** "CONTINUE? 9" countdown (9 down to 1, ~13 seconds total). Pressing Start continues. With "CHARACTER CHANGE AT CONTINUE" OFF, the same fight restarts. With it ON, the player goes back to character select. Timer out = GAME OVER, then the ranking screen.
12. On a win at stage 10: the ending movie plays, then the staff roll.
13. Unlocks: clearing Arcade unlocks fighters in a fixed order, one per clear, each clear with a different starting fighter: Kuma → Julia Chang → Gun Jack → Mokujin → Anna Williams → Bryan Fury → Heihachi Mishima → Ogre → True Ogre. Unlocked fighters join the CPU roster from stage 4 onward.
14. Two humans: if a second player joins, the winner goes on up the ladder and the loser drops out. A non-playing player can join from the 8th frame of a fight ("A NEW CHALLENGER ENTERS!!").
15. Round rules: default round timer 40 seconds in Tekken 3 (last game with a 40-second default). Rounds and time limit are changeable in the options.

### 1b. Tekken 5 — Arcade and Story are two different modes

Source: Part A §1b — Tekken Wiki Arcade Mode (Tekken 5 section), Tekkenpedia Tekken 5.

- **Tekken 5 Arcade Mode is NOT a fixed ladder.** It is an unlimited ranked ladder: endless AI fighters for money and rank (kyu/dan). Opponent rank decides money (default 1,000G at equal rank, −200G per rank lower, +100G per rank higher; 800G–4,000G per win). Wins/losses move promotion/demotion points (3 to promote, −3 to demote). This later became Ghost Battle in Tekken 5: Dark Resurrection.
- **Tekken 5 Story Mode IS the traditional arcade ladder.** 9 stages: 8 AI fighters, then Jinpachi Mishima as final boss on stage 9. Sub-bosses at stages 4, 7, and 8 — usually Devil Jin — with cut-scenes. Measured exceptions: for Hwoarang the stage-8 boss is Jin Kazama; for Kazuya, Raven, and Wang Jinrei it is Heihachi Mishima; for Heihachi it is Kazuya Mishima; for Devil Jin it is Asuka Kazama; Jin Kazama and Asuka Kazama face no boss on stage 8, just a random fighter.
- Story Mode flow: short prologue before the ladder, epilogue + ending movie after beating Jinpachi. Clearing Story Mode unlocks the prologue and epilogue of the fighter played, plus another fighter. Devil Jin is the exception: unlocked by 200 matches or by clearing the Devil Within minigame.
- Tekken 5 Time Attack: 9 stages, fixed defaults (2 rounds, 60 seconds per round, normal difficulty), fastest total time wins; 25G per match, 50G for beating Jinpachi.

### 1c. Tekken 7 arcade

Source: Part A §1c — Tekken Wiki Arcade Mode (Tekken 7 section).

1. Only 5 fights. First three opponents randomly selected. Stage 4 fixed: Heihachi Mishima in the Mishima Dojo.
2. Final boss, stage 5: Kazumi Mishima in Devil's Pit — or Akuma in the Abandoned Temple, if ALL three hold: (a) at least one perfect round in the first four stages, (b) win the first four fights in under three minutes, (c) no continues used.
3. Kazumi transforms mid-match: after the player wins a round against Kazumi, Kazumi becomes Devil Kazumi and the fight moves to the second part of Devil's Pit. If the player is K.O.'d in round 1, the fight stays in round 1 form until a round is won.
4. Final stage is always 2 rounds, even if options are set to 1 round; after the final stage it goes back to 1 round.
5. After the final boss: defeat animation, then credits. Large amount of Fight Money. The player also earns offline rank from Arcade Mode.

### 1d. Tekken 8 arcade

Source: Part A §1d — Tekken Wiki Arcade Mode (Tekken 8 section).

1. 8 stages. Stages 1–2 random opponents. Stage 3: Azucena Ortiz, Victor Chevalier, or a DLC fighter. Stage 4: Jin Kazama, Jun Kazama, Lars Alexandersson, or Reina.
2. Ghost opponents (AI trained on a real player's style) appear stages 5–7.
3. Final boss, stage 8: Devil Kazuya at Fallen Destiny. Upgrades if the player scores perfect rounds AND has cleared Chapter 14 of Story Mode: 1 perfect round → Azazel; 2 → True Devil Kazuya; 3+ → Angel Jin.
4. No credits roll after the final boss in this version, and it is the only version with no visible timer during stages.

### 1e. Tekken 6 and Tekken Tag Tournament 2 arcade (short)

Source: Part A §1e — Tekken Wiki Arcade Mode (Tekken 6 + TTT2 sections).

- **Tekken 6:** like the arcade version. Extra stage boss NANCY-MI847J (bonus fight — win or lose, the player still goes on; pays bonus Fight Money). Then Jin Kazama as sub-boss, then Azazel as final boss for all fighters. After beating Azazel the credits play with NO character ending.
- **TTT2:** 6 random ghost fights, then 3 boss fights: stage 7 is the tag team Heihachi Mishima + Jinpachi Mishima; stage 8 is True Ogre (alone, full health bar must be emptied, slowly regains health); final stage is Jun Kazama, who changes into Unknown for the second round. Reaching the final stage forces 2 rounds even on 1-round settings. Beating Arcade unlocks the fighter's ending (except Tiger Jackson, who goes straight to the staff roll).

### 1f. What the current game does (Arcade)

Source: Part A §1f — `game/js/modes.js` lines 122–131, 718–763, 1375–1382.

- 6 fights: rungs 1–4 random foe, rung 5 fixed Diablo ("DIABLO — SUB-BOSS"), rung 6 fixed Assembled Soul ("ASSEMBLED SOUL — FINAL").
- Difficulty per rung: 0.50, 0.58, 0.66, 0.74, 0.85, 0.95.
- Rungs 1–4 foes are picked by `_pickFoe`: random from the whole roster, only excluding the player's fighter and `custom`. No stage pool, no "distinct" rule (same foe can be drawn twice), no locked/boss exclusion — any roster fighter can appear, including King Tyrant.
- On a loss: no continue countdown. "GAME OVER / The ladder stands. The shrine is silent. Climb again." with one button, RETRY LADDER, restarting the whole ladder from rung 1. No retry-the-same-rung, no character-change option, no ranking screen.
- On a win at rung 6: "ARCADE CLEARED" screen with a WATCH ENDING button.
- No prologue before the ladder, no unlocks for clearing, no Fight Money, no rank.
- **The ladder is NOT built up front.** Each rung's foe is drawn when that rung starts, so the player never sees the ladder ahead of time.

---

## 2. Character select screen — measured

### 2a. Tekken 3 select (decompiled code)

Source: Part A §2a — n0madic/Tekken3Remake `docs/research/code/modes.md`, "Character select".

- **Layout:** two rows of 11 positions. Only the first ten positions of a row are drawn on screen (35 pixels apart); the 11th (Gon) is reached by moving past either end — the cursor goes invisible there and Gon's big portrait appears, with blinking arrows at the ends of the grid hinting at it for the first 180 frames.
- **Locked slots:** a locked fighter's cell value is `0x58` — it cannot be picked. A fighter that is unlocked but not available in this selection is `0x59` — also cannot be picked, and each team pick removes that fighter from the side's available mask.
- **Costumes by button:** Square = costume 0, X or Circle = costume 1, Triangle or Start = costume 2 when the fighter is in the Start-costume mask, otherwise Triangle = costume 0.
- **P1/P2 picking:** both sides choose at the same time, each with its own cursor and big portrait (126 × 208, facing each other). A side with nothing chosen yet shows a silhouette. If both sides pick the same fighter and costume, the later picker's costume changes (0/1 swap; 2 and 3 become 0) — unless only one side is human.
- **Timer — the key measurement:** the timer starts at `20 · T` select-screen frames, where T = 60, or 60 + 3·(n − 10) when more than 10 fighters are unlocked. It counts down once per frame **while both players are choosing**, and **at 0 each player gets the fighter under the cursor** — the cursor's current fighter, NOT a random one. (At 60 fps, 20·60 = 1,200 frames = 20 seconds with 10 or fewer unlocked; it grows by 3 seconds per extra unlocked fighter.)
- **Cursor memory:** each player's cursor starts at the last pick when SELECT CURSOR HOLD is on.
- **Exit:** Start + Select together returns to the main menu from select and from fights.
- **VS screen after select:** portraits slide in over 8 frames, then the fight loads.
- **Quick select (VS / team / Tekken Ball):** a different, smaller screen — a 3 × 7 grid, team-size choice (1–8 players per team), "NO ENTRY" for a locked cell, "SOLD OUT" for a taken one, and a 480-frame idle slide-out showing "PUSH START+SELECT TO EXIT".

### 2b. Tekken 7 / Tekken 8 select — what could be measured

Source: Part A §2b.

- **Layout:** a grid of fighter portraits with a large portrait + name on each side, P1 on the left (red side), P2 on the right (blue side), a RANDOM select slot, and locked/DLC slots shown greyed out until bought/unlocked. Costume is picked on the same screen (preset 1–4, changed with a button before confirming). Stage select follows character select (or is random in Versus).
- **Timer value, exact random-select behavior, and exact locked-slot behavior in T7/T8: UNMEASURED.** No public source checked states the T7/T8 select timer in seconds or what exactly happens at 0. The T3 decompiled measurement above is the only timer with a measured value.
- **Versus rules (T7, tournament rules):** rounds "first to three", timer 60 seconds, stage select random for the first game; the loser of a game may change fighter or stage, the winner is locked to the same fighter. (UNIFIED Tekken 7 competition rules.)

### 2c. What the current game does (select)

Source: Part A §2c — `game/js/main.js` lines 621–657, 901–919; `game/js/select-screen.js` lines 824–860; `game/js/modes.js` lines 508–540.

- **Timer is 99 seconds** (comment in code: "Tekken standard selector: starts at 99"). It starts only once assets are loaded.
- **At 0 it picks a RANDOM fighter** from the whole roster except the current `selectedChar`, and overwrites the live highlight via `selectById` — even if a fighter was already picked on the other side. The timer is never stopped when a fighter is confirmed. This is Playtest Break 1.
- **There is no measured Tekken source for a 99-second timer or a random pick at 0.** Tekken 3's measured timer is ~20 seconds (growing with unlocks) and gives each side the fighter under the cursor at 0. The 99 seconds and the random pick are both invented, not teardown.
- **Arcade shows a two-side select screen but only uses one pick.** `onConfirm` in Arcade takes one fighter and starts the ladder (`modes.js:534–536`); the ladder foe is a random draw (`_pickFoe`). A player picking a second fighter is picking someone Arcade never uses. This is Playtest Break 2.
- **Versus flow in code:** P1 picks, then the hint changes to "VERSUS — Player 2: choose your soul", then P2 picks, then `_beginVersus(p1, p2)` (`modes.js:516–533`, `613–637`). Both locked picks go straight through — no Versus path swaps a locked P2. Team Versus (draft) is checked first (`_vsDraft`, `modes.js:512–515`).
- **No costume pick on the select screen** in the current game (no costume step was found in `modes.js` `onConfirm` or in the select flow). Tekken 3 picks costume by button at select; T7/T8 pick a preset on the same screen. Whether costumes exist at all in the current build is **UNMEASURED** — check `game/js/attires.js` + `customization/` before building.
- **No locked/unavailable slot behavior** was found in the current select code (no `0x58`/`0x59` equivalent).

---

## 3. Every other mode — measured flow, and what the current game has

### 3a. Versus 1V1

**Measured (Tekken):** Two players, each picks one fighter on the same select screen (T3: both cursors live at once; T7: P1 then P2 on one screen). Then stage select (T7: random for game 1; loser picks after a loss). Best of rounds — T3 default 2 rounds to win a match, 40-second round timer; T5 Time Attack defaults 2 rounds / 60 seconds; T7 tournament standard first to 3 rounds, 60-second timer. After the match, back to select (T3: VS end hook goes back to select, win/draw stats kept). A second player can join mid-fight in arcade-style modes ("new challenger"); in pure VS the two sides are set at select.
Sources: Part A §3a — T3 modes doc; Tekkenpedia T5; UNIFIED T7 rules.

**Current game:** implemented. `modes.js:609–646` (`_beginVersus`): P1 vs P2, rounds/time/guard-damage from Versus setup rules, stage random from a pool when stage mode is random. Keeps Versus setup rules + result screen + REMATCH. **Difference:** no measured stage-pick step for the loser after a loss (rematch reuses the same setup); no double-blind select; no "winner locked / loser may change" rule.

### 3b. Tag (Tekken Tag Tournament 1/2)

**Measured (Tekken):** Each side picks TWO fighters. Tag button swaps the active fighter with the partner at almost any moment; the resting partner slowly regains health (the red/recoverable part of the bar). Only one of the opponent's two fighters needs to be K.O.'d to win the round. Tag Combo: press Tag right before a launcher hits — partner runs in and continues the juggle. Tag Assault (TTT2): press Tag right before a Bound move hits — partner jumps in and attacks for a short time, then swaps back; costs the partner's recoverable health, and the opponent's partner gets Rage. Tag Throw: Tag + right punch together — both fighters grab at once. Tag Crash: when the resting partner is in Rage (bar flashing red) and the active fighter is down, the partner barges in to break pressure, at the cost of red life. Solo vs Tag is allowed: one fighter against two gets double health and slowly regains the tagged-out bonus during the fight. TTT2 Arcade Mode is tag: 6 random ghost fights, then Heihachi + Jinpachi as a tag team, then True Ogre, then Jun → Unknown.
Sources: Part A §3b — Tekken Wiki Tag Assault; TTT2 Xbox 360 manual (archive.org); Eurogamer/NAG TTT2 reviews.

**Current game:** NOT implemented as a tag system. No tag button, no partner swap, no recoverable-health bar, no Tag Assault/Combo/Crash in `modes.js` or the fight core as read. `modes.js` has `_beginTeamVersus` (team draft) and TEAM BATTLE (§3c), but those are "one fighter at a time, winner stays on" — not tag. **Tag is a missing mode/system, not a wrong one.** Schedule as its own lane; do not bolt tag onto Team Battle.

### 3c. Team Battle

**Measured (Tekken):** Debut Tekken 2; present through TTT2; cut from T7 (a fan mod later restored it for T8). Each side fields a team of up to 8 fighters (T3 quick select: team size 1–8). Winner stays on: when a fighter falls, the next in line steps in. The winner's health carries over and increases slightly per win (T5:DR-era convention ~10–15% recovery). After the last member falls, a win/loss tally is shown. T3 decompiled detail: CPU team filled from unlocked fighters not already in the team, least-met first, shuffled into free places; CPU level = difficulty + 3 + option, +1 or +3 when the human side has more members left; result screen replays each fight one by one with a red/yellow/grey line per winner and ends "YOU WIN!" / "YOU LOSE!" / "DRAW GAME", or "PLAYER-1 WINS!" / "PLAYER-2 WINS!" with two humans. T3 team pick flow: each team pick removes that fighter from the side's available mask (cell `0x59`, "SOLD OUT" on quick select).
Sources: Part A §3c — repo `docs/modes/TEKKEN-MODES-RESEARCH.md` §3; T3 modes doc.

**Current game:** implemented. `modes.js:350` (`TEAM_CFG = { size: 3, restore: 0.15 }`), `508–588` (3-pick flow with a tray, duplicates refused), `1146–1211` (`_teamFight`, `_teamEnd`). 3v3. Single-round fights, winner keeps remaining HP + 15% recovery. CPU team is 3 random fighters. End screen shows the tally (fighters left per side). **Differences:** team size 3, not up to 8; no team-size choice at select; CPU team is pure random (no least-met / least-used rule); no per-fight replay result screen — just a win/lose message.

### 3d. Training / Practice

**Measured (Tekken 3 Practice, decompiled):** Mode 5, `practice.ovl`. Three sub-modes from MODE SELECT: FREE, VS CPU, COMBO TRAINING, plus PLAYER SELECT (back to character select) and RESET (main menu). FREE dummy settings: STAND, CROUCH, STAND GUARD, CROUCH GUARD, GUARD ALL, AUTO GUARD, UKEMI MAE, UKEMI OKU, CONTROLLER (second pad drives the dummy). VS CPU: CPU DIFFICULTY (EASY/MEDIUM/HARD) + CPU LEVEL (STAGE 1…9, FINAL STAGE). COMBO TRAINING: pick a combo from the fighter's list, guide shows the inputs, key display shows the last 15 inputs. Always on: ATTACK DATA (damage numbers, TOTAL DMG, COUNTER / CLEAN HIT labels, combo + damage counters), KEY DISPLAY (input history), COMMAND LIST (move list overlay), REPLAY SETTINGS (record/play back 4/5/6-hit combos or manual), FREEZE SIGNAL (the fighter glows green when it can act, red when it cannot — a live frame-advantage display). Pause menu in practice is its own menu (Start pauses only in practice via its own path; in other modes Start pauses and only CANCEL unpauses). T5+ added command display, frame data, and punishment training on top of this. T7 Practice Mode: same idea — free sparring vs a configurable dummy, with command display and frame data.
Sources: Part A §3d — T3 modes doc "Practice" + "Pause"; repo Lane G research §6; PowerPyx T7 review.

**Current game:** implemented in basic form only. `modes.js:962–971` (`_beginTraining`): endless round vs a passive dummy (aggression 0, grab 0, reaction 0, passive true), badge "TRAINING · DUMMY WILL NOT FIGHT BACK", quit button shown, rounds auto-reset. Plus FIGHT LAB / GUNGAKU (`modes.js:973–1001`): same shell, dummy runs a program (presets + record-your-own), panel mounted by `fightlab-gungaku.js`. **Differences (all missing):** no FREE / VS CPU / COMBO TRAINING choice; no dummy stance/guard settings; no CPU difficulty/level; no attack-data HUD (damage numbers, counter/clean-hit labels); no key/input display; no record/playback; no freeze-signal glow; no command-list overlay in training.

### 3e. Survival

**Measured (Tekken):** Debut Tekken 2; present in every sequel since. Endless stream of CPU opponents, **one round per fight**, health **carries over** — the bar is never refilled to 100%; each win restores only a small amount. Lose once and the run ends. Score = opponents beaten. T2/T3 showed top-10 leaderboards; T3 let the player unlock Gon by entering "GON" as initials. T3 decompiled detail: CPU level from wins — under 5 wins → level 1–3; under 10 → 2–4; under 20 → 3–7; under 50 → 3–7 (group 2 when an option bit is set); then every tenth win level 0, otherwise 3–9 with group 2. Opponent pool: the ten starting fighters for stages 0–6, then everyone but Ogre/True Ogre for 7–16, then everyone — never repeating any of the last four opponents; picks favor the least-met fighters. Result screen: "SURVIVAL RESULT", a portrait cell per fighter beaten with its win count, sorted by wins, TOTAL wins, then "YOU ARE THE nTH GREATEST SURVIVOR!" for a top-ten place or "YOU NEED MORE PRACTICE!".
Sources: Part A §3e — repo Lane G research §1; T3 modes doc "Survival opponents" + result state 14.

**Current game:** implemented. `modes.js:326` (`SURVIVAL_CFG = { restore: 0.25, roundsToWin: 1 }`), `1003–1039`. One round per fight, HP carried + 25% restore per win, difficulty 0.45 + 0.05 per wave (capped 0.95), record = waves beaten in localStorage, "RUN OVER" screen on loss with best-run line. **Differences:** restore is 25% (Tekken's measured amount is "only a small amount" — no exact percent was found, so 25% is **UNMEASURED** against Tekken, not proven wrong); foe pool is the whole roster at random with no least-met rule and no last-four exclusion, so the same foe can repeat back-to-back; no per-fighter win-count result screen; no leaderboard/top-10; difficulty is a flat linear ramp, not Tekken 3's stepped bands.

### 3f. Time Attack

**Measured (Tekken):** Debut Tekken 2; T3 identical (minus Gon/Dr. Bosconovitch fights). Same ladder shape as Arcade, but the clock is the score: fastest total time wins. T5 fixed the format at 9 stages with default settings (2 rounds, 60 seconds per round, normal difficulty). No pausing until T4. No endings, no credits — the timer is the game. T3 decompiled detail: Time Attack is the arcade ladder with a restricted character mask (`0x157FFF`); after the tenth fight it records the time and shows the result: "TIME ATTACK CLEAR!", ten stage rows one every 23 frames with `STAGE n`, opponent portrait, and stage time, then YOUR TIME (sum of the ten stage times) and the winner's portrait; NEW RECORD blinks when a record is pending. The Ogre scene is skipped in Time Attack. Tekken's rule: **no continues in Time Attack.**
Sources: Part A §3f — repo Lane G research §2; T3 modes doc.

**Current game:** implemented. `modes.js:337–348` (grade thresholds S < 4:00, A < 6:00, B < 9:00, else C), `1096–1145`. 8 single-round fights against escalating AI (difficulty 0.50 → 0.90), wall-clock time accumulated per fight, clock starts when the round actually begins (not during model loads), loss ends the run, clear shows grade + total time + best time. **Differences:** 8 fights, not 9 (T5) or 10 (T3); single-round fights, not 2-round / 60-second rounds; grade thresholds (S/A/B/C times) are invented — no measured Tekken source gives S < 4:00; no per-stage time breakdown on the result screen (only a total); foes are random from the whole roster, not the arcade ladder shape with fixed bosses.

### 3g. Story / Career (Tekken 4/5/6/7/8 — the "Story Mode" line)

**Measured (Tekken):**
- **Tekken 4:** what was Arcade Mode became "Story Mode" (per-fighter story, prologue + epilogue around the ladder, Heihachi as final boss for most; Jin as final boss for Hwoarang and Kazuya; Kazuya as final boss for Heihachi, fought right before Heihachi). Arcade Battle became a separate mode with changeable options and nothing unlockable.
- **Tekken 5:** Story Mode = 9-stage ladder with sub-bosses at stages 4/7/8 (usually Devil Jin) + cut-scenes, Jinpachi final boss, prologue before + epilogue/ending after, unlocks prologue+epilogue of the fighter played plus another fighter.
- **Tekken 6:** Scenario Campaign — a beat-'em-up story mode (not a ladder). Arcade Mode is separate.
- **Tekken 7:** The Mishima Saga — 14 chapters + epilogue + a "special match", mostly cut-scenes with one two-round fight per episode; separate from Arcade Battle.
- **Tekken 8:** Story Mode "The Dark Awakens" — chapters; Arcade Mode's upgraded final bosses are gated on clearing Chapter 14.
- **Tekken 3 has no Story Mode** — Arcade Mode IS the story (ending movie per fighter).
Sources: Part A §3g — Tekken Wiki Arcade Mode; Tekkenpedia T5; PowerPyx T7 review.

**Current game:** Story is a Western Heart original, not Tekken's Story Mode. `modes.js:98–120` (`STORY_STAGES` — 7 stages: Wood → Fire → Earth → Metal → Water → Phantom Marketplace trade → Final Shrine boss), `765–960` (Trial + reincarnation: death picks a new vessel by style profile, Diablo offers himself only after 3+ deaths, Trader stage, Assembled Soul final boss). This is canon-grounded (CANON.md §5 The Trial), not a Tekken copy — that is by design, and it is the one mode where "differs from Tekken" is not a defect. **Difference worth naming anyway:** Tekken's Story Mode is a fixed ladder with prologue/epilogue movies and unlocks; the current Story has an intro cutscene and reincarnation, but no per-fighter prologue/epilogue movies and no unlock-on-clear.

### 3h. Treasure Battle (Tekken 7)

**Measured (Tekken):** A modified Ghost Battle (T6/TTT2). Endless opponents; every win grants 1–3 chests (Fight Money or customization items) and moves the fighter's offline rank up (ranks are per-fighter, not per-profile; start 9th Kyu, Warrior rank after ~60–100 wins). Opponents get harder as the player climbs. Every so often a Special Match appears against powered-up boss fighters (Ascended Heihachi, True Devil Kazuya, Akuma in Brimstone & Fire, Devil Kazumi in Devil's Pit, Jin Kazama in Mishima Dojo) — they deal bigger damage and their Rage Art removes all of the player's health; beating one can give a Gold or Rainbow chest and a rank promotion. **There is no continuing** (a loss just ends that fight; the run continues).
Sources: Part A §3h — Tekken Wiki Treasure Battle; Windows Central T7 achievement guide.

**Current game:** implemented. `modes.js:1041–1095`. Endless waves, escalating difficulty (0.40 + 0.05 per wave, cap 0.95), each win opens a chest (coins always + one still-locked unlockable if any), coins to localStorage, prizes via `unlockables.js`, health fresh each wave. **Differences:** no rank ladder (no kyu/dan, no promotion matches); no Special Matches against powered-up bosses; chest count is 1 per win, not 1–3.

### 3i. Tekken Force (T3) / Devil Within (T5) — for reference (HeartMind uses this)

**Measured (Tekken):** Tekken Force (T3): side-scrolling beat-'em-up, 4 stages, waves of Tekken Force soldiers, a boss from the roster at the end of each stage (depends on the fighter picked, except stage 4 where the boss is Heihachi). Clearing all four stages can unlock Dr. Bosconovitch. Losing stores the high score and goes to game over — **no continue**. Items: roast chicken restores 50 health ("LIFE UP!"). Devil Within (T5): same idea, third-person camera, 5 stages, enemy groups, door/key puzzles, stage bosses, Devil Gene meter (transform at full meter — more power, costs health). See §5 for the full Devil Within measurement.
Sources: Part A §3i — T3 modes doc "Tekken Force"; repo Lane G research §4.

**Current game:** HeartMind (`game/js/heartmind.js`) is the Western Heart version — sequential inner battles vs "echoes" with HP carry-over + soul-ember restores, 5 inner stages, final boss the SHADOW SELF. See §5.

### 3j. Tekken Ball / Tekken Bowl — not in the current game

**Measured (Tekken):** Tekken Ball (T3): 1v1 beach volleyball — hit the ball back over the net; the ball is charged by attacks and damages whoever it hits. Ball types: Beginner/Beach Ball, Expert/Gum Ball, Grand Master/Iron Ball; ball damage 60%/80%/100%. Tekken Bowl (T7): full bowling minigame (Ultimate Tekken Bowl DLC).
Sources: Part A §3j — repo Lane G research §5; T3 modes doc "Tekken Ball's select".
**Current game:** not implemented. Documented in the repo research as a future minigame lane (needs ball physics). Recorded as absent, not a fix for this pass.

### 3k. What the current game has that Tekken does not (WH originals — recorded, not defects)

From `modes.js` MODE_LIST (lines 286–310): STORY (Trial + reincarnation), IMMORTAL QOMBAT / 不死クォンバット (endless waves, HP + 35% per win, +5% power per wave), SOUL SURGE GAUNTLET (8 fights, one per other soul), TRADER'S MIMIC (3-bout duel, Trader copies the player's moveset more each round it loses), FIGHT LAB / GUNGAKU (programmable dummy), TREASURE BATTLE (Tekken-based, see §3h). All are canon-grounded per the repo research. They are not measured against Tekken because they are not Tekken modes.

---

## 4. Round / match / stage rules — measured

| Rule | Tekken measured | Current game | Source |
|---|---|---|---|
| Round timer default | T3: 40 s (last game with 40 s default). T5 Time Attack: 60 s. T7 tournament: 60 s. T8 Arcade: NO visible timer during stages. | 60 s timer (AUDIT.md §5: "Best-of-3, 60 s timer") | Part A §4 |
| Rounds to win a match | T3 default 2 rounds; T5 Time Attack 2 rounds; T7 tournament first to 3 rounds; T7/T8/TTT2 final boss stage forced to 2 rounds even on 1-round settings | Best-of-3; `modes.js` passes `roundsToWin: 1` for survival/timeattack/team/treasure | Part A §4 |
| Rounds/time changeable in Arcade | Yes — Arcade's rounds and time limit can be modified, unlike Time Attack (fixed defaults) | No options step found in the Arcade flow — Arcade starts straight from select | Part A §4 |
| Continue | T3: "CONTINUE? 9" countdown, ~13 s; Start continues; same fight restarts, or back to select if CHARACTER CHANGE AT CONTINUE is on; timer out = GAME OVER → ranking | No continue at all. Loss = "GAME OVER" screen with RETRY LADDER (whole ladder from rung 1) or MAIN MENU | Part A §4; `modes.js:752–754` |
| Pause | T3: Start pauses mid-round; Start again does NOT unpause — only CANCEL does; pause menu has CANCEL / COMMAND (move list) / RESET (leave to main menu); music volume drops while paused | Pause button unclickable in fights (Playtest Break 7 — `styles.css:27` `.screen.hud` has `pointer-events: none`, `#wh-pause-btn` has no re-enable; Escape never wired to pause) | Part A §4; PIECE1-DIAGNOSIS.md §7 |
| Challenger join | T3: a non-playing player can join from the 8th frame of a fight with Start ("A NEW CHALLENGER ENTERS!!"); with L1+R1 held, quick select | Not implemented — no join path found in `modes.js` | Part A §4 |

### Stages — how Tekken picks them vs the current game

- **Tekken 3:** each ladder entry has its own stage index, picked when the ladder is built (`ArcadeBuildLadder` fills character + costume + stage per entry). Stages are tied to the ladder, not picked by the player in Arcade.
- **Tekken 7 Arcade:** fixed stages for the bosses (stage 4 Mishima Dojo, final Devil's Pit / Abandoned Temple); random stages for the first three.
- **Tekken 7 Versus:** stage is random for game 1; the loser picks after a loss.
- **Current game:** stage select screen exists (playtest: Shrine of the Blade preselected and confirms). In Versus, `_beginVersus` takes a stage from setup rules or random from a pool (`modes.js:626–629`). In Arcade, `startFight` is called with no stage — the stage the player picked on the stage screen is used for the whole ladder, as far as the code read shows. **Difference:** Tekken's Arcade changes stage per ladder rung (and fixes boss stages); the current Arcade plays the whole ladder on the one stage the player picked. Whether the stage actually changes per rung in the current build is **UNMEASURED** — no per-rung stage code was found in `_arcadeNext`, and the playtest only played one stage.

### Endings / results / records — measured

- **Tekken 1–3, 5, 7, TTT2:** beating the final boss plays the fighter's ending movie, then (usually) the credits. T6 is the exception: credits with no ending. T8 Arcade: no credits roll.
- **T3 result screens:** Time Attack shows all ten stage times + total + NEW RECORD; Survival shows per-fighter win counts + total + top-10 rank line; Team shows a fight-by-fight replay with winner lines. Then the ranking screen (3 pages: character time records, greatest survivors, character usage), with name entry (3,000-frame timer, 40-symbol alphabet; entering "GON" unlocks Gon).
- **Current game:** Arcade clear shows "ARCADE CLEARED" + WATCH ENDING button (per-fighter ending via `story-endings.js`). Records are localStorage only (`wh_records`: survival waves, timeattack best time, treasure waves). No per-stage time breakdown, no per-fighter win counts, no ranking pages, no name entry, no top-10. (AUDIT.md §12: no save system found; records exist but no save/progress system.)

---

## 5. Devil Within (Tekken 5) → HeartMind — measured base and mapping

### 5a. What Devil Within is (measured, public sources)

Source: Part B §2 — Tekken Wiki "Devil Within (Mode)"; Tekkenpedia "Devil Within" and "Tekken 5".

- A 3D action-adventure side game bundled with Tekken 5 (PS2, 2005), replacing the Tekken Force modes of Tekken 3/4. Unlike Tekken Force, the player cannot pick a character — it is Jin Kazama only — and it has a storyline.
- Story: after the tournament, Jin hears Jun Kazama may be alive and goes to a G Corporation lab (run by the Medicern subsidiary) to find Jun. Jin fights super-soldiers, robots, JACKs, a modified Gun Jack, and Heihachi clones in the lab; loses control of the Devil Gene as the descent goes deeper; finds the lab is built over ancient ruins (Ogre's temple); fights True Ogre, then an energy ball (the ruins' seal), then True Ogre again and Monstrous Ogre. Jin never finds Jun.
- **Stages (5), all indoors, multi-tiered hallways and connected passages, with platforming and door puzzles that get harder as the game goes on:**
  1. G Corp lab — boss: Modified Gun Jack.
  2. Medical wing, including a child's bedroom (sky-blue walls, clouds, yellow stars, big fluffy sheep on the floor) — boss: Heihachi clones. One clone first, then three at once.
  3. Ancient ruins (Aztec temple) — boss: True Ogre.
  4. Alien spaceship (grey/green, mystical) — boss: Soul Sphere, a ball of energy.
  5. Same spaceship theme, harder — boss: True Ogre then Monstrous Ogre, both fought on the same health bar. Monstrous Ogre is taller, more yellow than green, and adds whirlwinds, strong stomps, and powerful sweeps.
- **Enemies (minions):** JACKs, Jack-5, G Corp soldiers, Ogre's mutants. Per the repo's DW data doc, the mutants have names: Adam, Eve, Duke, Regal, Jill. Defeated enemies drop Force (fight money, spent in Customization Mode) or a healing pick-up.
- **Moves:** Square punch, X kick, Triangle block, Circle jump; Square+X throw; Square, Square, X combo; X+Circle combo kick; Square+Circle uppercut; L1+Square 5-hit combo into rising punch; L1+X jump kicks; Square+Circle, X pop-up into kick; R1+Circle forward roll; R1+down, Circle back flip. Double jump (press jump again mid-air) for extra distance. Forward roll and back somersault also listed. Jin fights in Mishima Style Fighting Karate, with some moves from Traditional (Kyokushin) Karate. Limited button system — Block, Jump, Punch, Kick — "but the character's real special moves still work" (repo `docs/modes/TEKKEN-MODES-RESEARCH.md` §4; `docs/modes/HEART-AND-MIND-INSIDE.md`).
- **Devil Gene meter / Devil Jin:** when the Devil Gauge is full, L1+Triangle transforms Jin into Devil Jin (press again to change back). Devil Jin is much stronger, has advanced Mishima techniques (Hell Scraper, Roundhouse to Triple Spin Kicks) and laser attacks that can hit several enemies at once — but the form drains Jin's health, so it must be used sparingly. Enemies killed in devil form disintegrate into black feathers. The laser is also needed for progress: on stage 4, a door made of crumbled rocks with a red Devil Gene symbol sits across a gap that cannot be crossed — Devil Jin must shoot the rocks with the laser until they break, and a floating bridge forms (medium difficulty or higher). After beating Devil Within on medium difficulty and collecting all Evil Symbols, Devil Jin can be played through the whole mode by holding L2 + SELECT + R3 while selecting a stage or starting a new game; the Devil bar becomes the laser bar.
- **Items:** blue gems and red gems (healing pick-ups); 40 red Devil Symbols hidden through the five stages (8 per stage), which unlock customization items for Tekken 5 characters. Symbols can sit above breakable objects.
- **Ranking:** after each stage, the player is ranked on time to finish, total damage, number of retries, Force collected, and more. The rank (S highest, then A/B/C) multiplies the Force collected. Exact rank thresholds: **UNMEASURED** — neither public page gives the numbers.
- **Unlocks for finishing Devil Within:** 1,000,000 G, the Cathedral stage, Devil Jin as a playable character, Devil Within stage select, Final Stage, Final Stage 2. After finishing once, stage select opens with difficulty choice, and a second playthrough lets the player collect the 500,000 G customization items via the red symbols. Devil Jin can also be unlocked without finishing Devil Within by finishing Time Attack with Jin or doing 200 arcade battles.
- **Manual (Tekken 5 USA, archive.org full text):** "As Jin Kazama, defeat a swarm of opponents and uncover the truth of his past and the devil gene." How-to-play ("fight your way toward the bottom of the lab… boss at the end… Result screen, then Save screen"), HUD meters named (Health, Devil Gauge, Force), Devil Jin confirmed as L1+Triangle at full gauge with "health declines with time, so use this power wisely," pause menu (Cancel, Camera Type, Vibration, Restart, Return to Devil Within Title), Retry on the Game Over screen, and the save warning (entering Devil Within enters save mode; 57 KB memory card). Link: https://archive.org/stream/ps2_Tekken_5_USA/Tekken_5_USA_djvu.txt
- **Other measured details:** stage 1 and boss-fight music is a remix of Jin's Tekken 3 theme; stage 3's theme was originally meant for Tekken 4's Jungle stage; the clone Heihachis have serial numbers on their hakama (first clone "0025") and electronic metal cuffs, and no chest scar.

### 5b. What decoded Devil Within data actually exists — the honest answer (updated 2026-11-08, real bytes)

Source: Part B §1 + Part E Devil Within box + the 2026-11-08 decode
(`teardown/tekken5/dw-motion-index.json`, `dw_measurements.json`,
`dw-motion-curves.json`, `DW-DECODE-LOG.md`, `ROMD-FORMAT.md`,
`tools/romd_extract_full.py`, `tools/gym_keyframes.py`,
branch `dw-decode`, on top of `3334ebf`). **Contents decoded at
file level from real disc bytes. Per-joint motion curves decoded
2026-11-08 (commit `1beffd18`). Game numbers not yet decoded.**

- What got decoded 2026-11-08 (archive pull, Jay authorized
  2026-11-07 ~20:15; Internet Archive item `slus-210.59.-tekken-5`,
  range-fetched per BIN — full-ISO md5/sha1 NOT verifiable, see
  `DW-DECODE-LOG.md`): **236/242 Devil Within files extracted**
  from `TK5DATA2.BIN` (romD). The romD file-table mapping is
  SOLVED: 99 `BDPK` containers, each a BD directory (128-byte
  records: type, X, Y=file size, filename) — entry count == A and
  Y-sum == data region − 12 on every container. 6 DW files have no
  data in TK5DATA2 (list references only: `ozhe_1ckj66a`,
  `katgym_Bbr_bbblow`, `katgym_Gan_mekin`, `testchr1/2/3`).
- Gym motion format — header decoded (`GYM1` magic @0x40):
  bone count 35 (fighter motions) / 78/111/96 (`init_obj`) / 12
  (`djin`); frame count per clip; field12 = frames × bones × 12
  (420 values/frame at 35 bones). **214 motion clips, 16,503
  frames, 275.1 s at 60 fps** (Surge donor kit — source: Devil Jin's kit — 52 clips/58.1 s, Gun Jack
  39/53.1 s, True Ogre 29/54.1 s, Monstrous Ogre 36/69.4 s,
  ikt5 24/27.4 s — the earlier 17,553 / ~292 s was a mis-add).
  14 clips are a SPARSE subtype (field12 much smaller —
  CORRECTION 2026-11-08: they decode identically to standard
  clips, full frame blocks; field12's exact meaning for them is
  unresolved, no separate handling needed; the long/special
  motions: deaths, entrances, projectile attacks, throws).
  **The keyframe stream is CRACKED 2026-11-08**
  (`tools/gym_keyframes.py` → `dw-motion-curves.json`,
  9,002 keyframes): full frame blocks, step flag (header
  u16[7]: 8192 = every 2nd frame, 0 = every frame), rotations
  i16 × 180/32768 deg with R = Ry(t0)·Rx(t1)·Rz(t2), positions
  mm Y-up. Validated on all 454 gym files (0 mismatches) and
  by rotation smoothness (stance max 0.95° per keyframe step).
  Full proof: `DW-DECODE-LOG.md` §18.
- Stage files — CORRECTION: `moj_stg00/01/02/04` are stage MAP
  OBJECTS (`.moj` geometry: NUDP models + TIM2 textures + MIF
  bones), NOT stage text. Measured: stg00 1,916,672 B (29 NUDP /
  29 TIM2 / 56 MIF); stg01 872,320 B (18/18/18); stg02 1,392,384 B
  (20/20/22); stg04 200,192 B (3/3/3). `moj_stg03` does not exist.
  NUDP/MIF contents (positions, collision) NOT yet parsed.
- Sounds: 17/18 `snd_*` files are a `P3Dp` container (header
  measured; audio payload not decoded). `snd_c02lei.dat` is a
  plain-text sound-position file.
- `TK5DATA3.BIN` PKG parsed (10 files); the NLZ1 Code blob
  decompressed (2,719,159 B); the PS2 LUT in it is VALID
  (TABLESTART 0x0027B5B0, 1571 entries, 99.9% of TK5DATA1
  covered). Code-blob string scan: `item_force` (menu/config
  name only), `handycap_gauge` (handicap UI), `Devil Jin`,
  `RankingMode` — **zero hits for `symbol`, `laser`, `drain`,
  `heal`**. The meter/gem/Force/rank/symbol numbers are NOT in
  the Code blob as readable data.
- What does NOT exist (unchanged): stage geometry parse, boss AI,
  enemy tables, wave tables, Devil Gene meter numbers, gem/Force
  values, ranking thresholds, symbol locations, moveset data.
  (Animation curves are DONE now — see above.) `TK5DATA0.BIN`
  (2.07 GB) + `TK5DATA1.BIN` (1.30 GB) are NOT held whole —
  blocked on the VM disk quota (measured ~1.5 GB ceiling).
  **Both were stream-scanned in discardable 10 MB chunks**
  (TK5DATA1: 232 hits, TK5DATA0: 309 hits — all false-positive
  "gem" strings or chance 4-letter matches in binary data):
  neither contains readable DW strings. The numbers are binary
  values there or MIPS immediates. `TK5DATA3.BIN` was deleted
  after its Code blob was saved (SHA-256 recorded; re-fetchable
  from the same archive item).
- The phrase **"god within" appears nowhere** in the repo copy searched. The mode is always called "Devil Within".
- Two cited-but-missing files: `~/workspace/devil-within-teardown.md` (design doc, 2026-10-22, cited by two repo docs — not on this machine) and `~/workspace/tekken5-extract/` (Oct 23 extraction workspace — not on this machine). A full-workspace text sweep finished with no decoded data anywhere — only mentions (memory copies, other repos' audit maps, sibling teardown parts).
- What the decoded files would change if the RE bench ever lands them (repo's own order, `DEVIL-WITHIN-DATA.md` §4): (1) the Surge donor kit's DW brawler moveset, (2) Devil Gene meter + Soul Surge Bloom transform data (source: Devil Jin transformation), (3) 5 stage layouts, (4) boss patterns, (5) ranking thresholds, (6) UI layouts. Until then they wire in as a spec, not as data — the 2026-11-08 file-level decode wires in as measured clip/stage inventories, not as playable motion.

### 5c. HeartMind today — what it is in the game

Source: Part B §3 — `game/js/brawler.js` (1,469 lines), `game/js/heartmind.js` (569 lines), `game/js/heartmind-campaign.js` (225 lines), `game/js/fighter.js` (Soul Surge form), `game/js/episodes.js`, `game/js/story-endings.js`, `game/story/heartmind-trial.ink` / `.yarn` / `.json`.

HeartMind's in-game name is "The Heart and Mind Inside" (owner-locked name, 2026-10-19). It is the Devil Within-style mode of Western Heart, reachable from the menu ("THE HEART AND MIND INSIDE" card, "a descent · beat-em-up"). No end-to-end live playthrough of HeartMind is on record — what follows is what the code says, not a played run.

**Flow:** pick any fighter — not forced Jin. Any Western Heart fighter plays the descent with their own moveset. Entry story beats play, then the brawler takes over. Five inner stages, each with waves then a boss, in order: The Threshold → The Gallery of Masks → The Drowning Room → The Furnace → The Still Point. On stage clear, the game records the highest stage reached per fighter and pauses 1.2 seconds before the next descent. On victory, the resolution beats play and the result screen says "PURIFIED". On death, a "THE DARK KEEPS WHAT IT CATCHES" beat plays and the game returns to the menu. Between stages, roads connect the rooms, with a one-line walk description each — never a teleport.

**Stages, enemies, bosses (as coded):**

| # | Stage (HeartMind name → game arena) | Waves (from `WAVE_TABLES` in `brawler.js`) | Boss |
|---|---|---|---|
| 1 | THE THRESHOLD → tong-nou | 3 waves: echoes ×2, ×3, then echoes ×2 + gunner ×1, brute ×1 + echoes ×2 | WARDEN (Modified Gun Jack analog: bruiser + heavy blockable projectiles, 380 HP, scale 1.35) |
| 2 | THE GALLERY OF MASKS → phantom-marketplace | 3 waves: echoes ×3, echoes ×2 + gunner ×1, then brute ×1 + echoes ×2, gunner ×2 + echoes ×2 | THE MASKS (Heihachi-clone analog: ONE mask first at 135 HP, then THREE at once) |
| 3 | THE DROWNING ROOM → palace-of-dreaming | 3 waves: echoes ×3, brute ×1 + gunner ×1, then echoes ×4, brute ×2 | THE DROWNED OGRE (True Ogre analog: teleports near the player, homing volley, fire-blast area attack, 520 HP, scale 1.42) |
| 4 | THE FURNACE → plains-of-chi-u | 3 waves: gunner ×2 + echoes ×2, brute ×1 + echoes ×3, then echoes ×4, brute ×2 + gunner ×1 | THE SOUL SPHERE (energy orb, 420 HP: contact damage, spawns monsters every ~6 s) |
| 5 | THE STILL POINT → octagonal-shrine | 1 wave (echoes ×3, brute ×1 + gunner ×1), then boss only | SHADOW SELF (the player's own fighter, darkened, power ×1.28, defense ×1.15, speed ×1.10, 460 HP) → on defeat, THE UNMASKED, a second form (320 HP, scale 1.28, same descent, no fresh health bar for the player) |

Enemy types: **echo** (a roster fighter as an inner demon — dark tint, hollow name "ECHO OF …", real moveset), **brute** (slow, hunts throws), **gunner** (keeps distance, shoots blockable projectiles), plus the five bosses. At most 5 enemies alive at once. Enemies circle the player instead of lining up, and are clamped inside the fight zone so a kiting gunner cannot stall a wave forever.

**Progression and systems (as coded):** difficulty ramp 0.45 → 0.55 → 0.65 → 0.75 → 0.90; between-wave health restore 0.30 → 0.30 → 0.32 → 0.32 → 0.35 ("soul-ember restore"). Healing pick-ups: soul embers — heal 22 HP, 35% drop chance from a defeated enemy (Devil Within's healing gems, renamed). Transform: the Nine-Soul Meter is the Devil Gauge analog. Full meter + transform input = SOUL SURGE FORM: timed powered state, 25 seconds, no model swap, power ×1.45, speed ×1.15 (capped 3.8), defense ×1.20 (`fighter.js`, `startSurgeForm`). If the fighter has a model-swap transform, that runs instead. Ranking: per-stage S/A/B/C rank from time + damage taken (`brawler.js`, `_rank`): S if under 150 s and under 50 damage; A if under 240 s and under 120 damage; B if under 360 s; else C. These thresholds are Western Heart's own numbers, not Devil Within's — Devil Within's real thresholds are **UNMEASURED**. Records: highest stage reached per fighter, total clears. Stories: deep written stories for Demonio, Doc Frank, Mariposa, Thor, and the nine souls; every other fighter gets a generic frame. Campaign layer (`heartmind-campaign.js`): roads between stages, party switching between fights only, a stage journal, ragdoll contexts, and a story-engine adapter (Yarn/Ink loaders exist; the adapter returns null when the engines are absent and the built-in beats are used). Story scripts (`game/story/`): `heartmind-trial.ink` (1,262 bytes), `.yarn` (1,338 bytes), `.json` (2,211 bytes) — the same short trial: a crossroads, a Trader, a Trial gate, five rooms named, the shadow self waiting at the Still Point.

**Working code (read, not played):** the full brawler engine (`brawler.js`, 1,469 lines), the HeartMind controller and stories, the campaign layer, menu wiring, and the transform/surge form. Tests exist: `game/tests/brawler-sim.test.mjs`, `brawler-surge.test.mjs`, `heartmind-campaign.test.mjs`.
**Doc-only / not yet real:** the teardown seam — `HM_TEARDOWN` in `heartmind.js` is an empty placeholder (`ready: false`, `enemyAi: null`, `waveTables: null`, `doorSystems: null`), waiting for the teardown lane to deliver Devil Within's exact mechanics, at which point the wave/boss builders consume them 1:1. 2026-11-08: the teardown lane delivered the index-level inventory + the full decode (branch `dw-decode` — 242 files named and glossed, 236 extracted, per-joint curves decoded in `dw-motion-curves.json`, moveset bank `game/data/moveset-library/banks/dw.json` + `game/data/heartmind-dw-teardown.json` landed, commits `606d2c8` + `1beffd18`); the seam still waits on enemy AI, wave tables, and door systems (all still null — those numbers live in TK5DATA0/1 as binary values or MIPS immediates), and no game code was changed in that pass. The wave tables, enemy AI patterns, boss behaviours, and rank thresholds in the brawler today are Western Heart's own inventions modeled on public Devil Within descriptions — not measured from the disc. **Whether the brawler actually runs on the live build is UNMEASURED** — it needs a headed playthrough, the same as Piece 1.

### 5d. Mapping — Devil Within onto HeartMind (draft only, no code)

"Carries over" = already in the game, from public research. "Western Heart's own" = invented for this game.

| Devil Within (measured) | HeartMind today | Status |
|---|---|---|
| 5 stages, boss at the end of each | 5 inner stages, boss at the end of each | Carries over — structure matches 1:1 |
| Stage order: lab → medical wing/child's bedroom → ruins → spaceship → deeper spaceship | Threshold → Gallery of Masks → Drowning Room → Furnace → Still Point (canon lands, not the lab) | Structure carries over; places are Western Heart's own |
| Boss 1: Modified Gun Jack (powerful projectiles) | WARDEN (bruiser + heavy blockable projectiles) | Carries over as an analog |
| Boss 2: Heihachi clones — 1 first, then 3 at once | THE MASKS — 1 first, then 3 at once | Carries over 1:1, including the 1-then-3 trick |
| Boss 3: True Ogre (fire breath, flying, teleporting) | THE DROWNED OGRE (teleport, homing volley, fire blast) | Carries over as an analog |
| Boss 4: Soul Sphere (energy ball, contact damage, spawns monsters) | THE SOUL SPHERE (420 HP orb, contact damage, spawns monsters) | Carries over 1:1 in behaviour |
| Boss 5: True Ogre → Monstrous Ogre, same health bar, second form taller/stronger with whirlwinds, stomps, sweeps | SHADOW SELF → THE UNMASKED, second form, same descent | Carries over as an analog; the second form's moves are now decoded as per-joint curves (`ozb3`: 36 clips / 69.4 s — `tatumaki` whirlwind, `fumi` stomp, `burn`, guard variants — `dw-motion-curves.json`, commit `1beffd18`) — the move data is measured at the joint level now; inputs/damage/hitboxes are still **UNMEASURED**. The Unmasked is a stat-buffed shadow, not a measured Monstrous Ogre kit |
| Jin only, forced character | Any fighter, own moveset | Western Heart's own — deliberate change, owner-ordered |
| Enemies: JACKs, Jack-5, G Corp soldiers, Ogre's mutants (Adam/Eve/Duke/Regal/Jill) | Echoes (roster fighters as inner demons), brutes, gunners | Western Heart's own enemy set; the DW mutant names are known from the repo doc and the monster archetypes are now inventoried (`mon_power/speed/standard/tricky` init objects — 2026-11-08 decode); behaviour is still **UNMEASURED** (no bytes) |
| Free-roam 3D, multi-enemy waves, camera behind the fighter | Free-roam 3D, multi-enemy waves (max 5 alive), third-person camera | Carries over |
| Platforming + door puzzles, double jump, forward roll, back flip | Not present — no platforming, no doors, no double jump in the brawler | **Missing.** Devil Within's platforming/door systems are the `doorSystems: null` slot in `HM_TEARDOWN`. Whether HeartMind should add them is a design decision, not a measurement. |
| Devil Gene meter fills, L1+Triangle transforms into Devil Jin; form drains health; lasers hit many enemies at once | Nine-Soul Meter fills, transform input = Soul Surge Form (25 s, power ×1.45, speed ×1.15, defense ×1.20, no model swap, no health drain) | Analog carries over; the Surge donor kit (source: Devil Jin's kit) is now decoded as per-joint curves (`ikdv`: 52 clips / 58.1 s — 5 beams incl. `all_beam`, 5 punches, 4 kicks, throws, turns, breakfalls — `dw-motion-curves.json`, commit `1beffd18`), but fill rates, laser damage, and health-drain rate are still **UNMEASURED**. HeartMind's surge has no health drain and no laser — Western Heart's own choice. |
| Healing gems (blue/red) dropped by enemies | Soul embers, heal 22, 35% drop chance | Carries over as an analog; the real gem heal values and drop rates are **UNMEASURED** |
| Force (fight money) dropped by enemies, spent in Customization | No Force in HeartMind | **Missing.** Devil Within's Force economy is listed as "not yet extracted". |
| Per-stage rank (S/A/B/C) from time, damage, retries, Force | Per-stage rank S/A/B/C from time + damage only (S <150 s & <50 dmg; A <240 s & <120 dmg; B <360 s; else C) | Rank letters carry over; the real thresholds and the retries/Force factors are **UNMEASURED** |
| 40 red Devil Symbols (8 per stage) unlocking customization items | No symbols, no collectibles in HeartMind | **Missing.** The symbol hunt is a whole Devil Within subsystem with no HeartMind equivalent yet. |
| Story beats after each boss (Jin's search for Jun) | Per-fighter story beats per stage + boss lines + resolution, plus the Shrine terminal at the Still Point | Structure carries over; the story is Western Heart's own (purification, shadow self) |
| Finishing unlocks: 1,000,000 G, Cathedral, Devil Jin, stage select, Final Stage 1/2 | Finishing records a clear per fighter; no unlocks gated on it yet | **Missing as a system.** What a HeartMind clear should unlock is a design decision. |
| Stage select + difficulty choice after first completion | No stage select, no difficulty choice in HeartMind | **Missing.** |
| Stage text/messages (`moj_stg00/01/02/04`) | No stage text in HeartMind | Inventoried 2026-11-08 (names only, no contents); `moj_stg03` absent; stage geometry still missing — it is not in romD at all |
| Devil Jin playable through the whole mode via a button code (after medium + all symbols) | No equivalent | **Missing / not applicable** — any fighter can already play, so there is no locked devil form to unlock. |

---

## 6. Urban Reign — feel, systems, and Redux

### 6a. What Urban Reign material is already in the repo

Source: Part C §1. `teardown/urban-reign/` is the biggest single-game teardown in the repo: coverage matrix rates it **~95%** complete, the highest rating in the matrix. 18 doc files + 3 listing files + 18 subfolders.

- **Models:** `teardown/urban-reign/models/` — 72 subfolders `char001`–`char072`, each with `charNNN.glb` (skinned phase-1 model), normals/pos/UV OBJs, `vmanifest.json`; plus `ROSTER.json`. `teardown/urban-reign/textured-models/` — 72 `charNNN_textured.glb` files (~374–484 KB each) with 733 embedded images total, verified geometry-identical to the phase-1 GLBs (`MANIFEST.json`). This is the canonical fighter model set.
- **Animations:** `teardown/urban-reign/animations/motion-packs/` — 46 files: `main.ppk`, `main_in.ppk`, `select.ppk`, `weapon.ppk`, 31 `pmotNNN.ppk` (per-character motion packs), 10 `tmotNNN.ppk` (team/tag packs). `teardown/urban-reign/motion/` — `general_normal.gyu`, `general_30frame.gyu`, `general_weapon.gyu` (three shared animation pools) + bank index tables. `teardown/urban-reign/motion-names/` — 36 files: move-name bridge evidence, `BANK-INVENTION-PHASE6.json`, censuses. Bank census: **285 banks / 3,357 motions** searchable (`BANK-COMPLETION.md`).
- **Moves:** 484 move names proven at the Phase-5 gate (max deviation ≤ 0.10 mm, unique), annotated as `motdatName` in the game movesets.
- **Stages:** `teardown/urban-reign/ppks/stages/` — 7 files (`stage003/004/020/028/029/030/031.ppk`, 34 MB total). **Stage geometry inside them is NOT decoded.**
- **Missions:** `teardown/urban-reign/missions/definitions/` — 256 files `mission000.bin`–`mission255.bin` (8,300 B each); `missions/ppks/` — 100 files `mission001.ppk`–`mission100.ppk` (~6–10 MB each, 821 MB total). Field layout is unknown; decoding is open work, not a wire-in.
- **Audio:** `teardown/urban-reign/audio/` — at least 1,000 sound-bank items (API listing cap); `sound/ok_adx/adx/` — at least 1,000 ADX music files. Exact counts **UNMEASURED** (listing cap).
- **UI:** `teardown/urban-reign/ui/` — character-select (`face.vgs`, `select.ppk`), menus (18 files incl. `dcm_pause.dcm`), screens (54 VGS screens), title screens. VGS tile payload is still undecodable (proprietary Namco encoding) — layout/measure references only. `VGS-FORMAT.md` documents the header.
- **Tools (own code):** `teardown/urban-reign/tools/` — 25 Python tools, including `ur_decode.py` (main decoder), `ur_gyu.py` (motion-bank decoder), `ur_tex_extract.py`, `ur_build_textured.py`, `ur_embed.py` / `ur_batch_embed.py`, `ur_name_bridge.py`.
- **The ISO itself is not a folder.** `TEARDOWN.md` records `Urban Reign (USA).iso`, 4.14 GB, from Internet Archive item `urban-reign-usa_202608`, stored as GitHub Release `urban-reign-iso-v1`, split into 8×500 MB parts. The local ISO was deleted after verification. This is extracted commercial game material in a public repo release — the same flag the audit already raised.

**Already wired into the playable game (`game/`):** `game/assets/models/street-reign/` — 72 files `char001.glb`–`char072.glb` (the **untextured** phase-1 copies; 31 carry embedded native animation, clips `ur_m*` + `Idle`). Roster ids `ur-char001`–`ur-char072`, shared moveset key `street-reign`. `game/assets/movesets/` — 33 Urban Reign files of 175 total: `street-reign.json` (proxy base set, `proxy: true`), 31 `ur-charNNN.json` files (2,805–10,928 B), `ur-native-index.json`. `game/assets/anim/` — 3 Urban Reign folders: `ur-general-normal/`, `ur-general-30frame/`, `ur-general-weapon/` (converted general-pool banks, 829 motions; per-fighter assignment still owed). **Named follow-up, NOT done:** the textured fighter swap — `teardown/urban-reign/textured-models/charNNN_textured.glb` → `game/assets/models/street-reign/charNNN.glb` (re-run `ur_embed.py` / `ur_batch_embed.py` with the textured GLBs as base for the 31 pmot fighters; the 31 animated game GLBs carry embedded clips the textured GLBs do not, so it is not a plain file swap). `moveset-library/` has NO Urban Reign moves (Soulcalibur II / WMXIX only) — Urban Reign moves live in `game/assets/movesets/ur-charNNN.json`, not in the library.

**Fighter identities: OWNER-pending.** The repo's per-fighter identity is only the id itself (`char001`–`char072`). Only Brad Hawk (the protagonist) and the Tekken guests Paul Phoenix and Marshall Law are named, without saying which PPK numbers they are. No fighter has been renamed to a Western Heart canon name. The one documented mapping is Glen Kluger → Cain Elias's moveset source, and the specific PPK for Glen Kluger is part of the flagged identity pass. No identity was guessed here.

### 6b. Urban Reign's actual feel and systems (measured, public sources)

Source: Part C §2. Game: **Urban Reign**, Namco, PlayStation 2, 2005 (USA September 13, 2005; Europe 2006). IDs: SLUS-21209 (USA), SLPS-25557 (Japan), SCES-53688 (Europe). Rated Teen. Made by the Tekken/Soulcalibur team. Runs at 60 fps.

- **Shape:** a 3D arena brawler, not a 1v1 fighter. Free-roam arenas, several fighters on screen at once, human and AI together. 100-mission Story Mode: Brad Hawk, a brawler-for-hire, hired by Shun Ying Lee to find a kidnapped gang member, fighting through the street gangs of Green Harbor. 60+ playable fighters, each with a distinct style (boxing, wrestling, karate, brawling, capoeira, kung fu, Muay Thai, Tae Kwon Do). Tekken guests Paul Phoenix and Marshall Law are unlockable, with Tekken 5-era models and trademark attacks. Modes: Story (100 missions), Free Mode, Challenge Mode (wave survival, solo or co-op), Versus (KO or points rules), Practice, Tutorial, Fighter Files, and 4-player multiplayer with a PS2 multitap: head-to-head, team brawls, Weapon Battle (hold the weapon to win) and Destruction/Object Battle (protect your object, smash theirs).
- **Controls (USA manual, archive.org full text):** Circle = Strike, Triangle = Grapple, X = Run/Dash, Square = Dodge/Deflect, R1 = lock target, L1 = pick up/discard weapon, L2 = taunt, R2 = partner commands, right stick = camera, R3 = reset camera.
- **Strike:** Circle. Neutral = a multi-hit combo string; with a direction (Up / Left-Right / Down) the strike targets the Head / Upper Body / Lower Body region.
- **Grapple:** Triangle. Directional grapples target a body region the same way; neutral grapple grabs and holds the opponent, front or back. Low and high grapples, air grapples, counters and reversals each have their own animation per character. Tekken Wiki: "Especially rich is the grappling system. There are low and high grapples, air grapples, counters and encounters each with its own animations for each character. The grapple system is highly reminiscent of Tobal 2."
- **Combo shape:** "most combos start with three presses of the attack button, the third of which will juggle an opponent. Then the player has choices of an air grapple, special move, simply continuing the combo or even running away to pick up a weapon or reposition."
- **Dodge instead of block.** There is no block button. Square, timed to the moment of the attack, dodges it; Up/Down + Square reverses it. Manual p. 32: "Pressing the Square button at just the right time while under enemy attack will allow you to dodge their Strike Attacks… if you are attacked by several enemies at once, you will be able to dodge all of them."
- **Deflect / Grapple Break:** direction + Square deflects and throws the opponent off balance (and reduces the enemy SPA gauge); Square timed right breaks a grapple, aiming at the body region grabbed.
- **Dash / Run-Up:** X to run; running into a wall, enemy, or partner lets the character run up it, then Circle = Diving Strike, Triangle = Diving Grapple.
- **Target lock:** R1 locks a target; right stick switches target while R1 is held.
- **Double Attack:** Triangle when directly facing, or surrounded by, two enemies hits both at once.
- **Quick Recovery:** Square before landing after being launched gets the character up at once, in a chosen direction; it also avoids down strikes and down grapples.
- **Special Arts (SPA) — the meter:** Circle + Triangle together. Neutral SPA is a knockback in all directions (usable while standing or lying face-up, cheapest); Up + SPA is a big slow charged attack; Left/Right + SPA is a quicker multi-hit combo; Down + SPA is a status-effect buff, not an attack. Special Arts cannot be countered, reversed, or dodged except by another Special Art, and they can be buffered. Status effects (Down + SPA): Power Up (red, +50% attack), Concentration (blue, auto-deflects / auto grapple-breaks), Super Armor (yellow, less damage, no stagger), Arcanum (green, unlocks special moves). The gauge fills when the character attacks, is attacked, or dodges/deflects. It can also be spent to recover from a stunned state. Brad starts with few moves and unlocks more Special Arts over the story, including wrestling moves (running powerbomb, stunner, leg whip, mid-air powerbomb) and the ability to grapple in mid-air and to change a grapple mid-animation with another input.
- **Weapons and destructible environments:** 30+ weapons (bats, pipes, bottles, shovels, 2x4s, knives, broken bottles). No weapon durability — a weapon lasts until dropped. Pick up / discard with L1; a weapon thrown into the air by a collision can be caught. Weapon attacks use Circle/Triangle while holding one, with direction picking the body region; Square + X throws the weapon (at the locked target, or the nearest enemy). The environment is a weapon: walls, cars, crates, furniture — smash launched enemies into walls or cars for extra damage, run up walls for Diving Strikes. Furniture breaks, shelves shed boxes, cars and pinball machines shatter.
- **Body regions matter:** Head, Upper Body, Lower Body each have their own health bar on screen; a region turns yellow when injured, red when destroyed. Destroying the lower body stuns easily; destroying the upper body makes the enemy drop a weapon.
- **Partner / tag mechanics — the heart of it:** AI partner, earned by beating them first. Partner commands (R2): R2 alone = Call for Double-Team; R2 + X = Call for Help; R2 + Circle = Split Up; R2 + Square = Pass Weapons/Items back and forth; R2 + Triangle = Switch Fighters (take control of the partner). Double-Team Attacks: press R2 near the partner, or attack when the player and the partner surround an enemy — the attack differs by which character the partner is. Signature move: launch an enemy into the air and the partner catches and slams the enemy onto the concrete. Grapple assists: approach an enemy the partner is grappling and press Circle for an extra attack on the held enemy. Switching is seamless, and the mission still hinges on Brad Hawk: the player can switch to control the partner at any time, but the mission fails if Brad Hawk's health reaches zero, even while the player controls the partner. Mission failure: fail if the objectives are not met or Brad Hawk's health hits zero; retry from a menu (RETRY / MISSION INFO / QUIT). No co-op Story at first: two players cannot play the single-player missions together until unlocked, and then only with a code, and the camera follows Player 1 only.

**Directly usable for HeartMind (the feel layer):**
- The three-press strike string where the third hit juggles, then a free choice (air grapple / special / reposition / grab a weapon). A simple, readable combo shape that fits a phone.
- Direction = body region (Up = head, Left/Right = upper body, Down = lower body) on both strikes and grapples. One idea, reused everywhere, instead of a long move list.
- Dodge-timing instead of a block button, with deflect and grapple-break on the same timing idea. The sharpest difference from Tekken-style blocking and the most portable feel.
- The SPA meter shape: builds on attacking, being hit, and dodging; two-button trigger; neutral = get-off-me knockback, Up = big slow hit, Left/Right = multi-hit, Down = buff. Western Heart already has a Nine-Soul Meter and Soul Surge; the SPA shape is the proven reference for how a meter like that should feel.
- Double-Team Attacks and partner commands as the template for any tag/partner play: launch-and-catch slam, surround-an-enemy trigger, grapple assist, switch control, split up.
- Body-region damage (head/upper/lower each injured, then destroyed) as a readable damage idea.
- Wall run-ups and diving strikes/grapples as the arena-movement idea.
- 60 fps as the bar: the original ran its multi-fighter brawls at 60 fps. Western Heart's Piece-1 playtest ran at ~1 timer tick per 30 s on HIGH — the gap to the reference is the point.

**Urban Reign-specific (do not lift as-is):** the 100-mission Green Harbor story, Brad Hawk, Shun Ying Lee, the gang plot — that is Namco's story, not a system. The exact roster, styles, and names (Brad Hawk, Glen Kluger, Paul Phoenix, Marshall Law, and the rest) — use only the documented canon link (Glen Kluger → Cain Elias's moveset source) and the flagged identity pass. Weapon Battle / Destruction Battle as named modes, and the multitap 4-player setup — the rules can inspire a mode, the names and the PS2 setup cannot be copied. The VGS/DCM UI art and layout files — layout reference only, never copied art.

### 6c. Urban Reign Redux — found, read, NOT downloaded

Source: Part C §3. **Urban Reign Redux** is a community mod project for Urban Reign by **Jasonafex**. Its own words: "More fighters, revised movesets, new voices, music and menus for Urban Reign." It is **not** an official release and is "not affiliated with or endorsed by the original game's publisher."

- **Home:** https://jasonafex.github.io/urban-reign-redux/
- **Code and releases:** https://github.com/Jasonafex/urban-reign-redux
- **Version 0.5, released October 28, 2026.** More fighters: the original roster plus Tekken guests (Asuka, Bryan, Jin, Kazuya, King, Nina, Paul, Yoshimitsu, Hwoarang, Heihachi, Devil Jin, Reina, Kunimitsu, Bob, Christie, Armor Queen) and crossovers from other games (Cammy, Leon, Carl Johnson, Kiryu, Jeff Hardy, Snake, Renamon, Vergence, Ricardo). Revised movesets and sound: updated Fighter Files stats, styles, and bios; grounded idles (feet on the floor — Reina, Bob, Devil Jin, Ricardo, Kunimitsu, Renamon, Yoshimitsu, Jeff and others no longer float or sink); skeleton repairs; Tekken 8 stances and idles; long strings that connect (mid-string knockdowns became heavy staggers); Yoshimitsu's own voice instead of Law's, and the Player 2 selection freeze fixed; Jeff's Twist of Fate, idle, taunt, and side SPA fixes; Snake's up SPA now does damage. Presentation: cleaner hair, glasses, and clothing; reduced rainbow sheen; spring-physics repairs; two HD texture packs; smaller battle HUD, hidden player indicators, multiplayer camera controls (L3 follows the player on that controller, R3 restores the shared camera); expanded, paged stage selection with story-mode locations available in multiplayer; Challenge mode retexture; a mouth-animation pilot for Leon, Cammy, and Violet. Known issues in 0.5 (stated by the author): Kunimitsu's and Devil Jin's rigs still have weight-painting rough spots; Armor Queen has armour colour bleeding onto skin at the waist and hips; Bob has no Fighter Files voice yet; "The Devil Within, stage 1: the first door doesn't block you while enemies are still alive"; Cammy's throws can slide at the start; Reina can show a thin streak on the cheek. Earlier versions: 0.4 (October 3, 2026, 1.75 GB package), 0.2 Alpha (September 30, 2026 refresh).
- **What it requires:** a player's own Urban Reign (USA) ISO — the USA build, SLUS-21209. The tested 0.5 disc has game CRC **74E78599**. European and Japanese editions are refused by the builder. PCSX2 (tested with 2.7.403) with ExtraMemory support enabled, and the player's own PS2 BIOS. Neither PCSX2 nor a BIOS is included. Windows 64-bit for the Mod Manager / Editor (`.exe` launchers). A fresh boot, not an old emulator save state. Memory-card saves are fine.
- **How it is distributed — two downloads, and they are not the same thing:**
  1. **All-in-one package, 2.67 GB, Google Drive, no sign-in required** — "the ready-made 0.5 disc, HD textures in PCSX2's folder layout, the Extra Memory game setting, START HERE.txt, patch notes and checksums." The ready-made disc is a complete modded copy of the commercial game. **Downloading this means downloading the commercial game itself. Do NOT get it this way.** (Disc SHA-256 `cc2312c1909cec438b8971133445eb7e2bfc7eecf03bdd0fed01cbefd7134541`, ZIP SHA-256 `9b0c94b67b2ddd2415a6dddfe1f4385db64461541770d52525a81b984036ba2f` — for identification only.)
  2. **Mod Manager + Editor 0.5, GitHub release** — https://github.com/Jasonafex/urban-reign-redux/releases/tag/v0.5.0 — "build the tested release from your own Urban Reign (USA) ISO and choose your packs." The Mod Manager is free, needs no sign-in, and "the shared patch reuses unchanged data from the player's ISO instead of redistributing it." With no extra fighter packs, the build is byte-identical to the tested 0.5 release. **This is the lawful route — but only for someone who already owns the original USA game.** The game ISO and PCSX2 are not included, and the builder refuses non-USA editions.
- **Licence and terms — what was actually found:** No LICENSE file exists in the repo. README's own terms line: "This repository hosts the release, website and setup support. It does not include the editor's complete source. **No blanket license is granted to third-party game or character assets.** Not affiliated with or endorsed by the original game's publisher." So: the mod tools are distributed freely by their author, but there is **no open-source licence stated** for the mod code, the editor's full source is not in the repo, and **no permission is granted over the game's own assets or the guest characters**. Nothing in Redux grants Western Heart any right to use Urban Reign's or Tekken's files. Publishing plans (not done): a Nexus Mods listing is planned but not created; a TekkenMods listing was investigated and the request "has not been sent". No paywall and no login bypass were involved in finding any of this.
- **Verdict for Western Heart:** Do NOT download the all-in-one package. The Mod Manager route is lawful only with an owned USA ISO. The repo already holds the USA ISO as release `urban-reign-iso-v1` plus the full extracted teardown, so Redux's disc adds nothing Western Heart does not already have. **What Redux is actually worth to this project is its methods and measurements, not its disc:** grounded idles and skeleton repairs (feet on the floor, no floating/sinking — the same class of fault as the Piece-1 King Tyrant sink), Tekken 8 stances, string-connection fixes (mid-string knockdowns → heavy staggers), the Player 2 select freeze fix, the expanded stage select, the multiplayer camera controls, and the mouth-animation pilot. Those are techniques to study and rebuild in our own code. **It cannot run here:** the Mod Manager and Editor are Windows `.exe` files that build a PS2 disc for PCSX2. Nothing in Redux runs on this Linux VM or in the web game, and its ISO cannot be wired into the web build.
- **Do not confuse it with the other project:** `thiagordsfx/urban-reign-recomp` is a separate PC recompilation port of Urban Reign (GPL-3.0, per its listing), not Redux. It also needs the player's own PS2 disc image (USA SLUS-21209). Found in GitHub code search; its README was not read this pass, so no claim is made about its state beyond that.

---

## 7. Select any character — gating today, and the plan

Source: Part D. **59 fighters** in `game/js/roster-full.js` (`FULL_ROSTER`). **50 pickable on the select grid today. 9 hidden (not pickable on the grid).**

### 7a. How the gating actually works

The grid shows a fighter unless it is hidden. `select-screen.js` line 480 builds the grid from every roster entry except the ones in `SELECT_HIDDEN` (lines 472–477). `selectVisible()` in `core-set.js` line 72 always returns `true` — it hides nothing. **There is no lock flag on any fighter.** There is no lock, no unlock, no greyed-out card state in the select code at all: a fighter is either on the grid (clickable) or not there.

**The 9 hidden fighters:**

| Hidden fighter | Why hidden |
|---|---|
| RIN, BYOU, TOU, SHA, KAI, JIN, RETSU | The seven vesseled souls. The code comment says they stay in the roster data for story/other modes and return later as unlockable boss-type characters once story modes progress — that unlock path is future design, not code. **CORRECTED 2026-11-08 (canon):** the seven are RIN, BYOU, TOU, SHA, KAI, JIN, RETSU — GYOU is unvesseled, not one of the seven. "No body of their own yet" is wrong as a file claim: RIN/SHA/KAI/RETSU bodies already exist on disk and passed the loader gate (see §7b); only the roster still says `model: null`. JIN fights as Phantom, its vessel, and is pickable — not hidden. |
| ZEN, GYOU | The two unvesseled souls. ZEN has a model (`zen`) but is still in `SELECT_HIDDEN` (see the contradiction note below). GYOU has no rigged model yet — 7 unrigged Tripo statics, archive-only. |
| RYUJI | No model (`model: null`, `modelPending: true`). **CORRECTED 2026-11-08 (canon):** RYUJI is NOT a soul — Ryuji Yamazaki is an inspiration for CORNERSTONE along with The Rock (CANON.md ~1299–1311). The pure-Yamazaki `ryuji` entry is a leftover duplicate that "is untouched and stays in the repo"; no model build and no unhide are owed for it. |

**The safety net at fight start.** If a fighter with no model ever reaches a fight anyway, `main.js` lines 1260–1267 swap it out silently: the player becomes the first ready fighter in roster order (today that is ZEN), and the enemy becomes a random ready fighter (`randomEnemy`, which also filters out `modelPending` and model-less entries, `main.js` line 663). So a model-pending fighter can never fight on another fighter's body — that is the owner law in code. But the swap is silent: the player is never told the pick changed.

**The arcade foe pool is wider than the grid.** `_pickFoe` (`modes.js` lines 1375–1382) draws from the *whole* roster with no model-pending filter — only the player and `custom` are excluded. The `startFight` safety net above is what stops a model-pending foe from actually fighting. One hole: ZEN has a model, so ZEN can be drawn as an arcade foe and will fight with **no animation bank at all** in public builds (see below).

**Unlockables are not fighter locks.** `unlockables.js` (used by Treasure Battle, `modes.js` lines 1070–1080) grants titles/frames/cosmetics. No fighter is gated behind it.

**Only 2 fighters are proven in a live fight:** Pantera and Demonio (Piece 1 playtest, 2026-11-07). The other 48 pickable fighters have a model key and a bank on paper, but no live fight proof was found.

### 7b. The full gating table (all 59)

"Pickable" means: on the select grid today (not in `SELECT_HIDDEN`) with a model key that exists in `MODEL_URLS` (`game/js/assets.js`). "Bank" is the animation bank `bankIdFor` resolves to — the motion the fighter actually plays. A fighter with no bank fights on embedded locomotion + procedural combat only, never another character's clips. `*` on a soul bank means the bank is bound but moot: the fighter has no model, so the bank never plays.

| Fighter | Tier | Model key | Bank | Status | Gate | Unblocker |
|---|---|---|---|---|---|---|
| RIN | Soul | — (null) | jin* | HIDDEN | Roster `model: null` + hidden only — body `rin-body.glb` (8,808,768 B) already on disk, loader-verified 2026-11-08 (18 skinned, 49 bones, 1.750 m) | Set `model: 'rin-body'` + remove from SELECT_HIDDEN. No new model needed. |
| BYOU | Soul | — (null) | jin* | HIDDEN | No body by canon design — a soul has no body of its own; it fights through its vessel + celestial stand (`docs/souls/VESSELS-AND-STANDS-OWNER-2026-10-21.md`). Vessel Zui is pickable (`model: 'zui-attire1'`). | No model build — canon forbids it. BYOU fights through vessel Zui + the soul-spirit stand (wiring verified 2026-11-08: `soul-spirit.js` → `main.js` startFight → `game.js` attachSoulSpirit). Stays hidden as a card per the 2026-10-22 directive. |
| TOU | Soul | — (null) | paul | HIDDEN | Roster `model: null` + hidden; base Paul models exist unwired in the Godot lab (`lab/game/assets/t3_paul.glb` + `t3_paul_t3real.glb`, the latter already keyed as `t3-paul`) | Convert/rig a Paul model for `game/` + set `model` + unhide. Neither lab file is game-ready as-is (159 validator errors — zero-length normals; 18-joint T3 skeleton, not the 49–50 Mixamo gate). The `pantera` fallback ride is an owner call, not this lane's decision. |
| SHA | Soul | — (null) | xiaoyu | HIDDEN | Roster `model: null` + hidden only — body `sha-body.glb` (16,816,172 B) already on disk, loader-verified 2026-11-08 (32 skinned, 50 bones, 1.750 m) | Set `model: 'sha-body'` + remove from SELECT_HIDDEN. No new model needed. |
| KAI | Soul | — (null) | eddy | HIDDEN | Roster `model: null` + hidden only — body `kai-body.glb` (25,644,156 B) already on disk, loader-verified 2026-11-08 (24 skinned, 50 bones, 1.750 m) | Set `model: 'kai-body'` + remove from SELECT_HIDDEN. No new model needed. |
| RETSU | Soul | — (null) | bryan | HIDDEN | Roster `model: null` + hidden only — body `retsu-body.glb` (472,476 B) already on disk, loader-verified 2026-11-08 (27 skinned, 49 bones, 1.750 m) | Set `model: 'retsu-body'` + remove from SELECT_HIDDEN. No new model needed. |
| ZEN | Soul | zen | NONE (unmapped) | HIDDEN | Hidden by SELECT_HIDDEN + no public bank | Remove from SELECT_HIDDEN + bind a bank (Dural bank is private-build only) |
| GYOU | Soul | — (null) | hwoarang | HIDDEN | Unvesseled soul; no rigged model — 7 unrigged Tripo statics, archive-only (`roster/gyou/spirit-body/`, verified 2026-11-08: 1 mesh, 0 skins, 0 joints, 0 animations) | Rig the spirit-body source (Blender + GameRig, per `roster/gyou/spirit-body/SPEC.md`) → `model-rigged.glb` → set `model` + unhide. Rig job BLOCKED 2026-11-08 on disk quota (no writable repo clone). |
| PANTERA | Main | pantera | king | PICKABLE | — | — |
| DEMONIO | Main | demonio-a1 | jin | PICKABLE | — | — |
| PHANTOM | Main | phantom | yoshimitsu | PICKABLE | — | — |
| DIABLO | Main | diablo | heihachi | PICKABLE | — | — |
| SKULL | Main | skull | bryan | PICKABLE | — | — |
| SAM-UR-A1 | Main | sam-ur-a1 | gunjack | PICKABLE | — | — |
| SAKU RA | Main | saku-ra | xiaoyu | PICKABLE | — | — |
| ZUI | Bonus | zui-attire1 | jin | PICKABLE | — | — |
| KINPO | Bonus | kinpo | jin | PICKABLE | — | — |
| WATERFALL | Bonus | waterfall | jin | PICKABLE | — | — |
| KING TYRANT | Bonus | king-tyrant | eddy | PICKABLE | — | — |
| BURGER | Bonus | burger | bryan | PICKABLE | — | — |
| AWA POP | Bonus | awa-pop-attire2 | nina | PICKABLE | — | — |
| SCIMITAR | Bonus | scimitar | jin | PICKABLE | — | — |
| PURPLE RAIN | Bonus | purple-rain | jin | PICKABLE | — | — |
| NIGHTWOLF | Bonus | nightwolf | julia | PICKABLE | — | — |
| DIO | Bonus | dio-attire1 | heihachi | PICKABLE | — | — |
| CAPE JONES | Bonus | cyborg-x | gunjack | PICKABLE | — | — |
| MICHIKO | Bonus | michiko | jin | PICKABLE | — | — |
| STAR | Bonus | star | xiaoyu | PICKABLE | — | — |
| TORCH | Bonus | torch-tripo-a1 | anna | PICKABLE | — | — |
| BRUNO | Bonus | bruno-attire2 | bryan | PICKABLE | — | — |
| N3GΔTIV0 | Bonus | negativo-attire1 | bryan | PICKABLE | — | — |
| THOR | Bonus | thor | bryan | PICKABLE | — | — |
| YUKIHYŌ | Bonus | yukihyo-attire1 | armorking | PICKABLE | — | — |
| SLICE | Bonus | slice | bryan | PICKABLE | — | — |
| DOC FRANK | Bonus | doc-frank-big | bosconovitch | PICKABLE | — | — |
| KEVIN | Bonus | baek | bryan | PICKABLE | — | — |
| MARIPOSA | Bonus | mariposa-butterfly-default | xiaoyu | PICKABLE | — | — |
| DXMMII | Bonus | dxmmii-tripo | jin | PICKABLE | — | — |
| CHARGER | Bonus | charger | bryan | PICKABLE | — | — |
| DOROWANI | Bonus | dorowani | gon | PICKABLE | — | — |
| CHATUR | Bonus | chatur | ogre | PICKABLE | — | — |
| POND | Bonus | pond | raven | PICKABLE | — | — |
| RYUSAN | Bonus | ryusan | luckychloe | PICKABLE | — | — |
| TOBI | Bonus | tobi | hwoarang | PICKABLE | — | — |
| MEGAMI | Bonus | megami | jun | PICKABLE | — | — |
| MENAJERII | Bonus | menajerii | roger | PICKABLE | — | — |
| KRONOS | Bonus | kronos | king | PICKABLE | — | — |
| DEATHFANG | Bonus | deathfang | heihachi | PICKABLE | — | — |
| RYUJI | Bonus | — (null) | UNMEASURED | HIDDEN | Not a soul — leftover pure-Yamazaki duplicate entry of CORNERSTONE, hidden under the owner no-duplicate law (CANON.md ~1299–1311) | No model build, no unhide. The entry stays in the repo untouched per canon. |
| CORNERSTONE | Bonus | ryuji-rock | king | PICKABLE | — | — |
| KORESHI | Bonus | koreshi | heihachi | PICKABLE | — | — |
| RAVE | Bonus | kiko-tanaka | lei | PICKABLE | — | — |
| BUFFALO BILL | Bonus | buffalo-bill | law | PICKABLE | — | — |
| VAIN ABEL | Bonus | vainabel | UNMEASURED | PICKABLE | Bank unmeasured (no MOVESET_MAP entry; moveset JSON not read) | Read movesets/vainabel.json anim_bank / t3_source and confirm a bank binds |
| CAIN ELIAS | Bonus | cain-elias | king | PICKABLE | — | — |
| CHORDZ | Bonus | chordz | UNMEASURED | PICKABLE | Bank unmeasured (no MOVESET_MAP entry; moveset JSON not read) | Read movesets/chordz.json anim_bank / t3_source and confirm a bank binds |
| GASHADOKURO | Bonus | gashadokuro | kuma | PICKABLE | — | — |
| AOTSUKI | Bonus | aotsuki | kuma | PICKABLE | — | — |
| SILVERTONGUE | Bonus | silvertongue | xiaoyu | PICKABLE | — | — |

**Notes on the table:**
- **ZEN is the odd one.** The comment above `SELECT_HIDDEN` says "Only ZEN and GYOU stay selectable as spirit fighters" — but both ZEN and GYOU are *in* the hidden set, so neither is on the grid in the code as it stands. ZEN also has **no animation bank in public builds**: `FIGHTER_BANK` maps ZEN to `null` on purpose (owner decision 2026-10-24 — ZEN is neither Heihachi nor Julia; the base chain is Eleven/Twelve → Dural). The Dural bank only binds when `T3_BANKS.dural` exists, which only happens in private builds (`t3anims.js`, `__WH_PRIVATE_ASSETS`). So even if ZEN were unhidden, ZEN would fight bankless in the public build. GYOU is model-pending as well, so the comment is wrong for both. The select-screen comment contradiction needs an owner call: unhide them, or fix the comment.
- **VAIN ABEL and CHORDZ are pickable but their banks are UNMEASURED.** Neither has a `MOVESET_MAP` entry in `fighter.js`, and their moveset JSONs were not read in this pass, so `bankIdFor` depends on those files' `anim_bank` / `t3_source` fields, which are unknown here. If a field names a source with no bank, they fight bankless.
- **Own-slot banks are NOT active.** `OWN_SLOT_BANKS` in `fighter.js` is an empty object (2026-11-07: the TTT2 own-character banks retarget with a strong forward pitch — walks nearly horizontal — so binding them would make fighters look worse). ZUI, KINPO, PURPLE RAIN, CHORDZ, BRUNO, AOTSUKI and others still play shared banks (mostly `jin`) until their own clips pass by eye. That is a quality gap, not a gate: they are pickable, they just do not move like their own base character yet.
- **Bank `jin` for RIN/BYOU/KAI/GYOU is the resolved animation bank, not a mistake.** `bankIdFor` resolves the moveset `demonio` through `game/assets/movesets/demonio.json` (`anim_bank: 'jin'`, `t3_source: 'jin'`) to the `jin` bank. `demonio` is the moveset id; `jin` is the bank it plays on. (The canon correction that "RIN/BYOU's bank is demonio, not jin" is about the moveset, not the resolved bank — the Bank column here names the bank.)
- **Model keys are not proof the GLB file is on disk.** All 50 pickable fighters' model keys exist in `MODEL_URLS` (195 keys total), and a model-key-guard test exists (`game/tests/model-key-guard.test.mjs`). But a key is a path string, not a load test. `MODEL-STATUS.md` (2026-10-17/18) is three weeks stale: it still lists BURGER, SCIMITAR, MICHIKO, STAR, TORCH, DIO, BRUNO, YUKIHYŌ, SLICE, CHORDZ and VAIN ABEL as "no model in repo", while the current roster gives all of them model keys (Tripo pulls landed since). **Update 2026-11-08 (Lane 5): the four soul bodies were loader-verified** — Khronos glTF Validator + the repo's own vendored GLTFLoader (`game/vendor/`) in headless Chromium: rin-body, sha-body, kai-body, retsu-body all parse, all skinned with Mixamo-style bones incl. Head, all 1.750 m tall (rin-body carries 1 validator error — declared buffer length 23,140,476 vs 8,638,536 actual BIN — stale metadata only; every bufferView/accessor ends inside the real BIN, and the file loads). Whether the other 46 pickable fighters' GLBs actually load is still **UNMEASURED** — it needs a fresh loader-path check, not a doc read.
- **The header count is stale.** `roster-full.js` says "48 selectable fighters" in its header comment, but the array holds **59** entries. The real pickable count is 50, not 48.

**The lists disagree — counts:**

| List | Count | What it says |
|---|---|---|
| `game/js/roster-full.js` header comment | 48 "selectable fighters" | Stale. The array actually holds 59 entries. |
| `game/js/roster-full.js` array (`FULL_ROSTER`) | **59** | 8 souls + 7 main + 44 bonus. This is the code truth. |
| `GAME-DEV-BRIEFING.md` §4 | **36 named fighters** | 9 souls + 7 main + 20 bonus + boss Sun Rā. |
| `ROSTER.md` | **9 souls + 7 main vessels** (16 in detail) | Plus the Trader and the Assembled Soul as post-launch design, not roster entries. |
| `AUDIT.md` (2026-11-06) | 36 named; "~49 entries per the Oct 22 audit" | Both stale now: the array has grown to 59. |

Disagreements, plainly: (1) Briefing says 36, code has 59 — **24 fighters were added after the briefing's count**. The briefing was never updated. (2) Briefing names boss **Sun Rā** — Sun Rā has **no entry** in `roster-full.js` at all. (3) `ROSTER.md` lists **9 souls including JIN (the Blade Soul)**. The roster array has **8 soul entries** (no `jin` entry) because JIN fights as Phantom, its vessel — but JIN is still a live soul in the code, not a legacy leftover: `jin_soul` is in `soul-spirit.js` NINE_SOULS (vessels `['phantom']`), `heartmind.js` NINE, and `movesets.js:32`, and appears in `MOVESET_MAP` (`jin_soul: 'yoshimitsu'`) and `SELECT_HIDDEN` as the soul's hidden card. **CORRECTED 2026-11-08 (canon):** the nine souls are RIN, BYOU, TOU, SHA, KAI, JIN, RETSU, ZEN, GYOU; JIN the Blade Soul is NOT Jin Kazama, and the fighter built on that data is DEMONIO. (4) The briefing (§8) still says "36-fighter select". The grid actually shows **50 cards + 1 RANDOM card**.

### 7c. The select-any-character plan

1. **Unlock the hidden souls the honest way — per fighter, not one blanket "give each a model":** a model-pending fighter can never fight on another fighter's body (owner law). **CORRECTED 2026-11-08 (canon):** there are 7 model-pending souls, not 8 — RYUJI is not a soul and gets no model and no unhide (leftover entry, stays untouched). RIN, SHA, KAI, RETSU need only a config change (`model: '<x>-body'` + remove from `SELECT_HIDDEN` — bodies already on disk, loader-verified). GYOU needs the Tripo spirit-body rig job. TOU needs a Paul convert/rig. BYOU needs NO model at all — BYOU fights through vessel Zui + the celestial stand (wiring already in place). One fighter at a time, in the repo's own short-jobs-first order.
2. **ZEN needs an owner call first:** ZEN has a model but no public bank (Dural is private-build only) and sits in `SELECT_HIDDEN` despite a comment saying ZEN stays selectable. Either bind a public bank and unhide, or keep ZEN hidden and fix the comment. Do not unhide ZEN bankless — a bankless fighter fights on procedural combat only and reads as broken, the same class of fault as the Piece-1 King Tyrant fight.
3. **Gate the arcade foe pool on the same rule as the grid:** `_pickFoe` must exclude `modelPending` and bankless fighters (ZEN today), the way `startFight`/`randomEnemy` already do. Until then, any hidden fighter can still be drawn as a ladder foe.
4. **Make the safety net loud, not silent:** when `main.js:1260–1267` swaps a pick, show the player what changed ("no model — switched to …") instead of swapping silently. This is the same fix as Break 2's "show the drawn foe" rule.
5. **Show locked/taken slots Tekken's way:** locked fighters greyed out and unpickable (`0x58`); a fighter already taken on the same screen marked taken (`0x59` / "SOLD OUT"). There is no lock flag today — add the display state, not a new lock system.
6. **Prove the 50, one at a time:** a model key is not a load test. Each pickable fighter needs a load + idle + one fight check before it counts as selectable. Only Pantera and Demonio are proven today. (VAIN ABEL and CHORDZ first: their banks are UNMEASURED.)
7. **Fix the stale counts:** `roster-full.js` header ("48 selectable"), `GAME-DEV-BRIEFING.md` ("36 named fighters", "36-fighter select"), and `ROSTER.md` (9 souls) all disagree with the code's 59 entries / 50 pickable. Update them to the code truth when the next fighter lands — do not leave three different numbers in the repo.

---

## 8. The chimera inventory — what actual code and data can be wired in

Source: Part E (HEAD `3334ebf`). **≥38,946 files inventoried: ≥38,811 in `teardown/` (4.05 GB) + 135 in `game/data/` (15.4 MB).** Every total is a floor — the recursive git-tree came back truncated and provably misses whole subtrees. **Wireable into `game/`: ~38,500 files** (everything except ~600 reference-only docs and ~40 unopened archives). "Wireable" means the file can be loaded or converted into the web build — it does **NOT** mean cleared to use.

**Origin split (estimated from folder + source, not by opening all ~39,000 files):** JAY'S OWN ≈ 1,250 (teardown tools + docs ~1,164; `game/data/` own JSONs/JS ~85) · COMMERCIAL-DERIVED ≈ 37,500+ · COMMUNITY-FREE (CC0/CMU) 2 files + free sources catalogued in docs · UNKNOWN ≈ 120 files (mostly unopened `.rar` / `.7z` / `.zip` archives) plus the subtrees the truncated tree missed.

**Licence warning — read this first:** this repo is public and it holds extracted commercial-game material, against its own `AGENTS.md` rule (no copyrighted/leaked game files in public repos). Every item flagged COMMERCIAL-DERIVED below is inventoried only. Nothing flagged that way is cleared for copying into any build, public or private, until Jay makes the licence call. Jay's own position (use the actual files, chimera build of mods) is recorded as his, not adopted here. The Tekken 7 frame data also carries its own warning in its README: TheBigTuna's repo has no licence file and TekkenDocs data has no redistribution licence stated — author check needed before verbatim redistribution.

### 8a. The biggest, most useful wireable items (exact paths)

1. `teardown/tekken3/movesets/` — 21 fighters' move tables, ~28 MB, 3,247 moves (king 3,409,137 B biggest). COMMERCIAL-DERIVED.
2. `teardown/urban-reign/textured-models/` — 72 textured GLBs, 32.7 MB, 733 images (Part C's named follow-up swap). COMMERCIAL-DERIVED.
3. `game/data/moveset-library/banks/t3.json` (5,673,360 B, 4,648 moves) + `banks/wrestling.json` (5,698,275 B, 4,409 moves). COMMERCIAL-DERIVED (frame/move data).
4. `teardown/soulcalibur-2/stages/` — 41 stage GLBs, 165 MB (`stage_m000.glb` 27,752,736 B). COMMERCIAL-DERIVED.
5. `teardown/tekken3/stages/` (15 panorama OBJs) + `teardown/tekken3/tim-output/` (17,116 files: 8,556 TIM + 8,559 PNG — exact count, not the old capped listing). COMMERCIAL-DERIVED.
6. `game/data/t7-frame-data/` — 40+ Tekken 7 fighters' frame data. COMMERCIAL-DERIVED (see licence warning above).
7. `game/data/t8_frame_tables.json` — 326 KB of Tekken 8 frame tables. COMMERCIAL-DERIVED; origin **UNMEASURED** in Part E (t8 origin not pinned).
8. `teardown/tekken5/t5_motion_manifest.txt` + `t5_char_codes.txt` — the 498-name Devil Within / Tekken 5 motion index. COMMERCIAL-DERIVED (names only; see §5b).
9. `teardown/urban-reign/animations/motion-packs/` — 46 PPKs (31 per-character packs, 10 team/tag packs) + `motion/general_*.gyu` shared pools + `motion-names/` (484 proven move names). COMMERCIAL-DERIVED.
10. `teardown/wwf-no-mercy/` — 17 arenas (OBJ+VC) + animation bank (436 decoded `.npy` clips). COMMERCIAL-DERIVED.
11. `teardown/tekken6/models/parts/` — 3,444 GLBs (model parts). COMMERCIAL-DERIVED.
12. `lab/skeleton/canonical_skeleton.json` + `retarget_maps.json` — WH-Canonical-22 skeleton + retarget maps (mixamo49, rigify13, tekken3_rigid27). **JAY'S OWN** — the cleared base the audit already landed.
13. `teardown/western-heart-asset-catalog.md` — catalog of free/open assets: Quaternius CC0, Mixamo, CMU mocap, Sketchfab CC-BY stages. **JAY'S OWN** (licence per entry, re-verify before shipping). COMMUNITY-FREE sources live here.
14. `teardown/urban-reign/tools/` — 25 own-code Python tools (`ur_decode.py`, `ur_gyu.py`, `ur_tex_extract.py`, `ur_build_textured.py`, `ur_embed.py`, `ur_name_bridge.py`, …). **JAY'S OWN.**
15. `teardown/tekken5/tools/iso9660_extract.py` + `t5_survey.py` — own-code survey tools; rerunning them is the path to any further Tekken 5 extraction. **JAY'S OWN.**

**Two flags worth Jay's eye (Part E):** the coverage matrix is stale for WWE 2K19 (says 0%, folder holds a 754 MB raw extraction) and DOA4 (says 15%, folder holds converted GLBs); and `game/data/sound-bank.json` calls Eastern Mind "owner-original" though it is a 1994 commercial title — flagged in Part E as COMMERCIAL-DERIVED, not cleared.

**Still unmeasured in the inventory:** bulk-file contents (~38,000 files inventoried by path/size/extension only, never opened); licences for psxrecomp, QuickBMS/UnrealPak, kaiutzi21 `LICENSE.txt`, MikuMikuModel.7z; `t8_frame_tables.json` origin; T7 frame-data second source family; per-file voice sources beyond Pantera/announcer; no live-load check of anything; the tree truncation means true totals are higher than stated.

### 8b. Archive.org — lawful reference material (read, measure, rebuild; do not copy)

Source: Part D §5. These are publisher-copyrighted scans (Namco, Prima) that archive.org hosts freely viewable in its Manual Library / Folkscanomy collections. They are **not public domain**. Usable the way this teardown uses them: read them, measure how the real games work, rebuild that behaviour in our own code. Do not copy their text, art, or layouts into the game.

1. **Tekken 3 NTSC-U/C Manual** — the single most useful reference for select-any-character + arcade mode. Mode select, Arcade Mode (one player vs the computer, no continue limit, Player 2 Start jumps in and switches to Versus), VS Mode, Team Battle, Tekken Force, Practice, Option modes, pause menu, game screen. https://archive.org/details/tekken-3-manual
2. **Tekken 1–5 Strategy Guides (Prima / EGM bundle)** — six guides in one item: Tekken (EGM), Tekken 2 Official Strategy Guide (1996), Tekken 3 Prima Official Strategy Guide (1998 — all moves, all combos, all characters, pro strategies, secret characters, ~8 pages per character), Tekken 4 Prima (2002), Tekken 5 SG. https://archive.org/details/tekken_1-5_strategy_guides
3. **Urban Reign (USA) Manual** — the brawl-layer reference: weapons/items, special attacks, dodging, teaming up with a partner, multi-fighter rules, character info. https://archive.org/details/ps2_Urban_Reign_USA
4. **Tekken 5 (USA) Manual** — Story Battle, Arcade, Arcade History, and **Tekken: Devil Within** (play as Jin Kazama in a 3D action-adventure game). https://archive.org/stream/ps2_Tekken_5_USA/Tekken_5_USA_djvu.txt
5. **Tekken 2 Arcade Kit Installation Manual (Namco, 1995)** — "a one-player game first pits the player against seven randomly selected computer opponents." https://archive.org/download/namco-tekken-2-arcade-kit-manual/tekken_2_kit_installation_manual.pdf
6. **Tekken 3 Kit Installation and Operation Manual** — https://archive.org/details/arcademanual_Tekken3_man
7. **Tekken: Dark Resurrection PSP Manual** — Arcade Mode (the complete arcade game), Quick Battle, Game Sharing, Ad Hoc / Infrastructure modes. https://archive.org/stream/SonyPSPManuals/Tekken%20-%20Dark%20Resurrection%20%28Europe%29_djvu.txt
8. **Tekken 3 Prima Strategy Guide (standalone item)** — https://archive.org/stream/tekken-3-prima-strategy-guide/Tekken%203%20Prima%20Strategy%20Guide_djvu.txt

Arcade flyers are *not* on archive.org — they live at The Arcade Flyer Archive (https://flyers.arcade-museum.com/videogames/list?manuf_id=1522). **Excluded, NOT sources:** Urban Reign (EU) PS2 ISO item and the PlayStation 2 RetroAchievements collection (game-file zips) — disc images, do not get them.

---

## 9. Wiring plan — which spec items fix which of the 9 Piece 1 breaks

The 9 breaks are from `PLAYTEST-PIECE1.md` (live playtest 2026-11-07, site build Nov 5, commit `2aebf11`); causes from `PIECE1-DIAGNOSIS.md` (HEAD `3334ebf`). Fix in player order. "Spec item" = the D-number from Part A §8 (the differences table).

### Break 1 — Select timer overwrites a picked P2 fighter at 0
**Spec: D1.** Tekken 3 measured: timer ~20 s (20·T frames, growing 3 s per extra unlocked fighter past 10), and at 0 each side gets the fighter under the cursor — never random. **Fix:** at 0, confirm the fighter under each side's cursor; never overwrite an existing pick/highlight. Stop the timer the moment either side locks (`main.js:621–657`, `select-screen.js:824–860`). No measured Tekken source supports 99 seconds or a random pick — both are invented and go.

### Break 2 — Confirmed P2 Demonio replaced by King Tyrant by fight start
**Spec: D2 + D3.** Most likely cause (diagnosis §2): Arcade has no P2 pick — the ladder foe is a random draw (`modes.js:_pickFoe`), and King Tyrant was the draw. **Fix:** in Arcade, show one pick only (or label the second side "CPU — random ladder foe"), and show the drawn foe's name/card before each fight starts. Never let the select screen look like a P2 pick exists in a one-player mode. If a Versus swap is ever proven, that is a separate bug — no code path supports one today.

### Break 3 — King Tyrant spawns T-posed, sunk waist-deep in the floor
**Spec: D3 gate + §6c Redux methods.** Likely cause (diagnosis §3): the Xiaoyu-bank neutral-bind bug — fixed in commit `e8147929` (Nov 7, after the Nov 5 playtest build), which regenerated the bank. **Fix: none in code until a live re-check on the current build confirms the bank fix cured King Tyrant.** If the sink survives, measure the hip-track height in the bank data next. General rule from the diagnosis, now spec: a fighter with no working animation bank must never be fielded as a foe — gate ladder foes on a working bank, the way model-pending fighters are already gated out of fights (`main.js:1266–1273`). Redux's grounded-idle / skeleton-repair methods (feet on the floor, no floating/sinking) are the reference technique for any remaining sink — study and rebuild, do not copy Redux files.

### Break 4 — Pantera loses health passively in the Tyrant fight
**Spec: D3 gate (same as Break 3).** Cause (diagnosis §4): there is no health drain anywhere in the code — the loss is King Tyrant attacking with no visible animation. Combat is decided by frame data, not by animation, and the hitbox code falls back to a frame-data box for a T-posed fighter. **Fix:** fix Break 3 first (the bank), then re-check. The gate in Break 3 is the fix: no bankless fighter as a foe. No drain code exists to remove.

### Break 5 — Damage ~1% per Pantera hit vs ~20% per counter; Surge does nothing; grab never lands
**Spec: D11 feedback + §6b SPA shape (no formula change).** Cause (diagnosis §5): not a formula bug. Pantera hits *harder* on paper (power 1.3 vs Demonio defense 1.0). A clean jab is ~9 health (~5% of 180); a *blocked* jab chips at 12% (~1 health, ~0.6%) — and 20 such hits land Demonio at ~93%, exactly what the playtest saw. Demonio's AI blocks reactively, so Pantera was mostly chipping a guarding Demonio. Demonio's counters are the other side of the same formula (counter-hit bonus ×1.2 + big base damage ≈ 36 health, ~20% — a normal counter launcher). Surge: L is not the full-meter super — L fires a plain 18-damage strike costing the whole meter, while the real super (Nine-Soul Release, 30 unblockable damage) only fires on 1+2+3+4; the L strike fails silently in hitstun/blockstun/recovery or out of reach. Grab: very small window (throw reach 1.7 m; bodies separate at 1.45 m — ~0.25 m usable), every miss silent. **Fix:** (a) make blocked vs clean hits look different on screen (the block spark and the hit flinch read the same today) — this is the D11 attack-data HUD (damage numbers, COUNTER / CLEAN HIT labels); (b) show a failed-surge / failed-grab cue instead of failing silently, and put the real input for the full-meter super on the button hint itself; (c) tune the AI's block rate down so a player can tell a blocked jab from a whiffed one; (d) widen the grab's connect window a little, since 0.25 m is unforgiving at the slow sim speed (Break 9). **Do not change the damage formula** — it is not the bug. Urban Reign's SPA meter shape (§6b) is the reference for how the Surge/super should feel when its feedback is rebuilt.

### Break 6 — "BREAK THE THROW — TAP LP" stuck on screen
**Spec: UNMEASURED cause — live repro first, no fix written yet.** The prompt is supposed to hide itself after 900 ms (`main.js:263`), and there is one element only. Two gaps were found but neither alone explains a permanently stuck prompt: the paired-throw path never calls the hide, and every fresh grab re-shows the prompt and resets the 900 ms timer. **Fix (only after a live repro confirms which gap it is):** hide the prompt on every throw resolution path (paired throws included) and on round end, and never re-show it within 900 ms of a hide. Do not write the fix blind.

### Break 7 — Pause unclickable, Escape does nothing, Clothing Back unclickable
**Spec: D15 + diagnosis §7.** Measured Tekken pause (T3 decompiled): Start pauses mid-round; Start again does NOT unpause — only CANCEL does; pause menu has CANCEL / COMMAND (move list) / RESET (leave to main menu); music volume drops while paused. Cause in code: three small omissions, not one overlay — `#wh-pause-btn` inherits `pointer-events: none` from `.screen.hud` (`styles.css:27`) with no re-enable (unlike the training-quit button, `styles.css:708–711`); Escape was simply never wired to pause (the only Escape binding is `main.js:1599`, exiting replay view); the clothing dialog has no CSS positioning rules at all, unlike its siblings `#wh-options` / `#wh-records` and `#wh-pause`. **Fix:** give `#wh-pause-btn` `pointer-events: auto`; add an Escape key handler that opens pause; give `#wh-clothing` the same fixed-position/z-index/show rules as `#wh-options`; build the pause menu Tekken's way (CANCEL / COMMAND / RESET).

### Break 8 — Result "YOU LOSE" heading clipped to "YOU L…"
**Spec: UNMEASURED cause — live repro first, no fix written yet.** No clipping cause exists in the current code (`.panel` is 460 px max, `.panel h2` capped at 32 px — "YOU LOSE" at 32 px fits several times over; no ellipsis/nowrap rule touches the result title). Most likely explanations are outside it: the playtest ran the Nov 5 build and the stylesheet has changed since, or the clipped heading was a different element (the round banner, `styles.css:287`, renders at up to 120 px). **Fix: none until a live repro** — first inspect `#result-title` at 1919 px and diff `styles.css` at the playtest commit.

### Break 9 — HIGH graphics: ~1 timer tick per 30 s; LOW: ~1 per 7–20 s
**Spec: §6b 60-fps bar + diagnosis §9.** Cause: arithmetic, not a timer bug. Fixed step 1/120 s × max 4 steps per render frame = at most 1/30 s of game time per frame; at ~1 fps on HIGH, one game second takes ~30 wall seconds. The timer is not broken; the renderer is too slow at 1919 px on that machine, and the fixed-step cap turns slow rendering into slow time. Urban Reign ran multi-fighter brawls at 60 fps — that is the bar. **Fix:** do NOT raise the step cap blindly (it exists to stop a spiral) — instead make HIGH cheaper at big widths (cap pixel ratio at 1 above phone widths, or drop shadows first), and separately drive the *displayed* timer from wall time so the clock never lies about how long a round has lasted.

### The rest of the differences table (beyond the 9 breaks)

From Part A §8 (D1–D17). D1, D2, D3, D15 map to Breaks 1, 2, 3/4, 7 above. The rest are the next lanes, in this order:
- **D4 — Continue:** add a "CONTINUE? 9" countdown on Arcade loss (Start = retry the SAME rung), then GAME OVER only when it runs out. Keep RETRY LADDER as the post-game-over option. Time Attack keeps no-continues (already correct).
- **D5 — Endings + unlocks:** wire clear → unlock (next fighter in a fixed order, or a WH equivalent) and show it on the clear screen. Do not invent Tekken's exact unlock order for WH fighters — use the WH roster order.
- **D6 — Costumes:** add a costume pick at select (button-cycled, like T3) or mark costumes as a separate lane. First check `game/js/attires.js` + `customization/` — whether costumes exist at all is **UNMEASURED**.
- **D7 — Locked/taken slots:** show locked fighters greyed out and unpickable; in Team Battle, mark already-picked fighters as taken on the same screen.
- **D8 — Versus loser rules:** after a Versus loss, offer the loser: same fighter + same stage, same fighter + new stage, or new fighter + random stage. Lock the winner's fighter until a loss.
- **D9 — Tag:** a new system, not a fix — schedule as its own lane. Do not bolt tag onto Team Battle.
- **D10 — Team Battle:** team-size choice (1–8, or at least 3/5/8); CPU team least-used first instead of pure random; per-fight replay result screen.
- **D11 — Training:** in order — dummy stance/guard settings, then attack-data HUD (damage + counter/clean-hit labels), then VS CPU difficulty/level, then record/playback. Gungaku already covers the programmable half. (D11's HUD is also the Break 5 fix.)
- **D12 — Survival:** stepped difficulty bands (T3's win-count bands); exclude the last four foes; prefer least-met foes; per-fighter win-count result screen. (The 25% restore per win is **UNMEASURED** against Tekken — do not change it on this evidence alone.)
- **D13 — Time Attack:** 9 or 10 fights of 2 rounds / 60 seconds (pick one and say which); per-stage times + total on the result screen; keep no-continues. Grade thresholds need a measured source or must be labeled WH-original.
- **D14 — Treasure Battle:** rank ladder with promotion matches; Special Matches (powered-up boss foe, better chest); chests 1–3 per win instead of exactly 1.
- **D16 — Stages per rung:** assign a stage per rung when the ladder is built (D3); fix boss stages (rung 5 / rung 6) to their own stages.
- **D17 — Arcade options:** add a pre-ladder options step (rounds, round time, difficulty) for Arcade; keep Time Attack fixed.

### Order of work (the fix team's sequence)

1. Breaks 1–2 (select timer + Arcade one-pick) — D1, D2.
2. Break 3 live re-check on current HEAD (bank fix `e8147929` may already have cured it) + foe-bank gate — D3.
3. Breaks 5–6 feedback (blocked/clean HUD, failed-move cues) — D11 + Break 6 live repro.
4. Break 7 clicks + pause menu — D15.
5. Break 9 speed (cheaper HIGH) + Break 8 live repro.
6. D4 continue, D16 stages per rung, D17 Arcade options.
7. D5 unlocks, D8 Versus loser rules, D12 Survival, D13 Time Attack, D14 Treasure, D10 Team, D6 costumes (after the check), D11 Training.
8. D9 Tag as its own lane. HeartMind gaps from §5d (platforming/doors, Force, symbols, stage select, unlocks) as HeartMind lanes. Urban Reign textured-model swap (§6a) as its own lane. Select-any-character plan (§7c) one fighter at a time.

---

## 10. What is still UNMEASURED (do not guess — measure next)

1. **T7/T8 select timer:** exact seconds and at-0 behavior. Only Tekken 3's timer is measured.
2. **T7/T8 locked/DLC slot behavior** (greyed? hidden? "SOLD OUT"?). T3's `0x58`/`0x59` are measured; T7/T8 equivalents are not.
3. **T7/T8 continue rules in detail** (exact countdown length and options).
4. **Survival restore amount:** "a small amount" is all the sources say; the current 25% cannot be confirmed or denied.
5. **Tekken 5/6/7 stage order in Arcade** (only boss stages are pinned).
6. **Costumes in the current build** (check `game/js/attires.js` + `customization/` first).
7. **Stage-per-rung in the current build** (live check: does the stage actually stay the same through the Arcade ladder?).
8. **Break 6 (stuck throw prompt) and Break 8 (clipped YOU LOSE)** — no cause found in code; both need a live repro before a fix is written.
9. **Devil Within contents:** every DW file's contents; enemy AI patterns, wave tables, platforming/door systems, boss attack patterns and numbers, Devil Gene fill rates / laser damage / health drain, gem heal values and drop rates, Force values, ranking thresholds; the code → fighter mapping for the 109 char codes; which `stg*.dat` is which DW stage. Blocked on the romD file-table mapping and the `TK5DATA0/1/3` container formats (RE bench, Tekken 5 #16 QUEUED).
10. **The design doc `~/workspace/devil-within-teardown.md` (2026-10-22)** cited by two repo docs — not on this machine; contents unknown.
11. **Whether HeartMind actually plays on the live build.** Code + tests exist; no live playthrough has been watched. A headed playthrough (menu → pick → stage 1 → boss → stage 5 → PURIFIED) is still owed.
12. **Whether each of the 50 pickable fighters' GLBs actually loads today.** Model keys exist; that is a path string, not a load test. `MODEL-STATUS.md` is three weeks stale. VAIN ABEL and CHORDZ banks unmeasured. Live fight proof for 48 of the 50 pickable fighters. ZEN's public-build bank behaviour. The ZEN/GYOU select-comment contradiction needs an owner call.
13. **Urban Reign:** stage place-names (PPK ids only); mission contents (field layout unknown); exact audio counts (listing cap); per-fighter identities (OWNER-pending); whether the 72 game GLBs and 31 moveset JSONs load today; frame data/timings (manual gives shapes, not numbers); repo-wide text search (code-search tool cannot scope to the repo); the `thiagordsfx/urban-reign-recomp` port (found, not read).
14. **Inventory gaps:** bulk-file contents (~38,000 files inventoried by path/size/extension only, never opened); licences for psxrecomp, QuickBMS/UnrealPak, kaiutzi21 `LICENSE.txt`, MikuMikuModel.7z; `t8_frame_tables.json` origin; T7 frame-data second source family; per-file voice sources beyond Pantera/announcer; no live-load check of anything; tree truncation means true totals are higher than stated.
15. **Tekken 6 Scenario Campaign and Tekken 8 Story Mode detail** (named, not measured step-by-step). **T7/T8 Versus stage-select flow in-game** (loser-picks-stage is from tournament rules; casual in-game flow unmeasured). **Repo teardown subfolder contents** beyond top-level listings (Part E completed the inventory by path/size; contents of most subfolders were not opened).

---

## Sources

- **Part files (this folder):** `TEARDOWN-PART-A-TEKKEN-MODES.md` (arcade/ladder/select/all modes, D1–D17, full links) · `TEARDOWN-PART-B-DEVIL-WITHIN.md` (Devil Within hunt, HeartMind today, mapping) · `TEARDOWN-PART-C-URBAN-REIGN.md` (Urban Reign inventory, systems, Redux) · `TEARDOWN-PART-D-ROSTER-ARCHIVE.md` (roster gating table, archive.org items) · `TEARDOWN-PART-E-WIREABLE-INVENTORY.md` (≥38,946 files, origin flags, 28 tables).
- **Playtest + diagnosis + audit (this folder):** `PLAYTEST-PIECE1.md` (9 breaks, 2026-11-07) · `PIECE1-DIAGNOSIS.md` (causes, HEAD `3334ebf`) · `AUDIT.md` (2026-11-06).
- **Key public sources (full links in the part files):** Tekken Wiki Arcade Mode; Tekkenpedia Tekken 5; n0madic/Tekken3Remake `docs/research/code/modes.md` (decompiled Tekken 3); Tekken Wiki Treasure Battle / Tag Assault / Urban Reign / Devil Within (Mode); Tekkenpedia Devil Within; UNIFIED Tekken 7 competition rules; TTT2 Xbox 360 manual (archive.org); Tekken 5 USA manual (archive.org); Urban Reign USA manual (archive.org); Jasonafex Urban Reign Redux (github.com/Jasonafex/urban-reign-redux, jasonafex.github.io/urban-reign-redux, releases/tag/v0.5.0).
- **Key repo files (HEAD `3334ebf`):** `game/js/modes.js`, `game/js/main.js`, `game/js/select-screen.js`, `game/js/roster-full.js`, `game/js/fighter.js`, `game/js/brawler.js`, `game/js/heartmind.js`, `game/js/heartmind-campaign.js`, `game/js/input.js`, `game/js/soul-systems.js`, `game/js/frame-step.js`, `game/js/assets.js`, `game/js/stages.js`, `game/styles.css`, `game/menus.css`, `game/index.html`, `docs/modes/TEKKEN-MODES-RESEARCH.md`, `docs/modes/HEART-AND-MIND-INSIDE.md`, `teardown/tekken5/DEVIL-WITHIN-DATA.md`, `teardown/tekken5/t5_motion_manifest.txt`, `teardown/urban-reign/WIRING-INVENTORY.md`, `teardown/urban-reign/CANON-CONVERSION.md`, `teardown/TEARDOWN-COVERAGE-MATRIX.md`, `tools/re/QUEUE.md`.
