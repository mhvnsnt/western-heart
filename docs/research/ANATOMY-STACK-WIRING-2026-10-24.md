# Anatomy Stack Wiring Spec — 2026-10-24

**Companion to** `EP1-STACK-RESEARCH-2026-10-24.md` (verdicts + sources).
This spec is the wiring: concrete steps that turn the evaluated pieces into
game systems, each with its license gate. Nothing here changes runtime
behavior by itself — it specifies the next implementation PRs and ships one
enforceable gate now (`tools/anatomy/stack_layers.json` +
`tools/anatomy/validate_stack_layers.py`).

**Standing constraints honored.** License firewall: copyleft code stays in
`tools/`, never in `game/` runtime; CC BY-SA datasets are study-only for
game assets; SKEL/SMPL assets are never shipped; all characters are adults;
no in-universe writing in this technical spec.

## 1. The gate that ships in this PR

`tools/anatomy/stack_layers.json` is the single allow/block list for anatomy
data. Rules it encodes:

- **ALLOW (shippable with attribution):** BodyParts3D 4.0 (CC BY 4.0),
  HuBMAP HRA 3D reference organs (CC BY 4.0). Every mesh reference must
  carry `dataset`, `dataset_version`, `license`, and the exact attribution
  string, matching schema v3 (`ANATOMY-DATASETS-2026-10-23.md` §4).
- **BLOCK (study-only, never bundled):** Z-Anatomy (CC BY-SA 4.0), SKEL /
  BSM / BioAmass (MPG research-only), SMPL family (MPG research-only),
  LearnAnatomy3D merged geometry (contains CC BY-SA material, no public
  license), and any mesh whose own header still says CC BY-SA 2.1 JP
  (the legacy BodyParts3D header — flagged even though the current 4.0
  database license supersedes it; a human resolves the flag per file).
- **CODE allow-list:** Somakine MIT code (keep notice), Purdue
  DestructibleVoxelSystem MIT code (keep notice). **CODE block-list for
  `game/`:** Flamenco GPLv3+ code (tool-only), any copyleft code at all.

`validate_stack_layers.py` enforces the map's own consistency (every
allow-list entry has license + attribution; every block-list entry has a
reason; no dataset appears on both lists; every Somakine→WH layer mapping
points at a real WH layer). Run it before any mesh-reference PR lands:
`python3 tools/anatomy/validate_stack_layers.py`. It validates the MAP, not
the repo's meshes — a future PR extends it to walk
`roster/*/anatomy/anatomy-layers.json` and reject unlisted datasets. That
extension is specified in §6, not claimed here.

## 2. Purdue splat/SDF layer → future X-ray interior rendering (methods-only)

Current state (do not redo): WH layers are analytic SDF primitives
(`wh.anatomy-layers/2`); X-ray renders proxies from them on KO blows.
Purdue's layer, if ever built, upgrades only the RENDERING of those layers:

