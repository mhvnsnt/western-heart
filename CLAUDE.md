# CLAUDE.md — read this first (Claude Code loads it automatically)

Also read and follow `AGENTS.md` (all crew laws apply to you).

## Never strand work on your local disk (owner rule, 2026-10-23)
Your session can hit its usage limit at any moment. Work that is only on your disk is
work the owner and the other agents (Muse, Grok/MoneyManBusch, Repo Co Dev) cannot use.

1. **Push early and often.** Commit and push every finished piece immediately — one rig,
   one fix, one doc. Never batch 16 things and push at the end.
2. **Commit the tool, not just the output.** Any script you use to generate or modify
   assets (rigging, limb isolation, retargeting, extraction) goes under `tools/`
   (e.g. `tools/auto_rig/`) in the same PR, so any agent can re-run it.
3. **Open the PR as soon as the first commit exists**, with the full PR template. Keep
   pushing to it.
4. **Merge rules:** merge only if it merges cleanly, every check is verified green via
   the Actions runs API (unreadable / 403 / timeout = fail), `--diff-filter=D` is empty,
   and nothing is frozen. No batch merges. Merge commits only; never force-push, rebase,
   amend pushed commits, or delete branches.
5. **On resume, before anything else:** push whatever is left over (the SessionStart hook
   already tries), then reconcile with other agents' branches via agent-ops `CLAIMS.md`
   and `TAG-TEAM.md`. If someone rebuilt your unpushed work meanwhile, keep both and
   compare; don't overwrite theirs.

## Autosave safety net (`.claude/settings.json` → `tools/agent/autosave.sh`)
Hooks run the autosave on `Stop` (end of every turn), `StopFailure` (turn killed by
rate/usage limit or API error), `PreCompact`, `SessionEnd`, and after `Write`/`Edit`
(debounced to once per 10 min). It:
- does nothing if the tree is clean; never runs mid-merge/rebase or in a sparse checkout;
- if you are on `main`/`gh-pages`, moves the work to a new `claude/autosave-<date>` branch;
- `git add -A` (respects `.gitignore`), **unstages every deletion**, skips files >100 MB
  unless LFS-tracked;
- runs `gitleaks protect --staged` (regex fallback if gitleaks is missing) and aborts on findings;
- commits `wip(autosave): <timestamp> [event]` as mhvnsnt and does a plain `git push` (never force);
- always exits 0 so it can't block you. Log: `.git/autosave.log`. Off switch: `AUTOSAVE_DISABLE=1`.

The autosave is a net, not the plan: still commit with real messages and open the PR yourself.


## Complete Wiring Law (owner 2026-10-23)

Read `docs/rules/COMPLETE-WIRING-LAW.md` and `docs/tech/SYSTEMS-COVERAGE.md`. Push every system or ~30 min; backup branch before long jobs.


## Main protection law (2026-10-23, after PR #498)
main is branch-protected with required checks (pr-safety-guard, clobber-guard, deletion-guard, no-deletion-guard, instruction-gate), admins included. Never merge with pending or red checks, never resolve merges in a sparse checkout, never self-apply `owner-approved-deletion` / `owner-approved-stale`. Full rules: `docs/rules/MAIN-PROTECTION.md`.
