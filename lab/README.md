# Western Heart — Lab track (private, owner's own source games)

The Lab track turns the owner's own Tekken 3 teardown into playable Godot 4 content. Plan: money-machine-hq `docs/western-heart-audit.md`; inventory: `docs/western-heart/INVENTORY.md`.

## Milestone 1: canonical skeleton + Tekken 3 → glTF importer + rig check
- `skeleton/canonical_skeleton.json`: **WH-Canonical-22**. Mixamo-compatible names, Y-up meters, faces +Z. The bind pose is the T3 stance with world-aligned joints.
- `skeleton/retarget_maps.json`: maps three source rigs (Tekken 3 rigid 27-row/18-part, Mixamo 49, and the 13-bone rigify-style pantera rig) to canonical.
- `tools/t3_to_gltf.py`: reads the KMD (hierarchy, joint offsets, faces) and the stance OBJ from `teardown/tekken3/tools/local/pose_assemble.py`. It recovers each part's real stance transform by rigid Kabsch fit (max RMS 0.94 T3 units, about 1 mm). It writes a rigid-skinned GLB (each vertex weighted 100% to its part) with 11 combat clips (`tools/clips.py`, 2-bone IK, planted feet). It also imports a T3 stage panorama.
  ```
  python3 lab/tools/t3_to_gltf.py fighter teardown/tekken3/models/king95/king95.kmd teardown/tekken3/renders/pose-check/king_stance75.obj lab/game/assets/t3_king.glb
  python3 lab/tools/t3_to_gltf.py stage teardown/tekken3/stages/l/stg_l_panorama.obj lab/game/assets/t3_stage_l.glb
  ```
- `tools/rig_check.py` + `tests/test_rig_check.py`: an automated check that bones, weights, mesh and animation agree, with no exploded vertices and feet on the floor. Run `python3 lab/tests/test_rig_check.py`. It also catches the cm-scale Mixamo Idle in `game/assets/models/pantera.glb` (stretch ×21, sinks 8 m).
- `tools/preview.py`: CPU-skinned matplotlib renders (`docs/m1_preview.png`).

### Honest gaps (M1)
- Only King has a decoded stance pose. The others need `pose_assemble.py`, whose `kmd`/`motion` modules lived at `/home/hatch/...` and are not in the repo.
- About 43% of KMD faces reference "imported" seam vertices (two import lists per row) that `kmd_parse.py` doesn't decode yet, so parts render with joint gaps and holes.
- The clips are authored on the canonical rig, not decoded T3 motion banks (same missing decoder). Textures (TIM atlas) aren't applied; the meshes use vertex colours.