1. Keep the data model: primitives + groups + morph params stay the source
   of truth. The splat/SDF layer is a bake target, exactly as the layers
   spec already anticipates ("can be baked to voxel grids, marching-cubes
   meshes, or McGraw-style per-splat SDFs later without changing the data
   model").
2. Bake step (tools/, MIT PBD code allowed): voxelize each layer group,
   place PBD particles on a coarse grid, splats at 4× carrying the layer's
   color, per-splat SDF updated per frame, SDF boolean ops for the cut.
   Only the outer shell of splats draws.
3. Game-side rule: this is for X-ray / dissection views and finisher VFX
   at small-to-medium scale (McGraw's own suggested scope) — not for
   whole-body real-time soft-body simulation of every fighter every frame.
   Mobile GPU budget decides whether it ships; the analytic proxies are
   always the fallback.
4. Never needed for Ep 1's 6+ minute target: the show's anatomy shots can
   use the existing proxy layers. Do not let this R&D block the episode.

## 3. Human Atlas datasets → schema v3 mesh references (next layer)

Follow the already-specified schema v3 path
(`ANATOMY-DATASETS-2026-10-23.md` §4), with this PR's gate added in front:

1. Pick the mesh: HRA organs first where BodyParts3D is thin (female
   anatomy; BodyParts3D is male-only), BodyParts3D 4.0 otherwise. Never
   Z-Anatomy, even when it looks like the convenient version of the same
   part — convenience does not change its license.
2. Download from the current archive only (BodyParts3D 4.0
   `isa_BP3D_4.0_obj_99.zip` per Human Atlas ATTRIBUTION.md, or the HRA
   reference-organ release in use). Record source URL, version, and
   adaptation steps (units mm/Z-up → m/Y-up, meshoptimizer-style
   simplification bound, normal quantization) in the mesh's manifest, the
   way Human Atlas and Somakine both do — provenance is part of the asset,
   not a comment.
3. Add the v3 `meshes[]` entry (dataset, version, license, attribution,
   joint) to the fighter's `anatomy-layers.json`. X-ray's `_anatomyMesh()`
   loads it when present, falls back to `_proxyMesh()` when absent —
   behavior unchanged for fighters with no meshes.
4. Run the (extended) validator before the PR: every referenced dataset
   must be on the allow-list, every attribution string must match the map
   exactly, and no blocked dataset may appear anywhere in the file.
5. Attribution surfaces (already specified, restated so they are not
   dropped): project `docs/ATTRIBUTION.md`, the per-mesh `attribution`
   field, and the in-game credits screen.

## 4. Somakine → creation-suite / X-ray layer vocabulary + viewer techniques

Layer mapping (canonical IDs are Somakine's concept; WH layers are the
target — full map in `stack_layers.json`):

| Somakine layer | WH layer | Treatment |
|---|---|---|
| bone | bone | Direct. Bone primitives + joint metadata. |
| muscle | muscle | Direct. Muscle groups with bulk params. |
| joint | bone (joint metadata) | Joints are not a WH volume layer; store as joint records on bone primitives (center, axis, range) so the SKEL checklist (§5 of the research doc) has something to check against. |
| ligament | muscle (attachment) | Ligaments attach muscle to bone; model as thin muscle-group attachments, not a separate volume. |
| tendon | muscle (attachment) | Same as ligament. |
| skin (viewer surface) | skin | Reference only, never copied — same rule as the existing spec. |

Viewer techniques to port (our own code, MIT-licensed pattern, not a
copy-paste of Somakine's viewer):

- **Demand-driven loading + bounded concurrency:** X-ray/creation-suite
  anatomy loads only the visible layers, N concurrent fetches max. This
  is the mobile-load fix before any mesh layer ships.
- **Occlusion-aware picking:** tapping selects the front-most visible
  structure; structures behind the skin shell are not pickable until their
  layer is isolated. (Somakine viewer: occlusion-aware picking.)
- **Exploded layouts:** the spaced-inventory view from Human Atlas /
  Somakine's explode module, applied to creation-suite layer inspection:
  bone / muscle / organ groups separate along one axis for inspection,
  then reassemble. No new data needed — it is a transform of existing
  layer groups.
- **Data-pack provenance contracts:** every anatomy pack carries source,
  license, attribution, digest, and geometry budget, validated before
  load — the Somakine data-pack pattern, implemented as the validator in
  §1 extended to packs.

## 5. LearnAnatomy3D techniques → X-ray rendering (reimplementation, no assets)

Each technique is implemented from the author's published description, in
our own code, with no LearnAnatomy3D geometry or code:

1. **Part-index data texture:** one merged mesh per system + material;
   each vertex carries a part index; a small data texture maps
   part-index → visibility/highlight/color. KO-blow highlighting then
   costs a texture update, not a re-merge. This replaces per-part draw
   calls in X-ray sequences (the same batching Human Atlas uses).
2. **Persistent clipping plane:** one clipping plane per material, parked
   far away when the cut view is off, so toggling cross-section never
   recompiles shaders. The cut view is a camera + plane state, not a
   geometry operation.
3. **Stencil body-volume mask:** inner anatomy renders only inside the
   skin shell's stencil mask, so organs never visibly float outside the
   body when the skin is hidden. This is the legibility fix for X-ray
   close-ups.
4. **Two-pass streaming:** body surface first (fight can start / view can
   open), full anatomy second, `compileAsync()` before joining the scene,
   shader-error checks off in production builds. Creation-suite load
   ordering follows the same two passes.
5. **Fitting pattern:** atlas anatomy fitted onto fighter bodies with
   TPS-warp-style tooling in Blender/Node (our own tooling, per fighter)
   — never by importing LearnAnatomy3D's fitted bodies, which blend
   CC BY-SA material.

## 6. Validator extension (specified, not yet built)

A follow-up PR extends `validate_stack_layers.py` with a `--check-roster`
mode that walks `roster/*/anatomy/anatomy-layers.json`, and fails on:
(a) any `meshes[]` entry whose dataset is not on the allow-list;
(b) any attribution string that does not match the map exactly;
(c) any blocked-dataset name appearing anywhere in the file;
(d) any mesh entry missing `dataset`, `dataset_version`, `license`, or
`attribution`. Until that lands, the same checks are done by hand on every
mesh-reference PR and recorded in the PR body.

## 7. Flamenco — pointer only (render track owns it)

No game wiring. The show-facing doc in cape-jones
(`EP1-STACK-SHOW-2026-10-24.md` + `EP1-FLAMENCO-JOB.example.json`) gives the
job shape the render track can pick up: one job per shot, frame-range
chunks, shared storage, baked simulations, identical Blender/add-on
versions. This track makes no throughput claim and ran no farm.
