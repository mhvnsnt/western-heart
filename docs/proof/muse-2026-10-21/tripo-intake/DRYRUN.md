# Tripo auto-intake — dry-run proof (2026-10-21)

End-to-end `--dry-run` of `tools/tripo-intake/intake.py` on a temp copy of
`roster/kinpo/attires/attire1/model.glb`.

## Input provenance (no guessing)

- file: `roster/kinpo/attires/attire1/model.glb` (temp copy; original untouched)
- sha256: `ec67f8f0ddd57e97a915cc85408df08956dcc8bfddfe982698261f03fb6a155f`
  — matches `roster/kinpo/ATTIRE-SLOTS.md`
- structure: 1 mesh, 0 skins, 0 joints (unrigged Tripo static)
- command:
  `python3 tools/tripo-intake/intake.py --in <tmp>/kinpo-dry.glb --fighter kinpo --attire 1 --stage-root <tmp> --report-root <tmp> --dry-run`

## Facing (the critical gate)

`facing_check.py` verdict: **CONFIDENT +X**

| cue | result |
|-----|--------|
| cue1 (gamerig foot-vs-shin) | raw yaw 2.8°, snapped +X, residual 2.8°, toe offset 3.2% of height, 74,045 foot verts |
| cue2 (assets.js feetFacingCue) | x-score +0.157, z-score −0.043 → dominant +X |
| agreement | both cues +X; all gate thresholds pass |

Full numbers: `facing_report.json`.

**Note:** the 2026-10-21 k-NN batch lanes rigged kinpo assuming +Z ("Tripo export
convention"). The intake measures +X on the source mesh with two agreeing cues.
The intake's `--facing +X` was passed to the rig; the pose renders confirm the
skeleton is correctly oriented (face visible in the -Y "back" camera, exactly
where GameRig puts a +X-facing mesh).

## Rig (proven pipeline, heavy stack)

`tools/auto_rig/rig_tripo_static.py` with `--facing +X`: decode → gamerig
Blender 4.0.2 backend (73 def bones; heat proxy 24k verts, 27 unweighted) →
smooth_weights (SMOOTH_OK, edge p99.9 1.70, bind-consistency 8.2e-07 m) →
validate + anim_check → render_poses → encode. See `steps.log`,
`gamerig_metrics.json`, `smooth_weights.log`.

## Gates

- `validate.py`: **PASS** (valid glTF, skinned mesh, canonical bones, height in range) — see `rig_report.json`
- `anim_check` (CMU135_04_boxing stress clip): flags recorded —
  `Hips->LeftPelvis` bone variance 155.5%, 40 vertex displacement spikes,
  p99.9 edge stretch 1.927 (< 2.5). These are clip-extreme deformation flags of
  the same kind the shipped Zui A1 carries (Zui: 609.4%, 60 spikes, p99.9 5.92→1.586);
  they are RECORDED in `intake_summary.json` (`anim_check_flags`), not silently passed.

## Renders (viewed)

`pose_t*.png` — front/back/side at t=0.00 and at the anim_check spike frames
(t=1.21, t=1.38). Viewed by the operator: rest pose is coherent (face, limbs,
proportions correct; no inside-out or detached geometry); spike frames show
plausible boxing motion, no catastrophic tearing. The render camera convention
(`render_poses.py`: "front" camera at Blender +Y) means the face appears in the
"back" image — this is correct for a +X-facing mesh rigged to -Y.

## First attempt / environment notes

- Attempt 1 failed at the final encode: `ENOSPC` (`/tmp` is a 512 MB tmpfs).
  Re-ran with stage/report roots and `TMPDIR` on the overlay filesystem; all
  stages completed.
- This VM's Blender 4.0.2 needed `libEGL.so.1`/`libGL`: apt hung on the
  mirror, so `libegl1_1.7.0-1build1` + `libgl1` were extracted from the Ubuntu
  pool (libglvnd) to `~/workspace/tools/syslibs` with `LD_LIBRARY_PATH`.
  Documented in `tools/tripo-intake/README.md`.
