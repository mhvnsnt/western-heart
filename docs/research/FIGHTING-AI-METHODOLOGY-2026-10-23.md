# Fighting Game AI Methodology — 2026-10-23

**User directive (verbatim 2026-10-23):** "Pulling everything from the list and wire it all up and where it'll work and where it's appropriate"

**Scope:** FightingICE/DareFightingICE (Ritsumeikan University) + Tencent "Hidden Ones" AI fighting tech (GDC). What the research teaches, what Tencent validates, and exactly how it wires into Western Heart's CPU AI (`game/js/ai/`).

---

## 1. FightingICE / DareFightingICE — the platform

- **What:** Open-source fighting-game AI research platform from the Intelligent Computer Entertainment Laboratory, Ritsumeikan University (Japan). Running since 2014/2015; annual Fighting Game AI Competition at IEEE CIG/CoG.
- **APIs:** Java natively, Python via Py4J, OpenAI Gym wrapper, gRPC interface. Game resources from *The Rumble Fish 2* (courtesy of Dimps).
- **The rules that matter:**
  - **16.67ms decision budget** — the agent must pick one of ~40 actions every frame at 60fps. Search depth is brutally capped; this is why MCTS and rolling-horizon methods dominate instead of deep planning.
  - **15-frame state delay** — "the information sent to AIs will have a delay of 15 frames... to simulate human response time." The AI never sees the true current state. This single rule is what keeps competition AIs humanlike instead of input-readers.
  - **Forward model** — the platform hands agents a simulator: "if I do X and the foe does Y, what happens." Every winning agent plans through it.
  - **Standard league:** round-robin, 400 HP, 60s rounds. **Speedrunning league:** beat the sample MCTS AI as fast as possible.
- **DareFightingICE** adds 3D sound design and a blind-AI track (AIs that play from audio only) — not wired into WH, noted for accessibility research later.
- **Sources:** https://www.ice.ci.ritsumei.ac.jp/~ftgaic/index-2.html · GitHub org: TeamFightingICE · DareFightingICE paper: https://arxiv.org/pdf/2203.01556

## 2. What a decade of competition taught (the winning approaches)

**MCTS era (2014–2019).** Monte-Carlo Tree Search through the forward model was the default champion architecture: simulate action sequences, backpropagate the HP-differential score, play the best first action. The platform even ships a sample MCTS AI as the speedrunning target. Lesson: *in a 16.67ms budget, shallow stochastic search through a good forward model beats deep cleverness.*

