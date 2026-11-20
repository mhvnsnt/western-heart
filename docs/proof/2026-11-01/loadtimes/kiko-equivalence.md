# Kiko Tanaka model — meshopt packing equivalence proof (2026-11-01)

File: `game/assets/models/kiko-tanaka.glb` (MODEL_URLS key `kiko-tanaka`, a live
main fight model, loaded from the remote asset base in the live build).

Packed with the repo's own pipeline policy (tools/gltfpack/README.md):
gltfpack v0.22 (meshoptimizer, built from the pinned tag via
tools/gltfpack/fetch-gltfpack.sh) with `-cc -kn` — meshopt compression on,
bone names kept, NO texture compression (`-tc` stays opt-in and was not
used), NO simplification (`-si` off).

## Size

| | bytes |
|---|---|
| before | 92,208,012 |
| after | 20,234,944 |
| change | **−71,973,068 (−78.1%)** |

## Equivalence checks (all run locally, 2026-11-01)

Decoded with the game's own three r160 GLTFLoader + vendored MeshoptDecoder
(bench harness in the load-times lane; raw attribute streams are quantized
in storage, so geometry was compared in world/normalized space):

| check | original | packed | verdict |
|---|---|---|---|
| vertices | 1,022,970 | 1,022,970 | identical |
| triangles | 1,964,560 | 1,964,560 | identical |
| meshes / skins | 1 / 1 | 1 / 1 | identical |
| skeleton joints / bones | 49 / 49 | 49 / 49 | identical |
| embedded images (3) | sha256 3b28c181…, c0959721…, f4c607c5… | same hashes, same byte counts | **byte-identical** (no `-tc`) |
| world-space position sum (3,068,910 components) | 1,129,078.75 | 1,129,078.88 | Δ 0.13 (quantization rounding, step 0.000108 m) |
| world-space position min/max | [−0.8822, 0, −0.189] … [0.8811, 1.75, 0.2492] basis | identical extremes | identical |
| total skin-weight mass | 1,022,970 | 1,022,970 | identical |
| per-bone weight mass (17 weighted bones) | — | — | worst delta **0.02%** (uint8 rounding) |
| bind-pose render | `kiko-ab-bind-a.png` | `kiko-ab-bind-b.png` | visually identical |
| posed render (7 bones rotated, same angles) | `kiko-ab-posed-a.png` | `kiko-ab-posed-b.png` | visually identical deformation |

Notes on representation differences that are NOT content differences:
gltfpack stores positions quantized (uint14) with the dequantization in
the mesh node's scale/translation (KHR_mesh_quantization, the same
encoding the game's shipped Tripo models use), UVs at 12-bit with a
compensating KHR_texture_transform, and remaps joint indices (bone
identity was therefore compared by NAME through weight mass, above).
Normals are re-normalized to unit length by the packer (the Tripo
source normals were not unit); three.js normalizes normals in the
shader regardless.

## Load timings (bench: local server, Chromium, swiftshader, this VM)

Medians of 3 runs; fetch is loopback (not a phone network) — the
transferable figure is the byte count: at the ~0.5 MB/s effective rate
measured from this VM to the asset Worker on 2026-11-01, 72 MB less is
~2 minutes less download per cold load of this model.

| file | bytes | fetch | parse | first render (compile+draw) |
|---|---|---|---|---|
| kiko-tanaka.glb (before) | 92,208,012 | 535 ms | 1,010 ms | 2,567 ms |
| kiko-tanaka.glb (packed) | 20,234,944 | 109 ms | 1,395 ms | 2,475 ms |

## Deployment note

This model is NOT shell-bundled: the live game fetches it from the
remote asset base first. The repo file is now packed; the bucket copy
at `game/assets/models/kiko-tanaka.glb` must be re-uploaded (20.2 MB)
for live players to receive the packed bytes — that upload belongs to
the B2 lane (tracked in docs/tech/LOAD-TIMES-2026-11-01.md).
