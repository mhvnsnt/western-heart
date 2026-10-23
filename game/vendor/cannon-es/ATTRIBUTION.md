# cannon-es — attribution & wiring

- **Upstream:** https://github.com/pmndrs/cannon-es
- **Version vendored:** 0.20.0 (2026-10-22)
- **License:** MIT (see LICENSE in this dir)
- **File:** `cannon-es.js` — the package's ESM build, zero dependencies, unmodified.
- **Import map:** `"cannon-es": "./vendor/cannon-es/cannon-es.js"` (game/index.html)

## Why
Western Heart had no physics engine: jump/launch motion was hand-written per
comment in game/js/t3anims.js, and the owner's feel target calls for extra
physics (partial ragdoll à la Gang Beasts / Human Fall Flat / MK Royal
Rumble — NOT fully ragdoll). cannon-es is the lightest maintained three.js
physics (MIT, ESM, no build step, no WASM) that fits our no-build-step stack.

## What uses it
- `game/js/physics.js` — `WHPhysics`: cannon-es world, arena prop bodies
  (knockable debris), impact debris chunks, KO launch impulses.
- Wired at boot by `game/js/integration.js` (lazy, try/catch — game runs
  without it if the module fails to load).

## Gameplay rule (determinism)
cannon-es is for **visuals only** (debris, props, KO tumble). Combat
simulation stays on the game's own fixed-step logic; netplay rollback must
never depend on cannon-es state.
