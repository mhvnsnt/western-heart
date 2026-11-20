# Measured optimization (this session, CPU gltfpack binary)

Fresh measurement, 2026-10-24, on a file NOT measured by the prior studio-pipeline lane:

- ep1_cape_main_stance.glb: 128,296 -> 53,828 bytes (-58%), flags `-kn` (bone names preserved), source never overwritten (copy optimized, original kept).

Prior lane measurements (studio-pipeline, same binary/flags, cited not re-run):
- Cape hand stance GLB: 158,884 -> 72,812 (-54%)
- Cape IK stance GLB: 131,240 -> 45,904 (-65%)
- Jungle Outpost stage: 1,669,744 -> 680,460 (-59%), meshes merged 203 -> 111

GPU honesty note: gltfpack is CPU-runnable. Its GPU value is batch parallelism only.
Never report gltfpack outputs as "GPU-optimised" in the compute sense.
