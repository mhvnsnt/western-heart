# Kaggle notebook cell set — UniRig auto-rigging on GPU (READY TO RUN, not yet run).
# GPU already verified on this notebook by nvidia-smi: 2x Tesla T4, 15GB each, driver 580.178.04, CUDA 13.0.
# Why Kaggle: the VM has no GPU; UniRig needs CUDA. Run these cells in
# https://www.kaggle.com/code/marsfmmg/notebook2ff3176461/edit (GPU T4 x2 ON).
# Input: upload a WH model (OBJ/GLB) to /kaggle/input/ or attach as a dataset.
# Output: rigged model + weights — download ONLY outputs, never the checkpoint cache.
# Checkpoint: VAST-AI/UniRig on Hugging Face (auto-download per UniRig README).
# License: check UniRig repo license at runtime before shipping outputs commercially.
# --- cell 1: environment ---
# !nvidia-smi  # expect 2x Tesla T4
# !pip install -q torch --index-url https://download.pytorch.org/whl/cu121  # skip if torch present
# --- cell 2: clone UniRig (code already mirrored in WH workspace tools; Kaggle copy is scratch) ---
# !git clone https://github.com/VAST-AI-Research/UniRig.git 2>/dev/null || echo "UniRig present"
# --- cell 3: run auto-rig on one model (adjust paths; UniRig CLI flags per its README) ---
# NOTE: confirm exact CLI flags from UniRig README before executing — do not guess flags.
# !cd UniRig && python -m unirig --input /kaggle/input/cape_body.obj --output /kaggle/working/cape_rigged.glb
# --- cell 4: verify rig (joint count, skin weights present) then download cape_rigged.glb ---
# import json  # parse/print rig report here; eye-check render before wiring into game.
