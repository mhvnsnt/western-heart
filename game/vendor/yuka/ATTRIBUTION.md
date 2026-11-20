# Attribution — Yuka.js

Vendored from the official repository. **Unmodified build.**

- **Project:** Yuka — JavaScript library for game AI
  (https://github.com/Mugen87/yuka)
- **Author:** Mugen87 (https://github.com/Mugen87)
- **License:** MIT — see `LICENSE` in this directory
  (Copyright © 2023 Yuka authors)
- **Build vendored:** official ES-module build `build/yuka.module.js`
  from `master` @ `10591304811222d6856020d5de129b39ef43b58d`
  (committed 2023-01-16), blob SHA
  `4a4cc6e779b9b4e9fc14b8f2de34fefcae6f729c`
- **Used for:** the combat AI brain — `game/js/ai/combat-state.js`
  (hierarchical combat state machine), `game/js/ai/grapple-chains.js`
  (grapple chain state machine). Yuka's `State` / `StateMachine`
  classes drive the CPU fighter's decisions; the game code only
  executes the resulting intents through its own `try*` calls.

No changes were made to the vendored build. To update: replace
`yuka.module.js` with the new official build and record the new
commit SHA + blob SHA here.

---

## Track 7 addition (2026-10-23) — NavMesh / pathfinding lane

- **Lane split** (issue #866): the combat-state-machine lane above
  stays as-is. Track 7 (cutscenes & story mode) uses the **same**
  vendored build for **NavMesh/pathfinding only**: `NavMesh`,
  `Corridor`, `Vehicle` + steering (`Seek`/`Separation`/
  `FollowPathBehavior`). No second copy of Yuka was pulled.
- **What uses it:** `game/js/story/navmesh.js` — `WHNavMesh`
  (`buildFromRects` / `buildFromTriangles`, `findPath`, `clampStep`),
  `WHNavZoneSet` (multi-level zones + off-mesh links),
  `WHGrunt` / `WHSquad` (pursue / flank / swarm with separation)
  for Heart and Mind Within open zones.
- **Verified API notes** (node-tested 2026-10-23 against this build):
  contours need positive-area CCW winding in the xz-plane, e.g.
  `(x1,z1)->(x1,z2)->(x2,z2)->(x2,z1)`; `fromPolygons()` merges
  coplanar+convex regions; `clampMovement(region, start, end, out)`
  is 4-arg — when the end point is already on the mesh, `out` is
  untouched (handled in `WHNavMesh.clampStep`); `SeparationBehavior`
  reads `vehicle.neighbors` (caller-maintained).
