# ANATOMY LAYERS — Data Model Spec (2026-10-23)

**Status:** implemented. Pipeline: `tools/anatomy/generate_layers.py`.
Proof fighter: Pantera (`roster/pantera/anatomy/`).

## 1. What this is

Purdue's Dissectible Anatomy models bodies as separable anatomical layers
(see `docs/research/DISSECTIBLE-ANATOMY-2026-10-23.md`). For Western Heart we
want the same idea as a **creation-suite data model**: "deepest per-body-part
morphing" — real anatomical layers instead of surface sliders.

Each character gets **five separable volumetric layers**:

| Layer | Contents | Representation |
|---|---|---|
| **BONE** | Simplified bone volumes from the skeleton: skull, ribcage, pelvis, limb capsules, axial capsules | Union of analytic SDF primitives |
| **MUSCLE** | Muscle-group volumes (pectoralis, abdominals, biceps, quadriceps, …) attached to bones | Union of analytic SDF primitives, one group per muscle with a bulk morph param |
| **ORGAN** | Visceral organs for X-ray sequences: heart, lungs, liver, stomach, intestines | Union of analytic SDF primitives positioned from the rig skeleton (chest/spine/hips); one group per organ with a bulk morph param |
| **FAT** | Offset shell: per-region subcutaneous thickness | Scalar thickness per body region + global |
| **SKIN** | The existing render mesh | Reference (never copied) + MPFB morph-target hooks |

### Why analytic SDF primitives

Each volumetric layer is a **union of analytic SDF primitives**
(`capsule` | `ellipsoid` | `sphere`) stored as plain JSON. This is the
shippable choice:

- **Tiny**: a full character's layers are ~50 KB of JSON (vs MBs for voxel
  grids or tet meshes).
- **Closed-form**: exact SDF evaluation at any point — no meshing needed for
  morph math, sampling, or validation.
- **Trivially morphable**: a bulk dial scales a radius; no re-voxelization.
- **Sampling-ready**: can be baked to voxel grids, marching-cubes meshes, or
  McGraw-style per-splat SDFs later without changing the data model.

No cryosection data is used. Volumes are **procedural from the skeleton +
body-part regions measured from the mesh** — the game-art version of McGraw's
"design the 3D texture representing alien or monster anatomy" suggestion.

## 2. JSON schema (`wh.anatomy-layers/2`)

Canonical location: `roster/<fighter>/anatomy/anatomy-layers.json`.

