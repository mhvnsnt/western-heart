# Creation suite — unification map (2026-10-22)

Where multiple tools do the same/similar job, they are COMBINED into one
system per domain — not separate islands. Three access layers everywhere:

1. **Unified** — one panel per domain merging all sources.
2. **Separate** — each original tool still reachable on its own menu.
3. **Universal** — the WWE step wizard: one combined front-end walking
   every system in creation order (template → body → face → … → done).

## Unified systems

### 1. BODY — one panel, three parametric sources
| Source | Contributes | State in fighter JSON |
|---|---|---|
| MB-Lab | 100s of morph params (mass/tone/age/phenotype…), hair engine | `F.mb_lab = {character, morphs:{}}` |
| MPFB 2 | macro + regional targets (bulk, belly, limbs…) | `F.morphs` (`MPFB_<id>` → -1..1, bakes to shape keys) |
| Build-A-Bod | body scaling/builder | *pending upstream — row reserved* |
| No Mercy/WMXIX | 14M+9F body types, H/W/muscle proportions | `F.body.body_type`, `F.body.proportions` |

The BODY tab renders ONE slider system: body-type cards, proportion
sliders, then the merged parametric group (MB-Lab + MPFB2 sliders
alphabetical by label, each tagged with its source). "Generate base"
submits an `mb-lab` job; "Bake MPFB2 targets" runs the data-path bake.
No separate "MB-Lab body" vs "MPFB2 body" islands.

### 2. FACE — one picker, two parametric sources
| Source | Contributes | State |
|---|---|---|
| GNM | identity (gender/ethnicity/seed), 20 semantic expression params, 4-joint pose/gaze | `F.gnm = {identity, expression, pose}` |
| MB-Lab | face-region morphs, expression presets | `F.mb_lab.morphs` (face keys), `F.face` |
| No Mercy/WMXIX | 98M+20F face textures, head shapes | `F.body.head_shape`, face part equip |

The FACE tab: preset cards merge GNM semantic presets + No Mercy faces in
one grid (each card tagged `gnm`/`wwe`); the 20 GNM param sliders and the
MB-Lab face-region sliders live in one "detail" group. "Bake GNM head"
submits a `gnm` job whose GLB can replace the head.

### 3. RIGGING — one panel, one chain
GameRig auto-rig → rig_repair verify → Wiggle 2 jiggle chains →
limb-system extras. The LIMBS tab + JOBS tab expose it as stages of ONE
"Rig this fighter" flow (each stage a real job), plus the separate tools
stay addressable: `tools/auto_rig`, `tools/jiggle`, `tools/rig_repair`.

### 4. SKIN — one panel
`tools/texture-pipe` (PBR bake) + `tools/customization/skin-library`
(swatch browser) + 8 No Mercy tones + MB-Lab skin engine params. Fluid
Painter row reserved pending upstream.

### 5. HAIR — one category
WMXIX 165-style library + No Mercy hair/front-hair + CC0 real meshes +
MB-Lab hair-engine jobs, in the ATTIRE > Hair grid (one grid, source tags).

### 6. IMPORT — one panel, backend picker
Tripo pull / Tripo intake / TripoSR / Stable-Fast-3D / CUE4Parse / file
import are backends of ONE import flow: pick source → options → job.
`model-audit` runs automatically on every import ("audit" stage);
`render-prep` normalizes before Blender ever sees the file. Backends stay
separately runnable via their fetch scripts.

### 7. EXPORT — one panel, chained
Blender batch cleanup → glTF-Transform → gltfpack, as ONE "Export
fighter" flow with per-stage toggles and the size report. Each stage also
runnable alone.

## Universal mode

The **WWE step wizard** (`customization/create-fighter/js/creation-flow.js`)
is the universal front-end: template → body → face → skin → hair →
facial hair → attire → profile → moveset → done. Every step deep-links to
its unified panel. It is not a launcher — the panels ARE the merged
systems, the wizard is their sequence (docs/CREATION-FLOW-MAP.md).

## What's genuinely merged vs linked

| Pair | Verdict |
|---|---|
| MB-Lab + MPFB2 bodies | **Merged**: one slider panel, one fighter-JSON morph space, both bake paths real. Full mesh-level merging isn't possible (different base topologies) — the merge is at the control + data layer, which is what the user touches. |
| GNM + MB-Lab faces | **Merged**: one preset grid, one param group, `F.face`+`F.gnm` side by side. Mesh-level merge pending the GNM head-bake job (then the baked head swaps in). |
| Import backends | **Merged**: one flow, backend picker, shared audit/prep stages. |
| Export chain | **Merged**: one chained flow. |
| Rigging stages | **Chained** (auto-rig → repair → jiggle), each stage separate-runnable. True single-click "rig everything" is a job-chain preset, not a fake merge. |
