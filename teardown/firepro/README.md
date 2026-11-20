# Fire Pro Wrestling World Teardown — Pull Plan

**Game:** Fire Pro Wrestling World | **Steam App ID:** 564230 | **Owned:** YES (vil3m, 133.5h)
**Status:** Research in progress (top-5 coordinator)

## User context

133 hours — mostly WATCHING and SIMULATING fights, not playing. This is the
user's reference for fight simulation and creation depth.

## What we're pulling (user priorities)

1. **CPU vs CPU simulation** — how Fire Pro simulates AI-vs-AI fights.
   The vision: build characters in WH, then watch them fight.
2. **Creation depth** — edit-a-wrestler system. Moves, AI logic, appearance,
   parameters. How deep does it go?
3. **AI logic programming** — how wrestlers are programmed to fight their own
   way (tendencies, move preferences, behavior).

## The vision (user's words)

"the ultimate fighting game where you can build almost any character from
any fighting game and it'll be like our game style inputs"
— deep creation + fight simulation + WH Tekken-style inputs.

## Directory layout

```
teardown/firepro/
├── README.md              (this file)
├── PULL-LOG.md
├── SIMULATION.md          (how CPU vs CPU works — technique, not code copy)
├── CREATION-DEPTH.md      (edit-a-wrestler system breakdown)
├── AI-LOGIC.md            (AI behavior programming system)
└── research/              (analysis docs → public repo)
```

## Wiring targets

| Pull | Wires into |
|------|-----------|
| Simulation system | New: `game/js/simulation.js` (watch mode) |
| Creation depth | `packages/creation-suite/` (expand parametric depth) |
| AI logic | `game/js/ai/` (fighter behavior programming) |

## Notes

- Extract TECHNIQUE, not assets. Fire Pro is sprite-based; we're after systems.
- Simulation mode is a new game mode, not a replacement for fighting.
- ALL CHARACTERS ARE ADULTS.

## Coordination

- Research: top-5 coordinator
- Status: issue #866
