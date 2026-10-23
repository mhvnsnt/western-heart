# SmutBase batch-2 tool evaluations (2026-10-22)

Three Blender tools landed in the SmutBase intake. All are **third-party code**,
so per the repo owner law they are **staged in the workspace, not committed**:
`~/workspace/fix2/smutbase-source/tools/{fluidpainter-nsfw,buildabod-male,buildabod-female,naughty-rig}/`.
Each was extracted, hashed, and inspected (file layout + blend datablock scan
where applicable). This doc records what each tool is, what pipeline it serves,
and the recommended adoption.

## 1. naughty_rig v0.2.3 — anatomy/jiggle rigging pipeline ✅ ADOPT for the Blender rig lane

- **What:** a **Rigify feature set** (not a standalone addon) by nekomata, Blender 3.3+.
  Installs via Rigify → Feature Sets → Install Feature Set from File.
  Original: `sess-3045850964/…-16-naughty_rig_v0.2.3.zip` (200 KB),
  sha256 `47b7b5e7081cca50bde9c3b2e0f30f40bd1fa41dbf73baa417f44cdf68a0e8ff`;
  extracted 1.1 MB.
- **Components** (all Rigify rig types with N-panel parameters):
  - `rigs/NTR/phys_single_chain.py`, `phys_double_chain.py` — **spring-chain
    physics rigs** (rotation overwrite params, per-axis stiffness): the classic
    breast/butt/belly jiggle mechanism.
  - `rigs/NTR/shrinkwrap.py` + `metarigs/NTR/shrinkwrap[_mirrored].py` — bones
    that shrinkwrap to a mesh surface (useful for anatomy/cloth-hugging bones).
  - `rigs/NTR/clothhook.py` — cloth-hook rig.
  - `rigs/NTR/spline/` — `spline_control`, `spline_segment`, `tentacle`,
    `penetrator`, `tracer`: spline-IK chains (distance-driven).
  - `NTR_geo_nodes_3.0.blend`, `NTR_geo_nodes_3.4.blend` — geometry-nodes assets.
- **Fit:** direct hit for the **Torch reference piece** — its spec demands a full
  jiggle set (breasts, belly with soft springs, hips/ass, thighs, camel-toe
  region) with motion-capture proof. The phys chains are exactly the "soft
  springs" mechanism, authored inside Rigify where the rest of the WH Blender
  rig lane already works.
- **Boundary:** naughty_rig is **authoring-time** (inside Blender/Rigify). The
  game's runtime jiggle stays in `tools/jiggle/` (`wiggle2_jiggle.py`,
  `jiggle_physics_bake.py` — bake to GLB). Handoff: Rigify + naughty_rig chains
  in Blender → bake → `tools/jiggle` runtime. Do not treat it as a runtime
  replacement.
- **Blocker:** Blender is not installed on this VM yet (toolchain via
  `tools/setup/setup_toolchain.sh`); Rigify ships with Blender, so no extra
  install beyond dropping the feature set into the rig lane's Blender profile.

## 2. BuildABod Female v1.3 / Male v1.3 — body-part scaling pipeline ✅ ADOPT as parametric reference

- **What:** parametric body-builder `.blend`s (Blender 2.78 format, open
  uncompressed): **DAZ Genesis 3 Female** (`BuildABod_Female_1_3.blend`, 104 MB)
  and **Genesis 3 Male** (`BuildABod_Male_1_3.blend`, 73 MB), each carrying a
  full morph set. Female morph names found in-file include `BreastsSize`,
  `BreastsDiameter`, `BreastsCleavage`, `BreastsImplants`, `BreastsNatural`,
  `BreastsShape01–08`, `BreastsUpwardSlope`, `BreastsDownwardSlope`,
  `BreastsPerkSide`, `BreastsSmall`, `BreastsGone`, `BreastsHeavy`,
  `BreastsUnderCurve`, `ButtOpen`, `ThighBend`, `ThighBack_35_L/R`, …
  Originals: `…-14-BuildABod_Male_1_3.7z` (sha256 `efe95e78…`),
  `…-15-BuildABod_Female_1_3.7z` (sha256 `5db2905d…`).
- **Fit:** the **body-part scaling pipeline** and the **Lily body-type work**.
  Lily (G8F, thick/curvy) is the user-approved female body reference; BuildABod
  Female gives the parametric dials (breast size/shape, butt, thighs) to hit
  that target repeatably instead of hand-sculpting each model. Also directly
  serves the standing Cydney note (size UP breasts and ass at rig time).
- **Caveats:** Blender 2.78 file — opens in modern Blender, but the original
  morph-driving UI may not survive; treat the morphs as a reference library and
  re-drive them through the WH rig lane (shape keys / lattice / bone scaling).
  DAZ morphs are proprietary-derived — fine as an internal reference, do not
  redistribute the blend itself.
- **Recommendation:** pair with the Lily donor — Lily sets the *target*
  silhouette, BuildABod sets the *dials* to reach it per model.

## 3. FluidPainter NSFW v1.0.1 — texture/anatomy pipeline ⚠️ ADOPT narrowly (detail layer only)

- **What:** Blender texture-painting addon (supports 3.1/4.0/5.0) with an NSFW
  fluid-decal asset library (`Fluid_Painter_NSFW_Library.blend` + 4.2 variant):
  paintable decals for breast milk, cum, pee, spit, etc. (`Pics/` previews,
  `Tools/Fluid_Painter_Tools.blend`). 8.3 MB zip → 38 MB extracted.
  Original: `…-13-FluidPainterNSFWAddon_1_0_1_Blender_3.1_4.0_5.0.zip`
  (sha256 `6d9f5a88…`).
- **Fit:** the **texture/anatomy finishing layer** — e.g. the Torch reference
  piece's "repaint painted-on clothing as skin with pores" work and the
  customization suite's NSFW detail options. It is a *decal/effects* tool, not
  an anatomy builder: it does not replace the skinning/repaint/anatomy-modeling
  work, it adds surface detail on top.
- **Recommendation:** install in the texture lane's Blender profile for the
  customization suite's detail pass; do not route core anatomy work through it.

## Placement summary

| Tool | Serves | Staged at | In-repo record |
|---|---|---|---|
| naughty_rig v0.2.3 | anatomy/jiggle rigging (Rigify authoring) | `~/workspace/fix2/smutbase-source/tools/naughty-rig/` | this doc + queue row 16 |
| BuildABod Female/Male v1.3 | body-part scaling (parametric reference) | `~/workspace/fix2/smutbase-source/tools/buildabod-{fe,male}/` | this doc + queue rows 14–15 |
| FluidPainter NSFW v1.0.1 | texture/anatomy detail layer | `~/workspace/fix2/smutbase-source/tools/fluidpainter-nsfw/` | this doc + queue row 13 |

None of the four are committed to the public repo (third-party code, owner law).
The Blender rig lane picks them up from workspace staging when Blender lands on
the rig VM.
