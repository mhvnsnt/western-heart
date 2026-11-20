# VENDOR: Puppeteer
- Upstream: https://github.com/Seed3D/Puppeteer (NeurIPS 2025 Spotlight, ByteDance Seed)
- License: Apache-2.0 (LICENSE file retained)
- Vendored: skeleton/ + skinning/ + animation/ code, export.py, READMEs. Excluded: examples/, assets/, animation/inputs/ (demo inputs), .git.
- Checkpoints (NOT vendored): skeleton/download.py + skinning/download.py
- What it does: rig (skeleton + skinning) PLUS video-guided animation — animate a rigged model from a video. The animation/ folder is the differentiator.
- Wire-in: tools/auto_rig/backends/ai_rig.py --backend puppeteer
