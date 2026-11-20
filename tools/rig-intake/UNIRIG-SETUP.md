# UniRig setup — GPU machine (for Grok / any CUDA box)

UniRig (SIGGRAPH 2025, MIT license) auto-rigs any mesh: skeleton prediction +
skinning weights, then merges the rig back onto the source model. Western Heart
uses it in the Tripo intake pipeline (`tools/import_model.py`) and the creation
suite: every user-created fighter gets auto-rigged on import when a GPU is
available, with graceful fallback when it is not.

Source: https://github.com/VAST-AI-Research/UniRig
Paper: https://arxiv.org/abs/2504.12451
Weights: https://huggingface.co/VAST-AI/UniRig (auto-downloaded on first run)

## Requirements

- NVIDIA GPU with **8GB+ VRAM** (hard requirement — no CPU fallback in UniRig)
- Python 3.11, PyTorch >= 2.3.1 with CUDA
- ~15GB disk for env + weights + Blender deps

## Option A — direct install (recommended for the intake pipeline)

```bash
# 1. clone
git clone https://github.com/VAST-AI-Research/UniRig
cd UniRig

# 2. env (conda recommended; venv works too)
conda create -n unirig python=3.11 -y
conda activate unirig

# 3. torch with CUDA (match your driver; CUDA 12.1 example)
python -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121

# 4. repo deps
python -m pip install -r requirements.txt
python -m pip install numpy==1.26.4

# 5. sparse / scatter / cluster (match YOUR torch+cu versions)
python -m pip install spconv-cu121
python -m pip install torch_scatter torch_cluster \
  -f https://data.pyg.org/whl/torch-2.3.1+cu121.html --no-cache-dir
#    ^ replace 2.3.1/cu121 with your actual torch/CUDA versions

# 6. flash attention (if pip fails, build from source per
#    https://github.com/Dao-AILab/flash-attention)
python -m pip install flash_attn

# 7. weights (auto-download on first run from VAST-AI/UniRig on Hugging Face;
#    or prefetch explicitly)
python - <<'EOF'
from huggingface_hub import snapshot_download
snapshot_download(repo_id="VAST-AI/UniRig", allow_patterns=["skeleton/*", "skin/*"])
EOF
```

## Option B — ComfyUI one-click wrapper

There is a community ComfyUI-UniRig wrapper for one-click use. If you already
run ComfyUI on the GPU box, install the wrapper node through ComfyUI Manager
(search "UniRig") and point it at the same weights above. Note: the Western
Heart intake pipeline calls `tools/rig-intake/unirig_intake.py` (Option A
paths), so Option B is for manual/experimental rigging only — the pipeline
will not see ComfyUI output unless you hand it the rigged GLB.

## Wiring it into the Western Heart repo on the GPU box

```bash
cd /path/to/western-heart        # repo checkout on the GPU machine
export UNIRIG_ROOT=/path/to/UniRig
export WH_UNIRIG=1               # default; set 0 to force fallback
# make sure the unirig conda env's python is the one running the pipeline,
# or that torch+cuda are importable in the pipeline's python
python3 tools/rig-intake/unirig_intake.py --check   # expect UNIRIG READY
```

Then the normal intake just works — unrigged models are auto-rigged before
the rig gates run:

```bash
python3 tools/import_model.py /path/to/tripo_model.glb --character <id> --attire a1
```

Manual single-file rig (no intake):

```bash
python3 tools/rig-intake/unirig_intake.py /path/to/model.glb --out /path/to/rigged.glb
```

## What the pipeline runs (3 stages)

1. `launch/inference/generate_skeleton.sh --input X.glb --output work/skeleton.fbx --npz_dir work/npz`
   — autoregressive skeleton prediction (checkpoint:
   `skeleton/articulation-xl_quantization_256/model.ckpt`)
2. `launch/inference/generate_skin.sh --input work/skeleton.fbx --output work/skin.fbx ...`
   — bone-point cross-attention skinning weights
   (`skin/articulation-xl/model.ckpt`)
3. `launch/inference/merge.sh --source work/skin.fbx --target X.glb --output rigged.glb`
   — bpy merge of the predicted skin back onto the source mesh

`unirig_intake.py` drives all three and returns the final GLB path.

## Post-rig expectations (Western Heart)

- UniRig predicts its own bone names/hierarchy. `tools/import_model.py` maps
  them onto `lab/skeleton/canonical_skeleton.json` by name (Mixamo/Bip/DEF
  prefixes, Spine1/Spine2 aliases). If UniRig's bone names do not map cleanly,
  extend the alias table at the top of `tools/import_model.py` — do not rename
  UniRig's output by hand.
- The rig gates (height 1.3–2.4 m, T/A-pose arms ≥ 40°, symmetric hands,
  segments cover body) still apply to UniRig output. A gate FAIL on a UniRig
  rig means the skeleton needs review, not the gates.
- Secondary jiggle chains (hair/tail/skirt/…) follow the naming table in
  `docs/MODEL_IMPORT_AUTORIG.md` — add them after the base rig passes.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `spconv` import error | install the build matching your CUDA (`spconv-cu121` etc.) |
| `torch_scatter`/`torch_cluster` fail | use the pyg wheel index matching torch+cu versions exactly |
| `flash_attn` pip fails | build from source (Dao-AILab/flash-attention) |
| CUDA OOM | close other GPU jobs; faces are decimated to 50k by default |
| merge stage fails | needs `bpy==4.2` importable in the same python |
| weights 404 / slow | prefetch with `snapshot_download` above; needs HF access |

## No-GPU behavior (this VM)

`unirig_intake.py --check` reports NOT READY and `maybe_autorig()` returns
`None`; `tools/import_model.py` keeps its existing behavior (fail with the
manual Tripo/Mixamo fix message). Nothing in the intake breaks on CPU-only
machines.
