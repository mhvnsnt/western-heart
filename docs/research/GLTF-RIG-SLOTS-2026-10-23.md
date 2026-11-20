# glTF Rig Slot Manager + Physics Audit — 2026-10-23

Owner instruction (verbatim): "Pull all of this stuff in and wire it up and put it to work the best way possible"

Two workstreams in one doc: (1) gltf-transform verification + rig-slot pattern for the
creation-suite crew, (2) Rapier vs cannon-es audit with a keep/migrate/hybrid recommendation
and reconciliation of the false "Rapier is in use" claims on main.

---

## Part 1 — gltf-transform verification

### Installed vs latest (verified 2026-10-23)

| Package | Installed (`~/workspace/tools/gltf/package.json`) | Latest (npm) |
|---|---|---|
| `@gltf-transform/core` | 4.1.1 | **4.5.1** |
| `@gltf-transform/extensions` | 4.1.1 | **4.5.1** |
| `@gltf-transform/functions` | 4.1.1 | **4.5.1** |
| `meshoptimizer` (npm) | ^0.22.0 | **1.3.0** |

The toolchain is **4 minor versions behind**. Good news from the upstream CHANGELOG
(`donmccurdy/glTF-Transform`, v4.1 → v4.5): **no breaking API changes in the 4.x line** —
only additive features and fixes. The upgrade is a drop-in `npm install`.

What 4.2–4.5 adds that WH actually wants:

- **v4.2** — `unwrap()` / `unwrapPrimitives()` (xatlas/WASM UV unwrapping). Directly useful
  for the customization suite's texture-painting path (Fluid Painter lane).
- **v4.3** — `KHR_node_visibility` extension support. **This is the slot-toggling primitive:**
  hide/show hair/clothing layers via a real glTF extension instead of node removal.
- **v4.3** — `textureCompress` gains `chromaSubsampling` + `--mipmaps` flags (smaller phone payloads).
- **v4.3** — internal meshoptimizer bumped to v1.0.1 (better compression ratios).
- **v4.4** — `EXT_mesh_features` + `EXT_structural_metadata` (per-part metadata — e.g. tag
  slot meshes with `{slot:"hair", region:"head"}` in a queryable way).
- **v4.5** — `palette()` UV-preservation fix, KTX-Software v4.4.

### Upgrade path (does NOT break the rig-repair toolchain)

The existing consumer is the meshopt/quantization decode → Blender → re-encode path
(`tools/anim/gltf_codec.mjs` per `tools/TOOLS-INDEX.md`; pinned in the repo as
`@gltf-transform 4.1.1 · meshoptimizer 0.22.0`). Because the 4.x API surface is stable,
the upgrade is:

```bash
cd ~/workspace/tools/gltf
npm install @gltf-transform/core@^4.5.1 \
            @gltf-transform/extensions@^4.5.1 \
            @gltf-transform/functions@^4.5.1 \
            meshoptimizer@^1.3.0
```

Regression guard before the creation-suite crew adopts it:

1. Round-trip a known-good rigged GLB through the codec path (decode → re-encode).
2. Diff joint count/order, skin weights (`sortPrimitiveWeights` behavior unchanged), and
   morph-target count against the 4.1.1 output. Vertex counts via `getMeshVertexCount`.
3. Keep the old `node_modules` tree archived until the round-trip diff is clean.

Note: `~/workspace/tools/gltf/gltf_codec.mjs` is currently a 0-byte stub; the real codec
script is the repo's `tools/anim/gltf_codec.mjs` (not visible in sparse checkouts — see
caveat at the end of this doc).

---

## Part 2 — Rig slot manager pattern (gltf-transform-native)

Goal: **one master armature**; base skin, facial bones, hair layers, clothing meshes all
share it. Slots are separate glTF meshes bound to the *same* joint set, toggled at runtime.

### Authoring convention (non-negotiable, enforce in CI)

1. Every slot GLB uses **identical joint names and joint order**, same bind pose.
2. Slot identity lives in `extras`: `{ "wh.slot": "hair", "wh.region": "head" }`
   (upgrade to `EXT_structural_metadata` once on 4.4+).
3. Morph-target (shape key) names are stored in `mesh.extras.targetNames`
   (de-facto standard three.js `GLTFLoader` reads into `morphTargetDictionary`).

### gltf-transform pipeline (CLI)

```bash
# 1. Inspect / validate every slot GLB against the master rig
gltf-transform inspect base_body.glb
gltf-transform inspect hair_afro.glb

# 2. Merge all slots of one fighter into a single document
gltf-transform merge base_body.glb hair_*.glb top_*.glb --output fighter_slots.glb

# 3. Collapse duplicate skins/materials the merge introduced
gltf-transform dedup fighter_slots.glb fighter_slots.glb

# 4. Drop joints no slot actually uses; strip dead nodes
gltf-transform prune fighter_slots.glb fighter_slots.glb --keep-attributes

# 5. Split buffers per slot so the game can stream slots independently
gltf-transform partition fighter_slots.glb fighter_slots.glb --meshes

# 6. Ship it: quantize + meshopt
gltf-transform quantize fighter_slots.glb fighter_slots.glb
gltf-transform meshopt fighter_slots.glb fighter_final.glb --level 4
```

