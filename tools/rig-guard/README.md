# tools/rig-guard — MODEL_URLS key-removal guard

Fails CI when a PR removes **any** key from `MODEL_URLS` (`game/js/assets.js`).
Deleting a key deletes a wired model — skinned or not — and silently makes a
fighter unreachable (the zui/zen gaps of 2026-10-21 were only found by manual
audit: GLBs on disk with no key). This is the model-key half of the
anti-clobber immune system; the line-revert half lives in
`.github/scripts/clobber_guard.py`.

## Files

- `rig_guard.py` — the guard. Pure functions (`extract_model_keys`,
  `removed_keys`, `check_removals`) + a CLI that diffs the `MODEL_URLS`
  literal between `BASE_SHA` (PR fork point) and `HEAD_SHA` via `git show`.
- `test_rig_guard.py` — unit tests: key removed → fail; key added → pass;
  escape path → pass. Run: `python3 -m unittest discover -s tools/rig-guard
  -p 'test_rig_guard.py' -v`

## Escape path (documented, PR-body-explicit)

Intentional removals are allowed but must be explicit — silence is refusal:

1. a `## Model removals` section in the PR body naming every removed key in
   backticks, **or**
2. the `owner-approved-model-removal` label on the PR.

## Local pre-push use (same pattern as tools/clobber-check)

```bash
BASE_SHA=<sync-sha> HEAD_SHA=$(git rev-parse HEAD) \
    python3 tools/rig-guard/rig_guard.py
```

Exit 0 = clean, exit 1 = REFUSED (removed keys printed), exit 2 = usage error.

## CI wiring

`.github/workflows/game-checks.yml` — job `rig-guard` (self-test + key-removal
check on a sparse checkout) and job `game-unit-tests` (the `test/*.test.mjs`
suite on a sparse checkout). Does not touch or duplicate the existing
`clobber-guard`, `deletion-guard`, `no-deletion-guard`, or `instruction-gate`
workflows.
