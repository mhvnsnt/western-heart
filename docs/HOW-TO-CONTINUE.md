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

## No-data-loss rules (MANDATORY)
Read and follow [`docs/NO-DATA-LOSS-RULES.md`](NO-DATA-LOSS-RULES.md) (canonical: mhvnsnt/agent-ops). No force-push, no rebase/amend of pushed work, no history rewrite, no branch/asset deletion without backup + owner approval, PRs only, empty D-filter + gitleaks + green CI before merge, push incrementally, keep WORKLOG, back up and sha256-verify before disk cleanup, never touch other agents' or Muse's work.

## Input resolver V2 (2026-10-23 14:15 CT)
Read docs/input/INPUT-RESOLVER-V2.md. Run `node test/input-determinism.test.mjs --report /tmp/r.json` after any moveset/input change; it must print PASS. Next: the 107 long-string cases, 34 duplicate-spelling conflicts, hold-button (`*`) input, DOA 2/4 slots from the DOA4 decode, port to AshLane + Brutal Fist.
