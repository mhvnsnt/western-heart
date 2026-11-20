# CUSTOMIZATION-JSON-SCHEMA — the Creation Suite per-attire contract

**Status:** fixed contract, Creation Suite Pass (2026-10-20). The UI lane writes
these files, the bake lane (`customization/tools/apply_customization.py`) turns
them into real game GLBs, the proof lane reads them. Nobody changes the shape
without changing this doc in the same PR.

Pattern: the `dome-params.json` precedent (PR #356) — one editable JSON living
in the attire folder, next to the models it describes.

## Where it lives

```
roster/<fighter>/attires/<attire>/customization.json
```

One file per attire. Next to it: `base_glb` (input, never overwritten) and
`out_glb` (the baked result the game loads via the Creation Suite registry).

## The schema (version 1)

```json
{
  "version": 1,
  "app": "wh-creation-suite",
  "fighter": "baek",
  "attire": "master-white",
  "base_glb": "baek-master-white-rigged.glb",
  "out_glb": "model-custom.glb",

  "body": { "body_type": "Medium 1", "skin_tone": "#c98d5e" },

  "morphs": { "muscle": 0.4, "shoulders": 0.3, "eye_size": 0.25 },

  "parts": {
    "hair": {
      "part_id": "some-hair-part",
      "glb": "customization/parts/hair/<part>.glb",
      "placement": { "px": 0, "py": 0, "pz": 0, "rx": 0, "ry": 0, "rz": 0, "s": 1 }
    }
  },

  "textures": [
    { "part_id": "eye-yellow-tiger", "kind": "eye",
      "image": "customization/parts/baek-eyes/eye-yellow-tiger.png" },
    { "part_id": "chest-decal", "kind": "decal",
      "image": "customization/decal-library/<...>.png",
      "material": "<optional material name>", "rect": [0, 0, 128, 128] }
  ],

  "colors": { "hair": "#202020", "skin": "#c98d5e" }
}
```

### Fields

| Field | Meaning |
|---|---|
| `version` | Always `1`. |
| `app` | Always `"wh-creation-suite"`. |
| `fighter` / `attire` | Roster ids; `fighter` keys registry lookups (`character_mappings`, `parts/<fighter>-eyes/`). |
| `base_glb` | File name (in this folder) of the untouched base model. |
| `out_glb` | File name (in this folder) the bake writes. Default `model-custom.glb`. |
| `body.body_type` | Suite body-type label (informational; the morphs below are the bake truth). |
| `body.skin_tone` | Suite skin-tone swatch (informational; `colors.skin` is the bake instruction). |
| `morphs` | Suite morph id → MPFB slider value. Ids + ranges come from `packages/creation-suite/src/morphs.js` (`BODY_MORPHS` + `FACE_SHAPE_MORPHS`), mapped to MPFB targets by `customization/body-morphs/MANIFEST.json`. Range −1…1 (height 0…1). `0` / absent = neutral. |
| `parts` | Suite slot → mesh part. `part_id` resolves against `customization/PARTS-REGISTRY.json`; `glb` is a repo-relative path (or `null` to take the registry part's `asset`). `placement` = bone-local offset: `px,py,pz` metres, `rx,ry,rz` degrees, `s` uniform scale. |
| `textures` | Texture applications. `part_id` resolves against the registry; `image` is a repo-relative PNG (or the registry part's `asset` when omitted). `kind` ∈ `eye \| decal \| hair`. `material` optionally names the exact target material. `rect` = `[x, y, w, h]` composite region in the target texture's pixel space, **top-left origin**; omit it for the registry placement (registry mode `full_replace` replaces the whole texture, alpha-blended). **Note:** `kind: "eye"` here is a *legacy texture-variant* mechanism (swapping a saved eye-texture variant on models whose eyes are part of the face/eye texture — e.g. the Baek eye-texture options). It is **not** the eye system — see "Eyes are mesh parts" below. |
| `colors` | `hair` / `skin` hex tints. Applied to materials resolved by registry mapping or by a material name containing `hair`/`skin`, as a Principled base-color factor multiplied with the texture. If no material resolves, the bake **fails that item loudly** — it never guesses a material. |

## Eyes are mesh parts (owner verdict 2026-10-20 ~19:40 CDT)

Eyes are **real placeable parts, never texture-paint decals.** The owner
rejected a hand-painted texture eye on Deathfang ("let it be a real eye not
just a decal") and wants to place eyes himself in the Creation Suite.

- Eyeball, eyelash, and eyebrow are **mesh parts** carried in the `parts` map,
  attached at the **eye socket** (slot `eye`, aliases on the `Head` bone) with
  the standard `placement` `{px,py,pz,rx,ry,rz,s}` — the owner can move, rotate,
  and scale them in the suite, and the bake socket-attaches them like any
  other mesh part. No special eye code path exists in the bake.
- The named future test case for placeable eyes is the **DEATHFANG human**
  form: real eyeball + lashes + brows placed through the suite, replacing the
  provisional painted eye.
- The `textures` `kind: "eye"` mechanism stays only as a legacy texture-variant
  swap for models that ship with a saved eye-texture option library (the
  baek-eyes pattern). Production eye *design* changes go through mesh parts.

## Round 2 additions (2026-10-21 — owner orders: placement by hand, piece swaps)

Additive on version 1 — every round-1 file still parses and bakes.

### Placement is exact bone-local (semantics FIXED, not just documented)

`parts.<slot>.placement` is the part's transform **in the socket bone's
local frame**: at bake time the part's evaluated world geometry is
re-expressed in the part's *own* socket-bone frame (the alias bone on the
part's rig, else its dominant weighted bone; unskinned parts attach by
bounding-box centre), the placement is applied in that frame, and the
result is skinned rigidly (100% weight) to the base socket bone. So
`world = base_bone_world × T(placement) × part_bone_local_geometry`, and
placement `0/0/0 · 0° · s=1` is the part in its native registration on the
bone. Round 1's bake left the bone matrix inside the transform, so saved
numbers were world-compensations — that is why the baked Master White
hair floated off the head and the beard hung at the neck (owner grade:
40/100). (An earlier round-2 build bone-*parented* the parts instead;
the glTF exporter bakes a bone-parented object's world transform into
its geometry while keeping the node TRS, so importers double-transformed
them — skinning is the portable path.) The round-trip proof
(`customization/tools/proof/cs-round2-roundtrip.py`) bakes the same record
twice with a known placement delta and verifies the output GLB's part
geometry moves by exactly that delta.

- `sx` / `sy` / `sz` (optional): per-axis scale, overriding `s` per axis.
- `parts.<slot>.tint` (optional hex): multiplies the Principled base-color
  factor of the part's own materials at bake (materials cloned first — a
  tint never leaks into the base model or another part). This is how the
  CC0 hair/beard on Master White stop reading white-gray.
- Placement on a **skinned-merge** part (part rig == base rig) is ignored
  with a loud bake warning: skinning already carries its registration.
- The suite UI edits placement with sliders **and** tap nudge steppers
  (±0.01 m / ±1° / ±0.05 scale) — tap-first, never drag-and-drop.

### `hide_meshes` — bake-time base-mesh removal

Top-level list of substrings. Any base mesh whose object name, mesh name,
or material name contains a pattern (case-insensitive) is removed from the
**baked output only** (the base GLB is never touched). This is the
base-hair hide toggle: `["hair"]` for models whose hair is a named mesh.
A pattern that matches nothing fails loudly.

### `region_swaps` — Tekken-style piece swaps

```json
"region_swaps": [
  { "region": "head", "from_glb": "roster/baek/attires/attire1/model.glb",
    "from_fighter": "baek", "from_attire": "attire1",
    "yaw_deg": 0, "scale": null }
]
```

Regions: `head` · `torso` · `arm_l` · `arm_r` · `legs`. Bake semantics:

1. The region is **cut from the base**: every vert whose dominant skin
   bone is in the region goes (Tekken cuts at the bone, so do we).
2. The region is **cut from the source** the same way when the source is
   skinned. An **unskinned** source (Tripo statue) supports `head` via a
   spatial neck-pinch cut (narrowest cross-section in the upper body);
   other regions on unskinned sources fail loudly.
3. The piece is **fit** to the base: anchored at the region's neck point
   (bottom-band centroid of the base's removed region), scaled by
   base-region-height / source-region-height (`scale` overrides), yawed so
   the source's head-centroid forward estimate matches the base's
   (`yaw_deg` adds a manual correction).
4. The piece is **re-skinned onto the base rig**: skin weights transfer
   by canonical bone name (prefixes `mixamorig:`/`DEF-`/`Bip01` etc.
   normalize away) when the source is skinned; unskinned pieces get
   distance weights to the region's anchor bones (head: Head+Neck).
5. Meshopt-compressed / mesh-quantized sources (Tripo exports) are
   decoded through gltf-transform (`copy` + `dequantize`) automatically;
   without `npx` the item fails loudly with the manual command.
6. Swaps compose with everything else: morphs → hide → swaps → textures
   → parts → colors. A swapped-away face makes `eye` texture entries fail
   loudly rather than paint the wrong head.

Per-piece morphs: a swapped region carries no MPFB keys of its own; the
record's `morphs` still drive the base's keys. Per-attire save/restore is
the record itself — removing the `region_swaps` entry and re-baking
restores the base model exactly.

Swap sources are indexed in `customization/region-sources.json`
(regenerate: `customization/tools/build_region_sources.py`).

### Colors: a mapping may name a `materials` list

`character_mappings[<fighter>][<kind>]` keeps `material` (single, used by
the texture-part path) and may add `materials: [...]` — the bake's color
step tints **all** of them. Skin tone lives on many materials at once
(Baek: 11 pek1u materials, mapped from per-texture mean-color evidence).

## Bake semantics (`apply_customization.py`, in order)

1. **Morphs** — existing `MPFB_<id>` shape keys are driven to the saved values;
   absent keys are transferred + baked with the height-normalized KD-tree
   transfer from `customization/body-morphs/MANIFEST.json` targets (the
   `mpfb_wire_cj.py` method). MANIFEST target names are MPFB *logical* names:
   on disk each `…-decr-incr` / `-down-up` / `-in-out` name is a paired file
   set, often split `l-`/`r-` — the bake resolves logical → disk files and
   picks the side matching the value's sign. The mix is baked into the Basis:
   the exported GLB carries deformed geometry, no live keys.
2. **Textures** — target resolution order: explicit `material`/`texture` →
   `PARTS-REGISTRY character_mappings[fighter][kind]` → registry part
   `placement` → `customization/parts/<fighter>-eyes/MANIFEST.json`
   (`eye_texture`, the baek-eyes pattern) → eye-library mappings. Composite or
   full-replace, alpha-blended, re-packed into the GLB.
3. **Mesh parts** — a part whose armature bone names all exist on the base rig
   is re-bound to the base armature (skinning by bone name); any other part is
   bone-parented at the slot socket (aliases mirror
   `packages/creation-suite/src/attire.js` `SOCKETS`) with `placement` applied
   in bone-local space.
4. **Colors** — as above.

Round 2 inserts two steps: **(a2) `hide_meshes`** runs right after morphs,
and **(a3) `region_swaps`** right after that — both before textures, parts,
and colors (full order: morphs → hide → swaps → textures → parts → colors).

Missing inputs fail loudly per-item (report + exit 2); a missing `base_glb`
aborts (exit 1). Nothing is silently skipped.

## Game wiring

After every bake the tool regenerates `game/js/attire-customizations.js`:

```js
export const ATTIRE_CUSTOMIZATIONS = {
  'baek-master-white': '../roster/baek/attires/master-white/model-custom.glb',
};
```

Keys are the `MODEL_URLS` keys of each attire's `base_glb` in
`game/js/assets.js` (fallback `<fighter>-<attire>`); values are paths relative
to `game/`. `assets.js` imports the map and lets it override `MODEL_URLS`
entries before use — guarded, and an exact no-op when the map is empty.
`customization.example.json` files (fixtures) do **not** feed the registry;
only a real `customization.json` does.

## Worked example

`roster/baek/attires/master-white/customization.example.json` — the self-proof
fixture: muscle +0.4, shoulders +0.3, eye_size +0.25, and the eye swap to
`eye-yellow-tiger` via the `customization/parts/baek-eyes/` mapping (Baek's eye
texture is `pek1u_29`, material `mat_21-pek1u_29.jpg`, full-replace 128×128).
Baked output: `model-custom.glb` in the same folder; before/after renders in
`customization/tools/proof/cs-bake-baek/`.

## Rig & Pose (`rig`) — additive section, Rig & Pose Studio (2026-10-21)

Owner order 2026-10-21 ~11:59 CDT: the owner gets FULL manual rig/pose
control in the Creation Suite — every bone, add/remove, per-bone
orientation/position/scale, weights, joints, mesh/part visibility, posing —
saved through THIS file. The `rig` section is optional and additive: its
absence is an exact no-op, and no existing field changes shape.

```json
"rig": {
  "bones": {
    "<bone name>": {
      "offset":  { "pos": [0,0,0], "rot_deg": [0,0,0], "scale": [1,1,1] },
      "visible": true
    }
  },
  "add_bones":    [ { "name": "...", "parent": "<bone name>",
                      "head": [0,0,0], "tail": [0,0,0] } ],
  "remove_bones": [ "<bone name>" ],
  "weights":      [ { "bone": "...", "center": [0,0,0], "radius": 0.1,
                      "strength": 1.0, "mode": "add" } ],
  "visibility":   { "<mesh or node name>": false },
  "pose":         { "<bone name>": { "rot_deg": [0,0,0], "pos": [0,0,0] } }
}
```

| Field | Meaning |
|---|---|
| `frame` | Model-frame correction applied to every scene-root node before all other rig ops: `translate` metres, `rot_deg` euler degrees. This is the intake frame fix as an owner control — e.g. a hip-origin model (feet at y = −1.05, like shipped Star) grounded to floor-origin with one saved value, instead of a silent exporter default. |
| `bones.<name>.offset` | Rest-pose edit for one bone: `pos` metres (local), `rot_deg` = `[pitch (X), yaw (Y), roll (Z)]` degrees, `scale` per-axis. Applied in bone-local space. This is the control that repairs a drifted rest frame (see the STEP 1 diagnosis: shipped Star's core rests sit at 90–180°). |
| `bones.<name>.visible` | Editor-only: bone shown/hidden in the suite viewport. No bake effect. |
| `add_bones` | New bones parented to an existing bone; `head` is parent-local; `tail` records the bone's aim for the editor (the bake stores head + orientation; tail is editor data). Added bones join every skin their parent belongs to, with zero weights until painted. |
| `remove_bones` | Bones deleted from the skins. Vertices bound to a removed bone fall back to its nearest kept ancestor joint; weights renormalize. The node itself stays in the tree (unskinned) so child bones keep their world frame — removal is a SKIN operation, stated plainly so nobody expects geometry to vanish. |
| `weights` | Weight-paint brush strokes, replayed by the bake in array order: a world-space sphere (`center`, `radius`, quadratic falloff) adds (`mode: "add"`) or blends toward (`mode: "set"`) the named bone's weight, capped at 4 influences, renormalized. Deterministic: same strokes → same weights → identical file. |
| `visibility` | Mesh/node name → shown in the baked scene. `false` removes the node from scene roots/children (geometry stays in the file; the game never draws it). This is the control for the "invisible parts" class: parts hidden by stored-blend flags are surfaced and toggled HERE, in the open. |
| `pose` | A static pose baked INTO the rest pose (a stance): same offset math as `bones`, semantically "the fighter's zero-pose from now on." Recorded separately so a stance is distinguishable from a rig repair. |

### Bake stage

`customization/tools/rigpose_bake.py` applies the `rig` section as the
stage AFTER `apply_customization.py` (morphs → textures → parts → colors →
**rig**), reading the same `customization.json`. After any rest edit it
**recomputes every skin's inverseBindMatrices from the edited world rests**
— rest edits therefore change the skeleton's zero-pose without moving the
mesh in world space, which is precisely the semantics a rest-frame repair
needs. Round-trip contract: edit → save → reload → bake is deterministic;
the studio's test (`customization/tools/test_rigpose_bake.py`) bakes twice
from the same saved JSON and requires byte-identical output, and requires
a no-`rig` bake to leave skeleton and weights untouched.

