# Mocap clips

- `cmu_55_02_lambada_loop.bvh` — CMU mocap subject 55, trial 02 ("lambada dance"),
  via the open mirror github.com/una-dinosauria/cmu-mocap (BVH conversion by
  Bruce Hahne / cgspeed, MotionBuilder joint names, frame 0 = T-pose).
  Trimmed to the highest hip-energy 3 s window (10.5–13.5 s of the take) and
  decimated 120 fps → 24 fps by `tools/anim-retarget/trim_bvh.py`.
  CMU mocap is free for research and commercial use; cite CMU Graphics Lab.
