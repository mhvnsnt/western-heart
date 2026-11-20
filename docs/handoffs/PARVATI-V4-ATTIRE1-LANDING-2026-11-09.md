# Parvati v4 → game attire1 landing + the "0.33 m below skeleton" claim: REFUTED (2026-11-09)

## Verdict
**No model change was needed, because the defect does not exist.** The
hair lane's claim that `parvati-basefixed-glb-v4.glb`'s skinned mesh sits
~0.33 m below its own skeleton is a measurement artifact. This PR lands
the already-accepted v4 state (material fixes + black gauntlets) as the
game's Megami attire1, unchanged.

## How the claim arose
The number traces to `rawAttrCentroid.y = -0.3353` — the raw local-space
POSITION centroid Y of one attire shell mesh (24_Material43_025_0_0) read
as if it were world space. The v4 file family uses
EXT_meshopt_compression + KHR_mesh_quantization with per-mesh local
frames; local-space centroids are not world positions.

## Measurements (three.js, the game's own engine convention)
- Bind consistency: K = JW·IBM is CONSTANT across all weighted joints of
  every skinned mesh (max deviation 2.1e-06 on v4, 2.3e-07 on v3). K ≠ I
  for this file family by design (gltfpack/Daz convention: geometry in
  per-mesh local frames; K's translation is the frame origin, e.g. brow10
  K0_t (−0.0001, 1.2677, 0.0647)). Pilot files use K = I (constancy
  3.6e-07). Both conventions compose correctly.
- Renders: full-body and skinned-only renders are coherent;
  SkeletonHelper bones run through the mesh correctly (foot bones inside
  the boots at the floor grid y=0, head fan inside the head).
- Pose test: Head +0.45 rad — the mesh follows the bone exactly like the
  pilot-file control. No offset exists in-engine.
- v3 ≡ v4 bind data byte-identical in every bindcheck number: the v4
  surgery touched materials and textures only, never bind data.

## What lands
`roster/parvati/attires/attire1/model-rigged.glb` is replaced with the v4
bytes: 42,298,953 B, sha256
907d007938ca566f56f103526fb9595d0b901e111a838218ff1ae278ed4d29b5.
Verified in the landing file: 29 materials; material 28 =
`24_Material44-gauntlet-black` with baseColorTexture index 40 (image 40
`mat44-gauntlet-black`); the Gaunlet primitive points at material 28;
41 images; stored morph weights all zero. This replaces the older
41,298,604 B variant currently on main. No Blender re-export was needed,
so the known full-export OOM wall (exit 137 on this VM) was avoided
entirely — no geometry was regenerated, shrunk or degraded.

## Downstream note
The bogus −0.33 figure was also baked into the hair-fix harness
(`_hair-fix-20261108/stage.html` line 57: `hairRoot.position.y = -0.33`
default) as a compensation constant, which displaced hair parts on the
v4 body — see the Defect C report. The correct joint-alignment offset of
a Daz-rig hair part on the v4 body is −0.417 (v4 Head joint y 1.212 vs
part head joint y 1.629).
