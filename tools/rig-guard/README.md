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

---

# tools/rig-guard — face-weight guard (added 2026-10-23)

Fails CI when a PR adds or modifies a rigged GLB whose **face-region vertices**
(top 15% of model height) carry **>5% skin weight on spine/pelvis/hips/root**
(or other non-head) bones.

The loss this prevents: the "face cone" bug (user-reported 2026-10-23) — jaw,
chin, and face verts weighted to `Spine`/`Spine1`/`Spine2`/`Hips` instead of
`Head`, so the face stretches down toward the spine whenever the body moves.
Found on Purple Rain (40,060 verts), Star (524), armor-king (1,578), awa-pop
(12,583), baek (16,965), and others; fixed universally by reassigning those
weights to the Head bone. This guard makes sure it can never come back.

## Files

- `face_weight_guard.py` — the guard. Pure function `check_face_weights(path)`
  returns the list of violating verts (empty = pass) + a CLI that scans GLB
  files (explicit paths, or PR-changed GLBs via `BASE_SHA`/`HEAD_SHA`).
- `test_face_weight_guard.py` — unit tests: clean model → pass; spine-weighted
  face → fail; below-threshold → pass; unskinned → pass. Run:
  `python3 -m unittest discover -s tools/rig-guard -p 'test_face_weight_guard.py' -v`

Requires: `pip install numpy pygltflib meshopt`.

## CI wiring

`.github/workflows/game-checks.yml` — job `face-weight-guard` (self-test, then
scans every `.glb` the PR added/modified). Exit 0 = clean, 1 = REFUSED (bad
GLBs printed), 2 = usage/error.
