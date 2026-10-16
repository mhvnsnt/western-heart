# AGENTS.md

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

## NO-SWEEP-INFLIGHT LAW (owner 2026-10-16)
NEVER delete, move, or "clean up" anything that is downloading, uploading, rendering, extracting, or otherwise in-flight — no matter how full the disk gets. Download folders, staging dirs, partial files (.part, .kaggle-partial, .aria2, split chunks), and anything an active lane is writing to are SACRED. The disk-space-guardian, watchdog, and every agent must treat in-flight work as untouchable. If disk is critical: pause NEW downloads, surface the alert to the owner, NEVER sweep in-flight work. A deleted partial can destroy unrecoverable progress (mirrors die, sessions expire, quota burns).

## NEVER-DELETE-GAME-FILES LAW — AMENDMENT (owner 2026-10-16)
Game files (ISOs, ROMs, game archives, teardown sources) are NEVER auto-deleted. They stay until verified on TERABOX and the owner confirms. AMENDMENT: when a game file IS verified on BOTH TeraBox and GitHub, proactively surface it to the owner with the verification evidence (exact TeraBox folder + piece count, exact GitHub release/repo) and ask "verified on both stores — can I delete the local copy?" He decides per file. The law is NOT relaxed — default is still never delete — but verified files must be brought to him instead of sitting silently on disk.

**ESCALATION (owner 2026-10-16):** First time a game file is verified on both stores: surface it with evidence, ask "can I delete this?", wait for his okay. If he does not answer and it keeps getting surfaced as verified (2nd or 3rd time) with thorough re-verification — delete it, do not ask forever. Silence after repeated asks is the go-ahead.

**RELAXATION (owner 2026-10-16 — supersedes the amendment/escalation):** When a game files FULL working folder is verified BYTE-IDENTICAL on BOTH GitHub and TeraBox, it MAY be deleted from local disk without asking. Conditions: (1) byte-identical full folder on both stores, hash/size verified; (2) NO teardown/decoding/decryption actively in progress on it right now; (3) if teardown is not 100% per the TEARDOWN-COMPLETION LAW, log it on ~/workspace/agent-ops/TEARDOWN-IDLE-QUEUE.md first — idle-time work, thread never lost; (4) log every deletion + backup locations.
