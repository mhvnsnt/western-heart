# Jiggle pipeline — Wiggle 2 (real tool, no hand-written solver)

Secondary-motion (breast/glute jiggle) for Western Heart rigs, produced
by the vendored **Wiggle 2** addon
(`tools/open-source/blender-addons/wiggle-2/wiggle_2.py`, shteeve3d
v2.2.4) — spring physics integrated by the addon itself, baked with the
addon's own `wiggle.bake` operator.

This replaces the hand-written verlet `Spring` class that used to run as
pass 2 of `anim-fix-work/scripts/retarget_def_rig.py`. That solver is
retired for this pipeline: jiggle keys in production blends must come
from this driver.

## Driver

`wiggle2_jiggle.py` (run inside Blender 4.0.2, headless):

```
xvfb-run -a env -u PYTHONPATH \
  LD_LIBRARY_PATH=~/workspace/tools/egl-stack/usr/lib/x86_64-linux-gnu \
  XDG_RUNTIME_DIR=/tmp \
  <blender> -b <mocap.blend> --python tools/jiggle/wiggle2_jiggle.py -- \
    --armature RIG-SCARLETT --out <baked.blend> --metrics <metrics.json>
```

What it does, in order:

1. Records the input's existing jiggle motion (tail series of the 18
   jiggle bones) for the baseline comparison.
2. Strips the old solver's jiggle fcurves and resets the jiggle bones'
   stored bases to rest — the true rigid reference (mocap only). Wiggle
   2's pre-handler clears wiggle-bone bases every frame during the sim
   anyway; the strip only cleans the reference and the output action.
3. Registers Wiggle 2 from the vendored file and configures it —
   **one bone selected at a time** (Wiggle 2 copies every property set
   to all selected bones; see the vendored USAGE.md gotchas).
4. Bakes via `bpy.ops.wiggle.bake()` (overwrite mode: keys merge into
   the current action), freezes the armature, disables scene wiggle.
5. Verifies before saving: every non-jiggle fcurve (face included)
   hash-identical to the input, face fcurve count unchanged (zero —
   the mocap keys no face bones and neither does this pipeline), zero
   NaN/Inf in the baked jiggle curves, and per-bone deviation stats
   vs the rigid reference for both the old verlet input and the new
   Wiggle 2 bake. Any failure exits non-zero and is listed in the
   metrics JSON.

## Bone setup (Scarlett/Star rig)

- `DEF-breast.L/R`, `.001`, `.002`, `.003` — TAIL wiggle, chain on,
  stiff 1400·0.88^level, damp 1.1, stretch 0.02, gravity 0.6.
- `Butt_L/R` + `.001`–`.004` spokes — HEAD wiggle, chain on,
  stiff 1100·0.85^level, damp 1.3, stretch 0.02, gravity 0.6.
  Head (not tail) because the Butt bones are 0.0026 units long and
  tail wiggle crashes Wiggle 2 with a singular matrix at that scale —
  full evidence in the vendored addon's USAGE.md, gotcha #2.
- Face bones: never configured, never keyed. Verified by fcurve hash
  on every run.
- Scene: solver iterations 4, loop physics on, bake preroll 24.

## Proof

`proof/scarlett-wiggle2-metrics.json` — the metrics from the production
run on the CMU lambada mocap (`scarlett_mocap.blend`, frames 1–72 @
24 fps): per-bone RMS/MAX deviation from rigid for the old verlet
bake and for this Wiggle 2 bake, face/non-jiggle digest checks, NaN
count, exact parameters per bone.

Proof videos (EEVEE 320×320, front + back, same framing as the
approved verlet baseline videos) are delivered next to the baseline
files as `scarlett-wiggle2-front.mp4` / `scarlett-wiggle2-back.mp4`.
