# Stage 2 — RETARGET

> **ALL AGENTS — READ THIS FIRST.**
> This stage **consumes** the retargeting lane's bone-map — it does not define
> one. The Tekken bone-map (`tools/anim-retarget/bone_maps/tekken_to_wh.json`)
> is owned by the retargeting lane. If it isn't there yet, this script **fails
> loudly** instead of silently substituting a different map. Do not "fix" that
> by hand-writing a Tekken map here — coordinate with the lane.

## What it does

Batch-retargets a whole directory of source animations (FBX, BVH —
whatever tools/anim-retarget/retarget_blender.py accepts) onto one
Western Heart-rigged target GLB, headless in Blender (`xvfb-run`),
one output GLB per input clip.

The retarget math is the lane's `tools/anim-retarget/retarget_blender.py`
(rest-relative delta retarget; Hips translation scaled by hip-height ratio).
This script is only the overnight batch harness around it: per-file logs,
continue-on-error, summary.

## Quick start

```bash
# needs Blender 4.0.2: bash tools/setup/setup_toolchain.sh  (once)
./retarget-batch.sh /path/to/anims /path/to/fighter-rigged.glb /path/to/work/s2 \
  --in-place
```

Options: `--bonemap PATH` (explicit map, e.g. the lane's `mixamo_to_wh.json`
for Mixamo sources), `--fps 30`, `--in-place` (zero Hips translation —
required by AssetManager), `--force` (allow non-empty outdir).

## Coordination contract

- Bone maps live in `tools/anim-retarget/bone_maps/`. New source skeleton?
  The retargeting lane adds the map; this stage picks it up via `--bonemap`.
- Never duplicate `retarget_blender.py` here. If the lane changes its CLI,
  update this wrapper — don't fork the math.
