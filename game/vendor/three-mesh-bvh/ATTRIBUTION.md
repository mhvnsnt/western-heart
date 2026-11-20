# three-mesh-bvh — attribution & wiring

- **Upstream:** https://github.com/gkjohnson/three-mesh-bvh
- **Version vendored:** 0.9.16 (2026-10-22)
- **License:** MIT (see LICENSE in this dir)
- **File:** `index.module.js` — the package's ESM build, unmodified.
  Imports `three` (resolved by the game's import map to the vendored r160).
- **Import map:** `"three-mesh-bvh": "./vendor/three-mesh-bvh/index.module.js"`

## Why
Owner playtest bug 2026-10-22: "HIT DETECTION BROKEN — only ~1/10 attacks
land." The combat resolves sphere-vs-sphere hitbox/hurtbox tests
(game/js/game.js `_resolveCombat`). three-mesh-bvh gives BVH-accelerated
raycast + `shapecast` against real posed meshes (incl. `StaticGeometryGenerator`
for SkinnedMesh), so we can verify and tighten hit detection against actual
geometry instead of hand-placed spheres.

## What uses it
- `game/js/hitdetect.js` — `WHHitDetect`: builds a BVH per fighter mesh,
  runs a precision shapecast between the attacker's striking limb segment and
  the defender's posed body. Runs in **verify mode** (logs sphere-vs-mesh
  disagreements for tuning; does not change combat outcomes) until the
  hitbox tables are re-derived from it.

## Gameplay rule
BVH builds are per-model and cached; never rebuild mid-fight. The sphere
system stays authoritative until a lane promotes the BVH path with proof.
