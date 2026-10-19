# TEKKEN MODES — RESEARCH
## Lane G (MODES), Western Heart Round-2 · 2026-10-18

Researched from: Tekkenpedia (Survival / Time Attack / Arcade mode articles),
the Tekken Wiki (Team Battle), the official Tekken 3 EU manual
(TEAMKAMPSLÄGE / ÖVERLEVNADSLÄGE / TIDSATTACKLÄGE / TEKKEN FORCE-LÄGE /
TRÄNINGSLÄGE), and a T8 Team Battle mod reference video.
Mode-by-mode fidelity notes below; "WIRED" = implemented in `game/js/modes.js`.

---

## 1. SURVIVAL — WIRED
- **Debut:** Tekken 2; present in every sequel since.
- **Rules:** Fight an unlimited stream of CPU opponents. One round per fight.
  Health **carries over** — the bar is never refilled to 100%; each win
  restores only a small amount of health. Lose once and the run ends
  (back to Match 1). Score = opponents beaten; T2/T3 showed top-10
  leaderboards (T3 let you unlock Gon by entering "GON" as initials).
- **WH wiring:** single-round matches (`roundsToWin: 1`), HP carried via
  `opts.hpCarry` = remaining HP + 25% restore per win. Record = waves
  beaten, persisted in localStorage (`wh_records.survival`).

## 2. TIME ATTACK — WIRED
- **Debut:** Tekken 2; T3 identical (minus Gon/Dr. Bosconovitch fights).
- **Rules:** Same ladder shape as Arcade, but the clock is the score:
  fastest total time wins. T5 fixed the format at 9 stages, default
  settings (2 rounds, 60s/round, normal difficulty). No pausing (until T4),
  no endings, no credits — the timer is the game.
- **WH wiring:** 8 single-round fights (`roundsToWin: 1`) against escalating
  AI; wall-clock time is accumulated per fight and the run is graded:
  **S** < 4:00, **A** < 6:00, **B** < 9:00, else **C**. Best total time per
  fighter persisted (`wh_records.timeattack`). A loss ends the run (Tekken
  rules: no continues in Time Attack).

## 3. TEAM BATTLE — WIRED
- **Debut:** Tekken 2; present through TTT2; cut from T7 (a fan mod later
  restored it for T8 with a 10% winner HP bonus).
- **Rules:** Each side fields a team of up to 8 fighters. Winner stays on:
  when a fighter falls, the next in line steps in. Like Survival, the
  winner's **health carries over and increases slightly per win**.
  T5:DR-era convention: ~10–15% recovery on a win. After the last member
  falls, a win/loss tally is shown.
- **WH wiring:** 3v3 (roster-friendly; Tekken allows up to 8, we field 3).
  Single-round fights, winner keeps remaining HP + 15% recovery into the
  next bout. CPU team is 3 random vessels. End screen shows the tally
  (fighters remaining per side). Team pick flow: the mode controller
  collects 3 picks from the select screen before starting.

## 4. TEKKEN FORCE (T3) / DEVIL WITHIN (T5) — DOCUMENTED, NOT WIRED
- **Rules:** A short beat-'em-up: 4 stages (T3) of side-scrolling brawling
  against waves of Tekken Force soldiers with a boss at the end of each
  stage. T5's Devil Within is the same idea with a third-person camera.
- **Why not wired:** our engine is a 1v1 versus fighter — a beat-'em-up
  needs multi-attacker targeting, walk-plane depth movement, and pickup
  items. That is a whole new engine subsystem, not a mode. Honest gap:
  revisit when (if) a brawler subsystem exists. The closest wired
  equivalents are SURVIVAL and IMMORTAL QOMBAT (endless waves, 1v1).

## 5. TEKKEN BALL (T3) / TEKKEN BOWL (T7) — DOCUMENTED, NOT WIRED
- **Rules:** Tekken Ball: 1v1 volleyball — hit a beach ball back over the
  net; the ball is charged by attacks and damages whoever it hits.
  Tekken Bowl: full bowling minigame (T7, Ultimate Tekken Bowl DLC).
- **Why not wired:** both need a ball-physics minigame loop (projectile
  ownership, net collision / pin physics). Engine gap. Documented as a
  future minigame lane, not a modes-lane wire-up.