**Version history.** `wh.anatomy-layers/1` (2026-10-23, PR #860): bone,
muscle, fat, skin. `wh.anatomy-layers/2` (2026-10-23): adds the ORGAN layer.
The change is **additive** — v2 documents carry a `layers.organ` key that v1
readers ignore; all v1 keys keep their shape and semantics.

```json
{
  "$schema": "wh.anatomy-layers/2",
  "schema_version": "wh.anatomy-layers/2",
  "fighter": "pantera",
  "generated": "2026-10-23",
  "generator": "tools/anatomy/generate_layers.py",
  "units": "meters",
  "source": {
    "glb": "roster/pantera/pantera_rigged.glb",
    "mesh": 0, "skin": 0,
    "joints": 13, "vertices": 10548,
    "mesh_rectification_y_deg": 90,
    "mesh_rectification_note": "mesh verts rotated about Y by this angle into skeleton space; 0 = already aligned",
    "rig_front": [0.0, 0.0, -1.0],
    "rig_front_note": "rig facing from bilateral naming; muscle 'front' offsets use this direction"
  },
  "skeleton": {
    "hips":   { "pos": [0.0, 0.929, 0.0], "parent": null },
    "spine":  { "pos": [0.0, 1.108, 0.0], "parent": "hips" }
  },
  "layers": {
    "bone": { "primitives": [
      { "id": "bone_skull", "kind": "ellipsoid",
        "center": [0.0, 1.70, 0.01], "radii": [0.075, 0.095, 0.085],
        "joint": "head", "morph": "bone_scale_skull" },
      { "id": "bone_thigh.L", "kind": "capsule",
        "a": [-0.275, 0.893, 0.0], "b": [-0.275, 0.500, 0.0], "r": 0.035,
        "joint": "thigh.L", "morph": "bone_scale_limbs" }
    ]},
    "muscle": { "groups": [
      { "id": "biceps.L", "label": "Biceps", "side": "L",
        "primitives": [ { "kind": "capsule",
          "a": [-0.31, 1.42, -0.02], "b": [-0.44, 1.42, -0.02], "r": 0.052 } ],
        "bulk_param": "muscle_biceps_L",
        "base_radius": 0.052 }
    ]},
    "organ": { "groups": [
      { "id": "heart", "label": "Heart", "side": "L",
        "primitives": [ { "kind": "ellipsoid",
          "center": [-0.041, 1.292, -0.014],
          "radii": [0.045, 0.058, 0.048] } ],
        "bulk_param": "organ_heart",
        "base_radius": 0.050 },
      { "id": "intestines.1", "label": "Intestines", "side": "C",
        "primitives": [ { "kind": "capsule",
          "a": [0.0, 0.979, -0.014], "b": [0.0, 1.068, -0.014],
          "r": 0.041 } ],
        "bulk_param": "organ_intestines_1",
        "base_radius": 0.041 }
    ]},
    "fat": {
      "baseline_global": 0.010,
      "regions": {
        "torso": { "thickness": 0.012, "param": "fat_torso" },
        "arm.L": { "thickness": 0.008, "param": "fat_arm_L" }
      },
      "thickness_param": "fat_thickness"
    },
    "skin": {
      "mesh_ref": "roster/pantera/pantera_rigged.glb#mesh0",
      "morph_targets": ["MPFB_bulk", "MPFB_muscle", "MPFB_fat"]
    }
  },
  "morph_params": [
    { "id": "muscle_biceps_L", "layer": "muscle",
      "label": "Biceps bulk (L)", "range": [-1, 1], "default": 0.0,
      "effect": "group radius *= 1 + 0.55*v",
      "applies_to": ["biceps.L"], "suite_dial": "body.biceps_L" },
    { "id": "fat_torso", "layer": "fat",
      "label": "Fat: torso", "range": [-1, 1], "default": 0.0,
      "effect": "region thickness *= 1 + 0.8*v",
      "applies_to": ["torso"], "suite_dial": "body.fat_torso" },
    { "id": "bone_scale_limbs", "layer": "bone",
      "label": "Bone: limbs", "range": [-1, 1], "default": 0.0,
      "effect": "bone radii *= 1 + 0.25*v",
      "applies_to": ["bone_thigh.L", "..."], "suite_dial": "body.bone_scale_limbs" }
  ]
}
```

### Primitive kinds

- `capsule`: `{a: [x,y,z], b: [x,y,z], r}` — segment with radius (limbs, abs).
- `ellipsoid`: `{center: [x,y,z], radii: [rx,ry,rz]}` — skull, ribcage, pelvis,
  deltoids, pecs, glutes.
- `sphere`: `{center, r}` — available, unused in v1.

### The ORGAN layer (v2)

Seven organ groups for Pantera, ~7 primitives total (per-character counts
vary with the rig). Placement is GEOMETRIC-FIRST: derived from rig joint
positions, never hand-tooled, never from skin weights.

| Group id | Label | Anchor | Position rule |
|---|---|---|---|
| `heart` | Heart | chest joint | left mid-chest: anatomical-left × 0.30·tr + front × 0.10·tr − 0.35·tr in Y; ellipsoid ~fist-sized (0.045/0.058/0.048 m × body_scale) |
| `lung.L` / `lung.R` | Lung | chest joint | one per side: ±anatomical-left × 0.40·tr, +0.12·tr in Y; ellipsoids filling the ribcage (nested inside `bone_ribcage`) |
| `liver` | Liver | spine→chest 32% | right abdomen: −anatomical-left × 0.30·tr + front × 0.08·tr, tucked under the ribcage |
| `stomach` | Stomach | spine→chest 55% | left abdomen: +anatomical-left × 0.22·tr + front × 0.14·tr |
| `intestines.1` / `intestines.2` | Intestines | hips→spine | simplified capsule cluster in the lower abdomen (vertical + transverse capsules) |

`tr` = torso radius (½ shoulder half-width from the skeleton), `body_scale` =
height/1.75. Anatomical left is derived from the `.L` joints' x-sign
(`_anatomical_left`), falling back to left = up × front. All radii are
hard-clamped to ≤ 0.70·tr so organs stay nested inside the torso.

**Purpose.** X-ray sequences (the user's "really good like organs" ask):
the ORGAN layer renders through the body via the same SDF union the bone
layer uses — a separate, locked layer that never plays during fights
(same separation rule as show animations: X-ray views are intros/cutscenes
only). Per-organ bulk params (`organ_heart`, …) give the PBD/soft-body crew
per-organ scale dials (e.g. heartbeat pulsation) without touching the
fight moveset.

### Morph parameter semantics

| Param pattern | Layer | Effect |
|---|---|---|
| `muscle_<group>` | muscle | group primitive radii `*= 1 + 0.55*v`, v∈[-1,1] |
| `organ_<group>` | organ | group primitive radii `*= 1 + 0.25*v`, v∈[-1,1] |
| `fat_<region>`, `fat_thickness` | fat | thickness `*= 1 + 0.8*v` (regional × global) |
| `bone_scale_<region>` | bone | primitive radii `*= 1 + 0.25*v` |

`applies_to` lists the affected group/primitive ids. `suite_dial` is the
creation-suite dial path the morphing UI crew builds on.

### Skin riding (bake semantics)

Anatomy morphs reach the render mesh via `bake_displacement`: for each skin
vertex, displacement along its normal =
`(muscle_SDF_base − muscle_SDF_morphed) + (fat_morphed − fat_base)`.
The skin rides the muscle surface; fat thickens/thins the shell. This bakes to
a per-vertex delta array — the same primitive the Daz-style dial system uses
(see `docs/research/DEEP-MORPHING-DIALS-V2-2026-10-23.md` §1.1), so anatomy
dials compose additively with MPFB shape keys.

## 3. Procedural generation pipeline

`tools/anatomy/generate_layers.py` (stdlib + numpy + pygltflib, no Blender):

1. **Load**: parse GLB (JSON + BIN), read accessors; joint bind positions from
   inverse bind matrices (`inv(IBM)` — exact, no hierarchy walk); mesh
   positions, triangles, dominant skin joint per vertex.
2. **Rectify**: Y-rotate the mesh into the skeleton's frame. Picks the rotation
   maximizing L/R mirror symmetry, then snaps the mesh's face direction
   (snout = head's dominant protrusion) to the rig's front (from `.L`/`.R`
   naming). Recorded in `source.mesh_rectification_y_deg`.
3. **Frames**: limb axes/lengths/radii measured from skin chunks —
   arms via farthest-point fit (robust to missing elbow joints and torso-blend
   verts), legs via joint axes + chunk radii. Torso radius = ½ shoulder
   half-width (skeleton heuristic, robust to contaminated chunks).
4. **BONE**: capsules along limb frames + axial joint segments; skull,
   ribcage, pelvis ellipsoids nested inside the torso surface.
5. **MUSCLE**: 25 groups (trapezius, neck, deltoids, biceps, triceps, forearms,
   pectorals, lats, abdominals, obliques, glutes, quads, hamstrings, calves —
   bilateral where the rig is). Radii are anatomically proportioned
   (× body_scale = height/1.75) and hard-clamped inside the measured mesh
   surface. Front/back offsets follow the rig's facing.
6. **FAT**: per-region thickness baselines (physiological defaults ×
   body_scale).
7. **SKIN**: reference to the source mesh + MPFB hooks.
8. **ORGAN** (v2): heart, lungs, liver, stomach, intestines — SDF primitives
   positioned from the rig skeleton (chest/spine/hips) geometrically; radii
   anatomically proportioned to torso_radius × body_scale, clamped inside the
   torso.
9. **Validate**: every joint center must be inside the bone layer (SDF < 0);
   every organ primitive center must be inside the body — wrapped in muscle
   or cradled by bone (min of the two SDFs < 0.02); report counts.
10. **Proof** (`--render-proof`): sphere-traced front-view renders of all five
   layers + a morph comparison (biceps 0→1) + numeric proof JSON.

## 4. Suite wiring

- `customization/body-morphs/MANIFEST.json`: `anatomy_layers` section —
  the layer model, the bake path, and how anatomy dials relate to MPFB dials.
- `packages/creation-suite/src/morphs.js`: `ANATOMY_LAYER_MORPHS` export —
  the dial registry (id, label, layer, range, default, effect, suite_dial)
  the morphing UI crew consumes. Anatomy dials compose additively with
  `BODY_MORPHS` (Daz-style: `final = base + Σ dial·delta`).

## 5. Proof (Pantera, 2026-10-23)

`roster/pantera/anatomy/`: `anatomy-layers.json`, `proof.json`, `PROOF.md`,
`renders/` (5 layer renders + biceps 0→1 comparison).

- 13 joints, 10,548 verts; rectification 90° (mesh z-symmetric → x-symmetric,
  snout → rig front −Z); 12 bone primitives, 25 muscle groups, 7 organ groups
  (heart, lung.L, lung.R, liver, stomach, intestines.1, intestines.2),
  44 morph params.
- Biceps bulk 0→1: capsule radius 0.053→0.082 m (+55%), volume +189%.
- Baked skin displacement: max 0.027 m (= radius delta — the skin rides the
  muscle), localized to the arm.
- Validation: 13/13 joints inside the bone layer; 7/7 organ primitive centers
  inside the body (wrapped in muscle or cradled by bone).
- Schema `wh.anatomy-layers/2`; v1 readers ignore the additive `organ` key.

## 6. Non-goals / boundaries

- The morphing UI itself (another crew).
- Cutting/destruction wiring into the game (the PBD crew owns simulation;
  these SDFs are the data they can sample).
- Fight code (untouched).
- Per-fighter artistic tuning: v1 is procedural; the suite exposes overrides
  per fighter later.

## 7. References

- `docs/research/DISSECTIBLE-ANATOMY-2026-10-23.md` — Purdue/McGraw research.
- `docs/research/DEEP-MORPHING-DIALS-V2-2026-10-23.md` — dial architecture.
- `customization/DEEP-BODY-MORPHING-RESEARCH.md` — body-morph background.
