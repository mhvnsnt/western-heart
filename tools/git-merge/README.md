# git-merge

Merge a pull request as a real merge commit without SSH and without the
merge REST endpoint.

## When to use it

The VM agents run on has no SSH route to github.com and the available
credential cannot call the merge endpoint. `git_merge.py` merges through the
Git Database API instead, with the same safety bar as the repo's
MERGE-IT-YOURSELF law.

## Usage

```text
python3 tools/git-merge/git_merge.py <PR> [--yes] [--owner o] [--repo r] [--base main]
```

Without `--yes` it dry-runs: prints the plan and changes nothing.

## Safety rules (refuses instead of clobbering)

- PR must be open, not a draft, `mergeable_state == clean`.
- CI check-runs on the head SHA must exist and none may fail.
- Every touched file gets a real 3-way merge (merge-base / base / branch)
  with `git merge-file`. Any conflict aborts the whole merge.
- Files only the base branch changed are never touched.
- The base ref update is fast-forward-only; if the base moved mid-merge,
  it aborts and nothing is pushed.
- Verifies GitHub closed the PR as merged afterward.

## Auth

Uses the `custom.github_pat` connector credential via Muse's dynamic
credential surrogate. No keys in the file, in args, or in env. Needs
`dynamic_credentials.py` from the custom-connector-setup skill on the
machine running it.
