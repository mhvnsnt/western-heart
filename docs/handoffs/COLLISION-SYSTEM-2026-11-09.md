# Collision System — handoff (2026-11-09)

**Owner order (2026-11-09):** collision between the models' own bodies,
industry standard, universal across all models, proven first on Megami.
No phasing anywhere: hair touching shoulders sits **on** the shoulders and
is pushed around by them; a tongue coming out pushes the jaw and teeth out
of the way and pushes the lip down — never clipping.

Architecture contract (physics-family doc, shared format):
`COLLISION-SYSTEM.md` in the Physique Lab repo's physics docs. This
handoff records what landed in Western Heart and the measured state.

## What landed

| Piece | Path | State |
|---|---|---|
| Shared collision core | `game/js/collision.js` | BodySDF (trilinear sample/gradient/project), sphere/capsule projection, PBD contact friction, spatial-hash self-collision, articulator coupling solver (face) |
| Core tests | `game/js/collision.test.mjs` | 11/11 pass (analytic fixtures: sphere field, capsule projection, friction, self-collision, articulator coupling ends penetration-free) |
| Hair wiring | `game/js/hair-spring.js` | `opts.collision` + `collisionSetFromData()`; posed colliders + SDF per substep, friction on contact; legacy colliders unchanged when no set is passed. Tests 7/7 pass |
| Cloth wiring | `game/js/fx/cloth.js` | Self-collision via the shared core available to the XPBD cloth |
| Baker | `tools/collision/bake-collision.mjs` | Skinned bind surface (morphs + LBS at bind) → fitted collider set + SDF grid; hard validation gates (below) |
| Megami data | `customization/collision/megami/` | Baked from `megami-angel-pilot2-v5.glb` (the current body; header `bakedFrom` verified) — see bake record. An earlier v4 bake exists in the lane scratch and must not ship: it carries the pre-fix Spine2→Neck capsule r=1.1729 (v5: r=0.2434) |

## The bake root cause (read this before baking another character)

Three predecessor sessions died on this bake. The failure chain, measured:

1. `new MeshBVH(geometry)` **rewrites the geometry's index buffer** by
   default; mapping `faceIndex` back through the source index array then
   reads the wrong triangle → sign garbage (1178/2000 = 59% mismatch on
   Megami). **Fix:** build with `{ indirect: true }`.
2. With lookups exact, the closest-triangle **normal test still
   disagrees with ray parity on ~6–9%** of near-surface samples — all in
   shell-contact zones. The surface is a union of shells; for a union,
   parity is the correct inside definition. **The sign is ray parity**
   (3-ray majority oracle; per-row parity sweep for grid cells).

Bake gates (hard — a failing bake does not ship): ground truth (bone-axis
points inside / clear points outside), row-sweep vs oracle agreement
≥ 99%, zero-level fidelity (surface points read ≈ 0 in the grid,
max ≤ 1.25 voxels).

## Runtime shape

- Colliders are fitted per character from the skinned bind pose
  (PhAT pattern): radii = measured percentiles of dominant-joint skin
  vertices. Margins add the simulated item's own radius at runtime.
- The SDF follows its frame bone by bind-inverse; colliders are posed
  from bone world positions each substep.
- Contact is inelastic with friction (`applyContactFriction`) — hair
  **rests and drags** on shoulders instead of skating or sinking.
- A character without baked data gets no collision set (fail-silent);
  the pre-existing head-sphere behaviour is unchanged.

## Phase B proof (Megami hair ↔ shoulders) — status 2026-11-09

The proof record lands with this PR under
`docs/proof/2026-11-09/megami-collision/` — read it before quoting any
number from it. Summary of what it establishes, honestly:

- **AFTER (core ON) measured:** zero penetration in every observed
  frame (6-frame settle probe + 135/160 frames of the full deterministic
  motion; the run's tail was lost to a renderer crash under load, and
  the BEFORE run has not yet been captured — browser launches were
  dying at page load on the proof box; no BEFORE number exists and none
  is estimated).
- **But the zero is vacuous for the shoulder-contact case:** the
  simulated tips never come within ~68 mm of the body. The solver
  drives the part's 19 guide bones; the *visible* strands are 2,573
  independent cards that are not simulated (≈43% of strand verts are
  head-weighted static mass), and the guide chains hold their authored
  bind directions instead of draping. Hair-on-shoulders is therefore
  **not yet demonstrated** — the blocker is the hair presentation layer
  (strand-level sim, or card↔chain binding with fall-capable solver
  parameters), not the collision core, which is unit-proven.
- The proof record also flags the export-pipeline root cause the
  harness compensates for: both GLBs' skin sits ~0.19 below their own
  joint skeletons (offset in the IBMs).

## Phase C (tongue / lips / teeth / jaw)

The solver core (`solveArticulatorCoupling`) is landed and unit-proven
against an analytic mouth. The per-character face contact set (head-space
mouth SDF + region segmentation + drive mapping) is specced in the
physics-family face-contact spec; its bake waits on the GNM head landing
for Megami — the spec deliberately does not fake a proof on the current
head. Everything head-independent (solver, drive limits, region
contract) is in place.

## Licences

three-mesh-bvh MIT (vendored) · three.js MIT · XPBD cloth ported from
jspdown/cloth, MIT · solvers' algorithms from Macklin et al. 2016/2019
and Müller et al. 2007 · face coupling after JALI's published drive
separation · commercial systems (Magica Cloth 2, Unreal PhAT, Unity
Cloth, TressFX) are the documented production patterns mirrored — no
commercial code ships.