### Programmatic slot build (Node — function names verified against installed 4.1.1)

```js
import { NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS } from '@gltf-transform/extensions';
import {
  mergeDocuments, dedup, prune, partition,
  quantize, meshopt, resample, sortPrimitiveWeights,
  clearNodeTransform, getMeshVertexCount,
} from '@gltf-transform/functions';

const io = new NodeIO().registerExtensions(ALL_EXTENSIONS);
const master = await io.read('slots/base_body.glb');

// Merge each slot GLB into the master document, then dedup shared skins.
for (const slotFile of ['slots/hair_afro.glb', 'slots/top_jacket.glb']) {
  const slot = await io.read(slotFile);
  mergeDocuments(master, slot);          // skins with identical joints collapse…
}
await master.transform(
  dedup(),                               // …dedup() finishes the job
  sortPrimitiveWeights(),                // clean skinning weights per primitive
  prune({ keepAttributes: true }),       // drop unused joints / dead nodes
  resample(),                            // normalize any animation frame rates
  partition({ meshes: true }),           // one buffer per slot mesh
  quantize(),
  meshopt({ level: 4 }),
);
await io.write('out/fighter_slots.glb', master);
```

Slot tagging + morph-target naming for the UI slider path:

```js
import { Document } from '@gltf-transform/core';
const doc = new Document();
// …after merging, tag each mesh and name its morph targets:
for (const mesh of doc.getRoot().listMeshes()) {
  const ex = mesh.getExtras() ?? {};
  if (ex['wh.slot'] && Array.isArray(ex.targetNames)) {
    mesh.setExtras(ex); // targetNames -> three.js morphTargetDictionary
  }
}
```

### Runtime (three.js — the pattern the creation suite consumes)

- Load **one** `THREE.Skeleton` from the master armature.
- Every slot `SkinnedMesh` binds to it: `slotMesh.bind(masterSkeleton, slotMesh.matrixWorld)`.
  Multiple skinned meshes sharing one skeleton is stock three.js — no per-slot skeletons,
  no "ghost bones" (all garments reference the same bone names, per the authoring convention).
- Toggle slots via `KHR_node_visibility` (4.3+) or plain `object.visible`.
- UI slider → shape key: `mesh.morphTargetInfluences[mesh.morphTargetDictionary[name]] = v`.
  Facial bones are just more skinned meshes on the same skeleton (jaw, brow, lid joints),
  driven by the same morph/pose system — no second rig.

---

## Part 3 — Configura / Modular 3D Systems research

### What was searched

- Web + GitHub for "Configura" character creator, "Modular 3D Systems", modular character
  mesh-swapping repos (2026-10-23).

### What exists

