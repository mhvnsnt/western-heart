# 2026-10-22 — Kinpo A1 rig repoint (worker 50)

Config-only repoint: `kinpo` + `kinpo-attire1` MODEL_URLS keys in
`game/js/assets.js` moved from the broken k-NN `model-rigged.glb` to the
already-working tripo-intake rig `roster/kinpo/attires/attire1/model-intake.glb`.

## Why

The intake rig (Blender 4.0.2 + GameRig, facing +X measured by the intake's
two-cue gate — the k-NN batch assumed +Z) landed 2026-10-21 as the
`kinpo-intake-demo` suite-viewer key only (commit d6b72ef); the live keys kept
riding the broken k-NN rig. This PR finishes the job: no re-rigging, no model
file changes, just key repointing.

## Fight-check (keys resolve to real files that load)

- Target exists on main: `roster/kinpo/attires/attire1/model-intake.glb`
  (29,960,676 bytes).
- Header parse: valid GLB 2.0, 1 mesh / 1 skin / 75 nodes / 1 animation,
  the single primitive carries JOINTS_0 (fully skinned) — a real loadable
  rigged file, not a static.
- Rig provenance: `docs/proof/muse-2026-10-21/tripo-intake/kinpo-attire1-20261022-044848/`
  (intake_summary.json: facing +X, residual 2.77deg, validate PASS).
- New `rig_guard.py` run against base-vs-new assets.js: 149 keys both sides,
  zero removed — the guard this round added passes on this PR.
- `node --check game/js/assets.js`: syntax OK.
- `attires.js` kinpo ladder references the MODEL_URLS keys (`'kinpo'`,
  `'kinpo-attire2'`, `'kinpo-t8'`), not asset paths — the two key repoints
  are the complete fix; no other config points at the broken rig.

## Kept, not removed

`kinpo-intake-demo` still points at the intake rig (it is now the same file
the live keys use). Removing the key would trip the new rig-guard; its
comment was updated to reflect the new state instead.

## Phantom: blocked, documented, not faked

Phantom's key (`phantom: '../roster/phantom/attires/attire1/model-rigged.glb'`)
could not be repointed config-only: no working `model-intake.glb` exists for
phantom anywhere on main (only kinpo has one). Pointing phantom at kinpo's
file would ship the wrong fighter — refused. Recorded in
`docs/owner-directives.md` (Rig repoint notes) and flagged to the round
coordinator: the tripo-intake lane must produce a phantom intake rig first.
