# VENDOR: UniRig
- Upstream: https://github.com/VAST-AI-Research/UniRig (SIGGRAPH 2025, Tsinghua + Tripo)
- License: MIT (LICENSE file retained)
- Vendored: code + configs + launch scripts + READMEs + blender/ addon. Excluded: examples/ (demo GLBs), assets/ (doc images), .git.
- Checkpoints (NOT vendored, download on GPU box): Hugging Face VAST-AI/UniRig (auto-download on first run).
- What it does: autoregressive transformer predicts skeleton + skinning weights; FBX in/out.
- Wire-in: tools/auto_rig/backends/ai_rig.py --backend unirig
