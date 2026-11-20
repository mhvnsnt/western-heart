# Main branch protection (added 2026-10-23, after PR #498)

## What happened
PR #498 (Pantera weights) was merged into main at 8:01 PM CT on Oct 23 2026 with the
owner's shared token (`mhvnsnt`). 34 seconds earlier an agent pushed "Merge main into
fix/pantera-weights-20261021 — keep both sides". That merge commit dropped 4,225 files
(likely resolved from a stale or sparse working tree). The PR was merged before any
check finished, and main had **no branch protection**, so nothing stopped it.

## Protection now on main (GitHub branch protection)
- Required status checks (strict / branch must be up to date): `pr-safety-guard`,
  `clobber-guard`, `deletion-guard`, `no-deletion-guard`, `instruction-gate`.
- Admins are included (`enforce_admins`), so the shared agent token cannot push
  straight to main or merge with red/pending checks.
- No force-pushes, no branch deletion.

## pr-safety-guard rules
Fails a PR that deletes >25 files, deletes anything under `.github/`, `game/js/`,
`CLAUDE.md` or `AGENTS.md` (override: label `owner-approved-deletion`, owner only),
or whose fork point is >200 commits behind main (override: `owner-approved-stale`).

## Agent rules
1. Never merge while any check is queued or pending. Wait for every Actions run to be green.
2. Never resolve a "merge main into branch" in a sparse or partial checkout.
3. Before merging, `git diff --diff-filter=D origin/main...HEAD` must be empty (or labelled by the owner).
4. Never add the override labels yourself; only the owner does.
