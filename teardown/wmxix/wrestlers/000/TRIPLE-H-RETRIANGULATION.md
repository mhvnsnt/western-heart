# Triple H (slot 000) — re-triangulation (W6, 2026-11-19)

The old faced assembly (`TRIPLE_XXX_wmxix.obj`, 606v/580f) was broken:
227 faces had max edge ≥ 0.2 m and only 192/580 face triples matched the
raw strip mesh's 383 faces — it triangulated the assembled vertex list
as one continuous strip, creating faces across batch boundaries.

## This rebuild

- **Files:** `triple-h-000_0.obj` / `triple-h-000_1.obj` (606 verts,
  383 faces each), `triple-h-000_0.png` / `triple-h-000_1.png`
  (2D-projection renders), `hhh-manifest.json`. The two attires have
  IDENTICAL geometry (verified); they differ only in textures.
- **Positions:** translation-only assembly (verts /2500 + bone world
  position). Bone world positions come from the FULL euler-matrix chain
  + perm (1,0,2) + /100, root-relative — a translation-only chain puts
  the calf/foot upside down (the leg chain's euler flips the
  direction). Reproduces the verified solution points OBJ to **median
  0.0002 m, max 0.0005 m** over all 606 verts; bbox **[0.77, 2.22,
  1.27] m — exact match** to the solution.
- **Correction to the solution doc §5 map:** batches 1 (arm) and 2
  (hand) do NOT go to the LEFT arm bones (40/43). The solution placed
  them on the RIGHT side (implied Z +0.239 / +0.801; nearest bones R
  UpperArm 19 / R Hand 22, +0.06 m in Z from the JSON chain — the v2
  assembler's skeleton computation is not in the repo). This rebuild
  uses the positions recovered from the verified solution points OBJ.
  All other 11 batches match the §5 map exactly.
- **Faces:** the raw strip mesh's 383 faces (`000_0_raw_strip.obj`),
  verified **0 cross-batch faces**. Its split rule is NOT
  distance-based (it splits at steps as small as 6 raw units — likely
  degenerate-triangle removal). A 1300-raw-unit distance rule gives 536
  faces (stable 1200–1500 plateau) but ADDS 285 unverified faces vs the
  raw mesh, so the raw faces are used directly.
- **Result:** bad faces (max edge ≥ 0.2 m) **227 → 33** (all 33 are
  within-batch raw-mesh faces, mostly wide head-shell triangles — real
  strip structure, not cross-batch slivers). Max edge 0.591 m.

## Still missing for a wire-ready attire

Textures/UVs (UVs never located in the YOBJ stream — open RE work;
the `000_0.tex` PNGs are now extracted, see `tex/0/`), Table1 detail
verts (1,254: head details, fingers), skinning/rig. The mesh is 13
rigid body-part batches, not a closed skinned mesh — Blender cleanup
→ GLB → UniRig auto-rig is the wiring lane's path.
