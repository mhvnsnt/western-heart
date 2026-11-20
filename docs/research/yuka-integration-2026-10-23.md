# Yuka.js combat-AI integration — 2026-10-23

Owner instruction (verbatim): "Pull all of this stuff in and wire it up and put it to work the best way possible"

## What was pulled

[Yuka.js](https://github.com/Mugen87/yuka) (MIT, (c) 2023 Yuka authors) — the
JavaScript game-AI library (state machines, steering, decision making).
Vendored as `game/vendor/yuka/`:

- `yuka.module.js` — the **official, unmodified** ES-module build
  (`build/yuka.module.js` from `master` @ `10591304811222d6856020d5de129b39ef43b58d`,
  blob SHA `4a4cc6e779b9b4e9fc14b8f2de34fefcae6f729c`)
- `LICENSE` — MIT text from the Yuka repo
- `ATTRIBUTION.md` — source, version pin, update instructions

Why the `.module.js` build: the game loads vendor code as ES modules
(`game/index.html` importmap pattern); the new AI modules import Yuka via
relative path (`../../vendor/yuka/yuka.module.js`), so no `index.html` change
was needed (avoids the ui-sources gate entirely).

Why Yuka fits: it is **decoupled from the render loop** — its `State` /
`StateMachine` classes take any owner object. The brains never touch the
fighter, the foe, or physics; they read a plain snapshot and emit intents.
Matches the combat-sim architecture (sim never reads physics state).

## What was built — `game/js/ai/`

1. **`combat-state.js`** — `CombatBrain`: hierarchical FSM on real Yuka
   classes. Root regions `ground` / `air`; ground states
   `neutral → attack → block → hit`; air states `launch` (juggled) /
   `down` (knocked down). Classic Yuka pattern: transitions evaluated in
   each state's `execute()`. Emits `{ state, move }` directives; the
   `AIController` executes them through its existing `try*` calls.
2. **`grapple-chains.js`** — `GrappleChain`: Yuka FSM for
   `idle → clinch → throw → ground → idle` (plus `reversed` on escape).
   Advisory intents: `tie-up` / `commit-throw` / `chain-ground` /
   `disengage`. Owns the clinch→throw→ground sequence in the controller.
3. **`reversal-logic.js`** — `ReversalBrain`: pure split-second reversal
   framework. Frame-window rules (Tekken-flavored): slow startup (≥15f)
   → sidestep; mid (≥10f) → duck; fast/active → block (the honest answer);
   blockstun + 50 meter → v-reversal; foe recovery in range → punish;
   thrown → throw-break with the arm read. Every defensive option is
   confidence-gated by `personality.reaction` so weak AI stays fair.

## Wiring (drive, don't replace)

- `game/js/ai.js` — `AIController` constructs the three brains; `update()`
  builds one snapshot per tick (`_snapshot`), asks the reversal brain first
  (existing reactive block stays as fallback), then on decide ticks the
  combat brain picks the state: `block` → guard, `hit`/`launch` → ride it
  out, `attack` → unlocks the surge/rage/urge install lanes (never wasted
  into pressure anymore), `neutral` → the existing spacing/poke/grab game
  unchanged. The moveset-driven `_attack(f, kind)` pools and the whiff-punish
  lane are untouched. `GungakuAI extends AIController` keeps working
  (constructor signature unchanged).
- `game/js/ghost-ai.js` — `GhostAI` takes optional `brain` /
  `brainMix` params; when the ghost model has no data for a situation, the
  Yuka brain (`CombatBrain.decideFromGhostSnap`) drives the fallback path.
  Defaults preserve the old behavior exactly.

## Verification

- `node --test game/tests/yuka-combat-ai.test.mjs` → **24/24 pass**
  (deterministic: all RNG injected; covers state transitions, region
  switches, grapple chain, reversal windows, ghost hook).
- `node --check` clean on all five touched/added JS files.
- No existing test imports `game/js/ai.js`; the one test importing
  `ghost-ai.js` (`fighter-depth.test.mjs`) is unaffected — the change is
  strictly additive (verified by the `no brain -> old fallback` test).
- Full-suite + fight-harness runs are CI's job on the PR (needs the full
  tree + browser; this worker is API-only by design).

## Follow-ups (not in this PR)

- Air-tech: `LaunchState` emits `move: 'tech'`; the fighter has no
  `tryTech` yet — the controller currently rides out juggles. Wire when a
  tech move exists.
- `foeStartupFrames` is `null` until the fighter exposes per-move startup
  on `p.attack`; the reversal brain degrades gracefully to block.
