# Western Heart — How to continue

Read first: `lab/README.md` (milestones), `docs/PLAYTEST-METHOD.md` (how to play/measure), `docs/QA-FINDINGS.md` (bugs), `docs/WORKLOG.md` (what happened, newest last). Claim in `mhvnsnt/agent-ops` CLAIMS.md before editing; Repo Co Dev owns `lab/game/scripts/*` engine work.

## Rules
- Branch + PR, commit as mhvnsnt, gitleaks before push, merge only when Actions are verified green. Never delete work; edit in place.
- After every change: rerun `godot --headless --path lab/game -s res://tests/qa_playtest.gd | grep '^QA|'` and `lab/game/tests/run_match_headless.sh`; paste the before/after `QA|` lines in the PR.
- Append to WORKLOG.md with a CT timestamp each time you stop.

## Next steps (in order)
1. Bug 1 grab row + throw state; Bug 2 startup mapping (check King T3 row for jab, should be i10).
2. Input buffer + string windows (Bug 3), then f,f dash / b,b backdash (Bug 4) — add scenarios already in the harness to confirm.
3. Launcher → juggle state (Bug 5).
4. Visual: King KMD seams/head (Bug 6), stage pano (Bug 8), separation (Bug 7).
5. Add harness scenarios for crouch/sidestep when implemented; extend comparison table.
6. Teardown inspirations: browser builds / chimera emulator hub are a separate track (PS2 titles barely run in browser); use reference footage + wiki frame data until then.
