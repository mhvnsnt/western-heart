# Kaggle notebook cell set — Real-ESRGAN texture batch upscale on GPU (READY TO RUN, not yet run).
# Tool: xinntao/Real-ESRGAN, BSD-3-Clause, open source. Needs PyTorch + CUDA (Kaggle T4 fits).
# Model choice (from research): RealESRGAN_x4plus for photos/AI images/screenshots;
# RealESRGAN_x4plus_anime_6B for anime/line-art/flat-shaded textures (keeps clean edges).
# Batch rule: upscale ONLY textures below target res; never upscale an already-clean 2K
# texture (wastes GPU, risks over-smoothing). Always eye-check one output per batch.
# --- cell 1 ---
# !git clone https://github.com/xinntao/Real-ESRGAN.git
# !pip install -q basicsr facexlib gfpgan
# !pip install -q -r Real-ESRGAN/requirements.txt
# !python Real-ESRGAN/setup.py develop
# !mkdir -p Real-ESRGAN/weights && cd Real-ESRGAN/weights && \
#   wget -q https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth && \
#   wget -q https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.2.4/RealESRGAN_x4plus_anime_6B.pth
# --- cell 2: batch (inputs in /kaggle/input/textures/, outputs in /kaggle/working/upscaled/) ---
# !python Real-ESRGAN/inference_realesrgan.py -n RealESRGAN_x4plus -i /kaggle/input/textures \
#     -o /kaggle/working/upscaled --suffix 4x --tile 512 --tile_pad 16 --fp32
# For anime-style textures swap -n to RealESRGAN_x4plus_anime_6B.
# Download ONLY /kaggle/working/upscaled/ back to the repo pipeline input dir.
