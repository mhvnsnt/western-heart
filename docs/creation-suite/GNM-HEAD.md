# GNM-Head Study → CJ Parametric Face Rig

**Date:** 2026-10-17 · **Lane:** gnm-head (Rig Perfection Wave)
**Upstream:** https://github.com/google/GNM — **Apache License 2.0** (commercial OK)
**Vendored code:** `tools/pulled/GNM/` (code only; weights not pulled)
**Paper:** Ploumpis et al., "GNM Head: A Generative aNthropometric Model of the human head",
arXiv:2607.23687 (29 July 2026)

## 1. What GNM Head is

GNM ("genome") is Google's family of parametric statistical human models, learned
from ~5,000 high-resolution 3D head scans (22-camera Z CAM rig) plus
artist-sculpted internal anatomy. GNM Head (first public module, July 2026) is a
**3D morphable model**: a template mesh + linear bases + linear blend skinning.

Model function (from the paper, §3.3):

```
M(Θ; Ψ) = L(VB, X; W)
VB = T + Σᵢ βᵢ·Iᵢ + Σᵢ φᵢ·Eᵢ        # bind-pose verts: template + identity + expression
```

- **Identity β ∈ ℝ²⁵³** — 170 head, 80 teeth, 3 eyeball shape components.
- **Expression φ ∈ ℝ³⁸³** — the part we care about:
  - 100 left eye, 100 right eye
  - 150 lower face
  - 32 tongue
  - 1 iris
- **Pose θ ∈ ℝ⁴ˣ³** — axis-angle rotations of K=4 joints: right eye, left eye,
  neck, head. **Translation τ ∈ ℝ³.**
- The expression basis E is a *learned linear basis*: each of the 383 params is a
  blendshape weight on a displacement field over the template vertices. There are
  no artist-named sliders inside the 383 — they are PCA-style components.

## 2. The semantic layer (what makes it artist-usable)

Raw PCA components are un-animatable, so Google ships `semantic_sampler.py`: two
pre-trained CVAE decoders (`identity_decoder_model.h5`,
`expression_decoder_model.h5`) that map **named classes → full param vectors**,
plus `blend_expressions({class: weight})` for mixing.

The 20 expression classes (verbatim from the enum in `semantic_sampler.py`):

| # | class | # | class |
|---|-------|---|-------|
| 0 | SURPRISE | 10 | SMILE_WIDE |
| 1 | DISGUST | 11 | CORNERS_DOWN |
| 2 | SUCK | 12 | PUCKER |
| 3 | COMPRESS_FACE | 13 | WINK_LEFT |
| 4 | STRETCH_FACE | 14 | WINK_RIGHT |
| 5 | HAPPY | 15 | MOUTH_LEFT |
| 6 | SQUINT | 16 | MOUTH_RIGHT |
| 7 | PLATYSMA | 17 | LIPS_ROLL_IN |
| 8 | BLOW | 18 | SNARL |
| 9 | FUNNELER | 19 | TONGUE_CENTER |

Note what's **missing**: GNM ships **no brow basis** (brows approximated through
the eye region) and **no appearance model** (no skin texture, no hair).

## 3. The Nathan Dickson add-on (studied, not vendored)

"GNM Head Importer" for Blender (Blender 5.1+, free download via Gumroad:
https://nathandickson365.gumroad.com/l/GNMImporter). Technique: slider panel
(grouped by parameter family) → sets φ/β/θ live → rebuilds the mesh in the
viewport. We did not vendor it: no license is stated (all-rights-reserved
implied) and it needs a Gumroad checkout. We built our own equivalent UI.

## 4. Adaptation: CJ parametric face rig

Steal-like-an-artist: we keep GNM's **control architecture**, not its mesh.

| GNM concept | CJ adaptation |
|---|---|
| Expression vector φ, grouped (eyes / lower face / tongue / iris) | `CJ_FaceParams` float props in the same 4 groups |
| 383 PCA components | ~20 semantic cartoon params (blink, squint, look, jaw, smile, …) — named, animator-grade |
| Semantic sampler (20 classes → vectors) | `CJ_PRESETS`: his 8 expression-matrix entries + eye-darts + GNM-class-inspired extras, as param vectors; `blend_presets()` mixes them like `blend_expressions` |
| LBS joints (eyes, neck, head) | Drivers on existing eye-card / pupil / brow / tongue objects |
| Iris param | `pupil_toggle` (canon: white eyes default, pupils toggle on for emphasis) |
| No brow basis | We ADD mask-brow cards (sheet 05: "the mask's dynamic movement") |

**Canon guards (locked, from the sheets):**
- White eyes by default; pupils appear only on emphasis beats (`pupil_toggle`).
- Mouths stay a **hard-cut swap set** (17 meshes, `mouth_index`) — the parametric
  layer drives jaw/smile/frown *transforms* on the socket children, never
  interpolates mouth geometry.
- Comedic Space Ghost / Aqua Teen range: exaggerated, never realistic.

Implementation: `3d-assets/face-rig/cj_parametric_face.py` (our original code).
Proof: `3d-assets/face-rig/proof_parametric.py` renders the 8-expression matrix +
eye-darts + viseme strip as the sign-off checklist.

## 5. License & citation

Apache 2.0 — free for commercial use, modification, and redistribution with the
copyright notice retained. Please cite the paper (bibtex in the upstream README)
if you publish work built on the model itself. Our rig code is original.
