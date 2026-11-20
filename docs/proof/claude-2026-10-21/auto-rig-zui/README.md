# Zui A1 (Drunken Monk Tripo) auto-rig — proof, 2026-10-21 (Claude session)

Before: `zui-attire1` (main PR #431) had ZERO skinned meshes. In a fight Zui was invisible and the
page threw 480 `getWorldPosition` errors.

After: `roster/zui/attires/attire1/model-rigged.glb` (sha256 cc6a5185…). It has 1 skin with 73 joints
and WH canonical names. The owner's original `model.glb` (c51e0d40…) is unchanged.

| File | What |
|---|---|
| rigged_poses_3frames_3views.png | CMU boxing clip at 0 s / 1.21 s / 1.71 s (the anim_check spike frames), back, front and side; Blender workbench render, viewed |
| live_fight_zui_vs_pantera.png | game harness `tools/proof-harness/fight.mjs zui pantera`: visible, T3 stance facing Pantera, 0 page errors |
| gamerig_backend_clip_renders.png | the backend's own proof renders |
| gamerig_metrics.json | normalize, fit and heat-proxy stats (attempts, unweighted counts) |
| anim_check_before_smoothing.json / anim_check_after_smoothing.json | official gate: edge p99.9 6.66 -> 1.52 (gate 2.5) |
| smooth_weights.log | tools/auto_rig/backends/smooth_weights.py run |

The backend fixes behind this run are in `tools/auto_rig/backends/gamerig_backend.py` (2026-10-21):
- **Arm/hand fit from a template snapshot.** The palm and finger bones had been left 0.23 m below the hand.
- **Bone heat with a triangle-based decimate target and a retry.** Heat had failed for every vertex at
  96k triangles and solved at 48k.
