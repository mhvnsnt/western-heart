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
| `textures` | Texture applications. `part_id` resolves against the registry; `image` is a repo-relative PNG (or the registry part's `asset` when omitted). `kind` ∈ `eye \| decal \| hair`. `material` optionally names the exact target material. `rect` = `[x, y, w, h]` composite region in the target texture's pixel space, **top-left origin**; omit it for the registry placement (registry mode `full_replace` replaces the whole texture, alpha-blended). |
| `colors` | `hair` / `skin` hex tints. Applied to materials resolved by registry mapping or by a material name containing `hair`/`skin`, as a Principled base-color factor multiplied with the texture. If no material resolves, the bake **fails that item loudly** — it never guesses a material. |

## Bake semantics (`apply_customization.py`, in order)

1. **Morphs** — existing `MPFB_<id>` shape keys are driven to the saved values;
   absent keys are transferred + baked with the height-normalized KD-tree
   transfer from `customization/body-morphs/MANIFEST.json` targets (the
   `mpfb_wire_cj.py` method). The mix is baked into the Basis: the exported GLB
   carries deformed geometry, no live keys.
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