**Configura** — by Team Figoose (`configura-team`), an **open-source (MIT, per the Godot
Asset Store listing) character-creator *creation* tool for the Godot engine** (v1.1,
2026-08-10). Feature set: modular character assets (hair, clothing, accessories), mesh
deformation via blendshapes, skeletal deformation, layered materials/color customization,
**automatic UI generation based on imported mesh data**.
Sources: https://store.godotengine.org/asset/configura-team/configura/
(also listed at https://store-beta.godotengine.org/search/?query=%23playercharacter).
The store pages link docs (Google Drive) and a Discord; **no public GitHub repo link was
found** on the reachable pages.

"Modular 3D Systems" as a named repo turned up nothing vendored-able: a paid itch.io
Godot addon ("Modular 3D Character System"), a Unreal/Notion architecture doc, and
generic UE/Unity modular-clothing writeups. No MIT JS/three.js library.

### Verdict: DO NOT VENDOR

License is compatible (MIT) but the code is **GDScript/Godot-scene based** — there is no
JS module to vendor into WH's three.js + gltf-transform pipeline. Porting it would mean
rewriting the slot manager and UI-generation logic from scratch, which is exactly what
Part 2 above already specifies natively. Per the no-junk rule, nothing was pulled.

**Adopt the ideas, not the code:**

- *Automatic UI generation from mesh data* → generate creation-suite menus from
  `wh.slot` / `targetNames` extras at intake time (the auto-rig lane already walks every GLB).
- *Blendshape-driven deformation* → the morph-target/slider mapping in Part 2.
- *Modular slots on one skeleton* → the master-armature pattern in Part 2.

---

## Part 4 — Rapier vs cannon-es audit

### The discrepancy (verified on main)

The brief said "Rapier3D: ALREADY IN USE." **Rapier is not in the repo.** The actual stack:

| Layer | Engine | Location | Version (latest verified) |
|---|---|---|---|
| Rigid bodies (visuals only) | **cannon-es** | `game/vendor/cannon-es/cannon-es.js` (MIT, ATTRIBUTION.md) | 0.20.0 = **latest on npm** |
| Soft body (XPBD muscle/jiggle) | **Jolt** | `game/vendor/jolt/jolt-physics.wasm-compat.js` (MIT) | jolt-physics 1.1.1 |
| Rapier | — | **not present anywhere** | — |

`game/js/physics.js` (~190 lines, `WHPhysics`) is wired by `game/js/integration.js`:
lazy `import('cannon-es')` inside try/catch — **the game runs fine without it**.
Fixed 60 Hz accumulator (clamped at 0.1 s), `SAPBroadphase`, `allowSleep`, static ground
plane. Three uses, all visuals-only per the file's own header and the gameplay
determinism rule (combat sim + netplay rollback must never read physics state):

1. **Arena props** — knockable crates/barrels/lanterns (`addProp`, `loadArenaProps`, `blast`).
2. **Impact debris** — short-lived chunks with fade-out (`debris`).
3. **KO tumble** — proxy body the fighter root lerps toward (`koTumble`).

### Is cannon-es doing its job well? Yes.

Evidence from the code: stepping is fixed-timestep and clamped (no spiral of death),
sleeping + SAP broadphase keep the body count cheap, debris self-cleans (geometry and
material disposed), failure mode is graceful (no physics = no props, game still runs).
The vendored copy is byte-current with upstream's final release. Nothing in the audit
suggests instability, perf problems, or missing features *for its current scope*.

### Would Rapier help? Only for a consumer that doesn't exist yet.

What `@dimforge/rapier3d-compat` would add: **determinism**, **joints**
(spherical/prismatic — the primitive a per-limb muscle servo needs), a **kinematic
character controller**, CCD, and WASM throughput. What it costs: a ~2 MB WASM payload on
a **mobile-first** game, a second physics integration to maintain, and a build-pipeline
exception (the repo is deliberately no-build-step; Jolt already needed a wasm-compat
base64-embedded build to fit that rule).

The only WH design that needs joints/determinism is the **active-ragdoll servo layer**
(ghost rig + variable-stiffness muscle servos + behavior library from the Euphoria
research) — and that stack **does not exist yet** (see reconciliation below). Migrating
props/debris/KO-tumble to Rapier buys nothing: cannon-es already does those jobs with
zero dependencies and no WASM.

### Recommendation: KEEP cannon-es — hybrid only on a real trigger

1. **Keep cannon-es** for the current visuals-only scope (props, debris, KO tumble).
2. **Do NOT migrate blindly.** No benefit, real costs (payload, complexity).
3. **Hybrid gate:** add Rapier *alongside* cannon-es **if and only if** the active-ragdoll
   servo layer gets built — that layer needs joints + kinematic controllers + determinism,
   which cannon-es cannot provide. Keep cannon-es for debris/props even then.

### Reconciliation: false "Rapier" claims on main

`docs/research/EUPHORIA-PHYSICS-2026-10-23.md` (merged via PR #892) repeatedly states WH
uses Rapier — e.g. line 53 ("WH's partial-ragdoll layer (Rapier + Jolt + PhysicsServo)"),
line 90 ("Rapier handles this in WH"), and the vision-mapping table at lines 125–136
("Rapier.js ✅ equivalent", "Rapier covers it"). **All false:** rigid bodies are cannon-es,
and there is no Rapier anywhere in the tree.

It also cites "WH's existing **PhysicsServo spec** from the Gang Beasts research."
Verified: **no `GANG-BEASTS-PHYSICS-2026-10-23.md` exists on main or in any branch history**
(`git log --all` on that path is empty; PR #880 never merged into this repo), and the
only "servo" mention in the entire tree is inside the EUPHORIA doc itself. The
PhysicsServo spec is a *planned* spec, not an existing one.

**Flagged for the doc owner** (PR #892 author / research crew): correct EUPHORIA-PHYSICS
to cannon-es + Jolt, and mark the PhysicsServo spec as planned-not-existing. This PR
intentionally does **not** edit that doc — surgical scope (one new file).

---

## Caveats

- This worker's checkout is **sparse** (`core.sparseCheckout=true`); `tools/anim/`,
  `packages/creation-suite/src/`, and other excluded paths were not visible locally.
  The `tools/anim/gltf_codec.mjs` reference comes from `tools/TOOLS-INDEX.md` (visible),
  not from reading the file. The upgrade regression test must be run by a worker with a
  full checkout.
- gltf-transform CLI command names in Part 2 are the standard v4 CLI surface
  (`merge`, `dedup`, `prune`, `partition`, `quantize`, `meshopt`, `inspect`); the
  programmatic function names were verified against the installed 4.1.1 exports.
- No game code was changed. No menus touched (ui_sources gate unaffected).
- ALL CHARACTERS ARE ADULTS (standing rule; no character content in this doc).
