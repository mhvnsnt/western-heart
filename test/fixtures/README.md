# Real-rig fixtures (names only)

These fixtures contain BONE NAMES ONLY — no mesh, texture,
animation, or model data, and no famous character is shipped or
redistributed by them. They exist so `rig-compat.js` is tested
against the real rigs WH builds on, per the 2026-10-24
owned-file correction (full owned-game files are the
authoritative source, not community approximations).

- `cape-node-names.json` (95 names): node names from WH's own
  Cape stance GLB (`CapeJones_Rig`), itself derived from owned
  T7 Alisa files via the WH Cape pipeline. Includes deform
  bones plus FK/IK/pole control bones — the mapper must pick
  the deform bones.
- `alisa-bone-names.json` (111 names): non-null source bone
  names from the WH Alisa->Cape bonemap (source: T7 Alisa_ARM,
  `cyborg-x.glb`, western-heart main). The bonemap is the
  authority for the t7-160 patterns in `rig-compat.js`
  (e.g. `LeftShoulder` -> `clavicle_L`, `LeftUpLeg` ->
  `thigh_L`).

Provisional (NOT covered by these fixtures): T3 and Tripo rig
patterns in `rig-compat.js` are still unverified against their
full-file rigs. The GPU creation batch
(`tools/gpu-lane/creation-batch-job.py`) validates them against
real models when it runs.
