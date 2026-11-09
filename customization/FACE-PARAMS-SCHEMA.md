# face-params/v1 — schema (creation suite)

The shared interchange format for face measurement in the creation
suite. The same format is produced and consumed by the Physique Lab
side of this system; files move between the two repos unchanged.

```json
{
  "schema": "face-params/v1",
  "frames_used": ["f0002.png"],
  "frames_skipped": {"f0001.png": "smile"},
  "mean_pitch_deg": 0.0,
  "iod_px": 0.0,
  "params": { "global.face_width_cheek": 2.0598, "...": 0.0 },
  "mean_shape": [[0.0, 0.0, 0.0]]
}
```

- All `params` values are in inter-ocular (iris-centre distance) units,
  pitch-corrected, averaged over gated neutral frames by 3D similarity
  (Procrustes) alignment. Verticals are kept, not discarded.
- The gate rejects smiling, jaw-open, blinking, and off-pose frames;
  every rejection is recorded in `frames_skipped` with its reason. A
  result built from few frames says so in `frames_used`.
- Parameter names are grouped: `global.*`, `brows.*`, `eyes.*`, `nose.*`,
  `lips.*`, `jaw.*`, `cheeks.*` — the same groups the creation suite UI
  exposes as slider sections.
- `mean_shape` is the aligned 478-point mean landmark set in pixels.
- Engine: `customization/face-measure/track.py` (MediaPipe Face
  Landmarker, Apache-2.0) + `params.py`. Licence-clean chain only — see
  MODEL-TWEAKING-PRINCIPLES.md principle 5 and the face-from-photo plan
  in the Physique Lab repo for the banned-component list.
