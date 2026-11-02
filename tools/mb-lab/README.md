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
| Blender 5.2.3 | ✅ Also verified — see proof below |
| Verdict | ✅ Compatible — fetch-mb-lab.sh pins the 1.8.x line and the job runner was tested headless on 4.0.2, and on 5.2.3 (2026-11-02, below) |

## Blender 5.2.3 proof (2026-11-02)

MB-Lab 1.8.1 (upstream tag `1_8_1`, commit `063bff04e60f3e7c651fda628c30f5d83f3f3078`)
runs headless under Blender 5.2.3 LTS (build 2026-10-22, hash `e13b728c6880`,
`~/workspace/tools-industry/blender-5.2.3-linux-x64/blender`) with the
in-repo runner, unmodified except flushed logging:

```bash
blender -b --factory-startup --python tools/mb-lab/run_mblab_job.py -- \
  --spec <spec.json> --out <file.glb> --mblab-dir <MB-Lab 1_8_1 checkout>
# spec: {"params": {"character": "m_ca01", "finalize": true,
#                   "decimate_ratio": 0.06}, "out": "<file.glb>"}
```

Result: lab session started, character updated, `finalized to standard
Blender model`, character mesh 17,074 polys decimated ×0.06 → 2,048 polys,
and a valid glTF 2.0 export (Blender I/O v5.2.41): 1 mesh (9 primitives),
73 nodes, 1 skin. No Blender 5.x API error; the run is slow on a CPU-only
VM (about 15 minutes end to end, including a 97.7 s GLB export), so allow
for that — it is not a failure. MB-Lab 1.8.1 therefore works on Blender
5.2.3 too; 4.0.2 remains a verified option, and the 4.0.2-only split from
the 2026-11-02 tools audit no longer applies to MB-Lab.

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


## Base family registry — selectable bases (2026-11-02)

The 9 MB-Lab template bases are a selectable family in the creation
suite, not just loose template rows:

- Registry: `tools/creation-suite/bases.json` (family `mb-lab`).
- Selector: `python3 tools/mb-lab/select_base.py list|show|job|fighter <id>`
  — `job` writes a suite job spec (`tool: "mb-lab"`) runnable with
  `python3 tools/suite-jobs/run_job.py --spec <spec>`; `fighter` writes
  the `F.mb_lab` fighter fragment.
- Proof: `python3 tools/mb-lab/test_select_base.py` (pure Python, no
  Blender; see `tools/mb-lab/BASES-PROOF-20261102.md`).

Licence reminder: MB-Lab code GPL-3.0, base data AGPL-3.0. These bases
are AGPL-3.0, NOT CC0.


## Blender version split (2026-11-02)

MB-Lab's verified path stays Blender 4.0.2. Blender 5.2.3 is the
Western Heart rig/render standard, but MB-Lab on 5.x is NOT verified
— the audit's alternative branch (document the split, don't claim
5.x) is what this section does:

| Job | Blender |
|---|---|
| MB-Lab generation (`run_mblab_job.py`, this tool) | 4.0.2 (verified path) |
| Rig / render (WH standard) | 5.2.3 (not MB-Lab; see lane-1 Blender pin) |

Do not run MB-Lab jobs on 5.2.3 and call the result verified until
both of these pass on 5.2.3: (1) `check_blender_compat.py --try-enable`
reports `addon-enabled`, and (2) `run_mblab_job.py` produces a GLB
from a spec on that Blender. The compat tool below reports honestly
at each step and never upgrades a "candidate" to a compatibility claim.

Compat check (pure Python, no bake):

```bash
python3 tools/mb-lab/check_blender_compat.py --blender <path-to-blender> [--try-enable] [--json]
# verdicts: "unverified: vendor missing" | "incompatible: blender < 4.0"
#           | "candidate: vendor present" | "addon-enabled" / "addon-enable-failed"
# Proof: python3 tools/mb-lab/test_check_blender_compat.py
#        (see tools/mb-lab/BLENDER-SPLIT-PROOF-20261102.md)
```

Licence reminder (unchanged): MB-Lab code GPL-3.0, base data
AGPL-3.0. These bases are AGPL-3.0, NOT CC0. For a licence-clean base
use the mpfb2 or charmorph-vitruvian family.
