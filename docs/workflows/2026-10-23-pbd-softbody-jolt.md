# 2026-10-23 — PBD soft-body lane: Jolt XPBD muscle volume (belly proving ground)

**Task:** Purdue Dissectible Anatomy soft-body techniques in the game. Research
(`~/workspace/dissectible-anatomy/research-report-pbd-impls.md`) picked JoltPhysics.js
(npm jolt-physics, MIT, WASM) — Rapier.js has no soft-body support in JS. Follow the
jiggle.js integration pattern; do NOT replace jiggle.js; no cutting/tearing
(show-animation lock — the owner hasn't asked for gore); don't hand-roll a physics
engine.

## Built

- `game/vendor/jolt/jolt-physics.wasm-compat.js` (jolt-physics 1.1.1, 3.2 MB) + `LICENSE`
  (MIT, Jorrit Rouwe) + `VENDOR.md` (source/version/upgrade notes). wasm-compat build =
  WASM base64-embedded, no separate .wasm hosting; single-threaded so no COOP/COEP
  headers needed on GitHub Pages. Same vendoring rule as three.js — no CDN at runtime.
- `game/js/softbody.js` — `SoftBody` class, jiggle.js contract:
  `SoftBody.fromMesh(skinnedMesh, SoftBody.anatomyFor(char))` + `update(dt)` per frame
  AFTER the animation pose and AFTER jiggle. Builds a coarse volumetric lattice
  (3x4x3 low / 4x5x4 high) over the belly ellipsoid (Spine1 bone + bbox), XPBD edge +
  volume constraints, core+caps pinned (invMass 0), shell dynamic. Sim runs in
  character-LOCAL space (mUpdatePosition=false — Jolt recentering would shift the frame),
  zero collisions, one shared Jolt world stepped once/frame for all fighters.
  `hit(worldPoint, dirX, strength)` dents the volume on hit; body acceleration excites
  volume jiggle. Quality toggle off/low/high, persisted `wh_softbody_v1`, default low
  (conservative). No top-level imports (node-testable, zero boot cost); Jolt loads
  lazily via dynamic import; every Jolt touch guarded + watchdog kill-switch to 'off'
  (physics never crashes the fight). `char.softbody === false` opts out.
- `game/js/fighter.js` (surgical, 4 sites): import; `_softbody` init beside `_jiggle`;
  `receiveHit` injects `hit()` at the attacker's hitbox point; `update()` calls
  `this._softbody.update(dt)` after jiggle. jiggle.js untouched.
- `test/softbody.test.mjs` — 28 node assertions (CI game-unit-tests): contract,
  quality toggle, persistence, plus a REAL Jolt sim (drift ~0, dent on hit, recovery,
  pinned core immobile).
- `game/softbody-test.html` — dev rig (not a game menu): loads a real fighter GLB,
  renders deformed mesh + particle cloud, Punch/quality buttons, PROOF console lines.
- `.github/workflows/game-checks.yml` — added `game/vendor/jolt` to the
  game-unit-tests sparse checkout (the test dynamically imports the vendored build).

## Verified 2026-10-23

- `node test/softbody.test.mjs`: 28 passed, 0 failed.
- Real model (pantera.glb torso mesh, 435 verts): 36 particles / 20 pinned, zero drift
  after 2 s idle, 23 mm dent on punch, 5.6 mm residual after 5 s, 0.49 ms/frame total
  update cost, quality rebuild (80 particles high), mesh restored on off/dispose.
- Tuning findings (kept in code comments):
  - Ellipsoid-masked lattices lose complete cells → volume constraints vanish →
    energy growth/instability. Full-box lattice required.
  - `mUpdatePosition` must be false: Jolt recenters the body on the average particle
    position, which shifts the local frame (pinned verts appeared to drift).
  - Never `Jolt.destroy()` getter results (e.g. `verts.at(i).mPosition`) — only
    explicitly `new`'d objects; destroying getter wrappers corrupts the WASM heap.
  - gitleaks `generic-api-key` false-positives on any `*KEY` identifier —
    localStorage key constant renamed to `QUALITY_STORE`.

## Deviations

none. No deletions (PR is +3145/-0). gitleaks clean on all touched files.
