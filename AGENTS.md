# AGENTS.md

# ANTI-CLOBBER LAWS (owner 2026-10-17 — the DXMMII 54k-file wipe)

On 2026-10-17, commit cd3bf38 ("DXMMII limb system", PR mhvnsnt/western-heart#221) deleted 54,456 files against 105 additions. The commit message said nothing about deletions. Nobody read the deletion list before merging. The repo was 99.996% gone. These laws exist so that never happens again. Every agent, every repo, every commit, every merge.

1. DELETION CHECK — before every commit, read `git status` and the diff stat. Every deleted file in the diff must be something your task intended to delete. A deleted file your task did not delete on purpose means STOP: do not commit, do not push, report what you found. The working tree is wrong, not the task.

2. OWN THE TREE — never `git add -A` or `git commit -a` in a working tree you did not fully populate yourself. Before committing, verify the tree is complete: file counts match the remote branch you branched from (your task's own additions and changes aside). A tree missing files you didn't delete is damaged — don't sweep it into history.

3. CIRCUIT BREAKER — if a commit would delete more than a handful of files outside your task's scope, STOP and report instead of committing. A big deletion count is a hard stop, not a warning to scroll past. Committing unexplained deletions "and letting someone else figure it out" is the failure.

4. SAY THE DELETIONS — the commit message names every deletion. One deleted file gets one line; many deleted files get a count plus what category went. A commit whose message and diff disagree is a hard failure — don't push it.

5. MERGE GATE — the merger reads the PR's deletion list against the task description before merging. Unexplained deletions block the merge. "CI is green" does not excuse a deletion list the task never asked for. A red, conflicting, or lossy PR stays open with a comment naming the blocker.

(Co-authored with Aider and Copilot per the ALL-AGENTS-WORKFLOW LAW. Cline's seat stays open — its free-tier API was down during drafting.)

Read by Codex-style and other coding agents automatically.

---

## Owner's Agent Working Standard (mandatory, all agents)

Full standard: https://github.com/mhvnsnt/money-machine-hq/blob/main/docs/AGENTS.md. Read it before working here. The short version:

1. Do exactly what was asked. Ask when it's ambiguous. Never quietly swap in a cheaper or placeholder approach; call it out.
2. No faked progress. No "done/PASS/verified" without proof (PR link, test output, frames/screenshots you actually viewed).
3. Feature branch + PR for everything. **Never push WIP to `main`.** Merge only if it merges cleanly, CI passes, and it deletes/breaks nothing on main; otherwise leave the PR open.
4. Run gitleaks before every push. No secrets or personal info.
5. Build on existing work; don't redo or overwrite it. Finish before going wide.
6. Report failures first and honestly.
7. Owner's interests first: his money, his time, no advertising of unfinished games.
8. No copyrighted/leaked game files or third-party logos in public repos or Pages.
9. **Edit in place:** a fix or edit means opening the SAME existing project/file and changing it, with a git commit per change. Never regenerate from scratch unless asked. Keep one canonical project per work item at a documented path, with editable sources (EDLs, timelines, scripts, asset lists) next to renders.
10. **Log your workflow** in `WORKLOG.md` or `docs/workflows/`: what you did, the tools and settings, and the file paths.
11. Media deliverables follow Producerbot's `media-proof-standard` skill (check frames actually viewed; UNKNOWN is never PASS).

Self-check before saying "done": asked-scope met · shortcuts disclosed · proof attached · on a branch/PR · CI green · gitleaks clean · nothing copyrighted made public.

## No guessing (owner law)

**Read [docs/RULES_NO_GUESSING.md](docs/RULES_NO_GUESSING.md) before any animation, pose, model or data work.** Never hand-make, procedurally generate or guess when teardown/owned data exists; search the teardowns, decoded files and all repos first; log every source; report missing sources instead of faking; prove real bytes. Current audit: [docs/anim/PROCEDURAL_AUDIT.md](docs/anim/PROCEDURAL_AUDIT.md).

## Muse training pack
Muse/Ashes and every agent: read the [Muse training pack](https://github.com/mhvnsnt/money-machine-hq/tree/main/docs/muse-training-pack) (instructions, pre-flight checklist, real before/after examples, right-way videos) before every job.


## Sale status (owner rule, Oct 14, 2026)

No game is on a commercial or sale track until the owner explicitly says "I'm going to sell this," even if earlier docs say it is being made to sell. Until then, agents must not withhold, water down, or refuse requested work because it might affect publishing or sale readiness. Sale-readiness rework (rescanning or replacing third-party-derived content) happens only after the owner declares a sale.

## No-data-loss rules (MANDATORY)
Read and follow [`docs/NO-DATA-LOSS-RULES.md`](docs/NO-DATA-LOSS-RULES.md) (canonical: mhvnsnt/agent-ops). No force-push, no rebase/amend of pushed work, no history rewrite, no branch/asset deletion without backup + owner approval, PRs only, empty D-filter + gitleaks + green CI before merge, push incrementally, keep WORKLOG, back up and sha256-verify before disk cleanup, never touch other agents' or Muse's work.


## MERGE-IT-YOURSELF LAW (owner 2026-10-15)
"Stop leaving things open for me to merge... I don't like to manually handle PRs."
When a PR satisfies ALL merge conditions (GitHub says MERGEABLE, CI green, no-deletion guard clean, gitleaks clean, build passes), MERGE IT — do not leave it open for the owner. He does not want to manually handle PRs.
The merge must be CLEAN and NON-DESTRUCTIVE: merge commits, never rebase/squash/force-push; resolve conflicts by keeping both sides' work — nothing lost, nothing clobbered, nothing destroyed on either side. Verify the merged result still builds and passes tests before calling it done.
A PR that is red, conflicting, or would lose work stays OPEN with a comment naming the blocker — but the default for a clean, green PR is MERGE, never "leave it for the owner."
Carve-outs (standing owner decisions, not overridden): never merge a DRAFT PR; never merge a PR the owner explicitly excluded.

## NO FAST-AND-LAZY LAW (owner 2026-10-23)
"Fast and lazy on purpose" is banned. Speed that breaks main costs the owner more than it saves. Done means PLAYED, not pushed: sync to latest main, surgical edits only, read your own diff and deletion list, run `node --test game/tests/*.test.mjs`, start a real fight with `tools/proof-harness/fight.mjs` (must reach `"round":"fight"` with no `[pageerror]`; look at the frames), and put the proof you viewed in the PR. Never wire an unskinned static as a fighter's playable slot: rig on intake with `--facing` read from renders. Real breakages and the right way: [docs/handoffs/CLAUDE_TO_CREW_2026-10-23.md](docs/handoffs/CLAUDE_TO_CREW_2026-10-23.md).