## 6. PRACTICE / TRAINING VARIANTS — PARTIALLY WIRED
- **Rules:** T3 Practice: free sparring vs a configurable dummy (T5+ added
  command display, frame data, punishment training).
- **WH status:** TRAINING mode (round-1) wires the core: endless rounds vs
  a passive dummy. Documented future: CPU-difficulty select, command-list
  overlay (moveset lane owns the data), record/playback.

## 7. ARCADE LADDER VARIANTS / TREASURE BATTLE (T7) — DOCUMENTED
- T5's arcade mode became an unlimited ranked ladder (kyu/dan ranks, fight
  money); T7's Treasure Battle is the same idea with loot boxes. Our
  ARCADE (round-1, 6 fixed fights) plus TIME ATTACK and SURVIVAL cover the
  ladder space; a ranked endless ladder is a future netplay-adjacent lane.

---

# ORIGINAL WESTERN HEART MODES (canon-grounded — CANON.md citations)

## 8. IMMORTAL QOMBAT — 不死クォンバット — WIRED
- **Canon:** CANON.md § SUN RĀ — "He puts souls through endless tiers and
  twenties of 不死クォンバット (fushi kwonbatto — 'Immortal Qombat') —
  death tournaments where the prize is keeping your soul and the cost of
  losing is becoming part of him." And: "His arena is a pocket realm
  where the trial's rules don't apply."
- **Rules from canon:** endless waves; NO reincarnation (the trial's rules
  don't apply in the pocket realm); losing a wave = absorbed by the sun;
  winning = you eat — the survivor feeds on the fallen.
- **WH wiring:** endless single-round fights, HP carried + 35% restore per
  win ("the sun feeds the survivors just enough"), plus a stacking
  **soul-eaten** buff (+5% power per wave — the eater grows). On loss the
  run ends and the vessel's name is added to Sun Rā's hunger count
  (`wh_records.qombatEaten`, a plain integer of souls eaten). Waves beaten
  persisted as the record. Naming rule honored (CANON.md): the UI uses
  不死クォンバット everywhere except the one line Sun Rā himself speaks —
  he gets the English "IMMORTAL QOMBAT."

## 9. SOUL SURGE GAUNTLET — WIRED
- **Canon:** CANON.md §4 THE NINE SOULS — "The Nine-Soul Meter: In combat,
  a fighter can invoke a Soul Surge — channeling one of the *other* eight
  souls for ten seconds, borrowing its signature techniques. This is not a
  mechanic layered onto the fiction. It *is* the fiction: the nine are
  fragments of one being, and in the surge, the fighter remembers."
- **WH wiring:** an 8-fight ladder, one fight per *other* soul. Each fight
  opens with that soul channeling through you for the whole bout —
  engine translation of the canon blessing, drawn from the soul's nature:
  RIN dignity → defense, BYOU sickness → unreadable (speed), TOU battle →
  power, SHA sand → erosion (chip), KAI sea → flow (speed+regen), JIN blade
  → precision (power+reach), RETSU violence → raw power, ZEN stillness →
  defense+regen, GYOU motion → speed. Banner announces each channeling.
  Single-round fights, escalating difficulty.

## 10. TRADER'S MIMIC — WIRED
- **Canon:** CANON.md §5 THE TRADER — "The Trader's fighting style is
  mimicry — it wears the opponent's moveset like a borrowed coat."
  (Also: "Nothing here is real, but the prices are.")
- **WH wiring:** a single best-of-3 duel at the Phantom Marketplace. The
  Trader opens with a random borrowed moveset; **every round it loses, it
  changes into YOUR moveset** — trying on your coat to beat you with it.
  Win and the Trader pays up: your mimic-victory count is recorded
  (`wh_records.traderWins`) and the Trader "sells" you the win banner.
  Lose and the Trader keeps your coat — rematch to take it back.

## Canon discipline
No invented lore anywhere above: every original mode is a rules
translation of a named CANON.md passage, cited per mode. The five forces,
the nine souls, the reincarnation math, and the Assembled Soul are
untouched by this lane — round-1's story mode owns them.
