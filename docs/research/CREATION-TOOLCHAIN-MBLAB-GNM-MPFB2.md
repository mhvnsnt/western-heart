# Creation toolchain: MB-Lab + GNM + MPFB 2 — pipeline placement

Three parametric generators feed the Western Heart character creation suite.
Each is fetched on demand (never committed), each is wired into the suite's
menus AND the unified per-domain systems, and each lands in the same
downstream chain.

## The chain

```
┌────────────────────────────── PARAMETRIC CREATION ──────────────────────────┐
│ MB-Lab (body+face+skin+hair)  │  GNM (head/face/neck/eyes/teeth/tongue)      │
│ MPFB 2 (body+skin+assets)     │  Build-A-Bod (body scaling, existing)        │
└──────────────────────────────┴──────────────────────────────────────────────┘
        │ unified BODY panel (all body sources) │ unified FACE panel (all face sources)
        v                                       v
┌────────────────────────────── WRAP ─────────────────────────────────────────┐
│ External intake meshes (Tripo / SmutBase) are fit onto the parametric base   │
│ (or the base is fit to them) so one rig drives everything.                    │
└──────────────────────────────────────────────────────────────────────────────┘
        v
┌────────────────────────────── RIG ──────────────────────────────────────────┐
│ GameRig auto-rig backend (tools/auto_rig) -> Western Heart canonical rig.     │
│ NaughTyRig / Wiggle 2 spring chains for jiggle bones (unified RIGGING panel). │
└──────────────────────────────────────────────────────────────────────────────┘
        v
┌────────────────────────────── EXPORT ───────────────────────────────────────┐
│ GLB via glTF-Transform + meshoptimizer (+ gltfpack), Blender batch cleanup.  │
│ Lands as: template base_mesh | custom fighter | roster attire.                │
└──────────────────────────────────────────────────────────────────────────────┘
```

## Tool cards

| Tool | Source | License | Blender | Role | Fetch |
|---|---|---|---|---|---|
| MB-Lab 1.8.x | animate1978/MB-Lab | GPL-3.0 code / **AGPL-3.0 database** | **4.0+ ✅** (1.8.0 added 4.0 support) | Full-body parametric: morphs, phenotypes, skin, hair, expressions, auto-rig | `tools/mb-lab/fetch-mb-lab.sh` |
| GNM | google/GNM | **Apache-2.0 ✅** | none (pure Python/numpy) | Parametric head: identity/expression PCA, 17,821-vert topology, 4-joint skeleton, teeth/tongue/eyes | `tools/gnm/fetch-gnm.sh` |
| MPFB 2 | makehumancommunity/mpfb2 | GPL-3.0 code / **CC0 assets ✅** | **≥ 4.2 ❌** (pipeline pins 4.0.2) | Parametric body, procedural skin, asset library, Rigify/game rigs | `tools/mpfb2/fetch-mpfb2.sh [--with-blender]` |
| Build-A-Bod | (existing intake tool) | — | 4.0.2 | Body scaling / proportion builder | already in repo |

## Compatibility notes (verified 2026-10-22)

- **MB-Lab ↔ Blender 4.0.2: YES.** MB-Lab 1.8.0 "introduced Blender 4.0
  support"; 1.8.1 is the final release. Headless generation tested on the
  pipeline Blender — see tools/mb-lab/README.md. This is the default
  parametric backend.
- **GNM ↔ Blender: N/A (good).** GNM evaluates in plain Python; the runner
  writes OBJ/GLB that the Blender chain consumes. No version coupling.
- **MPFB 2 ↔ Blender 4.0.2: NO.** MPFB 2 requires Blender ≥ 4.2
  (extension platform). Two paths, both real:
  1. *Data path (default):* drive MPFB2 morph-target values from the suite
     (already in morphdata.js) and bake to `MPFB_<id>` shape keys with
     `customization/body-morphs/apply_mpfb_morphs.py` — runs on 4.0.2 today.
  2. *Live path:* fetch script pulls a portable Blender 4.2+ next to the
     addon; `tool:"mpfb2-live"` jobs route there. Status JSON names the
     Blender that ran.

## License posture

- MB-Lab-generated base meshes are **AGPL-3.0** (database license). The
  generation scripts + param specs in this repo are the corresponding
  source. Template meshes ship with this notice (customization/templates/).
- GNM output: Apache-2.0, no copyleft on generated heads.
- MPFB2 output from CC0 assets: no copyleft — the clean-room alternative
  when it matters.

## Suite wiring

- BODY panel: MB-Lab morphs + MPFB2 targets + Build-A-Bod scaling, one
  slider system (unified) + per-tool sections (separate) — see the
  unification map.
- FACE panel: GNM identity/expression + MB-Lab face morphs, one picker.
- Template bases: `customization/templates/meshes/*.glb`, baked by
  `tools/suite-jobs/run_job.py` from the `mb_lab` spec in
  `customization/templates/body-templates.json`.
- Every Blender-backed option submits a real job (queue + live status),
  never a dead button — see tools/suite-jobs/README.md.
