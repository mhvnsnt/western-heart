# tools/customization

Crew-side tooling for the customization suite.

## import_tweak_patch.py — the round-trip apply script

Validates and applies a user-exported tweak patch (`wh-tweak-patch`,
see `customization/TWEAK-PATCH-SPEC.md`).

```
python3 tools/customization/import_tweak_patch.py <patch.json> [--repo DIR] [--check] [--pr]
```

- `--check`: validate only, write nothing (exit 0 = valid).
- `--pr`: push the applied change through the Git Database API helper and
  open a PR (`--branch` overrides the default branch name).

Validation is strict: bad format/version, unknown fighter, unknown kit,
kit/fighter mismatch, empty changes, unknown part group, duplicate group,
non-finite or out-of-range numbers — ANY failure rejects the whole patch
with a clear error and writes nothing. It never silently corrupts.

On success it merges each change into the staged kit's `adjustments`
(patch wins per group), bumps the kit version, appends a history entry, and
writes a canonical applied record under
`customization/tweak-kits/<fighter>/applied/`.

Tests: `python3 tools/customization/tests/test_import_tweak_patch.py`
(18 cases: valid apply + every malformed shape rejected).

## skin-library

Skin library assets and tooling (pre-existing).
