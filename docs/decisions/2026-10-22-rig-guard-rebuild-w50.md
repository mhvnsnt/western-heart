# 2026-10-22 — rig-guard rebuild (worker 50, picking up Claude's dropped work)

Claude's anti-clobber guard rebuild (rig_guard.py ~162 lines, test_rig_guard.py
~84 lines, game-checks.yml ~75 lines) was unpushed — it existed only on the
user's machine. Rebuilt from the task description and PR'd as
`.github/workflows/game-checks.yml` + `tools/rig-guard/`.

## What it does

- `tools/rig-guard/rig_guard.py`: CI guard that FAILS on ANY `MODEL_URLS`
  (`game/js/assets.js`) key removal — not just skinned models. Any wired
  model key removal = the loss the owner wants prevented (cf. the zui/zen
  gaps of 2026-10-21: GLBs on disk, no key, unreachable in fights, found only
  by manual audit).
- Escape path (documented, PR-body-explicit): a `## Model removals` section
  in the PR body naming each removed key in backticks, or the
  `owner-approved-model-removal` label. Silence = refusal.
- `tools/rig-guard/test_rig_guard.py`: 11 unit tests — key removed → fail;
  key added → pass; rename flags the old name; body callout → pass; partial
  callout still fails on the rest; label → pass. All green locally.
- `.github/workflows/game-checks.yml`: two jobs — `rig-guard` (self-test +
  key-removal check on a sparse checkout of `tools/rig-guard` +
  `game/js/assets.js`) and `game-unit-tests` (`test/*.test.mjs` via node on a
  sparse checkout of `test` + `game/js` + `game/data`, ~1 MB of blobs).
- Verified against the real `game/js/assets.js` at the PR base: 149 keys
  extracted; simulated `phantom` removal correctly flagged; addition and
  escape paths pass.

## Deliberate non-duplication

Does not touch or duplicate `clobber-guard`, `deletion-guard`,
`no-deletion-guard`, or `instruction-gate` workflows. Distinct name
(`rig-guard`), distinct concern (model-key presence vs line reverts vs
deletions vs PR-body format).

## Placement note

The task specified `tools/` with a README note (rather than
`.github/scripts/` where `clobber_guard.py` lives), so the guard doubles as a
local pre-push tool: `BASE_SHA=<sync-sha> HEAD_SHA=$(git rev-parse HEAD)
python3 tools/rig-guard/rig_guard.py` — same pattern as
`tools/clobber-check/`.
