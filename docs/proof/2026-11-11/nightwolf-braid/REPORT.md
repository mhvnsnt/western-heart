# Nightwolf braid fix — REPORT (owner order 2026-11-11 20:26 CT)

She/her for Nightwolf throughout (tribute to Serena Misae Brown).
Method: Shonzo + Kumo Blender anime-character tutorials, step by step in order,
render after every step. Tutorial = METHOD; Nightwolf's own design = LIKENESS.
No owner approval claimed.

## Defect (owner's words)
The braid/hair chains arc out in stiff dark curves behind her left side.
Stance proof (PR #1692, julia t035) shows them as "thick modeled strands
frozen mid-motion".

## Root cause (measured, not guessed)
The braid geometry hugged its bones (max lateral deviation from its own bone
segment only 0.04–0.10 m). THE BONES were the arc: the two `hair_jiggle`
chains (2 × 4 bones, 20,079 hair-owned verts) root at x ≈ −0.40 m — 0.4 m off
centerline — and hang in the air ~0.3 m outside the torso silhouette instead
of down her back. Both chains sit on the −X side (her right side; LeftArm
head x = +0.201, so her left is +X — the owner's "left side" is frame-left in
the stance proof; region x > 0.30, y > 0.05, z 1.0–1.45 contains 0 verts).

## Fix (Shonzo + Kumo hair steps, in order)
1. Hair volume/carve (Kumo): the existing Head-owned back hair mass is kept
   as the volume. No change.
2. Strand tubes (Shonzo extrude + Kumo curve → mesh): 2 braids × 3 woven
   tube strands on a NEW drape path hugging her back — roots inside the hair
   mass (x ≈ −0.10/−0.20, y ≈ +0.19), falling straight down the back to
   z ≈ 0.83, tapering 30% root → tip. Bevel tube + Subdivision modifier for
   the rounder inside; strand separation kept (3 visibly separate strands).
3. Weights + bone re-route: new strands weighted to the `hair_jiggle` chain
   (blended across bone boundaries); the 8 hair bones re-routed to the new
   path. Bind change limited to the hair chain; nothing else in the rig moves.
4. Old braid removed: 16,257 free-hanging hair-owned verts deleted (only 391
   boundary tris dropped). The 3,822-vert root cap was kept but re-weighted
   to Head so it cannot swing on a 0.34 m lever arm once the bones move.
   The new braid's UVs sample the old braid's own hair texel (median Color
   RGB 28,24,23; flat normal; metallic ~0.03) — same single material, one
   mesh, one skin, same game-safe structure.
5. Renders after every step (Cycles CPU; EEVEE blocked — libEGL.so.1 absent
   on this VM). V1 failed its own-eyes gate (braids read as light-gray
   twisted ropes — helix too strong, no taper). V2 (helix 0.015 → 0.010,
   tube 0.0135 → 0.012, twists 2.5 → 2.0, 30% tip taper) PASSED: two dark
   tapered braids drape straight down her back to the waist; the diagonal
   arcing mass is gone; no hole at the old root; front chest braids, face /
   war paint, gear, headdress unchanged.
6. Encode with the repo's own codec (meshopt + quantization, the #1692 path).
   Encoded file decoded back and re-rendered — identical to v2.

## Deliverable
- `roster/nightwolf/attires/attire1/model-rigged.glb` — 28,745,068 B
  (was 28,428,932 B, +316 KB / +1.1% for +29,943 net verts).
  1,200,360 verts, 58 joints (49 template + LeftHandThumb3 + 8 hair_jiggle),
  1 mesh, 1 skin, 0 animations. Hair-owned verts now 46,200 on the new path
  (bounds x −0.24…−0.08, y 0.14…0.21, z 0.83…1.26).
- Proofs in `docs/proof/2026-11-11/nightwolf-braid/`: this report,
  `braid-before-back.png` (baseline), `braid-after-back.png`,
  `braid-after-closeup.png`, `braid-after-front.png`.

## Notes / observations (not in scope, recorded)
- RightArm bone head sits at x ≈ −0.001 (near centerline) in the landed #1692
  file while LeftArm is at +0.201. The rerig report's own acceptance metrics
  passed their gates and the stance proof shows a clean guard, so this is
  recorded, NOT re-litigated here.
- The decoded GLB still carries a 42-vert Icosphere mesh node (the rerig
  report said it would not carry over — it did; harmless, left alone).
- Loose thin side strands (Head-owned hair volume, present in the baseline
  too) still arc out slightly at the shoulders. They are the hair volume's
  silhouette, not the braid chains — out of scope, noted.
- Assembly note: Blender OOM-killed the all-in-one build at ~1.3 GB free RAM
  (bmesh + join copies). The braid geometry was still modeled IN Blender per
  the tutorial; only the delete/append assembly ran in numpy on the GLB
  (same 52-byte interleaved layout; the import bake was measured as an exact
  global affine, Blender = 0.835 × file with axis swap, max err 5e-6 m).
  Bone move, export, and all renders ran in Blender. No PIL, no paint,
  no AI Horde, no card.
- The 8 hair-bone leaf tails read z = 0.799 on re-import vs 0.83 as set
  (glTF round-trip normalizes leaf-bone length); heads and directions are
  exact and the braid tips (z ≥ 0.822) stay covered. No impact.
