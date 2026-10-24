# Gang Beasts Teardown — Pull Plan

**Game:** Gang Beasts | **Steam App ID:** 285900 | **Owned:** YES (vil3m, 11.2h)
**Status:** Research in progress (top-5 coordinator)

## What we're pulling (user priority)

"Perfect for added physics to our Tekken style game and heart and mind
inside mode"

1. **Physics technique** — how does Gang Beasts do floppy/partial-ragdoll?
   The TECHNIQUE, not the assets.
2. **Character control with physics** — how do you control a physics-driven
   character and keep it fun?
3. **Grab/throw physics** — wrestling-relevant: how grabs work with soft bodies.

## How it feeds WH

WH's physics directive: **partial ragdoll** — authored animation is
authoritative; physics takes over the struck limb / landing, then blends
back (~0.25–0.4s). Gang Beasts shows the extreme end; we take the technique
and Tekken-ify it.

Current stack: Rapier.js (rigid) + Jolt (soft-body, PR #846). Gang Beasts
research informs the blend layer.

## Directory layout

```
teardown/gang-beasts/
├── README.md
├── PULL-LOG.md
├── PHYSICS-TECHNIQUE.md
└── research/
```

## Wiring targets

| Pull | Wires into |
|------|-----------|
| Physics technique | `game/js/softbody.js`, `game/js/physics.js` (blend layer) |

## Coordination

- Research: top-5 coordinator
- Status: issue #866
