# Checkpoints — downloaded on demand, NEVER vendored

The AI backends need pretrained weights (hundreds of MB to GBs). They do not
belong in git. Download them on the GPU box before running.

## MagicArticulate (Apache-2.0)

```bash
cd tools/auto_rig/vendor/magicarticulate
python download.py   # skeleton_ckpt/checkpoint_trainonv2_hier.pth
```

## UniRig (MIT)

```bash
# checkpoint auto-downloads from Hugging Face on first run:
#   VAST-AI/UniRig
```

## Puppeteer (Apache-2.0)

```bash
cd tools/auto_rig/vendor/puppeteer/skeleton
python download.py   # skeleton_ckpts/puppeteer_skeleton_w_diverse_pose.pth
cd ../skinning
python download.py   # skinning_ckpts/puppeteer_skin_w_diverse_pose_depth1.pth
```

On Kaggle, `tools/auto_rig/kaggle/auto_rig_gpu.py` runs these for you.
