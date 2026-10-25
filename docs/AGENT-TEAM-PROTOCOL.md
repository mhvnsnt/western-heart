# Agent Team Protocol (2026-10-23, user directive)

How the different AI agents (Muse/DoggByte, Claude Code, Grok, and any future agents)
work together as a real development team on Western Heart.

## The pattern (user-demonstrated 2026-10-23)

The user acts as the bridge between agents that can't talk to each other directly.
The working pattern that proved out:

1. **One agent finds the root cause, others build on top.** When an agent diagnoses
   the real cause of a bug, the other agents do NOT make a second version of the fix.
   They let the fix land, check it, and build on top of it.
2. **Claim before you start.** Before beginning work in a shared area, announce what
   you're touching (via the user, or via a handoff doc in `docs/handoffs/`).
3. **Work alongside, don't step on each other.** If two agents are in the same area
   (e.g. face-weight fix), coordinate through the user so the work is complementary,
   not duplicative.
4. **Check the landing.** When another agent's fix merges, verify it before extending it.

## Lanes (soft, not hard — user: "just pick up on all the work," no lane-guarding)

- **Muse/DoggByte:** inputs/combos, select screen/cards/dedupe, merges, menu rebuilds
- **Claude Code:** live deploys, anti-clobber CI, rig audit/re-rigs, facing audit,
  Tripo wiring audit, side-switch
- **Grok:** owner-law enforcement, menu teardown compliance, general crew work

Lanes are a starting point, not a fence. If something needs doing and your lane is
idle, do it. The user explicitly revoked lane-guarding.

## Resource rule (user directive 2026-10-23)

- **Use free resources as much as possible:** this VM, open-source tools, the GitHub
  data API, background agents — all free. Burn these first.
- **Save the user's paid credits** (Claude sessions, other metered tools) for work
  that actually needs them.
- **Keep work going autonomously** on the free tier as much as possible, around the
  clock. The user should wake up to progress, not blockers.

## Handoff format

Write handoff docs to `docs/handoffs/` using the existing pattern
(see `CLAUDE_TO_CREW_2026-10-23.md`): what broke, the commit, the fix, and how to
do it right. Every handoff names the real breakage with evidence — no vague
"something's wrong."

## Merge discipline (applies to ALL agents)

- Merge ONLY when every check is green (all 6: rig-guard, clobber-guard, guard,
  deletion-guard, instruction-gate, game-unit-tests).
- A timed-out or cancelled check counts as a FAIL — never merge on 5/6.
- Nothing gets deleted. PR not frozen. NO batch merges.
- Feature branch + PR for everything. NEVER push to main directly. No force-push.
- Real 3-way merges via git_merge.py (the merge REST endpoint 404s with the PAT,
  SSH is blocked). Merge commits only.
- PR body needs the 6 instruction-gate sections (verbatim owner quote, specified
  method, actual method, deviations, proof, self-check checkbox).
- Anti-clobber: sync to latest main BEFORE starting file work AND before committing.
  Surgical edits only — never rewrite a whole file when a targeted edit will do.
- Verify by playing: every fix gets verified on the live build (phone portrait,
  like the user plays), never by code inspection alone.

## Attribution problem (known limitation)

All agents merge through the single `mhvnsnt` GitHub login, so GitHub cannot show
which agent performed a merge. When in doubt about who did what, check branch
name prefixes (`claude/`, `grok/`, worker branches) and PR bodies — not the
merger login.
