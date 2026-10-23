# tools/mb-lab — MB-Lab parametric character generation

MB-Lab (github.com/animate1978/MB-Lab) is the free open-source Blender
character creator: parametric humanoid bodies/faces with hundreds of morph
parameters, phenotype presets, skin/shader engine, hair engine, expressions,
and automatic rigging. It is the community continuation of ManuelBastioniLAB.

## Place in the Western Heart pipeline

```
PARAMETRIC CREATION (this tool)
  MB-Lab generates the base character: body morphs + face + skin material
  + hair + expression, driven by a JSON param spec
        |
        v
WRAP EXTERNAL MESHES
  Tripo/SmutBase intake meshes are shrink-wrapped / surface-fit onto the
  MB-Lab base (or vice versa) so the parametric rig drives them
        |
        v
RIG
  MB-Lab's own skeleton -> retargeted to the Western Heart canonical rig
  (GameRig backend in tools/auto_rig, same as every other character)
        |
        v
EXPORT
  GLB out via the standard export path (tools/suite-jobs run_job.py,
  glTF-Transform + meshoptimizer optimize), lands in the suite as a
  template base mesh or a finished custom fighter
```

MB-Lab is the **BODY-system parametric source** in the unified creation
suite (see docs/CREATION-SUITE-UNIFICATION-MAP.md): its morphs sit alongside
MPFB2 targets and Build-A-Bod scaling behind one BODY panel, and its face
morphs sit behind the unified FACE panel next to GNM.

## Blender compatibility — VERIFIED

| | |
|---|---|
| Pipeline standard | Blender 4.0.2 (`~/workspace/tools/blender/blender-4.0.2-linux-x64/blender`) |
| MB-Lab requirement | **Blender 4.0+** — MB-Lab 1.8.0 introduced Blender 4.0 support; 1.8.1 is the final release |
| Verdict | ✅ Compatible — fetch-mb-lab.sh pins the 1.8.x line and the job runner was tested headless on 4.0.2 |

## License

- Addon **code**: GPL-3.0 (`license.txt`: "All python files … GNU General Public License 3")
- Addon **database** (meshes, .blend library, images, JSON morph data): **AGPL-3.0**

What this means for us: we use MB-Lab as a *tool* (like a compiler). Characters
we generate are built from its AGPL database, so generated template base
meshes are released under AGPL-3.0 too — the generation script
(`run_mblab_job.py`) and the param specs that reproduce every shipped base
mesh live in this repo, which satisfies the source-availability requirement.
If the owner ever wants a fully clean-room base, the MPFB2 path (CC0 assets)
is the alternative — see tools/mpfb2/README.md.

## Fetch-on-demand (DISK RULES)

MB-Lab is **never committed to git** (~200MB+ with the humanoid library).
The fetch script is the install:

```bash
bash tools/mb-lab/fetch-mb-lab.sh [dest]   # default: tools/mb-lab/vendor
```

It clones the pinned tag, verifies the checkout, and registers the addon path
for headless Blender. Re-running is a no-op when the pinned version is present.

## Headless generation (the wired path)

```bash
# Generate a character from a param spec, export GLB:
blender -b --python tools/mb-lab/run_mblab_job.py -- \
  --spec tools/mb-lab/specs/template-heavyweight.json \
  --out /tmp/mb-heavyweight.glb
```

Or through the suite job queue (live status in the suite UI):

```bash
python3 tools/suite-jobs/run_job.py --spec jobs/mb-lab-heavyweight.json
```

Job spec format: `{"tool":"mb-lab","params":{...},"out":"path/to.glb"}` —
see tools/suite-jobs/README.md. The creation suite's BODY panel submits
these jobs and polls status; no dead buttons.

## Param spec reference

```json
{
  "character": "female_01",
  "params": { "age": 0.1, "mass": 0.6, "tone": 0.7, "height": 0.2 },
  "phenotype": "european",
  "skin": { "tone": "medium", "freckles": 0.2 },
  "expression": "neutral",
  "finalize": true,
  "export": { "format": "glb", "apply_modifiers": true }
}
```

Full parameter list: MB-Lab's own `data/` morph JSONs after fetch
(`vendor/MB-Lab/data/*.json`). The suite's BODY sliders map 1:1 onto these.
