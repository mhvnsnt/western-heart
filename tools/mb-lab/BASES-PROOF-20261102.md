# MB-Lab base family — proof run (2026-11-02)

What this PR wires: the 9 MB-Lab template bases (already baked as meshes
in #1495) become a selectable family in the creation suite, via
`tools/creation-suite/bases.json` + `tools/mb-lab/select_base.py`.
Selecting a base emits a suite job spec (`tool: "mb-lab"`) that
`tools/suite-jobs/run_job.py` dispatches to `tools/mb-lab/run_mblab_job.py`,
and a fighter-JSON fragment (`F.mb_lab`).

## Proof (pure Python, no Blender, no vendor checkout)

```
python3 tools/mb-lab/test_select_base.py
PASS: mb-lab family — 9 bases selectable, job specs + fighter fragments round-trip, dispatch resolves

python3 tools/mb-lab/select_base.py list
MB-Lab — AGPL-3.0 base data, GPL-3.0 code (NOT CC0)
  super-heavyweight, powerhouse, showman, technician, highflyer, luchador,
  powerhouse-w, athletic-w, striker-w   (6 male m_ca01 + 3 female f_ca01)

python3 tools/mb-lab/select_base.py job powerhouse --out jobs/mb-lab-powerhouse.json
job spec -> jobs/mb-lab-powerhouse.json
run: python3 tools/suite-jobs/run_job.py --spec jobs/mb-lab-powerhouse.json
```

Example job spec (powerhouse): `{"tool": "mb-lab", "params": {"character":
"m_ca01", "finalize": true, "morphs": {"Age": 0.3, "Mass": 0.45, "Tone":
0.75}}, "out": "customization/templates/meshes/powerhouse.glb"}`. The spec
follows `run_mblab_job.py`'s actual schema (`character`/`morphs`
directly under `params`).

## What is NOT proven here

Baking a fresh mesh from a spec needs the MB-Lab vendor checkout
(`bash tools/mb-lab/fetch-mb-lab.sh`) and Blender 4.0.2, and is not
re-run in this proof — the 9 shipped meshes were baked in #1495.
MB-Lab on Blender 5.x is NOT verified; do not claim it.

## Licence

MB-Lab code GPL-3.0, base data AGPL-3.0. These bases are AGPL-3.0,
not CC0. For a licence-clean base use the mpfb2 or
charmorph-vitruvian family.
