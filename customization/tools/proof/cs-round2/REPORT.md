# Creation Suite Round 2 — Proof Report (2026-10-21/22)

Branch: `feat/creation-suite-round2-20261021` (repo mhvnsnt/western-heart).

## 1. In-suite part placement (owner order 1)

**Mechanism — PROVEN EXACT.** Placement in `customization.json` is a true
bone-local transform: the bake re-expresses a part's evaluated world
geometry in the part's own socket-bone frame, applies the placement in
that frame, and skins the result to the base rig — so
`world = base_bone_world × T(placement) × part_bone_local_geometry`.
Axis probes on Master White (bake the same record twice, one axis changed):

| probe | world delta measured | expected |
|---|---|---|
| hair pz +0.04 | 0.0400 along bone Z | 0.04 |
| beard px +0.05 | 0.0500 along bone X | 0.05 |
| brows py +0.03 | 0.0300 along bone Y | 0.03 |

**Two representation traps found and fixed on the way:**
- Bone-*parented* part objects measure perfectly in the GLB yet render
  displaced — the glTF exporter bakes their world transform into the
  geometry while keeping the node TRS, so importers double-transform
  them. Parts are now plain skinned meshes (the one path Blender,
  three.js and the game all evaluate identically).
- A flat 100%-socket-bone weight shears against any surface that blends
  several bones (Head/Neck/Spine — T7 binds carry a turned head/neck).
  Parts now copy the base's own skin field (nearest-base-vertex weight
  sets), so they deform *with* the surface in bind and in animation.

**Headline case — Master White hair + beard (was 40/100).** The shipped
record (`roster/baek/attires/master-white/customization.json`) now carries
measured bone-local placements (hair pitched −6° and seated on the skull,
beard on the chin, brows on the ridge), a `#2a1c10` per-part tint (the
tint now multiplies a clone of the part's base-color texture — a factor
multiply under a texture was a silent no-op), base-hair materials hidden
(`hide_meshes`: pek1u_14/15/13) so the placed cap replaces his hair, and
the Baek PARTS-REGISTRY mapping (skin 11 materials / hair 3 / eye) so
skin tone finally applies (round 1 loud-failed on the missing mapping).
Renders: `mw-final6_face.png`, `mw-final6_side.png` — dark hair ON the
head, dark beard ON the chin (round 1: white shells, beard at the neck).

**Suite controls:** placement sliders + per-axis scale + tap-first nudge
steppers (±0.01 m / ±1°) + reset, per-attire save/restore through
`customization.json`. Round-trip covered by `round2.test.js` (3/3).

## 2. Piece swaps (owner order 2)

Engine (`region_swaps` in the bake): canonical-bone region classification
(head / torso / arm_l / arm_r / legs), dominant-bone cut on skinned
sources and targets, canonical-name weight remap onto the target rig,
meshopt/quantized sources decoded automatically (gltf-transform),
unskinned sources cut spatially at the neck pinch (head) and re-skinned
with distance weights to the region anchors, fit by neck anchor + region
height scale + yaw (estimate, `yaw_deg` override in the record).

**Headline proof:** Kevin's head (`roster/baek/attires/attire1`) onto
Master White — `kevin-head-swap2_face.png`: Kevin's bearded head, textured,
facing forward on Master White's gi, seated at the neck (a visible
skin-tone seam at the jaw/neck junction is the expected un-blended graft
edge). The automatic yaw estimate landed −34°; the record pins
`yaw_deg: -90` (Tripo raw heads face +X), for −124° total. Second swap
attempted: DEATHFANG torso onto Master White (record
`../cs-round2-swap/customization-both.json`, render `swap-both_front.png`)
— the skinned-source path now runs end-to-end (a `base_bones` scoping
bug that killed it was found and fixed), but the graft renders SHREDDED:
DEATHFANG's bind is a hunched stance pose, and the fit anchors assume an
upright torso, so his torso lands scaled/rotated wrong and tears.
Skinned-source region swaps need bind-pose normalization with per-bone
frame alignment — named here as the next engine step, not papered over.
The unskinned-source head path (the headline case) is clean.

Suite: PIECES tab with region rows (SWAP / CHANGE / RESTORE), a source
picker fed by `customization/region-sources.json` (all 104 roster GLBs,
skinned/bone-count annotated), per-attire save/restore, hide-base-hair
toggle.

## 3. Tekken + WWE UI wiring (owner order 3)

Mapping documented in `customization/CREATION-SUITE-UI-WIRING.md`
(Tekken-style fighter/attire flow + WWE-style piece lists, tap-first —
never drag-and-drop).

## 4. Stretch items

- Base-hair hide toggle (suite) + `hide_meshes` (bake) — done.
- Bake part tinting incl. textured materials — done.
- Baek skin-tone registry mapping — done (see §1).
- Eyeball + eyelash mesh parts (`customization/parts/eyes/`, registered
  as `wh-eyeball-mesh` / `wh-eyelash-mesh`) — baked onto DEATHFANG human
  (the eye-as-part named test case): `df-eyes5_side.png` shows the mesh
  eyeball seated in his eye socket (white sclera + brown iris coinciding
  with the painted eye's almond, lash strip on top). His bind carries
  the Iori stance head twist the owner already rejected in the
  DEATHFANG lane; the eyes follow the Head frame exactly, and the suite
  placement controls are the owner's tool for final seating (his stated
  plan for the eye).

## Tests

packages/creation-suite: catalogs 6/6 · slotmap 4/4 (counts +2 for the
eye parts) · round2 3/3 · dna 4/4.

## Honest limits

- Placement *values* shipped for Master White are measured best-effort
  from profile/front renders; the suite exists so the owner can nudge
  them by eye — the bake now reproduces whatever is saved, exactly.
- Swap yaw for raw Tripo heads needs the record's `yaw_deg` (−90 for
  Kevin); the automatic estimate is documented as approximate in the
  schema.
- EEVEE renders of the T7 materials ghost semi-transparent from some
  angles (specular/ior); geometry placement was judged in profile,
  where the surface line is unambiguous.
