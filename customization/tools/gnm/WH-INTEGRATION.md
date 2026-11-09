# GNM × Western Heart — Integration Guide

How Google's GNM Head model plugs into the customization suite's BODY tab
(`customization/UNIFIED-UI-SPEC.md` §5.1).

## Pipeline

```
  one-time (offline, Python)
  ─────────────────────────
  wh_gnm_wireup.py fetch-weights            # gnm_head.npz -> ~/.cache/wh-gnm/
  wh_gnm_wireup.py export-glb \
      --seed 7 \
      --out  game/assets/heads/base_head.glb \
      --manifest-out game/assets/heads/sliders.json
                    │
                    ▼
  runtime (web build, Three.js)
  ─────────────────────────────
  GLTFLoader -> head mesh with morph targets
  BODY-tab sliders -> mesh.morphTargetInfluences[i]  (live re-morph)
```

## Offline steps

```bash
cd customization/tools/gnm
# 1. weights (PUBLIC HF repo google/gnm-v3, Apache-2.0 — no token needed;
#    the download is hard-verified against the published size + SHA-256)
python3 wh_gnm_wireup.py fetch-weights

# 2. inspect the named slider dimensions the UI binds to
python3 wh_gnm_wireup.py --weights ~/.cache/wh-gnm/v3_0/gnm_head.npz list-sliders

# 3. bake the preview head: base mesh + every expression as a morph target
python3 wh_gnm_wireup.py --weights ~/.cache/wh-gnm/v3_0/gnm_head.npz export-glb \
    --seed 7 \
    --out ../../../game/assets/heads/base_head.glb \
    --manifest-out ../../../game/assets/heads/sliders.json
```

`sliders.json` maps each named dimension to its UI slider
(§5.1 BODY → Head Shape / Face): identity dims get range [-3, 3],
expression dims get range [0, 1].

## Runtime (Three.js) — the live re-morph

Spec requirement (§5.1 functional behavior): *"Changing Body Type
re-morphs the preview instantly … Sliders move live; the fighter never
leaves the screen."* The exported GLB carries morph targets, so the
BODY tab needs no Python at runtime:

```js
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

const gltf = await new GLTFLoader().loadAsync('assets/heads/base_head.glb');
const head = gltf.scene.children[0];
// three.js builds morphTargetDictionary from primitive.extras.targetNames,
// which wh_gnm_wireup.py writes.
const dict = head.morphTargetDictionary; // { happy: 0, surprise: 1, ... }

// BODY tab slider handler (expression morphs):
function onFaceSlider(expressionName, value /* 0..1 */) {
  head.morphTargetInfluences[dict[expressionName]] = value;
}

// Head-shape presets (7M + 3F in the spec): bake each preset as an
// identity-parameter JSON via `wh_gnm_wireup.py sample --seed <n>` and
// re-export the GLB per preset, or blend identity params at authoring
// time. Fine identity sliders map 1:1 onto sliders.json identity_sliders.
```

## UI mapping (§5.1)

| Spec control | GNM source | Mechanism |
|---|---|---|
| Head Shape — 7M + 3F presets | identity basis, baked per preset | preset = identity param JSON; preview swaps base GLB |
| Head Shape — fine sliders | identity basis, named dims | authoring-time morph (re-export), or per-dim GLB set |
| Face — expression sliders | expression basis (named blendshapes) | **live**: `morphTargetInfluences` per slider |
| Face — "Randomize" | `sample_identity()` / semantic `IdentitySampler` | new seed → re-export or server-side bake |

## Likeness-locked roster heads

`gnm/fitting_utils/` (upstream) reconstructs GNM identity parameters from
2D landmarks of a face image. Pipeline for roster-faithful heads:

1. Owner key-art face scan → `fitting_utils` → identity params.
2. `wh_gnm_wireup.py export-glb --identity-json <fitted>.json` → head GLB.
3. Result: the character's locked likeness as a parametric base that still
   takes expression morphs live.

## Known limits

- **Head only.** Google has released GNM Head (v3.0) only; the full-body
  model is roadmap, not shipped. Body sliders (Height/Weight/Muscle/…)
  stay on the WMXIX parametric sliders + No Mercy body morphs.
- **Weights are public** (HF `google/gnm-v3`, Apache-2.0, `gated: false`).
  An earlier version of this doc wrongly named a gated `google/gnm-3`
  repo; that repo does not exist. Corrected 2026-11-08, and the first
  REAL-weights run is now done: `fetch-weights` downloaded
  `v3_0/gnm_head.npz` (53,328,601 B) and the wire-up's hard gate
  verified SHA-256
  `61d78bbfb4ad8e0b38495804a4caef3214d3df00f8c3f68761e63b41ce3747eb`
  (the published HF LFS oid). `list-sliders` on the real file: 17,821
  verts, 253 identity dims, 383 expression dims. `export-glb` baked a
  proof GLB with all 383 expression morph targets. (The synthetic
  round-trip from the original build is superseded by this run.)
- Live preview uses the linear shape model only (identity + expression).
  Joint posing / pose correctives live in upstream `gnm_numpy` for
  offline baking.
