# Yuka — attribution & wiring

- **Upstream:** https://github.com/Mugen87/yuka
- **Version vendored:** 0.7.8 (2026-10-23)
- **License:** MIT (see LICENSE in this dir; header embedded in the build)
- **File:** `yuka.module.js` — the package's ESM build, unmodified.
  Engine-independent (no DOM/three.js dependency).

## Why
Owner directive 2026-10-23 (Track 7): NavMesh pathfinding for the
Heart and Mind Within open zones — dozens of AI grunts pursuing /
flanking / swarming across multi-level structures. Yuka is the
three.js-ecosystem standard game-AI library (steering, navmesh,
state machines) by three.js maintainer Mugen87.

## Lane split (issue #866)
- **Track 7 (this):** NavMesh / pathfinding — NavMesh, NavMeshLoader,
  Corridor, Vehicle + steering (Seek/Separation/FollowPath).
- **Other track:** combat state machines — State, StateMachine,
  GoalEvaluator.
- Both import this same vendored build. No duplicate pulls.

## What uses it
- `game/js/story/navmesh.js` — WHNavMesh (buildFromRects /
  buildFromTriangles, findPath, clampStep), WHNavZoneSet
  (multi-level zones + off-mesh links), WHGrunt / WHSquad
  (pursue / flank / swarm with separation).

## Verified API notes (Yuka 0.7.8, node-tested 2026-10-23)
- Contours: `new Y.Polygon().fromContour(Vector3[])`, winding must be
  positive-area CCW in the xz-plane:
  `(x1,z1)->(x1,z2)->(x2,z2)->(x2,z1)`.
- `fromPolygons()` merges coplanar + convex regions.
- `findPath(from, to)` → Vector3[] corridor-smoothed waypoints.
- `clampMovement(currentRegion, start, end, out)` → new region; when
  the end point is already on the mesh, `out` is untouched and the
  caller keeps `end` (handled in WHNavMesh.clampStep).
- `SeparationBehavior` reads `vehicle.neighbors` (caller-maintained).
