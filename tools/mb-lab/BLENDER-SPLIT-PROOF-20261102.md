# MB-Lab Blender version split — proof run (2026-11-02)

What this PR does: it closes the audit's MB-Lab/Blender item by the
documented alternative branch — pin the split, don't claim 5.x.
MB-Lab generation stays on Blender 4.0.2 (the verified path);
Blender 5.2.3 is the WH rig/render standard, and MB-Lab on 5.x stays
UNVERIFIED until a vendor checkout + 5.x bake passes. Files:

- `tools/mb-lab/check_blender_compat.py` — the honest compat reporter
  (verdicts: unverified / incompatible / candidate / addon-enabled /
  addon-enable-failed; a "candidate" is never a compatibility claim).
- `tools/mb-lab/test_check_blender_compat.py` — its pure-Python proof.
- `tools/mb-lab/README.md` — new "Blender version split" section.
- `tools/creation-suite/bases.json` — the mb-lab family's `blender`
  field now states the split instead of only saying 5.x is unverified
  in passing.

Nothing about the 9 MB-Lab bases, their job specs, or their AGPL
licence changes in this PR.

## Proof (pure Python + real Blender --version, no vendor, no bake)

```
python3 tools/mb-lab/test_check_blender_compat.py
PASS: check_blender_compat — version parse, unverified / candidate /
incompatible verdicts, CLI exit codes verified

python3 tools/mb-lab/check_blender_compat.py \
  --blender <blender-5.2.3 binary> --json
{
 "blender_version": "5.2.3",
 "mblab_present": false,
 "verdict": "unverified: vendor missing — run bash tools/mb-lab/fetch-mb-lab.sh
              first; no claim is made about this Blender version"
}

python3 tools/mb-lab/check_blender_compat.py \
  --blender <blender-4.2.3 binary> --json
{
 "blender_version": "4.2.3",
 "mblab_present": false,
 "verdict": "unverified: vendor missing — run bash tools/mb-lab/fetch-mb-lab.sh
              first; no claim is made about this Blender version"
}
```

Blender binaries themselves were verified by running them on this
VM: "Blender 5.2.3 LTS, build date 2026-10-22" and "Blender 4.2.3 LTS,
build date 2024-10-14" (version output only — no MB-Lab run).

Note on the run above: a local repo clone was blocked by the home
disk quota on this VM, so the compat tool was run from the PR's file
in a test fixture (same file, same code); only its default vendor
path differs by location. The verdict logic is the fixture-tested
logic, and the vendor-missing verdict is the same either way because
no MB-Lab vendor checkout exists on this VM.

## What is NOT proven here

- MB-Lab on Blender 5.2.3 is NOT verified. Nothing in this PR says
  otherwise. The two steps that would verify it are documented in
  the README section: (1) `--try-enable` reports `addon-enabled` on
  5.2.3 with a vendor checkout present, and (2) `run_mblab_job.py`
  produces a GLB from a spec on 5.2.3. Both are owed, on a machine
  with the vendor checkout (fetch is ~200MB; it was not pulled here
  because of the disk quota).
- The 9 baked MB-Lab meshes (from #1495, on 4.0.2) are unaffected.

## Licence (unchanged)

MB-Lab code GPL-3.0, base data AGPL-3.0. These bases are AGPL-3.0,
NOT CC0. For a licence-clean base use the mpfb2 or
charmorph-vitruvian family.
