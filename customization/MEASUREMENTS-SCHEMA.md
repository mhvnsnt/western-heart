# body-measurements/v1 — the measurement sheet schema

The data foundation under the creation system (the foundation
rule: real measurements, every inch). One sheet per person, stored in the repo as JSON, next to the
character's other build data. The face sidecar is `face-params/v1`;
this is its body sibling. Builds read sheets; comparison rules (MAX
rule etc.) compute from sheets.

## Shape

```json
{
  "schema": "body-measurements/v1",
  "subject": "<name>",
  "units": "cm",
  "measurements": {
    "stature":        { "value": null, "head_units": null, "method": "...", "confidence": "measured|derived|claim-based", "source": "..." },
    "...": {}
  },
  "unmeasured": [ { "name": "inseam", "reason": "..." } ]
}
```

Every measurement entry carries `value` (cm, or null), optionally
`head_units` (the unit-free ratio that is usually the measured truth),
`method`, `confidence`, and `source`. Absolute cm values derived from
an unverified stature claim must say so in `method` and carry
`confidence: "claim-based"`.

## Field list (the full sheet — every inch)

- `stature` — total height
- `head_height` — chin to crown (the head unit everything scales from)
- `leg_length` — hip joint to floor
- `thigh_length`, `shin_length`, `inseam`
- `torso_length` — hip joint to shoulder joint
- `shoulder_width` — joint to joint
- `arm_upper_length`, `arm_forearm_length`, `arm_total_length`
- `neck_length`, `neck_circumference`
- `bust_width`, `bust_circumference`
- `waist_width`, `waist_circumference`
- `hip_width_joint` — hip joint span (NOT outer breadth)
- `hip_width_outer`, `hip_circumference`
- `glute_depth` — front-to-back at the glutes
- Face dimensions live in the face-params/v1 sidecar; the sheet
  references it, it does not duplicate it.

## Rules

- A field with no evidence goes in `unmeasured` with the reason. It is
  never estimated into `measurements`.
- Pose-affected numbers (seated, bent arm, foreshortening) say so in
  `method` — a pose artefact is not anatomy.
- Silhouette/mask widths are not circumferences and are never stored
  as such.