**2020 winner: ERHEAPI — Enhanced Rolling Horizon Evolution Algorithm with opponent-model learning** (Tang, Zhu, Zhao, Lucas, *IEEE Transactions on Games* 2020 — https://arxiv.org/pdf/2003.13949).
- **RHEA** evolves *action sequences* through the forward model (not a tree — a population of plans), then executes the first action of the best sequence. Matches MCTS strength with less domain knowledge.
- **The opponent model is the breakthrough:** learned *live during gameplay* from history observations — supervised (cross-entropy), policy-gradient, and Q-learning variants. Plans are evaluated against *what this opponent is likely to do*, not minimax worst-case. This was the only non-MCTS agent in the 2019 top five (2nd place), then won 2020 outright.
- Lesson for WH: *model the player, don't just model the game.* A frequency table of the player's habits, updated live, is the practical 90% of ERHEAPI's idea without a neural net at runtime.

**DRL era (2021+).** PPO + self-play + diversity-based RL, Elo-based opponent selection (ERHEAPPO). Strong, but the field's own surveys note the catch: *commercial fighting games run on consumer hardware with limited RAM/compute* — training-time DRL doesn't ship; what ships is cheap inference-time logic. Naruto Mobile's HESP (below) is the industry answer to the same constraint.

**The generalization problem** — the competition's stated aim: "strong against any unseen opponents (AIs or players), character types, and play modes." DRL agents overfit to training opponents; search + opponent-modeling generalizes. For WH's roster (45+ fighters, player-created characters incoming via the creation suite), *generalization beats memorization* — our CPU must play sensibly against characters it has never seen, using frame data, not matchup tables.

## 3. Tencent — what the industry validates (GDC)

**AI motion in-betweening (MoreFun Studios, Elvis Liu — GDC interview, https://gamesbeat.com/how-tencent-is-using-ai-to-make-fighting-games-more-fluid-gdc-interview/):**
- AI generates the frames *between* keyframes in real time. Same keyframes never play identically twice — movement varies with camera angle and positioning, killing the "foot sliding" and repetition that makes fighting games feel robotic.
- Shipped as **VISVISE / MotionGen** (GDC 2026): multimodal motion-generation model; motion-in-betweening module generates 200 frames in 4 seconds; autoskinning at 90%+ weight accuracy.
- **WH take:** technique only (proprietary). Our animation pipeline already keys on teardown data; the lesson is *procedural variation between keyframes* — a future animation-system pull, not this AI pass.

**Self-play AI agents ("millions of rounds"):**
- Each *Hidden Ones* character gets its own dedicated agent; each agent trains *per character matchup* through self-play. "If we only have a pool of 20 characters, it takes two or three days... 400 characters, it takes a year. Two years ago, I presented a way to train all 400 characters within a week."
- **Naruto Mobile (2016)** was the first commercial fighting game to ship DRL, via **HESP (Heterogeneous Exploitation Self-Play)** — built specifically because per-character DRL training was too expensive at roster scale.
- **WH take:** we don't ship trained nets — we ship the *design pattern*: per-character personality + live adaptation. Our `char.ai` personalities (Pantera hunts grabs, Demonio plays fundamentals) are the hand-authored version of per-character agents; the live opponent model is the runtime version of per-matchup adaptation. If we ever train offline, HESP-style self-play against the MCTS brain is the template — but that's a future lane, not this PR.

## 4. What we wired into WH (this pass)

| FightingICE / research lesson | WH implementation | File |
|---|---|---|
| 15-frame human-reaction delay | `ReactionDelay`: brains decide from a snapshot N frames old; N scales 15→8 with difficulty, never 0 | `game/js/ai/reaction-delay.js` |
| Frame-data forward model | `frame-data.js`: seconds↔frames, T7 advantage parsing, `bestPunish()` Tekken punish math | `game/js/ai/frame-data.js` |
| MCTS through the forward model | `MCTSSelector`: UCB1 over the CPU's move pool, depth-2 rollouts, 3ms hard budget | `game/js/ai/mcts-select.js` |
| ERHEAPI live opponent model | `OpponentModel`: per-situation frequency tables, Laplace smoothing, learns foe's fastest button + guard/mash habits live | `game/js/ai/mcts-select.js` |
| Tekken-style difficulty curve | `delayFramesForDifficulty()` + `mctsRolloutsForDifficulty()` + `scaledAi()` extension: rookie = 15f delay, heuristic only; boss = 8f delay, 24 MCTS rollouts | `game/js/modes.js`, `game/js/ai.js` |
| Bug found by the frame-data lens | `foeStartupFrames` was fed **seconds** (0.217) into a brain that reasons in **frames** — the ≥15f sidestep window could never open. Now converted via `startupFramesOf()` | `game/js/ai.js` `_snapshot()` |

**Deliberately NOT wired:** runtime neural nets (consumer-hardware constraint — the field's own conclusion); perfect play (see §5); input reading (the 15f delay exists precisely to forbid it); blind-audio AI (DareFightingICE track — future accessibility research).

## 5. The beatability contract (Tekken-style difficulty, not perfect play)

The CPU must be *fun to fight*, not optimal. Guards, all wired:

1. **Human delay always.** Even the hardest CPU decides from a ~8-frame-old world. It can never react to a button it hasn't "seen" yet.
2. **Probabilistic execution.** Every brain rolls against `reaction`/`aggression` — the CPU *fails reads* like a person. Reaction 1.0 still only blocks fast mixups ~75% of the time.
3. **MCTS is tier-gated.** Below difficulty 0.35 the CPU uses the old heuristic move picker — rookies fight a footsies brain, veterans fight a searching one.
4. **Bounded search.** 3ms budget, depth 2, candidate pool limited to the fighter's own moveset. No exhaustive solving, no frame-perfect punishes beyond what the frame data honestly allows (1f execution margin in `bestPunish`).
5. **Personality first.** Pantera still hunts command grabs at 15f delay; Demonio still plays spacing. The tech sharpens the character — it never replaces it.

## 6. Verification

- Unit: `game/tests/fighting-ai.test.mjs` — frame math, punish selection, delay buffer, opponent-model learning, MCTS determinism + budget.
- Existing suite untouched and green: `game/tests/yuka-combat-ai.test.mjs` (the reversal-logic frame contract is unchanged — `foeStartupFrames` was always *specified* in frames; only the feed was wrong).
- Play: `tools/proof-harness/fight.mjs` CPU-vs-CPU — must reach `"round":"fight"` with no `[pageerror]`; watch that the CPU blocks/punishes at higher tiers and plays loose at low tiers.

## 7. Future lanes (not this PR)

- **Offline self-play tuning** (Tencent pattern): pit the MCTS brain against itself across the roster to tune personality stats per character — HESP-style, but as a data-generation lane, not shipped weights.
- **AI motion in-betweening** (VISVISE/MotionGen technique): procedural variation between keyframes in the animation system — kills robotic repetition.
- **DareFightingICE blind-AI track**: audio-driven AI as accessibility research.
- **Ghost AI training**: record player matches → distill into opponent-model priors per rank tier.
