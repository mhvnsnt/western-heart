# customization/templates — data-driven creation templates

**No code changes to add a template.** Drop a JSON entry (or a new JSON file
in this dir following the schema below) and the suite's template-select
screen picks it up on next load.

## Files

| File | What |
|---|---|
| `body-templates.json` | The 9 starter BODY templates (3 Heavyweight, 3 Cruiserweight, 3 Women's). Each names its No Mercy source body type, proportions, default skin/head, the MB-Lab spec that bakes its `base_mesh`, and the GLB path. |
| `face-presets.json` | Face preset cards: `wwe` layer (extracted No Mercy face textures) + `gnm` layer (GNM semantic expression presets). Merged into one picker by the unified FACE system. |
| `skin-tones.json` | The 8 No Mercy CAW skin tones + 4 suite extensions. |
| `face-parts.json` | Eyes / facial hair / masks / hats, each `part_ref` pointing at the real extracted part in `customization/parts/PARTS-INDEX.json`. |
| `meshes/` | Generated `base_mesh` GLBs (MB-Lab headless bake). Reproduce any of them 1:1 from the `mb_lab` spec in body-templates.json via `tools/mb-lab/run_mblab_job.py`. |
| `specs/` | Per-template MB-Lab job specs (generated from body-templates.json). |

## Body template schema

```json
{
  "id": "powerhouse",
  "name": "Texas Powerhouse",
  "division": "Heavyweight | Cruiserweight | Women's",
  "gender": "male | female",
  "source": "no-mercy: Austin",
  "body_type": "Austin",
  "proportions": {"height": 1.0, "weight": 1.12, "muscle": 1.15},
  "skin_tone": "#c98d5e",
  "head_shape": "male_1",
  "base_mesh": "customization/templates/meshes/powerhouse.glb",
  "mb_lab": {"character": "male_01",
             "morphs": {"Age": 0.3, "Mass": 0.45, "Tone": 0.75}},
  "desc": "..."
}
```

- `body_type` must be a No Mercy CAW body type (14M + 9F — the suite's BODY
  step uses the same list, so template → customize is continuous).
- `mb_lab.morphs` are MB-Lab `character_data` morph names; the bake job
  matches them case-insensitively and warns on unknown names.
- `base_mesh` GLBs are **AGPL-3.0** (baked from MB-Lab's AGPL database).
  The bake scripts + specs in this repo are the corresponding source.

## License note

Template *definitions* (this JSON) are ours. Template *meshes* are
AGPL-3.0 via MB-Lab. If a license-clean base is ever required, re-bake
the same template through the MPFB2 path (CC0 assets) —
see tools/mpfb2/README.md.
