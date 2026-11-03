# PR status board (repo only, not the game)

Owner instruction (2026-11-03, verbatim): "no I don't want that on the game home screen but in the repo yes".
Nothing here touches `game/` or any menu.

## What it is
- Generator: `.github/scripts/pr_status_board.py` (stdlib Python; GraphQL for open PRs + their latest-commit check rollup, REST `/branches/main` for the required check names).
- Tests: `.github/scripts/test_pr_status_board.py` (offline, run by the workflow before publishing).
- Workflow: `.github/workflows/pr-status-board.yml`: hourly (`17 * * * *`), on `pull_request` (opened / reopened / synchronize / ready_for_review / converted_to_draft / closed / edited), and `workflow_dispatch`. Uses `GITHUB_TOKEN` only.
- Board: `docs/PR-STATUS.md`. Summary line (ready to merge / failing / running / conflicted), a "Merge order" list for stacked PRs (a PR whose base branch is another open PR's head merges after it), and one row per open PR: status, draft or ready, author / lane branch, head sha, base (+ stacked-on PR), each required check on `main`, other checks, mergeable state, last updated. Sorted ready-to-merge first.

## Where the live board is
`main` is branch-protected with required checks (admins included), so a bot push to it is refused. The workflow never writes to `main`. It publishes, only when the content changed (the `_Generated …_` timestamp line is ignored in the compare):
1. `docs/PR-STATUS.md` on the dedicated branch `pr-status-board` (created from `main` on first run; only that one file ever changes there). Do not open a PR from that branch.
2. The body of the pinned issue titled "PR Status Board".

The copy of `docs/PR-STATUS.md` on `main` is the first snapshot that shipped with the workflow PR; the live one is on the branch and the issue.

## Loop safety
- No `push` trigger. Commits and issue edits made with `GITHUB_TOKEN` do not start workflows.
- The job skips events from `github-actions[bot]`, PRs from forks, and PR events whose head is `pr-status-board`; `paths-ignore: docs/PR-STATUS.md` skips PRs that only touch the board.
- The board leaves its own `pr-status-board` check off every row, so it never reports itself as running.
- `concurrency: pr-status-board` (no cancel) serialises runs so two runs never race on the issue or branch.

## Run it by hand
`python3 .github/scripts/pr_status_board.py --out docs/PR-STATUS.md` (needs `GITHUB_TOKEN` with repo read). Add `--publish` to push to the branch and issue.

## Status rules
Priority conflicted > failing > running > draft > stacked > ready. Failing = any check (required or not) FAILURE / TIMED_OUT / ERROR / ACTION_REQUIRED / STARTUP_FAILURE. Ready = not draft, base `main`, GitHub MERGEABLE, every required check green, nothing failing, running or cancelled. Required check names come from `main`'s protection (`clobber-guard`, `deletion-guard`, `guard`, `instruction-gate` as of 2026-11-03), with that list as the fallback.
