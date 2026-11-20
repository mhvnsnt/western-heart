# SLICE — Rig Notes

## Attire 1 — Owner Tripo (cf9cf660, wired 2026-10-21)

- The wired GLB is the **raw Tripo pull**: glTF 2.0, EXT_meshopt_compression +
  KHR_mesh_quantization, 1 mesh / 1 primitive / 1 PBR material, 3 embedded textures.
- **STATIC — no skin, no joints, no animations.** Do not expect the fight rig to
  bind to it as-is. It wires as the default display/fight model now per Tripo law
  (owner Tripos are the mains); the skeleton comes at the **rig stage**, same as
  the other Tripo mains (Zui A1, Diablo A1, CornerStone).
- Rig-stage job when it runs: auto-rig / skeleton transfer onto the game skeleton,
  then re-verify the model-key guard + a stance render. The owner's canon details
  that must survive rigging: jagged chrome arm blades (both arms), skull mask
  blending into the back of the head, scars across the body, small blades on the
  belt buckle and the side of one shoe.
- Scale: Tripo native units — measure the bounding box at rig stage and normalize
  against the roster's porter scale there; do not rescale on a guess before then.

## Attire 2 — Dragunov build (PR #433)

- Already rigged: Tekken 7 game skeleton (`SK_CH_dra_bdu_1P`, 198 joints in the
  GLB), 17 meshes. No rig work needed.
- Scale flag carried from PR #433: bounding box 2.02 m in the rip's native units,
  kept at porter scale; settle it in the same rig/scale pass as Attire 1 so both
  attires stand at one height.
