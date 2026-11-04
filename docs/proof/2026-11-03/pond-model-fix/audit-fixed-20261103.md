# Pond Fixed GLB — Audit

**Date:** 2026-11-03 · **Files audited:** `pond-fixed-20261103.glb` (PRIMARY, encoded; structure read directly + decoded copy `pond-fixed-decoded-20261103.glb` for skinning) and `pond-fixed-keepbulge-20261103.glb` (alternate)
**Method:** `audit_fixed.py` — per-part skinning, three.js semantics (each mesh skinned by its own node's skin, bindWorld × IBM). The same script run on the shipped base (`work/tsuyu-fixed.glb`) **reproduces the diff report's shipped numbers exactly** (whole z max 0.4272, crotch slices 0.232/0.241/0.231/0.217/0.395/0.427/0.423, per-mesh bboxes), so the method is validated against the parent lane's independent implementation. Raw output: `audit-fixed-raw.txt`.

## Primary build — structural checks (encoded file, read directly)

| Check | Shipped | Primary fixed | Verdict |
|---|---|---|---|
| Meshes / prims | 9 / 15 | 7 / 13 | penis + bulge meshes gone, nothing else |
| Verts | 295,975 | **240,415** | Δ = −55,560 = −30,708 (penis) − 24,852 (bulge) exactly |
| Tris | 98,721 | **80,201** | Δ = −18,520 = −10,236 − 8,284 exactly |
| Skins | 9 × 52 joints | 7 × 52 joints | removed parts' skins left with them; all remaining skins full 52-joint sets |
| Nodes | 62 | 60 | −2 (the two removed mesh nodes) |
| Materials | 9 (5 textured) | 7 (**7 textured**) | `penis`, `boots` gone; every remaining material has a baseColorTexture |
| Images | 7 | 8 | −penis −boots BC −boots MR, +eyes +googles_mask +hair +outfit |
| TEXCOORD_0 | present on 9/15 prims in encoded shipped (pruned on 6) | **present on 13/13 prims** | D6 closed |
| Viewer load (three.js) | 15 prims, 9 textured | **13 prims, 13 textured, no error** | loads clean in the game viewer |

## Primary build — skinned geometry (per-part, bind pose)

- **Whole-model bbox:** min (−0.780, 0.000, −0.311), max (0.780, 1.800, **0.297**) — height unchanged 1.800 m; **forward max dropped 0.427 → 0.297** (the suit/breast surface), exactly the brief's target.
- **Crotch band** (centre column |x| < 0.06, 5 cm slices, grounded): the forward-most surface per slice is now the suit column from the diff report — 0.136 / 0.141 / 0.139 / **0.145** / **0.165** / 0.179 for y 0.65–0.95 — i.e. suit surface ≈0.145–0.165 at crotch height, no protrusion. (The body's own flush skin patch, mesh0 prim3, z ≤ 0.148, is the visible female crotch geometry in the renders.)
- **Every remaining mesh's skinned bbox is identical to shipped** (body, suit, gloves, googles, hair, belt, mask — see `audit-fixed-raw.txt` vs diff report §3), including the seam-unified Mask prim. Nothing moved, nothing rescaled.
- **New image bytes verified in the encoded file:** eyes 8,078 B sha256 `e08995ce…`, googles_mask 124,605 B `9e7cbe7f…`, hair 124,407 B `5f5e445a…`, outfit 1,445,635 B `5fd95488…` — byte-identical to the .blend's packed files. Pre-existing images byte-identical to shipped (skin `a1d48bb7…`, face `70ee32e0…`, suit `b4a0009a…`, suit_MR `7504e3a9…`).

## Alternate (Bulge-kept) build — deltas vs primary

8 meshes / 14 prims, 265,267 verts / 88,485 tris (Δ vs shipped = exactly the penis mesh only), 8 skins × 52, all prims UV'd and textured, whole z max 0.297, crotch forward-most = Bulge at **0.241**. Renders: `proofs/proof-pondfix-after-keepbulge-{front,q34,face}-20261103.png` — the exposed Bulge reads as a dark mottled mass hanging at the crotch; that render is the evidence behind excluding it in the primary.

## Visual verification (visual-gate viewer, headless Chromium)

Proofs in `pond-fix/proofs/`, all > 20 KB (232–317 KB), shot with `shoot_pondfix.py` (original `viewer.html` for front/q34; face close-up via `viewer2.html`, a copy with an added `view=face` camera — original viewer untouched):

- BEFORE (shipped): `proof-pondfix-before-{front,q34,face}-20261103.png` — cone at crotch, pale flat hair, cyan flower eyes, pink speckled belt, barefoot.
- AFTER (primary): `proof-pondfix-after-{front,q34,face}-20261103.png` — **viewed by this worker**: cone and bulge gone, crotch = flush suit/skin surface, she reads female in front and q34; hair dark green with authored highlights; eyes show the authored texture (sclera + black pupils) in the face close-up; googles/mask and belt carry their authored textures; suit/skin unchanged.

## Known remaining gaps (flagged, not fixed here)

1. **Boots:** the real `boots` object (clean .blend, at the feet, material `tsuyu-boots`) has no counterpart in any GLB — she still renders barefoot. Needs a rig-transfer job (Ryusan part-2 precedent), coordinator to schedule.
2. **Bulge call:** primary excludes it (evidence in ground truth §1/§4 + keepbulge render). If the owner wants the intake KEEP note applied literally to the playable model, land `pond-fixed-keepbulge-20261103.glb` instead — same textures/eyes/hair fixes, penis still removed.
