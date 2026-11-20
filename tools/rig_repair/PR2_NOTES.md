# PR 2: Skeleton refit + re-skin

## refit.py — the core new step

No free tool refits an EXISTING skeleton in place (all auto-riggers build new
skeletons, breaking clip compatibility). This implements the vendor-documented
"volume mode" algorithm from Voxel Heat Diffuse Skinning as headless Blender
Python:

- For each arm/leg joint: `object.ray_cast()` through the mesh on 3 axes.
- Inside (ray-parity vote) → move to the SHORTEST chord's midpoint.
- Outside → move to nearest surface point + half the inward thickness.
- Clamp displacement (default 0.10 m); log outliers to JSON.
- After repositioning, RECOMPUTE inverse bind matrices from the new rest pose
  on export — this keeps existing animation clips (local rotations) playing
  unchanged.
- One Blender process per model (crash isolation); flags
  `--background --factory-startup --disable-autoexec --python-exit-code 1`;
  run with `env -u PYTHONPATH`.

Measured (Stick-Up v1, decimated): 14 joints moved (shoulders/arms/upleg 2–3 cm;
elbows/wrists/knees/ankles 10 cm clamped, were 4–10 cm outside the mesh).

## reskin.py / reskin_heat.py — CONDITIONAL re-skin

- `reskin.py`: meshonline Surface-Heat-Diffuse-Skinning (MIT) — skins to YOUR
  existing armature, handles multi-sub-mesh. Binary verified working.
- `reskin_heat.py`: Blender ARMATURE_AUTO fallback.

**Decision (documented, measured):** re-skin is NOT a mandatory pipeline stage.
On the tested model, shd re-skin produced worse weights than the transfer
(Hips dominated 40% of verts, RightShoulder 25% → stretch 94–136 vs 28–45
baseline). The pipeline default (`pipeline.py --reskin none`) KEEPS transfer
weights and fixes them via separate+armpit (PR 3). Re-skin only when weights
are missing or stale.

## Blender-space lessons (in-file comments)

- Blender is Z-up, glTF is Y-up: the importer converts; pose/ray targets must
  be converted (`G2B`).
- `arm.data.bones` head/tail are NOT populated by the glTF importer — use
  edit bones.
- Bone parents must be restored after `use_connect` moves (else the export
  writes a broken hierarchy).
