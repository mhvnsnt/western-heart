# VENDOR: MagicArticulate
- Upstream: https://github.com/Seed3D/MagicArticulate (CVPR 2025, ByteDance Seed)
- License: Apache-2.0 (LICENSE file retained)
- Vendored: code + skeleton_models + utils + data_utils + third_partys + READMEs. Excluded: examples/ (demo meshes), assets/ (doc images), .git.
- Checkpoints (NOT vendored): python download.py -> skeleton_ckpt/checkpoint_trainonv2_hier.pth
- What it does: fastest skeleton predictor (4.6 GB VRAM, 1-2 s/mesh). Pair with blender-heat for skinning.
- Wire-in: tools/auto_rig/backends/ai_rig.py --backend magicarticulate
