# Scimitar pose-safe re-encode — proof (2026-11-22)

## What was wrong (PR #1837 defect)
`roster/scimitar/attires/attire1/source/scimitar-a1-rigged.glb` was reported as rendering NOTHING when skinned: skinned bbox min [7477, 4.7, 2119] max [136113800, 149112601, 38920884].

## What the diagnosis actually found
- The file was NOT broken. Plain load (the way the game loads it) renders Scimitar perfectly at 1.8 m.
- The explosion was caused by three.js `skeleton.pose()`, which the show lane's viewer called before measuring. Reproduced exactly: pose() gives bbox [7477.423, 4.679, 2119.646]..[136113800.531, 149112601.616, 38920884.317] and a blank screenshot.
- Root cause: gltfpack quantized POSITION to 14-bit ints (0..16383) and baked the dequantization transform B (scale 1.0987e-4, translation [-0.8215, 0, -0.2349]) into the mesh node AND the inverse bind matrices (IBM_j = J_j^-1 * B, spec-correct). `pose()` recovers bind world matrices as inverse(IBM) = B^-1 * J_j — wrong by B^-1 (x9102) on the root bone; after pose() the bone matrices become I and bindMatrixInverse (B^-1) blows the raw vertices to 0..1.49e8.
- Game impact: the fight and select-stance paths NEVER call pose(). The only in-game caller is game/js/portrait-capture.js:38, only under opts.rest (facing-audit rest portraits). So Scimitar plays fine in the game; only a rest portrait capture would blank him.

## The fix (this PR)
Pose-safe re-encode, no re-rig (the rig was proven correct — re-rigging would have rebuilt a correct rig):
1. Bake B into POSITION as float metres (1,262,492 verts, range [-0.8215, 0, -0.2349]..[0.8215, 1.8, 0.2349]).
2. Mesh node transform -> identity.
3. IBM_new = IBM_old * B^-1 (pure J^-1 now).
Script: fix-pose-safe.mjs (Node + @gltf-transform/core, the repo's own toolchain). Then re-encoded with the repo codec (tools/anim/gltf_codec.mjs encode: meshopt + KHR_mesh_quantization) to 23,206,904 B for staging.
Note: the codec's quantize step normalizes positions to the 2 m centered bind space and compensates in the IBMs (the same structure as Chordz/Cornerstone). So the STAGED file's pose() returns the bind geometry (2 m centered, feet at -1) — visible and correctly proportioned, NOT an explosion. The plain (unstaged, 96 MB) fixed file's pose() returns the exact 1.8 m standing figure. Both render the game-truth view identically.

## Verification
| file | mode | skinned bbox | result |
|---|---|---|---|
| original (main) | plain | [0,0,0]..[14954,16383,4276] (raw ints) | renders 1.8 m figure (correct) |
| original (main) | pose() | [7477,4.7,2119]..[1.36e8,1.49e8,3.89e7] | BLANK (the defect) |
| fixed plain (96 MB) | plain | [-0.822,0,-0.235]..[0.821,1.8,0.235] | full figure (scimitar-fixed-plain.png) |
| fixed plain (96 MB) | pose() | [-0.822,0,-0.235]..[0.821,1.8,0.235] | full figure (scimitar-fixed-pose.png) |
| staged encoded (23 MB) | plain | [-0.822,0,-0.235]..[0.821,1.8,0.235] | full figure (scimitar-enc-plain.png) |
| staged encoded (23 MB) | pose() | [-0.913,-1,-0.261]..[0.913,1,0.261] | bind geometry, visible (bbox measured; screenshot save was blocked by a disk-quota wave) |

Numerical: fixed plain file M_j = J_j*IBM_j = I (max err 1.16e-6); encoded file IBMs carry the common 0.9-scale transform (M_j vs M_0 err 1.1e-6), mesh node identity — pose() safe by the same structure as Chordz/Cornerstone.

## Cornerstone / Chordz leg-stretch verdict
NOT a defect. Plain load (game truth): Cornerstone 1.8 m standing [-0.672,0,-0.478]..[0.618,1.8,0.396]; Chordz 1.8 m [-0.789,0,-0.167]..[0.789,1.8,0.167]. Both are a uniform 0.9x of their 2 m bind geometry — no leg-specific stretch. pose() returns the bind geometry (2 m centered), correctly proportioned (cornerstone-pose.png, chordz-pose.png). The "legs 2-3x" look in the show lane's renders was a camera-fit artifact: the viewer fitted to the 2 m geometry box (center y=0) while the figure stands 0..1.8, cropping to legs only (chordz-plain.png shows this). No fix needed; no files changed for them.

## Not changed in this PR
- game/assets/models/scimitar-rigged.glb (12,868,988 B) and game/assets/models/scimitar.glb (13,789,832 B) are different files from the wired roster file; whether they are loaded anywhere / need the same fix is a follow-up, not assumed here.
- Cornerstone (roster/ryuji-rock/...) and Chordz (roster/chordz/...) — no changes, per the verdict above.

## Files in this PR
- roster/scimitar/attires/attire1/source/scimitar-a1-rigged.glb (replaced: 19,132,660 B -> 23,206,904 B)
- docs/proof/scimitar-pose-safe-20261122/ (this README + 6 screenshots)

PR proposal only — merge is the owner's call.
