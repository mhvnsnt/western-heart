# Diablo A1 (Tripo "fantasy demon") auto-rig: FAILED, not shipped (2026-10-21, Claude session)

Run: `python3 tools/auto_rig/rig_tripo_static.py --in roster/diablo/attires/attire1/model.glb --report-dir docs/proof/claude-2026-10-21/auto-rig-diablo`.
This was the tool's first full run.

**Verdict: FAIL. The rigged file was NOT committed and NOT wired.** `diablo-attire1` stays the unrigged static from PR #412.

- The gamerig fit measured an A-pose (arm droop 36° left / 45° right) on a winged model. Large wings, hair spikes and hanging robe cloth surround the arms, and the arm chain was fitted into that mass.
- In the renders below (`pose_t*_*.png`, front / back / side at the anim_check spike frames), the body crumples into the robe. The wings and spikes are swept along by the arm and spine weights.
- The gates: `validate.py` passes on structure. `anim_check.py` after smoothing measured edge stretch p99.9 = **11.16**, against a gate of 2.5, plus 70 tearing spikes. (smooth_weights' own 10-frame sample read 1.99 and missed the frames anim_check catches.)

**What it needs:** wing and robe bones of their own, i.e. a skeleton with extra chains. The GameRig humanoid template has none. A separate arm-vs-wing segmentation before the fit would also work. Rigging him as-is would ship a torn fighter, and the owner has already rejected that kind of result ("cronenberg").

Owner's original file: untouched.
