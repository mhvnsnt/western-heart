# tools/charmorph — CharMorph, Vitruvian base only

CharMorph (github.com/Upliner/CharMorph) is the free open-source
Blender character creator that reimplements most of MB-Lab's features
without MB-Lab's code: parametric humanoid bases, morphs, Rigify
support with a full face rig, real-time clothing fit, direct skin/eye
colour, and material-level displacement. It is the successor path
from MB-Lab in the upstream character-creator lineage — and, for
Western Heart, the CC0-base path that does not depend on MPFB2.

## What is wired here — and what is not

Wired in this PR (one base, one family):

- Registry: `tools/creation-suite/bases.json` (family `charmorph`).
- Selector: `python3 tools/charmorph/select_base.py list|show|job|fighter vitruvian`
  — `job` writes a suite job spec (`tool: "charmorph"`) runnable with
  `python3 tools/suite-jobs/run_job.py --spec <spec>`; `fighter` writes
  the `F.charmorph` fighter fragment.
- Runner: `tools/charmorph/run_charmorph_job.py` — imports the stored
  Vitruvian base from `char.blend` (Blender library link) and exports
  it as GLB. It is dispatched by `tools/suite-jobs/run_job.py`'s
  default convention (`tools/<tool>/run_<tool>_job.py`).
- Proof: `python3 tools/charmorph/test_select_base.py` (pure Python, no
  Blender; see `tools/charmorph/CHARMORPH-PROOF-20261102.md`).

NOT wired, NOT claimed:

- Other CharMorph bases. Antonia and Reom are CC-BY, the MB-Lab base
  is AGPL. They are not in this family, and the selector/runner
  reject any character other than `vitruvian`, so they cannot slip
  through under the family's CC0 label.
- Morph-customized exports. Morphs are set in CharMorph's UI and
  baked at finalization; this job exports the stored base as-is.
- Rigify generation. CharMorph's README states the rig is added only
  at finalization (Rigify generation takes a long time). The
  `rig: "rigify"` entry in bases.json records the downstream stage,
  not a step this job performs. Chain, in full:
  CharMorph import (this job) → finalize in Blender (Rigify) →
  WH GameRig retarget (`tools/auto_rig`, same as every other
  character) → standard export chain.
- A baked mesh or a render proof. No Vitruvian mesh ships in this PR;
  `base_mesh` in bases.json is the job's output path. The bake +
  full-body/part-zoom render proof is the next run, after the
  character download below.

## Place in the Western Heart pipeline

```
PARAMETRIC CREATION (this tool, Vitruvian CC0 base only)
  CharMorph imports the Vitruvian base -> GLB
        |
        v
FINALIZE + RIG (Blender GUI / suite stages, NOT this job)
  CharMorph finalize (Rigify) -> WH GameRig retarget
        |
        v
WRAP -> EXPORT (standard chain)
  -> suite as a template base mesh or a finished custom fighter
```

## Blender compatibility — READ THIS

| | |
|---|---|
| CharMorph 0.4 target | Blender 4.4 (per upstream release notes) |
| WH pipeline standard | Blender 4.0.2 |
| Verdict | WH 4.0.2 compatibility is NOT verified. Do not claim it. |

The job does not pin a Blender version: it takes `params.blender` /
`CHARMORPH_BLENDER` / `blender` on PATH, and fails at addon/character
lookup if the setup does not run. A version claim requires a real
bake on that version.

## Licence — PER BASE, never blanket

- Vitruvian base: CC0 (the only base wired here).
- Antonia: CC-BY. Reom: CC-BY. MB-Lab base: AGPL.
- Addon code licence: see `license.txt` in the CharMorph checkout
  (the repo ships GPL/AGPL texts; this README does not re-label it).

If a base other than Vitruvian is ever wanted, it is a separate PR
with its own licence entry — never an edit that reuses this family's
CC0 label.

## Fetch-on-demand (DISK RULES)

CharMorph is **never committed to git**. The fetch script is the install:

```bash
bash tools/charmorph/fetch-charmorph.sh   # default: tools/charmorph/vendor
```

It clones the pinned commit (with submodules — CharMorph's `data/`
dir is a submodule) and verifies the addon. The character library is
separate: use CharMorph 0.4's in-Blender character downloader (or the
CharMorph-db library into the addon's data dir) to get
`characters/vitruvian/char.blend` + `config.yaml`. Until those exist,
`run_charmorph_job.py` refuses to run instead of exporting a fake base.
