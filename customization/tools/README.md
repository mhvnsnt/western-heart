# Western Heart Customization Suite — Tools

Authoring/runtime tooling that powers the customization suite
(`../UNIFIED-UI-SPEC.md`). Per the PULL-IN DIRECTIVE, tools here are
**wired up, not just downloaded**: each entry ships an integration script or
module plus docs on how it plugs into the suite's UI spec.

## Current tools

### GNM — Generative aNthropometric Model (`gnm/`)

**What it is:** Google's open-source parametric 3D statistical human model
("GNM", pronounced *genome* — the owner's "GNM" pickup item, seq 77688).
Learned from a large dataset of high-fidelity 3D face scans. Gives
fine-grained, disentangled control over:

- **Identity** — subject-specific facial features (linear basis, named dims)
- **Expression** — rich expression blendshapes (named, e.g. happy/surprise)
- **Head pose** — neck + eyeball joint rotations
- Internal anatomy: eyeballs, teeth, tongue modeled in the mesh

**Source:** https://github.com/google/GNM
**Pinned upstream commit:** `5cf11d785a38a83597e64ad0b6d15950bcd6b390`
(pulled 2026-10-13; see `gnm/UPSTREAM-COMMIT.txt`)
**License:** Apache License 2.0 (`gnm/LICENSE.google-gnm`) — permissive,
suitable for commercial use. No copyleft contamination of Western Heart.
**What's in `gnm/`:** the `gnm/shape` Python package (NumPy/JAX/PyTorch/TF
backends, data loaders, semantic samplers, fitting utils) minus upstream's
demo media (28 MB of GIFs) and 4 K textures — 3.0 MB total. Upstream's own
README is preserved at `gnm/README.md` (shape package) and
`gnm/README.upstream.md` (repo root).

**Weights (important):** the model parameters (`gnm_head.npz`, version 3.0)
are NOT in the git repo — they download on first use from Hugging Face
(`https://huggingface.co/google/gnm-3`, path `v3_0/gnm_head.npz`). That repo
is **gated**: it returned HTTP 401 anonymously on 2026-10-13, so an HF
account with access granted is required. `wh_gnm_wireup.py --fetch-weights`
handles the download (via `huggingface_hub` or a token). Nothing is
re-downloaded if a cached copy exists (CHECK-BEFORE-DOWNLOAD).

**How it plugs into the suite (per `../UNIFIED-UI-SPEC.md`):**

| Spec section | GNM's role |
|---|---|
| §5.1 BODY → Head Shape (7M + 3F shapes) | GNM identity basis → continuous head-shape sliders. Bake the 7M/3F presets as identity-parameter presets; expose fine sliders on named identity dims. |
| §5.1 BODY → Face | GNM expression blendshapes → the face/expression morph targets; semantic `IdentitySampler` gives "randomize face" with gender/ethnicity controls. |
| §5.1 functional behavior ("re-morphs the preview instantly") | `wh_gnm_wireup.py export-glb` bakes base head + expression targets into a GLB with morph targets; the web build drives `mesh.morphTargetInfluences[i]` per slider — live re-morph, no round-trip. See `gnm/WH-INTEGRATION.md`. |
| Fitting pipeline (`gnm/fitting_utils/`) | Reconstruct a GNM identity from the owner's key-art face scans → roster-faithful head bases (feeds LIKENESS LOCK: owner art in, parametric head out). |

**Current limits (honest):**
1. **Head only.** Google has released only GNM Head; the full-body GNM model is
   on their roadmap, not yet open-sourced. BODY-tab body sliders (Height,
   Weight, Muscle, …) keep using the WMXIX parametric sliders + No Mercy body
   morphs until the body model lands.
2. **Weights are gated** (HF auth required) — the pipeline is built and tested
   against the documented `.npz` field layout, but a first real-weights run
   still needs an HF token with access to `google/gnm-3`.

## Tooling conventions

- One directory per tool under `customization/tools/<name>/`.
- Each tool ships: upstream code (lean), `UPSTREAM-COMMIT.txt`,
  `LICENSE.<name>`, `README.upstream.md`, and a `wh_<name>_wireup.py`
  (or equivalent) that connects it to the suite — plus a
  `WH-INTEGRATION.md` showing the exact UI-spec hookup.
- Never commit upstream demo media, datasets, or model weights — document
  where they come from and fetch on demand.
