# Tweak Patch Format — `wh-tweak-patch` (v1)

The ONE round-trip patch format for the Western Heart customization suite.
Crew stages work → user tweaks it live in the suite → user hits **EXPORT** →
suite downloads a small JSON patch → user sends it back in chat → the
coordinator runs `tools/customization/import_tweak_patch.py` to validate and
apply it to the repo in a PR.

Design rules (owner-approved):
- **One format, one export button, one importer.** No parallel dialects.
- **Self-describing:** the patch names the fighter, the kit it was made
  against, and every part change in plain fields.
- **Versioned:** `format` + `version` fields; the importer only accepts
  versions it knows and rejects everything else with a clear error.
- **Validatable:** the importer rejects malformed patches (bad fighter,
  unknown part group, non-numeric rotations, duplicate groups, unknown
  kit) with a clear error and changes NOTHING. It never silently corrupts.

## The 8 part groups

`head`, `torso`, `upper_arms`, `forearms`, `hands`, `thighs`, `shins`, `feet`

Arms/legs groups cover both sides together (the suite mirrors L/R). This is
deliberate: part-orientation fixes are almost always symmetric (a whole part
mirrored/flipped on import).

## Patch JSON (v1)

```json
{
  "format": "wh-tweak-patch",
  "version": 1,
  "kit_id": "julia-parts-fix-1",
  "fighter": "nightwolf",
  "attire": "default",
  "exported_at": "2026-10-22T06:35:00Z",
  "exported_by": "suite",
  "suite_build": "https://mhvnsnt.github.io/western-heart/ (main @ 4f2a1c9)",
  "notes": "head was facing backwards; flipped it",
  "changes": [
    {
      "kind": "part_transform",
      "group": "head",
      "rotation_deg": [0, 180, 0],
      "flip": [false, false, false],
      "offset": [0, 0, 0],
      "scale": 1.0,
      "note": "yaw 180 to face forward"
    }
  ]
}
```

Field rules (v1):
- `format` must be exactly `"wh-tweak-patch"`; `version` must be `1`.
- `fighter` must be a roster id known to the repo
  (`game/js/roster-full.js` or `customization/profiles/<fighter>.json`).
- `kit_id` may be `null`/omitted (a freehand patch); when present it must
  name a staged kit in `customization/tweak-kits/`.
- `changes` must be a non-empty array.
- Each change: `kind` must be `"part_transform"`; `group` must be one of the
  8 part groups; `rotation_deg` 3 finite numbers in [-360, 360] (degrees,
  XYZ Euler order — the same order the suite preview uses);
  `flip` 3 booleans (mirror on that axis — negative scale in the preview);
  `offset` 3 finite numbers in [-5, 5] (model units); `scale` a finite
  number in [0.1, 10]. `note` optional string.
- No group may appear twice in one patch (one entry per group — the entry
  is the user's FINAL value for that group).

## Tweak kits (crew-staged starting points)

`customization/tweak-kits/<kit-id>.json` — what the crew stages so the user
always starts from latest:

```json
{
  "format": "wh-tweak-kit",
  "version": 1,
  "id": "julia-parts-fix-1",
  "fighter": "nightwolf",
  "attire": "default",
  "status": "staged",
  "notes": "parts-audit flagged head + hands facing backwards",
  "flagged_parts": ["head", "hands"],
  "part_map": {
    "head": ["head", "hair"],
    "torso": ["body", "torso", "chest"],
    "upper_arms": ["upperarm", "shoulder"],
    "forearms": ["forearm", "elbow"],
    "hands": ["hand", "finger"],
    "thighs": ["thigh", "hip"],
    "shins": ["shin", "calf", "knee"],
    "feet": ["foot", "feet", "toe"]
  },
  "adjustments": {
    "head": { "rotation_deg": [0, 0, 0], "flip": [false, false, false],
              "offset": [0, 0, 0], "scale": 1.0 }
  }
}
```

- `part_map`: case-insensitive substring match against mesh names in the
  fighter's GLB — how the suite finds each part group on any fighter.
- `adjustments`: the crew's starting values (usually zeros); the suite loads
  these, the user tweaks from there.
- When the importer applies a user patch, it writes the patch's values back
  into the kit's `adjustments` (bumping `version`), so the NEXT round starts
  from the user's latest — the loop never loses work.

## What the importer does

`tools/customization/import_tweak_patch.py <patch.json>`:

1. **Validate** — every rule above, plus: fighter exists, kit exists (when
   named), no duplicate groups, JSON parses. Any failure → non-zero exit,
   clear message, nothing written.
2. **Apply** — merge each change into the kit's `adjustments` (patch wins
   per group), append a history entry, bump kit `version`.
3. **Record** — write `customization/tweak-kits/<fighter>/applied/<kit>-<ts>.applied.json`
   (the patch + a sha256 + the validation report) as the canonical record.
4. With `--pr` — push the tree change through the Git Database API helper
   and open a PR titled `tweak-patch: <fighter> <kit>`.

The rig/model-fix pipeline consumes `kit.adjustments` as its input spec —
per-group `rotation_deg`/`flip`/`offset`/`scale` are the counter-transforms
to bake into the rig.

## Suite surfaces

- Live: `game/customization-harness.html?tweak=<kit-id>` — loads the kit,
  shows the flagged parts, per-group rotate/flip controls, ONE export button
  ("EXPORT TWEAK PATCH") that downloads
  `<fighter>-<kit-id>-tweak-patch.json`.
- Without `?tweak=`, the harness is unchanged (plain fight view).

Full control/panel behavior: `game/js/fix-panel.js` (comment header).
