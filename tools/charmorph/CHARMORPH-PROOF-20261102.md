# CharMorph base family — proof run (2026-11-02)

What this PR wires: the Vitruvian base (CC0) becomes a selectable
family in the creation suite, via `tools/creation-suite/bases.json`
(family `charmorph`) + `tools/charmorph/select_base.py` +
`tools/charmorph/run_charmorph_job.py` + `tools/charmorph/fetch-charmorph.sh`.
Selecting the base emits a suite job spec (`tool: "charmorph"`) that
`tools/suite-jobs/run_job.py` dispatches by default convention to
`run_charmorph_job.py`, and a fighter-JSON fragment (`F.charmorph`).

## Proof (pure Python, no Blender, no addon checkout)

```
python3 tools/charmorph/test_select_base.py
PASS: charmorph family — 1 base selectable, job spec + fighter fragment
round-trip, dispatch resolves, validation + honest no-addon failure verified

python3 tools/charmorph/select_base.py list
CharMorph — Vitruvian — CC0 base data (Vitruvian only; see licence note)
  vitruvian  unspecified  Vitruvian  (vitruvian, rig: rigify)

python3 tools/charmorph/select_base.py job vitruvian --out jobs/charmorph-vitruvian.json
job spec -> jobs/charmorph-vitruvian.json
run: python3 tools/suite-jobs/run_job.py --spec jobs/charmorph-vitruvian.json
```

Example job spec: `{"tool": "charmorph", "params": {"character":
"vitruvian"}, "out": "customization/templates/meshes/charmorph-vitruvian.glb"}`.

End-to-end dispatch was also exercised through `run_job.py` itself:
it dispatched `charmorph` to the new runner, which failed honestly
with "CharMorph not found. Run: bash tools/charmorph/fetch-charmorph.sh"
and a job status of `error` — no fake bake, no substitute mesh.

Fetch script check: `bash -n tools/charmorph/fetch-charmorph.sh`
passes. The pinned commit (`ec5e13dcd5a7330b35fa7474b3abd2f406d77bd2`)
was verified with `git ls-remote` on 2026-11-02 and matches the
audit's 2026-10-24 verification. The script refuses to install a
different commit if HEAD has moved — re-pin deliberately instead.

## What is NOT proven here

- No baked CharMorph mesh ships in this PR. `base_mesh` in bases.json
  is the job's output path, not an existing file.
- No live Blender run was done here: that needs the addon checkout
  AND the downloaded Vitruvian character (`characters/vitruvian/
  char.blend` + `config.yaml`, via CharMorph 0.4's in-Blender
  downloader or CharMorph-db). Until then the runner refuses to run.
- Morph-customized exports and Rigify generation are NOT in this
  job (see `tools/charmorph/README.md` for the full chain:
  import → finalize in Blender (Rigify) → WH GameRig retarget →
  export). The `rig: "rigify"` entry in bases.json records the
  downstream stage, not a step this job performs.
- Blender version is not pinned: CharMorph 0.4 targets Blender 4.4
  per upstream; WH 4.0.2 compatibility is NOT verified. The next
  run (fetch → download Vitruvian → job → render proof) is also the
  first version claim, and only if it actually passes.
- Gender is "unspecified": no gendered Vitruvian variant is claimed.

## Licence

Vitruvian base CC0 — and ONLY Vitruvian. Antonia/Reom are CC-BY,
the MB-Lab base is AGPL, and neither is in this family. The selector
and runner reject any character other than `vitruvian`.
