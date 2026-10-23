# tools/mpfb2 — MPFB 2 (MakeHuman Plugin for Blender)

MPFB 2 (github.com/makehumancommunity/mpfb2) is the free/open-source
MakeHuman character generator rebuilt as a Blender plugin: one-click
parametric humanoid mesh, macro + regional body modeling targets,
auto-rigging (Rigify, IK/FK, game-engine rig variant with breast bones),
procedural skin + eye materials (MakeSkin), and an asset library for
clothes / body parts / materials. The suite already bakes its morphs
(customization/body-morphs/: BODY_MORPHS/FACE_SHAPE_MORPHS in
customization/create-fighter/js/morphdata.js, via cape-jones PR #128) —
this tool adds the LIVE plugin behind the unified BODY system.

## Place in the Western Heart pipeline

```
PARAMETRIC BODY CREATION (this tool)
  MPFB2 builds the base humanoid: parametric body + procedural skin/eyes
  + asset-library clothes, auto-rigged (Rigify or game-engine rig)
        |
        v
UNIFIED BODY SYSTEM — one BODY panel drawing on THREE sources:
  MPFB2 targets  +  MB-Lab morphs  +  Build-A-Bod scaling
  (see docs/CREATION-SUITE-UNIFICATION-MAP.md)
        |
        v
WRAP -> RIG (GameRig backend) -> EXPORT (standard chain)
```

## Blender compatibility — READ THIS ⚠️

| | |
|---|---|
| Pipeline standard | Blender 4.0.2 |
| MPFB2 requirement | **Blender ≥ 4.2** (extension platform; 2.0 betas: lowest 4.1.0) |
| Verdict | ❌ MPFB2 does **not** run on our pinned 4.0.2 |

How we handle it (documented, no stubs):

1. **Data path (default, runs on 4.0.2):** the suite drives MPFB2's *morph
   target values* (already in morphdata.js) and bakes them to
   `MPFB_<id>` shape keys with
   `customization/body-morphs/apply_mpfb_morphs.py` — no MPFB2 plugin
   needed, works on the 4.0.2 pipeline today.
2. **Live path (Blender 4.2+):** `fetch-mpfb2.sh` can also pull a portable
   Blender 4.2+ (`--with-blender`) into `tools/mpfb2/blender42/` for jobs
   that need the real plugin (asset-library clothes, MakeSkin materials,
   full auto-rig). The suite job queue routes `tool:"mpfb2-live"` jobs
   there and reports which Blender ran the job in the status JSON.

## License — VERIFIED ✅

- Plugin **code**: GPL-3.0
- Bundled **assets** (targets, skins, clothes): **CC0** — the cleanest
  license of the three parametric tools. MPFB2-generated base meshes from
  CC0 assets carry no copyleft; prefer this path when license-clean bases
  matter (contrast MB-Lab's AGPL database — see tools/mb-lab/README.md).

## Fetch-on-demand (DISK RULES)

```bash
bash tools/mpfb2/fetch-mpfb2.sh [dest] [--with-blender]
# default dest: tools/mpfb2/vendor
```

Pulls the MPFB2 nightly/extension zip (or extension-platform install
instructions for GUI use), verifies the addon, and optionally fetches a
portable Blender 4.2+ for the live path. Nothing large is committed.

## Suite wiring

- BODY panel → "MPFB2 targets" slider group (live preview + fighter JSON,
  works now on 4.0.2 via the data path).
- BODY panel → "Generate base in MPFB2" submits a `tool:"mpfb2-live"`
  job to the queue (needs the 4.2+ Blender; the job panel says so
  honestly and offers the data-path bake instead).
- Every option works: sliders drive the preview today; the live job runs
  the real plugin where installed.
