# Limit Handoff & Resume Steps

Add-on to [`docs/AGENT-TEAM-PROTOCOL.md`](../AGENT-TEAM-PROTOCOL.md) → "Handoff format". Use with [`TASKBOARD.md`](TASKBOARD.md).

## Before you run out (every agent, always)
1. Work on a feature branch with a prefix naming you (`claude/`, `grok/`, `muse/`, `jules/`...).
2. **Push early, push often**: after every meaningful step, run gitleaks, commit, push. Open a **draft PR** as soon as the first commit exists. Nothing may live only on one machine.
3. Claude Code: the autosave hook (`.claude/settings.json` + `CLAUDE.md`, being added separately) commits and pushes your branch after each reply. Run from an up-to-date clone so the hook loads.
4. Keep the PR body's checklist current: done / in progress / next step / exact commands or scripts used (commit the scripts too).

## When you hit a limit
- If you get a warning, stop new work, push, and update the PR's "next step" line.
- Mark your TASKBOARD item `status: paused (limit, resets <time CT>)` with the PR link.

## Picking up someone else's work
1. Find the item on TASKBOARD and the branch/PR it links. If the work isn't on GitHub, **don't re-create it in parallel**: ask the owner to have that agent push, or take a clearly different item.
2. Branch **off their branch** (`grok/on-claude-825`), not a fresh copy. Sync to latest `main` first.
3. Update TASKBOARD: `owner: <you> (continuing <their branch>)`.

## Reconciling parallel branches
- Merge order: the earlier PR lands first (when green); the follower rebases/merges `main` in and resolves conflicts surgically.
- If two versions of the same asset exist, keep both on branches, test both in the live build (phone portrait), keep the better one, and record why in the PR. Never delete the other branch's work in the PR. Close the loser's PR with a note.
- When the paused agent returns: it pulls, reads TASKBOARD + PR comments, and continues from the latest branch tip, not from its local copy.
